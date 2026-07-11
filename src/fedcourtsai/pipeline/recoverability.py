"""Read-only recoverability probe for sparse SCOTUS petition dispositions.

A diagnostic, **not** a data-production path: it fetches a docket (and its linked
opinion cluster) from the CourtListener REST API and decides whether the
disposition the pipeline needs is *actually recoverable from CourtListener* — an
ingestion gap a pull re-fetch can close — or *genuinely absent* upstream, so
the case belongs out of scope.

The motivating gap: the bulk-era load ingested no docket entries
and fills ``disposition`` only via the ``opinion_clusters`` LEFT JOIN, so a cert
**denial** — whose order lives in a docket entry, with no opinion cluster — lands
with ``disposition = NULL`` and a null decision date. This probe reads what a live
fetch actually exposes for such dockets so the next build (targeted re-ingest vs.
living with the gap) is measured rather than assumed.

It writes nothing — no corpus, no ``data/``, no DVC, no git. The pure classifier
(:func:`classify`) is separated from the fetch (:func:`probe_docket`) so the
decision is unit-testable against a stubbed client with no network.
"""

from __future__ import annotations

import random
import re
from enum import StrEnum
from typing import Any, NamedTuple, Protocol

from pydantic import BaseModel, Field

from .. import corpus
from ..schemas import Disposition
from .cert_signals import match_disposition_signal
from .ingest import normalize_disposition
from .outcome import is_machine_readable

JsonDict = dict[str, Any]


class RecoverabilityClient(Protocol):
    """The read-only slice of :class:`CourtListenerClient` the probe depends on.

    A structural type so tests can supply a canned stub (see ``docs/testing.md``)
    with no network — the probe only ever *reads*.
    """

    def get_docket(self, docket_id: int) -> JsonDict: ...

    def iter_docket_entries(self, docket_id: int) -> list[JsonDict]: ...

    def get_opinion_cluster(self, cluster_id: int) -> JsonDict: ...


class Classification(StrEnum):
    """The verdict for one docket's disposition."""

    recoverable = "RECOVERABLE"
    absent = "ABSENT"
    ambiguous = "AMBIGUOUS"


class EntrySignal(BaseModel):
    """A docket entry whose text signals a concrete cert disposition."""

    entry_id: int | None = Field(default=None, description="CourtListener docket-entry id, if any")
    disposition: Disposition = Field(description="Disposition the entry text signals")
    label: str = Field(description="Human label for the matched signal, e.g. 'cert denied'")
    snippet: str = Field(description="The matched text, with a little surrounding context")


class ClusterInfo(BaseModel):
    """The disposition-bearing facts of a docket's linked opinion cluster."""

    cluster_id: int | None = Field(default=None, description="CourtListener cluster id")
    raw_disposition: str | None = Field(default=None, description="Cluster `disposition` verbatim")
    disposition: Disposition | None = Field(
        default=None, description="Normalized cluster disposition (None if blank)"
    )
    precedential_status: str | None = Field(default=None)
    date_filed: str | None = Field(default=None, description="Cluster decision date, if any")
    citations: list[str] = Field(default_factory=list, description="Reporter citations, if any")


class DocketProbe(BaseModel):
    """The full recoverability report for one docket."""

    court: str
    docket: int
    case_name: str | None = None
    date_filed: str | None = None
    date_terminated: str | None = None
    raw_docket_disposition: str | None = Field(
        default=None, description="Docket-level `disposition`/`nature_of_judgement` verbatim"
    )
    docket_disposition: Disposition | None = Field(
        default=None, description="Normalized docket-level disposition (None if blank)"
    )
    docket_entry_count: int = 0
    entry_signals: list[EntrySignal] = Field(default_factory=list)
    cluster: ClusterInfo | None = None
    classification: Classification | None = Field(
        default=None, description="Verdict; None when the fetch errored"
    )
    source: str | None = Field(
        default=None, description="What makes it recoverable: entry-order / cluster-disposition / …"
    )
    reason: str = Field(default="", description="One-line explanation of the verdict")
    error: str | None = Field(default=None, description="Fetch error, if the docket could not load")
    stratum: str | None = Field(
        default=None,
        description="Sample stratum the docket was drawn from, when probed via the "
        "stratified dateless sample; None for an ad-hoc probe",
    )

    @property
    def docket_id_str(self) -> str:
        return f"{self.court}/{self.docket}"


