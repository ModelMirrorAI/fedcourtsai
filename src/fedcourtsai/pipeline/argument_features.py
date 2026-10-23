"""Who the Justices questioned at oral argument, and how much, read from the transcript.

A pure, deterministic parse of the cleaned text
:func:`fedcourtsai.pipeline.documents.extract_transcript_text` stores for the
``argument-transcript`` kind. It reads two things the Court's reporter prints
on every transcript and nothing else:

- **Segment headers.** Each advocate's time opens with a header — "ORAL
  ARGUMENT OF <name> ON BEHALF OF THE PETITIONERS", "... FOR THE UNITED STATES,
  AS AMICUS CURIAE, SUPPORTING THE RESPONDENT", "REBUTTAL ARGUMENT OF ..." —
  and the header is where the side is read: the advocate's role (a party, the
  United States as amicus, another amicus) and the position supported.
- **Speaker labels.** Each turn opens a line with its speaker's label —
  "JUSTICE KAGAN:", "CHIEF JUSTICE ROBERTS:", "MR. SMITH:", "MS. JONES:",
  "GENERAL PRELOGAR:". A Justice label resolves to the roster surname
  (:func:`fedcourtsai.pipeline.justices.resolve_surname`).

**The assignment.** A Justice's turn counts toward the side of the segment it
falls in: the Justice is taken to be questioning the advocate whose time it
is. A rebuttal is the petitioner's (the header says so; one that names no side
is still read as the petitioner's, the only party that rebuts). Turns before
the first header — the Chief Justice calling the case — fall in no segment.
Nothing is guessed: a segment whose header names no readable side, and a
Justice label the roster does not carry, are counted apart and reported in the
coverage, never spread over the sides.

What the headers do not allow, and so what this does not handle:

- **Consolidated arguments** are split only as far as their headers mark them.
  A header's "IN CASE <number>" is kept on the segment, but every petitioner
  segment is keyed ``petitioner`` whichever case it argued; the per-case split
  is the segments list, not the totals.
- **Divided argument** — two advocates for one side, or one side's time split
  by question ("... ON QUESTION 1") — is summed under the side; the segments
  list keeps each advocate apart.
- **A Justice addressing someone other than the advocate at the lectern** (the
  Chief Justice's "Thank you, counsel" and the next advocate's name, closing a
  segment; a rare question to a different counsel) is counted with the segment
  it falls in, because no label says otherwise.
- **"Supporting vacatur"** and **"supporting neither party"** are kept as
  ``neither``, not read as the petitioner's, though vacatur is often what the
  petitioner asked for.

Three furniture residues of the cleaned text are discounted here rather than
in the stored text, which is a cell's information set: a lone "Official" line
(what the cleaner leaves of the review header on some transcripts), a line
holding only a reporter's parenthetical ("(Laughter.)"), and the margin line
numbers a transcript whose extraction kept them on the text line carries. The
parse stops at the reporter's last closing line, so a word index the cleaner
kept (a closing line it did not match) is not read as speech.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Final, Literal

from ..schemas import (
    ArgumentAlignment,
    ArgumentFeatures,
    ArgumentParseCoverage,
    ArgumentRole,
    ArgumentSegment,
    ArgumentSide,
    ArgumentTurnCount,
    JusticeArgumentFeatures,
)
from .justices import resolve_surname

PARSER_VERSION: Final = "1"

#: The assignment rule, stated on every result.
ASSIGNMENT: Final = (
    "A Justice's turn counts toward the side of the segment it falls in, read from "
    + "the segment's 'ORAL ARGUMENT OF' / 'REBUTTAL ARGUMENT OF' header; a rebuttal "
    + "is the petitioner's; turns before the first header, in a segment whose header "
    + "names no side, or under a label the roster does not resolve are counted "
    + "unattributed."
)

# A speaker label opening a line: an honorific, then an all-caps name (a "Mc"
# prefix, accents, apostrophes and hyphens allowed), then a colon. The honorific
# list is closed, so a sentence that happens to open a line with "I would say:"
# is speech, not a speaker.
_APOSTROPHES = "'\u2019"
_NAME = rf"[A-ZÀ-Þ][A-Za-zÀ-ÿ{_APOSTROPHES}.\-]*(?: [A-ZÀ-Þ][A-Za-zÀ-ÿ{_APOSTROPHES}.\-]*){{0,3}}"
_LABEL_RE: Final = re.compile(
    rf"^(?P<title>CHIEF JUSTICE|JUSTICE|MR\.?|MRS\.?|MS\.?|GENERAL) (?P<name>{_NAME}):\s*"
)
# A line opening like a label (capital words, then a colon) that _LABEL_RE does
# not read, such as a title outside the closed list. Counted, not attributed.
_LABEL_LIKE_RE: Final = re.compile(r"^(?P<prefix>[A-Z][A-Z.'\-]*(?: [A-Z][A-Z.'\-]*){1,4}):")
# A segment header in the body. The table of contents prints the same words
# with a colon ("ORAL ARGUMENT OF:"), which is not a header. The reporter
# sometimes prints "ARGUMENT BY", and an extraction can lose the leading "ORAL";
# both still open a segment.
_HEADER_RE: Final = re.compile(r"^(?:(?P<kind>REBUTTAL|ORAL) )?ARGUMENT (?:OF|BY)(?![:\w])")
# How many lines past its first a header may run before it is read as unended.
_HEADER_MAX_LINES: Final = 6
# The reporter's closing line, "(Whereupon, at 11:19 a.m., the case was
# submitted.)", read with or without the comma; "submitted" must be on it or the
# next line, so a mid-argument "(Whereupon, a recess was taken.)" ends nothing.
_CLOSING_RE: Final = re.compile(r"^\(\s*whereupon\b", re.IGNORECASE)
_SUBMITTED_RE: Final = re.compile(r"\bsubmitted\b", re.IGNORECASE)
# The line that opens the argument proper, after the cover, the appearances and
# the table of contents, which print the advocates' names and sides as well.
_PROCEEDINGS_RE: Final = re.compile(r"^P ?R ?O ?C ?E ?E ?D ?I ?N ?G ?S$")
# What the cleaner leaves of the review header on some transcripts.
_OFFICIAL: Final = "Official"
_PARENTHETICAL_RE: Final = re.compile(r"^\([^()]*\)$")
_LINE_NUMBER_RE: Final = re.compile(r"^\d{1,2} (?=\S)")
_WORD_RE: Final = re.compile(r"\w")

_AMICUS_RE: Final = re.compile(r"\bAMIC(?:US|I) CURIAE\b")
_UNITED_STATES_AMICUS_RE: Final = re.compile(r"\bUNITED STATES,? AS AMIC(?:US|I)\b")
_BEHALF_RE: Final = re.compile(r"\bBEHALF OF\b")
_ROLE_WORD_RE: Final = re.compile(r"\b(PETITIONER|APPELLANT|RESPONDENT|APPELLEE)S?\b")
_SUPPORT_RE: Final = re.compile(r"\b(?:SUPPORTING|IN SUPPORT OF)\b")
_SUPPORT_TARGET_RE: Final = re.compile(
    r"\b(?P<petitioner>PETITIONERS?|APPELLANTS?|REVERSAL)\b"
    + r"|\b(?P<respondent>RESPONDENTS?|APPELLEES?|JUDGMENT BELOW|AFFIRMANCE)\b"
    + r"|\b(?P<neither>VACATUR|NEITHER PARTY)\b"
)
_CASE_NUMBER_RE: Final = re.compile(r"\bIN CASE (?:NO\. )?(\d{2}[-A]\d+)\b")


@dataclass
class _Segment:
    index: int
    kind: Literal["argument", "rebuttal"]
    header: str
    role: ArgumentRole | None
    supports: ArgumentAlignment | None
    case_number: str | None
    justice_turns: int = 0
    justice_words: int = 0
    advocate_turns: int = 0
    advocate_words: int = 0
    other_turns: int = 0

    @property
    def side(self) -> ArgumentSide | None:
        return _side(self.role, self.supports)


@dataclass
class _Tally:
    turns: int = 0
    words: int = 0

    def add(self, words: int) -> None:
        self.turns += 1
        self.words += words

    def count(self) -> ArgumentTurnCount:
        return ArgumentTurnCount(turns=self.turns, words=self.words)


@dataclass
class _JusticeTally:
    by_side: dict[ArgumentSide, _Tally] = field(default_factory=dict)
    by_alignment: dict[ArgumentAlignment, _Tally] = field(default_factory=dict)
    unattributed: _Tally = field(default_factory=_Tally)


_AMICUS_SIDES: dict[tuple[bool, ArgumentAlignment], ArgumentSide] = {
    (True, "petitioner"): "united-states-supporting-petitioner",
    (True, "respondent"): "united-states-supporting-respondent",
    (True, "neither"): "united-states-supporting-neither",
    (False, "petitioner"): "amicus-supporting-petitioner",
    (False, "respondent"): "amicus-supporting-respondent",
    (False, "neither"): "amicus-supporting-neither",
}


def _side(role: ArgumentRole | None, supports: ArgumentAlignment | None) -> ArgumentSide | None:
    if role == "petitioner":
        return "petitioner"
    if role == "respondent":
        return "respondent"
    if role is None or supports is None:
        return None
    return _AMICUS_SIDES[(role == "united-states-amicus", supports)]


def _supports(text: str) -> ArgumentAlignment | None:
    """The position named after the header's first 'SUPPORTING' / 'IN SUPPORT OF'."""
    support = _SUPPORT_RE.search(text)
    if support is None:
        return None
    target = _SUPPORT_TARGET_RE.search(text, support.end())
    if target is None:
        return None
    if target.group("petitioner"):
        return "petitioner"
    if target.group("respondent"):
        return "respondent"
    return "neither"


