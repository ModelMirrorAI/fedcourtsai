"""Build the published schedule: each pending public docket's next conference.

``data/schedule/schedule.json`` carries, for every docket that already has a
committed directory under ``data/cases``, is undecided in the corpus, and has
been distributed for a conference, the conference date the live channel last
read off its docket. It is the forward-looking date the public site's case
timeline shows beside the "Court decides" step, joined onto the big-case board
by ``fedcourts big-cases`` so the board itself stays a ledger-only read.

Two invariants:

- **Public set only.** The rows are enumerated from the committed ``data/cases``
  tree (:func:`fedcourtsai.scope_manifest.public_case_ids`), and the corpus is
  consulted by exact ``case_id`` lookup alone — the scope manifest's
  compilation-extent boundary, held for the same reason.
- **Never a past date as upcoming.** A conference before ``as_of`` keeps its row,
  with ``next_conference`` null and the reason, so a docket the Court has not yet
  acted on after its conference is never shown as still scheduled.

Not a cell input: no provisioning step reads this file, and a test holds the
provisioning modules to that, because feeding a scheduled date to a cell would
change what it sees.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from . import corpus
from .schemas import Schedule, ScheduleEntry
from .scope_manifest import public_case_ids


def schedule_path(data_root: Path) -> Path:
    """Where the committed schedule lives under ``data_root``."""
    return data_root / "schedule" / "schedule.json"


def build_schedule(*, data_root: Path, corpus_db_path: Path, as_of: date) -> Schedule:
    """Each pending public docket's distributed conference, judged against ``as_of``.

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
            if row is None or row.distributed_for_conference is None:
                continue
            # Either signal of a decision takes the docket off the schedule: a
            # disposition can land before the date that would carry it.
            if row.disposition is not None or corpus.resolution_date(row) is not None:
                continue
            conference = row.distributed_for_conference
            upcoming = conference >= as_of
            entries.append(
                ScheduleEntry(
                    case_id=case_id,
                    next_conference=conference if upcoming else None,
                    distributed_for_conference=conference,
                    stale_reason=None if upcoming else "conference_passed",
                    last_live_polled=row.last_live_polled,
                )
            )
    entries.sort(key=lambda entry: entry.case_id)
    return Schedule(as_of=as_of, entries=entries)