class ProbeReport(BaseModel):
    """The machine-readable report over every probed docket."""

    dockets: list[DocketProbe] = Field(default_factory=list)

    def counts(self) -> dict[str, int]:
        """Tally dockets by verdict; unclassified (fetch-failed) dockets under ``error``.

        A docket that classified despite a non-fatal note (e.g. a missing cluster)
        counts under its verdict — only a docket with no verdict is an ``error``.
        """
        tally: dict[str, int] = {c.value: 0 for c in Classification}
        tally["error"] = 0
        for d in self.dockets:
            if d.classification is None:
                tally["error"] += 1
            else:
                tally[d.classification.value] += 1
        return tally


def _clean_str(value: Any) -> str | None:
    """A trimmed, non-empty string, else None (bulk/API blanks render as None)."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _cluster_id_from_url(url: str) -> int | None:
    """Parse the trailing cluster id out of a CourtListener cluster URL."""
    match = re.search(r"/clusters/(\d+)/?", url)
    return int(match.group(1)) if match else None


def first_cluster_id(docket: JsonDict) -> int | None:
    """The id of the docket's first linked opinion cluster, if any.

    Public: the pull-side cluster enrichment follows the same link the probe
    does, so both read the docket's ``clusters`` list through one parser.
    """
    clusters = docket.get("clusters") or []
    for entry in clusters:
        if isinstance(entry, int):
            return entry
        if isinstance(entry, str):
            cid = _cluster_id_from_url(entry)
            if cid is not None:
                return cid
    return None


def _entry_text(entry: JsonDict) -> str:
    """All human-readable text on a docket entry (entry + its recap documents)."""
    parts: list[str] = []
    for key in ("description", "short_description"):
        text = _clean_str(entry.get(key))
        if text:
            parts.append(text)
    for doc in entry.get("recap_documents") or []:
        if isinstance(doc, dict):
            for key in ("description", "short_description"):
                text = _clean_str(doc.get(key))
                if text:
                    parts.append(text)
    return "  ".join(parts)


def scan_entries(entries: list[JsonDict]) -> list[EntrySignal]:
    """Find every docket entry whose text signals a concrete cert disposition."""
    signals: list[EntrySignal] = []
    for entry in entries:
        matched = match_disposition_signal(_entry_text(entry))
        if matched is None:
            continue
        disposition, label, snippet = matched
        raw_id = entry.get("id")
        signals.append(
            EntrySignal(
                entry_id=int(raw_id) if isinstance(raw_id, int) else None,
                disposition=disposition,
                label=label,
                snippet=snippet,
            )
        )
    return signals


def _docket_disposition(docket: JsonDict) -> tuple[str | None, Disposition | None]:
    """The docket-level disposition, verbatim and normalized (mirrors ingest)."""
    for key in ("disposition", "nature_of_judgement", "outcome"):
        raw = _clean_str(docket.get(key))
        if raw is not None:
            return raw, normalize_disposition(raw)
    return None, None


def _citation_strings(cluster: JsonDict) -> list[str]:
    """Render a cluster's citations to human strings, defensively across shapes."""
    out: list[str] = []
    for cite in cluster.get("citations") or []:
        if isinstance(cite, str):
            text = _clean_str(cite)
            if text:
                out.append(text)
        elif isinstance(cite, dict):
            volume = _clean_str(cite.get("volume"))
            reporter = _clean_str(cite.get("reporter"))
            page = _clean_str(cite.get("page"))
            joined = " ".join(p for p in (volume, reporter, page) if p)
            text = joined or _clean_str(cite.get("cite"))
            if text:
                out.append(text)
    return out


def build_cluster_info(cluster: JsonDict) -> ClusterInfo:
    """Lift the disposition-bearing facts out of a fetched opinion cluster."""
    raw = _clean_str(cluster.get("disposition"))
    cluster_id = cluster.get("id")
    return ClusterInfo(
        cluster_id=int(cluster_id) if isinstance(cluster_id, int) else None,
        raw_disposition=raw,
        disposition=normalize_disposition(raw) if raw is not None else None,
        precedential_status=_clean_str(cluster.get("precedential_status")),
        date_filed=_clean_str(cluster.get("date_filed")),
        citations=_citation_strings(cluster),
    )


