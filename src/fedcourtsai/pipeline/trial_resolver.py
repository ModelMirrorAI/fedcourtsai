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

- **The docket text decides; the order's text only checks it.** A ruling is
  the CM/ECF form: a ruling verb right after the entry's head, or opening a
  later clause, with the motion's entry number directly after it and naming a
  motion (``ORDER granting 45 Motion to Dismiss``). A verb anywhere else
  (``Order granting 45`` inside a later motion's title) and a number anywhere
  else (``re 45``) name a reference, not a ruling, and an entry that cites no
  entry number never rules. Any qualifier in the ruling's clause that its
  verb does not carry (``as to``, ``only``, ``moot``, ``in part``) is triage.
  Where the order's text is given, its decretal language must not disagree;
  it never resolves an event on its own, and an opinion whose docket text
  states no ruling is triage. Leave is read from the docket text only.
- **A closure is read from its own leading noun and must name nothing it is
  limited to**: a stipulation or notice of dismissal, an order granting one, a
  final approval of a settlement, or a consent judgment, followed by nothing
  but prejudice words, the whole action, a generic filer and the rule. It
  resolves the final disposition as no merits decision, and a motion still
  open as mooted.
- **A final judgment names its side in its docket text**, and is triage when
  a later entry may replace it or it leaves any claim undecided.
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
    #: The docket text, and the order's text, which agreed.
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
# A warning of what follows a failure to amend ("failure to file will result
# in dismissal with prejudice") states a consequence, not the ruling's leave.
_WARNING = re.compile(
    r"\b(?:failure|fail(?:s|ing)?|if\s+(?:plaintiffs?|no|an?)\b)[^.;]{0,200}?"
    r"\b(?:will|shall|may)\s+(?:result\s+in|be)\b[^.;]{0,200}",
    re.I,
)


def read_leave(text: str) -> Leave:
    """The leave to amend a ruling's text states, warnings of a failure to amend struck."""
    body = _WARNING.sub(" ", text)
    without = bool(_WITHOUT_LEAVE.search(body))
    with_ = bool(_WITH_LEAVE.search(body))
    if without and with_:
        return Leave.mixed
    if without:
        return Leave.without_leave
    if with_:
        return Leave.with_leave
    return Leave.unstated


# --- reading a docket text ---------------------------------------------------

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
    r"(?:" + "|".join(f"(?P<v{i}>{form})" for i, (form, _) in enumerate(_DOCKET_VERBS)) + r")\b",
    re.I,
)
# The head of a court entry's docket text, after which its first ruling verb
# must stand: "ORDER granting", "MEMORANDUM OPINION AND ORDER denying", "ORDER
# ADOPTING 58 REPORT AND RECOMMENDATIONS and granting". A verb anywhere else
# ("ORDER granting 70 Motion for Reconsideration of Order granting 45", "The
# Court is inclined toward granting 45") is a reference, not a ruling.
_DOCKET_HEAD = re.compile(
    r"\s*(?:(?:amended|corrected|redacted|sealed|electronic|text|minute|paperless|endorsed)\s+)*"
    r"(?:(?:memorandum\s+)?(?:opinion\s+)?and\s+)?(?:memorandum\s+)?(?:order|opinion|ruling|decision)\b"
    r"(?:\s*[:.,-])?\s*(?:adopting\s+[^;]{0,160}?\s+and\s+)?",
    re.I,
)
# Further rulings in the same text follow a semicolon, a comma or "and".
_NEXT_RULING = re.compile(r"(?:;|,|\s+and)\s*(?:and\s+)?(?=" + _DOCKET_VERB.pattern + r")", re.I)
# A run of entry numbers as the direct object of a verb ("45", "[45]",
# "ECF No. 45", "45 and 47"), which must go straight on to name a motion, so
# "granting 45 days" is not a ruling on entry 45.
_NUM = r"(?:(?:ecf|dkt|doc|docket)\.?\s*(?:nos?\.?|#)?\s*|\[\s*|#\s*)?(\d+)\s*\]?"
_MOTION_PREFIX = (
    r"(?:(?:joint|renewed|amended|corrected|cross|consolidated|first|second|third|supplemental|"
    r"partial|sealed|unopposed|emergency|[\w.]+['\u2019]s?)\s+){0,3}"
)
_OBJECT_RUN = re.compile(
    r"\s*(?:the\s+)?" + _NUM + r"(?:\s*(?:,|and|&)\s*(?:the\s+)?" + _NUM + r")*"
    r"(?=\s*" + _MOTION_PREFIX + r"motions?\b)",
    re.I,
)
_NUMBER = re.compile(r"\d+")
# Where the motion's ruling clause ends: the next ruling, a semicolon, or a
# sentence end not inside an ECF citation. A later motion inside the same
# clause stays in it ("granting 45 Motion and 47 Motion in part"), since the
# rule cannot tell which of the two a qualifier binds.
_PHRASE_END = re.compile(
    r";|(?:,|\s+and)\s*(?:and\s+)?(?=" + _DOCKET_VERB.pattern + r")|"
    r"(?<!\bno)(?<!\bnos)(?<!\bdkt)(?<!\becf)(?<!\bdoc)(?<!\bv)\.(?:\s+|$)",
    re.I,
)
# A word in the motion's ruling clause that could qualify the ruling, or belong to
# the motion's own title ("Motion to Dismiss in Part", "... as Moot"): the
# rule cannot tell which, so any of them is triage, unless the verb itself
# carried it ("denying as moot 45 Motion").
_QUALIFIER = re.compile(
    r"\bmoot\b|\bin\s+part\b|\bas\s+to\b|\bonly\b|\bexcept\b|\bto\s+the\s+extent\b|"
    r"\binsofar\b|\bwith\s+respect\s+to\b|\bpartial(?:ly)?\b",
    re.I,
)


