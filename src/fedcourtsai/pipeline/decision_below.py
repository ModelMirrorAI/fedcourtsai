"""The decision below: locating a SCOTUS petition's lower-court ruling on CourtListener.

A cert petition names the judgment it asks the Court to review, and the
supremecourt.gov docket JSON carries the facts that identify it: the lower
court's name (``LowerCourt``), its case number or numbers
(``LowerCourtCaseNumbers``), the judgment date (``LowerCourtDecision``) and,
where one was denied, the date rehearing was denied
(``LowerCourtRehearingDenied``). This module joins those facts to
CourtListener and reports what it finds there — the lower court's docket row,
the opinion cluster dated on the judgment date, whether that opinion carries a
downloadable file or extracted text, the panel, and, where upstream holds the
docket's entries (RECAP), whether a petition for rehearing en banc was filed,
how it was disposed of, and whether a dissent from the disposition was noted.

**A measurement, not a store.** Nothing here writes the corpus, the content
store or the ledger, and nothing reaches a cell: the ``decision-below`` command
prints one :class:`DecisionBelowMatch` per case so a maintainer can measure the
match rate before any of it is stored. No request buys anything: the client
reads CourtListener's REST API only, and RECAP Fetch is never called.

**Federal courts of appeals only.** The lower-court name maps to a
CourtListener court id through the same table the live channel uses
(:func:`fedcourtsai.pipeline.ingest.live_lower_court_id`). A state court, a
district court or any other tribunal is reported ``unmapped_court`` with the
class of court the name reads as: CourtListener's state-court docket numbers
follow each state's own grammar, and a district court is rarely the court a
petition seeks review of, so neither is joined here.

**The join is checked, not trusted.** Each docket number is asked twice at
most — the exact string first, then upstream's ``docket_number_core`` (the
year and serial digits, computed here the way upstream computes it for an
appellate number) — and every row a filter returns must carry this court and
this number, by either spelling, or it is dropped. A cluster counts as the
decision below only when its ``date_filed`` is the judgment date and it hangs
on a checked row; a cluster dated after the SCOTUS docketing is never a
candidate. Several clusters on the judgment date are all reported, since a
court can issue an opinion and an amended one the same day.

**The rehearing reading is text, and says so.** CourtListener serves docket
entries as filed text with no structured rehearing field, so the en banc
reading is a pattern match over the ``description`` of each entry filed on or
after the judgment date, with every entry that drove it cited by number and
date. The SCOTUS docket's own ``LowerCourtRehearingDenied`` date is reported
beside it unchanged; it does not say whether the denial was of panel or en
banc rehearing.

**Bounded spend.** Every request goes through the shared client and its rate
governor. A case costs at most two requests per lower-court number (up to
:data:`MAX_LOWER_NUMBERS` numbers), one per cluster followed (up to
:data:`MAX_CLUSTERS`), one per opinion read (up to :data:`MAX_OPINIONS`) and
up to :data:`MAX_ENTRY_PAGES` pages of entries for each of up to
:data:`MAX_ENTRY_DOCKETS` rows; a typical circuit case costs four or five. The
client's request budget (:class:`RateBudgetExceeded`) or a 429 its retries
could not clear stops the walk with the rest reported deferred, as the
opinion enrichment does.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Final, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled
from ..supremecourt import parse_scotus_docket_number
from .ingest import live_lower_court_id
from .opinion_enrichment import docket_court, resource_id

#: Lower-court numbers asked per case. A consolidated petition can list many;
#: the first few carry the decision, and the cap bounds what one case spends.
MAX_LOWER_NUMBERS: Final = 3

#: Opinion clusters followed per case, across every checked docket row.
MAX_CLUSTERS: Final = 4

#: Sub-opinions read per matched cluster, for the availability report.
MAX_OPINIONS: Final = 3

#: Docket rows whose entries are read per case, and pages read per row.
MAX_ENTRY_DOCKETS: Final = 2
MAX_ENTRY_PAGES: Final = 2

#: The default sample size of the ``decision-below`` command.
DEFAULT_SAMPLE: Final = 20

MatchStatus = Literal[
    "matched",
    "no_cluster_on_date",
    "no_cluster",
    "no_docket",
    "unmapped_court",
    "no_lower_court",
    "failed",
]

# Upstream's appellate core: the first `YY-N…` in the number, its serial padded
# to six digits (cl.lib.model_helpers.make_appellate_bankr_number_core). It is
# a search, not an anchored match, which is what folds a four-digit year
# ("2025-1812") to the same core as its two-digit spelling ("25-1812").
_APPELLATE_CORE_RE: Final = re.compile(r"(\d\d)-(\d+)")

# Names the docket JSON uses for courts this slice does not join, read in this
# order: the first that matches names the class reported.
_UNMAPPED_CLASSES: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("federal district court", re.compile(r"\bunited states district court\b", re.I)),
    ("federal bankruptcy court", re.compile(r"\bbankruptcy\b", re.I)),
    (
        "military or specialized federal court",
        re.compile(r"\barmed forces\b|\bveterans\b|\bmilitary\b|\bclaims\b|\btax court\b", re.I),
    ),
    (
        "state court",
        re.compile(
            r"\bsupreme court of\b|\bcourt of appeals? of\b|\bcourt of criminal appeals\b"
            + r"|\bdistrict court of appeal\b|\bsuperior court\b|\bappellate (?:court|division)\b"
            + r"|\bcommonwealth\b|\bstate of\b|\bcircuit court\b",
            re.I,
        ),
    ),
)

# The rehearing patterns, over a docket entry's filed text. "Rehearing en banc"
# is upstream's own phrase in every circuit's entries, and the order words are
# the ones a clerk dockets a disposition with.
_EN_BANC_RE: Final = re.compile(r"\brehearing\s+en\s+banc\b|\ben\s+banc\s+rehearing\b", re.I)
_PETITION_RE: Final = re.compile(r"\bpetition\b|\bmotion\b", re.I)
_ORDER_RE: Final = re.compile(r"\border\b", re.I)
_DENIED_RE: Final = re.compile(r"\bden(?:y|ied|ies|ying)\b", re.I)
_GRANTED_RE: Final = re.compile(r"\bgrant(?:ed|s|ing)?\b", re.I)
_DISSENT_RE: Final = re.compile(r"\bdissent(?:s|ed|ing)?\b", re.I)


class LowerCourtFacts(BaseModel):
    """What a SCOTUS docket says about the decision it asks the Court to review."""

    model_config = ConfigDict(extra="forbid")

    scotus_docket_number: str | None = Field(
        default=None, description="The SCOTUS docket number (`CaseNumber`), trimmed"
    )
    scotus_docketed: date | None = Field(
        default=None, description="When the Court docketed the petition (`DocketedDate`)"
    )
    court_name: str | None = Field(
        default=None, description="The lower court as the docket names it (`LowerCourt`)"
    )
    court_id: str | None = Field(
        default=None,
        description="The CourtListener court id the name maps to; None when unmapped",
    )
    docket_numbers: list[str] = Field(
        default_factory=list,
        description="The lower-court numbers (`LowerCourtCaseNumbers`), split on commas",
    )
    judgment_date: date | None = Field(
        default=None, description="The date of the judgment below (`LowerCourtDecision`)"
    )
    rehearing_denied: date | None = Field(
        default=None,
        description="When rehearing was denied below (`LowerCourtRehearingDenied`); the "
        "docket does not say whether panel or en banc rehearing",
    )


class OpinionAvailability(BaseModel):
    """One sub-opinion of a matched cluster: what it is and what upstream holds of it."""

    model_config = ConfigDict(extra="forbid")

    opinion_id: int
    type: str | None = Field(default=None, description="Upstream's opinion `type` code")
    author: str | None = Field(default=None, description="Upstream's `author_str`")
    per_curiam: bool | None = None
    joined_by: str | None = Field(default=None, description="Upstream's `joined_by_str`")
    has_download_url: bool = Field(
        description="Whether `download_url` (the court's own file link) is set"
    )
    has_local_file: bool = Field(description="Whether `local_path` (upstream's stored copy) is set")
    has_plain_text: bool = Field(description="Whether `plain_text` carries non-blank text")


class ClusterMatch(BaseModel):
    """An opinion cluster on a checked docket row, dated on or before the docketing."""

    model_config = ConfigDict(extra="forbid")

    cluster_id: int
    docket_id: int | None = Field(default=None, description="The row the cluster hangs on")
    date_filed: date | None = None
    on_judgment_date: bool = Field(description="Whether `date_filed` is the judgment date")
    precedential_status: str | None = None
    judges: str | None = Field(default=None, description="Upstream's `judges` string")
    panel_links: int = Field(
        default=0, ge=0, description="How many `panel` person links the cluster carries"
    )
    opinions: list[OpinionAvailability] = Field(
        default_factory=list, description="Read only for a cluster on the judgment date"
    )


class DocketRow(BaseModel):
    """A CourtListener docket row in the lower court filed under the case's number."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    docket_number: str | None = None
    case_name: str | None = None
    panel: str | None = Field(default=None, description="Upstream's `panel_str`, where set")
    cluster_links: int = Field(ge=0, description="How many `clusters` links the row carries")


