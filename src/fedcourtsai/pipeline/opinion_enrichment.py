"""Opinion-cluster enrichment: reporter cites and opinion bodies for granted cases.

The corpus records what a docket *did* — the cert disposition, the merits
judgment — but not what the Court *wrote*. This pass fills that in for the
cert-granted SCOTUS slice: each row carrying ``date_cert_granted`` is walked to
its published opinion cluster, and the cluster's reporter ``citations`` /
``citation_count`` and the lead opinion's body land on the row. Those are the
fields the retrieval surface's prior ranking keys on, and the opinion body is
the input a semantic claim family needs — so coverage here is the precondition
for both, not an end in itself.

**Two routes reach a case's cluster.** The docket id a granted row carries is
the case's *cert-stage* docket, and upstream keeps more than one docket row per
number: the published merits cluster hangs on whichever row holds it, commonly
a sibling row the corpus does not track. So the walk asks twice. First the
docket's own ``clusters`` links — a stored REST-shaped snapshot's where it has
one, else the docket fetch's — with a single link followed to the cluster.
Where that list comes back empty, the second route asks the relation from the
other side: the clusters upstream joins to this court and this docket number,
whichever of its docket rows they sit on. A list result is a full cluster
serialization, so the second route reads its cluster without following a link
to it. A row carrying no docket number has nothing to ask the second route
with, and stops at the first.

**Scope is the budget argument.** Four REST requests bound a case that reaches
its opinion by the number route — the docket, the cluster list, the docket the
found cluster names, and the lead opinion — and three bound one that reaches it
by the docket route (docket, cluster, opinion), dropping to two where a stored
REST-shaped snapshot already links the cluster. That last is rare on this
population: a granted SCOTUS docket is the set the live channel re-polls, so
its newest snapshot is normally a supremecourt.gov payload, which carries no
``clusters`` list. A case neither route resolves stops at two, or at one where
there was no number to ask with; a refusal on the docket's own links stops
earlier still, at one or at none. The cert-granted slice is ≈1,250 rows all-time
(grants and GVRs together) and ≈120 to 130 a Term, so ≈5,000 requests bounds a
sweep of the standing backlog in which every case reaches its opinion and ≈520
a Term bounds a Term's new grants — days of the allowance the pull windows
leave, not a budget event. ``max_cases`` bounds any one run on top of
the client's own governor, and either wall — the client's request budget
(:class:`RateBudgetExceeded`) or a 429 its retries could not clear — stops the
walk cleanly with the unfinished cases reported as deferred. Corpus-wide opinion coverage
is a different problem with a different answer: the replication channel
(``docs/data-sources.md``), not more REST.

**Grant-scoped, and idempotent on the presence bit.** A row already carrying
``has_opinion`` is skipped, so a converged corpus spends nothing. The scope is
the cert grant rather than ``corpus.opens_merits_proceeding`` because the
question here is "did this case produce a published opinion", which a summary
reversal can answer yes to; the cost is that the slice also admits the grants
that never produce one. An undecided grant has no cluster to link yet and
reports as such, converging on the run after its opinion publishes: a converged
case drops out of the next run's predicate, and one that found no cluster is
retried, which is what lets a grant pick up its opinion once published.

**A last-attempted cursor orders the walk.** Two populations never converge —
a grant that publishes no opinion at all (a GVR, a DIG), and a decided grant
neither route resolves, whether because the row carries no docket number to ask
with or because upstream joins several clusters to the one it carries — so
under a plain ``case_id`` order that residue
would head every run and, once it exceeded ``max_cases``, the cap could never
reach past it. The cursor is what unsticks it: each candidate the walk
*classifies* — a landed body, no cluster, a refusal, a 4xx on one of its
records — is
stamped with the run's date in
``corpus.CorpusRow.opinion_enrich_attempted_at``, through the same upsert the
enrichment itself writes through, and candidates are taken never-attempted
first, then stalest stamp first, ``case_id`` breaking ties. What may stamp is
what upstream *answered about the case*: a 5xx, a transport failure, an
unparseable body, or a 4xx on a collection query — upstream refusing the
question rather than the case — says nothing about this docket, so such a case
keeps its place rather than rotating to the back of a queue a degraded upstream
never really walked it in (:func:`_answers_about_the_case`). The residue
therefore rotates to the back of the queue for as long as anything else is
owed a turn, and successive runs advance through the slice instead of
re-spending on one head. A candidate the walk did **not** reach — deferred
behind a wall, or left outside the cap — is never stamped, so it keeps its
place at the front. A dry run classifies without stamping: it writes nothing at
all, so it reports what the *next* applied run would walk. The stamp is a date,
like every other rotation key in the corpus (``last_pulled``,
``last_live_polled``), so runs inside one day tie once the queue is exhausted —
which is the point at which every eligible row has already been walked that
day, and the ordering has nothing left to buy.

**The pass refuses to guess which document is the case's.** ``has_opinion``
max-latches, so a wrong body is not self-healing: the row stops matching this
pass's own predicate and no later run revisits it. So more than one candidate
cluster — several links on the docket, or several results for the number — is
refused rather than resolved by taking the first; a resolved cluster must name
a docket the route it came by can vouch for, which is the docket it was reached
from on the docket route and, on the number route, a fetched row in this court
carrying this docket number; and an opinion whose upstream
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
short keeps the coverage it already paid for. The cursor stamp rides that same
write — one upsert per classified case, carrying the enrichment where there was
one — so the record of what was attempted cannot drift from the record of what
landed. The cost is that a refusal now writes a row (and re-mirrors its
``case.json``) where it wrote nothing before, bounded by ``max_cases`` and
paid in small local writes rather than REST: the alternative, a direct
``UPDATE`` of the cursor alone, is the one thing this seam exists to refuse.

**A stored hyperlink is a claim, not a target.** Snapshot payloads carry
upstream URLs, and none of them is ever fetched as given: :func:`resource_id`
requires a link to resolve under the client's own REST base and to name
``<resource>/<numeric id>/``, and only that id reaches the client, which builds
its request path itself. A payload therefore cannot steer a request off the
CourtListener API however it was written. The number route addresses nothing at
all: the stored docket number travels as a query *parameter* the transport
url-encodes, so the path it is filtered on is still the client's own.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any, Final
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled
from ..supremecourt import is_live_docket_id

# A modest default: the pass is a standing maintenance step, not a bulk load,
# and the cap keeps one run's spend legible beside the pull windows that share
# the same daily budget — about two-thirds of the held tier's hourly ceiling at
# the four requests a case resolved by docket number costs (see docs/budget.md
# for the tier).
DEFAULT_MAX_CASES: Final = 50

# Upstream ids are integers; a link whose id segment is anything else is not a
# link this client can follow. Deliberately not `str.isdigit`, which accepts
# non-ASCII digit forms `int()` would then happily parse.
_ID_RE: Final = re.compile(r"[0-9]+")

# A court's id is a slug, not a number ("scotus", "ca9", "nysd"). The pattern
# is what keeps a served value — or a still-percent-encoded path segment — from
# leaving the hyperlink guard as free-form text: the answer is only ever
# compared, never fetched, and this is what makes that structural.
_COURT_RE: Final = re.compile(r"[a-z0-9_-]{1,32}")

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
    no_cluster: int = Field(
        ge=0, description="Rows neither the docket route nor the docket number reached a cluster on"
    )
    ambiguous_cluster: int = Field(
        default=0,
        ge=0,
        description="Rows whose docket links, or whose docket number matches, several "
        "clusters — refused, not guessed at",
    )
    foreign_cluster: int = Field(
        default=0,
        ge=0,
        description="Rows whose resolved cluster names a docket that is not the case's "
        "(a misjoin, skipped)",
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
        default_factory=list,
        description="Admitted case ids the walk did not complete — left for the "
        "next run, which re-derives the same predicate",
    )


def _resource_segments(url: object, *, base_url: str, resource: str) -> str | None:
    """The id segment a link names beneath ``<base_url>/<resource>/``, or ``None``.

    The shared half of the hyperlink guard: a link passes only if it resolves
    under ``base_url`` — same scheme, same host, same API path prefix — and
    names ``<resource>/<id>/`` beneath it; anything else (another host, another
    API version, a relative path, a nested route, a non-string) yields ``None``.
    What counts as an id is the caller's question, because upstream spells a
    court's id as a slug and everything else's as an integer.

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
    return segments[1] or None


