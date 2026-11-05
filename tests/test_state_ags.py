"""The state-AGs registry: the committed file loads, its checks refuse bad rows, and tiers rank."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.metrics_refresh import _headline
from fedcourtsai.schemas import StateAgsBoard
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.state_ags import (
    AMBITION_METHOD,
    JURISDICTIONS,
    Kind,
    Rung,
    StateAgRegistry,
    Track,
    build_board,
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


@pytest.mark.parametrize(("days_before", "expected"), [(729, Rung.sues), (730, Rung.none)])
def test_window_opens_after_day_730(days_before: int, expected: Rung) -> None:
    on = date(2026, 11, 5)
    announced = date.fromordinal(on.toordinal() - days_before)
    registry = StateAgRegistry.model_validate(_registry(_action(announced=announced.isoformat())))

    assert registry.tier("TX", on) is expected


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
        (_registry(_action(court=None, docket_number=None)), "names its court"),
        (_registry(_action(states=["TX", "UT"])), "names its lead"),
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


def _board_registry() -> StateAgRegistry:
    offices = _all_offices()
    states = [o["state"] for o in offices]
    offices[states.index("TX")] = _office(
        "TX",
        _holder(name="Outgoing", start="2015-01-05"),
        _holder(name="Incoming", party="D", status="successor", start="2027-01-01"),
    )
    offices[states.index("KS")] = _office(
        "KS",
        _holder(name="Sitting", start="2023-01-09"),
        _holder(name=None, party=None, status="uncalled", start="2026-11-01"),
    )
    return StateAgRegistry.model_validate(
        _registry(
            _action(),
            _action(
                id="letter-one",
                kind="letter",
                states=["TX", "CA", "NY"],
                lead="CA",
                court=None,
                docket_number=None,
                announced="2026-04-01",
            ),
            _action(
                id="letter-two",
                kind="letter",
                states=["CA", "NY"],
                lead="NY",
                court=None,
                docket_number=None,
                announced="2026-05-01",
            ),
            _action(
                id="defense-one",
                kind="defense",
                states=["CA"],
                announced="2026-06-01",
                watchlist_case="Doe v. Model Co.",
            ),
            offices=offices,
        )
    )


def test_board_rows_tiers_counts_and_transitions() -> None:
    board = build_board(_board_registry(), date(2026, 11, 5), frozenset({"Doe v. Model Co."}))
    rows = {row.state: row for row in board.offices}

    assert len(rows) == 51
    assert rows["TX"].tier == 4 and rows["TX"].tier_label == "Sues"
    assert rows["TX"].holder.name == "Outgoing"
    assert rows["TX"].transition is not None and rows["TX"].transition.name == "Incoming"
    assert not rows["TX"].transition_overdue
    # An uncalled race whose start day has passed is flagged, and names nobody.
    assert rows["KS"].transition_overdue and rows["KS"].holder.name is None
    # A defense never raises the tier; CA stays at the letters' rung.
    assert rows["CA"].tier == 1
    assert rows["CA"].window_counts["defense"] == 1
    assert rows["CA"].action_ids == ["defense-one", "letter-two", "letter-one"]
    assert board.defense_and_context == 1
    assert board.actions[0].id == "defense-one"
    letter = next(a for a in board.actions if a.id == "letter-one")
    assert letter.holders["TX"] == "Outgoing"
    assert letter.rungs == {"TX": 1, "CA": 1, "NY": 1}


def test_board_coalition_figures() -> None:
    coalition = build_board(
        _board_registry(), date(2026, 11, 5), frozenset({"Doe v. Model Co."})
    ).coalition

    assert coalition.multistate_actions == 2
    assert coalition.participation["CA"] == 1.0
    assert coalition.participation["TX"] == 0.5
    assert coalition.participation["WY"] == 0.0
    pairs = {(p.a, p.b): p for p in coalition.pairs}
    assert pairs[("CA", "NY")].affinity == 1.0
    assert pairs[("CA", "TX")].joint == 1 and pairs[("CA", "TX")].either == 2
    assert coalition.pairs[0].affinity == 1.0
    ranking = [(j.state, j.score) for j in coalition.join_rankings["CA"]]
    assert ranking == [("NY", 1.0), ("TX", 0.25)]
    assert "WY" not in coalition.join_rankings


def test_board_refuses_an_unknown_watchlist_case() -> None:
    with pytest.raises(ValueError, match="is not on the watchlist"):
        build_board(_board_registry(), date(2026, 11, 5), frozenset())


def test_empty_registry_board_validates_and_headlines(tmp_path: Path) -> None:
    board = build_board(load_state_ags(_COMMITTED), date(2026, 11, 5), frozenset())
    path = tmp_path / "state-ags.json"
    write_json(path, board)

    assert read_model(path, StateAgsBoard).coalition.multistate_actions == 0
    assert _headline(path, "metrics/state-ags.json").startswith("0 office(s) as of 2026-11-05")


def test_headline_counts_tiers_and_overdue(tmp_path: Path) -> None:
    path = tmp_path / "state-ags.json"
    write_json(
        path, build_board(_board_registry(), date(2026, 11, 5), frozenset({"Doe v. Model Co."}))
    )

    line = _headline(path, "metrics/state-ags.json")
    assert "51 office(s)" in line and "Sues 1" in line and "Signals 2" in line
    assert "4 action(s), 2 multistate; 1 transition(s) overdue" in line


def test_cli_writes_the_board(tmp_path: Path) -> None:
    out = tmp_path / "state-ags.json"
    result = CliRunner().invoke(app, ["state-ags", "--out", str(out), "--as-of", "2026-11-05"])

    assert result.exit_code == 0, result.output
    assert read_model(out, StateAgsBoard).as_of == date(2026, 11, 5)
