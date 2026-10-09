"""The Court's orders as a per-Justice notation channel: fetch, split, read.

The cert- and interim-stage acts a Justice publishes — a noted vote to grant or
deny, a written dissent, concurrence or statement, a non-participation — appear
in two places on supremecourt.gov, and this module reads both:

- **Order lists and miscellaneous orders**, listed per October Term at
  ``/orders/ordersofthecourt/<YY>``. The list proper is one entry per docket
  (or group of dockets sharing one order): a caption line, then the order and
  its notations. Writings the Court publishes with the list — dissents from
  denial, statements, a summary disposition's per curiam — are appended after
  it, each opening on its own ``SUPREME COURT OF THE UNITED STATES`` caption.
- **Opinions Relating to Orders**, listed at ``/opinions/relatingtoorders/<YY>``:
  the same appended-writing shape as a standalone PDF, which is how an order on
  an application is usually published together with its writings.

**Read-only.** Nothing here writes the corpus, the content store, the ledger or
``data/``: :func:`read_day` and :func:`read_url` return readings, and the
``order-notations`` command prints them. The channel is registered as the
``supremecourt-orders`` vote source (:mod:`fedcourtsai.pipeline.vote_sources`),
and what it reads reaches the ledger only through the writer
(:mod:`fedcourtsai.vote_writer`).

**Splitting a document.** The list proper runs to the first appended caption.
A line opening on a docket number starts an entry (consecutive ones share the
order that follows; a parenthesized application number on the next line joins
the group), a line with no lowercase letter after the order text is a section
heading, and the order text is everything else. A consolidated caption may
print its docket numbers alone, one per line, then a column of brackets, then
a capitals caption line per docket: a line holding only a docket number opens
an entry when the caption goes on below it, bracket lines are dropped, and
capitals lines before the order text are the caption's. The extracted text
of a long list can lift some captions' serial numbers out of their lines
(``25- DOE …``) into a column of bare numbers above them; the column is
rejoined to those captions in order where every serial fits between its
neighbours, a problem otherwise, and never read as order text — nor is any
entry text with no letters, which is a problem. A change to the split
can hand either grammar different text, so it bumps both grammar versions.
An order-list entry may print a short writing inline, after a colon
(``Justice Jackson, dissenting: …``); its header is read and its body is not.
Each appended section is read for its dockets (``No. 25-848``, ``Nos. …``)
and date (``Decided June 15, 2026`` or ``[May 14, 2026]``), then line by
line: the order text before the first header is read by the notation
grammar, every line that opens a header sentence is read by the header
grammar, and a writing's body is skipped — except the lines after the
Court's own ``It is so ordered.``, where notations on a summary disposition
are printed.

**Cross-checks.** Every writing prints its author in its running head
(``ALITO, J., dissenting``, ``Statement of SOTOMAYOR, J.``), so the check
runs both ways within each section: a running head naming a Justice for
whom no header was read is a writing the split missed, and a header whose
author no running head names is a line of some writing's body taken for a
header. A header is only read where its sentence ends at a line's end, as a
header's own paragraph does. Either mismatch is a problem, and so is an
appended section dated other than its document.

**Assembly and completeness.** Each docket's reading is the union of every
piece that names it, across every document read. Votes merge — a Justice read
two ways is a problem — and any problem on a docket empties its vote list.
The vote list is never ``complete``: a Justice who noted nothing is
unobserved. Writings are ``writings_complete`` — every participating Justice
observed to have written or not — only when the reading covered **every
document the Court lists for the order's date** (:func:`read_day`, every
fetch and extraction whole), no document read for that date has a problem
(one that names no docket included), the docket has none, and no writing
is announced as forthcoming. A single
document (:func:`read_url`) never covers an order's writings.
"""

from __future__ import annotations

import html
import itertools
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Final, Literal
from urllib.parse import urldefrag, urljoin

import httpx
from pydantic import BaseModel

from ..schemas import JusticeVote, VoteValue, WritingRole
from ..supremecourt import SupremeCourtClient, october_term_year
from .documents import extract_pdf_text
from .justices import bench_on, resolve_surname
from .lineup import Lineup, Writing, WritingKind, writing_role
from .opinion_lineups import OpinionFetcher, WritingReading
from .order_grammars import (
    ORDER_NOTATIONS,
    WRITING_HEADERS,
    match_header,
    normalize_order_text,
)
from .vote_sources import is_order_document_url

#: Where a header may begin: a name or a ``Statement of`` a name.
HEADER_START_RE: Final = re.compile(
    r"^\s*(?:statement\s+of\s+)?(?:the\s+chief\s+justice|chief\s+justice|justice)\s+[A-Za-z]",
    re.I,
)

#: The Court's per-Term list of order lists and miscellaneous orders.
ORDERS_LISTING_URL: Final = "https://www.supremecourt.gov/orders/ordersofthecourt/{term:02d}"
#: The Court's per-Term list of Opinions Relating to Orders.
RELATING_LISTING_URL: Final = "https://www.supremecourt.gov/opinions/relatingtoorders/{term:02d}"
_ORIGIN: Final = "https://www.supremecourt.gov/"

#: How much of one document's text is extracted. The longest order lists run to
#: tens of thousands of characters with their appended writings; a document
#: still running at the cap is read, but cannot cover an order's writings.
TEXT_CHAR_CAP: Final = 600_000
#: How much of a piece's text a printed reading carries.
_PRINTED_TEXT_CAP: Final = 1_200
#: How many lines of an appended section may precede its date: the caption,
#: its docket lines and rules. A section whose date is not among them has none.
_CAPTION_LINES: Final = 30

