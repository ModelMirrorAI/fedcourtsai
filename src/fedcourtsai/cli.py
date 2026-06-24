"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
import yaml

from . import corpus, ids
from .config import get_settings
from .courtlistener import CourtListenerClient, default_rate_limiter
from .matrix import evaluate_matrix, predict_matrix
from .paths import CasePaths
from .pipeline.pull import pull_case
from .pipeline.seed import seed_case
from .registry import load_evaluators, load_predictors
from .schemas import EXPORTABLE_MODELS, FILENAME_MODELS
from .serialize import write_raw_json
from .store import iter_tracked_cases, open_events, resolved_events

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


@app.command()
def seed(
    court: Annotated[str, typer.Option(help="CourtListener court id, e.g. ca9 or scotus.")],
    docket: Annotated[int, typer.Option(help="CourtListener docket id.")],
) -> None:
    """Pull a docket from CourtListener and start tracking it."""
    settings = get_settings()
    with _client() as client:
        case = seed_case(client, settings.data_root, court, docket)
    typer.echo(f"Seeded {case.case_id}: {case.case_name}")


@app.command()
def pull(
    court: Annotated[str, typer.Option(help="CourtListener court id.")],
    docket: Annotated[int, typer.Option(help="CourtListener docket id.")],
) -> None:
    """Refresh one tracked docket and report whether it changed."""
    settings = get_settings()
    with _client() as client:
        result = pull_case(client, settings.data_root, court, docket)
    typer.echo(f"{result.case_id} changed={result.changed} snapshot={result.snapshot}")


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
    """Print resolved on-disk paths for a case (or event). Useful in scripts."""
    settings = get_settings()
    cp = CasePaths(settings.data_root, court, docket)
    typer.echo(f"case_id     {ids.case_id(court, docket)}")
    typer.echo(f"case.yaml   {cp.case_file}")
    typer.echo(f"docket.json {cp.docket}")
    if event:
        ep = cp.event(event)
        typer.echo(f"event.yaml  {ep.event_file}")
        typer.echo(f"outcome     {ep.outcome}")


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
    limit: Annotated[int, typer.Option(help="Max cases to refresh this run.")] = 50,
) -> None:
    """Refresh all tracked cases; emit a queue of changed cases with open events."""
    settings = get_settings()
    queue: list[dict[str, object]] = []
    with _client() as client:
        for court, docket in iter_tracked_cases(settings.data_root)[:limit]:
            result = pull_case(client, settings.data_root, court, docket)
            events = open_events(settings.data_root, court, docket)
            if result.changed and events:
                queue.append({"court": court, "docket": docket, "events": events})
            typer.echo(f"{result.case_id} changed={result.changed} open_events={len(events)}")
    out.write_text(json.dumps(queue) + "\n")
    typer.echo(f"Queued {len(queue)} case(s) for prediction -> {out}")


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
