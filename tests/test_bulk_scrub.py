"""The bulk-cluster scrub: the ingest carve-out, converged onto stored rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.bulk_scrub import scrub_bulk_cluster_fields

runner = CliRunner()


def _row(case_id: str, court: str, **fields: object) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate({"case_id": case_id, "court": court, **fields})


_GARBAGE = {
    "summary": "Appeal from the Circuit Court of the City of St. Louis.",
    "precedential_status": "2 B. & C. 44.8-471; Thurston et al. v. Rosenfield",
    "judges": ["Bruce, McCobmick, Pabdeb"],
    "citation_count": 3,
    "citations": ["1 How. 1"],
}


def _seeded(tmp_path: Path) -> Path:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # The bulk shape: a never-pulled circuit row carrying the
                # misjoined cluster fields.
                _row("ca1/1883", "ca1", **_GARBAGE),
                # A REST-refreshed circuit row: its fields were re-projected
                # from the API's sound join on the pull, so they are kept.
                _row(
                    "ca1/100051",
                    "ca1",
                    precedential_status="Published",
                    judges=["barron"],
                    last_pulled=date(2026, 7, 3),
                ),
                # SCOTUS rows are outside the carve-out regardless of pulls.
                _row("scotus/304", "scotus", summary="Petition for certiorari."),
            ],
        )
    return db


def test_dry_run_counts_and_writes_nothing(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    with corpus.connect(db) as conn:
        result = scrub_bulk_cluster_fields(conn, apply=False)
        assert result.applied is False
        assert result.scrubbed == 1
        row = corpus.get_row(conn, "ca1/1883")
        assert row is not None and row.summary is not None


def test_apply_scrubs_only_the_never_pulled_circuit_slice(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    with corpus.connect(db) as conn:
        result = scrub_bulk_cluster_fields(conn, apply=True)
        assert result.applied is True and result.scrubbed == 1
        scrubbed = corpus.get_row(conn, "ca1/1883")
        assert scrubbed is not None
        assert scrubbed.summary is None
        assert scrubbed.precedential_status is None
        assert scrubbed.citation_count is None
        assert scrubbed.judges == [] and scrubbed.citations == []
        pulled = corpus.get_row(conn, "ca1/100051")
        assert pulled is not None and pulled.precedential_status == "Published"
        assert pulled.judges == ["barron"]
        scotus = corpus.get_row(conn, "scotus/304")
        assert scotus is not None and scotus.summary == "Petition for certiorari."


def test_apply_is_idempotent(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    with corpus.connect(db) as conn:
        scrub_bulk_cluster_fields(conn, apply=True)
        again = scrub_bulk_cluster_fields(conn, apply=True)
    assert again.scrubbed == 0


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seeded(tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["scrub-bulk-cluster-fields"])
    assert dry.exit_code == 0, dry.output
    assert "would scrub 1 never-pulled non-SCOTUS row(s)" in dry.output
    applied = runner.invoke(app, ["scrub-bulk-cluster-fields", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "scrubbed 1 never-pulled non-SCOTUS row(s)" in applied.output
