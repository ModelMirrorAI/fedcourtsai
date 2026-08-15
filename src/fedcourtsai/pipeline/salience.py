"""The salience gate: deterministic scoring and per-conference selection.

The write pass behind salience-ordered prediction scope (see ``docs/salience.md``).
It scores every in-scope SCOTUS case with the **active frozen** salience
function and latches ``salience_selected`` on the fundable slice: each conference
cohort's top-``N`` by score, plus the always-include carve-outs (CVSG petitions
and anything at/above the salience floor), which sit *above* ``N``, plus the
**interim reserve** — up to ``interim_reserve_slots`` pending substantive
applications per pass, which lower the current conference's rank-fill limit by
the slots in use, so the reserve is defined inside ``N`` (``docs/budget.md``).

Two invariants make the pass safe to re-run over a live conference:

- **Sticky selection.** ``salience_selected`` is a one-way latch
  (:func:`fedcourtsai.corpus.latch_salience_selected` only ever sets it), so a
  petition selected early keeps its committed forward prediction even if fresher
  petitions later out-rank it. The pass never de-selects; the realized selected
  count may drift above ``N``. The one sanctioned clear lives in this module
  too — :func:`unlatch_overselected`, a maintainer-run migration for the
  overhang a capacity resize leaves, never part of the pass.
- **Per-conference cohorts.** The cap is applied within each
  ``distributed_for_conference`` cohort, so "why this case and not that one"
  replays against one conference's candidate pool at a fixed score version. A
  petition not yet distributed for conference is scored but not selected — it is
  not up for prediction yet — unless the active scorer selects arrivals
  (``selects_arrivals``), in which case a second, cohort-less pass latches the
  arrival picks (the keyed random draw plus the carve-in predicate) and mints
  each pick's arrival event, with no rank and no capacity: the arrival cohort
  rides beside ``N``, never inside it. A petition already **decided**
  (:func:`fedcourtsai.corpus.resolution_date` is not ``None``) is scored (the
  board's historical rows still want a band) but never enters a cohort, so a
  historical conference's decided docket cannot be newly latched — it has no
  open event to predict, and counting it would muddy "selected = tournament
  spend" on the salience board.

The score is recomputed every run (a pure function of the row's current features);
only the selection latch persists. This module owns no destructive behavior — it
writes only the ``salience_*`` columns; the read-time enforcement that consumes the
latch lives elsewhere.

**Scoring is versioned by registry, not by edit.** :data:`SCORERS` holds every
frozen salience version as a :class:`SalienceScorer` — score function, band
function, band names, and always-include rule together, because all four decide
what a band label means. :data:`SALIENCE_VERSION` names the **active** one: the
version the live pass scores with and stamps onto the corpus and onto every
:class:`~fedcourtsai.schemas.PredictionContext`. A refit registers a new version
beside the old rather than editing it, so a past ranking always replays against
the function that produced it, and the base-rate pool stays pinned to the scorer
whose band it is quoting (``pipeline.base_rates._pooled_band_rate``).

The corpus itself is deliberately **single-version**: ``salience_score`` and
``salience_version`` are one column each, holding the active scorer's view. What
makes history safe is not the corpus but the frozen band and version on each
committed prediction — so re-pointing the active version can never retroactively
re-band a prediction already written.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType

from .. import corpus
from ..config import SalienceConfig
from ..schemas import SalienceSelectionResult, SalienceUnlatchResult
from . import caption

# The **active** salience-function version: the one the live selection pass scores
# and stamps with. A refit is a NEW version registered alongside, never an
# in-place edit, so any past ranking replays against the function that produced
# it — see :data:`SCORERS`.
SALIENCE_VERSION = "sal-v3"

# sal-v1 builds a ranking score from empirical grant rates. Every constant below
# is a real SCOTUS cert grant rate from ``metrics/statpack.md`` (denial-reweighted),
# so the ranking is interpretable and grounded in reality rather than invented
# weights. The primary signal is the stronger of the petition's *own-trajectory*
# grant rates — relist bucket and CVSG — and the originating circuit rides only as
# a small nudge (a circuit's marginal already reflects its relist mix, so treating
# it as a co-equal signal would double-count and inflate every petition from a
# high-grant circuit). The joint/compounding cut is deferred to a later
# version (sal-v2 reuses this score unchanged). Frozen for
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


#: The sal-v2 arrival draw's key — deliberately a string literal, never
#: `SALIENCE_VERSION`: the assignment is fixed by registration, so the
#: pointer flips and the draw does not, and a later version that wants an
#: arrival slice registers its own key (a new pre-registered population,
#: never a silent re-draw of this one). Re-running the draw under this key
#: over the same case ids reproduces the same slice, for the replay and for
#: any skeptic, and no selection rule can steer it (the hash input is the
#: public case id and this public constant).
_ARRIVAL_DRAW_KEY = "sal-v2"

#: When the sal-v2 arrival cohort begins: the OT2026 docket-year roll. A case
#: filed before this instant is not at its arrival moment — it is the standing
#: pre-registration-era backlog, which includes years of never-resolved
#: data-gap rows whose `distribution_count` was simply never parsed (a dry run
#: over the 2026-08 corpus finds ~560 such rows the draw would otherwise
#: latch, against the cohort's budgeted ~95/Term). Registration-fixed like
#: the draw key: moving it changes the arrival population, so a change is a
#: new pre-registered population, never a quiet widening. Backlog cases still
#: earn escalation selection as their trajectory signals accrue.
ARRIVAL_COHORT_SINCE = date(2026, 7, 1)


def arrival_draw(case_id: str, rate: float) -> bool:
    """Whether ``case_id`` falls in the deterministic arrival random slice.

    A keyed hash draw (the :mod:`fedcourtsai.blinding` shuffle-key shape):
    ``sha256(key NUL case_id)`` — the NUL byte the separator — with the
    digest's first 8 bytes read big-endian as a fraction of the hash space,
    selected iff below ``rate``. ``case_id`` is the canonical
    :func:`fedcourtsai.ids.case_id` form; any other spelling of the same case
    draws a different, silently valid answer. Pure and replayable — no stored
    column, no clock, no RNG state — so the slice is reproducible from the
    corpus and the committed constant alone, which is what lets its
    unbiasedness claim be audited rather than trusted; a golden-vector test
    pins the exact mapping. ``rate`` 0 selects nothing; 1 everything.
    """
    if rate <= 0.0:
        return False
    if rate >= 1.0:
        return True
    digest = hashlib.sha256(f"{_ARRIVAL_DRAW_KEY}\x00{case_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") < rate * 2**64


def _relist_signal(row: corpus.CorpusRow) -> float:
    """The relist bucket's empirical grant rate; the parse-coverage sentinel is NULL."""
    if row.distribution_count is None:
        return _RELIST_UNKNOWN_RATE
    relists = max(0, row.distribution_count - 1)
    if relists >= 2:
        return _RELIST_HIGH_RATE
    return _RELIST_GRANT_RATE[relists]


