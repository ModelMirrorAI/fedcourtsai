"""Merits vote lineups for every decision the per-opinion record holds, derived from it.

The corpus-side vote target. The git ledger carries votes only on outcomes the
pipeline forecast (:mod:`fedcourtsai.vote_writer`), so a decided case it never
forecast has no lineup there, and the historical vote tables — unanimity, the
split distribution, each Justice's majority and agreement rates — need one for
every decided case. They are read here, from two corpus tables and no third
source:

- ``opinions`` (:mod:`.opinion_record`): every writing in the decision, its
  kind, authors and joiners, partial joins included. These are the writings the
  syllabus grammar read, the same reading the ledger's merits vote source
  stamps from, so the side each Justice is on follows from them by
  :func:`~.lineup.lineup_from_writings`, the rule that source applies.
- ``opinion_benches``: who sat. The writings cannot say it: a Justice who took
  no part signs nothing, and neither does a Justice the record has simply not
  placed. A bench row's lists are filled only from a complete syllabus lineup
  that agrees with the listing (null otherwise), so a filled one is the
  observation that tells the two apart — and the gate that the writings
  themselves were read without a problem.

**Derived, not stored.** A lineup is recomputed from the rows on every read,
so it cannot drift from the record it describes, and a new rule reaches every
Term at once. A cell reads it only through the statpack's per-Justice votes
section (:func:`.justice_priors.justice_votes_section`): no ``query`` row,
provisioning step, outcome, mint or score reads it.

**Complete or nothing.** A lineup's ``votes`` are the whole bench or empty,
with the reason, and only a filled bench row can complete one. Without it the
writings are not enough: the syllabus grammar credits the lead with every
participant a paragraph does not exclude, so writings read around a sentence
the grammar could not place (a recusal or a dissent worded unusually) still
place every Justice, on the wrong side. Such a document's bench row is null,
and it derives no lineup (``unobserved``); so does a signed decision recorded
before its row, until the opinion-record pass adds one. A per curiam's record
comes from its headers, which name the separate writings but not who joined
the Court's opinion, so it derives no lineup (``per-curiam``).

**The census** (:func:`lineup_census`) sets the lineups against the decision
record's own count of decided cases (:func:`.decision_record.plenary_decided_dockets`),
per Term: how many plenary decided dockets any recorded document's listing row
prints (the ceiling) and how many a complete lineup's does, matched across the
range's Terms because the two put a case argued in one Term and decided in the
next in different ones; the complete lineups matching no census docket; and
the vote splits, with a vote in part on each side kept apart from the majority
and the dissent. The listing prints only a consolidated case's lead docket, so
a member docket decided with it is never covered. Every figure is over signed
decisions with a filled bench row: per curiams and unobserved documents are
counted by status and left out of the splits.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..schemas import QUORUM, JusticeVote, VoteValue
from .decision_record import plenary_decided_dockets
from .lineup import Join, Writing, WritingKind, justice_votes, lineup_from_writings

#: The derivation's stamp on every lineup, beside the reader stamp of the rows.
DERIVATION: Final = "scotus-merits-lineup"
#: Bump whenever the same rows could derive a different lineup — a change here or
#: to the side rules in :mod:`.lineup` (``_derive_vote``), which this derivation
#: shares with the ledger's vote writer.
DERIVATION_VERSION: Final = 1

Status = Literal["complete", "per-curiam", "unobserved", "unplaced", "refused"]


class MeritsLineup(BaseModel):
    """One decision's per-Justice merits votes, or why the record yields none."""

    model_config = ConfigDict(extra="forbid")

    term: int = Field(description="The October Term of the opinions listing")
    listing_number: str
    dockets: list[str] = Field(description="The docket numbers the listing row prints")
    case_id: str | None = Field(description="The `opinions` row's case link, as of its read")
    case_name: str
    decided: date
    status: Status = Field(
        description="complete: every Justice on the bench placed; per-curiam: the record "
        "names no joiners of the Court's opinion; unobserved: no filled bench row; unplaced: "
        "a Justice on the bench signs nothing; refused: any other problem (listed)"
    )
    votes: list[JusticeVote] = Field(
        default_factory=list, description="The whole bench in bench order; empty unless complete"
    )
    participating: int | None = Field(
        default=None, description="Justices who took part; None unless complete"
    )
    dissenting: int | None = Field(
        default=None,
        description="Participating Justices voting `dissent` in full; None unless complete",
    )
    partial: int | None = Field(
        default=None,
        description="Participating Justices voting in part on each side (`concur-in-part`): "
        "joined some of the Court's opinion and a dissent; None unless complete",
    )
    problems: list[str] = Field(default_factory=list)


