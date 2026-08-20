"""The whole-file corpus transport (``fedcourtsai.corpus_remote``), fully offline.

Everything runs against an in-memory transport injected through the seam —
no boto3, no network — mirroring how the casestore and ranged-backend tests
keep S3 out of the unit suite.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from fedcourtsai import corpus, corpus_ranged, corpus_remote
from fedcourtsai.cli import app

REMOTE_URL = "s3://test-bucket/store"


class InMemoryFileTransport:
    """A dict-backed whole-file transport, counting uploads for idempotency checks."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.uploads = 0

    def upload(self, key: str, source: Path) -> None:
        self.objects[key] = source.read_bytes()
        self.uploads += 1

    def download(self, key: str, dest: Path) -> None:
        if key not in self.objects:
            raise FileNotFoundError(key)
        dest.write_bytes(self.objects[key])

    def exists(self, key: str) -> bool:
        return key in self.objects


def _blob(tmp_path: Path, content: bytes = b"corpus index bytes") -> Path:
    db = tmp_path / "corpus.db"
    db.write_bytes(content)
    return db


# --- upload: content addressing, put-if-absent, pointer rewrite -------------------


def test_upload_publishes_content_addressed_and_writes_pointer(tmp_path: Path) -> None:
    db = _blob(tmp_path)
    transport = InMemoryFileTransport()

    pointer = corpus_remote.upload_index(db, REMOTE_URL, transport=transport)

    sha256 = hashlib.sha256(db.read_bytes()).hexdigest()
    assert pointer.key == f"index/sha256/{sha256}"
    assert pointer.size == db.stat().st_size
    assert pointer.sha256 == sha256
    assert transport.objects[f"store/index/sha256/{sha256}"] == db.read_bytes()
    # The committed pointer round-trips through the ranged resolver.
    written = corpus_ranged.read_index_pointer(corpus_remote.pointer_path_for(db))
    assert written == pointer


def test_upload_is_put_if_absent(tmp_path: Path) -> None:
    db = _blob(tmp_path)
    transport = InMemoryFileTransport()
    corpus_remote.upload_index(db, REMOTE_URL, transport=transport)
    corpus_remote.upload_index(db, REMOTE_URL, transport=transport)
    # The content-addressed key already holds identical bytes: no re-upload.
    assert transport.uploads == 1
    # New content publishes a NEW object; the old version stays (add-only remote).
    db.write_bytes(b"new corpus bytes")
    corpus_remote.upload_index(db, REMOTE_URL, transport=transport)
    assert transport.uploads == 2
    assert len(transport.objects) == 2


def test_upload_without_blob_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(corpus_remote.CorpusRemoteError, match="nothing to push"):
        corpus_remote.upload_index(
            tmp_path / "corpus.db", REMOTE_URL, transport=InMemoryFileTransport()
        )


# --- download: checksum-on-pull -----------------------------------------------------


def test_download_round_trip_verifies_sha256(tmp_path: Path) -> None:
    db = _blob(tmp_path)
    transport = InMemoryFileTransport()
    corpus_remote.upload_index(db, REMOTE_URL, transport=transport)
    original = db.read_bytes()
    db.unlink()

    remote = corpus_remote.download_index(
        corpus_remote.pointer_path_for(db), REMOTE_URL, db, transport=transport
    )

    assert db.read_bytes() == original
    assert remote.checksum == hashlib.sha256(original).hexdigest()
    assert not db.with_name(db.name + ".partial").exists()


def test_download_digest_mismatch_fails_loudly_and_leaves_no_file(tmp_path: Path) -> None:
    db = _blob(tmp_path)
    transport = InMemoryFileTransport()
    corpus_remote.upload_index(db, REMOTE_URL, transport=transport)
    db.unlink()
    # Corrupt the stored object: the pull must fail loudly, never landing the file.
    (key,) = transport.objects
    transport.objects[key] = b"corrupted bytes of the same origin"

    with pytest.raises(corpus_remote.CorpusRemoteError, match="does not match the pointer"):
        corpus_remote.download_index(
            corpus_remote.pointer_path_for(db), REMOTE_URL, db, transport=transport
        )
    assert not db.exists()
    assert not db.with_name(db.name + ".partial").exists()


