"""The Solicitor General's posted briefs for a paper-only docket (pipeline/sg_briefs.py)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.sg_briefs import (
    FillCandidate,
    OffSectionFetch,
    OsgClient,
    fill_candidates,
    fill_sg_briefs,
    is_osg_url,
    listing_search_url,
    paper_entry_dates,
    parse_listing,
)
from tests.test_documents import _pdf

_TODAY = date(2026, 11, 7)
_PAPER_ONLY = (
    "Pursuant to Rule 34.6 and Paragraph 9 of the Guidelines for the Submission of "
    + "Documents to the Supreme Court's Electronic Filing System, filings in this case "
    + "should be submitted in paper form only."
)
_LIFTED = (
    "As Rule 34.6 provides, 'If the Court schedules briefing and oral argument in a "
    + "case ... the parties shall submit electronic versions of all prior and "
    + "subsequent filings.'"
)


def _entries(*rows: tuple[str, str]) -> dict[str, Any]:
    return {"ProceedingsandOrder": [{"Date": when, "Text": text} for when, text in rows]}


def _row(header: str, body: str) -> str:
    return f'<td headers="view-field-{header}-table-column" class="views-field">{body}</td>'


def _listing_row(
    number: str, brief_type: str, *, pdf: str = "/osg/media/1463386/dl?inline", day: str
) -> str:
    return (
        "<tr>"
        + _row("sc-term", "2025 Term ")
        + _row("number", f"{number} ")
        + _row("title", '<a href="/osg/brief/momin-v-blanche">Momin v. Blanche</a>')
        + _row("brief-attachments", f'<a href="{pdf}" class="file pdf">PDF</a>')
        + _row("brief-type", f"{brief_type} ")
        + _row("topic", "Civil Div. I: General, Immigration")
        + _row("date", f'<time datetime="{day}T12:00:00Z">{day}</time>')
        + "</tr>"
    )


def _listing(*rows: str) -> str:
    head = '<tr><th id="view-field-number-table-column">Docket Number</th></tr>'
    return f'<table class="usa-table"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'


_PAGE_URL = listing_search_url("26-55")


@pytest.mark.parametrize(
    ("url", "ok"),
    [
        ("https://www.justice.gov/osg/media/1463386/dl?inline", True),
        ("https://www.justice.gov/osg/supreme-court-briefs?text=26-55", True),
        ("https://WWW.JUSTICE.GOV/osg/brief/x", True),
        ("http://www.justice.gov/osg/media/1/dl", False),
        ("https://www.justice.gov/opa/pr/x", False),
        ("https://justice.gov/osg/media/1/dl", False),
        ("https://www.justice.gov.example/osg/media/1/dl", False),
        ("https://user@www.justice.gov/osg/media/1/dl", False),
        ("https://www.justice.gov:8443/osg/media/1/dl", False),
        ("https://www.justice.gov/osg/media/1/dl\t", False),
    ],
)
def test_is_osg_url_holds_the_fetch_to_the_offices_section(url: str, ok: bool) -> None:
    assert is_osg_url(url) is ok


def test_listing_search_url_never_builds_a_disallowed_parameter() -> None:
    url = listing_search_url("26-55")
    assert url.startswith("https://www.justice.gov/osg/supreme-court-briefs?text=26-55")
    # robots.txt disallows `?page=` and the `f[...]` facets on this path.
    assert "page=" not in url and "f%5B" not in url and "f[" not in url


def test_parse_listing_reads_cells_by_their_header() -> None:
    page = _listing(
        _listing_row("26-55", "Petition Stage Response", day="2026-09-24"),
        _listing_row("25-1415, 25-1416", "Petition for Writ of Certiorari", day="2026-06-01"),
    )
    rows = parse_listing(page, page_url=_PAGE_URL)
    assert [row.docket_numbers for row in rows] == [("26-55",), ("25-1415", "25-1416")]
    first = rows[0]
    assert first.kind == "brief-in-opposition"
    assert first.pdf_url == "https://www.justice.gov/osg/media/1463386/dl?inline"
    assert first.brief_url == "https://www.justice.gov/osg/brief/momin-v-blanche"
    assert first.filed == date(2026, 9, 24)
    assert first.caption == "Momin v. Blanche"
    assert rows[1].kind == "petition"


def test_parse_listing_drops_an_off_section_link_but_keeps_the_row() -> None:
    page = _listing(
        _listing_row(
            "26-55", "Petition Stage Response", pdf="https://evil.example/x.pdf", day="2026-09-24"
        )
    )
    (row,) = parse_listing(page, page_url=_PAGE_URL)
    assert row.pdf_url is None


def test_an_unmapped_brief_type_has_no_kind() -> None:
    page = _listing(_listing_row("25-246", "Merits Stage Amicus Brief", day="2026-10-13"))
    (row,) = parse_listing(page, page_url=_PAGE_URL)
    assert row.kind is None


def test_paper_entry_dates_read_each_kind_off_its_docket_entry() -> None:
    payload = _entries(
        ("Jul 01 2026", "Petition for a writ of certiorari filed. (Response due August 3, 2026)"),
        ("Jul 02 2026", _PAPER_ONLY),
        (
            "Sep 24 2026",
            "Brief of respondent Todd Blanche, Acting Attorney General in opposition filed.",
        ),
        ("Sep 30 2026", "Brief of respondent Jane Roe in opposition filed."),
        ("Oct 07 2026", "Reply of petitioner Asif Momin filed."),
        ("Oct 08 2026", "DISTRIBUTED for Conference of 10/30/2026."),
    )
    assert paper_entry_dates(payload) == {
        "petition": "Jul 01 2026",
        # The latest opposition: the entry text cannot always tell the
        # government's brief apart, and the later date only places it late.
        "brief-in-opposition": "Sep 30 2026",
        "cert-reply": "Oct 07 2026",
    }


def test_paper_entry_dates_take_no_reply_after_a_disposition() -> None:
    payload = _entries(
        ("Jul 01 2026", "Petition for a writ of certiorari filed."),
        ("Oct 05 2026", "Petition DENIED."),
        ("Oct 20 2026", "Reply of petitioner Asif Momin filed."),
    )
    assert paper_entry_dates(payload) == {"petition": "Jul 01 2026"}


class _Upstream:
    def __init__(self, routes: dict[str, httpx.Response]) -> None:
        self.routes = routes
        self.seen: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.seen.append(url)
        return self.routes.get(url, httpx.Response(404))


def _client(upstream: Callable[[httpx.Request], httpx.Response], sleeps: list[float]) -> OsgClient:
    return OsgClient(
        client=httpx.Client(transport=httpx.MockTransport(upstream)), sleep=sleeps.append
    )


_PDF_URL = "https://www.justice.gov/osg/media/1463386/dl?inline"


def test_the_client_paces_every_request_after_the_first_at_the_crawl_delay() -> None:
    sleeps: list[float] = []
    upstream = _Upstream(
        {
            _PAGE_URL: httpx.Response(200, text=_listing()),
            _PDF_URL: httpx.Response(200, content=_pdf("Brief for the respondents")),
        }
    )
    with _client(upstream, sleeps) as client:
        client.search("26-55")
        assert client.get_pdf(_PDF_URL) is not None
        assert client.requests == 2
    assert sleeps == [10.0]


def test_the_client_refuses_a_redirect_off_the_section() -> None:
    sleeps: list[float] = []
    upstream = _Upstream(
        {_PDF_URL: httpx.Response(302, headers={"Location": "https://evil.example/x.pdf"})}
    )
    with _client(upstream, sleeps) as client, pytest.raises(OffSectionFetch):
        client.get_pdf(_PDF_URL)
    assert upstream.seen == [_PDF_URL]


def test_the_client_answers_none_for_a_body_that_is_not_a_pdf() -> None:
    upstream = _Upstream({_PDF_URL: httpx.Response(200, text="<html>moved</html>")})
    with _client(upstream, []) as client:
        assert client.get_pdf(_PDF_URL) is None


def _seed(db: Path, payload: dict[str, Any], **extra: Any) -> None:
    fields: dict[str, Any] = {
        "last_live_polled": _TODAY,
        "salience_selected": True,
    }
    fields.update(extra)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="26-55", **fields)],
        )
        corpus.upsert_snapshot(conn, "scotus/1", _TODAY, payload)


_PAPER_DOCKET = _entries(
    ("Jul 01 2026", "Petition for a writ of certiorari filed."),
    ("Jul 02 2026", _PAPER_ONLY),
    ("Sep 24 2026", "Brief of respondent Todd Blanche in opposition filed."),
)


def test_fill_candidates_take_a_paper_only_docket_owing_a_kind(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, _PAPER_DOCKET)
    with corpus.connect(db) as conn:
        (candidate,) = fill_candidates(conn, today=_TODAY, max_cases=6)
    assert candidate.docket_number == "26-55"
    assert candidate.owed == ("petition", "brief-in-opposition")


@pytest.mark.parametrize(
    ("payload", "extra"),
    [
        # The Court lifted the rule: its own copies are the selector's to fetch.
        (
            _entries(
                *[(e["Date"], e["Text"]) for e in _PAPER_DOCKET["ProceedingsandOrder"]],
                ("Oct 01 2026", _LIFTED),
            ),
            {},
        ),
        # Not paper-only at all.
        (_entries(("Jul 01 2026", "Petition for a writ of certiorari filed.")), {}),
        # No cell can be placed on it.
        (_PAPER_DOCKET, {"salience_selected": False}),
        (_PAPER_DOCKET, {"date_cert_denied": _TODAY}),
        (_PAPER_DOCKET, {"disposition": "gvr"}),
    ],
)
def test_fill_candidates_pass_over_a_docket_no_fill_helps(
    tmp_path: Path, payload: dict[str, Any], extra: dict[str, Any]
) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, payload, **extra)
    with corpus.connect(db) as conn:
        assert fill_candidates(conn, today=_TODAY, max_cases=6) == []


def _candidate(db: Path) -> FillCandidate:
    with corpus.connect(db) as conn:
        (candidate,) = fill_candidates(conn, today=_TODAY, max_cases=6)
    return candidate


def test_an_applied_fill_stores_the_posted_brief_dated_by_its_docket_entry(
    tmp_path: Path,
) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, _PAPER_DOCKET)
    candidate = _candidate(db)
    upstream = _Upstream(
        {
            _PAGE_URL: httpx.Response(
                200,
                text=_listing(
                    _listing_row("26-55", "Petition Stage Response", day="2026-09-24"),
                    _listing_row("25-246", "Petition Stage Response", day="2026-09-24"),
                ),
            ),
            _PDF_URL: httpx.Response(200, content=_pdf("Brief for the respondents in opposition")),
        }
    )
    with corpus.connect(db) as conn, _client(upstream, []) as client:
        dry = fill_sg_briefs(conn, client, [candidate], apply=False, today=_TODAY, char_cap=10_000)
        assert dry.stored == {"brief-in-opposition": 1}
        assert corpus.documents_for_case(conn, "scotus/1") == []
    with corpus.connect(db) as conn, _client(upstream, []) as client:
        report = fill_sg_briefs(
            conn, client, [candidate], apply=True, today=_TODAY, char_cap=10_000
        )
        (case,) = report.cases
        assert case.status == "stored"
        assert case.listed_types == ["Petition Stage Response"]
        (document,) = corpus.documents_for_case(conn, "scotus/1")
    assert document.kind == "brief-in-opposition"
    assert document.url == _PDF_URL
    assert document.entry_date == "Sep 24 2026"
    assert "in opposition" in document.text


def test_a_docket_the_office_posts_nothing_for_stores_nothing(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, _PAPER_DOCKET)
    candidate = _candidate(db)
    upstream = _Upstream({_PAGE_URL: httpx.Response(200, text=_listing())})
    with corpus.connect(db) as conn, _client(upstream, []) as client:
        report = fill_sg_briefs(
            conn, client, [candidate], apply=True, today=_TODAY, char_cap=10_000
        )
        assert [case.status for case in report.cases] == ["nothing-posted"]
        assert corpus.documents_for_case(conn, "scotus/1") == []
    assert report.requests == 1


def test_a_failed_search_is_reported_and_the_pass_moves_on(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, _PAPER_DOCKET)
    candidate = _candidate(db)
    upstream = _Upstream({_PAGE_URL: httpx.Response(503)})
    with corpus.connect(db) as conn, _client(upstream, []) as client:
        report = fill_sg_briefs(
            conn, client, [candidate, candidate], apply=True, today=_TODAY, char_cap=10_000
        )
    assert [case.status for case in report.cases] == ["failed", "failed"]
