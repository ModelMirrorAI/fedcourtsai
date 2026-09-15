"""The predict backlog deriver — what makes a scheduled ``run-predict`` level-triggered.

The live channel's transition trigger and its selection sweep queue predict off
*this cycle's* observations, and a run dropped on the floor leaves no trace they
can read. :func:`fedcourtsai.pipeline.pull.derive_predict_backlog` re-derives the
owed forecasts from committed state (in scope, funded, provisioned, and some
enabled predictor missing an open forecastable event), writing nothing.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus
from fedcourtsai.cli import app
from fedcourtsai.matrix import CaseRequest, predict_matrix
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.pull import (
    BACKLOG_MAX_POLL_AGE_DAYS,
    REPREDICT_MOMENTS,
    PredictBacklog,
    derive_predict_backlog,
)
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import CellFailure, Disposition, EventKind, Moment, ProcessVersion, Stage
from fedcourtsai.serialize import write_json
from tests.conftest import retired_stamp, seed_prediction

runner = CliRunner()

PREDICTORS = Path("config/predictors.yaml")
_REPO_CONFIG = Path(__file__).resolve().parents[1] / "config"

#: The case-baseline cert event every fixture case carries — the same id the
#: predict matrix tests use, so forecastability is exercised on the real moment.
EVENT = "evt-petition-cert"

#: The day every derivation in this module runs under, and a poll stamp one day
#: old. The freshness bound is an admission predicate now, so a fixture that
#: left `last_live_polled` unset would be held as stale before reaching whatever
#: it meant to exercise — the default says "the live rotation saw this
#: yesterday", which is the shipped corpus's median.
TODAY = date(2026, 7, 20)
FRESH = date(2026, 7, 19)


def _open_case(  # noqa: PLR0913 - one fixture knob per admission predicate under test
    db: Path,
    court: str,
    docket: int,
    *,
    event_id: str = EVENT,
    selected: bool = True,
    scored: bool = True,
    provisioned: bool = True,
    excluded: bool = False,
    stage: Stage | None = None,
    kind: EventKind = EventKind.petition,
    granted_on: date | None = None,
    polled_on: date | None = FRESH,
    queued_on: date | None = None,
    conference: date | None = None,
) -> None:
    """Seed one predict candidate: a distributed SCOTUS row, an open event, documents.

    ``distribution_count`` is not decoration — the case-baseline moment *is* the
    first distribution, so an undistributed petition has no forecastable
    baseline at all (``store._premature_distribution_cell``) and would drop out
    before any predicate this module tests. ``polled_on`` is load-bearing for
    the same reason: the record-freshness hold reads it.
    """
    case_id = f"{court}/{docket}"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court=court,
                    distribution_count=1,
                    salience_score=0.9 if scored else None,
                    salience_version="sal-v1" if scored else None,
                    salience_selected=selected,
                    date_cert_granted=granted_on,
                    disposition=Disposition.granted if granted_on else None,
                    last_live_polled=polled_on,
                    distributed_for_conference=conference,
                )
            ],
        )
        if queued_on is not None:
            corpus.stamp_predict_queued(conn, [case_id], queued_on)
        if excluded:
            corpus.set_predict_excluded(conn, case_id, True)
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event_id,
                    case_id=case_id,
                    court=court,
                    kind=kind,
                    stage=stage,
                    title="Disposition of the petition",
                    resolved=False,
                )
            ],
        )
        if provisioned:
            _provision(db, case_id)


def _provision(db: Path, case_id: str) -> None:
    """Commit one filed document for the case — the provisioning predicate's input."""
    with corpus.connect(db) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=case_id,
                    kind="petition",
                    url=f"https://example.invalid/{case_id}",
                    fetched_at=date(2026, 7, 1),
                    text="The petition text a predict cell is provisioned with.",
                )
            ],
        )


#: The register's second cert moment, for the fixtures that need a *second*
#: forecastable event on one case (per-event narrowing, the cohort bounds).
CVSG_EVENT = "evt-order-cvsg-disposition"


def _backlog(
    db: Path,
    data_root: Path,
    *,
    cap: int = 25,
    max_attempts: int = 0,
    today: date = TODAY,
    already_queued: set[str] | None = None,
) -> PredictBacklog:
    """One read-only derivation, whole."""
    with corpus.connect_readonly(db) as conn:
        return derive_predict_backlog(
            conn,
            data_root,
            PREDICTORS,
            cap=cap,
            max_attempts=max_attempts,
            already_queued=already_queued,
            today=today,
        )


def _derive(
    db: Path,
    data_root: Path,
    *,
    cap: int = 25,
    max_attempts: int = 0,
    today: date = TODAY,
    already_queued: set[str] | None = None,
) -> tuple[str, ...]:
    """Case ids one read-only derivation returns."""
    return _backlog(
        db,
        data_root,
        cap=cap,
        max_attempts=max_attempts,
        today=today,
        already_queued=already_queued,
    ).case_ids


def _entries(
    db: Path, data_root: Path, *, cap: int = 25, max_attempts: int = 0, today: date | None = None
) -> list[dict[str, object]]:
    with corpus.connect_readonly(db) as conn:
        backlog = derive_predict_backlog(
            conn,
            data_root,
            PREDICTORS,
            cap=cap,
            max_attempts=max_attempts,
            today=today or TODAY,
        )
    return [entry.as_queue_entry() for entry in backlog.entries]


def test_the_whole_feature_a_dropped_run_re_derives_then_stops(tmp_path: Path) -> None:
    """The load-bearing test. A predict run is owed, dropped on the floor (nothing
    committed), re-derived on a later cycle, then — once every engine has landed —
    stops re-deriving. This is the level-trigger the deriver exists to provide."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)

    assert _entries(db, data) == [{"court": "scotus", "docket": 1, "events": [EVENT]}]

    # The run is dropped: nothing is committed. A later cycle re-derives it.
    assert _derive(db, data, today=date(2026, 7, 21)) == ("scotus/1",)

    # Now every engine's prediction lands. The deriver goes quiet — the level has
    # been reached, with no stamp anywhere in the story.
    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(data, "scotus", 1, EVENT, predictor_id=predictor.id)
    assert _derive(db, data, today=date(2026, 7, 22)) == ()


def test_only_the_missing_engines_keep_a_case_owed(tmp_path: Path) -> None:
    """Partial coverage still counts as backlog: an event one engine predicted and
    the others did not is owed, so it re-derives (the matrix gate then mints only
    the missing engines). This is the per-(predictor, event) grain — a case-level
    gate would read the first landed prediction as "done" and never retry."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, EVENT, predictor_id=enabled_predictors(PREDICTORS)[0].id)

    assert _entries(db, data) == [{"court": "scotus", "docket": 1, "events": [EVENT]}]


