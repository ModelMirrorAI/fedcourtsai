import copy
import hashlib
import json
import re
import shutil
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus
from fedcourtsai.cli import app
from fedcourtsai.collect import ExpectedCell, cell_artifact_name
from fedcourtsai.corpus_ranged import RangedBackendError
from fedcourtsai.finalize import FinalizeRole
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID
from fedcourtsai.registry import enabled_evaluators
from fedcourtsai.schemas import Disposition, Engine, EventKind, ModelUsage, Stage, UsageRole
from fedcourtsai.serialize import write_json
from tests.conftest import seed_evaluation, seed_prediction

runner = CliRunner()

_REPO_CONFIG = Path(__file__).resolve().parents[1] / "config"

#: Every declared merits moment, read off the register rather than spelled out,
#: so a moment added there is asserted on here without a test edit.
_MERITS_EVENT_IDS = [spec.event_id for spec in moments.moments_for(Stage.merits)]

_BATCH_BODY = """Long conference.

```json
[
  {"court": "scotus", "docket": 24001, "events": ["evt-petition-cert"]},
  {"court": "scotus", "docket": 24002, "events": ["evt-petition-cert"]}
]
```
"""


def _cells(stdout: str) -> list[dict[str, object]]:
    cells: list[dict[str, object]] = json.loads(stdout)["include"]
    return cells


def _env(
    tmp_path: Path,
    *,
    scope: str,
    cases: tuple[str, ...] = (),
    max_cells: int | None = None,
    seed_predictions: bool = True,
    spend_ceiling_usd: float | None = None,
) -> dict[str, str]:
    """A hermetic config + corpus for a matrix run.

    Copies the real registries so the fan-out dimensions are unchanged, writes a
    ``tracking.yaml`` pinning ``predict.scope`` (and, with ``max_cells``, the
    volume backstop; with ``spend_ceiling_usd``, the ex-post spend backstop, which
    is otherwise absent and therefore disabled), and seeds a corpus holding a row
    for each of the ``cases``
    ids (the gate reads each case's row: an absent row, or a non-SCOTUS court, is
    out of scope).

    ``seed_predictions`` commits one prediction per case's event: the evaluate
    gate needs it (nothing to score = no cell), but the *predict* per-predictor
    skip would then drop the seeded engine's cell, so predict fan-out/cap tests
    that assert full cell counts pass ``seed_predictions=False``.
    """
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    for name in ("predictors.yaml", "evaluators.yaml"):
        (config_root / name).write_text((_REPO_CONFIG / name).read_text())
    tracking = f"predict:\n  scope: {scope}\n"
    if max_cells is not None:
        tracking += f"  max_predict_cells_per_run: {max_cells}\n"
    if spend_ceiling_usd is not None:
        tracking += f"spend:\n  ceiling_usd: {spend_ceiling_usd}\n"
    (config_root / "tracking.yaml").write_text(tracking)

    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [
                # Distributed: the baseline's own moment precondition — an
                # undistributed SCOTUS petition forecasts at the arrival
                # moment, not the distribution moment these tests exercise.
                corpus.CorpusRow(case_id=cid, court=cid.split("/")[0], distribution_count=1)
                for cid in cases
            ],
        )
    # The evaluate gate reads the ledger: seed one committed prediction per
    # case's event so evaluate-matrix keeps them.
    data_root = tmp_path / "data"
    if seed_predictions:
        for cid in cases:
            court, _, docket = cid.partition("/")
            seed_prediction(data_root, court, int(docket), "evt-petition-cert")
    return {
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(data_root),
    }


def test_predict_matrix_batch_body_fans_out_across_cases(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
    )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    # 3 predictors x 2 cases x 1 event
    assert len(cells) == 6
    assert {(c["court"], c["docket"]) for c in cells} == {("scotus", 24001), ("scotus", 24002)}


def test_predict_matrix_skips_an_already_predicted_engine(tmp_path: Path) -> None:
    # The data_root wiring end-to-end: with a committed claude-baseline prediction
    # for the event, the CLI mints only the not-yet-predicted engines — the
    # 2/3-landed backfill re-queue at the cell grain.
    body = tmp_path / "issue-body.md"
    body.write_text(
        '```json\n{"court": "scotus", "docket": 24001, "events": ["evt-petition-cert"]}\n```\n'
    )
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))  # seeds claude-baseline
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {c["predictor_id"] for c in _cells(result.stdout)} == {
        "codex-baseline",
        "gemini-baseline",
    }


def test_predict_matrix_volume_cap_defers_overflow_and_surfaces_it(tmp_path: Path) -> None:
    # Four in-scope SCOTUS cases x 3 engines = 12 cells; a 6-cell backstop keeps
    # the two lowest-case_id cases whole and defers the rest — regardless of
    # salience — so a fail-open selection can never overflow the run.
    dockets = (24001, 24002, 24003, 24004)
    entries = ",\n".join(
        f'  {{"court": "scotus", "docket": {d}, "events": ["evt-petition-cert"]}}' for d in dockets
    )
    body = tmp_path / "issue-body.md"
    body.write_text(f"Long conference.\n\n```json\n[\n{entries}\n]\n```\n")
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=tuple(f"scotus/{d}" for d in dockets),
        max_cells=6,
        seed_predictions=False,
    )
    summary = tmp_path / "step-summary.md"
    env["GITHUB_STEP_SUMMARY"] = str(summary)

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    # Capped to 6 cells, and only whole cases — the two lowest dockets.
    assert len(cells) == 6
    assert {(c["court"], c["docket"]) for c in cells} == {("scotus", 24001), ("scotus", 24002)}
    # The deferral is surfaced loudly: a workflow annotation + a plain drop line.
    assert "::warning::" in result.stderr
    assert "deferred 6 cell(s)" in result.stderr
    # ...and appended to the plan job's step summary.
    assert "volume cap deferred 6 cell(s)" in summary.read_text()
    assert "scotus/24003" in summary.read_text()
    # Non-destructive: the deferred cases are untouched in the corpus, so a later
    # cycle re-queues them — the cap defers, it does not delete.
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        for d in dockets:
            assert corpus.get_row(conn, f"scotus/{d}") is not None


def test_predict_matrix_volume_cap_deferring_every_case_escalates_to_error(tmp_path: Path) -> None:
    # Pathological cap-empty: even the single lowest-case_id case (3 cells) exceeds
    # a 2-cell cap, so the matrix empties. The workflow's empty-matrix branch will
    # report a drained backlog, so the cap escalates to a correctly-attributed
    # ::error:: — the deferred cases stay owed and re-derive next cycle.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        max_cells=2,
        seed_predictions=False,
    )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert _cells(result.stdout) == []  # matrix empty: has_jobs=false downstream
    assert "::error::" in result.stderr
    assert "deferred ALL 2 case(s)" in result.stderr
    # Names the misreading it exists to correct: an empty matrix otherwise reads
    # as a drained backlog on the summary.
    assert "drained backlog" in result.stderr


def test_predict_matrix_under_the_cap_is_unchanged(tmp_path: Path) -> None:
    # A run inside the backstop fans out fully and surfaces no deferral warning.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        max_cells=240,
        seed_predictions=False,
    )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 6
    assert "volume cap" not in result.stderr


EVENT = "evt-petition-cert"
_PREDICTORS = ("claude-baseline", "codex-baseline", "gemini-baseline")
_SINGLE_BODY = f'```json\n{{"court": "scotus", "docket": 24001, "events": ["{EVENT}"]}}\n```\n'


def _stranded_census(tmp_path: Path, records: list[dict[str, object]]) -> Path:
    """Write the plan job's census file — what its API step hands the matrix."""
    path = tmp_path / "stranded-artifacts.json"
    path.write_text(json.dumps(records))
    return path


def _stranded_cell(run_db_id: int, predictor_id: str) -> dict[str, object]:
    """One census record for the shared single-case fixture's event.

    The artifact name is built by the production helper the cell workflows'
    upload step mirrors, so a change to the naming convention breaks this test
    rather than silently disarming the guard.
    """
    return {
        "run_db_id": run_db_id,
        "artifact_name": cell_artifact_name(
            FinalizeRole.predict,
            ExpectedCell(actor=predictor_id, court="scotus", docket=24001, event_id=EVENT),
        ),
    }


def test_predict_matrix_withholds_a_cell_stranded_in_an_uncollected_run(tmp_path: Path) -> None:
    # The guard at its grain: one predictor's artifact from an uncollected run
    # withholds that predictor's cell and no other. A cell the stranded run never
    # produced still runs, exactly as an engine-backfill re-queue does today.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = _stranded_census(tmp_path, [_stranded_cell(4242, "claude-baseline")])
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert {c["predictor_id"] for c in _cells(result.stdout)} == {
        "codex-baseline",
        "gemini-baseline",
    }
    # The note names the run and the recovery, never a re-queue.
    assert "::warning::" in result.stderr
    assert "uncollected run 4242" in result.stderr
    assert "gh run rerun 4242 --failed" in result.stderr


def test_predict_matrix_keeps_cells_no_stranded_artifact_matches(tmp_path: Path) -> None:
    # A census that names another case's cells changes nothing: the match is on
    # (predictor, case, event), so an unrelated stranded run is inert here.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = _stranded_census(
        tmp_path,
        [
            {
                "run_db_id": 4242,
                "artifact_name": cell_artifact_name(
                    FinalizeRole.predict,
                    ExpectedCell(
                        actor="claude-baseline", court="scotus", docket=24002, event_id=EVENT
                    ),
                ),
            }
        ],
    )
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 3
    assert "stranded" not in result.stderr


def test_predict_matrix_skips_an_unreadable_artifact_name_with_a_warning(tmp_path: Path) -> None:
    # A name that does not split into (predictor, court, docket, event) is
    # reported and ignored — a guessed split would withhold the wrong cell — and
    # the readable records in the same census still apply.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = _stranded_census(
        tmp_path,
        [
            {"run_db_id": 4242, "artifact_name": "predict-nonsense"},
            {"run_db_id": 4242, "artifact_name": "predict-claude-baseline-scotus-x-evt-petition"},
            {"artifact_name": "predict-codex-baseline-scotus-24001-evt-petition-cert"},
            _stranded_cell(4242, "claude-baseline"),
        ],
    )
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    # The unreadable records are skipped, so codex (named only by the record
    # missing its run id) still runs; the readable one still withholds claude.
    assert {c["predictor_id"] for c in _cells(result.stdout)} == {
        "codex-baseline",
        "gemini-baseline",
    }
    assert "does not read as a cell artifact" in result.stderr
    assert "'predict-nonsense'" in result.stderr


