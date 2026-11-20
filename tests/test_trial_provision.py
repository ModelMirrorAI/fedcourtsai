"""Provisioning a forward cell on a district docket's trial event.

The gates a trial event is held to (the day the docket was last read, the
trial resolver's reading of the snapshot, the record) and the context a
lower-court docket's cell is written.
"""

from __future__ import annotations

import json
import time
from datetime import date, timedelta
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cell_context
from fedcourtsai.pipeline.outcome import forward_leakage, trial_leakage
from fedcourtsai.store import forward_refusal_reason_from_parts
from tests.conftest import FixtureCorpus

runner = CliRunner()

CASE = "cand/100"
DISMISSAL = "evt-motion-trial-dismissal-45"
JUDGMENT = "evt-order-trial-judgment"
#: The day the docket last moved: long before any staleness bound.
MOVED = date(2026, 1, 31)


def entry(number: int, description: str, day: str) -> dict[str, Any]:
    return {
        "id": 1000 + number,
        "entry_number": number,
        "date_filed": day,
        "description": description,
        "recap_documents": [],
    }


BRIEFED = [
    entry(45, "MOTION to Dismiss filed by Developer, Inc.", "2026-01-10"),
    entry(
        52, "OPPOSITION/RESPONSE (re 45 MOTION to Dismiss ) filed byListed Author.", "2026-01-24"
    ),
    entry(58, "REPLY (re 45 MOTION to Dismiss ) filed byDeveloper, Inc.", "2026-01-31"),
]
GRANTED = entry(70, "ORDER by Judge A. Bench granting 45 Motion to Dismiss.", "2026-07-20")
FINAL = entry(90, "JUDGMENT in favor of Defendants against Plaintiffs", "2026-08-01")
CITED = entry(71, "MEMORANDUM OPINION re 45 Motion to Dismiss.", "2026-07-21")


def payload(*entries: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": 100,
        "docket_number": "3:26-cv-00100",
        "case_name": "Listed v. Developer",
        "docket_entries": list(entries),
    }


def row(**fields: Any) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=CASE,
        court="cand",
        docket_number="3:26-cv-00100",
        case_name="Listed v. Developer",
        **fields,
    )


def seed(fixture: FixtureCorpus, *entries: dict[str, Any], read_on: date | None) -> None:
    with corpus.connect(fixture.db_path) as conn:
        corpus.upsert_rows(conn, [row(last_pulled=read_on)])
        corpus.upsert_snapshot(conn, CASE, MOVED, payload(*entries))


def provision(event: str, *extra: str) -> Any:
    return runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "cand",
            "--docket",
            "100",
            "--event",
            event,
            "--refuse-terminal",
            "--max-snapshot-age-days",
            "10",
            *extra,
        ],
    )


# --- the snapshot's own reading -------------------------------------------------


def test_an_open_motion_and_an_open_action_disclose_nothing() -> None:
    assert trial_leakage(payload(*BRIEFED), DISMISSAL) is None
    assert trial_leakage(payload(*BRIEFED), JUDGMENT) is None
    assert forward_leakage(payload(*BRIEFED), "cand", DISMISSAL) is None


def test_a_ruling_discloses_its_own_motion_and_names_the_entry_alone() -> None:
    reason = forward_leakage(payload(*BRIEFED, GRANTED), "cand", DISMISSAL)

    assert reason == f"snapshot docket entry 70 resolves {DISMISSAL}"
    assert trial_leakage(payload(*BRIEFED, GRANTED), DISMISSAL) == reason
    # The ruling on one motion is not the action's final disposition.
    assert forward_leakage(payload(*BRIEFED, GRANTED), "cand", JUDGMENT) is None


def test_a_final_judgment_discloses_the_judgment_event() -> None:
    reason = forward_leakage(payload(*BRIEFED, FINAL), "cand", JUDGMENT)

    assert reason == f"snapshot docket entry 90 resolves {JUDGMENT}"


def test_a_reading_the_rule_cannot_settle_refuses_too() -> None:
    reason = forward_leakage(payload(*BRIEFED, CITED), "cand", DISMISSAL)

    assert reason is not None
    assert "without a ruling the rule can read" in reason
    assert "71" in reason
    assert "MEMORANDUM" not in reason


def test_the_courts_terminal_scan_is_not_asked_of_a_trial_event() -> None:
    # A phrase the cert scan reads as a disposition, on an entry that rules on
    # another motion: nothing about motion 45.
    other = entry(60, "ORDER: Motion for leave to file 59 is DENIED.", "2026-02-10")

    assert forward_leakage(payload(*BRIEFED, other), "cand", DISMISSAL) is None


