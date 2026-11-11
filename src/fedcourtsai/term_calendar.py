"""Read the Court's conference calendar off its published case distribution schedule.

``data/schedule/term-calendar.json`` carries every conference day the Court has
published for the current and the next October Term, with the distribution
rows behind them, read from the Court's own *Case Distribution Schedule*
(``supremecourt.gov/casedistribution/casedistributionschedule<YYYY>.pdf``).
That document prints one row per distribution list: the distribution date, the
list, and the conference the list goes to. The conference days are the
distinct conference dates; the one the summer lists go to is the Term's long
conference.

The Court's illustrated *Term Calendar* PDF also marks argument days,
non-argument sessions and holidays, but it marks them by colour alone, and the
current Term's copy is a scanned image with no text layer, so it is not read.

Three invariants:

- **Fail closed.** A served document that does not parse whole (for
  instance an unrecognised line, a title naming another Term, a conference out
  of the Term's window, a row distributed on or after its conference, a
  document over the size cap, or anything but exactly one conference taking the
  summer lists) refuses the whole refresh, and the committed file stays as
  it was. Nothing writes a calendar without sessions.
- **The Court's host only.** Fetched through the live channel's
  :class:`~fedcourtsai.supremecourt.SupremeCourtClient`, which refuses any hop
  off supremecourt.gov.
- **Not a cell input.** No provisioning step reads this file; the schedule
  export is its one reader, and a test holds the provisioning modules to that.
"""

from __future__ import annotations

import hashlib
import io
import re
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .schemas import (
    TermCalendar,
    TermCalendarDistribution,
    TermCalendarSession,
    TermCalendarSource,
)
from .serialize import read_model, write_json
from .supremecourt import october_term_year

SCHEDULE_URL = "https://www.supremecourt.gov/casedistribution/casedistributionschedule{term}.pdf"

_MONTHS = (
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
)
_MONTH = "|".join(_MONTHS)

# The text layer is read with every run of whitespace removed, because the
# extractor splits words and numbers at arbitrary points ("SE PTEMBER",
# "20 26"); with the spaces gone the grammar is unambiguous.
_ROW = re.compile(
    rf"^(?P<dm>{_MONTH})(?P<dd>\d{{1,2}}),(?P<dy>\d{{4}})"
    r"(?P<summer>SUMMER)?LIST(?P<number>\d{1,3})(?:\((?P<paper>PAID|IFP)\))?"
    rf"(?:(?P<cm>{_MONTH})(?P<cd>\d{{1,2}}),(?P<cy>\d{{4}}))?$"
)
_TITLE = re.compile(r"^CASEDISTRIBUTIONSCHEDULE[-\u2013\u2014]OCTOBERTERM(?P<term>\d{4})$")
_COLUMN_HEADER = "DISTRIBUTIONDATELISTCONFERENCE"

#: A served schedule is tens of kilobytes; anything past this is not one, and
#: is refused before the parser sees it.
MAX_DOCUMENT_BYTES = 2_000_000

#: The most the refresh may wait on the Court, across both documents, so a
#: degraded upstream cannot hold the live poll past its own budget.
FETCH_DEADLINE_SECONDS = 120.0

#: Fewer rows than this is not a whole Term's schedule: a served Term prints
#: well over a hundred.
_MIN_ROWS = 40


class CalendarRefused(ValueError):
    """A served schedule that does not parse whole; the committed calendar stands."""


class DocumentFetcher(Protocol):
    """What the refresh needs of the live channel's client."""

    def get_document(self, url: str) -> bytes | None: ...


def term_calendar_path(data_root: Path) -> Path:
    """Where the committed term calendar lives under ``data_root``."""
    return data_root / "schedule" / "term-calendar.json"


def pdf_text(data: bytes) -> str:
    """The document's text layer, page after page; refused when it is not a readable PDF."""
    try:
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except (PyPdfError, ValueError, KeyError, TypeError) as exc:
        raise CalendarRefused(f"not a readable PDF ({type(exc).__name__}: {str(exc)!r})") from exc


def _day(month: str, day: str, year: str) -> date:
    try:
        return date(int(year), _MONTHS.index(month) + 1, int(day))
    except ValueError as exc:
        raise CalendarRefused(f"not a date: {month} {day}, {year}") from exc


def _parse_row(line: str, raw: str, *, term: int) -> TermCalendarDistribution:
    """One condensed line as a distribution row of OT ``term``, or refused."""
    match = _ROW.match(line)
    if match is None:
        raise CalendarRefused(f"unrecognised line: {raw.strip()!r}")
    distributed = _day(match["dm"], match["dd"], match["dy"])
    conference = _day(match["cm"], match["cd"], match["cy"]) if match["cm"] is not None else None
    if conference is None and match["summer"] is None:
        raise CalendarRefused(f"a term list with no conference: {raw.strip()!r}")
    if conference is not None:
        if not date(term, 9, 1) <= conference <= date(term + 1, 9, 30):
            raise CalendarRefused(f"conference {conference} is outside OT{term}")
        if distributed >= conference:
            raise CalendarRefused(f"distributed {distributed} for conference {conference}")
    name = ("SUMMER " if match["summer"] else "") + f"LIST {int(match['number'])}"
    if match["paper"] is not None:
        name += f" ({match['paper']})"
    return TermCalendarDistribution(
        distributed=distributed, list_name=name, conference=conference, term=term
    )


