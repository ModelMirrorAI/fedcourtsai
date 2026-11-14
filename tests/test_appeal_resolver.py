"""The appeal stage's opener and resolver: what each form reads as, and what it declines."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.ai_watchlist import AiWatchlist
from fedcourtsai.cli import app
from fedcourtsai.pipeline import appeal_resolver as appeal
from fedcourtsai.pipeline.appeal_resolver import AppealOutcome, Disposition, Unresolved

TODAY = date(2026, 11, 11)


def entry(number: int, day: str, text: str) -> dict[str, Any]:
    return {"id": 1000 + number, "entry_number": number, "date_filed": day, "description": text}


@pytest.mark.parametrize(
    ("text", "outcome"),
    [
        ("JUDGMENT, Affirmed. Costs taxed against Appellant. (SB)", AppealOutcome.affirmed),
        ("JUDGMENT, Vacated and Remanded.", AppealOutcome.vacated),
        ("JUDGMENT, Affirmed in part, Reversed in part and Remanded.", AppealOutcome.mixed),
        (
            "OPINION (A, B, C) Because the plaintiff is unlikely to succeed, we VACATE the "
            + "preliminary injunction and REMAND. The motion to seal, Dkt. 28, is GRANTED. "
            + "FILED AND ENTERED JUDGMENT.",
            AppealOutcome.vacated,
        ),
        (
            "FILED MEMORANDUM DISPOSITION (A, B, C) AFFIRMED. FILED AND ENTERED JUDGMENT.",
            AppealOutcome.affirmed,
        ),
        ("MEMORANDUM (A, B, C) AFFIRMED IN PART; REVERSED IN PART; REMANDED.", AppealOutcome.mixed),
        (
            "PER CURIAM JUDGMENT [2194982] filed that the judgment of the District Court be "
            + "affirmed, for the reasons in the accompanying opinion.",
            AppealOutcome.affirmed,
        ),
        (
            "SUMMARY ORDER AND JUDGMENT, affirming the judgment of the district court, by "
            + "ABC, DEF, GHI, FILED.",
            AppealOutcome.affirmed,
        ),
        (
            "OPINION, reversing the judgment of the district court, by ABC, FILED.",
            AppealOutcome.reversed,
        ),
        (
            "ORDER FILED. The stipulated motion for voluntary dismissal is granted. This appeal "
            + "is dismissed. Fed. R. App. P. 42(b).",
            AppealOutcome.no_merits_decision,
        ),
        (
            "ORDER (Clerk) dismissing the appeal for lack of appellate jurisdiction.",
            AppealOutcome.dismissed,
        ),
        ("MEMORANDUM (A, B, C) DISMISSED as moot.", AppealOutcome.dismissed),
        (
            "PER CURIAM JUDGMENT filed that the judgment of the District Court be affirmed in "
            + "part and reversed in part.",
            AppealOutcome.mixed,
        ),
        (
            "ORDER FILED. Joint motion for voluntary dismissal is granted; appeal dismissed. All "
            + "pending motions are denied as moot.",
            AppealOutcome.no_merits_decision,
        ),
        # A result stated in prose as the entry's leading clause.
        (
            "OPINION, the District Court\u2019s order is affirmed, by ABC, DEF, GHI, FILED.",
            AppealOutcome.affirmed,
        ),
        (
            "OPINION, vacating the injunction and remanding for further proceedings consistent "
            + "with this opinion, by ABC, DEF, GHI, FILED.",
            AppealOutcome.vacated,
        ),
        (
            "SUMMARY ORDER AND JUDGMENT, we affirm the judgment of the district court, by ABC, "
            + "DEF, GHI, copy to pro se appellant, FILED.",
            AppealOutcome.affirmed,
        ),
        (
            "OPINION, affirming the district court\u2019s dismissal of the complaint, by ABC, DEF, "
            + "GHI, FILED.",
            AppealOutcome.affirmed,
        ),
        # A judgment on what the district court did, in the court's own possessive.
        (
            "PER CURIAM JUDGMENT [2174591] filed that the District Court's grant of summary "
            + "judgment to the agency and its denial of the plaintiff's cross-motion for summary "
            + "judgment be affirmed, for the reasons in the accompanying opinion . Before Judges: "
            + "A, B and C. [24-0001]",
            AppealOutcome.affirmed,
        ),
        (
            "PER CURIAM JUDGMENT [2188250] filed that the appeal be dismissed for lack of "
            + "jurisdiction and the case be remanded for further proceedings, for the reasons in "
            + "the accompanying opinion . Before Judges: A, B and C.",
            AppealOutcome.dismissed,
        ),
        # A separate writing named in the label leaves the panel's result the panel's.
        (
            "MEMORANDUM DISPOSITION WITH DISSENT (A, B, C) AFFIRMED. FILED AND ENTERED JUDGMENT.",
            AppealOutcome.affirmed,
        ),
        # The appellant ends the appeal, in each court's form.
        (
            "ORDER (Clerk) dismissing case pursuant to Fed. R. App. P. 42(b). (AB)",
            AppealOutcome.no_merits_decision,
        ),
        (
            "ORDER FILED. The motion (Docket Entry No. 13) for voluntary dismissal is granted. See "
            + "Fed. R. App. P. 42(b). This case is dismissed. This order serves as the mandate of "
            + "the court.",
            AppealOutcome.no_merits_decision,
        ),
        (
            "MOTION ORDER, denying motion to dismiss at docket entry 50, granting motion to "
            + "withdraw appeal at docket entry 53, on behalf of Appellant X, FILED.",
            AppealOutcome.no_merits_decision,
        ),
        (
            "MOTION ORDER, denying motion for leave to proceed in forma pauperis at docket entry "
            + "23, granting motion to withdraw appeal at docket entry 32, FILED.",
            AppealOutcome.no_merits_decision,
        ),
        ("FRAP 42 STIPULATION, with prejudice, FILED.", AppealOutcome.no_merits_decision),
        (
            "CLERK'S ORDER [2074123] filed considering motion to withdraw notice of appeal "
            + "[2072690-2]. It is ORDERED that this appeal be dismissed. The Clerk is directed to "
            + "issue the mandate forthwith to the district court.",
            AppealOutcome.no_merits_decision,
        ),
        (
            "PER CURIAM ORDER [2114842] filed granting motion for voluntarily dismissal "
            + "[2114321-2]. The Clerk is directed to issue the mandate forthwith.",
            AppealOutcome.no_merits_decision,
        ),
        (
            "CLERK'S ORDER [2100627] filed granting appellant's unopposed motion to dismiss case "
            + "[2100004-2], The Clerk is directed to issue the mandate forthwith.",
            AppealOutcome.no_merits_decision,
        ),
        (
            "PER CURIAM ORDER [2098535] filed granting motion for summary affirmance "
            + "[2083280-2]. The Clerk is directed to publish this order.",
            AppealOutcome.affirmed,
        ),
        (
            "PER CURIAM ORDER [1] filed ORDERED that the motion for summary affirmance "
            + "[2083280-2] be granted. Withholding issuance of the mandate.",
            AppealOutcome.affirmed,
        ),
        (
            "OPINION WITH DISSENT (A, B, C) REVERSED. FILED AND ENTERED JUDGMENT.",
            AppealOutcome.reversed,
        ),
    ],
)
def test_a_disposition_form_reads_as_its_outcome(text: str, outcome: AppealOutcome) -> None:
    assert appeal.read_disposition(text) is outcome


@pytest.mark.parametrize(
    "text",
    [
        "PRECEDENTIAL OPINION. Coram: A, B and C, Circuit Judges. Total Pages: 32.",
        "JUDGMENT, FILED.",
        "MANDATE ISSUED. The judgment of this Court, entered 8/4/2026, takes effect this date.",
        "DISTRICT COURT OPINION AND ORDER, dated 06/18/2025, RECEIVED.",
        "ORDER FILED. The motion (Docket Entry No. 14) to stay the district court's order is "
        + "granted.",
        "ORDER FILED. The motion to dismiss the cross-claim below is noted.",
        "CLERK'S ORDER filed vacating the court's order filed October 23, 2026.",
        "ECF FILER: Motion filed by Appellee to dismiss the appeal for lack of jurisdiction.",
        "OPINION (A, B, C) The district court dismissed the complaint and vacated its earlier "
        + "order. Opinion by Judge A.",
        "[VACATED PURSUANT TO ORDER FILED 11/03/2026] -- MEMORANDUM (A, B, C) AFFIRMED.",
        "JUDGMENT, Affirmed. [VACATED by order of 11/3/2026]",
        "OPINION WITHDRAWN. MEMORANDUM (A, B, C) AFFIRMED.",
        "ORDER FILED. Appellant is ordered to show cause within 21 days why this appeal should "
        + "not be dismissed for lack of jurisdiction.",
        "ORDER FILED. Within 21 days appellant shall move for voluntary dismissal of the "
        + "appeal or show cause why the appeal should not be dismissed.",
        "ORDER FILED. The motion to dismiss is denied without prejudice. Appellee's argument "
        + "that the appeal should be dismissed for lack of jurisdiction is referred to the "
        + "merits panel.",
        "ORDER filed denying motion to dismiss case for lack of jurisdiction; the question "
        + "whether the appeal must be dismissed as moot is deferred to the merits panel.",
        "ORDER, dismissing appeal by 05/01/2026 unless Appellant submits Form D, FILED.",
        "ORDER, dated 06/18/2025, by District Judge X, dismissing the case for lack of "
        + "jurisdiction, RECEIVED.",
        "OPINION AND ORDER of the district court, DISMISSING the complaint, RECEIVED.",
        "ORDER FILED. The district court dismissed the case as moot. Appellant's motion for an "
        + "injunction pending appeal is denied.",
        "MEMORANDUM IN SUPPORT OF MOTION TO DISMISS APPEAL FOR LACK OF JURISDICTION filed by "
        + "Appellee Y.",
        "MEMORANDUM in opposition to motion to DISMISS filed by Appellant.",
        "JUDGMENT of the Supreme Court of the United States, received. The judgment of this "
        + "court is VACATED and the case is REMANDED.",
        "ORDER FILED. Rehearing en banc is granted. The panel opinion is VACATED.",
        "ORDER FILED. The appeal in 25-1235 is dismissed pursuant to Fed. R. App. P. 42(b); the "
        + "appeal in 25-1234 remains pending.",
        "OPINION, dated 07/17/2026, The foregoing is hereby certified to the Court of Appeals of "
        + "the State, as ordered, by ABC, DEF, GHI, FILED",
        "FRAP 42 STIPULATION, With Prejudice, RECEIVED. Service date 11/25/2025 by ACMS.",
        "CERTIFIED COPY OF ORDER, dated 12/08/2025, determining the appeal, ISSUED.[Mandate]",
        "CLERK'S ORDER [2067177] filed to show cause regarding dismissing case for lack of "
        + "jurisdiction. Failure to respond shall result in dismissal of the case.",
        "CLERK'S ORDER [2089154] filed dismissing as moot appellant's unopposed motion to extend "
        + "time [2088723-2].",
        "CLERK'S ORDER [2100001] filed granting appellee's motion to dismiss case [2100000-2].",
        "PER CURIAM ORDER [2110890] filed ORDERED that this case be held in abeyance and that "
        + "consideration of the motion for summary affirmance [2081876-2] be deferred.",
        "CLERK'S ORDER [2112966] filed granting motion to extend time; directing response to "
        + "motion for summary affirmance [2107142-2] due on 05/16/2025.",
        "PER CURIAM ORDER [2159366] filed ORDERED that the motion to vacate and remand "
        + "[2143801-2] be denied.",
        "ORDER FILED. The motion (Docket Entry No. 13) to dismiss for failure to prosecute is "
        + "denied. The opening brief is due June 30, 2025.",
        # Words of a dismissal, a withdrawal or an affirmance the entry does not make.
        "PER CURIAM ORDER [2098535] filed ORDERED that the motion for summary affirmance "
        + "be denied and the motion to expedite be granted.",
        "PER CURIAM ORDER [1] filed ORDERED that the motion requesting that this appeal "
        + "be dismissed for lack of jurisdiction be denied.",
        "PER CURIAM ORDER [1] filed ORDERED that the motion to dismiss be denied. The "
        + "district court's order that the case be dismissed as moot is appealable.",
        "CLERK'S ORDER [1] filed ORDERED that the cross-claim in this case be dismissed "
        + "as moot.",
        "ORDER FILED. The district court case is dismissed as moot according to appellee;"
        + " the motion to stay is denied.",
        "ORDER FILED. The motion to dismiss is denied. Appellee argues the appeal is "
        + "untimely and that this case be dismissed as untimely; we disagree.",
        "MEMORANDUM (A, B, C) The district court ordered that the case be dismissed for "
        + "lack of jurisdiction. We disagree and remand.",
        "OPINION filed. The panel holds that the district court erred when it ordered "
        + "that the case be dismissed as moot.",
        "JUDGMENT, the mandamus petition in this case is dismissed as moot. The appeal is"
        + " submitted.",
        "MOTION ORDER, granting motion to withdraw appeal bond, FILED.",
        "MOTION ORDER, granting motion to withdraw as counsel, FILED.",
        "FRAP 42 STIPULATION, defective, FILED.",
        "ORDER filed denying appellee's motion for an order dismissing the appeal for "
        + "lack of jurisdiction.",
        "PER CURIAM ORDER [2098535] filed ORDERED that the federal appellees' motion for "
        + "summary affirmance be granted. The Clerk is directed to calendar this case for "
        + "the District of Columbia appellees.",
    ],
)
def test_an_entry_that_disposes_of_nothing_reads_as_none(text: str) -> None:
    assert appeal.read_disposition(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "PER CURIAM JUDGMENT [1] filed that the petitions for review be denied.",
        # A capital result qualified in lower case is not the whole.
        "JUDGMENT, REVERSE in part the District Court\u2019s judgment and REMAND. Costs shall not "
        + "be taxed. (AB)",
        "OPINION, we vacate the District Court's award of attorney's fees and remand, by ABC, "
        + "DEF, GHI, FILED.",
        "OPINION, we vacate the district court\u2019s judgment as to the first video, affirm the "
        + "district court\u2019s judgment as to the second, and remand, by ABC, DEF, GHI, FILED.",
        "PER CURIAM JUDGMENT [2168546] filed that the District Court's grant of summary judgment "
        + "be vacated in part and the case be remanded for further proceedings.",
        "PER CURIAM JUDGMENT [2182048] filed that the District Court's dismissal of the claims "
        + "for injunctive relief be reversed; the District Court\u2019s dismissal of the damages "
        + "claims be affirmed; and the case be remanded for further proceedings.",
        "PER CURIAM ORDER [2127932] filed ORDERED that the motion to remand the case [2114426-2] "
        + "be granted, and this case be remanded to the district court for further proceedings.",
        "PER CURIAM ORDER [2102536] filed ORDERED, on the court's own motion, that this appeal "
        + "be dismissed for lack of prosecution as to the appellants other than X. It is FURTHER "
        + "ORDERED that the motion for summary affirmance [2078683-2] be granted.",
        "ORDER FILED. Appellant did not file the opening brief by the due date. This appeal is "
        + "therefore dismissed. See 9th Cir. R. 42-1.",
        "MEMORANDUM (A, B, C) REVERSED and VACATED.",
        "MEMORANDUM (A, B, C) VACATED IN PART.",
        "ORDER FILED. This appeal is dismissed.",
        "ORDER FILED. Appeal dismissed for failure to prosecute. 9th Cir. R. 42-1.",
        "ORDER FILED. The parties' stipulated dismissal is noted; the appeal is dismissed as moot.",
        "ORDER FILED. Counsel's motion to withdraw is granted. The appeal is dismissed for "
        + "failure to prosecute. 9th Cir. R. 42-1.",
        "ORDER FILED. Appellant's untimely motion for an extension is denied. This appeal is "
        + "dismissed for failure to prosecute.",
        "ORDER FILED. The appeal is dismissed in part for lack of jurisdiction.",
        "ORDER FILED. Appellant X's appeal is dismissed for lack of jurisdiction; appellant "
        + "Y's appeal proceeds.",
        "ORDER FILED. The cross-appeal is voluntarily dismissed; the principal appeal proceeds.",
        "FILED PER CURIAM OPINION (A, B, C) The emergency motion for a stay pending appeal is "
        + "DENIED. The administrative stay entered on March 3 is VACATED.",
        "OPINION filed certifying question to state supreme court. Submission is VACATED.",
        "OPINION, DISSENTING, by Judge X, who would REVERSE, FILED.",
        "OPINION (A, B, C) (en banc) The panel opinion is VACATED. We AFFIRM.",
        "MEMORANDUM (A, B, C) Appellee's motion to DISMISS the appeal is DENIED. AFFIRMED.",
        "FILED MEMORANDUM DISPOSITION (A, B, C) AFFIRMED. Appellant's request that we VACATE "
        + "the award is not properly before us.",
        "FILED OPINION (A, B, C) REVERSED AND REMANDED. Judge A dissents and would AFFIRM.",
        "MEMORANDUM (A, B, C) AFFIRMED. The cross-appeal is DISMISSED as moot.",
        "JUDGMENT, Affirmed; cross-appeal dismissed as moot.",
        "JUDGMENT. Affirmed as to appeal 25-1; dismissed as to 25-2.",
        "MEMORANDUM (A, B, C) We AFFIRM the denial of attorney's fees.",
        # Less than the whole appeal, a second result, or an end that may be undone.
        "PER CURIAM ORDER [1] filed ORDERED that the motion for summary affirmance be "
        + "granted with respect to the federal appellees.",
        "PER CURIAM ORDER [1] filed granting motion for summary affirmance [2083280-2] "
        + "with respect to the dismissal of the claims against the federal defendants; "
        + "denying motion for summary affirmance [2083281-2].",
        "PER CURIAM JUDGMENT [1] filed that the appeal be dismissed as moot and the "
        + "district court's judgment be vacated, for the reasons in the accompanying "
        + "opinion.",
        "JUDGMENT. The appeal is dismissed as moot. The judgment of the district court is"
        + " vacated and the case remanded.",
        "CLERK'S ORDER [1] filed dismissing case 24-5002 pursuant to FRAP 42(b). "
        + "[24-5001, 24-5002]",
        "ORDER (Clerk) dismissing case No. 24-1235 only pursuant to Fed. R. App. P. "
        + "42(b). (AB)",
        "CLERK'S ORDER [1] filed granting motion for voluntary dismissal of No. 24-5002 "
        + "[2]. [24-5001, 24-5002]",
        "CLERK'S ORDER [1] filed granting appellant's motion to dismiss case No. 24-5002 "
        + "[2]. [24-5001, 24-5002]",
        "CLERK'S ORDER [1] filed granting joint motion for voluntary dismissal of "
        + "appellee Acme Corp. [2]; the case continues against the other appellees.",
        "CLERK'S ORDER [1] filed granting motion to voluntarily dismiss appellant John "
        + "Doe from this case [2].",
        "MOTION ORDER, granting motion to withdraw appeal at docket entry 53, on behalf "
        + "of Appellant X only; the appeal of Appellant Z will continue, FILED.",
        "FRAP 42 STIPULATION, withdrawing appeal as to Appellee Y only, with prejudice, "
        + "FILED.",
        "FRAP 42 STIPULATION, of cross-appeal 25-123, with prejudice, FILED.",
        "FRAP 42 STIPULATION, with prejudice, on behalf of Cross-Appellant X, FILED.",
        "FRAP 42 STIPULATION, with prejudice, in 25-1235 only, FILED.",
        "FRAP 42 STIPULATION, without prejudice to reinstatement by 03/01/2026, FILED.",
        "OPINION, we affirm the district court's judgment insofar as it rejected the "
        + "contract claim and dismiss the remainder of the appeal for lack of jurisdiction,"
        + " by ABC, DEF, GHI, FILED.",
        "OPINION, affirming the denial of the preliminary injunction and dismissing the "
        + "appeal from the scheduling order, by ABC, DEF, GHI, FILED.",
        "OPINION, the district court's order is reversed insofar as it denied qualified "
        + "immunity to Officer A; the appeal of Officer B is dismissed, by ABC, FILED.",
        "OPINION, we affirm the judgment with respect to counts one and two and remand "
        + "for further proceedings on count three, by ABC, DEF, GHI, FILED.",
        "OPINION, we affirm the district court's judgment in No. 24-100 and reserve "
        + "decision in No. 24-200, by ABC, FILED.",
        "SUMMARY ORDER AND JUDGMENT, affirming the judgment of the district court except "
        + "to the extent it awarded prejudgment interest, which is modified, by ABC, FILED.",
        "OPINION, vacating the panel's earlier stay and denying the motion, by ABC, " + "FILED.",
        "OPINION, affirming the district court's order vacating the award, by ABC, FILED.",
        "PER CURIAM JUDGMENT [1] filed that the judgment of the District Court be "
        + "affirmed; and that the remainder of the appeal be dismissed for lack of "
        + "jurisdiction.",
        "MOTION ORDER, granting motion to withdraw appeal without prejudice to "
        + "reinstatement by 03/01/2026, FILED.",
        "CLERK'S ORDER [1] filed granting motion to voluntarily dismiss petition for "
        + "review [2].",
        "ORDER FILED granting appellee's unopposed motion to remand.",
        "MEMORANDUM DISPOSITION WITH DISSENT (A, B, C) AFFIRMED. Judge C would REVERSE.",
        "MEMORANDUM DISPOSITION WITH DISSENT AFFIRMED.",
    ],
)
def test_a_disposition_the_rule_will_not_settle_is_a_reason(text: str) -> None:
    assert isinstance(appeal.read_disposition(text), str)


@pytest.mark.parametrize(
    "text",
    [
        "REPLY BRIEF, on behalf of Appellant X, FILED. Service date 12/08/2025 by ACMS.",
        "ECF FILER: REDACTED ELECTRONIC REPLY BRIEF on behalf of Appellant X.",
        "REPLY BRIEF submitted for filing by Appellant X.",
        "PETITIONER REPLY BRIEF [2173124] filed by X Corp [Service Date: 05/13/2026 ]",
        "Submitted (ECF) Reply Brief for review. Submitted by Appellant X.",
    ],
)
def test_the_appellants_filed_reply_is_read(text: str) -> None:
    assert appeal.is_reply_brief(text)


@pytest.mark.parametrize(
    "text",
    [
        "Appellant's Reply Brief due 04/20/2026.",
        "REPLY BRIEF DUE 04/20/2026.",
        "Reply brief due 21 days after service of answering brief.",
        "Appellant's reply brief extension granted to 5/1.",
        "REPLY BRIEF NOT FILED; time expired.",
        "Reply brief deficiency notice sent to Appellant.",
        "Reply Brief stricken by clerk order.",
        "[STRICKEN] REPLY BRIEF on behalf of Appellant X.",
        "REPLY BRIEF in support of motion for stay pending appeal filed by Appellant.",
        "REPLY BRIEF, on behalf of Appellee Y, FILED.",
        "REPLY BRIEF, on behalf of Amicus Curiae Z, FILED.",
        "PETITIONER SUPPLEMENTAL REPLY BRIEF [1] filed by X Corp",
        "HARD COPY RECEIVED from Appellant X - SEALED Reply Brief. Copies: 7.",
        "ECF FILER: Motion filed by Appellant X to seal Reply Brief.",
        "CLERK ACTION: Reply Brief submitted at DE 56 by Appellant X is filed.",
    ],
)
def test_an_entry_about_a_reply_is_not_the_reply(text: str) -> None:
    assert not appeal.is_reply_brief(text)


def docket() -> list[dict[str, Any]]:
    return [
        entry(1, "2026-01-05", "CIVIL CASE DOCKETED."),
        entry(10, "2026-03-01", "BRIEF, on behalf of Appellant X, FILED."),
        entry(20, "2026-04-01", "BRIEF, on behalf of Appellee Y, FILED."),
        entry(29, "2026-04-10", "ECF FILER: Motion filed by Appellant X to seal Reply Brief."),
        entry(28, "2026-04-12", "Appellant's Reply Brief due 04/20/2026."),
        entry(30, "2026-04-20", "ECF FILER: SEALED PROOF REPLY BRIEF on behalf of Appellant X."),
        entry(40, "2026-09-29", "JUDGMENT, Affirmed. Costs taxed against Appellant."),
        entry(41, "2026-09-30", "PRECEDENTIAL OPINION. Coram: A, B and C. Total Pages: 32."),
    ]


def test_the_event_opens_on_the_reply_brief_and_resolves_on_the_judgment() -> None:
    opening = appeal.read_appeal(docket(), today=TODAY)
    assert opening.is_event
    assert opening.opens_on == date(2026, 4, 20)
    assert opening.reply is not None and opening.reply.entry_number == 30
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.affirmed
    assert opening.resolution.cited.entry_number == 40


def test_a_reading_as_of_a_past_day_sees_no_later_entry() -> None:
    opening = appeal.read_appeal(docket(), today=date(2026, 5, 1))
    assert opening.is_event and opening.resolution is None
    before = appeal.read_appeal(docket(), today=date(2026, 4, 15))
    assert before.opens_on is None
    assert before.waiting_on == "the appellant's reply brief"


def test_an_appeal_disposed_of_before_its_reply_opens_nothing() -> None:
    entries = [
        entry(1, "2026-01-05", "CIVIL CASE DOCKETED."),
        entry(5, "2026-02-01", "ORDER (Clerk) dismissing the appeal pursuant to FRAP 42(b)."),
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert opening.ruled_first and not opening.is_event and opening.waiting_on is None
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.no_merits_decision


def test_a_cross_appeal_opens_nothing() -> None:
    entries = [*docket()[:5], entry(6, "2026-01-20", "CROSS-APPEAL docketed as 26-1001.")]
    opening = appeal.read_appeal(entries, today=date(2026, 5, 1))
    assert opening.opens_on is None
    assert opening.waiting_on is not None and "cross-appeal" in opening.waiting_on


def test_an_unread_judgment_goes_to_triage_and_cites_its_entry() -> None:
    entries = [*docket()[:6], entry(40, "2026-09-25", "MEMORANDUM (A, B, C) REVERSED and VACATED.")]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert isinstance(opening.resolution, Unresolved)
    assert [c.entry_number for c in opening.resolution.candidates] == [40]


def test_a_later_readable_judgment_wins_over_an_earlier_unread_one() -> None:
    entries = [
        *docket()[:6],
        entry(39, "2026-09-25", "ORDER FILED. This appeal is dismissed."),
        entry(40, "2026-09-29", "JUDGMENT, Affirmed."),
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.affirmed
    assert opening.resolution.cited.entry_number == 40


def test_an_order_to_show_cause_does_not_hide_the_judgment() -> None:
    entries = [
        entry(
            3,
            "2026-01-10",
            "ORDER FILED. Appellant is ordered to show cause why this appeal "
            + "should not be dismissed for lack of jurisdiction.",
        ),
        *docket()[1:6],
        entry(40, "2026-09-29", "JUDGMENT, Reversed."),
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert opening.is_event
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.reversed


def test_an_unread_entry_before_the_reply_does_not_close_the_event() -> None:
    entries = [
        entry(3, "2026-01-10", "ORDER FILED. This appeal is dismissed."),
        *docket()[1:6],
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert opening.is_event and not opening.ruled_first
    assert isinstance(opening.resolution, Unresolved)


def _watchlist() -> AiWatchlist:
    return AiWatchlist.model_validate(
        {
            "categories": {"copyright": "Training on works."},
            "cases": [
                {
                    "name": "A v. B",
                    "court": "cand",
                    "docket_id": 1,
                    "docket_number": "3:25-cv-00001",
                    "category": "copyright",
                    "why": "Training.",
                    "developers": ["Developer"],
                    "added": "2026-10-30",
                    "related": [
                        {
                            "court": "ca9",
                            "docket_id": 2,
                            "docket_number": "26-1",
                            "relation": "appeal",
                        },
                        {
                            "court": "ca9",
                            "docket_id": 3,
                            "docket_number": "26-2",
                            "relation": "appeal",
                        },
                        {
                            "court": "cadc",
                            "docket_id": 4,
                            "docket_number": "26-3",
                            "relation": "companion",
                        },
                    ],
                }
            ],
        }
    )


def test_the_survey_reads_listed_appeals_only_and_counts_them() -> None:
    watchlist = _watchlist()
    stored = {"ca9/2": docket()}
    result = appeal.survey(watchlist, stored.get, today=TODAY)
    assert [row.docket for row in result.appeals] == ["ca9/2", "ca9/3"]
    assert result.counts() == {
        "listed": 2,
        "stored": 1,
        "events": 1,
        "ruled_first": 0,
        "waiting": 0,
        "events_resolved": 1,
        "events_triage": 0,
        "events_open": 0,
    }
    assert len(appeal.summary_lines(result)) == 3


def test_appeal_events_command_surveys_the_stored_appeals(
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
        corpus.upsert_snapshot(conn, "ca9/2", date(2026, 11, 1), {"docket_entries": docket()})
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")

    result = CliRunner().invoke(app, ["appeal-events", "--today", "2026-11-11"])

    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["counts"]["events_resolved"] == 1
    assert [row["stored"] for row in report["appeals"]] == [True, False]
    assert report["appeals"][0]["outcome"] == "affirmed"
    assert "appeal-events (appeal-resolver-v2" in result.stderr