def test_a_never_swept_case_is_held_and_admitted_once_provisioned(tmp_path: Path) -> None:
    """The provisioning hold, on the one class it applies to: a case the pull lane
    has never queued and that holds no documents, so provisioning has not been
    *attempted*. Held rather than minted with an empty record/ — and held, not
    excluded: the sweep reaches it, provisions it, and it derives."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False)

    assert _derive(db, data) == (), "provisioning has not been attempted for it yet"

    _provision(db, "scotus/1")
    assert _derive(db, data) == ("scotus/1",)


def test_a_queued_case_is_admitted_even_with_nothing_stored(tmp_path: Path) -> None:
    """The predicate is "provisioning was attempted", not "documents exist", and the
    queue stamp is the pull lane's own record that it ran — the sweep provisions at
    queue time. Reading document presence as the rule instead would conflate "not
    yet provisioned" with "provisioned, found nothing" and permanently strand every
    docket whose route came back empty: a Rule 34.6 paper filing the Court
    publishes no PDF for would be barred from this backlog forever rather than held
    for a window."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False, queued_on=date(2026, 7, 10))

    assert _derive(db, data) == ("scotus/1",)


def test_a_backlog_held_on_provisioning_is_counted_not_silently_empty(tmp_path: Path) -> None:
    """The held cases are reported, because the hold is expected to clear on its
    own. Without the count, a backlog every one of whose cases is waiting on
    run-pull is indistinguishable from a drained queue — the same conflation the
    absent-corpus refusal exists to prevent, one predicate over."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False)
    _open_case(db, "scotus", 2, provisioned=False)

    blocked = _backlog(db, data)
    assert blocked.entries == ()
    assert blocked.held_unswept == 2

    # Provision one: it derives, and only the still-unswept case is held.
    _provision(db, "scotus/1")
    partial = _backlog(db, data)
    assert partial.case_ids == ("scotus/1",)
    assert partial.held_unswept == 1

    # A genuinely drained backlog is the other reading, and says so.
    _provision(db, "scotus/2")
    for docket in (1, 2):
        for predictor in enabled_predictors(PREDICTORS):
            seed_prediction(data, "scotus", docket, EVENT, predictor_id=predictor.id)
    drained = _backlog(db, data)
    assert drained.entries == ()
    assert drained.held_unswept == 0


def test_a_held_case_that_is_not_owed_is_not_counted_as_held(tmp_path: Path) -> None:
    """The counts are taken over the **owed** population alone. A case that is
    unprovisioned *and* fully predicted is not work this lane owes, so counting it
    would make "held, still owed a forecast" false of the figure — which is exactly
    the reading the line invites. Only a case the holds are the sole obstacle for
    is counted."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False)  # unprovisioned AND fully predicted
    _open_case(db, "scotus", 2, provisioned=False, polled_on=date(2026, 1, 1))  # stale too
    for docket in (1, 2):
        for predictor in enabled_predictors(PREDICTORS):
            seed_prediction(data, "scotus", docket, EVENT, predictor_id=predictor.id)

    quiet = _backlog(db, data)
    assert quiet.entries == ()
    assert (quiet.held_unswept, quiet.held_stale) == (0, 0)


def test_the_hold_counts_are_censored_by_the_cap_and_say_so(tmp_path: Path) -> None:
    """The scan stops at the cap, so a candidate past the break is in neither hold
    count. `cap_reached` is what keeps a reader from quoting a lower bound as a
    total — the failure mode of an unqualified operational number."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    # Docket 1 derives and fills a cap of one; 2 would have been held, unexamined.
    _open_case(db, "scotus", 1)
    _open_case(db, "scotus", 2, provisioned=False)

    capped = _backlog(db, data, cap=1)
    assert capped.case_ids == ("scotus/1",)
    assert capped.cap_reached is True
    assert capped.held_unswept == 0, "the held case was never reached, so it is not counted"

    # Room for both: the hold is examined, counted, and the censoring flag is off.
    roomy = _backlog(db, data, cap=25)
    assert roomy.case_ids == ("scotus/1",)
    assert roomy.cap_reached is False
    assert roomy.held_unswept == 1


def test_a_stale_record_is_held_and_re_admitted_on_the_next_poll(tmp_path: Path) -> None:
    """The freshness bound. The live sweep re-polls before it queues and diverts a
    now-decided docket; this scan mints from committed state and cannot, so the
    record's own age is its only guard against a forward cell on a case whose
    answer is already public. Held, never excluded: the next poll re-admits it."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    stale = TODAY - timedelta(days=BACKLOG_MAX_POLL_AGE_DAYS + 1)
    _open_case(db, "scotus", 1, polled_on=stale)

    held = _backlog(db, data)
    assert held.entries == ()
    assert held.held_stale == 1

    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET last_live_polled = ? WHERE case_id = ?",
            (TODAY.isoformat(), "scotus/1"),
        )
        conn.commit()
    assert _derive(db, data) == ("scotus/1",)


def test_a_record_exactly_at_the_freshness_bound_is_still_admitted(tmp_path: Path) -> None:
    """The bound is inclusive, pinned so a refactor cannot quietly shave a day off
    a horizon whose whole job is to be a stated number."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, polled_on=TODAY - timedelta(days=BACKLOG_MAX_POLL_AGE_DAYS))

    assert _derive(db, data) == ("scotus/1",)


def test_a_case_neither_channel_has_ever_observed_is_held_stale(tmp_path: Path) -> None:
    """No stamp from either channel is the limit of "stale", not an exemption from
    it: nothing has ever confirmed the event is still open."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, polled_on=None)

    held = _backlog(db, data)
    assert held.entries == ()
    assert held.held_stale == 1


