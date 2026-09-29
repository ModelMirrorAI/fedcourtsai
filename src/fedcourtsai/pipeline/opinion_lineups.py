"""The Court's opinions as a vote source: fetch, locate the lineup, read it.

The ``supremecourt-opinions`` vote source (``docs/data-sources.md``). For one
October Term the Court publishes an opinions listing at
``supremecourt.gov/opinions/slipopinion/<YY>``: one row per opinion, with its
decision date, docket number, the author's initials and a link to the opinion
PDF — the slip opinion until the preliminary print replaces it, then the
print. This module reads that listing, fetches each opinion, finds the
syllabus's closing lineup paragraph, and reads it with the syllabus grammar
(:mod:`fedcourtsai.pipeline.syllabus_lineup`) against the bench the roster
says sat (:func:`fedcourtsai.pipeline.justices.bench_on`).

**Read-only.** Nothing here writes the corpus, the content store or the
ledger: :func:`read_term` returns readings, and the ``opinion-lineups`` command
prints them. A reading carries the ``Outcome.votes`` list and the
``VoteProvenance`` block a writer would commit, so what the channel would
publish can be inspected before anything publishes it.

**Scope.** A listing row is read only when it is a merits decision this
channel can read today; every other row is reported as skipped, with the
reason:

- *not a Term-form docket*: an application (``24A884``), whose opinion is an
  interim ruling, or an original action (``141, Orig.``);
- *per curiam*: an unsigned opinion's syllabus prints no lineup, and whether a
  Justice dissented without writing is in the opinion's body, which this
  grammar does not read;
- *volume-linked*: an earlier Term whose listing links into a whole
  preliminary-print or bound volume rather than a per-opinion PDF.

**The fetch.** Through :class:`~fedcourtsai.supremecourt.SupremeCourtClient`:
the browser user agent the Court's site requires, ~1 request/second, one
retry after a pause, and no request that leaves ``supremecourt.gov`` —
neither the listing's links nor any redirect (``OffHostFetch``). No token and
no budget: the site is public.

**Finding the paragraph.** The lineup is the syllabus's last paragraph: it
opens with the lead sentence (``ALITO, J., delivered the opinion …``,
``… announced the judgment …``) and runs until the opinion begins — the slip
opinion's rule and ``NOTICE``, or the preliminary print's counsel listing or
opinion heading. Running heads a page break drops inside it (``Cite as: …``,
``Syllabus``, ``8 BOUARFA v. MAYORKAS``) are removed, and so are the text
layer's stray spaces — after a name's initial where closing it up yields a
roster surname (the slip opinion's small capitals print ``S OTOMAYOR``), and
before a comma or period (``J .``). A
paragraph that runs off the end of the extracted text is refused, because a
truncated paragraph reads as a unanimous one.

**The bench.** The Justices in service on the printed decision date; any of
them who took the oath after the printed argument date (the latest, where the
case was reargued) is passed to the grammar as seated after argument, so only
the paragraph can place them — the convention never credits them. A decision
with no printed argument date treats everyone sworn in since the July before
its Term that way, since any of them could have missed the argument.

**Cross-checks.** The listing's author initials must name the lead opinion's
author, and the printed decision date must equal the listing's; either
disagreement is a problem on the reading. A reading yields a vote record only
when its lineup is complete and it has no problem of its own.
"""

from __future__ import annotations

import hashlib
import html
import os
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Final, Literal
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ConfigDict

from ..schemas import JusticeVote, VoteProvenance
from ..supremecourt import SupremeCourtClient, october_term_year, parse_scotus_docket_number
from .documents import extract_pdf_text
from .justices import bench_on, resolve_surname, seated_after
from .lineup import LEAD_KINDS, Lineup, justice_votes
from .syllabus_lineup import SCOTUS_SYLLABUS
from .vote_sources import SUPREMECOURT_OPINIONS

#: The Court's per-Term opinions listing.
LISTING_URL: Final = "https://www.supremecourt.gov/opinions/slipopinion/{term:02d}"
_ORIGIN: Final = "https://www.supremecourt.gov/"

#: How much of an opinion's text is extracted. The syllabus opens the document
#: and the lineup closes it, well inside this; a paragraph still running at the
#: cap is refused rather than read short.
TEXT_CHAR_CAP: Final = 120_000

