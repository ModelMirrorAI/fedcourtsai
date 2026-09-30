"""The Court's Granted & Noted list, as a cross-check on opinion lineups.

For each October Term the Court publishes a *Granted & Noted* list
(``supremecourt.gov/orders/<YY>grantednotedlist.pdf``): one entry per case set
for argument, giving the docket numbers decided together, the decision date,
the author of the Court's opinion and every other Justice who wrote, each with
a code for what they wrote::

    23-852  CFX BONDI V. VANDERSTOK
       Argument Date:  10/8/24   Decided:  3/26/25
       Author:  J. Gorsuch    Other:  Sotomayor (C);  Kavanaugh (C); ...
                         Thomas (D); Alito (D)

It is a second, independently prepared record of what the syllabus lineup
says (:mod:`fedcourtsai.pipeline.opinion_lineups`), so the two are compared:
the lead author, and the set of separate writers with the kind each wrote.
A disagreement means one of the two readings is wrong, and the merits vote
writer (:mod:`fedcourtsai.vote_writer`) holds such a record back rather than
publish it. The list itself is never published: it is a check, not a vote
source, and nothing it says reaches ``Outcome.votes``.

It also says which dockets were decided together: an entry opening on
``24-354)`` and ``24-422)`` is one argument and one opinion, which is how the
writer maps one opinion reading onto a consolidated case's other docket. The
opinions listing prints only the lead docket.

The codes (``C``, ``D``, ``C/J``, ``C/P``, ``D/P``) map onto the lineup
model's writing kinds; a combination the map does not know is a problem on the
entry, and an entry with a problem compares as a disagreement.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from types import MappingProxyType
from typing import Final

from .justices import chief_on_bench, resolve_surname
from .lineup import LEAD_KINDS, WritingKind

#: The Court's per-Term Granted & Noted list.
GRANTED_NOTED_URL: Final = "https://www.supremecourt.gov/orders/{term:02d}grantednotedlist.pdf"

#: How much of the list's text is extracted. A Term's list runs to tens of
#: thousands of characters; one still running at the cap is not read at all,
#: since a missing entry would read as a docket the list does not print.
TEXT_CHAR_CAP: Final = 400_000

#: What each printed combination of codes says one writing is. A Justice with
#: two writings is printed twice.
CODE_KINDS: Final[Mapping[frozenset[str], WritingKind]] = MappingProxyType(
    {
        frozenset({"C"}): WritingKind.concurrence,
        frozenset({"D"}): WritingKind.dissent,
        frozenset({"C/J"}): WritingKind.concurrence_in_judgment,
        frozenset({"C/P"}): WritingKind.concurrence_in_part,
        frozenset({"C/P", "C/J"}): WritingKind.concurrence_in_part,
        frozenset({"C/P", "D/P"}): WritingKind.concurrence_in_part_dissent_in_part,
        frozenset({"D/P"}): WritingKind.concurrence_in_part_dissent_in_part,
        frozenset({"C/J", "D/P"}): WritingKind.concurrence_in_part_dissent_in_part,
        frozenset({"C/J/P", "D/P"}): WritingKind.concurrence_in_part_dissent_in_part,
        frozenset({"C/P", "D/P", "C/J"}): WritingKind.concurrence_in_part_dissent_in_part,
        frozenset({"S"}): WritingKind.statement,
    }
)

# A docket line: a Term-form or application number opening the line, followed
# by anything but more of a number — the closing parenthesis a consolidated
# group prints after each member, a ``*`` or ``#`` marker, or the caption.
_DOCKET_LINE_RE = re.compile(r"^\s*(\d{2}-\d{1,5}|\d{2}A\d{1,4})(?![\d-])")
_DECIDED_RE = re.compile(r"\bDecided:\s*(\d{1,2}/\d{1,2}/\d{2,4})")
# "Decided: 6/30/26 (with No. 24-38)": the entry's opinion also decides these.
_WITH_RE = re.compile(r"\(with Nos?\.\s*([^)]*)\)")
_DOCKET_RE = re.compile(r"\b(\d{2}-\d{1,5}|\d{2}A\d{1,4})\b")


def _label(word: str) -> str:
    """A field label as printed, letter-spaced or not (``A u t h o r :``)."""
    return r"\b" + r"\s*".join(word) + r"\s*:"


_AUTHOR_RE = re.compile(_label("Author") + r"\s*(.*?)\s*(?:" + _label("Other") + r"|$)")
_OTHER_RE = re.compile(_label("Other") + r"\s*(.*)$")
# One other writing: its author or authors, then its codes in parentheses.
_OTHER_ENTRY_RE = re.compile(r"([^;()]+?)\s*\(([^)]*)\)")
_CODE_SPLIT_RE = re.compile(r"[,&]")
_NAME_SPLIT_RE = re.compile(r"\s*(?:&|/|,|\band\b)\s*")
#: Where an ``Other:`` list that wraps onto further lines has certainly ended.
#: Compared with the line's spaces removed, since some Terms' text layer
#: letter-spaces the labels (``R e s u l t :``).
_FIELD_LABELS: Final = (
    "Result:",
    "Court:",
    "ArgumentDate:",
    "RescheduledArgumentDate:",
    "Date:",
    "Order",
    "NOTE",
    "___",
)
#: The name the list prints for the Chief Justice as an other writer or author.
CHIEF: Final = "Chief Justice"


@dataclass(frozen=True)
class GrantedNotedEntry:
    """One case on the list: its dockets, decision date, author and other writers."""

    dockets: tuple[str, ...]
    decided: date | None
    author: str | None
    per_curiam: bool
    #: ``(justice, kind)`` for every separate writing the list prints; the
    #: Chief Justice is carried as :data:`CHIEF` and seated at comparison.
    others: tuple[tuple[str, WritingKind], ...]
    problems: tuple[str, ...] = ()
    #: Dockets the entry says its opinion also decides ("with No. …").
    joined: tuple[str, ...] = ()


@dataclass
class _Draft:
    dockets: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)


def _parse_date(raw: str) -> date | None:
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _name(raw: str) -> str | None:
    """A printed Justice name as the roster spells it, or :data:`CHIEF`.

    Some Terms' text layer letter-spaces a name (``S o t o m a y o r``,
    ``Sotomayo r``), so a name that does not resolve as printed is tried
    again with its spaces removed.
    """
    spaced = " ".join(raw.strip(" :;.,").split())
    solid = "".join(spaced.split())
    if spaced == CHIEF or solid == CHIEF.replace(" ", ""):
        return CHIEF
    return resolve_surname(spaced) or resolve_surname(solid)


def _others(text: str, problems: list[str]) -> list[tuple[str, WritingKind]]:
    """Every other writer the ``Other:`` text names; any it cannot read is a problem.

    Codes are separated by ``,`` or ``&``, and a jointly written opinion
    prints its authors together (``Sotomayor & Kagan (D)``,
    ``Breyer/Sotomayor/Kagan (D)``), each of whom wrote it. A qualified code
    (``C - as to 19-8709``) names no kind the map carries, so it is a problem
    rather than a silently dropped writer.
    """
    found: list[tuple[str, WritingKind]] = []
    for names, codes in _OTHER_ENTRY_RE.findall(text):
        code_set = frozenset("".join(c.split()) for c in _CODE_SPLIT_RE.split(codes) if c.strip())
        kind = CODE_KINDS.get(code_set)
        for name in _NAME_SPLIT_RE.split(names):
            if not name.strip():
                continue
            justice = _name(name)
            if justice is None:
                problems.append(f"an other writer {name.strip()!r} is not on the roster")
                continue
            if kind is None:
                problems.append(f"{justice}'s codes {sorted(code_set)} name no known writing kind")
                continue
            found.append((justice, kind))
    return found


def _ends_other(line: str) -> bool:
    solid = "".join(line.split())
    return not solid or solid.startswith(_FIELD_LABELS)


def _entry(draft: _Draft) -> GrantedNotedEntry:
    problems: list[str] = []
    decided: date | None = None
    author: str | None = None
    per_curiam = False
    joined: list[str] = []
    other_text: list[str] = []
    in_other = False
    for raw_line in draft.lines:
        line = " ".join(raw_line.split())
        if (match := _DECIDED_RE.search(line)) is not None:
            decided = _parse_date(match.group(1))
            if (with_match := _WITH_RE.search(line[match.end() :])) is not None:
                joined.extend(d.upper() for d in _DOCKET_RE.findall(with_match.group(1)))
        if (found := _AUTHOR_RE.search(line)) is not None:
            raw = found.group(1)
            solid = "".join(raw.split())
            if solid == "PerCuriam":
                per_curiam = True
            else:
                author = _name(re.sub(r"^J\s*\.\s*", "", raw))
                if author is None:
                    problems.append(f"the author {raw!r} is not on the roster")
        if (other := _OTHER_RE.search(line)) is not None:
            in_other = True
            other_text.append(other.group(1))
            continue
        if in_other:
            if _ends_other(line):
                in_other = False
            else:
                other_text.append(line)
    return GrantedNotedEntry(
        dockets=tuple(draft.dockets),
        decided=decided,
        author=author,
        per_curiam=per_curiam,
        others=tuple(_others(" ".join(other_text), problems)),
        problems=tuple(problems),
        joined=tuple(joined),
    )


def parse_granted_noted(text: str) -> list[GrantedNotedEntry]:
    """Every entry of one list's extracted text, in list order.

    A run of consecutive docket lines opens one entry (a consolidated group);
    the entry runs to the next docket line. Page furniture between them is
    harmless, since only the ``Decided``, ``Author`` and ``Other`` fields are
    read.
    """
    entries: list[GrantedNotedEntry] = []
    draft: _Draft | None = None
    opening = False
    for line in text.splitlines():
        match = _DOCKET_LINE_RE.match(line)
        if match is not None:
            if draft is None or not opening:
                if draft is not None:
                    entries.append(_entry(draft))
                draft = _Draft()
            draft.dockets.append(match.group(1).upper())
            opening = True
            continue
        opening = False
        if draft is not None:
            draft.lines.append(line)
    if draft is not None:
        entries.append(_entry(draft))
    return entries


def by_docket(entries: Iterable[GrantedNotedEntry]) -> dict[str, GrantedNotedEntry]:
    """Each docket's entry, with a consolidated group's dockets under one.

    A docket printed in two entries keeps the decided one. Where an entry
    prints no author of its own and says its opinion is another docket's
    ("Decided … (with No. 24-43)"), its dockets take that entry, widened to
    name them, so every docket one opinion decides maps to the entry that
    describes the opinion.
    """
    index: dict[str, GrantedNotedEntry] = {}
    for entry in entries:
        for docket in entry.dockets:
            held = index.get(docket)
            if held is None or (held.decided is None and entry.decided is not None):
                index[docket] = entry
    for entry in list(index.values()):
        if entry.author is not None or entry.per_curiam or not entry.joined:
            continue
        lead = next(
            (index[d] for d in entry.joined if d in index and index[d].author is not None),
            None,
        )
        if lead is None or lead.decided != entry.decided:
            continue
        group = tuple(dict.fromkeys((*lead.dockets, *entry.dockets)))
        merged = GrantedNotedEntry(
            dockets=group,
            decided=lead.decided,
            author=lead.author,
            per_curiam=lead.per_curiam,
            others=lead.others,
            problems=lead.problems,
            joined=lead.joined,
        )
        for docket in group:
            index[docket] = merged
    return index


@dataclass(frozen=True)
class WritingSummary:
    """What a lineup reading says, in the list's terms: lead author and other writers."""

    lead_author: str | None
    others: frozenset[tuple[str, WritingKind]]