def test_predict_matrix_without_a_census_is_unguarded(tmp_path: Path) -> None:
    # Guard off in all three shapes the workflow can hand it: no flag, an absent
    # file (a census step that died before writing), and the empty list a
    # degraded census step writes. None of them may cost a cell.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    absent = tmp_path / "never-written.json"
    empty = _stranded_census(tmp_path, [])
    for args in ([], ["--stranded-file", str(absent)], ["--stranded-file", str(empty)]):
        result = runner.invoke(
            app,
            ["predict-matrix", "--run-id", "RID", "--body-file", str(body), *args],
            env=env,
        )
        assert result.exit_code == 0, args
        assert len(_cells(result.stdout)) == 3, args
        assert "stranded" not in result.stderr, args


def test_predict_matrix_malformed_census_records_are_skipped_not_fatal(tmp_path: Path) -> None:
    # The census is machine-written, so a shape it should never take means the
    # census step misbehaved — and the guard degrades rather than failing the
    # plan job, which would block a legitimate fan-out.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = tmp_path / "stranded-artifacts.json"
    # Not a list at the top level: a `jq -s` mishap emitting one object.
    census.write_text(json.dumps({"run_db_id": 4242, "artifact_name": "x"}))
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 3
    assert "stranded-run guard is off" in result.stderr

    # Records that are not objects, or whose name is not a string, are skipped
    # one by one while the readable ones still apply.
    census.write_text(
        json.dumps([[1, 2], "x", {"artifact_name": 5}, _stranded_cell(4242, "codex-baseline")])
    )
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert {c["predictor_id"] for c in _cells(result.stdout)} == {
        "claude-baseline",
        "gemini-baseline",
    }
    assert "does not read as a cell artifact" in result.stderr


def test_predict_matrix_guard_runs_before_the_volume_cap(tmp_path: Path) -> None:
    # Order is load-bearing: the cap's budget must go to genuinely new cells. Two
    # cases x 3 engines = 6 cells with a 3-cell cap. With the guard first, case
    # 24001's three stranded cells are withheld and 24002's three fit whole; run
    # the cap first and it would admit 24001 (lowest case_id) and defer 24002,
    # leaving a run that mints nothing but re-spends.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        max_cells=3,
        seed_predictions=False,
    )
    census = _stranded_census(tmp_path, [_stranded_cell(4242, pid) for pid in _PREDICTORS])
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    assert {(c["court"], c["docket"]) for c in cells} == {("scotus", 24002)}
    assert len(cells) == 3
    assert "volume cap" not in result.stderr, "the withheld cells never reached the cap"


def test_predict_matrix_unreadable_census_fails_open_with_a_warning(tmp_path: Path) -> None:
    # The guard prevents an expensive failure, not a dangerous one: a census the
    # plan cannot trust must never be why a legitimate run does not start.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = tmp_path / "stranded-artifacts.json"
    census.write_text("{not json")
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 3
    assert "::warning::" in result.stderr
    assert "stranded-run guard is off" in result.stderr


def test_predict_matrix_all_cells_stranded_signals_recovery_not_requeue(tmp_path: Path) -> None:
    # Every cell withheld: the matrix empties, so the workflow's has_jobs=false
    # path reports an empty round — and the guard's note must be there to say
    # recover the stranded run rather than start another one.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = _stranded_census(
        tmp_path,
        [_stranded_cell(4242, pid) for pid in ("claude-baseline", "codex-baseline")]
        + [_stranded_cell(4343, "gemini-baseline")],
    )
    note = tmp_path / "stranded-close.md"
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
            "--stranded-note-file",
            str(note),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "::error::" in result.stderr
    assert "withheld ALL 3 cell(s)" in result.stderr
    body_text = note.read_text()
    # Both stranded runs are named, each with its own recovery command.
    assert "gh run rerun 4242 --failed" in body_text
    assert "gh run rerun 4343 --failed" in body_text
    # The override is documented, not built: an explicit deletion, no new trigger.
    assert "gh api -X DELETE" in body_text
    assert "48-hour window" in body_text


def test_predict_matrix_writes_no_close_note_when_only_some_cells_are_stranded(
    tmp_path: Path,
) -> None:
    # The distinct close note belongs to the fully-superseded run only; a partly
    # stranded run still queues its new cells and its issue closes the usual way.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = _stranded_census(tmp_path, [_stranded_cell(4242, "claude-baseline")])
    note = tmp_path / "stranded-close.md"
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-file",
            str(census),
            "--stranded-note-file",
            str(note),
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 2
    assert not note.exists()
    assert "::error::" not in result.stderr


def test_predict_matrix_predictors_filter_survives_default_event_resolution(tmp_path: Path) -> None:
    # The engine-backfill path end-to-end: a body entry naming `predictors` but
    # no `events` must keep its narrowing through default open-event resolution
    # (which rebuilds the CaseRequest) — losing it would silently fan out the
    # full registry and duplicate the healthy engines' committed predictions.
    body = tmp_path / "issue-body.md"
    body.write_text(
        """Backfill.

```json
[{"court": "scotus", "docket": 24001, "predictors": ["codex-baseline"]}]
```
"""
    )
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent.model_validate(
                    {
                        "case_id": "scotus/24001",
                        "event_id": "evt-petition-cert",
                        "court": "scotus",
                        "kind": EventKind.petition,
                        "title": "Doe v. Roe",
                        "opened_at": date(2026, 6, 1),
                    }
                )
            ],
        )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    assert [(c["predictor_id"], c["event_id"]) for c in cells] == [
        ("codex-baseline", "evt-petition-cert")
    ]


def test_predict_matrix_legacy_single_case_flags_still_work(tmp_path: Path) -> None:
    # An in-scope SCOTUS docket still fans out via the single-case flags.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/123",))
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--court",
            "scotus",
            "--docket",
            "123",
            "--event",
            "evt-x",
        ],
        env=env,
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    assert len(cells) == 3
    assert {c["event_id"] for c in cells} == {"evt-x"}


def test_predict_matrix_drops_a_court_of_appeals_docket(tmp_path: Path) -> None:
    # The scope predicate is the row's court: a CoA docket — even one carrying a
    # stale eligible flag from the earlier, broader rule — is ingested for
    # context but never predicted.
    env = _env(tmp_path, scope="scotus_docket", cases=("ca9/123",))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="ca9/123", court="ca9", predict_eligible=True)],
        )
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-x",
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "not a SCOTUS docket" in result.stderr


def test_predict_matrix_drops_out_of_scope_case_with_note(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Only one of the two requested cases is eligible; the other is dropped.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    assert {(c["court"], c["docket"]) for c in cells} == {("scotus", 24001)}
    # The drop is explained on stderr so the maintainer understands the gap.
    assert "24002" in result.stderr
    assert "out of prediction scope" in result.stderr


def test_predict_matrix_drops_pre_1925_mandatory_jurisdiction_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Both requested cases are SCOTUS dockets, but 24002 carries a bare historical
    # docket number — a pre-1925 mandatory-jurisdiction matter — whose
    # disposition meaning the modern cert model does not fit, so it is dropped even
    # though its court is scotus.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/24002",
                    court="scotus",
                    docket_number="801",
                )
            ],
        )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24001)}
    # The drop is explained on stderr, distinct from the out-of-scope note.
    assert "24002" in result.stderr
    assert "mandatory-jurisdiction" in result.stderr


def test_predict_matrix_drops_stale_unresolvable_scotus_petition(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Both cases are SCOTUS dockets, but 24002 is an old-Term petition ("01-7700" ->
    # OT2001) the corpus never resolved (no disposition / decision date) — a stale,
    # unresolvable stub — so it is dropped even though its court is scotus.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/24002",
                    court="scotus",
                    docket_number="01-7700",
                )
            ],
        )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24001)}
    # The drop is explained on stderr, distinct from the out-of-scope and pre-1925 notes.
    assert "24002" in result.stderr
    assert "stale unresolvable" in result.stderr


def test_predict_matrix_drops_a_salience_unselected_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Both cases are in-scope SCOTUS cert dockets, but 24002 was scored by the
    # salience gate and NOT selected into the fundable slice, so the matrix defers
    # it. 24001 is unscored → fail-open → still predicted. Nothing is predicted
    # anywhere (`seed_predictions=False`): a deferred case with no cohort to
    # complete is the plain drop this test is about.
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/24002", court="scotus", docket_number="24-2")],
        )
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24001)}
    assert "24002" in result.stderr
    assert "not selected this salience round" in result.stderr
    assert "cohort-completion" not in result.stderr


