"""Merits lineups derived from the per-opinion record and its bench rows."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import merits_lineups
from fedcourtsai.pipeline.lineup import WritingKind
from fedcourtsai.pipeline.merits_lineups import lineup_census
from fedcourtsai.pipeline.opinion_record import (
    OpinionDocumentReading,
    OpinionEntry,
    OpinionJoin,
    insert_opinions,
)
from fedcourtsai.schemas import VoteValue

BENCH = [
    "Roberts",
    "Thomas",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
    "Barrett",
    "Jackson",
]
DECIDED = date(2026, 6, 30)

runner = CliRunner()


def _opinion(
    position: int,
    kind: WritingKind,
    author: str | None,
    joins: list[str] | None = None,
    qualifier: str | None = None,
) -> OpinionEntry:
    return OpinionEntry(
        position=position,
        kind=kind,
        author=author,
        joins=[OpinionJoin(justice=j, qualifier=qualifier) for j in joins or []],
        words=10,
        footnote_words=0,
        header="header",
    )


def _document(
    number: str,
    opinions: list[OpinionEntry],
    *,
    bench: list[str] | None = None,
    absent: list[str] | None = None,
) -> OpinionDocumentReading:
    return OpinionDocumentReading(
        term=2025,
        listing_number=number,
        docket=f"25-{number}",
        dockets=[f"25-{number}"],
        name=f"Case {number}",
        url=f"https://www.supremecourt.gov/opinions/25pdf/25-{number}_x.pdf",
        decided=DECIDED,
        status="read",
        source_format="slip",
        lineup="scotus-syllabus/2",
        opinions=opinions,
        bench=bench,
        took_no_part=absent,
    )


def _court(author: str, *, besides: set[str]) -> OpinionEntry:
    """The Court's opinion, joined in full by everyone on the bench not in ``besides``."""
    joiners = [j for j in BENCH if j != author and j not in besides]
    return _opinion(1, WritingKind.opinion_of_the_court, author, joiners)


def _seven_two() -> list[OpinionEntry]:
    return [
        _court("Kagan", besides={"Alito", "Thomas"}),
        _opinion(2, WritingKind.dissent, "Alito", ["Thomas"]),
    ]


def _recusal() -> list[OpinionEntry]:
    return [_court("Roberts", besides={"Jackson"})]


@pytest.fixture
def db(tmp_path: Path) -> Path:
    return corpus.corpus_db_path(tmp_path / "corpus")


def _seated(
    document: OpinionDocumentReading, absent: list[str] | None = None
) -> OpinionDocumentReading:
    """The document with a filled bench row: the full bench, ``absent`` taking no part."""
    return document.model_copy(update={"bench": list(BENCH), "took_no_part": absent or []})


def _store(db: Path, *documents: OpinionDocumentReading, benched: bool = True) -> None:
    """Insert the documents' rows, with their bench rows (null where unobserved) if ``benched``."""
    with corpus.connect(db) as conn:
        pairs = [(d, o) for d in documents for o in d.opinions]
        seated = [d for d in documents if d.opinions[0].kind is not WritingKind.per_curiam]
        insert_opinions(conn, pairs, seated if benched else [])


def _lineups(db: Path) -> dict[str, merits_lineups.MeritsLineup]:
    with corpus.connect(db) as conn:
        found = merits_lineups.merits_lineups(conn, first_term=2025, last_term=2025)
    return {lineup.listing_number: lineup for lineup in found}


def test_a_filled_bench_row_completes_the_lineup(db: Path) -> None:
    _store(db, _seated(_document("1", _seven_two())))
    lineup = _lineups(db)["1"]
    assert lineup.status == "complete"
    assert (lineup.participating, lineup.dissenting, lineup.partial) == (9, 2, 0)
    votes = {v.justice: v.vote for v in lineup.votes}
    assert votes["Alito"] == VoteValue.dissent and votes["Kagan"] == VoteValue.majority
    assert sorted(votes) == sorted(BENCH)
    assert merits_lineups.split_key(lineup) == "7-2"


def test_a_recusal_is_seated_by_its_bench_row(db: Path) -> None:
    _store(db, _seated(_document("1", _recusal()), ["Jackson"]))
    lineup = _lineups(db)["1"]
    assert lineup.status == "complete"
    assert (lineup.participating, lineup.dissenting) == (8, 0)
    assert {v.justice: v.vote for v in lineup.votes}["Jackson"] == VoteValue.did_not_participate
    assert merits_lineups.split_key(lineup) == "8-0"


@pytest.mark.parametrize("benched", [True, False])
def test_writings_alone_complete_nothing(db: Path, benched: bool) -> None:
    """With no filled bench row, even writings that place every Justice derive no lineup.

    The syllabus grammar credits the lead with everyone a paragraph does not
    exclude, so a recusal sentence it could not read leaves writings that place
    the recused Justice in the majority; only the bench row's gate tells.
    """
    _store(db, _document("1", _seven_two()), benched=benched)  # a null row, or none
    lineup = _lineups(db)["1"]
    assert lineup.status == "unobserved" and lineup.votes == []


