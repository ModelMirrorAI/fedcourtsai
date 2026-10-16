"""The run-timing reading of an increment claim: the scorer's mask and the boards' set-aside.

An increment claim forecasts a docket signal the cell's provisioned record did
not show. :func:`fedcourtsai.set_aside.increment_timing` says whether the signal
was already on the docket when the forward cell ran; ``score_claims`` masks the
claims it reads ``signal-before-run`` and the claim-score board sets aside the
ones it reads ``signal-on-run-day``, with a per-reason sensitivity line.
"""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from types import ModuleType

import pytest

from fedcourtsai import corpus
from fedcourtsai.claim_metrics import (
    ClaimSetAsides,
    build_claim_scores,
    claim_set_aside_record,
    claim_set_aside_sensitivity_lines,
    without_set_aside_claims,
)
from fedcourtsai.integrity import FORWARD, StratifiedCell
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import claims
from fedcourtsai.schemas import (
    ClaimProbability,
    ClaimScore,
    ClaimScoreBlock,
    DocketPollRecord,
    Engine,
    EventKind,
    ModelUsage,
    Moment,
    Outcome,
    PolledIncrementSignals,
    PolledSignal,
    PredictableEvent,
    Prediction,
    PredictionContext,
    Stage,
    StatPack,
    UsageRole,
)
from fedcourtsai.serialize import write_json, write_yaml
from fedcourtsai.set_aside import (
    TIMED_INCREMENT_CLAIMS,
    claim_set_aside_reason,
    increment_timing,
)
from fedcourtsai.store import increment_signal_day, stratify
from tests.conftest import FixtureCorpus, frozen_stamp
from tests.test_claim_metrics import _evaluation as _claim_evaluation
from tests.test_leaderboard import _evaluation, _write_cell

APPLICATION = "scotus/9526000416"
MOTION = "evt-motion-disposition"
#: 2026-09-29 21:29Z: the 26A416 arrival cell's run, 17:29 in Court time.
RUN = datetime(2026, 9, 29, 21, 29, tzinfo=UTC)


def _prediction(*, at: datetime = RUN, mode: str = "forward") -> Prediction:
    return Prediction(
        case_id=APPLICATION,
        event_id=MOTION,
        predictor_id="claude-baseline",
        engine=Engine.claude_code,
        run_id="p1",
        created_at=at,
        input_snapshot="corpus",
        granted=0,
        probability=0.2,
        predicted_disposition="denied",
        context=PredictionContext(
            mode=mode,
            snapshot_date=date(2026, 9, 28),
            signals_observable=True,
            response_requested=False,
            referred_to_court=False,
            amicus_briefs=0,
        ),
        claims=[
            ClaimProbability(claim_id="interim-disposition", probability=0.2),
            ClaimProbability(claim_id="response-requested-increment", probability=0.98),
            ClaimProbability(claim_id="referral-increment", probability=0.94),
            ClaimProbability(claim_id="amicus-increment", probability=0.5),
        ],
    )


def _poll(
    *, state: str = "open", requested: bool | None = None, referred: bool | None = None
) -> DocketPollRecord:
    signals = None
    if requested is not None or referred is not None:
        signals = PolledIncrementSignals(
            response_requested=PolledSignal(present=requested, entry_date=date(2026, 9, 28))
            if requested is not None
            else None,
            referred_to_court=PolledSignal(present=referred) if referred is not None else None,
        )
    return DocketPollRecord(
        polled_at=datetime(2026, 9, 29, 21, 20, tzinfo=UTC),
        docket_number="26A416",
        state=state,
        signals=signals,
    )


def _day(value: date | None) -> Callable[[], date | None]:
    return lambda: value


# --- the timing reading ---------------------------------------------------------


@pytest.mark.parametrize(
    ("poll", "signal", "expected"),
    [
        # 26A416: requested 09-28, run 09-29, unpolled.
        (None, date(2026, 9, 28), "signal-before-run"),
        # 26A446: requested the run day, unpolled — nothing orders the two.
        (None, date(2026, 9, 29), "signal-on-run-day"),
        # After the run: a forecast.
        (None, date(2026, 9, 30), None),
        # No committed date: unassessable, so left as the record resolves it.
        (None, None, None),
        # A usable poll decides whatever the date says.
        (_poll(requested=True), date(2026, 9, 29), "signal-before-run"),
        (_poll(requested=False), date(2026, 9, 29), None),
        (_poll(requested=False), date(2026, 9, 28), None),
        # A poll that read no signals, or could not answer, falls back to the date.
        (_poll(), date(2026, 9, 29), "signal-on-run-day"),
        (_poll(state="unavailable", requested=True), date(2026, 9, 28), "signal-before-run"),
    ],
)
def test_increment_timing_reads_the_poll_first_then_the_date(
    poll: DocketPollRecord | None, signal: date | None, expected: str | None
) -> None:
    timing = increment_timing("response-requested-increment", _prediction(), poll, _day(signal))
    assert timing == expected


