"""The `paths` command must not name the outcome file to a predictor.

The realized ``outcome.json`` is the evaluator's ground truth. A forward
predictor cell runs `fedcourts paths` for input-path discovery; naming the
outcome path there is a leakage surface (and, if a resolved event slipped into
a forward queue, it would point the agent straight at the answer). The path is
resolved only for ``--role evaluator``.
"""

from __future__ import annotations

from typer.testing import CliRunner

from fedcourtsai.cli import app

runner = CliRunner()

_ARGS = [
    "paths",
    "--court",
    "scotus",
    "--docket",
    "73280412",
    "--event",
    "evt-petition-disposition",
]


def test_predictor_role_does_not_name_the_outcome_path() -> None:
    result = runner.invoke(app, [*_ARGS, "--role", "predictor"])
    assert result.exit_code == 0
    assert "event " in result.stdout  # the predictable event is still resolved
    assert "outcome.json" not in result.stdout  # ...but never the ground-truth file
    assert "evaluator-only" in result.stdout


def test_default_role_also_hides_the_outcome_path() -> None:
    # No role given (a script, or a predictor that forgot the flag) is protected
    # by default — the outcome path is opt-in, not opt-out.
    result = runner.invoke(app, _ARGS)
    assert result.exit_code == 0
    assert "outcome.json" not in result.stdout


def test_evaluator_role_resolves_the_outcome_path() -> None:
    result = runner.invoke(app, [*_ARGS, "--role", "evaluator"])
    assert result.exit_code == 0
    # The evaluator legitimately scores against outcome.json, so it is resolved.
    assert "outcome.json" in result.stdout
