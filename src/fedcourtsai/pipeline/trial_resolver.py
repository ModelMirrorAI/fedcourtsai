"""Deterministic resolution of the trial stage's events from a district docket.

The trial stage (``docs/trial-stage.md``) defines four moments a district case
passes: a ruling on a motion to dismiss, on class certification, on a motion
for summary judgment, and the case's final disposition. This module reads how
each resolved from the court's own record, with no agent.

The rule is built to miss rather than misread. It reads only the forms courts
use to rule, and anything else is either not a ruling (the event stays open)
or, where the record has plainly moved on and the rule cannot say how, an
:class:`Unresolved` outcome with its reason and the entries weighed, for the
maintainer's triage:

- **A ruling names the motion as its object.** In a docket text that is the
  CM/ECF form, a ruling verb with the motion's entry number directly after it
  (``ORDER granting 45 Motion to Dismiss``); a number that appears anywhere
  else (``re 45``, ``in support of 45``) names a motion's subject, not the one
  ruled on. In an order's decretal language it is a sentence whose subject
  cites the motion (``the Motion to Dismiss (ECF No. 45) is DENIED``) or whose
  verb takes it as object (``the Court GRANTS ... (ECF No. 45)``). An entry or
  order that cites no entry number is never read as a ruling, because a
  docket can hold several motions of one kind.
- **The two readings must agree.** Where the docket text and the order's text
  both read a ruling, a disagreement is triage.
- **A ruling in part is stated, not inferred.** Only "in part", or a grant and
  a denial in one predicate, reads as one; a grant beside a separate denial of
  something else does not.
- **A closure is read from its own leading noun**: a stipulation or notice of
  dismissal naming no party or claim, an order approving one, a final
  approval of a settlement, or a consent judgment. It resolves the final
  disposition as no merits decision, and a motion still open as mooted.
- **Every resolution cites the docket entry it read.**

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
    #: Some claims dismissed with leave and others without.
    mixed = "mixed"
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
    #: The docket text and the order's text, which agreed.
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


@dataclass(frozen=True)
class Reading:
    """What a text says about the ruling on one motion.

    ``conflict`` is set when the text rules on the motion more than once, or
    in a form the rule will not settle (granted "as to" some counts and
    nothing else, say): the caller sends the event to triage.
    """

    ruling: MotionRuling | None
    leave: Leave
    conflict: str | None = None


# --- text --------------------------------------------------------------------

_WS = re.compile(r"\s+")
_ATTACHMENTS = re.compile(r"\(\s*attachments?\s*:.*$", re.IGNORECASE | re.DOTALL)


def _clean(text: str) -> str:
    return _WS.sub(" ", _ATTACHMENTS.sub("", text)).strip()


# --- the motion kind ---------------------------------------------------------

# A motion entry's leading phrase: "MOTION to Dismiss", "Renewed MOTION for
# Summary Judgment". Only the kind the motion word governs counts, so a motion
# for an extension of time about a motion to dismiss is not one.
_MOTION_LEAD = (
    r"^\s*(?:(?:joint|renewed|amended|corrected|cross|consolidated|second|"
    r"supplemental|partial)[-\s]+)*motions?\s+"
)
_MOTION_KIND: Final[tuple[tuple[TrialMoment, re.Pattern[str]], ...]] = (
    (
        TrialMoment.summary_judgment,
        re.compile(_MOTION_LEAD + r"for\s+(?:partial\s+)?summary\s+judgment\b", re.I),
    ),
    (
        TrialMoment.class_certification,
        re.compile(
            _MOTION_LEAD + r"(?:to\s+certify\s+(?:a\s+|the\s+)?class\b|"
            r"for\s+class\s+certification\b|for\s+certification\s+of\s+(?:a\s+|the\s+)?class\b)",
            re.I,
        ),
    ),
    (
        TrialMoment.dismissal,
        re.compile(
            _MOTION_LEAD + r"to\s+dismiss\b(?![^.;]{0,60}\bcounterclaim)",
            re.I,
        ),
    ),
)


def motion_moment(text: str) -> TrialMoment | None:
    """The trial moment a motion entry's leading phrase names, or ``None``."""
    cleaned = _clean(text)
    for moment, pattern in _MOTION_KIND:
        if pattern.search(cleaned):
            return moment
    return None


