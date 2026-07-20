"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import BaseModel

from . import (
    analytics,
    cleanup,
    corpus,
    corpus_index,
    corpus_ranged,
    corpus_remote,
    corpus_service,
    ids,
    integration_check,
    mcp,
    metrics_refresh,
    provision,
    repo_gate,
    retrieval,
    scope_manifest,
    secretscan,
)
from .agent_feedback import post_agent_feedback
from .authz import authorize_trigger
from .backtest import default_backtesters, run_backtest, select_backtest_set
from .cert_backtest import (
    CERT_BACKTEST_SCOPES,
    build_segment_context,
    replay_predictors,
    replayable_items,
    run_cert_backtest,
    select_cert_backtest_set,
)
from .collect import (
    CellStatus,
    CollectPlan,
    ExpectedCell,
    PathJailError,
    PrPlan,
    assert_cleanup_within_jail,
    assert_within_jail,
    collect_plan,
    parse_name_status,
    render_stall_comment,
)
from .config import (
    PredictScope,
    get_settings,
    load_courts,
    load_historical_config,
    load_live_config,
    load_predict_config,
    load_pull_config,
    load_salience_config,
)
from .courtlistener import CourtListenerClient, default_rate_limiter
from .finalize import FinalizeRole, agent_produced_output
from .fixture import build_fixture_corpus
from .gvr_migration import relabel_munsingwear_gvr_outcomes
from .leaderboard import big_case_agreement, build_leaderboard
from .matrix import CaseRequest, evaluate_matrix, parse_cases, predict_matrix
from .ops import (
    build_ops_report,
    render_data_health,
    render_markdown,
    render_weekly_digest,
    summarize_substance,
    summarize_trigger_issues,
)
from .paths import CasePaths
from .pipeline import historical, liveprobe
from .pipeline.cascade import CascadeError, run_cascade
from .pipeline.cert_signals import match_disposition_signal
from .pipeline.discover import discover_cases
from .pipeline.live import live_poll_all
from .pipeline.outcome import entry_descriptions, snapshot_shows_disposition
from .pipeline.pull import pull_case, pull_cases
from .pipeline.runner import EngineFailed, EngineUnavailable
from .pipeline.salience import reconcile_salience_selection
from .pipeline.scope_reconcile import reconcile_predict_scope
from .pricing import DEFAULT_MODELS, MODEL_RATES, TokenCounts, estimate_cost_usd
from .registry import (
    enabled_predictors,
    load_evaluators,
    load_mcp_servers,
    load_predictors,
    resolve_mcp_servers,
)
from .schemas import (
    EXPORTABLE_MODELS,
    AgentFlags,
    ConferenceBucket,
    CorpusValidation,
    DataHealth,
    Disposition,
    Engine,
    GroupBy,
    LiveFrontier,
    ModelUsage,
    OpsReport,
    PredictableEvent,
    RetrievalCall,
    RetrievalLog,
    StatPack,
    UsageRole,
)
from .serialize import write_json, write_raw_json, write_text, write_yaml
from .store import (
    cases_due_for_pull,
    iter_flags,
    iter_stratified_evaluations,
    iter_tooling,
    iter_usage,
    ledger_cell_counts,
    open_events,
    resolved_events,
)
from .supremecourt import SupremeCourtClient, current_october_term
from .usage import (
    parse_claude_usage,
    parse_codex_usage,
    parse_gemini_usage,
    resolve_pipeline_sha,
)
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
    targets a real prediction. The corpus-dependent referential checks need the
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
    Graceful when the corpus is absent (run before a corpus pull): writes a skipped
    verdict and exits 0. The exit code reports check health (non-zero on a failed
    verdict) so a caller can surface it; the wiring that runs this treats a failure
    as loud-not-fatal, never blocking on it.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    as_of = date.fromisoformat(today) if today else datetime.now(UTC).date()
    verdict = run_corpus_validation(
        corpus_db_path=db_path,
        data_root=settings.data_root,
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
    """Census open corpus events the predict scope excludes; emit a JSON audit.

    Read-only: opens the packed corpus and, for every still-open SCOTUS event, tallies
    by exclusion reason (pre-1925 mandatory jurisdiction, stale unresolvable, and siblings)
    the cases, open events, and the recoverable subset (those whose case carries an
    opinion/citation/decision-date signal — a hint the disposition is an ingestion gap
    rather than genuinely absent). Writes the `CorpusScopeAudit` and prints a summary.
    Graceful when the corpus is absent (run before a corpus pull): writes a skipped audit
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
    """Reconcile the corpus's out-of-scope latch with the predicate set.

    The write counterpart of `corpus-scope-audit`: over the SCOTUS dockets, it
    latches `predict_excluded` on those the shared exclusion reasoning now matches
    (`corpus.out_of_scope_reason_full` — the row rules plus the snapshot-aware bare
    opinion-import rule) and clears it on those back in scope — so `open-events` (and
    thus the predict/queueing paths) drop excluded cases at the source. Dry-run by
    default; `--apply` writes (the run-seed walk then pushes the corpus). Prints a
    `ScopeReconcileResult`. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
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


@app.command("reconcile-salience-selection")
def reconcile_salience_selection_cmd(
    apply: Annotated[
        bool,
        typer.Option(
            "--apply", help="Write the scores and selection latch; omit for a dry-run count."
        ),
    ] = False,
) -> None:
    """Score the in-scope cert petitions and latch the per-conference selected slice.

    The salience gate's write pass (see `docs/salience.md`): scores every in-scope
    SCOTUS cert petition with the frozen salience function and latches
    `salience_selected` on each conference cohort's top-N by score plus the
    always-include carve-outs (CVSG, above-floor). The latch is one-way (sticky), so
    a re-run never de-selects a case that later drifts below the cap. Dry-run by
    default; `--apply` writes (the run-seed walk then pushes the corpus). Prints a
    `SalienceSelectionResult`. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the salience selection pass.",
            err=True,
        )
        raise typer.Exit(code=1)
    config = load_salience_config(settings.config_root)
    with corpus.connect(db_path) as conn:
        result = reconcile_salience_selection(conn, config, apply=apply)
    typer.echo(
        f"reconcile-salience-selection ({'applied' if apply else 'dry-run'}): "
        f"scored {result.scored}, newly selected {result.newly_selected} "
        f"across {result.conferences} conference(s)"
    )
    typer.echo(result.model_dump_json())


@app.command("migrate-gvr-labels")
def migrate_gvr_labels_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Rewrite the matching outcomes; omit for a dry-run count."),
    ] = False,
) -> None:
    """Relabel identifiable historical GVR outcomes to the `gvr` disposition.

    A one-time, deterministic migration for the introduction of the `gvr` label
    (see `docs/salience.md`): each committed `granted` outcome whose
    `disposition_basis` is `mootness` — an identifiable Munsingwear vacatur — is
    relabeled `actual_disposition = gvr`. Nothing else changes: `actual_granted`
    stays 1 (a GVR is a grant), the frozen `evaluation.json` records are untouched,
    and the relabeled cell keeps its `mootness` basis (procedural stratum). Dry-run
    by default; `--apply` writes.
    """
    settings = get_settings()
    result = relabel_munsingwear_gvr_outcomes(settings.data_root, apply=apply)
    typer.echo(
        f"migrate-gvr-labels ({'applied' if apply else 'dry-run'}): "
        f"{len(result.relabeled)} outcome(s) relabeled to gvr"
    )
    if result.relabeled:
        typer.echo(", ".join(result.relabeled))


@app.command("scope-manifest")
def scope_manifest_cmd(
    out: Annotated[
        Path | None,
        typer.Option(help="JSON output path (default: <data_root>/scope/scope.json)."),
    ] = None,
) -> None:
    """Publish the prediction-scope decision for the already-public case set.

    Writes ``data/scope/scope.json`` — one row per docket that already has a
    committed directory under ``data/cases`` and a corpus row, carrying that
    case's ``predict_eligible`` / ``predict_excluded`` / exclusion reason /
    sample weight from the corpus (a public docket absent from the corpus is
    omitted rather than guessed at). The transparency counterpart of ``reconcile-scope``:
    the reconcile decides scope in the corpus, this publishes the decision for
    the cases the repository already discloses. Enumerated from the committed
    ``data/cases`` tree alone — never a corpus scan — so it cannot enumerate the
    broader ingested corpus (a deliberate compilation-extent boundary).
    Deterministic and offline: a pure function of the committed tree + corpus, so
    reruns reproduce it byte for byte. Writes the empty ``skipped`` manifest when
    the corpus is absent (run after a corpus pull). Git-tracked; regenerate and
    open a reviewed PR when the public set or its scope latches change.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    manifest = scope_manifest.build_scope_manifest(
        data_root=settings.data_root, corpus_db_path=db_path
    )
    destination = out if out is not None else settings.data_root / "scope" / "scope.json"
    write_json(destination, manifest)
    if manifest.skipped:
        typer.echo(f"scope-manifest: skipped (no corpus at {db_path}) -> {destination}")
        return
    typer.echo(
        f"scope-manifest: {manifest.cases} public case(s), {manifest.eligible} eligible, "
        f"{manifest.excluded} excluded -> {destination}"
    )


@app.command("corpus-status")
def corpus_status(
    path: Annotated[Path, typer.Argument(help="Repository root to check.")] = Path("."),
) -> None:
    """Check the committed corpus + metrics bookkeeping is consistent (offline).

    The CI gate has no corpus remote or credentials, so it cannot diff the
    corpus blob against S3. This is the offline half that can run there: it
    confirms the corpus blob is gitignored and absent from git — so it can
    never slip into the repo — that the committed ``corpus/corpus.db.ref``
    pointer (when present) is well-formed, and that every metrics roll-up is
    on disk and committed. When the corpus blob is present locally it also
    checks the file's physical layout against the ranged-read contract (64 KB
    pages, non-WAL at rest) so a drifted file fails loudly before it is
    pushed. Exits non-zero and lists every problem if the bookkeeping has
    drifted. The online pull/push side belongs to the data workflows that
    hold the remote credentials.
    """
    is_tracked, is_ignored = repo_gate.git_checkers(path)
    errors = repo_gate.check_state(path, is_tracked=is_tracked, is_ignored=is_ignored)
    if errors:
        for err in errors:
            typer.echo(f"corpus-status: {err}", err=True)
        typer.echo(f"\n{len(errors)} corpus bookkeeping problem(s)", err=True)
        raise typer.Exit(code=1)
    pointer = "pointer present" if (path / repo_gate.CORPUS_POINTER).is_file() else "no pointer yet"
    typer.echo(
        f"OK: corpus bookkeeping consistent ({repo_gate.CORPUS_BLOB} out of git, {pointer}, "
        f"{len(repo_gate.METRICS_ARTIFACTS)} metrics artifact(s) committed)"
    )


def _require_corpus_remote_url() -> str:
    """The out-of-band corpus remote URL, or a loud CLI exit when unset."""
    remote_url = get_settings().corpus_remote_url
    if remote_url is None or not remote_url.strip():
        typer.echo(
            "corpus remote URL is not configured; set CORPUS_REMOTE_URL "
            "(the same out-of-band value the workflows use — see SECURITY.md)",
            err=True,
        )
        raise typer.Exit(code=1)
    return remote_url.strip()


@app.command("corpus-pull")
def corpus_pull(
    missing_pointer: Annotated[
        str,
        typer.Option(
            help="What to do when no corpus pointer is committed: 'fail' the "
            "command, or 'warn' and exit cleanly (writers: a fresh repo starts "
            "an empty corpus)."
        ),
    ] = "fail",
) -> None:
    """Download the corpus index blob from the remote, checksum-verified.

    Resolves the committed ``corpus/corpus.db.ref`` pointer against the
    out-of-band remote URL, streams the blob to ``corpus/corpus.db``, and
    verifies its digest and size before the file lands — a truncated or
    corrupted transfer fails loudly instead of masquerading as the corpus.
    """
    if missing_pointer not in {"fail", "warn"}:
        typer.echo(f"--missing-pointer must be 'fail' or 'warn', not {missing_pointer!r}", err=True)
        raise typer.Exit(code=2)
    db_path = corpus.corpus_db_path(get_settings().corpus_root)
    try:
        pointer = corpus_ranged.find_pointer(db_path)
    except corpus_ranged.RangedBackendError as exc:
        if missing_pointer == "warn":
            typer.echo("No corpus pointer yet; starting a fresh corpus.")
            return
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    remote_url = _require_corpus_remote_url()
    try:
        remote = corpus_remote.download_index(pointer, remote_url, db_path)
    except (corpus_remote.CorpusRemoteError, corpus_ranged.RangedBackendError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    # Deliberately no remote key in the log line: the joined key carries the
    # remote URL's path prefix, which is supplied out of band and never
    # published (see SECURITY.md); size + verified digest identify the pull.
    typer.echo(f"pulled {db_path} ({remote.size} bytes, sha256-verified, {remote.checksum})")


@app.command("corpus-push")
def corpus_push() -> None:
    """Publish the corpus index blob to the remote and rewrite the pointer.

    Digests ``corpus/corpus.db``, uploads it to its content-addressed key
    (put-if-absent: the remote stays add-only, every version immutable), and
    only then rewrites ``corpus/corpus.db.ref`` — so a committed pointer
    always resolves against the remote. The writer workflows commit the
    pointer after this command returns. Rebuilds the file to the ranged-read
    layout first if it drifted (the same guarantee every writer command gives).
    """
    db_path = corpus.corpus_db_path(get_settings().corpus_root)
    remote_url = _require_corpus_remote_url()
    try:
        _ensure_corpus_layout(db_path)
        pointer = corpus_remote.upload_index(db_path, remote_url)
    except (corpus_remote.CorpusRemoteError, corpus_ranged.RangedBackendError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(
        f"pushed {db_path} ({pointer.size} bytes) to {pointer.key}; "
        f"pointer rewritten at {corpus_remote.pointer_path_for(db_path)}"
    )


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
    each reported **per stratum** (forward forecasts vs retrospective cells vs
    procedural mootness-basis cells, never blended and with only the timing
    strata ranked; see the ``Leaderboard`` schema) — and
    writes it through the shared serializer for minimal diffs. Reruns over an
    unchanged ledger reproduce the file byte for byte.
    """
    settings = get_settings()
    board = build_leaderboard(
        iter_stratified_evaluations(settings.data_root),
        big_case=big_case_agreement(settings.data_root),
    )
    destination = out if out is not None else settings.metrics_root / "leaderboard.json"
    write_json(destination, board)
    typer.echo(
        f"leaderboard: {board.predictors_ranked} predictor(s) from "
        f"{board.evaluations_total} evaluation(s) "
        f"({board.forward_evaluations} forward / "
        f"{board.retrospective_evaluations} retrospective / "
        f"{board.procedural_evaluations} procedural) -> {destination}"
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
    after a corpus pull) or carries no resolved events.
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
            "claude-code, codex, gemini) routes every predictor through that one backend "
            "(offline runs / single-engine sweeps). Omit to score only the offline "
            "reference baselines."
        ),
    ] = "",
    skip_engines: Annotated[
        str,
        typer.Option(
            help="Comma-separated engines to opt out of the replay (e.g. 'gemini'), by "
            "the predictor's own configured engine. The default runs every enabled "
            "predictor's engine — the three-engine comparison. An engine whose CLI "
            "binary turns out to be missing is dropped loudly at run time regardless."
        ),
    ] = "",
    scope: Annotated[
        str,
        typer.Option(
            help="Population to back-test: 'all' every modern-cert petition (raw predictor "
            "quality); 'paid' the paid segment the salience gate scores (drops IFP); "
            "'selected' the gate's carve-out core (CVSG or at/above the salience floor) — "
            "the N-independent core of the live selected slice (which also fills to N by "
            "rank), the closest replay-safe like-for-live read."
        ),
    ] = "all",
    spread: Annotated[
        bool,
        typer.Option(
            "--spread/--no-spread",
            help="Sample across conference cohorts (a full term's live cadence) instead of "
            "the most recently decided N, which collapses onto the last, grant-heavy order "
            "lists. Applies within --limit.",
        ),
    ] = False,
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
    floor** and a P(granted) calibration view, alongside accuracy and Brier.
    ``--scope selected`` restricts the set to the salience gate's paid carve-out
    core — the ``N``-independent core of the live selected slice (which also fills
    to ``N`` by rank) — and ``--spread`` samples across conferences rather than the
    last order lists, together the closest replay-safe like-for-live read instead
    of a grant-heavy term-end snapshot. The
    offline reference baselines always run; ``--engine`` additionally replays
    every enabled predictor over redacted snapshots in a scratch tree, each
    through its own configured engine under ``auto`` (this spends tokens on a
    real engine). Petitions the corpus cannot replay (no held snapshot or
    petition event — partial coverage is the norm while the historical walk
    drains) are dropped up front and named, so every backtester in one report is
    scored over the same set. Out of band by design: it never writes the
    ``data/`` ledger, and the report is labeled retrospective (the outcomes
    predate every modern model's training cutoff).
    """
    if scope not in CERT_BACKTEST_SCOPES:
        raise typer.BadParameter(
            f"unknown scope {scope!r}; choose one of {', '.join(CERT_BACKTEST_SCOPES)}",
            param_hint="--scope",
        )
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    destination = out if out is not None else settings.metrics_root / "cert-backtest.json"
    if not db_path.exists():
        write_json(destination, run_cert_backtest([], []))
        typer.echo(f"No corpus at {db_path} — wrote empty cert back-test report -> {destination}")
        return
    with corpus.connect(db_path) as conn:
        items = select_cert_backtest_set(
            conn,
            limit=limit,
            scope=scope,
            spread=spread,
            salience_floor=load_salience_config(settings.config_root).floor,
        )
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
            skipped_engines = frozenset(e.strip() for e in skip_engines.split(",") if e.strip())
            known_engines = {
                str(p.engine) for p in enabled_predictors(settings.config_root / "predictors.yaml")
            }
            unknown_engines = skipped_engines - known_engines
            if unknown_engines:
                # Fail on a typo rather than silently run the engine you meant to
                # skip (a billable footgun) — the same contract --engine has.
                raise typer.BadParameter(
                    f"unknown engine(s): {', '.join(sorted(unknown_engines))}; enabled "
                    f"engines are {', '.join(sorted(known_engines))}",
                    param_hint="--skip-engines",
                )
            if skipped_engines:
                typer.echo(
                    "opted out of engine(s): " + ", ".join(sorted(skipped_engines)), err=True
                )
            replayed, unavailable = replay_predictors(
                items,
                corpus_db_path=db_path,
                config_root=settings.config_root,
                work_root=work_root,
                engine_override=None if engine == "auto" else engine,
                skip_engines=skipped_engines,
                run_id=ids.run_id(),
            )
            for pid in unavailable:
                typer.echo(
                    f"dropped predictor {pid}: its engine's CLI was not available at run time",
                    err=True,
                )
            replayed_ids = {b.id for b in replayed}
            for predictor in enabled_predictors(settings.config_root / "predictors.yaml"):
                if (
                    predictor.id not in replayed_ids
                    and predictor.id not in unavailable
                    and str(predictor.engine) not in skipped_engines
                ):
                    typer.echo(
                        f"skipped predictor {predictor.id}: engine "
                        f"{predictor.engine} has no registered runner",
                        err=True,
                    )
            backtesters += replayed
        # The leakage-safe segment context (band + per-Term base rate) mirrors
        # the forward stratum's yardstick; segment_base_rate masks each item to
        # Terms strictly before its own, so a full-corpus statpack is safe here.
        statpack = analytics.build_statpack(corpus_db_path=db_path)
        segments = build_segment_context(conn, items, statpack)
        report = run_cert_backtest(backtesters, items, segments=segments)
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

    An independent published artifact, two populations side by side: the
    full-corpus overview (cases by court, SCOTUS by era — bulk import included,
    labeled so) and the live/historical-slice cert statistics the predict and
    evaluate prompts anchor on — denial-reweighted disposition base rates, cuts
    by originating circuit / relist count / CVSG status, and per-Term detail
    with a cursor-derived filings census, per-fee-class estimates, and
    walk-complete flags. Deterministic and offline: a pure function of the
    corpus, so reruns reproduce both files byte for byte. Writes the empty
    zero-count pack when the corpus is absent (run after a corpus pull).
    Git-tracked alongside `leaderboard` / `backtest`.
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
    pipeline_sha: Annotated[
        str,
        typer.Option(
            help="Pipeline checkout commit (provenance); defaults to GITHUB_SHA, "
            "then the local git HEAD, else omitted."
        ),
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
        pipeline_sha=resolve_pipeline_sha(pipeline_sha),
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


@app.command("record-retrieval")
def record_retrieval(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to inputs
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id this run predicted/scored.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    engine: Annotated[Engine, typer.Option(help="Engine that ran (claude-code | codex | gemini).")],
    role: Annotated[UsageRole, typer.Option(help="predictor (predict) | evaluator (evaluate).")],
    actor: Annotated[str, typer.Option(help="The predictor_id or evaluator_id for this cell.")],
    mode: Annotated[
        str, typer.Option(help="The cell's provisioned mode: forward | replay ('' = unknown).")
    ] = "",
    claude_execution_file: Annotated[
        Path | None, typer.Option(help="Claude Code execution_file JSON to read tool calls from.")
    ] = None,
    codex_sessions_dir: Annotated[
        Path | None, typer.Option(help="Codex sessions dir (CODEX_HOME/sessions) to read.")
    ] = None,
    gemini_telemetry_file: Annotated[
        Path | None, typer.Option(help="Gemini CLI telemetry.log to read tool calls from.")
    ] = None,
) -> None:
    """Record the cell's tool-call transcript to ``retrieval_log.json``.

    The load-bearing half of the leakage doctrine: the log is harvested from
    the engine's own transcript (the same sources ``record-usage`` reads),
    never the agent's word, so the cross-evaluator's leakage grading can see what a replay cell
    actually retrieved. The pinned tool manifest the cell was configured with
    (from the actor's registry entry) is snapshotted alongside — the
    pipeline-attribution record. A cell with zero tool calls still records an
    empty log: "retrieved nothing" is itself evidence.
    """
    settings = get_settings()
    calls: list[RetrievalCall] = []
    if claude_execution_file is not None:
        calls = retrieval.parse_claude_retrieval(claude_execution_file)
    elif codex_sessions_dir is not None:
        calls = retrieval.parse_codex_retrieval(codex_sessions_dir)
    elif gemini_telemetry_file is not None:
        calls = retrieval.parse_gemini_retrieval(gemini_telemetry_file)

    registry_file = settings.config_root / (
        "predictors.yaml" if role == UsageRole.predictor else "evaluators.yaml"
    )
    labels: list[str] = []
    try:
        actors: list[Any] = (
            load_predictors(registry_file)
            if role == UsageRole.predictor
            else load_evaluators(registry_file)
        )
        match = next((a for a in actors if a.id == actor), None)
        if match is not None:
            servers = resolve_mcp_servers(load_mcp_servers(registry_file), match.mcp_servers)
            labels = mcp.manifest_labels(servers)
    except (OSError, KeyError):
        # Attribution is best-effort here: a registry drift must not lose the
        # harvested calls (the plan already validated the registry).
        labels = []

    record = RetrievalLog(
        case_id=ids.case_id(court, docket),
        run_id=run_id,
        role=role,
        actor_id=actor,
        engine=engine,
        mode=mode or None,
        mcp_servers=labels,
        calls=calls,
    )
    event_paths = CasePaths(settings.data_root, court, docket).event(event)
    destination = (
        event_paths.prediction_retrieval_log(actor, run_id)
        if role == UsageRole.predictor
        else event_paths.evaluation_retrieval_log(actor, run_id)
    )
    write_json(destination, record)
    typer.echo(f"retrieval: {actor} {len(calls)} call(s) -> {destination}")


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


def _read_best_effort[T: BaseModel](path: Path | None, model: type[T]) -> T | None:
    """Read and validate a published feed, best-effort: any miss just drops it.

    A missing file, unreadable JSON, or an incompatible earlier shape (the
    models are strict) returns ``None`` — a degraded feed degrades its section,
    never the report.
    """
    if path is None or not path.exists():
        return None
    try:
        return model.model_validate_json(path.read_text())
    except ValueError:
        return None


@app.command("ops-report")
def ops_report(  # noqa: PLR0913 - one option per independent read-only feed
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
    live_frontier: Annotated[
        Path | None,
        typer.Option(
            help="Latest `live-frontier` JSON (e.g. from the ops-metrics branch) for the "
            "substance section's watchlist-readiness view. Ignored if missing or unreadable."
        ),
    ] = None,
    previous: Annotated[
        Path | None,
        typer.Option(
            help="Prior OpsReport JSON (e.g. from the ops-metrics branch) for the "
            "substance section's deltas. Ignored if missing, unreadable, or from "
            "an incompatible earlier shape."
        ),
    ] = None,
    digest_out: Annotated[
        Path | None,
        typer.Option(
            help="Write the weekly maintainer digest Markdown here (the short "
            "interrogative comment the run-ops weekly schedule posts)."
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
    """Roll pipeline health, substance, spend, and data health into an ops snapshot.

    A read-only view of authoritative sources — the GitHub Actions run history
    (``--runs``), the recorded ``usage.json`` ledger under ``data/``, the
    committed ``flags.json`` files agents leave there (rolled into the **open
    agent flags** section), and the committed metrics artifacts (the statpack's
    deny base rate). The **substance** section answers "is the machine producing
    anything good": scored cells by stratum (with deltas against ``--previous``),
    replay calibration vs the deny base rate, per-predictor score distributions,
    and the published ``--live-frontier`` readiness snapshot. Also presents the
    **data-health** verdict: it runs the git-only ``validate`` over ``data/``
    itself and folds in the latest corpus verdict from ``--corpus-validation``
    (produced where the corpus is already pulled). Prints the dashboard Markdown
    to stdout (the run-ops issue body / step summary); ``--json`` writes the
    structured ``OpsReport`` and ``--digest-out`` the weekly maintainer digest.
    Unlike the leaderboard/back-test roll-ups it is a point-in-time snapshot, so
    it is surfaced, not committed.
    """
    settings = get_settings()
    run_rows = json.loads(runs.read_text()) if runs is not None else []
    # Data health: the git-only ledger schema check always runs here (no corpus
    # needed), and the corpus verdict is read back from the producer path if present
    # (best-effort: a missing/unreadable verdict just leaves that half null).
    corpus_verdict = _read_best_effort(corpus_validation, CorpusValidation)
    ledger = validate_ledger(settings.data_root)
    data_health = DataHealth(
        ok=ledger.ok and (corpus_verdict is None or corpus_verdict.ok),
        ledger=ledger,
        corpus=corpus_verdict,
    )
    # The live-frontier snapshot is surfaced like the corpus verdict: read back from
    # the producer path if published. The prior snapshot is additionally
    # shape-lenient: an older snapshot carrying since-removed fields (OpsReport is
    # strict) fails validation and just drops the deltas — never the report. The
    # statpack is a committed metrics artifact; its modern-cert section anchors
    # the calibration view.
    frontier = _read_best_effort(live_frontier, LiveFrontier)
    prior = _read_best_effort(previous, OpsReport)
    statpack = _read_best_effort(settings.metrics_root / "statpack.json", StatPack)
    # Open run:* trigger issues (stalled fan-outs), best-effort like the other feeds:
    # a missing/unreadable file just drops the section.
    open_triggers = None
    if trigger_issues is not None and trigger_issues.exists():
        try:
            open_triggers = summarize_trigger_issues(json.loads(trigger_issues.read_text()))
        except (ValueError, TypeError):
            open_triggers = None
    when = generated_at or datetime.now(UTC).isoformat()
    stratified = iter_stratified_evaluations(settings.data_root)
    substance = summarize_substance(
        cell_counts=ledger_cell_counts(settings.data_root),
        stratified_evaluations=stratified,
        statpack=statpack,
        live_frontier=frontier,
        previous=prior,
    )
    report = build_ops_report(
        generated_at=when,
        runs=run_rows,
        usage=iter_usage(settings.data_root),
        flags=iter_flags(settings.data_root),
        tooling=iter_tooling(settings.data_root),
        evaluations=[e for e, _ in stratified],
        substance=substance,
        data_health=data_health,
        open_triggers=open_triggers,
    )
    if json_out is not None:
        write_json(json_out, report)
    if data_health_out is not None:
        data_health_out.parent.mkdir(parents=True, exist_ok=True)
        data_health_out.write_text(render_data_health(data_health))
    if digest_out is not None:
        digest_out.parent.mkdir(parents=True, exist_ok=True)
        digest_out.write_text(render_weekly_digest(report))
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


@app.command("mcp-config")
def mcp_config_cmd(
    engine: Annotated[
        str, typer.Option(help="Which client format to emit: claude-code | codex | gemini.")
    ],
    role: Annotated[
        str, typer.Option(help="Registry to read: predictor (predictors.yaml) | evaluator.")
    ],
    actor: Annotated[str, typer.Option(help="The predictor/evaluator id whose manifest to emit.")],
    base_settings: Annotated[
        Path | None,
        typer.Option(
            help="gemini only: existing settings.json to merge mcpServers into "
            "(preserves the telemetry block the usage capture reads)."
        ),
    ] = None,
    http_url: Annotated[
        list[str] | None,
        typer.Option(
            help="Emit this server as a remote streamable-HTTP entry instead of a "
            "stdio launch: '<id>=<url>', repeatable. The config then carries only "
            "the URL — no launch command and no token (the mcp-serve sidecar "
            "holds it)."
        ),
    ] = None,
) -> None:
    """Emit one engine's MCP client config from the versioned tool manifest.

    The single seam between the registry's ``mcp_servers`` manifest and the
    three engines' client formats (Claude ``--mcp-config`` JSON, Codex
    ``config.toml`` tables, Gemini ``settings.json``), so the workflow steps
    only plumb stdout to a file. For stdio entries, token values are injected
    from THIS process's environment (see ``fedcourtsai.mcp``); run it in a
    step whose env holds the tokens the manifest names. ``--http-url``
    entries carry no token at all — the sidecar does. An actor with an empty
    manifest emits an empty config — a cell without retrieval is a valid
    configuration, not an error.
    """
    settings = get_settings()
    if role not in ("predictor", "evaluator"):
        typer.echo(f"unknown --role '{role}'; choose predictor or evaluator", err=True)
        raise typer.Exit(code=2)
    http_urls: dict[str, str] = {}
    for entry in http_url or []:
        server_id, separator, url = entry.partition("=")
        if not separator or not server_id or not url:
            typer.echo(f"malformed --http-url '{entry}'; expected '<id>=<url>'", err=True)
            raise typer.Exit(code=2)
        http_urls[server_id] = url
    registry_file = settings.config_root / (
        "predictors.yaml" if role == "predictor" else "evaluators.yaml"
    )
    actors: list[Any] = (
        load_predictors(registry_file) if role == "predictor" else load_evaluators(registry_file)
    )
    match = next((a for a in actors if a.id == actor), None)
    if match is None:
        typer.echo(f"no {role} '{actor}' in {registry_file}", err=True)
        raise typer.Exit(code=2)
    try:
        servers = resolve_mcp_servers(load_mcp_servers(registry_file), match.mcp_servers)
    except KeyError as exc:
        typer.echo(f"manifest id {exc} not in {registry_file} mcp_servers", err=True)
        raise typer.Exit(code=2) from exc
    # Fail closed on drift between the caller's --http-url ids and the
    # resolved manifest: a typo'd id would otherwise silently fall back to a
    # per-client stdio spawn, bypassing the sidecar.
    unknown = sorted(set(http_urls) - {server.id for server in servers})
    if unknown:
        typer.echo(f"--http-url names no resolved manifest server: {', '.join(unknown)}", err=True)
        raise typer.Exit(code=2)
    if engine == "claude-code":
        typer.echo(mcp.claude_mcp_config(servers, http_urls=http_urls), nl=False)
    elif engine == "codex":
        typer.echo(mcp.codex_mcp_config(servers, http_urls=http_urls), nl=False)
    elif engine == "gemini":
        base = json.loads(base_settings.read_text()) if base_settings else None
        typer.echo(mcp.gemini_mcp_settings(servers, base, http_urls=http_urls), nl=False)
    else:
        typer.echo(f"unknown --engine '{engine}'", err=True)
        raise typer.Exit(code=2)


@app.command("mcp-serve")
def mcp_serve(
    role: Annotated[
        str, typer.Option(help="Registry to read: predictor (predictors.yaml) | evaluator.")
    ],
    actor: Annotated[str, typer.Option(help="The predictor/evaluator id whose manifest to read.")],
    server: Annotated[
        str, typer.Option(help="Manifest id of the server to run.")
    ] = "courtlistener",
    port: Annotated[
        int, typer.Option(help="Loopback port to serve on.")
    ] = mcp.MCP_SIDECAR_DEFAULT_PORT,
) -> None:
    """Run one manifest server as the tokenless HTTP sidecar (foreground).

    The write side of ``mcp-config --http-url``: the cell workflows launch
    this as a background step whose env holds the server's API token, so the
    token lives in this process — never in a client config file an agent can
    read. Replaces the current process with the pinned server (uvx) — the
    same package and shim family the stdio transport launches, in HTTP mode
    on localhost (see ``fedcourtsai.mcp``).
    """
    settings = get_settings()
    if role not in ("predictor", "evaluator"):
        typer.echo(f"unknown --role '{role}'; choose predictor or evaluator", err=True)
        raise typer.Exit(code=2)
    registry_file = settings.config_root / (
        "predictors.yaml" if role == "predictor" else "evaluators.yaml"
    )
    actors: list[Any] = (
        load_predictors(registry_file) if role == "predictor" else load_evaluators(registry_file)
    )
    match = next((a for a in actors if a.id == actor), None)
    if match is None:
        typer.echo(f"no {role} '{actor}' in {registry_file}", err=True)
        raise typer.Exit(code=2)
    try:
        servers = resolve_mcp_servers(load_mcp_servers(registry_file), match.mcp_servers)
    except KeyError as exc:
        typer.echo(f"manifest id {exc} not in {registry_file} mcp_servers", err=True)
        raise typer.Exit(code=2) from exc
    entry = next((s for s in servers if s.id == server), None)
    if entry is None:
        typer.echo(f"{role} '{actor}' has no manifest server '{server}'", err=True)
        raise typer.Exit(code=2)
    try:
        command, args, env = mcp.http_sidecar_launch(entry, port=port)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(f"serving MCP '{entry.id}' ({entry.package}) on http://127.0.0.1:{port}")
    os.execvpe(command, [command, *args], {**os.environ, **env})


CorpusBackendOption = Annotated[
    str,
    typer.Option(
        "--corpus-backend",
        help="Corpus read backend: local (the pulled file) or ranged (query "
        "the blob in place on the corpus remote); query/open-events also accept "
        "service (forward to a corpus query sidecar — see corpus-serve), and "
        "the provisioning commands casestore (read the per-case content "
        "objects). Default: the corpus-backend setting from the environment.",
    ),
]


def _corpus_backend(
    value: str, *, allow_casestore: bool = False, allow_service: bool = False
) -> corpus.CorpusBackend | None:
    """Parse a --corpus-backend value; empty means \"use the setting\".

    ``casestore`` is a provisioning-only backend (it has no query surface), so it is
    accepted only where ``allow_casestore`` is set — the read commands reject it
    cleanly here rather than crashing later in ``connect_readonly``. ``service``
    is likewise accepted only by the commands that can forward to the corpus
    query service (``query`` / ``open-events``).
    """
    if not value:
        return None
    if value == "local":
        return "local"
    if value == "ranged":
        return "ranged"
    if value == "casestore" and allow_casestore:
        return "casestore"
    if value == "service" and allow_service:
        return "service"
    extras = [
        name for name, ok in (("casestore", allow_casestore), ("service", allow_service)) if ok
    ]
    choices = ", ".join(["local", "ranged", *extras])
    typer.echo(f"Unsupported --corpus-backend '{value}'; choose {choices}.", err=True)
    raise typer.Exit(code=2)


def _service_url_or_exit() -> str:
    """The configured corpus-service URL, or a clean exit when unset."""
    url = get_settings().corpus_service_url
    if not url:
        typer.echo(
            "the service backend needs FEDCOURTS_CORPUS_SERVICE_URL (the "
            "corpus-serve sidecar's base URL)",
            err=True,
        )
        raise typer.Exit(code=2)
    return url


def _echo_service_read_stats(reads: corpus_service.ReadCounters | None) -> None:
    """Report a service response's transfer counters to stderr.

    The same evidence line :func:`_echo_read_stats` prints for a direct ranged
    connection, relayed from the sidecar's per-request delta. ``None`` (the
    sidecar reads a local file) stays silent, matching the local path; a warm
    sidecar cache honestly reports ``0 GET(s)``.
    """
    if reads is not None:
        typer.echo(f"ranged corpus reads: {reads.gets} GET(s), {reads.bytes} byte(s)", err=True)


def _casestore_source() -> provision.CasestoreSource:
    """Build the casestore provisioning source, exiting cleanly if it is unconfigured."""
    try:
        return provision.casestore_source_from_settings()
    except provision.ProvisionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc


def _provision_backend(value: str) -> corpus.CorpusBackend:
    """The effective backend for a forward-cell provisioning read.

    An explicit ``--corpus-backend`` always wins. Otherwise, with the corpus-split
    mode on (:attr:`Settings.corpus_split`), the forward provisioners read the
    per-case content store *by default* — so a cutover flips the whole fleet with
    one setting rather than threading ``casestore`` onto every cell command. With
    the mode off it falls back to the ordinary corpus-backend setting (``local`` /
    ``ranged``), i.e. today's behavior.
    """
    override = _corpus_backend(value, allow_casestore=True)
    if override is not None:
        return override
    if get_settings().corpus_split:
        return "casestore"
    return corpus.resolve_backend(None)


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
    workflow pushes always satisfies the layout contract ``corpus-status``
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
        f"resolved={len(result.resolved)} unrecorded={len(result.unrecorded)}"
    )


@app.command()
def pull(
    court: Annotated[str, typer.Option(help="CourtListener court id, e.g. ca9 or scotus.")],
    docket: Annotated[int, typer.Option(help="CourtListener docket id.")],
) -> None:
    """Onboard or refresh one docket from the CourtListener REST API.

    Deterministic single-docket ingestion of raw facts: fetches the docket,
    re-ingests it into the corpus through the shared core, and reports whether
    it changed since the last pull (the signal that downstream ``run-predict``
    should run). The first pull of a docket onboards it.
    """
    _fetch_one_docket(court, docket)


@app.command("probe-live-terms")
def probe_live_terms(
    max_term: Annotated[
        int,
        typer.Option(help="Newest two-digit October Term to probe (e.g. 25 for OT2025)."),
    ],
    min_term: Annotated[
        int,
        typer.Option(help="Oldest two-digit October Term to probe (inclusive)."),
    ],
    numbers: Annotated[
        str,
        typer.Option(help="Comma-separated docket numbers sampled per Term (paid and IFP ranges)."),
    ] = ",".join(str(n) for n in liveprobe.DEFAULT_SAMPLE_NUMBERS),
    throttle: Annotated[
        float,
        typer.Option(help="Seconds to sleep between requests (polite-client pacing)."),
    ] = 1.0,
    report_out: Annotated[
        Path | None,
        typer.Option(help="Also write the machine per-Term/per-record JSON here."),
    ] = None,
    summary_out: Annotated[
        Path | None,
        typer.Option(help="Append the Markdown findings table here (e.g. $GITHUB_STEP_SUMMARY)."),
    ] = None,
) -> None:
    """Probe supremecourt.gov docket-JSON availability per October Term.

    The live-sources reachability probe: for each Term from ``--max-term`` back
    to ``--min-term`` it fetches a small sample of docket numbers and reports
    availability, document-link coverage, schema stability, and whether the
    proceedings text carries machine-matchable disposition orders. Strictly
    **read-only** and budget-free: this is the supremecourt.gov channel, not the
    CourtListener client — no token, no governor; writes nothing but the report
    files named. Findings re-establish the Term-floor and disposition-resolver
    recall conclusions recorded in ``docs/live-sources.md``.
    """
    if min_term > max_term:
        typer.echo("--min-term must not exceed --max-term", err=True)
        raise typer.Exit(code=2)
    try:
        sample = [int(n) for n in numbers.split(",") if n.strip()]
    except ValueError as exc:
        typer.echo(f"bad --numbers value: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    terms = range(max_term, min_term - 1, -1)
    summaries, records = liveprobe.probe_terms(terms, sample, throttle_seconds=throttle)
    table = liveprobe.render_markdown(summaries)
    payload = {
        "terms": [t.model_dump(mode="json") for t in summaries],
        "records": [r.model_dump(mode="json") for r in records],
    }
    typer.echo(json.dumps(payload, indent=2))
    typer.echo(table, err=True)
    if report_out is not None:
        write_raw_json(report_out, payload)
    if summary_out is not None:
        with summary_out.open("a", encoding="utf-8") as fh:
            fh.write(table + "\n")


@app.command("historical-terms")
def historical_terms(
    report: Annotated[
        Path | None,
        typer.Option(help="Write this invocation's JSON report here for the workflow's loop."),
    ] = None,
    totals: Annotated[
        Path | None,
        typer.Option(
            help="Fold this invocation's counts into the cumulative JSON report at "
            "this path (created if absent) — the historical loop's whole-run totals, "
            "which its single step summary renders."
        ),
    ] = None,
    max_probes: Annotated[
        int | None,
        typer.Option(
            help="Optional lower cap on docket-JSON probes this invocation; cannot "
            "exceed historical.max_probes_per_run."
        ),
    ] = None,
    max_run_seconds: Annotated[
        int | None,
        typer.Option(
            min=1,
            help="Optional lower cap on this invocation's wall-clock budget, seconds; "
            "cannot exceed historical.max_run_minutes. The run-seed walk loop "
            "passes the budget still remaining so the final chunk stops itself "
            "(stopped=time-cap) before the job's hard timeout instead of overrunning "
            "it and being killed mid-chunk. Must be >= 1: a non-positive budget would "
            "make the walk a silent no-op (model_copy bypasses the field's gt=0 check).",
        ),
    ] = None,
    summary_out: Annotated[
        Path | None,
        typer.Option(help="Append the Markdown progress table here (e.g. $GITHUB_STEP_SUMMARY)."),
    ] = None,
) -> None:
    """Load one capped chunk of the historical per-Term set (no agent).

    The historical half of the live channel (docs/live-sources.md): walks the
    configured October Terms' docket serials sequentially over the
    supremecourt.gov docket JSON — resuming from the persisted per-(Term, stream)
    cursors — and ingests **every decided petition except denials, which are
    systematically sampled** (all grants/GVRs kept; a denial kept when its
    serial is a multiple of ``historical.denial_sample_every``). Ingested
    petitions land through the shared live path: identity reconciled by docket
    number, raw JSON snapshotted, the resolved row + ``outcome.json`` recorded,
    and filed documents provisioned for OT``document_floor_term``+ — so they
    feed the statpack's per-Term base rates and replay/evaluation only.
    **Writes no handoff queues**: these are decided historical matters and must
    never queue forward prediction. The ``run-seed`` workflow loops this
    command, committing the corpus after each chunk.
    """
    settings = get_settings()
    cfg = load_historical_config(settings.config_root)
    cap = cfg.max_probes_per_run if max_probes is None else min(max_probes, cfg.max_probes_per_run)
    # The caller can only LOWER the wall-clock budget (mirrors max_probes): the
    # loop feeds its remaining budget so a chunk never runs past the job's hard
    # timeout. Both caps still bound the chunk — whichever binds first stops it.
    run_minutes = (
        cfg.max_run_minutes
        if max_run_seconds is None
        else min(max_run_seconds / 60, cfg.max_run_minutes)
    )
    db = corpus.corpus_db_path(settings.corpus_root)
    with SupremeCourtClient(throttle_seconds=cfg.throttle_seconds) as client:
        rep = historical.load_terms(
            client,
            db,
            settings.data_root,
            cfg.model_copy(update={"max_probes_per_run": cap, "max_run_minutes": run_minutes}),
            today=date.today(),
        )
    _ensure_corpus_layout(db)
    if report is not None:
        write_raw_json(report, rep.model_dump(mode="json"))
    if totals is not None:
        prior = (
            historical.HistoricalReport.model_validate_json(totals.read_text())
            if totals.exists()
            else None
        )
        write_raw_json(totals, historical.fold_totals(prior, rep).model_dump(mode="json"))
    if summary_out is not None:
        with summary_out.open("a", encoding="utf-8") as fh:
            fh.write(historical.render_markdown(rep) + "\n")
    ingested = rep.ingested_granted + rep.ingested_denied + rep.ingested_other
    typer.echo(
        f"historical-terms probed={rep.probed} served={rep.served} ingested={ingested} "
        f"(granted={rep.ingested_granted} denied={rep.ingested_denied} other={rep.ingested_other}) "
        f"skipped_denials={rep.skipped_denials} documents={rep.documents} "
        f"stopped={rep.stopped} complete={rep.complete}"
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
    the packed corpus, which in production is a `corpus-pull` of the S3 remote behind
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
    """Show the corpus location and row count (after `corpus-pull`, or ranged)."""
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend == "local" and not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.")
        return
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        typer.echo(
            f"corpus {db_path} [{backend}]: {corpus.count(conn)} row(s), "
            f"{corpus.snapshot_count(conn)} snapshot(s)"
        )
        _echo_read_stats(conn)


@app.command("build-index")
def build_index_cmd(
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <corpus_root>/index.db)."),
    ] = None,
) -> None:
    """Build the small, payload-stripped index from the corpus blob (corpus split).

    Empties the `snapshots`/`documents` tables and NULLs `cases.opinion_text` (the
    bulk that moves to the per-case content store), keeping every other column
    (including the `has_opinion` presence bit) and the schema. Result-identical for
    the bulk consumers `statpack`/`backtest`/`query` — proven byte-identical by the
    parity gate. Under the corpus-split mode the signal readers are served too: scope
    reconcile / `validate` key on the retained `has_opinion` bit rather than the body,
    and the snapshot readers (scope reconcile's bare-import rule and `cert-backtest`)
    read from the content store via the payload read source. This is a one-shot
    utility — under the split mode the writer already
    produces a payload-free blob, so no per-run build-index is needed.
    """
    settings = get_settings()
    src = corpus.corpus_db_path(settings.corpus_root)
    dst = out if out is not None else corpus_index.index_db_path(settings.corpus_root)
    if not src.exists():
        typer.echo(
            f"No corpus at {src} — `fedcourts corpus-pull` to fetch it from the remote.", err=True
        )
        raise typer.Exit(code=1)
    stats = corpus_index.build_index(src, dst)
    typer.echo(
        f"index: {stats.cases} case(s); dropped {stats.snapshots_dropped} snapshot(s) + "
        f"{stats.documents_dropped} document(s), NULLed {stats.opinions_nulled} opinion(s); "
        f"{stats.src_bytes / 1_000_000:.1f} MB -> {stats.index_bytes / 1_000_000:.1f} MB -> {dst}"
    )


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
        typer.Option(
            help="Reporter citation, e.g. '597 U.S. 1'; repeatable. Matches cases "
            "whose OWN parallel cites overlap — a lookup of specific known cases, "
            "not a cases-citing-this-authority search."
        ),
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
    ``--full``. Reads the pulled file, the blob in place on the remote with
    ``--corpus-backend ranged``, or forwards to a corpus query sidecar with
    ``--corpus-backend service`` (same rows, same read-stats line — a
    transport change, not a different surface).

    Maintained as-is: cells' open-web retrieval moved to the official
    CourtListener MCP server, so this surface gets no further feature work —
    it stays the corpus-priors/base-rates read (the one retrieval a *replay*
    cell leans on) rather than growing into a bespoke search engine.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend, allow_service=True))
    if backend == "local" and not db_path.exists():
        typer.echo(
            f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.",
            err=True,
        )
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
    if backend == "service":
        try:
            response = corpus_service.client_query(
                _service_url_or_exit(), q, limit=limit, full=full
            )
        except corpus_service.CorpusServiceError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
        _echo_service_read_stats(response.reads)
        for note in response.notes:
            typer.echo(f"note: {note}", err=True)
        for payload in response.rows:
            typer.echo(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        priors = corpus.retrieve_priors(conn, q, limit=limit)
        if not priors and limit > 0:
            for note in corpus.sparse_filter_coverage(conn, q):
                typer.echo(f"note: {note}", err=True)
        _echo_read_stats(conn)
    for row in priors:
        typer.echo(
            json.dumps(corpus.prior_payload(row, full=full), sort_keys=True, separators=(",", ":"))
        )


@app.command("corpus-serve")
def corpus_serve(
    corpus_backend: CorpusBackendOption = "",
    host: Annotated[
        str, typer.Option(help="Interface to bind; keep the localhost default.")
    ] = "127.0.0.1",
    port: Annotated[
        int, typer.Option(help="Port to bind (0 = an ephemeral port).")
    ] = corpus_service.DEFAULT_PORT,
) -> None:
    """Serve corpus `query`/`open-events` over localhost HTTP (the sidecar).

    The read side of the ``service`` backend: this process holds the one
    corpus connection (and, on the ranged backend, the cloud credentials from
    *its* environment), so callers pointing ``FEDCOURTS_CORPUS_SERVICE_URL``
    at it — agent cells above all — query the corpus holding no credentials
    at all. Runs until interrupted; built for the cell workflows to launch as
    a background step, and locally it pairs with
    ``FEDCOURTS_CORPUS_BACKEND=service`` for a tokenless `query`.
    """
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend not in ("local", "ranged"):
        typer.echo(f"corpus-serve serves the local or ranged backend, not '{backend}'.", err=True)
        raise typer.Exit(code=2)
    if host not in ("127.0.0.1", "localhost", "::1"):
        typer.echo(
            f"warning: binding {host} serves the corpus beyond localhost, unauthenticated",
            err=True,
        )
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if backend == "local" and not db_path.exists():
        typer.echo(
            f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.",
            err=True,
        )
        raise typer.Exit(code=1)
    try:
        server = corpus_service.create_server(db_path, backend=backend, host=host, port=port)
    except OSError as exc:
        typer.echo(f"could not bind http://{host}:{port}: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    bound_port = server.server_address[1]
    typer.echo(f"corpus service listening on http://{host}:{bound_port} [{backend}]")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        # Ctrl-C is the sidecar's normal shutdown, not an error: fall through
        # to the close below and exit 0.
        pass
    finally:
        server.server_close()


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
        typer.Option(
            help="Reporter citation, e.g. '597 U.S. 1'; repeatable. Matches cases "
            "whose OWN parallel cites overlap — a lookup of specific known cases, "
            "not a cases-citing-this-authority search."
        ),
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
    """Aggregate corpus disposition base-rates, overall and by a dimension (corpus on disk).

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
    role: Annotated[
        str,
        typer.Option(
            help="Cell role: predictor | evaluator. The realized outcome path is "
            "resolved only for an evaluator (a predictor never reads it).",
        ),
    ] = "",
) -> None:
    """Print resolved paths for a case (or event). Useful in scripts.

    Raw facts live in the packed corpus, not per-case git files; git holds only
    the derived ledger (events, outcomes, predictions, evaluations).

    The realized ``outcome.json`` is the evaluator's ground truth — never a
    predictor input. It is resolved only for ``--role evaluator``; a predictor
    (the default) is not shown the path, so the forward cell's input surface
    never names the answer file even if a resolved event slips into its queue.
    """
    settings = get_settings()
    cp = CasePaths(settings.data_root, court, docket)
    typer.echo(f"case_id   {ids.case_id(court, docket)}")
    typer.echo(f"corpus    {corpus.corpus_db_path(settings.corpus_root)}")
    if event:
        ep = cp.event(event)
        typer.echo(f"event     {ep.event_file}")
        if role == "evaluator":
            typer.echo(f"outcome   {ep.outcome}")
        else:
            typer.echo("outcome   (evaluator-only — never a predictor input)")


@app.command("provision-snapshot")
def provision_snapshot(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    out: Annotated[
        Path | None,
        typer.Option(help="Where to write the snapshot; defaults to the case's record path."),
    ] = None,
    mode: Annotated[
        str,
        typer.Option(
            help="The cell's mode, written into record/context.json: forward "
            "(a live cell — the default) | replay (a back-test cell; the replay "
            "provisioner in cert_backtest writes this itself)."
        ),
    ] = "forward",
    refuse_terminal: Annotated[
        bool,
        typer.Option(
            "--refuse-terminal",
            help="Refuse (exit 3, writing nothing) when the snapshot already "
            "shows the outcome — the latest entry reads terminal, or any "
            "entry carries a machine-readable disposition order. A forward "
            "*prediction* cell must never see a decided docket. Only "
            "run-predict passes this: an evaluate cell targets exactly "
            "decided dockets, so the default provisions unconditionally.",
        ),
    ] = False,
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Materialize a case's latest corpus snapshot (and documents) for an agent run.

    Point-in-time snapshots are raw facts that live in the packed corpus, not
    git. The predict/evaluate workflows call this to read the most
    recent dated snapshot for the case out of the corpus — the pulled
    file, or the blob in place on the remote with ``--corpus-backend ranged``, or
    the per-case content store (``--corpus-backend casestore``, the default under
    the corpus-split mode) — and write it where the agent reads it (a gitignored
    ``record/`` path, never committed). Any stored filed-document text (petition,
    questions presented, brief in opposition — fetched pipeline-side by the live poller) is
    materialized alongside, under ``record/documents/`` with a
    ``documents.json`` manifest, so the cell reads identical content with no
    fetch rights. Exits non-zero if the corpus holds no snapshot for the case
    (code 1), or — under ``--refuse-terminal`` on a forward cell — if the
    snapshot already reads decided (code 3, nothing written).
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    case = ids.case_id(court, docket)
    backend = _provision_backend(corpus_backend)
    if backend == "casestore":
        source = _casestore_source()
        found = source.latest_snapshot(case)
        documents = source.documents_for_case(case)
    else:
        with corpus.connect_readonly(db_path, backend=backend) as conn:
            found = corpus.latest_snapshot(conn, case)
            documents = corpus.documents_for_case(conn, case)
            _echo_read_stats(conn)
    if found is None:
        typer.echo(f"No snapshot in corpus for {case} (corpus-pull the corpus first?)", err=True)
        raise typer.Exit(code=1)
    if mode not in ("forward", "replay"):
        typer.echo(f"unknown --mode '{mode}'; choose forward or replay", err=True)
        raise typer.Exit(code=2)
    snapshot_date, payload = found
    # Leakage guard (opt-in): a forward *prediction* cell predicts a genuinely
    # pending event, so a snapshot that shows the outcome must never be
    # materialized — it would hand the predictor the answer. Two checks, both
    # over either payload shape (REST ``docket_entries`` or the raw live
    # ``ProceedingsandOrder`` the live channel stores verbatim):
    #   - the high-recall terminal scan (``snapshot_shows_disposition``,
    #     ``_TERMINAL_ENTRY_RE`` over *every* entry) — provisioning's semantic
    #     is "outcome visible anywhere in the snapshot", not docket pendency, so
    #     a disposition followed by administrative notations ("Application ...
    #     denied as moot") that hide it from the latest-entry rule, and the
    #     cert-before-judgment grant / merits judgment the resolver omits, are
    #     still caught;
    #   - the resolver (``match_disposition_signal``) over *every* entry, which
    #     adds the plain cert grant/denial orders that are not terminal-shaped.
    # The pull-side routing skip and the resolver latch are the primary
    # protections; this refusal is defense-in-depth for cells fanned out
    # before the docket latched. Refuses before writing anything (no snapshot,
    # no context.json); run-predict's provisioning step is continue-on-error,
    # so the cell runs snapshot-less and the agent notes the gap per the
    # prompt contract. Opt-in because the other callers *must* see decided
    # dockets: run-evaluate provisions the same forward-mode cell for an
    # already-resolved event, and the replay provisioner truncates
    # point-in-time itself.
    if refuse_terminal and mode == "forward":
        terminal = snapshot_shows_disposition(payload)
        if terminal is None:
            for text in entry_descriptions(payload):
                matched = match_disposition_signal(text)
                if matched is not None:
                    terminal = f"snapshot carries a disposition order: {matched[2]!r}"
                    break
        if terminal is not None:
            typer.echo(
                f"refusing to provision forward cell for {case}: {terminal}",
                err=True,
            )
            raise typer.Exit(code=3)
    paths = CasePaths(settings.data_root, court, docket)
    dest = out or paths.snapshot(snapshot_date.isoformat())
    write_raw_json(dest, payload)
    # The cell's mode context: stated at provisioning so the prompt
    # contract keys replay etiquette on it rather than inferring from env vars.
    write_raw_json(paths.cell_context, {"mode": mode})
    typer.echo(f"{case} snapshot {snapshot_date.isoformat()} ({mode}) -> {dest}")
    if documents:
        for doc in documents:
            write_text(paths.document(doc.kind), doc.text)
        write_raw_json(
            paths.documents_manifest,
            [
                {
                    **doc.model_dump(mode="json", exclude={"text"}),
                    # A present document whose extracted text is blank/whitespace
                    # (a scanned PDF with no text layer) would read as usable from
                    # pages/truncated alone; flag it so the cell distinguishes
                    # "no document" / "document present but no text layer" /
                    # "text present". Derived here, not stored on the row.
                    "empty_text": not doc.text.strip(),
                }
                for doc in documents
            ],
        )
        kinds = ", ".join(doc.kind for doc in documents)
        typer.echo(f"{case} documents ({kinds}) -> {paths.documents_dir}")


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

    The integration-test workflow's ranged-reads scenario: a point lookup (the case's open
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
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend, allow_service=True))
    if backend == "service":
        # The sidecar counterpart of the fixed set: two reads through the same
        # client a cell's `service` backend forwards with (the service exposes
        # query and open-events; snapshot provisioning is not a cell surface).
        report = integration_check.run_service_check(
            service_url=_service_url_or_exit(),
            court=court,
            docket=docket,
            limit=limit,
            budget_seconds=budget_seconds,
        )
        _finish_integration_report(report, summary_out)
        return
    if backend == "local" and not db_path.exists():
        typer.echo(
            f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.",
            err=True,
        )
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
    _finish_integration_report(report, summary_out)


@app.command("mcp-integration-check")
def mcp_integration_check(
    url: Annotated[
        str,
        typer.Option(help="The MCP endpoint to probe (the tokenless sidecar's localhost URL)."),
    ] = f"http://127.0.0.1:{mcp.MCP_SIDECAR_DEFAULT_PORT}/mcp",
    budget_seconds: Annotated[
        float, typer.Option(help="Wall-clock budget for the whole probe.")
    ] = 120.0,
    summary_out: Annotated[
        Path | None,
        typer.Option(
            help="Append the Markdown summary here (e.g. $GITHUB_STEP_SUMMARY); "
            "the machine JSON always goes to stdout.",
        ),
    ] = None,
) -> None:
    """Probe the CourtListener MCP sidecar; fail unless it hands out tools.

    The integration-test workflow's mcp-sidecar scenario: a minimal MCP client
    completes the streamable-HTTP handshake (``initialize`` +
    ``notifications/initialized``) and asserts ``tools/list`` advertises at
    least one tool — the exact surface every engine's generated cell config
    points at, exercised without spending a CourtListener call, so the sidecar
    may run token-free. Emits the machine report JSON on stdout and the
    Markdown summary on stderr; ``--summary-out`` also appends the Markdown.
    Exits 2 when the endpoint cannot be probed at all (a setup problem), 1
    when the protocol disappoints (no server name, no tools) or the budget
    blows.
    """
    try:
        report = integration_check.run_mcp_check(mcp_url=url, budget_seconds=budget_seconds)
    except integration_check.McpProbeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    _finish_integration_report(report, summary_out)


def _finish_integration_report(
    report: integration_check.IntegrationReport | integration_check.McpCheckReport,
    summary_out: Path | None,
) -> None:
    """Emit an integration report's JSON + Markdown and exit non-zero on failure."""
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
            "cassette) | claude-code | codex | gemini."
        ),
    ] = "stub",
    run_id: Annotated[
        str, typer.Option(help="Shared run id for the cells; defaults to now (UTC).")
    ] = "",
    predictor: Annotated[
        str,
        typer.Option(
            help="Run only this enabled predictor id (one cell); default: every enabled predictor."
        ),
    ] = "",
    corpus_backend: CorpusBackendOption = "",
    require_predictions: Annotated[
        bool,
        typer.Option(
            "--require-predictions",
            help="Exit non-zero when no predictor cell wrote a prediction. A real "
            "agent that finishes blocked (sandbox failure, missing inputs) exits 0 "
            "with an empty — and validly empty — ledger; the integration smoke "
            "needs that to fail, not pass.",
        ),
    ] = False,
) -> None:
    """Run the full predict → evaluate → validate cascade for one case locally.

    The repeatable, local form of the "one full cascade proven" milestone: over
    the fixture corpus (or a real provisioned one) it provisions the snapshot,
    materializes the git event/outcome definitions, fans the chosen engine out
    over the enabled predictors then evaluators, and validates the produced
    ledger — the iteration loop that otherwise only runs inside Actions. Corpus
    reads honor the corpus-backend setting, so a ``ranged``-configured
    environment runs the cascade against the remote blob with no local pull.

    ``--corpus-backend`` overrides that setting for the cascade's own
    provisioning reads only (``local`` or ``ranged`` — the service surface does
    not serve them); the spawned agent still inherits the ambient corpus
    settings, so an environment configured for the corpus query sidecar drives
    the agent's retrieval through the sidecar while provisioning reads the blob
    directly — the integration-test workflow's engine-smoke split.
    ``--predictor`` narrows the fan-out to one enabled predictor id, the
    one-cell shape a token-spending smoke run wants.

    ``--engine stub`` (the default) is deterministic, offline, and token-free.
    ``--engine replay`` is also offline but emits a captured real prediction from
    the cassette at ``FEDCOURTS_REPLAY_ROOT`` (see ``tests/cassettes``), so the
    scoring and leaderboard consumers run over realistic output rather than the stub
    floor. ``--engine claude-code`` / ``--engine codex`` / ``--engine gemini`` drive the
    real headless agents against the same env-var + prompt contract the workflows use;
    auth is inherited from the environment (``ANTHROPIC_API_KEY`` or the subscription
    ``CLAUDE_CODE_OAUTH_TOKEN`` from ``claude setup-token`` for Claude,
    ``OPENAI_API_KEY`` for Codex, ``GEMINI_API_KEY`` for Gemini). Writes derived
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
            predictor=predictor or None,
            backend=_corpus_backend(corpus_backend),
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
    if require_predictions and not report.predictions:
        typer.echo(
            "no predictor cell wrote a prediction (--require-predictions): the agent "
            "finished without output — a blocked cell, not a passing one",
            err=True,
        )
        raise typer.Exit(code=1)


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
    local-only open would silently create an empty corpus and find no events) and,
    under the corpus-split mode, it reads the per-case content store by default.
    Exits non-zero if the corpus holds no such event for the case.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = _provision_backend(corpus_backend)
    case = ids.case_id(court, docket)
    if backend == "casestore":
        match = next(
            (e for e in _casestore_source().events_for_case(case) if e.event_id == event), None
        )
    else:
        if backend == "local" and not db_path.exists():
            typer.echo(
                f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.",
                err=True,
            )
            raise typer.Exit(code=1)
        with corpus.connect_readonly(db_path, backend=backend) as conn:
            match = next(
                (e for e in corpus.events_for_case(conn, case) if e.event_id == event), None
            )
            _echo_read_stats(conn)
    if match is None:
        typer.echo(
            f"No event {event!r} in corpus for {case} (corpus-pull the corpus first?)", err=True
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
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend, allow_service=True))
    if backend == "service":
        try:
            response = corpus_service.client_open_events(_service_url_or_exit(), court, docket)
        except corpus_service.CorpusServiceError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
        for eid in response.event_ids:
            typer.echo(eid)
        return
    db = corpus.corpus_db_path(settings.corpus_root)
    for eid in open_events(db, court, docket, backend=backend):
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
    unrecorded_out: Annotated[
        Path,
        typer.Option(
            help="Write the unrecorded-outcome queue JSON here (decided but not "
            "deterministically recordable; surfaced on the run log)."
        ),
    ] = Path("unrecorded-queue.json"),
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
    an ``outcome.json`` this run), and ``unrecorded`` (cases that appear decided but
    whose outcome could not be recorded deterministically — surfaced on the run
    log for maintainer triage).

    The whole run is bounded by ``pull.max_run_minutes`` of wall clock: when the
    deadline (or the API budget, or the consecutive-transient-failure breaker)
    trips, the run stops where it is, defers the unreached cases to the next
    window's rotation, and still writes its queues — so a degraded upstream can
    never hang the job into its CI timeout and lose the window's work.
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
        # Rotation reads after discovery so freshly-onboarded cases are eligible.
        due = cases_due_for_pull(
            db,
            limit=cap,
            skip_closed=pull_cfg.skip_closed,
            eligible_reserve=pull_cfg.eligible_refresh_reserve,
        )
        queues = pull_cases(
            client,
            db,
            settings.data_root,
            due,
            scope=scope,
            deadline=deadline,
            max_consecutive_transient_failures=pull_cfg.max_consecutive_transient_failures,
        )
    _ensure_corpus_layout(db)
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    unrecorded_out.write_text(json.dumps(queues.unrecorded) + "\n")
    refreshed = len(due) - len(queues.failed) - len(queues.deferred)
    typer.echo(
        f"Refreshed {refreshed}/{cap} case(s){_format_refresh_failures(queues.failed)}; "
        f"queued {len(queues.predict)} predict, {len(queues.evaluate)} evaluate, "
        f"{len(queues.unrecorded)} unrecorded"
        + (
            f" ({len(queues.evaluate_skipped)} resolved case(s) had no prediction to score)"
            if queues.evaluate_skipped
            else ""
        )
        + (
            f" ({len(queues.predict_skipped_decided)} decided-looking case(s) skipped forward)"
            if queues.predict_skipped_decided
            else ""
        )
        + "."
    )
    for skipped in queues.predict_skipped_decided:
        typer.echo(
            "Skipped forward prediction for "
            f"{skipped['court']}/{skipped['docket']} — {skipped['reason']}"
        )
    if queues.stopped:
        deferred = len(queues.deferred)
        typer.echo(
            f"Stopped early ({queues.stopped}); deferred {deferred} case(s) to the rotation."
        )


@app.command("live-poll")
def live_poll(
    out: Annotated[Path, typer.Option(help="Write the predict queue JSON here.")] = Path(
        "predict-queue.json"
    ),
    evaluate_out: Annotated[
        Path, typer.Option(help="Write the evaluate queue JSON here (newly resolved events).")
    ] = Path("evaluate-queue.json"),
    unrecorded_out: Annotated[
        Path,
        typer.Option(
            help="Write the unrecorded-outcome queue JSON here (decided but not "
            "deterministically recordable; surfaced on the run log)."
        ),
    ] = Path("unrecorded-queue.json"),
    term: Annotated[
        int | None,
        typer.Option(
            help="Two-digit October Term to probe for new filings (default: the "
            "current Term, derived from today's date)."
        ),
    ] = None,
    limit: Annotated[
        int | None,
        typer.Option(
            help="Optional lower cap on pending petitions to re-poll this cycle; "
            "cannot exceed live.max_cases_per_run."
        ),
    ] = None,
    max_run_seconds: Annotated[
        float | None,
        typer.Option(
            help="Optional soft wall-clock budget for the cycle, seconds. When reached, "
            "the cycle stops cleanly with progress so far committed and resumes next "
            "cycle where the rotation left off — keeps a large watchlist from "
            "overrunning the job timeout (the workflow sets it under that timeout)."
        ),
    ] = None,
) -> None:
    """One SCOTUS live-channel cycle: discover new petitions, refresh pending ones.

    The live counterpart of ``pull-all``, fed by the supremecourt.gov
    docket JSON — no CourtListener token, no API budget; caps in the ``live``
    section of ``config/tracking.yaml`` bound wall clock and politeness.
    Discovery probes the Term's numbering frontier from the persisted per-Term
    cursor and onboards each served petition; the refresh re-polls the pending
    modern-cert watchlist (recent Terms first). Resolution is detected from the
    proceedings text, so a decided petition lands ``outcome.json``
    deterministically. Writes the same three handoff queues as ``pull-all``.
    """
    settings = get_settings()
    live_cfg = load_live_config(settings.config_root)
    scope = load_predict_config(settings.config_root).scope
    salience_cfg = load_salience_config(settings.config_root)
    cap = live_cfg.max_cases_per_run if limit is None else min(limit, live_cfg.max_cases_per_run)
    deadline = time.monotonic() + max_run_seconds if max_run_seconds is not None else None
    today = date.today()
    probe_term = term if term is not None else current_october_term(today)
    db = corpus.corpus_db_path(settings.corpus_root)
    with SupremeCourtClient(throttle_seconds=live_cfg.throttle_seconds) as client:
        queues, discovery = live_poll_all(
            client,
            db,
            settings.data_root,
            term=probe_term,
            config=live_cfg.model_copy(update={"max_cases_per_run": cap}),
            scope=scope,
            salience_config=salience_cfg,
            today=today,
            deadline=deadline,
        )
    _ensure_corpus_layout(db)
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    unrecorded_out.write_text(json.dumps(queues.unrecorded) + "\n")
    discovery_failed = f" ({len(discovery.failed)} stream error(s))" if discovery.failed else ""
    typer.echo(
        f"Live cycle (OT{probe_term:02d}): onboarded {len(discovery.onboarded)} new petition(s)"
        f"{discovery_failed}{_format_refresh_failures(queues.failed)}; "
        f"queued {len(queues.predict)} predict, {len(queues.evaluate)} evaluate, "
        f"{len(queues.unrecorded)} unrecorded"
        + (
            f" ({len(queues.evaluate_skipped)} resolved case(s) had no prediction to score)"
            if queues.evaluate_skipped
            else ""
        )
        + (
            f" ({len(queues.predict_skipped_decided)} decided-looking case(s) skipped forward)"
            if queues.predict_skipped_decided
            else ""
        )
        + "."
    )
    for skipped in queues.predict_skipped_decided:
        typer.echo(
            "Skipped forward prediction for "
            f"{skipped['court']}/{skipped['docket']} — {skipped['reason']}"
        )


@app.command("conference-set")
def conference_set(
    out: Annotated[
        Path | None,
        typer.Option(help="Also write the machine JSON (per-petition rows) here."),
    ] = None,
) -> None:
    """The pending-before-conference set: the live cert watchlist, by conference.

    Read-only: every pending modern-cert petition whose live proceedings
    carry a "DISTRIBUTED for Conference of …" membership, grouped by conference
    date — the set predictions fire ahead of and score against days later. The
    September long-conference set is this report's largest date bucket.
    """
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    if not db.exists():
        typer.echo(f"no corpus at {db}", err=True)
        raise typer.Exit(code=2)
    with corpus.connect_readonly(db) as conn:
        rows = corpus.conference_watchlist(conn)
    by_conference: dict[str, list[corpus.CorpusRow]] = {}
    for row in rows:
        assert row.distributed_for_conference is not None  # the query guarantees it
        by_conference.setdefault(row.distributed_for_conference.isoformat(), []).append(row)
    typer.echo(
        f"{len(rows)} pending petition(s) distributed across {len(by_conference)} conference(s)\n"
    )
    for conference, members in by_conference.items():
        typer.echo(f"Conference of {conference} — {len(members)} petition(s)")
        for row in members:
            typer.echo(f"  {row.docket_number:>9}  {row.case_name or row.case_id}")
        typer.echo("")
    if out is not None:
        write_raw_json(
            out,
            [
                {
                    "case_id": row.case_id,
                    "docket_number": row.docket_number,
                    "case_name": row.case_name,
                    "conference": row.distributed_for_conference.isoformat()
                    if row.distributed_for_conference
                    else None,
                }
                for row in rows
            ],
        )


@app.command("live-frontier")
def live_frontier_cmd(
    out: Annotated[
        Path | None,
        typer.Option(
            help="Write the LiveFrontier JSON here (default: <metrics_root>/live-frontier.json)."
        ),
    ] = None,
    today: Annotated[
        str,
        typer.Option(help="ISO as-of date for the next-conference pick; defaults to today (UTC)."),
    ] = "",
) -> None:
    """Snapshot the live cert watchlist's readiness for the ops dashboard.

    Read-only over the corpus: the pending-before-conference watchlist
    (``conference-set``'s population), its distribution calendar with the next
    conference relative to ``--today``, and how many watchlist petitions carry
    provisioned filed-document text. Produced where the corpus is already
    pulled and published to the ``ops-metrics`` branch (the corpus-writer
    path), so the corpus-free ``run-ops`` presenter can render live-frontier
    readiness. Graceful when the corpus is absent: writes a skipped snapshot
    and exits 0.
    """
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    destination = out if out is not None else settings.metrics_root / "live-frontier.json"
    as_of = date.fromisoformat(today) if today else datetime.now(UTC).date()
    if not db.exists():
        write_json(destination, LiveFrontier(skipped=True, generated_on=as_of))
        typer.echo(f"live-frontier: skipped (no corpus at {db}) -> {destination}")
        return
    with corpus.connect_readonly(db) as conn:
        rows = corpus.conference_watchlist(conn)
        provisioned = sum(1 for row in rows if corpus.documents_for_case(conn, row.case_id))
    by_conference: dict[date, int] = {}
    for row in rows:
        assert row.distributed_for_conference is not None  # the query guarantees it
        by_conference[row.distributed_for_conference] = (
            by_conference.get(row.distributed_for_conference, 0) + 1
        )
    upcoming = sorted(day for day in by_conference if day >= as_of)
    frontier = LiveFrontier(
        generated_on=as_of,
        watchlist=len(rows),
        next_conference=upcoming[0] if upcoming else None,
        next_conference_petitions=by_conference[upcoming[0]] if upcoming else None,
        conferences=[
            ConferenceBucket(conference=day, petitions=count)
            for day, count in sorted(by_conference.items())
        ],
        documents_provisioned=provisioned,
    )
    write_json(destination, frontier)
    typer.echo(
        f"live-frontier: {frontier.watchlist} petition(s) on the watchlist, "
        f"next conference {frontier.next_conference or 'none scheduled'}, "
        f"documents on {frontier.documents_provisioned} -> {destination}"
    )


@app.command()
def discover(
    since: Annotated[
        str,
        typer.Option(
            help="ISO date to start a never-discovered court from (default: today). "
            "Courts with a stored watermark resume from it regardless. Normally a "
            "court already carries a stored watermark, so pass --since only for a "
            "court that has none; the today "
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
        c if c.events else replace(c, events=tuple(default_events(c.court, c.docket)))
        for c in cases
    ]


def _scope_filtered(
    cases: list[CaseRequest],
    scope: PredictScope,
    corpus_root: Path,
    corpus_backend: corpus.CorpusBackend,
) -> list[CaseRequest]:
    """Drop out-of-scope cases under ``scotus_docket``; the matrix backstop.

    A manually-filed predict/evaluate issue cannot bypass the gate the pull
    queueing applies: the scope predicate is the corpus row's immutable
    ``court == "scotus"`` property, and an out-of-scope case is dropped with a
    visible note (to stderr, so the matrix JSON on stdout stays clean)
    explaining why a manual run produced an empty matrix. ``scope == all``
    passes every case through unchanged.

    A SCOTUS docket is still dropped when the shared exclusion reasoning
    matches it: the scope reconcile's ``predict_excluded`` latch, or any reason from
    ``corpus.out_of_scope_reason_full`` (the row rules — era, staleness, docket
    form, date consistency — plus the snapshot-aware bare opinion-import rule),
    with the reason echoed per case. These filters layer on top of the court
    predicate so ingestion coverage is unaffected.

    Gating reads the corpus through the configured backend — the pulled local
    file, or the committed pointer read in place over ``ranged``. The matrix is
    built from the *specific* cases the trigger issue names, so gating is a
    handful of point lookups (each case's row, and a latest-snapshot lookup only
    for a bare-import row), which the ranged backend serves in KBs — no full
    pull. Under ``local`` the database must be on disk: if it is absent the gate
    cannot distinguish "case not eligible" from "corpus never provisioned"
    (:func:`corpus.connect` would silently create an empty database and drop
    *every* case, an empty matrix that looks like a normal "nothing in scope"
    result), so fail loud. Under ``ranged`` the committed pointer + remote URL
    stand in for the file, and a missing pointer/URL fails loud in
    :func:`corpus.connect_readonly` itself.
    """
    if scope == PredictScope.all:
        return cases
    db_path = corpus.corpus_db_path(corpus_root)
    if corpus_backend == "local" and not db_path.exists():
        typer.echo(
            f"prediction scope is '{scope.value}' but the corpus database is missing at "
            f"{db_path}; provision it (fedcourts corpus-pull) before planning the matrix.",
            err=True,
        )
        raise typer.Exit(code=1)
    kept: list[CaseRequest] = []
    with corpus.connect_readonly(db_path, backend=corpus_backend) as conn:
        for case in cases:
            row = corpus.get_row(conn, ids.case_id(case.court, case.docket))
            if row is None or row.court != "scotus":
                typer.echo(
                    f"Skipping {case.court}/{case.docket}: out of prediction scope "
                    f"(predict.scope=scotus_docket, not a SCOTUS docket).",
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
            elif corpus.is_salience_deferred(row):
                typer.echo(
                    f"Skipping {case.court}/{case.docket}: not selected this salience round "
                    f"(scored, below the capacity slice).",
                    err=True,
                )
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
            _requested_cases(body_file, court, docket, event),
            scope,
            settings.corpus_root,
            settings.corpus_backend,
        ),
        lambda c, d: open_events(
            corpus.corpus_db_path(settings.corpus_root), c, d, backend=settings.corpus_backend
        ),
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
            _requested_cases(body_file, court, docket, event),
            scope,
            settings.corpus_root,
            settings.corpus_backend,
        ),
        lambda c, d: resolved_events(
            corpus.corpus_db_path(settings.corpus_root), c, d, backend=settings.corpus_backend
        ),
    )
    # The cost gate: events with no committed prediction are dropped here, at
    # plan time, so no evaluator cell (and no model spend) is minted for them —
    # a resolved-without-ever-predicted case has nothing to score.
    matrix = evaluate_matrix(
        settings.config_root / "evaluators.yaml", cases, run_id, data_root=settings.data_root
    )
    evaluator_count = len(
        [e for e in load_evaluators(settings.config_root / "evaluators.yaml") if e.enabled]
    )
    dropped = evaluator_count * sum(len(c.events) for c in cases) - len(matrix["include"])
    if dropped:
        typer.echo(f"evaluate-matrix: dropped {dropped} predictionless cell(s)", err=True)
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

    An auto-merged predict/evaluate PR may only *add* files under
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


@app.command("scan-diff-for-secrets")
def scan_diff_for_secrets_cmd(
    name_status_file: Annotated[
        Path, typer.Option(help="File holding `git diff --name-status` output to scan.")
    ],
    known_secret_env: Annotated[
        list[str] | None,
        typer.Option(
            help="Environment variable holding a live credential to search for "
            "literally (repeatable). Unset or too-short values fail the scan: "
            "a misconfigured gate must not pass silently."
        ),
    ] = None,
    extra_file: Annotated[
        list[Path] | None,
        typer.Option(
            help="Rendered text about to be posted (a PR body, a flag roll-up) to "
            "scan alongside the change set (repeatable). Must exist: the caller "
            "writes it immediately before scanning."
        ),
    ] = None,
    issue_comment_file: Annotated[
        Path | None,
        typer.Option(
            help="Where to append the redacted trigger-issue comment (appended only on findings)."
        ),
    ] = None,
    run_url: Annotated[
        str, typer.Option(help="Actions run URL, included in the issue comment.")
    ] = "",
) -> None:
    """Scan a change set's changed data/ files for secrets; exit non-zero on a hit.

    The third producer-side gate in the collect job, beside the path jail and
    the schema check: agent-written artifacts carry free text that schema
    validation deliberately does not read, so a credential copied into it
    would otherwise auto-merge to the public repo. Detectors and the
    redaction guarantee (findings name file/rule/line, never the matched
    text) live in ``secretscan``. On a hit the collect job withholds the
    branch — nothing pushed, no PR — because the push itself would publish
    the secret; a scan misconfiguration (a named env var that is unset or
    too short, a missing ``--extra-file``) fails the same way rather than
    silently dropping a detector or a surface.
    """
    misconfigured = False
    secrets: list[str] = []
    for env_name in known_secret_env or []:
        value = os.environ.get(env_name, "")
        if len(value) >= secretscan.MIN_KNOWN_SECRET_LENGTH:
            secrets.append(value)
        else:
            misconfigured = True
            typer.echo(
                f"::error::secret-scan: ${env_name} unset or too short; "
                "the containment detector cannot run",
                err=True,
            )
    changes = parse_name_status(name_status_file.read_text())
    findings = secretscan.scan_changes(changes, Path(), secrets)
    for extra in extra_file or []:
        if extra.is_file():
            findings.extend(secretscan.scan_file(extra, str(extra), secrets))
        else:
            misconfigured = True
            typer.echo(f"::error::secret-scan: extra file {extra} is missing", err=True)
    if findings:
        for line in secretscan.render_warnings(findings):
            typer.echo(line, err=True)
        if issue_comment_file is not None:
            with issue_comment_file.open("a") as handle:
                handle.write(secretscan.render_issue_comment(findings, run_url) + "\n")
        raise typer.Exit(code=1)
    if misconfigured:
        # Withholding must never be silent on the trigger issue: with no
        # findings to report, still say why nothing was published.
        if issue_comment_file is not None:
            with issue_comment_file.open("a") as handle:
                handle.write(secretscan.render_misconfigured_comment(run_url) + "\n")
        raise typer.Exit(code=2)
    typer.echo(f"secret scan OK ({len(changes)} change(s))")


@app.command("assert-cleanup-paths")
def assert_cleanup_paths_cmd(
    name_status_file: Annotated[
        Path, typer.Option(help="File holding `git diff --name-status` output to check.")
    ],
) -> None:
    """Enforce the cleanup jail; exit non-zero (with ::error::) on any violation.

    A cleanup-sweep PR may only *delete* files, and only under a
    ``data/cases/**/events/*/predictions/`` subtree. A maintainer runs this before
    committing a sweep, and CI runs it as a required status check on the PR, so a
    sweep that removed code, a workflow, an ``event.yaml`` / ``outcome.json``, or
    any non-prediction artifact cannot reach ``main`` without review.
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
    """Prune committed predictions for cases now out of predict scope.

    Reads the corpus (must be pulled) and the committed ``data/`` tree and
    finds every ``…/predictions`` directory whose case an exclusion predicate drops —
    pre-1925 mandatory jurisdiction or a stale unresolvable old SCOTUS petition;
    the event definition and any ``outcome.json`` stay, only the out-of-scope
    predictions go. Prints a JSON summary
    ``{"prunable":[{case_id,reason,paths}],"removed":<bool>,"pr":<branch/title/commit/body|null>}``;
    with ``--apply`` it also removes the directories. The ``pr`` block is the
    reviewed, manually merged PR a maintainer opens with the sweep. Gating
    on the real corpus row only — a case with predictions but no corpus row is left alone.
    """
    settings = get_settings()
    corpus_db = corpus.corpus_db_path(settings.corpus_root)
    if not corpus_db.exists():
        typer.echo(
            f"the corpus database is missing at {corpus_db}; provision it (fedcourts corpus-pull) "
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


@app.command("cert-backtest-plan")
def cert_backtest_plan(
    run_id: Annotated[
        str, typer.Option(help="The back-test run id for the PR prose; defaults to now (UTC).")
    ] = "",
    limit: Annotated[
        int, typer.Option(help="The --limit the run used (echoed in the prose).")
    ] = 25,
    engine: Annotated[
        str, typer.Option(help="The --engine the run used (echoed in the prose).")
    ] = "auto",
) -> None:
    """Render the review-PR plan for a cert back-test run (``run-backtest``).

    The workflow runs ``cert-backtest``, then hands the run's parameters here;
    this prints a JSON plan ``{"pr": <branch/title/commit/body|null>}`` with a
    headline read from the freshly-written report. ``pr`` is null when no
    report exists, so the workflow can exit quietly. The prose is rendered
    here, not with ``jq`` and a heredoc in the workflow, mirroring
    ``metrics-refresh-plan``.
    """
    settings = get_settings()
    pr = metrics_refresh.render_backtest_pr(
        settings.metrics_root, run_id or ids.run_id(), limit=limit, engine=engine
    )
    typer.echo(json.dumps({"pr": pr.model_dump() if pr is not None else None}))


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

    The workflow regenerates the metrics artifacts (the same tested commands the
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
        "dead_actors": list(plan.dead_actors),
        "noun": plan.noun,
        "missing_artifacts": list(plan.missing_artifacts),
        "uncovered_cells": [
            {"actor": c.actor, "court": c.court, "docket": c.docket, "event_id": c.event_id}
            for c in plan.uncovered_cells
        ],
    }


def _expected_cells(matrix_file: Path | None) -> list[ExpectedCell]:
    """Parse the plan job's matrix into the cells a run was supposed to produce.

    Degrades to an empty census on *any* malformed input, mirroring
    :func:`_load_flag_sets`. This is deliberately the most forgiving parse in the
    collect path: the census is **advisory** — it names gaps and withholds the
    issue close — while the aggregation it rides alongside carries the run's only
    copy of its agent output. A matrix that fails to parse (a truncated job
    output on a wide fan-out, a shape change) must never abort `collect-plan` and
    take the run's cells with it, which is the loss the per-artifact download was
    written to prevent. Worse, it would be deterministic: a rerun re-reads the
    same matrix and fails identically, stranding the run until a human steps in.

    Losing the census costs a warning and an issue that closes when it should
    have stayed open; losing the aggregation costs the run.
    """
    if matrix_file is None or not matrix_file.exists():
        return []
    try:
        entries = json.loads(matrix_file.read_text())["include"]
        return [ExpectedCell.from_matrix_entry(entry) for entry in entries]
    except (OSError, ValueError, TypeError, LookupError, AttributeError) as exc:
        typer.echo(
            f"::warning::could not read the plan matrix ({exc}); "
            "skipping the queued-cell census for this run",
            err=True,
        )
        return []


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
    growing with both history and matrix width):

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
    missing_file: Annotated[
        Path | None,
        typer.Option(
            help="File of artifact names (one per line) that failed to download. "
            "They are named in the PR body and withhold the issue close."
        ),
    ] = None,
    matrix_file: Annotated[
        Path | None,
        typer.Option(
            help="The plan job's matrix JSON. Cells it queued that uploaded nothing "
            "at all are named in the PR body and withhold the issue close."
        ),
    ] = None,
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
        # A lost artifact leaves no status.json, so it is invisible to the cell
        # census above; the collect job's downloader is the only thing that knows.
        missing_artifacts=(
            [n for n in missing_file.read_text().split() if n]
            if missing_file is not None and missing_file.exists()
            else []
        ),
        # What the run was *supposed* to produce. A cell that never uploaded
        # leaves no status.json, so without this it is indistinguishable from a
        # cell that was never queued.
        expected=_expected_cells(matrix_file),
    )
    typer.echo(json.dumps(_collect_plan_json(plan), separators=(",", ":")))


@app.command("stall-comment")
def stall_comment_cmd(
    role: Annotated[FinalizeRole, typer.Option(help="predict | evaluate.")],
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
