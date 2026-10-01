"""The per-opinion record: every opinion in a decided case, its author, joiners and length.

A Term's opinion statistics — opinions authored by each Justice, opinion
lengths, voting alignments with part-joins — count *opinions*, not cases, so
they need one row per opinion: the Court's opinion and every separate writing,
in the order the Court printed them. This module reads that record from the
Court's own documents and holds it **corpus-side**, in the ``opinions`` table
(``corpus/README.md``): a historical decision record, like the case row's
decision columns (:mod:`.decision_record`), and never an outcome in the git
ledger, which holds only what the pipeline forecast.

**The source.** One listing row of a Term's opinions listing
(:mod:`.opinion_lineups`) is one document: the slip opinion, or the
preliminary print once it replaces the slip. Each document is fetched through
the host-scoped :class:`~fedcourtsai.supremecourt.SupremeCourtClient`, read
whole, and split at each opinion's header.

**Who wrote what.** For a signed decision the syllabus lineup paragraph is the
record of each writing's kind, author, coauthors and joiners, partial joins
included — read by the syllabus grammar (:mod:`.syllabus_lineup`), which
keeps a partial join's printed limit ("as to Part II-B", "except as to Part
III-B") as its qualifier. The record stores that phrase on the join; a join
without one is a join in full. A per curiam prints no lineup, so its record
comes from the opinion headers alone: the per curiam, then each separate
writing's header (``JUSTICE X, with whom JUSTICE Y joins as to Part I,
dissenting.``) read for its author, kind and joiners.

**The cross-check.** A signed document is recorded only when its headers and
its syllabus agree: the document splits into exactly as many opinions as the
syllabus names, in the same order, and each header names the same author or
authors and a compatible kind. Anything else — a header not found, a header
the syllabus does not name, a kind that disagrees — refuses the whole
document, with the reason, rather than recording a guess.

**The word count** (:func:`count_words`, the rule :data:`WORD_RULE` version
:data:`WORD_RULE_VERSION`). Counted over one opinion's text from its header
sentence to the next opinion's header or the end of the document:

- **footnotes are in**: each opinion's footnotes count toward it, and
  ``footnote_words`` reports their share;
- **excluded**: the syllabus or headnote, the caption (court, docket number,
  parties, the writ, the bracketed date), the preliminary print's counsel
  listing and its amicus-brief and "Together with" notes, running heads and
  page numbers, and the print's "Page Proof Pending Publication" watermark;
- **tokens**: a hyphen ending a line is closed up, so a word broken across
  lines counts once; the text then splits on whitespace and on the em dash,
  and a token counts when it holds at least one letter or digit. So a
  hyphenated compound ("well-settled") and a number range ("404\u2013405") are one
  word each, and a citation counts token by token ("19 How. 393" is three;
  "§1983" one, and "§ 1983" one too, since a bare "§" holds no letter or
  digit); ellipsis dots and stray punctuation are not words;
- **reference marks**: a footnote's own number at the head of the note is not
  a word, nor is a reference mark the text layer separates from its word
  (``… 75. 1 Smith``) where it is the next expected number after punctuation;
  a mark printed against its word ("realms.2") adds nothing either way.

Two text layers are read, because each format extracts cleanly in one mode
only: the slip opinion in pypdf's layout mode (its plain mode splits words at
kerning, ``pr esent``), where an opinion opens on a new page under the Court's
caption and its footnotes sit below an em-dash rule; and the preliminary print
in plain mode (its layout mode letter-spaces), where opinions run on within a
page and footnotes are told from body text by their smaller type.

**Not read.** A listing row linked into a whole preliminary-print or
bound volume (the Terms before OT2020 on the Court's listings) is refused, as
is any document whose text does not extract.

**Fill-only.** A recorded document is never read again, so a new
:data:`WORD_RULE_VERSION` or reader version reaches stored rows only through a
pass built to replace them, which does not exist yet; each row says which
versions it was read under.

**Nothing a cell sees reads this.** The table is read by no ``query``
retrieval row, provisioning step, outcome, mint or scoring gate.
"""

from __future__ import annotations

import io
import json
import re
import sqlite3
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Final, Literal, Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .. import corpus
from .documents import extract_pdf_text
from .justices import bench_on, chief_on_bench, resolve_surname
from .lineup import LEAD_KINDS, Join, Lineup, Writing, WritingKind
from .opinion_lineups import (
    TEXT_CHAR_CAP,
    OpinionListing,
    read_lineup,
)
from .order_grammars import normalize_order_text
from .syllabus_lineup import writing_kind

