"""The Supreme Court syllabus lineup grammar: votes and authorship from one paragraph.

Every signed Supreme Court opinion's syllabus closes with a paragraph naming
who wrote what and who joined it::

    ALITO, J., delivered the opinion of the Court, in which ROBERTS, C. J.,
    and THOMAS, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. BARRETT, J.,
    filed a concurring opinion, in which THOMAS and GORSUCH, JJ., joined as to
    Part II-B. SOTOMAYOR, J., filed a dissenting opinion, in which KAGAN and
    JACKSON, JJ., joined.

This module reads that paragraph's text into a
:class:`~fedcourtsai.pipeline.lineup.Lineup`. The grammar is a Python
implementation of the one documented in ``docs/justices.md`` of the ceRt
project (credited in ``docs/data-sources.md``); it is written from that
description of the Court's conventions, and no ceRt code or data is used.

**The sentences.** The paragraph is one statement per sentence:

- *Lead*: ``X delivered the opinion of the Court[, in which A, B, and C
  joined]`` \u2014 or ``for a unanimous Court``, ``in which all other Members
  joined``, the scoped form ``with respect to Parts I and II, … and an opinion
  with respect to Part III, in which …``, the split form ``except as to
  Part II`` (its joiners named in the sentences that follow: ``A and B joined
  that opinion in full; C joined except as to Part II``), and the plurality
  form ``X announced the judgment of the Court and delivered …``.
- *Separate writing*: ``X filed a concurring opinion[, in which Y joined
  as to Part II-B]``, ``… an opinion concurring in the judgment``, ``… an
  opinion concurring in part and dissenting in part``, the plural ``X and Y
  filed dissenting opinions`` (one writing each), and the joint ``X, Y, and Z
  filed a dissenting opinion`` (one writing, three authors).
- *Non-participation*: ``Z took no part in the consideration or decision of
  the case``, or the lead's own ``…, except Z, who took no part …``.
- *Per curiam*: a ``PER CURIAM`` sentence in place of a lead.

**The convention that needs the bench.** The Court lists a lead clause's
joiners only where fewer than all joined, so a Court clause with no ``in
which`` of its own was joined by every participant who did not sign a writing
that departs from it (a dissent, a partial concurrence, a concurrence in the
judgment); a per curiam likewise speaks for everyone not writing or joining
such a separate opinion. That is why :func:`parse_syllabus_lineup` takes the
bench \u2014 the Justices who could have sat \u2014 and why the bench must be right: a
Justice on it whom the paragraph neither names nor excludes is credited to
the lead under this convention. Non-participation the paragraph states is
honored; a vacancy or a Justice seated after argument is the caller's to
leave off the bench.

**What it refuses to do.** Any sentence the grammar cannot read, any name the
roster (:mod:`fedcourtsai.pipeline.justices`) does not carry, a missing or
doubled lead, or a Justice the writings do not place is reported in
``problems`` and leaves the lineup ``complete=False`` \u2014 with no votes at all
when the paragraph itself did not parse, because a lineup read around an
unparsed sentence could be missing the dissent that moves a Justice's side.

**Text shapes.** Slip opinions print the paragraph in small caps; preliminary
prints and bound volumes in mixed case, with page cites (``post, p. 128``), a
text layer that drops the "fi" ligature (``fled``), and line-end hyphenation
(``con- curring``). Matching is case-blind, page cites are stripped, ``filed``
matches with or without its ``i``, and a hyphen that ends a line or splits a
lowercase word is closed up. Locating the paragraph in an opinion and
stripping running heads is the fetching channel's job, not this grammar's.

Bump :data:`GRAMMAR_VERSION` whenever a change could read the same text
differently; every lineup carries it, so cached paragraphs can be re-read.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Final

from ..schemas import QUORUM
from .justices import resolve_surname
from .lineup import (
    NOT_JOINING_LEAD_KINDS,
    Join,
    Lineup,
    Writing,
    WritingKind,
    lineup_from_writings,
)

#: The court this grammar reads, as the case id prints it.
COURT: Final = "scotus"
#: The grammar's stamp on every lineup it returns.
GRAMMAR_NAME: Final = "scotus-syllabus"
#: Bump whenever the same text could read differently.
GRAMMAR_VERSION: Final = 1

# The title marker a Justice's printed title (", C. J.,", ", J.,", ", JJ.,")
# collapses to, so the periods it carries cannot end a sentence and its commas
# cannot split a name list.
_TITLE: Final = "§"

_TITLE_RE = re.compile(r",\s*(?:C\.\s*J\.|JJ\.|J\.)(?:\s*,)?", re.IGNORECASE)
_PAGE_CITE_RE = re.compile(r",\s*(?:ante|post),\s*pp?\.\s*\d+(?:\s*[-\u2013]\s*\d+)?", re.I)
_LINE_HYPHEN_RE = re.compile(r"(\w)-[ \t]*\n\s*(\w)")
_SPLIT_WORD_RE = re.compile(r"([A-Za-z])- ([a-z])")

# One part or footnote id: a Roman numeral, capital letter, or number, then
# any dash-joined subdivisions ("II", "IV-B", "III-B-2-a"). Case-sensitive even
# inside the case-blind sentence patterns, so "in" or "a" is never a part id.
_ID = (
    r"(?-i:(?:[IVXL]+|[A-Z]|\d+)"
    r"(?:\s*[-\u2013\u2014]\s*(?:[IVXL]+|[A-Z]|[a-z]|\d+))*)\b"
)
_LIST_SEP = r"(?:\s*,\s*(?:and\s+)?|\s+and\s+)"
_SCOPE_ITEM = rf"(?:Parts?|footnotes?)\s+{_ID}(?:{_LIST_SEP}{_ID})*"
_SCOPE = rf"(?:all\s+but\s+)?{_SCOPE_ITEM}(?:{_LIST_SEP}{_SCOPE_ITEM})*"

_LEAD_RE = re.compile(r"^(?P<names>.+?)\s+(?P<verb>delivered|announced)\s+(?P<rest>.+)$", re.I)
_FILED_RE = re.compile(r"^(?P<names>.+?)\s+f(?:i)?led\s+(?P<rest>.+)$", re.I)
_TOOK_NO_PART_RE = re.compile(
    r"^(?P<names>.+?)\s+took\s+no\s+part(?:\s+in\s+the\s+(?:consideration|decision)\b.*)?$",
    re.I,
)
_PER_CURIAM_RE = re.compile(r"^per\s+curiam$", re.I)
_JOINED_WORD_RE = re.compile(r"\bjoined\b", re.I)

_ANNOUNCED_RE = re.compile(
    r"^announced\s+the\s+judgment\s+of\s+the\s+Court,?\s+and\s+delivered\s+(?P<rest>.+)$", re.I
)
_EXCEPT_ABSENT_RE = re.compile(
    r",?\s*except\s+(?P<names>(?:(?!\bexcept\b|\bas\s+to\b).)+?),?\s+who\s+took\s+no\s+part\b"
    r"[^,;]*",
    re.I,
)
_CLAUSE_SPLIT_RE = re.compile(r",?\s+and\s+(?=an\s+opinion\b)", re.I)
_CLAUSE_RE = re.compile(
    r"^(?P<head>the\s+opinion\s+(?:of|for)\s+(?P<court>the|a\s+unanimous)\s+Court"
    r"|an\s+opinion)"
    rf"(?:,?\s+(?:with\s+respect\s+to|as\s+to)\s+(?P<scope>{_SCOPE}))?"
    rf"(?:,?\s+except\s+as\s+to\s+(?P<except>{_SCOPE}))?"
    r"(?:,\s*in\s+which\s+(?P<joins>.+))?$",
    re.I,
)
_JOINED_RE = re.compile(
    r"\s*\bjoined\b"
    r"(?:\s+(?:that|the)\s+opinion(?:\s+of\s+the\s+Court)?)?"
    r"(?P<q>\s+in\s+full"
    rf"|,?\s+(?:except\s+)?(?:as\s+to|with\s+respect\s+to)\s+{_SCOPE}"
    r"|\s+in\s+part)?",
    re.I,
)
_JOIN_SEP_RE = re.compile(r"\s*(?:[,;]\s*)?(?:and\s+)?(?:in\s+which\s+)?", re.I)
_FILED_WHAT_RE = re.compile(r"^(?P<what>.+?)(?:,\s*in\s+which\s+(?P<joins>.+))?$", re.I)
_SINGLE_ADJ_RE = re.compile(r"^an?\s+(?P<desc>concurring|dissenting)\s+opinion$", re.I)
_PLURAL_ADJ_RE = re.compile(r"^(?P<desc>concurring|dissenting)\s+opinions$", re.I)
_SINGLE_DESC_RE = re.compile(r"^an?\s+opinion\s+(?P<desc>.+)$", re.I)
_PLURAL_DESC_RE = re.compile(r"^opinions\s+(?P<desc>.+)$", re.I)
_DESC_WORDS: Final = frozenset({"concurring", "dissenting", "in", "part", "the", "judgment", "and"})
_NAME_TOKEN_RE = re.compile(r"^[A-Z][A-Za-z'.]*$")
_ALL_OTHERS_RE = re.compile(r"^all\s+other\s+Members$", re.I)

# The sentinel a joiner list resolves to when it reads "all other Members".
_ALL_OTHERS: Final = "*"


def normalize_lineup_text(text: str) -> str:
    """The paragraph as the sentence patterns read it.

    Unicode-normalized (the "fi" ligature and curly apostrophes fold), line-end
    hyphenation closed up, whitespace collapsed, page cites dropped, and each
    printed title collapsed to one marker.
    """
    text = unicodedata.normalize("NFKC", text).replace("\u2019", "'").replace("\u2018", "'")
    text = _LINE_HYPHEN_RE.sub(r"\1\2", text)
    text = " ".join(text.split())
    text = _SPLIT_WORD_RE.sub(r"\1\2", text)
    text = _PAGE_CITE_RE.sub("", text)
    return _TITLE_RE.sub(f" {_TITLE}", text)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=\.)\s+", text)
    return [p.strip().removesuffix(".").strip() for p in parts if p.strip().strip(".")]


def _resolve_name(raw: str) -> str | None:
    """The roster spelling for one printed name, however much of it printed.

    The longest suffix the roster knows wins, so "Ketanji Brown Jackson"
    resolves to "Jackson" and "Van Devanter" stays whole; every token must be
    name-shaped (capitalized), so a stray clause never resolves on its last
    word.
    """
    tokens = raw.split()
    if not tokens or len(tokens) > 4 or not all(_NAME_TOKEN_RE.match(t) for t in tokens):
        return None
    for start in range(len(tokens)):
        if resolved := resolve_surname(" ".join(tokens[start:])):
            return resolved
    return None


def _names(chunk: str, problems: list[str]) -> list[str]:
    """Every Justice a printed name list names, or ``[]`` with a problem recorded."""
    cleaned = chunk.replace(_TITLE, " ").strip(" ,;")
    if _ALL_OTHERS_RE.match(" ".join(cleaned.split())):
        return [_ALL_OTHERS]
    raw = [part.strip() for part in re.split(r",|\band\b", cleaned) if part.strip()]
    resolved: list[str] = []
    for name in raw:
        surname = _resolve_name(name)
        if surname is None:
            problems.append(f"unrecognized Justice name {name!r}")
            return []
        resolved.append(surname)
    if not resolved:
        problems.append(f"no Justice named in {chunk.strip()!r}")
    return resolved


def _qualifier(raw: str | None) -> str | None:
    if raw is None:
        return None
    text = " ".join(raw.strip(" ,").split())
    return None if text.lower() == "in full" else text


def _joins(text: str, problems: list[str]) -> list[tuple[list[str], str | None]]:
    """Read ``A and B joined, and in which C joined as to Part I`` into chunks.

    Each chunk is the names before one ``joined`` and the qualifier after it.
    Text left over that is not a separator is a problem, never skipped.
    """
    chunks: list[tuple[list[str], str | None]] = []
    pos = 0
    while pos < len(text):
        sep = _JOIN_SEP_RE.match(text, pos)
        if sep is not None:
            pos = sep.end()
        if pos >= len(text):
            break
        match = _JOINED_RE.search(text, pos)
        if match is None:
            problems.append(f"unreadable join list {text[pos:]!r}")
            return []
        names = _names(text[pos : match.start()], problems)
        if not names:
            return []
        chunks.append((names, _qualifier(match.group("q"))))
        pos = match.end()
    if not chunks:
        problems.append(f"no joiner in {text!r}")
    return chunks


def _writing_kind(desc: str) -> WritingKind | None:
    """A separate writing's kind from its printed description, or ``None``."""
    lowered = " ".join(desc.lower().replace(",", " ").split())
    words = set(lowered.split())
    if not words or words - _DESC_WORDS:
        return None
    dissenting = "dissenting" in words
    concurring = "concurring" in words
    in_part = "part" in words
    if dissenting:
        return (
            WritingKind.concurrence_in_part_dissent_in_part
            if concurring or in_part
            else WritingKind.dissent
        )
    if not concurring:
        return None
    if "concurring in part" in lowered:
        return WritingKind.concurrence_in_part
    if "judgment" in words:
        return None if in_part else WritingKind.concurrence_in_judgment
    return WritingKind.concurrence if lowered == "concurring" else None


