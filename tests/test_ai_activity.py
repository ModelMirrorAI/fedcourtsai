from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.ai_activity import (
    EntryKind,
    activity_entries,
    activity_path,
    classify,
    entry_url,
    new_significant,
    record_activity,
)
from fedcourtsai.ai_cases_update import (
    ai_cases_subject,
    build_ai_cases_update,
    render_ai_cases_update,
)
from fedcourtsai.cli import app
from fedcourtsai.schemas import AiCaseActivity
from fedcourtsai.serialize import read_model
from fedcourtsai.validate import validate_ledger

TODAY = date(2026, 10, 30)
DOCKET: dict[str, Any] = {
    "id": 72379655,
    "court_id": "cand",
    "docket_number": "3:26-cv-01996",
    "absolute_url": "/docket/72379655/anthropic-pbc-v-us-department-of-war/",
}


def _entry(
    entry_id: int, description: str, short: str = "", *, filed: str = "2026-10-26", number: int = 1
) -> dict[str, Any]:
    documents = [{"description": short, "attachment_number": None}] if short else []
    return {
        "id": entry_id,
        "entry_number": number,
        "date_filed": filed,
        "description": description,
        "recap_documents": documents,
    }


@pytest.mark.parametrize(
    ("description", "short", "kind"),
    [
        (
            "NOTICE OF APPEAL to the 9th Circuit Court of Appeals filed by Paul S. Atkins. "
            + "Appeal of Order on Motion for Summary Judgment, Judgment 252",
            "Notice of Appeal to the Ninth Circuit",
            EntryKind.appeal,
        ),
        (
            "JUDGMENT. Signed by Judge Rita F. Lin on August 27, 2026.",
            "Judgment",
            EntryKind.judgment,
        ),
        (
            "ORDER ON 166 215 CROSS MOTIONS FOR SUMMARY JUDGMENT; GRANTING 169 MOTION TO "
            + "SUPPLEMENT THE ADMINISTRATIVE RECORD.",
            "Order on Motion for Summary Judgment",
            EntryKind.ruling,
        ),
        ("ORDER OF FINAL RELIEF. Signed by Judge Rita F. Lin.", "Order", EntryKind.judgment),
        (
            "OPINION AND ORDER re: 112 MOTION to Dismiss. The motion is GRANTED in part.",
            "",
            EntryKind.opinion,
        ),
        ("MEMORANDUM OPINION. Signed by Judge Stephanos Bibas.", "", EntryKind.opinion),
        ("COMPLAINT against OpenAI, Inc. (Filing fee $405.)", "Complaint", EntryKind.complaint),
        ("FIRST AMENDED COMPLAINT against Meta Platforms, Inc.", "", EntryKind.complaint),
        (
            "CONSOLIDATED CLASS ACTION COMPLAINT against all defendants.",
            "",
            EntryKind.complaint,
        ),
        ("MOTION to Dismiss filed by Anthropic PBC.", "Motion to Dismiss", EntryKind.motion),
        (
            "MOTION for Preliminary Injunction filed by Anthropic PBC.",
            "",
            EntryKind.motion,
        ),
        (
            "MOTION to Dismiss filed by OpenAI, Inc. (Attachments: # 1 Proposed Order, "
            + "# 2 Certificate of Service)",
            "",
            EntryKind.motion,
        ),
        (
            "OPINION AND ORDER re: 75 MOTION to Dismiss. An initial pretrial conference is "
            + "scheduled for 11/20/2026. Discovery is stayed.",
            "",
            EntryKind.opinion,
        ),
        (
            "MEMORANDUM OPINION AND ORDER re 30 motion to dismiss; consent to magistrate judge",
            "",
            EntryKind.opinion,
        ),
        ("ORDER GRANTING Dkt. No. 45 MOTION TO DISMISS.", "", EntryKind.ruling),
        ("ORDER granting Motion to Stay pending appeal.", "", EntryKind.ruling),
        ("NOTICE OF INTERLOCUTORY APPEAL by OpenAI, Inc.", "", EntryKind.appeal),
        (
            "ORDER GRANTING PRELIMINARY APPROVAL OF CLASS ACTION SETTLEMENT.",
            "",
            EntryKind.resolution,
        ),
        (
            "STIPULATION OF VOLUNTARY DISMISSAL with prejudice by all parties.",
            "",
            EntryKind.resolution,
        ),
        ("NOTICE of Settlement by Getty Images.", "", EntryKind.resolution),
    ],
)
def test_significant_entries_get_their_kind(description: str, short: str, kind: EntryKind) -> None:
    assert classify(_entry(1, description, short)) is kind


