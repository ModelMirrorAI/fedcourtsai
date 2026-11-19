"""The trial stage's watchlist pass (``pipeline/trial_events.py``) and its adjudication list.

No trial moment is switched on, so the cases that write an event switch the
declared moments on for the test alone.
"""

from __future__ import annotations

import dataclasses
import json
import shutil
from collections.abc import Iterator
from contextlib import nullcontext
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.ai_watchlist import AiWatchlist
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments, trial_events
from fedcourtsai.pipeline.trial_events import plan_docket, run_pass
from fedcourtsai.pipeline.watchlist_refresh import WatchlistRefreshReport
from fedcourtsai.schemas import Moment, Outcome, PredictableEvent, Stage
from fedcourtsai.serialize import read_model
from fedcourtsai.trial_adjudications import (
    TRIAL_ADJUDICATIONS_FILENAME,
    Adjudication,
    load_trial_adjudications,
)
from fedcourtsai.validate import run_ledger_referential_checks, validate_ledger

TODAY = date(2026, 11, 11)
SWITCHED_ON = date(2026, 6, 1)
CASE = "cand/100"
DISMISSAL = "evt-motion-trial-dismissal-45"
JUDGMENT = "evt-order-trial-judgment"


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
BRIEFED = [MOTION, OPPOSITION, REPLY]
GRANTED = entry(70, "ORDER by Judge A. Bench granting 45 Motion to Dismiss.", "2026-07-20")
FINAL = entry(90, "JUDGMENT in favor of Defendants against Plaintiffs", "2026-08-01")