def read_header(header: str) -> tuple[ArgumentRole | None, ArgumentAlignment | None, str | None]:
    """A segment header's role, supported position and named case number.

    An amicus header ("AMICUS CURIAE") is read first, so a court-appointed
    amicus is never mistaken for a party; the United States is told from any
    other amicus by "UNITED STATES, AS AMICUS". A party header's role is the
    first party word after "BEHALF OF", an appellant read as a petitioner and an
    appellee as a respondent, and it supports its own party unless the header
    says otherwise ("ON BEHALF OF THE RESPONDENT, IN SUPPORT OF THE PETITIONER").
    """
    text = header.upper()
    case = _CASE_NUMBER_RE.search(text)
    case_number = case.group(1) if case else None
    supports = _supports(text)
    if _AMICUS_RE.search(text):
        role: ArgumentRole = (
            "united-states-amicus" if _UNITED_STATES_AMICUS_RE.search(text) else "amicus"
        )
        return role, supports, case_number
    behalf = _BEHALF_RE.search(text)
    if behalf is None:
        return None, None, case_number
    word = _ROLE_WORD_RE.search(text, behalf.end())
    if word is None:
        return None, None, case_number
    if word.group(1) in ("PETITIONER", "APPELLANT"):
        return "petitioner", supports or "petitioner", case_number
    return "respondent", supports or "respondent", case_number


