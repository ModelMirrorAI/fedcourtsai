"""The trial stage's deterministic resolver (``pipeline/trial_resolver.py``)."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from fedcourtsai.pipeline.trial_resolver import (
    Citation,
    JudgmentOutcome,
    JudgmentResolution,
    Leave,
    MotionEvent,
    MotionResolution,
    MotionRuling,
    Source,
    TrialMoment,
    Unresolved,
    decretal,
    find_closure,
    motion_moment,
    read_judgment,
    read_ruling,
    resolve_judgment,
    resolve_motion,
)


def entry(
    number: int | None, description: str, *, day: str = "2026-03-01", **extra: Any
) -> dict[str, Any]:
    entry_id = 1000 + (number if number is not None else 999)
    return {
        "id": extra.pop("entry_id", entry_id),
        "entry_number": number,
        "date_filed": day,
        "description": description,
        "recap_documents": extra.pop("recap_documents", []),
    }


MTD = MotionEvent(TrialMoment.dismissal, 45)
MOTION = entry(
    45, "MOTION to Dismiss for Failure to State a Claim filed by OpenAI, Inc.", day="2026-01-10"
)


# --- the motion kind ---------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "moment"),
    [
        ("MOTION to Dismiss for Lack of Jurisdiction", TrialMoment.dismissal),
        ("MOTION to Certify Class filed by Plaintiffs", TrialMoment.class_certification),
        ("MOTION for Class Certification", TrialMoment.class_certification),
        ("MOTION for Partial Summary Judgment", TrialMoment.summary_judgment),
        ("Cross MOTION for Summary Judgment", TrialMoment.summary_judgment),
        ("MOTION to Compel Discovery", None),
        ("ORDER setting conference", None),
    ],
)
def test_motion_moment(text: str, moment: TrialMoment | None) -> None:
    assert motion_moment(text) is moment


def test_motion_event_refuses_the_judgment_moment() -> None:
    with pytest.raises(ValueError, match="not a motion moment"):
        MotionEvent(TrialMoment.judgment, 1)


# --- reading a ruling --------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "ruling", "leave"),
    [
        ("ORDER granting 45 Motion to Dismiss", MotionRuling.granted, Leave.unstated),
        ("ORDER denying 45 Motion to Dismiss", MotionRuling.denied, Leave.unstated),
        (
            "ORDER granting in part and denying in part 45 Motion to Dismiss",
            MotionRuling.granted_in_part,
            Leave.unstated,
        ),
        (
            "The motion is GRANTED as to Count I and DENIED as to Count II",
            MotionRuling.granted_in_part,
            Leave.unstated,
        ),
        (
            "ORDER granting 45 Motion to Dismiss with leave to amend",
            MotionRuling.granted,
            Leave.with_leave,
        ),
        (
            "The motion to dismiss is GRANTED. Leave to amend is DENIED.",
            MotionRuling.granted,
            Leave.without_leave,
        ),
        (
            "The complaint is dismissed with prejudice and the motion is granted",
            MotionRuling.granted,
            Leave.without_leave,
        ),
        (
            "Motion granted; plaintiffs may file a second amended complaint within 21 days",
            MotionRuling.granted,
            Leave.with_leave,
        ),
        ("ORDER denying as moot 45 Motion to Dismiss", MotionRuling.mooted, Leave.unstated),
        ("ORDER finding as moot 45 Motion to Dismiss", MotionRuling.mooted, Leave.unstated),
        ("The motion is deemed withdrawn", MotionRuling.withdrawn, Leave.unstated),
        ("ORDER setting hearing on 45 Motion to Dismiss", None, Leave.unstated),
    ],
)
def test_read_ruling(text: str, ruling: MotionRuling | None, leave: Leave) -> None:
    assert read_ruling(text) == type(read_ruling(text))(ruling, leave)


def test_decretal_starts_at_the_first_ordering_paragraph() -> None:
    order = (
        "Defendants move to dismiss. The motion is granted in the discussion's view. "
        "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is DENIED. "
        "IT IS FURTHER ORDERED that the parties meet and confer."
    )
    section = decretal(order)
    assert section is not None
    assert section.startswith("IT IS ORDERED")
    assert "FURTHER ORDERED" in section


def test_decretal_falls_back_to_the_last_concluding_anchor() -> None:
    order = (
        "For the reasons below, I hold... CONCLUSION\n"
        "For the foregoing reasons, the motion is denied."
    )
    assert decretal(order) == "For the foregoing reasons, the motion is denied."
    assert decretal("A scheduling order with no ruling at all.") is None


# --- resolving a motion ------------------------------------------------------


def test_open_motion_resolves_to_none() -> None:
    entries = [
        MOTION,
        entry(50, "RESPONSE in Opposition re 45 MOTION to Dismiss", day="2026-02-01"),
    ]
    assert resolve_motion(MTD, entries) is None


def test_ruling_from_docket_text_cites_its_entry() -> None:
    ruling = entry(
        60, "ORDER granting 45 Motion to Dismiss with leave to amend. Signed by Judge A."
    )
    resolved = resolve_motion(MTD, [ruling, MOTION])
    assert resolved == MotionResolution(
        TrialMoment.dismissal,
        MotionRuling.granted,
        Leave.with_leave,
        Citation(entry_id=1060, entry_number=60, date_filed=date(2026, 3, 1)),
        Source.docket_text,
    )


def test_party_filings_never_resolve() -> None:
    entries = [
        MOTION,
        entry(
            50,
            "REPLY in Support re 45 MOTION to Dismiss; asks that it be granted",
            day="2026-02-10",
        ),
        entry(51, "NOTICE of Supplemental Authority re 45 MOTION to Dismiss", day="2026-02-11"),
    ]
    assert resolve_motion(MTD, entries) is None


def test_an_order_on_another_motion_is_passed_over() -> None:
    entries = [
        MOTION,
        entry(52, "MOTION to Stay Discovery", day="2026-02-01"),
        entry(55, "ORDER granting 52 Motion to Stay Discovery", day="2026-02-15"),
        entry(60, "ORDER denying 45 Motion to Dismiss", day="2026-03-01"),
    ]
    resolved = resolve_motion(MTD, entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    assert resolved.cited.entry_number == 60


def test_one_order_on_two_motions_reads_the_motions_own_clause() -> None:
    ruling = entry(60, "ORDER granting 45 Motion to Dismiss; denying 47 Motion to Strike")
    resolved = resolve_motion(MTD, [MOTION, ruling])
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.granted
    other = resolve_motion(MotionEvent(TrialMoment.dismissal, 47), [MOTION, ruling])
    assert isinstance(other, MotionResolution)
    assert other.ruling is MotionRuling.denied


def test_order_text_agrees_with_docket_text() -> None:
    ruling = entry(60, "MEMORANDUM OPINION AND ORDER re 45 Motion to Dismiss")
    text = (
        "Defendants' arguments are considered below and largely denied. "
        "IT IS HEREBY ORDERED that Defendants' Motion to Dismiss (ECF No. 45) is GRANTED IN PART "
        "and DENIED IN PART, and Count III is DISMISSED with leave to amend."
    )
    resolved = resolve_motion(MTD, [MOTION, ruling], order_texts={1060: text})
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.granted_in_part
    assert resolved.leave is Leave.with_leave
    assert resolved.source is Source.order_text


def test_docket_text_and_order_must_agree() -> None:
    ruling = entry(60, "ORDER granting 45 Motion to Dismiss")
    text = "IT IS ORDERED that the Motion to Dismiss (Dkt. No. 45) is DENIED."
    resolved = resolve_motion(MTD, [MOTION, ruling], order_texts={1060: text})
    assert isinstance(resolved, Unresolved)
    assert "docket text reads granted" in resolved.reason
    assert resolved.candidates[-1].entry_number == 60


def test_agreeing_readings_are_both() -> None:
    ruling = entry(60, "ORDER denying 45 Motion to Dismiss")
    text = "For the foregoing reasons, the Motion to Dismiss (ECF No. 45) is DENIED."
    resolved = resolve_motion(MTD, [MOTION, ruling], order_texts={1060: text})
    assert isinstance(resolved, MotionResolution)
    assert resolved.source is Source.both


def test_an_order_citing_the_motion_with_no_readable_ruling_goes_to_triage() -> None:
    ruling = entry(60, "MEMORANDUM OPINION re 45")
    text = "IT IS ORDERED that the parties brief the effect of ECF No. 45 on Count II."
    assert isinstance(resolve_motion(MTD, [MOTION, ruling], order_texts={1060: text}), Unresolved)


def test_moot_after_an_amended_complaint() -> None:
    entries = [
        MOTION,
        entry(50, "AMENDED COMPLAINT against OpenAI, Inc.", day="2026-02-01"),
        entry(
            51,
            "ORDER denying as moot 45 Motion to Dismiss in light of 50 Amended Complaint",
            day="2026-02-03",
        ),
    ]
    resolved = resolve_motion(MTD, entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.mooted
    assert resolved.leave is None


def test_withdrawal_notice_citing_the_motion() -> None:
    entries = [MOTION, entry(50, "NOTICE of Withdrawal of 45 MOTION to Dismiss", day="2026-02-01")]
    resolved = resolve_motion(MTD, entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.withdrawn


def test_closure_moots_an_open_motion() -> None:
    entries = [
        MOTION,
        entry(
            70, "STIPULATION of Voluntary Dismissal with prejudice by all parties", day="2026-04-01"
        ),
    ]
    resolved = resolve_motion(MTD, entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.mooted
    assert resolved.cited.entry_number == 70


def test_partial_dismissal_does_not_moot() -> None:
    entries = [
        MOTION,
        entry(70, "STIPULATION of Dismissal as to Defendant Microsoft Corp.", day="2026-04-01"),
    ]
    assert resolve_motion(MTD, entries) is None


def test_an_unnumbered_minute_order_after_the_motion() -> None:
    entries = [
        MOTION,
        entry(50, "RESPONSE in Opposition re 45 MOTION to Dismiss", day="2026-02-01"),
        entry(None, "MINUTE ORDER denying 45 Motion to Dismiss", day="2026-03-05", entry_id=7777),
    ]
    resolved = resolve_motion(MTD, entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    assert resolved.cited == Citation(7777, None, date(2026, 3, 5))


def test_leave_is_read_only_for_a_dismissal() -> None:
    motion = entry(80, "MOTION for Summary Judgment", day="2026-05-01")
    ruling = entry(
        90, "ORDER granting 80 Motion for Summary Judgment with prejudice", day="2026-06-01"
    )
    resolved = resolve_motion(MotionEvent(TrialMoment.summary_judgment, 80), [motion, ruling])
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.granted
    assert resolved.leave is None


def test_an_uncited_order_rules_only_on_a_motion_of_its_own_kind() -> None:
    motion = entry(30, "MOTION to Certify Class", day="2026-01-01")
    entries = [
        motion,
        entry(40, "ORDER: the motion for class certification is DENIED.", day="2026-03-01"),
    ]
    resolved = resolve_motion(MotionEvent(TrialMoment.class_certification, 30), entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    other = [motion, entry(40, "ORDER: the motion to dismiss is DENIED.", day="2026-03-01")]
    assert resolve_motion(MotionEvent(TrialMoment.class_certification, 30), other) is None


# --- the final disposition ---------------------------------------------------


@pytest.mark.parametrize(
    ("text", "outcome"),
    [
        (
            "JUDGMENT in favor of Defendant OpenAI, Inc. against Plaintiffs",
            JudgmentOutcome.defendant,
        ),
        ("JUDGMENT in favor of Plaintiff and against Defendants", JudgmentOutcome.plaintiff),
        (
            "JUDGMENT in favor of Plaintiff on Count I and in favor of Defendant on Count II",
            JudgmentOutcome.mixed,
        ),
        ("CONSENT JUDGMENT entered", JudgmentOutcome.no_merits_decision),
        ("JUDGMENT entered.", None),
    ],
)
def test_read_judgment(text: str, outcome: JudgmentOutcome | None) -> None:
    assert read_judgment(text) is outcome


def test_judgment_open_while_no_closure_or_judgment() -> None:
    entries = [MOTION, entry(60, "ORDER granting 45 Motion to Dismiss with leave to amend")]
    assert resolve_judgment(entries) is None


def test_final_judgment_for_a_side() -> None:
    entries = [
        MOTION,
        entry(60, "ORDER granting 45 Motion to Dismiss with prejudice"),
        entry(61, "CLERK'S JUDGMENT in favor of Defendants against Plaintiffs", day="2026-03-02"),
    ]
    resolved = resolve_judgment(entries)
    assert resolved == JudgmentResolution(
        JudgmentOutcome.defendant,
        Citation(1061, 61, date(2026, 3, 2)),
        Source.docket_text,
    )


def test_settlement_is_no_merits_decision() -> None:
    entries = [
        MOTION,
        entry(70, "NOTICE of Settlement", day="2026-04-01"),
        entry(
            72,
            "STIPULATION of Dismissal with prejudice pursuant to Rule 41(a)(1)(A)(ii)",
            day="2026-04-20",
        ),
    ]
    resolved = resolve_judgment(entries)
    assert isinstance(resolved, JudgmentResolution)
    assert resolved.outcome is JudgmentOutcome.no_merits_decision
    assert resolved.cited.entry_number == 72
    found = find_closure(entries)
    assert found is not None
    assert found["entry_number"] == 72


def test_partial_and_default_judgments_are_not_final() -> None:
    entries = [
        entry(60, "PARTIAL JUDGMENT under Rule 54(b) in favor of Defendant Meta"),
        entry(61, "DEFAULT JUDGMENT against Defendant Doe"),
    ]
    assert resolve_judgment(entries) is None


def test_a_proposed_judgment_is_a_party_filing() -> None:
    assert resolve_judgment([entry(60, "PROPOSED JUDGMENT in favor of Plaintiff")]) is None


def test_a_judgment_naming_no_side_goes_to_triage() -> None:
    resolved = resolve_judgment([entry(60, "JUDGMENT entered. Case closed.")])
    assert isinstance(resolved, Unresolved)
    assert resolved.moment is TrialMoment.judgment


def test_judgment_text_and_docket_text_must_agree() -> None:
    judgment = entry(60, "JUDGMENT in favor of Plaintiff")
    resolved = resolve_judgment(
        [judgment], order_texts={1060: "Judgment is entered in favor of Defendants."}
    )
    assert isinstance(resolved, Unresolved)
    agreed = resolve_judgment(
        [judgment], order_texts={1060: "Judgment for the plaintiff... in favor of plaintiffs."}
    )
    assert isinstance(agreed, JudgmentResolution)
    assert agreed.source is Source.both