@pytest.fixture
def switched_on(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    declared = moments.trial_spec

    def on(moment: Moment | str) -> moments.TrialMomentSpec:
        return dataclasses.replace(declared(moment), forecastable=True, opens_from=SWITCHED_ON)

    monkeypatch.setattr(moments, "trial_spec", on)
    yield


def assert_valid(data: Path) -> None:
    ledger = validate_ledger(data)
    assert ledger.invalid == 0, ledger.problems
    for check in run_ledger_referential_checks(data):
        assert check.passed, (check.name, check.problems)


def stored(event_id: str, *, opened_at: date = SWITCHED_ON, resolved: bool = False) -> Any:
    spec = moments.trial_spec_for(event_id)
    assert spec is not None
    return corpus.CorpusEvent(
        event_id=event_id,
        case_id=CASE,
        court="cand",
        kind=spec.kind,
        stage=Stage.trial,
        moment=spec.moment,
        title="Listed v. Developer",
        opened_at=opened_at,
        decision_target=spec.decision_target,
        resolved=resolved,
    )


# --- the declaration ----------------------------------------------------------


def test_no_declared_moment_is_switched_on() -> None:
    assert all(
        not spec.forecastable and spec.opens_from is None for spec in moments.DECLARED_TRIAL_MOMENTS
    )


def test_the_switch_and_its_day_are_set_together() -> None:
    spec = moments.DECLARED_TRIAL_MOMENTS[0]
    with pytest.raises(ValueError, match="set together"):
        dataclasses.replace(spec, forecastable=True)
    with pytest.raises(ValueError, match="set together"):
        dataclasses.replace(spec, opens_from=SWITCHED_ON)
    with pytest.raises(ValueError, match="not a declared trial moment"):
        moments.trial_spec(Moment.grant)


# --- opening ------------------------------------------------------------------


def test_a_switched_off_moment_is_reported_and_not_written() -> None:
    plan = plan_docket(CASE, "Listed v. Developer", BRIEFED, {}, today=TODAY, judgment=True)
    assert plan.opens == [] and plan.outcomes == {} and plan.triage == []
    assert [(e.event_id, e.opened_at) for e in plan.would_open] == [
        (DISMISSAL, date(2026, 1, 31)),
        (JUDGMENT, TODAY),
    ]


def test_a_briefed_motion_opens_no_earlier_than_the_switch(switched_on: None) -> None:
    plan = plan_docket(CASE, "Listed v. Developer", BRIEFED, {}, today=TODAY)
    (event,) = plan.opens
    assert plan.would_open == []
    assert (event.event_id, event.opened_at) == (DISMISSAL, SWITCHED_ON)
    assert (event.kind, event.stage, event.moment) == ("motion", "trial", "trial-dismissal")
    assert (event.decision_target, event.docket_entry_id) == ("ruling", 1045)
    assert event.title == "Listed v. Developer" and not event.resolved

    later = entry(58, REPLY["description"], "2026-09-15")
    (event,) = plan_docket(CASE, "", [MOTION, OPPOSITION, later], {}, today=TODAY).opens
    assert (event.opened_at, event.title) == (date(2026, 9, 15), CASE)


def test_what_opens_nothing(switched_on: None) -> None:
    def opened(entries: list[dict[str, Any]], **kw: Any) -> list[str]:
        return [e.event_id for e in plan_docket(CASE, "", entries, {}, today=TODAY, **kw).opens]

    # Not fully briefed.
    assert opened([MOTION, OPPOSITION]) == []
    # Ruled on before the pass first read it: the outcome already exists.
    assert opened([*BRIEFED, GRANTED]) == []
    # The lead docket holds the same motion.
    assert opened(BRIEFED, lead_owned=frozenset({45})) == []
    # The final disposition is an event on a listed case's own docket only,
    # and only while the case is open.
    assert opened([]) == []
    assert opened([], judgment=True) == [JUDGMENT]
    assert opened([FINAL], judgment=True) == []
    # An event already stored is not written again.
    plan = plan_docket(CASE, "", BRIEFED, {DISMISSAL: stored(DISMISSAL)}, today=TODAY)
    assert plan.opens == []


def test_a_moment_whose_day_has_not_come_is_not_switched_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    declared = moments.trial_spec
    ahead = date(2027, 1, 1)
    monkeypatch.setattr(
        moments,
        "trial_spec",
        lambda m: dataclasses.replace(declared(m), forecastable=True, opens_from=ahead),
    )
    plan = plan_docket(CASE, "", BRIEFED, {}, today=TODAY, judgment=True)
    assert plan.opens == [] and len(plan.would_open) == 2


def test_a_member_opens_no_motion_while_its_lead_is_unread(switched_on: None) -> None:
    plan = plan_docket(CASE, "", BRIEFED, {}, today=TODAY, lead_unread=True)
    assert plan.opens == [] and plan.would_open == []


# --- resolving ----------------------------------------------------------------


def test_a_ruling_resolves_the_stored_event() -> None:
    plan = plan_docket(CASE, "", [*BRIEFED, GRANTED], {DISMISSAL: stored(DISMISSAL)}, today=TODAY)
    outcome = plan.outcomes[DISMISSAL]
    assert (outcome.trial_ruling, outcome.trial_leave) == ("granted", "unstated")
    assert (outcome.actual_disposition, outcome.actual_granted) == ("other", 1)
    assert (outcome.resolved_at, outcome.source) == (date(2026, 7, 20), "docket entry 70")
    assert plan.triage == [] and plan.opens == []


def test_a_final_judgment_resolves_the_judgment_event() -> None:
    plan = plan_docket(CASE, "", [FINAL], {JUDGMENT: stored(JUDGMENT)}, today=TODAY)
    outcome = plan.outcomes[JUDGMENT]
    assert (outcome.trial_judgment, outcome.actual_granted) == ("defendant", 0)
    assert (outcome.resolved_at, outcome.source) == (date(2026, 8, 1), "docket entry 90")


def test_an_open_event_with_no_ruling_stays_open() -> None:
    plan = plan_docket(
        CASE, "", BRIEFED, {DISMISSAL: stored(DISMISSAL), JUDGMENT: stored(JUDGMENT)}, today=TODAY
    )
    assert plan.outcomes == {} and plan.triage == []


def test_a_resolved_event_and_another_stages_event_are_left_alone() -> None:
    held = {
        DISMISSAL: stored(DISMISSAL, resolved=True),
        "evt-appeal-disposition": corpus.CorpusEvent(
            event_id="evt-appeal-disposition", case_id=CASE, court="cand", kind="appeal"
        ),
    }
    plan = plan_docket(CASE, "", [*BRIEFED, GRANTED], held, today=TODAY)
    assert plan.outcomes == {} and plan.triage == [] and plan.opens == []


def test_what_goes_to_triage() -> None:
    def triaged(entries: list[dict[str, Any]], event: Any) -> list[tuple[str, tuple[int, ...]]]:
        plan = plan_docket(CASE, "", entries, {event.event_id: event}, today=TODAY)
        assert plan.outcomes == {}
        return [(item.reason, item.entries) for item in plan.triage]

    # The resolver's own triage: an opinion that cites the motion and rules in no
    # form the docket text states.
    opinion = entry(70, "MEMORANDUM OPINION re 45 Motion to Dismiss.", "2026-07-20")
    ((reason, entries),) = triaged([*BRIEFED, opinion], stored(DISMISSAL))
    assert reason and entries == (70,)
    # A ruling dated before the event opened is not attributed to it.
    ((reason, _),) = triaged([*BRIEFED, GRANTED], stored(DISMISSAL, opened_at=date(2026, 8, 1)))
    assert reason == "the result is dated 2026-07-20, before the event opened on 2026-08-01"
    # A ruling read from an entry with no date.
    undated = {**GRANTED, "date_filed": None}
    ((reason, entries),) = triaged([*BRIEFED, undated], stored(DISMISSAL))
    assert (reason, entries) == ("the entry the resolver read is undated", (70,))
    # A stored motion event the opener no longer reads.
    ((reason, _),) = triaged([], stored(DISMISSAL))
    assert reason == "the opener no longer reads this motion"


# --- the adjudication list ----------------------------------------------------


def _adjudication(**fields: Any) -> Adjudication:
    row = {
        "case_id": CASE,
        "event_id": DISMISSAL,
        "result": "granted-in-part",
        "leave": "with-leave",
        "entry_number": 71,
        "resolved_at": "2026-07-21",
    }
    return Adjudication.model_validate({**row, **fields})


def test_an_adjudication_is_read_ahead_of_the_resolver() -> None:
    opinion = entry(70, "MEMORANDUM OPINION re 45 Motion to Dismiss.", "2026-07-20")
    settled = {(CASE, DISMISSAL): _adjudication()}
    for entries in ([*BRIEFED, opinion], [*BRIEFED, GRANTED], []):
        plan = plan_docket(
            CASE, "", entries, {DISMISSAL: stored(DISMISSAL)}, today=TODAY, adjudicated=settled
        )
        outcome = plan.outcomes[DISMISSAL]
        assert (outcome.trial_ruling, outcome.trial_leave) == ("granted-in-part", "with-leave")
        assert (outcome.resolved_at, outcome.source) == (
            date(2026, 7, 21),
            "docket entry 71 (adjudicated)",
        )
        assert plan.triage == []

    final = _adjudication(event_id=JUDGMENT, result="mixed", leave=None)
    plan = plan_docket(
        CASE,
        "",
        [],
        {JUDGMENT: stored(JUDGMENT)},
        today=TODAY,
        adjudicated={(CASE, JUDGMENT): final},
    )
    assert (plan.outcomes[JUDGMENT].trial_judgment, plan.outcomes[JUDGMENT].actual_granted) == (
        "mixed",
        1,
    )


def test_an_adjudication_dated_after_the_day_read_settles_nothing() -> None:
    settled = {(CASE, DISMISSAL): _adjudication(resolved_at="2026-12-01")}
    plan = plan_docket(
        CASE, "", BRIEFED, {DISMISSAL: stored(DISMISSAL)}, today=TODAY, adjudicated=settled
    )
    assert plan.outcomes == {}
    assert [(t.reason, t.entries) for t in plan.triage] == [
        ("its adjudication is dated 2026-12-01, after the day read", (71,))
    ]


def test_an_adjudication_settles_only_an_event_the_pass_wrote(switched_on: None) -> None:
    settled = {(CASE, DISMISSAL): _adjudication()}
    plan = plan_docket(CASE, "", BRIEFED, {}, today=TODAY, adjudicated=settled)
    assert plan.outcomes == {} and [e.event_id for e in plan.opens] == [DISMISSAL]
    plan = plan_docket(
        CASE,
        "",
        BRIEFED,
        {DISMISSAL: stored(DISMISSAL, resolved=True)},
        today=TODAY,
        adjudicated=settled,
    )
    assert plan.outcomes == {}


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"case_id": "cand"}, "case id"),
        ({"case_id": "cand/0100"}, "case id"),
        ({"case_id": "ca9/100"}, "not a district court id"),
        ({"case_id": "scotus/100"}, "not a district court id"),
        ({"event_id": "evt-motion-trial-dismissal"}, "not a declared trial event"),
        ({"event_id": "evt-petition-disposition"}, "not a declared trial event"),
        ({"result": "plaintiff"}, "is not one of"),
        ({"event_id": JUDGMENT, "result": "granted", "leave": None}, "is not one of"),
        ({"leave": None}, "`leave` is recorded"),
        ({"result": "denied"}, "`leave` is recorded"),
        ({"event_id": "evt-motion-trial-class-45"}, "`leave` is recorded"),
        ({"entry_number": 0}, "greater than or equal to 1"),
        ({"note": "x"}, "Extra inputs"),
    ],
)
def test_the_list_refuses_a_row_it_cannot_apply(fields: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        _adjudication(**fields)


def test_the_list_loads_by_event_and_refuses_a_repeat(tmp_path: Path) -> None:
    path = tmp_path / TRIAL_ADJUDICATIONS_FILENAME
    row = _adjudication().model_dump(mode="json")
    path.write_text(yaml.safe_dump({"adjudications": [row]}), encoding="utf-8")
    assert load_trial_adjudications(path) == {(CASE, DISMISSAL): _adjudication()}
    path.write_text(yaml.safe_dump({"adjudications": [row, row]}), encoding="utf-8")
    with pytest.raises(ValidationError, match="adjudicated twice"):
        load_trial_adjudications(path)
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_trial_adjudications(path)


def test_the_committed_list_loads() -> None:
    path = Path(__file__).resolve().parents[1] / "config" / TRIAL_ADJUDICATIONS_FILENAME
    for (case_id, event_id), row in load_trial_adjudications(path).items():
        assert (row.case_id, row.event_id) == (case_id, event_id)


# --- the pass -----------------------------------------------------------------


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
                            "court": "cand",
                            "docket_id": 103,
                            "docket_number": "3:23-cv-00103",
                            "relation": "member",
                        },
                        {
                            "court": "ca9",
                            "docket_id": 101,
                            "docket_number": "25-101",
                            "relation": "appeal",
                        },
                    ],
                }
            ],
        }
    )