#: The word-count rule's name, stamped on every recorded opinion.
WORD_RULE: Final = "scotus-opinion-words"
#: Bump whenever the same document could count differently (stored rows keep theirs).
WORD_RULE_VERSION: Final = 1
#: The opinion-header reader's stamp, on a per curiam's writings.
HEADER_READER: Final = "scotus-opinion-headers"
#: Bump whenever the same headers could read differently.
HEADER_READER_VERSION: Final = 1

SLIP: Final = "slip"
PRELIMINARY_PRINT: Final = "preliminary-print"

# --- counting -----------------------------------------------------------------

_LINE_HYPHEN_RE = re.compile(r"(\w)-[ \t]*\n[ \t]*(\w)")
_TOKEN_SPLIT_RE = re.compile(r"[\s—]+")
_WORD_CHAR_RE = re.compile(r"[^\W_]")
_TRAILING_PUNCT: Final = tuple(".,;:)]\u201d\u2019\"'")


def _tokens(text: str) -> list[str]:
    joined = _LINE_HYPHEN_RE.sub(r"\1\2", text)
    return [token for token in _TOKEN_SPLIT_RE.split(joined) if _WORD_CHAR_RE.search(token)]


def count_words(text: str) -> int:
    """The number of words in ``text`` under :data:`WORD_RULE`.

    A hyphen ending a line is closed up first; the text then splits on
    whitespace and the em dash, and a token counts when it holds a letter or a
    digit. Text selection (what is an opinion's text at all) is the splitter's
    job, not this function's.
    """
    return len(_tokens(text))


def _strip_reference_marks(text: str) -> str:
    """``text`` with reference marks the text layer split from their words removed.

    A standalone integer is a mark only where it is the next expected number
    (from 1) and follows a token ending in punctuation, which is how a
    superscript the text layer spaced off its word reads (``… 75. 1 Smith``).
    """
    out: list[str] = []
    expected = 1
    previous = ""
    for line in _LINE_HYPHEN_RE.sub(r"\1\2", text).splitlines():
        kept: list[str] = []
        for token in line.split():
            if token == str(expected) and previous.endswith(_TRAILING_PUNCT):
                expected += 1
                continue
            kept.append(token)
            previous = token
        out.append(" ".join(kept))
    return "\n".join(out)


# --- headers ------------------------------------------------------------------

_SURNAME = r"[A-Za-z][A-Za-z'\-]+"
_NAME = rf"(?:the\s+chief\s+justice|chief\s+justice\s+{_SURNAME}|justice\s+{_SURNAME})"
_NAME_LIST = rf"{_NAME}(?:\s*,\s*(?:and\s+)?{_NAME}|\s+and\s+{_NAME})*"
_NAME_RE = re.compile(_NAME, re.I)
_MARK = r"(?:\s*(?:[*†‡]+|\d{1,2}))?"
_ROLE_WORDS = r"(?:concurring|dissenting)(?:\s+(?:in|part|the|judgment|and|concurring|dissenting))*"
_SEPARATE_RE = re.compile(
    rf"^(?P<authors>{_NAME_LIST})(?P<with>\s*,\s*with\s+whom\s+.+?)?\s*,\s*"
    rf"(?P<role>{_ROLE_WORDS}){_MARK}\s*\.",
    re.I,
)
# A lead needs no sentence end in view: a plurality's runs for many lines.
_LEAD_RE = re.compile(
    rf"^(?P<authors>{_NAME_LIST})\s+(?P<verb>delivered|announced)\s+(?:the|an)\s+"
    r"(?:opinion|judgment)\b(?P<rest>[^.]{0,600}\.)?",
    re.I,
)
_STATEMENT_RE = re.compile(rf"^statement\s+of\s+(?P<authors>{_NAME_LIST}){_MARK}\s*\.", re.I)
_PER_CURIAM_RE = re.compile(rf"^per\s+curiam{_MARK}\s*\.", re.I)
# A join clause's limit runs to the next clause ("and with whom …") or the
# clause's end; a comma continues it only into a list of parts.
_SCOPE_CHAR = r"(?:(?!,?\s*and\s+with\s+whom\b)[^,])"
_JOIN_CLAUSE_RE = re.compile(
    rf"with\s+whom\s+(?P<names>{_NAME_LIST})\s+joins?\b(?P<scope>{_SCOPE_CHAR}*"
    rf"(?:,\s*(?!and\s+with\s+whom)(?:and\s+)?(?:Parts?|[IVXL]+\b|\d|footnotes?){_SCOPE_CHAR}*)*)",
    re.I,
)
# A word the text layer split at a hyphen and a space ("con- curring").
_SPLIT_WORD_RE = re.compile(r"([a-z])- ([a-z])")
_HEADER_START_RE = re.compile(
    r"^\s*(?:(?:the\s+)?chief\s+justice\s|justice\s|per\s+curiam\b|statement\s+of\s)", re.I
)


