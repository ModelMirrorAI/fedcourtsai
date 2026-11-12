"""The merits coverage check: the census set against the Granted & Noted list."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import merits_coverage_check as mcc
from fedcourtsai.pipeline.merits_coverage_check import MeritsAlarm, merits_coverage_check
from fedcourtsai.schemas import Disposition, EventKind, Judgment, MeritsTermination, Stage
from tests.conftest import seed_prediction

TODAY = date(2026, 11, 11)
ORDER = "evt-order-judgment"
ARGUED = "evt-argument-judgment"

# The list as its text layer extracts: one entry per case, a consolidated pair,
# an original-jurisdiction case and an argued application.
LIST = """
GRANTED & NOTED LIST
OCTOBER TERM 2026 CASES FOR ARGUMENT

156, Orig. *  NEW YORK V. NEW JERSEY
   Order:  12/12/25 - set for oral argument
   Argument Date:  10/5/26

25-100  CFX ALPHA V. BETA
   Court:  USCA-2     Granted:  6/29/26
   Argument Date:  1/12/27

25-200)1 CFX GAMMA V. DELTA
25-201)2 CFX EPSILON V. DELTA
   Court:  1USCA-7; 2USCA-2   Granted:  6/30/26
   Argument Date:  10/6/26

25-300  CSY ZETA V. ALASKA
   Court:  SC-AK     Granted:  6/15/26
   Argument Date:  11/20/26

25-400  CFX ETA V. THETA
   Court:  USCA-9     Granted:  1/16/26
   Argument Date:  10/7/26   Decided:  11/2/26
   Author:  J. Kagan

25-500  CFX IOTA V. KAPPA
   Court:  USCA-4     Granted:  11/6/26

25-600  CFX LAMBDA V. MU
   Court:  USCA-4     Granted:  10/1/26

26A10   NU V. XI
   Argument Date:  12/1/26
"""


def _case(
    conn: sqlite3.Connection,
    docket: int,
    number: str,
    granted: date,
    *,
    disposition: Disposition | None = Disposition.granted,
    events: Sequence[str] = (ORDER,),
    merits_judgment: Judgment | None = None,
    merits_decided: date | None = None,
) -> None:
    case_id = f"scotus/{docket}"
    corpus.upsert_rows(
        conn,
        [
            corpus.CorpusRow(
                case_id=case_id,
                court="scotus",
                docket_number=number,
                disposition=disposition,
                date_cert_granted=granted if disposition is not None else None,
                merits_judgment=merits_judgment,
                merits_decided=merits_decided,
            )
        ],
    )
    corpus.upsert_events(
        conn,
        [
            corpus.CorpusEvent(
                event_id=event_id,
                case_id=case_id,
                court="scotus",
                kind=EventKind.argument if event_id == ARGUED else EventKind.order,
                stage=Stage.merits,
            )
            for event_id in events
        ],
    )


@pytest.fixture
def world(tmp_path: Path) -> tuple[Path, Path]:
    """A corpus and ledger in which every listed docket is covered."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    with corpus.connect(db) as conn:
        _case(conn, 100, "25-100", date(2026, 6, 29))
        _case(conn, 200, "25-200", date(2026, 6, 30), events=(ORDER, ARGUED))
        _case(conn, 201, "25-201", date(2026, 6, 30))
        _case(conn, 300, "25-300", date(2026, 6, 15))
        _case(
            conn,
            400,
            "25-400",
            date(2026, 1, 16),
            events=(ORDER, ARGUED),
            merits_judgment=Judgment.reversed,
            merits_decided=date(2026, 11, 2),
        )
        _case(conn, 600, "25-600", date(2026, 10, 1))
    for docket in (100, 200, 300, 400, 600):
        seed_prediction(data, "scotus", docket, ORDER, run_id="20260801T000000Z")
    seed_prediction(data, "scotus", 200, ARGUED, run_id="20261007T000000Z")
    seed_prediction(data, "scotus", 400, ARGUED, run_id="20261008T000000Z")
    return db, data


def _check(
    db: Path, data: Path, *, today: date = TODAY, text: str | None = LIST
) -> dict[str, mcc.CheckedDocket]:
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage_check(
            conn, data, term=2026, lists={2026: text, 2027: None}, today=today
        )
    return {d.docket_number: d for d in result.dockets}


