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
