"""Census the SCOTUS dockets the withheld-petitioner-block reading changes.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/withheld_petitioner_census.py
    ```

it runs the real predicate (`pipeline.documents.withholds_petitioner_block`)
and the real scrub (`scrub_contact_details`, keyed by `party_contact_values`
over `unrepresented_sides`) over the latest live snapshot and the stored
documents of every live-slice SCOTUS row, and reports to the file named by
`CHECK_SUMMARY`:

- how many rows were walked and how many carry a live snapshot;
- the dockets the predicate reads as withholding the petitioner's block, by
  class: **newly scrubbed** (no side read self-represented before), **value
  only to value and shape** (only the `Other` list was read before), and
  **unchanged** (already shape-scrubbed) — each with how many are
  salience-selected, how many pending, how many hold stored documents, and the
  spans the scrub withholds (for the unchanged class a total, not spans the
  change adds);
- the known residual: Court-shaped payloads carrying neither side's counsel
  key, split selected and pending;
- per docket, the case id, its class, selected and pending flags, the
  document count and the span count.

The walk is the live slice (`iter_rows(..., live_slice=True)`): a live-shaped
payload is written only by the supremecourt.gov channel, which stamps
`last_live_polled` on every write, so a row outside the slice holds no payload
the predicate can read. Payload reads are fanned across the content store's
bounded reader pool (`pipeline.prefetch.prefetch_by_case`), serial on a
local blob.

Counts and identifiers only, never a withheld value or any stored snapshot or
document text: the summary is posted publicly (docs/corpus-check.md). The
corpus vintage line comes from `fedcourts corpus-info`, as in
`corpus_vintage.py`. `--no-listings` drops the per-docket listing.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline.documents import (
    OTHER_LIST,
    party_contact_values,
    scrub_contact_details,
    unrepresented_sides,
    withholds_petitioner_block,
)
from fedcourtsai.pipeline.prefetch import prefetch_by_case

CLASSES = ("newly-scrubbed", "value-only-to-shape", "unchanged")


@dataclass(frozen=True)
class Found:
    case_id: str
    change: str
    selected: bool
    pending: bool
    documents: int
    spans: int


@dataclass
class Census:
    rows: int = 0
    with_snapshot: int = 0
    residual: int = 0
    residual_selected: int = 0
    residual_pending: int = 0
    found: list[Found] = field(default_factory=list)


def classify(payload: dict[str, Any]) -> str:
    """The class a withholding payload falls in, read off the sides before and after."""
    after = unrepresented_sides(payload)
    before = tuple(side for side in after if side != "Petitioner")
    if not before:
        return "newly-scrubbed"
    if all(side == OTHER_LIST for side in before):
        return "value-only-to-shape"
    return "unchanged"


def is_residual(payload: dict[str, Any]) -> bool:
    """The Court's shape with neither side's counsel key: the residual the change leaves open."""
    return (
        "ProceedingsandOrder" in payload
        and "Petitioner" not in payload
        and "Respondent" not in payload
        and "AttorneyHeaderRespondent" not in payload
    )


def run_census(conn: Any) -> Census:
    census = Census()
    rows = {row.case_id: row for row in corpus.iter_rows(conn, court="scotus", live_slice=True)}
    census.rows = len(rows)

    def read(case_id: str) -> tuple[date, dict[str, Any]] | None:
        return corpus.latest_live_snapshot(conn, case_id)

    with prefetch_by_case(list(rows), read, thread_name_prefix="withheld-census") as stream:
        for case_id, snapshot in stream:
            if snapshot is None:
                continue
            census.with_snapshot += 1
            row = rows[case_id]
            payload = snapshot[1]
            pending = corpus.resolution_date(row) is None
            if is_residual(payload):
                census.residual += 1
                census.residual_selected += int(row.salience_selected)
                census.residual_pending += int(pending)
                continue
            if not withholds_petitioner_block(payload):
                continue
            docs = corpus.documents_for_case(conn, case_id)
            values = party_contact_values(payload, unrepresented_sides(payload))
            spans = sum(scrub_contact_details(doc.text, values).replacements for doc in docs)
            census.found.append(
                Found(case_id, classify(payload), row.salience_selected, pending, len(docs), spans)
            )
    return census


def render(census: Census, *, listings: bool) -> str:
    found = census.found
    lines = [
        "withheld petitioner block (latest live snapshot, live-slice SCOTUS rows):",
        "",
        f"- live-slice SCOTUS rows walked: {census.rows}; with a live snapshot: "
        + f"{census.with_snapshot}",
        f"- withheld petitioner block: {len(found)}",
    ]
    for change in CLASSES:
        group = [f for f in found if f.change == change]
        label = "spans withheld (total, not added)" if change == "unchanged" else "spans withheld"
        lines.append(
            f"  - {change}: {len(group)} (selected {sum(1 for f in group if f.selected)}, "
            + f"pending {sum(1 for f in group if f.pending)}, "
            + f"with stored documents {sum(1 for f in group if f.documents)}, "
            + f"{label} {sum(f.spans for f in group)})"
        )
    lines.append(
        f"- residual, Court shape with neither counsel key: {census.residual} "
        + f"(selected {census.residual_selected}, pending {census.residual_pending})"
    )
    if listings and found:
        lines += [
            "",
            "Per docket (case, class, selected, pending, documents, spans):",
            "",
        ]
        lines += [
            f"- `{f.case_id}` {f.change} {'selected' if f.selected else '-'} "
            + f"{'pending' if f.pending else 'resolved'} docs={f.documents} spans={f.spans}"
            for f in found
        ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    listings = "--no-listings" not in args
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
        census = run_census(conn)
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        handle.write(
            "payload reads: "
            + ("the per-case content store" if corpus.payload_reads_offloaded() else "the blob")
            + "\n\n"
        )
        handle.write(render(census, listings=listings))
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
