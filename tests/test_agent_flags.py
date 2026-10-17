"""The flag normaliser, the roll-up's grouping, and the committed theme map."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fedcourtsai.agent_flags import (
    FLAG_MESSAGE_LIMIT,
    NORMALISED_PREFIX,
    CellCoordinates,
    FlagTheme,
    coordinates_from_path,
    load_flag_themes,
    normalise_flags,
    roll_up,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    FlagCategory,
    FlagSeverity,
    FlagSource,
    UsageRole,
)

_WHERE = CellCoordinates(
    case_id="scotus/1", run_id="R", role=UsageRole.evaluator, actor_id="gemini-judge"
)


def _envelope(*flags: object, **extra: object) -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "case_id": "scotus/1",
            "run_id": "R",
            "role": "evaluator",
            "actor_id": "gemini-judge",
            "flags": list(flags),
            **extra,
        }
    )


def _round_trips(flags: AgentFlags) -> None:
    """Whatever came in, what comes out is schema-true."""
    AgentFlags.model_validate_json(flags.model_dump_json())


def test_a_valid_file_comes_back_unchanged() -> None:
    text = _envelope({"category": "scope", "severity": "warning", "message": "m"})
    result = normalise_flags(text, _WHERE)
    assert not result.changed
    assert result.flags == AgentFlags.model_validate_json(text)


def _flag_item(**override: object) -> dict[str, object]:
    return {"category": "scope", "severity": "info", "message": "m", **override}


@pytest.mark.parametrize(
    "text",
    [
        _envelope(_flag_item(), role=["predictor"]),
        _envelope(_flag_item(), role={"a": 1}),
        _envelope(_flag_item(), case_id=["scotus/1"]),
        _envelope(_flag_item(), case_id={"court": "scotus"}),
        _envelope(_flag_item(), schema_version=["1.0"]),
        _envelope(_flag_item(source={})),
        _envelope(_flag_item(source=["harness"])),
        _envelope(_flag_item(severity=["low"])),
        _envelope(_flag_item(severity={"level": "low"})),
        _envelope(_flag_item(category=["scope"])),
        _envelope(_flag_item(event_id={"id": "e"})),
        _envelope(_flag_item(message=["m"])),
        _envelope(_flag_item(), flags={"message": "m"}),
        "[" * 100000 + "]" * 100000,
        '{"flags": ' + "[" * 100000 + "]" * 100000 + "}",
    ],
    ids=[
        "role-list",
        "role-dict",
        "case-list",
        "case-dict",
        "schema-version-list",
        "source-dict",
        "source-list",
        "severity-list",
        "severity-dict",
        "category-list",
        "event-dict",
        "message-list",
        "flags-dict",
        "deep-list",
        "deep-flags",
    ],
)
def test_normalisation_is_total_on_hostile_shapes(text: str) -> None:
    """No shape an agent can write makes the normaliser raise, and its output is stable."""
    result = normalise_flags(text, _WHERE)
    assert result.changed
    _round_trips(result.flags)
    again = normalise_flags(result.flags.model_dump_json(), _WHERE)
    assert not again.changed


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("low", FlagSeverity.info),
        ("Minor", FlagSeverity.info),
        ("note", FlagSeverity.info),
        ("trivial", FlagSeverity.info),
        ("medium", FlagSeverity.warning),
        ("moderate", FlagSeverity.warning),
        ("HIGH", FlagSeverity.warning),
        ("warn", FlagSeverity.warning),
        ("error", FlagSeverity.warning),
        ("critical", FlagSeverity.warning),
        ("severe", FlagSeverity.warning),
        ("fatal", FlagSeverity.warning),
        ("bogus", FlagSeverity.warning),
        (3, FlagSeverity.warning),
        ("Blocker", FlagSeverity.blocker),
    ],
)
def test_a_severity_synonym_maps_by_table_and_an_unknown_one_to_warning(
    value: object, expected: FlagSeverity
) -> None:
    """Only the schema's own `blocker`, however spelled, ever reads as a blocker."""
    result = normalise_flags(_envelope(_flag_item(severity=value)), _WHERE)
    assert result.flags.flags[0].severity == expected
    assert repr(value) in result.flags.flags[-1].message


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("severity", "low", FlagSeverity.info),
        ("severity", "critical", FlagSeverity.warning),
        ("severity", "Warning", FlagSeverity.warning),
        ("severity", 3, FlagSeverity.warning),
        ("category", "capture-gap", FlagCategory.other),
        ("category", "data_quality", FlagCategory.data_quality),
        ("category", "Ambiguous Event", FlagCategory.ambiguous_event),
    ],
)
def test_an_off_vocabulary_value_is_coerced_and_quoted(
    field: str, value: object, expected: str
) -> None:
    item = {"category": "other", "severity": "info", "message": "keep me", field: value}
    result = normalise_flags(_envelope(item), _WHERE)
    assert result.changed
    _round_trips(result.flags)
    coerced, note = result.flags.flags
    assert getattr(coerced, field) == expected
    assert coerced.normalised is True
    assert coerced.message == "keep me"
    assert note.source == FlagSource.harness
    assert note.message.startswith(NORMALISED_PREFIX)
    assert repr(value) in note.message