def _sal_v1_score(row: corpus.CorpusRow) -> float:
    """The frozen ``sal-v1`` ranking score, built from empirical grant rates.

    The primary signal is the stronger of the petition's own-trajectory grant
    rates — relist bucket and (if present) CVSG — nudged by a small fraction of its
    originating circuit's grant rate. Monotone in each feature. Fee class does not
    enter: IFP petitions are excluded at Tier 0 (the ``OUT_OF_SCOPE_RULES``
    predicate), leaving the scored set paid-only (see
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


def _sal_v1_band(row: corpus.CorpusRow) -> str:
    """The frozen ``sal-v1`` salience band of a row (see :data:`_SALIENCE_BANDS`).

    A pure function of :func:`_sal_v1_score`, so it inherits the scorer's
    determinism: the same row features reproduce the same band.
    """
    score = _sal_v1_score(row)
    for band, lower in _SALIENCE_BANDS:
        if score >= lower:
            return band
    return _SALIENCE_BANDS[-1][0]  # unreachable (the baseline cutpoint is 0.0); a guard


def _sal_v1_carve_out(row: corpus.CorpusRow, score: float, floor: float) -> bool:
    """``sal-v1``'s always-include rule: a CVSG petition, or a score at/above the floor."""
    return row.cvsg_date is not None or score >= floor


