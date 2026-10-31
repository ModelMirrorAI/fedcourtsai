from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import merits_lineups
from fedcourtsai.pipeline.alignment_score import (
    K_GRID,
    MIN_FIT_DECISIONS,
    JusticePositions,
    PositionsRelease,
    brier,
    conservative_prevailed,
    consolidated_duplicates,
    fit_calibration,
    fit_spread,
    outcome_cases,
    predicted_conservative,
    read_vote_decision,
    score_readout,
    standardize,
    vote_cases,
    vote_probability,
)
from fedcourtsai.pipeline.merits_lineups import MeritsLineup
from fedcourtsai.schemas import (
    AlignmentCodeMode,
    AlignmentSide,
    AlignmentSideCode,
    AlignmentSideCodes,
    AlignmentValence,
    Judgment,
    VoteValue,
)

from .test_justice_priors import _lineup

runner = CliRunner()

M, D, P = VoteValue.majority, VoteValue.dissent, VoteValue.concur_in_part
CONSERVATIVES = ("Roberts", "Thomas", "Alito", "Gorsuch", "Kavanaugh", "Barrett")
LIBERALS = ("Sotomayor", "Kagan", "Jackson")
#: A published-looking ordering: the six conservatives above the three others.
BENCH = {
    "Thomas": 3.0,
    "Alito": 2.5,
    "Gorsuch": 1.5,
    "Kavanaugh": 0.6,
    "Barrett": 0.5,
    "Roberts": 0.4,
    "Kagan": -1.5,
    "Sotomayor": -2.5,
    "Jackson": -2.6,
}


def _positions(
    terms: dict[int, dict[str, float]], published: date = date(2020, 8, 1)
) -> JusticePositions:
    return JusticePositions(
        source="test", releases=[PositionsRelease(published=published, terms=terms)]
    )


def _code(
    n: int,
    *,
    score: float,
    side: AlignmentSide = AlignmentSide.petitioner,
    replay: bool = True,
    term: int = 2023,
) -> AlignmentSideCode:
    granted = date(term, 11, 1)
    return AlignmentSideCode(
        case_id=f"scotus/{n}",
        docket_number=f"{term % 100}-{n}",
        granted=granted,
        conservative_side=side,
        score=score,
        valence=AlignmentValence.clear,
        note="Test.",
        mode=AlignmentCodeMode.replay if replay else AlignmentCodeMode.forward,
        contamination_risk=replay,
        model="test-model",
        run_id="1",
        coded_at=date(2026, 10, 31) if replay else granted,
    )


def _bench(**overrides: VoteValue) -> dict[str, VoteValue]:
    votes = {name: M for name in (*CONSERVATIVES, *LIBERALS)}
    votes.update(overrides)
    return votes


def test_the_conservative_side_prevails_on_the_merits_binary() -> None:
    petitioner = _code(1, score=0.7)
    respondent = _code(2, score=0.7, side=AlignmentSide.respondent)
    assert conservative_prevailed(petitioner, Judgment.reversed)
    assert conservative_prevailed(petitioner, Judgment.vacated)
    assert not conservative_prevailed(petitioner, Judgment.affirmed)
    # A DIG and an equally divided Court leave the judgment below standing.
    assert conservative_prevailed(respondent, Judgment.dig)
    assert conservative_prevailed(respondent, Judgment.equally_divided)
    assert not conservative_prevailed(respondent, Judgment.affirmed_in_part)


def test_outcome_cases_key_on_the_decision_term_and_skip_the_undecided() -> None:
    codes = [_code(1, score=0.8), _code(2, score=0.3)]
    judgments = {"scotus/1": (Judgment.reversed, date(2024, 6, 20))}
    [case] = outcome_cases(codes, judgments)
    assert case.case_id == "scotus/1"
    assert case.term == 2023
    assert case.conservative_prevailed


def test_brier_is_the_mean_squared_error() -> None:
    assert brier([(0.8, True), (0.4, False)]) == pytest.approx((0.04 + 0.16) / 2)
    assert brier([]) is None


