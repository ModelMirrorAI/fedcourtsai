"""Back-test comparison: the paired estimator, the stratified draw, the two arms, the record."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import backtest_comparison as bc
from fedcourtsai import cert_backtest, cli, corpus, process_version
from fedcourtsai.backtest_comparison import (
    ArmForecast,
    PairedCell,
    ScoredCell,
    comparison_moments,
    comparison_pairs,
    exposure_note,
    paired_figures,
    pool_record,
    read_record,
    record_rows,
    stratified_figures,
    student_t_quantile,
    write_record,
)
from fedcourtsai.cert_backtest import (
    CERT_STRATA,
    STRATIFIED_DRAW_SALT,
    ReplayArm,
    _runners_by_predictor,
    draw_cert_backtest_set,
    draw_stratified_cert_set,
)
from fedcourtsai.cli import app
from fedcourtsai.merits_backtest import MeritsReplayOutcome, MeritsReplaySweep
from fedcourtsai.pipeline.runner import ClaudeCodeRunner, EngineFailed, RunRequest, StubRunner
from fedcourtsai.pricing import DEFAULT_MODELS
from fedcourtsai.schemas import (
    BacktestArmRole,
    BacktestComparison,
    BacktestComparisonArm,
    BacktestComparisonStratum,
    BacktestPooled,
    BacktestRecordRow,
    Disposition,
)
from tests.conftest import FixtureCorpus
from tests.test_cert_backtest import _cert_row
from tests.test_merits_backtest import _DECIDED_DOCKET, _replayable

runner = CliRunner()

INCUMBENT_MODEL = DEFAULT_MODELS["claude-code"]
CANDIDATE_MODEL = "claude-fable-5-2"


def _cell(
    case_id: str,
    outcome: int,
    incumbent: float | None,
    candidate: float | None,
    *,
    stratum: str | None = None,
    decided: date | None = None,
    moment: str = "distribution",
) -> PairedCell:
    def forecast(probability: float | None) -> ArmForecast | None:
        if probability is None:
            return None
        return ArmForecast(probability=probability, positive_call=probability >= 0.5)

    return PairedCell(
        case_id=case_id,
        moment=moment,
        outcome=outcome,
        decided=decided,
        stratum=stratum,
        provisioning="dated",
        incumbent=forecast(incumbent),
        candidate=forecast(candidate),
    )


# ---------------------------------------------------------------- the quantile


@pytest.mark.parametrize(
    ("df", "expected"),
    [(1, 12.7062), (2, 4.3027), (9, 2.2622), (30, 2.0423), (1e7, 1.9600)],
)
def test_the_t_quantile_matches_the_tables(df: float, expected: float) -> None:
    assert student_t_quantile(0.975, df) == pytest.approx(expected, abs=1e-3)


def test_the_t_quantile_is_symmetric_and_refuses_nonsense() -> None:
    assert student_t_quantile(0.5, 4) == 0.0
    assert student_t_quantile(0.025, 9) == pytest.approx(-student_t_quantile(0.975, 9))
    with pytest.raises(ValueError, match="probability"):
        student_t_quantile(1.0, 4)
    with pytest.raises(ValueError, match="degrees"):
        student_t_quantile(0.9, 0)


# ------------------------------------------------------------ the paired figures


def test_the_paired_difference_is_candidate_minus_incumbent_over_shared_cells() -> None:
    cells = [
        _cell("scotus/1", 1, 0.2, 0.6),  # 0.16 - 0.64 = -0.48, and the call turns correct
        _cell("scotus/2", 0, 0.1, 0.3),  # 0.09 - 0.01 = +0.08
        _cell("scotus/3", 0, 0.4, 0.6),  # 0.36 - 0.16 = +0.20, and the call turns wrong
        _cell("scotus/4", 1, 0.9, None),  # the candidate lost it: not a pair
    ]
    figures = paired_figures(cells)

    assert (figures.pairs, figures.positives) == (3, 1)
    differences = [-0.48, 0.08, 0.20]
    mean = sum(differences) / 3
    assert figures.mean_brier_difference == pytest.approx(mean)
    assert figures.incumbent_mean_brier == pytest.approx((0.64 + 0.01 + 0.16) / 3)
    assert figures.candidate_mean_brier == pytest.approx((0.16 + 0.09 + 0.36) / 3)
    sd = math.sqrt(sum((d - mean) ** 2 for d in differences) / 2)
    half = student_t_quantile(0.975, 2) * sd / math.sqrt(3)
    assert figures.interval_low == pytest.approx(mean - half)
    assert figures.interval_high == pytest.approx(mean + half)
    assert figures.degrees_of_freedom == 2
    assert (figures.calls_changed, figures.changed_to_correct, figures.changed_to_wrong) == (
        2,
        1,
        1,
    )


def test_the_pairing_cancels_what_the_arms_share() -> None:
    # Two arms that differ by a constant on every case: the difference has no
    # spread, so the interval collapses on it however much the cases vary.
    cells = [_cell(f"scotus/{n}", 0, p, p + 0.1) for n, p in enumerate([0.05, 0.2, 0.35, 0.3])]
    figures = paired_figures(cells)
    assert figures.interval_low is not None and figures.interval_high is not None
    assert figures.interval_low > 0  # the candidate is worse on every case, and it shows
    unpaired_spread = max(c.incumbent.probability**2 for c in cells if c.incumbent) - min(
        c.incumbent.probability**2 for c in cells if c.incumbent
    )
    assert figures.interval_high - figures.interval_low < unpaired_spread


def test_one_pair_has_a_difference_and_no_interval() -> None:
    figures = paired_figures([_cell("scotus/1", 0, 0.2, 0.1)])
    assert figures.pairs == 1
    assert figures.mean_brier_difference == pytest.approx(0.01 - 0.04)
    assert figures.interval_low is None and figures.degrees_of_freedom is None


def test_no_pair_has_no_figure() -> None:
    figures = paired_figures([_cell("scotus/1", 0, None, 0.1)])
    assert figures.pairs == 0 and figures.mean_brier_difference is None


def _stratified_cells() -> list[PairedCell]:
    return [
        _cell("scotus/1", 1, 0.2, 0.6, stratum="granted"),  # -0.48
        _cell("scotus/2", 1, 0.5, 0.7, stratum="granted"),  # 0.09 - 0.25 = -0.16
        _cell("scotus/3", 0, 0.1, 0.3, stratum="not-granted"),  # +0.08
        _cell("scotus/4", 0, 0.2, 0.2, stratum="not-granted"),  # 0
    ]


def test_the_stratified_figure_weights_each_stratum_by_its_population_share() -> None:
    figures = stratified_figures(_stratified_cells(), {"granted": 0.3, "not-granted": 0.7})
    assert figures is not None and figures.estimator == "stratified"
    assert figures.mean_brier_difference == pytest.approx(0.3 * -0.32 + 0.7 * 0.04)
    # The drawn set is half grants, so its own mean sits further toward them.
    assert paired_figures(_stratified_cells()).mean_brier_difference == pytest.approx(-0.14)
    variance = 0.3**2 * (2 * 0.16**2 / 1) / 2 + 0.7**2 * (2 * 0.04**2 / 1) / 2
    df = variance**2 / ((0.3**2 * 0.0512 / 2) ** 2 + (0.7**2 * 0.0032 / 2) ** 2)
    half = student_t_quantile(0.975, df) * math.sqrt(variance)
    assert figures.degrees_of_freedom == pytest.approx(df)
    assert figures.mean_brier_difference is not None
    assert figures.interval_high == pytest.approx(figures.mean_brier_difference + half)
    assert figures.incumbent_mean_brier == pytest.approx(
        0.3 * (0.64 + 0.25) / 2 + 0.7 * (0.01 + 0.04) / 2
    )


def test_a_dominant_stratum_leaves_the_estimate_and_takes_the_interval() -> None:
    # Nine parts in ten of the estimate rest on two denials: no interval is honest.
    figures = stratified_figures(_stratified_cells(), {"granted": 0.1, "not-granted": 0.9})
    assert figures is not None
    assert figures.mean_brier_difference == pytest.approx(0.1 * -0.32 + 0.9 * 0.04)
    assert (figures.interval_low, figures.interval_high, figures.degrees_of_freedom) == (
        None,
        None,
        None,
    )
    at_the_line = stratified_figures(
        _stratified_cells(), {"granted": 1 - bc.DOMINANT_STRATUM_WEIGHT, "not-granted": 0.8}
    )
    assert at_the_line is not None and at_the_line.interval_low is not None


def test_differences_with_no_spread_have_no_interval() -> None:
    cells = [_cell(f"scotus/{n}", 0, 0.1, 0.3) for n in range(4)]
    figures = paired_figures(cells)
    assert figures.mean_brier_difference == pytest.approx(0.08)
    assert figures.interval_low is None and figures.degrees_of_freedom is None
    stratified = stratified_figures(
        [_cell(f"scotus/{n}", n % 2, 0.5, 0.5, stratum=("a", "b")[n % 2]) for n in range(4)],
        {"a": 0.5, "b": 0.5},
    )
    assert stratified is not None and stratified.interval_low is None


def test_each_stratum_states_its_own_pairs_and_largest_move() -> None:
    cells = [*_stratified_cells(), _cell("scotus/5", 0, 0.2, None, stratum="not-granted")]
    granted, not_granted = bc.stratum_figures(cells)
    assert (granted.stratum, granted.pairs) == ("granted", 2)
    assert granted.mean_brier_difference == pytest.approx(-0.32)
    assert granted.largest_absolute_difference == pytest.approx(0.48)
    assert not_granted.pairs == 2
    assert not_granted.mean_brier_difference == pytest.approx(0.04)
    assert not_granted.largest_absolute_difference == pytest.approx(0.08)
    assert bc.stratum_figures([_cell("scotus/1", 0, 0.1, 0.2)]) == []  # an unstratified set


def test_a_weighted_stratum_with_no_pair_leaves_no_population_figure() -> None:
    cells = [c for c in _stratified_cells() if c.stratum == "not-granted"]
    assert stratified_figures(cells, {"granted": 0.1, "not-granted": 0.9}) is None
    # A stratum the population does not hold carries no weight and is not missed.
    only = stratified_figures(cells, {"granted": 0.0, "not-granted": 1.0})
    assert only is not None and only.mean_brier_difference == pytest.approx(0.04)


def test_a_stratum_of_one_pair_has_an_estimate_and_no_interval() -> None:
    cells = _stratified_cells()[1:]
    figures = stratified_figures(cells, {"granted": 0.1, "not-granted": 0.9})
    assert figures is not None
    assert figures.mean_brier_difference == pytest.approx(0.1 * -0.16 + 0.9 * 0.04)
    assert figures.interval_low is None


# ------------------------------------------------------- cutoffs and the report


def test_a_pair_is_after_both_cutoffs_only_when_both_are_known_and_passed() -> None:
    cells = [
        _cell("scotus/1", 0, 0.1, 0.2, decided=date(2026, 10, 5)),
        _cell("scotus/2", 0, 0.1, 0.2, decided=date(2026, 6, 30)),
        _cell("scotus/3", 0, 0.1, 0.2, decided=None),
    ]
    known = comparison_pairs(cells, [date(2026, 6, 30), date(2026, 1, 31)])
    assert [p.after_both_cutoffs for p in known] == [True, False, None]
    unknown = comparison_pairs(cells, [date(2026, 6, 30), None])
    assert [p.after_both_cutoffs for p in unknown] == [None, None, None]


def test_the_moment_block_splits_out_the_cases_neither_model_can_recall() -> None:
    cells = [
        _cell("scotus/1", 0, 0.1, 0.2, decided=date(2026, 10, 5)),
        _cell("scotus/2", 0, 0.3, 0.2, decided=date(2025, 6, 30)),
    ]
    cutoffs = [date(2026, 6, 30), date(2026, 6, 30)]
    [moment] = comparison_moments(cells, ["distribution"], [], cutoffs)
    assert moment.cells == 2 and moment.population is None
    assert moment.drawn_set.pairs == 2
    assert moment.after_both_cutoffs is not None and moment.after_both_cutoffs.pairs == 1
    assert moment.after_both_cutoffs.mean_brier_difference == pytest.approx(0.04 - 0.01)
    # With a cutoff unrecorded the split is undetermined, not empty.
    [undetermined] = comparison_moments(cells, ["distribution"], [], [date(2026, 6, 30), None])
    assert undetermined.after_both_cutoffs is None


def test_the_moment_block_reweights_a_stratified_draw() -> None:
    strata = [
        BacktestComparisonStratum(stratum="granted", population=10, weight=0.1, target=2, drawn=2),
        BacktestComparisonStratum(
            stratum="not-granted", population=90, weight=0.9, target=2, drawn=2
        ),
    ]
    [moment] = comparison_moments(_stratified_cells(), ["distribution"], strata, [None, None])
    assert moment.population is not None
    assert moment.population.mean_brier_difference == pytest.approx(0.1 * -0.32 + 0.9 * 0.04)
    assert moment.population.interval_low is None  # the not-granted class dominates
    assert [(s.stratum, s.pairs) for s in moment.by_stratum] == [
        ("granted", 2),
        ("not-granted", 2),
    ]


def _arms(incumbent: str, candidate: str, cells: list[PairedCell]) -> list[BacktestComparisonArm]:
    return [
        bc.arm_record(
            role,  # type: ignore[arg-type]
            engine="claude-code",
            model=model,
            requested_model=model,
            prompt=".github/prompts/predict.md",
            process_digest="sha256:" + "0" * 64,
            cells=cells,
        )
        for role, model in (("incumbent", incumbent), ("candidate", candidate))
    ]


def test_the_exposure_note_says_which_of_three_things_is_true() -> None:
    cells = [
        _cell("scotus/1", 0, 0.1, 0.2, decided=date(2026, 10, 5)),
        _cell("scotus/2", 0, 0.3, None, decided=date(2025, 6, 30)),
    ]
    arms = _arms(INCUMBENT_MODEL, CANDIDATE_MODEL, cells)
    assert [(a.cells_scored, a.cells_lost) for a in arms] == [(2, 0), (1, 1)]
    cutoffs = [a.training_cutoff for a in arms]
    assert all(cutoffs)  # both listed in the table
    assert "1 of 1 scored pair(s)" in exposure_note(comparison_pairs(cells, cutoffs), arms)
    early = [_cell("scotus/2", 0, 0.3, 0.2, decided=date(2025, 6, 30))]
    assert "No scored pair was decided after" in exposure_note(
        comparison_pairs(early, cutoffs), arms
    )
    unlisted = _arms(INCUMBENT_MODEL, "a-model-with-no-recorded-cutoff", cells)
    note = exposure_note(comparison_pairs(cells, [a.training_cutoff for a in unlisted]), unlisted)
    assert "No training cutoff is recorded for a-model-with-no-recorded-cutoff" in note


# ------------------------------------------------------------ the stratified draw


def _seed_mixed(db: Path) -> None:
    rows = [
        _cert_row(f"scotus/{n}", f"23-{n}", disposition=Disposition.granted)
        for n in range(100, 106)
    ] + [_cert_row(f"scotus/{n}", f"23-{n}") for n in range(200, 240)]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


def test_the_stratified_draw_takes_fixed_counts_at_random_within_each_class(
    tmp_path: Path,
) -> None:
    db = tmp_path / "corpus.sqlite3"
    _seed_mixed(db)
    with corpus.connect(db) as conn:
        drawn = draw_stratified_cert_set(conn, limit=8)
        again = draw_stratified_cert_set(conn, limit=8)
        spread = draw_cert_backtest_set(conn, limit=8, spread=True)

    assert [i.features.case_id for i in drawn.items] == [i.features.case_id for i in again.items]
    by_stratum = {s.stratum: s for s in drawn.strata}
    assert (by_stratum["granted"].population, by_stratum["not-granted"].population) == (6, 40)
    assert all((s.target, s.drawn) == (4, 4) for s in drawn.strata)
    outcomes = [cert_backtest.cert_stratum(i.actual_disposition) for i in drawn.items]
    assert outcomes == list(CERT_STRATA) * 4  # alternating, so a prefix stays balanced

    # Each stratum is the head of its own salted-hash order, and nothing else.
    def rank(case_id: str) -> str:
        return hashlib.sha256(f"{STRATIFIED_DRAW_SALT}|{drawn.key}|{case_id}".encode()).hexdigest()

    granted = sorted((f"scotus/{n}" for n in range(100, 106)), key=rank)[:4]
    assert [i.features.case_id for i in drawn.items if i.actual_disposition == "granted"] == (
        granted
    )
    # A different rule from the spread draw: its own salt, so its own order.
    assert STRATIFIED_DRAW_SALT != cert_backtest.SPREAD_DRAW_SALT
    assert {i.features.case_id for i in spread.items} != {i.features.case_id for i in drawn.items}


def test_a_short_stratum_is_drawn_short_and_says_so(tmp_path: Path) -> None:
    db = tmp_path / "corpus.sqlite3"
    _seed_mixed(db)
    with corpus.connect(db) as conn:
        drawn = draw_stratified_cert_set(conn, limit=20)
    by_stratum = {s.stratum: s for s in drawn.strata}
    assert (by_stratum["granted"].target, by_stratum["granted"].drawn) == (10, 6)
    assert by_stratum["not-granted"].drawn == 10
    assert len(drawn.items) == 16


def test_an_odd_limit_gives_the_spare_petition_to_the_larger_class(tmp_path: Path) -> None:
    db = tmp_path / "corpus.sqlite3"
    _seed_mixed(db)
    with corpus.connect(db) as conn:
        drawn = draw_stratified_cert_set(conn, limit=5)
    assert {s.stratum: s.target for s in drawn.strata} == {"granted": 2, "not-granted": 3}


# ------------------------------------------------------------------ the two arms


def test_an_arm_narrows_the_roster_and_carries_its_model_and_prompt() -> None:
    [(predictor, routed)] = _runners_by_predictor(
        Path("config"),
        None,
        arm=ReplayArm("claude-baseline", model=CANDIDATE_MODEL, prompt="elsewhere/predict.md"),
    )
    assert predictor.id == "claude-baseline" and predictor.prompt == "elsewhere/predict.md"
    assert isinstance(routed, ClaudeCodeRunner) and routed.model == CANDIDATE_MODEL
    assert cert_backtest.replay_model(routed) == CANDIDATE_MODEL
    # The incumbent arm leaves the engine's default and the registry's prompt alone.
    [(own, default)] = _runners_by_predictor(Path("config"), None, arm=ReplayArm("claude-baseline"))
    assert isinstance(default, ClaudeCodeRunner) and default.model == INCUMBENT_MODEL
    assert own.prompt != "elsewhere/predict.md"


def test_an_arm_on_an_offline_backend_runs_no_model() -> None:
    [(_, routed)] = _runners_by_predictor(
        Path("config"), "stub", arm=ReplayArm("claude-baseline", model=CANDIDATE_MODEL)
    )
    assert isinstance(routed, StubRunner)
    assert cert_backtest.replay_model(routed) is None


def test_an_arm_for_a_predictor_that_is_not_enabled_is_refused() -> None:
    with pytest.raises(ValueError, match="not an enabled predictor"):
        _runners_by_predictor(Path("config"), None, arm=ReplayArm("no-such-predictor"))


def test_the_configuration_digest_is_the_actors_own_until_something_changes() -> None:
    own = process_version.digest_for_actor(
        Path.cwd(), Path("config"), "predictor", "claude-baseline"
    )
    assert (
        process_version.digest_for_configuration(Path.cwd(), Path("config"), "claude-baseline")
        == own
    )
    changed = process_version.digest_for_configuration(
        Path.cwd(), Path("config"), "claude-baseline", model=CANDIDATE_MODEL
    )
    assert changed != own and changed.startswith("sha256:")


# ----------------------------------------------------------- the commands, offline


@pytest.fixture
def metrics_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "metrics"
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(root))
    return root


def _compare(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "cert-backtest-compare",
        "--predictor",
        "claude-baseline",
        "--candidate-model",
        CANDIDATE_MODEL,
        "--scope",
        "all",
        "--work-dir",
        str(tmp_path / "work"),
        *extra,
    ]


def test_a_stub_comparison_runs_offline_and_writes_the_paired_report(
    fixture_corpus: FixtureCorpus, tmp_path: Path, metrics_root: Path
) -> None:
    record = tmp_path / "record.jsonl"
    result = runner.invoke(
        app, _compare(tmp_path, "--draw", "spread", "--limit", "4", "--record", str(record))
    )
    assert result.exit_code == 0, result.output
    [path] = (metrics_root / "backtest-comparisons").glob("cert-claude-baseline-*.json")
    report = BacktestComparison.model_validate_json(path.read_text())

    assert (report.kind, report.stratum) == ("cert", "retrospective")
    assert report.dispatch.engine == "stub"
    assert report.dispatch.draw_rule == cert_backtest.SPREAD_DRAW_RULE
    incumbent, candidate = report.arms
    # The stub ran both arms, so no model ran, and the report still says which
    # two configurations it was asked to compare.
    assert (incumbent.engine, incumbent.model) == ("stub", None)
    assert (candidate.engine, candidate.model) == ("stub", None)
    assert (incumbent.requested_model, candidate.requested_model) == (
        INCUMBENT_MODEL,
        CANDIDATE_MODEL,
    )
    assert incumbent.process_digest != candidate.process_digest
    assert (incumbent.cells_scored, candidate.cells_scored) == (1, 1)
    [pair] = report.pairs
    assert pair.case_id == "scotus/304" and pair.outcome == 0
    # One deterministic backend under both arms: identical forecasts.
    assert pair.brier_difference == 0.0 and pair.call == "same"
    [moment] = report.moments
    assert moment.drawn_set.pairs == 1 and moment.population is None
    assert not report.strata
    # No model ran, so nothing was recorded, and the command says so.
    assert not record.exists()
    assert "no model ran" in result.stderr


def test_a_stratified_stub_comparison_states_its_strata(
    fixture_corpus: FixtureCorpus, tmp_path: Path, metrics_root: Path
) -> None:
    out = tmp_path / "comparison.json"
    result = runner.invoke(app, _compare(tmp_path, "--limit", "4", "--out", str(out)))
    assert result.exit_code == 0, result.output
    report = BacktestComparison.model_validate_json(out.read_text())
    assert report.dispatch.draw_rule == cert_backtest.STRATIFIED_DRAW_RULE
    by_stratum = {s.stratum: s for s in report.strata}
    # The fixture holds one replayable petition, a denial: the granted stratum
    # is empty in the population, so it carries no weight and is not missed.
    assert (by_stratum["granted"].population, by_stratum["granted"].weight) == (0, 0.0)
    assert (by_stratum["not-granted"].drawn, by_stratum["not-granted"].weight) == (1, 1.0)
    [moment] = report.moments
    assert moment.population is not None and moment.population.estimator == "stratified"
    assert [p.stratum for p in report.pairs] == ["not-granted"]


@dataclass(frozen=True)
class _ModelSensitiveRunner(ClaudeCodeRunner):
    """An agentic runner that spawns nothing: the stub's cell, moved by the model it carries."""

    def run(self, request: RunRequest) -> list[Path]:
        written = StubRunner().run(request)
        path = request.event_paths.prediction(request.actor_id, request.run_id)
        payload = json.loads(path.read_text())
        payload["probability"] = 0.1 if self.model == INCUMBENT_MODEL else 0.4
        path.write_text(json.dumps(payload))
        return written