def test_the_rest_rotation_stamp_counts_as_an_observation(tmp_path: Path) -> None:
    """Freshness is the age of the record, not of one channel's coverage, so the
    freshest of the two rotation stamps answers it. A case the live poller has not
    reached but the CourtListener rotation refreshed today is a fresh record."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, polled_on=TODAY - timedelta(days=30))
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET last_pulled = ? WHERE case_id = ?", (FRESH.isoformat(), "scotus/1")
        )
        conn.commit()

    assert _derive(db, data) == ("scotus/1",)


def test_the_provisioning_predicate_does_not_spend_a_cap_slot(tmp_path: Path) -> None:
    """A held case must not consume the cycle's cap, or a run of unprovisioned rows
    at the stale front of the queue would starve every derivable case behind them
    — the failure mode a held-but-counted candidate quietly creates."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False)
    _open_case(db, "scotus", 2, provisioned=False)
    _open_case(db, "scotus", 3)

    assert _derive(db, data, cap=1) == ("scotus/3",)


def test_an_unscored_unselected_case_is_not_a_candidate(tmp_path: Path) -> None:
    """The funding gate. Predict's case set is a funded salience selection, and a
    row selection has not had an opinion about yet spends nothing until it does —
    the conservative direction, and the sweep's own reading."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, selected=False, scored=False)

    assert _derive(db, data) == ()


def test_a_salience_deferred_case_is_narrowed_to_its_claimable_cohort(tmp_path: Path) -> None:
    """The scope trap, in predict's own shape. A case scored below the funding line
    is not swept — unless it already carries a committed cohort a claimable board
    will count, in which case the missing engines are the only spend left on it and
    the queue is narrowed to exactly those events. An event with no such cohort
    would be brand-new spend on a case the gate declined, so it goes with the
    drop."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, selected=False)
    # A second open event on the same case, carrying no cohort at all.
    _open_case(db, "scotus", 1, event_id="evt-petition-cvsg", selected=False)

    assert _derive(db, data) == (), "deferred and with no cohort anywhere: not a candidate"

    seed_prediction(data, "scotus", 1, EVENT, predictor_id="claude-baseline", frozen=True)
    assert _entries(db, data) == [{"court": "scotus", "docket": 1, "events": [EVENT]}], (
        "admitted for cohort completion, narrowed to the event holding the cohort"
    )


def test_an_open_merits_event_bypasses_the_funding_gate(tmp_path: Path) -> None:
    """A granted case was selected by the Court itself, and the cert-stage funding
    question — which of ~1,500 petitions earns a forecast — has no bearing on a
    population of ~65 grants a Term. So a deferred row carrying an open merits
    event is still owed its merits cells."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(
        db,
        "scotus",
        1,
        event_id="evt-order-judgment",
        selected=False,
        stage=Stage.merits,
        kind=EventKind.order,
        granted_on=date(2026, 6, 1),
    )

    assert _entries(db, data) == [
        {"court": "scotus", "docket": 1, "events": ["evt-order-judgment"]}
    ]


def test_an_excluded_case_is_never_owed(tmp_path: Path) -> None:
    """`predict_excluded` is the hard-scope latch the scope reconcile writes; the
    funding grounds ride beside it, never through it."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, excluded=True)

    assert _derive(db, data) == ()


def test_a_resolved_event_is_not_owed(tmp_path: Path) -> None:
    """The complement of the evaluate backlog: a forecast is owed on an event still
    open, and resolution latches closed. A resolved event is grading work, not
    forecasting work."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    with corpus.connect(db) as conn:
        corpus.set_event_resolved(conn, "scotus/1", EVENT)

    assert _derive(db, data) == ()


def test_a_case_a_caller_already_queued_is_not_double_derived(tmp_path: Path) -> None:
    """The caller's own queue and the deriver share one fan-out; a case already
    covered this cycle must not appear twice."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)

    assert _derive(db, data, already_queued={"scotus/1"}) == ()


def test_the_cap_bounds_the_backlog_and_drains_stalest_first(tmp_path: Path) -> None:
    """The cap bounds spend and PR volume; the backlog drains across cycles, oldest
    `predict_queued_at` first, so nothing is starved."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    for docket in (1, 2, 3):
        _open_case(db, "scotus", docket)
    # Pre-stamp docket 2 as queued longest ago, 3 more recently, 1 never.
    with corpus.connect(db) as conn:
        corpus.stamp_predict_queued(conn, ["scotus/2"], date(2026, 7, 1))
        corpus.stamp_predict_queued(conn, ["scotus/3"], date(2026, 7, 10))

    # Never-queued (None) sorts first, then the stalest stamp.
    assert _derive(db, data, cap=2) == ("scotus/1", "scotus/2")


def test_a_backlog_larger_than_the_cap_fully_drains_over_cycles(tmp_path: Path) -> None:
    """With more owed cases than the cap, does the backlog still drain? It does —
    but only because a consumer eventually commits the predictions. Stamp-free, the
    deriver re-presents the same head each cycle, so the drain is the ledger moving
    under it, not the ordering rotating on its own."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    for docket in range(1, 6):
        _open_case(db, "scotus", docket)

    drained: set[str] = set()
    day = date(2026, 7, 20)
    for _ in range(3):  # ceil(5 / cap=2) = 3 cycles
        cycle = _derive(db, data, cap=2, today=day)
        drained |= set(cycle)
        for case_id in cycle:
            for predictor in enabled_predictors(PREDICTORS):
                seed_prediction(
                    data, "scotus", int(case_id.split("/")[1]), EVENT, predictor_id=predictor.id
                )
        day += timedelta(days=1)

    assert drained == {f"scotus/{n}" for n in range(1, 6)}


