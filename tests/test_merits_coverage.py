"""The merits coverage census: every plenary grant gets exactly one status."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.merits_coverage import MeritsCoverageStatus, merits_coverage
from fedcourtsai.schemas import Disposition, EventKind, Judgment, MeritsTermination, Stage
from tests.conftest import seed_prediction

TODAY = date(2026, 10, 21)
GRANTED = date(2026, 1, 9)  # OT2025
ORDER_JUDGMENT = "evt-order-judgment"


def _grant(  # noqa: PLR0913 - one fixture knob per classification rule
    conn: sqlite3.Connection,
    docket: int,
    *,
    docket_number: str = "25-100",
    disposition: Disposition = Disposition.granted,
    granted: date = GRANTED,
    event: bool = True,
    resolved: bool = False,
    merits_judgment: Judgment | None = None,
    merits_decided: date | None = None,
    merits_terminated: MeritsTermination | None = None,
) -> str:
    case_id = f"scotus/{docket}"
    corpus.upsert_rows(
        conn,
        [
            corpus.CorpusRow(
                case_id=case_id,
                court="scotus",
                docket_number=docket_number,
                disposition=disposition,
                date_cert_granted=granted,
                merits_judgment=merits_judgment,
                merits_decided=merits_decided,
                merits_terminated=merits_terminated,
            )
        ],
    )
    if event:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=ORDER_JUDGMENT,
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                    resolved=resolved,
                )
            ],
        )
    return case_id


def _census(db: Path, data: Path) -> dict[str, MeritsCoverageStatus]:
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage(conn, data, first_term=2025, last_term=2026, today=TODAY)
    return {e.case_id: e.status for e in result.uncovered}


def test_every_plenary_grant_gets_one_status(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1)  # forecast, below
        _grant(conn, 2)  # owed: open, forecastable, no cell yet
        _grant(conn, 3, event=False)  # a pending grant the stream never minted
        _grant(conn, 4)
        corpus.set_merits_termination(conn, "scotus/4", MeritsTermination.voluntary_dismissal)
        _grant(
            conn,
            5,
            event=False,
            merits_judgment=Judgment.reversed,
            merits_decided=date(2026, 6, 1),
        )
        _grant(conn, 6, granted=date(2024, 1, 9))  # OT2023: outside the range
    seed_prediction(data, "scotus", 1, ORDER_JUDGMENT)

    with corpus.connect_readonly(db) as conn:
        result = merits_coverage(conn, data, first_term=2025, last_term=2026, today=TODAY)

    statuses = {e.case_id: e.status for e in result.uncovered}
    assert statuses == {
        "scotus/2": MeritsCoverageStatus.owed,
        "scotus/3": MeritsCoverageStatus.no_event,
        "scotus/4": MeritsCoverageStatus.terminated,
        "scotus/5": MeritsCoverageStatus.decided_unforecast,
    }
    (ot2025, ot2026) = result.terms
    assert ot2025.plenary_grants == 5
    assert sum(ot2025.statuses.values()) == ot2025.plenary_grants
    assert ot2025.statuses["forecast"] == 1
    assert ot2026.plenary_grants == 0
    assert result.gaps == 1  # the unminted pending grant


def test_order_riding_grants_are_counted_apart(tmp_path: Path) -> None:
    # A vacatur dated on its own grant rode the cert order: a cert-stage fact the
    # merits stream never forecasts, whatever its label says.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1, event=False, merits_judgment=Judgment.vacated, merits_decided=GRANTED)
        _grant(conn, 2, disposition=Disposition.gvr, event=False)

    with corpus.connect_readonly(db) as conn:
        result = merits_coverage(conn, data, first_term=2025, last_term=2025, today=TODAY)

    (term,) = result.terms
    assert term.order_riding == 1  # the GVR label opens no merits proceeding at all
    assert term.plenary_grants == 0
    assert result.uncovered == []


def test_scope_refusal_and_staleness_are_named(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1)
        conn.execute(
            "UPDATE cases SET date_filed = '2025-06-01', date_decided = '2025-01-01' "
            + "WHERE case_id = 'scotus/1'"
        )
        conn.commit()
        _grant(conn, 2, granted=TODAY - timedelta(days=corpus.STALE_GRANT_DAYS + 30))

    with corpus.connect_readonly(db) as conn:
        result = merits_coverage(conn, data, first_term=2023, last_term=2026, today=TODAY)

    by_case = {e.case_id: e for e in result.uncovered}
    assert by_case["scotus/1"].status == MeritsCoverageStatus.out_of_scope
    assert by_case["scotus/1"].detail == "internally inconsistent dates — decided before filed"
    assert by_case["scotus/2"].status == MeritsCoverageStatus.stale


def test_a_granted_ifp_case_is_owed_not_refused(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1, docket_number="25-5343")

    assert _census(db, data) == {"scotus/1": MeritsCoverageStatus.owed}


def test_the_cli_exits_3_on_a_hole(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "corpus"
    db = corpus.corpus_db_path(root)
    with corpus.connect(db) as conn:
        _grant(conn, 1, granted=date.today() - timedelta(days=30), event=False)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))

    result = CliRunner().invoke(app, ["merits-coverage", "--first-term", "2020"])

    assert result.exit_code == 3, result.output
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["gaps"] == 1
    assert payload["uncovered"][0]["status"] == "no_event"


def test_a_scope_refused_grant_without_an_event_is_not_a_hole(tmp_path: Path) -> None:
    # The mint refuses an out-of-scope grant its merits event, so the missing
    # event is the documented refusal.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1, event=False)
        conn.execute(
            "UPDATE cases SET date_filed = '2025-06-01', date_decided = '2025-01-01' "
            + "WHERE case_id = 'scotus/1'"
        )
        conn.commit()

    assert _census(db, data) == {"scotus/1": MeritsCoverageStatus.out_of_scope}


def test_a_resolved_event_with_no_judgment_is_a_named_hole(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1, resolved=True)

    with corpus.connect_readonly(db) as conn:
        result = merits_coverage(conn, data, first_term=2025, last_term=2025, today=TODAY)

    (entry,) = result.uncovered
    assert entry.status == MeritsCoverageStatus.no_event
    assert entry.detail == "merits event resolved, no judgment latched"
    assert result.gaps == 1


def test_a_prediction_counts_even_without_its_corpus_event_row(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _grant(conn, 1, event=False)
    seed_prediction(data, "scotus", 1, ORDER_JUDGMENT)

    assert _census(db, data) == {}
