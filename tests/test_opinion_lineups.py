"""The opinions vote channel: listing, paragraph locator, bench, and record.

Every fixture is text shaped like what the Court's site serves — a listing
table, or an opinion's extracted text with its running heads and text-layer
artifacts — written out here. The fetcher is exercised over an in-memory
transport, so nothing in this file touches the network.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError

from fedcourtsai.pipeline.lineup import (
    Lineup,
    WritingKind,
    justice_votes,
    writing_role,
)
from fedcourtsai.pipeline.opinion_lineups import (
    OpinionFetcher,
    OpinionListing,
    locate_lineup,
    parse_listing,
    read_entry,
    read_term,
    read_text,
    select,
    vote_record,
)
from fedcourtsai.pipeline.syllabus_lineup import GRAMMAR_NAME, GRAMMAR_VERSION
from fedcourtsai.schemas import (
    Disposition,
    GrammarStamp,
    Judgment,
    JusticeVote,
    Outcome,
    VoteProvenance,
    VoteValue,
    WritingRole,
)
from fedcourtsai.supremecourt import SupremeCourtClient

_ROW = (
    "<tr><td>{n}</td><td>{d}</td><td>{docket}</td>"
    + "<td><a href='{href}' target='_blank' title=\"Held: …\">{name}</a>{extra}</td>"
    + "<td>{j}</td><td><span>{cite}</span></td></tr>"
)


def _row(
    n: str,
    d: str,
    docket: str,
    href: str,
    name: str,
    j: str,
    cite: str = "609/2",
    extra: str = "",
) -> str:
    return _ROW.format(n=n, d=d, docket=docket, href=href, name=name, j=j, cite=cite, extra=extra)


LISTING = (
    "<table><tr><th>R-</th><th>Date</th><th>Docket</th><th>Name</th><th>J.</th>"
    + "<th>Citation</th></tr>"
    + _row(
        "68",
        "6/30/26",
        "24-43",
        "/opinions/25pdf/24-43_2b35.pdf",
        "West Virginia v. B. P. J.",
        "BK",
    )
    + _row(
        "66",
        "6/30/26",
        "25-365",
        "/opinions/25pdf/25-365_new_5if6.pdf",
        "Trump v. Barbara",
        "R",
        extra=" Revisions : <a href='/opinions/25pdf/25-365_diff_ed9g.pdf'>7/01/26</a>",
    )
    + _row("73", "9/25/26", "26A388", "/opinions/25pdf/26a388_q86b.pdf", "People v. Onder", "PC")
    + _row(
        "D1", "5/26/26", "141, Orig.", "/opinions/25pdf/608us1r36d.pdf", "Texas v. New Mexico", "D"
    )
    + _row(
        "36", "5/26/26", "25-767", "/opinions/25pdf/608us1r36_n758.pdf", "Margolin v. NAIJ", "PC"
    )
    + _row(
        "2",
        "11/02/20",
        "19-1261",
        "/opinions/preliminaryprint/592US1PP_web.pdf#page=47",
        "Taylor v. Riojas",
        "BK",
    )
    + _row("5", "12/10/21", "21-588 (21A85)", "/opinions/21pdf/21-588_x.pdf", "US v. Texas", "BK")
    + "</table>"
)

# A slip opinion's closing syllabus page, as pypdf extracts it: the running
# head of a page break mid-paragraph, the small-capitals split "S OTOMAYOR",
# then the rule and notice that open the opinion.
SLIP = """ 1 (Slip Opinion) OCTOBER TERM, 2025
Syllabus
SUPREME COURT OF THE UNITED STATES
Syllabus
WEST VIRGINIA ET AL. v. B. P. J.
No. 24\u201343. Argued January 13, 2026—Decided June 30, 2026*
The question before the Court is whether schools may maintain teams.
No. 24\u201343, 98 F. 4th 542, reversed and
remanded.
KAVANAUGH, J., delivered the opinion of the Court, in which ROBERTS,
C. J., and THOMAS, ALITO, GORSUCH, and BARRETT, JJ., joined.  THOMAS,

5 Cite as: 609 U. S. ___ (2026)
Syllabus
J., and GORSUCH, J., filed concurring opinions.  S OTOMAYOR, J., filed an
opinion concurring in the judgment in part and dissenting in part, in
which KAGAN and JACKSON, JJ., joined.  JACKSON, J., filed an opinion con-
curring in the judgment in part and dissenting in part.

_________________
1  Cite as: 609 U. S. ____ (2026)
Opinion of the Court
NOTICE: This opinion is subject to formal revision before publication.
 JUSTICE KAVANAUGH delivered the opinion of the Court.
