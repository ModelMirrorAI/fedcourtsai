"""The fixed corpus read set behind ``fedcourts corpus-integration-check``.

Exercises :mod:`fedcourtsai.integration_check` over the fixture corpus on the
local backend, and over moto's S3 stand-in on the ranged backend — the offline
mirror of what the integration-corpus workflow dispatches against the real
remote. No test touches the network.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from fedcourtsai import corpus, corpus_ranged
from fedcourtsai.cli import app
from fedcourtsai.fixture import build_fixture_corpus
from fedcourtsai.integration_check import IntegrationReport, render_markdown, run_integration_check

REMOTE_URL = "s3://test-bucket/store"

# ca9/103 is the fixture's open-event appeals case: an open event, resolved
# priors in the same court, and a stored snapshot — the shape the check wants.
COURT, DOCKET = "ca9", 103


@pytest.fixture
def corpus_db(tmp_path: Path) -> Path:
    """A freshly built synthetic fixture corpus."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    build_fixture_corpus(db)
    return db


def _check(corpus_db: Path, **kwargs: object) -> IntegrationReport:
    return run_integration_check(
        corpus_db_path=corpus_db,
        court=COURT,
        docket=DOCKET,
        **kwargs,  # type: ignore[arg-type]
    )


def test_known_case_passes_every_read(corpus_db: Path) -> None:
    report = _check(corpus_db)

    assert report.ok and report.within_budget
    assert report.case_id == f"{COURT}/{DOCKET}"
    assert report.backend == "local"
    assert [s.ok for s in report.steps] == [True, True, True]
    # The local backend transfers nothing, so it carries no counters.
    assert all(s.gets is None and s.bytes_fetched is None for s in report.steps)
    assert "evt-appeal-disposition" in report.steps[0].detail


def test_snapshot_out_materializes_the_snapshot(corpus_db: Path, tmp_path: Path) -> None:
    dest = tmp_path / "snapshot.json"
    report = _check(corpus_db, snapshot_out=dest)

    assert report.ok
    payload = json.loads(dest.read_text())
    assert isinstance(payload, dict) and payload


def test_unknown_case_fails_the_point_reads(corpus_db: Path) -> None:
    report = run_integration_check(corpus_db_path=corpus_db, court="ca9", docket=99999999, limit=5)

    assert not report.ok
    by_name = {s.name: s for s in report.steps}
    assert not by_name["open-events"].ok
    assert not by_name["provision-snapshot"].ok
    # The priors read filters by court, not case, so it still succeeds.
    assert by_name["priors (court ca9, limit 5)"].ok


def test_blown_budget_fails_the_report(corpus_db: Path) -> None:
    report = _check(corpus_db, budget_seconds=0.0)

    assert not report.within_budget
    assert not report.ok
    assert all(s.ok for s in report.steps), "the reads themselves still pass"


def test_markdown_summary_names_every_read(corpus_db: Path) -> None:
    summary = render_markdown(_check(corpus_db))

    assert f"Corpus integration check — {COURT}/{DOCKET} [local]" in summary
    assert "| open-events | ok |" in summary
    assert "| provision-snapshot | ok |" in summary
    assert "within the 300s budget" in summary


def _stage_ranged_remote(db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Publish the corpus blob to moto's S3 and point the env at it, ranged."""
    blob = db.read_bytes()
    md5 = hashlib.md5(blob).hexdigest()
    pointer = db.with_name(db.name + ".dvc")
    pointer.write_text(
        f"outs:\n- md5: {md5}\n  size: {len(blob)}\n  hash: md5\n  path: {db.name}\n"
    )
    remote = corpus_ranged.resolve_pointer(pointer, REMOTE_URL)
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=remote.bucket)
    client.put_object(Bucket=remote.bucket, Key=remote.key, Body=blob)
    db.unlink()  # ranged access must not need (or recreate) the local blob
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.setenv("FEDCOURTS_DVC_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@mock_aws
def test_ranged_backend_reports_transfer_counters(
    corpus_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stage_ranged_remote(corpus_db, monkeypatch)

    report = _check(corpus_db)

    assert report.ok
    assert report.backend == "ranged"
    for step in report.steps:
        assert step.gets is not None and step.gets > 0
        assert step.bytes_fetched is not None and step.bytes_fetched > 0
    assert "GET(s)" in render_markdown(report)
    assert not corpus_db.exists(), "the ranged check must not create a local corpus file"


def test_cli_writes_summary_and_exits_by_verdict(corpus_db: Path, tmp_path: Path) -> None:
    summary_out = tmp_path / "summary.md"
    args = [
        "corpus-integration-check",
        "--court",
        COURT,
        "--docket",
        str(DOCKET),
        "--summary-out",
        str(summary_out),
    ]
    env = {"FEDCOURTS_CORPUS_ROOT": str(corpus_db.parent)}

    passed = CliRunner().invoke(app, args, env=env)
    assert passed.exit_code == 0, passed.output
    assert json.loads(passed.stdout)["ok"] is True
    assert "Corpus integration check" in summary_out.read_text()

    failed = CliRunner().invoke(
        app,
        ["corpus-integration-check", "--court", COURT, "--docket", "99999999"],
        env=env,
    )
    assert failed.exit_code == 1
