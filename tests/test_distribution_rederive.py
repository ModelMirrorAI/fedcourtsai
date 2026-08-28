"""Tests for the distribution-count re-derivation sweep.

The property under test that no other suite covers: the write is a **direct
UPDATE**, deliberately outside the upsert path's max latch, because a narrower
registered parse moves every changed row down and the latch is built to reject
exactly that. The first test proves both halves — that the sweep's write lands
and that the same value routed through ``upsert_rows`` does not — because a
silent no-op reading as convergence is the hazard the design exists to avoid,
and only a test that exercises the rejected path can show the sweep avoided it.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.distribution_rederive import rederive_distribution_counts
from fedcourtsai.pipeline.salience import SALIENCE_VERSION, SCORERS

# One petition's own distribution and one belonging to an ancillary motion:
# two conferences under `dist-v1`, one under `dist-v2`, which is the whole
# difference between the two registered readings.
_OWN = "DISTRIBUTED for Conference of 3/24/2023."
_MOTION = "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026."


def _row(case_id: str, docket: str, *, distribution_count: int | None = 2) -> corpus.CorpusRow:
    """A live-slice, paid, modern-cert petition carrying a stored count."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        case_name="John Doe v. Roe",
        last_live_polled=date(2026, 8, 1),
        distribution_count=distribution_count,
    )


def _live(*texts: str) -> dict[str, object]:
    """A **live-shaped** snapshot — the only channel this sweep recounts."""
    return {"ProceedingsandOrder": [{"Text": text, "Date": "08/01/2026"} for text in texts]}


def _stored(conn: sqlite3.Connection, case_id: str) -> int | None:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.distribution_count


def _seed(conn: sqlite3.Connection) -> None:
    """One petition whose count falls under ``dist-v2``, one that does not move."""
    corpus.upsert_rows(
        conn, [_row("scotus/1", "24-100"), _row("scotus/2", "24-101", distribution_count=1)]
    )
    corpus.upsert_snapshot(conn, "scotus/1", date(2026, 8, 1), _live(_OWN, _MOTION))
    corpus.upsert_snapshot(conn, "scotus/2", date(2026, 8, 1), _live(_OWN))


def test_the_direct_update_lands_a_narrower_count_the_upsert_latch_would_eat(
    tmp_path: Path,
) -> None:
    """The sweep's whole reason for existing, shown against the path it avoids.

    ``distribution_count`` is max-latched on upsert so a degraded payload's
    confident low count cannot wipe a stored one. A re-derivation under a
    narrower parse *is* a lower count, so the same write routed through
    ``upsert_rows`` is a silent no-op that reads as convergence — the control
    arm here — while the sweep's direct UPDATE lands it.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        _seed(conn)
        assert _stored(conn, "scotus/1") == 2
        # The control: the narrower count offered to the ordinary write path.
        # The latch takes the larger of stored and incoming, so nothing moves —
        # and nothing reports that nothing moved, which is the hazard.
        corpus.upsert_rows(conn, [_row("scotus/1", "24-100", distribution_count=1)])
        assert _stored(conn, "scotus/1") == 2, "the latch was expected to eat the narrower count"
        # The sweep, writing the same value through the direct UPDATE.
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert _stored(conn, "scotus/1") == 1
        # The unmoved petition is untouched rather than rewritten to itself.
        assert _stored(conn, "scotus/2") == 1
    assert (result.applied, result.refused) == (True, False)
    assert (result.changed, result.unchanged) == (1, 1)
    assert (result.decreased, result.increased) == (1, 0)
    assert result.changed_case_ids == ["scotus/1"]


def test_a_dry_run_reports_the_plan_and_writes_nothing(tmp_path: Path) -> None:
    """The dry run is the maintainer's reading, so it must not be the write."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        _seed(conn)
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=False)
        assert _stored(conn, "scotus/1") == 2
    assert result.applied is False
    # The plan the dry run describes is exactly what an apply would write: one
    # pass, so the report a maintainer reads and the write set cannot differ.
    assert (result.changed, result.changed_case_ids) == (1, ["scotus/1"])