# sal-v2: the arrival-aware version. The RANKING is sal-v1's exactly — the
# caption enters as a band dimension and an always-include predicate, never a
# score weight, because the class's discrimination replicates while its
# magnitude is a census figure that re-measures every Term (the reviewed
# verdict; docs/salience.md). What sal-v2 adds:
#
# - a `federal` band above `high` and a `state` band between `high` and
#   `elevated`, ordered by measured grant rate (census caption-v1: federal
#   ~0.70; the state CLASS marginal ~0.23 against high's 0.28-0.44 span and
#   elevated's 0.078 — the band's own realized rate sits below the marginal,
#   since its strongest members band `high`; the statpack measures each band
#   empirically either way). The
#   band is the strongest of the caption-class band and the relist/CVSG
#   tier, so it stays monotone over a petition's life: the class is fixed at
#   filing and the trajectory tier only rises.
# - the federal arrival carve-in beside sal-v1's CVSG/floor rule: a
#   government petitioner is always in, at any score — the one arrival-time
#   signal whose discrimination replicated in all eight complete measured
#   Terms (OT2017-OT2024, lift 8.1x-16.4x; OT2025 is right-censored and
#   counted as supportive, never as held-out). The frozen thing is the
#   PREDICATE (classify_petitioner == "federal" under caption-v1), not the
#   concept "government petitioner" — which is why that rule's federal recall
#   gap is answered by a new caption rule under a new salience version
#   (sal-v3, below) rather than by widening anything here.
# - the arrival random slice (`arrival_draw`), applied at the selection
#   seam rather than here: the draw is selection policy over undistributed
#   arrivals, not a property of a row's strength.
_SAL_V2_BAND_ORDER: tuple[str, ...] = ("federal", "high", "state", "elevated", "baseline")


def _sal_v2_band(row: corpus.CorpusRow) -> str:
    """The strongest of the caption-class band and the sal-v1 trajectory tier."""
    trajectory = _sal_v1_band(row)
    cls = caption.petitioner_class(row)
    if cls == "federal":
        return "federal"
    if cls == "state" and trajectory not in ("high",):
        return "state"
    return trajectory


def _sal_v2_carve_out(row: corpus.CorpusRow, score: float, floor: float) -> bool:
    """sal-v1's rule, plus the federal arrival carve-in."""
    return _sal_v1_carve_out(row, score, floor) or caption.petitioner_class(row) == "federal"


# sal-v3: sal-v2 with the caption predicate at `caption-v2`. Everything else is
# sal-v2's byte for byte — the same sal-v1 ranking score, the same band
# vocabulary and order (`_SAL_V2_BAND_ORDER`, shared deliberately: the two
# versions' band labels mean the same tier, so a band name is comparable across
# them and only the class predicate moves), and the same carve-in shape. What
# changes is recall of the frozen thing: sal-v2's carve-in predicate is
# `classify_petitioner == "federal"` under caption-v1, whose measured federal
# recall gap classifies genuinely federal petitioners `private`; sal-v3's is the
# same predicate under caption-v2, which reads those shapes. caption-v2 keeps
# every non-`private` caption-v1 read by construction, so a row's band under
# sal-v3 is its sal-v2 band or stronger and its carve status only ever gains —
# what the widened captions do is migrate from their trajectory tier into the
# `federal` band and the carve-in, which is a census question with its own
# statistical review (docs/salience.md).


def _sal_v3_band(row: corpus.CorpusRow) -> str:
    """sal-v2's band rule, read through ``caption-v2``."""
    trajectory = _sal_v1_band(row)
    cls = caption.petitioner_class_v2(row)
    if cls == "federal":
        return "federal"
    if cls == "state" and trajectory not in ("high",):
        return "state"
    return trajectory


def _sal_v3_carve_out(row: corpus.CorpusRow, score: float, floor: float) -> bool:
    """sal-v1's rule, plus the federal arrival carve-in read through ``caption-v2``."""
    return _sal_v1_carve_out(row, score, floor) or caption.petitioner_class_v2(row) == "federal"


