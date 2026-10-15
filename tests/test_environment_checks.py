"""The `corpus-check` environment's gate (``fedcourtsai.environment_checks``).

The read-only role trusts this environment, so a missing reviewer, an open
branch policy or a stray secret hands that role out. The promotion gate's
`contexts` stage and the lane's plan job both decide on these predicates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import environment_checks as ec
from fedcourtsai.cli import app

APPROVER = "modelmirror"
APPROVER_ID = 7


def _environment(
    *,
    reviewers: list[dict[str, Any]] | None = None,
    protected_branches: bool = False,
    custom: bool = True,
) -> dict[str, Any]:
    if reviewers is None:
        reviewers = [{"type": "User", "reviewer": {"login": APPROVER, "id": APPROVER_ID}}]
    return {
        "name": "corpus-check",
        "protection_rules": [
            {"type": "required_reviewers", "prevent_self_review": False, "reviewers": reviewers},
            {"type": "branch_policy"},
        ],
        "deployment_branch_policy": {
            "protected_branches": protected_branches,
            "custom_branch_policies": custom,
        },
    }


MAIN_ONLY = {"total_count": 1, "branch_policies": [{"name": "main", "type": "branch"}]}
NO_SECRETS: dict[str, Any] = {"total_count": 0, "secrets": []}
ROLE_VARIABLE_ITEMS: list[dict[str, Any]] = [
    {"name": "AWS_ROLE_TO_ASSUME_READONLY"},
    {"name": "AWS_REGION"},
    {"name": "CORPUS_BASE_URL"},
]
ROLE_VARIABLES = {"total_count": 3, "variables": ROLE_VARIABLE_ITEMS}


def _gate(**overrides: Any) -> list[str]:
    values: dict[str, Any] = {
        "environment": _environment(),
        "branch_policies": MAIN_ONLY,
        "secrets": NO_SECRETS,
        "variables": ROLE_VARIABLES,
        "approver_login": APPROVER,
        "approver_id": APPROVER_ID,
    }
    values.update(overrides)
    return ec.environment_problems(
        values["environment"],
        values["branch_policies"],
        values["secrets"],
        values["variables"],
        approver_login=values["approver_login"],
        approver_id=values["approver_id"],
    )


def test_the_provisioned_shape_passes() -> None:
    assert _gate() == []
    assert ec.protection_problems(_environment(), MAIN_ONLY, approver_login="ModelMirror") == []


def test_fewer_variables_pass() -> None:
    assert _gate(variables={"variables": [{"name": "AWS_REGION"}]}) == []


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"environment": None}, "does not exist"),
        ({"approver_login": None}, "no approver is configured"),
        ({"approver_id": None}, "user id was unread"),
        ({"environment": _environment(reviewers=[])}, "no required-reviewer rule"),
        (
            {
                "environment": _environment(
                    reviewers=[{"type": "Team", "reviewer": {"slug": APPROVER, "id": APPROVER_ID}}]
                )
            },
            "no required-reviewer rule",
        ),
        (
            {
                "environment": _environment(
                    reviewers=[{"type": "User", "reviewer": {"login": APPROVER, "id": 8}}]
                )
            },
            "no required-reviewer rule",
        ),
        ({"environment": _environment(protected_branches=True, custom=False)}, "custom"),
        ({"environment": _environment(custom=False)}, "custom"),
        ({"branch_policies": None}, "policies were unread"),
        ({"branch_policies": {"branch_policies": []}}, "admits: none"),
        (
            {"branch_policies": {"branch_policies": [{"name": "*", "type": "branch"}]}},
            "exactly `main`",
        ),
        (
            {
                "branch_policies": {
                    "branch_policies": [
                        {"name": "main", "type": "branch"},
                        {"name": "staging", "type": "branch"},
                    ]
                }
            },
            "exactly `main`",
        ),
        (
            {"branch_policies": {"branch_policies": [{"name": "main", "type": "tag"}]}},
            "exactly `main`",
        ),
        ({"secrets": None}, "secrets were unread"),
        ({"secrets": {"secrets": [{"name": "DEV_APP_PRIVATE_KEY"}]}}, "1 secret(s)"),
        ({"variables": None}, "variables were unread"),
        (
            {"variables": {"variables": [*ROLE_VARIABLE_ITEMS, {"name": "AWS_ROLE"}]}},
            "AWS_ROLE",
        ),
    ],
)
def test_each_weakening_is_named(overrides: dict[str, Any], fragment: str) -> None:
    problems = _gate(**overrides)
    assert any(fragment in problem for problem in problems), problems


def test_the_plan_cannot_see_contents_but_still_needs_the_protection() -> None:
    # The plan's read has no secrets or variables listing; protection alone.
    assert ec.protection_problems(None, MAIN_ONLY, approver_login=APPROVER)
    assert ec.protection_problems(_environment(reviewers=[]), MAIN_ONLY, approver_login=APPROVER)


def test_the_gate_cli_reads_the_four_listings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "corpus-check.yaml").write_text("approver: modelmirror\n")
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(tmp_path))
    files = {
        "environment": _environment(),
        "branch-policies": MAIN_ONLY,
        "secrets": NO_SECRETS,
        "variables": ROLE_VARIABLES,
    }
    for name, document in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(document))
    args = [
        "assert-corpus-check-environment",
        "--environment-file",
        str(tmp_path / "environment.json"),
        "--branch-policies-file",
        str(tmp_path / "branch-policies.json"),
        "--secrets-file",
        str(tmp_path / "secrets.json"),
        "--variables-file",
        str(tmp_path / "variables.json"),
    ]
    runner = CliRunner()
    passed = runner.invoke(app, [*args, "--approver-id", str(APPROVER_ID)])
    assert passed.exit_code == 0, passed.output
    # No approver id (the gate could not resolve it) fails closed.
    assert runner.invoke(app, args).exit_code == 1
    (tmp_path / "secrets.json").unlink()
    assert runner.invoke(app, [*args, "--approver-id", str(APPROVER_ID)]).exit_code == 1


def test_the_promotion_gate_checks_the_environment_unconditionally() -> None:
    """The trust exists from the moment the role names the environment, before
    any workflow binding it reaches `main`, so the gate's check must not wait
    for one: it sits in the `contexts` stage outside any `grep` of main's
    workflows, resolves the approver's id itself, and fails the stage."""
    script = (Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh").read_text()
    contexts = script[script.index("\ncontexts() {") : script.index("\nregistry() {")]
    tail = contexts[contexts.index("The corpus-check environment") :]
    assert "uv run fedcourts corpus-check-approver" in tail
    assert 'gh api "users/${approver}"' in tail
    for listing in ("deployment-branch-policies", "secrets", "variables"):
        assert listing in tail
    assert "uv run fedcourts assert-corpus-check-environment" in tail
    assert "fail=1" in tail
    assert "grep -rq" not in tail


@pytest.mark.parametrize(
    "extra",
    [
        {"type": "User", "reviewer": {"login": "second-maintainer", "id": 9}},
        {"type": "Team", "reviewer": {"slug": "maintainers", "id": 3}},
    ],
)
def test_the_approver_must_be_the_only_reviewer(extra: dict[str, Any]) -> None:
    approver = {"type": "User", "reviewer": {"login": APPROVER, "id": APPROVER_ID}}
    environment = _environment(reviewers=[approver, extra])
    problems = _gate(environment=environment)
    assert any("exactly `modelmirror`" in problem for problem in problems), problems
    # The plan's lighter read refuses it too.
    assert ec.protection_problems(environment, MAIN_ONLY, approver_login=APPROVER)


def test_a_second_reviewer_rule_counts_toward_the_set() -> None:
    environment = _environment()
    environment["protection_rules"].append(
        {
            "type": "required_reviewers",
            "reviewers": [{"type": "Team", "reviewer": {"slug": "maintainers", "id": 3}}],
        }
    )
    assert _gate(environment=environment)
