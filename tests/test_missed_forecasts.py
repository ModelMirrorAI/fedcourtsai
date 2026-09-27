"""The missed-forecast monitor — classify resolved events no forecast covered.

:func:`fedcourtsai.pipeline.missed.scan_predictionless_resolutions` reads each
SCOTUS event resolved in a window and, where an enabled predictor's forecast is
missing, files it as **declined** by design (with the reason) or **missed**.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import date, time, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.missed import (
    PREDICT_ROUND_TIMES_UTC,
    PredictionlessReport,
    had_a_scheduled_round,
    scan_predictionless_resolutions,
)
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import Disposition, EventKind, Outcome, Stage
from fedcourtsai.serialize import write_json
from tests.conftest import seed_prediction

runner = CliRunner()

_ROOT = Path(__file__).resolve().parents[1]
PREDICTORS = _ROOT / "config" / "predictors.yaml"

CERT_EVENT = "evt-petition-disposition"
INTERIM_EVENT = "evt-motion-disposition"
OPENED = date(2026, 9, 1)
RESOLVED = date(2026, 9, 10)
SINCE = date(2026, 9, 1)
UNTIL = date(2026, 9, 27)


def _resolved_case(  # noqa: PLR0913 - one fixture knob per classification rule
    db: Path,
    data_root: Path,
    docket: int,
    *,
    event_id: str = CERT_EVENT,
    kind: EventKind = EventKind.petition,
    stage: Stage | None = Stage.cert,
    docket_number: str = "",
    selected: bool = True,
    scored: bool = True,
    excluded: bool = False,
    opened_at: date | None = OPENED,
    resolved_at: date = RESOLVED,
    outcome: bool = True,
    date_decided: date | None = None,
    polled_on: date | None = None,
) -> str:
    """Seed one resolved SCOTUS event: a corpus row and event, and its ledger outcome.

    Every enabled predictor is also given one early committed prediction on an
    unrelated docket, so each is owed any event resolved after it — the monitor
    declines a gap only a not-yet-enabled predictor leaves.
    """
    _enable_all(data_root)
    case_id = f"scotus/{docket}"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=docket_number,
                    distribution_count=1,
                    salience_score=0.9 if scored else None,
                    salience_version="sal-v1" if scored else None,
                    salience_selected=selected,
                    date_decided=date_decided,
                    last_live_polled=polled_on,
                    # Read only on an application-form docket, where a
                    # substantive ask is what keeps it in interim scope.
                    application_kind="substantive" if docket_number else None,
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
                    court="scotus",
                    kind=kind,
                    stage=stage,
                    title="The event",
                    opened_at=opened_at,
                    resolved=True,
                )
            ],
        )
    if not outcome:
        return case_id
    write_json(
        CasePaths(data_root, "scotus", docket).event(event_id).outcome,
        Outcome(
            case_id=case_id,
            event_id=event_id,
            resolved_at=resolved_at,
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    return case_id


#: An unrelated docket every predictor's enabling prediction is committed on.
_ENABLING_DOCKET = 999_999


def _enable_all(data_root: Path, *, run_id: str = "20260101T000000Z") -> None:
    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(
            data_root,
            "scotus",
            _ENABLING_DOCKET,
            CERT_EVENT,
            predictor_id=predictor.id,
            run_id=run_id,
        )


def _scan(db: Path, data_root: Path, *, since: date = SINCE) -> PredictionlessReport:
    with corpus.connect_readonly(db) as conn:
        return scan_predictionless_resolutions(
            conn, data_root, PREDICTORS, since=since, until=UNTIL
        )


def _by_case(report: PredictionlessReport) -> dict[str, tuple[str, str]]:
    return {e.case_id: (e.verdict.value, e.reason) for e in report.events}


def test_a_selected_in_scope_event_resolved_unforecast_is_missed(tmp_path: Path) -> None:
    """The class the monitor exists for: funded, in scope, a forecastable moment,
    open across scheduled rounds — and no prediction. Missed, not declined."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1)

    report = _scan(db, data)

    assert _by_case(report) == {"scotus/1": ("missed", "owed_and_unforecast")}
    (event,) = report.missed
    assert event.detail == "no committed prediction"
    assert not event.partial
    assert event.missing_predictors == tuple(p.id for p in enabled_predictors(PREDICTORS))


