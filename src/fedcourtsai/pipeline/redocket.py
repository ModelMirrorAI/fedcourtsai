"""Re-docketed numbers: a stored docket that now names another petition.

The Supreme Court Clerk occasionally re-dockets: a petition docketed under one
number is moved to another, and the freed number is re-entered for a different
petition. The live channel keys a row on its docket number
(:func:`fedcourtsai.pipeline.live._resolve_identity`), so the row keeps its id
and takes on the new petition's caption, docketed date and lower-court case,
while an event opened under the old petition still sits on it. Resolved against
the row, that event would receive the other petition's disposition.

An event's own record of whose petition it forecasts is its **caption**, its
``opened_at`` and its stage. The corpus event's ``title`` is stamped from the
row's caption when the event is written. The committed ledger ``event.yaml``
keeps the caption and opening date it carried at first touch:
``materialize-event`` never rewrites it, a re-fired mint keeps its title
(:func:`fedcourtsai.pipeline.outcome.persist_moment_events`), and the outcome
writer rewrites it only beside an outcome. So it is the identity a committed
prediction was made under. A case-level baseline's corpus title and opening date re-track the row on
every re-extraction, so for a baseline the ledger copy is the only surviving
witness, and both are read.

**The rule** (:func:`is_redocketed`). An event names another petition when

- its caption and the row's current caption share no party word on the
  **petitioner** side; or
- they share none on the **respondent** side, the event is not an interim
  (application) moment, and it opened before the row's current docketed date.

A re-docketed number commonly keeps a respondent such as ``United States`` or a
State, so the petitioner side alone is enough. The respondent side alone is not:
a caption's first-named respondent changes when that party leaves the case,
with the petition and its docketed date unchanged. A re-entered number carries
the new petition's later docketed date, which is the corroboration that side
needs. It corroborates only where a moment opens at or after docketing (the
cert and merits stages). An application's interim baseline opens at the
application's filing, which routinely precedes its docketing by days to weeks,
so "opened before docketing" says nothing there, and an interim moment is read
on the petitioner side alone. A side that yields no party word on either
caption is not compared: an ``In re`` caption or a bare docket number has no
respondent side, and a caption of initials (``M. W.``) has no party word.

Party words are the caption's words of three or more letters, accents folded
and apostrophes dropped (``Dep't`` reads ``dept``), outside a fixed list of role
and connective words. Two words match when they are equal, or when the shorter
is four or more letters and either a prefix of the longer (``Corr.`` against
``Corrections``) or an abbreviation of it: same first letter, its letters in
order (``Dept`` against ``Department``). A three-letter word matches only
itself, so a short name is not absorbed into a longer one. A substituted
officer leaves the office words in place (``…, Attorney General``,
``…, Warden``), so a Rule 35.3 substitution keeps an overlap. A moved docketed
date with the same parties is a date correction, not a re-docketing, and is not
refused.

**What the rule misses.** Two petitions whose petitioner sides share a word — a
common first name or surname, or a shared word such as ``County`` in two
governments' names — read as one, unless the respondent arm catches them. A
party renamed outright (a corporation's new name, a substituted officer named
without an office) reads as another petition, which refuses a real decision.

What a refusal does is the caller's: outcome detection surfaces the event for
triage with :data:`REDOCKETED_REASON` instead of attributing the row's
disposition to it (:func:`fedcourtsai.pipeline.outcome.detect_resolution`).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from ..paths import CasePaths

#: The triage reason for an event whose caption names another petition than the
#: docket now does. Fixed text, so a reader (the outcome pass's residue classing
#: among them) can key on it.
REDOCKETED_REASON = (
    "the docket now names other parties than the moment was opened under (a re-docketed "
    "number); the outcome is not attributed to it"
)

#: Words that name a party's role or join a caption rather than identify a party.
_ROLE_WORDS = frozenset(
    {
        "administrator",
        "al",
        "and",
        "appellant",
        "appellants",
        "appellee",
        "appellees",
        "applicant",
        "applicants",
        "behalf",
        "child",
        "children",
        "company",
        "corp",
        "corporation",
        "deceased",
        "defendant",
        "defendants",
        "estate",
        "et",
        "for",
        "friend",
        "her",
        "his",
        "inc",
        "individually",
        "llc",
        "ltd",
        "minor",
        "movant",
        "movants",
        "next",
        "others",
        "petitioner",
        "petitioners",
        "plaintiff",
        "plaintiffs",
        "re",
        "respondent",
        "respondents",
        "the",
        "their",
        "vir",
    }
)

_MIN_WORD = 3
#: The shortest word a prefix or abbreviation match may start from; a shorter
#: one matches only an equal word.
_MIN_PREFIX = 4
# Lower-case only: captions write the separator ``v.``, and an upper-case ``V.``
# is a middle initial.
_VERSUS = re.compile(r"\s+vs?\.?\s+")
_WORD = re.compile(r"[a-z]+")
_APOSTROPHE = re.compile(r"['\u2019]")
_INTERIM = "interim"


@dataclass(frozen=True)
class EventIdentity:
    """Whose petition an event was opened under: its caption, opening date and stage."""

    title: str
    opened_at: date | None = None
    stage: str | None = None


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    folded = "".join(c for c in decomposed if not unicodedata.combining(c)).lower()
    return _APOSTROPHE.sub("", folded)


def party_words(side: str) -> frozenset[str]:
    """The party-identifying words of one side of a caption, accent-folded and lower-cased."""
    return frozenset(
        word
        for word in _WORD.findall(_fold(side))
        if len(word) >= _MIN_WORD and word not in _ROLE_WORDS
    )


def caption_sides(caption: str) -> tuple[frozenset[str], frozenset[str]]:
    """A caption's petitioner and respondent party words; the respondent side is
    empty when the caption has no ``v.``."""
    petitioner, *rest = _VERSUS.split(caption, maxsplit=1)
    return party_words(petitioner), party_words(rest[0] if rest else "")


def _abbreviates(short: str, long: str) -> bool:
    if short[0] != long[0]:
        return False
    rest = iter(long)
    return all(c in rest for c in short)


def _match(x: str, y: str) -> bool:
    short, long = sorted((x, y), key=len)
    if short == long:
        return True
    return len(short) >= _MIN_PREFIX and (long.startswith(short) or _abbreviates(short, long))


def sides_differ(a: frozenset[str], b: frozenset[str]) -> bool:
    """Whether two sides both name a party and share no party word."""
    return bool(a) and bool(b) and not any(_match(x, y) for x in a for y in b)


def is_redocketed(identity: EventIdentity, current_caption: str, docketed: date | None) -> bool:
    """Whether an event opened under ``identity`` names another petition than the row.

    ``current_caption`` and ``docketed`` are the row's caption and docketed
    date. The rule is the module docstring's.
    """
    if not identity.title or not current_caption:
        return False
    event_petitioner, event_respondent = caption_sides(identity.title)
    current_petitioner, current_respondent = caption_sides(current_caption)
    if sides_differ(event_petitioner, current_petitioner):
        return True
    corroborated = (
        identity.stage != _INTERIM
        and identity.opened_at is not None
        and docketed is not None
        and identity.opened_at < docketed
    )
    return corroborated and sides_differ(event_respondent, current_respondent)


def _committed_identity(path: Path) -> EventIdentity | None:
    """One committed ``event.yaml``'s identity, or ``None`` when it cannot be read.

    A file the ledger gate would reject (unparseable, or a field of the wrong
    shape) is not a witness: the poll degrades to the corpus reading rather than
    failing on it.
    """
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    if not isinstance(loaded, dict):
        return None
    title, opened, stage = loaded.get("title"), loaded.get("opened_at"), loaded.get("stage")
    if not isinstance(title, str) or not title:
        return None
    if isinstance(opened, str):
        try:
            opened = date.fromisoformat(opened)
        except ValueError:
            return None
    return EventIdentity(
        title,
        opened if isinstance(opened, date) else None,
        stage if isinstance(stage, str) else None,
    )


def ledger_identities(
    data_root: Path, court_id: str, docket_id: int, event_ids: Iterable[str]
) -> dict[str, EventIdentity]:
    """The committed ``event.yaml`` identity of each event that has a readable one.

    The caption, opening date and stage the event carried at first touch, which
    is the identity a committed prediction was made under. An event with no
    committed file, or one that cannot be read (:func:`_committed_identity`),
    is absent.
    """
    case = CasePaths(data_root, court_id, docket_id)
    identities: dict[str, EventIdentity] = {}
    for event_id in event_ids:
        path = case.event(event_id).event_file
        if not path.is_file():
            continue
        identity = _committed_identity(path)
        if identity is not None:
            identities[event_id] = identity
    return identities


def redocketed_events(
    current_caption: str,
    docketed: date | None,
    *witnesses: Mapping[str, EventIdentity],
) -> frozenset[str]:
    """The event ids any witness shows opened under another petition.

    Each witness maps an event id to an :class:`EventIdentity`: the corpus
    event's, and the committed ledger ``event.yaml``'s
    (:func:`ledger_identities`).
    """
    return frozenset(
        event_id
        for witness in witnesses
        for event_id, identity in witness.items()
        if is_redocketed(identity, current_caption, docketed)
    )