def classify(probe: DocketProbe) -> DocketProbe:
    """Set ``classification`` / ``source`` / ``reason`` from the gathered facts.

    Pure. The taxonomy answers the build question — is the disposition recoverable
    from CourtListener (an ingestion gap) or genuinely absent?

    - **RECOVERABLE** — a concrete disposition is exposed (a cert-order entry or a
      machine-readable cluster/docket disposition), or a decided-and-published
      signal that a targeted re-ingest can follow (a cluster citation, a
      termination date). The ``source`` names the strongest such signal.
    - **AMBIGUOUS** — the docket looks decided but nothing here recovers the
      disposition: a linked cluster with no disposition and no citation, or text
      that normalized only to the ``other`` catch-all.
    - **ABSENT** — a genuinely bare shell: no disposition anywhere, no cluster, no
      signal entries, no termination date.
    """
    cluster = probe.cluster
    entry_signal = next(
        (s for s in probe.entry_signals if is_machine_readable(s.disposition)), None
    )
    cluster_readable = cluster is not None and is_machine_readable(cluster.disposition)
    docket_readable = is_machine_readable(probe.docket_disposition)
    has_citation = bool(cluster and cluster.citations)
    has_termination = probe.date_terminated is not None

    if entry_signal is not None:
        probe.classification = Classification.recoverable
        probe.source = "entry-order"
        probe.reason = f"docket entry signals a {entry_signal.disposition} ({entry_signal.label})"
    elif cluster_readable:
        assert cluster is not None
        probe.classification = Classification.recoverable
        probe.source = "cluster-disposition"
        probe.reason = f"linked opinion cluster exposes a {cluster.disposition} disposition"
    elif docket_readable:
        probe.classification = Classification.recoverable
        probe.source = "docket-disposition"
        probe.reason = f"docket-level disposition is machine-readable ({probe.docket_disposition})"
    elif has_citation:
        probe.classification = Classification.recoverable
        probe.source = "citation"
        probe.reason = (
            "linked cluster carries a reporter citation — the published opinion's "
            "disposition is recoverable by enrichment"
        )
    elif has_termination:
        probe.classification = Classification.recoverable
        probe.source = "date_terminated"
        probe.reason = (
            "docket carries a termination date — decided upstream; re-ingesting it "
            "gives the decision date outcome detection needs"
        )
    elif cluster is not None or probe.docket_disposition is not None or probe.entry_signals:
        probe.classification = Classification.ambiguous
        probe.source = None
        if cluster is not None:
            probe.reason = "linked opinion cluster present but exposes no disposition or citation"
        elif probe.docket_disposition is not None:
            probe.reason = "disposition text present but classifies only as 'other'"
        else:
            probe.reason = "docket entries mention a disposition but none is machine-readable"
    else:
        probe.classification = Classification.absent
        probe.source = None
        probe.reason = (
            "no disposition, opinion cluster, cert-order entry, or termination date — "
            "genuinely bare upstream"
        )
    return probe


def probe_docket(client: RecoverabilityClient, court: str, docket_id: int) -> DocketProbe:
    """Fetch one docket (and its cluster) and classify its recoverability.

    Read-only. Any fetch failure is captured on the returned probe's ``error``
    rather than raised, so a batch run reports every docket it was asked about.
    """
    probe = DocketProbe(court=court, docket=docket_id)
    try:
        docket = client.get_docket(docket_id)
    except Exception as exc:
        probe.error = f"{type(exc).__name__}: {exc}"
        return probe

    probe.case_name = _clean_str(docket.get("case_name") or docket.get("case_name_full"))
    probe.date_filed = _clean_str(docket.get("date_filed"))
    probe.date_terminated = _clean_str(docket.get("date_terminated") or docket.get("date_decided"))
    probe.raw_docket_disposition, probe.docket_disposition = _docket_disposition(docket)

    try:
        entries = client.iter_docket_entries(docket_id)
    except Exception as exc:
        entries = []
        probe.error = f"docket-entries: {type(exc).__name__}: {exc}"
    probe.docket_entry_count = len(entries)
    probe.entry_signals = scan_entries(entries)

    cluster_id = first_cluster_id(docket)
    if cluster_id is not None:
        try:
            probe.cluster = build_cluster_info(client.get_opinion_cluster(cluster_id))
        except Exception as exc:
            probe.cluster = ClusterInfo(cluster_id=cluster_id)
            note = f"cluster {cluster_id}: {type(exc).__name__}: {exc}"
            probe.error = f"{probe.error}; {note}" if probe.error else note

    return classify(probe)