# --- leave to amend ----------------------------------------------------------

_WITHOUT_LEAVE = re.compile(
    r"\bwithout\s+leave\s+to\s+(?:amend|replead)\b|\bwith\s+prejudice\b|"
    r"\bleave\s+to\s+(?:amend|replead)\s+(?:is\s+|shall\s+be\s+)?denied\b|"
    r"\bdenies\s+leave\s+to\s+(?:amend|replead)\b|\bamendment\s+would\s+be\s+futile\b",
    re.I,
)
_WITH_LEAVE = re.compile(
    r"\bwith\s+leave\s+to\s+(?:amend|replead)\b|"
    r"\bleave\s+to\s+(?:amend|replead)\s+(?:is\s+|shall\s+be\s+)?granted\b|"
    r"\bgrants\s+leave\s+to\s+(?:amend|replead)\b|"
    r"\bmay\s+file\s+(?:a|an)\s+(?:second\s+|third\s+)?amended\s+complaint\b",
    re.I,
)


def read_leave(text: str) -> Leave:
    """The leave to amend a ruling's text states."""
    without = bool(_WITHOUT_LEAVE.search(text))
    with_ = bool(_WITH_LEAVE.search(text))
    if without and with_:
        return Leave.mixed
    if without:
        return Leave.without_leave
    if with_:
        return Leave.with_leave
    return Leave.unstated


# --- ruling verbs ------------------------------------------------------------

# A docket text's ruling verb, longest form first. "Terminating" alone says
# nothing about how, so it is read as a ruling the rule will not settle.
_DOCKET_VERBS: Final[tuple[tuple[str, MotionRuling | None], ...]] = (
    (r"granting\s+in\s+part\s+and\s+denying\s+in\s+part", MotionRuling.granted_in_part),
    (r"denying\s+in\s+part\s+and\s+granting\s+in\s+part", MotionRuling.granted_in_part),
    (r"granting\s+in\s+part", MotionRuling.granted_in_part),
    (r"denying\s+in\s+part", MotionRuling.granted_in_part),
    (r"(?:denying|finding|terminating|deeming)\s+as\s+moot", MotionRuling.mooted),
    (r"mooting", MotionRuling.mooted),
    (r"granting", MotionRuling.granted),
    (r"denying", MotionRuling.denied),
    (r"terminating", None),
)
_DOCKET_VERB = re.compile(
    r"\b(?:" + "|".join(f"(?P<v{i}>{form})" for i, (form, _) in enumerate(_DOCKET_VERBS)) + r")\b",
    re.I,
)
# A run of entry numbers as the direct object of a verb: "45", "[45]",
# "ECF No. 45", "45 and 47", "45, 47".
_NUM = r"(?:(?:ecf|dkt|doc|docket)\.?\s*(?:nos?\.?|#)?\s*|\[\s*|#\s*)?(\d+)\s*\]?"
_OBJECT_RUN = re.compile(
    r"\s*(?:the\s+)?" + _NUM + r"(?:\s*(?:,|and|&)\s*(?:the\s+)?" + _NUM + r")*", re.I
)
_NUMBER = re.compile(r"\d+")


def _object_numbers(text: str, at: int) -> set[int]:
    """The entry numbers directly after position ``at``: a verb's object run."""
    match = _OBJECT_RUN.match(text, at)
    if match is None:
        return set()
    return {int(n) for n in _NUMBER.findall(match.group(0))}


def read_docket_ruling(text: str, number: int) -> Reading:
    """Read a docket text for its ruling on motion ``number``.

    The ruling is the verb whose direct object names ``number``. None naming
    it reads no ruling; two that disagree read a conflict.
    """
    cleaned = _clean(text)
    found: set[MotionRuling | None] = set()
    for match in _DOCKET_VERB.finditer(cleaned):
        if number not in _object_numbers(cleaned, match.end()):
            continue
        index = int(next(k for k, v in match.groupdict().items() if v is not None)[1:])
        found.add(_DOCKET_VERBS[index][1])
    leave = read_leave(cleaned)
    if not found:
        return Reading(None, leave)
    if len(found) > 1 or None in found:
        return Reading(None, leave, "the docket text rules on the motion in more than one way")
    (ruling,) = found
    return Reading(ruling, leave)


