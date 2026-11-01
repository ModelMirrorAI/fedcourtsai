"""The policy-area vocabulary and its committed, hand-labeled reference."""

from __future__ import annotations

import json
import re
from datetime import date

import pytest

from fedcourtsai.pipeline import executive_success as executive_success_module
from fedcourtsai.pipeline.exec_action import EXEC_ACTION_RULE_VERSION
from fedcourtsai.pipeline.executive_success import _success
from fedcourtsai.pipeline.policy_area import (
    POLICY_AREA_RULE_VERSION,
    POLICY_AREAS,
    PolicyLabel,
    PolicySource,
    parse_policy_areas,
    policy_areas,
    policy_label,
)
from fedcourtsai.schemas import Disposition
from tests.test_executive_success import _app


def _document(labels: dict[str, object], version: str = POLICY_AREA_RULE_VERSION) -> str:
    return json.dumps({"rule_version": version, "labels": labels})


def test_the_committed_reference_parses_and_names_applications() -> None:
    labels = policy_areas()
    assert labels, "the reference is empty"
    assert all(re.fullmatch(r"\d{2}A\d+", docket) for docket in labels)
    assert {label.area for label in labels.values()} <= set(POLICY_AREAS)
    assert all(label.note for label in labels.values())
    assert POLICY_AREAS[-1] == "other"


def test_a_label_is_found_under_any_spelling() -> None:
    docket, label = next(iter(policy_areas().items()))
    assert policy_label(f" {docket.lower()} ") == label
    assert policy_label("99A99999") is None


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (_document({}, version="policy-area-v9"), "not 'policy-area-v1'"),
        (
            _document({"24A1": {"area": "tax", "note": "x", "uncertain": False}}),
            "unknown policy area",
        ),
        (
            '{"rule_version": "policy-area-v1", "labels": {'
            + '"24A1": {"area": "health", "note": "x", "uncertain": false}, '
            + '"24a1 ": {"area": "health", "note": "x", "uncertain": false}}}',
            "twice",
        ),
        (
            '{"rule_version": "policy-area-v1", "labels": {'
            + '"24A1": {"area": "health", "note": "x", "uncertain": false}, '
            + '"24A1": {"area": "other", "note": "x", "uncertain": false}}}',
            "twice",
        ),
        (
            _document({"24A1": {"area": "health", "note": "x", "uncertain": "false"}}),
            "uncertain a boolean",
        ),
        (_document({"24A1": {"area": "health", "note": "x"}}), "exactly area, note"),
    ],
)
def test_the_parser_refuses_what_it_cannot_read(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_policy_areas(text)


def test_the_cut_counts_in_scope_rows_by_area(monkeypatch: pytest.MonkeyPatch) -> None:
    noem = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."
    ohio = "Ohio, et al. v. Environmental Protection Agency, et al."
    labels = {
        "24A900": PolicyLabel("immigration", "parole termination", False),
        "24A901": PolicyLabel("immigration", "parole termination", True),
        "24A100": PolicyLabel("environment-energy", "emissions rule", False),
        "24A903": PolicyLabel("immigration", "parole termination", False),
        "24A104": PolicyLabel("personnel-removal", "service rule", False),
    }
    monkeypatch.setattr(
        executive_success_module,
        "hand_source",
        lambda: PolicySource(rule_version=POLICY_AREA_RULE_VERSION, labels=labels),
    )
    rows = [
        _app("scotus/1", noem, "24A900", date(2025, 3, 1), Disposition.granted),
        _app("scotus/2", noem, "24A901", date(2025, 3, 2), Disposition.denied),
        _app("scotus/3", noem, "24A902", date(2025, 3, 3), None),  # unlabeled
        _app("scotus/4", ohio, "24A100", date(2024, 7, 1), Disposition.denied),
        # Labeled but never parsed: listed with its area, counted in no cell.
        _app("scotus/5", noem, "24A903", date(2025, 3, 4), Disposition.granted, kind=None),
        # Unknown scope: listed with its area, counted in no cell either.
        _app(
            "scotus/6",
            "Jane Roe, et al. v. Austin, Secretary of Defense, et al.",
            "24A104",
            date(2024, 7, 5),
            Disposition.denied,
        ),
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
    assert result.policy_rule_version == POLICY_AREA_RULE_VERSION
    cells = {(c.administration, c.filer, c.area): c for c in result.policy_cells}
    immigration = cells[("trump-47", "government", "immigration")]
    assert (immigration.rows, immigration.decided, immigration.wins) == (2, 2, 1)
    environment = cells[("biden-46", "challenger", "environment-energy")]
    assert (environment.wins, environment.decided) == (1, 1)
    assert result.policy_unlabeled == 1
    # The policy cells partition the cut's own population: rows plus unlabeled.
    population = sum(c.rows for c in result.cells if c.filer != "all")
    assert sum(c.rows for c in result.policy_cells) + result.policy_unlabeled == population
    # Reporting order: administration, then the government's cells, then area.
    assert [c.area for c in result.policy_cells] == ["environment-energy", "immigration"]
    listed = {row.docket_number: row for row in result.review_rows}
    assert (listed["24A901"].policy_area, listed["24A901"].policy_uncertain) == (
        "immigration",
        True,
    )
    assert listed["24A902"].policy_area is None
    assert listed["24A903"].policy_area == "immigration"
    assert listed["24A104"].policy_area == "personnel-removal"