def parse_schedule(text: str, *, term: int) -> list[TermCalendarDistribution]:
    """Every distribution row of October Term ``term``'s schedule, in print order.

    Refuses (:class:`CalendarRefused`) rather than skip: a line that is neither
    the title, a column header, a page number nor a row; a title naming another
    Term or none; too few rows; a conference outside the Term's window (the
    September before it opens through the September after); a row distributed
    on or after its conference; or anything other than exactly one conference
    taking summer lists.
    """
    rows: list[TermCalendarDistribution] = []
    titled = False
    for raw in text.splitlines():
        line = re.sub(r"\s+", "", raw).upper()
        if not line or line.isdigit() or line == _COLUMN_HEADER:
            continue
        title = _TITLE.match(line)
        if title is not None:
            if int(title["term"]) != term:
                raise CalendarRefused(f"schedule is titled OT{title['term']}, expected OT{term}")
            titled = True
            continue
        rows.append(_parse_row(line, raw, term=term))
    if not titled:
        raise CalendarRefused(f"no OT{term} title")
    if len(rows) < _MIN_ROWS:
        raise CalendarRefused(f"{len(rows)} row(s), fewer than a Term's {_MIN_ROWS}")
    long_conferences = {
        row.conference
        for row in rows
        if row.list_name.startswith("SUMMER ") and row.conference is not None
    }
    if len(long_conferences) != 1:
        raise CalendarRefused(
            f"{len(long_conferences)} conference(s) take summer lists, expected exactly one"
        )
    return rows


def _sessions(rows: list[TermCalendarDistribution]) -> list[TermCalendarSession]:
    """One conference session per distinct conference day, in day order."""
    long_days = {
        row.conference
        for row in rows
        if row.list_name.startswith("SUMMER ") and row.conference is not None
    }
    terms: dict[date, int] = {}
    for row in rows:
        if row.conference is None:
            continue
        seen = terms.setdefault(row.conference, row.term)
        if seen != row.term:
            raise CalendarRefused(
                f"conference {row.conference} printed by OT{seen} and OT{row.term}"
            )
    return [
        TermCalendarSession(
            day=day, kind="conference", term=terms[day], long_conference=day in long_days
        )
        for day in sorted(terms)
    ]


def build_calendar(
    client: DocumentFetcher,
    *,
    today: date,
    extract: Callable[[bytes], str] = pdf_text,
) -> TermCalendar:
    """The calendar the Court publishes on ``today``, or :class:`CalendarRefused`.

    Reads the schedule of the October Term ``today`` falls in, which must be
    served, and the next Term's, which may not be yet. A served document of
    either that does not parse whole refuses the build.
    """
    current = october_term_year(today)
    sources: list[TermCalendarSource] = []
    rows: list[TermCalendarDistribution] = []
    for term in (current, current + 1):
        url = SCHEDULE_URL.format(term=term)
        data = client.get_document(url)
        if data is None:
            if term == current:
                raise CalendarRefused(f"OT{term} schedule not served at {url}")
            continue
        if len(data) > MAX_DOCUMENT_BYTES:
            raise CalendarRefused(f"OT{term} schedule is {len(data)} bytes, over the cap")
        rows.extend(parse_schedule(extract(data), term=term))
        sources.append(
            TermCalendarSource(term=term, url=url, sha256=hashlib.sha256(data).hexdigest())
        )
    return TermCalendar(
        checked_on=today, sources=sources, sessions=_sessions(rows), distributions=rows
    )


def committed_calendar(data_root: Path) -> TermCalendar | None:
    """The committed calendar, or ``None`` when none is committed or it does not read."""
    path = term_calendar_path(data_root)
    if not path.exists():
        return None
    try:
        return read_model(path, TermCalendar)
    except (OSError, ValueError, ValidationError):
        return None


def next_conference(calendar: TermCalendar | None, as_of: date) -> date | None:
    """The calendar's first conference on or after ``as_of``, or ``None``."""
    if calendar is None:
        return None
    return next(
        (s.day for s in calendar.sessions if s.kind == "conference" and s.day >= as_of), None
    )


def refresh_calendar(
    client: DocumentFetcher,
    data_root: Path,
    *,
    today: date,
    force: bool = False,
    extract: Callable[[bytes], str] = pdf_text,
) -> str:
    """Re-read the calendar unless it was read today, and swap it in whole; a status line.

    A refusal leaves the committed file in place and raises
    :class:`CalendarRefused` saying which calendar stands, for the caller to
    report; a transport error propagates to be reported the same way. Written
    beside the destination and renamed over it, so a write that fails partway
    leaves the committed file as it was.
    """
    destination = term_calendar_path(data_root)
    committed = committed_calendar(data_root)
    if not force and committed is not None and committed.checked_on >= today:
        return f"term-calendar: read {committed.checked_on}; not re-read"
    try:
        built = build_calendar(client, today=today, extract=extract)
    except CalendarRefused as exc:
        kept = f"{committed.checked_on}'s calendar kept" if committed else "nothing written"
        raise CalendarRefused(f"{exc}; {kept}") from exc
    staged = destination.with_name(destination.name + ".tmp")
    try:
        write_json(staged, built)
        staged.replace(destination)
    finally:
        staged.unlink(missing_ok=True)
    terms = ", ".join(f"OT{source.term}" for source in built.sources)
    return (
        f"term-calendar: {len(built.sessions)} conference(s) from {terms}; "
        f"next {next_conference(built, today) or 'none'}"
    )
