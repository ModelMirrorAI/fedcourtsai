"""Census the post-conference first forecasts, and reconcile them with the set-aside list.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/post_conference_census.py
    ```

it reads the committed ledger at the checkout and the pulled corpus's latest
live payload for each cert distribution-moment event carrying a forward,
frozen-scope cell, and lists the events whose first such cell ran on or after
the day the conference that actually considered the petition sat
(`release_sensitivity.post_conference_rows`, the rule the scored-figure
set-aside's listed `post-conference-first-forecast` rows follow). It then
compares that census with `src/fedcourtsai/set_aside_events.json`: an event
the census finds and the list lacks is a row owed to the list, and a listed
event the census does not find is a row to explain. It also counts the
unreadable events (no live payload, or one stored before the conference day),
whose reading the census cannot make, and the events a post-conference relist
kept in — a petition relisted by the first cell's run day is read against the
conference ahead (`cert_signals.relisted_past`), so those cells are forward by
the rule, but the carve-out is date-dependent and the count is published.
Graded cells are counted over the frozen-scope pass with nothing set aside
(`stratify(..., apply_set_aside=False)`), so a listed event's gradings count.

Only counts and identifiers reach `CHECK_SUMMARY` — case ids, event ids,
conference dates and harness run ids — never stored snapshot text: the summary
is posted publicly (docs/corpus-check.md). The corpus vintage line comes from
`fedcourts corpus-info`, as in `corpus_vintage.py`.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.ids import parse_run_id
from fedcourtsai.leaderboard import stage_moment_key
from fedcourtsai.pipeline.cert_signals import relisted_past
from fedcourtsai.release_sensitivity import RANKED_ARM, cert_events, post_conference_rows
from fedcourtsai.schemas import Evaluation
from fedcourtsai.set_aside import SET_ASIDE_EVENTS
from fedcourtsai.store import stratify


def render(
    rows: Sequence[Mapping[str, Any]],
    unreadable: Sequence[Mapping[str, Any]],
    listed: set[tuple[str, str]],
    relisted: Sequence[tuple[str, str]] = (),
) -> str:
    """The summary's census section, from the census rows and the listed keys."""
    found = {(row["case_id"], row["event_id"]) for row in rows}
    owed = sorted(found - listed)
    unexplained = sorted(listed - found)
    lines = [
        "post-conference first forecasts (frozen scope, cert@distribution):",
        "",
        f"- census events: {len(rows)} "
        f"({sum(1 for row in rows if row['resolved'])} resolved, "
        f"{sum(1 for row in rows if row['graded_cells'])} with graded cells, "
        f"{sum(int(row['graded_cells']) for row in rows)} graded cells)",
        f"- listed in set_aside_events.json: {len(listed)}",
        f"- census events not listed (rows owed): {len(owed)}",
        f"- listed events the census does not find: {len(unexplained)}",
        f"- unreadable events: {len(unreadable)}",
        f"- events kept in by a relist docketed by the first cell's run day: {len(relisted)}",
        "",
        "| case | event | conference | first forward run | resolved | graded cells | listed |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in sorted(rows, key=lambda r: (r["considering_conference"], r["case_id"])):
        key = (row["case_id"], row["event_id"])
        lines.append(
            f"| `{row['case_id']}` | `{row['event_id']}` | {row['considering_conference']} "
            f"| {row['first_forward_run_id']} | {row['resolved']} | {row['graded_cells']} "
            f"| {key in listed} |"
        )
    if unexplained:
        lines += ["", "Listed, not found:", ""]
        lines += [f"- `{case}` `{event}`" for case, event in unexplained]
    if relisted:
        lines += ["", "Kept in by a relist:", ""]
        lines += [f"- `{case}` `{event}`" for case, event in sorted(relisted)]
    if unreadable:
        lines += ["", "Unreadable:", ""]
        lines += [
            f"- `{row['case_id']}` `{row['event_id']}`: "
            + ("no live payload" if row["reason"] == "no live payload" else "payload predates")
            for row in unreadable
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    graded: dict[tuple[str, str], list[Evaluation]] = defaultdict(list)
    for evaluation, _stratum, _stage, _moment in stratify(
        settings.data_root, frozen_only=True, apply_set_aside=False
    ).cells:
        graded[(evaluation.case_id, evaluation.event_id)].append(evaluation)
    events = cert_events(settings.data_root)
    relisted: list[tuple[str, str]] = []
    with corpus.connect_readonly(db, backend=settings.corpus_backend) as conn:

        def payloads(case_id: str) -> tuple[date, Mapping[str, Any]] | None:
            return corpus.latest_live_snapshot(conn, case_id)

        rows, unreadable = post_conference_rows(events, payloads, graded)
        for event in events:
            if stage_moment_key(event.stage, event.moment) != RANKED_ARM:
                continue
            if not event.frozen_forward_runs:
                continue
            found = payloads(event.case_id)
            run_day = parse_run_id(event.frozen_forward_runs[0]).date()
            if found is not None and relisted_past(found[1], run_day):
                relisted.append((event.case_id, event.event_id))
    listed = {
        key
        for key, event in SET_ASIDE_EVENTS.items()
        if event.reason == "post-conference-first-forecast"
    }
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        handle.write("\n")
        handle.write(render(rows, unreadable, listed, relisted))
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
