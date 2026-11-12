"""The trial stage's event opener (``pipeline/trial_opener.py``).

The rule is built to miss rather than misread, so most cases are realistic
docket texts that must open nothing, or be reported as declined, rather than
open an event on a guess.
"""

from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.ai_watchlist import AiWatchlist
from fedcourtsai.cli import app
from fedcourtsai.pipeline import trial_opener
from fedcourtsai.pipeline.trial_opener import (
    Basis,
    LocalRule,
    owned_by_lead,
    read_docket,
    survey,
    survey_dockets,
)
from fedcourtsai.pipeline.trial_resolver import MotionResolution, MotionRuling, TrialMoment

TODAY = date(2026, 11, 11)


def entry(number: int | None, description: str, day: str) -> dict[str, Any]:
    return {
        "id": 1000 + (number or 0),
        "entry_number": number,
        "date_filed": day,
        "description": description,
        "recap_documents": [],
    }


MOTION = entry(45, "MOTION to Dismiss filed by Developer, Inc.", "2026-01-10")
OPPOSITION = entry(
    52, "OPPOSITION/RESPONSE (re 45 MOTION to Dismiss ) filed byListed Author.", "2026-01-24"
)
REPLY = entry(58, "REPLY (re 45 MOTION to Dismiss ) filed byDeveloper, Inc.", "2026-01-31")


def one(*entries: dict[str, Any], **kw: Any) -> trial_opener.Opening:
    openings, _ = read_docket(list(entries), today=kw.pop("today", TODAY), **kw)
    assert len(openings) == 1, openings
    return openings[0]


# --- the motion ---------------------------------------------------------------


def test_a_briefed_motion_opens_on_its_reply() -> None:
    opening = one(MOTION, OPPOSITION, REPLY)
    assert opening.event.moment is TrialMoment.dismissal
    assert opening.event.entry_number == 45
    assert (opening.opposition and opening.opposition.entry_number) == 52
    assert (opening.reply and opening.reply.entry_number) == 58
    assert opening.opens_on == date(2026, 1, 31)
    assert opening.basis is Basis.reply
    assert opening.is_event
    assert opening.rule == "trial-opener-v1"


@pytest.mark.parametrize(
    ("opposition", "reply"),
    [
        (
            "RESPONSE in Opposition re 45 MOTION to Dismiss filed by Listed Author.",
            "REPLY to Response to Motion re 45 MOTION to Dismiss filed by Developer, Inc.",
        ),
        (
            "MEMORANDUM OF LAW in Opposition re: 45 MOTION to Dismiss. Document filed by Author.",
            "REPLY MEMORANDUM OF LAW in Support re: 45 MOTION to Dismiss. Document filed by Dev.",
        ),
        (
            "[SEALED] ANSWERING BRIEF in Opposition re 45 MOTION to Dismiss filed by Author.",
            "[SEALED] REPLY BRIEF re 45 MOTION to Dismiss filed by Developer, Inc.",
        ),
        (
            "Amended RESPONSE in Opposition re 45 MOTION to Dismiss filed by Listed Author.",
            "REPLY in Support (re 45 MOTION to Dismiss ) filed byDeveloper, Inc.",
        ),
    ],
)
def test_each_district_s_briefing_forms_are_read(opposition: str, reply: str) -> None:
    opening = one(MOTION, entry(52, opposition, "2026-01-24"), entry(58, reply, "2026-01-31"))
    assert opening.opens_on == date(2026, 1, 31)


