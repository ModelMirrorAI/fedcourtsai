"""Re-band the ledger's forward cells under sal-v8 beside sal-v7 (caption-v5).

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/sal_v8_forward_cells.py
    ```

it walks every committed forward prediction whose context froze a band, keeps
one cell per (case, event, cutoff), and re-places each truncated one with a
forward provisioning's date rule: the case's newest stored snapshot from the
per-case content store, cut to the cell's cutoff (`truncate_snapshot`, then
`cut_dated_fields`; the interim arrival anchor bound is not applied, since an
application docket freezes no band), banded by `cell_context.build` in `forward` mode under
sal-v7 and under sal-v8. sal-v8 differs only on a truncated forward payload,
so the as-stored and dated cells are counted, not re-placed. It appends to the
file named by `CHECK_SUMMARY` the corpus vintage, the cell count by provenance,
how many re-placed sal-v7 bands reproduce the band of a cell frozen under
sal-v7, and the cells whose
band moves, with their case ids and docket numbers. The newest snapshot can be
later than the pull a cell was placed on, so a re-placed band is a reading of
the rule over today's counsel blocks, not a replay of the cell. Counts and
identifiers only, never stored text.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus and the content store addressed; an optional argument
names the `data/cases` directory to walk instead of the checkout's own.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from fedcourtsai import provision
from fedcourtsai.pipeline import cell_context, salience

Cell = tuple[str, str, str]  # (case id, event id, cutoff)


def ledger_cells(root: Path) -> dict[Cell, dict[str, object]]:
    """One frozen forward context per (case, event, cutoff), banded cells only, the last read."""
    cells: dict[Cell, dict[str, object]] = {}
    for path in sorted(root.glob("scotus/*/events/*/predictions/*/*/prediction.json")):
        context = json.loads(path.read_text(encoding="utf-8")).get("context") or {}
        if context.get("mode") != "forward" or context.get("band") is None:
            continue
        case_id = f"scotus/{path.parts[-7]}"
        key = (case_id, path.parts[-5], str(context.get("cutoff")))
        # Paths sort by run id within a predictor, so the newest run's context
        # of each predictor overwrites older ones; any one per key is kept.
        cells[key] = context
    return cells


def band_under(version: str, case_id: str, payload: dict[str, object], cutoff: date) -> str | None:
    salience.SALIENCE_VERSION = version
    return cell_context.build(
        case_id, cutoff, payload, "forward", provenance="truncated", cutoff=cutoff
    ).band


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    source = provision.casestore_source_from_settings()
    # The ledger to walk: `data/cases` here, or a checkout of `main` named as
    # the one argument, since data commits land on `main` first.
    ledger = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/cases")
    cells = ledger_cells(ledger)
    provenance: Counter[str] = Counter()
    reproduced = frozen_v7 = replaced = unreadable = 0
    moved: list[tuple[str, str, str, str]] = []
    for (case_id, event_id, cutoff_text), context in sorted(cells.items()):
        kind = str(context.get("snapshot_provenance"))
        provenance[kind] += 1
        if kind != "truncated" or cutoff_text == "None":
            continue
        try:
            latest = source.latest_snapshot(case_id)
        except Exception:
            latest = None
        if latest is None:
            unreadable += 1
            continue
        cutoff = date.fromisoformat(cutoff_text)
        payload, _ = provision.truncate_snapshot(latest[1], cutoff)
        payload = provision.cut_dated_fields(payload, cutoff)
        before = band_under("sal-v7", case_id, payload, cutoff)
        after = band_under("sal-v8", case_id, payload, cutoff)
        replaced += 1
        # Only a cell frozen under sal-v7 can be reproduced by a sal-v7 band.
        if context.get("salience_version") == "sal-v7":
            frozen_v7 += 1
            reproduced += before == context.get("band")
        if before != after:
            docket = str(latest[1].get("CaseNumber") or "")
            moved.append((docket, case_id, event_id, f"{before} → {after}"))
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = ["### Forward cells whose frozen band moves from sal-v7 to sal-v8", ""]
    lines += ["`fedcourts corpus-info`:", ""]
    lines += [f"    {line}" for line in info.stdout.splitlines()]
    lines += ["", "| provenance | banded forward cells |", "| --- | --: |"]
    lines += [f"| {kind} | {n} |" for kind, n in sorted(provenance.items())]
    lines += [
        "",
        f"Truncated cells re-placed: {replaced} (no readable snapshot: {unreadable}); "
        f"of the {frozen_v7} frozen under sal-v7, the sal-v7 re-placement reproduces "
        f"the frozen band on {reproduced}.",
        f"Cells whose band moves under sal-v8: {len(moved)}",
        "",
        "| docket | case | event | sal-v7 → sal-v8 |",
        "| --- | --- | --- | --- |",
    ]
    lines += [f"| {' | '.join(cells_)} |" for cells_ in moved]
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