# --- the wider net a motion is held to ------------------------------------------

# Forms of a ruling, or of the action ending, that the resolver's exact reading
# passes over. Each must refuse the motion's cell.
SIGNS = [
    "ORDER: Defendants' motion to dismiss is GRANTED.",
    "ORDER re 45: the motion is DENIED.",
    "ORDER granting in part and denying in part OAI's motion to dismiss",
    "ORDER granting OpenAI, Inc.'s Motion to Dismiss.",
    "ORDER denying Defendants Microsoft Corporation and OpenAI OpCo LLC's Motion to Dismiss",
    "ORDER granting in part (51) Motion to Dismiss; denying (45) Motion to Dismiss in 1:23-cv-1",
    "Judge A: ELECTRONIC ORDER entered denying 45 Motion to Dismiss.",
    "MINUTES (IN CHAMBERS) ORDER GRANTING DEFENDANT'S MOTION TO DISMISS [45] by Judge A.",
    "MEMO ENDORSEMENT on re: 45 MOTION to Dismiss. ENDORSEMENT: Application DENIED. SO ORDERED.",
    "Motions terminated: 45 MOTION to Dismiss.",
    "NOTICE by Developer of withdrawal of its motion to dismiss",
    "Minute Entry: Motion Hearing held re 45 MOTION to Dismiss. Motion DENIED on the record.",
    "ORDER denying 45. Answer deadline is 14 days from this order.",
    "ORDER: [45] is GRANTED; the hearing set for 7/1/2026 is VACATED.",
    "ORDER: The motion at ECF No. 45 is denied. Defendant shall appear on 7/1.",
    "ORDER granting 45.",
    "ORAL ORDER: the motion (D.I. 45) is DENIED.",
    "ORDER: For the reasons stated in the accompanying opinion, Defendant's motion is DENIED.",
    "ORDER re 45 MOTION to Dismiss. Signed by Judge A on 6/10/26.",
    "ORDER on Motion to Dismiss for Failure to State a Claim. Signed by Judge A.",
    "MEMORANDUM OPINION. Signed by Judge A.",
    "ORDER ADOPTING 58 Report and Recommendation in its entirety.",
    "MEMORANDUM AND ORDER: The motion to dismiss is ALLOWED.",
    "ORDER sustaining in part and overruling in part Defendant's Motion to Dismiss 45.",
    "ORDER STRIKING 45 Motion to Dismiss for failure to comply with Local Rule 7.",
    "ORDER dismissing Counts II and III of the Amended Complaint.",
    "ORDER: The Amended Complaint is DISMISSED with leave to amend.",
    "SECOND AMENDED COMPLAINT against Developer, Inc., filed by Listed Author.",
    "NOTICE of Voluntary Dismissal by Listed Author as to Developer, Inc.",
    "JUDGMENT in favor of Developer, Inc. against Plaintiff.",
    "Civil Case Terminated.",
    "ORDER: The motion is granted. This case is closed.",
    "ORDER: The Clerk is directed to close this case.",
    "ORDER DISMISSING CASE. Signed by Judge A.",
    "ORDER TRANSFERRING CASE to the Southern District of New York.",
    "STIPULATION of Dismissal with prejudice by all parties",
    # A ruling beside something procedural the same order does.
    "ORDER DENYING DEFENDANT'S MOTION TO DISMISS AND SETTING CASE MANAGEMENT CONFERENCE",
    "ORDER GRANTING MOTION TO DISMISS AND VACATING HEARING",
    "ORDER: The hearing on the motion to dismiss is vacated and the motion is DENIED.",
    "ORDER vacating hearing and denying motion. Signed by Judge A.",
    "Minute Entry: Hearing held re 45 MOTION to Dismiss. Taken under advisement; ruling: DENIED.",
    # A ruling on the motion joined to one on a neighbouring entry.
    "ORDER denying 58 and 45",
    "ORDER granting [58] and [45]",
    "ORDER denying 58 Motion to Strike & 45 Motion to Dismiss",
    "ORDER denying 58 Motion to Strike, granting Motion to Dismiss",
    "ORDER granting 58 Motion to Compel and the Court finds the Motion to Dismiss should be DENIED",
    # A number that is no docket entry beside the ruling.
    "ORDER: The motion is DENIED. Signed by Judge A on June 10, 2026.",
    "MEMORANDUM OPINION AND ORDER. Signed by Judge A on 6/10/2026. (Courtroom 4)",
    "OPINION AND ORDER (25 pages). Signed by Judge A.",
    "OPINION. Civil Action No. 25-1234. Signed by Judge A.",
    "ORDER: The complaint is dismissed without prejudice.",
    "ORDER resolving 45 Motion to Dismiss. See attached order.",
    "RULING on Defendant's Motion to Dismiss. Signed by Judge A.",
    "ORDER OF DISCONTINUANCE. Signed by Judge A.",
    "Notice of Settlement by Plaintiff.",
    "ORDER: Upon the parties' joint request, the Clerk is directed to close this case.",
    # The motion's number cited by "No.", or in a list before the ruling.
    "ORDER: ECF No. 45 is DENIED.",
    "ORDER: Dkt. No. 45 DENIED.",
    "ORDER: [45] and [49] are DENIED.",
    "ORDER: Defendants' motions (Dkts. 45, 46 & 48) are GRANTED.",
    "ORDER: ECF Nos. 45, 47: DENIED.",
    "MEMORANDUM & ORDER. (Ordered by Judge A on 6/10/2026)",
    "ORDER: The Court declines to dismiss the complaint.",
]