@pytest.mark.parametrize(
    "text",
    [
        "Declaration of A. Witness in Support of 45 MOTION to Dismiss filed byDeveloper, Inc.",
        "MEMORANDUM in Support of 45 MOTION to Dismiss filed by Developer, Inc.",
        "NOTICE of Supplemental Authority re: 45 MOTION to Dismiss. Document filed by Dev.",
        "Request for Judicial Notice re 45 MOTION to Dismiss filed byDeveloper, Inc.",
        "REQUEST for Oral Argument by Developer, Inc. re 45 MOTION to Dismiss.",
        "Reply Declaration of A. Witness in Support of 58 Reply filed byDeveloper, Inc.",
        "OBJECTIONS to Reply Evidence Re 58 REPLY (re 45 MOTION to Dismiss) by Listed Author.",
        "MOTION for Leave to File Amicus Brief in Opposition re 45 MOTION to Dismiss by Group.",
        "RESPONSE in Opposition re 60 MOTION for Leave to File Brief re 45 MOTION to Dismiss",
        "REPLY to Response to re 60 MOTION for Leave to File Brief re 45 MOTION to Dismiss",
        "Defendant's Surreply re 45 MOTION to Dismiss filed byListed Author.",
        "RESPONSE in Support re 45 MOTION to Dismiss filed by Co-Defendant LLC.",
    ],
)
def test_filings_about_the_motion_are_not_its_briefing(text: str) -> None:
    opening = one(MOTION, entry(50, text, "2026-01-20"))
    assert opening.opposition is None
    assert opening.reply is None
    assert opening.opens_on is None
    assert not opening.is_event


def test_a_reply_before_any_opposition_is_not_the_reply() -> None:
    opening = one(MOTION, entry(50, REPLY["description"], "2026-01-12"), OPPOSITION)
    assert opening.reply is None
    assert opening.waiting_on == "the reply, or its deadline"


@pytest.mark.parametrize(
    ("opposition", "reply"),
    [
        (
            "OPPOSITION to Request for Judicial Notice re 45 MOTION to Dismiss",
            "REPLY to Opposition to Request for Judicial Notice re 45 MOTION to Dismiss",
        ),
        (
            "RESPONSE to Motion to Strike Expert Declaration re 45 MOTION to Dismiss",
            "REPLY in Support of Motion to Strike re 45 MOTION to Dismiss",
        ),
        (
            "OPPOSITION to Administrative Motion to File Under Seal parts of 45 MOTION to Dismiss",
            "REPLY re Administrative Motion to Consider Sealing re 45 MOTION to Dismiss",
        ),
        (
            "OPPOSITION to Motion for Leave to File Amicus Brief supporting 45 MOTION to Dismiss",
            "REPLY to Opposition to Motion to File Amicus Brief as to 45 MOTION to Dismiss",
        ),
        (
            "RESPONSE to Motion re 45 MOTION to Dismiss (Joinder) filed by Co-Defendant LLC.",
            "REPLY (re 46 MOTION to Dismiss ) filed byCo-Defendant LLC.",
        ),
        (
            "STATEMENT OF NON-OPPOSITION re 45 MOTION to Dismiss filed by Co-Defendant LLC.",
            "NOTICE of Non-Opposition to Motion to Expedite Hearing as to 45 MOTION to Dismiss",
        ),
    ],
)
def test_briefing_on_something_about_the_motion_opens_nothing(opposition: str, reply: str) -> None:
    opening = one(MOTION, entry(50, opposition, "2026-01-20"), entry(55, reply, "2026-01-27"))
    assert opening.opposition is None
    assert opening.reply is None
    assert opening.opens_on is None


def test_a_row_of_asterisks_is_read_in_linear_time() -> None:
    started = time.perf_counter()
    opening = one(MOTION, entry(50, "*" * 4000 + " re 45 MOTION to Dismiss", "2026-01-20"))
    assert opening.opposition is None
    assert time.perf_counter() - started < 1.0


# --- declined -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (
            "MOTION to Dismiss or, in the Alternative, to Transfer Venue filed by Dev.",
            "other relief",
        ),
        ("MOTION to Dismiss the Complaint and to Stay Discovery filed by Dev.", "other relief"),
        ("MOTION for Temporary Restraining Order filed by Listed Author.", "restraining order"),
    ],
)
def test_a_covered_motion_that_is_not_an_event_is_declined(text: str, reason: str) -> None:
    openings, declined = read_docket([entry(30, text, "2026-01-10")], today=TODAY)
    assert openings == []
    assert len(declined) == 1
    assert reason in declined[0].reason
    assert declined[0].cited.entry_number == 30