def summarize(writings: Sequence[tuple[WritingKind, Sequence[str]]]) -> WritingSummary:
    """A reading's writings as the list prints them: every author of every writing.

    ``writings`` is ``(kind, authors)`` per writing. A joint writing credits
    each co-author, as the list does.
    """
    lead: str | None = None
    others: set[tuple[str, WritingKind]] = set()
    for kind, authors in writings:
        if kind in LEAD_KINDS:
            lead = authors[0] if authors else None
            continue
        others.update((author, kind) for author in authors)
    return WritingSummary(lead_author=lead, others=frozenset(others))


def disagreements(
    entry: GrantedNotedEntry, reading: WritingSummary, *, bench: Sequence[str], decided: date | None
) -> list[str]:
    """How the list's entry and a lineup reading of the same opinion differ.

    Empty when they agree on the decision date, the lead author and every
    separate writer with what they wrote. An entry the list could not be read
    for, or a per curiam (whose lineup is not read), disagrees.
    """
    found = [f"the list could not be read: {p}" for p in entry.problems]
    if entry.per_curiam:
        found.append("the list prints a per curiam")
    if decided is not None and entry.decided is not None and decided != entry.decided:
        found.append(
            f"the list dates the decision {entry.decided.isoformat()}, "
            f"the opinion {decided.isoformat()}"
        )
    chief = chief_on_bench(tuple(bench))
    listed_author = chief if entry.author == CHIEF else entry.author
    if listed_author != reading.lead_author:
        found.append(f"the list's author is {listed_author}, the lineup's {reading.lead_author}")
    listed = frozenset(
        (chief if justice == CHIEF else justice, kind)
        for justice, kind in entry.others
        if justice != CHIEF or chief is not None
    )
    for justice, kind in sorted(listed - reading.others):
        found.append(f"the list prints {justice} ({kind}), the lineup does not")
    for justice, kind in sorted(reading.others - listed):
        found.append(f"the lineup reads {justice} ({kind}), the list does not")
    return found
