"""The AI watchlist's docket activity: which new entries matter, and the daily record of them.

``watchlist-refresh`` keeps the watchlist's dockets current in the corpus. Each
refresh that finds entries the stored docket lacked passes them here, and the
ones this module's rule calls significant are recorded in
``data/ai-cases/activity/<YYYY-MM-DD>.json``, which the AI-cases update renders.

The rule (:data:`ACTIVITY_RULE`) is deliberately narrow, because the feed is
read by people following a handful of cases, and an MDL docket files dozens of
entries a week. It keeps:

- **opinions** and **judgments**;
- **rulings** on a principal motion (to dismiss, for summary judgment, class
  certification, an injunction or restraining order, judgment on the
  pleadings, to compel arbitration, to transfer);
- the principal **motions** themselves;
- **complaints**, original or amended;
- **appeals**: a notice of appeal or a petition for review;
- **resolutions**: a settlement, or a dismissal by stipulation or notice.

Everything else is routine and dropped: scheduling, appearances, pro hac vice,
extensions, sealing, transcripts, letters, discovery and its disputes. The rule
reads an entry's own description and the short description upstream gives its
main document, and nothing else.

A second, separate rule (:data:`AVAILABILITY_RULE`) watches the entries a
docket already held: a document often reaches CourtListener days or weeks
after its entry, when someone buys it from PACER. When a refresh finds an
entry filed within the last 60 days whose documents were not readable and now
are, it keeps:

- the main document of an **opinion**, a **judgment**, a **ruling** or a
  **complaint** under the significance rule;
- **exhibits** filed with a principal motion (or a motion to exclude an
  expert), with an opposition or reply to one, or in an exhibit or declaration
  entry that names one: where discovery material usually becomes public;
- **unsealed** documents and public redacted versions of any filing;
- **transcripts**, except of a conference (status, scheduling, discovery,
  pretrial), which is routine.

An entry whose documents were readable when it first appeared is not "newly
available": it was an ordinary item. An incremental refresh sees a document
arrive only if upstream marks its entry modified; the weekly whole re-read
sees every one, so an arrival is recorded within a week of it at the latest.

The record carries identifiers, dates, the kind this rule assigns (with the
principal motion a motion, ruling or opinion names), how many documents became
readable, and a link to the entry on CourtListener: never the entry's text. CourtListener's docket
content is CC BY-ND, so what is published is a pointer to the public record,
not a copy of it (``docs/data-sources.md``).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from .schemas import AiCaseActivity, AiCaseActivityEntry, AiCaseAvailableEntry
from .serialize import read_model, write_json

#: The label of the significance rule below. A changed rule is a new label.
ACTIVITY_RULE: Final = "ai-activity-v1"

#: Where the daily activity records live, under the data root.
ACTIVITY_DIR: Final = Path("ai-cases") / "activity"

#: An entry first seen more than this many days after it was filed is a late
#: upload of old history, not news, and is not recorded.
MAX_AGE_DAYS: Final = 14

COURTLISTENER: Final = "https://www.courtlistener.com"


class EntryKind(StrEnum):
    """What a significant docket entry is, in the feed's words."""

    opinion = "opinion"
    judgment = "judgment"
    ruling = "ruling"
    motion = "motion"
    complaint = "complaint"
    appeal = "appeal"
    resolution = "resolution"


