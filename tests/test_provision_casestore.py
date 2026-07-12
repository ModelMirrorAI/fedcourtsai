"""Casestore-backed provisioning parity (corpus split, phase 3).

Proves the casestore provisioning source returns the same shapes as the corpus,
and that the `provision-snapshot` / `materialize-event` commands materialize a
byte-identical `record/` whether they read the blob or the per-case content store.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus, provision
from fedcourtsai.cli import app
from fedcourtsai.fixture import build_fixture_corpus

runner = CliRunner()


def _case_with_event_and_snapshot(src: Path) -> tuple[str, str]:
    """A fixture case id + one of its event ids (has both a snapshot and an event)."""
    with corpus.connect(src) as conn:
        case_id = conn.execute(
            "SELECT e.case_id FROM events e JOIN snapshots s ON e.case_id = s.case_id "
            "ORDER BY e.case_id LIMIT 1"
        ).fetchone()[0]
        event_id = conn.execute(
            "SELECT event_id FROM events WHERE case_id = ? ORDER BY event_id LIMIT 1", (case_id,)
        ).fetchone()[0]
    return case_id, event_id


def _add_document(src: Path, case_id: str) -> None:
    # Text without a trailing newline, to exercise the leaf round-trip through
    # write_text (which adds the newline the leaf does not store).
    with corpus.connect(src) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=case_id,
                    kind="petition",
                    url="https://sc.gov/p.pdf",
                    fetched_at=date(2026, 5, 1),
                    text="petition body text",
                )
            ],
        )


def _tree(root: Path) -> dict[str, bytes]:
    """Every file under ``root`` as {relative path: bytes}, for a byte-level diff."""
    return {
        str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()
    }


def test_casestore_source_matches_corpus_reads(tmp_path: Path) -> None:
    """The casestore source returns identical shapes to the corpus read functions."""
    transport = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(transport)  # dual-write the fixture into this store
    src = tmp_path / "corpus.db"
    build_fixture_corpus(src)
    case_id, _ = _case_with_event_and_snapshot(src)
    _add_document(src, case_id)

    source = provision.CasestoreSource(transport)
    with corpus.connect(src) as conn:
        assert source.latest_snapshot(case_id) == corpus.latest_snapshot(conn, case_id)
        assert source.documents_for_case(case_id) == corpus.documents_for_case(conn, case_id)
        assert source.events_for_case(case_id) == corpus.events_for_case(conn, case_id)


@mock_aws
def test_provision_record_is_byte_identical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="fcai-prov")
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", "s3://fcai-prov/casestore/v1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    src = corpus.corpus_db_path(corpus_root)
    casestore.set_active_transport(casestore.transport_from_settings())  # mirror to moto S3
    build_fixture_corpus(src)
    case_id, event_id = _case_with_event_and_snapshot(src)
    _add_document(src, case_id)
    casestore.reset_active_transport()  # the CLI builds its own transport from the env

    court, docket = case_id.split("/")

    def provision_record(backend: str, data_root: Path) -> dict[str, bytes]:
        monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
        monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
        base = ["--court", court, "--docket", docket, "--corpus-backend", backend]
        snap = runner.invoke(app, ["provision-snapshot", *base])
        assert snap.exit_code == 0, snap.stderr
        evt = runner.invoke(app, ["materialize-event", *base, "--event", event_id])
        assert evt.exit_code == 0, evt.stderr
        return _tree(data_root)

    blob_tree = provision_record("local", tmp_path / "blob")
    casestore_tree = provision_record("casestore", tmp_path / "cs")
    assert blob_tree  # provisioning actually wrote a record/ (snapshot + event + document)
    assert blob_tree == casestore_tree


def test_connect_readonly_rejects_casestore(tmp_path: Path) -> None:
    with (
        pytest.raises(ValueError, match="casestore"),
        corpus.connect_readonly(tmp_path / "c.db", backend="casestore"),
    ):
        pass


def test_casestore_backend_without_url_exits_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FEDCOURTS_CASESTORE_URL", raising=False)
    monkeypatch.delenv("CASESTORE_URL", raising=False)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path))
    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "1",
            "--corpus-backend",
            "casestore",
        ],
    )
    assert result.exit_code == 2
    assert "FEDCOURTS_CASESTORE_URL" in result.stderr
