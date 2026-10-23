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
syllabus names, in the same order, each header names the same author or
authors and a compatible kind, and each separate writing's header names the
same joiners as the syllabus (a lead's header prints none, so the lead's
joiners rest on the syllabus alone). Anything else — a header not found, a
header the syllabus does not name, a kind or a joiner that disagrees —
refuses the whole document, with the reason, rather than recording a guess.

**The word count** (:func:`count_words`, the rule :data:`WORD_RULE` version
:data:`WORD_RULE_VERSION`). Counted over one opinion's text from its header
sentence to the next opinion's header or the end of the document:

- **footnotes are in**: each opinion's footnotes count toward it, and
  ``footnote_words`` reports their share;
- **excluded**: the syllabus or headnote, the caption (court, docket number,
  parties, the writ, the bracketed date), the preliminary print's counsel
  listing, its amicus-brief and "Together with" notes and its closing
  Reporter's Note, running heads and page numbers, and the print's "Page
  Proof Pending Publication" watermark;
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
bound volume (every row before OT2020 on the Court's listings, and some of
OT2020's) is skipped unfetched; a document whose text does not extract is
refused.

**Who sat.** Each read signed decision also gets one ``opinion_benches`` row:
the bench and the Justices who took no part, read off its syllabus lineup
where that lineup is complete and agrees with the listing (:func:`participation`),
and null otherwise. A per curiam gets none. A signed decision recorded before
its bench row is read once more for it; the row is added only where the
re-read writings are the stored ones, and a re-read that reads them
differently gets a null row instead, since its bench describes other writings.

**The text** (the rule :data:`TEXT_RULE` version :data:`TEXT_RULE_VERSION`).
Each read document's writings are also stored as text, for the grade that
reads a merits forecast against what the Court wrote: each writing's body
from its header sentence on and its footnotes, exactly the lines the word
count was taken over, with each line's spacing collapsed and its line breaks
and line-end hyphens kept. A writing's text is held to its own counts — the
word rule counts the body, reference marks stripped, and the footnotes to the
stored ``words`` and ``footnote_words`` — so a document whose text does not
recount is refused, and a plan whose text does not is refused whole. The
writings go to the content store as one content-addressed object per document
(:func:`opinion_text`, :func:`casestore.opinion_text_key`), and the corpus
holds only its pointer, one ``opinion_texts`` row: text is payload, and the
index stays payload-free. A document recorded before its text row is read once
more for it, on the bench row's terms: the text is stored only where the
re-read writings are the stored ones, and a re-read that reads them
differently gets a null row instead.

**Fill-only.** A whole document (:func:`complete_documents`) is never read
again, so a new :data:`WORD_RULE_VERSION`, :data:`TEXT_RULE_VERSION` or reader
version reaches stored rows only through a pass built to replace them, which
does not exist yet; each row says which versions it was read under.

**Nothing a cell sees reads this.** The tables and the stored texts are read
by no ``query`` retrieval row, provisioning step, outcome, mint or scoring
gate.

**Split across a credential boundary.** On run-repair the PDF parse runs in a
job holding no credential: a read-only job writes the documents the record
already holds whole, and those it holds without a bench row or a text row
(:class:`OpinionRecordProjection`); the credential-free job
fetches and reads every other listed document against it and writes the
readings, texts included (:class:`OpinionRecordPlan`); and on an apply the
writer job, holding the corpus lock and the read-write role, re-validates
every reading (:func:`reading_problems`), resolves each case id from the
corpus it has just pulled, stores each text and inserts fill-only
(:func:`apply_opinion_record_plan`), fetching nothing. In one process — a dev
checkout over a pulled corpus — the same functions compose as
:func:`build_opinion_record`.
"""

from __future__ import annotations

import io
import json
import re
import sqlite3
from collections import Counter
from collections.abc import Callable, Container, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Annotated, Any, Final, Literal, Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .. import casestore, corpus
from ..handoff import HandoffRefused
from ..schemas import VoteValue
from .documents import extract_pdf_text
from .justices import KNOWN_SURNAMES, bench_on, chief_on_bench, resolve_surname
from .lineup import LEAD_KINDS, Join, Lineup, Writing, WritingKind
from .opinion_lineups import (
    TEXT_CHAR_CAP,
    OpinionListing,
    read_lineup,
)
from .order_grammars import normalize_order_text
from .syllabus_lineup import writing_kind
from .vote_sources import is_opinion_pdf

#: The word-count rule's name, stamped on every recorded opinion.
WORD_RULE: Final = "scotus-opinion-words"
#: Bump whenever the same document could count differently (stored rows keep theirs).
#: The stamp assumes the locked pypdf: an extractor upgrade that changes the text
#: layer is a reason to bump it.
WORD_RULE_VERSION: Final = 1
#: The text rule's name, stamped on every stored document's writings: each
#: writing's body lines and footnote lines as the splitter cut them, each line's
#: whitespace collapsed, so the word rule counts them to the stored `words`.
TEXT_RULE: Final = "scotus-opinion-text"
#: Bump whenever the same document could yield other text (stored objects keep theirs).
TEXT_RULE_VERSION: Final = 1
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

    @property
    def text(self) -> str:
        """The body under :data:`TEXT_RULE`: the lines the word rule counts, spacing collapsed."""
        return _text_lines(self.body)

    @property
    def footnotes(self) -> str:
        """The footnote lines under :data:`TEXT_RULE`, each note's mark removed."""
        return _text_lines(self.notes)


def _text_lines(lines: Iterable[str]) -> str:
    return "\n".join(collapsed for line in lines if (collapsed := " ".join(line.split())))


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

    def assign(self, lines: Iterable[str], current: Section | None, starts: list[Section]) -> None:
        pending = list(starts)
        target = current if current is not None else (pending.pop(0) if pending else None)
        page = [line for line in lines if line.strip()]
        ones = sum(1 for line in page if (m := _NUMBER_MARK_RE.match(line)) and m.group(1) == "1")
        for raw in page:
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
    return sections, problems


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
            runs.append((text, round(float(size) * scale, 1)))

        page.extract_text(visitor_text=visit)
        pages.append(lines_from_runs(runs))
    return pages


def lines_from_runs(runs: Iterable[tuple[str, float]]) -> list[PrintLine]:
    """One page's text runs, as pypdf's plain mode emits them, joined into sized lines.

    The watermark is removed from every run first; a line's size is that of
    the run contributing most of its characters.
    """
    lines: list[PrintLine] = []
    text = ""
    weights: Counter[float] = Counter()
    for raw, size in runs:
        parts = raw.replace(_WATERMARK, "").split("\n")
        for i, part in enumerate(parts):
            text += part
            weights[size] += len(part.strip())
            if i < len(parts) - 1:
                if text.strip():
                    lines.append(PrintLine(text, weights.most_common(1)[0][0]))
                text, weights = "", Counter()
    if text.strip():
        lines.append(PrintLine(text, weights.most_common(1)[0][0]))
    return lines


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
    return sections, []


# --- reading a document ------------------------------------------------------------


#: The longest text a writing's body or footnotes may carry, in characters: the
#: longest opinions run to some 40,000 words, well under a fifth of this.
WRITING_TEXT_CAP: Final = 1_000_000


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
    text: str | None = Field(
        default=None,
        max_length=WRITING_TEXT_CAP,
        description="The writing's body under the text rule, header sentence first; the word "
        "rule counts it, reference marks stripped, to `words` less `footnote_words`",
    )
    footnotes: str | None = Field(
        default=None,
        max_length=WRITING_TEXT_CAP,
        description="The writing's footnotes under the text rule; the word rule counts them "
        "to `footnote_words`",
    )


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
    bench: list[str] | None = Field(
        default=None,
        description="The Justices the reader seated, where the syllabus lineup accounts for "
        "every one of them; None where participation was not observed",
    )
    took_no_part: list[str] | None = Field(
        default=None,
        description="The bench members the syllabus says took no part; recorded with `bench` "
        "and None with it",
    )


_DOCKET_TOKEN_RE = re.compile(r"\b\d{2}-\d+\b|\b\d{2}A\d+\b|\b\d+,\s*Orig\.", re.I)


def printed_dockets(cell: str) -> list[str]:
    """Every docket number a listing's docket cell prints, in order."""
    return [
        " ".join(m.group(0).split()).upper().replace("ORIG.", "Orig.")
        for m in _DOCKET_TOKEN_RE.finditer(cell)
    ]


def listed_dockets(entry: OpinionListing) -> list[str]:
    """Every docket number the listing row's docket cell prints, in order."""
    return printed_dockets(entry.docket)


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
        elif not header.lead and _joiners(header.joins) != _joiners(writing.joins):
            problems.append(
                f"opinion {position}: the syllabus joins {sorted(_joiners(writing.joins))}, "
                f"the header {sorted(_joiners(header.joins))}"
            )
    return problems


def _joiners(joins: Iterable[Join]) -> set[str]:
    return {join.justice for join in joins}


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
            text=section.text,
            footnotes=section.footnotes,
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
    seated: dict[str, list[str]] = {}
    if not per_curiam:
        reading, lineup = read_lineup(entry, plain.text, truncated=plain.truncated)
        argued, decided = reading.argued, reading.decided or entry.decided
        if lineup is None:
            return _base(entry, status="refused", reason=f"syllabus lineup: {reading.reason}")
        if reading.votes is not None:
            seated = participation(lineup)
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
    opinions = _entries(writings, sections) if len(writings) == len(sections) else []
    problems.extend(
        f"opinion {o.position} {why}" for o in opinions if (why := _text_problem(o)) is not None
    )
    base = {"argued": argued, "source_format": fmt, "lineup": stamp}
    if problems or not opinions:
        return _base(entry, status="refused", reason="; ".join(problems), **base)
    return _base(entry, status="read", opinions=opinions, **base, **seated)


def participation(lineup: Lineup) -> dict[str, list[str]]:
    """A complete lineup's bench and the members of it who took no part.

    Read only off a lineup the merits vote source would stamp from — complete,
    and agreeing with the listing — because that is when every Justice on the
    bench is accounted for, so a name missing from ``took_no_part`` is observed
    to have sat.
    """
    return {
        "bench": list(lineup.bench),
        "took_no_part": [
            justice
            for justice in lineup.bench
            if lineup.votes.get(justice) is VoteValue.did_not_participate
        ],
    }


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


def _keys(conn: corpus.ReadConnection, sql: str) -> set[tuple[int, str]]:
    """The (Term, listing number) pairs ``sql`` selects; empty where its table is missing."""
    try:
        rows = conn.execute(sql).fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table" not in str(exc):
            raise
        return set()
    return {_row_key(int(row[0]), str(row[1])) for row in rows}


def recorded_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The (Term, listing number) of every document the table already records.

    Empty where the table does not exist yet — a corpus written before it was
    added and opened read-only, so nothing created it.
    """
    return _keys(conn, "SELECT DISTINCT term, listing_number FROM opinions")


def _seated_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The recorded documents owing no bench row: a per curiam, or one that has its row."""
    benched = _keys(conn, "SELECT term, listing_number FROM opinion_benches")
    per_curiam = _keys(
        conn,
        "SELECT term, listing_number FROM opinions WHERE position = 1 AND kind = 'per-curiam'",
    )
    return benched | per_curiam


def texted_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The documents with a text row, stored or not; empty where the table is missing."""
    return _keys(conn, "SELECT term, listing_number FROM opinion_texts")


def complete_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The recorded documents the pass has nothing left to read for.

    A recorded document with a text row, and — a per curiam aside, whose
    headers say nothing of who sat — a bench row, either observed or not. A
    document recorded without one of them is read once more, so the row it
    lacks can be added beside the rows it already has; nothing else about it
    changes.
    """
    return recorded_documents(conn) & _seated_documents(conn) & texted_documents(conn)


def rebench_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The recorded signed decisions with no bench row: read once more, for it."""
    return recorded_documents(conn) - _seated_documents(conn)


def retext_documents(conn: corpus.ReadConnection) -> set[tuple[int, str]]:
    """The recorded documents with no text row: read once more, for it."""
    return recorded_documents(conn) - texted_documents(conn)


_Writing = tuple[str, str | None, str, str, str | None]


def _entry_writings(opinions: Iterable[OpinionEntry]) -> tuple[_Writing, ...]:
    return tuple(
        (
            o.kind.value,
            o.author,
            json.dumps(o.coauthors),
            json.dumps([j.model_dump() for j in o.joins]),
            o.scope,
        )
        for o in sorted(opinions, key=lambda o: o.position)
    )


def stored_writings(conn: corpus.ReadConnection) -> dict[tuple[int, str], tuple[_Writing, ...]]:
    """Each recorded document's writings as stored, in position order, for the bench check."""
    try:
        rows = conn.execute(
            "SELECT term, listing_number, kind, author, coauthors, joins, scope "
            "FROM opinions ORDER BY term, listing_number, position"
        ).fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table" not in str(exc):
            raise
        return {}
    found: dict[tuple[int, str], list[_Writing]] = {}
    for row in rows:
        found.setdefault(_row_key(int(row[0]), str(row[1])), []).append(
            (str(row[2]), row[3], str(row[4]), str(row[5]), row[6])
        )
    return {key: tuple(writings) for key, writings in found.items()}


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
    benches: int = Field(
        default=0,
        ge=0,
        description="Bench rows the readings yield: one per read signed decision, a recorded "
        "one that had none included; `bench` is null on those whose lineup is not complete",
    )
    benches_inserted: int = Field(
        default=0, ge=0, description="Bench rows the apply actually inserted (0 on a dry run)"
    )
    texts: int = Field(
        default=0,
        ge=0,
        description="Text rows the readings yield: one per read document, a recorded one that "
        "had none included; `object_key` is null on those whose re-read writings are not the "
        "stored ones",
    )
    texts_inserted: int = Field(
        default=0,
        ge=0,
        description="Text rows the apply actually inserted (0 on a dry run); short of `texts` "
        "where no content store was addressed for the write, which stores no text",
    )
    reread_conflicts: list[str] = Field(
        default_factory=list,
        description="Recorded documents whose re-read writings differ from the stored rows, "
        "so no bench and no text is added to them",
    )
    refused: bool = Field(
        default=False,
        description="Apply was asked for but the rows exceed the bound; nothing written",
    )
    failures: list[str] = Field(default_factory=list, description="Listings that could not be read")
    deferred: int = Field(
        default=0,
        ge=0,
        description="Listing rows left unread for a later window by a sweep's per-window slice",
    )


def read_opinion_record(
    fetcher: OpinionSource,
    *,
    terms: Sequence[int],
    recorded: set[tuple[int, str]],
    rebench: Container[tuple[int, str]] = frozenset(),
    retext: Container[tuple[int, str]] = frozenset(),
    dockets: Sequence[str] = (),
    max_documents: int | None = None,
    rotation: int = 0,
) -> OpinionRecordResult:
    """Fetch and read every listing row of ``terms`` not in ``recorded``, as a dry run.

    The fetch-and-parse half, which touches no corpus: ``recorded`` is the
    (Term, listing number) of each document there is nothing left to read for
    (:func:`complete_documents`), ``rebench`` each one recorded without its
    bench row (:func:`rebench_documents`) and ``retext`` each one recorded
    without its text row (:func:`retext_documents`), from the corpus or its
    projection. Those documents' opinion rows are stored already, so a reading
    of one counts toward the row it lacks alone. Case ids are left unresolved;
    the caller holding the corpus resolves them.

    ``max_documents`` is a sweep's per-window slice of the rows that need a
    fetch: at most that many are read and the rest are counted in ``deferred``
    for a later window. A row skipped unfetched (volume-linked) costs nothing
    and is always reported. Two thirds of the slice go newest decision first,
    so a decision is read the window after it issues; the last third goes to
    the older rows rotated by ``rotation`` (a window index), so a run of rows
    the reader refuses, each unrecorded and offered again every window, cannot
    hold the rest back for good.
    """
    result = OpinionRecordResult(applied=False, terms=list(terms))
    wanted = {n for d in dockets if (n := corpus.normalize_docket_number(d)) is not None}
    owed: list[OpinionListing] = []
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
            if _row_key(term, entry.number) in recorded:
                result.already_recorded += 1
                continue
            owed.append(entry)
    if max_documents is not None:
        owed = _sweep_slice(owed, max_documents, rotation)
        result.deferred = result.listed - result.already_recorded - len(owed)
    result.readings = [read_listing_entry(entry, fetcher) for entry in owed]
    read = [(r, _row_key(r.term, r.listing_number)) for r in result.readings if r.status == "read"]
    # A recorded document is in one of the two re-read sets, so a key in
    # neither is a new document, which owes every row.
    result.rows = sum(
        len(r.opinions) for r, key in read if key not in rebench and key not in retext
    )
    result.benches = sum(
        1 for r, key in read if _seats(r) and (key in rebench or key not in retext)
    )
    result.texts = sum(1 for _, key in read if key in retext or key not in rebench)
    return result


def _sweep_slice(owed: Sequence[OpinionListing], cap: int, rotation: int) -> list[OpinionListing]:
    """A sweep window's rows: every unfetched skip, then ``cap`` fetches (see the caller)."""
    skipped = [entry for entry in owed if skip_reason(entry) is not None]
    fetched = sorted(
        (entry for entry in owed if skip_reason(entry) is None),
        key=lambda entry: (entry.decided, entry.term, entry.number),
        reverse=True,
    )
    newest = cap - cap // 3
    head, tail = fetched[:newest], fetched[newest:]
    if tail:
        start = rotation % len(tail)
        tail = (tail[start:] + tail[:start])[: cap - len(head)]
    return [*skipped, *head, *tail]


def _seats(reading: OpinionDocumentReading) -> bool:
    """Whether a reading yields a bench row: any read signed decision."""
    return reading.status == "read" and reading.opinions[0].kind is not WritingKind.per_curiam


Pairs = list[tuple[OpinionDocumentReading, OpinionEntry]]
#: A document's text row: its reading, and whether its writings' text is stored
#: (False where the re-read writings are not the stored ones: a null row).
TextRows = list[tuple[OpinionDocumentReading, bool]]
#: Inserts opinion, bench and text rows in one transaction; returns how many of each it wrote.
RecordWriter = Callable[[Pairs, list[OpinionDocumentReading], TextRows], tuple[int, int, int]]


def _land(
    conn: corpus.ReadConnection,
    result: OpinionRecordResult,
    *,
    apply: bool,
    max_rows: int | None,
    write: RecordWriter | None,
) -> OpinionRecordResult:
    """Resolve each reading's case id from ``conn``, then insert within the bound.

    A reading of a document ``conn`` already records adds only the bench row
    and the text row it lacks, and fills them only where its writings are the
    stored ones: a bench says who sat for the writings it was read with, and a
    text is those writings' words, so beside rows read differently either
    would describe a decision the table does not hold. Such a document gets
    null rows instead — read, but nothing observed for what is stored — which
    also ends its re-reading, and is reported in ``reread_conflicts``.
    """
    ids = case_ids_by_docket(conn, (r.dockets[0] for r in result.readings if r.dockets))
    for reading in result.readings:
        if reading.dockets:
            reading.case_id = ids.get(corpus.normalize_docket_number(reading.dockets[0]) or "")
    stored = stored_writings(conn)
    seated = _seated_documents(conn)
    texted = texted_documents(conn)
    pairs: Pairs = []
    benches: list[OpinionDocumentReading] = []
    texts: TextRows = []
    result.reread_conflicts = []
    for reading in (r for r in result.readings if r.status == "read"):
        key = _row_key(reading.term, reading.listing_number)
        if key not in stored:
            pairs.extend((reading, o) for o in reading.opinions)
        same = key not in stored or stored[key] == _entry_writings(reading.opinions)
        owes_bench = _seats(reading) and (key not in stored or key not in seated)
        owes_text = key not in stored or key not in texted
        if not same and (owes_bench or owes_text):
            result.reread_conflicts.append(
                f"backfill-opinion-record: OT{key[0]} listing row {key[1]}: the re-read "
                "writings differ from the stored rows, so it records no bench and no text"
            )
        if owes_bench:
            unobserved = {"bench": None, "took_no_part": None}
            benches.append(reading if same else reading.model_copy(update=unobserved))
        if owes_text:
            texts.append((reading, same))
    result.rows = len(pairs)
    result.benches = len(benches)
    result.texts = len(texts)
    result.applied = apply
    if not apply:
        return result
    if max_rows is not None and result.rows + result.benches + result.texts > max_rows:
        result.refused = True
        result.applied = False
        return result
    if write is not None and (pairs or benches or texts):
        result.inserted, result.benches_inserted, result.texts_inserted = write(
            pairs, benches, texts
        )
    return result


def build_opinion_record(
    conn: corpus.ReadConnection,
    fetcher: OpinionSource,
    *,
    terms: Sequence[int],
    dockets: Sequence[str] = (),
    apply: bool = False,
    max_rows: int | None = None,
    write: RecordWriter | None = None,
) -> OpinionRecordResult:
    """Read every listing row of ``terms`` the per-opinion record does not hold whole.

    Fill-only and idempotent: a complete document (:func:`complete_documents`)
    is not fetched again, and nothing stored is ever changed — a recorded
    document with no bench row or no text row is read again only to add it.
    ``max_rows`` bounds an apply by the opinion, bench and text rows it would
    insert; over it nothing is written and ``refused`` is set. ``write``
    performs the insert (the caller's writable connection) and returns the
    rows of each kind it wrote; a dry run never calls it, and an apply without
    it is a caller error.

    A whole document is never read again, whatever the counting rule or reader
    version it was recorded under: a version bump reaches stored rows only
    through a pass built to replace them, which does not exist yet.
    """
    if apply and write is None:
        raise ValueError("an apply needs a writer")
    result = read_opinion_record(
        fetcher,
        terms=terms,
        recorded=complete_documents(conn),
        rebench=rebench_documents(conn),
        retext=retext_documents(conn),
        dockets=dockets,
    )
    return _land(conn, result, apply=apply, max_rows=max_rows, write=write)


# --- the handoff --------------------------------------------------------------------

#: The largest plan or projection either side accepts, in documents: a Term
#: lists well under a hundred, and the pass reads six.
_MAX_DOCUMENTS: Final = 5_000
_LISTING_NUMBER_RE: Final = re.compile(r"^[0-9A-Za-z][0-9A-Za-z.\-]{0,15}$")
_STAMP_RE: Final = re.compile(r"^[a-z0-9-]{1,64}/[0-9]{1,4}$")
_TEXT_CAP: Final = 2_000


class RecordedDocument(BaseModel):
    """One document the pass has nothing left to read for, by the Court's own listing key."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    term: int = Field(ge=2000, le=2100)
    listing_number: str = Field(pattern=_LISTING_NUMBER_RE.pattern)


class OpinionRecordProjection(BaseModel):
    """The one corpus fact the parse needs: which listed documents are complete.

    Complete is :func:`complete_documents`: recorded with its text row, and
    either a per curiam or carrying its bench row. ``rebench`` lists the
    signed decisions recorded without a bench row (:func:`rebench_documents`)
    and ``retext`` the documents recorded without a text row
    (:func:`retext_documents`); each is read again for the row it lacks, so
    the parse counts its stored rows out of what it would insert.

    Public: a (Term, listing number) pair is the row key of the Court's own
    opinions listing, which anyone can read at supremecourt.gov. It says the
    project has recorded that document, and nothing the document or the
    corpus holds about it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/opinion-record-projection"] = "fedcourts/opinion-record-projection"
    version: Literal[3] = 3
    terms: list[int] = Field(max_length=100)
    recorded: list[RecordedDocument] = Field(max_length=_MAX_DOCUMENTS)
    rebench: list[RecordedDocument] = Field(default_factory=list, max_length=_MAX_DOCUMENTS)
    retext: list[RecordedDocument] = Field(default_factory=list, max_length=_MAX_DOCUMENTS)


class OpinionRecordPlan(BaseModel):
    """What the parse read: the file the writer job applies.

    Public: every field of an :class:`OpinionDocumentReading` is read off the
    Court's listing or the opinion PDF itself — kind, author, joiners, word
    counts, the printed header sentence, each writing's text, and the bench
    and non-participation the syllabus states — with ``case_id`` left empty,
    to be resolved by the writer from its own corpus. The refused rows'
    reasons quote at most a header's opening words. The texts are most of its
    bytes: a Term's run to about 4.5 MB, so the six Terms the repair pass reads
    stay well under the handoff cap.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/opinion-record-plan"] = "fedcourts/opinion-record-plan"
    version: Literal[3] = 3
    terms: list[int] = Field(max_length=100)
    listed: int = Field(ge=0)
    already_recorded: int = Field(ge=0)
    failures: list[
        Annotated[str, StringConstraints(max_length=500, pattern=r"^[^\x00-\x1f]*$")]
    ] = Field(max_length=100)
    readings: list[OpinionDocumentReading] = Field(max_length=_MAX_DOCUMENTS)


def opinion_record_projection(
    conn: corpus.ReadConnection, *, terms: Sequence[int]
) -> OpinionRecordProjection:
    """The recorded-documents projection for ``terms``."""
    wanted = set(terms)

    def listed(keys: set[tuple[int, str]]) -> list[RecordedDocument]:
        return [
            RecordedDocument(term=term, listing_number=number)
            for term, number in sorted(keys)
            if term in wanted
        ]

    return OpinionRecordProjection(
        terms=list(terms),
        recorded=listed(complete_documents(conn)),
        rebench=listed(rebench_documents(conn)),
        retext=listed(retext_documents(conn)),
    )


def projected_recorded(
    projection: OpinionRecordProjection, *, terms: Sequence[int]
) -> set[tuple[int, str]]:
    """The projection's recorded keys, refused when it was read for other Terms."""
    if list(projection.terms) != list(terms):
        raise HandoffRefused(
            f"the projection was read for Terms {projection.terms}, not {list(terms)}"
        )
    return {_row_key(doc.term, doc.listing_number) for doc in projection.recorded}


def projected_rebench(projection: OpinionRecordProjection) -> set[tuple[int, str]]:
    """The projection's recorded-without-a-bench-row keys."""
    return {_row_key(doc.term, doc.listing_number) for doc in projection.rebench}


def projected_retext(projection: OpinionRecordProjection) -> set[tuple[int, str]]:
    """The projection's recorded-without-a-text-row keys."""
    return {_row_key(doc.term, doc.listing_number) for doc in projection.retext}


def opinion_record_plan(result: OpinionRecordResult) -> OpinionRecordPlan:
    """A dry run's readings as the plan a writer job applies (case ids cleared)."""
    return OpinionRecordPlan(
        terms=result.terms,
        listed=result.listed,
        already_recorded=result.already_recorded,
        failures=[" ".join(failure.split())[:500] for failure in result.failures[:100]],
        readings=[r.model_copy(update={"case_id": None}) for r in result.readings],
    )


def _names_problem(names: Iterable[str | None]) -> str | None:
    unknown = sorted({n for n in names if n is not None and n not in KNOWN_SURNAMES})
    return f"names no Justice on the roster: {unknown}" if unknown else None


def _opinions_problem(reading: OpinionDocumentReading) -> str | None:  # noqa: PLR0911 - one return per check
    """Why a read document's opinion rows are not ones the reader can produce."""
    opinions = reading.opinions
    if not opinions:
        return "is read but records no opinion"
    if [o.position for o in opinions] != list(range(1, len(opinions) + 1)):
        return "numbers its opinions out of order"
    if reading.source_format not in (SLIP, PRELIMINARY_PRINT):
        return f"names no known source format: {str(reading.source_format)[:40]!r}"
    if reading.lineup is None or not _STAMP_RE.match(reading.lineup):
        return "carries no reader stamp"
    for o in opinions:
        if o.footnote_words > o.words:
            return f"counts more footnote words than words in opinion {o.position}"
        if (o.kind is WritingKind.per_curiam) != (o.author is None):
            return f"pairs kind {o.kind} with author {o.author!r} in opinion {o.position}"
        names = [o.author, *o.coauthors, *(j.justice for j in o.joins)]
        if (why := _names_problem(names)) is not None:
            return f"opinion {o.position} {why}"
        texts = [o.header, o.scope or "", *(j.qualifier or "" for j in o.joins)]
        if any(len(text) > _TEXT_CAP for text in texts):
            return f"carries an over-long text field in opinion {o.position}"
        if (why := _text_problem(o)) is not None:
            return f"opinion {o.position} {why}"
    return _bench_problem(reading)


def _text_problem(opinion: OpinionEntry) -> str | None:
    """Why a read opinion's text is not the text its own counts were taken over."""
    if opinion.text is None or opinion.footnotes is None:
        return "carries no text"
    if "\x00" in opinion.text or "\x00" in opinion.footnotes:
        return "carries a NUL in its text"
    if count_words(opinion.footnotes) != opinion.footnote_words:
        return "carries footnotes the word rule does not count to its footnote words"
    body = count_words(_strip_reference_marks(opinion.text))
    if body + opinion.footnote_words != opinion.words:
        return "carries a text the word rule does not count to its words"
    return None


def _bench_problem(reading: OpinionDocumentReading) -> str | None:  # noqa: PLR0911 - one return per check
    """Why a read document's bench is not one a complete syllabus lineup yields."""
    bench, absent = reading.bench, reading.took_no_part
    if bench is None or absent is None:
        return None if bench is None and absent is None else "carries half a bench"
    if reading.opinions[0].kind is WritingKind.per_curiam:
        return "carries a bench on a per curiam, whose headers do not observe one"
    if (why := _names_problem(bench)) is not None:
        return f"bench {why}"
    try:
        seated = list(bench_on(reading.decided))
    except ValueError:
        return "carries a bench for a date the seat roster does not cover"
    if sorted(bench) != sorted(seated):
        return "carries a bench other than the one the seat roster gives its decision date"
    if len(set(absent)) != len(absent) or not set(absent) <= set(bench):
        return "names a Justice off its bench, or one twice"
    signing = {
        name
        for o in reading.opinions
        for name in (o.author, *o.coauthors, *(j.justice for j in o.joins))
    }
    if signing & set(absent) or not signing <= set(bench):
        return "has a Justice who took no part, or one off the bench, sign a writing"
    return None


def reading_problems(  # noqa: PLR0911 - one return per check
    reading: OpinionDocumentReading, *, terms: Sequence[int]
) -> str | None:
    """Why a planned reading cannot have come from an honest read of the listing.

    The checks the reader's own output always passes: a Term the pass read, a
    listing key and URL of the Court's own shape, docket numbers that are the
    ones the docket cell prints, no case id (the writer resolves it), bounded
    text, and — for a read document — consecutive opinions naming roster
    Justices with word counts that add up.
    """
    if reading.term not in terms:
        return f"is for OT{reading.term}, which the pass did not read"
    if not _LISTING_NUMBER_RE.fullmatch(reading.listing_number):
        return "carries a malformed listing number"
    if not is_opinion_pdf(reading.url):
        return "links no opinion PDF on the Court's own host"
    if reading.case_id is not None:
        return "carries a case id, which only the writer resolves"
    if any(len(t) > _TEXT_CAP for t in (reading.docket, reading.name, reading.reason or "")):
        return "carries an over-long text field"
    if reading.dockets != printed_dockets(reading.docket):
        return "lists docket numbers its docket cell does not print"
    if reading.status == "read":
        return _opinions_problem(reading)
    if reading.opinions:
        return f"is {reading.status} yet records opinions"
    return None


def apply_opinion_record_plan(
    conn: corpus.ReadConnection,
    plan: OpinionRecordPlan,
    *,
    terms: Sequence[int],
    apply: bool,
    max_rows: int | None = None,
    write: RecordWriter | None = None,
) -> OpinionRecordResult:
    """Re-validate a plan, then resolve and insert it into the corpus ``conn`` holds.

    The plan is untrusted input — written by the job that parsed the fetched
    PDFs — so it must be for exactly ``terms``, name each listing row once, and
    every reading must pass :func:`reading_problems`; any departure refuses the
    whole plan with :class:`HandoffRefused` before anything is written. A
    document the corpus has completed since the plan was read is counted as
    already recorded and not inserted again, and a recorded one gains only the
    bench and text rows it lacks, where its writings are the stored ones. Then
    the one-process apply's own
    steps: each case id is resolved from ``conn``, the bound refuses above
    ``max_rows``, and the insert is fill-only. Fetches nothing.
    """
    if apply and write is None:
        raise ValueError("an apply needs a writer")
    if list(plan.terms) != list(terms):
        raise HandoffRefused(f"the plan was read for Terms {plan.terms}, not {list(terms)}")
    seen: set[tuple[int, str]] = set()
    for reading in plan.readings:
        key = _row_key(reading.term, reading.listing_number)
        if key in seen:
            raise HandoffRefused(f"the plan reads OT{key[0]} listing row {key[1]!r} twice")
        seen.add(key)
        if (why := reading_problems(reading, terms=terms)) is not None:
            raise HandoffRefused(f"the plan's OT{key[0]} listing row {key[1]!r} {why}")
    recorded = complete_documents(conn)
    fresh = [r for r in plan.readings if _row_key(r.term, r.listing_number) not in recorded]
    result = OpinionRecordResult(
        applied=False,
        terms=list(terms),
        listed=plan.listed,
        already_recorded=plan.already_recorded + len(plan.readings) - len(fresh),
        readings=[r.model_copy() for r in fresh],
        failures=list(plan.failures),
    )
    return _land(conn, result, apply=apply, max_rows=max_rows, write=write)


#: A sweep apply's row bound per document of its slice: opinion rows plus the
#: bench and text rows. A decision prints one lead opinion and a handful of separate
#: writings, so an honest slice stays far under it, and a plan padding its
#: readings with invented rows is refused whole rather than inserted.
SWEEP_ROWS_PER_DOCUMENT: Final = 20


def sweep_class(plan: OpinionRecordPlan, *, cap: int) -> int:
    """The class a sweep's plan found: every listing row it left unrecorded, read or deferred.

    An honest sweep parse fetches at most ``cap`` documents, so a plan carrying
    more fetched readings refuses whole with :class:`HandoffRefused`; a row
    skipped unfetched is not one. The caller weighs the returned class against
    its ceiling.
    """
    fetched = sum(1 for reading in plan.readings if reading.status != "skipped")
    if fetched > cap:
        raise HandoffRefused(
            f"the plan reads {fetched} listing rows, above the sweep's slice of {cap}"
        )
    return max(len(plan.readings), plan.listed - plan.already_recorded)


_INSERT_COLUMNS: Final = tuple(corpus.OPINIONS_COLUMN_DDL)
_BENCH_COLUMNS: Final = tuple(corpus.OPINION_BENCHES_COLUMN_DDL)
_TEXT_COLUMNS: Final = tuple(corpus.OPINION_TEXTS_COLUMN_DDL)


class WritingText(BaseModel):
    """One writing's text, as the stored object carries it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position: int = Field(ge=1)
    kind: WritingKind
    author: str | None
    header: str
    words: int = Field(ge=0)
    footnote_words: int = Field(ge=0)
    text: str = Field(max_length=WRITING_TEXT_CAP)
    footnotes: str = Field(max_length=WRITING_TEXT_CAP)


class OpinionText(BaseModel):
    """One opinion document's writings: the content-store object a text row points at.

    Everything in it is read off the Court's listing and the document itself,
    so it says which document it is (its listing key, docket cell and PDF) and
    which text rule cut it, and carries each writing in the order printed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/opinion-text"] = "fedcourts/opinion-text"
    version: Literal[1] = 1
    term: int
    listing_number: str
    docket: str
    dockets: list[str]
    name: str
    decided: date
    document_url: str
    source_format: str
    text_rule: str
    writings: list[WritingText]


def opinion_text(reading: OpinionDocumentReading) -> OpinionText:
    """A read document's writings as the object its text row points at."""
    return OpinionText(
        term=reading.term,
        listing_number=reading.listing_number,
        docket=reading.docket,
        dockets=list(reading.dockets),
        name=reading.name,
        decided=reading.decided,
        document_url=reading.url,
        source_format=reading.source_format or "",
        text_rule=f"{TEXT_RULE}/{TEXT_RULE_VERSION}",
        writings=[
            WritingText(
                position=o.position,
                kind=o.kind,
                author=o.author,
                header=o.header,
                words=o.words,
                footnote_words=o.footnote_words,
                text=o.text or "",
                footnotes=o.footnotes or "",
            )
            for o in reading.opinions
        ],
    )


def opinion_text_bytes(reading: OpinionDocumentReading) -> bytes:
    """The stored object's bytes: sorted keys, so one reading always stores one object."""
    payload = opinion_text(reading).model_dump(mode="json")
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def insert_opinions(
    conn: sqlite3.Connection,
    pairs: Sequence[tuple[OpinionDocumentReading, OpinionEntry]],
    benches: Sequence[OpinionDocumentReading] = (),
    texts: Sequence[tuple[OpinionDocumentReading, bool]] = (),
    *,
    store: casestore.ObjectTransport | None = None,
) -> tuple[int, int, int]:
    """Insert opinion, bench and text rows, never replacing one: the fill-only write.

    Each text to keep is stored first, at its content-addressed key in
    ``store``, and its row points at it; one transaction then inserts every
    row, so a document's rows land together and a pointer never names an
    object that was not written. A store failure raises before any row is
    inserted, leaving at most an object no row names. With no ``store`` a text
    is kept nowhere and its row is not written, so the document stays owed. A
    text not kept (the re-read writings were not the stored ones) gets its
    null row either way. Returns the opinion, bench and text rows written.
    """
    stamp = datetime.now(UTC).replace(microsecond=0).isoformat()
    text_rule = f"{TEXT_RULE}/{TEXT_RULE_VERSION}"
    texted: list[dict[str, Any]] = []
    for reading, keep in texts:
        ref: casestore.ObjectRef | None = None
        if keep:
            if store is None:
                continue
            body = opinion_text_bytes(reading)
            ref = casestore.write_opinion_text(store, reading.term, reading.listing_number, body)
        texted.append(
            {
                "term": reading.term,
                "listing_number": reading.listing_number,
                "object_key": None if ref is None else ref.key,
                "digest": None if ref is None else ref.digest,
                "bytes": None if ref is None else ref.size,
                "text_rule": text_rule,
                "read_at": stamp,
            }
        )
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
    seated = [
        {
            "term": reading.term,
            "listing_number": reading.listing_number,
            "bench": None if reading.bench is None else json.dumps(reading.bench),
            "took_no_part": (
                None if reading.took_no_part is None else json.dumps(reading.took_no_part)
            ),
            "lineup": reading.lineup or "",
            "read_at": stamp,
        }
        for reading in benches
    ]
    columns = ", ".join(_INSERT_COLUMNS)
    marks = ", ".join(f":{c}" for c in _INSERT_COLUMNS)
    bench_columns = ", ".join(_BENCH_COLUMNS)
    bench_marks = ", ".join(f":{c}" for c in _BENCH_COLUMNS)
    text_columns = ", ".join(_TEXT_COLUMNS)
    text_marks = ", ".join(f":{c}" for c in _TEXT_COLUMNS)
    with conn:
        before = conn.total_changes
        conn.executemany(f"INSERT OR IGNORE INTO opinions ({columns}) VALUES ({marks})", values)
        rows = conn.total_changes - before
        conn.executemany(
            f"INSERT OR IGNORE INTO opinion_benches ({bench_columns}) VALUES ({bench_marks})",
            seated,
        )
        bench_rows = conn.total_changes - before - rows
        conn.executemany(
            f"INSERT OR IGNORE INTO opinion_texts ({text_columns}) VALUES ({text_marks})",
            texted,
        )
        return rows, bench_rows, conn.total_changes - before - rows - bench_rows