DocumentKind = Literal["order-list", "miscellaneous-order", "relating-to-orders", "document"]

_ORDERS_ROW_RE = re.compile(
    r"(\d{2}/\d{2}/\d{2})(?:\s|&nbsp;)*+</span>\s*+<span[^>]*>\s*+"
    r"<a\s[^>]*href=['\"]([^'\"]+)['\"][^>]*>([^<]*)</a>",
    re.I | re.S,
)
_ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
_CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S | re.I)
_HREF_RE = re.compile(r"<a\s[^>]*href=['\"]([^'\"]+)['\"]", re.I)
_TAG_RE = re.compile(r"<[^>]+>")

_MONTH_DATE = r"[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}"
_COURT_CAPTION_RE = re.compile(r"^SUPREME COURT OF THE UNITED STATES$")
_DAY_LINE_RE = re.compile(
    r"^(?:MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY),\s+(?P<d>[A-Z]+\s+\d{1,2},\s+\d{4})$"
)
_LIST_TOP_RE = re.compile(r"^\(ORDER LIST\b")
# A caption is printed in capitals; a name particle (McCAULEY, PhRMA) leaves at
# most a stray lowercase letter, never a lowercase word, so a line of order text
# that happens to open on a docket number is not a caption.
_CAPTION_RE = re.compile(
    r"^(?P<docket>\d{2}-\d{1,5}|\d{2}[AMO]\d{1,5}|\d{1,3},\s*ORIG\.?)\s+(?!.*[a-z]{3})\S"
)
# A consolidated caption may print its docket numbers alone, one per line, then
# a column of brackets, then one capitals caption line per docket.
_BARE_DOCKET_RE = re.compile(r"^(?P<docket>\d{2}-\d{1,5}|\d{2}[AMO]\d{1,5})$")
_BRACKET_LINE_RE = re.compile(r"^[()\[\]{}| ]+$")
# A line of order text that runs on into a docket number on the next line.
_RUNS_INTO_DOCKET_RE = re.compile(r"(?:\bNos?\.|,|\band|\bor)$", re.I)
_APPLICATION_LINE_RE = re.compile(r"^\((?P<docket>\d{2}A\d{1,5})\)$")
# The extracted text of a long list can lift a caption's serial out of its
# line: the caption prints as ``25- DOE, JANE V. ROE`` and the page's lifted
# serials land together, above its captions, as a column of bare numbers.
_LIFTED_CAPTION_RE = re.compile(r"^(?P<prefix>\d{2})-\s+(?!.*[a-z]{3})\S")
_NUMBER_LINE_RE = re.compile(r"^\d{1,5}$")
_DOCKET_SERIAL_RE = re.compile(r"^(?P<prefix>\d{2})-(?P<serial>\d{1,5})$")
_LETTER_RE = re.compile(r"[A-Za-z]")
_PAGE_NUMBER_RE = re.compile(r"^\d{1,3}$")
_RULE_RE = re.compile(r"^[_\u2014\u2013\-]{3,}$")
_CITE_AS_RE = re.compile(r"^(?:\d+\s+)?Cite as:.*$")
_RUNNING_HEAD_RE = re.compile(
    r"^(?:\d+\s+)?(?:(?:Statement|Opinion)\s+of\s+)?"
    r"(?P<name>[A-Z][A-Z'\-]+(?:\s+[A-Z][A-Z'\-]+)?),\s*(?:C\.\s*)?J\.(?:,\s*[a-z][a-z ]*)?$"
)
_CASE_HEAD_RE = re.compile(r"^\d+\s+[^a-z]*\bv\.\s[^a-z]*$")
_COURT_HEAD_RE = re.compile(r"^(?:Per Curiam|Opinion of the Court)$")
_PER_CURIAM_RE = re.compile(r"^PER CURIAM\.$")
_SO_ORDERED_RE = re.compile(r"\bIt is so ordered\.")
_SECTION_DATE_RE = re.compile(rf"(?:\bDecided\s+(?P<a>{_MONTH_DATE})|^\[(?P<b>{_MONTH_DATE})\]$)")
_SECTION_DOCKETS_RE = re.compile(r"\bNos?\.\s+(?P<list>[^.\d]*+\d[^.]*+)(?:\.\s|\.$|$)")
_DOCKET_TOKEN_RE = re.compile(r"\d{2}[-\u2013\u2014]\d{1,5}|\d{2}A\d{1,5}|\d{1,3},?\s*Orig\b", re.I)
_INLINE_START_RE = re.compile(
    r"(?:^|(?<=[.:)]\s))(?=(?:statement\s+of\s+)?(?:the\s+chief\s+justice|chief\s+justice|justice)\s)",
    re.I,
)
_HEADING_RE = re.compile(r"^[A-Z][A-Z .,'&\-]*$")
# Orphan text that could be a Justice's act: any Justice named, or any act word.
_TRIGGER_RE = re.compile(
    r"\bjustice\s+[a-z]|\bwould\s+(?:grant|deny)\b|\btook\s+no\s+part\b"
    + r"|\bdissent|\bconcur|\brespecting\b",
    re.I,
)