# The decretal language of an order. Each clause is read on its own: a clause
# ends at a sentence end (not inside an ECF citation), a semicolon, or a comma
# or "and" that opens a new subject.
_ORDERED = re.compile(r"\bit\s+is\s+(?:hereby\s+)?ordered\b", re.I)
_CONCLUDING = re.compile(
    r"\bfor\s+the\s+(?:foregoing\s+)?reasons\b|"
    r"\bfor\s+(?:these|those|all\s+of\s+the\s+above)\s+reasons\b|\bin\s+conclusion\b|"
    r"\baccordingly,|^\s*conclusion\s*$",
    re.I | re.M,
)


def decretal(order_text: str) -> str | None:
    """An order's decretal language, or ``None`` when it has no ordering anchor.

    It runs from the last "it is ordered" (a later "it is further ordered"
    adds to it) to the end, so a recital quoting an earlier order is left
    out; an order with none runs from its last concluding anchor ("for the
    foregoing reasons", "accordingly", a "Conclusion" heading).
    """
    ordered = list(_ORDERED.finditer(order_text))
    if ordered:
        return order_text[ordered[-1].start() :]
    anchors = list(_CONCLUDING.finditer(order_text))
    if not anchors:
        return None
    return order_text[anchors[-1].start() :]


_CLAUSE_END = re.compile(
    r";|(?<!\bno)(?<!\bnos)(?<!\bdkt)(?<!\becf)(?<!\bdoc)(?<!\bv)(?<!\bu\.s)\.(?:\s+|$)|"
    r",?\s+and\s+(?=(?:\S+\s+){1,8}?(?:is|are|shall)\b)",
    re.I,
)
_REF = re.compile(
    r"(?:\b(?:ecf|dkt|doc|docket)\.?\s*(?:nos?\.?|#)?\s*|\[\s*|#\s*)(\d+(?:\s*(?:,|and|&)\s*\d+)*)",
    re.I,
)
_PASSIVE = re.compile(
    r"\b(?:is|are|be|shall\s+be)\s+(?:hereby\s+)?(?P<p>"
    r"granted\s+in\s+part\s+and\s+denied\s+in\s+part|denied\s+in\s+part\s+and\s+granted\s+in\s+part|"
    r"granted\s+in\s+part|denied\s+in\s+part|denied\s+as\s+moot|(?:moot|mooted)\b|"
    r"granted|denied|withdrawn)\b",
    re.I,
)
_ACTIVE = re.compile(
    r"\b(?:court|it)\s+(?:hereby\s+)?(?P<a>"
    r"grants\s+in\s+part\s+and\s+denies\s+in\s+part|denies\s+in\s+part\s+and\s+grants\s+in\s+part|"
    r"grants\s+in\s+part|denies\s+in\s+part|denies\s+as\s+moot|grants|denies)\b",
    re.I,
)
_GRANT_WORD = re.compile(r"\bgrant(?:ed|s|ing)\b", re.I)
_DENY_WORD = re.compile(r"\bden(?:ied|ies|ying)\b", re.I)
_AS_TO = re.compile(r"^\s*as\s+to\b", re.I)
_LEAVE_PHRASES = re.compile(
    r"\b(?:with(?:out)?\s+)?leave\s+to\s+(?:amend|replead)\b[^.;]*|"
    r"\bleave\s+to\s+(?:amend|replead)\s+(?:is\s+|shall\s+be\s+)?(?:granted|denied)\b",
    re.I,
)


def _ruling_word(phrase: str) -> MotionRuling:
    lowered = _WS.sub(" ", phrase.lower())
    if "in part" in lowered:
        return MotionRuling.granted_in_part
    if "moot" in lowered:
        return MotionRuling.mooted
    if lowered.startswith("withdrawn"):
        return MotionRuling.withdrawn
    return MotionRuling.granted if lowered.startswith("grant") else MotionRuling.denied


def _clauses(text: str) -> list[str]:
    return [clause for clause in _CLAUSE_END.split(text) if clause and clause.strip()]


