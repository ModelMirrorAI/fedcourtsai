"""A cell's mis-shaped ``tooling.json`` is normalised where that is honest."""

from __future__ import annotations

import json

import pytest

from fedcourtsai.agent_flags import CellCoordinates
from fedcourtsai.agent_tooling import (
    _LIST_LIMIT,
    _MANIFEST_LIMIT,
    _NOTES_LIMIT,
    normalise_tooling,
)
from fedcourtsai.schemas import AgentToolingFeedback, UsageRole

WHERE = CellCoordinates("scotus/9026000517", "20261017T173457Z", UsageRole.predictor, "gemini-x")

# What a gemini predict cell wrote on 2026-10-17: three keys the schema has no
# place for, two of them saying "None".
INVENTED = {
    "case_id": "scotus/9026000517",
    "run_id": "20261017T173457Z",
    "role": "predictor",
    "actor_id": "gemini-x",
    "used_corpus_query": False,
    "used_mcp": False,
    "missing_tools": "None",
    "pain_points": "None",
}


def _report(raw: object) -> AgentToolingFeedback:
    result = normalise_tooling(json.dumps(raw), WHERE)
    assert result.changed is True
    assert result.feedback is not None
    return result.feedback


def test_the_caps_are_the_schemas_own() -> None:
    fields = AgentToolingFeedback.model_json_schema()["properties"]
    assert fields["gaps"]["maxItems"] == _LIST_LIMIT
    assert fields["tool_manifest"]["anyOf"][0]["maxItems"] == _MANIFEST_LIMIT
    assert fields["notes"]["anyOf"][0]["maxLength"] == _NOTES_LIMIT


def test_a_valid_report_is_left_as_written() -> None:
    valid = dict(INVENTED)
    for key in ("used_mcp", "missing_tools", "pain_points"):
        del valid[key]
    result = normalise_tooling(json.dumps(valid), WHERE)
    assert result == (result.__class__(None, changed=False))


def test_invented_keys_are_dropped_and_named() -> None:
    report = _report(INVENTED)
    assert report.used_corpus_query is False
    assert report.notes is not None
    assert report.notes.startswith("[harness] tooling.json did not validate")
    for key in ("used_mcp", "missing_tools", "pain_points"):
        assert f"unknown key {key!r}" in report.notes


def test_the_result_is_stable_under_a_second_pass() -> None:
    once = _report(INVENTED)
    again = normalise_tooling(once.model_dump_json(), WHERE)
    assert again.changed is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [("None", []), ("n/a", []), ("a query tool", ["a query tool"]), ([1, "x", ""], ["1", "x"])],
)
def test_a_list_field_written_otherwise_is_read_as_a_list(
    value: object, expected: list[str]
) -> None:
    raw = {**INVENTED, "gaps": value}
    assert _report(raw).gaps == expected


def test_a_long_list_is_cut_at_the_cap() -> None:
    raw = {**INVENTED, "helpful": [f"h{i}" for i in range(80)]}
    assert len(_report(raw).helpful) == _LIST_LIMIT


@pytest.mark.parametrize(("word", "expected"), [("yes", True), ("false", False), ("TRUE", True)])
def test_a_yes_or_no_word_is_read_for_the_corpus_answer(word: str, expected: bool) -> None:
    report = _report({**INVENTED, "used_corpus_query": word})
    assert report.used_corpus_query is expected


@pytest.mark.parametrize("value", [None, "maybe", 3, [True]])
def test_no_corpus_answer_is_invented(value: object) -> None:
    raw = dict(INVENTED)
    if value is None:
        del raw["used_corpus_query"]
    else:
        raw["used_corpus_query"] = value
    result = normalise_tooling(json.dumps(raw), WHERE)
    assert result.feedback is None
    assert result.changed is False


@pytest.mark.parametrize("text", ["", "not json", "[1, 2]", '{"used_corpus_query": tr'])
def test_a_file_with_no_report_in_it_is_left_alone(text: str) -> None:
    result = normalise_tooling(text, WHERE)
    assert result.feedback is None
    assert result.changed is False


def test_a_missing_envelope_is_filled_from_the_cell() -> None:
    raw = {"used_corpus_query": True, "role": "judge"}
    report = _report(raw)
    assert (report.case_id, report.run_id, report.actor_id) == (
        WHERE.case_id,
        WHERE.run_id,
        WHERE.actor_id,
    )
    assert report.role == UsageRole.predictor


def test_the_agents_notes_come_first_and_the_whole_stays_in_bounds() -> None:
    own = "the corpus query timed out twice"
    report = _report({**INVENTED, "notes": own})
    assert report.notes is not None and report.notes.startswith(own + "\n[harness]")
    long = _report({**INVENTED, "notes": "n" * 1990})
    assert long.notes is not None and len(long.notes) <= _NOTES_LIMIT


def test_a_malformed_manifest_is_dropped_and_named() -> None:
    report = _report({**INVENTED, "tool_manifest": "courtlistener"})
    assert report.tool_manifest is None
    assert report.notes is not None and "tool_manifest" in report.notes