def _is_line_numbered(lines: list[str]) -> bool:
    """Whether the extraction kept the margin line numbers on the text lines."""
    if not lines:
        return False
    numbered = sum(1 for line in lines if _LINE_NUMBER_RE.match(line))
    return numbered * 2 >= len(lines)


def _words(text: str) -> int:
    return sum(1 for token in text.split() if _WORD_RE.search(token))


def _names_advocate(name: str, header: str) -> bool:
    """Whether a label's surname is a word of the segment's header."""
    surname = name.rsplit(maxsplit=1)[-1].upper()
    return re.search(rf"(?<!\w){re.escape(surname)}(?!\w)", header.upper()) is not None


def _argument_lines(text: str) -> tuple[list[str], bool, bool]:
    """The argument's lines, with whether the opening and the closing line were found.

    Margin line numbers kept on the text line are dropped, the text is cut at
    the reporter's last closing line, and everything up to the "P R O C E E D I
    N G S" line is dropped, since the cover, appearances and contents name every
    advocate and side as well.
    """
    lines = [line.strip() for line in text.splitlines()]
    if _is_line_numbered(lines):
        lines = [_LINE_NUMBER_RE.sub("", line, count=1) for line in lines]
    closes = [
        i
        for i, line in enumerate(lines)
        if _CLOSING_RE.match(line) and _SUBMITTED_RE.search(" ".join(lines[i : i + 2]))
    ]
    if closes:
        lines = lines[: closes[-1]]
    opening = next((i for i, line in enumerate(lines) if _PROCEEDINGS_RE.match(line)), None)
    if opening is not None:
        lines = lines[opening + 1 :]
    return lines, opening is not None, bool(closes)


