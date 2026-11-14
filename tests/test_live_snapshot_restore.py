"""Tests for the live-snapshot restore (`restore-replaced-live-snapshots`)."""

from __future__ import annotations

import io
import json
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.live_snapshot_restore import (
    RestoreUnavailable,
    restore_replaced_live_snapshots,
)

LIVE = {"ProceedingsandOrder": [{"Text": "Petition filed."}]}
REFRESH = {"id": 1, "docket_entries": []}
DAY = date(2026, 11, 13)


def _body(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True).encode()


def _seed(db: Path, rows: list[tuple[str, str | None, str | None]]) -> None:
    with corpus.connect(db) as conn:
        for case_id, pulled, polled in rows:
            conn.execute(
                "INSERT INTO cases (case_id, court, last_pulled, last_live_polled) "
                "VALUES (?, 'scotus', ?, ?)",
                (case_id, pulled, polled),
            )
        conn.commit()


def _store(
    transport: casestore.InMemoryObjectTransport,
    case_id: str,
    day: date,
    *bodies: Mapping[str, object],
) -> str:
    key = casestore.snapshot_key(case_id, day)
    for body in bodies:
        transport.put(key, _body(body))
    return key


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(
        path,
        [
            ("scotus/1", "2026-11-13", "2026-11-13"),
            ("scotus/2", "2026-11-13", "2026-11-13"),
            ("scotus/3", "2026-11-13", "2026-11-13"),
            ("scotus/4", None, "2026-11-13"),
        ],
    )
    return path


def test_a_replaced_live_snapshot_is_planned_and_restored(db: Path) -> None:
    transport = casestore.InMemoryObjectTransport()
    replaced = _store(transport, "scotus/1", DAY, LIVE, REFRESH)
    # The live poll ran last here: the key already serves the Court's docket.
    kept = _store(transport, "scotus/2", DAY, REFRESH, LIVE)
    # Two refreshes on one day: nothing live was ever stored.
    _store(transport, "scotus/3", DAY, REFRESH, REFRESH)
    # A row only the live channel has read is never listed.
    _store(transport, "scotus/4", DAY, LIVE, REFRESH)
    with corpus.connect(db) as conn:
        dry = restore_replaced_live_snapshots(conn, transport, apply=False)
    assert [(r.case_id, r.snapshot_date) for r in dry.restores] == [("scotus/1", DAY)]
    assert (dry.cases_read, dry.rewritten_keys, dry.live_current, dry.no_live_version) == (
        3,
        3,
        1,
        1,
    )
    assert dry.cases_without_live_snapshot == 1
    assert not dry.applied
    assert json.loads(transport.objects[replaced]) == REFRESH

    with corpus.connect(db) as conn:
        applied = restore_replaced_live_snapshots(conn, transport, apply=True, max_restores=1)
    assert applied.applied
    assert json.loads(transport.objects[replaced]) == LIVE
    assert json.loads(transport.objects[kept]) == LIVE
    # The displaced refresh stays behind as an earlier version.
    assert [json.loads(b) for b in transport.history[replaced]] == [LIVE, REFRESH, LIVE]

    with corpus.connect(db) as conn:
        again = restore_replaced_live_snapshots(conn, transport, apply=False)
    assert again.total_restores == 0


def test_the_newest_live_version_is_the_one_restored(db: Path) -> None:
    transport = casestore.InMemoryObjectTransport()
    later = {"ProceedingsandOrder": [{"Text": "Petition filed."}, {"Text": "Waiver filed."}]}
    key = _store(transport, "scotus/1", DAY, LIVE, later, REFRESH)
    with corpus.connect(db) as conn:
        restore_replaced_live_snapshots(conn, transport, apply=True, max_restores=1)
    assert json.loads(transport.objects[key]) == later


def test_a_case_with_a_live_snapshot_on_another_day_is_not_counted_bare(db: Path) -> None:
    transport = casestore.InMemoryObjectTransport()
    _store(transport, "scotus/1", DAY, LIVE, REFRESH)
    _store(transport, "scotus/1", date(2026, 11, 10), LIVE)
    with corpus.connect(db) as conn:
        dry = restore_replaced_live_snapshots(conn, transport, apply=False)
    assert dry.total_restores == 1
    assert dry.cases_without_live_snapshot == 0


def test_an_apply_above_its_bound_writes_nothing(db: Path) -> None:
    transport = casestore.InMemoryObjectTransport()
    first = _store(transport, "scotus/1", DAY, LIVE, REFRESH)
    _store(transport, "scotus/2", DAY, LIVE, REFRESH)
    with corpus.connect(db) as conn:
        refused = restore_replaced_live_snapshots(conn, transport, apply=True, max_restores=1)
    assert refused.refused and not refused.applied
    assert json.loads(transport.objects[first]) == REFRESH


def test_a_transport_without_version_reads_is_refused(db: Path) -> None:
    class Plain:
        def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None: ...
        def get(self, key: str) -> bytes | None:
            return None

        def exists(self, key: str) -> bool:
            return False

        def list_keys(self, prefix: str) -> list[str]:
            return []

    with corpus.connect(db) as conn, pytest.raises(RestoreUnavailable):
        restore_replaced_live_snapshots(conn, Plain(), apply=False)