#: A row as either backend returns it (``sqlite3.Row`` locally, the ranged backend's own row):
#: both index by column name.
Row = Any


def _table_rows(conn: corpus.ReadConnection, sql: str, params: tuple[int, ...] = ()) -> list[Row]:
    try:
        return list(conn.execute(sql, params).fetchall())
    except Exception as exc:
        # sqlite3's OperationalError locally, the ranged backend's own error type remotely.
        if "no such table" not in str(exc).lower():
            raise
        return []


def _writing(row: Row) -> Writing:
    joins = tuple(Join(j["justice"], j.get("qualifier")) for j in json.loads(row["joins"]))
    return Writing(
        WritingKind(row["kind"]),
        row["author"],
        joins,
        row["scope"],
        tuple(json.loads(row["coauthors"])),
    )


def _derive(rows: list[Row], bench_row: Row | None) -> MeritsLineup:
    head = rows[0]
    decided = date.fromisoformat(head["decided"])
    base = MeritsLineup(
        term=int(head["term"]),
        listing_number=str(head["listing_number"]),
        dockets=json.loads(head["dockets"]),
        case_id=head["case_id"],
        case_name=head["case_name"],
        decided=decided,
        status="refused",
    )
    writings = [_writing(row) for row in rows]
    if writings[0].kind is WritingKind.per_curiam:
        base.status = "per-curiam"
        base.problems = ["a per curiam's headers do not say who joined the Court's opinion"]
        return base
    if bench_row is None:
        base.status = "unobserved"
        base.problems = ["no bench row observed who sat"]
        return base
    lineup = lineup_from_writings(
        court="scotus",
        grammar=DERIVATION,
        grammar_version=DERIVATION_VERSION,
        bench=json.loads(bench_row["bench"]),
        writings=writings,
        took_no_part=json.loads(bench_row["took_no_part"]),
        quorum=QUORUM,
    )
    base.problems = list(lineup.problems)
    if lineup.complete:
        base.status = "complete"
        base.votes = justice_votes(lineup)
        base.participating = lineup.participating
        base.dissenting = sum(1 for v in lineup.votes.values() if v is VoteValue.dissent)
        base.partial = sum(1 for v in lineup.votes.values() if v is VoteValue.concur_in_part)
    elif all("is not accounted for" in p for p in lineup.problems):
        # The writings are consistent with each other; someone is just not placed.
        base.status = "unplaced"
    return base


def recorded_terms(conn: corpus.ReadConnection) -> tuple[int, int] | None:
    """The first and last Term the per-opinion record holds; None while it holds none."""
    rows = _table_rows(conn, "SELECT MIN(term), MAX(term) FROM opinions")
    if not rows or rows[0][0] is None:
        return None
    return int(rows[0][0]), int(rows[0][1])


def merits_lineups(
    conn: corpus.ReadConnection, *, first_term: int, last_term: int
) -> list[MeritsLineup]:
    """Every recorded document's lineup over the Terms, by Term and listing number. Read-only.

    A blob without the tables reads as an empty record.
    """
    terms = (first_term, last_term)
    opinions = _table_rows(
        conn,
        "SELECT * FROM opinions WHERE term BETWEEN ? AND ? ORDER BY term, listing_number, position",
        terms,
    )
    benches = {
        (int(row["term"]), str(row["listing_number"])): row
        for row in _table_rows(
            conn,
            "SELECT * FROM opinion_benches WHERE bench IS NOT NULL AND term BETWEEN ? AND ?",
            terms,
        )
    }
    documents: dict[tuple[int, str], list[Row]] = {}
    for row in opinions:
        documents.setdefault((int(row["term"]), str(row["listing_number"])), []).append(row)
    return [_derive(rows, benches.get(key)) for key, rows in documents.items()]