def probe_dockets(client: RecoverabilityClient, pairs: list[tuple[str, int]]) -> ProbeReport:
    """Probe each ``(court, docket_id)`` pair and collect the reports, in order."""
    return ProbeReport(dockets=[probe_docket(client, court, docket) for court, docket in pairs])


# --- stratified sample over the dateless resolved slice -------------------------


class SampleTarget(NamedTuple):
    """One docket drawn for the stratified dateless sample."""

    stratum: str
    court: str
    docket_id: int


# The strata the dateless-resolved sample is drawn from, in allocation order:
# the SCOTUS modern-cert slice (highest back-test value: it feeds the cert
# back-test set), the dominant circuit slice, and everything else pooled. The
# per-stratum read sizes what a REST re-fetch can actually recover, and from
# which source, before the pull budget is spent on the drip.
SAMPLE_STRATA: tuple[str, ...] = ("scotus-modern-cert", "ca4", "other-circuits")

# Resolved (disposition set) but carrying no decision-time signal at all.
_DATELESS_RESOLVED_SQL = (
    "disposition IS NOT NULL AND date_decided IS NULL "
    "AND date_cert_granted IS NULL AND date_cert_denied IS NULL"
)


def _stratum_candidates(conn: corpus.ReadConnection, stratum: str) -> list[tuple[str, int]]:
    """The dateless-resolved ``(court, docket_id)`` candidates of one stratum,
    in stable ``case_id`` order (the deterministic base the sampler draws from)."""
    params: tuple[str, ...]
    if stratum == "scotus-modern-cert":
        clause, params = "court = ?", ("scotus",)
    elif stratum == "other-circuits":
        clause, params = "court NOT IN (?, ?)", ("scotus", "ca4")
    else:
        clause, params = "court = ?", (stratum,)
    rows = conn.execute(
        f"SELECT case_id, court, docket_number FROM cases "
        f"WHERE {clause} AND {_DATELESS_RESOLVED_SQL} ORDER BY case_id",
        params,
    ).fetchall()
    pairs: list[tuple[str, int]] = []
    for record in rows:
        if stratum == "scotus-modern-cert" and (
            corpus.scotus_term_year(record["docket_number"]) is None
        ):
            continue
        docket = int(str(record["case_id"]).rsplit("/", 1)[1])
        pairs.append((record["court"], docket))
    return pairs


def sample_dateless_targets(
    conn: corpus.ReadConnection, *, total: int, seed: int = 0
) -> list[SampleTarget]:
    """Draw a stratified random sample of the dateless resolved slice.

    ``total`` splits evenly across :data:`SAMPLE_STRATA` (remainder to the earlier
    strata); a stratum short of candidates yields what it has and the shortfall
    tops up the later strata, so the draw uses the full budget whenever the slice
    is large enough. Deterministic for a given corpus and ``seed`` — candidates
    are collected in stable order and drawn with a seeded PRNG — so a probe run
    is reproducible.
    """
    if total <= 0:
        return []
    rng = random.Random(seed)
    base, extra = divmod(total, len(SAMPLE_STRATA))
    shares = [base + (1 if i < extra else 0) for i in range(len(SAMPLE_STRATA))]
    targets: list[SampleTarget] = []
    carry = 0
    for stratum, share in zip(SAMPLE_STRATA, shares, strict=True):
        candidates = _stratum_candidates(conn, stratum)
        want = min(share + carry, len(candidates))
        carry = share + carry - want
        for court, docket in sorted(rng.sample(candidates, want)):
            targets.append(SampleTarget(stratum, court, docket))
    return targets


