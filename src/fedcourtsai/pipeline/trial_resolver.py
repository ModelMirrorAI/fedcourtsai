"""Deterministic resolution of the trial stage's events from a district docket.

The trial stage (``docs/trial-stage.md``) registers four moments a district
case passes: a ruling on a motion to dismiss, on class certification, on a
motion for summary judgment, and the case's final disposition. This module
reads how each resolved from the court's own record, with no agent:

- the order disposing of a motion is located by docket entry, a later order or
  opinion that cites the motion's entry number (or, where an order cites no
  entry at all, names a motion of the same kind);
- the disposition is read from the docket text and, where the order's text is
  at hand, from its decretal language (the ordering paragraph, not the
  discussion), and the two must agree;
- a settlement, a stipulated dismissal or a voluntary dismissal of the whole
  action resolves the final disposition as **no merits decision**, and any
  motion still open as mooted;
- a motion withdrawn, or denied or terminated as moot, resolves as such:
  nothing is voided.

Anything the rule cannot read with confidence is returned as
:class:`Unresolved`, with the reason and the entries it weighed, for the
maintainer's triage, and never guessed. Every resolution cites the docket
entry it read.

The input is the docket-entry shape CourtListener's ``docket-entries``
endpoint serves (``id``, ``entry_number``, ``date_filed``, ``description``,
``recap_documents``), which is what ``watchlist-refresh`` stores. The order
text, where a caller has it, is passed separately, keyed by entry id. This
module reads only what it is given and fetches nothing.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any, Final

#: The label of the reading rule below. A changed rule is a new label.
RESOLVER_RULE: Final = "trial-resolver-v1"


class TrialMoment(StrEnum):
    """The trial stage's moments (``docs/trial-stage.md``)."""

    dismissal = "trial-dismissal"
    class_certification = "trial-class"
    summary_judgment = "trial-summary-judgment"
    judgment = "trial-judgment"


#: The moments that forecast a ruling on one motion.
MOTION_MOMENTS: Final = frozenset(
    {TrialMoment.dismissal, TrialMoment.class_certification, TrialMoment.summary_judgment}
)


class MotionRuling(StrEnum):
    """How a motion event resolved."""

    granted = "granted"
    granted_in_part = "granted-in-part"
    denied = "denied"
    #: The movant withdrew the motion.
    withdrawn = "withdrawn"
    #: The court denied or terminated the motion as moot, or the action closed
    #: without a ruling on it.
    mooted = "mooted"


class Leave(StrEnum):
    """Whether a dismissal, in whole or in part, left the claims open to amendment."""

    with_leave = "with-leave"
    without_leave = "without-leave"
    #: The text says neither; ``without prejudice`` alone is read as unstated.
    unstated = "unstated"


class JudgmentOutcome(StrEnum):
    """How the case's final disposition resolved."""

    plaintiff = "plaintiff"
    defendant = "defendant"
    mixed = "mixed"
    #: Settled, or dismissed by stipulation or voluntarily: the court decided
    #: nothing on the merits.
    no_merits_decision = "no-merits-decision"


class Source(StrEnum):
    """What a resolution was read from."""

    docket_text = "docket-text"
    order_text = "order-text"
    #: The docket text and the order's decretal language, which agreed.
    both = "docket-and-order"


@dataclass(frozen=True)
class Citation:
    """The docket entry a resolution read."""

    entry_id: int | None
    entry_number: int | None
    date_filed: date | None


@dataclass(frozen=True)
class MotionEvent:
    """One motion the trial stage forecasts, named by the entry that filed it."""

    moment: TrialMoment
    entry_number: int

    def __post_init__(self) -> None:
        if self.moment not in MOTION_MOMENTS:
            raise ValueError(f"{self.moment} is not a motion moment")


@dataclass(frozen=True)
class MotionResolution:
    moment: TrialMoment
    ruling: MotionRuling
    #: Read only for a dismissal granted in whole or in part; otherwise ``None``.
    leave: Leave | None
    cited: Citation
    source: Source
    rule: str = RESOLVER_RULE


@dataclass(frozen=True)
class JudgmentResolution:
    outcome: JudgmentOutcome
    cited: Citation
    source: Source
    moment: TrialMoment = TrialMoment.judgment
    rule: str = RESOLVER_RULE


@dataclass(frozen=True)
class Unresolved:
    """An event the record has moved on but the rule cannot read: maintainer triage."""

    moment: TrialMoment
    reason: str
    candidates: tuple[Citation, ...]
    rule: str = RESOLVER_RULE


