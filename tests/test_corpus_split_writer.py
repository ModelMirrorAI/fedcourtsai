"""Writer side of the corpus split (phase 4): a payload-free ``corpus.db``.

With ``FEDCOURTS_CORPUS_SPLIT`` on, the writer stops putting the bulk payloads
(snapshots, documents, the opinion body) into the blob — they live only in the
per-case content store — so ``corpus.db`` collapses to a small metadata index.
The payload *reads* the writer itself needs (change detection, document dedup) and
the readers need (provisioning, back-test) are served from the store through the
same seam. These tests prove the flip is lossless and that the store round-trips.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import casestore, corpus
from fedcourtsai.corpus_index import build_index
from fedcourtsai.fixture import build_fixture_corpus


def _table(db: Path, sql: str) -> list[tuple[object, ...]]:
    with corpus.connect(db) as conn:
        return [tuple(r) for r in conn.execute(sql)]


def _count(db: Path, sql: str) -> int:
    with corpus.connect(db) as conn:
        return int(conn.execute(sql).fetchone()[0])


def _row(case_id: str = "scotus/74112233", **kwargs: object) -> corpus.CorpusRow:
    court = case_id.split("/", 1)[0]
    return corpus.CorpusRow(case_id=case_id, court=court, docket_number="25-9", **kwargs)


def _doc(kind: str, text: str, fetched_at: date = date(2026, 5, 1)) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="scotus/74112233",
        kind=kind,
        url=f"https://sc.gov/{kind}.pdf",
        fetched_at=fetched_at,
        text=text,
    )


# --- has_opinion presence bit -------------------------------------------------


def test_has_opinion_derived_from_body_and_survives_roundtrip(tmp_path: Path) -> None:
    """`has_opinion` is set from the body at construction and round-trips as its own
    column, so it holds even when the body is later stripped."""
    row = _row(opinion_text="The judgment is affirmed.")
    assert row.has_opinion is True  # derived by the model validator
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [row])
        back = corpus.get_row(conn, row.case_id)
    assert back is not None and back.has_opinion is True and back.opinion_text is not None


def test_classifiers_key_on_has_opinion_not_body() -> None:
    """The scope classifiers read `has_opinion`, so a stripped body (None) still
    classifies when the presence bit is set."""
    stripped = corpus.CorpusRow(
        case_id="scotus/1003943", court="scotus", opinion_text=None, has_opinion=True
    )
    assert corpus.is_published_opinion_unresolvable(stripped) is True


# --- the split writer: payload-free blob, payloads in the store ---------------


def test_split_writer_matches_build_index_and_populates_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The parity gate: a blob written under the split mode is byte-for-content the
    same as the legacy blob run through ``build-index`` (payloads stripped), and the
    stripped payloads all landed in the content store."""
    # Mode off: the full blob (payloads present), then the phase-2 stripped index.
    off_store = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(off_store)
    off_db = tmp_path / "off.db"
    build_fixture_corpus(off_db)
    index_off = tmp_path / "index_off.db"
    build_index(off_db, index_off)

    # Sanity: the legacy blob really carried payloads to strip.
    assert _count(off_db, "SELECT COUNT(*) FROM snapshots") > 0
    assert _count(off_db, "SELECT COUNT(*) FROM cases WHERE opinion_text IS NOT NULL") > 0

    # Mode on: a fresh fixture, born payload-free, mirroring to its own store.
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    on_store = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(on_store)
    on_db = tmp_path / "on.db"
    build_fixture_corpus(on_db)

    # The split blob == the stripped legacy index, table for table.
    assert _table(on_db, "SELECT * FROM cases ORDER BY case_id") == _table(
        index_off, "SELECT * FROM cases ORDER BY case_id"
    )
    assert _table(on_db, "SELECT * FROM events ORDER BY case_id, event_id") == _table(
        index_off, "SELECT * FROM events ORDER BY case_id, event_id"
    )
    assert _table(on_db, "SELECT COUNT(*) FROM snapshots") == [(0,)]
    assert _table(on_db, "SELECT COUNT(*) FROM documents") == [(0,)]
    assert _table(on_db, "SELECT COUNT(*) FROM cases WHERE opinion_text IS NOT NULL") == [(0,)]
    # has_opinion carried the presence signal through the strip.
    assert _count(on_db, "SELECT COUNT(*) FROM cases WHERE has_opinion = 1") > 0

    # The store holds the payloads the blob shed — including the opinion body.
    assert any("/snapshots/" in k for k in on_store.objects)
    bodies = [json.loads(on_store.objects[k]) for k in on_store.objects if k.endswith("/case.json")]
    assert bodies  # at least one case mirrored
    assert any(b.get("opinion_text") for b in bodies)  # the body is in the store, not the blob


