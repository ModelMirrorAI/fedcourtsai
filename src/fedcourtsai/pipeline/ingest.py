"""Shared ingestion core: one normalized corpus row from either source.

``seed`` reads CourtListener **bulk data** (S3 CSV) and ``pull`` reads the
**REST API**; both hand their source records to this module so the packed
corpus has a single shape, schema, and set of APIs regardless of origin. The
two phases differ on *source* and *budget*, never on how a fact is shaped or
stored (see ``docs/data-pipeline.md``).

- :func:`from_api_docket` maps an API docket JSON object to a :class:`CorpusRow`.
- :func:`from_bulk_row` maps a bulk CSV row (already parsed to a dict) to the
  same :class:`CorpusRow`.

Both delegate to one private normalizer, so equivalent inputs from the two
sources produce byte-identical rows apart from the recorded :attr:`CorpusRow.source`.

Normalized rows are persisted into the single packed corpus — the SQLite store
defined in :mod:`fedcourtsai.corpus` — via :func:`upsert_to_corpus`, so ``seed``
and ``pull`` both land facts in one place through one seam.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

from dateutil import parser as date_parser
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..schemas import Disposition, EventKind

CORPUS_SCHEMA_VERSION: Final = "1.0"


class CorpusSource(StrEnum):
    """Which pipeline phase / upstream source produced a corpus row."""

    api = "api"
    bulk = "bulk"


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
    disposition: Disposition | None = Field(
        default=None, description="Realized outcome label (the back-testing target)"
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
    so a bulk (seed) row leaves this blank — only the originating *court* is
    recoverable there — and the precise lower-court latch is REST (pull) driven.
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
    return CorpusRow(
        case_id=ids.case_id(court, docket_id),
        court=court,
        docket_id=docket_id,
        docket_number=_clean(record.get("docket_number")) or "",
        case_name=_clean(record.get("case_name") or record.get("case_name_full")) or "",
        date_filed=_date(record.get("date_filed")),
        date_decided=_date(record.get("date_terminated") or record.get("date_decided")),
        disposition=_disposition(record),
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
    """Normalize a CourtListener bulk-data CSV row (the ``seed`` path).

    ``row`` is a single CSV record already parsed to a mapping (e.g. via
    :class:`csv.DictReader`); blank cells are treated as missing.
    """
    return _normalize(row, CorpusSource.bulk)


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
    """Whether a freshly-ingested case enters the prediction-scope gate.

    The *rule* behind the latching ``predict_eligible`` flag: a case is in-scope
    for the agentic predict/evaluate stages once it has interacted with the
    Supreme Court (``docs/data-pipeline.md``). A SCOTUS docket
    (``court == "scotus"``) is in-scope — its whole lifecycle is at SCOTUS, so this
    satisfies "stays in-scope for its lifecycle". Set identically on both ingestion
    paths (seed and pull) because both project through :func:`to_corpus_row`.

    The *other* half of the rule — pulling the same case's originating
    court-of-appeals docket into scope — is not decidable from a single row (it
    needs the lower-court link resolved against the *other* docket's corpus row),
    so it lives in :func:`fedcourtsai.corpus.latch_originating_eligible`, invoked
    after the upsert. Because the flag is persisted and latching, that is a purely
    additive change — never a filter change.
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


def to_corpus_row(row: CorpusRow, *, last_pulled: date | None = None) -> corpus.CorpusRow:
    """Project a normalized ingestion row onto the packed-corpus storage row.

    The ingestion model carries provenance the storage model does not need
    (``source``, ``schema_version``, ``docket_id`` — recoverable from
    ``case_id``); ``nature_of_suit`` maps onto the store's ``topic`` column.

    ``last_pulled`` is pull-time tracking state (not a docket fact), so it is
    supplied by the caller: ``pull`` stamps the refresh date, while bulk seed
    leaves it ``None`` (the upsert preserves any timestamp a prior pull set).
    """
    return corpus.CorpusRow(
        case_id=row.case_id,
        court=row.court,
        docket_number=row.docket_number,
        case_name=row.case_name,
        date_filed=row.date_filed,
        date_decided=row.date_decided,
        disposition=row.disposition,
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
        predict_eligible=is_predict_eligible(row),
        originating_court=row.originating_court,
        originating_docket_number=row.originating_docket_number,
    )


def upsert_to_corpus(
    db_path: Path, rows: Iterable[CorpusRow], *, last_pulled: date | None = None
) -> int:
    """Upsert normalized rows into the packed SQLite corpus at ``db_path``.

    Idempotent by ``case_id`` (last write wins), so re-ingesting a docket — by
    ``seed`` or ``pull`` — overwrites its row rather than duplicating it. When
    ``pull`` passes ``last_pulled`` it stamps the refresh date onto every row in
    this batch, advancing the governor's rotation key.

    After the upsert, any SCOTUS row in the batch carrying a lower-court link
    latches its originating tracked court-of-appeals docket eligible (the second
    half of the prediction-scope rule); an unlinked or untracked one is a no-op.
    """
    store_rows = [to_corpus_row(row, last_pulled=last_pulled) for row in merge_rows(rows)]
    with corpus.connect(db_path) as conn:
        written = corpus.upsert_rows(conn, store_rows)
        corpus.latch_originating_eligible(conn, store_rows)
        return written
