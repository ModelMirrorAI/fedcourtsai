"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Annotated

import typer
import yaml

from . import corpus, ids
from .backtest import default_backtesters, run_backtest, select_backtest_set
from .config import get_settings, load_courts, load_pull_config, load_seed_config
from .courtlistener import CourtListenerClient, default_rate_limiter
from .leaderboard import build_leaderboard
from .matrix import CaseRequest, evaluate_matrix, parse_cases, predict_matrix
from .paths import CasePaths
from .pipeline.discover import discover_cases
from .pipeline.pull import pull_case, pull_cases
from .pipeline.seed import (
    CourtListenerBulkSource,
    backfill,
    resolve_dockets_source,
    sibling_bulk_url,
)
from .pricing import DEFAULT_MODELS, MODEL_RATES, TokenCounts, estimate_cost_usd
from .registry import load_evaluators, load_predictors
from .schemas import EXPORTABLE_MODELS, FILENAME_MODELS, Disposition, Engine, ModelUsage, UsageRole
from .serialize import write_json, write_raw_json
from .store import (
    cases_due_for_pull,
    iter_evaluations,
    iter_usage,
    open_events,
    resolved_events,
)
from .usage import parse_claude_usage, parse_codex_usage

app = typer.Typer(add_completion=False, help="Predict events in US federal courts.")


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
    """Validate every known artifact under PATH against its schema."""
    errors: list[str] = []
    checked = 0
    for file in sorted(path.rglob("*")):
        model = FILENAME_MODELS.get(file.name)
        if model is None or not file.is_file():
            continue
        checked += 1
        try:
            text = file.read_text()
            data = json.loads(text) if file.suffix == ".json" else yaml.safe_load(text)
            model.model_validate(data)
        except Exception as exc:
            errors.append(f"{file}: {exc}")

    if errors:
        for err in errors:
            typer.echo(f"INVALID {err}", err=True)
        typer.echo(f"\n{len(errors)} invalid / {checked} checked", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"OK: {checked} artifact(s) valid")


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

    Deterministic single-docket ingestion of raw facts (what ``run-seed`` runs):
    fetches the docket and upserts its normalized row into the corpus through the
    shared ingestion core. ``pull`` refreshes an already-onboarded docket. The
    historical mass is loaded separately by the bulk-data backfill — a planned
    expansion of this path; see ``docs/data-pipeline.md``.
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
) -> None:
    """Load the next chunk of CourtListener bulk data into the corpus (no agent).

    The deterministic historical backfill: reads the committed cursor
    (``config/seed-progress.yaml``), streams the next slice of the public bulk
    snapshot for the tracked courts (``config/tracking.yaml``), normalizes each
    row through the shared ingestion core into the packed corpus, and advances the
    cursor — all without spending the CourtListener REST budget. ``--max-cases``
    may only lower the per-run cap, never raise it. Idempotent: re-running after
    completion loads zero rows.
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
        typer.echo(f"corpus {db_path}: {corpus.count(conn)} row(s)")


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


@app.command("open-events")
def open_events_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
) -> None:
    """Print unresolved (predictable) event ids for a case, one per line."""
    settings = get_settings()
    for eid in open_events(settings.data_root, court, docket):
        typer.echo(eid)


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
            typer.echo(f"Discovered {disc.total} new case(s) before refresh")
        # Rotation reads after discovery so freshly-onboarded cases are eligible.
        due = cases_due_for_pull(db, limit=cap, skip_closed=pull_cfg.skip_closed)
        queues = pull_cases(client, db, settings.data_root, due)
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    reconcile_out.write_text(json.dumps(queues.reconcile) + "\n")
    typer.echo(
        f"Refreshed {len(due)}/{cap} case(s); queued {len(queues.predict)} predict, "
        f"{len(queues.evaluate)} evaluate, {len(queues.reconcile)} reconcile."
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
    cases = _resolve_cases(
        _requested_cases(body_file, court, docket, event),
        lambda c, d: open_events(settings.data_root, c, d),
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
    cases = _resolve_cases(
        _requested_cases(body_file, court, docket, event),
        lambda c, d: resolved_events(settings.data_root, c, d),
    )
    matrix = evaluate_matrix(settings.config_root / "evaluators.yaml", cases, run_id)
    typer.echo(json.dumps(matrix, separators=(",", ":")))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
