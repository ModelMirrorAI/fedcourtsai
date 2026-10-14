"""The event void: its registry, its freeze-record linkage, and every reader it reaches.

The void's predicate lives in :mod:`fedcourtsai.voids`; the scored boards'
exclusion is pinned in ``tests/test_leaderboard.py``, the export's in
``tests/test_dataset_export.py`` and the backlog's in
``tests/test_evaluate_backlog.py``. This file holds what is specific to the
registry and the readers outside those three.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai import ops, voids
from fedcourtsai.matrix import CaseRequest, evaluate_matrix
from fedcourtsai.schemas import Engine, VoidedEvent, VoidedEventsRecord
from fedcourtsai.tool_usage import build_tool_usage
from fedcourtsai.window_records import successor_disclosures
from tests.conftest import seed_prediction, set_windows
from tests.test_tool_usage import _cell as _tool_cell
from tests.test_window_records import BETA, CLOSED, SUCCESSOR, T2, _ledger

EVALUATORS = Path("config/evaluators.yaml")

#: How a voiding entry's heading opens, so the reverse check below can find every
#: void the freeze record declares.
_VOID_HEADING = "- **An event whose docket number the Court re-docketed is voided"


def _voided(case_id: str, event_id: str = "evt-petition-disposition") -> VoidedEvent:
    return VoidedEvent(
        case_id=case_id,
        event_id=event_id,
        ground="redocketed",
        detection="outcome-triggered",
        declared=date(2026, 10, 14),
        defect="a docket number re-docketed in a test",
    )


def _void(monkeypatch: pytest.MonkeyPatch, *keys: tuple[str, str]) -> None:
    monkeypatch.setattr(voids, "VOIDED_EVENTS", {key: _voided(*key) for key in keys})


def _registry(*rows: dict[str, str]) -> str:
    return json.dumps({"schema_version": "1.0", "events": list(rows)})


_ROW = {
    "case_id": "scotus/1",
    "event_id": "evt-petition-disposition",
    "ground": "redocketed",
    "detection": "scan",
    "declared": "2026-10-14",
    "defect": "a test",
}


# --- the registry --------------------------------------------------------------


def test_the_registry_refuses_an_event_registered_twice() -> None:
    with pytest.raises(ValueError, match="twice"):
        voids.load_voided_events(_registry(_ROW, _ROW))


def test_the_registry_refuses_malformed_json() -> None:
    with pytest.raises(ValidationError):
        voids.load_voided_events("{not json")


@pytest.mark.parametrize(
    "field, value",
    [
        ("case_id", "9026000221"),  # no court
        ("case_id", "scotus/26-221"),  # a docket number, not an id
        ("event_id", "petition-disposition"),  # no evt- prefix
        ("ground", "bad-forecast"),  # not a ground the rule admits
        ("detection", "manual"),
    ],
)
def test_the_registry_refuses_a_row_outside_its_vocabulary(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        voids.load_voided_events(_registry({**_ROW, field: value}))


def test_the_predicate_reads_the_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    _void(monkeypatch, ("scotus/1", "evt-petition-disposition"))
    assert voids.is_voided("scotus/1", "evt-petition-disposition")
    assert not voids.is_voided("scotus/1", "evt-petition-arrival-disposition")
    assert not voids.is_voided("scotus/2", "evt-petition-disposition")


@pytest.mark.reads_data
def test_every_voided_event_names_a_committed_event_directory() -> None:
    # A row naming an event the ledger does not hold voids nothing, and would
    # hide a typo in a pre-registration record.
    for case_id, event_id in voids.VOIDED_EVENTS:
        assert (Path("data/cases") / case_id / "events" / event_id / "event.yaml").is_file(), (
            case_id,
            event_id,
        )


# --- the freeze record ---------------------------------------------------------


def _freeze_entries() -> list[str]:
    """The freeze record's top-level entries, each with its whitespace collapsed."""
    text = Path("docs/freeze-record.md").read_text(encoding="utf-8")
    return [" ".join(("- **" + entry).split()) for entry in text.split("\n- **")[1:]]