@dataclass
class _Clause:
    label: str | None
    of_court: bool
    unanimous: bool
    joins: list[tuple[list[str], str | None]] | None


@dataclass
class _Lead:
    author: str
    plurality: bool
    clauses: list[_Clause]
    followers: list[tuple[list[str], str | None]]


def _read_lead(
    names: str, verb: str, rest: str, absent: set[str], problems: list[str]
) -> _Lead | None:
    authors = _names(names, problems)
    if len(authors) != 1 or authors[0] == _ALL_OTHERS:
        if authors:
            problems.append(f"a lead opinion needs one author, read {names.strip()!r}")
        return None
    plurality = verb.lower() == "announced"
    if plurality:
        announced = _ANNOUNCED_RE.match(f"announced {rest}")
        if announced is None:
            problems.append(f"unreadable plurality lead {rest!r}")
            return None
        rest = announced.group("rest")
    if (excepted := _EXCEPT_ABSENT_RE.search(rest)) is not None:
        absent.update(n for n in _names(excepted.group("names"), problems) if n != _ALL_OTHERS)
        rest = rest[: excepted.start()] + rest[excepted.end() :]
    clauses: list[_Clause] = []
    for raw in _CLAUSE_SPLIT_RE.split(rest.strip(" ,")):
        match = _CLAUSE_RE.match(raw.strip(" ,"))
        if match is None:
            problems.append(f"unreadable lead clause {raw!r}")
            return None
        scope, excepted_parts = match.group("scope"), match.group("except")
        label_parts = []
        if scope:
            label_parts.append(f"with respect to {' '.join(scope.split())}")
        if excepted_parts:
            label_parts.append(f"except as to {' '.join(excepted_parts.split())}")
        joins = _joins(match.group("joins"), problems) if match.group("joins") else None
        if match.group("joins") and not joins:
            return None
        court = match.group("court")
        clauses.append(
            _Clause(
                label=", ".join(label_parts) or None,
                of_court=court is not None,
                unanimous=court is not None and court.lower() != "the",
                joins=joins,
            )
        )
    if not plurality and not clauses[0].of_court:
        problems.append("a delivered lead must deliver the opinion of the Court")
        return None
    return _Lead(author=authors[0], plurality=plurality, clauses=clauses, followers=[])


