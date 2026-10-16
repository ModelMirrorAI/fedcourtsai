"""The run gate's shape in a workflow, shared by the tests that read job conditions.

Every workflow that binds a deployment environment opens with an ``authorize``
job (``src/fedcourtsai/run_gate.py``) and closes with a ``run-gate`` job that
fails a refused re-run; every job between them needs ``authorize`` and ends its
``if:`` with :data:`RUN_GATE_GUARD`. ``test_workflow_auth_gate.py`` pins that
shape; the helpers here let a test about a job's *own* routing — its pass, its
mode, its hold — read the condition and the needs list the job would carry
without the gate, so the gate's conjunct does not have to be restated in every
such test.
"""

from __future__ import annotations

from typing import Any

#: The gate's job id.
AUTHORIZE_JOB = "authorize"

#: The closing job that fails a run the gate refused.
SENTINEL_JOB = "run-gate"

#: The sentinel step's condition, whitespace-normalized: the gate did not pass,
#: or this attempt is not the one it judged and its re-runner is not listed.
SENTINEL_CONDITION = (
    "${{ needs.authorize.result != 'success'"
    + " || (needs.authorize.outputs.attempt != github.run_attempt"
    + " && !contains(needs.authorize.outputs.rerunners,"
    + " format(',{0},', github.triggering_actor))) }}"
)

#: The conjunct every gated job's condition ends with, whitespace-normalized:
#: the authorize job passed, and either this is the attempt it judged or the
#: login re-running this job alone is a human it published.
RUN_GATE_GUARD = (
    "needs.authorize.result == 'success'"
    + " && (needs.authorize.outputs.attempt == github.run_attempt"
    + " || contains(needs.authorize.outputs.rerunners,"
    + " format(',{0},', github.triggering_actor)))"
)


def norm(text: object) -> str:
    """Collapse runs of whitespace, as a folded ``if:`` block reads once joined."""
    return " ".join(str(text).split())


def _encloses(expr: str) -> bool:
    """Whether ``expr``'s first parenthesis closes at its last character."""
    if not (expr.startswith("(") and expr.endswith(")")):
        return False
    depth = 0
    quoted = False
    for index, char in enumerate(expr):
        if char == "'":
            quoted = not quoted
        elif not quoted and char == "(":
            depth += 1
        elif not quoted and char == ")":
            depth -= 1
            if depth == 0 and index != len(expr) - 1:
                return False
    return True


def own_condition(job: dict[str, Any]) -> str:
    """The job's ``if:`` without the run gate: unwrapped and whitespace-normalized.

    Empty when the gate is the whole condition. A condition that does not end in
    the gate is returned normalized but otherwise as written, so a test reading
    an ungated job still sees its text.
    """
    condition = norm(job.get("if") or "")
    if condition.startswith("${{") and condition.endswith("}}"):
        condition = condition[3:-2].strip()
    if condition == RUN_GATE_GUARD:
        return ""
    suffix = " && " + RUN_GATE_GUARD
    if not condition.endswith(suffix):
        return condition
    condition = condition[: -len(suffix)].strip()
    return condition[1:-1].strip() if _encloses(condition) else condition


def own_needs(job: dict[str, Any]) -> list[str]:
    """The job's ``needs`` as a list, without the authorize job."""
    needs = job.get("needs") or []
    needs = [needs] if isinstance(needs, str) else list(needs)
    return [need for need in needs if need != AUTHORIZE_JOB]


def gated_jobs(workflow: dict[Any, Any]) -> dict[str, dict[str, Any]]:
    """The workflow's jobs other than the gate's own two."""
    jobs = workflow.get("jobs") or {}
    return {name: job for name, job in jobs.items() if name not in (AUTHORIZE_JOB, SENTINEL_JOB)}


def top_level_disjunction(expr: str) -> bool:
    """Whether ``expr`` holds an ``||`` outside every parenthesis and quoted string.

    Such an expression conjoined with the guard as ``expr && guard`` would bind
    as ``a || (b && guard)``, so its ``a`` would run without the gate.
    """
    depth = 0
    quoted = False
    index = 0
    while index < len(expr):
        char = expr[index]
        if char == "'":
            quoted = not quoted
        elif not quoted and char == "(":
            depth += 1
        elif not quoted and char == ")":
            depth -= 1
        elif not quoted and depth == 0 and expr.startswith("||", index):
            return True
        index += 1
    return False
