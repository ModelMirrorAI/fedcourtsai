"""Shared ingestion core: one normalized corpus row from either source shape.

``pull`` reads the CourtListener **REST API**; a bulk-shaped source (a CSV
export, or a future replication feed) hands flat rows. Both hand their source
records to this module so the packed corpus has a single shape, schema, and
set of APIs regardless of origin. Channels differ on *source* and *budget*,
never on how a fact is shaped or stored (see ``docs/data-pipeline.md``).

- :func:`from_api_docket` maps an API docket JSON object to a :class:`CorpusRow`.
- :func:`from_bulk_row` maps a bulk row (already parsed to a dict) to the
  same :class:`CorpusRow`.

Both delegate to one private normalizer, so equivalent inputs from the two
sources produce byte-identical rows apart from the recorded :attr:`CorpusRow.source`.

Normalized rows are persisted into the single packed corpus — the SQLite store
defined in :mod:`fedcourtsai.corpus` — via :func:`upsert_to_corpus`, so every
channel lands facts in one place through one seam.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

from dateutil import parser as date_parser
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..schemas import Disposition, EventKind
from .cert_signals import match_disposition_signal

CORPUS_SCHEMA_VERSION: Final = "1.0"


class CorpusSource(StrEnum):
    """Which pipeline phase / upstream source produced a corpus row."""

    api = "api"
    bulk = "bulk"
    live = "live"


class CorpusRow(BaseModel):
    """One normalized, labeled raw-fact record in the packed corpus.

    Governed by its own schema (distinct from the git-ledger models in
    ``fedcourtsai.schemas``): each row carries the realized ``disposition`` so
    the corpus doubles as a back-testing set, and structured columns so it is
    queryable for retrieval.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    schema_version: Literal["1.0"] = CORPUS_SCHEMA_VERSION
    case_id: str
    court: str
    docket_id: int
    docket_number: str = ""
    case_name: str = ""
    date_filed: date | None = None
    date_decided: date | None = None
    date_cert_granted: date | None = Field(
        default=None, description="Petition-stage date certiorari was granted (SCOTUS)"
    )
    date_cert_denied: date | None = Field(
        default=None, description="Petition-stage date certiorari was denied (SCOTUS)"
    )
    disposition: Disposition | None = Field(
        default=None, description="Realized outcome label (the back-testing target)"
    )
    distributed_for_conference: date | None = Field(
        default=None,
        description="The SCOTUS conference this petition is currently distributed for "
        "(the latest 'DISTRIBUTED for Conference of …' proceedings entry; a "
        "re-distribution updates it). Live-channel only; None elsewhere.",
    )
    nature_of_suit: str | None = Field(default=None, description="Nature/topic of the matter")
    judges: list[str] = Field(default_factory=list)
    panel: list[corpus.PanelMember] = Field(
        default_factory=list, description="Structured panel (name + seniority) behind `judges`"
    )
    parties: list[str] = Field(default_factory=list, description="Party names on the docket")
    attorneys: list[str] = Field(default_factory=list, description="Attorney names of record")
    citations: list[str] = Field(default_factory=list)
    citation_count: int | None = Field(default=None, description="Times the decision was cited")
    precedential_status: str | None = Field(
        default=None, description="Published / Unpublished / Errata"
    )
    summary: str | None = Field(default=None, description="Opinion text or summary")
    originating_court: str | None = Field(
        default=None, description="Lower court this docket came from (`appeal_from`)"
    )
    originating_docket_number: str | None = Field(
        default=None, description="Docket number in the originating court (REST-only)"
    )
    source: CorpusSource


# --- field extraction (tolerant of both API objects and bulk CSV rows) ---------


