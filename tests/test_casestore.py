"""Tests for the write-once per-case content store (corpus split, phase 1)."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import boto3
import pytest
from moto import mock_aws

from fedcourtsai import casestore, corpus

REMOTE_URL = "s3://fcai-test-casestore/casestore/v1"


def _read(t: casestore.InMemoryObjectTransport, key: str) -> bytes:
    body = t.get(key)
    assert body is not None
    return body


def _loads(t: casestore.InMemoryObjectTransport, key: str) -> Any:
    return json.loads(_read(t, key))


def _row(case_id: str = "ca9/64512345", **kwargs: object) -> corpus.CorpusRow:
    court = case_id.split("/", 1)[0]
    return corpus.CorpusRow(case_id=case_id, court=court, docket_number="25-9", **kwargs)


def _doc(kind: str, text: str, fetched_at: date = date(2026, 5, 1)) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="ca9/64512345",
        kind=kind,
        url=f"https://sc.gov/{kind}.pdf",
        fetched_at=fetched_at,
        text=text,
    )


# --- key layout ---------------------------------------------------------------


def test_key_layout_mirrors_case_paths() -> None:
    cid = "scotus/74112233"
    assert casestore.case_key(cid) == "scotus/74112233/case.json"
    assert casestore.events_key(cid) == "scotus/74112233/events.json"
    assert (
        casestore.snapshot_key(cid, date(2026, 5, 1)) == "scotus/74112233/snapshots/2026-05-01.json"
    )
    assert casestore.documents_manifest_key(cid) == "scotus/74112233/documents/documents.json"
    leaf = casestore.document_leaf_key(cid, "petition", date(2026, 5, 1), "abcdef0123456789")
    assert leaf == "scotus/74112233/documents/petition/2026-05-01-abcdef012345.txt"


def test_split_case_id_rejects_malformed() -> None:
    with pytest.raises(casestore.CasestoreError):
        casestore.case_key("not-a-case-id")


def test_parse_s3_url() -> None:
    assert casestore.parse_s3_url("s3://bucket/a/b") == ("bucket", "a/b")
    assert casestore.parse_s3_url("s3://bucket") == ("bucket", "")
    assert casestore.parse_s3_url("s3://bucket/a/b/") == ("bucket", "a/b")
    with pytest.raises(casestore.CasestoreError):
        casestore.parse_s3_url("https://not-s3/x")


# --- serialization + digest ---------------------------------------------------


def test_canonical_json_is_deterministic_and_digest_stable() -> None:
    a = casestore._canonical_json({"b": 1, "a": 2})
    b = casestore._canonical_json({"a": 2, "b": 1})
    assert a == b  # sorted keys → key order does not matter
    assert a.endswith(b"\n")
    assert casestore.digest_bytes(a) == casestore.digest_bytes(b)


# --- in-memory transport ------------------------------------------------------


def test_in_memory_transport_if_absent_skips_existing() -> None:
    t = casestore.InMemoryObjectTransport()
    t.put("k", b"one", if_absent=True)
    t.put("k", b"two", if_absent=True)  # skipped — key present
    assert t.get("k") == b"one"
    assert t.puts == 1
    t.put("k", b"three")  # overwrite allowed without if_absent
    assert t.get("k") == b"three"
    assert t.exists("k") and not t.exists("missing")
    assert t.get("missing") is None


# --- writers ------------------------------------------------------------------


def test_write_case_and_events_round_trip() -> None:
    t = casestore.InMemoryObjectTransport()
    row = _row(case_name="Doe v. Roe")
    ref = casestore.write_case(t, row)
    assert ref.key == "ca9/64512345/case.json"
    stored = _loads(t, ref.key)
    assert stored["case_name"] == "Doe v. Roe"
    assert ref.digest == casestore.digest_bytes(_read(t, ref.key))

    event = corpus.CorpusEvent(
        event_id="evt-appeal-merits", case_id=row.case_id, court="ca9", kind="appeal"
    )
    eref = casestore.write_events(t, row.case_id, [event])
    assert eref.key == "ca9/64512345/events.json"
    assert _loads(t, eref.key)[0]["event_id"] == "evt-appeal-merits"


def test_write_documents_content_addressed_leaf_and_manifest() -> None:
    t = casestore.InMemoryObjectTransport()
    refs = casestore.write_documents(t, "ca9/64512345", [_doc("petition", "the petition text")])
    assert len(refs) == 1
    leaf = refs[0].key
    assert leaf.startswith("ca9/64512345/documents/petition/2026-05-01-")
    assert t.get(leaf) == b"the petition text"

    manifest = _loads(t, casestore.documents_manifest_key("ca9/64512345"))
    entry = manifest["documents"][0]
    assert entry["kind"] == "petition"
    assert entry["text_key"] == leaf
    assert entry["digest"] == refs[0].digest


def test_superseding_document_lands_at_new_leaf_never_overwrites() -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.write_documents(t, "ca9/64512345", [_doc("brief-in-opposition", "first BIO")])
    manifest_key = casestore.documents_manifest_key("ca9/64512345")
    first_leaf = _loads(t, manifest_key)["documents"][0]["text_key"]

    # A corrected BIO with different content on the same day → a new leaf key,
    # the old bytes are never overwritten (write-once).
    casestore.write_documents(t, "ca9/64512345", [_doc("brief-in-opposition", "corrected BIO")])
    second_leaf = _loads(t, manifest_key)["documents"][0]["text_key"]

    assert first_leaf != second_leaf
    assert t.get(first_leaf) == b"first BIO"
    assert t.get(second_leaf) == b"corrected BIO"


def test_identical_document_remirror_uploads_nothing() -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.write_documents(t, "ca9/64512345", [_doc("petition", "same text")])
    puts_after_first = t.puts
    casestore.write_documents(t, "ca9/64512345", [_doc("petition", "same text")])
    # The content-addressed leaf is skipped (if_absent); only the manifest re-writes.
    assert t.puts == puts_after_first + 1


def test_write_documents_collapses_to_one_leaf_per_kind() -> None:
    t = casestore.InMemoryObjectTransport()
    refs = casestore.write_documents(
        t,
        "ca9/64512345",
        [_doc("petition", "stale"), _doc("petition", "current")],
    )
    assert len(refs) == 1  # last of a repeated kind wins
    manifest = _loads(t, casestore.documents_manifest_key("ca9/64512345"))
    assert [e["kind"] for e in manifest["documents"]] == ["petition"]
    assert _read(t, manifest["documents"][0]["text_key"]) == b"current"


def test_mirror_case_writes_the_provided_subset() -> None:
    t = casestore.InMemoryObjectTransport()
    row = _row()
    mirror = casestore.mirror_case(
        t,
        row=row,
        snapshot=(date(2026, 5, 1), {"ProceedingsandOrder": []}),
        documents=[_doc("petition", "p")],
    )
    assert mirror.case.key == "ca9/64512345/case.json"
    assert mirror.events is None  # not provided → no events.json
    assert mirror.snapshot is not None and t.exists(mirror.snapshot.key)
    assert len(mirror.documents) == 1
    assert not t.exists("ca9/64512345/events.json")

    # events=[] writes an explicit empty list (distinct from None).
    mirror2 = casestore.mirror_case(t, row=row, events=[])
    assert mirror2.events is not None
    assert _loads(t, "ca9/64512345/events.json") == []


# --- settings / transport construction ----------------------------------------


def test_transport_from_settings_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEDCOURTS_CASESTORE_URL", raising=False)
    monkeypatch.delenv("CASESTORE_URL", raising=False)
    assert casestore.transport_from_settings() is None


@mock_aws
def test_transport_from_settings_builds_s3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    transport = casestore.transport_from_settings()
    assert isinstance(transport, casestore.S3ObjectTransport)


# --- S3 transport under moto --------------------------------------------------


@mock_aws
def test_s3_transport_put_get_exists_and_prefix() -> None:
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="fcai-test-casestore")
    transport = casestore.S3ObjectTransport("fcai-test-casestore", prefix="casestore/v1")

    transport.put("ca9/1/case.json", b"body")
    assert transport.get("ca9/1/case.json") == b"body"
    assert transport.exists("ca9/1/case.json")
    assert not transport.exists("ca9/1/missing.json")
    assert transport.get("ca9/1/missing.json") is None

    # The prefix is applied to the stored key, not the caller's key.
    listed = client.list_objects_v2(Bucket="fcai-test-casestore")["Contents"]
    assert listed[0]["Key"] == "casestore/v1/ca9/1/case.json"


@mock_aws
def test_s3_transport_if_absent_skips_second_put() -> None:
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="fcai-test-casestore")
    transport = casestore.S3ObjectTransport("fcai-test-casestore")
    transport.put("leaf.txt", b"first", if_absent=True)
    transport.put("leaf.txt", b"second", if_absent=True)
    assert transport.get("leaf.txt") == b"first"


@mock_aws
def test_mirror_case_end_to_end_over_s3() -> None:
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="fcai-test-casestore")
    transport = casestore.S3ObjectTransport("fcai-test-casestore", prefix="casestore/v1")
    row = _row("scotus/74112233")
    casestore.mirror_case(
        transport,
        row=row,
        events=[
            corpus.CorpusEvent(
                event_id="evt-petition-cert", case_id=row.case_id, court="scotus", kind="petition"
            )
        ],
        snapshot=(date(2026, 5, 1), {"ProceedingsandOrder": [{"Text": "Petition filed."}]}),
        documents=[_doc("petition", "p").model_copy(update={"case_id": row.case_id})],
    )
    keys = {o["Key"] for o in client.list_objects_v2(Bucket="fcai-test-casestore")["Contents"]}
    assert "casestore/v1/scotus/74112233/case.json" in keys
    assert "casestore/v1/scotus/74112233/events.json" in keys
    assert "casestore/v1/scotus/74112233/snapshots/2026-05-01.json" in keys
    assert "casestore/v1/scotus/74112233/documents/documents.json" in keys


# --- dual-write hooks through the corpus write seams --------------------------
# (the process transport cache is reset per test by an autouse conftest fixture)


class _BoomTransport:
    """A transport whose writes always fail — to prove mirroring is best-effort."""

    def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
        raise RuntimeError("s3 down")

    def get(self, key: str) -> bytes | None:
        return None

    def exists(self, key: str) -> bool:
        return False

    def list_keys(self, prefix: str) -> list[str]:
        return []


def test_corpus_writes_do_not_mirror_when_flag_off(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FEDCOURTS_CASESTORE_URL", raising=False)
    monkeypatch.delenv("CASESTORE_URL", raising=False)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/1")])
        corpus.upsert_snapshot(conn, "scotus/1", date(2026, 5, 1), {"x": 1})
    assert casestore.active_transport() is None  # dormant → pure no-op


def test_upsert_rows_mirrors_case_json(tmp_path: Any) -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(t)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/74112233", case_name="A v. B")])
    assert _loads(t, "scotus/74112233/case.json")["case_name"] == "A v. B"


def test_upsert_snapshot_mirrors_dated_object(tmp_path: Any) -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(t)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_snapshot(conn, "scotus/1", date(2026, 5, 1), {"ProceedingsandOrder": []})
    assert t.exists("scotus/1/snapshots/2026-05-01.json")


def test_upsert_documents_mirrors_full_set_across_batches(tmp_path: Any) -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(t)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/1",
                    kind="petition",
                    url="u1",
                    fetched_at=date(2026, 5, 1),
                    text="P",
                )
            ],
        )
        # A later batch carries only the BIO; the mirrored manifest must still
        # list BOTH kinds (read-back of the full stored set, not just this batch).
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/1",
                    kind="brief-in-opposition",
                    url="u2",
                    fetched_at=date(2026, 5, 2),
                    text="B",
                )
            ],
        )
    manifest = _loads(t, "scotus/1/documents/documents.json")
    assert sorted(e["kind"] for e in manifest["documents"]) == ["brief-in-opposition", "petition"]


def test_upsert_events_mirrors_full_set(tmp_path: Any) -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(t)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-cert",
                    case_id="scotus/1",
                    court="scotus",
                    kind="petition",
                )
            ],
        )
    assert _loads(t, "scotus/1/events.json")[0]["event_id"] == "evt-petition-cert"


def test_mirror_failure_never_breaks_the_corpus_write(tmp_path: Any) -> None:
    casestore.set_active_transport(_BoomTransport())
    with corpus.connect(tmp_path / "c.db") as conn:
        # The corpus write must succeed even though every mirror put raises.
        assert corpus.upsert_rows(conn, [_row("scotus/1")]) == 1
        assert corpus.count(conn) == 1


def test_read_back_skipped_when_flag_off(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """With the store off, the documents/events read-back must not even run."""
    monkeypatch.delenv("FEDCOURTS_CASESTORE_URL", raising=False)
    monkeypatch.delenv("CASESTORE_URL", raising=False)
    calls: list[str] = []
    real = corpus.documents_for_case

    def spy(conn: corpus.ReadConnection, case_id: str) -> list[corpus.CaseDocument]:
        calls.append(case_id)
        return real(conn, case_id)

    monkeypatch.setattr(casestore, "documents_for_case", spy)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/1",
                    kind="petition",
                    url="u",
                    fetched_at=date(2026, 5, 1),
                    text="P",
                )
            ],
        )
    assert calls == []  # the read-back is guarded behind the transport check


def test_malformed_casestore_url_disables_store_not_ingestion(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fat-fingered flag disables the store; it must never crash a corpus write."""
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", "not-an-s3-url")
    casestore.reset_active_transport()
    with corpus.connect(tmp_path / "c.db") as conn:
        assert corpus.upsert_rows(conn, [_row("scotus/1")]) == 1  # ingestion succeeds
        assert corpus.count(conn) == 1
    assert casestore.active_transport() is None  # store disabled, not raised


def test_set_event_resolved_re_mirrors_events(tmp_path: Any) -> None:
    """Resolving an event re-mirrors the case's events.json (a direct UPDATE the
    upsert hook never sees)."""
    t = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(t)
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-cert",
                    case_id="scotus/1",
                    court="scotus",
                    kind="petition",
                )
            ],
        )
        assert _loads(t, "scotus/1/events.json")[0]["resolved"] is False
        corpus.set_event_resolved(conn, "scotus/1", "evt-petition-cert", resolved=True)
        assert _loads(t, "scotus/1/events.json")[0]["resolved"] is True