class _OracleProbe(_ModelSensitiveRunner):
    seen: list[bool] = []  # noqa: RUF012 - one probe per test, reset by it
    watched: tuple[Path, ...] = ()

    def run(self, request: RunRequest) -> list[Path]:
        type(self).seen.append(any(path.exists() for path in type(self).watched))
        return super().run(request)


def test_a_real_engine_comparison_pairs_the_two_models_and_records_both(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    metrics_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": _ModelSensitiveRunner())
    out = tmp_path / "comparison.json"
    record = bc.record_path(metrics_root, "cert-compare", "run")
    result = runner.invoke(
        app,
        _compare(
            tmp_path,
            "--engine",
            "auto",
            "--draw",
            "spread",
            "--out",
            str(out),
            "--record",
            str(record),
        ),
    )
    assert result.exit_code == 0, result.output
    report = BacktestComparison.model_validate_json(out.read_text())
    incumbent, candidate = report.arms
    assert (incumbent.engine, incumbent.model) == ("claude-code", INCUMBENT_MODEL)
    assert (candidate.engine, candidate.model) == ("claude-code", CANDIDATE_MODEL)
    [pair] = report.pairs
    assert (pair.incumbent_probability, pair.candidate_probability) == (0.1, 0.4)
    assert pair.brier_difference == pytest.approx(0.16 - 0.01)
    assert pair.call == "same"  # both still call the denial
    assert "+0.1500" in result.output

    files, rows = read_record(record.parent)
    assert files == 1
    assert {(r.arm, r.model, r.probability) for r in rows} == {
        ("incumbent", INCUMBENT_MODEL, 0.1),
        ("candidate", CANDIDATE_MODEL, 0.4),
    }
    assert {r.process_digest for r in rows} == {
        incumbent.process_digest,
        candidate.process_digest,
    }
    assert all(
        (r.population, r.stratum, r.stratum_share, r.draw_rule)
        == ("cert:all", "not-granted", 1.0, cert_backtest.SPREAD_DRAW_RULE)
        for r in rows
    )

    pooled_out = tmp_path / "pooled.json"
    pooled = runner.invoke(app, ["backtest-pooled", "--out", str(pooled_out)])
    assert pooled.exit_code == 0, pooled.output
    board = BacktestPooled.model_validate_json(pooled_out.read_text())
    assert (board.files, board.rows) == (1, 2)
    # Two models are two entries: nothing pools across them.
    by_model = {e.model: e.mean_brier_score for e in board.entries}
    assert by_model == pytest.approx({INCUMBENT_MODEL: 0.01, CANDIDATE_MODEL: 0.16})


def test_the_record_and_the_reports_are_out_of_the_tree_while_cells_run(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    metrics_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    watched = (
        metrics_root / "backtest-record",
        metrics_root / "backtest-comparisons",
        metrics_root / "cert-backtest.json",
    )
    for directory in watched[:2]:
        directory.mkdir(parents=True)
        (directory / "earlier.txt").write_text("an earlier run's outcomes")
    watched[2].write_text("the standing report")
    _OracleProbe.seen, _OracleProbe.watched = [], watched
    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": _OracleProbe())

    result = runner.invoke(app, _compare(tmp_path, "--engine", "auto", "--draw", "spread"))

    assert result.exit_code == 0, result.output
    assert _OracleProbe.seen == [False, False]  # one cell per arm, neither saw them
    assert all((d / "earlier.txt").is_file() for d in watched[:2])  # and all are back
    assert watched[2].read_text() == "the standing report"


def test_a_candidate_that_scores_nothing_ends_the_comparison_before_the_incumbent_runs(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    metrics_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ran: list[str] = []

    @dataclass(frozen=True)
    class _RefusesTheCandidate(_ModelSensitiveRunner):
        def run(self, request: RunRequest) -> list[Path]:
            ran.append(self.model)
            if self.model != INCUMBENT_MODEL:
                raise EngineFailed("the engine does not serve this model")
            return super().run(request)

    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": _RefusesTheCandidate())
    out = tmp_path / "comparison.json"
    result = runner.invoke(
        app, _compare(tmp_path, "--engine", "auto", "--draw", "spread", "--out", str(out))
    )
    assert result.exit_code == 0, result.output
    assert ran == [CANDIDATE_MODEL]  # the incumbent's cells were never paid for
    report = BacktestComparison.model_validate_json(out.read_text())
    assert [(a.cells_scored, a.cells_lost) for a in report.arms] == [(0, 1), (0, 1)]
    assert report.moments[0].drawn_set.pairs == 0


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--predictor", "no-such-predictor", "--candidate-model", "m"], "not an enabled"),
        (["--predictor", "claude-baseline"], "the candidate is the incumbent"),
        (
            ["--predictor", "claude-baseline", "--candidate-model", INCUMBENT_MODEL],
            "the candidate is the incumbent",
        ),
        (
            ["--predictor", "claude-baseline", "--candidate-prompt", "no/such/prompt.md"],
            "is not a file",
        ),
        (
            ["--predictor", "claude-baseline", "--candidate-model", "m", "--draw", "recent"],
            "stratified",
        ),
        (
            ["--predictor", "claude-baseline", "--candidate-model", "m", "--engine", "nope"],
            "unknown backend",
        ),
        (
            ["--predictor", "claude-baseline", "--candidate-model", "m", "--engine", "codex"],
            "on its own",
        ),
    ],
)
def test_the_comparison_refuses_what_it_cannot_run(
    fixture_corpus: FixtureCorpus, metrics_root: Path, args: list[str], message: str
) -> None:
    result = runner.invoke(app, ["cert-backtest-compare", *args])
    assert result.exit_code == 2
    assert message in result.output


def test_a_candidate_changing_both_the_model_and_the_prompt_is_refused(
    fixture_corpus: FixtureCorpus, tmp_path: Path, metrics_root: Path
) -> None:
    prompt = tmp_path / "predict-candidate.md"
    prompt.write_text("A candidate prompt.\n")
    result = runner.invoke(
        app,
        _compare(tmp_path, "--candidate-prompt", str(prompt)),  # with its --candidate-model
    )
    assert result.exit_code == 2
    assert "not both" in result.output


def test_an_existing_record_is_refused_before_any_cell_runs(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    metrics_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = tmp_path / "cert-run.jsonl"
    record.write_text("")
    _OracleProbe.seen, _OracleProbe.watched = [], ()
    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": _OracleProbe())
    result = runner.invoke(app, _compare(tmp_path, "--engine", "auto", "--record", str(record)))
    assert result.exit_code == 2
    assert "never rewritten" in result.output
    assert _OracleProbe.seen == []  # nothing was paid for


def test_the_fence_puts_back_what_it_can_and_keeps_what_it_cannot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kept, stuck = tmp_path / "record", tmp_path / "reports"
    for directory in (kept, stuck):
        directory.mkdir()
        (directory / "earlier.txt").write_text("held")
    real_move = shutil.move

    def move(src: str, dst: str) -> object:
        if dst == str(stuck):
            raise OSError("the tree is read-only")
        return real_move(src, dst)

    with (
        pytest.raises(RuntimeError, match="could not be restored") as raised,
        cli._replay_oracles_withheld(stuck, kept, tmp_path / "absent"),
    ):
        assert not kept.exists() and not stuck.exists()
        kept.mkdir()  # written during the replay: the held copy wins
        (kept / "during.txt").write_text("a cell's doing")
        monkeypatch.setattr(shutil, "move", move)
    # One failed restore does not strand the other, and its copy survives in the stash.
    assert [f.name for f in kept.iterdir()] == ["earlier.txt"]
    stash = Path(str(raised.value).rsplit(" ", 1)[1])
    assert (stash / "0" / "earlier.txt").read_text() == "held"


def test_a_merits_incumbent_that_never_ran_reports_nothing_of_its_own(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ran = MeritsReplayOutcome(
        sweep=MeritsReplaySweep.model_construct(cells=["a cell"], fenced=[]),  # type: ignore[list-item]
        predictions={"claude-baseline": {}},
        ran_on={"claude-baseline": ("claude-code", CANDIDATE_MODEL)},
        unavailable=[],
        lost_cells=["the candidate's loss"],  # type: ignore[list-item]
    )
    calls: list[str] = []

    def replay(*args: object, **kwargs: object) -> MeritsReplayOutcome:
        calls.append(str(kwargs["work_root"]))
        return ran

    monkeypatch.setattr(bc, "replay_merits_predictors", replay)
    replay_ = bc.replay_merits_comparison(
        None,  # type: ignore[arg-type]
        [],
        config_root=tmp_path,
        work_root=tmp_path,
        run_id="run",
        incumbent=ReplayArm("claude-baseline"),
        candidate=ReplayArm("claude-baseline", model=CANDIDATE_MODEL),
    )
    assert calls == [str(tmp_path / "candidate")]
    assert (replay_.incumbent.ran_on, replay_.incumbent.lost_cells) == ({}, [])
    assert replay_.candidate is ran


def test_a_candidate_prompt_is_a_comparison_too(
    fixture_corpus: FixtureCorpus, tmp_path: Path, metrics_root: Path
) -> None:
    prompt = tmp_path / "predict-candidate.md"
    prompt.write_text("A candidate prompt.\n")
    out = tmp_path / "comparison.json"
    result = runner.invoke(
        app,
        [
            "cert-backtest-compare",
            "--predictor",
            "claude-baseline",
            "--candidate-prompt",
            str(prompt),
            "--scope",
            "all",
            "--draw",
            "spread",
            "--out",
            str(out),
            "--work-dir",
            str(tmp_path / "work"),
        ],
    )
    assert result.exit_code == 0, result.output
    report = BacktestComparison.model_validate_json(out.read_text())
    incumbent, candidate = report.arms
    assert candidate.prompt == str(prompt) and incumbent.prompt != candidate.prompt
    assert incumbent.requested_model == candidate.requested_model == INCUMBENT_MODEL
    assert incumbent.process_digest != candidate.process_digest


def test_the_standing_cert_backtest_records_its_cells_when_asked(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": _ModelSensitiveRunner())
    record = tmp_path / "backtest-record" / "cert-run.jsonl"

    def run(*extra: str) -> object:
        return runner.invoke(
            app,
            [
                "cert-backtest",
                "--out",
                str(tmp_path / "cert-backtest.json"),
                "--engine",
                "claude-code",
                "--work-dir",
                str(tmp_path / "work"),
                "--record",
                str(record),
                *extra,
            ],
        )

    result = run("--spread")
    assert result.exit_code == 0, result.output  # type: ignore[attr-defined]
    _, rows = read_record(record.parent)
    assert rows and {r.arm for r in rows} == {"standing"}
    assert {r.stratum_share for r in rows} == {1.0}
    # A record file is never rewritten, and the run is refused before a cell is paid for.
    again = run("--spread")
    assert again.exit_code == 2  # type: ignore[attr-defined]
    assert "never rewritten" in again.output  # type: ignore[attr-defined]


def test_a_recency_head_run_is_recorded_without_a_share(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": _ModelSensitiveRunner())
    record = tmp_path / "backtest-record" / "cert-run.jsonl"
    result = runner.invoke(
        app,
        [
            "cert-backtest",
            "--out",
            str(tmp_path / "cert-backtest.json"),
            "--engine",
            "claude-code",
            "--work-dir",
            str(tmp_path / "work"),
            "--record",
            str(record),
        ],
    )
    assert result.exit_code == 0, result.output
    files, rows = read_record(record.parent)
    assert rows and all(r.stratum_share is None for r in rows)
    [*entries] = pool_record(files, rows).entries
    assert all(e.mean_brier_score is None and e.unweighted_rows == e.rows for e in entries)


def test_a_stub_merits_comparison_pairs_both_moments(
    tmp_path: Path, metrics_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    with _replayable(tmp_path, _DECIDED_DOCKET):
        pass
    out = tmp_path / "comparison.json"
    result = runner.invoke(
        app,
        [
            "merits-backtest-compare",
            "--predictor",
            "claude-baseline",
            "--candidate-model",
            CANDIDATE_MODEL,
            "--terms",
            "2024",
            "--out",
            str(out),
            "--work-dir",
            str(tmp_path / "work"),
            "--corpus-backend",
            "local",
        ],
    )
    assert result.exit_code == 0, result.output
    report = BacktestComparison.model_validate_json(out.read_text())
    assert report.kind == "merits" and report.dispatch.terms == [2024]
    assert [m.moment for m in report.moments] == ["grant", "briefed"]
    assert [m.drawn_set.pairs for m in report.moments] == [1, 1]
    assert {(p.moment, p.outcome, p.decided) for p in report.pairs} == {
        ("grant", 1, date(2025, 5, 22)),
        ("briefed", 1, date(2025, 5, 22)),
    }
    assert all(p.brier_difference == 0.0 for p in report.pairs)


# -------------------------------------------------------------------- the record


def _scored(case_id: str, probability: float, outcome: int, share: float | None) -> ScoredCell:
    return ScoredCell(
        case_id=case_id,
        stage="cert",
        moment="distribution",
        probability=probability,
        outcome=outcome,
        decided=date(2026, 10, 5),
        provisioning="dated",
        stratum="granted" if outcome else "not-granted",
        stratum_share=share,
    )


def _rows(
    run_id: str,
    cells: list[ScoredCell],
    *,
    model: str = INCUMBENT_MODEL,
    process_digest: str = "sha256:" + "a" * 64,
    population: str = "cert:paid",
    draw_rule: str = "vintage-keyed-hash-v1",
    arm: BacktestArmRole = "standing",
) -> list[BacktestRecordRow]:
    return record_rows(
        cells,
        kind="cert",
        population=population,
        run_id=run_id,
        predictor_id="claude-baseline",
        arm=arm,
        engine="claude-code",
        model=model,
        process_digest=process_digest,
        draw_rule=draw_rule,
    )


def test_an_offline_backends_cells_are_never_recorded(tmp_path: Path) -> None:
    rows = record_rows(
        [_scored("scotus/1", 0.2, 0, 0.9)],
        kind="cert",
        population="cert:paid",
        run_id="run",
        predictor_id="claude-baseline",
        arm="standing",
        engine="stub",
        model=None,
        process_digest="",
        draw_rule="vintage-keyed-hash-v1",
    )
    assert rows == []
    assert write_record(tmp_path / "record" / "cert-run.jsonl", rows) is False
    assert not (tmp_path / "record").exists()


def test_the_record_is_one_file_per_run_and_never_rewritten(tmp_path: Path) -> None:
    path = bc.record_path(tmp_path, "cert", "20261111T000000Z")
    rows = _rows("20261111T000000Z", [_scored("scotus/1", 0.2, 0, 0.9)])
    assert write_record(path, rows) is True
    assert path == tmp_path / "backtest-record" / "cert-20261111T000000Z.jsonl"
    with pytest.raises(FileExistsError, match="never rewritten"):
        write_record(path, rows)
    files, read = read_record(path.parent)
    assert files == 1 and read == rows
    assert read_record(tmp_path / "absent") == (0, [])


def test_the_pooled_figure_is_post_stratified_on_the_outcome_class() -> None:
    # A simple random run (one grant in ten, here two rows of it) and an
    # outcome-stratified run (half grants) feed the same class means.
    random_run = _rows(
        "run-a",
        [_scored("scotus/1", 0.3, 1, 0.1), _scored("scotus/2", 0.1, 0, 0.9)],
    )
    stratified_run = _rows(
        "run-b",
        [
            _scored("scotus/3", 0.5, 1, 0.1),
            _scored("scotus/4", 0.3, 0, 0.9),
            # The same petition as run-a's denial, replayed again: averaged first.
            _scored("scotus/2", 0.3, 0, 0.9),
        ],
        draw_rule="outcome-stratified-hash-v1",
    )
    [entry] = pool_record(2, random_run + stratified_run).entries

    assert (entry.runs, entry.rows, entry.cases, entry.unweighted_rows) == (2, 5, 4, 0)
    by_stratum = {s.stratum: s for s in entry.strata}
    assert by_stratum["granted"].mean_brier_score == pytest.approx((0.49 + 0.25) / 2)
    assert (by_stratum["not-granted"].rows, by_stratum["not-granted"].cases) == (3, 2)
    assert by_stratum["not-granted"].mean_brier_score == pytest.approx(
        ((0.01 + 0.09) / 2 + 0.09) / 2
    )
    assert entry.mean_brier_score == pytest.approx(0.1 * 0.37 + 0.9 * 0.07)


def test_nothing_pools_across_a_model_a_digest_or_a_population() -> None:
    cells = [_scored("scotus/1", 0.3, 1, 0.1)]
    rows = (
        _rows("run-a", cells)
        + _rows("run-b", cells, model=CANDIDATE_MODEL)
        + _rows("run-c", cells, process_digest="sha256:" + "b" * 64)
        + _rows("run-d", cells, population="cert:all")
    )
    pooled = pool_record(4, rows)
    assert len(pooled.entries) == 4
    assert all(e.rows == 1 for e in pooled.entries)


def test_a_row_without_a_share_is_counted_and_left_out() -> None:
    rows = _rows("run-a", [_scored("scotus/1", 0.3, 1, 0.1)]) + _rows(
        "run-b", [_scored("scotus/9", 0.9, 0, None)], draw_rule="recency-head"
    )
    [entry] = pool_record(2, rows).entries
    assert (entry.rows, entry.unweighted_rows) == (2, 1)
    # One class of the population holds no weighted cell: its mean stands
    # alone and is not passed off as the population's.
    [granted] = entry.strata
    assert granted.stratum == "granted"
    assert granted.mean_brier_score == pytest.approx(0.49)
    assert entry.mean_brier_score is None


def test_a_class_share_is_averaged_over_runs_not_rows() -> None:
    # One large run and one small run recorded different mixes: each counts once.
    large = _rows(
        "run-a",
        [_scored(f"scotus/{n}", 0.5, 1, 0.2) for n in range(3)]
        + [_scored("scotus/7", 0.5, 0, 0.8)],
    )
    small = _rows("run-b", [_scored("scotus/8", 0.5, 1, 0.1), _scored("scotus/9", 0.5, 0, 0.9)])
    [entry] = pool_record(2, large + small).entries
    assert {s.stratum: s.share for s in entry.strata} == {
        "granted": pytest.approx(0.15),
        "not-granted": pytest.approx(0.85),
    }


def test_a_population_is_named_by_what_defines_it() -> None:
    assert bc.cert_population_name("paid", 0.3) == "cert:paid"
    assert bc.cert_population_name("selected", 0.3) == "cert:selected@0.3"
    assert bc.merits_population_name([2025, 2024]) == "merits:argued:OT2024+OT2025"
    assert bc.merits_population_name([2024]) != bc.merits_population_name([2024, 2025])


# ------------------------------------------------------------ the hand-off check


def _handoff(tmp_path: Path, rows: list[BacktestRecordRow], **kwargs: object) -> list[str]:
    record = tmp_path / "record.jsonl"
    record.write_text("".join(row.model_dump_json() + "\n" for row in rows))
    defaults: dict[str, object] = {
        "kind": "cert",
        "comparison_predictor": None,
        "known_predictors": {"claude-baseline"},
        "report": None,
        "record": record,
    }
    return bc.handoff_problems(**{**defaults, **kwargs})  # type: ignore[arg-type]


def test_a_runs_own_record_passes_the_handoff_check(tmp_path: Path) -> None:
    cells = [_scored("scotus/1", 0.3, 1, 0.1)]
    assert _handoff(tmp_path, _rows("run-a", cells)) == []
    compared = _rows("run-a", cells, arm="incumbent") + _rows("run-a", cells, arm="candidate")
    assert _handoff(tmp_path, compared, comparison_predictor="claude-baseline") == []


def test_the_handoff_check_names_what_a_run_could_not_have_written(tmp_path: Path) -> None:
    cells = [_scored("scotus/1", 0.3, 1, 0.1)]
    two_runs = _handoff(tmp_path, _rows("run-a", cells) + _rows("run-b", cells))
    assert two_runs == ["the record holds more than one run's rows"]
    assert _handoff(tmp_path, _rows("run-a", cells), kind="merits") == [
        "the record holds rows that are not merits rows"
    ]
    # A standing run writes no comparison arms, and a comparison no standing ones.
    assert "arms other than" in _handoff(tmp_path, _rows("run-a", cells, arm="candidate"))[0]
    assert "arms other than" in "".join(
        _handoff(tmp_path, _rows("run-a", cells), comparison_predictor="claude-baseline")
    )
    assert _handoff(tmp_path, _rows("run-a", cells), known_predictors={"codex-baseline"}) == [
        "the record names a predictor this run did not replay"
    ]
    assert "0 row(s)" in _handoff(tmp_path, [])[0]


def test_a_record_row_has_no_field_that_holds_prose(tmp_path: Path) -> None:
    [row] = _rows("run-a", [_scored("scotus/1", 0.3, 1, 0.1)])
    for name in ("run_id", "predictor_id", "model", "population", "case_id", "stratum"):
        with pytest.raises(ValueError, match=r"pattern|at most"):
            BacktestRecordRow.model_validate({**row.model_dump(), name: "a sentence of text"})
        with pytest.raises(ValueError, match=r"pattern|at most"):
            BacktestRecordRow.model_validate({**row.model_dump(), name: "x" * 161})
    record = tmp_path / "record.jsonl"
    record.write_text(json.dumps({**row.model_dump(mode="json"), "model": "two words"}) + "\n")
    assert bc.handoff_problems(
        kind="cert",
        comparison_predictor=None,
        known_predictors={"claude-baseline"},
        report=None,
        record=record,
    ) == ["the record does not parse: ValidationError"]


def test_the_handoff_check_reads_a_comparison_report_as_one(
    fixture_corpus: FixtureCorpus, tmp_path: Path, metrics_root: Path
) -> None:
    out = tmp_path / "comparison.json"
    assert runner.invoke(app, _compare(tmp_path, "--out", str(out))).exit_code == 0

    def check(*extra: str) -> object:
        return runner.invoke(
            app, ["backtest-handoff-check", "--report", str(out), *extra], catch_exceptions=False
        )

    good = check("--kind", "cert", "--comparison-predictor", "claude-baseline")
    assert good.exit_code == 0, good.output  # type: ignore[attr-defined]
    wrong = check("--kind", "merits", "--comparison-predictor", "codex-baseline")
    assert wrong.exit_code == 1  # type: ignore[attr-defined]
    assert "a cert comparison, not merits" in wrong.output  # type: ignore[attr-defined]
    assert "a different predictor" in wrong.output  # type: ignore[attr-defined]
    out.write_text("not a report")
    broken = check("--kind", "cert", "--comparison-predictor", "claude-baseline")
    assert broken.exit_code == 1  # type: ignore[attr-defined]
    assert "is not a comparison report" in broken.output  # type: ignore[attr-defined]


# ------------------------------------------------------------- the hand-off plan


def test_the_handoff_plan_names_each_modes_files_from_the_dispatch_alone() -> None:
    assert bc.handoff_plan("salience-gate", "", "77") == bc.HandoffPlan(
        report="salience-replay.json", record=None, kind=None
    )
    assert bc.handoff_plan("cert", "", "77") == bc.HandoffPlan(
        report="cert-backtest.json", record="backtest-record/cert-77.jsonl", kind="cert"
    )
    assert bc.handoff_plan("merits", "ignored=here", "77").report == "merits-backtest.json"
    compared = bc.handoff_plan("merits-compare", "claude-baseline=claude-fable-5-2", "77")
    assert compared == bc.HandoffPlan(
        report="backtest-comparisons/merits-claude-baseline-77.json",
        record="backtest-record/merits-77.jsonl",
        kind="merits",
        predictor="claude-baseline",
        model="claude-fable-5-2",
        limit_cap=10,
        cells_per_case=4,
    )
    cert = bc.handoff_plan("cert-compare", "claude-baseline=m", "77")
    assert (cert.limit_cap, cert.cells_per_case) == (20, 2)


@pytest.mark.parametrize(
    ("replay", "candidate", "run_id"),
    [
        ("cert-compare", "", "77"),
        ("cert-compare", "../x=m", "77"),
        ("cert-compare", "claude-baseline=a b", "77"),
        ("cert-compare", "claude-baseline=m\nx", "77"),
        ("cert-compare", "Claude=m", "77"),
        ("cert-compare", "claude-baseline=-m", "77"),
        ("cert-compare", "claude-baseline=m/n", "77"),
        ("nonsense", "", "77"),
        ("cert", "", "7/7"),
        ("cert", "", ""),
    ],
)
def test_the_handoff_plan_refuses_what_could_not_name_a_file(
    replay: str, candidate: str, run_id: str
) -> None:
    with pytest.raises(ValueError, match=r"candidate|run id|unknown"):
        bc.handoff_plan(replay, candidate, run_id)
    result = runner.invoke(
        app,
        ["backtest-handoff-plan", "--replay", replay, "--candidate", candidate, "--run-id", run_id],
    )
    assert result.exit_code == 2


def test_the_handoff_plan_command_prints_the_plan_as_json() -> None:
    result = runner.invoke(
        app,
        [
            "backtest-handoff-plan",
            "--replay",
            "cert-compare",
            "--candidate",
            "claude-baseline=claude-fable-5-2",
            "--run-id",
            "77",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["report"] == (
        "backtest-comparisons/cert-claude-baseline-77.json"
    )


def test_a_failed_record_write_is_annotated_and_does_not_fail_the_command(
    capsys: pytest.CaptureFixture[str],
) -> None:
    def append() -> None:
        raise FileExistsError("a cell made this run's file")

    with cli._record_failure_annotated("cert-backtest"):
        append()
    out = capsys.readouterr().out
    assert out.startswith("::error::cert-backtest: the pooled record was not written")
    assert "FileExistsError" in out and "a cell made" not in out
