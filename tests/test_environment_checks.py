"""The gated environments' checks (``fedcourtsai.environment_checks``).

The read-only role trusts `corpus-check` and `corpus-check-auto`, so a missing
reviewer (on the first), an open branch policy or a stray secret hands that
role out. The promotion gate's
`contexts` stage and the lane's plan job both decide on these predicates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml
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


# The `website` environment: the Buttondown key `post-public-update` drafts with.

WEBSITE_SECRETS: dict[str, Any] = {"total_count": 1, "secrets": [{"name": "BUTTONDOWN_API_KEY"}]}
WEBSITE_VARIABLES: dict[str, Any] = {
    "total_count": 3,
    "variables": [
        {"name": "WEEKLY_SCOTUS_TAG_ID"},
        {"name": "SCOTUS_PREDICTIONS_TAG_ID"},
        {"name": "AI_CASES_TAG_ID"},
    ],
}


def _website(**overrides: Any) -> list[str]:
    values: dict[str, Any] = {
        # No required reviewers: the draft is the hold.
        "environment": _environment(reviewers=[]),
        "branch_policies": MAIN_ONLY,
        "secrets": WEBSITE_SECRETS,
        "variables": WEBSITE_VARIABLES,
    }
    values.update(overrides)
    return ec.website_problems(
        values["environment"], values["branch_policies"], values["secrets"], values["variables"]
    )


def test_the_configured_website_environment_passes() -> None:
    assert _website() == []
    # A reviewer only adds a wait, so it is not a problem either.
    assert _website(environment=_environment()) == []


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"environment": None}, "does not exist"),
        ({"environment": _environment(reviewers=[], custom=False)}, "custom branch policy"),
        (
            {"environment": _environment(reviewers=[], protected_branches=True)},
            "custom branch policy",
        ),
        ({"branch_policies": None}, "branch policies were unread"),
        (
            {
                "branch_policies": {
                    "branch_policies": [
                        {"name": "main", "type": "branch"},
                        {"name": "staging", "type": "branch"},
                    ]
                }
            },
            "admits: main, staging",
        ),
        ({"branch_policies": {"branch_policies": [{"name": "main", "type": "tag"}]}}, "exactly"),
        ({"secrets": None}, "secrets were unread"),
        (
            {"secrets": {"secrets": [{"name": "BUTTONDOWN_API_KEY"}, {"name": "OTHER_KEY"}]}},
            "outside ['BUTTONDOWN_API_KEY']: OTHER_KEY",
        ),
        ({"secrets": NO_SECRETS}, "lacks its secrets: BUTTONDOWN_API_KEY"),
        ({"variables": None}, "variables were unread"),
        (
            {
                "variables": {
                    "variables": [
                        {"name": "WEEKLY_SCOTUS_TAG_ID"},
                        {"name": "SCOTUS_PREDICTIONS_TAG_ID"},
                        {"name": "AI_CASES_TAG_ID"},
                        {"name": "X"},
                    ]
                }
            },
            "outside ['AI_CASES_TAG_ID', 'SCOTUS_PREDICTIONS_TAG_ID', 'WEEKLY_SCOTUS_TAG_ID']: X",
        ),
        (
            {"variables": {"variables": [{"name": "WEEKLY_SCOTUS_TAG_ID"}]}},
            "lacks its variables: AI_CASES_TAG_ID, SCOTUS_PREDICTIONS_TAG_ID",
        ),
    ],
)
def test_each_website_weakening_is_named(overrides: dict[str, Any], fragment: str) -> None:
    problems = _website(**overrides)
    assert any(fragment in problem for problem in problems), problems


def test_the_website_gate_cli_reads_the_four_listings(tmp_path: Path) -> None:
    files = {
        "environment": _environment(reviewers=[]),
        "branch-policies": MAIN_ONLY,
        "secrets": WEBSITE_SECRETS,
        "variables": WEBSITE_VARIABLES,
        "repository-secrets": NO_SECRETS,
        "organization-secrets": NO_SECRETS,
    }
    for name, document in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(document))
    args = [
        "assert-website-environment",
        "--environment-file",
        str(tmp_path / "environment.json"),
        "--branch-policies-file",
        str(tmp_path / "branch-policies.json"),
        "--secrets-file",
        str(tmp_path / "secrets.json"),
        "--variables-file",
        str(tmp_path / "variables.json"),
        "--repository-secrets-file",
        str(tmp_path / "repository-secrets.json"),
        "--organization-secrets-file",
        str(tmp_path / "organization-secrets.json"),
    ]
    runner = CliRunner()
    passed = runner.invoke(app, args)
    assert passed.exit_code == 0, passed.output
    # An absent listing is an unread one, and fails.
    (tmp_path / "variables.json").unlink()
    assert runner.invoke(app, args).exit_code == 1


def test_the_promotion_gate_checks_the_website_environment_unconditionally() -> None:
    """The key is reachable from the moment the environment holds it, so the
    check does not wait for a workflow binding it to reach `main`."""
    script = (Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh").read_text()
    contexts = script[script.index("\ncontexts() {") : script.index("\nregistry() {")]
    tail = contexts[contexts.index('web_base="repos/${REPO}/environments/website"') :]
    for listing in (
        "deployment-branch-policies",
        "secrets",
        "variables",
        "actions/secrets",
        "actions/organization-secrets",
    ):
        assert listing in tail
    assert "uv run fedcourts assert-website-environment" in tail
    assert "fail=1" in tail
    assert "grep -rq" not in tail


def test_the_website_names_are_the_ones_the_workflow_reads() -> None:
    """The gate's expected secret and variable are exactly what the job that
    binds `website` reads, so a rename in one cannot leave the other checking
    a name nothing uses."""
    workflow = (
        Path(__file__).resolve().parent.parent / ".github" / "workflows" / "post-public-update.yml"
    ).read_text()
    assert set(re.findall(r"secrets\.([A-Z0-9_]+)", workflow)) == set(ec.WEBSITE_SECRETS)
    assert set(re.findall(r"vars\.([A-Z0-9_]+)", workflow)) == set(ec.WEBSITE_VARIABLES)


@pytest.mark.parametrize("scope", ["repository", "organization"])
def test_a_shadow_copy_of_the_key_is_refused(scope: str) -> None:
    """`secrets.NAME` falls back to a repository or organization secret, which
    no branch policy guards."""
    shadow = {"secrets": [{"name": "BUTTONDOWN_API_KEY"}, {"name": "UNRELATED"}]}
    listings = {"repository": NO_SECRETS, "organization": NO_SECRETS, scope: shadow}
    problems = ec.shadow_secret_problems(listings["repository"], listings["organization"])
    assert len(problems) == 1
    assert "BUTTONDOWN_API_KEY" in problems[0] and "UNRELATED" not in problems[0]


def test_unrelated_repository_secrets_pass_and_unread_ones_fail() -> None:
    other = {"secrets": [{"name": "UNRELATED"}]}
    assert ec.shadow_secret_problems(other, other) == []
    assert any(
        "repository secrets were unread" in p for p in ec.shadow_secret_problems(None, other)
    )
    assert any("organization" in p for p in ec.shadow_secret_problems(other, None))


# The `corpus-check-auto` environment: the read-only role, unapproved, for an
# allowlisted subcommand at `main`'s own commit. Its branch policy is its one
# control.


def _auto(**overrides: Any) -> list[str]:
    values: dict[str, Any] = {
        "environment": _environment(reviewers=[]),
        "branch_policies": MAIN_ONLY,
        "secrets": NO_SECRETS,
        "variables": ROLE_VARIABLES,
    }
    values.update(overrides)
    return ec.auto_environment_problems(
        values["environment"], values["branch_policies"], values["secrets"], values["variables"]
    )


def test_the_configured_auto_environment_passes() -> None:
    assert _auto() == []
    # A reviewer is the stop for the unapproved path, never a promotion blocker.
    assert _auto(environment=_environment()) == []
    assert ec.auto_protection_problems(_environment(reviewers=[]), MAIN_ONLY) == []


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"environment": None}, "`corpus-check-auto` environment does not exist"),
        ({"environment": _environment(reviewers=[], custom=False)}, "custom branch policy"),
        (
            {"environment": _environment(reviewers=[], protected_branches=True)},
            "custom branch policy",
        ),
        ({"branch_policies": None}, "branch policies were unread"),
        (
            {"branch_policies": {"branch_policies": [{"name": "*", "type": "branch"}]}},
            "admits: *",
        ),
        ({"branch_policies": {"branch_policies": [{"name": "main", "type": "tag"}]}}, "exactly"),
        ({"secrets": None}, "secrets were unread"),
        ({"secrets": {"secrets": [{"name": "TOKEN"}]}}, "1 secret(s)"),
        ({"variables": None}, "variables were unread"),
        (
            {"variables": {"variables": [*ROLE_VARIABLE_ITEMS, {"name": "AWS_ROLE_TO_ASSUME"}]}},
            "AWS_ROLE_TO_ASSUME",
        ),
    ],
)
def test_each_auto_weakening_is_named(overrides: dict[str, Any], fragment: str) -> None:
    problems = _auto(**overrides)
    assert any(fragment in problem for problem in problems), problems


def test_the_plan_routes_to_the_approval_without_the_auto_policy() -> None:
    """The plan's lighter read: no environment, or no `main`-only policy, is a
    problem, and every request then waits on the approval (test_corpus_check)."""
    assert ec.auto_protection_problems(None, MAIN_ONLY)
    assert ec.auto_protection_problems(_environment(reviewers=[]), None)
    assert ec.auto_protection_problems(_environment(reviewers=[], custom=False), MAIN_ONLY)


def test_the_auto_gate_cli_reads_the_four_listings(tmp_path: Path) -> None:
    files = {
        "environment": _environment(reviewers=[]),
        "branch-policies": MAIN_ONLY,
        "secrets": NO_SECRETS,
        "variables": ROLE_VARIABLES,
    }
    for name, document in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(document))
    args = [
        "assert-corpus-check-auto-environment",
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
    passed = runner.invoke(app, args)
    assert passed.exit_code == 0, passed.output
    (tmp_path / "branch-policies.json").unlink()
    assert runner.invoke(app, args).exit_code == 1


def test_the_promotion_gate_checks_the_auto_environment_unconditionally() -> None:
    """The trust names `environment:corpus-check-auto` from the moment the
    maintainer adds it, and an environment that does not exist is one any
    branch's workflow creates unprotected — so the gate requires it, outside
    any `grep` of main's workflows, and fails the stage."""
    script = (Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh").read_text()
    contexts = script[script.index("\ncontexts() {") : script.index("\nregistry() {")]
    start = contexts.index('cca_base="repos/${REPO}/environments/corpus-check-auto"')
    tail = contexts[start : contexts.index("The website environment")]
    for listing in ("deployment-branch-policies", "secrets", "variables"):
        assert listing in tail
    assert "uv run fedcourts assert-corpus-check-auto-environment" in tail
    assert "fail=1" in tail
    assert "grep -rq" not in tail


# The `corpus-write` environment: the one the production read-write role trusts.

WRITER_SECRETS: dict[str, Any] = {
    "total_count": 2,
    "secrets": [{"name": "DATA_APP_PRIVATE_KEY"}, {"name": "COURTLISTENER_API_TOKEN"}],
}
WRITER_VARIABLES: dict[str, Any] = {
    "total_count": 5,
    "variables": [
        {"name": "AWS_ROLE_TO_ASSUME"},
        {"name": "AWS_ROLE_TO_ASSUME_READONLY"},
        {"name": "AWS_REGION"},
        {"name": "CORPUS_BASE_URL"},
        {"name": "DATA_APP_CLIENT_ID"},
    ],
}


def _corpus_write(**overrides: Any) -> list[str]:
    values: dict[str, Any] = {
        # No required reviewers: the writer windows run on a schedule.
        "environment": _environment(reviewers=[]),
        "branch_policies": MAIN_ONLY,
        "secrets": WRITER_SECRETS,
        "variables": WRITER_VARIABLES,
    }
    values.update(overrides)
    return ec.corpus_write_problems(
        values["environment"], values["branch_policies"], values["secrets"], values["variables"]
    )


def test_the_configured_corpus_write_environment_passes() -> None:
    assert _corpus_write() == []
    # The rate caps are optional, and admitted when present.
    caps = [{"name": f"COURTLISTENER_RP{unit}"} for unit in "MHD"]
    items = [*WRITER_VARIABLES["variables"], *caps]
    assert _corpus_write(variables={"total_count": len(items), "variables": items}) == []


@pytest.mark.parametrize("name", sorted(ec.CORPUS_WRITE_REQUIRED_SECRETS))
def test_each_required_corpus_write_secret_is_named_when_missing(name: str) -> None:
    items = [i for i in WRITER_SECRETS["secrets"] if i["name"] != name]
    problems = _corpus_write(secrets={"total_count": len(items), "secrets": items})
    assert problems == [f"the environment lacks its secrets: {name}"]


@pytest.mark.parametrize("name", sorted(ec.CORPUS_WRITE_REQUIRED_VARIABLES))
def test_each_required_corpus_write_variable_is_named_when_missing(name: str) -> None:
    items = [i for i in WRITER_VARIABLES["variables"] if i["name"] != name]
    problems = _corpus_write(variables={"total_count": len(items), "variables": items})
    assert problems == [f"the environment lacks its variables: {name}"]


def test_the_required_names_are_the_admitted_ones_less_the_rate_caps() -> None:
    assert ec.CORPUS_WRITE_REQUIRED_SECRETS == ec.CORPUS_WRITE_SECRETS
    assert {
        "COURTLISTENER_RPM",
        "COURTLISTENER_RPH",
        "COURTLISTENER_RPD",
    } == ec.CORPUS_WRITE_VARIABLES - ec.CORPUS_WRITE_REQUIRED_VARIABLES


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        # A page that is not the whole listing hides names past it.
        (
            {"branch_policies": {**MAIN_ONLY, "total_count": 2}},
            "branch policies were unread or truncated",
        ),
        ({"secrets": {**WRITER_SECRETS, "total_count": 3}}, "secrets were unread or truncated"),
        (
            {"variables": {**WRITER_VARIABLES, "total_count": 31}},
            "variables were unread or truncated",
        ),
    ],
)
def test_a_truncated_corpus_write_listing_is_unread(
    overrides: dict[str, Any], fragment: str
) -> None:
    problems = _corpus_write(**overrides)
    assert any(fragment in problem for problem in problems), problems


