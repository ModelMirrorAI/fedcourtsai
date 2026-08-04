"""Aggregate disposition base-rates over the corpus (read-only, deterministic, offline).

The aggregate counterpart of :func:`fedcourtsai.corpus.retrieve_priors` — the per-case
precedent retrieval behind ``fedcourts query``. Instead of returning a handful of
individual priors, it rolls the *whole* matched set into base-rates: how the realized
dispositions split overall and per a chosen dimension (court, topic, judge, SCOTUS
Term year, disposition). A pure function of the corpus — no clock, no network, no
randomness — so the same corpus yields byte-identical output.

Exposed two ways, both read-only: ``fedcourts stats`` (a maintainer investigating the
corpus, or a predictor pulling base-rate context after a corpus pull) and the
``corpus-stats`` mode of the ``run-analytics`` workflow. It never writes the corpus,
``data/``, the corpus remote, or git.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from . import corpus
from .config import StatpackConfig
from .corpus import CorpusRow
from .pipeline.interim_signals import ApplicationKind
from .pipeline.judgment import grant_term_year, judgment_disturbed
from .pipeline.outcome import granted_flag, is_machine_readable
from .pipeline.salience import SALIENCE_VERSION, salience_band, salience_bands
from .schemas import (
    GRANT_FAMILY_DISPOSITIONS,
    AnalyticsReport,
    BaseRateBucket,
    Disposition,
    DispositionShare,
    DocketPack,
    DocketPackTerm,
    FeeClass,
    GroupBy,
    Judgment,
    StatPack,
    StatPackCoverage,
    StatPackInterim,
    StatPackInterimTerm,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackSection,
    StatPackTerm,
    StatPackTermClass,
    StatPackTermSegment,
    TimingStats,
)
from .supremecourt import IFP_SERIAL_BASE, parse_scotus_docket_number

if TYPE_CHECKING:
    import sqlite3

# Bucket key stand-ins for rows that carry no value on the grouped dimension (a null
# topic, an unparseable Term, no panel), for the open cases in a disposition group,
# and for rows whose live-parsed signal columns were never populated (the cert-signal
# dimensions distinguish "no signal observed" from "never looked").
_NONE_KEY = "(none)"
_OPEN_KEY = "(open)"
_UNKNOWN_KEY = "(unknown)"

# Disposition labels that count as a cert grant for the grant-rate summaries — a
# GVR grants the petition, so it sums into the grant rate alongside a plain grant
# (both were a single "granted" bucket before the `gvr` label split them out).
# `granted-in-part` stays its own bucket, preserving the pre-`gvr` definition.
# The label form of `schemas.GRANT_FAMILY_DISPOSITIONS`, which is the one
# definition: the rendered tables print a grant count and a grant rate in
# adjacent columns, and a consumer that reconstructs the count from the rate
# subtracts on these terms — so two enumerations of "what counts as a grant"
# would diverge somewhere visible. It is deliberately *not*
# `pipeline.outcome.granted_flag`'s set, which owns the binary scoring target
# and admits `granted-in-part`. Sorted, so the constant is order-stable.
_GRANT_LABELS = tuple(sorted(d.value for d in GRANT_FAMILY_DISPOSITIONS))


def _grant_family_share(bucket: BaseRateBucket) -> float | None:
    """The pooled grant-family share of a bucket's resolved rows.

    The single definition behind every published ``est_grant*rate`` figure. The
    pooling is load-bearing: the ``gvr`` label is a forward convention, so the
    ``granted`` / ``gvr`` split reflects ingestion history between Terms
    (:data:`_GVR_SPLIT_CAVEAT`), and only the pooled family is comparable
    across them. ``None`` when nothing resolved — an all-denied bucket has a
    real 0% rate; a bucket with nothing resolved has no rate at all.
    """
    if not bucket.resolved:
        return None
    return sum(d.share for d in bucket.dispositions if d.disposition in _GRANT_LABELS)


class AnalyticsQuery(BaseModel):
    """Structured filter selecting the corpus rows an :class:`AnalyticsReport` aggregates.

    Reuses the ``fedcourts query`` vocabulary so the two share one mental model:
    ``court`` / ``topic`` / ``disposition`` match exactly, ``judges`` / ``citations``
    match on **overlap** (a row qualifies if it shares at least one value), and
    ``date_from`` / ``date_to`` bound ``date_filed`` inclusively. Unlike ``query`` the
    default keeps **open** cases, because their count is part of the base-rate picture
    (they are still excluded from each disposition's denominator); flip ``resolved_only``
    to drop them. ``group_by`` chooses the breakdown dimension, or ``None`` for the
    overall base rate only.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    court: str | None = None
    topic: str | None = None
    judges: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    disposition: Disposition | None = None
    date_from: date | None = Field(default=None, description="Keep rows filed on/after this date.")
    date_to: date | None = Field(default=None, description="Keep rows filed on/before this date.")
    term: int | None = Field(
        default=None,
        description="Keep SCOTUS rows whose docket number parses to this October-Term "
        "year. A Term is a SCOTUS concept, so non-SCOTUS rows (whose docket numbers "
        "can coincidentally parse, e.g. ca9 `22-15001`) never match a term filter.",
    )
    era: str | None = Field(
        default=None,
        description="Keep rows in one decade era, e.g. `1890s` "
        "(:func:`fedcourtsai.corpus.case_era`) — usable on exactly the historical "
        "rows whose docket numbers `term` cannot parse.",
    )
    cert_stage: bool = Field(
        default=False,
        description="Keep only modern Term-prefixed discretionary-cert SCOTUS "
        "dockets (:func:`fedcourtsai.corpus.is_modern_cert`), so the base rate "
        "reflects the population the cert model predicts rather than blending in "
        "historical merits-era labels.",
    )
    resolved_only: bool = Field(
        default=False,
        description="Drop unlabeled cases (default keeps them for the open count). "
        "Resolved here means disposition-LABELED — deliberately narrower than "
        "`query`'s resolved reading (which also counts a decision date), because "
        "the disposition denominators this command aggregates need labels.",
    )
    group_by: GroupBy | None = None


def _row_matches(row: CorpusRow, query: AnalyticsQuery) -> bool:
    """Whether ``row`` satisfies the query's Python-side filters.

    ``court`` and ``disposition`` are pushed into SQL by :func:`corpus.iter_rows`; the
    overlap filters (``judges`` / ``citations``), the exact ``topic``, the ``date_filed``
    range, the SCOTUS ``term``, and ``resolved_only`` are applied here over the
    narrowed candidate set. A row matches when no filter it is subject to misses.
    """
    filed = row.date_filed
    mismatches = (
        query.topic is not None and row.topic != query.topic,
        bool(query.judges) and not (set(query.judges) & set(row.judges)),
        bool(query.citations) and not (set(query.citations) & set(row.citations)),
        query.date_from is not None and (filed is None or filed < query.date_from),
        query.date_to is not None and (filed is None or filed > query.date_to),
        query.term is not None
        and (row.court != "scotus" or corpus.scotus_term_year(row.docket_number) != query.term),
        query.era is not None and corpus.case_era(row) != query.era,
        query.cert_stage and not corpus.is_modern_cert(row),
        query.resolved_only and row.disposition is None,
    )
    return not any(mismatches)


def _term_year_key(row: CorpusRow) -> str | None:
    year = corpus.scotus_term_year(row.docket_number)
    return str(year) if year is not None else None


def _relist_bucket_key(row: CorpusRow) -> str:
    """The relist bucket: 0 / 1 / 2 / 3+, or ``(unknown)`` before a live parse.

    Relists are ``distribution_count - 1`` floored at 0 (the first distribution
    is consideration, each further one a relist — an upper bound: a reschedule
    before first consideration also adds an entry). NULL means the proceedings
    were never live-parsed, which is a different fact from "never distributed".
    """
    if row.distribution_count is None:
        return _UNKNOWN_KEY
    relists = max(0, row.distribution_count - 1)
    return "3+" if relists >= 3 else str(relists)


def _cvsg_key(row: CorpusRow) -> str:
    """``cvsg`` / ``none`` / ``(unknown)`` — asserting "none" needs parse coverage.

    ``distribution_count`` is the live-signal family's parse-coverage sentinel:
    only a row whose proceedings were actually parsed can say the Court never
    called for the Solicitor General's views.
    """
    if row.cvsg_date is not None:
        return "cvsg"
    return "none" if row.distribution_count is not None else _UNKNOWN_KEY


def _fee_class(row: CorpusRow) -> FeeClass | None:
    """The docket serial's numbering stream, or ``None`` off the modern-cert form."""
    if row.court != "scotus":
        return None
    parsed = parse_scotus_docket_number(row.docket_number)
    if parsed is None:
        return None
    return FeeClass.ifp if parsed[1] >= IFP_SERIAL_BASE else FeeClass.paid


def _fee_class_key(row: CorpusRow) -> str | None:
    fee = _fee_class(row)
    return fee.value if fee is not None else None


def _is_scored_segment_row(row: CorpusRow) -> bool:
    """True for the population the salience scorer scores: paid modern-cert petitions.

    The salience gate excludes IFP petitions at Tier 0, so the scored (and thus
    predicted) segment is paid-only; the segment base rate must be conditioned on
    the same population it will anchor. ``is_modern_cert`` already implies a
    Term-prefixed SCOTUS docket, and the paid fee class narrows it to the scored set.
    """
    return corpus.is_modern_cert(row) and _fee_class(row) == FeeClass.paid


def _salience_band_key(row: CorpusRow) -> str:
    """The row's frozen ``sal-v1`` salience band (the pack-wide segment section key)."""
    return salience_band(row)


# Single-valued dimension -> its (possibly absent) key on a row. Judge is the one
# multi-valued dimension, handled apart in `_bucket_keys`. Rows without a value
# share the `(none)` bucket — for `originating_court` that visibility matters
# doubly, since only the REST and live channels populate the linkage (bulk rows
# never carry it); open cases under `disposition` share `(open)` rather than
# scattering. The cert-signal dimensions emit `(unknown)` themselves, so a
# coverage gap never masquerades as a value.
_KEY_FNS: dict[GroupBy, Callable[[CorpusRow], str | None]] = {
    GroupBy.court: lambda row: row.court,
    GroupBy.topic: lambda row: row.topic,
    GroupBy.term_year: _term_year_key,
    GroupBy.era: corpus.case_era,
    GroupBy.originating_court: lambda row: row.originating_court,
    GroupBy.disposition: lambda row: row.disposition,
    GroupBy.relist_bucket: _relist_bucket_key,
    GroupBy.cvsg: _cvsg_key,
    GroupBy.fee_class: _fee_class_key,
    GroupBy.salience_band: _salience_band_key,
}


def _bucket_keys(row: CorpusRow, group_by: GroupBy) -> list[str]:
    """The bucket key(s) ``row`` contributes to for the grouped dimension.

    Single-valued for every dimension except ``judge``, where a row joins one bucket
    per panel member (so grouped case counts can exceed the ungrouped total).
    """
    if group_by == GroupBy.judge:
        return list(row.judges) or [_NONE_KEY]
    key = _KEY_FNS[GroupBy(group_by)](row)
    if key is None:
        return [_OPEN_KEY] if group_by == GroupBy.disposition else [_NONE_KEY]
    return [key]


def _bucket_from_counts(key: str, cases: int, labels: Counter[str]) -> BaseRateBucket:
    """Roll accumulated per-label counts into a bucket's counts and base-rates."""
    resolved = sum(labels.values())
    dispositions = [
        DispositionShare(disposition=Disposition(label), count=n, share=n / resolved)
        for label, n in labels.items()
    ]
    # Most common first; ties broken by the disposition label for a total, stable order.
    dispositions.sort(key=lambda d: (-d.count, d.disposition))
    return BaseRateBucket(
        key=key,
        cases=cases,
        resolved=resolved,
        open=cases - resolved,
        dispositions=dispositions,
    )


def _build_bucket(key: str, rows: list[CorpusRow]) -> BaseRateBucket:
    """Roll a slice of rows into its case/resolved/open counts and disposition base-rates."""
    # CorpusRow uses `use_enum_values`, so `row.disposition` is already the string
    # label (or None) at runtime; `str()` only narrows the static type to match.
    labels = Counter(str(row.disposition) for row in rows if row.disposition is not None)
    return _bucket_from_counts(key, len(rows), labels)


def _nearest_rank(sorted_days: list[int], quantile: float) -> float:
    """The nearest-rank percentile of a non-empty ascending list — deterministic.

    ``rank = ceil(quantile x n)``, with a ``round()`` guard against float artifacts
    (0.9 x 10 evaluates to 9.000000000000002; its ceiling must be rank 9, not 10).
    """
    rank = max(1, math.ceil(round(quantile * len(sorted_days), 9)))
    return float(sorted_days[min(rank, len(sorted_days)) - 1])


def _weighted_nearest_rank(pairs: list[tuple[int, int]], quantile: float) -> float:
    """Nearest-rank percentile over ``(days, weight)`` pairs, ascending by days.

    Equivalent to :func:`_nearest_rank` over the expanded list with each value
    repeated ``weight`` times — a sampled denial's timing counts at the strength
    of the serials it stands for — without materializing the expansion. Integer
    weights, cumulative walk: deterministic.
    """
    total = sum(weight for _, weight in pairs)
    rank = max(1, math.ceil(round(quantile * total, 9)))
    cumulative = 0
    for days, weight in pairs:
        cumulative += weight
        if cumulative >= rank:
            return float(days)
    return float(pairs[-1][0])


def _decision_days(row: CorpusRow) -> int | None:
    """Days filed→decided for a resolved row with a usable date pair, else ``None``.

    Rows missing either date — or with a decision before the filing (a data glitch)
    — are excluded rather than guessed.
    """
    if row.disposition is None or row.date_filed is None or row.date_decided is None:
        return None
    days = (row.date_decided - row.date_filed).days
    return days if days >= 0 else None


def _cert_days(row: CorpusRow) -> int | None:
    """Days filed→cert-stage resolution, keyed on :func:`corpus.resolution_date`.

    The per-Term timing key: a live-channel denial carries ``date_cert_denied``
    with no ``date_decided`` at all, and a granted petition's ``date_decided``
    is the merits termination months later — so docket-termination timing
    (:func:`_decision_days`) would silently drop denials and overstate grants.
    """
    resolved_on = corpus.resolution_date(row)
    if row.disposition is None or row.date_filed is None or resolved_on is None:
        return None
    days = (resolved_on - row.date_filed).days
    return days if days >= 0 else None


def _timing_from_days(day_values: list[int]) -> TimingStats:
    """Roll accumulated filing→decision day counts into :class:`TimingStats`."""
    days = sorted(day_values)
    if not days:
        return TimingStats()
    return TimingStats(
        cases=len(days),
        mean_days=round(sum(days) / len(days), 1),
        median_days=_nearest_rank(days, 0.5),
        p90_days=_nearest_rank(days, 0.9),
    )


def _timing_from_pairs(day_pairs: list[tuple[int, int]]) -> TimingStats:
    """Roll accumulated ``(days, weight)`` pairs into weighted :class:`TimingStats`.

    ``cases`` is the weighted count — the estimated population the timing
    describes, matching the weighted resolved counts it sits beside.
    """
    pairs = sorted(day_pairs)
    if not pairs:
        return TimingStats()
    total = sum(weight for _, weight in pairs)
    return TimingStats(
        cases=total,
        mean_days=round(sum(days * weight for days, weight in pairs) / total, 1),
        median_days=_weighted_nearest_rank(pairs, 0.5),
        p90_days=_weighted_nearest_rank(pairs, 0.9),
    )


def compute_report(conn: sqlite3.Connection, query: AnalyticsQuery) -> AnalyticsReport:
    """Aggregate the corpus rows matching ``query`` into an :class:`AnalyticsReport`.

    One pass over the (court/disposition-narrowed) candidate rows applies the remaining
    filters, tallies the overall base rate, and — when ``group_by`` is set — the per-group
    breakdown. Buckets sort by case count descending, then key, so the output is
    deterministic under ties.
    """
    disposition = Disposition(query.disposition) if query.disposition else None
    matched = [
        row
        for row in corpus.iter_rows(conn, court=query.court, disposition=disposition)
        if _row_matches(row, query)
    ]

    buckets: list[BaseRateBucket] = []
    if query.group_by is not None:
        grouped: dict[str, list[CorpusRow]] = defaultdict(list)
        for row in matched:
            for key in _bucket_keys(row, GroupBy(query.group_by)):
                grouped[key].append(row)
        buckets = [_build_bucket(key, rows) for key, rows in grouped.items()]
        buckets.sort(key=lambda b: (-b.cases, b.key))

    return AnalyticsReport(
        skipped=False,
        group_by=query.group_by,
        total=_build_bucket("", matched),
        buckets=buckets,
    )


def run_analytics(*, corpus_db_path: Path, query: AnalyticsQuery) -> AnalyticsReport:
    """Compute base-rates from the packed corpus, or a skipped report if it is absent.

    Graceful before a corpus pull (mirrors :func:`fedcourtsai.validate.run_scope_audit`):
    a missing corpus yields ``skipped=True`` with an empty total rather than an error.
    """
    if not corpus_db_path.exists():
        return AnalyticsReport(skipped=True, group_by=query.group_by)
    with corpus.connect(corpus_db_path) as conn:
        return compute_report(conn, query)


# A key override for the reader-facing by-originating-court section: the tracked
# circuit id when the linkage resolved, else the raw `LowerCourt` name the live
# channel kept — so state courts appear by name instead of vanishing into `(none)`.
def _originating_court_or_name(row: CorpusRow) -> str | None:
    return row.originating_court or row.originating_court_name


@dataclass(frozen=True)
class _SectionSpec:
    """One curated statpack breakdown: its filters, population, and dimension.

    ``live_slice`` restricts the section to rows the supremecourt.gov channel
    wrote (:func:`corpus.is_live_slice`) — the predictor-facing populations,
    whose dispositions come from parsed proceedings rather than the frozen bulk
    import. ``weighted`` counts each row ``sample_weight`` times so the
    historical walker's denial sampling does not bias the rates. ``key_fn``
    overrides the dimension's stock key function where a section wants richer
    keys under the same ``group_by``. ``row_filter`` narrows the population
    beyond the court/live/cert flags (the salience-band section restricts to the
    paid scored segment) — a row failing it joins no bucket.
    """

    title: str
    court: str | None
    cert_stage: bool
    live_slice: bool
    weighted: bool
    group_by: GroupBy
    key_fn: Callable[[CorpusRow], str | None] | None = None
    row_filter: Callable[[CorpusRow], bool] | None = None


# The curated breakdowns, named individually so the two published artifacts
# compose their own tuple from one definition apiece: a cut computed for both
# is the *same* spec, not a copy that can drift.
_BY_COURT = _SectionSpec("Cases by court", None, False, False, False, GroupBy.court)
_SCOTUS_BY_ERA = _SectionSpec("SCOTUS cases by era", "scotus", False, False, False, GroupBy.era)
# The same two cuts, reweighted, for the court-facing pack. Raw is defensible in
# the statpack, whose reader is calibrating against a known frame; it is not
# defensible in a citable artifact. Almost every labeled SCOTUS row is live
# slice, where legacy walk rows keep one denial in ten (`sample_weight`
# reconstructs the rest), so a raw disposition split
# there overstates the grant family several-fold — while a bulk-import circuit
# row carries weight 1 and is unaffected, which is why reweighting is the whole
# fix rather than a trade.
_BY_COURT_WEIGHTED = replace(_BY_COURT, weighted=True)
_SCOTUS_BY_ERA_WEIGHTED = replace(_SCOTUS_BY_ERA, weighted=True)
# The calibration anchor the predict prompts point at (and ops reads by its
# cert_stage + disposition shape): modern Term-prefixed discretionary-cert
# dockets, live slice, denial-reweighted — the trustworthy grant/deny split.
_CERT_BY_DISPOSITION = _SectionSpec(
    "Modern discretionary-cert petitions by disposition",
    "scotus",
    True,
    True,
    True,
    GroupBy.disposition,
)
_CERT_BY_CIRCUIT = _SectionSpec(
    "Modern cert petitions by originating circuit",
    "scotus",
    True,
    True,
    True,
    GroupBy.originating_court,
)
_CERT_BY_RELIST = _SectionSpec(
    "Cert petitions by relist count", "scotus", True, True, True, GroupBy.relist_bucket
)
_CERT_BY_CVSG = _SectionSpec(
    "Cert petitions by CVSG status", "scotus", True, True, True, GroupBy.cvsg
)
# The segment base rate the salience program turns on: the paid scored segment
# split by sal-v1 band. Pack-wide (blended across Terms) for the human board;
# the leakage-safe per-Term counterpart is `StatPackTerm.segments`.
# The same two cuts over the **paid scored segment** — the population the salience
# gate actually predicts on. The pooled versions above include IFP petitions,
# which relist far less often and have never drawn a CVSG in this corpus, so their
# levels sit below what a selected petition faces. A court-facing artifact wants
# the pooled view; a predict cell needs its own.
_CERT_BY_RELIST_PAID = _SectionSpec(
    "Cert petitions by relist count (paid scored segment)",
    "scotus",
    True,
    True,
    True,
    GroupBy.relist_bucket,
    row_filter=_is_scored_segment_row,
)
_CERT_BY_CVSG_PAID = _SectionSpec(
    "Cert petitions by CVSG status (paid scored segment)",
    "scotus",
    True,
    True,
    True,
    GroupBy.cvsg,
    row_filter=_is_scored_segment_row,
)
_CERT_BY_SALIENCE_BAND = _SectionSpec(
    "Cert petitions by salience band",
    "scotus",
    True,
    True,
    True,
    GroupBy.salience_band,
    row_filter=_is_scored_segment_row,
)
_PETITIONS_BY_ORIGINATING_COURT = _SectionSpec(
    "Petitions by originating court (incl. state courts)",
    "scotus",
    True,
    True,
    False,
    GroupBy.originating_court,
    key_fn=_originating_court_or_name,
)
# The same reader cut, denial-reweighted, for the court-facing artifact. It is a
# separate spec rather than a flag on the one above because the two answer
# different questions: the statpack's raw version reports rows on hand, while a
# published state-court grant rate has to estimate the population — over the
# walker's frame an unweighted rate inflates the grant family several-fold,
# since denials are sampled and every non-denial is kept. This is the only cut
# in which a state court appears, so it is the one that must be reweighted.
_PETITIONS_BY_ORIGINATING_COURT_WEIGHTED = _SectionSpec(
    "Petitions by originating court (incl. state courts)",
    "scotus",
    True,
    True,
    True,
    GroupBy.originating_court,
    key_fn=_originating_court_or_name,
)
# Paid petitions number from 1 and IFP petitions from 5001, so the fee class is
# exact from the docket number — the coarsest cut in the cert docket, and one a
# reader of the court-facing artifact expects beside the circuit and relist cuts.
_CERT_BY_FEE_CLASS = _SectionSpec(
    "Cert petitions by fee class (paid vs IFP)",
    "scotus",
    True,
    True,
    True,
    GroupBy.fee_class,
)

# The breakdowns the statpack publishes. Two populations, deliberately side by
# side: the full-corpus overview (court composition, era spread — includes the
# frozen bulk import, labeled so in the render) for human context, and the
# live-slice weighted cuts the predict/evaluate prompts anchor on. The per-Term
# detail is not a section — it is the richer `terms` array, built in
# `build_statpack`.
_STATPACK_SECTIONS: tuple[_SectionSpec, ...] = (
    _BY_COURT,
    _SCOTUS_BY_ERA,
    _CERT_BY_DISPOSITION,
    _CERT_BY_CIRCUIT,
    _CERT_BY_RELIST_PAID,
    _CERT_BY_CVSG_PAID,
    _CERT_BY_SALIENCE_BAND,
    _PETITIONS_BY_ORIGINATING_COURT,
)

# The breakdowns the court-facing docket pack publishes: the same docket
# composition cuts, plus the fee-class split, minus the salience band — a band
# is a statement about which petitions this project predicts, which is exactly
# the kind of claim that artifact excludes. Every cert cut here is weighted, so
# each published rate estimates the population rather than the walked sample.
_DOCKET_SECTIONS: tuple[_SectionSpec, ...] = (
    _BY_COURT_WEIGHTED,
    _SCOTUS_BY_ERA_WEIGHTED,
    _CERT_BY_DISPOSITION,
    _CERT_BY_CIRCUIT,
    _CERT_BY_RELIST,
    _CERT_BY_CVSG,
    _PETITIONS_BY_ORIGINATING_COURT_WEIGHTED,
    _CERT_BY_FEE_CLASS,
)


class _Slice:
    """Streaming accumulator for one published slice (the whole set, a bucket, a Term).

    The unit :func:`_scan_corpus` fills as it streams: each row updates the
    counters of every slice it belongs to, and the buckets/timing are rolled up
    from the counters afterwards, so no row list is materialized.

    Every add records both raw and weighted counters (weight =
    ``sample_weight`` or 1, so unweighted-capture rows count once); the caller
    picks the view at roll-up. ``cert_timing`` keys the timing pairs on the
    cert-stage resolution date instead of docket termination — the per-Term
    slices use it so live-channel denials (dated only by ``date_cert_denied``)
    are not silently dropped.
    """

    __slots__ = (
        "cases",
        "cert_timing",
        "dated_resolved",
        "day_pairs",
        "labels",
        "machine_readable_resolved",
        "weighted_cases",
        "weighted_labels",
    )

    def __init__(self, *, cert_timing: bool = False) -> None:
        self.cert_timing = cert_timing
        self.cases = 0
        self.weighted_cases = 0
        self.labels: Counter[str] = Counter()
        self.weighted_labels: Counter[str] = Counter()
        self.day_pairs: list[tuple[int, int]] = []
        self.machine_readable_resolved = 0
        self.dated_resolved = 0

    def add(self, row: CorpusRow) -> None:
        # Writers guarantee weights >= 1, but the blob is external input to this
        # pure function — floor it so a corrupt 0 can never zero a denominator.
        weight = max(1, row.sample_weight if row.sample_weight is not None else 1)
        self.cases += 1
        self.weighted_cases += weight
        if row.disposition is not None:
            self.labels[row.disposition] += 1
            self.weighted_labels[row.disposition] += weight
            # The back-testable slice and its dated share: a machine-readable
            # disposition is scoreable, and a resolution date is what lets the
            # time-masked replay clock anchor the row.
            if is_machine_readable(Disposition(row.disposition)):
                self.machine_readable_resolved += 1
                if corpus.resolution_date(row) is not None:
                    self.dated_resolved += 1
        days = _cert_days(row) if self.cert_timing else _decision_days(row)
        if days is not None:
            self.day_pairs.append((days, weight))

    def bucket(self, key: str, *, weighted: bool = False) -> BaseRateBucket:
        if weighted:
            return _bucket_from_counts(key, self.weighted_cases, self.weighted_labels)
        return _bucket_from_counts(key, self.cases, self.labels)

    def timing(self, *, weighted: bool = False) -> TimingStats:
        if weighted:
            return _timing_from_pairs(self.day_pairs)
        return _timing_from_days([days for days, _ in self.day_pairs])


class _TermAcc:
    """Streaming accumulator for one October Term's live-slice cert population."""

    __slots__ = ("classes", "grant_days", "grants", "overall", "prefixes", "segments")

    def __init__(self) -> None:
        self.overall = _Slice(cert_timing=True)
        self.classes: dict[FeeClass, _Slice] = {
            FeeClass.paid: _Slice(cert_timing=True),
            FeeClass.ifp: _Slice(cert_timing=True),
        }
        # One slice per frozen sal-v1 band over the paid scored segment — the
        # leakage-safe per-Term segment base rate. Pre-seeded for every band so a
        # Term with no rows in a band still emits that band (a stable JSON shape).
        self.segments: dict[str, _Slice] = {band: _Slice() for band in salience_bands()}
        # The same bands on a **risk-set** denominator: every row that ever
        # *reached* a band, not only those that ended in it. See `add`.
        self.prefixes: dict[str, _Slice] = {band: _Slice() for band in salience_bands()}
        self.grants = 0
        self.grant_days: list[int] = []

    def add(self, row: CorpusRow) -> None:
        self.overall.add(row)
        fee = _fee_class(row)
        if fee is not None:
            self.classes[fee].add(row)
        if _is_scored_segment_row(row):
            band = salience_band(row)
            self.segments[band].add(row)
            # A band is monotone non-decreasing over a petition's life: the
            # distribution count is max-latched and a CVSG date, once set, stays
            # set. So "this petition has reached band b" is the same event as
            # "its final band is b or stronger", and the risk set for b is every
            # row at b or above it. `salience_bands()` is ordered strongest-first,
            # so a row joins its own band's prefix slice and every weaker one.
            order = salience_bands()
            for weaker in order[order.index(band) :]:
                self.prefixes[weaker].add(row)
        if row.disposition in _GRANT_LABELS:
            self.grants += 1
            if row.date_filed is not None and row.date_cert_granted is not None:
                days = (row.date_cert_granted - row.date_filed).days
                if days >= 0:
                    self.grant_days.append(days)


# The parsed-ask vocabulary, as stored strings — the membership check that keeps
# a corrupt kind value from silently escaping the published kind split.
_APPLICATION_KINDS = frozenset(kind.value for kind in ApplicationKind)


class _InterimAcc:
    """Streaming accumulator for one slice of the interim application docket.

    Counts are raw throughout — the live channel polls every application it
    discovers, so no row stands in for another and nothing here is reweighted
    (``sample_weight`` is deliberately unread; the denial-sampling frame covers
    cert petitions only, and every application row is written at weight 1 — if
    a sampling design ever reaches applications, this accumulator must learn
    to weight).
    The kind tally keeps ``unknown`` (parsed, ask unreadable) apart from
    ``unparsed`` (never application-parsed), so a coverage gap never masquerades
    as a value; the resolved/granted counters and the escalation signals read the
    **substantive** slice only, because that is the only slice any published rate
    or ladder claim may be computed over.
    """

    __slots__ = (
        "applications",
        "kinds",
        "referred_to_court",
        "response_requested",
        "substantive_granted",
        "substantive_resolved",
        "unparsed",
        "with_amicus",
    )

    def __init__(self) -> None:
        self.applications = 0
        self.kinds: Counter[str] = Counter()
        self.unparsed = 0
        self.substantive_resolved = 0
        self.substantive_granted = 0
        self.response_requested = 0
        self.referred_to_court = 0
        self.with_amicus = 0

    def add(self, row: CorpusRow) -> None:
        self.applications += 1
        if row.application_kind is None:
            self.unparsed += 1
            return
        # The blob is external input to this pure function: a kind string
        # outside the vocabulary counts with the unreadable asks rather than
        # vanishing, so the kind split always sums to `applications`.
        kind = (
            row.application_kind
            if row.application_kind in _APPLICATION_KINDS
            else ApplicationKind.unknown.value
        )
        self.kinds[kind] += 1
        if kind != ApplicationKind.substantive.value:
            return
        if row.disposition is not None:
            disposition = Disposition(row.disposition)
            # Machine-readable labels only, as the cert accumulators count and
            # docs/salience.md states the interim rule: an application counts as
            # resolved only when the interim vocabulary matched its disposing
            # entry, so an `other` (or channel-crossed) label joins the visibly
            # unresolved residue instead of entering the rate as a silent denial.
            # The binary outcome mapping owns "what counts as granted"; the
            # interim vocabulary (granted / denied / withdrawn / dismissed)
            # projects through the same function as cert scoring.
            if is_machine_readable(disposition):
                self.substantive_resolved += 1
                self.substantive_granted += granted_flag(disposition)
        if row.response_requested:
            self.response_requested += 1
        if row.referred_to_court:
            self.referred_to_court += 1
        if row.amicus_briefs is not None and row.amicus_briefs > 0:
            self.with_amicus += 1

    def merge(self, other: _InterimAcc) -> None:
        """Fold another slice's counters into this one (for the pack-level totals)."""
        self.applications += other.applications
        self.kinds.update(other.kinds)
        self.unparsed += other.unparsed
        self.substantive_resolved += other.substantive_resolved
        self.substantive_granted += other.substantive_granted
        self.response_requested += other.response_requested
        self.referred_to_court += other.referred_to_court
        self.with_amicus += other.with_amicus


def _interim_counts(acc: _InterimAcc) -> dict[str, Any]:
    """One interim slice's shared count block, keyed by the model's field names.

    ``dict`` rather than a model so the same roll-up feeds both
    :class:`StatPackInterim` and :class:`StatPackInterimTerm` without a copy that
    could drift. The rate divides raw counts and exists only where something
    substantive resolved — an all-denied slice has a real 0%, an unresolved one
    no rate at all.
    """
    return {
        "applications": acc.applications,
        "extension": acc.kinds[ApplicationKind.extension.value],
        "substantive": acc.kinds[ApplicationKind.substantive.value],
        "unknown": acc.kinds[ApplicationKind.unknown.value],
        "unparsed": acc.unparsed,
        "substantive_resolved": acc.substantive_resolved,
        "substantive_granted": acc.substantive_granted,
        "substantive_grant_rate": (
            acc.substantive_granted / acc.substantive_resolved if acc.substantive_resolved else None
        ),
        "response_requested": acc.response_requested,
        "referred_to_court": acc.referred_to_court,
        "with_amicus": acc.with_amicus,
    }


def _interim_section(accs: dict[int, _InterimAcc]) -> StatPackInterim | None:
    """Roll the per-application-Term accumulators into the interim stage section.

    ``None`` when the corpus holds no application rows: a stage section is shown
    only once its feed exists, so the pack omits it entirely rather than emitting
    an empty scaffold — and the serializer drops the absent section, so such a
    pack carries no ``interim`` key at all.
    """
    if not accs:
        return None
    total = _InterimAcc()
    for acc in accs.values():
        total.merge(acc)
    terms = [
        StatPackInterimTerm(term=year, **_interim_counts(accs[year]))
        for year in sorted(accs, reverse=True)
    ]
    return StatPackInterim(terms=terms, **_interim_counts(total))


# The merits-judgment vocabulary, as stored strings — the membership check that
# keeps a corrupt column value from silently entering the published distribution
# (the TEXT column's readers re-validate, as `_APPLICATION_KINDS` does for the
# ask column; an out-of-vocabulary value counts as unparsed, since there is no
# `unknown` member to fold it into).
_JUDGMENT_VALUES = frozenset(judgment.value for judgment in Judgment)


class _MeritsAcc:
    """Streaming accumulator for one slice of the granted-merits docket.

    Counts are raw throughout — a grant is always ingested with certainty
    (weight 1 under the denial-sampling frame), so no row stands in for
    another and ``sample_weight`` is deliberately unread. ``granted`` counts
    the whole cohort and ``parsed`` the rows the merits backfill could read, so
    the published rate's coverage is visible beside it; the disturbed counter
    projects each judgment through
    :func:`fedcourtsai.pipeline.judgment.judgment_disturbed` — the single
    definition of "disturbed" the merits baseline shares
    (:func:`fedcourtsai.pipeline.evaluate.merits_base_rate` pools exactly
    these per-Term counts, strictly-prior). The cohort admitted here is the
    scored population itself: the caller
    (:func:`fedcourtsai.corpus.opens_merits_proceeding`) keeps out the grants
    that decide in the cert order, so no near-certain GVR vacatur reaches a
    counter.
    """

    __slots__ = ("disturbed", "granted", "judgments", "parsed")

    def __init__(self) -> None:
        self.granted = 0
        self.parsed = 0
        self.judgments: Counter[str] = Counter()
        self.disturbed = 0

    def add(self, row: CorpusRow) -> None:
        self.granted += 1
        value = row.merits_judgment
        # The blob is external input to this pure function: an out-of-vocabulary
        # value counts with the never-parsed rows rather than entering the
        # distribution, so the six judgment counts always sum to `parsed`.
        if value is None or value not in _JUDGMENT_VALUES:
            return
        self.parsed += 1
        self.judgments[value] += 1
        if judgment_disturbed(Judgment(value)):
            self.disturbed += 1

    def merge(self, other: _MeritsAcc) -> None:
        """Fold another slice's counters into this one (for the pack-level totals)."""
        self.granted += other.granted
        self.parsed += other.parsed
        self.judgments.update(other.judgments)
        self.disturbed += other.disturbed


def _merits_counts(acc: _MeritsAcc) -> dict[str, Any]:
    """One merits slice's shared count block, keyed by the model's field names.

    ``dict`` rather than a model so the same roll-up feeds both
    :class:`StatPackMerits` and :class:`StatPackMeritsTerm` without a copy that
    could drift. The rate divides raw counts and exists only where something
    parsed — an all-affirmed slice has a real 0%, an unparsed one no rate.
    """
    return {
        "granted": acc.granted,
        "parsed": acc.parsed,
        "affirmed": acc.judgments[Judgment.affirmed.value],
        "reversed": acc.judgments[Judgment.reversed.value],
        "vacated": acc.judgments[Judgment.vacated.value],
        "affirmed_in_part": acc.judgments[Judgment.affirmed_in_part.value],
        "dig": acc.judgments[Judgment.dig.value],
        "equally_divided": acc.judgments[Judgment.equally_divided.value],
        "disturbed": acc.disturbed,
        "disturbed_rate": acc.disturbed / acc.parsed if acc.parsed else None,
    }


def _merits_section(accs: dict[int, _MeritsAcc]) -> StatPackMerits | None:
    """Roll the per-grant-Term accumulators into the merits stage section.

    ``None`` while no row carries a parsed judgment — a stage section is shown
    only once its feed exists, exactly as the interim section joins on
    application rows, and the serializer drops the absent section so such a
    pack carries no ``merits`` key at all. The pack-level totals cover the
    whole granted cohort (so coverage is honest), while the per-Term rows keep
    to Terms with at least one parsed judgment — a Term of granted-but-unparsed
    rows would render as pure noise.
    """
    total = _MeritsAcc()
    for acc in accs.values():
        total.merge(acc)
    if total.parsed == 0:
        return None
    terms = [
        StatPackMeritsTerm(term=year, **_merits_counts(accs[year]))
        for year in sorted(accs, reverse=True)
        if accs[year].parsed
    ]
    return StatPackMerits(terms=terms, **_merits_counts(total))


# How each (Term, stream) cursor contributes to its fee class's census: the count
# of docketed serials from the stream's base through the cursor. The forward
# poller's and the historical walker's cursors cover the same serial space, so a
# class's census is the max over its stream family, and completeness is read
# from whichever family cursor is furthest along.
_STREAM_CLASSES: dict[str, tuple[FeeClass, int]] = {
    "paid": (FeeClass.paid, 1),
    "historical-paid": (FeeClass.paid, 1),
    "ifp": (FeeClass.ifp, IFP_SERIAL_BASE),
    "historical-ifp": (FeeClass.ifp, IFP_SERIAL_BASE),
}


def _census(
    cursor_rows: list[tuple[int, str, int, int | None]],
) -> dict[tuple[int, FeeClass], tuple[int, bool]]:
    """Per (Term, fee class): ``(filings, complete)`` from the discovery cursors.

    Filings = serials from the stream base through the family's furthest cursor
    (clamped at zero for a cursor still below its base) — exact for docketed
    numbers, a slight upper bound on real petitions (withheld serials count).
    Complete = the furthest cursor carries a frontier stamp at exactly its
    serial: the walk observed the stream's end there and nothing has been
    served past it since. A never-probed (Term, class) is simply absent.

    Keys are four-digit October-Term years: the cursor table stores the
    two-digit docket-prefix form (the e-filing era is unambiguously 2000+),
    normalized here to match :func:`corpus.scotus_term_year`'s row keys. One
    horizon to note: ``scotus_term_year`` folds prefixes >= 30 into 1900+, so
    at OT2030 the two functions diverge and one Term would split into two
    entries — the century heuristic needs revisiting before then.
    """
    census: dict[tuple[int, FeeClass], tuple[int, bool]] = {}
    for prefix, stream, last_serial, frontier_serial in cursor_rows:
        term = 2000 + prefix
        mapped = _STREAM_CLASSES.get(stream)
        if mapped is None:
            continue
        fee, base = mapped
        filings = max(0, last_serial - base + 1)
        complete = frontier_serial is not None and frontier_serial == last_serial
        stored = census.get((term, fee))
        if stored is None or filings > stored[0]:
            census[(term, fee)] = (filings, complete)
        elif filings == stored[0] and complete and not stored[1]:
            # Equal cursors (both walkers at the same serial): completeness is a
            # fact about the serial space, so either stream's stamp confirms it.
            census[(term, fee)] = (filings, True)
    return census


def _term_entry(
    year: int, acc: _TermAcc | None, census: dict[tuple[int, FeeClass], tuple[int, bool]]
) -> StatPackTerm:
    """Assemble one Term's statpack entry from its accumulator and the census.

    ``acc`` is ``None`` for a cursor-only Term (probed, nothing ingested — e.g.
    a Term whose walk has only served sampled-out denials so far): the entry
    still appears, carrying its census with zero counts, so coverage is visible.
    """
    acc = acc or _TermAcc()
    classes = []
    for fee in (FeeClass.paid, FeeClass.ifp):
        entry = acc.classes[fee]
        filings_complete = census.get((year, fee))
        weighted = entry.bucket("", weighted=True)
        classes.append(
            StatPackTermClass(
                fee_class=fee,
                filings=filings_complete[0] if filings_complete is not None else None,
                complete=filings_complete[1] if filings_complete is not None else False,
                ingested=entry.cases,
                resolved=entry.bucket("").resolved,
                weighted_resolved=weighted.resolved,
                est_grant_rate=_grant_family_share(weighted),
                dispositions=weighted.dispositions,
                timing=entry.timing(weighted=True),
            )
        )
    segments = []
    for band in salience_bands():
        entry = acc.segments[band]
        weighted = entry.bucket("", weighted=True)
        prefix_acc = acc.prefixes[band]
        prefix = prefix_acc.bucket("", weighted=True)
        segments.append(
            StatPackTermSegment(
                band=band,
                ingested=entry.cases,
                resolved=entry.bucket("").resolved,
                weighted_resolved=weighted.resolved,
                est_grant_rate=_grant_family_share(weighted),
                prefix_resolved=prefix_acc.bucket("").resolved,
                prefix_weighted_resolved=prefix.resolved,
                prefix_est_grant_rate=_grant_family_share(prefix),
            )
        )
    grant_days = sorted(acc.grant_days)
    base_rates = acc.overall.bucket(str(year), weighted=True)
    return StatPackTerm(
        term=year,
        ingested=acc.overall.cases,
        base_rates=base_rates,
        est_grant_family_rate=_grant_family_share(base_rates),
        timing=acc.overall.timing(weighted=True),
        classes=classes,
        grants=acc.grants,
        salience_version=SALIENCE_VERSION,
        segments=segments,
        median_days_to_grant=_nearest_rank(grant_days, 0.5) if grant_days else None,
    )


@dataclass(frozen=True)
class _CorpusScan:
    """The counters one streamed pass over the corpus fills, for any published artifact.

    ``sections`` holds one ``bucket key -> slice`` map per spec, so a caller rolls
    its own sections up without re-reading the corpus. The scan carries the
    ``specs`` it ran under rather than trusting a caller to re-supply them: both
    artifacts' tuples are the same length, so a mismatched pairing would zip
    cleanly and publish a section's buckets under another's title — which in the
    docket pack would mean rendering the salience band the artifact exists to
    exclude. ``terms`` and ``cursor_rows`` back the per-Term census, which both
    published artifacts carry. ``interim`` holds the application-docket
    accumulators (keyed by application-Term year) and ``merits`` the
    granted-cohort accumulators (keyed by grant-Term year); only the statpack
    rolls either into a section — the docket pack ignores them by design.
    """

    specs: tuple[_SectionSpec, ...]
    overall: _Slice
    live_slice: _Slice
    sections: tuple[defaultdict[str, _Slice], ...]
    terms: dict[int, _TermAcc]
    interim: dict[int, _InterimAcc]
    merits: dict[int, _MeritsAcc]
    cursor_rows: list[tuple[int, str, int, int | None]]
    corpus_through: date | None


def _accumulate_scotus_terms(
    row: CorpusRow,
    row_is_live: bool,
    term_accs: dict[int, _TermAcc],
    interim_accs: dict[int, _InterimAcc],
    merits_accs: dict[int, _MeritsAcc],
) -> None:
    """Offer one SCOTUS row to the per-Term accumulators of every stage axis.

    A docket number parses as the cert ``YY-NNNN`` form or the application
    ``YYAnnn`` form, never both, so a row contributes to at most one of those
    stage populations. The cert entries keep their live-slice restriction; the
    interim axis keys on the form alone, which is the live channel's
    addressable population either way. The merits axis is a *projection* of the
    cert population rather than a third form — the rows whose grant opens a
    merits proceeding (:func:`fedcourtsai.corpus.opens_merits_proceeding`),
    keyed on the Term of the grant — so such a row feeds both a cert Term entry
    and a merits one, describing two different stages of the same case. A GVR
    or summary reversal is a grant that decides in the cert order itself, so it
    contributes no merits row: its vacatur is a cert-stage disposition, and
    pooling it would put a near-certain disturbance into the rate that scores
    merits forecasts, from a case no one was asked to predict.
    """
    if row_is_live:
        year = corpus.scotus_term_year(row.docket_number)
        if year is not None:
            term_accs.setdefault(year, _TermAcc()).add(row)
    application_year = corpus.scotus_application_term_year(row.docket_number)
    if application_year is not None:
        interim_accs.setdefault(application_year, _InterimAcc()).add(row)
    if corpus.opens_merits_proceeding(row) and row.date_cert_granted is not None:
        grant_year = grant_term_year(row.date_cert_granted)
        merits_accs.setdefault(grant_year, _MeritsAcc()).add(row)


def _scan_corpus(corpus_db_path: Path, specs: tuple[_SectionSpec, ...]) -> _CorpusScan:
    """Stream every corpus row once, updating every slice the row belongs to.

    The corpus is millions of rows, so a published artifact gets **one pass**: each
    row is offered to each spec (court / live-slice / cert-stage / row filter), to
    the pack-wide totals, and to its October Term's accumulator. No row list is
    materialized and no per-section re-scan runs.
    """
    overall = _Slice()
    live_slice_totals = _Slice()
    # The corpus's own high-water mark, so an artifact can state its vintage
    # without reading a clock and stay a pure function of its input.
    corpus_through: date | None = None
    section_slices: tuple[defaultdict[str, _Slice], ...] = tuple(defaultdict(_Slice) for _ in specs)
    term_accs: dict[int, _TermAcc] = {}
    interim_accs: dict[int, _InterimAcc] = {}
    merits_accs: dict[int, _MeritsAcc] = {}
    with corpus.connect(corpus_db_path) as conn:
        cursor_rows = corpus.live_cursor_rows(conn)
        for row in corpus.iter_rows(conn):
            overall.add(row)
            if row.last_pulled is not None and (
                corpus_through is None or row.last_pulled > corpus_through
            ):
                corpus_through = row.last_pulled
            row_is_live = corpus.is_live_slice(row)
            if row_is_live:
                live_slice_totals.add(row)
            for spec, slices in zip(specs, section_slices, strict=True):
                if spec.court is not None and row.court != spec.court:
                    continue
                if spec.live_slice and not row_is_live:
                    continue
                if spec.cert_stage and not corpus.is_modern_cert(row):
                    continue
                if spec.row_filter is not None and not spec.row_filter(row):
                    continue
                keys = (
                    _bucket_keys(row, spec.group_by)
                    if spec.key_fn is None
                    else [spec.key_fn(row) or _NONE_KEY]
                )
                for key in keys:
                    slices[key].add(row)
            if row.court == "scotus":
                _accumulate_scotus_terms(row, row_is_live, term_accs, interim_accs, merits_accs)
    return _CorpusScan(
        specs=specs,
        corpus_through=corpus_through,
        overall=overall,
        live_slice=live_slice_totals,
        sections=section_slices,
        terms=term_accs,
        interim=interim_accs,
        merits=merits_accs,
        cursor_rows=cursor_rows,
    )


def _sections(
    specs: tuple[_SectionSpec, ...], scan: _CorpusScan | None = None
) -> list[StatPackSection]:
    """Roll a scan's accumulated slices into one :class:`StatPackSection` per spec.

    ``scan`` is ``None`` when no corpus is present: the sections still render as
    empty scaffolding from ``specs``, so an artifact's shape is stable whether the
    corpus is merely absent or present-but-empty. With a scan present its own
    ``specs`` win — a scan can only be described by the specs it accumulated
    under. Buckets sort by case count descending, then key, so ties order
    deterministically.
    """
    slice_maps: tuple[defaultdict[str, _Slice], ...] = (
        scan.sections if scan is not None else tuple(defaultdict(_Slice) for _ in specs)
    )
    if scan is not None:
        specs = scan.specs
    sections = []
    for spec, slices in zip(specs, slice_maps, strict=True):
        buckets = [entry.bucket(key, weighted=spec.weighted) for key, entry in slices.items()]
        buckets.sort(key=lambda b: (-b.cases, b.key))
        sections.append(
            StatPackSection(
                title=spec.title,
                court=spec.court,
                cert_stage=spec.cert_stage,
                live_slice=spec.live_slice,
                weighted=spec.weighted,
                group_by=spec.group_by,
                buckets=buckets,
            )
        )
    return sections


def build_statpack(*, corpus_db_path: Path) -> StatPack:
    """Roll the whole corpus into a base-rate statpack, or the empty pack if it is absent.

    Deterministic and offline — a pure function of the corpus — so reruns reproduce it
    byte for byte. Mirrors ``fedcourts backtest`` / ``leaderboard``: an absent corpus
    (run before a corpus pull) yields the empty zero-count pack rather than an error.

    Two populations, kept apart by section flags: the full-corpus overview
    (bulk import included) for composition context, and the live-slice weighted
    cuts + per-Term entries the predict/evaluate prompts anchor on. The ``terms``
    array iterates the union of row-derived Terms and cursor-table Terms, so a
    Term the walkers have probed but not yet populated still shows its census.
    Two more populations ride beside them as their own stage sections: the
    interim application docket (``interim``), present only once the corpus
    holds application rows, and the granted-merits cohort (``merits``), present
    only once a row carries a parsed merits judgment.
    """
    if not corpus_db_path.exists():
        return StatPack(sections=_sections(_STATPACK_SECTIONS))
    scan = _scan_corpus(corpus_db_path, _STATPACK_SECTIONS)
    overall = scan.overall
    live_slice_totals = scan.live_slice
    term_accs = scan.terms
    sections = _sections(_STATPACK_SECTIONS, scan)
    census = _census(scan.cursor_rows)
    term_years = sorted({*term_accs, *(term for term, _ in census)}, reverse=True)
    total = overall.bucket("")
    live_total = live_slice_totals.bucket("")
    census_values = [filings for filings, _ in census.values()]
    return StatPack(
        corpus_rows=overall.cases,
        resolved=total.resolved,
        open=total.open,
        machine_readable_resolved=overall.machine_readable_resolved,
        dated_resolved=overall.dated_resolved,
        overall=total,
        timing=overall.timing(),
        coverage=StatPackCoverage(
            live_slice_rows=live_slice_totals.cases,
            live_slice_resolved=live_total.resolved,
            census_filings=sum(census_values) if census_values else None,
        ),
        sections=sections,
        terms=[_term_entry(year, term_accs.get(year), census) for year in term_years],
        interim=_interim_section(scan.interim),
        merits=_merits_section(scan.merits),
    )


def _docket_term_entry(
    year: int, acc: _TermAcc | None, census: dict[tuple[int, FeeClass], tuple[int, bool]]
) -> DocketPackTerm:
    """Assemble one Term's docket-pack census, pooling the paid and IFP streams.

    ``filings`` sums the two streams' censuses (``None`` only when neither has
    been probed) and ``complete`` holds when every **probed** stream reached its
    observed frontier. An unprobed stream is absent from the sum and cannot make
    ``complete`` false, so a Term walked on one stream alone can read complete
    over a census that covers half the docket — read ``filings`` alongside it.
    ``acc`` is ``None`` for a cursor-only Term — probed, nothing ingested — which
    still appears with zero counts so the coverage gap is visible.
    """
    probed = [census[(year, fee)] for fee in (FeeClass.paid, FeeClass.ifp) if (year, fee) in census]
    acc = acc or _TermAcc()
    raw = acc.overall.bucket("")
    weighted = acc.overall.bucket("", weighted=True)
    grant_days = sorted(acc.grant_days)
    family_rate = _grant_family_share(weighted)
    return DocketPackTerm(
        term=year,
        filings=sum(filings for filings, _ in probed) if probed else None,
        complete=bool(probed) and all(complete for _, complete in probed),
        ingested=acc.overall.cases,
        resolved=raw.resolved,
        weighted_resolved=weighted.resolved,
        est_grant_rate=family_rate,
        est_grant_family_rate=family_rate,
        dispositions=weighted.dispositions,
        grants=acc.grants,
        median_days_to_grant=_nearest_rank(grant_days, 0.5) if grant_days else None,
        dated_grants=len(grant_days),
    )


def build_docket_pack(*, corpus_db_path: Path) -> DocketPack:
    """Roll the corpus into the court-facing docket pack, or the empty pack if absent.

    The same streamed pass and the same section machinery as
    :func:`build_statpack`, over :data:`_DOCKET_SECTIONS` — the docket-composition
    cuts plus the fee-class split, without the salience band — and a per-Term
    census that pools the fee streams and drops the salience segments. Nothing
    here reads a prediction, an evaluation, or the leaderboard. Deterministic and
    offline, so reruns reproduce it byte for byte.
    """
    if not corpus_db_path.exists():
        return DocketPack(sections=_sections(_DOCKET_SECTIONS))
    scan = _scan_corpus(corpus_db_path, _DOCKET_SECTIONS)
    census = _census(scan.cursor_rows)
    term_years = sorted({*scan.terms, *(term for term, _ in census)}, reverse=True)
    total = scan.overall.bucket("")
    live_total = scan.live_slice.bucket("")
    census_values = [filings for filings, _ in census.values()]
    return DocketPack(
        corpus_through=scan.corpus_through,
        corpus_rows=scan.overall.cases,
        resolved=total.resolved,
        open=total.open,
        coverage=StatPackCoverage(
            live_slice_rows=scan.live_slice.cases,
            live_slice_resolved=live_total.resolved,
            census_filings=sum(census_values) if census_values else None,
        ),
        sections=_sections(_DOCKET_SECTIONS, scan),
        terms=[_docket_term_entry(year, scan.terms.get(year), census) for year in term_years],
    )


# How many buckets a section's Markdown table shows; the JSON carries them all.
# Sized for the state-court originating-court cut, whose long tail is real data
# but unreadable as a table.
_MARKDOWN_BUCKETS = 25


def _scope_line(section: StatPackSection) -> str:
    """The self-describing scope sentence under a section heading."""
    scope = "all courts" if section.court is None else section.court
    if section.cert_stage:
        scope += ", modern discretionary-cert dockets"
    if section.live_slice:
        scope += ", live/historical slice"
    else:
        scope += "; includes the frozen bulk import"
    if section.weighted:
        scope += "; counts are denial-reweighted estimates"
    return f"_Scope: {scope}._"


def _section_tables(sections: list[StatPackSection], *, sample_size: bool = False) -> list[str]:
    """One heading, scope line, and capped Markdown table per curated breakdown.

    Shared by both published base-rate artifacts, so a section computed for each
    renders identically. ``sample_size`` appends the base rate's denominator to
    the cell, so a rate quoted out of the table keeps the count it was computed
    over. On a weighted section that denominator is a denial-reweighted
    *estimate* of the population, not a count of rows on hand, so it renders as
    ``est. n=`` — the two are several-fold apart wherever the walker sampled, and
    one ``n=`` spelling for both would misreport the weaker cells as far
    better-evidenced than they are.
    """
    lines: list[str] = []
    for section in sections:
        lines += [
            "",
            f"## {section.title}",
            _scope_line(section),
            "",
            f"| {section.group_by} | cases | resolved | open | base rate (resolved) |",
            "| --- | --: | --: | --: | --- |",
        ]
        if not section.buckets:
            lines.append("| _(none)_ | 0 | 0 | 0 | — |")
        for bucket in section.buckets[:_MARKDOWN_BUCKETS]:
            key = bucket.key or "—"
            rate = _disposition_summary(bucket)
            if sample_size and bucket.dispositions:
                label = "est. n" if section.weighted else "n"
                rate += f" ({label}={bucket.resolved})"
            lines.append(f"| {key} | {bucket.cases} | {bucket.resolved} | {bucket.open} | {rate} |")
        overflow = len(section.buckets) - _MARKDOWN_BUCKETS
        if overflow > 0:
            lines.append(f"| _… {overflow} more bucket(s) in the JSON_ | | | | |")
    return lines


def render_statpack_markdown(pack: StatPack, *, markdown_terms: int | None = None) -> str:
    """Render a :class:`StatPack` as a publishable Markdown document.

    Leads with headline counts, the overall base rate, coverage, and decision
    timing; then one table per curated breakdown (capped per section — the JSON
    carries every bucket) and the per-Term live-slice detail table for the most
    recent Terms, with the stage sections last (the interim docket, then the
    merits cohort) — each rendered only when the pack carries it.
    Deterministic; safe on the empty pack (renders a one-line note).

    ``markdown_terms`` caps that per-Term detail; ``0`` renders every Term, and
    ``None`` takes :class:`~fedcourtsai.config.StatpackConfig`'s *field* default —
    not the value in ``config/tracking.yaml``, which only the CLI seam reads, so
    this function stays a pure function of its arguments. The cap is not merely
    cosmetic: this document is the surface the predict and evaluate prompts send
    agents to anchor on, so it bounds the forward stratum's segment base-rate
    window as instructed — the counterpart of
    ``salience.base_rate_lookback_terms``, which bounds the same window in code
    for the cert back-test. Both per-Term captions state the rendered window, so a
    truncation is visible to the agent reading the table."""
    lines = ["# Corpus statpack", ""]
    if pack.corpus_rows == 0:
        lines.append("_Empty — no corpus present. Regenerated once a corpus is available._")
        return "\n".join(lines) + "\n"

    dated_share = (
        f" ({_pct(pack.dated_resolved / pack.machine_readable_resolved)})"
        if pack.machine_readable_resolved
        else ""
    )
    census = (
        f"{pack.coverage.census_filings} docketed filing(s) across the walked Terms"
        if pack.coverage.census_filings is not None
        else "no Term census yet"
    )
    lines += [
        f"**{pack.corpus_rows}** case(s): {pack.resolved} resolved, {pack.open} open.",
        "",
        f"**Live/historical slice:** {pack.coverage.live_slice_rows} case(s), "
        f"{pack.coverage.live_slice_resolved} resolved — the polled population the "
        f"live-slice sections below draw from. It also carries the interim "
        f"application rows, which no cert section aggregates, so a cert section's "
        f"denominator can sit below this count; {census}.",
        "",
        f"**Overall base rate (resolved):** {_disposition_summary(pack.overall)}",
        "",
        f"**Dated share:** {pack.dated_resolved} of {pack.machine_readable_resolved} "
        f"machine-readable resolved case(s) carry a resolution date{dated_share} — "
        "the slice the time-masked replay clock can anchor.",
        "",
        f"**Filing → decision timing:** {_timing_summary(pack.timing)}",
    ]
    lines += _section_tables(pack.sections)
    if pack.terms:
        # `0` means every Term, so it must branch — `pack.terms[:0]` is empty. A
        # negative cap would invert the truncation (dropping the *oldest* Term);
        # `ge=0` guards the config path, and this guards a direct caller.
        window = markdown_terms if markdown_terms is not None else StatpackConfig().markdown_terms
        shown = pack.terms[: max(0, window)] if window > 0 else list(pack.terms)
        lines += [
            "",
            "## SCOTUS cert petitions by Term",
            f"_Live/historical slice; denial-reweighted estimates. Most recent {len(shown)} "
            f"of {len(pack.terms)} Term(s); the JSON artifact carries every Term and the "
            "per-fee-class detail._",
            "",
            (
                "| Term | filings (paid/IFP) | ingested | est. resolved | est. base rate "
                "| est. grant rate | grants | median days | complete |"
            ),
            "| --- | --- | --: | --: | --- | --- | --: | --: | --- |",
        ]
        for entry in shown:
            lines.append(_term_row(entry))
        # The disposition split in the `est. base rate` column separates `granted`
        # from `gvr`, so the comparability caveat rides directly under the table
        # that prints it — the same text the docket pack carries.
        lines += ["", _GVR_SPLIT_CAVEAT]
        bands = salience_bands()
        version = next((t.salience_version for t in shown if t.salience_version), SALIENCE_VERSION)
        lines += [
            "",
            f"### Segment base rate by salience band ({version})",
            (
                "_Paid scored-segment grant rate per band, this Term's live slice only "
                "(denial-reweighted); the leakage-safe base rate the predict prompt is designed "
                "to anchor on and the evaluator will score skill against. `n` is the weighted "
                "resolved denominator. The bracketed `reached` figure is the same band on a "
                "**risk-set** denominator — every petition that ever reached the band, not "
                "only those that ended in it — which is the rate a live petition actually "
                "faces, since a band only ever strengthens. **Which figure is scored depends "
                "on how the band was obtained**: a cell carrying a band frozen at prediction "
                "is scored against the bracketed one, because that is the population it was "
                "in; a cell without one falls back to its terminal band and the leading "
                "figure, which at least agrees with it. The risk sets are **nested**, so the "
                "bracketed denominators are "
                "cumulative across a row rather than a partition of it; the strongest "
                "band's two figures coincide because nothing sits above it, and the weakest "
                "band's risk set is the whole scored segment, so its bracketed figure is the "
                "paid segment's own grant rate rather than a band effect. "
                f"Most recent {len(shown)} of {len(pack.terms)} Term(s) — "
                "pooling a band over the rows below is bounded by what this table renders._"
            ),
            "",
            "| Term | " + " | ".join(bands) + " |",
            "| --- | " + " | ".join("---" for _ in bands) + " |",
        ]
        for entry in shown:
            lines.append(_term_segment_row(entry, bands))
        lines += [
            "",
            (
                "_Replay/backtest cells (a `DECIDED_BEFORE` clock in `record/context.json`): "
                "anchor only on Term rows strictly preceding your clock — later Terms "
                "post-date what you are allowed to know._"
            ),
        ]
    if pack.interim is not None:
        lines += _interim_lines(pack.interim)
    if pack.merits is not None:
        lines += _merits_lines(pack.merits)
    return "\n".join(lines) + "\n"


def _interim_lines(interim: StatPackInterim) -> list[str]:
    """The interim-docket section of the statpack Markdown.

    Rendered only when the pack carries the section, i.e. once the corpus holds
    application rows. Raw counts with the substantive-only rate discipline the
    schema states; the caption carries the interpretation contract so a quoted
    figure cannot shed it.
    """
    lines = [
        "",
        "## The interim docket (applications)",
        (
            "_SCOTUS application dockets (`YYAnnn` — stays, injunctions, vacaturs, and the "
            "time-extension requests that dominate the docket), split by application-Term "
            "year; raw counts, never reweighted. Descriptive only: the grant rate is "
            "computed over **resolved substantive** applications alone — extensions are "
            "counted so their dominance stays visible, but they never pool into any rate — "
            "and it is not a segment base rate: the interim stage's scored base rate "
            "publishes only at the pre-registered resolved-count floor (docs/salience.md), "
            "so until then no skill or calibration claim rests on these "
            "figures. Resolved means a machine-matched interim disposition — an unmatched "
            "resolution stays visibly unresolved rather than entering any denominator — "
            "and withdrawn/dismissed resolutions count as ungranted. This is not a "
            "salience-band product and carries no salience version. "
            "The escalation-signal columns count substantive applications only, and carry "
            "max-latched ending states rather than as-at-prediction values — no rate here "
            "conditions on them. "
            "Replay/backtest cells: the cert Term tables' self-selection rule applies here "
            "too — anchor only on Term rows strictly preceding your clock._"
        ),
        "",
        f"**{interim.applications}** application(s): {interim.extension} extension, "
        f"{interim.substantive} substantive, {interim.unknown} unknown ask, "
        f"{interim.unparsed} never parsed.",
        "",
        f"**Substantive slice:** {interim.substantive_resolved} resolved, "
        f"{interim.substantive_granted} granted — grant rate {_interim_rate(interim)}. "
        f"Escalation signals: response requested {interim.response_requested}, "
        f"referred to the Court {interim.referred_to_court}, "
        f"with amicus {interim.with_amicus}.",
        "",
        (
            "| Term | applications | extension | substantive | unknown | unparsed "
            "| resolved (subst.) | granted | grant rate | resp. requested | referred | amicus |"
        ),
        "| --- | --: | --: | --: | --: | --: | --: | --: | --- | --: | --: | --: |",
    ]
    lines += [_interim_term_row(entry) for entry in interim.terms]
    return lines


def _merits_lines(merits: StatPackMerits) -> list[str]:
    """The merits-cohort section of the statpack Markdown.

    Rendered only when the pack carries the section, i.e. once a corpus row
    holds a parsed merits judgment. Raw counts with the parsed-only rate
    discipline the schema states; the caption carries the interpretation
    contract so a quoted figure cannot shed it.
    """
    lines = [
        "",
        "## The merits docket (granted cases)",
        (
            "_SCOTUS cases whose cert grant opened a merits proceeding — a plain or "
            "partial grant; a GVR or summary reversal decides in the cert order itself, "
            "so it is a cert-stage fact and is excluded by its disposition label (only "
            "as exact as that label: a Term resolved before the `gvr` label existed "
            "carries its GVRs as plain `granted`, so its rate here reads high) — split "
            "by the October Term "
            "certiorari was granted in: a grant-date-keyed axis that does **not** align "
            "with the cert tables' docket-number Terms (a petition docketed in Term T is "
            "routinely granted in T+1), and Terms with no parsed judgment are omitted "
            "from the table. Raw counts, never reweighted (a grant is always "
            "ingested with certainty). The judgment distribution and disturbed rate cover "
            "the **parsed** slice only — cases whose stored snapshot the deterministic "
            "merits parser could read — and `parsed` against `granted` states that "
            "coverage; the gap blends still-pending cases (granted, not yet decided) "
            "with genuine parse gaps, so a recent Term's thin `parsed` is mostly "
            "pendency, not parser failure. The per-Term disturbed rates "
            "(reversed + vacated + affirmed-in-part over parsed) are the committed "
            "feed of the registered merits Brier baseline: a merits cell's skill is "
            "scored against these rates pooled over grant Terms **strictly before** "
            "the case's (docs/decision-model.md), so a skill claim exists only where "
            "strictly-prior Terms carry parsed judgments — and the rate is measured "
            "over exactly the population a merits cell is drawn from, which is why the "
            "cert-order grants are excluded. "
            "A DIG or an equally divided affirmance counts as undisturbed "
            "(both leave the judgment below standing) and sits in the scored pool on "
            "that footing, since the baseline's denominator counts it the same way. "
            "This is not a salience-band product and carries "
            "no salience version. Replay/backtest cells: the cert Term tables' "
            "self-selection rule applies here too — anchor only on Term rows strictly "
            "preceding your clock._"
        ),
        "",
        f"**{merits.granted}** granted case(s): {merits.parsed} with a parsed judgment.",
        "",
        f"**Parsed slice:** {merits.affirmed} affirmed, {merits.reversed} reversed, "
        f"{merits.vacated} vacated, {merits.affirmed_in_part} affirmed in part, "
        f"{merits.dig} DIG, {merits.equally_divided} equally divided — "
        f"disturbed rate {_merits_rate(merits)}.",
        "",
        (
            "| Term | granted | parsed | affirmed | reversed | vacated | in part "
            "| DIG | equally divided | disturbed | disturbed rate |"
        ),
        "| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --- |",
    ]
    lines += [_merits_term_row(entry) for entry in merits.terms]
    return lines


def _merits_rate(entry: StatPackMerits | StatPackMeritsTerm) -> str:
    """The disturbed rate with its raw denominator beside it, or a dash."""
    if entry.disturbed_rate is None:
        return "—"
    return f"{_pct(entry.disturbed_rate)} (n={entry.parsed})"


def _merits_term_row(entry: StatPackMeritsTerm) -> str:
    """One grant-Term's row in the merits docket table."""
    return (
        f"| {entry.term} | {entry.granted} | {entry.parsed} | {entry.affirmed} "
        f"| {entry.reversed} | {entry.vacated} | {entry.affirmed_in_part} | {entry.dig} "
        f"| {entry.equally_divided} | {entry.disturbed} | {_merits_rate(entry)} |"
    )


def _interim_rate(entry: StatPackInterim | StatPackInterimTerm) -> str:
    """The substantive grant rate with its raw denominator beside it, or a dash."""
    if entry.substantive_grant_rate is None:
        return "—"
    return f"{_pct(entry.substantive_grant_rate)} (n={entry.substantive_resolved})"


def _interim_term_row(entry: StatPackInterimTerm) -> str:
    """One application-Term's row in the interim docket table."""
    return (
        f"| {entry.term} | {entry.applications} | {entry.extension} | {entry.substantive} "
        f"| {entry.unknown} | {entry.unparsed} | {entry.substantive_resolved} "
        f"| {entry.substantive_granted} | {_interim_rate(entry)} | {entry.response_requested} "
        f"| {entry.referred_to_court} | {entry.with_amicus} |"
    )


def _term_segment_row(entry: StatPackTerm, bands: tuple[str, ...]) -> str:
    """One Term's row in the per-salience-band grant-rate table."""
    by_band = {s.band: s for s in entry.segments}

    def _cell(band: str) -> str:
        """The terminal rate first, with the risk-set rate bracketed beside it so
        the gap is legible without a second table. Which one is scored depends on
        how the reader's band was obtained — see the caption. A band's risk set contains its
        terminal set, so a bracketed figure can exist where the leading one does
        not — a band no petition *ended* in, but some passed through."""
        seg = by_band.get(band)
        if seg is None:
            return "—"
        reached = (
            f"[reached {_pct(seg.prefix_est_grant_rate)}, n={seg.prefix_weighted_resolved}]"
            if seg.prefix_est_grant_rate is not None
            else ""
        )
        if seg.est_grant_rate is None:
            return reached or "—"
        return f"{_pct(seg.est_grant_rate)} (n={seg.weighted_resolved}) {reached}".rstrip()

    return f"| {entry.term} | " + " | ".join(_cell(band) for band in bands) + " |"


def _term_row(entry: StatPackTerm) -> str:
    """One Term's row in the Markdown detail table."""
    by_class = {c.fee_class: c for c in entry.classes}
    paid = by_class.get(FeeClass.paid)
    ifp = by_class.get(FeeClass.ifp)

    def _filings(cls: StatPackTermClass | None) -> str:
        return "—" if cls is None or cls.filings is None else str(cls.filings)

    def _complete(cls: StatPackTermClass | None) -> str:
        return "✓" if cls is not None and cls.complete else "partial"

    rates = entry.base_rates
    # The rendered rate is the field's own value, never a recomputation: the JSON
    # and the Markdown must publish the same grant-family pool (a GVR is a grant),
    # and `_grant_family_share` is that pool's one definition.
    grant_rate = entry.est_grant_family_rate
    # `ingested` is the raw row count; every `est.` column is the weighted
    # estimate — mixing the two under one label would publish a false coverage
    # claim on the exact surface the predict prompt points cells at.
    return (
        f"| {entry.term} | {_filings(paid)}/{_filings(ifp)} | {entry.ingested} "
        f"| {rates.resolved} | {_disposition_summary(rates)} "
        f"| {_pct(grant_rate) if grant_rate is not None else '—'} | {entry.grants} "
        f"| {_days(entry.timing.median_days)} "
        f"| {_complete(paid)}/{_complete(ifp)} |"
    )


# The one caveat every surface that prints the `granted` / `gvr` split must
# carry — a single constant so the statpack (the surface the predict/evaluate
# cells anchor on) and the docket pack (the citable court-facing document) can
# never state it differently.
_GVR_SPLIT_CAVEAT = (
    "**The `granted` / `gvr` split is not comparable across Terms.** The `gvr` "
    "label is a forward convention: a resolution recorded before it existed keeps "
    "`granted`, and no post-hoc rule separates a merits GVR from a plenary grant "
    "without re-resolving the source. OT2023 and OT2024 were resolved into the "
    "corpus inside that window, so they carry **zero** GVRs against 30-59% of the "
    "grant family in every Term either side of them — ingestion history, not the "
    "Court changing behaviour. Read the grant family as one number — the JSON "
    "artifacts publish it per Term as `est_grant_family_rate` — because the split "
    "is safe within a Term and meaningless between them."
)


# The statistics a reader of a published court stat pack expects and this
# artifact cannot yet compute. Named in the document rather than left as silent
# gaps, so a citation is not read as a claim that the number is zero.
_DOCKET_GAPS = (
    _GVR_SPLIT_CAVEAT,
    "**What the petitions are about.** A distribution of the questions presented "
    "by subject matter needs a claim taxonomy to classify them against, and no "
    "such taxonomy is built. Inventing one for this artifact alone would publish "
    "a categorization nothing else in the project shares, and that no later work "
    "could reproduce.",
    "**Summary reversals are not broken out.** The disposition vocabulary carries "
    "a label for them, but no resolver rule reads one off an order, so none is "
    "produced and a summary reversal is counted inside the grant family above "
    "rather than being missing from it. "
    "On mandatory-jurisdiction direct appeals the outcome resolver latches only "
    "the vacatur-remand form (`gvr`); summary affirmance and dismissal for want "
    "of a substantial federal question are deliberate resolver misses that reach "
    "maintainer triage instead.",
    "**Justice-level statistics.** Vote frequencies, agreement matrices, and "
    "opinion authorship are per-justice facts; this corpus is docket-first and "
    "holds no per-justice vote record.",
)


def render_docket_markdown(pack: DocketPack) -> str:
    """Render a :class:`DocketPack` as a publishable Markdown document.

    Leads with what the document is and — as pointedly — what it is not: a
    reader who does not care how well this project's models forecast the Court
    should still be able to read and cite every figure in it. Then the coverage
    denominators, a how-to-read note covering the denial reweighting, one table
    per docket-composition breakdown, the per-Term census, and the named gaps.
    Deterministic; safe on the empty pack (renders a one-line note).

    Every Term is rendered rather than capped. The statpack's cap bounds what the
    predict/evaluate prompts point agents at; this document is not that surface,
    and capping it would buy nothing anyway — the JSON sibling in the same
    checkout is unbounded either way, so the bound is conventional. What the cap
    does carry there and must carry here is the replay self-selection rule, which
    rides under the Term table.
    """
    lines = ["# Docket pack", ""]
    if pack.corpus_rows == 0:
        lines.append("_Empty — no corpus present. Regenerated once a corpus is available._")
        return "\n".join(lines) + "\n"

    census = (
        f"{pack.coverage.census_filings} docketed filing(s) across the walked Terms"
        if pack.coverage.census_filings is not None
        else "no Term census yet"
    )
    vintage = (
        f", pulled through {pack.corpus_through.isoformat()}"
        if pack.corpus_through is not None
        else ""
    )
    lines += [
        "Facts about the dockets themselves: what the Supreme Court is asked to take, "
        "from which court below, on which fee stream, after how many relists, and how "
        "it disposes of what it is asked. It carries **no claim about this project's "
        "predictions** — no accuracy, no model ranking, no measure of which petitions "
        "are worth predicting — so it is readable and citable without any interest in "
        "whether those models are any good.",
        "",
        f"**Corpus.** {pack.corpus_rows} case(s): {pack.resolved} resolved, {pack.open} open"
        f"{vintage}. Most rows are an unlabeled bulk import, so the two overview "
        "sections below describe the **labeled subset only** — read `resolved` against "
        "`cases` before quoting one.",
        "",
        f"**Live/historical slice.** {pack.coverage.live_slice_rows} case(s), "
        f"{pack.coverage.live_slice_resolved} resolved — matters read from the Court's "
        "own docket pages, the population the cert statistics below draw from. It "
        "also carries the interim application rows, which no cert statistic "
        f"aggregates, so a cert denominator can sit below this count; {census}.",
        "",
        "**How to read the tables.** Each section states its own scope: the court, the "
        "population, and whether its counts are denial-reweighted. That reweighting "
        "matters. The historical walk ingests every decided petition except denials, "
        "which it samples on a committed frame, so a raw count would badly overstate "
        "the grant rate; a reweighted section counts each ingested petition for the "
        "number of petitions it stands in for. **Every section here is reweighted**, "
        "including the two overview cuts: nearly every labeled SCOTUS row is a "
        "sampled one, so a raw disposition split there would overstate the grant "
        "family several-fold, while a bulk-import circuit row carries weight 1 and is "
        "unchanged by it. So every count is a population **estimate** rather than rows "
        "on hand, and every denominator is written `est. n=`. In the breakdown tables "
        "that denominator is the `resolved` column beside the rate; the per-Term "
        "census states its own the same way.",
        "",
        "**In the breakdown tables the estimate does not tell you** how many "
        "petitions were actually read to produce it. An `est. n=` of a few hundred "
        "rests on a raw row count several times smaller, and a breakdown row carries "
        "no raw view of its own — so treat a small reweighted cell as weaker evidence "
        "than its denominator suggests, and read a rate against the whole-population "
        "figures above it rather than on its own. The per-Term census is the "
        "exception and the place to calibrate that gap: it prints the observed "
        "`ingested (rows)` beside the reweighted estimate, so the ratio between them "
        "is legible for every Term.",
        "",
        "**Where a value is missing** the row still appears rather than being dropped, "
        "so a coverage gap is never hidden inside a rate. A `(none)` bucket means "
        "*no value on that dimension*, and what that stands for differs by cut, so "
        "read it against the section rather than as one thing. On the circuit cut it "
        "is mostly **not** an unknown court below: it is the petitions whose court "
        "below is not a federal circuit — state supreme courts above all — and the "
        "section that follows names them. On the era cut it is the absence of any "
        "date signal. On the fee-class cut it is a parsing gap: fee class is read by "
        "a stricter serial parser than the one behind the Term cuts, so docket "
        "numbers it cannot read — annotated ones such as a capital-case marker most "
        "visibly, but also consolidated and prefixed spellings — land here. That "
        "bucket is therefore **not a random slice**, so read the paid/IFP table as a "
        "split of the petitions whose numbers parse cleanly rather than a partition "
        "of the whole docket. Where an `(unknown)` bucket appears — the relist and "
        "CVSG cuts, whose signal comes from parsed proceedings — it means *not yet "
        "parsed* rather than *did not happen*.",
    ]
    lines += _section_tables(pack.sections, sample_size=True)
    if pack.terms:
        lines += [
            "",
            "## SCOTUS cert petitions by Term",
            "_Live/historical slice. `filings` is the count of docketed serials across "
            "the paid and IFP streams, read from the discovery cursors — exact for "
            "docketed numbers, a slight upper bound on real petitions since withheld "
            "serials still count. **The two columns are not nested**: `ingested` counts "
            "rows on hand, and a row can sit outside the serial census — most visibly a "
            "petition whose docket number carries an annotation the serial parser "
            "cannot read (a capital-case marker, say), ingested under its Term but "
            "belonging to no stream's census — so `ingested` can "
            "exceed `filings`. `ingested` and `grants "
            "observed` are raw counts of rows on hand; the grant rate is the "
            "denial-reweighted estimate, and its `est. n` is the reweighted resolved "
            "count it divides by — which is why it too can exceed `ingested`. The "
            "plain `n` beside the pace to grant is different: that one is a raw count "
            "of the granted petitions carrying both dates. Dividing "
            "`grants observed` by `ingested` does **not** reproduce the rate and is "
            "not a rate at all; the raw grant count is comparable to the weighted "
            "denominator only because a grant is always kept at weight 1 while "
            "denials are sampled. The rate pools the paid and IFP streams, whose own "
            "grant rates differ several-fold, so a Term-over-Term move can be a shift "
            "in that mix rather than in the Court's appetite. A Term reads `complete` "
            "only "
            "once every probed stream was walked to its observed end; until then its "
            "figures describe the walked prefix, and for a Term still in progress that "
            "end moves as the Court dockets more petitions, so `complete` there means "
            "current, not final. Every Term the walk has touched is listed, most recent "
            "first._",
            "",
            (
                "| Term | filings | ingested (rows) | est. grant rate (weighted) "
                "| grants observed (rows) | median days to grant | census |"
            ),
            "| --- | --: | --: | --- | --: | --- | --- |",
        ]
        for entry in pack.terms:
            lines.append(_docket_term_row(entry))
        lines += [
            "",
            (
                "_Replay/backtest cells (a `DECIDED_BEFORE` clock in `record/context.json`): "
                "this document sits in the same checkout as the statpack and the same rule "
                "applies — anchor only on Term rows strictly preceding your clock, because "
                "later Terms post-date what you are allowed to know._"
            ),
        ]
    lines += ["", "## Not yet included", ""]
    lines += [f"- {gap}" for gap in _DOCKET_GAPS]
    return "\n".join(lines) + "\n"


def _docket_term_row(entry: DocketPackTerm) -> str:
    """One Term's row in the docket-pack census table."""
    # `est. n` on the weighted rate, plain `n` on the pace-to-grant subset: one
    # spelling rule across the document, and this row shows both side by side.
    # The rate reads the pooled-family field, as the statpack's Term row does.
    rate = (
        f"{_pct(entry.est_grant_family_rate)} (est. n={entry.weighted_resolved})"
        if entry.est_grant_family_rate is not None
        else "—"
    )
    pace = (
        "—"
        if entry.median_days_to_grant is None
        else f"{_days(entry.median_days_to_grant)} (n={entry.dated_grants})"
    )
    return (
        f"| {entry.term} | {entry.filings if entry.filings is not None else '—'} "
        f"| {entry.ingested} | {rate} | {entry.grants} "
        f"| {pace} "
        f"| {'complete' if entry.complete else 'partial'} |"
    )


def _days(value: float | None) -> str:
    return "—" if value is None else f"{value:.0f}"


def _timing_summary(timing: TimingStats) -> str:
    """A compact ``median 245d, p90 410d (mean 260.1d over N cases)`` line, or a dash."""
    if timing.cases == 0:
        return "—"
    return (
        f"median {_days(timing.median_days)}d, p90 {_days(timing.p90_days)}d "
        f"(mean {timing.mean_days}d over {timing.cases} dated case(s))"
    )


def _pct(share: float) -> str:
    return f"{share * 100:.1f}%"


def _disposition_summary(bucket: BaseRateBucket) -> str:
    """A compact ``granted 50.0%, denied 50.0%`` line, or a dash when nothing resolved."""
    if not bucket.dispositions:
        return "—"
    return ", ".join(f"{d.disposition} {_pct(d.share)}" for d in bucket.dispositions)


def render_markdown(report: AnalyticsReport) -> str:
    """Render an :class:`AnalyticsReport` as a Markdown summary for the step summary/log.

    Follows the ``ops.render_*`` house style: a heading, the overall base rate, and —
    when grouped — a table of one row per bucket. Safe on a skipped (corpus-absent)
    report.
    """
    if report.skipped:
        return "## Corpus analytics\n\n_No corpus present — run after `fedcourts corpus-pull`._\n"

    total = report.total
    lines = [
        "## Corpus analytics",
        "",
        f"**{total.cases}** matched case(s): {total.resolved} resolved, {total.open} open.",
        "",
        f"**Base rate (resolved):** {_disposition_summary(total)}",
    ]
    if report.group_by:
        lines += [
            "",
            f"### By {report.group_by}",
            "",
            f"| {report.group_by} | cases | resolved | open | base rate (resolved) |",
            "| --- | --: | --: | --: | --- |",
        ]
        for bucket in report.buckets:
            key = bucket.key or "—"
            lines.append(
                f"| {key} | {bucket.cases} | {bucket.resolved} | {bucket.open} "
                f"| {_disposition_summary(bucket)} |"
            )
    return "\n".join(lines) + "\n"