def _object_numbers(text: str, at: int) -> tuple[set[int], int]:
    """The entry numbers directly after position ``at``, and where the run ends."""
    match = _OBJECT_RUN.match(text, at)
    if match is None:
        return set(), at
    return {int(n) for n in _NUMBER.findall(match.group(0))}, match.end()


def _verb_positions(text: str) -> list[re.Match[str]]:
    """The ruling verbs that stand where a ruling does: after the head, or a later clause."""
    head = _DOCKET_HEAD.match(text)
    if head is None:
        return []
    starts = [head.end(), *(m.end() for m in _NEXT_RULING.finditer(text, head.end()))]
    found: list[re.Match[str]] = []
    for start in starts:
        verb = _DOCKET_VERB.match(text, start)
        if verb is not None:
            found.append(verb)
    return found


def read_docket_ruling(text: str, number: int) -> Reading:
    """Read a docket text for its ruling on motion ``number``.

    The ruling is a verb standing where a ruling does (right after the entry's
    head, or after a semicolon or comma that opens another ruling) whose
    direct object names ``number`` and goes straight on to name a motion. A
    word in the motion's own phrase that could qualify the ruling is triage.
    Leave is read from the motion's ruling up to the next one. None naming it
    reads no ruling; two that disagree read a conflict.
    """
    cleaned = _clean(text)
    found: set[MotionRuling] = set()
    leave = Leave.unstated
    verbs = _verb_positions(cleaned)
    for index, verb in enumerate(verbs):
        numbers, end = _object_numbers(cleaned, verb.end())
        if number not in numbers:
            continue
        stop = _PHRASE_END.search(cleaned, end)
        phrase = cleaned[end : stop.start() if stop else len(cleaned)]
        which = int(next(k for k, v in verb.groupdict().items() if v is not None)[1:])
        ruling = _DOCKET_VERBS[which][1]
        if ruling is None:
            return Reading(None, leave, "the docket text terminates the motion without saying how")
        if _QUALIFIER.search(phrase):
            return Reading(None, leave, "the docket text qualifies its ruling on the motion")
        found.add(ruling)
        following = verbs[index + 1].start() if index + 1 < len(verbs) else len(cleaned)
        leave = read_leave(cleaned[verb.start() : following])
    if not found:
        return Reading(None, leave)
    if len(found) > 1:
        return Reading(None, leave, "the docket text rules on the motion in more than one way")
    (ruling,) = found
    return Reading(ruling, leave)


# --- reading an order's text -------------------------------------------------