def test_predict_matrix_keeps_a_deferred_case_narrowed_to_its_cohort_events(
    tmp_path: Path,
) -> None:
    """Cohort completion at the plan-time backstop: a deferred case keeps the
    listed events that already carry a prediction — the missing engines are the
    only spend left on them — while its unpredicted event, which would be a new
    cell on a case the funding gate declined, goes with the drop."""
    body = tmp_path / "issue-body.md"
    body.write_text(
        "```json\n"
        '[{"court": "scotus", "docket": 24002, '
        '"events": ["evt-petition-cert", "evt-petition-disposition"]}]\n'
        "```\n"
    )
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24002",), seed_predictions=False)
    # One engine landed on one of the two listed events, in the frozen process
    # partition: that is a cohort a claimable board counts.
    seed_prediction(
        tmp_path / "data",
        "scotus",
        24002,
        "evt-petition-cert",
        predictor_id="claude-baseline",
        frozen=True,
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    # Narrowed to the cohort event, and within it to the engines still missing:
    # two independent gates between a deferred case and any new cell.
    assert {(c["event_id"], c["predictor_id"]) for c in _cells(result.stdout)} == {
        ("evt-petition-cert", "codex-baseline"),
        ("evt-petition-cert", "gemini-baseline"),
    }
    assert "Kept 1 of 2 listed event(s) for cohort completion" in result.stderr


def test_predict_plan_names_the_events_the_cohort_narrowing_took_away(tmp_path: Path) -> None:
    """The narrowing's casualties are their own drop class. The case is KEPT, so
    it is in no case-drop list, and `requested` is the pre-gate listing — without
    a record of its own the plan (and the approval report a maintainer reads at
    the spend hold) would show a listed event simply gone."""
    body = tmp_path / "issue-body.md"
    body.write_text(
        "```json\n"
        '[{"court": "scotus", "docket": 24002, '
        '"events": ["evt-petition-cert", "evt-petition-disposition"]}]\n'
        "```\n"
    )
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24002",), seed_predictions=False)
    seed_prediction(
        tmp_path / "data",
        "scotus",
        24002,
        "evt-petition-cert",
        predictor_id="claude-baseline",
        frozen=True,
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert plan["counts"]["provenance"]["dropped_cohort_narrowed_events"] == 1
    assert plan["counts"]["provenance"]["dropped_out_of_scope_cases"] == 0
    (narrowed,) = plan["dropped_cohort_narrowed"]
    assert narrowed["case_id"] == "scotus/24002"
    assert narrowed["event_id"] == "evt-petition-disposition"
    # The reason names the ground that actually applied — here, no prediction at
    # all, so a cell would be new spend.
    assert "no committed prediction on this event" in narrowed["reason"]

    # And the approval report — the maintainer's surface at the spend hold —
    # carries the class rather than dropping it on the floor.
    report = tmp_path / "approval.md"
    runner.invoke(
        app,
        ["predict-plan", "--body-file", str(body), "--approval-report", str(report)],
        env=env,
    )
    assert "1 event(s) narrowed away on a salience-deferred case" in report.read_text()


def test_predict_plan_names_the_comparability_ground_when_that_is_what_refused(
    tmp_path: Path,
) -> None:
    """The two bounds refuse for opposite reasons, and the drop reason is what a
    maintainer reads in the approval report. An event whose cohort is merely
    *unfrozen* does hold committed predictions, so a reason saying it holds none
    would be false about the case it most needs to explain."""
    body = tmp_path / "issue-body.md"
    body.write_text(
        "```json\n"
        '[{"court": "scotus", "docket": 24002, '
        '"events": ["evt-petition-cert", "evt-petition-disposition"]}]\n'
        "```\n"
    )
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24002",), seed_predictions=False)
    # One event's cohort is frozen (keeps the case); the other's is real but
    # unstamped, so it is refused on comparability, not on absence.
    seed_prediction(
        tmp_path / "data",
        "scotus",
        24002,
        "evt-petition-cert",
        predictor_id="claude-baseline",
        frozen=True,
    )
    seed_prediction(
        tmp_path / "data",
        "scotus",
        24002,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    (narrowed,) = json.loads(result.stdout)["dropped_cohort_narrowed"]
    assert narrowed["event_id"] == "evt-petition-disposition"
    assert "outside the frozen process scope" in narrowed["reason"]
    assert "no committed prediction" not in narrowed["reason"]


def test_predict_matrix_drops_a_deferred_case_whose_cohort_no_board_counts(
    tmp_path: Path,
) -> None:
    """The comparability bound at the plan backstop, mirroring the sweep's. An
    unstamped cohort is outside the frozen partition the boards score in, so a
    freshly-stamped cell would not complete it — it would leave the board an
    event scored on one engine while its rivals are structurally excluded."""
    body = tmp_path / "issue-body.md"
    body.write_text(
        '```json\n{"court": "scotus", "docket": 24002, "events": ["evt-petition-cert"]}\n```\n'
    )
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24002",), seed_predictions=False)
    # A prediction exists, but unstamped — the pre-freeze shakedown shape.
    seed_prediction(
        tmp_path / "data", "scotus", 24002, "evt-petition-cert", predictor_id="claude-baseline"
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "not selected this salience round" in result.stderr
    assert "cohort completion" not in result.stderr


def test_predict_matrix_drops_a_deferred_case_whose_request_lists_no_events(
    tmp_path: Path,
) -> None:
    """The invariant standing between the carve-out and a full fan-out on a
    declined case: an unlisted request means 'resolve this case's defaults',
    which is a request for NEW cells, so a cohort cannot rescue it. This holds
    only because the scope gate runs before default-event resolution."""
    body = tmp_path / "issue-body.md"
    body.write_text('```json\n[{"court": "scotus", "docket": 24002}]\n```\n')
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24002",), seed_predictions=False)
    # A real, board-counted cohort exists on the case — it is the missing event
    # list, not a missing prediction, that refuses it.
    seed_prediction(
        tmp_path / "data",
        "scotus",
        24002,
        "evt-petition-cert",
        predictor_id="claude-baseline",
        frozen=True,
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "not selected this salience round" in result.stderr
    assert "cohort completion" not in result.stderr


def test_predict_matrix_keeps_an_unselected_case_with_an_open_merits_event(
    tmp_path: Path,
) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # The merits bypass at the matrix backstop: 24002 was scored and NOT selected,
    # but the Court granted it and its merits event is open — the cert funding
    # question no longer applies, so the gate must not drop it.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/24002",
                    court="scotus",
                    docket_number="24-2",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2026, 1, 12),
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-order-judgment",
                    case_id="scotus/24002",
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                )
            ],
        )
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {
        ("scotus", 24001),
        ("scotus", 24002),
    }
    assert "not selected this salience round" not in result.stderr


def test_predict_matrix_drops_bare_opinion_import_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Both cases are SCOTUS dockets, but 24002 is a bare bulk-import row (every
    # predicate-keyed field empty) whose snapshot links an opinion cluster — the
    # snapshot-aware exclusion — so the backstop drops it too.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/24002", court="scotus")],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/24002",
            date(2026, 7, 2),
            {"id": 24002, "clusters": ["https://example/clusters/88494/"]},
        )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24001)}
    assert "24002" in result.stderr
    assert "bare bulk-import" in result.stderr


def test_predict_matrix_drops_latched_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # A case the corpus reconcile latched out is dropped on the latch alone, even
    # when no live rule re-derives the exclusion at plan time.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/24002",
                    court="scotus",
                    docket_number="24-102",
                )
            ],
        )
        corpus.set_predict_excluded(conn, "scotus/24002", True)
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24001)}
    assert "24002" in result.stderr
    assert "latched out of predict scope" in result.stderr


def test_predict_matrix_scope_all_keeps_every_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Under `all` the corpus is never consulted: an empty corpus still fans out.
    env = _env(tmp_path, scope="all")
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {
        ("scotus", 24001),
        ("scotus", 24002),
    }


def test_predict_matrix_missing_corpus_fails_loudly(tmp_path: Path) -> None:
    # Regression: the scope gate reads each case's corpus row. If the
    # corpus DB was never provisioned (e.g. the planning job skipped the corpus pull),
    # an absent database must abort loudly — not silently drop every case and emit
    # an empty matrix, which reads as a normal "nothing in scope" result and skips
    # the predict job. The config exists; only the corpus DB is missing.
    config_root = tmp_path / "config"
    config_root.mkdir()
    for name in ("predictors.yaml", "evaluators.yaml"):
        (config_root / name).write_text((_REPO_CONFIG / name).read_text())
    (config_root / "tracking.yaml").write_text("predict:\n  scope: scotus_docket\n")
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = {
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),  # no DB on disk
    }
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code != 0
    assert "corpus database is missing" in result.stderr
    assert "include" not in result.stdout  # no matrix emitted


def test_predict_matrix_ranged_backend_does_not_require_a_local_db(tmp_path: Path) -> None:
    # Under the ranged backend the plan job reads the committed pointer in place,
    # so a missing local corpus.db must NOT trigger the local "corpus is missing"
    # abort — the gate routes through connect_readonly and (with no remote URL
    # configured here) fails with the ranged-backend error instead. This pins
    # that the backend is honored and the local-file precondition is scoped to
    # the local backend.
    config_root = tmp_path / "config"
    config_root.mkdir()
    for name in ("predictors.yaml", "evaluators.yaml"):
        (config_root / name).write_text((_REPO_CONFIG / name).read_text())
    (config_root / "tracking.yaml").write_text("predict:\n  scope: scotus_docket\n")
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = {
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),  # no DB on disk
        "FEDCOURTS_CORPUS_BACKEND": "ranged",  # and no remote URL set
    }
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code != 0
    # The ranged path was taken: a RangedBackendError (no pointer/URL here), not
    # the local "corpus database is missing" precondition.
    assert isinstance(result.exception, RangedBackendError)
    assert "corpus database is missing" not in result.stderr


def test_evaluate_matrix_batch_body_fans_out_across_cases(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    # 3 evaluators x 2 cases x 1 event
    assert len(_cells(result.stdout)) == 6


def test_evaluate_matrix_drops_out_of_scope_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24002",))
    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24002)}
    assert "24001" in result.stderr


def test_evaluate_matrix_grades_a_salience_unselected_case(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # 24002 is scored and NOT selected — the shape `unlatch-overselected`
    # creates for cases carrying committed predictions. Selection decides which
    # cases earn NEW cells, never whether an existing prediction is scored, so
    # the evaluate matrix must keep it: a cleared-then-resolved petition's
    # pre-registered forward prediction grades like any other.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        conn.execute(
            "UPDATE cases SET salience_version = 'sal-v1', salience_selected = 0 "
            "WHERE case_id = 'scotus/24002'"
        )
        conn.commit()
    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    # 3 evaluators x 2 cases: the unselected case's cells all mint.
    assert len(_cells(result.stdout)) == 6
    assert "not selected this salience round" not in result.stderr


def test_evaluate_matrix_reports_the_drop_count(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    # Remove one case's seeded prediction: its 3 evaluator cells drop, loudly.
    shutil.rmtree(tmp_path / "data" / "cases" / "scotus" / "24002")
    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 3
    assert "dropped 3 predictionless cell(s)" in result.output


def test_evaluate_matrix_reports_already_evaluated_separately(tmp_path: Path) -> None:
    """The two gates mean different things — one is a cost gate (nothing to
    score), the other an idempotency gate (already scored). Collapsed into one
    number, a fully-graded re-queue would read as a run with no predictions."""
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    seed_evaluation(tmp_path / "data", "scotus", 24001, "evt-petition-cert")

    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert "dropped 1 already-evaluated cell(s)" in result.output
    assert "predictionless" not in result.output
    # Only that one judge's cell is withheld; the rest of the fan-out is intact.
    minted = {(c["docket"], c["evaluator_id"]) for c in _cells(result.stdout)}
    assert (24001, "claude-judge") not in minted
    assert (24002, "claude-judge") in minted


def test_evaluate_matrix_force_restores_the_already_evaluated_cells(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    seed_evaluation(tmp_path / "data", "scotus", 24001, "evt-petition-cert")

    result = runner.invoke(
        app,
        ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body), "--force"],
        env=env,
    )
    assert result.exit_code == 0
    assert "already-evaluated" not in result.output
    assert (24001, "claude-judge") in {
        (c["docket"], c["evaluator_id"]) for c in _cells(result.stdout)
    }


def test_an_event_that_is_both_gaps_is_counted_once_as_predictionless(tmp_path: Path) -> None:
    """The overlap case. Counting it under both gates would double-report, and
    deriving one count by subtracting the other would print a negative."""
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    # 24002 has an evaluation but no prediction: nothing to score AND graded.
    seed_evaluation(tmp_path / "data", "scotus", 24002, "evt-petition-cert")
    shutil.rmtree(
        tmp_path
        / "data"
        / "cases"
        / "scotus"
        / "24002"
        / "events"
        / "evt-petition-cert"
        / "predictions"
    )

    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert "dropped 3 predictionless cell(s)" in result.output
    assert "already-evaluated" not in result.output, "attributed once, to the cost gate"