def test_a_covered_list_raises_no_alarm(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage_check(
            conn, data, term=2026, lists={2026: LIST, 2027: None}, today=TODAY
        )

    assert result.ok and result.alarms == 0
    own, following = result.lists
    assert (own.term, own.read, own.entries, own.dockets) == (2026, True, 7, 7)
    # 25-500 was granted five days ago: no row yet, inside the grace period.
    assert (own.with_merits_event, own.without_merits_event) == (6, 1)
    assert own.original == ["156, Orig."]
    assert own.applications == ["26A10"]
    assert (following.term, following.read) == (2027, False)
    dockets = {d.docket_number: d for d in result.dockets}
    assert dockets["25-201"].lead == "25-200"
    assert dockets["25-200"].code == "CFX"
    assert dockets["25-300"].code == "CSY"
    assert dockets["25-400"].decided == date(2026, 11, 2)
    assert dockets["25-100"].first_forecast == date(2026, 8, 1)


def test_a_listed_docket_missing_from_the_corpus_alarms_after_the_grace_period(
    world: tuple[Path, Path],
) -> None:
    db, data = world
    assert _check(db, data)["25-500"].alarms == []
    late = _check(db, data, today=date(2026, 11, 13))
    assert late["25-500"].alarms == [MeritsAlarm.no_corpus_row]


def test_a_row_without_a_merits_grant_or_event_alarms(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 500, "25-500", date(2026, 10, 1), disposition=None, events=())
        _case(conn, 700, "25-700", date(2026, 10, 1), events=())
    text = LIST.replace("Granted:  11/6/26", "Granted:  10/1/26") + (
        "\n25-700  CFX OMICRON V. PI\n   Court:  USCA-4     Granted:  10/1/26\n"
    )
    dockets = _check(db, data, text=text)
    assert dockets["25-500"].alarms == [MeritsAlarm.no_merits_grant]
    # In scope and pending with no event: the census hole, seen from the list too.
    assert dockets["25-700"].alarms == [MeritsAlarm.no_merits_event, MeritsAlarm.coverage_hole]


def test_an_approaching_argument_without_a_forecast_alarms(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 301, "25-301", date(2026, 6, 15))
        _case(conn, 101, "25-101", date(2026, 6, 15))
    text = LIST + (
        "\n25-301  CFX RHO V. SIGMA\n   Court:  USCA-4     Granted:  6/15/26\n"
        + "   Argument Date:  11/25/26\n"
        + "\n25-101  CFX TAU V. UPSILON\n   Court:  USCA-4     Granted:  6/15/26\n"
        + "   Argument Date:  1/12/27\n"
    )
    dockets = _check(db, data, text=text)
    assert dockets["25-301"].alarms == [MeritsAlarm.argument_unforecast]
    # Argument two months out: owed, and not yet an alarm.
    assert dockets["25-101"].alarms == []
    assert dockets["25-300"].alarms == []


def test_the_argued_moment_is_checked_after_its_grace_period(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 301, "25-301", date(2026, 6, 15))
        _case(conn, 302, "25-302", date(2026, 6, 15))
    seed_prediction(data, "scotus", 301, ORDER)
    seed_prediction(data, "scotus", 302, ORDER)
    text = LIST + (
        "\n25-301  CFX RHO V. SIGMA\n   Court:  USCA-4     Granted:  6/15/26\n"
        + "   Argument Date:  11/4/26\n"
        + "\n25-302  CFX PHI V. CHI\n   Court:  USCA-4     Granted:  6/15/26\n"
        + "   Argument Date:  11/9/26\n"
    )
    dockets = _check(db, data, text=text)
    assert dockets["25-301"].alarms == [MeritsAlarm.argued_unforecast]
    assert dockets["25-302"].alarms == []  # argued two days ago
    # One argument, one opinion: the lead's argued forecast covers its member.
    assert dockets["25-201"].alarms == []
    assert not dockets["25-201"].argued_forecast


def test_a_rescheduled_argument_reads_its_new_day(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 301, "25-301", date(2026, 6, 15))
    seed_prediction(data, "scotus", 301, ORDER)
    text = LIST + (
        "\n25-301  CFX RHO V. SIGMA\n   Court:  USCA-4     Granted:  6/15/26\n"
        + "   Argument Date:  10/5/26\n   Rescheduled Argument Date:  12/1/26\n"
    )
    docket = _check(db, data, text=text)["25-301"]
    assert docket.argument == date(2026, 12, 1)
    assert docket.alarms == []


def test_a_decision_without_an_earlier_forecast_alarms_then_stands(
    world: tuple[Path, Path],
) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(
            conn,
            401,
            "25-401",
            date(2026, 1, 16),
            merits_judgment=Judgment.affirmed,
            merits_decided=date(2026, 11, 2),
        )
        _case(
            conn,
            402,
            "25-402",
            date(2026, 1, 16),
            merits_judgment=Judgment.affirmed,
            merits_decided=date(2026, 11, 2),
        )
    # A forecast dated on the decision day is not one made before it.
    seed_prediction(data, "scotus", 402, ORDER, run_id="20261102T141200Z")
    text = LIST + (
        "\n25-401  CFX PSI V. OMEGA\n   Court:  USCA-4     Granted:  1/16/26\n"
        + "   Argument Date:  10/7/26   Decided:  11/2/26\n"
        + "\n25-402  CFX AYIN V. BET\n   Court:  USCA-4     Granted:  1/16/26\n"
        + "   Argument Date:  10/7/26   Decided:  11/2/26\n"
    )
    recent = _check(db, data, text=text)
    assert recent["25-401"].alarms == [MeritsAlarm.decided_unforecast]
    assert recent["25-402"].alarms == [MeritsAlarm.decided_unforecast]
    assert recent["25-400"].alarms == []  # forecast in August, decided in November
    assert not recent["25-401"].standing_miss

    later = _check(db, data, text=text, today=date(2026, 12, 15))
    assert later["25-401"].alarms == []
    assert later["25-401"].standing_miss
    assert not later["25-400"].standing_miss


def test_a_dismissed_case_owes_no_further_forecast(world: tuple[Path, Path]) -> None:
    # Forecast at the grant, then dismissed before argument: its status stays
    # `forecast`, and the argued moment it never reached is not a miss.
    db, data = world
    with corpus.connect(db) as conn:
        corpus.set_merits_termination(conn, "scotus/600", MeritsTermination.voluntary_dismissal)
    text = LIST.replace("Granted:  10/1/26\n", "Granted:  10/1/26\n   Argument Date:  10/13/26\n")
    docket = _check(db, data, text=text)["25-600"]
    assert docket.terminated == "voluntary-dismissal"
    assert docket.alarms == []


def test_a_census_grant_on_no_list_is_still_checked(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 900, "26-900", date(2026, 10, 20), events=())
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage_check(
            conn, data, term=2026, lists={2026: LIST, 2027: None}, today=TODAY
        )
    (unlisted,) = [d for d in result.dockets if d.list_term is None]
    assert unlisted.docket_number == "26-900"
    assert unlisted.alarms == [MeritsAlarm.coverage_hole]
    assert not result.ok
    report = mcc.render_report(result, vintage="latest pull 2026-11-11")
    assert "**26-900** (`scotus/900`): census hole, census status `no_event`" in report
    assert "Corpus vintage, corpus-wide: latest pull 2026-11-11." in report
    # The headline counts the Term's own list (a member with no forecast of its
    # own and the five-day-old grant are the two short); the alarm is off it.
    assert "5 of 7 dockets on the Term's Granted & Noted list hold a merits forecast" in report
    assert "1 docket(s) checked, listed or not, carry an alarm" in report
    assert "not a coverage rate" in report
    # Corpus text cannot mention or link from the bot's issue.
    result.dockets[-1].docket_number = "26-900 @someone #12"
    assert "**26-900 someone 12**" in mcc.render_report(result)
    assert "25-201 with lead 25-200" in report
    assert "156, Orig., 26A10" in report


def test_a_fresh_grant_without_its_event_is_inside_the_grace_period(
    world: tuple[Path, Path],
) -> None:
    # Pulled before its event is minted: a census hole on paper, the stream
    # working in fact, on a list or off one.
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 500, "25-500", date(2026, 11, 6), events=())
        _case(conn, 900, "26-900", date(2026, 11, 9), events=())
    early = _check(db, data)
    assert early["25-500"].status == "no_event"
    assert early["25-500"].alarms == []
    assert early["26-900"].alarms == []
    late = _check(db, data, today=date(2026, 11, 16))
    assert late["25-500"].alarms == [MeritsAlarm.no_merits_event, MeritsAlarm.coverage_hole]
    assert late["26-900"].alarms == [MeritsAlarm.coverage_hole]


