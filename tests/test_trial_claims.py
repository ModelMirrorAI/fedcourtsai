"""The trial stage's claim sets and its correctness rule.

Declared with the stage's moments and reachable only through a trial event
id: a headline binary per set, categorical distributions over the outcome's
own labels, no baseline (so nothing is scored under the registered rule), and
``correct`` on the stage's binary.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, get_args

import pytest

from fedcourtsai.pipeline import claims as claims_module
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.claims import (
    CLAIM_SET_TRIAL_DISMISSAL_V1,
    CLAIM_SET_TRIAL_JUDGMENT_V1,
    CLAIM_SET_TRIAL_MOTION_V1,
    CLAIM_TRIAL_JUDGMENT,
    CLAIM_TRIAL_JUDGMENT_FOR_PLAINTIFF,
    CLAIM_TRIAL_LEAVE,
    CLAIM_TRIAL_RULING,
    CLAIM_TRIAL_RULING_GRANTED,
    DISTRIBUTION_CLAIMS,
    claim_block_problems,
    declared_claim_set,
    declared_claim_set_for,
    declared_distribution_claims,
    declared_distribution_claims_for,
    distribution_problems,
    score_claims,
    trial_headline_problems,
)
from fedcourtsai.pipeline.evaluate import is_correct, scored_granted
from fedcourtsai.pipeline.runner import StubRunner
from fedcourtsai.schemas import (
    ClaimDistribution,
    ClaimProbability,
    Disposition,
    Engine,
    Moment,
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
    TrialJudgmentLabel,
    TrialLeaveLabel,
    TrialRulingLabel,
)

_DISMISSAL = "evt-motion-trial-dismissal-45"
_CLASS = "evt-motion-trial-class-90"
_JUDGMENT = "evt-order-trial-judgment"

_RULINGS = get_args(TrialRulingLabel)
_LEAVES = get_args(TrialLeaveLabel)
_JUDGMENTS = get_args(TrialJudgmentLabel)

# --- the declaration ------------------------------------------------------------


def test_the_set_constants_are_the_moment_table_s() -> None:
    assert CLAIM_SET_TRIAL_MOTION_V1 == moments.CLAIM_SET_TRIAL_MOTION_V1
    assert CLAIM_SET_TRIAL_DISMISSAL_V1 == moments.CLAIM_SET_TRIAL_DISMISSAL_V1
    assert CLAIM_SET_TRIAL_JUDGMENT_V1 == moments.CLAIM_SET_TRIAL_JUDGMENT_V1


@pytest.mark.parametrize(
    ("moment", "entry", "version", "binary", "distributions"),
    [
        (
            Moment.trial_dismissal,
            45,
            CLAIM_SET_TRIAL_DISMISSAL_V1,
            CLAIM_TRIAL_RULING_GRANTED,
            (CLAIM_TRIAL_RULING, CLAIM_TRIAL_LEAVE),
        ),
        (
            Moment.trial_class,
            90,
            CLAIM_SET_TRIAL_MOTION_V1,
            CLAIM_TRIAL_RULING_GRANTED,
            (CLAIM_TRIAL_RULING,),
        ),
        (
            Moment.trial_summary_judgment,
            7,
            CLAIM_SET_TRIAL_MOTION_V1,
            CLAIM_TRIAL_RULING_GRANTED,
            (CLAIM_TRIAL_RULING,),
        ),
        (
            Moment.trial_preliminary_injunction,
            3,
            CLAIM_SET_TRIAL_MOTION_V1,
            CLAIM_TRIAL_RULING_GRANTED,
            (CLAIM_TRIAL_RULING,),
        ),
        (
            Moment.trial_judgment,
            None,
            CLAIM_SET_TRIAL_JUDGMENT_V1,
            CLAIM_TRIAL_JUDGMENT_FOR_PLAINTIFF,
            (CLAIM_TRIAL_JUDGMENT,),
        ),
    ],
)
def test_each_trial_moment_declares_its_set(
    moment: Moment,
    entry: int | None,
    version: str,
    binary: str,
    distributions: tuple[str, ...],
) -> None:
    event_id = moments.trial_event_id(moment, entry)
    assert declared_claim_set(event_id) == (version, (binary,))
    assert declared_distribution_claims(event_id) == distributions


def test_every_trial_spec_names_a_set_the_claims_module_resolves() -> None:
    for spec in moments.DECLARED_TRIAL_MOMENTS:
        assert spec.claim_set_version in claims_module._SETS_BY_VERSION


def test_an_entry_pinned_motion_still_declares_nothing() -> None:
    """Only a declared trial id reaches a trial set: a motion's kind says nothing of its stage."""
    for event_id in ("evt-motion-stay", "evt-motion-re-trial-transcripts", "evt-order-judgment-x"):
        assert declared_claim_set(event_id) is None
        assert declared_distribution_claims(event_id) == ()


