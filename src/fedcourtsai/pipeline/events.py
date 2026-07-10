"""Deterministic event-definition stage: one docket → its predictable events.

Turning an ingested docket into **predictable event definitions** is a separate
stage from ingestion (:mod:`fedcourtsai.pipeline.ingest`): it runs once over the
corpus regardless of how a case entered (bulk ``seed`` or forward ``pull``
discovery), so the classification is not duplicated per entry path.

Definition is *classification over structured docket entries*, not open-ended
analysis — every ``event.yaml``/:class:`fedcourtsai.corpus.CorpusEvent` is pinned
to one docket entry with a closed ``kind`` enum
(``motion`` / ``petition`` / ``appeal`` / ``order``). So this stage:

- maps each qualifying docket entry to an event (``kind``, ``docket_entry_id``,
  ``opened_at``, ``description``);
- treats an event as **predictable / unresolved** unless a *later disposing
  order references it* (cites its docket-entry number), in which case the event
  is recorded ``resolved``;
- always emits the case-level baseline event — the disposition of the appeal (or
  the petition, at SCOTUS) — so a docket with no machine-readable entries still
  carries the one thing always worth predicting.

**Deterministic first, agent only if ambiguous.** An entry the classifier cannot
confidently place (it reads like a request but matches more than one ``kind``) is
*not* guessed; it is returned in :attr:`EventExtraction.ambiguous` for a caller
to escalate to an agent reconcile issue — the same deterministic-first / agent-
fallback split the resolution-detection stage uses. The default path runs no
agent.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .. import corpus, ids
from ..schemas import EventKind
from .ingest import CorpusRow, default_event, from_api_docket

# --- docket-entry classification ----------------------------------------------

# A disposition verb is what turns an order into a *disposing* one — the signal
# that an entry resolves a request rather than being a request itself. Only the
# *resolved* forms count (``granting`` / ``dismissed``), never the base verb, so
# the requested relief in "MOTION to dismiss" is not mistaken for a disposition.
_DISPOSITION_RE = re.compile(
    r"\b(?:"
    r"grant(?:ed|ing|s)|"
    r"den(?:ied|ying|ies|ial)|"
    r"dismiss(?:ed|ing|es|al)|"
    r"withdr(?:awn|awing|aws|ew)|"
    r"vacat(?:ed|ing|es)|"
    r"affirm(?:ed|ing|s)|"
    r"revers(?:ed|ing|es)|"
    r"remand(?:ed|ing|s)|"
    r"moot(?:ed)?"
    r")\b",
    re.IGNORECASE,
)

# Request kinds, matched independently so an entry naming two of them is flagged
# ambiguous rather than silently forced into one.
_KIND_PATTERNS: tuple[tuple[EventKind, re.Pattern[str]], ...] = (
    (EventKind.appeal, re.compile(r"\bnotice of (?:cross-)?appeal\b", re.IGNORECASE)),
    (EventKind.petition, re.compile(r"\bpetition(?:s|ed|ing)?\b", re.IGNORECASE)),
    (EventKind.motion, re.compile(r"\bmotion(?:s)?\b|\bmove[sd]? (?:to|for)\b", re.IGNORECASE)),
)

# The subject of a request — the words after "motion to/for" / "petition for" —
# becomes the event slug, so two motions on one docket get distinct event ids.
_SUBJECT_PATTERNS: dict[EventKind, re.Pattern[str]] = {
    EventKind.motion: re.compile(r"motion(?:s)?\s+(?:to|for)\s+(.+)", re.IGNORECASE),
    EventKind.petition: re.compile(r"petition(?:s)?\s+for\s+(?:a\s+)?(.+)", re.IGNORECASE),
}

# The substantive SCOTUS applications worth an entry-pinned event; every other
# SCOTUS motion (extensions, IFP leave, amicus leave, …) is administrative.
_SCOTUS_SUBSTANTIVE_MOTION_RE = re.compile(r"\bstay\b|\binjunction\b|\bemergency\b", re.IGNORECASE)

# How a disposing order cites the entry it resolves: "Dkt. 12", "ECF No. 12",
# "entry 12", "#12". The captured number is matched against an entry's number.
_REFERENCE_RE = re.compile(
    r"(?:dkt|docket|ecf|doc(?:ument)?|entry|entries|no|nos|#)\.?\s*(?:no\.?\s*)?(\d+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DocketEntry:
    """The slice of one CourtListener docket entry classification needs."""

    entry_id: int
    text: str
    date_filed: date | None
    number: int | None


@dataclass
class AmbiguousEntry:
    """A docket entry the deterministic classifier could not place confidently.

    Surfaced (not guessed) so a caller can escalate it to an agent reconcile
    issue; carries enough context for that issue to be actionable.
    """

    case_id: str
    entry_id: int
    description: str
    reason: str


@dataclass
class EventExtraction:
    """What the event-definition stage derived from one docket."""

    events: list[corpus.CorpusEvent] = field(default_factory=list)
    ambiguous: list[AmbiguousEntry] = field(default_factory=list)


def _entry_text(raw: Mapping[str, Any]) -> str:
    """Flatten an entry's description and its documents' descriptions into text."""
    parts: list[str] = [str(raw.get("description") or "")]
    documents = raw.get("recap_documents")
    if isinstance(documents, Sequence) and not isinstance(documents, str | bytes):
        for doc in documents:
            if isinstance(doc, Mapping):
                parts.append(str(doc.get("short_description") or doc.get("description") or ""))
    return " ".join(part for part in parts if part).strip()


def _to_entry(raw: Mapping[str, Any]) -> DocketEntry | None:
    """Project a raw API docket entry onto :class:`DocketEntry`, or skip if unusable."""
    entry_id = raw.get("id")
    if entry_id is None:
        return None
    number_raw = raw.get("entry_number")
    date_raw = raw.get("date_filed")
    return DocketEntry(
        entry_id=int(entry_id),
        text=_entry_text(raw),
        date_filed=date.fromisoformat(date_raw) if isinstance(date_raw, str) and date_raw else None,
        number=int(number_raw)
        if isinstance(number_raw, int | str) and str(number_raw).isdigit()
        else None,
    )


def _matched_kinds(text: str) -> list[EventKind]:
    return [kind for kind, pattern in _KIND_PATTERNS if pattern.search(text)]


def _is_disposing_order(text: str) -> bool:
    """Whether an entry disposes of a request (has a disposition verb)."""
    return bool(_DISPOSITION_RE.search(text))


def _subject_slug(text: str, kind: EventKind) -> str:
    """Slug for an event id, taken from the request's subject (e.g. ``stay-pending-appeal``)."""
    pattern = _SUBJECT_PATTERNS.get(kind)
    subject = ""
    if pattern is not None:
        match = pattern.search(text)
        if match:
            subject = match.group(1)
    # Cut at the first boundary that ends the request phrase, keep a few words.
    subject = re.split(r"[.;,]| filed | by | pursuant ", subject, maxsplit=1, flags=re.IGNORECASE)[
        0
    ]
    slug = ids.slugify(" ".join(subject.split()[:6]))
    return slug if slug != "x" else "disposition"


