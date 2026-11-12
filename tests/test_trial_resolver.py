"""The trial stage's deterministic resolver (``pipeline/trial_resolver.py``).

The rule is built to miss rather than misread, so most of these cases are
realistic texts that must read no ruling, or go to triage, rather than record
a wrong one.
"""

from __future__ import annotations

import time
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


DISCUSSION = "The discussion weighs each argument at length. " * 30


def test_decretal_is_the_last_run_of_ordering_paragraphs() -> None:
    order = (
        "On May 1 the Court wrote: IT IS ORDERED that the motion to stay is granted. "
        + DISCUSSION
        + "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is DENIED. "
        + "IT IS ORDERED that the parties meet and confer. "
        + "IT IS FURTHER ORDERED that the Clerk close the motion."
    )
    section = decretal(order)
    assert section is not None
    assert section.startswith("IT IS ORDERED that the Motion to Dismiss")
    assert "FURTHER ORDERED" in section


def test_decretal_starts_at_the_conclusion_before_its_ordering_paragraphs() -> None:
    order = (
        "IT IS ORDERED that briefing proceed. "
        + DISCUSSION
        + "For the foregoing reasons, IT IS THEREFORE ORDERED that the Motion to Dismiss "
        + "(ECF No. 45) is GRANTED."
    )
    section = decretal(order)
    assert section is not None
    assert section.startswith("For the foregoing reasons")
    assert read_order_ruling(order, 45).ruling is MotionRuling.granted


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


def test_an_opinion_the_docket_text_cannot_read_is_triage() -> None:
    ruling = entry(60, "MEMORANDUM OPINION AND ORDER re 45 Motion to Dismiss")
    text = (
        "Defendants' arguments are considered below and largely denied. "
        "IT IS HEREBY ORDERED that Defendants' Motion to Dismiss (ECF No. 45) is GRANTED IN PART "
        "and DENIED IN PART, and Count III is DISMISSED with leave to amend."
    )
    # The order's text checks a docket reading; it never resolves on its own.
    for texts in ({1060: text}, {}):
        resolved = ruling_on(MTD, ruling, order_texts=texts)
        assert isinstance(resolved, Unresolved)
        assert "states no ruling" in resolved.reason


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
    assert isinstance(resolve_judgment([judgment], order_texts={1060: text}), Unresolved)
    named = entry(60, "JUDGMENT in favor of Defendants")
    resolved = resolve_judgment([named], order_texts={1060: text})
    assert isinstance(resolved, JudgmentResolution)
    assert resolved.outcome is JudgmentOutcome.defendant
    assert resolved.source is Source.both


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


# --- second-round counterexamples: none may record an outcome ----------------

DOCKET_DENY = entry(60, "ORDER denying 45 Motion to Dismiss")


@pytest.mark.parametrize(
    "order",
    [
        "IT IS ORDERED that Plaintiff's unopposed motion for an extension of time to respond to "
        + "Defendant's Motion to Dismiss (ECF No. 45) is GRANTED.",
        "Accordingly, the Court GRANTS Plaintiff leave to file a sur-reply to the Motion to "
        + "Dismiss (ECF No. 45).",
        "IT IS ORDERED that Plaintiff's Motion to Strike the Reply in Support of the Motion to "
        + "Dismiss [45] is GRANTED.",
        "IT IS ORDERED that oral argument on the Motion to Dismiss (ECF No. 45) is granted.",
        "IT IS ORDERED that Plaintiff show cause in writing within 14 days why Defendant's "
        + "Motion to Dismiss (ECF No. 45) should not be granted as unopposed.",
        "If Plaintiff fails to respond, the Motion to Dismiss (ECF No. 45) will be granted.",
    ],
)
def test_order_clauses_about_other_matters_read_no_ruling(order: str) -> None:
    assert read_order_ruling(order, 45).ruling is None
    # With the docket text ruling the other way, nothing contradicts it.
    resolved = ruling_on(MTD, DOCKET_DENY, order_texts={1060: order})
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    assert resolved.source is Source.docket_text


@pytest.mark.parametrize(
    "order",
    [
        "Accordingly, the Court GRANTS Defendants' Motion to Dismiss (ECF No. 45) and DENIES "
        + "Plaintiff's request for oral argument.",
        "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is GRANTED, Plaintiff's motion "
        + "for sanctions is DENIED.",
    ],
)
def test_a_separate_denial_is_not_a_ruling_in_part(order: str) -> None:
    assert read_order_ruling(order, 45).ruling is MotionRuling.granted


def test_a_ruling_with_an_exception_is_triage() -> None:
    order = (
        "IT IS ORDERED that the Motion to Dismiss (ECF No. 45) is DENIED, except that "
        + "Defendant's request for judicial notice is GRANTED."
    )
    assert read_order_ruling(order, 45).conflict is not None
    assert isinstance(ruling_on(MTD, DOCKET_DENY, order_texts={1060: order}), Unresolved)


def test_an_order_on_another_entry_never_resolves_the_motion() -> None:
    docket = entry(60, "ORDER granting 50 Motion for Leave to File Excess Pages in support of 45")
    order = (
        "IT IS ORDERED that the Motion for Leave to File Excess Pages in support of the Motion "
        + "to Dismiss (ECF No. 45) is GRANTED."
    )
    assert ruling_on(MTD, docket, order_texts={1060: order}) is None


