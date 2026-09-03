"""Converge a denied petition's ``date_decided`` onto its own cert-denial date.

The order refusing the writ is the order that ends the docket, so on a denied
SCOTUS petition the petition-stage decision and the docket's termination are
ordinarily the same moment — ``date_cert_denied``'s contract on
:class:`fedcourtsai.corpus.CorpusRow` says so, and hedges it, because a
rehearing round can re-terminate a denied docket later. The hedge does not
weaken the fill, because of what the fill writes: the date the row already
carries as its resolution
(:func:`fedcourtsai.corpus.resolution_date` returns exactly this value for a
denied row), so the converged ``date_decided`` can never disagree with the date
every seam in the pipeline already reads off the row. The live channel's
resolution parse carries that date across
(:func:`fedcourtsai.pipeline.ingest._live_resolution`), so every fresh denial
lands with both columns set; this sweep converges the rows written before that
default reached them, which is a fill-in of a date the row already holds rather
than a derivation of one it does not.

**The grant side is out of population, and that is the honest boundary.** A
granted docket terminates at its merits judgment — months after the grant, and a
date no column on the row carries — so stamping ``date_cert_granted`` there
would invent the termination rather than converge it. A GVR sits on the grant
side of the same split. Both keep their null ``date_decided``, which is also the
shape :mod:`fedcourtsai.pipeline.outcome` reads as a retained grant.

**Why a standing sweep and not a repair pass.** It is idempotent (a converged
row leaves the population), needs no maintainer triage before it writes, and
converges toward exactly the state the ingest default reaches on its own —
the three properties that put a pass on the walker rather than on the repair
bench (*Maintenance passes* in ``docs/data-pipeline.md``). The pairing is also
what makes it converge at all: ``date_decided`` is a last-write-wins column
(:func:`fedcourtsai.corpus._update_clause`), so a sweep without the ingest
default behind it would be undone by the next walk of the Term.

**Why no writer can put a converged row back in the population.** The live
channel re-derives the same date, so its re-serve is a no-op. A CourtListener
REST payload carries no cert-stage date fields at all — the projection reads
``date_cert_denied`` off the record (:func:`fedcourtsai.pipeline.ingest._normalize`)
and finds nothing there — so a REST re-serve of one of these rows writes nulls
across the whole trio: ``date_decided``, ``date_cert_denied``, and the
disposition the cert dates derived. The population predicate requires the denial
date *and* the denied disposition, so such a row leaves the population rather
than re-entering it, and the flap shape — a writer that keeps the disposition
and the denial date while blanking the termination — is exactly the live path
the ingest default closes.

**Two date guards, and both decline rather than propagate.** A denial dated
before its own filing, or after the as-of day, is not written: the first is an
upstream disagreement this sweep would only spread into a second column, and the
second is the one shape ``validate.check_case_dates`` fails on with no baseline
to absorb it. Both are stated on
:data:`fedcourtsai.corpus.DENIAL_TERMINATION_GAP_SQL`, which is where the plan
and the write both read them.

**One visible interaction.** :mod:`fedcourtsai.dedupe` compares ``date_filed``,
``date_decided`` and ``disposition`` before it drops a duplicate twin, treating
a null as agreement. Filling the column can therefore turn a pair whose denial
dates already disagree into a reported conflict instead of a silent merge —
which is the conservative direction: the disagreement was always there, and the
dedupe reports such a pair rather than dropping it.

**One measured surface moves.** The statpack's pack-level filing→decision timing
(:func:`fedcourtsai.analytics._decision_days`) keys on ``date_decided``, so the
denial population enters a headline it was absent from. The rendered line
carries the scope note that says what the number is over; the per-Term timing,
keyed on the cert-stage resolution date, does not move at all.
"""

from __future__ import annotations

import sqlite3
from datetime import date

from .. import corpus
from ..schemas import DecisionDateConvergenceResult

#: Bounded sample of the planned write set, for the run summary the lane tees.
#: The **lexicographically first** ids, not a spread: it is a spot check that
#: the population looks like what the predicate describes, not a triage list —
#: the write is a copy within one row, so there is nothing per-row to triage.
_MAX_SAMPLE = 20


def converge_decision_dates(
    conn: sqlite3.Connection, *, apply: bool, today: date | None = None
) -> DecisionDateConvergenceResult:
    """Fill ``date_decided`` from ``date_cert_denied`` on every denied petition missing it.

    Dry run by default (plans the write set, writes nothing); ``apply`` performs
    the write. The plan and the write share one predicate
    (:data:`fedcourtsai.corpus.DENIAL_TERMINATION_GAP_SQL`), so the count read
    off a dry run is the count an apply touches. Idempotent — a second run with
    no corpus change reports zero.

    ``today`` anchors the future-date guard; ``None`` reads the wall clock, which
    is what a scheduled window means by now, and tests pass a fixed date.
    """
    as_of = today if today is not None else date.today()
    case_ids = corpus.denial_termination_gap_case_ids(conn, today=as_of)
    converged = corpus.converge_denial_termination_dates(conn, today=as_of) if apply else 0
    return DecisionDateConvergenceResult(
        applied=apply,
        candidates=len(case_ids),
        converged=converged,
        sample=case_ids[:_MAX_SAMPLE],
    )
