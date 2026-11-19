"""The trial stage's declaration: its moments table, its ids, its outcome fields.

Declared and switched off: nothing here mints a cell. These tests hold the
shape the later wiring writes to.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import ValidationError

from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.events import entry_event_id
from fedcourtsai.pipeline.trial_resolver import (
    MOTION_MOMENTS,
    JudgmentOutcome,
    Leave,
    MotionRuling,
    TrialMoment,
)
from fedcourtsai.schemas import (
    TRIAL_JUDGMENTS_FOR_PLAINTIFF,
    TRIAL_RULINGS_GRANTED,
    CorpusCheck,
    Disposition,
    EventKind,
    Judgment,
    JusticeVote,
    Moment,
    Outcome,
    PredictableEvent,
    Stage,
    TrialJudgmentLabel,
    TrialLeaveLabel,
    TrialRulingLabel,
    VoteValue,
)
from fedcourtsai.serialize import write_yaml
from fedcourtsai.validate import CHECK_TRIAL_EVENTS, run_ledger_referential_checks

# --- the table ----------------------------------------------------------------


def test_the_table_declares_the_stage_s_five_moments_and_no_other() -> None:
    declared = {spec.moment for spec in moments.DECLARED_TRIAL_MOMENTS}
    assert declared == {m for m in Moment if m.value.startswith("trial-")}
    assert {m.value for m in declared} == {m.value for m in TrialMoment}
    assert all(spec.stage is Stage.trial for spec in moments.DECLARED_TRIAL_MOMENTS)


def test_every_trial_moment_is_switched_off() -> None:
    """Declared is not forecast: no trial moment mints a cell."""
    assert not any(spec.forecastable for spec in moments.DECLARED_TRIAL_MOMENTS)


def test_the_motion_moments_are_the_resolver_s_motion_moments() -> None:
    per_motion = {spec.moment.value for spec in moments.DECLARED_TRIAL_MOMENTS if spec.per_motion}
    assert per_motion == {m.value for m in MOTION_MOMENTS}


def test_the_court_s_table_holds_no_trial_row() -> None:
    """The Court's lookups read a null moment as the stage's first and fan one
    disposition over a stage's events; neither is true of the trial stage."""
    assert moments.moments_for(Stage.trial) == ()
    assert moments.first_moment(Stage.trial) is None
    assert not any(spec.stage == Stage.trial for spec in moments.DECLARED_MOMENTS)
    assert not any(moments.trial_moment(spec.moment) for spec in moments.DECLARED_MOMENTS)


# --- ids ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("moment", "entry", "expected"),
    [
        (Moment.trial_dismissal, 45, "evt-motion-trial-dismissal-45"),
        (Moment.trial_class, 7, "evt-motion-trial-class-7"),
        (Moment.trial_summary_judgment, 212, "evt-motion-trial-summary-judgment-212"),
        (
            Moment.trial_preliminary_injunction,
            3,
            "evt-motion-trial-preliminary-injunction-3",
        ),
        (Moment.trial_judgment, None, "evt-order-trial-judgment"),
    ],
)
def test_an_id_round_trips_through_the_table(
    moment: Moment, entry: int | None, expected: str
) -> None:
    event_id = moments.trial_event_id(moment, entry)
    assert event_id == expected
    spec = moments.trial_spec_for(event_id)
    assert spec is not None and spec.moment is moment
    assert moments.trial_entry_number(event_id) == entry
    assert moments.on_trial_label(event_id)
    # The Court's table has never heard of it.
    assert moments.spec_for(event_id) is None


@pytest.mark.parametrize(
    ("moment", "entry"),
    [
        (Moment.trial_dismissal, None),
        (Moment.trial_dismissal, 0),
        (Moment.trial_judgment, 4),
        (Moment.distribution, 4),
    ],
)
def test_a_mismatched_id_is_refused(moment: Moment, entry: int | None) -> None:
    with pytest.raises(ValueError, match=r"entry|trial moment"):
        moments.trial_event_id(moment, entry)