# The decretal language of an order. An order's text is only ever a check on
# the docket text's reading, never a reading on its own.
_ORDERED = re.compile(
    r"\bit\s+is\s+(?:hereby\s+|therefore\s+|accordingly\s+|so\s+)?ordered\b|"
    r"(?:^|[.:]\s+)ordered\s+that\b",
    re.I | re.M,
)
_CONCLUDING = re.compile(
    r"\bfor\s+the\s+(?:foregoing\s+)?reasons\b|"
    r"\bfor\s+(?:these|those|all\s+of\s+the\s+above)\s+reasons\b|\bin\s+conclusion\b|"
    r"\baccordingly,|^\s*conclusion\s*$",
    re.I | re.M,
)
# Ordering paragraphs this close together are one run of them.
_ORDERING_RUN_GAP: Final = 800


def decretal(order_text: str) -> str | None:
    """An order's decretal language, or ``None`` when it has no ordering anchor.

    It is the final run of "it is ordered" paragraphs, from the first of them
    after the last concluding anchor ("for the foregoing reasons",
    "accordingly", a "Conclusion" heading), else from the first of the last
    run of them, so a recital quoting an earlier order is left out; an order
    with none runs from its last concluding anchor.
    """
    ordered = list(_ORDERED.finditer(order_text))
    anchors = list(_CONCLUDING.finditer(order_text))
    if ordered:
        if anchors:
            after = [m for m in ordered if m.start() > anchors[-1].start()]
            if after:
                return order_text[anchors[-1].start() :]
        start = len(ordered) - 1
        while start > 0 and ordered[start].start() - ordered[start - 1].end() < _ORDERING_RUN_GAP:
            start -= 1
        return order_text[ordered[start].start() :]
    if not anchors:
        return None
    return order_text[anchors[-1].start() :]


_CLAUSE_END = re.compile(
    r";|(?<!\bno)(?<!\bnos)(?<!\bdkt)(?<!\becf)(?<!\bdoc)(?<!\bv)(?<!\bu\.s)\.(?:\s+|$)",
    re.I,
)
_REF = re.compile(
    r"(?:\b(?:ecf|dkt|doc|docket)\.?\s*(?:nos?\.?|#)?\s*|\[\s*|#\s*)(\d+(?:\s*(?:,|and|&)\s*\d+)*)",
    re.I,
)
# The predicate that must follow the motion's own citation directly.
_PASSIVE = re.compile(
    r"\s*[)\]]?\s*,?\s*(?:is|are|shall\s+be)\s+(?:hereby\s+)?(?P<p>"
    r"granted\s+in\s+part\s+and\s+denied\s+in\s+part|denied\s+in\s+part\s+and\s+granted\s+in\s+part|"
    r"granted\s+in\s+part|denied\s+in\s+part|denied\s+as\s+moot|moot|mooted|"
    r"granted|denied|withdrawn)\b",
    re.I,
)
_ACTIVE = re.compile(
    r"\b(?:court|it)\s+(?:hereby\s+)?(?P<a>"
    r"grants\s+in\s+part\s+and\s+denies\s+in\s+part|denies\s+in\s+part\s+and\s+grants\s+in\s+part|"
    r"grants\s+in\s+part|denies\s+in\s+part|denies\s+as\s+moot|grants|denies)\b",
    re.I,
)
# Between an active verb and the citation: the motion itself, by its name.
_ACTIVE_OBJECT = re.compile(
    r"\s*(?:the\s+)?(?:[\w'\u2019.,-]+\s+){0,4}?motions?\s+(?:to|for)\s+[\w\s'\u2019-]{0,40}?[(\[]?\s*$",
    re.I,
)
# A clause that conditions, negates or anticipates a ruling makes none, and
# one whose subject names another matter about the motion is about that
# matter, not the motion.
_HEDGE = re.compile(
    r"\b(?:not|if|why|will|would|may|might|should|could|cannot|unless|until|pending|"
    r"show\s+cause)\b",
    re.I,
)
_OTHER_MATTER = re.compile(
    r"\b(?:argument|hearing|leave|request|exhibit|reply|sur-?reply|opposition|response|"
    r"reconsideration|extension|seal|pages|stay|resolution|ruling|briefing|order\s+granting|"
    r"order\s+denying)\b",
    re.I,
)
_MOTION_WORD = re.compile(r"\bmotions?\b", re.I)
_QUALIFIER_MOOT = re.compile(r"\bmoot\b", re.I)
_GRANT_WORD = re.compile(r"\bgrant(?:ed|s|ing)\b", re.I)
_DENY_WORD = re.compile(r"\bden(?:ied|ies|ying)\b", re.I)
_PART_QUALIFIER = re.compile(
    r"\bas\s+to\b|\bin\s+all\s+other\s+respects\b|\binsofar\b|\bto\s+the\s+extent\b|"
    r"\bwith\s+respect\s+to\b",
    re.I,
)
# An exception or limit after the predicate is triage: "except that" opens a
# ruling on something else as often as on part of the motion.
_EXCEPTION = re.compile(r"\bexcept\b|\bonly\b", re.I)
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