def test_the_adopting_order_rules() -> None:
    text = "ORDER ADOPTING 58 REPORT AND RECOMMENDATIONS and granting 45 Motion to Dismiss"
    resolved = ruling_on(MTD, entry(60, text))
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.granted


@pytest.mark.parametrize(
    "text",
    [
        # A qualifier after the number may be the ruling's or the motion's own
        # title ("Motion to Dismiss in Part", "... as Moot"): triage either way.
        "ORDER denying 45 Motion to Dismiss as moot in light of the 52 Amended Complaint.",
        "TEXT ORDER denying [45] Motion to Dismiss as MOOT",
        "ORDER denying 45 Motion to Dismiss without prejudice as moot.",
        "ORDER granting 45 Motion to Dismiss in part.",
        "ORDER denying 45 MOTION to Dismiss in Part Plaintiff's First Amended Complaint",
        "ORDER granting 45 MOTION to Dismiss Case as Moot filed by Acme Corp",
        "ORDER granting 45 Motion to Dismiss as to Count I.",
        "ORDER granting 45 Motion to Dismiss only as to the federal claims.",
        "ORDER granting 45 Motion to Dismiss except as to Count III, which is moot",
    ],
)
def test_a_qualified_docket_ruling_is_triage(text: str) -> None:
    assert isinstance(ruling_on(MTD, entry(60, text)), Unresolved)


@pytest.mark.parametrize(
    "text",
    [
        "ORDER granting 45 Motion to Dismiss, rendering 50 Motion to Stay Discovery moot",
        "ORDER granting 45 Motion to Dismiss and 47 Motion to Dismiss in part",
    ],
)
def test_a_qualifier_on_another_motion_stays_with_it(text: str) -> None:
    resolved = ruling_on(MTD, entry(60, text))
    assert (
        isinstance(resolved, MotionResolution)
        or resolved is None
        or isinstance(resolved, Unresolved)
    )
    if isinstance(resolved, MotionResolution):
        assert resolved.ruling is MotionRuling.granted


@pytest.mark.parametrize(
    "text",
    [
        "ORDER granting 70 Motion for Reconsideration of Order granting 45 Motion to Dismiss",
        "ORDER vacating 60 Order granting 45 Motion to Dismiss",
        "ORDER striking 60 Order granting 45 Motion to Dismiss, entered in error",
        "ORDER: The Court is inclined toward granting 45 Motion to Dismiss; hearing set for 3/1",
        "ORDER of USCA granting 45 Motion to Dismiss Appeal",
        "ORDER granting 30 days to file motion",
    ],
)
def test_references_to_a_ruling_are_not_rulings(text: str) -> None:
    assert ruling_on(MTD, entry(60, text)) is None
    assert ruling_on(MotionEvent(TrialMoment.dismissal, 30), entry(60, text)) is None


def test_leave_is_read_from_the_motions_own_ruling() -> None:
    text = (
        "ORDER granting 45 Motion to Dismiss with leave to amend; granting 47 Motion to "
        + "Dismiss with prejudice"
    )
    resolved = ruling_on(MTD, entry(60, text))
    assert isinstance(resolved, MotionResolution)
    assert resolved.leave is Leave.with_leave


def test_a_joint_motion_withdrawn_by_one_movant_stays_open() -> None:
    motion = entry(45, "JOINT MOTION to Dismiss by Acme Corp. and Beta LLC", day="2026-01-10")
    notice = entry(50, "NOTICE of Withdrawal of 45 Motion to Dismiss by Defendant Beta")
    assert resolve_motion(MTD, [motion, notice]) is None


def test_a_number_not_naming_a_motion_is_not_an_object() -> None:
    assert ruling_on(MTD, entry(60, "ORDER granting 45 days to file amended complaint")) is None


def test_a_warning_is_not_leave() -> None:
    text = (
        "ORDER granting 45 Motion to Dismiss with leave to amend. Amended complaint due within 21 "
        + "days; failure to file will result in dismissal with prejudice."
    )
    resolved = ruling_on(MTD, entry(60, text))
    assert isinstance(resolved, MotionResolution)
    assert resolved.leave is Leave.with_leave


def test_a_limited_withdrawal_is_not_read() -> None:
    notice = entry(50, "NOTICE of Withdrawal of 45 Motion to Dismiss as to Count III only")
    assert ruling_on(MTD, notice) is None


@pytest.mark.parametrize(
    "text",
    [
        "ORDER granting 50 Motion to Withdraw Notice of Dismissal",
        "ORDER granting 50 Motion to Vacate Stipulation of Dismissal",
        "ORDER granting 50 Motion to Strike Notice of Dismissal",
        "NOTICE of Voluntary Dismissal of Wells Fargo Bank, N.A. by Jane Doe",
        "NOTICE of Voluntary Dismissal of John Smith by Jane Doe",
        "STIPULATION of Dismissal of the Fifth Cause of Action",
        "STIPULATION of Dismissal of Fraud Claim",
        "STIPULATION of Dismissal of Crossclaims",
        "ORDER granting 60 Stipulation of Dismissal re: Defendant Smith",
        "NOTICE of Voluntary Dismissal of Appeal",
        "NOTICE of Dismissal in Related Case 3:25-cv-01234",
        "ORDER GRANTING FINAL APPROVAL OF SETTLEMENT WITH DEFENDANT BANK OF AMERICA",
        "NOTICE of Voluntary Dismissal by Plaintiff John Smith As To Defendant Acme Corp.",
        "NOTICE OF VOLUNTARY DISMISSAL BY PLAINTIFF AS TO DEFENDANT ACME CORP ONLY",
        "STIPULATION of Dismissal by Plaintiff Smith Of Defendant Jones Only",
        "NOTICE of Voluntary Dismissal by Plaintiffs Re Defendant Beta",
        "ORDER granting 70 Stipulation of Dismissal by Plaintiff Smith As To Defendant Acme",
        "ORDER granting 80 Motion for Final Approval of Settlement with the Toyota Defendants",
    ],
)
def test_second_round_non_closures(text: str) -> None:
    assert find_closure([entry(70, text)]) is None