@dataclass(frozen=True)
class Header:
    """One opinion header as read: its kind, authors, and printed joiners."""

    text: str
    kind: WritingKind | None
    authors: tuple[str, ...]
    joins: tuple[Join, ...] = ()
    lead: bool = False


def _names(chunk: str, bench: Sequence[str]) -> tuple[str, ...] | None:
    chief = chief_on_bench(bench)
    found: list[str] = []
    for match in _NAME_RE.finditer(chunk):
        words = match.group(0).split()
        if [w.lower() for w in words[:3]] == ["the", "chief", "justice"]:
            name = chief
        else:
            name = resolve_surname(words[-1])
        if name is None or name not in bench or name in found:
            return None
        found.append(name)
    return tuple(found) or None


def _joins(clause: str, bench: Sequence[str]) -> tuple[Join, ...] | None:
    joins: list[Join] = []
    for match in _JOIN_CLAUSE_RE.finditer(clause):
        names = _names(match.group("names"), bench)
        if names is None:
            return None
        scope = " ".join(match.group("scope").split()).strip(" ,") or None
        joins.extend(Join(name, scope) for name in names)
    return tuple(joins)


def read_header(text: str, *, bench: Sequence[str]) -> Header | None:  # noqa: PLR0911 - one return per header shape
    """The header sentence ``text`` opens with, read, or ``None`` when it opens with none.

    ``text`` is the opinion's first lines, in any case and spacing. A lead
    (``X delivered the opinion of the Court``, ``X announced the judgment``) or
    a per curiam reads as ``lead``; a separate writing's kind is its role's
    (:func:`~.syllabus_lineup.writing_kind`), and a role that reads as no kind
    gives ``kind=None``. Every name must be a roster Justice on ``bench``.
    """
    normalized = _SPLIT_WORD_RE.sub(r"\1\2", normalize_order_text(text))
    if (match := _PER_CURIAM_RE.match(normalized)) is not None:
        return Header(match.group(0), WritingKind.per_curiam, (), lead=True)
    if (match := _LEAD_RE.match(normalized)) is not None:
        authors = _names(match.group("authors"), bench)
        if authors is None:
            return None
        announced = match.group("verb").lower() == "announced"
        kind = WritingKind.plurality if announced else WritingKind.opinion_of_the_court
        return Header(match.group(0).strip(), kind, authors, lead=True)
    if (match := _STATEMENT_RE.match(normalized)) is not None:
        authors = _names(match.group("authors"), bench)
        if authors is None:
            return None
        return Header(match.group(0), WritingKind.statement, authors)
    if (match := _SEPARATE_RE.match(normalized)) is not None:
        authors = _names(match.group("authors"), bench)
        joins = _joins(match.group("with") or "", bench)
        if authors is None or joins is None:
            return None
        return Header(match.group(0), writing_kind(match.group("role")), authors, joins)
    return None


# --- sections -----------------------------------------------------------------


@dataclass
class Section:
    """One opinion's text as split from a document."""

    header: Header
    body: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    next_note: int = 1

    @property
    def words(self) -> int:
        return count_words(_strip_reference_marks("\n".join(self.body))) + self.footnote_words

    @property
    def footnote_words(self) -> int:
        return count_words("\n".join(self.notes))


_FRONT_NOTE_RE = re.compile(r"\bamic(?:us|i)\b|\btogether\s+with\b", re.I)
_SYMBOL_MARK_RE = re.compile(r"^\s*([*†‡]+)\s*(?=\S)")
_NUMBER_MARK_RE = re.compile(r"^\s*(\d{1,3})\s+(?=\S)")


