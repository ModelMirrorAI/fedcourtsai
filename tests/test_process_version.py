"""The process-version digest and the frozen-headline partition.

A cell is stamped with a content digest of the process that produced it (the
prompt template, the resolved registry config, and the engine's retrieval
surface), so headline metrics can reflect only
the frozen, blessed process. These lock the two properties the stamp rests on:
the digest is *reproducible* (a maintainer can compute a digest to bless) and
*sensitive* (any real process change moves it), and `is_frozen` gates on the
digest, never the label.

They also hold the two boundaries apart. A digest's **bless moment** is when
its bytes became immutable on `main`, so a stamp before it is retroactive
blessing and the ledger tripwires fire — prediction and evaluation halves
alike; `FROZEN_SINCE` is when the headline
starts **counting**, guessed late, so a cell minted in the window between them
lands honestly and is de-counted on timing alone.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from fedcourtsai import process_version
from fedcourtsai.process_version import _config_canonical
from fedcourtsai.registry import enabled_evaluators, enabled_predictors, load_predictors
from fedcourtsai.schemas import ProcessVersion
from tests.conftest import bless_process, open_freeze_window

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


def test_the_frozen_map_and_the_freeze_instant_move_together() -> None:
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
    for digest, blessed in digests.items():
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", digest), digest
        # An aware bless moment for the same reason the instant is aware: the
        # tripwire compares it against a stamp, and a naive one would order
        # against nothing. Not pinned against `since` — the held-instant
        # evaluator re-bless legitimately blesses after the instant.
        assert blessed.tzinfo is not None, f"{digest}: the bless moment must be aware"
        # A bless moment in the future is step 2's forecast left uncorrected:
        # step 4 replaces it with the carrying merge's real date, which has by
        # definition already happened. Left standing, it fires the tripwire on
        # every honest cell minted before the correction lands, so the one
        # link in the procedure that rests on discipline gets a guard.
        assert blessed <= datetime.now(UTC), (
            f"{digest}: blessed at {blessed}, which is in the future — step 2's "
            "forecast was never corrected to the carrying promotion's merge time"
        )
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


def test_no_committed_cell_predates_the_bless_it_claims() -> None:
    """The retroactive-blessing tripwire, on the real ledger.

    A committed prediction carrying a blessed digest with a stamp before that
    digest's **bless moment** is exactly the cell the pre-registration claim
    cannot survive: it ran while the commitment was still editable, so the
    digest was applied to it backwards. The freeze procedure's step 0 in
    prose, enforced here so the freeze commit fails loudly instead of relying
    on a maintainer's grep. Trivially green while nothing is blessed, and
    forever after a clean freeze.

    The **counting** instant is deliberately not the boundary here. It is
    guessed generously late at the freeze commit, so cells minted between the
    bless moment and the instant are honest ledger cells that ``is_frozen``
    de-counts on timing — shakedown, not retroactivity — and a tripwire keyed
    on the instant would call them a broken pre-registration.

    Predictions half; the evaluation twin below walks the evaluation ledger
    against the evaluator bless moments with the same rule.
    """
    if not process_version.FROZEN_PROCESS_DIGESTS:
        pytest.skip("no digests blessed yet — the tripwire arms at the freeze commit")
    ledger = Path(__file__).resolve().parents[1] / "data" / "cases"
    paths = sorted(ledger.glob("*/*/events/*/predictions/*/*/prediction.json"))
    assert paths, "glob matched no prediction.json — the ledger path shape moved"
    for path in paths:
        payload = json.loads(path.read_text())
        stamp = payload.get("process_version")
        if not stamp or stamp["digest"] not in process_version.FROZEN_PROCESS_DIGESTS:
            continue
        cell = ProcessVersion(
            label=stamp["label"],
            digest=stamp["digest"],
            stamped_at=datetime.fromisoformat(stamp["stamped_at"]),
        )
        assert process_version.at_or_after_bless(cell), (
            f"{path}: stamped {stamp['stamped_at']} under a digest not blessed until "
            f"{process_version.blessed_at(stamp['digest'])} — that is retroactive "
            "blessing, not shakedown; the digest was applied to a run made while the "
            "commitment was still editable, so either the bless moment in "
            "FROZEN_PROCESS_DIGESTS is wrong or the claim does not hold"
        )


def test_no_committed_evaluation_predates_the_bless_it_claims() -> None:
    """The retroactive-blessing tripwire's evaluation twin, on the real ledger.

    An evaluation's stamp carries the same pre-registration claim a
    prediction's does — this grading ran under a commitment already made — so
    a stamp before its digest's bless moment is the same broken claim on the
    other half of the ledger. The extra path segment is the evaluator/
    predictor pair: ``evaluations/<evaluator_id>/<predictor_id>/<run_id>/``.
    """
    if not process_version.FROZEN_PROCESS_DIGESTS:
        pytest.skip("no digests blessed yet — the tripwire arms at the freeze commit")
    ledger = Path(__file__).resolve().parents[1] / "data" / "cases"
    paths = sorted(ledger.glob("*/*/events/*/evaluations/*/*/*/evaluation.json"))
    assert paths, "glob matched no evaluation.json — the ledger path shape moved"
    for path in paths:
        payload = json.loads(path.read_text())
        stamp = payload.get("process_version")
        if not stamp or stamp["digest"] not in process_version.FROZEN_PROCESS_DIGESTS:
            continue
        cell = ProcessVersion(
            label=stamp["label"],
            digest=stamp["digest"],
            stamped_at=datetime.fromisoformat(stamp["stamped_at"]),
        )
        assert process_version.at_or_after_bless(cell), (
            f"{path}: stamped {stamp['stamped_at']} under a digest not blessed until "
            f"{process_version.blessed_at(stamp['digest'])} — that is retroactive "
            "blessing, not shakedown; the digest was applied to a grading made while "
            "the commitment was still editable, so either the bless moment in "
            "FROZEN_PROCESS_DIGESTS is wrong or the claim does not hold"
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


# The two boundaries as one fixture: blessed 2026-01-15 (the carrying
# promotion's merge), counting from 2026-02-01 (the instant, guessed late).
BLESS = datetime(2026, 1, 15, tzinfo=UTC)
INSTANT = datetime(2026, 2, 1, tzinfo=UTC)


def _stamped(moment: datetime) -> ProcessVersion:
    return ProcessVersion(label="proc-v1", digest="sha256:blessed", stamped_at=moment)


def test_a_stamp_predating_its_bless_is_retroactive_blessing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The boundary the tripwire enforces: nothing may precede its own bless.

    A cell stamped before the promotion that made its digest immutable ran
    against a commitment that could still be edited, so the digest was applied
    to it backwards. No declaration licenses that, which is why it is the
    tripwire's boundary and the counting instant is not.
    """
    bless_process(monkeypatch, "sha256:blessed", since=INSTANT, blessed_at=BLESS)
    assert not process_version.at_or_after_bless(_stamped(BLESS - timedelta(seconds=1)))
    assert process_version.at_or_after_bless(_stamped(BLESS))
    # Unstamped and unblessed cells have no bless moment to be after.
    assert not process_version.at_or_after_bless(None)
    assert not process_version.at_or_after_bless(
        ProcessVersion(label="proc-v1", digest="sha256:drifted", stamped_at=INSTANT)
    )
    assert process_version.blessed_at("sha256:blessed") == BLESS
    assert process_version.blessed_at("sha256:drifted") is None