def test_an_entry_with_no_grant_date_is_past_its_grace_period(world: tuple[Path, Path]) -> None:
    db, data = world
    text = LIST.replace("USCA-4     Granted:  11/6/26", "USCA-4")
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage_check(conn, data, term=2026, lists={2026: text}, today=TODAY)
    (own,) = result.lists
    assert own.problems == ["25-500"]
    docket = next(d for d in result.dockets if d.docket_number == "25-500")
    assert docket.alarms == [MeritsAlarm.no_corpus_row]


def test_the_miss_window_ends_after_twenty_eight_days(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(
            conn,
            401,
            "25-401",
            date(2026, 1, 16),
            merits_judgment=Judgment.affirmed,
            merits_decided=date(2026, 11, 2),
        )
    text = LIST + "\n25-401  CFX PSI V. OMEGA\n   Court:  USCA-4     Granted:  1/16/26\n"
    on_the_day = _check(db, data, text=text, today=date(2026, 11, 30))["25-401"]
    assert on_the_day.alarms == [MeritsAlarm.decided_unforecast]
    after = _check(db, data, text=text, today=date(2026, 12, 1))["25-401"]
    assert (after.alarms, after.standing_miss) == ([], True)


def test_a_decision_the_corpus_lacks_stays_an_alarm(world: tuple[Path, Path]) -> None:
    # The list prints the decision; the row was never latched. Forecast or
    # not, and however old, that is a corpus fault someone can still repair.
    db, data = world
    text = LIST.replace(
        "   Argument Date:  1/12/27\n", "   Argument Date:  3/2/26   Decided:  6/1/26\n"
    )
    docket = _check(db, data, text=text)["25-100"]
    assert docket.decided == date(2026, 6, 1)
    assert not docket.decision_recorded
    assert docket.alarms == [MeritsAlarm.decision_unrecorded]
    assert docket.standing_miss  # its only forecast is dated after the decision
    recorded = _check(db, data)["25-400"]
    assert recorded.decision_recorded and recorded.alarms == []


def test_a_case_on_two_lists_is_read_once_from_the_later_one(world: tuple[Path, Path]) -> None:
    # Held over for reargument: the earlier list's argument date is stale.
    db, data = world
    later = (
        "25-300  CSY ZETA V. ALASKA\n   Court:  SC-AK     Granted:  6/15/26\n"
        + "   Reargument Date:  10/12/27\n"
    )
    earlier = LIST.replace("Argument Date:  11/20/26", "Argument Date:  10/20/26")
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage_check(
            conn, data, term=2026, lists={2026: earlier, 2027: later}, today=TODAY
        )
    (docket,) = [d for d in result.dockets if d.docket_number == "25-300"]
    assert (docket.list_term, docket.argument) == (2027, date(2027, 10, 12))
    assert docket.alarms == []
    assert [(r.term, r.dockets) for r in result.lists] == [(2026, 6), (2027, 1)]


def test_a_members_forecast_counts_for_its_entry(world: tuple[Path, Path]) -> None:
    # The lead holds no forecast and the member does: one argument, covered.
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 310, "25-310", date(2026, 6, 15))
        _case(conn, 311, "25-311", date(2026, 6, 15))
    seed_prediction(data, "scotus", 311, ORDER)
    text = LIST + (
        "\n25-310)1 CFX RHO V. SIGMA\n25-311)2 CFX PHI V. SIGMA\n"
        + "   Court:  USCA-4     Granted:  6/15/26\n   Argument Date:  11/20/26\n"
    )
    dockets = _check(db, data, text=text)
    assert dockets["25-310"].status == "owed"
    assert dockets["25-310"].alarms == []


