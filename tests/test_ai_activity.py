from datetime import date
from pathlib import Path
from typing import Any, get_args

import pytest
from typer.testing import CliRunner

from fedcourtsai.ai_activity import (
    ACTIVITY_RULE,
    AVAILABILITY_RULE,
    PRINCIPAL_MOTIONS,
    AvailableKind,
    EntryKind,
    activity_entries,
    activity_path,
    available_entries,
    became_available,
    classify,
    classify_available,
    entry_url,
    new_significant,
    principal_motion,
    record_activity,
)
from fedcourtsai.ai_cases_update import (
    AVAILABLE_PER_CASE,
    COURT_NAMES,
    MOTION_LABELS,
    SECTIONS,
    ai_cases_subject,
    build_ai_cases_update,
    render_ai_cases_update,
)
from fedcourtsai.ai_rulings import owed_rulings
from fedcourtsai.ai_watchlist import AI_WATCHLIST_FILENAME, AiWatchlist, load_ai_watchlist
from fedcourtsai.cli import app
from fedcourtsai.schemas import (
    AiActivityKind,
    AiActivityMotion,
    AiCaseActivity,
    AiCaseActivityEntry,
)
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
    assert "## Rulings" in text
    assert "### Anthropic v. Department of War" in text
    assert "*Government*" in text
    assert "**This update:** 1 ruling" in text
    assert "- Oct 27: Judgment (N.D. Cal. 3:26-cv-01996, entry 252)." in text
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


@pytest.mark.parametrize(
    ("description", "motion"),
    [
        ("MOTION to Dismiss filed by Anthropic PBC.", "dismiss"),
        ("ORDER GRANTING Dkt. No. 45 MOTION TO DISMISS.", "dismiss"),
        (
            "ORDER ON 166 215 CROSS MOTIONS FOR SUMMARY JUDGMENT; GRANTING 169 MOTION TO "
            + "SUPPLEMENT THE ADMINISTRATIVE RECORD.",
            "summary-judgment",
        ),
        ("MOTION for Partial Summary Judgment filed by Meta.", "partial-summary-judgment"),
        ("MOTION for Preliminary Injunction filed by Anthropic PBC.", "preliminary-injunction"),
        ("ORDER granting Motion to Stay pending appeal.", "stay-pending-appeal"),
        ("ORDER denying Motion for Class Certification.", "class-certification"),
        ("OPINION AND ORDER re: 112 MOTION to Dismiss. The motion is GRANTED in part.", "dismiss"),
        ("MEMORANDUM OPINION. Signed by Judge Stephanos Bibas.", None),
        ("JUDGMENT.", None),
        (
            "ORDER certifying question for interlocutory appeal; GRANTING motion to dismiss.",
            "dismiss",
        ),
        ("ORDER granting the Certified motion to dismiss.", "dismiss"),
        ("MOTION for Leave to File Motion to Dismiss filed by OpenAI.", None),
        ("COMPLAINT against OpenAI, Inc.", None),
        ("NOTICE OF APPEAL to the 9th Circuit.", None),
    ],
)
def test_the_record_names_the_principal_motion(description: str, motion: str | None) -> None:
    assert principal_motion(_entry(1, description)) == motion


def test_every_motion_label_is_in_the_schema_and_in_the_readers_words() -> None:
    labels = {label for label, _ in PRINCIPAL_MOTIONS}
    assert labels == set(get_args(AiActivityMotion)) == set(MOTION_LABELS)


def test_every_watchlist_court_has_a_readers_name() -> None:
    watchlist = load_ai_watchlist(Path("config") / AI_WATCHLIST_FILENAME)
    courts = {court for case in watchlist.cases for court, _ in case.dockets()}
    courts |= {r.court for case in watchlist.cases for r in case.related}
    assert courts <= set(COURT_NAMES)


def _activity(
    case: str, category: str, entry_id: int, kind: str, filed: date, motion: str | None = None
) -> AiCaseActivityEntry:
    return AiCaseActivityEntry.model_validate(
        {
            "case": case,
            "category": category,
            "court": "nysd",
            "docket_id": 1,
            "docket_number": "1:25-cv-01234",
            "entry_id": entry_id,
            "entry_number": entry_id,
            "date_filed": filed,
            "kind": kind,
            "motion": motion,
            "url": f"https://www.courtlistener.com/docket/1/#entry-{entry_id}",
        }
    )


