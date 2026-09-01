"""The denial-sampling weight rule, and the block it has to check its claim against.

A weight of `LEGACY_DENIAL_SAMPLE_EVERY` asserts that one row stands for itself
and the nine petitions the walk passed over. Landing on the sample grid at or
below the walker's cursor does not establish that: it proves the serial was
*probed*, and probing coincided with one-in-ten keeping only during the legacy
sampled walk. So the rule checks the claim where it is falsifiable — against the
neighbourhood — and these pin that, the boundary it turns on, and the failure
directions either side of it.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Literal

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline import ingest as ingest_module
from fedcourtsai.pipeline.ingest import (
    _ENUMERATED_BLOCK_MIN_KEPT,
    LEGACY_DENIAL_SAMPLE_EVERY,
    UNSAMPLED_WEIGHT,
    backfill_live_signals,
    legacy_denial_sample_weight,
    legacy_sample_cell,
    live_slice_serials,
    sampled_block_is_enumerated,
)
from fedcourtsai.pipeline.live import ingest_live_payload
from fedcourtsai.schemas import Disposition
from tests.test_live import _DENIED_ENTRY, _GRANTED_ENTRY, _payload

_POLLED = date(2026, 7, 1)
#: Comfortably past every serial these tests use, in both streams, so what
#: decides a weight is the grid and the block rather than an unprobed cell.
_CURSOR = 9000
_PAID = (19, "historical-paid")
_IFP = (19, "historical-ifp")


def _row(
    serial: int,
    *,
    term: int = 19,
    disposition: Disposition | None = Disposition.denied,
    live: bool = True,
) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {
            "case_id": f"scotus/{term}{serial:07d}",
            "court": "scotus",
            "docket_number": f"{term}-{serial}",
            "disposition": None if disposition is None else disposition.value,
            "last_live_polled": _POLLED if live else None,
        }
    )


def _seed_frame(tmp_path: Path, rows: list[corpus.CorpusRow], *, cursor: int = _CURSOR) -> Path:
    """Land a walk's stored rows and its cursors; return the corpus path.

    Split out from :func:`_seeded` because the writer-seam tests below drive
    ``ingest_live_payload``, which opens its own connections — the frame has to
    be a committed corpus rather than a connection held open around them.

    ``cursor`` is settable because :func:`corpus.set_live_cursor` is forward-only
    — a later write below the stored serial is ignored — so a test that needs the
    walk caught mid-stream has to seed the cursor there rather than move it back.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        for term in (19, 20):
            for stream in ("historical-paid", "historical-ifp"):
                corpus.set_live_cursor(conn, term, stream, cursor)
        conn.commit()
    return db


@contextmanager
def _seeded(tmp_path: Path, rows: list[corpus.CorpusRow]) -> Iterator[sqlite3.Connection]:
    db = _seed_frame(tmp_path, rows)
    with corpus.connect(db) as conn:
        yield conn


def _sampled(lo: int, hi: int, *, term: int = 19) -> list[corpus.CorpusRow]:
    """A range walked at one-in-ten: only the grid serials were kept."""
    return [
        _row(serial, term=term)
        for serial in range(lo, hi + 1)
        if serial % LEGACY_DENIAL_SAMPLE_EVERY == 0
    ]


def _enumerated(lo: int, hi: int, *, term: int = 19) -> list[corpus.CorpusRow]:
    """A range walked to completeness: every serial kept."""
    return [_row(serial, term=term) for serial in range(lo, hi + 1)]


def _weight(conn: sqlite3.Connection, number: str) -> int:
    return legacy_denial_sample_weight(conn, number, Disposition.denied.value)


def test_a_sampled_blocks_grid_denial_derives_the_sampled_weight(tmp_path: Path) -> None:
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY


def test_an_enumerated_blocks_grid_denial_stays_unsampled(tmp_path: Path) -> None:
    """The conjunct, and the double-count it exists to stop.

    The serial is on the grid and below the cursor exactly as in the sampled
    case. What differs is that the nine petitions a weight of ten would speak
    for are each already stored, so the corpus is counting them at
    ``UNSAMPLED_WEIGHT`` and a ten here invents nine more.
    """
    with _seeded(tmp_path, _enumerated(900, 1100)) as conn:
        assert _weight(conn, "19-1000") == UNSAMPLED_WEIGHT


