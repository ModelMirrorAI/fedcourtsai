"""The repository rulesets the review record and the tag record rest on.

Five controls live in GitHub settings rather than in this repository, so a
promotion can silently outlive one of them being edited away:

- ``main: require approval`` — one approving review from a named team before
  anything but a recorded bypass merges into ``main``. A plain approval count
  would accept the agent account's approval, so the team requirement is the
  part that makes the approval the maintainer's.
- ``staging: require PR``'s code-owner review — what holds an owned-path change
  for the maintainer. Its most-recent-push approval must stay **off**: with
  required approvals at zero, GitHub then asks one approval of every PR, which
  ends the agents' self-merge lane and the sync's auto-merge.
- A tag ruleset blocking update and deletion of the three record namespaces.
- A tag ruleset restricting their creation, so no identity but the writer (or
  the maintainer) can plant a name ahead of it.
- Two branch rulesets over ``refs/heads/promote/**``, the promotion train's
  candidates: creation by the dev App alone, and a freeze — no update, force
  push or deletion — that no App bypasses. A candidate's integration evidence
  and approval are bound to its head SHA, and the staging environment admits
  ``promote/*``, so a candidate anyone could create or move would carry both.

:func:`ruleset_problems` reads the full ruleset documents (what
``GET /repos/{owner}/{repo}/rulesets/{id}`` returns, which needs repository
administration read) and names each control that is missing or weaker than
the docs record. It is pure: the promotion gate's admin-read ``contexts``
stage fetches the documents and resolves the identities they must name (the
maintainers team and the two Apps) into :class:`Expected`; this decides.
Bypass lists come back only to an admin, so each bypass check runs only when
the list is present, and then holds it to exactly the actors the docs name.
Every unknown resolves to a finding: a pattern this module cannot read as
covering a ref does not cover it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

MAIN_APPROVAL_RULESET = "main: require approval"
STAGING_PR_RULESET = "staging: require PR"
RECORD_TAG_NAMESPACES = ("promotion", "prereg", "results")
RECORD_CREATION_RULESET = "tags: restrict record creation"
OTHER_CREATION_RULESET = "tags: restrict creation"
TAG_PROTECT_RULESET = "tags: protect record"
PROMOTE_CREATION_RULESET = "promote: restrict creation"
PROMOTE_FREEZE_RULESET = "promote: freeze"
PROMOTE_BRANCH_PATTERN = "refs/heads/promote/**"
# GitHub's built-in repository admin role, as rulesets name it.
ADMIN_ROLE_ID = 5
_ALL_FILES = frozenset({"*", "**", "**/*"})
_ALLOWED_MERGE_METHODS = frozenset({"merge", "squash"})


@dataclass(frozen=True)
class Expected:
    """The identities the rulesets must name, resolved by the caller.

    ``reviewer_team_id`` is the maintainers team, the one whose approval
    counts on ``main``; the two App ids are the data App (the deterministic
    writers and the record-tag writer) and the dev App (the auto-merged lanes).
    """

    reviewer_team_id: int
    data_app_id: int
    dev_app_id: int
    # True when the reader was an admin, so every document must carry its
    # bypass list; a missing one is then a finding, not an unread field.
    require_bypass_lists: bool = True


def _by_name(rulesets: Iterable[Mapping[str, Any]], name: str) -> Mapping[str, Any] | None:
    for ruleset in rulesets:
        if ruleset.get("name") == name:
            return ruleset
    return None


def _rules(ruleset: Mapping[str, Any], rule_type: str) -> list[Mapping[str, Any]]:
    return [rule for rule in ruleset.get("rules") or [] if rule.get("type") == rule_type]


def _params(ruleset: Mapping[str, Any], rule_type: str) -> Mapping[str, Any] | None:
    rules = _rules(ruleset, rule_type)
    if not rules:
        return None
    params = rules[0].get("parameters")
    return params if isinstance(params, Mapping) else {}


def _active(ruleset: Mapping[str, Any]) -> bool:
    return ruleset.get("enforcement") == "active"


def _ref_patterns(ruleset: Mapping[str, Any], key: str) -> list[str]:
    conditions = ruleset.get("conditions") or {}
    ref_name = conditions.get("ref_name") or {}
    return [str(pattern) for pattern in ref_name.get(key) or []]


def _targets_branch(ruleset: Mapping[str, Any], branch: str, *, default: bool) -> bool:
    """Whether the ruleset applies to ``refs/heads/<branch>``, read strictly.

    An include must name the branch (or ``~ALL``, or ``~DEFAULT_BRANCH`` for the
    default branch); any exclude at all is treated as possibly excluding it,
    since the documented rulesets carry none.
    """
    if ruleset.get("target") != "branch":
        return False
    include = set(_ref_patterns(ruleset, "include"))
    names = {f"refs/heads/{branch}", "~ALL"} | ({"~DEFAULT_BRANCH"} if default else set())
    return bool(include & names) and not _ref_patterns(ruleset, "exclude")


def _covers_tag_namespace(ruleset: Mapping[str, Any], namespace: str) -> bool:
    """Whether a tag ruleset applies to every tag under ``<namespace>/``.

    An include must be the namespace's own ``refs/tags/<ns>/**``, ``refs/tags/**``
    or ``~ALL``; an exclude may only be another record namespace's exact
    pattern. Anything else might carve out part of this namespace, so it does
    not count as covering it.
    """
    if ruleset.get("target") != "tag":
        return False
    own = f"refs/tags/{namespace}/**"
    include = set(_ref_patterns(ruleset, "include"))
    if not include & {own, "refs/tags/**", "~ALL"}:
        return False
    others = {f"refs/tags/{ns}/**" for ns in RECORD_TAG_NAMESPACES if ns != namespace}
    return all(pattern in others for pattern in _ref_patterns(ruleset, "exclude"))


def _bypass_problems(
    ruleset: Mapping[str, Any],
    allowed: Mapping[tuple[str, int], frozenset[str]],
    *,
    required: bool,
) -> list[str]:
    """Bypass entries outside ``allowed`` ((type, id) -> permitted modes).

    GitHub returns the list only to an admin. With ``required`` a missing list
    is a finding, since the reader claimed admin; without it the check is
    skipped, which only a deliberately partial read asks for.
    """
    actors = ruleset.get("bypass_actors")
    name = ruleset.get("name")
    if actors is None:
        if required:
            return [f"{name!r} came back without its bypass list; read it with an admin token"]
        return []
    problems: list[str] = []
    for actor in actors:
        key = (str(actor.get("actor_type")), int(actor.get("actor_id") or 0))
        mode = str(actor.get("bypass_mode"))
        modes = allowed.get(key)
        if modes is None:
            problems.append(
                f"{name!r} lets {key[0]} {key[1]} bypass it; the docs name no such actor"
            )
        elif mode not in modes:
            problems.append(
                f"{name!r} lets {key[0]} {key[1]} bypass it in mode {mode!r}; "
                + f"the docs allow {sorted(modes)}"
            )
    return problems


def _main_approval_problems(rulesets: Sequence[Mapping[str, Any]], expected: Expected) -> list[str]:
    ruleset = _by_name(rulesets, MAIN_APPROVAL_RULESET)
    if ruleset is None:
        return [f"no ruleset named {MAIN_APPROVAL_RULESET!r}: main merges on checks alone"]
    problems: list[str] = []
    if not _active(ruleset):
        problems.append(f"{MAIN_APPROVAL_RULESET!r} is not active")
    if not _targets_branch(ruleset, "main", default=True):
        problems.append(f"{MAIN_APPROVAL_RULESET!r} does not plainly target main")
    params = _params(ruleset, "pull_request")
    if params is None:
        return [*problems, f"{MAIN_APPROVAL_RULESET!r} has no pull-request rule"]
    if int(params.get("required_approving_review_count") or 0) < 1:
        problems.append(f"{MAIN_APPROVAL_RULESET!r} requires no approving review")
    team_covers_all = any(
        (entry.get("reviewer") or {}).get("type") == "Team"
        and int((entry.get("reviewer") or {}).get("id") or 0) == expected.reviewer_team_id
        and int(entry.get("minimum_approvals") or 0) >= 1
        and _ALL_FILES & set(entry.get("file_patterns") or [])
        for entry in params.get("required_reviewers") or []
    )
    if not team_covers_all:
        problems.append(
            f"{MAIN_APPROVAL_RULESET!r} does not require the maintainers team over all "
            + "files: another team's approval, or any write holder's, would satisfy it"
        )
    if not params.get("dismiss_stale_reviews_on_push"):
        problems.append(
            f"{MAIN_APPROVAL_RULESET!r} keeps stale approvals: a head pushed after "
            + "the approval would merge on it"
        )
    methods = set(params.get("allowed_merge_methods") or [])
    if not methods or not methods <= _ALLOWED_MERGE_METHODS:
        problems.append(
            f"{MAIN_APPROVAL_RULESET!r} allows merge methods {sorted(methods)}; "
            + "only merge and squash are documented (a rebase rewrites the record's commits)"
        )
    problems += _bypass_problems(
        ruleset,
        {
            ("Integration", expected.dev_app_id): frozenset({"pull_request"}),
            ("Integration", expected.data_app_id): frozenset({"always"}),
            ("RepositoryRole", ADMIN_ROLE_ID): frozenset({"pull_request"}),
        },
        required=expected.require_bypass_lists,
    )
    return problems


def _staging_problems(rulesets: Sequence[Mapping[str, Any]], expected: Expected) -> list[str]:
    ruleset = _by_name(rulesets, STAGING_PR_RULESET)
    if ruleset is None:
        return [f"no ruleset named {STAGING_PR_RULESET!r}"]
    problems: list[str] = []
    if not _active(ruleset):
        problems.append(f"{STAGING_PR_RULESET!r} is not active")
    if not _targets_branch(ruleset, "staging", default=False):
        problems.append(f"{STAGING_PR_RULESET!r} does not plainly target staging")
    problems += _bypass_problems(
        ruleset,
        {("RepositoryRole", ADMIN_ROLE_ID): frozenset({"always"})},
        required=expected.require_bypass_lists,
    )
    params = _params(ruleset, "pull_request")
    if params is None:
        return [*problems, f"{STAGING_PR_RULESET!r} has no pull-request rule"]
    if not params.get("require_code_owner_review"):
        problems.append(
            f"{STAGING_PR_RULESET!r} does not require code-owner review: owned paths "
            + "would merge without the maintainer"
        )
    if not params.get("dismiss_stale_reviews_on_push"):
        problems.append(f"{STAGING_PR_RULESET!r} keeps stale approvals")
    if params.get("require_last_push_approval"):
        problems.append(
            f"{STAGING_PR_RULESET!r} requires approval of the most recent push, "
            + "which asks an approval of every PR and stops the self-merge and sync lanes"
        )
    return problems


def _tag_problems(rulesets: Sequence[Mapping[str, Any]], expected: Expected) -> list[str]:
    active_tags = [r for r in rulesets if _active(r) and r.get("target") == "tag"]
    problems: list[str] = []
    admin = ("RepositoryRole", ADMIN_ROLE_ID)
    bypass: dict[str, Mapping[tuple[str, int], frozenset[str]]] = {
        TAG_PROTECT_RULESET: {},
        RECORD_CREATION_RULESET: {
            ("Integration", expected.data_app_id): frozenset({"always"}),
            admin: frozenset({"always"}),
        },
        OTHER_CREATION_RULESET: {admin: frozenset({"always"})},
    }
    for ruleset in active_tags:
        allowed = bypass.get(str(ruleset.get("name")))
        if allowed is None:
            continue
        problems += _bypass_problems(ruleset, allowed, required=expected.require_bypass_lists)
    for namespace in RECORD_TAG_NAMESPACES:
        covering = [r for r in active_tags if _covers_tag_namespace(r, namespace)]
        for rule_type, what in (
            ("update", "moved"),
            ("deletion", "deleted"),
            ("creation", "created by any write holder"),
        ):
            if not any(_rules(r, rule_type) for r in covering):
                problems.append(
                    f"no active tag ruleset restricts {rule_type} of {namespace}/**: "
                    + f"a record tag can be {what}"
                )
    return problems


def _covers_promote_branches(ruleset: Mapping[str, Any]) -> bool:
    """Whether a branch ruleset applies to every ``refs/heads/promote/`` branch.

    The include must be ``refs/heads/promote/**`` or ``~ALL`` (a single-segment
    ``promote/*`` would leave ``promote/a/b`` open), and no exclude at all.
    """
    if ruleset.get("target") != "branch":
        return False
    include = set(_ref_patterns(ruleset, "include"))
    return bool(include & {PROMOTE_BRANCH_PATTERN, "~ALL"}) and not _ref_patterns(
        ruleset, "exclude"
    )


def _promote_problems(rulesets: Sequence[Mapping[str, Any]], expected: Expected) -> list[str]:
    """The promotion train's candidate branches: created by the dev App alone,
    then frozen — never updated, force-pushed or deleted by anyone but the
    admin role. The integration evidence, the approval and the staging
    environment's admission of ``promote/*`` all rest on that."""
    covering = [r for r in rulesets if _active(r) and _covers_promote_branches(r)]
    admin = ("RepositoryRole", ADMIN_ROLE_ID)
    problems: list[str] = []
    for ruleset in covering:
        freezes = any(_rules(ruleset, t) for t in ("update", "deletion", "non_fast_forward"))
        # A ruleset whose bypass would let the dev App move or delete a
        # candidate is a finding whatever it is named: the App may create one.
        allowed: dict[tuple[str, int], frozenset[str]] = {admin: frozenset({"always"})}
        if not freezes:
            allowed[("Integration", expected.dev_app_id)] = frozenset({"always"})
        problems += _bypass_problems(ruleset, allowed, required=expected.require_bypass_lists)
    for rule_type, what in (
        ("creation", "created by any write holder"),
        ("update", "moved after it is cut"),
        ("deletion", "deleted"),
        ("non_fast_forward", "force-pushed"),
    ):
        if not any(_rules(r, rule_type) for r in covering):
            problems.append(
                f"no active branch ruleset restricts {rule_type} of promote/**: "
                + f"a promotion candidate can be {what}"
            )
    return problems


def ruleset_problems(rulesets: Sequence[Mapping[str, Any]], expected: Expected) -> list[str]:
    """Every way the live rulesets fall short of the documented controls."""
    return [
        *_main_approval_problems(rulesets, expected),
        *_staging_problems(rulesets, expected),
        *_tag_problems(rulesets, expected),
        *_promote_problems(rulesets, expected),
    ]
