from __future__ import annotations

from datetime import date
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.pipeline.scope_reconcile import reconcile_predict_scope
from fedcourtsai.schemas import Disposition


def _rows() -> list[corpus.CorpusRow]:
    return [
        # eligible + out of scope (stale unresolvable) -> should be latched out
        corpus.CorpusRow(
            case_id="scotus/1", court="scotus", docket_number="01-7700", predict_eligible=True
        ),
        # eligible + in scope (recent Term) -> left alone
        corpus.CorpusRow(
            case_id="scotus/2", court="scotus", docket_number="24-101", predict_eligible=True
        ),
        # out of scope but NOT eligible -> outside the reconcile universe, untouched
        corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="93-7515"),
    ]


def _excluded(db: Path, case_id: str) -> bool:
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.predict_excluded


def test_reconcile_dry_run_counts_without_writing(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        result = reconcile_predict_scope(conn, apply=False)
    assert result.applied is False
    assert result.eligible_cases == 2  # only the predict_eligible rows are weighed
    assert (result.excluded, result.released) == (1, 0)
    assert result.sample_excluded == ["scotus/1"]
    assert _excluded(db, "scotus/1") is False  # dry run wrote nothing


def test_reconcile_apply_latches_out_of_scope_eligible_cases(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        result = reconcile_predict_scope(conn, apply=True)
    assert result.applied is True and result.excluded == 1
    assert _excluded(db, "scotus/1") is True  # out-of-scope eligible case latched out
    assert _excluded(db, "scotus/2") is False  # in-scope case untouched
    assert _excluded(db, "scotus/3") is False  # ineligible case outside the universe


def test_reconcile_is_idempotent_and_two_directional(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        reconcile_predict_scope(conn, apply=True)
        # Second run changes nothing.
        again = reconcile_predict_scope(conn, apply=True)
        assert (again.excluded, again.released) == (0, 0)
        # The case returns to scope (a disposition is recorded); the latch clears.
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="01-7700",
                    predict_eligible=True,
                    disposition=Disposition.denied,
                    date_decided=date(2002, 1, 7),
                )
            ],
        )
        released = reconcile_predict_scope(conn, apply=True)
    assert (released.excluded, released.released) == (0, 1)
    assert _excluded(db, "scotus/1") is False


def test_reconcile_latches_and_releases_bare_opinion_import(tmp_path: Path) -> None:
    # A bare bulk-import row (every predicate-keyed field empty) whose
    # snapshot links an opinion cluster is latched out; a later re-ingest that
    # fills in real petition-stage facts breaks the profile and releases it.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/1038466", court="scotus", predict_eligible=True)],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/1038466",
            date(2026, 7, 2),
            {"id": 1038466, "clusters": ["https://example/clusters/88494/"]},
        )
        latched = reconcile_predict_scope(conn, apply=True)
        assert latched.sample_excluded == ["scotus/1038466"]
        assert _excluded(db, "scotus/1038466") is True
        # The row gains a real docket number: no longer bare, so the latch clears.
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1038466",
                    court="scotus",
                    docket_number="24-101",
                    predict_eligible=True,
                )
            ],
        )
        released = reconcile_predict_scope(conn, apply=True)
    assert (released.excluded, released.released) == (0, 1)
    assert _excluded(db, "scotus/1038466") is False


def test_reconcile_leaves_bare_row_without_cluster_in_scope(tmp_path: Path) -> None:
    # The bare profile alone is not an exclusion signal: with no snapshot (or no
    # linked cluster) the case could be a malformed but live matter, so it stays.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/7", court="scotus", predict_eligible=True)],
        )
        result = reconcile_predict_scope(conn, apply=True)
    assert (result.excluded, result.released) == (0, 0)
    assert _excluded(db, "scotus/7") is False


def test_reconcile_preserved_across_reingest(tmp_path: Path) -> None:
    # An ingestion re-write must not clobber the reconcile's latch (it is not an
    # ingestion fact); only the reconcile clears it.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        reconcile_predict_scope(conn, apply=True)
        assert _excluded(db, "scotus/1") is True
        # Re-ingest the same case (predict_excluded defaults False on the model).
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="01-7700",
                    predict_eligible=True,
                )
            ],
        )
    assert _excluded(db, "scotus/1") is True  # latch survived the re-ingest
