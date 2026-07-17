"""The salience gate: deterministic scoring and per-conference selection.

The write pass behind salience-ordered prediction scope (see ``docs/salience.md``).
It scores every in-scope SCOTUS cert petition with the **frozen** ``sal-v1``
function and latches ``salience_selected`` on the fundable slice: each conference
cohort's top-``N`` by score, plus the always-include carve-outs (CVSG petitions
and anything at/above the salience floor), which sit *above* ``N``.

Two invariants make the pass safe to re-run over a live conference:

- **Sticky selection.** ``salience_selected`` is a one-way latch
  (:func:`fedcourtsai.corpus.latch_salience_selected` only ever sets it), so a
  petition selected early keeps its committed forward prediction even if fresher
  petitions later out-rank it. The pass never de-selects; the realized selected
  count may drift above ``N``.
- **Per-conference cohorts.** The cap is applied within each
  ``distributed_for_conference`` cohort, so "why this case and not that one"
  replays against one conference's candidate pool at a fixed score version. A
  petition not yet distributed for conference is scored but not selected — it is
  not up for prediction yet.

The score is recomputed every run (a pure function of the row's current features);
only the selection latch persists. This module owns no destructive behavior — it
writes only the ``salience_*`` columns; the read-time enforcement that consumes the
latch lives elsewhere.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import date

from .. import corpus
from ..config import SalienceConfig
from ..schemas import SalienceSelectionResult

# The frozen salience-function version. A refit is a NEW version, never an
# in-place edit, so any past ranking replays against the function that produced it.
SALIENCE_VERSION = "sal-v1"

# sal-v1 builds a ranking score from empirical grant rates. Every constant below
# is a real SCOTUS cert grant rate from ``metrics/statpack.md`` (denial-reweighted),
# so the ranking is interpretable and grounded in reality rather than invented
# weights. The primary signal is the stronger of the petition's *own-trajectory*
# grant rates — relist bucket and CVSG — and the originating circuit rides only as
# a small nudge (a circuit's marginal already reflects its relist mix, so treating
# it as a co-equal signal would double-count and inflate every petition from a
# high-grant circuit). The joint/compounding cut is deferred to sal-v2. Frozen for
# sal-v1: a refit is a new version.
_RELIST_GRANT_RATE: dict[int, float] = {0: 0.008, 1: 0.078}
_RELIST_HIGH_RATE = 0.394  # 2+ relists (the relist-3+ empirical dip is small-sample noise)
_RELIST_UNKNOWN_RATE = 0.024  # never live-parsed: a conservative sub-relist-1 sentinel
# (the most recent Term's overall grant rate, statpack Term table), so an unscanned
# petition ranks below any known relist count rather than being assumed distributed.
_CVSG_GRANT_RATE = 0.283
# How much the originating circuit's grant rate nudges the score — a bounded
# secondary tie-breaker (at most ~0.046 for cadc), never enough to lift a
# low-relist petition over the always-include floor on its own.
_CIRCUIT_WEIGHT = 0.1
_CIRCUIT_GRANT_RATE: dict[str, float] = {
    "ca1": 0.065,
    "ca2": 0.228,
    "ca3": 0.160,
    "ca4": 0.254,
    "ca5": 0.257,
    "ca6": 0.155,
    "ca7": 0.102,
    "ca8": 0.186,
    "ca9": 0.168,
    "ca10": 0.245,
    "ca11": 0.229,
    "cadc": 0.457,
    "cafc": 0.200,
}
_CIRCUIT_DEFAULT_RATE = 0.05  # state courts / unlinked petitions: grant rarely in the sample

# Bounded per-direction sample of selected case ids, for the run log / PR note.
_MAX_SAMPLE = 20

# The Term's opening "long conference" sits in late September; every other
# conference runs during the Term (October-June). The Court holds no *regular*
# September conference, so keying the larger cap on the month cleanly identifies
# the long conference without a separate calendar. Used only to pick the capacity.
_LONG_CONFERENCE_MONTH = 9


def _relist_signal(row: corpus.CorpusRow) -> float:
    """The relist bucket's empirical grant rate; the parse-coverage sentinel is NULL."""
    if row.distribution_count is None:
        return _RELIST_UNKNOWN_RATE
    relists = max(0, row.distribution_count - 1)
    if relists >= 2:
        return _RELIST_HIGH_RATE
    return _RELIST_GRANT_RATE[relists]


def salience_score(row: corpus.CorpusRow) -> float:
    """The frozen ``sal-v1`` ranking score, built from empirical grant rates.

    The primary signal is the stronger of the petition's own-trajectory grant
    rates — relist bucket and (if present) CVSG — nudged by a small fraction of its
    originating circuit's grant rate. Monotone in each feature. Fee class does not
    enter: IFP petitions will be excluded at Tier 0 (a separate change adds the
    ``OUT_OF_SCOPE_RULES`` predicate), leaving the scored set paid-only (see
    ``docs/salience.md``). A pure function of the row's features, so a rescoring
    reproduces the same value.
    """
    primary = _relist_signal(row)
    if row.cvsg_date is not None:
        primary = max(primary, _CVSG_GRANT_RATE)
    circuit = _CIRCUIT_GRANT_RATE.get(row.originating_court or "", _CIRCUIT_DEFAULT_RATE)
    return primary + _CIRCUIT_WEIGHT * circuit