#: The listing's author initials (its ``J.`` column), by roster surname, for
#: every Justice in :data:`fedcourtsai.pipeline.justices.SERVICE`.
LISTING_AUTHOR_CODES: Final = {
    "R": "Roberts",
    "K": "Kennedy",
    "T": "Thomas",
    "G": "Ginsburg",
    "B": "Breyer",
    "A": "Alito",
    "SS": "Sotomayor",
    "EK": "Kagan",
    "NG": "Gorsuch",
    "BK": "Kavanaugh",
    "AB": "Barrett",
    "KJ": "Jackson",
}
_PER_CURIAM_CODE: Final = "PC"

_ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S | re.I)
_CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S | re.I)
_HREF_RE = re.compile(r"<a\s[^>]*href=['\"]([^'\"]+)['\"]", re.I)
_TAG_RE = re.compile(r"<[^>]+>")
_TERM_DOCKET_RE = re.compile(r"^\s*(\d{2}-\d+)\b")

_DATE = r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})"
_ARGUED_RE = re.compile(rf"\b(?:Re)?argued\s+{_DATE}", re.I)
_DECIDED_RE = re.compile(rf"\bDecided\s+{_DATE}")
_HEADER_HYPHEN_RE = re.compile(r"(\w)-[ \t]*\n\s*(\w)")

# A lead sentence opens the paragraph: a printed name and title, then the verb.
_LEAD_START_RE = re.compile(
    r"^\s*[A-Z][A-Za-z'\u2019.\- ]{0,40}?,\s*(?:C\.\s*J\.|J\.)\s*,\s*(?:delivered|announced)\b"
)
# Where the paragraph has certainly ended: the slip opinion's rule and notice,
# the opinion's own caption or heading, or the preliminary print's counsel list.
# Only patterns no lineup line can match belong here — a paragraph cut short
# reads as a unanimous one, while one run long is refused as unreadable.
_END_RES: Final = (
    re.compile(r"^\s*_{3,}"),
    re.compile(r"^\s*NOTICE:"),
    re.compile(r"^\s*SUPREME COURT OF THE UNITED STATES\s*$"),
    re.compile(r"^\s*(?:CHIEF\s+)?JUSTICE\s+[A-Z]", re.I),
    re.compile(r"^\s*(?:PER CURIAM|Per Curiam)\.\s*$"),
    re.compile(r"^\s*Counsel\s*$"),
    # A counsel line opening on a person's full name ("Michael L. Zuckerman,
    # Deputy Solicitor General …"). Justices' names in a lineup are always
    # separated by a comma or "and", so two capitalized words then a comma open
    # a lineup line only where the first is a scope word a wrapped join left at
    # the line's start ("Part V. Kagan, J., filed …") or a title; those are
    # excluded, and the pattern ends nothing else.
    re.compile(
        r"^\s*(?!(?:Parts?|[Ff]ootnotes?|Chief|The|Justice|Justices)\b)"
        + r"[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z'\-]+,"
    ),
    # The preliminary print's counsel list. Anywhere in the line, because no
    # lineup sentence uses any of these words.
    re.compile(r"\b(?:re)?argued\b|\bon\s+the\s+briefs?\b|\bsubmitted\s+for\b", re.I),
)
# Running heads a page break drops into the paragraph.
_RUNNING_HEAD_RES: Final = (
    re.compile(r"^\s*(?:\d+\s+)?Cite as:.*$"),
    re.compile(r"^\s*(?:Syllabus|Opinion of the Court|Page Proof Pending Publication)\s*$"),
    re.compile(r"^\s*\d+\s+[^a-z]*\bv\.\s[^a-z]*$"),
    re.compile(r"^\s*\d+\s*$"),
)
# The text layer's stray spaces inside a name: the slip opinion sets names in
# small capitals and leaves a space after the full-size initial ("S OTOMAYOR"),
# and some preliminary prints split an initial the same way ("K avanaugh").
# Closed up only where the result is a roster surname, so "C. J." and any
# other capital-and-word pair are untouched.
_SPLIT_INITIAL_RE = re.compile(r"\b([A-Z]) ([A-Za-z]{2,})\b")
# A space the text layer leaves before a comma or period ("J .", "post , p").
_SPACE_BEFORE_PUNCT_RE = re.compile(r"[ \t]+(?=[,.])")


@dataclass(frozen=True)
class OpinionListing:
    """One row of a Term's opinions listing, as printed."""

    term: int
    number: str
    decided: date
    docket: str
    name: str
    url: str
    author_code: str

    @property
    def docket_number(self) -> str | None:
        """The row's Term-form docket number (``24-43``), or ``None``.

        The leading number where the cell carries more (``21-588 (21A85)``);
        ``None`` for an application or an original action.
        """
        match = _TERM_DOCKET_RE.match(self.docket)
        if match is None or parse_scotus_docket_number(match.group(1)) is None:
            return None
        return match.group(1)

    @property
    def volume_linked(self) -> bool:
        """Whether the link is into a whole preliminary-print or bound volume."""
        return "#" in self.url or "/preliminaryprint/" in self.url or "/boundvolumes/" in self.url