@pytest.mark.parametrize(
    "text",
    [
        "NOTICE of Voluntary Dismissal by Plaintiffs (Smith, John)",
        "STIPULATION of Dismissal with prejudice by all parties. Signed by Judge A on 4/1/2026.",
    ],
)
def test_second_round_closures(text: str) -> None:
    assert find_closure([entry(70, text)]) is not None


@pytest.mark.parametrize(
    "text",
    [
        "JUDGMENT by default in favor of Plaintiff against Defendant Smith",
        "JUDGMENT of USCA as to 70 Notice of Appeal",
    ],
)
def test_judgments_that_are_not_the_final_disposition(text: str) -> None:
    assert resolve_judgment([entry(60, text)]) is None


@pytest.mark.parametrize(
    "text",
    [
        "JUDGMENT in favor of Defendant Smith as to all claims against Smith",
        "JUDGMENT entered against Defendant Acme's counterclaims",
        "JUDGMENT in favor of plaintiff on Defendant's counterclaim",
        "JUDGMENT in favor of Defendant Acme and judgment entered against Defendant Doe",
    ],
)
def test_judgments_the_rule_will_not_read_for_a_side(text: str) -> None:
    assert isinstance(resolve_judgment([entry(60, text)]), Unresolved)


def test_a_possessive_is_not_a_side() -> None:
    assert read_judgment("JUDGMENT in favor of Plaintiff's former employer, Defendant Acme") is None


def test_post_judgment_relief_supersedes() -> None:
    entries = [
        entry(60, "JUDGMENT in favor of Plaintiff on jury verdict", day="2026-05-01"),
        entry(
            70,
            "ORDER granting 65 Renewed Motion for Judgment as a Matter of Law; the judgment in "
            + "favor of Plaintiff is set aside",
            day="2026-06-01",
        ),
    ]
    assert isinstance(resolve_judgment(entries), Unresolved)


def test_the_closure_tail_fails_in_linear_time() -> None:
    text = "STIPULATION of Dismissal" + " by Defendants" * 200 + " x"
    started = time.perf_counter()
    assert find_closure([entry(70, text)]) is None
    assert time.perf_counter() - started < 0.5


@pytest.mark.parametrize(
    "entries",
    [
        [
            entry(60, "JUDGMENT in favor of Plaintiff and against Defendant, plus costs"),
            entry(70, "STIPULATION of Dismissal with prejudice by all parties", day="2026-05-01"),
        ],
        [
            entry(60, "PARTIAL JUDGMENT under Rule 54(b) in favor of Defendant Meta"),
            entry(70, "STIPULATION of Dismissal with prejudice by all parties", day="2026-05-01"),
        ],
    ],
)
def test_a_closure_after_a_judgment_is_not_no_merits(entries: list[dict[str, Any]]) -> None:
    resolved = resolve_judgment(entries)
    assert not (
        isinstance(resolved, JudgmentResolution)
        and resolved.outcome is JudgmentOutcome.no_merits_decision
    )


@pytest.mark.parametrize(
    ("entries", "expected"),
    [
        (
            [
                entry(
                    60,
                    "JUDGMENT in favor of Defendant. "
                    + "Plaintiff's notice of appeal is due within 30 days",
                )
            ],
            JudgmentOutcome.defendant,
        ),
        (
            [
                entry(
                    60,
                    "JUDGMENT in favor of Plaintiff and against Defendant "
                    + "in the amount of $50,000, plus costs",
                )
            ],
            JudgmentOutcome.plaintiff,
        ),
    ],
)
def test_a_judgment_mentioning_costs_or_appeal_is_still_final(
    entries: list[dict[str, Any]], expected: JudgmentOutcome
) -> None:
    resolved = resolve_judgment(entries)
    assert isinstance(resolved, JudgmentResolution)
    assert resolved.outcome is expected


@pytest.mark.parametrize(
    "text",
    [
        "JUDGMENT in favor of Third-Party Defendant Gamma "
        + "against Defendant/Third-Party Plaintiff Acme",
    ],
)
def test_third_party_judgments_are_triage(text: str) -> None:
    assert isinstance(resolve_judgment([entry(60, text)]), Unresolved)


@pytest.mark.parametrize(
    "text",
    [
        "CLERK'S JUDGMENT in favor of Plaintiff against Defendant Acme "
        + "pursuant to Fed. R. Civ. P. 55(b)(1)",
        "JUDGMENT TAXING COSTS in favor of Defendant",
    ],
)
def test_default_and_costs_judgments_are_passed_over(text: str) -> None:
    assert resolve_judgment([entry(60, text)]) is None


