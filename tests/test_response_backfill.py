"""The dated-signal back-fill: re-parsing the stored snapshot the forward channels never revisit."""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.response_backfill import backfill_response_fields

runner = CliRunner()

_CASE = "scotus/900100"
_GRANTED_AT = date(2024, 1, 12)

_REQUEST_ENTRY = {
    "Date": "Mar 04 2024",
    "Text": "Response to application (23A800) requested by Justice Alito, due March 11, 2024",
}
_FILED_ENTRY = {
    "Date": "Mar 11 2024",
    "Text": "Response to application from Roe, et al. filed.",
}
_MERITS_BRIEF_ENTRY = {
    "Date": "Apr 22 2024",
    "Text": "Brief of respondents Richard Roe, et al. on the merits filed.",
}
# Same anchor, excluded: the cert-stage brief in opposition is not a merits brief.
_OPPOSITION_ENTRY = {
    "Date": "Nov 02 2023",
    "Text": "Brief of respondents in opposition filed.",
}


def _payload(*entries: dict[str, Any]) -> dict[str, Any]:
    return {"CaseNumber": "23-100 ", "ProceedingsandOrder": list(entries)}


class _LiveSnapshotSource:
    """A payload read source serving live-shaped snapshots, recording what it read.

    The shared `DictSnapshotSource` stubs `latest_live_snapshot` to ``None``, which
    is the one method this pass reads through.
    """

    def __init__(self, snapshots: Mapping[str, tuple[date, dict[str, Any]] | None]) -> None:
        self._snapshots = snapshots
        self.read_cases: list[str] = []
        self._lock = threading.Lock()

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        return None

    def snapshot_at(self, case_id: str, *, before: date) -> tuple[date, dict[str, Any]] | None:
        return None

    def latest_live_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        with self._lock:
            self.read_cases.append(case_id)
        return self._snapshots.get(case_id)

    def documents_for_case(self, case_id: str) -> list[corpus.CaseDocument]:
        return []

    def opinion_text(self, case_id: str) -> str | None:
        return None


def _row(**fields: Any) -> corpus.CorpusRow:
    base: dict[str, Any] = {
        "case_id": _CASE,
        "court": "scotus",
        "docket_number": "23-100",
        "last_live_polled": date(2024, 5, 1),
    }
    return corpus.CorpusRow.model_validate({**base, **fields})


@contextmanager
def _seeded(
    tmp_path: Path,
    rows: list[corpus.CorpusRow],
    snapshots: dict[str, tuple[date, dict[str, Any]]] | None = None,
) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        for case_id, (day, payload) in (snapshots or {}).items():
            corpus.upsert_snapshot(conn, case_id, day, payload)
        conn.commit()
        yield conn


def _stored(tmp_path: Path, case_id: str = _CASE) -> corpus.CorpusRow:
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        row = corpus.get_row(conn, case_id)
    assert row is not None
    return row


def _full_snapshot() -> dict[str, tuple[date, dict[str, Any]]]:
    return {
        _CASE: (
            date(2024, 5, 1),
            _payload(_REQUEST_ENTRY, _FILED_ENTRY, _OPPOSITION_ENTRY, _MERITS_BRIEF_ENTRY),
        )
    }


def test_dry_run_reports_the_fill_and_writes_nothing(tmp_path: Path) -> None:
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=False)
    assert result.applied is False
    assert result.candidates == 1
    assert len(result.filled) == 1
    fill = result.filled[0]
    assert fill.response_requested_at == date(2024, 3, 4)
    assert fill.response_filed_at == date(2024, 3, 11)
    assert fill.merits_brief_filed == date(2024, 4, 22)
    stored = _stored(tmp_path)
    assert stored.response_requested_at is None
    assert stored.merits_brief_filed is None


def test_apply_fills_all_three_dated_columns(tmp_path: Path) -> None:
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.applied is True and result.refused is False
    stored = _stored(tmp_path)
    assert stored.response_requested_at == date(2024, 3, 4)
    assert stored.response_filed_at == date(2024, 3, 11)
    # The cert-stage brief in opposition shares the anchor and is excluded; the
    # grant date bounds the scan that separates them.
    assert stored.merits_brief_filed == date(2024, 4, 22)


