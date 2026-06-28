"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from . import corpus, dvc, ids
from .backtest import default_backtesters, run_backtest, select_backtest_set
from .config import (
    PredictScope,
    get_settings,
    load_courts,
    load_predict_config,
    load_pull_config,
    load_seed_config,
)
from .courtlistener import CourtListenerClient, default_rate_limiter
from .leaderboard import build_leaderboard
from .matrix import CaseRequest, evaluate_matrix, parse_cases, predict_matrix, reconcile_matrix
from .ops import build_ops_report, render_data_health, render_markdown
from .paths import CasePaths
from .pipeline.discover import discover_cases
from .pipeline.pull import pull_case, pull_cases
from .pipeline.seed import (
    CourtListenerBulkSource,
    backfill,
    load_cursor,
    resolve_dockets_source,
    sibling_bulk_url,
)
from .pricing import DEFAULT_MODELS, MODEL_RATES, TokenCounts, estimate_cost_usd
from .registry import load_evaluators, load_predictors
from .schemas import (
    EXPORTABLE_MODELS,
    CorpusValidation,
    DataHealth,
    Disposition,
    Engine,
    ModelUsage,
    OpsReport,
    UsageRole,
)
from .serialize import write_json, write_raw_json
from .store import (
    cases_due_for_pull,
    iter_evaluations,
    iter_usage,
    open_events,
    resolved_events,
)
from .usage import parse_claude_usage, parse_codex_usage
from .validate import run_corpus_validation, run_ledger_referential_checks, validate_ledger

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
            s.courtlistener_rpm, s.courtlistener_rph, s.courtlistener_rpd
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
    pipeline output (the ``metrics/`` roll-ups) is committed. Exits non-zero and
    lists every problem if the bookkeeping has drifted. The online ``dvc status``
    / push side belongs to the data workflows that hold the remote credentials.
    """
    is_tracked, is_ignored = dvc.git_checkers(path)
    errors = dvc.check_state(path, is_tracked=is_tracked, is_ignored=is_ignored)
    if errors:
        for err in errors:
            typer.echo(f"DVC {err}", err=True)
        typer.echo(f"\n{len(errors)} DVC metadata problem(s)", err=True)
        raise typer.Exit(code=1)
    outs, _ = dvc.collect_outs(path)
    tracked = dvc.tracked_paths(outs)
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
    Brier score, mean vote accuracy, a reasoning-quality summary, and counts —
    and writes it through the shared serializer for minimal diffs. Reruns over an
    unchanged ledger reproduce the file byte for byte.
    """
    settings = get_settings()
    board = build_leaderboard(iter_evaluations(settings.data_root))
    destination = out if out is not None else settings.metrics_root / "leaderboard.json"
    write_json(destination, board)
    typer.echo(
        f"leaderboard: {board.predictors_ranked} predictor(s) from "
        f"{board.evaluations_total} evaluation(s) -> {destination}"
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


def _resolve_token_counts(
    explicit: TokenCounts,
    claude_execution_file: Path | None,
    codex_sessions_dir: Path | None,
) -> TokenCounts | None:
    """Token counts from an engine log if given, else the explicit overrides.

    Returns ``None`` when a log source was named but carried no usage — the
    signal for the caller to skip writing rather than record false zeros.
    """
    if claude_execution_file is not None:
        return parse_claude_usage(claude_execution_file)
    if codex_sessions_dir is not None:
        return parse_codex_usage(codex_sessions_dir)
    return explicit


@app.command("record-usage")
def record_usage(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to inputs
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id this run predicted/scored.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    engine: Annotated[Engine, typer.Option(help="Engine that ran (claude-code | codex).")],
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
    created_at: Annotated[
        str, typer.Option(help="ISO timestamp; defaults to the run id's timestamp.")
    ] = "",
) -> None:
    """Record one run's measured token usage and estimated cost to ``usage.json``.

    Reads token counts from the engine's own log (``--claude-execution-file`` or
    ``--codex-sessions-dir``) or from the explicit ``--*-tokens`` overrides,
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
) -> None:
    """Roll pipeline health, backfill, spend, and data health into an ops snapshot.

    A read-only view of authoritative sources — the GitHub Actions run history
    (``--runs``), the seed cursor (``config/seed-progress.yaml``), and the recorded
    ``usage.json`` ledger under ``data/``. Also presents the **data-health** verdict:
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
    when = generated_at or datetime.now(UTC).isoformat()
    report = build_ops_report(
        generated_at=when,
        runs=run_rows,
        progress=progress,
        courts=courts,
        usage=iter_usage(settings.data_root),
        previous=prior,
        data_health=data_health,
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


def _fetch_one_docket(court: str, docket: int) -> None:
    """Fetch one docket via REST and ingest it into the corpus (onboard/refresh)."""
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    with _client() as client:
        result = pull_case(client, db, settings.data_root, court, docket)
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

    if report is not None:
        write_raw_json(report, rep.model_dump(mode="json"))
    typer.echo(
        f"seed-backfill snapshot={rep.snapshot} loaded_this_run={rep.loaded_this_run} "
        f"complete={rep.complete}"
    )


@app.command("corpus-info")
def corpus_info() -> None:
    """Show the packed corpus location and row count (run after `dvc pull`)."""
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `dvc pull` to fetch it from the remote.")
        return
    with corpus.connect(db_path) as conn:
        typer.echo(
            f"corpus {db_path}: {corpus.count(conn)} row(s), "
            f"{corpus.snapshot_count(conn)} snapshot(s)"
        )


@app.command()
def query(
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
    include_open: Annotated[
        bool, typer.Option(help="Include unresolved cases (default: decided priors only).")
    ] = False,
    limit: Annotated[
        int, typer.Option(help="Maximum priors to return.")
    ] = corpus.DEFAULT_PRIOR_LIMIT,
    full: Annotated[
        bool, typer.Option(help="Include each prior's full opinion_text (omitted by default).")
    ] = False,
) -> None:
    """Retrieve relevant priors from the corpus, most relevant first (run after `dvc pull`).

    Precedent retrieval for predictors: pull a handful of similar resolved cases
    by structured filter instead of loading the bulk set. ``--court`` / ``--topic``
    / ``--disposition`` match exactly; ``--judge`` and ``--citation`` (repeatable)
    match on overlap and rank the results by how much they share. Prints one
    compact JSON row per line, ranked, with ``opinion_text`` omitted unless
    ``--full``. Semantic search lands later on the same query seam.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
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
        resolved_only=not include_open,
    )
    with corpus.connect(db_path) as conn:
        priors = corpus.retrieve_priors(conn, q, limit=limit)
    for row in priors:
        payload = row.model_dump(mode="json")
        if not full:
            payload.pop("opinion_text", None)
        typer.echo(json.dumps(payload, sort_keys=True, separators=(",", ":")))


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
) -> None:
    """Materialize a case's latest corpus snapshot to disk for an agent run.

    Point-in-time snapshots are raw facts that live in the packed corpus, not
    git. The predict/evaluate/reconcile workflows call this after a ``dvc pull``
    to read the most recent dated snapshot for the case out of the corpus and
    write it where the agent reads it (a gitignored ``record/`` path, never
    committed). Exits non-zero if the corpus holds no snapshot for the case.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    case = ids.case_id(court, docket)
    with corpus.connect(db_path) as conn:
        found = corpus.latest_snapshot(conn, case)
    if found is None:
        typer.echo(f"No snapshot in corpus for {case} (dvc pull the corpus first?)", err=True)
        raise typer.Exit(code=1)
    snapshot_date, payload = found
    dest = out or CasePaths(settings.data_root, court, docket).snapshot(snapshot_date.isoformat())
    write_raw_json(dest, payload)
    typer.echo(f"{case} snapshot {snapshot_date.isoformat()} -> {dest}")


@app.command("open-events")
def open_events_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
) -> None:
    """Print unresolved (predictable) event ids for a case, one per line."""
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    for eid in open_events(db, court, docket):
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
    """
    settings = get_settings()
    pull_cfg = load_pull_config(settings.config_root)
    scope = load_predict_config(settings.config_root).scope
    cap = pull_cfg.max_cases_per_run if limit is None else min(limit, pull_cfg.max_cases_per_run)
    db = corpus.corpus_db_path(settings.corpus_root)
    with _client() as client:
        if pull_cfg.discover_new_filings:
            disc = discover_cases(
                client,
                db,
                load_courts(settings.config_root),
                max_new=pull_cfg.max_new_cases_per_run,
                default_since=date.today(),
            )
            disc_failed = _format_discovery_failures(disc.failed)
            typer.echo(f"Discovered {disc.total} new case(s) before refresh{disc_failed}")
        # Rotation reads after discovery so freshly-onboarded cases are eligible.
        due = cases_due_for_pull(db, limit=cap, skip_closed=pull_cfg.skip_closed)
        queues = pull_cases(client, db, settings.data_root, due, scope=scope)
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    reconcile_out.write_text(json.dumps(queues.reconcile) + "\n")
    failed = f" ({len(queues.failed)} failed)" if queues.failed else ""
    typer.echo(
        f"Refreshed {len(due) - len(queues.failed)}/{cap} case(s){failed}; "
        f"queued {len(queues.predict)} predict, {len(queues.evaluate)} evaluate, "
        f"{len(queues.reconcile)} reconcile."
    )


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
    """
    if scope == PredictScope.all:
        return cases
    kept: list[CaseRequest] = []
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        for case in cases:
            row = corpus.get_row(conn, ids.case_id(case.court, case.docket))
            if row is not None and row.predict_eligible:
                kept.append(case)
            else:
                typer.echo(
                    f"Skipping {case.court}/{case.docket}: out of prediction scope "
                    f"(predict.scope=scotus_touched, not SCOTUS-eligible).",
                    err=True,
                )
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