@dataclass(frozen=True)
class OrderDocumentRef:
    """One document the Court lists for a date: an order list, a miscellaneous
    order, or an opinion relating to orders."""

    url: str
    day: date
    kind: DocumentKind
    label: str


def orders_listing_url(term: int) -> str:
    """The order-list listing for a two-digit October Term."""
    if not 0 <= term < 100:
        raise ValueError(f"term out of range: {term}")
    return ORDERS_LISTING_URL.format(term=term)


def relating_listing_url(term: int) -> str:
    """The Opinions-Relating-to-Orders listing for a two-digit October Term."""
    if not 0 <= term < 100:
        raise ValueError(f"term out of range: {term}")
    return RELATING_LISTING_URL.format(term=term)


def _listed_day(raw: str) -> date | None:
    try:
        return datetime.strptime(raw.strip(), "%m/%d/%y").date()
    except ValueError:
        return None


def parse_orders_listing(page: str) -> list[OrderDocumentRef]:
    """Every order-list and miscellaneous-order link on a listing page, with its date."""
    refs: list[OrderDocumentRef] = []
    for raw_day, href, label in _ORDERS_ROW_RE.findall(page):
        day = _listed_day(raw_day)
        url = urljoin(_ORIGIN, html.unescape(href))
        if day is None or not is_order_document_url(url):
            continue
        text = " ".join(html.unescape(label).split())
        kind: DocumentKind = "order-list" if text.lower() == "order list" else "miscellaneous-order"
        refs.append(OrderDocumentRef(url=url, day=day, kind=kind, label=text))
    return refs


def _cell_text(cell: str) -> str:
    return " ".join(html.unescape(_TAG_RE.sub(" ", cell)).split())


def parse_relating_listing(page: str) -> list[OrderDocumentRef]:
    """Every Opinions-Relating-to-Orders PDF on a listing page, once each.

    The listing prints one row per writing, several rows linking into one PDF
    at different pages; the document is the PDF, so the fragment is dropped
    and each PDF is listed once, labelled with its first row's docket.
    """
    refs: dict[str, OrderDocumentRef] = {}
    for row in _ROW_RE.findall(page):
        cells = _CELL_RE.findall(row)
        if len(cells) < 3:
            continue
        day = _listed_day(_cell_text(cells[0]))
        href = _HREF_RE.search(cells[2])
        if day is None or href is None:
            continue
        url = urldefrag(urljoin(_ORIGIN, html.unescape(href.group(1)))).url
        if not is_order_document_url(url) or url in refs:
            continue
        label = f"{_cell_text(cells[1])} {_cell_text(cells[2])}".strip()
        refs[url] = OrderDocumentRef(url=url, day=day, kind="relating-to-orders", label=label)
    return list(refs.values())


# --- Splitting one document --------------------------------------------------


@dataclass(frozen=True)
class OrderPiece:
    """One piece of a document a grammar reads, and the dockets it belongs to.

    ``where`` is ``list-entry`` (an order-list entry's order text),
    ``order-text`` (an appended section's order, or the lines after its
    ``It is so ordered.``) or ``header`` (one writing's header sentence).
    ``section`` numbers the appended section the piece came from (``None`` in
    the list proper), for the running-head cross-check.
    """

    dockets: tuple[str, ...]
    where: Literal["list-entry", "order-text", "header"]
    text: str
    day: date | None
    section: int | None = None


@dataclass(frozen=True)
class SectionHeads:
    """The authors one appended section's running heads name, by docket."""

    section: int
    dockets: tuple[str, ...]
    authors: frozenset[str]


@dataclass(frozen=True)
class SplitDocument:
    """A document cut into grammar-sized pieces, with what the cut itself found.

    ``problems`` are the document's own: text the cut could assign to no
    docket that is shaped like a Justice's act, a section with no dockets, a
    running head naming nobody on the roster, a column of lifted caption
    serials that does not fit its captions (or a lifted caption with no
    column, or a column no caption claims), or an entry whose order text has
    no letters. ``docket_problems`` belong to
    single dockets (a section dated other than its document).
    """

    day: date | None
    pieces: tuple[OrderPiece, ...]
    heads: tuple[SectionHeads, ...]
    problems: tuple[str, ...]
    docket_problems: Mapping[str, tuple[str, ...]]


def _parse_long_date(raw: str) -> date | None:
    text = " ".join(raw.replace(".", "").split()).title()
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _docket(raw: str) -> str:
    token = " ".join(raw.replace("\u2013", "-").replace("\u2014", "-").split())
    orig = re.match(r"^(\d{1,3}),?\s*orig\b", token, re.I)
    return f"{orig.group(1)}, Orig." if orig else token.upper()


def _is_page_furniture(line: str) -> bool:
    return bool(
        _PAGE_NUMBER_RE.match(line)
        or _RULE_RE.match(line)
        or _CITE_AS_RE.match(line)
        or _CASE_HEAD_RE.match(line)
        or _COURT_HEAD_RE.match(line)
        or _RUNNING_HEAD_RE.match(line)
    )


@dataclass
class _Group:
    dockets: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)


