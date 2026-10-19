"""The scored-figure set-aside: its reasons, its registry, the pass, and the sensitivity lines.

The rule lives in :mod:`fedcourtsai.set_aside`; :func:`fedcourtsai.store.stratify`
applies it, and the boards publish the ``set_aside`` block with the sensitivity
figures beside the defaults it moved.
"""

from __future__ import annotations

import importlib.util
import json
import re
from datetime import UTC, date, datetime
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import ValidationError

from fedcourtsai import ops, set_aside
from fedcourtsai.claim_metrics import (
    build_claim_scores,
    claim_set_aside_sensitivity,
    claim_surface_set_aside,
)
from fedcourtsai.integrity import FORWARD, RETROSPECTIVE, StratifiedCell
from fedcourtsai.leaderboard import (
    build_leaderboard,
    leaderboard_set_aside_sensitivity,
    set_aside_record,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cert_signals
from fedcourtsai.process_version import window_of
from fedcourtsai.schemas import (
    DocketPollRecord,
    Engine,
    EventKind,
    ModelUsage,
    Moment,
    Outcome,
    Prediction,
    PredictionContext,
    PreDistributionSetAsideEvent,
    SetAsideEvent,
    Stage,
    UsageRole,
)
from fedcourtsai.serialize import write_json
from fedcourtsai.store import SetAsideCell, stratify
from tests.test_claim_metrics import _block
from tests.test_claim_metrics import _evaluation as _claim_evaluation
from tests.test_leaderboard import _evaluation, _write_cell

#: The sentence of a declaring entry that lists the set-aside events, and its end.
_LISTING_MARK = "set_aside_events.json` lists"
_LISTING_END = ". "

APPLICATION = "scotus/9526000447"
MOTION = "evt-motion-disposition"


def _context(mode: str = "forward") -> PredictionContext:
    return PredictionContext(mode=mode, snapshot_date=date(2026, 10, 1), signals_observable=True)


def _prediction(at: datetime, *, mode: str = "forward") -> Prediction:
    return Prediction(
        case_id=APPLICATION,
        event_id=MOTION,
        predictor_id="claude-baseline",
        engine=Engine.claude_code,
        run_id="p1",
        created_at=at,
        input_snapshot="corpus",
        granted=0,
        probability=0.2,
        predicted_disposition="denied",
        context=_context(mode),
    )


def _outcome(resolved_at: date) -> Outcome:
    return Outcome.model_validate(
        dict(
            case_id=APPLICATION,
            event_id=MOTION,
            resolved_at=resolved_at,
            actual_disposition="denied",
            actual_granted=0,
        )
    )


# --- the interim reason ----------------------------------------------------------


@pytest.mark.parametrize(
    ("at", "poll", "stage", "mode", "expected"),
    [
        # 26A447: run at about 21:30Z on the decision day, before the poll existed.
        (datetime(2026, 10, 2, 21, 24, tzinfo=UTC), None, Stage.interim, "forward", True),
        # A poll that could not answer leaves the ordering unresolvable.
        (datetime(2026, 10, 2, 21, 24, tzinfo=UTC), "unavailable", Stage.interim, "forward", True),
        # An open pre-mint poll is the one record that shows the cell began first.
        (datetime(2026, 10, 2, 21, 24, tzinfo=UTC), "open", Stage.interim, "forward", False),
        # After the decision day, unpolled.
        (datetime(2026, 10, 3, 15, 0, tzinfo=UTC), None, Stage.interim, "forward", True),
        # 01:13Z on the decision day is the evening before in Court time: forward.
        (datetime(2026, 10, 2, 1, 13, tzinfo=UTC), None, Stage.interim, "forward", False),
        # The day before.
        (datetime(2026, 10, 1, 18, 0, tzinfo=UTC), None, Stage.interim, "forward", False),
        # Only forward interim cells: cert is the listed reason's, replay claims nothing.
        (datetime(2026, 10, 2, 21, 24, tzinfo=UTC), None, Stage.cert, "forward", False),
        (datetime(2026, 10, 2, 21, 24, tzinfo=UTC), None, Stage.interim, "replay", False),
    ],
)
def test_interim_decision_day_reads_the_cell_clock_in_court_time(
    at: datetime, poll: str | None, stage: Stage, mode: str, expected: bool
) -> None:
    prediction = _prediction(at, mode=mode)
    outcome = _outcome(date(2026, 10, 2))
    assert set_aside.interim_decision_day(prediction, outcome, stage, lambda: poll) is expected
    reason = set_aside.set_aside_reason(
        APPLICATION, MOTION, prediction, outcome, stage, lambda: poll
    )
    assert reason == ("interim-decision-day" if expected else None)


def test_the_poll_is_read_only_for_a_cell_the_timing_test_caught() -> None:
    reads: list[str] = []

    def poll() -> str | None:
        reads.append("read")
        return None

    early = _prediction(datetime(2026, 10, 1, 18, 0, tzinfo=UTC))
    assert (
        set_aside.set_aside_reason(
            APPLICATION, MOTION, early, _outcome(date(2026, 10, 2)), Stage.interim, poll
        )
        is None
    )
    assert reads == []


# --- the listed reason and its registry --------------------------------------


def _listed(case_id: str, event_id: str = "evt-petition-disposition") -> SetAsideEvent:
    return SetAsideEvent(
        case_id=case_id,
        event_id=event_id,
        reason="post-conference-first-forecast",
        conference=date(2026, 9, 28),
        first_forward_run_id="20261004T201824Z",
        declared=date(2026, 10, 16),
    )


def _registry(*rows: SetAsideEvent | PreDistributionSetAsideEvent) -> str:
    return json.dumps(
        {"schema_version": "1.0", "events": [row.model_dump(mode="json") for row in rows]}
    )


def test_the_registry_refuses_an_event_listed_twice() -> None:
    row = _listed("scotus/1")
    with pytest.raises(ValueError, match="twice"):
        set_aside.load_set_aside_events(_registry(row, row))


def test_the_registry_admits_only_a_listed_reason() -> None:
    raw = json.loads(_registry(_listed("scotus/1")))
    raw["events"][0]["reason"] = "interim-decision-day"
    with pytest.raises(ValidationError):
        set_aside.load_set_aside_events(json.dumps(raw))


def test_a_listed_event_is_set_aside_whatever_its_timing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        set_aside,
        "SET_ASIDE_EVENTS",
        {("scotus/1", "evt-petition-disposition"): _listed("scotus/1")},
    )
    early = _prediction(datetime(2026, 10, 4, 20, 18, tzinfo=UTC))
    assert (
        set_aside.set_aside_reason(
            "scotus/1",
            "evt-petition-disposition",
            early,
            _outcome(date(2026, 10, 5)),
            Stage.cert,
            lambda: None,
        )
        == "post-conference-first-forecast"
    )