def _referenced_numbers(text: str) -> set[int]:
    return {int(m.group(1)) for m in _REFERENCE_RE.finditer(text)}


def extract_events(
    docket: Mapping[str, Any],
    *,
    normalize: Callable[[Mapping[str, Any]], CorpusRow] = from_api_docket,
) -> EventExtraction:
    """Derive the predictable events defined by one docket.

    Always includes the case-level baseline event (the appeal/petition
    disposition). For each classifiable docket entry it adds a finer-grained
    event pinned to that entry, marking it ``resolved`` when a later disposing
    order cites the entry's number. Entries that read like a request but match
    more than one ``kind`` are returned as :attr:`EventExtraction.ambiguous`
    rather than guessed.

    ``normalize`` is the seam over the entry path: forward ``pull`` discovery
    hands API docket objects (the default, :func:`from_api_docket`), while bulk
    ``seed`` hands CSV rows (:func:`from_bulk_row`). Both normalize to the same
    :class:`CorpusRow`, so one extractor serves both sources and a seeded docket
    yields the same event shape as a discovered one. Entry-pinned events still
    require ``docket_entries``; a bulk row that carries none gets the baseline
    event alone, and a later ``pull`` refresh can enrich it.
    """
    row = normalize(docket)
    result = EventExtraction(events=[default_event(row)])

    raw_entries = docket.get("docket_entries")
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, str | bytes):
        return result

    entries = [entry for raw in raw_entries if (entry := _to_entry(raw)) is not None]

    # A disposing order resolves a request only if it references that request's
    # entry number — "no later disposing order referencing it" ⇒ still predictable.
    resolved_numbers: set[int] = set()
    for entry in entries:
        if _is_disposing_order(entry.text):
            resolved_numbers |= _referenced_numbers(entry.text)

    used_ids: set[str] = {event.event_id for event in result.events}
    for entry in entries:
        if _is_disposing_order(entry.text):
            continue  # a disposition, not a thing to predict
        kinds = _matched_kinds(entry.text)
        if not kinds:
            continue  # routine entry (scheduling order, notice of appearance, …)
        if len(kinds) > 1:
            result.ambiguous.append(
                AmbiguousEntry(
                    case_id=row.case_id,
                    entry_id=entry.entry_id,
                    description=entry.text,
                    reason=f"matches multiple event kinds: {', '.join(k.value for k in kinds)}",
                )
            )
            continue

        kind = kinds[0]
        if (
            kind == EventKind.motion
            and row.court == "scotus"
            and not _SCOTUS_SUBSTANTIVE_MOTION_RE.search(entry.text)
        ):
            # A SCOTUS docket's motions are overwhelmingly administrative —
            # extensions of time, IFP leave, amicus leave — filed and granted as
            # a matter of course; the live channel (#472) surfaces them on every
            # petition, and each would sit as an open "predictable" event
            # forever (SCOTUS orders never cite entry numbers, so the
            # disposing-order latch cannot close them) and drag decided cases
            # into the predict queue. Only the substantive applications the
            # pipeline actually means to track (stay / injunction / emergency)
            # earn an entry-pinned event; widening this is additive — a new
            # pattern extracts on the next refresh.
            continue
        if kind == EventKind.petition and row.court == "scotus":
            # At SCOTUS the petition *is* the case: the "petition for a writ of
            # certiorari filed" entry (every live docket's first proceedings
            # line, #472) duplicates the case-level baseline
            # `evt-petition-disposition`, and a second open petition event would
            # turn every deterministic resolution ambiguous ("the case-level
            # disposition cannot be attributed to one event"). Rehearing and
            # successive petitions collapse into the same baseline for the same
            # reason; stays and emergency applications are motions and still
            # extract as their own events.
            continue
        event_id = ids.event_id(kind.value, _subject_slug(entry.text, kind))
        # Guarantee within-case uniqueness deterministically (two like motions).
        if event_id in used_ids:
            event_id = f"{event_id}-{entry.number if entry.number is not None else entry.entry_id}"
        used_ids.add(event_id)

        result.events.append(
            corpus.CorpusEvent(
                event_id=event_id,
                case_id=row.case_id,
                court=row.court,
                kind=kind,
                title=row.case_name or row.docket_number or row.case_id,
                description=entry.text or None,
                docket_entry_id=entry.entry_id,
                decision_target="disposition",
                opened_at=entry.date_filed or row.date_filed,
                resolved=entry.number is not None and entry.number in resolved_numbers,
            )
        )

    return result