def listing_url(term: int) -> str:
    """The opinions listing for a two-digit October Term."""
    if not 0 <= term < 100:
        raise ValueError(f"term out of range: {term}")
    return LISTING_URL.format(term=term)


def _cell_text(cell: str) -> str:
    return " ".join(html.unescape(_TAG_RE.sub(" ", cell)).split())


def parse_listing(page: str, *, term: int) -> list[OpinionListing]:
    """Every opinion row of a listing page, in page order.

    A row needs the listing's six cells, a decision date and an opinion link;
    anything else (a header row, a layout table) is not an opinion row. Only
    the first link in the name cell is the opinion — a revised opinion's row
    carries its revision links after it.
    """
    rows: list[OpinionListing] = []
    for row in _ROW_RE.findall(page):
        cells = _CELL_RE.findall(row)
        if len(cells) < 6:
            continue
        href = _HREF_RE.search(cells[3])
        try:
            decided = datetime.strptime(_cell_text(cells[1]), "%m/%d/%y").date()
        except ValueError:
            continue
        if href is None:
            continue
        name_cell = cells[3].split("</a>", 1)[0]
        rows.append(
            OpinionListing(
                term=term,
                number=_cell_text(cells[0]),
                decided=decided,
                docket=_cell_text(cells[2]),
                name=_cell_text(name_cell),
                url=urljoin(_ORIGIN, html.unescape(href.group(1))),
                author_code=_cell_text(cells[4]),
            )
        )
    return rows


@dataclass(frozen=True)
class LocatedLineup:
    """The lineup paragraph and the header dates of one opinion's text."""

    paragraph: str | None
    argued: date | None
    decided: date | None
    problems: tuple[str, ...]


def _parse_date(raw: str) -> date | None:
    text = " ".join(raw.replace(".", "").split())
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _join_initial(match: re.Match[str]) -> str:
    joined = match.group(1) + match.group(2)
    return joined if resolve_surname(joined) is not None else match.group(0)


def _clean_line(line: str) -> str:
    """One line with the text layer's stray spaces inside names and before
    punctuation removed; nothing else about it changes."""
    return _SPLIT_INITIAL_RE.sub(_join_initial, _SPACE_BEFORE_PUNCT_RE.sub("", line))


def locate_lineup(text: str, *, truncated: bool = False) -> LocatedLineup:
    """Find the syllabus lineup paragraph and the argued/decided dates.

    The paragraph is the lines from the first lead sentence to the first line
    that ends it, running heads removed and lines rejoined with the line-end
    hyphenation the grammar closes up. The dates are read from the text before
    the paragraph — the syllabus caption — so nothing in the opinion's body is
    mistaken for them; the argument date is the latest printed, a reargument's.
    A paragraph that reaches the end of the text without meeting an end line
    is refused: the opinion always follows its syllabus, so text ending inside
    the lineup is text cut short — at the extraction cap (``truncated``), or
    by a damaged or partial document — and a lineup cut short reads as a
    unanimous one.
    """
    lines = text.splitlines()
    problems: list[str] = []
    start = next(
        (i for i, line in enumerate(lines) if _LEAD_START_RE.match(_clean_line(line))), None
    )
    if start is None:
        return LocatedLineup(None, None, None, ("no syllabus lineup paragraph found",))
    body: list[str] = []
    ended = False
    for line in lines[start:]:
        cleaned = _clean_line(line)
        if body and any(pattern.search(cleaned) for pattern in _END_RES):
            ended = True
            break
        if not cleaned.strip() or any(p.match(cleaned) for p in _RUNNING_HEAD_RES):
            continue
        body.append(cleaned.rstrip())
    if not ended:
        problems.append(
            "the lineup paragraph runs to the extraction cap"
            if truncated
            else "the lineup paragraph runs to the end of the text"
        )
    # The caption hyphenates across lines like any text ("—De-" / "cided").
    header = _HEADER_HYPHEN_RE.sub(r"\1\2", "\n".join(lines[:start]))
    argued = [d for m in _ARGUED_RE.finditer(header) if (d := _parse_date(m.group(1)))]
    decided_match = _DECIDED_RE.search(header)
    decided = _parse_date(decided_match.group(1)) if decided_match else None
    if decided is None:
        problems.append("no printed decision date before the lineup")
    return LocatedLineup(
        paragraph="\n".join(body) if not problems else None,
        argued=max(argued) if argued else None,
        decided=decided,
        problems=tuple(problems),
    )