def test_a_row_with_no_stored_snapshot_is_counted_not_failed(tmp_path: Path) -> None:
    """The split-mode residue: nothing to parse is reported, never an error."""
    rows = [_row(response_requested=True)]
    with _seeded(tmp_path, rows) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.candidates == 1
    assert result.no_snapshot == 1
    assert result.filled == []
    assert _stored(tmp_path).response_requested_at is None


def test_a_payload_without_the_proceedings_key_is_no_snapshot(tmp_path: Path) -> None:
    """`latest_live_snapshot` keys on the proceedings key, so this is never offered."""
    rows = [_row(response_requested=True)]
    snapshots = {_CASE: (date(2024, 5, 1), {"CaseNumber": "23-100 "})}
    with _seeded(tmp_path, rows, snapshots) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.no_snapshot == 1
    assert result.no_proceedings == 0
    assert result.filled == []


def test_an_empty_proceedings_list_is_unobservable_not_an_absent_signal(tmp_path: Path) -> None:
    """A served shell discloses no signals; it does not assert that none exist."""
    rows = [_row(response_requested=True)]
    with _seeded(tmp_path, rows, {_CASE: (date(2024, 5, 1), _payload())}) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.no_proceedings == 1
    assert result.no_snapshot == 0
    assert result.filled == []
    assert _stored(tmp_path).response_requested_at is None


def test_a_row_read_with_nothing_to_fill_is_not_a_fill(tmp_path: Path) -> None:
    """The steady state: selected, read, and yielding no date — still a candidate."""
    rows = [_row(response_requested=True)]
    entry = {"Date": "Jun 01 2023", "Text": "Petition for a writ of certiorari filed."}
    with _seeded(tmp_path, rows, {_CASE: (date(2024, 5, 1), _payload(entry))}) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.unchanged == 1
    assert result.filled == []


def test_a_stored_date_is_never_overwritten(tmp_path: Path) -> None:
    """Fill-in only, matching the latch family these columns sit in on the upsert."""
    rows = [
        _row(
            response_requested=True,
            response_requested_at=date(2020, 1, 1),
            date_cert_granted=_GRANTED_AT,
            disposition="granted",
        )
    ]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    # Selected by the granted arm, so it is still read — but the stored request
    # date stands.
    assert result.candidates == 1
    assert _stored(tmp_path).response_requested_at == date(2020, 1, 1)
    assert _stored(tmp_path).merits_brief_filed == date(2024, 4, 22)


def test_a_row_without_a_grant_reads_no_merits_brief(tmp_path: Path) -> None:
    """No grant date means no merits proceeding to be briefed."""
    rows = [_row(response_requested=True)]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.filled[0].merits_brief_filed is None
    assert _stored(tmp_path).merits_brief_filed is None


@pytest.mark.parametrize("disposition", ["gvr", "summary-reversal"])
def test_a_grant_that_opens_no_merits_proceeding_is_out_of_population(
    tmp_path: Path, disposition: str
) -> None:
    """The grant date alone does not select the merits arm.

    A GVR and a summary reversal keep ``date_cert_granted`` while opening no
    merits proceeding, so a brief date on one would be a value no channel writes —
    and the column is fill-in only, so it would never self-correct. The arm carries
    the disposition leg the column's own writer gates on.
    """
    rows = [_row(date_cert_granted=_GRANTED_AT, disposition=disposition)]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.candidates == 0
    assert result.filled == []
    assert _stored(tmp_path).merits_brief_filed is None