def test_a_window_cell_lands_as_shakedown_rather_than_counting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The window between the boundaries is exactly the shakedown lane.

    A cell minted after its digest was blessed but before the counting instant
    is an honest ledger cell — the pre-registration claim holds for it — and
    the instant is what keeps it out of the headline. Both halves matter: the
    tripwire must not fire on it, and no counted surface may admit it.
    """
    bless_process(monkeypatch, "sha256:blessed", since=INSTANT, blessed_at=BLESS)
    window = _stamped(datetime(2026, 1, 20, tzinfo=UTC))
    assert process_version.at_or_after_bless(window)
    assert not process_version.at_or_after_freeze(window.stamped_at)
    assert not process_version.is_frozen(window)
    assert not process_version.graded_post_freeze(window)


def test_a_stamp_at_the_instant_passes_both_boundaries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """At or after the instant a cell is both non-retroactive and counted."""
    bless_process(monkeypatch, "sha256:blessed", since=INSTANT, blessed_at=BLESS)
    counted = _stamped(INSTANT)
    assert process_version.at_or_after_bless(counted)
    assert process_version.is_frozen(counted)
    assert process_version.graded_post_freeze(counted)


def test_a_naive_stamp_is_excluded_from_the_bless_boundary_too(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One malformed record must not crash the tripwire on a comparison.

    Same rule as :func:`at_or_after_freeze`: a stamp with no offset orders
    against nothing, so it reads as before the bless moment and the tripwire
    fires on it rather than raising.
    """
    bless_process(monkeypatch, "sha256:blessed", since=INSTANT, blessed_at=BLESS)
    assert not process_version.at_or_after_bless(_stamped(datetime(2026, 3, 1)))


def test_the_pending_window_prediction_is_ledgered_but_not_counted() -> None:
    """The live constants, against a cell stamped in today's open window.

    The real shape a predict round lands right now: a prediction under a
    blessed proc-v5 predictor digest, stamped after the carrying promotion and
    before the instant. It must pass the retroactive-blessing tripwire — its
    process was already immutable on `main` when it ran — and must stay out of
    every frozen-scope figure until the instant. Read off the module, so the
    next freeze cutover moves it without an edit here.
    """
    opening = open_freeze_window()
    if opening is None:
        pytest.skip("no window between a bless moment and the counting instant is open")
    digest, minted = opening
    window = ProcessVersion(
        label=process_version.CURRENT_PROCESS_LABEL, digest=digest, stamped_at=minted
    )
    assert process_version.at_or_after_bless(window)
    assert not process_version.is_frozen(window)
