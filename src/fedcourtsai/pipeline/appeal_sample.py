"""A sample of civil appeals read by the appeal stage's disposition reader.

The appeal stage (``docs/appeal-stage.md``) does not register until its
reader's triage rate has been measured on appeals already decided, and the AI
watchlist holds too few of those. This module measures the reader
(:mod:`~fedcourtsai.pipeline.appeal_resolver`) on a fixed draw of civil
appeals from CourtListener instead: one circuit a run, a seeded random order
over the dockets filed in a closed window old enough that most have ended.

**The draw.** A docket search over one court of appeals, the dockets filed
from :data:`FILED_AFTER` to :data:`FILED_BEFORE`, in upstream's random order
under :data:`SEED`, so every run of one court walks the same sequence. Each
result is read once for its case type; an appeal whose type does not begin
"civil" (a criminal appeal, an agency petition, an original proceeding, a
bankruptcy appeal) is counted and passed over, and so is one with no type
recorded. The first :data:`TAKE` civil appeals are the court's sample.

**The reading.** Each sampled docket's entries are read whole, up to
:data:`MAX_ENTRY_PAGES` pages; a longer docket is counted too long and not
read, never read in part. The reader then says what it says of any docket: a
disposition, an entry for triage, or nothing. An appeal upstream marks
terminated on which the reader read nothing is counted apart, because that is
where a disposition the rule did not see would be.

**What it measures.** How often the reader settles a disposition, how often
it hands one to triage, and how often it is silent on an ended appeal. It does
not measure whether a disposition it read is the right one: that takes a hand
check of the rows, which the report names by docket and entry number.

**What the report carries.** Court-record identifiers, counts and the
reader's own fixed reason strings: court, docket id and number, entry numbers
and dates. No caption, party, case type or entry text. Nothing here writes
the corpus, the ledger or ``data/``, and no reading is a scored figure.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any, Final, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled
from . import appeal_resolver
from .appeal_resolver import APPEAL_RULE, Disposition, Unresolved

#: The courts of appeals sampled, one a run.
SAMPLE_COURTS: Final = ("ca2", "ca3", "ca9", "cadc")
#: The filing window drawn from, both days included: old enough that most
#: appeals in it have ended.
FILED_AFTER: Final = date(2024, 7, 1)
FILED_BEFORE: Final = date(2025, 6, 30)
#: The seed of upstream's random order, so a court's draw repeats.
SEED: Final = 20261112
#: Civil appeals sampled per court.
TAKE: Final = 25
#: Requests one run may spend: the ``appeal-sample`` lane's share.
MAX_REQUESTS: Final = 150
#: Entry pages read per docket; a longer docket is not read.
MAX_ENTRY_PAGES: Final = 6

Reading = Literal["resolved", "triage", "open", "too-long"]


class SampleRow(BaseModel):
    """One sampled appeal and what the reader said of it."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    docket_number: str
    #: Upstream records a termination date for the appeal.
    terminated: bool
    entries: int
    reading: Reading
    outcome: str | None = None
    #: The entry the disposition was read from, or the entries sent to triage.
    entry_numbers: list[int] = Field(default_factory=list)
    reason: str | None = None
    #: The appellant's reply brief was read, so the event would have opened.
    reply_read: bool = False


class SampleReport(BaseModel):
    """One court's sample: the draw, the spend and every row read."""

    model_config = ConfigDict(extra="forbid")

    generated_at: str
    rule: str = APPEAL_RULE
    court: str
    filed_after: str
    filed_before: str
    seed: int
    take: int
    max_requests: int
    max_entry_pages: int
    requests: int = 0
    #: Search results walked, whatever became of them.
    candidates: int = 0
    not_civil: int = 0
    no_case_type: int = 0
    rows: list[SampleRow] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    #: Why the run ended before its sample was full; None when it filled it or
    #: the draw ran out.
    stopped: str | None = None
    #: The search had no more dockets to give.
    exhausted: bool = False

    def counts(self) -> dict[str, int]:
        found = Counter(row.reading for row in self.rows)
        return {
            "sampled": len(self.rows),
            "resolved": found["resolved"],
            "triage": found["triage"],
            "open": found["open"],
            "open_terminated": sum(row.reading == "open" and row.terminated for row in self.rows),
            "too_long": found["too-long"],
        }


class _RunCapReached(Exception):
    """The next request would pass the run's request cap."""


def _stop_reason(exc: Exception) -> str | None:
    if isinstance(exc, _RunCapReached):
        return str(exc)
    if isinstance(exc, RateBudgetExceeded):
        return f"API budget exhausted ({exc})"
    if is_throttled(exc):
        return f"CourtListener throttling persisted ({exc})"
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 401:
        return "CourtListener refused the credential (HTTP 401)"
    return None


def search_params(court: str) -> dict[str, str]:
    """The docket search one court's draw sends."""
    return {
        "type": "d",
        "court": court,
        "filed_after": FILED_AFTER.isoformat(),
        "filed_before": FILED_BEFORE.isoformat(),
        "order_by": f"random_{SEED} desc",
    }


def is_civil(case_type: Any) -> bool | None:
    """Whether upstream's appellate case type names a civil appeal; None when it names none."""
    if not isinstance(case_type, str) or not case_type.strip():
        return None
    return case_type.strip().lower().startswith("civil")


