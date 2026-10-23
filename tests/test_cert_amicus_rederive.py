"""Tests for the cert amicus back-fill (`rederive-cert-amicus-briefs`).

What the pass owes and nothing else pins:

- **The count is ingest's.** Every recount equals what the live cert branch
  (`map_live_docket(form="cert")`) writes for the same payload, so a filled row
  and a polled row cannot disagree.
- **The population is the cert branch's**: cert-form live-slice SCOTUS rows,
  paid and IFP, annotated numbers included; applications and rows outside the
  live slice are not walked.
- **The write keeps the max latch.** A NULL fills and a lower count rises; a
  recount below the stored value is reported and never written, through the
  pass and through its setter alike.
- An unreadable snapshot is `unobservable` and never written; the dry run
  writes nothing; the bound refuses whole; a re-run after an apply is a no-op.
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
from fedcourtsai.pipeline.cert_amicus_rederive import rederive_cert_amicus_briefs
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row

_PETITION = ("Jan 09 2026", "Petition for a writ of certiorari filed.")
_AMICUS = ("Feb 10 2026", "Brief amicus curiae of Cato Institute filed.")
_AMICI = ("Feb 11 2026", "Brief amici curiae of Professors of Law, et al. filed.")
_MOTION = (
    "Feb 12 2026",
    "Motion of Pilots Union for leave to file a brief as amicus curiae filed.",
)
_MOTION_ORDER = (
    "Mar 02 2026",
    "Motion of Pilots Union for leave to file a brief as amicus curiae GRANTED.",
)
_GRANT = ("Jun 01 2026", "Petition GRANTED.")
_DENY = ("Jun 01 2026", "Petition DENIED.")
_MERITS_AMICUS = ("Jul 15 2026", "Brief amicus curiae of Chamber of Commerce filed.")


def _payload(*entries: tuple[str, str], number: str) -> dict[str, object]:
    return {
        "CaseNumber": f"{number} ",
        "ProceedingsandOrder": [{"Date": d, "Text": t, "Links": []} for d, t in entries],
    }


def _row(
    case_id: str,
    docket: str,
    *,
    stored: int | None = None,
    live: bool = True,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        case_name="Marbury v. Ellison",
        last_live_polled=date(2026, 8, 1) if live else None,
        cert_amicus_briefs=stored,
    )


def _stored(conn: sqlite3.Connection, case_id: str) -> int | None:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.cert_amicus_briefs


# A granted paid petition: two cert-stage amici and a motion whose order is
# dropped, then a merits amicus after the grant that the cut leaves out. Counts 3.
_GRANTED = _payload(
    _PETITION, _AMICUS, _AMICI, _MOTION, _MOTION_ORDER, _GRANT, _MERITS_AMICUS, number="25-700"
)
# A denied IFP petition with one amicus. Counts 1.
_DENIED_IFP = _payload(_PETITION, _AMICUS, _DENY, number="25-5001")
# An open petition with one amicus so far. Counts 1.
_OPEN = _payload(_PETITION, _AMICUS, number="25-702")


def _seed(conn: sqlite3.Connection) -> None:
    corpus.upsert_rows(
        conn,
        [
            _row("scotus/700", "25-700"),  # NULL: filled with 3
            _row("scotus/5001", "25-5001", stored=0),  # stored low: raised to 1
            _row("scotus/702", "25-702 *** CAPITAL CASE ***", stored=1),  # unchanged, open
        ],
    )
    corpus.upsert_snapshot(conn, "scotus/700", date(2026, 7, 15), _GRANTED)
    corpus.upsert_snapshot(conn, "scotus/5001", date(2026, 6, 1), _DENIED_IFP)
    corpus.upsert_snapshot(conn, "scotus/702", date(2026, 2, 10), _OPEN)


def test_every_recount_is_what_the_live_cert_branch_writes() -> None:
    """The pass's count and ingest's count are one function over one payload."""
    for payload, docket_id, expected in (
        (_GRANTED, 700, 3),
        (_DENIED_IFP, 5001, 1),
        (_OPEN, 702, 1),
    ):
        row = to_corpus_row(from_live_record(map_live_docket(payload, docket_id, form="cert")))
        assert row.cert_amicus_briefs == expected


def test_the_pass_fills_and_raises_the_cert_slice(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = rederive_cert_amicus_briefs(conn, apply=True, max_changes=2)
        assert (result.eligible, result.read, result.unobservable) == (3, 3, 0)
        assert (result.filled, result.raised, result.unchanged, result.latch_held) == (1, 1, 1, 0)
        assert result.filled_distribution == {3: 1}
        assert [(m.case_id, m.was, m.now) for m in result.raised_moves] == [("scotus/5001", 0, 1)]
        assert result.open_petitions == 1
        assert result.total_changes == 2
        assert not result.refused
        assert _stored(conn, "scotus/700") == 3
        assert _stored(conn, "scotus/5001") == 1
        assert _stored(conn, "scotus/702") == 1


def test_applications_and_rows_outside_the_live_slice_are_not_walked(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/800", "25A800"),
                _row("scotus/801", "25-801", live=False),
            ],
        )
        corpus.upsert_snapshot(
            conn, "scotus/800", date(2026, 2, 1), _payload(_AMICUS, number="25A800")
        )
        corpus.upsert_snapshot(
            conn, "scotus/801", date(2026, 2, 1), _payload(_AMICUS, number="25-801")
        )
        result = rederive_cert_amicus_briefs(conn, apply=True, max_changes=5)
        assert result.eligible == 0
        assert _stored(conn, "scotus/800") is None
        assert _stored(conn, "scotus/801") is None


def test_a_lower_recount_is_held_by_the_latch_and_never_written(tmp_path: Path) -> None:
    """A snapshot that lost entries recounts low; the stored count stands."""
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/900", "25-900", stored=4)])
        corpus.upsert_snapshot(
            conn, "scotus/900", date(2026, 6, 1), _payload(_PETITION, _AMICUS, number="25-900")
        )
        result = rederive_cert_amicus_briefs(conn, apply=True, max_changes=5)
        assert result.latch_held == 1
        assert result.total_changes == 0
        assert [(m.case_id, m.was, m.now) for m in result.latch_held_moves] == [
            ("scotus/900", 4, 1)
        ]
        assert _stored(conn, "scotus/900") == 4


def test_the_setter_applies_the_upsert_latch(tmp_path: Path) -> None:
    """The guarded UPDATE and the upsert path agree on what lands."""
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/1", "25-1"), _row("scotus/2", "25-2", stored=2)])
        assert corpus.raise_cert_amicus_briefs(conn, [("scotus/1", 0), ("scotus/2", 1)]) == 1
        assert _stored(conn, "scotus/1") == 0
        assert _stored(conn, "scotus/2") == 2
        corpus.upsert_rows(conn, [_row("scotus/2", "25-2", stored=1)])
        assert _stored(conn, "scotus/2") == 2
        assert corpus.raise_cert_amicus_briefs(conn, [("scotus/2", 3)]) == 1
        assert _stored(conn, "scotus/2") == 3


@pytest.mark.parametrize(
    "snapshot",
    [
        None,
        # A REST-shaped snapshot is not live-shaped, so no live snapshot is found.
        {"docket_entries": [{"description": "Brief amicus curiae filed."}]},
        # Live-shaped key, but no proceedings list disclosed.
        {"CaseNumber": "25-910 ", "ProceedingsandOrder": None},
    ],
)
def test_an_unreadable_snapshot_is_unobservable_and_untouched(
    tmp_path: Path, snapshot: dict[str, object] | None
) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(conn, [_row("scotus/910", "25-910")])
        if snapshot is not None:
            corpus.upsert_snapshot(conn, "scotus/910", date(2026, 6, 1), snapshot)
        result = rederive_cert_amicus_briefs(conn, apply=True, max_changes=5)
        assert (result.eligible, result.read, result.unobservable) == (1, 0, 1)
        assert result.total_changes == 0
        assert _stored(conn, "scotus/910") is None


def test_a_dry_run_reports_the_plan_and_writes_nothing(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = rederive_cert_amicus_briefs(conn, apply=False)
        assert result.total_changes == 2
        assert not result.applied
        assert _stored(conn, "scotus/700") is None
        assert _stored(conn, "scotus/5001") == 0


def test_the_bound_refuses_the_whole_apply(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        result = rederive_cert_amicus_briefs(conn, apply=True, max_changes=1)
        assert result.refused
        assert _stored(conn, "scotus/700") is None
        assert _stored(conn, "scotus/5001") == 0


def test_a_write_the_corpus_does_not_admit_stops_the_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        monkeypatch.setattr(corpus, "raise_cert_amicus_briefs", lambda _conn, _updates: 1)
        with pytest.raises(RuntimeError, match="plan and the corpus disagree"):
            rederive_cert_amicus_briefs(conn, apply=True, max_changes=2)


def test_a_re_run_after_the_apply_changes_nothing(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        _seed(conn)
        rederive_cert_amicus_briefs(conn, apply=True, max_changes=2)
        again = rederive_cert_amicus_briefs(conn, apply=False)
        assert again.total_changes == 0
        assert again.unchanged == 3


def test_the_command_prints_the_ledger_and_refuses_an_unbounded_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        _seed(conn)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    unbounded = CliRunner().invoke(app, ["rederive-cert-amicus-briefs", "--apply"])
    assert unbounded.exit_code == 2
    assert "requires an explicit --max-changes" in unbounded.stderr

    dry = CliRunner().invoke(app, ["rederive-cert-amicus-briefs"])
    assert dry.exit_code == 0, dry.output
    assert "3 read, 0 unobservable" in dry.stdout
    assert "would write 2: 1 NULL -> value, 1 value -> higher value" in dry.stdout
    assert "raise scotus/5001: 0 -> 1" in dry.stdout
    ledger = json.loads(dry.stdout.strip().splitlines()[-1])
    assert ledger["total_changes"] == 2

    refused = CliRunner().invoke(
        app, ["rederive-cert-amicus-briefs", "--apply", "--max-changes", "1"]
    )
    assert refused.exit_code == 1
    assert "refusing to apply 2 change(s)" in refused.stderr
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        assert _stored(conn, "scotus/700") is None
