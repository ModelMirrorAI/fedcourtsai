"""The order-stage notation channel: both grammars, the document split, assembly, fetch.

Every fixture is text shaped like what the Court's order lists and Opinions
Relating to Orders extract to — small-caps splits, line-end hyphenation,
running heads — written out here. The fetch runs over an in-memory transport
with PDF extraction stubbed, so nothing in this file touches the network.
"""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline import order_lineups, vote_sources
from fedcourtsai.pipeline.documents import ExtractedText
from fedcourtsai.pipeline.justices import bench_on, chief_on_bench
from fedcourtsai.pipeline.lineup import WritingKind
from fedcourtsai.pipeline.order_grammars import (
    HEADERS_GRAMMAR,
    HEADERS_VERSION,
    NOTATIONS_GRAMMAR,
    NOTATIONS_VERSION,
    match_header,
    parse_order_notations,
    parse_writing_header,
)
from fedcourtsai.pipeline.order_lineups import (
    FetchedDocument,
    OrderFetcher,
    parse_orders_listing,
    parse_relating_listing,
    read_day,
    read_documents,
    read_url,
    split_document,
)
from fedcourtsai.schemas import VoteValue, WritingRole
from fedcourtsai.supremecourt import SupremeCourtClient

DAY = date(2026, 6, 22)
BENCH = bench_on(DAY)


def _notes(text: str) -> dict[str, VoteValue]:
    lineup = parse_order_notations(text, bench=BENCH)
    assert not lineup.complete and not lineup.writings_complete
    return dict(lineup.votes)


# --- the notation grammar --------------------------------------------------------


def test_a_single_noted_vote_is_read_and_stamped() -> None:
    lineup = parse_order_notations(
        "The petition for a writ of certiorari is denied.  Justice\n"
        "Kavanaugh would grant the petition for a writ of certiorari.",
        bench=BENCH,
    )
    assert dict(lineup.votes) == {"Kavanaugh": VoteValue.grant}
    assert (lineup.grammar, lineup.grammar_version) == (NOTATIONS_GRAMMAR, NOTATIONS_VERSION)
    assert lineup.problems == ()
    assert lineup.participating is None  # a partial list has no denominator


def test_several_noted_votes_in_small_caps_are_read() -> None:
    assert _notes(
        "It is so ordered.\n JUSTICE SOTOMAYOR, J USTICE KAGAN, and JUSTICE\n"
        "JACKSON would deny the petition for a writ of certiorari."
    ) == {
        "Sotomayor": VoteValue.deny,
        "Kagan": VoteValue.deny,
        "Jackson": VoteValue.deny,
    }


def test_a_noted_vote_with_a_summary_reversal_is_a_vote_to_grant() -> None:
    assert _notes(
        "The petition for a writ of certiorari is denied.  Justice Thomas and Justice Alito "
        "would grant the petition for certiorari and summarily reverse for the reasons "
        "stated in Alabama v. Powell, 608 U. S. ___ (2026) (Alito, J., dissenting from "
        "denial of certiorari)."
    ) == {"Thomas": VoteValue.grant, "Alito": VoteValue.grant}


def test_took_no_part_is_did_not_participate_and_the_chief_resolves_by_title() -> None:
    assert _notes(
        "The petition for a writ of certiorari is denied.  The Chief\n"
        "Justice took no part in the consideration or decision of this\npetition.  "
        "See 28 U. S. C. §455 and Code of Conduct for Justices of the Supreme Court."
    ) == {"Roberts": VoteValue.did_not_participate}
    assert chief_on_bench(BENCH) == "Roberts"


def test_an_application_notation_sets_aside_the_circuit_justice() -> None:
    assert _notes(
        "The application for stay presented to Justice Alito and by him referred to the "
        "Court is denied.  Justice Sotomayor would grant the application."
    ) == {"Sotomayor": VoteValue.grant}


def test_an_unwritten_dissent_from_a_grant_of_a_stay_is_a_vote_to_deny() -> None:
    assert _notes(
        "The application for stay is granted.  Justice Jackson dissents from the grant "
        "of the application for stay."
    ) == {"Jackson": VoteValue.deny}


@pytest.mark.parametrize(
    "text",
    [
        # A name the roster does not carry: never a guessed Justice.
        "The petition is denied.  Justice Thompson would grant the petition.",
        # A Justice not on this bench.
        "The petition is denied.  Justice Breyer would grant the petition.",
        # A noted act no rule reads.
        "The application is granted.  Justice Gorsuch would vacate the stay.",
        # Limited to part of the matter.
        "The application is granted in part.  Justice Alito would grant the application in full"
        + " and deny it as to the second request.",
        # A vote on a motion, not the petition.
        "The motion is denied.  Justice Thomas would grant the motion.",
        "The motion is granted.  Justice Kavanaugh took no part in the consideration or"
        + " decision of this motion.",
        # A writing announced but not yet published.
        "The application is denied.  Justice Alito would grant the application.  An opinion"
        + " to follow.",
        # One Justice read two ways.
        "Justice Thomas would grant the petition.  Justice Thomas would deny the petition.",
    ],
)
def test_anything_unread_is_a_problem_and_empties_the_votes(text: str) -> None:
    lineup = parse_order_notations(text, bench=BENCH)
    assert lineup.problems
    assert dict(lineup.votes) == {}


