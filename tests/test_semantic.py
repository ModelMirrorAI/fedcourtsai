"""Tests for the semantic claim family's declaration and descriptive roll-up.

`pipeline.semantic` declares `semantic-v1` on the merits moments and still
produces nothing: the prompts now ask a merits cell for the propositions and a
grader for the grades, but no opinion body is ingested to grade against, so
every declared claim masks and no census publishes. The invariants worth
pinning are therefore of two kinds.

The **declaration**: that `semantic-v1` is exactly two claims, each naming the
axis its mask is checked against and the document class it needs, on exactly the
merits moments and no other event; that the declaration — never the grader's
block — fixes what is graded and which set version the units carry; that a grade
is never run through the mechanical scoring rule (there is no baseline and no
score field to run it through); and that the optional schema blocks leave every
committed artifact valid.

The **plumbing**, proven against synthetic graded units before any opinion text
exists: the census counts each unit once at the panel's grade, the availability
mask is counted apart from the ordinal levels and a split on the mask apart
from both, derived figures are withheld below the minimum count, the population
a census covers is the caller's word and is recorded, and inter-grader
agreement is the same leave-one-out tau-b `Leaderboard.evaluator_agreement`
uses, over a different population.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import get_args

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner, Result

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments, semantic
from fedcourtsai.pipeline.claims import declared_claim_set
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID
from fedcourtsai.pipeline.semantic import (
    DECLARED_SEMANTIC_CLAIM_SETS,
    DECLARED_SEMANTIC_CLAIM_SETS_BY_EVENT_ID,
    SEMANTIC_MERITS_V1,
    SEMANTIC_MIN_GRADED,
    SEMANTIC_SET_V1,
    GradedUnit,
    SemanticClaimSpec,
    declared_semantic_claim_set,
    graded_units,
    ordinal,
    summarize_semantic_grades,
)
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    SemanticClaim,
    SemanticGrade,
    SemanticGradeBlock,
    SemanticGradeSummary,
    SemanticSupport,
    Stage,
    Stratum,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml

runner = CliRunner()

_EVENT_ID = "evt-petition-writ-of-certiorari"
_SUPPORTED = SemanticSupport.supported
_PARTIAL = SemanticSupport.partial
_UNSUPPORTED = SemanticSupport.unsupported
_MASKED = SemanticSupport.not_addressed


def _unit(
    grader: str,
    grade: SemanticSupport,
    *,
    claim_id: str = "majority-ground",
    cell: str = "1",
) -> GradedUnit:
    return GradedUnit(
        case_id="scotus/1",
        event_id=_EVENT_ID,
        predictor_id=f"p{cell}",
        grader_id=grader,
        claim_id=claim_id,
        grade=grade,
    )


def _panel(
    *grades: SemanticSupport, claim_id: str = "majority-ground", cell: str = "1"
) -> list[GradedUnit]:
    """One unit graded by as many graders as grades given."""
    return [_unit(f"g{i}", grade, claim_id=claim_id, cell=cell) for i, grade in enumerate(grades)]


def _evaluation(*, semantic_grades: SemanticGradeBlock | None = None) -> Evaluation:
    return Evaluation(
        case_id="scotus/1",
        event_id=_EVENT_ID,
        predictor_id="p",
        evaluator_id="e",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 3, 1),
        correct=True,
        semantic_grades=semantic_grades,
    )


# --- the declaration: semantic-v1, on the merits moments and nowhere else ---


def test_the_declared_set_is_exactly_two_claims_with_their_axes() -> None:
    """The declaration itself, pinned: a claim added or renamed is a new version."""
    assert SEMANTIC_SET_V1 == "semantic-v1"
    assert [spec.claim_id for spec in SEMANTIC_MERITS_V1] == [
        "majority-ground",
        "ground-breadth",
    ]
    # The axis is what makes "silent on the claim's axis" checkable rather than
    # conventional, and `requires` is the mask's first ground — neither may be
    # declared blank.
    assert all(spec.axis.strip() for spec in SEMANTIC_MERITS_V1)
    assert {spec.requires for spec in SEMANTIC_MERITS_V1} == {"majority-opinion"}


def test_the_ground_and_its_breadth_are_two_claims_not_one() -> None:
    """Bundling them would reintroduce the compound-claim failure v1 rejects."""
    assert len({spec.claim_id for spec in SEMANTIC_MERITS_V1}) == 2
    assert len({spec.axis for spec in SEMANTIC_MERITS_V1}) == 2


def test_every_merits_moment_declares_the_set() -> None:
    """Keyed off the moment table, so an inserted merits moment cannot declare nothing."""
    merits = moments.moments_for(Stage.merits)
    assert len(merits) >= 2
    for spec in merits:
        declared = declared_semantic_claim_set(spec.event_id)
        assert declared == (SEMANTIC_SET_V1, SEMANTIC_MERITS_V1)
    assert set(DECLARED_SEMANTIC_CLAIM_SETS_BY_EVENT_ID) == {s.event_id for s in merits}
    assert declared_semantic_claim_set(MERITS_EVENT_ID) is not None
    assert declared_claim_set(MERITS_EVENT_ID) is not None


def test_no_event_outside_the_merits_moments_declares_a_semantic_set() -> None:
    """A claim about a merits opinion belongs to the moments that forecast one."""
    assert DECLARED_SEMANTIC_CLAIM_SETS == {}
    merits = {spec.event_id for spec in moments.moments_for(Stage.merits)}
    for spec in moments.DECLARED_MOMENTS:
        if spec.event_id not in merits:
            assert declared_semantic_claim_set(spec.event_id) is None


@pytest.mark.parametrize("kind", list(EventKind))
def test_no_event_kind_declares_a_semantic_set(kind: EventKind) -> None:
    """The kind table is the fallback the mechanical family keeps, and it is empty."""
    assert declared_semantic_claim_set(f"evt-{kind.value}-anything") is None


def test_a_malformed_event_id_yields_no_set_rather_than_a_crash() -> None:
    assert declared_semantic_claim_set("not-an-event-id") is None
    assert declared_semantic_claim_set("evt-nonsense-thing") is None


# --- the grade vocabulary: three ordinal levels and a mask that is not one ---


def test_the_vocabulary_is_exactly_four_values() -> None:
    assert [g.value for g in SemanticSupport] == [
        "supported",
        "partially-supported",
        "unsupported",
        "not-addressed",
    ]


def test_the_mask_has_no_position_on_the_ordinal_scale() -> None:
    """`not-addressed` is a property of the record, not a low grade."""
    assert ordinal(_MASKED) is None
    assert ordinal(_UNSUPPORTED) == 0
    assert ordinal(_PARTIAL) == 1
    assert ordinal(_SUPPORTED) == 2


def test_a_semantic_grade_carries_no_baseline_and_no_score() -> None:
    """The design decision, enforced by the schema: grades never enter `claim_score`."""
    assert set(SemanticGrade.model_fields) == {"claim_id", "grade", "basis"}
    assert "total" not in set(SemanticGradeBlock.model_fields)


def test_a_semantic_claim_carries_no_probability() -> None:
    """No harness-computable prior exists, so no number invites the mechanical rule."""
    assert set(SemanticClaim.model_fields) == {"claim_id", "proposition"}


# --- the census: one entry per unit, at the panel's grade ---


def test_each_unit_is_counted_once_however_many_graders_graded_it() -> None:
    summary = summarize_semantic_grades(_panel(_SUPPORTED, _SUPPORTED, _SUPPORTED))
    assert summary.units == 1
    assert summary.graders == 3
    census = summary.claims[0]
    assert (census.supported, census.graded) == (1, 1)


def test_the_panel_grade_is_the_median_ordinal() -> None:
    summary = summarize_semantic_grades(_panel(_SUPPORTED, _PARTIAL, _PARTIAL))
    assert summary.claims[0].partial == 1
    assert summary.claims[0].supported == 0


def test_an_even_split_rounds_toward_less_support() -> None:
    """Grader multiplicity must never manufacture credit."""
    summary = summarize_semantic_grades(_panel(_SUPPORTED, _UNSUPPORTED))
    assert summary.claims[0].unsupported == 1
    assert summary.claims[0].supported == 0


def test_a_four_grader_split_takes_the_lower_median_not_the_floor_of_the_median() -> None:
    """On [0, 0, 2, 2] the lower median is `unsupported`; the floor of the median is not."""
    summary = summarize_semantic_grades(_panel(_UNSUPPORTED, _UNSUPPORTED, _SUPPORTED, _SUPPORTED))
    assert summary.claims[0].unsupported == 1
    assert summary.claims[0].partial == 0


def test_a_four_grader_majority_carries_the_unit() -> None:
    summary = summarize_semantic_grades(_panel(_PARTIAL, _SUPPORTED, _SUPPORTED, _SUPPORTED))
    assert summary.claims[0].supported == 1


def test_the_census_is_independent_of_input_order() -> None:
    units = [
        *_panel(_SUPPORTED, _PARTIAL, cell="1"),
        *_panel(_UNSUPPORTED, _UNSUPPORTED, cell="2"),
        *_panel(_MASKED, _MASKED, claim_id="dissent-ground", cell="1"),
    ]
    forward = summarize_semantic_grades(units)
    backward = summarize_semantic_grades(list(reversed(units)))
    assert forward == backward


def test_claims_are_reported_in_a_stable_sorted_order() -> None:
    summary = summarize_semantic_grades(
        [
            *_panel(_SUPPORTED, claim_id="majority-ground"),
            *_panel(_SUPPORTED, claim_id="dissent-ground"),
        ]
    )
    assert [c.claim_id for c in summary.claims] == ["dissent-ground", "majority-ground"]


def test_the_pooled_census_carries_no_claim_id() -> None:
    """A pooled share describes the claim mix as much as the predictor."""
    summary = summarize_semantic_grades(_panel(_SUPPORTED))
    assert summary.overall is not None
    assert summary.overall.claim_id is None
    assert summary.overall.graded == 1


def test_no_units_yields_an_empty_summary_not_a_crash() -> None:
    summary = summarize_semantic_grades([])
    assert summary.units == 0
    assert summary.cells == 0
    assert summary.claims == []
    assert summary.overall is None
    assert summary.agreement == {}


# --- the availability mask: a property of the record, never of the predictor ---


def test_a_unanimously_masked_unit_is_counted_apart_from_the_ordinal_levels() -> None:
    summary = summarize_semantic_grades(_panel(_MASKED, _MASKED, _MASKED))
    census = summary.claims[0]
    assert census.not_addressed == 1
    assert census.graded == 0
    assert (census.supported, census.partial, census.unsupported) == (0, 0, 0)


def test_a_split_on_the_mask_is_counted_apart_from_both() -> None:
    """The graders disagree about the record, not about the prediction."""
    summary = summarize_semantic_grades(_panel(_MASKED, _SUPPORTED, _SUPPORTED))
    census = summary.claims[0]
    assert census.mask_disputed == 1
    assert census.graded == 0
    assert census.not_addressed == 0


def test_a_disputed_mask_never_enters_the_agreement_coefficient() -> None:
    units = [unit for i in range(12) for unit in _panel(_MASKED, _SUPPORTED, cell=str(i))]
    summary = summarize_semantic_grades(units)
    assert summary.claims[0].mask_disputed == 12
    assert summary.agreement == {}


def test_a_masked_unit_never_depresses_the_supported_share() -> None:
    """The mask sits outside the denominator, so an ungradeable record costs nothing."""
    graded = [unit for i in range(10) for unit in _panel(_SUPPORTED, cell=str(i))]
    masked = [unit for i in range(10, 20) for unit in _panel(_MASKED, cell=str(i))]
    summary = summarize_semantic_grades(graded + masked, min_graded=10)
    census = summary.claims[0]
    assert census.graded == 10
    assert census.not_addressed == 10
    assert census.supported_share == 1.0


# --- suppression: counts publish, derived figures do not ---


def test_the_supported_share_is_withheld_below_the_minimum() -> None:
    units = [unit for i in range(9) for unit in _panel(_SUPPORTED, cell=str(i))]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.claims[0].graded == 9
    assert summary.claims[0].supported_share is None


def test_the_supported_share_publishes_at_the_minimum() -> None:
    units = [unit for i in range(10) for unit in _panel(_SUPPORTED, cell=str(i))]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.claims[0].supported_share == 1.0


def test_the_threshold_travels_with_the_figures() -> None:
    """A withheld share must not read as a missing one."""
    summary = summarize_semantic_grades(_panel(_SUPPORTED), min_graded=7)
    assert summary.min_graded == 7


def test_the_default_threshold_is_the_published_minimum() -> None:
    assert SEMANTIC_MIN_GRADED == 10
    summary = summarize_semantic_grades(_panel(_SUPPORTED))
    assert summary.min_graded == SEMANTIC_MIN_GRADED


# --- the population the census covers is the caller's word, and must be stated ---


def test_an_unstated_population_reads_as_unstated_rather_than_as_fine() -> None:
    """Strata and process scope have no other representation in the output."""
    summary = summarize_semantic_grades(_panel(_SUPPORTED))
    assert summary.stratum is None
    assert summary.process_scope is None


def test_the_stated_population_is_recorded_verbatim() -> None:
    summary = summarize_semantic_grades(
        _panel(_SUPPORTED), stratum="forward", process_scope="frozen"
    )
    assert (summary.stratum, summary.process_scope) == ("forward", "frozen")


def test_the_population_labels_are_closed_vocabularies() -> None:
    """The roll-up cannot check the label against the cells, so the type must."""
    with pytest.raises(ValidationError):
        SemanticGradeSummary(stratum="Forward")
    with pytest.raises(ValidationError):
        SemanticGradeSummary(process_scope="everything")
    assert set(get_args(Stratum)) == {"forward", "retrospective", "procedural"}


# --- inter-grader agreement: leave-one-out, the panel's number ---


def test_a_constant_grade_across_units_leaves_nothing_to_correlate() -> None:
    """Undefined because the *axis* never moves — not because the panel agreed.

    The distinction matters: the reading rule bars publication on a null
    coefficient precisely because this state and the pathology below are
    indistinguishable from the number alone.
    """
    units = [unit for i in range(12) for unit in _panel(_SUPPORTED, _SUPPORTED, cell=str(i))]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert set(summary.agreement) == {"g0", "g1"}
    assert summary.agreement["g0"].paired_units == 12
    assert summary.agreement["g0"].suppressed is False
    assert summary.agreement["g0"].rank_agreement is None


def test_a_unanimous_panel_whose_grades_vary_reads_plus_one_not_null() -> None:
    """Unanimity is not what makes tau-b undefined; a constant axis is."""
    grades = [_SUPPORTED, _PARTIAL, _UNSUPPORTED] * 4
    units = [unit for i, g in enumerate(grades) for unit in _panel(g, g, cell=str(i))]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement["g0"].rank_agreement == pytest.approx(1.0)
    assert summary.agreement["g1"].rank_agreement == pytest.approx(1.0)


def test_a_uniformly_generous_grader_reads_undefined_not_agreeing() -> None:
    """The pathology the number exists to catch, and it arrives wearing a null."""
    grades = [_SUPPORTED, _PARTIAL, _UNSUPPORTED] * 4
    units: list[GradedUnit] = []
    for i, grade in enumerate(grades):
        units.append(_unit("varies", grade, cell=str(i)))
        units.append(_unit("generous", _SUPPORTED, cell=str(i)))
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement["generous"].rank_agreement is None
    assert summary.agreement["generous"].suppressed is False
    # Same null as a genuinely uniform record — which is why it bars publication.
    assert summary.agreement["varies"].rank_agreement is None


def test_a_grader_who_reverses_the_panel_reads_negative() -> None:
    mine = [_SUPPORTED, _PARTIAL, _UNSUPPORTED] * 4
    units: list[GradedUnit] = []
    for i, grade in enumerate(mine):
        units.append(_unit("g0", grade, cell=str(i)))
        units.append(_unit("g1", list(reversed(mine))[i], cell=str(i)))
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement["g0"].rank_agreement is not None
    assert summary.agreement["g0"].rank_agreement < 0


def test_agreement_is_leave_one_out_never_a_panel_mean_containing_itself() -> None:
    """The self-term is what leave-one-out removes, and removing it changes the answer.

    One grader varies, its only peer is uniformly generous. Against the peer
    alone there is no variation to correlate with, so the honest answer is
    "undefined". A panel mean *containing* the grader would vary with the
    grader's own read and manufacture a perfect +1 out of nothing.
    """
    grades = [_SUPPORTED, _PARTIAL, _UNSUPPORTED] * 4
    units: list[GradedUnit] = []
    for i, grade in enumerate(grades):
        units.append(_unit("varies", grade, cell=str(i)))
        units.append(_unit("generous", _SUPPORTED, cell=str(i)))
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement["varies"].paired_units == 12
    assert summary.agreement["varies"].suppressed is False
    assert summary.agreement["varies"].rank_agreement is None


def test_a_dissenting_grader_reads_negative_against_its_peers() -> None:
    """A three-judge panel: the dissenter's own read never enters its comparison."""
    pattern = [_SUPPORTED, _UNSUPPORTED] * 6
    units: list[GradedUnit] = []
    for i, grade in enumerate(pattern):
        opposite = _UNSUPPORTED if grade == _SUPPORTED else _SUPPORTED
        units.append(_unit("g0", grade, cell=str(i)))
        units.append(_unit("g1", grade, cell=str(i)))
        units.append(_unit("g2", opposite, cell=str(i)))
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement["g2"].rank_agreement == pytest.approx(-1.0)


