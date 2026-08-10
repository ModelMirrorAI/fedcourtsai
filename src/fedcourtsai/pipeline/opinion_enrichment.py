"""Opinion-cluster enrichment: reporter cites and opinion bodies for the merits track.

The corpus records what a docket *did* — the cert disposition, the merits
judgment — but not what the Court *wrote*. This pass fills that in for the
registered merits population: each SCOTUS row carrying a cert grant
(``date_cert_granted``) is walked to its published opinion cluster, and the
cluster's reporter ``citations`` / ``citation_count`` and the lead opinion's
body land on the row. Those are the fields the retrieval surface's prior
ranking keys on, and the opinion body is the input a semantic claim family
needs — so coverage here is the precondition for both, not an end in itself.

**Scope is the budget argument.** Two REST requests per case (cluster, then
opinion), three where the stored snapshot links no cluster and the docket must
be re-fetched to find one. The merits track is ~1,250 rows all-time and ~65 a
Term ongoing, so the whole standing population fits inside a few windows of the
held tier's daily allowance and the ongoing cost is negligible against it —
which is exactly why the pass is scoped to the merits track rather than run
corpus-wide. Bulk-scale opinion coverage waits on the replication channel
(``docs/data-sources.md``); this is the targeted channel that makes the merits
track usable now. ``max_cases`` bounds any one run on top of the client's own
governor, and a :class:`RateBudgetExceeded` stops the walk cleanly with the
cases it never reached reported, exactly as the pull rotation does.

**Resolved-only, and idempotent on the presence bit.** A row already carrying
``has_opinion`` is skipped, so a converged corpus spends nothing; a pending
grant has no published opinion to find and simply reports no cluster. The
enrichment writes through :func:`fedcourtsai.corpus.upsert_rows` — never a
direct ``UPDATE`` — because that is the seam
:func:`fedcourtsai.casestore.read_opinion_text` rests its freshness invariant
on: every opinion write re-mirrors the case's stored ``case.json``, so the
content store is never staler than the index for the body. The row is projected
from the stored row rather than re-normalized from an upstream docket, since
the pass adds fields to a case the corpus already knows rather than re-serving
it.

**A stored hyperlink is a claim, not a target.** Snapshot payloads carry
upstream URLs, and none of them is ever fetched as given: :func:`resource_id`
requires a link to resolve under the client's own REST base and to name
``<resource>/<numeric id>/``, and only that id reaches the client, which builds
its request path itself. A payload therefore cannot steer a request off the
CourtListener API however it was written.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Mapping
from typing import Any, Final
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..courtlistener import CourtListenerClient, RateBudgetExceeded

# A modest default: the pass is a standing maintenance step, not a bulk load,
# and a small cap keeps one run's spend legible beside the pull windows that
# share the same daily budget.
DEFAULT_MAX_CASES: Final = 25

# Upstream ids are integers; a link whose id segment is anything else is not a
# link this client can follow. Deliberately not `str.isdigit`, which accepts
# non-ASCII digit forms `int()` would then happily parse.
_ID_RE: Final = re.compile(r"[0-9]+")


class OpinionEnrichmentResult(BaseModel):
    """What one enrichment pass over the merits track did (or would do)."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the corpus (False = dry-run)")
    eligible: int = Field(ge=0, description="Granted SCOTUS rows still lacking an opinion")
    considered: int = Field(ge=0, description="Eligible rows the per-run cap admitted")
    enriched: int = Field(ge=0, description="Rows an opinion body and/or citations landed on")
    no_cluster: int = Field(ge=0, description="Rows whose docket links no opinion cluster")
    no_body: int = Field(
        ge=0,
        description="Rows whose cluster yielded no body — no followable sub-opinion, "
        "or a lead opinion with no extracted plain text",
    )
    requests: int = Field(ge=0, description="REST requests the pass spent")
    failed: list[tuple[str, str]] = Field(
        default_factory=list, description="(case_id, reason) for each row that raised"
    )
    stopped: str | None = Field(
        default=None, description="Why the walk ended early, or None when it ran the cap out"
    )
    deferred: list[str] = Field(
        default_factory=list, description="Admitted case ids the walk never reached"
    )


def resource_id(url: object, *, base_url: str, resource: str) -> int | None:
    """The integer id a CourtListener REST hyperlink names, or ``None``.

    The guard between a stored payload and an outbound request. A link passes
    only if it resolves under ``base_url`` — same scheme, same host, same API
    path prefix — and names ``<resource>/<numeric id>/`` beneath it; anything
    else (another host, another API version, a relative path, a nested route, a
    non-numeric id, a non-string) yields ``None``. The caller keeps the id and
    discards the link, so the request path is always the client's own
    construction rather than text a payload supplied.
    """
    if not isinstance(url, str):
        return None
    base = urlsplit(base_url)
    target = urlsplit(url.strip())
    if target.scheme != base.scheme or target.netloc != base.netloc:
        return None
    prefix = base.path if base.path.endswith("/") else f"{base.path}/"
    if not target.path.startswith(prefix):
        return None
    segments = target.path[len(prefix) :].strip("/").split("/")
    if len(segments) != 2 or segments[0] != resource:
        return None
    return int(segments[1]) if _ID_RE.fullmatch(segments[1]) else None


def _first_resource_id(links: Any, *, base_url: str, resource: str) -> int | None:
    """The first followable id in a list of upstream hyperlinks, or ``None``."""
    if not isinstance(links, list):
        return None
    for link in links:
        found = resource_id(link, base_url=base_url, resource=resource)
        if found is not None:
            return found
    return None