def test_an_order_with_no_notation_reads_nothing_and_no_problem() -> None:
    lineup = parse_order_notations("The petitions for writs of certiorari are denied.", bench=BENCH)
    assert (dict(lineup.votes), lineup.problems) == ({}, ())


# --- the writing-header grammar ----------------------------------------------------


def test_a_joined_dissent_from_denial_votes_its_author_and_joiner_to_grant() -> None:
    lineup = parse_writing_header(
        "JUSTICE ALITO, with whom J USTICE THOMAS joins, dis-\nsenting from the denial of "
        "certiorari.",
        bench=BENCH,
    )
    (writing,) = lineup.writings
    assert (writing.kind, writing.author, writing.joiners) == (
        WritingKind.dissent,
        "Alito",
        frozenset({"Thomas"}),
    )
    assert dict(lineup.votes) == {"Alito": VoteValue.grant, "Thomas": VoteValue.grant}
    assert (lineup.grammar, lineup.grammar_version) == (HEADERS_GRAMMAR, HEADERS_VERSION)
    assert not lineup.complete and not lineup.writings_complete


def test_a_dissent_from_a_grant_of_stay_with_two_joiners_votes_to_deny() -> None:
    lineup = parse_writing_header(
        "JUSTICE SOTOMAYOR, with whom J USTICE KAGAN and\nJUSTICE JACKSON join, dissenting "
        "from grant of stay.",
        bench=BENCH,
    )
    assert dict(lineup.votes) == dict.fromkeys(("Sotomayor", "Kagan", "Jackson"), VoteValue.deny)


def test_a_statement_respecting_denial_records_a_writing_and_no_vote() -> None:
    lineup = parse_writing_header(
        "Statement of JUSTICE SOTOMAYOR respecting the denial\nof certiorari.", bench=BENCH
    )
    (writing,) = lineup.writings
    assert (writing.kind, writing.author) == (WritingKind.statement, "Sotomayor")
    assert dict(lineup.votes) == {}
    assert lineup.problems == ()


def test_a_concurrence_in_the_denial_of_an_application_votes_to_deny() -> None:
    lineup = parse_writing_header(
        "CHIEF JUSTICE ROBERTS, with whom JUSTICE KAVANAUGH joins, concurring in the denial "
        "of the application for stay.",
        bench=BENCH,
    )
    assert dict(lineup.votes) == {"Roberts": VoteValue.deny, "Kavanaugh": VoteValue.deny}


def test_the_chief_as_a_joiner_resolves_by_title() -> None:
    lineup = parse_writing_header(
        "JUSTICE KAVANAUGH, with whom THE CHIEF JUSTICE joins, concurring in the grant of the "
        "application.",
        bench=BENCH,
    )
    assert dict(lineup.votes) == {"Kavanaugh": VoteValue.grant, "Roberts": VoteValue.grant}


@pytest.mark.parametrize(
    ("header", "kind"),
    [
        ("JUSTICE ALITO, dissenting.", WritingKind.dissent),
        ("JUSTICE KAVANAUGH, concurring in the judgment.", WritingKind.concurrence_in_judgment),
        ("Justice Jackson, dissenting:", WritingKind.dissent),
        ("Statement of JUSTICE GORSUCH.", WritingKind.statement),
    ],
)
def test_a_header_whose_role_names_no_side_records_no_vote(header: str, kind: WritingKind) -> None:
    lineup = parse_writing_header(header, bench=BENCH)
    assert [w.kind for w in lineup.writings] == [kind]
    assert dict(lineup.votes) == {}


def test_a_partial_joiner_joins_but_gets_no_vote() -> None:
    lineup = parse_writing_header(
        "JUSTICE GORSUCH, with whom JUSTICE THOMAS joins as to Part II, dissenting from the "
        "denial of certiorari.",
        bench=BENCH,
    )
    (writing,) = lineup.writings
    assert [(j.justice, j.qualifier) for j in writing.joins] == [("Thomas", "as to Part II")]
    assert dict(lineup.votes) == {"Gorsuch": VoteValue.grant}


