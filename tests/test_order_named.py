"""The dockets recent order documents name, and their place at the head of the live cycle."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest

from fedcourtsai import corpus
from fedcourtsai.config import LiveConfig
from fedcourtsai.pipeline import order_lineups
from fedcourtsai.pipeline.documents import ExtractedText
from fedcourtsai.pipeline.live import live_poll_all
from fedcourtsai.pipeline.order_named import read_order_named
from fedcourtsai.schemas import Disposition
from fedcourtsai.supremecourt import SupremeCourtClient

TODAY = date(2026, 11, 20)
ORDER_DAY = date(2026, 11, 19)

LISTING = (
    "<div><span>11/16/26&nbsp;</span> <span>"
    + "<a href='/orders/courtorders/111626zor_a1b2.pdf'>Order List</a></span></div>"
    + "<div><span>11/19/26&nbsp;</span> <span>"
    + "<a href='/orders/courtorders/111926zr_c3d4.pdf'>Miscellaneous Order</a></span></div>"
    + "<div><span>11/20/26&nbsp;</span> <span>"
    + "<a href='/orders/courtorders/112026zr_e5f6.pdf'>Miscellaneous Order</a></span></div>"
)

# An order in chambers: no list, its dockets on `No.` lines.
MISCELLANEOUS = "\n".join(
    [
        "Supreme Court of the United States",
        "No. 26A716",
        "No. 26-6187",
        "O R D E R",
        "The application for stay of execution is denied. The petition for a",
        "writ of certiorari is denied.",
    ]
)

ORDER_LIST = "\n".join(
    [
        "(ORDER LIST: 610 U.S.)",
        "MONDAY, NOVEMBER 16, 2026",
        "ORDERS IN PENDING CASES",
        "26M23 ODOM, RACHEL B. V. OKLAHOMA",
        "  The motion for leave to file a petition for a writ of",
        "certiorari under seal is granted.",
        "25-842 WASSILY, TAMER S., ET AL. V. BLANCHE, ATT'Y GEN.",
        "  The motion of petitioners to dispense with printing the",
        "joint appendix is granted.",
    ]
)

DOCUMENTS = {
    "111626zor_a1b2.pdf": ORDER_LIST,
    "111926zr_c3d4.pdf": MISCELLANEOUS,
}


def _payload(number: str, proceedings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "CaseNumber": f"{number} ",
        "bCapitalCase": False,
        "sJsonCaseType": "Paid",
        "sJsonTerm": "2026",
        "DocketedDate": "November 18, 2026",
        "PetitionerTitle": "Doe, Petitioner",
        "RespondentTitle": "Roe, Respondent",
        "ProceedingsandOrder": proceedings
        if proceedings is not None
        else [{"Date": "Nov 18 2026", "Text": "Petition for a writ of certiorari filed."}],
    }


def _site(
    monkeypatch: pytest.MonkeyPatch,
    *,
    listing: int = 200,
    dockets: dict[str, dict[str, Any]] | None = None,
) -> tuple[SupremeCourtClient, list[str]]:
    """The Court's site: both listings, the order PDFs as plain text, and docket JSON."""
    requested: list[str] = []
    served = dockets or {}

    def extract(data: bytes, *, char_cap: int) -> ExtractedText:
        return ExtractedText(text=data.decode()[:char_cap], pages=1, truncated=False)

    def handle(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        requested.append(path)
        name = path.rsplit("/", 1)[-1]
        if path.startswith("/orders/ordersofthecourt/"):
            return httpx.Response(listing, text=LISTING)
        if path.startswith("/opinions/relatingtoorders/"):
            return httpx.Response(200, text="<table></table>")
        if name in DOCUMENTS:
            return httpx.Response(200, content=DOCUMENTS[name].encode())
        if name.removesuffix(".json") in served:
            return httpx.Response(200, json=served[name.removesuffix(".json")])
        return httpx.Response(404)

    monkeypatch.setattr(order_lineups, "extract_pdf_text", extract)
    client = SupremeCourtClient(
        client=httpx.Client(transport=httpx.MockTransport(handle)), sleep=lambda _s: None
    )
    return client, requested


def _seed(conn: sqlite3.Connection, rows: list[corpus.CorpusRow]) -> None:
    """Rows, each with the open event the petition rotation's test requires."""
    corpus.upsert_rows(conn, rows)
    corpus.upsert_events(
        conn,
        [
            corpus.CorpusEvent(
                event_id="evt-petition-disposition",
                case_id=row.case_id,
                court="scotus",
                kind="petition",
                title=row.case_id,
            )
            for row in rows
        ],
    )


def _row(docket_id: int, number: str, **fields: Any) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=f"scotus/{docket_id}", court="scotus", docket_number=number, **fields
    )


# --- reading the documents --------------------------------------------------------