def citation_strings(payload: Mapping[str, Any]) -> list[str]:
    """A cluster's reporter citations as the flat strings the corpus column stores.

    Upstream serves each citation structured (``{volume, reporter, page}``);
    the corpus stores the assembled reporter cite, which is what the retrieval
    surface's ``--citation`` overlap match compares. Order is preserved
    (upstream leads with the official reporter) and duplicates collapse.
    """
    out: list[str] = []
    for item in payload.get("citations") or []:
        if isinstance(item, Mapping):
            parts = [str(item.get(key) or "").strip() for key in ("volume", "reporter", "page")]
            text = " ".join(part for part in parts if part)
        else:
            text = str(item).strip()
        if text and text not in out:
            out.append(text)
    return out


def _opinion_body(payload: Mapping[str, Any]) -> str | None:
    """The opinion's extracted body, or ``None`` when upstream serves none.

    ``plain_text`` only: upstream also carries HTML renderings, and converting
    one would put a parser of ours between the court's words and the corpus.
    A body-less opinion is reported rather than approximated, and its cluster's
    citations still land.
    """
    text = payload.get("plain_text")
    return text.strip() or None if isinstance(text, str) else None


def _cluster_id(
    client: CourtListenerClient,
    conn: sqlite3.Connection,
    row: corpus.CorpusRow,
    docket_id: int,
) -> tuple[int | None, int]:
    """``(cluster id, requests spent)`` for a case — snapshot first, docket second.

    The stored snapshot is the free source: a REST-shaped docket payload
    already carries the ``clusters`` list, so a case the corpus has snapshotted
    costs nothing to resolve. Only a case with no snapshotted link pays the
    extra docket fetch.
    """
    snapshot = corpus.latest_snapshot(conn, row.case_id)
    if snapshot is not None:
        stored = _first_resource_id(
            snapshot[1].get("clusters"), base_url=client.base_url, resource="clusters"
        )
        if stored is not None:
            return stored, 0
    docket = client.get_docket(docket_id)
    return (
        _first_resource_id(docket.get("clusters"), base_url=client.base_url, resource="clusters"),
        1,
    )


def _enriched_row(
    row: corpus.CorpusRow, cluster: Mapping[str, Any], body: str | None
) -> corpus.CorpusRow:
    """The stored row with the cluster's facts and the opinion body applied.

    Re-validated rather than copied, so ``has_opinion`` derives from the body
    the way it does on any other ingest; every other column carries through
    untouched, because the write is a full-row upsert.
    """
    citations = citation_strings(cluster)
    count = cluster.get("citation_count")
    return corpus.CorpusRow.model_validate(
        {
            **row.model_dump(),
            "citations": citations or row.citations,
            "citation_count": count if isinstance(count, int) else row.citation_count,
            "opinion_text": body or row.opinion_text,
        }
    )


def enrich_opinions(
    conn: sqlite3.Connection,
    client: CourtListenerClient,
    *,
    apply: bool,
    max_cases: int = DEFAULT_MAX_CASES,
) -> OpinionEnrichmentResult:
    """Walk the merits track's opinion-less rows to their clusters and bodies.

    Eligibility is the registered merits scope with the presence bit as the
    idempotency key: a SCOTUS row with ``date_cert_granted`` set and
    ``has_opinion`` clear. Candidates are taken in ``case_id`` order and capped
    at ``max_cases``; the rest are left for the next run, which re-derives the
    same predicate.

    Each case costs the cluster and opinion fetches (plus a docket fetch when
    its snapshot links no cluster). A case whose docket links no cluster, or
    whose lead opinion carries no extracted text, is counted and left alone —
    a coverage gap, reported rather than fatal. A per-case REST failure is
    recorded and the walk continues, because one bad docket must not cost the
    run; :class:`RateBudgetExceeded` stops it outright, since every later case
    would hit the same wall.

    Dry-run by default: ``apply`` gates only the writes, so the request spend
    and the coverage report are identical either way — the dry run is what the
    spend is inspected from.
    """
    candidates = [
        row
        for row in corpus.iter_rows(conn, court="scotus")
        if row.date_cert_granted is not None and not row.has_opinion
    ]
    admitted = candidates[: max(max_cases, 0)]
    result = OpinionEnrichmentResult(
        applied=apply,
        eligible=len(candidates),
        considered=len(admitted),
        enriched=0,
        no_cluster=0,
        no_body=0,
        requests=0,
    )
    updates: list[corpus.CorpusRow] = []
    for index, row in enumerate(admitted):
        _, _, docket_raw = row.case_id.partition("/")
        if not docket_raw.isdigit():
            result.failed.append((row.case_id, "case id carries no numeric docket id"))
            continue
        try:
            cluster_id, spent = _cluster_id(client, conn, row, int(docket_raw))
            result.requests += spent
            if cluster_id is None:
                result.no_cluster += 1
                continue
            cluster = client.get_cluster(cluster_id)
            result.requests += 1
            opinion_id = _first_resource_id(
                cluster.get("sub_opinions"), base_url=client.base_url, resource="opinions"
            )
            body: str | None = None
            if opinion_id is not None:
                body = _opinion_body(client.get_opinion(opinion_id))
                result.requests += 1
            if body is None:
                result.no_body += 1
            # A cluster that adds nothing the row already carries is converged,
            # not enriched: writing it back would report coverage the pass did
            # not produce.
            enriched = _enriched_row(row, cluster, body)
            if enriched != row:
                updates.append(enriched)
        except RateBudgetExceeded as exc:
            result.stopped = f"API budget exhausted ({exc})"
            result.deferred = [pending.case_id for pending in admitted[index:]]
            break
        except httpx.HTTPError as exc:
            result.failed.append((row.case_id, f"{type(exc).__name__}: {exc}"))
            continue
    result.enriched = len(updates)
    if apply and updates:
        corpus.upsert_rows(conn, updates)
    return result