@pytest.mark.parametrize(
    "header",
    [
        "JUSTICE ALITO, with whom JUSTICE THOMSON joins, dissenting.",
        "JUSTICE STEVENS, dissenting from the denial of certiorari.",
        "JUSTICE ALITO, lamenting the denial of certiorari.",
        "JUSTICE ALITO, with whom JUSTICE ALITO joins, dissenting.",
    ],
)
def test_an_unreadable_header_yields_no_writing_and_no_vote(header: str) -> None:
    lineup = parse_writing_header(header, bench=BENCH)
    assert lineup.problems
    assert dict(lineup.votes) == {}


def test_match_header_tells_a_header_from_a_notation_or_prose() -> None:
    assert match_header("JUSTICE THOMAS, dissenting.\nApplicants are") == (
        "JUSTICE THOMAS, dissenting."
    )
    assert match_header("JUSTICE THOMAS would grant the application.") is None
    assert match_header("JUSTICE KAVANAUGH, concurring in the judgment, would hold") is None
    assert match_header("Statement of JUSTICE SOTOMAYOR.") == "Statement of JUSTICE SOTOMAYOR."


def test_the_bench_is_an_input_not_a_reading() -> None:
    with pytest.raises(ValueError, match="not on the roster"):
        parse_order_notations("", bench=["Nobody"])


# --- splitting a document ------------------------------------------------------------

ORDER_LIST = """(ORDER LIST: 608 U.S.)
MONDAY, JUNE 22, 2026
CERTIORARI DENIED
25-7457 WILLIAMS, MARIO M. V. UNITED STATES
25-7458 ESPINDOLA, HUGO E. V. UNITED STATES
  The petitions for writs of certiorari are denied.
25-538 LOS ANGELES, CA, ET AL. V. ESTATE OF HERNANDEZ, ET AL.
  The petition for a writ of certiorari is denied.  Justice
Thomas and Justice Alito would grant the petition for a writ of
certiorari.
25-1309   CARR, DAVID V. PNC BANK, NAT. ASSN.
  The petition for a writ of certiorari is denied.  Justice
Alito took no part in the consideration or decision of this
6
petition.
25-7460 GORDON, MICHAEL L. V. OHIO
  The motion of petitioner for leave to proceed in forma
 pauperis is denied, and the petition for a writ of certiorari is
dismissed. See Rule 39.8.  Justice Jackson, dissenting:  I respectfully
dissent from the order barring this incarcerated petitioner.
26-5637 RAMEY, KER'SEAN O. V. TEXAS
(26A380)
The application for stay of execution of sentence of death
presented to Justice Alito and by him referred to the Court is
denied.  The petition for a writ of certiorari is denied.
HABEAS CORPUS DENIED
25-7502 IN RE GURJOT S. DHALIWAL
  The petition for a writ of habeas corpus is denied.
7
 Cite as: 608 U. S. ____ (2026) 1
Per Curiam
SUPREME COURT OF THE UNITED STATES
KEVIN MCCARTHY, SUPERINTENDENT v.
PEDRO HERNANDEZ
ON PETITION FOR WRIT OF CERTIORARI TO THE UNITED
STATES COURT OF APPEALS FOR THE SECOND CIRCUIT
No. 25\u2013748. Decided June 22, 2026
 PER CURIAM.
The Second Circuit exceeded its authority, as Justice Kennedy
explained, and we grant the petition and reverse.
It is so ordered.
 JUSTICE SOTOMAYOR, J USTICE KAGAN, and JUSTICE
JACKSON would deny the petition for a writ of certiorari.
1  Cite as: 608 U. S. ____ (2026)
ALITO, J., dissenting
SUPREME COURT OF THE UNITED STATES
UNITED STATES v. DONTE J. CARTER
ON PETITION FOR WRIT OF CERTIORARI TO THE DISTRICT OF
COLUMBIA COURT OF APPEALS
No. 25\u2013885. Decided June 22, 2026
The petition for a writ of certiorari is denied.
JUSTICE ALITO, with whom J USTICE THOMAS joins, dis-
senting from the denial of certiorari.
On a September afternoon in 2020, several officers approached. I would
grant the petition.
2 UNITED STATES v. CARTER
ALITO, J., dissenting
JUSTICE THOMAS, writing elsewhere, said so. I respectfully dissent.
"""


def test_the_split_finds_entries_sections_and_their_dockets() -> None:
    split = split_document(ORDER_LIST)
    assert split.day == DAY
    by_where = {(p.where, p.dockets) for p in split.pieces}
    assert ("list-entry", ("25-7457", "25-7458")) in by_where
    assert ("list-entry", ("26-5637", "26A380")) in by_where
    assert ("header", ("25-7460",)) in by_where
    assert ("order-text", ("25-748",)) in by_where
    assert ("header", ("25-885",)) in by_where
    assert split.problems == ()
    (per_curiam,) = [p for p in split.pieces if p.dockets == ("25-748",)]
    # Only the lines after "It is so ordered." are read from a per curiam.
    assert "Kennedy" not in per_curiam.text
    assert per_curiam.text.startswith("JUSTICE SOTOMAYOR")