# --- reading text ------------------------------------------------------------

_WS = re.compile(r"\s+")
_ATTACHMENTS = re.compile(r"\(\s*attachments?\s*:.*$", re.IGNORECASE | re.DOTALL)

_MOTION_KIND: Final[tuple[tuple[TrialMoment, re.Pattern[str]], ...]] = (
    (TrialMoment.summary_judgment, re.compile(r"\bsummary\s+judgment\b", re.I)),
    (
        TrialMoment.class_certification,
        re.compile(r"\b(?:for|to)\s+(?:class\s+)?certif\w*|\bclass\s+certification\b", re.I),
    ),
    (TrialMoment.dismissal, re.compile(r"\bto\s+dismiss\b", re.I)),
)

# A motion named in a docket text or an order: what an order with no entry
# reference must name to be read as disposing of a motion of that kind.
_MOTION_WORD = re.compile(r"\bmotions?\b", re.I)

# Leave to amend, read before the polarity so its own "granted" or "denied"
# never counts as the ruling's.
_WITHOUT_LEAVE = re.compile(
    r"\bwithout\s+leave\s+to\s+(?:amend|replead)\b|\bwith\s+prejudice\b|"
    r"\bleave\s+to\s+(?:amend|replead)\s+(?:is\s+|shall\s+be\s+)?denied\b|"
    r"\bdenies\s+leave\s+to\s+(?:amend|replead)\b|\bamendment\s+would\s+be\s+futile\b",
    re.I,
)
_WITH_LEAVE = re.compile(
    r"\bwith\s+leave\s+to\s+(?:amend|replead|file)\b|"
    r"\bleave\s+to\s+(?:amend|replead)\s+(?:is\s+|shall\s+be\s+)?granted\b|"
    r"\bgrants\s+leave\s+to\s+(?:amend|replead)\b|"
    r"\bmay\s+file\s+(?:a|an)\s+(?:second\s+|third\s+)?amended\s+complaint\b",
    re.I,
)
_LEAVE_PHRASES = re.compile(
    r"\b(?:with(?:out)?\s+)?leave\s+to\s+(?:amend|replead|file)\b[^.;]*|"
    r"\b(?:grants|denies)\s+leave\s+to\s+(?:amend|replead)\b[^.;]*|"
    r"\bwith(?:out)?\s+prejudice\b|"
    r"\bmay\s+file\s+(?:a|an)\s+(?:second\s+|third\s+)?amended\s+complaint\b[^.;]*",
    re.I,
)

_IN_PART = re.compile(
    r"\bgrant\w*\s+in\s+part\b|\bden\w*\s+in\s+part\b|\bin\s+part\s+(?:granted|denied)\b|"
    r"\bpartial(?:ly)?\s+grant",
    re.I,
)
_MOOT = re.compile(
    r"(?:\b(?:den(?:y|ies|ied|ying)|terminat\w*|dismiss\w*|find\w*|deem\w*)\s+"
    r"(?:\S+\s+){0,8}?)?\bas\s+moot\b|\b(?:is|are|now)\s+moot\b|\bmooted\b",
    re.I,
)
_WITHDRAWN = re.compile(r"\bwithdrawn\b|\bwithdrawal\s+of\b[^.;]{0,40}\bmotion\b", re.I)
_GRANTED = re.compile(r"\bgrant(?:s|ed|ing)?\b", re.I)
_DENIED = re.compile(r"\bden(?:y|ies|ied|ying)\b", re.I)

# Where an order with no "it is ordered" states its ruling: the last of these.
_ORDERED = re.compile(r"\bit\s+is\s+(?:hereby\s+)?ordered\b", re.I)
_DECRETAL = re.compile(
    r"\bfor\s+the\s+(?:foregoing\s+)?reasons\b|"
    r"\bfor\s+(?:these|those|all\s+of\s+the\s+above)\s+reasons\b|\bin\s+conclusion\b|"
    r"\baccordingly,|^\s*conclusion\s*$",
    re.I | re.M,
)