def test_download_size_mismatch_fails_loudly(tmp_path: Path) -> None:
    db = _blob(tmp_path)
    transport = InMemoryFileTransport()
    pointer = corpus_remote.upload_index(db, REMOTE_URL, transport=transport)
    db.unlink()
    # Same-prefix truncation: size drifts while the pointer still names the digest.
    full_key = f"store/{pointer.key}"
    transport.objects[full_key] = transport.objects[full_key][:-1]

    with pytest.raises(corpus_remote.CorpusRemoteError, match="does not match the pointer"):
        corpus_remote.download_index(
            corpus_remote.pointer_path_for(db), REMOTE_URL, db, transport=transport
        )
    assert not db.exists()


# --- pointer file round-trip and validation ------------------------------------------


def test_pointer_write_read_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "corpus.db.ref"
    pointer = corpus_ranged.IndexPointer(key="index/sha256/" + "a" * 64, size=7, sha256="a" * 64)
    corpus_remote.write_pointer(path, pointer)
    assert corpus_ranged.read_index_pointer(path) == pointer
    # Deterministic serialization: sorted keys, trailing newline (minimal diffs).
    payload = json.loads(path.read_text())
    assert list(payload) == sorted(payload)
    assert path.read_text().endswith("}\n")


def test_digest_file_streams_digest_and_size(tmp_path: Path) -> None:
    blob = tmp_path / "blob"
    blob.write_bytes(b"x" * 1000)
    digest, size = corpus_remote.digest_file(blob)
    assert digest == hashlib.sha256(b"x" * 1000).hexdigest()
    assert size == 1000


# --- the boto3 transport (moto) and the CLI commands ---------------------------------


@mock_aws
def test_s3_transport_round_trip(tmp_path: Path) -> None:
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
    db = _blob(tmp_path)

    pointer = corpus_remote.upload_index(db, REMOTE_URL)
    original = db.read_bytes()
    db.unlink()
    corpus_remote.download_index(corpus_remote.pointer_path_for(db), REMOTE_URL, db)

    assert db.read_bytes() == original
    transport = corpus_remote.S3FileTransport("test-bucket")
    assert transport.exists(f"store/{pointer.key}")
    assert not transport.exists("store/index/sha256/absent")


def test_cli_corpus_pull_missing_pointer_modes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)

    warned = CliRunner().invoke(app, ["corpus-pull", "--missing-pointer", "warn"])
    assert warned.exit_code == 0, warned.output
    assert "No corpus pointer yet" in warned.stdout

    failed = CliRunner().invoke(app, ["corpus-pull"])
    assert failed.exit_code == 1
    assert "no corpus pointer" in failed.stderr


