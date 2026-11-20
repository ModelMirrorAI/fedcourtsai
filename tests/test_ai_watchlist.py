"""The AI-case watchlist config: the committed file loads, and its checks refuse bad rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from fedcourtsai.ai_watchlist import (
    AI_TAG,
    AiWatchlist,
    Relation,
    load_ai_watchlist,
    tagged_case_ids,
)

_ROOT = Path(__file__).resolve().parent.parent
_COMMITTED = _ROOT / "config" / "ai-watchlist.yaml"


def _case(**overrides: Any) -> dict[str, Any]:
    case: dict[str, Any] = {
        "name": "Doe v. Model Co.",
        "court": "cand",
        "docket_id": 101,
        "docket_number": "3:26-cv-00001",
        "category": "copyright",
        "why": "Training on protected works.",
        "developers": ["Model Co."],
        "added": "2026-10-30",
        "related": [
            {"court": "ca9", "docket_id": 202, "docket_number": "26-1", "relation": "appeal"}
        ],
    }
    case.update(overrides)
    return case


def _watchlist(*cases: dict[str, Any]) -> dict[str, Any]:
    return {
        "categories": {"copyright": "Protected works.", "antitrust": "Competition."},
        "cases": list(cases) or [_case()],
    }


def test_committed_watchlist_loads() -> None:
    watchlist = load_ai_watchlist(_COMMITTED)

    assert watchlist.cases
    assert all(case.added <= date.today() for case in watchlist.cases)


def test_tag_covers_every_docket_a_case_names() -> None:
    watchlist = AiWatchlist.model_validate(_watchlist())

    assert AI_TAG == "ai"
    assert tagged_case_ids(watchlist) == frozenset({"cand/101", "ca9/202"})


def test_by_category_keeps_empty_categories() -> None:
    watchlist = AiWatchlist.model_validate(_watchlist())

    grouped = watchlist.by_category()
    assert [case.name for case in grouped["copyright"]] == ["Doe v. Model Co."]
    assert grouped["antitrust"] == []


def test_relation_vocabulary() -> None:
    assert {r.value for r in Relation} == {"appeal", "transfer", "mdl", "member", "companion"}


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (_watchlist(_case(category="privacy")), "is not one of"),
        (_watchlist(_case(court="scotus", related=[])), "SCOTUS docket is never listed"),
        (
            _watchlist(
                _case(
                    related=[
                        {
                            "court": "scotus",
                            "docket_id": 9,
                            "docket_number": "26-5",
                            "relation": "appeal",
                        }
                    ]
                )
            ),
            "SCOTUS docket is never listed",
        ),
        (_watchlist(_case(), _case(name="Again", related=[])), "named twice"),
        (
            _watchlist(_case(), _case(name="Shares the appeal", docket_id=303)),
            "named twice",
        ),
        (_watchlist(_case(), _case(docket_id=999, related=[])), "names must be distinct"),
        (
            _watchlist(_case(), _case(name="Mistyped id", docket_id=999, related=[])),
            "docket number 3:26-cv-00001 is named twice",
        ),
        (_watchlist(_case(developers=[])), "at least 1"),
        (_watchlist(_case(developers=["A", "A"])), "distinct"),
        (_watchlist(_case(court="N.D. Cal.")), "pattern"),
        (_watchlist(_case(unexpected=True)), "Extra inputs"),
        (
            _watchlist(
                _case(
                    related=[
                        {"court": "ca9", "docket_id": 5, "docket_number": "x", "relation": "cousin"}
                    ]
                )
            ),
            "relation",
        ),
        ({"categories": {"Copyright": "Bad name."}, "cases": [_case()]}, "kebab-case"),
        ({"categories": {"copyright": " "}, "cases": [_case()]}, "needs a description"),
    ],
)
def test_refuses_bad_rows(data: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        AiWatchlist.model_validate(data)


def test_missing_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_ai_watchlist(tmp_path / "ai-watchlist.yaml")


def test_repeated_key_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "ai-watchlist.yaml"
    path.write_text("categories:\n  copyright: One.\n  copyright: Two.\ncases: []\n")
    with pytest.raises(ValueError, match="duplicate key"):
        load_ai_watchlist(path)


def test_empty_file_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "ai-watchlist.yaml"
    path.write_text("")
    with pytest.raises(ValidationError):
        load_ai_watchlist(path)


def _state_watchlist(**overrides: Any) -> dict[str, Any]:
    case: dict[str, Any] = {
        "name": "Fund v. Model Co.",
        "court": "ca-super-sf",
        "case_number": "CGC-26-000001",
        "category": "copyright",
        "why": "An order sought against model development.",
        "developers": ["Model Co."],
        "added": "2026-11-20",
        "entries": [
            {"date": "2026-11-12", "kind": "complaint"},
            {"date": "2026-11-19", "kind": "motion", "motion": "dismiss"},
        ],
    }
    case.update(overrides)
    return {
        **_watchlist(),
        "state_courts": {
            "ca-super-sf": {
                "name": "Superior Court of California, County of San Francisco",
                "short": "S.F. Super. Ct.",
                "case_information": "https://court.example/case-information",
            }
        },
        "state_cases": [case],
    }


def test_a_state_case_is_listed_by_case_number_and_carries_no_tag() -> None:
    watchlist = AiWatchlist.model_validate(_state_watchlist())

    (case,) = watchlist.state_cases
    assert case.case_number == "CGC-26-000001"
    assert [entry.kind for entry in case.entries] == ["complaint", "motion"]
    assert tagged_case_ids(watchlist) == frozenset({"cand/101", "ca9/202"})


def test_the_committed_watchlist_admits_one_state_court() -> None:
    watchlist = load_ai_watchlist(_COMMITTED)

    assert set(watchlist.state_courts) == {"ca-super-sf"}
    assert all(case.court in watchlist.state_courts for case in watchlist.state_cases)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"court": "ca-super-la"}, "not one of the admitted state courts"),
        ({"category": "tax"}, "is not one of"),
        ({"name": "Doe v. Model Co."}, "case names must be distinct"),
        ({"developers": []}, "developers"),
        ({"docket_id": 5}, "Extra inputs"),
        (
            {
                "entries": [
                    {"date": "2026-11-19", "kind": "motion"},
                    {"date": "2026-11-12", "kind": "complaint"},
                ]
            },
            "date order",
        ),
        ({"entries": [{"date": "2026-11-12", "kind": "hearing"}]}, "kind"),
        (
            {"entries": [{"date": "2026-11-12", "kind": "complaint", "motion": "dismiss"}]},
            "names no motion",
        ),
        ({"entries": [{"date": "2026-11-12", "kind": "complaint", "text": "x"}]}, "Extra inputs"),
    ],
)
def test_a_bad_state_case_is_refused(overrides: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        AiWatchlist.model_validate(_state_watchlist(**overrides))


def test_a_state_court_id_cannot_pass_for_a_courtlistener_id() -> None:
    data = _state_watchlist()
    data["state_courts"]["casf"] = data["state_courts"].pop("ca-super-sf")

    with pytest.raises(ValidationError, match="postal code and hyphenated parts"):
        AiWatchlist.model_validate(data)


def test_a_state_case_number_is_listed_once() -> None:
    data = _state_watchlist()
    data["state_cases"].append({**data["state_cases"][0], "name": "Other v. Model Co."})

    with pytest.raises(ValidationError, match="named twice"):
        AiWatchlist.model_validate(data)


def test_a_state_courts_page_is_an_https_link_that_cannot_break_out_of_one() -> None:
    for bad in ("http://court.example/x", "https://court.example/x)"):
        data = _state_watchlist()
        data["state_courts"]["ca-super-sf"]["case_information"] = bad
        with pytest.raises(ValidationError, match="case_information"):
            AiWatchlist.model_validate(data)
