from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai.leaderboard import (
    CellSkill,
    VoteScore,
    _evaluation_key,
    build_leaderboard,
    skill_components,
    stage_moment_key,
    vote_scores,
)
from fedcourtsai.pipeline.alignment_board import AlignmentInputs, load_inputs, read_cell
from fedcourtsai.pipeline.alignment_fits import fits_path
from fedcourtsai.pipeline.alignment_side import codes_path
from fedcourtsai.pipeline.moments import first_moment
from fedcourtsai.schemas import (
    AlignmentCodeMode,
    AlignmentFits,
    AlignmentSide,
    AlignmentSideCode,
    AlignmentSideCodes,
    AlignmentTermFit,
    AlignmentValence,
    Disposition,
    Judgment,
    JusticeVote,
    Outcome,
    Stage,
    VoteProvenance,
    VoteValue,
)
from fedcourtsai.serialize import write_json

from .test_alignment_score import BENCH
from .test_leaderboard import (
    _MERITS_EVENT_ID,
    _SITTING,
    _evaluation,
    _forward,
    _write_voting_cell,
)

DECIDED = date(2026, 6, 23)  # an OT2025 decision, as the leaderboard fixtures resolve


def _code(case_id: str = "scotus/1", **changes: object) -> AlignmentSideCode:
    fields: dict[str, object] = {
        "case_id": case_id,
        "docket_number": "25-1",
        "granted": date(2025, 11, 1),
        "conservative_side": AlignmentSide.petitioner,
        "score": 0.8,
        "valence": AlignmentValence.clear,
        "note": "Test.",
        "mode": AlignmentCodeMode.forward,
        "contamination_risk": False,
        "model": "test-model",
        "run_id": "1",
        "coded_at": date(2025, 11, 5),
    }
    fields.update(changes)
    return AlignmentSideCode.model_validate(fields)


def _fit(**changes: object) -> AlignmentTermFit:
    fields: dict[str, object] = {
        "term": 2025,
        "opened": date(2025, 10, 1),
        "frozen_on": date(2025, 9, 15),
        "codes_digest": "0" * 64,
        "latest_decision_read": date(2025, 6, 27),
        "transform": [[0.0, 0.2], [0.75, 0.9]],
        "transform_decisions": 40,
        "k": 0.0,
        "k_decisions": 40,
        "k_at_grid_edge": False,
        "consolidated": 0,
        "positions": BENCH,
        "positions_source": "test",
        "contamination_risk": 10,
    }
    fields.update(changes)
    return AlignmentTermFit.model_validate(fields)


def _outcome(case_id: str = "scotus/1", *, disturbed: int = 1) -> Outcome:
    votes = [JusticeVote(justice=name, vote=VoteValue.majority) for name in _SITTING]
    votes.append(JusticeVote(justice="Jackson", vote=VoteValue.did_not_participate))
    return Outcome(
        case_id=case_id,
        event_id=_MERITS_EVENT_ID,
        resolved_at=DECIDED,
        actual_disposition=Disposition.other,
        actual_granted=disturbed,
        judgment=Judgment.reversed if disturbed else Judgment.affirmed,
        votes=votes,
        vote_provenance=VoteProvenance(
            source="supremecourt-opinions", participating=8, complete=True
        ),
    )


def _inputs(
    code: AlignmentSideCode | None = None, fit: AlignmentTermFit | None = None
) -> AlignmentInputs:
    code = code or _code()
    fit = fit or _fit()
    return AlignmentInputs(codes={code.case_id: code}, fits={fit.term: fit})


def test_baseline_three_reads_the_transform_as_p_disturbed() -> None:
    reading = read_cell(_inputs(), _outcome(), votes_complete=True)
    assert reading is not None
    # 0.8 maps to the 0.75 block's 0.9; a conservative petitioner prevailing is disturbed.
    assert reading.brier == pytest.approx(0.1**2)
    assert reading.term == 2025
    assert reading.fit_replay_share == pytest.approx(10 / 40)
    respondent = read_cell(
        _inputs(_code(conservative_side=AlignmentSide.respondent)), _outcome(), votes_complete=True
    )
    assert respondent is not None
    # A conservative respondent prevailing is undisturbed, so P(disturbed) is 0.1.
    assert respondent.brier == pytest.approx(0.9**2)


def test_baseline_four_calls_each_sitting_justice_relative_to_the_predicted_winner() -> None:
    # No spread: every Justice goes with the score, the conservative side, which wins.
    flat = read_cell(_inputs(), _outcome(), votes_complete=True)
    assert flat is not None and flat.vote_accuracy == pytest.approx(1.0)
    # A wide spread splits the bench along the ordering: the two liberals sitting dissent.
    wide = read_cell(_inputs(fit=_fit(k=8.0, k_at_grid_edge=True)), _outcome(), votes_complete=True)
    assert wide is not None and wide.vote_accuracy == pytest.approx(6 / 8)
    # Not read where the board does not vote-score the outcome,
    unscored = read_cell(_inputs(), _outcome(), votes_complete=False)
    assert unscored is not None and unscored.vote_accuracy is None
    # nor without a spread, nor where a sitting Justice has no position.
    no_k = read_cell(_inputs(fit=_fit(k=None)), _outcome(), votes_complete=True)
    assert no_k is not None and no_k.vote_accuracy is None
    partial = {j: x for j, x in BENCH.items() if j != "Kagan"}
    unplaced = read_cell(_inputs(fit=_fit(positions=partial)), _outcome(), votes_complete=True)
    assert unplaced is not None and unplaced.vote_accuracy is None