# A docket entry that is the court's disposition: an order, an opinion, or a
# minute order, as against a party's filing that merely mentions one.
_COURT_ENTRY = re.compile(
    r"^\s*(?:(?:memorandum|amended|corrected|redacted|sealed|electronic|text|minute|"
    r"paperless|endorsed|stipulated)\s+)*(?:order|opinion|memorandum\b|ruling|decision)\b|"
    r"^\s*minute\s+entry\b",
    re.I,
)
# An entry that is a party's own filing about a motion, never the ruling.
_PARTY_FILING = re.compile(
    r"^\s*(?:(?:joint|amended|corrected)\s+)*(?:notice|response|reply|opposition|"
    r"memorandum\s+(?:of\s+(?:law|points)|in\s+(?:support|opposition))|brief|"
    r"declaration|letter|stipulation|proposed\s+order)\b",
    re.I,
)

_WITHDRAWAL_NOTICE = re.compile(r"^\s*notice\s+of\s+withdrawal\b|^\s*notice\s+withdrawing\b", re.I)

_REF_PREFIX = r"(?:ecf|dkt|doc|docket|d\.\s*e)\.?\s*(?:nos?\.?|#)?\s*"


def _ref_pattern(number: str) -> re.Pattern[str]:
    """How a docket text or an order cites a docket entry by ``number``.

    The court's ECF forms (``ECF No. 45``, ``Dkt. 45``, ``Doc. #45``, ``[45]``,
    ``re 45``) and CM/ECF's bare ``45 MOTION`` lead. A bare number not followed
    by a motion is not a reference, so a count of days never reads as one.
    """
    return re.compile(
        rf"{_REF_PREFIX}(?:\d+\s*(?:,|and|&)\s*)*{number}\b|\[\s*{number}\s*\]|"
        rf"#\s*{number}\b|\bre:?\s+{number}\b|"
        rf"\b{number}\s+(?:\w+\s+){{0,4}}?motion",
        re.I,
    )


_ANY_REF = _ref_pattern(r"\d+")


def _clean(text: str) -> str:
    return _WS.sub(" ", _ATTACHMENTS.sub("", text)).strip()


def motion_moment(text: str) -> TrialMoment | None:
    """The trial moment a motion's docket text names, or ``None`` for another motion."""
    cleaned = _clean(text)
    if not _MOTION_WORD.search(cleaned):
        return None
    for moment, pattern in _MOTION_KIND:
        if pattern.search(cleaned):
            return moment
    return None


@dataclass(frozen=True)
class Reading:
    """What one stretch of text says about a ruling."""

    ruling: MotionRuling | None
    leave: Leave


def read_ruling(text: str) -> Reading:
    """Read a ruling from a stretch of text that concerns one motion.

    Leave to amend and prejudice are read first and then struck, so the
    ``granted`` in "leave to amend is granted" is never the ruling. "In part",
    or a grant and a denial together, is a ruling in part; "as moot" is a
    mooted motion unless a grant or denial on the merits stands beside it; and
    a text with no ruling verb reads ``None``.
    """
    cleaned = _clean(text)
    if _WITHOUT_LEAVE.search(cleaned):
        leave = Leave.without_leave
    elif _WITH_LEAVE.search(cleaned):
        leave = Leave.with_leave
    else:
        leave = Leave.unstated
    return Reading(_polarity(_LEAVE_PHRASES.sub(" ", cleaned)), leave)


def _polarity(body: str) -> MotionRuling | None:
    """The ruling a text with its leave phrases struck states, or ``None``."""
    if _IN_PART.search(body):
        return MotionRuling.granted_in_part
    merits = _MOOT.sub(" ", body)
    granted = bool(_GRANTED.search(merits))
    denied = bool(_DENIED.search(merits))
    if granted or denied:
        if granted and denied:
            return MotionRuling.granted_in_part
        return MotionRuling.granted if granted else MotionRuling.denied
    if _MOOT.search(body):
        return MotionRuling.mooted
    if _WITHDRAWN.search(body):
        return MotionRuling.withdrawn
    return None


def _clauses_citing(text: str, number: int) -> list[str] | None:
    """The clauses of ``text`` that cite entry ``number``.

    ``None`` when the text cites no entry at all, so the caller reads it whole;
    an empty list when it cites other entries only. A clause ends at a
    semicolon, or at a sentence end not inside an ECF citation.
    """
    if not _ANY_REF.search(text):
        return None
    own = _ref_pattern(str(number))
    clauses = re.split(
        r";|(?<!\bno)(?<!\bnos)(?<!\bdkt)(?<!\becf)(?<!\bdoc)\.\s+", text, flags=re.I
    )
    return [clause for clause in clauses if own.search(clause)]