# What a docket carries while the motion is pending. None may refuse it.
PENDING = [
    "ORDER setting hearing on 45 Motion to Dismiss for 3/1/2026.",
    "ORDER granting 59 Motion for Extension of Time re 45 Motion.",
    "ORDER granting 59 Stipulation re briefing on 45 Motion to Dismiss.",
    "ORDER granting 59 Motion for Summary Judgment page limits.",
    "ORDER granting 59 Motion to Strike Opposition to Motion to Dismiss",
    "ORDER: the Court GRANTS three more pages for the motion to dismiss",
    "ORDER: Exhibit 3 stays sealed until 90 days after this case is closed.",
    "NOTICE by Listed Author re 45 Motion to Dismiss: it should be denied",
    "ORDER of USCA denying petition as to 45 Motion to Dismiss",
    "ORDER taking under submission 45 Motion to Dismiss. The hearing is vacated.",
    "Minute Entry: Motion Hearing held re 45 MOTION to Dismiss. Motion taken under advisement.",
    "ORDER denying 58 Motion to Stay Discovery pending ruling on 45 Motion to Dismiss.",
    "ORDER denying 58 Motion to Dismiss counterclaims filed by Plaintiff.",
    "ORDER granting 58 Motion to Withdraw as Attorney. Attorney C terminated.",
    "ORDER: The parties shall submit supplemental briefs on 45 by 7/1/2026.",
    "ORDER REASSIGNING CASE. Case reassigned to Judge B for all further proceedings.",
    "STANDING ORDER regarding civil cases. Motions will be denied if not in compliance.",
    "ORDER TO SHOW CAUSE why the case should not be dismissed for failure to prosecute.",
    "ORDER: If no amended complaint is filed in 45 days, the Clerk shall close the case.",
    "The Court granted 46 Other's motion to dismiss. As to 45, the parties shall confer.",
    "ORDER: Plaintiff shall show cause why this action should not be dismissed.",
    "INITIAL STANDING ORDER: failure to comply may result in the case being dismissed.",
    "ORDER: Motion to Ascertain Status 58 is GRANTED, and Motion for Oral Argument 59 is DENIED.",
    "ORDER GRANTING DEVELOPER'S MOTION PURSUANT TO CIVIL L.R. 7-11 TO SEAL ITS REPLY.",
    "ORDER: Other's motion (ECF No. 59 in 5:26-cv-00880) is DENIED, and the hearing is VACATED.",
    "ORDER denying letter motion. The Clerk is directed to close Case No. 24-CV-3285, ECF 58.",
    "ORDER granting 58 Motion for Extension of Time to respond to 45 Motion to Dismiss",
    # A ruling on another motion that carries no number.
    "ORDER: Plaintiff's motion to remand is denied.",
    "ORDER denying Motion to Strike.",
    "SCHEDULING ORDER: Any motion to dismiss not timely filed will be denied.",
    # A ruling on something the motion's name hangs from.
    "ORDER: The motion for extension of time to respond to the motion to dismiss is GRANTED.",
    "ORDER: Oral argument on the motion to dismiss is denied as unnecessary.",
    "ORDER: The request to file an oversized opposition to the motion to dismiss is granted.",
    "ORDER: Request granted. Defendants' motion to dismiss is due 4/1/2026.",
    # A warning of what may follow.
    "ORDER TO SHOW CAUSE why the motion to dismiss should not be granted as unopposed.",
    "ORDER: Failure to respond may result in the motion being granted as unopposed.",
    # A referral.
    "ORDER: 45 MOTION to Dismiss referred to Magistrate Judge E for report and recommendation.",
    "ORDER REFERRING CASE to Magistrate Judge K for recommendations on dispositive motions.",
    # The action ended for one party alone, or not ended.
    "ORDER: The Clerk shall not close the case.",
    "ORDER: No judgment shall be entered until all claims are resolved.",
]


