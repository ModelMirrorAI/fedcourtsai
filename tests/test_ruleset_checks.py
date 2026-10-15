"""The rulesets the review record and the tag record rest on."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.ruleset_checks import (
    MAIN_APPROVAL_RULESET,
    RECORD_TAG_NAMESPACES,
    STAGING_PR_RULESET,
    ruleset_problems,
)

GATE_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh"


def _branch(name: str, include: list[str], rules: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": include, "exclude": []}},
        "rules": rules,
    }


def _good() -> list[dict[str, Any]]:
    """The arrangement docs/security.md records, in the shape the API returns."""
    approval = _branch(
        MAIN_APPROVAL_RULESET,
        ["~DEFAULT_BRANCH", "refs/heads/main"],
        [
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews_on_push": True,
                    "require_last_push_approval": False,
                    "allowed_merge_methods": ["merge", "squash"],
                    "required_reviewers": [
                        {
                            "file_patterns": ["*"],
                            "minimum_approvals": 1,
                            "reviewer": {"id": 1, "type": "Team"},
                        }
                    ],
                },
            }
        ],
    )
    approval["bypass_actors"] = [
        {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"},
        {"actor_id": 11, "actor_type": "Integration", "bypass_mode": "pull_request"},
        {"actor_id": 12, "actor_type": "Integration", "bypass_mode": "always"},
    ]
    staging = _branch(
        STAGING_PR_RULESET,
        ["refs/heads/staging"],
        [
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 0,
                    "require_code_owner_review": True,
                    "dismiss_stale_reviews_on_push": True,
                    "require_last_push_approval": False,
                },
            }
        ],
    )
    record = [f"refs/tags/{ns}/**" for ns in RECORD_TAG_NAMESPACES]
    protect = {
        "name": "tags: protect record",
        "target": "tag",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": record, "exclude": []}},
        "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}, {"type": "update"}],
    }
    writer = {
        "name": "tags: restrict record creation",
        "target": "tag",
        "enforcement": "active",
        "conditions": {
            "ref_name": {
                "include": ["refs/tags/promotion/**", "refs/tags/prereg/**"],
                "exclude": [],
            }
        },
        "rules": [{"type": "creation"}],
    }
    others = {
        "name": "tags: restrict creation",
        "target": "tag",
        "enforcement": "active",
        "conditions": {
            "ref_name": {
                "include": ["~ALL"],
                "exclude": ["refs/tags/promotion/**", "refs/tags/prereg/**"],
            }
        },
        "rules": [{"type": "creation"}],
    }
    return [approval, staging, protect, writer, others]


def _approval_params(rulesets: list[dict[str, Any]]) -> dict[str, Any]:
    params: dict[str, Any] = rulesets[0]["rules"][0]["parameters"]
    return params


def test_the_documented_arrangement_passes() -> None:
    assert ruleset_problems(_good()) == []


def test_a_missing_approval_ruleset_is_named() -> None:
    rulesets = [r for r in _good() if r["name"] != MAIN_APPROVAL_RULESET]
    assert any(MAIN_APPROVAL_RULESET in p for p in ruleset_problems(rulesets))


@pytest.mark.parametrize("enforcement", ["disabled", "evaluate"])
def test_an_approval_ruleset_not_enforced_is_named(enforcement: str) -> None:
    rulesets = _good()
    rulesets[0]["enforcement"] = enforcement
    assert any("not active" in p for p in ruleset_problems(rulesets))


def test_an_approval_count_alone_is_not_enough() -> None:
    # Without the team requirement any write holder's approval counts — the
    # agent account's included — which is the failure the team exists to stop.
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"] = []
    assert any("required-reviewer team" in p for p in ruleset_problems(rulesets))


def test_a_team_scoped_to_some_files_does_not_cover_main() -> None:
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"][0]["file_patterns"] = ["docs/**"]
    assert any("required-reviewer team" in p for p in ruleset_problems(rulesets))


def test_zero_required_approvals_is_named() -> None:
    rulesets = _good()
    _approval_params(rulesets)["required_approving_review_count"] = 0
    assert any("no approving review" in p for p in ruleset_problems(rulesets))


def test_stale_approvals_on_main_are_named() -> None:
    rulesets = _good()
    _approval_params(rulesets)["dismiss_stale_reviews_on_push"] = False
    assert any("stale approvals" in p for p in ruleset_problems(rulesets))


def test_rebase_on_main_is_named() -> None:
    rulesets = _good()
    _approval_params(rulesets)["allowed_merge_methods"] = ["merge", "squash", "rebase"]
    assert any("merge methods" in p for p in ruleset_problems(rulesets))


def test_a_human_bypass_that_is_not_pull_request_only_is_named() -> None:
    rulesets = _good()
    rulesets[0]["bypass_actors"][0]["bypass_mode"] = "always"
    assert any("RepositoryRole" in p for p in ruleset_problems(rulesets))


def test_an_unread_bypass_list_is_not_a_finding() -> None:
    # A non-admin token gets no bypass list back; the rest still checks.
    rulesets = _good()
    del rulesets[0]["bypass_actors"]
    assert ruleset_problems(rulesets) == []


def test_staging_without_code_owner_review_is_named() -> None:
    rulesets = _good()
    rulesets[1]["rules"][0]["parameters"]["require_code_owner_review"] = False
    assert any("code-owner review" in p for p in ruleset_problems(rulesets))


def test_staging_last_push_approval_is_named() -> None:
    rulesets = _good()
    rulesets[1]["rules"][0]["parameters"]["require_last_push_approval"] = True
    assert any("most recent push" in p for p in ruleset_problems(rulesets))


@pytest.mark.parametrize("namespace", RECORD_TAG_NAMESPACES)
def test_each_record_namespace_needs_a_creation_rule(namespace: str) -> None:
    rulesets = _good()
    for ruleset in rulesets[3:]:
        ruleset["conditions"]["ref_name"]["exclude"].append(f"refs/tags/{namespace}/**")
    problems = ruleset_problems(rulesets)
    assert any(f"creation of {namespace}/**" in p for p in problems)
    assert len(problems) == 1


def test_without_creation_rulesets_every_namespace_is_named() -> None:
    problems = ruleset_problems(_good()[:3])
    assert sorted(problems) == sorted(
        f"no active tag ruleset restricts creation of {ns}/**: "
        + "a record tag can be created by any write holder"
        for ns in RECORD_TAG_NAMESPACES
    )


def test_a_disabled_tag_ruleset_protects_nothing() -> None:
    rulesets = _good()
    rulesets[2]["enforcement"] = "disabled"
    problems = ruleset_problems(rulesets)
    assert any("update of results/**" in p for p in problems)
    assert any("deletion of promotion/**" in p for p in problems)


def test_a_branch_ruleset_does_not_count_for_tags() -> None:
    rulesets = _good()
    as_branch = copy.deepcopy(rulesets[2])
    as_branch["target"] = "branch"
    rulesets[2] = as_branch
    assert any("update of prereg/**" in p for p in ruleset_problems(rulesets))


def _write(directory: Path, rulesets: list[dict[str, Any]]) -> None:
    directory.mkdir()
    for index, ruleset in enumerate(rulesets):
        (directory / f"{index}.json").write_text(json.dumps(ruleset))


def test_the_cli_passes_the_documented_arrangement(tmp_path: Path) -> None:
    _write(tmp_path / "r", _good())
    result = CliRunner().invoke(app, ["assert-rulesets", "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 0, result.output
    assert "rulesets OK (5 read)" in result.output


def test_the_cli_fails_and_names_the_problem(tmp_path: Path) -> None:
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"] = []
    _write(tmp_path / "r", rulesets)
    result = CliRunner().invoke(app, ["assert-rulesets", "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 1
    assert "required-reviewer team" in result.output


def test_the_cli_refuses_an_empty_read(tmp_path: Path) -> None:
    (tmp_path / "r").mkdir()
    result = CliRunner().invoke(app, ["assert-rulesets", "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 1
    assert "no ruleset documents" in result.output


def test_the_cli_refuses_an_unparseable_document(tmp_path: Path) -> None:
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "1.json").write_text("{not json")
    result = CliRunner().invoke(app, ["assert-rulesets", "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 1


def test_the_gate_fetches_every_ruleset_whole_and_hands_them_to_the_check() -> None:
    """The list endpoint omits rules, so each ruleset is read by id; pin the
    script to that read and to the tested command that judges it."""
    script = GATE_SCRIPT.read_text()
    contexts = script[script.index("contexts() {") : script.index("registry() {")]
    assert 'gh api "repos/${REPO}/rulesets/${id}"' in contexts
    assert "uv run fedcourts assert-rulesets --rulesets-dir" in contexts