def _clause_ruling(  # noqa: PLR0911 - each return is one form the rule settles or refuses
    clause: str, number: int
) -> tuple[MotionRuling | None, str | None]:
    """The ruling one decretal clause makes on motion ``number``, and any conflict."""
    refs = [
        m for m in _REF.finditer(clause) if number in {int(n) for n in _NUMBER.findall(m.group(1))}
    ]
    if not refs:
        return None, None
    if len({m.group(1) for m in _REF.finditer(clause)}) > 1:
        return None, "an order clause cites several entries"
    if _HEDGE.search(clause):
        return None, None
    stripped = _LEAVE_PHRASES.sub(" ", clause)
    ref = next(
        (
            m
            for m in _REF.finditer(stripped)
            if number in {int(n) for n in _NUMBER.findall(m.group(1))}
        ),
        None,
    )
    if ref is None:
        return None, None
    head = stripped[: ref.start()]
    passive = _PASSIVE.match(stripped, ref.end())
    word: str | None = None
    tail = ""
    if passive is not None:
        if _OTHER_MATTER.search(head) or len(_MOTION_WORD.findall(head)) > 1:
            return None, None
        word, tail = passive.group("p"), stripped[passive.end() :]
    else:
        actives = list(_ACTIVE.finditer(head))
        if actives and _ACTIVE_OBJECT.fullmatch(head, actives[-1].end()):
            between = head[actives[-1].end() :]
            if _OTHER_MATTER.search(between) or len(_MOTION_WORD.findall(between)) > 1:
                return None, None
            word, tail = actives[-1].group("a"), stripped[ref.end() :]
    if word is None:
        return None, None
    return _qualify_tail(_ruling_word(word), tail)


def _qualify_tail(ruling: MotionRuling, tail: str) -> tuple[MotionRuling | None, str | None]:
    """A decretal ruling read with what follows its predicate in the same clause."""
    if ruling not in {MotionRuling.granted, MotionRuling.denied}:
        return ruling, None
    if _EXCEPTION.search(tail):
        return None, f"the order rules {ruling} with an exception or a limit"
    if _PART_QUALIFIER.search(tail):
        other = _DENY_WORD if ruling is MotionRuling.granted else _GRANT_WORD
        if other.search(tail):
            return MotionRuling.granted_in_part, None
        return None, f"the order rules {ruling} on part of the motion only"
    if _QUALIFIER_MOOT.search(tail):
        return MotionRuling.mooted, None
    return ruling, None


def read_order_ruling(order_text: str, number: int) -> Reading:
    """Read an order's decretal language for its ruling on motion ``number``.

    Leave is not read from an order's text: a decretal section can rule on
    several motions with different leave, and the order only checks the
    docket text's ruling.
    """
    section = decretal(order_text)
    if section is None:
        return Reading(None, Leave.unstated)
    cleaned = _clean(section)
    found: set[MotionRuling] = set()
    for clause in _CLAUSE_END.split(cleaned):
        if not clause or not clause.strip():
            continue
        ruling, conflict = _clause_ruling(clause, number)
        if conflict is not None:
            return Reading(None, Leave.unstated, conflict)
        if ruling is not None:
            found.add(ruling)
    if not found:
        return Reading(None, Leave.unstated)
    if len(found) > 1:
        return Reading(None, Leave.unstated, "the order rules on the motion in more than one way")
    (ruling,) = found
    return Reading(ruling, Leave.unstated)


# --- entries -----------------------------------------------------------------


