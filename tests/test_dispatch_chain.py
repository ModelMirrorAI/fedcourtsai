"""When the dispatch chain starts a predict round: relevance and each chain step."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.dispatch_chain import (
    ChainAction,
    ChainMode,
    chain_step,
    forecast_relevance,
    ready_promotion,
)

REPO = "ModelMirrorAI/fedcourtsai"
EVENT = "data/cases/scotus/73281056/events/evt-brief-judgment/event.yaml"

# --- forecast relevance -------------------------------------------------------


def test_a_pointer_bump_and_outcomes_are_not_relevant() -> None:
    relevance = forecast_relevance(
        [
            ("M", "corpus/corpus.db.ref"),
            ("A", "data/cases/scotus/1/events/evt-petition-disposition/outcome.json"),
        ]
    )
    assert not relevance.relevant


def test_an_added_or_changed_event_record_is_relevant() -> None:
    relevance = forecast_relevance([("M", "corpus/corpus.db.ref"), ("A", EVENT), ("M", EVENT)])
    assert relevance.relevant
    assert (relevance.events_added, relevance.events_changed) == (1, 1)


def test_a_deleted_event_record_is_not_relevant() -> None:
    assert not forecast_relevance([("D", EVENT)]).relevant


def test_a_moved_scope_manifest_is_relevant() -> None:
    relevance = forecast_relevance([("M", "data/scope/scope.json")])
    assert relevance.relevant
    assert relevance.scope_changed


@pytest.mark.parametrize(
    "path",
    [
        "data/cases/scotus/1/events/evt-x/event.yaml.bak",
        "data/cases/scotus/1/events/evt-x/predictions/a/b/event.yaml",
        "docs/data/cases/scotus/1/events/evt-x/event.yaml",
    ],
)
def test_only_an_event_record_at_its_own_path_counts(path: str) -> None:
    assert not forecast_relevance([("A", path)]).relevant


# --- the promotion stand-down -------------------------------------------------


def _pull(
    *, draft: bool = False, head: str = "staging", repo: str = REPO, number: int = 2373
) -> dict[str, Any]:
    return {
        "number": number,
        "state": "open",
        "draft": draft,
        "base": {"ref": "main"},
        "head": {"ref": head, "repo": {"full_name": repo}},
    }


def test_a_ready_same_repo_promotion_is_found() -> None:
    assert ready_promotion([_pull()], repo=REPO) == 2373


@pytest.mark.parametrize(
    "pull",
    [_pull(draft=True), _pull(head="feature"), _pull(repo="someone/fork")],
)
def test_drafts_other_heads_and_forks_are_not_a_ready_promotion(pull: dict[str, Any]) -> None:
    assert ready_promotion([pull], repo=REPO) is None


@pytest.mark.parametrize("mode", list(ChainMode))
def test_a_ready_promotion_stands_every_chain_down(mode: ChainMode) -> None:
    step = chain_step(mode, repo=REPO, promotion_pulls=[_pull()], collect_pulls=[_merged()])
    assert step.action is ChainAction.STOP
    assert "#2373 is ready" in step.reason


@pytest.mark.parametrize("mode", list(ChainMode))
def test_an_unread_promotion_list_stands_the_chain_down(mode: ChainMode) -> None:
    step = chain_step(mode, repo=REPO, promotion_pulls=None, collect_pulls=[_merged()])
    assert step.action is ChainAction.STOP


def test_the_pull_chain_dispatches_beside_a_draft_promotion() -> None:
    step = chain_step(ChainMode.PULL, repo=REPO, promotion_pulls=[_pull(draft=True)])
    assert step.action is ChainAction.DISPATCH


# --- the drain wait -----------------------------------------------------------


def _merged() -> dict[str, Any]:
    return {"state": "closed", "merged_at": "2026-10-12T15:00:00Z", "draft": False}


def _drain(collect: list[dict[str, Any]] | None, attempt: int = 1) -> ChainAction:
    return chain_step(
        ChainMode.DRAIN, repo=REPO, promotion_pulls=[], collect_pulls=collect, attempt=attempt
    ).action


def test_a_merged_collect_pr_dispatches_the_next_round() -> None:
    assert _drain([_merged()]) is ChainAction.DISPATCH


def test_an_open_collect_pr_waits() -> None:
    assert _drain([{"state": "open", "draft": False, "merged_at": None}]) is ChainAction.WAIT


@pytest.mark.parametrize(
    "collect",
    [
        [{"state": "open", "draft": True, "merged_at": None}],
        [{"state": "closed", "draft": False, "merged_at": None}],
    ],
)
def test_a_draft_or_unmerged_close_stops(collect: list[dict[str, Any]]) -> None:
    assert _drain(collect) is ChainAction.STOP


def test_no_collect_pr_waits_briefly_then_stops() -> None:
    assert _drain([], attempt=2) is ChainAction.WAIT
    assert _drain([], attempt=3) is ChainAction.STOP


def test_an_unreadable_collect_pr_waits_until_the_last_attempt() -> None:
    assert _drain(None, attempt=39) is ChainAction.WAIT
    assert _drain(None, attempt=40) is ChainAction.STOP


# --- the commands -------------------------------------------------------------

runner = CliRunner()


def test_the_relevance_command_reads_name_status_lines(tmp_path: Path) -> None:
    changes = tmp_path / "changes.txt"
    changes.write_text(f"M\tcorpus/corpus.db.ref\nA\t{EVENT}\n")
    result = runner.invoke(app, ["window-forecast-relevance", "--changes-file", str(changes)])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["relevant"] is True


def test_the_relevance_command_fails_on_a_missing_file(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["window-forecast-relevance", "--changes-file", str(tmp_path / "nope")]
    )
    assert result.exit_code == 1


def test_the_chain_step_command_reads_both_lists(tmp_path: Path) -> None:
    promotions = tmp_path / "promotions.json"
    promotions.write_text(json.dumps([_pull(draft=True)]))
    collect = tmp_path / "collect.json"
    collect.write_text(json.dumps([_merged()]))
    result = runner.invoke(
        app,
        [
            "chain-step",
            "--mode",
            "drain",
            "--repo",
            REPO,
            "--promotion-prs-file",
            str(promotions),
            "--collect-prs-file",
            str(collect),
            "--attempt",
            "5",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["action"] == "dispatch"


def test_the_chain_step_command_stands_down_without_the_promotion_list() -> None:
    result = runner.invoke(app, ["chain-step", "--mode", "pull", "--repo", REPO])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["action"] == "stop"
