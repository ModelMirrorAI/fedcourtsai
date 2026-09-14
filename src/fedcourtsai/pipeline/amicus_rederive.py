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
so. Bypassing a guard obliges naming what it was for and what replaces it, and
saying how much of it is **not** replaced. The latch rejects any regression from
any cause. What replaces it here is narrower — a row with **no readable
disposition date** is skipped, and a row whose snapshot is missing or discloses
no entries is counted ``unobservable`` and left untouched, never lowered. So the
pass touches only a **resolved** application (a readable disposition date, hence
a fixed cut value ``live_rotation`` no longer re-polls) — exactly the rows whose
resolution value an ``outcome.json`` can freeze.

The skipped bucket holds two different rows, and only one of them has an owner:
an *open* application, which the live channel keeps polling under this same
widened reading, and a *resolved* one whose disposing entry carries no readable
date. The second is owned by nobody —
:func:`fedcourtsai.corpus.application_rotation` selects on a null disposition, so
it is never re-polled, and this pass declines it too. That row keeps whatever the
latch accumulated, which is the conservative direction and the same residual the
bounded derivation already carries.

That covers *total* payload loss and not *partial* degradation, which is the gap
the latch used to cover and this pass does not: a snapshot that still parses a
disposition entry but has lost earlier ones recounts low, and the direct
``UPDATE`` lands that — then :func:`_plan_refreezes` propagates it into a
committed ``outcome.json``. One accidental protection is worth stating rather
than relying on silently: the disposing entry is normally at the docket's tail,
so tail-first truncation takes it too and the row falls to ``open_no_cut`` and is
skipped. Head-first or selective loss is not covered. The replacement is
therefore **procedural**: every changed row is published in the ledger with its
old and new count (:attr:`AmicusRederiveResult.corpus_moves`), so an implausible
decrease is visible to the maintainer *before* the apply rather than discoverable
only afterwards.

**A move is not by itself the reading's doing.** The recount runs over the
docket's *current* snapshot, so an entry dated at or before the disposition that
the poll had not yet seen when the resolution was detected raises the re-derived
count legitimately under the cut — for a reason that is late docket-data arrival
rather than the widening. Both reach the ledger as one ``was -> now``, and
nothing here can separate them. For a scored claim's resolution end that is the
difference between a hit and measurement drift, so each flip owes the same check
the freeze record performs by hand: the moving entry's date against the affected
cells' own anchor. A flip whose entry predates the anchor is the measurement
widening, and its increment is not claimable as a forecast hit.

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
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .. import corpus
from ..schemas import InterimResolutionSignals, Outcome
from ..serialize import read_model, write_json
from . import cert_signals
from .interim_signals import amicus_briefs_through, interim_disposition_date
from .prefetch import prefetch_by_case


class AmicusRefreeze(BaseModel):
    """One committed interim outcome whose ``interim_signals.amicus_briefs`` moves."""

    model_config = ConfigDict(extra="forbid")

    ref: str = Field(description='"<case_id>/<event_id>"')
    was: int = Field(
        ge=0, description="The frozen count the outcome carried, under the old reading"
    )
    now: int = Field(
        ge=0, description="The re-derived count under the widened reading and the end-of-day cut"
    )
    regrade_cells: list[str] = Field(
        default_factory=list,
        description="The committed evaluator cells this re-freeze puts in the re-grade "
        "backlog, in the `court/docket/event/run_id/actor` grammar `run-repair`'s "
        "`regrade-stale` selector parses — one per distinct (evaluator, run) pair under "
        "the event, so the debt can be dispatched off the ledger rather than reconstructed",
    )


