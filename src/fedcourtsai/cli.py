"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from . import (
    analytics,
    cleanup,
    corpus,
    corpus_ranged,
    dvc,
    ids,
    integration_check,
    metrics_refresh,
)
from .agent_feedback import post_agent_feedback
from .authz import authorize_trigger
from .backtest import default_backtesters, run_backtest, select_backtest_set
from .cert_backtest import (
    replay_predictors,
    replayable_items,
    run_cert_backtest,
    select_cert_backtest_set,
)
from .collect import (
    CellStatus,
    CollectPlan,
    PathJailError,
    PrPlan,
    ReconcileCellStatus,
    assert_cleanup_within_jail,
    assert_within_jail,
    collect_plan,
    parse_name_status,
    reconcile_collect_plan,
    render_stall_comment,
)
from .config import (
    PredictScope,
    get_settings,
    load_courts,
    load_predict_config,
    load_pull_config,
    load_seed_config,
)
from .courtlistener import CourtListenerClient, default_rate_limiter
from .finalize import FinalizeRole, agent_produced_output
from .fixture import build_fixture_corpus
from .leaderboard import build_leaderboard
from .matrix import CaseRequest, evaluate_matrix, parse_cases, predict_matrix, reconcile_matrix
from .ops import (
    build_ops_report,
    render_data_health,
    render_markdown,
    summarize_trigger_issues,
)
from .paths import CasePaths
from .pipeline.cascade import CascadeError, run_cascade
from .pipeline.discover import discover_cases
from .pipeline.pull import PullQueues, pull_case, pull_cases
from .pipeline.recoverability import (
    dated_share_snapshot,
    parse_docket_pairs,
    probe_dockets,
    probe_sample,
    render_summary,
    sample_dateless_targets,
)
from .pipeline.refresh import full_refresh as run_full_refresh
from .pipeline.runner import EngineFailed, EngineUnavailable
from .pipeline.scope_reconcile import reconcile_predict_scope
from .pipeline.seed import (
    CourtListenerBulkSource,
    backfill,
    load_cursor,
    resolve_dockets_source,
    sibling_bulk_url,
)
from .pricing import DEFAULT_MODELS, MODEL_RATES, TokenCounts, estimate_cost_usd
from .registry import enabled_predictors, load_evaluators, load_predictors
from .schemas import (
    EXPORTABLE_MODELS,
    AgentFlags,
    CorpusScopeAudit,
    CorpusValidation,
    DataHealth,
    Disposition,
    Engine,
    GroupBy,
    ModelUsage,
    OpsReport,
    PredictableEvent,
    UsageRole,
)
from .serialize import write_json, write_raw_json, write_text, write_yaml
from .store import (
    cases_due_for_backfill,
    cases_due_for_pull,
    iter_flags,
    iter_stratified_evaluations,
    iter_tooling,
    iter_usage,
    open_events,
    resolved_events,
)
from .usage import parse_claude_usage, parse_codex_usage, parse_gemini_usage
from .validate import (
    run_corpus_validation,
    run_ledger_referential_checks,
    run_scope_audit,
    validate_ledger,
)

app = typer.Typer(add_completion=False, help="Predict events in US federal courts.")


def _version_callback(value: bool) -> None:
    """Print the installed package version and exit (eager ``--version``)."""
    if value:
        typer.echo(version("fedcourtsai"))
        raise typer.Exit


@app.callback()
def _main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the installed fedcourtsai version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Predict events in US federal courts."""


def _client() -> CourtListenerClient:
    s = get_settings()
    return CourtListenerClient(
        base_url=s.courtlistener_base_url,
        api_token=s.courtlistener_api_token,
        timeout=s.request_timeout,
        rate_limiter=default_rate_limiter(
            s.courtlistener_rpm,
            s.courtlistener_rph,
            s.courtlistener_rpd,
            max_wait=s.courtlistener_max_wait,
        ),
    )


@app.command()
def validate(
    path: Annotated[Path, typer.Argument(help="Directory to validate recursively.")] = Path("data"),
) -> None:
    """Validate the git ledger under PATH: schema conformance + git-only references.

    Two corpus-free layers the PR gate can enforce offline: every known artifact
    matches its schema, and every judgment references an event that exists in the
    git tree (with its declared ids matching the path) while every evaluation
    targets a real prediction. The corpus-dependent referential checks need the DVC
    remote, so they run scheduled via ``validate-corpus`` rather than here.
    """
    result = validate_ledger(path)
    references = run_ledger_referential_checks(path)
    ref_failures = sum(c.failures for c in references)
    if not result.ok or ref_failures:
        for err in result.problems:
            typer.echo(f"INVALID {err}", err=True)
        for check in references:
            for problem in check.problems:
                typer.echo(f"ORPHAN {problem}", err=True)
        typer.echo(
            f"\n{result.invalid} invalid / {result.checked} checked; "
            f"{ref_failures} referential problem(s)",
            err=True,
        )
        raise typer.Exit(code=1)
    refs_checked = sum(c.checked for c in references)
    typer.echo(f"OK: {result.checked} artifact(s) valid, {refs_checked} reference(s) consistent")


@app.command("validate-corpus")
def validate_corpus_cmd(
    out: Annotated[
        Path | None,
        typer.Option(
            help="Write the verdict JSON here (default: <metrics_root>/corpus-validation.json)."
        ),
    ] = None,
    baseline_count: Annotated[
        int | None,
        typer.Option(
            help="Prior corpus row count; the verdict fails if the current count dropped "
            "below it. Absent, the append-only check is a no-op pass."
        ),
    ] = None,
    today: Annotated[
        str,
        typer.Option(
            help="ISO as-of date for the future-dated-snapshot check; defaults to today (UTC)."
        ),
    ] = "",
) -> None:
    """Run corpus-integrity + referential checks and emit a JSON verdict.

    The complement to ``validate``: it opens the packed corpus and asserts the
    correctness invariants that span the two stores — the corpus is append-only and
    self-consistent, and no git-ledger judgment under ``data/`` is an orphan. Writes
    the structured ``CorpusValidation`` verdict and prints a one-line summary.
    Graceful when the corpus is absent (run before ``dvc pull``): writes a skipped
    verdict and exits 0. The exit code reports check health (non-zero on a failed
    verdict) so a caller can surface it; the wiring that runs this treats a failure
    as loud-not-fatal, never blocking on it.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    cursor = load_cursor(load_seed_config(settings.config_root).cursor)
    as_of = date.fromisoformat(today) if today else datetime.now(UTC).date()
    verdict = run_corpus_validation(
        corpus_db_path=db_path,
        data_root=settings.data_root,
        seed_cursor=cursor,
        today=as_of,
        baseline_count=baseline_count,
        tracked_courts=load_courts(settings.config_root),
    )
    destination = out if out is not None else settings.metrics_root / "corpus-validation.json"
    write_json(destination, verdict)
    if verdict.skipped:
        typer.echo(f"corpus-validation: skipped (no corpus at {db_path}) -> {destination}")
        return
    passed = sum(1 for c in verdict.checks if c.passed)
    status = "OK" if verdict.ok else "FAIL"
    typer.echo(
        f"corpus-validation: {status} — {passed}/{len(verdict.checks)} check(s) passed over "
        f"{verdict.corpus_rows} row(s) -> {destination}"
    )
    if not verdict.ok:
        for check in verdict.checks:
            if not check.passed:
                typer.echo(f"FAIL {check.name}: {check.failures} problem(s)", err=True)
        raise typer.Exit(code=1)


@app.command("corpus-scope-audit")
def corpus_scope_audit_cmd(
    out: Annotated[
        Path | None,
        typer.Option(
            help="Write the audit JSON here (default: <metrics_root>/corpus-scope-audit.json)."
        ),
    ] = None,
) -> None:
    """Census open corpus events the predict scope excludes; emit a JSON audit (#343).

    Read-only: opens the packed corpus and, for every still-open SCOTUS event, tallies
    by exclusion reason (pre-1925 mandatory jurisdiction #309, stale unresolvable #333)
    the cases, open events, and the recoverable subset (those whose case carries an
    opinion/citation/decision-date signal — a hint the disposition is an ingestion gap
    rather than genuinely absent). Writes the `CorpusScopeAudit` and prints a summary.
    Graceful when the corpus is absent (run before `dvc pull`): writes a skipped audit
    and exits 0. The corpus-writer path publishes this for `run-ops` to present.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    audit = run_scope_audit(corpus_db_path=db_path)
    destination = out if out is not None else settings.metrics_root / "corpus-scope-audit.json"
    write_json(destination, audit)
    if audit.skipped:
        typer.echo(f"corpus-scope-audit: skipped (no corpus at {db_path}) -> {destination}")
        return
    total = sum(e.open_events for e in audit.exclusions)
    typer.echo(
        f"corpus-scope-audit: {total} out-of-scope open event(s) across "
        f"{len(audit.exclusions)} reason(s), of {audit.scotus_open_events} SCOTUS open "
        f"-> {destination}"
    )
    for exclusion in audit.exclusions:
        typer.echo(
            f"  - {exclusion.reason}: {exclusion.open_events} event(s) on {exclusion.cases} "
            f"case(s), {exclusion.recoverable} recoverable"
        )
    for bucket in audit.unclassified:
        typer.echo(f"  · in scope — {bucket.reason}: {bucket.open_events} event(s)")
    for shape in audit.unparseable_docket_shapes:
        typer.echo(f"    · shape {shape.shape!r}: {shape.count} event(s)")


@app.command("reconcile-scope")
def reconcile_scope_cmd(
    apply: Annotated[
        bool,
        typer.Option(
            "--apply", help="Write the latch changes; omit for a dry-run that only counts."
        ),
    ] = False,
) -> None:
    """Reconcile the corpus's out-of-scope latch with the predicate set (issue #343).

    The write counterpart of `corpus-scope-audit`: over the predict-eligible cases, it
    latches `predict_excluded` on those the shared exclusion reasoning now matches
    (`corpus.out_of_scope_reason_full` — the row rules plus the snapshot-aware bare
    opinion-import rule) and clears it on those back in scope — so `open-events` (and
    thus the predict/queueing paths) drop excluded cases at the source. Dry-run by
    default; `--apply` writes (the seed run then `dvc push`es the corpus). Prints a
    `ScopeReconcileResult`. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (dvc pull) "
            "before running the scope reconcile.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = reconcile_predict_scope(conn, apply=apply)
    verb = "latched out / released" if apply else "would latch out / release"
    typer.echo(
        f"reconcile-scope ({'applied' if apply else 'dry-run'}): {verb} "
        f"{result.excluded} / {result.released} of {result.eligible_cases} eligible case(s)"
    )
    typer.echo(result.model_dump_json())


@app.command("dvc-status")
def dvc_status(
    path: Annotated[Path, typer.Argument(help="Repository root to check.")] = Path("."),
) -> None:
    """Check the committed DVC metadata is internally consistent (offline).

    The CI gate has no DVC remote or credentials, so it cannot diff the corpus
    blob against S3. This is the offline half that can run there: it confirms
    every DVC-tracked data output (the ``corpus/corpus.db.dvc`` pointer, any
    cached stage output) is well-formed, gitignored, and absent from git — so the
    corpus blob can never slip into the repo — and that every ``cache: false``
    pipeline output (the ``metrics/`` roll-ups) is committed. When the corpus
    blob is present locally it also checks the file's physical layout against
    the ranged-read contract (64 KB pages, non-WAL at rest) so a drifted file
    fails loudly before it is pushed. Exits non-zero and lists every problem if
    the bookkeeping has drifted. The online ``dvc status`` / push side belongs
    to the data workflows that hold the remote credentials.
    """
    is_tracked, is_ignored = dvc.git_checkers(path)
    errors = dvc.check_state(path, is_tracked=is_tracked, is_ignored=is_ignored)
    outs, _ = dvc.collect_outs(path)
    tracked = dvc.tracked_paths(outs)
    # The ranged-read layout contract rides on the same offline gate: check the
    # corpus blob's header whenever the file is present (absent is fine — the
    # gate runs before any `dvc pull`).
    errors += [
        problem
        for out_path in tracked
        if out_path.name == corpus.CORPUS_DB_FILENAME
        for problem in corpus.check_ranged_layout(path / out_path)
    ]
    if errors:
        for err in errors:
            typer.echo(f"DVC {err}", err=True)
        typer.echo(f"\n{len(errors)} DVC metadata problem(s)", err=True)
        raise typer.Exit(code=1)
    summary = ", ".join(str(p) for p in tracked) if tracked else "none"
    typer.echo(f"OK: DVC metadata consistent ({len(tracked)} remote-tracked output(s): {summary})")


