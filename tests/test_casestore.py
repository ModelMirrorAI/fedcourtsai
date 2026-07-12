"""Tests for the write-once per-case content store (corpus split, phase 1)."""

from __future__ import annotations

import json
from datetime import date

import boto3
import pytest
from moto import mock_aws

from fedcourtsai import casestore, corpus

REMOTE_URL = "s3://fcai-test-casestore/casestore/v1"


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
    stored = json.loads(t.get(ref.key))
    assert stored["case_name"] == "Doe v. Roe"
    assert ref.digest == casestore.digest_bytes(t.get(ref.key))

    event = corpus.CorpusEvent(
        event_id="evt-appeal-merits", case_id=row.case_id, court="ca9", kind="appeal"
    )
    eref = casestore.write_events(t, row.case_id, [event])
    assert eref.key == "ca9/64512345/events.json"
    assert json.loads(t.get(eref.key))[0]["event_id"] == "evt-appeal-merits"


def test_write_documents_content_addressed_leaf_and_manifest() -> None:
    t = casestore.InMemoryObjectTransport()
    refs = casestore.write_documents(t, "ca9/64512345", [_doc("petition", "the petition text")])
    assert len(refs) == 1
    leaf = refs[0].key
    assert leaf.startswith("ca9/64512345/documents/petition/2026-05-01-")
    assert t.get(leaf) == b"the petition text"

    manifest = json.loads(t.get(casestore.documents_manifest_key("ca9/64512345")))
    entry = manifest["documents"][0]
    assert entry["kind"] == "petition"
    assert entry["text_key"] == leaf
    assert entry["digest"] == refs[0].digest


def test_superseding_document_lands_at_new_leaf_never_overwrites() -> None:
    t = casestore.InMemoryObjectTransport()
    casestore.write_documents(t, "ca9/64512345", [_doc("brief-in-opposition", "first BIO")])
    first_leaf = json.loads(t.get(casestore.documents_manifest_key("ca9/64512345")))["documents"][
        0
    ]["text_key"]

    # A corrected BIO with different content on the same day → a new leaf key,
    # the old bytes are never overwritten (write-once).
    casestore.write_documents(t, "ca9/64512345", [_doc("brief-in-opposition", "corrected BIO")])
    second_leaf = json.loads(t.get(casestore.documents_manifest_key("ca9/64512345")))["documents"][
        0
    ]["text_key"]

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
    assert json.loads(t.get("ca9/64512345/events.json")) == []


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
