"""The legacy HTML docket page, read into the docket JSON's own keys."""

from __future__ import annotations

import hashlib
from datetime import date

from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket
from fedcourtsai.pipeline.legacy_docket import (
    LEGACY_FORMAT,
    LEGACY_SOURCE_KEY,
    page_digest,
    parse_legacy_docket,
)

URL = "https://www.supremecourt.gov/docketfiles/16a752.htm"


def legacy_page(
    number: str = "16A752",
    *,
    docketed: str = "January 26, 2017",
    linked: str | None = "Linked with 16-7710",
    proceedings: tuple[tuple[str, str], ...] | None = None,
    respondent_counsel: bool = True,
) -> str:
    """A legacy docket page in the Court's layout, with invented parties and counsel."""
    rows = proceedings or (
        (
            "Jan 26 2017",
            f"Application ({number}) for a stay of execution, submitted to Justice Thomas. ",
        ),
        ("Jan 26 2017", f"Application ({number}) referred to the Court. "),
        ("Jan 26 2017", f"Application ({number}) denied by the Court.  "),
    )
    linked_row = f"<TR><TD ColSpan=2>{linked}</TD></TR>" if linked else ""
    respondent = (
        "<TR><TD><B>Attorneys for Respondent:</B></TD><TD></TD><TD></TD></TR>"
        + "<TR><TD>Rhea&nbsp;Quillfeather</TD><TD>\nAssistant Attorney General</TD>"
        + "<TD>(555) 010-0002</TD></TR>"
        + "<TR><TD>&nbsp;&nbsp;&nbsp;&nbsp;Counsel&nbsp;of&nbsp;Record</TD>"
        + "<TD>\nOffice of the Attorney General</TD><TD></TD></TR>"
        + "<TR><TD></TD><TD>Exampleton,&nbsp;ZZ&nbsp;&nbsp;00000</TD><TD></TD></TR>"
        + "<TR><TD COLSPAN=3>Party name: Warden of Example Prison</TD></TR>"
        if respondent_counsel
        else ""
    )
    proceedings_rows = "".join(
        f"<tr>\n<td valign=top>{day}</td>\n<td valign=top>{text}</td>\n</tr>\n"
        for day, text in rows
    )
    return (
        "<HTML><HEAD><TITLE>Docket for "
        + number
        + "</TITLE>"
        + "<script>var x = '<tr><td>not a row</td></tr>';</script></HEAD><Body>"
        + "<TABLE align=center BORDER=0 width='100%'>"
        + f"<TR><TD width='20%'>No. {number}</TD><TD align=left></TD></TR>"
        + "<TR>\n<TD valign='top'>Title:</TD>\n<TD>\n"
        + "<Table border=0><TR><TD>Ada Example, Applicant</TD></TR>\n"
        + "<TR><TD> v.</TD></TR>\n<TR><TD> Warden of Example Prison</TD></TR>\n</Table>\n"
        + "</TD></TR>"
        + f"<TR><TD>Docketed:</TD><TD>{docketed}</TD></TR>"
        + linked_row
        + "<TR><TD>Lower Ct:</TD><TD>United States Court of Appeals for the Fifth Circuit</TD></TR>"
        + "</TABLE>"
        + "<TABLE align=center BORDER=0 width='100%'>"
        + "<TR><TD width='20%'>&nbsp;&nbsp;Case Nos.:</TD><TD align=left>(17-00001)</TD></TR>"
        + "</TABLE><BR>"
        + "<table align=center border=0 width='100%'><TBody>\n<tr>\n"
        + "<td>~~~Date~~~&nbsp;</td><td>~~~~~~~Proceedings&nbsp; and &nbsp;Orders~~~~</td>\n"
        + "</tr>\n"
        + proceedings_rows
        + "</TBody></table></td></tr>\n<tr><td>\n</td></tr>\n</TBody></table><BR><HR><BR>"
        + "<TABLE BORDER=0 width='100%'>"
        + "<TR><TD>~~Name~~~~~~~~&nbsp;</TD><TD>~~~~Address~~~~&nbsp;</TD><TD>~~Phone~~~</TD></TR>"
        + "<TR><TD><B>Attorneys for Petitioner:</B></TD><TD></TD><TD></TD></TR>"
        + "<TR><TD>Ada&nbsp;Advocate</TD><TD>\nPO Box 1</TD><TD>(555) 010-0001</TD></TR>"
        + "<TR><TD>&nbsp;&nbsp;&nbsp;&nbsp;Counsel&nbsp;of&nbsp;Record</TD>"
        + "<TD>Exampleton,&nbsp;ZZ&nbsp;&nbsp;00000</TD><TD></TD></TR>"
        + "<TR><TD>Bo&nbsp;Second</TD><TD>\n2 Example Lane</TD><TD></TD></TR>"
        + "<TR><TD COLSPAN=3>Party name: Ada Example</TD></TR>"
        + respondent
        + "<TR><TD><B>Other:</B></TD><TD></TD><TD></TD></TR>"
        + "<TR><TD>Cy&nbsp;Amicus</TD><TD>\n3 Example Lane</TD><TD></TD></TR>"
        + "<TR><TD COLSPAN=3>Party name: Example Amicus Society</TD></TR>"
        + "</TABLE></BODY></HTML>"
    )


