"""Salience-gate replay: the frozen gate run over past Terms at reconstructed moments.

The cert back-test (:mod:`fedcourtsai.cert_backtest`) replays *predictors*;
this replays the **gate** — the deterministic ``sal-v1`` scoring, banding, and
per-conference selection that decides which petitions the tournament funds at
all. For each named Term it projects every resolved paid modern-cert petition
to the state its docket disclosed at a policy-chosen moment
(:class:`fedcourtsai.pipeline.asof.CutoffPolicy` — arrival, first
distribution, resolution-adjacent), reproduces the as-of conference cohorts,
and runs the same selection core the live pass runs
(:func:`fedcourtsai.pipeline.salience.plan_cohorts`). The report says what the
gate *would have* selected then, and scores that selection against the
realized grant-family outcomes with sample-weighted precision and recall.

Two structural facts the numbers document:

- **At arrival the gate is degenerate.** Every signal ``sal-v1`` turns on is
  docket-acquired (relists, CVSG), so a petition projected to its arrival sits
  in the baseline band with no conference cohort — nothing is selected, and
  precision is undefined rather than zero.
- **The population frame for a full predict/evaluate backtest.** A later run
  that replays predictors over a past Term inherits this module's population,
  cutoffs, and provenance accounting, so its band mix is stated rather than
  discovered.

Reconstruction reuses the cert back-test's leakage machinery — redaction,
date-keyed truncation, the dated-snapshot preference, and the fail-closed
disposition scan — so the two replays cannot disagree about what a
point-in-time docket is. Read-only over the corpus; it writes nothing but the
report its caller lands under ``metrics/``.
"""

from __future__ import annotations

import sqlite3
from collections import Counter
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Literal

from . import corpus
from .analytics import _is_scored_segment_row
from .cert_backtest import _kept_entries_show_a_disposition, redact_snapshot, truncate_snapshot
from .config import SalienceConfig
from .pipeline import asof
from .pipeline.outcome import granted_flag, is_machine_readable
from .pipeline.salience import (
    SALIENCE_VERSION,
    _capacity,
    carve_out,
    plan_cohorts,
    salience_band,
)
from .schemas import Disposition, SalienceReplay, SalienceReplayCell


def select_replay_population(
    conn: sqlite3.Connection, *, terms: Sequence[int]
) -> list[corpus.CorpusRow]:
    """The named Terms' resolved petitions the gate replay runs over, ``case_id``-ordered.

    The cert back-test's eligibility bar — a resolved SCOTUS modern
    discretionary-cert docket with a machine-readable disposition and
    internally consistent dates — narrowed to the **live slice** (rows whose
    signals come from parsed proceedings, so a snapshot exists to reconstruct
    from) and scope-filtered by **time-invariant predicates only**: the paid
    fee class is fixed at filing (the IFP serial stream), so applying it
    reconstructs the Tier-0 population without leaking any post-arrival state
    into the frame. Predicates that read the docket's later life (a
    bare-import profile, a below-cap latch) are deliberately not applied —
    they are the gate's own subject matter, not its population.
    """
    wanted = set(terms)
    return [
        row
        for row in corpus.iter_rows(conn, court="scotus", resolved=True)
        if row.disposition is not None
        and is_machine_readable(Disposition(row.disposition))
        and corpus.is_modern_cert(row)
        and not corpus.is_date_inconsistent(row)
        and corpus.is_live_slice(row)
        and corpus.scotus_term_year(row.docket_number) in wanted
        and _is_scored_segment_row(row)
    ]


def _project(
    conn: sqlite3.Connection, row: corpus.CorpusRow, policy: asof.CutoffPolicy
) -> tuple[asof.AsOfRow, str] | None:
    """Project one petition to the policy's moment, or ``None`` with no snapshot.

    The cert back-test's provisioning ladder, applied to a row instead of a
    cell: redact the latest payload, find the policy cutoff, prefer a snapshot
    the docket really served before it (``dated``) over truncating the later
    payload (``truncated``), and fail closed to blind — proceedings removed
    outright — when no cutoff exists or a disposition survives truncation. The
    returned label is the report's provenance-mix key: the two blind causes are
    told apart (``blind-no-moment`` — the live gate would also never have
    cohorted this petition — vs ``blind-untrusted-cutoff`` — a distributed,
    cohortable petition whose reconstruction could not be trusted), because
    they read very differently under recall.
    """
    found = corpus.latest_snapshot(conn, row.case_id)
    if found is None:
        return None
    working = redact_snapshot(found[1])
    cutoff = asof.policy_cutoff(policy, row, working)
    provenance: Literal["dated", "truncated", "blind"] = (
        "truncated" if cutoff is not None else "blind"
    )
    label: str = provenance if cutoff is not None else "blind-no-moment"
    if cutoff is not None:
        dated = corpus.snapshot_at(conn, row.case_id, before=cutoff)
        if dated is not None:
            working = redact_snapshot(dated[1])
            provenance = label = "dated"
    # Truncation runs on the dated payload too: a no-op when the stored snapshot
    # really predates the cutoff, an alarm when it does not.
    working, _ = truncate_snapshot(working, cutoff)
    # Fail closed on the cutoff rule's premise, exactly as the cell replay does:
    # a disposition surviving the cutoff means the moment cannot be trusted.
    if cutoff is not None and _kept_entries_show_a_disposition(working):
        working, _ = truncate_snapshot(working, None)
        provenance = "blind"
        label = "blind-untrusted-cutoff"
        cutoff = None
    projected = asof.project_row(row, working, cutoff=cutoff, provenance=provenance)
    if cutoff is not None:
        # The as-of conference, so cohorting reproduces the latest-entry-wins
        # value the live channel would have held at that moment.
        projected.row.distributed_for_conference = asof.asof_conference(working, cutoff)
    return projected, label


