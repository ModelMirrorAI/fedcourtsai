"""Aggregate disposition base-rates over the corpus (read-only, deterministic, offline).

The aggregate counterpart of :func:`fedcourtsai.corpus.retrieve_priors` — the per-case
precedent retrieval behind ``fedcourts query``. Instead of returning a handful of
individual priors, it rolls the *whole* matched set into base-rates: how the realized
dispositions split overall and per a chosen dimension (court, topic, judge, SCOTUS
Term year, disposition). A pure function of the corpus — no clock, no network, no
randomness — so the same corpus yields byte-identical output.

Exposed two ways, both read-only: ``fedcourts stats`` (a maintainer investigating the
corpus, or a predictor pulling base-rate context after a ``dvc pull``) and the
``corpus-stats`` mode of the ``run-analytics`` workflow. It never writes the corpus,
``data/``, DVC, or git.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from . import corpus
from .corpus import CorpusRow
from .pipeline.outcome import is_machine_readable
from .schemas import (
    AnalyticsReport,
    BaseRateBucket,
    Disposition,
    DispositionShare,
    FeeClass,
    GroupBy,
    StatPack,
    StatPackCoverage,
    StatPackSection,
    StatPackTerm,
    StatPackTermClass,
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
        default=False, description="Drop unresolved cases (default keeps them for the open count)."
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

    Graceful before a ``dvc pull`` (mirrors :func:`fedcourtsai.validate.run_scope_audit`):
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
    keys under the same ``group_by``.
    """

    title: str
    court: str | None
    cert_stage: bool
    live_slice: bool
    weighted: bool
    group_by: GroupBy
    key_fn: Callable[[CorpusRow], str | None] | None = None


# The curated breakdowns the statpack publishes. Two populations, deliberately
# side by side: the full-corpus overview (court composition, era spread —
# includes the frozen bulk import, labeled so in the render) for human context,
# and the live-slice weighted cuts the predict/evaluate prompts anchor on. The
# per-Term detail is not a section — it is the richer `terms` array, built in
# `build_statpack`.
_STATPACK_SECTIONS: tuple[_SectionSpec, ...] = (
    _SectionSpec("Cases by court", None, False, False, False, GroupBy.court),
    _SectionSpec("SCOTUS cases by era", "scotus", False, False, False, GroupBy.era),
    # The calibration anchor the predict prompts point at (and ops reads by its
    # cert_stage + disposition shape): modern Term-prefixed discretionary-cert
    # dockets, live slice, denial-reweighted — the trustworthy grant/deny split.
    _SectionSpec(
        "Modern discretionary-cert petitions by disposition",
        "scotus",
        True,
        True,
        True,
        GroupBy.disposition,
    ),
    _SectionSpec(
        "Modern cert petitions by originating circuit",
        "scotus",
        True,
        True,
        True,
        GroupBy.originating_court,
    ),
    _SectionSpec(
        "Cert petitions by relist count", "scotus", True, True, True, GroupBy.relist_bucket
    ),
    _SectionSpec("Cert petitions by CVSG status", "scotus", True, True, True, GroupBy.cvsg),
    _SectionSpec(
        "Petitions by originating court (incl. state courts)",
        "scotus",
        True,
        True,
        False,
        GroupBy.originating_court,
        key_fn=_originating_court_or_name,
    ),
)