# A principal motion, the kind a ruling or a filing must name to be kept.
_PRINCIPAL = (
    r"(?:motion|petition)s?\b[^.;]{0,80}?\b(?P<motion>"
    r"to\s+dismiss|for\s+(?:partial\s+)?summary\s+judgment|"
    r"(?:for|to)\s+(?:class\s+)?certif|class\s+certification|"
    r"(?:for\s+(?:a\s+)?)?preliminary\s+injunction|temporary\s+restraining\s+order|"
    r"for\s+judgment\s+on\s+the\s+pleadings|to\s+compel\s+arbitration|"
    r"to\s+transfer|(?:for|to)\s+(?:a\s+)?stay\b[^.;]{0,40}?pending\s+appeal)"
)
#: The principal motion an entry names, as the record's ``motion`` field
#: spells it, each with the phrase that identifies it. Read only from the
#: motion phrase itself (the ``motion`` group of the principal-motion pattern),
#: so words before it, such as an order certifying a question, never label it.
#: The label is the rule's own classification of the entry, like its kind: no
#: docket text. It adds to the record without changing which entries the rule
#: keeps or the kind it gives them, so the rule's label stands.
PRINCIPAL_MOTIONS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("partial-summary-judgment", re.compile(r"partial\s+summary\s+judgment", re.I)),
    ("summary-judgment", re.compile(r"summary\s+judgment", re.I)),
    ("judgment-on-the-pleadings", re.compile(r"judgment\s+on\s+the\s+pleadings", re.I)),
    ("dismiss", re.compile(r"to\s+dismiss", re.I)),
    (
        "class-certification",
        re.compile(r"(?:for|to)\s+(?:class\s+)?certif|class\s+certification", re.I),
    ),
    ("preliminary-injunction", re.compile(r"preliminary\s+injunction", re.I)),
    ("temporary-restraining-order", re.compile(r"temporary\s+restraining\s+order", re.I)),
    ("compel-arbitration", re.compile(r"compel\s+arbitration", re.I)),
    ("transfer", re.compile(r"to\s+transfer", re.I)),
    ("stay-pending-appeal", re.compile(r"stay\b[^.;]{0,40}?pending\s+appeal", re.I)),
)

# A ruling's text up to the motion it names. A period ends the sentence, except
# the abbreviations dockets cite motions by ("Dkt. No. 45", "ECF No. 12").
_SENTENCE = r"(?:[^.]|(?<=dkt)\.|(?<=no)\.|(?<=nos)\.|(?<=ecf)\.)"
# Routine business. It is read only in the stretch of an entry from its start
# through the phrase a rule matched, so an order that also schedules a
# conference, or a motion whose attachment list names a proposed order, is
# still kept, while a proposed order or a clerk's notice about a motion is not.
_ROUTINE = re.compile(
    r"pro\s+hac\s+vice|notice\s+of\s+appearance|\bappearance\b|"
    r"extension\s+of\s+time|extend\s+(?:the\s+)?(?:time|deadline)|\bschedul|"
    r"\bto\s+seal\b|\bunder\s+seal\b|\bsealing\b|\bredact|transcript|"
    r"certificate\s+of\s+service|clerk'?s\s+notice|\bsummons\b|"
    r"\bletter\b|discovery|deposition|subpoena|protective\s+order|"
    r"proposed\s+order|excess\s+pages|page\s+limit|\bwithdraw|"
    r"\bmediat|status\s+report|status\s+conference|joint\s+case\s+management|"
    r"civil\s+case\s+terminated|consent\s+to|corporate\s+disclosure|"
    r"\bminute\s+entry\b|\bopposition\b|\breply\b|\bresponse\b",
    re.IGNORECASE,
)
# The attachment list PACER appends to an entry, which describes exhibits, not
# the entry.
_ATTACHMENTS = re.compile(r"\(\s*attachments?\s*:.*$", re.IGNORECASE | re.DOTALL)
_RULES: Final[tuple[tuple[EntryKind, re.Pattern[str]], ...]] = (
    (
        EntryKind.appeal,
        re.compile(
            r"^\s*(?:amended\s+)?(?:notice\s+of\s+(?:interlocutory\s+|cross[-\s]+)?appeal|"
            r"petition\s+for\s+review)",
            re.I,
        ),
    ),
    (
        EntryKind.resolution,
        re.compile(
            r"settlement\s+agreement|notice\s+of\s+settlement|"
            r"(?:preliminary|final)\s+approval\s+of\s+(?:the\s+)?(?:proposed\s+)?"
            r"(?:class\s+(?:action\s+)?)?settlement|"
            r"stipulation\s+(?:and\s+(?:\[?proposed\]?\s+)?order\s+)?(?:of|for|to)\s+"
            r"(?:voluntary\s+)?dismissal|notice\s+of\s+(?:voluntary\s+)?dismissal|"
            r"dismissed\s+with\s+prejudice",
            re.I,
        ),
    ),
    (
        EntryKind.judgment,
        re.compile(
            r"^\s*(?:final\s+|amended\s+|partial\s+|consent\s+)?judgment\b|"
            r"^\s*order\s+of\s+final\s+relief|^\s*(?:order\s+(?:and|of)\s+)?permanent\s+injunction",
            re.I,
        ),
    ),
    (
        EntryKind.opinion,
        re.compile(
            r"^\s*(?:"
            r"(?:(?:memorandum|amended|corrected|redacted|sealed)\s+)*opinion\b"
            r"(?!\s+(?:of|from)\s+(?:counsel|expert))|"
            r"(?:memorandum|order)\s+(?:and|&)\s+(?:order|opinion)\b|"
            r"(?:\w+\s+){0,2}findings\s+of\s+fact)",
            re.I,
        ),
    ),
    (
        EntryKind.ruling,
        re.compile(r"^\s*(?:\w+\s+){0,3}order\b" + _SENTENCE + r"{0,200}?" + _PRINCIPAL, re.I),
    ),
    (
        EntryKind.complaint,
        re.compile(
            r"^\s*(?:(?:first|second|third|fourth|consolidated|class\s+action|amended|"
            r"corrected|master|verified)\s+)*complaint\b",
            re.I,
        ),
    ),
    (
        EntryKind.motion,
        re.compile(r"^\s*(?:(?:joint|cross|renewed|notice\s+of)\s+)*" + _PRINCIPAL, re.I),
    ),
)