def _entry_text(entry: Mapping[str, Any]) -> str:
    """The entry's own description, cut before PACER's attachment list."""
    return _clean(str(entry.get("description") or ""))


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
# magistrate judge's recommendation is not a ruling; the order adopting one is.
_COURT_ENTRY = re.compile(
    r"^\s*(?:(?:amended|corrected|redacted|sealed|electronic|text|minute|"
    r"paperless|endorsed|stipulated)\s+)*(?:(?:memorandum\s+)?opinion\s+and\s+)?"
    r"(?:order|opinion|memorandum\s+(?:opinion|order|decision|and\s+order)|ruling|decision)\b|"
    r"^\s*minute\s+entry\b",
    re.I,
)
# An opinion, as against a bare order: an entry of this kind that cites the
# motion is almost always its ruling, so one the docket text cannot read is
# triage rather than passed over.
_OPINION_ENTRY = re.compile(
    r"^\s*(?:(?:amended|corrected|redacted|sealed)\s+)*(?:memorandum\s+)?(?:opinion|decision)\b|"
    r"^\s*(?:memorandum|opinion)\s+and\s+order\b|^\s*order\s+and\s+opinion\b",
    re.I,
)
_RECOMMENDATION = re.compile(r"\brecommend", re.I)
_ADOPTING = re.compile(r"^\s*(?:\w+\s+)?order\s+adopting\b", re.I)


# The court of appeals' orders and mandates land on the district docket too,
# and their entry numbers are the appeal's own.
_APPELLATE = re.compile(r"\busca\b|\bcourt\s+of\s+appeals\b|\bmandate\b", re.I)


def _is_court_entry(text: str) -> bool:
    if not _COURT_ENTRY.search(text) or _APPELLATE.search(text):
        return False
    return bool(_ADOPTING.search(text)) or not _RECOMMENDATION.search(text[:80])


# --- closures ----------------------------------------------------------------

# The forms that close the whole action without a merits decision, by their
# leading noun: never a motion asking for one, a response to it, or an order
# denying it.
_SETTLEMENT = r"(?:the\s+)?(?:proposed\s+)?(?:class\s+(?:action\s+)?)?settlement"
_CLOSURE_HEADS = re.compile(
    r"^\s*(?:joint\s+)?(?:stipulation|notice)\s+(?:and\s+\[?proposed\]?\s+order\s+)?"
    r"(?:of|for)\s+(?:voluntary\s+)?dismissal\b|"
    r"^\s*\[?(?:stipulated|consent|agreed)\]?\s+(?:final\s+)?judgment\b|"
    r"^\s*final\s+approval\s+order\b|"
    rf"^\s*(?:final\s+)?(?:order|judgment)\s+granting\s+final\s+approval\s+of\s+{_SETTLEMENT}\b|"
    r"^\s*(?:\w+\s+)?order\s+(?:granting|approving|so[-\s]ordering|entering)\s+(?:\[?\d+\]?\s+)?"
    r"(?:the\s+)?(?:joint\s+)?(?:stipulation|notice)\s+(?:of|for)\s+(?:voluntary\s+)?dismissal\b|"
    r"^\s*(?:\w+\s+)?order\s+granting\s+(?:\[?\d+\]?\s+)?(?:joint\s+|unopposed\s+)?motion\s+for\s+"
    rf"final\s+approval\s+of\s+{_SETTLEMENT}\b",
    re.I,
)
# What may follow a closure's head for it to close the whole action: prejudice
# words, the whole action or all claims, who filed it, the rule it rests on,
# and the clerk's trailer. Anything else (a party, a claim, a cause of action,
# "re:", an appeal, a related case) leaves it unread.
# Each piece is atomic and the run possessive, so a tail that fails fails in
# linear time.
_CLOSURE_TAIL = re.compile(
    r"(?>\s+|[,.;:]|"
    r"with(?:out)?\s+prejudice\b|"
    r"of\s+(?:the\s+|this\s+)?(?:entire\s+)?(?:action|case|matter)\b|"
    r"(?:of|as\s+to)\s+all\s+(?:claims|parties|defendants|counts)(?:\s+and\s+(?:counterclaims|parties))?\b|"
    r"(?:filed\s+)?by\s+(?:all\s+(?:parties|plaintiffs|defendants)|the\s+parties|plaintiffs?|defendants?)\b|"
    r"pursuant\s+to\s+(?:fed\.?\s*r\.?\s*civ\.?\s*p\.?\s*|federal\s+rule\s+of\s+civil\s+procedure\s+|rule\s+)?"
    r"41\S*|under\s+rule\s+41\S*|"
    r"and\s+(?:final\s+)?judgment\b|"
    r"signed\s+by\s+.*$|\(\s*entered:.*$|\(\s*\w{2,4}\s*\)|"
    r"\(\s*[a-z.'\u2019-]+,\s*[a-z.'\u2019 -]+\)"
    r")*+",
    re.I,
)


