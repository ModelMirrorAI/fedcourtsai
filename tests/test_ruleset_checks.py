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
    ADMIN_ROLE_ID,
    MAIN_APPROVAL_RULESET,
    PROMOTE_BRANCH_PATTERN,
    PROMOTE_CREATION_RULESET,
    PROMOTE_FREEZE_RULESET,
    RECORD_TAG_NAMESPACES,
    STAGING_PR_RULESET,
    Expected,
    ruleset_problems,
)

TEAM, DATA_APP, DEV_APP, AGENTS_TEAM = 101, 202, 303, 404
EXPECTED = Expected(reviewer_team_id=TEAM, data_app_id=DATA_APP, dev_app_id=DEV_APP)
ADMIN_ALWAYS = {"actor_id": ADMIN_ROLE_ID, "actor_type": "RepositoryRole", "bypass_mode": "always"}

GATE_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh"


def _branch(name: str, include: list[str], rules: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": include, "exclude": []}},
        "rules": rules,
    }


def _promote() -> list[dict[str, Any]]:
    """The promotion train's two candidate-branch rulesets: creation by the dev
    App alone, and a freeze the admin role alone bypasses."""
    creation = _branch(PROMOTE_CREATION_RULESET, [PROMOTE_BRANCH_PATTERN], [{"type": "creation"}])
    creation["bypass_actors"] = [
        {"actor_id": DEV_APP, "actor_type": "Integration", "bypass_mode": "always"},
        dict(ADMIN_ALWAYS),
    ]
    freeze = _branch(
        PROMOTE_FREEZE_RULESET,
        [PROMOTE_BRANCH_PATTERN],
        [{"type": "update"}, {"type": "deletion"}, {"type": "non_fast_forward"}],
    )
    freeze["bypass_actors"] = [dict(ADMIN_ALWAYS)]
    return [creation, freeze]


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
                            "reviewer": {"id": TEAM, "type": "Team"},
                        }
                    ],
                },
            }
        ],
    )
    approval["bypass_actors"] = [
        {"actor_id": ADMIN_ROLE_ID, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"},
        {"actor_id": DEV_APP, "actor_type": "Integration", "bypass_mode": "pull_request"},
        {"actor_id": DATA_APP, "actor_type": "Integration", "bypass_mode": "always"},
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
    staging["bypass_actors"] = [dict(ADMIN_ALWAYS)]
    record = [f"refs/tags/{ns}/**" for ns in RECORD_TAG_NAMESPACES]
    protect = {
        "name": "tags: protect record",
        "target": "tag",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": record, "exclude": []}},
        "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}, {"type": "update"}],
        "bypass_actors": [],
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
        "bypass_actors": [
            {"actor_id": DATA_APP, "actor_type": "Integration", "bypass_mode": "always"},
            dict(ADMIN_ALWAYS),
        ],
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
        "bypass_actors": [dict(ADMIN_ALWAYS)],
    }
    return [approval, staging, protect, writer, others, *_promote()]


def _approval_params(rulesets: list[dict[str, Any]]) -> dict[str, Any]:
    params: dict[str, Any] = rulesets[0]["rules"][0]["parameters"]
    return params


def test_the_documented_arrangement_passes() -> None:
    assert ruleset_problems(_good(), EXPECTED) == []


def test_a_missing_approval_ruleset_is_named() -> None:
    rulesets = [r for r in _good() if r["name"] != MAIN_APPROVAL_RULESET]
    assert any(MAIN_APPROVAL_RULESET in p for p in ruleset_problems(rulesets, EXPECTED))


@pytest.mark.parametrize("enforcement", ["disabled", "evaluate"])
def test_an_approval_ruleset_not_enforced_is_named(enforcement: str) -> None:
    rulesets = _good()
    rulesets[0]["enforcement"] = enforcement
    assert any("not active" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_an_approval_count_alone_is_not_enough() -> None:
    # Without the team requirement any write holder's approval counts — the
    # agent account's included — which is the failure the team exists to stop.
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"] = []
    assert any("maintainers team" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_a_team_scoped_to_some_files_does_not_cover_main() -> None:
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"][0]["file_patterns"] = ["docs/**"]
    assert any("maintainers team" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_zero_required_approvals_is_named() -> None:
    rulesets = _good()
    _approval_params(rulesets)["required_approving_review_count"] = 0
    assert any("no approving review" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_stale_approvals_on_main_are_named() -> None:
    rulesets = _good()
    _approval_params(rulesets)["dismiss_stale_reviews_on_push"] = False
    assert any("stale approvals" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_rebase_on_main_is_named() -> None:
    rulesets = _good()
    _approval_params(rulesets)["allowed_merge_methods"] = ["merge", "squash", "rebase"]
    assert any("merge methods" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_a_human_bypass_that_is_not_pull_request_only_is_named() -> None:
    rulesets = _good()
    rulesets[0]["bypass_actors"][0]["bypass_mode"] = "always"
    assert any("RepositoryRole" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_another_team_as_the_required_reviewer_is_named() -> None:
    # The agent account sits in a team too; naming it would let its own
    # approval satisfy main's rule.
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"][0]["reviewer"]["id"] = AGENTS_TEAM
    assert any("maintainers team" in p for p in ruleset_problems(rulesets, EXPECTED))


@pytest.mark.parametrize(
    "actor",
    [
        {"actor_id": 4, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"},
        {"actor_id": AGENTS_TEAM, "actor_type": "Team", "bypass_mode": "pull_request"},
        {"actor_id": 999, "actor_type": "Integration", "bypass_mode": "pull_request"},
        {"actor_id": 7, "actor_type": "DeployKey", "bypass_mode": "always"},
    ],
)
def test_a_bypass_actor_the_docs_do_not_name_is_named(actor: dict[str, Any]) -> None:
    # The write role, a team holding the agent account, a third App or a
    # deploy key would each let a writer merge into main unapproved.
    rulesets = _good()
    rulesets[0]["bypass_actors"].append(actor)
    problems = ruleset_problems(rulesets, EXPECTED)
    assert any("the docs name no such actor" in p for p in problems)


def test_the_dev_app_with_an_always_bypass_is_named() -> None:
    rulesets = _good()
    rulesets[0]["bypass_actors"][1]["bypass_mode"] = "always"
    assert any(f"Integration {DEV_APP}" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_an_unread_bypass_list_is_a_finding_by_default() -> None:
    # The gate reads as an admin; a document without its list then means the
    # read did not see it, and a check that cannot see it proves nothing.
    rulesets = _good()
    del rulesets[0]["bypass_actors"]
    assert any("without its bypass list" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_an_explicitly_partial_read_skips_the_bypass_lists() -> None:
    rulesets = _good()
    for ruleset in rulesets:
        del ruleset["bypass_actors"]
    partial = Expected(TEAM, DATA_APP, DEV_APP, require_bypass_lists=False)
    assert ruleset_problems(rulesets, partial) == []


def test_main_carved_out_of_the_approval_ruleset_is_named() -> None:
    rulesets = _good()
    rulesets[0]["conditions"]["ref_name"]["exclude"] = ["refs/heads/main"]
    assert any("plainly target main" in p for p in ruleset_problems(rulesets, EXPECTED))


@pytest.mark.parametrize("change", ["exclude", "tag"])
def test_a_staging_ruleset_that_misses_staging_is_named(change: str) -> None:
    rulesets = _good()
    if change == "exclude":
        rulesets[1]["conditions"]["ref_name"]["exclude"] = ["refs/heads/staging"]
    else:
        rulesets[1]["target"] = "tag"
    assert any("plainly target staging" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_a_wildcard_exclude_uncovers_a_namespace() -> None:
    # `refs/tags/results/*` carves the released tags out without naming the
    # namespace pattern; any exclude but another namespace's is read as one.
    rulesets = _good()
    for ruleset in rulesets[2:]:
        ruleset["conditions"]["ref_name"]["exclude"].append("refs/tags/results/*")
    problems = ruleset_problems(rulesets, EXPECTED)
    assert any("of results/**" in p for p in problems)


def test_a_bypass_on_the_tag_protect_ruleset_is_named() -> None:
    rulesets = _good()
    rulesets[2]["bypass_actors"] = [dict(ADMIN_ALWAYS)]
    assert any("tags: protect record" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_the_dev_app_on_a_creation_ruleset_is_named() -> None:
    rulesets = _good()
    rulesets[4]["bypass_actors"].append(
        {"actor_id": DEV_APP, "actor_type": "Integration", "bypass_mode": "always"}
    )
    assert any("tags: restrict creation" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_staging_without_code_owner_review_is_named() -> None:
    rulesets = _good()
    rulesets[1]["rules"][0]["parameters"]["require_code_owner_review"] = False
    assert any("code-owner review" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_staging_last_push_approval_is_named() -> None:
    rulesets = _good()
    rulesets[1]["rules"][0]["parameters"]["require_last_push_approval"] = True
    assert any("most recent push" in p for p in ruleset_problems(rulesets, EXPECTED))


@pytest.mark.parametrize("namespace", RECORD_TAG_NAMESPACES)
def test_each_record_namespace_needs_a_creation_rule(namespace: str) -> None:
    rulesets = _good()
    for ruleset in rulesets[3:5]:
        ruleset["conditions"]["ref_name"]["exclude"].append(f"refs/tags/{namespace}/**")
    problems = ruleset_problems(rulesets, EXPECTED)
    assert any(f"creation of {namespace}/**" in p for p in problems)
    assert len(problems) == 1


def test_without_creation_rulesets_every_namespace_is_named() -> None:
    problems = ruleset_problems([*_good()[:3], *_good()[5:]], EXPECTED)
    assert sorted(problems) == sorted(
        f"no active tag ruleset restricts creation of {ns}/**: "
        + "a record tag can be created by any write holder"
        for ns in RECORD_TAG_NAMESPACES
    )


def test_a_disabled_tag_ruleset_protects_nothing() -> None:
    rulesets = _good()
    rulesets[2]["enforcement"] = "disabled"
    problems = ruleset_problems(rulesets, EXPECTED)
    assert any("update of results/**" in p for p in problems)
    assert any("deletion of promotion/**" in p for p in problems)


def test_a_branch_ruleset_does_not_count_for_tags() -> None:
    rulesets = _good()
    as_branch = copy.deepcopy(rulesets[2])
    as_branch["target"] = "branch"
    rulesets[2] = as_branch
    assert any("update of prereg/**" in p for p in ruleset_problems(rulesets, EXPECTED))


# --- The promotion train's candidate branches --------------------------------


def _without(name: str) -> list[dict[str, Any]]:
    return [r for r in _good() if r["name"] != name]


def test_without_the_promote_rulesets_every_rule_is_named() -> None:
    problems = ruleset_problems(_good()[:5], EXPECTED)
    assert sorted(problems) == sorted(
        f"no active branch ruleset restricts {rule} of promote/**: "
        + f"a promotion candidate can be {what}"
        for rule, what in (
            ("creation", "created by any write holder"),
            ("update", "moved after it is cut"),
            ("deletion", "deleted"),
            ("non_fast_forward", "force-pushed"),
        )
    )


def test_a_missing_creation_rule_lets_anyone_cut_a_candidate() -> None:
    problems = ruleset_problems(_without(PROMOTE_CREATION_RULESET), EXPECTED)
    assert problems == [
        "no active branch ruleset restricts creation of promote/**: "
        + "a promotion candidate can be created by any write holder"
    ]


def test_a_missing_freeze_lets_a_candidate_move() -> None:
    problems = ruleset_problems(_without(PROMOTE_FREEZE_RULESET), EXPECTED)
    assert any("update of promote/**" in p for p in problems)
    assert any("deletion of promote/**" in p for p in problems)


def test_the_dev_app_bypassing_the_freeze_is_named() -> None:
    """The App may create a candidate, never move or delete one."""
    rulesets = _good()
    rulesets[6]["bypass_actors"].append(
        {"actor_id": DEV_APP, "actor_type": "Integration", "bypass_mode": "always"}
    )
    assert any(f"Integration {DEV_APP}" in p for p in ruleset_problems(rulesets, EXPECTED))


def test_one_ruleset_holding_both_rules_cannot_let_the_dev_app_bypass() -> None:
    """Whatever the name: a ruleset that freezes candidates admits no App bypass,
    so folding creation into the freeze with the App on its list is a finding."""
    creation, freeze = _promote()
    freeze["rules"].append({"type": "creation"})
    freeze["bypass_actors"] = creation["bypass_actors"]
    problems = ruleset_problems([*_good()[:5], freeze], EXPECTED)
    assert any(f"Integration {DEV_APP}" in p for p in problems)


def test_another_identity_allowed_to_cut_is_named() -> None:
    rulesets = _good()
    rulesets[5]["bypass_actors"].append(
        {"actor_id": DATA_APP, "actor_type": "Integration", "bypass_mode": "always"}
    )
    assert any(f"Integration {DATA_APP}" in p for p in ruleset_problems(rulesets, EXPECTED))


@pytest.mark.parametrize(
    "include",
    [["refs/heads/promote/*"], ["refs/heads/staging"], ["refs/heads/promote/2026-*"]],
)
def test_a_pattern_short_of_every_candidate_covers_none(include: list[str]) -> None:
    """`promote/*` would leave `promote/a/b` open; only `promote/**` (or ~ALL) covers."""
    rulesets = _good()
    for ruleset in rulesets[5:]:
        ruleset["conditions"]["ref_name"]["include"] = include
    problems = ruleset_problems(rulesets, EXPECTED)
    assert any("creation of promote/**" in p for p in problems)
    assert any("update of promote/**" in p for p in problems)


def test_an_exclude_uncovers_the_candidates() -> None:
    rulesets = _good()
    rulesets[6]["conditions"]["ref_name"]["exclude"] = ["refs/heads/promote/old/**"]
    assert any("update of promote/**" in p for p in ruleset_problems(rulesets, EXPECTED))


_CLI = [
    "assert-rulesets",
    "--reviewer-team-id",
    str(TEAM),
    "--data-app-id",
    str(DATA_APP),
    "--dev-app-id",
    str(DEV_APP),
]


def _write(directory: Path, rulesets: list[dict[str, Any]]) -> None:
    directory.mkdir()
    for index, ruleset in enumerate(rulesets):
        (directory / f"{index}.json").write_text(json.dumps(ruleset))


def test_the_cli_passes_the_documented_arrangement(tmp_path: Path) -> None:
    _write(tmp_path / "r", _good())
    result = CliRunner().invoke(app, [*_CLI, "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 0, result.output
    assert "rulesets OK (7 read)" in result.output


def test_the_cli_fails_and_names_the_problem(tmp_path: Path) -> None:
    rulesets = _good()
    _approval_params(rulesets)["required_reviewers"] = []
    _write(tmp_path / "r", rulesets)
    result = CliRunner().invoke(app, [*_CLI, "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 1
    assert "maintainers team" in result.output


def test_the_cli_refuses_an_empty_read(tmp_path: Path) -> None:
    (tmp_path / "r").mkdir()
    result = CliRunner().invoke(app, [*_CLI, "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 1
    assert "no ruleset documents" in result.output


def test_the_cli_refuses_an_unparseable_document(tmp_path: Path) -> None:
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "1.json").write_text("{not json")
    result = CliRunner().invoke(app, [*_CLI, "--rulesets-dir", str(tmp_path / "r")])
    assert result.exit_code == 1


def test_the_gate_fetches_every_ruleset_whole_and_hands_them_to_the_check() -> None:
    """The list endpoint omits rules, so each ruleset is read by id; pin the
    script to that read and to the tested command that judges it."""
    script = GATE_SCRIPT.read_text()
    contexts = script[script.index("contexts() {") : script.index("registry() {")]
    assert 'gh api "repos/${REPO}/rulesets/${id}"' in contexts
    assert "uv run fedcourts assert-rulesets --rulesets-dir" in contexts
    # Read as an admin, or the bypass lists are invisible and checked by nobody.
    assert ".permissions.admin" in contexts
    assert "--allow-unread-bypass" not in contexts
