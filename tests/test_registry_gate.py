"""The promotion gate's Step 0, on a synthetic history.

``main`` holds the committed registry (the merge-stamping rule declared) and a
ledger; ``staging`` registers ``proc-v10`` over a moved claude-baseline digest.
Each refusal is built by bending one fact of that history — a pending digest
already in main's ledger, an unregistered live digest, a predecessor window
left open, a ``prereg/`` tag already minted, a repeated boundary, a pending row
already on main, a registry that does not load — and the clean history is the
control. The live digests are read from a tree's own config and prompts, so
the end-to-end check runs the command against a history carrying them.
"""

from __future__ import annotations

import copy
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version
from fedcourtsai.cli import app
from fedcourtsai.process_registration import LiveActor, register_boundary
from fedcourtsai.promotion_record import (
    DECLARATION_HEADING,
    FREEZE_RECORD_PATH,
    REGISTRY_PATH,
    PromotionRecordError,
    dump_registry,
    labels_new_to,
)
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.registry_gate import live_actors_at, registry_gate
from tests.test_promotion_record import (
    COMMITTED,
    DECLARED,
    DECLARED_ON,
    NEW_CLAUDE,
    NEW_LABEL,
    PENDING,
    _artifact,
    _commit,
    _git,
    _init,
    _live_fleet,
    _registered,
    _write,
)

ROOT = Path(__file__).resolve().parents[1]
MAIN_AT = datetime(2026, 10, 12, tzinfo=UTC)
STAGING_AT = datetime(2026, 10, 12, 12, tzinfo=UTC)
RECORD = "# Freeze record\n"
#: Main's record once the merge-stamping rule is declared, as DECLARED names it.
DECLARED_RECORD = f"{RECORD}\n- **{DECLARATION_HEADING}, {DECLARED_ON}.** Declared.\n"


def _history(
    tmp_path: Path,
    *,
    main_registry: dict[str, Any] | None = DECLARED,
    staging_registry: dict[str, Any] | None = None,
    main_digest: str = "sha256:" + "c" * 64,
    main_record: str = DECLARED_RECORD,
) -> tuple[Path, str]:
    """``main`` with ``main_registry`` and one prediction; ``staging`` registering proc-v10."""
    repo = _init(tmp_path)
    if main_registry is not None:
        _write(repo, REGISTRY_PATH, dump_registry(main_registry))
    _write(repo, FREEZE_RECORD_PATH, main_record)
    _artifact(repo, "predictions", 1, main_digest)
    _commit(repo, "main", MAIN_AT)
    _git(repo, "switch", "-q", "-c", "staging")
    _write(repo, REGISTRY_PATH, dump_registry(staging_registry or _registered()))
    _write(repo, FREEZE_RECORD_PATH, main_record + "- staging\n")
    return repo, _commit(repo, "register proc-v10", STAGING_AT)


def _problems(repo: Path, at: str, actors: list[LiveActor] | None = None) -> list[str]:
    return registry_gate(repo, at, "main", actors or _live_fleet()).problems


def test_a_clean_registration_passes_and_counts_its_pending_rows(tmp_path: Path) -> None:
    repo, at = _history(tmp_path)
    result = registry_gate(repo, at, "main", _live_fleet())
    assert result.problems == []
    # proc-v10's counting instant, its one new blessing, the window it opens and
    # the claude-baseline window it closes.
    assert result.pending == 4


def test_a_pending_digest_already_in_mains_ledger_is_refused(tmp_path: Path) -> None:
    repo, at = _history(tmp_path, main_digest=NEW_CLAUDE)
    (problem,) = _problems(repo, at)
    assert "claude-baseline" in problem and NEW_CLAUDE in problem
    assert "already stamps 1 committed predictions on main" in problem


def test_an_unregistered_live_digest_is_refused(tmp_path: Path) -> None:
    repo, at = _history(tmp_path)
    stray = "sha256:" + "e" * 64
    fleet = _live_fleet()
    fleet[-1] = LiveActor(fleet[-1].role, fleet[-1].actor_id, stray)
    (problem,) = _problems(repo, at, fleet)
    assert fleet[-1].actor_id in problem and stray in problem and "register-process" in problem


def test_a_new_window_that_leaves_its_predecessor_open_is_refused(tmp_path: Path) -> None:
    registry = _registered()
    for window in registry["windows"]:
        if window["closes"] == PENDING:
            window["closes"] = None
    repo, at = _history(tmp_path, staging_registry=registry)
    problems = _problems(repo, at)
    assert any("claude-baseline has 2 open windows" in p for p in problems)


def test_two_pending_windows_for_one_predictor_are_refused(tmp_path: Path) -> None:
    registry = _registered()
    twin = copy.deepcopy(registry["windows"][-1])
    twin["digest"] = "sha256:" + "f" * 64
    registry["windows"].append(twin)
    blessing = next(b for b in registry["blessings"] if b["digest"] == NEW_CLAUDE)
    registry["blessings"].append({**blessing, "digest": twin["digest"]})
    repo, at = _history(tmp_path, staging_registry=registry)
    problems = _problems(repo, at)
    assert any("claude-baseline has 2 open windows" in p for p in problems), problems


