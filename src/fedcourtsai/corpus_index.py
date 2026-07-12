"""Build the small, payload-stripped index from the corpus blob (corpus split, phase 2).

The corpus commingles tiny queryable metadata with huge write-once payloads. The
per-case content store (:mod:`fedcourtsai.casestore`) now stages those payloads as
browsable objects; this module produces the complementary **index**: a copy of the
corpus with the bulk stripped, so the queryable metadata can eventually be served
and re-pushed on its own (a fraction of the size) while the payloads live in the
content store.

What is stripped:

- the ``snapshots`` and ``documents`` tables — emptied (the point-in-time docket
  JSON and extracted document text);
- ``cases.opinion_text`` — NULLed (the full opinion body).

What is **kept**: every other ``cases`` column (including ``summary``, which
``query`` emits), the ``events`` / ``discovery_watermarks`` / ``live_discovery_cursors``
tables, and every index. The schema is left identical to the corpus (columns are
NULLed and tables emptied, never dropped), so read code does not error on the index.

**Drop-in scope.** The index is *result-identical* only for the three **bulk
consumers** — ``statpack``, ``backtest``, and ``query`` — which the parity gate in
``tests/test_corpus_index.py`` proves byte-for-byte. It is **not** a drop-in for
code that reads a stripped field as a *signal*: scope reconcile / audit and
``validate`` read ``cases.opinion_text`` (and, for the bare-import rule, a case's
``snapshots``) to classify it, and ``cert-backtest`` replay reads ``snapshots`` —
those must keep reading the full corpus blob. A later phase repoints only the bulk
consumers here.

This phase only *produces* the index and proves parity; no consumer reads it yet.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

INDEX_DB_FILENAME = "index.db"


def index_db_path(corpus_root: Path) -> Path:
    """The default location of the built index, beside the corpus blob."""
    return corpus_root / INDEX_DB_FILENAME


@dataclass(frozen=True)
class IndexStats:
    """A summary of one :func:`build_index` run, for the CLI to report."""

    cases: int
    snapshots_dropped: int
    documents_dropped: int
    opinions_nulled: int
    src_bytes: int
    index_bytes: int


def build_index(src: Path, dst: Path) -> IndexStats:
    """Write a payload-stripped copy of the corpus at ``src`` to ``dst``.

    Copies the blob with ``VACUUM INTO`` (a clean, compact copy that reads the
    committed state through a connection, so it is correct even if a WAL sidecar
    exists — unlike a raw file copy), empties the ``snapshots`` and ``documents``
    tables, NULLs ``cases.opinion_text``, then ``VACUUM``s the result so the freed
    space is reclaimed. The schema is unchanged (nothing dropped).
    """
    if dst.exists():
        dst.unlink()  # VACUUM INTO requires the target not to exist
    copier = sqlite3.connect(src)
    try:
        copier.execute("VACUUM INTO ?", (str(dst),))
    finally:
        copier.close()
    conn = sqlite3.connect(dst)
    try:
        cases = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        snapshots = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        documents = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        opinions = conn.execute(
            "SELECT COUNT(*) FROM cases WHERE opinion_text IS NOT NULL"
        ).fetchone()[0]
        conn.execute("DELETE FROM snapshots")
        conn.execute("DELETE FROM documents")
        conn.execute("UPDATE cases SET opinion_text = NULL")
        conn.commit()
        conn.execute("VACUUM")  # reclaim the freed pages (must run outside a transaction)
    finally:
        conn.close()
    return IndexStats(
        cases=int(cases),
        snapshots_dropped=int(snapshots),
        documents_dropped=int(documents),
        opinions_nulled=int(opinions),
        src_bytes=src.stat().st_size,
        index_bytes=dst.stat().st_size,
    )