@app.command()
def leaderboard(
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <metrics_root>/leaderboard.json)."),
    ] = None,
) -> None:
    """Rank predictors from the evaluations ledger into ``metrics/leaderboard.json``.

    Deterministic and offline: aggregates every committed ``evaluation.json``
    under ``data/`` into one best-first standing per predictor — accuracy, mean
    Brier score, mean vote accuracy, a reasoning-quality summary, and counts,
    each reported **per pre-registration stratum** (forward forecasts vs
    retrospective cells, never blended; see the ``Leaderboard`` schema) — and
    writes it through the shared serializer for minimal diffs. Reruns over an
    unchanged ledger reproduce the file byte for byte.
    """
    settings = get_settings()
    board = build_leaderboard(iter_stratified_evaluations(settings.data_root))
    destination = out if out is not None else settings.metrics_root / "leaderboard.json"
    write_json(destination, board)
    typer.echo(
        f"leaderboard: {board.predictors_ranked} predictor(s) from "
        f"{board.evaluations_total} evaluation(s) "
        f"({board.forward_evaluations} forward / "
        f"{board.retrospective_evaluations} retrospective) -> {destination}"
    )


@app.command()
def backtest(
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <metrics_root>/backtest.json)."),
    ] = None,
    court: Annotated[
        str, typer.Option(help="Restrict the back-test set to one CourtListener court id.")
    ] = "",
    limit: Annotated[
        int | None, typer.Option(help="Cap the back-test set to the first N resolved events.")
    ] = None,
) -> None:
    """Replay the reference predictors over resolved corpus events into ``metrics/backtest.json``.

    The corpus doubles as a back-test set: each resolved event's outcome is
    hidden, every reference predictor is replayed against the remaining facts,
    and the prediction is scored against the known disposition. Deterministic and
    offline — a pure function of the corpus — so reruns reproduce the file byte
    for byte. Writes an empty zero-count report when the corpus is absent (run
    after `dvc pull`) or carries no resolved events.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    destination = out if out is not None else settings.metrics_root / "backtest.json"
    if not db_path.exists():
        report = run_backtest([], [])
        write_json(destination, report)
        typer.echo(f"No corpus at {db_path} — wrote empty back-test report -> {destination}")
        return
    with corpus.connect(db_path) as conn:
        items = select_backtest_set(conn, court=court or None, limit=limit)
        report = run_backtest(default_backtesters(conn), items)
    write_json(destination, report)
    typer.echo(
        f"backtest: {report.predictors_evaluated} predictor(s) over "
        f"{report.events_scored} resolved event(s) -> {destination}"
    )


@app.command("cert-backtest")
def cert_backtest_cmd(
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <metrics_root>/cert-backtest.json)."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option(
            help="Cap the cert set to the N most recently decided petitions. Keep it "
            "small with a real --engine: every petition costs one cell per predictor."
        ),
    ] = 25,
    engine: Annotated[
        str,
        typer.Option(
            help="Also replay the enabled agentic predictors: 'auto' routes each "
            "predictor through its own configured engine (skipping any whose engine "
            "has no registered runner); a concrete backend (stub, replay, "
            "claude-code, codex) routes every predictor through that one backend "
            "(offline runs / single-engine sweeps). Omit to score only the offline "
            "reference baselines."
        ),
    ] = "",
    work_dir: Annotated[
        Path | None,
        typer.Option(
            help="Scratch root for the replay's provisioned snapshots and prediction "
            "cells (default: a temporary directory). Never data/."
        ),
    ] = None,
) -> None:
    """Back-test cert predictors over decided petitions into ``metrics/cert-backtest.json``.

    Selects the most recently decided modern discretionary-cert petitions with a
    machine-readable grant/deny label, hides their outcomes, replays predictors,
    and scores them with the honest cert signals: **lift over the always-deny
    floor** and a P(granted) calibration view, alongside accuracy and Brier. The
    offline reference baselines always run; ``--engine`` additionally replays
    every enabled predictor over redacted snapshots in a scratch tree, each
    through its own configured engine under ``auto`` (this spends tokens on a
    real engine). Petitions the corpus cannot replay (no held snapshot or
    petition event — partial coverage is the norm while the date backfill
    drains) are dropped up front and named, so every backtester in one report is
    scored over the same set. Out of band by design: it never writes the
    ``data/`` ledger, and the report is labeled retrospective (the outcomes
    predate every modern model's training cutoff).
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    destination = out if out is not None else settings.metrics_root / "cert-backtest.json"
    if not db_path.exists():
        write_json(destination, run_cert_backtest([], []))
        typer.echo(f"No corpus at {db_path} — wrote empty cert back-test report -> {destination}")
        return
    with corpus.connect(db_path) as conn:
        items = select_cert_backtest_set(conn, limit=limit)
        backtesters = default_backtesters(conn)
        if engine:
            items, unreplayable = replayable_items(db_path, items)
            if unreplayable:
                typer.echo(
                    f"skipped {len(unreplayable)} petition(s) without a replayable "
                    "snapshot: " + ", ".join(unreplayable),
                    err=True,
                )
            work_root = work_dir if work_dir is not None else Path(tempfile.mkdtemp())
            replayed = replay_predictors(
                items,
                corpus_db_path=db_path,
                config_root=settings.config_root,
                work_root=work_root,
                engine_override=None if engine == "auto" else engine,
                run_id=ids.run_id(),
            )
            replayed_ids = {b.id for b in replayed}
            for predictor in enabled_predictors(settings.config_root / "predictors.yaml"):
                if predictor.id not in replayed_ids:
                    typer.echo(
                        f"skipped predictor {predictor.id}: engine "
                        f"{predictor.engine} has no registered runner",
                        err=True,
                    )
            backtesters += replayed
        report = run_cert_backtest(backtesters, items)
    write_json(destination, report)
    typer.echo(
        f"cert-backtest: {report.predictors_evaluated} predictor(s) over "
        f"{report.events_scored} decided petition(s); always-deny floor "
        f"{report.always_denied_accuracy:.3f} -> {destination}"
    )


@app.command()
def statpack(
    out: Annotated[
        Path | None,
        typer.Option(help="JSON output path (default: <metrics_root>/statpack.json)."),
    ] = None,
    markdown_out: Annotated[
        Path | None,
        typer.Option(help="Markdown output path (default: <metrics_root>/statpack.md)."),
    ] = None,
) -> None:
    """Roll the corpus into a base-rate statpack at ``metrics/statpack.{json,md}``.

    An independent published artifact — headline counts plus curated disposition
    base-rate breakdowns (by court, and SCOTUS petitions by Term and topic).
    Deterministic and offline: a pure function of the corpus, so reruns reproduce both
    files byte for byte. Writes the empty zero-count pack when the corpus is absent (run
    after `dvc pull`). Git-tracked as a DVC metric alongside `leaderboard` / `backtest`.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    pack = analytics.build_statpack(corpus_db_path=db_path)
    json_dest = out if out is not None else settings.metrics_root / "statpack.json"
    md_dest = markdown_out if markdown_out is not None else settings.metrics_root / "statpack.md"
    write_json(json_dest, pack)
    write_text(md_dest, analytics.render_statpack_markdown(pack))
    typer.echo(
        f"statpack: {pack.corpus_rows} case(s), {len(pack.sections)} section(s) "
        f"-> {json_dest}, {md_dest}"
    )


def _resolve_token_counts(
    explicit: TokenCounts,
    claude_execution_file: Path | None,
    codex_sessions_dir: Path | None,
    gemini_telemetry_file: Path | None,
) -> TokenCounts | None:
    """Token counts from an engine log if given, else the explicit overrides.

    Returns ``None`` when a log source was named but carried no usage — the
    signal for the caller to skip writing rather than record false zeros.
    """
    if claude_execution_file is not None:
        return parse_claude_usage(claude_execution_file)
    if codex_sessions_dir is not None:
        return parse_codex_usage(codex_sessions_dir)
    if gemini_telemetry_file is not None:
        return parse_gemini_usage(gemini_telemetry_file)
    return explicit


@app.command("record-usage")
def record_usage(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to inputs
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id this run predicted/scored.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    engine: Annotated[Engine, typer.Option(help="Engine that ran (claude-code | codex | gemini).")],
    role: Annotated[UsageRole, typer.Option(help="predictor (predict) | evaluator (evaluate).")],
    actor: Annotated[str, typer.Option(help="The predictor_id or evaluator_id for this cell.")],
    model: Annotated[
        str | None, typer.Option(help="Model run; defaults to the engine's default model.")
    ] = None,
    input_tokens: Annotated[int, typer.Option(help="Fresh input tokens (override).")] = 0,
    output_tokens: Annotated[int, typer.Option(help="Output tokens (override).")] = 0,
    cache_read_tokens: Annotated[int, typer.Option(help="Cached input tokens (override).")] = 0,
    cache_creation_tokens: Annotated[int, typer.Option(help="Cache-write tokens (override).")] = 0,
    claude_execution_file: Annotated[
        Path | None, typer.Option(help="Claude Code execution_file JSON to read usage from.")
    ] = None,
    codex_sessions_dir: Annotated[
        Path | None, typer.Option(help="Codex sessions dir (CODEX_HOME/sessions) to read usage.")
    ] = None,
    gemini_telemetry_file: Annotated[
        Path | None, typer.Option(help="Gemini CLI telemetry.log to read usage from.")
    ] = None,
    created_at: Annotated[
        str, typer.Option(help="ISO timestamp; defaults to the run id's timestamp.")
    ] = "",
) -> None:
    """Record one run's measured token usage and estimated cost to ``usage.json``.

    Reads token counts from the engine's own log (``--claude-execution-file``,
    ``--codex-sessions-dir``, or ``--gemini-telemetry-file``) or from the explicit
    ``--*-tokens`` overrides,
    applies the central rates in ``fedcourtsai.pricing`` (kept in sync with
    ``docs/budget.md``), and writes the validated artifact next to the run's
    prediction or evaluation output. Best-effort: exits non-zero without writing
    if no usage can be determined, so a capture step can warn and move on rather
    than fail the run or commit false zeros.
    """
    settings = get_settings()
    counts = _resolve_token_counts(
        TokenCounts(input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens),
        claude_execution_file,
        codex_sessions_dir,
        gemini_telemetry_file,
    )
    if counts is None or counts.total_tokens == 0:
        typer.echo("No model usage found; nothing recorded.", err=True)
        raise typer.Exit(code=3)

    resolved_model = model or DEFAULT_MODELS.get(engine.value)
    if resolved_model is None or resolved_model not in MODEL_RATES:
        known = ", ".join(sorted(MODEL_RATES))
        typer.echo(f"No rate for model '{resolved_model}'; known models: {known}", err=True)
        raise typer.Exit(code=2)

    if created_at:
        when = datetime.fromisoformat(created_at)
    else:
        try:
            when = ids.parse_run_id(run_id)
        except ValueError as exc:
            typer.echo(f"run-id '{run_id}' is not a timestamp; pass --created-at.", err=True)
            raise typer.Exit(code=2) from exc

    record = ModelUsage(
        case_id=ids.case_id(court, docket),
        event_id=event,
        run_id=run_id,
        role=role,
        actor_id=actor,
        engine=engine,
        model=resolved_model,
        created_at=when,
        input_tokens=counts.input_tokens,
        output_tokens=counts.output_tokens,
        cache_read_input_tokens=counts.cache_read_input_tokens,
        cache_creation_input_tokens=counts.cache_creation_input_tokens,
        estimated_cost_usd=estimate_cost_usd(resolved_model, counts),
    )
    event_paths = CasePaths(settings.data_root, court, docket).event(event)
    destination = (
        event_paths.prediction_usage(actor, run_id)
        if role == UsageRole.predictor
        else event_paths.evaluation_usage(actor, run_id)
    )
    write_json(destination, record)
    typer.echo(
        f"usage: {actor} {counts.total_tokens} tok ~${record.estimated_cost_usd:.4f} "
        f"-> {destination}"
    )


@app.command("usage-summary")
def usage_summary() -> None:
    """Sum recorded ``usage.json`` into an actual \\$/run, as JSON on stdout.

    Aggregates every ``usage.json`` under ``data/`` — overall totals and a
    per-actor (predictor/evaluator) breakdown with mean cost per run — so a
    maintainer can replace the planning assumption in ``docs/budget.md`` with the
    measured figure. Pure roll-up; persists nothing.
    """
    settings = get_settings()
    records = iter_usage(settings.data_root)

    def _agg(rows: list[ModelUsage]) -> dict[str, object]:
        runs = len(rows)
        cost = sum(r.estimated_cost_usd for r in rows)
        return {
            "runs": runs,
            "input_tokens": sum(r.input_tokens for r in rows),
            "output_tokens": sum(r.output_tokens for r in rows),
            "cache_read_input_tokens": sum(r.cache_read_input_tokens for r in rows),
            "cache_creation_input_tokens": sum(r.cache_creation_input_tokens for r in rows),
            "estimated_cost_usd": round(cost, 6),
            "mean_cost_usd_per_run": round(cost / runs, 6) if runs else 0.0,
        }

    by_actor: dict[str, list[ModelUsage]] = {}
    for record in records:
        by_actor.setdefault(record.actor_id, []).append(record)
    summary = {
        "overall": _agg(records),
        "by_actor": {
            actor: {"role": rows[0].role, **_agg(rows)} for actor, rows in sorted(by_actor.items())
        },
    }
    typer.echo(json.dumps(summary, indent=2, sort_keys=True))


@app.command("ops-report")
def ops_report(
    runs: Annotated[
        Path | None,
        typer.Option(
            help="JSON file of recent Actions runs (`gh run list --json …`) for the "
            "health section; omit to skip it."
        ),
    ] = None,
    json_out: Annotated[
        Path | None,
        typer.Option("--json", help="Also write the OpsReport JSON artifact here."),
    ] = None,
    previous: Annotated[
        Path | None,
        typer.Option(
            help="Prior OpsReport JSON (e.g. from the ops-metrics branch) for the "
            "backfill rate + ETA. Ignored if missing or unreadable."
        ),
    ] = None,
    generated_at: Annotated[
        str, typer.Option(help="ISO timestamp stamped on the report; defaults to now (UTC).")
    ] = "",
    corpus_validation: Annotated[
        Path | None,
        typer.Option(
            help="Latest `validate-corpus` verdict JSON (e.g. from the ops-metrics "
            "branch) for the data-health section. Ignored if missing or unreadable."
        ),
    ] = None,
    data_health_out: Annotated[
        Path | None,
        typer.Option(help="Write the data-health section Markdown here (the escalation body)."),
    ] = None,
    scope_audit: Annotated[
        Path | None,
        typer.Option(
            help="Latest `corpus-scope-audit` JSON (e.g. from the ops-metrics branch) for the "
            "out-of-scope-open-events section. Ignored if missing or unreadable."
        ),
    ] = None,
    trigger_issues: Annotated[
        Path | None,
        typer.Option(
            help="JSON file of open issues (`gh issue list --json number,title,labels,createdAt`) "
            "for the open-trigger-issues section; omit to skip it."
        ),
    ] = None,
) -> None:
    """Roll pipeline health, backfill, spend, and data health into an ops snapshot.

    A read-only view of authoritative sources — the GitHub Actions run history
    (``--runs``), the seed cursor (``config/seed-progress.yaml``), the recorded
    ``usage.json`` ledger under ``data/``, and the committed ``flags.json`` files
    agents leave there (rolled into the **open agent flags** section). Also presents
    the **data-health** verdict:
    it runs the git-only ``validate`` over ``data/`` itself and folds in the latest
    corpus verdict from ``--corpus-validation`` (produced where the corpus is already
    pulled). Prints the dashboard Markdown to stdout (the run-ops issue body / step
    summary) and, with ``--json``, writes the structured ``OpsReport``. Unlike the
    leaderboard/back-test roll-ups it is a point-in-time snapshot, so it is surfaced,
    not committed.
    """
    settings = get_settings()
    seed_cfg = load_seed_config(settings.config_root)
    courts = load_courts(settings.config_root)
    progress = load_cursor(seed_cfg.cursor)
    run_rows = json.loads(runs.read_text()) if runs is not None else []
    # The prior snapshot is best-effort: a missing/unreadable file just drops the
    # rate + ETA rather than failing the report.
    prior: OpsReport | None = None
    if previous is not None and previous.exists():
        try:
            prior = OpsReport.model_validate_json(previous.read_text())
        except ValueError:
            prior = None
    # Data health: the git-only ledger schema check always runs here (no corpus
    # needed), and the corpus verdict is read back from the producer path if present
    # (best-effort: a missing/unreadable verdict just leaves that half null).
    corpus_verdict: CorpusValidation | None = None
    if corpus_validation is not None and corpus_validation.exists():
        try:
            corpus_verdict = CorpusValidation.model_validate_json(corpus_validation.read_text())
        except ValueError:
            corpus_verdict = None
    ledger = validate_ledger(settings.data_root)
    data_health = DataHealth(
        ok=ledger.ok and (corpus_verdict is None or corpus_verdict.ok),
        ledger=ledger,
        corpus=corpus_verdict,
    )
    # The scope audit is surfaced like the corpus verdict: read back from the producer
    # path if published, best-effort (a missing/unreadable file just drops the section).
    scope_verdict: CorpusScopeAudit | None = None
    if scope_audit is not None and scope_audit.exists():
        try:
            scope_verdict = CorpusScopeAudit.model_validate_json(scope_audit.read_text())
        except ValueError:
            scope_verdict = None
    # Open run:* trigger issues (stalled fan-outs), best-effort like the other feeds:
    # a missing/unreadable file just drops the section.
    open_triggers = None
    if trigger_issues is not None and trigger_issues.exists():
        try:
            open_triggers = summarize_trigger_issues(json.loads(trigger_issues.read_text()))
        except (ValueError, TypeError):
            open_triggers = None
    when = generated_at or datetime.now(UTC).isoformat()
    report = build_ops_report(
        generated_at=when,
        runs=run_rows,
        progress=progress,
        courts=courts,
        usage=iter_usage(settings.data_root),
        flags=iter_flags(settings.data_root),
        tooling=iter_tooling(settings.data_root),
        previous=prior,
        data_health=data_health,
        scope_audit=scope_verdict,
        open_triggers=open_triggers,
    )
    if json_out is not None:
        write_json(json_out, report)
    if data_health_out is not None:
        data_health_out.parent.mkdir(parents=True, exist_ok=True)
        data_health_out.write_text(render_data_health(data_health))
    typer.echo(render_markdown(report), nl=False)


@app.command("export-schemas")
def export_schemas(
    out: Annotated[Path, typer.Argument(help="Output directory for JSON Schemas.")] = Path(
        "schemas"
    ),
) -> None:
    """Write JSON Schema for every model (for agents and Codex --output-schema)."""
    out.mkdir(parents=True, exist_ok=True)
    for name, model in EXPORTABLE_MODELS.items():
        write_raw_json(out / f"{name}.schema.json", model.model_json_schema())
    typer.echo(f"Exported {len(EXPORTABLE_MODELS)} schema(s) to {out}")


CorpusBackendOption = Annotated[
    str,
    typer.Option(
        "--corpus-backend",
        help="Corpus read backend: local (the dvc-pulled file) or ranged (query "
        "the blob in place on the DVC remote). Default: the corpus-backend "
        "setting from the environment.",
    ),
]


def _corpus_backend(value: str) -> corpus.CorpusBackend | None:
    """Parse a --corpus-backend value; empty means \"use the setting\"."""
    if not value:
        return None
    if value not in ("local", "ranged"):
        typer.echo(f"Unknown --corpus-backend '{value}'; choose local or ranged.", err=True)
        raise typer.Exit(code=2)
    return "local" if value == "local" else "ranged"