def test_no_trial_distribution_claim_is_scored() -> None:
    """No committed cut of prior rulings prices one, so each is collected and resolved only."""
    for claim_id in (CLAIM_TRIAL_RULING, CLAIM_TRIAL_LEAVE, CLAIM_TRIAL_JUDGMENT):
        assert DISTRIBUTION_CLAIMS[claim_id] == ("categorical", False)


# --- cells ----------------------------------------------------------------------


def _even(labels: tuple[str, ...]) -> dict[str, float]:
    return {label: 1 / len(labels) for label in labels}


def _ruling(probability: float = 0.7) -> dict[str, float]:
    """A ruling distribution whose granted side carries ``probability``."""
    rest = (1 - probability) / 3
    return {
        "granted": probability / 2,
        "granted-in-part": probability / 2,
        "denied": rest,
        "withdrawn": rest,
        "mooted": rest,
    }


def _judgment(probability: float) -> dict[str, float]:
    return {
        "plaintiff": probability / 2,
        "mixed": probability / 2,
        "defendant": (1 - probability) / 2,
        "no-merits-decision": (1 - probability) / 2,
    }


def _prediction(
    event_id: str = _DISMISSAL,
    *,
    probability: float = 0.7,
    claims: list[ClaimProbability] | None = None,
    distributions: list[ClaimDistribution] | None = None,
) -> Prediction:
    headline = (
        CLAIM_TRIAL_JUDGMENT_FOR_PLAINTIFF if event_id == _JUDGMENT else CLAIM_TRIAL_RULING_GRANTED
    )
    return Prediction(
        case_id="cand/1",
        event_id=event_id,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 3, 1),
        input_snapshot="x",
        granted=int(probability >= 0.5),
        probability=probability,
        predicted_disposition=Disposition.other,
        context=PredictionContext(
            mode="forward", snapshot_date=date(2026, 3, 1), signals_observable=False
        ),
        claims=(
            claims
            if claims is not None
            else [ClaimProbability(claim_id=headline, probability=probability)]
        ),
        claim_distributions=distributions,
    )


def _outcome(event_id: str = _DISMISSAL, **fields: Any) -> Outcome:
    base: dict[str, Any] = {
        "case_id": "cand/1",
        "event_id": event_id,
        "resolved_at": date(2026, 6, 1),
        "actual_disposition": Disposition.other,
        "actual_granted": 0,
    }
    return Outcome(**(base | fields))


def _dismissal_block(
    ruling: dict[str, float] | None = None, leave: dict[str, float] | None = None
) -> list[ClaimDistribution]:
    return [
        ClaimDistribution(claim_id=CLAIM_TRIAL_RULING, probabilities=ruling or _ruling()),
        ClaimDistribution(claim_id=CLAIM_TRIAL_LEAVE, probabilities=leave or _even(_LEAVES)),
    ]


def _score(prediction: Prediction, outcome: Outcome) -> Any:
    return score_claims(prediction, outcome, StatPack(corpus_rows=1), lookback_terms=3)


def test_a_trial_cell_reads_its_set_through_the_trial_table() -> None:
    prediction = _prediction(distributions=_dismissal_block())
    assert declared_claim_set_for(prediction) == (
        CLAIM_SET_TRIAL_DISMISSAL_V1,
        (CLAIM_TRIAL_RULING_GRANTED,),
    )
    assert declared_distribution_claims_for(prediction) == (CLAIM_TRIAL_RULING, CLAIM_TRIAL_LEAVE)
    assert claim_block_problems(prediction) == []