def test_only_the_mis_shaped_flag_is_marked() -> None:
    result = normalise_flags(
        _envelope(
            {"category": "scope", "message": "fine"},
            {"category": "scope", "severity": "low", "message": "off"},
        ),
        _WHERE,
    )
    fine, off, note = result.flags.flags
    assert (fine.normalised, off.normalised) == (False, True)
    assert "flag 2: severity 'low'" in note.message


def test_an_over_long_message_continues_whole_across_flags() -> None:
    """A long disclosure is never cut: its text continues in further flags."""
    message = "".join(str(i % 10) for i in range(2 * FLAG_MESSAGE_LIMIT + 50))
    result = normalise_flags(
        _envelope(
            {"category": "data-quality", "severity": "warning", "message": message, "event_id": "e"}
        ),
        _WHERE,
    )
    _round_trips(result.flags)
    *parts, note = result.flags.flags
    assert len(parts) == 3
    assert "".join(part.message for part in parts) == message
    assert {(p.category, p.severity, p.event_id, p.normalised) for p in parts} == {
        (FlagCategory.data_quality, FlagSeverity.warning, "e", True)
    }
    assert "continued across 3 flags" in note.message


def test_a_non_text_message_is_carried_as_its_json() -> None:
    result = normalise_flags(_envelope({"category": "other", "message": {"why": "gap"}}), _WHERE)
    assert result.flags.flags[0].message == '{"why": "gap"}'


def test_unknown_keys_are_dropped_and_their_values_quoted() -> None:
    result = normalise_flags(
        _envelope({"category": "other", "message": "m", "confidence": "high"}, notes="n"), _WHERE
    )
    _round_trips(result.flags)
    note = result.flags.flags[-1].message
    assert "confidence='high'" in note and "notes='n'" in note


def test_a_missing_envelope_is_filled_from_the_harness_coordinates() -> None:
    result = normalise_flags(json.dumps({"flags": ["a bare string note"]}), _WHERE)
    _round_trips(result.flags)
    flags = result.flags
    assert (flags.case_id, flags.run_id, flags.role, flags.actor_id) == (
        "scotus/1",
        "R",
        UsageRole.evaluator,
        "gemini-judge",
    )
    assert flags.flags[0].message == "a bare string note"
    assert flags.flags[0].category == FlagCategory.other


def test_a_present_envelope_field_is_kept_as_written() -> None:
    text = json.dumps(
        {
            "case_id": "scotus/2",
            "run_id": "R",
            "role": "evaluator",
            "actor_id": "gemini-judge",
            "flags": [{"category": "x", "message": "m"}],
        }
    )
    assert normalise_flags(text, _WHERE).flags.case_id == "scotus/2"