def _echo_read_stats(conn: corpus.ReadConnection) -> None:
    """Report a ranged connection's transfer counters to stderr.

    The per-query egress evidence: retrieval logging and the integration check
    read these numbers, and a human sees at a glance that a lookup moved KBs,
    not the blob. A no-op for the local backend (nothing was transferred).
    """
    if isinstance(conn, corpus_ranged.RangedConnection):
        stats = conn.stats
        typer.echo(
            f"ranged corpus reads: {stats.gets} GET(s), {stats.bytes_fetched} byte(s)",
            err=True,
        )


def _ensure_corpus_layout(db_path: Path) -> None:
    """Rebuild the corpus file to the ranged-read layout if it has drifted.

    Every corpus-writer command calls this before returning, so the file a
    workflow ``dvc add``s always satisfies the layout contract ``dvc-status``
    enforces (64 KB pages, non-WAL at rest) — the migration happens under the
    ``corpus-write`` lock the writer's job already holds.
    """
    if corpus.ensure_ranged_layout(db_path):
        typer.echo(
            f"corpus layout: rebuilt {db_path} to {corpus.RANGED_PAGE_SIZE}-byte pages, non-WAL"
        )


def _fetch_one_docket(court: str, docket: int) -> None:
    """Fetch one docket via REST and ingest it into the corpus (onboard/refresh)."""
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    with _client() as client:
        result = pull_case(client, db, settings.data_root, court, docket)
    _ensure_corpus_layout(db)
    typer.echo(
        f"{result.case_id} changed={result.changed} snapshot={result.snapshot} "
        f"resolved={len(result.resolved)} reconcile={len(result.reconcile)}"
    )


@app.command()
def seed(
    court: Annotated[str, typer.Option(help="CourtListener court id, e.g. ca9 or scotus.")],
    docket: Annotated[int, typer.Option(help="CourtListener docket id.")],
) -> None:
    """Onboard one docket from the CourtListener REST API into the corpus.

    Deterministic single-docket ingestion of raw facts: fetches the docket and
    upserts its normalized row into the corpus through the shared ingestion core.
    ``pull`` refreshes an already-onboarded docket. The historical mass is loaded
    separately by the bulk-data backfill (``seed-backfill`` / the ``run-seed``
    workflow); see ``docs/data-pipeline.md``.
    """
    _fetch_one_docket(court, docket)


@app.command()
def pull(
    court: Annotated[str, typer.Option(help="CourtListener court id, e.g. ca9 or scotus.")],
    docket: Annotated[int, typer.Option(help="CourtListener docket id.")],
) -> None:
    """Refresh one docket from the CourtListener REST API and report changes.

    The forward-freshness counterpart to ``seed``: re-fetches the docket,
    re-ingests it into the corpus through the shared core, and reports whether it
    changed since the last pull (the signal that downstream ``run-predict``
    should run).
    """
    _fetch_one_docket(court, docket)