def test_the_run_day_is_read_in_court_time() -> None:
    # 01:42Z on 09-01 is the evening of 08-31 in Court time (26A275): a request
    # dated 09-01 came after the run, not on its day.
    at = datetime(2026, 9, 1, 1, 42, tzinfo=UTC)
    timing = increment_timing(
        "response-requested-increment", _prediction(at=at), None, _day(date(2026, 9, 1))
    )
    assert timing is None


def test_only_a_forward_cells_timed_increment_claims_are_read() -> None:
    def unasked() -> date | None:
        raise AssertionError("the signal date is read only for a timed forward claim")

    assert increment_timing("amicus-increment", _prediction(), None, unasked) is None
    assert increment_timing("interim-disposition", _prediction(), None, unasked) is None
    replay = _prediction(mode="replay")
    assert increment_timing("response-requested-increment", replay, None, unasked) is None


def test_the_referral_reads_its_own_poll_field() -> None:
    poll = _poll(requested=False, referred=True)
    assert increment_timing("referral-increment", _prediction(), poll, _day(None)) == (
        "signal-before-run"
    )
    assert increment_timing("response-requested-increment", _prediction(), poll, _day(None)) is None


def test_the_timed_claims_are_the_scorers_increment_claims_and_the_polls_fields() -> None:
    assert set(TIMED_INCREMENT_CLAIMS) == {
        claims.CLAIM_RESPONSE_REQUESTED_INCREMENT,
        claims.CLAIM_REFERRAL_INCREMENT,
        claims.CLAIM_CVSG_INCREMENT,
    }
    assert set(TIMED_INCREMENT_CLAIMS.values()) == set(PolledIncrementSignals.model_fields)


def test_a_claim_is_set_aside_only_when_resolved_and_on_the_run_day() -> None:
    same_day = _day(date(2026, 9, 29))
    claim = "response-requested-increment"
    assert claim_set_aside_reason(claim, 1, _prediction(), None, same_day) == "increment-run-day"
    assert claim_set_aside_reason(claim, None, _prediction(), None, same_day) is None
    before = _day(date(2026, 9, 28))
    assert claim_set_aside_reason(claim, 1, _prediction(), None, before) is None


# --- the scorer's mask ----------------------------------------------------------


def _interim_outcome() -> Outcome:
    return Outcome.model_validate(
        dict(
            case_id=APPLICATION,
            event_id=MOTION,
            resolved_at=date(2026, 10, 9),
            actual_disposition="denied",
            actual_granted=0,
            interim_signals=dict(response_requested=True, referred_to_court=True, amicus_briefs=2),
        )
    )


def _score(timing: Callable[[str], str | None] | None) -> dict[str, ClaimScore]:
    block = claims.score_claims(
        _prediction(),
        _interim_outcome(),
        StatPack.model_validate({"terms": []}),
        lookback_terms=3,
        increment_timing=timing,  # type: ignore[arg-type]
    )
    assert block is not None
    return {row.claim_id: row for row in block.claims}


def test_score_claims_masks_a_claim_whose_signal_preceded_the_run() -> None:
    rows = _score(
        lambda claim_id: (
            "signal-before-run"
            if claim_id == "response-requested-increment"
            else "signal-on-run-day"
        )
    )
    masked = rows["response-requested-increment"]
    assert masked.outcome is None and masked.mask_reason == "signal-before-run"
    # A run-day reading is the boards' to set aside, not the scorer's to mask.
    referral = rows["referral-increment"]
    assert referral.outcome == 1 and referral.mask_reason is None
    assert "mask_reason" not in referral.model_dump(mode="json")
    assert masked.model_dump(mode="json")["mask_reason"] == "signal-before-run"


def test_score_claims_without_a_timing_reading_resolves_as_before() -> None:
    rows = _score(None)
    assert rows["response-requested-increment"].outcome == 1
    assert rows["referral-increment"].outcome == 1


# --- the committed signal date ----------------------------------------------------