def resource_id(url: object, *, base_url: str, resource: str) -> int | None:
    """The integer id a CourtListener REST hyperlink names, or ``None``.

    The guard between a stored payload and an outbound request: the link must
    pass :func:`_resource_segments` and name a *numeric* id, or the answer is
    ``None``. The caller keeps the id and discards the link, so the request path
    is always the client's own construction rather than text a payload supplied.
    """
    segment = _resource_segments(url, base_url=base_url, resource=resource)
    if segment is None:
        return None
    return int(segment) if _ID_RE.fullmatch(segment) else None


def docket_court(docket: Mapping[str, Any], *, base_url: str) -> str | None:
    """The court id a fetched docket belongs to, or ``None`` if it names none.

    Upstream serves the court either as a ``court_id`` slug or as a ``court``
    hyperlink (``.../courts/scotus/``) whose last segment is that slug, so both
    spellings are read. The hyperlink is held to the same guard as any other —
    it must resolve under the client's own REST base — because an unguarded
    reading would let a payload's link decide that a foreign court's docket is
    this one's, and the segment must then *look* like a court id
    (:data:`_COURT_RE`): the guard hands back a raw path segment, still
    percent-encoded as served, and only a well-formed slug leaves this function.
    Nothing interpolates the answer into a request path — it is compared, never
    fetched — and the slug test is what keeps that true by construction rather
    than by every caller's care.
    """
    raw = docket.get("court_id")
    if isinstance(raw, str) and _COURT_RE.fullmatch(raw.strip()):
        return raw.strip()
    segment = _resource_segments(docket.get("court"), base_url=base_url, resource="courts")
    return segment if segment is not None and _COURT_RE.fullmatch(segment) else None


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


