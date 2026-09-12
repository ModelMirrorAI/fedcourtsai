"""Re-derive the corpus ``amicus_briefs`` column and re-freeze the committed
interim outcomes it was frozen onto, under the widened submitted-form reading.

The interim ``amicus_briefs`` count — a stakes proxy an interim forecast may
condition on, and the resolution end of the pre-registered ``amicus-increment``
claim — is *parsed* out of free docket-entry text. Which entries a reading
admits, and where it stops counting, is part of what a stored count means. The
widened reading (:func:`fedcourtsai.pipeline.interim_signals.amicus_briefs`,
:func:`~fedcourtsai.pipeline.interim_signals.amicus_briefs_through`) counts each
lead filer whose brief the docket shows as *submitted* and not yet accepted,
beyond the accepted-form entries the old reading counted, and cuts the count at
the **end of the disposition day** so an entry the Court filed once the
application was already decided is not counted into a number labelled "as at
resolution". The reading itself is live for every application frozen after it
merged; this pass is the **retrospective data motion** for the rows frozen under
the old one — registered in ``docs/freeze-record.md`` (the 2026-09-10
interim-amicus-reading entry, which pre-computes the affected set), scoped out of
the change that made the reading, and dispatched from ``run-repair``.

Two writes, in one bounded pass with one dry-run ledger, because they are two
ends of one correction:

**1. The corpus column, a direct ``UPDATE`` that bypasses the max latch.** The
ordinary ingestion path max-latches this column
(:func:`fedcourtsai.corpus._update_clause`): an amicus count only ever grows as
briefs accumulate, so a degraded live payload must never lower a stored count,
and the latch takes the larger of stored and incoming. The end-of-day cut is
exactly the write that latch is built to reject — dropping an after-disposition
entry moves a resolved row's count **down** — so routing it through
:func:`fedcourtsai.corpus.upsert_rows` would write nothing while reporting
success. A silent no-op that reads as convergence is worse than a refusal, so
the write goes through :func:`fedcourtsai.corpus.set_amicus_briefs`, which says
so. Bypassing a guard obliges naming what it was for and what replaces it: the
latch rejects any regression from any cause, and what replaces it here is
narrower — a row with **no readable disposition date** (an *open* application) is
left to the live channel, which polls it under the same widened reading, and a
row whose snapshot is missing or discloses no entries is counted
``unobservable`` and left untouched, never lowered. So the pass touches only a
**resolved** application (a readable disposition date, hence a fixed cut value
``live_rotation`` no longer re-polls) — exactly the rows whose resolution value
an ``outcome.json`` can freeze.

**2. The committed ``interim_signals`` blocks, re-frozen from the corrected
reading.** Nothing else re-freezes ``interim_signals`` today
(``disposition_convergence`` only *nulls* it when a withdrawal re-dates the
resolution). A committed interim outcome's ``interim_signals.amicus_briefs`` was
frozen from the corpus column at resolution
(:func:`fedcourtsai.pipeline.outcome.interim_resolution_signals`), so a row
frozen under the old reading disagrees with the corrected column. This pass
rewrites **that one field** to the re-derived value, leaving
``response_requested`` and ``referred_to_court`` — which the widened reading does
not touch — exactly as they were.

**The prediction end is never re-derived, and that is deliberate.** A committed
``prediction.json`` carries ``context.amicus_briefs`` — the prediction-time
snapshot the cell was handed (:func:`fedcourtsai.pipeline.asof`) — and it is
frozen *by design*, the immutable record of the information set the forecast was
made on. The two ends of the ``amicus-increment`` claim move at different times
on purpose (``docs/freeze-record.md``): this pass moves only the **resolution
end** on the committed ``outcome.json``, and touches no ``prediction.json`` at
all. :attr:`AmicusRederiveResult.context_amicus_untouched` is the ledger's
standing assertion of that invariant.

**The control is idempotence, not a second reading.** The reading is fixed in
code (the merged widening), not selected per dispatch, so there is no incumbent
reading to dry-run as a control. Re-running the pass after an apply is the
control: it re-derives the same values, finds the column and the committed
blocks already equal, and reports ``total_changes = 0``. A non-zero re-run means
the population moved (a new resolution) rather than that the reading did.

Durability: unlike the distribution re-derivation, this one needs no companion
change to the ingest default, because the widened reading **is** the ingest
default already — a re-poll of an open application re-derives the same widened
count. And the pass writes only resolved applications, which the live rotation no
longer polls, so nothing reverts what it lands.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .. import corpus
from ..schemas import Outcome
from ..serialize import read_model, write_json
from . import cert_signals
from .interim_signals import amicus_briefs_through, interim_disposition_date


@dataclass(frozen=True, kw_only=True)
class AmicusRefreeze:
    """One committed interim outcome whose ``interim_signals.amicus_briefs`` moves."""

    #: ``"<case_id>/<event_id>"``.
    ref: str
    #: The frozen count the outcome carried, under the old reading.
    was: int
    #: The re-derived count under the widened reading and the end-of-day cut.
    now: int


@dataclass
class AmicusRederiveResult:
    """What one re-derive-and-re-freeze pass wrote (or would write on a dry run)."""

    applied: bool = False
    #: True when ``apply`` was asked for but the blast-radius bound refused it;
    #: nothing is written and the whole plan is reported and abandoned.
    refused: bool = False
    #: sha256 of the corpus database the pass read — the ledger of a
    #: latch-bypassing write names the blob it is re-derivable against.
    corpus_sha256: str = ""

    # --- Step 1: the corpus column ---
    #: Interim application dockets walked (``application_kind`` non-null,
    #: live-slice SCOTUS rows — the interim signal family's populated frame).
    eligible: int = 0
    #: Resolved applications with a readable disposition date and a snapshot
    #: disclosing entries — the rows the re-derivation can and does read.
    observable: int = 0
    #: Rows with no live-shaped snapshot, or one disclosing no entries — counted
    #: and left untouched, never lowered.
    unobservable: int = 0
    #: Rows with no readable disposition date (an open application, or a resolved
    #: one whose disposing entry carries no readable date): no end-of-day cut to
    #: apply, so they are left to the live channel and never written here.
    open_no_cut: int = 0
    #: Application-parsed rows carrying no stored amicus count — the coverage
    #: sentinel for the interim signal family; reported and left alone.
    no_stored_count: int = 0
    #: Observable rows whose re-derived count differs from the stored one.
    corpus_changed: int = 0
    corpus_increased: int = 0
    corpus_decreased: int = 0
    #: Total absolute movement in the count across changed rows — a magnitude
    #: beside the row count, the twin of ``arrival-cut-ledger``'s
    #: ``amicus_shift_entries``.
    amicus_shift_entries: int = 0
    corpus_changed_case_ids: list[str] = field(default_factory=list)

    # --- Step 2: the committed interim outcomes ---
    #: Committed ``outcome.json`` rows carrying a non-null ``interim_signals``
    #: block — the re-freeze population (the freeze-record worklist).
    outcomes_with_interim: int = 0
    #: The distribution of the frozen ``interim_signals.amicus_briefs`` values
    #: across that population, keyed by value — the shape the freeze-record entry
    #: pre-computed, so a reader can confirm the affected set matches it.
    interim_amicus_distribution: dict[int, int] = field(default_factory=dict)
    #: Committed interim outcomes whose ``amicus_briefs`` this pass re-freezes.
    outcomes_refrozen: int = 0
    #: Committed interim outcomes whose case the re-derivation could not resolve
    #: (not in the walked interim population, or unobservable/open) — reported
    #: and left exactly as frozen.
    outcomes_unresolvable: int = 0
    #: Distinct cases the re-freeze touches.
    cases_refrozen: int = 0
    refrozen: list[AmicusRefreeze] = field(default_factory=list)

    #: The standing invariant this pass upholds: a committed
    #: ``context.amicus_briefs`` (the prediction end, on ``prediction.json``) is
    #: never re-derived. Always true — no ``prediction.json`` is opened.
    context_amicus_untouched: bool = True

    @property
    def total_changes(self) -> int:
        """The blast radius the bound is read against: both writes summed."""
        return self.corpus_changed + self.outcomes_refrozen


def _rederive_amicus(payload: dict[str, Any]) -> int | None:
    """The re-derived amicus count for one live payload, or ``None``.

    ``None`` means the row is out of this pass's reach and must be left untouched:
    the payload discloses no entries, or the application has no readable
    disposition date (an open application, whose column the live channel
    maintains, or a resolved one whose disposing entry carries no readable date —
    the conservative direction the ingest derivation also takes). Otherwise the
    widened reading is applied with the end-of-day cut at the disposition date,
    exactly as :func:`fedcourtsai.pipeline.ingest` freezes the resolution value.
    """
    entries = cert_signals.proceedings_entries(payload)
    if not entries:
        return None
    through = interim_disposition_date(entries)
    if through is None:
        return None
    return amicus_briefs_through(entries, through)


def _rederive_column(
    conn: sqlite3.Connection, result: AmicusRederiveResult
) -> tuple[dict[str, int | None], list[tuple[str, int]]]:
    """Step 1: walk the interim application slice and plan the corpus rewrites.

    Fills the result's step-1 counters and returns the ``case_id -> re-derived
    count`` map (``None`` where the row is unobservable or open) and the corpus
    update set. The map is what step 2 reads, so the two writes share one
    derivation and a dry run's committed-side ledger is honest before the column
    is written.
    """
    # Materialized before any snapshot read, not walked beside it: `iter_rows` is
    # a lazily consumed cursor on `conn`, and stepping it while `latest_live_snapshot`
    # reads (from `conn` under the local backend) would put two readers on one
    # connection. The rows are metadata; the payloads are read one at a time below.
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
        if row.application_kind is not None
    ]
    result.eligible = len(rows)
    rederived: dict[str, int | None] = {}
    corpus_updates: list[tuple[str, int]] = []
    for row in rows:
        if row.amicus_briefs is None:
            # The interim signal family's coverage sentinel: a null count is what
            # makes a null flag read "never parsed" rather than "did not happen".
            # Filling it here would assert an observation the derivation never
            # made, so the row is reported and left alone.
            result.no_stored_count += 1
            continue
        found = corpus.latest_live_snapshot(conn, row.case_id)
        if found is None:
            result.unobservable += 1
            rederived[row.case_id] = None
            continue
        recount = _rederive_amicus(found[1])
        if recount is None:
            # A snapshot with no entries, or no readable disposition date: either
            # unobservable or an open application the live channel owns. The two
            # are counted apart so the ledger's denominators stay honest.
            if cert_signals.proceedings_entries(found[1]):
                result.open_no_cut += 1
            else:
                result.unobservable += 1
            rederived[row.case_id] = None
            continue
        result.observable += 1
        rederived[row.case_id] = recount
        stored = row.amicus_briefs
        if recount != stored:
            corpus_updates.append((row.case_id, recount))
            result.corpus_increased += int(recount > stored)
            result.corpus_decreased += int(recount < stored)
            result.amicus_shift_entries += abs(recount - stored)
    result.corpus_changed = len(corpus_updates)
    result.corpus_changed_case_ids = [case_id for case_id, _ in corpus_updates]
    return rederived, corpus_updates


def _plan_refreezes(
    data_root: Path, rederived: dict[str, int | None], result: AmicusRederiveResult
) -> list[tuple[Path, Outcome, int]]:
    """Step 2: plan the committed-outcome re-freezes against the re-derived map.

    Fills the result's step-2 counters (including the frozen-value distribution
    the freeze-record worklist is confirmed against) and returns the write plans,
    each rewriting only ``interim_signals.amicus_briefs``.
    """
    distribution: dict[int, int] = defaultdict(int)
    plans: list[tuple[Path, Outcome, int]] = []
    cases: set[str] = set()
    for path in sorted((data_root / "cases").glob("*/*/events/*/outcome.json")):
        outcome = read_model(path, Outcome)
        block = outcome.interim_signals
        if block is None:
            continue
        result.outcomes_with_interim += 1
        distribution[block.amicus_briefs] += 1
        recount = rederived.get(outcome.case_id)
        if outcome.case_id not in rederived or recount is None:
            # The case is outside the walked interim population, or its snapshot
            # could not be re-derived. The frozen block stays exactly as it is —
            # a re-freeze must rest on a reading, never on absence.
            result.outcomes_unresolvable += 1
            continue
        if recount != block.amicus_briefs:
            plans.append((path, outcome, recount))
            cases.add(outcome.case_id)
            result.refrozen.append(
                AmicusRefreeze(
                    ref=f"{outcome.case_id}/{outcome.event_id}",
                    was=block.amicus_briefs,
                    now=recount,
                )
            )
    result.interim_amicus_distribution = dict(sorted(distribution.items()))
    result.outcomes_refrozen = len(plans)
    result.cases_refrozen = len(cases)
    return plans


def rederive_amicus_briefs(
    conn: sqlite3.Connection,
    data_root: Path,
    *,
    apply: bool,
    corpus_sha256: str = "",
    max_changes: int | None = None,
) -> AmicusRederiveResult:
    """Re-derive the interim ``amicus_briefs`` column and re-freeze its committed outcomes.

    One pass **within an invocation**: the plan reported is exactly the write set,
    so a dry run and the apply inside one call cannot describe different work.
    Across two dispatches it is a reading, not a guarantee — the live channel
    resolves new applications between them — which is why the apply prints its own
    report as the record of what it did.

    Step 1 walks the interim application dockets in the live slice, recounts each
    resolved one's amicus briefs from its latest live-shaped snapshot under the
    widened reading with the end-of-day cut, and writes the changed rows through
    :func:`fedcourtsai.corpus.set_amicus_briefs` — a **direct ``UPDATE`` that
    bypasses the max latch** (see the module docstring for why). Step 2 re-reads
    every committed interim ``outcome.json`` and rewrites its
    ``interim_signals.amicus_briefs`` to the re-derived value the same recount
    produced, leaving the two flags in the block untouched. The re-freeze target
    is computed from the snapshot in **both** modes, so a dry run's ledger shows
    the true old→new for the committed blocks whether or not the column has been
    written yet.

    ``max_changes`` is the blast-radius bound over
    :attr:`AmicusRederiveResult.total_changes` (both writes summed), and lives
    here rather than in the caller so a code caller is bounded on the same terms
    as the command. Above it nothing is written and
    :attr:`AmicusRederiveResult.refused` comes back true. ``None`` is unbounded; a
    dry run never consults it, since it writes nothing.

    Idempotent: a second pass over an already-converged corpus recomputes the same
    counts, finds them stored and the committed blocks already equal, and writes
    nothing — the control this pass is verified by. A committed
    ``prediction.json`` is never opened;
    :attr:`AmicusRederiveResult.context_amicus_untouched` records that invariant.
    """
    result = AmicusRederiveResult(applied=apply, corpus_sha256=corpus_sha256)
    rederived, corpus_updates = _rederive_column(conn, result)
    refreeze_plans = _plan_refreezes(data_root, rederived, result)

    if not apply:
        return result
    if max_changes is not None and result.total_changes > max_changes:
        result.refused = True
        return result

    written = corpus.set_amicus_briefs(conn, corpus_updates)
    if written != len(corpus_updates):
        # The report is a claim about what the corpus now holds, so a write set
        # the statements did not land on is a report that lies — unreachable in
        # the writer lane's single transaction, which is the point: if it fires,
        # the plan and the store disagree about which rows exist.
        raise RuntimeError(
            f"planned {len(corpus_updates)} amicus-count rewrite(s) but the UPDATE "
            f"touched {written} row(s) — the plan and the corpus disagree"
        )
    for path, outcome, recount in refreeze_plans:
        assert outcome.interim_signals is not None  # only planned where non-null
        new_block = outcome.interim_signals.model_copy(update={"amicus_briefs": recount})
        write_json(path, outcome.model_copy(update={"interim_signals": new_block}))
    return result