def _day(*texts: str, covers: bool = True) -> dict[str, order_lineups.OrderDocketReading]:
    documents = [
        FetchedDocument(f"https://www.supremecourt.gov/orders/courtorders/{i}.pdf", None, text)
        for i, text in enumerate(texts)
    ]
    reading = read_documents(documents, day=DAY, covers_the_day=covers)
    return {d.docket: d for d in reading.dockets}


def test_a_covered_day_reads_every_docket_with_complete_writing_roles() -> None:
    dockets = _day(ORDER_LIST)
    carter = dockets["25-885"]
    assert carter.problems == []
    assert carter.complete is False
    assert carter.writings_complete is True
    assert {v.justice: (v.vote, v.writing) for v in carter.votes} == {
        "Thomas": (VoteValue.grant, WritingRole.none),
        "Alito": (VoteValue.grant, WritingRole.dissent),
    }
    # Every participating Justice's writing role is observed, silent ones included.
    assert carter.writing_roles["Kagan"] is WritingRole.none
    assert set(carter.writing_roles) == set(BENCH)

    carr = dockets["25-1309"]
    assert [(v.justice, v.vote) for v in carr.votes] == [("Alito", VoteValue.did_not_participate)]
    assert "Alito" not in carr.writing_roles  # took no part, so wrote nothing to observe

    assert {v.justice for v in dockets["25-748"].votes} == {"Sotomayor", "Kagan", "Jackson"}
    assert dockets["25-7460"].writings[0].kind == "dissent"
    assert dockets["25-7460"].votes == []
    assert dockets["25-7457"].votes == [] and dockets["25-7457"].writings_complete


def test_an_uncovered_day_records_authors_only() -> None:
    carter = _day(ORDER_LIST, covers=False)["25-885"]
    assert carter.writings_complete is False
    assert carter.writing_roles == {"Alito": WritingRole.dissent}
    assert {v.justice: v.writing for v in carter.votes} == {
        "Thomas": None,
        "Alito": WritingRole.dissent,
    }


RELATING = """1  Cite as: 608 U. S. ____ (2026)
ALITO, J., dissenting
SUPREME COURT OF THE UNITED STATES
UNITED STATES v. DONTE J. CARTER
No. 25\u2013885. Decided June 22, 2026
The petition for a writ of certiorari is denied.
JUSTICE ALITO, with whom JUSTICE THOMAS joins, dissenting
from the denial of certiorari.
On a September afternoon in 2020, several officers approached.
"""


def test_the_same_writing_in_two_documents_is_one_writing() -> None:
    carter = _day(ORDER_LIST, RELATING)["25-885"]
    assert len(carter.writings) == 1
    assert len(carter.documents) == 2
    assert carter.writings_complete


def test_a_running_head_with_no_header_read_is_a_problem() -> None:
    missed = RELATING.replace(
        "JUSTICE ALITO, with whom JUSTICE THOMAS joins, dissenting\nfrom the denial of "
        + "certiorari.",
        "The dissent of JUSTICE ALITO follows.",
    )
    carter = _day(missed)["25-885"]
    assert any("running head names Alito" in p for p in carter.problems)
    assert carter.votes == [] and not carter.writings_complete


def test_a_justice_read_two_ways_across_documents_empties_the_votes() -> None:
    other = RELATING.replace("dissenting\nfrom the denial", "concurring\nin the denial").replace(
        "ALITO, J., dissenting", "ALITO, J., concurring"
    )
    carter = _day(ORDER_LIST, other)["25-885"]
    assert any("read both as" in p for p in carter.problems)
    assert carter.votes == []


def test_a_section_dated_off_its_document_is_a_problem() -> None:
    late = ORDER_LIST.replace(
        "No. 25\u2013885. Decided June 22, 2026", "No. 25\u2013885. Decided June 23, 2026"
    )
    carter = _day(late)["25-885"]
    assert any("dated 2026-06-23" in p for p in carter.problems)


def test_orphan_text_shaped_like_a_notation_is_a_document_problem() -> None:
    orphaned = ORDER_LIST.replace(
        "CERTIORARI DENIED\n25-7457",
        "CERTIORARI DENIED\nJustice Alito would grant the petition.\n25-7457",
    )
    reading = read_documents(
        [FetchedDocument("https://www.supremecourt.gov/orders/courtorders/x.pdf", None, orphaned)],
        day=DAY,
        covers_the_day=True,
    )
    assert reading.documents[0].problems
    assert not any(d.writings_complete for d in reading.dockets)


