"""Per-Justice merits priors rolled up from merits lineups and the cases' judgments."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.analytics import build_statpack, render_statpack_markdown
from fedcourtsai.cli import app
from fedcourtsai.pipeline.justice_priors import (
    case_judgments,
    justice_priors,
    justice_votes_section,
    pool_before,
)
from fedcourtsai.pipeline.merits_lineups import MeritsLineup
from fedcourtsai.schemas import Disposition, Judgment, JusticeVote, VoteValue

from .test_merits_lineups import _document, _seated, _seven_two, _store

runner = CliRunner()


def _lineup(
    term: int,
    number: str,
    votes: dict[str, VoteValue],
    *,
    case_id: str | None = None,
    status: str = "complete",
) -> MeritsLineup:
    return MeritsLineup(
        term=term,
        listing_number=number,
        dockets=[f"{term % 100}-{number}"],
        case_id=case_id,
        case_name=f"Case {number}",
        decided=date(term + 1, 6, 1),
        status=status,
        votes=[JusticeVote(justice=name, vote=vote) for name, vote in votes.items()]
        if status == "complete"
        else [],
    )


M, D, P = VoteValue.majority, VoteValue.dissent, VoteValue.concur_in_part


def test_sides_and_disturb_votes_follow_the_judgment() -> None:
    lineups = [
        _lineup(2024, "1", {"A": M, "B": M, "C": D}, case_id="scotus/1"),
        _lineup(2024, "2", {"A": M, "B": D, "C": D}, case_id="scotus/2"),
    ]
    judgments = {"scotus/1": Judgment.reversed, "scotus/2": Judgment.affirmed}
    (term,) = justice_priors(lineups, judgments).terms
    rows = {row.justice: row for row in term.justices}
    assert (term.complete, term.judged) == (2, 2)
    assert (rows["A"].majority, rows["A"].disturb) == (2, 1)
    # Dissenting from an affirmance is a vote to disturb; joining a reversal is too.
    assert (rows["B"].majority, rows["B"].disturb) == (1, 2)
    assert (rows["C"].majority, rows["C"].disturb) == (0, 1)
    pairs = {pair.justices: (pair.both, pair.agree) for pair in term.pairs}
    assert pairs == {("A", "B"): (2, 1), ("A", "C"): (2, 0), ("B", "C"): (2, 1)}


def test_a_vote_in_part_sits_but_takes_no_side() -> None:
    lineups = [_lineup(2024, "1", {"A": M, "B": P, "C": D}, case_id="scotus/1")]
    (term,) = justice_priors(lineups, {"scotus/1": Judgment.vacated}).terms
    rows = {row.justice: row for row in term.justices}
    assert (rows["B"].sat, rows["B"].in_part, rows["B"].majority) == (1, 1, 0)
    assert rows["B"].disturb_eligible == 0
    assert [pair.justices for pair in term.pairs] == [("A", "C")]


@pytest.mark.parametrize(
    "judgment", [Judgment.affirmed_in_part, Judgment.dig, Judgment.equally_divided, None]
)
def test_a_judgment_with_no_single_side_counts_majority_only(judgment: Judgment | None) -> None:
    lineups = [_lineup(2024, "1", {"A": M, "B": D}, case_id="scotus/1")]
    (term,) = justice_priors(lineups, {"scotus/1": judgment}).terms
    assert term.judged == 0
    assert all(row.disturb_eligible == 0 for row in term.justices)
    assert sum(row.majority for row in term.justices) == 1


def test_a_justice_who_took_no_part_is_not_counted() -> None:
    lineups = [_lineup(2024, "1", {"A": M, "B": VoteValue.recused}, case_id="scotus/1")]
    (term,) = justice_priors(lineups, {}).terms
    assert [row.justice for row in term.justices] == ["A"]


def test_only_complete_lineups_are_tallied() -> None:
    lineups = [
        _lineup(2024, "1", {"A": M}, case_id="scotus/1"),
        _lineup(2024, "2", {}, status="per-curiam"),
        _lineup(2024, "3", {}, status="unobserved"),
    ]
    (term,) = justice_priors(lineups, {}).terms
    assert (term.documents, term.complete) == (3, 1)
    assert term.justices[0].sat == 1


def test_pooling_reads_only_strictly_earlier_terms() -> None:
    lineups = [
        _lineup(2023, "1", {"A": M, "B": D}, case_id="scotus/1"),
        _lineup(2024, "1", {"A": D, "B": M}, case_id="scotus/2"),
        _lineup(2025, "1", {"A": D, "B": M}, case_id="scotus/3"),
    ]
    judgments = {f"scotus/{n}": Judgment.reversed for n in (1, 2, 3)}
    priors = justice_priors(lineups, judgments)
    assert [t.term for t in priors.terms] == [2025, 2024, 2023]
    pooled = pool_before(priors, 2025)
    assert (pooled.terms, pooled.decisions) == ([2023, 2024], 2)
    rates = {row.justice: row for row in pooled.justices}
    assert rates["A"].majority_rate == 0.5
    assert rates["A"].disturb_rate == 0.5
    assert pooled.pairs[0].agreement == 0.0
    assert pool_before(priors, 2023).decisions == 0


def test_pooling_limits_to_a_bench() -> None:
    lineups = [_lineup(2024, "1", {"A": M, "B": M, "C": D}, case_id="scotus/1")]
    pooled = pool_before(justice_priors(lineups, {}), 2025, justices=["A", "B"])
    assert [row.justice for row in pooled.justices] == ["A", "B"]
    assert [pair.justices for pair in pooled.pairs] == [("A", "B")]
    assert pooled.justices[0].disturb_rate is None


def test_case_judgments_reads_the_parsed_label(tmp_path: Path) -> None:
    with corpus.connect(tmp_path / "c.db") as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-1",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2024, 10, 7),
                    merits_judgment="reversed",
                    merits_decided=date(2025, 6, 1),
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-2",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2024, 10, 7),
                ),
            ],
        )
        judgments = case_judgments(conn, ["scotus/1", "scotus/2", "scotus/3"])
    assert judgments == {"scotus/1": Judgment.reversed, "scotus/2": None}


def test_the_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    assert runner.invoke(app, ["justice-priors"]).exit_code == 1  # no corpus yet
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass
    result = runner.invoke(app, ["justice-priors", "--first-term", "2024", "--last-term", "2025"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["terms"] == []
    assert payload["pooled"]["before_term"] == 2026
    backwards = ["justice-priors", "--first-term", "2025", "--last-term", "2024"]
    assert runner.invoke(app, backwards).exit_code == 2


def test_a_vote_with_no_merits_side_is_refused() -> None:
    lineups = [_lineup(2024, "1", {"A": M, "B": VoteValue.grant}, case_id="scotus/1")]
    with pytest.raises(ValueError, match="no merits side"):
        justice_priors(lineups, {})


def _decided_case(db: Path, case_id: str, number: str, judgment: str) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=number,
                    disposition=Disposition.granted,
                    date_cert_granted=date(2025, 10, 6),
                    merits_judgment=judgment,
                    merits_decided=date(2026, 6, 30),
                )
            ],
        )


def test_the_statpack_section_reads_the_whole_record(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert justice_votes_section(conn) is None  # no record, no section
    _decided_case(db, "scotus/1", "25-1", "reversed")
    _store(db, _seated(_document("1", _seven_two()).model_copy(update={"case_id": "scotus/1"})))
    with corpus.connect(db) as conn:
        section = justice_votes_section(conn)
    assert section is not None
    (term,) = section.terms
    assert (term.term, term.documents, term.complete, term.judged) == (2025, 1, 1, 1)
    rows = {row.justice: row for row in term.justices}
    assert (rows["Kagan"].disturb, rows["Alito"].disturb) == (1, 0)

    pack = build_statpack(corpus_db_path=db)
    assert pack.justice_votes == section
    markdown = render_statpack_markdown(pack)
    assert "## Per-Justice merits votes (complete lineups)" in markdown
    assert "| Kagan | 1 | 1 (100.0%) | 0 | 1 of 1 (100.0%) |" in markdown


def test_a_record_without_a_complete_lineup_has_no_section(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _store(db, _document("1", _seven_two()), benched=False)
    with corpus.connect(db) as conn:
        assert justice_votes_section(conn) is None
    assert "justice_votes" not in build_statpack(corpus_db_path=db).model_dump()