def _departing(separate: Sequence[Writing]) -> set[str]:
    """Everyone who signed a separate writing that departs from the lead."""
    return {name for w in separate if w.kind in NOT_JOINING_LEAD_KINDS for name in w.signatories}


def _clause_members(
    lead: _Lead, clause: _Clause, others: Sequence[str], implicit: Sequence[str]
) -> list[tuple[str, str | None]]:
    """Who joined one lead clause, with each join's own qualifier.

    A unanimous clause is everyone else; a Court clause printing no joiners of
    its own is everyone not departing — unless follower sentences name the
    joiners instead (the split form); any other clause is its printed list.
    """
    if clause.joins is not None:
        return [
            (name, q)
            for names, q in clause.joins
            for name in (others if names == [_ALL_OTHERS] else names)
        ]
    if clause.unanimous:
        return [(p, None) for p in others]
    if clause.of_court and not lead.followers:
        return [(p, None) for p in implicit]
    return []


def _lead_join(
    name: str, held: Sequence[tuple[int, str | None]], clauses: Sequence[_Clause]
) -> Join:
    """One Justice's join of the whole lead, from their joins of its clauses."""
    if len(held) == len(clauses) and all(q is None for _, q in held):
        return Join(name)
    if len(clauses) == 1:
        return Join(name, held[0][1])
    parts = [" ".join(p for p in (clauses[i].label, q) if p) for i, q in held]
    return Join(name, "; ".join(p for p in parts if p) or None)


