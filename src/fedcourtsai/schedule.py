"""Build the published schedule: each pending public docket's next dates at the Court.

``data/schedule/schedule.json`` carries, for every docket that already has a
committed directory under ``data/cases``, the dates ahead the live channel last
read off its docket:

- **the conference** an undecided petition is distributed for;
- **the argument day** a granted case awaiting its merits decision is set for;
- **the response deadline**, while the docket is undecided and the response is
  still owed (no response or waiver has followed the newest stated deadline).

It is the forward-looking data the public site's case timeline shows beside
each step, joined onto the big-case board by ``fedcourts big-cases`` so the
board itself stays a ledger-only read.

Two invariants:

- **Public set only.** The rows are enumerated from the committed ``data/cases``
  tree (:func:`fedcourtsai.scope_manifest.public_case_ids`), and the corpus is
  consulted by exact ``case_id`` lookup alone — the scope manifest's
  compilation-extent boundary, held for the same reason.
- **Never a past date as upcoming.** A date before ``as_of`` keeps its row, with
  the upcoming date null and the reason, so a docket the Court has not yet
  acted on after the day is never shown as still scheduled.

Not a cell input: no provisioning step reads this file, and a test holds the
provisioning modules to that, because feeding a scheduled date to a cell would
change what it sees. The corpus columns behind the argument day and the
response deadline are withheld from the retrieval surface for the same reason.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from . import corpus
from .schemas import Schedule, ScheduledDay, ScheduleEntry
from .scope_manifest import public_case_ids


def schedule_path(data_root: Path) -> Path:
    """Where the committed schedule lives under ``data_root``."""
    return data_root / "schedule" / "schedule.json"


def _day(set_for: date | None, as_of: date) -> ScheduledDay | None:
    """``set_for`` judged against ``as_of``: upcoming, passed, or absent."""
    if set_for is None:
        return None
    if set_for >= as_of:
        return ScheduledDay(set_for=set_for, upcoming=set_for)
    return ScheduledDay(set_for=set_for, upcoming=None, stale_reason="passed")


def _awaits_merits(row: corpus.CorpusRow) -> bool:
    """Whether a granted case's merits proceeding is still undecided."""
    return (
        corpus.opens_merits_proceeding(row)
        and row.merits_judgment is None
        and row.merits_decided is None
        and row.merits_terminated is None
    )


def _entry(row: corpus.CorpusRow, as_of: date) -> ScheduleEntry | None:
    """The row's dates in play on ``as_of``, or ``None`` when it has none."""
    # Either signal of a decision takes the docket off the cert-stage schedule:
    # a disposition can land before the date that would carry it.
    undecided = row.disposition is None and corpus.resolution_date(row) is None
    conference = row.distributed_for_conference if undecided else None
    argument: ScheduledDay | None = None
    if _awaits_merits(row) and row.argument_set_for is not None:
        # An argument heard on or after the setting has happened; one heard
        # before it is a first argument, and the setting is a reargument.
        argued = row.merits_argued is not None and row.merits_argued >= row.argument_set_for
        argument = None if argued else _day(row.argument_set_for, as_of)
    owed = undecided and row.response_due_state == "due"
    response_due = _day(row.response_due, as_of) if owed else None
    if conference is None and argument is None and response_due is None:
        return None
    upcoming = conference is not None and conference >= as_of
    return ScheduleEntry(
        case_id=row.case_id,
        next_conference=conference if upcoming else None,
        distributed_for_conference=conference,
        stale_reason="conference_passed" if conference is not None and not upcoming else None,
        argument=argument,
        response_due=response_due,
        last_live_polled=row.last_live_polled,
    )


def build_schedule(*, data_root: Path, corpus_db_path: Path, as_of: date) -> Schedule:
    """Each pending public docket's dates in play, judged against ``as_of``.

    Deterministic in its inputs: the committed tree, the corpus, and the day.
    Returns a ``skipped`` schedule when the corpus is absent, which a caller
    does not write over a committed one.
    """
    if not corpus_db_path.exists():
        return Schedule(skipped=True)
    entries: list[ScheduleEntry] = []
    with corpus.connect_readonly(corpus_db_path, backend="local") as conn:
        for case_id in public_case_ids(data_root):
            row = corpus.get_row(conn, case_id)
            if row is None:
                continue
            entry = _entry(row, as_of)
            if entry is not None:
                entries.append(entry)
    entries.sort(key=lambda entry: entry.case_id)
    return Schedule(as_of=as_of, entries=entries)
