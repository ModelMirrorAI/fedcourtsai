"""The federal-label cross-check: pending petitions a looser reading places federal."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.federal_label import FederalLabelReport, federal_label_check
from fedcourtsai.pipeline.unforecast import FederalSignal
from fedcourtsai.schemas import Disposition

TODAY = date(2026, 11, 11)
SOON = TODAY + timedelta(days=9)


def _party(party: str = "United States") -> corpus.CounselEntry:
    return corpus.CounselEntry(
        party=party, attorney="A. Lawyer", role=corpus.CounselRole.petitioner
    )


def _petition(
    conn: sqlite3.Connection,
    docket: int,
    docket_number: str,
    *,
    case_name: str = "Acme Corp. v. Roe",
    counsel: list[corpus.CounselEntry] | None = None,
    disposition: Disposition | None = None,
    conference: date | None = None,
) -> None:
    corpus.upsert_rows(
        conn,
        [
            corpus.CorpusRow(
                case_id=f"scotus/{docket}",
                court="scotus",
                docket_number=docket_number,
                case_name=case_name,
                date_filed=date(2026, 9, 1),
                disposition=disposition,
                date_cert_denied=TODAY if disposition else None,
                counsel=counsel or [],
                distributed_for_conference=conference,
            )
        ],
    )


def _check(db: Path) -> FederalLabelReport:
    with corpus.connect_readonly(db) as conn:
        return federal_label_check(conn, today=TODAY)


def test_a_pending_petition_with_a_federal_petitioner_party_is_flagged(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "26-101", counsel=[_party()])
        _petition(conn, 2, "26-102", counsel=[_party("Acme Corp.")])
        _petition(conn, 3, "26-103", case_name="United States v. Roe")  # already federal
        _petition(conn, 4, "26-104", counsel=[_party()], disposition=Disposition.denied)
        _petition(conn, 5, "26-5105", counsel=[_party()])  # in forma pauperis

    report = _check(db)

    assert (report.pending, report.federal) == (3, 1)
    assert [(f.docket_number, f.signals) for f in report.flagged] == [
        ("26-101", [FederalSignal.federal_petitioner_party])
    ]
    assert report.alarms == []


def test_a_relators_caption_is_not_flagged_for_its_united_states_party(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(
            conn, 1, "26-101", case_name="United States ex rel. Doe v. Acme", counsel=[_party()]
        )

    assert _check(db).flagged == []


def _office(party: str = "Acme Warden") -> corpus.CounselEntry:
    # The roster places this attorney in the office from 2025-04-04.
    return corpus.CounselEntry(
        party=party, attorney="D. John Sauer", role=corpus.CounselRole.petitioner
    )


def test_the_alarm_is_an_office_flag_on_an_unselected_petition(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "26-101", counsel=[_office()], conference=SOON)
        _petition(conn, 2, "26-102", counsel=[_office()], conference=TODAY - timedelta(days=3))
        _petition(conn, 3, "26-103", counsel=[_office()])
        _petition(conn, 4, "26-104", counsel=[_party()])  # the party signal never alarms
        conn.execute("UPDATE cases SET salience_selected = 1 WHERE case_id = 'scotus/3'")
        conn.commit()

    report = _check(db)

    assert [f.days_to_conference for f in report.flagged] == [9, -3, None, None]
    assert FederalSignal.sg_office_counsel in report.flagged[0].signals
    assert [a.split(":")[0] for a in report.alarms] == ["26-101", "26-102"]


def test_an_old_open_docket_is_not_pending(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "24-101", counsel=[_party()])  # two Terms back: in
        _petition(conn, 2, "23-101", counsel=[_party()])
        _petition(conn, 3, "98-101", counsel=[_party()])

    report = _check(db)

    assert report.pending == 1
    assert [f.docket_number for f in report.flagged] == ["24-101"]


def test_the_cli_reports_and_refuses_an_unregistered_scorer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")

    assert CliRunner().invoke(app, ["federal-label-check"]).exit_code == 1

    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _petition(conn, 1, "26-101", counsel=[_party()])

    result = CliRunner().invoke(app, ["federal-label-check"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert [f["docket_number"] for f in payload["flagged"]] == ["26-101"]

    refused = CliRunner().invoke(app, ["federal-label-check", "--salience-version", "sal-v0"])
    assert refused.exit_code == 2

    reread = CliRunner().invoke(app, ["federal-label-check", "--salience-version", "sal-v4"])
    assert reread.exit_code == 0, reread.output
    assert json.loads(reread.stdout.strip().splitlines()[-1])["salience_version"] == "sal-v4"

    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _petition(conn, 2, "26-102", counsel=[_office()])
    alarmed = CliRunner().invoke(app, ["federal-label-check"])
    assert alarmed.exit_code == 3, alarmed.output
