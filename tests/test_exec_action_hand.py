"""The committed hand reading and the ``exec-action-v3`` scope rule that applies it."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline import exec_action as exec_action_module
from fedcourtsai.pipeline.exec_action import (
    EXEC_ACTION_RULE_VERSION,
    EXEC_ACTION_RULE_VERSION_V3,
    EXEC_ACTION_RULE_VERSION_V5,
    exec_action_rule,
    hand_codes,
    parse_hand_codes,
)


def _document(rows: dict[str, object], version: str = EXEC_ACTION_RULE_VERSION_V3) -> str:
    return json.dumps({"rule_version": version, "rows": rows})


def _row(case_name: str, docket_number: str) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=f"scotus/{docket_number}",
        court="scotus",
        case_name=case_name,
        docket_number=docket_number,
        date_filed=date(2024, 3, 1),
        application_kind="substantive",
        last_live_polled=date(2026, 9, 1),
    )


def test_the_committed_reading_parses_and_names_applications() -> None:
    codes = hand_codes()
    assert all(re.fullmatch(r"\d{2}A\d+", docket) for docket in codes)
    reasons = Counter(code.reason for code in codes.values())
    assert reasons["hand-in-scope"] > 150 and reasons["hand-out-of-scope"] > 100
    # Two of the rule's government applications the hand reading sets aside, and
    # one challenge the caption reads as a prosecution that it puts in scope.
    assert codes["23A87"].reason == "hand-out-of-scope"
    assert codes["23A814"].reason == "hand-out-of-scope"
    assert (codes["23A469"].reason, codes["23A469"].government_side) == (
        "hand-in-scope",
        "respondent",
    )


def test_a_hand_code_replaces_the_caption_reading() -> None:
    v2, v3 = (
        exec_action_rule(EXEC_ACTION_RULE_VERSION),
        exec_action_rule(EXEC_ACTION_RULE_VERSION_V3),
    )
    listed = _row("United States v. Missouri, et al.", "23A814")
    assert v2(listed, None, None).reason == "gov-applicant"
    hand = v3(listed, None, None)
    assert (hand.rule_version, hand.in_scope, hand.reason) == (
        "exec-action-v3",
        False,
        "hand-out-of-scope",
    )
    unlisted = _row("Kristi Noem, Secretary of Homeland Security v. Doe", "24A99999")
    rule = v3(unlisted, None, None)
    assert (rule.rule_version, rule.reason, rule.government_side) == (
        "exec-action-v3",
        "gov-applicant",
        "applicant",
    )


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (_document({}, version="exec-action-v2"), "not 'exec-action-v3'"),
        (json.dumps({"rule_version": "exec-action-v3"}), "rows object"),
        (_document({"23A1": {"scope": "maybe", "basis": "adjudicated"}}), "unknown scope"),
        (
            _document({"23A1": {"scope": "out", "government_side": "both", "basis": "override"}}),
            "unknown government side",
        ),
        (_document({"23A1": {"scope": "out", "basis": "guess"}}), "unknown basis"),
        (_document({"23A1": {"scope": "in", "basis": "adjudicated"}}), "names the government"),
        (_document({"23A1": {"scope": "out", "basis": "override", "note": "x"}}), "a code holds"),
        (
            _document(
                {
                    "23A1": {"scope": "out", "basis": "override"},
                    " 23a1": {"scope": "out", "basis": "override"},
                }
            ),
            "lists 23A1 twice",
        ),
        (
            '{"rule_version": "exec-action-v3", "rows": {'
            + '"23A1": {"scope": "out", "basis": "override"}, '
            + '"23A1": {"scope": "in", "government_side": "applicant", "basis": "override"}}}',
            "lists 23A1 twice",
        ),
    ],
)
def test_a_malformed_reading_is_refused(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_hand_codes(text)


def test_the_hand_side_replaces_the_caption_side_and_falls_back_to_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    codes = parse_hand_codes(
        _document(
            {
                "24A1": {"scope": "in", "government_side": "respondent", "basis": "override"},
                "24A2": {"scope": "unclear", "basis": "adjudicated"},
            }
        )
    )
    monkeypatch.setattr(exec_action_module, "hand_codes", lambda: codes)
    v2, v3 = (
        exec_action_rule(EXEC_ACTION_RULE_VERSION),
        exec_action_rule(EXEC_ACTION_RULE_VERSION_V3),
    )
    caption = "Kristi Noem, Secretary of Homeland Security v. Doe"
    replaced = _row(caption, "24A1")
    assert v2(replaced, None, None).government_side == "applicant"
    assert v3(replaced, None, None).government_side == "respondent"
    kept = _row(caption, "24A2")
    hand = v3(kept, None, None)
    assert (hand.reason, hand.in_scope, hand.government_side) == (
        "hand-unclear",
        None,
        "applicant",
    )


def test_v5_applies_the_hand_reading_over_v4() -> None:
    v5 = exec_action_rule(EXEC_ACTION_RULE_VERSION_V5)
    listed = _row("Mike Moyle, Speaker, et al. v. United States", "23A469")
    hand = v5(listed, None, None)
    assert (hand.rule_version, hand.reason, hand.government_side) == (
        "exec-action-v5",
        "hand-in-scope",
        "respondent",
    )
    unlisted = _row("United States v. California, et al.", "26A99999")
    rule = v5(unlisted, None, None)
    assert (rule.rule_version, rule.reason, rule.in_scope) == (
        "exec-action-v5",
        "suit-against-state-law",
        False,
    )
