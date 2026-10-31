"""The trial stage's deterministic resolver (``pipeline/trial_resolver.py``).

The rule is built to miss rather than misread, so most of these cases are
realistic texts that must read no ruling, or go to triage, rather than record
a wrong one.
"""

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
    read_docket_ruling,
    read_judgment,
    read_leave,
    read_order_ruling,
    resolve_judgment,
    resolve_motion,
)


def entry(
    number: int | None, description: str, *, day: str = "2026-03-01", entry_id: int | None = None
) -> dict[str, Any]:
    return {
        "id": entry_id if entry_id is not None else 1000 + (number or 0),
        "entry_number": number,
        "date_filed": day,
        "description": description,
        "recap_documents": [],
    }


MTD = MotionEvent(TrialMoment.dismissal, 45)
MOTION = entry(
    45, "MOTION to Dismiss for Failure to State a Claim filed by OpenAI, Inc.", day="2026-01-10"
)


def ruling_on(event: MotionEvent, *later: dict[str, Any], **kw: Any) -> Any:
    return resolve_motion(event, [MOTION, *later], **kw)


# --- the motion kind ---------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "moment"),
    [
        ("MOTION to Dismiss for Lack of Jurisdiction", TrialMoment.dismissal),
        ("Renewed MOTION to Dismiss the Amended Complaint", TrialMoment.dismissal),
        ("MOTION to Certify Class filed by Plaintiffs", TrialMoment.class_certification),
        ("MOTION for Class Certification", TrialMoment.class_certification),
        ("MOTION for Partial Summary Judgment", TrialMoment.summary_judgment),
        ("Cross MOTION for Summary Judgment", TrialMoment.summary_judgment),
        ("MOTION to Compel Discovery", None),
        ("MOTION to Certify Order for Interlocutory Appeal", None),
        ("MOTION for Certification of Interlocutory Appeal", None),
        ("MOTION to Certify Question to the California Supreme Court", None),
        ("MOTION for Leave to File Excess Pages for its Motion to Dismiss", None),
        ("MOTION for Extension of Time to File Response re 45 MOTION to Dismiss", None),
        ("MOTION to Stay Discovery Pending Resolution of Motion to Dismiss", None),
        ("MOTION to Dismiss Counterclaims", None),
        ("ORDER setting conference", None),
    ],
)
def test_motion_moment(text: str, moment: TrialMoment | None) -> None:
    assert motion_moment(text) is moment


def test_motion_event_refuses_the_judgment_moment() -> None:
    with pytest.raises(ValueError, match="not a motion moment"):
        MotionEvent(TrialMoment.judgment, 1)


# --- reading a docket text ---------------------------------------------------


@pytest.mark.parametrize(
    ("text", "ruling"),
    [
        ("ORDER granting 45 Motion to Dismiss", MotionRuling.granted),
        ("ORDER denying [45] Motion to Dismiss (Signed by Judge Grant)", MotionRuling.denied),
        ("ORDER denying 45 Motion to Dismiss filed by Grant Thornton LLP", MotionRuling.denied),
        (
            "ORDER granting in part and denying in part 45 Motion to Dismiss",
            MotionRuling.granted_in_part,
        ),
        (
            "ORDER denying 47 Motion to Strike and granting 45 Motion to Dismiss",
            MotionRuling.granted,
        ),
        (
            "ORDER granting 45 Motion to Dismiss, denying 47 Motion for Sanctions",
            MotionRuling.granted,
        ),
        (
            "ORDER denying 45 Motion to Dismiss, and granting Plaintiff leave to file a sur-reply",
            MotionRuling.denied,
        ),
        ("ORDER granting 45 and 47 Motions to Dismiss", MotionRuling.granted),
        ("ORDER denying as moot 45 Motion to Dismiss", MotionRuling.mooted),
        ("ORDER finding as moot 45 Motion to Dismiss", MotionRuling.mooted),
        # The motion's number names another motion's subject, not its object.
        ("ORDER granting 46 Motion for Leave to File Excess Pages re 45 Motion to Dismiss", None),
        ("ORDER granting 50 Stipulation to Extend Time to Respond to 45 MOTION to Dismiss", None),
        ("ORDER denying 52 Motion to Strike 45 Motion to Dismiss", None),
        (
            "ORDER granting 52 Motion for Leave to File Amicus Brief in Support of "
            + "45 Motion to Dismiss",
            None,
        ),
        ("ORDER granting 50 Motion to Withdraw 45 Motion to Dismiss", None),
        ("STIPULATED ORDER granting extension of time re 45 MOTION to Dismiss", None),
        ("ORDER setting hearing on 45 Motion to Dismiss", None),
    ],
)
def test_read_docket_ruling(text: str, ruling: MotionRuling | None) -> None:
    reading = read_docket_ruling(text, 45)
    assert reading.ruling is ruling
    assert reading.conflict is None