def test_the_calibration_is_monotone_and_pools_violators() -> None:
    assert fit_calibration([(0.5, True)] * (MIN_FIT_DECISIONS - 1)) is None
    points = (
        [(0.2, False)] * 10 + [(0.4, True)] * 6 + [(0.4, False)] * 4 + [(0.6, False)] * 10
    ) + [(0.9, True)] * 10
    calibration = fit_calibration(points)
    assert calibration is not None
    # 0.4 (rate 0.6) and 0.6 (rate 0) violate monotonicity and pool to 6/20,
    # and every block's rate is shrunk by one success and one failure.
    assert calibration.apply(0.2) == pytest.approx(1 / 12)
    assert calibration.apply(0.4) == pytest.approx(7 / 22)
    assert calibration.apply(0.6) == pytest.approx(7 / 22)
    assert calibration.apply(0.95) == pytest.approx(11 / 12)
    assert calibration.apply(0.0) == pytest.approx(1 / 12)
    rates = [rate for _, rate in calibration.knots]
    assert rates == sorted(rates)


def test_a_zero_spread_calls_every_justice_the_same_way() -> None:
    z = standardize(BENCH)
    assert z["Barrett"] == 0.0  # the median Justice sits at the center
    assert set(predicted_conservative(0.7, z, 0.0).values()) == {True}
    assert set(predicted_conservative(0.3, z, 0.0).values()) == {False}


def test_a_large_spread_splits_the_bench_along_the_ordering() -> None:
    z = standardize(BENCH)
    sides = predicted_conservative(0.7, z, K_GRID[-1])
    assert {j for j, side in sides.items() if side} == set(CONSERVATIVES)
    # A low score moves the cut into the conservatives.
    low = predicted_conservative(0.2, z, 2.0)
    assert sides != low
    assert sum(low.values()) < 6


def test_vote_probability_is_finite_at_the_edges() -> None:
    assert 0 < vote_probability(0.0, -3.0, 8.0) < 1
    assert 0 < vote_probability(1.0, 3.0, 8.0) <= 1


def test_the_vote_reading_is_relative_to_the_predicted_judgment() -> None:
    lineup = _lineup(2023, "1", _bench(Sotomayor=D, Kagan=D, Jackson=D), case_id="scotus/1")
    codes = [_code(1, score=0.7)]
    outcomes = outcome_cases(codes, {"scotus/1": (Judgment.reversed, date(2024, 6, 1))})
    [case] = vote_cases([lineup], outcomes, codes)
    z = standardize(BENCH)
    ideological = read_vote_decision(case, predicted_conservative(0.7, z, K_GRID[-1]))
    assert ideological.justice_hits == 9
    assert ideological.exact_split and ideological.full_coalition
    unanimous = read_vote_decision(case, predicted_conservative(0.7, z, 0.0))
    assert unanimous.justice_hits == 6
    assert not unanimous.exact_split
    # Predicting the liberal side 6-3 the other way still reads relative to the judgment:
    # the predicted majority is the three plus three, the coalition misses.
    flipped = {j: j in (*LIBERALS, "Roberts", "Barrett", "Kavanaugh") for j in BENCH}
    reading = read_vote_decision(case, flipped)
    assert reading.exact_split and not reading.full_coalition


def test_a_vote_in_part_is_a_miss_and_bars_split_and_coalition() -> None:
    lineup = _lineup(2023, "1", _bench(Kagan=P), case_id="scotus/1")
    codes = [_code(1, score=0.7)]
    outcomes = outcome_cases(codes, {"scotus/1": (Judgment.reversed, date(2024, 6, 1))})
    [case] = vote_cases([lineup], outcomes, codes)
    reading = read_vote_decision(case, predicted_conservative(0.7, standardize(BENCH), 0.0))
    assert reading.justice_hits == 8
    assert not reading.exact_split and not reading.full_coalition