class EntryCite(BaseModel):
    """A docket entry the rehearing reading rests on."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    entry_number: int | None = None
    date_filed: date | None = None


class RehearingReading(BaseModel):
    """The en banc reading of a lower-court docket's post-judgment entries.

    Text-derived: each flag is a pattern match over the entries' filed text,
    and ``cites`` names every entry that set one. ``None`` means no entry was
    read, which is not the same answer as ``False``.
    """

    model_config = ConfigDict(extra="forbid")

    entries_read: int = Field(ge=0, description="Entries read, filed on or after the judgment")
    petition_filed: bool | None = None
    disposition: Literal["denied", "granted"] | None = None
    dissent_noted: bool | None = None
    cites: list[EntryCite] = Field(default_factory=list)
    unavailable: str | None = Field(
        default=None, description="Why entries could not be read, where upstream refused them"
    )


class DecisionBelowMatch(BaseModel):
    """One case's decision-below join: what was asked, what upstream answered."""

    model_config = ConfigDict(extra="forbid")

    case_id: str | None = Field(default=None, description="The corpus case id, where one")
    facts: LowerCourtFacts
    status: MatchStatus
    reason: str = Field(description="Why the status, in a sentence")
    dockets: list[DocketRow] = Field(default_factory=list)
    clusters: list[ClusterMatch] = Field(default_factory=list)
    rehearing: RehearingReading | None = None
    requests: int = Field(default=0, ge=0, description="REST requests this case issued")


