"""The forecast-coverage verdict: the three coverage checks folded into one answer."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import alarm_issue, corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import coverage_verdict as cv
from fedcourtsai.pipeline.coverage_verdict import (
    CoverageVerdict,
    attempt_capped_cells,
    coverage_verdict,
    render_markdown,
)
from fedcourtsai.pipeline.federal_label import SG_LISTING_SUBJECT, SgPetitionListing
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import Disposition, EventKind, Stage
from tests.conftest import seed_prediction

TODAY = date(2026, 11, 11)
EVENT = "evt-petition-disposition"
PREDICTORS = Path(__file__).resolve().parents[1] / "config" / "predictors.yaml"


def _resolved(
    conn: sqlite3.Connection,
    docket: int,
    docket_number: str,
    *,
    disposition: Disposition = Disposition.denied,
    resolved: date = TODAY - timedelta(days=6),
    selected: bool = True,
    case_name: str = "Acme Corp. v. Roe",
) -> None:
    case_id = f"scotus/{docket}"
    granted = disposition == Disposition.granted
    corpus.upsert_rows(
        conn,
        [
            corpus.CorpusRow(
                case_id=case_id,
                court="scotus",
                docket_number=docket_number,
                case_name=case_name,
                disposition=disposition,
                date_filed=date(2026, 6, 1),
                date_cert_granted=resolved if granted else None,
                date_cert_denied=None if granted else resolved,
                distribution_count=1,
                salience_version="sal-v8",
                salience_score=0.3,
                salience_selected=selected,
            )
        ],
    )
    corpus.upsert_events(
        conn,
        [
            corpus.CorpusEvent(
                event_id=EVENT,
                case_id=case_id,
                court="scotus",
                kind=EventKind.petition,
                stage=Stage.cert,
                resolved=True,
                opened_at=date(2026, 6, 1),
            )
        ],
    )


def _verdict(db: Path, data: Path) -> CoverageVerdict:
    with corpus.connect_readonly(db) as conn:
        return coverage_verdict(conn, data, PREDICTORS, today=TODAY)


def test_a_clean_ledger_is_ok_and_its_counts_are_flat(tmp_path: Path) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        _resolved(conn, 1, "26-101", selected=False)  # declined, by design

    verdict = _verdict(db, data)

    assert verdict.ok
    assert verdict.alarms == []
    assert verdict.counts["missed_events"] == 0
    assert verdict.counts["declined_not_funded_events"] == 1
    assert all(not isinstance(v, (dict, list)) for v in verdict.counts.values())
    assert "no alarm." in render_markdown(verdict)


def test_a_missed_forecast_and_an_unforecast_federal_grant_each_alarm_once(tmp_path: Path) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        _resolved(conn, 1, "26-101")  # selected, owed, never forecast, no outcome record
        _resolved(
            conn,
            2,
            "26-102",
            disposition=Disposition.granted,
            selected=False,
            case_name="United States v. Roe",
        )
    # Every enabled predictor has produced a forecast somewhere, so each was owed.
    for predictor in enabled_predictors(PREDICTORS):
        seed_prediction(data, "scotus", 999_999, EVENT, predictor_id=predictor.id)

    verdict = _verdict(db, data)
    by_check = {a.check: a.subject for a in verdict.alarms}

    assert not verdict.ok
    assert by_check["missed_forecast"] == f"scotus/1 {EVENT}"
    assert "no_outcome_record" not in by_check  # one event, one alarm
    assert by_check["unforecast_outcomes"] == "26-102"
    body = render_markdown(verdict)
    assert "## Alarms" in body
    assert "| 26-102 | granted |" in body
    assert "United States" not in body  # identifiers only, never a caption


def test_a_fresh_gap_in_the_outcome_record_is_the_writers_lag(tmp_path: Path) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        _resolved(conn, 1, "26-101", resolved=TODAY - timedelta(days=1))

    verdict = _verdict(db, data)

    assert "no_outcome_record" not in {a.check for a in verdict.alarms}
    assert verdict.counts["no_outcome_record_on_selected_row_events"] == 1


def test_the_cli_writes_both_files_and_exits_3_on_an_alarm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "corpus"
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(PREDICTORS.parent))
    out, body = tmp_path / "verdict.json", tmp_path / "verdict.md"
    args = ["coverage-verdict", "--json-out", str(out), "--markdown-out", str(body)]

    assert CliRunner().invoke(app, args).exit_code == 1  # no corpus

    today = datetime.now(UTC).date()
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _resolved(conn, 1, "26-101", selected=False, resolved=today - timedelta(days=6))
    quiet = CliRunner().invoke(app, args)
    assert quiet.exit_code == 0, quiet.output
    assert json.loads(out.read_text())["ok"] is True
    assert body.read_text().startswith("Forecast coverage as of ")

    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        _resolved(
            conn,
            2,
            "26-102",
            disposition=Disposition.granted,
            selected=False,
            resolved=today - timedelta(days=6),
            case_name="United States v. Roe",
        )
    alarmed = CliRunner().invoke(app, args)
    assert alarmed.exit_code == 3, alarmed.output
    assert json.loads(out.read_text())["ok"] is False


def test_a_decided_selected_row_with_no_outcome_alarms_after_the_grace_period(
    tmp_path: Path,
) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        _resolved(conn, 1, "26-101", resolved=TODAY - timedelta(days=3))
        _resolved(conn, 2, "26-102", resolved=TODAY - timedelta(days=2))
    # Every enabled predictor forecast both, so neither is a missed forecast;
    # both are decided with no outcome record.
    for predictor in enabled_predictors(PREDICTORS):
        for docket in (1, 2):
            seed_prediction(
                data, "scotus", docket, EVENT, predictor_id=predictor.id, run_id="20261101T141200Z"
            )

    verdict = _verdict(db, data)
    unrecorded = [a.subject for a in verdict.alarms if a.check == "no_outcome_record"]

    assert unrecorded == [f"scotus/1 {EVENT}"]


def test_an_unselected_office_petition_raises_the_federal_label_alarm(tmp_path: Path) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="26-101",
                    case_name="Acme Warden v. Roe",
                    date_filed=date(2026, 9, 1),
                    counsel=[
                        corpus.CounselEntry(
                            party="Acme Warden",
                            attorney="D. John Sauer",
                            role=corpus.CounselRole.petitioner,
                        )
                    ],
                )
            ],
        )

    verdict = _verdict(db, data)

    assert [(a.check, a.subject) for a in verdict.alarms] == [("federal_label", "26-101")]
    assert "- 26-101: band " in render_markdown(verdict)


class _Gh:
    """A recorded `gh`: a canned issue listing and issue body, every call kept."""

    def __init__(self, issues: list[dict[str, object]], body: str = "") -> None:
        self.issues = issues
        self.body = body
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        if argv[:2] == ["gh", "api"]:
            return self.body if "--jq" in argv else json.dumps(self.issues)
        if argv[1:3] == ["issue", "create"]:
            return "https://github.com/o/r/issues/7\n"
        return ""

    def verbs(self) -> list[str]:
        return [" ".join(call[1:3]) for call in self.calls]


_ALARM = {"number": 7, "title": cv.ISSUE_TITLE, "user": {"login": alarm_issue.ALARM_AUTHOR}}


def _missed_and_clean(tmp_path: Path) -> tuple[CoverageVerdict, CoverageVerdict]:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        _resolved(conn, 1, "26-101", selected=False)
    clean = _verdict(db, data)
    with corpus.connect(db) as conn:
        _resolved(conn, 2, "26-102")
    return _verdict(db, data), clean


def test_the_latch_opens_refreshes_and_closes_one_issue(tmp_path: Path) -> None:
    failing, passing = _missed_and_clean(tmp_path)
    assert failing.alarms and passing.ok
    body = tmp_path / "v.md"
    body.write_text(render_markdown(failing), encoding="utf-8")

    gh = _Gh([])
    assert cv.latch("o/r", failing, body, runner=gh) == "opened https://github.com/o/r/issues/7"
    assert gh.calls[-1][-2:] == ["--body-file", str(body)]
    assert "forecast-coverage" in gh.calls[-1]

    # The open issue already names every alarm: a body rewrite and no comment.
    gh = _Gh([_ALARM], body=render_markdown(failing))
    assert cv.latch("o/r", failing, body, runner=gh) == "refreshed #7"
    assert "issue comment" not in gh.verbs()

    gh = _Gh([_ALARM, {**_ALARM, "number": 9}])
    assert cv.latch("o/r", passing, body, runner=gh) == "closed #7, #9"
    assert gh.verbs().count("issue close") == 2

    gh = _Gh([])
    assert cv.latch("o/r", passing, body, runner=gh) == "no alarm, and no open issue"
    assert "issue create" not in gh.verbs()


def test_a_refresh_comments_only_the_alarms_the_issue_did_not_name(tmp_path: Path) -> None:
    failing, _ = _missed_and_clean(tmp_path)
    body = tmp_path / "v.md"
    body.write_text(render_markdown(failing), encoding="utf-8")

    gh = _Gh([_ALARM], body="Forecast coverage as of 2026-11-01: 1 alarm(s).\n\n- `scotus/9 x`")
    done = cv.latch("o/r", failing, body, runner=gh)

    assert done == f"refreshed #7, {len(failing.alarms)} new alarm(s) commented"
    # The comment lands before the rewrite, so a failed rewrite is re-noticed.
    verbs = gh.verbs()
    assert verbs.index("issue comment") < verbs.index("issue edit")
    comment = next(c for c in gh.calls if c[1:3] == ["issue", "comment"])[-1]
    assert all(f"`{a.subject}`" in comment for a in failing.alarms)


def test_a_subject_already_named_under_another_check_is_still_new(tmp_path: Path) -> None:
    failing, _ = _missed_and_clean(tmp_path)
    alarm = failing.alarms[0]
    body = tmp_path / "v.md"
    body.write_text(render_markdown(failing), encoding="utf-8")
    others = "".join(f"- **{a.check}** `{a.subject}`: x\n" for a in failing.alarms[1:])

    gh = _Gh([_ALARM], body=f"- **some_other_check** `{alarm.subject}`: x\n" + others)
    done = cv.latch("o/r", failing, body, runner=gh)

    assert done == "refreshed #7, 1 new alarm(s) commented"
    comment = next(c for c in gh.calls if c[1:3] == ["issue", "comment"])[-1]
    assert f"**{alarm.check}** `{alarm.subject}`" in comment


def test_a_long_verdict_lists_a_bounded_number_of_alarms(tmp_path: Path) -> None:
    failing, _ = _missed_and_clean(tmp_path)
    many = failing.model_copy(
        update={
            "alarms": [
                cv.CoverageAlarm(check="missed_forecast", subject=f"scotus/{n} {EVENT}", detail="d")
                for n in range(cv.ALARMS_LISTED + 25)
            ]
        }
    )

    body = render_markdown(many)

    assert body.count("- **missed_forecast**") == cv.ALARMS_LISTED
    assert "- and 25 more, not listed." in body
    assert len(body) <= cv.ALARM_BODY_CHARS + 200
    # Only listed alarms can be new, so the unlisted ones never comment daily.
    path = tmp_path / "many.md"
    path.write_text(body, encoding="utf-8")
    gh = _Gh([_ALARM], body=body)
    assert cv.latch("o/r", many, path, runner=gh) == "refreshed #7"


def test_the_latch_touches_only_an_issue_the_workflow_token_opened(tmp_path: Path) -> None:
    _, passing = _missed_and_clean(tmp_path)
    gh = _Gh(
        [
            {"number": 1, "title": cv.ISSUE_TITLE, "user": {"login": "someone"}},
            {"number": 2, "title": "Another report", "user": {"login": alarm_issue.ALARM_AUTHOR}},
            {**_ALARM, "number": 3, "pull_request": {}},
        ]
    )
    assert cv.latch("o/r", passing, tmp_path / "v.md", runner=gh) == "no alarm, and no open issue"


def test_the_alarm_command_refuses_what_it_cannot_read(tmp_path: Path) -> None:
    bad = tmp_path / "v.json"
    bad.write_text("{}", encoding="utf-8")
    args = ["coverage-verdict-alarm", "--verdict", str(bad), "--report", str(bad)]
    assert CliRunner().invoke(app, [*args, "--repo", "o/r"]).exit_code == 2
    assert CliRunner().invoke(app, [*args, "--repo", "not a repo"]).exit_code == 2


def _fail(data: Path, docket: int, predictor_id: str, runs: int) -> None:
    event = CasePaths(data, "scotus", docket).event(EVENT)
    for n in range(runs):
        attempt = event.prediction_attempt(predictor_id, f"2026110{n + 1}T141200Z")
        attempt.parent.mkdir(parents=True, exist_ok=True)
        attempt.write_text("{}\n")


def test_a_cell_at_the_attempt_cap_alarms_while_its_event_is_open(tmp_path: Path) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db):
        pass
    first, second = (p.id for p in enabled_predictors(PREDICTORS)[:2])
    _fail(data, 1, first, 3)  # capped, open, unforecast: the alarm
    _fail(data, 2, first, 2)  # under the cap: still re-queued
    _fail(data, 3, first, 3)  # capped, but a later prediction landed
    seed_prediction(data, "scotus", 3, EVENT, predictor_id=first)
    _fail(data, 4, first, 3)  # capped, but decided: the monitor's to report
    CasePaths(data, "scotus", 4).event(EVENT).outcome.write_text("{}\n")
    _fail(data, 5, "retired-predictor", 3)  # not enabled: owed nothing
    seed_prediction(data, "scotus", 1, EVENT, predictor_id=second)  # another engine's cell

    assert [
        (c.case_id, c.predictor_id, c.failures)
        for c in attempt_capped_cells(data, [first, second], max_attempts=3)
    ] == [("scotus/1", first, 3)]
    assert attempt_capped_cells(data, [first, second], max_attempts=0) == []

    with corpus.connect_readonly(db) as conn:
        verdict = coverage_verdict(conn, data, PREDICTORS, today=TODAY, max_attempts=3)

    assert [(a.check, a.subject) for a in verdict.alarms] == [
        ("attempt_capped", f"scotus/1 {EVENT}")
    ]
    assert verdict.counts["attempt_capped_open_cells"] == 1
    assert "reached the predict attempt cap" in render_markdown(verdict)


def test_the_verdict_carries_the_offices_listing_when_handed_one(tmp_path: Path) -> None:
    db, data = corpus.corpus_db_path(tmp_path / "corpus"), tmp_path / "data"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="26-101",
                    case_name="Acme Warden v. Roe",
                    date_filed=date(2026, 9, 1),
                )
            ],
        )

    def verdict(listing: SgPetitionListing | None) -> CoverageVerdict:
        with corpus.connect_readonly(db) as conn:
            return coverage_verdict(conn, data, PREDICTORS, today=TODAY, sg_listing=listing)

    unasked = verdict(None)
    assert unasked.ok and unasked.counts["sg_listed_petitions"] is None
    assert "Solicitor General's listing" not in render_markdown(unasked)

    listed = verdict(SgPetitionListing(frozenset({"26-101", "25-9"}), oldest_filed=TODAY))
    assert [(a.check, a.subject) for a in listed.alarms] == [("federal_label", "26-101")]
    assert (
        listed.counts["sg_listed_petitions"],
        listed.counts["sg_listed_pending"],
        listed.counts["sg_listed_not_federal"],
    ) == (2, 1, 1)
    assert "1 are pending here, 1 outside the federal band" in render_markdown(listed)

    unread = verdict(SgPetitionListing(frozenset(), error="the listing was not found"))
    assert [a.subject for a in unread.alarms] == [SG_LISTING_SUBJECT]
    assert unread.counts["sg_listed_petitions"] is None
    assert "was not read: the listing was not found" in render_markdown(unread)
