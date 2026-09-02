"""The writer-lane repair of the sampled frame, and the guard it shares its rule with.

The pass exists because the ``sample_weight`` min latch cannot be asked to raise
a weight: a repair is a direct ``UPDATE`` or it is nothing. What these pin is the
two ways that could go wrong — a bypass that reaches rows the registration does
not cover, and a repair the next re-serve latches straight back down — plus the
bounded-apply procedure the writer lane runs it under.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.ingest import (
    LEGACY_DENIAL_SAMPLE_EVERY,
    UNSAMPLED_WEIGHT,
    legacy_denial_sample_weight,
    live_slice_serials,
)
from fedcourtsai.pipeline.sampled_frame_repair import (
    SampledFrameRepairResult,
    SampledFrameWeightRepair,
    repair_sampled_frame_weights,
)
from fedcourtsai.schemas import Disposition
from tests.test_legacy_denial_weight import _serve

_POLLED = date(2026, 7, 1)
#: Past every serial these tests use, so what decides a weight is the grid and
#: the block rather than an unprobed cell.
_CURSOR = 9000
#: A registered Term (OT2019) in the IFP stream, which is where the whole
#: registered population sits: an IFP serial is one at or above
#: ``IFP_SERIAL_BASE``, and that reading *is* the stream half of a walk cell.
_TERM = 19


def _row(
    serial: int,
    *,
    term: int = _TERM,
    weight: int | None = UNSAMPLED_WEIGHT,
    disposition: Disposition | None = Disposition.denied,
    live: bool = True,
) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {
            "case_id": f"scotus/{term}{serial:07d}",
            "court": "scotus",
            "docket_number": f"{term}-{serial}",
            "disposition": None if disposition is None else disposition.value,
            "sample_weight": weight,
            "last_live_polled": _POLLED if live else None,
        }
    )


def _sampled(lo: int, hi: int, *, term: int = _TERM) -> list[corpus.CorpusRow]:
    """A range walked at one-in-ten: only the grid serials were kept."""
    return [
        _row(serial, term=term)
        for serial in range(lo, hi + 1)
        if serial % LEGACY_DENIAL_SAMPLE_EVERY == 0
    ]


def _enumerated(lo: int, hi: int, *, term: int = _TERM) -> list[corpus.CorpusRow]:
    """A range walked to completeness: every serial kept, each at certainty."""
    return [_row(serial, term=term) for serial in range(lo, hi + 1)]


def _seed_frame(tmp_path: Path, rows: list[corpus.CorpusRow]) -> Path:
    """Land a walk's stored rows and its cursors; return the corpus path."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        for term in (16, _TERM):
            for stream in ("historical-paid", "historical-ifp"):
                corpus.set_live_cursor(conn, term, stream, _CURSOR)
        conn.commit()
    return db


@contextmanager
def _seeded(tmp_path: Path, rows: list[corpus.CorpusRow]) -> Iterator[sqlite3.Connection]:
    with corpus.connect(_seed_frame(tmp_path, rows)) as conn:
        yield conn


def _stored_weight(conn: sqlite3.Connection, case_id: str) -> int | None:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.sample_weight


# The sampled IFP frame these tests repair: a one-in-ten walk over an IFP range,
# every kept row latched down to certainty by the channel that served it.
_IFP_SAMPLED = (6000, 8000)


def test_the_pass_and_the_guard_agree_on_membership(tmp_path: Path) -> None:
    """The predicate is the guard's own rule, not a second reading of the frame.

    Three rows, one of each kind the frame holds, and for every one of them the
    pass's verdict is asserted to be the guard's: a grid denial inside a sampled
    block is repaired because the rule derives the sampled weight for it, and the
    two rows the rule derives 1 for are the two the pass leaves alone. Asserted
    against `legacy_denial_sample_weight` itself rather than against expected
    booleans, so a change to the rule moves both sides together or fails here.
    """
    rows = [
        *_sampled(*_IFP_SAMPLED),
        # An enumerated block inside the same cell: its grid denial is at 1
        # correctly, the corpus counting its neighbours one by one.
        *_enumerated(5000, 5200),
        # A grid denial already carrying the sampled weight — nothing to repair.
        _row(8500, weight=LEGACY_DENIAL_SAMPLE_EVERY),
    ]
    with _seeded(tmp_path, rows) as conn:
        serials = live_slice_serials(conn)
        result = repair_sampled_frame_weights(conn, apply=False)
        repaired = {entry.case_id for entry in result.repairs}

        for case_id, number in (
            ("scotus/190006500", "19-6500"),  # sampled block, latched to 1
            ("scotus/190005100", "19-5100"),  # enumerated block, correctly 1
            ("scotus/190008500", "19-8500"),  # already at the sampled weight
        ):
            derives_sampled = (
                legacy_denial_sample_weight(conn, number, Disposition.denied.value, serials=serials)
                == LEGACY_DENIAL_SAMPLE_EVERY
            )
            latched = _stored_weight(conn, case_id) == UNSAMPLED_WEIGHT
            assert (case_id in repaired) == (derives_sampled and latched), (
                f"{case_id}: the pass and the guard disagree about membership"
            )
        assert "scotus/190006500" in repaired
        assert repaired.isdisjoint({"scotus/190005100", "scotus/190008500"})