def _docket_id(result: Any) -> int | None:
    value = result.get("docket_id") if isinstance(result, Mapping) else None
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _read(
    client: CourtListenerClient, report: SampleReport, docket_id: int, *, today: date
) -> SampleRow | None:
    """Read one drawn docket; None when it is not a civil appeal."""

    def spend() -> None:
        if report.requests >= report.max_requests:
            raise _RunCapReached(f"run cap of {report.max_requests} requests reached")
        report.requests += 1

    spend()
    docket = client.get_docket(docket_id)
    civil = is_civil(docket.get("appellate_case_type_information"))
    if civil is None:
        report.no_case_type += 1
        return None
    if not civil:
        report.not_civil += 1
        return None
    read = client.docket_entries(docket_id, max_pages=report.max_entry_pages, on_request=spend)
    row = SampleRow(
        docket_id=docket_id,
        docket_number=str(docket.get("docket_number") or ""),
        terminated=bool(docket.get("date_terminated")),
        entries=len(read.entries),
        reading="too-long",
    )
    if not read.complete:
        return row
    opening = appeal_resolver.read_appeal(read.entries, today=today)
    row.reply_read = opening.reply is not None
    resolution = opening.resolution
    if isinstance(resolution, Disposition):
        row.reading = "resolved"
        row.outcome = resolution.outcome.value
        if resolution.cited.entry_number is not None:
            row.entry_numbers = [resolution.cited.entry_number]
    elif isinstance(resolution, Unresolved):
        row.reading = "triage"
        row.reason = resolution.reason
        row.entry_numbers = [
            cited.entry_number for cited in resolution.candidates if cited.entry_number is not None
        ]
    else:
        row.reading = "open"
    return row


def sample(
    client: CourtListenerClient,
    court: str,
    *,
    take: int = TAKE,
    max_requests: int = MAX_REQUESTS,
    now: datetime | None = None,
) -> SampleReport:
    """Draw one court's civil appeals and read each with the appeal reader.

    A wall (the run cap, the rate budget, persistent throttling, a refused
    credential) stops the run with the rows read before it kept; a docket in
    the middle of its read when the wall came is not counted. A docket whose
    read fails otherwise is recorded and passed over.
    """
    if court not in SAMPLE_COURTS:
        raise ValueError(f"{court!r} is not a sampled court ({', '.join(SAMPLE_COURTS)})")
    moment = now or datetime.now(UTC)
    report = SampleReport(
        generated_at=moment.isoformat(timespec="seconds"),
        court=court,
        filed_after=FILED_AFTER.isoformat(),
        filed_before=FILED_BEFORE.isoformat(),
        seed=SEED,
        take=take,
        max_requests=max_requests,
        max_entry_pages=MAX_ENTRY_PAGES,
    )
    seen: set[int] = set()
    next_url: str | None = None
    first = True
    try:
        while len(report.rows) < take:
            if not first and next_url is None:
                report.exhausted = True
                break
            if report.requests >= max_requests:
                raise _RunCapReached(f"run cap of {max_requests} requests reached")
            report.requests += 1
            page = client.search(search_params(court)) if first else client.search_next(next_url)  # type: ignore[arg-type]
            first = False
            results = page.get("results")
            if not isinstance(results, list):
                raise ValueError("search page carries no results list")
            found = page.get("next")
            next_url = found if isinstance(found, str) and found else None
            for result in results:
                if len(report.rows) >= take:
                    break
                docket_id = _docket_id(result)
                if docket_id is None or docket_id in seen:
                    continue
                seen.add(docket_id)
                report.candidates += 1
                try:
                    row = _read(client, report, docket_id, today=moment.date())
                except (RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
                    if _stop_reason(exc) is not None:
                        raise
                    report.errors.append(f"docket {docket_id}: {type(exc).__name__}: {exc}")
                    continue
                if row is not None:
                    report.rows.append(row)
    except (_RunCapReached, RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
        report.stopped = _stop_reason(exc) or f"the search failed ({type(exc).__name__}: {exc})"
    return report


def failure(report: SampleReport) -> str | None:
    """Why the run should fail its job though its report stands; None when it should not."""
    if report.stopped is not None and (not report.rows or "HTTP 401" in report.stopped):
        return report.stopped
    return None


def plan_lines(court: str, *, take: int, max_requests: int) -> list[str]:
    """What a run would ask, sending no request."""
    params = " ".join(f"{key}={value}" for key, value in search_params(court).items())
    return [
        f"appeal-sample {court}: the first {take} civil appeals of the search {params}",
        f"  one request a search page and a drawn docket, up to {MAX_ENTRY_PAGES} entry pages "
        + f"a civil appeal, at most {max_requests} requests",
    ]


def summary_lines(report: SampleReport) -> list[str]:
    """The run's reading, in counts."""
    counts = report.counts()
    outcomes = Counter(row.outcome for row in report.rows if row.outcome is not None)
    by_outcome = ", ".join(f"{name} {count}" for name, count in sorted(outcomes.items()))
    acted = counts["resolved"] + counts["triage"]
    rate = f" ({counts['triage'] / acted:.2f})" if acted else ""
    lines = [
        f"appeal-sample {report.court}: {counts['sampled']} of {report.take} civil appeals read "
        + f"(filed {report.filed_after} to {report.filed_before}, seed {report.seed}), "
        + f"{report.requests} of {report.max_requests} requests",
        f"  drawn {report.candidates}: {report.not_civil} not civil, "
        + f"{report.no_case_type} with no case type, {counts['too_long']} too long to read",
        f"  disposition read: {counts['resolved']}" + (f" ({by_outcome})" if by_outcome else ""),
        f"  triage: {counts['triage']} of the {acted} appeals with a disposition entry{rate}",
        f"  nothing read: {counts['open']}, of which {counts['open_terminated']} "
        + "upstream marks terminated",
        f"  rule {report.rule}",
    ]
    if report.exhausted:
        lines.append("  the search ran out before the sample was full")
    if report.stopped is not None:
        lines.append(f"  stopped: {report.stopped}")
    lines.extend(f"  error: {error}" for error in report.errors)
    return lines