def probe_sample(client: RecoverabilityClient, targets: list[SampleTarget]) -> ProbeReport:
    """Probe each sampled docket, tagging every probe with its stratum."""
    dockets = []
    for stratum, court, docket in targets:
        probe = probe_docket(client, court, docket)
        probe.stratum = stratum
        dockets.append(probe)
    return ProbeReport(dockets=dockets)


def dated_share_snapshot(conn: corpus.ReadConnection) -> tuple[int, int]:
    """``(dated, machine_readable_resolved)`` over the corpus at probe time.

    The point-in-time "before" measurement the sample report carries: how many
    machine-readable resolved rows already hold any resolution date (decision or
    cert-stage), out of the whole back-testable slice.
    """
    record = conn.execute(
        "SELECT "
        "SUM(CASE WHEN date_decided IS NOT NULL OR date_cert_granted IS NOT NULL "
        "OR date_cert_denied IS NOT NULL THEN 1 ELSE 0 END) AS dated, "
        "COUNT(*) AS total FROM cases "
        "WHERE disposition IS NOT NULL AND disposition != ?",
        (Disposition.other.value,),
    ).fetchone()
    return int(record["dated"] or 0), int(record["total"])


def parse_docket_pairs(values: list[str]) -> list[tuple[str, int]]:
    """Parse ``court/docket`` tokens (comma-joined or repeated) into typed pairs.

    Accepts both a repeated option and a comma-separated list, deduplicating while
    preserving first-seen order. Raises :class:`ValueError` on a malformed token.
    """
    pairs: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()
    for value in values:
        for raw_token in value.split(","):
            token = raw_token.strip()
            if not token:
                continue
            court, sep, docket = token.partition("/")
            court = court.strip()
            docket = docket.strip()
            if not sep or not court or not docket:
                raise ValueError(f"expected court/docket, got {token!r}")
            try:
                docket_id = int(docket)
            except ValueError as exc:
                raise ValueError(f"docket id must be an integer in {token!r}") from exc
            pair = (court, docket_id)
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)
    if not pairs:
        raise ValueError("no dockets given")
    return pairs


def render_summary(report: ProbeReport, *, dated_share: tuple[int, int] | None = None) -> str:
    """Render the report as a short Markdown summary (for the Actions step summary).

    ``dated_share`` — the :func:`dated_share_snapshot` pair — adds the
    point-in-time dated-share line a sampled run reports as its "before" number.
    """
    counts = report.counts()
    lines = ["## Recoverability probe", ""]
    summary_bits = [f"**{counts[c.value]}** {c.value}" for c in Classification]
    if counts["error"]:
        summary_bits.append(f"**{counts['error']}** error")
    lines.append(f"{len(report.dockets)} docket(s): " + " · ".join(summary_bits))
    if dated_share is not None:
        dated, total = dated_share
        pct = f" ({dated / total * 100:.1f}%)" if total else ""
        lines.extend(
            [
                "",
                f"**Dated share at probe time:** {dated} of {total} machine-readable "
                f"resolved case(s) carry a resolution date{pct}.",
            ]
        )
    strata = [d.stratum for d in report.dockets if d.stratum is not None]
    if strata:
        lines.extend(
            ["", "| Stratum | dockets | " + " | ".join(c.value for c in Classification) + " |"]
        )
        lines.append("| --- | --: | " + " | ".join("--:" for _ in Classification) + " |")
        for stratum in dict.fromkeys(strata):  # first-seen order, deduplicated
            members = [d for d in report.dockets if d.stratum == stratum]
            by_verdict = ProbeReport(dockets=members).counts()
            cells = " | ".join(str(by_verdict[c.value]) for c in Classification)
            lines.append(f"| {stratum} | {len(members)} | {cells} |")
    lines.extend(["", "| Docket | Verdict | Source | Reason |", "| --- | --- | --- | --- |"])
    for d in report.dockets:
        if d.classification is None:
            verdict, source, reason = "ERROR", "—", d.error or "fetch failed"
        else:
            verdict = d.classification.value
            source = d.source or "—"
            reason = f"{d.reason} (note: {d.error})" if d.error else d.reason
        lines.append(f"| `{d.docket_id_str}` | {verdict} | {source} | {reason} |")
    return "\n".join(lines) + "\n"