@dataclass
class _Notes:
    """Assigns one page's footnote lines to sections, dropping front-matter notes.

    A note opens at a line beginning with a symbol mark (``*``, ``†``) or with
    the next expected number of the section it belongs to. Numbering restarts
    with each opinion, so the notes numbered 1 on a page where opinions open
    are assigned by count: when the previous opinion already has notes, each
    opens the next opened opinion's; when it has none, those beyond one per
    opened opinion are the previous opinion's, taken first. The residue this
    cannot tell apart — a previous opinion whose first note falls on its last
    page, beside an opened opinion with no note on that page — is stated in
    the rule rather than detected. Lines before the page's first mark continue
    the previous page's last note. A symbol-marked note about amicus briefs or
    consolidated cases is the caption's, not an opinion's, and is dropped with
    its continuations.
    """

    dropping: bool = False
    problems: list[str] = field(default_factory=list)

    def assign(self, lines: Iterable[str], current: Section | None, starts: list[Section]) -> None:
        pending = list(starts)
        target = current if current is not None else (pending.pop(0) if pending else None)
        page = [line for line in lines if line.strip()]
        ones = sum(1 for line in page if (m := _NUMBER_MARK_RE.match(line)) and m.group(1) == "1")
        for raw in page:
            if not raw.strip():
                continue
            line = raw
            symbol = _SYMBOL_MARK_RE.match(line)
            number = _NUMBER_MARK_RE.match(line)
            if symbol is not None:
                self.dropping = bool(_FRONT_NOTE_RE.search(line[:200]))
                if self.dropping:
                    continue
                line = line[symbol.end() :]
            elif number is not None and target is not None:
                value = int(number.group(1))
                if value == 1:
                    if pending and (target.next_note > 1 or ones <= len(pending)):
                        target = pending.pop(0)
                    ones -= 1
                if value == target.next_note:
                    target.next_note += 1
                    self.dropping = False
                    line = line[number.end() :]
            if self.dropping or target is None:
                continue
            target.notes.append(line)


# The slip opinion's caption and the bracketed date that closes it.
_CAPTION_RE = re.compile(r"^\s*SUPREME COURT OF THE UNITED STATES\s*$")
_BRACKET_DATE_RE = re.compile(r"^\s*\[\s*[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}\s*\]\s*$")
_SLIP_RULE_RE = re.compile(r"^\s*—{3,}\s*$")
_HEADER_LINES: Final = 6


def _caption_end(lines: Sequence[str]) -> int | None:
    """The index after a page's caption date, when the page opens an opinion."""
    caption = next((i for i, line in enumerate(lines[:16]) if _CAPTION_RE.match(line)), None)
    if caption is None:
        return None
    for i in range(caption + 1, min(len(lines), caption + 30)):
        if _BRACKET_DATE_RE.match(lines[i]):
            return i + 1
    return None


def _without_head(lines: Sequence[str], count: int = 2) -> list[str]:
    """A page's lines after its first ``count`` non-blank lines (the running heads)."""
    seen = 0
    for i, line in enumerate(lines):
        if line.strip():
            seen += 1
            if seen == count:
                return list(lines[i + 1 :])
    return []


def split_slip(pages: Sequence[str], *, bench: Sequence[str]) -> tuple[list[Section], list[str]]:
    """Split a slip opinion's layout-mode page texts into its opinions.

    An opinion opens on the page that carries the Court's caption and its
    bracketed date; its text runs from the line after the date. Every other
    page loses its two running-head lines; below an em-dash rule a page's lines
    are footnotes. Pages before the first opinion (the syllabus) are skipped.
    """
    sections: list[Section] = []
    problems: list[str] = []
    notes = _Notes()
    for index, page in enumerate(pages):
        lines = page.splitlines()
        start = _caption_end(lines)
        if start is not None:
            content = lines[start:]
            first = "\n".join(line for line in content[:_HEADER_LINES] if line.strip())
            header = read_header(first, bench=bench)
            if header is None:
                problems.append(f"page {index + 1}: an opinion opens with an unread header")
                header = Header(" ".join(first.split())[:120], None, ())
            sections.append(Section(header))
        elif not sections:
            continue
        else:
            content = _without_head(lines)
        rule = next((i for i, line in enumerate(content) if _SLIP_RULE_RE.match(line)), None)
        body = content if rule is None else content[:rule]
        sections[-1].body.extend(line for line in body if line.strip())
        if rule is not None:
            notes.assign(content[rule + 1 :], sections[-1], [])
    return sections, [*problems, *notes.problems]


# --- the preliminary print ------------------------------------------------------

_WATERMARK: Final = "Page Proof Pending Publication"
# The print's closing page, the Reporter's list of revisions: no opinion's text.
_REPORTERS_NOTE_RE = re.compile(r"^\s*Reporter[\u2019']s\s+Note\s*$")


@dataclass(frozen=True)
class PrintLine:
    """One line of a preliminary print's plain text, with its dominant type size."""

    text: str
    size: float