def test_an_unread_list_is_never_ok(world: tuple[Path, Path]) -> None:
    db, data = world
    with corpus.connect_readonly(db) as conn:
        result = merits_coverage_check(conn, data, term=2026, lists={2026: None}, today=TODAY)
    assert result.alarms == 0
    assert not result.ok
    assert "could not be read" in mcc.render_report(result)


class _Gh:
    """A recorded `gh`: canned issue listing, every call kept."""

    def __init__(self, issues: list[dict[str, object]]) -> None:
        self.issues = issues
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        if argv[:2] == ["gh", "api"]:
            return json.dumps(self.issues)
        if argv[1:3] == ["issue", "create"]:
            return "https://github.com/o/r/issues/7\n"
        return ""

    def verbs(self) -> list[str]:
        return [" ".join(call[1:3]) for call in self.calls]


def _result(db: Path, data: Path, *, text: str | None = LIST) -> mcc.MeritsCoverageCheck:
    with corpus.connect_readonly(db) as conn:
        return merits_coverage_check(
            conn, data, term=2026, lists={2026: text}, today=date(2026, 11, 13)
        )


_ALARM = {"number": 7, "title": mcc.ISSUE_TITLE, "user": {"login": mcc.ALARM_AUTHOR}}


def test_the_latch_opens_refreshes_and_closes_one_issue(
    world: tuple[Path, Path], tmp_path: Path
) -> None:
    db, data = world
    failing = _result(db, data)  # 25-500 is past its grace period
    assert failing.alarms == 1
    body = tmp_path / "report.md"
    body.write_text(mcc.render_report(failing), encoding="utf-8")

    gh = _Gh([])
    assert mcc.latch("o/r", failing, body, runner=gh) == "opened https://github.com/o/r/issues/7"
    assert gh.verbs() == [
        "label create",
        "api repos/o/r/issues?labels=merits-coverage&state=open&per_page=100",
        "issue create",
    ]
    assert gh.calls[-1][-2:] == ["--body-file", str(body)]

    gh = _Gh([_ALARM])
    assert mcc.latch("o/r", failing, body, runner=gh) == "refreshed #7"
    assert gh.verbs()[-1] == "issue edit"

    with corpus.connect(db) as conn:
        _case(conn, 500, "25-500", date(2026, 11, 6))
    seed_prediction(data, "scotus", 500, ORDER)
    passing = _result(db, data)
    assert passing.ok
    gh = _Gh([_ALARM])
    assert mcc.latch("o/r", passing, body, runner=gh) == "closed #7"
    assert gh.verbs()[-2:] == ["issue comment", "issue close"]

    # A re-sent create can leave two: a clean check closes both.
    gh = _Gh([_ALARM, {**_ALARM, "number": 9}])
    assert mcc.latch("o/r", passing, body, runner=gh) == "closed #7, #9"
    assert gh.verbs().count("issue close") == 2

    gh = _Gh([])
    assert mcc.latch("o/r", passing, body, runner=gh) == "no alarm, and no open issue"
    assert gh.verbs()[-1].startswith("api ")