def _closes(text: str) -> bool:
    """Whether a docket text closes the whole action without a merits decision."""
    head = _CLOSURE_HEADS.search(text)
    if head is None:
        return False
    return _CLOSURE_TAIL.fullmatch(text, head.end()) is not None


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
_LIMITED = re.compile(r"\bas\s+to\b|\bonly\b|\bin\s+part\b|\bpartial\b", re.I)
# One movant's withdrawal of a joint motion leaves the others' standing.
_JOINT = re.compile(r"\bjoint\b", re.I)


def resolve_motion(  # noqa: PLR0911 - each return is one way a motion resolves
    event: MotionEvent,
    entries: Iterable[Mapping[str, Any]],
    *,
    order_texts: Mapping[int, str] | None = None,
) -> MotionResolution | Unresolved | None:
    """How motion ``event`` resolved on this docket, or ``None`` while it is open.

    ``entries`` are the docket's entries, in any order. ``order_texts`` maps an
    entry id to the text of the order or opinion that entry carries, where the
    caller has it. The first court entry after the motion whose docket text
    rules on it resolves it; the order's decretal language, where given, must
    not disagree. An opinion that cites the motion with no ruling the docket
    text can read is triage. A withdrawal notice naming the motion, with no
    limit, resolves it withdrawn, and a closure of the action before any
    ruling resolves it mooted.
    """
    texts = order_texts or {}
    listed = list(entries)
    own = next((e for e in listed if _number(e) == event.entry_number), None)
    joint = own is not None and bool(_JOINT.search(_entry_text(own)))
    for entry in _after(listed, event.entry_number):
        docket_text = _entry_text(entry)
        cited = cite(entry)
        if _closes(docket_text):
            return MotionResolution(
                event.moment, MotionRuling.mooted, None, cited, Source.docket_text
            )
        notice = _WITHDRAWAL_NOTICE.match(docket_text)
        if notice is not None:
            named = {int(n) for n in notice.groups() if n is not None}
            if event.entry_number in named and not joint and not _LIMITED.search(docket_text):
                return MotionResolution(
                    event.moment, MotionRuling.withdrawn, None, cited, Source.docket_text
                )
            continue
        if not _is_court_entry(docket_text):
            continue
        from_docket = read_docket_ruling(docket_text, event.entry_number)
        if from_docket.conflict is not None:
            return Unresolved(event.moment, from_docket.conflict, (cited,))
        if from_docket.ruling is None:
            if _OPINION_ENTRY.search(docket_text) and _cites(docket_text, event.entry_number):
                return Unresolved(
                    event.moment,
                    "an opinion cites the motion and its docket text states no ruling",
                    (cited,),
                )
            continue
        order_text = texts.get(cited.entry_id) if cited.entry_id is not None else None
        from_order = (
            read_order_ruling(order_text, event.entry_number)
            if order_text
            else Reading(None, Leave.unstated)
        )
        if from_order.conflict is not None:
            return Unresolved(event.moment, from_order.conflict, (cited,))
        return _settle(event, cited, from_docket, from_order)
    return None


def _cites(text: str, number: int) -> bool:
    """Whether a docket text cites entry ``number`` (``45 Motion``, ``re 45``, ``[45]``)."""
    return bool(
        re.search(
            rf"(?:\b(?:ecf|dkt|doc|docket)\.?\s*(?:nos?\.?|#)?\s*|\[\s*|#\s*|\bre:?\s+)"
            rf"{number}\b|\b{number}\s+(?:[\w'\u2019]+\s+){{0,3}}?motion",
            text,
            re.I,
        )
    )


