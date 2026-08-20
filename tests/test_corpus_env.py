"""The corpus-env flip script: pair switching and capture/restore symmetry.

Pure shell — the script only re-exports the env contract, no store is touched —
so the tests drive real bash with fabricated URLs and assert what a flipped
shell (or a flipped single command) actually sees. The pointer override rides
the same capture/restore as the URLs: a staging flip must supply it and a prod
flip must restore whatever the shell had, or a later prod command silently
reads the staging blob.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parents[1] / "scripts" / "corpus-env")

_STAGING_POINTER = '{"key": "index/sha256/aa", "size": 1, "sha256": "aa"}'
_BASE_ENV = {
    "STAGING_CORPUS_REMOTE_URL": "s3://staging-bucket/store",
    "STAGING_CASESTORE_URL": "s3://staging-bucket/cases",
    "STAGING_CORPUS_POINTER": _STAGING_POINTER,
    "CORPUS_REMOTE_URL": "s3://prod-bucket/store",
}


def _bash(snippet: str, extra_env: dict[str, str] | None = None) -> list[str]:
    env = {"PATH": os.environ["PATH"], **_BASE_ENV, **(extra_env or {})}
    result = subprocess.run(
        ["bash", "-c", snippet], env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.splitlines()


def test_one_command_form_forwards_the_staging_contract() -> None:
    lines = _bash(
        f'"{SCRIPT}" staging bash -c '
        '\'echo "${FEDCOURTS_CORPUS_REMOTE_URL}"; echo "${FEDCOURTS_CORPUS_SPLIT}"; '
        'echo "${FEDCOURTS_CORPUS_POINTER}"; echo "${CORPUS_POINTER}"\''
    )
    assert lines == [
        "s3://staging-bucket/store",
        "1",
        _STAGING_POINTER,
        _STAGING_POINTER,
    ]


def test_one_command_form_without_staging_pointer_leaves_override_off() -> None:
    # Casestore-only staging reads predate the pointer secret; an unset
    # STAGING_CORPUS_POINTER must land as the empty string (= off for
    # fedcourtsai.config), never as a leaked ambient override.
    lines = _bash(
        f'"{SCRIPT}" staging bash -c ' + "'echo \"[${FEDCOURTS_CORPUS_POINTER}]\"'",
        extra_env={"STAGING_CORPUS_POINTER": "", "FEDCOURTS_CORPUS_POINTER": "ambient"},
    )
    assert lines == ["[]"]


def test_one_command_prod_form_restores_captured_values() -> None:
    # A one-command prod invocation inside a flipped shell must serve the
    # captured production values, pointer included — not the staging ones the
    # ambient (flipped) environment carries.
    lines = _bash(
        f'eval "$("{SCRIPT}" staging)" >/dev/null; '
        + f'"{SCRIPT}" prod bash -c '
        + '\'echo "${FEDCOURTS_CORPUS_REMOTE_URL}"; echo "[${FEDCOURTS_CORPUS_POINTER}]"\'',
        extra_env={"FEDCOURTS_CORPUS_POINTER": "prod-held-pointer"},
    )
    assert lines == ["s3://prod-bucket/store", "[prod-held-pointer]"]


def test_eval_round_trip_restores_the_prod_pointer() -> None:
    # A shell that had a pointer override before flipping to staging gets that
    # exact value back on the prod flip; the URLs restore alongside it.
    lines = _bash(
        f'eval "$("{SCRIPT}" staging)" >/dev/null; '
        'mid="${FEDCOURTS_CORPUS_POINTER}"; '
        f'eval "$("{SCRIPT}" prod)" >/dev/null; '
        'echo "${mid}"; echo "${FEDCOURTS_CORPUS_POINTER}"; '
        'echo "${FEDCOURTS_CORPUS_REMOTE_URL}"',
        extra_env={"FEDCOURTS_CORPUS_POINTER": "prod-held-pointer"},
    )
    assert lines == [_STAGING_POINTER, "prod-held-pointer", "s3://prod-bucket/store"]


def test_eval_round_trip_from_a_clean_shell_leaves_pointer_empty() -> None:
    # The normal case: production has no override, so the restore must land
    # empty (= off), not the staging value.
    lines = _bash(
        f'eval "$("{SCRIPT}" staging)" >/dev/null; '
        f'eval "$("{SCRIPT}" prod)" >/dev/null; '
        'echo "[${FEDCOURTS_CORPUS_POINTER}]"; echo "[${FEDCOURTS_CORPUS_SPLIT}]"'
    )
    assert lines == ["[]", "[]"]