def _inline_pieces(dockets: tuple[str, ...], text: str, day: date | None) -> list[OrderPiece]:
    """An entry's notation text, and the header of each writing printed inline.

    An inline writing opens on a header ending in a colon; its body runs to
    the end of the entry and is not read.
    """
    normalized = normalize_order_text(text)
    pieces: list[OrderPiece] = []
    cut: int | None = None
    for start in _INLINE_START_RE.finditer(normalized):
        header = match_header(normalized[start.start() :])
        if header is None or not header.endswith(":"):
            continue
        if cut is None:
            cut = start.start()
        pieces.append(OrderPiece(dockets, "header", header, day))
    notation = normalized if cut is None else normalized[:cut]
    if notation.strip():
        pieces.insert(0, OrderPiece(dockets, "list-entry", notation.strip(), day))
    return pieces


def _opens_bare_caption(lines: Sequence[str], index: int) -> bool:
    """Whether a line holding only a docket number opens a caption.

    It does when the caption goes on: the next line of text is another docket
    number, a bracket column, an application number or a capitals caption
    line. A line of order text that wraps to leave a docket number alone
    (``… with No.`` / ``25-200`` / ``and a total …``) runs into it from above
    and goes on in lowercase; either rules the caption out, so a wrap followed
    by a section heading does not open an entry the next caption would join.
    """
    above = next(
        (line for line in reversed(lines[:index]) if line and not _is_page_furniture(line)),
        "",
    )
    if _RUNS_INTO_DOCKET_RE.search(above):
        return False
    for line in lines[index + 1 :]:
        if not line or _is_page_furniture(line):
            continue
        return bool(
            _BARE_DOCKET_RE.match(line)
            or _BRACKET_LINE_RE.match(line)
            or _APPLICATION_LINE_RE.match(line)
            or _HEADING_RE.match(line)
        )
    return False


def _neighbor_serial(lines: Sequence[str], indices: Iterable[int], prefix: str) -> int | None:
    """The serial of the first whole caption at ``indices`` carrying ``prefix``."""
    for i in indices:
        caption = _CAPTION_RE.match(lines[i])
        if caption is None:
            continue
        whole = _DOCKET_SERIAL_RE.match(_docket(caption.group("docket")))
        if whole is not None and whole.group("prefix") == prefix:
            return int(whole.group("serial"))
    return None


def _number_runs(lines: Sequence[str]) -> list[list[int]]:
    """The line indices of each run of bare-number lines, blank lines between them aside."""
    runs: list[list[int]] = []
    last_text: int | None = None
    for index, line in enumerate(lines):
        if not line:
            continue
        if _NUMBER_LINE_RE.match(line):
            if runs and last_text is not None and runs[-1][-1] == last_text:
                runs[-1].append(index)
            else:
                runs.append([index])
        last_text = index
    return runs


def _pair_column(
    lines: Sequence[str], run: Sequence[int], claimants: Sequence[int]
) -> dict[int, str] | None:
    """The claimants' rejoined dockets, or ``None`` if the column does not fit them.

    The run's last numbers are the serials, in the claimants' order; at most
    one number ahead of them may be a page number. Every serial must ascend
    and sit between the whole captions printed around its claimant
    (``25-1374`` < ``25-1375`` < ``25-1377``), at least one of which must be
    there to bound it.
    """
    if len(run) < len(claimants):
        return None
    lead = run[: len(run) - len(claimants)]
    if len(lead) > 1 or not all(_PAGE_NUMBER_RE.match(lines[i]) for i in lead):
        return None
    pairs: list[tuple[int, str, int]] = []
    for claimant, serial_index in zip(claimants, run[len(lead) :], strict=True):
        found = _LIFTED_CAPTION_RE.match(lines[claimant])
        assert found is not None
        pairs.append((claimant, found.group("prefix"), int(lines[serial_index])))
    serials = [serial for _claimant, _prefix, serial in pairs]
    if any(later <= earlier for earlier, later in itertools.pairwise(serials)):
        return None
    for claimant, prefix, serial in pairs:
        below = _neighbor_serial(lines, range(claimant - 1, -1, -1), prefix)
        above = _neighbor_serial(lines, range(claimant + 1, len(lines)), prefix)
        if below is None and above is None:
            return None
        if (below is not None and below >= serial) or (above is not None and above <= serial):
            return None
    return {claimant: f"{prefix}-{serial}" for claimant, prefix, serial in pairs}


def _rejoin_lifted_serials(
    lines: Sequence[str],
) -> tuple[dict[int, str], set[int], list[str]]:
    """Captions whose serial the extraction lifted out, rejoined to it.

    A run of bare-number lines is claimed by the lifted captions (``25- DOE …``)
    that follow it before the next run, and rejoined to them by
    :func:`_pair_column`; a column that does not fit is a problem, and its
    claimants stay unnumbered. Every run's lines are dropped either way, so a
    column of numbers is never read as an entry's order text. A run of more
    than one number that no caption claims is a problem too, as is a lifted
    caption no run precedes.

    Returns the rejoined docket by line index, the line indices to drop, and
    the problems.
    """
    runs = _number_runs(lines)
    lifted = [i for i, line in enumerate(lines) if _LIFTED_CAPTION_RE.match(line)]
    rejoined: dict[int, str] = {}
    dropped: set[int] = set()
    problems: list[str] = []
    claimed: set[int] = set()
    for number, run in enumerate(runs):
        dropped.update(run)
        end = runs[number + 1][0] if number + 1 < len(runs) else len(lines)
        claimants = [i for i in lifted if run[-1] < i < end]
        claimed.update(claimants)
        column = " ".join(lines[i] for i in run)
        if not claimants:
            if len(run) > 1:
                problems.append(f"a column of bare numbers no caption claims: {column[:160]!r}")
            continue
        paired = _pair_column(lines, run, claimants)
        if paired is None:
            problems.append(
                f"{len(claimants)} caption(s) printed without a serial could not be "
                f"rejoined to the column {column[:160]!r}"
            )
            continue
        rejoined.update(paired)
    problems.extend(
        f"a caption printed without a serial: {lines[index][:160]!r}"
        for index in lifted
        if index not in claimed
    )
    return rejoined, dropped, problems


