import json
import shutil
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.corpus_ranged import RangedBackendError
from fedcourtsai.schemas import EventKind
from tests.conftest import seed_evaluation, seed_prediction

runner = CliRunner()

_REPO_CONFIG = Path(__file__).resolve().parents[1] / "config"

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
) -> dict[str, str]:
    """A hermetic config + corpus for a matrix run.

    Copies the real registries so the fan-out dimensions are unchanged, writes a
    ``tracking.yaml`` pinning ``predict.scope`` (and, with ``max_cells``, the
    volume backstop), and seeds a corpus holding a row for each of the ``cases``
    ids (the gate reads each case's row: an absent row, or a non-SCOTUS court, is
    out of scope).
    """
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    for name in ("predictors.yaml", "evaluators.yaml"):
        (config_root / name).write_text((_REPO_CONFIG / name).read_text())
    tracking = f"predict:\n  scope: {scope}\n"
    if max_cells is not None:
        tracking += f"  max_predict_cells_per_run: {max_cells}\n"
    (config_root / "tracking.yaml").write_text(tracking)

    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id=cid, court=cid.split("/")[0]) for cid in cases],
        )
    # The evaluate gate reads the ledger: seed one committed prediction per
    # case's event so evaluate-matrix keeps them.
    data_root = tmp_path / "data"
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
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    cells = _cells(result.stdout)
    # 3 predictors x 2 cases x 1 event
    assert len(cells) == 6
    assert {(c["court"], c["docket"]) for c in cells} == {("scotus", 24001), ("scotus", 24002)}


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
    # a 2-cell cap, so the matrix empties. The workflow's empty-matrix step will
    # close the trigger issue as if out of scope, so the cap escalates to a
    # correctly-attributed ::error:: — the deferred cases still re-run next cycle.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        max_cells=2,
    )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert _cells(result.stdout) == []  # matrix empty: has_jobs=false downstream
    assert "::error::" in result.stderr
    assert "deferred ALL 2 case(s)" in result.stderr
    assert "out of scope" in result.stderr  # names the misattributed close


def test_predict_matrix_under_the_cap_is_unchanged(tmp_path: Path) -> None:
    # A run inside the backstop fans out fully and surfaces no deferral warning.
    body = tmp_path / "issue-body.md"
    body.write_text(_BATCH_BODY)
    env = _env(
        tmp_path,
        scope="scotus_docket",
        cases=("scotus/24001", "scotus/24002"),
        max_cells=240,
    )
    result = runner.invoke(
        app, ["predict-matrix", "--run-id", "RID", "--body-file", str(body)], env=env
    )
    assert result.exit_code == 0
    assert len(_cells(result.stdout)) == 6
    assert "volume cap" not in result.stderr


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
    # it. 24001 is unscored → fail-open → still predicted.
    env = _env(tmp_path, scope="scotus_docket", cases=("scotus/24001", "scotus/24002"))
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


def test_matrix_without_body_or_flags_errors() -> None:
    result = runner.invoke(app, ["predict-matrix", "--run-id", "RID"])
    assert result.exit_code == 2


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