def _texts(entry: Mapping[str, Any]) -> list[str]:
    """The entry's own description, then its main document's short description.

    Each is cut before PACER's attachment list.
    """
    texts = [str(entry.get("description") or "")]
    for document in entry.get("recap_documents") or []:
        if isinstance(document, Mapping) and not document.get("attachment_number"):
            texts.append(str(document.get("description") or ""))
            break
    cut = (_ATTACHMENTS.sub("", text) for text in texts)
    return [text for text in cut if text.strip()]


def classify(entry: Mapping[str, Any]) -> EntryKind | None:
    """The entry's kind under :data:`ACTIVITY_RULE`, or ``None`` for a routine entry.

    The first rule whose phrase appears with no routine phrase before it wins,
    reading the entry's description and then its main document's.
    """
    found = _classified(entry)
    return found[0] if found is not None else None


def _classified(entry: Mapping[str, Any]) -> tuple[EntryKind, str] | None:
    """The entry's kind and the text the winning rule matched in."""
    texts = _texts(entry)
    for kind, pattern in _RULES:
        for text in texts:
            match = pattern.search(text)
            if match and not _ROUTINE.search(text, 0, match.end()):
                return kind, text
    return None


#: The kinds whose record names the principal motion: the motion itself, a
#: ruling on it, and an opinion that decides one.
_MOTION_KINDS: Final = frozenset({EntryKind.motion, EntryKind.ruling, EntryKind.opinion})


def principal_motion(entry: Mapping[str, Any]) -> str | None:
    """The principal motion a motion, ruling or opinion entry names, or ``None``.

    The first principal motion named in the text the kind's rule matched (an
    opinion's, within its first sentence), read from the motion phrase alone.
    A motion for leave to file one names none: it asks permission, and the
    motion it names is not yet made.
    """
    found = _classified(entry)
    if found is None or found[0] not in _MOTION_KINDS:
        return None
    match = re.search(_SENTENCE + r"{0,200}?" + _PRINCIPAL, found[1], re.I)
    if match is None:
        return None
    if re.search(r"leave\s+to\s+file", found[1][match.start() : match.start("motion")], re.I):
        return None
    phrase = match.group("motion")
    return next((label for label, pattern in PRINCIPAL_MOTIONS if pattern.search(phrase)), None)


def entry_url(entry: Mapping[str, Any], docket: Mapping[str, Any]) -> str:
    """A link to the entry on CourtListener: its main document's page, else the docket."""
    for document in entry.get("recap_documents") or []:
        if isinstance(document, Mapping) and document.get("absolute_url"):
            return COURTLISTENER + str(document["absolute_url"])
    docket_path = str(docket.get("absolute_url") or f"/docket/{docket.get('id')}/")
    number = entry.get("entry_number")
    return COURTLISTENER + docket_path + (f"#entry-{number}" if number else "")