def _pre_distribution(case_id: str) -> PreDistributionSetAsideEvent:
    return PreDistributionSetAsideEvent(
        case_id=case_id,
        event_id="evt-petition-disposition",
        reason="pre-distribution-mint",
        minted_run_id="20261006T142731Z",
        declared=date(2026, 10, 19),
    )


def test_the_registry_reads_each_row_by_its_reason() -> None:
    listed = set_aside.load_set_aside_events(
        _registry(_listed("scotus/1"), _pre_distribution("scotus/2"))
    )
    assert isinstance(listed[("scotus/1", "evt-petition-disposition")], SetAsideEvent)
    row = listed[("scotus/2", "evt-petition-disposition")]
    assert isinstance(row, PreDistributionSetAsideEvent)
    assert row.minted_run_id == "20261006T142731Z"


def test_a_pre_distribution_row_carries_its_own_fields_only() -> None:
    raw = json.loads(_registry(_pre_distribution("scotus/2")))
    raw["events"][0]["conference"] = "2026-09-28"
    with pytest.raises(ValidationError):
        set_aside.load_set_aside_events(json.dumps(raw))
    del raw["events"][0]["conference"], raw["events"][0]["minted_run_id"]
    with pytest.raises(ValidationError):
        set_aside.load_set_aside_events(json.dumps(raw))


