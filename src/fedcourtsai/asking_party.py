"""Who is asking the Court to act, and what each action open to it does for that side.

Display-only: the big-case board publishes it beside each row's forecast so a
reader who sees "granted 30%" can tell whom a grant helps (``metrics/README.md``).
Nothing predicts, evaluates or scores on it, and nothing reads it back.

**The asking side is the first-named side of the caption.** The Court's docket
labels its sides — Petitioner, Applicant, Appellant, Plaintiff, Movant on one, Respondent,
Appellee, Defendant on the other — and its captions name the labeled asking side
first. The board has no committed copy of those labels apart from the caption
itself (the docket's structured petitioner and respondent titles live in the
corpus, which the board does not read), so where a caption still carries a label
the rule reads it, and declines if the label contradicts the order; where it
carries none, the order stands on its own.

The party names are the short-caption rule's (:func:`fedcourtsai.short_caption.short_party`),
so a side has a name here exactly where the board's ``short_caption`` would.

Like that rule, this one is conservative because its two failures are not equal:
a ``None`` costs a reader nothing (the site falls back to the case summary or
shows nothing), while a line naming the wrong side as the one asking tells the
reader the opposite of what a ruling does. So it declines (:data:`AskingDecline`)
wherever the caption cannot carry the answer:

- any ``In re`` caption (an extraordinary writ — mandamus, prohibition, habeas),
  which names no second side;
- a caption whose labels contradict its order, or that labels a side as a
  cross-petitioner;
- a caption either side of which the short-caption rule cannot name, or whose
  two sides shorten to the same name (a line could not tell them apart);
- a possible **original-jurisdiction** case — an original docket number, or,
  where the docket number is unknown, a caption whose both sides are sovereigns
  (a State or the United States), the shape an original action takes. A
  Term-form petition number or an application number is never original, so a
  sovereign pair on one of those is read like any other caption;
- a probable **cross-petition** — the caller's finding that another committed
  case names the same two parties in reverse order within a Term and a half
  (:data:`CROSS_PETITION_WINDOW_DAYS`); both sides are asking, so neither is
  "the" asking side;
- a stage it has no lines for.

What the rule cannot see is a party that supports the other side — the federal
government as respondent agreeing with the petitioner. The lines are worded about
what each action does, never about which side "wins" beyond that, so they stay
true there too. Nor does it know who stands behind a name: the names are the
caption's short names, so an official sued in that capacity appears by surname,
not as the government.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final, Literal

from .pipeline.caption import STATE_NAMES
from .schemas import AskingDeclineReason, Stage
from .short_caption import AGENCY_ACRONYMS, CORPORATE_FORMS, short_party

#: Why a row carries no asking side. One value per rule branch, so a row's
#: decline is checkable against the rule without re-running it.
AskingDecline = AskingDeclineReason

#: An action the Court can take at a stage, spelled as the outcome vocabularies
#: spell it (``Disposition`` for a petition or application, ``Judgment`` for the
#: merits).
OutcomeAction = Literal["granted", "denied", "reversed", "affirmed", "vacated"]

#: Which side of the stage's forecast binary an action falls on — what a line
#: pairs with. A petition or application forecast is P(granted), so `granted`
#: pairs with it and `not-granted` with its complement. A merits forecast is
#: P(judgment below disturbed), which pools reversal, vacatur and the mixed
#: in-part outcome, so `reversed` and `vacated` are both on the `disturbed` side
#: and `affirmed` on the `undisturbed` one: a merits line never pairs one-to-one
#: with the headline number.
OutcomeSide = Literal["granted", "not-granted", "disturbed", "undisturbed"]

#: How close in docket dates two mirrored captions must be to read as a
#: cross-petition pair. A cross-petition is due within 30 days of the petition's
#: docketing (Rule 12.5), and a case's later dated moments — the CVSG, the grant,
#: the briefing — fall within about a Term of that, so a mirror inside a Term and a
#: half is read as a pair; the same two parties meeting again years later are not.
CROSS_PETITION_WINDOW_DAYS: Final = 548

_ASKING_LABELS: Final = frozenset(
    {
        "applicant",
        "applicants",
        "appellant",
        "appellants",
        "movant",
        "movants",
        "petitioner",
        "petitioners",
        "plaintiff",
        "plaintiffs",
    }
)
_ANSWERING_LABELS: Final = frozenset(
    {"appellee", "appellees", "defendant", "defendants", "respondent", "respondents"}
)
_ROLE_LABELS: Final = _ASKING_LABELS | _ANSWERING_LABELS

#: A name whose first or last word is one of these reads with "the" in a sentence
#: ("the Department of Labor", "the Republican National Committee"); a person, a
#: company, a State or a place-named county does not.
_ARTICLE_NOUNS: Final = frozenset(
    {
        "Administration",
        "Agency",
        "Alliance",
        "Association",
        "Bar",
        "Board",
        "Bureau",
        "Center",
        "Coalition",
        "College",
        "Colony",
        "Commission",
        "Committee",
        "Congress",
        "Council",
        "Court",
        "Department",
        "District",
        "Foundation",
        "Institute",
        "Nation",
        "Office",
        "Program",
        "Service",
        "Society",
        "Tribe",
        "Tribes",
        "Union",
        "University",
    }
)

_IN_RE_RE: Final = re.compile(r"^In\s+re\b", re.IGNORECASE)
_ORIGINAL_DOCKET_RE: Final = re.compile(r"^\d+\s*O\s*\d+$|\bOrig\b", re.IGNORECASE)
#: A Term-form petition number or an application number: never an original docket.
_NOT_ORIGINAL_RE: Final = re.compile(r"^\d{2}(?:-|A)\d+$", re.IGNORECASE)
#: Adjectives that lead an institution's name ("National Association …").
_INSTITUTION_LEADS: Final = frozenset({"American", "National"})
_ACRONYMS: Final = frozenset(AGENCY_ACRONYMS.values())
_PARENTHETICAL_RE: Final = re.compile(r"\s*\([^)]*\)")
_SOVEREIGNS: Final = frozenset({"United States", *STATE_NAMES})


@dataclass(frozen=True)
class AskingSides:
    """The side asking the Court to act and the side answering, by short name."""

    asking: str
    other: str


def caption_heads(caption: str | None) -> tuple[str, str] | None:
    """Each side's first-named party as a comparison key, or ``None``.

    The key a mirrored-caption search matches on: the text before each side's
    first comma, stripped of a parenthetical, a leading ``The`` and a trailing
    role label, whitespace-collapsed and case-folded. Deliberately the whole
    first name rather than its short form, so two different people who share a
    surname do not read as the same party.
    """
    text = " ".join((caption or "").split())
    if not text or _IN_RE_RE.match(text):
        return None
    sides = text.split(" v. ")
    if len(sides) != 2:
        return None
    left, right = (_head(side) for side in sides)
    return (left, right) if left and right else None


def _head(side: str) -> str:
    name = _PARENTHETICAL_RE.sub("", side.split(",", maxsplit=1)[0]).strip()
    words = name.split()
    while words and words[-1].casefold().strip(".") in _ROLE_LABELS:
        words.pop()
    if words and words[0] == "The":
        words = words[1:]
    return " ".join(words).casefold()


def asking_sides(  # noqa: PLR0911 - one return per decline branch
    caption: str | None,
    *,
    court_id: str,
    docket_number: str | None,
    stage: Stage | None,
    mirrored: bool,
) -> AskingSides | AskingDecline:
    """The row's asking and answering sides, or why the rule declines.

    ``mirrored`` is the caller's cross-petition finding (it needs the whole
    committed ledger, which this pure function does not read).
    """
    text = " ".join((caption or "").split())
    decline: AskingDecline | None = None
    if not text:
        decline = "no_caption"
    elif court_id != "scotus":
        decline = "not_scotus"
    elif _IN_RE_RE.match(text):
        decline = "in_re"
    sides = text.split(" v. ")
    if decline is None and len(sides) != 2:
        decline = "not_two_sided"
    if decline is not None:
        return decline
    left, right = sides
    left_label, right_label = _label(left), _label(right)
    if (
        left_label in _ANSWERING_LABELS
        or right_label in _ASKING_LABELS
        or left_label.startswith("cross-")
        or right_label.startswith("cross-")
    ):
        return "docket_labels"
    asking, other = short_party(left), short_party(right)
    if asking is None or other is None or asking == other:
        return "short_form"
    if _original(docket_number, asking, other):
        return "original_jurisdiction"
    if mirrored:
        return "cross_petition"
    if stage not in _LINES:
        return "stage"
    return AskingSides(asking=asking, other=other)


def _label(side: str) -> str:
    """The side's trailing role label, lower-cased, or the empty string."""
    words = side.rstrip(" ,.").split()
    last = words[-1].casefold() if words else ""
    return last if last in _ROLE_LABELS or last.startswith("cross-") else ""


