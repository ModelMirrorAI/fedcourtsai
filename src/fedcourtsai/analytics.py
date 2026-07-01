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
    resolved_only: bool = Field(
        default=False, description="Drop unresolved cases (default keeps them for the open count)."
    )
    group_by: GroupBy | None = None


def _row_matches(row: CorpusRow, query: AnalyticsQuery) -> bool:
    """Whether ``row`` satisfies the query's Python-side filters.

    ``court`` and ``disposition`` are pushed into SQL by :func:`corpus.iter_rows`; the
    overlap filters (``judges`` / ``citations``), the exact ``topic``, the ``date_filed``
    range, and ``resolved_only`` are applied here over the narrowed candidate set.
    """
    if query.topic is not None and row.topic != query.topic:
        return False
    if query.judges and not (set(query.judges) & set(row.judges)):
        return False
    if query.citations and not (set(query.citations) & set(row.citations)):
        return False
    filed = row.date_filed
    if query.date_from is not None and (filed is None or filed < query.date_from):
        return False
    if query.date_to is not None and (filed is None or filed > query.date_to):
        return False
    return not (query.resolved_only and row.disposition is None)


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
    # GroupBy.disposition — open cases share one bucket rather than scattering.
    return [row.disposition or _OPEN_KEY]


def _build_bucket(key: str, rows: list[CorpusRow]) -> BaseRateBucket:
    """Roll a slice of rows into its case/resolved/open counts and disposition base-rates."""
    # CorpusRow uses `use_enum_values`, so `row.disposition` is the string label or None.
    labels = Counter(row.disposition for row in rows if row.disposition is not None)
    resolved = sum(labels.values())
    dispositions = [
        DispositionShare(disposition=Disposition(label), count=n, share=n / resolved)
        for label, n in labels.items()
    ]
    # Most common first; ties broken by the disposition label for a total, stable order.
    dispositions.sort(key=lambda d: (-d.count, d.disposition))
    return BaseRateBucket(
        key=key,
        cases=len(rows),
        resolved=resolved,
        open=len(rows) - resolved,
        dispositions=dispositions,
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
# prediction domain is SCOTUS cert, so the Term-year and topic cuts are scoped to it;
# the court cut spans the whole corpus for composition context.
_STATPACK_SECTIONS: tuple[tuple[str, str | None, GroupBy], ...] = (
    ("Cases by court", None, GroupBy.court),
    ("SCOTUS petitions by Term", "scotus", GroupBy.term_year),
    ("SCOTUS petitions by nature-of-suit topic", "scotus", GroupBy.topic),
)


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
    with corpus.connect(corpus_db_path) as conn:
        overall = compute_report(conn, AnalyticsQuery()).total
        sections = [
            StatPackSection(
                title=title,
                court=court,
                group_by=dimension,
                buckets=compute_report(
                    conn, AnalyticsQuery(court=court, group_by=dimension)
                ).buckets,
            )
            for title, court, dimension in _STATPACK_SECTIONS
        ]
        return StatPack(
            corpus_rows=corpus.count(conn),
            resolved=overall.resolved,
            open=overall.open,
            overall=overall,
            sections=sections,
        )


def render_statpack_markdown(pack: StatPack) -> str:
    """Render a :class:`StatPack` as a publishable Markdown document.

    Leads with headline counts and the overall base rate, then one table per curated
    breakdown. Deterministic; safe on the empty pack (renders a one-line note)."""
    lines = ["# Corpus statpack", ""]
    if pack.corpus_rows == 0:
        lines.append("_Empty — no corpus present. Regenerated once a corpus is available._")
        return "\n".join(lines) + "\n"

    lines += [
        f"**{pack.corpus_rows}** case(s): {pack.resolved} resolved, {pack.open} open.",
        "",
        f"**Overall base rate (resolved):** {_disposition_summary(pack.overall)}",
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
    return "\n".join(lines) + "\n"


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