def test_the_latch_touches_only_its_own_issue(world: tuple[Path, Path], tmp_path: Path) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 500, "25-500", date(2026, 11, 6))
    seed_prediction(data, "scotus", 500, ORDER)
    passing = _result(db, data)
    others: list[dict[str, object]] = [
        {"number": 1, "title": mcc.ISSUE_TITLE, "user": {"login": "someone"}},
        {"number": 2, "title": "Another report", "user": {"login": mcc.ALARM_AUTHOR}},
        {**_ALARM, "number": 3, "pull_request": {}},
    ]
    gh = _Gh(others)
    assert mcc.latch("o/r", passing, tmp_path / "r.md", runner=gh) == "no alarm, and no open issue"
    assert not any(call[1:3] == ["issue", "close"] for call in gh.calls)


def test_the_latch_refuses_a_check_that_read_no_list(
    world: tuple[Path, Path], tmp_path: Path
) -> None:
    db, data = world
    unread = _result(db, data, text=None)
    gh = _Gh([_ALARM])
    with pytest.raises(ValueError, match="never read the OT2026"):
        mcc.latch("o/r", unread, tmp_path / "r.md", runner=gh)
    assert gh.calls == []


def test_the_command_reports_and_exits_three_on_an_alarm(
    world: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db, data = world
    with corpus.connect(db) as conn:
        _case(conn, 900, "26-900", date(2026, 10, 20), events=())
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(db.parent))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    served = {26: LIST}
    monkeypatch.setattr(cli, "_granted_noted_text", lambda _fetcher, term: served.get(term))
    report = tmp_path / "report.md"

    result = CliRunner().invoke(
        app, ["merits-coverage-check", "--term", "2026", "--report-out", str(report)]
    )

    assert result.exit_code == 3, result.output
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["term"] == 2026
    assert payload["ok"] is False
    assert "**26-900**" in report.read_text(encoding="utf-8")
    assert "OT2027 Granted & Noted list: not published or not readable" in result.stderr

    served.clear()
    unread = CliRunner().invoke(app, ["merits-coverage-check", "--term", "2026"])
    assert unread.exit_code == 1
    assert "could not be read" in unread.stderr


def test_the_alarm_command_refuses_bad_input(tmp_path: Path) -> None:
    bad = tmp_path / "check.json"
    bad.write_text("{}", encoding="utf-8")
    runner = CliRunner()
    args = ["--check", str(bad), "--report", str(bad)]
    assert (
        runner.invoke(app, ["merits-coverage-alarm", "--repo", "not a repo", *args]).exit_code == 2
    )
    assert runner.invoke(app, ["merits-coverage-alarm", "--repo", "o/r", *args]).exit_code == 2
