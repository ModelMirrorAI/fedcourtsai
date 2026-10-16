"""Census the stored interim rows the finer reading names partial or moot.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/interim_partial_moot_census.py
    ```

it runs `fedcourts interim-reading-census`, which reads the corpus and the
committed ledger and writes nothing, and reports to the file named by
`CHECK_SUMMARY`:

- the corpus vintage (`fedcourts corpus-info`);
- that nothing scored or cell-facing moves now: how many stored labels the
  registered reading reproduces from their snapshots (every one, unless the
  corpus already carried drift), and that the census wrote nothing;
- the registered reading's known side-motion misreading: stored denials whose
  application clause grants;
- as information only: how many resolved applications carry partial-grant or
  mootness order text, by application Term and ask; the statpack's substantive
  counts per Term (the base rate's population) beside the re-read subset's,
  with the unobservable and non-live gap; and the committed interim outcomes
  on the named rows with the predictions under each — which stay exactly as
  recorded.

Counts and identifiers only, never stored snapshot text: the summary is posted
publicly (docs/corpus-check.md). The ledger read is the checkout's `data/`,
which in the lane is the pull request head's.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus and the content store addressed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _census(stdout: str) -> dict[str, Any] | None:
    """The command's serialized result: its last JSON line."""
    for line in reversed(stdout.strip().splitlines()):
        if line.startswith("{"):
            parsed = json.loads(line)
            return parsed if isinstance(parsed, dict) else None
    return None


def _render(census: dict[str, Any]) -> list[str]:
    rows = census["rows"]
    lines = [
        "",
        "`fedcourts interim-reading-census` (read-only):",
        "",
        f"- corpus read: `{census['corpus_sha256'] or 'unrecorded'}`",
        f"- re-read population (resolved, application-parsed, live slice): {census['eligible']} "
        + f"(snapshot read for {census['observable']}, unobservable {census['unobservable']} — "
        + "read this first: an index-only pull lands every row there); resolved "
        + f"application-parsed rows outside the live slice, not re-read: {census['non_live']}",
        "",
        "**Now — nothing scored or cell-facing moves:**",
        "- stored labels the registered reading reproduces: "
        + f"{census['observable'] - len(census['registered_disagreements'])} of "
        + f"{census['observable']}; pre-existing drift: "
        + f"{', '.join(census['registered_disagreements']) or 'none'}",
        f"- stored labels written: {census['stored_labels_written']}",
        "- registered reading's side-motion misreading (stored denied, application clause "
        + f"grants): {len(census['registered_plain_grant_misreads'])}"
        + (
            f" — {', '.join(census['registered_plain_grant_misreads'])}"
            if census["registered_plain_grant_misreads"]
            else ""
        ),
        "",
        "**What the finer reading names (information only):**",
        f"- rows carrying partial-grant or mootness order text: {len(rows)} "
        + f"({sum(1 for r in rows if not r['same_entry'])} read off a different entry than "
        + "the stored date)",
        "",
        "| application Term | ask | granted-in-part | dismissed-moot |",
        "| --- | --- | --: | --: |",
    ]
    for term, kinds in census["by_term"].items():
        for kind, labels in kinds.items():
            lines.append(
                f"| {term} | {kind} | {labels.get('granted-in-part', 0)} "
                f"| {labels.get('dismissed-moot', 0)} |"
            )
    moves = Counter((r["stored"], r["reading"]) for r in rows)
    lines += ["", "By stored label -> finer reading:"]
    lines += [f"- {stored} -> {reading}: {n}" for (stored, reading), n in sorted(moves.items())]
    lines += [
        "",
        "Substantive counts by application Term — the statpack's (the base rate's "
        + "population) beside the re-read subset:",
        "",
        "| Term | statpack granted/resolved | re-read granted/resolved | re-read partial "
        + "(stored ungranted) | re-read moot | unobservable | non-live |",
        "| --- | --- | --- | --- | --: | --: | --: |",
    ]
    for term, c in census["terms"].items():
        if not c["statpack_resolved"]:
            continue
        lines.append(
            f"| {term} | {c['statpack_granted']}/{c['statpack_resolved']} "
            f"| {c['reread_granted']}/{c['reread_resolved']} "
            f"| {c['reread_partial']} ({c['reread_partial_stored_ungranted']}) "
            f"| {c['reread_moot']} | {c['unobservable']} | {c['non_live']} |"
        )
    lines += ["", "Rows (case id, docket number, Term, ask, stored -> finer reading):"]
    lines += [
        f"- {r['case_id']} {r['docket_number']} OT{r['term']} {r['application_kind']}: "
        f"{r['stored']} -> {r['reading']}"
        for r in rows
    ]
    outcomes = census["committed_outcomes"]
    lines += [
        "",
        f"Committed interim outcomes on those rows (unchanged): {len(outcomes)}; on events "
        f"carrying committed predictions: {sum(1 for o in outcomes if o['predictions'])}",
    ]
    lines += [
        f"- {o['ref']}: recorded {o['recorded']}, finer reading {o['reading']}, "
        f"{o['predictions']} prediction(s)"
        for o in outcomes
    ]
    return lines


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    info = _run("corpus-info")
    run = _run("interim-reading-census")
    sys.stderr.write(info.stderr + run.stderr)
    census = _census(run.stdout) if run.returncode == 0 else None
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        if census is None:
            handle.write(
                f"\n`fedcourts interim-reading-census` failed (exit {run.returncode}); no census.\n"
            )
        else:
            handle.write("\n".join(_render(census)) + "\n")
    if info.returncode != 0:
        return info.returncode
    return 0 if census is not None else 1


if __name__ == "__main__":
    sys.exit(main())