def test_cap_zero_is_a_no_op(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    assert _derive(db, data, cap=0) == ()


def _fail_cell(
    data_root: Path, court: str, docket: int, predictor_id: str, event_id: str, times: int
) -> None:
    """Commit `times` predict-seam failure facts for one cell into the ledger.

    One run-scoped `attempt.json` per distinct run, so the deriver's ledger glob
    (`cell_failure_count`) counts `times`, mirroring what the collect job writes."""
    for i in range(times):
        run_id = f"20260101T0000{i:02d}Z"
        write_json(
            CasePaths(data_root, court, docket)
            .event(event_id)
            .prediction_attempt(predictor_id, run_id),
            CellFailure(
                seam="predict",
                actor=predictor_id,
                court=court,
                docket=docket,
                event_id=event_id,
                run_id=run_id,
                error_class="no_output",
            ),
        )


def test_a_fresh_never_attempted_cell_is_owed_under_the_cap(tmp_path: Path) -> None:
    """The baseline the cap must not disturb: a cell with no recorded attempts is
    below any positive cap, so it derives exactly as it would with no cap."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)

    assert _derive(db, data, max_attempts=5) == ("scotus/1",)


def test_a_cell_at_the_cap_is_not_re_derived(tmp_path: Path) -> None:
    """The poison-pill backstop. Once every predictor's cell for the event has hit
    the attempt cap the event is no longer owed, so a cell that fails every attempt
    cannot re-derive forever — which a stamp-free deriver alone would allow."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    for predictor in enabled_predictors(PREDICTORS):
        _fail_cell(data, "scotus", 1, predictor.id, EVENT, times=3)

    assert _derive(db, data, max_attempts=3) == (), "all cells exhausted the cap"

    # The cap is the only thing holding it back: raise the ceiling and the same
    # under-cap cells are owed again (they are still unpredicted).
    assert _derive(db, data, max_attempts=4) == ("scotus/1",)


def test_a_fully_covered_sibling_event_is_dropped_and_the_owed_one_kept(tmp_path: Path) -> None:
    """Per-event narrowing on a **funded** case, where no cohort bound applies. The
    entry carries only the events some predictor still owes: an event every engine
    has covered is dropped even though its sibling keeps the case in the backlog.
    This changes no cell — the matrix's per-(predictor, event) skip would drop
    those anyway — it keeps the fan-out from being handed an event that would
    arrive empty."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    _open_case(db, "scotus", 1, event_id=CVSG_EVENT, stage=Stage.cert, kind=EventKind.order)
    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(data, "scotus", 1, EVENT, predictor_id=predictor.id)

    assert _entries(db, data) == [{"court": "scotus", "docket": 1, "events": [CVSG_EVENT]}]


def test_an_attempt_capped_sibling_event_is_dropped_stricter_than_the_sweep(
    tmp_path: Path,
) -> None:
    """The second narrowing ground, and the one that is *not* a no-op. An event
    whose every still-missing predictor is attempt-capped is dropped, while a
    sibling under the cap keeps the case — a stricter reading than the live sweep,
    whose owed check is per case and would queue both. Deliberate: an unattended
    lane writes no debounce stamp, so a cell failing every attempt would otherwise
    be re-derived every cycle forever."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    _open_case(db, "scotus", 1, event_id=CVSG_EVENT, stage=Stage.cert, kind=EventKind.order)
    for predictor in enabled_predictors(PREDICTORS):
        _fail_cell(data, "scotus", 1, predictor.id, EVENT, times=3)

    assert _entries(db, data, max_attempts=3) == [
        {"court": "scotus", "docket": 1, "events": [CVSG_EVENT]}
    ]
    # The cap is the only thing dropping it: raise the ceiling and both return.
    assert _entries(db, data, max_attempts=4) == [
        {"court": "scotus", "docket": 1, "events": [CVSG_EVENT, EVENT]}
    ]


def test_the_cap_is_per_cell_a_sibling_predictor_is_still_owed(tmp_path: Path) -> None:
    """Per-(predictor, event) granularity: one engine hitting the cap must not
    suppress a sibling still owed the same event — the reason the cap keys on cell
    identity rather than a coarse per-case counter."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    _fail_cell(data, "scotus", 1, enabled_predictors(PREDICTORS)[0].id, EVENT, times=3)

    assert _derive(db, data, max_attempts=3) == ("scotus/1",)


def test_the_deriver_never_indexes_the_whole_court(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Candidates come from the open-event set, not from a whole-court index.

    Peak memory must scale with the work (cases holding an open event) rather than
    with the corpus, whose SCOTUS slice is hundreds of thousands of rows and only
    grows. `iter_rows` is the whole-court walk — the walk the live sweep does take
    — so making it fatal is what pins the property; a fixture-sized test cannot
    observe the memory itself.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)

    def _fail(*args: object, **kwargs: object) -> object:
        raise AssertionError("derive_predict_backlog must not walk every row in the court")

    monkeypatch.setattr(corpus, "iter_rows", _fail)
    assert _derive(db, data) == ("scotus/1",)


def test_an_open_event_whose_case_row_is_absent_is_skipped(tmp_path: Path) -> None:
    """An open event with no `cases` row cannot be scope-checked or funded, so it
    is not a candidate — absence must stay a skip rather than becoming a crash."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    with corpus.connect(db) as conn:
        conn.execute("DELETE FROM cases WHERE case_id = ?", ("scotus/1",))
        conn.commit()

    assert _derive(db, data) == ()


def test_the_deriver_reads_through_a_read_only_connection_and_stamps_nothing(
    tmp_path: Path,
) -> None:
    """The scan alone: it finds the owed forecast and leaves `predict_queued_at`
    untouched. That is the contract the predict stage's own schedule depends on —
    it runs outside the writer jobs, so it holds no corpus-write credentials and
    could not stamp even if it wanted to."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)

    with corpus.connect_readonly(db) as conn:
        backlog = derive_predict_backlog(
            conn, data, PREDICTORS, cap=25, max_attempts=5, today=date(2026, 7, 20)
        )

    assert [entry.as_queue_entry() for entry in backlog.entries] == [
        {"court": "scotus", "docket": 1, "events": [EVENT]}
    ]
    assert backlog.case_ids == ("scotus/1",)
    assert backlog.day == date(2026, 7, 20)
    with corpus.connect_readonly(db) as conn:
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None
    assert row.predict_queued_at is None


def test_a_stamp_free_derivation_repeats_until_the_prediction_lands(tmp_path: Path) -> None:
    """Without a debounce stamp the same backlog re-derives every cycle — and that
    is correct, not a leak. Idempotency comes from the ledger the scan reads: the
    moment the predictions are committed, the deriver goes quiet on its own."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)

    # Same day, same cycle, twice over: no stamp means no self-debounce.
    assert _derive(db, data) == ("scotus/1",)
    assert _derive(db, data) == ("scotus/1",)

    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(data, "scotus", 1, EVENT, predictor_id=predictor.id)
    assert _derive(db, data) == ()


def test_a_stamp_the_pull_lane_wrote_still_holds_the_derivation_back(tmp_path: Path) -> None:
    """The two lanes debounce against each other in the one direction that is
    possible: this scan writes no stamp, but it honours the one the pull/live lane
    wrote, so a case handed off this morning is not derived again tonight."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1)
    with corpus.connect(db) as conn:
        corpus.stamp_predict_queued(conn, ["scotus/1"], date(2026, 7, 20))

    assert _derive(db, data, today=date(2026, 7, 20)) == ()
    assert _derive(db, data, today=date(2026, 7, 21)) == ("scotus/1",)


# --- the predict stage's second input mode, through the CLI ---


def _flat(output: str) -> str:
    """CLI output with ANSI styling stripped and runs of whitespace collapsed.

    Typer renders a refusal inside a bordered box, wrapping the message at the
    frame width, so a phrase that is contiguous in the source is split across
    lines here — and on a CI runner rich emits color escapes mid-phrase, so a
    substring match must strip them too.
    """
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    return " ".join(plain.replace("│", " ").split())


def _cli_env(tmp_path: Path, *dockets: int, provisioned: bool = True) -> dict[str, str]:
    """A hermetic config + corpus holding one predict candidate per docket.

    Every path is under ``tmp_path`` and every setting the derivation reads is
    named explicitly, so the run cannot fall through to an ambient corpus — a
    backlog mode that reads the checkout's real corpus would scan production
    state from inside the unit suite, and would pass or fail on whether the
    machine happened to have pulled one.
    """
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    (config_root / "predictors.yaml").write_text((_REPO_CONFIG / "predictors.yaml").read_text())
    (config_root / "evaluators.yaml").write_text((_REPO_CONFIG / "evaluators.yaml").read_text())
    (config_root / "tracking.yaml").write_text("predict:\n  scope: scotus_docket\n")
    corpus_root = tmp_path / "corpus"
    for docket in dockets:
        # Polled today, not on this module's fixed fixture date: a CLI run reads
        # the wall clock, so a fixture stamp would age past the freshness bound
        # and every case would be held stale for a reason no test meant to set.
        _open_case(
            corpus.corpus_db_path(corpus_root),
            "scotus",
            docket,
            provisioned=provisioned,
            polled_on=date.today(),
        )
    return {
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
    }


def test_predict_matrix_with_no_body_file_derives_its_cases_from_the_backlog(
    tmp_path: Path,
) -> None:
    """The scheduled mode: given no case list at all, the fan-out is the
    forecasts committed state still owes — the derivation a run-predict
    schedule consumes."""
    env = _cli_env(tmp_path, 24001, 24002)

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    cells = json.loads(result.stdout)["include"]
    minted = {(c["docket"], c["predictor_id"]) for c in cells}
    assert minted == {
        (docket, predictor.id)
        for docket in (24001, 24002)
        for predictor in enabled_predictors(PREDICTORS)
    }


def test_predict_plan_takes_the_backlog_mode_too(tmp_path: Path) -> None:
    """The dry run of the scheduled fan-out: the same derivation, reported rather
    than minted, so a maintainer can read what a cron would spend before it does."""
    env = _cli_env(tmp_path, 24001)

    result = runner.invoke(app, ["predict-plan", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    plan = json.loads(result.stdout)
    assert {cell["docket"] for cell in plan["would_mint"]} == {24001}


def test_the_backlog_mode_writes_no_debounce_stamp(tmp_path: Path) -> None:
    """The mode must not write the corpus at all: it runs outside the writer jobs,
    which hold the only corpus-write credentials. `predict_queued_at` is the write
    it would otherwise inherit from the live lane, so its absence is asserted
    directly — and the database file's digest with it, since a stray write
    elsewhere in the scan would not move the stamp."""
    env = _cli_env(tmp_path, 24001)
    db = corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"]))
    digest = hashlib.sha256(db.read_bytes()).hexdigest()

    minted = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert minted.exit_code == 0, minted.output
    # Write-freedom *on a run that did the work*: without this, a regression that
    # derived an empty backlog would leave the test green while destroying what it
    # claims to protect.
    assert json.loads(minted.stdout)["include"]
    with corpus.connect_readonly(db) as conn:
        row = corpus.get_row(conn, "scotus/24001")
    assert row is not None
    assert row.predict_queued_at is None
    assert hashlib.sha256(db.read_bytes()).hexdigest() == digest


def test_a_body_file_still_wins_over_the_backlog(tmp_path: Path) -> None:
    """A body file names the fan-out outright, so it takes precedence: the cases
    are the body's, and the backlog is never consulted."""
    env = _cli_env(tmp_path, 24001, 24002)
    body = tmp_path / "issue-body.md"
    body.write_text(
        'Trigger.\n\n```json\n{"court": "scotus", "docket": 24001, "events": ["'
        + EVENT
        + '"]}\n```\n'
    )

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0, result.output
    assert {c["docket"] for c in json.loads(result.stdout)["include"]} == {24001}


@pytest.mark.parametrize(
    "flags",
    [
        ["--court", "scotus"],
        ["--docket", "24001"],
        ["--event", EVENT],
    ],
)
def test_a_half_named_case_is_refused_rather_than_widened_to_the_backlog(
    tmp_path: Path, flags: list[str]
) -> None:
    """Silence is what selects the backlog mode, so a dropped `--docket` would
    otherwise turn one intended case into a whole-backlog fan-out. That is the one
    typo whose blast radius is model spend, so each half-named form is an error."""
    env = _cli_env(tmp_path, 24001)

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID", *flags], env=env)

    assert result.exit_code != 0
    assert '"include"' not in result.stdout
    assert "go together" in _flat(result.output) or "--event names" in _flat(result.output)


def test_the_backlog_mode_refuses_a_read_in_place_corpus_backend(tmp_path: Path) -> None:
    """The scan is one pass over every open event plus a point query per candidate
    — the opposite shape from the point lookups a named-case run makes, and so the
    opposite backend. Refused here rather than discovered as a range-request storm
    on an unattended run."""
    env = _cli_env(tmp_path, 24001)

    result = runner.invoke(
        app,
        ["predict-matrix", "--run-id", "RID"],
        env={**env, "FEDCOURTS_CORPUS_BACKEND": "ranged"},
    )

    assert result.exit_code != 0
    assert "cannot be derived over" in _flat(result.output)


def test_the_backlog_mode_refuses_a_corpus_backend_with_no_query_surface(tmp_path: Path) -> None:
    """A backend with no queryable connection is refused by the same gate, and for
    the stronger reason: it could not serve the scan at all. It fails loudly rather
    than falling back to a local file the runner may never have pulled."""
    env = _cli_env(tmp_path, 24001)

    result = runner.invoke(
        app,
        ["predict-matrix", "--run-id", "RID"],
        env={**env, "FEDCOURTS_CORPUS_BACKEND": "service"},
    )

    assert result.exit_code != 0
    assert "cannot be derived over" in _flat(result.output)


def test_the_cli_reports_the_held_count_on_stderr(tmp_path: Path) -> None:
    """The held cases reach the operator, on stderr — stdout carries only the
    matrix JSON. An empty fan-out and one whose every case is waiting on
    provisioning are different operational facts, and only the second says the
    lane is blocked on run-pull rather than done."""
    env = _cli_env(tmp_path, 24001, 24002, provisioned=False)

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["include"] == []
    assert "held 2 owed case(s) the pull lane has never queued" in _flat(result.stderr)


def test_the_cli_stays_quiet_when_nothing_is_held(tmp_path: Path) -> None:
    """The complement, so the line means something: a fully provisioned backlog
    reports no held cases at all rather than a zero."""
    env = _cli_env(tmp_path, 24001)

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    assert "held" not in _flat(result.stderr)
    # The summary line still runs, and names which store answered the probe — a
    # mis-set split flag is otherwise invisible in the plan output.
    assert "1 case(s) owed a forecast" in _flat(result.stderr)
    assert "resolve against the corpus blob" in _flat(result.stderr)


def test_the_backlog_mode_refuses_an_unreachable_content_store(tmp_path: Path) -> None:
    """Under the corpus-split mode the blob holds no documents, so an unbuilt
    casestore transport answers every provisioning probe false — and the transport
    build swallows its own failure by design, so nothing raises. The derivation
    would hold every case and return empty, reading exactly like a drained queue.
    Refused instead, on the same principle as the absent corpus."""
    env = _cli_env(tmp_path, 24001)

    with casestore.transport_override(None):
        result = runner.invoke(
            app,
            ["predict-matrix", "--run-id", "RID"],
            env={**env, "FEDCOURTS_CORPUS_SPLIT": "1"},
        )

    assert result.exit_code != 0
    assert "no content store could be reached" in _flat(result.output)


def test_a_reachable_content_store_serves_the_split_mode_derivation(tmp_path: Path) -> None:
    """The refusal is about reachability, not about the split mode: with a store
    that actually holds the case's documents the derivation runs, and the
    provisioning predicate is answered from the store rather than the blob."""
    env = _cli_env(tmp_path, 24001, provisioned=False)
    transport = casestore.InMemoryObjectTransport()
    casestore.write_documents(
        transport,
        "scotus/24001",
        [
            corpus.CaseDocument(
                case_id="scotus/24001",
                kind="petition",
                url="https://example.invalid/p",
                fetched_at=date(2026, 7, 1),
                text="stored in the content store, not the blob",
            )
        ],
    )

    with casestore.transport_override(transport):
        result = runner.invoke(
            app,
            ["predict-matrix", "--run-id", "RID"],
            env={**env, "FEDCOURTS_CORPUS_SPLIT": "1"},
        )

    assert result.exit_code == 0, result.output
    assert {c["docket"] for c in json.loads(result.stdout)["include"]} == {24001}
    # And the summary names the store that answered, so a mis-set split flag is
    # visible in the plan output rather than an unexplained short fan-out.
    assert "resolve against the content store" in _flat(result.stderr)


def test_the_backlog_mode_refuses_an_absent_corpus(tmp_path: Path) -> None:
    """For an unattended lane, "nothing is owed" and "no corpus on disk" must not
    be the same output — an empty fan-out from a runner that never pulled reads
    exactly like a drained backlog."""
    env = _cli_env(tmp_path, 24001)
    corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"])).unlink()

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code != 0
    assert "corpus-pull" in _flat(result.output)


# --- The pre-freeze re-predict rule ------------------------------------------
#
# The owed check above is version-blind, which is a hole a predictor-half
# re-bless opens: an event whose whole committed cohort carries retired digests
# is reported covered while holding forecasts no claimable board will ever
# count. These exercise the rule that re-owes it — and, just as importantly,
# every case it must refuse.

#: The register's cert baseline, whose declared moment is the first
#: distribution. The rule is keyed on the *declared* moment, so these fixtures
#: use the real id rather than this module's undeclared `EVENT`.
BASELINE_EVENT = "evt-petition-disposition"

#: A conference still ahead of `TODAY`, and one already behind it — the
#: distribution moment's open/closed boundary.
FUTURE_CONFERENCE = date(2026, 8, 7)
PAST_CONFERENCE = date(2026, 7, 10)


def _retired_cohort(
    data: Path,
    docket: int,
    *,
    event_id: str = BASELINE_EVENT,
    frozen_predictors: tuple[str, ...] = (),
    stamp: ProcessVersion | None = None,
) -> None:
    """Commit one prediction per enabled predictor, all but ``frozen_predictors`` retired."""
    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(
            data,
            "scotus",
            docket,
            event_id,
            predictor_id=predictor.id,
            frozen=predictor.id in frozen_predictors,
            stamp=None if predictor.id in frozen_predictors else stamp,
        )


def _reopened(backlog: PredictBacklog) -> dict[str, tuple[str, ...]]:
    return {entry.case_id: entry.reopened for entry in backlog.entries}


def test_an_event_whose_whole_cohort_is_retired_is_re_owed(tmp_path: Path) -> None:
    """The rule itself. Every predictor has predicted the event, so the
    version-blind owed check reports nothing due — yet no cell it holds is in the
    frozen partition, so when the event resolves the whole cohort is dropped from
    the board and the event is consumed for nothing."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    _retired_cohort(data, 1)

    backlog = _backlog(db, data)

    assert backlog.case_ids == ("scotus/1",)
    assert _reopened(backlog) == {"scotus/1": (BASELINE_EVENT,)}
    assert backlog.entries[0].events == (BASELINE_EVENT,)
    assert backlog.reowed_events == 1


def test_a_retired_digest_reads_the_same_as_an_unstamped_cell(tmp_path: Path) -> None:
    """The two ways out of the frozen partition are one condition. An unstamped
    shakedown cell carries no digest; a de-counted cell carries one the current
    freeze no longer blesses. `is_frozen` rejects both, and so does this rule."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    _retired_cohort(data, 1, stamp=retired_stamp())

    assert _reopened(_backlog(db, data)) == {"scotus/1": (BASELINE_EVENT,)}


def test_a_predictor_holding_a_blessed_cell_is_not_re_owed_one(tmp_path: Path) -> None:
    """The rule buys a blessed cell where there is none, never a second one. With
    every engine already inside the partition there is nothing to repair, and the
    event drops out of the backlog entirely."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    _retired_cohort(data, 1, frozen_predictors=tuple(p.id for p in enabled_predictors(PREDICTORS)))

    assert _backlog(db, data).case_ids == ()


def test_a_partly_blessed_cohort_re_mints_only_its_retired_half(tmp_path: Path) -> None:
    """Per (predictor, event), not per event: an engine that already re-ran under
    the blessed process keeps its cell, and only the engines still on a retired
    digest are minted again."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    blessed = enabled_predictors(PREDICTORS)[0].id
    _retired_cohort(data, 1, frozen_predictors=(blessed,))

    backlog = _backlog(db, data)
    assert _reopened(backlog) == {"scotus/1": (BASELINE_EVENT,)}

    # The event is re-owed, and the fan-out decides the engines: the blessed one
    # is skipped exactly as an already-predicted cell always was.
    case = CaseRequest("scotus", 1, (BASELINE_EVENT,), reopen_events=(BASELINE_EVENT,))
    minted = predict_matrix(PREDICTORS, [case], "RID", data)["include"]
    assert {cell["predictor_id"] for cell in minted} == {
        p.id for p in enabled_predictors(PREDICTORS)
    } - {blessed}


def test_an_event_the_ledger_already_resolved_is_not_re_owed(tmp_path: Path) -> None:
    """A recorded outcome ends the forecast. The rule adds forward cells only, so
    it defers to the same record-side gate the fan-out applies."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    _retired_cohort(data, 1)
    # The gate reads the file's existence, not its body.
    outcome = CasePaths(data, "scotus", 1).event(BASELINE_EVENT).outcome
    outcome.parent.mkdir(parents=True, exist_ok=True)
    outcome.write_text("{}")

    assert _backlog(db, data).case_ids == ()


def test_a_case_decided_in_the_corpus_without_an_outcome_yet_is_not_re_owed(
    tmp_path: Path,
) -> None:
    """The maintainer's hard caveat, and the one exclusion a version-blind reading
    would miss. The live channel polls a docket as decided before it writes the
    outcome, so between the two the corpus says decided and the ledger says open.
    A cell minted in that window is a replay wearing forward clothing — with
    unrestricted retrieval over an answer that is already public."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(
        db,
        "scotus",
        1,
        event_id=BASELINE_EVENT,
        conference=FUTURE_CONFERENCE,
        granted_on=date(2026, 7, 15),
    )
    _retired_cohort(data, 1)

    assert _backlog(db, data).case_ids == ()


