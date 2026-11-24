"""The decision below: locating a SCOTUS petition's lower-court ruling on CourtListener.

A cert petition names the judgment it asks the Court to review, and the
supremecourt.gov docket JSON carries the facts that identify it: the lower
court's name (``LowerCourt``), its case number or numbers
(``LowerCourtCaseNumbers``), the judgment date (``LowerCourtDecision``) and,
where one was denied, the date rehearing was denied
(``LowerCourtRehearingDenied``). This module joins those facts to
CourtListener and reports what it finds there — the lower court's docket row,
the opinion cluster dated on the judgment date (or the one that follows a
judgment entered by order), whether that opinion carries a
downloadable file or extracted text, the panel, and, where upstream holds the
docket's entries (RECAP), whether a petition for rehearing en banc was filed,
how it was disposed of, and whether a dissent from the disposition was noted.

**A measurement, and a fill.** The ``decision-below`` command writes nothing:
it prints one :class:`DecisionBelowMatch` per case so a maintainer can measure
the match rate. The ``enrich-decision-below`` command walks the same join over
a rotation (:func:`fill_candidates`) and stores what upstream holds
(:func:`fill_decision_below`): the opinion on the judgment date, with any
amended opinion or opinion on rehearing filed after it and before the SCOTUS
docketing, as a ``decision-below`` document, the docket record as a
``lower-court-docket`` document, and the case's
``decision_below_attempted_at`` stamp. Both kinds
reach cert and merits cells only (``provision.LOWER_COURT_STAGES``), under the
``decision-below-documents`` harness boundary. No request buys anything: the
client reads CourtListener's REST API only, and RECAP Fetch is never called.

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
this number, by either spelling, or it is dropped. The clusters are then
asked for by the court and each checked row's own number, dated on or before
the SCOTUS docketing — one list request however many clusters a row carries —
and a returned cluster must hang on a checked row. A cluster counts as the
decision below when its ``date_filed`` is the judgment date, or under the
rule for a judgment entered by order below. Several
clusters on the judgment date are all reported, since a court can issue an
opinion and an amended one the same day; a list that says more exist than one
page holds is reported ``clusters_truncated``. A cluster dated after the
judgment date, still on or before the docketing, is reported ``after_judgment``
and read too: a court that amends its opinion, or publishes its order on
rehearing with the writings attached, files it as a later cluster on the same
docket, and that is the text the petition then quotes. It does not make a
match where the judgment date has a cluster of its own.

**A judgment entered by order has its opinion filed later.** A court can enter
judgment by order and file the opinion that explains it weeks afterwards; the
SCOTUS docket then names the order's date, which carries no cluster. So where
no row — found by number or by the opinion search below — carries a cluster on
the judgment date, the earliest cluster filed after it is reported
``follows_judgment`` and makes the match: it is on or before the docketing as
every later cluster is, and filed before any rehearing denial the SCOTUS
docket states, since a cluster filed on or after that day is a writing on
rehearing, not the opinion the petition for rehearing asked about. Clusters
sharing that earliest date are all marked. The read is an inference from
dates, and the stored rows say so: the reason, the opinion's header and the
docket record each state that the judgment date has no opinion of its own and
that this is the earliest filed after it. Nothing is marked where that
emptiness was not established: a cluster list that ran past one page, or a
request of the opinion search that upstream refused or failed, leaves the case
``no_cluster_on_date`` with its later clusters read and stored as before.

**A consolidated appeal's opinion can sit on a row no number reaches.** A
court's opinion feed can file the opinion of a consolidated appeal on a docket
row of its own, numbered for the lead appeals together
(``"23-258 (L); 23-354 (L)"``), which neither number filter returns; the rows
they do return then carry no cluster. So where no checked row carries a
cluster on the judgment date, one opinion search asks for the court's opinions
filed on that date that mention any of the case's numbers. A hit is a lead,
not an answer. Its docket is fetched and must be this court's, its clusters
are listed and checked as any row's are, and the row joins the case only where
it carries a cluster on the judgment date and is tied to the case by one of
two things, reported as ``lead_by``: its docket number lists one of the case's
numbers, or — for a member appeal the combined number leaves out — the caption
of its opinion on the judgment date does, read over the first
:data:`CAPTION_CHARS` of the text with the number standing alone. An opinion
that cites the number further in passes neither test. The caption test reads
position, not layout: another opinion of the same court, filed the same day,
that names the number on its first page (a companion heard in tandem) would
pass it, which is why the docket record says how each added row was found and
by which test. Only the first sub-opinion's extracted text is read, so an
opinion upstream holds without text is not tied this way. At most
:data:`MAX_LEAD_DOCKETS` rows are added, after the number-matched ones. A case
with no row found by number is ``no_docket`` and is not searched for, and a
refused or failed request on this path leaves the case as the number join
answered it.

**The rehearing reading is text, and says so.** CourtListener serves docket
entries as filed text with no structured rehearing field, so the en banc
reading is a pattern match over the text of each entry filed on or after the
judgment date and before the SCOTUS docketing — its own ``description`` and
those of its documents, since upstream fills one or the other — with every
entry that drove it cited by number and date. A motion about the *time* to
petition is not a petition, and its grant is not a grant of rehearing. A
positive reading is a fact about the entries read; a negative one is reported
only when the read was complete — every row, every page — and is ``None``
otherwise. Upstream holds a circuit docket only as far as someone last
uploaded it, so a complete read can still end before the court ruled: where
the SCOTUS docket states a rehearing denial and the entries show no
disposition and none filed that late, the reading is ``short_of_denial`` and
reports no absence either. Nor is an absence reported where the text was not
there to match: an entry described nowhere is counted in ``blank_entries``,
and a complete read that reaches the stated denial without an entry recording
an order on rehearing, panel or en banc, is ``denial_unrecorded`` — a court's
feed can label its orders "Court order filed" and nothing more. A dissent is
read off the order's own entry and off a separate writing docketed the same
day, which is how some circuits file one. A court can also publish its order
with the writings attached and docket it as an order and nothing more, so an
opinion cluster filed on the day of the disposition, or on the denial date
the SCOTUS docket states, leaves a dissent unknown rather than absent where
no entry names one: the cluster's metadata does not say whether it holds an
amended opinion, a dissent, a concurrence or a statement, and the docket
record names the cluster and says so. A cluster list that ran past one page
may hold such a cluster unseen, and leaves the dissent unknown as well.
Without a judgment date there is no bound to read from, so the entries are
not read.
The SCOTUS docket's own ``LowerCourtRehearingDenied`` date is reported beside
it unchanged; it does not say whether the denial was of panel or en banc
rehearing. A refusal or a fault on the entries degrades the reading to
``unavailable`` and leaves the docket and cluster match standing; only a
throttle wall propagates.

**Bounded spend.** Every request goes through the shared client and the rate
governor of the process that runs it. A case costs at most two docket
requests per lower-court number (up to :data:`MAX_LOWER_NUMBERS` numbers),
one cluster list per distinct checked number (up to the same cap), one
request per opinion read (up to :data:`MAX_OPINIONS` a case) and up to
:data:`MAX_ENTRY_PAGES` pages of entries for each of up to
:data:`MAX_ENTRY_DOCKETS` rows — 6 + 3 + 3 + 4 = 16 — and, where no checked
row carries a cluster on the judgment date, the opinion search's
:data:`MAX_SEARCH_REQUESTS`: the search, then a docket, a cluster list and a
caption read for each of up to :data:`MAX_LEAD_DOCKETS` rows, 1 + 6 = 7. That
is :data:`MAX_REQUESTS_PER_CASE`, 23, at worst; a single-number circuit case
with one matched opinion costs four, and one with no opinion upstream four as
well, the search in place of the opinion read.
The client's request budget (:class:`RateBudgetExceeded`), a 429 its retries
could not clear, or a 401 (the credential refused, which every later request
would meet too) stops the walk with the rest reported deferred, as the opinion
enrichment does.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from functools import partial
from typing import Any, Final, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled
from ..supremecourt import parse_scotus_docket_number
from .documents import KIND_DECISION_BELOW, KIND_LOWER_COURT_DOCKET
from .ingest import live_lower_court_id
from .opinion_enrichment import cluster_docket_id, docket_court, resource_id

#: Lower-court numbers asked per case. A consolidated petition can list many;
#: the first few carry the decision, and the cap bounds what one case spends.
MAX_LOWER_NUMBERS: Final = 3

#: Sub-opinions read per case, across its clusters on and after the judgment
#: date; it bounds the availability report and the stored text alike.
MAX_OPINIONS: Final = 3

#: Docket rows whose entries are read per case, and pages read per row.
MAX_ENTRY_DOCKETS: Final = 2
MAX_ENTRY_PAGES: Final = 2

#: Docket rows the opinion search may add to a case: rows a court's opinion
#: feed filed under a number of its own, which no number filter reaches.
MAX_LEAD_DOCKETS: Final = 2

#: How far into an opinion's text its caption is read for a docket number. A
#: consolidated caption lists every member appeal on the first page, after
#: any header the extraction keeps; a number met deeper in is a citation.
CAPTION_CHARS: Final = 4000

#: The most requests the opinion search adds to a case with no cluster on the
#: judgment date: the search, each added row's docket and cluster list, and a
#: caption read on each.
MAX_SEARCH_REQUESTS: Final = 1 + 3 * MAX_LEAD_DOCKETS

#: The most requests one case can cost (see the module docstring).
MAX_REQUESTS_PER_CASE: Final = (
    2 * MAX_LOWER_NUMBERS
    + MAX_LOWER_NUMBERS
    + MAX_OPINIONS
    + MAX_ENTRY_DOCKETS * MAX_ENTRY_PAGES
    + MAX_SEARCH_REQUESTS
)

#: The default and the largest sample of the ``decision-below`` command. The
#: ceiling keeps a sample's worst case (``MAX_SAMPLE * MAX_REQUESTS_PER_CASE``)
#: inside the held tier's daily allowance with room left for the pull windows.
DEFAULT_SAMPLE: Final = 20
MAX_SAMPLE: Final = 50

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
_GRANTED_RE: Final = re.compile(r"\bgrant(?:ed|s|ing)?\b|\bordered\b", re.I)
# "Rehearing en banc denied" / "en banc is ordered": the disposition stated on
# the phrase itself, which reads as one even beside a petition word (a mandate
# entry recites the petition it follows).
_DIRECT_DISPOSITION_RE: Final = re.compile(
    r"\ben\s+banc\s+(?:(?:is|was|be|are|were)\s+)?(?:hereby\s+)?"
    + r"(?:den(?:ied|y)|grant(?:ed)?|ordered)\b",
    re.I,
)
# A motion about the time to petition: neither a petition nor its disposition.
_TIME_MOTION_RE: Final = re.compile(
    r"\bextension\b|\b(?:extend|enlarg)\w*|\btime\s+to\s+file\b"
    + r"|\bleave\s+to\s+file\b.*\bout\s+of\s+time\b",
    re.I,
)
# Any rehearing, panel or en banc: an entry that names one beside a denial
# accounts for the denial the SCOTUS docket states.
_REHEARING_RE: Final = re.compile(r"\brehearing\b", re.I)
_DISSENT_RE: Final = re.compile(r"\bdissent(?:s|ed|ing)?\b", re.I)
# A clerk's label for a separate writing of either kind ("Concurring or
# Dissenting Opinion FILED"): it names no dissent, and does not rule one out.
_EITHER_WRITING_RE: Final = re.compile(r"\bconcurring\s+or\s+dissenting\b", re.I)
# An amended opinion filed with the rehearing order recites the panel's own
# dissent, which is not a dissent from that order.
_AMENDED_RE: Final = re.compile(r"\bamend(?:ed|ing|s)?\b", re.I)

# A marker a court hangs on one number of a combined docket number
# ("23-258 (L); 23-354 (L)", "(CON)", "(XAP)").
_NUMBER_MARKER_RE: Final = re.compile(r"\([^)]*\)")
# A docket number that can stand as a quoted search phrase: nothing in it can
# close the phrase or read as query syntax.
_SEARCHABLE_NUMBER_RE: Final = re.compile(r"[\w.:-]+")


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
    after_judgment: bool = Field(
        default=False,
        description="Whether `date_filed` falls after the judgment date and on or before the "
        "SCOTUS docketing: an amended opinion, one issued on rehearing, or the opinion on a "
        "judgment entered by order",
    )
    follows_judgment: bool = Field(
        default=False,
        description="Whether this is the earliest cluster filed after a judgment date that "
        "carries none, and before any rehearing denial the SCOTUS docket states: read as the "
        "opinion on a judgment the court entered by order",
    )
    precedential_status: str | None = None
    judges: str | None = Field(default=None, description="Upstream's `judges` string")
    panel_links: int = Field(
        default=0, ge=0, description="How many `panel` person links the cluster carries"
    )
    opinions: list[OpinionAvailability] = Field(
        default_factory=list,
        description="Read only for a cluster on the judgment date or after it, newest first",
    )


class DocketRow(BaseModel):
    """A CourtListener docket row in the lower court filed under the case's number."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    docket_number: str | None = None
    case_name: str | None = None
    panel: str | None = Field(default=None, description="Upstream's `panel_str`, where set")
    cluster_links: int = Field(ge=0, description="How many `clusters` links the row carries")
    lead_by: Literal["docket_number", "caption"] | None = Field(
        default=None,
        description="Set on a row the opinion search found rather than a number filter, and "
        "says what tied it to the case: its combined docket number lists one of the case's "
        "numbers, or the caption of its opinion on the judgment date does",
    )