def test_the_counts_that_bound_the_coefficient_travel_with_it() -> None:
    """10 units over 2 cells and 5 claims is not 10 independent readings."""
    grades = [_SUPPORTED, _PARTIAL, _UNSUPPORTED, _SUPPORTED, _PARTIAL]
    units = [
        unit
        for cell in ("1", "2")
        for i, grade in enumerate(grades)
        for unit in _panel(grade, grade, claim_id=f"claim-{i}", cell=cell)
    ]
    summary = summarize_semantic_grades(units, min_graded=10)
    record = summary.agreement["g0"]
    assert record.paired_units == 10
    assert record.cells == 2
    assert record.claims_pooled == 5
    assert record.suppressed is False


def test_a_single_claim_leaves_no_between_claim_contrast_to_pool() -> None:
    """`claims_pooled` is the integer that bounds the pooling caveat."""
    units = [unit for i in range(12) for unit in _panel(_SUPPORTED, _PARTIAL, cell=str(i))]
    assert summarize_semantic_grades(units, min_graded=10).agreement["g0"].claims_pooled == 1


def test_the_pooled_census_carries_the_cell_count_its_share_rests_on() -> None:
    """`overall` reaches the minimum on units, which a multi-claim set gets from few cells."""
    units = [
        unit
        for cell in ("1", "2")
        for i in range(5)
        for unit in _panel(_SUPPORTED, claim_id=f"claim-{i}", cell=cell)
    ]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.overall is not None
    assert summary.overall.graded == 10
    assert summary.overall.cells == 2
    assert summary.overall.supported_share == 1.0
    # On a per-claim census the cell count is the unit count — it states the
    # identity rather than adding to it.
    assert all(c.cells == c.graded + c.not_addressed + c.mask_disputed for c in summary.claims)