def test_the_page_reads_into_the_docket_jsons_keys() -> None:
    page = legacy_page()
    record = parse_legacy_docket(page, url=URL)
    assert record is not None
    assert record["CaseNumber"] == "16A752"
    assert record["PetitionerTitle"] == "Ada Example, Applicant"
    assert record["RespondentTitle"] == "Warden of Example Prison"
    assert record["DocketedDate"] == "January 26, 2017"
    assert record["Links"] == "Linked with 16-7710"
    assert record["LowerCourt"] == "United States Court of Appeals for the Fifth Circuit"
    assert record["LowerCourtCaseNumbers"] == "(17-00001)"
    assert [entry["Date"] for entry in record["ProceedingsandOrder"]] == ["Jan 26 2017"] * 3
    assert record["ProceedingsandOrder"][1]["Text"] == "Application (16A752) referred to the Court."
    assert record["AttorneyHeaderPetitioner"] == "Attorneys for Petitioner"
    assert record["AttorneyHeaderRespondent"] == "Attorneys for Respondent"
    # Each attorney keeps the counsel-of-record marker and the party name the
    # block closes on; the address and phone columns are not read.
    first, second = record["Petitioner"]
    assert first == {
        "Attorney": "Ada Advocate",
        "IsCounselofRecord": True,
        "PartyName": "Ada Example",
    }
    assert "PO Box" not in repr(record) and "555" not in repr(record)
    assert second["IsCounselofRecord"] is False
    assert second["PartyName"] == "Ada Example"
    (respondent,) = record["Respondent"]
    assert respondent["IsCounselofRecord"] is True
    assert respondent["PartyName"] == "Warden of Example Prison"
    # The page's bare `Other:` header opens its own side, as the JSON keys it.
    assert record["AttorneyHeaderOther"] == "Other"
    assert record["Other"] == [
        {"Attorney": "Cy Amicus", "IsCounselofRecord": False, "PartyName": "Example Amicus Society"}
    ]
    # Nothing the page does not carry is invented.
    for absent in ("bCapitalCase", "RelatedCaseNumber", "LowerCourtDecision", "sJsonTerm"):
        assert absent not in record
    assert record[LEGACY_SOURCE_KEY] == {
        "format": LEGACY_FORMAT,
        "url": URL,
        "sha256": page_digest(page),
    }


def test_a_legacy_record_maps_through_the_live_mapping() -> None:
    record = parse_legacy_docket(legacy_page(docketed="", linked=None), url=URL)
    assert record is not None
    row = from_live_record(map_live_docket(record, 0, form="application"))
    assert str(row.application_kind) == "substantive"
    assert row.referred_to_court is True
    assert str(row.disposition) == "denied"
    assert row.date_decided == date(2017, 1, 26)
    assert row.date_filed is None
    assert row.case_name == "Ada Example v. Warden of Example Prison"
    assert len(row.counsel) == 4


def test_a_page_without_a_number_or_proceedings_is_not_a_docket_page() -> None:
    assert parse_legacy_docket("<html><body><p>Page not found</p></body></html>", url=URL) is None
    page = legacy_page().replace("~~~Date~~~", "Date")
    assert parse_legacy_docket(page, url=URL) is None


def test_a_page_without_counsel_blocks_carries_none() -> None:
    page = legacy_page(respondent_counsel=False)
    cut = page[: page.index("<TABLE BORDER=0")] + "</BODY></HTML>"
    record = parse_legacy_docket(cut, url=URL)
    assert record is not None
    assert "Petitioner" not in record and "Respondent" not in record


def test_the_digest_leaves_out_the_per_request_beacon() -> None:
    page = legacy_page()
    reread = page.replace("var x = '", "var x = 'rid=9f3; ")
    assert page_digest(page) == page_digest(reread)
    assert page_digest(page) != page_digest(page.replace("16-7710", "16-7711"))
    assert (
        page_digest(page)
        == hashlib.sha256(
            page.replace("<script>var x = '<tr><td>not a row</td></tr>';</script>", "").encode()
        ).hexdigest()
    )