def print_pages(data: bytes) -> list[list[PrintLine]]:
    """A preliminary print's pages as lines with type sizes, from pypdf's plain mode.

    Each line's size is the size of the text run that contributes most of its
    characters, so a line of footnote text reads small and a body line with a
    superscript mark reads at body size. The watermark is removed.
    """
    reader = PdfReader(io.BytesIO(data))
    pages: list[list[PrintLine]] = []
    for page in reader.pages:
        runs: list[tuple[str, float]] = []

        def visit(
            text: str,
            cm: Any,
            tm: Any,
            font: Any,
            size: float,
            runs: list[tuple[str, float]] = runs,
        ) -> None:
            del font
            scale = abs(float(tm[3]) * float(cm[3])) or abs(float(tm[0]) * float(cm[0])) or 1.0
            runs.append((text.replace(_WATERMARK, ""), round(float(size) * scale, 1)))

        page.extract_text(visitor_text=visit)
        lines: list[PrintLine] = []
        text = ""
        weights: Counter[float] = Counter()
        for run, size in runs:
            parts = run.split("\n")
            for i, part in enumerate(parts):
                text += part
                weights[size] += len(part.strip())
                if i < len(parts) - 1:
                    if text.strip():
                        lines.append(PrintLine(text, weights.most_common(1)[0][0]))
                    text, weights = "", Counter()
        if text.strip():
            lines.append(PrintLine(text, weights.most_common(1)[0][0]))
        pages.append(lines)
    return pages


def body_size(pages: Sequence[Sequence[PrintLine]]) -> float:
    """The type size most of a print's characters are set in."""
    weights: Counter[float] = Counter()
    for page in pages:
        for line in page:
            weights[line.size] += len(line.text.strip())
    return weights.most_common(1)[0][0] if weights else 0.0


def _print_page_parts(
    page: Sequence[PrintLine], body: float
) -> tuple[list[PrintLine], list[PrintLine]]:
    """A print page's body lines and its trailing small-type (footnote) lines.

    The running heads — up to two leading lines in small type — are dropped.
    """
    small = body - 0.5
    lines = list(page)
    for _ in range(2):
        if lines and lines[0].size < small:
            lines.pop(0)
    end = len(lines)
    while end > 0 and lines[end - 1].size < small:
        end -= 1
    return lines[:end], lines[end:]


def _header_at(lines: Sequence[PrintLine], index: int, bench: Sequence[str]) -> Header | None:
    if not _HEADER_START_RE.match(lines[index].text):
        return None
    window = "\n".join(line.text for line in lines[index : index + _HEADER_LINES])
    return read_header(window, bench=bench)


def split_print(
    pages: Sequence[Sequence[PrintLine]], *, bench: Sequence[str]
) -> tuple[list[Section], list[str]]:
    """Split a preliminary print into its opinions at each header line.

    A header opens at the start of a body-type line. Body lines before the
    first header (the headnote and counsel listing) belong to no opinion, and
    neither do footnotes on pages before it; the closing Reporter's Note page
    ends the text.
    """
    body = body_size(pages)
    sections: list[Section] = []
    notes = _Notes()
    for page in pages:
        if page and _REPORTERS_NOTE_RE.match(page[0].text):
            break
        lines, small = _print_page_parts(page, body)
        current = sections[-1] if sections else None
        opened: list[Section] = []
        for index, line in enumerate(lines):
            header = _header_at(lines, index, bench)
            if header is not None and (header.lead or sections):
                section = Section(header)
                sections.append(section)
                opened.append(section)
            if sections:
                sections[-1].body.append(line.text)
        notes.assign((line.text for line in small), current, opened)
    return sections, notes.problems


# --- reading a document ------------------------------------------------------------


class OpinionJoin(BaseModel):
    """One Justice joining one opinion, in full or as limited by ``qualifier``."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    justice: str
    qualifier: str | None = Field(
        default=None,
        description="The printed limit of a partial join ('as to Part II-B', "
        "'except as to Part III-B'); None is a join in full",
    )


class OpinionEntry(BaseModel):
    """One opinion as recorded: its place, kind, author, joiners and length."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position: int = Field(ge=1, description="Its order in the document, from 1")
    kind: WritingKind
    author: str | None = Field(description="The signing Justice; None for a per curiam")
    coauthors: list[str] = Field(default_factory=list)
    joins: list[OpinionJoin] = Field(default_factory=list)
    scope: str | None = Field(
        default=None, description="A lead opinion's own limit ('except as to Part II')"
    )
    words: int = Field(ge=0, description="Words under the counting rule, footnotes included")
    footnote_words: int = Field(ge=0, description="The footnotes' share of `words`")
    header: str = Field(description="The header sentence as printed (normalized)")


Status = Literal["read", "refused", "skipped"]