@pytest.mark.parametrize(
    "later",
    [
        "ORDER granting 65 Motion to Alter or Amend Judgment",
        "JUDGMENT in favor of Defendant",
    ],
)
def test_a_later_judgment_or_alteration_is_triage(later: str) -> None:
    entries = [
        entry(60, "JUDGMENT in favor of Plaintiff", day="2026-05-01"),
        entry(70, later, day="2026-06-01"),
    ]
    assert isinstance(resolve_judgment(entries), Unresolved)


@pytest.mark.parametrize(
    "text",
    [
        "JUDGMENT in favor of defendants on all claims except Count V, "
        + "which is remanded to state court",
        "JUDGMENT in favor of defendant Beta and against plaintiff. "
        + "Claims against Acme remain pending.",
        "JUDGMENT: plaintiff shall take nothing on her claims; "
        + "defendant shall take nothing on its claims",
    ],
)
def test_judgments_that_leave_claims_or_cut_both_ways_are_triage(text: str) -> None:
    assert isinstance(resolve_judgment([entry(60, text)]), Unresolved)


@pytest.mark.parametrize(
    "text",
    [
        "ORDER granting 45 Motion to Dismiss and 47 Motion to Dismiss in part",
        "ORDER granting 45 Motion to Dismiss, rendering 50 Motion to Stay Discovery moot",
        "ORDER granting 45 Motion to Dismiss and 50 Motion to Stay Discovery is moot",
    ],
)
def test_a_qualifier_anywhere_in_the_ruling_clause_is_triage(text: str) -> None:
    assert isinstance(resolve_motion(MTD, [MOTION, entry(60, text)]), Unresolved)


def test_a_long_run_of_entry_numbers_fails_in_linear_time() -> None:
    text = "ORDER granting " + "100 , " * 40 + "Stipulations to Extend Time"
    started = time.perf_counter()
    assert read_docket_ruling(text, 45).ruling is None
    assert time.perf_counter() - started < 0.5


@pytest.mark.parametrize(
    "text",
    [
        "MOTION to Dismiss or, in the Alternative, to Transfer Venue by Acme Corp.",
        "MOTION to Dismiss or Compel Arbitration by Acme Corp.",
        "MOTION to Dismiss or Stay by Acme Corp.",
    ],
)
def test_a_motion_to_dismiss_or_for_other_relief_is_not_the_dismissal_moment(text: str) -> None:
    assert motion_moment(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "ORDER granting 45 Motion to Dismiss or, in the Alternative, to Transfer Venue. "
        + "This case is TRANSFERRED to the Northern District of California.",
        "ORDER granting 45 Motion to Dismiss for Failure to State a Claim. "
        + "Counts I and II are dismissed. The motion is denied as to Count III.",
        "ORDER granting 45 Motion to Dismiss Counts I and II but denying it on Count III.",
        "ORDER granting 45 Motion to Dismiss filed by Smith. "
        + "Defendant Jones's 47 Motion to Dismiss is GRANTED with leave to amend.",
    ],
)
def test_a_later_limit_or_another_entry_in_the_ruling_run_is_triage(text: str) -> None:
    assert isinstance(resolve_motion(MTD, [MOTION, entry(60, text)]), Unresolved)


def test_a_motion_title_naming_failure_is_not_a_warning() -> None:
    text = (
        "ORDER granting 45 Motion to Dismiss for Failure to State a Claim, and Count I "
        + "shall be dismissed with prejudice. Plaintiff may file an amended complaint "
        + "within 21 days."
    )
    assert read_leave(text) is Leave.mixed


def test_a_later_sentence_on_some_counts_is_triage() -> None:
    for text in [
        "ORDER granting 45 Motion to Dismiss; denying 47 Motion to Strike. "
        + "The motion to dismiss is denied as to Count III.",
        "ORDER granting 45 Motion to Dismiss. Count III shall proceed to discovery.",
        "ORDER granting 45 Motion to Dismiss. Count III survives.",
        "ORDER granting 45 Motion to Dismiss. Plaintiff's negligence claim is not dismissed.",
    ]:
        assert isinstance(resolve_motion(MTD, [MOTION, entry(60, text)]), Unresolved), text


def test_a_closure_is_not_read_past_the_judge_signature() -> None:
    text = (
        "ORDER granting 50 Stipulation of Dismissal. Signed by Judge X on 2/1/2026. "
        + "Claims against Acme only. (ab)"
    )
    assert find_closure([entry(70, text)]) is None


@pytest.mark.parametrize(
    "text",
    [
        "STIPULATION of Dismissal with prejudice signed by Plaintiff and Defendant Acme Corp. only",
        "JOINT STIPULATION of Dismissal signed by counsel for Plaintiff and Defendant Beta LLC; "
        + "claims against Gamma Inc. remain",
    ],
)
def test_a_closure_signed_by_parties_is_not_read_past_the_signature(text: str) -> None:
    assert find_closure([entry(70, text)]) is None


@pytest.mark.parametrize(
    "later",
    [
        "MANDATE of USCA as to 82 Notice of Appeal: REVERSED and REMANDED for further proceedings",
        "ORDER granting 85 Motion to Reopen Case",
    ],
)
def test_a_judgment_reversed_or_reopened_is_triage(later: str) -> None:
    entries = [
        entry(80, "JUDGMENT in favor of Defendant against Plaintiff."),
        entry(90, later, day="2027-03-01"),
    ]
    assert isinstance(resolve_judgment(entries), Unresolved)