def _settle(
    event: MotionEvent, cited: Citation, from_docket: Reading, from_order: Reading
) -> MotionResolution | Unresolved:
    assert from_docket.ruling is not None
    ruling, source = from_docket.ruling, Source.docket_text
    if from_order.ruling is not None:
        if from_order.ruling is not ruling:
            return Unresolved(
                event.moment,
                f"the docket text reads {ruling} and the order reads {from_order.ruling}",
                (cited,),
            )
        source = Source.both
    leave: Leave | None = None
    if event.moment is TrialMoment.dismissal and ruling in {
        MotionRuling.granted,
        MotionRuling.granted_in_part,
    }:
        leave = from_docket.leave
    return MotionResolution(event.moment, ruling, leave, cited, source)


# --- the final disposition ---------------------------------------------------

_JUDGMENT_ENTRY = re.compile(
    r"^\s*(?:(?:final|amended|clerk'?s|corrected|partial|default)\s+)*judgment\b|"
    r"^\s*order\s+(?:and|of)\s+final\s+judgment\b",
    re.I,
)
# Not the final disposition: a partial, Rule 54(b) or default judgment (read
# from the entry's first sentence), a judgment for costs or fees (read from its
# head), or the court of appeals' judgment.
_FIRST_SENTENCE = re.compile(r"^[^.;]*")
_NOT_FINAL_LEAD = re.compile(r"\bpartial\b|\bdefault\b", re.I)
# A judgment under Rule 54(b) or Rule 55 anywhere in its text is not the
# action's final judgment ("pursuant to Fed. R. Civ. P. 55(b)(1)").
_NOT_FINAL_RULE = re.compile(
    r"\brule\s+54\s*\(\s*b\s*\)|\b54\s*\(\s*b\s*\)|\b55\s*\(\s*[ab]\s*\)|\brule\s+55\b", re.I
)
_COSTS_HEAD = re.compile(
    r"^\s*(?:clerk'?s\s+)?(?:judgment\s+(?:taxing|for|on)\s+(?:the\s+)?(?:costs|(?:attorneys?['\u2019]?\s+)?fees)|"
    r"(?:bill|taxation)\s+of\s+costs)\b",
    re.I,
)
# A judgment the rule will not read for a side: one limited to some parties or
# claims, or one on a counterclaim, crossclaim or third-party claim.
_JUDGMENT_TRIAGE = re.compile(
    r"\bas\s+to\b|\bcounter-?claims?\b|\bcross-?claims?\b|\bthird[-\s]party\b|"
    r"\bexcept\b|\bremand\w*|\bremains?\s+pending\b|\bremaining\b|"
    r"\bdefendants?\s+(?:shall\s+)?takes?\s+nothing\b",
    re.I,
)
# A later entry that may undo or replace the judgment.
_SUPERSEDES = re.compile(
    r"^\s*(?:(?:clerk'?s)\s+)*(?:amended|corrected)\s+(?:final\s+)?judgment\b|"
    r"\bvacat\w*\s+(?:\w+\s+){0,4}?judgment\b|\bset\s+aside\b|\bnew\s+trial\b|"
    r"\bjudgment\s+as\s+a\s+matter\s+of\s+law\b|\brule\s+(?:59|60)\b|"
    r"\balter\s+or\s+amend\b|\bremittitur\b|\bnotwithstanding\s+the\s+verdict\b|\bjnov\b",
    re.I,
)
_SIDE = r"(?:the\s+)?(?:(?!(?:against|and|on|in|as)\b)[\w.,&-]+\s+){0,2}?"
_FAVOR_PLAINTIFF = re.compile(rf"\bin\s+favou?r\s+of\s+{_SIDE}plaintiffs?\b(?!['\u2019])", re.I)
_FAVOR_DEFENDANT = re.compile(rf"\bin\s+favou?r\s+of\s+{_SIDE}defendants?\b(?!['\u2019])", re.I)
_AGAINST_DEFENDANT = re.compile(
    rf"\bjudgment\s+(?:is\s+(?:hereby\s+)?)?(?:entered\s+)?against\s+{_SIDE}defendants?\b(?!['\u2019])",
    re.I,
)
_AGAINST_PLAINTIFF = re.compile(
    rf"\bjudgment\s+(?:is\s+(?:hereby\s+)?)?(?:entered\s+)?against\s+{_SIDE}plaintiffs?\b(?!['\u2019])|"
    r"\bplaintiffs?\s+(?:shall\s+)?takes?\s+nothing\b",
    re.I,
)


