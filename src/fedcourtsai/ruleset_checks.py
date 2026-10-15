"""The repository rulesets the review record and the tag record rest on.

Four controls live in GitHub settings rather than in this repository, so a
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

:func:`ruleset_problems` reads the full ruleset documents (what
``GET /repos/{owner}/{repo}/rulesets/{id}`` returns, which needs repository
administration read) and names each control that is missing or weaker than
the docs record. It is pure: the promotion gate's admin-read ``contexts``
stage fetches, this decides. Bypass lists come back only to an admin, so the
bypass check runs only when one is present.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

MAIN_APPROVAL_RULESET = "main: require approval"
STAGING_PR_RULESET = "staging: require PR"
RECORD_TAG_NAMESPACES = ("promotion", "prereg", "results")
_ALL_FILES = frozenset({"*", "**", "**/*"})
_ALLOWED_MERGE_METHODS = frozenset({"merge", "squash"})
# Human-held bypass on the approval ruleset is for pull requests only: an
# `always` bypass would let the holder push to `main` past every rule in it.
_HUMAN_ACTOR_TYPES = frozenset({"RepositoryRole", "Team", "OrganizationAdmin"})


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


def _targets_main(ruleset: Mapping[str, Any]) -> bool:
    include = _ref_patterns(ruleset, "include")
    return ruleset.get("target", "branch") == "branch" and (
        "~DEFAULT_BRANCH" in include or "refs/heads/main" in include or "~ALL" in include
    )


def _covers_tag_namespace(ruleset: Mapping[str, Any], namespace: str) -> bool:
    if ruleset.get("target") != "tag":
        return False
    pattern = f"refs/tags/{namespace}/**"
    include = _ref_patterns(ruleset, "include")
    exclude = _ref_patterns(ruleset, "exclude")
    included = pattern in include or "~ALL" in include or "refs/tags/**" in include
    return included and pattern not in exclude


def _main_approval_problems(rulesets: Sequence[Mapping[str, Any]]) -> list[str]:
    ruleset = _by_name(rulesets, MAIN_APPROVAL_RULESET)
    if ruleset is None:
        return [f"no ruleset named {MAIN_APPROVAL_RULESET!r}: main merges on checks alone"]
    problems: list[str] = []
    if not _active(ruleset):
        problems.append(f"{MAIN_APPROVAL_RULESET!r} is not active")
    if not _targets_main(ruleset):
        problems.append(f"{MAIN_APPROVAL_RULESET!r} does not target main")
    params = _params(ruleset, "pull_request")
    if params is None:
        return [*problems, f"{MAIN_APPROVAL_RULESET!r} has no pull-request rule"]
    if int(params.get("required_approving_review_count") or 0) < 1:
        problems.append(f"{MAIN_APPROVAL_RULESET!r} requires no approving review")
    team_covers_all = any(
        (entry.get("reviewer") or {}).get("type") == "Team"
        and int(entry.get("minimum_approvals") or 0) >= 1
        and _ALL_FILES & set(entry.get("file_patterns") or [])
        for entry in params.get("required_reviewers") or []
    )
    if not team_covers_all:
        problems.append(
            f"{MAIN_APPROVAL_RULESET!r} names no required-reviewer team over all files: "
            + "any write holder's approval, the agent account's included, would satisfy it"
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
            + "only merge and squash keep main and staging sharing history"
        )
    for actor in ruleset.get("bypass_actors") or []:
        if actor.get("actor_type") in _HUMAN_ACTOR_TYPES and actor.get("bypass_mode") != (
            "pull_request"
        ):
            problems.append(
                f"{MAIN_APPROVAL_RULESET!r} lets a {actor.get('actor_type')} bypass "
                + f"in mode {actor.get('bypass_mode')!r}; a human-held bypass must be "
                + "for pull requests only"
            )
    return problems


def _staging_problems(rulesets: Sequence[Mapping[str, Any]]) -> list[str]:
    ruleset = _by_name(rulesets, STAGING_PR_RULESET)
    if ruleset is None:
        return [f"no ruleset named {STAGING_PR_RULESET!r}"]
    problems: list[str] = []
    if not _active(ruleset):
        problems.append(f"{STAGING_PR_RULESET!r} is not active")
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


def _tag_problems(rulesets: Sequence[Mapping[str, Any]]) -> list[str]:
    active_tags = [r for r in rulesets if _active(r) and r.get("target") == "tag"]
    problems: list[str] = []
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


def ruleset_problems(rulesets: Sequence[Mapping[str, Any]]) -> list[str]:
    """Every way the live rulesets fall short of the documented controls."""
    return [
        *_main_approval_problems(rulesets),
        *_staging_problems(rulesets),
        *_tag_problems(rulesets),
    ]
