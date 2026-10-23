"""Who wrote the Court's decisions, per Term: the authorship claims' baseline feed.

The statpack's authorship section (:class:`~fedcourtsai.schemas.StatPackAuthorship`)
is rolled up here from the per-opinion record, the corpus's ``opinions`` and
``opinion_benches`` tables, and the claims' strictly-prior baselines
(:func:`fedcourtsai.pipeline.base_rates.majority_author_base_rate` and
:func:`~fedcourtsai.pipeline.base_rates.separate_writing_base_rate`) pool it.

**A decision** is one listing row: its writings are the rows sharing its Term
and listing number, ordered by position, and the first is the deciding opinion.
One that decides for the Court and names its author (the opinion of the Court,
or a plurality) is **signed**; a per curiam names none. The Term is the
listing's own, the Term the Court files the decision under. Only an **argued**
decision that decides the case is counted: a merits forecast is made on a case
the Court granted for argument, so the summary per curiams the listing also
carries would price a per curiam that population rarely sees, and a dismissal
is one the claim masks. A signed decision is argued when its opinion prints an
argument date. A per curiam prints none, so it is counted when the corpus row it
links to classifies it as a per curiam after argument (``merits_decision_method``),
the one per curiam the claim resolves on a merits case; one linked to no row,
or to a row not yet classified, is left out, as the claim masks it.

A signed decision whose writings put its lead author on a second writing, or
carry a second lead-kind writing (an opinion of the Court for one part by
another Justice), is counted by neither tally: the claims record such a Justice
with a mixed role, no single lead, and mask the decision.

**Majority authorship** counts, for each Justice serving on a decision's date
(:func:`~.justices.bench_on`), the decisions decided while seated and the
signed ones the Justice delivered. A Justice is counted as one who could have
written whether or not they sat, the same reading the authorship tally gives a
recusal.

**Separate writing** counts only signed decisions whose bench row is filled,
the observation that the writings were read whole and that says who took part.
Over the Justices taking part, it counts those who wrote or co-wrote any
writing but the deciding one. A per curiam carries no bench observation the
claim can resolve against, and an unobserved decision would misread a Justice
who signed nothing as one who wrote nothing, so neither is counted. The
population is the argued signed decisions alone, while the claim also
resolves a dismissal or a summary disposition whose roles were observed; the
record carries no bench observation for those, so the baseline cannot price
them apart.

Read-only, and a pure function of the two tables and the per curiams' case
rows: a blob without the tables reads as an empty record.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .. import corpus
from ..schemas import StatPackAuthorship, StatPackAuthorshipJustice, StatPackAuthorshipTerm
from .authorship import LEAD_KINDS
from .justices import SERVICE, SERVICE_FLOOR, bench_on

_PER_CURIAM = "per-curiam"

# Case ids per lookup, inside SQLite's bound-parameter limit.
_CHUNK = 500


def _rows(conn: corpus.ReadConnection, sql: str) -> list[Any]:
    try:
        return list(conn.execute(sql).fetchall())
    except Exception as exc:
        # sqlite3's OperationalError locally, the ranged backend's own error type remotely.
        if "no such table" not in str(exc).lower():
            raise
        return []


def _names(raw: object) -> list[str]:
    """The names a JSON list column prints; empty where it prints none."""
    if not raw:
        return []
    parsed = json.loads(str(raw))
    return [str(name) for name in parsed] if isinstance(parsed, list) else []


@dataclass
class _Writing:
    kind: str
    author: str | None
    coauthors: list[str]
    argued: bool
    case_id: str | None


@dataclass
class _Decision:
    decided: date
    writings: dict[int, _Writing] = field(default_factory=dict)


@dataclass
class _JusticeAcc:
    decisions: int = 0
    majority: int = 0
    sat: int = 0
    separate: int = 0


@dataclass
class _TermAcc:
    decisions: int = 0
    per_curiam: int = 0
    observed: int = 0
    justices: defaultdict[str, _JusticeAcc] = field(
        default_factory=lambda: defaultdict(_JusticeAcc)
    )


def _argued_cases(conn: corpus.ReadConnection, case_ids: list[str]) -> set[str]:
    """Of ``case_ids``, the rows classified as a per curiam after argument."""
    argued: set[str] = set()
    for start in range(0, len(case_ids), _CHUNK):
        chunk = case_ids[start : start + _CHUNK]
        marks = ", ".join("?" * len(chunk))
        argued.update(
            str(row[0])
            for row in conn.execute(
                f"SELECT case_id FROM cases WHERE case_id IN ({marks}) "
                "AND merits_decision_method = 'argued-per-curiam'",
                tuple(chunk),
            ).fetchall()
        )
    return argued


def authorship_section(conn: corpus.ReadConnection) -> StatPackAuthorship | None:
    """Roll the per-opinion record into the statpack's authorship section.

    ``None`` while the record holds no argued decision, so the pack carries no
    ``authorship`` key. A decision dated before the
    roster's floor is left out, since no bench can be seated for it.
    """
    decisions: dict[tuple[int, str], _Decision] = {}
    for row in _rows(
        conn,
        "SELECT term, listing_number, position, decided, kind, author, coauthors, argued, "
        "case_id FROM opinions ORDER BY term, listing_number, position",
    ):
        key = (int(row[0]), str(row[1]))
        decided = date.fromisoformat(str(row[3]))
        decision = decisions.setdefault(key, _Decision(decided=decided))
        decision.writings[int(row[2])] = _Writing(
            kind=str(row[4]),
            author=str(row[5]) if row[5] else None,
            coauthors=_names(row[6]),
            argued=bool(row[7]),
            case_id=str(row[8]) if row[8] else None,
        )
    benches = {
        (int(row[0]), str(row[1])): (_names(row[2]), _names(row[3]))
        for row in _rows(
            conn,
            "SELECT term, listing_number, bench, took_no_part FROM opinion_benches "
            "WHERE bench IS NOT NULL",
        )
    }
    argued_per_curiams = _argued_cases(
        conn,
        sorted(
            {
                lead.case_id
                for lead in (d.writings[min(d.writings)] for d in decisions.values())
                if lead.kind == _PER_CURIAM and lead.case_id
            }
        ),
    )
    accs: dict[int, _TermAcc] = {}
    for key in sorted(decisions):
        decision = decisions[key]
        positions = sorted(decision.writings)
        lead = decision.writings[positions[0]]
        signed = lead.kind in LEAD_KINDS
        argued = lead.argued if signed else lead.case_id in argued_per_curiams
        if not (signed or lead.kind == _PER_CURIAM) or not argued:
            continue
        if decision.decided < SERVICE_FLOOR:
            continue
        separate = [decision.writings[position] for position in positions[1:]]
        writers = {
            name for writing in separate for name in (writing.author, *writing.coauthors) if name
        }
        if signed and (
            lead.author in writers or any(writing.kind in LEAD_KINDS for writing in separate)
        ):
            # A mixed role or no single lead: the claims mask it, so neither counts it.
            continue
        acc = accs.setdefault(key[0], _TermAcc())
        acc.decisions += 1
        acc.per_curiam += not signed
        for justice in bench_on(decision.decided):
            seat = acc.justices[justice]
            seat.decisions += 1
            seat.majority += signed and lead.author == justice
        bench = benches.get(key)
        if not signed or bench is None:
            continue
        acc.observed += 1
        seated, took_no_part = bench
        for justice in seated:
            if justice in took_no_part:
                continue
            seat = acc.justices[justice]
            seat.sat += 1
            seat.separate += justice in writers
    if not accs:
        return None
    order = {service.justice: rank for rank, service in enumerate(SERVICE)}
    return StatPackAuthorship(
        terms=[
            StatPackAuthorshipTerm(
                term=term,
                decisions=acc.decisions,
                per_curiam=acc.per_curiam,
                observed=acc.observed,
                justices=[
                    StatPackAuthorshipJustice(
                        justice=justice,
                        decisions=seat.decisions,
                        majority=seat.majority,
                        sat=seat.sat,
                        separate=seat.separate,
                    )
                    for justice, seat in sorted(
                        acc.justices.items(), key=lambda item: order.get(item[0], len(order))
                    )
                ],
            )
            for term, acc in sorted(accs.items(), reverse=True)
        ]
    )