def _segment_reading(text: str, number: int, moment: TrialMoment) -> Reading | None:
    """Read ``text`` for the ruling on motion ``number``, or ``None`` if it rules on none."""
    cleaned = _clean(text)
    clauses = _clauses_citing(cleaned, number)
    if clauses is None:
        # No entry cited: the text speaks for the motion only if it names one
        # of the same kind and no other kind.
        if motion_moment(cleaned) is not moment:
            return None
        named = {m for m, pattern in _MOTION_KIND if pattern.search(cleaned)}
        if len(named) != 1:
            return None
        reading = read_ruling(cleaned)
    elif not clauses:
        return None
    else:
        reading = read_ruling(" ; ".join(clauses))
    return reading if reading.ruling is not None else None


def decretal(order_text: str) -> str | None:
    """An order's decretal language, or ``None`` when it has no ordering anchor.

    It runs from the first "it is ordered" to the end, since a later "it is
    further ordered" adds to the ruling rather than replacing it; an order with
    none runs from its last concluding anchor ("for the foregoing reasons",
    "accordingly", a "Conclusion" heading).
    """
    ordered = _ORDERED.search(order_text)
    if ordered is not None:
        return order_text[ordered.start() :]
    anchors = list(_DECRETAL.finditer(order_text))
    if not anchors:
        return None
    return order_text[anchors[-1].start() :]


# --- reading entries ---------------------------------------------------------


def _entry_texts(entry: Mapping[str, Any]) -> list[str]:
    """The entry's own description, then its main document's short description."""
    texts = [str(entry.get("description") or "")]
    for document in entry.get("recap_documents") or []:
        if isinstance(document, Mapping) and not document.get("attachment_number"):
            texts.append(str(document.get("description") or ""))
            break
    return [_clean(text) for text in texts if text and text.strip()]


def _entry_text(entry: Mapping[str, Any]) -> str:
    return " ; ".join(_entry_texts(entry))


def _number(entry: Mapping[str, Any]) -> int | None:
    value = entry.get("entry_number")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _filed(entry: Mapping[str, Any]) -> date | None:
    try:
        return date.fromisoformat(str(entry.get("date_filed")))
    except ValueError:
        return None


def cite(entry: Mapping[str, Any]) -> Citation:
    """The citation a resolution carries for ``entry``."""
    raw = entry.get("id")
    try:
        entry_id = int(raw) if raw is not None else None
    except (TypeError, ValueError):
        entry_id = None
    return Citation(entry_id=entry_id, entry_number=_number(entry), date_filed=_filed(entry))


