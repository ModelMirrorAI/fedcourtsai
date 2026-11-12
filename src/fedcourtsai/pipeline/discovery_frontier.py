"""The discovery frontier check: did each numbering stream reach the Court's real frontier?

New SCOTUS dockets are found by probing serial numbers in order from a per-Term,
per-stream cursor (:func:`fedcourtsai.pipeline.live.discover_live`), and a run of
consecutive unserved numbers stamps the frontier. Nothing in that walk can tell
"the Court has assigned no further number" from "the next numbers are withheld
or not yet posted", and a docket discovery never reaches can be neither selected
nor forecast. This module asks the question from outside the walk, four ways:

- **Outside frontier.** The highest number of each stream on lists the cursor
  does not drive: the Court's newest order lists and miscellaneous orders, and
  the Granted & Noted list. A number above the cursor is a missed frontier.
- **Movement.** How many business days old the stream's newest held docket is.
- **Holes.** Serials below the cursor with no corpus row. Sequential probing
  steps over an unserved number and never returns to it; a bounded sample is
  re-probed and the ones that now serve are counted.
- **Look-ahead.** A fixed run of serials past the cursor is probed, so a short
  run of unserved numbers cannot pin the stream unnoticed.

Two halves, kept apart. :func:`run_frontier_check` is the network half: it runs
inside the live cycle at most once a UTC day, spends supremecourt.gov requests
at the live client's pacing, and stores one reading per stream
(``live_frontier_checks``). :func:`read_discovery_frontier` is the read-only
half: it sets the stored reading beside the corpus as it stands and applies the
thresholds, wherever the corpus is pulled.

Monitoring only. The check never moves a cursor and onboards nothing, and none
of its counts is a scored figure.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

import httpx

from .. import corpus
from ..config import FrontierCheckConfig
from ..schemas import DiscoveryFrontier, DiscoveryFrontierStream
from ..supremecourt import (
    IFP_SERIAL_BASE,
    SupremeCourtClient,
    parse_scotus_application_number,
    parse_scotus_docket_number,
    scotus_docket_slug,
)
from . import granted_noted, order_lineups
from .documents import extract_pdf_text
from .opinion_lineups import OpinionFetcher

StreamName = Literal["paid", "ifp", "application"]
Form = Literal["cert", "application"]

# The forward poller's numbering streams as (name, first serial, docket form),
# in the order discovery walks them (`live.STREAMS`, which a test holds equal).
STREAMS: tuple[tuple[StreamName, int, Form], ...] = (
    ("paid", 1, "cert"),
    ("ifp", IFP_SERIAL_BASE, "cert"),
    ("application", 1, "application"),
)

# The summer recess, for the movement threshold: filings arrive more slowly and
# the Clerk dockets them in batches.
_RECESS_MONTHS = frozenset({7, 8, 9})

# The whole reading's request budget, for the client it runs on. A normal
# reading is about 70 paced requests; one against a degraded upstream is cut off
# here, and sooner where the cycle's own soft budget has less left.
READING_DEADLINE_SECONDS = 300.0

# How many of a stream's newest held serials are read for a filing date; a row
# just onboarded may not carry one yet.
_NEWEST_ROWS = 25


def stream_serial(number: str) -> tuple[int, StreamName, int] | None:
    """A docket number as ``(term, stream, serial)``, or ``None`` if it is neither form.

    ``"26-618"`` is ``(26, "paid", 618)``, ``"26-6135"`` the IFP stream (serials
    from 5001), ``"26A669"`` the application stream. Motion (``26M30``) and
    original (``159, Orig.``) numbers belong to no stream the cursor walks.
    """
    normalized = corpus.normalize_docket_number(number)
    if normalized is None:
        return None
    cert = parse_scotus_docket_number(normalized)
    if cert is not None:
        term, serial = cert
        return term, ("ifp" if serial >= IFP_SERIAL_BASE else "paid"), serial
    application = parse_scotus_application_number(normalized)
    if application is not None:
        return application[0], "application", application[1]
    return None


def _form(stream: StreamName) -> Form:
    return "application" if stream == "application" else "cert"


def _slug(term: int, stream: StreamName, serial: int) -> str:
    return scotus_docket_slug(term, serial, form=_form(stream))


def held_serials(conn: corpus.ReadConnection, term: int) -> dict[StreamName, dict[int, str]]:
    """Every serial of ``term`` the corpus holds, by stream, with its case id.

    Looked up by docket number, not by reserved id: a docket CourtListener
    indexed first is enriched under its CourtListener id.
    """
    held: dict[StreamName, dict[int, str]] = {name: {} for name, _, _ in STREAMS}
    for prefix in (f"{term:02d}-", f"{term:02d}A"):
        for number, case_id in corpus.scotus_case_ids_by_docket_number_prefix(conn, prefix).items():
            parsed = stream_serial(number)
            if parsed is not None and parsed[0] == term:
                held[parsed[1]][parsed[2]] = case_id
    return held


def stream_holes(held: Iterable[int], base: int, cursor: int | None) -> list[int]:
    """Serials from ``base`` through ``cursor`` that no corpus row holds, ascending."""
    if cursor is None:
        return []
    return sorted(set(range(base, cursor + 1)) - set(held))


def hole_sample(holes: Sequence[int], size: int, today: date) -> list[int]:
    """``size`` holes to re-probe today, rotating through all of them by day.

    A window over the ascending holes that advances ``size`` places a day and
    wraps, so every hole is re-probed within ``len(holes) / size`` days and the
    choice is a function of the date alone.
    """
    if size <= 0 or not holes:
        return []
    if len(holes) <= size:
        return list(holes)
    start = (today.toordinal() * size) % len(holes)
    return [holes[(start + offset) % len(holes)] for offset in range(size)]


def unreachable_hits(
    cursor: int, probed: Sequence[int], served: Iterable[int], frontier_misses: int
) -> list[int]:
    """The served serials sequential discovery cannot reach from ``cursor``.

    Replays the walk over the probe's own answers: it advances over a served
    number, and stops at ``frontier_misses`` consecutive unserved ones. A
    served number before that stop is ordinary new intake the next cycle
    onboards; one past it is pinned behind the unserved run.
    """
    serving = set(served)
    pinned: list[int] = []
    misses = 0
    stopped = False
    for serial in sorted(s for s in probed if s > cursor):
        if stopped:
            if serial in serving:
                pinned.append(serial)
        elif serial in serving:
            misses = 0
        else:
            misses += 1
            stopped = misses >= frontier_misses
    return pinned


def quiet_business_days(newest: date, today: date) -> int:
    """Weekdays strictly after ``newest`` and strictly before ``today``.

    ``today`` is left out because its own filings may not be posted yet. Court
    holidays are not modelled: one counts as a quiet day, which is why the
    thresholds are measured in several days.
    """
    day = newest + timedelta(days=1)
    quiet = 0
    while day < today:
        quiet += day.weekday() < 5
        day += timedelta(days=1)
    return quiet


def stall_threshold(stream: StreamName, today: date, config: FrontierCheckConfig) -> int:
    """Quiet business days at which ``stream`` alarms on ``today``."""
    if today.month in _RECESS_MONTHS:
        return config.recess_stall_business_days
    return config.ifp_stall_business_days if stream == "ifp" else config.stall_business_days


# --- The network half --------------------------------------------------------


@dataclass
class OutsideFrontier:
    """The highest serial per stream the Court's lists name, and what was unreadable."""

    highest: dict[StreamName, tuple[int, str]] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def note(self, numbers: Iterable[str], term: int, source: str) -> None:
        """Fold one list's docket numbers in, keeping each stream's highest of ``term``."""
        for number in numbers:
            parsed = stream_serial(number)
            if parsed is None or parsed[0] != term:
                continue
            _, stream, serial = parsed
            if stream not in self.highest or serial > self.highest[stream][0]:
                self.highest[stream] = (serial, source)


