"""The Supreme Court's order-stage grammars: noted votes and separate-writing headers.

Two grammars over the lineup model (:mod:`fedcourtsai.pipeline.lineup`), for
the per-Justice acts the Court publishes at the cert and interim stages. Each
reads one piece of text and stamps its own name and version on the
:class:`~fedcourtsai.pipeline.lineup.Lineup` it returns; the channel that
finds the pieces and assembles one order's reading from them is
:mod:`fedcourtsai.pipeline.order_lineups`.

**Order-list notations** (:data:`NOTATIONS_GRAMMAR`). The sentences an order
prints after its disposition, in an order list's entry for a docket or at the
foot of an order published with its opinions::

    The petition for a writ of certiorari is denied. Justice Thomas and
    Justice Alito would grant the petition for a writ of certiorari.

- *A noted vote*: ``X [and Y] would grant|deny the petition|application …``
  — ``grant`` or ``deny`` on the shared vote vocabulary. The object must be
  the petition (``certiorari``, a writ) or the application (a stay, an
  injunction, a vacatur); a noted vote on a motion or a petition for
  rehearing, or one limited ``in part``, ``as to`` or ``except`` something,
  is not read.
- *An unwritten dissent or concurrence*: ``X dissents from the denial of
  certiorari`` (``grant``), ``X and Y dissent from the grant of the
  application`` (``deny``), and ``X concurs in …`` the other way round. A
  bare ``X dissents.`` names no act, so it is not read.
- *Non-participation*: ``X took no part in the consideration or decision of
  this petition|application|case`` — ``did-not-participate``, since the
  sentence does not say whether it is a recusal.
- *Not a vote*: ``… presented to Justice X and by him referred to the Court``
  names the Circuit Justice who received the application and is set aside.

**Separate-writing headers** (:data:`HEADERS_GRAMMAR`). The first sentence
of a writing published with an order — in the Court's *Opinions Relating to
Orders*, appended to an order list, or printed inline in a list entry with a
colon::

    JUSTICE ALITO, with whom JUSTICE THOMAS joins, dissenting from the
    denial of certiorari.
    Statement of JUSTICE SOTOMAYOR respecting the denial of certiorari.

- The writing's kind comes from its role word: ``dissenting`` a dissent
  (``dissenting in part`` and ``concurring in part and dissenting in part``
  the mixed kind), ``concurring`` a concurrence (``in the judgment`` its own
  kind), ``respecting`` or a ``Statement of`` a statement.
- A vote is read from the role's object only where it says one: a dissent
  from a *denial* of certiorari or of an application is ``grant``, from a
  *grant* is ``deny``; a concurrence in a denial is ``deny``, in a grant
  ``grant``. Author and full joiners share it; a joiner ``as to`` part of a
  writing gets no vote. A statement, a concurrence in the judgment, a mixed
  writing, and a bare ``dissenting`` (a dissent from a summary disposition,
  whose side the header does not say) record the writing and no vote.

**Both grammars refuse rather than guess.** A name the roster
(:mod:`fedcourtsai.pipeline.justices`) does not carry, a Justice off the
bench, or a Justice read two ways is a ``problem`` in either grammar; for
notations, so is an object the grammar does not read and any leftover
sentence shaped like a Justice's act that no rule read. Any problem empties
the vote list: an unread sentence could be the very notation that moves a
Justice. A header the grammar cannot read yields no writing and a problem;
a header whose object it does not read (a motion, a petition for
rehearing, part of the matter) yields its writing and no vote. "The Chief Justice" resolves to the
bench's Chief (:data:`~fedcourtsai.pipeline.justices.CHIEF_JUSTICES`), never to
whoever is most senior.

**Never complete.** A vote list read from an order is always partial
(``complete=False``): a Justice who noted nothing is unobserved, not a vote to
deny. Whether each participating Justice *wrote* can be observed, but only
across every document published with the order, so ``writings_complete`` is
the channel's to set, never a single piece's.

**Text shapes.** The slip-opinion small capitals leave a space after the
initial (``J USTICE``, ``T HOMAS``); it is closed up where the result is a
title word or a roster surname. Line-end hyphenation before a lowercase letter
is closed up, whitespace collapsed, and matching is case-blind.

The two grammars share the name reader and the normalization below, so a
change to either bumps **both** versions. Both also read what
:func:`~fedcourtsai.pipeline.order_lineups.split_document` cuts, so a change to
the split that can hand either grammar different text bumps both as well.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from ..schemas import VoteValue
from .justices import chief_on_bench, resolve_surname
from .lineup import Join, Lineup, Writing, WritingKind

#: The court these grammars read, as the case id prints it.
COURT: Final = "scotus"
#: The notation grammar's stamp.
NOTATIONS_GRAMMAR: Final = "scotus-order-notations"
#: Bump whenever the same notation text could read differently.
NOTATIONS_VERSION: Final = 3
#: The separate-writing header grammar's stamp.
HEADERS_GRAMMAR: Final = "scotus-writing-headers"
#: Bump whenever the same header could read differently.
HEADERS_VERSION: Final = 3

_TITLE_WORDS: Final = frozenset({"JUSTICE", "JUSTICES", "THE", "CHIEF"})
_SPLIT_INITIAL_RE = re.compile(r"\b([A-Z]) ([A-Za-z]{2,})\b")
_LINE_HYPHEN_RE = re.compile(r"([A-Za-z])-[ \t]*\n\s*([a-z])")

_SURNAME = r"[A-Za-z][A-Za-z'\-]+"
_NAME = rf"(?:the\s+chief\s+justice|chief\s+justice\s+{_SURNAME}|justice\s+{_SURNAME})"
# The two separators never both match one text (", and" is the first's), so a
# long list that fails to match costs linear, not exponential, backtracking.
_NAME_LIST = rf"{_NAME}(?:\s*,\s*(?:and\s+)?{_NAME}|\s+and\s+{_NAME})*"
_NAME_RE = re.compile(_NAME, re.I)
# A sentence ends at a period followed by a capital, or at the end of text.
_SENTENCE_END = r"(?=\.\s+(?-i:[A-Z(])|\.\s*$|;|$)"

_NOTED_RE = re.compile(
    rf"(?P<names>{_NAME_LIST})\s+would\s+(?P<verb>grant|deny)\b(?P<object>.*?){_SENTENCE_END}",
    re.I,
)
_UNWRITTEN_RE = re.compile(
    rf"(?P<names>{_NAME_LIST})\s+(?P<verb>dissents?|concurs?)\b(?P<object>.*?){_SENTENCE_END}",
    re.I,
)
_ABSENT_RE = re.compile(
    rf"(?P<names>{_NAME_LIST})\s+took\s+no\s+part\s+in\s+the\s+"
    r"(?:consideration\s+(?:or|and)\s+decision|consideration|decision)\s+of\s+"
    r"(?:this|these|the|that|those)\s+(?P<noun>[a-z]+)",
    re.I,
)
_REFERRED_RE = re.compile(
    rf"\b(?:addressed|presented|submitted|directed)\s+to\s+{_NAME}"
    r"(?:\s+and\s+(?:by\s+(?:him|her)\s+)?referred\s+to\s+the\s+Court)?",
    re.I,
)
_LEFTOVER_RE = re.compile(
    rf"{_NAME}\s*,?\s+(?:would|dissents?|dissenting|concurs?|concurring|respecting"
    r"|took|votes?|joins?|joined)\b"
    r"|\btook\s+no\s+part\b"
    r"|\bstatement\s+of\s+(?:the\s+)?(?:chief\s+)?justice\b"
    r"|\bwould\s+(?:grant|deny)\s+(?:the\s+|a\s+)?(?:petition|application|stay|certiorari)\b",
    re.I,
)
_FORTHCOMING_RE = re.compile(
    r"\b(?:opinions?|statements?|dissents?)\s+(?:to\s+follow|will\s+(?:be\s+)?(?:filed|issued|follow))"
    r"|\bwill\s+file\s+(?:an?\s+)?(?:opinion|statement|dissent)",
    re.I,
)
_OBJECT_RE = re.compile(
    r"^\s*(?:the\s+|a\s+|an\s+)?"
    r"(?P<noun>petitions?|applications?|certiorari|stays?|injunctions?|motions?|writs?)\b"
    r"(?P<rest>.*)$",
    re.I | re.S,
)
_PARTIAL_RE = re.compile(r"\bin\s+part\b|\bas\s+to\b|\bexcept\b|\bto\s+the\s+extent\b", re.I)
_ACT_RE = re.compile(
    r"^\s*(?:from|in)?\s*(?:the\s+)?(?:Court's\s+)?(?P<act>denials?|grants?)\s+of\s+(?P<target>.+)$",
    re.I | re.S,
)

# A header: authors, an optional joiner clause, and a role without a comma,
# ending at the sentence's period (or an inline writing's colon).
_JOINS = (
    rf"(?P<joins>{_NAME_LIST})\s+joins?"
    r"(?P<scope>\s+(?:only\s+)?(?:as\s+to|except\s+as\s+to|with\s+respect\s+to)\s+[^,.:]+?)?"
)
_HEADER_RE = re.compile(
    rf"^\s*(?P<statement>statement\s+of\s+)?(?P<authors>{_NAME_LIST})"
    rf"(?:\s*,\s*with\s+whom\s+{_JOINS})?"
    r"(?:\s*,?\s*(?P<role>(?:dissenting|concurring|respecting)\b[^.:,]*?))?"
    # The period must end the sentence, not an abbreviation a body sentence
    # carries ("… in Doe v. Roe", "… J. Smith").
    r"(?<!\sv)(?<!\sV)(?<!\s(?-i:[A-Z]))\s*(?P<end>[.:])",
    re.I,
)
# Unwritten acts: from which act of the Court, and the side that implies.
_DISSENT_SIDES: Final = {"denial": VoteValue.grant, "grant": VoteValue.deny}
_CONCUR_SIDES: Final = {"denial": VoteValue.deny, "grant": VoteValue.grant}


def _join_initial(match: re.Match[str]) -> str:
    joined = match.group(1) + match.group(2)
    if joined.upper() in _TITLE_WORDS or resolve_surname(joined) is not None:
        return joined
    return match.group(0)


def normalize_order_text(text: str) -> str:
    """Text as both grammars read it: one line, small-caps splits closed up.

    Unicode-normalized (curly apostrophes fold), line-end hyphenation before a
    lowercase letter closed up (``dis-`` / ``senting``), a small-caps split
    initial closed up where the result is a title word or a roster surname
    (``J USTICE``, ``T HOMAS``), and whitespace collapsed.
    """
    text = unicodedata.normalize("NFKC", text).replace("\u2019", "'").replace("\u2018", "'")
    text = _LINE_HYPHEN_RE.sub(r"\1\2", text)
    text = " ".join(text.split())
    return _SPLIT_INITIAL_RE.sub(_join_initial, text)


def match_header(text: str) -> str | None:
    """The header sentence ``text`` opens with, or ``None`` when it opens with none.

    ``text`` is normalized first. A ``Statement of`` a Justice needs no role
    word; any other header does, so a notation (``JUSTICE X would grant …``)
    or a sentence of prose that merely opens on a name is never a header.
    """
    normalized = normalize_order_text(text)
    match = _HEADER_RE.match(normalized)
    if match is None or (match.group("role") is None and match.group("statement") is None):
        return None
    return match.group(0).strip()


@dataclass
class _Names:
    """Resolves printed names against one bench, collecting problems."""

    bench: tuple[str, ...]
    chief: str | None
    problems: list[str]

    def read(self, chunk: str) -> list[str] | None:  # noqa: PLR0911 - one refusal per name rule
        """Every Justice a matched name list names, or ``None`` with a problem."""
        resolved: list[str] = []
        for match in _NAME_RE.finditer(chunk):
            words = match.group(0).split()
            lowered = [w.lower() for w in words]
            if lowered[:3] == ["the", "chief", "justice"]:
                name = self.chief
                if name is None:
                    self.problems.append("'The Chief Justice' names no Chief on this bench")
                    return None
            else:
                printed = words[-1]
                name = resolve_surname(printed)
                if name is None:
                    self.problems.append(f"unrecognized Justice name {match.group(0)!r}")
                    return None
                if lowered[0] == "chief" and name != self.chief:
                    self.problems.append(f"{name} is printed as Chief Justice but is not the Chief")
                    return None
            if name not in self.bench:
                self.problems.append(f"{name} is not on the bench")
                return None
            if name in resolved:
                self.problems.append(f"{name} is named twice in {chunk!r}")
                return None
            resolved.append(name)
        if not resolved:
            self.problems.append(f"no Justice named in {chunk!r}")
            return None
        return resolved


def _bench(bench: Sequence[str]) -> tuple[str, ...]:
    """The bench in roster spelling; an unknown or repeated name is a caller error."""
    roster: list[str] = []
    for name in bench:
        surname = resolve_surname(name)
        if surname is None:
            raise ValueError(f"bench name {name!r} is not on the roster")
        if surname in roster:
            raise ValueError(f"bench names {surname!r} twice")
        roster.append(surname)
    return tuple(roster)


def _record(
    votes: dict[str, VoteValue], names: Iterable[str], vote: VoteValue, problems: list[str]
) -> None:
    for name in names:
        held = votes.get(name)
        if held is not None and held is not vote:
            problems.append(f"{name} is read both as {held} and as {vote}")
        votes[name] = vote


def _matter(raw: str, problems: list[str], *, what: str) -> bool:
    """Whether a noted act's object is the petition or the application, whole.

    Anything else — a motion, a petition for rehearing, a vote limited to part
    of the matter, or an object the grammar does not know — is a problem.
    """
    match = _OBJECT_RE.match(raw)
    if match is None:
        problems.append(f"{what} on an unread object {raw.strip()!r}")
        return False
    noun = match.group("noun").lower()
    rest = match.group("rest")
    if noun.startswith("motion"):
        problems.append(f"{what} on a motion is not read: {raw.strip()!r}")
        return False
    if "rehearing" in rest.lower()[:40]:
        problems.append(f"{what} on a petition for rehearing is not read: {raw.strip()!r}")
        return False
    if _PARTIAL_RE.search(rest):
        problems.append(f"{what} limited to part of the matter is not read: {raw.strip()!r}")
        return False
    return True


def parse_order_notations(text: str, *, bench: Sequence[str], chief: str | None = None) -> Lineup:
    """Read one order's notation sentences into a partial :class:`Lineup`.

    ``text`` is the order as printed for one docket or group of dockets —
    disposition and notations — without any separate writing's header or
    body. ``bench`` is the Justices in service on the order's date; ``chief``
    defaults to the bench's Chief Justice. The lineup is never ``complete``
    and never ``writings_complete``; any problem empties its vote list.
    """
    roster = _bench(bench)
    problems: list[str] = []
    names = _Names(roster, chief if chief is not None else chief_on_bench(roster), problems)
    normalized = normalize_order_text(text)
    votes: dict[str, VoteValue] = {}
    spans: list[tuple[int, int]] = [m.span() for m in _REFERRED_RE.finditer(normalized)]

    for match in _NOTED_RE.finditer(normalized):
        spans.append(match.span())
        who = names.read(match.group("names"))
        if who is None or not _matter(match.group("object"), problems, what="a noted vote"):
            continue
        vote = VoteValue.grant if match.group("verb").lower() == "grant" else VoteValue.deny
        _record(votes, who, vote, problems)

    for match in _UNWRITTEN_RE.finditer(normalized):
        spans.append(match.span())
        who = names.read(match.group("names"))
        if who is None:
            continue
        act = _ACT_RE.match(match.group("object"))
        sides = (
            _DISSENT_SIDES if match.group("verb").lower().startswith("dissent") else _CONCUR_SIDES
        )
        if act is None:
            problems.append(
                f"an unwritten {match.group('verb').lower()} with no act read: "
                + repr(match.group(0))
            )
            continue
        if not _matter(act.group("target"), problems, what="an unwritten vote"):
            continue
        _record(votes, who, sides[act.group("act").lower().rstrip("s")], problems)

    for match in _ABSENT_RE.finditer(normalized):
        spans.append(match.span())
        who = names.read(match.group("names"))
        noun = match.group("noun").lower().rstrip("s")
        if noun not in {"petition", "application", "case", "matter"}:
            problems.append(f"non-participation in a {noun} is not read: {match.group(0)!r}")
            continue
        if who is not None:
            _record(votes, who, VoteValue.did_not_participate, problems)

    leftover = list(normalized)
    for start, end in spans:
        leftover[start:end] = " " * (end - start)
    rest = "".join(leftover)
    for match in _LEFTOVER_RE.finditer(rest):
        problems.append(f"unread notation near {rest[match.start() : match.start() + 80]!r}")
    if (found := _FORTHCOMING_RE.search(normalized)) is not None:
        problems.append(f"a writing is announced as forthcoming: {found.group(0)!r}")

    return Lineup(
        court=COURT,
        grammar=NOTATIONS_GRAMMAR,
        grammar_version=NOTATIONS_VERSION,
        bench=roster,
        votes=MappingProxyType({} if problems else votes),
        problems=tuple(problems),
    )


def _role(  # noqa: PLR0911 - one return per role shape the grammar reads
    role: str | None, *, statement: bool, problems: list[str]
) -> tuple[WritingKind, VoteValue | None] | None:
    """A header role's writing kind and the vote it implies, or ``None`` if unread."""
    if role is None:
        return (WritingKind.statement, None) if statement else None
    words = " ".join(role.lower().split())
    word, _, rest = words.partition(" ")
    if statement or word == "respecting":
        if statement and word != "respecting":
            problems.append(f"a statement with the role {role!r} is not read")
            return None
        return WritingKind.statement, None
    if rest.startswith("in part and dissenting in part") or (
        word == "dissenting" and rest.startswith("in part")
    ):
        return WritingKind.concurrence_in_part_dissent_in_part, None
    if word == "concurring" and rest.startswith("in part"):
        problems.append(f"the role {role!r} is not read")
        return None
    if word == "concurring" and re.match(r"^in\s+(?:the\s+)?judgment\b", rest):
        return WritingKind.concurrence_in_judgment, None
    kind = WritingKind.dissent if word == "dissenting" else WritingKind.concurrence
    act = _ACT_RE.match(rest) if rest else None
    if act is None:
        return kind, None
    target = act.group("target")
    matter = _OBJECT_RE.match(target)
    if matter is None or matter.group("noun").lower().startswith("motion"):
        return kind, None
    if _PARTIAL_RE.search(matter.group("rest")) or "rehearing" in target.lower():
        return kind, None
    sides = _DISSENT_SIDES if kind is WritingKind.dissent else _CONCUR_SIDES
    return kind, sides[act.group("act").lower().rstrip("s")]