def _lead_writing(
    lead: _Lead, participants: Sequence[str], separate: Sequence[Writing], problems: list[str]
) -> Writing:
    """Resolve the lead's clauses, its follower sentences and the Court's
    list-only-where-fewer-than-all convention into one writing's joins."""
    departing = _departing(separate)
    others = [p for p in participants if p != lead.author]
    implicit = [p for p in others if p not in departing]
    memberships: dict[str, list[tuple[int, str | None]]] = {}
    for index, clause in enumerate(lead.clauses):
        for name, q in _clause_members(lead, clause, others, implicit):
            memberships.setdefault(name, []).append((index, q))

    joins: list[Join] = []
    for name, held in memberships.items():
        if name == lead.author:
            problems.append(f"{name} is read both as the lead's author and a joiner")
            continue
        joins.append(_lead_join(name, held, lead.clauses))
    for names, q in lead.followers:
        for name in others if names == [_ALL_OTHERS] else names:
            if name in memberships:
                problems.append(f"{name} joins the lead twice")
                continue
            memberships[name] = [(0, q)]
            joins.append(Join(name, q))

    if lead.plurality and not any(c.of_court for c in lead.clauses):
        kind = WritingKind.plurality
    else:
        kind = WritingKind.opinion_of_the_court
    scoped = [
        f"{'the opinion of the Court' if c.of_court else 'an opinion'} {c.label}"
        for c in lead.clauses
        if c.label
    ]
    return Writing(kind, lead.author, tuple(joins), "; ".join(scoped) or None)


