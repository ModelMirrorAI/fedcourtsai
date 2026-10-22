"""The post-argument moment: the Court's transcript list, the pass that stores it, the mint."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import httpx

from fedcourtsai import corpus, supremecourt
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import live as live_module
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.documents import (
    KIND_ARGUMENT_TRANSCRIPT,
    KIND_MERITS_BRIEF_PETITIONER,
    clean_transcript_text,
    extract_transcript_text,
)
from fedcourtsai.pipeline.ingest import CorpusRow
from fedcourtsai.pipeline.outcome import (
    MERITS_EVENT_ID,
    Resolution,
    argued_merits_event_for,
    mint_moment_events,
)
from fedcourtsai.provision import CellRead, documents_for_moment, place_at_moment
from fedcourtsai.schemas import Disposition, Moment, PredictableEvent, Stage
from fedcourtsai.serialize import read_model
from fedcourtsai.store import forecastable_event_ids
from fedcourtsai.supremecourt import (
    TRANSCRIPT_LISTING_URL,
    ArgumentSitting,
    ArgumentTranscript,
    SupremeCourtClient,
    TranscriptListing,
    parse_argument_sittings,
    parse_transcript_listing,
)
from tests.test_documents import _pdf

_PAGE = TRANSCRIPT_LISTING_URL.format(term=2025)
_HOST = "https://www.supremecourt.gov/oral_arguments/argument_transcripts"


def _listing_row(docket: str, href: str, argued: str) -> str:
    return (
        "<tr><td><span><a href='"
        + href
        + "' Target='_blank'>"
        + docket
        + "</a></span>"
        + " <span>Doe v. Roe</span></td><td style='text-align: center;'>"
        + argued
        + "</td></tr>"
    )


def _listing(*rows: str, session: str = "April 20, 2026 - April 29, 2026") -> str:
    return (
        "<h4><a href='#cell'>Argument Session: "
        + session
        + "</a></h4>"
        + "<table><tr><th>Oral Argument</th><th>Date Argued</th></tr>"
        + "".join(rows)
        + "</table>"
    )


# --- the list ------------------------------------------------------------------


def test_the_listing_parse_keeps_term_form_dockets_on_the_courts_host() -> None:
    html = _listing(
        _listing_row("25-466", "../argument_transcripts/2025/25-466_ec8f.pdf", "04/20/26"),
        # An application argued on the interim docket has no merits stage.
        _listing_row("25A312", "../argument_transcripts/2025/25A312_a1b2.pdf", "01/21/26"),
        # A link off the Court's host is not this channel.
        _listing_row("25-197", "https://example.com/argument_transcripts/25-197.pdf", "04/20/26"),
        # A row whose date cannot be read is left out rather than guessed.
        _listing_row("25-406", "../argument_transcripts/2025/25-406_9ok0.pdf", "April 21"),
        # Reargued the same Term: the later row is the one the decision follows.
        _listing_row("24-109", "../argument_transcripts/2025/24-109_first.pdf", "10/15/25"),
        _listing_row("24-109", "../argument_transcripts/2025/24-109_again.pdf", "03/02/26"),
    )
    rows = parse_transcript_listing(html, page_url=_PAGE)
    assert rows == [
        ArgumentTranscript("25-466", f"{_HOST}/2025/25-466_ec8f.pdf", date(2026, 4, 20)),
        ArgumentTranscript("24-109", f"{_HOST}/2025/24-109_again.pdf", date(2026, 3, 2)),
    ]


def _client(served: dict[str, Any]) -> tuple[SupremeCourtClient, list[str]]:
    asked: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        asked.append(url)
        body = served.get(url)
        if body is None:
            return httpx.Response(404)
        if isinstance(body, Exception):
            raise body
        if isinstance(body, str):
            return httpx.Response(200, text=body)
        return httpx.Response(200, content=body)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None), asked


def test_the_client_reads_one_terms_list_or_none() -> None:
    html = _listing(_listing_row("25-466", "../argument_transcripts/2025/25-466.pdf", "04/20/26"))
    client, asked = _client({_PAGE: html})
    with client:
        assert client.get_transcript_listing(2025) == TranscriptListing(
            transcripts=[
                ArgumentTranscript("25-466", f"{_HOST}/2025/25-466.pdf", date(2026, 4, 20))
            ],
            sittings=[ArgumentSitting(2025, date(2026, 4, 20), date(2026, 4, 29))],
        )
        assert client.get_transcript_listing(2026) is None
    assert asked == [_PAGE, TRANSCRIPT_LISTING_URL.format(term=2026)]


def test_the_sittings_are_the_courts_own_headings() -> None:
    html = (
        _listing(session="February 08, 2024 - February 28, 2024")
        + _listing(session="October 02, 2023 - October 11, 2023")
        + _listing(session="October 02, 2023 - October 11, 2023")
        # Unreadable, or ending before it starts: left out.
        + _listing(session="Sometime, 2024 - April 25, 2024")
        + _listing(session="April 25, 2024 - April 15, 2024")
    )
    assert parse_argument_sittings(html, term=2023) == [
        ArgumentSitting(2023, date(2023, 10, 2), date(2023, 10, 11)),
        ArgumentSitting(2023, date(2024, 2, 8), date(2024, 2, 28)),
    ]
    sitting = ArgumentSitting(2023, date(2024, 2, 8), date(2024, 2, 28))
    assert sitting.holds(date(2024, 2, 8)) and sitting.holds(date(2024, 2, 28))
    assert not sitting.holds(date(2024, 3, 1))


# --- the text --------------------------------------------------------------------


def test_the_transcript_text_drops_its_furniture_and_word_index() -> None:
    raw = "\n".join(
        [
            "Official - Subject to Final Review",
            "1   ",
            "  CHIEF JUSTICE ROBERTS:   We will hear",
            "2",
            "argument first this morning.",
            "Heritage Reporting Corporation",
            "- - - - - - - - - -",
            "",
            "(Whereupon, at 11:16 a.m., the case",
            "was submitted.)",
            "84",
            "$4 [1] 30:9 abuse [1] 5:9",
        ]
    )
    assert clean_transcript_text(raw) == "\n".join(
        [
            "CHIEF JUSTICE ROBERTS: We will hear",
            "argument first this morning.",
            "(Whereupon, at 11:16 a.m., the case",
            "was submitted.)",
        ]
    )
    # Without the reporter's closing line nothing past it can be told from index.
    assert clean_transcript_text("JUSTICE KAGAN: Why?\n12\nabuse [1] 5:9") == (
        "JUSTICE KAGAN: Why?\nabuse [1] 5:9"
    )


def test_the_transcript_cut_is_made_after_the_clean() -> None:
    extracted = extract_transcript_text(_pdf("JUSTICE THOMAS: A question."), char_cap=1_000)
    assert (extracted.text, extracted.truncated) == ("JUSTICE THOMAS: A question.", False)
    cut = extract_transcript_text(_pdf("JUSTICE THOMAS: A question."), char_cap=10)
    assert (cut.text, cut.truncated) == ("JUSTICE TH", True)


# --- the pass --------------------------------------------------------------------

_TODAY = date(2026, 10, 22)
_LIST_2026 = TRANSCRIPT_LISTING_URL.format(term=2026)
_LIST_2025 = TRANSCRIPT_LISTING_URL.format(term=2025)


def _seed(db: Path, *numbers: str) -> dict[str, str]:
    rows = [
        corpus.CorpusRow(
            case_id=f"scotus/{9_000_000_000 + index}", court="scotus", docket_number=number
        )
        for index, number in enumerate(numbers, start=1)
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    return {row.docket_number or "": row.case_id for row in rows}


def _served() -> dict[str, Any]:
    return {
        _LIST_2026: _listing(
            _listing_row("25-170", "../argument_transcripts/2026/25-170.pdf", "10/05/26"),
            _listing_row("25-999", "../argument_transcripts/2026/25-999.pdf", "10/06/26"),
            session="October 05, 2026 - October 14, 2026",
        ),
        _LIST_2025: _listing(
            _listing_row("25-466", "../argument_transcripts/2025/25-466.pdf", "04/20/26"),
            _listing_row("24-624", "../argument_transcripts/2025/24-624.pdf", "10/15/25"),
        ),
        f"{_HOST}/2026/25-170.pdf": _pdf("JUSTICE ALITO: Counsel."),
        f"{_HOST}/2025/25-466.pdf": _pdf("JUSTICE KAGAN: Why?"),
        f"{_HOST}/2025/24-624.pdf": _pdf(""),
    }


def test_the_pass_stores_each_listed_transcript_once_and_latches_its_day(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    cases = _seed(db, "25-170", "25-466", "24-624")
    client, asked = _client(_served())
    with client:
        ledger = live_module.fetch_argument_transcripts(
            client, db, cap=2, char_cap=10_000, today=_TODAY
        )
    # Newest argument first, two under the cap, the third deferred; the docket
    # the corpus does not hold is counted and left.
    assert ledger == {
        "listed": 4,
        "sittings": 2,
        "unmatched": 1,
        "held": 0,
        "owed": 3,
        "stored": 2,
        "empty": 0,
        "unavailable": 0,
        "failed": 0,
        "deferred": 1,
    }
    assert asked == [_LIST_2026, _LIST_2025, f"{_HOST}/2026/25-170.pdf", f"{_HOST}/2025/25-466.pdf"]
    with corpus.connect(db) as conn:
        stored = {d.kind: d for d in corpus.documents_for_case(conn, cases["25-170"])}
        row = corpus.get_row(conn, cases["25-170"])
        assert corpus.argument_sittings(conn) == [
            ArgumentSitting(2025, date(2026, 4, 20), date(2026, 4, 29)),
            ArgumentSitting(2026, date(2026, 10, 5), date(2026, 10, 14)),
        ]
    document = stored[KIND_ARGUMENT_TRANSCRIPT]
    assert (document.entry_date, document.text) == ("2026-10-05", "JUSTICE ALITO: Counsel.")
    assert row is not None and row.argument_transcript_at == date(2026, 10, 5)

    client, asked = _client(_served())
    with client:
        again = live_module.fetch_argument_transcripts(
            client, db, cap=5, char_cap=10_000, today=_TODAY
        )
    # The two held are not fetched again; the one owed stores no text, so it
    # opens no moment.
    assert (again["held"], again["stored"], again["empty"]) == (2, 1, 1)
    assert f"{_HOST}/2026/25-170.pdf" not in asked
    with corpus.connect(db) as conn:
        blank = corpus.get_row(conn, cases["24-624"])
    assert blank is not None and blank.argument_transcript_at is None


def test_the_pass_counts_a_failed_list_and_a_missing_transcript(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, "25-466")
    served = _served()
    served[_LIST_2026] = httpx.ConnectError("down")
    del served[f"{_HOST}/2025/25-466.pdf"]
    client, _ = _client(served)
    with client:
        ledger = live_module.fetch_argument_transcripts(
            client, db, cap=5, char_cap=10_000, today=_TODAY
        )
    assert (ledger["failed"], ledger["unavailable"], ledger["stored"]) == (1, 1, 0)
    assert live_module.fetch_argument_transcripts(
        client, db, cap=0, char_cap=10_000, today=_TODAY
    ) == dict.fromkeys(ledger, 0)


def test_the_latch_keeps_the_first_argument_day(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    cases = _seed(db, "24-109")
    with corpus.connect(db) as conn:
        corpus.latch_argument_transcript_at(conn, cases["24-109"], date(2025, 3, 3))
        corpus.latch_argument_transcript_at(conn, cases["24-109"], date(2025, 10, 15))
        # A later row upsert that does not carry the fact keeps it.
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id=cases["24-109"], court="scotus", docket_number="24-109")],
        )
        row = corpus.get_row(conn, cases["24-109"])
    assert row is not None and row.argument_transcript_at == date(2025, 3, 3)


# --- the moment ----------------------------------------------------------------


def _granted(**update: Any) -> CorpusRow:
    return CorpusRow(
        case_id="scotus/9525000466",
        court="scotus",
        docket_id=9525000466,
        source="live",
        docket_number="25-466",
        disposition=Disposition.granted,
        date_cert_granted=date(2026, 1, 9),
    ).model_copy(update=update)


def test_the_post_argument_moment_mints_only_on_an_open_merits_proceeding() -> None:
    argued = date(2026, 4, 20)
    minted = argued_merits_event_for(_granted(), [MERITS_EVENT_ID], argued)
    assert minted is not None
    assert (minted.event_id, minted.stage, minted.moment, minted.opened_at) == (
        "evt-argument-judgment",
        Stage.merits,
        Moment.argued,
        argued,
    )
    assert argued_merits_event_for(_granted(), [MERITS_EVENT_ID], None) is None
    assert argued_merits_event_for(_granted(), [], argued) is None
    decided = _granted(merits_judgment="reversed")
    assert argued_merits_event_for(decided, [MERITS_EVENT_ID], argued) is None
    gvr = _granted(disposition=Disposition.gvr)
    assert argued_merits_event_for(gvr, [MERITS_EVENT_ID], argued) is None
    spec = moments.spec_for("evt-argument-judgment")
    assert spec is not None and not spec.forecastable


def test_the_post_argument_moment_mints_off_the_stored_row_but_is_never_forecast(
    tmp_path: Path,
) -> None:
    """The poll's own row carries no transcript; the stored one the pass latched does."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row = _granted()
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=row.case_id,
                    court="scotus",
                    docket_number="25-466",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2026, 1, 9),
                )
            ],
        )
    args = (db, tmp_path, "scotus", 9525000466, row, Resolution(), [MERITS_EVENT_ID])
    assert "evt-argument-judgment" not in mint_moment_events(*args)
    with corpus.connect(db) as conn:
        corpus.latch_argument_transcript_at(conn, row.case_id, date(2026, 4, 20))
    assert "evt-argument-judgment" in mint_moment_events(*args)
    event = read_model(
        CasePaths(tmp_path, "scotus", 9525000466).event("evt-argument-judgment").event_file,
        PredictableEvent,
    )
    assert (event.stage, event.moment, event.opened_at) == (
        Stage.merits,
        Moment.argued,
        date(2026, 4, 20),
    )
    with corpus.connect(db) as conn:
        offered = forecastable_event_ids(conn, "scotus", 9525000466, today=date(2026, 4, 27))
    assert "evt-argument-judgment" not in offered