def new_significant(
    stored: Iterable[Mapping[str, Any]],
    fresh: Iterable[Mapping[str, Any]],
    *,
    today: date,
    max_age_days: int = MAX_AGE_DAYS,
) -> list[tuple[Mapping[str, Any], EntryKind]]:
    """The fresh entries the stored docket lacked that the rule keeps, oldest first.

    An entry filed more than ``max_age_days`` before ``today``, or with no
    filing date, is old history surfacing late and is left out.
    """
    known = {entry.get("id") for entry in stored}
    oldest = today - timedelta(days=max_age_days)
    found: list[tuple[Mapping[str, Any], EntryKind]] = []
    for entry in fresh:
        if entry.get("id") in known:
            continue
        try:
            filed = date.fromisoformat(str(entry.get("date_filed")))
        except ValueError:
            continue
        if filed < oldest:
            continue
        kind = classify(entry)
        if kind is not None:
            found.append((entry, kind))
    found.sort(key=lambda pair: (str(pair[0].get("date_filed")), int(pair[0].get("id") or 0)))
    return found


#: The label of the availability rule below. A changed rule is a new label.
AVAILABILITY_RULE: Final = "ai-availability-v1"

#: An entry filed more than this many days before its documents became
#: readable is old history surfacing, not news, and is not recorded.
AVAILABLE_MAX_AGE_DAYS: Final = 60


class AvailableKind(StrEnum):
    """What became readable, in the feed's words."""

    opinion = "opinion"
    judgment = "judgment"
    ruling = "ruling"
    complaint = "complaint"
    exhibits = "exhibits"
    unsealed = "unsealed"
    transcript = "transcript"


# The kinds whose main document becoming readable is news on its own.
_AVAILABLE_MAIN: Final = {
    EntryKind.opinion: AvailableKind.opinion,
    EntryKind.judgment: AvailableKind.judgment,
    EntryKind.ruling: AvailableKind.ruling,
    EntryKind.complaint: AvailableKind.complaint,
}
# A document that is itself the public form of sealed material: its own text
# opens by saying so. A motion or an order *about* unsealing is not.
_UNSEALED = re.compile(
    r"^\W*(?:unsealed|(?:public(?:ly\s+filed)?\s+)?redacted|public(?:ly\s+filed)?\s+version)\b",
    re.I,
)
_TRANSCRIPT = re.compile(
    r"^\s*(?:official\s+|certified\s+)?transcript\b(?!\s+(?:request|order|designation))", re.I
)
# A transcript of a conference (status, scheduling, discovery, pretrial) is routine.
_CONFERENCE = re.compile(r"conference|case\s+management", re.I)
# An attachment that is not evidence: the filing's paperwork.
_PAPERWORK = re.compile(
    r"proposed\s+order|certificate|cover\s+sheet|summons|text\s+of\s+proposed", re.I
)
# A filing whose exhibits carry the evidence a principal motion is argued on.
# The motion itself is read by the significance rule (so a routine motion
# that only mentions one never qualifies); an opposition or reply to one, an
# exhibit or declaration entry that names one, and a motion to exclude an
# expert are read here, each from the start of the entry.
_EXHIBIT_TOPIC = (
    r"(?:summary\s+judgment|class\s+certification|preliminary\s+injunction|"
    r"temporary\s+restraining\s+order|to\s+dismiss|judgment\s+on\s+the\s+pleadings|"
    r"compel\s+arbitration|to\s+(?:partially\s+)?exclude|daubert)"
)
_EXHIBIT_PARENT = re.compile(
    r"^\s*(?:opposition|response|reply|memorandum)\b[^.;]{0,160}?"
    + _EXHIBIT_TOPIC
    + r"|^\s*(?:additional\s+)?(?:exhibits?|declaration|affidavit|appendix)\b.{0,240}?"
    + _EXHIBIT_TOPIC
    + r"|^\s*(?:[\w']+\s+){0,6}?motion\s+to\s+(?:partially\s+)?exclude\b",
    re.I | re.DOTALL,
)
# Business that makes a filing routine even when it names a principal motion:
# the significance rule's routine list, less the briefing and sealing words
# these filings carry by nature.
_EXHIBIT_ROUTINE = re.compile(
    r"extension\s+of\s+time|extend\s+(?:the\s+)?(?:time|deadline)|excess\s+pages|"
    r"page\s+limit|leave\s+to\s+file|discovery|deposition|subpoena|\bto\s+seal\b|"
    r"\bwithdraw|proposed\s+order|\bschedul",
    re.IGNORECASE,
)
# Which kind wins when one entry is recorded twice with different kinds: the
# court's own document first, then unsealed material, a transcript, exhibits.
_AVAILABLE_RANK: Final = (
    "opinion",
    "judgment",
    "ruling",
    "complaint",
    "unsealed",
    "transcript",
    "exhibits",
)