def _split_list(  # noqa: PLR0912 - one branch per line shape the list prints
    lines: Sequence[str], day: date | None
) -> tuple[list[OrderPiece], list[str]]:
    """The list proper's entries, and any orphan text shaped like a Justice's act."""
    groups: list[_Group] = []
    current: _Group | None = None
    orphans: list[str] = []
    rejoined, dropped, problems = _rejoin_lifted_serials(lines)
    for index, line in enumerate(lines):
        if not line or _LIST_TOP_RE.match(line) or _DAY_LINE_RE.match(line):
            continue
        if index in dropped or _is_page_furniture(line) or _BRACKET_LINE_RE.match(line):
            continue
        docket: str | None = None
        if (caption := _CAPTION_RE.match(line)) is not None:
            docket = _docket(caption.group("docket"))
        elif (bare := _BARE_DOCKET_RE.match(line)) is not None and _opens_bare_caption(
            lines, index
        ):
            docket = _docket(bare.group("docket"))
        # A lifted caption that could not be rejoined still opens its entry, so
        # the order below it is not read onto the captions above; its own docket
        # is unknown, and the problem is already recorded.
        if docket is not None or index in rejoined or _LIFTED_CAPTION_RE.match(line):
            if current is None or current.lines:
                current = _Group()
                groups.append(current)
            if (docket := docket or rejoined.get(index)) is not None:
                current.dockets.append(docket)
            continue
        if (application := _APPLICATION_LINE_RE.match(line)) is not None and current is not None:
            current.dockets.append(_docket(application.group("docket")))
            continue
        if _HEADING_RE.match(line):
            # A caption wrapped onto a second line, or a section heading.
            if current is not None and current.lines:
                current = None
            continue
        if current is None:
            orphans.append(line)
        else:
            current.lines.append(line)
    pieces: list[OrderPiece] = []
    for group in groups:
        if group.lines:
            text = "\n".join(group.lines)
            if not _LETTER_RE.search(text):
                # A run of bare numbers or punctuation is never an order.
                problems.append(f"an entry's order text has no letters: {text[:160]!r}")
            pieces.extend(_inline_pieces(tuple(group.dockets), text, day))
    orphan_text = normalize_order_text("\n".join(orphans))
    if _TRIGGER_RE.search(orphan_text):
        problems.append(f"text outside any entry reads like a notation: {orphan_text[:160]!r}")
    return pieces, problems


def _heads_before(lines: Sequence[str], index: int, floor: int) -> int:
    """How many lines above ``index`` (not below ``floor``) are the next page's furniture."""
    start = index
    while start - 1 >= floor and index - (start - 1) <= 4:
        line = lines[start - 1]
        if line and not _is_page_furniture(line):
            break
        start -= 1
    return start


def _head_author(line: str) -> str | Literal[False] | None:
    """The Justice a running head names; ``None`` for a court head; ``False`` if unknown."""
    match = _RUNNING_HEAD_RE.match(line)
    if match is None:
        return None
    return resolve_surname(match.group("name").split()[-1]) or False


def _line_header(body: Sequence[str], index: int) -> str | None:
    """The header sentence opening at ``body[index]``, if it ends where a line ends.

    A writing's header is set as its own paragraph, so its period closes a
    line; a sentence of a writing's body that opens on a name and runs on
    (``JUSTICE ALITO, dissenting from the denial of certiorari in Doe v. Roe,
    warned …``) never ends at a line's end after its first period.
    """
    for end in range(index + 1, min(index + 4, len(body)) + 1):
        joined = normalize_order_text("\n".join(body[index:end])).strip()
        header = match_header(joined)
        if header is not None and header.endswith(".") and header == joined:
            return header
    return None


def _split_section(  # noqa: PLR0912 - one branch per line shape a section prints
    lines: Sequence[str], number: int, heads_above: Sequence[str]
) -> tuple[list[OrderPiece], SectionHeads | None, list[str], date | None]:
    """One appended section's pieces, its running heads, its problems, its date."""
    problems: list[str] = []
    date_index = next(
        (i for i, line in enumerate(lines[:_CAPTION_LINES]) if _SECTION_DATE_RE.search(line)),
        None,
    )
    if date_index is None:
        return [], None, ["an appended section prints no date"], None
    found = _SECTION_DATE_RE.search(lines[date_index])
    assert found is not None
    day = _parse_long_date(found.group("a") or found.group("b"))
    caption = " ".join(lines[: date_index + 1][:_CAPTION_LINES])
    dockets: list[str] = []
    for listed in _SECTION_DOCKETS_RE.finditer(caption):
        for token in _DOCKET_TOKEN_RE.findall(listed.group("list")):
            if (docket := _docket(token)) not in dockets:
                dockets.append(docket)
    if not dockets:
        return [], None, [f"an appended section names no docket: {caption[:160]!r}"], day
    key = tuple(dockets)

    authors: set[str] = set()
    for line in [*heads_above, *lines[date_index + 1 :]]:
        author = _head_author(line)
        if author is False:
            problems.append(f"a running head names nobody on the roster: {line!r}")
        elif author is not None:
            authors.add(author)

    pieces: list[OrderPiece] = []
    order_lines: list[str] = []
    mode: Literal["order", "court", "writing"] = "order"
    body = lines[date_index + 1 :]
    for index, line in enumerate(body):
        if not line or _is_page_furniture(line):
            continue
        normalized = normalize_order_text(line)
        if _PER_CURIAM_RE.match(normalized):
            mode = "court"
            continue
        if HEADER_START_RE.match(normalized) and (header := _line_header(body, index)):
            pieces.append(OrderPiece(key, "header", header, day, number))
            mode = "writing"
            continue
        if mode == "court" and _SO_ORDERED_RE.search(normalized):
            order_lines.append(normalized.split("It is so ordered.", 1)[1])
            mode = "order"
            continue
        if mode == "order":
            order_lines.append(line)
    order_text = normalize_order_text("\n".join(order_lines)).strip()
    if order_text:
        pieces.insert(0, OrderPiece(key, "order-text", order_text, day, number))
    return pieces, SectionHeads(number, key, frozenset(authors)), problems, day