@dataclass(frozen=True)
class SalienceScorer:
    """One frozen salience version: everything that makes a ranking reproducible.

    A version is not just a score function. The band cutpoints, the band *names*,
    and the always-include rule are all part of what "sal-v1 high" means, so a
    refit that changed any of them while reusing the label would silently
    redefine a published segment. Bundling the four here makes a version a single
    object to register, and makes "which function produced this band" answerable
    by lookup rather than by reading the commit that was live at the time.

    The pairing of ``carve_out`` with ``bands`` is load-bearing and pinned by
    test: the always-include floor and the strongest band's cutpoint must select
    the same petitions, or a refit opens a silent gap between "carved in" and the
    band the statpack conditions its base rate on.
    """

    version: str
    score: Callable[[corpus.CorpusRow], float]
    band: Callable[[corpus.CorpusRow], str]
    bands: tuple[str, ...]
    carve_out: Callable[[corpus.CorpusRow, float, float], bool]
    # Whether this version selects an ARRIVAL cohort: undistributed pending
    # petitions picked at docketing by the deterministic draw
    # (`arrival_draw` at `config.arrival_sample_rate`) or the version's own
    # carve-out predicate. False for sal-v1 — its features are
    # docket-acquired, so it has nothing to say at arrival.
    selects_arrivals: bool = False


_SAL_V1 = SalienceScorer(
    version="sal-v1",
    score=_sal_v1_score,
    band=_sal_v1_band,
    bands=tuple(band for band, _ in _SALIENCE_BANDS),
    carve_out=_sal_v1_carve_out,
)

_SAL_V2 = SalienceScorer(
    version="sal-v2",
    score=_sal_v1_score,  # the ranking IS sal-v1's; the caption never weights it
    band=_sal_v2_band,
    bands=_SAL_V2_BAND_ORDER,
    carve_out=_sal_v2_carve_out,
    selects_arrivals=True,
)

_SAL_V3 = SalienceScorer(
    version="sal-v3",
    score=_sal_v1_score,  # still sal-v1's ranking; the caption never weights it
    band=_sal_v3_band,
    bands=_SAL_V2_BAND_ORDER,  # the same band vocabulary, in the same order
    carve_out=_sal_v3_carve_out,
    selects_arrivals=True,
)

# Every registered version, keyed by label. A past ranking replays against the
# function that produced it, so a version is only ever added here — never edited
# and never removed, whatever the live pass currently scores with.
SCORERS: Mapping[str, SalienceScorer] = MappingProxyType(
    {_SAL_V1.version: _SAL_V1, _SAL_V2.version: _SAL_V2, _SAL_V3.version: _SAL_V3}
)


def scorer(version: str | None = None) -> SalienceScorer:
    """The registered scorer for ``version``, defaulting to the active one.

    Raises :class:`KeyError` for an unregistered label rather than falling back
    to the active scorer: a caller asking for a version the process cannot
    produce wants an error, not silently re-banded output under a name it did
    not ask for.
    """
    return SCORERS[version if version is not None else SALIENCE_VERSION]


def registered_versions() -> tuple[str, ...]:
    """The registered version labels, active first, then the rest sorted.

    The order any all-versions consumer iterates in, so a report's cell order is
    stable across runs and puts the live scorer's numbers first.
    """
    rest = sorted(version for version in SCORERS if version != SALIENCE_VERSION)
    return (SALIENCE_VERSION, *rest)


def salience_score(row: corpus.CorpusRow) -> float:
    """The **active** scorer's ranking score for a row."""
    return scorer().score(row)


def salience_band(row: corpus.CorpusRow) -> str:
    """The **active** scorer's salience band for a row."""
    return scorer().band(row)


def salience_bands() -> tuple[str, ...]:
    """The active scorer's band names strongest→weakest — the statpack's segment order."""
    return scorer().bands


def carve_out(row: corpus.CorpusRow, score: float, floor: float) -> bool:
    """The **active** scorer's always-include rule.

    The version-agnostic entry point, for a caller that means "whatever the live
    pass would carve in". A caller working with a specific version — the gate
    replay, which must apply the same predicate the selector applied — reaches
    :attr:`SalienceScorer.carve_out` on that version's record instead, so its
    report cannot drift from the selection it describes.
    """
    return scorer().carve_out(row, score, floor)


def _capacity(conference: date, config: SalienceConfig) -> int:
    """The per-cohort ``N``: a larger cap for the Term's opening long conference."""
    if conference.month == _LONG_CONFERENCE_MONTH:
        return config.long_conference_capacity
    return config.per_conference_capacity