def _readable(entry: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    """The entry's readable documents, by RECAP document id."""
    return {
        int(doc["id"]): doc
        for doc in entry.get("recap_documents") or []
        if isinstance(doc, Mapping) and doc.get("is_available") and doc.get("id") is not None
    }


def became_available(
    stored: Iterable[Mapping[str, Any]], fresh: Iterable[Mapping[str, Any]]
) -> list[tuple[Mapping[str, Any], frozenset[int]]]:
    """The fresh entries the stored docket already held that gained readable documents.

    Each with the ids of the documents that became readable. An entry the
    stored docket lacked is not here: it is new, and readable or not when it
    arrived, the significance rule's to judge.
    """
    held = {entry.get("id"): entry for entry in stored if isinstance(entry, Mapping)}
    found: list[tuple[Mapping[str, Any], frozenset[int]]] = []
    for entry in fresh:
        before = held.get(entry.get("id"))
        if before is None:
            continue
        gained = frozenset(_readable(entry)) - frozenset(_readable(before))
        if gained:
            found.append((entry, gained))
    return found


def classify_available(  # noqa: PLR0911 - one return per kind the rule keeps
    entry: Mapping[str, Any], gained: frozenset[int]
) -> tuple[AvailableKind, int, str | None] | None:
    """What the availability rule keeps of an entry's newly readable documents.

    ``(kind, documents, motion)``, or ``None`` when the rule keeps nothing.
    Read from the entry's own description and its main document's short
    description, as the significance rule reads them.
    """
    docs = _readable(entry)
    main = [i for i in gained if docs[i].get("attachment_number") is None]
    attached = [
        i
        for i in gained
        if docs[i].get("attachment_number") is not None
        and not _PAPERWORK.search(str(docs[i].get("description") or ""))
    ]
    texts = _texts(entry)
    kind = classify(entry)
    if main and kind in _AVAILABLE_MAIN:
        return _AVAILABLE_MAIN[kind], 1, principal_motion(entry)
    if any(_UNSEALED.search(t) for t in texts):
        return AvailableKind.unsealed, len(main) + len(attached), _exhibit_motion(texts)
    unsealed = [i for i in attached if _UNSEALED.search(str(docs[i].get("description") or ""))]
    if unsealed:
        return AvailableKind.unsealed, len(unsealed), _exhibit_motion(texts)
    if main and any(_TRANSCRIPT.search(t) for t in texts):
        if any(_CONFERENCE.search(t) for t in texts):
            return None
        return AvailableKind.transcript, 1, None
    if attached and _carries_evidence(entry, kind, texts):
        return AvailableKind.exhibits, len(attached), _exhibit_motion(texts)
    return None


def _carries_evidence(entry: Mapping[str, Any], kind: EntryKind | None, texts: list[str]) -> bool:
    """Whether the entry's exhibits are the evidence a principal motion is argued on."""
    if kind is EntryKind.motion and principal_motion(entry) is not None:
        return True
    for text in texts:
        match = _EXHIBIT_PARENT.search(text)
        if match is not None and not _EXHIBIT_ROUTINE.search(text, 0, match.end()):
            return True
    return False


def merge_available(
    prior: AiCaseAvailableEntry | None, later: AiCaseAvailableEntry
) -> AiCaseAvailableEntry:
    """One entry recorded twice: one kind sums its documents, else the weightier kind stands."""
    if prior is None:
        return later
    if prior.kind == later.kind:
        return later.model_copy(update={"documents": prior.documents + later.documents})
    rank = _AVAILABLE_RANK.index
    return prior if rank(prior.kind) <= rank(later.kind) else later


def _exhibit_motion(texts: list[str]) -> str | None:
    """The principal motion exhibits are filed for, read from the entry's text."""
    for text in texts:
        match = re.search(_PRINCIPAL, text, re.I)
        if match is not None:
            phrase = match.group("motion")
            return next(
                (label for label, pattern in PRINCIPAL_MOTIONS if pattern.search(phrase)), None
            )
        for label, pattern in PRINCIPAL_MOTIONS:
            if label != "transfer" and pattern.search(text):
                return label
    return None


def available_entries(
    case: str,
    category: str,
    docket: Mapping[str, Any],
    gained: Iterable[tuple[Mapping[str, Any], frozenset[int]]],
    *,
    today: date,
    max_age_days: int = AVAILABLE_MAX_AGE_DAYS,
) -> list[AiCaseAvailableEntry]:
    """The records for one docket's entries whose documents became readable, that the rule keeps."""
    court = _court(docket)
    oldest = today - timedelta(days=max_age_days)
    found: list[AiCaseAvailableEntry] = []
    for entry, ids in gained:
        try:
            filed = date.fromisoformat(str(entry.get("date_filed")))
        except ValueError:
            continue
        if filed < oldest:
            continue
        kept = classify_available(entry, ids)
        if kept is None:
            continue
        kind, documents, motion = kept
        number = entry.get("entry_number")
        try:
            found.append(
                AiCaseAvailableEntry(
                    case=case,
                    category=category,
                    court=court,
                    docket_id=int(docket["id"]),
                    docket_number=str(docket.get("docket_number") or "").strip() or "unnumbered",
                    entry_id=int(entry["id"]),
                    entry_number=int(number) if number is not None else None,
                    date_filed=filed,
                    kind=kind.value,
                    documents=documents,
                    motion=motion,
                    url=entry_url(entry, docket),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    found.sort(key=lambda e: (e.date_filed, e.entry_id))
    return found


def activity_path(data_root: Path, day: date) -> Path:
    """The day's activity record under ``data_root``."""
    return data_root / ACTIVITY_DIR / f"{day.isoformat()}.json"


def _court(docket: Mapping[str, Any]) -> str:
    """The docket's CourtListener court id."""
    court = str(docket.get("court_id") or "")
    return court or str(docket.get("court") or "").rstrip("/").rsplit("/", 1)[-1]


def activity_entries(
    case: str,
    category: str,
    docket: Mapping[str, Any],
    added: Iterable[Mapping[str, Any]],
    *,
    today: date,
) -> list[AiCaseActivityEntry]:
    """The records for one docket's newly seen entries that the rule keeps."""
    court = _court(docket)
    found: list[AiCaseActivityEntry] = []
    for entry, kind in new_significant([], added, today=today):
        try:
            found.append(_record(case, category, court, docket, entry, kind))
        except (KeyError, TypeError, ValueError):
            # A malformed upstream entry costs only itself, not the docket's
            # other entries: once stored, none of them is "new" again.
            continue
    return found


def _record(
    case: str,
    category: str,
    court: str,
    docket: Mapping[str, Any],
    entry: Mapping[str, Any],
    kind: EntryKind,
) -> AiCaseActivityEntry:
    number = entry.get("entry_number")
    return AiCaseActivityEntry(
        case=case,
        category=category,
        court=court,
        docket_id=int(docket["id"]),
        docket_number=str(docket.get("docket_number") or "").strip() or "unnumbered",
        entry_id=int(entry["id"]),
        entry_number=int(number) if number is not None else None,
        date_filed=date.fromisoformat(str(entry["date_filed"])),
        kind=kind.value,
        motion=principal_motion(entry),
        url=entry_url(entry, docket),
    )


def record_activity(
    data_root: Path,
    day: date,
    entries: Iterable[AiCaseActivityEntry],
    available: Iterable[AiCaseAvailableEntry] = (),
) -> Path | None:
    """Add ``entries`` and ``available`` to the day's record, merging each by entry id.

    ``None`` when the day has neither. A second refresh on the same day adds to
    the record rather than replacing it, so the day's file is everything any
    refresh that day found.
    """
    path = activity_path(data_root, day)
    merged: dict[int, AiCaseActivityEntry] = {}
    readable: dict[int, AiCaseAvailableEntry] = {}
    if path.is_file():
        record = read_model(path, AiCaseActivity)
        merged = {e.entry_id: e for e in record.entries}
        readable = {e.entry_id: e for e in record.available}
    merged.update({e.entry_id: e for e in entries})
    for found in available:
        readable[found.entry_id] = merge_available(readable.get(found.entry_id), found)
    if not merged and not readable:
        return None
    write_json(
        path,
        AiCaseActivity(
            day=day,
            rule=ACTIVITY_RULE,
            entries=sorted(merged.values(), key=lambda e: (e.date_filed, e.case, e.entry_id)),
            available_rule=AVAILABILITY_RULE if readable else None,
            available=sorted(readable.values(), key=lambda e: (e.date_filed, e.case, e.entry_id)),
        ),
    )
    return path