@pytest.mark.reads_docs
def test_every_voided_event_is_declared_by_its_own_dated_freeze_record_entry() -> None:
    # A void de-counts gradings, so each registry row must point at a landed
    # entry that names the event and carries the row's date in its own heading,
    # not a date found anywhere in the file.
    entries = _freeze_entries()
    for (case_id, event_id), event in voids.VOIDED_EVENTS.items():
        named = [entry for entry in entries if f"`{case_id}` `{event_id}`" in entry]
        assert named, (case_id, event_id)
        heading = named[0].split(".**", 1)[0]
        assert heading.endswith(event.declared.isoformat()), (heading, event.declared)


@pytest.mark.reads_docs
def test_every_void_the_freeze_record_declares_is_still_registered() -> None:
    # The reverse direction: a voiding entry whose row left the registry would
    # re-count gradings the dated entry withdrew.
    registered = {f"`{case_id}` `{event_id}`" for case_id, event_id in voids.VOIDED_EVENTS}
    declared = [entry for entry in _freeze_entries() if entry.startswith(_VOID_HEADING)]
    assert declared, "the freeze record declares no void"
    for entry in declared:
        assert any(key in entry for key in registered), entry[:200]


# --- the readers outside the scored boards ------------------------------------


def test_the_closed_windows_record_drops_a_voided_events_gradings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The closed window held two counted gradings (scotus/1 and scotus/2); voiding
    # scotus/1's event leaves one, and the instant it was graded after is unmoved.
    set_windows(monkeypatch, CLOSED, SUCCESSOR, BETA)
    data = tmp_path / "data"
    _ledger(data)
    _void(monkeypatch, ("scotus/1", "evt-petition-disposition"))

    report = successor_disclosures(data, closed_label="proc-a", successor_label="proc-b")

    assert report.instant == T2
    (judge,) = report.evaluator_digests
    assert (judge.evaluator_id, judge.gradings, judge.graded_after_instant) == ("e1", 1, 1)


def test_the_ops_report_carries_the_voided_record_and_omits_it_when_empty() -> None:
    record = VoidedEventsRecord(
        excluded=2,
        events=["scotus/1 evt-petition-disposition"],
        by_predictor={"alpha": 2},
        correct_by_predictor={"alpha": 0},
        mean_brier_by_predictor={"alpha": 0.5},
    )
    digest = ops.summarize_substance(
        cell_counts=(1, 1, 1), stratified_evaluations=[], voided_events=record
    )
    assert digest.voided_events == record
    empty = ops.summarize_substance(cell_counts=(1, 1, 1), stratified_evaluations=[])
    assert "voided_events" not in json.loads(empty.model_dump_json())


def test_the_usefulness_join_drops_a_voided_events_gradings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for docket in ("1", "2"):
        _tool_cell(
            tmp_path,
            docket=docket,
            predictor="claude-baseline",
            engine=Engine.claude_code,
            calls=4,
            brier=0.16,
        )
    before = build_tool_usage(tmp_path, frozen_only=False).usefulness
    assert before is not None and before.joined_cells == 2

    _void(monkeypatch, ("scotus/1", "evt-petition-disposition"))

    after = build_tool_usage(tmp_path, frozen_only=False).usefulness
    assert after is not None and after.joined_cells == 1


def test_the_evaluate_matrix_mints_no_cell_on_a_voided_event(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Every route into an evaluate cell goes through the fan-out: an explicit
    # body, a manual dispatch whose events resolve to the case's, or the backlog.
    data = tmp_path / "data"
    for docket in (1, 2):
        seed_prediction(data, "scotus", docket, "evt-petition-disposition")
    cases = [
        CaseRequest(court="scotus", docket=docket, events=("evt-petition-disposition",))
        for docket in (1, 2)
    ]
    _void(monkeypatch, ("scotus/1", "evt-petition-disposition"))

    minted = evaluate_matrix(EVALUATORS, cases, "RID", data_root=data)

    assert {cell["docket"] for cell in minted["include"]} == {2}