def test_a_truncated_listing_is_unread_for_every_environment() -> None:
    """The truncation rule lives in the shared reader, so the corpus-check and
    website checks refuse a partial page too."""
    truncated = {**MAIN_ONLY, "total_count": 2}
    assert any("unread" in p for p in _gate(branch_policies=truncated))
    assert any("unread" in p for p in _website(branch_policies=truncated))
    assert any("unread" in p for p in _gate(variables={**ROLE_VARIABLES, "total_count": 4}))


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"environment": None}, "`corpus-write` environment does not exist"),
        ({"environment": _environment(reviewers=[], custom=False)}, "custom branch policy"),
        (
            {"environment": _environment(reviewers=[], protected_branches=True)},
            "custom branch policy",
        ),
        ({"branch_policies": None}, "branch policies were unread"),
        ({"branch_policies": {"branch_policies": []}}, "admits: none"),
        (
            {
                "branch_policies": {
                    "branch_policies": [
                        {"name": "main", "type": "branch"},
                        {"name": "staging", "type": "branch"},
                    ]
                }
            },
            "admits: main, staging",
        ),
        ({"branch_policies": {"branch_policies": [{"name": "main", "type": "tag"}]}}, "exactly"),
        ({"secrets": None}, "secrets were unread"),
        ({"secrets": {"secrets": [{"name": "DEV_APP_PRIVATE_KEY"}]}}, "secrets outside"),
        (
            {"secrets": NO_SECRETS},
            "lacks its secrets: COURTLISTENER_API_TOKEN, DATA_APP_PRIVATE_KEY",
        ),
        ({"variables": None}, "variables were unread"),
        (
            {"variables": {"variables": [{"name": "AWS_ROLE_TO_ASSUME_STAGING_RW"}]}},
            "variables outside",
        ),
        ({"variables": {"variables": []}}, "lacks its variables: AWS_REGION"),
    ],
)
def test_each_corpus_write_weakening_is_named(overrides: dict[str, Any], fragment: str) -> None:
    problems = _corpus_write(**overrides)
    assert any(fragment in problem for problem in problems), problems


