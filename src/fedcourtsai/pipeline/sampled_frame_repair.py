"""The writer-lane repair of the legacy denial-sampling frame's latched-down rows.

The population is the one `docs/freeze-record.md` registers: live-slice SCOTUS
rows the guarded rule :func:`~.ingest.legacy_denial_sample_weight` derives at
:data:`~.ingest.LEGACY_DENIAL_SAMPLE_EVERY` and that are **stored at**
:data:`~.ingest.UNSAMPLED_WEIGHT` — grid denials genuinely inside sampled ranges
that some channel writing with certainty min-latched down to 1, leaving the nine
petitions each would have stood for represented by nobody.

**The rule is reused, never restated.** Every conjunct that decides whether a
block is still sampled — the grid test, the walker's cursor, and the density
guard's neighbourhood reading — is read out of the guard's own functions, so the
pass and the writer that has to keep its result cannot drift apart. What this
module adds is the two things the guard has no opinion about: which rows are
*stored* below their derived weight, and which of those the freeze record
licenses the pass to touch.

**The scope is the registration's, and it is narrower than the rule's.** The
entry licenses magnitudes, never membership: the pass touches only rows that are
IFP, on the sampling grid, inside the eight ``historical-ifp`` OT2017-OT2024
cells, at or below their cell's cursor, and read as sampled by the density guard.
A row the rule derives at the sampled weight *outside* those cells is a different
population needing its own entry, so it is reported in the ledger and left
alone rather than silently repaired — reported rather than dropped, because the
one thing a maintainer cannot read off a ledger of repairs is the row it does not
mention. IFP membership is not a second filter beside the cell: the stream half
of a cell id is exactly the ``serial >= IFP_SERIAL_BASE`` reading, so
``historical-ifp`` *is* the IFP predicate.

**The write is a direct ``UPDATE`` that deliberately bypasses the upsert path's
min latch**, the precedent being the distribution re-derivation's bypass of the
max latch. The bypass is the pass: ``sample_weight`` min-latches — the stored
weight only ever latches downward, an inclusion probability only ever learned
toward certainty — so a 1 → 10 rewrite
routed through :func:`corpus.upsert_rows` would report success having changed
nothing. What replaces the latch is the guard, which is *narrower* than it: a row
whose block the corpus now stores row by row derives 1 and is never selected, so
this pass cannot invent a petition the corpus already counts.

The repaired weight is durable rather than merely written, and that property is
the guard's rather than this pass's: the live-ingest seam derives an asserted
certainty instead of taking it, so a re-serve of a repaired row carries a 10 and
``MIN(10, 10)`` holds. Without that half a repair would survive only until the
next walk touched the row.

Idempotent and self-checking: a repaired row is stored at its derived weight, so
it leaves the population it was selected from, and the apply re-runs the
selection and reports what remains — which must be zero. Like its ``set_*``
siblings the write is a direct ``UPDATE`` of the index and **never the casestore
mirror**, so a store-side rebuild from ``case.json`` would resurrect the latched
weights.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Final

from .. import corpus
from ..schemas import Disposition
from .ingest import (
    LEGACY_DENIAL_SAMPLE_EVERY,
    UNSAMPLED_WEIGHT,
    legacy_denial_sample_weight,
    legacy_sample_cell,
    live_slice_serials,
    stored_block_neighbours,
)

#: The walk stream the registered population sits in. Not a filter beside an IFP
#: test but the IFP test itself: :func:`~.ingest.legacy_sample_cell` reads the
#: stream off the serial against ``IFP_SERIAL_BASE``, which is what makes a
#: petition IFP.
REGISTERED_STREAM: Final = "historical-ifp"

#: The Terms of the eight registered cells, OT2017-OT2024, in the two-digit form
#: a modern docket number carries — 17 to 24 inclusive, which is the eight the
#: entry names. The registration is a fact about those cells' sampled coverage,
#: so a row in a Term outside them is outside the entry whatever the rule derives
#: for it.
REGISTERED_TERMS: Final = frozenset(range(17, 25))


@dataclass
class SampledFrameWeightRepair:
    """One stored row moving from its latched certainty to its derived weight."""

    case_id: str
    docket_number: str
    #: The ``(term, stream)`` walk cell whose cursor and neighbourhood decided
    #: the weight — the unit the denial sample was drawn in.
    cell: tuple[int, str]
    #: The October Term the cell's two-digit term names, read through the
    #: corpus's own century pivot rather than a local ``20{term}``. The ledger's
    #: out-of-scope lines are exactly where a pre-2000 docket would be misnamed,
    #: and those are the lines a maintainer adjudicates an unregistered
    #: population from. ``None`` only where the number will not parse as a Term
    #: form, which the cell reading has already ruled out.
    term_year: int | None
    serial: int
    was: int
    now: int
    #: Stored rows in the row's own eighteen-serial block, the occupancy the
    #: density guard thresholds. Printed as a distance from that threshold rather
    #: than as a verdict a reader could second-guess: the guard reads 7 or more as
    #: enumerated, so every selected row necessarily sits at 0 to 6, and what the
    #: number says is how much room the reading had. A ledger of 5s and 6s is one
    #: to triage; the sampled regime's own signature is far lower than that.
    block_neighbours: int


@dataclass
class SampledFrameRepairResult:
    """What the sampled-frame repair wrote (or would write on a dry run)."""

    applied: bool = False
    #: The registered population, in ``case_id`` order.
    repairs: list[SampledFrameWeightRepair] = field(default_factory=list)
    #: Rows the rule derives at the sampled weight that fall OUTSIDE the
    #: registered cells. Never repaired — a different population needs its own
    #: freeze-record entry — and never dropped either, because a widening
    #: predicate is only visible to a maintainer if the ledger names what it
    #: refused to touch.
    out_of_registration: list[SampledFrameWeightRepair] = field(default_factory=list)
    #: Live-slice SCOTUS denials stored at :data:`~.ingest.UNSAMPLED_WEIGHT` —
    #: the frame the two lists above are read out of, and the denominator that
    #: makes their size interpretable.
    scanned: int = 0
    #: True when ``apply`` was asked for but the blast-radius bound refused it.
    #: Nothing is written in that case — the plan is reported and abandoned.
    refused: bool = False
    #: The registered population re-selected AFTER the write: the apply's own
    #: witness, which must be zero. ``None`` on a dry run, where nothing was
    #: written and the population is by definition still there.
    remaining: int | None = None


def _within_registration(cell: tuple[int, str]) -> bool:
    """Whether a walk cell is one of the eight the freeze-record entry names."""
    term, stream = cell
    return stream == REGISTERED_STREAM and term in REGISTERED_TERMS


def _select(conn: sqlite3.Connection) -> SampledFrameRepairResult:
    """The membership predicate, as one read of the corpus.

    The SQL half is only the cheap part of it — live slice, SCOTUS, denied, and
    stored at certainty. Everything that decides whether the certainty is *wrong*
    comes from the guard's own rule, evaluated per row against one shared reading
    of the live slice's serials.
    """
    result = SampledFrameRepairResult()
    rows = conn.execute(
        "SELECT case_id, docket_number, disposition, sample_weight FROM cases "
        f"WHERE {corpus.LIVE_SLICE_SQL} AND court = 'scotus' "
        "AND sample_weight = ? AND disposition = ? ORDER BY case_id",
        (UNSAMPLED_WEIGHT, Disposition.denied.value),
    ).fetchall()
    result.scanned = len(rows)
    if not rows:
        return result
    # One reading of the live slice for the whole batch; the rule would otherwise
    # re-scan it per row. Built only where there is something to consider.
    serials = live_slice_serials(conn)
    for record in rows:
        number = str(record["docket_number"])
        read = legacy_sample_cell(number)
        if read is None:
            # Not a modern Term-form number, so no serial to test — the rule
            # falls through to the unsampled weight, which is what is stored.
            continue
        cell, serial = read
        derived = legacy_denial_sample_weight(
            conn, number, str(record["disposition"]), serials=serials
        )
        if derived != LEGACY_DENIAL_SAMPLE_EVERY:
            continue
        entry = SampledFrameWeightRepair(
            case_id=str(record["case_id"]),
            docket_number=number,
            cell=cell,
            term_year=corpus.scotus_term_year(number),
            serial=serial,
            was=int(record["sample_weight"]),
            now=derived,
            block_neighbours=stored_block_neighbours(serials, cell, serial),
        )
        if _within_registration(cell):
            result.repairs.append(entry)
        else:
            result.out_of_registration.append(entry)
    return result


def repair_sampled_frame_weights(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_repairs: int | None = None,
) -> SampledFrameRepairResult:
    """Restore the derived sampling weight on the registered latched-down rows.

    ``max_repairs`` is the blast-radius bound and lives here rather than in the
    caller, so a code caller is bounded on the same terms as the command. Over
    the bound nothing is written and ``refused`` is set — and the bound guards
    *membership* rather than magnitude, since the registered population is fixed
    by a predicate and a count above the one read off the dry run means the
    predicate reached rows the entry does not cover.

    The apply witnesses itself: the selection is re-run over the written corpus
    and its size reported in ``remaining``, which a converged apply leaves at
    zero. That is the check the pointer cannot be — a direct ``UPDATE`` of a
    column no downstream artifact recomputes moves the blob whether or not it
    moved the right rows.
    """
    result = _select(conn)
    result.applied = apply
    if apply and max_repairs is not None and len(result.repairs) > max_repairs:
        result.refused = True
        result.applied = False
        return result
    if not apply:
        return result

    with conn:
        for entry in result.repairs:
            # The direct UPDATE that is the whole point of the pass: routed
            # through `upsert_rows` this 1 -> 10 would meet the column's min
            # latch and be discarded, reporting success having written nothing.
            conn.execute(
                "UPDATE cases SET sample_weight = ? WHERE case_id = ?",
                (entry.now, entry.case_id),
            )
    result.remaining = len(_select(conn).repairs)
    return result