def test_a_lineup_joins_on_its_docket_when_it_has_no_case_link() -> None:
    lineup = _lineup(2023, "7", _bench())
    codes = [_code(7, score=0.6)]
    outcomes = outcome_cases(codes, {"scotus/7": (Judgment.reversed, date(2024, 6, 1))})
    assert [c.case_id for c in vote_cases([lineup], outcomes, codes)] == ["scotus/7"]


def _record(n: int, *, ideological: bool, term: int) -> tuple[AlignmentSideCode, MeritsLineup]:
    """A case coded 0.8 whose conservative petitioner wins, 6-3 or 9-0."""
    code = _code(n, score=0.8, term=term)
    votes = _bench(Sotomayor=D, Kagan=D, Jackson=D) if ideological else _bench()
    return code, _lineup(term, str(n), votes, case_id=code.case_id)


def test_the_spread_fit_follows_the_record() -> None:
    z = standardize(BENCH)
    conservative = {j: j in CONSERVATIVES for j in BENCH}
    unanimous = dict.fromkeys(BENCH, True)
    assert fit_spread([(0.8, z, conservative)] * (MIN_FIT_DECISIONS - 1)) is None
    assert fit_spread([(0.8, z, unanimous)] * MIN_FIT_DECISIONS) == 0.0
    spread = fit_spread([(0.8, z, conservative)] * MIN_FIT_DECISIONS)
    assert spread is not None and spread >= 4


def test_the_readout_fits_out_of_sample_on_earlier_terms_only() -> None:
    codes: list[AlignmentSideCode] = []
    lineups: list[MeritsLineup] = []
    judgments: dict[str, tuple[Judgment, date]] = {}
    for n in range(1, 41):  # OT2022: ideological 6-3s
        code, lineup = _record(n, ideological=True, term=2022)
        codes.append(code)
        lineups.append(lineup)
        judgments[code.case_id] = (Judgment.reversed, date(2023, 6, 1))
    for n in range(41, 81):  # OT2023: unanimous
        code, lineup = _record(n, ideological=False, term=2023)
        codes.append(code)
        lineups.append(lineup)
        judgments[code.case_id] = (Judgment.reversed, date(2024, 6, 1))
    codes.sort(key=lambda c: c.case_id)
    positions = _positions({2021: BENCH, 2022: BENCH, 2023: BENCH})
    readout = score_readout(
        codes, judgments, lineups, first_term=2022, last_term=2023, positions=positions
    )
    [ot2023, ot2022] = readout.terms
    assert ot2023.term == 2023
    assert ot2023.outcome.decisions == 40
    assert ot2023.outcome.call_hits == 40
    assert ot2023.outcome.brier_raw == pytest.approx(0.04)
    # The transform fitted on OT2022's 40 won codes maps 0.8 to 41/42.
    assert ot2023.outcome.brier_calibrated_out_of_sample == pytest.approx((1 / 42) ** 2)
    assert ot2023.outcome.fit_out_of_sample is not None
    assert ot2023.outcome.fit_out_of_sample.contamination_risk == 40
    out, inside = ot2023.votes_out_of_sample, ot2023.votes_in_sample
    assert out is not None and inside is not None
    # Fitted on OT2022's 6-3s, the out-of-sample spread predicts 6-3s for a unanimous Term,
    assert out.k is not None and out.k >= 4
    assert out.justice_hits == 6 * 40
    # while the in-sample ceiling fits the Term's own 9-0s.
    assert inside.k == 0.0
    assert inside.justice_hits == 9 * 40
    # OT2022 has no earlier Term to fit on.
    assert ot2022.outcome.brier_calibrated_out_of_sample is None
    assert ot2022.votes_out_of_sample is not None and ot2022.votes_out_of_sample.k is None


def test_a_bench_with_no_position_for_a_justice_is_not_read() -> None:
    code, lineup = _record(1, ideological=True, term=2023)
    partial = {j: x for j, x in BENCH.items() if j != "Jackson"}
    readout = score_readout(
        [code],
        {code.case_id: (Judgment.reversed, date(2024, 6, 1))},
        [lineup],
        first_term=2023,
        last_term=2023,
        positions=_positions({2022: partial, 2023: partial}),
    )
    [term] = readout.terms
    assert term.lineups == 1
    assert term.votes_in_sample is not None and term.votes_in_sample.decisions == 0