def test_cli_corpus_push_requires_remote_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    for name in (
        "FEDCOURTS_CORPUS_REMOTE_URL",
        "CORPUS_REMOTE_URL",
        "FEDCOURTS_DVC_REMOTE_URL",
        "DVC_REMOTE_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    result = CliRunner().invoke(app, ["corpus-push"])
    assert result.exit_code == 1
    assert "CORPUS_REMOTE_URL" in result.stderr


def test_cli_corpus_push_refuses_under_pointer_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A writer owns the committed pointer; an environment that overrides reads
    # would push to one pair while reading another, so the mixture is refused.
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv(
        "FEDCOURTS_CORPUS_POINTER",
        json.dumps(
            {
                "key": "index/sha256/" + "a" * 64,
                "size": 7,
                "sha256": "a" * 64,
                "schema_version": "1.0",
            }
        ),
    )
    result = CliRunner().invoke(app, ["corpus-push"])
    assert result.exit_code == 1
    assert "refuses" in result.stderr


@mock_aws
def test_cli_corpus_pull_honors_pointer_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With the override set, the pull needs no committed pointer at all.

    The staging-read shape: the pair's pointer arrives out of band, the
    checkout's `.ref` (absent here, production's in a real checkout) is not
    consulted, and the download still verifies digest + size.
    """
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    db = corpus_root / "corpus.db"
    with corpus.connect(db):  # a real (empty) corpus, so corpus-info can open it
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    published = corpus_remote.upload_index(db, REMOTE_URL)
    original = db.read_bytes()
    db.unlink()
    corpus_remote.pointer_path_for(db).unlink()
    monkeypatch.setenv(
        "FEDCOURTS_CORPUS_POINTER",
        json.dumps(
            {
                "key": published.key,
                "size": published.size,
                "sha256": published.sha256,
                "schema_version": "1.0",
            }
        ),
    )
    # `--missing-pointer warn` governs only the committed file, so it is inert
    # here: the override still names what to pull.
    pulled = CliRunner().invoke(app, ["corpus-pull", "--missing-pointer", "warn"])
    assert pulled.exit_code == 0, pulled.output
    assert "No corpus pointer yet" not in pulled.stdout
    assert db.read_bytes() == original
    assert "sha256-verified" in pulled.stdout
    # The pull records its provenance durably: the sidecar carries the
    # override's digest, so a later shell without the override can tell the
    # blob on disk is not the committed ref's.
    sidecar = corpus_remote.pulled_pointer_path_for(db)
    assert corpus_ranged.read_index_pointer(sidecar).sha256 == published.sha256
    # Simulate that later shell: override gone, a committed ref naming some
    # OTHER blob present — the local freshness surface must disclose the drift.
    monkeypatch.delenv("FEDCOURTS_CORPUS_POINTER", raising=False)
    other = corpus_ranged.IndexPointer(key="index/sha256/" + "b" * 64, size=9, sha256="b" * 64)
    corpus_remote.write_pointer(corpus_remote.pointer_path_for(db), other)
    info = CliRunner().invoke(app, ["corpus-info"])
    assert info.exit_code == 0, info.output
    assert "blob on disk is not the committed ref's" in info.stdout
    assert published.sha256 in info.stdout
    # And with the committed ref matching the pulled blob, no drift line.
    corpus_remote.write_pointer(
        corpus_remote.pointer_path_for(db),
        corpus_ranged.IndexPointer(key=published.key, size=published.size, sha256=published.sha256),
    )
    clean = CliRunner().invoke(app, ["corpus-info"])
    assert clean.exit_code == 0, clean.output
    assert "blob on disk is not the committed ref's" not in clean.stdout


@mock_aws
def test_cli_corpus_info_disclosure_names_the_blob_actually_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `pointer:` line under the override: digest under ranged, a
    not-read note under local — never the override digest beside a local
    file's freshness."""
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    db = corpus_root / "corpus.db"
    with corpus.connect(db):  # a real (empty) corpus in the ranged-read layout
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    published = corpus_remote.upload_index(db, REMOTE_URL)
    corpus_remote.pointer_path_for(db).unlink()
    monkeypatch.setenv(
        "FEDCOURTS_CORPUS_POINTER",
        json.dumps(
            {
                "key": published.key,
                "size": published.size,
                "sha256": published.sha256,
                "schema_version": "1.0",
            }
        ),
    )
    ranged = CliRunner().invoke(app, ["corpus-info", "--corpus-backend", "ranged"])
    assert ranged.exit_code == 0, ranged.output
    assert f"pointer: out-of-band override (sha256 {published.sha256})" in ranged.stdout
    local = CliRunner().invoke(app, ["corpus-info", "--corpus-backend", "local"])
    assert local.exit_code == 0, local.output
    assert "override set (not read by the local backend)" in local.stdout
    assert published.sha256 not in local.stdout


@mock_aws
def test_cli_corpus_push_then_pull_round_trip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The writer sequence end to end: push publishes + rewrites the pointer, pull verifies.

    Also proves the legacy DVC_REMOTE_URL env alias still selects the remote,
    so the repo variable can be renamed later without a lockstep change.
    """
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    db = corpus_root / "corpus.db"
    with corpus.connect(db):  # a real (empty) corpus in the ranged-read layout
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    # Exercise the lowest-priority legacy alias; clear the names that outrank
    # it so an ambient value (a developer's real remote) cannot shadow moto's.
    for name in ("FEDCOURTS_CORPUS_REMOTE_URL", "CORPUS_REMOTE_URL", "FEDCOURTS_DVC_REMOTE_URL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DVC_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    pushed = CliRunner().invoke(app, ["corpus-push"])
    assert pushed.exit_code == 0, pushed.output
    assert corpus_remote.pointer_path_for(db).is_file()

    original = db.read_bytes()
    db.unlink()
    pulled = CliRunner().invoke(app, ["corpus-pull"])
    assert pulled.exit_code == 0, pulled.output
    assert db.read_bytes() == original
    assert "sha256-verified" in pulled.stdout