def test_a_term_walked_under_both_regimes_is_read_per_row(tmp_path: Path) -> None:
    """The reason the read is a neighbourhood and not a verdict on the Term.

    The enumerating walk resumes from the sampled walk's persisted cursor, so one
    (Term, stream) can carry a sampled prefix and an enumerated tail. Any
    whole-cell verdict hands one regime's answer to the other's rows — and the
    direction that matters is the sampled verdict landing on the enumerated tail,
    which fabricates petitions the corpus already holds.
    """
    rows = _sampled(10, 4000) + _enumerated(4001, 4400)
    with _seeded(tmp_path, rows) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY  # in the prefix
        assert _weight(conn, "19-4200") == UNSAMPLED_WEIGHT  # in the tail


def test_the_streams_carry_separate_neighbourhoods(tmp_path: Path) -> None:
    """Paid and IFP were walked under their own cursors, so under their own regimes.

    The serials would collide if the cell were only the Term: ``19-1000`` and
    ``19-6000`` sit in different streams and must not read each other's blocks.
    """
    rows = _sampled(10, 2000) + _enumerated(5900, 6100)
    with _seeded(tmp_path, rows) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY
        assert _weight(conn, "19-6000") == UNSAMPLED_WEIGHT


def test_the_walks_grant_family_keeps_do_not_tip_a_sampled_block(tmp_path: Path) -> None:
    """The sampled walk kept the grant family in full, off-grid serials included.

    A presence test would read those as enumeration and demote genuinely sampled
    rows; the counted threshold is what absorbs them.
    """
    rows = _sampled(10, 2000) + [
        _row(serial, disposition=Disposition.granted) for serial in (995, 997, 1003)
    ]
    with _seeded(tmp_path, rows) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY


def test_a_stored_petition_of_any_disposition_counts_as_observed(tmp_path: Path) -> None:
    """What the claim is about is petitions, not denials.

    A block the corpus holds row by row falsifies the sampling claim whatever
    those rows resolved to, so the neighbourhood read is disposition-blind.
    """
    rows = _sampled(10, 2000) + [
        _row(serial, disposition=Disposition.granted)
        for serial in range(991, 1010)
        if serial != 1000
    ]
    with _seeded(tmp_path, rows) as conn:
        assert _weight(conn, "19-1000") == UNSAMPLED_WEIGHT


def test_the_threshold_sits_in_the_band_the_two_regimes_leave_empty(tmp_path: Path) -> None:
    """One neighbour below the cut is still sampled; the cut itself is not.

    Pinned because the exact cut is the difference between demoting a sampled row
    and keeping a fabricated weight, and it is invisible from the real corpus,
    whose regimes sit far either side of it — a sampled block holds at most six
    stored neighbours there and an enumerated one at least ten.
    """
    below = [_row(serial) for serial in range(994, 994 + _ENUMERATED_BLOCK_MIN_KEPT - 1)]
    assert len(below) == _ENUMERATED_BLOCK_MIN_KEPT - 1
    with _seeded(tmp_path, [_row(1000), *below]) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY
    with _seeded(tmp_path, [_row(1000), *below, _row(1003)]) as conn:
        assert _weight(conn, "19-1000") == UNSAMPLED_WEIGHT


def test_the_cut_clears_the_sampled_regimes_observed_ceiling(tmp_path: Path) -> None:
    """The margin is spent on catching enumeration, not on preserving sampling.

    A sampled block picks up the walk's grant-family keeps — at most six of them
    across the whole corpus. The cut sits above that ceiling, so no observed
    sampled shape is demoted, and below the enumerated floor of ten, so the slack
    in the empty band goes to the side whose error fabricates petitions.
    """
    ceiling = [
        _row(serial, disposition=Disposition.granted)
        for serial in (994, 996, 997, 1002, 1004, 1008)
    ]
    assert len(ceiling) == 6
    with _seeded(tmp_path, [*_sampled(10, 2000), *ceiling]) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY


def test_the_block_reaches_both_ways(tmp_path: Path) -> None:
    """Which side of a kept serial the passed-over petitions fell is not recorded,
    so the read looks both ways and a one-sided block counts as much as a split one.

    This is what the walk's resume boundary lands on — the last sampled serial
    before an enumerated tail sees that tail and nothing below it — and the cut
    resolves it toward :data:`UNSAMPLED_WEIGHT`. That direction forgoes a
    correction rather than inventing the absent range below, which is the safe
    side of the asymmetry the threshold is placed on.
    """
    for neighbours in (
        _enumerated(1001, 1000 + _ENUMERATED_BLOCK_MIN_KEPT),  # all above
        _enumerated(1000 - _ENUMERATED_BLOCK_MIN_KEPT, 999),  # all below
    ):
        with _seeded(tmp_path, [_row(1000), *neighbours]) as conn:
            assert _weight(conn, "19-1000") == UNSAMPLED_WEIGHT