def test_the_cli_scores_baseline_three_without_positions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = tmp_path / "data"
    codes_file = data / "merits-alignment" / "alignment-side-codes.json"
    codes_file.parent.mkdir(parents=True)
    codes_file.write_text(
        AlignmentSideCodes(entries=[_code(1, score=0.8)]).model_dump_json(indent=2)
    )
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    db = corpus.corpus_db_path(root)
    db.parent.mkdir(parents=True)
    with corpus.connect(db):
        pass
    result = runner.invoke(app, ["alignment-score-baseline", "--first-term", "2023"])
    assert result.exit_code == 0, result.output
    readout = json.loads(result.stdout.strip().splitlines()[-1])
    assert readout["codes"] == 1
    assert readout["positions_source"] is None


def test_the_cli_refuses_a_missing_codes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    result = runner.invoke(app, ["alignment-score-baseline"])
    assert result.exit_code == 1
    assert "no side codes" in result.output


def test_the_cli_refuses_a_reversed_range_and_an_unreadable_positions_file(
    tmp_path: Path,
) -> None:
    reversed_range = runner.invoke(
        app, ["alignment-score-baseline", "--first-term", "2025", "--last-term", "2024"]
    )
    assert reversed_range.exit_code == 2
    bad = tmp_path / "positions.json"
    bad.write_text(json.dumps({"source": "test", "releases": []}))
    unreadable = runner.invoke(app, ["alignment-score-baseline", "--positions", str(bad)])
    assert unreadable.exit_code == 2
    assert "positions.json" in unreadable.output


def test_positions_read_with_string_term_keys() -> None:
    table = JusticePositions.model_validate_json(
        json.dumps(
            {"source": "test", "releases": [{"published": "2025-08-01", "terms": {"2024": BENCH}}]}
        )
    )
    assert table.bench(2024) == BENCH


def test_a_decision_two_lineups_resolve_to_is_read_once() -> None:
    code, lineup = _record(1, ideological=True, term=2023)
    twin = lineup.model_copy(update={"listing_number": "1a"})
    outcomes = outcome_cases([code], {code.case_id: (Judgment.reversed, date(2024, 6, 1))})
    assert len(vote_cases([lineup, twin], outcomes, [code])) == 1


def test_out_of_sample_fits_read_terms_before_the_scored_range() -> None:
    codes: list[AlignmentSideCode] = []
    lineups: list[MeritsLineup] = []
    judgments: dict[str, tuple[Judgment, date]] = {}
    for n in range(1, 41):
        code, lineup = _record(n, ideological=True, term=2022)
        codes.append(code)
        lineups.append(lineup)
        judgments[code.case_id] = (Judgment.reversed, date(2023, 6, 1))
    code, lineup = _record(99, ideological=True, term=2023)
    codes.append(code)
    lineups.append(lineup)
    judgments[code.case_id] = (Judgment.reversed, date(2024, 6, 1))
    codes.sort(key=lambda c: c.case_id)
    readout = score_readout(
        codes,
        judgments,
        lineups,
        first_term=2023,
        last_term=2023,
        positions=_positions({2021: BENCH, 2022: BENCH}),
    )
    [term] = readout.terms
    assert term.outcome.brier_calibrated_out_of_sample is not None
    assert term.votes_out_of_sample is not None and term.votes_out_of_sample.k is not None


def test_the_smoothed_transform_stays_monotone_over_blocks_of_unequal_size() -> None:
    points = [(0.1, False)] + [(0.2, True)] + [(0.2, False)] * 9
    points += [(0.3, True)] * 5 + [(0.3, False)] * 14
    calibration = fit_calibration(points)
    assert calibration is not None
    rates = [calibration.apply(s) for s in (0.1, 0.2, 0.3)]
    assert rates == sorted(rates)