# Frozen sal-v1 salience bands: score cutpoints that collapse the scored petitions
# into three interpretable grant-likelihood segments. The cutpoints sit in the gaps
# *between* the relist/CVSG grant-rate tiers, so the band tracks a petition's primary
# trajectory signal and the bounded circuit nudge never carries a petition across a
# boundary — a band is, in effect, "which relist/CVSG tier is this petition in". The
# band (not the raw score) is what the statpack conditions its per-Term base rate on,
# so a case's baseline is its own tier's historical grant rate — a relisted petition
# is not scored against the whole-docket rate. Frozen with sal-v1: a rescore
# reproduces the band, and a refit is a new version. Ordered strongest-first.
_SALIENCE_BANDS: tuple[tuple[str, float], ...] = (
    ("high", 0.20),  # CVSG (0.283) or 2+ relists (0.394) — the always-include tier
    ("elevated", 0.075),  # one relist (0.078)
    ("baseline", 0.0),  # relist-0 (0.008) or never-scanned (0.024)
)


def salience_band(row: corpus.CorpusRow) -> str:
    """The frozen ``sal-v1`` salience band of a row (see :data:`_SALIENCE_BANDS`).

    A pure function of :func:`salience_score`, so it inherits the scorer's
    determinism: the same row features reproduce the same band.
    """
    score = salience_score(row)
    for band, lower in _SALIENCE_BANDS:
        if score >= lower:
            return band
    return _SALIENCE_BANDS[-1][0]  # unreachable (the baseline cutpoint is 0.0); a guard


def salience_bands() -> tuple[str, ...]:
    """The band names strongest→weakest — the fixed segment order the statpack emits."""
    return tuple(band for band, _ in _SALIENCE_BANDS)


def _capacity(conference: date, config: SalienceConfig) -> int:
    """The per-cohort ``N``: a larger cap for the Term's opening long conference."""
    if conference.month == _LONG_CONFERENCE_MONTH:
        return config.long_conference_capacity
    return config.per_conference_capacity


def _select_cohort(
    rows: list[corpus.CorpusRow], scores: dict[str, float], capacity: int, floor: float
) -> set[str]:
    """The case ids to hold selected in one conference cohort.

    Carve-outs (CVSG petitions and anything at/above the floor) are selected
    unconditionally and sit *above* the ``N`` budget; the remainder is ranked by
    score (descending, case_id tie-break) and fills to ``N``.
    """
    selected = {
        row.case_id for row in rows if row.cvsg_date is not None or scores[row.case_id] >= floor
    }
    remainder = sorted(
        (row for row in rows if row.case_id not in selected),
        key=lambda row: (-scores[row.case_id], row.case_id),
    )
    selected.update(row.case_id for row in remainder[: max(0, capacity)])
    return selected


def _selection_plan(
    conn: sqlite3.Connection, config: SalienceConfig
) -> tuple[dict[str, float], list[str], int, int]:
    """Score the in-scope cert petitions and pick each cohort's selected slice.

    The pure planning half of the pass: returns ``(scores, to_select, eligible,
    conferences)`` where ``to_select`` holds only the **not-yet-latched** picks
    (the sticky latch is additive; the plan never de-selects).
    """
    scores: dict[str, float] = {}
    cohorts: dict[date, list[corpus.CorpusRow]] = defaultdict(list)
    already_selected: set[str] = set()
    eligible = 0
    for row in corpus.iter_rows(conn, court="scotus"):
        if corpus.out_of_scope_reason_full(conn, row) is not None:
            continue  # Tier-0 excluded (incl. IFP): not scored, not selected
        eligible += 1
        scores[row.case_id] = salience_score(row)
        if row.salience_selected:
            already_selected.add(row.case_id)
        if row.distributed_for_conference is not None:
            cohorts[row.distributed_for_conference].append(row)

    to_select: list[str] = []
    for conference, rows in cohorts.items():
        selected = _select_cohort(rows, scores, _capacity(conference, config), config.floor)
        # Sticky + additive: latch only the not-yet-selected; never de-select.
        to_select.extend(case_id for case_id in selected if case_id not in already_selected)
    return scores, to_select, eligible, len(cohorts)


def apply_salience_selection(conn: sqlite3.Connection, config: SalienceConfig) -> list[str]:
    """The live cycle's write pass: score, latch, and return the newly-latched ids.

    Runs after the cycle's polls so the cohorts reflect the day's ingested
    transitions, and before the caller's corpus push so the committed pointer
    always carries the latch state downstream readers see. The returned ids are
    the cycle's newly-latched picks (the selection sweep queues them via the
    ``predict_queued_at`` debounce — a never-queued case passes it).
    """
    scores, to_select, _, _ = _selection_plan(conn, config)
    corpus.set_salience_scores(conn, scores, SALIENCE_VERSION)
    corpus.latch_salience_selected(conn, to_select)
    return to_select


def reconcile_salience_selection(
    conn: sqlite3.Connection, config: SalienceConfig, *, apply: bool
) -> SalienceSelectionResult:
    """Score the in-scope cert petitions and latch the per-conference selected slice.

    Dry run by default (scores and picks are computed but nothing is written);
    ``apply`` writes the scores/version on every in-scope case and latches
    ``salience_selected`` on the newly-selected ones. Idempotent under the sticky
    latch — a second run with no corpus change latches nothing new.
    """
    scores, to_select, eligible, conferences = _selection_plan(conn, config)
    if apply:
        corpus.set_salience_scores(conn, scores, SALIENCE_VERSION)
        corpus.latch_salience_selected(conn, to_select)
    return SalienceSelectionResult(
        applied=apply,
        version=SALIENCE_VERSION,
        eligible_cases=eligible,
        scored=len(scores),
        conferences=conferences,
        newly_selected=len(to_select),
        sample_selected=sorted(to_select)[:_MAX_SAMPLE],
    )