@app.command("probe-recoverability")
def probe_recoverability(
    dockets: Annotated[
        list[str] | None,
        typer.Option(
            "--dockets",
            help="court/docket pair(s) to probe; repeatable and/or comma-separated, "
            "e.g. --dockets scotus/1000512,scotus/1000515.",
        ),
    ] = None,
    sample_dateless: Annotated[
        int,
        typer.Option(
            help="Instead of --dockets: probe a stratified random sample of this many "
            "resolved-but-dateless corpus rows (SCOTUS modern-cert / ca4 / other "
            "circuits). Needs the corpus on disk. Each docket costs ~2-3 REST requests.",
        ),
    ] = 0,
    seed: Annotated[
        int,
        typer.Option(help="PRNG seed for --sample-dateless; same corpus + seed = same draw."),
    ] = 0,
    report_out: Annotated[
        Path | None,
        typer.Option(
            help="Also write the machine ProbeReport JSON here (e.g. for an Actions "
            "artifact); it always goes to stdout regardless.",
        ),
    ] = None,
    summary_out: Annotated[
        Path | None,
        typer.Option(
            help="Append the Markdown summary here (e.g. $GITHUB_STEP_SUMMARY); "
            "the machine JSON always goes to stdout.",
        ),
    ] = None,
) -> None:
    """Probe whether sparse dockets' dispositions are recoverable from CourtListener.

    Strictly **read-only**: for each ``court/docket`` it fetches the docket, its
    entries, and any linked opinion cluster via the REST API and classifies the
    disposition as RECOVERABLE (an ingestion gap a seed/pull backfill can close),
    ABSENT (genuinely bare upstream), or AMBIGUOUS. Writes nothing — no corpus,
    ``data/``, DVC, or git (``--report-out`` writes only the report file named).
    Targets come from ``--dockets`` (ad-hoc pairs) or ``--sample-dateless N`` (a
    deterministic stratified sample of the resolved-but-dateless slice, sizing what
    a date backfill can recover per stratum; the summary then carries a per-stratum
    rollup and the corpus's dated share at probe time). Emits the machine
    ``ProbeReport`` JSON on stdout and a short human summary on stderr;
    ``--summary-out`` also appends the Markdown summary to a file. Needs the
    CourtListener REST token in the environment (it is dispatched by the diagnostic
    workflow, which holds it). See ``docs/cli.md``.
    """
    if bool(dockets) == (sample_dateless > 0):
        typer.echo("give exactly one of --dockets or --sample-dateless", err=True)
        raise typer.Exit(code=2)
    dated_share: tuple[int, int] | None = None
    if dockets:
        try:
            pairs = parse_docket_pairs(dockets)
        except ValueError as exc:
            typer.echo(f"bad --dockets value: {exc}", err=True)
            raise typer.Exit(code=2) from exc
        with _client() as client:
            report = probe_dockets(client, pairs)
    else:
        db_path = corpus.corpus_db_path(get_settings().corpus_root)
        if not db_path.exists():
            typer.echo(f"--sample-dateless needs the corpus at {db_path}", err=True)
            raise typer.Exit(code=2)
        with corpus.connect_readonly(db_path) as conn:
            targets = sample_dateless_targets(conn, total=sample_dateless, seed=seed)
            dated_share = dated_share_snapshot(conn)
        with _client() as client:
            report = probe_sample(client, targets)
    summary = render_summary(report, dated_share=dated_share)
    typer.echo(report.model_dump_json(indent=2))
    typer.echo(summary, err=True)
    if report_out is not None:
        write_raw_json(report_out, report.model_dump(mode="json"))
    if summary_out is not None:
        with summary_out.open("a", encoding="utf-8") as fh:
            fh.write(summary)


@app.command("seed-backfill")
def seed_backfill(
    max_cases: Annotated[
        int | None,
        typer.Option(
            help="Optional lower cap on cases to load this run; cannot exceed "
            "seed.max_cases_per_run."
        ),
    ] = None,
    report: Annotated[
        Path | None,
        typer.Option(help="Write progress JSON here for the tracking-issue comment."),
    ] = None,
    staging_path: Annotated[
        Path | None,
        typer.Option(
            help="Persist the staged snapshot here and reuse it on the next run. "
            "Lets a workflow loop many chunks without re-downloading/re-staging the "
            "GB-scale bulk files each time (the build is skipped when the snapshot id "
            "matches). Omit for a throwaway temp staging DB."
        ),
    ] = None,
) -> None:
    """Load the next chunk of CourtListener bulk data into the corpus (no agent).

    The deterministic historical backfill: reads the committed cursor
    (``config/seed-progress.yaml``), streams the next slice of the public bulk
    snapshot for the tracked courts (``config/tracking.yaml``), normalizes each
    row through the shared ingestion core into the packed corpus, and advances the
    cursor — all without spending the CourtListener REST budget. ``--max-cases``
    may only lower the per-run cap, never raise it. Idempotent: re-running after
    completion loads zero rows.

    ``--staging-path`` makes the heavy stage-once phase reusable: a workflow that
    loops ``seed-backfill`` over a persistent path pays the ~tens-of-minutes
    download+stage once per job, then each subsequent chunk is a cheap served read.
    """
    settings = get_settings()
    seed_cfg = load_seed_config(settings.config_root)
    courts = load_courts(settings.config_root)
    cap = (
        seed_cfg.max_cases_per_run
        if max_cases is None
        else min(max_cases, seed_cfg.max_cases_per_run)
    )
    if not settings.courtlistener_bulk_url:
        typer.echo(
            "No bulk snapshot URL configured; seed-backfill has no source to load and is a no-op.",
            err=True,
        )
        raise typer.Exit(code=2)

    snapshot_id, dockets_url = resolve_dockets_source(
        settings.courtlistener_bulk_url,
        timeout=settings.request_timeout,
    )
    # The dockets file is the case spine; sibling bulk files enrich each row via the
    # staged join — opinion-clusters (disposition/summary/judges/precedential-status/
    # citation-count + the people-resolved panel), and the parties / attorneys name
    # lists. A non-standard pinned dockets URL has no derivable siblings, so the
    # spine still loads and those fields stay blank.
    source = CourtListenerBulkSource(
        snapshot_id,
        dockets_url=dockets_url,
        courts=courts,
        clusters_url=sibling_bulk_url(dockets_url, "opinion-clusters"),
        parties_url=sibling_bulk_url(dockets_url, "parties"),
        attorneys_url=sibling_bulk_url(dockets_url, "attorneys"),
        people_url=sibling_bulk_url(dockets_url, "people-db-people"),
        timeout=settings.request_timeout,
        staging_path=staging_path,
    )
    try:
        rep = backfill(
            source,
            cursor_path=seed_cfg.cursor,
            courts=courts,
            corpus_db_path=corpus.corpus_db_path(settings.corpus_root),
            max_cases=cap,
        )
    finally:
        source.cleanup()

    _ensure_corpus_layout(corpus.corpus_db_path(settings.corpus_root))
    if report is not None:
        write_raw_json(report, rep.model_dump(mode="json"))
    typer.echo(
        f"seed-backfill snapshot={rep.snapshot} loaded_this_run={rep.loaded_this_run} "
        f"complete={rep.complete}"
    )


@app.command("full-refresh")
def full_refresh_cmd(
    dry_run: Annotated[
        bool,
        typer.Option(help="Report what would be reset without writing anything."),
    ] = False,
    report: Annotated[
        Path | None,
        typer.Option(help="Write the RefreshReport JSON here for the run summary."),
    ] = None,
) -> None:
    """Reset the pipeline's forward state for a clean rebuild (no agent, no data loss).

    The operator escape hatch for a structural change to how data is produced — a
    new corpus column, a corrected normalization, a data-validity fix best solved
    by rebuilding from source. Resets the seed cursor (``config/seed-progress.yaml``)
    so the next ``seed-backfill`` re-loads every court from the top, clears each
    case's ``last_pulled`` so ``pull`` re-pulls the active set, and resets each
    court's discovery watermark to the snapshot frontier so discovery re-walks the
    post-snapshot range — re-ingesting cases that resolved after the snapshot, which
    ``pull`` alone would skip. Re-ingestion never reopens a resolved event.

    History is preserved, not dropped: corpus case/event/snapshot rows and the git
    ledger under ``data/`` stay in place (recoverable via the content-addressed DVC
    blob under a no-delete remote and git history of the pointer / ledger).
    ``--dry-run`` reports the blast radius without writing. Run inside the run-seed
    workflow (it holds the corpus-write lock and pushes the reset corpus blob); see
    ``docs/data-pipeline.md``.
    """
    settings = get_settings()
    seed_cfg = load_seed_config(settings.config_root)
    rep = run_full_refresh(
        cursor_path=seed_cfg.cursor,
        corpus_db_path=corpus.corpus_db_path(settings.corpus_root),
        dry_run=dry_run,
    )
    if not dry_run:
        _ensure_corpus_layout(corpus.corpus_db_path(settings.corpus_root))
    if report is not None:
        write_raw_json(report, rep.model_dump(mode="json"))
    verb = "would reset" if dry_run else "reset"
    since = f" to re-discover from {rep.rediscover_since}" if rep.rediscover_since else ""
    note = "" if rep.corpus_present else " (no corpus present — run after `dvc pull`)"
    typer.echo(
        f"full-refresh: {verb} {rep.courts_reset} court(s) for re-seed; cleared "
        f"last_pulled on {rep.cases_unpulled} case(s) and reset {rep.watermarks_reset} "
        f"discovery watermark(s){since}{note}"
    )


@app.command("make-fixture-corpus")
def make_fixture_corpus(
    out: Annotated[
        Path | None,
        typer.Option(
            help="Where to write the fixture corpus DB; defaults to the configured corpus path."
        ),
    ] = None,
) -> None:
    """Build a tiny deterministic synthetic corpus for offline local runs.

    The local read loop (`provision-snapshot`, `query`, `open-events`, …) reads
    the packed corpus, which in production is a `dvc pull` of the S3 remote behind
    OIDC — unreachable from a laptop. This builds a small, fully synthetic corpus
    from hard-coded facts instead: a handful of cases across several courts, a mix
    of resolved and open, with their predictable events and dated snapshots, so
    those commands work with no remote, token, or network. Overwrites any file at
    the destination so the build is reproducible run to run. Synthetic data only —
    never a substitute for the real corpus the data workflows produce.
    """
    settings = get_settings()
    dest = out if out is not None else corpus.corpus_db_path(settings.corpus_root)
    build_fixture_corpus(dest)
    with corpus.connect(dest) as conn:
        typer.echo(
            f"fixture corpus -> {dest}: {corpus.count(conn)} case(s), "
            f"{corpus.event_count(conn)} event(s), {corpus.snapshot_count(conn)} snapshot(s)"
        )


@app.command("corpus-info")
def corpus_info(corpus_backend: CorpusBackendOption = "") -> None:
    """Show the corpus location and row count (after `dvc pull`, or ranged)."""
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend == "local" and not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `dvc pull` to fetch it from the remote.")
        return
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        typer.echo(
            f"corpus {db_path} [{backend}]: {corpus.count(conn)} row(s), "
            f"{corpus.snapshot_count(conn)} snapshot(s)"
        )
        _echo_read_stats(conn)