def test_an_unselected_event_is_declined_as_not_funded(tmp_path: Path) -> None:
    """The salience gate's decision is by design: the same event on a case the
    selection pass did not fund is declined, with that reason."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, selected=False)

    report = _scan(db, data)

    assert _by_case(report) == {"scotus/1": ("declined", "not_funded")}
    assert report.missed == ()


def test_each_decline_reason_is_named(tmp_path: Path) -> None:
    """Out of scope, a moment the fan-out never forecasts, and an event that
    resolved before a scheduled round could certainly have run are each declined
    with their own reason."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, excluded=True)
    # A motion on a cert docket: tracked for its ground truth, never forecast.
    _resolved_case(db, data, 2, event_id="evt-motion-stay", kind=EventKind.motion, stage=None)
    _resolved_case(db, data, 3, opened_at=RESOLVED - timedelta(days=1))

    assert _by_case(_scan(db, data)) == {
        "scotus/1": ("declined", "out_of_scope"),
        "scotus/2": ("declined", "non_forecastable_moment"),
        "scotus/3": ("declined", "resolved_before_a_round"),
    }


def test_an_interim_application_event_is_classified_on_its_own_form(tmp_path: Path) -> None:
    """An application's arrival moment is forecastable on an application docket, so
    a selected one resolved unforecast is missed — the class every one of the
    audit's misses belonged to."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(
        db,
        data,
        1,
        event_id=INTERIM_EVENT,
        kind=EventKind.motion,
        stage=Stage.interim,
        docket_number="26A308",
    )

    assert _by_case(_scan(db, data)) == {"scotus/1": ("missed", "owed_and_unforecast")}


def test_a_partial_gap_names_the_missing_predictor(tmp_path: Path) -> None:
    """Some engines forecast the event, one did not: a partial gap, missed, with the
    absent predictor and its recorded failures named."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1)
    predictors = [p.id for p in enabled_predictors(PREDICTORS)]
    for pid in predictors[1:]:
        seed_prediction(data, "scotus", 1, CERT_EVENT, predictor_id=pid, frozen=True)

    (event,) = _scan(db, data).events

    assert event.verdict.value == "missed"
    assert event.partial
    assert event.missing_predictors == (predictors[0],)
    assert event.detail == f"missing {predictors[0]}"


