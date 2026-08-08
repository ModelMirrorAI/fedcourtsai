"""Scrub the bulk export's misjoined cluster fields from the stored slice.

The bulk export's docket-to-opinion-cluster join is misjoined on the circuit
slices (nineteenth-century cluster text and OCR-garbled judge names on
2018-19 dockets — an id-space collision in the staged join), so
:func:`fedcourtsai.pipeline.ingest.to_corpus_row` withholds the
cluster-derived fields — ``summary``, ``precedential_status``, ``judges``,
``panel``, ``citations``, ``citation_count`` — from a bulk-sourced non-SCOTUS
row. That projection reaches a stored row only when the row is re-served,
and nothing re-serves the historical bulk slice; this sweep converges those
rows onto the same shape.

The stored row carries no source column (the projection drops ingestion
provenance), so the slice is read from the one channel stamp that separates
it: a non-SCOTUS row the REST channel has refreshed carries ``last_pulled``,
and its cluster fields — re-projected from the API's sound per-docket join
on that refresh — are kept; a never-pulled non-SCOTUS row's cluster fields
can only have come from the bulk join, and are dropped. SCOTUS rows are
untouched, as in the projection: the misjoin is observed only on the circuit
slices. Idempotent: a scrubbed row no longer matches the populated
predicate. The freed pages stay in the blob for the daily walks to reuse —
no vacuum, so the sweep never rewrites the file it is one UPDATE against.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

# A row still carrying any value the projection would have withheld. The
# list-valued columns store JSON text (``'[]'`` when empty), the rest NULL.
_CLUSTER_POPULATED = (
    "summary IS NOT NULL OR precedential_status IS NOT NULL"
    " OR citation_count IS NOT NULL OR judges != '[]' OR panel != '[]'"
    " OR citations != '[]'"
)

_BULK_SLICE = f"court != 'scotus' AND last_pulled IS NULL AND ({_CLUSTER_POPULATED})"


@dataclass(frozen=True)
class BulkScrubResult:
    """What one scrub pass found (dry run) or converged (apply)."""

    applied: bool
    scrubbed: int


def scrub_bulk_cluster_fields(conn: sqlite3.Connection, *, apply: bool) -> BulkScrubResult:
    """Null the cluster-derived fields on the never-pulled non-SCOTUS slice.

    One UPDATE over the ``cases`` table; see the module docstring for why the
    predicate is the faithful projection of the ingest carve-out onto stored
    rows. Dry run counts the same predicate it would rewrite.
    """
    row = conn.execute(f"SELECT COUNT(*) FROM cases WHERE {_BULK_SLICE}").fetchone()
    matched = int(row[0])
    if apply and matched:
        conn.execute(
            "UPDATE cases SET summary = NULL, precedential_status = NULL,"
            " citation_count = NULL, judges = '[]', panel = '[]', citations = '[]'"
            f" WHERE {_BULK_SLICE}"
        )
        conn.commit()
    return BulkScrubResult(applied=apply, scrubbed=matched)