@pytest.mark.parametrize(
    "event_id",
    [
        "evt-motion-trial-dismissal",  # a motion id without its entry
        "evt-motion-trial-dismissal-045",  # one motion, one id
        "evt-order-trial-judgment-4",  # the judgment is one event per case
        "evt-order-trial-dismissal-45",  # the wrong kind for the moment
        "evt-motion-trial-judgment",
        "evt-motion-trial-transcript-12",  # an undeclared word
        "evt-motion-re-trial-dismissal-45",
        "evt-order-trial-judgment\n",
        "evt-motion-disposition",
    ],
)
def test_an_id_no_trial_moment_writes_reads_as_none(event_id: str) -> None:
    assert moments.trial_spec_for(event_id) is None
    assert moments.trial_entry_number(event_id) is None


def test_the_entry_pinned_extractor_steps_off_the_reserved_label() -> None:
    """A motion about a trial transcript is not a trial-stage event, so its id
    may not sit where only the trial mint seam writes."""
    minted = entry_event_id(
        "Motion for trial transcripts at government expense filed by petitioner.",
        EventKind.motion,
    )
    assert not moments.on_trial_label(minted)
    assert minted.startswith("evt-motion-re-trial-")
    # The bare word steps off too: a second such entry would be suffixed onto the label.
    assert entry_event_id("Motion for trial.", EventKind.motion) == "evt-motion-re-trial"
    # A subject that only mentions a trial is untouched.
    assert entry_event_id("Motion for a new trial filed.", EventKind.motion).startswith(
        "evt-motion-a-new-trial"
    )


# --- the outcome fields ---------------------------------------------------------


def test_the_outcome_vocabularies_are_the_resolver_s() -> None:
    assert set(get_args(TrialRulingLabel)) == {m.value for m in MotionRuling}
    assert set(get_args(TrialLeaveLabel)) == {m.value for m in Leave}
    assert set(get_args(TrialJudgmentLabel)) == {m.value for m in JudgmentOutcome}
    assert set(get_args(TrialRulingLabel)) >= TRIAL_RULINGS_GRANTED
    assert set(get_args(TrialJudgmentLabel)) >= TRIAL_JUDGMENTS_FOR_PLAINTIFF


def _outcome(**fields: Any) -> Outcome:
    base: dict[str, Any] = {
        "case_id": "cand/1",
        "event_id": "evt-motion-trial-dismissal-45",
        "resolved_at": date(2026, 3, 2),
        "actual_disposition": Disposition.other,
        "actual_granted": 0,
    }
    return Outcome(**(base | fields))


@pytest.mark.parametrize(
    ("ruling", "granted"),
    [("granted", 1), ("granted-in-part", 1), ("denied", 0), ("withdrawn", 0), ("mooted", 0)],
)
def test_a_motion_outcome_s_binary_is_granted_in_whole_or_in_part(
    ruling: str, granted: int
) -> None:
    assert _outcome(trial_ruling=ruling, actual_granted=granted).actual_granted == granted
    with pytest.raises(ValidationError, match="scores as"):
        _outcome(trial_ruling=ruling, actual_granted=1 - granted)


@pytest.mark.parametrize(
    ("judgment", "granted"),
    [("plaintiff", 1), ("mixed", 1), ("defendant", 0), ("no-merits-decision", 0)],
)
def test_a_judgment_outcome_s_binary_is_for_the_plaintiff_or_mixed(
    judgment: str, granted: int
) -> None:
    assert _outcome(trial_judgment=judgment, actual_granted=granted).actual_granted == granted
    with pytest.raises(ValidationError, match="scores as"):
        _outcome(trial_judgment=judgment, actual_granted=1 - granted)


def test_leave_rides_only_a_dismissal_granted_in_whole_or_in_part() -> None:
    kept = _outcome(trial_ruling="granted-in-part", trial_leave="mixed", actual_granted=1)
    assert kept.trial_leave == "mixed"
    with pytest.raises(ValidationError, match="leave is read only"):
        _outcome(trial_ruling="denied", trial_leave="unstated")
    with pytest.raises(ValidationError, match="without a `trial_ruling`"):
        _outcome(trial_leave="with-leave")
    with pytest.raises(ValidationError, match=r"without a `trial_ruling`|leave is read only"):
        _outcome(trial_judgment="plaintiff", trial_leave="with-leave", actual_granted=1)