# --- provisioning ----------------------------------------------------------------


def _document(kind: str, entry_date: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="scotus/9525000466",
        kind=kind,
        url=f"{_HOST}/{kind}.pdf",
        entry_date=entry_date,
        fetched_at=date(2026, 4, 21),
        pages=1,
        truncated=False,
        text="text",
    )


def test_only_a_post_argument_cell_is_handed_the_transcript() -> None:
    documents = [
        _document(KIND_MERITS_BRIEF_PETITIONER, "2026-02-20"),
        _document(KIND_ARGUMENT_TRANSCRIPT, "2026-04-20"),
    ]
    kinds = {d.kind for d in documents_for_moment(documents, "evt-argument-judgment")}
    assert kinds == {KIND_MERITS_BRIEF_PETITIONER, KIND_ARGUMENT_TRANSCRIPT}
    for event in ("evt-order-judgment", "evt-brief-judgment", "evt-petition-review"):
        kept = documents_for_moment(documents, event)
        assert {d.kind for d in kept} == {KIND_MERITS_BRIEF_PETITIONER}
    # An uncut cell reads every stored document but this one, and the count of
    # what it was not handed says so.
    read = CellRead(
        latest=(date(2026, 4, 21), {}),
        documents=documents,
        events=[],
        row=None,
        cutoff=None,
        dated=None,
    )
    placement = place_at_moment(
        "scotus/9525000466",
        "evt-petition-review",
        None,
        read,
        payload={},
        snapshot_date=date(2026, 4, 21),
        documents=documents,
    )
    assert [d.kind for d in placement.documents] == [KIND_MERITS_BRIEF_PETITIONER]
    assert placement.dropped_documents == 1


