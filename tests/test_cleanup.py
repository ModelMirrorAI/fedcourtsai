from __future__ import annotations

from datetime import date
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
            # Out of scope: pre-1925 mandatory jurisdiction and stale unresolvable.
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


def test_find_leaves_salience_deferred_predictions_alone(tmp_path: Path) -> None:
    # The load-bearing separation: a petition scored but NOT selected by the
    # salience gate (below the capacity slice) is hard-in-scope, so cleanup must
    # never prune its committed prediction — only out-of-scope cases are prunable.
    # Deleting a below-cap forward prediction would destroy a pre-registered
    # forecast; the salience gate defers at read time, it does not delete.
    data_root = tmp_path / "data"
    corpus_db = _seed_corpus(
        tmp_path / "corpus",
        [
            corpus.CorpusRow(
                case_id="scotus/2400001",
                court="scotus",
                docket_number="24-101",
                salience_version="sal-v1",
                salience_selected=False,  # scored, not selected → deferred, not out of scope
            )
        ],
    )
    _write_prediction(data_root, "scotus/2400001")

    prunable = cleanup.find_out_of_scope_predictions(data_root, corpus_db)

    assert prunable == []  # deferred ≠ out of scope; its prediction survives


def test_find_flags_bare_opinion_import_case(tmp_path: Path) -> None:
    # A bare bulk-import row (no docket number, no dates, no citation
    # fields) whose snapshot links an opinion cluster is prunable; the same bare
    # row without the cluster link stays untouched.
    data_root = tmp_path / "data"
    corpus_db = _seed_corpus(
        tmp_path / "corpus",
        [
            corpus.CorpusRow(case_id="scotus/1038466", court="scotus"),
            corpus.CorpusRow(case_id="scotus/7", court="scotus"),
        ],
    )
    with corpus.connect(corpus_db) as conn:
        corpus.upsert_snapshot(
            conn,
            "scotus/1038466",
            date(2026, 7, 2),
            {"id": 1038466, "clusters": ["https://example/clusters/88494/"]},
        )
    _write_prediction(data_root, "scotus/1038466")
    _write_prediction(data_root, "scotus/7")

    prunable = cleanup.find_out_of_scope_predictions(data_root, corpus_db)

    assert [case.case_id for case in prunable] == ["scotus/1038466"]
    assert prunable[0].reason == corpus.BARE_OPINION_IMPORT_REASON


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

    # Call outside the assert: remove() has a side effect (deleting dirs), which an
    # `assert f() == n` would drop under `python -O`.
    first_pass = cleanup.remove(prunable, data_root.parent)
    second_pass = cleanup.remove(prunable, data_root.parent)
    assert first_pass == 1
    assert second_pass == 0  # already gone, no error


def test_find_handles_missing_tree_or_corpus(tmp_path: Path) -> None:
    # No data/ tree and/or no corpus database -> nothing to do, no crash.
    assert cleanup.find_out_of_scope_predictions(tmp_path / "data", tmp_path / "corpus.db") == []


def test_render_cleanup_pr_table_and_closes() -> None:
    prunable = [
        cleanup.PrunableCase(
            case_id="scotus/1004191",
            reason="stale unresolvable old SCOTUS petition (pre-2015 Term, still open)",
            paths=["data/cases/scotus/1004191/events/evt-petition-disposition/predictions"],
        ),
        cleanup.PrunableCase(
            case_id="scotus/1001931",
            reason="pre-1925 mandatory-jurisdiction matter",
            paths=["p1", "p2"],
        ),
    ]
    pr = cleanup.render_cleanup_pr(prunable, run_id="RID", issue=320)
    assert pr.branch == "cleanup/out-of-scope-predictions-RID"
    assert pr.title == "cleanup: prune predictions for 2 out-of-scope cases"
    assert pr.commit_message == pr.title
    assert (
        "| `scotus/1004191` | stale unresolvable old SCOTUS petition "
        "(pre-2015 Term, still open) | 1 |" in pr.body
    )
    assert "| `scotus/1001931` | pre-1925 mandatory-jurisdiction matter | 2 |" in pr.body
    assert "Closes #320." in pr.body
    assert "not** auto-merged" in pr.body


def test_render_cleanup_pr_singular_and_no_issue() -> None:
    pr = cleanup.render_cleanup_pr(
        [cleanup.PrunableCase(case_id="scotus/1004191", reason="r", paths=["p"])], run_id="RID"
    )
    assert pr.title == "cleanup: prune predictions for 1 out-of-scope case"
    assert "Closes #" not in pr.body