def test_the_blast_radius_bound_refuses_the_apply_and_writes_nothing(tmp_path: Path) -> None:
    """Above the bound the sweep refuses whole — never a partial write.

    A count past the bound means the predicate widened or the parse is not the
    reading the census measured, and half a re-derivation would leave the column
    mixed-parse, which is the one state it must never be in.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        _seed(conn)
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=True, max_changes=0)
        assert _stored(conn, "scotus/1") == 2
    assert (result.applied, result.refused) == (True, True)
    assert result.changed == 1, "the refusal still reports what it declined to write"


def test_an_unregistered_parse_raises_before_the_walk(tmp_path: Path) -> None:
    """A parse this process cannot perform is an error, never a fallback.

    Resolved up front, so the refusal does not depend on the frame happening to
    hold a readable snapshot: an empty corpus refuses it just as loudly.
    """
    db = tmp_path / "corpus.db"
    with (
        corpus.connect(db) as conn,
        pytest.raises(KeyError, match="unregistered distribution parse"),
    ):
        rederive_distribution_counts(conn, parse="dist-v99", apply=False)


def test_the_command_refuses_an_unregistered_parse_and_names_the_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The command's own refusal, before it opens the corpus."""
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        _seed(conn)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = CliRunner().invoke(app, ["rederive-distribution-counts", "--parse", "dist-v99"])
    assert result.exit_code == 2, result.output
    assert "unregistered distribution parse 'dist-v99'" in result.stderr
    assert "dist-v2" in result.stderr


def test_a_row_with_no_readable_live_snapshot_is_counted_and_left_untouched(
    tmp_path: Path,
) -> None:
    """Absence is not agreement, and it is certainly not a count of zero.

    This is the guard that replaces the max latch the sweep bypasses: the
    degradation the latch defends against is a payload disclosing no
    proceedings, which reads as "parsed, never distributed". Two shapes of it —
    no snapshot at all, and a REST-shaped one the entry-initial reading may not
    be read against — both land in ``unobservable`` with the column intact.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/1", "24-100"),  # no snapshot stored at all
                _row("scotus/2", "24-101"),  # REST-shaped: not the live channel
                _row("scotus/3", "24-102"),  # live-shaped, and recounted
            ],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/2",
            date(2026, 8, 1),
            {"docket_entries": [{"description": _OWN}, {"description": _MOTION}]},
        )
        corpus.upsert_snapshot(conn, "scotus/3", date(2026, 8, 1), _live(_OWN, _MOTION))
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert (_stored(conn, "scotus/1"), _stored(conn, "scotus/2")) == (2, 2)
        assert _stored(conn, "scotus/3") == 1
    assert (result.eligible, result.observable, result.unobservable) == (3, 1, 2)
    assert result.changed_case_ids == ["scotus/3"]


def test_a_row_with_no_stored_count_is_reported_and_never_filled(tmp_path: Path) -> None:
    """The null count is a coverage sentinel for a whole family, not a gap here.

    A null ``distribution_count`` is what makes a null ``cvsg_date`` read as
    "never parsed" rather than "no CVSG", so filling the count on its own would
    promote an unknown CVSG to an observed absence. These rows belong to
    ``backfill-live-signals``, which fills the family in one statement — and an
    interim application docket, deliberately null, sits here too.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/1", "24-100", distribution_count=None),
                _row("scotus/2", "24A1099", distribution_count=None),  # an application
            ],
        )
        for case_id in ("scotus/1", "scotus/2"):
            corpus.upsert_snapshot(conn, case_id, date(2026, 8, 1), _live(_OWN, _MOTION))
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert (_stored(conn, "scotus/1"), _stored(conn, "scotus/2")) == (None, None)
    assert (result.observable, result.no_stored_count) == (2, 2)
    assert (result.changed, result.changed_case_ids) == (0, [])


def test_an_empty_proceedings_list_is_degradation_not_a_count_of_zero(tmp_path: Path) -> None:
    """The confident zero the bypassed max latch existed to reject.

    A payload disclosing an *empty* entry list is a served shell — every
    live-polled SCOTUS docket carries at least its docketing entry — so reading
    it as "parsed, never distributed" and writing 0 over a stored count is
    exactly the regression the latch used to stop. Keying observability on the
    entries rather than on the proceedings key is what keeps that closed.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/1", "24-100")])
        corpus.upsert_snapshot(conn, "scotus/1", date(2026, 8, 1), _live())
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert _stored(conn, "scotus/1") == 2
    assert (result.observable, result.unobservable, result.changed) == (0, 1, 0)
    # The census frame's own residue is published beside the write frame's, so
    # the band matrix is never read as a cut over the whole frame.
    assert (result.scored_segment, result.scored_segment_unobservable) == (0, 1)


def test_a_subsampled_census_frame_row_refuses_the_band_cut(tmp_path: Path) -> None:
    """The band matrix counts raw, as both censuses do, so it refuses a weight.

    Published beside `distribution-census` figures, a denial-sampled row would
    silently stand for ten. The *write* is per-row and indifferent to weight,
    which is why the refusal is keyed on the census frame rather than the walk.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [_row("scotus/1", "24-100").model_copy(update={"sample_weight": 10.0})]
        )
        corpus.upsert_snapshot(conn, "scotus/1", date(2026, 8, 1), _live(_OWN, _MOTION))
        with pytest.raises(ValueError, match="must not run over a subsampled census frame"):
            rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert _stored(conn, "scotus/1") == 2