def test_an_off_grid_denial_is_unsampled(tmp_path: Path) -> None:
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        assert _weight(conn, "19-1001") == UNSAMPLED_WEIGHT


def test_a_non_denial_is_unsampled_whatever_its_serial(tmp_path: Path) -> None:
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        for disposition in (Disposition.granted.value, Disposition.gvr.value, None):
            assert legacy_denial_sample_weight(conn, "19-1000", disposition) == UNSAMPLED_WEIGHT


def test_a_serial_beyond_its_cursor_is_unsampled(tmp_path: Path) -> None:
    """The walker never confirmed serving it, so nothing shows it was sampled."""
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        assert _weight(conn, f"19-{_CURSOR + 10}") == UNSAMPLED_WEIGHT


def test_an_unprobed_cell_is_unsampled(tmp_path: Path) -> None:
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        assert _weight(conn, "23-1000") == UNSAMPLED_WEIGHT


def test_the_marking_is_stripped_before_the_serial_is_read(tmp_path: Path) -> None:
    """A marked number parses as nothing, so both readings have to strip it."""
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        assert _weight(conn, "19-1000 *** CAPITAL CASE ***") == LEGACY_DENIAL_SAMPLE_EVERY


def test_a_marked_neighbour_still_counts_toward_its_block(tmp_path: Path) -> None:
    """The strip matters most on the *neighbourhood* side, and in the unsafe
    direction: an unstripped marking keeps that petition out of every block it
    belongs to, so the blocks around it read emptier than they are and tip toward
    the sampled weight — which is the direction that fabricates observations."""
    marked = [
        corpus.CorpusRow.model_validate(
            {
                "case_id": f"scotus/19{serial:07d}",
                "court": "scotus",
                "docket_number": f"19-{serial} *** CAPITAL CASE ***",
                "disposition": Disposition.denied.value,
                "last_live_polled": _POLLED,
            }
        )
        for serial in range(991, 1010)
        if serial != 1000
    ]
    with _seeded(tmp_path, [*_sampled(10, 2000), *marked]) as conn:
        assert _weight(conn, "19-1000") == UNSAMPLED_WEIGHT


def test_an_unparseable_number_is_unsampled(tmp_path: Path) -> None:
    with _seeded(tmp_path, _sampled(10, 2000)) as conn:
        for number in ("", "19A11", "Docket 17-2737***; 17-2741***"):
            assert _weight(conn, number) == UNSAMPLED_WEIGHT