def test_out_of_sample_positions_come_only_from_a_release_before_the_term() -> None:
    early = PositionsRelease(published=date(2023, 8, 1), terms={2022: BENCH})
    late = PositionsRelease(published=date(2025, 8, 1), terms={2022: {"Thomas": 9.0}, 2024: BENCH})
    table = JusticePositions(source="test", releases=[early, late])
    # OT2023 opened after the early release and before the late one.
    assert table.prior_bench(2023) == BENCH
    assert table.prior_bench(2022) is None
    assert table.bench(2024) == BENCH


def test_a_predicted_tie_on_an_even_bench_goes_to_the_respondent() -> None:
    votes = {name: M for name in (*CONSERVATIVES[:4], *LIBERALS, "Barrett")}
    votes.update(Sotomayor=D, Kagan=D, Jackson=D, Barrett=D)
    lineup = _lineup(2023, "1", votes, case_id="scotus/1")
    code = _code(1, score=0.5, side=AlignmentSide.respondent)
    outcomes = outcome_cases([code], {"scotus/1": (Judgment.affirmed, date(2024, 6, 1))})
    [case] = vote_cases([lineup], outcomes, [code])
    tie = {j: j in CONSERVATIVES[:4] for j in votes}
    # The conservative respondent wins the predicted 4-4, so its four are with the judgment.
    assert read_vote_decision(case, tie).full_coalition


def test_a_consolidated_decision_is_read_once_under_one_code() -> None:
    first, second = _code(1, score=0.8), _code(2, score=0.2, side=AlignmentSide.respondent)
    lineup = _lineup(2023, "1", _bench()).model_copy(
        update={"dockets": [first.docket_number, second.docket_number], "status": "per-curiam"}
    )
    assert consolidated_duplicates([lineup], [first, second]) == {second.case_id}
    # A decided docket is kept before an undecided one listed ahead of it.
    assert consolidated_duplicates([lineup], [first, second], {second.case_id}) == {first.case_id}
    readout = score_readout(
        [first, second],
        {c.case_id: (Judgment.reversed, date(2024, 6, 1)) for c in (first, second)},
        [lineup],
        first_term=2023,
        last_term=2023,
    )
    assert readout.decided == 1
    assert readout.consolidated == 1


def test_the_cli_reads_lineups_from_the_first_coded_decision_term(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = tmp_path / "data"
    codes_file = data / "merits-alignment" / "alignment-side-codes.json"
    codes_file.parent.mkdir(parents=True)
    code = _code(1, score=0.8, term=2021)
    codes_file.write_text(AlignmentSideCodes(entries=[code]).model_dump_json(indent=2))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    db = corpus.corpus_db_path(root)
    db.parent.mkdir(parents=True)
    with corpus.connect(db):
        pass
    rows = [
        SimpleNamespace(
            case_id=code.case_id, merits_judgment="reversed", merits_decided=date(2022, 6, 1)
        ),
        SimpleNamespace(
            case_id=code.case_id, merits_judgment="garbled", merits_decided=date(2022, 6, 1)
        ),
    ]
    monkeypatch.setattr(corpus, "iter_rows", lambda *_a, **_k: iter(rows))
    seen: dict[str, int] = {}

    def fake_lineups(_conn: object, *, first_term: int, last_term: int) -> list[MeritsLineup]:
        seen.update(first_term=first_term, last_term=last_term)
        return []

    monkeypatch.setattr(merits_lineups, "merits_lineups", fake_lineups)
    result = runner.invoke(
        app, ["alignment-score-baseline", "--first-term", "2024", "--last-term", "2025"]
    )
    assert result.exit_code == 0, result.output
    # Scored from OT2024, fitted from OT2021, the Term the coded case was decided in.
    assert seen == {"first_term": 2021, "last_term": 2025}
    # A judgment outside the vocabulary is counted and left out, not fatal.
    assert "1 with a judgment outside the vocabulary" in result.output