def _clause_ruling(clause: str, number: int) -> tuple[MotionRuling | None, str | None]:
    """The ruling one clause makes on motion ``number``, and any conflict."""
    refs = [
        m for m in _REF.finditer(clause) if number in {int(n) for n in _NUMBER.findall(m.group(1))}
    ]
    if not refs:
        return None, None
    if len({m.group(1) for m in _REF.finditer(clause)}) > 1:
        return None, "the clause cites several entries"
    stripped = _LEAVE_PHRASES.sub(" ", clause)
    passive = _PASSIVE.search(stripped, refs[0].end())
    active = None
    for candidate in _ACTIVE.finditer(stripped, 0, refs[0].start() + 1):
        active = candidate
    match = passive or active
    if match is None:
        return None, None
    word = match.group("p") if passive else match.group("a")
    ruling = _ruling_word(word)
    tail = stripped[match.end() :]
    if ruling in {MotionRuling.granted, MotionRuling.denied}:
        other = _DENY_WORD if ruling is MotionRuling.granted else _GRANT_WORD
        if other.search(tail):
            return MotionRuling.granted_in_part, None
        if _AS_TO.search(tail):
            return None, f"the order rules {ruling} as to part of the motion only"
    return ruling, None


def read_order_ruling(order_text: str, number: int) -> Reading:
    """Read an order's decretal language for its ruling on motion ``number``."""
    section = decretal(order_text)
    if section is None:
        return Reading(None, Leave.unstated)
    found: set[MotionRuling] = set()
    for clause in _clauses(_clean(section)):
        ruling, conflict = _clause_ruling(clause, number)
        if conflict is not None:
            return Reading(None, read_leave(section), conflict)
        if ruling is not None:
            found.add(ruling)
    leave = read_leave(_clean(section))
    if not found:
        return Reading(None, leave)
    if len(found) > 1:
        return Reading(None, leave, "the order rules on the motion in more than one way")
    (ruling,) = found
    return Reading(ruling, leave)


# --- entries -----------------------------------------------------------------


def _entry_texts(entry: Mapping[str, Any]) -> list[str]:
    """The entry's own description, then its main document's short description."""
    texts = [str(entry.get("description") or "")]
    for document in entry.get("recap_documents") or []:
        if isinstance(document, Mapping) and not document.get("attachment_number"):
            texts.append(str(document.get("description") or ""))
            break
    return [_clean(text) for text in texts if text and text.strip()]


def _entry_text(entry: Mapping[str, Any]) -> str:
    texts = _entry_texts(entry)
    return texts[0] if texts else ""


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


# A docket entry that is the court's disposition, by its leading noun. A
# magistrate judge's recommendation is not a ruling until it is adopted, and
# the adopting order is read in its place.
_COURT_ENTRY = re.compile(
    r"^\s*(?:(?:memorandum|amended|corrected|redacted|sealed|electronic|text|minute|"
    r"paperless|endorsed|stipulated|opinion\s+and|memorandum\s+opinion\s+and)\s+)*"
    r"(?:order|opinion|memorandum\s+(?:opinion|order|decision|and\s+order)|ruling|decision)\b|"
    r"^\s*minute\s+entry\b",
    re.I,
)
_RECOMMENDATION = re.compile(r"\brecommend", re.I)


def _is_court_entry(text: str) -> bool:
    return bool(_COURT_ENTRY.search(text)) and not _RECOMMENDATION.search(text[:80])


# --- closures ----------------------------------------------------------------