def test_the_update_orders_cases_by_their_weightiest_item_and_introduces_them(
    tmp_path: Path,
) -> None:
    filings = [
        _activity("Filer v. Lab", "copyright", 1, "complaint", date(2026, 11, 2)),
        _activity("Appellant v. Lab", "employment", 2, "appeal", date(2026, 11, 3)),
        _activity("Authors v. Lab", "copyright", 3, "motion", date(2026, 11, 3), "dismiss"),
        _activity("Authors v. Lab", "copyright", 4, "ruling", date(2026, 11, 6), "dismiss"),
    ]
    record_activity(tmp_path, date(2026, 11, 7), filings)
    watchlist = AiWatchlist.model_validate(
        {
            "categories": {"copyright": "Copying.", "employment": "Hiring."},
            "cases": [
                {
                    "name": "Authors v. Lab",
                    "court": "nysd",
                    "docket_id": 1,
                    "docket_number": "1:25-cv-01234",
                    "category": "copyright",
                    "why": "Training a model on the authors' books.",
                    "developers": ["Lab"],
                    "added": "2026-10-30",
                }
            ],
        }
    )
    update = build_ai_cases_update(tmp_path, date(2026, 11, 2), date(2026, 11, 8), watchlist)
    text = render_ai_cases_update(update, title=False)
    assert "in the 1 federal AI case FedCourtsAI follows" in text
    assert "**This update:** 1 ruling \N{MIDDLE DOT} 1 appeal \N{MIDDLE DOT} 2 new filings" in text
    order = [
        text.index(h)
        for h in (
            "## Rulings",
            "### Authors v. Lab",
            "## Appeals and settlements",
            "### Appellant v. Lab",
            "## New filings",
            "### Filer v. Lab",
        )
    ]
    assert order == sorted(order)
    # A case keeps all its items under its weightiest section.
    authors = text.split("### Authors v. Lab")[1].split("##")[0]
    assert "Motion to dismiss filed (S.D.N.Y. 1:25-cv-01234, entry 3)" in authors
    assert "Ruling on a motion to dismiss (S.D.N.Y. 1:25-cv-01234, entry 4)" in authors
    assert "*Copyright · S.D.N.Y. · Training a model on the authors' books.*" in authors
    assert "[fedcourts.ai](https://fedcourts.ai/)" in text.split("---")[-1]


def test_every_kind_has_a_section() -> None:
    assert set().union(*(kinds for _, kinds in SECTIONS)) == set(get_args(AiActivityKind))


def _docs(*docs: tuple[int, int | None, bool, str]) -> list[dict[str, Any]]:
    return [
        {"id": i, "attachment_number": a, "is_available": readable, "description": d}
        for i, a, readable, d in docs
    ]


def _with_docs(entry_id: int, description: str, docs: list[dict[str, Any]]) -> dict[str, Any]:
    entry = _entry(entry_id, description, filed="2026-10-10", number=entry_id)
    entry["recap_documents"] = docs
    return entry


def test_became_available_lists_held_entries_that_gained_readable_documents() -> None:
    before = _with_docs(1, "ORDER GRANTING MOTION TO DISMISS.", _docs((10, None, False, "")))
    after = _with_docs(1, "ORDER GRANTING MOTION TO DISMISS.", _docs((10, None, True, "")))
    new = _with_docs(2, "COMPLAINT against OpenAI.", _docs((20, None, True, "")))
    gained = became_available([before], [after, new])
    assert [(e["id"], ids) for e, ids in gained] == [(1, frozenset({10}))]
    # Readable already: nothing gained.
    assert became_available([after], [after]) == []


