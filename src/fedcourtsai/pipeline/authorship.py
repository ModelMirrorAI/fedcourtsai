"""Who has written from each argument sitting, as of a day: the authorship tally.

The Court spreads the majority opinions of each argument sitting across the
Justices, close to one apiece. So late in a Term, the Justices who have not yet
written for a sitting are the likely authors of its undecided cases, and the
pattern is public: every decided case's opinion names its author. This module
reads that pattern off the corpus as it stood on a given day, the input a
late-Term authorship forecast moment would be conditioned on.

**The sittings** are the Court's own, as its transcript list heads them
(:func:`fedcourtsai.corpus.argument_sittings`), never a reading of gaps between
argument days: the Court widens a heading to take in a special session (OT2023's
February sitting opens on its February 8 special session, OT2024's April sitting
runs to its May 15 add-on), which no gap rule reproduces. A case is placed by
its argument day falling within a heading's first and last day; one that falls
in none is left out.

**The cases of a sitting** are the corpus's granted cases whose argument day
(``merits_argued``) falls in it, and every recorded lead opinion whose printed
argument date does, one per docket until a decision consolidates them: a decided
lead opinion takes in the corpus rows of the other dockets it prints. A recorded
case sits where its opinion's printed argument date places it, whatever its
corpus row says, so no case is counted in two sittings. A case is
**decided** on the day when the per-opinion record holds its lead opinion decided
by then, or its row records a merits decision by then (a dismissal or a summary
disposition after argument, which no opinion names an author for). Its
**author** is the lead opinion's: the opinion of the Court, or a plurality's; a
per curiam names none. A decided case the record holds no opinion for is
**unrecorded**, distinct from one decided without an author: the record is
written per Term by a separate pass, so a Term it has not read shows every
decision unrecorded.

**As of a day** cuts the decisions: a decision dated after the day is not read,
a case argued after it is not yet in its sitting, and a sitting that opens after
it is not reported. The argument days and the sittings themselves are as stored
now, so a case reargued after the day sits under its reargument, and a heading
is read with its latest last day.

**The bench** is the roster on the sitting's first day (:func:`~.justices.bench_on`).
A Justice who took no part in a case still counts as one who could write, so a
recusal shows as a Justice owed an opinion no case of the sitting can supply.

Read-only and analytic: no ``query`` retrieval row, provisioning step, outcome,
mint or scoring gate reads it, and nothing a predict or evaluate cell sees
includes it.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from .. import corpus
from ..supremecourt import ArgumentSitting
from .justices import bench_on

#: The opinion kinds that decide a case for the Court and name its author: the
#: opinion of the Court and, where no majority joined one, the plurality. The
#: lineup reader's lead kinds less the per curiam, which names no author.
LEAD_KINDS: tuple[str, ...] = ("opinion-of-the-court", "plurality")


@dataclass(frozen=True)
class SittingCase:
    """One case of a sitting as of the tally's day.

    ``key`` is the corpus case id, or the printed docket where the per-opinion
    record links the opinion to no corpus row. ``author`` is None for an
    undecided case and for a decision no opinion names an author for.
    ``recorded`` says the per-opinion record holds the case's lead opinion.
    """

    key: str
    docket: str
    argued: date
    decided: date | None
    author: str | None
    recorded: bool = False


@dataclass(frozen=True)
class SittingTally:
    """One sitting's cases and who has written for it, as of the tally's day."""

    sitting: ArgumentSitting
    bench: tuple[str, ...]
    cases: tuple[SittingCase, ...]

    @property
    def authors(self) -> tuple[str, ...]:
        """The authors of the sitting's decided cases, in decision order, repeats kept."""
        decided = sorted(
            (case for case in self.cases if case.author is not None),
            key=lambda case: (case.decided or case.argued, case.key),
        )
        return tuple(case.author for case in decided if case.author is not None)

    @property
    def undecided(self) -> tuple[SittingCase, ...]:
        """The sitting's cases not yet decided."""
        return tuple(case for case in self.cases if case.decided is None)

    @property
    def unrecorded(self) -> tuple[SittingCase, ...]:
        """Decided cases the per-opinion record holds no opinion for: author unknown."""
        return tuple(case for case in self.cases if case.decided is not None and not case.recorded)

    @property
    def yet_to_write(self) -> tuple[str, ...]:
        """The bench's Justices who have written no lead opinion for the sitting.

        Oldest oath first, as :func:`~.justices.bench_on` seats them.
        """
        written = set(self.authors)
        return tuple(name for name in self.bench if name not in written)