def _select_cohort(
    rows: list[corpus.CorpusRow],
    scores: dict[str, float],
    capacity: int,
    floor: float,
    *,
    reserve: int = 0,
    version: SalienceScorer,
) -> set[str]:
    """The case ids to hold selected in one conference cohort.

    Carve-outs (:func:`carve_out` — CVSG petitions and anything at/above the
    floor) are selected unconditionally and sit *above* the ``N`` budget; the
    remainder is ranked by score (descending, case_id tie-break) and fills to
    ``N`` minus ``reserve`` — the interim reserve slots in use this pass, which
    displace the lowest-ranked rank-fill picks (never a carve-out) so the
    reserve spends inside ``N``.
    """
    selected = {row.case_id for row in rows if version.carve_out(row, scores[row.case_id], floor)}
    remainder = sorted(
        (row for row in rows if row.case_id not in selected),
        key=lambda row: (-scores[row.case_id], row.case_id),
    )
    selected.update(row.case_id for row in remainder[: max(0, capacity - reserve)])
    return selected


def _interim_ladder_key(row: corpus.CorpusRow) -> tuple[int, int, str]:
    """Reserve pick order: furthest up the escalation ladder first.

    Two of the latched interim signals, strongest first — a requested response
    (the Court's affirmative act of attention), then the amicus count — with
    ``case_id`` for determinism. The referral signal stays on the ladder as a
    latched observation but out of the pick order:
    a referral is usually the disposition docket entry itself, so it carries
    no forecast horizon — a slot spent on it funds a prediction of an already
    written order. A deliberate *ordering*, not a scored rate: no grant
    probability is asserted, only which pending applications the bounded reserve
    funds first. The ordering is nonetheless a **selection** the interim
    baseline is not conditioned on, which is registered as the estimator's
    stated limitation (``docs/salience.md``, *The interim docket*). ``None``
    signals sort as absent, so a never-parsed row never outranks a parsed one.
    """
    return (
        0 if row.response_requested else 1,
        -(row.amicus_briefs or 0),
        row.case_id,
    )