def _store(db: Path, case_id: str, entries: list[dict[str, Any]]) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, case_id, date(2026, 11, 1), {"docket_entries": entries})


def test_a_switched_off_pass_writes_nothing(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _store(db, CASE, BRIEFED)
    report = run_pass(db, tmp_path / "data", _watchlist(), today=TODAY)
    assert report.opened == [] and report.resolved == [] and report.triage == []
    assert report.would_open == [(CASE, DISMISSAL), (CASE, JUDGMENT)]
    assert report.dockets_read == [CASE] and report.dockets_missing == ["cand/103"]
    assert not (tmp_path / "data").exists()
    with corpus.connect(db) as conn:
        assert corpus.events_for_case(conn, CASE) == []
    assert "2 not opened (moment switched off)" in report.summary_line()
    assert "Developer" not in json.dumps(report.as_json())


def test_the_pass_opens_then_resolves_and_the_records_validate(
    tmp_path: Path, switched_on: None
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _store(db, CASE, BRIEFED)
    # The member docket repeats the lead's motion, which stays the lead's event.
    _store(db, "cand/103", BRIEFED)

    first = run_pass(db, data, _watchlist(), today=TODAY)
    assert first.opened == [(CASE, DISMISSAL), (CASE, JUDGMENT)]
    assert first.resolved == [] and first.would_open == []
    case = CasePaths(data, "cand", 100)
    event = read_model(case.event(DISMISSAL).event_file, PredictableEvent)
    assert (event.stage, event.moment, event.opened_at, event.resolved) == (
        "trial",
        "trial-dismissal",
        SWITCHED_ON,
        False,
    )
    assert not (data / "cases" / "cand" / "103").exists()
    assert_valid(data)

    # A second pass over the same docket writes nothing again.
    again = run_pass(db, data, _watchlist(), today=TODAY)
    assert again.opened == [] and again.resolved == [] and again.triage == []

    final = entry(90, FINAL["description"], "2026-11-20")
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(
            conn, CASE, date(2026, 11, 20), {"docket_entries": [*BRIEFED, GRANTED, final]}
        )
    later = date(2026, 11, 21)
    second = run_pass(db, data, _watchlist(), today=later)
    assert second.resolved == [(CASE, DISMISSAL), (CASE, JUDGMENT)]
    assert second.opened == []
    outcome = read_model(case.event(DISMISSAL).outcome, Outcome)
    assert (outcome.trial_ruling, outcome.resolved_at) == ("granted", date(2026, 7, 20))
    assert read_model(case.event(DISMISSAL).event_file, PredictableEvent).resolved
    assert read_model(case.event(JUDGMENT).outcome, Outcome).trial_judgment == "defendant"
    with corpus.connect(db) as conn:
        assert all(e.resolved for e in corpus.events_for_case(conn, CASE))
    assert_valid(data)

    # Resolved once: a later pass neither reopens nor rewrites.
    third = run_pass(db, data, _watchlist(), today=later)
    assert third.opened == [] and third.resolved == [] and third.triage == []


def test_the_pass_lists_triage_and_an_adjudication_settles_it(
    tmp_path: Path, switched_on: None
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _store(db, CASE, BRIEFED)
    run_pass(db, data, _watchlist(), today=TODAY)
    opinion = entry(70, "MEMORANDUM OPINION re 45 Motion to Dismiss.", "2026-07-20")
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(
            conn, CASE, date(2026, 11, 10), {"docket_entries": [*BRIEFED, opinion]}
        )

    held = run_pass(db, data, _watchlist(), today=TODAY)
    assert [(t.case_id, t.event_id, t.entries) for t in held.triage] == [(CASE, DISMISSAL, (70,))]
    assert held.resolved == []
    assert held.as_json()["triage"][0]["entries"] == [70]
    assert not CasePaths(data, "cand", 100).event(DISMISSAL).outcome.exists()

    settled = run_pass(
        db, data, _watchlist(), today=TODAY, adjudicated={(CASE, DISMISSAL): _adjudication()}
    )
    assert settled.resolved == [(CASE, DISMISSAL)] and settled.triage == []
    outcome = read_model(CasePaths(data, "cand", 100).event(DISMISSAL).outcome, Outcome)
    assert (outcome.trial_ruling, outcome.source) == (
        "granted-in-part",
        "docket entry 71 (adjudicated)",
    )


def test_a_member_waits_for_its_lead_and_an_unwritten_event_is_written_again(
    tmp_path: Path, switched_on: None
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _store(db, "cand/103", BRIEFED)
    held = run_pass(db, data, _watchlist(), today=TODAY)
    assert held.opened == [] and held.held_for_lead == ["cand/103"]
    assert held.as_json()["held_for_lead"] == ["cand/103"]

    _store(db, CASE, BRIEFED)
    run_pass(db, data, _watchlist(), today=TODAY)
    file = CasePaths(data, "cand", 100).event(DISMISSAL).event_file
    before = file.read_text(encoding="utf-8")
    file.unlink()
    again = run_pass(db, data, _watchlist(), today=TODAY)
    assert again.opened == [] and again.held_for_lead == []
    assert file.read_text(encoding="utf-8") == before


def test_a_docket_the_pass_fails_on_is_recorded_and_the_rest_are_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _store(db, CASE, BRIEFED)
    _store(db, "cand/103", [MOTION])
    planned = trial_events.plan_docket

    def failing(case_id: str, *args: Any, **kw: Any) -> Any:
        if case_id == CASE:
            raise RuntimeError("MOTION to Dismiss filed by Developer, Inc.")
        return planned(case_id, *args, **kw)

    monkeypatch.setattr(trial_events, "plan_docket", failing)
    report = run_pass(db, tmp_path / "data", _watchlist(), today=TODAY)
    assert report.failed == {CASE: "RuntimeError"}
    assert report.dockets_read == [CASE, "cand/103"]
    assert "1 docket(s) failed" in report.summary_line()
    assert "Developer" not in json.dumps(report.as_json())


# --- the command --------------------------------------------------------------


class _Quiet:
    """A CourtListener client whose every docket read fails: the pass still runs."""

    def get(self, *_a: Any, **_k: Any) -> Any:
        raise AssertionError("not reached")


def test_the_refresh_command_runs_the_pass_and_reports_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config"
    shutil.copytree(Path(__file__).resolve().parents[1] / "config", config)
    (config / "ai-watchlist.yaml").write_text(
        json.dumps(_watchlist().model_dump(mode="json")), encoding="utf-8"
    )
    (config / TRIAL_ADJUDICATIONS_FILENAME).write_text("adjudications: []\n", encoding="utf-8")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _store(db, CASE, BRIEFED)
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")
    monkeypatch.setattr("fedcourtsai.cli._client", lambda _lane, **_w: nullcontext(_Quiet()))
    monkeypatch.setattr(
        "fedcourtsai.pipeline.watchlist_refresh.refresh_watchlist",
        lambda *_a, **_k: WatchlistRefreshReport(),
    )
    out = tmp_path / "report.json"

    result = CliRunner().invoke(app, ["watchlist-refresh", "--report", str(out)])

    assert result.exit_code == 0, result.output
    assert "1 docket(s) read, 0 opened, 0 resolved, 0 to triage, 2 not opened" in result.output
    trial = json.loads(out.read_text(encoding="utf-8"))["trial"]
    assert trial["would_open"] == [
        {"case_id": CASE, "event_id": DISMISSAL},
        {"case_id": CASE, "event_id": JUDGMENT},
    ]
    assert trial["opened"] == [] and trial["dockets_missing"] == ["cand/103"]
    assert not (tmp_path / "data" / "cases").exists()

    def failing(*_a: Any, **_k: Any) -> Any:
        raise RuntimeError("docket text")

    monkeypatch.setattr(trial_events, "plan_docket", failing)
    failed = CliRunner().invoke(app, ["watchlist-refresh", "--report", str(out)])
    assert failed.exit_code == 0, failed.output
    assert "trial pass failed on cand/100: RuntimeError" in failed.output
    assert "docket text" not in failed.output
    assert json.loads(out.read_text(encoding="utf-8"))["trial"]["failed"] == {CASE: "RuntimeError"}

    (config / TRIAL_ADJUDICATIONS_FILENAME).unlink()
    refused = CliRunner().invoke(app, ["watchlist-refresh"])
    assert refused.exit_code != 0
