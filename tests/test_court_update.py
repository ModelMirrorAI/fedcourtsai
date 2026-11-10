"""The weekly Court update: which committed Court actions it shows, and how."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import court_update, voids
from fedcourtsai.buttondown import API_KEY_ENV
from fedcourtsai.cli import app
from fedcourtsai.court_update import (
    LISTED_TOP,
    build_court_update,
    court_update_subject,
    render_court_update,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    CaseSummaryFrontMatter,
    Disposition,
    EventKind,
    Judgment,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    Stage,
    TermCalendar,
    TermCalendarSession,
    TermCalendarSource,
)
from fedcourtsai.serialize import write_json, write_text, write_yaml
from fedcourtsai.summaries import render_summary
from fedcourtsai.supremecourt import live_application_id, live_docket_id
from fedcourtsai.term_calendar import term_calendar_path

from .conftest import frozen_stamp

runner = CliRunner()

WEEK = "2026-W45"
MONDAY = date(2026, 11, 2)
PETITION = "evt-petition-disposition"


def _event(
    data_root: Path,
    docket: int,
    title: str,
    event_id: str = PETITION,
    *,
    kind: EventKind = EventKind.petition,
    stage: Stage | None = Stage.cert,
    moment: Moment | None = Moment.distribution,
    opened_at: date | None = None,
) -> None:
    write_yaml(
        CasePaths(data_root, "scotus", docket).event(event_id).event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=f"scotus/{docket}",
            kind=kind,
            stage=stage,
            moment=moment,
            title=title,
            opened_at=opened_at,
            decision_target="disposition",
            resolved=False,
        ),
    )


def _outcome(
    data_root: Path,
    docket: int,
    *,
    on: date,
    disposition: Disposition = Disposition.denied,
    judgment: Judgment | None = None,
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
            judgment=judgment,
        ),
    )


def _stakes(data_root: Path, docket: int, score: float, event_id: str = PETITION) -> None:
    """One counted forward forecast on the case, carrying a stakes read."""
    stamped = frozen_stamp().stamped_at
    assert stamped is not None
    at = stamped + timedelta(hours=1)
    run_id = at.strftime("%Y%m%dT%H%M%SZ")
    write_json(
        CasePaths(data_root, "scotus", docket)
        .event(event_id)
        .prediction("claude-baseline", run_id),
        Prediction(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id=run_id,
            created_at=at,
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.07,
            big_case_score=score,
            predicted_disposition=Disposition.denied,
            process_version=frozen_stamp().model_copy(update={"stamped_at": at}),
            context=PredictionContext(
                mode="forward", snapshot_date=at.date(), signals_observable=False
            ),
        ),
    )


def _summary(data_root: Path, docket: int, brief: str, day: str = "2026-10-30") -> None:
    front = CaseSummaryFrontMatter(
        case_id=f"scotus/{docket}",
        snapshot=date.fromisoformat(day),
        record_digest="sha256:" + "1" * 64,
        model="claude-sonnet-5",
        prompt_digest="sha256:" + "0" * 64,
        body_version=2,
        generated_at=datetime(2026, 10, 31, 4, 0, tzinfo=UTC),
    )
    body = (
        f"## In brief\n\n{brief}\n\n## What happened\n\nA dispute.\n\n"
        "## What the Court is being asked\n\nA question.\n\n## Where it stands\n\nPending.\n\n"
        "## What each outcome would mean\n\nOne thing or another.\n"
    )
    write_text(CasePaths(data_root, "scotus", docket).summary(day), render_summary(front, body))


def test_a_decision_is_listed_once_per_stage_with_no_forecast_in_it(tmp_path: Path) -> None:
    data = tmp_path / "data"
    application = live_application_id(26, 623)
    # One application decided, with the question opened at two forecast moments.
    _event(
        data,
        application,
        "Guardado v. Florida",
        "evt-motion-disposition",
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
    )
    _event(
        data,
        application,
        "Guardado v. Florida",
        "evt-brief-response-disposition",
        kind=EventKind.brief,
        stage=Stage.interim,
        moment=Moment.response_filed,
    )
    for event_id in ("evt-motion-disposition", "evt-brief-response-disposition"):
        _outcome(data, application, on=MONDAY + timedelta(days=3), event_id=event_id)
    _stakes(data, application, 0.4, "evt-motion-disposition")
    _summary(data, application, "A prisoner asks the Court to stay his execution.")
    # A grant on a CourtListener-id case, which carries no docket number.
    _event(data, 73520108, "Goldman Sachs Bank USA v. Rhea Ann Brown, et al.")
    _outcome(data, 73520108, on=MONDAY + timedelta(days=4), disposition=Disposition.granted)
    # Decided the week before: not this week's news.
    _event(data, 501, "Old v. News")
    _outcome(data, 501, on=MONDAY - timedelta(days=1))

    update = build_court_update(data, WEEK)

    assert [(d.case.case_id, d.stage) for d in update.decisions] == [
        ("scotus/73520108", Stage.cert),
        (f"scotus/{application}", Stage.interim),
    ]
    text = render_court_update(update)
    assert text.startswith(
        "# FedCourtsAI Supreme Court update: November 2 \N{EN DASH} November 8, 2026\n"
    )
    assert text.index("### Emergency applications") < text.index("### Petitions for review")
    assert (
        "- **Guardado v. Florida** (No. 26A623) — Application denied. A prisoner asks the "
        "Court to stay his execution. "
        "([docket](https://www.supremecourt.gov/docket/docketfiles/html/public/26a623.html))"
    ) in text
    assert (
        "- **Goldman Sachs Bank USA v. Rhea Ann Brown** — Granted: the Court will hear the case."
        in text
    )
    assert text.count("Guardado v. Florida") == 1
    assert "Old v. News" not in text
    # No forecast, no stakes read, no percentage.
    assert "%" not in text
    assert "0.4" not in text
    assert "Forecasts:" not in text


def test_denials_are_counted_whole_and_cut_to_the_biggest_while_grants_all_show(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    day = MONDAY + timedelta(days=4)
    denied = LISTED_TOP + 3
    for n in range(denied):
        docket = live_docket_id(26, 100 + n)
        _event(data, docket, f"Denied{n:02d} v. State")
        _outcome(data, docket, on=day)
        # The last ones filed carry the highest stakes reads; one has none.
        if n:
            _stakes(data, docket, 0.01 * n)
    for n in range(2):
        docket = live_docket_id(26, 300 + n)
        _event(data, docket, f"Granted{n} v. State")
        _outcome(data, docket, on=day, disposition=Disposition.granted)

    update = build_court_update(data, WEEK)
    text = render_court_update(update)

    assert f"{denied + 2} decided: {denied} denied, 2 another outcome." in text
    assert f"Showing {LISTED_TOP} of the {denied} cases denied" in text
    assert "Granted0 v. State" in text
    assert "Granted1 v. State" in text
    shown = [n for n in range(denied) if f"Denied{n:02d} v. State" in text]
    assert shown == list(range(denied - LISTED_TOP, denied))
    # Grants come first.
    assert text.index("Granted1 v. State") < text.index("Denied12 v. State")
    # Uncut, every case is listed and the note goes.
    whole = render_court_update(update, top=None)
    assert "Showing" not in whole
    assert all(f"Denied{n:02d} v. State" in whole for n in range(denied))


def test_a_merits_decision_reads_as_a_judgment(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _event(
        data,
        901,
        "Alpha v. Beta",
        "evt-order-judgment",
        kind=EventKind.order,
        stage=Stage.merits,
        moment=Moment.argued,
    )
    _outcome(
        data,
        901,
        on=MONDAY,
        disposition=Disposition.other,
        judgment=Judgment.reversed,
        event_id="evt-order-judgment",
    )

    text = render_court_update(build_court_update(data, WEEK))

    assert "### Argued cases decided\n\n- **Alpha v. Beta** — Reversed." in text


def test_other_actions_and_new_filings_come_from_the_events_opened_in_the_week(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    inside = MONDAY + timedelta(days=2)
    _event(
        data,
        601,
        "Argued v. Case",
        "evt-argument-judgment",
        kind=EventKind.argument,
        stage=Stage.merits,
        moment=Moment.argued,
        opened_at=inside,
    )
    _event(
        data,
        602,
        "Views v. Invited",
        "evt-order-cvsg-disposition",
        kind=EventKind.order,
        moment=Moment.cvsg,
        opened_at=inside,
    )
    _event(
        data,
        603,
        "Relisted v. Once",
        "evt-order-relist-disposition",
        kind=EventKind.order,
        moment=Moment.relist,
        opened_at=inside,
    )
    _event(
        data,
        604,
        "Response v. Asked",
        "evt-order-response-disposition",
        kind=EventKind.order,
        moment=Moment.response_requested,
        opened_at=inside,
    )
    # Not the Court's act, so not an action: the Solicitor General's brief, a grant's opening.
    _event(
        data,
        605,
        "Brief v. Filed",
        "evt-brief-sg-disposition",
        kind=EventKind.brief,
        moment=Moment.sg_brief,
        opened_at=inside,
    )
    # Opened outside the week.
    _event(
        data,
        606,
        "Earlier v. Relist",
        "evt-order-relist-disposition",
        kind=EventKind.order,
        moment=Moment.relist,
        opened_at=MONDAY - timedelta(days=3),
    )
    filed = live_application_id(26, 700)
    _event(
        data,
        filed,
        "Fresh v. Application",
        "evt-motion-disposition",
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        opened_at=inside,
    )
    petition = live_docket_id(26, 584)
    _event(
        data,
        petition,
        "Jack v. Whateley",
        "evt-petition-arrival-disposition",
        moment=Moment.arrival,
        opened_at=inside,
    )
    # Filed and decided inside the week: a decision, not also a new filing.
    quick = live_application_id(26, 701)
    _event(
        data,
        quick,
        "Quick v. Ruling",
        "evt-motion-disposition",
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        opened_at=MONDAY,
    )
    _outcome(data, quick, on=inside, event_id="evt-motion-disposition")

    update = build_court_update(data, WEEK)
    text = render_court_update(update)

    assert [(a.case.caption, a.moment) for a in update.actions] == [
        ("Argued v. Case", Moment.argued),
        ("Relisted v. Once", Moment.relist),
        ("Response v. Asked", Moment.response_requested),
        ("Views v. Invited", Moment.cvsg),
    ]
    order = [
        "## Decisions",
        "## Other actions by the Court",
        "### Argued\n\n- **Argued v. Case**.",
        "### Solicitor General's views invited\n\n- **Views v. Invited**.",
        "### Relisted for the first time\n\n- **Relisted v. Once**.",
        "### Response requested\n\n- **Response v. Asked**.",
        "## New filings",
        "### Emergency applications filed\n\n- **Fresh v. Application** (No. 26A700).",
        "### Newly filed petitions FedCourtsAI is following\n\n"
        + "- **Jack v. Whateley** (No. 26-584).",
    ]
    positions = [text.index(part) for part in order]
    assert positions == sorted(positions)
    assert "Brief v. Filed" not in text
    assert "Earlier v. Relist" not in text
    assert text.count("Quick v. Ruling") == 1


def test_a_voided_event_is_never_news(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = tmp_path / "data"
    _event(data, 801, "Wrong v. Petition")
    _outcome(data, 801, on=MONDAY, disposition=Disposition.granted)
    assert not build_court_update(data, WEEK).empty

    monkeypatch.setattr(voids, "VOIDED_EVENTS", {("scotus/801", PETITION): object()})

    assert build_court_update(data, WEEK).empty


def test_the_next_conference_is_the_calendars_first_after_the_week(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _event(data, 801, "Alpha v. Beta")
    _outcome(data, 801, on=MONDAY)
    assert "## Ahead" not in render_court_update(build_court_update(data, WEEK))

    write_json(
        term_calendar_path(data),
        TermCalendar(
            checked_on=date(2026, 11, 9),
            sources=[
                TermCalendarSource(
                    term=2026, url="https://www.supremecourt.gov/x.pdf", sha256="0" * 64
                )
            ],
            sessions=[
                TermCalendarSession(day=day, kind="conference", term=2026, long_conference=long)
                for day, long in (
                    (date(2026, 9, 29), True),
                    (date(2026, 11, 6), False),
                    (date(2026, 11, 13), False),
                    (date(2026, 11, 20), False),
                )
            ],
            distributions=[],
        ),
    )

    update = build_court_update(data, WEEK)

    assert update.next_conference == date(2026, 11, 13)
    assert (
        "## Ahead\n\nThe Court's next scheduled conference is Friday, November 13, 2026."
        in render_court_update(update)
    )


def test_a_summary_without_an_in_brief_line_or_that_does_not_read_adds_nothing(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    _event(data, 801, "Alpha v. Beta")
    _outcome(data, 801, on=MONDAY)
    write_text(CasePaths(data, "scotus", 801).summary("2026-10-30"), "not a summary file\n")

    text = render_court_update(build_court_update(data, WEEK))

    assert "- **Alpha v. Beta** — Denied: the Court will not hear the case.\n" in text


def test_a_brief_cannot_open_markdown_of_its_own(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _event(data, 801, "Alpha v. Beta")
    _outcome(data, 801, on=MONDAY)
    _summary(data, 801, "A [link](https://example.com) and *stars*.")

    text = render_court_update(build_court_update(data, WEEK))

    assert "[link](" not in text
    assert r"\[link\]" in text


def test_the_same_tree_renders_the_same_bytes_and_an_empty_week_says_so(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _event(data, 801, "Alpha v. Beta")
    _outcome(data, 801, on=MONDAY)

    assert render_court_update(build_court_update(data, WEEK)) == render_court_update(
        build_court_update(data, WEEK)
    )
    quiet = build_court_update(data, "2026-W46")
    assert quiet.empty
    assert "took no action this week" in render_court_update(quiet)
    assert court_update_subject(quiet) != court_update_subject(build_court_update(data, WEEK))


def test_the_subject_differs_from_the_forecasts_updates(tmp_path: Path) -> None:
    """Each draft is found by its subject, so the week's two must never collide."""
    from fedcourtsai.public_update import build_public_update, public_update_subject  # noqa: PLC0415

    data = tmp_path / "data"
    assert court_update_subject(build_court_update(data, WEEK)) != public_update_subject(
        build_public_update(data, WEEK)
    )