def test_rule_12_is_not_entry_12() -> None:
    text = "ORDER denying 30 Motion to Strike portions of the Rule 12 motion"
    assert read_docket_ruling(text, 12).ruling is None


def test_terminating_alone_is_a_conflict() -> None:
    assert read_docket_ruling("ORDER terminating 45 Motion to Dismiss", 45).conflict is not None


@pytest.mark.parametrize(
    ("text", "leave"),
    [
        ("dismissed with leave to amend", Leave.with_leave),
        ("Leave to amend is DENIED", Leave.without_leave),
        ("dismissed with prejudice", Leave.without_leave),
        ("plaintiffs may file a second amended complaint within 21 days", Leave.with_leave),
        ("dismissed without prejudice", Leave.unstated),
        (
            "Counts I and II are dismissed with prejudice; Count III is dismissed "
            + "with leave to amend.",
            Leave.mixed,
        ),
    ],
)
def test_read_leave(text: str, leave: Leave) -> None:
    assert read_leave(text) is leave


# --- reading an order --------------------------------------------------------


def test_decretal_starts_at_the_last_ordering_paragraph() -> None:
    order = (
        "On May 1 the Court wrote: IT IS ORDERED that the motion to stay is granted. "
        "The discussion follows and the motion is denied in the Court's view. "
        "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is DENIED. "
        "IT IS FURTHER ORDERED that the parties meet and confer."
    )
    section = decretal(order)
    assert section is not None
    assert section.startswith("IT IS ORDERED that the Motion to Dismiss")
    assert "FURTHER ORDERED" in section


def test_decretal_falls_back_to_the_last_concluding_anchor() -> None:
    order = (
        "For the reasons below, I hold... CONCLUSION\n"
        "For the foregoing reasons, the motion is denied."
    )
    assert decretal(order) == "For the foregoing reasons, the motion is denied."
    assert decretal("A scheduling order with no ruling at all.") is None


@pytest.mark.parametrize(
    ("text", "ruling"),
    [
        ("IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is DENIED.", MotionRuling.denied),
        (
            "Accordingly, the Court GRANTS Defendants' Motion to Dismiss (Dkt. 45).",
            MotionRuling.granted,
        ),
        (
            "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is GRANTED IN PART "
            + "and DENIED IN PART.",
            MotionRuling.granted_in_part,
        ),
        (
            "IT IS ORDERED that the motion (ECF No. 45) is GRANTED as to Count I "
            + "and DENIED as to Count II.",
            MotionRuling.granted_in_part,
        ),
        (
            "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is DENIED, and Plaintiffs' "
            + "request for jurisdictional discovery is granted.",
            MotionRuling.denied,
        ),
        (
            "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is GRANTED. "
            + "Leave to amend is DENIED.",
            MotionRuling.granted,
        ),
        ("IT IS ORDERED that the parties brief the effect of ECF No. 45 on Count II.", None),
        ("IT IS ORDERED that the motion to dismiss is GRANTED.", None),
    ],
)
def test_read_order_ruling(text: str, ruling: MotionRuling | None) -> None:
    reading = read_order_ruling(text, 45)
    assert reading.ruling is ruling
    assert reading.conflict is None


def test_a_grant_as_to_some_counts_alone_is_a_conflict() -> None:
    text = "IT IS ORDERED that the motion (ECF No. 45) is GRANTED as to Count I."
    assert read_order_ruling(text, 45).conflict is not None


# --- resolving a motion ------------------------------------------------------


def test_open_motion_resolves_to_none() -> None:
    assert ruling_on(MTD, entry(50, "RESPONSE in Opposition re 45 MOTION to Dismiss")) is None


