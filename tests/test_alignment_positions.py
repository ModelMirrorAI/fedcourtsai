from __future__ import annotations

import itertools
import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import alignment_positions
from fedcourtsai.pipeline.alignment_positions import (
    MIN_JUSTICE_DECISIONS,
    WINDOW_TERMS,
    _sides,
    bench_order,
    classical_scaling,
    estimated_positions,
    term_positions,
)
from fedcourtsai.pipeline.alignment_score import JusticePositions
from fedcourtsai.pipeline.merits_lineups import MeritsLineup
from fedcourtsai.schemas import VoteValue

from .test_justice_priors import _lineup

runner = CliRunner()

M, D, P, R = (
    VoteValue.majority,
    VoteValue.dissent,
    VoteValue.concur_in_part,
    VoteValue.recused,
)
#: Most to least conservative, as the synthetic record votes them.
ORDER = (
    "Thomas",
    "Alito",
    "Gorsuch",
    "Kavanaugh",
    "Roberts",
    "Barrett",
    "Kagan",
    "Sotomayor",
    "Jackson",
)


def _cut(term: int, n: int, cut: int, *, conservative_wins: bool = True) -> MeritsLineup:
    """A decision splitting the ordering after its first ``cut`` Justices."""
    votes = {j: (M if (i < cut) == conservative_wins else D) for i, j in enumerate(ORDER)}
    return _lineup(term, str(n), votes)


def _record(term: int) -> list[MeritsLineup]:
    """Fifty decisions: unanimous ones, and splits cutting the ordering at every point."""
    lineups = [_lineup(term, str(n), dict.fromkeys(ORDER, M)) for n in range(10)]
    n = 10
    for cut in range(1, 9):
        for _ in range(5):
            lineups.append(_cut(term, n, cut, conservative_wins=cut >= 5))
            n += 1
    return lineups


def test_classical_scaling_recovers_points_on_a_line() -> None:
    points = [0.0, 1.0, 3.0, 7.0]
    distance = [[abs(a - b) for b in points] for a in points]
    placed = classical_scaling(distance)
    gaps = [b - a for a, b in itertools.pairwise(placed)]
    # Up to sign and centring, the scaling is the line itself.
    if gaps[0] < 0:
        placed = [-x for x in placed]
    assert placed[1] - placed[0] == pytest.approx(1.0, abs=1e-6)
    assert placed[3] - placed[2] == pytest.approx(4.0, abs=1e-6)


def test_the_estimate_orders_the_bench_as_it_votes() -> None:
    placed = term_positions(_record(2023), 2023)
    assert bench_order(placed)[:2] == ["Thomas", "Alito"]
    assert bench_order(placed)[-1] == "Jackson"
    # The conservative bloc sits at the higher end.
    assert placed["Thomas"] > 0 > placed["Jackson"]
    assert placed["Barrett"] > placed["Kagan"]


def test_a_vote_in_part_or_an_absence_has_no_side() -> None:
    odd = _lineup(2023, "x", dict.fromkeys(ORDER, M) | {"Kagan": P, "Jackson": R, "Alito": D})
    sides = _sides(odd)
    assert "Kagan" not in sides and "Jackson" not in sides
    assert sides["Alito"] is False and sides["Thomas"] is True


def test_a_justice_with_too_few_decisions_is_not_placed() -> None:
    lineups = _record(2023)
    thin = [
        lu.model_copy(
            update={
                "votes": [
                    v
                    if v.justice != "Jackson" or i < MIN_JUSTICE_DECISIONS - 1
                    else v.model_copy(update={"vote": R})
                    for v in lu.votes
                ]
            }
        )
        for i, lu in enumerate(lineups)
    ]
    assert "Jackson" not in term_positions(thin, 2023)


def test_a_term_reads_only_its_window() -> None:
    outside = [
        lu.model_copy(update={"listing_number": f"old{lu.listing_number}"})
        for lu in _record(2023 - WINDOW_TERMS)
    ]
    flipped = [
        lu.model_copy(update={"votes": [v.model_copy(update={"vote": M}) for v in lu.votes]})
        for lu in outside
    ]
    # A Term before the window changes nothing, whatever its votes.
    assert term_positions(_record(2023) + flipped, 2023) == pytest.approx(
        term_positions(_record(2023), 2023)
    )
    # A Term no Justice sat in places no bench.
    assert term_positions(_record(2023), 2024) == {}