# The forms that close the whole action without a merits decision, by their
# leading noun: never a motion asking for one, a response to it, or an order
# denying it.
_CLOSURE_FILING = re.compile(
    r"^\s*(?:joint\s+)?(?:stipulation|notice)\s+(?:and\s+\[?proposed\]?\s+order\s+)?"
    r"(?:of|for)\s+(?:voluntary\s+)?dismissal\b|"
    r"^\s*(?:\[?(?:stipulated|consent|agreed)\]?\s+)(?:final\s+)?judgment\b|"
    r"^\s*(?:(?:final\s+)?(?:order|judgment)\s+(?:granting\s+)?final\s+approval\b|"
    r"final\s+approval\s+order\b|final\s+order\s+and\s+judgment\s+approving\b)",
    re.I,
)
_CLOSURE_ORDER = re.compile(
    r"^\s*(?:\w+\s+){0,2}?order\s+(?:granting|approving|so[-\s]ordering|adopting|entering)\s+"
    r"(?:\d+\s+)?(?:\w+\s+){0,3}?(?:(?:stipulation|notice)\s+(?:of|for)\s+(?:voluntary\s+)?dismissal|"
    r"motion\s+for\s+final\s+approval|final\s+approval)\b",
    re.I,
)
# A closure limited to some parties, counts or claims, which leaves the action
# open. A closure filing that names whom it dismisses is read as partial.
_PARTIAL = re.compile(
    r"\b(?:as\s+to|of|against|dismissing)\s+(?:the\s+)?(?:defendants?|plaintiffs?|"
    r"counter\w*|claims?|counts?|certain|some|party|parties)\b(?!\s+(?:all|and\s+all))|"
    r"\bcount\s+[ivx\d]+\b|'s\s+claims\b|\bpartial\b|\bonly\b|"
    r"\b(?:of|as\s+to)\s+[A-Z][\w.&-]*(?:\s+[A-Z][\w.&-]*)*\s+(?:inc|llc|corp|pbc|ltd|co)\b",
    re.I,
)
_ALL = re.compile(r"\ball\s+(?:claims|parties)\b|\b(?:entire|this|the)\s+(?:action|case)\b", re.I)


def _closes(text: str) -> bool:
    """Whether a docket text closes the whole action without a merits decision."""
    if not (_CLOSURE_FILING.search(text) or _CLOSURE_ORDER.search(text)):
        return False
    return not _PARTIAL.search(_ALL.sub(" ", text))