def test_a_row_outside_the_registered_cells_is_reported_not_repaired(tmp_path: Path) -> None:
    """The freeze-record entry's predicate is the scope law, and it bounds terms.

    An OT2016 IFP cell is walked and latched exactly as the registered ones are,
    and the rule derives the sampled weight for its grid denial all the same. It
    is still not this pass's population: the entry registers eight cells, and a
    row outside them needs its own entry. So it is named in the ledger — the one
    place a widening predicate is visible — and left at its stored weight.
    """
    rows = [*_sampled(*_IFP_SAMPLED), *_sampled(*_IFP_SAMPLED, term=16)]
    with _seeded(tmp_path, rows) as conn:
        result = repair_sampled_frame_weights(conn, apply=True, max_repairs=500)
        assert {entry.cell[0] for entry in result.repairs} == {_TERM}
        assert result.out_of_registration, "the out-of-scope Term reported nothing"
        assert {entry.cell for entry in result.out_of_registration} == {(16, "historical-ifp")}
        assert _stored_weight(conn, "scotus/160006500") == UNSAMPLED_WEIGHT


def test_a_paid_grid_denial_is_outside_the_registered_stream(tmp_path: Path) -> None:
    """IFP is not a filter beside the cell — it is the cell's stream half.

    A paid serial (below ``IFP_SERIAL_BASE``) in a registered Term reads as
    ``historical-paid``, so it is outside the registration however the rule reads
    its block. That is what keeps the pass off every scored-segment cut, all of
    which are gated on a paid serial.
    """
    with _seeded(tmp_path, [*_sampled(*_IFP_SAMPLED), *_sampled(100, 2000)]) as conn:
        result = repair_sampled_frame_weights(conn, apply=False)
        assert all(entry.cell[1] == "historical-ifp" for entry in result.repairs)
        assert {entry.cell for entry in result.out_of_registration} == {(_TERM, "historical-paid")}


def test_the_dry_run_writes_nothing(tmp_path: Path) -> None:
    """A dry run is a reading. It reports the population and leaves it there."""
    with _seeded(tmp_path, _sampled(*_IFP_SAMPLED)) as conn:
        result = repair_sampled_frame_weights(conn, apply=False)
        assert result.repairs and not result.applied
        assert result.remaining is None
        assert all(
            _stored_weight(conn, entry.case_id) == UNSAMPLED_WEIGHT for entry in result.repairs
        )


def test_the_apply_writes_the_derived_weight_and_re_derives_to_nothing(tmp_path: Path) -> None:
    """The direct UPDATE lands, and the pass's own witness says so.

    The min latch is why this cannot be an upsert: the same 1 -> 10 routed
    through `upsert_rows` keeps the smaller value and reports success having
    written nothing. So the write is asserted on the stored column, and the
    self-check — the selection re-run over the written corpus — is asserted to
    come back empty, which is the only evidence a caller has that the bypass
    reached the rows the ledger named.
    """
    with _seeded(tmp_path, _sampled(*_IFP_SAMPLED)) as conn:
        planned = repair_sampled_frame_weights(conn, apply=False)
        result = repair_sampled_frame_weights(conn, apply=True, max_repairs=500)
        assert len(result.repairs) == len(planned.repairs)
        assert result.remaining == 0
        assert all(
            _stored_weight(conn, entry.case_id) == LEGACY_DENIAL_SAMPLE_EVERY
            for entry in result.repairs
        )
        # Idempotent: the repaired rows have left the population they were
        # selected from, so a second dispatch is a no-op rather than a re-write.
        assert not repair_sampled_frame_weights(conn, apply=False).repairs


