"""Parity gate for the payload-stripped index (corpus split, phase 2).

Proves the bulk consumers (statpack / backtest / query) produce byte-identical
output whether they read the full corpus blob or the stripped index — the
prerequisite for a later phase repointing those consumers at the index.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus, corpus_index
from fedcourtsai.backtest import default_backtesters, run_backtest, select_backtest_set
from fedcourtsai.cli import app
from fedcourtsai.fixture import build_fixture_corpus

runner = CliRunner()


def _two_roots(tmp_path: Path) -> tuple[Path, Path]:
    """Two corpus roots — one holding the fixture blob, one the stripped index —
    each with the db named ``corpus.db`` so the CLI resolves it.

    The blob carries a non-null ``summary`` (kept: query emits it) and a
    ``documents`` row (so emptying that table is actually exercised) alongside the
    fixture's snapshots and opinion_text, so every strip/keep leg is non-vacuous.
    """
    blob_root, idx_root = tmp_path / "blob", tmp_path / "idx"
    blob_root.mkdir()
    idx_root.mkdir()
    src = corpus.corpus_db_path(blob_root)
    build_fixture_corpus(src)
    with corpus.connect(src) as conn:
        conn.execute("UPDATE cases SET summary = 'abstract' WHERE court = 'scotus'")
        conn.commit()
        case_id = conn.execute("SELECT case_id FROM cases ORDER BY case_id LIMIT 1").fetchone()[0]
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=case_id,
                    kind="petition",
                    url="https://sc.gov/p.pdf",
                    fetched_at=date(2026, 5, 1),
                    text="petition text",
                )
            ],
        )
    corpus_index.build_index(src, corpus.corpus_db_path(idx_root))
    return blob_root, idx_root


# --- structural: what the strip does -------------------------------------------


def test_build_index_strips_bulk_keeps_metadata(tmp_path: Path) -> None:
    blob_root, idx_root = _two_roots(tmp_path)
    src, index = corpus.corpus_db_path(blob_root), corpus.corpus_db_path(idx_root)
    with corpus.connect(src) as conn:
        src_cases = corpus.count(conn)
    stats = corpus_index.build_index(src, index)

    assert stats.snapshots_dropped > 0  # the fixture snapshots the cases
    assert stats.documents_dropped > 0  # the added document
    assert stats.opinions_nulled > 0  # the fixture sets opinion_text on some cases
    assert stats.cases == src_cases
    assert stats.index_bytes <= stats.src_bytes

    with corpus.connect(index) as conn:
        assert corpus.count(conn) == src_cases  # every case row retained
        assert corpus.snapshot_count(conn) == 0  # snapshots emptied
        assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
        assert (
            conn.execute("SELECT COUNT(*) FROM cases WHERE opinion_text IS NOT NULL").fetchone()[0]
            == 0
        )  # opinion_text NULLed
        assert (
            conn.execute("SELECT COUNT(*) FROM cases WHERE summary IS NOT NULL").fetchone()[0] > 0
        )  # summary retained (query emits it)
        assert conn.execute("SELECT COUNT(*) FROM live_discovery_cursors").fetchone()[0] > 0


def test_non_opinion_columns_are_identical(tmp_path: Path) -> None:
    """Every ``cases`` column except opinion_text is byte-identical after stripping."""
    blob_root, idx_root = _two_roots(tmp_path)
    cols = ", ".join(c for c in corpus._COLUMNS if c != "opinion_text")
    with (
        corpus.connect(corpus.corpus_db_path(blob_root)) as a,
        corpus.connect(corpus.corpus_db_path(idx_root)) as b,
    ):
        rows_src = a.execute(f"SELECT {cols} FROM cases ORDER BY case_id").fetchall()
        rows_idx = b.execute(f"SELECT {cols} FROM cases ORDER BY case_id").fetchall()
    assert [tuple(r) for r in rows_src] == [tuple(r) for r in rows_idx]


# --- consumer parity: blob vs index -------------------------------------------
#
# statpack/backtest drive the same library functions the `statpack`/`backtest` CLI
# commands call (analytics.build_statpack; select_backtest_set + default_backtesters
# + run_backtest — cf. cli.py `statpack`/`backtest`), so they are faithful. `query`
# is driven through the real CLI, because its output does a per-row transform
# (era + opinion_text pop) that a hand-copied replica could silently drift from.


def test_statpack_parity(tmp_path: Path) -> None:
    blob_root, idx_root = _two_roots(tmp_path)

    def pack(root: Path) -> Any:
        return analytics.build_statpack(corpus_db_path=corpus.corpus_db_path(root)).model_dump(
            mode="json"
        )

    assert pack(blob_root) == pack(idx_root)


def test_backtest_parity(tmp_path: Path) -> None:
    blob_root, idx_root = _two_roots(tmp_path)

    def report(root: Path) -> Any:
        with corpus.connect(corpus.corpus_db_path(root)) as conn:
            items = select_backtest_set(conn)
            return run_backtest(default_backtesters(conn), items).model_dump(mode="json")

    assert report(blob_root) == report(idx_root)


def test_query_parity_via_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    blob_root, idx_root = _two_roots(tmp_path)

    def run(root: Path) -> str:
        monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
        result = runner.invoke(app, ["query", "--limit", "1000"])
        assert result.exit_code == 0, result.stdout
        return result.stdout

    blob_out = run(blob_root)
    assert blob_out.strip()  # the fixture yields priors, so parity is non-vacuous
    assert blob_out == run(idx_root)


def test_query_full_would_differ_on_opinion_text(tmp_path: Path) -> None:
    """Sanity: the strip is real — with opinion_text retained (``--full``), blob and
    index differ, which is exactly why the index does not serve ``--full``."""
    blob_root, idx_root = _two_roots(tmp_path)
    q = corpus.PriorQuery(resolved_only=False)
    with (
        corpus.connect_readonly(corpus.corpus_db_path(blob_root)) as a,
        corpus.connect_readonly(corpus.corpus_db_path(idx_root)) as b,
    ):
        src_full = [r.model_dump(mode="json") for r in corpus.retrieve_priors(a, q, limit=1000)]
        idx_full = [r.model_dump(mode="json") for r in corpus.retrieve_priors(b, q, limit=1000)]
    assert src_full != idx_full  # opinion_text present in the blob, NULL in the index