def parse_syllabus_lineup(text: str, *, bench: Sequence[str]) -> Lineup:
    """Read one syllabus lineup paragraph into a :class:`Lineup`.

    ``bench`` is the Justices who could have sat on the decision, in any case
    the roster resolves; a name it does not carry is a caller error
    (``ValueError``), because the bench is an input, not a reading. Anything
    the paragraph itself does not settle is a ``problem`` on an incomplete
    lineup, never an exception.
    """
    roster = _roster(bench)
    reading = _read_paragraph(text)
    problems = reading.problems
    if reading.leads_read > 1:
        problems.append(f"expected one lead sentence, read {reading.leads_read}")
    elif reading.leads_read == 0:
        problems.append("no lead opinion and no per curiam")

    participants = [name for name in roster if name not in reading.absent]
    writings: list[Writing] = []
    if reading.leads_read == 1 and reading.lead is not None:
        writings.append(_lead_writing(reading.lead, participants, reading.separate, problems))
    elif reading.leads_read == 1 and reading.per_curiam:
        departing = _departing(reading.separate)
        joins = tuple(Join(p) for p in participants if p not in departing)
        writings.append(Writing(WritingKind.per_curiam, None, joins))
    writings.extend(reading.separate)

    return lineup_from_writings(
        court=COURT,
        grammar=GRAMMAR_NAME,
        grammar_version=GRAMMAR_VERSION,
        bench=roster,
        writings=writings,
        took_no_part=reading.absent,
        problems=problems,
        quorum=QUORUM,
    )


def _roster(bench: Sequence[str]) -> list[str]:
    """The bench in roster spelling; an unknown or repeated name is a caller error."""
    roster: list[str] = []
    for name in bench:
        surname = resolve_surname(name)
        if surname is None:
            raise ValueError(f"bench name {name!r} is not on the roster")
        if surname in roster:
            raise ValueError(f"bench names {surname!r} twice")
        roster.append(surname)
    return roster


@dataclass
class _Reading:
    """What the sentences of one paragraph said, before the bench is applied."""

    problems: list[str] = field(default_factory=list)
    absent: set[str] = field(default_factory=set)
    lead: _Lead | None = None
    leads_read: int = 0
    per_curiam: bool = False
    separate: list[Writing] = field(default_factory=list)