@pytest.mark.parametrize(
    ("ruling", "granted"),
    [("granted", 1), ("granted-in-part", 1), ("denied", 0), ("withdrawn", 0), ("mooted", 0)],
)
def test_the_headline_resolves_on_every_ruling_and_is_never_scored(
    ruling: str, granted: int
) -> None:
    """Resolved on a withdrawn or mooted motion too, and unscored for want of a baseline."""
    block = _score(
        _prediction(
            _CLASS,
            distributions=[ClaimDistribution(claim_id=CLAIM_TRIAL_RULING, probabilities=_ruling())],
        ),
        _outcome(_CLASS, trial_ruling=ruling, actual_granted=granted),
    )
    assert block is not None and block.declared_set_version == CLAIM_SET_TRIAL_MOTION_V1
    (row,) = block.claims
    assert (row.claim_id, row.outcome, row.baseline, row.score) == (
        CLAIM_TRIAL_RULING_GRANTED,
        granted,
        None,
        None,
    )
    assert block.total is None and block.floor is None and block.lift is None
    (distribution,) = block.distributions
    assert distribution.outcome == {label: int(label == ruling) for label in _RULINGS}
    assert not distribution.scored and distribution.score is None and distribution.baseline is None


def test_leave_resolves_only_on_a_dismissal_granted_in_whole_or_in_part() -> None:
    granted = _score(
        _prediction(distributions=_dismissal_block()),
        _outcome(trial_ruling="granted", trial_leave="with-leave", actual_granted=1),
    )
    rows = {row.claim_id: row for row in granted.distributions}
    assert rows[CLAIM_TRIAL_LEAVE].outcome == {
        label: int(label == "with-leave") for label in _LEAVES
    }
    denied = _score(_prediction(distributions=_dismissal_block()), _outcome(trial_ruling="denied"))
    rows = {row.claim_id: row for row in denied.distributions}
    assert rows[CLAIM_TRIAL_LEAVE].outcome is None
    assert rows[CLAIM_TRIAL_RULING].outcome is not None


def test_the_judgment_set_resolves_on_the_final_disposition() -> None:
    block = _score(
        _prediction(
            _JUDGMENT,
            probability=0.3,
            distributions=[
                ClaimDistribution(claim_id=CLAIM_TRIAL_JUDGMENT, probabilities=_judgment(0.3))
            ],
        ),
        _outcome(_JUDGMENT, trial_judgment="mixed", actual_granted=1),
    )
    assert block is not None and block.declared_set_version == CLAIM_SET_TRIAL_JUDGMENT_V1
    assert block.claims[0].claim_id == CLAIM_TRIAL_JUDGMENT_FOR_PLAINTIFF
    assert block.claims[0].outcome == 1
    assert block.distributions[0].outcome == {label: int(label == "mixed") for label in _JUDGMENTS}


def test_a_trial_claim_is_masked_on_an_outcome_of_another_shape() -> None:
    """The resolvers read the trial result, never the shared binary."""
    block = _score(_prediction(distributions=_dismissal_block()), _outcome(actual_granted=1))
    assert block is not None
    assert block.claims[0].outcome is None
    assert all(row.outcome is None for row in block.distributions)


def test_a_headline_that_diverges_from_the_probability_voids_the_block() -> None:
    prediction = _prediction(
        claims=[ClaimProbability(claim_id=CLAIM_TRIAL_RULING_GRANTED, probability=0.4)],
        distributions=_dismissal_block(),
    )
    assert _score(prediction, _outcome(trial_ruling="denied")) is None
    assert any("headline claim" in problem for problem in claim_block_problems(prediction))


def test_a_malformed_trial_distribution_is_named_and_scores_no_row() -> None:
    assert distribution_problems(CLAIM_TRIAL_RULING, _even(_RULINGS)) == []
    wrong_label = distribution_problems(CLAIM_TRIAL_RULING, {"granted": 0.5, "Kagan": 0.5})
    assert len(wrong_label) == 1 and "not one of its outcomes" in wrong_label[0]
    short = distribution_problems(CLAIM_TRIAL_LEAVE, {"with-leave": 0.5})
    assert len(short) == 1 and "one outcome, so one distribution" in short[0]
    # A bench claim's wording is its own.
    assert "one author" in distribution_problems("majority-author", {"Kagan": 0.5})[0]
    # A dismissal cell that leaves leave out states a partial set: no rows, and
    # the binary block stands.
    partial = _prediction(
        distributions=[ClaimDistribution(claim_id=CLAIM_TRIAL_RULING, probabilities=_ruling())]
    )
    assert f"declared distribution claim {CLAIM_TRIAL_LEAVE!r} is not stated" in (
        claim_block_problems(partial)
    )
    block = _score(partial, _outcome(trial_ruling="denied"))
    assert block is not None and block.distributions == [] and len(block.claims) == 1