def test_the_window_names_each_followed_docket_with_its_latest_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, requested = _site(monkeypatch)
    with client:
        named = read_order_named(order_lineups.OrderFetcher(client), today=TODAY, lookback_days=4)

    # The motion number names no row the channel follows.
    assert named.days == {
        "26A716": ORDER_DAY,
        "26-6187": ORDER_DAY,
        "25-842": date(2026, 11, 16),
    }
    # Three listed, and the one whose PDF is not served is counted unread.
    assert (named.documents, named.unread) == (3, 1)
    assert any(path.endswith("112026zr_e5f6.pdf") for path in requested)


def test_the_window_leaves_out_a_document_listed_before_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, requested = _site(monkeypatch)
    with client:
        named = read_order_named(order_lineups.OrderFetcher(client), today=TODAY, lookback_days=1)

    assert set(named.days) == {"26A716", "26-6187"}
    assert not any(path.endswith("111626zor_a1b2.pdf") for path in requested)


def test_an_expired_deadline_reads_no_document_and_counts_them_unread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, requested = _site(monkeypatch)
    with client:
        named = read_order_named(
            order_lineups.OrderFetcher(client),
            today=TODAY,
            lookback_days=4,
            deadline=0.0,
            time_fn=lambda: 1.0,
        )

    assert named.days == {} and (named.documents, named.unread) == (3, 3)
    assert not any(path.endswith(".pdf") for path in requested)


# --- which rows are owed ----------------------------------------------------------