def plan_cohorts(
    rows: Iterable[corpus.CorpusRow],
    config: SalienceConfig,
    *,
    version: SalienceScorer | None = None,
    select_arrivals: bool | None = None,
) -> tuple[dict[str, float], list[str], int, int]:
    """Score ``rows`` and pick each conference cohort's selected slice.

    ``version`` selects the scorer, defaulting to the active one; the gate
    replay passes each registered version in turn so one report can say what
    every scorer would have picked at the same reconstructed moment.

    The connection-free core of the selection pass, shared with the gate replay
    (:mod:`fedcourtsai.salience_replay`), which feeds it point-in-time
    synthesized rows instead of the live corpus scan. Callers own eligibility:
    every row given is scored, so the Tier-0 filter runs before this. Returns
    ``(scores, to_select, eligible, conferences)`` where ``to_select`` holds
    only the **not-yet-latched** picks (the sticky latch is additive; the plan
    never de-selects). Cohorting keys on each row's
    ``distributed_for_conference``, so a replay caller sets that field to the
    as-of value it reconstructs.

    An **application** row (the interim docket — only substantive applications
    survive Tier 0) is never distributed for conference, so it competes for the
    **interim reserve** instead of a cohort: pending (unresolved) applications
    fill up to ``interim_reserve_slots``, escalation-ladder order
    (:func:`_interim_ladder_key`), counting the still-pending already-selected
    ones against the cap first (a slot frees only when its occupant resolves).
    The slots in use lower the rank-fill limit in the **latest** conference
    cohort of the pass — the conference cycle the applications are live in — so
    the reserve is defined inside ``N``. It is sized to *spend* inside ``N``
    too: a lowered limit costs a cert pick wherever the eligible non-carve-out
    remainder exceeds it — near the typical cohort's eligible size, and not
    yet measured at the shipped capacity (``docs/budget.md``). An unfilled
    reserve lowers nothing.
    """
    active = version if version is not None else scorer()
    # `select_arrivals` narrows (never widens) the version's own arrival
    # semantics: the gate replay passes False at every non-arrival policy,
    # because "still undistributed at a later cutoff" is a property of the
    # reconstruction, not a live arrival — pooling those picks into an
    # escalation cell is the cohort blend the design forbids.
    arrivals_on = (
        active.selects_arrivals
        if select_arrivals is None
        else (select_arrivals and active.selects_arrivals)
    )
    scores: dict[str, float] = {}
    cohorts: dict[date, list[corpus.CorpusRow]] = defaultdict(list)
    applications: list[corpus.CorpusRow] = []
    arrivals: list[str] = []
    already_selected: set[str] = set()
    eligible = 0
    for row in rows:
        eligible += 1
        scores[row.case_id] = active.score(row)
        if row.salience_selected:
            already_selected.add(row.case_id)
        if row.court == "scotus" and corpus.is_scotus_application_form(row.docket_number):
            # An application is never distributed for conference, so it can
            # never enter a cert cohort; a pending one competes for the
            # interim reserve instead. Resolved ones are scored only, exactly
            # like decided petitions below.
            if row.disposition is None and corpus.resolution_date(row) is None:
                applications.append(row)
            continue
        # A decided petition has no open event left to predict, so latching it
        # spends nothing — but it would still count toward "newly selected" and
        # muddy the salience board's "selected = tournament spend" reading with
        # historical cohorts. Score it (the board's historical rows still want a
        # band), but leave it out of cohort selection entirely.
        if row.distributed_for_conference is not None and corpus.resolution_date(row) is None:
            cohorts[row.distributed_for_conference].append(row)
        elif (
            arrivals_on
            and row.distributed_for_conference is None
            and not row.distribution_count
            and corpus.resolution_date(row) is None
            and row.disposition is None
            and not row.salience_selected
            and row.date_filed is not None
            and row.date_filed >= ARRIVAL_COHORT_SINCE
            and (
                arrival_draw(row.case_id, config.arrival_sample_rate)
                or active.carve_out(row, scores[row.case_id], config.floor)
            )
        ):
            # The arrival cohort: predicate-selected at docketing — the
            # deterministic slice or the version's always-include rule — with
            # no rank and no capacity, because the whole design is that no
            # ranking exists yet worth the name (docs/salience.md). The
            # freshness condition mirrors the arrival event's own mint guard,
            # and the cohort-start bound keeps the standing backlog out (a
            # dateless row is likewise out: no filing date, no arrival moment).
            arrivals.append(row.case_id)

    # The interim reserve: still-pending occupants hold their slots (sticky
    # latch), new picks fill the remainder in ladder order.
    occupants = [row for row in applications if row.salience_selected]
    open_slots = max(0, config.interim_reserve_slots - len(occupants))
    contenders = sorted(
        (row for row in applications if not row.salience_selected), key=_interim_ladder_key
    )
    reserve_picks = [row.case_id for row in contenders[:open_slots]]
    reserve_in_use = len(occupants) + len(reserve_picks)

    to_select: list[str] = [*reserve_picks, *arrivals]
    current_conference = max(cohorts) if cohorts else None
    for conference, cohort_rows in cohorts.items():
        selected = _select_cohort(
            cohort_rows,
            scores,
            _capacity(conference, config),
            config.floor,
            reserve=reserve_in_use if conference == current_conference else 0,
            version=active,
        )
        # Sticky + additive: latch only the not-yet-selected; never de-select.
        to_select.extend(case_id for case_id in selected if case_id not in already_selected)
    return scores, to_select, eligible, len(cohorts)


def _selection_plan(
    conn: sqlite3.Connection, config: SalienceConfig
) -> tuple[dict[str, float], list[str], int, int]:
    """Score the in-scope SCOTUS cases and pick each cohort's selected slice.

    The pure planning half of the pass: the live corpus scan with the Tier-0
    eligibility filter applied (which admits cert petitions and substantive
    applications), delegating scoring, cohort selection, and the interim
    reserve to :func:`plan_cohorts`.
    """
    return plan_cohorts(
        (
            row
            for row in corpus.iter_rows(conn, court="scotus")
            # Tier-0 excluded (incl. IFP): not scored, not selected.
            if corpus.out_of_scope_reason_full(conn, row) is None
        ),
        config,
    )


