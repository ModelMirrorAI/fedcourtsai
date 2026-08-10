"""Scrub the bulk export's misjoined cluster fields from the stored slice.

The bulk export's docket-to-opinion-cluster join is misjoined on the circuit
slices (nineteenth-century cluster text and OCR-garbled judge names on
2018-19 dockets — an id-space collision in the staged join), so
:func:`fedcourtsai.pipeline.ingest.to_corpus_row` withholds the
cluster-derived fields — ``summary``, ``opinion_text``,
``precedential_status``, ``judges``,
``panel``, ``citations``, ``citation_count`` — from a bulk-sourced non-SCOTUS
row. That projection reaches a stored row only when the row is re-served,
and nothing re-serves the historical bulk slice; this sweep converges those
rows onto the same shape.

Provenance is provable for four of the seven fields, and the proof is a
**scope** argument rather than a claim about which endpoints exist. Cluster
data reaches the corpus through exactly two channels: the bulk join, and the
opinion enrichment (:mod:`fedcourtsai.pipeline.opinion_enrichment`), which
walks the SCOTUS merits track alone and writes nothing outside it. So a
populated ``summary``, ``precedential_status``, ``citations``, or
``citation_count`` on a **non-SCOTUS** row can only have come from the bulk
join, whatever the row's pull history — and the sweep's existing
``court != 'scotus'`` filter is what keeps that true, not an incidental
narrowing. Those four are the detection
predicate, and are nulled wherever populated. ``judges`` and ``panel`` are
different: discovery and pull re-derive them from the docket record itself,
so a populated pair proves nothing on its own — they are cleared only on
rows one of the four bulk-only fields marks, where the last cluster-bearing
write was necessarily the bulk join's. ``opinion_text`` is the seventh field
and deliberately not swept at all: every write to that column flows through
``upsert_rows``, which re-mirrors the case's stored ``case.json``, and
:func:`fedcourtsai.casestore.read_opinion_text` rests its freshness invariant
on no direct-``UPDATE`` writer touching it — this sweep is one, so it leaves
the column to the ingest projection that keeps a bulk body out of it in the
first place. The residue — a bulk row carrying
judges or panel and none of the four — is left alone, indistinguishable
from a discovery-onboarded row's sound values and measured in single digits
against the 1.36M-row slice. SCOTUS rows are untouched, as in the
projection: the misjoin is observed only on the circuit slices. Idempotent:
a scrubbed row no longer matches the predicate. The one UPDATE rewrites the
pages holding matched rows (most of the table on the first pass — the
run-seed step's bound covers it); the space the nulled text frees is reused
in place by the daily walks, so the sweep never vacuums.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

# A row carrying any field no channel could have written here — bulk provenance,
# proven by the writing channels' scope rather than inferred from channel stamps
# (see the module docstring; the `court != 'scotus'` filter below is load-bearing
# to that proof, not a convenience).
# The list-valued column stores JSON text (``'[]'`` when empty), the rest NULL.
_BULK_ONLY_POPULATED = (
    "summary IS NOT NULL OR precedential_status IS NOT NULL"
    " OR citation_count IS NOT NULL OR citations != '[]'"
)

_BULK_SLICE = f"court != 'scotus' AND ({_BULK_ONLY_POPULATED})"


@dataclass(frozen=True)
class BulkScrubResult:
    """What one scrub pass found (dry run) or converged (apply)."""

    applied: bool
    scrubbed: int


def scrub_bulk_cluster_fields(conn: sqlite3.Connection, *, apply: bool) -> BulkScrubResult:
    """Null the cluster-derived fields on the bulk-marked non-SCOTUS slice.

    One UPDATE over the ``cases`` table; see the module docstring for why the
    predicate is the faithful projection of the ingest carve-out onto stored
    rows. ``judges``/``panel`` clear in the same statement on the same
    predicate, so the four bulk-only fields mark the rows before being
    nulled. The dry run counts the same predicate the apply rewrites; the
    apply reports the UPDATE's own rowcount inside one transaction.
    """
    if not apply:
        row = conn.execute(f"SELECT COUNT(*) FROM cases WHERE {_BULK_SLICE}").fetchone()
        return BulkScrubResult(applied=False, scrubbed=int(row[0]))
    with conn:
        cursor = conn.execute(
            "UPDATE cases SET summary = NULL, precedential_status = NULL,"
            " citation_count = NULL, judges = '[]', panel = '[]', citations = '[]'"
            f" WHERE {_BULK_SLICE}"
        )
        return BulkScrubResult(applied=True, scrubbed=int(cursor.rowcount))
