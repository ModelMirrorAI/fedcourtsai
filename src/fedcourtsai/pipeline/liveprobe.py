"""Reachability probe for the supremecourt.gov docket-JSON channel.

The gate on the live-sources loader (docs/live-sources.md): before any ingest
code is written, establish — per October Term, walking backward from the
current one — whether the per-docket JSON is actually served, how far back the
document links reach, whether the schema is stable across Terms, and whether
the proceedings text carries the machine-matchable disposition orders the
ingest-time resolution needs. The findings note and the Term-floor decision
live in docs/live-sources-probe.md.

Strictly read-only and budget-free: this is not the CourtListener client — no
token, no governor. The three access facts from the design doc shape the
fetcher: a browser user-agent (the default programmatic UA is refused), a
polite ~1 request/second throttle, and backoff on errors. Sampling is a handful
of docket numbers per Term (low paid + low IFP numbers exist in every real
Term), so a Term where every sample is missing reads as "not served", while a
mixed Term reads through the per-record statuses.

The classification/aggregation half is pure (no I/O) so it is tested offline;
only :func:`probe_terms` touches the network.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable, Iterable, Sequence

import httpx
from pydantic import BaseModel, Field

from .cert_signals import match_disposition_signal

DOCKET_JSON_URL = "https://www.supremecourt.gov/rss/cases/JSON/{term:02d}-{number}.json"

# The default programmatic UA gets a 403 (verified live, 2026-07-10); any
# ordinary browser UA is accepted. Keep one pinned so probe runs are comparable.
BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"

# Low paid (…-1) and low IFP (…-5001) numbers are docketed in every real Term,
# so their absence separates "Term not served" from "number never used"; the
# mid/high numbers size how deep into a Term's sequence coverage runs.
DEFAULT_SAMPLE_NUMBERS: tuple[int, ...] = (1, 100, 400, 800, 5001, 5500, 6000)

# One retry after a pause is polite-client backoff, not resilience machinery:
# the probe is a one-off diagnostic and a stubborn upstream error is itself a
# finding (recorded as status="error"), never something to hammer through.
_RETRY_PAUSE_SECONDS = 5.0


class RecordProbe(BaseModel):
    """What one ``<term>-<number>.json`` fetch found."""

    term: int = Field(description="Two-digit October Term, e.g. 24 for OT2024")
    number: int = Field(description="Docket number within the Term")
    status: str = Field(description="ok | missing | error")
    http_status: int | None = Field(default=None, description="HTTP status, if a response came")
    detail: str | None = Field(default=None, description="Error detail / non-JSON note")
    keys: list[str] = Field(default_factory=list, description="Top-level JSON keys, sorted")
    case_type: str | None = Field(default=None, description="sJsonCaseType, e.g. Paid/Prisoner")
    docketed_date: str | None = Field(default=None, description="DocketedDate verbatim")
    has_lower_court: bool = Field(default=False, description="LowerCourt is non-empty")
    proceedings: int = Field(default=0, description="ProceedingsandOrder entry count")
    entries_with_links: int = Field(default=0, description="Entries carrying document Links")
    documents: int = Field(default=0, description="Total linked documents across entries")
    has_questions_presented: bool = Field(
        default=False, description="A QP link is present (top-level or entry-level)"
    )
    disposition_label: str | None = Field(
        default=None,
        description="First cert-disposition signal matched in the proceedings text "
        "(cert_signals.match_disposition_signal), e.g. 'cert denied'; None if no order matched",
    )


class TermProbe(BaseModel):
    """One Term's aggregate over its sampled records."""

    term: int = Field(description="Two-digit October Term")
    sampled: int = Field(description="Numbers probed")
    available: int = Field(description="Records served as JSON")
    missing: int = Field(description="404s / non-JSON responses")
    errors: int = Field(description="Transport or 5xx-after-retry failures")
    common_keys: list[str] = Field(
        default_factory=list, description="Top-level keys present on every available record"
    )
    variable_keys: list[str] = Field(
        default_factory=list, description="Keys present on some but not all available records"
    )
    proceedings: int = Field(default=0, description="Proceedings entries across the Term's records")
    entries_with_links: int = Field(default=0, description="Of those, entries carrying Links")
    documents: int = Field(default=0, description="Total linked documents")
    with_questions_presented: int = Field(default=0, description="Records with a QP link")
    with_disposition_signal: int = Field(
        default=0, description="Records whose proceedings matched a cert-disposition order"
    )
    disposition_labels: dict[str, int] = Field(
        default_factory=dict, description="Matched signal labels, counted"
    )