def test_agreement_is_withheld_below_the_minimum_with_the_count_published() -> None:
    grades = [_SUPPORTED, _PARTIAL, _UNSUPPORTED]
    units = [unit for i, g in enumerate(grades) for unit in _panel(g, g, cell=str(i))]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement["g0"].suppressed is True
    assert summary.agreement["g0"].rank_agreement is None
    assert summary.agreement["g0"].paired_units == 3


def test_a_single_grader_produces_no_agreement_record() -> None:
    """Agreement is the family's only check on grader latitude; one grader has none."""
    units = [unit for i in range(12) for unit in _panel(_SUPPORTED, cell=str(i))]
    summary = summarize_semantic_grades(units, min_graded=10)
    assert summary.agreement == {}


def test_one_grader_grading_one_unit_twice_is_an_error_not_an_average() -> None:
    units = [_unit("g0", _SUPPORTED), _unit("g0", _UNSUPPORTED)]
    with pytest.raises(ValueError, match="twice"):
        summarize_semantic_grades(units)


# --- the bridge from a committed evaluation: the declaration is authoritative ---

_SKETCH_SET = (
    SemanticClaimSpec(
        claim_id="majority-ground",
        axis="the majority's doctrinal basis",
        requires="majority-opinion",
    ),
    SemanticClaimSpec(
        claim_id="dissent-ground",
        axis="the ground the dissent rests on",
        requires="dissent",
    ),
)
_SKETCH_IDS = [spec.claim_id for spec in _SKETCH_SET]


