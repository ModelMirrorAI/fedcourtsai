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
whose reading the census cannot make.

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
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.release_sensitivity import cert_events, post_conference_rows
from fedcourtsai.set_aside import SET_ASIDE_EVENTS


def render(
    rows: Sequence[Mapping[str, Any]],
    unreadable: Sequence[Mapping[str, Any]],
    listed: set[tuple[str, str]],
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
    with corpus.connect_readonly(db, backend=settings.corpus_backend) as conn:
        rows, unreadable = post_conference_rows(
            cert_events(settings.data_root),
            lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        )
    listed = {
        key
        for key, event in SET_ASIDE_EVENTS.items()
        if event.reason == "post-conference-first-forecast"
    }
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        handle.write("\n")
        handle.write(render(rows, unreadable, listed))
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