def _is_furniture(line: str) -> bool:
    return line == _OFFICIAL or bool(_PARENTHETICAL_RE.match(line))


class _Parse:
    """One pass over an argument's lines: the segments, and every turn's tally."""

    def __init__(self) -> None:
        self.segments: list[_Segment] = []
        self.notes: list[str] = []
        self.justices: dict[str, _JusticeTally] = {}
        self.unresolved: Counter[str] = Counter()
        self.label_like: Counter[str] = Counter()
        self.justice_turns = 0
        self.outside = 0
        self.unresolved_turns = 0
        self.unattributed_segment = 0
        self.attributed = 0
        # The open turn's speaker (title, name) and its words so far.
        self.speaker: tuple[str, str] | None = None
        self.words = 0

    def run(self, lines: list[str]) -> None:
        index = 0
        while index < len(lines):
            line = lines[index]
            header = _HEADER_RE.match(line)
            if header is not None:
                self.close_turn()
                index = self.open_segment(lines, index, rebuttal=header.group("kind") == "REBUTTAL")
                continue
            label = _LABEL_RE.match(line)
            if label is not None:
                self.close_turn()
                self.speaker = (label.group("title").rstrip("."), label.group("name"))
                self.words = _words(line[label.end() :])
            else:
                if (like := _LABEL_LIKE_RE.match(line)) is not None:
                    self.label_like[like.group("prefix")] += 1
                if self.speaker is not None and not _is_furniture(line):
                    self.words += _words(line)
            index += 1
        self.close_turn()

    def open_segment(self, lines: list[str], index: int, *, rebuttal: bool) -> int:
        """Read the header at ``index`` and open its segment; the index past the header."""
        block = [lines[index]]
        end = index + 1
        while (
            end < len(lines)
            and end - index < _HEADER_MAX_LINES
            and not _LABEL_RE.match(lines[end])
            and not _HEADER_RE.match(lines[end])
        ):
            if not _is_furniture(lines[end]):
                block.append(lines[end])
            end += 1
        joined = " ".join(part for part in block if part)
        role, supports, case_number = read_header(joined)
        position = len(self.segments)
        if rebuttal and role is None:
            role, supports = "petitioner", "petitioner"
            self.notes.append(
                f"segment {position}: rebuttal header names no side; counted with the petitioner"
            )
        segment = _Segment(
            position, "rebuttal" if rebuttal else "argument", joined, role, supports, case_number
        )
        if segment.side is None:
            self.notes.append(f"segment {position}: no side read from header {joined!r}")
        self.segments.append(segment)
        return end

    def close_turn(self) -> None:
        if self.speaker is None:
            return
        title, name = self.speaker
        words, self.speaker, self.words = self.words, None, 0
        segment = self.segments[-1] if self.segments else None
        if title not in ("JUSTICE", "CHIEF JUSTICE"):
            if segment is None:
                return
            if _names_advocate(name, segment.header):
                segment.advocate_turns += 1
                segment.advocate_words += words
            else:
                segment.other_turns += 1
            return
        self.justice_turns += 1
        if segment is None:
            self.outside += 1
            return
        segment.justice_turns += 1
        segment.justice_words += words
        surname = resolve_surname(name)
        if surname is None:
            self.unresolved[f"{title} {name}"] += 1
            self.unresolved_turns += 1
            return
        tally = self.justices.setdefault(surname, _JusticeTally())
        side = segment.side
        if side is None or segment.supports is None:
            tally.unattributed.add(words)
            self.unattributed_segment += 1
            return
        tally.by_side.setdefault(side, _Tally()).add(words)
        tally.by_alignment.setdefault(segment.supports, _Tally()).add(words)
        self.attributed += 1