def cluster_docket_id(cluster: Mapping[str, Any], *, base_url: str) -> int | None:
    """The docket a cluster names, whichever way upstream spells the relation.

    Upstream serves the relation as a ``docket`` hyperlink, and both of the
    id-shaped spellings alongside it (a bare ``docket`` integer, a ``docket_id``)
    are read too, because a serializer that carries one rather than the other
    must not read as "this cluster belongs to no docket" — on the number route
    that answer is a refusal, so a shape change there would silently zero the
    route instead of failing visibly. A hyperlink passes the same guard as any
    other stored link; an integer names no host and so needs none.
    """
    named = resource_id(cluster.get("docket"), base_url=base_url, resource="dockets")
    if named is not None:
        return named
    for key in ("docket", "docket_id"):
        value = cluster.get(key)
        # `bool` is an `int` subclass, and a negative id addresses nothing.
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
    return None


def cluster_names_docket(cluster: Mapping[str, Any], *, base_url: str, docket_id: int) -> bool:
    """Whether a fetched cluster belongs to the docket it was reached from.

    The hyperlink guard proves a link points into the API; it proves nothing
    about *which* case the cluster describes, and a cluster written onto the
    wrong row is exactly the misjoin class the bulk-cluster scrub exists to
    undo. A cluster naming a followable docket must name this one. A cluster
    naming none is accepted: it was reached from this docket's own ``clusters``
    list either way, and refusing on an absent field would turn a served-shape
    change into a silent no-op across the whole population.

    The guard for the docket route only. A cluster reached by docket *number*
    is expected to name another row, so what it must satisfy there is
    :func:`docket_names_case` on the row it does name.
    """
    named = cluster_docket_id(cluster, base_url=base_url)
    return named is None or named == docket_id


def docket_names_case(
    docket: Mapping[str, Any], *, base_url: str, court: str, docket_number: str
) -> bool:
    """Whether a fetched docket is another of upstream's rows for this case.

    The docket-number route's half of the misjoin guard. Upstream keeps more
    than one docket row per case — a cert-stage row and a merits row for the
    same number — and the published cluster hangs on whichever of them carries
    it, so "names the docket it was reached from" cannot be the test there.
    What is the test is the case's own identity: the row the cluster names must
    be in this court and carry this docket number, compared on
    :func:`fedcourtsai.corpus.normalize_docket_number` so two spellings of one
    number match and a consolidated string matches nothing.

    Checked here rather than taken from the list filter that found the cluster,
    because that filter's matching is upstream's to define and ``has_opinion``
    latches: a number the filter folded more loosely than this comparison would
    write another case's body onto the row permanently. An absent court or
    number is a refusal, not a pass — on this route the fetched docket is the
    only evidence of identity there is.
    """
    wanted = corpus.normalize_docket_number(docket_number)
    if wanted is None or docket_court(docket, base_url=base_url) != court:
        return False
    served = docket.get("docket_number")
    return isinstance(served, str) and corpus.normalize_docket_number(served) == wanted


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