def apply_salience_selection(conn: sqlite3.Connection, config: SalienceConfig) -> list[str]:
    """The live cycle's write pass: score, latch, and return the newly-latched ids.

    Runs after the cycle's polls so the cohorts reflect the day's ingested
    transitions, and before the caller's corpus push so the committed pointer
    always carries the latch state downstream readers see. The returned ids are
    the cycle's newly-latched picks (the selection sweep queues them via the
    ``predict_queued_at`` debounce — a never-queued case passes it).

    Under a scorer with ``selects_arrivals`` the pass also mints the
    **arrival event** for every latched, pending, undistributed cert row
    that lacks one — driven off *state*, not off this pass's latch delta, so
    it is idempotent, a crash between the latch write and the mint heals on
    the next pass, and the manual ``reconcile-salience-selection`` command
    mints correctly too. The mint matters because the sweep queues a latched
    case's open events and an undistributed petition's only mintable cert
    cell is the arrival moment's — the baseline waits for its own
    distribution moment (``store``'s admission), so an unminted pick would
    sit latched with nothing to forecast.
    """
    scores, to_select, _, _ = _selection_plan(conn, config)
    corpus.set_salience_scores(conn, scores, SALIENCE_VERSION)
    corpus.latch_salience_selected(conn, to_select)
    _mint_owed_arrival_events(conn)
    return to_select


def _mint_owed_arrival_events(conn: sqlite3.Connection) -> None:
    """Mint the arrival event for every selected arrival still lacking one.

    State-driven and idempotent: scans the latched, pending, undistributed
    SCOTUS cert rows and mints where the event is absent — the recovery path
    for a pass interrupted between its latch write and its mint, and the
    reason the manual reconcile needs no minting logic of its own. A no-op
    under a scorer without arrival semantics.
    """
    if not scorer().selects_arrivals:
        return
    from . import outcome  # noqa: PLC0415 - outcome<-moments<-... keeps this deferred

    events: list[corpus.CorpusEvent] = []
    for row in corpus.iter_rows(conn, court="scotus"):
        if (
            not row.salience_selected
            or row.distributed_for_conference is not None
            or row.distribution_count
            or corpus.resolution_date(row) is not None
            or corpus.is_scotus_application_form(row.docket_number)
            # The cohort-start bound, restated here so a row latched some other
            # way (a pre-boundary carve-out, an older latch vintage) can never
            # back into an arrival event it was never selected for.
            or row.date_filed is None
            or row.date_filed < ARRIVAL_COHORT_SINCE
        ):
            continue
        case_events = corpus.events_for_case(conn, row.case_id)
        if any(e.event_id == "evt-petition-arrival-disposition" for e in case_events):
            continue
        open_ids = [e.event_id for e in case_events if not e.resolved]
        minted = outcome.arrival_event_for(row, open_ids)
        if minted is not None:
            events.append(minted)
    if events:
        corpus.upsert_events(conn, events)


def reconcile_salience_selection(
    conn: sqlite3.Connection, config: SalienceConfig, *, apply: bool
) -> SalienceSelectionResult:
    """Score the in-scope SCOTUS cases and latch the per-conference selected slice.

    Dry run by default (scores and picks are computed but nothing is written);
    ``apply`` writes the scores/version on every in-scope case and latches
    ``salience_selected`` on the newly-selected ones. Idempotent under the sticky
    latch — a second run with no corpus change latches nothing new.
    """
    scores, to_select, eligible, conferences = _selection_plan(conn, config)
    if apply:
        corpus.set_salience_scores(conn, scores, SALIENCE_VERSION)
        corpus.latch_salience_selected(conn, to_select)
        _mint_owed_arrival_events(conn)
    return SalienceSelectionResult(
        applied=apply,
        version=SALIENCE_VERSION,
        eligible_cases=eligible,
        scored=len(scores),
        conferences=conferences,
        newly_selected=len(to_select),
        sample_selected=sorted(to_select)[:_MAX_SAMPLE],
    )


