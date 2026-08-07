"""Which status-check contexts a branch's required-checks rule can actually get.

A required context is satisfied only by a check run that *reports* on the PR,
and the workflow that would report it has to exist on the branch whose
workflows the PR runs. PRs into ``main`` from the bot lanes — the collect run
branches, ``cleanup/*``, ``metrics/refresh``, ``metrics/cert-backtest``,
``metrics/salience-replay`` — are
cut **from** ``main``, so they run ``main``'s own workflow files. Requiring a
context that no workflow on that branch produces leaves every such PR pending
forever, and the auto-merging collect PRs are the ones that hang first: data
production stops, quietly, on a rule that reads like a tightening.

So the order is forced. A job's definition must reach the branch before its
name may join that branch's required contexts, and the two steps are at least
one promotion apart. This module is the check that says which step you are on:
:func:`unproduced_contexts` names the contexts that would hang, and
:func:`ready_to_require` names the candidates whose definition has landed.

Only a workflow that runs on *every* pull request into the branch can produce a
required context. Three things disqualify one, and the distinction that matters
is between a workflow that does not run and a job that is skipped: a job gated
by ``if:`` still reports ``skipped``, which **satisfies** the requirement — that
is exactly how ``promotion-gate`` passes on an ordinary PR — while a workflow
filtered out by its trigger reports nothing at all, and nothing is what hangs.
So a workflow is a producer here only when it triggers on ``pull_request``, with
no ``paths`` / ``paths-ignore`` filter, and no ``branches`` filter excluding the
branch. ``zizmor`` is the live example of the difference: its workflow is
path-filtered to ``.github/**``, so requiring it would hang any PR that does not
touch a workflow.

A job reports under its ``name`` when it sets one and its job id otherwise —
except where the real spelling cannot be known from the file, which is the case
for a matrix job (one context per combination, ``<name> (<values>)``) and for an
expression-valued name. Those contribute nothing, so no spelling of them is ever
vouched for.

The bias is one-directional on purpose. Every unknown resolves to *unproduced*,
which can raise a false alarm on a context that would in fact report — a
required context satisfied by an external app's commit status rather than a
workflow job is invisible here for the same reason. That costs a second look.
The opposite error costs a stalled branch, so it is the one worth never making.
"""

from __future__ import annotations

from collections.abc import Iterable
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

# Workflow files whose jobs can report a check context.
_WORKFLOW_SUFFIXES = (".yml", ".yaml")
# Trigger filters that make a workflow conditional on what a PR touches, so it
# cannot be relied on to report at all.
_PATH_FILTERS = ("paths", "paths-ignore")


def _pull_request_trigger(document: dict[Any, Any]) -> Any:
    """The workflow's ``pull_request`` trigger config, or ``None`` if it has none.

    ``on`` is the YAML 1.1 boolean ``True`` once parsed, so both spellings are
    checked; the value itself may be a string, a list, or a mapping.
    """
    triggers = document.get("on", document.get(True))
    if isinstance(triggers, str):
        return {} if triggers == "pull_request" else None
    if isinstance(triggers, list):
        return {} if "pull_request" in triggers else None
    if isinstance(triggers, dict):
        if "pull_request" not in triggers:
            return None
        config = triggers["pull_request"]
        return config if isinstance(config, dict) else {}
    return None


def _reports_on_every_pr(document: dict[Any, Any], base_branch: str | None) -> bool:
    """Whether this workflow runs on every pull request into ``base_branch``."""
    config = _pull_request_trigger(document)
    if config is None:
        return False
    if any(key in config for key in _PATH_FILTERS):
        return False
    if base_branch is None:
        return True
    ignored = config.get("branches-ignore")
    if isinstance(ignored, list) and any(fnmatch(base_branch, str(p)) for p in ignored):
        return False
    allowed = config.get("branches")
    if isinstance(allowed, list):
        return any(fnmatch(base_branch, str(pattern)) for pattern in allowed)
    return True


def _job_contexts(job_id: str, job: Any) -> set[str]:
    """The context name(s) a single job definition can report under.

    Empty when the real spelling is unenumerable. A matrix job reports one
    context per combination (``<name> (<values>)``) and an expression-valued
    name renders at run time — in both cases the bare spelling this could
    otherwise offer is a context GitHub never reports, so vouching for it would
    bless a rule that hangs. Contributing nothing costs a false alarm; the
    alternative costs a stalled branch.
    """
    if not isinstance(job, dict):
        return {job_id}
    strategy = job.get("strategy")
    if isinstance(strategy, dict) and "matrix" in strategy:
        return set()
    name = job.get("name")
    if isinstance(name, str) and name:
        return set() if "${{" in name else {name}
    return {job_id}


def produced_contexts(workflow_dir: Path, base_branch: str | None = None) -> set[str]:
    """Every check context the workflows under ``workflow_dir`` reliably report.

    Only workflows that run on every pull request into ``base_branch`` count;
    pass ``None`` to skip the branch-filter test and keep the rest.

    Tolerant by construction: an unreadable or unparseable workflow contributes
    nothing rather than raising. A file this cannot read is a file whose jobs it
    cannot vouch for, which is the conservative reading.
    """
    contexts: set[str] = set()
    if not workflow_dir.is_dir():
        return contexts
    for path in sorted(workflow_dir.iterdir()):
        if path.suffix not in _WORKFLOW_SUFFIXES or not path.is_file():
            continue
        try:
            document = yaml.safe_load(path.read_text())
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(document, dict) or not _reports_on_every_pr(document, base_branch):
            continue
        jobs = document.get("jobs")
        if not isinstance(jobs, dict):
            continue
        for job_id, job in jobs.items():
            contexts |= _job_contexts(str(job_id), job)
    return contexts


def unproduced_contexts(
    required: Iterable[str], workflow_dir: Path, base_branch: str | None = None
) -> list[str]:
    """Required contexts with no producing job — the ones that would hang a PR."""
    produced = produced_contexts(workflow_dir, base_branch)
    return sorted({context for context in required if context and context not in produced})


def ready_to_require(
    candidates: Iterable[str], workflow_dir: Path, base_branch: str | None = None
) -> list[str]:
    """Candidate contexts whose producing job has landed on this branch.

    The other half of the ordering: a candidate absent here is one whose
    definition has not promoted yet, so adding it to the rule would hang.
    """
    produced = produced_contexts(workflow_dir, base_branch)
    return sorted({candidate for candidate in candidates if candidate and candidate in produced})