def _rows(conn: corpus.ReadConnection, sql: str, params: tuple[Any, ...]) -> list[Any]:
    try:
        return list(conn.execute(sql, params).fetchall())
    except Exception as exc:
        # sqlite3's OperationalError locally, the ranged backend's own error type remotely.
        if "no such table" not in str(exc).lower():
            raise
        return []


def _day(raw: object) -> date | None:
    return date.fromisoformat(str(raw)) if raw else None


def _sitting_of(day: date, sittings: Sequence[ArgumentSitting]) -> ArgumentSitting | None:
    return next((sitting for sitting in sittings if sitting.holds(day)), None)


def authorship_tally(conn: corpus.ReadConnection, *, term: int, as_of: date) -> list[SittingTally]:
    """Each of ``term``'s sittings that opened by ``as_of``, with its cases and authors.

    Empty where the corpus holds no sittings for the Term. Earliest sitting
    first; within one, cases by argument day then key. Raises ``ValueError``
    for a sitting before the roster's floor (:func:`~.justices.bench_on`).
    """
    sittings = [s for s in corpus.argument_sittings(conn, term=term) if s.start <= as_of]
    if not sittings:
        return []
    first, last = sittings[0].start.isoformat(), min(sittings[-1].end, as_of).isoformat()
    by_sitting: dict[ArgumentSitting, dict[str, SittingCase]] = {s: {} for s in sittings}
    key_of_docket: dict[str, str] = {}
    for row in _rows(
        conn,
        "SELECT case_id, docket_number, merits_argued, merits_decided FROM cases "
        "WHERE court = 'scotus' AND merits_argued BETWEEN ? AND ?",
        (first, last),
    ):
        argued = _day(row[2])
        sitting = _sitting_of(argued, sittings) if argued is not None else None
        if argued is None or sitting is None:
            continue
        decided = _day(row[3])
        docket = corpus.normalize_docket_number(row[1])
        if docket is not None:
            key_of_docket[docket] = str(row[0])
        by_sitting[sitting][str(row[0])] = SittingCase(
            key=str(row[0]),
            docket=str(row[1] or ""),
            argued=argued,
            decided=decided if decided is not None and decided <= as_of else None,
            author=None,
        )
    for row in _rows(
        conn,
        "SELECT case_id, docket, argued, decided, kind, author, dockets FROM opinions "
        "WHERE position = 1 AND argued BETWEEN ? AND ? AND decided <= ? "
        "ORDER BY decided, term, listing_number",
        (first, last, as_of.isoformat()),
    ):
        argued = _day(row[2])
        sitting = _sitting_of(argued, sittings) if argued is not None else None
        if argued is None or sitting is None:
            continue
        lead = corpus.normalize_docket_number(str(row[1]))
        key = str(row[0]) if row[0] else key_of_docket.get(lead or "", f"docket:{row[1]}")
        # The opinion's printed argument date places the case: a row the corpus
        # holds under another sitting (a reargument, a disagreeing date) moves
        # here rather than being counted twice.
        held = None
        for cases in by_sitting.values():
            held = cases.pop(key, None) or held
            for member in _member_dockets(row[6]):
                member_key = key_of_docket.get(member)
                if member != lead and member_key is not None and member_key != key:
                    cases.pop(member_key, None)
        by_sitting[sitting][key] = SittingCase(
            key=key,
            docket=str(row[1]) if held is None else held.docket or str(row[1]),
            argued=argued,
            decided=_day(row[3]),
            author=str(row[5]) if row[4] in LEAD_KINDS and row[5] else None,
            recorded=True,
        )
    return [
        SittingTally(
            sitting=sitting,
            bench=bench_on(sitting.start),
            cases=tuple(sorted(cases.values(), key=lambda case: (case.argued, case.key))),
        )
        for sitting, cases in by_sitting.items()
    ]


def _member_dockets(raw: object) -> list[str]:
    """The normalized docket numbers an opinion row's ``dockets`` JSON prints."""
    if not raw:
        return []
    try:
        parsed = json.loads(str(raw))
    except ValueError:
        return []
    if not isinstance(parsed, list):
        return []
    return [d for d in (corpus.normalize_docket_number(str(x)) for x in parsed) if d]
