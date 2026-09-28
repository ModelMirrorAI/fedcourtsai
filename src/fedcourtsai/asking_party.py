"""Who is asking the Court to act, and what each action open to it does for that side.

Display-only: the big-case board publishes it beside each row's forecast so a
reader who sees "granted 30%" can tell whom a grant helps (``metrics/README.md``).
Nothing predicts, evaluates or scores on it, and nothing reads it back.

**The asking side is the first-named side of the caption.** The Court's docket
labels its sides — Petitioner, Applicant, Appellant, Plaintiff on one, Respondent,
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

- an ``In re`` caption, which names no second side;
- a caption whose labels contradict its order, or that labels a side as a
  cross-petitioner;
- a caption either side of which the short-caption rule cannot name, or whose
  two sides shorten to the same name (a line could not tell them apart);
- a possible **original-jurisdiction** case — an original docket number, or a
  caption whose both sides are sovereigns (a State or the United States) on a
  docket that is not a Term-form petition number, the shape an original action
  takes. A petition or application between two sovereigns on an application or
  unknown docket number declines with it;
- a probable **cross-petition** — the caller's finding that another committed
  case names the same two parties in reverse order within a Term and a half
  (:data:`CROSS_PETITION_WINDOW_DAYS`); both sides are asking, so neither is
  "the" asking side;
- a stage it has no lines for.

What the rule cannot see is a party that supports the other side — the federal
government as respondent agreeing with the petitioner. The lines are worded about
what each action does, never about which side "wins" beyond that, so they stay
true there too.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final, Literal

from .pipeline.caption import STATE_NAMES
from .schemas import AskingDeclineReason, Stage
from .short_caption import short_party

#: Why a row carries no asking side. One value per rule branch, so a row's
#: decline is checkable against the rule without re-running it.
AskingDecline = AskingDeclineReason

#: An action the Court can take at a stage, spelled as the outcome vocabularies
#: spell it (``Disposition`` for a petition or application, ``JudgmentDisposition``
#: for the merits), so a line pairs with the forecast label it explains.
OutcomeAction = Literal["granted", "denied", "reversed", "affirmed", "vacated"]

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
_TERM_FORM_RE: Final = re.compile(r"^\d{2}-\d+$")
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
    """Whether the case is, or may be, an original action."""
    number = (docket_number or "").strip()
    if number and _ORIGINAL_DOCKET_RE.search(number):
        return True
    if asking in _SOVEREIGNS and other in _SOVEREIGNS:
        return not _TERM_FORM_RE.match(number)
    return False


def outcome_lines(stage: Stage, sides: AskingSides) -> list[tuple[OutcomeAction, str]]:
    """One plain-language line per action open at ``stage``, filled with the names.

    Consequences only, never likelihood, and each action gets a line of the same
    weight: the lines say what an action does for the sides, not how likely it is.
    """
    return [(action, template(sides)) for action, template in _LINES[stage]]


def _name(party: str, *, start: bool = False) -> str:
    """``party`` as a sentence names it: with "the" where its form takes one."""
    words = party.split()
    article = (
        party.startswith("United States")
        or " of " in party
        or words[0] in _ARTICLE_NOUNS
        or words[-1] in _ARTICLE_NOUNS
    )
    if not article:
        return party
    return f"{'The' if start else 'the'} {party}"


def _possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def _cert_granted(sides: AskingSides) -> str:
    return (
        f"The Court agrees to hear {_possessive(_name(sides.asking))} case; "
        "that decides nothing yet about who is right."
    )


def _cert_denied(sides: AskingSides) -> str:
    return (
        f"{_possessive(_name(sides.other, start=True))} win in the lower court stands; "
        "that is not a ruling that the lower court was right."
    )


def _interim_granted(sides: AskingSides) -> str:
    return (
        f"{_name(sides.asking, start=True)} gets the relief requested, for now; "
        "the case continues in the lower courts."
    )


def _interim_denied(sides: AskingSides) -> str:
    return (
        f"{_name(sides.asking, start=True)} does not get the relief requested; "
        "the lower court's order stays in effect while the case continues."
    )


def _merits_reversed(sides: AskingSides) -> str:
    return (
        f"{_name(sides.asking, start=True)} wins in the Court; "
        "the lower court's decision is overturned."
    )


def _merits_affirmed(sides: AskingSides) -> str:
    return (
        f"{_name(sides.other, start=True)} wins in the Court; the lower court's decision is upheld."
    )


def _merits_vacated(_sides: AskingSides) -> str:
    return (
        "The lower court's decision is set aside and the case goes back to it, "
        "without either side winning yet."
    )


#: The actions open at each stage, in the order a reader meets them, and each
#: one's line. A petition and an application are decided granted or denied; a
#: merits case reversed, affirmed or vacated.
_LINES: Final[Mapping[Stage, tuple[tuple[OutcomeAction, Callable[[AskingSides], str]], ...]]] = {
    Stage.cert: (("granted", _cert_granted), ("denied", _cert_denied)),
    Stage.interim: (("granted", _interim_granted), ("denied", _interim_denied)),
    Stage.merits: (
        ("reversed", _merits_reversed),
        ("affirmed", _merits_affirmed),
        ("vacated", _merits_vacated),
    ),
}