def test_build_index_backfills_has_opinion_on_a_legacy_blob(tmp_path: Path) -> None:
    """Stripping a blob that predates the `has_opinion` column must preserve the
    presence signal — `build-index` adds the column and sets it from the body before
    NULLing it, so a legacy strip never silently reclassifies opinion-bearing cases."""
    legacy = tmp_path / "legacy.db"
    with corpus.connect(legacy) as conn:
        corpus.upsert_rows(
            conn, [_row("scotus/1003943", opinion_text="Affirmed."), _row("scotus/2")]
        )
    # Simulate a blob that predates the column: drop it back out, full schema otherwise.
    raw = sqlite3.connect(legacy)
    raw.execute("ALTER TABLE cases DROP COLUMN has_opinion")
    raw.commit()
    raw.close()
    assert "has_opinion" not in {
        r[1] for r in sqlite3.connect(legacy).execute("PRAGMA table_info(cases)")
    }

    index = tmp_path / "index.db"
    build_index(legacy, index)

    with corpus.connect(index) as out:
        opinion = corpus.get_row(out, "scotus/1003943")
        plain = corpus.get_row(out, "scotus/2")
    assert opinion is not None and opinion.has_opinion is True and opinion.opinion_text is None
    assert plain is not None and plain.has_opinion is False


def test_split_reads_route_to_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Under the mode, ``corpus.latest_snapshot`` / ``documents_for_case`` read the
    store even though the blob's tables are empty."""
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    store = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(store)
    db = tmp_path / "c.db"
    payload = {"ProceedingsandOrder": [{"Text": "Petition filed."}]}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_snapshot(conn, "scotus/74112233", date(2026, 5, 1), payload)
        corpus.upsert_documents(conn, [_doc("petition", "the petition")])
        # The blob stayed empty; the reads come from the store.
        assert conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
        found = corpus.latest_snapshot(conn, "scotus/74112233")
        docs = corpus.documents_for_case(conn, "scotus/74112233")
    assert found is not None and found[1] == payload
    assert [d.kind for d in docs] == ["petition"] and docs[0].text == "the petition"


def test_split_change_detection_reads_prior_from_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Change detection (latest_snapshot before upsert) sees the store's prior, so a
    re-poll of identical facts is `changed=False` — the writer's own read routes."""
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    casestore.set_active_transport(casestore.InMemoryObjectTransport())
    db = tmp_path / "c.db"
    payload = {"ProceedingsandOrder": [{"Text": "Petition filed."}]}

    def poll(day: date) -> bool:
        with corpus.connect(db) as conn:
            prior = corpus.latest_snapshot(conn, "scotus/74112233")
            changed = prior is None or prior[1] != payload
            corpus.upsert_snapshot(conn, "scotus/74112233", day, payload)
        return changed

    assert poll(date(2026, 5, 1)) is True  # onboard (no prior in the store)
    assert poll(date(2026, 5, 2)) is False  # same facts, prior read from the store


def test_split_documents_merge_across_batches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A later document batch merges into the store manifest rather than replacing
    it, so an earlier kind is never dropped once the blob stops accumulating."""
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    casestore.set_active_transport(casestore.InMemoryObjectTransport())
    db = tmp_path / "c.db"
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, [_doc("petition", "P", date(2026, 5, 1))])
        corpus.upsert_documents(conn, [_doc("brief-in-opposition", "B", date(2026, 5, 2))])
        docs = corpus.documents_for_case(conn, "scotus/74112233")
    assert sorted(d.kind for d in docs) == ["brief-in-opposition", "petition"]