def test_the_neighbourhood_ignores_rows_outside_the_live_slice(tmp_path: Path) -> None:
    """`sample_weight` is a walk-construction fact about the live slice, so the
    bulk import's rows must not decide whether a block was walked."""
    rows = _sampled(10, 2000) + [
        _row(serial, live=False) for serial in range(991, 1010) if serial != 1000
    ]
    with _seeded(tmp_path, rows) as conn:
        assert _weight(conn, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY


def test_a_shared_reading_is_the_same_as_a_per_call_one(tmp_path: Path) -> None:
    """The batch optimization must change the cost of an answer, never the answer."""
    rows = _sampled(10, 4000) + _enumerated(4001, 4400)
    with _seeded(tmp_path, rows) as conn:
        shared = live_slice_serials(conn)
        for number in ("19-1000", "19-4200", "19-1001", "19-6000"):
            assert legacy_denial_sample_weight(
                conn, number, Disposition.denied.value, serials=shared
            ) == legacy_denial_sample_weight(conn, number, Disposition.denied.value)


def test_backfill_weights_an_enumerated_block_at_one(tmp_path: Path) -> None:
    """The conjunct through its real caller, which is the only writer of these.

    The rule is reached from `backfill_live_signals` with a shared reading, so the
    threading and its `serials` short-circuit need coverage at that seam and not
    only at the rule's own.
    """
    rows = _sampled(10, 4000) + _enumerated(4001, 4400)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with _seeded(tmp_path, rows) as conn, conn:
        conn.execute("UPDATE cases SET sample_weight = NULL")

    signals, weights = backfill_live_signals(db)
    assert weights == len(rows)

    with corpus.connect(db) as conn:
        prefix = corpus.get_row(conn, "scotus/190001000")
        tail = corpus.get_row(conn, "scotus/190004200")
        off_grid = corpus.get_row(conn, "scotus/190004201")
    assert prefix is not None and prefix.sample_weight == LEGACY_DENIAL_SAMPLE_EVERY
    assert tail is not None and tail.sample_weight == UNSAMPLED_WEIGHT
    assert off_grid is not None and off_grid.sample_weight == UNSAMPLED_WEIGHT

    # Idempotent: nothing is left NULL, so the second pass weighs nothing.
    assert backfill_live_signals(db) == (signals, 0)


def test_the_guard_leaves_every_genuinely_sampled_row_at_its_sampled_weight(
    tmp_path: Path,
) -> None:
    """The blob's own sampled shape, reproduced: off-grid keeps inside the blocks.

    On the real corpus 1,156 of the 2,583 stored weight-10 rows have at least one
    off-grid live-slice sibling within nine either side (682 in the block above
    alone), because the sampled walk kept the grant family in full. So a
    *presence* test — cell-wide or block-scoped — demotes genuinely sampled rows
    and destroys the weight that keeps the legacy frame from biasing a base rate.
    The majority test absorbs those keeps: every grid serial here holds its
    sampled weight while its block carries scattered off-grid neighbours.
    """
    sampled = _sampled(10, 2000)
    keeps = [
        _row(serial, disposition=Disposition.granted)
        for serial in (993, 996, 1002, 1007, 1493, 1998)
    ]
    with _seeded(tmp_path, [*sampled, *keeps]) as conn:
        demoted = [
            row.docket_number
            for row in sampled
            if _weight(conn, row.docket_number) != LEGACY_DENIAL_SAMPLE_EVERY
        ]
        assert demoted == []


def test_the_unguarded_rule_would_over_weight_a_fully_walked_range(tmp_path: Path) -> None:
    """The latent bug the conjunct closes, sized on a fixture.

    Without it every on-grid denial in an enumerated range derives the sampled
    weight — on the real corpus that is 1,567 on-grid stored-weight-1 denials,
    1,224 of them in the paid scored segment, each of which would come out of the
    back-fill standing for nine petitions the corpus separately holds. The guard
    takes that population to zero here; on the blob it leaves only the documented
    poller-inside-a-sampled-range residue, which is off-grid-neighbour-free by
    construction and so invisible to any neighbourhood test.
    """
    rows = _enumerated(900, 1100)
    # The interior grid serials — the two at the range's edges are excluded
    # because half of each one's block lies outside the walked range, which is
    # the one-sided case pinned above rather than anything about this one.
    on_grid = [f"19-{serial}" for serial in range(910, 1091, LEGACY_DENIAL_SAMPLE_EVERY)]
    assert len(on_grid) == 19
    with _seeded(tmp_path, rows) as conn:
        empty: dict[tuple[int, str], frozenset[int]] = {}
        unguarded = [
            number
            for number in on_grid
            if legacy_denial_sample_weight(conn, number, Disposition.denied.value, serials=empty)
            == LEGACY_DENIAL_SAMPLE_EVERY
        ]
        assert unguarded == on_grid  # every one of them, over-weighted
        assert [number for number in on_grid if _weight(conn, number) != UNSAMPLED_WEIGHT] == []


def test_live_slice_serials_groups_by_cell(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_row(1000), _row(6000), _row(1001, live=False)]) as conn:
        assert live_slice_serials(conn) == {_PAID: frozenset({1000}), _IFP: frozenset({6000})}


def test_sampled_block_is_enumerated_reads_only_its_own_cell() -> None:
    """The helper takes the map rather than the connection, so the boundary it
    draws is visible without a corpus behind it."""
    span = LEGACY_DENIAL_SAMPLE_EVERY - 1
    block = frozenset(range(1000 - span, 1000 + span + 1)) - {1000}
    assert sampled_block_is_enumerated({_PAID: block}, _PAID, 1000)
    assert not sampled_block_is_enumerated({_IFP: block}, _PAID, 1000)
    assert not sampled_block_is_enumerated({}, _PAID, 1000)