def test_the_corpus_write_gate_cli_reads_the_four_listings(tmp_path: Path) -> None:
    files = {
        "environment": _environment(reviewers=[]),
        "branch-policies": MAIN_ONLY,
        "secrets": WRITER_SECRETS,
        "variables": WRITER_VARIABLES,
    }
    for name, document in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(document))
    args = [
        "assert-corpus-write-environment",
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
    passed = runner.invoke(app, args)
    assert passed.exit_code == 0, passed.output
    # An absent listing is an unread one, and fails.
    (tmp_path / "branch-policies.json").unlink()
    assert runner.invoke(app, args).exit_code == 1


def test_the_promotion_gate_checks_the_corpus_write_environment_unconditionally() -> None:
    """The read-write role's trust names the environment from the moment IAM
    says so, before any workflow binding it reaches `main`, so the check does
    not wait for one."""
    script = (Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh").read_text()
    contexts = script[script.index("\ncontexts() {") : script.index("\nregistry() {")]
    start = contexts.index('cw_base="repos/${REPO}/environments/corpus-write"')
    # The block ends at its own closing `fi`, so nothing after it can satisfy
    # the assertions below.
    tail = contexts[start : contexts.index("\n  fi\n", start)]
    for listing in ("deployment-branch-policies", "secrets", "variables"):
        assert listing in tail
    assert "uv run fedcourts assert-corpus-write-environment" in tail
    assert "fail=1" in tail
    assert "grep -rq" not in tail


# The Claude-only environments: the federation rule's identifiers and the
# engine key, for the jobs that call Claude with no cloud credential. Their
# branch policies are their one control.

STAGING_POLICIES: dict[str, Any] = {
    "total_count": 2,
    "branch_policies": [
        {"name": "staging", "type": "branch"},
        {"name": "promote/*", "type": "branch"},
    ],
}
CLAUDE_SECRETS: dict[str, Any] = {"total_count": 0, "secrets": []}
ANTHROPIC_KEY_SECRETS: dict[str, Any] = {
    "total_count": 1,
    "secrets": [{"name": "ANTHROPIC_API_KEY"}],
}
CLAUDE_VARIABLES: dict[str, Any] = {
    "total_count": 4,
    "variables": [{"name": name} for name in sorted(ec.CLAUDE_ONLY_VARIABLES)],
}


def _claude(name: str = ec.CLAUDE_PROD_ENVIRONMENT, **overrides: Any) -> list[str]:
    values: dict[str, Any] = {
        # No required reviewers: the labeler and the summaries run on schedules.
        "environment": _environment(reviewers=[]),
        "branch_policies": MAIN_ONLY if name == ec.CLAUDE_PROD_ENVIRONMENT else STAGING_POLICIES,
        "secrets": CLAUDE_SECRETS,
        "variables": CLAUDE_VARIABLES,
    }
    values.update(overrides)
    return ec.claude_only_problems(
        name,
        values["environment"],
        values["branch_policies"],
        values["secrets"],
        values["variables"],
    )


def test_the_configured_claude_only_environments_pass() -> None:
    assert _claude(ec.CLAUDE_PROD_ENVIRONMENT) == []
    assert _claude(ec.CLAUDE_STAGING_ENVIRONMENT) == []
    # `promote/*` is admitted, not required, on `claude-staging`.
    staging_only = {"branch_policies": [{"name": "staging", "type": "branch"}]}
    assert _claude(ec.CLAUDE_STAGING_ENVIRONMENT, branch_policies=staging_only) == []


def test_the_claude_only_sign_in_is_required_and_the_optional_ids_are_not() -> None:
    """The rule and organization are the jobs' only sign-in, so an environment
    without them fails; the service account and workspace may be omitted."""
    empty_variables = {"total_count": 0, "variables": []}
    assert _claude(variables=empty_variables) == [
        "the environment lacks its variables: "
        "ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID"
    ]
    required = {"variables": [{"name": name} for name in sorted(ec.CLAUDE_ONLY_REQUIRED_VARIABLES)]}
    assert _claude(variables=required) == []


@pytest.mark.parametrize(
    ("name", "overrides", "fragment"),
    [
        (ec.CLAUDE_PROD_ENVIRONMENT, {"environment": None}, "`claude-prod` environment does not"),
        (ec.CLAUDE_STAGING_ENVIRONMENT, {"environment": None}, "`claude-staging` environment"),
        (
            ec.CLAUDE_PROD_ENVIRONMENT,
            {"environment": _environment(reviewers=[], custom=False)},
            "custom branch policy",
        ),
        (
            ec.CLAUDE_STAGING_ENVIRONMENT,
            {"environment": _environment(reviewers=[], protected_branches=True)},
            "custom branch policy",
        ),
        (ec.CLAUDE_PROD_ENVIRONMENT, {"branch_policies": None}, "branch policies were unread"),
        (
            ec.CLAUDE_PROD_ENVIRONMENT,
            {"branch_policies": {"branch_policies": []}},
            "does not admit main",
        ),
        # `claude-prod` must not also serve staging or the candidates.
        (ec.CLAUDE_PROD_ENVIRONMENT, {"branch_policies": STAGING_POLICIES}, "also admits"),
        # `claude-staging` must not serve `main`, or anything else.
        (
            ec.CLAUDE_STAGING_ENVIRONMENT,
            {
                "branch_policies": {
                    "branch_policies": [
                        *STAGING_POLICIES["branch_policies"],
                        {"name": "main", "type": "branch"},
                    ]
                }
            },
            "also admits: branch:main",
        ),
        (
            ec.CLAUDE_STAGING_ENVIRONMENT,
            {"branch_policies": {"branch_policies": [{"name": "promote/*", "type": "branch"}]}},
            "does not admit staging",
        ),
        # A tag policy cannot pass for the branch of the same name.
        (
            ec.CLAUDE_PROD_ENVIRONMENT,
            {"branch_policies": {"branch_policies": [{"name": "main", "type": "tag"}]}},
            "also admits: tag:main",
        ),
        (ec.CLAUDE_PROD_ENVIRONMENT, {"secrets": None}, "secrets were unread"),
        (
            ec.CLAUDE_PROD_ENVIRONMENT,
            {"secrets": {"secrets": [{"name": "DEV_APP_PRIVATE_KEY"}]}},
            "secrets outside",
        ),
        # The jobs read no key, so one left in the environment is refused.
        (ec.CLAUDE_STAGING_ENVIRONMENT, {"secrets": ANTHROPIC_KEY_SECRETS}, "secrets outside"),
        (
            ec.CLAUDE_PROD_ENVIRONMENT,
            {"variables": {"variables": [{"name": "ANTHROPIC_FEDERATION_RULE_ID"}]}},
            "lacks its variables: ANTHROPIC_ORGANIZATION_ID",
        ),
        (ec.CLAUDE_STAGING_ENVIRONMENT, {"variables": None}, "variables were unread"),
        (
            ec.CLAUDE_STAGING_ENVIRONMENT,
            {"variables": {"variables": [{"name": "AWS_ROLE_TO_ASSUME_READONLY"}]}},
            "variables outside",
        ),
        (
            ec.CLAUDE_PROD_ENVIRONMENT,
            {"variables": {**CLAUDE_VARIABLES, "total_count": 31}},
            "variables were unread or truncated",
        ),
    ],
)
def test_each_claude_only_weakening_is_named(
    name: str, overrides: dict[str, Any], fragment: str
) -> None:
    problems = _claude(name, **overrides)
    assert any(fragment in problem for problem in problems), problems


def test_an_unknown_claude_only_name_is_refused() -> None:
    assert _claude("claude-dev") == ["`claude-dev` is not a Claude-only environment"]


def test_the_claude_only_gate_cli_reads_the_six_listings(tmp_path: Path) -> None:
    files = {
        "environment": _environment(reviewers=[]),
        "branch-policies": STAGING_POLICIES,
        "secrets": CLAUDE_SECRETS,
        "variables": CLAUDE_VARIABLES,
        "repository-secrets": NO_SECRETS,
        "organization-secrets": NO_SECRETS,
    }
    for name, document in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(document))
    args = ["assert-claude-only-environment", "--name", ec.CLAUDE_STAGING_ENVIRONMENT]
    for name in files:
        args += [f"--{name}-file", str(tmp_path / f"{name}.json")]
    runner = CliRunner()
    passed = runner.invoke(app, args)
    assert passed.exit_code == 0, passed.output
    # A repository-level copy of the key reaches a workflow run off any branch.
    (tmp_path / "repository-secrets.json").write_text(json.dumps(ANTHROPIC_KEY_SECRETS))
    assert runner.invoke(app, args).exit_code == 1
    # An absent listing is an unread one, and fails.
    (tmp_path / "repository-secrets.json").write_text(json.dumps(NO_SECRETS))
    (tmp_path / "branch-policies.json").unlink()
    assert runner.invoke(app, args).exit_code == 1


def test_the_promotion_gate_checks_both_claude_only_environments() -> None:
    script = (Path(__file__).resolve().parent.parent / "scripts" / "promotion-gate.sh").read_text()
    contexts = script[script.index("\ncontexts() {") : script.index("\nregistry() {")]
    start = contexts.index("for claude_env in claude-prod claude-staging; do")
    tail = contexts[start : contexts.index("\n  done\n", start)]
    for listing in (
        "deployment-branch-policies",
        '"${claude_base}/secrets',
        '"${claude_base}/variables',
        # The website check's repository and organization reads, taken once.
        '"${web_dir}/repository-secrets.json"',
        '"${web_dir}/organization-secrets.json"',
    ):
        assert listing in tail
    assert "uv run fedcourts assert-claude-only-environment" in tail
    assert "fail=1" in tail


def test_the_claude_only_names_are_the_ones_their_jobs_read() -> None:
    """The gate's admitted names are exactly what the jobs binding a `claude-`
    environment read, and those jobs are the ones that bind one."""
    workflows = Path(__file__).resolve().parent.parent / ".github" / "workflows"
    secrets: set[str] = set()
    variables: set[str] = set()
    bound = 0
    for path in sorted(workflows.glob("*.yml")):
        for job in (yaml.safe_load(path.read_text()).get("jobs") or {}).values():
            if "format('claude-{0}'" not in str(job.get("environment", "")):
                continue
            bound += 1
            text = yaml.safe_dump(job)
            secrets |= set(re.findall(r"secrets\.([A-Z0-9_]+)", text))
            variables |= set(re.findall(r"vars\.([A-Z0-9_]+)", text))
    assert bound >= 3
    assert secrets == set(ec.CLAUDE_ONLY_SECRETS)
    assert variables == set(ec.CLAUDE_ONLY_VARIABLES)