class DecisionBelowReport(BaseModel):
    """A dry run's per-case matches and the tally a maintainer reads the rate from."""

    model_config = ConfigDict(extra="forbid")

    matches: list[DecisionBelowMatch] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict, description="Cases per status")
    requests: int = Field(default=0, ge=0)
    stopped: str | None = Field(default=None, description="Why the walk ended early")
    deferred: list[str] = Field(
        default_factory=list, description="Cases the walk did not reach, by label"
    )


# --- reading the SCOTUS docket ------------------------------------------------


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _served_date(value: object) -> date | None:
    """A docket JSON date (``"April 9, 2025"``), or ``None`` when it is not one."""
    text = _text(value)
    if text is None:
        return None
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _iso_date(value: object) -> date | None:
    """An upstream ISO date or datetime (``"2025-04-09"``), or ``None``."""
    text = _text(value)
    if text is None:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def split_lower_numbers(raw: object) -> list[str]:
    """The lower-court numbers a ``LowerCourtCaseNumbers`` string lists.

    The JSON parenthesizes the list and separates numbers with commas
    (``"(24-812, 24-901)"``); a semicolon separates them on some dockets too.
    Order is kept and duplicates collapse.
    """
    text = _text(raw)
    if text is None:
        return []
    found: list[str] = []
    for part in re.split(r"[,;]", text.strip().strip("()")):
        number = part.strip().strip("()").strip()
        if number and number not in found:
            found.append(number)
    return found


def lower_court_facts(payload: Mapping[str, Any]) -> LowerCourtFacts:
    """The lower-court facts a supremecourt.gov docket JSON carries."""
    name = _text(payload.get("LowerCourt"))
    return LowerCourtFacts(
        scotus_docket_number=_text(payload.get("CaseNumber")),
        scotus_docketed=_served_date(payload.get("DocketedDate")),
        court_name=name,
        court_id=live_lower_court_id(name),
        docket_numbers=split_lower_numbers(payload.get("LowerCourtCaseNumbers")),
        judgment_date=_served_date(payload.get("LowerCourtDecision")),
        rehearing_denied=_served_date(payload.get("LowerCourtRehearingDenied")),
    )


def unmapped_class(name: str) -> str:
    """The class of court an unmapped ``LowerCourt`` name reads as, for the report."""
    for label, pattern in _UNMAPPED_CLASSES:
        if pattern.search(name):
            return label
    return "unrecognized tribunal"


