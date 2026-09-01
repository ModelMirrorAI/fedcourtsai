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
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.pull import PredictBacklog, derive_predict_backlog
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import CellFailure, Disposition, EventKind, Stage
from fedcourtsai.serialize import write_json
from tests.conftest import seed_prediction

runner = CliRunner()

PREDICTORS = Path("config/predictors.yaml")
_REPO_CONFIG = Path(__file__).resolve().parents[1] / "config"

#: The case-baseline cert event every fixture case carries — the same id the
#: predict matrix tests use, so forecastability is exercised on the real moment.
EVENT = "evt-petition-cert"


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
) -> None:
    """Seed one predict candidate: a distributed SCOTUS row, an open event, documents.

    ``distribution_count`` is not decoration — the case-baseline moment *is* the
    first distribution, so an undistributed petition has no forecastable
    baseline at all (``store._premature_distribution_cell``) and would drop out
    before any predicate this module tests.
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
                )
            ],
        )
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
    today: date = date(2026, 7, 20),
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
    today: date = date(2026, 7, 20),
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
            today=today or date(2026, 7, 20),
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


def test_an_unprovisioned_case_is_held_and_admitted_once_provisioned(tmp_path: Path) -> None:
    """The provisioning predicate. run-pull provisions a case's filed-document text
    at queue time and this scan cannot fetch, so a queued-but-unprovisioned case is
    **held** rather than minted as a cell whose record/ carries no petition text.
    Held, not errored: the next pull window provisions it and it becomes
    derivable."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False)

    assert _derive(db, data) == (), "an unprovisioned case is not a forecast we can mint"

    _provision(db, "scotus/1")
    assert _derive(db, data) == ("scotus/1",), "provisioning admits it, one window later at most"


def test_a_backlog_held_on_provisioning_is_counted_not_silently_empty(tmp_path: Path) -> None:
    """The held cases are reported, because the provisioning predicate is the one
    admission rule whose refusals are expected to clear on their own. Without the
    count, a backlog every one of whose cases is waiting on run-pull is
    indistinguishable from a drained queue — the same conflation the absent-corpus
    refusal exists to prevent, one predicate over."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _open_case(db, "scotus", 1, provisioned=False)
    _open_case(db, "scotus", 2, provisioned=False)

    blocked = _backlog(db, data)
    assert blocked.entries == ()
    assert blocked.held_unprovisioned == 2

    # Provision one: it derives, and only the still-unprovisioned case is held.
    _provision(db, "scotus/1")
    partial = _backlog(db, data)
    assert partial.case_ids == ("scotus/1",)
    assert partial.held_unprovisioned == 1

    # A genuinely drained backlog is the other reading, and says so.
    _provision(db, "scotus/2")
    for docket in (1, 2):
        for predictor in enabled_predictors(PREDICTORS):
            seed_prediction(data, "scotus", docket, EVENT, predictor_id=predictor.id)
    drained = _backlog(db, data)
    assert drained.entries == ()
    assert drained.held_unprovisioned == 0


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
        _open_case(corpus.corpus_db_path(corpus_root), "scotus", docket, provisioned=provisioned)
    return {
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
    }


def test_predict_matrix_with_no_body_file_derives_its_cases_from_the_backlog(
    tmp_path: Path,
) -> None:
    """The scheduled mode: given no trigger at all, the fan-out is the forecasts
    committed state still owes — the derivation a run-predict schedule consumes
    instead of a handoff from the pull run."""
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
    assert "held 2 case(s) with no stored documents" in _flat(result.stderr)


def test_the_cli_stays_quiet_when_nothing_is_held(tmp_path: Path) -> None:
    """The complement, so the line means something: a fully provisioned backlog
    reports no held cases at all rather than a zero."""
    env = _cli_env(tmp_path, 24001)

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    assert "no stored documents" not in _flat(result.stderr)


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


def test_the_backlog_mode_refuses_an_absent_corpus(tmp_path: Path) -> None:
    """For an unattended lane, "nothing is owed" and "no corpus on disk" must not
    be the same output — an empty fan-out from a runner that never pulled reads
    exactly like a drained backlog."""
    env = _cli_env(tmp_path, 24001)
    corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"])).unlink()

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code != 0
    assert "corpus-pull" in _flat(result.output)
