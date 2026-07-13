"""Offline consistency checks for the repository's corpus + metrics bookkeeping.

CI runs without the corpus remote or its credentials — the gate stays offline
and fast (see ``docs/data-pipeline.md``) — so it cannot fetch the corpus blob
to diff it against the remote. What it *can* verify, deterministically and
offline, is that the committed bookkeeping is internally coherent:

* the corpus blob (``corpus/corpus.db``) is **gitignored and absent from
  git**, so the multi-hundred-megabyte file can never slip into the repo —
  only the small committed pointer names it;
* the committed pointer (``corpus/corpus.db.ref``), when present, is
  well-formed (valid JSON, a 64-hex sha256, a positive size);
* every metrics roll-up (:data:`METRICS_ARTIFACTS`) exists on disk **and** is
  committed — they are small, reviewable, and git-tracked by contract; and
* a locally present corpus blob satisfies the ranged-read layout contract
  (64 KB pages, non-WAL at rest — see ``corpus.check_ranged_layout``).

``fedcourts corpus-status`` runs these checks. The online side — the actual
pull/push against the remote — belongs to the data workflows (``run-pull``'s
writer jobs), which hold the remote credentials.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

from . import corpus, corpus_remote
from .corpus_ranged import RangedBackendError, read_index_pointer

# The corpus blob and its committed pointer, repo-relative. The blob path is
# a constant (not derived from a pointer file) so the out-of-git invariant
# holds even before the first pointer is ever committed.
CORPUS_BLOB = Path("corpus") / corpus.CORPUS_DB_FILENAME
CORPUS_POINTER = corpus_remote.pointer_path_for(CORPUS_BLOB)

# The pipeline roll-ups that must be committed to git: small, deterministic,
# and worth reading in a diff. run-analytics's metrics-refresh job regenerates
# them; this gate fails when one is missing or uncommitted.
METRICS_ARTIFACTS: tuple[Path, ...] = (
    Path("metrics") / "leaderboard.json",
    Path("metrics") / "backtest.json",
    Path("metrics") / "statpack.json",
    Path("metrics") / "statpack.md",
)


def check_state(
    repo_root: Path,
    *,
    is_tracked: Callable[[Path], bool],
    is_ignored: Callable[[Path], bool],
) -> list[str]:
    """Return human-readable problems with the repo's bookkeeping (empty = clean).

    ``is_tracked`` / ``is_ignored`` answer git questions about a repo-relative
    path; the CLI wires them to git, and tests inject fakes so the core logic
    stays pure and offline.
    """
    errors: list[str] = []
    pointer_file = repo_root / CORPUS_POINTER
    if pointer_file.is_file():
        try:
            read_index_pointer(pointer_file)
        except RangedBackendError as exc:
            errors.append(str(exc))
    if is_tracked(CORPUS_BLOB):
        errors.append(
            f"{CORPUS_BLOB}: the corpus blob is committed to git; "
            "it must live only in the corpus remote (the pointer names it)"
        )
    if not is_ignored(CORPUS_BLOB):
        errors.append(
            f"{CORPUS_BLOB}: the corpus blob is not gitignored; it could be committed by accident"
        )
    for artifact in METRICS_ARTIFACTS:
        if not (repo_root / artifact).is_file():
            errors.append(
                f"{artifact}: metrics artifact is missing; regenerate it "
                "(fedcourts leaderboard / backtest / statpack — the same "
                "commands the run-analytics metrics refresh runs) and commit it"
            )
        elif not is_tracked(artifact):
            errors.append(f"{artifact}: metrics artifact is not committed to git")
    # The ranged-read layout contract rides on the same offline gate: check the
    # blob's file header whenever it is present locally (absent is fine — the
    # gate runs before any corpus pull).
    errors.extend(corpus.check_ranged_layout(repo_root / CORPUS_BLOB))
    return errors


def _git_tracked_files(repo_root: Path) -> set[Path]:
    """Repo-relative paths git currently tracks."""
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {Path(name) for name in proc.stdout.split("\0") if name}


def _git_is_ignored(repo_root: Path, path: Path) -> bool:
    """Whether git would ignore ``path`` (works even if the file is absent)."""
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-q", "--", str(path)],
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def git_checkers(repo_root: Path) -> tuple[Callable[[Path], bool], Callable[[Path], bool]]:
    """Build ``(is_tracked, is_ignored)`` backed by git for :func:`check_state`."""
    tracked = _git_tracked_files(repo_root)

    def is_tracked(path: Path) -> bool:
        return path in tracked

    def is_ignored(path: Path) -> bool:
        return _git_is_ignored(repo_root, path)

    return is_tracked, is_ignored