def _replay_cell(
    conn: sqlite3.Connection,
    term: int,
    policy: asof.CutoffPolicy,
    rows: list[corpus.CorpusRow],
    config: SalienceConfig,
) -> SalienceReplayCell:
    """One (Term, policy) cell: project, run the selection core, score the pick."""
    projected: list[tuple[corpus.CorpusRow, asof.AsOfRow]] = []
    provenance_mix: Counter[str] = Counter()
    skipped = 0
    for row in rows:
        found = _project(conn, row, policy)
        if found is None:
            skipped += 1
            continue
        projection, label = found
        provenance_mix[label] += 1
        projected.append((row, projection))

    synthesized = [projection.row for _, projection in projected]
    scores, to_select, _, conferences = plan_cohorts(synthesized, config)
    selected = set(to_select)  # no projected row is pre-latched, so this is the whole pick
    carved = {
        row.case_id
        for row in synthesized
        if row.case_id in selected and carve_out(row, scores[row.case_id], config.floor)
    }

    cohort_members: dict[date, list[corpus.CorpusRow]] = {}
    for row in synthesized:
        if row.distributed_for_conference is not None:
            cohort_members.setdefault(row.distributed_for_conference, []).append(row)
    capacity_bound = sum(
        1
        for conference, members in cohort_members.items()
        if sum(
            1 for member in members if not carve_out(member, scores[member.case_id], config.floor)
        )
        > _capacity(conference, config)
    )
    # The rank fill is a functional of the realized sample's cohort, so under
    # legacy denial weights (a thinned cohort) it is not reweightable into a
    # population estimate. This figure is the reader's check: the largest
    # cohort's weighted non-carve-out mass against the capacity says whether
    # the real cohort could have been cut where the sample was not.
    largest_weighted_cohort = max(
        (
            sum(
                float(member.sample_weight or 1)
                for member in members
                if not carve_out(member, scores[member.case_id], config.floor)
            )
            for members in cohort_members.values()
        ),
        default=0.0,
    )

    bands: Counter[str] = Counter()
    for _, projection in projected:
        bands[salience_band(projection.row) if projection.observable else "unobservable"] += 1

    raw_selected_granted = raw_granted = 0
    weighted_selected = weighted_selected_granted = weighted_granted = weighted_population = 0.0
    for real, _ in projected:
        weight = float(real.sample_weight or 1)
        granted = granted_flag(Disposition(str(real.disposition))) == 1
        weighted_population += weight
        if granted:
            raw_granted += 1
            weighted_granted += weight
        if real.case_id in selected:
            weighted_selected += weight
            if granted:
                raw_selected_granted += 1
                weighted_selected_granted += weight

    return SalienceReplayCell(
        term=term,
        policy=str(policy),
        eligible=len(rows),
        skipped_no_snapshot=skipped,
        cohorts=conferences,
        selected=len(selected),
        selected_carve_out=len(carved),
        selected_rank_fill=len(selected) - len(carved),
        capacity_bound_cohorts=capacity_bound,
        largest_weighted_cohort=largest_weighted_cohort,
        bands=dict(bands),
        provenance=dict(provenance_mix),
        selected_granted=raw_selected_granted,
        realized_granted=raw_granted,
        weighted_selected=weighted_selected,
        weighted_selected_granted=weighted_selected_granted,
        weighted_granted=weighted_granted,
        weighted_population=weighted_population,
        precision=(weighted_selected_granted / weighted_selected) if weighted_selected else None,
        recall=(weighted_selected_granted / weighted_granted) if weighted_granted else None,
    )


def replay_gate(
    corpus_db_path: Path,
    *,
    terms: Sequence[int],
    policies: Sequence[asof.CutoffPolicy],
    config: SalienceConfig,
) -> SalienceReplay:
    """Replay the gate over each (Term, policy) cell into a :class:`SalienceReplay`.

    Deterministic and read-only: the population is ``case_id``-ordered, every
    projection is a pure function of stored payloads, and the selection core is
    the live pass's own (:func:`~fedcourtsai.pipeline.salience.plan_cohorts`),
    so two runs over the same corpus produce the same report. A Term with no
    eligible petitions still yields its cells (zero counts), so an empty Term
    is visible rather than silently absent.
    """
    cells: list[SalienceReplayCell] = []
    with corpus.connect(corpus_db_path) as conn:
        by_term: dict[int, list[corpus.CorpusRow]] = {}
        for row in select_replay_population(conn, terms=terms):
            term = corpus.scotus_term_year(row.docket_number)
            if term is not None:  # guaranteed by is_modern_cert; guards the type
                by_term.setdefault(term, []).append(row)
        for term in terms:
            for policy in policies:
                cells.append(_replay_cell(conn, term, policy, by_term.get(term, []), config))
    return SalienceReplay(
        salience_version=SALIENCE_VERSION,
        terms=list(terms),
        policies=[str(policy) for policy in policies],
        cells_evaluated=len(cells),
        cells=cells,
    )