def test_legacy_sample_cell_reads_the_cell_and_the_serial() -> None:
    """Both come back from one parse: two parses are how the cell and the grid
    test drift apart, and the stream split is part of the cell rather than a
    second reading of the same serial."""
    assert legacy_sample_cell("19-840") == (_PAID, 840)
    assert legacy_sample_cell("19-5850") == (_IFP, 5850)
    assert legacy_sample_cell("19-840 *** CAPITAL CASE ***") == (_PAID, 840)
    assert legacy_sample_cell("26A11") is None
    assert legacy_sample_cell("") is None


# --- the writer seam ------------------------------------------------------------
#
# Deriving the rule correctly is half of it. The other half is that no channel
# writing with certainty can bypass it: a walker re-serve, a rotation re-poll, or
# a frontier onboard that asserts `UNSAMPLED_WEIGHT` on a grid denial whose block
# is still stored one row in ten min-latches away a sampling weight nothing
# observed the nine petitions behind. Every live-channel SCOTUS write funnels
# through `ingest_live_payload`, so that is where the assertion is checked.


def _serve(
    db: Path,
    tmp_path: Path,
    number: str,
    *,
    denied: bool = True,
    weight: int = UNSAMPLED_WEIGHT,
    form: Literal["cert", "application"] = "cert",
) -> int | None:
    """Re-serve one docket through the live-ingest seam; read back its stored weight."""
    entry = _DENIED_ENTRY if denied else _GRANTED_ENTRY
    payload = _payload(number, proceedings=[entry])
    term, serial = number.split("-")
    docket_id = int(f"{term}{int(serial):07d}")
    result = ingest_live_payload(
        db, tmp_path / "data", payload, docket_id, today=_POLLED, sample_weight=weight, form=form
    )
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, result.case_id)
    assert stored is not None
    return stored.sample_weight


def test_a_certainty_write_onto_a_sampled_block_keeps_the_sampled_weight(
    tmp_path: Path,
) -> None:
    """The latch this guard exists to stop, at the seam that used to write it.

    The walker re-serves one grid denial inside a range still stored one row in
    ten. It includes that row with certainty and says so — but certainty about
    *this* petition is not observation of the nine it stands for, and the block
    around it is untouched. So the weight is derived, not taken, and the row
    keeps the ten.
    """
    db = _seed_frame(tmp_path, _sampled(10, 2000))
    assert _serve(db, tmp_path, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY


def test_a_certainty_write_onto_an_enumerated_block_lands_at_one(tmp_path: Path) -> None:
    """The other side, and why the guard is not simply "never write 1 on the grid".

    Same grid serial, same cursor, same assertion — but here the walk has stored
    the block row by row, so the nine petitions are counted individually and a
    ten would invent nine more. The certainty is warranted and is written.
    """
    db = _seed_frame(tmp_path, _enumerated(900, 1100))
    assert _serve(db, tmp_path, "19-1000") == UNSAMPLED_WEIGHT


def test_a_repaired_weight_survives_a_later_re_serve(tmp_path: Path) -> None:
    """The durability property: repair, then re-walk, and the repair is still there.

    The min-latch keeps the smaller of stored and incoming, so an incoming 1 is
    what erases a repaired 10 — and before this guard every re-serve carried one.
    With the weight derived against the unchanged block the re-serve carries a
    10 instead, and ``MIN(10, 10)`` holds. This is the whole reason the guard is
    the durable half of the repair rather than a tidy-up beside it.
    """
    db = _seed_frame(tmp_path, _sampled(10, 2000))
    # The writer-lane pass sets the row to the sampled weight.
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET sample_weight = ? WHERE case_id = ?",
            (LEGACY_DENIAL_SAMPLE_EVERY, "scotus/190001000"),
        )
        conn.commit()
    assert _serve(db, tmp_path, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY
    # And again: idempotent, not merely surviving one pass.
    assert _serve(db, tmp_path, "19-1000") == LEGACY_DENIAL_SAMPLE_EVERY


def test_a_re_serve_regresses_the_weight_once_the_block_is_enumerated(tmp_path: Path) -> None:
    """The guard withholds the regression; it does not prevent it.

    The point of the sampling weight is that it lapses when the walk actually
    enumerates the range. Repair the row to 10, then enumerate its block and
    re-serve it: the derivation now reads the block as walked row by row, writes
    1, and the min-latch takes it. A guard that latched 10 permanently would
    freeze the legacy frame into a corpus that had outgrown it.
    """
    db = _seed_frame(tmp_path, _sampled(10, 2000))
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET sample_weight = ? WHERE case_id = ?",
            (LEGACY_DENIAL_SAMPLE_EVERY, "scotus/190001000"),
        )
        corpus.upsert_rows(conn, _enumerated(991, 1009))
        conn.commit()
    assert _serve(db, tmp_path, "19-1000") == UNSAMPLED_WEIGHT