@pytest.mark.parametrize(
    "unit",
    ["granted and denied in part and adopt 58 certify ", "grant deny ", "adopt ", "[45], "],
)
def test_the_net_reads_a_long_entry_in_bounded_time(unit: str) -> None:
    """A docket text is not bounded in length; the net's reading of one is."""
    longest = "ORDER " + unit * (50_000 // len(unit))
    held = payload(*BRIEFED, entry(60, longest, "2026-02-10"))

    began = time.perf_counter()
    forward_leakage(held, "cand", DISMISSAL)

    assert time.perf_counter() - began < 2


@pytest.mark.parametrize("text", SIGNS)
def test_a_sign_the_resolver_passes_over_refuses_the_motion(text: str) -> None:
    reason = forward_leakage(payload(*BRIEFED, entry(70, text, "2026-07-20")), "cand", DISMISSAL)

    assert reason is not None
    assert text[:24] not in reason


@pytest.mark.parametrize("text", PENDING)
def test_an_entry_about_the_pending_motion_is_no_sign(text: str) -> None:
    held = payload(*BRIEFED, entry(60, text, "2026-02-10"))

    assert forward_leakage(held, "cand", DISMISSAL) is None


@pytest.mark.parametrize(
    ("moment_id", "motion", "text"),
    [
        (
            "evt-motion-trial-summary-judgment-45",
            "MOTION for Summary Judgment",
            "ORDER granting summary judgment for defendant on all claims.",
        ),
        (
            "evt-motion-trial-preliminary-injunction-45",
            "MOTION for Preliminary Injunction",
            "PRELIMINARY INJUNCTION. Signed by Judge A.",
        ),
        (
            "evt-motion-trial-preliminary-injunction-45",
            "MOTION for Preliminary Injunction",
            "ORDER: Plaintiffs' application for preliminary injunctive relief is denied.",
        ),
        (
            "evt-motion-trial-class-45",
            "MOTION to Certify Class",
            "ORDER denying Plaintiffs' Renewed Motion for Class Certification and Appointment "
            + "of Class Counsel.",
        ),
    ],
)
def test_the_net_reads_each_kind_of_motion(moment_id: str, motion: str, text: str) -> None:
    filed = entry(45, f"{motion} filed by a party.", "2026-01-10")

    assert forward_leakage(payload(filed), "cand", moment_id) is None
    assert forward_leakage(payload(filed, entry(70, text, "2026-07-20")), "cand", moment_id)


def test_an_unnumbered_ruling_names_no_entry() -> None:
    minute = {
        **entry(0, "MINUTE ORDER granting Motion to Dismiss.", "2026-07-20"),
        "entry_number": None,
    }

    reason = forward_leakage(payload(*BRIEFED, minute), "cand", DISMISSAL)

    assert reason == f"snapshot an unnumbered docket entry may dispose of {DISMISSAL}"


def test_an_action_that_may_be_over_refuses_the_judgment_event() -> None:
    closed = entry(80, "Civil Case Terminated.", "2026-07-01")

    reason = forward_leakage(payload(*BRIEFED, closed), "cand", JUDGMENT)

    assert reason == f"snapshot docket entry 80 may show the action over, for {JUDGMENT}"


def test_a_snapshot_without_the_motions_entry_refuses_it() -> None:
    reason = forward_leakage(payload(*BRIEFED[1:]), "cand", DISMISSAL)

    assert reason == f"snapshot does not carry docket entry 45, the motion {DISMISSAL} names"
    assert forward_leakage({}, "cand", DISMISSAL) == reason
    # The judgment event names no entry, and an empty docket shows no judgment.
    assert forward_leakage({}, "cand", JUDGMENT) is None


# --- the record gate ------------------------------------------------------------


@pytest.mark.parametrize("event", [DISMISSAL, JUDGMENT])
def test_a_row_the_corpus_records_decided_refuses_either_event(tmp_path: Any, event: str) -> None:
    closed = row(date_decided=date(2026, 3, 1))

    assert (
        forward_refusal_reason_from_parts(tmp_path, "cand", 100, event, [], closed)
        == "the corpus records the case decided"
    )


# --- the command ----------------------------------------------------------------


def test_a_quiet_docket_read_inside_the_bound_is_provisioned(
    fixture_corpus: FixtureCorpus,
) -> None:
    seed(fixture_corpus, *BRIEFED, read_on=date.today() - timedelta(days=2))

    result = provision(DISMISSAL)

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "cand", 100)
    context = json.loads(paths.cell_context.read_text())
    assert context["snapshot_date"] == MOVED.isoformat()
    # None of the Court's fields is written for a district docket.
    assert context["band"] is None
    assert context["salience_version"] is None
    assert context["term"] is None
    assert context["signals_observable"] is False