def appellate_core(number: str) -> str | None:
    """Upstream's ``docket_number_core`` for an appellate number, or ``None``.

    Mirrors upstream's appellate rule: the first ``YY-N…`` in the number, the
    serial zero-padded to six digits, so ``"24-50496"`` and ``"2024-50496"``
    both read ``"24050496"``. A number with no such part has no core.
    """
    # The corpus normalizer folds typographic dashes and drops a "No." label.
    match = _APPELLATE_CORE_RE.search(corpus.normalize_docket_number(number) or "")
    if match is None:
        return None
    return f"{match.group(1)}{int(match.group(2)):06d}"


def number_names(served: object, wanted: str) -> bool:
    """Whether a served docket number is ``wanted`` by either spelling.

    Equal under :func:`fedcourtsai.corpus.normalize_docket_number`, or sharing
    an :func:`appellate_core`. A served value that is not a string matches
    nothing.
    """
    if not isinstance(served, str):
        return False
    left = corpus.normalize_docket_number(served)
    if left is not None and left == corpus.normalize_docket_number(wanted):
        return True
    core = appellate_core(wanted)
    return core is not None and appellate_core(served) == core


# --- the rehearing reading -----------------------------------------------------


@dataclass(frozen=True)
class _EntryReading:
    petition: bool = False
    denied: bool = False
    granted: bool = False
    dissent: bool = False


def read_entry(text: str) -> _EntryReading:
    """What one docket entry's text says about rehearing en banc.

    An entry that does not mention rehearing en banc says nothing. One that does
    is a disposition when it reads as an order (or carries a disposition word
    without a petition word), and a petition otherwise; a dissent counts only on
    a disposition, where it is a dissent from the order.
    """
    if not _EN_BANC_RE.search(text):
        return _EntryReading()
    denied = bool(_DENIED_RE.search(text))
    granted = bool(_GRANTED_RE.search(text)) and not denied
    is_order = bool(_ORDER_RE.search(text)) or (
        (denied or granted) and not _PETITION_RE.search(text)
    )
    if is_order and (denied or granted):
        return _EntryReading(denied=denied, granted=granted, dissent=bool(_DISSENT_RE.search(text)))
    return _EntryReading(petition=bool(_PETITION_RE.search(text)))


def _entry_text(entry: Mapping[str, Any]) -> str:
    parts = [entry.get("description")]
    docs = entry.get("recap_documents")
    if isinstance(docs, list):
        parts.extend(doc.get("description") for doc in docs if isinstance(doc, Mapping))
    return " ".join(part for part in parts if isinstance(part, str))


def read_rehearing(entries: Iterable[tuple[int, Mapping[str, Any]]]) -> RehearingReading:
    """The en banc reading over ``(docket_id, entry)`` pairs."""
    read = 0
    petition = denied = granted = dissent = False
    cites: list[EntryCite] = []
    for docket_id, entry in entries:
        read += 1
        found = read_entry(_entry_text(entry))
        if not (found.petition or found.denied or found.granted):
            continue
        petition = petition or found.petition
        denied = denied or found.denied
        granted = granted or found.granted
        dissent = dissent or found.dissent
        number = entry.get("entry_number")
        cites.append(
            EntryCite(
                docket_id=docket_id,
                entry_number=number
                if isinstance(number, int) and not isinstance(number, bool)
                else None,
                date_filed=_iso_date(entry.get("date_filed")),
            )
        )
    if read == 0:
        return RehearingReading(entries_read=0)
    disposition: Literal["denied", "granted"] | None = (
        "denied" if denied else "granted" if granted else None
    )
    return RehearingReading(
        entries_read=read,
        # A disposition implies a petition was before the court, whether or not
        # its filing entry was among those read.
        petition_filed=petition or disposition is not None,
        disposition=disposition,
        dissent_noted=dissent if disposition is not None else False,
        cites=cites,
    )


# --- the walk ------------------------------------------------------------------


def _int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _object(payload: object) -> Mapping[str, Any]:
    """A response body that is a JSON object, or a :class:`ValueError`.

    The client returns whatever the body parsed to; a body that is not an
    object is a one-case fault the batch records, not an attribute error that
    ends the run.
    """
    if not isinstance(payload, Mapping):
        raise ValueError(f"CourtListener served a {type(payload).__name__}, not an object")
    return payload