# --- the ex-post spend backstop -----------------------------------------------


def _spend_ledger(data_root: Path, *, cost: float) -> None:
    """Commit one predict `usage.json` dated now, so it lands inside any window."""
    now = datetime.now(tz=UTC)
    write_json(
        data_root
        / "cases/scotus/23999/events/evt-petition-cert/predictions"
        / "claude-baseline/RIDOLD/usage.json",
        ModelUsage(
            case_id="scotus/23999",
            event_id="evt-petition-cert",
            run_id="RIDOLD",
            role=UsageRole.predictor,
            actor_id="claude-baseline",
            engine=Engine.claude_code,
            model="claude-fable-5",
            created_at=now,
            input_tokens=1000,
            output_tokens=100,
            estimated_cost_usd=cost,
        ),
    )


def test_predict_matrix_mints_nothing_once_the_spend_ceiling_is_reached(tmp_path: Path) -> None:
    """A breach empties the matrix and says so loudly — the queued cases are
    untouched in the corpus and re-run next cycle."""
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
        spend_ceiling_usd=10.0,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=12.0)

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "::error::predict-matrix: spend backstop reached" in result.stderr
    assert "$12.00" in result.stderr and "$10.00" in result.stderr


def test_predict_matrix_under_the_spend_ceiling_is_unaffected(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
        spend_ceiling_usd=100.0,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=12.0)

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 6
    assert "spend backstop" not in result.stderr


def test_evaluate_matrix_mints_nothing_once_the_spend_ceiling_is_reached(tmp_path: Path) -> None:
    """The ceiling governs total inference spend, so it gates gradings too. An owed
    grading is never lost — the backlog deriver re-derives it from the ledger."""
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        spend_ceiling_usd=10.0,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=12.0)

    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "::error::evaluate-matrix: spend backstop reached" in result.stderr


def test_matrix_is_unaffected_when_no_spend_section_is_configured(tmp_path: Path) -> None:
    """The default is off: a large ledger with no `spend:` section changes nothing."""
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=10_000.0)

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 6


def test_predict_matrix_drops_events_resolved_since_queueing(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # The forecastability re-check: a case list composed while both events were
    # open fans out after one resolved (the review-hold gap). The resolved
    # listing is dropped at plan time, with the cause on the record, rather
    # than minted into a cell provisioning must refuse.
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-cert",
                    case_id="scotus/24002",
                    court="scotus",
                    kind=EventKind.petition,
                    resolved=True,
                )
            ],
        )

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {("scotus", 24001)}
    assert "dropped evt-petition-cert on scotus/24002" in result.stderr
    assert "resolved" in result.stderr


def test_predict_matrix_errors_when_the_forecastability_recheck_empties_the_matrix(
    tmp_path: Path,
) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # When every listed event resolved since listing the matrix is empty, and
    # the workflow's empty-matrix branch will report a drained backlog — so the
    # re-check must leave the correctly attributed record as an ::error::
    # annotation.
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
    )
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-cert",
                    case_id=cid,
                    court="scotus",
                    kind=EventKind.petition,
                    resolved=True,
                )
                for cid in ("scotus/24001", "scotus/24002")
            ],
        )

    note = tmp_path / "close-note.md"
    result = runner.invoke(
        app,
        [
            "predict-matrix",
            "--run-id",
            "RID",
            "--body-file",
            str(body),
            "--stranded-note-file",
            str(note),
        ],
        env=env,
    )

    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "::error::predict-matrix: the forecastability re-check dropped every listed event" in (
        result.stderr
    )
    # The durable half of the record: an attributed note for the round's own
    # report, naming each dropped event and its reason.
    text = note.read_text(encoding="utf-8")
    assert "unforecastable since it was listed" in text
    assert "`scotus/24001` `evt-petition-cert`" in text
    assert "resolved" in text


def test_predict_matrix_scope_all_skips_the_forecastability_recheck(tmp_path: Path) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Under `all` the scope gate never consults the corpus, and the
    # forecastability re-check follows it: a listed event the corpus records
    # resolved still fans out, because dev/back-test runs may target exactly
    # that shape. The bypass carries a residue the resolved class does not:
    # a stale or gvr-re-resolved grant minted under `all` provisions as a
    # *forward* cell with no later backstop, so `all` is a dev-only scope on
    # purpose (shipped config is scotus_docket).
    env = _env(tmp_path, scope="all", seed_predictions=False)
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-cert",
                    case_id="scotus/24001",
                    court="scotus",
                    kind=EventKind.petition,
                    resolved=True,
                )
            ],
        )

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert {(c["court"], c["docket"]) for c in _cells(result.stdout)} == {
        ("scotus", 24001),
        ("scotus", 24002),
    }
    assert "dropped" not in result.stderr


def _listing_body(path: Path, events: list[str], *, docket: int = 24001) -> Path:
    """A one-case trigger body **listing** its events — the replay shape.

    A listing skips queue selection entirely, which is what the forecastability
    re-check exists to cover.
    """
    listing = json.dumps([{"court": "scotus", "docket": docket, "events": events}])
    path.write_text(f"Queued.\n\n```json\n{listing}\n```\n")
    return path


def _granted_row(corpus_root: Path, case_id: str, granted: date) -> None:
    """Overwrite ``case_id``'s row with a cert grant that opened a merits proceeding."""
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="24-100",
                    disposition=Disposition.granted,
                    date_cert_granted=granted,
                    distribution_count=1,
                )
            ],
        )


def test_predict_matrix_drops_listed_merits_events_on_a_stale_grant(tmp_path: Path) -> None:
    # The replay hole the re-check closes: re-running an old case list
    # replays its event listing, which skips the selection-time stale-grant
    # refusal. Every declared merits moment goes — the staleness is a property
    # of the proceeding — while the case's cert event, which the rule says
    # nothing about, stays listed.
    body = _listing_body(tmp_path / "issue-body.md", [*_MERITS_EVENT_IDS, "evt-petition-cert"])
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    _granted_row(tmp_path / "corpus", "scotus/24001", date(2020, 1, 6))

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert {c["event_id"] for c in _cells(result.stdout)} == {"evt-petition-cert"}
    for event_id in _MERITS_EVENT_IDS:
        assert f"dropped {event_id} on scotus/24001" in result.stderr
    assert "cert grant is more than 730 days old" in result.stderr


def test_predict_matrix_keeps_listed_merits_events_on_a_fresh_grant(tmp_path: Path) -> None:
    # The other side of the bound: a grant inside the merits window is a
    # pending proceeding, and its listed merits event mints its cells.
    body = _listing_body(tmp_path / "issue-body.md", [MERITS_EVENT_ID])
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    _granted_row(tmp_path / "corpus", "scotus/24001", date.today() - timedelta(days=30))

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert {c["event_id"] for c in _cells(result.stdout)} == {MERITS_EVENT_ID}
    assert "dropped" not in result.stderr


def test_predict_matrix_scope_all_keeps_a_stale_grants_merits_event(tmp_path: Path) -> None:
    # Under `all` the corpus is deliberately never consulted, so the stale-grant
    # class rides the same bypass as the resolved one: back-testing targets
    # exactly this shape.
    body = _listing_body(tmp_path / "issue-body.md", [MERITS_EVENT_ID])
    env = _env(tmp_path, scope="all", seed_predictions=False)
    _granted_row(tmp_path / "corpus", "scotus/24001", date(2020, 1, 6))

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert {c["event_id"] for c in _cells(result.stdout)} == {MERITS_EVENT_ID}
    assert "dropped" not in result.stderr


def test_predict_matrix_errors_when_the_stale_grant_drop_empties_the_matrix(
    tmp_path: Path,
) -> None:
    # An emptied matrix reads on the workflow's summary as a drained backlog,
    # so the re-check must leave the attributed record — reason-agnostic, since
    # the per-event warnings carry which class each was.
    body = _listing_body(tmp_path / "issue-body.md", [MERITS_EVENT_ID])
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    _granted_row(tmp_path / "corpus", "scotus/24001", date(2020, 1, 6))

    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert _cells(result.stdout) == []
    assert "::error::predict-matrix: the forecastability re-check dropped every listed event" in (
        result.stderr
    )


# The plan-only dry runs. `predict-plan` / `evaluate-plan` report what their
# matrix counterparts would mint without minting it, so the parity tests below
# are the contract: a plan that describes a different fan-out than the command
# performs is worse than no plan at all.


def _plan(stdout: str) -> dict[str, Any]:
    plan: dict[str, Any] = json.loads(stdout)
    return plan


def _files(root: Path) -> set[Path]:
    """Every file under ``root`` — the snapshot a "writes nothing" claim needs."""
    return {p for p in root.rglob("*") if p.is_file()}


def _assert_predict_balances(plan: dict[str, Any]) -> None:
    """The opening balance reconciles: every candidate cell is minted or accounted for."""
    c = plan["counts"]["cell_ledger"]
    assert (
        c["candidate_cells"]
        - c["dropped_by_request_narrowing_cells"]
        - c["dropped_already_predicted_cells"]
        - c["withheld_stranded_cells"]
        - c["deferred_by_cap_cells"]
        == c["would_mint_cells"]
    )


def _assert_evaluate_balances(plan: dict[str, Any]) -> None:
    """The same reconciliation across evaluate's two gates."""
    c = plan["counts"]["cell_ledger"]
    assert (
        c["candidate_cells"]
        - c["dropped_predictionless_cells"]
        - c["dropped_already_evaluated_cells"]
        == c["would_mint_cells"]
    )


