"""Leaderboard aggregation and stratification over a small fixture ledger."""

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version as pv
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import (
    FORWARD,
    NO_STAGE_KEY,
    PROCEDURAL,
    RETROSPECTIVE,
    CellSkill,
    _evaluation_key,
    big_case_agreement,
    build_leaderboard,
    classify_stratum,
    evaluator_agreement,
    kendall_tau_b,
    skill_components,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.moments import first_moment
from fedcourtsai.schemas import (
    BaseRateBucket,
    BigCaseAssessment,
    BigCaseLeaderboard,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    Leaderboard,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
    Stage,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
    Stratum,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.store import iter_evaluations, iter_stratified_evaluations

runner = CliRunner()

# The stage-annotated cell shape `iter_stratified_evaluations` yields and
# `build_leaderboard` consumes.
Cell = tuple[Evaluation, Stratum, Stage | None, Moment | None]

#: Sentinel: derive the stage's first moment rather than hard-coding one, so a
#: fixture that names a stage cannot accidentally pair it with another stage's
#: moment.
_DERIVE: Any = object()


def _moment_for(stage: Stage | None, moment: Moment | None) -> Moment | None:
    if moment is not _DERIVE:
        return moment
    return first_moment(stage) if stage is not None else None


def _evaluation(predictor_id: str, **kw: object) -> Evaluation:
    base: dict[str, object] = dict(
        case_id="ca9/123",
        event_id="evt-motion-stay",
        predictor_id=predictor_id,
        evaluator_id="eval-a",
        engine=Engine.claude_code,
        run_id="r1",
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        correct=1,
        brier_score=0.1,
        vote_accuracy=1.0,
        reasoning_quality=0.8,
    )
    base.update(kw)
    return Evaluation.model_validate(base)


def _forward(
    ev: Evaluation, stage: Stage | None = Stage.cert, moment: Moment | None = _DERIVE
) -> Cell:
    return (ev, FORWARD, stage, _moment_for(stage, moment))


def _retro(
    ev: Evaluation, stage: Stage | None = Stage.cert, moment: Moment | None = _DERIVE
) -> Cell:
    return (ev, RETROSPECTIVE, stage, _moment_for(stage, moment))


def _write(data_root: Path, ev: Evaluation) -> None:
    court, _, docket = ev.case_id.partition("/")
    path = (
        CasePaths(data_root, court, int(docket))
        .event(ev.event_id)
        .evaluation(ev.evaluator_id, ev.predictor_id, ev.run_id)
    )
    write_json(path, ev)


def _write_cell(  # noqa: PLR0913 - one keyword per artifact field a test varies
    data_root: Path,
    ev: Evaluation,
    *,
    predicted_at: datetime = datetime(2026, 6, 20, tzinfo=UTC),
    resolved_at: date = date(2026, 6, 23),
    disposition_basis: str = "standard",
    process_version: ProcessVersion | None = None,
    kind: EventKind = EventKind.petition,
    stage: Stage | None = None,
    context: PredictionContext | None = None,
    big_case_score: float | None = None,
) -> None:
    """A full scored cell: evaluation plus the event, prediction, and outcome it targets.

    ``process_version`` stamps the prediction, which is what the frozen filter
    partitions on; ``None`` leaves it a shakedown cell. ``kind``/``stage`` land
    on the event.yaml the stratification join reads — the petition-kind default
    with a null stage is the committed-ledger shape, which stratifies as cert.
    ``context`` is the harness-frozen conditioning the realized-Term skill reads
    the band, version, and Term off.
    """
    _write(data_root, ev)
    court, _, docket = ev.case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(ev.event_id)
    write_yaml(
        event.event_file,
        PredictableEvent(
            event_id=ev.event_id,
            case_id=ev.case_id,
            kind=kind,
            stage=stage,
            title="Test event",
            resolved=True,
        ),
    )
    write_json(
        event.prediction(ev.predictor_id, "p1"),
        Prediction(
            case_id=ev.case_id,
            event_id=ev.event_id,
            predictor_id=ev.predictor_id,
            engine=Engine.claude_code,
            run_id="p1",
            created_at=predicted_at,
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
            big_case_score=big_case_score,
            process_version=process_version,
            context=context,
        ),
    )
    write_json(
        event.outcome,
        Outcome.model_validate(
            dict(
                case_id=ev.case_id,
                event_id=ev.event_id,
                resolved_at=resolved_at,
                actual_disposition=Disposition.granted,
                actual_granted=1,
                disposition_basis=disposition_basis,
            )
        ),
    )


def test_classify_stratum_splits_on_resolution_vs_commit() -> None:
    predicted = datetime(2026, 6, 20, 12, 0, tzinfo=UTC)
    # Event resolved after the prediction -> a true forward forecast.
    assert classify_stratum(predicted, date(2026, 6, 23)) == FORWARD
    # Event resolved decades earlier -> retrospective by construction.
    assert classify_stratum(predicted, date(1950, 12, 11)) == RETROSPECTIVE
    # Same-day tie: the within-day ordering is unknowable, so the conservative
    # reading applies and the cell is never presented as forward.
    assert classify_stratum(predicted, date(2026, 6, 20)) == RETROSPECTIVE


def test_empty_ledger_is_empty_board() -> None:
    board = build_leaderboard([])
    assert board.predictors_ranked == 0
    assert board.evaluations_total == 0
    assert board.forward_evaluations == 0
    assert board.retrospective_evaluations == 0
    assert board.entries == []


def test_aggregates_per_predictor_per_stratum() -> None:
    cells = [
        _forward(_evaluation("alpha", correct=1, brier_score=0.1, event_id="evt-a")),
        _retro(
            _evaluation(
                "alpha", correct=0, brier_score=0.3, event_id="evt-b", evaluator_id="eval-b"
            )
        ),
        _forward(_evaluation("beta", correct=1, brier_score=0.2, event_id="evt-a")),
    ]
    board = build_leaderboard(cells)
    assert board.predictors_ranked == 2
    assert board.evaluations_total == 3
    assert board.forward_evaluations == 2
    assert board.retrospective_evaluations == 1
    alpha = next(e for e in board.entries if e.predictor_id == "alpha")
    # The strata never blend: one perfect forward cell, one missed retro cell.
    assert alpha.forward is not None and alpha.retrospective is not None
    assert alpha.forward.accuracy == 1.0
    assert alpha.forward.mean_brier_score == 0.1
    assert alpha.retrospective.accuracy == 0.0
    assert alpha.retrospective.mean_brier_score == 0.3
    assert alpha.evaluators == 2
    # A stratum with no cells is null, never zero-filled.
    beta = next(e for e in board.entries if e.predictor_id == "beta")
    assert beta.retrospective is None


def test_ranking_orders_by_forward_then_retrospective() -> None:
    cells = [
        # No forward cells at all: sorts after everyone with any forward cell,
        # however strong its retrospective numbers.
        _retro(_evaluation("retro-only", correct=1, brier_score=0.05)),
        _forward(_evaluation("low", correct=0, brier_score=0.1)),
        _forward(_evaluation("high", correct=1, brier_score=0.4)),
        _forward(_evaluation("mid-a", correct=1, brier_score=0.5)),
        _forward(_evaluation("mid-b", correct=1, brier_score=0.2)),
    ]
    board = build_leaderboard(cells)
    order = [(e.rank, e.predictor_id) for e in board.entries]
    # Forward accuracy desc; perfect-but-tied predictors split on forward Brier
    # (lower wins); 0-forward-accuracy still beats having no forward cells.
    assert order == [
        (1, "mid-b"),
        (2, "high"),
        (3, "mid-a"),
        (4, "low"),
        (5, "retro-only"),
    ]


def test_missing_optionals_average_only_over_present() -> None:
    cells = [
        _forward(_evaluation("alpha", brier_score=0.2, vote_accuracy=None, reasoning_quality=None)),
        _forward(_evaluation("alpha", brier_score=None, vote_accuracy=0.5, reasoning_quality=0.6)),
    ]
    stratum = build_leaderboard(cells).entries[0].forward
    assert stratum is not None
    assert stratum.mean_brier_score == 0.2
    assert stratum.mean_vote_accuracy == 0.5
    assert stratum.mean_reasoning_quality == 0.6


def test_all_optionals_absent_stay_none() -> None:
    cells = [
        _forward(_evaluation("alpha", brier_score=None, vote_accuracy=None, reasoning_quality=None))
    ]
    stratum = build_leaderboard(cells).entries[0].forward
    assert stratum is not None
    assert stratum.mean_brier_score is None
    assert stratum.mean_vote_accuracy is None
    assert stratum.mean_reasoning_quality is None
    assert stratum.population_brier_skill_score is None


def test_brier_skill_score_aggregates_over_present_cells() -> None:
    # The skill column covers only cells carrying a baseline, and admits
    # negative skill (a forecast worse than the segment base rate).
    scored = [_evaluation("alpha", event_id="evt-a"), _evaluation("alpha", event_id="evt-b")]
    unscored = _evaluation("alpha", event_id="evt-c")
    cells = [_forward(ev) for ev in [*scored, unscored]]
    stratum = (
        build_leaderboard(
            cells,
            skills={
                _evaluation_key(scored[0]): CellSkill(brier=0.06, prior_term_baseline=0.1),
                _evaluation_key(scored[1]): CellSkill(brier=0.24, prior_term_baseline=0.2),
            },
        )
        .entries[0]
        .forward
    )
    assert stratum is not None
    # A ratio of sums (0.30 Brier over 0.30 baseline = 0.0), not the mean of the
    # per-cell ratios +0.4 and -0.2 that the same two cells would give (+0.1).
    assert stratum.population_brier_skill_score == pytest.approx(0.0)
    assert stratum.skill_scored == 2


def test_skill_aggregates_as_a_ratio_of_sums_not_a_mean_of_ratios() -> None:
    """The estimator, pinned on the case that separates them.

    Two cells: a low-baseline denial the forecast nearly nails, and a
    high-baseline grant it misses. Per-cell ratios are +0.99 and -1.0, which
    average to a near-zero saying the forecast was about as good as its
    baseline; the population skill divides total Brier by total baseline Brier
    and reports the -0.96 the cells actually add up to. Cert's class imbalance
    makes this the difference between paying a predictor to under-forecast
    grants and not.
    """
    cheap = _evaluation("alpha", event_id="evt-cheap")
    dear = _evaluation("alpha", event_id="evt-dear")
    stratum = (
        build_leaderboard(
            [_forward(cheap), _forward(dear)],
            skills={
                _evaluation_key(cheap): CellSkill(brier=0.0001, prior_term_baseline=0.01),
                _evaluation_key(dear): CellSkill(brier=0.9, prior_term_baseline=0.45),
            },
        )
        .entries[0]
        .forward
    )
    assert stratum is not None
    per_cell_mean = ((1 - 0.0001 / 0.01) + (1 - 0.9 / 0.45)) / 2
    assert per_cell_mean == pytest.approx(-0.00500, abs=1e-5)
    assert stratum.population_brier_skill_score == pytest.approx(1 - 0.9001 / 0.46)
    assert stratum.population_brier_skill_score == pytest.approx(-0.9567, abs=1e-4)


def test_iter_evaluations_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert iter_evaluations(tmp_path) == []
    assert iter_stratified_evaluations(tmp_path) == []


def test_iter_evaluations_reads_ledger(tmp_path: Path) -> None:
    _write(tmp_path, _evaluation("alpha", event_id="evt-a"))
    _write(tmp_path, _evaluation("beta", event_id="evt-b"))
    found = iter_evaluations(tmp_path)
    assert {e.predictor_id for e in found} == {"alpha", "beta"}


def test_iter_stratified_evaluations_joins_prediction_and_outcome(tmp_path: Path) -> None:
    # A prediction committed before resolution is forward; one committed after
    # (a different event) is retrospective.
    _write_cell(
        tmp_path,
        _evaluation("alpha", event_id="evt-a"),
        predicted_at=datetime(2026, 6, 20, tzinfo=UTC),
        resolved_at=date(2026, 6, 23),
    )
    _write_cell(
        tmp_path,
        _evaluation("alpha", event_id="evt-b"),
        predicted_at=datetime(2026, 6, 20, tzinfo=UTC),
        resolved_at=date(1950, 12, 11),
    )
    strata = {
        ev.event_id: stratum
        for ev, stratum, _stage, _moment in iter_stratified_evaluations(tmp_path, frozen_only=False)
    }
    assert strata == {"evt-a": FORWARD, "evt-b": RETROSPECTIVE}


def test_iter_stratified_evaluations_normalizes_the_event_stage(tmp_path: Path) -> None:
    # The join reads each event's stage off its event.yaml, normalized for
    # stratification: an explicit stage passes through; a null stage on a
    # petition/appeal-kind event reads as cert (the case-baseline kinds resolve
    # on the cert standard by construction); a null stage on any other kind
    # stays no-stage, never guessed.
    _write_cell(tmp_path, _evaluation("p", event_id="evt-a"), kind=EventKind.petition, stage=None)
    _write_cell(tmp_path, _evaluation("p", event_id="evt-b"), kind=EventKind.appeal, stage=None)
    _write_cell(
        tmp_path,
        _evaluation("p", event_id="evt-c"),
        kind=EventKind.motion,
        stage=Stage.interim,
    )
    _write_cell(tmp_path, _evaluation("p", event_id="evt-d"), kind=EventKind.motion, stage=None)
    stages = {
        ev.event_id: stage
        for ev, _stratum, stage, _moment in iter_stratified_evaluations(tmp_path, frozen_only=False)
    }
    assert stages == {
        "evt-a": Stage.cert,
        "evt-b": Stage.cert,
        "evt-c": Stage.interim,
        "evt-d": None,
    }


def test_committed_interim_cell_lands_in_the_stages_block_not_the_cert_board(
    tmp_path: Path,
) -> None:
    # End to end over the committed ledger: an evaluated interim cell — the
    # shape the interim predict path produces (motion-kind event, interim
    # stage) — flows through the join into the leaderboard's `stages` block,
    # never the ranked cert board or its counts.
    _write_cell(tmp_path, _evaluation("cert-p", event_id="evt-a"))
    _write_cell(
        tmp_path,
        _evaluation("interim-p", event_id="evt-motion-disposition"),
        kind=EventKind.motion,
        stage=Stage.interim,
    )
    board = build_leaderboard(list(iter_stratified_evaluations(tmp_path, frozen_only=False)))
    assert [e.predictor_id for e in board.entries] == ["cert-p"]
    assert board.evaluations_total == 1  # cert only
    interim = board.stages["interim"]
    assert [e.predictor_id for e in interim.entries] == ["interim-p"]
    assert interim.evaluations_total == 1


def test_cli_writes_valid_sorted_leaderboard(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_cell(data_root, _evaluation("alpha", correct=0, brier_score=0.3, event_id="evt-a"))
    _write_cell(data_root, _evaluation("beta", correct=1, brier_score=0.2, event_id="evt-b"))
    out = tmp_path / "leaderboard.json"
    result = runner.invoke(
        app,
        ["leaderboard", "--out", str(out), "--all-versions"],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert result.exit_code == 0, result.output
    assert "2 forward / 0 retrospective" in result.output
    board = read_model(out, Leaderboard)
    assert board.process_scope == "all"
    assert [e.predictor_id for e in board.entries] == ["beta", "alpha"]
    # Deterministic: a second run reproduces the file byte for byte.
    first = out.read_text()
    runner.invoke(
        app,
        ["leaderboard", "--out", str(out), "--all-versions"],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert out.read_text() == first


def test_mootness_outcome_routes_to_the_procedural_stratum(tmp_path: Path) -> None:
    # A mootness-basis outcome (a Munsingwear vacatur, a dismissal as moot)
    # carries a label that tracks vacatur practice, not cert-worthiness — the
    # cell segments into the procedural stratum regardless of timing, even
    # when the prediction was a true forward forecast.
    ev = _evaluation("p-moot")
    _write_cell(
        tmp_path,
        ev,
        predicted_at=datetime(2026, 6, 20, tzinfo=UTC),
        resolved_at=date(2026, 6, 23),  # timing alone would read forward
        disposition_basis="mootness",
    )
    ((_, stratum, _stage, _moment),) = iter_stratified_evaluations(tmp_path, frozen_only=False)
    assert stratum == PROCEDURAL


def test_procedural_cells_aggregate_separately_and_never_rank(tmp_path: Path) -> None:
    # Predictor A: one real forward win. Predictor B: a perfect score that is
    # purely procedural. A must outrank B — procedural accuracy buys no rank —
    # and the totals must report the segmentation.
    board = build_leaderboard(
        [
            (
                _evaluation("a", correct=1, brier_score=0.1),
                FORWARD,
                Stage.cert,
                Moment.distribution,
            ),
            (
                _evaluation("b", correct=1, brier_score=0.0),
                PROCEDURAL,
                Stage.cert,
                Moment.distribution,
            ),
        ]
    )
    assert [e.predictor_id for e in board.entries] == ["a", "b"]
    a, b = board.entries
    assert a.forward is not None and a.procedural is None
    assert b.forward is None and b.retrospective is None
    assert b.procedural is not None and b.procedural.accuracy == 1.0
    assert board.procedural_evaluations == 1
    assert board.evaluations_total == 2
    assert board.forward_evaluations == 1


def test_non_cert_stages_report_separately_and_never_rank() -> None:
    # The ranked board is cert's FIRST moment. An interim cell and a stage-less
    # cell land in their own `stage@moment` blocks — out of the entries, out of
    # the top-level counts, never pooled with cert or with each other.
    board = build_leaderboard(
        [
            (
                _evaluation("a", correct=1, brier_score=0.1),
                FORWARD,
                Stage.cert,
                Moment.distribution,
            ),
            (_evaluation("b", correct=1, brier_score=0.0), FORWARD, Stage.interim, Moment.arrival),
            (_evaluation("c", correct=0, brier_score=0.5), RETROSPECTIVE, None, None),
        ]
    )
    assert [e.predictor_id for e in board.entries] == ["a"]
    assert board.predictors_ranked == 1
    assert board.evaluations_total == 1  # cert only; each stage carries its own
    assert set(board.stages) == {"interim@arrival", NO_STAGE_KEY}
    interim = board.stages["interim@arrival"]
    assert interim.evaluations_total == 1
    assert interim.forward_evaluations == 1
    (b_entry,) = interim.entries
    assert b_entry.predictor_id == "b"
    assert b_entry.forward is not None and b_entry.forward.accuracy == 1.0
    no_stage = board.stages[NO_STAGE_KEY]
    assert no_stage.retrospective_evaluations == 1


def test_the_empty_stage_axis_is_omitted_from_the_payload() -> None:
    # The StatPack omit-when-absent rule: an all-cert board serializes with no
    # `stages` key at all — which is also what keeps the committed
    # metrics/leaderboard.json byte-identical.
    all_cert = build_leaderboard([_forward(_evaluation("a"))])
    assert "stages" not in all_cert.model_dump(mode="json")
    with_stage = build_leaderboard([_forward(_evaluation("a"), stage=Stage.interim)])
    # Keyed on the pair, because two moments of one stage are two populations.
    assert "interim@arrival" in with_stage.model_dump(mode="json")["stages"]


def test_skill_scored_counts_the_skill_figures_denominator() -> None:
    # The silent gap between the skill column's denominator and `evaluations`
    # must be visible: three cells, two carrying a baseline to score against.
    scored = [_evaluation("alpha", event_id="evt-a"), _evaluation("alpha", event_id="evt-b")]
    cells = [_forward(ev) for ev in [*scored, _evaluation("alpha", event_id="evt-c")]]
    stratum = (
        build_leaderboard(
            cells,
            skills={
                _evaluation_key(ev): CellSkill(brier=0.1, prior_term_baseline=0.2) for ev in scored
            },
        )
        .entries[0]
        .forward
    )
    assert stratum is not None
    assert stratum.evaluations == 3
    assert stratum.skill_scored == 2
    assert stratum.population_brier_skill_score == pytest.approx(1 - 0.2 / 0.4)


# --- realized-Term skill: the ex-post complement to the prior-Term mean -----------


def _statpack(*, resolved: int = 72, grants: int = 32, version: str = "sal-v1") -> StatPack:
    """A pack whose OT2025 `high` band carries the published OT2025 counts."""
    return StatPack(
        corpus_rows=1,
        terms=[
            StatPackTerm(
                term=2025,
                base_rates=BaseRateBucket(),
                salience_version=version,
                segments=[
                    StatPackTermSegment(
                        band="high",
                        resolved=resolved,
                        weighted_resolved=resolved,
                        est_grant_rate=grants / resolved,
                        prefix_resolved=resolved,
                        prefix_weighted_resolved=resolved,
                        prefix_est_grant_rate=grants / resolved,
                    )
                ],
            )
        ],
    )


def _frozen_context() -> PredictionContext:
    return PredictionContext(
        mode="forward",
        snapshot_date=date(2026, 1, 5),
        signals_observable=True,
        distribution_count=3,
        band="high",
        salience_version="sal-v1",
        term=2025,
    )


def test_realized_term_skill_aggregates_with_its_own_denominator() -> None:
    # Its own `*_scored` count, separate from the prior-Term column's: the two
    # omit different cells, so one denominator cannot stand for both — and each
    # divides only its own sums.
    both = _evaluation("alpha", event_id="evt-a")
    prior_only = _evaluation("alpha", event_id="evt-b")
    stratum = (
        build_leaderboard(
            [_forward(both), _forward(prior_only)],
            skills={
                _evaluation_key(both): CellSkill(
                    brier=0.1, prior_term_baseline=0.2, realized_term_baseline=0.05
                ),
                _evaluation_key(prior_only): CellSkill(brier=0.1, prior_term_baseline=0.2),
            },
        )
        .entries[0]
        .forward
    )
    assert stratum is not None
    assert stratum.evaluations == 2
    assert stratum.skill_scored == 2
    assert stratum.population_brier_skill_score == pytest.approx(1 - 0.2 / 0.4)
    # The cell with no realized-Term baseline is left out, never a zero — and
    # the realized figure divides by 0.05 alone, not by the prior column's sum.
    assert stratum.realized_term_skill_scored == 1
    assert stratum.population_realized_term_skill_score == pytest.approx(1 - 0.1 / 0.05)


def test_realized_term_skill_is_absent_when_nothing_scored() -> None:
    stratum = build_leaderboard([_forward(_evaluation("alpha"))]).entries[0].forward
    assert stratum is not None
    assert stratum.population_realized_term_skill_score is None
    assert stratum.realized_term_skill_scored == 0


def test_realized_term_skill_never_moves_the_ranking() -> None:
    # It is ex post — no predictor could have known its Term's realized rate —
    # so it must not rank, in-season or ever. The two predictors are identical
    # on every key the ranking reads (accuracy, Brier, stratum), so the realized
    # column is the ONLY thing that could reorder them: the tie must still break
    # on `predictor_id`, not on the skill it is handed.
    alpha = _evaluation("alpha", correct=1, brier_score=0.2)
    beta = _evaluation("beta", correct=1, brier_score=0.2)
    cells = [_forward(alpha), _forward(beta)]
    assert [e.predictor_id for e in build_leaderboard(cells).entries] == ["alpha", "beta"]
    with_skill = build_leaderboard(
        cells,
        skills={
            _evaluation_key(alpha): CellSkill(brier=0.2, realized_term_baseline=0.1),
            _evaluation_key(beta): CellSkill(brier=0.2, realized_term_baseline=0.9),
        },
    )
    assert [e.predictor_id for e in with_skill.entries] == ["alpha", "beta"]
    # …and it did land in the aggregates, so the test is not passing vacuously.
    assert with_skill.entries[0].forward is not None
    assert with_skill.entries[0].forward.population_realized_term_skill_score == pytest.approx(
        1 - 2.0
    )


def test_skill_components_scores_the_frozen_band_against_its_own_term(
    tmp_path: Path,
) -> None:
    """End to end over a fixture ledger, hand-computed.

    OT2025's `high` band is 32 weighted grants over 72 resolved; the scored case
    was granted, so its leave-one-out baseline is 31/71 and the baseline Brier
    it contributes is `(31/71 - 1)**2`. The prior-Term baseline rides in the
    same record, from the evaluator's own `segment_base_rate`.
    """
    ev = _evaluation(
        "alpha",
        brier_score=0.25,
        base_rate_basis="risk_set",
        segment_base_rate=0.4,
        brier_skill_score=1 - 0.25 / 0.36,
    )
    _write_cell(tmp_path, ev, context=_frozen_context())
    cells = iter_stratified_evaluations(tmp_path, frozen_only=False)
    (cell,) = skill_components(cells, tmp_path, _statpack()).values()
    assert cell.brier == pytest.approx(0.25)
    assert cell.prior_term_baseline == pytest.approx((0.4 - 1) ** 2)
    assert cell.realized_term_baseline == pytest.approx((31 / 71 - 1) ** 2)


def test_skill_components_omits_a_realized_baseline_it_cannot_pair(tmp_path: Path) -> None:
    """Four omissions, each visible rather than substituted.

    A non-cert cell has no salience band, so nothing to realize; a
    `terminal`-basis cell would need the band re-derived from the corpus row,
    which the committed ledger does not carry, so scoring it here would pair
    this number with a different band population than the prior-Term one beside
    it; a cell whose prediction froze no context has no band at all; and a pack
    carrying the Term under another salience version offers nothing the band
    name means anything under.
    """
    cert = _evaluation("alpha", event_id="evt-cert", base_rate_basis="risk_set")
    interim = _evaluation("alpha", event_id="evt-interim", base_rate_basis="risk_set")
    terminal = _evaluation("alpha", event_id="evt-terminal", base_rate_basis="terminal")
    contextless = _evaluation("alpha", event_id="evt-bare", base_rate_basis="risk_set")
    _write_cell(tmp_path, cert, context=_frozen_context())
    _write_cell(tmp_path, interim, context=_frozen_context(), stage=Stage.interim)
    _write_cell(tmp_path, terminal, context=_frozen_context())
    _write_cell(tmp_path, contextless, context=None)
    cells = iter_stratified_evaluations(tmp_path, frozen_only=False)

    def realized(pack: StatPack | None) -> set[str]:
        return {
            key[1]
            for key, cell in skill_components(cells, tmp_path, pack).items()
            if cell.realized_term_baseline is not None
        }

    assert realized(_statpack()) == {"evt-cert"}
    # A version the pack does not carry is the contracted `None`, not a blend.
    assert realized(_statpack(version="sal-v2")) == set()
    # No pack at all drops the column wholesale rather than half-computing it.
    assert realized(None) == set()


def test_a_cell_whose_recorded_skill_contradicts_its_inputs_is_omitted(tmp_path: Path) -> None:
    """`Evaluation` constrains no relation between its own numbers.

    The column's figure is computed from `segment_base_rate` and the realized
    outcome, so a record whose recorded `brier_skill_score` does not reproduce
    from its own inputs is dropped — visibly, in `skill_scored` — rather than
    published on a baseline it was never graded against. An evaluator that
    rounded its arithmetic still counts; a skill taken against another band
    does not.
    """
    # Outcome is granted, so the baseline Brier is (0.4 - 1)**2 = 0.36 and the
    # implied skill is 1 - 0.25/0.36 = 0.3056 — which 0.306 rounds to.
    rounded = _evaluation(
        "alpha",
        event_id="evt-rounded",
        brier_score=0.25,
        segment_base_rate=0.4,
        brier_skill_score=0.306,
    )
    contradictory = _evaluation(
        "alpha",
        event_id="evt-contradictory",
        brier_score=0.25,
        segment_base_rate=0.4,
        brier_skill_score=0.9,
    )
    _write_cell(tmp_path, rounded)
    _write_cell(tmp_path, contradictory)
    cells = iter_stratified_evaluations(tmp_path, frozen_only=False)
    scored = {
        key[1]: cell.prior_term_baseline
        for key, cell in skill_components(cells, tmp_path, None).items()
        if cell.prior_term_baseline is not None
    }
    assert scored == {"evt-rounded": pytest.approx(0.36)}


def test_skill_components_omits_a_band_under_the_minimum(tmp_path: Path) -> None:
    # The floor is on the leave-one-out denominator: 30 resolved leaves 29 and
    # publishes nothing, 31 leaves the stated minimum and publishes.
    ev = _evaluation("alpha", brier_score=0.25, base_rate_basis="risk_set")
    _write_cell(tmp_path, ev, context=_frozen_context())
    cells = iter_stratified_evaluations(tmp_path, frozen_only=False)

    def realized(pack: StatPack) -> float | None:
        # Absent from the map entirely when neither column scores the cell (the
        # fixture records no `segment_base_rate`, so there is no prior baseline).
        cell = skill_components(cells, tmp_path, pack).get(_evaluation_key(ev))
        return cell.realized_term_baseline if cell is not None else None

    assert realized(_statpack(resolved=30, grants=10)) is None
    assert realized(_statpack(resolved=31, grants=10)) is not None


def test_the_cli_scores_the_realized_column_from_the_committed_pack(tmp_path: Path) -> None:
    """The wiring the workflow actually runs, end to end.

    The command reads `<metrics_root>/statpack.json`, so the column is populated
    with a pack in place and absent without one — and a missing pack says so on
    stderr rather than rendering as a computed zero.
    """
    data_root, metrics_root = tmp_path / "data", tmp_path / "metrics"
    ev = _evaluation("alpha", brier_score=0.25, base_rate_basis="risk_set")
    _write_cell(data_root, ev, context=_frozen_context())
    env = {"FEDCOURTS_DATA_ROOT": str(data_root), "FEDCOURTS_METRICS_ROOT": str(metrics_root)}
    out = tmp_path / "leaderboard.json"
    argv = ["leaderboard", "--out", str(out), "--all-versions"]

    no_pack = runner.invoke(app, argv, env=env)
    assert no_pack.exit_code == 0, no_pack.output
    assert "no readable metrics/statpack.json" in no_pack.output
    forward = read_model(out, Leaderboard).entries[0].forward
    assert forward is not None
    assert forward.realized_term_skill_scored == 0
    assert forward.population_realized_term_skill_score is None

    write_json(metrics_root / "statpack.json", _statpack())
    with_pack = runner.invoke(app, argv, env=env)
    assert with_pack.exit_code == 0, with_pack.output
    assert "no readable metrics/statpack.json" not in with_pack.output
    forward = read_model(out, Leaderboard).entries[0].forward
    assert forward is not None
    assert forward.realized_term_skill_scored == 1
    assert forward.population_realized_term_skill_score == pytest.approx(
        1 - 0.25 / (1 - 31 / 71) ** 2
    )


def test_the_committed_leaderboard_round_trips_byte_for_byte(tmp_path: Path) -> None:
    """Byte-identity regression on the committed artifact: parsing
    `metrics/leaderboard.json` under the current schema and re-serializing it
    through `serialize.write_json` (how the metrics refresh writes it)
    reproduces the committed bytes exactly — so this change requires no
    regeneration of the committed board (the empty `stages` axis is omitted,
    and `skill_scored` appears only in strata the new code builds). The board
    carries no generated-at/timestamp field by contract (the `Leaderboard`
    docstring — the same ledger must always serialize identically), so no
    field needs normalizing before the comparison.

    Deliberately *not* a rebuild from the committed `data/` tree: evaluations
    land on `main` via collect PRs on a different cadence than the metrics
    refresh regenerates this file, so a rebuild comparison would redden the
    path-jailed collect PR that lands the first frozen evaluation. The
    round-trip binds only the artifact to its own schema, which travels in the
    same PR as any schema change — the drift this test exists to catch.
    """
    repo_root = Path(__file__).resolve().parents[1]
    committed = repo_root / "metrics" / "leaderboard.json"
    board = read_model(committed, Leaderboard)
    rewritten = tmp_path / "leaderboard.json"
    write_json(rewritten, board)
    assert rewritten.read_bytes() == committed.read_bytes()


# --- big-case rank-agreement (Kendall's tau-b) -------------------------------------


def testkendall_tau_b_perfect_and_reversed_and_ties() -> None:
    assert kendall_tau_b([(1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]) == 1.0  # concordant
    assert kendall_tau_b([(1.0, 3.0), (2.0, 2.0), (3.0, 1.0)]) == -1.0  # reversed
    assert kendall_tau_b([(1.0, 1.0)]) is None  # need >= 2 points
    assert kendall_tau_b([(1.0, 1.0), (1.0, 1.0)]) is None  # every pair ties → undefined
    # A monotone set with one x-tie: tau-b's denominator drops the tied pair.
    tau = kendall_tau_b([(1.0, 1.0), (2.0, 2.0), (2.0, 3.0)])
    assert tau is not None and tau == pytest.approx(2 / (6**0.5))


def _write_big_case_cell(
    data_root: Path,
    predictor_id: str,
    case_id: str,
    *,
    pred_score: float | None,
    eval_scores: list[float],
) -> None:
    court, _, docket = case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event("evt-petition-disposition")
    write_json(
        event.prediction(predictor_id, "p1"),
        Prediction(
            case_id=case_id,
            event_id="evt-petition-disposition",
            predictor_id=predictor_id,
            engine=Engine.claude_code,
            run_id="p1",
            created_at=datetime(2026, 6, 20, tzinfo=UTC),
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
            big_case_score=pred_score,
        ),
    )
    for i, score in enumerate(eval_scores):
        write_json(
            event.evaluation(f"eval-{i}", predictor_id, "r1"),
            Evaluation(
                case_id=case_id,
                event_id="evt-petition-disposition",
                predictor_id=predictor_id,
                evaluator_id=f"eval-{i}",
                engine=Engine.claude_code,
                run_id="r1",
                created_at=datetime(2026, 6, 24, tzinfo=UTC),
                correct=1,
                big_case=BigCaseAssessment(evaluator_score=score),
            ),
        )
    write_json(
        event.outcome,
        Outcome(
            case_id=case_id,
            event_id="evt-petition-disposition",
            resolved_at=date(2026, 6, 23),
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )


def test_big_case_agreement_correlates_predictor_and_panel_orderings(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    # A predictor whose stakes ordering matches the panel's → tau +1.
    _write_big_case_cell(data_root, "agree", "scotus/1", pred_score=0.9, eval_scores=[0.8])
    _write_big_case_cell(data_root, "agree", "scotus/2", pred_score=0.5, eval_scores=[0.55])
    _write_big_case_cell(data_root, "agree", "scotus/3", pred_score=0.1, eval_scores=[0.2])
    # A predictor whose ordering is reversed vs the panel → tau -1.
    _write_big_case_cell(data_root, "invert", "scotus/4", pred_score=0.9, eval_scores=[0.1])
    _write_big_case_cell(data_root, "invert", "scotus/5", pred_score=0.5, eval_scores=[0.5])
    _write_big_case_cell(data_root, "invert", "scotus/6", pred_score=0.1, eval_scores=[0.9])

    result = big_case_agreement(data_root, frozen_only=False)

    assert result["agree"].rank_agreement == 1.0
    assert result["agree"].cases == 3
    assert result["invert"].rank_agreement == -1.0


def test_big_case_agreement_averages_the_evaluator_panel(tmp_path: Path) -> None:
    # Two evaluators disagree on one case; the panel mean is what the predictor's
    # score is correlated against.
    data_root = tmp_path / "data"
    _write_big_case_cell(data_root, "p", "scotus/1", pred_score=0.9, eval_scores=[0.2, 1.0])
    _write_big_case_cell(data_root, "p", "scotus/2", pred_score=0.1, eval_scores=[0.1, 0.1])
    result = big_case_agreement(data_root, frozen_only=False)
    # case1 panel mean = 0.6 > case2's 0.1, and pred 0.9 > 0.1 → concordant → +1.
    assert result["p"].rank_agreement == 1.0
    assert result["p"].cases == 2


def test_big_case_agreement_uses_the_latest_prediction_score(tmp_path: Path) -> None:
    # The latest prediction's score wins. Latest scores (0.1, 0.9) are concordant
    # with the panel (0.2, 0.8) → +1. A stale earlier score of 0.9 on case 1, if
    # used, would tie the x-axis with case 2 → undefined (None). So +1 proves the
    # recency latch.
    data_root = tmp_path / "data"
    _write_big_case_cell(data_root, "p", "scotus/1", pred_score=0.1, eval_scores=[0.2])
    _write_big_case_cell(data_root, "p", "scotus/2", pred_score=0.9, eval_scores=[0.8])
    stale = CasePaths(data_root, "scotus", 1).event("evt-petition-disposition")
    write_json(
        stale.prediction("p", "p0"),
        Prediction(
            case_id="scotus/1",
            event_id="evt-petition-disposition",
            predictor_id="p",
            engine=Engine.claude_code,
            run_id="p0",
            created_at=datetime(2026, 6, 1, tzinfo=UTC),  # earlier than the p1 run
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
            big_case_score=0.9,
        ),
    )
    result = big_case_agreement(data_root, frozen_only=False)
    assert result["p"].rank_agreement == 1.0
    assert result["p"].cases == 2


def test_big_case_agreement_single_case_reports_null_agreement(tmp_path: Path) -> None:
    # One comparable case: the block is present (cases=1) but the rank correlation
    # is undefined with a single point — distinct from the absent-from-map case.
    data_root = tmp_path / "data"
    _write_big_case_cell(data_root, "p", "scotus/1", pred_score=0.5, eval_scores=[0.5])
    entry = big_case_agreement(data_root, frozen_only=False)["p"]
    assert entry.cases == 1
    assert entry.rank_agreement is None


def test_big_case_agreement_skips_a_predictor_without_a_score(tmp_path: Path) -> None:
    # An evaluator gave a read but the predictor emitted no big_case_score → the
    # case is not comparable, so the predictor is absent from the map.
    data_root = tmp_path / "data"
    _write_big_case_cell(data_root, "p", "scotus/1", pred_score=None, eval_scores=[0.5])
    assert big_case_agreement(data_root, frozen_only=False) == {}


def test_big_case_agreement_empty_when_no_ledger(tmp_path: Path) -> None:
    assert big_case_agreement(tmp_path / "nope") == {}


def test_build_leaderboard_attaches_big_case_when_supplied() -> None:
    ev = _evaluation("p1")
    board = build_leaderboard(
        [_forward(ev)], big_case={"p1": BigCaseLeaderboard(rank_agreement=0.5, cases=4)}
    )
    assert board.entries[0].big_case is not None
    assert board.entries[0].big_case.rank_agreement == 0.5
    # Without the map the dimension is simply null (backward-compatible).
    assert build_leaderboard([_forward(ev)]).entries[0].big_case is None


def _frozen_stamp(digest: str = "sha256:blessed") -> ProcessVersion:
    return ProcessVersion(
        label="proc-v1", digest=digest, stamped_at=datetime(2026, 1, 1, tzinfo=UTC)
    )


def test_frozen_leaderboard_excludes_unstamped_shakedown_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The headline: a shakedown cell (no stamp) is out of the frozen board, a
    blessed-process cell is in. Same ledger, two scopes."""
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    data_root = tmp_path / "data"
    _write_cell(data_root, _evaluation("shakedown", event_id="evt-a"), process_version=None)
    _write_cell(data_root, _evaluation("frozen", event_id="evt-b"), process_version=_frozen_stamp())

    frozen = build_leaderboard(iter_stratified_evaluations(data_root))
    assert [e.predictor_id for e in frozen.entries] == ["frozen"]

    all_versions = build_leaderboard(
        iter_stratified_evaluations(data_root, frozen_only=False), process_scope="all"
    )
    assert {e.predictor_id for e in all_versions.entries} == {"shakedown", "frozen"}


def test_a_cell_stamped_with_an_unblessed_digest_is_not_frozen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Stamped is not enough — the digest must be blessed. A process that drifted
    under the same label carries a different digest and stays out of the headline."""
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    data_root = tmp_path / "data"
    _write_cell(
        data_root,
        _evaluation("drifted", event_id="evt-a"),
        process_version=_frozen_stamp("sha256:drifted"),
    )
    assert iter_stratified_evaluations(data_root) == []


def test_the_default_frozen_board_is_empty_during_shakedown(tmp_path: Path) -> None:
    """With no digest blessed (the shipped state), the frozen headline is empty
    even over a full stamped-nowhere ledger — the honest 'nothing frozen yet'."""
    data_root = tmp_path / "data"
    _write_cell(data_root, _evaluation("alpha", event_id="evt-a"))
    board = build_leaderboard(iter_stratified_evaluations(data_root))
    assert board.predictors_ranked == 0
    assert board.process_scope == "frozen"


def test_big_case_agreement_defaults_to_frozen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The big-case section must not show a shakedown read beside a frozen board."""
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    data_root = tmp_path / "data"
    _write_big_case_cell(data_root, "shakedown", "scotus/1", pred_score=0.5, eval_scores=[0.6, 0.4])
    # Frozen default: the unstamped shakedown read is excluded.
    assert big_case_agreement(data_root) == {}
    # All-versions still sees it.
    assert "shakedown" in big_case_agreement(data_root, frozen_only=False)


def _big_case_cell(
    data_root: Path, *, case: str, evaluator: str, score: float, predictor: str = "p-a"
) -> None:
    """One evaluator's big-case read on one case, with the cell it targets."""
    _write_cell(
        data_root,
        _evaluation(
            predictor,
            case_id=case,
            evaluator_id=evaluator,
            big_case=BigCaseAssessment(evaluator_score=score),
        ),
        process_version=_frozen_stamp(),
    )


def test_evaluator_agreement_is_positive_when_the_panel_orders_alike(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    root = tmp_path / "data"
    for case, (a, b, c) in {
        "ca9/1": (0.9, 0.8, 0.85),
        "ca9/2": (0.5, 0.6, 0.55),
        "ca9/3": (0.1, 0.2, 0.15),
    }.items():
        _big_case_cell(root, case=case, evaluator="eval-a", score=a)
        _big_case_cell(root, case=case, evaluator="eval-b", score=b)
        _big_case_cell(root, case=case, evaluator="eval-c", score=c)
    agreement = evaluator_agreement(root)
    assert set(agreement) == {"eval-a", "eval-b", "eval-c"}
    assert all(v.events == 3 for v in agreement.values())
    assert all(v.rank_agreement == 1.0 for v in agreement.values())


def test_one_inverting_grader_drags_the_whole_small_panel_negative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A property of the measure worth knowing before reading it.

    Leave-one-out means each grader is scored against the *mean* of the others, so
    on a three-judge panel one inverting grader sits in both peers' comparison and
    can turn them negative — the two who agree with each other still post negative
    agreement. That is not a bug in the statistic, it is what a panel this small
    supports: with three judges there is no majority to be an outlier against.

    So a negative figure identifies a *disagreement in the panel*, not a
    disagreement by the grader carrying it. Read the whole map, not one row, and
    read it beside `events`.
    """
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    root = tmp_path / "data"
    for case, (a, b, c) in {
        "ca9/1": (0.9, 0.8, 0.1),
        "ca9/2": (0.5, 0.6, 0.5),
        "ca9/3": (0.1, 0.2, 0.9),
    }.items():
        _big_case_cell(root, case=case, evaluator="eval-a", score=a)
        _big_case_cell(root, case=case, evaluator="eval-b", score=b)
        _big_case_cell(root, case=case, evaluator="eval-c", score=c)
    agreement = evaluator_agreement(root)
    # The inverter reads fully reversed, which is the signal.
    assert agreement["eval-c"].rank_agreement == -1.0
    # But so does a grader that agreed with a peer, because the peer mean it is
    # scored against contains the inverter.
    assert agreement["eval-a"].rank_agreement is not None
    assert agreement["eval-a"].rank_agreement < 0
    # And the third reads *undefined*: averaging the aligned grader against the
    # inverter leaves a flat peer series with no ordering to correlate against,
    # so the answer is silence rather than a fabricated zero.
    assert agreement["eval-b"].rank_agreement is None
    assert agreement["eval-b"].events == 3


def test_an_evaluator_is_never_scored_against_a_panel_containing_itself(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    """Leave-one-out is the whole design. With a panel of two, a self-inclusive
    mean would correlate each grader half with itself, so two graders who disagree
    completely would still post positive agreement. They must post -1.
    """
    root = tmp_path / "data"
    for case, (a, b) in {"ca9/1": (0.9, 0.1), "ca9/2": (0.1, 0.9)}.items():
        _big_case_cell(root, case=case, evaluator="eval-a", score=a)
        _big_case_cell(root, case=case, evaluator="eval-b", score=b)
    agreement = evaluator_agreement(root)
    assert agreement["eval-a"].rank_agreement == -1.0
    assert agreement["eval-b"].rank_agreement == -1.0


def test_an_event_only_one_evaluator_read_contributes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pv, "FROZEN_PROCESS_DIGESTS", frozenset({"sha256:blessed"}))
    # Agreement needs a peer. A solo read is not a disagreement, and counting it
    # would let a single-grader event dilute the correlation toward zero.
    root = tmp_path / "data"
    _big_case_cell(root, case="ca9/1", evaluator="eval-a", score=0.9)
    _big_case_cell(root, case="ca9/2", evaluator="eval-a", score=0.2)
    _big_case_cell(root, case="ca9/2", evaluator="eval-b", score=0.3)
    agreement = evaluator_agreement(root)
    assert agreement["eval-a"].events == 1  # only ca9/2 had a peer
    # One shared event cannot support a correlation.
    assert agreement["eval-a"].rank_agreement is None


def test_evaluator_agreement_honours_the_frozen_partition(tmp_path: Path) -> None:
    # Same partition as the predictor-side view, keyed on the prediction's stamp,
    # so the two agreement blocks always describe the same cells.
    root = tmp_path / "data"
    for case in ("ca9/1", "ca9/2"):
        for ev, score in (("eval-a", 0.9), ("eval-b", 0.8)):
            _write_cell(
                root,
                _evaluation(
                    "p-a",
                    case_id=case,
                    evaluator_id=ev,
                    big_case=BigCaseAssessment(evaluator_score=score),
                ),
                process_version=None,  # shakedown
            )
    assert evaluator_agreement(root, frozen_only=True) == {}
    assert evaluator_agreement(root, frozen_only=False) != {}


def test_the_board_names_every_gate_version_its_cells_were_scored_under() -> None:
    """The gate partitions the population, and no digest records that it moved.

    A process change moves a digest and the frozen filter sees it. A salience
    change does not move anything — it just hands the tournament a different set
    of petitions — so the only way a reader can tell that a board spans two
    gated populations is if the board says so.
    """
    cells = [
        _forward(_evaluation("p1", base_rate_salience_version="sal-v1")),
        _forward(_evaluation("p1", base_rate_salience_version="sal-v2")),
        _forward(_evaluation("p2", base_rate_salience_version="sal-v1")),
        _forward(_evaluation("p2")),  # no basis recorded -> no version to report
    ]
    board = build_leaderboard(cells)
    assert board.salience_versions == ["sal-v1", "sal-v2"]  # sorted, deduped, nulls dropped


def test_a_board_with_no_banded_baseline_names_no_gate_version() -> None:
    """Empty, not a fabricated default — a merits cell has no scorer to pin."""
    board = build_leaderboard([_forward(_evaluation("p1"))])
    assert board.salience_versions == []


def test_two_moments_of_one_stage_never_share_a_block() -> None:
    """Two moments are two populations, so they must not share a mean.

    The later moment answers the same question with strictly more evidence, so
    pooling them would publish a figure over a mixture of information sets —
    the error the stage axis, the salience version and the claim-set version
    each already refuse on their own axis.
    """
    board = build_leaderboard(
        [
            _forward(_evaluation("a", correct=1, brier_score=0.1)),  # cert@distribution
            _forward(_evaluation("a", correct=0, brier_score=0.9), moment=Moment.cvsg),
            _forward(_evaluation("a", correct=1, brier_score=0.2), stage=Stage.merits),
            _forward(
                _evaluation("a", correct=1, brier_score=0.3),
                stage=Stage.merits,
                moment=Moment.briefed,
            ),
        ]
    )
    # Only cert's first moment ranks; every later moment reports unranked.
    assert board.evaluations_total == 1
    assert set(board.stages) == {"cert@cvsg", "merits@grant", "merits@briefed"}
    # And the two merits moments keep separate figures rather than averaging.
    assert board.stages["merits@grant"].evaluations_total == 1
    assert board.stages["merits@briefed"].evaluations_total == 1


def test_a_stage_with_no_recorded_moment_keys_bare() -> None:
    """Honest rather than guessed: "stage known, moment not" is its own block."""
    board = build_leaderboard([_forward(_evaluation("a"), stage=Stage.interim, moment=None)])
    assert set(board.stages) == {"interim"}


def test_big_case_agreement_counts_cases_not_events(tmp_path: Path) -> None:
    """Stakes are a property of the case, so its moments contribute one point.

    Two moments would otherwise put two *non-independent* observations into a
    rank correlation that assumes independence, and `cases` would be counting
    events while calling them cases.
    """
    moments_read = (("evt-petition-disposition", 0.8, 0.7), ("evt-order-judgment", 0.6, 0.5))
    for event_id, own, panel in moments_read:
        _write_cell(
            tmp_path,
            _evaluation("p", event_id=event_id, big_case=BigCaseAssessment(evaluator_score=panel)),
            big_case_score=own,
        )
    ((predictor, agreement),) = big_case_agreement(tmp_path, frozen_only=False).items()
    assert predictor == "p"
    assert agreement.cases == 1  # one case, two moments