def test_the_command_plans_then_applies_under_a_bound(
    db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transport = casestore.InMemoryObjectTransport()
    key = _store(transport, "scotus/1", DAY, LIVE, REFRESH)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(db.parent))
    runner = CliRunner()
    with casestore.transport_override(transport):
        dry = runner.invoke(app, ["restore-replaced-live-snapshots"])
        assert dry.exit_code == 0, dry.output
        assert "would restore 1 case-day(s) on 1 case(s)" in dry.output
        assert "scotus/1 2026-11-13" in dry.output
        unbounded = runner.invoke(app, ["restore-replaced-live-snapshots", "--apply"])
        assert unbounded.exit_code == 2
        refused = runner.invoke(
            app, ["restore-replaced-live-snapshots", "--apply", "--max-restores", "0"]
        )
        assert refused.exit_code == 1
        assert json.loads(transport.objects[key]) == REFRESH
        applied = runner.invoke(
            app, ["restore-replaced-live-snapshots", "--apply", "--max-restores", "1"]
        )
        assert applied.exit_code == 0, applied.output
    assert json.loads(transport.objects[key]) == LIVE


class _StubS3Error(Exception):
    def __init__(self, code: str) -> None:
        super().__init__("upstream text naming an account, a role and a bucket")
        self.response = {"Error": {"Code": code}}


class _StubS3Client:
    """The two calls the version reads make, with canned pages."""

    def __init__(self, *, refuse: str | None = None) -> None:
        self.refuse = refuse
        self.asked: list[dict[str, str]] = []

    def get_paginator(self, name: str) -> _StubS3Client:
        assert name == "list_object_versions"
        return self

    def paginate(self, **kwargs: str) -> list[dict[str, object]]:
        self.asked.append(kwargs)
        if self.refuse:
            raise _StubS3Error(self.refuse)
        stamp = datetime(2026, 11, 13, 19, tzinfo=UTC)
        return [
            {
                "Versions": [
                    {
                        "Key": "pre/a/1.json",
                        "VersionId": "v2",
                        "IsLatest": True,
                        "LastModified": stamp,
                    }
                ]
            },
            {
                "Versions": [
                    {
                        "Key": "pre/a/1.json",
                        "VersionId": "v1",
                        "IsLatest": False,
                        "LastModified": stamp,
                    }
                ],
                "DeleteMarkers": [{"Key": "pre/a/2.json"}],
            },
        ]

    def get_object(self, **kwargs: str) -> dict[str, object]:
        self.asked.append(kwargs)
        if kwargs["VersionId"] == "gone":
            raise _StubS3Error("NoSuchVersion")
        if self.refuse:
            raise _StubS3Error(self.refuse)
        return {"Body": io.BytesIO(b"body")}


def _s3_transport(client: _StubS3Client) -> casestore.S3ObjectTransport:
    transport = object.__new__(casestore.S3ObjectTransport)
    transport._bucket = "bucket"
    transport._prefix = "pre"
    transport._client = client
    transport._ClientError = _StubS3Error
    return transport


def test_the_s3_transport_lists_versions_across_pages_and_reads_one() -> None:
    client = _StubS3Client()
    transport = _s3_transport(client)
    versions = transport.list_versions("a/")
    # Keys come back logical (prefix stripped), delete markers are not versions.
    assert [(v.key, v.version_id, v.is_latest) for v in versions] == [
        ("a/1.json", "v2", True),
        ("a/1.json", "v1", False),
    ]
    assert client.asked[0] == {"Bucket": "bucket", "Prefix": "pre/a/"}
    assert transport.get_version("a/1.json", "v1") == b"body"
    assert client.asked[-1] == {"Bucket": "bucket", "Key": "pre/a/1.json", "VersionId": "v1"}
    assert transport.get_version("a/1.json", "gone") is None


def test_a_refused_version_read_names_the_grant_and_nothing_else(db: Path) -> None:
    transport = _s3_transport(_StubS3Client(refuse="AccessDenied"))
    with corpus.connect(db) as conn, pytest.raises(RestoreUnavailable) as refused:
        restore_replaced_live_snapshots(conn, transport, apply=False)
    assert "s3:ListBucketVersions" in str(refused.value)
    assert "account" not in str(refused.value)
    assert refused.value.__cause__ is None


def test_an_unparseable_current_version_is_counted_not_restored(db: Path) -> None:
    transport = casestore.InMemoryObjectTransport()
    key = casestore.snapshot_key("scotus/1", DAY)
    transport.put(key, _body(LIVE))
    transport.put(key, b"not json")
    with corpus.connect(db) as conn:
        dry = restore_replaced_live_snapshots(conn, transport, apply=False)
    assert (dry.unreadable, dry.total_restores) == (1, 0)


def test_the_ledger_carries_no_version_ids(db: Path) -> None:
    transport = casestore.InMemoryObjectTransport()
    _store(transport, "scotus/1", DAY, LIVE, REFRESH)
    with corpus.connect(db) as conn:
        dry = restore_replaced_live_snapshots(conn, transport, apply=False)
    assert "version_id" not in dry.model_dump_json()