def test_the_cli_renders_dry_runs_and_skips_an_empty_week(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = tmp_path / "data"
    _event(data, 801, "Alpha v. Beta")
    _outcome(data, 801, on=MONDAY)
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    env = {"FEDCOURTS_DATA_ROOT": str(data)}

    rendered = runner.invoke(app, ["court-update", "--week", WEEK], env=env)
    assert rendered.exit_code == 0, rendered.output
    assert rendered.output.startswith("# FedCourtsAI Supreme Court update: ")

    dry = runner.invoke(
        app, ["post-court-update", "--tag", "weekly-scotus", "--week", WEEK, "--dry-run"], env=env
    )
    assert dry.exit_code == 0, dry.output
    assert dry.output.startswith("Subject: FedCourtsAI Supreme Court update: ")
    assert "Tag: weekly-scotus" in dry.output
    assert "\n# FedCourtsAI" not in dry.output

    for command in ("court-update", "post-court-update"):
        args = [command, "--week", "2026-W46"] + (
            ["--tag", "weekly-scotus", "--dry-run"] if command.startswith("post") else []
        )
        assert runner.invoke(app, args, env=env).exit_code == 3

    assert runner.invoke(app, ["post-court-update", "--week", WEEK], env=env).exit_code == 2
    assert runner.invoke(app, ["court-update", "--week", "2026-45"], env=env).exit_code == 2
    no_key = runner.invoke(app, ["post-court-update", "--tag-id", "t", "--week", WEEK], env=env)
    assert no_key.exit_code == 2
    assert API_KEY_ENV in no_key.output


def test_the_footer_says_what_the_update_covers_and_who_wrote_the_descriptions() -> None:
    assert "not every matter" in court_update._FOOTER
    assert "written by an AI model" in court_update._FOOTER
