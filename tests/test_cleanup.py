from __future__ import annotations

from pathlib import Path

from fedcourtsai import cleanup, corpus


def _seed_corpus(corpus_root: Path, rows: list[corpus.CorpusRow]) -> Path:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    return db


def _write_prediction(data_root: Path, case_id: str, actor: str = "codex-baseline") -> Path:
    # A merged prediction artifact: …/events/<event>/predictions/<actor>/<run>/prediction.json
    pred_dir = (
        data_root
        / "cases"
        / case_id
        / "events"
        / "evt-petition-disposition"
        / "predictions"
        / actor
        / "20260630T000000Z"
    )
    pred_dir.mkdir(parents=True, exist_ok=True)
    (pred_dir / "prediction.json").write_text("{}")
    # The event definition sits a level above predictions/ and must never be touched.
    event_dir = data_root / "cases" / case_id / "events" / "evt-petition-disposition"
    (event_dir / "event.yaml").write_text("id: evt-petition-disposition\n")
    return pred_dir.parent.parent  # the predictions/ dir


def test_find_flags_out_of_scope_cases_only(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    corpus_db = _seed_corpus(
        tmp_path / "corpus",
        [
            # Out of scope: pre-1925 mandatory jurisdiction (#309) and stale unresolvable (#333).
            corpus.CorpusRow(case_id="scotus/1001931", court="scotus", docket_number="801"),
            corpus.CorpusRow(case_id="scotus/1004191", court="scotus", docket_number="01-7700"),
            # In scope: a recent open petition.
            corpus.CorpusRow(case_id="scotus/2400001", court="scotus", docket_number="24-101"),
        ],
    )
    for case_id in ("scotus/1001931", "scotus/1004191", "scotus/2400001"):
        _write_prediction(data_root, case_id)
    # A case with predictions but no corpus row is left alone (gate on real rows only).
    _write_prediction(data_root, "scotus/9999999")

    prunable = cleanup.find_out_of_scope_predictions(data_root, corpus_db)

    by_case = {case.case_id: case for case in prunable}
    assert set(by_case) == {"scotus/1001931", "scotus/1004191"}
    assert "mandatory-jurisdiction" in by_case["scotus/1001931"].reason
    assert "stale unresolvable" in by_case["scotus/1004191"].reason
    # Paths are repo-relative and point at the predictions/ dir, not the event.
    assert by_case["scotus/1004191"].paths == [
        "data/cases/scotus/1004191/events/evt-petition-disposition/predictions"
    ]


def test_remove_deletes_only_the_named_predictions(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    corpus_db = _seed_corpus(
        tmp_path / "corpus",
        [corpus.CorpusRow(case_id="scotus/1004191", court="scotus", docket_number="01-7700")],
    )
    predictions_dir = _write_prediction(data_root, "scotus/1004191")
    event_dir = predictions_dir.parent  # …/events/evt-petition-disposition

    prunable = cleanup.find_out_of_scope_predictions(data_root, corpus_db)
    removed = cleanup.remove(prunable, data_root.parent)

    assert removed == 1
    assert not predictions_dir.exists()  # predictions pruned
    assert (event_dir / "event.yaml").exists()  # the event definition stays


def test_remove_is_idempotent(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    corpus_db = _seed_corpus(
        tmp_path / "corpus",
        [corpus.CorpusRow(case_id="scotus/1004191", court="scotus", docket_number="01-7700")],
    )
    _write_prediction(data_root, "scotus/1004191")
    prunable = cleanup.find_out_of_scope_predictions(data_root, corpus_db)

    assert cleanup.remove(prunable, data_root.parent) == 1
    assert cleanup.remove(prunable, data_root.parent) == 0  # already gone, no error


def test_find_handles_missing_tree_or_corpus(tmp_path: Path) -> None:
    # No data/ tree and/or no corpus database -> nothing to do, no crash.
    assert cleanup.find_out_of_scope_predictions(tmp_path / "data", tmp_path / "corpus.db") == []