def test_the_signal_day_is_read_from_the_committed_ledger(tmp_path: Path) -> None:
    case = CasePaths(tmp_path, "scotus", 9526000416)
    write_yaml(
        case.event("evt-order-response-requested-disposition").event_file,
        PredictableEvent(
            event_id="evt-order-response-requested-disposition",
            case_id=APPLICATION,
            kind=EventKind.order,
            stage=Stage.interim,
            moment=Moment.response_requested,
            opened_at=date(2026, 9, 28),
            title="Test event",
        ),
    )
    event_dir = case.event(MOTION).base
    assert increment_signal_day(event_dir, "response-requested-increment", None) == date(
        2026, 9, 28
    )
    # No committed artifact dates a referral.
    assert increment_signal_day(event_dir, "referral-increment", _interim_outcome()) is None
    outcome = Outcome.model_validate(
        dict(
            case_id="scotus/26221",
            event_id="evt-petition-disposition",
            resolved_at=date(2026, 12, 1),
            actual_disposition="denied",
            actual_granted=0,
            signals=dict(distribution_count=2, cvsg_date=date(2026, 10, 13)),
        )
    )
    assert increment_signal_day(event_dir, "cvsg-increment", outcome) == date(2026, 10, 13)
    # An unminted response-requested moment leaves the date unknown.
    other = CasePaths(tmp_path, "scotus", 9526000500).event(MOTION).base
    assert increment_signal_day(other, "response-requested-increment", None) is None


# --- the board's claim-grain set-aside --------------------------------------------


def _cvsg_block(*, cvsg_score: float | None) -> ClaimScoreBlock:
    rows = [
        ClaimScore(claim_id="disposition", probability=0.3, baseline=0.1, outcome=0, score=-0.08),
        ClaimScore(
            claim_id="cvsg-increment",
            probability=0.2,
            baseline=0.1 if cvsg_score is not None else None,
            outcome=1,
            score=cvsg_score,
        ),
    ]
    total = sum(row.score for row in rows if row.score is not None)
    return ClaimScoreBlock(
        declared_set_version="cert-v2", claims=rows, total=total, floor=0.0, lift=total
    )


def _cert_cell(event_id: str, block: ClaimScoreBlock) -> StratifiedCell:
    ev = _claim_evaluation("alpha", event_id=event_id, claim_scores=block)
    return (ev, FORWARD, Stage.cert, Moment.distribution)


def test_the_default_takes_a_set_aside_claims_score_out_and_its_line_counts_it_back() -> None:
    kept = _cert_cell("evt-a", _cvsg_block(cvsg_score=None))
    held = _cert_cell("evt-b", _cvsg_block(cvsg_score=0.17))
    cells = [kept, held]
    key = (held[0].case_id, held[0].event_id, "alpha", "eval-a", "r1")
    claim_set_aside: ClaimSetAsides = {key: {"cvsg-increment": "increment-run-day"}}

    default = build_claim_scores(without_set_aside_claims(cells, claim_set_aside))
    entry = default.entries[0].forward
    assert entry is not None
    per_claim = {row.claim_id: row for row in entry.claims}
    assert per_claim["cvsg-increment"].scored == 0
    assert entry.mean_total == pytest.approx(-0.08)

    record = claim_set_aside_record(cells, claim_set_aside)
    assert record is not None
    assert (record.claims, record.scored_claims, record.gradings) == (1, 1, 1)
    assert record.by_reason == {"increment-run-day": 1}
    assert record.by_claim == {"cvsg-increment": 1}
    assert record.events == ["scotus/123 evt-b cvsg-increment increment-run-day"]

    (line,) = claim_set_aside_sensitivity_lines(cells, claim_set_aside, build_claim_scores)
    assert (line.reason, line.predictor_id, line.stratum, line.claims) == (
        "increment-run-day",
        "alpha",
        "forward",
        1,
    )
    assert line.including is not None
    counted = {row.claim_id: row for row in line.including.claims}
    assert counted["cvsg-increment"].scored == 1
    assert line.including.mean_total == pytest.approx((-0.08 + (-0.08 + 0.17)) / 2)


def test_nothing_set_aside_at_the_claim_grain_publishes_nothing() -> None:
    cells = [_cert_cell("evt-a", _cvsg_block(cvsg_score=0.17))]
    assert claim_set_aside_record(cells, {}) is None
    assert claim_set_aside_sensitivity_lines(cells, {}, build_claim_scores) == []
    assert without_set_aside_claims(cells, {}) == cells


def _write_cvsg_cell(data_root: Path, *, cvsg_date: date, poll: DocketPollRecord | None) -> None:
    ev = _evaluation(
        "claude-baseline",
        case_id="scotus/9026000221",
        event_id="evt-petition-disposition",
        claim_scores=_cvsg_block(cvsg_score=None),
    )
    _write_cell(
        data_root,
        ev,
        predicted_at=datetime(2026, 10, 13, 18, 0, tzinfo=UTC),
        resolved_at=date(2027, 1, 12),
        context=PredictionContext(
            mode="forward", snapshot_date=date(2026, 10, 12), signals_observable=True
        ),
    )
    event = CasePaths(data_root, "scotus", 9026000221).event("evt-petition-disposition")
    write_json(
        event.outcome,
        Outcome.model_validate(
            dict(
                case_id=ev.case_id,
                event_id=ev.event_id,
                resolved_at=date(2027, 1, 12),
                actual_disposition="granted",
                actual_granted=1,
                signals=dict(distribution_count=3, cvsg_date=cvsg_date),
            )
        ),
    )
    if poll is not None:
        write_json(
            event.prediction_usage("claude-baseline", "p1"),
            ModelUsage(
                case_id=ev.case_id,
                event_id=ev.event_id,
                run_id="p1",
                role=UsageRole.predictor,
                actor_id="claude-baseline",
                engine=Engine.claude_code,
                model="claude-fable-5",
                created_at=datetime(2026, 10, 13, 18, 5, tzinfo=UTC),
                input_tokens=1,
                output_tokens=1,
                estimated_cost_usd=0.0,
                pre_mint_poll=poll,
            ),
        )