def classify_record(term: int, number: int, payload: object) -> RecordProbe:
    """Classify one served JSON payload (pure; no I/O).

    Anything that is not a JSON object is recorded as ``missing`` with a detail
    note — supremecourt.gov serves HTML error pages under some failure modes,
    and a non-object payload must read as "no docket here", never crash a run.
    """
    if not isinstance(payload, dict):
        return RecordProbe(
            term=term,
            number=number,
            status="missing",
            detail=f"non-object JSON payload ({type(payload).__name__})",
        )
    entries = [e for e in payload.get("ProceedingsandOrder") or [] if isinstance(e, dict)]
    linked = [e for e in entries if e.get("Links")]
    documents = sum(len(e.get("Links") or []) for e in linked)
    # The QP link travels either as a top-level key (QPLink) or as a linked
    # document titled "Questions Presented" — accept both shapes.
    has_qp = bool(payload.get("QPLink")) or any(
        "question" in str(link.get("Description", "")).lower()
        for e in linked
        for link in e.get("Links") or []
        if isinstance(link, dict)
    )
    label: str | None = None
    for entry in entries:
        matched = match_disposition_signal(str(entry.get("Text") or ""))
        if matched is not None:
            label = matched[1]
            break
    return RecordProbe(
        term=term,
        number=number,
        status="ok",
        http_status=200,
        keys=sorted(str(k) for k in payload),
        case_type=payload.get("sJsonCaseType"),
        docketed_date=payload.get("DocketedDate"),
        has_lower_court=bool(payload.get("LowerCourt")),
        proceedings=len(entries),
        entries_with_links=len(linked),
        documents=documents,
        has_questions_presented=has_qp,
        disposition_label=label,
    )


def summarize_term(term: int, records: Sequence[RecordProbe]) -> TermProbe:
    """Aggregate one Term's record probes (pure; no I/O)."""
    available = [r for r in records if r.status == "ok"]
    key_sets = [set(r.keys) for r in available]
    common = sorted(set.intersection(*key_sets)) if key_sets else []
    union = sorted(set.union(*key_sets)) if key_sets else []
    labels = Counter(r.disposition_label for r in available if r.disposition_label)
    return TermProbe(
        term=term,
        sampled=len(records),
        available=len(available),
        missing=sum(1 for r in records if r.status == "missing"),
        errors=sum(1 for r in records if r.status == "error"),
        common_keys=common,
        variable_keys=[k for k in union if k not in common],
        proceedings=sum(r.proceedings for r in available),
        entries_with_links=sum(r.entries_with_links for r in available),
        documents=sum(r.documents for r in available),
        with_questions_presented=sum(1 for r in available if r.has_questions_presented),
        with_disposition_signal=sum(1 for r in available if r.disposition_label),
        disposition_labels=dict(sorted(labels.items())),
    )


def render_markdown(terms: Sequence[TermProbe]) -> str:
    """The per-Term findings table for the step summary / findings note (pure)."""
    lines = [
        "| OT | served | doc-linked entries | documents | QP | disposition order |",
        "|----|--------|--------------------|-----------|----|-------------------|",
    ]
    for t in sorted(terms, key=lambda t: t.term, reverse=True):
        linked = f"{t.entries_with_links}/{t.proceedings}" if t.available else "—"
        labels = ", ".join(f"{k} x{v}" for k, v in t.disposition_labels.items()) or "—"
        lines.append(
            f"| {t.term} | {t.available}/{t.sampled} | {linked} | {t.documents} "
            f"| {t.with_questions_presented}/{t.available} "
            f"| {t.with_disposition_signal}/{t.available} ({labels}) |"
        )
    return "\n".join(lines)


def _fetch_record(
    client: httpx.Client, term: int, number: int, sleep: Callable[[float], None]
) -> RecordProbe:
    """One polite fetch → RecordProbe. Retries once on 403/429/5xx, then records."""
    url = DOCKET_JSON_URL.format(term=term, number=number)
    for attempt in (1, 2):
        try:
            response = client.get(url)
        except httpx.HTTPError as exc:
            if attempt == 1:
                sleep(_RETRY_PAUSE_SECONDS)
                continue
            return RecordProbe(
                term=term, number=number, status="error", detail=f"{type(exc).__name__}: {exc}"
            )
        if response.status_code == 404:
            return RecordProbe(term=term, number=number, status="missing", http_status=404)
        if response.status_code in (403, 429) or response.status_code >= 500:
            if attempt == 1:
                sleep(_RETRY_PAUSE_SECONDS)
                continue
            return RecordProbe(
                term=term, number=number, status="error", http_status=response.status_code
            )
        try:
            payload = response.json()
        except json.JSONDecodeError:
            return RecordProbe(
                term=term,
                number=number,
                status="missing",
                http_status=response.status_code,
                detail="non-JSON body",
            )
        return classify_record(term, number, payload)
    raise AssertionError("unreachable")  # pragma: no cover


def probe_terms(
    terms: Iterable[int],
    numbers: Sequence[int] = DEFAULT_SAMPLE_NUMBERS,
    *,
    throttle_seconds: float = 1.0,
    client: httpx.Client | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[list[TermProbe], list[RecordProbe]]:
    """Probe each Term's sample numbers politely; return (per-Term, per-record).

    The only networked function in the module. ``client`` and ``sleep`` are
    injectable for tests; the default client pins the browser UA and a sane
    timeout. Throttles between every request (including across Terms).
    """
    own_client = client is None
    if client is None:
        client = httpx.Client(
            headers={"User-Agent": BROWSER_USER_AGENT},
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )
    records: list[RecordProbe] = []
    summaries: list[TermProbe] = []
    try:
        first = True
        for term in terms:
            term_records: list[RecordProbe] = []
            for number in numbers:
                if not first:
                    sleep(throttle_seconds)
                first = False
                term_records.append(_fetch_record(client, term, number, sleep))
            records.extend(term_records)
            summaries.append(summarize_term(term, term_records))
    finally:
        if own_client:
            client.close()
    return summaries, records
