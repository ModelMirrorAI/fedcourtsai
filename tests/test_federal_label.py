"""The federal-label cross-check: pending petitions a looser reading places federal."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.federal_label import (
    SG_LISTING_SUBJECT,
    FederalLabelReport,
    SgPetitionListing,
    federal_label_check,
    read_sg_petition_listing,
)
from fedcourtsai.pipeline.sg_briefs import MAX_LISTING_BYTES, OsgClient, cert_petitions_url
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


def _listing_row(number: str, brief_type: str = "Petition for Writ of Certiorari") -> str:
    def cell(header: str, body: str) -> str:
        return f'<td headers="view-field-{header}-table-column">{body}</td>'

    return (
        "<tr>"
        + cell("sc-term", "2026 Term")
        + cell("number", number)
        + cell("title", '<a href="/osg/brief/roe-v-doe">Roe v. Doe</a>')
        + cell("brief-type", brief_type)
        + cell("date", '<time datetime="2026-10-28T12:00:00Z">October 28, 2026</time>')
        + "</tr>"
    )


def _osg(response: httpx.Response, seen: list[str] | None = None) -> OsgClient:
    def upstream(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(str(request.url))
        return response

    return OsgClient(
        client=httpx.Client(transport=httpx.MockTransport(upstream)), sleep=lambda _: None
    )


def test_the_listing_is_read_in_one_request_and_keeps_only_the_offices_petitions() -> None:
    page = "<table>" + _listing_row("26-101, 26-102") + _listing_row("26-103") + "</table>"
    stray = _listing_row("26-900", "Petition Stage Response")
    seen: list[str] = []

    listing = read_sg_petition_listing(_osg(httpx.Response(200, text=page + stray), seen))

    assert seen == [cert_petitions_url()]
    assert listing.error is None
    assert listing.docket_numbers == {"26-101", "26-102", "26-103"}
    assert (listing.newest_filed, listing.oldest_filed) == (date(2026, 10, 28),) * 2


@pytest.mark.parametrize(
    ("response", "said"),
    [
        (httpx.Response(503), "HTTPStatusError"),
        (httpx.Response(404), "not found"),
        (httpx.Response(200, text="<html>26-101 maintenance</html>"), "no petition row"),
        (httpx.Response(302, headers={"location": "https://example.com/"}), "OffSectionFetch"),
        (httpx.Response(200, text="x" * (MAX_LISTING_BYTES + 1)), "OversizedBrief"),
        (
            httpx.Response(
                200,
                text="<tr>"
                + '<td headers="view-field-number-table-column">26-101</td>'
                + '<td headers="view-field-brief-type-table-column">Petition</td>'
                + '<td headers="view-field-title-table-column">'
                + '<a href="https://[x">maintenance</a></td></tr>',
            ),
            "could not be parsed (ValueError)",
        ),
    ],
)
def test_a_listing_that_cannot_be_read_says_how_and_nothing_of_the_page(
    response: httpx.Response, said: str
) -> None:
    listing = read_sg_petition_listing(_osg(response))

    assert listing.docket_numbers == frozenset()
    assert listing.error is not None and said in listing.error
    assert "maintenance" not in listing.error and "example.com" not in listing.error


def test_a_pending_petition_on_the_offices_listing_outside_the_band_alarms(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "26-101", conference=SOON)  # listed, read private
        _petition(conn, 2, "26-102", case_name="United States v. Roe")  # listed, federal
        _petition(conn, 3, "26-103", disposition=Disposition.denied)  # listed, resolved
        _petition(conn, 4, "26-104")  # not listed
        conn.execute("UPDATE cases SET salience_selected = 1 WHERE case_id = 'scotus/1'")
        conn.commit()
    listing = SgPetitionListing(
        frozenset({"26-101", "26-102", "26-103", "26-999"}), oldest_filed=date(2025, 9, 26)
    )

    with corpus.connect_readonly(db) as conn:
        report = federal_label_check(conn, today=TODAY, sg_listing=listing)

    check = report.sg_petition_list
    assert check is not None and check.read
    assert (check.listed, check.pending) == (4, 2)
    assert [(p.docket_number, p.selected) for p in check.not_federal] == [("26-101", True)]
    # Selected or not, the band is what prices the forecast, so it alarms.
    assert [a.split(":")[0] for a in report.alarms] == ["26-101"]
    assert report.flagged == []


def test_the_census_reads_no_listing_unless_handed_one(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "26-101")

    assert _check(db).sg_petition_list is None


def test_an_unread_listing_is_an_alarm_of_its_own(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "26-101")
    unread = SgPetitionListing(frozenset(), error="the request failed (ConnectTimeout)")

    with corpus.connect_readonly(db) as conn:
        report = federal_label_check(conn, today=TODAY, sg_listing=unread)

    assert report.sg_petition_list is not None and not report.sg_petition_list.read
    assert [a.split(":")[0] for a in report.alarms] == [SG_LISTING_SUBJECT]


def test_the_cli_fetches_the_listing_only_under_its_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _petition(conn, 1, "26-101")
    fetches: list[int] = []

    def listing() -> SgPetitionListing:
        fetches.append(1)
        return SgPetitionListing(frozenset({"26-101"}))

    monkeypatch.setattr(cli, "_read_sg_petition_listing", listing)

    quiet = CliRunner().invoke(app, ["federal-label-check"])
    assert quiet.exit_code == 0, quiet.output
    assert fetches == []

    alarmed = CliRunner().invoke(app, ["federal-label-check", "--sg-list"])
    assert alarmed.exit_code == 3, alarmed.output
    assert fetches == [1]
    payload = json.loads(alarmed.stdout.strip().splitlines()[-1])
    assert [p["docket_number"] for p in payload["sg_petition_list"]["not_federal"]] == ["26-101"]


def test_a_capital_marking_on_the_stored_number_does_not_hide_a_listed_petition(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _petition(conn, 1, "26-101 *** CAPITAL CASE ***")

    with corpus.connect_readonly(db) as conn:
        report = federal_label_check(
            conn, today=TODAY, sg_listing=SgPetitionListing(frozenset({"26-101"}))
        )

    assert report.sg_petition_list is not None
    assert [a.split(",")[0] for a in report.sg_petition_list.alarms] == [
        "26-101 *** CAPITAL CASE ***: on the Solicitor General's listing of its own cert petitions"
    ]