def split_document(text: str) -> SplitDocument:
    """Cut one order document's extracted text into pieces for the grammars."""
    lines = [normalize_order_text(line) for line in text.splitlines()]
    day: date | None = None
    for line in [line for line in lines if line][:6]:
        if (match := _DAY_LINE_RE.match(line)) is not None:
            day = _parse_long_date(match.group("d"))
            break
    captions = [i for i, line in enumerate(lines) if _COURT_CAPTION_RE.match(line)]
    problems: list[str] = []
    docket_problems: dict[str, list[str]] = {}

    list_end = _heads_before(lines, captions[0], 0) if captions else len(lines)
    pieces, list_problems = _split_list(lines[:list_end], day)
    problems.extend(list_problems)

    heads: list[SectionHeads] = []
    for number, caption_index in enumerate(captions):
        top = _heads_before(lines, caption_index, 0 if number == 0 else captions[number - 1] + 1)
        bottom = (
            _heads_before(lines, captions[number + 1], caption_index + 1)
            if number + 1 < len(captions)
            else len(lines)
        )
        section_pieces, section_heads, section_problems, section_day = _split_section(
            lines[caption_index + 1 : bottom], number, lines[top:caption_index]
        )
        if day is None:
            day = section_day
        if section_heads is None:
            problems.extend(section_problems)
            continue
        heads.append(section_heads)
        pieces.extend(section_pieces)
        for docket in section_heads.dockets:
            listed = docket_problems.setdefault(docket, [])
            listed.extend(section_problems)
            if section_day is not None and day is not None and section_day != day:
                listed.append(
                    f"an appended section is dated {section_day.isoformat()}, "
                    f"its document {day.isoformat()}"
                )
    return SplitDocument(
        day=day,
        pieces=tuple(pieces),
        heads=tuple(heads),
        problems=tuple(problems),
        docket_problems={k: tuple(v) for k, v in docket_problems.items() if v},
    )


# --- Reading and assembly ----------------------------------------------------


class OrderPartReading(BaseModel):
    """One piece as one grammar read it."""

    document: str
    where: str
    grammar: str
    grammar_version: int
    text: str
    votes: dict[str, VoteValue] = {}
    writings: list[WritingReading] = []
    problems: list[str] = []


class OrderDocketReading(BaseModel):
    """One docket's notations and writings on one order date.

    ``votes`` is partial by construction (``complete`` is always false): only
    the Justices the order names are there. ``writing_roles`` is every
    participating Justice's role when ``writings_complete``, and the authors'
    only otherwise; ``votes[].writing`` follows it, so a Justice is never
    recorded as having written nothing unless every writing was observed.
    """

    docket: str
    order_date: date | None
    documents: list[str]
    bench: list[str]
    complete: Literal[False] = False
    writings_complete: bool
    votes: list[JusticeVote]
    writing_roles: dict[str, WritingRole | None]
    writings: list[WritingReading]
    problems: list[str]
    parts: list[OrderPartReading]


class OrderDocumentReading(BaseModel):
    """One fetched document: what it is, whether it was read, what it named."""

    url: str
    kind: str
    label: str | None = None
    listed_date: date | None = None
    printed_date: date | None = None
    status: Literal["read", "failed"]
    reason: str | None = None
    truncated: bool = False
    dockets: list[str] = []
    problems: list[str] = []


class OrderDayReading(BaseModel):
    """Every document read for one order date (or one URL), and every docket in them.

    ``covers_the_day`` is true only when every document the Court lists for
    the date was fetched and extracted whole — the precondition for any
    docket's ``writings_complete``.
    """

    date: date | None
    covers_the_day: bool
    documents: list[OrderDocumentReading]
    dockets: list[OrderDocketReading]


def _writing_reading(writing: Writing) -> WritingReading:
    return WritingReading(
        kind=str(writing.kind),
        authors=list(writing.authors),
        joins=[
            j.justice if j.qualifier is None else f"{j.justice} ({j.qualifier})"
            for j in writing.joins
        ],
        scope=writing.scope,
    )


def _printed(text: str) -> str:
    return text if len(text) <= _PRINTED_TEXT_CAP else text[:_PRINTED_TEXT_CAP] + " …"