def test_a_partial_gap_is_not_excused_by_the_round_rule(tmp_path: Path) -> None:
    """An event open a single day would be declined as a full gap, but a partial
    gap proves a round reached it — its sibling engines' cells landed — so the
    missing engine is a miss. The shape of a cell that failed on a fast docket."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, opened_at=RESOLVED - timedelta(days=1))
    _resolved_case(db, data, 2, opened_at=RESOLVED - timedelta(days=1))
    predictors = [p.id for p in enabled_predictors(PREDICTORS)]
    for pid in predictors[1:]:
        seed_prediction(data, "scotus", 1, CERT_EVENT, predictor_id=pid, frozen=True)

    assert _by_case(_scan(db, data)) == {
        "scotus/1": ("missed", "owed_and_unforecast"),
        "scotus/2": ("declined", "resolved_before_a_round"),
    }


def test_a_fully_covered_or_out_of_window_event_is_not_listed(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1)
    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(data, "scotus", 1, CERT_EVENT, predictor_id=predictor.id)
    _resolved_case(db, data, 2, opened_at=date(2026, 6, 1), resolved_at=date(2026, 6, 20))

    report = _scan(db, data)

    assert report.events == ()
    assert _scan(db, data, since=date(2026, 6, 1)).events[0].case_id == "scotus/2"


@pytest.mark.parametrize(
    ("opened", "resolved", "had"),
    [
        (date(2026, 9, 10), date(2026, 9, 10), False),  # same day
        (date(2026, 9, 9), date(2026, 9, 10), False),  # next day: no round certainly between
        (date(2026, 9, 8), date(2026, 9, 10), True),  # a whole day's rounds between
    ],
)
def test_the_round_rule_reads_the_open_span_at_its_narrowest(
    opened: date, resolved: date, had: bool
) -> None:
    assert had_a_scheduled_round(opened, resolved) is had


def test_the_round_times_mirror_the_predict_workflow_schedule() -> None:
    """The rule's round times are a copy of run-predict's crons; a cron change not
    mirrored here would skew which events count as open across a round. Only
    daily crons (``M H * * *``) are read — a weekday-only or otherwise restricted
    schedule would not match the pattern and would fail the non-empty check, and
    the rule itself assumes the rounds run every day."""
    workflow = (_ROOT / ".github" / "workflows" / "run-predict.yml").read_text()
    crons = re.findall(r'-\s*cron:\s*"(\d+) (\d+) \* \* \*"', workflow)
    assert crons, "run-predict.yml carries no daily cron this test can read"
    assert sorted(time(int(h), int(m)) for m, h in crons) == sorted(PREDICT_ROUND_TIMES_UTC)


def _cli_env(tmp_path: Path) -> dict[str, str]:
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    for name in ("predictors.yaml", "evaluators.yaml"):
        (config_root / name).write_text((_ROOT / "config" / name).read_text())
    (config_root / "tracking.yaml").write_text("predict:\n  scope: scotus_docket\n")
    return {
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
    }


def _flat(output: str) -> str:
    return " ".join(re.sub(r"\x1b\[[0-9;]*m", "", output).split())


def test_the_evaluate_plan_splits_declined_from_missed_and_warns_on_misses(
    tmp_path: Path,
) -> None:
    """Both evaluate commands run the monitor in the backlog mode: each missed event
    is a `::warning::` naming it, and the plan carries the split at event grain."""
    env = _cli_env(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    today = date.today()
    _resolved_case(db, data, 1, opened_at=today - timedelta(days=5), resolved_at=today)
    _resolved_case(
        db, data, 2, selected=False, opened_at=today - timedelta(days=5), resolved_at=today
    )

    matrix = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)
    assert matrix.exit_code == 0, matrix.output
    stderr = _flat(matrix.stderr)
    assert f"::warning::missed forecast: scotus/1 {CERT_EVENT} resolved" in stderr
    assert "scotus/2" not in stderr.split("::warning::", 1)[1]

    plan = runner.invoke(app, ["evaluate-plan", "--run-id", "RID"], env=env)
    assert plan.exit_code == 0, plan.output
    document = json.loads(plan.stdout)
    counts = document["counts"]["predictionless_resolutions"]
    assert counts["missed_events"] == 1
    assert counts["declined_events"] == 1
    assert counts["declined_not_funded_events"] == 1
    assert [e["case_id"] for e in document["predictionless_resolutions"]["missed"]] == ["scotus/1"]
    assert [e["reason"] for e in document["predictionless_resolutions"]["declined"]] == [
        "not_funded"
    ]


def test_missed_since_backfills_the_window(tmp_path: Path) -> None:
    env = _cli_env(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1)  # resolved 2026-09-10, outside the default lookback

    backfill = runner.invoke(
        app, ["evaluate-plan", "--run-id", "RID", "--missed-since", "2026-07-01"], env=env
    )

    assert backfill.exit_code == 0, backfill.output
    counts = json.loads(backfill.stdout)["counts"]["predictionless_resolutions"]
    assert counts["since"] == "2026-07-01"
    assert counts["missed_events"] == 1


def test_missed_since_is_refused_with_named_cases(tmp_path: Path) -> None:
    env = _cli_env(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _resolved_case(db, tmp_path / "data", 1)

    refused = runner.invoke(
        app,
        [
            "evaluate-plan",
            "--run-id",
            "RID",
            "--court",
            "scotus",
            "--docket",
            "1",
            "--missed-since",
            "2026-07-01",
        ],
        env=env,
    )

    assert refused.exit_code != 0
    assert "backlog mode only" in _flat(refused.output)


def test_a_resolved_event_with_no_ledger_directory_is_seen_and_named(tmp_path: Path) -> None:
    """The monitor is driven from the corpus, not the ledger: an event the corpus
    records resolved whose case never reached the ledger at all — no outcome, no
    prediction — is dated from the corpus row, classified, and named as having no
    outcome record, not passed over."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(
        db,
        data,
        209,
        event_id=INTERIM_EVENT,
        kind=EventKind.motion,
        stage=Stage.interim,
        docket_number="26A209",
        outcome=False,
        date_decided=RESOLVED,
    )

    report = _scan(db, data)

    (event,) = report.missed
    assert event.case_id == "scotus/209"
    assert event.date_source.value == "corpus_decision_date"
    assert event.resolved_at == RESOLVED
    assert "no outcome.json" in event.detail
    assert [u.case_id for u in report.no_outcome_record] == ["scotus/209"]
    assert report.counts_json()["no_outcome_record_on_selected_row_events"] == 1