@pytest.mark.parametrize(
    ("code", "fit"),
    [
        (_code(mode=AlignmentCodeMode.replay, contamination_risk=True), None),
        (_code(coded_at=date(2026, 1, 15)), None),  # past the clean lag
        (_code(granted=date(2026, 6, 1), coded_at=DECIDED), None),  # coded on the decision day
        (None, _fit(frozen_on=DECIDED)),  # fit made on the decision day
        (None, _fit(transform=None, k=None, transform_decisions=0, contamination_risk=0)),
        (None, _fit(term=2024, opened=date(2024, 10, 1), latest_decision_read=None)),
    ],
)
def test_a_reading_that_is_not_pre_registered_is_not_made(
    code: AlignmentSideCode | None, fit: AlignmentTermFit | None
) -> None:
    assert read_cell(_inputs(code, fit), _outcome(), votes_complete=True) is None


def test_an_uncoded_case_has_no_reading() -> None:
    assert read_cell(_inputs(), _outcome("scotus/2"), votes_complete=True) is None


def test_the_board_pairs_each_baseline_with_the_forecasts_over_its_own_cells() -> None:
    a = _evaluation("alpha", case_id="scotus/1", event_id=_MERITS_EVENT_ID, run_id="r1")
    b = _evaluation("alpha", case_id="scotus/2", event_id=_MERITS_EVENT_ID, run_id="r2")
    c = _evaluation("alpha", case_id="scotus/3", event_id=_MERITS_EVENT_ID, run_id="r3")
    cells = [_forward(ev, Stage.merits) for ev in (a, b, c)]
    key = stage_moment_key(Stage.merits, first_moment(Stage.merits))
    skills = {
        _evaluation_key(a): CellSkill(
            brier=0.1, alignment_baseline=0.3, alignment_fit_replay_share=0.5
        ),
        _evaluation_key(b): CellSkill(
            brier=0.2, alignment_baseline=0.1, alignment_fit_replay_share=1.0
        ),
        _evaluation_key(c): CellSkill(brier=0.9),
    }
    votes = {
        _evaluation_key(a): VoteScore(model=0.9, unanimity=1.0, majority_alignment=0.8),
        _evaluation_key(b): VoteScore(
            model=0.5, unanimity=0.6, majority_alignment=0.4, alignment=0.75
        ),
    }
    stratum = (
        build_leaderboard(cells, skills=skills, vote_scores=votes).stages[key].entries[0].forward
    )
    assert stratum is not None
    assert stratum.alignment_score_cells == 2
    assert stratum.alignment_score_brier == pytest.approx(0.2)
    # The forecasts' Brier over the same two cells, not the stratum's three.
    assert stratum.alignment_score_model_brier == pytest.approx(0.15)
    assert stratum.alignment_fit_replay_share == pytest.approx(0.75)
    assert stratum.alignment_vote_cells == 1
    assert stratum.alignment_vote_accuracy == pytest.approx(0.75)
    assert stratum.alignment_vote_model_accuracy == pytest.approx(0.5)


def test_a_board_with_no_reading_serializes_no_alignment_field() -> None:
    a = _evaluation("alpha", case_id="scotus/1", event_id=_MERITS_EVENT_ID, run_id="r1")
    key = stage_moment_key(Stage.merits, first_moment(Stage.merits))
    stratum = build_leaderboard([_forward(a, Stage.merits)]).stages[key].entries[0].forward
    assert stratum is not None
    assert not any(name.startswith("alignment_") for name in stratum.model_dump(mode="json"))


def _commit(data_root: Path, code: AlignmentSideCode, fit: AlignmentTermFit) -> None:
    write_json(codes_path(data_root), AlignmentSideCodes(entries=[code]))
    write_json(fits_path(data_root), AlignmentFits(entries=[fit]))


def test_the_board_reads_the_committed_codes_and_fits(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    ev = _evaluation("alpha", case_id="scotus/1", event_id=_MERITS_EVENT_ID, prediction_run_id="p1")
    full = [JusticeVote(justice=n, vote=VoteValue.majority) for n in _SITTING]
    _write_voting_cell(data_root, ev, predicted=full, complete=True)
    cells = [_forward(ev, Stage.merits)]
    assert load_inputs(data_root) is None
    assert vote_scores(cells, data_root)[_evaluation_key(ev)].alignment is None
    assert _evaluation_key(ev) not in skill_components(cells, data_root, None)
    _commit(data_root, _code(), _fit())
    assert vote_scores(cells, data_root)[_evaluation_key(ev)].alignment == pytest.approx(1.0)
    skill = skill_components(cells, data_root, None)[_evaluation_key(ev)]
    assert skill.alignment_baseline == pytest.approx(0.1**2)
    assert skill.prior_term_baseline is None


def test_a_fit_made_after_the_decision_is_not_read_by_the_board(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    ev = _evaluation("alpha", case_id="scotus/1", event_id=_MERITS_EVENT_ID, prediction_run_id="p1")
    full = [JusticeVote(justice=n, vote=VoteValue.majority) for n in _SITTING]
    _write_voting_cell(data_root, ev, predicted=full, complete=True)
    _commit(data_root, _code(), _fit(frozen_on=date(2026, 11, 3)))
    cells = [_forward(ev, Stage.merits)]
    assert vote_scores(cells, data_root)[_evaluation_key(ev)].alignment is None
    assert _evaluation_key(ev) not in skill_components(cells, data_root, None)
