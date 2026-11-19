"""Provisioning a forward cell on a district docket's trial event.

The gates a trial event is held to (the day the docket was last read, the
trial resolver's reading of the snapshot, the record) and the context a
lower-court docket's cell is written.
"""

from __future__ import annotations

import json
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


@pytest.mark.parametrize(
    "later",
    [
        entry(70, "ORDER: Defendants' motion to dismiss is GRANTED.", "2026-07-20"),
        {
            **entry(0, "MINUTE ORDER granting Motion to Dismiss.", "2026-07-20"),
            "entry_number": None,
        },
        entry(70, "ORDER re 45: the motion is DENIED.", "2026-07-20"),
        entry(
            70, "ORDER granting in part and denying in part OAI's motion to dismiss", "2026-07-20"
        ),
        entry(70, "JUDGMENT in favor of Developer, Inc. against Plaintiff.", "2026-07-20"),
        entry(70, "Civil Case Terminated.", "2026-07-20"),
        entry(70, "ORDER: The Clerk is directed to close this case.", "2026-07-20"),
        entry(70, "STIPULATION of Dismissal with prejudice by all parties", "2026-07-20"),
    ],
)
def test_a_sign_of_a_ruling_the_resolver_passes_over_refuses_the_motion(
    later: dict[str, Any],
) -> None:
    reason = forward_leakage(payload(*BRIEFED, later), "cand", DISMISSAL)

    assert reason is not None
    assert "ORDER" not in reason and "GRANTED" not in reason


@pytest.mark.parametrize(
    "later",
    [
        entry(60, "ORDER setting hearing on 45 Motion to Dismiss for 3/1/2026.", "2026-02-10"),
        entry(60, "ORDER granting 59 Motion for Extension of Time re 45 Motion.", "2026-02-10"),
        entry(
            60, "ORDER granting 59 Stipulation re briefing on 45 Motion to Dismiss.", "2026-02-10"
        ),
        entry(60, "ORDER granting 59 Motion for Summary Judgment page limits.", "2026-02-10"),
        entry(
            60,
            "ORDER: Exhibit 3 stays sealed until 90 days after this case is closed.",
            "2026-02-10",
        ),
        entry(
            60, "ORDER granting 59 Motion to Strike Opposition to Motion to Dismiss", "2026-02-10"
        ),
        entry(
            60, "ORDER: the Court GRANTS three more pages for the motion to dismiss", "2026-02-10"
        ),
        entry(
            60, "NOTICE by Listed Author re 45 Motion to Dismiss: it should be denied", "2026-02-10"
        ),
        entry(60, "ORDER of USCA denying petition as to 45 Motion to Dismiss", "2026-02-10"),
    ],
)
def test_an_order_about_the_motion_is_no_sign_of_its_ruling(later: dict[str, Any]) -> None:
    assert forward_leakage(payload(*BRIEFED, later), "cand", DISMISSAL) is None


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