def test_an_upsert_would_have_been_a_silent_no_op(tmp_path: Path) -> None:
    """Why the pass bypasses the latch, pinned rather than asserted in prose.

    The same weight offered through the ordinary write path meets the min latch
    and is discarded — success, nothing written. A pass built on `upsert_rows`
    would report a repair it never made.
    """
    with _seeded(tmp_path, _sampled(*_IFP_SAMPLED)) as conn:
        corpus.upsert_rows(conn, [_row(6500, weight=LEGACY_DENIAL_SAMPLE_EVERY)])
        conn.commit()
        assert _stored_weight(conn, "scotus/190006500") == UNSAMPLED_WEIGHT
        repair_sampled_frame_weights(conn, apply=True, max_repairs=500)
        assert _stored_weight(conn, "scotus/190006500") == LEGACY_DENIAL_SAMPLE_EVERY


def test_the_repair_survives_a_later_min_latching_upsert(tmp_path: Path) -> None:
    """The interplay with the guard: repair, re-serve, and the repair holds.

    The durability half is the ingest seam's, not this pass's — but a repair that
    the next walk latched back to 1 would be a write with no effect on any
    published figure, so the pairing is pinned here as well as there. The
    re-serve carries an asserted certainty; the seam derives against the
    unchanged block and writes the sampled weight instead, and MIN(10, 10) holds.
    """
    db = _seed_frame(tmp_path, _sampled(*_IFP_SAMPLED))
    with corpus.connect(db) as conn:
        result = repair_sampled_frame_weights(conn, apply=True, max_repairs=500)
    assert result.remaining == 0
    assert _serve(db, tmp_path, "19-6500") == LEGACY_DENIAL_SAMPLE_EVERY


def test_the_bound_refuses_and_writes_nothing(tmp_path: Path) -> None:
    """Over the bound the plan is reported and abandoned, not truncated.

    A half-applied population is worse to reason about than a refused one, and
    on a registered re-weighting it is worse still: the ledger a maintainer read
    would describe a corpus that never existed.
    """
    with _seeded(tmp_path, _sampled(*_IFP_SAMPLED)) as conn:
        result = repair_sampled_frame_weights(conn, apply=True, max_repairs=1)
        assert result.refused and not result.applied
        assert result.remaining is None
        assert all(
            _stored_weight(conn, entry.case_id) == UNSAMPLED_WEIGHT for entry in result.repairs
        )


def test_a_null_weight_is_the_backfills_population_not_this_ones(tmp_path: Path) -> None:
    """A never-weighted row is left to the signals back-fill.

    The predicate is *stored at certainty*, which a NULL is not: nothing latched
    it down, so there is no min-latch error to undo, and the unattended
    `backfill_live_signals` hook already weights it under the same rule.
    """
    rows = [*_sampled(*_IFP_SAMPLED), _row(8500, weight=None)]
    with _seeded(tmp_path, rows) as conn:
        result = repair_sampled_frame_weights(conn, apply=False)
        assert "scotus/190008500" not in {entry.case_id for entry in result.repairs}


def test_the_ledger_carries_each_rows_block_occupancy(tmp_path: Path) -> None:
    """What a maintainer checks the verdict against, per row.

    The density guard's threshold sits at 7 stored neighbours; a sampled block
    holds at most 6. Printing the occupancy is what lets a reader see how far
    from that line each repair sat, so it is read from the guard's own window
    function rather than recomputed here.
    """
    with _seeded(tmp_path, _sampled(*_IFP_SAMPLED)) as conn:
        result = repair_sampled_frame_weights(conn, apply=False)
        # A one-in-ten walk stores no neighbour inside the eighteen-serial block:
        # the nearest kept serials either side are exactly ten away.
        assert {entry.block_neighbours for entry in result.repairs} == {0}


def _cli(tmp_path: Path, *args: str) -> tuple[int, str]:
    result = CliRunner().invoke(
        app,
        ["repair-sampled-frame-weights", *args],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus")},
    )
    return result.exit_code, result.output


def test_the_command_refuses_an_unbounded_apply(tmp_path: Path) -> None:
    """`--apply` without `--max-repairs` is a usage error, before any read."""
    _seed_frame(tmp_path, _sampled(*_IFP_SAMPLED))
    code, output = _cli(tmp_path, "--apply")
    assert code == 2
    assert "--apply requires an explicit --max-repairs" in output