@pytest.mark.parametrize("read_on", [None, date.today() - timedelta(days=11)])
def test_a_docket_not_read_inside_the_bound_is_refused(
    fixture_corpus: FixtureCorpus, read_on: date | None
) -> None:
    seed(fixture_corpus, *BRIEFED, read_on=read_on)

    result = provision(DISMISSAL)

    assert result.exit_code == 3
    assert "forward bound" in result.output
    assert not CasePaths(fixture_corpus.data_root, "cand", 100).cell_context.exists()


def test_a_fresh_snapshot_needs_no_read_stamp(fixture_corpus: FixtureCorpus) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(conn, [row()])
        corpus.upsert_snapshot(conn, CASE, date.today(), payload(*BRIEFED))

    assert provision(DISMISSAL).exit_code == 0


def test_a_decided_row_refuses_the_judgment_event_at_the_command(
    fixture_corpus: FixtureCorpus,
) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(conn, [row(last_pulled=date.today(), date_decided=date(2026, 3, 1))])
        corpus.upsert_snapshot(conn, CASE, MOVED, payload(*BRIEFED))

    result = provision(JUDGMENT)

    assert result.exit_code == 3
    assert "the corpus records the case decided" in result.output


def test_the_read_day_does_not_freshen_a_trial_id_on_the_courts_docket(
    fixture_corpus: FixtureCorpus,
) -> None:
    # scotus/305's snapshot is long past the bound; a read stamp on its row is
    # the Court channels' own and buys a trial id nothing.
    with corpus.connect(fixture_corpus.db_path) as conn:
        conn.execute(
            "UPDATE cases SET last_pulled = ? WHERE case_id = 'scotus/305'",
            (date.today().isoformat(),),
        )

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            DISMISSAL,
            "--refuse-terminal",
            "--max-snapshot-age-days",
            "10",
        ],
    )

    assert result.exit_code == 3
    assert "forward bound" in result.output


def test_the_read_day_does_not_freshen_another_stages_event(
    fixture_corpus: FixtureCorpus,
) -> None:
    seed(fixture_corpus, *BRIEFED, read_on=date.today())

    result = provision("evt-appeal-disposition")

    assert result.exit_code == 3
    assert f"snapshot {MOVED.isoformat()} is" in result.output


def test_a_ruled_motion_is_refused_on_the_snapshot_and_recorded(
    fixture_corpus: FixtureCorpus, tmp_path: Any
) -> None:
    seed(fixture_corpus, *BRIEFED, GRANTED, read_on=date.today())
    refusal = tmp_path / "refusal.json"

    result = provision(DISMISSAL, "--refusal-out", str(refusal))

    assert result.exit_code == 3
    assert "snapshot docket entry 70 resolves" in result.output
    assert json.loads(refusal.read_text())["gate"] == "snapshot"


def test_the_pre_mint_poll_is_not_run_for_a_trial_event(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    seed(fixture_corpus, *BRIEFED, read_on=date.today())

    def refuse(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("the Court's poll was run for a district docket")

    monkeypatch.setattr("fedcourtsai.cli._pre_mint_poll_gate", refuse)
    poll = tmp_path / "poll.json"

    result = provision(DISMISSAL, "--pre-mint-poll", "--pre-mint-poll-out", str(poll))

    assert result.exit_code == 0, result.output
    assert not poll.exists()


# --- the context ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("case_id", "number"), [("cand/100", "3:26-cv-00100"), ("ca9/55", "23-15285")]
)
def test_a_lower_court_context_carries_placement_alone(case_id: str, number: str) -> None:
    context = cell_context.build(
        case_id,
        date(2026, 11, 19),
        {"docket_number": number, "case_name": "Listed v. Developer", "docket_entries": BRIEFED},
        "forward",
        decided_before="2026",
    )

    stated = {k: v for k, v in context.model_dump().items() if v not in (None, [], False)}
    assert stated == {
        "schema_version": context.schema_version,
        "mode": "forward",
        "snapshot_date": date(2026, 11, 19),
        "snapshot_provenance": "as-stored",
        "decided_before": "2026",
    }