def find_closure(entries: Iterable[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """The first entry that closes the whole action without a merits decision."""
    for entry in _ordered(entries):
        if _closes(_entry_text(entry)):
            return entry
    return None


# --- resolving a motion ------------------------------------------------------

_WITHDRAWAL_NOTICE = re.compile(
    r"^\s*notice\s+of\s+withdrawal\s+of\s+" + _NUM + r"|^\s*notice\s+withdrawing\s+" + _NUM,
    re.I,
)


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
    resolves it, from its docket text and, where given, its order's decretal
    language; where both read a ruling they must agree. A withdrawal notice
    naming the motion resolves it withdrawn, and a closure of the action
    before any ruling resolves it mooted.
    """
    texts = order_texts or {}
    for entry in _after(list(entries), event.entry_number):
        docket_text = _entry_text(entry)
        cited = cite(entry)
        if _closes(docket_text):
            return MotionResolution(
                event.moment, MotionRuling.mooted, None, cited, Source.docket_text
            )
        notice = _WITHDRAWAL_NOTICE.match(docket_text)
        if notice is not None:
            if event.entry_number in {int(n) for n in notice.groups() if n is not None}:
                return MotionResolution(
                    event.moment, MotionRuling.withdrawn, None, cited, Source.docket_text
                )
            continue
        if not _is_court_entry(docket_text):
            continue
        from_docket = read_docket_ruling(docket_text, event.entry_number)
        order_text = texts.get(cited.entry_id) if cited.entry_id is not None else None
        from_order = (
            read_order_ruling(order_text, event.entry_number)
            if order_text
            else Reading(None, Leave.unstated)
        )
        conflict = from_docket.conflict or from_order.conflict
        if conflict is not None:
            return Unresolved(event.moment, conflict, (cited,))
        if from_docket.ruling is None and from_order.ruling is None:
            continue
        return _settle(event, cited, from_docket, from_order)
    return None


def _settle(
    event: MotionEvent, cited: Citation, from_docket: Reading, from_order: Reading
) -> MotionResolution | Unresolved:
    if from_docket.ruling is not None and from_order.ruling is not None:
        if from_docket.ruling is not from_order.ruling:
            return Unresolved(
                event.moment,
                f"the docket text reads {from_docket.ruling} and the order reads "
                f"{from_order.ruling}",
                (cited,),
            )
        leave = _leave(from_docket.leave, from_order.leave)
        if leave is None:
            return Unresolved(
                event.moment,
                f"the docket text reads leave {from_docket.leave} and the order "
                f"reads leave {from_order.leave}",
                (cited,),
            )
        ruling, source = from_docket.ruling, Source.both
    elif from_order.ruling is not None:
        ruling, leave, source = from_order.ruling, from_order.leave, Source.order_text
    else:
        assert from_docket.ruling is not None
        ruling, leave, source = from_docket.ruling, from_docket.leave, Source.docket_text
    leave_read: Leave | None = None
    if event.moment is TrialMoment.dismissal and ruling in {
        MotionRuling.granted,
        MotionRuling.granted_in_part,
    }:
        leave_read = leave
    return MotionResolution(event.moment, ruling, leave_read, cited, source)


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
    r"^\s*order\s+(?:and|of)\s+final\s+judgment\b",
    re.I,
)
_NOT_FINAL = re.compile(
    r"^\s*(?:(?:clerk'?s|amended)\s+)*(?:partial|default)\b|^\s*(?:clerk'?s\s+)?entry\s+of\s+default\b|"
    r"\brule\s+54\s*\(\s*b\s*\)",
    re.I,
)
_SUPERSEDES = re.compile(
    r"^\s*(?:(?:clerk'?s)\s+)*(?:amended|corrected)\s+(?:final\s+)?judgment\b|"
    r"\bvacat\w*\s+(?:\w+\s+){0,4}?judgment\b",
    re.I,
)
_SIDE = r"(?:the\s+)?(?:(?!(?:against|and|on|in|as)\b)\w+\s+){0,2}?"
_FOR_PLAINTIFF = re.compile(
    rf"\bin\s+favou?r\s+of\s+{_SIDE}plaintiffs?\b|"
    rf"\bjudgment\s+(?:is\s+(?:hereby\s+)?)?(?:entered\s+)?against\s+{_SIDE}defendants?\b",
    re.I,
)
_FOR_DEFENDANT = re.compile(
    rf"\bin\s+favou?r\s+of\s+{_SIDE}defendants?\b|"
    rf"\bjudgment\s+(?:is\s+(?:hereby\s+)?)?(?:entered\s+)?against\s+{_SIDE}plaintiffs?\b|"
    r"\bplaintiffs?\s+(?:shall\s+)?takes?\s+nothing\b",
    re.I,
)


def read_judgment(text: str) -> JudgmentOutcome | None:
    """The side a final judgment's text names, or ``None`` when it names neither.

    Only "in favor of", "judgment against" and "take nothing" name a side; a
    mention of the claims against a party names none.
    """
    cleaned = _clean(text)
    if _closes(cleaned):
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
    merits decision, or a final judgment, read for the side it names from the
    docket text and, where given, the judgment's decretal language; where both
    name a side they must agree. A partial, Rule 54(b) or default judgment is
    passed over. A final judgment that names no side, or that a later entry
    amends or vacates, is :class:`Unresolved`.
    """
    texts = order_texts or {}
    ordered = _ordered(entries)
    for index, entry in enumerate(ordered):
        docket_text = _entry_text(entry)
        cited = cite(entry)
        if _closes(docket_text):
            return JudgmentResolution(JudgmentOutcome.no_merits_decision, cited, Source.docket_text)
        if not _JUDGMENT_ENTRY.search(docket_text) or _NOT_FINAL.search(docket_text):
            continue
        later = [cite(e) for e in ordered[index + 1 :] if _SUPERSEDES.search(_entry_text(e))]
        if later:
            return Unresolved(
                TrialMoment.judgment,
                "a later entry amends or vacates the judgment",
                (cited, *later),
            )
        judgment_text = texts.get(cited.entry_id) if cited.entry_id is not None else None
        return _settle_judgment(cited, read_judgment(docket_text), judgment_text)
    return None


def _settle_judgment(
    cited: Citation, from_docket: JudgmentOutcome | None, judgment_text: str | None
) -> JudgmentResolution | Unresolved:
    from_order = None
    if judgment_text:
        from_order = read_judgment(decretal(judgment_text) or judgment_text)
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