def parse_writing_header(text: str, *, bench: Sequence[str], chief: str | None = None) -> Lineup:
    """Read one separate writing's header sentence into a partial :class:`Lineup`.

    Returns a lineup holding the one writing (author, coauthors, joiners) and
    the vote its role implies for the author and every full joiner, if it
    implies one. A header that does not read yields no writing and a problem.
    """
    roster = _bench(bench)
    problems: list[str] = []
    names = _Names(roster, chief if chief is not None else chief_on_bench(roster), problems)
    normalized = normalize_order_text(text)
    match = _HEADER_RE.match(normalized)
    writings: tuple[Writing, ...] = ()
    votes: dict[str, VoteValue] = {}
    if match is None or match.end() != len(normalized):
        problems.append(f"unreadable writing header {normalized!r}")
    else:
        authors = names.read(match.group("authors"))
        joiners = names.read(match.group("joins")) if match.group("joins") else []
        shape = _role(
            match.group("role"), statement=bool(match.group("statement")), problems=problems
        )
        if shape is None and not problems:
            problems.append(f"unreadable writing header {normalized!r}")
        if authors is not None and joiners is not None and shape is not None:
            scope = match.group("scope")
            qualifier = " ".join(scope.split()) if scope else None
            if overlap := sorted(set(authors) & set(joiners)):
                problems.append(f"{', '.join(overlap)} both writes and joins one writing")
            kind, vote = shape
            writings = (
                Writing(
                    kind,
                    authors[0],
                    tuple(Join(name, qualifier) for name in joiners),
                    coauthors=tuple(authors[1:]),
                ),
            )
            if vote is not None:
                _record(votes, authors, vote, problems)
                if qualifier is None:
                    _record(votes, joiners, vote, problems)
    return Lineup(
        court=COURT,
        grammar=HEADERS_GRAMMAR,
        grammar_version=HEADERS_VERSION,
        bench=roster,
        writings=writings,
        votes=MappingProxyType({} if problems else votes),
        problems=tuple(problems),
    )


class OrderNotationsGrammar:
    """:func:`parse_order_notations` behind the lineup-grammar shape."""

    court: Final = COURT
    name: Final = NOTATIONS_GRAMMAR
    version: Final = NOTATIONS_VERSION

    def parse(self, text: str, *, bench: Sequence[str], chief: str | None = None) -> Lineup:
        return parse_order_notations(text, bench=bench, chief=chief)


class WritingHeadersGrammar:
    """:func:`parse_writing_header` behind the lineup-grammar shape."""

    court: Final = COURT
    name: Final = HEADERS_GRAMMAR
    version: Final = HEADERS_VERSION

    def parse(self, text: str, *, bench: Sequence[str], chief: str | None = None) -> Lineup:
        return parse_writing_header(text, bench=bench, chief=chief)


#: The grammar instances a channel reads order text and headers with.
ORDER_NOTATIONS: Final = OrderNotationsGrammar()
WRITING_HEADERS: Final = WritingHeadersGrammar()
