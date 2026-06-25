import json
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app

runner = CliRunner()

_BATCH_BODY = """Long conference.

```json
[
  {"court": "scotus", "docket": 24001, "events": ["evt-petition-cert"]},
  {"court": "scotus", "docket": 24002, "events": ["evt-petition-cert"]}
]
```
"""


def _cells(stdout: str) -> list[dict[str, object]]:
    cells: list[dict[str, object]] = json.loads(stdout)["include"]
    return cells


def test_predict_matrix_batch_body_fans_out_across_cases(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)])
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    # 2 predictors x 2 cases x 1 event
    assert len(cells) == 4
    assert {(c["court"], c["docket"]) for c in cells} == {("scotus", 24001), ("scotus", 24002)}


def test_predict_matrix_legacy_single_case_flags_still_work(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-x",
        ],
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    assert len(cells) == 2
    assert {c["event_id"] for c in cells} == {"evt-x"}


def test_evaluate_matrix_batch_body_fans_out_across_cases(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)])
    assert result.exit_code == 0
    # 2 evaluators x 2 cases x 1 event
    assert len(_cells(result.stdout)) == 4


def test_matrix_without_body_or_flags_errors() -> None:
    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"])
    assert result.exit_code == 2