def _original(docket_number: str | None, asking: str, other: str) -> bool:
    """Whether the case is, or may be, an original action.

    An original docket number says so outright. A Term-form petition number or
    an application number says it is not, whoever the parties are. Only where
    the docket number is unknown (or of neither form) does a caption whose both
    sides are sovereigns — the shape of an original action — decline on its own.
    """
    number = (docket_number or "").strip()
    if number and _ORIGINAL_DOCKET_RE.search(number):
        return True
    if _NOT_ORIGINAL_RE.match(number):
        return False
    return asking in _SOVEREIGNS and other in _SOVEREIGNS


def outcome_lines(stage: Stage, sides: AskingSides) -> list[tuple[OutcomeAction, OutcomeSide, str]]:
    """One plain-language line per action open at ``stage``, filled with the names.

    Each line carries the side of the stage's forecast binary its action falls on
    (:data:`OutcomeSide`). Consequences only, never likelihood, and each action
    gets a line of the same weight: the lines say what an action does for the
    sides, not how likely it is.
    """
    return [(action, side, template(sides)) for action, side, template in _LINES[stage]]


def _name(party: str, *, start: bool = False) -> str:
    """``party`` as a sentence names it: with "the" where its form takes one.

    Display-grade, not grammar-complete: an institution noun at either end, a
    leading "National"/"American" before one, an agency acronym, the United
    States, or an "of" phrase in a name that is not a company's.
    """
    words = party.split()
    corporate = any(word in CORPORATE_FORMS for word in words)
    article = (
        party.startswith("United States")
        or party in _ACRONYMS
        or (" of " in party and not corporate)
        or words[0] in _ARTICLE_NOUNS
        or words[-1] in _ARTICLE_NOUNS
        or (len(words) > 1 and words[0] in _INSTITUTION_LEADS and words[1] in _ARTICLE_NOUNS)
    )
    if not article:
        return party
    return f"{'The' if start else 'the'} {party}"