def test_a_trial_outcome_carries_one_result_and_nothing_of_the_court_s() -> None:
    with pytest.raises(ValidationError, match="both set"):
        _outcome(trial_ruling="denied", trial_judgment="defendant")
    with pytest.raises(ValidationError, match="records `actual_disposition` as `other`"):
        _outcome(trial_ruling="denied", actual_disposition=Disposition.denied)
    with pytest.raises(ValidationError, match="field of the Court's stages: judgment"):
        _outcome(trial_judgment="plaintiff", actual_granted=1, judgment=Judgment.reversed)
    with pytest.raises(ValidationError, match="field of the Court's stages"):
        _outcome(trial_ruling="mooted", disposition_basis="mootness")
    with pytest.raises(ValidationError, match="field of the Court's stages: votes"):
        _outcome(
            trial_ruling="denied",
            votes=[JusticeVote(justice="Kagan", vote=VoteValue.dissent)],
        )
    with pytest.raises(ValidationError, match="field of the Court's stages: disposition_route"):
        _outcome(trial_ruling="granted", actual_granted=1, disposition_route="plenary")
    with pytest.raises(ValidationError, match="interim"):
        _outcome(trial_ruling="granted", actual_granted=1, interim_granted=1)


def test_the_trial_fields_are_omitted_while_null() -> None:
    """An outcome of the Court's stages serializes as it did before the fields."""
    court = Outcome(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        resolved_at=date(2026, 1, 2),
        actual_disposition=Disposition.denied,
        actual_granted=0,
    ).model_dump(mode="json")
    assert not {"trial_ruling", "trial_leave", "trial_judgment"} & court.keys()
    trial = _outcome(trial_ruling="granted", actual_granted=1).model_dump(mode="json")
    assert trial["trial_ruling"] == "granted"
    assert "trial_leave" not in trial and "trial_judgment" not in trial


# --- validate -------------------------------------------------------------------


def _event(
    data_root: Path,
    event_id: str,
    *,
    kind: EventKind,
    stage: Stage | None,
    moment: Moment | None,
    outcome: dict[str, Any] | None = None,
    docket: int = 1,
    decision_target: str | None = None,
) -> None:
    spec = moments.trial_spec_for(event_id)
    if decision_target is None:
        decision_target = spec.decision_target if spec is not None else "disposition"
    ep = CasePaths(data_root, "cand", docket).event(event_id)
    write_yaml(
        ep.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=f"cand/{docket}",
            kind=kind,
            stage=stage,
            moment=moment,
            title="Motion",
            decision_target=decision_target,
        ),
    )
    if outcome is not None:
        base = {
            "schema_version": "1.0",
            "case_id": f"cand/{docket}",
            "event_id": event_id,
            "resolved_at": "2026-03-02",
            "actual_disposition": "other",
            "actual_granted": 0,
        }
        ep.outcome.parent.mkdir(parents=True, exist_ok=True)
        ep.outcome.write_text(json.dumps(base | outcome))


def _check(data_root: Path) -> CorpusCheck:
    return next(c for c in run_ledger_referential_checks(data_root) if c.name == CHECK_TRIAL_EVENTS)


