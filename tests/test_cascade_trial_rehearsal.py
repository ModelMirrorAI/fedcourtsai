"""The local cascade on a prediction slice's docket, and its trial rehearsal.

A slice docket goes to the slice's own actors and is forecast on one named
trial event. Where the corpus stores none, ``--rehearse-trial`` plans the
docket in the run with the watchlist pass's reader, so each case here compares
what the cascade wrote against what the pass writes for the same docket and
day. The rehearsal reads its docket on the committed switch-on day, since the
day the cases run on is earlier.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.ai_watchlist import AI_WATCHLIST_FILENAME, load_ai_watchlist
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.cascade import CascadeError, CascadeReport, run_cascade
from fedcourtsai.pipeline.trial_events import run_pass
from fedcourtsai.registry import predictors_for
from fedcourtsai.schemas import Prediction, PredictionContext, Stage, TrialRecord
from fedcourtsai.serialize import read_model
from fedcourtsai.trial_adjudications import (
    TRIAL_ADJUDICATIONS_FILENAME,
    load_trial_adjudications,
)
from fedcourtsai.trial_local_rules import TRIAL_LOCAL_RULES_FILENAME, load_trial_local_rules
from tests.fixture_metrics import fixture_metrics_root

RUN = "20261120T120000Z"
#: Before the switch-on day, so the rehearsal reads the docket on that day.
TODAY = date(2026, 11, 20)
SLICE = "ai-watchlist"
COURT, DOCKET = "cand", 100
CASE = f"{COURT}/{DOCKET}"
DISMISSAL = "evt-motion-trial-dismissal-45"
JUDGMENT = "evt-order-trial-judgment"
#: A docket of the fixture corpus that no slice lists.
COURT_DOCKET = ("ca9", 103)


def entry(number: int, description: str, day: str) -> dict[str, Any]:
    return {
        "id": 1000 + number,
        "entry_number": number,
        "date_filed": day,
        "description": description,
        "recap_documents": [],
    }


BRIEFED = [
    entry(45, "MOTION to Dismiss filed by Developer, Inc.", "2026-01-10"),
    entry(
        52, "OPPOSITION/RESPONSE (re 45 MOTION to Dismiss ) filed byListed Author.", "2026-01-24"
    ),
    entry(58, "REPLY (re 45 MOTION to Dismiss ) filed byDeveloper, Inc.", "2026-01-31"),
]
#: A hearing minute the resolver cannot read as a ruling: the pass holds the motion's event.
MINUTE = entry(
    60,
    "Minute Entry for proceedings held before Judge A. Bench: Motion Hearing held "
    + "re 45 Motion to Dismiss. Motion DENIED for the reasons stated on the record.",
    "2026-06-10",
)
GRANTED = entry(70, "ORDER by Judge A. Bench granting 45 Motion to Dismiss.", "2026-07-20")

WATCHLIST = {
    "categories": {"copyright": "Training on works."},
    "cases": [
        {
            "name": "Listed v. Developer",
            "court": COURT,
            "docket_id": DOCKET,
            "docket_number": "3:26-cv-00100",
            "category": "copyright",
            "why": "Training.",
            "developers": ["Developer"],
            "added": "2026-10-30",
            "related": [
                {
                    "court": "ca9",
                    "docket_id": 9101,
                    "docket_number": "26-101",
                    "relation": "appeal",
                },
            ],
        }
    ],
}


def _config(tmp_path: Path) -> Path:
    """The committed config with the watchlist replaced by one listing the test's docket."""
    root = tmp_path / "config"
    shutil.copytree("config", root)
    (root / AI_WATCHLIST_FILENAME).write_text(yaml.safe_dump(WATCHLIST))
    return root


def _corpus(tmp_path: Path, *entries: dict[str, Any], name: str = "corpus") -> Path:
    """The fixture corpus plus the listed district docket, stored with ``entries``."""
    db = corpus.corpus_db_path(tmp_path / name)
    fixture.build_fixture_corpus(db)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=CASE,
                    court=COURT,
                    docket_number="3:26-cv-00100",
                    case_name="Listed v. Developer",
                    last_pulled=date(2026, 11, 18),
                )
            ],
        )
        corpus.upsert_snapshot(
            conn,
            CASE,
            date(2026, 11, 18),
            {
                "id": DOCKET,
                "docket_number": "3:26-cv-00100",
                "case_name": "Listed v. Developer",
                "assigned_to_str": "A. Bench",
                "docket_entries": list(entries),
            },
        )
    return db


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(tmp_path: Path, db: Path, config: Path, **kwargs: Any) -> CascadeReport:
    kwargs.setdefault("court", COURT)
    kwargs.setdefault("docket", DOCKET)
    return run_cascade(
        corpus_db_path=db,
        data_root=tmp_path / "data",
        config_root=config,
        metrics_root=fixture_metrics_root(tmp_path),
        run_id=RUN,
        today=TODAY,
        **kwargs,
    )