def _walk_order(candidate: tuple[corpus.CorpusRow, int]) -> tuple[bool, date, str]:
    """The walk's rotation key: never-attempted first, then the stalest stamp.

    ``case_id`` breaks ties, so the order is deterministic given the stamps —
    and a run that stamps everything it classified leaves the next run a
    different head, which is how the permanent residue stops holding the front
    of the queue (see the module docstring).
    """
    row = candidate[0]
    attempted = row.opinion_enrich_attempted_at
    # `date.min` never reaches a comparison against a real stamp: the first key
    # element already separates the never-attempted from the attempted.
    return (attempted is not None, attempted or date.min, row.case_id)


@dataclass(frozen=True)
class _Resolution:
    """A case's published cluster, or why the walk has none to write.

    ``cluster`` is set only when exactly one candidate was found, so the two
    refusals are legible without it: ``ambiguous`` says several came back and
    the pass declined to pick, and neither set says nothing did.
    ``by_docket_number`` records which route answered, because the two are
    checked for misjoin differently.
    """

    cluster: Mapping[str, Any] | None = None
    ambiguous: bool = False
    by_docket_number: bool = False


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

    def clusters(self, row: corpus.CorpusRow, docket_id: int) -> _Resolution:
        """A case's published cluster, by the docket route or the number route.

        **The docket's own links first.** A stored **REST-shaped** snapshot
        already carries the ``clusters`` list, so a case that has one costs
        nothing to resolve; a granted SCOTUS row's newest snapshot is normally
        the live channel's supremecourt.gov payload instead, which has no such
        list, so the docket fetch is the usual first request. Several links is
        an ambiguity refused here rather than resolved by position, and the
        cluster fetch that a single link earns is the second request.

        **Then the docket number.** The id a granted row carries is its
        cert-stage docket, and upstream hangs the merits cluster on whichever of
        its rows for that number holds it — commonly a sibling row the corpus
        does not track — so a docket linking nothing is the start of the second
        route, not the end of the walk: the clusters upstream joins to this
        court and number. Each result is a full cluster serialization, so this
        route resolves in one request where following a link would take two.
        A row carrying no docket number has nothing to ask with and stops at the
        first route.
        """
        ids = self._docket_cluster_ids(row.case_id, docket_id)
        if len(ids) > 1:
            return _Resolution(ambiguous=True)
        if ids:
            return _Resolution(cluster=self.cluster(ids[0]))
        # The filter carries the docket's own spelling with the Court's
        # ``*** CAPITAL CASE ***`` marking removed: that marking is a flag on
        # the case rather than part of its number, and upstream knows the
        # number without it — the same strip every other channel applies before
        # addressing upstream by a stored number.
        number = corpus.strip_docket_annotation(row.docket_number)
        if not number:
            return _Resolution()
        return self._clusters_by_docket_number(row.court, number)

    def _docket_cluster_ids(self, case_id: str, docket_id: int) -> list[int]:
        """The clusters a case's own docket links, snapshot first, docket second."""
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

    def _clusters_by_docket_number(self, court: str, docket_number: str) -> _Resolution:
        """The clusters upstream joins to this court and docket number.

        The ambiguity refusal is the same one the docket route makes, read off
        the list instead of a link list: more than one result — or a page that
        says more exist, by a further page or by a served ``count`` — means
        upstream holds several clusters for this number and nothing here says
        which is the case's decision. It doubles as the guard against a filter
        upstream ignored rather than applied, since an unfiltered page comes
        back full.
        """
        self.requests += 1
        page = self.client.list_clusters_by_docket_number(court=court, docket_number=docket_number)
        results = page.get("results")
        if not isinstance(results, list) or not results:
            return _Resolution()
        count = page.get("count")
        # `bool` is an `int` subclass, so a served `true` would otherwise count.
        counted = count if isinstance(count, int) and not isinstance(count, bool) else 0
        if len(results) > 1 or page.get("next") or counted > 1:
            return _Resolution(ambiguous=True)
        found = results[0]
        if not isinstance(found, Mapping):
            return _Resolution()
        return _Resolution(cluster=found, by_docket_number=True)

    def names_the_case(
        self, found: _Resolution, cluster: Mapping[str, Any], row: corpus.CorpusRow, docket_id: int
    ) -> bool:
        """Whether a resolved cluster is this case's, by its route's own test.

        On the docket route the cluster must name the docket it was reached from
        (:func:`cluster_names_docket`). On the number route it is *expected* to
        name another row, so the test moves to that row: the docket it names
        must be one this client can name (:func:`cluster_docket_id`) — the only
        identity evidence this route has, so an unnamed docket is a refusal here
        rather than the fail-open the docket
        route can afford — and, unless it is the case's own docket, it is
        fetched and held to :func:`docket_names_case`. That fetch is the third
        request on this route, and it is what keeps the join the pass's own
        check rather than a filter's promise.
        """
        base_url = self.client.base_url
        if not found.by_docket_number:
            return cluster_names_docket(cluster, base_url=base_url, docket_id=docket_id)
        named = cluster_docket_id(cluster, base_url=base_url)
        if named is None:
            return False
        if named == docket_id:
            # The case's own docket, whose court and number the row already is.
            return True
        return docket_names_case(
            self._get_docket(named),
            base_url=base_url,
            court=row.court,
            docket_number=row.docket_number,
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
    a quota wall, whichever window imposed it. Every later case would hit the
    same wall, so both stop the walk; anything else costs its case and nothing
    more. (A persistent 5xx is deliberately not a wall here: ``max_cases``
    bounds what a degraded upstream can burn, per the module docstring.)
    """
    if isinstance(exc, RateBudgetExceeded):
        return f"API budget exhausted ({exc})"
    if is_throttled(exc):
        return f"CourtListener throttling persisted ({exc})"
    return None


def _addresses_a_collection(request: httpx.Request) -> bool:
    """Whether a request asked a collection a question rather than read a record.

    Read off the path: a record's path ends in its numeric id, a collection's
    in the resource name. The distinction is what separates a refusal *about
    the case* from a refusal *about the query*.
    """
    segments = [segment for segment in request.url.path.split("/") if segment]
    return bool(segments) and not _ID_RE.fullmatch(segments[-1])


def _answers_about_the_case(exc: Exception) -> bool:
    """Whether a per-case fault is upstream's answer *about this case*.

    The cursor records a verdict the walk reached about a case, so what may
    stamp it is what upstream said about the case: a 4xx on one of its
    records — the resource is not there, or is not one this client may have —
    is as much an answer as an empty ``clusters`` list, and a case that 404s
    every run must not re-take the head of the queue. A 5xx, a transport
    failure, or a body that would not parse is a fact about the network or the
    moment instead, so the case keeps its place and is retried at the front
    rather than rotated to the back of a queue it was never really walked in.
    (A 429 never reaches here — it is a batch wall, see :func:`_stop_reason`.)

    A 4xx on a **collection** query is the third kind: upstream refused the
    question, not the case. A rejected cluster filter would otherwise stamp
    every admitted row in turn and rotate the whole slice on a fault that
    recurs identically next run — so such a case keeps its place too, and the
    refusal stays visible in ``failed`` where a re-run cannot hide it.
    """
    if not isinstance(exc, httpx.HTTPStatusError) or not 400 <= exc.response.status_code < 500:
        return False
    return not _addresses_a_collection(exc.request)


def _candidates(conn: sqlite3.Connection) -> tuple[list[tuple[corpus.CorpusRow, int]], int]:
    """The walk's queue, stalest-first, and the count of unaddressable grants.

    Eligibility is the grant with the presence bit as the idempotency key: a
    SCOTUS row carrying ``date_cert_granted`` and not ``has_opinion``, whose
    case id names a CourtListener docket. A granted row whose id is the live
    channel's reserved-range mint addresses nothing upstream, so it is counted
    (``live_only``) rather than queued. The queue is ordered by
    :func:`_walk_order`, whose key carries ``case_id`` as its own last element —
    so the order holds whatever order ``iter_rows`` yielded in.
    """
    queue: list[tuple[corpus.CorpusRow, int]] = []
    live_only = 0
    for row in corpus.iter_rows(conn, court="scotus"):
        if row.date_cert_granted is None or row.has_opinion:
            continue
        docket_id = _courtlistener_docket_id(row.case_id)
        if docket_id is None:
            live_only += 1
            continue
        queue.append((row, docket_id))
    queue.sort(key=_walk_order)
    return queue, live_only


def enrich_opinions(
    conn: sqlite3.Connection,
    client: CourtListenerClient,
    *,
    apply: bool,
    max_cases: int = DEFAULT_MAX_CASES,
    today: date | None = None,
) -> OpinionEnrichmentResult:
    """Walk the cert-granted rows that carry no opinion to their clusters and bodies.

    Eligibility is the grant with the presence bit as the idempotency key: a
    SCOTUS row with ``date_cert_granted`` set and ``has_opinion`` clear, whose
    docket id is a CourtListener one. Candidates are taken stalest-first on the
    ``opinion_enrich_attempted_at`` cursor — never-attempted rows in ``case_id``
    order, then the attempted ones oldest stamp first — and capped at
    ``max_cases``; the rest are left for the next run, which re-derives the same
    predicate against the stamps this one wrote. Every candidate the walk
    classifies is stamped with ``today`` (the current date unless a caller pins
    one) in the same upsert that carries its enrichment; a candidate the walk
    never reached, or whose fault said nothing about its docket, is left
    unstamped and keeps its place at the front.

    A case's cluster is resolved by the docket's own links and then, where
    those are empty, by the clusters upstream joins to the case's court and
    docket number — the route that reaches a merits cluster hanging on a
    sibling docket row (see the module docstring).

    Every way a case can fail to yield a document is counted and left alone —
    no cluster on either route, several clusters, a cluster naming a docket
    that is not the case's, an opinion
    that is a separate writing or carries no text — because a coverage gap is
    a report, not an error, and because ``has_opinion`` latches so a guess is
    permanent. A per-case REST or parse failure is recorded and the walk
    continues; :class:`RateBudgetExceeded` stops it outright, since every later
    case would hit the same wall — and a **429 that survived the client's own
    retries** stops it the same way, because a throttle the retry cycle could
    not clear is a quota wall (whichever window it is), so the unfinished
    remainder defers for a re-run in a genuine dead zone instead of burning
    the batch into the wall. ``max_cases`` is the walk's only other bound,
    and it is a hard one — the rotation's wall-clock deadline and transient
    breaker have no counterpart here because the 50-case default cap bounds
    the damage a degraded upstream can do without them (200 requests,
    two-thirds of the held tier's hourly ceiling, even if every one stalls to
    a retry).

    Dry-run by default: ``apply`` gates only the writes — the cursor stamp
    included, so a dry run reports what an applied run would walk without
    moving the queue — and the request spend and the coverage report are
    identical either way, which is what the dry run is inspected for.
    """
    candidates, live_only = _candidates(conn)
    admitted = candidates[: max(max_cases, 0)]
    stamp = today or date.today()
    walk = _Walk(client, conn)

    def record(attempted: corpus.CorpusRow) -> None:
        """Write one classified case: its enrichment (if any) and the cursor.

        The stamp goes on every case the walk reached a verdict about, so a
        refusal advances the rotation exactly as a landed body does — that is
        the whole point of the cursor. ``apply`` gates it with the enrichment,
        because a dry run writes nothing.
        """
        if apply:
            corpus.upsert_rows(
                conn, [attempted.model_copy(update={"opinion_enrich_attempted_at": stamp})]
            )

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
            found = walk.clusters(row, docket_id)
            cluster = found.cluster
            if cluster is None:
                # Several published clusters can answer for one case (a
                # statement respecting denial, a per curiam, the merits
                # opinion). Nothing about them says which is the case's
                # decision, and the presence bit latches, so the pass reports
                # the ambiguity instead of resolving it by position.
                if found.ambiguous:
                    result.ambiguous_cluster += 1
                else:
                    result.no_cluster += 1
                record(row)
                continue
            if not walk.names_the_case(found, cluster, row, docket_id):
                result.foreign_cluster += 1
                record(row)
                continue
            body = walk.body(cluster)
            if body is None:
                result.no_body += 1
            # A cluster that adds nothing the row already carries is converged,
            # not enriched: writing it back would report coverage the pass did
            # not produce. The cursor still moves — the case was walked.
            enriched = _enriched_row(row, cluster, body)
            if enriched == row:
                record(row)
                continue
            result.enriched += 1
            record(enriched)
        except (RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
            reason = _stop_reason(exc)
            if reason is not None:
                # A batch-level wall: the walk stops and the remainder — the
                # case that hit it included — defers rather than fails.
                # Nothing latches, so the deferral costs only time.
                result.stopped = reason
                result.deferred = [pending.case_id for pending, _ in admitted[index:]]
                break
            # A non-batch fault: a non-429 REST failure, or the ValueError an
            # untrusted response body can raise on the way in (a 200 that is
            # not JSON, most of all). Either is one case's problem, so it
            # costs that case and nothing else.
            result.failed.append({"case_id": row.case_id, "reason": f"{type(exc).__name__}: {exc}"})
            if _answers_about_the_case(exc):
                record(row)
            continue
    result.requests = walk.requests
    return result
