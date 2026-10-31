"""Tests for the application re-read pass (`reread-applications`).

What the pass owes and nothing else pins:

- **The reading is ingest's.** Every re-read equals what the live application
  branch (`map_live_docket(form="application")`) stores for the same payload,
  so a filled row and a polled row cannot disagree.
- **The population is the resolved application slice**: live-slice SCOTUS
  rows with an `application_kind` and a registered disposition. A pending
  application, a cert-form row and a row outside the live slice are not walked.
- **The registered `disposition` never moves.**
- A NULL fills and a differing value moves (listed); an unreadable snapshot is
  `unobservable` and never written; the dry run writes nothing; the bound
  refuses whole; a re-run after an apply is a no-op.
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
from fedcourtsai.pipeline.application_reread import reread_applications
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row

_ASK = ("Jan 09 2026", "Application ({number}) for a stay, submitted to Justice Alito.")


def _payload(number: str, *entries: tuple[str, str]) -> dict[str, object]:
    texts = [_ASK, *entries]
    return {
        "CaseNumber": f"{number} ",
        "ProceedingsandOrder": [
            {"Date": d, "Text": t.format(number=number), "Links": []} for d, t in texts
        ],
    }


_PARTIAL = _payload(
    "25A10", ("Feb 01 2026", "Application ({number}) granted in part and denied in part.")
)
_MOOT = _payload(
    "25A11",
    ("Feb 02 2026", "Application ({number}) dismissed in light of the relief granted in No. 25A9."),
)
_DENIED = _payload("25A12", ("Feb 03 2026", "Application ({number}) denied by Justice Alito."))
_PENDING = _payload("25A13")


def _row(
    case_id: str,
    docket: str,
    *,
    disposition: str | None,
    stored: str | None = None,
    kind: str | None = "substantive",
    live: bool = True,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        case_name="In re Application",
        disposition=disposition,
        last_live_polled=date(2026, 8, 1) if live else None,
        application_kind=kind,
        interim_reading=stored,
    )


def _stored(conn: sqlite3.Connection, case_id: str) -> tuple[str | None, str | None]:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.interim_reading, row.disposition


def _seed(conn: sqlite3.Connection) -> None:
    corpus.upsert_rows(
        conn,
        [
            _row("scotus/10", "25A10", disposition="denied"),  # NULL: filled
            _row("scotus/11", "25A11", disposition="granted", stored="granted"),  # moves
            _row("scotus/12", "25A12", disposition="denied", stored="denied"),  # unchanged
            _row("scotus/13", "25A13", disposition=None),  # pending: not walked
        ],
    )
    for case_id, payload in (
        ("scotus/10", _PARTIAL),
        ("scotus/11", _MOOT),
        ("scotus/12", _DENIED),
        ("scotus/13", _PENDING),
    ):
        corpus.upsert_snapshot(conn, case_id, date(2026, 2, 5), payload)


def test_every_re_read_is_what_the_live_application_branch_stores() -> None:
    for payload, docket_id, expected, registered in (
        (_PARTIAL, 10, "granted-in-part", "denied"),
        (_MOOT, 11, "dismissed-moot", "granted"),
        (_DENIED, 12, "denied", "denied"),
        (_PENDING, 13, None, None),
    ):
        row = to_corpus_row(
            from_live_record(map_live_docket(payload, docket_id, form="application"))
        )
        assert row.interim_reading == expected
        assert row.disposition == registered


def test_the_pass_fills_and_moves_and_never_touches_the_registered_label(
    tmp_path: Path,
) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = reread_applications(conn, apply=True, max_changes=2)
        assert (result.eligible, result.read, result.unobservable) == (3, 3, 0)
        assert (result.filled, result.moved, result.unchanged, result.no_reading) == (1, 1, 1, 0)
        assert result.filled_readings == {"granted-in-part": 1}
        assert [(m.case_id, m.was, m.now) for m in result.moves] == [
            ("scotus/11", "granted", "dismissed-moot")
        ]
        assert result.finer_vs_registered == {
            "denied -> denied": 1,
            "denied -> granted-in-part": 1,
            "granted -> dismissed-moot": 1,
        }
        assert result.total_changes == 2
        assert _stored(conn, "scotus/10") == ("granted-in-part", "denied")
        assert _stored(conn, "scotus/11") == ("dismissed-moot", "granted")
        assert _stored(conn, "scotus/12") == ("denied", "denied")
        assert _stored(conn, "scotus/13") == (None, None)


def test_cert_rows_and_rows_outside_the_live_slice_are_not_walked(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/20", "25-20", disposition="denied", kind=None),
                _row("scotus/21", "25A21", disposition="denied", live=False),
            ],
        )
        result = reread_applications(conn, apply=True, max_changes=5)
        assert result.eligible == 0


@pytest.mark.parametrize(
    "snapshot",
    [None, {"CaseNumber": "25A30 ", "ProceedingsandOrder": None}],
)
def test_an_unreadable_snapshot_is_unobservable_and_untouched(
    tmp_path: Path, snapshot: dict[str, object] | None
) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/30", "25A30", disposition="denied")])
        if snapshot is not None:
            corpus.upsert_snapshot(conn, "scotus/30", date(2026, 6, 1), snapshot)
        result = reread_applications(conn, apply=True, max_changes=5)
        assert (result.eligible, result.read, result.unobservable) == (1, 0, 1)
        assert _stored(conn, "scotus/30") == (None, "denied")


def test_a_snapshot_with_no_reading_is_listed_and_untouched(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/31", "25A31", disposition="denied")])
        corpus.upsert_snapshot(conn, "scotus/31", date(2026, 6, 1), _payload("25A31"))
        result = reread_applications(conn, apply=True, max_changes=5)
        assert result.no_reading == 1
        assert result.no_reading_rows == ["scotus/31"]
        assert result.total_changes == 0


def test_a_dry_run_reports_the_plan_and_writes_nothing(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = reread_applications(conn, apply=False)
        assert result.total_changes == 2
        assert not result.applied
        assert _stored(conn, "scotus/10") == (None, "denied")


def test_the_bound_refuses_the_whole_apply(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = reread_applications(conn, apply=True, max_changes=1)
        assert result.refused
        assert _stored(conn, "scotus/10") == (None, "denied")
        assert _stored(conn, "scotus/11") == ("granted", "granted")


def test_a_write_the_corpus_does_not_admit_stops_the_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        monkeypatch.setattr(corpus, "set_interim_readings", lambda _conn, _updates: 1)
        with pytest.raises(RuntimeError, match="plan and the corpus disagree"):
            reread_applications(conn, apply=True, max_changes=2)


def test_a_re_run_after_the_apply_changes_nothing(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        reread_applications(conn, apply=True, max_changes=2)
        again = reread_applications(conn, apply=False)
        assert again.total_changes == 0
        assert again.unchanged == 3


def test_the_upsert_fills_in_and_a_fresh_reading_replaces(tmp_path: Path) -> None:
    """A writer with no reading keeps the stored one; a fresh reading wins."""
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(
            conn, [_row("scotus/40", "25A40", disposition="denied", stored="denied")]
        )
        corpus.upsert_rows(conn, [_row("scotus/40", "25A40", disposition="denied", stored=None)])
        assert _stored(conn, "scotus/40") == ("denied", "denied")
        corpus.upsert_rows(
            conn, [_row("scotus/40", "25A40", disposition="denied", stored="granted-in-part")]
        )
        assert _stored(conn, "scotus/40") == ("granted-in-part", "denied")


def test_the_command_prints_the_ledger_and_refuses_an_unbounded_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        _seed(conn)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    unbounded = CliRunner().invoke(app, ["reread-applications", "--apply"])
    assert unbounded.exit_code == 2
    assert "requires an explicit --max-changes" in unbounded.stderr

    dry = CliRunner().invoke(app, ["reread-applications"])
    assert dry.exit_code == 0, dry.output
    assert "3 read, 0 unobservable" in dry.stdout
    assert "would write 2: 1 NULL -> value, 1 value -> other value" in dry.stdout
    assert "move scotus/11 (25A11): granted -> dismissed-moot" in dry.stdout
    ledger = json.loads(dry.stdout.strip().splitlines()[-1])
    assert ledger["total_changes"] == 2

    refused = CliRunner().invoke(app, ["reread-applications", "--apply", "--max-changes", "1"])
    assert refused.exit_code == 1
    assert "refusing to apply 2 change(s)" in refused.stderr
