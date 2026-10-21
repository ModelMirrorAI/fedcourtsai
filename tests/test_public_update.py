"""The weekly public update: which committed forecasts and outcomes it shows, and how."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, tzinfo
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, public_update, set_aside
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.public_update import (
    archive_path,
    archive_public_updates,
    build_public_update,
    last_complete_week,
    render_public_update,
    week_bounds,
    weeks_through,
)
from fedcourtsai.schemas import (
    Disposition,
    EventKind,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
    SetAsideEvent,
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
    mootness: bool = False,
) -> None:
    write_json(
        CasePaths(data_root, "scotus", docket).event(event_id).outcome,
        Outcome(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            resolved_at=on,
            actual_disposition=disposition,
            actual_granted=int(disposition is Disposition.granted),
            disposition_basis="mootness" if mootness else "standard",
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

    update = build_public_update(data, week)
    assert [item.case_id for item in update.new] == ["scotus/201"]
    assert update.new[0].outcome is None

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


def test_footer_links_the_results_page(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 811, "Tau v. Upsilon")
    _forecast(data, 811, at=base, probability=0.3)
    text = render_public_update(build_public_update(data, _week_of(base.date())))
    assert "[Results page](https://fedcourts.ai/results/)" in text


def test_a_predictor_that_re_ran_in_its_window_shows_once_with_its_latest_cell(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 901, "Rho v. Sigma")
    _forecast(data, 901, at=base, probability=0.4)
    _forecast(data, 901, at=base + timedelta(minutes=30), probability=0.55)

    (item,) = build_public_update(data, _week_of(base.date())).new
    assert [(f.predictor_id, f.probability) for f in item.forecasts] == [("claude-baseline", 0.55)]


def test_a_mootness_outcome_is_not_shown_as_forecast_in_advance(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    resolved_on = (base + timedelta(days=3)).date()
    _event(data, 1001, "Tau v. Upsilon")
    _forecast(data, 1001, at=base, probability=0.3)
    _outcome(data, 1001, on=resolved_on, disposition=Disposition.gvr, mootness=True)
    assert build_public_update(data, _week_of(resolved_on)).resolved == ()


def test_a_merits_outcome_without_a_judgment_reads_neutrally(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    resolved_on = (base + timedelta(days=3)).date()
    event_id = "evt-brief-judgment"
    _event(data, 1101, "Phi v. Chi", event_id, kind=EventKind.brief, stage=Stage.merits)
    _forecast(data, 1101, at=base, probability=0.6, event_id=event_id)
    _outcome(data, 1101, on=resolved_on, disposition=Disposition.other, event_id=event_id)

    (item,) = build_public_update(data, _week_of(resolved_on)).resolved
    assert item.outcome == "Decided"
    assert item.usual


def test_a_corrupt_ledger_file_is_not_reported_as_a_bad_week(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 1201, "Psi v. Omega")
    _forecast(data, 1201, at=base, probability=0.5)
    CasePaths(data, "scotus", 1201).event(PETITION).event_file.write_text("kind: [unclosed\n")
    result = runner.invoke(
        app,
        ["public-update", "--week", _week_of(base.date())],
        env={"FEDCOURTS_DATA_ROOT": str(data)},
    )
    assert result.exit_code not in (0, 2, 3)


def _listed(case_id: str) -> dict[tuple[str, str], SetAsideEvent]:
    return {
        (case_id, PETITION): SetAsideEvent(
            case_id=case_id,
            event_id=PETITION,
            reason="post-conference-first-forecast",
            conference=date(2026, 9, 28),
            first_forward_run_id="20261004T201824Z",
            declared=date(2026, 10, 16),
        )
    }


def test_a_set_aside_event_is_never_shown_as_forecast_in_advance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A listed set-aside event leaves both sections; an unlisted one beside it stays."""
    data = tmp_path / "data"
    base = _base()
    resolved_on = (base + timedelta(days=3)).date()
    for docket, title in ((401, "Iota v. Kappa"), (402, "Lambda v. Mu")):
        _event(data, docket, title)
        _forecast(data, docket, at=base, probability=0.6)
        _outcome(data, docket, on=resolved_on, disposition=Disposition.granted)
    _event(data, 403, "Nu v. Xi")
    _forecast(data, 403, at=base, probability=0.2)
    monkeypatch.setattr(
        set_aside, "SET_ASIDE_EVENTS", {**_listed("scotus/401"), **_listed("scotus/403")}
    )

    resolved = build_public_update(data, _week_of(resolved_on))
    assert [item.case_id for item in resolved.resolved] == ["scotus/402"]

    new = build_public_update(data, _week_of(base.date()))
    assert [item.case_id for item in new.new] == ["scotus/402"]


def test_weeks_through_crosses_a_year_and_is_empty_when_reversed() -> None:
    # 2026 is a 53-week ISO year.
    assert weeks_through("2026-W52", "2027-W01") == ["2026-W52", "2026-W53", "2027-W01"]
    assert weeks_through("2026-W42", "2026-W42") == ["2026-W42"]
    assert weeks_through("2026-W43", "2026-W42") == []