class _Walk:
    """One case's requests, counted as they are issued."""

    def __init__(self, client: CourtListenerClient) -> None:
        self.client = client
        self.requests = 0

    def dockets(self, court: str, number: str) -> list[Mapping[str, Any]]:
        """The checked rows for one number: exact spelling first, then the core."""
        asks: list[tuple[str, bool]] = [(number, False)]
        core = appellate_core(number)
        if core is not None:
            asks.append((core, True))
        for value, by_core in asks:
            self.requests += 1
            page = _object(
                self.client.list_dockets_by_number(court=court, docket_number=value, core=by_core)
            )
            results = page.get("results")
            if not isinstance(results, list):
                continue
            checked = [
                row
                for row in results
                if isinstance(row, Mapping)
                and docket_court(row, base_url=self.client.base_url) == court
                and number_names(row.get("docket_number"), number)
            ]
            if checked:
                return checked
        return []

    def cluster(self, cluster_id: int) -> Mapping[str, Any]:
        self.requests += 1
        return _object(self.client.get_cluster(cluster_id))

    def opinion(self, opinion_id: int) -> Mapping[str, Any]:
        self.requests += 1
        return _object(self.client.get_opinion(opinion_id))

    def entries(self, docket_id: int, since: date | None) -> list[Mapping[str, Any]]:
        found: list[Mapping[str, Any]] = []
        for page in range(1, MAX_ENTRY_PAGES + 1):
            self.requests += 1
            payload = _object(
                self.client.list_docket_entries(docket_id, page=page, date_filed_gte=since)
            )
            results = payload.get("results")
            if isinstance(results, list):
                found.extend(entry for entry in results if isinstance(entry, Mapping))
            if not payload.get("next"):
                break
        return found


def _availability(opinion_id: int, payload: Mapping[str, Any]) -> OpinionAvailability:
    text = payload.get("plain_text")
    per_curiam = payload.get("per_curiam")
    return OpinionAvailability(
        opinion_id=opinion_id,
        type=_text(payload.get("type")),
        author=_text(payload.get("author_str")),
        per_curiam=per_curiam if isinstance(per_curiam, bool) else None,
        joined_by=_text(payload.get("joined_by_str")),
        has_download_url=_text(payload.get("download_url")) is not None,
        has_local_file=_text(payload.get("local_path")) is not None,
        has_plain_text=isinstance(text, str) and bool(text.strip()),
    )


def _docket_row(row: Mapping[str, Any], *, base_url: str) -> DocketRow | None:
    docket_id = _int(row.get("id"))
    if docket_id is None:
        return None
    links = row.get("clusters")
    return DocketRow(
        docket_id=docket_id,
        docket_number=_text(row.get("docket_number")),
        case_name=_text(row.get("case_name")),
        panel=_text(row.get("panel_str")),
        cluster_links=len(_linked_ids(links, base_url=base_url, resource="clusters")),
    )


def _linked_ids(links: object, *, base_url: str, resource: str) -> list[int]:
    """The followable ids in a list of upstream hyperlinks, order kept.

    Every link passes the opinion enrichment's hyperlink guard
    (:func:`~fedcourtsai.pipeline.opinion_enrichment.resource_id`), so only an
    id reaches the client, which builds its own request path.
    """
    found: list[int] = []
    for link in links if isinstance(links, list) else []:
        ident = resource_id(link, base_url=base_url, resource=resource)
        if ident is not None and ident not in found:
            found.append(ident)
    return found


def match_case(
    client: CourtListenerClient, facts: LowerCourtFacts, *, case_id: str | None = None
) -> DecisionBelowMatch:
    """Join one case's lower-court facts to CourtListener.

    Raises what the client raises — a batch caller decides which faults stop
    the walk (:func:`match_cases`).
    """
    return _match(_Walk(client), facts, case_id=case_id)


def _unjoinable(facts: LowerCourtFacts) -> tuple[MatchStatus, str] | None:
    """Why a case cannot be joined before any request, or ``None`` if it can."""
    if facts.court_name is None and not facts.docket_numbers:
        return "no_lower_court", "the SCOTUS docket names no lower court or lower-court number"
    if facts.court_id is None:
        label = unmapped_class(facts.court_name) if facts.court_name else "unnamed court"
        return "unmapped_court", f"{label}: only the federal courts of appeals are joined"
    if not facts.docket_numbers:
        return (
            "no_lower_court",
            "the SCOTUS docket names the lower court but no lower-court number",
        )
    return None