class EntryCite(BaseModel):
    """A docket entry the rehearing reading rests on."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    entry_number: int | None = None
    date_filed: date | None = None


class RehearingReading(BaseModel):
    """The en banc reading of a lower-court docket's post-judgment entries.

    Text-derived: each flag is a pattern match over the entries' filed text,
    and ``cites`` names every entry that set one. ``True`` is a fact about the
    entries read. For ``petition_filed``, ``False`` is reported only when
    ``complete`` and none of ``short_of_denial``, ``denial_unrecorded`` and
    ``blank_entries`` is set, and ``None`` otherwise — an unread page is not
    evidence of absence, and neither is a docket upstream stopped receiving
    or an entry whose text does not say what was filed. For ``dissent_noted``
    beside a disposition, ``False`` needs a complete read, no unread
    writing on the disposition's day, no opinion cluster filed with the
    disposition (``disposition_day_clusters``) and cluster lists read whole.
    """

    model_config = ConfigDict(extra="forbid")

    entries_read: int = Field(
        ge=0,
        description="Entries read: those filed on or after the judgment date and before "
        "the SCOTUS docketing, on the rows and pages the caps admitted; 0 where none was read",
    )
    complete: bool = Field(
        default=False,
        description="Whether every post-judgment entry of every checked row was read — "
        "no row past the row cap, no page past the page cap",
    )
    through: date | None = Field(
        default=None, description="The latest filing date among the entries read"
    )
    short_of_denial: bool = Field(
        default=False,
        description="Whether the SCOTUS docket states a rehearing denial the entries read "
        "neither show nor reach: upstream holds no entry that late, so no absence is reported",
    )
    denial_unrecorded: bool = Field(
        default=False,
        description="Whether a complete read reaches the rehearing denial the SCOTUS docket "
        "states and no entry records a ruling on rehearing in its text, so no absence is reported",
    )
    blank_entries: int = Field(
        default=0,
        ge=0,
        description="Entries read that carry no text, on the entry or on its documents; "
        "any makes a petition's absence unknown",
    )
    petition_filed: bool | None = None
    disposition: Literal["denied", "granted"] | None = None
    dissent_noted: bool | None = Field(
        default=None, description="A dissent noted from the disposition; None without one"
    )
    disposition_day_clusters: list[int] = Field(
        default_factory=list,
        description="Opinion clusters filed after the judgment date on the day of the "
        "disposition, or on the rehearing denial date the SCOTUS docket states: an amended "
        "opinion, or the order published with its writings, which the metadata does not tell "
        "apart, so a dissent no entry names is unknown rather than absent; empty without a "
        "disposition",
    )
    cites: list[EntryCite] = Field(default_factory=list)
    unavailable: str | None = Field(
        default=None,
        description="Why the entries were not read: no judgment date to bound the read, "
        "or upstream refused or failed the request",
    )
    faulted: bool = Field(
        default=False,
        description="Whether `unavailable` is a refused or failed request, which another "
        "walk may not meet, rather than a fact about the case",
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
    clusters_truncated: bool = Field(
        default=False,
        description="Whether a cluster list held more than one page, so clusters beyond "
        "it were not seen",
    )
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
    stored: dict[str, int] = Field(
        default_factory=dict,
        description="Documents a fill stored (or, in a dry run, would store), per kind; "
        "empty for a measurement",
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


def lists_number(served: object, wanted: str) -> bool:
    """Whether a served docket number lists ``wanted``, alone or among several.

    A court's opinion feed can file a consolidated appeal under one combined
    number (``"23-258 (L); 23-354 (L)"``). Each part between semicolons or
    commas is read with its parenthesized marker dropped and compared by
    :func:`number_names`, so a part must be the number, not merely contain it.
    """
    if not isinstance(served, str):
        return False
    parts = re.split(r"[;,]", _NUMBER_MARKER_RE.sub(" ", served))
    return any(number_names(part, wanted) for part in parts if part.strip())


def caption_names(text: str, wanted: str) -> bool:
    """Whether an opinion's caption carries the docket number ``wanted``.

    Read over the first :data:`CAPTION_CHARS` of the text only. The number
    must stand alone: a longer serial (``23-4441``, ``23-444-5``) or a longer
    prefix (``123-444``, ``2:23-444``) is another case's, while a case-type
    suffix the court prints after it (``23-444-cv``) is not.
    """
    number = corpus.normalize_docket_number(wanted)
    if number is None:
        return False
    pattern = rf"(?<![\w:-]){re.escape(number)}(?!-?\d)"
    return re.search(pattern, text[:CAPTION_CHARS], re.I) is not None


def _search_query(numbers: Sequence[str]) -> str | None:
    """The opinion-search query for a case's numbers: each a quoted phrase, any of them."""
    terms: list[str] = []
    for raw in numbers[:MAX_LOWER_NUMBERS]:
        number = corpus.normalize_docket_number(raw)
        if number is not None and _SEARCHABLE_NUMBER_RE.fullmatch(number) and number not in terms:
            terms.append(number)
    return " OR ".join(f'"{term}"' for term in terms) or None