def test_an_unnumbered_motion_names_no_event() -> None:
    openings, declined = read_docket(
        [entry(None, MOTION["description"], "2026-01-10")], today=TODAY
    )
    assert openings == []
    assert "no number" in declined[0].reason


def test_a_motion_about_a_motion_is_neither_an_event_nor_declined() -> None:
    openings, declined = read_docket(
        [
            entry(
                30,
                "MOTION for Extension of Time to File Response as to 45 MOTION to Dismiss",
                "2026-01-12",
            )
        ],
        today=TODAY,
    )
    assert openings == []
    assert declined == []


def test_a_number_in_a_later_motion_s_title_is_not_a_correction() -> None:
    first = entry(45, "MOTION to Dismiss filed by Developer, Inc.", "2026-01-10")
    other = entry(
        60,
        "MOTION for Summary Judgment (Corrected to 45 pages) filed by Developer, Inc.",
        "2026-04-22",
    )
    openings, declined = read_docket([first, other], today=TODAY)
    assert [o.event.entry_number for o in openings] == [45, 60]
    assert declined == []


def test_a_motion_refiled_as_a_correction_is_one_event() -> None:
    first = entry(86, "MOTION for Summary Judgment filed by Developer, Inc.", "2026-04-20")
    second = entry(
        93,
        "MOTION for Summary Judgment (CORRECTION OF DOCKET # 86 ) filed by Developer, Inc.",
        "2026-04-22",
    )
    openings, declined = read_docket([first, second], today=TODAY)
    assert [o.event.entry_number for o in openings] == [93]
    assert [(d.cited.entry_number, d.reason) for d in declined] == [(86, "re-filed as entry 93")]


# --- preliminary injunctions -----------------------------------------------------

PI = entry(4, "MOTION for Preliminary Injunction filed by Listed Author.", "2026-03-01")


def test_an_injunction_motion_opens_on_the_opposition() -> None:
    opening = one(
        PI,
        entry(
            35,
            "OPPOSITION/RESPONSE (re 4 MOTION for Preliminary Injunction ) filed byDev.",
            "2026-03-15",
        ),
        entry(
            40,
            "REPLY (re 4 MOTION for Preliminary Injunction ) filed byListed Author.",
            "2026-03-22",
        ),
    )
    assert opening.event.moment is TrialMoment.preliminary_injunction
    assert opening.opens_on == date(2026, 3, 15)
    assert opening.basis is Basis.opposition


def test_a_combined_restraining_order_and_injunction_motion_is_an_injunction_event() -> None:
    combined = entry(
        6,
        "MOTION for Temporary Restraining Order, MOTION for Preliminary Injunction filed by Dev.",
        "2026-03-09",
    )
    opening = one(combined)
    assert opening.event.moment is TrialMoment.preliminary_injunction
    assert opening.opens_on is None


# --- deadlines ------------------------------------------------------------------

DUE = entry(
    45,
    "MOTION to Dismiss filed by Developer, Inc. Motion Hearing set for 3/5/2026 10:00 AM. "
    + "Responses due by 1/24/2026. Replies due by 1/31/2026.",
    "2026-01-10",
)


def test_a_stated_reply_deadline_opens_an_opposed_motion_the_day_after() -> None:
    opening = one(DUE, OPPOSITION)
    assert opening.opens_on == date(2026, 2, 1)
    assert opening.basis is Basis.docket_deadline


def test_a_deadline_that_has_not_passed_opens_nothing() -> None:
    opening = one(DUE, OPPOSITION, today=date(2026, 1, 31))
    assert opening.opens_on is None
    assert opening.waiting_on == "the reply, or its deadline"