def _checked_rows(walk: _Walk, court: str, numbers: Sequence[str]) -> list[Mapping[str, Any]]:
    """Every checked docket row for the case's numbers, each row once."""
    rows: list[Mapping[str, Any]] = []
    seen: set[int] = set()
    for number in numbers[:MAX_LOWER_NUMBERS]:
        for row in walk.dockets(court, number):
            ident = _int(row.get("id"))
            if ident is not None and ident not in seen:
                seen.add(ident)
                rows.append(row)
    return rows


def _clusters(
    walk: _Walk, rows: Sequence[Mapping[str, Any]], facts: LowerCourtFacts
) -> list[ClusterMatch]:
    """The clusters the rows link, dated on or before the docketing.

    A cluster dated after the SCOTUS docketing cannot be the decision the
    petition asks about, so it is dropped; one with no date is kept, since
    nothing rules it out. Sub-opinions are read only for a cluster on the
    judgment date — the candidate for the decision below.
    """
    base_url = walk.client.base_url
    clusters: list[ClusterMatch] = []
    followed = 0
    for row in rows:
        for cluster_id in _linked_ids(row.get("clusters"), base_url=base_url, resource="clusters"):
            if followed >= MAX_CLUSTERS:
                return clusters
            followed += 1
            cluster = walk.cluster(cluster_id)
            filed = _iso_date(cluster.get("date_filed"))
            docketed = facts.scotus_docketed
            if filed is not None and docketed is not None and filed > docketed:
                continue
            on_date = filed is not None and filed == facts.judgment_date
            panel = cluster.get("panel")
            opinions = (
                _linked_ids(cluster.get("sub_opinions"), base_url=base_url, resource="opinions")
                if on_date
                else []
            )
            clusters.append(
                ClusterMatch(
                    cluster_id=cluster_id,
                    docket_id=_int(row.get("id")),
                    date_filed=filed,
                    on_judgment_date=on_date,
                    precedential_status=_text(cluster.get("precedential_status")),
                    judges=_text(cluster.get("judges")),
                    panel_links=len(panel) if isinstance(panel, list) else 0,
                    opinions=[
                        _availability(opinion_id, walk.opinion(opinion_id))
                        for opinion_id in opinions[:MAX_OPINIONS]
                    ],
                )
            )
    return clusters


def _verdict(
    clusters: Sequence[ClusterMatch], dockets: Sequence[DocketRow], facts: LowerCourtFacts
) -> tuple[MatchStatus, str]:
    on_date = [c for c in clusters if c.on_judgment_date]
    if on_date:
        return (
            "matched",
            f"{len(on_date)} cluster(s) dated {facts.judgment_date} on "
            + f"{len(dockets)} {facts.court_id} docket row(s)",
        )
    if clusters:
        return (
            "no_cluster_on_date",
            "clusters dated on or before the docketing exist, none on the judgment date "
            + f"({facts.judgment_date or 'not served'})",
        )
    return (
        "no_cluster",
        "the docket row(s) carry no opinion cluster dated on or before the docketing",
    )


def _match(walk: _Walk, facts: LowerCourtFacts, *, case_id: str | None) -> DecisionBelowMatch:
    refused = _unjoinable(facts)
    if refused is not None:
        return DecisionBelowMatch(
            case_id=case_id, facts=facts, status=refused[0], reason=refused[1]
        )
    court = facts.court_id
    if court is None:  # _unjoinable refuses an unmapped court; this narrows the type
        raise AssertionError("an unmapped court reached the join")
    rows = _checked_rows(walk, court, facts.docket_numbers)
    base_url = walk.client.base_url
    dockets = [d for d in (_docket_row(row, base_url=base_url) for row in rows) if d is not None]
    if not dockets:
        return DecisionBelowMatch(
            case_id=case_id,
            facts=facts,
            status="no_docket",
            reason=f"CourtListener holds no {court} docket under "
            + ", ".join(facts.docket_numbers[:MAX_LOWER_NUMBERS]),
            requests=walk.requests,
        )
    clusters = _clusters(walk, rows, facts)
    rehearing = _rehearing(walk, dockets, facts)
    status, reason = _verdict(clusters, dockets, facts)
    return DecisionBelowMatch(
        case_id=case_id,
        facts=facts,
        status=status,
        reason=reason,
        dockets=dockets,
        clusters=clusters,
        rehearing=rehearing,
        requests=walk.requests,
    )


