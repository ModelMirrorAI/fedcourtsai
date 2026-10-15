"""The weekly public update: which committed forecasts and outcomes it shows, and how."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import public_update
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.public_update import (
    build_public_update,
    last_complete_week,
    render_public_update,
    week_bounds,
)
from fedcourtsai.schemas import (
    Disposition,
    EventKind,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
    Stage,
)
from fedcourtsai.serialize import write_json, write_yaml

from .conftest import frozen_stamp

runner = CliRunner()

PETITION = "evt-petition-disposition"


def _stamp_at(when: datetime) -> ProcessVersion:
    """The frozen stamp, moved to ``when`` — which must stay inside its window."""
    return frozen_stamp().model_copy(update={"stamped_at": when})


def _base() -> datetime:
    """An instant inside the frozen window, so every seeded cell counts."""
    stamped = frozen_stamp().stamped_at
    assert stamped is not None
    return stamped + timedelta(hours=1)


def _week_of(day: date) -> str:
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def _event(
    data_root: Path,
    docket: int,
    title: str,
    event_id: str = PETITION,
    *,
    kind: EventKind = EventKind.petition,
    stage: Stage | None = None,
) -> None:
    write_yaml(
        CasePaths(data_root, "scotus", docket).event(event_id).event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=f"scotus/{docket}",
            kind=kind,
            stage=stage,
            title=title,
            decision_target="disposition",
            resolved=False,
        ),
    )


def _forecast(
    data_root: Path,
    docket: int,
    *,
    at: datetime,
    probability: float,
    predictor_id: str = "claude-baseline",
    mode: str = "forward",
    stamped: bool = True,
    event_id: str = PETITION,
) -> None:
    run_id = at.strftime("%Y%m%dT%H%M%SZ")
    write_json(
        CasePaths(data_root, "scotus", docket).event(event_id).prediction(predictor_id, run_id),
        Prediction(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            predictor_id=predictor_id,
            engine="claude-code",
            model="claude-fable-5",
            run_id=run_id,
            created_at=at,
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=int(probability >= 0.5),
            probability=probability,
            predicted_disposition=Disposition.granted if probability >= 0.5 else Disposition.denied,
            process_version=_stamp_at(at) if stamped else None,
            context=PredictionContext(mode=mode, snapshot_date=at.date(), signals_observable=False),
        ),
    )


def _outcome(
    data_root: Path,
    docket: int,
    *,
    on: date,
    disposition: Disposition,
    event_id: str = PETITION,
) -> None:
    write_json(
        CasePaths(data_root, "scotus", docket).event(event_id).outcome,
        Outcome(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            resolved_at=on,
            actual_disposition=disposition,
            actual_granted=int(disposition is Disposition.granted),
        ),
    )


def test_week_bounds_and_last_complete_week() -> None:
    assert week_bounds("2026-W42") == (date(2026, 10, 12), date(2026, 10, 18))
    assert last_complete_week(datetime(2026, 10, 15, 9, tzinfo=UTC)) == "2026-W41"
    assert last_complete_week(datetime(2026, 1, 2, tzinfo=UTC)) == "2025-W52"
    for bad in ("2026-42", "2026-W00", "2026-W54", "W42"):
        with pytest.raises(ValueError, match="week"):
            week_bounds(bad)


def test_a_resolution_shows_only_the_counted_forward_forecasts_made_before_it(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    base = _base()
    resolved_on = (base + timedelta(days=3)).date()
    _event(data, 101, "Alpha v. Beta")
    _forecast(data, 101, at=base, probability=0.7, predictor_id="claude-baseline")
    _forecast(data, 101, at=base, probability=0.4, predictor_id="codex-baseline")
    # A shakedown cell and a replay cell never appear, counted or not.
    _forecast(data, 101, at=base, probability=0.9, predictor_id="gemini-baseline", stamped=False)
    _forecast(data, 101, at=base, probability=0.9, predictor_id="other-baseline", mode="replay")
    _outcome(data, 101, on=resolved_on, disposition=Disposition.granted)
    # A forecast committed on the day of its outcome is retrospective, not forward.
    _event(data, 102, "Gamma v. Delta")
    _forecast(data, 102, at=datetime.combine(resolved_on, base.timetz()), probability=0.1)
    _outcome(data, 102, on=resolved_on, disposition=Disposition.denied)

    update = build_public_update(data, _week_of(resolved_on))

    assert [item.case_id for item in update.resolved] == ["scotus/101"]
    item = update.resolved[0]
    assert [(f.predictor_id, f.probability) for f in item.forecasts] == [
        ("claude-baseline", 0.7),
        ("codex-baseline", 0.4),
    ]
    assert item.outcome is not None
    assert item.outcome.startswith("Granted")
    assert not item.usual
    assert item.event_path == f"data/cases/scotus/101/events/{PETITION}"


def test_new_forecasts_are_the_counted_forward_cells_whose_clock_is_in_the_week(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 201, "Epsilon v. Zeta")
    _forecast(data, 201, at=base, probability=0.2)
    week = _week_of(base.date())
    start, end = week_bounds(week)

    update = build_public_update(data, week)
    assert [item.case_id for item in update.new] == ["scotus/201"]
    assert update.new[0].outcome is None
    assert start <= base.date() <= end

    later = build_public_update(data, _week_of(base.date() + timedelta(days=7)))
    assert later.empty


def test_a_voided_event_never_appears(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 301, "Eta v. Theta")
    _forecast(data, 301, at=base, probability=0.3)
    monkeypatch.setattr(
        public_update, "is_voided", lambda case_id, _event_id: case_id == "scotus/301"
    )
    assert build_public_update(data, _week_of(base.date())).empty


def test_render_puts_the_unusual_outcome_first_and_escapes_captions(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    resolved_on = (base + timedelta(days=2)).date()
    for docket, title, disposition in (
        (401, "Aardvark v. United States", Disposition.denied),
        (402, "Zebra *Corp* v. [Smith]", Disposition.granted),
    ):
        _event(data, docket, title)
        _forecast(data, docket, at=base, probability=0.25)
        _outcome(data, docket, on=resolved_on, disposition=disposition)

    update = build_public_update(data, _week_of(resolved_on))
    text = render_public_update(update)

    resolved = text.split("## Resolved this week")[1].split("## New forecasts")[0]
    assert resolved.index("Zebra") < resolved.index("Aardvark")
    assert r"Zebra \*Corp\* v. \[Smith\]" in text
    assert "claude-baseline 25%" in text
    assert "2 resolved: 1 not denied, 1 denied." in text
    assert "(GVR) counts as a grant" in text
    assert "Each percentage is a model's committed chance of a grant." in text
    assert "not an accuracy claim" in text
    assert render_public_update(build_public_update(data, _week_of(resolved_on))) == text


def test_cli_exits_3_on_an_empty_week_and_writes_the_update_otherwise(tmp_path: Path) -> None:
    data = tmp_path / "data"
    env = {"FEDCOURTS_DATA_ROOT": str(data)}
    out = tmp_path / "update.md"

    empty = runner.invoke(app, ["public-update", "--week", "2026-W42", "--out", str(out)], env=env)
    assert empty.exit_code == 3
    assert not out.exists()

    bad = runner.invoke(app, ["public-update", "--week", "2026-42"], env=env)
    assert bad.exit_code == 2

    base = _base()
    _event(data, 501, "Iota v. Kappa")
    _forecast(data, 501, at=base, probability=0.6)
    week = _week_of(base.date())
    result = runner.invoke(app, ["public-update", "--week", week, "--out", str(out)], env=env)
    assert result.exit_code == 0, result.output
    assert "Iota v. Kappa" in out.read_text()


def test_an_application_reads_in_its_own_words_after_a_round_trip_through_disk(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    base = _base()
    resolved_on = (base + timedelta(days=1)).date()
    event_id = "evt-motion-application"
    _event(data, 601, "Lambda v. Mu", event_id, kind=EventKind.motion, stage=Stage.interim)
    _forecast(data, 601, at=base, probability=0.8, event_id=event_id)
    _outcome(data, 601, on=resolved_on, disposition=Disposition.denied, event_id=event_id)

    (item,) = build_public_update(data, _week_of(resolved_on)).resolved
    assert item.outcome == "Application denied"
    assert item.usual
    assert "Will the Court grant the application?" in render_public_update(
        build_public_update(data, _week_of(resolved_on))
    )


def test_a_cell_stamped_on_its_outcome_day_is_not_a_new_forecast(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 701, "Nu v. Xi")
    _forecast(data, 701, at=base, probability=0.4)
    _outcome(data, 701, on=base.date(), disposition=Disposition.denied)
    assert build_public_update(data, _week_of(base.date())).empty


def test_percentages_never_round_to_certainty(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 801, "Omicron v. Pi")
    _forecast(data, 801, at=base, probability=0.001, predictor_id="claude-baseline")
    _forecast(data, 801, at=base, probability=0.999, predictor_id="codex-baseline")
    text = render_public_update(build_public_update(data, _week_of(base.date())))
    assert "claude-baseline <1%" in text
    assert "codex-baseline >99%" in text
    assert " 0%" not in text
    assert "100%" not in text