def test_a_pre_distribution_event_is_set_aside_with_its_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        set_aside,
        "SET_ASIDE_EVENTS",
        {("scotus/2", "evt-petition-disposition"): _pre_distribution("scotus/2")},
    )
    cell = _prediction(datetime(2026, 10, 6, 14, 54, tzinfo=UTC))
    assert (
        set_aside.set_aside_reason(
            "scotus/2",
            "evt-petition-disposition",
            cell,
            _outcome(date(2026, 10, 20)),
            Stage.cert,
            lambda: None,
        )
        == "pre-distribution-mint"
    )


def _listed_run(event: object) -> str:
    if isinstance(event, PreDistributionSetAsideEvent):
        return event.minted_run_id
    assert isinstance(event, SetAsideEvent)
    return event.first_forward_run_id


@pytest.mark.reads_data
def test_every_listed_event_names_a_committed_event_and_its_first_forward_run() -> None:
    for (case_id, event_id), event in set_aside.SET_ASIDE_EVENTS.items():
        base = Path("data/cases") / case_id / "events" / event_id
        assert (base / "event.yaml").is_file(), (case_id, event_id)
        run_id = _listed_run(event)
        assert list(base.glob(f"predictions/*/{run_id}/prediction.json")), (case_id, run_id)


@pytest.mark.reads_data
def test_every_pre_distribution_row_names_forward_frozen_cells_minted_undistributed() -> None:
    # The committed half of the row's fact: the run it names holds forward,
    # frozen-scope cells whose provisioned context counted no petition
    # distribution. The corpus half (an ancillary paper was distributed by the
    # run day) is the declaring entry's census.
    rows = [
        event
        for event in set_aside.SET_ASIDE_EVENTS.values()
        if isinstance(event, PreDistributionSetAsideEvent)
    ]
    assert rows, "no pre-distribution-mint row is listed"
    for event in rows:
        base = Path("data/cases") / event.case_id / "events" / event.event_id
        cells = sorted(base.glob(f"predictions/*/{event.minted_run_id}/prediction.json"))
        assert cells, (event.case_id, event.minted_run_id)
        for path in cells:
            prediction = Prediction.model_validate_json(path.read_text(encoding="utf-8"))
            assert prediction.context is not None, path
            assert prediction.context.mode == "forward", path
            assert prediction.context.distribution_count == 0, path
            assert window_of(prediction.process_version) is not None, path


def _freeze_entries() -> list[str]:
    text = Path("docs/freeze-record.md").read_text(encoding="utf-8")
    return [" ".join(("- **" + entry).split()) for entry in text.split("\n- **")[1:]]


@pytest.mark.reads_docs
def test_every_listed_event_is_declared_by_its_own_dated_freeze_record_entry() -> None:
    # Each row must point at a landed entry that names the event — case and
    # event together — and carries the row's date in its own heading, so a row
    # appended later owes an entry of its own.
    entries = _freeze_entries()
    for (case_id, event_id), event in set_aside.SET_ASIDE_EVENTS.items():
        named = [
            entry
            for entry in entries
            if f"`{case_id}` `{event_id}`" in entry
            and entry.split(".**", 1)[0].endswith(event.declared.isoformat())
        ]
        assert named, (case_id, event_id, event.declared)


@pytest.mark.reads_docs
def test_every_event_a_listing_entry_names_is_still_listed() -> None:
    # The reverse direction: a listed event whose row left the registry would
    # put back gradings a dated entry set aside.
    listed = {f"`{case_id}` `{event_id}`" for case_id, event_id in set_aside.SET_ASIDE_EVENTS}
    declaring = [entry for entry in _freeze_entries() if _LISTING_MARK in entry]
    assert declaring, "the freeze record lists no set-aside event"
    for entry in declaring:
        listing = entry.split(_LISTING_MARK, 1)[1].split(_LISTING_END, 1)[0]
        named = set(re.findall(r"`scotus/\d+` `evt-[a-z0-9-]+`", listing))
        assert named, entry[:200]
        assert named <= listed, sorted(named - listed)


# --- the pass ----------------------------------------------------------------