def test_an_event_dated_only_by_observation_is_placed_and_one_undatable_is_named(
    tmp_path: Path,
) -> None:
    """No outcome and no decision date: the row's newest observation dates it (an
    upper bound). No date at all: counted all-time, and named where selected."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, outcome=False, polled_on=RESOLVED)
    _resolved_case(db, data, 2, outcome=False)

    report = _scan(db, data)

    assert [(e.case_id, e.date_source.value) for e in report.events] == [
        ("scotus/1", "last_observed")
    ]
    assert report.undated_all_time == 1
    assert [u.case_id for u in report.undated_selected] == ["scotus/2"]
    detail = report.detail_json()
    assert [u["case_id"] for u in detail["undated_on_selected_row"]] == ["scotus/2"]


def test_a_never_scored_in_scope_event_is_a_miss_not_a_decline(tmp_path: Path) -> None:
    """A case the salience pass never scored had no funding decision at all — a
    pipeline failure, reported as a miss with its own reason and count."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, selected=False, scored=False)

    report = _scan(db, data)

    assert _by_case(report) == {"scotus/1": ("missed", "not_scored")}
    assert report.counts_json()["missed_not_scored_events"] == 1


def test_a_predictor_enabled_after_the_resolution_is_not_owed_it(tmp_path: Path) -> None:
    """Enabling an engine must not turn every event resolved before it into a miss:
    a predictor is owed an event only if it had forecast something by then."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    predictors = [p.id for p in enabled_predictors(PREDICTORS)]
    # Two events: one every engine covered except a newcomer, one nobody covered.
    _resolved_case(db, data, 1)
    _resolved_case(db, data, 2)
    newcomer = predictors[0]
    # Replace the fixture's early enabling prediction for the newcomer with a late one.
    shutil.rmtree(
        CasePaths(data, "scotus", _ENABLING_DOCKET).event(CERT_EVENT).predictions_dir / newcomer
    )
    seed_prediction(
        data,
        "scotus",
        _ENABLING_DOCKET,
        CERT_EVENT,
        predictor_id=newcomer,
        run_id="20260920T000000Z",
    )
    for pid in predictors[1:]:
        seed_prediction(data, "scotus", 1, CERT_EVENT, predictor_id=pid, frozen=True)

    report = _scan(db, data)

    assert _by_case(report) == {
        "scotus/1": ("declined", "predictor_not_enabled"),
        "scotus/2": ("missed", "owed_and_unforecast"),
    }
    (missed,) = report.missed
    assert newcomer not in missed.missing_predictors


def test_an_out_of_scope_decline_on_a_selected_row_is_named_a_contradiction(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, excluded=True)
    _resolved_case(db, data, 2, excluded=True, selected=False)

    report = _scan(db, data)

    assert [e.case_id for e in report.scope_contradictions] == ["scotus/1"]
    assert report.counts_json()["declined_out_of_scope_on_selected_row_events"] == 1


def test_an_open_merits_proceeding_funds_every_event_of_the_case(tmp_path: Path) -> None:
    """The walk funds a case with an open merits event whatever its salience, and so
    does the monitor: an unselected case's cert-stage event resolved while its merits
    event was open is owed."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_case(db, data, 1, selected=False)
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-order-judgment",
                    case_id="scotus/1",
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                    title="Judgment",
                    opened_at=OPENED,
                    resolved=False,
                )
            ],
        )

    assert _by_case(_scan(db, data))["scotus/1"] == ("missed", "owed_and_unforecast")


def test_a_monitor_that_raises_degrades_to_a_warning_and_the_matrix_still_emits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*args: object, **kwargs: object) -> PredictionlessReport:
        raise RuntimeError("scan exploded")

    monkeypatch.setattr(cli, "scan_predictionless_resolutions", boom)
    env = _cli_env(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _resolved_case(db, tmp_path / "data", 1)

    matrix = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)
    assert matrix.exit_code == 0, matrix.output
    assert "include" in json.loads(matrix.stdout)
    assert "::warning::missed-forecast monitor failed: RuntimeError: scan exploded" in _flat(
        matrix.stderr
    )

    plan = runner.invoke(app, ["evaluate-plan", "--run-id", "RID"], env=env)
    assert plan.exit_code == 0, plan.output
    document = json.loads(plan.stdout)
    assert document["counts"]["predictionless_resolutions"] is None
    assert document["predictionless_resolutions"] == {"error": "RuntimeError: scan exploded"}
    assert "::warning::" not in plan.stderr
    assert "warning: missed-forecast monitor failed" in _flat(plan.stderr)
