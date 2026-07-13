from __future__ import annotations

from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.scope_manifest import build_scope_manifest


def _make_case_dir(data_root: Path, case_id: str) -> None:
    """Create a committed-style case directory (the git-visible public marker)."""
    court, _, docket = case_id.partition("/")
    (data_root / "cases" / court / docket).mkdir(parents=True, exist_ok=True)


def test_skipped_when_corpus_absent(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _make_case_dir(data_root, "scotus/2")
    manifest = build_scope_manifest(
        data_root=data_root, corpus_db_path=corpus.corpus_db_path(tmp_path / "corpus")
    )
    assert manifest.skipped is True
    assert manifest.entries == []


def test_enumerates_only_the_public_dir_set_not_the_corpus(tmp_path: Path) -> None:
    # The load-bearing invariant: the corpus holds more dockets than are public,
    # and the manifest must publish ONLY the ones with a committed directory —
    # never enumerate the wider ingested corpus (the compilation-extent boundary).
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-101"),
                corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24-102"),
                # In the corpus but NOT public — must never appear in the manifest.
                corpus.CorpusRow(case_id="scotus/9999", court="scotus", docket_number="24-900"),
            ],
        )
    _make_case_dir(data_root, "scotus/2")
    _make_case_dir(data_root, "scotus/3")

    manifest = build_scope_manifest(data_root=data_root, corpus_db_path=db)

    assert [e.case_id for e in manifest.entries] == ["scotus/2", "scotus/3"]
    assert manifest.cases == 2
    assert "scotus/9999" not in {e.case_id for e in manifest.entries}


def test_publishes_scope_columns_for_public_cases(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # In scope, with an asserted sampling weight (ingest sets
                # predict_eligible for SCOTUS dockets; the manifest republishes it).
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-101",
                    predict_eligible=True,
                    sample_weight=7,
                ),
                # Out of scope (stale unresolvable) and latched out.
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="01-7700",
                    predict_eligible=True,
                ),
            ],
        )
        corpus.set_predict_excluded(conn, "scotus/1", True)
    _make_case_dir(data_root, "scotus/1")
    _make_case_dir(data_root, "scotus/2")

    manifest = build_scope_manifest(data_root=data_root, corpus_db_path=db)
    by_id = {e.case_id: e for e in manifest.entries}

    in_scope = by_id["scotus/2"]
    assert in_scope.predict_eligible is True
    assert in_scope.predict_excluded is False
    assert in_scope.out_of_scope_reason is None
    assert in_scope.sample_weight == 7

    excluded = by_id["scotus/1"]
    assert excluded.predict_excluded is True
    assert excluded.out_of_scope_reason is not None
    assert manifest.excluded == 1
    assert manifest.eligible == 2  # both are SCOTUS dockets


def test_public_dir_missing_from_corpus_is_omitted(tmp_path: Path) -> None:
    # A public directory whose case is not in the corpus is skipped rather than
    # emitted with guessed-at scope fields.
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-101")],
        )
    _make_case_dir(data_root, "scotus/2")
    _make_case_dir(data_root, "scotus/404")  # public dir, no corpus row

    manifest = build_scope_manifest(data_root=data_root, corpus_db_path=db)
    assert [e.case_id for e in manifest.entries] == ["scotus/2"]


def test_entries_are_case_id_sorted_and_deterministic(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id="scotus/30", court="scotus", docket_number="24-3"),
                corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="24-4"),
                corpus.CorpusRow(case_id="scotus/200", court="scotus", docket_number="24-2"),
            ],
        )
    for cid in ("scotus/30", "scotus/4", "scotus/200"):
        _make_case_dir(data_root, cid)

    first = build_scope_manifest(data_root=data_root, corpus_db_path=db)
    second = build_scope_manifest(data_root=data_root, corpus_db_path=db)
    assert [e.case_id for e in first.entries] == ["scotus/200", "scotus/30", "scotus/4"]
    assert first.model_dump() == second.model_dump()