def test_a_reset_deadline_replaces_the_motion_s_own() -> None:
    reset = entry(
        None,
        "Set/Reset Deadlines as to 45 MOTION to Dismiss. Responses due by 2/20/2026. "
        + "Replies due by 3/6/2026.",
        "2026-01-15",
    )
    opening = one(DUE, reset, OPPOSITION)
    assert opening.opens_on == date(2026, 3, 7)


def test_an_unopposed_motion_does_not_open_on_a_default_deadline() -> None:
    opening = one(DUE)
    assert opening.opens_on is None
    assert opening.waiting_on == "an opposition the rule can read"


@pytest.mark.parametrize(
    "moved",
    [
        "STIPULATION WITH PROPOSED ORDER re 45 MOTION to Dismiss to extend the briefing schedule",
        "ORDER granting 56 Motion for Extension of Time to File Response/Reply. "
        + "Replies due by 3/29/2026.",
        "ORDER re 56 Stipulation extending reply deadline as to 45 MOTION to Dismiss.",
        "CLERK'S NOTICE CONTINUING MOTION HEARING. Motion to Dismiss 45 reply deadline continued.",
    ],
)
def test_a_schedule_change_for_any_brief_distrusts_every_deadline(moved: str) -> None:
    opening = one(DUE, entry(47, moved, "2026-01-15"), OPPOSITION, local_rule=LocalRule(14, 7))
    assert opening.opens_on is None
    assert opening.waiting_on == "the reply, or its deadline"


def test_a_reset_restores_only_the_deadline_it_states() -> None:
    moved = entry(
        47, "STIPULATION to extend briefing schedule re 45 MOTION to Dismiss", "2026-01-15"
    )
    reset = entry(
        None,
        "Set/Reset Deadlines as to 45 MOTION to Dismiss. Responses due by 2/20/2026.",
        "2026-01-16",
    )
    late = entry(52, OPPOSITION["description"], "2026-02-20")
    assert one(DUE, moved, reset, late).opens_on is None


def test_a_reply_deadline_before_the_opposition_opens_nothing() -> None:
    late = entry(52, OPPOSITION["description"], "2026-02-20")
    assert one(DUE, late).opens_on is None


def test_an_entry_dated_after_the_reading_day_is_not_read() -> None:
    opening = one(MOTION, OPPOSITION, REPLY, today=date(2026, 1, 30))
    assert opening.reply is None
    assert opening.opens_on is None


def test_a_local_rule_counts_only_where_the_docket_states_no_deadline() -> None:
    assert one(MOTION, OPPOSITION).opens_on is None
    opening = one(MOTION, OPPOSITION, local_rule=LocalRule(14, 7))
    assert opening.opens_on == date(2026, 2, 1)
    assert opening.basis is Basis.local_rule
    assert one(MOTION, OPPOSITION, local_rule=LocalRule(14, None)).opens_on is None


def test_an_injunction_motion_opens_after_a_stated_response_deadline() -> None:
    due = entry(
        4,
        "MOTION for Preliminary Injunction filed by Listed Author. Responses due by 3/15/2026.",
        "2026-03-01",
    )
    opening = one(due)
    assert opening.opens_on == date(2026, 3, 16)
    assert opening.basis is Basis.docket_deadline


# --- the ruling ------------------------------------------------------------------


def test_a_ruling_after_the_opening_leaves_the_event_and_carries_its_resolution() -> None:
    order = entry(70, "ORDER by Judge A. Bench granting 45 Motion to Dismiss.", "2026-03-20")
    opening = one(MOTION, OPPOSITION, REPLY, order)
    assert opening.is_event
    assert isinstance(opening.resolution, MotionResolution)
    assert opening.resolution.ruling is MotionRuling.granted