class OpinionDocumentReading(BaseModel):
    """One listing row's per-opinion record, or why it has none."""

    model_config = ConfigDict(extra="forbid")

    term: int = Field(description="The October Term (four-digit year)")
    listing_number: str
    docket: str = Field(description="The listing's docket cell as printed")
    dockets: list[str] = Field(default_factory=list, description="Its docket numbers")
    case_id: str | None = None
    name: str
    url: str
    decided: date
    argued: date | None = None
    status: Status
    reason: str | None = None
    source_format: str | None = None
    lineup: str | None = Field(default=None, description="'<reader>/<version>' of the writings")
    opinions: list[OpinionEntry] = Field(default_factory=list)


_DOCKET_TOKEN_RE = re.compile(r"\b\d{2}-\d+\b|\b\d{2}A\d+\b|\b\d+,\s*Orig\.", re.I)


def listed_dockets(entry: OpinionListing) -> list[str]:
    """Every docket number the listing row's docket cell prints, in order."""
    return [
        " ".join(m.group(0).split()).upper().replace("ORIG.", "Orig.")
        for m in _DOCKET_TOKEN_RE.finditer(entry.docket)
    ]


def _base(entry: OpinionListing, **fields: Any) -> OpinionDocumentReading:
    return OpinionDocumentReading.model_validate(
        {
            "term": 2000 + entry.term,
            "listing_number": entry.number,
            "docket": entry.docket,
            "dockets": listed_dockets(entry),
            "name": entry.name,
            "url": entry.url,
            "decided": entry.decided,
            **fields,
        }
    )


def is_preliminary_print(data: bytes) -> bool:
    """Whether a document is the preliminary print rather than the slip opinion."""
    head = extract_pdf_text(data, char_cap=4000).text
    return "PRELIMINARY PRINT" in head.replace(" ", "") or _WATERMARK in head


def _kinds_agree(expected: WritingKind, header: Header) -> bool:
    if expected in LEAD_KINDS:
        return header.lead
    return not header.lead and header.kind is expected


def _cross_check(writings: Sequence[Writing], sections: Sequence[Section]) -> list[str]:
    """Why the split disagrees with the syllabus writings, or nothing."""
    if len(writings) != len(sections):
        printed = "; ".join(s.header.text[:60] for s in sections)
        return [
            f"the syllabus names {len(writings)} opinions, the document splits into "
            f"{len(sections)}: {printed}"
        ]
    problems: list[str] = []
    for position, (writing, section) in enumerate(zip(writings, sections, strict=True), 1):
        header = section.header
        if set(header.authors) != set(writing.authors):
            problems.append(
                f"opinion {position}: the syllabus names {', '.join(writing.authors) or 'none'}, "
                f"the header {', '.join(header.authors) or 'none'}"
            )
        elif not _kinds_agree(writing.kind, header):
            problems.append(
                f"opinion {position}: the syllabus reads {writing.kind}, the header "
                f"{header.kind or 'an unread role'}"
            )
    return problems


def _entries(writings: Sequence[Writing], sections: Sequence[Section]) -> list[OpinionEntry]:
    return [
        OpinionEntry(
            position=position,
            kind=writing.kind,
            author=writing.author,
            coauthors=list(writing.coauthors),
            joins=[OpinionJoin(justice=j.justice, qualifier=j.qualifier) for j in writing.joins],
            scope=writing.scope,
            words=section.words,
            footnote_words=section.footnote_words,
            header=section.header.text,
        )
        for position, (writing, section) in enumerate(zip(writings, sections, strict=True), 1)
    ]


def _per_curiam_writings(sections: Sequence[Section]) -> tuple[list[Writing], list[str]]:
    """A per curiam document's writings, from its headers alone."""
    problems: list[str] = []
    writings: list[Writing] = []
    for position, section in enumerate(sections, 1):
        header = section.header
        if position == 1:
            if header.kind is not WritingKind.per_curiam:
                problems.append(f"the listing says per curiam, the document opens {header.text!r}")
            writings.append(Writing(WritingKind.per_curiam, None))
            continue
        if header.lead or header.kind is None or not header.authors:
            problems.append(f"opinion {position}: unread header {header.text!r}")
            continue
        writings.append(
            Writing(header.kind, header.authors[0], header.joins, coauthors=header.authors[1:])
        )
    return writings, problems


def _stray_headers(sections: Sequence[Section], bench: Sequence[str]) -> list[str]:
    """Header-shaped lines inside an opinion's body: an opinion the split ran past."""
    found: list[str] = []
    for position, section in enumerate(sections, 1):
        lines = section.body
        for index in range(1, len(lines)):
            if not _HEADER_START_RE.match(lines[index]):
                continue
            window = "\n".join(lines[index : index + _HEADER_LINES])
            header = read_header(window, bench=bench)
            if header is not None and not header.lead:
                found.append(f"opinion {position} runs past a header: {header.text[:80]!r}")
    return found