def test_a_latched_case_keeps_its_first_transcript(tmp_path: Path) -> None:
    """A reargument's transcript, or a re-posted link, never replaces the moment's own."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    cases = _seed(db, "25-466")
    with corpus.connect(db) as conn:
        corpus.latch_argument_transcript_at(conn, cases["25-466"], date(2025, 12, 1))
    served = _served()
    served[_LIST_2026] = _listing(
        _listing_row("25-466", "../argument_transcripts/2026/25-466_re.pdf", "10/06/26")
    )
    client, asked = _client(served)
    with client:
        ledger = live_module.fetch_argument_transcripts(
            client, db, cap=5, char_cap=10_000, today=_TODAY
        )
    assert (ledger["held"], ledger["owed"], ledger["stored"]) == (1, 0, 0)
    assert asked == [_LIST_2026, _LIST_2025]


def test_the_pass_spends_nothing_past_the_deadline_and_isolates_one_failure(
    tmp_path: Path, monkeypatch: Any
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, "25-170", "25-466")
    client, asked = _client(_served())
    with client:
        ledger = live_module.fetch_argument_transcripts(
            client, db, cap=5, char_cap=10_000, today=_TODAY, deadline=0.0, time_fn=lambda: 1.0
        )
    assert asked == [] and ledger["listed"] == 0

    def broken(data: bytes, *, char_cap: int) -> Any:
        if b"ALITO" in data:
            raise ValueError("unreadable")
        return extract_transcript_text(data, char_cap=char_cap)

    monkeypatch.setattr(live_module, "extract_transcript_text", broken)
    client, _ = _client(_served())
    with client:
        ledger = live_module.fetch_argument_transcripts(
            client, db, cap=5, char_cap=10_000, today=_TODAY
        )
    assert (ledger["failed"], ledger["stored"]) == (1, 1)