def test_ruling_from_docket_text_cites_its_entry() -> None:
    ruling = entry(
        60, "ORDER granting 45 Motion to Dismiss with leave to amend. Signed by Judge A."
    )
    assert ruling_on(MTD, ruling) == MotionResolution(
        TrialMoment.dismissal,
        MotionRuling.granted,
        Leave.with_leave,
        Citation(entry_id=1060, entry_number=60, date_filed=date(2026, 3, 1)),
        Source.docket_text,
    )


def test_an_order_about_the_motion_does_not_pre_empt_its_ruling() -> None:
    resolved = ruling_on(
        MTD,
        entry(
            50,
            "ORDER granting 46 Motion for Leave to File Excess Pages re 45 Motion to Dismiss",
            day="2026-02-01",
        ),
        entry(55, "ORDER setting hearing on 45 Motion to Dismiss", day="2026-02-10"),
        entry(60, "ORDER denying 45 Motion to Dismiss", day="2026-03-01"),
    )
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    assert resolved.cited.entry_number == 60


@pytest.mark.parametrize(
    "text",
    [
        "REPLY in Support re 45 MOTION to Dismiss; asks that it be granted",
        "MEMORANDUM re 45 Motion to Dismiss filed by Plaintiffs, asking that it be denied",
        "ORDER AND RECOMMENDATION re 45 Motion to Dismiss: RECOMMENDED that the motion be granted",
        "MEMORANDUM AND RECOMMENDATION granting 45 Motion to Dismiss",
        "TEXT ORDER: Microsoft's motion to dismiss is GRANTED.",
    ],
)
def test_what_is_not_a_ruling(text: str) -> None:
    assert ruling_on(MTD, entry(60, text)) is None


def test_order_text_settles_a_docket_text_with_no_verb() -> None:
    ruling = entry(60, "MEMORANDUM OPINION AND ORDER re 45 Motion to Dismiss")
    text = (
        "Defendants' arguments are considered below and largely denied. "
        "IT IS HEREBY ORDERED that Defendants' Motion to Dismiss (ECF No. 45) is GRANTED IN PART "
        "and DENIED IN PART, and Count III is DISMISSED with leave to amend."
    )
    resolved = ruling_on(MTD, ruling, order_texts={1060: text})
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.granted_in_part
    assert resolved.leave is Leave.with_leave
    assert resolved.source is Source.order_text


def test_docket_text_and_order_must_agree() -> None:
    ruling = entry(60, "ORDER granting 45 Motion to Dismiss")
    text = "IT IS ORDERED that the Motion to Dismiss (Dkt. No. 45) is DENIED."
    resolved = ruling_on(MTD, ruling, order_texts={1060: text})
    assert isinstance(resolved, Unresolved)
    assert "docket text reads granted" in resolved.reason
    assert resolved.candidates == (Citation(1060, 60, date(2026, 3, 1)),)


def test_agreeing_readings_are_both() -> None:
    ruling = entry(60, "ORDER denying 45 Motion to Dismiss")
    text = "For the foregoing reasons, the Motion to Dismiss (ECF No. 45) is DENIED."
    resolved = ruling_on(MTD, ruling, order_texts={1060: text})
    assert isinstance(resolved, MotionResolution)
    assert resolved.source is Source.both


def test_a_scheduling_order_with_text_leaves_the_motion_open() -> None:
    ruling = entry(55, "ORDER re 45 Motion to Dismiss")
    text = "The hearing on ECF No. 45 is set. IT IS ORDERED that the parties appear."
    assert ruling_on(MTD, ruling, order_texts={1055: text}) is None


def test_moot_after_an_amended_complaint() -> None:
    resolved = ruling_on(
        MTD,
        entry(50, "AMENDED COMPLAINT against OpenAI, Inc.", day="2026-02-01"),
        entry(
            51,
            "ORDER denying as moot 45 Motion to Dismiss in light of 50 Amended Complaint",
            day="2026-02-03",
        ),
    )
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.mooted
    assert resolved.leave is None