def test_the_history_is_write_once_and_skips_an_empty_week(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, metrics = tmp_path / "data", tmp_path / "metrics"
    base = _base()
    first = _week_of(base.date())
    monkeypatch.setattr(public_update, "ARCHIVE_FIRST_WEEK", first)
    _event(data, 601, "Lambda v. Mu")
    _forecast(data, 601, at=base, probability=0.7)
    following = _week_of(base.date() + timedelta(days=7))

    result = archive_public_updates(data, metrics, following)
    assert result.written == (first,)
    assert result.empty == (following,)
    path = archive_path(metrics, first)
    assert path == metrics / "updates" / f"{first}.md"
    # The file is the email's render, with its title.
    assert path.read_text() == render_public_update(build_public_update(data, first))

    # A later change to the ledger inside that week does not rewrite the page.
    _event(data, 602, "Nu v. Xi")
    _forecast(data, 602, at=base + timedelta(minutes=5), probability=0.4)
    again = archive_public_updates(data, metrics, following)
    assert again.written == ()
    assert again.present == (first,)
    assert "Nu v. Xi" not in path.read_text()


def test_the_history_starts_at_the_first_week_the_list_was_sent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, metrics = tmp_path / "data", tmp_path / "metrics"
    base = _base()
    _event(data, 611, "Omicron v. Pi")
    _forecast(data, 611, at=base, probability=0.6)
    later = _week_of(base.date() + timedelta(days=14))
    monkeypatch.setattr(public_update, "ARCHIVE_FIRST_WEEK", later)
    result = archive_public_updates(data, metrics, later)
    assert result.written == ()
    assert not (metrics / "updates").exists()


def test_archive_cli_reports_what_it_wrote(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data, metrics = tmp_path / "data", tmp_path / "metrics"
    env = {"FEDCOURTS_DATA_ROOT": str(data), "FEDCOURTS_METRICS_ROOT": str(metrics)}
    base = _base()
    week = _week_of(base.date())
    monkeypatch.setattr(public_update, "ARCHIVE_FIRST_WEEK", week)

    class _WeekLater(datetime):
        """The CLI's clock, a week past ``base``, so ``base``'s week is complete."""

        @classmethod
        def now(cls, tz: tzinfo | None = None) -> _WeekLater:
            return cls.fromtimestamp((base + timedelta(days=7)).timestamp(), tz)

    monkeypatch.setattr(cli, "datetime", _WeekLater)
    _event(data, 621, "Rho v. Sigma")
    _forecast(data, 621, at=base, probability=0.6)

    bad = runner.invoke(app, ["archive-public-updates", "--through", "2026-42"], env=env)
    assert bad.exit_code == 2

    result = runner.invoke(app, ["archive-public-updates", "--through", week], env=env)
    assert result.exit_code == 0, result.output
    assert f"wrote {week}" in result.output
    assert "Rho v. Sigma" in archive_path(metrics, week).read_text()

    rerun = runner.invoke(app, ["archive-public-updates", "--through", week], env=env)
    assert rerun.exit_code == 0, rerun.output
    assert "0 written, 1 already archived" in rerun.output


def test_a_missed_run_catches_up_every_non_empty_week(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, metrics = tmp_path / "data", tmp_path / "metrics"
    base = _base()
    first = _week_of(base.date())
    monkeypatch.setattr(public_update, "ARCHIVE_FIRST_WEEK", first)
    _event(data, 631, "Tau v. Upsilon")
    _forecast(data, 631, at=base, probability=0.6)
    _event(data, 632, "Phi v. Chi")
    _forecast(data, 632, at=base + timedelta(days=14), probability=0.3)
    third = _week_of(base.date() + timedelta(days=14))
    result = archive_public_updates(data, metrics, third)
    assert result.written == (first, third)
    assert len(result.empty) == 1


def test_a_caption_line_break_cannot_open_a_block(tmp_path: Path) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 641, "Psi\n# v. Omega\n---")
    _forecast(data, 641, at=base, probability=0.6)
    text = render_public_update(build_public_update(data, _week_of(base.date())))
    assert "\n# v. Omega" not in text
    assert "\n---\n\n_" not in text.split("## New forecasts this week", 1)[1].split("---")[0]


def test_archive_cli_refuses_a_week_still_in_progress(tmp_path: Path) -> None:
    env = {"FEDCOURTS_DATA_ROOT": str(tmp_path / "data"), "FEDCOURTS_METRICS_ROOT": str(tmp_path)}
    year, week, _ = datetime.now(UTC).date().isocalendar()
    current = f"{year}-W{week:02d}"
    result = runner.invoke(app, ["archive-public-updates", "--through", current], env=env)
    assert result.exit_code == 2
    assert "not complete yet" in result.output
