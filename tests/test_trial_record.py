"""A trial-stage cell's ``record/trial.json``: the judge, the briefing, the other dockets."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, provision
from fedcourtsai.ai_watchlist import AiWatchlist
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import trial_record
from fedcourtsai.schemas import TrialRecord
from fedcourtsai.serialize import read_model
from fedcourtsai.trial_local_rules import TRIAL_LOCAL_RULES_FILENAME
from tests.conftest import FixtureCorpus
from tests.test_trial_provision import BRIEFED, CASE, DISMISSAL, JUDGMENT, MOVED, payload, row

runner = CliRunner()
READ_ON = date(2026, 11, 19)


def watchlist(*related: dict[str, Any], court: str = "cand", docket: int = 100) -> AiWatchlist:
    return AiWatchlist.model_validate(
        {
            "categories": {"training-data": "Suits over what a model was trained on."},
            "cases": [
                {
                    "name": "Listed v. Developer",
                    "court": court,
                    "docket_id": docket,
                    "docket_number": "3:26-cv-00100",
                    "category": "training-data",
                    "why": "A developer is a defendant.",
                    "developers": ["Developer"],
                    "added": "2026-01-01",
                    "related": list(related),
                }
            ],
        }
    )


APPEAL = {"court": "ca9", "docket_id": 55, "docket_number": "26-1234", "relation": "appeal"}
MEMBER = {"court": "cand", "docket_id": 101, "docket_number": "3:26-cv-00101", "relation": "member"}


def judged(*entries: dict[str, Any], **header: Any) -> dict[str, Any]:
    return {**payload(*entries), **header}


def test_a_motion_cell_reads_its_briefing_by_entry_and_date() -> None:
    record = trial_record.build(CASE, DISMISSAL, payload(*BRIEFED), None, read_on=READ_ON)

    assert record is not None
    assert record.moment == "trial-dismissal"
    briefing = record.briefing
    assert briefing is not None
    assert (briefing.motion.entry_number, briefing.motion.date_filed) == (45, date(2026, 1, 10))
    assert briefing.opposition is not None
    assert (briefing.opposition.entry_number, briefing.opposition.date_filed) == (
        52,
        date(2026, 1, 24),
    )
    assert briefing.reply is not None
    assert briefing.reply.entry_number == 58
    assert (briefing.opened_on, briefing.opening_basis) == (date(2026, 1, 31), "reply")


def test_briefing_still_open_states_what_is_there_and_no_opening() -> None:
    record = trial_record.build(CASE, DISMISSAL, payload(*BRIEFED[:2]), None, read_on=READ_ON)

    assert record is not None
    assert record.briefing is not None
    assert record.briefing.opposition is not None
    assert record.briefing.reply is None
    assert (record.briefing.opened_on, record.briefing.opening_basis) == (None, None)


def test_an_entry_after_the_read_day_is_not_briefing() -> None:
    record = trial_record.build(CASE, DISMISSAL, payload(*BRIEFED), None, read_on=date(2026, 1, 25))

    assert record is not None
    assert record.briefing is not None
    assert record.briefing.opposition is not None
    assert record.briefing.reply is None


def test_the_judgment_event_and_an_unread_motion_carry_no_briefing() -> None:
    judgment = trial_record.build(CASE, JUDGMENT, payload(*BRIEFED), None, read_on=READ_ON)
    unread = trial_record.build(
        CASE, "evt-motion-trial-dismissal-46", payload(*BRIEFED), None, read_on=READ_ON
    )

    assert judgment is not None
    assert judgment.briefing is None
    assert judgment.moment == "trial-judgment"
    assert unread is not None
    assert unread.briefing is None


def test_the_judges_are_the_snapshots_own_header_fields() -> None:
    named = trial_record.build(
        CASE,
        JUDGMENT,
        judged(assigned_to_str=" A. Bench ", referred_to_str=""),
        None,
        read_on=READ_ON,
    )
    unnamed = trial_record.build(
        CASE, JUDGMENT, judged(assigned_to_str=None), None, read_on=READ_ON
    )

    assert named is not None
    assert (named.assigned_judge, named.referred_judge) == ("A. Bench", None)
    assert unnamed is not None
    assert (unnamed.assigned_judge, unnamed.referred_judge) == (None, None)


def test_the_listed_cases_other_dockets_are_identifiers_with_their_relation() -> None:
    record = trial_record.build(
        CASE, JUDGMENT, payload(), watchlist(APPEAL, MEMBER), read_on=READ_ON
    )

    assert record is not None
    assert record.listed_case == "Listed v. Developer"
    assert [(d.case_id, d.docket_number, d.relation) for d in record.related_dockets] == [
        ("ca9/55", "26-1234", "appeal"),
        ("cand/101", "3:26-cv-00101", "member"),
    ]


def test_a_member_dockets_cell_is_given_the_listed_docket_and_not_itself() -> None:
    record = trial_record.build(
        "cand/101", JUDGMENT, payload(), watchlist(APPEAL, MEMBER), read_on=READ_ON
    )

    assert record is not None
    assert [(d.case_id, d.relation) for d in record.related_dockets] == [
        ("cand/100", "listed"),
        ("ca9/55", "appeal"),
    ]


def test_a_docket_the_watchlist_does_not_name_has_no_listed_case() -> None:
    record = trial_record.build(
        CASE, JUDGMENT, payload(), watchlist(court="nysd", docket=7), read_on=READ_ON
    )

    assert record is not None
    assert record.listed_case is None
    assert record.related_dockets == []


def test_another_stages_event_has_no_trial_record() -> None:
    assert (
        trial_record.build("scotus/1", "evt-cert-petition", payload(), None, read_on=READ_ON)
        is None
    )


def _provision(event: str, *extra: str, court: str = "cand", docket: str = "100") -> Any:
    return runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            court,
            "--docket",
            docket,
            "--event",
            event,
            "--refuse-terminal",
            "--max-snapshot-age-days",
            "10",
            *extra,
        ],
    )


def test_a_replay_cell_is_given_no_trial_record(fixture_corpus: FixtureCorpus) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(conn, [row(last_pulled=date.today())])
        corpus.upsert_snapshot(conn, CASE, MOVED, payload(*BRIEFED))

    result = _provision(DISMISSAL, "--mode", "replay")

    assert result.exit_code == 0, result.output
    assert not CasePaths(fixture_corpus.data_root, "cand", 100).trial_record.exists()
    assert "trial record" not in result.output


def test_a_local_rules_file_that_cannot_be_read_refuses_the_cell(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(tmp_path / "config"))
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(conn, [row(last_pulled=date.today())])
        corpus.upsert_snapshot(conn, CASE, MOVED, payload(*BRIEFED))
    rules = tmp_path / "config" / TRIAL_LOCAL_RULES_FILENAME
    rules.parent.mkdir(parents=True)
    rules.write_text("courts: [not, a, mapping]\n")

    result = _provision(DISMISSAL)

    assert result.exit_code == 1, result.output
    assert not CasePaths(fixture_corpus.data_root, "cand", 100).cell_context.exists()


def test_the_command_stages_the_record_for_a_trial_cell(fixture_corpus: FixtureCorpus) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(conn, [row(last_pulled=date.today() - timedelta(days=2))])
        corpus.upsert_snapshot(conn, CASE, MOVED, judged(*BRIEFED, assigned_to_str="A. Bench"))

    result = _provision(DISMISSAL)

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "cand", 100)
    record = read_model(paths.trial_record, TrialRecord)
    assert record.event_id == DISMISSAL
    assert record.assigned_judge == "A. Bench"
    assert record.briefing is not None
    assert record.briefing.reply is not None
    assert "trial record: motion briefing read" in result.output
    # The record names entries and never quotes one.
    assert "MOTION to Dismiss" not in paths.trial_record.read_text()
    assert "A. Bench" not in result.output


def test_a_later_record_on_the_same_tree_clears_the_trial_file(
    fixture_corpus: FixtureCorpus,
) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(conn, [row(last_pulled=date.today() - timedelta(days=2))])
        corpus.upsert_snapshot(conn, CASE, MOVED, payload(*BRIEFED))
    assert _provision(JUDGMENT).exit_code == 0
    paths = CasePaths(fixture_corpus.data_root, "cand", 100)
    assert json.loads(paths.trial_record.read_text())["briefing"] is None

    # A record written for no trial event leaves none behind.
    placed = provision.Placement(
        snapshot_date=MOVED,
        payload=payload(*BRIEFED),
        documents=[],
        provenance="as-stored",
        boundary=None,
        dropped_entries=0,
        dropped_documents=0,
    )
    provision.write_cell_record(paths, CASE, placed, mode="forward", cutoff=None)

    assert not paths.trial_record.exists()