def test_predict_plan_enumerates_exactly_the_cells_predict_matrix_would_mint(
    tmp_path: Path,
) -> None:
    # Parity is the whole point: the plan runs the same pipeline, so its
    # would-mint set is the matrix command's cell set, field for field.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    # Seeded predictions leave the per-predictor ledger gate something to
    # report, so the drop lists are exercised rather than trivially empty.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))

    minted = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    planned = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert minted.exit_code == 0
    assert planned.exit_code == 0
    plan = _plan(planned.stdout)
    assert plan["would_mint"] == [
        {
            "predictor_id": cell["predictor_id"],
            "court": cell["court"],
            "docket": cell["docket"],
            "event_id": cell["event_id"],
            "engine": cell["engine"],
            "model": cell["model"],
        }
        for cell in _cells(minted.stdout)
    ]
    # 3 predictors x 2 cases x 1 event, less the seeded claude-baseline cell on each.
    ledger = plan["counts"]["cell_ledger"]
    assert ledger["candidate_cells"] == 6
    assert ledger["would_mint_cells"] == 4
    assert ledger["would_mint_cells_after_spend_gate"] == 4
    assert ledger["dropped_already_predicted_cells"] == 2
    assert {d["actor_id"] for d in plan["dropped_already_predicted"]} == {"claude-baseline"}
    _assert_predict_balances(plan)
    # The rates are pinned in code against docs/budget.md; a silent re-anchor
    # re-prices every plan, so the literals are asserted rather than derived.
    assert plan["spend_estimate_basis"]["rates_usd_per_cell"] == {
        "claude-code": 4.27,
        "codex": 1.88,
        "gemini": 0.64,
    }
    # The fallback rate lives inside the basis block, named as the fallback it
    # is — never at the top level, where a consumer multiplying it by
    # `would_mint_cells` would rebuild the flat-rate error the table removes.
    assert "planning_rate_usd_per_cell" not in plan
    assert plan["spend_estimate_basis"]["fallback_usd_per_cell"] == 2.50
    # The surviving cells are codex + gemini on both cases, priced per engine.
    assert plan["estimated_spend_usd"] == round(2 * (1.88 + 0.64), 2)
    assert plan["estimated_spend_caveat"] is None
    assert plan["spend_estimate_basis"]["cells_at_fallback_rate"] == 0
    # The guard ran against no census at all — distinct from a clean run.
    assert plan["stranded_guard"] == {
        "active": False,
        "degraded_reason": None,
        "unparsed_records": [],
    }
    # No ceiling configured: the backstop never read the ledger, so its figures
    # are unmeasured rather than measured-zero.
    assert plan["spend_gate"]["enforced"] is False
    assert plan["spend_gate"]["spent_usd"] is None
    assert plan["spend_gate"]["ceiling_usd"] is None
    assert plan["spend_gate"]["cells"] is None
    # A floor claim about a null is not a weaker claim, it is not a claim.
    assert plan["spend_gate"]["spent_usd_is_floor"] is None


def test_predict_plan_names_the_step_that_dropped_a_stale_grant(tmp_path: Path) -> None:
    # The stale-listing regression, read off the plan: re-labelling an old
    # trigger replays an event listing that skips selection, and the plan must
    # attribute each dropped merits moment to the forecastability re-check with
    # that step's own reason — not merely show a smaller cell set.
    body = _listing_body(tmp_path / "issue-body.md", [*_MERITS_EVENT_IDS, "evt-petition-cert"])
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    _granted_row(tmp_path / "corpus", "scotus/24001", date(2020, 1, 6))

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    assert plan["counts"]["provenance"]["dropped_unforecastable_events"] == len(_MERITS_EVENT_IDS)
    _assert_predict_balances(plan)
    dropped = plan["dropped_unforecastable"]
    assert {d["event_id"] for d in dropped} == set(_MERITS_EVENT_IDS)
    assert {d["case_id"] for d in dropped} == {"scotus/24001"}
    assert all("cert grant is more than 730 days old" in d["reason"] for d in dropped)
    # The cert event the rule says nothing about survives and is priced.
    assert {c["event_id"] for c in plan["would_mint"]} == {"evt-petition-cert"}


def test_evaluate_plan_enumerates_exactly_the_cells_evaluate_matrix_would_mint(
    tmp_path: Path,
) -> None:
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    # One case loses its seeded prediction, so the cost gate has cells to name.
    shutil.rmtree(tmp_path / "data" / "cases" / "scotus" / "24002")

    minted = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    planned = runner.invoke(app, ["evaluate-plan", "--body-file", str(body)], env=env)

    assert minted.exit_code == 0
    assert planned.exit_code == 0
    plan = _plan(planned.stdout)
    assert plan["would_mint"] == [
        {
            "evaluator_id": cell["evaluator_id"],
            "court": cell["court"],
            "docket": cell["docket"],
            "event_id": cell["event_id"],
            "engine": cell["engine"],
            "model": cell["model"],
        }
        for cell in _cells(minted.stdout)
    ]
    ledger = plan["counts"]["cell_ledger"]
    assert ledger["candidate_cells"] == 6
    assert ledger["would_mint_cells"] == 3
    assert ledger["dropped_predictionless_cells"] == 3
    _assert_evaluate_balances(plan)
    assert {d["case_id"] for d in plan["dropped_predictionless"]} == {"scotus/24002"}
    assert all("no committed prediction" in d["reason"] for d in plan["dropped_predictionless"])
    # The evaluate seam prices off its own rates, and says they are an
    # assumption rather than a measurement.
    assert plan["spend_estimate_basis"]["rates_usd_per_cell"] == {
        "claude-code": 5.92,
        "codex": 1.30,
        "gemini": 0.96,
    }
    assert plan["estimated_spend_usd"] == round(5.92 + 1.30 + 0.96, 2)
    caveats = plan["spend_estimate_basis"]["caveats"]
    assert any("ASSUMPTION, not a measurement" in c for c in caveats)
    # An assumption is the right basis for a reason that keeps changing, so the
    # caveat carries the reason and not just the label: a stamped evaluate
    # measurement exists, and what disqualifies it from re-anchoring these
    # rates is its stage and its superseded digests. Pinned because the failure
    # mode is silent — a caveat that goes stale against docs/budget.md still
    # renders, and the approval report quotes it as the basis of a spend
    # decision.
    assert any(
        "evaluate measurement EXISTS outside the frozen partition" in c
        and "INTERIM" in c
        and "since-superseded evaluator" in c
        and "cert stage" in c
        for c in caveats
    )


def test_predict_plan_writes_nothing_where_the_matrix_command_writes(tmp_path: Path) -> None:
    # A plan reports; it never mints, and it never leaves a trace. The
    # all-withheld stranded path is where `predict-matrix` makes both of its
    # writes — the recovery note and the Actions step-summary block —
    # so it is where "writes nothing" is worth asserting.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = _stranded_census(tmp_path, [_stranded_cell(4242, pid) for pid in _PREDICTORS])
    summary = tmp_path / "step-summary.md"
    summary.write_text("")
    before = _files(tmp_path)

    result = runner.invoke(
        app,
        ["predict-plan", "--body-file", str(body), "--stranded-file", str(census)],
        env={**env, "GITHUB_STEP_SUMMARY": str(summary)},
    )

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    assert plan["counts"]["cell_ledger"]["withheld_stranded_cells"] == 3
    assert plan["would_mint"] == []
    assert {c["run_db_id"] for c in plan["withheld_stranded"]} == {4242}
    assert plan["estimated_spend_usd"] == 0.0
    # The guard ran and matched — the state a bare `withheld == 0` cannot show.
    assert plan["stranded_guard"]["active"] is True
    assert plan["stranded_guard"]["degraded_reason"] is None
    _assert_predict_balances(plan)
    # `predict-plan` takes no --stranded-note-file, so no note can exist, and the
    # step summary the matrix command would have appended to stays empty.
    assert summary.read_text() == ""
    assert _files(tmp_path) == before


def test_predict_plan_names_a_guard_that_failed_open(tmp_path: Path) -> None:
    # The guard fails open on an unreadable census, which is the one state a
    # `withheld_stranded_cells: 0` must not be read as "nothing was stranded":
    # the cells it could not check may re-spend. A plan run emits no annotation
    # at all, so the JSON is the only place that distinction can live.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = tmp_path / "stranded-artifacts.json"
    census.write_text('{"not": "a list"}')

    result = runner.invoke(
        app,
        ["predict-plan", "--body-file", str(body), "--stranded-file", str(census)],
        env=env,
    )

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    guard = plan["stranded_guard"]
    assert guard["active"] is False
    assert guard["degraded_reason"] is not None
    assert "unreadable" in guard["degraded_reason"]
    # Fail-open: the cells still plan, exactly as the matrix command mints them.
    assert plan["counts"]["cell_ledger"]["would_mint_cells"] == 3
    assert plan["counts"]["cell_ledger"]["withheld_stranded_cells"] == 0
    _assert_predict_balances(plan)
    # Suppress-all: a plan run leaves no workflow-command annotation behind.
    assert "::warning::" not in result.stderr
    assert "::error::" not in result.stderr


def test_predict_plan_reports_a_spend_breach_without_emptying_the_cell_set(
    tmp_path: Path,
) -> None:
    # The deliberate asymmetry with `predict-matrix`: a breach empties the
    # matrix there, and here it is reported beside the fan-out the earlier steps
    # decided — a plan describes the pipeline rather than standing in for it.
    # Both halves must be legible, so the closing stderr line carries the breach
    # rather than contradicting the warning above it.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
        spend_ceiling_usd=10.0,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=12.0)

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    assert plan["spend_gate"]["breached"] is True
    assert plan["spend_gate"]["enforced"] is True
    ledger = plan["counts"]["cell_ledger"]
    assert ledger["would_mint_cells"] == 6
    assert len(plan["would_mint"]) == 6
    # The breach is legible on stdout, not only on stderr: a machine reader that
    # takes `would_mint` must be able to see it would not actually be minted.
    assert ledger["would_mint_cells_after_spend_gate"] == 0
    assert plan["spend_gate"]["would_empty_matrix"] is True
    assert plan["estimated_spend_caveat"] is not None
    assert "would mint 0 cells" in plan["estimated_spend_caveat"]
    # An enforced ceiling means the ledger WAS read, so the figures are real.
    assert plan["spend_gate"]["spent_usd"] == 12.0
    assert plan["spend_gate"]["ceiling_usd"] == 10.0
    assert plan["spend_gate"]["cells"] == 1
    assert plan["spend_gate"]["spent_usd_is_floor"] is True
    _assert_predict_balances(plan)
    assert "the ex-post spend backstop is breached" in result.stderr
    assert "so a real run mints 0." in result.stderr


def test_evaluate_plan_reports_already_graded_cells_and_what_force_would_change(
    tmp_path: Path,
) -> None:
    # The idempotency gate at plan grain, and the flag that lifts it: without
    # `--force` a graded event's judge is named as dropped; with it the same
    # request plans the re-grade.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    seed_evaluation(Path(env["FEDCOURTS_DATA_ROOT"]), "scotus", 24001, EVENT)

    planned = runner.invoke(app, ["evaluate-plan", "--body-file", str(body)], env=env)
    forced = runner.invoke(app, ["evaluate-plan", "--body-file", str(body), "--force"], env=env)

    assert planned.exit_code == 0
    assert forced.exit_code == 0
    plan = _plan(planned.stdout)
    assert plan["counts"]["cell_ledger"]["dropped_already_evaluated_cells"] == 1
    assert [d["actor_id"] for d in plan["dropped_already_evaluated"]] == ["claude-judge"]
    assert plan["dropped_already_evaluated"][0]["case_id"] == "scotus/24001"
    assert plan["counts"]["cell_ledger"]["would_mint_cells"] == 5
    _assert_evaluate_balances(plan)

    forced_plan = _plan(forced.stdout)
    assert forced_plan["dropped_already_evaluated"] == []
    assert forced_plan["counts"]["cell_ledger"]["would_mint_cells"] == 6
    _assert_evaluate_balances(forced_plan)