@pytest.mark.parametrize(
    ("description", "short"),
    [
        ("TRANSCRIPT ORDER for proceedings held on 7/30/2026 before Judge Rita F. Lin", ""),
        (
            "CLERK'S NOTICE RE: ZOOM ACCESS RE: MOTION HEARING RE: 166 MOTION for Summary Judgment",
            "",
        ),
        ("Proposed Order re 166 MOTION for Summary Judgment by Anthropic PBC.", ""),
        ("ORDER. By July 24, 2026, Anthropic shall file a proposed order.", "Order"),
        ("MOTION for Leave to Appear Pro Hac Vice by Jane Doe.", ""),
        ("ORDER granting 40 Motion for Extension of Time to File Answer.", ""),
        ("LETTER MOTION to Compel discovery addressed to Judge Stein.", ""),
        ("Minute Entry for proceedings held before Judge Rita F. Lin: Motion Hearing", ""),
        ("NOTICE of Appearance by John Roe on behalf of OpenAI, Inc.", ""),
        ("ORDER granting motion to file under seal.", ""),
        ("MEMORANDUM OF LAW in Support re: 87 MOTION to Dismiss the Amended Complaint.", ""),
        ("MEMORANDUM in Opposition re 45 MOTION to Dismiss filed by Authors Guild.", ""),
        ("NOTICE of Supplemental Authority re: Bartz v. Anthropic opinion", ""),
        ("STATEMENT OF RECENT DECISION re opinion in Kadrey v. Meta", ""),
        ("ORDER granting Motion for Leave to File Opinion of Expert.", ""),
        ("", ""),
    ],
)
def test_routine_entries_are_dropped(description: str, short: str) -> None:
    assert classify(_entry(1, description, short)) is None


def test_the_short_description_alone_can_carry_the_kind() -> None:
    assert classify(_entry(1, "", "Order on Motion to Dismiss")) is EntryKind.ruling


def test_new_significant_keeps_recent_unseen_entries_oldest_first() -> None:
    stored = [_entry(1, "COMPLAINT against X.")]
    fresh = [
        _entry(4, "JUDGMENT.", filed="2026-10-29"),
        _entry(3, "MOTION to Dismiss filed by X.", filed="2026-10-20"),
        _entry(2, "NOTICE of Appearance by Y.", filed="2026-10-28"),
        _entry(1, "COMPLAINT against X."),
        _entry(5, "MEMORANDUM OPINION.", filed="2026-09-01"),  # old history surfacing late
        _entry(6, "JUDGMENT.", filed=""),
    ]
    found = new_significant(stored, fresh, today=TODAY)
    assert [(entry["id"], kind) for entry, kind in found] == [
        (3, EntryKind.motion),
        (4, EntryKind.judgment),
    ]


def test_a_malformed_entry_costs_only_itself() -> None:
    added = [
        _entry(21, "JUDGMENT.", filed="2026-10-27", number=252),
        {**_entry(22, "MOTION to Dismiss filed by X.", filed="2026-10-28"), "entry_number": "x"},
    ]
    entries = activity_entries("Case", "government", DOCKET, added, today=TODAY)
    assert [e.entry_id for e in entries] == [21]


def test_entry_url_prefers_the_document_page_then_the_docket_entry() -> None:
    with_document = _entry(1, "JUDGMENT.", number=252)
    with_document["recap_documents"] = [{"absolute_url": "/docket/72379655/252/x/"}]
    assert (
        entry_url(with_document, DOCKET) == "https://www.courtlistener.com/docket/72379655/252/x/"
    )
    assert entry_url(_entry(2, "JUDGMENT.", number=252), DOCKET) == (
        "https://www.courtlistener.com/docket/72379655/anthropic-pbc-v-us-department-of-war/#entry-252"
    )


