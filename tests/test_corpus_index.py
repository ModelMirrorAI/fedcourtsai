"""Parity gate for the payload-stripped index (corpus split, phase 2).

Proves the bulk consumers (statpack / backtest / query) produce byte-identical
output whether they read the full corpus blob or the stripped index — the
prerequisite for a later phase repointing them at the index.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fedcourtsai import analytics, corpus, corpus_index
from fedcourtsai.backtest import default_backtesters, run_backtest, select_backtest_set
from fedcourtsai.fixture import build_fixture_corpus


def _corpus_and_index(tmp_path: Path) -> tuple[Path, Path]:
    """A built fixture corpus and its stripped index; the corpus carries a summary
    so the index is checked to retain it (query emits summary)."""
    src = tmp_path / "corpus.db"
    build_fixture_corpus(src)
    with corpus.connect(src) as conn:
        conn.execute(
            "UPDATE cases SET summary = 'kept abstract' "
            "WHERE case_id = (SELECT case_id FROM cases ORDER BY case_id LIMIT 1)"
        )
        conn.commit()
    dst = tmp_path / "index.db"
    corpus_index.build_index(src, dst)
    return src, dst


def test_build_index_strips_bulk_keeps_metadata(tmp_path: Path) -> None:
    src = tmp_path / "corpus.db"
    build_fixture_corpus(src)
    with corpus.connect(src) as conn:
        conn.execute("UPDATE cases SET summary = 'abstract' WHERE court = 'scotus'")
        conn.commit()
        src_cases = corpus.count(conn)
    dst = tmp_path / "index.db"
    stats = corpus_index.build_index(src, dst)

    assert stats.snapshots_dropped > 0  # the fixture snapshots the cases
    assert stats.opinions_nulled > 0  # the fixture sets opinion_text on some cases
    assert stats.cases == src_cases
    assert stats.index_bytes <= stats.src_bytes

    with corpus.connect(dst) as conn:
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
    """Every `cases` column except opinion_text is byte-identical after stripping."""
    src, dst = _corpus_and_index(tmp_path)
    cols = ", ".join(c for c in corpus._COLUMNS if c != "opinion_text")
    with corpus.connect(src) as a, corpus.connect(dst) as b:
        rows_src = a.execute(f"SELECT {cols} FROM cases ORDER BY case_id").fetchall()
        rows_idx = b.execute(f"SELECT {cols} FROM cases ORDER BY case_id").fetchall()
    assert [tuple(r) for r in rows_src] == [tuple(r) for r in rows_idx]


# --- consumer parity: blob vs index -------------------------------------------


def _statpack(db: Path) -> Any:
    return analytics.build_statpack(corpus_db_path=db).model_dump(mode="json")


def _backtest(db: Path) -> Any:
    with corpus.connect(db) as conn:
        items = select_backtest_set(conn)
        return run_backtest(default_backtesters(conn), items).model_dump(mode="json")


def _query(db: Path) -> list[dict[str, Any]]:
    """Mirror the default `query` CLI output (opinion_text popped; era carried)."""
    q = corpus.PriorQuery(resolved_only=False)
    with corpus.connect_readonly(db) as conn:
        priors = corpus.retrieve_priors(conn, q, limit=1000)
    out: list[dict[str, Any]] = []
    for row in priors:
        payload = row.model_dump(mode="json")
        payload["era"] = corpus.case_era(row)
        payload.pop("opinion_text", None)
        out.append(payload)
    return out


def test_statpack_parity(tmp_path: Path) -> None:
    src, dst = _corpus_and_index(tmp_path)
    assert _statpack(src) == _statpack(dst)


def test_backtest_parity(tmp_path: Path) -> None:
    src, dst = _corpus_and_index(tmp_path)
    assert _backtest(src) == _backtest(dst)


def test_query_parity(tmp_path: Path) -> None:
    src, dst = _corpus_and_index(tmp_path)
    src_out, idx_out = _query(src), _query(dst)
    assert src_out == idx_out
    assert src_out  # the fixture yields priors, so parity is non-vacuous


def test_query_full_would_differ_on_opinion_text(tmp_path: Path) -> None:
    """Sanity: the strip is real — with opinion_text retained (`--full`), blob and
    index differ, which is exactly why the index does not serve `--full`."""
    src, dst = _corpus_and_index(tmp_path)
    q = corpus.PriorQuery(resolved_only=False)
    with corpus.connect_readonly(src) as a, corpus.connect_readonly(dst) as b:
        src_full = [r.model_dump(mode="json") for r in corpus.retrieve_priors(a, q, limit=1000)]
        idx_full = [r.model_dump(mode="json") for r in corpus.retrieve_priors(b, q, limit=1000)]
    assert src_full != idx_full  # opinion_text present in the blob, NULL in the index