# --- the rehearing reading -----------------------------------------------------


@dataclass(frozen=True)
class _EntryReading:
    petition: bool = False
    denied: bool = False
    granted: bool = False
    dissent: bool = False


def read_entry(text: str) -> _EntryReading:
    """What one docket entry's text says about rehearing en banc.

    An entry that does not mention rehearing en banc says nothing, and neither
    does a motion about the time to file one: granting an extension is not
    granting rehearing. Otherwise an entry is a disposition when the phrase
    states one (``rehearing en banc denied``, ``en banc is ordered``), when it
    reads as an order, or when it carries a disposition word without a petition
    word; a petition otherwise. A dissent counts only on a disposition, where it
    is a dissent from the order.
    """
    if not _EN_BANC_RE.search(text) or _TIME_MOTION_RE.search(text):
        return _EntryReading()
    denied = bool(_DENIED_RE.search(text))
    granted = bool(_GRANTED_RE.search(text)) and not denied
    is_order = (
        bool(_DIRECT_DISPOSITION_RE.search(text))
        or bool(_ORDER_RE.search(text))
        or ((denied or granted) and not _PETITION_RE.search(text))
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


def _records_rehearing_denial(text: str) -> bool:
    """Whether an entry's text records a denial of rehearing, panel or en banc.

    The order test is :func:`read_entry`'s: the text reads as an order, or
    carries the denial without a petition word. A petition docketed beside
    the denial of some other motion is not the ruling, and neither is a
    motion about the time to petition.
    """
    if not _REHEARING_RE.search(text) or _TIME_MOTION_RE.search(text):
        return False
    if not _DENIED_RE.search(text):
        return False
    return bool(_ORDER_RE.search(text)) or not _PETITION_RE.search(text)


def read_separate_writing(text: str) -> bool | None:
    """Whether an entry that is not the rehearing order records a dissent.

    A circuit that dockets each writing on its own entry files a dissent from
    the denial of rehearing en banc beside the order, not inside it. ``True``
    where the text names a dissent; ``None`` where it carries only the clerk's
    either-kind label (``Concurring or Dissenting Opinion``), which neither
    names one nor rules one out, or names a dissent on an amended opinion,
    which may be the panel's own; ``False`` otherwise.
    """
    named = _EITHER_WRITING_RE.sub(" ", text)
    if _DISSENT_RE.search(named):
        return None if _AMENDED_RE.search(named) else True
    return None if named != text else False


def _cite(docket_id: int, entry: Mapping[str, Any]) -> EntryCite:
    number = entry.get("entry_number")
    return EntryCite(
        docket_id=docket_id,
        entry_number=number if isinstance(number, int) and not isinstance(number, bool) else None,
        date_filed=_iso_date(entry.get("date_filed")),
    )


def read_rehearing(
    entries: Iterable[tuple[int, Mapping[str, Any]]],
    *,
    complete: bool = True,
    judgment_date: date | None = None,
    rehearing_denied: date | None = None,
    clusters: Sequence[ClusterMatch] = (),
    clusters_whole: bool = True,
) -> RehearingReading:
    """The en banc reading over ``(docket_id, entry)`` pairs.

    ``complete`` says whether the pairs are every post-judgment entry upstream
    holds; without it a negative answer is ``None`` rather than ``False``.

    A dissent is read off the disposition's own entry, and off any other entry
    of the same docket filed the same day (:func:`read_separate_writing`) once
    that day is after
    ``judgment_date`` — on the judgment date itself a separate writing belongs
    to the panel's decision, not to the rehearing order. An either-kind label
    on the disposition's day leaves the dissent unknown rather than absent.

    ``clusters`` are the case's opinion clusters. One filed after the judgment
    date on a day an entry records the disposition, or on ``rehearing_denied``,
    is a writing the court published with its order, and a clerk can docket
    such an order without naming what is attached. Its metadata does not say
    whether it holds a dissent, so with a disposition read and no dissent
    named in the entries the dissent is unknown rather than absent, and the
    clusters are reported in ``disposition_day_clusters``. ``clusters_whole``
    says whether the cluster lists were read whole: a list that ran past one
    page may hold such a cluster unseen, so it leaves the dissent unknown too.

    ``rehearing_denied`` is the denial date the SCOTUS docket states. Where
    the entries show no disposition and none is filed that late, upstream
    stopped receiving the docket before the denial, so the reading is
    ``short_of_denial`` and reports no absence. Where they reach that date
    and none records a ruling on rehearing of either kind, the order is among
    them under a label that does not say so, and the reading is
    ``denial_unrecorded``. An entry with no text at all could be the petition,
    so any such entry leaves a petition's absence unknown, and one on the
    disposition's day leaves the dissent unknown.
    """
    read = blank = 0
    writing_unread = False
    petition = denied = granted = dissent = ruled = False
    cites: list[EntryCite] = []
    through: date | None = None
    disposed: set[tuple[int, date]] = set()
    others: list[tuple[int, Mapping[str, Any], date]] = []
    for docket_id, entry in entries:
        read += 1
        filed = _iso_date(entry.get("date_filed"))
        if filed is not None and (through is None or filed > through):
            through = filed
        text = _entry_text(entry)
        if not text.strip():
            blank += 1
            # An undated blank entry cannot be placed off the disposition's day.
            writing_unread = writing_unread or filed is None
        ruled = ruled or _records_rehearing_denial(text)
        found = read_entry(text)
        if not (found.petition or found.denied or found.granted):
            if filed is not None:
                others.append((docket_id, entry, filed))
            continue
        petition = petition or found.petition
        denied = denied or found.denied
        granted = granted or found.granted
        dissent = dissent or found.dissent
        if filed is not None and (found.denied or found.granted):
            disposed.add((docket_id, filed))
        cites.append(_cite(docket_id, entry))
    if read == 0:
        # Upstream holds entries only where someone uploaded them, so an empty
        # read is not evidence that nothing was filed, however complete.
        return RehearingReading(entries_read=0, complete=complete)
    for docket_id, entry, filed in others:
        if (docket_id, filed) not in disposed or (
            judgment_date is not None and filed <= judgment_date
        ):
            continue
        text = _entry_text(entry)
        writing = read_separate_writing(text) if text.strip() else None
        if writing:
            dissent = True
            cites.append(_cite(docket_id, entry))
        elif writing is None:
            writing_unread = True
    disposition: Literal["denied", "granted"] | None = (
        "denied" if denied else "granted" if granted else None
    )
    short = (
        disposition is None
        and rehearing_denied is not None
        and (through is None or through < rehearing_denied)
    )
    # Only a complete read can say the ruling is among the entries unlabelled:
    # on a partial one it may sit on a page not read.
    unrecorded = (
        complete
        and disposition is None
        and rehearing_denied is not None
        and not short
        and not ruled
    )
    negative = False if complete and not (short or unrecorded or blank) else None
    # A disposition implies a petition was before the court, whether or not its
    # filing entry was among those read.
    filed_any = petition or disposition is not None
    published = _disposition_day_clusters(
        clusters, {filed for _, filed in disposed}, rehearing_denied
    )
    with_order = published if disposition is not None else []
    unseen = writing_unread or not complete or not clusters_whole
    no_dissent = None if unseen or with_order else False
    return RehearingReading(
        entries_read=read,
        complete=complete,
        through=through,
        short_of_denial=short,
        denial_unrecorded=unrecorded,
        blank_entries=blank,
        petition_filed=True if filed_any else negative,
        disposition=disposition,
        dissent_noted=None if disposition is None else (True if dissent else no_dissent),
        disposition_day_clusters=with_order,
        cites=cites,
    )


def _disposition_day_clusters(
    clusters: Sequence[ClusterMatch], disposed: set[date], rehearing_denied: date | None
) -> list[int]:
    """The clusters filed after the judgment on a day rehearing was disposed of, oldest first.

    The day is one an entry records the disposition on, or the denial date
    the SCOTUS docket states. A cluster on the judgment date belongs to the
    panel's decision and is left out.
    """
    days = disposed | ({rehearing_denied} if rehearing_denied is not None else set())
    return [
        cluster.cluster_id
        for cluster in sorted(clusters, key=lambda c: (c.date_filed or date.min, c.cluster_id))
        if cluster.after_judgment and cluster.date_filed in days
    ]


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
        # Each read opinion's `plain_text`, kept off the report: the fill
        # stores it, and a measurement drops it with the walk.
        self.texts: dict[int, str] = {}
        self._opinions: dict[int, Mapping[str, Any]] = {}
        # Requests of the opinion search upstream refused or failed: with any,
        # the search did not establish that no row carries the opinion.
        self.search_faults = 0

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

    def clusters(self, court: str, number: str, on_or_before: date | None) -> Mapping[str, Any]:
        self.requests += 1
        return _object(
            self.client.list_clusters_by_docket_number(
                court=court, docket_number=number, date_filed_lte=on_or_before
            )
        )

    def opinion(self, opinion_id: int) -> Mapping[str, Any]:
        """One sub-opinion, requested once however often the walk asks for it."""
        held = self._opinions.get(opinion_id)
        if held is not None:
            return held
        self.requests += 1
        payload = _object(self.client.get_opinion(opinion_id))
        text = payload.get("plain_text")
        if isinstance(text, str) and text.strip():
            self.texts[opinion_id] = text
        self._opinions[opinion_id] = payload
        return payload

    def opinion_search(self, court: str, query: str, filed: date) -> Mapping[str, Any]:
        """The first page of the court's opinions filed on ``filed`` that match ``query``."""
        self.requests += 1
        day = filed.isoformat()
        return _object(
            self.client.search(
                {"type": "o", "court": court, "q": query, "filed_after": day, "filed_before": day}
            )
        )

    def docket(self, docket_id: int) -> Mapping[str, Any]:
        self.requests += 1
        return _object(self.client.get_docket(docket_id))

    def _count(self) -> None:
        self.requests += 1

    def entries(self, docket_id: int, since: date) -> tuple[list[Mapping[str, Any]], bool]:
        """A row's entries filed on or after ``since``, and whether all were read."""
        read = self.client.docket_entries(
            docket_id, max_pages=MAX_ENTRY_PAGES, date_filed_gte=since, on_request=self._count
        )
        found: list[Mapping[str, Any]] = [e for e in read.entries if isinstance(e, Mapping)]
        return found, read.complete


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


def _docket_row(
    row: Mapping[str, Any],
    *,
    base_url: str,
    lead_by: Literal["docket_number", "caption"] | None = None,
) -> DocketRow | None:
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
        lead_by=lead_by,
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


@dataclass
class _Clusters:
    found: list[ClusterMatch]
    # The sub-opinion ids of each cluster on or after the judgment date.
    links: dict[int, list[int]]
    truncated: bool = False


def _list_clusters(
    walk: _Walk, rows: Sequence[Mapping[str, Any]], court: str, facts: LowerCourtFacts
) -> _Clusters:
    """The clusters on the checked rows, dated on or before the docketing.

    One list request per distinct number the checked rows carry, filtered on
    the court, that number and ``date_filed`` on or before the SCOTUS
    docketing — a cluster dated later cannot be the decision the petition asks
    about. Each result is a full cluster serialization, so no per-cluster fetch
    follows, and each must name one of the checked rows
    (:func:`~fedcourtsai.pipeline.opinion_enrichment.cluster_docket_id`), or it
    is another case's and is dropped. Sub-opinion links are kept for a cluster
    on the judgment date — the candidate for the decision below — and for one
    dated after it, which is an amended opinion or one issued on rehearing and
    is what the petition asks the Court to review where it replaced the first
    (:func:`_read_opinions` reads them). Without a served docketing date
    nothing bounds a later cluster, and none is kept.
    """
    base_url = walk.client.base_url
    row_ids = {ident for ident in (_int(row.get("id")) for row in rows) if ident is not None}
    numbers: list[str] = []
    for row in rows:
        served = _text(row.get("docket_number"))
        if served is not None and served not in numbers:
            numbers.append(served)
    found: list[ClusterMatch] = []
    links: dict[int, list[int]] = {}
    seen: set[int] = set()
    truncated = False
    judgment, docketed = facts.judgment_date, facts.scotus_docketed
    for number in numbers[:MAX_LOWER_NUMBERS]:
        page = walk.clusters(court, number, docketed)
        results = page.get("results")
        if page.get("next"):
            truncated = True
        for cluster in results if isinstance(results, list) else []:
            if not isinstance(cluster, Mapping):
                continue
            cluster_id = _int(cluster.get("id"))
            docket_id = cluster_docket_id(cluster, base_url=base_url)
            if cluster_id is None or cluster_id in seen or docket_id not in row_ids:
                continue
            seen.add(cluster_id)
            filed = _iso_date(cluster.get("date_filed"))
            if filed is not None and docketed is not None and filed > docketed:
                continue
            on_date = filed is not None and filed == judgment
            later = (
                filed is not None
                and judgment is not None
                and docketed is not None
                and filed > judgment
            )
            if on_date or later:
                links[cluster_id] = _linked_ids(
                    cluster.get("sub_opinions"), base_url=base_url, resource="opinions"
                )
            panel = cluster.get("panel")
            found.append(
                ClusterMatch(
                    cluster_id=cluster_id,
                    docket_id=docket_id,
                    date_filed=filed,
                    on_judgment_date=on_date,
                    after_judgment=later,
                    precedential_status=_text(cluster.get("precedential_status")),
                    judges=_text(cluster.get("judges")),
                    panel_links=len(panel) if isinstance(panel, list) else 0,
                )
            )
    return _Clusters(found=found, links=links, truncated=truncated)


def _read_opinions(walk: _Walk, clusters: _Clusters) -> None:
    """Read the sub-opinions of the clusters on and after the judgment date.

    The newest cluster is read first, at most :data:`MAX_OPINIONS` a case, with
    one read held for the judgment-date cluster, or for the cluster that
    follows a judgment entered by order (``follows_judgment``): the cap falls
    on the earlier opinion, and never takes all of it.
    """
    found, links = clusters.found, clusters.links
    newest_first = sorted(
        (c for c in found if c.cluster_id in links),
        key=lambda c: c.date_filed or date.min,
        reverse=True,
    )
    # One read is held for the judgment-date cluster, so an order on rehearing
    # published with several writings cannot leave the panel's opinion unread.
    held = next(
        (
            c
            for c in newest_first
            if (c.on_judgment_date or c.follows_judgment) and links[c.cluster_id]
        ),
        None,
    )
    opinions_left = MAX_OPINIONS - (1 if held is not None else 0)
    for cluster in newest_first:
        take = max(opinions_left, 0) + (1 if cluster is held else 0)
        opinion_ids = links[cluster.cluster_id][:take]
        opinions_left -= len(opinion_ids) - (1 if cluster is held else 0)
        cluster.opinions = [
            _availability(opinion_id, walk.opinion(opinion_id)) for opinion_id in opinion_ids
        ]


@dataclass(frozen=True)
class _Lead:
    row: Mapping[str, Any]
    by: Literal["docket_number", "caption"]


def _lead_rows(
    walk: _Walk,
    court: str,
    facts: LowerCourtFacts,
    rows: Sequence[Mapping[str, Any]],
    clusters: _Clusters,
) -> list[_Lead]:
    """Rows the opinion search ties to the case, their clusters added to ``clusters``.

    A court's opinion feed can file a consolidated appeal's opinion on a docket
    row of its own, numbered for the lead appeals together
    (``"23-258 (L); 23-354 (L)"``) and carrying no ``docket_number_core``, so
    neither number filter reaches it and the rows it does reach carry no
    cluster. One search asks for the court's opinions filed on the judgment
    date that mention any of the case's numbers. A hit is a lead, not an
    answer: its docket is fetched and must be this court's, the clusters are
    listed by that row's own number as for any checked row, and the row is
    kept only where it carries a cluster on the judgment date and one of two
    things ties it to the case — its docket number lists one of the case's
    numbers (:func:`lists_number`), or, for a member appeal the combined
    number leaves out, the caption of its first opinion on the judgment date
    does (:func:`caption_names`). A hit that cites the number below the
    caption passes neither and is dropped with its clusters. A fault on any of
    these requests leaves the case as the number join answered it.
    """
    fetched = _searched_rows(walk, court, facts, rows)
    if not fetched:
        return []
    listed = _attempt(walk, lambda: _list_clusters(walk, fetched, court, facts))
    if listed is None:
        return []
    leads: list[_Lead] = []
    for row in fetched:
        ident = _int(row.get("id"))
        mine = [c for c in listed.found if c.docket_id == ident]
        by = _tied_by(walk, row, [c for c in mine if c.on_judgment_date], listed, facts)
        if by is None:
            continue
        leads.append(_Lead(row=row, by=by))
        clusters.found.extend(mine)
        clusters.links.update(
            {c.cluster_id: listed.links[c.cluster_id] for c in mine if c.cluster_id in listed.links}
        )
        clusters.truncated = clusters.truncated or listed.truncated
    return leads


def _searched_rows(
    walk: _Walk, court: str, facts: LowerCourtFacts, rows: Sequence[Mapping[str, Any]]
) -> list[Mapping[str, Any]]:
    """The court's docket rows an opinion search for the case's numbers points at.

    Rows not already checked, whose hit is this court's and filed on the
    judgment date, at most :data:`MAX_LEAD_DOCKETS`; each is fetched and must
    itself name this court.
    """
    judgment = facts.judgment_date
    query = _search_query(facts.docket_numbers)
    if judgment is None or query is None:
        return []
    known = {_int(row.get("id")) for row in rows}
    page = _attempt(walk, lambda: walk.opinion_search(court, query, judgment))
    results = page.get("results") if page is not None else None
    candidates: list[int] = []
    for hit in results if isinstance(results, list) else []:
        if not isinstance(hit, Mapping) or hit.get("court_id") != court:
            continue
        ident = _int(hit.get("docket_id"))
        if _iso_date(hit.get("dateFiled")) != judgment or ident is None:
            continue
        if ident not in known and ident not in candidates:
            candidates.append(ident)
    fetched: list[Mapping[str, Any]] = []
    for ident in candidates[:MAX_LEAD_DOCKETS]:
        row = _attempt(walk, partial(walk.docket, ident))
        if (
            row is not None
            and _int(row.get("id")) == ident
            and docket_court(row, base_url=walk.client.base_url) == court
        ):
            fetched.append(row)
    return fetched


def _attempt[T](walk: _Walk, call: Callable[[], T]) -> T | None:
    """``call``'s answer, or ``None`` where upstream refused or failed it.

    The opinion search is an extra look for a case the number join already
    answered about, so a fault on it leaves that answer standing, as a fault
    on the entries does; only a batch wall propagates. The fault is counted
    on the walk (``search_faults``), since a search that failed says nothing
    about what it would have found.
    """
    try:
        return call()
    except (httpx.HTTPError, ValueError) as exc:
        if _stop_reason(exc) is not None:
            raise
        walk.search_faults += 1
        return None


def _tied_by(
    walk: _Walk,
    row: Mapping[str, Any],
    on_date: Sequence[ClusterMatch],
    listed: _Clusters,
    facts: LowerCourtFacts,
) -> Literal["docket_number", "caption"] | None:
    """What ties a searched row to the case, or ``None`` where nothing does."""
    if not on_date:
        return None
    if any(lists_number(row.get("docket_number"), n) for n in facts.docket_numbers):
        return "docket_number"
    first = next((ids[0] for c in on_date if (ids := listed.links[c.cluster_id])), None)
    if first is None:
        return None
    if _attempt(walk, lambda: walk.opinion(first)) is None:
        return None
    text = walk.texts.get(first, "")
    return "caption" if any(caption_names(text, n) for n in facts.docket_numbers) else None


def _mark_following(clusters: Sequence[ClusterMatch], facts: LowerCourtFacts) -> None:
    """Mark the opinion that follows a judgment entered by order.

    Where no cluster is dated on the judgment date, the earliest cluster filed
    after it (``after_judgment``, so on or before the docketing) is marked
    ``follows_judgment``, with any other cluster of that date — unless the
    SCOTUS docket states a rehearing denial on or before that day, when the
    cluster is a writing on rehearing and nothing is marked. The caller marks
    only where the judgment date's emptiness was established: every cluster
    list read whole, and no request of the opinion search faulted.
    """
    if any(c.on_judgment_date for c in clusters):
        return
    later = [c.date_filed for c in clusters if c.after_judgment and c.date_filed is not None]
    if not later:
        return
    earliest = min(later)
    if facts.rehearing_denied is not None and earliest >= facts.rehearing_denied:
        return
    for cluster in clusters:
        if cluster.after_judgment and cluster.date_filed == earliest:
            cluster.follows_judgment = True


def _verdict(
    clusters: Sequence[ClusterMatch], dockets: Sequence[DocketRow], facts: LowerCourtFacts
) -> tuple[MatchStatus, str]:
    following = [c for c in clusters if c.follows_judgment]
    if following:
        return (
            "matched",
            f"no cluster dated {facts.judgment_date}; {len(following)} cluster(s) dated "
            + f"{following[0].date_filed}, the earliest filed after it, read as the opinion "
            + "on a judgment entered by order",
        )
    on_date = [c for c in clusters if c.on_judgment_date]
    if on_date:
        searched = {d.docket_id for d in dockets if d.lead_by is not None}
        return (
            "matched",
            f"{len(on_date)} cluster(s) dated {facts.judgment_date} on "
            + f"{len(dockets)} {facts.court_id} docket row(s)"
            + (
                ", on a row found by opinion search"
                if any(c.docket_id in searched for c in on_date)
                else ""
            ),
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
    clusters = _list_clusters(walk, rows, court, facts)
    if not any(c.on_judgment_date for c in clusters.found):
        for lead in _lead_rows(walk, court, facts, rows, clusters):
            found = _docket_row(lead.row, base_url=base_url, lead_by=lead.by)
            if found is not None:
                dockets.append(found)
    if not clusters.truncated and not walk.search_faults:
        _mark_following(clusters.found, facts)
    _read_opinions(walk, clusters)
    rehearing = _rehearing(walk, dockets, facts, clusters)
    status, reason = _verdict(clusters.found, dockets, facts)
    return DecisionBelowMatch(
        case_id=case_id,
        facts=facts,
        status=status,
        reason=reason,
        dockets=dockets,
        clusters=clusters.found,
        clusters_truncated=clusters.truncated,
        rehearing=rehearing,
        requests=walk.requests,
    )


def _rehearing(
    walk: _Walk,
    dockets: Sequence[DocketRow],
    facts: LowerCourtFacts,
    clusters: _Clusters,
) -> RehearingReading:
    """The en banc reading of the checked rows' post-judgment entries.

    The rehearing reading is a by-product of the match, so a fault on the
    entries degrades it to ``unavailable`` and the docket and cluster match
    stand; only a batch wall — the request budget, a persistent 429 —
    propagates, since every later case would meet it too.

    Only entries filed before the SCOTUS docketing are read, where the docket
    serves that date: the rehearing a petition follows is decided before it is
    docketed, and a later entry (a petition on remand, a mandate after the
    Court's judgment) would tell a cell what came of the petition. An undated
    entry is dropped on the same bound.
    """
    since = facts.judgment_date
    if since is None:
        return RehearingReading(
            entries_read=0, unavailable="no judgment date is served to bound the read"
        )
    pairs: list[tuple[int, Mapping[str, Any]]] = []
    complete = len(dockets) <= MAX_ENTRY_DOCKETS
    for row in dockets[:MAX_ENTRY_DOCKETS]:
        try:
            entries, whole = walk.entries(row.docket_id, since)
        except (httpx.HTTPError, ValueError) as exc:
            if _stop_reason(exc) is not None:
                raise
            if isinstance(exc, httpx.HTTPStatusError):
                why = f"CourtListener answered the docket entries HTTP {exc.response.status_code}"
            else:
                why = f"the docket entries could not be read ({type(exc).__name__})"
            return RehearingReading(entries_read=0, unavailable=why, faulted=True)
        complete = complete and whole
        pairs.extend(
            (row.docket_id, entry)
            for entry in entries
            if _before_docketing(entry, facts.scotus_docketed)
        )
    return read_rehearing(
        pairs,
        complete=complete,
        judgment_date=since,
        rehearing_denied=facts.rehearing_denied,
        clusters=clusters.found,
        clusters_whole=not clusters.truncated,
    )


def _before_docketing(entry: Mapping[str, Any], docketed: date | None) -> bool:
    if docketed is None:
        return True
    filed = _iso_date(entry.get("date_filed"))
    return filed is not None and filed < docketed


def _stop_reason(exc: Exception) -> str | None:
    if isinstance(exc, RateBudgetExceeded):
        return f"API budget exhausted ({exc})"
    if is_throttled(exc):
        return f"CourtListener throttling persisted ({exc})"
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 401:
        return "CourtListener refused the credential (HTTP 401)"
    return None


@dataclass(frozen=True)
class CaseInput:
    """One case to match: a label for the report and the facts to join."""

    label: str
    facts: LowerCourtFacts
    case_id: str | None = None


def match_cases(client: CourtListenerClient, cases: Sequence[CaseInput]) -> DecisionBelowReport:
    """Match each case in turn, stopping cleanly at a batch-level wall."""
    return _walk_cases(client, cases, None)


def _walk_cases(
    client: CourtListenerClient,
    cases: Sequence[CaseInput],
    on_match: Callable[[CaseInput, DecisionBelowMatch, _Walk], None] | None,
) -> DecisionBelowReport:
    """Match each case in turn, handing each answer to ``on_match``.

    A failed case is reported and not handed on: it says nothing about the
    docket. A batch-level wall stops the walk with the rest deferred.
    """
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
        if on_match is not None and found.status != "failed":
            on_match(item, found, walk)
    return report


# --- the inputs ----------------------------------------------------------------

#: The CourtListener ids the join addresses: the federal courts of appeals.
JOINED_COURTS: Final = frozenset({f"ca{n}" for n in range(1, 12)} | {"cadc", "cafc"})


def joins_lower_court(row: corpus.CorpusRow) -> bool:
    """Whether ``row``'s lower court is one the fill joins to CourtListener.

    The row's own originating court id where ingest latched one, else the
    court the payload's ``LowerCourt`` name maps to, read against
    :data:`JOINED_COURTS`. The court test :func:`fill_candidates` applies, asked
    alone so the predict backlog's arrival hold
    (:func:`fedcourtsai.pipeline.pull.derive_predict_backlog`) waits only on a
    row the fill can reach.
    """
    court = row.originating_court or live_lower_court_id(row.originating_court_name)
    return court in JOINED_COURTS


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


# --- the fill ------------------------------------------------------------------

#: The public site a stored row's link names: the opinion's cluster page and the
#: docket's page, which a reader can open, where the API path needs a token.
COURTLISTENER_SITE: Final = "https://www.courtlistener.com"

#: Days before a case CourtListener answered about is asked again. Upstream
#: ingests appellate opinions and RECAP entries late, so a docket or opinion
#: missing today can be there next month; asking every window would spend the
#: same requests to learn the same thing.
RETRY_DAYS: Final = 30

#: The default and the largest number of cases one fill walks. The ceiling
#: keeps a run's worst case (``MAX_FILL_CASES * MAX_REQUESTS_PER_CASE``) inside
#: an hour's allowance at the pull lanes' ceilings.
DEFAULT_FILL_CASES: Final = 25
MAX_FILL_CASES: Final = 50

# Sub-opinion types that carry the court's own opinion (combined, unanimous,
# lead, plurality), read before the separate writings.
_LEAD_TYPE_RE: Final = re.compile(r"^0[12]\d")


def _cap(text: str, char_cap: int) -> tuple[str, bool]:
    if len(text) <= char_cap:
        return text, False
    return text[:char_cap], True


def _decided(match: DecisionBelowMatch) -> list[ClusterMatch]:
    """The clusters that carry the decision below, newest first.

    Those on the judgment date and those after it (the opinion on a judgment
    entered by order, an amended opinion, or one issued on rehearing); a
    cluster before the judgment date is an earlier stage of the appeal and is
    left out.
    """
    return sorted(
        (c for c in match.clusters if c.on_judgment_date or c.after_judgment),
        key=lambda c: c.date_filed or date.min,
        reverse=True,
    )


def opinion_document(
    match: DecisionBelowMatch, texts: Mapping[int, str], *, today: date, char_cap: int
) -> corpus.CaseDocument | None:
    """The decision below as a stored ``decision-below`` row, where upstream holds its text.

    Every sub-opinion with text of the clusters on the judgment date and of
    those after it, the newest cluster first — a later opinion ahead of the
    judgment-date one — and, within a cluster, the court's own opinion first.
    Each sits under a ``=== <type> (<author>) ===`` header where there is more
    than one; where a cluster is dated after the judgment date, every header
    carries its cluster's filing date and that cluster's says it follows the
    judgment, or, for the opinion on a judgment entered by order
    (``follows_judgment``), that it is the earliest filed after a judgment
    date with no opinion of its own. Cut at ``char_cap``. Dated on the newest
    cluster it holds, which is what places it against a moment cutoff and
    never follows the SCOTUS docketing. ``None`` for a case with no such cluster, or whose opinions
    carry no text.
    """
    judgment = match.facts.judgment_date
    if match.case_id is None or judgment is None:
        return None
    clusters = _decided(match)
    opinions = [
        (cluster, opinion)
        for cluster in clusters
        for opinion in sorted(
            cluster.opinions, key=lambda o: 0 if _LEAD_TYPE_RE.match(o.type or "") else 1
        )
        if opinion.opinion_id in texts
    ]
    if not opinions:
        return None
    dated = any(cluster.after_judgment for cluster, _ in opinions)
    parts: list[str] = []
    for cluster, opinion in opinions:
        body = texts[opinion.opinion_id].strip()
        if len(opinions) > 1 or dated:
            label = opinion.type or "opinion"
            if opinion.author:
                label += f" ({opinion.author})"
            if dated:
                label += f", filed {cluster.date_filed}"
            if cluster.follows_judgment:
                label += (
                    f", the earliest opinion after the {judgment} judgment the SCOTUS "
                    + "docket names, which has none of its own on CourtListener"
                )
            elif cluster.after_judgment:
                label += f", after the {judgment} judgment the SCOTUS docket names"
            body = f"=== {label} ===\n{body}"
        parts.append(body)
    text, truncated = _cap("\n\n".join(parts), char_cap)
    newest = max((c.date_filed for c, _ in opinions if c.date_filed), default=judgment)
    return corpus.CaseDocument(
        case_id=match.case_id,
        kind=KIND_DECISION_BELOW,
        url=f"{COURTLISTENER_SITE}/opinion/{opinions[0][0].cluster_id}/",
        entry_date=newest.isoformat(),
        fetched_at=today,
        pages=0,
        truncated=truncated,
        text=text,
    )


def _yes_no(value: bool | None, unknown: str) -> str:
    """A reading's flag as the docket record words it.

    A negative is worded as what it is, an absence among the entries read: it
    is reported only for a complete read — of a petition, one whose entries
    all carry text — and even then says nothing of an entry upstream never
    received.
    """
    return unknown if value is None else ("yes" if value else "none in the entries read")


def _cluster_lines(decided: Sequence[ClusterMatch]) -> list[str]:
    """The docket record's lines for the clusters on or after the judgment date.

    One a cluster, oldest first, then what the judgment date itself holds:
    where it holds none, a line says so, and a second names the opinion read
    as following a judgment entered by order, where one is.
    """
    lines: list[str] = []
    for cluster in reversed(decided):
        ids = ", ".join(str(opinion.opinion_id) for opinion in cluster.opinions)
        later = cluster.after_judgment and not cluster.follows_judgment
        lines.append(
            ("Later opinion cluster" if later else "Opinion cluster")
            + f" {cluster.cluster_id} ({cluster.date_filed}"
            + (", after the judgment date" if cluster.after_judgment else "")
            + f"): {cluster.precedential_status or 'status not served'}; "
            + f"judges: {cluster.judges or 'not recorded'}; "
            + f"opinion id(s): {ids or 'not read'}"
        )
    if not any(cluster.on_judgment_date for cluster in decided):
        lines.append("Opinion on the judgment date: none on CourtListener")
        following = [cluster for cluster in decided if cluster.follows_judgment]
        if following:
            lines.append(
                "  The earliest opinion filed after it is cluster "
                + ", ".join(str(cluster.cluster_id) for cluster in reversed(following))
                + f" ({following[0].date_filed}), read here as the court's opinion on a "
                + "judgment it entered by order: an inference from the dates, to be checked "
                + "against the petition's appendix."
            )
    return lines


def docket_document(match: DecisionBelowMatch, *, today: date) -> corpus.CaseDocument | None:
    """The lower court's docket as a stored ``lower-court-docket`` row.

    A short text record, one fact a line: the court and numbers the SCOTUS
    docket names, the judgment and rehearing dates it serves, the CourtListener
    rows found, the panel where upstream records one, each opinion cluster on
    or after the judgment date with its opinion ids, a line naming the opinion
    read as following a judgment entered by order, and the en banc reading
    with the date its entries run through and the entries it rests on. Where
    the court published an opinion cluster on the day of the disposition and
    no entry names a dissent, the record names the cluster and says a dissent
    is not ruled out. Where
    the entries' text could not carry an answer — an entry described nowhere,
    or a stated rehearing denial no entry records — the record says "could not
    be read" in place of an absence. Stored
    wherever a docket row was found, matched opinion or not. Dated on the
    latest entry the reading read or later opinion cluster it lists, else on
    the judgment date: no fact in it follows the SCOTUS docketing.
    """
    if match.case_id is None or not match.dockets:
        return None
    facts = match.facts
    lines = [
        "Lower-court docket of the decision this petition asks the Court to review, "
        + "read from CourtListener.",
        f"Court: {facts.court_name or 'not named'}"
        + (f" ({facts.court_id})" if facts.court_id else ""),
        f"Case number(s): {', '.join(facts.docket_numbers) or 'not named'}",
        "Judgment below (SCOTUS docket): "
        + (facts.judgment_date.isoformat() if facts.judgment_date else "not served"),
        "Rehearing denied below (SCOTUS docket; panel or en banc not said): "
        + (facts.rehearing_denied.isoformat() if facts.rehearing_denied else "not served"),
    ]
    for row in match.dockets:
        lines.append(
            f"CourtListener docket {row.docket_id}: {row.case_name or 'no caption'}, "
            + f"No. {row.docket_number or 'not served'}; panel: {row.panel or 'not recorded'}"
        )
        if row.lead_by is not None:
            lines.append(
                "  Found by opinion search rather than by case number: a docket the court's "
                + "opinions are filed on for a consolidated appeal, tied to this case because "
                + (
                    "its docket number lists one of the case numbers above."
                    if row.lead_by == "docket_number"
                    else "the caption of its opinion on the judgment date lists one of the "
                    + "case numbers above."
                )
            )
    decided = _decided(match)
    lines.extend(_cluster_lines(decided))
    reading = match.rehearing
    if reading is None or reading.unavailable is not None or reading.entries_read == 0:
        why = reading.unavailable if reading and reading.unavailable else "no entries held"
        lines.append(f"Rehearing en banc: not read ({why})")
    else:
        unknown = (
            "could not be read"
            if reading.blank_entries or reading.denial_unrecorded
            else "not found"
        )
        # A writing published with the order explains an unnamed dissent; a
        # dissent an entry names needs no such note.
        by_id = {c.cluster_id: c for c in decided}
        with_order = (
            [by_id[ident] for ident in reading.disposition_day_clusters if ident in by_id]
            if reading.dissent_noted is None
            else []
        )
        lines.extend(
            [
                "Rehearing en banc, read from the text of "
                + f"{reading.entries_read} docket entr{'y' if reading.entries_read == 1 else 'ies'}"
                + " filed after the judgment and before the SCOTUS docketing"
                + (" (all of them)" if reading.complete else " (not all of them)")
                + (f", the latest filed {reading.through}" if reading.through else "")
                + ":",
                f"  petition filed: {_yes_no(reading.petition_filed, unknown)}",
                f"  disposition: {reading.disposition or unknown}",
                "  dissent noted: "
                + (
                    "not named in the entries read"
                    if with_order
                    else _yes_no(reading.dissent_noted, unknown)
                ),
            ]
        )
        if with_order:
            lines.append(
                "  Published the day rehearing was disposed of: opinion cluster "
                + ", ".join(f"{c.cluster_id} ({c.date_filed})" for c in with_order)
                + ". What the court published that day may be an amended opinion, or its "
                + "order with a dissent, a concurrence or a statement attached. CourtListener's "
                + "record of the cluster does not say which, so no absence of a dissent is "
                + "reported: read the writing itself, in the decision below under the heading "
                + "with its filing date where its text is held, or in the petition's appendix."
            )
        for cite in reading.cites:
            lines.append(
                f"  entry {cite.entry_number if cite.entry_number is not None else '(unnumbered)'}"
                + f" on docket {cite.docket_id}, filed {cite.date_filed or 'undated'}"
            )
        if reading.short_of_denial:
            lines.append(
                "  CourtListener holds no entry as late as the rehearing denial the SCOTUS "
                + f"docket states ({facts.rehearing_denied}), so its entries stop before the "
                + "court ruled on rehearing: what is not shown above was not there to read."
            )
        if reading.denial_unrecorded:
            lines.append(
                "  The SCOTUS docket states rehearing was denied on "
                + f"{facts.rehearing_denied}, and no entry read records a ruling on rehearing "
                + "in its text: CourtListener's entries name these filings too thinly to show "
                + "it, so what is not shown above could not be read, and is not ruled out."
            )
        if reading.blank_entries:
            lines.append(
                f"  {reading.blank_entries} of the entries read "
                + ("carries" if reading.blank_entries == 1 else "carry")
                + " no text on CourtListener, on the entry or on its documents: what is not "
                + "shown above could not be read from them, and is not ruled out."
            )
    cited = [cite.date_filed for cite in (reading.cites if reading else []) if cite.date_filed]
    cited.extend(c.date_filed for c in decided if c.after_judgment and c.date_filed)
    if reading is not None and reading.through is not None:
        cited.append(reading.through)
    dated = max(cited) if cited else facts.judgment_date
    return corpus.CaseDocument(
        case_id=match.case_id,
        kind=KIND_LOWER_COURT_DOCKET,
        url=f"{COURTLISTENER_SITE}/docket/{match.dockets[0].docket_id}/",
        entry_date=dated.isoformat() if dated else None,
        fetched_at=today,
        pages=0,
        truncated=False,
        text="\n".join(lines) + "\n",
    )


def fill_candidates(
    conn: corpus.ReadConnection,
    *,
    today: date,
    max_cases: int,
    priority: frozenset[str] = frozenset(),
    retry_days: int = RETRY_DAYS,
) -> list[corpus.CorpusRow]:
    """The cert-form rows the next fill walks, at most ``max_cases``.

    A SCOTUS row whose lower court is a joined circuit, whose petition was not
    denied and whose case is not decided on the merits: a pending petition, or a
    grant still before the Court, the cells this input reaches. Not attempted
    in the last ``retry_days``. Ordered: cases the ledger forecasts
    (``priority``) and the salience selection first, then never-attempted
    before a stale stamp, then newest by Term and serial. A case whose opinion
    is already stored is walked again once its stamp is stale, behind every
    never-attempted row of its tier: upstream can receive a circuit docket's
    later entries, an amended opinion or an order on rehearing after the first
    walk, so a stored row is a reading as of its stamp, not a settled one. A
    dismissed petition is not told apart from a pending one, and costs its
    walk once a cycle.
    """
    picked: list[tuple[tuple[int, int, date, int, int], corpus.CorpusRow]] = []
    for row in corpus.iter_rows(conn, court="scotus"):
        serial = parse_scotus_docket_number(corpus.strip_docket_annotation(row.docket_number))
        if serial is None or row.date_cert_denied is not None or row.merits_decided is not None:
            continue
        if not joins_lower_court(row):
            continue
        attempted = row.decision_below_attempted_at
        if attempted is not None and (today - attempted).days < retry_days:
            continue
        first = 0 if row.case_id in priority or row.salience_selected else 1
        key = (
            first,
            0 if attempted is None else 1,
            attempted or date.min,
            -serial[0],
            -serial[1],
        )
        picked.append((key, row))
    picked.sort(key=lambda pair: pair[0])
    return [row for _, row in picked[: max(max_cases, 0)]]


def fill_decision_below(
    conn: sqlite3.Connection,
    client: CourtListenerClient,
    rows: Sequence[corpus.CorpusRow],
    *,
    apply: bool,
    today: date,
    char_cap: int,
) -> DecisionBelowReport:
    """Match each row and store what upstream holds of its decision below.

    Each case CourtListener answered about gets its ``decision-below`` row
    where an opinion on or after the judgment date carries text, its
    ``lower-court-docket`` row where a docket was found, and its
    ``decision_below_attempted_at`` stamp, all only under ``apply``; a dry run
    counts what it would store. A failed case is stamped neither way, and a
    batch wall defers the rest unstamped. A case is stamped even where its
    rehearing entries could not be read: its docket row says so, and the next
    walk reads them again. A walk whose entries request faulted does not
    replace a docket row the case already holds, which may carry a reading
    where this one carries none. Under the corpus split a store write that
    fails is logged rather than raised, so such a case is stamped too and waits
    out its retry window.
    """
    report_stored: dict[str, int] = {}

    def store(item: CaseInput, match: DecisionBelowMatch, walk: _Walk) -> None:
        docket = docket_document(match, today=today)
        if (
            docket is not None
            and match.rehearing is not None
            and match.rehearing.faulted
            and KIND_LOWER_COURT_DOCKET in corpus.document_urls_for_case(conn, docket.case_id)
        ):
            docket = None
        documents = [
            document
            for document in (
                opinion_document(match, walk.texts, today=today, char_cap=char_cap),
                docket,
            )
            if document is not None
        ]
        for document in documents:
            report_stored[document.kind] = report_stored.get(document.kind, 0) + 1
        if not apply or item.case_id is None:
            return
        if documents:
            corpus.upsert_documents(conn, documents)
        corpus.stamp_decision_below_attempt(conn, item.case_id, today)

    cases = [
        CaseInput(label=row.case_id, case_id=row.case_id, facts=facts_for_row(conn, row))
        for row in rows
    ]
    report = _walk_cases(client, cases, store)
    report.stored = dict(sorted(report_stored.items()))
    return report
