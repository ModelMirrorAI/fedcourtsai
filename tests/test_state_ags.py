"""The state-AGs registry: the committed file loads, its checks refuse bad rows, and tiers rank."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from fedcourtsai.state_ags import (
    AMBITION_METHOD,
    JURISDICTIONS,
    Kind,
    Rung,
    StateAgRegistry,
    Track,
    load_state_ags,
    rung,
    track,
)

_ROOT = Path(__file__).resolve().parent.parent
_COMMITTED = _ROOT / "config" / "state-ags.yaml"


def _holder(**overrides: Any) -> dict[str, Any]:
    holder: dict[str, Any] = {
        "name": "A. General",
        "party": "R",
        "status": "serving",
        "start": "2023-01-01",
        "sources": ["https://ag.example.gov/about"],
    }
    holder.update(overrides)
    return holder


def _office(state: str, *holders: dict[str, Any]) -> dict[str, Any]:
    return {"state": state, "selection": "elected", "holders": list(holders) or [_holder()]}


def _action(**overrides: Any) -> dict[str, Any]:
    action: dict[str, Any] = {
        "id": "tx-v-model-co",
        "title": "Texas v. Model Co.",
        "announced": "2026-03-01",
        "kind": "suit",
        "category": "child-safety",
        "states": ["TX"],
        "developers": ["Model Co."],
        "court": "Tex. Dist. Ct. (Travis County)",
        "docket_number": "D-1-GN-26-000001",
        "why": "A chatbot's outputs to minors.",
        "sources": ["https://ag.example.gov/news/1"],
        "added": "2026-11-05",
    }
    action.update(overrides)
    return action


def _registry(
    *actions: dict[str, Any], offices: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    return {
        "categories": {"child-safety": "Minors.", "privacy": "Data."},
        "offices": offices if offices is not None else [],
        "actions": list(actions),
    }


def _all_offices() -> list[dict[str, Any]]:
    return [_office(state) for state in sorted(JURISDICTIONS)]


def test_committed_registry_loads() -> None:
    registry = load_state_ags(_COMMITTED)

    assert registry.categories
    assert all(action.added <= date.today() for action in registry.actions)


def test_jurisdictions_are_the_states_and_dc() -> None:
    assert len(JURISDICTIONS) == 51
    assert "DC" in JURISDICTIONS
    assert AMBITION_METHOD == "ag-ai-ambition-v1"


@pytest.mark.parametrize(
    ("kind", "led", "multistate", "expected"),
    [
        (Kind.letter, True, True, Rung.signals),
        (Kind.letter, False, True, Rung.signals),
        (Kind.amicus, True, True, Rung.joins),
        (Kind.investigation, False, True, Rung.joins),
        (Kind.investigation, True, False, Rung.investigates),
        (Kind.settlement, True, True, Rung.investigates),
        (Kind.suit, False, True, Rung.joins),
        (Kind.suit, True, True, Rung.sues),
        (Kind.suit, True, False, Rung.sues),
        (Kind.defense, True, False, Rung.none),
        (Kind.advocacy, True, True, Rung.none),
    ],
)
def test_rung_ladder(kind: Kind, led: bool, multistate: bool, expected: Rung) -> None:
    assert rung(kind, led=led, multistate=multistate) is expected


def test_only_enforcement_kinds_raise_a_tier() -> None:
    assert {k for k in Kind if track(k) is not Track.enforcement} == {Kind.defense, Kind.advocacy}


def test_tier_takes_the_highest_rung_in_the_window() -> None:
    registry = StateAgRegistry.model_validate(
        _registry(
            _action(),
            _action(
                id="multistate-letter",
                kind="letter",
                states=["TX", "CA", "NY"],
                lead="CA",
                court=None,
                docket_number=None,
            ),
            _action(
                id="old-ca-suit",
                announced="2023-06-01",
                states=["CA"],
            ),
        )
    )

    on = date(2026, 11, 5)
    assert registry.tier("TX", on) is Rung.sues
    assert registry.tier("NY", on) is Rung.signals
    # CA's suit is outside the 730-day window; only the letter it led counts.
    assert registry.tier("CA", on) is Rung.signals
    assert registry.tier("WY", on) is Rung.none
    # An action dated after the reading day does not count yet.
    assert registry.tier("TX", date(2026, 2, 1)) is Rung.none


def test_multistate_suit_ranks_the_lead_above_the_joiners() -> None:
    registry = StateAgRegistry.model_validate(_registry(_action(states=["TX", "UT"], lead="UT")))

    assert registry.tier("UT", date(2026, 11, 5)) is Rung.sues
    assert registry.tier("TX", date(2026, 11, 5)) is Rung.joins
    assert registry.actions[0].multistate


def test_holder_on_and_transition() -> None:
    offices = _all_offices()
    offices[[o["state"] for o in offices].index("TX")] = _office(
        "TX",
        _holder(name="Outgoing", start="2015-01-05"),
        _holder(name="Incoming", party="D", status="successor", start="2027-01-01"),
    )
    registry = StateAgRegistry.model_validate(_registry(offices=offices))
    texas = registry.office("TX")

    assert texas.holder_on(date(2026, 11, 5)).name == "Outgoing"
    assert texas.holder_on(date(2027, 1, 1)).name == "Incoming"
    transition = texas.transition()
    assert transition is not None and transition.name == "Incoming"
    assert registry.office("WY").transition() is None


def test_uncalled_race_names_no_winner() -> None:
    offices = _all_offices()
    offices[0] = _office(
        offices[0]["state"],
        _holder(),
        _holder(name=None, party=None, status="uncalled", start="2027-01-01"),
    )

    office = StateAgRegistry.model_validate(_registry(offices=offices)).offices[0]
    pending = office.transition()
    assert pending is not None and pending.name is None


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (_registry(_action(category="antitrust")), "is not one of"),
        (_registry(_action(states=["TX", "ZZ"])), "unknown states"),
        (_registry(_action(states=["TX", "TX"])), "listed twice"),
        (_registry(_action(lead="CA")), "is not among the states"),
        (_registry(_action(docket_number=None)), "come together"),
        (_registry(_action(added="2026-01-01")), "added before"),
        (_registry(_action(id="Bad Id")), "kebab-case"),
        (_registry(_action(), _action()), "used twice"),
        (_registry(_action(sources=[])), "at least 1"),
        (_registry(offices=[_office("TX")]), "covers every state and DC"),
        (_registry(offices=[*_all_offices(), _office("TX")]), "listed twice"),
        (
            _registry(
                offices=[
                    _office(
                        "TX",
                        _holder(start="2027-01-01"),
                        _holder(start="2015-01-01"),
                    )
                ]
            ),
            "in order",
        ),
        (
            _registry(offices=[_office("TX", _holder(status="successor"))]),
            "first holder",
        ),
        (
            _registry(
                offices=[
                    _office(
                        "TX",
                        _holder(),
                        _holder(status="successor", start="2027-01-01"),
                        _holder(start="2028-01-01"),
                    )
                ]
            ),
            "only last",
        ),
        (
            _registry(
                offices=[_office("TX", _holder(), _holder(status="uncalled", start="2027-01-01"))]
            ),
            "no winner",
        ),
        (_registry(offices=[_office("TX", _holder(name=None))]), "needs a name"),
    ],
)
def test_bad_rows_are_refused(data: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        StateAgRegistry.model_validate(data)


def test_repeated_key_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "state-ags.yaml"
    path.write_text("categories: {a: b}\ncategories: {c: d}\n")

    with pytest.raises(ValueError, match="duplicate key"):
        load_state_ags(path)