class WritingReading(BaseModel):
    """One writing as the grammar read it, for the printed reading."""

    model_config = ConfigDict(frozen=True)

    kind: str
    authors: list[str]
    joins: list[str]
    scope: str | None = None


class OpinionLineupReading(BaseModel):
    """One listing row's reading: what was fetched, read, and would be written.

    ``status`` is ``read`` when the paragraph was located and parsed (whether or
    not the lineup is complete), ``skipped`` for a row outside the channel's
    scope, and ``failed`` when a fetch or the locator failed. ``votes`` and
    ``vote_provenance`` are present only when the lineup is complete and the
    reading has no problem — the record a writer would commit to
    ``Outcome.votes`` / ``Outcome.vote_provenance``.
    """

    term: int
    listing_number: str
    docket: str
    docket_number: str | None
    name: str
    url: str
    listed_decided: date
    listed_author: str
    status: Literal["read", "skipped", "failed"]
    reason: str | None = None
    argued: date | None = None
    decided: date | None = None
    bench: list[str] = []
    seated_after_argument: list[str] = []
    paragraph: str | None = None
    grammar: str | None = None
    grammar_version: int | None = None
    complete: bool = False
    writings_complete: bool = False
    writings: list[WritingReading] = []
    problems: list[str] = []
    votes: list[JusticeVote] | None = None
    vote_provenance: VoteProvenance | None = None


def vote_record(lineup: Lineup, *, document: str) -> tuple[list[JusticeVote], VoteProvenance]:
    """The ``Outcome.votes`` list and ``VoteProvenance`` a complete lineup yields.

    Raises ``ValueError`` on an incomplete lineup: this source records only
    whole benches, so a partial reading is never written as a partial list.
    """
    participating = lineup.participating
    if not lineup.complete or participating is None:
        raise ValueError("only a complete lineup yields a vote record")
    provenance = VoteProvenance(
        source=SUPREMECOURT_OPINIONS,
        document=document,
        grammar=lineup.grammar,
        grammar_version=lineup.grammar_version,
        participating=participating,
        complete=True,
    )
    return justice_votes(lineup), provenance


def _cross_check(entry: OpinionListing, lineup: Lineup, decided: date | None) -> list[str]:
    problems: list[str] = []
    if decided is not None and decided != entry.decided:
        problems.append(
            f"printed decision date {decided.isoformat()} is not the listing's "
            f"{entry.decided.isoformat()}"
        )
    lead = lineup.lead
    listed = LISTING_AUTHOR_CODES.get(entry.author_code)
    if listed is None:
        problems.append(f"listing author code {entry.author_code!r} is not on the roster")
    elif lead is not None and lead.kind in LEAD_KINDS and lead.author != listed:
        problems.append(f"the listing names {listed} as author but the lead reads {lead.author}")
    return problems


def _skip_reason(entry: OpinionListing) -> str | None:
    if entry.docket_number is None:
        return "not a Term-form merits docket (an application or an original action)"
    if entry.author_code == _PER_CURIAM_CODE:
        return "per curiam: its syllabus prints no lineup paragraph to read"
    if entry.volume_linked:
        return "volume-linked: the listing links into a whole volume, not one opinion"
    return None


class OpinionFetcher:
    """Fetches listing pages and opinion PDFs, optionally through a local cache.

    The cache is a directory of raw PDF bytes keyed by a hash of the URL, for
    re-reading the same opinions after a grammar change without asking the
    Court's site again. Listing pages are never cached: they change as the Term
    goes on. The cache is a dev convenience on the local disk, not the content
    store, and it is trusted as it lies: a cached file is read without the
    host scoping a fetch gets, so a lane that publishes what it reads — a
    writer stamping ``vote_provenance.document`` — must not pass ``cache_dir``.
    Each file is written whole or not at all, so an interrupted run leaves no
    partial PDF behind to be re-read.
    """

    def __init__(self, client: SupremeCourtClient, *, cache_dir: Path | None = None) -> None:
        self._client = client
        self._cache_dir = cache_dir

    def listing(self, term: int) -> list[OpinionListing]:
        page = self._client.get_document(listing_url(term))
        if page is None:
            return []
        return parse_listing(page.decode("utf-8", errors="replace"), term=term)

    def opinion(self, url: str) -> bytes | None:
        if self._cache_dir is None:
            return self._client.get_document(url)
        path = self._cache_dir / (hashlib.sha256(url.encode()).hexdigest() + ".pdf")
        if path.is_file():
            return path.read_bytes()
        data = self._client.get_document(url)
        if data is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            partial = path.with_suffix(f".{os.getpid()}.part")
            partial.write_bytes(data)
            partial.replace(path)
        return data