def test_a_liability_only_judgment_is_triage() -> None:
    text = "JUDGMENT in favor of Plaintiff on liability; damages to be determined at trial."
    assert isinstance(resolve_judgment([entry(80, text)]), Unresolved)


# --- preliminary injunctions, and the judge named before the ruling -----------

PI = MotionEvent(TrialMoment.preliminary_injunction, 12)


@pytest.mark.parametrize(
    ("text", "moment"),
    [
        ("MOTION for Preliminary Injunction filed by Author.", TrialMoment.preliminary_injunction),
        ("Emergency MOTION for a Preliminary Injunction", TrialMoment.preliminary_injunction),
        (
            "MOTION for Temporary Restraining Order and Preliminary Injunction",
            TrialMoment.preliminary_injunction,
        ),
        (
            "MOTION for Temporary Restraining Order, MOTION for Preliminary Injunction",
            TrialMoment.preliminary_injunction,
        ),
        ("MOTION for Temporary Restraining Order filed by Author.", None),
        ("MOTION for Leave to File Excess Pages for Motion for Preliminary Injunction", None),
        ("MOTION to Ascertain Status of Motion for Preliminary Injunction re 12", None),
    ],
)
def test_the_injunction_motion_kind(text: str, moment: TrialMoment | None) -> None:
    assert motion_moment(text) is moment


def test_an_injunction_ruling_reads_like_any_motion_ruling() -> None:
    motion = entry(12, "MOTION for Preliminary Injunction filed by Author.", day="2026-01-10")
    order = entry(
        40, "ORDER denying 12 Motion for Preliminary Injunction. Signed by Judge A. Bench."
    )
    resolved = resolve_motion(PI, [motion, order])
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    assert resolved.leave is None
    assert resolved.rule == "trial-resolver-v3"


COMBINED = entry(
    12,
    "Emergency MOTION for Temporary Restraining Order and Preliminary Injunction",
    day="2026-01-10",
)


@pytest.mark.parametrize(
    "text",
    [
        "ORDER granting 12 Motion for TRO and Preliminary Injunction. Signed by Judge A. Bench.",
        "ORDER granting in part 12 Motion for Temporary Restraining Order and Preliminary "
        + "Injunction. Signed by Judge A. Bench.",
        "ORDER granting 12 Emergency Motion. Defendants are temporarily restrained pending a "
        + "hearing set for 2/20/2026.",
        "ORDER by Judge A. Bench granting in part 12 Motion. Defendants are restrained from "
        + "deleting data until the hearing.",
    ],
)
def test_a_ruling_that_names_a_restraining_order_is_passed_over(text: str) -> None:
    assert resolve_motion(PI, [COMBINED, entry(20, text)]) is None


def test_a_ruling_on_a_combined_motion_that_names_neither_half_is_triage() -> None:
    resolved = resolve_motion(PI, [COMBINED, entry(20, "ORDER denying 12 Motion.")])
    assert isinstance(resolved, Unresolved)
    assert "neither half" in resolved.reason


def test_a_combined_motion_resolves_on_a_ruling_that_names_the_injunction_alone() -> None:
    order = entry(30, "ORDER denying 12 Motion for Preliminary Injunction.")
    restraining = entry(20, "ORDER granting 12 Motion for TRO.")
    resolved = resolve_motion(PI, [COMBINED, restraining, order])
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.denied
    assert resolved.cited.entry_number == 30


def test_a_restraining_order_ruling_on_another_motion_leaves_the_injunction_open() -> None:
    motion = entry(12, "MOTION for Preliminary Injunction filed by Author.", day="2026-01-10")
    other = entry(20, "ORDER denying 11 Motion for Temporary Restraining Order.")
    assert resolve_motion(PI, [motion, other]) is None


@pytest.mark.parametrize(
    ("text", "ruling"),
    [
        ("ORDER by Judge Rita F. Lin granting 45 Motion to Dismiss.", MotionRuling.granted),
        (
            "Order by Magistrate Judge A. B. Bench granting in part and denying in part 45 Motion "
            + "to Dismiss.",
            MotionRuling.granted_in_part,
        ),
        ("ORDER Signed by Judge A. Bench denying 45 Motion to Dismiss.", MotionRuling.denied),
    ],
)
def test_a_judge_named_before_the_ruling_verb_is_read_past(text: str, ruling: MotionRuling) -> None:
    assert read_docket_ruling(text, 45).ruling is ruling


@pytest.mark.parametrize(
    "text",
    [
        "ORDER by Judge A. Bench re 45 Motion to Dismiss. The parties shall confer on granting it.",
        "ORDER by Judge A. Bench setting hearing on 45 Motion to Dismiss; granting 44 Motion.",
        "NOTICE by Judge Grant granting 45 Motion to Dismiss",
        "ORDER by Judge Lin tentatively granting 45 Motion to Dismiss",
        "ORDER by Judge Lin not granting 45 Motion to Dismiss",
        "ORDER by Judge Lin re Proposed Order granting 45 Motion to Dismiss",
        "ORDER by Judge William Alsup vacating order granting 45 Motion to Dismiss",
        "ORDER by Judge Lin withdrawing order granting 45 Motion to Dismiss",
        "ORDER by Judge Lin staying order granting 45 Motion to Dismiss",
        "ORDER by Judge Lin reversing magistrate order granting 45 Motion to Dismiss",
        "ORDER by Judge Lin declining to adopt recommendation granting 45 Motion to Dismiss",
        "ORDER by Judge Lin setting hearing before granting 45 Motion to Dismiss",
        "ORDER by Judge Lin reconsidering order denying 45 Motion to Dismiss",
        "ORDER by Judge Lin on reconsideration of order denying 45 Motion to Dismiss",
        "ORDER BY JUDGE LIN VACATING ORDER GRANTING 45 MOTION TO DISMISS",
        "ORDER by Judge Lin Vacating Prior Order Granting 45 Motion to Dismiss",
    ],
)
def test_a_judge_s_name_does_not_make_a_reference_a_ruling(text: str) -> None:
    assert read_docket_ruling(text, 45).ruling is None