def read_outside_frontier(
    client: SupremeCourtClient, term: int, *, today: date, documents: int
) -> OutsideFrontier:
    """Read the Court's newest order documents and the Granted & Noted list for ``term``'s numbers.

    The order listings are those of the October Term ``today`` falls in (and, in
    October, the outgoing one), which is where the Court posts the orders that
    name a docket Term's numbers. A listing or a document that cannot be read is
    recorded as a problem and the rest are still read: a partial outside
    frontier is a lower bound, never a false alarm.
    """
    outside = OutsideFrontier()
    if documents <= 0:
        return outside
    fetcher = order_lineups.OrderFetcher(client)
    refs: dict[str, order_lineups.OrderDocumentRef] = {}
    for listing_term in order_lineups.listing_terms(today):
        try:
            page = client.get_document(order_lineups.orders_listing_url(listing_term))
        except httpx.HTTPError as exc:
            outside.problems.append(
                f"OT{listing_term:02d} order listing not read: {type(exc).__name__}"
            )
            continue
        if page is None:
            outside.problems.append(f"OT{listing_term:02d} order listing not read: not served")
            continue
        for ref in order_lineups.parse_orders_listing(page.decode("utf-8", errors="replace")):
            refs.setdefault(ref.url, ref)
    newest = sorted(refs.values(), key=lambda ref: (ref.day, ref.url), reverse=True)[:documents]
    for ref in newest:
        fetched = fetcher.document(ref.url, ref)
        if fetched.text is None:
            # The reason's head only: its tail is upstream's own error text,
            # and a problem line is published.
            reason = (fetched.reason or "no text").split(":", 1)[0]
            outside.problems.append(f"{ref.kind} {ref.day.isoformat()} not read: {reason}")
            continue
        try:
            reading = order_lineups.read_documents([fetched], day=ref.day, covers_the_day=False)
        except Exception as exc:  # one unparsed document must not cost the reading
            outside.problems.append(
                f"{ref.kind} {ref.day.isoformat()} not parsed: {type(exc).__name__}"
            )
            continue
        named = [docket for document in reading.documents for docket in document.dockets]
        outside.note(named, term, f"{ref.kind} {ref.day.isoformat()}")
    opinions = OpinionFetcher(client)
    for listing_term in order_lineups.listing_terms(today):
        try:
            data = opinions.opinion(granted_noted.GRANTED_NOTED_URL.format(term=listing_term))
        except httpx.HTTPError as exc:
            outside.problems.append(
                f"OT{listing_term:02d} granted-noted list not read: {type(exc).__name__}"
            )
            continue
        if data is None:
            # Not published until the Term's first grant: nothing to read, no problem.
            continue
        try:
            text = extract_pdf_text(data, char_cap=granted_noted.TEXT_CHAR_CAP).text
            entries = granted_noted.parse_granted_noted(text)
        except Exception as exc:  # as above: recorded, and the reading goes on
            outside.problems.append(
                f"OT{listing_term:02d} granted-noted list not parsed: {type(exc).__name__}"
            )
            continue
        outside.note(
            (docket for entry in entries for docket in entry.dockets),
            term,
            f"granted-noted list OT{listing_term:02d}",
        )
    return outside