def test_the_incumbent_parse_moves_nothing_when_the_column_agrees_with_it(
    tmp_path: Path,
) -> None:
    """The control run that licenses reading a candidate's changes as the parse.

    The stored column is the incumbent reading of these same snapshots, so a
    pass under the incumbent parse must move nothing. Anything it does move is
    stored-column drift — a degraded payload, a dedupe merge-max, a backfill
    gap — and would otherwise be folded into the candidate's count and
    attributed to the reading.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        _seed(conn)
        control = rederive_distribution_counts(conn, parse="dist-v1", apply=True)
        assert _stored(conn, "scotus/1") == 2
    assert (control.observable, control.changed) == (2, 0)


def test_a_second_pass_over_a_converged_column_writes_nothing(tmp_path: Path) -> None:
    """Idempotent: a converged column recomputes to itself."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        _seed(conn)
        first = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        second = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert _stored(conn, "scotus/1") == 1
    assert first.changed == 1
    assert (second.changed, second.unchanged) == (0, 2)
    assert second.changed_case_ids == []


def test_the_write_frame_is_the_live_slice_and_the_band_cut_is_the_census_frame(
    tmp_path: Path,
) -> None:
    """Two denominators, both published, because they answer different questions.

    The column is the corpus's, so the write covers every live-slice SCOTUS row
    — an IFP petition among them. A band label is a claim about a petition the
    gate scores, so that same row is written without being banded, and the
    square is emitted whole so an observed zero is never an omitted cell.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/1", "24-100"),  # scored segment: written and banded
                _row("scotus/2", "24-5001"),  # IFP: written, never banded
                corpus.CorpusRow(  # outside the live slice: not the column's support
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="24-102",
                    case_name="John Doe v. Roe",
                    distribution_count=2,
                ),
            ],
        )
        for case_id in ("scotus/1", "scotus/2", "scotus/3"):
            corpus.upsert_snapshot(conn, case_id, date(2026, 8, 1), _live(_OWN, _MOTION))
        result = rederive_distribution_counts(conn, parse="dist-v2", apply=True)
        assert (_stored(conn, "scotus/1"), _stored(conn, "scotus/2")) == (1, 1)
        # Never walked: the bulk import parsed no proceedings, so a non-live row
        # carries no count for a parse to disagree with.
        assert _stored(conn, "scotus/3") == 2
    assert (result.eligible, result.changed) == (2, 2)
    assert (result.scored_segment, result.scored_segment_changed) == (1, 1)
    assert result.band_changed == 1
    vocabulary = SCORERS[SALIENCE_VERSION].bands
    assert [(m.from_band, m.to_band) for m in result.band_moves] == [
        (from_band, to_band) for from_band in vocabulary for to_band in vocabulary
    ]
    # The `from` side is the STORED column, not a second reading of the
    # snapshot — which is what the gate is really banding on today.
    assert [(m.from_band, m.to_band, m.n) for m in result.band_moves if m.n] == [
        ("elevated", "baseline", 1)
    ]


def test_the_command_prints_both_denominators_and_the_occupied_moves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The banner states coverage and the untouched residue, not just a count."""
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        _seed(conn)
        corpus.upsert_rows(conn, [_row("scotus/3", "24-102")])  # no snapshot: unobservable
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = CliRunner().invoke(app, ["rederive-distribution-counts", "--parse", "dist-v2"])
    assert result.exit_code == 0, result.output
    assert "would rewrite 1 of 2 observable row(s) (66.7% of 3)" in result.output
    assert "1 down, 0 up; 1 unobservable and 0 never-counted, both untouched" in result.output
    assert "elevated -> baseline: 1" in result.output


def test_the_command_refuses_above_the_bound_and_says_what_to_do(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The refusal exits non-zero, so a dispatched sweep fails rather than reports."""
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        _seed(conn)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = CliRunner().invoke(
        app, ["rederive-distribution-counts", "--parse", "dist-v2", "--apply", "--max-changes", "0"]
    )
    assert result.exit_code == 1, result.output
    assert "refusing to apply 1 count rewrite(s)" in result.stderr
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        assert _stored(conn, "scotus/1") == 2