def read_document(entry: OpinionListing, data: bytes) -> OpinionDocumentReading:
    """Split one fetched document into its opinions and record each, or refuse it."""
    per_curiam = entry.author_code == "PC"
    plain = extract_pdf_text(data, char_cap=TEXT_CHAR_CAP)
    if not plain.text.strip():
        return _base(entry, status="refused", reason="the PDF yielded no text")
    lineup: Lineup | None = None
    argued: date | None = None
    decided = entry.decided
    if not per_curiam:
        reading, lineup = read_lineup(entry, plain.text, truncated=plain.truncated)
        argued, decided = reading.argued, reading.decided or entry.decided
        if lineup is None:
            return _base(entry, status="refused", reason=f"syllabus lineup: {reading.reason}")
    try:
        bench = lineup.bench if lineup is not None else bench_on(decided)
    except ValueError as exc:
        return _base(entry, status="refused", reason=str(exc))
    prelim = is_preliminary_print(data)
    try:
        if prelim:
            sections, problems = split_print(print_pages(data), bench=bench)
        else:
            reader = PdfReader(io.BytesIO(data))
            pages = [page.extract_text(extraction_mode="layout") for page in reader.pages]
            sections, problems = split_slip(pages, bench=bench)
    except (PyPdfError, ValueError, TypeError) as exc:
        return _base(entry, status="refused", reason=f"the PDF could not be split: {exc}")
    fmt = PRELIMINARY_PRINT if prelim else SLIP
    if not sections:
        problems.append("no opinion header found")
    if per_curiam:
        writings, more = _per_curiam_writings(sections)
        stamp = f"{HEADER_READER}/{HEADER_READER_VERSION}"
    else:
        assert lineup is not None
        writings, more = list(lineup.writings), _cross_check(lineup.writings, sections)
        stamp = f"{lineup.grammar}/{lineup.grammar_version}"
    problems.extend(more)
    problems.extend(_stray_headers(sections, bench))
    base = {"argued": argued, "source_format": fmt, "lineup": stamp}
    if problems or len(writings) != len(sections):
        return _base(entry, status="refused", reason="; ".join(problems), **base)
    return _base(entry, status="read", opinions=_entries(writings, sections), **base)


def skip_reason(entry: OpinionListing) -> str | None:
    """Why a listing row is not read at all, or ``None`` to read it."""
    if entry.volume_linked:
        return "volume-linked: the listing links into a whole volume, not one opinion"
    return None


class OpinionSource(Protocol):
    """What the pass reads through: :class:`~.opinion_lineups.OpinionFetcher`'s shape."""

    def listing(self, term: int) -> list[OpinionListing]: ...

    def opinion(self, url: str) -> bytes | None: ...


def read_listing_entry(entry: OpinionListing, fetcher: OpinionSource) -> OpinionDocumentReading:
    """Fetch and read one listing row, or say why it was skipped or refused."""
    if (reason := skip_reason(entry)) is not None:
        return _base(entry, status="skipped", reason=reason)
    try:
        data = fetcher.opinion(entry.url)
    except httpx.HTTPError as exc:
        return _base(entry, status="refused", reason=f"fetch failed: {exc}")
    if data is None:
        return _base(entry, status="refused", reason="the opinion is not served")
    return read_document(entry, data)


# --- the writer ---------------------------------------------------------------------


def _row_key(term: int, listing_number: str) -> tuple[int, str]:
    return term, listing_number


def recorded_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The (Term, listing number) of every document the table already records.

    Empty where the table does not exist yet — a corpus written before it was
    added and opened read-only, so nothing created it.
    """
    try:
        rows = conn.execute("SELECT DISTINCT term, listing_number FROM opinions").fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table" not in str(exc):
            raise
        return set()
    return {_row_key(int(row[0]), str(row[1])) for row in rows}


def case_ids_by_docket(conn: corpus.ReadConnection, dockets: Iterable[str]) -> dict[str, str]:
    """The SCOTUS case id of each docket number, keyed by its normalized form.

    The corpus's own reconciliation rule
    (:func:`~fedcourtsai.corpus.scotus_case_ids_by_docket_numbers`): numbers
    compare after ``norm_dn`` normalization, and where two rows carry one
    number the lowest docket id wins.
    """
    return corpus.scotus_case_ids_by_docket_numbers(conn, dockets)


class OpinionRecordResult(BaseModel):
    """What one pass did, or would do on a dry run."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the corpus (False = dry-run)")
    terms: list[int] = Field(default_factory=list)
    listed: int = Field(default=0, ge=0, description="Listing rows in the selected Terms")
    already_recorded: int = Field(
        default=0, ge=0, description="Rows whose document the table already records"
    )
    readings: list[OpinionDocumentReading] = Field(default_factory=list)
    rows: int = Field(default=0, ge=0, description="Opinion rows the read documents yield")
    inserted: int = Field(
        default=0, ge=0, description="Rows the apply actually inserted (0 on a dry run)"
    )
    refused: bool = Field(
        default=False,
        description="Apply was asked for but the rows exceed the bound; nothing written",
    )
    failures: list[str] = Field(default_factory=list, description="Listings that could not be read")