def test_the_planning_rate_table_matches_the_budget_doc_per_event_totals() -> None:
    """The rate table is a transcription of `docs/budget.md`, so pin its totals.

    Predict: the whole-run row of *Per-cell cost is keyed on the stage* sums to
    **$6.79 an event**. Evaluate: that section's `proc-v2` row scaled by the
    predict move sums to **$8.18**, the upper anchor of the doc's $14.6-15.0
    per-case band. Pinning the sums rather than only the columns means a
    re-anchor of the doc lands here as a visible test edit instead of silently
    re-pricing every plan.
    """
    assert round(sum(cli._PLANNING_RATES_USD_PER_CELL["predict"].values()), 2) == 6.79
    assert round(sum(cli._PLANNING_RATES_USD_PER_CELL["evaluate"].values()), 2) == 8.18
    # And the pair is the $14.97 the six-cell $2.50 fallback is the rounding of.
    assert round(6.79 + 8.18, 2) == 14.97


def test_predict_plan_prices_an_unknown_engine_at_the_stated_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A registry entry ahead of the rate table must not vanish from the total.
    # Standing in for that: a table with gemini removed, which is the same code
    # path a genuinely new engine takes.
    monkeypatch.setitem(
        cli._PLANNING_RATES_USD_PER_CELL,
        "predict",
        {"claude-code": 4.27, "codex": 1.88},
    )
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    basis = plan["spend_estimate_basis"]
    # One of the three cells ran the unnamed engine and is counted as such.
    assert plan["counts"]["cell_ledger"]["would_mint_cells"] == 3
    assert basis["cells_at_fallback_rate"] == 1
    # Priced in, not dropped: the total carries it at the fallback rate.
    assert plan["estimated_spend_usd"] == round(4.27 + 1.88 + 2.50, 2)
    assert any("design-mix fallback" in c for c in basis["caveats"])


def test_predict_plan_names_a_case_whose_default_events_resolved_empty(
    tmp_path: Path,
) -> None:
    # The quiet class: a case that listed no events and whose corpus lookup came
    # back empty stays in the case count and contributes to neither the event
    # count nor the cell count, so it is invisible unless it is named.
    body = tmp_path / "issue-body.md"
    body.write_text('```json\n{"court": "scotus", "docket": 24001}\n```\n')
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    provenance = plan["counts"]["provenance"]
    assert provenance["resolved_cases"] == 1
    assert provenance["resolved_events"] == 0
    assert provenance["cases_with_no_default_events"] == 1
    assert plan["cases_with_no_default_events"][0]["case_id"] == "scotus/24001"
    assert "resolved none" in plan["cases_with_no_default_events"][0]["reason"]
    assert plan["counts"]["cell_ledger"]["candidate_cells"] == 0
    _assert_predict_balances(plan)


def test_predict_plan_names_the_census_records_the_guard_could_not_read(
    tmp_path: Path,
) -> None:
    # Partly blind is its own state: the guard ran, so `active` is true and no
    # fail-open reason is set, but records it could not parse mean the withheld
    # count is silent about whatever they named.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = tmp_path / "stranded-artifacts.json"
    census.write_text(
        json.dumps([[1, 2], "x", {"artifact_name": 5}, _stranded_cell(4242, "codex-baseline")])
    )

    result = runner.invoke(
        app,
        ["predict-plan", "--body-file", str(body), "--stranded-file", str(census)],
        env=env,
    )

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    guard = plan["stranded_guard"]
    assert guard["active"] is True
    assert guard["degraded_reason"] is None
    assert len(guard["unparsed_records"]) == 3
    # The one record it could read still withheld its cell.
    assert plan["counts"]["cell_ledger"]["withheld_stranded_cells"] == 1
    _assert_predict_balances(plan)


def test_evaluate_plan_reports_a_spend_breach_without_emptying_the_cell_set(
    tmp_path: Path,
) -> None:
    # The breach trio is not predict-only: an evaluate plan under a breached
    # ceiling has to be just as legible on stdout, and its stderr line has to
    # keep the assumption clause beside the number.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        spend_ceiling_usd=10.0,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=12.0)

    result = runner.invoke(app, ["evaluate-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    ledger = plan["counts"]["cell_ledger"]
    assert plan["spend_gate"]["breached"] is True
    assert plan["spend_gate"]["would_empty_matrix"] is True
    assert ledger["would_mint_cells"] == 6
    assert ledger["would_mint_cells_after_spend_gate"] == 0
    assert plan["estimated_spend_caveat"] is not None
    _assert_evaluate_balances(plan)
    # The evaluate seam prices an assumption, and the line a reader quotes says so.
    assert "are an assumption" in result.stderr
    assert "not a measurement" in result.stderr


def test_predict_plan_prices_an_engine_narrowed_backfill_at_that_engine_rate(
    tmp_path: Path,
) -> None:
    # The reason the estimate is conditioned on the engine at all: a backfill
    # body naming one engine is the common narrowed shape, and the engines
    # differ ~7x within the predict seam. Priced at the flat design-mix rate
    # this run would read $5.00; at gemini's own measured rate it is $1.28.
    narrowed = json.dumps(
        [
            {
                "court": "scotus",
                "docket": docket,
                "events": [EVENT],
                "predictors": ["gemini-baseline"],
            }
            for docket in (24001, 24002)
        ]
    )
    body = tmp_path / "issue-body.md"
    body.write_text(f"Backfill.\n\n```json\n{narrowed}\n```\n")
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
    )

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    ledger = plan["counts"]["cell_ledger"]
    # The request's own narrowing is its own drop class, held apart from the
    # ledger gate: collapsed, a narrowed backfill reads as an already-complete
    # event.
    assert ledger["candidate_cells"] == 6
    assert ledger["dropped_by_request_narrowing_cells"] == 4
    assert ledger["dropped_already_predicted_cells"] == 0
    assert ledger["would_mint_cells"] == 2
    _assert_predict_balances(plan)
    assert {d["actor_id"] for d in plan["dropped_by_request_narrowing"]} == {
        "claude-baseline",
        "codex-baseline",
    }
    assert all("gemini-baseline" in d["reason"] for d in plan["dropped_by_request_narrowing"])
    # The whole point: the estimate is not cells x the flat rate.
    assert plan["estimated_spend_usd"] == round(2 * 0.64, 2)
    fallback = plan["spend_estimate_basis"]["fallback_usd_per_cell"]
    assert plan["estimated_spend_usd"] != round(2 * fallback, 2)


def test_predict_plan_balances_when_the_volume_cap_defers_a_case(tmp_path: Path) -> None:
    # The cap is the one drop class that removes cells after the guard, so the
    # opening balance has to survive it: 2 cases x 3 engines under a 3-cell cap
    # keeps the lowest case_id whole and defers the other.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        max_cells=3,
        seed_predictions=False,
    )

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)

    assert result.exit_code == 0
    plan = _plan(result.stdout)
    ledger = plan["counts"]["cell_ledger"]
    assert ledger["candidate_cells"] == 6
    assert ledger["deferred_by_cap_cells"] == 3
    assert ledger["would_mint_cells"] == 3
    _assert_predict_balances(plan)
    assert plan["deferred_by_cap"]["cases"] == ["scotus/24002"]
    assert plan["deferred_by_cap"]["max_cells"] == 3
    assert {(c["court"], c["docket"]) for c in plan["would_mint"]} == {("scotus", 24001)}
    # A capped plan prices this run only, and says so on both channels.
    assert any("Covers THIS run only" in c for c in plan["spend_estimate_basis"]["caveats"])
    assert "deferred by the volume cap re-queue" in result.stderr


# The approval report. A hold gate publishes it for a maintainer to approve or
# reject the fan-out from, so it is rendered by the tested command rather than
# assembled in the workflow's shell — and it is bounded, because GitHub refuses
# an over-long comment with a 422 rather than truncating it, and a 422 is not
# transient.

#: GitHub's issue-comment ceiling. The report's own cap sits under it.
_COMMENT_LIMIT = 65_536


def _report(tmp_path: Path, args: list[str], env: dict[str, str]) -> tuple[str, str]:
    """Invoke a plan command with ``--approval-report`` and return (report, stdout)."""
    out = tmp_path / "approval-report.md"
    result = runner.invoke(app, [*args, "--approval-report", str(out)], env=env)
    assert result.exit_code == 0, result.stderr
    return out.read_text(), result.stdout


def _widened(plan: dict[str, Any], cells: int) -> dict[str, Any]:
    """A real plan re-pointed at ``cells`` would-mint cells, one per docket.

    The renderer is a pure function of the plan document, so widening a plan the
    command actually produced exercises the size bound on real field shapes
    without standing up a 200-cell corpus.
    """
    wide = copy.deepcopy(plan)
    template = wide["would_mint"][0]
    wide["would_mint"] = [{**template, "docket": 30000 + n} for n in range(cells)]
    wide["counts"]["cell_ledger"]["would_mint_cells"] = cells
    return wide


def test_the_approval_report_carries_the_counts_the_table_and_the_spend_caveats(
    tmp_path: Path,
) -> None:
    # The decision surface: a maintainer approves a fan-out from this comment,
    # so it has to carry both count grains, the cells themselves, and the spend
    # sentence with its basis in the same sentence as the number.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))

    report, stdout = _report(
        tmp_path,
        ["predict-plan", "--body-file", str(body), "--approval-report-run-url", "https://run/9"],
        env,
    )

    plan = _plan(stdout)
    assert "predict-plan: 4 cell(s) held for approval" in report
    # Both grains, verbatim from the same helper the stderr summary prints, so
    # the comment and the log cannot disagree about what the plan counted.
    assert "predict-plan provenance: requested_cases=2" in report
    assert "predict-plan cell ledger: candidate_cells=6" in report
    # The spend sentence, with the basis inside it rather than a paragraph away.
    assert f"estimated ${plan['estimated_spend_usd']:.2f} at the per-engine rates" in report
    assert "Nothing was spent and nothing was written." in report
    # Every would-mint cell, one row each, naming the engine the price is keyed on.
    for cell in plan["would_mint"]:
        assert f"| `{cell['predictor_id']}` | `scotus/{cell['docket']}` " in report
    assert "| `evt-petition-cert` | `codex` |" in report
    assert "… and" not in report
    # The drop class that actually took cells, as a count and no more — the
    # per-record reasons stay in the JSON the comment points at. The label opens
    # with its own grain: the classes do not share one, and under a section a
    # reader arrives at counting cells an ungrained count is read as cells.
    assert "- 2 cell(s) dropped as already predicted by that predictor" in report
    assert "Each drop's per-record reason is in the plan JSON." in report
    # The line the workflow parameterizes, and the only GitHub specific here.
    assert "Approve or reject the `review` deployment on the run: https://run/9" in report