def test_a_justice_who_signs_nothing_on_a_filled_bench_is_unplaced(db: Path) -> None:
    _store(db, _seated(_document("1", _recusal())))  # the row says Jackson sat
    lineup = _lineups(db)["1"]
    assert lineup.status == "unplaced" and lineup.votes == []
    assert lineup.problems == ["Jackson is not accounted for by any writing"]


def test_a_per_curiam_derives_no_lineup(db: Path) -> None:
    _store(
        db,
        _document(
            "1",
            [
                _opinion(1, WritingKind.per_curiam, None),
                _opinion(2, WritingKind.dissent, "Alito"),
            ],
        ),
    )
    lineup = _lineups(db)["1"]
    assert lineup.status == "per-curiam" and lineup.votes == []


def test_writings_that_contradict_themselves_are_refused(db: Path) -> None:
    opinions = [
        _court("Kagan", besides=set()),
        _opinion(2, WritingKind.dissent, "Alito"),  # joined the Court in full, too
    ]
    _store(db, _seated(_document("1", opinions)))
    lineup = _lineups(db)["1"]
    assert lineup.status == "refused" and lineup.votes == []


def test_a_vote_in_part_is_kept_apart_from_the_majority_and_the_dissent(db: Path) -> None:
    # Roberts, Thomas and Alito join Part I of the Court's opinion and dissent from the rest.
    lead = _opinion(
        1, WritingKind.opinion_of_the_court, "Kagan", ["Gorsuch", "Kavanaugh", "Barrett", "Jackson"]
    )
    lead.joins.extend(
        OpinionJoin(justice=j, qualifier="as to Part I") for j in ("Roberts", "Thomas", "Alito")
    )
    dissent = _opinion(2, WritingKind.dissent, "Alito", ["Roberts", "Thomas", "Sotomayor"])
    _store(db, _seated(_document("1", [lead, dissent])))
    lineup = _lineups(db)["1"]
    assert lineup.status == "complete"
    assert (lineup.dissenting, lineup.partial) == (1, 3)
    assert merits_lineups.split_key(lineup) == "5-1, 3 in part"


def test_a_blob_without_the_tables_reads_as_no_lineups(tmp_path: Path) -> None:
    path = tmp_path / "legacy.db"
    raw = sqlite3.connect(path)
    raw.execute("CREATE TABLE cases (case_id TEXT)")
    raw.commit()
    raw.close()
    ro = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    ro.row_factory = sqlite3.Row
    try:
        assert merits_lineups.merits_lineups(ro, first_term=2025, last_term=2025) == []
    finally:
        ro.close()


def _census(
    db: Path, monkeypatch: pytest.MonkeyPatch, decided: dict[int, list[str]]
) -> merits_lineups.LineupCensus:
    monkeypatch.setattr(
        merits_lineups, "plenary_decided_dockets", lambda conn, first_term, last_term: decided
    )
    first, last = min(decided), max(decided)
    with corpus.connect(db) as conn:
        lineups = merits_lineups.merits_lineups(conn, first_term=first, last_term=last)
        return lineup_census(conn, lineups, first_term=first, last_term=last)


def test_the_census_counts_coverage_and_splits(db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _store(
        db,
        _seated(_document("1", _seven_two())),
        _seated(_document("2", _recusal()), ["Jackson"]),
        _document("3", _seven_two()),  # unobserved
        _seated(_document("4", _seven_two())),  # decided outside the census population
    )
    (term,) = _census(db, monkeypatch, {2025: ["25-1", "25-2", "25-3", "25-9"]}).terms
    assert term.documents == 4
    assert term.statuses == {"complete": 3, "unobserved": 1}
    assert (term.covered, term.printed, term.plenary_decided) == (2, 3, 4)
    assert (term.covered_across_terms, term.unmatched_complete, term.unanimous) == (0, 1, 1)
    assert term.splits == {"8-0": 1, "7-2": 2}


def test_the_census_matches_a_docket_across_terms(
    db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _store(db, _seated(_document("1", _seven_two())))
    ot24, ot25 = _census(db, monkeypatch, {2024: ["25-1"], 2025: []}).terms
    assert (ot24.documents, ot24.covered, ot24.covered_across_terms) == (0, 1, 1)
    assert ot25.unmatched_complete == 0


def test_the_command(db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    assert runner.invoke(app, ["merits-lineups"]).exit_code == 1  # no corpus yet
    _store(db, _seated(_document("1", _seven_two())))
    result = runner.invoke(app, ["merits-lineups", "--first-term", "2025", "--last-term", "2025"])
    assert result.exit_code == 0, result.output
    assert "OT2025: 1 documents (complete 1)" in result.output
    payload = json.loads(result.stdout)
    assert payload["lineups"][0]["status"] == "complete"
    assert payload["census"]["derivation"] == "scotus-merits-lineup/1"
    backwards = ["merits-lineups", "--first-term", "2025", "--last-term", "2024"]
    assert runner.invoke(app, backwards).exit_code == 2