def test_withdrawal_notice_naming_the_motion() -> None:
    resolved = ruling_on(MTD, entry(50, "NOTICE of Withdrawal of 45 MOTION to Dismiss"))
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.withdrawn
    other = entry(50, "NOTICE of Withdrawal of 48 Motion for Extension re 45 MOTION to Dismiss")
    assert ruling_on(MTD, other) is None


def test_closure_moots_an_open_motion() -> None:
    closing = entry(70, "STIPULATION of Voluntary Dismissal with prejudice by all parties")
    resolved = ruling_on(MTD, closing)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.mooted
    assert resolved.cited.entry_number == 70


@pytest.mark.parametrize(
    "text",
    [
        "STIPULATION of Dismissal as to Defendant Microsoft Corp.",
        "STIPULATION re 45 MOTION to Dismiss",
        "STIPULATION regarding briefing on Motion to Dismiss",
        "STIPULATION to Dismiss Defendant Doe",
        "STIPULATION of Dismissal of Plaintiff Jane Roe's claims",
        "NOTICE of Voluntary Dismissal of Defendant Anthropic PBC",
        "MOTION for Voluntary Dismissal under Rule 41(a)(2)",
        "RESPONSE in Opposition re 50 Motion for Voluntary Dismissal",
        "ORDER denying 50 Motion for Voluntary Dismissal",
        "MOTION for Final Approval of Class Action Settlement",
        "ORDER granting preliminary approval of class settlement; "
        + "Final Approval Hearing set for 9/1/2026",
        "MOTION for Entry of Consent Judgment",
        "NOTICE of Settlement",
    ],
)
def test_non_closures(text: str) -> None:
    assert find_closure([entry(70, text)]) is None
    assert ruling_on(MTD, entry(70, text)) is None
    assert resolve_judgment([entry(70, text)]) is None


@pytest.mark.parametrize(
    "text",
    [
        "STIPULATION of Dismissal with prejudice pursuant to Rule 41(a)(1)(A)(ii)",
        "NOTICE of Voluntary Dismissal of the entire action without prejudice",
        "ORDER granting 72 Stipulation of Dismissal",
        "ORDER granting 60 Motion for Final Approval of Class Action Settlement",
        "FINAL APPROVAL ORDER and judgment",
        "CONSENT JUDGMENT",
    ],
)
def test_closures(text: str) -> None:
    assert find_closure([entry(70, text)]) is not None


def test_an_unnumbered_minute_order_after_the_motion() -> None:
    resolved = ruling_on(
        MTD,
        entry(50, "RESPONSE in Opposition re 45 MOTION to Dismiss", day="2026-02-01"),
        entry(None, "MINUTE ORDER denying 45 Motion to Dismiss", day="2026-03-05", entry_id=7777),
    )
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


def test_a_renewed_motion_is_its_own_event() -> None:
    entries = [
        MOTION,
        entry(50, "AMENDED COMPLAINT", day="2026-02-01"),
        entry(55, "MOTION to Dismiss the Amended Complaint", day="2026-02-20"),
        entry(60, "ORDER granting 55 Motion to Dismiss", day="2026-04-01"),
    ]
    assert resolve_motion(MTD, entries) is None
    renewed = resolve_motion(MotionEvent(TrialMoment.dismissal, 55), entries)
    assert isinstance(renewed, MotionResolution)
    assert renewed.ruling is MotionRuling.granted


# --- the final disposition ---------------------------------------------------


@pytest.mark.parametrize(
    ("text", "outcome"),
    [
        (
            "JUDGMENT in favor of Defendant OpenAI, Inc. against Plaintiffs",
            JudgmentOutcome.defendant,
        ),
        ("JUDGMENT in favor of Defendants against Plaintiffs", JudgmentOutcome.defendant),
        ("JUDGMENT in favor of Plaintiff and against Defendants", JudgmentOutcome.plaintiff),
        (
            "JUDGMENT in favor of Plaintiff on Count I and in favor of Defendant on Count II",
            JudgmentOutcome.mixed,
        ),
        (
            "JUDGMENT: Plaintiffs take nothing on their claims against Defendants",
            JudgmentOutcome.defendant,
        ),
        (
            "JUDGMENT in favor of Defendant. All claims against Defendant are dismissed "
            + "with prejudice.",
            JudgmentOutcome.defendant,
        ),
        (
            "JUDGMENT: Plaintiff shall take nothing; the action against Defendants is "
            + "dismissed on the merits",
            JudgmentOutcome.defendant,
        ),
        (
            "JUDGMENT in favor of defendant on the jury verdict; plaintiff's claims against "
            + "defendant fail",
            JudgmentOutcome.defendant,
        ),
        ("CONSENT JUDGMENT", JudgmentOutcome.no_merits_decision),
        ("JUDGMENT entered.", None),
    ],
)
def test_read_judgment(text: str, outcome: JudgmentOutcome | None) -> None:
    assert read_judgment(text) is outcome