def test_the_approval_report_omits_the_approval_line_without_a_run_url(tmp_path: Path) -> None:
    # The closing line points at a deployment gate; with no URL there is nothing
    # to point at, and a dangling "approve on the run:" would name no run.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)

    report, _ = _report(tmp_path, ["predict-plan", "--body-file", str(body)], env)

    assert "Approve or reject" not in report
    assert "predict-plan: 3 cell(s) held for approval" in report
    # Nothing was dropped, and the section says so rather than going silent —
    # an absent section reads as a section that was not rendered.
    assert "- Nothing was dropped: every candidate cell would be minted." in report


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # The ordinary case: no escaping, no widened fence.
        ("claude-baseline", "`claude-baseline`"),
        # A pipe splits the row into an extra column even inside a code span,
        # because GFM resolves cell boundaries before inline code.
        ("pipe|baseline", r"`pipe\|baseline`"),
        # A backtick would close the span early and let the rest of the value
        # render as markdown into a public issue comment, so the fence widens
        # past the longest run inside the value.
        ("tick`baseline", "``tick`baseline``"),
        ("two``ticks", "```two``ticks```"),
        # Padding where the value's own backtick would otherwise touch the
        # fence; the renderer strips the padding again, so the value survives.
        ("`leading", "`` `leading ``"),
        ("trailing`", "`` trailing` ``"),
        # Both characters at once — neither escape may undo the other.
        ("a|b`c", "``a\\|b`c``"),
    ],
)
def test_a_table_cell_cannot_break_out_of_its_span(value: str, expected: str) -> None:
    # The report is posted as a public issue comment, so a value that escaped
    # its cell would render as markdown in it. Ids are corpus- and
    # registry-derived, which makes this containment rather than a live threat —
    # but the property has to hold by construction, not by what ids happen to
    # contain today.
    assert cli._md_cell(value) == expected


def test_the_approval_report_truncates_the_cell_table_at_its_row_cap(tmp_path: Path) -> None:
    # Past the cap the surviving count carries the fan-out better than another
    # 160 rows would, and the dropped rows are named rather than silently cut.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _, stdout = _report(tmp_path, ["predict-plan", "--body-file", str(body)], env)

    report = cli._render_approval_report(_widened(_plan(stdout), 200), stage="predict-plan")

    rows = [line for line in report.splitlines() if line.startswith("| `")]
    assert len(rows) == cli._APPROVAL_REPORT_MAX_ROWS == 40
    assert "… and 160 more cells. Rows are ordered by case, then actor" in report
    # The kept rows are a contiguous range of the lowest case ids, which is what
    # makes a truncated table readable: the reader knows the rest lie past them,
    # rather than seeing every case's first engine with the others cut.
    dockets = [int(row.split("`")[3].split("/")[1]) for row in rows]
    assert dockets == sorted(dockets) == list(range(30000, 30040))
    # The header count is the whole fan-out, not the rows that fit: a reader who
    # took 40 for the run size would approve four times the cells they read.
    assert "predict-plan: 200 cell(s) held for approval" in report


def test_the_approval_report_stays_under_the_comment_ceiling_on_a_wide_plan(
    tmp_path: Path,
) -> None:
    # The bound the whole design exists for. A full-width run's pretty-printed
    # JSON approaches GitHub's comment limit, and a 422 loses the approval
    # surface exactly where the fan-out most needs a human reading it.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _, stdout = _report(tmp_path, ["predict-plan", "--body-file", str(body)], env)

    report = cli._render_approval_report(_widened(_plan(stdout), 200), stage="predict-plan")

    assert len(report) < cli._APPROVAL_REPORT_MAX_CHARS < _COMMENT_LIMIT
    # Bounded by construction, not by the clamp: a document that only just fits
    # because it was cut is one section away from losing something load-bearing.
    assert cli._APPROVAL_REPORT_TRUNCATED not in report


def test_the_approval_report_clamp_cuts_a_document_that_overflows_anyway(
    tmp_path: Path,
) -> None:
    # The backstop behind the construction bound, exercised through the one
    # unbounded string a plan carries into the report — the run id. Whatever
    # widens past the sections' own caps, the document still fits a comment, and
    # says it was cut rather than ending mid-sentence.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _, stdout = _report(tmp_path, ["predict-plan", "--body-file", str(body)], env)
    plan = _plan(stdout)
    plan["run_id"] = "X" * 70_000

    report = cli._render_approval_report(plan, stage="predict-plan")

    assert len(report) == cli._APPROVAL_REPORT_MAX_CHARS < _COMMENT_LIMIT
    assert report.endswith(cli._APPROVAL_REPORT_TRUNCATED)


def test_every_drop_class_a_plan_emits_is_named_in_the_report(tmp_path: Path) -> None:
    # The drift guard. A new drop class added to a plan but not to the report's
    # table renders as a silently missing line — the counts block would still
    # reconcile, so nothing else fails, and the approval comment would quietly
    # stop naming a class that took cells.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    named = {key for key, _ in cli._APPROVAL_DROP_CLASSES}

    for command in ("predict-plan", "evaluate-plan"):
        plan = _plan(runner.invoke(app, [command, "--body-file", str(body)], env=env).stdout)
        emitted = {k for k in plan if k.startswith(("dropped_", "withheld_"))}
        assert emitted, f"{command} emitted no drop lists at all"
        assert emitted <= named, (
            f"{command} drop classes missing from the report: {emitted - named}"
        )


def test_the_approval_report_carries_a_spend_breach_verbatim(tmp_path: Path) -> None:
    # The one state where approving costs nothing and does nothing: the report
    # must say so in the backstop's own words, beside a table that still lists
    # the fan-out the earlier steps decided.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        seed_predictions=False,
        spend_ceiling_usd=10.0,
    )
    _spend_ledger(Path(env["FEDCOURTS_DATA_ROOT"]), cost=12.0)

    report, stdout = _report(tmp_path, ["predict-plan", "--body-file", str(body)], env)

    result = runner.invoke(app, ["predict-plan", "--body-file", str(body)], env=env)
    breach = (
        "predict-plan: the ex-post spend backstop is breached, so a real run would mint 0 cells "
        "however many this plan lists; the plan reports the gate rather than applying it"
    )
    assert breach in report
    assert breach in result.stderr
    # And the closing spend sentence carries it too, so the last line a reader
    # keeps does not read as a forecast of what approving would cost.
    assert "so a real run mints 0." in report
    # The heading is the one line a skimmer is guaranteed to read, so it cannot
    # promise 6 cells a real run would not mint.
    assert (
        "## predict-plan: 6 cell(s) held for approval — but a real run mints 0 under the "
        "spend backstop" in report
    )
    assert len(_plan(stdout)["would_mint"]) == 6


def test_the_approval_report_names_a_stranded_guard_that_failed_open(tmp_path: Path) -> None:
    # A withheld count of zero is three states, and only the degraded ones are a
    # reason to hesitate before approving — so they are named where the decision
    # is made rather than left in the JSON.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)
    census = tmp_path / "stranded-artifacts.json"
    census.write_text('{"not": "a list"}')

    report, _ = _report(
        tmp_path,
        ["predict-plan", "--body-file", str(body), "--stranded-file", str(census)],
        env,
    )

    assert "### Stranded-run guard" in report
    assert "may re-spend output an uncollected run already produced" in report
    # The reason quotes the underlying exception, and this census's exception
    # carries `<class 'dict'>`. Unspanned, GitHub's comment sanitizer eats that
    # as a tag and the maintainer reads "got ." where the cause should be — so
    # the whole reason is pinned inside a code span, not merely present.
    plan = _plan(
        runner.invoke(
            app, ["predict-plan", "--body-file", str(body), "--stranded-file", str(census)], env=env
        ).stdout
    )
    reason = plan["stranded_guard"]["degraded_reason"]
    assert "<class 'dict'>" in reason
    assert f"The stranded-run guard failed open (`{reason}`)," in report


def test_the_approval_report_stays_silent_about_a_guard_that_ran_clean(tmp_path: Path) -> None:
    # The mirror: a clean or absent guard is not a warning, and a section that
    # printed on every plan would train a reader to skip the one that matters.
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",), seed_predictions=False)

    report, _ = _report(tmp_path, ["predict-plan", "--body-file", str(body)], env)

    assert "### Stranded-run guard" not in report


def test_the_evaluate_approval_report_carries_the_assumption_caveat(tmp_path: Path) -> None:
    # The evaluate seam's rates are a scaled pre-freeze anchor, so the figure the
    # approval decision turns on cannot be quoted from this comment without it.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))

    report, stdout = _report(tmp_path, ["evaluate-plan", "--body-file", str(body)], env)

    assert "evaluate-plan: 6 cell(s) held for approval" in report
    assert "an assumption (pre-freeze cert-stage anchor scaled ~+22%), not a measurement" in report
    # The judge column is the evaluate seam's actor, not a predictor.
    assert "| Evaluator | Case | Event | Engine |" in report
    for cell in _plan(stdout)["would_mint"]:
        assert f"| `{cell['evaluator_id']}` |" in report


@pytest.mark.parametrize("command", ["predict-plan", "evaluate-plan"])
def test_the_approval_report_leaves_the_plan_json_byte_identical(
    tmp_path: Path, command: str
) -> None:
    # The report is a third channel, not a mode: a gate that parses stdout must
    # not be able to tell whether a report was written beside it.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    # A fixed run id, since a plan otherwise stamps itself with the clock.
    args = [command, "--body-file", str(body), "--run-id", "RID"]

    bare = runner.invoke(app, args, env=env)
    reported, with_report = _report(tmp_path, args, env)

    assert bare.exit_code == 0
    assert bare.stdout == with_report
    assert reported.endswith("\n")


# --- the evaluate stage's second input mode: no trigger, derive the backlog ---

EVALUATORS_YAML = "evaluators.yaml"


def _flat(output: str) -> str:
    """CLI output with ANSI styling stripped and runs of whitespace collapsed.

    Typer renders a refusal inside a bordered box, wrapping the message at the
    frame width, so a phrase that is contiguous in the source is split across
    lines here — and on a CI runner rich emits color escapes mid-phrase, so a
    substring match must strip them too. Assert against this rather than
    pinning the line breaks or the terminal styling.
    """
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    return " ".join(plain.replace("│", " ").split())


def _resolve(env: dict[str, str], *cases: str, event_id: str = EVENT) -> None:
    """Mark each case's event resolved in the corpus — the backlog's first condition.

    `_env` seeds rows and predictions; a grading is only owed once the event is
    also recorded resolved, so the backlog mode needs this on top.
    """
    with corpus.connect(corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"]))) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event_id,
                    case_id=cid,
                    court=cid.split("/")[0],
                    kind=EventKind.petition,
                    title="Disposition of the petition",
                    resolved=True,
                )
                for cid in cases
            ],
        )


