from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.alignment_baseline import (
    CONSERVATIVE_BLOC,
    alignment_readout,
    predicted_sides,
    read_decision,
    roster_is_partitioned,
)
from fedcourtsai.schemas import VoteValue

from .test_justice_priors import _lineup

runner = CliRunner()

M, J, D, P = (
    VoteValue.majority,
    VoteValue.concur_in_judgment,
    VoteValue.dissent,
    VoteValue.concur_in_part,
)
R = VoteValue.recused

CONSERVATIVES = ("Roberts", "Thomas", "Alito", "Gorsuch", "Kavanaugh", "Barrett")
LIBERALS = ("Sotomayor", "Kagan", "Jackson")


def _bench(**overrides: VoteValue) -> dict[str, VoteValue]:
    votes = {name: M for name in (*CONSERVATIVES, *LIBERALS)}
    votes.update(overrides)
    return votes


def _ideological() -> dict[str, VoteValue]:
    return _bench(Sotomayor=D, Kagan=D, Jackson=D)


def test_every_justice_on_the_roster_sits_in_exactly_one_bloc() -> None:
    assert roster_is_partitioned()
    assert set(CONSERVATIVES) <= CONSERVATIVE_BLOC
    assert not set(LIBERALS) & CONSERVATIVE_BLOC


def test_a_justice_neither_bloc_names_is_refused() -> None:
    with pytest.raises(ValueError, match="no bloc"):
        predicted_sides("unanimity", ["Roberts", "Nobody"])


def test_an_ideological_six_three_is_a_full_hit_for_alignment_only() -> None:
    lineup = _lineup(2025, "1", _ideological())
    alignment = read_decision("majority-alignment", lineup)
    assert alignment.participating == 9
    assert alignment.justice_hits == 9
    assert alignment.exact_split and alignment.full_coalition
    unanimity = read_decision("unanimity", lineup)
    assert unanimity.justice_hits == 6
    assert not unanimity.exact_split and not unanimity.full_coalition


def test_a_unanimous_decision_is_a_full_hit_for_unanimity_only() -> None:
    lineup = _lineup(2025, "1", _bench(Kagan=J))  # a concurrence in the judgment sides with it
    assert read_decision("unanimity", lineup).justice_hits == 9
    assert read_decision("unanimity", lineup).full_coalition
    alignment = read_decision("majority-alignment", lineup)
    assert alignment.justice_hits == 6
    assert not alignment.exact_split


def test_a_crossover_six_three_is_an_exact_split_but_not_the_coalition() -> None:
    # The winning side is liberal: three conservatives in dissent.
    lineup = _lineup(2025, "1", _bench(Thomas=D, Alito=D, Gorsuch=D))
    alignment = read_decision("majority-alignment", lineup)
    assert alignment.exact_split
    assert not alignment.full_coalition
    assert alignment.justice_hits == 3  # Roberts, Kavanaugh, Barrett


def test_a_vote_in_part_is_a_miss_and_breaks_split_and_coalition() -> None:
    lineup = _lineup(2025, "1", _bench(Sotomayor=D, Kagan=D, Jackson=P))
    alignment = read_decision("majority-alignment", lineup)
    assert alignment.justice_hits == 8
    assert not alignment.exact_split and not alignment.full_coalition


def test_a_justice_who_took_no_part_leaves_the_denominator() -> None:
    lineup = _lineup(2025, "1", _bench(Barrett=R, Sotomayor=D, Kagan=D, Jackson=D))
    alignment = read_decision("majority-alignment", lineup)
    assert alignment.participating == 8
    assert alignment.justice_hits == 8
    assert alignment.full_coalition


def test_only_a_complete_lineup_is_read() -> None:
    with pytest.raises(ValueError, match="not a complete lineup"):
        read_decision("unanimity", _lineup(2025, "1", {}, status="per-curiam"))


def test_the_readout_pools_terms_and_counts_the_realized_shape() -> None:
    lineups = [
        _lineup(2025, "1", _ideological()),
        _lineup(2025, "2", _bench()),
        _lineup(2025, "3", {}, status="per-curiam"),
        _lineup(2024, "1", _bench(Thomas=D, Alito=D, Gorsuch=D)),
        _lineup(2021, "1", _bench()),  # outside the range
    ]
    readout = alignment_readout(lineups, first_term=2024, last_term=2025)
    assert [t.term for t in readout.terms] == [2025, 2024]
    ot2025 = readout.terms[0]
    assert (ot2025.documents, ot2025.decisions) == (3, 2)
    assert (ot2025.unanimous, ot2025.bloc_coalition, ot2025.with_other_bloc) == (1, 1, 1)
    pooled = readout.pooled
    assert pooled.decisions == 3
    alignment, unanimity = pooled.readings
    assert alignment.baseline == "majority-alignment"
    assert (alignment.justice_votes, alignment.justice_hits) == (27, 9 + 6 + 3)
    assert alignment.exact_split_hits == 2
    assert alignment.full_coalition_hits == 1
    assert alignment.full_coalition_accuracy == pytest.approx(1 / 3)
    assert (unanimity.justice_hits, unanimity.exact_split_hits) == (6 + 9 + 6, 1)


def test_an_empty_range_has_no_rates() -> None:
    readout = alignment_readout([], first_term=2024, last_term=2025)
    assert readout.terms == []
    assert all(r.justice_accuracy is None for r in readout.pooled.readings)


def test_the_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    assert runner.invoke(app, ["merits-alignment-baseline"]).exit_code == 1  # no corpus yet
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass
    result = runner.invoke(app, ["merits-alignment-baseline", "--first-term", "2024"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert (payload["first_term"], payload["last_term"]) == (2024, 2025)
    assert payload["terms"] == []
    lineups = [_lineup(2025, "1", _ideological()), _lineup(2024, "1", _bench())]
    monkeypatch.setattr("fedcourtsai.cli.merits_lineups.merits_lineups", lambda conn, **_: lineups)
    result = runner.invoke(app, ["merits-alignment-baseline", "--first-term", "2024"])
    assert result.exit_code == 0, result.output
    assert "OT2025: 1 of 1 documents with a complete lineup; 0 unanimous, 1 bloc coalition" in (
        result.stderr
    )
    assert "OT2024-OT2025: 2 of 2" in result.stderr
    assert "majority-alignment: justice 83.3% (15/18)" in result.stderr
    backwards = ["merits-alignment-baseline", "--first-term", "2025", "--last-term", "2024"]
    assert runner.invoke(app, backwards).exit_code == 2