def _recorded(tmp_path: Path) -> Path:
    added = [
        _entry(11, "JUDGMENT.", "Judgment", filed="2026-10-27", number=252),
        _entry(12, "NOTICE of Appearance by Y.", filed="2026-10-28", number=253),
    ]
    entries = activity_entries(
        "Anthropic v. Department of War", "government", DOCKET, added, today=TODAY
    )
    path = record_activity(tmp_path, TODAY, entries)
    assert path == activity_path(tmp_path, TODAY)
    return path


def test_a_day_records_identifiers_kinds_and_links_and_no_docket_text(tmp_path: Path) -> None:
    path = _recorded(tmp_path)
    record = read_model(path, AiCaseActivity)
    assert [(e.entry_id, e.kind, e.court, e.docket_number) for e in record.entries] == [
        (11, "judgment", "cand", "3:26-cv-01996")
    ]
    assert "JUDGMENT." not in path.read_text()
    assert validate_ledger(tmp_path).ok


def test_a_second_refresh_the_same_day_adds_to_the_record(tmp_path: Path) -> None:
    _recorded(tmp_path)
    later = activity_entries(
        "Anthropic v. Department of War",
        "government",
        DOCKET,
        [_entry(13, "NOTICE OF APPEAL to the 9th Circuit.", filed="2026-10-29", number=254)],
        today=TODAY,
    )
    path = record_activity(tmp_path, TODAY, later)
    assert path is not None
    assert [e.entry_id for e in read_model(path, AiCaseActivity).entries] == [11, 13]
    assert record_activity(tmp_path, date(2026, 10, 31), []) is None


def test_a_misnamed_record_fails_validation(tmp_path: Path) -> None:
    path = _recorded(tmp_path)
    path.rename(path.with_name("2026-10-29.json"))
    report = validate_ledger(tmp_path)
    assert not report.ok and "records day 2026-10-30" in report.problems[0]


def test_the_update_groups_a_span_by_case_and_quotes_no_docket_text(tmp_path: Path) -> None:
    _recorded(tmp_path)
    update = build_ai_cases_update(tmp_path, date(2026, 10, 26), date(2026, 11, 1))
    assert update.items == 1
    assert (
        ai_cases_subject(update)
        == "AI cases in federal court: October 26 \N{EN DASH} November 1, 2026"
    )
    text = render_ai_cases_update(update)
    assert "## Anthropic v. Department of War" in text
    assert "*Government*" in text
    assert "- Oct 27: Judgment (cand 3:26-cv-01996, entry 252)." in text
    assert "CourtListener" in text.split("---")[-1]
    empty = build_ai_cases_update(tmp_path, date(2026, 11, 2), date(2026, 11, 8))
    assert empty.empty
    one_day = build_ai_cases_update(tmp_path, TODAY, TODAY)
    assert ai_cases_subject(one_day) == "AI cases in federal court: October 30, 2026"


def test_post_dry_run_prints_the_draft_and_an_empty_span_exits_three(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _recorded(tmp_path)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path))
    runner = CliRunner()

    posted = runner.invoke(
        app, ["post-ai-cases-update", "--tag", "ai-cases", "--week", "2026-W44", "--dry-run"]
    )
    assert posted.exit_code == 0, posted.output
    assert posted.output.startswith("Subject: AI cases in federal court: October 26")
    assert "Tag: ai-cases" in posted.output

    quiet = runner.invoke(
        app, ["post-ai-cases-update", "--tag", "ai-cases", "--day", "2026-11-03", "--dry-run"]
    )
    assert quiet.exit_code == 3
    both = runner.invoke(
        app,
        ["post-ai-cases-update", "--tag", "ai-cases", "--day", "2026-11-03", "--week", "2026-W44"],
    )
    assert both.exit_code == 2
