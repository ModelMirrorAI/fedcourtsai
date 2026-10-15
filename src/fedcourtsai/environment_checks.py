"""Whether the `corpus-check` environment still gates what its trust hands out.

The read-only role's OIDC trust names `environment:corpus-check`, so the
environment's own settings are the gate on that role: a job binding it holds
the role. GitHub auto-creates a referenced environment with no reviewer and no
branch policy, and anyone with write can push a branch whose own workflow binds
the environment and names the role — so an environment missing either control
hands the read-only role to any write holder's branch. Two readers decide on
the same predicate:

- **the promotion gate's `contexts` stage** (:func:`environment_problems`),
  unconditionally and with an admin read: the environment exists, its
  required-reviewer rule names the configured approver by user id, its
  deployment branches are a custom policy of exactly `main`, and it holds no
  secret and no variable outside :data:`CORPUS_CHECK_VARIABLES`;
- **the lane's plan job** (:func:`protection_problems`), on every poll and with
  the job's `actions: read` grant: the reviewer rule and the `main`-only
  policy, so the lane plans nothing while they are missing. It cannot see
  secrets or variables, which is why the gate is the check that holds.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

#: The environment the corpus-check lane's `run` job binds.
CORPUS_CHECK_ENVIRONMENT = "corpus-check"

#: The only variables the environment may hold: the read-only role, its region
#: and the corpus estate's address. The check's code can read everything its
#: job is handed, so anything else here would be handed to it.
CORPUS_CHECK_VARIABLES = frozenset({"AWS_ROLE_TO_ASSUME_READONLY", "AWS_REGION", "CORPUS_BASE_URL"})

#: The one branch the environment admits: the lane's triggers run `main`'s file.
CORPUS_CHECK_BRANCH = "main"


def _items(document: Mapping[str, Any] | None, key: str) -> list[Mapping[str, Any]] | None:
    if document is None:
        return None
    items = document.get(key)
    if not isinstance(items, list):
        return None
    return [item for item in items if isinstance(item, Mapping)]


def protection_problems(
    environment: Mapping[str, Any] | None,
    branch_policies: Mapping[str, Any] | None,
    *,
    approver_login: str | None,
    approver_id: int | None = None,
) -> list[str]:
    """What the environment lacks of its reviewer rule and its `main`-only policy.

    ``environment`` is ``GET /repos/{repo}/environments/corpus-check`` and
    ``branch_policies`` its ``deployment-branch-policies`` listing; None means
    the read failed or the environment does not exist, and fails. With
    ``approver_id`` the reviewer must match by id as well as login, which is
    what the gate checks; the plan matches the login.
    """
    if not approver_login:
        return ["no approver is configured (config/corpus-check.yaml `approver`)"]
    if environment is None:
        return [f"the `{CORPUS_CHECK_ENVIRONMENT}` environment does not exist or was unread"]
    problems: list[str] = []
    reviewers = [
        reviewer.get("reviewer")
        for rule in _items(environment, "protection_rules") or []
        if rule.get("type") == "required_reviewers"
        for reviewer in rule.get("reviewers") or []
        if isinstance(reviewer, Mapping) and reviewer.get("type") == "User"
    ]
    named = [
        user
        for user in reviewers
        if isinstance(user, Mapping)
        and str(user.get("login", "")).casefold() == approver_login.casefold()
        and (approver_id is None or user.get("id") == approver_id)
    ]
    if not named:
        problems.append(f"no required-reviewer rule names the approver `{approver_login}`")
    policy = environment.get("deployment_branch_policy")
    if not (
        isinstance(policy, Mapping)
        and policy.get("custom_branch_policies") is True
        and policy.get("protected_branches") is False
    ):
        problems.append("deployment branches are not restricted to a custom branch policy")
    policies = _items(branch_policies, "branch_policies")
    if policies is None:
        problems.append("the deployment branch policies were unread")
    elif [(p.get("name"), p.get("type")) for p in policies] != [(CORPUS_CHECK_BRANCH, "branch")]:
        names = ", ".join(sorted(str(p.get("name")) for p in policies)) or "none"
        problems.append(
            f"the branch policy must admit exactly `{CORPUS_CHECK_BRANCH}` (branch); "
            + f"it admits: {names}"
        )
    return problems


def environment_problems(
    environment: Mapping[str, Any] | None,
    branch_policies: Mapping[str, Any] | None,
    secrets: Mapping[str, Any] | None,
    variables: Mapping[str, Any] | None,
    *,
    approver_login: str | None,
    approver_id: int | None,
) -> list[str]:
    """Everything the promotion gate requires of the `corpus-check` environment.

    The protection above, matched by user id, plus the contents: no secret at
    all, and no variable outside :data:`CORPUS_CHECK_VARIABLES`. An unread
    listing is a problem, never a pass.
    """
    if approver_id is None:
        return ["the approver's user id was unread"]
    problems = protection_problems(
        environment, branch_policies, approver_login=approver_login, approver_id=approver_id
    )
    if environment is None:
        return problems
    secret_items = _items(secrets, "secrets")
    if secret_items is None:
        problems.append("the environment's secrets were unread")
    elif secret_items:
        problems.append(f"the environment holds {len(secret_items)} secret(s); it may hold none")
    variable_items = _items(variables, "variables")
    if variable_items is None:
        problems.append("the environment's variables were unread")
    else:
        extra = sorted(
            str(item.get("name"))
            for item in variable_items
            if item.get("name") not in CORPUS_CHECK_VARIABLES
        )
        if extra:
            problems.append(
                "the environment holds variables outside "
                + f"{sorted(CORPUS_CHECK_VARIABLES)}: {', '.join(extra)}"
            )
    return problems