def test_a_revoked_earlier_window_leaves_one_open(tmp_path: Path) -> None:
    """The invariant counts unrevoked windows only: a revoked predecessor is not open."""
    registry = _registered()
    for window in registry["windows"]:
        if window["closes"] == PENDING:
            window["closes"] = None
            window["revoked_at"] = "2026-10-12T06:00:00Z"
    repo, at = _history(tmp_path, staging_registry=registry)
    assert not any("open windows" in p for p in _problems(repo, at))


def test_a_new_labels_prereg_tag_already_minted_is_refused(tmp_path: Path) -> None:
    repo, at = _history(tmp_path)
    _git(repo, "tag", "-a", f"prereg/{NEW_LABEL}", "-m", "early", at)
    problems = _problems(repo, at)
    assert any(f"prereg/{NEW_LABEL} already exists" in p for p in problems)


def test_a_repeated_boundary_name_is_refused(tmp_path: Path) -> None:
    registry = register_boundary(
        _registered(), "a-boundary", predictors=None, reach="all", gradual=False
    )
    registry["harness_boundaries"].append(copy.deepcopy(registry["harness_boundaries"][-1]))
    repo, at = _history(tmp_path, staging_registry=registry)
    assert any("'a-boundary' is registered 2 times" in p for p in _problems(repo, at))


def test_a_pending_row_already_on_main_is_refused(tmp_path: Path) -> None:
    main = register_boundary(DECLARED, "stuck", predictors=None, reach="all", gradual=False)
    repo, at = _history(tmp_path, main_registry=main, staging_registry=main)
    problems = _problems(repo, at)
    assert any("boundary stuck: pending on main" in p for p in problems)


def test_a_registry_that_does_not_load_is_refused(tmp_path: Path) -> None:
    registry = _registered()
    registry["windows"][-1]["opens"] = copy.deepcopy(COMMITTED["labels"][-1]["since"])
    repo, at = _history(tmp_path, staging_registry=registry)
    assert any("does not load" in p for p in _problems(repo, at))


def test_a_main_without_a_registry_holds_every_label_the_record_moved_in(
    tmp_path: Path,
) -> None:
    """The first promotion to carry the record finds main with no registry at all:
    its labels were frozen by hand, their prereg/ tags made then, so none is new
    and the existing tags refuse nothing — in the gate and in the plan alike."""
    repo, at = _history(tmp_path, main_registry=None, staging_registry=COMMITTED)
    for entry in COMMITTED["labels"]:
        _git(repo, "tag", "-a", f"prereg/{entry['label']}", "-m", "hand freeze", "main")
    fleet = [LiveActor(b["role"], b["actor_id"], b["digest"]) for b in COMMITTED["blessings"]]
    assert registry_gate(repo, at, "main", fleet).problems == []
    assert labels_new_to(COMMITTED, None) == []
    assert labels_new_to(_registered(), DECLARED) == [NEW_LABEL]


def test_pending_rows_on_an_undeclared_main_are_refused(tmp_path: Path) -> None:
    """A batch carrying a pending boundary while main has not declared the rule:
    no merge would stamp it, so the declaration has to land first."""
    staging = register_boundary(DECLARED, "early", predictors=None, reach="all", gradual=False)
    repo, at = _history(
        tmp_path, main_registry=COMMITTED, staging_registry=staging, main_record=RECORD
    )
    problems = _problems(repo, at)
    assert any(
        "1 pending registration(s)" in p and "merge_stamping_declared" in p for p in problems
    )


def test_pending_rows_on_a_registry_less_main_are_refused(tmp_path: Path) -> None:
    staging = register_boundary(DECLARED, "early", predictors=None, reach="all", gradual=False)
    repo, at = _history(tmp_path, main_registry=None, staging_registry=staging, main_record=RECORD)
    assert any("pending registration(s)" in p for p in _problems(repo, at))


def test_a_declared_registry_without_its_entry_is_refused(tmp_path: Path) -> None:
    staging = register_boundary(DECLARED, "early", predictors=None, reach="all", gradual=False)
    repo, at = _history(
        tmp_path, main_registry=DECLARED, staging_registry=staging, main_record=RECORD
    )
    assert any("holds no entry headed" in p for p in _problems(repo, at))


def test_a_schema_invalid_registry_is_refused_before_any_field_is_read(tmp_path: Path) -> None:
    registry = _registered()
    del registry["windows"][0]["closes"]
    repo, at = _history(tmp_path, staging_registry=registry)
    result = registry_gate(repo, at, "main", _live_fleet())
    assert result.pending == 0
    assert len(result.problems) == 1 and "does not load" in result.problems[0]