@pytest.fixture
def declared(monkeypatch: pytest.MonkeyPatch) -> tuple[str, tuple[SemanticClaimSpec, ...]]:
    """A synthetic declaration on the petition kind, where the real tables declare none.

    Exercised on the *kind* table so the bridge's refusals are pinned against a
    set the real declaration does not carry — including `dissent-ground`, a
    candidate `semantic-v1` deliberately leaves out.
    """
    entry = (SEMANTIC_SET_V1, _SKETCH_SET)
    monkeypatch.setattr(semantic, "DECLARED_SEMANTIC_CLAIM_SETS", {EventKind.petition: entry})
    return entry


def _prediction(*, semantic_claims: list[str] | None = None) -> Prediction:
    return Prediction(
        case_id="scotus/1",
        event_id=_EVENT_ID,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 3, 1),
        input_snapshot="x",
        granted=0,
        probability=0.2,
        predicted_disposition=Disposition.denied,
        semantic_claims=(
            None
            if semantic_claims is None
            else [
                SemanticClaim(claim_id=claim_id, proposition=f"proposition for {claim_id}")
                for claim_id in semantic_claims
            ]
        ),
    )


def _block(
    *grades: tuple[str, SemanticSupport], version: str = SEMANTIC_SET_V1
) -> SemanticGradeBlock:
    return SemanticGradeBlock(
        declared_set_version=version,
        grades=[SemanticGrade(claim_id=claim_id, grade=grade) for claim_id, grade in grades],
    )