def test_the_cert_arrival_moment_is_not_re_owed(tmp_path: Path) -> None:
    """Its whole contract is "forecast at docketing, before any distribution or
    docket-acquired signal exists". A cell minted now would not be a late forecast
    of that moment but a forecast of a different one — the moment is gone, and only
    the original cell ever observed it."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    arrival = "evt-petition-arrival-disposition"
    _open_case(db, "scotus", 1, event_id=arrival, stage=Stage.cert, conference=FUTURE_CONFERENCE)
    _retired_cohort(data, 1, event_id=arrival)

    assert (Stage.cert, Moment.arrival) not in REPREDICT_MOMENTS
    assert _backlog(db, data).case_ids == ()


def test_a_distribution_whose_conference_has_passed_is_not_re_owed(tmp_path: Path) -> None:
    """The distribution cell forecasts the conference the petition is distributed
    for. Once that conference is behind us the order list has issued or the
    petition relisted, and a cell minted now answers a different question from the
    one the retired cells answered."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=PAST_CONFERENCE)
    _retired_cohort(data, 1)

    assert _backlog(db, data).case_ids == ()
    # …and the same case with the conference still ahead is re-owed, so the
    # refusal is the date and nothing else about the fixture.
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    assert _backlog(db, data).case_ids == ("scotus/1",)


