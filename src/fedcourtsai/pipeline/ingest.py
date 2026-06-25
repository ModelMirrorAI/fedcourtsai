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
    citations: list[str] = Field(default_factory=list)
    summary: str | None = Field(default=None, description="Opinion text or summary")
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


def _date(value: Any) -> date | None:
    text = _clean(value)
    if text is None:
        return None
    return date_parser.parse(text).date()


def _str_list(value: Any) -> list[str]:
    """Coerce a list, a delimited string, or a scalar to a list of strings."""
    items: list[Any]
    if value is None:
        items = []
    elif isinstance(value, str):
        items = value.replace("|", ";").split(";")
    elif isinstance(value, Mapping):
        items = [value]
    elif isinstance(value, Iterable):
        items = list(value)
    else:
        items = [value]

    out: list[str] = []
    for item in items:
        name = item.get("name_full") or item.get("name") if isinstance(item, Mapping) else item
        cleaned = _clean(name)
        if cleaned is not None and cleaned not in out:
            out.append(cleaned)
    return out


def _judges(record: Mapping[str, Any]) -> list[str]:
    """Panel members and/or the assigned judge, deduplicated and sorted."""
    found: list[str] = []
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
        judges=_judges(record),
        citations=_str_list(record.get("citations")),
        summary=_clean(record.get("summary") or record.get("opinion_text")),
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
        date_filed=row.date_filed,
        date_decided=row.date_decided,
        disposition=row.disposition,
        judges=row.judges,
        topic=row.nature_of_suit,
        citations=row.citations,
        summary=row.summary,
        last_pulled=last_pulled,
    )


def upsert_to_corpus(
    db_path: Path, rows: Iterable[CorpusRow], *, last_pulled: date | None = None
) -> int:
    """Upsert normalized rows into the packed SQLite corpus at ``db_path``.

    Idempotent by ``case_id`` (last write wins), so re-ingesting a docket — by
    ``seed`` or ``pull`` — overwrites its row rather than duplicating it. When
    ``pull`` passes ``last_pulled`` it stamps the refresh date onto every row in
    this batch, advancing the governor's rotation key.
    """
    store_rows = [to_corpus_row(row, last_pulled=last_pulled) for row in merge_rows(rows)]
    with corpus.connect(db_path) as conn:
        return corpus.upsert_rows(conn, store_rows)