# --- correctness ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("probability", "fields", "expected"),
    [
        (0.7, {"trial_ruling": "granted", "actual_granted": 1}, 1),
        (0.7, {"trial_ruling": "granted-in-part", "actual_granted": 1}, 1),
        (0.7, {"trial_ruling": "mooted"}, 0),
        (0.2, {"trial_ruling": "withdrawn"}, 1),
        (0.2, {"trial_ruling": "granted-in-part", "actual_granted": 1}, 0),
    ],
)
def test_correct_follows_the_stage_s_binary(
    probability: float, fields: dict[str, Any], expected: int
) -> None:
    """The accuracy column and the Brier score the same event; the label is not read."""
    prediction, outcome = _prediction(probability=probability), _outcome(**fields)
    assert is_correct(prediction, outcome) == expected
    # The routing is the outcome's, so the caller's interim word changes nothing.
    assert is_correct(prediction, outcome, interim=True) == expected
    assert scored_granted(prediction, outcome, interim=False) == outcome.actual_granted


def test_correct_on_the_judgment_event_is_the_plaintiff_side() -> None:
    outcome = _outcome(_JUDGMENT, trial_judgment="defendant")
    assert is_correct(_prediction(_JUDGMENT, probability=0.3), outcome) == 1
    assert is_correct(_prediction(_JUDGMENT, probability=0.8), outcome) == 0


def test_a_distribution_that_contradicts_the_headline_scores_no_row() -> None:
    """The spread's granted side is the headline stated again, so the two must agree."""
    assert trial_headline_problems(CLAIM_TRIAL_RULING, _ruling(0.7), 0.7) == []
    assert trial_headline_problems(CLAIM_TRIAL_LEAVE, _even(_LEAVES), 0.7) == []
    assert trial_headline_problems("majority-author", {"Kagan": 1.0}, 0.7) == []
    contradicting = _prediction(distributions=_dismissal_block(ruling=_ruling(0.2)))
    problems = claim_block_problems(contradicting)
    assert len(problems) == 1 and "one belief, two committed numbers" in problems[0]
    block = _score(contradicting, _outcome(trial_ruling="denied"))
    assert block is not None and block.distributions == [] and len(block.claims) == 1
    # Three-decimal rounding of the spread is not a contradiction.
    rounded = {label: round(p, 3) for label, p in _ruling(0.7).items()}
    assert trial_headline_problems(CLAIM_TRIAL_RULING, rounded, 0.7) == []


def test_the_headline_tolerance_is_two_rounded_labels() -> None:
    spread = {"granted": 0.35, "granted-in-part": 0.35, "denied": 0.3}
    assert trial_headline_problems(CLAIM_TRIAL_RULING, spread, 0.701) == []
    assert trial_headline_problems(CLAIM_TRIAL_RULING, spread, 0.699) == []
    assert len(trial_headline_problems(CLAIM_TRIAL_RULING, spread, 0.705)) == 1
    assert len(trial_headline_problems(CLAIM_TRIAL_RULING, spread, 0.698)) == 1


def test_a_judgment_spread_that_contradicts_the_headline_scores_no_row() -> None:
    contradicting = _prediction(
        _JUDGMENT,
        probability=0.3,
        distributions=[
            ClaimDistribution(claim_id=CLAIM_TRIAL_JUDGMENT, probabilities=_judgment(0.8))
        ],
    )
    assert any("plaintiff" in problem for problem in claim_block_problems(contradicting))
    block = _score(contradicting, _outcome(_JUDGMENT, trial_judgment="defendant"))
    assert block is not None and block.distributions == []


@pytest.mark.parametrize("event_id", [_DISMISSAL, _CLASS, _JUDGMENT])
def test_the_stub_states_a_well_formed_trial_block(event_id: str) -> None:
    """The offline cascade's cell is one validate accepts and the scorer resolves."""
    distributions = StubRunner._claim_distributions(event_id, date(2026, 3, 1))
    claims = StubRunner._claims(event_id)
    assert distributions is not None and claims is not None
    prediction = _prediction(
        event_id, probability=claims[0].probability, claims=claims, distributions=distributions
    )
    assert claim_block_problems(prediction) == []
    assert {d.claim_id for d in distributions} == set(declared_distribution_claims(event_id))