def _judgment_reading(  # noqa: PLR0911 - each return is one reading of a side
    text: str,
) -> tuple[JudgmentOutcome | None, str | None]:
    cleaned = _clean(text)
    if _closes(cleaned):
        return JudgmentOutcome.no_merits_decision, None
    if _JUDGMENT_TRIAGE.search(cleaned):
        return None, "the judgment is limited to some parties or claims, or a counterclaim"
    favor_p = bool(_FAVOR_PLAINTIFF.search(cleaned))
    favor_d = bool(_FAVOR_DEFENDANT.search(cleaned))
    for_p = favor_p or bool(_AGAINST_DEFENDANT.search(cleaned))
    for_d = favor_d or bool(_AGAINST_PLAINTIFF.search(cleaned))
    if for_p and for_d:
        if favor_p and favor_d:
            return JudgmentOutcome.mixed, None
        return None, "the judgment names both sides in different forms"
    if for_p:
        return JudgmentOutcome.plaintiff, None
    if for_d:
        return JudgmentOutcome.defendant, None
    return None, None


def read_judgment(text: str) -> JudgmentOutcome | None:
    """The side a final judgment's text names, or ``None`` when it names none it can read.

    Only "in favor of", "judgment against" and "take nothing" name a side; a
    mention of the claims against a party names none, and mixed needs both
    sides named "in favor of".
    """
    return _judgment_reading(text)[0]


def resolve_judgment(
    entries: Iterable[Mapping[str, Any]],
    *,
    order_texts: Mapping[int, str] | None = None,
) -> JudgmentResolution | Unresolved | None:
    """How the case's final disposition resolved, or ``None`` while it is open.

    The first entry that closes the action decides it: a closure without a
    merits decision, or a final judgment read for the side its docket text
    names, which the judgment's decretal language, where given, must not
    contradict. A partial, Rule 54(b), default or appellate judgment is passed
    over. A final judgment whose docket text names no side, or that a later
    entry amends, vacates or sets aside, is :class:`Unresolved`.
    """
    texts = order_texts or {}
    ordered = _ordered(entries)
    passed: list[Citation] = []
    for index, entry in enumerate(ordered):
        docket_text = _entry_text(entry)
        cited = cite(entry)
        if _closes(docket_text):
            if passed:
                return Unresolved(
                    TrialMoment.judgment,
                    "a closure follows a judgment the rule passed over",
                    (*passed, cited),
                )
            return JudgmentResolution(JudgmentOutcome.no_merits_decision, cited, Source.docket_text)
        if not _JUDGMENT_ENTRY.search(docket_text) or _APPELLATE.search(docket_text):
            continue
        lead = _FIRST_SENTENCE.match(docket_text)
        if (
            (lead and _NOT_FINAL_LEAD.search(lead.group(0)))
            or _NOT_FINAL_RULE.search(docket_text)
            or _COSTS_HEAD.search(docket_text)
        ):
            passed.append(cited)
            continue
        later = [
            cite(e)
            for e in ordered[index + 1 :]
            if _SUPERSEDES.search(_entry_text(e)) or _JUDGMENT_ENTRY.search(_entry_text(e))
        ]
        if later:
            return Unresolved(
                TrialMoment.judgment,
                "a later entry may amend, vacate, set aside or replace the judgment",
                (cited, *later),
            )
        judgment_text = texts.get(cited.entry_id) if cited.entry_id is not None else None
        return _settle_judgment(cited, docket_text, judgment_text)
    return None


def _settle_judgment(
    cited: Citation, docket_text: str, judgment_text: str | None
) -> JudgmentResolution | Unresolved:
    from_docket, conflict = _judgment_reading(docket_text)
    if conflict is not None:
        return Unresolved(TrialMoment.judgment, conflict, (cited,))
    if from_docket is None:
        return Unresolved(
            TrialMoment.judgment, "a final judgment's docket text names no side", (cited,)
        )
    if not judgment_text:
        return JudgmentResolution(from_docket, cited, Source.docket_text)
    from_order, order_conflict = _judgment_reading(decretal(judgment_text) or judgment_text)
    if order_conflict is not None or (from_order is not None and from_order is not from_docket):
        return Unresolved(
            TrialMoment.judgment,
            order_conflict
            or f"the docket text reads {from_docket} and the judgment reads {from_order}",
            (cited,),
        )
    return JudgmentResolution(from_docket, cited, Source.both if from_order else Source.docket_text)
