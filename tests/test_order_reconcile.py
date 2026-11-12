"""The order-list reconciliation: what a list says against what the corpus holds.

Every fixture is text shaped like what the Court's order lists extract to,
written out here, and every corpus is a temporary one. The one fetch runs
over an in-memory transport with PDF extraction stubbed, so nothing in this
file touches the network.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import order_lineups, order_reconcile
from fedcourtsai.pipeline.documents import ExtractedText
from fedcourtsai.pipeline.order_lineups import (
    FetchedDocument,
    ListEntry,
    OrderDocumentRef,
    list_entries,
)
from fedcourtsai.pipeline.order_reconcile import (
    EntryFinding,
    EntryStatus,
    OrderReconciliation,
    read_entry,
    reconcile,
)
from fedcourtsai.schemas import Disposition, EventKind, Stage
from fedcourtsai.supremecourt import SupremeCourtClient
from tests.conftest import seed_prediction

DAY = date(2026, 10, 13)
#: Past every grace period.
LATER = datetime(2026, 10, 20, 12, tzinfo=UTC)
URL = "https://www.supremecourt.gov/orders/courtorders/101326zor_qol1.pdf"
PETITION = "evt-petition-disposition"
MOTION = "evt-motion-disposition"

ORDER_LIST = "\n".join(
    [
        "(ORDER LIST: 610 U.S.)",
        "TUESDAY, OCTOBER 13, 2026",
        "CERTIORARI -- SUMMARY DISPOSITIONS",
        "25-1367 ROOFING DESIGNS, L.L.C. V. ROYAL CONSTR., INC.",
        "  The petition for a writ of certiorari is granted.  The",
        "judgment is vacated, and the case is remanded to the United",
        "States Court of Appeals for the Fifth Circuit for further",
        "consideration in light of Keathley v. Ayers, 608 U. S. 647 (2026).",
        "ORDERS IN PENDING CASES",
        "26A36 GORDON, CARL V. NEWSOM, GAVIN, ET AL.",
        "  The application for stay addressed to The Chief Justice and",
        "referred to the Court is denied.",
        "26M23 ODOM, RACHEL B. V. OKLAHOMA",
        "  The motion for leave to file a petition for a writ of",
        "certiorari under seal is granted.",
        "25-842 WASSILY, TAMER S., ET AL. V. BLANCHE, ATT'Y GEN.",
        "  The motion of petitioners to dispense with printing the",
        "joint appendix is granted.",
        "25-900 ACME CORP. V. UNITED STATES",
        "  The Solicitor General is invited to file a brief in this",
        "case expressing the views of the United States.",
        "25-7598 PAYNE, DAVID H. V. UNITED STATES",
        "26-5011 LEATHAM, BILLIE J. V. MOSE, HUGH",
        "  The motions of petitioners for leave to proceed in forma",
        "pauperis are denied. Petitioners are allowed until November 3,",
        "2026, within which to pay the docketing fees required by Rule",
        "38(a).",
        "CERTIORARI GRANTED",
        "25-1103 U.S. DOGE SERVICE, ET AL. V. USDC DC, ET AL.",
        "25-1343 BLANCHE, ATT'Y GEN. V. OZURUMBA, IZUCHUKWU",
        "  The petitions for writs of certiorari are granted.",
        "CERTIORARI DENIED",
        "25-590 ALDRIDGE, JERRY, ET AL. V. REGIONS BANK",
        "25-882 PARKER, ANDREW D., ET AL. V. GATES, BILL, ET AL.",
        "25-7001 DOE, JOHN V. ROE, RICHARD",
        "  The motion of petitioner for leave to proceed in forma",
        "pauperis is denied, and the petition for a writ of certiorari",
        "is dismissed.  See Rule 39.8.",
        "MANDAMUS DENIED",
        "26-5254 IN RE WAYNE P. VANCE",
        "  The petition for a writ of mandamus is denied.",
        "REHEARINGS DENIED",
        "25-7382 IN RE RAYMOND R. PEOPLES",
        "  The petition for rehearing is denied.",
        "SUPREME COURT OF THE UNITED STATES",
        "No. 25-590",
        "Statement of SOTOMAYOR, J.",
    ]
)


def _row(  # noqa: PLR0913 - one fixture knob per comparison rule
    conn: sqlite3.Connection,
    docket: int,
    docket_number: str,
    *,
    disposition: Disposition | None = None,
    granted: date | None = None,
    denied: date | None = None,
    decided: date | None = None,
    cvsg: date | None = None,
    selected: bool = False,
    polled: bool = True,
    event: str | None = PETITION,
    stage: Stage = Stage.cert,
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
                date_cert_denied=denied,
                date_decided=decided,
                cvsg_date=cvsg,
                salience_selected=selected,
                last_live_polled=DAY if polled else None,
            )
        ],
    )
    if selected:
        corpus.latch_salience_selected(conn, [case_id])
    if event is not None:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event,
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=stage,
                    resolved=disposition is not None,
                )
            ],
        )
    return case_id


def _document(text: str | None = ORDER_LIST, *, kind: str = "order-list") -> FetchedDocument:
    ref = OrderDocumentRef(url=URL, day=DAY, kind=kind, label="Order List")  # type: ignore[arg-type]
    return FetchedDocument(URL, ref, text, reason=None if text else "the document is not served")


def _reconcile(
    db: Path,
    data: Path,
    *,
    document: FetchedDocument | None = None,
    now: datetime = LATER,
    first_observed: dict[str, date] | None = None,
) -> OrderReconciliation:
    with corpus.connect_readonly(db) as conn:
        return reconcile(
            [document or _document()],
            since=DAY,
            until=DAY,
            now=now,
            conn=conn,
            data_root=data,
            first_observed=(first_observed or {}).get,
        )


def _by_docket(report: OrderReconciliation) -> dict[str, EntryFinding]:
    return {f.docket: f for d in report.documents for f in d.entries}


def _seed_everything(conn: sqlite3.Connection) -> None:
    """A corpus that agrees with ``ORDER_LIST`` on every entry."""
    _row(conn, 1, "25-1367", disposition=Disposition.gvr, granted=DAY)
    _row(
        conn,
        2,
        "26A36",
        disposition=Disposition.denied,
        decided=DAY,
        event=MOTION,
        stage=Stage.interim,
    )
    _row(conn, 3, "25-842", disposition=Disposition.granted, granted=date(2026, 6, 29))
    _row(conn, 4, "25-900", cvsg=DAY)
    _row(conn, 5, "25-7598")
    _row(conn, 6, "26-5011")
    _row(conn, 7, "25-1103", disposition=Disposition.granted, granted=DAY)
    _row(conn, 8, "25-1343", disposition=Disposition.granted, granted=DAY)
    _row(conn, 9, "25-590", disposition=Disposition.denied, denied=DAY, decided=DAY)
    _row(conn, 10, "25-882", disposition=Disposition.denied, denied=DAY, decided=DAY)
    _row(conn, 11, "25-7001", disposition=Disposition.dismissed, decided=DAY)
    _row(conn, 12, "26-5254", disposition=Disposition.denied, denied=DAY)
    _row(conn, 13, "25-7382", disposition=Disposition.denied, denied=date(2026, 6, 8))


# --- the entry reader -----------------------------------------------------------


def test_every_caption_is_an_entry_under_its_heading() -> None:
    entries, problems = list_entries(ORDER_LIST)
    assert problems == []
    assert [(e.docket, e.section) for e in entries] == [
        ("25-1367", "CERTIORARI -- SUMMARY DISPOSITIONS"),
        ("26A36", "ORDERS IN PENDING CASES"),
        ("26M23", "ORDERS IN PENDING CASES"),
        ("25-842", "ORDERS IN PENDING CASES"),
        ("25-900", "ORDERS IN PENDING CASES"),
        ("25-7598", "ORDERS IN PENDING CASES"),
        ("26-5011", "ORDERS IN PENDING CASES"),
        ("25-1103", "CERTIORARI GRANTED"),
        ("25-1343", "CERTIORARI GRANTED"),
        ("25-590", "CERTIORARI DENIED"),
        ("25-882", "CERTIORARI DENIED"),
        ("25-7001", "CERTIORARI DENIED"),
        ("26-5254", "MANDAMUS DENIED"),
        ("25-7382", "REHEARINGS DENIED"),
    ]
    by_docket = {e.docket: e for e in entries}
    # A run of captions shares the text below it, and only the last closes it.
    assert by_docket["25-1103"].text == by_docket["25-1343"].text != ""
    assert not by_docket["25-1103"].closes_run and by_docket["25-1343"].closes_run
    # The appended writing is not part of the list.
    assert "SOTOMAYOR" not in "".join(e.text for e in entries)


def test_a_heading_closes_a_run_of_bare_captions() -> None:
    # The last denials carry no text of their own, so the next section's first
    # entry must not hand them its order.
    text = "\n".join(
        [
            "CERTIORARI DENIED",
            "25-590 ALDRIDGE, JERRY, ET AL. V. REGIONS BANK",
            "HABEAS CORPUS DENIED",
            "26-5555 IN RE JAMES C. CASTLE",
            "  The petition for a writ of habeas corpus is denied.",
        ]
    )
    entries, _ = list_entries(text)
    assert [(e.docket, e.section, bool(e.text)) for e in entries] == [
        ("25-590", "CERTIORARI DENIED", False),
        ("26-5555", "HABEAS CORPUS DENIED", True),
    ]


def test_an_application_number_in_parentheses_joins_its_caption() -> None:
    text = "\n".join(
        [
            "CERTIORARI DENIED",
            "26-5800 SMITH, JOHN V. TEXAS",
            "(26A480)",
            "  The application for stay of execution of sentence of death",
            "presented to Justice Alito and by him referred to the Court is",
            "denied.  The petition for a writ of certiorari is denied.",
        ]
    )
    entries, _ = list_entries(text)
    assert [e.docket for e in entries] == ["26-5800", "26A480"]
    petition, application = (read_entry(e) for e in entries)
    assert petition.kind == "cert" and petition.dispositions == {Disposition.denied}
    assert application.kind == "application"
    assert application.dispositions == {Disposition.denied}


# --- what an entry says ---------------------------------------------------------


@pytest.mark.parametrize(
    ("section", "text", "closes", "kind", "labels"),
    [
        ("CERTIORARI DENIED", "", True, "cert", {"denied"}),
        ("PROBABLE JURISDICTION NOTED", "", True, "cert", {"granted", "granted-in-part"}),
        ("CERTIORARI DISMISSED", "", True, "cert", {"dismissed"}),
        (
            "CERTIORARI DENIED",
            "The motion for leave to file a brief as amicus curiae is granted.",
            True,
            "cert",
            {"denied"},
        ),
        (
            "CERTIORARI DENIED",
            "The petitions for writs of certiorari are dismissed. See Rule 39.8.",
            False,
            "cert",
            {"denied", "dismissed"},
        ),
        ("REHEARINGS DENIED", "The petition for rehearing is denied.", True, "presence", set()),
        (
            "ORDERS IN PENDING CASES",
            "The motions for leave to file petitions for writs of certiorari "
            + "under seal are granted.",
            True,
            "presence",
            set(),
        ),
        (None, "The petition for a writ of certiorari is denied.", True, "cert", {"denied"}),
    ],
)
def test_the_heading_is_read_before_the_text(
    section: str | None, text: str, closes: bool, kind: str, labels: set[str]
) -> None:
    reading = read_entry(ListEntry("25-100", section, text, closes_run=closes))
    assert reading.kind == kind and reading.unparsed is None
    assert {d.value for d in reading.dispositions} == labels


def test_a_fee_allowance_leaves_the_petition_pending() -> None:
    text = (
        "The motion for leave to proceed in forma pauperis is denied. Petitioner is "
        + "allowed until November 3, 2026, within which to pay the docketing fee."
    )
    own = read_entry(ListEntry("26-5136", "HABEAS CORPUS DENIED", text, closes_run=True))
    shared = read_entry(ListEntry("26-5135", "HABEAS CORPUS DENIED", text, closes_run=False))
    assert own.kind == "presence"
    # The singular speaks of its own caption only; the plural of the run.
    assert shared.dispositions == {Disposition.denied}
    plural = (
        "The motions of petitioners for leave to proceed in forma pauperis are denied. "
        + "Petitioners are allowed until November 3, 2026, within which to pay the "
        + "docketing fees."
    )
    assert (
        read_entry(ListEntry("26-5135", "HABEAS CORPUS DENIED", plural, closes_run=False)).kind
        == "presence"
    )


@pytest.mark.parametrize(
    ("docket", "section", "text"),
    [
        ("25-100", "ATTORNEY DISCIPLINE", ""),
        ("25-100", "CERTIORARI -- SUMMARY DISPOSITIONS", "The motion to strike is noted."),
        ("25-100", None, ""),
        ("26A12", None, "The application is held in abeyance."),
    ],
)
def test_an_entry_no_reading_is_taken_from_is_unparsed(
    docket: str, section: str | None, text: str
) -> None:
    assert read_entry(ListEntry(docket, section, text, closes_run=True)).unparsed is not None


# --- the comparison -------------------------------------------------------------


def test_a_corpus_that_agrees_raises_nothing(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)

    report = _reconcile(db, tmp_path / "data")

    assert report.alarms == []
    statuses = {docket: f.status for docket, f in _by_docket(report).items()}
    motion_number = statuses.pop("26M23")
    assert motion_number == EntryStatus.out_of_frame
    presence = {d for d, s in statuses.items() if s == EntryStatus.presence_only}
    assert presence == {"25-842", "25-7598", "26-5011", "25-7382"}
    assert {s for d, s in statuses.items() if d not in presence} == {EntryStatus.matched}
    assert report.counts["entries"] == 14 and report.counts["matched"] == 9
    assert order_reconcile.digest_lines(report) == [
        "2026-10-13 order-list 101326zor_qol1.pdf: 14 entries read, 9 matched, 0 mismatched, "
        + "0 with no row, 0 unparsed"
    ]


def test_a_listed_docket_with_no_row_alarms_after_48_hours(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        conn.execute("DELETE FROM cases WHERE case_id = 'scotus/10'")
        conn.commit()
    end_of_day = datetime(2026, 10, 14, tzinfo=UTC)

    early = _reconcile(db, tmp_path / "data", now=end_of_day + timedelta(hours=47))
    late = _reconcile(db, tmp_path / "data", now=end_of_day + timedelta(hours=48))

    assert _by_docket(early)["25-882"].status == EntryStatus.no_row
    assert early.alarms == []
    assert late.alarms == ["2026-10-13 25-882: no corpus row"]
    assert "Inside the grace period" in order_reconcile.render_markdown(early)
    assert "### Alarms" in order_reconcile.render_markdown(late)


def test_a_row_the_live_channel_never_polled_is_still_found(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        conn.execute("UPDATE cases SET last_live_polled = NULL WHERE case_id = 'scotus/10'")
        conn.commit()

    report = _reconcile(db, tmp_path / "data")

    assert _by_docket(report)["25-882"].status == EntryStatus.matched


def test_a_disagreeing_row_alarms_after_two_pull_windows(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        # Denied on the list: one row still pending, one granted, one dated wrong.
        _row(conn, 9, "25-590")
        _row(conn, 10, "25-882", disposition=Disposition.granted, granted=DAY)
        _row(conn, 12, "26-5254", disposition=Disposition.denied, denied=date(2026, 10, 6))
        conn.execute("UPDATE cases SET cvsg_date = NULL WHERE case_id = 'scotus/4'")
        conn.commit()
    end_of_day = datetime(2026, 10, 14, tzinfo=UTC)

    early = _reconcile(db, tmp_path / "data", now=end_of_day + timedelta(hours=11))
    late = _reconcile(db, tmp_path / "data", now=end_of_day + timedelta(hours=12))

    found = _by_docket(late)
    assert found["25-590"].status == EntryStatus.disposition_mismatch
    assert found["25-590"].detail == "the row records no disposition"
    assert found["25-882"].detail == "the row records granted"
    assert found["26-5254"].status == EntryStatus.date_mismatch
    assert found["25-900"].status == EntryStatus.date_mismatch
    assert early.alarms == []
    assert late.alarms == [
        "2026-10-13 25-900: date mismatch",
        "2026-10-13 25-590: disposition mismatch",
        "2026-10-13 25-882: disposition mismatch",
        "2026-10-13 26-5254: date mismatch",
    ]
    assert "4 mismatched" in order_reconcile.digest_lines(late)[0]


def test_a_renewed_application_is_reported_not_alarmed(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        _row(
            conn,
            2,
            "26A36",
            disposition=Disposition.denied,
            decided=date(2026, 7, 9),
            event=MOTION,
            stage=Stage.interim,
        )

    report = _reconcile(db, tmp_path / "data")

    assert _by_docket(report)["26A36"].status == EntryStatus.renewed
    assert report.alarms == []


def test_a_selected_or_predicted_event_owes_an_outcome_record(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        _row(conn, 7, "25-1103", disposition=Disposition.granted, granted=DAY, selected=True)
        _row(conn, 8, "25-1343", disposition=Disposition.granted, granted=DAY, selected=True)
    # 25-1343 is selected and recorded; 25-590 is unselected but predicted.
    recorded = CasePaths(data, "scotus", 8).event(PETITION).outcome
    recorded.parent.mkdir(parents=True)
    recorded.write_text("{}")
    seed_prediction(data, "scotus", 9, PETITION)

    on_time = _reconcile(db, data, now=datetime(2026, 10, 16, 23, tzinfo=UTC))
    overdue = _reconcile(db, data, now=datetime(2026, 10, 17, tzinfo=UTC))

    found = _by_docket(overdue)
    assert found["25-1103"].missing_outcomes == [PETITION]
    assert found["25-590"].missing_outcomes == [PETITION]
    assert found["25-1343"].missing_outcomes == []
    assert found["25-882"].missing_outcomes == []  # neither selected nor predicted
    assert on_time.alarms == []
    assert overdue.alarms == [
        f"2026-10-13 25-1103: no outcome record: {PETITION}",
        f"2026-10-13 25-590: no outcome record: {PETITION}",
    ]


def test_an_event_closed_without_an_outcome_on_purpose_owes_none(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        case_id = _row(conn, 9, "25-590", disposition=Disposition.denied, denied=DAY, selected=True)
        conn.execute("UPDATE events SET resolved_without_outcome = 1 WHERE case_id = ?", (case_id,))
        conn.commit()

    assert _reconcile(db, tmp_path / "data").alarms == []


def test_an_application_first_stored_after_its_ruling_is_counted(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)

    late = _reconcile(db, tmp_path / "data", first_observed={"scotus/2": DAY + timedelta(days=1)})
    same_day = _reconcile(db, tmp_path / "data", first_observed={"scotus/2": DAY})

    assert late.late_applications == ["26A36"] and late.alarms == []
    assert _by_docket(late)["26A36"].first_observed == DAY + timedelta(days=1)
    assert same_day.late_applications == []
    assert "first stored after their order's day: 1 (26A36)" in order_reconcile.render_markdown(
        late
    )
    assert late.undated_applications == [] and same_day.undated_applications == []
    assert _reconcile(db, tmp_path / "data").undated_applications == ["26A36"]


def test_a_document_the_reader_cannot_read_is_an_alarm_not_a_pass(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)

    unserved = _reconcile(db, tmp_path / "data", document=_document(None))
    empty = _reconcile(db, tmp_path / "data", document=_document("TUESDAY, OCTOBER 13, 2026"))
    # An order list that only names a docket in chambers form split no entry.
    no_entries = _reconcile(db, tmp_path / "data", document=_document("No. 25-590\nO R D E R"))

    assert unserved.alarms == [f"2026-10-13 {URL}: not read (the document is not served)"]
    for report in (empty, no_entries):
        assert report.alarms == [
            f"2026-10-13 {URL}: not read (the reader split no entry out of it)"
        ]
    assert order_reconcile.digest_lines(unserved) == [
        "2026-10-13 order-list 101326zor_qol1.pdf: not read (the document is not served)"
    ]


def test_a_document_that_is_not_a_list_is_checked_for_presence(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _row(
            conn,
            1,
            "26A476",
            disposition=Disposition.granted,
            decided=date(2026, 10, 20),
            event=MOTION,
            stage=Stage.interim,
        )
    chambers = "\n".join(
        [
            "Supreme Court of the United States",
            "No. 26A476",
            "No. 26A477",
            "O R D E R",
            "IT IS ORDERED that the judgment is hereby stayed pending further order.",
        ]
    )

    report = _reconcile(
        db, tmp_path / "data", document=_document(chambers, kind="miscellaneous-order")
    )

    found = _by_docket(report)
    assert found["26A476"].status == EntryStatus.presence_only
    assert found["26A477"].status == EntryStatus.no_row
    assert report.alarms == ["2026-10-13 26A477: no corpus row"]


def test_an_unparsed_entry_is_counted_and_never_alarms(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _row(conn, 1, "25-100", disposition=Disposition.denied, denied=DAY)
    text = "ATTORNEY DISCIPLINE\n25-100 IN THE MATTER OF DOE\n  It is so ordered today."

    report = _reconcile(db, tmp_path / "data", document=_document(text))

    assert report.counts["unparsed"] == 1 and report.alarms == []
    assert "0 matched, 0 mismatched, 0 with no row, 1 unparsed" in "".join(
        order_reconcile.digest_lines(report)
    )


# --- the window and the command ---------------------------------------------------


ORDERS_PAGE = (
    "<div><span>10/13/26&nbsp;</span> <span>"
    + "<a href='/orders/courtorders/101326zor_qol1.pdf'>Order List</a></span></div>"
    + "<div><span>10/19/26&nbsp;</span> <span>"
    + "<a href='/orders/courtorders/101926zor_q8l1.pdf'>Order List</a></span></div>"
)


def _stub_site(monkeypatch: pytest.MonkeyPatch, *, listing: int = 200) -> list[str]:
    requested: list[str] = []

    def extract(data: bytes, *, char_cap: int) -> ExtractedText:
        return ExtractedText(text=data.decode()[:char_cap], pages=1, truncated=False)

    def handle(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path.startswith("/orders/ordersofthecourt/"):
            return httpx.Response(listing, text=ORDERS_PAGE)
        if request.url.path.startswith("/opinions/relatingtoorders/"):
            return httpx.Response(200, text="<table></table>")
        if request.url.path.endswith("101326zor_qol1.pdf"):
            return httpx.Response(200, content=ORDER_LIST.encode())
        return httpx.Response(404)

    monkeypatch.setattr(order_lineups, "extract_pdf_text", extract)
    monkeypatch.setattr(
        "fedcourtsai.cli.SupremeCourtClient",
        lambda **_kw: SupremeCourtClient(
            client=httpx.Client(transport=httpx.MockTransport(handle)), sleep=lambda _s: None
        ),
    )
    return requested


def _point_at(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return corpus.corpus_db_path(root)


def test_the_command_reads_the_window_and_exits_3_on_an_alarm(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    requested = _stub_site(monkeypatch)
    db = _point_at(monkeypatch, tmp_path)
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        conn.execute("DELETE FROM cases WHERE case_id = 'scotus/10'")
        conn.commit()
    summary = tmp_path / "summary.md"

    result = CliRunner().invoke(
        app,
        [
            "order-reconcile",
            "--since",
            "2026-10-12",
            "--until",
            "2026-10-14",
            "--summary-out",
            str(summary),
        ],
    )

    assert result.exit_code == 3, result.output
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["alarms"] == ["2026-10-13 25-882: no corpus row"]
    assert "14 entries read, 8 matched" in result.stderr
    assert "## Order-list reconciliation: failing" in summary.read_text()
    assert not any(path.endswith("101926zor_q8l1.pdf") for path in requested)  # outside


def test_the_command_exits_0_on_a_clean_window(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_site(monkeypatch)
    db = _point_at(monkeypatch, tmp_path)
    with corpus.connect(db) as conn:
        _seed_everything(conn)

    result = CliRunner().invoke(
        app, ["order-reconcile", "--since", "2026-10-13", "--until", "2026-10-13"]
    )

    assert result.exit_code == 0, result.output


def test_the_command_fails_rather_than_pass_an_unread_window(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = _point_at(monkeypatch, tmp_path)
    runner = CliRunner()
    window = ["--since", "2026-10-13", "--until", "2026-10-13"]

    assert runner.invoke(app, ["order-reconcile", *window]).exit_code == 1  # no corpus
    with corpus.connect(db) as conn:
        _seed_everything(conn)
    _stub_site(monkeypatch, listing=503)
    unserved = runner.invoke(app, ["order-reconcile", *window])
    reversed_window = runner.invoke(
        app, ["order-reconcile", "--since", "2026-10-14", "--until", "2026-10-13"]
    )
    bad_date = runner.invoke(app, ["order-reconcile", "--since", "yesterday"])

    assert unserved.exit_code == 1 and "could not be fetched" in unserved.stderr
    assert (reversed_window.exit_code, bad_date.exit_code) == (2, 2)


def test_an_order_on_a_motion_about_an_application_disposes_of_nothing() -> None:
    motion = "The motion for leave to file redacted copies of the application and reply is granted."
    referred = (
        "The application for stay addressed to Justice Gorsuch and referred to the "
        + "Court is denied."
    )
    assert read_entry(ListEntry("25A1448", "ORDERS IN PENDING CASES", motion, True)).kind == (
        "presence"
    )
    reading = read_entry(ListEntry("26A97", "ORDERS IN PENDING CASES", referred, True))
    assert reading.kind == "application" and reading.dispositions == {Disposition.denied}


def test_a_list_cut_at_the_extraction_cap_is_refused(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
    ref = OrderDocumentRef(url=URL, day=DAY, kind="order-list", label="Order List")
    cut = FetchedDocument(URL, ref, ORDER_LIST, truncated=True)

    report = _reconcile(db, tmp_path / "data", document=cut)

    assert report.alarms == [f"2026-10-13 {URL}: not read (the text was cut at the extraction cap)"]
    assert report.counts.get("entries", 0) == 0


def test_an_unnumbered_caption_keeps_its_order_text_to_itself() -> None:
    text = "\n".join(
        [
            "CERTIORARI DENIED",
            "25-100 SMITH, JOHN V. JONES, MARY",
            "25- DOE, JOHN V. ROE, RICHARD",
            "  The petition for a writ of certiorari is dismissed.  See Rule 39.8.",
            "25-103 ABLE, ANN V. BAKER, BOB",
        ]
    )
    entries, problems = list_entries(text)
    assert [(e.docket, e.text) for e in entries] == [("25-100", ""), ("25-103", "")]
    assert problems  # the caption with no serial


def test_a_heading_outside_the_vocabulary_files_its_entries_as_unparsed() -> None:
    text = "\n".join(
        [
            "CERTIORARI GRANTED",
            "25-100 SMITH, JOHN V. JONES, MARY",
            "  The petition for a writ of certiorari is granted.",
            "JURISDICTION POSTPONED",
            "25-200 ABLE, ANN V. BAKER, BOB",
            "  Further consideration of the question of jurisdiction is",
            "postponed to the hearing of the case on the merits.",
        ]
    )
    entries, _ = list_entries(text)
    assert [(e.docket, e.section) for e in entries] == [
        ("25-100", "CERTIORARI GRANTED"),
        ("25-200", "JURISDICTION POSTPONED"),
    ]
    assert "JURISDICTION" not in entries[0].text
    assert read_entry(entries[1]).unparsed == (
        "a heading outside the vocabulary: JURISDICTION POSTPONED"
    )


def test_a_caption_the_cut_does_not_recognise_is_a_problem() -> None:
    text = "\n".join(
        [
            "CERTIORARI DENIED",
            "25-100 SMITH, JOHN V. JONES, MARY",
            "  The motion for leave to file a brief as amicus curiae is granted.",
            "25-101 VandeKamp, Ann V. ROE, RICHARD",
        ]
    )
    entries, problems = list_entries(text)
    assert [e.docket for e in entries] == ["25-100"]
    assert any("opens on a docket number" in p for p in problems)


def test_a_selected_row_out_of_predict_scope_owes_no_outcome(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)
        case_id = _row(conn, 9, "25-590", disposition=Disposition.denied, denied=DAY, selected=True)
        corpus.set_predict_excluded(conn, case_id, True)
        conn.commit()

    assert _reconcile(db, tmp_path / "data").alarms == []


def test_a_store_fault_leaves_the_application_undated(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_everything(conn)

    def fault(_case_id: str) -> date | None:
        raise RuntimeError("the store is unreachable")

    with corpus.connect_readonly(db) as read:
        report = reconcile(
            [_document()],
            since=DAY,
            until=DAY,
            now=LATER,
            conn=read,
            data_root=tmp_path / "data",
            first_observed=fault,
        )

    assert report.alarms == [] and report.undated_applications == ["26A36"]