def _possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def _cert_granted(sides: AskingSides) -> str:
    return (
        f"The Court takes up {_possessive(_name(sides.asking))} case; "
        "a grant alone decides nothing yet about who is right."
    )


def _cert_denied(sides: AskingSides) -> str:
    return (
        f"{_possessive(_name(sides.asking, start=True))} petition ends and the lower "
        "court's decision stands; that is not a ruling that the lower court was right."
    )


def _interim_granted(sides: AskingSides) -> str:
    return (
        f"{_name(sides.asking, start=True)} gets the relief requested, for now; "
        "the case continues in the lower courts."
    )


def _interim_denied(sides: AskingSides) -> str:
    return (
        f"{_name(sides.asking, start=True)} does not get the relief requested, for now; "
        "things stay as the lower courts left them while the case continues."
    )


def _merits_reversed(sides: AskingSides) -> str:
    return (
        f"{_name(sides.asking, start=True)} wins in the Court; the lower court's "
        "decision is overturned, and any remaining issues go back to it."
    )


def _merits_affirmed(sides: AskingSides) -> str:
    return (
        f"{_name(sides.other, start=True)} wins in the Court; the lower court's decision is upheld."
    )


def _merits_vacated(_sides: AskingSides) -> str:
    return (
        "The lower court's decision is set aside and the case goes back to it, "
        "without the Court deciding it for either side."
    )


_Line = tuple[OutcomeAction, OutcomeSide, Callable[[AskingSides], str]]

#: The actions open at each stage, in the order a reader meets them, each with
#: its forecast side and its line. A petition and an application are decided
#: granted or denied; a merits case reversed, affirmed or vacated. The mixed
#: in-part outcome is on the `disturbed` side but gets no line of its own.
_LINES: Final[Mapping[Stage, tuple[_Line, ...]]] = {
    Stage.cert: (
        ("granted", "granted", _cert_granted),
        ("denied", "not-granted", _cert_denied),
    ),
    Stage.interim: (
        ("granted", "granted", _interim_granted),
        ("denied", "not-granted", _interim_denied),
    ),
    Stage.merits: (
        ("reversed", "disturbed", _merits_reversed),
        ("affirmed", "undisturbed", _merits_affirmed),
        ("vacated", "disturbed", _merits_vacated),
    ),
}