def test_a_grant_on_the_grid_is_written_with_the_certainty_it_was_included_with(
    tmp_path: Path,
) -> None:
    """The sample was drawn over denials only, so a grant short-circuits.

    Its serial is on the grid inside a sampled block — the two conditions that
    decide a denial — and it still lands at 1, because the walk kept the grant
    family in full and no grant ever stood for nine others.
    """
    db = _seed_frame(tmp_path, _sampled(10, 2000))
    assert _serve(db, tmp_path, "19-1000", denied=False) == UNSAMPLED_WEIGHT


def test_an_application_write_is_outside_the_sampled_frame(tmp_path: Path) -> None:
    """The application rotation's rows can never be sampled-frame rows.

    An application number is not a Term-form docket number, so it names no walk
    cell and no serial: the derivation falls through on the parse, before the
    cursor read or the live-slice scan the density guard needs.
    """
    db = _seed_frame(tmp_path, _sampled(10, 2000))
    payload = _payload("19A11", proceedings=[_DENIED_ENTRY])
    result = ingest_live_payload(
        db, tmp_path / "data", payload, 190009911, today=_POLLED, form="application"
    )
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, result.case_id)
    assert stored is not None and stored.sample_weight == UNSAMPLED_WEIGHT


def test_a_caller_asserting_a_weight_it_alone_knows_is_written_as_given(
    tmp_path: Path,
) -> None:
    """Only an assertion of *certainty* is re-derived.

    A caller passing anything else is claiming knowledge the corpus cannot
    reproduce — the seam has no way to check it and no business overwriting it —
    so it is written as given and left to the min-latch. Pinned because the
    guard's shape reads as "derive the weight" and it is in fact "check the
    certainty": an enumerated block, where the derivation would say 1.
    """
    db = _seed_frame(tmp_path, _enumerated(900, 1100))
    assert _serve(db, tmp_path, "19-1000", weight=LEGACY_DENIAL_SAMPLE_EVERY) == (
        LEGACY_DENIAL_SAMPLE_EVERY
    )


def test_the_forward_walk_writes_certainty_because_its_cursor_trails_it(
    tmp_path: Path,
) -> None:
    """The path where the assertion and the derivation always agree, and why.

    The walker sets a stream's cursor *after* each serial is served, so at ingest
    the stored cursor is ``serial - 1`` and the rule's cursor conjunct
    short-circuits before the density guard is consulted. A forward walk
    therefore writes :data:`UNSAMPLED_WEIGHT` on an on-grid denial even where its
    block is sparse — which is what lets a re-walk regress the legacy frame at
    all. The guard bites on the below-cursor re-serves instead, which the tests
    above cover.
    """
    # The walk is *at* 1000: every serial below it is served and its cursor
    # trails by one. The same block is sparse, so a below-cursor re-serve here
    # would derive the sampled weight — the contrast is the cursor alone.
    db = _seed_frame(tmp_path, _sampled(10, 2000), cursor=999)
    assert _serve(db, tmp_path, "19-1000") == UNSAMPLED_WEIGHT


def test_the_cheap_conjuncts_are_settled_before_the_slice_is_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ordering pinned as behavior, not as a docstring claim.

    The density guard's read is the one expensive step, and the seam now runs
    per row rather than once per batch — so a reordering that put it ahead of
    the disposition, parse, grid or cursor tests would make every live write pay
    it. Making the read raise turns that from a performance regression, which no
    test would catch, into a failure.
    """
    monkeypatch.setattr(
        ingest_module,
        "live_slice_serials",
        lambda conn: pytest.fail("the live slice was read for a row the cheap tests settle"),
    )
    db = _seed_frame(tmp_path, _sampled(10, 2000))
    assert _serve(db, tmp_path, "19-1000", denied=False) == UNSAMPLED_WEIGHT  # not a denial
    assert _serve(db, tmp_path, "19-1001") == UNSAMPLED_WEIGHT  # off the grid
    assert _serve(db, tmp_path, "21-1000") == UNSAMPLED_WEIGHT  # cell never probed
    payload = _payload("19A11", proceedings=[_DENIED_ENTRY])
    ingest_live_payload(
        db, tmp_path / "data", payload, 190009911, today=_POLLED, form="application"
    )
