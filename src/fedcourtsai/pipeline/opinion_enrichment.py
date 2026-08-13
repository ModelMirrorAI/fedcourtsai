"""Opinion-cluster enrichment: reporter cites and opinion bodies for granted cases.

The corpus records what a docket *did* — the cert disposition, the merits
judgment — but not what the Court *wrote*. This pass fills that in for the
cert-granted SCOTUS slice: each row carrying ``date_cert_granted`` is walked to
its published opinion cluster, and the cluster's reporter ``citations`` /
``citation_count`` and the lead opinion's body land on the row. Those are the
fields the retrieval surface's prior ranking keys on, and the opinion body is
the input a semantic claim family needs — so coverage here is the precondition
for both, not an end in itself.

**Scope is the budget argument.** Three REST requests per case — the docket
(for its ``clusters`` list), the cluster, and the lead opinion — dropping to two
where a stored REST-shaped snapshot already links the cluster. That is rare on
this population: a granted SCOTUS docket is the set the live channel re-polls,
so its newest snapshot is normally a supremecourt.gov payload, which carries no
``clusters`` list. The cert-granted slice is ≈1,250 rows all-time (grants and
GVRs together) and ≈120 to 130 a Term, so converging the standing backlog costs
≈3,750 requests and holding it ≈400 a Term — days of the allowance the pull
windows leave, not a budget event. ``max_cases`` bounds any one run on top of
the client's own governor, and a :class:`RateBudgetExceeded` stops the walk
cleanly with the cases it never reached reported. Corpus-wide opinion coverage
is a different problem with a different answer: the replication channel
(``docs/data-sources.md``), not more REST.

**Grant-scoped, and idempotent on the presence bit.** A row already carrying
``has_opinion`` is skipped, so a converged corpus spends nothing. The scope is
the cert grant rather than ``corpus.opens_merits_proceeding`` because the
question here is "did this case produce a published opinion", which a summary
reversal can answer yes to; the cost is that the slice also admits the grants
that never produce one. An undecided grant has no cluster to link yet and
reports as such, converging on the run after its opinion publishes. Candidates
are walked in ``case_id`` order, deterministically: a converged case drops out
of the next run's predicate, and one that found no cluster is retried, which is
what lets a grant pick up its opinion once published. That retry is also the
pass's one standing limitation — a grant that never publishes an opinion at all
(a GVR, a DIG) never converges, so once that residue exceeds ``max_cases`` the
cap can no longer reach past it. It is an operator-run command for that reason;
putting it on a schedule wants an ordering, or a last-attempted cursor, that
the residue cannot sit at the head of.

**The pass refuses to guess which document is the case's.** ``has_opinion``
max-latches, so a wrong body is not self-healing: the row stops matching this
pass's own predicate and no later run revisits it. So a docket linking more than
one cluster is refused rather than resolved by taking the first; a fetched
cluster must name the docket it was reached from; and an opinion whose upstream
``type`` says it is a separate writing — a concurrence, a dissent, an addendum
— never becomes the case's body. Each refusal is counted and the citations
still land, so a coverage gap is visible in the report rather than papered over
with a plausible-looking body.

**Writes go through the ingestion upsert.** The enrichment calls
:func:`fedcourtsai.corpus.upsert_rows` — never a direct ``UPDATE`` — because
that is the seam :func:`fedcourtsai.casestore.read_opinion_text` rests its
freshness invariant on: every opinion write re-mirrors the case's stored
``case.json``, so the content store is never staler than the index for the body.
The row is projected from the stored row rather than re-normalized from an
upstream docket, since the pass adds fields to a case the corpus already knows
rather than re-serving it, and each case is written as it converges so a run cut
short keeps the coverage it already paid for.

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
from ..supremecourt import is_live_docket_id

# A modest default: the pass is a standing maintenance step, not a bulk load,
# and the cap keeps one run's spend legible beside the pull windows that share
# the same daily budget — about half the held tier's hourly ceiling at three
# requests a case (see docs/budget.md for the tier).
DEFAULT_MAX_CASES: Final = 50

# Upstream ids are integers; a link whose id segment is anything else is not a
# link this client can follow. Deliberately not `str.isdigit`, which accepts
# non-ASCII digit forms `int()` would then happily parse.
_ID_RE: Final = re.compile(r"[0-9]+")

# An upper bound on a stored opinion body. The longest opinions upstream serves
# run to a few hundred thousand characters, so this refuses a response that is
# not one — the body travels into SQLite and then an S3 object, and a response
# read whole into memory is the wrong place to discover an unbounded one.
MAX_OPINION_CHARS: Final = 2_000_000

# Upstream's opinion `type` vocabulary spells a separate writing out in the
# code's own words ("030concurrence", "040dissent"), so the test is on the word
# rather than the numeric prefix, which upstream is free to renumber. A type
# this does not recognize — including an absent one — is accepted: refusing on
# an unknown code would turn a served-shape change into a silent corpus-wide
# no-op, while refusing on a recognized separate writing is what keeps a dissent
# out of the `opinion_text` column.
_SEPARATE_WRITING: Final = ("concurrence", "dissent", "addendum", "remittitur", "rehearing")


class OpinionEnrichmentResult(BaseModel):
    """What one enrichment pass over the cert-granted slice did (or would do)."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the corpus (False = dry-run)")
    eligible: int = Field(ge=0, description="Addressable granted SCOTUS rows still lacking a body")
    considered: int = Field(ge=0, description="Eligible rows the per-run cap admitted")
    enriched: int = Field(ge=0, description="Rows an opinion body and/or citations landed on")
    no_cluster: int = Field(ge=0, description="Rows whose docket links no followable cluster")
    ambiguous_cluster: int = Field(
        default=0,
        ge=0,
        description="Rows whose docket links several clusters — refused, not guessed at",
    )
    foreign_cluster: int = Field(
        default=0,
        ge=0,
        description="Rows whose fetched cluster names a different docket (a misjoin, skipped)",
    )
    no_body: int = Field(
        ge=0,
        description="Rows whose cluster yielded no body — no followable sub-opinion, a first "
        "opinion that is a separate writing, no extracted plain text, or one past the size bound",
    )
    live_only: int = Field(
        default=0,
        ge=0,
        description="Granted rows skipped unwalked: their docket id is the live channel's "
        "reserved-range mint, which addresses nothing upstream",
    )
    requests: int = Field(ge=0, description="REST requests the pass issued (retries not counted)")
    failed: list[dict[str, str]] = Field(
        default_factory=list, description="`{case_id, reason}` for each row whose fetch raised"
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

    A link the URL parser refuses outright (an authority that fails NFKC
    normalization, a malformed IPv6 host) is the same answer as a link off the
    API — a stored payload is untrusted input, and "unparseable" must not become
    an exception the walk unwinds on.
    """
    if not isinstance(url, str):
        return None
    try:
        base = urlsplit(base_url)
        target = urlsplit(url.strip())
    except ValueError:
        return None
    # Host comparison is case-insensitive (hostnames are), everything else is
    # exact: userinfo, a port, or any other authority decoration makes the
    # netloc differ from the base's and the link is refused.
    if target.scheme != base.scheme or target.netloc.lower() != base.netloc.lower():
        return None
    prefix = base.path if base.path.endswith("/") else f"{base.path}/"
    if not target.path.startswith(prefix):
        return None
    segments = target.path[len(prefix) :].strip("/").split("/")
    if len(segments) != 2 or segments[0] != resource:
        return None
    return int(segments[1]) if _ID_RE.fullmatch(segments[1]) else None


def _resource_ids(links: Any, *, base_url: str, resource: str) -> list[int]:
    """Every followable id in a list of upstream hyperlinks, order preserved."""
    if not isinstance(links, list):
        return []
    found: list[int] = []
    for link in links:
        ident = resource_id(link, base_url=base_url, resource=resource)
        if ident is not None and ident not in found:
            found.append(ident)
    return found


def _courtlistener_docket_id(case_id: str) -> int | None:
    """The CourtListener docket id a case id names, or ``None`` if it names none.

    ``None`` covers both a malformed id and a live-first petition's
    reserved-range mint: that id is the live channel's own and addresses nothing
    upstream, so a case carrying one has no docket to fetch.
    """
    _, _, raw = case_id.partition("/")
    if not _ID_RE.fullmatch(raw):
        return None
    docket_id = int(raw)
    return None if is_live_docket_id(docket_id) else docket_id


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


def is_separate_writing(payload: Mapping[str, Any]) -> bool:
    """Whether an opinion is a separate writing rather than the case's decision.

    Keyed on upstream's own ``type`` wording (see :data:`_SEPARATE_WRITING`).
    A concurrence or dissent is a real opinion but not the one the case's
    ``opinion_text`` claims to be, and the presence bit that records the body is
    a latch — so the wrong answer here is permanent, and this is the test that
    keeps it from being reached by accident.
    """
    kind = payload.get("type")
    if not isinstance(kind, str):
        return False
    lowered = kind.lower()
    return any(word in lowered for word in _SEPARATE_WRITING)


def opinion_body(payload: Mapping[str, Any]) -> str | None:
    """The opinion's extracted body, or ``None`` when it is not one to store.

    ``plain_text`` only: upstream also carries HTML renderings, and converting
    one would put a parser of ours between the court's words and the corpus.
    Three answers collapse to ``None`` — a separate writing, an empty body, and
    a body past :data:`MAX_OPINION_CHARS` — because each is a reason to leave
    the column alone, and the cluster's citations land regardless.
    """
    if is_separate_writing(payload):
        return None
    text = payload.get("plain_text")
    if not isinstance(text, str):
        return None
    stripped = text.strip()
    if not stripped or len(stripped) > MAX_OPINION_CHARS:
        return None
    return stripped


def cluster_names_docket(cluster: Mapping[str, Any], *, base_url: str, docket_id: int) -> bool:
    """Whether a fetched cluster belongs to the docket it was reached from.

    The hyperlink guard proves a link points into the API; it proves nothing
    about *which* case the cluster describes, and a cluster written onto the
    wrong row is exactly the misjoin class the bulk-cluster scrub exists to
    undo. A cluster naming a followable docket must name this one. A cluster
    naming none is accepted: it was reached from this docket's own ``clusters``
    list either way, and refusing on an absent field would turn a served-shape
    change into a silent no-op across the whole population.
    """
    named = resource_id(cluster.get("docket"), base_url=base_url, resource="dockets")
    return named is None or named == docket_id


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
    # `bool` is an `int` subclass, so a served `true` would otherwise store 1.
    counted = isinstance(count, int) and not isinstance(count, bool)
    return corpus.CorpusRow.model_validate(
        {
            **row.model_dump(),
            "citations": citations or row.citations,
            "citation_count": count if counted else row.citation_count,
            "opinion_text": body or row.opinion_text,
        }
    )


class _Walk:
    """One pass's mutable tally, so the per-case steps read as what they decide."""

    def __init__(self, client: CourtListenerClient, conn: sqlite3.Connection) -> None:
        self.client = client
        self.conn = conn
        self.requests = 0

    def _get_docket(self, docket_id: int) -> Mapping[str, Any]:
        # Counted before the call, not after: an inspection of what a run spent
        # must include the request that failed, which is the expensive one.
        self.requests += 1
        return self.client.get_docket(docket_id)

    def cluster_ids(self, case_id: str, docket_id: int) -> list[int]:
        """The clusters a case's docket links, snapshot first, docket second.

        A stored **REST-shaped** snapshot already carries the ``clusters`` list,
        so a case that has one costs nothing to resolve. A granted SCOTUS row's
        newest snapshot is normally the live channel's supremecourt.gov payload
        instead, which has no such list, so the docket fetch is the usual path
        here — which is why the budget arithmetic is quoted at three requests.
        """
        snapshot = corpus.latest_snapshot(self.conn, case_id)
        if snapshot is not None:
            stored = _resource_ids(
                snapshot[1].get("clusters"), base_url=self.client.base_url, resource="clusters"
            )
            if stored:
                return stored
        docket = self._get_docket(docket_id)
        return _resource_ids(
            docket.get("clusters"), base_url=self.client.base_url, resource="clusters"
        )

    def cluster(self, cluster_id: int) -> Mapping[str, Any]:
        self.requests += 1
        return self.client.get_cluster(cluster_id)

    def body(self, cluster: Mapping[str, Any]) -> str | None:
        """The case's opinion body from its cluster, or ``None``.

        The first followable sub-opinion is fetched and then *tested*: upstream
        orders the list but does not promise the lead opinion leads it, so a
        first entry that turns out to be a separate writing yields no body
        rather than the wrong one.
        """
        sub_opinions = _resource_ids(
            cluster.get("sub_opinions"), base_url=self.client.base_url, resource="opinions"
        )
        if not sub_opinions:
            return None
        self.requests += 1
        return opinion_body(self.client.get_opinion(sub_opinions[0]))


def _stop_reason(exc: Exception) -> str | None:
    """Why an exception ends the whole walk, or ``None`` for a one-case failure.

    Two faults are the batch's, not a case's: the client's own request budget
    (:class:`RateBudgetExceeded`) and a 429 its retry cycle could not clear —
    the shared daily quota spent. Every later case would hit the same wall, so
    both stop the walk; anything else costs its case and nothing more.
    """
    if isinstance(exc, RateBudgetExceeded):
        return f"API budget exhausted ({exc})"
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
        return f"CourtListener throttling persisted ({exc})"
    return None


def enrich_opinions(
    conn: sqlite3.Connection,
    client: CourtListenerClient,
    *,
    apply: bool,
    max_cases: int = DEFAULT_MAX_CASES,
) -> OpinionEnrichmentResult:
    """Walk the cert-granted rows that carry no opinion to their clusters and bodies.

    Eligibility is the grant with the presence bit as the idempotency key: a
    SCOTUS row with ``date_cert_granted`` set and ``has_opinion`` clear, whose
    docket id is a CourtListener one. Candidates are taken in ``case_id`` order
    and capped at ``max_cases``; the rest are left for the next run, which
    re-derives the same predicate.

    Every way a case can fail to yield a document is counted and left alone —
    no cluster, several clusters, a cluster naming another docket, an opinion
    that is a separate writing or carries no text — because a coverage gap is
    a report, not an error, and because ``has_opinion`` latches so a guess is
    permanent. A per-case REST or parse failure is recorded and the walk
    continues; :class:`RateBudgetExceeded` stops it outright, since every later
    case would hit the same wall — and a **429 that survived the client's own
    retries** stops it the same way, because persistent throttling means the
    shared daily quota is spent, so the unfinished remainder defers for a
    re-run in a genuine dead zone instead of burning the batch into the wall.
    ``max_cases`` is the walk's only other bound,
    and it is a hard one — the rotation's wall-clock deadline and transient
    breaker have no counterpart here because the 50-case default cap bounds
    the damage a degraded upstream can do without them (150 requests, half
    the held tier's hourly ceiling, even if every one stalls to a retry).

    Dry-run by default: ``apply`` gates only the writes, so the request spend
    and the coverage report are identical either way — the dry run is what the
    spend is inspected from.
    """
    candidates: list[tuple[corpus.CorpusRow, int]] = []
    live_only = 0
    for row in corpus.iter_rows(conn, court="scotus"):
        if row.date_cert_granted is None or row.has_opinion:
            continue
        docket_id = _courtlistener_docket_id(row.case_id)
        if docket_id is None:
            live_only += 1
            continue
        candidates.append((row, docket_id))
    admitted = candidates[: max(max_cases, 0)]
    walk = _Walk(client, conn)
    result = OpinionEnrichmentResult(
        applied=apply,
        eligible=len(candidates),
        considered=len(admitted),
        enriched=0,
        no_cluster=0,
        no_body=0,
        live_only=live_only,
        requests=0,
    )
    for index, (row, docket_id) in enumerate(admitted):
        try:
            cluster_ids = walk.cluster_ids(row.case_id, docket_id)
            if not cluster_ids:
                result.no_cluster += 1
                continue
            if len(cluster_ids) > 1:
                # Several published clusters can hang off one docket (a
                # statement respecting denial, a per curiam, the merits
                # opinion). Nothing in the list says which is the case's
                # decision, and the presence bit latches, so the pass reports
                # the ambiguity instead of resolving it by position.
                result.ambiguous_cluster += 1
                continue
            cluster = walk.cluster(cluster_ids[0])
            if not cluster_names_docket(cluster, base_url=client.base_url, docket_id=docket_id):
                result.foreign_cluster += 1
                continue
            body = walk.body(cluster)
            if body is None:
                result.no_body += 1
            # A cluster that adds nothing the row already carries is converged,
            # not enriched: writing it back would report coverage the pass did
            # not produce.
            enriched = _enriched_row(row, cluster, body)
            if enriched == row:
                continue
            result.enriched += 1
            if apply:
                corpus.upsert_rows(conn, [enriched])
        except (RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
            reason = _stop_reason(exc)
            if reason is not None:
                # A batch-level wall: the walk stops and the remainder — the
                # case that hit it included — defers rather than fails.
                # Nothing latches, so the deferral costs only time.
                result.stopped = reason
                result.deferred = [pending.case_id for pending, _ in admitted[index:]]
                break
            # ValueError covers what an untrusted response body can raise on the
            # way in — a 200 that is not JSON, most of all. Both are one case's
            # problem, so both cost that case and nothing else.
            result.failed.append({"case_id": row.case_id, "reason": f"{type(exc).__name__}: {exc}"})
            continue
    result.requests = walk.requests
    return result