# --- listings and the fetch ---------------------------------------------------------

ORDERS_PAGE = (
    "<div><span style='x'>06/22/26 &nbsp;</span> <span><a href='/orders/courtorders/"
    + "062226zor_g314.pdf' target='_blank' >Order List</a></span></div>"
    + "<div><span>06/23/26 &nbsp;</span> <span><a href='/orders/courtorders/062326zr_1.pdf'"
    + ">Miscellaneous Order</a></span></div>"
    + "<div><span>06/22/26 &nbsp;</span> <span><a href='https://example.org/orders/x.pdf'"
    + ">Miscellaneous Order</a></span></div>"
)
RELATING_PAGE = (
    "<table><tr><th>Date</th></tr>"
    + "<tr><td>6/22/26</td><td>25-885</td><td><a href='/opinions/25pdf/25-885_5h26.pdf'>"
    + "United States v. Carter</a></td><td>A</td><td>608/2</td></tr>"
    + "<tr><td>6/22/26</td><td>25-885</td><td><a href='/opinions/25pdf/25-885_5h26.pdf#page=3'>"
    + "United States v. Carter</a></td><td>SS</td><td>608/2</td></tr></table>"
)


def test_the_listings_parse_dates_kinds_and_drop_off_host_links() -> None:
    orders = parse_orders_listing(ORDERS_PAGE)
    assert [(r.day, r.kind) for r in orders] == [
        (date(2026, 6, 22), "order-list"),
        (date(2026, 6, 23), "miscellaneous-order"),
    ]
    (relating,) = parse_relating_listing(RELATING_PAGE)
    assert relating.url == "https://www.supremecourt.gov/opinions/25pdf/25-885_5h26.pdf"


def _client(handler: httpx.MockTransport) -> SupremeCourtClient:
    return SupremeCourtClient(client=httpx.Client(transport=handler), sleep=lambda _s: None)


def _stub_extraction(monkeypatch: pytest.MonkeyPatch) -> None:
    def extract(data: bytes, *, char_cap: int) -> ExtractedText:
        text = data.decode()
        return ExtractedText(text=text[:char_cap], pages=1, truncated=len(text) > char_cap)

    monkeypatch.setattr(order_lineups, "extract_pdf_text", extract)


def test_read_day_fetches_every_listed_document_for_the_date_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_extraction(monkeypatch)
    requested: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path == "/orders/ordersofthecourt/25":
            return httpx.Response(200, text=ORDERS_PAGE)
        if request.url.path == "/opinions/relatingtoorders/25":
            return httpx.Response(200, text=RELATING_PAGE)
        if request.url.path.endswith("062226zor_g314.pdf"):
            return httpx.Response(200, content=ORDER_LIST.encode())
        if request.url.path.endswith("25-885_5h26.pdf"):
            return httpx.Response(200, content=RELATING.encode())
        return httpx.Response(404)

    with _client(httpx.MockTransport(handle)) as client:
        reading = read_day(DAY, OrderFetcher(client, cache_dir=tmp_path))
    assert reading.covers_the_day
    assert [d.status for d in reading.documents] == ["read", "read"]
    assert "/orders/courtorders/062326zr_1.pdf" not in requested  # another date
    assert all(not p.startswith("/orders/x") for p in requested)  # off-host, never asked
    assert {d.docket for d in reading.dockets if d.writings_complete} >= {"25-885", "25-538"}