def test_the_command_exits_non_zero_over_the_bound(tmp_path: Path) -> None:
    """The refusal is an exit code, after the ledger a maintainer triages from.

    The header says *refused*, not *dry-run*: nothing was written either way, but
    a dispatch that asked to write and was stopped is not the same record as a
    reading, and the header is what a reader attributes the ledger to.
    """
    _seed_frame(tmp_path, _sampled(*_IFP_SAMPLED))
    code, output = _cli(tmp_path, "--apply", "--max-repairs", "1")
    assert code == 1
    assert "refusing to apply" in output
    assert "(refused)" in output and "dry-run" not in output
    assert "refused to repair scotus/" in output, (
        "the refusal withheld the ledger it tells one to read"
    )


def test_the_command_prints_the_count_and_the_per_row_ledger(tmp_path: Path) -> None:
    """The dry run's product: a count over its frame, and one line per row.

    The frame carries an enumerated block the pass does not repair, so the count
    and its denominator differ: a ledger printing the repair count in the
    denominator's place would read as a whole frame repaired.
    """
    _seed_frame(tmp_path, [*_sampled(*_IFP_SAMPLED), *_enumerated(5000, 5200)])
    code, output = _cli(tmp_path)
    assert code == 0
    assert "would repair 201 row(s) of 402 live-slice SCOTUS denial(s)" in output
    assert "scotus/190006500 (19-6500): 1 -> 10" in output
    assert "cell OT2019/historical-ifp, serial 6500" in output


def test_the_command_reports_a_missing_corpus(tmp_path: Path) -> None:
    """Fails loud rather than reporting an empty population over no corpus."""
    code, output = _cli(tmp_path)
    assert code == 1
    assert "corpus database is missing" in output


def test_the_command_applies_and_converges(tmp_path: Path) -> None:
    """The apply's own witness reaches the exit code, which is what the workflow reads."""
    db = _seed_frame(tmp_path, _sampled(*_IFP_SAMPLED))
    code, output = _cli(tmp_path, "--apply", "--max-repairs", "500")
    assert code == 0, output
    assert "repaired 201 row(s)" in output
    with corpus.connect(db) as conn:
        assert _stored_weight(conn, "scotus/190006500") == LEGACY_DENIAL_SAMPLE_EVERY


def test_an_unconverged_apply_stops_the_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The witness's failing side, which nothing else in the suite reaches.

    A converged apply is the ordinary path and is pinned above; this is the branch
    the whole self-check exists for — a direct `UPDATE` that reached fewer rows
    than the ledger named. It is load-bearing at the workflow seam: under
    `set -euo pipefail` this exit code is what stops the step before
    `corpus-push`, so a partially-repaired blob is never published. Driven by
    replacing the pass's own result rather than by corrupting a corpus, because
    the failure it stands for is a write that silently did less than it said.
    """
    _seed_frame(tmp_path, _sampled(*_IFP_SAMPLED))
    stub = SampledFrameRepairResult(
        applied=True,
        repairs=[
            SampledFrameWeightRepair(
                case_id="scotus/190006500",
                docket_number="19-6500",
                cell=(_TERM, "historical-ifp"),
                term_year=2019,
                serial=6500,
                was=UNSAMPLED_WEIGHT,
                now=LEGACY_DENIAL_SAMPLE_EVERY,
                block_neighbours=0,
            )
        ],
        scanned=201,
        remaining=3,
    )
    monkeypatch.setattr(cli, "repair_sampled_frame_weights", lambda *a, **k: stub)
    code, output = _cli(tmp_path, "--apply", "--max-repairs", "500")
    assert code == 1
    assert "did not converge" in output
    assert "still selects 3 row(s)" in output
    # And it withholds the follow-through: nothing to follow through on until the
    # write is known to have landed.
    assert "fedcourts docket" not in output


def test_an_apply_names_the_artifacts_it_leaves_stale(tmp_path: Path) -> None:
    """The follow-through travels with the write, not with a doc.

    The corpus disagrees with every committed weighted artifact the moment the
    apply lands, and only some heal on the metrics schedule — the docket pack and
    the one committed prose figure carry no marker distinguishing a stale copy
    from a current one. So the apply names them, and names the half that does not
    move too, since "did I just re-base the leaderboard?" is the question a
    maintainer asks next.
    """
    _seed_frame(tmp_path, _sampled(*_IFP_SAMPLED))
    code, output = _cli(tmp_path, "--apply", "--max-repairs", "500")
    assert code == 0, output
    assert "fedcourts docket" in output
    assert "docs/outcome-decomposition.md" in output
    assert "No scored number moves" in output
    # A dry run has written nothing, so it owes no follow-through.
    _, dry = _cli(tmp_path)
    assert "fedcourts docket" not in dry