def test_a_batch_without_a_registry_is_refused_first(tmp_path: Path) -> None:
    repo = _init(tmp_path)
    _write(repo, FREEZE_RECORD_PATH, RECORD)
    at = _commit(repo, "no registry", MAIN_AT)
    result = registry_gate(repo, at, "main", _live_fleet())
    assert result.problems == [f"no {REGISTRY_PATH} at {at}"]


def test_a_batch_carrying_two_new_labels_is_refused(tmp_path: Path) -> None:
    main = copy.deepcopy(DECLARED)
    main["labels"] = main["labels"][:-1]
    repo, at = _history(tmp_path, main_registry=main)
    problems = _problems(repo, at)
    assert any("2 labels new to main" in p and "one label per promotion" in p for p in problems)


def test_an_empty_registry_file_bootstraps_nothing() -> None:
    """Only an absent registry file predates the record; a present empty one
    holds no label, so every label is new to it."""
    labels = [entry["label"] for entry in COMMITTED["labels"]]
    assert labels_new_to(COMMITTED, {}) == labels
    assert labels_new_to(COMMITTED, None) == []


# --- the live digests --------------------------------------------------------


def _carry_fleet(repo: Path) -> list[str]:
    """Commit ROOT's actor registries and each enabled actor's prompt into ``repo``."""
    config = ROOT / "config"
    paths = ["config/predictors.yaml", "config/evaluators.yaml"]
    paths += [str(p.prompt) for p in enabled_predictors(config / "predictors.yaml")]
    paths += [str(e.prompt) for e in enabled_evaluators(config / "evaluators.yaml")]
    for path in paths:
        _write(repo, path, (ROOT / path).read_bytes().decode("utf-8"))
    return paths


def test_the_live_digests_are_read_from_the_commits_own_tree(tmp_path: Path) -> None:
    repo = _init(tmp_path)
    _carry_fleet(repo)
    at = _commit(repo, "fleet", MAIN_AT)
    expected = [
        (role, actor, process_version.digest_for_actor(ROOT, ROOT / "config", role, actor))
        for role, actor in [
            ("predictor", p.id) for p in enabled_predictors(ROOT / "config/predictors.yaml")
        ]
        + [("evaluator", e.id) for e in enabled_evaluators(ROOT / "config/evaluators.yaml")]
    ]
    # A later commit changing a prompt moves nothing read at `at`.
    paths = _carry_fleet(repo)
    _write(repo, paths[2], "moved\n")
    _commit(repo, "move", STAGING_AT)
    assert [(a.role, a.actor_id, a.digest) for a in live_actors_at(repo, at)] == expected


def test_a_tree_missing_a_prompt_is_refused(tmp_path: Path) -> None:
    repo = _init(tmp_path)
    paths = _carry_fleet(repo)
    (repo / paths[2]).unlink()
    at = _commit(repo, "fleet", MAIN_AT)
    with pytest.raises(PromotionRecordError, match="missing at"):
        live_actors_at(repo, at)


def _cli(repo: Path, at: str) -> Any:
    previous = Path.cwd()
    os.chdir(repo)
    try:
        return CliRunner().invoke(app, ["registry-gate", "--at", at, "--main-ref", "main"])
    finally:
        os.chdir(previous)


def test_the_command_passes_a_registered_fleet_and_refuses_a_moved_one(tmp_path: Path) -> None:
    repo = _init(tmp_path)
    paths = _carry_fleet(repo)
    _write(repo, REGISTRY_PATH, dump_registry(DECLARED))
    _write(repo, FREEZE_RECORD_PATH, RECORD)
    _commit(repo, "main", MAIN_AT)
    _git(repo, "switch", "-q", "-c", "staging")
    clean = _git(repo, "rev-parse", "HEAD")
    result = _cli(repo, clean)
    assert result.exit_code == 0, result.output
    assert "registry: 0 pending, step 0 clean" in result.output

    _write(repo, paths[2], "a prompt nobody registered\n")
    moved = _commit(repo, "move a prompt", STAGING_AT)
    result = _cli(repo, moved)
    assert result.exit_code == 1
    assert "::error::registry:" in result.output and "register-process" in result.output


def test_the_committed_registry_is_clean_against_itself() -> None:
    """The real fleet on this tree is registered: the gate's second check holds
    for the record as committed, so a batch carrying it unchanged passes."""
    registered = {b["digest"] for b in json.loads((ROOT / REGISTRY_PATH).read_text())["blessings"]}
    config = ROOT / "config"
    for role, entries in (
        ("predictor", enabled_predictors(config / "predictors.yaml")),
        ("evaluator", enabled_evaluators(config / "evaluators.yaml")),
    ):
        for entry in entries:
            digest = process_version.digest_for_actor(ROOT, config, role, entry.id)
            assert digest in registered, (
                f"{role} {entry.id} computes {digest}, which process_registry.json does not "
                "register: run `fedcourts register-process` in the PR that moved it"
            )
