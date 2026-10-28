"""Read the Court's legacy HTML docket page into the docket JSON's own keys.

supremecourt.gov serves its docket JSON from the e-filing era on: of OT2016's
applications, mostly those from ``16A1051`` (docketed 2017-04-28). Most of the
rest are still served, as the legacy HTML page at
:data:`~fedcourtsai.supremecourt.LEGACY_DOCKET_URL` — the same Clerk's record in
an older layout: the number, the caption, the docketed date, the court below and
its case numbers, a linked-case line, the dated proceedings, and the counsel
blocks under their party headers.

:func:`parse_legacy_docket` reads that page into a mapping keyed exactly as the
JSON keys those fields, so everything downstream — the live mapping, ingest-time
resolution, event minting, the contact scrubs — reads a legacy record through
the same code as a served JSON one, and nothing here maps a field. It carries
only what the page carries: no ``bCapitalCase`` (the page has no capital
marker, so ``capital_case`` falls to the docket-number annotation, which these
pages also lack), no ``RelatedCaseNumber``, no ``LowerCourtDecision``, no
document links, and no ``sJson*`` stamps. A counsel block keeps the attorney,
the counsel-of-record marker and the party name, which are what the live
mapping reads of one. The page's address and phone columns, which run a title,
an office, a street and a prisoner register number together without labels,
are not read at all: the stored record carries no contact detail for a scrub
to withhold.

The mapping is not the Court's JSON and never passes as it:
:data:`LEGACY_SOURCE_KEY` names the page it was read from and the SHA-256 of
the page with its script elements removed, so a stored snapshot says what it
is and a re-read of the page can be checked against it. The scripts are left
out of the digest because the served page embeds a measurement beacon whose
values change on every request; nothing the parse reads is in them.

A leaf module over the standard library's HTML tokenizer: the page is tables
of rows of cells, read in document order.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Final

#: The key a legacy record carries in place of the JSON's own stamps: where the
#: page was read and the digest of the text parsed.
LEGACY_SOURCE_KEY: Final = "LegacyDocketSource"

#: The ``format`` value under :data:`LEGACY_SOURCE_KEY`.
LEGACY_FORMAT: Final = "supremecourt-docketfiles-htm"

_NUMBER = re.compile(r"^No\.\s+(\S+)$")
_PARTY_NAME = re.compile(r"^Party name:\s*(.*)$")
_HEADER = re.compile(r"^(Attorneys? for .+?|Other):?$")
_COUNSEL_OF_RECORD = "Counsel of Record"


@dataclass
class _Row:
    depth: int
    cells: list[list[str]] = field(default_factory=list)


class _Rows(HTMLParser):
    """Every table row's cell texts, in the order the rows open.

    The pages nest a caption table inside a row and close their tags loosely,
    so a row ends at its own ``</tr>``, at the next ``<tr>`` of the same table,
    or at the end of its table, whichever comes first. Text outside any cell
    is dropped.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[_Row] = []
        self._open: list[_Row] = []
        self._depth = 0
        self._skip = 0

    def _close_to(self, depth: int) -> None:
        while self._open and self._open[-1].depth >= depth:
            self._open.pop()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "table":
            self._depth += 1
        elif tag == "tr":
            self._close_to(self._depth)
            row = _Row(self._depth)
            self.rows.append(row)
            self._open.append(row)
        elif tag == "td" and self._open and self._open[-1].depth == self._depth:
            self._open[-1].cells.append([])
        elif tag == "br":
            self.handle_data(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag == "table":
            self._close_to(self._depth)
            self._depth = max(0, self._depth - 1)
        elif tag == "tr" and self._open and self._open[-1].depth == self._depth:
            self._open.pop()

    def handle_data(self, data: str) -> None:
        if self._skip or not self._open:
            return
        row = self._open[-1]
        if row.depth == self._depth and row.cells:
            row.cells[-1].append(data)


def _text(parts: list[str]) -> str:
    return " ".join("".join(parts).replace("\xa0", " ").split())


def _table_rows(page: str) -> list[list[str]]:
    reader = _Rows()
    reader.feed(page)
    reader.close()
    return [[_text(cell) for cell in row.cells] for row in reader.rows if row.cells]


def _caption(lines: list[str]) -> tuple[str, str]:
    """The applicant and respondent titles, split at the caption's ``v.`` line."""
    if "v." in lines:
        at = lines.index("v.")
        return " ".join(lines[:at]), " ".join(lines[at + 1 :])
    return " ".join(lines), ""


def _counsel(rows: list[list[str]]) -> dict[str, Any]:
    """The counsel blocks under each party header, keyed as the JSON keys them."""
    out: dict[str, Any] = {}
    side: str | None = None
    pending: list[dict[str, Any]] = []
    for cells in rows:
        first, rest = (cells[0], cells[1:]) if cells else ("", [])
        if (header := _HEADER.match(first)) is not None and not any(rest):
            label = header.group(1)
            side = (
                "Petitioner"
                if "Petitioner" in label
                else "Respondent"
                if "Respondent" in label
                else "Other"
            )
            out[f"AttorneyHeader{side}"] = label
            out.setdefault(side, [])
            pending = []
            continue
        if side is None:
            continue
        if (party := _PARTY_NAME.match(first)) is not None:
            for block in pending:
                block["PartyName"] = party.group(1).strip()
            pending = []
            continue
        if first == _COUNSEL_OF_RECORD:
            if pending:
                pending[-1]["IsCounselofRecord"] = True
        elif first:
            attorney: dict[str, Any] = {"Attorney": first, "IsCounselofRecord": False}
            out[side].append(attorney)
            pending.append(attorney)
    return out


_LABELS: Final = {
    "Docketed:": "DocketedDate",
    "Lower Ct:": "LowerCourt",
    "Case Nos.:": "LowerCourtCaseNumbers",
}


@dataclass
class _Head:
    """The page's head and proceedings, read row by row."""

    number: str | None = None
    caption: list[str] | None = None
    fields: dict[str, str] = field(default_factory=dict)
    proceedings: list[dict[str, str]] | None = None

    def close_caption(self) -> None:
        if self.caption is not None:
            self.fields["PetitionerTitle"], self.fields["RespondentTitle"] = _caption(self.caption)
            self.caption = None

    def read(self, cells: list[str]) -> None:
        first = cells[0]
        if self.proceedings is not None:
            if len(cells) >= 2 and first:
                self.proceedings.append({"Date": first, "Text": cells[1]})
        elif first.startswith("~~~Date~~~"):
            self.proceedings = []
        elif self.number is None and (match := _NUMBER.match(first)) is not None:
            self.number = match.group(1)
        elif first == "Title:":
            self.caption = []
        elif (label := _LABELS.get(first)) is not None:
            self.close_caption()
            self.fields[label] = cells[1] if len(cells) > 1 else ""
        elif first.startswith("Linked with"):
            self.fields["Links"] = first
        elif self.caption is not None and len(cells) == 1 and first:
            self.caption.append(first)


#: A script element, start tag to end tag. The end tag admits anything up to its
#: ``>``, as a browser's tokenizer does, so no variant leaves script text behind.
_SCRIPT = re.compile(r"<script\b[^>]*>.*?</script\b[^>]*>", re.IGNORECASE | re.DOTALL)


def page_digest(page: str) -> str:
    """``page``'s SHA-256 without its script elements, as recorded under the source key."""
    return hashlib.sha256(_SCRIPT.sub("", page).encode("utf-8")).hexdigest()


def parse_legacy_docket(page: str, *, url: str) -> dict[str, Any] | None:
    """The page read into the docket JSON's keys, or ``None`` when it is not a docket page.

    A docket page carries its ``No.`` line and its proceedings header; a page
    lacking either is not one, whatever it served. ``url`` is where the page
    was read, recorded under :data:`LEGACY_SOURCE_KEY` beside the digest of
    ``page``.
    """
    rows = _table_rows(page)
    head = _Head()
    counsel: list[list[str]] = []
    for index, cells in enumerate(rows):
        if cells[0].startswith("~~Name~~"):
            counsel = rows[index + 1 :]
            break
        head.read(cells)
    if head.number is None or head.proceedings is None:
        return None
    head.close_caption()
    record: dict[str, Any] = {
        "CaseNumber": head.number,
        **head.fields,
        "ProceedingsandOrder": head.proceedings,
    }
    record.update(_counsel(counsel))
    record[LEGACY_SOURCE_KEY] = {
        "format": LEGACY_FORMAT,
        "url": url,
        "sha256": page_digest(page),
    }
    return record
