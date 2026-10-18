"""Whether the gated deployment environments still hold their controls.

The `corpus-check` environment gates what its trust hands out.

The read-only role's OIDC trust names `environment:corpus-check`, so the
environment's own settings are the gate on that role: a job binding it holds
the role. GitHub auto-creates a referenced environment with no reviewer and no
branch policy, and anyone with write can push a branch whose own workflow binds
the environment and names the role — so an environment missing either control
hands the read-only role to any write holder's branch. Two readers decide on
the same predicate:

- **the promotion gate's `contexts` stage** (:func:`environment_problems`),
  unconditionally and with an admin read: the environment exists, its
  required reviewers are exactly the configured approver, by user id — no
  other user and no team — its
  deployment branches are a custom policy of exactly `main`, and it holds no
  secret and no variable outside :data:`CORPUS_CHECK_VARIABLES`;
- **the lane's plan job** (:func:`protection_problems`), on every poll and with
  the job's `actions: read` grant: the approver as sole reviewer and the
  `main`-only policy, so the lane plans nothing while they are missing. It cannot see
  secrets or variables, which is why the gate is the check that holds.

The read-only role's trust also names `environment:corpus-check-auto`, the
reviewer-less environment the lane's `run-auto` job binds to run an
allowlisted `fedcourts` subcommand at `main`'s own commit — no PR code — without
the approval. Its branch policy is its only control, so the same two readers
check it: the promotion gate (:func:`auto_environment_problems`) requires it to
exist, admit `main` alone, and hold no secret and no variable outside
:data:`CORPUS_CHECK_VARIABLES`; the plan (:func:`auto_protection_problems`)
requires the existence and the policy, and while either is missing routes
every request to the approval. Neither requires or refuses a reviewer: one
added there is the immediate stop, holding every auto run for a click.

The same stage checks the `website` environment (:func:`website_problems`),
which holds the Buttondown API key `post-public-update` drafts the weekly
update with: its `main`-only policy is what keeps the key from any other ref,
and nothing else reads that policy. And it checks the `corpus-write`
environment (:func:`corpus_write_problems`), the one the production read-write
role's trust is to name: its `main`-only policy is what keeps that role from
any other ref. The trust statements themselves live in IAM, which nothing
here reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

#: The environment the corpus-check lane's `run` job binds.
CORPUS_CHECK_ENVIRONMENT = "corpus-check"

#: The reviewer-less environment the lane's `run-auto` job binds.
CORPUS_CHECK_AUTO_ENVIRONMENT = "corpus-check-auto"

#: The only variables the environment may hold: the read-only role, its region
#: and the corpus estate's address. The check's code can read everything its
#: job is handed, so anything else here would be handed to it.
CORPUS_CHECK_VARIABLES = frozenset({"AWS_ROLE_TO_ASSUME_READONLY", "AWS_REGION", "CORPUS_BASE_URL"})

#: The one branch each environment checked here admits: the triggers of the
#: workflows that bind them run `main`'s file.
MAIN_BRANCH = "main"


def _items(document: Mapping[str, Any] | None, key: str) -> list[Mapping[str, Any]] | None:
    """The listing's items, or None when it is unread or only a page of it was.

    A listing whose `total_count` disagrees with the items it carries was
    truncated by pagination, and a name past the page would go unseen, so it
    counts as unread rather than as the whole set.
    """
    if document is None:
        return None
    items = document.get(key)
    if not isinstance(items, list):
        return None
    total = document.get("total_count")
    if isinstance(total, int) and not isinstance(total, bool) and total != len(items):
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
        reviewer
        for rule in _items(environment, "protection_rules") or []
        if rule.get("type") == "required_reviewers"
        for reviewer in rule.get("reviewers") or []
        if isinstance(reviewer, Mapping)
    ]
    approver = [
        reviewer
        for reviewer in reviewers
        if reviewer.get("type") == "User"
        and isinstance(reviewer.get("reviewer"), Mapping)
        and str(reviewer["reviewer"].get("login", "")).casefold() == approver_login.casefold()
        and (approver_id is None or reviewer["reviewer"].get("id") == approver_id)
    ]
    if not approver:
        problems.append(f"no required-reviewer rule names the approver `{approver_login}`")
    elif len(reviewers) != 1:
        # Any other reviewer — a second user, or a team whose members change
        # without a commit — could release the role on their own approval.
        problems.append(
            f"the required reviewers must be exactly `{approver_login}`; "
            + f"the rule names {len(reviewers)}"
        )
    problems.extend(_main_only_problems(environment, branch_policies))
    return problems


def _main_only_problems(
    environment: Mapping[str, Any], branch_policies: Mapping[str, Any] | None
) -> list[str]:
    """What keeps the environment from being a custom policy admitting `main` alone.

    A tag policy is listed with its type, so one named `main` cannot pass for
    the branch.
    """
    problems: list[str] = []
    policy = environment.get("deployment_branch_policy")
    if not (
        isinstance(policy, Mapping)
        and policy.get("custom_branch_policies") is True
        and policy.get("protected_branches") is False
    ):
        problems.append("deployment branches are not restricted to a custom branch policy")
    policies = _items(branch_policies, "branch_policies")
    if policies is None:
        problems.append("the deployment branch policies were unread or truncated")
    elif [(p.get("name"), p.get("type")) for p in policies] != [(MAIN_BRANCH, "branch")]:
        names = ", ".join(sorted(str(p.get("name")) for p in policies)) or "none"
        problems.append(
            f"the branch policy must admit exactly `{MAIN_BRANCH}` (branch); "
            + f"it admits: {names}"
        )
    return problems


def auto_protection_problems(
    environment: Mapping[str, Any] | None, branch_policies: Mapping[str, Any] | None
) -> list[str]:
    """What `corpus-check-auto` lacks of its existence and its `main`-only policy.

    ``environment`` is ``GET /repos/{repo}/environments/corpus-check-auto`` and
    ``branch_policies`` its ``deployment-branch-policies`` listing; None means
    the read failed or the environment does not exist, and fails — GitHub
    would create a referenced environment with no branch policy, which the
    read-only role's trust would then hand to any branch's workflow.
    """
    if environment is None:
        return [f"the `{CORPUS_CHECK_AUTO_ENVIRONMENT}` environment does not exist or was unread"]
    return _main_only_problems(environment, branch_policies)


def auto_environment_problems(
    environment: Mapping[str, Any] | None,
    branch_policies: Mapping[str, Any] | None,
    secrets: Mapping[str, Any] | None,
    variables: Mapping[str, Any] | None,
) -> list[str]:
    """Everything the promotion gate requires of the `corpus-check-auto` environment.

    Its existence and `main`-only policy (:func:`auto_protection_problems`),
    no secret at all, and no variable outside :data:`CORPUS_CHECK_VARIABLES`.
    Reviewers are not checked: the environment has none by design, and one
    added is the stop for the unapproved path, which must not block a
    promotion. An unread listing is a problem, never a pass.
    """
    problems = auto_protection_problems(environment, branch_policies)
    if environment is None:
        return problems
    problems.extend(_contents_problems(secrets, variables))
    return problems


def _contents_problems(
    secrets: Mapping[str, Any] | None, variables: Mapping[str, Any] | None
) -> list[str]:
    """No secret, and no variable outside :data:`CORPUS_CHECK_VARIABLES`; unread fails."""
    problems: list[str] = []
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


def _exact_names_problems(
    listing: Mapping[str, Any] | None, key: str, expected: frozenset[str]
) -> list[str]:
    """A listing of secrets or variables that is unread, or names other than ``expected``."""
    items = _items(listing, key)
    if items is None:
        return [f"the environment's {key} were unread"]
    names = {str(item.get("name")) for item in items}
    problems: list[str] = []
    extra = sorted(names - expected)
    if extra:
        problems.append(
            f"the environment holds {key} outside {sorted(expected)}: {', '.join(extra)}"
        )
    missing = sorted(expected - names)
    if missing:
        problems.append(f"the environment lacks its {key}: {', '.join(missing)}")
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
    problems.extend(_contents_problems(secrets, variables))
    return problems


#: The environment `post-public-update`'s `post` job binds.
WEBSITE_ENVIRONMENT = "website"

#: Its one secret, the Buttondown API key the weekly draft is created with.
WEBSITE_SECRETS = frozenset({"BUTTONDOWN_API_KEY"})

#: Its one variable, the Buttondown id of the tag the draft is addressed to.
WEBSITE_VARIABLES = frozenset({"WEEKLY_SCOTUS_TAG_ID"})


def website_problems(
    environment: Mapping[str, Any] | None,
    branch_policies: Mapping[str, Any] | None,
    secrets: Mapping[str, Any] | None,
    variables: Mapping[str, Any] | None,
) -> list[str]:
    """Everything the promotion gate requires of the `website` environment.

    The environment holds the Buttondown API key, which can create, send or
    edit the list's emails, and its deployment-branch policy is what keeps that
    key from a workflow a write holder runs from their own branch. So: it
    exists, its deployment branches are a custom policy of exactly `main`, and
    it holds exactly the key and the tag id, nothing else — a secret added
    here would be handed to the same job. Required reviewers are not checked:
    the draft is the hold, and a reviewer only adds a wait. An unread listing
    is a problem, never a pass.
    """
    if environment is None:
        return [f"the `{WEBSITE_ENVIRONMENT}` environment does not exist or was unread"]
    problems = _main_only_problems(environment, branch_policies)
    problems.extend(_exact_names_problems(secrets, "secrets", WEBSITE_SECRETS))
    problems.extend(_exact_names_problems(variables, "variables", WEBSITE_VARIABLES))
    return problems


#: The environment the corpus writer jobs bind: every job that assumes the
#: production read-write role, and no other (`tests/test_workflow_corpus_write.py`).
CORPUS_WRITE_ENVIRONMENT = "corpus-write"

#: The secrets those jobs read: the data App's key, which commits their
#: pointer, and the CourtListener token `run-pull` fetches with.
CORPUS_WRITE_SECRETS = frozenset({"DATA_APP_PRIVATE_KEY", "COURTLISTENER_API_TOKEN"})

#: Of those, the ones the environment must itself hold: both. They are
#: environment secrets on `prod` today, and a repository-level copy would
#: reach a workflow run off any branch.
CORPUS_WRITE_REQUIRED_SECRETS = CORPUS_WRITE_SECRETS

#: The variables those jobs read: both corpus roles (the decision-record job
#: pulls with the read-only one), the region, the corpus estate's address, the
#: data App's client id and `run-pull`'s CourtListener rate caps.
CORPUS_WRITE_VARIABLES = frozenset(
    {
        "AWS_ROLE_TO_ASSUME",
        "AWS_ROLE_TO_ASSUME_READONLY",
        "AWS_REGION",
        "CORPUS_BASE_URL",
        "DATA_APP_CLIENT_ID",
        "COURTLISTENER_RPM",
        "COURTLISTENER_RPH",
        "COURTLISTENER_RPD",
    }
)

#: Of those, the ones the environment must itself hold: everything but the
#: three rate caps, which the workflow defaults when unset. Each is one of the
#: per-environment values `prod` holds, so none is served from the
#: repository level, and a writer without one fails at its first step that
#: needs it.
CORPUS_WRITE_REQUIRED_VARIABLES = CORPUS_WRITE_VARIABLES - {
    "COURTLISTENER_RPM",
    "COURTLISTENER_RPH",
    "COURTLISTENER_RPD",
}


def _bounded_names_problems(
    listing: Mapping[str, Any] | None,
    key: str,
    allowed: frozenset[str],
    required: frozenset[str],
) -> list[str]:
    """A listing that is unread, names one outside ``allowed``, or lacks one of ``required``."""
    items = _items(listing, key)
    if items is None:
        return [f"the environment's {key} were unread or truncated"]
    names = {str(item.get("name")) for item in items}
    problems: list[str] = []
    extra = sorted(names - allowed)
    if extra:
        problems.append(
            f"the environment holds {key} outside {sorted(allowed)}: {', '.join(extra)}"
        )
    missing = sorted(required - names)
    if missing:
        problems.append(f"the environment lacks its {key}: {', '.join(missing)}")
    return problems


def corpus_write_problems(
    environment: Mapping[str, Any] | None,
    branch_policies: Mapping[str, Any] | None,
    secrets: Mapping[str, Any] | None,
    variables: Mapping[str, Any] | None,
) -> list[str]:
    """Everything the promotion gate requires of the `corpus-write` environment.

    The design has the production read-write role's trust name this
    environment alone, so its deployment-branch policy is what keeps that role
    from a workflow a write holder runs from their own branch: GitHub
    auto-creates a referenced environment with no policy at all. So: it
    exists, its deployment branches are a custom policy of exactly `main`, it
    holds no secret outside :data:`CORPUS_WRITE_SECRETS` and no variable
    outside :data:`CORPUS_WRITE_VARIABLES` — anything else would be handed to
    the writer jobs for no reason they have — and it holds every name in
    :data:`CORPUS_WRITE_REQUIRED_SECRETS` and
    :data:`CORPUS_WRITE_REQUIRED_VARIABLES`, so a promotion cannot move the
    writers onto an environment that would fail their next window. Required
    reviewers are not checked: the writer windows run on a schedule, and a
    reviewer would hold every one. The trust itself lives in IAM and is not
    read here. An unread or truncated listing is a problem, never a pass.
    """
    if environment is None:
        return [f"the `{CORPUS_WRITE_ENVIRONMENT}` environment does not exist or was unread"]
    problems = _main_only_problems(environment, branch_policies)
    problems.extend(
        _bounded_names_problems(
            secrets, "secrets", CORPUS_WRITE_SECRETS, CORPUS_WRITE_REQUIRED_SECRETS
        )
    )
    problems.extend(
        _bounded_names_problems(
            variables, "variables", CORPUS_WRITE_VARIABLES, CORPUS_WRITE_REQUIRED_VARIABLES
        )
    )
    return problems


def shadow_secret_problems(
    repository_secrets: Mapping[str, Any] | None,
    organization_secrets: Mapping[str, Any] | None,
    names: frozenset[str] = WEBSITE_SECRETS,
) -> list[str]:
    """A copy of an environment's secret at repository or organization level.

    A workflow's `secrets.NAME` falls back to a repository or organization
    secret of the same name, which no deployment-branch policy guards: a copy
    there reaches a workflow run off any branch. So neither listing may name
    one of ``names``, and an unread listing is a problem.
    """
    problems: list[str] = []
    for scope, listing in (
        ("repository", repository_secrets),
        ("organization (shared with this repository)", organization_secrets),
    ):
        items = _items(listing, "secrets")
        if items is None:
            problems.append(f"the {scope} secrets were unread")
            continue
        shadowed = sorted(names & {str(item.get("name")) for item in items})
        if shadowed:
            problems.append(
                f"the {scope} secrets hold {', '.join(shadowed)}, which any branch's "
                + "workflow can read; keep it in the environment alone"
            )
    return problems
