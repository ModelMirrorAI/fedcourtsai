"""The issue-less collect path — the only path the collect seam takes.

No fan-out round has a trigger issue: `issue: ${{ github.event.issue.number }}`
evaluates to the empty string on every round, and
`collect-plan --issue ""` exits 2 because the option is an `int`. The
composite absorbs that with an Actions-expression fallback to `collect-plan`'s
own no-issue sentinel — one expression, in one `env:` key, standing between a
round and a collect job that aborts under `set -euo pipefail` with the
run's only copy of its agent output still on the runner.

That makes it the hottest path in the seam and the one an Actions expression
alone would leave unexercised by any Python test. These tests exercise it,
from both ends: the sentinel the composite normalizes to is read back out of the
action, and the `collect-plan` command line is read back out of the same step
and executed with it — so the two halves are checked against each other rather
than each against a copy of the contract kept here.

The composite's other properties — the download loop, the union/push loop, the
PR partition — are pinned in `tests/test_workflow_collect.py`; `collect-plan`'s
own output shape is pinned in `tests/test_cli_collect.py` and
`tests/test_collect.py`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai.cli import app
from tests.workflow_argv import command_argv, expand, shell_arrays

ROOT = Path(__file__).resolve().parent.parent
COLLECT_ACTION = ROOT / ".github" / "actions" / "collect-run" / "action.yml"

#: The composite calls the CLI it pinned to this checkout, never a bare
#: `uv run` — see `tests/test_workflow_collect.py` for why that pin exists.
PINNED_CLI = ("$FEDCOURTS",)

#: `github.event.issue.number` on a lane with no trigger issue. Not `"0"` and
#: not absent: the empty string is what the expression actually yields, and it
#: is the one value `collect-plan` cannot take.
NO_TRIGGER_ISSUE = ""

RUN_ID = "20260628T120000Z"

#: One ready evaluate cell, matching the matrix entry below so the run reads as
#: complete — the case where the ready PR *would* close a trigger issue, which
#: is exactly where an issue-less run must still succeed and simply close none.
CELL = {"court": "scotus", "docket": 1, "event_id": "evt-petition-disposition"}
ACTOR = "claude-judge"


def _action() -> dict[Any, Any]:
    data = yaml.safe_load(COLLECT_ACTION.read_text())
    assert isinstance(data, dict)
    return data


def _aggregate_step() -> dict[str, Any]:
    step = next(s for s in _action()["runs"]["steps"] if str(s["name"]).startswith("Aggregate"))
    assert isinstance(step, dict)
    return step


def _normalized_issue() -> str:
    """The value the composite hands the CLI when the run has no trigger issue.

    Read off the step's own `env:` rather than assumed, then evaluated the way
    Actions evaluates it: `a || b` yields `b` when `a` is falsy, and
    :data:`NO_TRIGGER_ISSUE` — the empty string a scheduled round supplies — is
    falsy. So the fallback operand is what the CLI actually receives.
    """
    expression = str(_aggregate_step()["env"]["ISSUE"])
    fallback = re.fullmatch(r"\$\{\{\s*inputs\.issue\s*\|\|\s*(\S+)\s*\}\}", expression)
    assert fallback is not None, (
        f"the composite no longer defaults an absent trigger issue (ISSUE: {expression}); "
        "a scheduled round passes the empty string, which `collect-plan --issue` "
        "rejects with exit 2 — aborting the collect job under `set -euo pipefail`"
    )
    assert not NO_TRIGGER_ISSUE, "the falsiness this fallback turns on"
    return fallback.group(1)


def _collect_plan_argv(*, with_matrix: bool) -> list[str]:
    """The composite's own `collect-plan` command line, as concrete argv."""
    body = str(_aggregate_step()["run"])
    invocations = [
        argv for argv in command_argv(body, PINNED_CLI) if argv and argv[0] == "collect-plan"
    ]
    assert len(invocations) == 1, "the composite must plan the run exactly once"
    return expand(
        invocations[0],
        arrays=shell_arrays(body) if with_matrix else {},
        values={
            "ROLE": "evaluate",
            "run_id": RUN_ID,
            "ISSUE": _normalized_issue(),
        },
    )


def _stub_run(workspace: Path) -> None:
    """The runner state the aggregate step reaches `collect-plan` with.

    The paths are the composite's own relative literals, so the workspace is
    built where it runs from rather than substituted — a renamed download root
    or matrix file then fails here too.
    """
    cell = workspace / "cell-artifacts" / f"evaluate-{ACTOR}-scotus-1-evt-petition-disposition"
    (cell / "data").mkdir(parents=True)
    (cell / "status.json").write_text(
        json.dumps(
            {**CELL, "actor": ACTOR, "run_id": RUN_ID}
            | {"produced": True, "validated": True, "agent_ok": True}
        )
    )
    (workspace / "missing-artifacts.txt").write_text("")
    (workspace / "plan-matrix.json").write_text(
        json.dumps({"include": [{**CELL, "evaluator_id": ACTOR, "run_id": RUN_ID}]})
    )


@pytest.mark.parametrize("with_matrix", [False, True])
def test_the_composites_issue_less_collect_plan_call_succeeds(
    with_matrix: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The seam itself: the composite's argv, its normalized sentinel, executed.

    Both states of the matrix flag, because the census argument is spliced in
    from a shell array under its own conditional and a scheduled round is
    precisely where an unexercised branch would first be taken.
    """
    _stub_run(tmp_path)
    monkeypatch.chdir(tmp_path)
    argv = _collect_plan_argv(with_matrix=with_matrix)

    result = CliRunner().invoke(app, argv)

    assert result.exit_code == 0, f"`fedcourts {' '.join(argv)}`\n{result.output}"
    plan = json.loads(result.stdout)
    assert plan["ready"] is not None, (
        "the run's output must still reach a PR with no issue to close"
    )
    assert plan["ready"]["artifact_dirs"], "the ready PR must carry the cell that produced output"
    # The one thing an issue-less run legitimately loses: nothing to close.
    assert "Closes #" not in plan["ready"]["body"]


def test_collect_plan_refuses_the_un_normalized_empty_issue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Why the normalization exists, pinned so it cannot quietly stop being true.

    If `--issue ""` ever became acceptable the fallback would look like dead
    weight and invite removal; while it exits 2 the fallback is load-bearing,
    and this is the failure the scheduled lane would take without it.
    """
    _stub_run(tmp_path)
    monkeypatch.chdir(tmp_path)
    raw = _collect_plan_argv(with_matrix=True)
    # Un-normalize the one argument, addressed by the option that takes it: a
    # value-equality swap would also rewrite any other option that happened to
    # be passed the same sentinel.
    raw[raw.index("--issue") + 1] = NO_TRIGGER_ISSUE

    result = CliRunner().invoke(app, raw)

    assert result.exit_code == 2
    # Styling-proof: on a CI runner rich interleaves color escapes into the
    # refusal box, splitting the asserted token mid-word.
    plain = " ".join(re.sub(r"\x1b\[[0-9;]*m", "", result.output).split())
    assert "--issue" in plain


def test_the_trigger_issue_never_reaches_the_collect_shell_un_normalized() -> None:
    """The fallback must sit between the input and the shell, not beside it.

    An `${{ inputs.issue }}` interpolated straight into the run body would
    bypass the `env:` default entirely — and would also splice a trigger-issue
    field into the script, which is the pattern the composite keeps every
    issue-derived value out of.
    """
    body = str(_aggregate_step()["run"])
    assert "${{ inputs.issue" not in body
    assert '--issue "$ISSUE"' in body, "the CLI must be handed the normalized value"
