"""The policy keys: a hand-labeled grouping counted beside the controversy rule's."""

from __future__ import annotations

import json
import re
from datetime import date

import pytest

from fedcourtsai.pipeline import executive_success as executive_success_module
from fedcourtsai.pipeline.controversy import group_controversies
from fedcourtsai.pipeline.exec_action import EXEC_ACTION_RULE_VERSION
from fedcourtsai.pipeline.executive_success import _success
from fedcourtsai.pipeline.policy_key import (
    POLICY_KEY_RULE_VERSION,
    PolicyKey,
    parse_policy_keys,
    policy_key,
    policy_keys,
)
from fedcourtsai.schemas import Disposition
from tests.test_executive_success import _app, _links


def _document(keys: dict[str, object], version: str = POLICY_KEY_RULE_VERSION) -> str:
    return json.dumps({"rule_version": version, "keys": keys})


def test_the_committed_keys_parse_and_name_applications() -> None:
    keys = policy_keys()
    assert keys, "the reference is empty"
    assert all(re.fullmatch(r"\d{2}A\d+", docket) for docket in keys)
    assert all(found.note and len(found.dockets) >= 2 for found in keys.values())
    assert keys["17A550"].key == "travel-ban"


def test_a_key_is_found_under_any_spelling() -> None:
    assert policy_key(" 17a550 ") == policy_key("17A550")
    assert policy_key("99A99999") is None


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (_document({}, version="policy-key-v9"), "not 'policy-key-v1'"),
        (_document({"k": {"note": "x", "dockets": ["24A1"]}}), "at least two"),
        # Three entries, so the repeat is past the at-least-two check.
        (_document({"k": {"note": "x", "dockets": ["24A1", "24a1 ", "24A2"]}}), "twice"),
        ("[]", "a keys object"),
        ('{"rule_version": "policy-key-v1"}', "a keys object"),
        (_document({" ": {"note": "x", "dockets": ["24A1", "24A2"]}}), "needs a name"),
        (
            _document(
                {
                    "k": {"note": "x", "dockets": ["24A1", "24A2"]},
                    "j": {"note": "y", "dockets": ["24A3", "24a2"]},
                }
            ),
            "sits under k and j",
        ),
        (
            '{"rule_version": "policy-key-v1", "keys": {'
            + '"k": {"note": "x", "dockets": ["24A1", "24A2"]}, '
            + '"k": {"note": "x", "dockets": ["24A3", "24A4"]}}}',
            "twice",
        ),
        (_document({"k": {"note": "", "dockets": ["24A1", "24A2"]}}), "non-empty"),
        (_document({"k": {"note": "x", "dockets": "24A1"}}), "list of docket numbers"),
        (_document({"k": {"dockets": ["24A1", "24A2"]}}), "exactly note and dockets"),
    ],
)
def test_the_parser_refuses_what_it_cannot_read(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_policy_keys(text)


def test_a_key_joins_on_top_of_the_rules_links() -> None:
    links = [
        _links("24A95", lower={("ca9", "25-1")}),
        _links("24A105", lower={("ca9", "25-1")}),
        _links("24A300", lower={("ca5", "25-9")}),  # same policy, another court
        _links("24A400"),  # unkeyed, unlinked
    ]
    keys = {"24A300": "rule", "24A95": "rule"}
    assert group_controversies(links) == {
        "24A95": "24A95",
        "24A105": "24A95",
        "24A300": "24A300",
        "24A400": "24A400",
    }
    assert group_controversies(links, keyed=keys.get) == {
        "24A95": "24A95",
        "24A105": "24A95",
        "24A300": "24A95",
        "24A400": "24A400",
    }


def test_the_keyed_cells_sit_beside_the_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    ohio = "Ohio, et al. v. Environmental Protection Agency, et al."
    utah = "Utah, et al. v. Environmental Protection Agency, et al."
    keys = {
        docket: PolicyKey("emissions-rule", "one rule", ("24A100", "24A101"))
        for docket in ("24A100", "24A101")
    }
    monkeypatch.setattr(
        executive_success_module, "policy_key", lambda docket: keys.get(docket.strip())
    )
    rows = [
        # Two states' challenges to one rule, from two courts, decided apart.
        _app("scotus/1", ohio, "24A100", date(2024, 7, 1), Disposition.denied),
        _app("scotus/2", utah, "24A101", date(2024, 8, 1), Disposition.granted),
        _app("scotus/3", ohio, "24A102", date(2024, 9, 1), Disposition.denied),
    ]
    result = _success(
        rows,
        as_of_field="filed",
        through=None,
        since=None,
        corpus_sha256="",
        scope_rule_version=EXEC_ACTION_RULE_VERSION,
        fetch=None,
        reading="registered",
        latest_pull=None,
        latest_snapshot=None,
    )
    assert result.policy_key_rule_version == POLICY_KEY_RULE_VERSION
    rule = {(c.administration, c.filer): c for c in result.controversy_cells}
    keyed = {(c.administration, c.filer): c for c in result.policy_controversy_cells}
    # The rule keeps all three apart; the key joins two, which take the later result.
    assert rule[("biden-46", "challenger")].controversies == 3
    challenger = keyed[("biden-46", "challenger")]
    assert (challenger.controversies, challenger.applications) == (2, 3)
    assert (challenger.wins, challenger.determinate) == (1, 2)
    assert result.policy_key_joins == 1
    listed = {row.docket_number: row for row in result.review_rows}
    assert listed["24A101"].controversy_id == "24A101"
    assert listed["24A101"].policy_controversy_id == "24A100"
    assert listed["24A102"].policy_controversy_id == "24A102"