def test_the_moment_allow_list_holds_merits_out_and_is_one_edit_from_taking_them(
    tmp_path: Path,
) -> None:
    """Merits moments resolve months out, so the rule *would* apply to them — they
    are held out because that is spend now for a board population a Term away, a
    funding call rather than a correctness one. The table is the whole switch."""
    assert (Stage.merits, Moment.grant) not in REPREDICT_MOMENTS
    assert (Stage.merits, Moment.briefed) not in REPREDICT_MOMENTS
    assert {
        (Stage.cert, Moment.distribution),
        (Stage.cert, Moment.cvsg),
        (Stage.interim, Moment.arrival),
        (Stage.interim, Moment.response_requested),
        (Stage.interim, Moment.response_filed),
    } == REPREDICT_MOMENTS

    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(
        db,
        "scotus",
        1,
        event_id="evt-order-judgment",
        kind=EventKind.order,
        stage=Stage.merits,
        granted_on=date(2026, 7, 1),
        conference=FUTURE_CONFERENCE,
    )
    _retired_cohort(data, 1, event_id="evt-order-judgment")

    assert _backlog(db, data).case_ids == ()


def test_re_owed_cases_are_ordered_after_never_predicted_ones(tmp_path: Path) -> None:
    """The rule must never starve the ordinary backlog. Stalest-first would put the
    re-owed case first here; the grouping puts the never-predicted one in front of
    it, so a cap truncates from the re-owed end."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    # The re-owed case is the *staler* of the two, so candidate order alone
    # would lead with it.
    _open_case(
        db,
        "scotus",
        1,
        event_id=BASELINE_EVENT,
        conference=FUTURE_CONFERENCE,
        polled_on=TODAY - timedelta(days=5),
    )
    _retired_cohort(data, 1)
    _open_case(db, "scotus", 2, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)

    assert _derive(db, data) == ("scotus/2", "scotus/1")
    # And under a cap of one it is the never-predicted case that survives.
    assert _derive(db, data, cap=1) == ("scotus/2",)


def test_within_a_case_the_never_predicted_events_lead(tmp_path: Path) -> None:
    """The same priority at the event grain, so a downstream reader that truncates
    an event list keeps the ordinary backlog first."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=CVSG_EVENT,
                    case_id="scotus/1",
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.cert,
                    title="CVSG",
                    resolved=False,
                )
            ],
        )
    _retired_cohort(data, 1)

    entry = _backlog(db, data).entries[0]
    assert entry.events == (CVSG_EVENT, BASELINE_EVENT)
    assert entry.reopened == (BASELINE_EVENT,)