def _sum_into[K: str](totals: dict[K, _Tally], parts: dict[K, _Tally]) -> None:
    for key, part in parts.items():
        total = totals.setdefault(key, _Tally())
        total.turns += part.turns
        total.words += part.words


def _counts[K: str](tallies: dict[K, _Tally]) -> dict[K, ArgumentTurnCount]:
    return {key: tallies[key].count() for key in sorted(tallies)}


def parse_argument_features(text: str) -> ArgumentFeatures:
    """Per-Justice turns and words by advocate side, read from one cleaned transcript."""
    lines, opened, closing_line = _argument_lines(text)
    parse = _Parse()
    parse.run(lines)
    notes = parse.notes
    if not opened:
        notes.append("no 'P R O C E E D I N G S' line: parsed from the start of the text")
    if not closing_line:
        notes.append("no reporter's closing line: parsed to the end of the text")
    if not parse.segments:
        notes.append("no segment header read: every turn is outside a segment")

    side_totals: dict[ArgumentSide, _Tally] = {}
    alignment_totals: dict[ArgumentAlignment, _Tally] = {}
    rows: list[JusticeArgumentFeatures] = []
    for surname in sorted(parse.justices):
        tally = parse.justices[surname]
        _sum_into(side_totals, tally.by_side)
        _sum_into(alignment_totals, tally.by_alignment)
        rows.append(
            JusticeArgumentFeatures(
                justice=surname,
                total=ArgumentTurnCount(
                    turns=sum(p.turns for p in tally.by_side.values()),
                    words=sum(p.words for p in tally.by_side.values()),
                ),
                by_side=_counts(tally.by_side),
                by_alignment=_counts(tally.by_alignment),
                unattributed=tally.unattributed.count(),
            )
        )

    segments = parse.segments
    attributed_segments = sum(1 for s in segments if s.side is not None)
    return ArgumentFeatures(
        parser_version=PARSER_VERSION,
        assignment=ASSIGNMENT,
        segments=[
            ArgumentSegment(
                index=s.index,
                kind=s.kind,
                header=s.header,
                role=s.role,
                supports=s.supports if s.role is not None else None,
                side=s.side,
                case_number=s.case_number,
                justice=ArgumentTurnCount(turns=s.justice_turns, words=s.justice_words),
                advocate=ArgumentTurnCount(turns=s.advocate_turns, words=s.advocate_words),
                other_turns=s.other_turns,
            )
            for s in segments
        ],
        justices=rows,
        side_totals=_counts(side_totals),
        alignment_totals=_counts(alignment_totals),
        coverage=ArgumentParseCoverage(
            segments=len(segments),
            segments_attributed=attributed_segments,
            segments_unattributed=len(segments) - attributed_segments,
            justice_turns=parse.justice_turns,
            justice_turns_attributed=parse.attributed,
            justice_turns_outside_segments=parse.outside,
            justice_turns_unresolved=parse.unresolved_turns,
            justice_turns_unattributed_segment=parse.unattributed_segment,
            unresolved_labels=sorted(parse.unresolved),
            unrecognized_label_lines=sum(parse.label_like.values()),
            unrecognized_labels=sorted(parse.label_like),
            closing_line=closing_line,
            notes=notes,
        ),
    )