def _interim_cell(data_root: Path, *, poll: str | None) -> None:
    ev = _evaluation("claude-baseline", case_id=APPLICATION, event_id=MOTION)
    _write_cell(
        data_root,
        ev,
        predicted_at=datetime(2026, 10, 2, 21, 24, tzinfo=UTC),
        resolved_at=date(2026, 10, 2),
        kind=EventKind.motion,
        stage=Stage.interim,
        context=_context(),
    )
    if poll is not None:
        usage = ModelUsage(
            case_id=APPLICATION,
            event_id=MOTION,
            run_id="p1",
            role=UsageRole.predictor,
            actor_id="claude-baseline",
            engine=Engine.claude_code,
            model="claude-fable-5",
            created_at=datetime(2026, 10, 2, 21, 30, tzinfo=UTC),
            input_tokens=1,
            output_tokens=1,
            estimated_cost_usd=0.0,
            pre_mint_poll=DocketPollRecord(
                polled_at=datetime(2026, 10, 2, 21, 20, tzinfo=UTC),
                docket_number="26A447",
                state=poll,
            ),
        )
        court, _, docket = APPLICATION.partition("/")
        write_json(
            CasePaths(data_root, court, int(docket))
            .event(MOTION)
            .prediction_usage("claude-baseline", "p1"),
            usage,
        )


def test_stratify_sets_a_decision_day_cell_aside_with_its_stratum(tmp_path: Path) -> None:
    _interim_cell(tmp_path, poll=None)
    run = stratify(tmp_path, frozen_only=False)
    assert run.cells == []
    ((cell, reason),) = run.set_aside
    assert reason == "interim-decision-day"
    # The same-day tie already reads retrospective; the set-aside keeps it.
    assert cell[1] == RETROSPECTIVE and cell[2] == Stage.interim
    assert list(run.sensitivity_cells()) == [cell]
    # The Release 1 computation keeps it in.
    kept = stratify(tmp_path, frozen_only=False, apply_set_aside=False)
    assert [c[0] for c in kept.cells] == [cell[0]] and not kept.set_aside


def test_an_open_pre_mint_poll_keeps_the_cell_in_the_default(tmp_path: Path) -> None:
    _interim_cell(tmp_path, poll="open")
    run = stratify(tmp_path, frozen_only=False)
    assert len(run.cells) == 1 and run.set_aside == []
    assert run.sensitivity_cells() == run.cells


# --- the boards' sensitivity lines --------------------------------------------


def _cert(predictor: str, event: str, *, correct: int, brier: float) -> StratifiedCell:
    ev = _evaluation(
        predictor,
        case_id="scotus/9026000066",
        event_id=event,
        correct=correct,
        brier_score=brier,
    )
    return (ev, FORWARD, Stage.cert, Moment.distribution)


def test_the_leaderboard_publishes_the_default_and_the_reading_with_them_counted() -> None:
    kept = _cert("alpha", "evt-a", correct=1, brier=0.01)
    aside = _cert("alpha", "evt-b", correct=0, brier=0.81)
    cells = [kept, aside]
    held = [SetAsideCell(aside, "post-conference-first-forecast")]
    default = build_leaderboard([kept])
    sensitivity = leaderboard_set_aside_sensitivity(held, build_leaderboard(cells))
    assert sensitivity is not None
    (line,) = sensitivity.lines
    assert (line.population, line.predictor_id, line.stratum, line.set_aside) == (
        "cert@distribution",
        "alpha",
        "forward",
        1,
    )
    assert default.entries[0].forward is not None
    assert default.entries[0].forward.evaluations == 1
    assert line.including.evaluations == 2
    assert line.including.accuracy == pytest.approx(0.5)
    # A ranked-board set-aside carries the paired figure too.
    assert sensitivity.paired is not None
    record = set_aside_record(held)
    assert record is not None
    assert record.by_reason == {"post-conference-first-forecast": 1}
    assert record.events == ["scotus/9026000066 evt-b post-conference-first-forecast"]


def test_nothing_set_aside_publishes_no_block() -> None:
    assert set_aside_record([]) is None
    assert leaderboard_set_aside_sensitivity([], build_leaderboard([])) is None


