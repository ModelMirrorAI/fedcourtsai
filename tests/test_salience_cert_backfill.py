"""Tests for the sal-v5 cert-column back-fill (`backfill-salience-cert-columns`).

What the pass owes and nothing else pins:

- **The readings are ingest's.** Every fill equals what the live cert branch
  (`map_live_docket(form="cert")`) writes for the same payload.
- **The latch holds.** A column already carrying a value is `already_set` and
  never written, even where the snapshot now reads something else; only NULLs
  fill, and a row carrying all three is not read at all.
- A missing or proceedings-less snapshot is `unparseable` and untouched; a
  parsed docket with no call or no petition entry is `no_reading`.
- A count whose snapshot dates the call differently from the stored call is a
  `pair_mismatch` and stays NULL; a planned row gone before the write raises.
- The dry run writes nothing; the bound refuses whole; a re-run after an apply
  is a no-op; the population is the cert live slice.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row
from fedcourtsai.pipeline.salience_cert_backfill import (
    COLUMNS,
    backfill_salience_cert_columns,
)

_PETITION = ("Jan 09 2026", "Petition for a writ of certiorari filed.")
_MANDAMUS = ("Jan 09 2026", "Petition for a writ of mandamus filed.")
_FIRST_DIST = ("Feb 11 2026", "DISTRIBUTED for Conference of 2/27/2026.")
_CALLED = ("Feb 20 2026", "Response Requested. (Due March 23, 2026)")
_BACK = ("Mar 30 2026", "DISTRIBUTED for Conference of 4/17/2026.")
_AGAIN = ("Apr 20 2026", "DISTRIBUTED for Conference of 5/15/2026.")
_DENY = ("May 18 2026", "Petition DENIED.")


def _payload(*entries: tuple[str, str], number: str) -> dict[str, object]:
    return {
        "CaseNumber": f"{number} ",
        "ProceedingsandOrder": [{"Date": d, "Text": t, "Links": []} for d, t in entries],
    }


# A denied paid petition: a call, then two new conferences. Fills
# 2026-02-20 / 2 / certiorari.
_CALLED_TWICE = _payload(_PETITION, _FIRST_DIST, _CALLED, _BACK, _AGAIN, _DENY, number="25-700")
# A denied IFP mandamus petition with no call: only the writ can be read.
_WRIT_NO_CALL = _payload(_MANDAMUS, _FIRST_DIST, _DENY, number="25-5001")
# A snapshot that discloses no proceedings list at all (a redacted payload
# drops the key): unobservable, not "no call".
_REDACTED = {"CaseNumber": "25-703 "}


def _row(
    case_id: str,
    docket: str,
    *,
    live: bool = True,
    called: date | None = None,
    after: int | None = None,
    writ: str | None = None,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        case_name="Marbury v. Ellison",
        last_live_polled=date(2026, 8, 1) if live else None,
        call_for_response_at=called,
        distributed_after_call=after,
        opening_writ=writ,
    )


def _stored(conn: sqlite3.Connection, case_id: str) -> tuple[object, ...]:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return tuple(getattr(row, column) for column in COLUMNS)


def _seed(conn: sqlite3.Connection) -> None:
    corpus.upsert_rows(
        conn,
        [
            _row("scotus/700", "25-700"),  # all three NULL: all three fill
            _row("scotus/5001", "25-5001"),  # writ fills; no call to read
            # A latched writ that disagrees with the snapshot is kept; the
            # call and its count still fill.
            _row("scotus/702", "25-702 *** CAPITAL CASE ***", writ="other"),
            _row("scotus/703", "25-703"),  # snapshot has no proceedings
            _row("scotus/704", "25-704"),  # no snapshot at all
            _row(  # all three set: not read
                "scotus/705", "25-705", called=date(2026, 1, 2), after=0, writ="certiorari"
            ),
        ],
    )
    corpus.upsert_snapshot(conn, "scotus/700", date(2026, 5, 18), _CALLED_TWICE)
    corpus.upsert_snapshot(conn, "scotus/5001", date(2026, 5, 18), _WRIT_NO_CALL)
    corpus.upsert_snapshot(
        conn, "scotus/702", date(2026, 5, 18), {**_CALLED_TWICE, "CaseNumber": "25-702 "}
    )
    corpus.upsert_snapshot(conn, "scotus/703", date(2026, 5, 18), _REDACTED)
    corpus.upsert_snapshot(conn, "scotus/705", date(2026, 5, 18), _WRIT_NO_CALL)


def test_every_fill_is_what_the_live_cert_branch_writes() -> None:
    for payload, docket_id, expected in (
        (_CALLED_TWICE, 700, (date(2026, 2, 20), 2, "certiorari")),
        (_WRIT_NO_CALL, 5001, (None, None, "rule-20")),
    ):
        row = to_corpus_row(from_live_record(map_live_docket(payload, docket_id, form="cert")))
        assert tuple(getattr(row, column) for column in COLUMNS) == expected


def test_the_pass_fills_nulls_and_keeps_every_latched_value(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = backfill_salience_cert_columns(conn, apply=True, max_fills=6)
        assert (result.eligible, result.all_set, result.read, result.unobservable) == (6, 1, 3, 2)
        ledger = {column: result.columns[column] for column in COLUMNS}
        counts = {
            column: (c.would_fill, c.already_set, c.no_reading, c.unparseable, c.pair_mismatch)
            for column, c in ledger.items()
        }
        assert counts == {
            "call_for_response_at": (2, 1, 1, 2, 0),
            "distributed_after_call": (2, 1, 1, 2, 0),
            "opening_writ": (2, 2, 0, 2, 0),
        }
        assert ledger["opening_writ"].filled_values == {"certiorari": 1, "rule-20": 1}
        assert ledger["distributed_after_call"].filled_values == {"2": 2}
        assert result.total_fills == 6
        assert not result.refused
        assert _stored(conn, "scotus/700") == (date(2026, 2, 20), 2, "certiorari")
        assert _stored(conn, "scotus/5001") == (None, None, "rule-20")
        assert _stored(conn, "scotus/702") == (date(2026, 2, 20), 2, "other")
        assert _stored(conn, "scotus/703") == (None, None, None)
        assert _stored(conn, "scotus/704") == (None, None, None)
        assert _stored(conn, "scotus/705") == (date(2026, 1, 2), 0, "certiorari")
        again = backfill_salience_cert_columns(conn, apply=True, max_fills=1)
        assert again.total_fills == 0


def test_the_dry_run_writes_nothing(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = backfill_salience_cert_columns(conn, apply=False)
        assert result.total_fills == 6
        assert not result.applied
        assert _stored(conn, "scotus/700") == (None, None, None)


def test_the_bound_refuses_the_whole_apply(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = backfill_salience_cert_columns(conn, apply=True, max_fills=5)
        assert result.refused
        assert _stored(conn, "scotus/700") == (None, None, None)
        assert _stored(conn, "scotus/5001") == (None, None, None)


def test_a_value_landed_after_the_read_survives_the_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The statement keeps the fill-in latch itself, not only the plan."""
    real = corpus.latest_live_snapshot

    def poll_in_between(conn: sqlite3.Connection, case_id: str) -> object:
        # A poll that stamps the writ after the pass read the stored row.
        if case_id == "scotus/700":
            with conn:
                conn.execute(
                    "UPDATE cases SET opening_writ = 'ambiguous' WHERE case_id = ?", (case_id,)
                )
        return real(conn, case_id)

    monkeypatch.setattr(corpus, "latest_live_snapshot", poll_in_between)
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = backfill_salience_cert_columns(conn, apply=True, max_fills=6)
        assert {fill.case_id: fill for fill in result.fills}["scotus/700"].opening_writ == (
            "certiorari"
        )
        assert _stored(conn, "scotus/700") == (date(2026, 2, 20), 2, "ambiguous")