def test_judgment_open_while_no_closure_or_judgment() -> None:
    entries = [
        MOTION,
        entry(60, "ORDER granting 45 Motion to Dismiss with leave to amend"),
        entry(
            61,
            "ORDER granting 80 Motion for Summary Judgment. Judgment is hereby entered "
            "against Defendant Doe on Count I.",
        ),
    ]
    assert resolve_judgment(entries) is None


def test_final_judgment_for_a_side() -> None:
    entries = [
        MOTION,
        entry(60, "ORDER granting 45 Motion to Dismiss with prejudice"),
        entry(61, "CLERK'S JUDGMENT in favor of Defendants against Plaintiffs", day="2026-03-02"),
    ]
    assert resolve_judgment(entries) == JudgmentResolution(
        JudgmentOutcome.defendant,
        Citation(1061, 61, date(2026, 3, 2)),
        Source.docket_text,
    )


def test_a_final_judgment_mentioning_default_is_still_final() -> None:
    text = (
        "FINAL JUDGMENT in favor of Defendants. Plaintiffs' motion for default judgment "
        "against Doe is denied."
    )
    resolved = resolve_judgment([entry(60, text)])
    assert isinstance(resolved, JudgmentResolution)
    assert resolved.outcome is JudgmentOutcome.defendant


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


def test_partial_and_default_judgments_are_not_final() -> None:
    entries = [
        entry(60, "PARTIAL JUDGMENT under Rule 54(b) in favor of Defendant Meta"),
        entry(61, "DEFAULT JUDGMENT against Defendant Doe"),
    ]
    assert resolve_judgment(entries) is None


def test_a_proposed_judgment_is_not_a_judgment() -> None:
    assert resolve_judgment([entry(60, "PROPOSED JUDGMENT in favor of Plaintiff")]) is None


def test_a_judgment_naming_no_side_goes_to_triage() -> None:
    resolved = resolve_judgment([entry(60, "JUDGMENT entered. Case closed.")])
    assert isinstance(resolved, Unresolved)
    assert resolved.moment is TrialMoment.judgment


def test_a_vacated_or_amended_judgment_goes_to_triage() -> None:
    entries = [
        entry(90, "JUDGMENT in favor of Plaintiff", day="2026-05-01"),
        entry(95, "ORDER vacating 90 Judgment", day="2026-06-01"),
        entry(96, "AMENDED JUDGMENT in favor of Defendants", day="2026-06-02"),
    ]
    resolved = resolve_judgment(entries)
    assert isinstance(resolved, Unresolved)
    assert [c.entry_number for c in resolved.candidates] == [90, 95, 96]


def test_judgment_text_is_read_from_its_decretal_language() -> None:
    judgment = entry(60, "JUDGMENT")
    text = (
        "This action came before the Court on Plaintiffs' claims against Defendants. "
        "IT IS ORDERED AND ADJUDGED that judgment is entered in favor of Defendants."
    )
    resolved = resolve_judgment([judgment], order_texts={1060: text})
    assert isinstance(resolved, JudgmentResolution)
    assert resolved.outcome is JudgmentOutcome.defendant
    assert resolved.source is Source.order_text


def test_judgment_text_and_docket_text_must_agree() -> None:
    judgment = entry(60, "JUDGMENT in favor of Plaintiff")
    clash = resolve_judgment(
        [judgment], order_texts={1060: "Judgment is entered in favor of Defendants."}
    )
    assert isinstance(clash, Unresolved)
    agreed = resolve_judgment(
        [judgment], order_texts={1060: "Judgment is entered in favor of plaintiffs."}
    )
    assert isinstance(agreed, JudgmentResolution)
    assert agreed.source is Source.both