def test_stratify_records_a_run_day_claim_and_leaves_the_cell_in(tmp_path: Path) -> None:
    _write_cvsg_cell(tmp_path, cvsg_date=date(2026, 10, 13), poll=None)
    run = stratify(tmp_path, frozen_only=False)
    (cell,) = run.cells
    assert run.set_aside == []
    key = (cell[0].case_id, cell[0].event_id, cell[0].predictor_id, cell[0].evaluator_id, "r1")
    assert dict(run.claim_set_aside[key]) == {"cvsg-increment": "increment-run-day"}
    # The Release 1 computation applies no set-aside at either grain.
    assert not stratify(tmp_path, frozen_only=False, apply_set_aside=False).claim_set_aside


def test_a_poll_that_read_no_cvsg_keeps_the_run_day_claim_in(tmp_path: Path) -> None:
    poll = DocketPollRecord(
        polled_at=datetime(2026, 10, 13, 17, 55, tzinfo=UTC),
        docket_number="26-221",
        state="open",
        signals=PolledIncrementSignals(cvsg=PolledSignal(present=False)),
    )
    _write_cvsg_cell(tmp_path, cvsg_date=date(2026, 10, 13), poll=poll)
    assert not stratify(tmp_path, frozen_only=False).claim_set_aside


# --- the corpus-check census ----------------------------------------------------


def _census_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "checks" / "increment_timing_census.py"
    spec = importlib.util.spec_from_file_location("increment_timing_census", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # A dataclass resolves its annotations through its module's registry entry.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_the_census_reads_each_claim_from_the_ledger_and_the_corpus(tmp_path: Path) -> None:
    census = _census_module()
    case = CasePaths(tmp_path, "scotus", 9526000416)
    write_yaml(
        case.event("evt-order-response-requested-disposition").event_file,
        PredictableEvent(
            event_id="evt-order-response-requested-disposition",
            case_id=APPLICATION,
            kind=EventKind.order,
            stage=Stage.interim,
            moment=Moment.response_requested,
            opened_at=date(2026, 9, 28),
            title="Test event",
        ),
    )
    event = case.event(MOTION)
    stamp = frozen_stamp().model_copy(update={"stamped_at": RUN})
    write_json(
        event.prediction("claude-baseline", "p1"),
        _prediction().model_copy(update={"process_version": stamp}),
    )
    write_json(event.outcome, _interim_outcome())

    def corpus_day(case_id: str, claim_id: str) -> date | None:
        assert case_id == APPLICATION
        return date(2026, 9, 28) if claim_id == "response-requested-increment" else RUN.date()

    found = {c.claim_id: c for c in census.census(tmp_path, corpus_day)}
    assert set(found) == {"response-requested-increment", "referral-increment"}
    requested = found["response-requested-increment"]
    assert (requested.ledger, requested.corpus, requested.resolved) == (
        "signal-before-run",
        "signal-before-run",
        True,
    )
    # No committed artifact dates a referral; the corpus payload does.
    referral = found["referral-increment"]
    assert (referral.ledger, referral.corpus) == ("unassessable", "signal-on-run-day")

    text = census.render(list(found.values()), 0)
    assert "| `response-requested-increment` | ledger | 1 | 1 | 1 (1 resolved)" in text
    assert (
        "| corpus | signal-on-run-day | `referral-increment` | `scotus/9526000416` "
        + "| `evt-motion-disposition` | 1 | True |"
    ) in text
    assert "- ledger and corpus readings that disagree (beyond unassessable): 0" in text


def test_the_census_runs_against_the_fixture_corpus(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    census = _census_module()
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("CHECK_SUMMARY", str(summary))
    with corpus.connect_readonly(fixture_corpus.db_path) as conn:
        day, unreadable = census._corpus_reader(conn)
        assert day("scotus/1", "referral-increment") is None
        assert unreadable() == 0
    assert census.main() == 0
    text = summary.read_text()
    assert "`fedcourts corpus-info`:" in text
    assert "| `cvsg-increment` | corpus | 0 | 0 |" in text