def test_applications_and_rows_outside_the_live_slice_are_not_walked(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(
            conn, [_row("scotus/800", "25A800"), _row("scotus/801", "25-801", live=False)]
        )
        for case_id in ("scotus/800", "scotus/801"):
            corpus.upsert_snapshot(conn, case_id, date(2026, 5, 18), _CALLED_TWICE)
        result = backfill_salience_cert_columns(conn, apply=True, max_fills=10)
        assert result.eligible == 0
        assert _stored(conn, "scotus/800") == (None, None, None)
        assert _stored(conn, "scotus/801") == (None, None, None)


@pytest.fixture
def seeded_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _seed(conn)
    return root


def test_the_command_prints_the_per_column_ledger_and_requires_a_bound(seeded_root: Path) -> None:
    runner = CliRunner()
    dry = runner.invoke(app, ["backfill-salience-cert-columns"])
    assert dry.exit_code == 0, dry.output
    assert "opening_writ: 2 would fill, 2 already set (latched, untouched)" in dry.output
    payload = json.loads(dry.output.strip().splitlines()[-1])
    assert payload["total_fills"] == 6
    assert "fills" not in payload
    unbounded = runner.invoke(app, ["backfill-salience-cert-columns", "--apply"])
    assert unbounded.exit_code == 2
    refused = runner.invoke(app, ["backfill-salience-cert-columns", "--apply", "--max-fills", "5"])
    assert refused.exit_code == 1
    applied = runner.invoke(app, ["backfill-salience-cert-columns", "--apply", "--max-fills", "6"])
    assert applied.exit_code == 0, applied.output
    with corpus.connect(corpus.corpus_db_path(seeded_root)) as conn:
        assert _stored(conn, "scotus/700") == (date(2026, 2, 20), 2, "certiorari")


def test_a_count_off_a_differently_dated_call_is_a_pair_mismatch(tmp_path: Path) -> None:
    """A stored call the snapshot dates differently keeps the count NULL."""
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/900", "25-900", called=date(2026, 1, 5)),  # differs
                _row("scotus/901", "25-901", called=date(2026, 2, 20)),  # agrees
            ],
        )
        for case_id in ("scotus/900", "scotus/901"):
            corpus.upsert_snapshot(conn, case_id, date(2026, 5, 18), _CALLED_TWICE)
        result = backfill_salience_cert_columns(conn, apply=True, max_fills=10)
        after = result.columns["distributed_after_call"]
        assert (after.would_fill, after.pair_mismatch, after.already_set) == (1, 1, 0)
        assert result.columns["call_for_response_at"].already_set == 2
        assert _stored(conn, "scotus/900") == (date(2026, 1, 5), None, "certiorari")
        assert _stored(conn, "scotus/901") == (date(2026, 2, 20), 2, "certiorari")


def test_a_planned_row_gone_before_the_write_stops_the_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Rows written must equal rows planned; a shortfall raises and rolls back."""
    real = corpus.latest_live_snapshot

    def row_removed(conn: sqlite3.Connection, case_id: str) -> object:
        found = real(conn, case_id)
        if case_id == "scotus/700":
            with conn:
                conn.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
        return found

    monkeypatch.setattr(corpus, "latest_live_snapshot", row_removed)
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        with pytest.raises(RuntimeError, match="the plan and the corpus disagree"):
            backfill_salience_cert_columns(conn, apply=True, max_fills=6)
        assert _stored(conn, "scotus/5001") == (None, None, None)
