"""The process-version digest and the frozen-headline partition.

A cell is stamped with a content digest of the process that produced it (the
prompt template, the resolved registry config, and the engine's retrieval
surface), so headline metrics can reflect only
the frozen, blessed process. These lock the two properties the stamp rests on:
the digest is *reproducible* (a maintainer can compute a digest to bless) and
*sensitive* (any real process change moves it), and `is_frozen` gates on the
digest, never the label.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fedcourtsai import process_version
from fedcourtsai.process_version import _config_canonical
from fedcourtsai.registry import enabled_evaluators, enabled_predictors, load_predictors
from fedcourtsai.schemas import ProcessVersion
from tests.conftest import bless_process

CONFIG = Path("config")
REPO = Path(".")


def test_the_digest_is_reproducible() -> None:
    a = process_version.compute_process_digest(b"prompt", {"engine": "claude-code", "model": "m"})
    b = process_version.compute_process_digest(b"prompt", {"engine": "claude-code", "model": "m"})
    assert a == b
    assert a.startswith("sha256:")


def test_the_digest_moves_on_any_real_process_change() -> None:
    base = process_version.compute_process_digest(
        b"prompt", {"engine": "claude-code", "model": "m"}
    )
    # A whitespace-only prompt edit is a legitimately new version.
    assert base != process_version.compute_process_digest(
        b"prompt ", {"engine": "claude-code", "model": "m"}
    )
    # A model change is a new version.
    assert base != process_version.compute_process_digest(
        b"prompt", {"engine": "claude-code", "model": "m2"}
    )


def test_a_cosmetic_mcp_description_edit_does_not_bump_the_version() -> None:
    """A manifest comment is documentation, not a process input — editing it
    must not re-version every actor. The resolved config the digest hashes
    excludes the MCP `description`, consistent with the actor-level one."""
    entry = next(p for p in load_predictors(CONFIG / "predictors.yaml") if p.mcp_servers)
    canonical = _config_canonical(CONFIG / "predictors.yaml", entry)
    servers = canonical["mcp_servers"]
    assert isinstance(servers, list) and servers, "the fixture predictor pins a server"
    assert all("description" not in server for server in servers)


def test_the_prompt_config_boundary_cannot_be_forged() -> None:
    """The NUL join means shifting a byte across the prompt/config boundary is a
    different digest, so two distinct processes can't collide by concatenation."""
    assert process_version.compute_process_digest(
        b"ab", {"x": "c"}
    ) != process_version.compute_process_digest(b"a", {"x": "bc"})


def test_digest_for_actor_resolves_from_the_real_registry() -> None:
    """Each enabled actor has a resolvable, distinct digest — the value
    `process-digest --all` prints for a maintainer to bless."""
    digests = {
        actor: process_version.digest_for_actor(REPO, CONFIG, "predictor", actor)
        for actor in ("claude-baseline", "codex-baseline", "gemini-baseline")
    }
    # Same prompt, different engine/model -> genuinely different processes.
    assert len(set(digests.values())) == 3
    assert all(d.startswith("sha256:") for d in digests.values())


def test_the_retrieval_surface_is_hashed_into_the_digest() -> None:
    """Dropping the retrieval surface from the canonical config would leave a
    capability change riding under the identity that blessed the earlier runs."""
    entry = next(p for p in load_predictors(CONFIG / "predictors.yaml") if p.engine == "codex")
    canonical = _config_canonical(CONFIG / "predictors.yaml", entry)
    assert canonical["retrieval"] == list(process_version.ENGINE_RETRIEVAL[entry.engine])


def test_a_capability_change_moves_the_digest(monkeypatch: pytest.MonkeyPatch) -> None:
    """The point of hashing the surface: revoke codex's web reach and the
    digest must move, so its cells cannot be pooled with web-enabled ones."""
    before = process_version.digest_for_actor(REPO, CONFIG, "predictor", "codex-baseline")
    monkeypatch.setitem(process_version.ENGINE_RETRIEVAL, "codex", ("subprocess-network",))
    after = process_version.digest_for_actor(REPO, CONFIG, "predictor", "codex-baseline")
    assert before != after


def test_the_live_codex_cells_declare_the_surface_they_run_with() -> None:
    """The tournament's cells are configured by the workflows, not the runner
    seam, so the declared surface is pinned to the args those steps pass."""
    workflows = Path(".github") / "workflows"
    declared = process_version.ENGINE_RETRIEVAL["codex"]
    for name in ("run-predict.yml", "run-evaluate.yml"):
        text = (workflows / name).read_text()
        assert ("web" in declared) == ("web_search=live" in text), name
        assert ("subprocess-network" in declared) == (
            "sandbox_workspace_write.network_access=true" in text
        ), name


def test_an_unknown_actor_fails_loudly() -> None:
    """A registry typo must not resolve to a fabricated-looking digest."""
    with pytest.raises(KeyError):
        process_version.digest_for_actor(REPO, CONFIG, "predictor", "no-such-predictor")