class AmicusCorpusMove(BaseModel):
    """One corpus row whose stored ``amicus_briefs`` the re-derivation moves."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    was: int = Field(ge=0, description="The stored count, under the reading that wrote it")
    now: int = Field(
        ge=0, description="The re-derived count under the widened reading and the end-of-day cut"
    )


class AmicusRederiveResult(BaseModel):
    """What one re-derive-and-re-freeze pass wrote (or would write on a dry run).

    A model rather than a plain record so the command can serialize it whole:
    the workflow tees this into the run summary as the ledger a maintainer reads
    before approving the apply, and a field added here that a hand-built payload
    forgot would be silently missing from the one artifact that outlives the run.
    """

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(
        default=False, description="Whether the pass ran in apply mode (False = dry-run)"
    )
    refused: bool = Field(
        default=False,
        description="Whether the blast-radius bound stopped the apply — nothing was written",
    )
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the pass read — the ledger of a "
        "latch-bypassing write names the blob it is re-derivable against",
    )

    # --- Step 1: the corpus column ---
    eligible: int = Field(
        default=0,
        ge=0,
        description="Interim application dockets walked (`application_kind` non-null, "
        "live-slice SCOTUS rows — the interim signal family's populated frame)",
    )
    observable: int = Field(
        default=0,
        ge=0,
        description="Resolved applications with a readable disposition date and a "
        "snapshot disclosing entries — the rows the re-derivation can and does read",
    )
    unobservable: int = Field(
        default=0,
        ge=0,
        description="Rows with no live-shaped snapshot, or one disclosing no entries — "
        "counted and left untouched, never lowered. Read this FIRST: against an "
        "index-only pull every row lands here and the empty ledger is a wrong-blob "
        "reading rather than a converged corpus",
    )
    open_no_cut: int = Field(
        default=0,
        ge=0,
        description="Rows with no readable disposition date, so there is no end-of-day "
        "cut to apply and nothing is written. Two arms: an OPEN application, which the "
        "live channel keeps polling under this same reading, and a RESOLVED one whose "
        "disposing entry carries no readable date — which the application rotation no "
        "longer selects, so no channel revisits it either",
    )
    no_stored_count: int = Field(
        default=0,
        ge=0,
        description="Application-parsed rows carrying no stored amicus count — the "
        "coverage sentinel for the interim signal family; reported and left alone",
    )
    corpus_changed: int = Field(
        default=0,
        ge=0,
        description="Observable rows whose re-derived count differs from the stored one",
    )
    corpus_increased: int = Field(default=0, ge=0)
    corpus_decreased: int = Field(default=0, ge=0)
    amicus_shift_entries: int = Field(
        default=0,
        ge=0,
        description="Total absolute movement in the count across changed rows — a "
        "magnitude beside the row count, the twin of `arrival-cut-ledger`'s reading",
    )
    corpus_moves: list[AmicusCorpusMove] = Field(
        default_factory=list,
        description="Every changed corpus row with its old and new count, complete "
        "rather than sampled, in `case_id` order — the per-row half of the ledger, and "
        "the procedural replacement for the max latch this write bypasses: an "
        "implausible decrease is visible here before the apply",
    )
    corpus_changed_case_ids: list[str] = Field(default_factory=list)

    # --- Step 2: the committed interim outcomes ---
    outcomes_with_interim: int = Field(
        default=0,
        ge=0,
        description="Committed `outcome.json` rows carrying a non-null `interim_signals` "
        "block — the re-freeze population (the freeze-record worklist)",
    )
    interim_amicus_distribution: dict[int, int] = Field(
        default_factory=dict,
        description="The distribution of the frozen `interim_signals.amicus_briefs` "
        "values across that population, keyed by value — the shape the freeze-record "
        "entry pre-computes, so a reader can confirm the affected set matches it. "
        "Reported as FOUND, before this pass's own writes, in both modes",
    )
    outcomes_refrozen: int = Field(
        default=0,
        ge=0,
        description="Committed interim outcomes whose `amicus_briefs` this pass re-freezes",
    )
    outcomes_unresolvable: int = Field(
        default=0,
        ge=0,
        description="Committed interim outcomes whose case the re-derivation could not "
        "resolve (not in the walked interim population, or unobservable/open) — "
        "reported and left exactly as frozen",
    )
    cases_refrozen: int = Field(default=0, ge=0, description="Distinct cases the re-freeze touches")
    refrozen: list[AmicusRefreeze] = Field(default_factory=list)

    context_amicus_untouched: bool = Field(
        default=True,
        description="The standing invariant this pass upholds: a committed "
        "`context.amicus_briefs` (the prediction end, on `prediction.json`) is never "
        "re-derived. True BY CONSTRUCTION — no `prediction.json` is opened — rather "
        "than as an observation this pass made",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="The blast radius the bound is read against: both writes summed"
    )
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
    # a lazily consumed cursor on `conn`, and stepping it while the prefetch's
    # workers read would put two readers on one connection. The rows are
    # metadata; the payloads stay in the prefetch's streamed window.
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
        if row.application_kind is not None
    ]
    result.eligible = len(rows)
    rederived: dict[str, int | None] = {}
    corpus_updates: list[tuple[str, int]] = []
    # The reads ride the shared bounded prefetch, as the distribution
    # re-derivation's do: under the corpus-split mode `latest_live_snapshot`
    # serves each payload from the per-case content store, so a serial walk would
    # pay one GET latency per eligible row inside the step's cap.
    # `latest_live_snapshot` never touches `conn` where payload reads are
    # offloaded, which is what makes handing the call to the pool's workers
    # sound; the loop body runs on the calling thread either way, so pooled and
    # serial passes classify identically.
    with prefetch_by_case(
        [row.case_id for row in rows],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="amicus-rederive",
    ) as fetched:
        for row, (_, found) in zip(rows, fetched, strict=True):
            if row.amicus_briefs is None:
                # The interim signal family's coverage sentinel: a null count is
                # what makes a null flag read "never parsed" rather than "did not
                # happen". Filling it here would assert an observation the
                # derivation never made, so the row is reported and left alone.
                result.no_stored_count += 1
                continue
            if found is None:
                result.unobservable += 1
                rederived[row.case_id] = None
                continue
            recount = _rederive_amicus(found[1])
            if recount is None:
                # A snapshot with no entries, or no readable disposition date.
                # The two are counted apart so the denominators stay honest, and
                # the second bucket holds two different rows: an open application
                # the live channel keeps polling, and a resolved one whose
                # disposing entry carries no readable date — which the
                # application rotation no longer selects, so nothing revisits it.
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
                result.corpus_moves.append(
                    AmicusCorpusMove(case_id=row.case_id, was=stored, now=recount)
                )
                result.corpus_increased += int(recount > stored)
                result.corpus_decreased += int(recount < stored)
                result.amicus_shift_entries += abs(recount - stored)
    result.corpus_changed = len(corpus_updates)
    result.corpus_changed_case_ids = [case_id for case_id, _ in corpus_updates]
    return rederived, corpus_updates


def _regrade_cells(event_dir: Path, case_id: str, event_id: str) -> list[str]:
    """The committed evaluator cells one re-freeze puts in the re-grade backlog.

    Emitted in the ``court/docket/event/run_id/actor`` grammar ``run-repair``'s
    ``regrade-stale`` selector parses, so the debt this pass owes can be
    dispatched straight off the ledger rather than reconstructed by hand from a
    directory walk. Keyed on the distinct ``(evaluator, run)`` pairs under
    ``evaluations/<evaluator>/<predictor>/<run_id>/`` — a re-grade recomputes an
    evaluator cell, and several predictors' evaluations share one such cell, so
    the per-predictor directories collapse to one line each.

    Directory presence is enough, as it is for the sibling relabel's count: an
    empty leftover still means a cell was provisioned there, and erring toward
    naming a re-grade that is not owed is cheaper than missing one that is.
    """
    court, _, docket = case_id.partition("/")
    root = event_dir / "evaluations"
    if not root.is_dir():
        return []
    cells = {
        f"{court}/{docket}/{event_id}/{run_dir.name}/{evaluator_dir.name}"
        for evaluator_dir in root.iterdir()
        if evaluator_dir.is_dir()
        for predictor_dir in evaluator_dir.iterdir()
        if predictor_dir.is_dir()
        for run_dir in predictor_dir.iterdir()
        if run_dir.is_dir()
    }
    return sorted(cells)


def _plan_refreezes(
    data_root: Path, rederived: dict[str, int | None], result: AmicusRederiveResult
) -> list[tuple[Path, Outcome, InterimResolutionSignals]]:
    """Step 2: plan the committed-outcome re-freezes against the re-derived map.

    Fills the result's step-2 counters (including the frozen-value distribution
    the freeze-record worklist is confirmed against) and returns the write plans.
    Each plan carries the **already-built** replacement block rather than a bare
    count, so the write site copies it in without re-deriving anything — the
    field the pass may move is decided in exactly one place.
    """
    distribution: dict[int, int] = defaultdict(int)
    plans: list[tuple[Path, Outcome, InterimResolutionSignals]] = []
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
            # Only `amicus_briefs` moves; the two flags the widened reading does
            # not touch are carried through by the copy.
            plans.append((path, outcome, block.model_copy(update={"amicus_briefs": recount})))
            cases.add(outcome.case_id)
            result.refrozen.append(
                AmicusRefreeze(
                    ref=f"{outcome.case_id}/{outcome.event_id}",
                    was=block.amicus_briefs,
                    now=recount,
                    regrade_cells=_regrade_cells(path.parent, outcome.case_id, outcome.event_id),
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
        #
        # The index write has already COMMITTED when this raises, so the two
        # stores are momentarily out of step — the corpus moved and no outcome
        # did. That is safe where it matters, and only there: in the writer lane
        # the step runs under `set -euo pipefail`, so the raise stops the job
        # before `corpus-push` and before anything is staged, and the mutated
        # blob goes to the scrapheap with the runner rather than into a commit.
        # A code caller holding its own connection owns the rollback.
        raise RuntimeError(
            f"planned {len(corpus_updates)} amicus-count rewrite(s) but the UPDATE "
            f"touched {written} row(s) — the plan and the corpus disagree"
        )
    for path, outcome, new_block in refreeze_plans:
        write_json(path, outcome.model_copy(update={"interim_signals": new_block}))
    return result