def _rehearing(
    walk: _Walk, dockets: Sequence[DocketRow], facts: LowerCourtFacts
) -> RehearingReading:
    pairs: list[tuple[int, Mapping[str, Any]]] = []
    for row in dockets[:MAX_ENTRY_DOCKETS]:
        try:
            pairs.extend(
                (row.docket_id, entry) for entry in walk.entries(row.docket_id, facts.judgment_date)
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in (401, 403):
                return RehearingReading(
                    entries_read=0,
                    unavailable=f"CourtListener refused the docket entries (HTTP {status})",
                )
            raise
    return read_rehearing(pairs)


def _stop_reason(exc: Exception) -> str | None:
    if isinstance(exc, RateBudgetExceeded):
        return f"API budget exhausted ({exc})"
    if is_throttled(exc):
        return f"CourtListener throttling persisted ({exc})"
    return None


@dataclass(frozen=True)
class CaseInput:
    """One case to match: a label for the report and the facts to join."""

    label: str
    facts: LowerCourtFacts
    case_id: str | None = None


def match_cases(client: CourtListenerClient, cases: Sequence[CaseInput]) -> DecisionBelowReport:
    """Match each case in turn, stopping cleanly at a batch-level wall."""
    report = DecisionBelowReport()
    for index, item in enumerate(cases):
        walk = _Walk(client)
        try:
            found = _match(walk, item.facts, case_id=item.case_id)
        except (RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
            reason = _stop_reason(exc)
            if reason is not None:
                # The case that hit the wall defers with the rest; what it spent
                # still counts.
                report.requests += walk.requests
                report.stopped = reason
                report.deferred = [pending.label for pending in cases[index:]]
                break
            found = DecisionBelowMatch(
                case_id=item.case_id,
                facts=item.facts,
                status="failed",
                reason=f"{type(exc).__name__}: {exc}",
                requests=walk.requests,
            )
        report.matches.append(found)
        report.requests += found.requests
        report.counts[found.status] = report.counts.get(found.status, 0) + 1
    return report


# --- the inputs ----------------------------------------------------------------

#: The CourtListener ids the join addresses: the federal courts of appeals.
JOINED_COURTS: Final = frozenset({f"ca{n}" for n in range(1, 12)} | {"cadc", "cafc"})


def facts_for_row(conn: corpus.ReadConnection, row: corpus.CorpusRow) -> LowerCourtFacts:
    """A corpus case's lower-court facts, from its newest live snapshot.

    The supremecourt.gov payload is the only stored source of the judgment and
    rehearing dates. A case with no live snapshot falls back to the row's own
    linkage columns, which carry the court and number but no dates — so its
    join can find a docket but never a cluster on the judgment date.
    """
    snapshot = corpus.latest_live_snapshot(conn, row.case_id)
    if snapshot is not None:
        return lower_court_facts(snapshot[1])
    court_id = row.originating_court if row.originating_court in JOINED_COURTS else None
    return LowerCourtFacts(
        scotus_docket_number=row.docket_number or None,
        scotus_docketed=row.date_filed,
        court_name=row.originating_court_name,
        court_id=court_id or live_lower_court_id(row.originating_court_name),
        docket_numbers=split_lower_numbers(row.originating_docket_number),
    )


def sample_rows(conn: corpus.ReadConnection, size: int) -> list[corpus.CorpusRow]:
    """The newest ``size`` cert-form SCOTUS rows whose lower court is a joined circuit.

    Newest by Term and serial, so the sample is the petitions the pipeline is
    forecasting now; the court is read from the row's own linkage columns, so
    choosing the sample reads no snapshot.
    """
    picked: list[tuple[tuple[int, int], corpus.CorpusRow]] = []
    for row in corpus.iter_rows(conn, court="scotus"):
        serial = parse_scotus_docket_number(corpus.strip_docket_annotation(row.docket_number))
        if serial is None:
            continue
        court = row.originating_court or live_lower_court_id(row.originating_court_name)
        if court in JOINED_COURTS:
            picked.append((serial, row))
    picked.sort(key=lambda pair: pair[0], reverse=True)
    return [row for _, row in picked[: max(size, 0)]]