def test_a_rehearsal_runs_the_slice_predictor_on_the_event_the_pass_would_write(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    db = _corpus(tmp_path, *BRIEFED)
    before = _digest(db)

    report = _run(
        tmp_path, db, config, event=DISMISSAL, predictor="claude-trial", rehearse_trial=True
    )

    assert report.valid, report.problems
    assert report.events == (DISMISSAL,)
    assert report.rehearsed == (DISMISSAL,)
    assert report.unforecastable == ()
    assert report.outcomes == () and report.evaluations == ()
    # One cell, the slice's own predictor's: three documents under its id.
    paths = CasePaths(tmp_path / "data", COURT, DOCKET)
    cell = paths.event(DISMISSAL).prediction("claude-trial", RUN)
    assert len(report.predictions) == 3
    assert {p.parent for p in report.predictions} == {cell.parent}
    prediction = read_model(cell, Prediction)
    assert prediction.predictor_id == "claude-trial"
    assert [c.claim_id for c in prediction.claims or []] == ["trial-ruling-granted"]
    assert {d.claim_id for d in prediction.claim_distributions or []} == {
        "trial-ruling",
        "trial-leave",
    }

    # The record a forward trial cell gets: the whole snapshot, the context, trial.json.
    (placement,) = report.placements
    assert (placement.role, placement.mode, placement.cutoff) == ("predict", "forward", None)
    assert report.snapshot is not None and report.context is not None
    staged = json.loads(report.snapshot.read_text())
    assert [e["entry_number"] for e in staged["docket_entries"]] == [45, 52, 58]
    context = read_model(report.context, PredictionContext)
    assert context.mode == "forward" and context.cert_anchor is None
    assert report.trial == paths.trial_record
    trial = TrialRecord.model_validate_json(paths.trial_record.read_text())
    assert trial.event_id == DISMISSAL and trial.assigned_judge == "A. Bench"
    assert trial.briefing is not None and trial.briefing.motion.entry_number == 45
    assert [d.case_id for d in trial.related_dockets] == ["ca9/9101"]

    # The corpus was only read, and holds no trial event.
    assert _digest(db) == before
    with corpus.connect_readonly(db, backend="local") as conn:
        assert [e for e in corpus.events_for_case(conn, CASE) if e.stage == Stage.trial] == []

    # The definition is the pass's own for the same docket on the day read.
    passed = _corpus(tmp_path, *BRIEFED, name="passed")
    report_pass = run_pass(
        passed,
        tmp_path / "passed-data",
        load_ai_watchlist(config / AI_WATCHLIST_FILENAME),
        today=moments.TRIAL_SWITCH_ON,
        local_rules=load_trial_local_rules(config / TRIAL_LOCAL_RULES_FILENAME),
        adjudicated=load_trial_adjudications(config / TRIAL_ADJUDICATIONS_FILENAME),
    )
    assert (CASE, DISMISSAL) in report_pass.opened
    written = CasePaths(tmp_path / "passed-data", COURT, DOCKET).event(DISMISSAL).event_file
    assert paths.event(DISMISSAL).event_file.read_bytes() == written.read_bytes()
    definition = yaml.safe_load(written.read_text())
    assert definition["stage"] == "trial" and definition["moment"] == "trial-dismissal"
    assert definition["opened_at"] == moments.TRIAL_SWITCH_ON.isoformat()
    # Only the named event is materialized: the judgment event is planned and not run.
    assert not paths.event(JUDGMENT).event_file.exists()


def test_a_rehearsal_without_a_named_predictor_runs_the_slice_fleet_alone(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    report = _run(
        tmp_path, _corpus(tmp_path, *BRIEFED), config, event=JUDGMENT, rehearse_trial=True
    )

    assert report.valid, report.problems
    fleet = {p.id for p in predictors_for(config / "predictors.yaml", SLICE)}
    assert fleet and {p.parent.parent.name for p in report.predictions} == fleet
    # The judgment event names no motion, so its trial record carries no briefing.
    assert report.trial is not None
    assert TrialRecord.model_validate_json(report.trial.read_text()).briefing is None


def test_a_slice_docket_without_the_flag_is_refused_naming_it(tmp_path: Path) -> None:
    with pytest.raises(CascadeError, match=r"no open\s+trial event.*--rehearse-trial"):
        _run(tmp_path, _corpus(tmp_path, *BRIEFED), _config(tmp_path), event=DISMISSAL)
    assert not (tmp_path / "data").exists()


def test_a_rehearsal_names_its_event(tmp_path: Path) -> None:
    with pytest.raises(CascadeError, match=rf"pass --event \(available on {CASE}: ") as refused:
        _run(tmp_path, _corpus(tmp_path, *BRIEFED), _config(tmp_path), rehearse_trial=True)
    assert DISMISSAL in str(refused.value) and JUDGMENT in str(refused.value)


def test_an_event_the_pass_holds_is_refused_with_its_reason(tmp_path: Path) -> None:
    db = _corpus(tmp_path, *BRIEFED, MINUTE)
    with pytest.raises(
        CascadeError, match=r"the pass holds it.*a later entry may already dispose of the motion"
    ):
        _run(tmp_path, db, _config(tmp_path), event=DISMISSAL, rehearse_trial=True)
    assert not (tmp_path / "data").exists()


def test_a_ruled_motion_and_an_unplanned_event_are_refused(tmp_path: Path) -> None:
    config = _config(tmp_path)
    db = _corpus(tmp_path, *BRIEFED, GRANTED)
    # The court ruled before the pass first read the motion: no event opens.
    with pytest.raises(CascadeError, match="the opener plans no such event"):
        _run(tmp_path, db, config, event=DISMISSAL, rehearse_trial=True)
    with pytest.raises(CascadeError, match="the opener plans no such event"):
        _run(tmp_path, db, config, event="evt-motion-trial-dismissal-999", rehearse_trial=True)
    with pytest.raises(CascadeError, match="no declared trial moment writes that id"):
        _run(tmp_path, db, config, event="evt-appeal-disposition", rehearse_trial=True)


def test_a_predictor_of_the_other_population_is_refused(tmp_path: Path) -> None:
    config = _config(tmp_path)
    db = _corpus(tmp_path, *BRIEFED)
    with pytest.raises(CascadeError, match=rf"'claude-baseline' is not enabled .*'{SLICE}'"):
        _run(
            tmp_path,
            db,
            config,
            event=DISMISSAL,
            predictor="claude-baseline",
            rehearse_trial=True,
        )
    court, docket = COURT_DOCKET
    with pytest.raises(CascadeError, match=r"'claude-trial' is not enabled .*'scotus'"):
        _run(tmp_path, db, config, court=court, docket=docket, predictor="claude-trial")
    with pytest.raises(CascadeError, match=r"'claude-trial' is not enabled .*'scotus'"):
        _run(tmp_path, db, config, court="scotus", docket=24001, predictor="claude-trial")
    assert not (tmp_path / "data").exists()


def test_a_rehearsal_is_refused_on_a_docket_no_slice_lists(tmp_path: Path) -> None:
    court, docket = COURT_DOCKET
    with pytest.raises(CascadeError, match="--rehearse-trial plans a trial event"):
        _run(
            tmp_path,
            _corpus(tmp_path, *BRIEFED),
            _config(tmp_path),
            court=court,
            docket=docket,
            rehearse_trial=True,
        )


def test_a_stored_open_trial_event_runs_without_the_flag(tmp_path: Path) -> None:
    # After the pass's first writing day the event is a corpus row, and the
    # cascade targets it as it targets any stored event.
    config = _config(tmp_path)
    db = _corpus(tmp_path, *BRIEFED)
    run_pass(
        db,
        tmp_path / "pass-data",
        load_ai_watchlist(config / AI_WATCHLIST_FILENAME),
        today=moments.TRIAL_SWITCH_ON,
    )

    report = _run(tmp_path, db, config, event=DISMISSAL, predictor="codex-trial")

    assert report.valid, report.problems
    assert report.rehearsed == () and report.trial is not None
    assert len(report.predictions) == 3


def test_the_command_reports_a_rehearsal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _corpus(tmp_path, *BRIEFED)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(db.parent))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(_config(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(fixture_metrics_root(tmp_path)))
    base = ["local-cascade", "--court", COURT, "--docket", str(DOCKET), "--event", DISMISSAL]
    smoke = ["--predictor", "gemini-trial", "--require-predictions", "--require-record"]

    refused = CliRunner().invoke(app, [*base, *smoke])
    assert refused.exit_code == 2
    assert "--rehearse-trial" in refused.output

    result = CliRunner().invoke(app, [*base, *smoke, "--rehearse-trial", "--run-id", RUN])
    assert result.exit_code == 0, result.output
    assert f"provisioned: predict {DISMISSAL} — forward, as-stored, no cut" in result.output
    assert "a rehearsal: the event is planned in this run" in result.output
    assert "not a cell run-predict mints" not in result.output
    assert "trial:       " in result.output
    assert "predictions: 3 file(s)" in result.output
    assert "validate:    OK" in result.output


def test_a_docket_stored_with_no_entries_is_refused(tmp_path: Path) -> None:
    """The opener has nothing to read, so the rehearsal plans nothing and no cell runs."""
    with pytest.raises(CascadeError, match="no stored docket entries"):
        _run(tmp_path, _corpus(tmp_path), _config(tmp_path), event=DISMISSAL, rehearse_trial=True)
    assert not (tmp_path / "data").exists()