@dataclass
class _DocketParts:
    day: date | None = None
    documents: list[str] = field(default_factory=list)
    lineups: list[tuple[str, OrderPiece, Lineup]] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    #: Running-head authors of each appended section naming this docket, by
    #: (document, section number).
    heads: dict[tuple[str, int], frozenset[str]] = field(default_factory=dict)


def _writing_key(writing: Writing) -> tuple[WritingKind, tuple[str, ...]]:
    return writing.kind, writing.authors


def _assemble(  # noqa: PLR0912 - each merge rule is its own check
    docket: str, parts: _DocketParts, *, covers_the_day: bool
) -> OrderDocketReading:
    """One docket's reading from every piece that names it."""
    problems = list(parts.problems)
    bench: tuple[str, ...] = ()
    if parts.day is not None:
        try:
            bench = bench_on(parts.day)
        except ValueError as exc:
            problems.append(str(exc))
    votes: dict[str, VoteValue] = {}
    writings: dict[tuple[WritingKind, tuple[str, ...]], Writing] = {}
    for _, _, lineup in parts.lineups:
        bench = bench or lineup.bench
        if lineup.bench != bench:
            problems.append("pieces of one docket were read against different benches")
        problems.extend(lineup.problems)
        for name, vote in lineup.votes.items():
            held = votes.get(name)
            if held is not None and held is not vote:
                problems.append(f"{name} is read both as {held} and as {vote}")
            votes[name] = vote
        for writing in lineup.writings:
            key = _writing_key(writing)
            if key in writings and writings[key] != writing:
                problems.append(
                    f"two readings of {' and '.join(writing.authors)}'s {writing.kind} disagree"
                )
            writings.setdefault(key, writing)
    absent = {name for name, vote in votes.items() if vote is VoteValue.did_not_participate}
    for writing in writings.values():
        for name in sorted(writing.signatories & absent):
            problems.append(f"{name} took no part but signs a {writing.kind}")
    missing, unheaded = _unmatched_heads(parts)
    for name in missing:
        problems.append(f"a running head names {name} but no header of theirs was read")
    for name in unheaded:
        problems.append(f"a header by {name} has no running head of theirs in its section")

    if not bench:
        problems.append("no bench to read the order against")
    complete_writings = covers_the_day and not problems
    roles: dict[str, list[WritingKind]] = {}
    if complete_writings:
        for name in bench:
            if name not in absent:
                roles[name] = []
    for writing in writings.values():
        for author in writing.authors:
            roles.setdefault(author, []).append(writing.kind)
    writing_roles = {name: writing_role(kinds) for name, kinds in roles.items()}
    kept = {} if problems else votes
    return OrderDocketReading(
        docket=docket,
        order_date=parts.day,
        documents=parts.documents,
        bench=list(bench),
        writings_complete=complete_writings,
        votes=[
            JusticeVote(justice=name, vote=kept[name], writing=writing_roles.get(name))
            for name in bench
            if name in kept
        ],
        writing_roles=writing_roles,
        writings=[_writing_reading(w) for w in writings.values()],
        problems=problems,
        parts=[
            OrderPartReading(
                document=document,
                where=piece.where,
                grammar=lineup.grammar,
                grammar_version=lineup.grammar_version,
                text=_printed(piece.text),
                votes=dict(lineup.votes),
                writings=[_writing_reading(w) for w in lineup.writings],
                problems=list(lineup.problems),
            )
            for document, piece, lineup in parts.lineups
        ],
    )


def _unmatched_heads(parts: _DocketParts) -> tuple[list[str], list[str]]:
    """Running heads with no header read, and headers with no running head.

    Per section, both ways: every page of a writing carries its author's
    running head, so a head whose author has no header in the same section
    is a writing the split missed, and a header whose author no head names
    is a line of some writing's body the split took for a header.
    """
    read: dict[tuple[str, int], set[str]] = {}
    for document, piece, lineup in parts.lineups:
        if piece.section is not None and piece.where == "header":
            key = (document, piece.section)
            for writing in lineup.writings:
                read.setdefault(key, set()).update(writing.authors)
    missing: list[str] = []
    for key, authors in parts.heads.items():
        missing.extend(sorted(authors - read.get(key, set())))
    unheaded: list[str] = []
    for key, written in read.items():
        unheaded.extend(sorted(written - parts.heads.get(key, frozenset())))
    return missing, unheaded


@dataclass(frozen=True)
class FetchedDocument:
    """One document's extracted text, or why there is none."""

    url: str
    ref: OrderDocumentRef | None
    text: str | None
    truncated: bool = False
    reason: str | None = None


