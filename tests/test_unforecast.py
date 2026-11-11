"""The unforecast-outcomes census: the grants and application rulings no forecast preceded."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import unforecast
from fedcourtsai.pipeline.unforecast import (
    FederalSignal,
    UnforecastReason,
    UnforecastReport,
    unforecast_outcomes,
)
from fedcourtsai.schemas import Disposition
from tests.conftest import seed_prediction

SINCE = date(2026, 10, 1)
UNTIL = date(2026, 10, 31)
FILED = date(2026, 6, 1)
GRANTED = date(2026, 10, 13)
EVENT = "evt-petition-disposition"


def _row(  # noqa: PLR0913 - one fixture knob per rule
    conn: sqlite3.Connection,
    docket: int,
    docket_number: str,
    *,
    disposition: Disposition = Disposition.granted,
    resolved: date = GRANTED,
    filed: date = FILED,
    case_name: str = "Acme Corp. v. Roe",
    selected: bool = False,
    scored: bool = True,
    counsel: list[corpus.CounselEntry] | None = None,
    application_kind: str | None = None,
    referred_to_court: bool | None = None,
) -> str:
    case_id = f"scotus/{docket}"
    application = corpus.is_scotus_application_form(docket_number)
    granted = disposition in (Disposition.granted, Disposition.gvr)
    corpus.upsert_rows(
        conn,
        [
            corpus.CorpusRow(
                case_id=case_id,
                court="scotus",
                docket_number=docket_number,
                case_name=case_name,
                disposition=disposition,
                date_filed=filed,
                date_cert_granted=resolved if granted and not application else None,
                date_cert_denied=resolved if not granted and not application else None,
                date_decided=resolved if application else None,
                salience_version="sal-v8" if scored else None,
                salience_score=0.02 if scored else None,
                salience_selected=selected,
                counsel=counsel or [],
                application_kind=application_kind,
                referred_to_court=referred_to_court,
            )
        ],
    )
    return case_id


def _census(db: Path, data: Path) -> UnforecastReport:
    with corpus.connect_readonly(db) as conn:
        return unforecast_outcomes(conn, data, since=SINCE, until=UNTIL)


def _db(tmp_path: Path) -> tuple[Path, Path]:
    return corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"


def test_a_grant_with_no_prior_forecast_is_named_with_its_reason(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101")  # scored, unselected
        _row(conn, 2, "26-102", selected=True)
        _row(conn, 3, "26-103", scored=False)
        _row(conn, 4, "26-104", filed=GRANTED)  # no round could reach it
        _row(conn, 5, "26-105", disposition=Disposition.denied)  # not an outcome watched
        _row(conn, 6, "26-106", resolved=date(2026, 11, 5))  # outside the window

    report = _census(db, data)

    assert {e.docket_number: e.reason for e in report.cert_unforecast} == {
        "26-101": UnforecastReason.not_selected,
        "26-102": UnforecastReason.selected_unforecast,
        "26-103": UnforecastReason.not_scored,
        "26-104": UnforecastReason.resolved_before_a_round,
    }
    assert (report.window.outcomes, report.window.forecast) == (4, 0)
    assert report.window.reachable_outcomes == 3  # less the one no round could reach


def test_a_forecast_counts_only_when_dated_on_or_before_the_outcome(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", selected=True)
        _row(conn, 2, "26-102", selected=True)
        _row(conn, 3, "26-103", selected=True)
    seed_prediction(data, "scotus", 1, EVENT, run_id="20261001T141200Z")
    seed_prediction(data, "scotus", 2, EVENT, run_id="20261013T141200Z")  # the same day
    seed_prediction(data, "scotus", 3, "evt-order-judgment", run_id="20261020T141200Z")  # after

    report = _census(db, data)

    assert [e.docket_number for e in report.cert_unforecast] == ["26-103"]
    assert (report.window.outcomes, report.window.forecast) == (3, 2)
    assert report.window.recall == pytest.approx(2 / 3)


def test_ifp_grants_are_listed_apart_and_kept_out_of_the_recall(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-5343", disposition=Disposition.gvr)

    report = _census(db, data)

    assert report.cert_unforecast == []
    assert [e.docket_number for e in report.ifp_grants_unforecast] == ["26-5343"]
    assert report.window.outcomes == 0
    assert report.window.recall is None
    assert report.alarms == []


def test_an_unforecast_grant_in_the_federal_band_alarms(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", case_name="United States v. Roe")
        _row(conn, 2, "26-102", case_name="United States v. Doe", filed=GRANTED)

    report = _census(db, data)

    assert [e.band for e in report.cert_unforecast] == ["federal", "federal"]
    assert report.alarms == ["26-101: granted with no forecast, in the federal band"]


def test_a_federal_party_the_caption_does_not_lead_with_alarms(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    party = corpus.CounselEntry(
        party="United States", attorney="A. Lawyer", role=corpus.CounselRole.petitioner
    )
    respondent = corpus.CounselEntry(
        party="United States", attorney="A. Lawyer", role=corpus.CounselRole.respondent
    )
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", counsel=[party])
        _row(conn, 2, "26-102", counsel=[respondent])

    report = _census(db, data)
    by_docket = {e.docket_number: e for e in report.cert_unforecast}

    assert by_docket["26-101"].federal_signals == [FederalSignal.federal_petitioner_party]
    assert by_docket["26-102"].federal_signals == []
    assert len(report.alarms) == 1
    assert report.alarms[0].startswith("26-101: granted with no forecast, outside the federal")


def test_term_to_date_recall_alarms_only_past_the_minimum(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        for n in range(1, 4):
            _row(conn, n, f"26-10{n}")

    assert _census(db, data).alarms == []  # 0 of 3, under the minimum

    monkeypatch.setattr(unforecast, "RECALL_ALARM_MIN_OUTCOMES", 3)
    report = _census(db, data)

    assert report.term_to_date.since == date(2026, 10, 1)
    assert report.alarms == ["Term-to-date reachable grant recall 0.000 (0/3) is below 0.70"]


def test_the_term_to_date_span_reaches_back_before_the_window(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", resolved=date(2026, 10, 5))
        _row(conn, 2, "26-102", resolved=date(2026, 10, 20))
    with corpus.connect_readonly(db) as conn:
        report = unforecast_outcomes(conn, data, since=date(2026, 10, 15), until=date(2026, 10, 31))

    assert [e.docket_number for e in report.cert_unforecast] == ["26-102"]
    assert report.window.outcomes == 1
    assert report.term_to_date.outcomes == 2


def test_applications_are_watched_when_substantive_or_referred(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26A101", application_kind="substantive", referred_to_court=False)
        _row(conn, 2, "26A102", application_kind="unknown", referred_to_court=True)
        _row(conn, 3, "26A103", application_kind="extension", referred_to_court=False)
        _row(
            conn,
            4,
            "26A104",
            disposition=Disposition.denied,
            application_kind="substantive",
            selected=True,
        )
    seed_prediction(data, "scotus", 4, "evt-motion-disposition", run_id="20261005T141200Z")

    report = _census(db, data)

    assert report.interim_outcomes == 3
    assert {e.docket_number: e.referred_not_substantive for e in report.interim_unforecast} == {
        "26A101": False,
        "26A102": True,
    }
    assert report.cert_unforecast == []


def test_the_cli_exits_3_on_an_alarm_and_0_when_quiet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _row(conn, 1, "26-101", case_name="United States v. Roe")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    window = ["--since", SINCE.isoformat(), "--until", UNTIL.isoformat()]

    result = CliRunner().invoke(app, ["unforecast-outcomes", *window])

    assert result.exit_code == 3, result.output
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["cert_unforecast"][0]["docket_number"] == "26-101"
    assert len(payload["alarms"]) == 1

    seed_prediction(tmp_path / "data", "scotus", 1, EVENT, run_id="20261001T141200Z")
    quiet = CliRunner().invoke(app, ["unforecast-outcomes", *window])
    assert quiet.exit_code == 0, quiet.output

    reversed_window = CliRunner().invoke(
        app, ["unforecast-outcomes", "--since", "2026-11-01", "--until", "2026-10-01"]
    )
    assert reversed_window.exit_code == 2


def test_a_scope_refused_grant_is_named_and_left_out_of_the_reachable_recall(
    tmp_path: Path,
) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101")
        conn.execute("UPDATE cases SET predict_excluded = 1 WHERE case_id = 'scotus/1'")
        conn.commit()

    report = _census(db, data)

    assert [e.reason for e in report.cert_unforecast] == [UnforecastReason.out_of_scope]
    assert (report.window.outcomes, report.window.reachable_outcomes) == (1, 0)
    assert report.window.reachable_recall is None


def test_a_partial_grant_and_a_grant_with_no_cert_date_are_left_out(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", disposition=Disposition.granted_in_part)
        _row(conn, 2, "26-102")
        conn.execute(
            "UPDATE cases SET date_cert_granted = NULL, date_decided = ? WHERE case_id = ?",
            (GRANTED.isoformat(), "scotus/2"),
        )
        conn.commit()

    report = _census(db, data)

    assert report.cert_unforecast == []
    assert report.window.outcomes == 0


def test_a_signal_on_a_grant_no_round_could_reach_raises_nothing(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    party = corpus.CounselEntry(
        party="United States", attorney="A. Lawyer", role=corpus.CounselRole.petitioner
    )
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", counsel=[party], filed=GRANTED)

    report = _census(db, data)

    assert report.cert_unforecast[0].federal_signals == [FederalSignal.federal_petitioner_party]
    assert report.alarms == []


def test_the_term_opens_in_october_of_the_year_before_a_spring_window(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26-101", resolved=date(2026, 9, 29))  # the outgoing Term
        _row(conn, 2, "26-102", resolved=date(2026, 10, 13))
        _row(conn, 3, "26-103", resolved=date(2027, 3, 2))
    with corpus.connect_readonly(db) as conn:
        report = unforecast_outcomes(conn, data, since=date(2027, 3, 1), until=date(2027, 3, 31))

    assert report.term_to_date.since == date(2026, 10, 1)
    assert report.term_to_date.outcomes == 2
    assert report.window.outcomes == 1


def test_an_application_kind_outside_the_vocabulary_is_not_admitted(tmp_path: Path) -> None:
    db, data = _db(tmp_path)
    with corpus.connect(db) as conn:
        _row(conn, 1, "26A101", application_kind="substantive")
        _row(conn, 2, "26A102", application_kind="substantive", referred_to_court=True)
        conn.execute("UPDATE cases SET application_kind = 'novel' WHERE case_id LIKE 'scotus/%'")
        conn.commit()

    report = _census(db, data)

    assert [e.docket_number for e in report.interim_unforecast] == ["26A102"]
    assert report.interim_unforecast[0].referred_not_substantive


def test_the_cli_refuses_an_unreadable_date_and_a_missing_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))

    assert CliRunner().invoke(app, ["unforecast-outcomes", "--since", "soon"]).exit_code == 2
    assert CliRunner().invoke(app, ["unforecast-outcomes"]).exit_code == 1