def _read_paragraph(text: str) -> _Reading:
    """Classify each sentence and read it; anything unclassifiable is a problem.

    A bare ``joined`` sentence is read only straight after the lead (or another
    such sentence): that is where the split form prints the lead's joiners, and
    anywhere else it could belong to any writing.
    """
    reading = _Reading()
    problems = reading.problems
    previous: str | None = None
    sentences = _sentences(normalize_lineup_text(text))
    if not sentences:
        problems.append("empty lineup paragraph")
    for sentence in sentences:
        if _PER_CURIAM_RE.match(sentence):
            reading.per_curiam = True
            reading.leads_read += 1
            previous = "per-curiam"
        elif (m := _LEAD_RE.match(sentence)) is not None:
            reading.leads_read += 1
            names, verb, rest = m.group("names"), m.group("verb"), m.group("rest")
            reading.lead = _read_lead(names, verb, rest, reading.absent, problems)
            previous = "lead"
        elif (m := _FILED_RE.match(sentence)) is not None:
            reading.separate.extend(_read_filed(m.group("names"), m.group("rest"), problems))
            previous = "filed"
        elif (m := _TOOK_NO_PART_RE.match(sentence)) is not None:
            named = _names(m.group("names"), problems)
            reading.absent.update(n for n in named if n != _ALL_OTHERS)
            previous = "absent"
        elif _JOINED_WORD_RE.search(sentence) and previous in {"lead", "followers"}:
            if reading.lead is not None:
                reading.lead.followers.extend(_joins(sentence, problems))
            previous = "followers"
        else:
            problems.append(f"unreadable sentence {sentence!r}")
            previous = None
    return reading


def _read_filed(names: str, rest: str, problems: list[str]) -> list[Writing]:
    """One ``filed`` sentence's writings: one, or one per author when plural."""
    authors = _names(names, problems)
    if _ALL_OTHERS in authors:
        problems.append(f"a writing needs named authors, read {names.strip()!r}")
        return []
    parts = _FILED_WHAT_RE.match(rest.strip())
    shape = _filed_shape(" ".join(parts.group("what").split())) if parts else None
    if not authors or parts is None or shape is None:
        if authors:
            problems.append(f"unreadable writing {rest!r}")
        return []
    kind, plural = shape
    if plural:
        if len(authors) == 1 or parts.group("joins"):
            problems.append(f"plural writings need several authors and no joiners: {rest!r}")
            return []
        return [Writing(kind, author) for author in authors]
    joins = _separate_joins(parts.group("joins"), problems)
    if joins is None:
        return []
    return [Writing(kind, authors[0], joins, coauthors=tuple(authors[1:]))]


def _filed_shape(what: str) -> tuple[WritingKind, bool] | None:
    """A ``filed`` object's writing kind and whether it is plural, or ``None``."""
    for pattern, plural in (
        (_SINGLE_ADJ_RE, False),
        (_PLURAL_ADJ_RE, True),
        (_SINGLE_DESC_RE, False),
        (_PLURAL_DESC_RE, True),
    ):
        if (found := pattern.match(what)) is not None:
            kind = _writing_kind(found.group("desc"))
            return None if kind is None else (kind, plural)
    return None


def _separate_joins(text: str | None, problems: list[str]) -> tuple[Join, ...] | None:
    """A separate writing's joiners; ``None`` when the list does not read."""
    if not text:
        return ()
    chunks = _joins(text, problems)
    if not chunks:
        return None
    joins: list[Join] = []
    for names, q in chunks:
        if names == [_ALL_OTHERS]:
            problems.append("a separate writing cannot be joined by all other Members")
            return None
        joins.extend(Join(name, q) for name in names)
    return tuple(joins)


class ScotusSyllabusGrammar:
    """:func:`parse_syllabus_lineup` behind the lineup-grammar shape.

    Structurally a :class:`~fedcourtsai.pipeline.lineup.LineupGrammar`.
    """

    court: Final = COURT
    name: Final = GRAMMAR_NAME
    version: Final = GRAMMAR_VERSION

    def parse(self, text: str, *, bench: Sequence[str]) -> Lineup:
        return parse_syllabus_lineup(text, bench=bench)


#: The grammar instance a channel reads syllabus paragraphs with.
SCOTUS_SYLLABUS: Final = ScotusSyllabusGrammar()
