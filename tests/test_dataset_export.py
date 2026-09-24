"""The release dataset export over a small fixture ledger."""

import csv
import json
import os
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, process_version
from fedcourtsai.cli import app
from fedcourtsai.dataset_export import (
    DATA_DICTIONARY,
    MANIFEST,
    BuildContext,
    ExportError,
    ExportTables,
    build_tables,
    git_source,
    ledger_commit_index,
    read_docket_numbers,
    render_data_dictionary,
    verify_bundle,
    with_docket_numbers,
    write_bundle,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    ExportGradingRow,
    ExportManifest,
    ExportPredictionRow,
    ExportReasoningRecord,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.store import stratify
from tests.conftest import bless_process

runner = CliRunner()

FREEZE = datetime(2026, 1, 1, tzinfo=UTC)
BLESSED = "sha256:blessed"


def _stamp(when: datetime, digest: str = BLESSED) -> ProcessVersion:
    return ProcessVersion(label="proc-v1", digest=digest, stamped_at=when, pipeline_sha="abc123")


def _event(data_root: Path, case_id: str, event_id: str = "evt-petition-disposition") -> None:
    court, _, docket = case_id.partition("/")
    paths = CasePaths(data_root, court, int(docket)).event(event_id)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=case_id,
            kind=EventKind.petition,
            title=f"Petitioner v. Respondent ({case_id})",
        ),
    )


def _prediction(
    data_root: Path,
    case_id: str,
    *,
    predictor_id: str = "alpha",
    run_id: str = "p1",
    stamp: ProcessVersion | None = None,
    mode: str | None = None,
    docs: bool = False,
    event_id: str = "evt-petition-disposition",
) -> None:
    court, _, docket = case_id.partition("/")
    paths = CasePaths(data_root, court, int(docket)).event(event_id)
    context = (
        PredictionContext(
            mode=mode,
            snapshot_date=date(2026, 1, 15),
            signals_observable=False,
            term=2025,
        )
        if mode is not None
        else None
    )
    write_json(
        paths.prediction(predictor_id, run_id),
        Prediction(
            case_id=case_id,
            event_id=event_id,
            predictor_id=predictor_id,
            engine=Engine.claude_code,
            run_id=run_id,
            created_at=datetime(2026, 1, 20, tzinfo=UTC),
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
            predicted_reasoning_doc="predicted_reasoning.md" if docs else None,
            process_version=stamp,
            context=context,
        ),
    )
    if docs:
        paths.reasoning(predictor_id, run_id).write_text("Why 0.7.\n")
        paths.predicted_reasoning(predictor_id, run_id).write_text("The Court grants.\n")