def _stamps(env: dict[str, str], *cases: str) -> dict[str, object]:
    with corpus.connect_readonly(corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"]))) as conn:
        rows = {cid: corpus.get_row(conn, cid) for cid in cases}
    return {cid: None if row is None else row.evaluate_queued_at for cid, row in rows.items()}


def test_evaluate_matrix_with_no_body_file_derives_its_cases_from_the_backlog(
    tmp_path: Path,
) -> None:
    """The scheduled mode: given no case list at all, the fan-out is the
    gradings committed state still owes — the derivation a run-evaluate cron
    consumes."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _resolve(env, "scotus/24001", "scotus/24002")

    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0
    minted = {(c["docket"], c["evaluator_id"]) for c in _cells(result.stdout)}
    # Expected from the registry, not from the output: deriving the expectation
    # from the cells would let an evaluator silently vanishing from every cell
    # shrink both sides together and still pass.
    judges = {
        e.id for e in enabled_evaluators(Path(env["FEDCOURTS_CONFIG_ROOT"]) / EVALUATORS_YAML)
    }
    assert minted == {(d, j) for d in (24001, 24002) for j in judges}


def test_the_backlog_mode_mints_nothing_for_a_case_with_no_resolved_event(
    tmp_path: Path,
) -> None:
    """The backlog is a level on committed state, not a list of known cases: a row
    with a prediction but no *resolved* event is not owed a grading yet, so a
    scheduled run over it is empty rather than a fan-out over the whole corpus."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))

    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0
    assert _cells(result.stdout) == []


def test_the_already_graded_gate_is_the_backlog_modes_idempotency(tmp_path: Path) -> None:
    """The load-bearing test for the stamp-free design. With no debounce stamp the
    derivation repeats, so the already-graded gate is the only thing standing
    between a re-plan and a double-graded cell — and it holds, per (evaluator,
    event), leaving the siblings still owed intact."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _resolve(env, "scotus/24001", "scotus/24002")
    seed_evaluation(tmp_path / "data", "scotus", 24001, EVENT)

    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0
    assert "dropped 1 already-evaluated cell(s)" in result.output
    minted = {(c["docket"], c["evaluator_id"]) for c in _cells(result.stdout)}
    assert (24001, "claude-judge") not in minted
    assert (24002, "claude-judge") in minted

    # Grade the rest and the mode goes quiet: a re-plan of the same backlog mints
    # nothing, which is what makes a repeating cron safe without a stamp.
    for evaluator_id in {str(c["evaluator_id"]) for c in _cells(result.stdout)}:
        for docket in (24001, 24002):
            seed_evaluation(tmp_path / "data", "scotus", docket, EVENT, evaluator_id=evaluator_id)
    again = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID2"], env=env)
    assert again.exit_code == 0
    assert _cells(again.stdout) == []


def test_the_backlog_mode_writes_no_debounce_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mode must not write the corpus at all: it runs outside the writer jobs,
    which are the only holders of corpus-write credentials. The shared deriver's
    `evaluate_queued_at` writer API is the write it would otherwise inherit,
    so its absence is asserted directly, and the stamp function is
    made fatal to catch a call that somehow wrote nothing."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _resolve(env, "scotus/24001", "scotus/24002")
    before = _stamps(env, "scotus/24001", "scotus/24002")
    assert before == {"scotus/24001": None, "scotus/24002": None}

    def _fatal(*args: object, **kwargs: object) -> None:
        raise AssertionError("the backlog mode must not stamp the corpus")

    monkeypatch.setattr(corpus, "stamp_evaluate_queued", _fatal)
    db = corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"]))
    digest = hashlib.sha256(db.read_bytes()).hexdigest()

    minted = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)
    assert minted.exit_code == 0, minted.output
    # The property is write-freedom *on a run that did the work*: without this,
    # a regression that derived an empty backlog would leave the test green
    # while destroying what it claims to protect.
    assert _cells(minted.stdout)
    assert _stamps(env, "scotus/24001", "scotus/24002") == before
    # Not just the stamp column — the file. The deriver's connection is a
    # one-method protocol over a writable sqlite3 handle on the local backend,
    # so a stray write elsewhere in the scan would not move the stamp.
    assert hashlib.sha256(db.read_bytes()).hexdigest() == digest

    planned = runner.invoke(app, ["evaluate-plan", "--run-id", "RID"], env=env)
    assert planned.exit_code == 0, planned.output
    assert _stamps(env, "scotus/24001", "scotus/24002") == before
    assert hashlib.sha256(db.read_bytes()).hexdigest() == digest


def test_the_backlog_mode_refuses_a_corpus_backend_with_no_query_surface(
    tmp_path: Path,
) -> None:
    """A backend with no queryable connection is refused by the same gate that
    refuses the read-in-place one, and for the stronger reason: it could not serve
    the scan at all. It fails loudly rather than falling back to a local file the
    runner may never have pulled."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))
    _resolve(env, "scotus/24001")

    result = runner.invoke(
        app,
        ["evaluate-matrix", "--run-id", "RID"],
        env={**env, "FEDCOURTS_CORPUS_BACKEND": "service"},
    )

    assert result.exit_code != 0
    assert "cannot be derived over" in _flat(result.output)


def test_a_body_file_still_wins_over_the_backlog(tmp_path: Path) -> None:
    """A body file names the fan-out outright, so it takes precedence: the cases
    are the body's, and the backlog is never consulted."""
    body = tmp_path / "issue-body.md"
    body.write_text(_SINGLE_BODY)
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    # 24002 is owed a grading too; the body names only 24001, so it must not appear.
    _resolve(env, "scotus/24001", "scotus/24002")

    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )

    assert result.exit_code == 0
    assert {c["docket"] for c in _cells(result.stdout)} == {24001}


@pytest.mark.parametrize(
    "flags",
    [
        ["--court", "scotus"],
        ["--docket", "24001"],
        ["--event", EVENT],
    ],
)
def test_a_half_named_case_is_refused_rather_than_widened_to_the_backlog(
    tmp_path: Path, flags: list[str]
) -> None:
    """Silence is what selects the backlog mode, so a dropped `--docket` would
    otherwise turn one intended case into a whole-backlog fan-out. That is the one
    typo whose blast radius is model spend, so each half-named form is an error."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _resolve(env, "scotus/24001", "scotus/24002")

    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID", *flags], env=env)

    assert result.exit_code != 0
    assert '"include"' not in result.stdout
    assert "go together" in _flat(result.output) or "--event names" in _flat(result.output)


def test_predict_matrix_refuses_a_half_named_case_on_the_shared_helper(tmp_path: Path) -> None:
    """The half-named refusal lives in the helper both stages share, so pin it on
    the predict caller too — it has no backlog to be widened into, but it must not
    start accepting a case the evaluate caller rejects."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID", "--court", "scotus"], env=env)

    assert result.exit_code != 0
    assert "go together" in _flat(result.output)


def test_force_is_refused_with_the_backlog(tmp_path: Path) -> None:
    """`--force` and the backlog select opposite sets: a re-grade names its target,
    while the backlog drops a fully-graded case *before* the already-graded gate
    `--force` disables ever sees it. Accepting the pair would answer a rubric-change
    re-grade with an empty fan-out, the flag reading as honoured while doing
    nothing — so it is refused instead."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))
    _resolve(env, "scotus/24001")
    for evaluator in enabled_evaluators(Path(env["FEDCOURTS_CONFIG_ROOT"]) / EVALUATORS_YAML):
        seed_evaluation(tmp_path / "data", "scotus", 24001, EVENT, evaluator_id=evaluator.id)

    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID", "--force"], env=env)

    assert result.exit_code != 0
    assert "cannot re-grade the backlog" in _flat(result.output)


def test_the_backlog_mode_refuses_a_read_in_place_corpus_backend(tmp_path: Path) -> None:
    """The scan is one pass over every resolved event plus a row per candidate —
    the opposite shape from the point lookups a named-case run makes, and so the
    opposite backend. Refused here rather than discovered as a range-request storm
    on an unattended run."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))
    _resolve(env, "scotus/24001")

    result = runner.invoke(
        app,
        ["evaluate-matrix", "--run-id", "RID"],
        env={**env, "FEDCOURTS_CORPUS_BACKEND": "ranged"},
    )

    assert result.exit_code != 0
    assert "cannot be derived over" in _flat(result.output)


def test_the_backlog_mode_refuses_an_absent_corpus(tmp_path: Path) -> None:
    """For an unattended lane, "nothing is owed" and "no corpus on disk" must not
    be the same output — an empty fan-out from a runner that never pulled reads
    exactly like a drained backlog."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))
    _resolve(env, "scotus/24001")
    corpus.corpus_db_path(Path(env["FEDCOURTS_CORPUS_ROOT"])).unlink()

    result = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code != 0
    assert "corpus-pull" in _flat(result.output)


def test_predict_matrix_derives_its_own_backlog_when_given_no_input(tmp_path: Path) -> None:
    """Predict takes the same second input mode, over its own deriver. This fixture
    provisions no documents, so the backlog's provisioning predicate holds every
    case and the fan-out is empty — the point here being that an input-less run is
    a *derivation*, not a refusal. `tests/test_predict_backlog.py` carries the
    populated derivation and the predicate itself."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001",))

    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"], env=env)

    assert result.exit_code == 0, result.output
    assert _cells(result.stdout) == []


def test_evaluate_plan_dry_runs_exactly_the_backlog_matrix_would_mint(tmp_path: Path) -> None:
    """The dry run of the scheduled derivation — the executed check the workflow
    half needs before it is wired to a cron. Both modes go through one pipeline,
    so the plan cannot describe a fan-out the minting command would not perform."""
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    _resolve(env, "scotus/24001", "scotus/24002")
    seed_evaluation(tmp_path / "data", "scotus", 24001, EVENT)

    minted = runner.invoke(app, ["evaluate-matrix", "--run-id", "RID"], env=env)
    planned = runner.invoke(app, ["evaluate-plan", "--run-id", "RID"], env=env)

    assert minted.exit_code == 0
    assert planned.exit_code == 0
    plan = _plan(planned.stdout)
    _assert_evaluate_balances(plan)
    assert plan["counts"]["provenance"]["requested_cases"] == 2
    assert plan["counts"]["cell_ledger"]["dropped_already_evaluated_cells"] == 1
    assert [
        (c["evaluator_id"], c["court"], c["docket"], c["event_id"]) for c in plan["would_mint"]
    ] == [
        (c["evaluator_id"], c["court"], c["docket"], c["event_id"]) for c in _cells(minted.stdout)
    ]