@pytest.mark.parametrize(
    ("description", "docs", "gained", "expected"),
    [
        (
            "ORDER GRANTING Dkt. No. 45 MOTION TO DISMISS.",
            _docs((10, None, True, "")),
            {10},
            (AvailableKind.ruling, 1, "dismiss"),
        ),
        (
            "COMPLAINT against OpenAI.",
            _docs((10, None, True, "")),
            {10},
            (AvailableKind.complaint, 1, None),
        ),
        (
            "MOTION for Summary Judgment filed by Meta. "
            + "(Attachments: # 1 Exhibit A, # 2 Exhibit B)",
            _docs((10, None, True, ""), (11, 1, True, ""), (12, 2, True, "")),
            {11, 12},
            (AvailableKind.exhibits, 2, "summary-judgment"),
        ),
        (
            "OPPOSITION/RESPONSE (re 35 MOTION for Class Certification) filed by Workday.",
            _docs((10, None, False, ""), (11, 1, True, "")),
            {11},
            (AvailableKind.exhibits, 1, "class-certification"),
        ),
        (
            "EXHIBITS re 806 Joint Administrative Motion to File Under Seal re Parties' "
            + "Summary Judgment Briefing",
            _docs((10, None, False, ""), (11, 1, True, "")),
            {11},
            (AvailableKind.exhibits, 1, "summary-judgment"),
        ),
        (
            "REDACTED VERSION of Opposition to Motion to Dismiss filed by Anthropic.",
            _docs((10, None, True, ""), (11, 1, True, "")),
            {10, 11},
            (AvailableKind.unsealed, 2, "dismiss"),
        ),
        (
            "TRANSCRIPT of Proceedings held on 10/1/2026 before Judge X.",
            _docs((10, None, True, "")),
            {10},
            (AvailableKind.transcript, 1, None),
        ),
        (
            "TRANSCRIPT of Status Conference held on 10/1/2026.",
            _docs((10, None, True, "")),
            {10},
            None,
        ),
        (
            "Statement - Issue Statement Regarding Discovery by Anthropic.",
            _docs((10, None, True, "")),
            {10},
            None,
        ),
        (
            "MOTION to Compel Discovery filed by Amazon. (Attachments: # 1 Exhibit)",
            _docs((10, None, True, ""), (11, 1, True, "")),
            {11},
            None,
        ),
        ("NOTICE of Appearance by Y.", _docs((10, None, True, "")), {10}, None),
    ],
)
def test_the_availability_rule_keeps_significant_documents(
    description: str,
    docs: list[dict[str, Any]],
    gained: set[int],
    expected: tuple[AvailableKind, int, str | None] | None,
) -> None:
    assert classify_available(_with_docs(1, description, docs), frozenset(gained)) == expected


def test_available_entries_skip_old_history_and_render_last_by_case(tmp_path: Path) -> None:
    ruling = _with_docs(
        30, "ORDER GRANTING Dkt. No. 45 MOTION TO DISMISS.", _docs((300, None, True, ""))
    )
    old = _entry(31, "COMPLAINT against OpenAI.", filed="2026-07-01", number=1)
    old["recap_documents"] = _docs((310, None, True, ""))
    exhibits = [
        _with_docs(
            40 + i,
            "MOTION for Summary Judgment. (Attachments: # 1 Exhibit A)",
            _docs((400 + i, 1, True, "")),
        )
        for i in range(6)
    ]
    gained = [(ruling, frozenset({300})), (old, frozenset({310}))]
    gained += [(e, frozenset({400 + i})) for i, e in enumerate(exhibits)]
    found = available_entries(
        "Anthropic v. Department of War", "government", DOCKET, gained, today=TODAY
    )
    assert [e.entry_id for e in found] == [30, 40, 41, 42, 43, 44, 45]
    path = record_activity(tmp_path, TODAY, [], found)
    assert path is not None
    record = read_model(path, AiCaseActivity)
    assert record.entries == [] and record.available_rule == AVAILABILITY_RULE
    assert validate_ledger(tmp_path).ok
    update = build_ai_cases_update(tmp_path, date(2026, 10, 26), date(2026, 11, 1))
    text = render_ai_cases_update(update, title=False)
    assert "**This update:** 7 newly readable" in text
    assert "## Newly available" in text
    assert "- Ruling on a motion to dismiss of Oct 10 is now readable (N.D. Cal." in text
    assert "1 exhibit filed Oct 10 on a motion for summary judgment is now readable" in text
    assert text.count("exhibit filed") == AVAILABLE_PER_CASE - 1
    assert "- And 2 more in this case. [View the docket]" in text
    assert "MOTION for Summary" not in text


def test_a_ruling_that_became_readable_is_owed_a_summary(tmp_path: Path) -> None:
    ruling = _with_docs(
        30, "ORDER GRANTING Dkt. No. 45 MOTION TO DISMISS.", _docs((300, None, True, ""))
    )
    found = available_entries(
        "Anthropic v. Department of War",
        "government",
        DOCKET,
        [(ruling, frozenset({300}))],
        today=TODAY,
    )
    record_activity(tmp_path, TODAY, [], found)
    assert [e.entry_id for e in owed_rulings(tmp_path, TODAY)] == [30]


def test_a_record_needs_an_entry_and_the_availability_label_with_its_list() -> None:
    with pytest.raises(ValueError, match="at least one entry"):
        AiCaseActivity(day=TODAY, rule=ACTIVITY_RULE)
    entry = _activity("A v. B", "copyright", 1, "complaint", TODAY)
    with pytest.raises(ValueError, match="available_rule"):
        AiCaseActivity(day=TODAY, rule=ACTIVITY_RULE, entries=[entry], available_rule="x")