@app.command()
def query(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to the query filters
    court: Annotated[str, typer.Option(help="Restrict to one CourtListener court id.")] = "",
    topic: Annotated[str, typer.Option(help="Exact nature-of-suit / subject topic.")] = "",
    judge: Annotated[
        list[str] | None,
        typer.Option(help="Judge name; repeatable. Matches cases sharing any given judge."),
    ] = None,
    citation: Annotated[
        list[str] | None,
        typer.Option(help="Citation; repeatable. Matches cases citing any given authority."),
    ] = None,
    disposition: Annotated[
        str, typer.Option(help="Restrict to one realized outcome label, e.g. granted.")
    ] = "",
    era: Annotated[
        str,
        typer.Option(
            help="Restrict to one decade era, e.g. 1890s — retrieve priors from "
            "the case's own period (derived from Term year or filing/decision date)."
        ),
    ] = "",
    decided_before: Annotated[
        int,
        typer.Option(
            help="Exclusive year cutoff for back-test replays: keep only priors "
            "whose best-known year strictly precedes it (rows with no derivable "
            "year are excluded). 0 = no cutoff (the live, forward view)."
        ),
    ] = 0,
    include_open: Annotated[
        bool, typer.Option(help="Include unresolved cases (default: decided priors only).")
    ] = False,
    limit: Annotated[
        int, typer.Option(help="Maximum priors to return.")
    ] = corpus.DEFAULT_PRIOR_LIMIT,
    full: Annotated[
        bool, typer.Option(help="Include each prior's full opinion_text (omitted by default).")
    ] = False,
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Retrieve relevant priors from the corpus, most relevant first.

    Precedent retrieval for predictors: pull a handful of similar resolved cases
    by structured filter instead of loading the bulk set. ``--court`` / ``--topic``
    / ``--disposition`` match exactly; ``--judge`` and ``--citation`` (repeatable)
    match on overlap and rank the results by how much they share. Prints one
    compact JSON row per line, ranked, with ``opinion_text`` omitted unless
    ``--full``. Reads the ``dvc pull``-ed file, or the blob in place on the
    remote with ``--corpus-backend ranged``. Semantic search lands later on the
    same query seam.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend == "local" and not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `dvc pull` to fetch it from the remote.", err=True)
        raise typer.Exit(code=1)
    try:
        disp = Disposition(disposition) if disposition else None
    except ValueError as exc:
        choices = ", ".join(d.value for d in Disposition)
        typer.echo(f"Unknown disposition '{disposition}'; choose one of: {choices}", err=True)
        raise typer.Exit(code=2) from exc
    q = corpus.PriorQuery(
        court=court or None,
        topic=topic or None,
        judges=judge or [],
        citations=citation or [],
        disposition=disp,
        era=era or None,
        decided_before=decided_before or None,
        resolved_only=not include_open,
    )
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        priors = corpus.retrieve_priors(conn, q, limit=limit)
        _echo_read_stats(conn)
    for row in priors:
        payload = row.model_dump(mode="json")
        # Era is derived, not stored; carry it on each prior so relevance is
        # judgeable without re-deriving.
        payload["era"] = corpus.case_era(row)
        if not full:
            payload.pop("opinion_text", None)
        typer.echo(json.dumps(payload, sort_keys=True, separators=(",", ":")))


@app.command()
def stats(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to the query filters
    court: Annotated[str, typer.Option(help="Restrict to one CourtListener court id.")] = "",
    topic: Annotated[str, typer.Option(help="Exact nature-of-suit / subject topic.")] = "",
    judge: Annotated[
        list[str] | None,
        typer.Option(help="Judge name; repeatable. Matches cases sharing any given judge."),
    ] = None,
    citation: Annotated[
        list[str] | None,
        typer.Option(help="Citation; repeatable. Matches cases citing any given authority."),
    ] = None,
    disposition: Annotated[
        str, typer.Option(help="Restrict to one realized outcome label, e.g. granted.")
    ] = "",
    date_from: Annotated[
        str, typer.Option(help="Keep cases filed on/after this ISO date, e.g. 2020-01-01.")
    ] = "",
    date_to: Annotated[str, typer.Option(help="Keep cases filed on/before this ISO date.")] = "",
    term: Annotated[
        str,
        typer.Option(
            help="Restrict to one SCOTUS October-Term year (parsed from the docket "
            "number), e.g. 2024. A Term is a SCOTUS concept, so this keeps SCOTUS "
            "cases only; other courts' dockets never match."
        ),
    ] = "",
    era: Annotated[
        str,
        typer.Option(
            help="Keep cases in one decade era, e.g. 1890s (derived from Term year "
            "or filing/decision date) — usable on exactly the historical rows "
            "--term cannot parse."
        ),
    ] = "",
    cert_stage: Annotated[
        bool,
        typer.Option(
            "--cert-stage",
            help="Keep only modern Term-prefixed discretionary-cert SCOTUS dockets, "
            "so the base rate reflects the population the cert model predicts.",
        ),
    ] = False,
    resolved_only: Annotated[
        bool, typer.Option(help="Drop unresolved cases (default keeps them for the open count).")
    ] = False,
    group_by: Annotated[
        str,
        typer.Option(
            help="Break base-rates down by a dimension: court, topic, judge, "
            "term_year, disposition, originating_court, or era. Omit for the "
            "overall base rate only."
        ),
    ] = "",
    summary_out: Annotated[
        Path | None,
        typer.Option(
            help="Append the Markdown summary here (e.g. $GITHUB_STEP_SUMMARY); "
            "the machine JSON always goes to stdout.",
        ),
    ] = None,
) -> None:
    """Aggregate corpus disposition base-rates, overall and by a dimension (run after `dvc pull`).

    The aggregate counterpart of `query`: instead of returning individual priors it
    rolls the whole matched set into base-rates — how the realized dispositions split,
    overall and (with `--group-by`) per court / topic / judge / SCOTUS Term / disposition.
    Shares the `query` filter grammar (`--court` / `--topic` / `--disposition` match
    exactly; `--judge` / `--citation` match on overlap), plus a `--date-from` / `--date-to`
    filed-date window. Strictly read-only. Emits the machine `AnalyticsReport` JSON on
    stdout and a Markdown summary on stderr; `--summary-out` also appends the Markdown.
    Graceful when the corpus is absent (writes a skipped report and exits 0).
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    try:
        disp = Disposition(disposition) if disposition else None
    except ValueError as exc:
        choices = ", ".join(d.value for d in Disposition)
        typer.echo(f"Unknown disposition '{disposition}'; choose one of: {choices}", err=True)
        raise typer.Exit(code=2) from exc
    try:
        dimension = GroupBy(group_by) if group_by else None
    except ValueError as exc:
        choices = ", ".join(g.value for g in GroupBy)
        typer.echo(f"Unknown --group-by '{group_by}'; choose one of: {choices}", err=True)
        raise typer.Exit(code=2) from exc
    try:
        parsed_from = date.fromisoformat(date_from) if date_from else None
        parsed_to = date.fromisoformat(date_to) if date_to else None
    except ValueError as exc:
        typer.echo(f"Bad date (expected ISO YYYY-MM-DD): {exc}", err=True)
        raise typer.Exit(code=2) from exc
    try:
        parsed_term = int(term) if term else None
    except ValueError as exc:
        typer.echo(f"Bad --term '{term}' (expected a year, e.g. 2024).", err=True)
        raise typer.Exit(code=2) from exc
    query = analytics.AnalyticsQuery(
        court=court or None,
        topic=topic or None,
        judges=judge or [],
        citations=citation or [],
        disposition=disp,
        date_from=parsed_from,
        date_to=parsed_to,
        term=parsed_term,
        era=era or None,
        cert_stage=cert_stage,
        resolved_only=resolved_only,
        group_by=dimension,
    )
    report = analytics.run_analytics(corpus_db_path=db_path, query=query)
    summary = analytics.render_markdown(report)
    typer.echo(report.model_dump_json(indent=2))
    typer.echo(summary, err=True)
    if summary_out is not None:
        with summary_out.open("a", encoding="utf-8") as fh:
            fh.write(summary)


@app.command()
def predictors() -> None:
    """List configured predictors."""
    settings = get_settings()
    for p in load_predictors(settings.config_root / "predictors.yaml"):
        flag = "" if p.enabled else " (disabled)"
        typer.echo(f"{p.id}\t{p.engine}\t{p.model or '-'}{flag}")


@app.command()
def evaluators() -> None:
    """List configured evaluators."""
    settings = get_settings()
    for e in load_evaluators(settings.config_root / "evaluators.yaml"):
        flag = "" if e.enabled else " (disabled)"
        typer.echo(f"{e.id}\t{e.engine}\t{e.model or '-'}{flag}")


@app.command()
def paths(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Optional event id to resolve event paths.")] = "",
) -> None:
    """Print resolved paths for a case (or event). Useful in scripts.

    Raw facts live in the packed corpus, not per-case git files; git holds only
    the derived ledger (events, outcomes, predictions, evaluations).
    """
    settings = get_settings()
    cp = CasePaths(settings.data_root, court, docket)
    typer.echo(f"case_id   {ids.case_id(court, docket)}")
    typer.echo(f"corpus    {corpus.corpus_db_path(settings.corpus_root)}")
    if event:
        ep = cp.event(event)
        typer.echo(f"event     {ep.event_file}")
        typer.echo(f"outcome   {ep.outcome}")


@app.command("provision-snapshot")
def provision_snapshot(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    out: Annotated[
        Path | None,
        typer.Option(help="Where to write the snapshot; defaults to the case's record path."),
    ] = None,
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Materialize a case's latest corpus snapshot to disk for an agent run.

    Point-in-time snapshots are raw facts that live in the packed corpus, not
    git. The predict/evaluate/reconcile workflows call this to read the most
    recent dated snapshot for the case out of the corpus — the ``dvc pull``-ed
    file, or the blob in place on the remote with ``--corpus-backend ranged`` —
    and write it where the agent reads it (a gitignored ``record/`` path, never
    committed). Exits non-zero if the corpus holds no snapshot for the case.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    case = ids.case_id(court, docket)
    backend = _corpus_backend(corpus_backend)
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        found = corpus.latest_snapshot(conn, case)
        _echo_read_stats(conn)
    if found is None:
        typer.echo(f"No snapshot in corpus for {case} (dvc pull the corpus first?)", err=True)
        raise typer.Exit(code=1)
    snapshot_date, payload = found
    dest = out or CasePaths(settings.data_root, court, docket).snapshot(snapshot_date.isoformat())
    write_raw_json(dest, payload)
    typer.echo(f"{case} snapshot {snapshot_date.isoformat()} -> {dest}")


@app.command("corpus-integration-check")
def corpus_integration_check(
    court: Annotated[str, typer.Option(help="Court id of the known case the read set targets.")],
    docket: Annotated[int, typer.Option(help="Docket id of the known case.")],
    limit: Annotated[int, typer.Option(help="Priors to retrieve in the query step.")] = 5,
    budget_seconds: Annotated[
        float, typer.Option(help="Wall-clock budget for the whole read set.")
    ] = 300.0,
    snapshot_out: Annotated[
        Path | None,
        typer.Option(help="Also materialize the provisioned snapshot here."),
    ] = None,
    summary_out: Annotated[
        Path | None,
        typer.Option(
            help="Append the Markdown summary here (e.g. $GITHUB_STEP_SUMMARY); "
            "the machine JSON always goes to stdout.",
        ),
    ] = None,
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Run the fixed corpus read set; fail on an empty result or a blown budget.

    The integration-corpus workflow's engine: a point lookup (the case's open
    events), a priors retrieval (a narrow indexed filter over the case's
    court), and a snapshot provisioning, each on its own read connection so a
    ranged run reports per-read GET/byte transfer counters (see
    ``fedcourtsai.integration_check``). Emits the machine report JSON on stdout
    and the Markdown summary on stderr; ``--summary-out`` also appends the
    Markdown. Exits non-zero when any read comes back empty or the set blows
    the wall-clock budget — the signature of a scan or a cache regression, not
    a slow network day.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend == "local" and not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `dvc pull` to fetch it from the remote.", err=True)
        raise typer.Exit(code=1)
    report = integration_check.run_integration_check(
        corpus_db_path=db_path,
        court=court,
        docket=docket,
        limit=limit,
        budget_seconds=budget_seconds,
        backend=backend,
        snapshot_out=snapshot_out,
    )
    summary = integration_check.render_markdown(report)
    typer.echo(report.model_dump_json(indent=2))
    typer.echo(summary, err=True)
    if summary_out is not None:
        with summary_out.open("a", encoding="utf-8") as fh:
            fh.write(summary)
    if not report.ok:
        raise typer.Exit(code=1)


@app.command("local-cascade")
def local_cascade(
    court: Annotated[str, typer.Option(help="CourtListener court id, e.g. ca9 or scotus.")],
    docket: Annotated[int, typer.Option(help="CourtListener docket id.")],
    event: Annotated[
        str,
        typer.Option(help="Event id to run; default: every event the case defines."),
    ] = "",
    engine: Annotated[
        str,
        typer.Option(
            help="Engine backend: stub (offline, default) | replay (offline, recorded "
            "cassette) | claude-code | codex."
        ),
    ] = "stub",
    run_id: Annotated[
        str, typer.Option(help="Shared run id for the cells; defaults to now (UTC).")
    ] = "",
) -> None:
    """Run the full predict → evaluate → validate cascade for one case locally.

    The repeatable, local form of the "one full cascade proven" milestone: over
    the fixture corpus (or a real provisioned one) it provisions the snapshot,
    materializes the git event/outcome definitions, fans the chosen engine out
    over the enabled predictors then evaluators, and validates the produced
    ledger — the iteration loop that otherwise only runs inside Actions. Corpus
    reads honor the corpus-backend setting, so a ``ranged``-configured
    environment runs the cascade against the remote blob with no local pull.

    ``--engine stub`` (the default) is deterministic, offline, and token-free.
    ``--engine replay`` is also offline but emits a captured real prediction from
    the cassette at ``FEDCOURTS_REPLAY_ROOT`` (see ``tests/cassettes``), so the
    scoring and leaderboard consumers run over realistic output rather than the stub
    floor. ``--engine claude-code`` / ``--engine codex`` drive the real headless agents
    against the same env-var + prompt contract the workflows use; auth is inherited
    from the environment (for Claude, ``ANTHROPIC_API_KEY`` or the subscription
    ``CLAUDE_CODE_OAUTH_TOKEN`` from ``claude setup-token``). Writes derived
    artifacts under ``data/`` exactly as a real run would — review and discard them
    rather than committing a local cascade's output. See ``docs/cli.md``.
    """
    settings = get_settings()
    try:
        report = run_cascade(
            corpus_db_path=corpus.corpus_db_path(settings.corpus_root),
            data_root=settings.data_root,
            config_root=settings.config_root,
            court=court,
            docket=docket,
            event=event or None,
            engine=engine,
            run_id=run_id or ids.run_id(),
        )
    except KeyError as exc:
        # Unknown engine backend (get_runner names the available ones).
        typer.echo(str(exc).strip("\"'"), err=True)
        raise typer.Exit(code=2) from exc
    except (CascadeError, EngineUnavailable) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except EngineFailed as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"local-cascade {report.case_id} via {report.engine} (run {report.run_id})")
    typer.echo(f"  events:      {', '.join(report.events)}")
    typer.echo(f"  snapshot:    {report.snapshot or 'none in corpus'}")
    typer.echo(f"  predictions: {len(report.predictions)} file(s)")
    typer.echo(f"  outcomes:    {len(report.outcomes)} file(s)")
    typer.echo(f"  evaluations: {len(report.evaluations)} file(s)")
    if not report.valid:
        typer.echo("  validate:    FAILED", err=True)
        for problem in report.problems:
            typer.echo(f"    {problem}", err=True)
        raise typer.Exit(code=1)
    typer.echo("  validate:    OK")


@app.command("materialize-event")
def materialize_event(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id to materialize from the corpus.")],
    out: Annotated[
        Path | None,
        typer.Option(help="Where to write event.yaml; defaults to the event's ledger path."),
    ] = None,
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Materialize a predictable event's ``event.yaml`` from the corpus into the ledger.

    Forward discovery records predictable events as raw facts in the packed corpus,
    not as per-case ``event.yaml`` files. But a prediction committed under an event
    directory needs its ``event.yaml`` beside it so the offline PR gate
    (``validate``) can confirm the judgment references a real event without the
    corpus remote. The predict/evaluate cells call this to project the corpus event
    row into the committed git ledger; like their other corpus reads it honors the
    configured read backend, so a ranged cell queries the remote blob in place (a
    local-only open would silently create an empty corpus and find no events).
    Exits non-zero if the corpus holds no such event for the case.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend == "local" and not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `dvc pull` to fetch it from the remote.", err=True)
        raise typer.Exit(code=1)
    case = ids.case_id(court, docket)
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        match = next((e for e in corpus.events_for_case(conn, case) if e.event_id == event), None)
        _echo_read_stats(conn)
    if match is None:
        typer.echo(
            f"No event {event!r} in corpus for {case} (dvc pull the corpus first?)", err=True
        )
        raise typer.Exit(code=1)
    dest = out or CasePaths(settings.data_root, court, docket).event(event).event_file
    write_yaml(
        dest,
        PredictableEvent(
            event_id=match.event_id,
            case_id=match.case_id,
            kind=match.kind,
            title=match.title,
            description=match.description,
            docket_entry_id=match.docket_entry_id,
            opened_at=match.opened_at,
            decision_target=match.decision_target,
            resolved=match.resolved,
        ),
    )
    typer.echo(f"{case} event {event} -> {dest}")


@app.command("open-events")
def open_events_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Print unresolved (predictable) event ids for a case, one per line."""
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    for eid in open_events(db, court, docket, backend=_corpus_backend(corpus_backend)):
        typer.echo(eid)


def _format_discovery_failures(failed: list[dict[str, object]]) -> str:
    """Render discovery casualties as a parenthetical with each court's reason.

    ``discover_cases`` records the per-court failure ``reason`` (exception type +
    message) on ``DiscoverResult.failed``; surface it in the ``pull-all`` echo so a
    timeout vs. throttle vs. 5xx is visible from the run log without opening raw
    traces. Empty when no court failed, so it appends cleanly to the count line.
    """
    if not failed:
        return ""
    courts = ", ".join(f"{f['court']} [{f['reason']}]" for f in failed)
    return f" ({len(failed)} court(s) failed: {courts})"


def _format_refresh_failures(failed: list[dict[str, object]]) -> str:
    """Render refresh casualties as a parenthetical with each case's reason.

    The per-case counterpart to :func:`_format_discovery_failures`: surfaces
    which dockets failed and why in the ``pull-all`` summary line, so a run of
    upstream timeouts is diagnosable from the run log alone.
    """
    if not failed:
        return ""
    cases = ", ".join(f"{f['court']}/{f['docket']} [{f['reason']}]" for f in failed)
    return f" ({len(failed)} failed: {cases})"


@app.command("pull-all")
def pull_all(
    out: Annotated[Path, typer.Option(help="Write the predict queue JSON here.")] = Path(
        "predict-queue.json"
    ),
    evaluate_out: Annotated[
        Path, typer.Option(help="Write the evaluate queue JSON here (newly resolved events).")
    ] = Path("evaluate-queue.json"),
    reconcile_out: Annotated[
        Path, typer.Option(help="Write the reconcile queue JSON here (decided but not readable).")
    ] = Path("reconcile-queue.json"),
    limit: Annotated[
        int | None,
        typer.Option(
            help="Optional lower cap on cases to refresh this run; cannot exceed "
            "pull.max_cases_per_run."
        ),
    ] = None,
) -> None:
    """Refresh the stalest tracked cases within budget; queue downstream handoffs.

    The API-budget governor: rotation picks the oldest-``last_pulled``-first slice
    of the active set (skipping closed/resolved cases), capped at
    ``pull.max_cases_per_run`` from ``config/tracking.yaml``. ``--limit`` may only
    lower that cap for a one-off run, never raise it, so a run provably stays
    within the CourtListener budget.

    Each refresh also detects resolution of open events, writing ``outcome.json``
    deterministically. The command writes three queues for the workflow to act on:
    ``predict`` (changed cases with open events), ``evaluate`` (cases that gained
    an ``outcome.json`` this run), and ``reconcile`` (cases that appear decided but
    whose outcome an agent must confirm by hand).

    The whole run is bounded by ``pull.max_run_minutes`` of wall clock: when the
    deadline (or the API budget, or the consecutive-transient-failure breaker)
    trips, the run stops where it is, defers the unreached cases to the next
    window's rotation, and still writes its queues — so a degraded upstream can
    never hang the job into its CI timeout and lose the window's work.

    ``pull.backfill_reserve`` carves part of the cap for the interim **date
    backfill** (:func:`fedcourtsai.corpus.backfill_rotation`): dockets whose rows
    lack every decision-time date, fetched after the live rotation under the same
    deadline and budget. A backfill docket feeds only the ``reconcile`` queue —
    its outcome is already known upstream, so it must not spend predict tokens,
    and it has no predictions to evaluate.
    """
    settings = get_settings()
    pull_cfg = load_pull_config(settings.config_root)
    scope = load_predict_config(settings.config_root).scope
    cap = pull_cfg.max_cases_per_run if limit is None else min(limit, pull_cfg.max_cases_per_run)
    deadline = time.monotonic() + pull_cfg.max_run_minutes * 60
    db = corpus.corpus_db_path(settings.corpus_root)
    with _client() as client:
        if pull_cfg.discover_new_filings:
            disc = discover_cases(
                client,
                db,
                load_courts(settings.config_root),
                max_new=pull_cfg.max_new_cases_per_run,
                default_since=date.today(),
                deadline=deadline,
            )
            disc_failed = _format_discovery_failures(disc.failed)
            disc_stopped = f"; stopped early: {disc.stopped}" if disc.stopped else ""
            typer.echo(
                f"Discovered {disc.total} new case(s) before refresh{disc_failed}{disc_stopped}"
            )
        # The date backfill carves its reserve out of the run cap (total REST
        # spend is unchanged); the live rotation keeps the rest and runs first —
        # forward freshness is the mission, the backfill is the opportunistic
        # drain of the dateless pool.
        backfill_due = cases_due_for_backfill(
            db,
            limit=min(pull_cfg.backfill_reserve, cap),
            unresolved_cert_min_term=pull_cfg.backfill_unresolved_cert_min_term,
        )
        # Rotation reads after discovery so freshly-onboarded cases are eligible.
        due = cases_due_for_pull(
            db,
            limit=cap - len(backfill_due),
            skip_closed=pull_cfg.skip_closed,
            eligible_reserve=pull_cfg.eligible_refresh_reserve,
        )
        # An unresolved cert shell can surface in both selectors; the rotation
        # keeps it (a rotation refresh retains its predict-queue rights).
        backfill_due = [pair for pair in backfill_due if pair not in set(due)]
        queues = pull_cases(
            client,
            db,
            settings.data_root,
            due,
            scope=scope,
            deadline=deadline,
            max_consecutive_transient_failures=pull_cfg.max_consecutive_transient_failures,
        )
        backfill_queues = PullQueues()
        if backfill_due and queues.stopped is None:
            backfill_queues = pull_cases(
                client,
                db,
                settings.data_root,
                backfill_due,
                scope=scope,
                deadline=deadline,
                max_consecutive_transient_failures=pull_cfg.max_consecutive_transient_failures,
            )
        elif backfill_due:
            # The rotation already exhausted the window; the backfill pool keeps
            # its place (nothing was stamped) and drains on a later run.
            backfill_queues.stopped = queues.stopped
            backfill_queues.deferred = [{"court": c, "docket": d} for c, d in backfill_due]
    _ensure_corpus_layout(db)
    # The backfill batch feeds only `reconcile` downstream: its dockets are
    # decided-upstream historical matters, so a `predict` entry would spend live
    # tokens on a known outcome, and an `evaluate` entry has no predictions to
    # score — recording ground truth is the batch's whole point.
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    reconcile_out.write_text(json.dumps(queues.reconcile + backfill_queues.reconcile) + "\n")
    refreshed = len(due) - len(queues.failed) - len(queues.deferred)
    typer.echo(
        f"Refreshed {refreshed}/{cap} case(s){_format_refresh_failures(queues.failed)}; "
        f"queued {len(queues.predict)} predict, {len(queues.evaluate)} evaluate, "
        f"{len(queues.reconcile) + len(backfill_queues.reconcile)} reconcile."
    )
    if backfill_due or pull_cfg.backfill_reserve:
        backfilled = len(backfill_due) - len(backfill_queues.failed) - len(backfill_queues.deferred)
        typer.echo(
            f"Backfill: fetched {backfilled}/{len(backfill_due)} dateless case(s)"
            f"{_format_refresh_failures(backfill_queues.failed)}; "
            f"{len(backfill_queues.evaluate)} resolved, "
            f"{len(backfill_queues.reconcile)} for reconcile."
        )
    stopped = queues.stopped or backfill_queues.stopped
    if stopped:
        deferred = len(queues.deferred) + len(backfill_queues.deferred)
        typer.echo(f"Stopped early ({stopped}); deferred {deferred} case(s) to the next rotation.")


@app.command()
def discover(
    since: Annotated[
        str,
        typer.Option(
            help="ISO date to start a never-discovered court from (default: today). "
            "Courts with a stored watermark resume from it regardless. Normally a "
            "court is seeded first (seed hands off the snapshot date as its initial "
            "watermark), so pass --since only for a never-seeded court; the today "
            "default is a last resort that discovers nothing useful on its own."
        ),
    ] = "",
    limit: Annotated[
        int | None,
        typer.Option(
            help="Optional lower cap on new dockets onboarded this run; cannot "
            "exceed pull.max_new_cases_per_run."
        ),
    ] = None,
) -> None:
    """Onboard newly-filed dockets in the tracked courts into the corpus.

    Forward discovery: for each tracked court, fetch dockets filed since its
    watermark, upsert the normalized docket and its predictable event(s) into the
    corpus, and advance the watermark — all raw facts, never per-case git files.
    Stays within the API budget via ``pull.max_new_cases_per_run`` (``--limit``
    may only lower it for a one-off run).
    """
    settings = get_settings()
    pull_cfg = load_pull_config(settings.config_root)
    courts = load_courts(settings.config_root)
    cap = (
        pull_cfg.max_new_cases_per_run
        if limit is None
        else min(limit, pull_cfg.max_new_cases_per_run)
    )
    start = date.fromisoformat(since) if since else date.today()
    db = corpus.corpus_db_path(settings.corpus_root)
    with _client() as client:
        result = discover_cases(client, db, courts, max_new=cap, default_since=start)
    for cd in result.courts:
        typer.echo(f"{cd.court}\tonboarded={cd.onboarded}\twatermark={cd.watermark}")
    typer.echo(f"Discovered {result.total}/{cap} new case(s) across {len(courts)} court(s)")


def _resolve_cases(
    cases: list[CaseRequest], default_events: Callable[[str, int], list[str]]
) -> list[CaseRequest]:
    """Fill in each case's default events when the request listed none."""
    return [
        c if c.events else CaseRequest(c.court, c.docket, tuple(default_events(c.court, c.docket)))
        for c in cases
    ]


def _scope_filtered(
    cases: list[CaseRequest], scope: PredictScope, corpus_root: Path
) -> list[CaseRequest]:
    """Drop out-of-scope cases under ``scotus_touched``; the matrix backstop.

    A manually-filed predict/evaluate issue cannot bypass the gate the pull
    queueing applies: eligibility is read from the corpus' latched
    ``predict_eligible`` flag, and an out-of-scope case is dropped with a visible
    note (to stderr, so the matrix JSON on stdout stays clean) explaining why a
    manual run produced an empty matrix. ``scope == all`` passes every case
    through unchanged.

    A SCOTUS-eligible case is still dropped when the shared exclusion reasoning
    matches it: the reconcile's ``predict_excluded`` latch, or any reason from
    ``corpus.out_of_scope_reason_full`` (the row rules — era, staleness, docket
    form, date consistency — plus the snapshot-aware bare opinion-import rule),
    with the reason echoed per case. The eligibility latch stays a pure
    "SCOTUS-touched" signal; these filters layer on top here so ingestion
    coverage is unaffected.

    Gating reads the corpus, so the corpus database must be on disk. If it is
    absent the gate cannot distinguish "case not eligible" from "corpus never
    provisioned" — :func:`corpus.connect` would silently create an empty database
    and drop *every* case, producing an empty matrix that looks like a normal
    "nothing in scope" result. Fail loud instead, so a planning job that forgot to
    ``dvc pull`` the corpus aborts visibly rather than silently predicting nothing.
    """
    if scope == PredictScope.all:
        return cases
    db_path = corpus.corpus_db_path(corpus_root)
    if not db_path.exists():
        typer.echo(
            f"prediction scope is '{scope.value}' but the corpus database is missing at "
            f"{db_path}; provision it (dvc pull) before planning the matrix.",
            err=True,
        )
        raise typer.Exit(code=1)
    kept: list[CaseRequest] = []
    with corpus.connect(db_path) as conn:
        for case in cases:
            row = corpus.get_row(conn, ids.case_id(case.court, case.docket))
            if row is None or not row.predict_eligible:
                typer.echo(
                    f"Skipping {case.court}/{case.docket}: out of prediction scope "
                    f"(predict.scope=scotus_touched, not SCOTUS-eligible).",
                    err=True,
                )
            elif row.predict_excluded:
                typer.echo(
                    f"Skipping {case.court}/{case.docket}: latched out of predict scope "
                    f"by the corpus reconcile.",
                    err=True,
                )
            elif (reason := corpus.out_of_scope_reason_full(conn, row)) is not None:
                typer.echo(f"Skipping {case.court}/{case.docket}: {reason}.", err=True)
            else:
                kept.append(case)
    return kept


def _requested_cases(
    body_file: Path | None, court: str, docket: int | None, event: list[str] | None
) -> list[CaseRequest]:
    """Cases to fan out over, from a batch body file or single-case flags.

    ``--body-file`` (one ``{court, docket, events}`` object or a JSON array of
    them) is the multi-case path the workflows use. The single-case
    ``--court``/``--docket``/``--event`` flags are kept for back-compat and
    ad-hoc invocations.
    """
    if body_file is not None:
        return parse_cases(body_file.read_text())
    if court and docket is not None:
        return [CaseRequest(court, docket, tuple(event or ()))]
    raise typer.BadParameter("provide --body-file, or both --court and --docket.")


@app.command("predict-matrix")
def predict_matrix_cmd(
    run_id: Annotated[str, typer.Option(help="Shared run id for this fan-out.")],
    body_file: Annotated[
        Path | None,
        typer.Option(help="Issue body file; its ```json block (one case or an array) is parsed."),
    ] = None,
    court: Annotated[
        str, typer.Option(help="Single-case court id (ignored with --body-file).")
    ] = "",
    docket: Annotated[
        int | None, typer.Option(help="Single-case docket id (ignored with --body-file).")
    ] = None,
    event: Annotated[
        list[str] | None, typer.Option(help="Single-case event id(s); default: all open events.")
    ] = None,
) -> None:
    """Emit the predictor x case x event GitHub Actions matrix as compact JSON.

    A case with no listed ``events`` defaults to that case's open events.
    """
    settings = get_settings()
    scope = load_predict_config(settings.config_root).scope
    cases = _resolve_cases(
        _scope_filtered(
            _requested_cases(body_file, court, docket, event), scope, settings.corpus_root
        ),
        lambda c, d: open_events(corpus.corpus_db_path(settings.corpus_root), c, d),
    )
    matrix = predict_matrix(settings.config_root / "predictors.yaml", cases, run_id)
    typer.echo(json.dumps(matrix, separators=(",", ":")))


@app.command("evaluate-matrix")
def evaluate_matrix_cmd(
    run_id: Annotated[str, typer.Option(help="Shared run id for this fan-out.")],
    body_file: Annotated[
        Path | None,
        typer.Option(help="Issue body file; its ```json block (one case or an array) is parsed."),
    ] = None,
    court: Annotated[
        str, typer.Option(help="Single-case court id (ignored with --body-file).")
    ] = "",
    docket: Annotated[
        int | None, typer.Option(help="Single-case docket id (ignored with --body-file).")
    ] = None,
    event: Annotated[
        list[str] | None,
        typer.Option(help="Single-case event id(s); default: all resolved events."),
    ] = None,
) -> None:
    """Emit the evaluator x case x event GitHub Actions matrix as compact JSON.

    A case with no listed ``events`` defaults to that case's resolved events.
    """
    settings = get_settings()
    scope = load_predict_config(settings.config_root).scope
    cases = _resolve_cases(
        _scope_filtered(
            _requested_cases(body_file, court, docket, event), scope, settings.corpus_root
        ),
        lambda c, d: resolved_events(corpus.corpus_db_path(settings.corpus_root), c, d),
    )
    matrix = evaluate_matrix(settings.config_root / "evaluators.yaml", cases, run_id)
    typer.echo(json.dumps(matrix, separators=(",", ":")))


@app.command("reconcile-matrix")
def reconcile_matrix_cmd(
    run_id: Annotated[str, typer.Option(help="Shared run id for this fan-out.")],
    body_file: Annotated[
        Path | None,
        typer.Option(help="Issue body file; its ```json block (one case or an array) is parsed."),
    ] = None,
    court: Annotated[
        str, typer.Option(help="Single-case court id (ignored with --body-file).")
    ] = "",
    docket: Annotated[
        int | None, typer.Option(help="Single-case docket id (ignored with --body-file).")
    ] = None,
    event: Annotated[
        list[str] | None,
        typer.Option(help="Single-case event id(s); default: all open events."),
    ] = None,
) -> None:
    """Emit the per-case ``run-reconcile`` GitHub Actions matrix as compact JSON.

    A case with no listed ``events`` defaults to that case's open events — the
    ones flagged decided-but-not-machine-readable that the agent must confirm.
    """
    settings = get_settings()
    cases = _resolve_cases(
        _requested_cases(body_file, court, docket, event),
        lambda c, d: open_events(corpus.corpus_db_path(settings.corpus_root), c, d),
    )
    matrix = reconcile_matrix(cases, run_id)
    typer.echo(json.dumps(matrix, separators=(",", ":")))


@app.command("authorize-trigger")
def authorize_trigger_cmd(
    sender_type: Annotated[
        str, typer.Option(help="github.event.sender.type (a 'Bot' sender is the App handoff).")
    ],
    actor: Annotated[str, typer.Option(help="github.actor that applied the run:* label.")],
    repo: Annotated[str, typer.Option(help="github.repository, owner/name.")],
) -> None:
    """Authorize a run:* label trigger, or refuse and exit non-zero (fail closed).

    The pipeline's trust boundary: a Bot sender is the trusted App handoff, any
    other actor needs write-or-higher collaborator access (looked up via ``gh
    api``). Every ``run:*`` workflow runs this *before* it mints a token, assumes
    the S3 role, or runs an agent. Prints the authorization line and exits 0 when
    allowed; prints the refusal to stderr and exits 1 otherwise. Needs ``GH_TOKEN``
    in the environment for the permission lookup.
    """
    decision = authorize_trigger(sender_type, actor, repo)
    if not decision.authorized:
        typer.echo(f"::error::{decision.message}", err=True)
        raise typer.Exit(code=1)
    typer.echo(decision.message)


@app.command("finalize-produced")
def finalize_produced_cmd(
    role: Annotated[FinalizeRole, typer.Option(help="predict | evaluate.")],
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id the cell acted on.")],
    actor: Annotated[str, typer.Option(help="The predictor_id / evaluator_id for this cell.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
) -> None:
    """Print 'true' if the agent wrote its judgment artifact for this cell, else 'false'.

    The finalize step materializes the event's ``event.yaml`` before the agent
    runs, so a failed agent that wrote nothing still leaves a staged change. This
    reports whether the agent's *own* output (the prediction or evaluation) exists,
    so the workflow can skip a PR that carries only the event scaffold.
    """
    settings = get_settings()
    produced = agent_produced_output(
        role,
        data_root=settings.data_root,
        court=court,
        docket=docket,
        event=event,
        actor=actor,
        run_id=run_id,
    )
    typer.echo("true" if produced else "false")


@app.command("assert-paths")
def assert_paths_cmd(
    name_status_file: Annotated[
        Path, typer.Option(help="File holding `git diff --name-status` output to check.")
    ],
    run_id: Annotated[
        str, typer.Option(help="If set, every changed path must be under this run id.")
    ] = "",
) -> None:
    """Enforce the data/ path jail; exit non-zero (with ::error::) on any violation.

    An auto-merged predict/evaluate/reconcile PR may only *add* files under
    ``data/``. The collect job runs this before it commits, and CI runs it as a
    required status check on the PR, so a change that touches code, a workflow, or
    an existing artifact cannot reach ``main`` without review.
    """
    changes = parse_name_status(name_status_file.read_text())
    try:
        assert_within_jail(changes, run_id=run_id or None)
    except PathJailError as exc:
        typer.echo(f"::error::{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"path jail OK ({len(changes)} change(s))")


@app.command("assert-cleanup-paths")
def assert_cleanup_paths_cmd(
    name_status_file: Annotated[
        Path, typer.Option(help="File holding `git diff --name-status` output to check.")
    ],
) -> None:
    """Enforce the cleanup jail; exit non-zero (with ::error::) on any violation.

    A run-cleanup PR may only *delete* files, and only under a
    ``data/cases/**/events/*/predictions/`` subtree. The cleanup job runs this before
    it commits, and CI runs it as a required status check on the PR, so a sweep that
    removed code, a workflow, an ``event.yaml`` / ``outcome.json``, or any
    non-prediction artifact cannot reach ``main`` without review.
    """
    changes = parse_name_status(name_status_file.read_text())
    try:
        assert_cleanup_within_jail(changes)
    except PathJailError as exc:
        typer.echo(f"::error::{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"cleanup jail OK ({len(changes)} deletion(s))")


@app.command("cleanup-out-of-scope-predictions")
def cleanup_out_of_scope_predictions_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Delete the directories; omit for a dry-run that only lists."),
    ] = False,
    run_id: Annotated[
        str, typer.Option(help="Run id for the review PR's branch name; defaults to now (UTC).")
    ] = "",
    issue: Annotated[
        int, typer.Option(help="Trigger issue the PR closes on merge (0 = none).")
    ] = 0,
) -> None:
    """Prune committed predictions for cases now out of predict scope (issues #320/#333).

    Reads the corpus (must be ``dvc pull``'d) and the committed ``data/`` tree and
    finds every ``…/predictions`` directory whose case an exclusion predicate drops —
    pre-1925 mandatory jurisdiction (#309) or a stale unresolvable old SCOTUS petition
    (#333); the event definition and any ``outcome.json`` stay, only the out-of-scope
    predictions go. Prints a JSON summary
    ``{"prunable":[{case_id,reason,paths}],"removed":<bool>,"pr":<branch/title/commit/body|null>}``;
    with ``--apply`` it also removes the directories. The ``pr`` block (rendered here, not
    in the workflow) is what the run-cleanup job commits and opens as a reviewed PR. Gating
    on the real corpus row only — a case with predictions but no corpus row is left alone.
    """
    settings = get_settings()
    corpus_db = corpus.corpus_db_path(settings.corpus_root)
    if not corpus_db.exists():
        typer.echo(
            f"the corpus database is missing at {corpus_db}; provision it (dvc pull) "
            "before running cleanup.",
            err=True,
        )
        raise typer.Exit(code=1)
    prunable = cleanup.find_out_of_scope_predictions(settings.data_root, corpus_db)
    if apply:
        cleanup.remove(prunable, settings.data_root.parent)
    pr = (
        cleanup.render_cleanup_pr(prunable, run_id or ids.run_id(), issue or None)
        if prunable
        else None
    )
    typer.echo(
        json.dumps(
            {
                "prunable": [case.model_dump() for case in prunable],
                "removed": apply,
                "pr": pr.model_dump() if pr is not None else None,
            },
            separators=(",", ":"),
        )
    )


@app.command("metrics-refresh-plan")
def metrics_refresh_plan(
    changed_file: Annotated[
        Path,
        typer.Option(help="File holding `git diff --name-only -- metrics/` output to summarize."),
    ],
    run_id: Annotated[
        str, typer.Option(help="Refresh run id for the PR prose; defaults to now (UTC).")
    ] = "",
) -> None:
    """Render the review-PR plan for a metrics refresh (``run-analytics``).

    The workflow regenerates the metrics artifacts (the same tested commands the DVC
    stages run), diffs ``metrics/``, and hands the changed paths here; this prints a
    JSON plan ``{"changed":[...],"pr":<branch/title/commit/body|null>}`` with a
    per-artifact headline read from the regenerated files. ``pr`` is null when
    nothing changed (byte-stable artifacts -> empty diff -> no PR), so the workflow
    can exit quietly. The prose is rendered here, not with ``jq`` and a heredoc in
    the workflow, mirroring ``cleanup-out-of-scope-predictions``.
    """
    settings = get_settings()
    changed = [line.strip() for line in changed_file.read_text().splitlines() if line.strip()]
    pr = metrics_refresh.render_refresh_pr(changed, settings.metrics_root, run_id or ids.run_id())
    typer.echo(
        json.dumps(
            {"changed": changed, "pr": pr.model_dump() if pr is not None else None},
            separators=(",", ":"),
        )
    )


def _pr_plan_json(plan: PrPlan | None) -> dict[str, object] | None:
    if plan is None:
        return None
    return {
        "branch": plan.branch,
        "commit_message": plan.commit_message,
        "title": plan.title,
        "body": plan.body,
        "draft": plan.draft,
        "artifact_dirs": list(plan.artifact_dirs),
    }


def _collect_plan_json(plan: CollectPlan) -> dict[str, object]:
    return {
        "ready": _pr_plan_json(plan.ready),
        "partial": _pr_plan_json(plan.partial),
        "skipped": [
            {"actor": c.actor, "court": c.court, "docket": c.docket, "event_id": c.event_id}
            for c in plan.skipped
            if isinstance(c, CellStatus)
        ],
        "flags": plan.flags_markdown,
        "feedback_comment": plan.feedback_comment,
        "stalled": plan.stalled,
    }


def _load_flag_sets(status_dir: Path, run_id: str) -> list[AgentFlags]:
    """Parse this run's per-cell ``flags.json`` under ``status_dir`` into models.

    The collect job downloads each cell's artifact (its ``status.json`` plus the
    cell's whole ``data/`` subtree); a cell that surfaced feedback wrote a
    ``flags.json`` somewhere under that subtree. Read them wherever they landed so
    the roll-up sees flags from *every* cell — including a blocked cell that produced
    no judgment and is never committed.

    Because every artifact carries the full ``data/`` tree, *previously committed*
    flag files from earlier runs ride along in each cell, so two filters keep the
    per-run roll-up honest (without them a prior run's flags reappear once per cell,
    growing with both history and matrix width — see issue #333):

    * **run id** — keep only flags from this ``run_id``; an earlier run's committed
      flags are not this run's feedback.
    * **identity** — collapse byte-identical flag files, so the same note shipped in
      more than one cell's artifact counts once.

    A malformed flag file is skipped (the cell's own status already reflects its
    failure) rather than aborting the run's aggregation.
    """
    seen: set[str] = set()
    flag_sets: list[AgentFlags] = []
    for path in sorted(status_dir.glob("**/flags.json")):
        try:
            flag_set = AgentFlags.model_validate_json(path.read_text())
        except (OSError, ValueError):
            continue
        if flag_set.run_id != run_id:
            continue
        identity = flag_set.model_dump_json()
        if identity in seen:
            continue
        seen.add(identity)
        flag_sets.append(flag_set)
    return flag_sets


@app.command("collect-plan")
def collect_plan_cmd(
    role: Annotated[FinalizeRole, typer.Option(help="predict | evaluate.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    status_dir: Annotated[Path, typer.Option(help="Root the cell artifacts were downloaded into.")],
    issue: Annotated[
        int,
        typer.Option(help="Triggering issue number; the ready PR closes it on merge (0 = none)."),
    ] = 0,
) -> None:
    """Emit the per-run aggregate PR decision as compact JSON.

    Reads every ``status.json`` under ``status_dir`` (one per matrix cell), then
    prints ``{"ready": <pr|null>, "partial": <pr|null>, "skipped": [...]}`` where
    each ``pr`` carries ``branch`` / ``commit_message`` / ``title`` / ``body`` /
    ``draft`` and the ``artifact_dirs`` whose ``data/`` the collect job copies into
    that PR. The ready ``body`` closes ``--issue`` on merge unless a draft remains.
    ``flags`` is the run's rolled-up agent flags (also appended to the PR body),
    which the collect step echoes into the Actions summary; ``feedback_comment``
    is the same roll-up wrapped for the long-lived agent-feedback tracking issue
    (empty when no flags), which the collect step posts so a note survives even a
    fully-failed run that opens no PR.
    """
    cells = []
    for status_path in sorted(status_dir.glob("**/status.json")):
        artifact_dir = str(status_path.parent.relative_to(status_dir))
        cells.append(
            CellStatus.from_dict(json.loads(status_path.read_text()), artifact_dir=artifact_dir)
        )
    plan = collect_plan(
        role,
        run_id=run_id,
        cells=cells,
        issue=issue or None,
        flags=_load_flag_sets(status_dir, run_id),
    )
    typer.echo(json.dumps(_collect_plan_json(plan), separators=(",", ":")))


@app.command("stall-comment")
def stall_comment_cmd(
    role: Annotated[FinalizeRole, typer.Option(help="predict | evaluate | reconcile.")],
    run_url: Annotated[str, typer.Option(help="The Actions run URL to link from the comment.")],
) -> None:
    """Print the trigger-issue comment for a run that produced no output at all.

    A wholesale failure (every cell dying before its agent ran) opens no PR and
    would leave the trigger issue silently orphaned open. The collect job renders
    this comment — prose from tested code, per the house rule — and posts it to
    the trigger issue with the ambient ``GITHUB_TOKEN`` so the stall is loud and
    carries retry instructions.
    """
    typer.echo(render_stall_comment(role, run_url))


@app.command("post-agent-feedback")
def post_agent_feedback_cmd(
    body_file: Annotated[
        Path, typer.Option(help="The rendered feedback comment (collect-plan's feedback_comment).")
    ],
    repo: Annotated[str, typer.Option(help="owner/name of the repository to post into.")],
) -> None:
    """Latch a run's agent-flag roll-up onto the long-lived agent-feedback issue.

    Reads the rendered comment from ``--body-file`` (an empty/blank file means the
    run raised no flags, so nothing is posted), then find-or-creates the single
    ``agent-feedback`` issue and posts the comment once (marker-deduped, so a
    ``collect`` re-run never duplicates it). The predict/evaluate collect job calls
    this with the ambient ``GITHUB_TOKEN`` — off its contents-write App token, since
    the label is non-triggering. The find-or-create and idempotency are tested in
    ``agent_feedback.py``; this command is the thin gh-invoking wrapper.
    """
    comment = body_file.read_text(encoding="utf-8") if body_file.exists() else ""
    typer.echo(post_agent_feedback(comment, repo))


def _reconcile_collect_plan_json(plan: CollectPlan) -> dict[str, object]:
    # Reconcile skips are per case (no actor/event), so serialize court/docket only.
    return {
        "ready": _pr_plan_json(plan.ready),
        "partial": _pr_plan_json(plan.partial),
        "skipped": [{"court": c.court, "docket": c.docket} for c in plan.skipped],
        "flags": plan.flags_markdown,
        "feedback_comment": plan.feedback_comment,
        "stalled": plan.stalled,
    }


@app.command("collect-reconcile-plan")
def collect_reconcile_plan_cmd(
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    status_dir: Annotated[Path, typer.Option(help="Root the cell artifacts were downloaded into.")],
    issue: Annotated[
        int,
        typer.Option(help="Triggering issue number; the ready PR closes it on merge (0 = none)."),
    ] = 0,
) -> None:
    """Emit the per-run aggregate reconcile PR decision as compact JSON.

    Reads every per-case ``status.json`` under ``status_dir``, then prints
    ``{"ready": <pr|null>, "partial": <pr|null>, "skipped": [{court,docket}],
    "flags": <md>, "feedback_comment": <md>}``. The ready ``commit_message`` /
    ``title`` start with ``reconcile:`` so the squash-merge to ``main`` fires the
    evaluate handoff, and the ready ``body`` closes ``--issue`` on merge unless a
    draft remains. ``flags`` / ``feedback_comment`` carry the run's rolled-up agent
    flags for the Actions summary and the long-lived agent-feedback issue, like
    ``collect-plan``.
    """
    cells = []
    for status_path in sorted(status_dir.glob("**/status.json")):
        artifact_dir = str(status_path.parent.relative_to(status_dir))
        cells.append(
            ReconcileCellStatus.from_dict(
                json.loads(status_path.read_text()), artifact_dir=artifact_dir
            )
        )
    plan = reconcile_collect_plan(
        run_id=run_id, cells=cells, issue=issue or None, flags=_load_flag_sets(status_dir, run_id)
    )
    typer.echo(json.dumps(_reconcile_collect_plan_json(plan), separators=(",", ":")))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