def test_declared_trial_records_pass(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _event(
        data_root,
        "evt-motion-trial-dismissal-45",
        kind=EventKind.motion,
        stage=Stage.trial,
        moment=Moment.trial_dismissal,
        outcome={"trial_ruling": "granted", "trial_leave": "with-leave", "actual_granted": 1},
    )
    _event(
        data_root,
        "evt-order-trial-judgment",
        kind=EventKind.order,
        stage=Stage.trial,
        moment=Moment.trial_judgment,
        outcome={"trial_judgment": "defendant"},
    )
    # An open event owes no outcome.
    _event(
        data_root,
        "evt-motion-trial-class-90",
        kind=EventKind.motion,
        stage=Stage.trial,
        moment=Moment.trial_class,
    )
    # An event of another stage is outside the rule and is not counted.
    _event(data_root, "evt-motion-stay", kind=EventKind.motion, stage=None, moment=None, docket=2)
    check = _check(data_root)
    assert check.passed, check.problems
    assert check.checked == 3


@pytest.mark.parametrize(
    ("event_id", "kind", "stage", "moment", "outcome", "expected"),
    [
        pytest.param(
            "evt-motion-trial-transcript-12",
            EventKind.motion,
            Stage.trial,
            Moment.trial_dismissal,
            None,
            "no trial moment writes",
            id="undeclared-id",
        ),
        pytest.param(
            "evt-motion-trial-dismissal-45",
            EventKind.motion,
            Stage.trial,
            Moment.trial_class,
            None,
            "id declares moment 'trial-dismissal'",
            id="moment-disagrees",
        ),
        pytest.param(
            "evt-motion-trial-dismissal-45",
            EventKind.motion,
            Stage.trial,
            None,
            None,
            "id declares moment 'trial-dismissal'",
            id="moment-missing",
        ),
        pytest.param(
            "evt-motion-trial-dismissal-45",
            EventKind.motion,
            None,
            None,
            None,
            "reserved label",
            id="label-off-stage",
        ),
        pytest.param(
            "evt-motion-stay",
            EventKind.motion,
            Stage.interim,
            Moment.trial_dismissal,
            None,
            "trial moment 'trial-dismissal' off the trial stage",
            id="moment-off-stage",
        ),
        pytest.param(
            "evt-motion-stay",
            EventKind.motion,
            None,
            None,
            {"trial_ruling": "denied"},
            "the fields are the trial stage's",
            id="field-off-stage",
        ),
        pytest.param(
            "evt-motion-trial-class-90",
            EventKind.motion,
            Stage.trial,
            Moment.trial_class,
            {},
            "carries no `trial_ruling`",
            id="result-missing",
        ),
        pytest.param(
            "evt-motion-trial-class-90",
            EventKind.motion,
            Stage.trial,
            Moment.trial_class,
            {"trial_ruling": "granted", "trial_leave": "with-leave", "actual_granted": 1},
            "leave to amend is read on a motion to dismiss only",
            id="leave-off-dismissal",
        ),
        pytest.param(
            "evt-order-trial-judgment",
            EventKind.order,
            Stage.trial,
            Moment.trial_judgment,
            {"trial_ruling": "denied"},
            "carries `trial_ruling`",
            id="ruling-on-judgment",
        ),
        pytest.param(
            "evt-order-trial-judgment",
            EventKind.order,
            Stage.trial,
            Moment.trial_judgment,
            {},
            "carries no `trial_judgment`",
            id="judgment-missing",
        ),
        pytest.param(
            "evt-motion-trial-class-90",
            EventKind.order,
            Stage.trial,
            Moment.trial_class,
            None,
            "id declares kind 'motion'",
            id="kind-disagrees",
        ),
    ],
)
def test_an_undeclared_trial_shape_fails(
    tmp_path: Path,
    event_id: str,
    kind: EventKind,
    stage: Stage | None,
    moment: Moment | None,
    outcome: dict[str, Any] | None,
    expected: str,
) -> None:
    data_root = tmp_path / "data"
    _event(data_root, event_id, kind=kind, stage=stage, moment=moment, outcome=outcome)
    check = _check(data_root)
    assert not check.passed
    assert any(expected in problem for problem in check.problems), check.problems
    assert check.checked == 1


def test_a_trial_event_records_its_moment_s_decision_target(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _event(
        data_root,
        "evt-motion-trial-class-90",
        kind=EventKind.motion,
        stage=Stage.trial,
        moment=Moment.trial_class,
        decision_target="disposition",
    )
    check = _check(data_root)
    assert not check.passed
    assert any("decision target is 'ruling'" in problem for problem in check.problems)


def test_an_event_that_never_mentions_the_stage_is_not_counted(tmp_path: Path) -> None:
    """The Court's ledger is outside the rule, and is passed over unparsed."""
    data_root = tmp_path / "data"
    _event(data_root, "evt-motion-stay", kind=EventKind.motion, stage=Stage.interim, moment=None)
    check = _check(data_root)
    assert check.passed and check.checked == 0