def _pv(digest: str) -> ProcessVersion:
    return ProcessVersion(
        label="proc-v1", digest=digest, stamped_at=datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_is_frozen_gates_on_the_digest_not_the_label(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    bless_process(monkeypatch, "sha256:blessed")
    assert process_version.is_frozen(_pv("sha256:blessed"))
    # Same label, unblessed digest — a process that drifted under an unchanged
    # label must NOT read as frozen.
    assert not process_version.is_frozen(_pv("sha256:drifted"))
    # An unstamped shakedown cell is never frozen.
    assert not process_version.is_frozen(None)


def test_the_frozen_set_and_the_freeze_instant_move_together() -> None:
    """The freeze commit fills both or neither.

    Digests without an instant would bless shakedown runs of the same bytes
    retroactively; an instant without digests would freeze nothing. Either
    half-state is a botched freeze commit, so the coupling is pinned — and
    while both are unset (the shakedown state), nothing is frozen. Every
    blessed digest must be a well-formed sha256 spelling, matching what
    `stamp-cell` writes.
    """
    digests = process_version.FROZEN_PROCESS_DIGESTS
    since = process_version.FROZEN_SINCE
    assert (len(digests) > 0) == (since is not None), (
        "FROZEN_PROCESS_DIGESTS and FROZEN_SINCE must be set in the same commit"
    )
    for digest in digests:
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", digest), digest
    if since is not None:
        assert since.tzinfo is not None, "the freeze instant must be timezone-aware"
    if not digests:
        assert not process_version.is_frozen(_pv("sha256:anything"))


def test_a_naive_stamp_reads_as_pre_freeze_never_a_crash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stamp with no offset has no defined order against the aware freeze
    instant, so it is excluded by rule — one malformed record must not take
    every frozen-scope surface down with a comparison error."""
    bless_process(monkeypatch, "sha256:blessed", since=datetime(2026, 2, 1, tzinfo=UTC))
    naive = ProcessVersion(
        label="proc-v1", digest="sha256:blessed", stamped_at=datetime(2026, 3, 1)
    )
    assert not process_version.is_frozen(naive)
    assert not process_version.at_or_after_freeze(datetime(2026, 3, 1))


def test_no_committed_cell_predates_the_freeze_it_claims() -> None:
    """The retroactive-blessing tripwire, on the real ledger.

    A committed prediction carrying a blessed digest with a stamp before the
    freeze instant is exactly the cell the pre-registration claim cannot
    survive — the freeze procedure's step 0 in prose, enforced here so the
    freeze commit fails loudly instead of relying on a maintainer's grep.
    Trivially green while the set is empty, and forever after a clean freeze.
    Predictions only, deliberately: the digest half of the claim lives there,
    and the evaluation side's guard is the freeze procedure's instant rule,
    not this test.
    """
    if not process_version.FROZEN_PROCESS_DIGESTS:
        pytest.skip("no digests blessed yet — the tripwire arms at the freeze commit")
    ledger = Path(__file__).resolve().parents[1] / "data" / "cases"
    for path in sorted(ledger.glob("*/*/events/*/predictions/*/*/prediction.json")):
        payload = json.loads(path.read_text())
        stamp = payload.get("process_version")
        if not stamp or stamp["digest"] not in process_version.FROZEN_PROCESS_DIGESTS:
            continue
        stamped_at = datetime.fromisoformat(stamp["stamped_at"])
        assert process_version.at_or_after_freeze(stamped_at), (
            f"{path}: blessed digest, pre-freeze stamp — list it in the freeze "
            "record as pre-registration-excluded or the claim does not hold"
        )


def test_every_enabled_actor_runs_a_blessed_process() -> None:
    """The de-blessing tripwire: the live tree still computes blessed digests.

    The digest folds in the prompt bytes, the resolved model, and the pinned
    MCP surface, so an edit to any of them silently drops every cell the
    fleet produces out of the frozen headline — fail-safe in direction, but
    indistinguishable from "no cells yet" on every scored surface. A digest
    move must arrive as a deliberate freeze-record update (a re-bless or a
    label bump beside it), never ride an unrelated edit; this pins that
    coupling. Skipped while nothing is blessed — arms at the freeze commit.
    """
    if not process_version.FROZEN_PROCESS_DIGESTS:
        pytest.skip("no digests blessed yet — the tripwire arms at the freeze commit")
    actors = [("predictor", p) for p in enabled_predictors(CONFIG / "predictors.yaml")] + [
        ("evaluator", e) for e in enabled_evaluators(CONFIG / "evaluators.yaml")
    ]
    assert actors, "an empty enabled fleet cannot be what the freeze blessed"
    for role, entry in actors:
        digest = process_version.digest_for_actor(REPO, CONFIG, role, entry.id)
        assert digest in process_version.FROZEN_PROCESS_DIGESTS, (
            f"{role} {entry.id}: the tree computes {digest}, which is not blessed — "
            "the process moved after the freeze; re-bless it deliberately or bump "
            "the label, in the same commit as the change that moved it"
        )


def test_is_frozen_requires_the_stamp_to_postdate_the_freeze(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A shakedown run of the very bytes later blessed is still shakedown.

    The digest says which process ran, never when — pre-registration means
    the commitment preceded the run, so a stamp from before the freeze
    instant stays out of the frozen headline even with a blessed digest.
    """
    bless_process(monkeypatch, "sha256:blessed", since=datetime(2026, 2, 1, tzinfo=UTC))
    # _pv stamps 2026-01-01: same digest, pre-freeze run — excluded.
    assert not process_version.is_frozen(_pv("sha256:blessed"))
    at_freeze = ProcessVersion(
        label="proc-v1", digest="sha256:blessed", stamped_at=datetime(2026, 2, 1, tzinfo=UTC)
    )
    assert process_version.is_frozen(at_freeze)