def test_the_salience_cohort_is_untouched_by_the_rule(tmp_path: Path) -> None:
    """The rule re-opens events the project already paid for; it opens none the
    funding gate declined. A salience-deferred case reaches the deriver only on the
    cohort-completion ground, which keeps exactly the events a claimable board
    already counts — and a wholly retired cohort is not one of them."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(
        db,
        "scotus",
        1,
        event_id=BASELINE_EVENT,
        selected=False,
        conference=FUTURE_CONFERENCE,
    )
    _retired_cohort(data, 1)

    assert _backlog(db, data).case_ids == ()


def test_the_plan_reports_re_owed_cells_in_their_own_bucket(tmp_path: Path) -> None:
    """A re-forecast of an event the ledger already covers is a spend decision, so
    the dry run a maintainer reads before the hold must show it as such rather than
    as an ordinary unpredicted cell."""
    # No docket from the helper: this case carries the register's declared
    # baseline alone, so every cell in the plan is one the rule re-owed.
    env = _cli_env(tmp_path)
    db = corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"]))
    _open_case(
        db,
        "scotus",
        24001,
        event_id=BASELINE_EVENT,
        polled_on=date.today(),
        conference=date.today() + timedelta(days=14),
    )
    _retired_cohort(Path(env["FEDCOURTS_DATA_ROOT"]), 24001)

    result = runner.invoke(app, ["predict-plan", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    plan = json.loads(result.stdout)
    engines = len(enabled_predictors(PREDICTORS))
    assert plan["counts"]["cell_ledger"]["reowed_pre_freeze_cells"] == engines
    assert plan["counts"]["cell_ledger"]["dropped_already_predicted_cells"] == 0
    assert plan["counts"]["cell_ledger"]["would_mint_cells"] == engines
    assert {r["event_id"] for r in plan["reowed_pre_freeze"]} == {BASELINE_EVENT}
    assert "retired process digest" in plan["reowed_pre_freeze"][0]["reason"]
    assert "RE-OWED under the pre-freeze rule" in _flat(result.stderr)


def test_an_event_with_one_missing_engine_and_two_retired_ones_re_owes_both_arms(
    tmp_path: Path,
) -> None:
    """The two arms overlap per event and stay disjoint per cell. This is the state
    a run leaves when one engine quota-fails before a re-bless, and taking only the
    never-predicted arm would mint that engine, stamp it blessed, and leave its
    rivals de-counted — a one-engine frozen cohort, which is the very shape the
    cohort-completion bound exists to refuse."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
    predictors = [p.id for p in enabled_predictors(PREDICTORS)]
    missing, *retired = predictors
    for predictor_id in retired:
        seed_prediction(data, "scotus", 1, BASELINE_EVENT, predictor_id=predictor_id)

    entry = _backlog(db, data).entries[0]
    # The event is owed on both grounds, and is listed once.
    assert entry.events == (BASELINE_EVENT,)
    assert entry.reopened == (BASELINE_EVENT,)

    # And the fan-out mints every engine: the missing one because it has no
    # cell, the other two because theirs are out of frozen scope.
    case = CaseRequest("scotus", 1, entry.events, reopen_events=entry.reopened)
    minted = predict_matrix(PREDICTORS, [case], "RID", data)["include"]
    assert {cell["predictor_id"] for cell in minted} == {missing, *retired}