def test_a_motion_ruled_on_before_its_briefing_closes_opens_nothing() -> None:
    order = entry(48, "ORDER denying as moot 45 Motion to Dismiss.", "2026-01-20")
    opening = one(MOTION, order, OPPOSITION, REPLY)
    assert opening.ruled_first
    assert not opening.is_event
    assert opening.waiting_on is None


# --- two dockets, the watchlist ---------------------------------------------------


def test_a_motion_on_the_lead_and_a_member_docket_is_the_lead_s() -> None:
    lead = [entry(300, "MOTION to Dismiss filed by Developer, Inc.", "2026-01-10")]
    member = [
        entry(88, "MOTION to Dismiss filed by Developer, Inc.", "2026-01-10"),
        entry(90, "MOTION to Dismiss filed by Other Developer LLC.", "2026-01-10"),
        entry(95, "MOTION to Dismiss filed by Developer, Inc.", "2026-02-10"),
    ]
    assert owned_by_lead(lead, member) == frozenset({88})


def _watchlist() -> AiWatchlist:
    return AiWatchlist.model_validate(
        {
            "categories": {"copyright": "Training on works."},
            "cases": [
                {
                    "name": "Listed v. Developer",
                    "court": "cand",
                    "docket_id": 100,
                    "docket_number": "3:23-cv-00100",
                    "category": "copyright",
                    "why": "Training.",
                    "developers": ["Developer"],
                    "added": "2026-10-30",
                    "related": [
                        {
                            "court": "ca9",
                            "docket_id": 101,
                            "docket_number": "25-101",
                            "relation": "appeal",
                        },
                        {
                            "court": "tnmd",
                            "docket_id": 102,
                            "docket_number": "3:23-cv-00102",
                            "relation": "transfer",
                        },
                        {
                            "court": "cand",
                            "docket_id": 103,
                            "docket_number": "3:24-cv-00103",
                            "relation": "member",
                        },
                        {
                            "court": "nysd",
                            "docket_id": 104,
                            "docket_number": "1:24-cv-00104",
                            "relation": "companion",
                        },
                    ],
                }
            ],
        }
    )


def test_the_survey_reads_district_dockets_with_motions_of_their_own() -> None:
    assert survey_dockets(_watchlist()) == [
        ("cand/100", None),
        ("cand/103", "cand/100"),
        ("nysd/104", None),
    ]


def test_the_survey_counts_events_and_carries_no_docket_text() -> None:
    order = entry(70, "ORDER granting 45 Motion to Dismiss.", "2026-03-20")
    stored = {
        "cand/100": [MOTION, OPPOSITION, REPLY, order],
        "cand/103": [entry(9, MOTION["description"], "2026-01-10")],
    }
    result = survey(_watchlist(), stored.get, today=TODAY)
    assert result.dockets_read == ["cand/100", "cand/103"]
    assert result.dockets_missing == ["nysd/104"]
    assert [(row.case_id, row.status, row.resolved) for row in result.motions] == [
        ("cand/100", "event", "granted"),
        ("cand/103", "lead-docket", None),
    ]
    counts = result.counts()
    assert (counts["events"], counts["events_resolved"], counts["lead_docket"]) == (1, 1, 1)
    assert "Developer" not in result.model_dump_json()


def test_trial_events_command_surveys_the_stored_dockets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config"
    config.mkdir()
    (config / "ai-watchlist.yaml").write_text(
        json.dumps(_watchlist().model_dump(mode="json")), encoding="utf-8"
    )
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_snapshot(
            conn, "cand/100", date(2026, 11, 1), {"docket_entries": [MOTION, OPPOSITION, REPLY]}
        )
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")

    result = CliRunner().invoke(app, ["trial-events", "--today", "2026-11-11"])

    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["counts"]["events"] == 1
    assert report["motions"][0]["opens_on"] == "2026-01-31"
    assert report["dockets_missing"] == ["cand/103", "nysd/104"]
    assert "trial-events (trial-opener-v1" in result.stderr
