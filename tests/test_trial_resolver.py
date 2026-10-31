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
    resolved = resolve_motion(MTD, [MOTION, entry(60, text)])
    assert isinstance(resolved, MotionResolution)
    assert resolved.leave is Leave.mixed


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