def test_a_distribution_event_with_no_conference_at_all_is_not_re_owed(tmp_path: Path) -> None:
    """The distribution moment has not happened, so there is no cell of it to
    re-mint — the same information-set precondition the fan-out's own premature-cell
    refusal applies. Only the live channel parses that column, so this is the limb
    most likely to decide real yield."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, event_id=BASELINE_EVENT, conference=None)
    _retired_cohort(data, 1)

    assert _backlog(db, data).case_ids == ()


def test_an_undeclared_event_is_not_re_owed_however_retired_its_cohort(tmp_path: Path) -> None:
    """The register cannot place an entry-pinned or legacy event in a cohort, so
    the rule leaves it alone rather than guessing one. The rule ADDS admissions to
    a version-blind backlog, so an event it cannot classify is refused."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    # `EVENT` is this module's undeclared baseline id: `moments.spec_for` has no
    # row for it, which is exactly the case under test.
    _open_case(db, "scotus", 1, event_id=EVENT, conference=FUTURE_CONFERENCE)
    _retired_cohort(data, 1, event_id=EVENT)

    assert _backlog(db, data).case_ids == ()


def test_cap_reached_is_set_when_the_budget_fills_with_re_owed_work(tmp_path: Path) -> None:
    """The cap's second stopping shape. The walk no longer breaks outright once the
    budget is full of re-owed cases — it keeps looking for never-predicted work —
    but it stops evaluating re-predict grounds, so the counts past that point are
    censored and the flag has to say so."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    for docket in (1, 2):
        _open_case(db, "scotus", docket, event_id=BASELINE_EVENT, conference=FUTURE_CONFERENCE)
        _retired_cohort(data, docket)

    uncapped = _backlog(db, data)
    assert uncapped.case_ids == ("scotus/1", "scotus/2")
    assert not uncapped.cap_reached

    capped = _backlog(db, data, cap=1)
    assert capped.case_ids == ("scotus/1",)
    assert capped.cap_reached