def test_the_claim_surface_lines_only_its_own_population() -> None:
    kept = (
        _claim_evaluation("alpha", event_id="evt-a", claim_scores=_block(0.4)),
        FORWARD,
        Stage.cert,
        Moment.distribution,
    )
    aside = (
        _claim_evaluation("alpha", event_id="evt-b", claim_scores=_block(-0.6)),
        FORWARD,
        Stage.cert,
        Moment.distribution,
    )
    interim = (
        _claim_evaluation("alpha", event_id="evt-c"),
        RETROSPECTIVE,
        Stage.interim,
        Moment.arrival,
    )
    held = [
        SetAsideCell(aside, "post-conference-first-forecast"),
        SetAsideCell(interim, "interim-decision-day"),
    ]
    lines = claim_set_aside_sensitivity(held, build_claim_scores([kept, aside, interim]))
    # The surface's record counts its own population only: the interim cell set
    # aside on the leaderboard's stage blocks was never on this surface.
    record = set_aside_record(claim_surface_set_aside(held))
    assert record is not None
    assert record.excluded == 1
    assert record.by_reason == {"post-conference-first-forecast": 1}
    (line,) = lines
    assert (line.predictor_id, line.stratum, line.set_aside) == ("alpha", "forward", 1)
    assert line.including is not None and line.including.events == 2


# --- the relist carve-out ----------------------------------------------------


def _docket(*entries: tuple[str, str]) -> dict[str, object]:
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


def test_a_relist_docketed_by_the_run_day_keeps_the_petition_forward() -> None:
    relisted = _docket(
        ("Jul 01 2026", "DISTRIBUTED for Conference of 9/28/2026."),
        ("Sep 30 2026", "DISTRIBUTED for Conference of 10/9/2026."),
    )
    assert cert_signals.relisted_past(relisted, date(2026, 10, 3))
    # Date-dependent: run before the relist was docketed, it reads the
    # conference that sat.
    assert not cert_signals.relisted_past(relisted, date(2026, 9, 29))
    # A first distribution still ahead is no relist.
    ahead = _docket(("Jul 01 2026", "DISTRIBUTED for Conference of 10/9/2026."))
    assert not cert_signals.relisted_past(ahead, date(2026, 10, 3))


# --- the corpus-check census --------------------------------------------------


def _census_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "checks" / "post_conference_census.py"
    spec = importlib.util.spec_from_file_location("post_conference_census", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_census_reconciles_with_the_listed_rows() -> None:
    census = _census_module()
    rows = [
        {
            "case_id": "scotus/1",
            "event_id": "evt-petition-disposition",
            "considering_conference": "2026-09-28",
            "first_forward_run_id": "20261004T201824Z",
            "resolved": True,
            "graded_cells": 9,
        },
        {
            "case_id": "scotus/2",
            "event_id": "evt-petition-disposition",
            "considering_conference": "2026-10-09",
            "first_forward_run_id": "20261010T150000Z",
            "resolved": False,
            "graded_cells": 0,
        },
    ]
    unreadable = [{"case_id": "scotus/4", "event_id": "e", "reason": "no live payload"}]
    listed = {("scotus/1", "evt-petition-disposition"), ("scotus/3", "evt-petition-disposition")}
    text = census.render(rows, unreadable, listed, [("scotus/5", "evt-petition-disposition")])
    assert "- census events: 2 (1 resolved, 1 with graded cells, 9 graded cells)" in text
    assert "- census events not listed (rows owed): 1" in text
    assert "- listed events the census does not find: 1" in text
    assert "- `scotus/3` `evt-petition-disposition`" in text
    assert "- `scotus/4` `e`: no live payload" in text
    assert "- events kept in by a relist docketed by the first cell's run day: 1" in text


def test_the_ops_report_prints_the_set_aside_count() -> None:
    held = [SetAsideCell(_cert("alpha", "evt-b", correct=0, brier=0.81), "interim-decision-day")]
    digest = ops.summarize_substance(
        cell_counts=(1, 1, 1), stratified_evaluations=[], set_aside=set_aside_record(held)
    )
    text = ops.render_substance(digest)
    assert "Set aside: **1** graded cell(s)" in text
    assert "1 interim-decision-day" in text
    # A board the set-aside emptied is not the shakedown state.
    assert "No frozen-process evaluations yet" not in text