def test_a_granted_row_is_in_population(tmp_path: Path) -> None:
    """The other side of the same gate, so the leg is shown to select, not just refuse."""
    rows = [_row(date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.candidates == 1
    assert _stored(tmp_path).merits_brief_filed == date(2024, 4, 22)


def test_a_gvr_selected_by_the_response_arm_gains_no_brief_date(tmp_path: Path) -> None:
    """The disposition gate is on the fill, not only on the selection.

    A GVR carrying the response flag is selected by the *first* arm, so gating only
    the merits arm would still let its grant date drive `respondent_brief_date` on
    the way past — the same bad write by another route.
    """
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="gvr")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=10)
    assert result.candidates == 1  # selected by the response arm
    assert result.filled[0].response_requested_at == date(2024, 3, 4)
    assert result.filled[0].merits_brief_filed is None
    assert _stored(tmp_path).merits_brief_filed is None


def test_the_offloaded_schedule_reads_the_content_store_and_agrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pooling the read is sound, and produces the serial pass's answer exactly.

    Under the corpus-split mode `latest_live_snapshot` is served by the registered
    source and never touches the connection, which is what lets `prefetch_by_case`
    hand the read to worker threads. Pinned rather than read off the source,
    because the pass is only as safe as that gate actually being the one the pool
    keys on.
    """
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        serial = backfill_response_fields(conn, apply=False)
        stored = {_CASE: corpus.latest_live_snapshot(conn, _CASE)}
    assert len(serial.filled) == 1

    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    source = _LiveSnapshotSource(stored)
    # Save/restore the registered source around the swap; the read of the private
    # registry is the only way to put back the casestore singleton it registers at
    # import (there is no public getter).
    previous = corpus._READ_SOURCE.get("source")
    corpus.set_payload_read_source(source)
    try:
        assert corpus.payload_reads_offloaded()
        with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
            offloaded = backfill_response_fields(conn, apply=False)
    finally:
        corpus.set_payload_read_source(previous)

    assert source.read_cases == [_CASE]
    assert [
        (f.case_id, f.response_requested_at, f.merits_brief_filed) for f in offloaded.filled
    ] == [(f.case_id, f.response_requested_at, f.merits_brief_filed) for f in serial.filled]


def test_apply_is_idempotent(tmp_path: Path) -> None:
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        backfill_response_fields(conn, apply=True, max_fills=10)
        again = backfill_response_fields(conn, apply=True, max_fills=10)
    # The response arm is satisfied; the granted arm no longer matches either,
    # since the merits brief is now stored.
    assert again.filled == []
    assert again.candidates == 0


def test_the_bound_refuses_and_writes_nothing(tmp_path: Path) -> None:
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()) as conn:
        result = backfill_response_fields(conn, apply=True, max_fills=0)
    assert result.refused is True and result.applied is False
    assert _stored(tmp_path).response_requested_at is None


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [_row(response_requested=True, date_cert_granted=_GRANTED_AT, disposition="granted")]
    with _seeded(tmp_path, rows, _full_snapshot()):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["backfill-response-fields"])
    assert dry.exit_code == 0, dry.output
    assert "would fill 1 of 1 candidate(s)" in dry.output
    assert _stored(tmp_path).response_requested_at is None

    applied = runner.invoke(app, ["backfill-response-fields", "--apply", "--max-fills", "5"])
    assert applied.exit_code == 0, applied.output
    assert "filled 1 of 1 candidate(s)" in applied.output
    assert _stored(tmp_path).response_requested_at == date(2024, 3, 4)

    again = runner.invoke(app, ["backfill-response-fields"])
    assert again.exit_code == 0, again.output
    assert "would fill 0 of 0 candidate(s)" in again.output  # idempotent


def test_cli_apply_requires_an_explicit_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The maintainer states the number they read in the dry run; no default applies."""
    with _seeded(tmp_path, [_row(response_requested=True)], _full_snapshot()):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["backfill-response-fields", "--apply"])
    assert result.exit_code == 2
    assert "--apply requires an explicit --max-fills" in result.output
    assert _stored(tmp_path).response_requested_at is None


def test_cli_apply_refuses_above_the_bound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _seeded(tmp_path, [_row(response_requested=True)], _full_snapshot()):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["backfill-response-fields", "--apply", "--max-fills", "0"])
    assert result.exit_code == 1
    assert "refusing to apply 1 fills (--max-fills 0)" in result.output
    assert _stored(tmp_path).response_requested_at is None


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["backfill-response-fields"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.output