def read_documents(  # noqa: PLR0912 - per-document failure paths, each recorded
    documents: Sequence[FetchedDocument], *, day: date | None, covers_the_day: bool
) -> OrderDayReading:
    """Split every document, read every piece, and assemble each docket.

    ``covers_the_day`` says the documents are every one the Court lists for
    ``day``, each fetched and extracted whole; only then can a docket's
    writings be complete. No network: the caller fetched the text.
    """
    readings: list[OrderDocumentReading] = []
    dockets: dict[str, _DocketParts] = {}
    for document in documents:
        kind: str = document.ref.kind if document.ref else "document"
        label = document.ref.label if document.ref else None
        listed = document.ref.day if document.ref else None
        if document.text is None:
            readings.append(
                OrderDocumentReading(
                    url=document.url,
                    kind=kind,
                    label=label,
                    listed_date=listed,
                    status="failed",
                    reason=document.reason,
                )
            )
            continue
        split = split_document(document.text)
        doc_problems = list(split.problems)
        if listed is not None and split.day is not None and split.day != listed:
            doc_problems.append(
                f"printed date {split.day.isoformat()} is not the listing's {listed.isoformat()}"
            )
        if document.truncated:
            doc_problems.append("the text was cut at the extraction cap")
        order_day = listed or split.day
        named: list[str] = []
        for piece in split.pieces:
            piece_day = piece.day or order_day
            if piece_day is None:
                doc_problems.append("a piece with no date to seat a bench by")
                continue
            try:
                bench = bench_on(piece_day)
            except ValueError as exc:
                doc_problems.append(str(exc))
                continue
            grammar = WRITING_HEADERS if piece.where == "header" else ORDER_NOTATIONS
            lineup = grammar.parse(piece.text, bench=bench)
            for docket in piece.dockets:
                parts = dockets.setdefault(docket, _DocketParts(day=order_day))
                if document.url not in parts.documents:
                    parts.documents.append(document.url)
                parts.lineups.append((document.url, piece, lineup))
                if docket not in named:
                    named.append(docket)
        for section in split.heads:
            for docket in section.dockets:
                parts = dockets.setdefault(docket, _DocketParts(day=order_day))
                parts.heads[(document.url, section.section)] = section.authors
        for docket, found in split.docket_problems.items():
            dockets.setdefault(docket, _DocketParts(day=order_day)).problems.extend(found)
        for docket in named:
            dockets[docket].problems.extend(f"in {document.url}: {p}" for p in doc_problems)
        readings.append(
            OrderDocumentReading(
                url=document.url,
                kind=kind,
                label=label,
                listed_date=listed,
                printed_date=split.day,
                status="read",
                truncated=document.truncated,
                dockets=named,
                problems=doc_problems,
            )
        )
    # A problem on any document of the day — one that names no docket
    # included — could be a writing the reading lacks, so it uncovers the day.
    covers_the_day = covers_the_day and not any(r.problems or r.status != "read" for r in readings)
    return OrderDayReading(
        date=day,
        covers_the_day=covers_the_day,
        documents=readings,
        dockets=[
            _assemble(docket, dockets[docket], covers_the_day=covers_the_day)
            for docket in sorted(dockets)
        ],
    )


# --- Fetching ----------------------------------------------------------------


class OrderFetcher:
    """Fetches the two per-Term listings and the documents they link.

    Listing pages are never cached (they grow through the Term); documents go
    through :class:`~fedcourtsai.pipeline.opinion_lineups.OpinionFetcher`, so
    ``cache_dir`` is the same dev-only raw-PDF cache with the same caveat: a
    cached file is trusted as it lies, so no publishing lane may pass one.
    """

    def __init__(self, client: SupremeCourtClient, *, cache_dir: Path | None = None) -> None:
        self._client = client
        self._documents = OpinionFetcher(client, cache_dir=cache_dir)

    def _page(self, url: str) -> str:
        page = self._client.get_document(url)
        if page is None:
            raise httpx.HTTPError(f"listing not served: {url}")
        return page.decode("utf-8", errors="replace")

    def listed(self, term: int) -> list[OrderDocumentRef]:
        """Every document both listings carry for one Term."""
        return [
            *parse_orders_listing(self._page(orders_listing_url(term))),
            *parse_relating_listing(self._page(relating_listing_url(term))),
        ]

    def document(self, url: str, ref: OrderDocumentRef | None = None) -> FetchedDocument:
        """One document's text, or the reason it has none. Never raises on a fetch."""
        try:
            data = self._documents.opinion(url)
        except httpx.HTTPError as exc:
            return FetchedDocument(url, ref, None, reason=f"fetch failed: {exc}")
        if data is None:
            return FetchedDocument(url, ref, None, reason="the document is not served")
        extracted = extract_pdf_text(data, char_cap=TEXT_CHAR_CAP)
        if not extracted.text.strip():
            return FetchedDocument(url, ref, None, reason="the PDF yielded no text")
        return FetchedDocument(url, ref, extracted.text, truncated=extracted.truncated)


def read_day(day: date, fetcher: OrderFetcher) -> OrderDayReading:
    """Read every order and opinion relating to orders the Court lists for ``day``.

    The listings are the October Term's that ``day`` falls in. A listing that
    cannot be fetched raises (``httpx.HTTPError``); a document that cannot be
    read is recorded on its reading and leaves the day uncovered.
    """
    term = october_term_year(day) % 100
    refs = [ref for ref in fetcher.listed(term) if ref.day == day]
    documents = [fetcher.document(ref.url, ref) for ref in refs]
    covers = bool(documents) and all(d.text is not None and not d.truncated for d in documents)
    return read_documents(documents, day=day, covers_the_day=covers)


def read_url(url: str, fetcher: OrderFetcher) -> OrderDayReading:
    """Read one order or opinion-relating-to-orders PDF by its URL.

    One document never covers an order's writings, so no docket read this way
    is ``writings_complete``. Raises ``ValueError`` for a URL that is not a
    PDF under the Court's orders or opinions paths.
    """
    if not is_order_document_url(url):
        raise ValueError(f"not an order or opinion PDF on supremecourt.gov: {url}")
    document = fetcher.document(url)
    return read_documents([document], day=None, covers_the_day=False)
