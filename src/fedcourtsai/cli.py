"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
import yaml

from . import corpus, ids
from .config import get_settings, load_courts, load_pull_config, load_seed_config
from .courtlistener import CourtListenerClient, default_rate_limiter
from .matrix import evaluate_matrix, predict_matrix
from .paths import CasePaths
from .pipeline.discover import discover_cases
from .pipeline.pull import pull_case
from .pipeline.seed import CourtListenerBulkSource, backfill, quarter_id
from .registry import load_evaluators, load_predictors
from .schemas import EXPORTABLE_MODELS, FILENAME_MODELS
from .serialize import write_raw_json
from .store import cases_due_for_pull, open_events, resolved_events

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

    snapshot_id = settings.seed_snapshot or quarter_id(date.today())
    source = CourtListenerBulkSource(
        snapshot_id, url=settings.courtlistener_bulk_url, timeout=settings.request_timeout
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
    predict_queue: list[dict[str, object]] = []
    evaluate_queue: list[dict[str, object]] = []
    reconcile_queue: list[dict[str, object]] = []
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
        for court, docket in due:
            result = pull_case(client, db, settings.data_root, court, docket)
            events = open_events(settings.data_root, court, docket)
            if result.changed and events:
                predict_queue.append({"court": court, "docket": docket, "events": events})
            if result.resolved:
                evaluate_queue.append({"court": court, "docket": docket, "events": result.resolved})
            if result.reconcile:
                reconcile_queue.append(
                    {
                        "court": court,
                        "docket": docket,
                        "events": [r.event_id for r in result.reconcile],
                        "reason": result.reconcile[0].reason,
                    }
                )
            typer.echo(
                f"{result.case_id} changed={result.changed} open_events={len(events)} "
                f"resolved={len(result.resolved)} reconcile={len(result.reconcile)}"
            )
    out.write_text(json.dumps(predict_queue) + "\n")
    evaluate_out.write_text(json.dumps(evaluate_queue) + "\n")
    reconcile_out.write_text(json.dumps(reconcile_queue) + "\n")
    typer.echo(
        f"Refreshed {len(due)}/{cap} case(s); queued {len(predict_queue)} predict, "
        f"{len(evaluate_queue)} evaluate, {len(reconcile_queue)} reconcile."
    )


@app.command()
def discover(
    since: Annotated[
        str,
        typer.Option(
            help="ISO date to start a never-discovered court from (default: today). "
            "Courts with a stored watermark resume from it regardless."
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


@app.command("predict-matrix")
def predict_matrix_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    run_id: Annotated[str, typer.Option(help="Shared run id for this fan-out.")],
    event: Annotated[
        list[str] | None, typer.Option(help="Event id(s); defaults to all open events.")
    ] = None,
) -> None:
    """Emit the predictor x event GitHub Actions matrix as compact JSON."""
    settings = get_settings()
    events = event or open_events(settings.data_root, court, docket)
    matrix = predict_matrix(settings.config_root / "predictors.yaml", court, docket, events, run_id)
    typer.echo(json.dumps(matrix, separators=(",", ":")))


@app.command("evaluate-matrix")
def evaluate_matrix_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    run_id: Annotated[str, typer.Option(help="Shared run id for this fan-out.")],
    event: Annotated[
        list[str] | None, typer.Option(help="Event id(s); defaults to all resolved events.")
    ] = None,
) -> None:
    """Emit the evaluator x event GitHub Actions matrix as compact JSON."""
    settings = get_settings()
    events = event or resolved_events(settings.data_root, court, docket)
    matrix = evaluate_matrix(
        settings.config_root / "evaluators.yaml", court, docket, events, run_id
    )
    typer.echo(json.dumps(matrix, separators=(",", ":")))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