"""

# A preliminary print: mixed case, the dropped "fi" ligature, page cites, a
# caption hyphenated across lines, a reargument, and the counsel list that
# follows the paragraph.
PRINT = """PRELIMINARY PRINT
Syllabus
LOUISIANA v. CALLAIS
No. 24\u2013109. Argued March 24, 2025—Reargued October 15, 2025—De-
cided April 29, 2026
Held: something. Pp. 5\u201320.
Alito, J., delivered the opinion of the Court, in which Roberts, C. J.,
and Thomas, Gorsuch, Kavanaugh, and Barrett, JJ., joined.
Thomas, J., fled a concurring opinion, in which Gorsuch, J., joined, post,
p. 126. Kagan, J., fled a dissenting opinion, in which Sotomayor and
Jackson, JJ., joined, post, p. 127.
Michael L. Zuckerman, Deputy Solicitor General of New
York, argued the cause for the State.
Justice Alito delivered the opinion of the Court.
"""


def _entry(
    docket: str = "24-43", author: str = "BK", decided: date = date(2026, 6, 30)
) -> OpinionListing:
    return OpinionListing(
        term=25,
        number="68",
        decided=decided,
        docket=docket,
        name="West Virginia v. B. P. J.",
        url=f"https://www.supremecourt.gov/opinions/25pdf/{docket}_2b35.pdf",
        author_code=author,
    )


# --- the listing ---------------------------------------------------------------


def test_the_listing_reads_every_opinion_row_and_only_those() -> None:
    rows = parse_listing(LISTING, term=25)
    assert [r.docket for r in rows] == [
        "24-43",
        "25-365",
        "26A388",
        "141, Orig.",
        "25-767",
        "19-1261",
        "21-588 (21A85)",
    ]
    first = rows[0]
    assert first.url == "https://www.supremecourt.gov/opinions/25pdf/24-43_2b35.pdf"
    assert first.decided == date(2026, 6, 30)
    assert first.author_code == "BK"
    assert first.name == "West Virginia v. B. P. J."
    # A revised opinion's revision link is not the opinion.
    assert rows[1].url.endswith("25-365_new_5if6.pdf")
    assert rows[1].name == "Trump v. Barbara"


def test_docket_forms_and_volume_links() -> None:
    rows = {r.docket: r for r in parse_listing(LISTING, term=25)}
    assert rows["24-43"].docket_number == "24-43"
    assert rows["21-588 (21A85)"].docket_number == "21-588"
    assert rows["26A388"].docket_number is None
    assert rows["141, Orig."].docket_number is None
    assert rows["19-1261"].volume_linked
    assert not rows["24-43"].volume_linked


def test_rows_outside_the_channel_are_skipped_before_any_fetch() -> None:
    """An application, an original action, a per curiam, a volume link."""

    class _NoFetch:
        def opinion(self, url: str) -> bytes | None:
            raise AssertionError(f"fetched {url}")

    reasons = {
        r.docket: read_entry(r, _NoFetch()).reason  # type: ignore[arg-type]
        for r in parse_listing(LISTING, term=25)
        if r.docket in {"26A388", "141, Orig.", "25-767", "19-1261"}
    }
    assert reasons["26A388"] is not None and "application" in reasons["26A388"]
    assert reasons["141, Orig."] is not None and "original" in reasons["141, Orig."]
    assert reasons["25-767"] is not None and reasons["25-767"].startswith("per curiam")
    assert reasons["19-1261"] is not None and reasons["19-1261"].startswith("volume-linked")


def test_select_caps_in_scope_rows_and_filters_by_docket() -> None:
    rows = parse_listing(LISTING, term=25)
    capped = select(rows, limit=1)
    assert [r.docket for r in capped] == ["24-43"]
    two = select(rows, limit=2)
    # The cut falls at the first in-scope row past the cap; skipped rows before
    # it are listed with their reasons.
    assert [r.docket for r in two] == [
        "24-43",
        "25-365",
        "26A388",
        "141, Orig.",
        "25-767",
        "19-1261",
    ]
    assert [r.docket for r in select(rows, dockets=["21-588"])] == ["21-588 (21A85)"]


# --- locating the paragraph ------------------------------------------------------


def test_the_slip_paragraph_is_located_across_a_page_break() -> None:
    located = locate_lineup(SLIP)
    assert located.problems == ()
    assert located.argued == date(2026, 1, 13)
    assert located.decided == date(2026, 6, 30)
    assert located.paragraph is not None
    assert "Cite as" not in located.paragraph and "Syllabus" not in located.paragraph
    assert "SOTOMAYOR, J., filed" in located.paragraph
    assert located.paragraph.rstrip().endswith("dissenting in part.")


def test_the_print_paragraph_ends_at_the_counsel_list() -> None:
    """A hyphenated caption still dates the case, and a reargument is the argument."""
    located = locate_lineup(PRINT)
    assert located.problems == ()
    assert located.argued == date(2025, 10, 15)
    assert located.decided == date(2026, 4, 29)
    assert located.paragraph is not None
    assert "Zuckerman" not in located.paragraph
    assert located.paragraph.rstrip().endswith("p. 127.")


def test_a_wrapped_scope_word_does_not_end_the_paragraph() -> None:
    """`Part V. Kagan, J., filed` opens on two capitalized words and a comma.

    That is the counsel-line shape, but here it is a join's scope wrapped to
    the next line, and ending the paragraph there would drop Kagan's dissent —
    a lineup cut short, which reads as more unanimous than it was.
    """
    text = (
        "No. 20\u20131. Argued March 1, 2021\u2014Decided June 1, 2021\n"
        + "Alito, J., delivered the opinion of the Court, in which Roberts, C. J.,\n"
        + "and Thomas, Gorsuch, Kavanaugh, and Barrett, JJ., joined. Thomas, J.,\n"
        + "fled a concurring opinion, in which Breyer, J., joined as to\n"
        + "Part V. Kagan, J., fled a dissenting opinion, in which Sotomayor, J.,\n"
        + "joined.\n"
        + "Michael L. Zuckerman, Deputy Solicitor General, argued the cause.\n"
    )
    located = locate_lineup(text)
    assert located.paragraph is not None
    assert located.paragraph.endswith("joined.")
    assert "Zuckerman" not in located.paragraph


def test_with_no_argument_date_a_newly_seated_justice_is_never_credited() -> None:
    """Missing the printed argument date must not switch the guard off.

    Decided 2018-12-10 with no argument date printed: Kavanaugh, sworn in on
    2018-10-06, could have missed the argument, so a silent unanimous
    paragraph cannot credit him and yields no record.
    """
    text = (
        "No. 17\u20131. Decided December 10, 2018\n"
        + "GINSBURG, J., delivered the opinion for a unanimous Court.\n"
        + "NOTICE: This opinion is subject to formal revision.\n"
    )
    entry = _entry(docket="17-1", author="G", decided=date(2018, 12, 10))
    reading = read_text(entry, text, truncated=False)
    assert reading.seated_after_argument == ["Kavanaugh"]
    assert not reading.complete and reading.votes is None


def test_a_paragraph_running_into_the_extraction_cap_is_refused() -> None:
    """A truncated paragraph reads as a unanimous one, so it is never read."""
    cut = SLIP.split("_________________", maxsplit=1)[0]
    refused = locate_lineup(cut, truncated=True)
    assert refused.paragraph is None
    assert "extraction cap" in refused.problems[0]


def test_a_paragraph_running_off_the_end_of_the_text_is_refused() -> None:
    """Text that stops inside the lineup is cut short, cap or no cap.

    The opinion always follows its syllabus, so a damaged or partial document
    can end the text mid-paragraph without the extraction cap being reached;
    read as it stands, the silent Justices would be credited to the lead.
    """
    cut = SLIP.split("_________________", maxsplit=1)[0]
    refused = locate_lineup(cut)
    assert refused.paragraph is None
    assert refused.problems == ("the lineup paragraph runs to the end of the text",)


def test_text_with_no_lead_sentence_locates_nothing() -> None:
    located = locate_lineup("Per Curiam.\nThe petition for certiorari is granted.")
    assert located.paragraph is None
    assert located.problems == ("no syllabus lineup paragraph found",)


# --- reading one opinion -----------------------------------------------------------


def test_a_slip_opinion_reads_to_a_complete_vote_record() -> None:
    reading = read_text(_entry(), SLIP, truncated=False)
    assert reading.status == "read"
    assert reading.complete and reading.problems == []
    assert reading.seated_after_argument == []
    assert reading.votes is not None and reading.vote_provenance is not None
    votes = {v.justice: v for v in reading.votes}
    assert votes["Kavanaugh"].vote == VoteValue.majority
    assert votes["Kavanaugh"].writing == WritingRole.majority
    assert votes["Roberts"].writing == WritingRole.none
    assert votes["Thomas"].writing == WritingRole.concurrence
    assert votes["Sotomayor"].vote == VoteValue.concur_in_part
    # A mixed writing has no single role, so it records "not stated".
    assert votes["Sotomayor"].writing is None
    assert votes["Kagan"].vote == VoteValue.concur_in_part
    assert reading.vote_provenance == VoteProvenance(
        source="supremecourt-opinions",
        documents=["https://www.supremecourt.gov/opinions/25pdf/24-43_2b35.pdf"],
        grammars=[GrammarStamp(grammar=GRAMMAR_NAME, version=GRAMMAR_VERSION)],
        participating=9,
        complete=True,
    )


def test_a_justice_seated_after_argument_and_silent_leaves_it_incomplete() -> None:
    """Argued 2020-10-05, decided 2021-04-05: Barrett missed the argument.

    A unanimous Court clause would credit her by the Court's convention; the
    channel passes her as seated after argument, so only the paragraph can
    place her, and a paragraph silent about her yields no vote record.
    """
    text = (
        "No. 18\u2013956. Argued October 7, 2020—Decided April 5, 2021\n"
        + "BREYER, J., delivered the opinion for a unanimous Court.\n"
        + "NOTICE: This opinion is subject to formal revision.\n"
    )
    entry = _entry(docket="18-956", author="B", decided=date(2021, 4, 5))
    silent = read_text(entry, text, truncated=False)
    assert silent.seated_after_argument == ["Barrett"]
    assert not silent.complete and silent.votes is None
    named = read_text(
        entry,
        text.replace(
            "Court.\n", "Court. BARRETT, J., took no part in the consideration or decision.\n"
        ),
        truncated=False,
    )
    assert named.complete and named.votes is not None
    assert {v.justice: v.vote for v in named.votes}["Barrett"] == VoteValue.did_not_participate
    assert named.vote_provenance is not None and named.vote_provenance.participating == 8


def test_a_listing_author_the_lead_does_not_name_withholds_the_record() -> None:
    reading = read_text(_entry(author="EK"), SLIP, truncated=False)
    assert reading.complete  # the lineup itself read cleanly
    assert reading.votes is None and reading.vote_provenance is None
    assert any("the listing names Kagan as author" in p for p in reading.problems)


def test_a_listing_date_the_opinion_does_not_print_withholds_the_record() -> None:
    reading = read_text(_entry(decided=date(2026, 6, 29)), SLIP, truncated=False)
    assert reading.votes is None
    assert any("printed decision date 2026-06-30" in p for p in reading.problems)


def test_a_decision_before_the_roster_floor_fails() -> None:
    text = (
        "No. 15\u20131. Argued March 1, 2016—Decided June 1, 2016\n" + SLIP.split("remanded.\n")[1]
    )
    reading = read_text(_entry(decided=date(2016, 6, 1)), text, truncated=False)
    assert reading.status == "failed"
    assert reading.reason is not None and "no bench roster before" in reading.reason


def test_only_a_complete_lineup_yields_a_vote_record() -> None:
    incomplete = Lineup(court="scotus", grammar=GRAMMAR_NAME, grammar_version=2, bench=("Alito",))
    with pytest.raises(ValueError, match="only a complete lineup"):
        vote_record(incomplete, document="https://www.supremecourt.gov/x.pdf")


# --- the writing-role projection -----------------------------------------------


def test_writing_role_maps_single_roles_and_withholds_mixed_ones() -> None:
    assert writing_role(()) is WritingRole.none
    assert writing_role((WritingKind.opinion_of_the_court,)) is WritingRole.majority
    assert writing_role((WritingKind.dissent, WritingKind.dissent)) is WritingRole.dissent
    assert writing_role((WritingKind.concurrence_in_part,)) is None
    assert writing_role((WritingKind.concurrence_in_part_dissent_in_part,)) is None
    assert writing_role((WritingKind.opinion_of_the_court, WritingKind.concurrence)) is None


def test_an_incomplete_reading_never_claims_a_justice_wrote_nothing() -> None:
    lineup = Lineup(
        court="scotus",
        grammar=GRAMMAR_NAME,
        grammar_version=2,
        bench=("Alito", "Kagan"),
        votes={"Alito": VoteValue.majority, "Kagan": VoteValue.majority},
    )
    assert [v.writing for v in justice_votes(lineup)] == [None, None]


# --- the record's schema -----------------------------------------------------------


def _outcome(**record: object) -> Outcome:
    return Outcome.model_validate(
        {
            "case_id": "scotus/1",
            "event_id": "evt-order-judgment",
            "resolved_at": date(2026, 6, 30),
            "actual_disposition": Disposition.other,
            "actual_granted": 1,
            "judgment": Judgment.reversed,
            **record,
        }
    )


_SIX = [JusticeVote(justice=f"J{i}", vote=VoteValue.majority) for i in range(6)]
_COMPLETE_SIX = VoteProvenance(source="supremecourt-opinions", participating=6, complete=True)


def test_a_complete_record_counts_its_participating_votes() -> None:
    assert _outcome(votes=_SIX, vote_provenance=_COMPLETE_SIX).vote_provenance is not None
    recused = [*_SIX, JusticeVote(justice="J6", vote=VoteValue.recused)]
    assert _outcome(votes=recused, vote_provenance=_COMPLETE_SIX).votes == recused
    with pytest.raises(ValidationError, match="counts 5 participating"):
        _outcome(votes=_SIX[:5], vote_provenance=_COMPLETE_SIX)


def test_a_provenance_block_must_describe_a_list() -> None:
    with pytest.raises(ValidationError, match="`writing_roles` are empty"):
        _outcome(vote_provenance=_COMPLETE_SIX)
    with pytest.raises(ValidationError, match="more than once"):
        _outcome(votes=[*_SIX, _SIX[0]], vote_provenance=_COMPLETE_SIX)
    # A partial record's count is not checked: the rest are unobserved.
    partial = _COMPLETE_SIX.model_copy(update={"complete": False})
    assert _outcome(votes=_SIX[:2], vote_provenance=partial).votes == _SIX[:2]


def test_a_grammar_is_stamped_with_its_version_once() -> None:
    with pytest.raises(ValidationError, match="version"):
        GrammarStamp.model_validate({"grammar": "scotus-syllabus"})
    stamp = GrammarStamp(grammar="scotus-syllabus", version=2)
    with pytest.raises(ValidationError, match="more than once"):
        VoteProvenance(source="x", participating=9, complete=True, grammars=[stamp, stamp])


# --- the fetch -------------------------------------------------------------------


def _client(handler: httpx.MockTransport) -> SupremeCourtClient:
    return SupremeCourtClient(client=httpx.Client(transport=handler), sleep=lambda _s: None)


def test_the_fetcher_caches_opinions_but_never_the_listing(tmp_path: Path) -> None:
    seen: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        if request.url.path == "/opinions/slipopinion/25":
            return httpx.Response(200, text=LISTING)
        return httpx.Response(200, content=b"%PDF-not-really")

    with _client(httpx.MockTransport(handle)) as client:
        fetcher = OpinionFetcher(client, cache_dir=tmp_path / "cache")
        assert len(fetcher.listing(25)) == 7
        url = "https://www.supremecourt.gov/opinions/25pdf/24-43_2b35.pdf"
        assert fetcher.opinion(url) == b"%PDF-not-really"
        assert fetcher.opinion(url) == b"%PDF-not-really"
        fetcher.listing(25)
    # Written whole: no partial file is left beside the cached one.
    assert [p.suffix for p in (tmp_path / "cache").iterdir()] == [".pdf"]
    assert seen.count("https://www.supremecourt.gov/opinions/25pdf/24-43_2b35.pdf") == 1
    assert seen.count("https://www.supremecourt.gov/opinions/slipopinion/25") == 2


def test_a_row_whose_pdf_yields_nothing_or_is_not_served_fails_with_a_reason() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/opinions/slipopinion/25":
            return httpx.Response(200, text=LISTING)
        if request.url.path.endswith("24-43_2b35.pdf"):
            return httpx.Response(200, content=b"not a pdf")
        return httpx.Response(404)

    with _client(httpx.MockTransport(handle)) as client:
        readings = read_term(25, OpinionFetcher(client), dockets=["24-43", "25-365"])
    by_docket = {r.docket: r for r in readings}
    assert by_docket["24-43"].status == "failed"
    assert by_docket["24-43"].reason == "the PDF yielded no text"
    assert by_docket["25-365"].reason == "the opinion is not served"


def test_a_listing_link_off_the_courts_host_is_never_fetched() -> None:
    """The listing is upstream text, so its links are held to the host rule."""
    requested: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(200, content=b"")

    entry = OpinionListing(
        term=25,
        number="1",
        decided=date(2026, 6, 30),
        docket="24-43",
        name="X v. Y",
        url="https://example.org/24-43.pdf",
        author_code="BK",
    )
    with _client(httpx.MockTransport(handle)) as client:
        reading = read_entry(entry, OpinionFetcher(client))
    assert reading.status == "failed"
    assert reading.reason is not None and "off the Court's host" in reading.reason
    assert requested == []