@pytest.mark.parametrize(
    "text",
    [
        "MOTION for Preliminary Injunction Pending Appeal filed by Author.",
        "MOTION for Preliminary Injunction Hearing Continuance",
        "MOTION for Summary Judgment Briefing Schedule",
        "MOTION for Summary Judgment Page Limit Extension",
        "MOTION for Class Certification Deadline Extension",
        "MOTION to Dismiss Party John Doe",
        "MOTION to Dismiss Appeal",
        "Joint MOTION to Dismiss with prejudice pursuant to settlement",
        "Joint MOTION to Dismiss voluntarily",
    ],
)
def test_a_motion_about_a_covered_motion_is_not_one(text: str) -> None:
    assert motion_moment(text) is None


# --- rulings that cite the motion after naming it ------------------------------

_FIRST_PERSON_ORDER = (
    "ORDER, I GRANT IN PART AND DENY IN PART Plaintiffs' motion for summary judgment on "
    + "infringement (D.I. 249 ). I DENY Defendant's motion for summary judgment on fair use "
    + "(D.I. 271 ). I GRANT Plaintiffs' Motion for Summary Judgment on Counterclaims (No. 1) "
    + "(D.I. [519). Because I am granting summary judgment on Motions 1 and 2, I DISMISS AS MOOT "
    + "Plaintiffs' Motion for Summary Judgment on Counterclaims (No. 3) Time (D.I. 523)."
)


@pytest.mark.parametrize(
    ("text", "number", "ruling"),
    [
        (_FIRST_PERSON_ORDER, 249, MotionRuling.granted_in_part),
        (_FIRST_PERSON_ORDER, 271, MotionRuling.denied),
        (_FIRST_PERSON_ORDER, 519, MotionRuling.granted),
        (_FIRST_PERSON_ORDER, 523, MotionRuling.mooted),
        (
            "ORDER GRANTING MOTION FOR PRELIMINARY INJUNCTION 6 . Signed by Judge A on 3/26/2026.",
            6,
            MotionRuling.granted,
        ),
        ("ORDER DENYING MOTION TO DISMISS 45.", 45, MotionRuling.denied),
        (
            "ORDER: Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED.",
            54,
            MotionRuling.granted,
        ),
        (
            "ORDER: Plaintiff's Motion for Class Certification (ECF No. 80) is DENIED. The parties "
            + "shall confer.",
            80,
            MotionRuling.denied,
        ),
    ],
)
def test_a_ruling_that_cites_the_motion_after_its_title_is_read(
    text: str, number: int, ruling: MotionRuling
) -> None:
    reading = read_docket_ruling(text, number)
    assert reading.ruling is ruling
    assert reading.conflict is None


@pytest.mark.parametrize(
    ("text", "number"),
    [
        (
            "ORDER GRANTING MOTION FOR LEAVE TO FILE AMICUS BRIEF AND GRANTING IN PART AND DENYING "
            + "IN PART MOTION TO DISMISS AND TO STRIKE 237 256 .",
            237,
        ),
        (
            "ORDER ON 166 215 CROSS MOTIONS FOR SUMMARY JUDGMENT; GRANTING 169 MOTION TO ADD "
            + "TO THE RECORD.",
            166,
        ),
        (
            "ORDER: Defendant's Motion to Dismiss or, in the Alternative, to Transfer Venue (Doc. "
            + "No. 54 ) is GRANTED IN PART and DENIED AS MOOT IN PART.",
            54,
        ),
        ("ORDER: Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED as to Count I.", 54),
        (
            "ORDER: I DENY Defendant's Motion for Reconsideration of the ruling on the Motion for "
            + "Summary Judgment (D.I. 249).",
            249,
        ),
        (
            "ORDER: I GRANT Plaintiff's Motion to Strike the summary judgment papers (D.I. 249).",
            249,
        ),
        ("ORDER: I GRANT Plaintiffs' Motion for Summary Judgment (D.I. 249) as to liability.", 249),
        (
            "ORDER: I GRANT Plaintiffs' Motion (D.I. 249). I DENY Plaintiffs' Motion (D.I. 249).",
            249,
        ),
        ("ORDER GRANTING MOTION TO DISMISS OR TRANSFER 45.", 45),
        ("ORDER GRANTING MOTION TO DISMISS 45 46.", 45),
    ],
)
def test_a_cited_ruling_the_rule_will_not_settle_is_triage(text: str, number: int) -> None:
    reading = read_docket_ruling(text, number)
    assert reading.ruling is None
    assert reading.conflict is not None