def _clean(value: Any) -> str | None:
    """Trim a scalar to a non-empty string, or ``None`` for blanks/nulls."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _court_id(record: Mapping[str, Any]) -> str:
    """Resolve the CourtListener court id.

    Bulk rows carry ``court_id`` directly; API dockets carry a ``court``
    hyperlink (``.../courts/ca9/``) whose final path segment is the id.
    """
    raw = _clean(record.get("court_id"))
    if raw is None:
        court = _clean(record.get("court"))
        if court is not None:
            raw = court.rstrip("/").rsplit("/", 1)[-1]
    if raw is None:
        raise ValueError("record has neither 'court_id' nor a 'court' url")
    return ids.slugify(raw)


def _originating_court(record: Mapping[str, Any]) -> str | None:
    """The originating (lower) court id for an appellate / SCOTUS docket, or ``None``.

    Bulk rows carry ``appeal_from_id`` (the ``Court`` primary key, e.g. ``ca9``)
    directly; REST dockets carry an ``appeal_from`` hyperlink
    (``.../courts/ca9/``) whose final path segment is the id. The free-text
    ``appeal_from_str`` is not a reliable join key, so it is intentionally unused.
    """
    raw = _clean(record.get("appeal_from_id"))
    if raw is None:
        url = _clean(record.get("appeal_from"))
        if url is not None:
            raw = url.rstrip("/").rsplit("/", 1)[-1]
    return ids.slugify(raw) if raw is not None else None


def _originating_docket_number(record: Mapping[str, Any]) -> str | None:
    """The docket number in the originating court for an appellate / SCOTUS docket.

    The REST docket nests it under ``originating_court_information.docket_number``.
    CourtListener does not export the originating-court-information table in bulk,
    so a bulk-shaped row leaves this blank — only the originating *court* is
    recoverable there — and the precise lower-court link is REST (pull) driven.
    """
    info = record.get("originating_court_information")
    if isinstance(info, Mapping):
        return _clean(info.get("docket_number"))
    return None


def _date(value: Any) -> date | None:
    text = _clean(value)
    if text is None:
        return None
    return date_parser.parse(text).date()


def _as_count(value: Any) -> int | None:
    """Parse a non-negative integer count, or ``None`` for blanks/non-numeric."""
    text = _clean(value)
    if text is None:
        return None
    try:
        count = int(text)
    except ValueError:
        return None
    return count if count >= 0 else None


def _maybe_json_array(text: str) -> list[Any] | None:
    """Parse a string that is a JSON array, else ``None``.

    The staged join serves a multi-valued sibling (parties, attorneys, the
    resolved panel) as a JSON array string; a plain free-text cell is left for
    the delimiter split. Only strings that open with ``[`` are even tried, so a
    normal ``"Smith; Lee"`` never round-trips through the JSON parser.
    """
    stripped = text.strip()
    if not stripped.startswith("["):
        return None
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, list) else None


def _items(value: Any) -> list[Any]:
    """Normalize a list / JSON-array string / delimited string / scalar to items."""
    if value is None:
        return []
    if isinstance(value, str):
        parsed = _maybe_json_array(value)
        return parsed if parsed is not None else value.replace("|", ";").split(";")
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Iterable):
        return list(value)
    return [value]


def _str_list(value: Any) -> list[str]:
    """Coerce a list, a JSON array, a delimited string, or a scalar to strings."""
    out: list[str] = []
    for item in _items(value):
        name = item.get("name_full") or item.get("name") if isinstance(item, Mapping) else item
        cleaned = _clean(name)
        if cleaned is not None and cleaned not in out:
            out.append(cleaned)
    return out


def _panel(record: Mapping[str, Any]) -> list[corpus.PanelMember]:
    """Structured panel members (name + seniority), deduplicated by name.

    Reads the sibling people-db join the staged source resolves onto each cluster
    (a JSON array of ``{name, seniority}``), and is equally tolerant of an API
    docket's list of judge objects. The flat :func:`_judges` names are derived
    from this plus the free-text judge fields, so retrieval still sees every name.
    """
    members: list[corpus.PanelMember] = []
    seen: set[str] = set()
    for item in _items(record.get("panel")):
        if isinstance(item, Mapping):
            name = _clean(item.get("name_full") or item.get("name"))
            seniority = _clean(item.get("seniority"))
        else:
            name = _clean(item)
            seniority = None
        if name is None or name in seen:
            continue
        seen.add(name)
        members.append(corpus.PanelMember(name=name, seniority=seniority))
    return members


def _judges(record: Mapping[str, Any], *, extra: Iterable[str] = ()) -> list[str]:
    """Panel members and/or the assigned judge, deduplicated and sorted.

    ``extra`` carries the resolved-panel names so the flat retrieval key includes
    every judge even when the free-text ``judges`` cell is blank.
    """
    found: list[str] = []
    for name in extra:
        if name not in found:
            found.append(name)
    for key in ("panel", "judges", "assigned_to_str", "assigned_to"):
        for name in _str_list(record.get(key)):
            if name not in found:
                found.append(name)
    return sorted(found)


def _disposition(record: Mapping[str, Any]) -> Disposition | None:
    for key in ("disposition", "outcome", "nature_of_judgement"):
        label = normalize_disposition(record.get(key))
        if label is not None:
            return label
    return None


def _cert_date_disposition(granted: date | None, denied: date | None) -> Disposition | None:
    """The disposition a SCOTUS docket's cert-stage dates imply, or ``None``.

    Upstream records the petition-stage decision as a date rather than a
    disposition string, so for a cert petition the date *is* the label. A grant
    date wins when both are present: a granted-then-disposed petition (including
    a grant-vacate-remand) was granted at the petition stage.
    """
    if granted is not None:
        return Disposition.granted
    if denied is not None:
        return Disposition.denied
    return None


def normalize_disposition(raw: Any) -> Disposition | None:
    """Map a free-text disposition to the shared :class:`Disposition` label.

    Returns ``None`` for blanks/nulls so an unlabeled docket stays unlabeled
    rather than being forced to ``other``.
    """
    text = _clean(raw)
    if text is None:
        return None
    lowered = text.lower()
    if "grant" in lowered:
        return Disposition.granted_in_part if "part" in lowered else Disposition.granted
    keywords: tuple[tuple[str, Disposition], ...] = (
        ("den", Disposition.denied),
        ("dismiss", Disposition.dismissed),
        ("withdraw", Disposition.withdrawn),
    )
    for needle, label in keywords:
        if needle in lowered:
            return label
    return Disposition.other


def _normalize(record: Mapping[str, Any], source: CorpusSource) -> CorpusRow:
    court = _court_id(record)
    docket_id = int(record["id"])
    panel = _panel(record)
    date_cert_granted = _date(record.get("date_cert_granted"))
    date_cert_denied = _date(record.get("date_cert_denied"))
    # A textual disposition always wins; the cert-stage dates only fill the gap
    # on SCOTUS dockets, where upstream records the petition decision as a date.
    disposition = _disposition(record)
    if disposition is None and court == "scotus":
        disposition = _cert_date_disposition(date_cert_granted, date_cert_denied)
    return CorpusRow(
        case_id=ids.case_id(court, docket_id),
        court=court,
        docket_id=docket_id,
        docket_number=_clean(record.get("docket_number")) or "",
        case_name=_clean(record.get("case_name") or record.get("case_name_full")) or "",
        date_filed=_date(record.get("date_filed")),
        date_decided=_date(record.get("date_terminated") or record.get("date_decided")),
        date_cert_granted=date_cert_granted,
        date_cert_denied=date_cert_denied,
        disposition=disposition,
        distributed_for_conference=_date(record.get("distributed_for_conference")),
        nature_of_suit=_clean(record.get("nature_of_suit")),
        judges=_judges(record, extra=[m.name for m in panel]),
        panel=panel,
        parties=sorted(_str_list(record.get("parties"))),
        attorneys=sorted(_str_list(record.get("attorneys"))),
        citations=_str_list(record.get("citations")),
        citation_count=_as_count(record.get("citation_count")),
        precedential_status=_clean(record.get("precedential_status")),
        summary=_clean(record.get("summary") or record.get("opinion_text")),
        originating_court=_originating_court(record),
        originating_docket_number=_originating_docket_number(record),
        source=source,
    )


def from_api_docket(docket: Mapping[str, Any]) -> CorpusRow:
    """Normalize a CourtListener REST API docket object (the ``pull`` path)."""
    return _normalize(docket, CorpusSource.api)


def from_bulk_row(row: Mapping[str, Any]) -> CorpusRow:
    """Normalize a CourtListener bulk-data row (a flat CSV/replication record).

    ``row`` is a single record already parsed to a mapping (e.g. via
    :class:`csv.DictReader`); blank cells are treated as missing.
    """
    return _normalize(row, CorpusSource.bulk)


# --- the SCOTUS live channel (supremecourt.gov docket JSON) ---------------

# The lower-court names the docket JSON's `LowerCourt` uses for the tracked
# federal courts of appeals, mapped to CourtListener court ids so the live
# channel populates the same originating linkage the REST path does. A state
# court, a district court, or an unlisted tribunal maps to None — the raw name
# stays on the snapshot; only the tracked-court *linkage* needs the id.
_LIVE_LOWER_COURT_IDS: Final[dict[str, str]] = {
    "united states court of appeals for the first circuit": "ca1",
    "united states court of appeals for the second circuit": "ca2",
    "united states court of appeals for the third circuit": "ca3",
    "united states court of appeals for the fourth circuit": "ca4",
    "united states court of appeals for the fifth circuit": "ca5",
    "united states court of appeals for the sixth circuit": "ca6",
    "united states court of appeals for the seventh circuit": "ca7",
    "united states court of appeals for the eighth circuit": "ca8",
    "united states court of appeals for the ninth circuit": "ca9",
    "united states court of appeals for the tenth circuit": "ca10",
    "united states court of appeals for the eleventh circuit": "ca11",
    "united states court of appeals for the district of columbia circuit": "cadc",
    "united states court of appeals for the federal circuit": "cafc",
}

# Trailing role labels on the JSON's party titles ("Acme Corp., Petitioner",
# "..., et al., Petitioners"), stripped so the caption reads `X v. Y`.
_LIVE_TITLE_ROLE_RE = re.compile(r",\s*(?:petitioner|respondent|applicant|appellant)s?\s*$", re.I)

# Conference membership rides in the proceedings as its own entry —
# "DISTRIBUTED for Conference of 3/24/2023." — one entry per (re)distribution.
# Anchored on the full phrase so a filing's "(Distributed)" suffix never matches.
_LIVE_DISTRIBUTED_RE = re.compile(r"DISTRIBUTED\s+for\s+Conference\s+of\s+([\d/A-Za-z, ]+)", re.I)


def _live_conference_date(entries: list[dict[str, Any]]) -> date | None:
    """The conference this petition is currently distributed for, or ``None``.

    The **last** distribution entry in docket order wins: a relisted or
    re-scheduled petition gets a fresh "DISTRIBUTED for Conference of …" entry
    per conference, and the latest one is its current membership. An
    unparseable date degrades to the previous match, never a crash.
    """
    conference: date | None = None
    for entry in entries:
        match = _LIVE_DISTRIBUTED_RE.search(str(entry.get("description") or ""))
        if match is None:
            continue
        try:
            parsed = _date(match.group(1).strip(" ."))
        except (ValueError, OverflowError):
            continue
        if parsed is not None:
            conference = parsed
    return conference


def _live_title(raw: Any) -> str | None:
    text = _clean(raw)
    return _LIVE_TITLE_ROLE_RE.sub("", text) if text else None


def _live_counsel(payload: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """(parties, attorneys) from the JSON's counsel blocks, order-preserving."""
    parties: list[str] = []
    attorneys: list[str] = []
    for side in ("Petitioner", "Respondent", "Other"):
        blocks = payload.get(side)
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, Mapping):
                continue
            party = _clean(block.get("PartyName"))
            attorney = _clean(block.get("Attorney"))
            if party is not None and party not in parties:
                parties.append(party)
            if attorney is not None and attorney not in attorneys:
                attorneys.append(attorney)
    return parties, attorneys