def test_a_bare_list_reads_as_the_flags() -> None:
    result = normalise_flags(json.dumps([{"category": "scope", "message": "m"}]), _WHERE)
    _round_trips(result.flags)
    assert result.flags.flags[0].category == FlagCategory.scope


@pytest.mark.parametrize("text", ['{"flags": [ truncated', "42", '"just text"', ""])
def test_a_file_with_no_structure_is_carried_verbatim(text: str) -> None:
    result = normalise_flags(text, _WHERE)
    assert result.changed
    _round_trips(result.flags)
    head, *body = result.flags.flags
    assert head.message.startswith(NORMALISED_PREFIX)
    assert all(flag.source == FlagSource.harness for flag in result.flags.flags)
    assert "".join(flag.message for flag in body) == (text or "(empty)")


def test_a_long_unparseable_file_is_kept_whole_across_parts() -> None:
    text = "{" + "y" * (3 * FLAG_MESSAGE_LIMIT)
    result = normalise_flags(text, _WHERE)
    _round_trips(result.flags)
    assert "".join(flag.message for flag in result.flags.flags[1:]) == text


def test_an_empty_flag_list_still_yields_a_valid_set() -> None:
    result = normalise_flags(_envelope(), _WHERE)
    _round_trips(result.flags)
    assert "no usable flag survived" in result.flags.flags[-1].message


def test_normalisation_is_idempotent() -> None:
    once = normalise_flags(_envelope({"category": "nope", "message": "m"}), _WHERE).flags
    again = normalise_flags(once.model_dump_json(), _WHERE)
    assert not again.changed
    assert again.flags == once


def test_coordinates_are_read_off_the_ledger_path(tmp_path: Path) -> None:
    event = CasePaths(tmp_path / "data", "scotus", 9).event("evt-x")
    assert coordinates_from_path(event.evaluation_flags("gemini-judge", "R")) == CellCoordinates(
        "scotus/9", "R", UsageRole.evaluator, "gemini-judge"
    )
    assert coordinates_from_path(event.prediction_flags("claude-baseline", "R")) == (
        CellCoordinates("scotus/9", "R", UsageRole.predictor, "claude-baseline")
    )
    assert coordinates_from_path(tmp_path / "data" / "flags.json") is None


def test_the_committed_theme_map_loads_and_each_theme_matches_its_own_example() -> None:
    themes = load_flag_themes()
    assert themes, "the committed map names at least one tracked theme"
    by_issue = {theme.issue: theme for theme in themes}
    distribution = by_issue[1858]
    assert distribution.matches(
        "Frozen distribution_count=2 counts the May 19 distribution of sealing motion 25M82"
    )
    # Mentioning the field is not enough to be swept into the tracked count.
    assert not distribution.matches("distribution_count is 0 at a distribution moment")


def test_a_theme_id_registered_twice_is_refused() -> None:
    theme = {"id": "t", "issue": 1, "summary": "s", "all_of": ["x"]}
    with pytest.raises(ValueError, match="twice"):
        load_flag_themes(json.dumps({"themes": [theme, theme]}))


def test_a_theme_with_a_broken_pattern_is_refused() -> None:
    with pytest.raises(ValueError):
        load_flag_themes(
            json.dumps({"themes": [{"id": "t", "issue": 1, "summary": "s", "all_of": ["("]}]})
        )


def test_roll_up_counts_repeats_across_runs_into_one_group() -> None:
    sets = [
        AgentFlags(
            case_id="scotus/1",
            run_id=run,
            role=UsageRole.predictor,
            actor_id="a",
            flags=[AgentFlag(category=FlagCategory.other, message="same", event_id="e")],
        )
        for run in ("R1", "R2")
    ]
    rollup = roll_up(sets, themes=(FlagTheme(id="x", issue=1, summary="s", all_of=("nomatch",)),))
    (group,) = rollup.groups
    assert (group.count, group.actors, group.runs) == (2, ["a"], {"R1", "R2"})
