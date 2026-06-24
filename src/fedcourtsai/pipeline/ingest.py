"""Shared ingestion core: normalize either source into one shape.

Two very different sources feed the pipeline (see ``docs/data-pipeline.md``):

* the **CourtListener REST API** — a rich docket JSON, used by seed/pull today to
  keep the *active* tier (``data/cases/``) current within the API budget, and
* **CourtListener bulk data** — a flat CSV row, used by the historical backfill
  to build the packed *historical* corpus (DVC-versioned).

This module is the single normalization layer both go through so the API path
and the bulk path produce identical artifacts. Each source first becomes a
:class:`NormalizedDocket` (the common intermediate); that intermediate then
projects to either the active-tier :class:`~fedcourtsai.schemas.TrackedCase` /
``docket.json`` or the historical-tier
:class:`~fedcourtsai.schemas.CorpusRow`. Writers reuse
:mod:`fedcourtsai.serialize` (sorted, newline-terminated) and
:mod:`fedcourtsai.store` so diffs stay minimal and discovery stays deduplicated.

**Unify the library, not the job** — seed and pull stay separate workflows but
share this core.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from .. import ids
from ..paths import CasePaths
from ..schemas import CaseStatus, CorpusRow, Disposition, TrackedCase
from ..serialize import write_raw_json, write_yaml
from ..store import iter_tracked_cases

JsonDict = dict[str, Any]
BulkRow = Mapping[str, str]


# --- field parsing -----------------------------------------------------------


def _clean(value: object) -> str | None:
    """Collapse empty/whitespace-only cells (common in bulk CSV) to ``None``."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_date(value: object) -> date | None:
    """Parse an ISO date, tolerating a trailing time component (``YYYY-MM-DD…``)."""
    text = _clean(value)
    if text is None:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _split_list(value: object, *, separators: str = ";|") -> tuple[str, ...]:
    """Split a delimited bulk cell (``"a; b | c"``) into a clean, ordered tuple."""
    text = _clean(value)
    if text is None:
        return ()
    parts = [text]
    for sep in separators:
        parts = [piece for chunk in parts for piece in chunk.split(sep)]
    return tuple(p.strip() for p in parts if p.strip())


def parse_disposition(value: object) -> Disposition | None:
    """Map free-text disposition language to the :class:`Disposition` enum.

    Bulk and API sources phrase outcomes inconsistently ("Motion Granted",
    "DENIED", "granted in part"); this normalizes them. Unknown but non-empty
    text becomes :attr:`Disposition.other`; empty stays ``None`` (unresolved).
    """
    text = _clean(value)
    if text is None:
        return None
    lowered = text.lower()
    if "grant" in lowered:
        return Disposition.granted_in_part if "part" in lowered else Disposition.granted
    for needle, disposition in (
        ("den", Disposition.denied),
        ("dismiss", Disposition.dismissed),
        ("withdraw", Disposition.withdrawn),
    ):
        if needle in lowered:
            return disposition
    return Disposition.other


def _court_id_from_api(payload: Mapping[str, Any]) -> str | None:
    """Resolve a court id from an API docket, preferring the explicit field.

    The ``court`` field is a hyperlinked resource URL such as
    ``.../api/rest/v4/courts/ca9/``; fall back to its last path segment.
    """
    explicit = _clean(payload.get("court_id"))
    if explicit is not None:
        return explicit
    court_url = _clean(payload.get("court"))
    if court_url is None:
        return None
    return court_url.rstrip("/").rsplit("/", 1)[-1] or None


# --- normalized intermediate -------------------------------------------------