def test_each_release_is_dated_before_the_next_term_and_reads_nothing_later() -> None:
    lineups = _record(2022) + _record(2023)
    table = estimated_positions(lineups, first_term=2022, last_term=2023)
    assert [r.published for r in table.releases] == [date(2023, 9, 30), date(2024, 9, 30)]
    # OT2023 out of sample reads OT2022's positions, fitted on OT2022 alone.
    assert table.prior_bench(2023) == pytest.approx(term_positions(_record(2022), 2022))
    assert table.bench(2023) == pytest.approx(term_positions(lineups, 2023))
    assert table.source.startswith("estimated")


def test_the_cli_prints_each_terms_bench(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    db = corpus.corpus_db_path(root)
    db.parent.mkdir(parents=True)
    with corpus.connect(db):
        pass
    result = runner.invoke(
        app, ["alignment-positions", "--first-term", "2024", "--last-term", "2025"]
    )
    assert result.exit_code == 0, result.output
    assert "OT2025: no bench placed" in result.output
    printed = result.stdout.strip().splitlines()[-1]
    table = json.loads(printed)
    assert len(table["releases"]) == 2
    # The printed table is the `--positions` shape the score readout reads.
    assert JusticePositions.model_validate_json(printed).source.startswith("estimated")
    reversed_range = runner.invoke(
        app, ["alignment-positions", "--first-term", "2025", "--last-term", "2024"]
    )
    assert reversed_range.exit_code == 2


def _absent(lineups: list[MeritsLineup], justice: str, keep: range) -> list[MeritsLineup]:
    """``lineups`` with ``justice`` recused outside the decisions indexed by ``keep``."""
    return [
        lu
        if i in keep
        else lu.model_copy(
            update={
                "votes": [
                    v.model_copy(update={"vote": R}) if v.justice == justice else v
                    for v in lu.votes
                ]
            }
        )
        for i, lu in enumerate(lineups)
    ]


def test_the_line_is_turned_so_the_conservative_bloc_sits_higher(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = alignment_positions.classical_scaling
    plain = term_positions(_record(2023), 2023)
    monkeypatch.setattr(alignment_positions, "classical_scaling", lambda d: [-x for x in real(d)])
    # Whatever sign the scaling lands on, the orientation puts the bloc above.
    assert term_positions(_record(2023), 2023) == pytest.approx(plain)
    assert plain["Thomas"] > 0


def test_a_thinly_shared_pair_drops_the_justice_with_fewer_decisions() -> None:
    record = _record(2023)  # fifty decisions
    record = _absent(record, "Kagan", range(25, 50))
    record = _absent(record, "Jackson", range(0, 20))
    placed = term_positions(record, 2023)
    # Each clears the 20-decision floor, but the two share no decision.
    assert "Kagan" in placed
    assert "Jackson" not in placed


def test_the_window_reaches_back_to_its_first_term() -> None:
    edge = 2023 - WINDOW_TERMS + 1
    early = [
        lu.model_copy(update={"listing_number": f"e{lu.listing_number}"}) for lu in _record(edge)
    ]
    unanimous = [
        lu.model_copy(update={"votes": [v.model_copy(update={"vote": M}) for v in lu.votes]})
        for lu in early
    ]
    assert term_positions(_record(2023) + early, 2023) != pytest.approx(
        term_positions(_record(2023) + unanimous, 2023)
    )


def test_a_terms_own_decisions_never_reach_its_out_of_sample_positions() -> None:
    before = _record(2021) + _record(2022)
    after = [
        *before,
        *(
            lu.model_copy(update={"listing_number": f"n{lu.listing_number}"})
            for lu in _record(2023)
        ),
    ]
    through_2022 = estimated_positions(before, first_term=2021, last_term=2022)
    through_2023 = estimated_positions(after, first_term=2021, last_term=2023)
    assert through_2023.prior_bench(2023) == pytest.approx(through_2022.prior_bench(2023))