def _ordered(entries: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Entries in docket order: by filing date, then entry number, then id."""

    def key(entry: Mapping[str, Any]) -> tuple[date, int, int]:
        cited = cite(entry)
        return (
            cited.date_filed or date.max,
            cited.entry_number if cited.entry_number is not None else 1 << 30,
            cited.entry_id or 0,
        )

    return sorted(entries, key=key)


def _after(entries: Sequence[Mapping[str, Any]], number: int) -> list[Mapping[str, Any]]:
    """The entries after the motion's own, in docket order.

    Where the motion's entry is not among ``entries``, an entry numbered above
    it is after it; an unnumbered entry (a minute order) counts only once a
    numbered entry after the motion precedes it.
    """
    ordered = _ordered(entries)
    for index, entry in enumerate(ordered):
        if _number(entry) == number:
            return ordered[index + 1 :]
    later: list[Mapping[str, Any]] = []
    started = False
    for entry in ordered:
        entry_number = _number(entry)
        if entry_number is not None:
            started = entry_number > number
        if started:
            later.append(entry)
    return later


# A closure limited to some parties, counts or claims, which leaves the action open.
_PARTIAL = re.compile(
    r"\bas\s+to\s+(?:defendants?|plaintiffs?|count|claims?)\b|\b(?:of|dismissing)\s+(?:certain|some)\b|"
    r"\bpartial\b|\bcount\s+[ivx\d]+\b|\bonly\b|\bagainst\s+defendants?\s+[A-Z]",
    re.I,
)
# A settlement notice is news, not yet the end: the case closes on the
# dismissal or judgment that follows. These close it on their own.
_CLOSES_ON_ITS_OWN = re.compile(
    r"\bstipulat\w*\s+(?:\w+\s+){0,4}?(?:of\s+|for\s+|to\s+)?(?:voluntary\s+)?dismiss\w*|"
    r"\bnotice\s+of\s+(?:voluntary\s+)?dismissal\b|\bvoluntar\w*\s+dismiss\w*|"
    r"\bfinal\s+approval\b|\b(?:consent|stipulated|agreed)\s+judgment\b|"
    r"\bjudgment\s+(?:by|on)\s+consent\b|\bdismissed\s+(?:as\s+)?settled\b",
    re.I,
)


def _closes(text: str) -> bool:
    """Whether a docket text closes the whole action without a merits decision."""
    return bool(_CLOSES_ON_ITS_OWN.search(text)) and not _PARTIAL.search(text)


def find_closure(entries: Iterable[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """The first entry that closes the whole action without a merits decision.

    A stipulated or voluntary dismissal, a final settlement approval, or a
    consent judgment closes it; a dismissal limited to some parties, counts or
    claims does not, and neither does a notice of settlement alone.
    """
    for entry in _ordered(entries):
        if _closes(_entry_text(entry)):
            return entry
    return None


def resolve_motion(
    event: MotionEvent,
    entries: Iterable[Mapping[str, Any]],
    *,
    order_texts: Mapping[int, str] | None = None,
) -> MotionResolution | Unresolved | None:
    """How motion ``event`` resolved on this docket, or ``None`` while it is open.

    ``entries`` are the docket's entries, in any order. ``order_texts`` maps an
    entry id to the text of the order or opinion that entry carries, where the
    caller has it. The first court entry after the motion that rules on it
    resolves it: read from the docket text, and from the order's decretal
    language where its text is given, and the two must agree. A withdrawal
    notice citing the motion resolves it withdrawn; a closure of the action
    before any ruling resolves it mooted.
    """
    texts = order_texts or {}
    later = _after(list(entries), event.entry_number)
    weighed: list[Citation] = []
    for entry in later:
        docket_text = _entry_text(entry)
        cited = cite(entry)
        if _closes(docket_text):
            return MotionResolution(
                event.moment, MotionRuling.mooted, None, cited, Source.docket_text
            )
        if _PARTY_FILING.search(docket_text):
            if _WITHDRAWAL_NOTICE.search(docket_text) and _clauses_citing(
                docket_text, event.entry_number
            ):
                return MotionResolution(
                    event.moment, MotionRuling.withdrawn, None, cited, Source.docket_text
                )
            continue
        if not _COURT_ENTRY.search(docket_text):
            continue
        from_docket = _segment_reading(docket_text, event.entry_number, event.moment)
        order_text = texts.get(cited.entry_id) if cited.entry_id is not None else None
        from_order: Reading | None = None
        if order_text:
            ordering = decretal(order_text)
            if ordering is not None:
                from_order = _segment_reading(ordering, event.entry_number, event.moment)
        if from_docket is None and from_order is None:
            if order_text and _ref_pattern(str(event.entry_number)).search(order_text):
                weighed.append(cited)
            continue
        return _settle(event, cited, from_docket, from_order, weighed)
    if weighed:
        return Unresolved(
            event.moment,
            "an order cites the motion but no ruling on it could be read",
            tuple(weighed),
        )
    return None


def _settle(
    event: MotionEvent,
    cited: Citation,
    from_docket: Reading | None,
    from_order: Reading | None,
    weighed: Sequence[Citation],
) -> MotionResolution | Unresolved:
    candidates = (*weighed, cited)
    if from_docket is not None and from_order is not None:
        if from_docket.ruling is not from_order.ruling:
            return Unresolved(
                event.moment,
                f"the docket text reads {from_docket.ruling} and the order reads "
                f"{from_order.ruling}",
                candidates,
            )
        leave = _leave(from_docket.leave, from_order.leave)
        if leave is None:
            return Unresolved(
                event.moment,
                f"the docket text reads leave {from_docket.leave} and the order "
                f"reads leave {from_order.leave}",
                candidates,
            )
        reading = Reading(from_docket.ruling, leave)
        source = Source.both
    elif from_order is not None:
        reading, source = from_order, Source.order_text
    else:
        assert from_docket is not None
        reading, source = from_docket, Source.docket_text
    assert reading.ruling is not None
    leave_read: Leave | None = None
    if event.moment is TrialMoment.dismissal and reading.ruling in {
        MotionRuling.granted,
        MotionRuling.granted_in_part,
    }:
        leave_read = reading.leave
    return MotionResolution(event.moment, reading.ruling, leave_read, cited, source)


def _leave(docket: Leave, order: Leave) -> Leave | None:
    """The leave both readings support: a stated one wins over unstated; a clash is ``None``."""
    if docket is order:
        return docket
    if docket is Leave.unstated:
        return order
    if order is Leave.unstated:
        return docket
    return None


# --- the final disposition ---------------------------------------------------

_JUDGMENT_ENTRY = re.compile(
    r"^\s*(?:(?:final|amended|clerk'?s|corrected)\s+)*judgment\b|"
    r"^\s*(?:order\s+(?:and|of)\s+)?final\s+judgment\b|\bjudgment\s+is\s+(?:hereby\s+)?entered\b",
    re.I,
)
_NOT_FINAL = re.compile(
    r"\bpartial\s+(?:final\s+)?judgment\b|\brule\s+54\s*\(\s*b\s*\)|\bdefault\b",
    re.I,
)
# A party word in the gap names that side, never the other: "in favor of
# Defendants against Plaintiffs" is a judgment for the defendants.
_FOR_PLAINTIFF = re.compile(
    r"\bin\s+favou?r\s+of\s+(?:the\s+)?(?:(?!(?:against|and|on|in)\b)\w+\s+){0,2}?plaintiffs?\b|"
    r"\bagainst\s+(?:the\s+)?(?:(?!(?:against|and|on|in)\b)\w+\s+){0,2}?defendants?\b",
    re.I,
)
_FOR_DEFENDANT = re.compile(
    r"\bin\s+favou?r\s+of\s+(?:the\s+)?(?:(?!(?:against|and|on|in)\b)\w+\s+){0,2}?defendants?\b|"
    r"\bagainst\s+(?:the\s+)?(?:(?!(?:against|and|on|in)\b)\w+\s+){0,2}?plaintiffs?\b|"
    r"\b(?:plaintiffs?\s+take\s+nothing|action\s+is\s+dismissed\s+(?:on\s+the\s+merits|with\s+prejudice))\b",
    re.I,
)


def read_judgment(text: str) -> JudgmentOutcome | None:
    """The side a final judgment's text names, or ``None`` when it names neither."""
    cleaned = _clean(text)
    if _CLOSES_ON_ITS_OWN.search(cleaned):
        return JudgmentOutcome.no_merits_decision
    plaintiff = bool(_FOR_PLAINTIFF.search(cleaned))
    defendant = bool(_FOR_DEFENDANT.search(cleaned))
    if plaintiff and defendant:
        return JudgmentOutcome.mixed
    if plaintiff:
        return JudgmentOutcome.plaintiff
    if defendant:
        return JudgmentOutcome.defendant
    return None


def resolve_judgment(
    entries: Iterable[Mapping[str, Any]],
    *,
    order_texts: Mapping[int, str] | None = None,
) -> JudgmentResolution | Unresolved | None:
    """How the case's final disposition resolved, or ``None`` while it is open.

    The first entry that closes the action decides it: a closure without a
    merits decision (:func:`find_closure`), or a final judgment, read for the
    side it names from the docket text and, where given, the judgment's own
    text, which must agree. A partial, Rule 54(b) or default judgment is not
    the final disposition and is passed over. A final judgment naming no side
    is :class:`Unresolved`.
    """
    texts = order_texts or {}
    for entry in _ordered(entries):
        docket_text = _entry_text(entry)
        cited = cite(entry)
        if _closes(docket_text):
            return JudgmentResolution(JudgmentOutcome.no_merits_decision, cited, Source.docket_text)
        if _PARTY_FILING.search(docket_text) or not _JUDGMENT_ENTRY.search(docket_text):
            continue
        if _NOT_FINAL.search(docket_text):
            continue
        judgment_text = texts.get(cited.entry_id) if cited.entry_id is not None else None
        return _settle_judgment(cited, read_judgment(docket_text), judgment_text)
    return None


def _settle_judgment(
    cited: Citation, from_docket: JudgmentOutcome | None, judgment_text: str | None
) -> JudgmentResolution | Unresolved:
    from_order = read_judgment(judgment_text) if judgment_text else None
    if from_docket is not None and from_order is not None and from_docket is not from_order:
        return Unresolved(
            TrialMoment.judgment,
            f"the docket text reads {from_docket} and the judgment reads {from_order}",
            (cited,),
        )
    if from_docket is not None and from_order is not None:
        return JudgmentResolution(from_docket, cited, Source.both)
    if from_order is not None:
        return JudgmentResolution(from_order, cited, Source.order_text)
    if from_docket is not None:
        return JudgmentResolution(from_docket, cited, Source.docket_text)
    return Unresolved(TrialMoment.judgment, "a final judgment entered but names no side", (cited,))