class LineupTermCensus(BaseModel):
    """One October Term's lineups beside the decision record's decided cases."""

    model_config = ConfigDict(extra="forbid")

    term: int = Field(description="The opinions listing's Term for the lineups")
    documents: int = Field(ge=0, description="Listing rows the per-opinion record holds")
    statuses: dict[str, int] = Field(description="Documents by lineup status")
    plenary_decided: int = Field(
        ge=0,
        description="The decision census's decided dockets less those that rode the cert "
        "order, on that census's Term axis (argued Term, else decided Term), which is not "
        "the listing's: a case argued in one Term and decided in the next is in each "
        "count's own Term",
    )
    printed: int = Field(
        ge=0,
        description="Of `plenary_decided`, dockets any recorded document's listing row prints, "
        "whatever its lineup status, in any Term of the range: the ceiling `covered` can "
        "reach. The listing prints only a consolidated case's lead docket, so its member "
        "dockets are never printed",
    )
    covered: int = Field(
        ge=0,
        description="Of `plenary_decided`, dockets a complete lineup's listing row prints, in "
        "any Term of the range",
    )
    covered_across_terms: int = Field(
        ge=0, description="Of `covered`, those whose lineup is listed in another Term"
    )
    unmatched_complete: int = Field(
        ge=0,
        description="This Term's complete lineups printing no plenary decided docket of the "
        "range (an original action, a docket outside the census population): lineups the "
        "vote tables hold that the census does not count",
    )
    unanimous: int = Field(
        ge=0, description="Complete lineups with no vote in dissent, in full or in part"
    )
    splits: dict[str, int] = Field(
        description="Complete lineups by vote, 'majority-dissent' ('9-0', '6-3', '8-0'), with "
        "', N in part' where N Justices voted in part on each side ('5-2, 2 in part'), who "
        "are in neither count; the majority counts concurrences in the judgment"
    )


class LineupCensus(BaseModel):
    """The per-Term lineup census over a range of October Terms."""

    model_config = ConfigDict(extra="forbid")

    derivation: str = f"{DERIVATION}/{DERIVATION_VERSION}"
    terms: list[LineupTermCensus]


def _numbers(lineup: MeritsLineup) -> set[str]:
    return {n for raw in lineup.dockets if (n := corpus.normalize_docket_number(raw)) is not None}


def split_key(lineup: MeritsLineup) -> str:
    """A complete lineup's vote, majority first: '6-3', or '5-2, 2 in part'."""
    if lineup.participating is None or lineup.dissenting is None or lineup.partial is None:
        raise ValueError("only a complete lineup has a split")
    majority = lineup.participating - lineup.dissenting - lineup.partial
    split = f"{majority}-{lineup.dissenting}"
    return f"{split}, {lineup.partial} in part" if lineup.partial else split


def lineup_census(
    conn: corpus.ReadConnection,
    lineups: list[MeritsLineup],
    *,
    first_term: int,
    last_term: int,
) -> LineupCensus:
    """Count ``lineups`` per Term against the decision record's plenary decided dockets.

    A docket is matched against the lineups of every Term in the range, since
    the census and the listing put a case argued in one Term and decided in
    the next in different Terms.
    """
    decided = plenary_decided_dockets(conn, first_term=first_term, last_term=last_term)
    all_decided = {number for dockets in decided.values() for number in dockets}
    printed_by: dict[str, set[int]] = {}
    complete_by: dict[str, set[int]] = {}
    for lu in lineups:
        for number in _numbers(lu):
            printed_by.setdefault(number, set()).add(lu.term)
            if lu.status == "complete":
                complete_by.setdefault(number, set()).add(lu.term)
    terms = []
    for term in range(first_term, last_term + 1):
        members = [lu for lu in lineups if lu.term == term]
        complete = [lu for lu in members if lu.status == "complete"]
        dockets = decided.get(term, [])
        covered = [number for number in dockets if number in complete_by]
        splits = Counter(split_key(lu) for lu in complete)
        terms.append(
            LineupTermCensus(
                term=term,
                documents=len(members),
                statuses=dict(sorted(Counter(lu.status for lu in members).items())),
                plenary_decided=len(dockets),
                printed=sum(1 for number in dockets if number in printed_by),
                covered=len(covered),
                covered_across_terms=sum(1 for n in covered if term not in complete_by[n]),
                unmatched_complete=sum(1 for lu in complete if not _numbers(lu) & all_decided),
                unanimous=sum(1 for lu in complete if lu.dissenting == 0 and lu.partial == 0),
                splits=dict(
                    sorted(splits.items(), key=lambda kv: (-int(kv[0].split("-")[0]), kv[0]))
                ),
            )
        )
    return LineupCensus(terms=terms)