def test_a_named_row_is_owed_until_a_poll_dated_after_its_order(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed(
            conn,
            [
                # Polled on the order's own day: before or after the order, the date cannot say.
                _row(9026006187, "26-6187", last_live_polled=ORDER_DAY),
                # Polled the day after: that poll read the order.
                _row(9026006154, "26-6154", last_live_polled=TODAY),
                # Never polled.
                _row(9026006013, "26-6013"),
                # Polled days before.
                _row(9026006051, "26-6051", last_live_polled=date(2026, 11, 14)),
                # Decided already: a rehearing denial names it, and nothing is left to read.
                _row(
                    9025001004,
                    "25-1004",
                    disposition=Disposition.denied,
                    date_decided=date(2026, 4, 20),
                    last_live_polled=date(2026, 8, 3),
                ),
                # Not named.
                _row(9026000001, "26-1", last_live_polled=date(2026, 11, 14)),
            ],
        )
        corpus.upsert_rows(
            conn,
            [
                _row(9526000716, "26A716", last_live_polled=ORDER_DAY),
                _row(
                    9526000500,
                    "26A500",
                    disposition=Disposition.denied,
                    date_decided=date(2026, 10, 27),
                ),
            ],
        )
        petitions, applications = corpus.order_named_rows(
            conn,
            {
                number: ORDER_DAY
                for number in (
                    "26-6187",
                    "26-6154",
                    "26-6013",
                    "26-6051",
                    "25-1004",
                    "26A716",
                    "26A500",
                    "26-9999",
                )
            },
        )

    # Never-polled first, then stalest.
    assert [row.docket_number for row in petitions] == ["26-6013", "26-6051", "26-6187"]
    assert [row.docket_number for row in applications] == ["26A716"]


def test_no_named_docket_is_no_read(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.order_named_rows(conn, {}) == ([], [])


# --- the cycle --------------------------------------------------------------------


def _pending_estate(db: Path) -> None:
    """A named petition and application behind rows their rotations prefer."""
    with corpus.connect(db) as conn:
        _seed(
            conn,
            [
                # Distributed for a past conference and stale: the rotation's head.
                _row(
                    9026000001,
                    "26-1",
                    distributed_for_conference=date(2026, 11, 13),
                    last_live_polled=date(2026, 11, 14),
                ),
                # Undistributed, polled on the order's day: the rotation's tail.
                _row(9026006187, "26-6187", last_live_polled=ORDER_DAY),
            ],
        )
        corpus.upsert_rows(
            conn,
            [
                _row(9526000001, "26A1", last_live_polled=date(2026, 11, 14)),
                _row(9526000716, "26A716", last_live_polled=ORDER_DAY),
            ],
        )


def _polled(db: Path, *case_ids: str) -> list[date | None]:
    with corpus.connect(db) as conn:
        rows = [corpus.get_row(conn, case_id) for case_id in case_ids]
    return [row.last_live_polled if row is not None else None for row in rows]


DENIED = [
    {"Date": "Nov 18 2026", "Text": "Petition for a writ of certiorari filed."},
    {"Date": "Nov 19 2026", "Text": "Petition DENIED."},
]
SERVED = {
    "26-1": _payload("26-1"),
    "26-6187": _payload("26-6187", DENIED),
    "26a1": _payload("26A1"),
    "26a716": _payload("26A716"),
}


def test_the_cycle_polls_a_named_docket_ahead_of_its_rotation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_estate(db)
    config = LiveConfig(
        max_cases_per_run=1,
        max_applications_per_run=1,
        max_new_cases_per_run=0,
        order_named_per_run=5,
        order_named_lookback_days=1,
    )
    client, _requested = _site(monkeypatch, dockets=SERVED)
    with client:
        queues, _discovery = live_poll_all(
            client, db, tmp_path / "data", term=26, config=config, today=TODAY
        )

    assert queues.order_named == {
        "documents": 2,
        "unread": 1,
        "dockets": 2,
        "owed": 2,
        "petitions": 1,
        "applications": 1,
    }
    # The one slot of each cap went to the named row, not to the rotation's head.
    assert _polled(
        db, "scotus/9026006187", "scotus/9026000001", "scotus/9526000716", "scotus/9526000001"
    ) == [TODAY, date(2026, 11, 14), TODAY, date(2026, 11, 14)]
    with corpus.connect(db) as conn:
        denied = corpus.get_row(conn, "scotus/9026006187")
    assert denied is not None and denied.disposition == Disposition.denied
    assert denied.date_decided == ORDER_DAY


def test_the_cycle_keeps_the_named_rows_inside_their_own_cap(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_estate(db)
    config = LiveConfig(
        max_cases_per_run=2,
        max_applications_per_run=2,
        max_new_cases_per_run=0,
        order_named_per_run=1,
        order_named_lookback_days=1,
    )
    client, _requested = _site(monkeypatch, dockets=SERVED)
    with client:
        queues, _discovery = live_poll_all(
            client, db, tmp_path / "data", term=26, config=config, today=TODAY
        )

    # One slot for both forms, applications first: the petition is polled here on
    # its rotation's own order and stays owed as a named row.
    assert queues.order_named["owed"] == 2
    assert (queues.order_named["petitions"], queues.order_named["applications"]) == (0, 1)
    assert _polled(db, "scotus/9026006187", "scotus/9026000001") == [TODAY, TODAY]


def test_a_named_row_at_the_rotation_head_costs_the_cycle_no_slot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed(
            conn,
            [
                # Named, and the rotation's own head as well.
                _row(
                    9026006187,
                    "26-6187",
                    distributed_for_conference=date(2026, 11, 13),
                    last_live_polled=date(2026, 11, 14),
                ),
                _row(9026000001, "26-1", last_live_polled=date(2026, 11, 15)),
                _row(9026000002, "26-2", last_live_polled=date(2026, 11, 16)),
            ],
        )
    config = LiveConfig(
        max_cases_per_run=2,
        max_applications_per_run=0,
        max_new_cases_per_run=0,
        order_named_per_run=5,
        order_named_lookback_days=1,
    )
    served = {**SERVED, "26-2": _payload("26-2")}
    client, _requested = _site(monkeypatch, dockets=served)
    with client:
        live_poll_all(client, db, tmp_path / "data", term=26, config=config, today=TODAY)

    # Both slots are used: the named row, then the next row behind it.
    assert _polled(db, "scotus/9026006187", "scotus/9026000001", "scotus/9026000002") == [
        TODAY,
        TODAY,
        date(2026, 11, 16),
    ]


def test_a_document_the_reader_raises_on_is_that_document_alone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _requested = _site(monkeypatch)

    def extract(data: bytes, *, char_cap: int) -> ExtractedText:
        if b"ORDER LIST" in data:
            raise RecursionError("a malformed page tree")
        return ExtractedText(text=data.decode()[:char_cap], pages=1, truncated=False)

    monkeypatch.setattr(order_lineups, "extract_pdf_text", extract)
    with client:
        named = read_order_named(order_lineups.OrderFetcher(client), today=TODAY, lookback_days=4)

    assert set(named.days) == {"26A716", "26-6187"}
    assert (named.documents, named.unread) == (3, 2)


def test_a_spent_budget_skips_the_pass_before_any_fetch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_estate(db)
    config = LiveConfig(max_new_cases_per_run=0, order_named_per_run=5)
    client, requested = _site(monkeypatch, dockets=SERVED)
    with client:
        queues, _discovery = live_poll_all(
            client,
            db,
            tmp_path / "data",
            term=26,
            config=config,
            today=TODAY,
            deadline=0.0,
            time_fn=lambda: 1.0,
        )

    assert queues.order_named == {"skipped": "deadline"}
    assert not any("/orders/" in path for path in requested)


def test_an_unserved_listing_costs_the_cycle_only_the_ordering(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_estate(db)
    config = LiveConfig(
        max_cases_per_run=1,
        max_applications_per_run=1,
        max_new_cases_per_run=0,
        order_named_per_run=5,
    )
    client, _requested = _site(monkeypatch, listing=503, dockets=SERVED)
    with client:
        queues, _discovery = live_poll_all(
            client, db, tmp_path / "data", term=26, config=config, today=TODAY
        )

    assert queues.order_named == {"error": "HTTPStatusError"}
    # The rotations ran on their own order.
    assert _polled(db, "scotus/9026000001", "scotus/9026006187") == [TODAY, ORDER_DAY]


def test_the_pass_is_off_by_default_and_fetches_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_estate(db)
    config = LiveConfig(max_cases_per_run=1, max_applications_per_run=1, max_new_cases_per_run=0)
    client, requested = _site(monkeypatch, dockets=SERVED)
    with client:
        queues, _discovery = live_poll_all(
            client, db, tmp_path / "data", term=26, config=config, today=TODAY
        )

    assert queues.order_named == {}
    assert not any("/orders/" in path or "/opinions/" in path for path in requested)
