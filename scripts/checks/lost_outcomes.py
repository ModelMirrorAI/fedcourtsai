"""Size the lost-outcome pass and check what the outcome-writer changes move.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/lost_outcomes.py
    ```

it runs over the corpus the lane pulled and the ledger at the checkout, and
appends counts and case identifiers — never stored snapshot text — to the file
named by `CHECK_SUMMARY`:

0. **The decided population**: every declared moment on a selected row whose
   stage the row records decided (corpus-resolved, or open on the decided row),
   by disposition, and how many already carry a complete ledger pair.
1. **The outcome pass, dry-run** (`record_lost_outcomes`): the gap population;
   the outcomes it would write (gap moments and the open siblings resolved with
   them, counted apart) by disposition; the merits mints a recorded grant
   implies, split minted-pending / judgment-latched / terminated / stale /
   out-of-scope; the residue it would mark and the open gaps it would leave
   open, each by disposition, with a reason x disposition cross-tab; and the
   cases it holds back because a gap stage carries a committed prediction.
2. **The standing convergence's open-gap arm**: open declared moments on
   selected rows whose stage the row records decided, with no ledger outcome,
   split by whether the stage carries a committed prediction and whether the
   decision is inside the lookback.
3. **Predicted events closed without an outcome**: committed predictions whose
   event the corpus records resolved with no `outcome.json`, selected and
   unselected rows apart.
4. **Exposure to the side-motion misreading** (read-only, no re-parse): the
   selected application rows, and the committed interim outcomes, whose stored
   live proceedings carry an entry in the shape the registered interim reader
   can take for the application's own disposition — a motion's order naming the
   application in its sentence.
5. **Opened after the decision**: committed outcomes whose event opened after
   the outcome's `resolved_at` (ledger-only), by disposition.
6. **The merits split of the grants the apply recorded**: the pass is a
   dry-run over gaps, so once applied it no longer sees them. For each case
   whose cert grant the apply commit recorded (listed in
   `lost_outcomes_applied_grants.json`, read from that commit's diff), the
   corpus's merits event and the row's merits ladder as the pass reads it —
   carries a merits event / judgment-latched / terminated / stale (on the
   apply's date) / none of these. The last bucket holds the out-of-scope
   grants and any grant the pass would have minted; the row is read at the
   pulled vintage, not the apply's.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline import outcome as outcome_module

_MAX_IDS = 40

# A sentence whose subject is a motion and which names an application beside a
# disposing verb: the shape the registered interim reader can read as the
# application's own order. A count of exposure only — nothing is re-parsed.
_SIDE_MOTION_SHAPE = re.compile(
    r"(?:^|\.\s*)(?:the\s+)?(?:[a-z-]+\s+){0,2}?motions?\b[^.]{0,300}?\bapplications?\b"
    r"[^.]{0,200}?\b(?:granted|denied|dismissed|withdrawn)\b",
    re.IGNORECASE,
)


def _ids(values: list[str]) -> str:
    shown = sorted(values)[:_MAX_IDS]
    more = f" (+{len(values) - _MAX_IDS} more)" if len(values) > _MAX_IDS else ""
    return (", ".join(shown) or "-") + more


def _counts(counter: Mapping[str, int]) -> str:
    return ", ".join(f"{k}={v}" for k, v in sorted(counter.items())) or "-"


def _has_prediction(event_dir: Path) -> bool:
    return any((event_dir / "predictions").glob("*/*/prediction.json"))


def _label(row: corpus.CorpusRow | None) -> str:
    return str(row.disposition) if row is not None and row.disposition is not None else "none"


def _event_dir(data_root: Path, case_id: str, event_id: str) -> Path:
    docket = case_id.rsplit("/", 1)[-1]
    return data_root / "cases" / "scotus" / docket / "events" / event_id


def _population_section(conn: Any, data_root: Path) -> list[str]:
    decided: Counter[str] = Counter()
    complete: Counter[str] = Counter()
    for event in corpus.events_on_selected_rows(conn, court="scotus"):
        spec = moments.spec_for(event.event_id)
        if spec is None:
            continue
        row = corpus.get_row(conn, event.case_id)
        if row is None:
            continue
        if not event.resolved and not corpus.stage_shows_decided(row, spec.stage):
            continue
        label = _label(row)
        decided[label] += 1
        event_dir = _event_dir(data_root, event.case_id, event.event_id)
        if (event_dir / "outcome.json").exists() and (event_dir / "event.yaml").exists():
            complete[label] += 1
    return [
        "## 0. Decided declared moments on selected rows",
        "",
        f"- total: {sum(decided.values())}; by disposition: {_counts(decided)}",
        f"- with a complete ledger pair: {sum(complete.values())}; by disposition: "
        + _counts(complete),
        "",
    ]


def _pass_section(db: Path, data_root: Path) -> list[str]:
    plan = outcome_module.record_lost_outcomes(db, data_root)
    with corpus.connect(db) as conn:
        labels = {
            case_id: _label(corpus.get_row(conn, case_id))
            for case_id in set(plan.open_declined) | set(plan.residue)
        }
    residue_reason: Counter[str] = Counter()
    cross: Counter[str] = Counter()
    for case_id, marks in plan.residue.items():
        for reason in marks.values():
            residue_reason[reason] += 1
            cross[f"closed/{reason}/{labels[case_id]}"] += 1
    open_by_label: Counter[str] = Counter()
    for case_id, reasons in plan.open_declined_reasons.items():
        for reason in reasons.values():
            open_by_label[labels[case_id]] += 1
            cross[f"open/{reason}/{labels[case_id]}"] += 1
    merits: Counter[str] = Counter(plan.merits_not_minted.values())
    merits["minted-pending"] = len(plan.merits_minted)
    all_outcomes = sum(len(v) for v in plan.recorded.values())
    gap_outcomes = sum(plan.recorded_by_disposition.values())
    return [
        "## 1. Outcome pass (dry-run)",
        "",
        f"- gap moments in the population: {plan.population}",
        f"- would record {all_outcomes} outcome(s) on {len(plan.recorded)} case(s): "
        + f"{gap_outcomes} gap moment(s), {all_outcomes - gap_outcomes} open sibling(s) "
        + "resolved with them",
        "  - gap moments recorded by disposition: " + _counts(plan.recorded_by_disposition),
        "- merits outcome of each recorded grant that opens a merits proceeding: "
        + _counts(merits),
        "- residue to mark resolved_without_outcome: "
        + f"{sum(len(v) for v in plan.residue.values())} moment(s) on {len(plan.residue)} case(s)",
        "  - by reason: " + _counts(residue_reason),
        "  - by disposition: " + _counts(plan.residue_by_disposition),
        f"- open gaps declined (left open): {sum(len(v) for v in plan.open_declined.values())}"
        + f" on {len(plan.open_declined)} case(s); by disposition: {_counts(open_by_label)}",
        "- reason x disposition (closed residue and open declines): " + _counts(cross),
        f"- held back (gap stage predicted): {len(plan.held_predicted)}: "
        + _ids(plan.held_predicted),
        f"- failed: {len(plan.failed)}: {_ids(list(plan.failed))}",
        f"- cases_written (the apply bound): {plan.cases_written}",
        "",
    ]


def _open_gap_section(conn: Any, data_root: Path, today: date) -> list[str]:
    floor = today.toordinal() - outcome_module.OUTCOME_CONVERGENCE_LOOKBACK_DAYS
    counts: Counter[str] = Counter()
    predicted_ids: list[str] = []
    for event in corpus.events_on_selected_rows(conn, court="scotus"):
        spec = moments.spec_for(event.event_id)
        if event.resolved or spec is None:
            continue
        row = corpus.get_row(conn, event.case_id)
        if row is None or not corpus.stage_shows_decided(row, spec.stage):
            continue
        event_dir = _event_dir(data_root, event.case_id, event.event_id)
        if (event_dir / "outcome.json").exists():
            continue
        decided = outcome_module._stage_decided(row, spec.stage)
        predicted = _has_prediction(event_dir)
        inside = decided is not None and decided.toordinal() >= floor
        counts[
            f"{'predicted' if predicted else 'unpredicted'}/"
            + ("undated" if decided is None else ("in-lookback" if inside else "past-lookback"))
        ] += 1
        if predicted:
            predicted_ids.append(f"{event.case_id} {event.event_id}")
    return [
        "## 2. Open declared moments on decided selected rows, no ledger outcome",
        "",
        f"- total: {sum(counts.values())}; {_counts(counts)}",
        f"- predicted ones: {_ids(predicted_ids)}",
        "",
    ]


def _predicted_closed_section(conn: Any, data_root: Path) -> list[str]:
    closed: dict[bool, list[str]] = {True: [], False: []}
    checked = 0
    for prediction in (data_root / "cases" / "scotus").glob("*/events/*/predictions"):
        event_dir = prediction.parent
        if not _has_prediction(event_dir) or (event_dir / "outcome.json").exists():
            continue
        checked += 1
        case_id = f"scotus/{event_dir.parent.parent.name}"
        row = corpus.get_row(conn, case_id)
        selected = bool(row is not None and row.salience_selected)
        for event in corpus.events_for_case(conn, case_id):
            if event.event_id == event_dir.name and event.resolved:
                closed[selected].append(f"{case_id} {event.event_id}")
    return [
        "## 3. Predicted events the corpus closed without an outcome",
        "",
        f"- predicted events with no outcome.json: {checked}",
        f"- of them corpus-resolved on a selected row: {len(closed[True])}: {_ids(closed[True])}",
        f"- of them corpus-resolved on an unselected row: {len(closed[False])}: "
        + _ids(closed[False]),
        "",
    ]


def _exposed(payload: Mapping[str, Any]) -> bool:
    entries = payload.get("ProceedingsandOrder")
    if not isinstance(entries, list):
        return False
    return any(
        isinstance(entry, Mapping) and _SIDE_MOTION_SHAPE.search(str(entry.get("Text") or ""))
        for entry in entries
    )


def _exposure_section(conn: Any, data_root: Path) -> list[str]:
    selected_rows: list[str] = []
    seen: set[str] = set()
    for event in corpus.events_on_selected_rows(conn, court="scotus"):
        if event.case_id in seen:
            continue
        seen.add(event.case_id)
        row = corpus.get_row(conn, event.case_id)
        if row is None or not corpus.is_scotus_application_form(row.docket_number):
            continue
        snapshot = corpus.latest_snapshot(conn, event.case_id)
        if snapshot is not None and _exposed(snapshot[1]):
            selected_rows.append(event.case_id)
    committed = predicted = 0
    predicted_ids: list[str] = []
    for outcome_path in (data_root / "cases" / "scotus").glob("*/events/*/outcome.json"):
        event_file = outcome_path.parent / "event.yaml"
        if not event_file.exists():
            continue
        definition = yaml.safe_load(event_file.read_text(encoding="utf-8")) or {}
        if definition.get("stage") != "interim":
            continue
        case_id = f"scotus/{outcome_path.parent.parent.parent.name}"
        snapshot = corpus.latest_snapshot(conn, case_id)
        if snapshot is None or not _exposed(snapshot[1]):
            continue
        committed += 1
        if _has_prediction(outcome_path.parent):
            predicted += 1
            predicted_ids.append(f"{case_id} {outcome_path.parent.name}")
    return [
        "## 4. Exposure to the side-motion misreading (registered reading, unchanged)",
        "",
        "- selected application rows whose stored proceedings carry the shape: "
        + f"{len(selected_rows)}: {_ids(selected_rows)}",
        f"- committed interim outcomes on such a docket: {committed}; on a predicted event: "
        + f"{predicted}: {_ids(predicted_ids)}",
        "",
    ]


def _opened_after_section(data_root: Path) -> list[str]:
    by_label: Counter[str] = Counter()
    predicted_refs: list[str] = []
    for outcome_path in (data_root / "cases").glob("*/*/events/*/outcome.json"):
        event_file = outcome_path.parent / "event.yaml"
        if not event_file.exists():
            continue
        event = yaml.safe_load(event_file.read_text(encoding="utf-8")) or {}
        outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
        resolved_at = outcome.get("resolved_at")
        opened_at = event.get("opened_at")
        if opened_at and resolved_at and str(opened_at) > str(resolved_at):
            by_label[str(outcome.get("actual_disposition"))] += 1
            if _has_prediction(outcome_path.parent):
                predicted_refs.append(str(outcome_path.parent.relative_to(data_root)))
    return [
        "## 5. Committed outcomes whose event opened after resolved_at",
        "",
        f"- total: {sum(by_label.values())}; by disposition: {_counts(by_label)}",
        f"- on a predicted event: {len(predicted_refs)}: {_ids(predicted_refs)}",
        "",
    ]


_APPLIED_GRANTS = Path(__file__).with_name("lost_outcomes_applied_grants.json")


def _applied_grants_section(conn: Any) -> list[str]:
    applied = json.loads(_APPLIED_GRANTS.read_text(encoding="utf-8"))
    on = date.fromisoformat(applied["recorded_on"])
    split: Counter[str] = Counter()
    rest: list[str] = []
    for case_id in applied["granted_cases"]:
        row = corpus.get_row(conn, case_id)
        if row is None:
            split["no-row"] += 1
        elif any(
            e.event_id == outcome_module.MERITS_EVENT_ID
            for e in corpus.events_for_case(conn, case_id)
        ):
            split["carries-merits-event"] += 1
        elif row.merits_judgment is not None:
            split["judgment-latched"] += 1
        elif row.merits_terminated is not None:
            split["terminated"] += 1
        elif corpus.is_stale_unparsed_grant(row, today=on):
            split["stale"] += 1
        else:
            split["none-of-these"] += 1
            rest.append(case_id)
    return [
        "## 6. Merits split of the grants the apply recorded",
        "",
        f"- apply commit {applied['commit'][:9]} ({applied['recorded_on']}); "
        + f"granted cases: {len(applied['granted_cases'])}",
        f"- split: {_counts(split)}",
        f"- none-of-these: {_ids(rest)}",
        "",
    ]


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    if not db.exists():
        print(f"no corpus at {db}; pull it first", file=sys.stderr)
        return 1
    data_root = settings.data_root
    lines = [f"Ledger read at the checkout; today {date.today().isoformat()}.", ""]
    with corpus.connect(db) as conn:
        lines += _population_section(conn, data_root)
    lines += _pass_section(db, data_root)
    with corpus.connect(db) as conn:
        lines += _open_gap_section(conn, data_root, date.today())
        lines += _predicted_closed_section(conn, data_root)
        lines += _exposure_section(conn, data_root)
        lines += _applied_grants_section(conn)
    lines += _opened_after_section(data_root)
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