def test_a_document_that_fails_leaves_the_day_uncovered(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_extraction(monkeypatch)

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/orders/ordersofthecourt/25":
            return httpx.Response(200, text=ORDERS_PAGE)
        if request.url.path == "/opinions/relatingtoorders/25":
            return httpx.Response(200, text=RELATING_PAGE)
        if request.url.path.endswith("062226zor_g314.pdf"):
            return httpx.Response(200, content=ORDER_LIST.encode())
        return httpx.Response(404)

    with _client(httpx.MockTransport(handle)) as client:
        reading = read_day(DAY, OrderFetcher(client))
    assert not reading.covers_the_day
    assert [d.reason for d in reading.documents if d.status == "failed"] == [
        "the document is not served"
    ]
    assert not any(d.writings_complete for d in reading.dockets)


def test_one_url_never_covers_an_order(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_extraction(monkeypatch)

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=RELATING.encode())

    with _client(httpx.MockTransport(handle)) as client:
        fetcher = OrderFetcher(client)
        reading = read_url("https://www.supremecourt.gov/opinions/25pdf/25-885_5h26.pdf", fetcher)
        with pytest.raises(ValueError, match="not an order or opinion PDF"):
            read_url("https://example.org/opinions/25pdf/x.pdf", fetcher)
    (carter,) = reading.dockets
    assert carter.docket == "25-885" and not carter.writings_complete
    assert carter.order_date == DAY


def test_the_command_takes_exactly_one_of_date_or_url() -> None:
    runner = CliRunner()
    both = runner.invoke(
        app,
        ["order-notations", "--date", "2026-06-22", "--url", "https://www.supremecourt.gov/a.pdf"],
    )
    neither = runner.invoke(app, ["order-notations"])
    off_host = runner.invoke(app, ["order-notations", "--url", "https://example.org/a.pdf"])
    assert (both.exit_code, neither.exit_code, off_host.exit_code) == (2, 2, 2)


def test_the_command_prints_one_reading_per_docket(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_extraction(monkeypatch)

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=RELATING.encode())

    monkeypatch.setattr(
        "fedcourtsai.cli.SupremeCourtClient",
        lambda **_kw: _client(httpx.MockTransport(handle)),
    )
    result = CliRunner().invoke(
        app, ["order-notations", "--url", "https://www.supremecourt.gov/opinions/25pdf/25-885.pdf"]
    )
    assert result.exit_code == 0, result.output
    assert '"docket": "25-885"' in result.stdout
    assert "1 dockets" in result.stderr and "not covered" in result.stderr


# --- regressions: each would otherwise mis-assign, invent or over-complete -------


def test_a_problem_on_a_document_that_names_no_docket_uncovers_the_day() -> None:
    undated = RELATING.replace("No. 25\u2013885. Decided June 22, 2026", "No. 25\u2013885.")
    reading = read_documents(
        [
            FetchedDocument(
                "https://www.supremecourt.gov/orders/courtorders/a.pdf", None, ORDER_LIST
            ),
            FetchedDocument("https://www.supremecourt.gov/opinions/25pdf/b.pdf", None, undated),
        ],
        day=DAY,
        covers_the_day=True,
    )
    assert reading.documents[1].problems
    assert reading.documents[1].dockets == []
    assert not reading.covers_the_day
    assert not any(d.writings_complete for d in reading.dockets)


def test_a_wrapped_line_opening_on_a_docket_number_is_not_a_caption() -> None:
    split = split_document(
        "25-100 SMITH V. JONES\n"
        + "  The motion to consolidate this case with No.\n"
        + "25-200 and a total of one hour is allotted for oral argument.\n"
        + "Justice Alito took no part in the consideration or decision of this petition.\n"
    )
    assert [p.dockets for p in split.pieces] == [("25-100",)]


# The shape the order list of February 24, 2025 prints a consolidated caption
# in: the docket numbers alone, a column of brackets, one caption line each.
CONSOLIDATED_CAPTIONS = """(ORDER LIST: 604 U.S.)
MONDAY, FEBRUARY 24, 2025
CERTIORARI -- SUMMARY DISPOSITIONS
24-100 ROE, JANE V. DOE, JOHN
  The motion for leave to file under seal is granted.
23-1067
23-1068
)
 )
)
 OKLAHOMA, ET AL. V. EPA, ET AL.
 PACIFICORP, ET AL. V. EPA, ET AL.
  The motion of petitioners for divided argument is granted.
 Justice Alito took no part in the consideration or decision of
this motion.
23-1229 EPA V. CALUMET SHREVEPORT RFG., ET AL.
  The motion of respondents in support of petitioner for
divided argument is granted.
24-354
24-422
 )
)
)
FCC, ET AL. V. CONSUMERS' RESEARCH, ET AL.
SHLB COALITION, ET AL. V. CONSUMERS' RESEARCH, ET AL.
  The motion of the Acting Solicitor General for divided
 argument is granted.
"""


def test_a_consolidated_caption_printed_as_bare_dockets_opens_one_entry() -> None:
    split = split_document(CONSOLIDATED_CAPTIONS)
    assert split.problems == ()
    by_dockets = {p.dockets: p.text for p in split.pieces}
    assert list(by_dockets) == [
        ("24-100",),
        ("23-1067", "23-1068"),
        ("23-1229",),
        ("24-354", "24-422"),
    ]
    assert by_dockets[("23-1067", "23-1068")].endswith(
        "Justice Alito took no part in the consideration or decision of this motion."
    )
    # Neither the next entry's docket numbers nor its brackets run into the one above.
    assert by_dockets[("24-100",)] == "The motion for leave to file under seal is granted."
    assert by_dockets[("23-1229",)].endswith("divided argument is granted.")
    assert by_dockets[("24-354", "24-422")].startswith("The motion of the Acting Solicitor")


# The shape the long-conference order lists (October 7, 2024; October 6, 2025;
# October 5, 2026) extract to: on some pages the serial of every caption whose
# number ends in 0 or 5 is lifted out of its line, the caption keeping only
# ``25-``, and the page's lifted serials land together as a column of bare
# numbers above its captions, after the page number. Captions are invented or
# institutional; the layout (padding, blank lines, trailing spaces) is the
# extracted text's.
LIFTED_SERIALS = "\n".join(
    [
        "(ORDER LIST: 607 U.S.)",
        "MONDAY, OCTOBER 5, 2026",
        "CERTIORARI DENIED",
        "25-1030 DOE, JANE V. UNITED STATES ",
        "25-1373   ACME CORP. V. ROE, JOHN, ET AL. ",
        "10 ",
        " ",
        "    ",
        "       ",
        "1375 ",
        "1380 ",
        "1385  ",
        "25-1374   SMITH, JOHN V. UNITED STATES ",
        "25- ROE, RICHARD V. ACME CORP. ",
        "25-1377   DOE, JOHN V. TEXAS ",
        "25-1379 ROE, JANE V. JONES, WARDEN ",
        "25- UNITED STATES V. DOE, JANE ",
        "25-1382 NATIONAL ASSN. OF ACME V. FTC ",
        "25-1384 SMITH, JANE V. FLORIDA ",
        "25-  DOE, RICHARD V. ROE, JOHN, ET AL. ",
        "25-1386   JONES, JOHN V. UNITED STATES ",
        "11 ",
        "  The petitions for writs of certiorari are denied. ",
        "",
    ]
)


def test_lifted_serials_are_rejoined_to_their_captions() -> None:
    split = split_document(LIFTED_SERIALS)
    assert split.problems == ()
    (entry,) = split.pieces
    assert entry.dockets == (
        "25-1030",
        "25-1373",
        "25-1374",
        "25-1375",
        "25-1377",
        "25-1379",
        "25-1380",
        "25-1382",
        "25-1384",
        "25-1385",
        "25-1386",
    )
    # The column is not read as any entry's order text.
    assert entry.text == "The petitions for writs of certiorari are denied."


def test_a_column_that_does_not_fit_its_captions_is_a_problem_not_a_guess() -> None:
    # 1390 cannot sit between 25-1374 and 25-1377, so no serial is rejoined.
    split = split_document(LIFTED_SERIALS.replace("1375 \n", "1390 \n", 1))
    assert any("could not be rejoined" in p for p in split.problems)
    dockets = {d for p in split.pieces for d in p.dockets}
    assert not dockets & {"25-1375", "25-1380", "25-1385", "25-1390"}
    # Every entry still reads the real order, never the column.
    assert {p.text for p in split.pieces} == {"The petitions for writs of certiorari are denied."}


def test_a_lifted_caption_with_no_column_is_a_problem() -> None:
    split = split_document(
        LIFTED_SERIALS.replace("1375 \n1380 \n1385  \n", "").replace("10 \n", "")
    )
    assert sum("printed without a serial" in p for p in split.problems) == 3
    assert {p.text for p in split.pieces} == {"The petitions for writs of certiorari are denied."}


def test_a_column_no_caption_claims_is_dropped_as_a_problem() -> None:
    split = split_document(
        "CERTIORARI DENIED\n"
        + "25-1030 DOE, JANE V. UNITED STATES\n"
        + "1375\n"
        + "1380\n"
        + "25-1374 SMITH, JOHN V. UNITED STATES\n"
        + "  The petitions for writs of certiorari are denied.\n"
    )
    assert any("no caption claims: '1375 1380'" in p for p in split.problems)
    (entry,) = split.pieces
    assert entry.dockets == ("25-1030", "25-1374")


def test_entry_text_with_no_letters_is_a_problem() -> None:
    split = split_document(
        "CERTIORARI DENIED\n"
        + "25-1030 DOE, JANE V. UNITED STATES\n"
        + "  --- ; 12.\n"
        + "25-1374 SMITH, JOHN V. UNITED STATES\n"
        + "  The petition for a writ of certiorari is denied.\n"
    )
    assert any("has no letters" in p for p in split.problems)


def test_a_bracket_line_between_two_captions_does_not_end_the_first() -> None:
    # The shape of the order list of October 21, 2024: each caption line carries
    # its bracket, and a lone bracket line sits between them.
    split = split_document(
        "CERTIORARI GRANTED\n"
        + "23-1067  )  OKLAHOMA, ET AL. V. EPA, ET AL.\n"
        + ") \n"
        + "23-1068  )  PACIFICORP, ET AL. V. EPA, ET AL.\n"
        + "  The petitions for writs of certiorari are granted.  The\n"
        + "cases are consolidated. Justice Alito took no part in the\n"
        + "consideration or decision of these petitions.\n"
    )
    assert split.problems == ()
    (entry,) = split.pieces
    assert entry.dockets == ("23-1067", "23-1068")
    assert entry.text.endswith(
        "Justice Alito took no part in the consideration or decision of these petitions."
    )


def test_a_docket_number_left_alone_by_a_wrap_is_not_a_caption() -> None:
    split = split_document(
        "25-100 SMITH V. JONES\n"
        + "  The motion to consolidate this case with No.\n"
        + "25-200\n"
        + "is granted.  Justice Alito took no part in the consideration or decision of\n"
        + "this motion.\n"
    )
    assert split.problems == ()
    (entry,) = split.pieces
    assert entry.dockets == ("25-100",)
    assert "No. 25-200 is granted." in entry.text


def test_a_docket_number_left_alone_before_a_section_heading_is_not_a_caption() -> None:
    split = split_document(
        "CERTIORARI GRANTED\n"
        + "25-100 SMITH V. JONES\n"
        + "  The petition is granted. The case is consolidated with No.\n"
        + "25-200\n"
        + "CERTIORARI DENIED\n"
        + "25-300 DOE V. ROE\n"
        + "  The petition is denied. Justice Alito would grant the petition.\n"
    )
    assert split.problems == ()
    assert [p.dockets for p in split.pieces] == [("25-100",), ("25-300",)]


def test_a_body_line_opening_on_a_name_is_not_a_header() -> None:
    body = RELATING + (
        "JUSTICE KAGAN, dissenting from the denial of certiorari in Doe v.\n"
        + "Roe, warned that the question would recur.\n"
    )
    carter = _day(body)["25-885"]
    assert [w.authors for w in carter.writings] == [["Alito"]]
    assert carter.problems == []


def test_a_header_no_running_head_names_is_a_problem() -> None:
    extra = RELATING + "JUSTICE GORSUCH, dissenting.\nI would grant.\n"
    carter = _day(extra)["25-885"]
    assert any("header by Gorsuch has no running head" in p for p in carter.problems)
    assert carter.votes == []
    assert not carter.writings_complete


def test_it_is_so_ordered_in_an_order_keeps_the_notation_before_it() -> None:
    order = (
        "SUPREME COURT OF THE UNITED STATES\nNo. 25A100\nSMITH v. JONES\n"
        + "ON APPLICATION FOR STAY\n[June 22, 2026]\n"
        + "The application for stay is granted. Justice Alito would deny the application. It is"
        + " so ordered.\n"
    )
    reading = _day(order)["25A100"]
    assert [(v.justice, v.vote) for v in reading.votes] == [("Alito", VoteValue.deny)]


def test_orphan_act_text_is_a_problem_and_a_citation_line_does_not_close_an_entry() -> None:
    orphaned = split_document(
        "CERTIORARI DENIED\n25-1 A V. B\n  The petition is denied.\nHABEAS CORPUS DENIED\n"
        + "Justice Alito dissents from the denial of certiorari.\n"
    )
    assert orphaned.problems
    wrapped = split_document(
        "25-2 C V. D\n  The petition is denied, as in Powell, 608 U. S.\n___ (2026).  Justice"
        + " Thomas would grant the petition.\n"
    )
    (entry,) = wrapped.pieces
    assert "Thomas would grant" in entry.text


def test_a_section_with_no_pieces_still_seats_its_bench() -> None:
    per_curiam = (
        " Cite as: 608 U. S. ____ (2026) 1\nPer Curiam\nSUPREME COURT OF THE UNITED STATES\n"
        + "No. 25\u2013300. Decided June 22, 2026\n PER CURIAM.\nWe reverse.\nIt is so ordered.\n"
    )
    reading = _day(per_curiam)["25-300"]
    assert reading.bench == list(BENCH)
    assert reading.writings_complete
    assert set(reading.writing_roles) == set(BENCH)


def test_a_long_name_list_that_fails_to_match_does_not_backtrack_exponentially() -> None:
    names = ", and ".join(["Justice Alito"] * 40)
    started = time.monotonic()
    parse_order_notations(f"{names} xyz.", bench=BENCH)
    parse_writing_header(f"{names} xyz.", bench=BENCH)
    split_document("SUPREME COURT OF THE UNITED STATES\nNo. " + "1 " * 20_000 + "\n")
    assert time.monotonic() - started < 2.0


def test_a_path_that_climbs_out_of_the_orders_tree_is_not_an_order_document() -> None:
    assert not vote_sources.is_order_document_url("https://www.supremecourt.gov/orders/../x.pdf")


def test_a_plural_unwritten_dissent_is_read_and_a_bare_one_is_not() -> None:
    assert _notes(
        "The application is granted.  Justice Sotomayor and Justice Jackson dissent from the"
        + " grant of the application."
    ) == {"Sotomayor": VoteValue.deny, "Jackson": VoteValue.deny}
    assert parse_order_notations("Justice Thomas dissents.", bench=BENCH).problems