class _Slice:
    """Streaming accumulator for one statpack slice (the whole set, a bucket, a Term).

    The corpus is millions of rows, so the statpack is built in **one streamed
    pass**: each row updates the counters of every slice it belongs to, and the
    buckets/timing are rolled up from the counters afterwards — no row list is
    materialized and no per-section re-scan runs.

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

    __slots__ = ("classes", "grant_days", "grants", "overall")

    def __init__(self) -> None:
        self.overall = _Slice(cert_timing=True)
        self.classes: dict[FeeClass, _Slice] = {
            FeeClass.paid: _Slice(cert_timing=True),
            FeeClass.ifp: _Slice(cert_timing=True),
        }
        self.grants = 0
        self.grant_days: list[int] = []

    def add(self, row: CorpusRow) -> None:
        self.overall.add(row)
        fee = _fee_class(row)
        if fee is not None:
            self.classes[fee].add(row)
        if row.disposition == Disposition.granted.value:
            self.grants += 1
            if row.date_filed is not None and row.date_cert_granted is not None:
                days = (row.date_cert_granted - row.date_filed).days
                if days >= 0:
                    self.grant_days.append(days)


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
                est_grant_rate=next(
                    (d.share for d in weighted.dispositions if d.disposition == "granted"),
                    0.0 if weighted.resolved else None,
                ),
                dispositions=weighted.dispositions,
                timing=entry.timing(weighted=True),
            )
        )
    grant_days = sorted(acc.grant_days)
    return StatPackTerm(
        term=year,
        ingested=acc.overall.cases,
        base_rates=acc.overall.bucket(str(year), weighted=True),
        timing=acc.overall.timing(weighted=True),
        classes=classes,
        grants=acc.grants,
        median_days_to_grant=_nearest_rank(grant_days, 0.5) if grant_days else None,
    )


def build_statpack(*, corpus_db_path: Path) -> StatPack:
    """Roll the whole corpus into a base-rate statpack, or the empty pack if it is absent.

    Deterministic and offline — a pure function of the corpus — so reruns reproduce it
    byte for byte. Mirrors ``fedcourts backtest`` / ``leaderboard``: an absent corpus
    (run before ``dvc pull``) yields the empty zero-count pack rather than an error.

    Two populations, kept apart by section flags: the full-corpus overview
    (bulk import included) for composition context, and the live-slice weighted
    cuts + per-Term entries the predict/evaluate prompts anchor on. The ``terms``
    array iterates the union of row-derived Terms and cursor-table Terms, so a
    Term the walkers have probed but not yet populated still shows its census.
    """
    if not corpus_db_path.exists():
        # Keep the section scaffolding (empty buckets) so the artifact's shape is stable
        # whether the corpus is merely absent or present-but-empty.
        return StatPack(
            sections=[
                StatPackSection(
                    title=spec.title,
                    court=spec.court,
                    cert_stage=spec.cert_stage,
                    live_slice=spec.live_slice,
                    weighted=spec.weighted,
                    group_by=spec.group_by,
                )
                for spec in _STATPACK_SECTIONS
            ]
        )
    overall = _Slice()
    live_slice_totals = _Slice()
    section_slices: list[defaultdict[str, _Slice]] = [
        defaultdict(_Slice) for _ in _STATPACK_SECTIONS
    ]
    term_accs: dict[int, _TermAcc] = {}
    with corpus.connect(corpus_db_path) as conn:
        cursor_rows = corpus.live_cursor_rows(conn)
        for row in corpus.iter_rows(conn):
            overall.add(row)
            row_is_live = corpus.is_live_slice(row)
            if row_is_live:
                live_slice_totals.add(row)
            for spec, slices in zip(_STATPACK_SECTIONS, section_slices, strict=True):
                if spec.court is not None and row.court != spec.court:
                    continue
                if spec.live_slice and not row_is_live:
                    continue
                if spec.cert_stage and not corpus.is_modern_cert(row):
                    continue
                keys = (
                    _bucket_keys(row, spec.group_by)
                    if spec.key_fn is None
                    else [spec.key_fn(row) or _NONE_KEY]
                )
                for key in keys:
                    slices[key].add(row)
            if row_is_live and row.court == "scotus":
                year = corpus.scotus_term_year(row.docket_number)
                if year is not None:
                    term_accs.setdefault(year, _TermAcc()).add(row)

    sections = []
    for spec, slices in zip(_STATPACK_SECTIONS, section_slices, strict=True):
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
    census = _census(cursor_rows)
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
    )


# How many recent Terms the Markdown detail table shows; the JSON carries them all.
_MARKDOWN_TERMS = 10
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


def render_statpack_markdown(pack: StatPack) -> str:
    """Render a :class:`StatPack` as a publishable Markdown document.

    Leads with headline counts, the overall base rate, coverage, and decision
    timing; then one table per curated breakdown (capped per section — the JSON
    carries every bucket) and the per-Term live-slice detail table for the most
    recent Terms. Deterministic; safe on the empty pack (renders a one-line
    note)."""
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
        f"{pack.coverage.live_slice_resolved} resolved — the population behind every "
        f"live-slice section below; {census}.",
        "",
        f"**Overall base rate (resolved):** {_disposition_summary(pack.overall)}",
        "",
        f"**Dated share:** {pack.dated_resolved} of {pack.machine_readable_resolved} "
        f"machine-readable resolved case(s) carry a resolution date{dated_share} — "
        "the slice the time-masked replay clock can anchor.",
        "",
        f"**Filing → decision timing:** {_timing_summary(pack.timing)}",
    ]
    for section in pack.sections:
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
            lines.append(
                f"| {key} | {bucket.cases} | {bucket.resolved} | {bucket.open} "
                f"| {_disposition_summary(bucket)} |"
            )
        overflow = len(section.buckets) - _MARKDOWN_BUCKETS
        if overflow > 0:
            lines.append(f"| _… {overflow} more bucket(s) in the JSON_ | | | | |")
    if pack.terms:
        shown = pack.terms[:_MARKDOWN_TERMS]
        lines += [
            "",
            "## SCOTUS cert petitions by Term",
            f"_Live/historical slice; denial-reweighted estimates. Most recent {len(shown)} "
            f"of {len(pack.terms)} Term(s); the JSON artifact carries every Term and the "
            "per-fee-class detail._",
            "",
            "| Term | filings (paid/IFP) | ingested | est. resolved | est. base rate "
            "| est. grant rate | grants | median days | complete |",
            "| --- | --- | --: | --: | --- | --- | --: | --: | --- |",
        ]
        for entry in shown:
            lines.append(_term_row(entry))
        lines += [
            "",
            "_Replay/backtest cells (a `DECIDED_BEFORE` clock in `record/context.json`): "
            "anchor only on Term rows strictly preceding your clock — later Terms "
            "post-date what you are allowed to know._",
        ]
    return "\n".join(lines) + "\n"


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
    # An all-denied Term has a real grant rate of 0%; only a Term with nothing
    # resolved has no rate at all.
    grant_rate = next(
        (d.share for d in rates.dispositions if d.disposition == "granted"),
        0.0 if rates.resolved else None,
    )
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
        return "## Corpus analytics\n\n_No corpus present — run after `dvc pull`._\n"

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