@dataclass(frozen=True, slots=True)
class NormalizedDocket:
    """Source-independent docket, the common shape both ingestion paths produce.

    Construct via :meth:`from_api_docket` or :meth:`from_bulk_row`, then project
    to the active tier (:meth:`to_tracked_case` + :meth:`to_record`) or the
    historical tier (:meth:`to_corpus_row`).
    """

    court_id: str
    docket_id: int
    docket_number: str = ""
    case_name: str = ""
    date_filed: date | None = None
    date_decided: date | None = None
    disposition: Disposition | None = None
    judges: tuple[str, ...] = ()
    nature_of_suit: str | None = None
    citations: tuple[str, ...] = ()
    summary: str | None = None
    source_url: str | None = None
    # Raw timeline entries, preserved on the active path so predictors keep the
    # full docket context. Bulk rows carry none.
    entries: tuple[JsonDict, ...] = field(default=(), repr=False)

    @property
    def case_id(self) -> str:
        return ids.case_id(self.court_id, self.docket_id)

    # -- constructors --

    @classmethod
    def from_api_docket(
        cls,
        payload: Mapping[str, Any],
        *,
        court_id: str | None = None,
        docket_id: int | None = None,
    ) -> NormalizedDocket:
        """Normalize a CourtListener REST API docket JSON object.

        ``court_id`` / ``docket_id`` override what is parsed from ``payload``
        (the caller usually already knows them); otherwise they are read from
        the ``court``/``court_id`` and ``id`` fields. Any ``docket_entries``
        attached to the payload are preserved.
        """
        resolved_docket_id = docket_id if docket_id is not None else payload.get("id")
        if resolved_docket_id is None:
            raise ValueError("API docket payload has no 'id' and no docket_id was supplied")
        resolved_court_id = court_id or _court_id_from_api(payload)
        if resolved_court_id is None:
            raise ValueError("API docket payload has no resolvable court id")

        judges = tuple(
            j
            for j in (
                _clean(payload.get("assigned_to_str")),
                _clean(payload.get("referred_to_str")),
            )
            if j is not None
        )
        entries = tuple(payload.get("docket_entries") or ())
        return cls(
            court_id=resolved_court_id,
            docket_id=int(resolved_docket_id),
            docket_number=_clean(payload.get("docket_number")) or "",
            case_name=(
                _clean(payload.get("case_name")) or _clean(payload.get("case_name_full")) or ""
            ),
            date_filed=_parse_date(payload.get("date_filed")),
            date_decided=_parse_date(payload.get("date_terminated")),
            disposition=parse_disposition(payload.get("disposition")),
            judges=judges,
            nature_of_suit=_clean(payload.get("nature_of_suit")),
            citations=_split_list(payload.get("citations")),
            summary=_clean(payload.get("summary")),
            source_url=_clean(payload.get("absolute_url")),
            entries=entries,
        )

    @classmethod
    def from_bulk_row(cls, row: BulkRow) -> NormalizedDocket:
        """Normalize one row of a CourtListener bulk-data CSV.

        Column names follow the bulk dockets export; missing/blank cells degrade
        to empty defaults so a sparse historical row still yields a valid corpus
        record.
        """
        court_id = _clean(row.get("court_id")) or _clean(row.get("court"))
        raw_id = _clean(row.get("id")) or _clean(row.get("docket_id"))
        if court_id is None or raw_id is None:
            raise ValueError("bulk row is missing a court id or docket id")

        return cls(
            court_id=court_id,
            docket_id=int(raw_id),
            docket_number=_clean(row.get("docket_number")) or "",
            case_name=_clean(row.get("case_name")) or "",
            date_filed=_parse_date(row.get("date_filed")),
            date_decided=_parse_date(row.get("date_terminated") or row.get("date_decided")),
            disposition=parse_disposition(row.get("disposition")),
            judges=_split_list(row.get("assigned_to_str") or row.get("judges")),
            nature_of_suit=_clean(row.get("nature_of_suit")),
            citations=_split_list(row.get("citations")),
            summary=_clean(row.get("summary") or row.get("opinion_text")),
            source_url=_clean(row.get("absolute_url")),
        )

    # -- projections --

    def to_tracked_case(
        self,
        *,
        tracked_since: date | None = None,
        last_pulled: datetime | None = None,
        status: CaseStatus = CaseStatus.active,
    ) -> TrackedCase:
        """Project to the active-tier ``case.yaml`` model."""
        return TrackedCase(
            case_id=self.case_id,
            court_id=self.court_id,
            docket_id=self.docket_id,
            docket_number=self.docket_number,
            case_name=self.case_name,
            courtlistener_url=self.source_url,
            status=status,
            tracked_since=tracked_since or date.today(),
            last_pulled=last_pulled,
        )

    def to_corpus_row(self) -> CorpusRow:
        """Project to the historical-tier packed corpus row."""
        return CorpusRow(
            case_id=self.case_id,
            court_id=self.court_id,
            docket_id=self.docket_id,
            docket_number=self.docket_number,
            case_name=self.case_name,
            date_filed=self.date_filed,
            date_decided=self.date_decided,
            disposition=self.disposition,
            judges=list(self.judges),
            nature_of_suit=self.nature_of_suit,
            citations=list(self.citations),
            summary=self.summary,
            source_url=self.source_url,
        )

    def to_record(self) -> JsonDict:
        """Build the canonical ``docket.json`` payload (active tier).

        A normalized, source-independent dict so the API and bulk paths write an
        identical record for identical inputs. Any preserved timeline ``entries``
        are attached for predictors to reason over.
        """
        record: JsonDict = {
            "case_id": self.case_id,
            "court_id": self.court_id,
            "docket_id": self.docket_id,
            "docket_number": self.docket_number,
            "case_name": self.case_name,
            "date_filed": self.date_filed.isoformat() if self.date_filed else None,
            "date_decided": self.date_decided.isoformat() if self.date_decided else None,
            "disposition": self.disposition.value if self.disposition else None,
            "judges": list(self.judges),
            "nature_of_suit": self.nature_of_suit,
            "citations": list(self.citations),
            "summary": self.summary,
            "source_url": self.source_url,
        }
        if self.entries:
            record["docket_entries"] = list(self.entries)
        return record


# --- writers (reuse serialize + store) ---------------------------------------


def write_active_case(
    data_root: Path,
    docket: NormalizedDocket,
    *,
    tracked_since: date | None = None,
    last_pulled: datetime | None = None,
    snapshot_date: date | None = None,
) -> TrackedCase:
    """Materialize the active-tier artifacts for one docket.

    Writes ``case.yaml``, ``record/docket.json``, and a dated snapshot through
    :mod:`fedcourtsai.serialize`, returning the persisted
    :class:`~fedcourtsai.schemas.TrackedCase`.
    """
    paths = CasePaths(data_root, docket.court_id, docket.docket_id)
    record = docket.to_record()
    snapshot_day = snapshot_date or date.today()
    write_raw_json(paths.docket, record)
    write_raw_json(paths.snapshot(snapshot_day.isoformat()), record)
    case = docket.to_tracked_case(
        tracked_since=tracked_since or snapshot_day,
        last_pulled=last_pulled if last_pulled is not None else datetime.now(UTC),
    )
    write_yaml(paths.case_file, case)
    return case


def select_untracked(
    data_root: Path, dockets: Iterable[NormalizedDocket]
) -> list[NormalizedDocket]:
    """Filter to dockets not already in the active tree (discovery dedup).

    Reuses :func:`fedcourtsai.store.iter_tracked_cases` so pull's discovery job
    onboards only genuinely new filings instead of re-seeding known cases.
    """
    tracked = set(iter_tracked_cases(data_root))
    return [d for d in dockets if (d.court_id, d.docket_id) not in tracked]
