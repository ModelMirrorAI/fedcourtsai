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

The record carries identifiers, dates, the kind this rule assigns and a link to
the entry on CourtListener: never the entry's text. CourtListener's docket
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

from .schemas import AiCaseActivity, AiCaseActivityEntry
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
    r"(?:motion|petition)s?\b[^.;]{0,80}?\b(?:"
    r"to\s+dismiss|for\s+(?:partial\s+)?summary\s+judgment|"
    r"(?:for|to)\s+(?:class\s+)?certif|class\s+certification|"
    r"(?:for\s+(?:a\s+)?)?preliminary\s+injunction|temporary\s+restraining\s+order|"
    r"for\s+judgment\s+on\s+the\s+pleadings|to\s+compel\s+arbitration|"
    r"to\s+transfer|(?:for|to)\s+(?:a\s+)?stay\b[^.;]{0,40}?pending\s+appeal)"
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
    texts = _texts(entry)
    for kind, pattern in _RULES:
        for text in texts:
            match = pattern.search(text)
            if match and not _ROUTINE.search(text, 0, match.end()):
                return kind
    return None


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


def activity_path(data_root: Path, day: date) -> Path:
    """The day's activity record under ``data_root``."""
    return data_root / ACTIVITY_DIR / f"{day.isoformat()}.json"


def activity_entries(
    case: str,
    category: str,
    docket: Mapping[str, Any],
    added: Iterable[Mapping[str, Any]],
    *,
    today: date,
) -> list[AiCaseActivityEntry]:
    """The records for one docket's newly seen entries that the rule keeps."""
    court = str(docket.get("court_id") or "")
    if not court:
        court = str(docket.get("court") or "").rstrip("/").rsplit("/", 1)[-1]
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
        url=entry_url(entry, docket),
    )


def record_activity(
    data_root: Path, day: date, entries: Iterable[AiCaseActivityEntry]
) -> Path | None:
    """Add ``entries`` to the day's record, merging by entry id; ``None`` when there are none.

    A second refresh on the same day adds to the record rather than replacing
    it, so the day's file is everything any refresh that day found.
    """
    path = activity_path(data_root, day)
    merged: dict[int, AiCaseActivityEntry] = {}
    if path.is_file():
        merged = {e.entry_id: e for e in read_model(path, AiCaseActivity).entries}
    merged.update({e.entry_id: e for e in entries})
    if not merged:
        return None
    ordered = sorted(merged.values(), key=lambda e: (e.date_filed, e.case, e.entry_id))
    write_json(path, AiCaseActivity(day=day, rule=ACTIVITY_RULE, entries=ordered))
    return path