def _live_entries(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The proceedings list as CourtListener-shaped docket entries.

    Synthetic 1-based ids/numbers: the proceedings list is append-only, so the
    index is stable across polls and downstream event definitions pinned to it
    stay coherent. Dates are re-serialized to ISO (the entry classifier parses
    ``date.fromisoformat``); an unparseable date degrades to ``None``, never a
    crash.
    """
    entries: list[dict[str, Any]] = []
    for index, entry in enumerate(payload.get("ProceedingsandOrder") or [], start=1):
        if not isinstance(entry, Mapping):
            continue
        entry_date: date | None
        try:
            entry_date = _date(entry.get("Date"))
        except (ValueError, OverflowError):
            entry_date = None
        entries.append(
            {
                "id": index,
                "entry_number": index,
                "date_filed": entry_date.isoformat() if entry_date else None,
                "description": _clean(entry.get("Text")) or "",
            }
        )
    return entries


def _live_resolution(
    entries: list[dict[str, Any]],
) -> tuple[str | None, date | None, date | None, date | None]:
    """(disposition, cert_granted, cert_denied, terminated) from the proceedings.

    The disposition orders ride as plain proceedings text ("Petition DENIED."),
    which the shared cert-order patterns match — 64/64 on the reachability-probe
    sample (docs/live-sources-probe.md). The first matching entry, in docket
    order, is the cert-stage disposition and its entry date is the decision
    date: a grant dates ``date_cert_granted``, a denial ``date_cert_denied``,
    and anything else (dismissed / withdrawn) dates the termination.
    """
    for entry in entries:
        matched = match_disposition_signal(str(entry.get("description") or ""))
        if matched is None:
            continue
        disposition = matched[0].value
        decided = date.fromisoformat(entry["date_filed"]) if entry.get("date_filed") else None
        if disposition == Disposition.granted.value:
            return disposition, decided, None, None
        if disposition == Disposition.denied.value:
            return disposition, None, decided, None
        return disposition, None, None, decided
    return None, None, None, None


def map_live_docket(payload: Mapping[str, Any], docket_id: int) -> dict[str, Any]:
    """A supremecourt.gov docket JSON as an upstream-shaped ingestion record.

    The live channel's half of the guardrail "new upstream fields land as
    columns mapped in the shared normalization layer": this produces a record
    the shared :func:`_normalize` (and the entry classifier) consumes exactly
    like a REST docket, so nothing downstream keys on the channel. ``docket_id``
    is supplied by the caller, which resolved identity first — the matched
    existing row's id, or the reserved-range live id for a genuinely unseen
    petition (``fedcourtsai.supremecourt.live_docket_id``).
    """
    entries = _live_entries(payload)
    conference = _live_conference_date(entries)
    disposition, cert_granted, cert_denied, terminated = _live_resolution(entries)
    petitioner = _live_title(payload.get("PetitionerTitle"))
    respondent = _live_title(payload.get("RespondentTitle"))
    case_name = f"{petitioner} v. {respondent}" if petitioner and respondent else petitioner
    parties, attorneys = _live_counsel(payload)
    lower_court = _clean(payload.get("LowerCourt"))
    lower_numbers = _clean(payload.get("LowerCourtCaseNumbers"))
    return {
        "id": docket_id,
        "court_id": "scotus",
        "docket_number": _clean(payload.get("CaseNumber")) or "",
        "case_name": case_name,
        "date_filed": _clean(payload.get("DocketedDate")),
        "date_cert_granted": cert_granted.isoformat() if cert_granted else None,
        "date_cert_denied": cert_denied.isoformat() if cert_denied else None,
        "date_terminated": terminated.isoformat() if terminated else None,
        "distributed_for_conference": conference.isoformat() if conference else None,
        "disposition": disposition,
        "parties": parties,
        "attorneys": attorneys,
        "appeal_from_id": _LIVE_LOWER_COURT_IDS.get(lower_court.lower()) if lower_court else None,
        "originating_court_information": (
            # The JSON parenthesizes the lower-court numbers ("(21-5166)").
            {"docket_number": lower_numbers.strip("()")} if lower_numbers else None
        ),
        "docket_entries": entries,
    }


def from_live_record(record: Mapping[str, Any]) -> CorpusRow:
    """Normalize an already-mapped live record (the entry classifier's seam)."""
    return _normalize(record, CorpusSource.live)


def from_live_docket(payload: Mapping[str, Any], docket_id: int) -> CorpusRow:
    """Normalize a raw supremecourt.gov docket JSON (the live-poll path)."""
    return from_live_record(map_live_docket(payload, docket_id))


# --- predictable event derivation ---------------------------------------------


def default_event(row: CorpusRow) -> corpus.CorpusEvent:
    """Derive the default predictable event for a freshly-onboarded docket.

    Every tracked appellate matter has at least one thing to predict — the
    disposition of the appeal (or, at SCOTUS, the petition). Discovery records
    this as a raw fact in the corpus, replacing the per-case ``event.yaml`` the
    retired active tier used. Deterministic so a re-discovery reproduces the same
    ``event_id``; richer, agent-defined events can be layered on top later.
    """
    kind = EventKind.petition if row.court == "scotus" else EventKind.appeal
    return corpus.CorpusEvent(
        event_id=ids.event_id(kind.value, "disposition"),
        case_id=row.case_id,
        court=row.court,
        kind=kind,
        title=row.case_name or row.docket_number or row.case_id,
        decision_target="disposition",
        opened_at=row.date_filed,
        resolved=row.disposition is not None,
    )


# --- prediction-scope rule -----------------------------------------------------


def is_predict_eligible(row: CorpusRow) -> bool:
    """Whether a freshly-ingested case is in the prediction scope.

    The rule behind the derived ``predict_eligible`` convenience column, and
    exactly the scope predicate: only a SCOTUS docket (``court == "scotus"``)
    is in-scope for the agentic predict/evaluate stages
    (``docs/data-pipeline.md``). Set identically on every ingestion path
    because all project through :func:`to_corpus_row`. Every scope seam reads
    the court predicate directly — the column is a queryable mirror, never the
    source of truth.
    """
    return row.court == "scotus"


# --- persistence (one packed corpus, deterministic writes) ---------------------


def merge_rows(rows: Iterable[CorpusRow]) -> list[CorpusRow]:
    """Collapse rows to one per ``case_id``, last occurrence winning.

    Lets a phase fold fresh facts over a prior corpus (``existing`` then
    ``fresh``) without proliferating duplicate rows for the same case.
    """
    by_case: dict[str, CorpusRow] = {}
    for row in rows:
        by_case[row.case_id] = row
    return list(by_case.values())


def to_corpus_row(
    row: CorpusRow, *, last_pulled: date | None = None, last_live_polled: date | None = None
) -> corpus.CorpusRow:
    """Project a normalized ingestion row onto the packed-corpus storage row.

    The ingestion model carries provenance the storage model does not need
    (``source``, ``schema_version``, ``docket_id`` — recoverable from
    ``case_id``); ``nature_of_suit`` maps onto the store's ``topic`` column.

    ``last_pulled`` and ``last_live_polled`` are channel tracking state (not
    docket facts), so they are supplied by the caller: ``pull`` stamps the REST
    refresh date, the live poller stamps its own, and every other writer leaves
    both ``None`` (the upsert preserves any timestamp a prior stamp set).
    """
    return corpus.CorpusRow(
        case_id=row.case_id,
        court=row.court,
        docket_number=row.docket_number,
        case_name=row.case_name,
        date_filed=row.date_filed,
        date_decided=row.date_decided,
        date_cert_granted=row.date_cert_granted,
        date_cert_denied=row.date_cert_denied,
        disposition=row.disposition,
        distributed_for_conference=row.distributed_for_conference,
        judges=row.judges,
        panel=row.panel,
        parties=row.parties,
        attorneys=row.attorneys,
        topic=row.nature_of_suit,
        citations=row.citations,
        citation_count=row.citation_count,
        precedential_status=row.precedential_status,
        summary=row.summary,
        last_pulled=last_pulled,
        last_live_polled=last_live_polled,
        predict_eligible=is_predict_eligible(row),
        originating_court=row.originating_court,
        originating_docket_number=row.originating_docket_number,
    )


def upsert_to_corpus(
    db_path: Path,
    rows: Iterable[CorpusRow],
    *,
    last_pulled: date | None = None,
    last_live_polled: date | None = None,
) -> int:
    """Upsert normalized rows into the packed SQLite corpus at ``db_path``.

    Idempotent by ``case_id`` (last write wins), so re-ingesting a docket — by
    ``pull``, the live poller, or the historical walker — overwrites its row
    rather than duplicating it. ``last_pulled`` / ``last_live_polled`` stamp the writing
    channel's refresh date onto every row in the batch, advancing that channel's
    rotation key (each preserves the other channel's prior stamp).
    """
    store_rows = [
        to_corpus_row(row, last_pulled=last_pulled, last_live_polled=last_live_polled)
        for row in merge_rows(rows)
    ]
    with corpus.connect(db_path) as conn:
        return corpus.upsert_rows(conn, store_rows)
