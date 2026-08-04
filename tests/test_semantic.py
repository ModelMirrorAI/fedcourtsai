"""Tests for the semantic claim family's declaration seam and descriptive roll-up.

`pipeline.semantic` is wired but inert: no stage declares a `semantic-v0` set,
no prompt asks for one, and no committed artifact carries a grade. The
invariants worth pinning are therefore of two kinds.

The **seam**: that "no semantic set is declared for any stage" is an asserted
state rather than an accident, so turning the family on later is a declaration
plus a prompt rather than a new shape; that the declaration — never the
grader's block — fixes what is graded and which set version the units carry;
that a grade is never run through the mechanical scoring rule (there is no
baseline and no score field to run it through); and that the optional schema
blocks leave every committed artifact valid.

The **plumbing**, proven against synthetic graded units before any opinion text
exists: the census counts each unit once at the panel's grade, the availability
mask is counted apart from the ordinal levels and a split on the mask apart
from both, derived figures are withheld below the minimum count, the population
a census covers is the caller's word and is recorded, and inter-grader
agreement is the same leave-one-out tau-b `Leaderboard.evaluator_agreement`
uses, over a different population.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import get_args

import pytest
from pydantic import ValidationError

from fedcourtsai.pipeline import semantic
from fedcourtsai.pipeline.claims import declared_claim_set
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID
from fedcourtsai.pipeline.semantic import (
    DECLARED_SEMANTIC_CLAIM_SETS,
    DECLARED_SEMANTIC_CLAIM_SETS_BY_EVENT_ID,
    SEMANTIC_MIN_GRADED,
    SEMANTIC_SET_V0,
    GradedUnit,
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
    Prediction,
    SemanticClaim,
    SemanticGrade,
    SemanticGradeBlock,
    SemanticGradeSummary,
    SemanticSupport,
    Stratum,
)
from fedcourtsai.serialize import read_model, write_json

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


# --- the declaration seam: empty, on purpose, and asserted ---


def test_no_stage_declares_a_semantic_set_today() -> None:
    """The state the wiring exists to make explicit: nothing is declared."""
    assert DECLARED_SEMANTIC_CLAIM_SETS == {}
    assert DECLARED_SEMANTIC_CLAIM_SETS_BY_EVENT_ID == {}


@pytest.mark.parametrize("kind", list(EventKind))
def test_no_event_kind_declares_a_semantic_set(kind: EventKind) -> None:
    assert declared_semantic_claim_set(f"evt-{kind.value}-anything") is None


def test_the_minted_merits_event_declares_no_semantic_set() -> None:
    """The one event id keyed by exact id on the mechanical side declares none here."""
    assert declared_claim_set(MERITS_EVENT_ID) is not None
    assert declared_semantic_claim_set(MERITS_EVENT_ID) is None


def test_a_malformed_event_id_yields_no_set_rather_than_a_crash() -> None:
    assert declared_semantic_claim_set("not-an-event-id") is None
    assert declared_semantic_claim_set("evt-nonsense-thing") is None


def test_the_alpha_set_version_is_v0() -> None:
    """Pinned so a rename is a deliberate act: the first working set is v1."""
    assert SEMANTIC_SET_V0 == "semantic-v0"


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

_SKETCH_SET = ("majority-ground", "dissent-ground")


@pytest.fixture
def declared(monkeypatch: pytest.MonkeyPatch) -> tuple[str, tuple[str, ...]]:
    """A synthetic declaration, so the bridge is exercised without declaring one.

    The tables ship empty and stay empty; this only proves the seam behaves
    when an entry lands in it, which is what makes turning the family on a
    declaration plus a prompt rather than a new shape.
    """
    entry = (SEMANTIC_SET_V0, _SKETCH_SET)
    monkeypatch.setattr(semantic, "DECLARED_SEMANTIC_CLAIM_SETS", {EventKind.petition: entry})
    return entry


def _block(
    *grades: tuple[str, SemanticSupport], version: str = SEMANTIC_SET_V0
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
    declared: tuple[str, tuple[str, ...]],
) -> None:
    """Two grades for one proposition: take none rather than pick silently."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("majority-ground", _UNSUPPORTED),
        ("dissent-ground", _SUPPORTED),
    )
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_block_skipping_a_declared_claim_yields_no_units(
    declared: tuple[str, tuple[str, ...]],
) -> None:
    """The set is mandatory: a partial answer grades nothing, not the graded half."""
    block = _block(("majority-ground", _SUPPORTED))
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_claim_outside_the_declared_set_is_ignored(
    declared: tuple[str, tuple[str, ...]],
) -> None:
    """The declaration, not the census, fixes what is graded."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _PARTIAL),
        ("invented-claim", _SUPPORTED),
    )
    units = graded_units(_evaluation(semantic_grades=block))
    assert [u.claim_id for u in units] == list(_SKETCH_SET)


def test_a_block_answering_a_different_declaration_yields_no_units(
    declared: tuple[str, tuple[str, ...]],
) -> None:
    """Refused, never relabelled: silently restamping would pool two declarations."""
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _SUPPORTED),
        version="semantic-v1",
    )
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_stale_v0_block_under_a_v1_declaration_yields_no_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The supersession case: grades formed under the old set answer another question."""
    monkeypatch.setattr(
        semantic,
        "DECLARED_SEMANTIC_CLAIM_SETS",
        {EventKind.petition: ("semantic-v1", _SKETCH_SET)},
    )
    block = _block(
        ("majority-ground", _SUPPORTED),
        ("dissent-ground", _SUPPORTED),
        version=SEMANTIC_SET_V0,
    )
    assert graded_units(_evaluation(semantic_grades=block)) == ()


def test_a_matching_block_carries_the_declarations_version(
    declared: tuple[str, tuple[str, ...]],
) -> None:
    block = _block(("majority-ground", _SUPPORTED), ("dissent-ground", _SUPPORTED))
    units = graded_units(_evaluation(semantic_grades=block))
    assert {u.declared_set_version for u in units} == {SEMANTIC_SET_V0}


def test_a_block_becomes_units_carrying_the_grades_the_grader_gave(
    declared: tuple[str, tuple[str, ...]],
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
    assert summary.declared_set_versions == [SEMANTIC_SET_V0]
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
            declared_set_version="semantic-v1",
        ),
    ]
    summary = summarize_semantic_grades(units)
    assert summary.declared_set_versions == ["semantic-v0", "semantic-v1"]


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
            declared_set_version=SEMANTIC_SET_V0,
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
