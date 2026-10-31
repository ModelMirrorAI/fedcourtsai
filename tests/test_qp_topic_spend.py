"""The topic labeler's per-run spend record, its plan price, and their validation.

A labeling run refused at the reference gate spends as much as one that
publishes and writes no labels file, so each run's spend is its own record under
``data/qp-topics/spend/``, priced by the rule every cell's ``usage.json`` is.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline.qp_topics import build_label_plan, render_label_plan, run_spend_path
from fedcourtsai.planning_rates import (
    LABEL_RATES_USD_PER_ROW,
    SIDE_CODE_RATES_USD_PER_ROW,
    label_rate_usd_per_row,
)
from fedcourtsai.pricing import MODEL_RATES, TokenCounts, estimate_cost_usd
from fedcourtsai.schemas import QpTopicAgreement, QpTopicRunSpend
from fedcourtsai.serialize import write_json
from fedcourtsai.validate import validate_ledger

runner = CliRunner()

USAGE = {
    "input_tokens": 1_000,
    "output_tokens": 50_000,
    "cache_read_input_tokens": 2_000_000,
    "cache_creation_input_tokens": 100_000,
}


def _execution_file(tmp_path: Path, usage: dict[str, int] | None = None) -> Path:
    path = tmp_path / "execution.json"
    events: list[dict[str, Any]] = [{"type": "system"}]
    if usage is not None:
        events.append({"type": "result", "usage": usage})
    path.write_text(json.dumps(events))
    return path


def _agreement(tmp_path: Path, *, agree: int, n: int, passed: bool) -> Path:
    path = tmp_path / "agreement.json"
    write_json(
        path,
        QpTopicAgreement(
            overall_agree=agree,
            overall_n=n,
            overall_rate=agree / n,
            uncovered=0,
            floor=0.3,
            gate_passed=passed,
        ),
    )
    return path


def _spend(tmp_path: Path, *extra: str) -> tuple[int, str, Path]:
    out = tmp_path / "spend.json"
    result = runner.invoke(
        app,
        [
            "qp-topic-spend",
            "--execution-file",
            str(_execution_file(tmp_path, USAGE)),
            "--frame",
            "applications",
            "--run-id",
            "123",
            "--run-attempt",
            "1",
            "--model",
            "claude-opus-5-5",
            "--batch-rows",
            "1200",
            "--label-lines",
            "1200",
            "--recorded-at",
            "2026-10-28T09:40:00+00:00",
            "--out",
            str(out),
            *extra,
        ],
    )
    return result.exit_code, result.output, out


def test_a_refused_run_records_its_spend_and_its_gate_figures(tmp_path: Path) -> None:
    agreement = _agreement(tmp_path, agree=78, n=100, passed=False)
    code, output, out = _spend(tmp_path, "--agreement-file", str(agreement))
    assert code == 0, output
    record = QpTopicRunSpend.model_validate_json(out.read_text())
    assert record.outcome == "refused"
    assert (record.agree, record.n, record.rate, record.floor) == (78, 100, 0.78, 0.3)
    # The one pricing rule cells use.
    counts = TokenCounts(**{k: v for k, v in USAGE.items()})
    assert record.estimated_cost_usd == estimate_cost_usd("claude-opus-5-5", counts)
    assert record.cache_read_input_tokens == 2_000_000
    assert record.labeler == "claude-code/claude-opus-5-5"


def test_a_published_run_needs_a_measurement_that_cleared_the_gate(tmp_path: Path) -> None:
    passed = _agreement(tmp_path, agree=90, n=100, passed=True)
    code, output, out = _spend(tmp_path, "--agreement-file", str(passed), "--published")
    assert code == 0, output
    assert QpTopicRunSpend.model_validate_json(out.read_text()).outcome == "published"
    refused = _agreement(tmp_path, agree=70, n=100, passed=False)
    code, output, _ = _spend(tmp_path, "--agreement-file", str(refused), "--published")
    assert code == 2
    assert "cleared the gate" in output


def test_an_unmeasured_run_is_incomplete(tmp_path: Path) -> None:
    code, output, out = _spend(tmp_path, "--agreement-file", str(tmp_path / "absent.json"))
    assert code == 0, output
    record = QpTopicRunSpend.model_validate_json(out.read_text())
    assert record.outcome == "incomplete"
    assert record.agree is None and record.rate is None


def test_a_gate_passing_run_that_never_published_is_incomplete(tmp_path: Path) -> None:
    passed = _agreement(tmp_path, agree=90, n=100, passed=True)
    code, output, out = _spend(tmp_path, "--agreement-file", str(passed))
    assert code == 0, output
    assert QpTopicRunSpend.model_validate_json(out.read_text()).outcome == "incomplete"


def test_no_usage_records_nothing(tmp_path: Path) -> None:
    out = tmp_path / "spend.json"
    result = runner.invoke(
        app,
        [
            "qp-topic-spend",
            "--execution-file",
            str(_execution_file(tmp_path)),
            "--frame",
            "petitions",
            "--run-id",
            "1",
            "--run-attempt",
            "1",
            "--model",
            "claude-opus-5-5",
            "--batch-rows",
            "10",
            "--label-lines",
            "3",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 3
    assert not out.exists()


def test_the_default_destination_is_the_run_and_attempt_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_root = tmp_path / "data"
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    result = runner.invoke(
        app,
        [
            "qp-topic-spend",
            "--execution-file",
            str(_execution_file(tmp_path, USAGE)),
            "--frame",
            "petitions",
            "--run-id",
            "77",
            "--run-attempt",
            "2",
            "--model",
            "claude-fable-5",
            "--batch-rows",
            "1200",
            "--label-lines",
            "40",
        ],
    )
    assert result.exit_code == 0, result.output
    path = run_spend_path(data_root, "77", 2)
    assert path == data_root / "qp-topics" / "spend" / "77-2.json"
    assert validate_ledger(data_root).ok


def test_the_validator_holds_a_record_to_the_name_it_sits_under(tmp_path: Path) -> None:
    code, output, out = _spend(tmp_path)
    assert code == 0, output
    root = tmp_path / "data"
    good = run_spend_path(root, "123", 1)
    good.parent.mkdir(parents=True)
    good.write_text(out.read_text())
    assert validate_ledger(root).ok
    (good.parent / "124-1.json").write_text(out.read_text())
    (good.parent / "notes.json").write_text(out.read_text())
    problems = validate_ledger(root).problems
    assert any("names run 124 attempt 1 but records run 123 attempt 1" in p for p in problems)
    assert any("expected spend/<run_id>-<run_attempt>.json" in p for p in problems)


@pytest.mark.parametrize(
    "change",
    [
        {"recorded_at": "2026-10-28T09:40:00"},  # naive
        {"outcome": "refused", "agree": None, "n": None},  # refused carries its figures
        {"agree": 101},  # agree over n
        {"outcome": "published", "label_lines": 3},  # a published run labeled every row
        {"rate": 0.9},  # rate is agree / n
        {"rate": None},  # a measured run carries its rate
        {"outcome": "incomplete", "agree": None, "n": None},  # a rate without agree and n
    ],
)
def test_the_record_model_refuses_an_inconsistent_record(
    tmp_path: Path, change: dict[str, Any]
) -> None:
    code, output, out = _spend(
        tmp_path, "--agreement-file", str(_agreement(tmp_path, agree=78, n=100, passed=False))
    )
    assert code == 0, output
    payload = {**json.loads(out.read_text()), **change}
    with pytest.raises(ValueError):
        QpTopicRunSpend.model_validate(payload)


def test_the_label_plan_prices_rows_at_the_models_rate(tmp_path: Path) -> None:
    plan = build_label_plan(frame="petitions", model="claude-opus-5-5", rows=1200)
    assert plan["estimated_cost_usd_high"] == 24.0
    assert plan["rate_source"] == "measured"
    unknown = build_label_plan(frame="applications", model="claude-new-6", rows=100)
    assert unknown["rate_usd_per_row"] == max(LABEL_RATES_USD_PER_ROW.values())
    assert unknown["rate_source"] == "highest-rate fallback"
    assert "highest rate" in render_label_plan(unknown)
    out, report = tmp_path / "plan.json", tmp_path / "plan.md"
    result = runner.invoke(
        app,
        [
            "qp-label-plan",
            "--rows",
            "1200",
            "--model",
            "claude-fable-5",
            "--frame",
            "applications",
            "--out",
            str(out),
            "--report",
            str(report),
        ],
    )
    assert result.exit_code == 0, result.output
    written = json.loads(out.read_text())
    assert (written["frame"], written["rows"], written["estimated_cost_usd_high"]) == (
        "applications",
        1200,
        72.0,
    )
    assert "**$72.00**" in report.read_text()


def test_the_label_rates_sit_at_or_above_the_measured_batches() -> None:
    # The measured ceiling-sized batches: $10.01 (opus) and $37.48 / $60.16 (fable).
    assert label_rate_usd_per_row("claude-opus-5-5") * 1200 >= 10.01
    assert label_rate_usd_per_row("claude-fable-5") * 1200 >= 60.16


def test_an_unpriced_model_is_recorded_at_the_dearest_rate(tmp_path: Path) -> None:
    # The plan prices an unknown model at the top per-row rate, so the record
    # must never drop that run's spend: it prices at the dearest table entry
    # for these counts and names it.
    code, output, out = _spend(tmp_path, "--model", "claude-new-6")
    assert code == 0, output
    record = QpTopicRunSpend.model_validate_json(out.read_text())
    counts = TokenCounts(**dict(USAGE.items()))
    dearest = max(estimate_cost_usd(model, counts) for model in MODEL_RATES)
    assert record.model == "claude-new-6"
    assert record.priced_as is not None and record.priced_as in MODEL_RATES
    assert record.estimated_cost_usd == dearest
    known_code, _, known = _spend(tmp_path)
    assert known_code == 0
    assert QpTopicRunSpend.model_validate_json(known.read_text()).priced_as is None


def test_a_bad_recorded_at_exits_2_and_writes_nothing(tmp_path: Path) -> None:
    out = tmp_path / "spend.json"
    code, output, _ = _spend(tmp_path, "--recorded-at", "last tuesday")
    assert code == 2
    assert "not an ISO timestamp" in output
    assert not out.exists()


def test_a_side_coding_run_publishes_without_a_gate(tmp_path: Path) -> None:
    # The merits side coder has no reference set: a run that coded every row
    # publishes with no gate figures, and an agreement file is refused.
    code, output, out = _spend(tmp_path, "--frame", "alignment-sides", "--published")
    assert code == 0, output
    record = QpTopicRunSpend.model_validate_json(out.read_text())
    assert (record.frame, record.outcome) == ("alignment-sides", "published")
    assert (record.agree, record.n, record.rate, record.floor) == (None, None, None, None)
    agreement = _agreement(tmp_path, agree=78, n=100, passed=True)
    code, output, _ = _spend(
        tmp_path, "--frame", "alignment-sides", "--agreement-file", str(agreement)
    )
    assert code == 2, output


@pytest.mark.parametrize(
    "change",
    [
        {"outcome": "refused"},
        {"agree": 1, "n": 1, "rate": 1.0},
        {"floor": 0.3},
    ],
)
def test_a_side_coding_record_carries_no_gate(tmp_path: Path, change: dict[str, Any]) -> None:
    code, output, out = _spend(tmp_path, "--frame", "alignment-sides", "--published")
    assert code == 0, output
    payload = {**json.loads(out.read_text()), **change}
    with pytest.raises(ValueError):
        QpTopicRunSpend.model_validate(payload)


def test_the_side_coding_plan_prices_at_its_own_provisional_table(tmp_path: Path) -> None:
    plan = build_label_plan(frame="alignment-sides", model="claude-opus-5-5", rows=302)
    assert plan["rate_usd_per_row"] == SIDE_CODE_RATES_USD_PER_ROW["claude-opus-5-5"]
    assert plan["estimated_cost_usd_high"] == round(302 * 0.06, 2)
    assert plan["rate_source"] == "provisional"
    assert "provisional rate" in render_label_plan(plan)
    unknown = build_label_plan(frame="alignment-sides", model="claude-new-6", rows=10)
    assert unknown["rate_usd_per_row"] == max(SIDE_CODE_RATES_USD_PER_ROW.values())
    assert unknown["rate_source"] == "highest-rate fallback"
    # Never below the topic labeler's rate for the same model.
    for model, rate in LABEL_RATES_USD_PER_ROW.items():
        assert label_rate_usd_per_row(model, frame="alignment-sides") >= rate


def test_a_short_side_coding_run_is_incomplete(tmp_path: Path) -> None:
    code, output, out = _spend(tmp_path, "--frame", "alignment-sides", "--label-lines", "10")
    assert code == 0, output
    record = QpTopicRunSpend.model_validate_json(out.read_text())
    assert (record.outcome, record.agree, record.rate) == ("incomplete", None, None)
