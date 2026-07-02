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
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from . import corpus
from .corpus import CorpusRow
from .schemas import (
    AnalyticsReport,
    BaseRateBucket,
    Disposition,
    DispositionShare,
    GroupBy,
    StatPack,
    StatPackSection,
    StatPackTerm,
    TimingStats,
)

if TYPE_CHECKING:
    import sqlite3

# Bucket key stand-ins for rows that carry no value on the grouped dimension (a null
# topic, an unparseable Term, no panel) and for the open cases in a disposition group.
_NONE_KEY = "(none)"
_OPEN_KEY = "(open)"


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
        query.resolved_only and row.disposition is None,
    )
    return not any(mismatches)


def _bucket_keys(row: CorpusRow, group_by: GroupBy) -> list[str]:
    """The bucket key(s) ``row`` contributes to for the grouped dimension.

    Single-valued for every dimension except ``judge``, where a row joins one bucket
    per panel member (so grouped case counts can exceed the ungrouped total).
    """
    if group_by == GroupBy.court:
        return [row.court]
    if group_by == GroupBy.topic:
        return [row.topic or _NONE_KEY]
    if group_by == GroupBy.judge:
        return list(row.judges) or [_NONE_KEY]
    if group_by == GroupBy.term_year:
        year = corpus.scotus_term_year(row.docket_number)
        return [str(year) if year is not None else _NONE_KEY]
    if group_by == GroupBy.originating_court:
        # The (none) bucket keeps unlinked rows visible: only the REST path
        # populates the linkage, so coverage matters as much as the split.
        return [row.originating_court or _NONE_KEY]
    # GroupBy.disposition — open cases share one bucket rather than scattering.
    return [row.disposition or _OPEN_KEY]


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


def _decision_days(row: CorpusRow) -> int | None:
    """Days filed→decided for a resolved row with a usable date pair, else ``None``.

    Rows missing either date — or with a decision before the filing (a data glitch)
    — are excluded rather than guessed.
    """
    if row.disposition is None or row.date_filed is None or row.date_decided is None:
        return None
    days = (row.date_decided - row.date_filed).days
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


# The curated breakdowns the statpack publishes: (title, court filter, dimension). The
# prediction domain is SCOTUS cert, so the topic and originating-circuit cuts are
# scoped to it; the court cut spans the whole corpus for composition context. The
# per-Term detail is not a section — it is the richer `terms` array (base rates +
# timing per SCOTUS October Term), built in `build_statpack`.
_STATPACK_SECTIONS: tuple[tuple[str, str | None, GroupBy], ...] = (
    ("Cases by court", None, GroupBy.court),
    ("SCOTUS petitions by nature-of-suit topic", "scotus", GroupBy.topic),
    ("SCOTUS petitions by originating circuit", "scotus", GroupBy.originating_court),
)


class _Slice:
    """Streaming accumulator for one statpack slice (the whole set, a bucket, a Term).

    The corpus is millions of rows, so the statpack is built in **one streamed
    pass**: each row updates the counters of every slice it belongs to, and the
    buckets/timing are rolled up from the counters afterwards — no row list is
    materialized and no per-section re-scan runs.
    """

    __slots__ = ("cases", "days", "labels")

    def __init__(self) -> None:
        self.cases = 0
        self.labels: Counter[str] = Counter()
        self.days: list[int] = []

    def add(self, row: CorpusRow) -> None:
        self.cases += 1
        if row.disposition is not None:
            self.labels[row.disposition] += 1
        days = _decision_days(row)
        if days is not None:
            self.days.append(days)

    def bucket(self, key: str) -> BaseRateBucket:
        return _bucket_from_counts(key, self.cases, self.labels)

    def timing(self) -> TimingStats:
        return _timing_from_days(self.days)