def _outcome(data_root: Path, case_id: str, resolved_at: date = date(2026, 3, 1)) -> None:
    court, _, docket = case_id.partition("/")
    paths = CasePaths(data_root, court, int(docket)).event("evt-petition-disposition")
    write_json(
        paths.outcome,
        Outcome(
            case_id=case_id,
            event_id="evt-petition-disposition",
            resolved_at=resolved_at,
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )


def _grade(
    data_root: Path,
    case_id: str,
    evaluator_id: str,
    *,
    run_id: str = "r1",
    predictor_id: str = "alpha",
    prediction_run_id: str = "p1",
    stamped: datetime | None = datetime(2026, 3, 2, tzinfo=UTC),
    leakage: bool | None = False,
) -> None:
    court, _, docket = case_id.partition("/")
    paths = CasePaths(data_root, court, int(docket)).event("evt-petition-disposition")
    write_json(
        paths.evaluation(evaluator_id, predictor_id, run_id),
        Evaluation(
            case_id=case_id,
            event_id="evt-petition-disposition",
            predictor_id=predictor_id,
            evaluator_id=evaluator_id,
            engine=Engine.codex,
            run_id=run_id,
            prediction_run_id=prediction_run_id,
            created_at=datetime(2026, 3, 2, tzinfo=UTC),
            correct=1,
            brier_score=0.09,
            leakage_suspected=leakage,
            process_version=_stamp(stamped, "sha256:judge") if stamped else None,
        ),
    )


def _ledger(data_root: Path) -> None:
    """One case per scenario the export has to tell apart."""
    frozen = _stamp(datetime(2026, 2, 1, tzinfo=UTC))
    # 100: counted, forward; judge e1 re-graded (r1 superseded by r2); e9 unstamped.
    _event(data_root, "scotus/100")
    _prediction(data_root, "scotus/100", stamp=frozen, mode="forward", docs=True)
    _outcome(data_root, "scotus/100")
    _grade(data_root, "scotus/100", "e1", run_id="r1")
    _grade(data_root, "scotus/100", "e1", run_id="r2", stamped=datetime(2026, 3, 5, tzinfo=UTC))
    _grade(data_root, "scotus/100", "e9", stamped=None)
    # 101: a forward claim the outcome's date contradicts.
    _event(data_root, "scotus/101")
    _prediction(
        data_root, "scotus/101", stamp=_stamp(datetime(2026, 3, 10, tzinfo=UTC)), mode="forward"
    )
    _outcome(data_root, "scotus/101")
    _grade(data_root, "scotus/101", "e1", stamped=datetime(2026, 3, 11, tzinfo=UTC))
    # 102: every judge flags leakage.
    _event(data_root, "scotus/102")
    _prediction(data_root, "scotus/102", stamp=frozen, mode="forward")
    _outcome(data_root, "scotus/102")
    _grade(data_root, "scotus/102", "e1", leakage=True)
    _grade(data_root, "scotus/102", "e2", leakage=True)
    # 103: one judge of three flags leakage.
    _event(data_root, "scotus/103")
    _prediction(data_root, "scotus/103", stamp=frozen, mode="forward")
    _outcome(data_root, "scotus/103")
    _grade(data_root, "scotus/103", "e1", leakage=True)
    _grade(data_root, "scotus/103", "e2")
    _grade(data_root, "scotus/103", "e3")
    # 104: unresolved, two frozen runs (p2 is the staged one).
    _event(data_root, "scotus/104")
    _prediction(data_root, "scotus/104", stamp=frozen, mode="forward")
    _prediction(
        data_root,
        "scotus/104",
        run_id="p2",
        stamp=_stamp(datetime(2026, 2, 2, tzinfo=UTC)),
        mode="forward",
    )
    # 105: a shakedown (unstamped) prediction, graded.
    _event(data_root, "scotus/105")
    _prediction(data_root, "scotus/105", predictor_id="shake")
    _outcome(data_root, "scotus/105")
    _grade(data_root, "scotus/105", "e1", predictor_id="shake")


@pytest.fixture
def ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    bless_process(monkeypatch, BLESSED, since=FREEZE)
    data_root = tmp_path / "data"
    _ledger(data_root)
    return data_root


def _by_case(tables: ExportTables) -> dict[tuple[str, str], ExportPredictionRow]:
    return {(row.case_id, row.run_id): row for row in tables.predictions}


def test_the_frozen_population_is_every_frozen_prediction_graded_or_not(ledger: Path) -> None:
    tables = build_tables(ledger)
    assert sorted(_by_case(tables)) == [
        ("scotus/100", "p1"),
        ("scotus/101", "p1"),
        ("scotus/102", "p1"),
        ("scotus/103", "p1"),
        ("scotus/104", "p1"),
        ("scotus/104", "p2"),
    ]
    assert all(row.process_frozen for row in tables.predictions)
    everything = build_tables(ledger, all_versions=True)
    shake = _by_case(everything)[("scotus/105", "p1")]
    assert shake.predictor_id == "shake"
    assert shake.process_frozen is False
    assert shake.scored is True


def test_counted_and_set_aside_flags(ledger: Path) -> None:
    rows = _by_case(build_tables(ledger))
    counted = rows[("scotus/100", "p1")]
    assert (counted.scored, counted.set_aside, counted.stratum) == (True, False, "forward")
    # e1 (newest run) and the out-of-scope e9 grading: one in-scope judge.
    assert counted.gradings_total == 1

    breached = rows[("scotus/101", "p1")]
    assert breached.forward_claim_excluded is True
    assert (breached.scored, breached.set_aside, breached.stratum) == (False, True, None)

    all_flagged = rows[("scotus/102", "p1")]
    assert (all_flagged.gradings_total, all_flagged.gradings_leakage_flagged) == (2, 2)
    assert (all_flagged.scored, all_flagged.set_aside) == (False, True)

    one_flagged = rows[("scotus/103", "p1")]
    assert (one_flagged.gradings_total, one_flagged.gradings_leakage_flagged) == (3, 1)
    assert (one_flagged.scored, one_flagged.set_aside) == (True, False)


def test_an_unresolved_frozen_prediction_is_exported_with_a_null_outcome(ledger: Path) -> None:
    rows = _by_case(build_tables(ledger))
    for run_id in ("p1", "p2"):
        row = rows[("scotus/104", run_id)]
        assert (row.resolved_at, row.actual_disposition, row.actual_granted) == (None, None, None)
        assert (row.scored, row.set_aside, row.gradings_total) == (False, False, 0)
    assert rows[("scotus/104", "p1")].staged is False
    assert rows[("scotus/104", "p2")].staged is True
    assert rows[("scotus/104", "p2")].stage == "cert"


@pytest.mark.parametrize("all_versions", [False, True])
def test_the_scored_flag_and_counted_gradings_match_stratify(
    ledger: Path, all_versions: bool
) -> None:
    tables = build_tables(ledger, all_versions=all_versions)
    run = stratify(ledger, frozen_only=not all_versions)
    cells = {
        (ev.case_id, ev.event_id, ev.predictor_id, ev.evaluator_id, ev.run_id)
        for ev, _s, _st, _m in run.cells
    }
    counted = {
        (g.case_id, g.event_id, g.predictor_id, g.evaluator_id, g.run_id)
        for g in tables.gradings
        if g.counted
    }
    assert counted == cells
    scored = {(p.case_id, p.predictor_id, p.run_id) for p in tables.predictions if p.scored}
    assert scored == {
        (ev.case_id, ev.predictor_id, ev.prediction_run_id) for ev, _s, _st, _m in run.cells
    }


def test_gradings_are_long_form_and_join_the_predictions(ledger: Path) -> None:
    tables = build_tables(ledger)
    keys = {(p.case_id, p.event_id, p.predictor_id, p.run_id) for p in tables.predictions}
    for grading in tables.gradings:
        assert (
            grading.case_id,
            grading.event_id,
            grading.predictor_id,
            grading.prediction_run_id,
        ) in keys
    reasons = {(g.case_id, g.evaluator_id, g.run_id): g.excluded_reason for g in tables.gradings}
    assert reasons == {
        ("scotus/100", "e1", "r1"): "superseded",
        ("scotus/100", "e1", "r2"): None,
        ("scotus/100", "e9", "r1"): "out_of_scope",
        ("scotus/101", "e1", "r1"): "forward_claim",
        ("scotus/102", "e1", "r1"): "leakage",
        ("scotus/102", "e2", "r1"): "leakage",
        ("scotus/103", "e1", "r1"): "leakage",
        ("scotus/103", "e2", "r1"): None,
        ("scotus/103", "e3", "r1"): None,
    }
    grading = next(g for g in tables.gradings if g.case_id == "scotus/103")
    # The recorded model, never a back-fill from today's engine default.
    assert grading.evaluator_model is None
    assert _by_case(tables)[("scotus/103", "p1")].model is None


def test_a_regrade_of_another_run_supersedes_across_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One judge grades run p1, then the same predictor's p2 on the same event:
    # stratify collapses on (case, event, predictor, evaluator), so p1's grading
    # is superseded and p1 is left with no in-scope grading.
    bless_process(monkeypatch, BLESSED, since=FREEZE)
    data_root = tmp_path / "data"
    _event(data_root, "scotus/200")
    _prediction(data_root, "scotus/200", stamp=_stamp(datetime(2026, 2, 1, tzinfo=UTC)))
    _prediction(
        data_root, "scotus/200", run_id="p2", stamp=_stamp(datetime(2026, 2, 2, tzinfo=UTC))
    )
    _outcome(data_root, "scotus/200")
    _grade(data_root, "scotus/200", "e1", run_id="r1")
    _grade(
        data_root,
        "scotus/200",
        "e1",
        run_id="r2",
        prediction_run_id="p2",
        stamped=datetime(2026, 3, 5, tzinfo=UTC),
    )
    tables = build_tables(data_root)
    reasons = {(g.prediction_run_id, g.run_id): g.excluded_reason for g in tables.gradings}
    assert reasons == {("p1", "r1"): "superseded", ("p2", "r2"): None}
    rows = _by_case(tables)
    assert (rows[("scotus/200", "p1")].gradings_total, rows[("scotus/200", "p1")].scored) == (
        0,
        False,
    )
    assert rows[("scotus/200", "p2")].scored is True


def test_a_forward_claim_resolved_on_its_clock_day_is_retrospective_not_set_aside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The breach rule is strict (resolved before the clock day); the stratum
    # rule counts a same-day tie retrospective. The row carries mode=forward.
    bless_process(monkeypatch, BLESSED, since=FREEZE)
    data_root = tmp_path / "data"
    _event(data_root, "scotus/400")
    _prediction(
        data_root,
        "scotus/400",
        stamp=_stamp(datetime(2026, 3, 1, 15, tzinfo=UTC)),
        mode="forward",
    )
    _outcome(data_root, "scotus/400", resolved_at=date(2026, 3, 1))
    _grade(data_root, "scotus/400", "e1")
    row = build_tables(data_root).predictions[0]
    assert row.mode == "forward"
    assert (row.stratum, row.scored) == ("retrospective", True)
    assert (row.forward_claim_excluded, row.set_aside) == (False, False)


@pytest.mark.parametrize(
    ("out_of_scope_flagged", "in_scope_flagged", "set_aside"),
    [(True, False, False), (False, True, True)],
)
def test_only_in_scope_gradings_decide_set_aside(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    out_of_scope_flagged: bool,
    in_scope_flagged: bool,
    set_aside: bool,
) -> None:
    bless_process(monkeypatch, BLESSED, since=FREEZE)
    data_root = tmp_path / "data"
    _event(data_root, "scotus/500")
    _prediction(data_root, "scotus/500", stamp=_stamp(datetime(2026, 2, 1, tzinfo=UTC)))
    _outcome(data_root, "scotus/500")
    _grade(data_root, "scotus/500", "e1", stamped=None, leakage=out_of_scope_flagged)
    _grade(data_root, "scotus/500", "e2", leakage=in_scope_flagged)
    row = build_tables(data_root).predictions[0]
    assert (row.gradings_total, row.gradings_leakage_flagged) == (1, int(in_scope_flagged))
    assert row.set_aside is set_aside
    assert row.scored is not set_aside


def test_a_grading_both_rules_catch_names_both(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bless_process(monkeypatch, BLESSED, since=FREEZE)
    data_root = tmp_path / "data"
    _event(data_root, "scotus/300")
    _prediction(
        data_root, "scotus/300", stamp=_stamp(datetime(2026, 3, 10, tzinfo=UTC)), mode="forward"
    )
    _outcome(data_root, "scotus/300")
    _grade(data_root, "scotus/300", "e1", stamped=datetime(2026, 3, 11, tzinfo=UTC), leakage=True)
    tables = build_tables(data_root)
    assert [g.excluded_reason for g in tables.gradings] == ["forward_claim_and_leakage"]
    row = tables.predictions[0]
    assert (row.forward_claim_excluded, row.set_aside, row.scored) == (True, True, False)


def test_reasoning_is_keyed_to_the_prediction_and_null_where_absent(ledger: Path) -> None:
    records = {(r.case_id, r.run_id): r for r in build_tables(ledger).reasoning}
    assert records[("scotus/100", "p1")].reasoning == "Why 0.7.\n"
    assert records[("scotus/100", "p1")].predicted_reasoning == "The Court grants.\n"
    assert records[("scotus/101", "p1")].reasoning is None
    assert records[("scotus/101", "p1")].predicted_reasoning is None


class _SpyConnection:
    """A read connection that records every statement it runs."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.statements: list[str] = []

    def execute(self, sql: str, parameters: Any = (), /) -> Any:
        self.statements.append(sql)
        return self.inner.execute(sql, parameters)


def _corpus(corpus_root: Path) -> Path:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/100",
                    court="scotus",
                    docket_number="25-100",
                    case_name="CORPUS-ONLY CAPTION",
                    topic="CORPUS-ONLY TOPIC",
                    summary="CORPUS-ONLY SUMMARY",
                )
            ],
        )
        conn.commit()
    return db


def test_the_docket_number_is_the_only_corpus_field_read(ledger: Path, tmp_path: Path) -> None:
    db = _corpus(tmp_path / "corpus")
    with corpus.connect_readonly(db, backend="local") as conn:
        spy = _SpyConnection(conn)
        numbers = read_docket_numbers(spy, ["scotus/100", "scotus/101"])
    assert numbers == {"scotus/100": "25-100"}
    assert {sql.split(" FROM ")[0] for sql in spy.statements} == {"SELECT docket_number"}
    rows = _by_case(with_docket_numbers(build_tables(ledger), numbers))
    assert rows[("scotus/100", "p1")].docket_number == "25-100"
    assert rows[("scotus/101", "p1")].docket_number is None


#: An ambient identity (a Codespace sets its committer to GitHub) would
#: override the repo config the fixtures rely on.
_IDENTITY_ENV = ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL")


def _git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if k not in _IDENTITY_ENV}
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=env
    ).stdout.strip()


def _repo(root: Path) -> Path:
    """A git repo whose ledger lands one prediction by merge and one by direct commit."""
    repo = root / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "root")
    _git(repo, "switch", "-q", "-c", "feature")
    data_root = repo / "data"
    _event(data_root, "scotus/100")
    _prediction(data_root, "scotus/100", stamp=_stamp(datetime(2026, 2, 1, tzinfo=UTC)))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feature cell")
    _git(repo, "switch", "-q", "main")
    # The landing merge is GitHub's, as a web merge's committer is.
    _git(
        repo,
        "-c",
        "user.name=GitHub",
        "-c",
        "user.email=noreply@github.com",
        "merge",
        "-q",
        "--no-ff",
        "-m",
        "land feature",
        "feature",
    )
    _event(data_root, "scotus/101")
    _prediction(data_root, "scotus/101", stamp=_stamp(datetime(2026, 2, 1, tzinfo=UTC)))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "direct cell")
    return repo


def test_ledger_commit_is_the_first_parent_commit_that_added_the_file(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    data_root = repo / "data"
    source = git_source(data_root)
    assert source.head == _git(repo, "rev-parse", "HEAD")
    assert source.dirty is False
    index = ledger_commit_index(data_root, source)
    merged = CasePaths(data_root, "scotus", 100).event("evt-petition-disposition")
    direct = CasePaths(data_root, "scotus", 101).event("evt-petition-disposition")
    merge_sha = _git(repo, "rev-parse", "HEAD~1")
    assert index[merged.prediction("alpha", "p1").resolve()].sha == merge_sha
    assert index[direct.prediction("alpha", "p1").resolve()].sha == source.head
    assert index[merged.prediction("alpha", "p1").resolve()].by_github is True
    assert index[direct.prediction("alpha", "p1").resolve()].by_github is False
    # Every attributed commit resolves in the repository.
    for commit in index.values():
        _git(repo, "cat-file", "-e", commit.sha)


def test_the_source_commit_is_placed_against_main_first_parent(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    # No origin/main in the checkout: unknown, never guessed.
    assert git_source(repo / "data").on_main_first_parent is None
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    assert git_source(repo / "data").on_main_first_parent is True
    # The feature branch's commit reached main only as a merge's second parent.
    _git(repo, "switch", "-q", "feature")
    assert git_source(repo / "data").on_main_first_parent is False


def test_a_shallow_clone_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        check=True,
        capture_output=True,
    )
    with pytest.raises(ExportError, match="shallow"):
        git_source(shallow / "data")


def _invoke(data_root: Path, corpus_root: Path, *args: str) -> Any:
    return runner.invoke(
        app,
        ["export", *args],
        env={
            "FEDCOURTS_DATA_ROOT": str(data_root),
            "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
            "FEDCOURTS_CORPUS_BACKEND": "local",
        },
    )


def test_cli_builds_a_verified_deterministic_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bless_process(monkeypatch, BLESSED, since=FREEZE)
    repo = _repo(tmp_path)
    data_root = repo / "data"
    _outcome(data_root, "scotus/100")
    _grade(data_root, "scotus/100", "e1")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "grade")
    corpus_root = tmp_path / "corpus"
    _corpus(corpus_root)

    first, second = tmp_path / "b1", tmp_path / "b2"
    for out in (first, second):
        result = _invoke(data_root, corpus_root, "--out", str(out))
        assert result.exit_code == 0, result.output
    assert "2 prediction(s) (1 scored, 0 set aside)" in result.output

    names = sorted(p.relative_to(first).as_posix() for p in first.rglob("*") if p.is_file())
    assert names == sorted(
        p.relative_to(second).as_posix() for p in second.rglob("*") if p.is_file()
    )
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
    assert verify_bundle(first) == []
    assert not any(name.endswith(".py") for name in names)

    manifest = read_model(first / MANIFEST, ExportManifest)
    assert manifest.source_commit == _git(repo, "rev-parse", "HEAD")
    assert manifest.source_dirty is False
    assert manifest.process_scope == "frozen"
    assert manifest.frozen_process is not None
    assert manifest.frozen_process.digests == [BLESSED]
    assert manifest.frozen_process.since == FREEZE
    assert manifest.build_command == "fedcourts export --out <dir>"
    assert manifest.docket_numbers == "corpus" and manifest.corpus_vintage is not None
    assert manifest.counts["predictions"] == 2 and manifest.counts["gradings"] == 1

    with (first / "predictions.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0]) == list(ExportPredictionRow.model_fields)
    assert {row["docket_number"] for row in rows} == {"25-100", ""}
    for row in rows:
        _git(repo, "cat-file", "-e", row["ledger_commit"])
    table = pq.read_table(first / "predictions.parquet")
    assert table.column_names == list(ExportPredictionRow.model_fields)
    assert table.num_rows == 2
    assert pq.read_table(first / "gradings.parquet").column_names == list(
        ExportGradingRow.model_fields
    )
    lines = (first / "reasoning.jsonl").read_text().splitlines()
    assert [sorted(json.loads(line)) for line in lines] == [
        sorted(ExportReasoningRecord.model_fields)
    ] * 2
    # No corpus field beyond the docket number reaches any file.
    for name in names:
        text = (first / name).read_bytes()
        assert b"CORPUS-ONLY" not in text, name


def test_cli_refuses_a_missing_corpus_unless_allowed(ledger: Path, tmp_path: Path) -> None:
    corpus_root = tmp_path / "no-corpus"
    refused = _invoke(ledger, corpus_root, "--out", str(tmp_path / "b"), "--no-git")
    assert refused.exit_code == 1
    assert "--allow-missing-docket-numbers" in refused.output
    assert not (tmp_path / "b").exists()

    out = tmp_path / "b"
    built = _invoke(
        ledger, corpus_root, "--out", str(out), "--no-git", "--allow-missing-docket-numbers"
    )
    assert built.exit_code == 0, built.output
    manifest = read_model(out / MANIFEST, ExportManifest)
    assert (manifest.docket_numbers, manifest.corpus_vintage) == ("omitted", None)
    assert (manifest.ledger_commits, manifest.source_commit) == ("omitted", None)
    assert manifest.counts["predictions_without_docket_number"] == 6
    assert manifest.build_command == (
        "fedcourts export --no-git --allow-missing-docket-numbers --out <dir>"
    )


def test_cli_refuses_a_shallow_clone_unless_no_git(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        check=True,
        capture_output=True,
    )
    args = ("--out", str(tmp_path / "b"), "--all-versions", "--allow-missing-docket-numbers")
    refused = _invoke(shallow / "data", tmp_path / "c", *args)
    assert refused.exit_code == 1
    assert "shallow" in refused.output
    built = _invoke(shallow / "data", tmp_path / "c", *args, "--no-git")
    assert built.exit_code == 0, built.output
    manifest = read_model(tmp_path / "b" / MANIFEST, ExportManifest)
    assert manifest.process_scope == "all" and manifest.frozen_process is None


def test_cli_refuses_a_non_empty_out_dir(ledger: Path, tmp_path: Path) -> None:
    out = tmp_path / "b"
    out.mkdir()
    (out / "keep.txt").write_text("mine\n")
    result = _invoke(
        ledger, tmp_path / "c", "--out", str(out), "--no-git", "--allow-missing-docket-numbers"
    )
    assert result.exit_code == 1
    assert "not an empty directory" in result.output
    assert (out / "keep.txt").read_text() == "mine\n"


def test_a_tampered_file_fails_verification(ledger: Path, tmp_path: Path) -> None:
    out = tmp_path / "b"
    write_bundle(
        out,
        build_tables(ledger),
        BuildContext(
            build_command="fedcourts export --out <dir>",
            package_version="0",
            all_versions=False,
            source=None,
            vintage=None,
        ),
    )
    (out / "predictions.csv").write_text("tampered\n")
    assert verify_bundle(out) == ["predictions.csv: checksum mismatch"]


def test_the_data_dictionary_lists_every_row_field() -> None:
    text = render_data_dictionary()
    for model in (ExportPredictionRow, ExportGradingRow, ExportReasoningRecord):
        for name, info in model.model_fields.items():
            assert f"| `{name}` |" in text, name
            assert info.description, f"{model.__name__}.{name} has no description"
    assert "CC BY 4.0" in text and "CourtListener" in text
    assert "within 0.01" in text and "## Reproducing the board" in text
    assert DATA_DICTIONARY == "DATA-DICTIONARY.md"


def test_the_frozen_scope_follows_the_process_version_constants(
    ledger: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Unbless the digest: nothing is frozen, so the release population is empty.
    bless_process(monkeypatch, "sha256:other", since=FREEZE)
    assert build_tables(ledger).predictions == []
    assert process_version.is_frozen(_stamp(datetime(2026, 2, 1, tzinfo=UTC))) is False
