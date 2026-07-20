"""Leaderboard aggregation and stratification over a small fixture ledger."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version as pv
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import (
    FORWARD,
    PROCEDURAL,
    RETROSPECTIVE,
    Stratum,
    _kendall_tau_b,
    big_case_agreement,
    build_leaderboard,
    classify_stratum,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    BigCaseAssessment,
    BigCaseLeaderboard,
    Disposition,
    Engine,
    Evaluation,
    Leaderboard,
    Outcome,
    Prediction,
    ProcessVersion,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import iter_evaluations, iter_stratified_evaluations

runner = CliRunner()


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


def _forward(ev: Evaluation) -> tuple[Evaluation, Stratum]:
    return (ev, FORWARD)


def _retro(ev: Evaluation) -> tuple[Evaluation, Stratum]:
    return (ev, RETROSPECTIVE)


def _write(data_root: Path, ev: Evaluation) -> None:
    court, _, docket = ev.case_id.partition("/")
    path = (
        CasePaths(data_root, court, int(docket))
        .event(ev.event_id)
        .evaluation(ev.evaluator_id, ev.predictor_id, ev.run_id)
    )
    write_json(path, ev)


def _write_cell(
    data_root: Path,
    ev: Evaluation,
    *,
    predicted_at: datetime = datetime(2026, 6, 20, tzinfo=UTC),
    resolved_at: date = date(2026, 6, 23),
    disposition_basis: str = "standard",
    process_version: ProcessVersion | None = None,
) -> None:
    """A full scored cell: evaluation plus the prediction and outcome it targets.

    ``process_version`` stamps the prediction, which is what the frozen filter
    partitions on; ``None`` leaves it a shakedown cell.
    """
    _write(data_root, ev)
    court, _, docket = ev.case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(ev.event_id)
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
            process_version=process_version,
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
    assert stratum.mean_brier_skill_score is None


def test_brier_skill_score_aggregates_over_present_cells() -> None:
    # The skill column averages only reported cells and admits negative skill
    # (a forecast worse than the segment base rate).
    cells = [
        _forward(_evaluation("alpha", brier_skill_score=0.4)),
        _forward(_evaluation("alpha", brier_skill_score=-0.2)),
        _forward(_evaluation("alpha", brier_skill_score=None)),  # skipped, not zero
    ]
    stratum = build_leaderboard(cells).entries[0].forward
    assert stratum is not None
    assert stratum.mean_brier_skill_score == pytest.approx(0.1)


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
        for ev, stratum in iter_stratified_evaluations(tmp_path, frozen_only=False)
    }
    assert strata == {"evt-a": FORWARD, "evt-b": RETROSPECTIVE}


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
    ((_, stratum),) = iter_stratified_evaluations(tmp_path, frozen_only=False)
    assert stratum == PROCEDURAL


def test_procedural_cells_aggregate_separately_and_never_rank(tmp_path: Path) -> None:
    # Predictor A: one real forward win. Predictor B: a perfect score that is
    # purely procedural. A must outrank B — procedural accuracy buys no rank —
    # and the totals must report the segmentation.
    board = build_leaderboard(
        [
            (_evaluation("a", correct=1, brier_score=0.1), FORWARD),
            (_evaluation("b", correct=1, brier_score=0.0), PROCEDURAL),
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


# --- big-case rank-agreement (Kendall's tau-b) -------------------------------------


def test_kendall_tau_b_perfect_and_reversed_and_ties() -> None:
    assert _kendall_tau_b([(1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]) == 1.0  # concordant
    assert _kendall_tau_b([(1.0, 3.0), (2.0, 2.0), (3.0, 1.0)]) == -1.0  # reversed
    assert _kendall_tau_b([(1.0, 1.0)]) is None  # need >= 2 points
    assert _kendall_tau_b([(1.0, 1.0), (1.0, 1.0)]) is None  # every pair ties → undefined
    # A monotone set with one x-tie: tau-b's denominator drops the tied pair.
    tau = _kendall_tau_b([(1.0, 1.0), (2.0, 2.0), (2.0, 3.0)])
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