def build_statpack(*, corpus_db_path: Path) -> StatPack:
    """Roll the whole corpus into a base-rate statpack, or the empty pack if it is absent.

    Deterministic and offline — a pure function of the corpus — so reruns reproduce it
    byte for byte. Mirrors ``fedcourts backtest`` / ``leaderboard``: an absent corpus
    (run before ``dvc pull``) yields the empty zero-count pack rather than an error.
    """
    if not corpus_db_path.exists():
        # Keep the section scaffolding (empty buckets) so the artifact's shape is stable
        # whether the corpus is merely absent or present-but-empty.
        return StatPack(
            sections=[
                StatPackSection(title=title, court=court, group_by=dimension)
                for title, court, dimension in _STATPACK_SECTIONS
            ]
        )
    overall = _Slice()
    section_slices: list[defaultdict[str, _Slice]] = [
        defaultdict(_Slice) for _ in _STATPACK_SECTIONS
    ]
    term_slices: defaultdict[int, _Slice] = defaultdict(_Slice)
    with corpus.connect(corpus_db_path) as conn:
        for row in corpus.iter_rows(conn):
            overall.add(row)
            for (_, court_filter, dimension), slices in zip(
                _STATPACK_SECTIONS, section_slices, strict=True
            ):
                if court_filter is None or row.court == court_filter:
                    for key in _bucket_keys(row, dimension):
                        slices[key].add(row)
            if row.court == "scotus":
                year = corpus.scotus_term_year(row.docket_number)
                if year is not None:
                    term_slices[year].add(row)

    sections = []
    for (title, court_filter, dimension), slices in zip(
        _STATPACK_SECTIONS, section_slices, strict=True
    ):
        buckets = [entry.bucket(key) for key, entry in slices.items()]
        buckets.sort(key=lambda b: (-b.cases, b.key))
        sections.append(
            StatPackSection(title=title, court=court_filter, group_by=dimension, buckets=buckets)
        )
    total = overall.bucket("")
    return StatPack(
        corpus_rows=overall.cases,
        resolved=total.resolved,
        open=total.open,
        overall=total,
        timing=overall.timing(),
        sections=sections,
        terms=[
            StatPackTerm(term=year, base_rates=entry.bucket(str(year)), timing=entry.timing())
            for year, entry in sorted(term_slices.items(), reverse=True)
        ],
    )


# How many recent Terms the Markdown detail table shows; the JSON carries them all.
_MARKDOWN_TERMS = 10


def render_statpack_markdown(pack: StatPack) -> str:
    """Render a :class:`StatPack` as a publishable Markdown document.

    Leads with headline counts, the overall base rate, and decision timing; then one
    table per curated breakdown and a per-Term detail table for the most recent
    Terms (the JSON carries every Term). Deterministic; safe on the empty pack
    (renders a one-line note)."""
    lines = ["# Corpus statpack", ""]
    if pack.corpus_rows == 0:
        lines.append("_Empty — no corpus present. Regenerated once a corpus is available._")
        return "\n".join(lines) + "\n"

    lines += [
        f"**{pack.corpus_rows}** case(s): {pack.resolved} resolved, {pack.open} open.",
        "",
        f"**Overall base rate (resolved):** {_disposition_summary(pack.overall)}",
        "",
        f"**Filing → decision timing:** {_timing_summary(pack.timing)}",
    ]
    for section in pack.sections:
        scope = "all courts" if section.court is None else section.court
        lines += [
            "",
            f"## {section.title}",
            f"_Scope: {scope}._",
            "",
            f"| {section.group_by} | cases | resolved | open | base rate (resolved) |",
            "| --- | --: | --: | --: | --- |",
        ]
        if not section.buckets:
            lines.append("| _(none)_ | 0 | 0 | 0 | — |")
        for bucket in section.buckets:
            key = bucket.key or "—"
            lines.append(
                f"| {key} | {bucket.cases} | {bucket.resolved} | {bucket.open} "
                f"| {_disposition_summary(bucket)} |"
            )
    if pack.terms:
        shown = pack.terms[:_MARKDOWN_TERMS]
        lines += [
            "",
            "## SCOTUS petitions by Term",
            f"_Most recent {len(shown)} of {len(pack.terms)} Term(s); "
            "the JSON artifact carries every Term._",
            "",
            "| Term | cases | resolved | open | base rate (resolved) | median days | p90 days |",
            "| --- | --: | --: | --: | --- | --: | --: |",
        ]
        for entry in shown:
            rates = entry.base_rates
            lines.append(
                f"| {entry.term} | {rates.cases} | {rates.resolved} | {rates.open} "
                f"| {_disposition_summary(rates)} "
                f"| {_days(entry.timing.median_days)} | {_days(entry.timing.p90_days)} |"
            )
    return "\n".join(lines) + "\n"


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