@pytest.mark.parametrize(
    ("text", "number"),
    [
        (_FIRST_PERSON_ORDER, 5),
        ("ORDER GRANTING MOTION FOR PRELIMINARY INJUNCTION 6 .", 7),
        ("ORDER: The hearing on the Motion to Dismiss (Doc. No. 54) is set for May 1.", 54),
        ("ORDER: I will hear argument on the Motion for Summary Judgment (D.I. 249).", 249),
        ("ORDER: i grant plaintiffs' motion (d.i. 249).", 249),
        ("ORDER extending time. The Motion to Dismiss (Doc. No. 54) is fully briefed.", 54),
    ],
)
def test_a_text_that_cites_the_motion_without_ruling_reads_nothing(text: str, number: int) -> None:
    reading = read_docket_ruling(text, number)
    assert reading.ruling is None
    assert reading.conflict is None


@pytest.mark.parametrize(
    ("text", "number"),
    [
        (
            "ORDER: I GRANT in part Plaintiffs' Motion for Summary Judgment (D.I. 249).",
            249,
        ),
        (
            "ORDER: I DENY as moot Plaintiffs' Motion for Summary Judgment (D.I. 249).",
            249,
        ),
        (
            "ORDER: I GRANT Plaintiffs' Motion for Summary Judgment as to liability (D.I. 2"
            + "49).",
            249,
        ),
        (
            "ORDER: I GRANT the portion of Plaintiffs' Motion for Summary Judgment concerni"
            + "ng infringement (D.I. 249).",
            249,
        ),
        (
            "ORDER: I DENY Defendant's Motion for Summary Judgment with respect to Count I "
            + "(D.I. 249).",
            249,
        ),
        (
            "ORDER: I GRANT Defendants' Motion to Dismiss in Part (D.I. 45).",
            45,
        ),
        (
            "ORDER: I GRANT Defendant's Motion to Dismiss or, in the alternative, to Transf"
            + "er (D.I. 45).",
            45,
        ),
        (
            "ORDER: I GRANT Defendant's Motion to Dismiss Count I, and otherwise reserve de"
            + "cision (D.I. 45).",
            45,
        ),
        (
            "ORDER: I GRANT Plaintiffs' Motion for Summary Judgment (D.I. 249). However, I "
            + "DENY it as to damages.",
            249,
        ),
        (
            "ORDER: I GRANT Plaintiffs' Motion for Summary Judgment (D.I. 249). Summary jud"
            + "gment is DENIED as to Count III.",
            249,
        ),
        (
            "ORDER: Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED. The claims agai"
            + "nst Beta are DISMISSED. In all other respects the motion is DENIED.",
            54,
        ),
        (
            "ORDER: Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED; however, Count "
            + "III survives.",
            54,
        ),
        (
            "ORDER: Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED. Counts I and II"
            + " are dismissed; Count III may proceed.",
            54,
        ),
        (
            "ORDER GRANTING MOTION TO DISMISS 45. THE MOTION IS DENIED AS TO COUNT III.",
            45,
        ),
        (
            "ORDER GRANTING MOTION TO DISMISS 45; DENYING MOTION TO DISMISS 45.",
            45,
        ),
        (
            "ORDER: Plaintiff's request to file excess pages in opposition to Defendant's M"
            + "otion for Summary Judgment (Doc. No. 88) is GRANTED.",
            88,
        ),
        (
            "ORDER: Plaintiff's request for oral argument on the Motion to Dismiss (Doc. No"
            + ". 54) is DENIED.",
            54,
        ),
        (
            "ORDER: The parties' stipulation regarding briefing on the Motion to Dismiss (D"
            + "oc. No. 54) is GRANTED.",
            54,
        ),
        (
            "ORDER: Plaintiff's objection to the Magistrate Judge's recommendation on the M"
            + "otion to Dismiss (Doc. No. 54) is DENIED.",
            54,
        ),
        (
            "ORDER: I GRANT Defendant's request to file a sur-reply to Plaintiffs' Motion f"
            + "or Summary Judgment (D.I. 249).",
            249,
        ),
        (
            "ORDER: I DENY the objections to the Report and Recommendation on the Motion to"
            + " Dismiss (D.I. 45).",
            45,
        ),
        (
            "ORDER: Plaintiff's Motion to Strike Defendant's Fed. R. Civ. P. 12(b)(6) Motio"
            + "n to Dismiss (Doc. No. 54) is GRANTED.",
            54,
        ),
        (
            "ORDER: Plaintiff's Motion for Extension of Time to respond to Defendant Acme, "
            + "Inc. 's Motion to Dismiss (Doc. No. 54) is GRANTED.",
            54,
        ),
        (
            "ORDER: Plaintiff's Motion for Reconsideration of the ruling on Acme Inc. and B"
            + "eta Corp. Motion to Dismiss (Doc. No. 54) is GRANTED.",
            54,
        ),
        (
            "ORDER: The Court does not agree that Defendant's Motion to Dismiss (Doc. No. 5"
            + "4) is GRANTED.",
            54,
        ),
        (
            "ORDER: If no opposition is filed by May 1, the Motion to Dismiss (Doc. No. 54)"
            + " is GRANTED.",
            54,
        ),
        (
            "ORDER: Unless Plaintiff files an amended complaint by June 1, Defendant's Moti"
            + "on to Dismiss (Doc. No. 54) is GRANTED.",
            54,
        ),
        (
            "ORDER: The Court is inclined to rule that Defendant's Motion to Dismiss (Doc. "
            + "No. 54) is GRANTED.",
            54,
        ),
        (
            "MINUTE ORDER: Tentative ruling: Defendant's Motion to Dismiss (Doc. No. 54) is"
            + " GRANTED.",
            54,
        ),
        (
            "ORDER TO SHOW CAUSE why Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED" + ".",
            54,
        ),
        (
            "ORDER granting 70 Motion for Reconsideration. The Court previously ruled that "
            + "Defendant's Motion to Dismiss (Doc. No. 54) is DENIED. On reconsideration the "
            + "motion is granted.",
            54,
        ),
        (
            "ORDER: The Magistrate Judge recommended that I GRANT Defendant's Motion to Dis"
            + "miss (D.I. 45). I decline to adopt that recommendation.",
            45,
        ),
        (
            "ORDER ADOPTING REPORT AND RECOMMENDATIONS: The Magistrate Judge recommended th"
            + "at Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED. The Court declines "
            + "to adopt it.",
            54,
        ),
        (
            "ORDER: Having reviewed the papers, I am not persuaded that I GRANT Plaintiffs'"
            + " Motion (D.I. 249).",
            249,
        ),
        (
            "ORDER GRANTING MOTION FOR JUDGMENT ON THE PLEADINGS UNDER RULE 12.",
            12,
        ),
        (
            "ORDER DENYING MOTION FOR SANCTIONS UNDER RULE 11.",
            11,
        ),
        (
            "ORDER GRANTING MOTION FOR SUMMARY JUDGMENT ON CLAIM 6.",
            6,
        ),
        (
            "ORDER GRANTING MOTION TO DISMISS IN CASE NO 45.",
            45,
        ),
        (
            "ORDER GRANTING MOTION TO EXPEDITE BRIEFING ON PRELIMINARY INJUNCTION 6.",
            6,
        ),
        (
            "ORDER: I DENY without prejudice Plaintiffs' Motion for Summary Judgment (D.I. "
            + "249).",
            249,
        ),
        (
            "ORDER DENYING WITHOUT PREJUDICE MOTION TO DISMISS 45.",
            45,
        ),
        (
            "ORDER: As to Count I GRANT the Motion to Dismiss (D.I. 45).",
            45,
        ),
        (
            "ORDER: Acme Corp. Motion to Dismiss (Doc. No. 54) is GRANTED.",
            54,
        ),
    ],
)
def test_a_cited_ruling_outside_its_plain_shape_is_never_read_as_one(
    text: str, number: int
) -> None:
    reading = read_docket_ruling(text, number)
    assert reading.ruling is None
    assert reading.conflict is not None