def test_an_evaluation_without_a_semantic_block_yields_no_units() -> None:
    assert graded_units(_evaluation()) == ()


def test_a_block_on_an_event_with_no_declared_set_yields_no_units() -> None:
    """Today's state, and the reason it is: the declaration, not the block, decides."""
    block = _block(("majority-ground", _SUPPORTED))
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_block_grading_one_claim_twice_yields_no_units(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """Two grades for one proposition: take none rather than pick silently."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("majority-ground", _UNSUPPORTED),
        ("dissent-ground", _SUPPORTED),
    )
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_block_skipping_a_declared_claim_yields_no_units(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """The set is mandatory: a partial answer grades nothing, not the graded half."""
    block = _block(("majority-ground", _SUPPORTED))
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_claim_outside_the_declared_set_is_ignored(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """The declaration, not the census, fixes what is graded."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _PARTIAL),
        ("invented-claim", _SUPPORTED),
    )
    units = graded_units(_evaluation(semantic_grades=block))
    assert [u.claim_id for u in units] == _SKETCH_IDS


def test_a_block_answering_a_different_declaration_yields_no_units(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """Refused, never relabelled: silently restamping would pool two declarations."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _SUPPORTED),
        version="semantic-v2",
    )
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_superseded_block_under_the_current_declaration_yields_no_units(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """The supersession case: grades formed under the old set answer another question."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _SUPPORTED),
        version="semantic-v0",
    )
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_matching_block_carries_the_declarations_version(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    block = _block(("majority-ground", _SUPPORTED), ("dissent-ground", _SUPPORTED))
    units = graded_units(_evaluation(semantic_grades=block))
    assert {u.declared_set_version for u in units} == {SEMANTIC_SET_V1}


def test_a_block_becomes_units_carrying_the_grades_the_grader_gave(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """The payload itself, end to end: model → units → census."""
    block = _block(("majority-ground", _SUPPORTED), ("dissent-ground", _MASKED))
    units = graded_units(_evaluation(semantic_grades=block))
    assert [u.claim_id for u in units] == ["majority-ground", "dissent-ground"]
    assert [u.grade for u in units] == [_SUPPORTED, _MASKED]
    # The model stores the enum's *value* (`use_enum_values`), so the bridge has
    # to re-widen it or the ordinal lookup would be reading a bare string.
    assert [type(u.grade) for u in units] == [SemanticSupport, SemanticSupport]
    assert ordinal(units[0].grade) == 2 and ordinal(units[1].grade) is None
    assert {u.grader_id for u in units} == {"e"}
    assert units[0].unit_key == ("scotus/1", _EVENT_ID, "p", "majority-ground")
    summary = summarize_semantic_grades(units)
    assert summary.declared_set_versions == [SEMANTIC_SET_V1]
    assert summary.cells == 1
    census = {c.claim_id: c for c in summary.claims}
    assert census["majority-ground"].supported == 1
    assert census["dissent-ground"].not_addressed == 1


def test_the_payload_survives_a_round_trip_through_the_committed_artifact(
    declared: tuple[str, tuple[str, ...]], tmp_path: Path
) -> None:
    """The seam a real ledger would use: written, re-read, bridged, counted."""
    evaluation = _evaluation(
        semantic_grades=_block(("majority-ground", _PARTIAL), ("dissent-ground", _UNSUPPORTED))
    )
    path = tmp_path / "evaluation.json"
    write_json(path, evaluation)
    units = graded_units(read_model(path, Evaluation))
    assert [u.grade for u in units] == [_PARTIAL, _UNSUPPORTED]
    summary = summarize_semantic_grades(units)
    census = {c.claim_id: c for c in summary.claims}
    assert census["majority-ground"].partial == 1
    assert census["dissent-ground"].unsupported == 1


# --- the refusals, said out loud: what `validate` surfaces ---------------------
#
# `graded_units` refuses silently and nothing reads `semantic_claims` at all, so
# a non-conforming block on either side commits green and simply drops out of
# the census later. These pin the two enumerators to those refusals: a new
# refusal arm in `graded_units` needs a matching arm in `semantic_grade_problems`.


def test_an_absent_semantic_block_is_not_a_problem() -> None:
    """Absence is a legitimate state on both sides — every cell written before the
    prompts asked carries none — so it is skipped, never flagged."""
    assert semantic.semantic_grade_problems(_evaluation()) == []
    assert semantic.semantic_claim_problems(_prediction()) == []


def test_a_block_on_an_undeclaring_event_is_not_a_problem() -> None:
    block = _block(("majority-ground", _SUPPORTED))
    assert semantic.semantic_grade_problems(_evaluation(semantic_grades=block)) == []
    assert semantic.semantic_claim_problems(_prediction(semantic_claims=["majority-ground"])) == []


def test_every_grade_block_refusal_is_named_by_the_enumerator(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """Each shape `graded_units` drops the block on, said in words."""
    twice = _block(
        ("majority-ground", _SUPPORTED),
        ("majority-ground", _UNSUPPORTED),
        ("dissent-ground", _SUPPORTED),
    )
    assert any(
        "graded twice" in p
        for p in semantic.semantic_grade_problems(_evaluation(semantic_grades=twice))
    )
    skipped = _block(("majority-ground", _SUPPORTED))
    assert any(
        "'dissent-ground'" in p
        for p in semantic.semantic_grade_problems(_evaluation(semantic_grades=skipped))
    )
    other = _block(
        ("majority-ground", _SUPPORTED), ("dissent-ground", _SUPPORTED), version="semantic-v2"
    )
    assert any(
        "another declaration" in p
        for p in semantic.semantic_grade_problems(_evaluation(semantic_grades=other))
    )


def test_a_conforming_grade_block_has_no_problems(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    block = _block(("majority-ground", _SUPPORTED), ("dissent-ground", _MASKED))
    assert semantic.semantic_grade_problems(_evaluation(semantic_grades=block)) == []


def test_a_row_outside_the_declared_set_is_not_a_grade_block_problem(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """The enumerator reports refusals, not opinions: `graded_units` ignores such a
    row rather than dropping the block, so flagging it would be stricter than the
    consumer it exists to speak for."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _SUPPORTED),
        ("invented-claim", _SUPPORTED),
    )
    assert semantic.semantic_grade_problems(_evaluation(semantic_grades=block)) == []


@pytest.mark.parametrize(
    "rows",
    [
        # Conforming.
        (("majority-ground", _SUPPORTED), ("dissent-ground", _PARTIAL)),
        # Skipped declared claim.
        (("majority-ground", _SUPPORTED),),
        # Same claim graded twice.
        (
            ("majority-ground", _SUPPORTED),
            ("majority-ground", _UNSUPPORTED),
            ("dissent-ground", _PARTIAL),
        ),
        # An out-of-set row, ignored by both.
        (
            ("majority-ground", _SUPPORTED),
            ("dissent-ground", _PARTIAL),
            ("invented-claim", _SUPPORTED),
        ),
        # An out-of-set row duplicated: `graded_units` refuses on the duplicate
        # wherever it sits, so the enumerator must speak even though a single
        # out-of-set row is silent.
        (
            ("majority-ground", _SUPPORTED),
            ("dissent-ground", _PARTIAL),
            ("invented-claim", _SUPPORTED),
            ("invented-claim", _UNSUPPORTED),
        ),
    ],
)
def test_the_enumerator_speaks_exactly_when_the_rollup_refuses(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
    rows: tuple[tuple[str, SemanticSupport], ...],
) -> None:
    """The invariant the shape assertions above only sample: for a block present
    against a declared set, the enumerator is non-empty **iff** `graded_units`
    yields nothing. A new refusal arm on either side breaks this rather than
    quietly diverging."""
    evaluation = _evaluation(semantic_grades=_block(*rows))
    assert bool(semantic.semantic_grade_problems(evaluation)) == (graded_units(evaluation) == ())


def test_the_predictor_side_is_held_to_the_declaration_too(
    declared: tuple[str, tuple[SemanticClaimSpec, ...]],
) -> None:
    """The half that had no enforcement: nothing consumes `semantic_claims`, so a
    skipped or invented claim leaves no trace anywhere downstream."""
    assert semantic.semantic_claim_problems(_prediction(semantic_claims=["majority-ground"])) == [
        f"declared semantic claim 'dissent-ground' ({SEMANTIC_SET_V1}) is not stated"
    ]
    invented = semantic.semantic_claim_problems(
        _prediction(semantic_claims=["majority-ground", "dissent-ground", "invented-claim"])
    )
    assert any("is not declared by" in p for p in invented)
    twice = semantic.semantic_claim_problems(
        _prediction(semantic_claims=["majority-ground", "majority-ground", "dissent-ground"])
    )
    assert any("stated twice" in p for p in twice)
    assert (
        semantic.semantic_claim_problems(
            _prediction(semantic_claims=["majority-ground", "dissent-ground"])
        )
        == []
    )


def test_more_than_one_declaration_version_is_visible_in_the_summary() -> None:
    """A defensive disclosure only: `graded_units` cannot produce a mixed set.

    The bridge refuses a block whose version disagrees with the declaration, so
    units assembled through it always share one. A mixed value therefore says
    the units were assembled by some other path — which is exactly when a
    reader needs to see it.
    """
    units = [
        _unit("g0", _SUPPORTED, cell="1"),
        GradedUnit(
            case_id="scotus/1",
            event_id=_EVENT_ID,
            predictor_id="p2",
            grader_id="g0",
            claim_id="majority-ground",
            grade=_SUPPORTED,
            declared_set_version="semantic-v2",
        ),
    ]
    summary = summarize_semantic_grades(units)
    assert summary.declared_set_versions == ["semantic-v1", "semantic-v2"]


# --- the schema surface: optional everywhere, so every committed artifact validates ---


def test_a_prediction_without_semantic_claims_is_valid_and_round_trips(tmp_path) -> None:  # type: ignore[no-untyped-def]
    prediction = Prediction(
        case_id="scotus/1",
        event_id=_EVENT_ID,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 3, 1),
        input_snapshot="x",
        granted=0,
        probability=0.2,
        predicted_disposition=Disposition.denied,
    )
    assert prediction.semantic_claims is None
    path = tmp_path / "prediction.json"
    write_json(path, prediction)
    assert read_model(path, Prediction) == prediction


def test_an_evaluation_carrying_a_semantic_block_round_trips(tmp_path) -> None:  # type: ignore[no-untyped-def]
    evaluation = _evaluation(
        semantic_grades=SemanticGradeBlock(
            declared_set_version=SEMANTIC_SET_V1,
            grades=[
                SemanticGrade(
                    claim_id="majority-ground",
                    grade=_PARTIAL,
                    basis="The majority reaches the same result on a narrower ground.",
                )
            ],
        )
    )
    path = tmp_path / "evaluation.json"
    write_json(path, evaluation)
    assert read_model(path, Evaluation) == evaluation


# --- the published surface: two preconditions, both of which withhold today ---


def _write_merits_event(data_root: Path, *, case_id: str, event_id: str, moment: Moment) -> None:
    court, _, docket = case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(event_id)
    write_yaml(
        event.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=case_id,
            kind=EventKind.order,
            stage=Stage.merits,
            moment=moment,
            title="Judgment",
            resolved=True,
        ),
    )
    write_json(
        event.prediction("p", "p1"),
        Prediction(
            case_id=case_id,
            event_id=event_id,
            predictor_id="p",
            engine=Engine.claude_code,
            run_id="p1",
            created_at=datetime(2026, 6, 20, tzinfo=UTC),
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
        ),
    )
    write_json(
        event.outcome,
        Outcome(
            case_id=case_id,
            event_id=event_id,
            resolved_at=date(2026, 6, 23),
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )


def _write_grade(
    data_root: Path,
    *,
    case_id: str,
    grader: str,
    grades: tuple[SemanticSupport, SemanticSupport] = (_SUPPORTED, _PARTIAL),
    event_id: str = MERITS_EVENT_ID,
    run_id: str = "r",
    graded_at: datetime = datetime(2026, 6, 25, tzinfo=UTC),
    block: SemanticGradeBlock | None = None,
) -> None:
    court, _, docket = case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(event_id)
    write_json(
        event.evaluation(grader, "p", run_id),
        Evaluation(
            case_id=case_id,
            event_id=event_id,
            predictor_id="p",
            evaluator_id=grader,
            engine=Engine.claude_code,
            run_id=run_id,
            created_at=graded_at,
            correct=True,
            semantic_grades=block
            if block is not None
            else _block(("majority-ground", grades[0]), ("ground-breadth", grades[1])),
        ),
    )


def _write_merits_cell(data_root: Path, *, case_id: str, grader: str) -> None:
    """A full merits cell on disk at the first moment, graded under the declaration."""
    _write_merits_event(data_root, case_id=case_id, event_id=MERITS_EVENT_ID, moment=Moment.grant)
    _write_grade(data_root, case_id=case_id, grader=grader)


def _panel_ledger(data_root: Path, cases: int) -> None:
    """Enough cases, graded by two graders whose reads vary, to clear both preconditions."""
    varying = [(_SUPPORTED, _PARTIAL), (_UNSUPPORTED, _SUPPORTED), (_PARTIAL, _UNSUPPORTED)]
    for i in range(cases):
        case_id = f"scotus/{i + 1}"
        _write_merits_event(
            data_root, case_id=case_id, event_id=MERITS_EVENT_ID, moment=Moment.grant
        )
        _write_grade(data_root, case_id=case_id, grader="e1", grades=varying[i % 3])
        _write_grade(data_root, case_id=case_id, grader="e2", grades=varying[i % 3])


def _invoke(data_root: Path, *args: str) -> Result:
    return runner.invoke(
        app, ["semantic-summary", *args], env={"FEDCOURTS_DATA_ROOT": str(data_root)}
    )


def test_the_summary_command_withholds_below_the_floor_and_writes_nothing(
    tmp_path: Path,
) -> None:
    """A census under the floor is a handful of readings, not a description."""
    data_root = tmp_path / "data"
    _write_merits_cell(data_root, case_id="scotus/1", grader="e1")
    _write_merits_cell(data_root, case_id="scotus/2", grader="e1")
    out = tmp_path / "semantic-grades.json"
    result = _invoke(data_root, "--out", str(out), "--all-versions")
    assert result.exit_code == 0, result.output
    # The declaration matched and produced units — two claims over two cells —
    # and the floor is what withholds them, not an empty ledger.
    assert "4 graded / 0 masked / 0 mask-disputed unit(s) over 2 cell(s)" in result.output
    assert "on 2 case(s)" in result.output
    assert f"below the {SEMANTIC_MIN_GRADED}-unit floor" in result.output
    assert not out.exists()


def test_the_summary_command_withholds_a_census_no_grader_agrees_over(
    tmp_path: Path,
) -> None:
    """The floor is not the whole predicate: a share with no agreement figure is barred."""
    data_root = tmp_path / "data"
    # Ten cases, one grader each: 20 graded units, well clear of the floor, and
    # no unit carries two graders — so `agreement` is empty.
    for i in range(10):
        _write_merits_cell(data_root, case_id=f"scotus/{i + 1}", grader="e1")
    out = tmp_path / "semantic-grades.json"
    result = _invoke(data_root, "--out", str(out), "--all-versions")
    assert result.exit_code == 0, result.output
    assert "20 graded" in result.output
    assert "no grader carries an agreement coefficient" in result.output
    assert not out.exists()


def test_the_summary_command_publishes_once_both_preconditions_clear(tmp_path: Path) -> None:
    """The moment the census becomes claimable, and what the artifact then carries."""
    data_root = tmp_path / "data"
    _panel_ledger(data_root, cases=6)
    out = tmp_path / "semantic-grades.json"
    result = _invoke(data_root, "--out", str(out), "--all-versions")
    assert result.exit_code == 0, result.output
    summary = read_model(out, SemanticGradeSummary)
    # The population is stated, never inferred — the roll-up cannot check either.
    assert (summary.stratum, summary.process_scope) == ("forward", "all")
    assert summary.declared_set_versions == [SEMANTIC_SET_V1]
    assert [c.claim_id for c in summary.claims] == ["ground-breadth", "majority-ground"]
    assert summary.overall is not None
    assert summary.overall.graded == 12
    # The bound that travels with the counts: 12 units rest on 6 opinions.
    assert (summary.cells, summary.cases) == (6, 6)
    assert any(record.rank_agreement is not None for record in summary.agreement.values())
    # Deterministic: a second run reproduces the file byte for byte.
    first = out.read_text()
    _invoke(data_root, "--out", str(out), "--all-versions")
    assert out.read_text() == first


def test_the_summary_command_takes_one_grade_per_grader_per_cell(tmp_path: Path) -> None:
    """Two runs are two grades from one grader on one unit, which the roll-up refuses."""
    data_root = tmp_path / "data"
    _panel_ledger(data_root, cases=6)
    # An ordinary re-grade: same grader, same cell, a later run. Without the
    # collapse this raises out of `summarize_semantic_grades`.
    _write_grade(
        data_root,
        case_id="scotus/1",
        grader="e1",
        grades=(_UNSUPPORTED, _UNSUPPORTED),
        run_id="r2",
        graded_at=datetime(2026, 7, 1, tzinfo=UTC),
    )
    out = tmp_path / "semantic-grades.json"
    result = _invoke(data_root, "--out", str(out), "--all-versions")
    assert result.exit_code == 0, result.output
    summary = read_model(out, SemanticGradeSummary)
    assert summary.overall is not None
    assert summary.overall.graded == 12  # not 14: the re-run replaced, never added
    assert "12 block(s)" in result.output
    # And it is the *newest* run that survived: e1's re-grade of scotus/1 flips
    # that unit's panel from `supported` to `unsupported` (the lower median of
    # the re-grade against e2's unchanged read).
    census = {c.claim_id: c for c in summary.claims}
    assert (census["majority-ground"].supported, census["majority-ground"].unsupported) == (1, 3)


def test_a_grader_whose_newest_run_carries_no_block_has_withdrawn_the_grade(
    tmp_path: Path,
) -> None:
    """A re-run that grades nothing is a withdrawal, not a reason to resurrect the old one."""
    data_root = tmp_path / "data"
    _write_merits_cell(data_root, case_id="scotus/1", grader="e1")
    # The same grader's later run, carrying no semantic block at all.
    event = CasePaths(data_root, "scotus", 1).event(MERITS_EVENT_ID)
    write_json(
        event.evaluation("e1", "p", "r2"),
        Evaluation(
            case_id="scotus/1",
            event_id=MERITS_EVENT_ID,
            predictor_id="p",
            evaluator_id="e1",
            engine=Engine.claude_code,
            run_id="r2",
            created_at=datetime(2026, 7, 1, tzinfo=UTC),
            correct=True,
        ),
    )
    result = _invoke(data_root, "--all-versions")
    assert result.exit_code == 0, result.output
    assert "0 block(s), 0 refused; 0 graded" in result.output


def test_a_refused_block_is_counted_rather_than_read_as_a_missing_grade(
    tmp_path: Path,
) -> None:
    """A systematic refusal must not render as 'few grades'."""
    data_root = tmp_path / "data"
    _write_merits_event(
        data_root, case_id="scotus/1", event_id=MERITS_EVENT_ID, moment=Moment.grant
    )
    _write_grade(
        data_root,
        case_id="scotus/1",
        grader="e1",
        block=_block(("majority-ground", _SUPPORTED), version="semantic-v2"),
    )
    result = _invoke(data_root, "--all-versions")
    assert result.exit_code == 0, result.output
    assert "1 block(s), 1 refused; 0 graded" in result.output


def test_the_later_merits_moment_is_not_pooled_with_the_first(tmp_path: Path) -> None:
    """A set is declared on every moment of its stage; a census covers one vantage."""
    data_root = tmp_path / "data"
    _write_merits_cell(data_root, case_id="scotus/1", grader="e1")
    briefed = next(
        spec.event_id for spec in moments.moments_for(Stage.merits) if spec.moment == Moment.briefed
    )
    _write_merits_event(data_root, case_id="scotus/1", event_id=briefed, moment=Moment.briefed)
    _write_grade(data_root, case_id="scotus/1", grader="e1", event_id=briefed)
    result = _invoke(data_root, "--all-versions")
    assert result.exit_code == 0, result.output
    # Both events declare `semantic-v1` and both are graded; only the stage's
    # first moment enters, so the briefed forecast never averages with the grant.
    assert declared_semantic_claim_set(briefed) is not None
    assert "1 block(s), 0 refused; 2 graded" in result.output


def test_the_summary_command_rejects_an_unknown_stratum(tmp_path: Path) -> None:
    """A census must state a population the reading contract recognizes."""
    result = _invoke(tmp_path / "data", "--stratum", "Forward")
    assert result.exit_code != 0
    assert "unknown stratum" in result.output