def _unlatch_scan(
    conn: sqlite3.Connection, active: SalienceScorer
) -> tuple[dict[str, float], dict[date, list[corpus.CorpusRow]], int, int]:
    """The reconcile's eligibility scan, mirroring ``_selection_plan``'s.

    Returns ``(scores, pending cohorts, spared_out_of_scope,
    spared_undistributed)`` — the spared counts tally latched pending rows the
    sweep deliberately leaves outside every cohort, so the result's ledger
    reconciles against the corpus's own latched-row count.
    """
    scores: dict[str, float] = {}
    cohorts: dict[date, list[corpus.CorpusRow]] = defaultdict(list)
    spared_out_of_scope = 0
    spared_undistributed = 0
    for row in corpus.iter_rows(conn, court="scotus"):
        pending = corpus.resolution_date(row) is None
        if corpus.out_of_scope_reason_full(conn, row) is not None:
            if row.salience_selected and pending:
                spared_out_of_scope += 1
            continue
        scores[row.case_id] = active.score(row)
        if corpus.is_scotus_application_form(row.docket_number):
            continue
        if row.distributed_for_conference is None:
            if row.salience_selected and pending:
                spared_undistributed += 1
            continue
        if pending:
            cohorts[row.distributed_for_conference].append(row)
    return scores, cohorts, spared_out_of_scope, spared_undistributed


def unlatch_overselected(
    conn: sqlite3.Connection, config: SalienceConfig, *, apply: bool
) -> SalienceUnlatchResult:
    """Clear the latch where a from-scratch selection would not pick — one-time.

    The sticky latch is additive by design, so a capacity resize leaves every
    petition latched under the old caps latched — a standing overhang the live
    pass can never shrink, spending cells the shipped envelope never budgeted.
    This deliberate, maintainer-run migration recomputes each **pending**
    conference cohort's selection from scratch — same scorer, same carve-outs,
    ``reserve=0`` (the permissive reading: the interim reserve can only shrink
    a cut, so ignoring it never widens the clear) — and clears the latch on
    pending petitions the recomputation would not pick.

    Deliberately untouched, each counted in the result so the ledger
    reconciles against the corpus: decided rows (their latch is the
    historical record of having been selected), interim applications (the
    reserve's occupancy is its own sticky contract), never-distributed
    petitions — under sal-v2 these are the arrival cohort, a frozen
    pre-registered draw that is never re-cut, so its picks are spared by
    policy; under sal-v1 there is simply no cohort to recompute — and
    Tier-0-excluded rows —
    those keep a stale latch that is inert under ``predict_excluded`` and the
    shared exclusion reasoning, deliberately not cleared here. A committed
    prediction on a cleared case stays committed **and stays graded**: the
    evaluate matrix reads the scope filter without the salience skip, so
    clearing a latch never strands a prediction from scoring. Two residuals
    the recomputation accepts by construction: ``reserve=0`` means the
    current cohort retains up to ``interim_reserve_slots`` petitions the live
    pass's own rank fill would not fund, and a stale cohort's from-scratch
    pick ranks its *stragglers* (resolved members are gone), so "retained" is
    top-N of what remains, not what the gate would pick from the original
    pool. Run ``dedupe-live-rows --apply`` first: a merge takes the latch
    stickily from either twin, so an unmerged bulk twin could re-latch a
    cleared case. Idempotent: a reconciled corpus clears nothing. Dry-run by
    default; ``apply`` writes.
    """
    active = scorer()
    scores, cohorts, spared_out_of_scope, spared_undistributed = _unlatch_scan(conn, active)
    latched_pending = 0
    retained = 0
    unlatch: list[str] = []
    for conference, cohort_rows in cohorts.items():
        keep = _select_cohort(
            cohort_rows,
            scores,
            _capacity(conference, config),
            config.floor,
            reserve=0,
            version=active,
        )
        for row in cohort_rows:
            if not row.salience_selected:
                continue
            latched_pending += 1
            if row.case_id in keep:
                retained += 1
            else:
                unlatch.append(row.case_id)
    if apply and unlatch:
        corpus.unlatch_salience_selected(conn, unlatch)
    return SalienceUnlatchResult(
        applied=apply,
        version=SALIENCE_VERSION,
        pending_cohorts=len(cohorts),
        latched_pending=latched_pending,
        retained=retained,
        unlatched=len(unlatch),
        spared_out_of_scope=spared_out_of_scope,
        spared_undistributed=spared_undistributed,
        unlatched_case_ids=sorted(unlatch),
    )