@pytest.mark.parametrize(
    ("text", "number"),
    [
        (
            "ORDER: The deadline to respond to the Motion to Dismiss (Doc. No. 54) is EXTEN"
            + "DED.",
            54,
        ),
        (
            "ORDER: Motion to Dismiss (Doc. No. 54) and Motion to Strike (Doc. No. 56) are "
            + "DENIED.",
            54,
        ),
        (
            "ORDER GRANTING MOTION TO DISMISS 45 IN PART.",
            45,
        ),
    ],
)
def test_a_citation_that_is_no_ruling_on_the_motion_reads_nothing(text: str, number: int) -> None:
    reading = read_docket_ruling(text, number)
    assert reading.ruling is None
    assert reading.conflict is None


def test_leave_is_read_from_a_cited_dismissal_that_stands_alone() -> None:
    text = (
        "ORDER: Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED. Plaintiff may file an "
        + "amended complaint within 21 days."
    )
    reading = read_docket_ruling(text, 54)
    assert reading.ruling is MotionRuling.granted
    assert reading.leave is Leave.with_leave


def test_a_cited_ruling_resolves_the_event_and_cites_its_entry() -> None:
    entries = [
        {
            "id": 1,
            "entry_number": 6,
            "date_filed": "2026-03-01",
            "description": "MOTION for Preliminary Injunction filed by Plaintiff.",
        },
        {
            "id": 2,
            "entry_number": 134,
            "date_filed": "2026-03-26",
            "description": "ORDER GRANTING MOTION FOR PRELIMINARY INJUNCTION 6 . Signed by A.",
        },
    ]
    resolved = resolve_motion(MotionEvent(TrialMoment.preliminary_injunction, 6), entries)
    assert isinstance(resolved, MotionResolution)
    assert resolved.ruling is MotionRuling.granted
    assert resolved.cited.entry_number == 134


_CITED_SJ = "ORDER: I GRANT Plaintiffs' Motion for Summary Judgment (D.I. 249). "


def test_a_ruling_on_a_motion_outside_the_stage_does_not_unsettle_the_cited_one() -> None:
    text = _CITED_SJ + "I GRANT IN PART Plaintiffs' Motion to Preclude Dr. Smith. I exclude a part."
    assert read_docket_ruling(text, 249).ruling is MotionRuling.granted


@pytest.mark.parametrize(
    "more",
    [
        "I DENY IN PART Plaintiffs' Motion for Summary Judgment on damages.",
        "I DENY Plaintiffs' Motion to Strike, and DENY summary judgment as to damages.",
    ],
)
def test_a_second_uncited_ruling_that_may_reach_the_motion_is_triage(more: str) -> None:
    reading = read_docket_ruling(_CITED_SJ + more, 249)
    assert reading.ruling is None
    assert reading.conflict is not None