def _probe(
    client: SupremeCourtClient, term: int, stream: StreamName, serials: Sequence[int]
) -> tuple[list[int], list[int], str | None]:
    """Probe ``serials`` in order: ``(probed, served, problem)``, stopping at an upstream error."""
    probed: list[int] = []
    served: list[int] = []
    for serial in serials:
        try:
            payload = client.get_docket(term, serial, form=_form(stream))
        except httpx.HTTPError as exc:
            return probed, served, f"{_slug(term, stream, serial)}: {type(exc).__name__}"
        probed.append(serial)
        if payload is not None:
            served.append(serial)
    return probed, served, None


def run_frontier_check(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    term: int,
    config: FrontierCheckConfig,
    *,
    frontier_misses: int,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> dict[str, object]:
    """Take today's frontier reading for every stream that has none, and store it.

    Runs after the live cycle's own work. No stream is started once the soft
    budget is spent, and the caller's client carries the request deadline that
    stops one mid-stream (``DeadlineExceeded``, raised through): either way the
    stream keeps yesterday's reading and is due again next cycle,
    so the check costs its requests once a UTC day however often the cycle
    runs. A stream with no cursor has served nothing and is not read. Returns
    the pass's ledger for the run log; empty when the check is off.
    """
    if not config.enabled:
        return {}
    with corpus.connect(corpus_db_path) as conn:
        cursors = {
            stream: corpus.get_live_cursor(conn, term, stream) for stream, _base, _form in STREAMS
        }
        stored = corpus.live_frontier_checks(conn, term)
        due = [
            (stream, base)
            for stream, base, _form in STREAMS
            if cursors[stream] is not None
            and (stream not in stored or stored[stream].checked_on < today)
        ]
        held = held_serials(conn, term) if due else {}
    if not due:
        return {"due": 0}

    def expired() -> bool:
        return deadline is not None and time_fn() >= deadline

    if expired():
        return {"due": len(due), "checked": 0, "deferred": len(due)}
    outside = read_outside_frontier(client, term, today=today, documents=config.outside_documents)
    checked = 0
    outside_ahead = 0
    pinned_total = 0
    serving_total = 0
    deferred = 0
    for stream, base in due:
        if expired():
            deferred += 1
            continue
        cursor = cursors[stream]
        assert cursor is not None  # a due stream has a cursor
        problems = list(outside.problems)
        ahead = range(cursor + 1, cursor + 1 + config.lookahead)
        probed, served, problem = _probe(client, term, stream, ahead)
        if problem is not None:
            problems.append(f"look-ahead stopped at {problem}")
        pinned = unreachable_hits(cursor, probed, served, frontier_misses)
        holes = stream_holes(held[stream], base, cursor)
        sample = hole_sample(holes, config.hole_reprobes_per_stream, today)
        reprobed, now_serving, problem = _probe(client, term, stream, sample)
        if problem is not None:
            problems.append(f"hole re-probe stopped at {problem}")
        prior = stored.get(stream)
        # Carried while still a hole, unless today's own re-probe found it unserved.
        carried = set(prior.holes_serving) & set(holes) if prior is not None else set()
        serving = sorted((carried - set(reprobed)) | set(now_serving))
        named = outside.highest.get(stream)
        with corpus.connect(corpus_db_path) as conn:
            corpus.set_live_frontier_check(
                conn,
                corpus.FrontierCheck(
                    term=term,
                    stream=stream,
                    checked_on=today,
                    cursor_serial=cursor,
                    outside_serial=named[0] if named is not None else None,
                    outside_source=named[1] if named is not None else None,
                    lookahead_probed=len(probed),
                    lookahead_hits=tuple(pinned),
                    holes_reprobed=len(reprobed),
                    holes_serving=tuple(serving),
                    problems=tuple(problems),
                ),
            )
        checked += 1
        outside_ahead += int(named is not None and named[0] > cursor)
        pinned_total += len(pinned)
        serving_total += len(serving)
    return {
        "due": len(due),
        "checked": checked,
        "outside_ahead": outside_ahead,
        "lookahead_hits": pinned_total,
        "holes_serving": serving_total,
        "deferred": deferred,
        "unread": len(outside.problems),
    }


# --- The read-only half ------------------------------------------------------


def _newest_filed(
    conn: corpus.ReadConnection, held: dict[int, str], cursor: int | None
) -> date | None:
    """The latest filing date among the stream's newest held serials."""
    newest = [held[serial] for serial in sorted(held, reverse=True)[:_NEWEST_ROWS]]
    if cursor is None or not newest:
        return None
    marks = ",".join("?" for _ in newest)
    row = conn.execute(
        f"SELECT MAX(date_filed) AS newest FROM cases WHERE case_id IN ({marks})", newest
    ).fetchone()
    return date.fromisoformat(row["newest"]) if row is not None and row["newest"] else None


def _stream_alarms(
    row: DiscoveryFrontierStream, term: int, *, today: date, config: FrontierCheckConfig
) -> list[str]:
    def numbers(serials: Sequence[int]) -> str:
        return ", ".join(_slug(term, row.stream, serial) for serial in serials)

    alarms: list[str] = []
    if row.cursor is None:
        return alarms
    if row.outside_serial is not None and row.outside_serial > row.cursor:
        alarms.append(
            f"{row.outside_source} names {_slug(term, row.stream, row.outside_serial)}, "
            f"above the cursor at {_slug(term, row.stream, row.cursor)}"
        )
    if row.quiet_business_days is not None and row.quiet_business_days >= row.stall_threshold:
        alarms.append(
            f"no docket newer than {row.newest_filed} for {row.quiet_business_days} "
            f"business day(s) (alarm at {row.stall_threshold})"
        )
    if row.lookahead_hits:
        alarms.append(
            f"{numbers(row.lookahead_hits)} served past an unserved run the sequential "
            "probe stops at"
        )
    if len(row.holes_serving) > config.hole_alarm_over:
        alarms.append(
            f"{len(row.holes_serving)} skipped number(s) now serve and are not in the corpus "
            f"(alarm over {config.hole_alarm_over}): {numbers(row.holes_serving)}"
        )
    if row.checked_on is not None and (today - row.checked_on).days > config.stale_check_days:
        alarms.append(
            f"the frontier reading is from {row.checked_on}, more than "
            f"{config.stale_check_days} day(s) old"
        )
    return alarms


def read_discovery_frontier(
    conn: corpus.ReadConnection, term: int, *, today: date, config: FrontierCheckConfig
) -> DiscoveryFrontier:
    """Each stream's cursor, holes and stored reading, with the thresholds applied.

    Read-only. The stored reading is set against the corpus as it stands now,
    not as it stood when the reading was taken: an outside number or a
    look-ahead hit the cursor has since passed, and a hole a row now holds, no
    longer count, so an alarm clears as soon as the corpus catches up.
    """
    cursor_rows = {
        (row_term, stream): (last, frontier)
        for row_term, stream, last, frontier in corpus.live_cursor_rows(conn)
    }
    stored = corpus.live_frontier_checks(conn, term)
    held = held_serials(conn, term)
    streams: list[DiscoveryFrontierStream] = []
    for stream, base, _form in STREAMS:
        cursor, frontier = cursor_rows.get((term, stream), (None, None))
        holes = stream_holes(held[stream], base, cursor)
        newest = _newest_filed(conn, held[stream], cursor)
        check = stored.get(stream)
        row = DiscoveryFrontierStream(
            stream=stream,
            cursor=cursor,
            frontier=frontier,
            newest_filed=newest,
            quiet_business_days=quiet_business_days(newest, today) if newest else None,
            stall_threshold=stall_threshold(stream, today, config),
            holes=len(holes),
        )
        if check is not None and cursor is not None:
            row = row.model_copy(
                update={
                    "checked_on": check.checked_on,
                    "outside_serial": check.outside_serial,
                    "outside_source": check.outside_source,
                    "lookahead_hits": [s for s in check.lookahead_hits if s > cursor],
                    "holes_reprobed": check.holes_reprobed,
                    "holes_serving": sorted(set(check.holes_serving) & set(holes)),
                    "problems": list(check.problems),
                }
            )
        streams.append(
            row.model_copy(update={"alarms": _stream_alarms(row, term, today=today, config=config)})
        )
    return DiscoveryFrontier(term=term, ok=not any(row.alarms for row in streams), streams=streams)


# --- Rendering ---------------------------------------------------------------


def stream_line(term: int, row: DiscoveryFrontierStream) -> str:
    """One stream's report line: cursor, frontier stamp, outside frontier, holes, movement."""
    if row.cursor is None:
        return f"- **{row.stream}**: no cursor yet (nothing served this Term)"
    stamp = (
        "frontier stamped there"
        if row.frontier == row.cursor
        else f"frontier stamp {_slug(term, row.stream, row.frontier)}"
        if row.frontier is not None
        else "no frontier stamp"
    )
    movement = (
        f"newest docket {row.newest_filed} ({row.quiet_business_days} quiet business day(s))"
        if row.newest_filed is not None
        else "no filing date held"
    )
    head = f"- **{row.stream}**: cursor {_slug(term, row.stream, row.cursor)}, {stamp}"
    if row.checked_on is None:
        return f"{head} · {row.holes} hole(s) · {movement} · never probed"
    outside = (
        f"lists name up to {_slug(term, row.stream, row.outside_serial)} ({row.outside_source})"
        if row.outside_serial is not None
        else "no number on the lists read"
    )
    holes = f"{row.holes} hole(s), {len(row.holes_serving)} now serving"
    return f"{head} · {outside} · {holes} · {movement} · probed {row.checked_on}"


def render_lines(discovery: DiscoveryFrontier) -> list[str]:
    """The ops report's block: one line per stream, each alarm beneath its stream."""
    unprobed = any(row.cursor is not None and row.checked_on is None for row in discovery.streams)
    verdict = "**behind**" if not discovery.ok else "not yet probed" if unprobed else "no alarm"
    lines = [f"**Discovery frontier** (OT{discovery.term:02d}): {verdict}"]
    for row in discovery.streams:
        lines.append(stream_line(discovery.term, row))
        lines += [f"  - ⚠️ {alarm}" for alarm in row.alarms]
    return lines


def render_block(discovery: DiscoveryFrontier | None) -> list[str]:
    """:func:`render_lines` set off by a blank line, or nothing when the check is off."""
    return ["", *render_lines(discovery)] if discovery is not None else []


def render_alarm(discovery: DiscoveryFrontier) -> str:
    """The latched issue's body: what tripped, the standing of every stream, what to do."""
    lines = [
        "The discovery frontier check found a numbering stream that may not have reached "
        + "the Court's real frontier. A docket discovery never reaches is never selected or "
        + "forecast, and no later check names it.",
        "",
        *render_lines(discovery),
    ]
    unread = sorted({problem for row in discovery.streams for problem in row.problems})
    if unread:
        lines += ["", "Not read in the stored reading:", *(f"- {problem}" for problem in unread)]
    lines += [
        "",
        "This issue is refreshed by each ops run while an alarm stands and closes itself "
        + "when the check is clean. See *The discovery frontier check* in "
        + "`docs/live-sources.md` for what each alarm means and how it clears.",
    ]
    return "\n".join(lines) + "\n"