def _reading(entry: OpinionListing, **fields: object) -> OpinionLineupReading:
    return OpinionLineupReading.model_validate(
        {
            "term": entry.term,
            "listing_number": entry.number,
            "docket": entry.docket,
            "docket_number": entry.docket_number,
            "name": entry.name,
            "url": entry.url,
            "listed_decided": entry.decided,
            "listed_author": entry.author_code,
            **fields,
        }
    )


def read_text(entry: OpinionListing, text: str, *, truncated: bool) -> OpinionLineupReading:
    """Read one opinion's extracted text: locate, seat the bench, parse, check."""
    located = locate_lineup(text, truncated=truncated)
    if located.paragraph is None or located.decided is None:
        return _reading(
            entry,
            status="failed",
            reason="; ".join(located.problems),
            argued=located.argued,
            decided=located.decided,
        )
    try:
        bench = bench_on(located.decided)
    except ValueError as exc:
        return _reading(entry, status="failed", reason=str(exc), decided=located.decided)
    # With no printed argument date, anyone sworn in since the July before the
    # decision's Term could have missed the argument, so the convention credits
    # none of them: only the paragraph may place them.
    since = located.argued or date(october_term_year(located.decided), 7, 1)
    late = seated_after(since, bench)
    lineup = SCOTUS_SYLLABUS.parse(located.paragraph, bench=bench, seated_after_argument=late)
    problems = [*lineup.problems, *_cross_check(entry, lineup, located.decided)]
    usable = lineup.complete and not problems
    votes, provenance = vote_record(lineup, document=entry.url) if usable else (None, None)
    return _reading(
        entry,
        status="read",
        argued=located.argued,
        decided=located.decided,
        bench=list(bench),
        seated_after_argument=list(late),
        paragraph=located.paragraph,
        grammar=lineup.grammar,
        grammar_version=lineup.grammar_version,
        complete=lineup.complete,
        writings_complete=lineup.writings_complete,
        writings=[
            WritingReading(
                kind=str(w.kind),
                authors=list(w.authors),
                joins=[
                    j.justice if j.qualifier is None else f"{j.justice} ({j.qualifier})"
                    for j in w.joins
                ],
                scope=w.scope,
            )
            for w in lineup.writings
        ],
        problems=problems,
        votes=votes,
        vote_provenance=provenance,
    )


def read_entry(entry: OpinionListing, fetcher: OpinionFetcher) -> OpinionLineupReading:
    """Fetch and read one listing row, or say why it was skipped or failed."""
    if (reason := _skip_reason(entry)) is not None:
        return _reading(entry, status="skipped", reason=reason)
    try:
        data = fetcher.opinion(entry.url)
    except httpx.HTTPError as exc:
        return _reading(entry, status="failed", reason=f"fetch failed: {exc}")
    if data is None:
        return _reading(entry, status="failed", reason="the opinion is not served")
    extracted = extract_pdf_text(data, char_cap=TEXT_CHAR_CAP)
    if not extracted.text.strip():
        return _reading(entry, status="failed", reason="the PDF yielded no text")
    return read_text(entry, extracted.text, truncated=extracted.truncated)


def select(
    listing: Iterable[OpinionListing], *, dockets: Sequence[str] = (), limit: int | None = None
) -> list[OpinionListing]:
    """The rows to read: those whose docket number is named, else all, capped.

    ``limit`` counts in-scope rows only, so a cap of five reads five opinions
    rather than stopping at five application rows; the listing is cut at the
    first in-scope row past the cap.
    """
    wanted = {d.strip() for d in dockets if d.strip()}
    chosen: list[OpinionListing] = []
    in_scope = 0
    for entry in listing:
        if wanted and entry.docket_number not in wanted:
            continue
        if limit is not None and _skip_reason(entry) is None:
            if in_scope >= limit:
                break
            in_scope += 1
        chosen.append(entry)
    return chosen


def read_term(
    term: int,
    fetcher: OpinionFetcher,
    *,
    dockets: Sequence[str] = (),
    limit: int | None = None,
) -> list[OpinionLineupReading]:
    """Read one Term's listing, or the named dockets in it, row by row."""
    return [
        read_entry(entry, fetcher)
        for entry in select(fetcher.listing(term), dockets=dockets, limit=limit)
    ]