def build_opinion_record(
    conn: corpus.ReadConnection,
    fetcher: OpinionSource,
    *,
    terms: Sequence[int],
    dockets: Sequence[str] = (),
    apply: bool = False,
    max_rows: int | None = None,
    write: Callable[[list[tuple[OpinionDocumentReading, OpinionEntry]]], int] | None = None,
) -> OpinionRecordResult:
    """Read every unrecorded listing row of ``terms`` into the per-opinion record.

    Fill-only and idempotent: a document the table already records is not
    fetched again, and nothing stored is ever changed. ``max_rows`` bounds an
    apply by the opinion rows it would insert; over it nothing is written and
    ``refused`` is set. ``write`` performs the insert (the caller's writable
    connection) and returns the rows it wrote; a dry run never calls it, and an
    apply without it is a caller error.

    A recorded document is never read again, whatever the counting rule or
    reader version it was recorded under: a version bump reaches stored rows
    only through a pass built to replace them, which does not exist yet.
    """
    if apply and write is None:
        raise ValueError("an apply needs a writer")
    result = OpinionRecordResult(applied=apply, terms=list(terms))
    done = recorded_documents(conn)
    wanted = {n for d in dockets if (n := corpus.normalize_docket_number(d)) is not None}
    for term in terms:
        try:
            listing = fetcher.listing(term % 100)
        except httpx.HTTPError as exc:
            result.failures.append(f"OT{term}: the opinions listing could not be read: {exc}")
            continue
        for entry in listing:
            printed = {corpus.normalize_docket_number(d) for d in listed_dockets(entry)}
            if wanted and not wanted & printed:
                continue
            result.listed += 1
            if _row_key(term, entry.number) in done:
                result.already_recorded += 1
                continue
            result.readings.append(read_listing_entry(entry, fetcher))
    ids = case_ids_by_docket(conn, (r.dockets[0] for r in result.readings if r.dockets))
    for reading in result.readings:
        if reading.dockets:
            reading.case_id = ids.get(corpus.normalize_docket_number(reading.dockets[0]) or "")
    pairs = [(r, o) for r in result.readings if r.status == "read" for o in r.opinions]
    result.rows = len(pairs)
    if not apply:
        return result
    if max_rows is not None and result.rows > max_rows:
        result.refused = True
        result.applied = False
        return result
    if write is not None and pairs:
        result.inserted = write(pairs)
    return result


_INSERT_COLUMNS: Final = tuple(corpus.OPINIONS_COLUMN_DDL)


def insert_opinions(
    conn: sqlite3.Connection, pairs: Sequence[tuple[OpinionDocumentReading, OpinionEntry]]
) -> int:
    """Insert opinion rows, never replacing one: the fill-only write. Returns rows written."""
    stamp = datetime.now(UTC).replace(microsecond=0).isoformat()
    rule = f"{WORD_RULE}/{WORD_RULE_VERSION}"
    values = [
        {
            "term": reading.term,
            "listing_number": reading.listing_number,
            "position": opinion.position,
            "docket": reading.docket,
            "dockets": json.dumps(reading.dockets),
            "case_id": reading.case_id,
            "case_name": reading.name,
            "decided": reading.decided.isoformat(),
            "argued": reading.argued.isoformat() if reading.argued else None,
            "kind": opinion.kind.value,
            "author": opinion.author,
            "coauthors": json.dumps(opinion.coauthors),
            "joins": json.dumps([j.model_dump() for j in opinion.joins]),
            "scope": opinion.scope,
            "words": opinion.words,
            "footnote_words": opinion.footnote_words,
            "word_rule": rule,
            "lineup": reading.lineup or "",
            "source_format": reading.source_format or "",
            "document_url": reading.url,
            "header": opinion.header,
            "read_at": stamp,
        }
        for reading, opinion in pairs
    ]
    columns = ", ".join(_INSERT_COLUMNS)
    marks = ", ".join(f":{c}" for c in _INSERT_COLUMNS)
    with conn:
        before = conn.total_changes
        conn.executemany(f"INSERT OR IGNORE INTO opinions ({columns}) VALUES ({marks})", values)
        return conn.total_changes - before
