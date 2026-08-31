"""``fedcourts`` command line interface.

Thin wrapper over the library used by scripts, workflows, and humans. The most
important command is ``validate``, which CI runs to guarantee every artifact
committed under ``data/`` matches the schema contract.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
import tempfile
import textwrap
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Any, Literal, cast, get_args
from urllib.parse import quote

import typer
import yaml
from pydantic import BaseModel, ValidationError

# Typer vendors click, and re-exports neither the base command class a `cls=`
# override needs nor the parse-time error it raises. `typer.core` is the
# documented home of the first; the second has no public spelling at all —
# there is no installed `click` to import instead, and a real one would name a
# different class. A typer bump that moved it fails here at import, which takes
# every `fedcourts` command down at once: the gate cannot miss it, and no run
# can degrade quietly around it.
from typer._click.exceptions import UsageError
from typer.core import TyperCommand

from . import (
    analytics,
    blinding,
    casestore,
    cleanup,
    corpus,
    corpus_index,
    corpus_ranged,
    corpus_remote,
    corpus_seed,
    corpus_service,
    dedupe,
    ids,
    integration_check,
    mcp,
    metrics_refresh,
    process_version,
    provision,
    repo_gate,
    retrieval,
    scope_manifest,
    secretscan,
    tool_usage,
)
from .agent_feedback import post_agent_feedback, post_once
from .application_migration import (
    MOTION_BASELINE_EVENT_ID,
    relabel_application_baseline_events,
)
from .attribution_migration import (
    remove_ungranted_merits_events,
    remove_unmintable_baseline_events,
    reopen_misattributed_outcomes,
)
from .authz import authorize_trigger
from .backtest import default_backtesters, run_backtest, select_backtest_set
from .cert_backtest import (
    CERT_BACKTEST_SCOPES,
    build_segment_context,
    replay_predictors,
    replayable_items,
    run_cert_backtest,
    select_cert_backtest_set,
    truncate_snapshot,
)
from .claim_metrics import agreement_summary, build_claim_scores
from .collect import (
    CODE_MODE_PARENT_TOOL,
    CellStatus,
    CollectPlan,
    ExpectedCell,
    PathJailError,
    PriorAvailabilityRollup,
    PrPlan,
    ThrottleRollup,
    assert_cleanup_within_jail,
    assert_within_jail,
    attempted_corpus_query,
    cell_failures,
    code_mode_lift_blind,
    collect_plan,
    parse_name_status,
    render_stall_comment,
)
from .config import (
    CorpusBackend,
    PredictScope,
    Settings,
    get_settings,
    load_courts,
    load_evaluate_config,
    load_historical_config,
    load_live_config,
    load_predict_config,
    load_pull_config,
    load_salience_config,
    load_spend_config,
    load_statpack_config,
)
from .courtlistener import CourtListenerClient, default_rate_limiter
from .disposition_convergence import converge_disposition_labels
from .docket_marking_migration import normalize_docket_markings
from .finalize import FinalizeRole, agent_produced_output
from .fixture import build_fixture_corpus
from .gvr_migration import relabel_munsingwear_gvr_outcomes
from .integrity import (
    cell_clock,
    evaluation_clock,
    forward_claim_record,
    latest_evaluation_runs,
)
from .leaderboard import (
    big_case_agreement,
    build_leaderboard,
    evaluator_agreement,
    skill_components,
)
from .matrix import (
    CappedMatrix,
    CaseRequest,
    GuardedMatrix,
    StrandedCell,
    cap_predict_cells,
    drop_stranded_cells,
    evaluate_matrix,
    event_has_evaluations,
    event_has_predictions,
    parse_cases,
    predict_matrix,
    read_stranded_census,
)
from .merits_event_migration import (
    backfill_event_moments,
    backfill_merits_events,
)
from .ops import (
    build_ops_report,
    render_data_health,
    render_markdown,
    render_weekly_digest,
    summarize_substance,
    summarize_trigger_issues,
)
from .paths import CasePaths, EventPaths
from .pipeline import cell_context, historical, liveprobe, moments, qp_topics, semantic
from .pipeline.asof import CutoffPolicy
from .pipeline.base_rates import interim_base_rate, merits_base_rate
from .pipeline.bulk_scrub import scrub_bulk_cluster_fields
from .pipeline.caption import CAPTION_RULE_VERSION, CAPTION_RULES, caption_census
from .pipeline.cascade import CascadeError, run_cascade
from .pipeline.cert_signals import (
    DEFAULT_DISTRIBUTION_PARSE,
    DISTRIBUTION_PARSES,
    match_disposition_signal,
)
from .pipeline.claims import score_claims
from .pipeline.discover import discover_cases
from .pipeline.distribution_rederive import rederive_distribution_counts
from .pipeline.documents import (
    KIND_PETITION,
    TextCoverage,
    backfill_questions_presented,
    document_text_coverage,
    questions_presented_extract,
)
from .pipeline.evaluate import brier_score, brier_skill, is_correct
from .pipeline.judgment import backfill_merits_judgments, grant_term_year, last_judgment_entry
from .pipeline.live import live_poll_all
from .pipeline.opinion_enrichment import DEFAULT_MAX_CASES as DEFAULT_MAX_OPINION_CASES
from .pipeline.opinion_enrichment import enrich_opinions
from .pipeline.outcome import (
    entry_descriptions,
    interim_disposal_signal,
    snapshot_shows_disposition,
    snapshot_shows_judgment,
)
from .pipeline.pull import derive_evaluate_backlog, evaluate_backlog, pull_case, pull_cases
from .pipeline.response_backfill import backfill_response_fields
from .pipeline.runner import EngineFailed, EngineUnavailable, available_backends
from .pipeline.salience import (
    SALIENCE_VERSION,
    SCORERS,
    distribution_census,
    reconcile_salience_selection,
    registered_versions,
    unlatch_overselected,
)
from .pipeline.scope_reconcile import reconcile_predict_scope
from .pricing import DEFAULT_MODELS, MODEL_RATES, TokenCounts, estimate_cost_usd
from .registry import (
    enabled_evaluators,
    enabled_predictors,
    load_evaluators,
    load_mcp_servers,
    load_predictors,
    resolve_mcp_servers,
)
from .required_checks import produced_contexts
from .salience_replay import replay_gate
from .schemas import (
    EXPORTABLE_MODELS,
    AgentFlags,
    AgentToolingFeedback,
    CellFailure,
    ClaimScoreBlock,
    ConferenceBucket,
    CorpusValidation,
    DataHealth,
    Disposition,
    Engine,
    Evaluation,
    ForwardClaimRecord,
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStageEntry,
    LiveFrontier,
    ModelUsage,
    OpsReport,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
    QpTopicReference,
    RetrievalCall,
    RetrievalLog,
    SalienceReplay,
    Stage,
    StatPack,
    Stratum,
    UsageRole,
    observed_mcp_conditions,
)
from .serialize import read_model, write_json, write_raw_json, write_text, write_yaml
from .slug_migration import converge_event_slugs
from .spend import SpendVerdict, check_spend
from .store import (
    ExcludedCell,
    StratifiedRun,
    cases_due_for_pull,
    event_has_claimable_prediction,
    forecastable_events,
    forward_refusal_reason,
    forward_refusal_reason_from_parts,
    iter_evaluations,
    iter_flags,
    iter_tooling,
    iter_usage,
    ledger_cell_counts,
    open_events,
    resolved_events,
    scored_prediction,
    stratify,
    unforecastable_listed_events,
)
from .supremecourt import SupremeCourtClient, current_docket_term, parse_scotus_docket_number
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
    targets a real prediction, every recorded ``risk_set`` base-rate basis
    carries the salience version it was banded under, every prose document a
    prediction names sits beside it, and every committed claims block is one
    the claim scorer will not silently void. The corpus-dependent referential
    checks need the remote, so they run scheduled via ``validate-corpus``
    rather than here.
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
            help="ISO as-of date for the date-keyed checks — future-dated "
            "snapshots and dates, and the stale-grant cutoff; defaults to today (UTC)."
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
    # A check that passed while counting failures is a known condition, not a
    # defect — held within an accepted baseline, or advisory, where the count is
    # a backlog only a data pass can clear. Either way the number is worth
    # reading, and neither is worth holding the verdict red for. The cost is a
    # standing annotation per non-zero monitored count on every writer run —
    # the habituation risk the advisory doctrine warns about — accepted because
    # the counts are few and each is expected to drain to zero.
    for check in verdict.checks:
        if check.passed and check.failures:
            typer.echo(
                f"::warning::corpus-validation: {check.name} — {check.failures} row(s); "
                f"{check.detail}"
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


@app.command("scrub-bulk-cluster-fields")
def scrub_bulk_cluster_fields_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Scrub the matching rows; omit for a dry-run count."),
    ] = False,
    max_scrub: Annotated[
        int,
        typer.Option(
            "--max-scrub",
            help="Blast-radius bound: refuse to apply more scrubs than this.",
        ),
    ] = 1_500_000,
) -> None:
    """Scrub the bulk export's misjoined cluster fields from the stored slice.

    The ingest projection withholds the cluster-derived fields (`summary`,
    `opinion_text`, `precedential_status`, `judges`, `panel`, `citations`,
    `citation_count`)
    from a bulk-sourced non-SCOTUS row — the bulk docket-to-cluster join is
    misjoined on the circuit slices — but that rule reaches a stored row only
    on a re-serve, and nothing re-serves the historical bulk slice. This
    converges it: one UPDATE over every non-SCOTUS row a bulk-only field
    marks. The mark is provable, not inferred, and the proof is scope: cluster
    data reaches the corpus through the bulk join and the SCOTUS-only opinion
    enrichment (`enrich-opinions`) and nothing else, so a populated `summary`,
    `precedential_status`, `citations`, or `citation_count` on a **non-SCOTUS**
    row can only be the bulk join's, whatever
    the row's pull history — while `judges`/`panel`, which discovery and
    pull re-derive from the docket record itself, clear only on marked rows
    and survive everywhere else. `opinion_text` is withheld at ingest but left
    out of the sweep: every write to it flows through `upsert_rows`, whose
    re-mirror is what `casestore.read_opinion_text` rests its freshness
    invariant on, and this sweep is a direct UPDATE. Idempotent. `--apply`
    refuses above
    `--max-scrub`, whose default sits just over the measured bulk slice: a
    count past it means the predicate widened (a lost filter reaching rows
    the carve-out never covered), not that the slice grew. Run where the
    corpus is pulled (run-seed's writer lane in production). Fails loud if
    the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the scrub.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        if apply:
            preview = scrub_bulk_cluster_fields(conn, apply=False)
            if preview.scrubbed > max_scrub:
                typer.echo(
                    f"scrub-bulk-cluster-fields: refusing to apply {preview.scrubbed} "
                    f"scrubs (--max-scrub {max_scrub}). The bound sits just over the "
                    "measured bulk slice; a count past it means the predicate "
                    "widened — triage before raising it.",
                    err=True,
                )
                raise typer.Exit(code=1)
        result = scrub_bulk_cluster_fields(conn, apply=apply)
    verb = "scrubbed" if apply else "would scrub"
    typer.echo(
        f"scrub-bulk-cluster-fields ({'applied' if apply else 'dry-run'}): "
        f"{verb} {result.scrubbed} bulk-marked non-SCOTUS row(s)"
    )


@app.command("rederive-distribution-counts")
def rederive_distribution_counts_cmd(
    parse: Annotated[
        str,
        typer.Option(
            "--parse",
            help="The registered distribution parse to re-derive the column under "
            "(`pipeline.cert_signals.DISTRIBUTION_PARSES`). Required — a re-derivation "
            "names its reading rather than inheriting a default.",
        ),
    ],
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Write the re-derived counts; omit for a dry-run plan."),
    ] = False,
    max_changes: Annotated[
        int,
        typer.Option(
            "--max-changes",
            help="Blast-radius bound: refuse to apply more count rewrites than this.",
        ),
        # The basis, so raising it is a decision rather than a reflex. Measured
        # for dist-v2 over the live slice: 378 rows of the ~22.7k walked whose
        # stored count differs from a dist-v2 reading, of which 181 fall in the
        # census's narrower scored-segment frame — the census's own figure. That
        # the incumbent parse moves 0 rows on the same blob is what licenses
        # reading those 378 as the parse's doing rather than stored drift. The
        # bound sits ~5x the measured delta and about an order of magnitude
        # under the walked population, which makes it a guard against a
        # catastrophic write rather than a wrong one: the sharper signal is
        # `increased`, since under a narrowing parse a rise means the stored
        # column sat below its own reading — a corpus-integrity finding, not a
        # parse effect.
    ] = 2_000,
    version: Annotated[
        str,
        typer.Option(
            "--version",
            help="Which registered salience version's band function keys the band-move matrix.",
        ),
    ] = SALIENCE_VERSION,
) -> None:
    """Re-derive the corpus `distribution_count` column under a registered parse.

    The first of the three pieces of work that activate a new distribution parse
    (`docs/salience.md`): until the stored column is re-derived, every downstream
    consumer — the gate's banding, the statpack's per-band base rates, the
    relist-tier cutpoints — is still reading the incumbent parse's counts.

    Over every **live-slice SCOTUS row** — where the column is populated, the
    bulk import having parsed no proceedings text — recount the conferences the
    case's latest **live-shaped** snapshot discloses (split-aware: the read
    serves from the per-case content store under the corpus-split mode) and
    write the result with a **direct UPDATE that deliberately bypasses the
    upsert path's max latch**. The latch exists so a degraded payload's
    confident 0 cannot wipe a stored count; a narrower parse moves every changed
    row down, which is precisely the write it rejects, so routing this through
    `upsert_rows` would write nothing while reporting success. What replaces the
    latch is narrower than the latch: a row with no live-shaped snapshot, or one
    disclosing no proceedings **entries**, is counted `unobservable` and left
    untouched — never written to 0 — but nothing here detects a merely
    *truncated* entry list. **So run the incumbent parse first**: that pass must
    report `changed = 0`, or what a candidate moves is stored-column drift
    rather than the reading. A row carrying no stored count at all is reported
    and left alone too (the null is the live-signal family's coverage sentinel;
    `backfill-live-signals` owns it), which is also where interim application
    dockets sit.

    One pass **per invocation**, so a dry run and the apply inside one call
    cannot describe different work; across two dispatches the plan is a reading,
    not a guarantee, which is why the apply prints its own report. `--apply`
    refuses above `--max-changes` (default sized off a measured delta — see the
    code comment), printing the report first so the refusal is triageable, and
    writes the whole batch in one transaction. Idempotent.
    Band moves are reported over the **census frame** (paid, modern-cert,
    parseable Term), since a band label is only meaningful where the gate
    scores, while the write covers the whole live slice; every count carries its
    own denominator, unreadable residue included, and all of them are raw row
    counts rather than denial-reweighted estimates. The matrix's `from` side is
    the **stored** column, not a second reading of the snapshot, so it carries
    whatever the max latch accumulated — which is what the gate is really
    reading today, and why it need not agree cell for cell with
    `distribution-census`.

    **Corpus-side only**: `data/` is never touched. A frozen `record/context.json`
    records the count the cell was handed and a committed prediction is a
    judgment made on that input; rewriting either would retcon an information
    set. Note the durability limit: the live channel re-polls pending petitions
    and open merits proceedings and upserts a count read under the ingest
    default, which the max latch takes where it is higher — so a re-polled row
    reverts unless `cert_signals.DEFAULT_DISTRIBUTION_PARSE` moves to the same
    parse in the same batch. Run where the corpus is pulled (run-repair's
    `rederive-distribution-parse` pass in production; a dev checkout serves the
    dry run). Prints a
    `DistributionRederiveResult`. Fails loud if the corpus is absent or the
    parse or version label is unregistered.
    """
    if parse not in DISTRIBUTION_PARSES:
        typer.echo(
            f"unregistered distribution parse {parse!r}; "
            f"registered: {', '.join(sorted(DISTRIBUTION_PARSES))}",
            err=True,
        )
        raise typer.Exit(code=2)
    if version not in SCORERS:
        typer.echo(
            f"unregistered salience version {version!r}; registered: {', '.join(sorted(SCORERS))}",
            err=True,
        )
        raise typer.Exit(code=2)
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before re-deriving the distribution counts.",
            err=True,
        )
        raise typer.Exit(code=1)
    # The blob this pass read, resolved exactly as the census resolves it: the
    # ledger of a latch-bypassing write has to name the corpus state it is
    # re-derivable against, and a count quoted beside a census figure is
    # comparable only where both name one blob.
    if settings.corpus_backend == "local":
        corpus_sha, _ = corpus_remote.digest_file(db_path)
    elif settings.corpus_pointer is None:
        pointer_file = corpus_remote.pointer_path_for(db_path)
        corpus_sha = (
            corpus_ranged.read_index_pointer(pointer_file).sha256 if pointer_file.is_file() else ""
        )
    else:
        corpus_sha = corpus.resolve_read_pointer(db_path).sha256
        typer.echo(
            "corpus provenance: out-of-band pointer override in effect — the "
            "recorded corpus_sha256 names the override's blob",
            err=True,
        )
    with corpus.connect(db_path) as conn:
        result = rederive_distribution_counts(
            conn,
            parse=parse,
            apply=apply,
            corpus_sha256=corpus_sha,
            max_changes=max_changes,
            version=version,
        )
    verb = "rewrote" if apply else "would rewrite"
    if result.refused:
        verb = "refused to rewrite"
    # `observable` is the denominator, not the frame: a pass that could read a
    # tenth of the live slice and one that read all of it otherwise announce
    # themselves identically, and an unobservable row is untouched rather than
    # agreed with. Under the corpus split a store miss and "no live snapshot
    # was ever stored" land in the same bucket, so the fraction is a coverage
    # figure as much as a docket one.
    frame = result.observable + result.unobservable
    coverage = f"{100 * result.observable / frame:.1f}% of {frame}" if frame else "no rows"
    typer.echo(
        f"rederive-distribution-counts {result.parse} "
        f"({'applied' if apply else 'dry-run'}): {verb} {result.changed} of "
        f"{result.observable} observable row(s) ({coverage}); "
        f"{result.decreased} down, {result.increased} up; "
        f"{result.unobservable} unobservable and {result.no_stored_count} "
        "never-counted, both untouched"
    )
    # The frame's parts sum: banded, unreadable, and readable-but-never-counted.
    census_frame = (
        result.scored_segment
        + result.scored_segment_unobservable
        + result.scored_segment_no_stored_count
    )
    typer.echo(
        f"band moves ({result.salience_version}, over {result.scored_segment} of the "
        f"{census_frame}-row census frame): {result.band_changed} banded row(s) move, "
        f"{result.scored_segment_changed} counts change"
    )
    if not apply and result.changed > max_changes:
        # The dry run never consults the bound, so without this the refusal
        # would surface only on the second dispatch — after the reading that
        # was supposed to decide whether to make it.
        typer.echo(
            f"note: {result.changed} changes is above --max-changes {max_changes}; "
            "an apply would refuse. Triage, or dispatch with a bound you can justify.",
            err=True,
        )
    for move in result.band_moves:
        # The diagonal is the unmoved mass; printing only the off-diagonal
        # occupied cells keeps the banner readable, and the full zero-filled
        # square is in the JSON below either way.
        if move.from_band != move.to_band and move.n:
            typer.echo(f"  {move.from_band} -> {move.to_band}: {move.n}")
    typer.echo(result.model_dump_json())
    if result.refused:
        # After the report, never instead of it: the message tells a maintainer
        # to triage, and the denominators, the band matrix and the changed ids
        # are what triage reads.
        typer.echo(
            f"rederive-distribution-counts: refusing to apply {result.changed} count "
            f"rewrite(s) (--max-changes {max_changes}). Nothing was written. The bound "
            "is sized off a measured delta; a count past it means the predicate widened "
            "or the parse is not a narrowing of the incumbent — triage the report above "
            "before raising it.",
            err=True,
        )
        raise typer.Exit(code=1)


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
        result = reconcile_salience_selection(conn, settings.data_root, config, apply=apply)
    typer.echo(
        f"reconcile-salience-selection ({'applied' if apply else 'dry-run'}): "
        f"scored {result.scored}, newly selected {result.newly_selected} "
        f"across {result.conferences} conference(s)"
    )
    typer.echo(result.model_dump_json())


@app.command("caption-census")
def caption_census_cmd(
    rule_version: str = typer.Option(
        CAPTION_RULE_VERSION,
        "--rule-version",
        help="Which registered caption rule cuts the frame (caption-v1, caption-v2).",
    ),
) -> None:
    """The petitioner-class census: per-Term grant-family rates by caption class.

    A deterministic, read-only cut of the salience gate's scored segment
    (live-slice, paid, modern-cert, resolved) under one registered caption rule
    (`pipeline.caption`) — the artifact any caption-keyed selection constant
    must be frozen from, after a statistical review of the run
    (`docs/salience.md`), and the run names the rule version it was cut under.
    Prints a `CaptionCensus`. Fails loud if the corpus is absent or the rule
    version is unregistered.
    """
    if rule_version not in CAPTION_RULES:
        typer.echo(
            f"unregistered caption rule {rule_version!r}; "
            f"registered: {', '.join(sorted(CAPTION_RULES))}",
            err=True,
        )
        raise typer.Exit(code=2)
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the caption census.",
            err=True,
        )
        raise typer.Exit(code=1)
    # The provenance the freeze record needs: under `local` the hash of the
    # file the census actually ran over (which can drift from the committed
    # pointer); under `ranged` the immutable blob IS the pointer's object, so
    # the digest of the pointer the read paths resolve — the out-of-band
    # override when set, else the committed file — names it exactly.
    if settings.corpus_backend == "local":
        corpus_sha, _ = corpus_remote.digest_file(db_path)
    else:
        if settings.corpus_pointer is None:
            # Only a MISSING committed pointer is excused (an empty digest); a
            # malformed one must raise rather than blank a freeze-record input.
            pointer_file = corpus_remote.pointer_path_for(db_path)
            corpus_sha = (
                corpus_ranged.read_index_pointer(pointer_file).sha256
                if pointer_file.is_file()
                else ""
            )
        else:
            corpus_sha = corpus.resolve_read_pointer(db_path).sha256
        # The census is a freeze-record input: a provenance digest that came
        # from the override must never read like a committed-pointer one.
        if settings.corpus_pointer is not None:
            typer.echo(
                "corpus provenance: out-of-band pointer override in effect — the "
                "recorded corpus_sha256 names the override's blob",
                err=True,
            )
    with corpus.connect_readonly(db_path, backend=settings.corpus_backend) as conn:
        census = caption_census(conn, corpus_sha256=corpus_sha, rule_version=rule_version)
    typer.echo(f"caption census ({census.rule_version}), pooled:", err=True)
    for cell in census.pooled:
        rate = f"{cell.rate:.4f}" if cell.rate is not None else "-"
        typer.echo(
            f"{cell.petitioner_class}: n={cell.n} grant-family={cell.grant_family} rate={rate}",
            err=True,
        )
    typer.echo(census.model_dump_json())


@app.command("distribution-census")
def distribution_census_cmd(
    baseline_parse: str = typer.Option(
        DEFAULT_DISTRIBUTION_PARSE,
        "--baseline-parse",
        help="The registered distribution parse counted as the incumbent.",
    ),
    # `--candidate-parse` is required, as it is on `distribution_census` itself.
    # The incumbent has a default because the registry names it
    # (`DEFAULT_DISTRIBUTION_PARSE`, the reading the corpus column holds); the
    # challenger is whatever a caller is arguing for, which the registry cannot
    # know. Defaulting it to a label would also, on the commit that activates
    # that label, quietly turn a bare invocation into a parse-against-itself
    # census reporting no movement on every row.
    candidate_parse: str = typer.Option(
        ...,
        "--candidate-parse",
        help=(
            "Required — the registered distribution parse counted against the "
            "incumbent. No default: the challenger is the caller's argument, not "
            "the registry's."
        ),
    ),
    version: str = typer.Option(
        SALIENCE_VERSION,
        "--version",
        help="Which registered salience version's band function bands both counts.",
    ),
) -> None:
    """The distribution-parse census: what re-reading DISTRIBUTED would move.

    A deterministic, read-only count of two registered distribution parses
    (`pipeline.cert_signals`) over the salience gate's scored segment —
    live-slice, paid, modern-cert petitions, **pending rows included**, since
    the count is a banding input the gate reads before a petition resolves and
    the ancillary-paper distributions the readings differ on accumulate on live
    pending dockets. Both counts come off each case's latest **live-shaped**
    snapshot — the entry-initial rule is a claim about the live channel's entry
    conventions, so counting a REST payload under it would report a channel
    artifact as a parse delta — and are banded by one salience version's band
    function, so the reported delta (changed counts split by direction, the
    band-transition matrix, a per-Term rollup split by docket maturity, a
    per-band rollup keyed on the incumbent label, and every changed case id) is
    attributable to the phrase-reading alone.

    Every cut carries its denominator. The banner prints `cases` as a fraction
    of the `cases + unobservable` frame; pending rides both denominators
    (`frame_pending` over the whole frame, the per-Term `pending` over the
    observable rows); and the matrix is the full band-by-band square,
    zero-filled, so an observed zero is never an omitted cell — which half of it
    a parse pair can occupy is a property of the pair (a subset candidate can
    only lower the count and every band function is monotone in it, so no case
    moves to a stronger band), with `count_increased` as the observed check.

    The **input-level** cut only, and conditional: the corpus column, the
    statpack's band base rates, and the relist-tier cutpoints were all fitted
    under the default parse, so pinning a new parse means re-deriving the column
    on a writer job, rebuilding the statpack, and re-measuring the tier rates.
    The selection question is read from `salience-replay` with the candidate
    version registered, never from this matrix (`docs/salience.md`). Prints a
    `DistributionCensus`. Fails loud if the corpus is absent, a parse or version
    label is unregistered, or the frame is subsampled.
    """
    for label in (baseline_parse, candidate_parse):
        if label not in DISTRIBUTION_PARSES:
            typer.echo(
                f"unregistered distribution parse {label!r}; "
                f"registered: {', '.join(sorted(DISTRIBUTION_PARSES))}",
                err=True,
            )
            raise typer.Exit(code=2)
    if version not in SCORERS:
        typer.echo(
            f"unregistered salience version {version!r}; registered: {', '.join(sorted(SCORERS))}",
            err=True,
        )
        raise typer.Exit(code=2)
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the distribution census.",
            err=True,
        )
        raise typer.Exit(code=1)
    # The provenance the freeze record needs, read exactly as the caption census
    # reads it: under `local` the hash of the file the census actually ran over,
    # under `ranged` the parsed digest of the pointer the read paths resolve.
    if settings.corpus_backend == "local":
        corpus_sha, _ = corpus_remote.digest_file(db_path)
    else:
        if settings.corpus_pointer is None:
            # Only a MISSING committed pointer is excused (an empty digest); a
            # malformed one must raise rather than blank a freeze-record input.
            pointer_file = corpus_remote.pointer_path_for(db_path)
            corpus_sha = (
                corpus_ranged.read_index_pointer(pointer_file).sha256
                if pointer_file.is_file()
                else ""
            )
        else:
            corpus_sha = corpus.resolve_read_pointer(db_path).sha256
        # The census is a freeze-record input: a provenance digest that came
        # from the override must never read like a committed-pointer one.
        if settings.corpus_pointer is not None:
            typer.echo(
                "corpus provenance: out-of-band pointer override in effect — the "
                "recorded corpus_sha256 names the override's blob",
                err=True,
            )
    with corpus.connect_readonly(db_path, backend=settings.corpus_backend) as conn:
        census = distribution_census(
            conn,
            corpus_sha256=corpus_sha,
            baseline_parse=baseline_parse,
            candidate_parse=candidate_parse,
            version=version,
        )
    # `cases` is the observable rows, not the frame, so it is printed against
    # its own denominator: a census that could read a tenth of its frame and one
    # that read all of it otherwise announce themselves identically.
    frame = census.cases + census.unobservable
    coverage = f"{100 * census.cases / frame:.1f}% of the {frame}-row frame" if frame else "no rows"
    typer.echo(
        f"distribution census {census.baseline_parse} -> {census.candidate_parse} "
        f"({census.salience_version}): cases={census.cases} ({coverage}) "
        f"unobservable={census.unobservable} count-changed={census.count_changed} "
        f"band-changed={census.band_changed}",
        err=True,
    )
    # Both pending denominators, in the line that names the frame: the divergence
    # between them is the reason the census carries two.
    typer.echo(
        "frame: live-slice paid modern-cert SCOTUS, pending included, "
        f"latest live snapshot; pending={census.frame_pending} of the frame "
        f"and {census.pending} of the {census.cases} observable; "
        f"corpus sha256={census.corpus_sha256 or '(unknown)'}",
        err=True,
    )
    # The occupied off-diagonal cells, as a count and never as a share of the
    # square: how many cells a parse pair can reach at all is a property of the
    # pair (a subset candidate only lowers counts, so it only moves a case down
    # the band order), so a density over every off-diagonal cell would read as
    # sparsity where the unreached cells are an identity. The artifact carries
    # every cell zero-filled, so an unprinted cell is an observed zero.
    moves = [cell for cell in census.transitions if cell.from_band != cell.to_band and cell.n]
    for cell in moves:
        typer.echo(f"{cell.from_band} -> {cell.to_band}: {cell.n}", err=True)
    typer.echo(
        f"occupied off-diagonal transition cells: {len(moves)} (the square carries all "
        f"{len(census.transitions)} zero-filled; which are reachable depends on the parse "
        f"pair); count moved up in {census.count_increased} case(s), "
        f"down in {census.count_decreased}",
        err=True,
    )
    typer.echo(census.model_dump_json())


@app.command("unlatch-overselected")
def unlatch_overselected_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Clear the over-selection latches; omit for a dry-run count."),
    ] = False,
) -> None:
    """Clear `salience_selected` where a from-scratch selection would not pick.

    The one-time reconcile for the overhang a capacity resize leaves behind: the
    sticky latch is additive, so petitions latched under the old caps stay
    latched and keep earning cells the shipped envelope never budgeted. This
    recomputes each pending conference cohort's selection from scratch under the
    current config (same scorer, same carve-outs, reserve=0 so the clear is
    never widened) and clears the latch on pending petitions the recomputation
    would not pick — decided rows, interim applications, and never-distributed
    petitions are untouched, and a committed prediction on a cleared case stays
    committed — and still graded: the evaluate matrix never applies the
    salience skip. Deliberate maintainer surface, never scheduled: run
    `dedupe-live-rows --apply` first (a merge takes the latch stickily from
    either twin), dry-run by default, run where the corpus is pulled,
    `corpus-push` after an `--apply`. Prints a `SalienceUnlatchResult` — keep
    it: the full cleared-id ledger in it, beside the pre-apply pointer echoed
    below, is the record of the pre-resize sticky set the write erases. Fails
    loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the latch reconcile.",
            err=True,
        )
        raise typer.Exit(code=1)
    config = load_salience_config(settings.config_root)
    ref = db_path.parent / (db_path.name + ".ref")
    if ref.is_file():
        typer.echo(f"pre-apply corpus pointer: {ref.read_text().strip()}", err=True)
    with corpus.connect(db_path) as conn:
        result = unlatch_overselected(conn, config, apply=apply)
    verb = "cleared" if apply else "would clear"
    typer.echo(
        f"unlatch-overselected ({'applied' if apply else 'dry-run'}): "
        f"{verb} {result.unlatched} of {result.latched_pending} latched pending petition(s) "
        f"across {result.pending_cohorts} cohort(s); {result.retained} retained"
    )
    typer.echo(result.model_dump_json())


@app.command("dedupe-live-rows")
def dedupe_live_rows_cmd(
    apply: Annotated[
        bool,
        typer.Option(
            "--apply", help="Drop the duplicate rows; omit for a dry-run that only reports."
        ),
    ] = False,
) -> None:
    """Merge and drop the live-minted twin of each duplicated SCOTUS docket.

    Where one SCOTUS docket number carries two rows — the upstream
    CourtListener docket id and a live-minted reserved-range id, the pair shape
    an annotated docket-number spelling leaves when it defeats the channels'
    identity join — this merges the pair onto the CourtListener-keyed survivor
    and drops the live row: every fact only the live twin carries fills in on
    the survivor, its events / snapshots / documents move under the surviving
    id, the survivor's `sample_weight` takes the pair's minimum, and the
    live-minted row is deleted from all four tables — no orphans. A **minted**
    forecast moment's committed `event.yaml` directory moves with its re-keyed
    row, its case id restamped inside, so the merge never leaves the shape
    `minted_moments_defined_in_ledger` fails on — a row under the survivor whose
    definition still sits on the dropped case's path. The ledger half goes
    first, so an interrupted pair converges on the next run. A pair disagreeing
    on `date_filed`, `date_decided`, or `disposition` is skipped and reported,
    never dropped — the dry-run output is the triage list — and so is one this
    merge cannot carry mechanically: committed cell output anywhere under the
    dropped id (a prediction names that id inside its own file, which no restamp
    here rewrites, so the row delete would orphan it), committed directories for
    one moment under **both** ids, or a survivor-side document that will not
    read. A half-merged twin is worse than an unmerged one. Content-store
    objects under a dropped id are left in place (no-delete store; nothing
    resolves a dropped id, so they are inert). Idempotent. Run where the corpus
    is pulled, `corpus-push` after an `--apply`. Because an `--apply` now writes
    `data/` as well as the corpus, the lane that runs it **must stage the moved
    paths in the same pointer commit**, as the merits-events backfill step does;
    an `--apply` whose ledger writes are not committed drops the corpus half
    alone and leaves the directory stranded, which no later pass re-detects (the
    dropped row is gone). Prints a `LiveDedupeResult`. Fails loud if the corpus
    is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the dedupe.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = dedupe.dedupe_live_rows(conn, settings.data_root, apply=apply)
    verb = "dropped" if apply else "would drop"
    typer.echo(
        f"dedupe-live-rows ({'applied' if apply else 'dry-run'}): "
        f"{result.pairs} duplicate pair(s); {verb} {len(result.dropped)} live-minted row(s), "
        f"skipped {len(result.skipped)} pair(s) for triage"
    )
    for entry in result.skipped:
        typer.echo(
            f"  - kept {entry.pair.keep}, not dropped {entry.pair.drop}: "
            f"{'; '.join(entry.conflicts)}"
        )
    for move in result.ledger_moves:
        if move.restamp_only:
            verbed = "restamped" if apply else "would restamp"
            where = f"{move.to_case}/{move.event_id} (already at the survivor)"
        else:
            verbed = "moved" if apply else "would move"
            where = f"{move.from_case}/{move.event_id} -> {move.to_case}/{move.event_id}"
        typer.echo(f"  {verbed} ledger event directory {where}")
    if result.dropped:
        typer.echo(
            "  content-store objects under the dropped ids are left in place "
            "(no-delete store; nothing resolves a dropped id, so they are inert)"
        )
    typer.echo(result.model_dump_json())


@app.command("backfill-merits-judgments")
def backfill_merits_judgments_cmd(
    apply: Annotated[
        bool,
        typer.Option(
            "--apply", help="Write the parsed judgments; omit for a dry-run that only counts."
        ),
    ] = False,
) -> None:
    """Parse each granted SCOTUS case's stored snapshot for its merits judgment.

    Over the rows whose cert grant opens a merits proceeding
    (`corpus.opens_merits_proceeding` — a GVR or summary reversal decides in the
    cert order and is excluded), read the latest stored snapshot
    (SQLite, or the per-case content store under the corpus-split mode — the
    same offline path the salience replay reads), parse the last
    judgment-shaped terminal entry (`pipeline/judgment.py`), and stamp
    `merits_judgment` / `merits_decided` — the offline reconciler behind the
    columns the live poll also latches at ingest, feeding the statpack's merits
    stage section, the merits base rate pooled from it, and merits outcome
    detection. Where no judgment shape matches anywhere, a second, smaller
    vocabulary runs as fallback — the terminations, for a proceeding that ended
    without a disposition (a post-grant Rule 46 dismissal, a dismissal as moot,
    an abatement on the petitioner's death, a grant the Court vacated, a bare
    mandate notation) — and stamps `merits_terminated` instead, which closes
    the row's pendency without entering the parsed slice. Idempotent; a row
    whose snapshot is unreachable is counted `no_snapshot` and left as it is.
    Dry-run by default; `--apply` writes (run where the corpus is pulled,
    `corpus-push` after). Prints a `MeritsBackfillResult`. Fails loud if the
    corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the merits backfill.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = backfill_merits_judgments(conn, apply=apply)
    verb = "stamped" if apply else "would stamp"
    distribution = (
        ", ".join(f"{value}: {count}" for value, count in result.judgments.items()) or "none"
    )
    typer.echo(
        f"backfill-merits-judgments ({'applied' if apply else 'dry-run'}): "
        f"{result.eligible} granted case(s) — {result.parsed} parsed "
        f"({result.unchanged} already stored, {verb} {result.updated}), "
        f"{result.no_snapshot} without a reachable snapshot, "
        f"{result.terminated} terminated without a disposition "
        f"({verb} {result.terminations_written}), "
        f"{result.no_match} with no judgment-shaped entry"
    )
    if result.stale:
        typer.echo(
            f"  STALE: {result.stale} row(s) carry a stored judgment this pass could not "
            "re-derive (never cleared automatically — triage them)"
        )
    typer.echo(f"  judgments: {distribution}")
    terminations = (
        ", ".join(f"{value}: {count}" for value, count in result.terminations.items()) or "none"
    )
    typer.echo(f"  terminations: {terminations}")
    typer.echo(result.model_dump_json())


@app.command("backfill-questions-presented")
def backfill_questions_presented_cmd(
    apply: Annotated[
        bool,
        typer.Option(
            "--apply",
            help="Rewrite the questions-presented rows; omit for a dry-run that only counts.",
        ),
    ] = False,
) -> None:
    """Re-derive each SCOTUS case's questions presented from its stored petition text.

    The `questions-presented` row is **derived** from the petition, and the
    ingest path derives it only when the petition itself is (re)fetched — an
    unchanged petition URL is never re-fetched, so a row keeps whatever the
    extractor said the day it was ingested and an extractor fix never reaches
    it. This pass closes that gap: over the live-slice SCOTUS cases holding
    petition text (SQLite, or the per-case content store under the corpus-split
    mode — documents reach the corpus on that channel only), run the current
    extractor (`pipeline/documents.py`) and rewrite the row only where its
    output differs from what is stored. Nothing is fetched and no PDF is
    re-read — the input is text the corpus already holds. A stored full-length
    question the extractor can no longer derive is reported (`refused`) rather
    than emptied — that reading is as likely to be this pass misjudging a
    question as a bad row, and the sweep does not decide it alone — unless the
    stored value is contents junk throughout (leader dots clear the character
    floor by counting the dots), which empties under its own reason class,
    `toc-junk-emptied`, so a dry run shows the emptied subset apart. Each
    rewrite is
    classified by the extraction hole it comes from (`stale-toc-fragment`,
    `prose-terminator-fragment`, `below-floor`, `other-change`,
    `toc-junk-emptied`, plus
    `derived-anew` where a case had no row), so the dry run is the triage list;
    the printed `QPBackfillResult` carries the untruncated case-id ledger of
    which rows an applied pass replaced, beside the pre-apply `corpus.db.ref`
    the command echoes. Idempotent. A
    deliberate maintainer surface, never scheduled: corpus writes exist only
    inside the writer workflows, so this fires on an explicit `run-repair`
    dispatch naming its `qp-backfill` pass — two dispatches by design, a
    `dry-run` whose summary ledger the maintainer reads and then an `apply`,
    which verifies its own convergence by re-running the dry-run (under the
    corpus split the durable write is the content store's per-case mirror, so
    the pointer alone cannot witness it) before the `corpus-push`. Fails loud if
    the corpus is absent, or if it holds no petition text at all (a payload-free
    index, or a split-mode blob with no content store configured — the wrong
    blob for this command).
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the questions-presented backfill.",
            err=True,
        )
        raise typer.Exit(code=1)
    if apply:
        # The pointer the rewrite is about to supersede. Where the replaced text
        # is recoverable from depends on the mode: from this blob in the
        # self-contained mode, which holds the documents inline; from the prior
        # content-addressed leaf and the bucket-versioned manifest under the
        # split mode, where the blob carries no document text at all. Echo it
        # either way — it is what names the corpus state the ledger below
        # describes.
        ref = db_path.parent / (db_path.name + ".ref")
        if ref.is_file():
            typer.echo(f"pre-apply corpus pointer: {ref.read_text().strip()}", err=True)
    with corpus.connect(db_path) as conn:
        result = backfill_questions_presented(conn, apply=apply)
    if not result.petitions:
        typer.echo(
            f"backfill-questions-presented: no stored petition text in {db_path} "
            "— wrong blob for this command?",
            err=True,
        )
        raise typer.Exit(code=1)
    verb = "rewrote" if apply else "would rewrite"
    distribution = (
        ", ".join(f"{reason}: {count}" for reason, count in result.reasons.items()) or "none"
    )
    # Summary first: the per-case ledger below runs to the size of the change
    # set, and a first pass over an unconverged corpus would bury the counts.
    typer.echo(
        f"backfill-questions-presented ({'applied' if apply else 'dry-run'}): "
        f"{result.petitions} stored petition(s) — {result.unchanged} unchanged, "
        f"{verb} {result.updated}, {result.no_petition_text} without petition text"
    )
    typer.echo(f"  reasons: {distribution}")
    if result.refused:
        typer.echo(
            f"  REFUSED: {result.refused} carry a full-length question this pass "
            "cannot re-derive — never emptied automatically; triage them"
        )
    for case_id, reason in result.changes.items():
        typer.echo(f"  {case_id}: {reason}")
    if apply:
        _ensure_corpus_layout(db_path)
    typer.echo(result.model_dump_json())


@app.command("enrich-opinions")
def enrich_opinions_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Write the enriched rows; omit for a dry-run report."),
    ] = False,
    max_cases: Annotated[
        int,
        typer.Option(help="Cases to walk this run — the per-run REST spend bound."),
    ] = DEFAULT_MAX_OPINION_CASES,
) -> None:
    """Fill each granted SCOTUS case's reporter cites and opinion body from REST.

    Over the cert-granted slice — SCOTUS rows carrying `date_cert_granted` and
    not yet an opinion — resolve the docket's published opinion cluster (from a
    stored REST-shaped snapshot's `clusters` links where it has one, else a
    docket fetch), take the cluster's reporter `citations` and
    `citation_count`, and take the cluster's first sub-opinion's `plain_text`
    as the body. Each case is written through the corpus's own upsert as it
    converges (casestore mirror included), so `has_opinion` derives and `query
    --full` can hydrate the body.

    Because `has_opinion` latches, a wrong body is permanent — so the pass
    refuses rather than guesses: a docket linking several clusters is skipped,
    a fetched cluster must name the docket it was reached from, and an opinion
    whose upstream `type` marks it a separate writing (a concurrence, a
    dissent) never becomes the body. Each refusal is counted and the citations
    still land — a coverage gap, never fatal, as are a docket linking no
    cluster and a per-case non-429 REST or parse failure.

    Three REST requests a case (two where a REST-shaped snapshot already links
    the cluster), so `--max-cases` bounds the run's spend on top of the
    client's rate governor; the walk stops cleanly when the API budget is
    exhausted — or when a 429 survives the client's retries, a quota wall
    either way — deferring the unfinished cases for a re-run in a genuine
    dead zone. Run it outside a pull
    window: the governor is per-process, so two runs would each stay under the
    ceiling while the account did not.

    Idempotent: an enriched row no longer matches, while one that found no
    cluster is retried, so a grant picks up its opinion the run after
    publication. A grant that never publishes one (a GVR, a DIG) never
    converges, so raise `--max-cases` past that residue when converging the
    backlog. Dry-run by default (the
    requests are spent either way — the dry run is how the spend is
    inspected); run where the corpus is pulled, `corpus-push` after an
    `--apply`. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the opinion enrichment.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn, _client() as client:
        result = enrich_opinions(conn, client, apply=apply, max_cases=max_cases)
    if apply:
        _ensure_corpus_layout(db_path)
    verb = "enriched" if apply else "would enrich"
    typer.echo(
        f"enrich-opinions ({'applied' if apply else 'dry-run'}): "
        f"{result.eligible} granted case(s) without an opinion — walked "
        f"{result.considered}, {verb} {result.enriched}, "
        f"{result.no_cluster} with no linked cluster, {result.no_body} with no body; "
        f"{result.requests} REST request(s)"
    )
    if result.ambiguous_cluster or result.foreign_cluster:
        typer.echo(
            f"  refused: {result.ambiguous_cluster} docket(s) linking several clusters, "
            f"{result.foreign_cluster} cluster(s) naming another docket"
        )
    if result.live_only:
        typer.echo(
            f"  {result.live_only} granted row(s) carry a live-channel docket id, which "
            "addresses nothing upstream — not walked"
        )
    if result.stopped:
        typer.echo(f"  stopped: {result.stopped} ({len(result.deferred)} case(s) deferred)")
    for entry in result.failed:
        typer.echo(f"  failed {entry['case_id']}: {entry['reason']}")
    typer.echo(result.model_dump_json())


@app.command("backfill-merits-events")
def backfill_merits_events_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Mint the missing events; omit for a dry-run report."),
    ] = False,
) -> None:
    """Mint the open merits forecast events onto already-granted, undecided dockets.

    The live mint opens a case's merits events at cert-grant *detection*, so a
    docket whose grant is already latched in the corpus without a live
    resolution pass carries none. This deterministic corpus-convergence sweep
    mints, for each row whose grant opens a merits proceeding
    (`corpus.opens_merits_proceeding`) and whose judgment is not latched
    (forward-only: a decided grant leaves nothing to forecast), the
    grant-moment event `evt-order-judgment` opened at `date_cert_granted` —
    and, where the respondent's merits brief is latched, the briefed moment
    `evt-brief-judgment` beside it — through the live mint's own write path,
    corpus row first, ledger `event.yaml` second. A case already carrying an
    open grant event is topped up with just the owed briefed moment; a
    resolved grant event means the case is converged. A mint also requires the
    docket shown still **pending** — a stored snapshot whose high-recall
    judgment scan is clean, because a null `merits_judgment` means unlatched,
    not pending — so run `backfill-merits-judgments --apply` immediately
    before this sweep in the same corpus session. A case whose target id
    already exists entry-pinned, with committed ledger artifacts under the
    id and no corpus event row, with no stored snapshot, or whose snapshot
    shows an unparsed judgment signal, is skipped and reported for triage.
    Idempotent: a converged corpus mints nothing. Dry-run by default;
    `--apply` writes. Run
    where the corpus is pulled, `corpus-push` after an `--apply`. Fails loud if
    the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the backfill.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = backfill_merits_events(conn, settings.data_root, apply=apply)
    verb = "minted" if apply else "would mint"
    cases = sorted({case_id for case_id, _ in result.minted})
    typer.echo(
        f"backfill-merits-events ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.minted)} merits event(s) on {len(cases)} case(s); "
        f"{result.already_present} case(s) already converged; "
        f"{result.decided} decided grant(s) outside the forecast population; "
        f"skipped {len(result.skipped)} for triage"
    )
    preview = cases[:10]
    if preview:
        suffix = ", …" if len(cases) > len(preview) else ""
        typer.echo(f"  {', '.join(preview)}{suffix}")
    for case_id, reason in result.skipped:
        typer.echo(f"  skipped {case_id}: {reason}")


@app.command("backfill-event-moments")
def backfill_event_moments_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Stamp the null moments; omit for a dry-run count."),
    ] = False,
) -> None:
    """Stamp stage-carrying event rows' null `moment` as the stage's first moment.

    A null `moment` already reads downstream as the stage's first moment, so
    the stamp changes no behavior — it materializes that reading into the
    corpus column so moment-keyed grouping reads it directly. Stage-keyed off
    the declared moments table (`pipeline.moments.first_moment`), written
    through the corpus's own writer (casestore events mirror included).
    Idempotent: a stamped row no longer matches. Dry-run by default; `--apply`
    writes. Run where the corpus is pulled, `corpus-push` after an `--apply`.
    Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the backfill.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = backfill_event_moments(conn, apply=apply)
    verb = "stamped" if apply else "would stamp"
    detail = ", ".join(f"{stage}: {count}" for stage, count in sorted(result.stamped.items()))
    typer.echo(
        f"backfill-event-moments ({'applied' if apply else 'dry-run'}): "
        f"{verb} {sum(result.stamped.values())} event row(s)" + (f" — {detail}" if detail else "")
    )


@app.command("migrate-gvr-labels")
def migrate_gvr_labels_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Rewrite the matching outcomes; omit for a dry-run count."),
    ] = False,
) -> None:
    """Relabel identifiable historical GVR outcomes to the `gvr` disposition.

    A deterministic convergence sweep for the introduction of the `gvr` label
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


@app.command("converge-event-slugs")
def converge_event_slugs_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Rename the diverged events; omit for a dry-run report."),
    ] = False,
    max_renames: Annotated[
        int,
        typer.Option(
            "--max-renames",
            help="Blast-radius bound: refuse to apply more renames than this.",
        ),
    ] = 20,
) -> None:
    """Rename entry-pinned events whose ids the current slug derivation no longer mints.

    An entry-pinned event's id is derived from its docket entry's text, and
    `corpus.upsert_events` keys on `(case_id, event_id)` — so a row minted under
    a superseded derivation is not updated by a re-ingest of its docket: the
    refresh inserts a *second* row under today's id, open, beside the stale one
    that holds the `resolved` latch and the committed ledger directory. Nothing
    closes the new row (a SCOTUS disposing order cites no entry number), so the
    case carries a permanent open event. This convergence sweep re-derives each
    entry-pinned row's id from its own stored entry text and renames the
    divergent ones in both stores — the corpus row through
    `corpus.rename_event` (atomic, `resolved` latch carried, casestore mirror
    included) and the ledger directory by moving it and restamping the id inside
    `event.yaml` / `outcome.json`. The ledger half goes first: the corpus row is
    the detection handle, so an interrupted run is re-found and finished by the
    next one. Where the derived id is already on the case *pinned to the same
    docket entry*, that row is the duplicate this sweep exists to clear, and the
    rename folds onto it — `rename_event` takes `resolved` as the MAX of the
    two, so the case ends with one row holding the latch. A **different**
    entry's row under the derived id is the genuine collision and is reported
    for triage, as are a ledger directory holding committed cell output,
    directories under both ids, and a row whose text or kind cannot be read.
    Idempotent. Dry-run by default; `--apply` writes, and refuses above
    `--max-renames`: the population is the finite set of rows a derivation
    change left behind, so a large count means the derivation moved further
    than intended. Corpus writes exist only inside the writer workflows and no
    lane runs this sweep, so today only the **dry run** is runnable — from a dev
    checkout over a pulled corpus, as the triage report a maintainer reads.
    Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the convergence.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        if apply:
            preview = converge_event_slugs(conn, settings.data_root, apply=False)
            if len(preview.renamed) > max_renames:
                typer.echo(
                    f"converge-event-slugs: refusing to apply {len(preview.renamed)} renames "
                    f"(--max-renames {max_renames}). The population is the finite set of rows "
                    "a derivation change left behind; a count this size means the derivation "
                    "moved further than intended — triage before raising the bound.",
                    err=True,
                )
                raise typer.Exit(code=1)
        result = converge_event_slugs(conn, settings.data_root, apply=apply)
    verb = "renamed" if apply else "would rename"
    typer.echo(
        f"converge-event-slugs ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.renamed)} event(s); "
        f"{result.already_converged} entry-pinned row(s) already converged; "
        f"skipped {len(result.skipped)} for triage"
    )
    for ref, new_event_id in result.renamed:
        typer.echo(f"  {verb} {ref} -> {new_event_id}")
    for ref, reason in result.skipped:
        typer.echo(f"  skipped {ref}: {reason}")


@app.command("relabel-application-events")
def relabel_application_events_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Rename the matching events; omit for a dry-run report."),
    ] = False,
) -> None:
    """Relabel application dockets' baseline events to the motion/interim form.

    A SCOTUS `YYAnnn` application docket's baseline event is
    `evt-motion-disposition` (`kind = motion`, `stage = interim`) — a stay or
    injunction application is a motion under the interim standard, not a cert
    petition. This deterministic convergence sweep renames any cert-shaped
    baseline (`evt-petition-disposition`) still sitting on an application docket
    to that form, carrying every field and the `resolved` latch, atomically per
    case. A case with committed ledger artifacts under the old identity, or
    whose existing `evt-motion-disposition` row is entry-pinned, is skipped and
    reported for triage rather than folded. Idempotent: a converged corpus
    renames nothing. Dry-run by default; `--apply` writes. Run where the corpus
    is pulled, `corpus-push` after an `--apply`. Fails loud if the corpus is
    absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the relabel.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = relabel_application_baseline_events(conn, settings.data_root, apply=apply)
    verb = "renamed" if apply else "would rename"
    typer.echo(
        f"relabel-application-events ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.renamed)} baseline event(s) to "
        f"{MOTION_BASELINE_EVENT_ID}; "
        f"{result.already_relabeled} application docket(s) already carried it; "
        f"skipped {len(result.skipped)} for triage"
    )
    preview = result.renamed[:10]
    if preview:
        suffix = ", …" if len(result.renamed) > len(preview) else ""
        typer.echo(f"  {', '.join(preview)}{suffix}")
    for case_id, reason in result.skipped:
        typer.echo(f"  skipped {case_id}: {reason}")


@app.command("reopen-misattributed-outcomes")
def reopen_misattributed_outcomes_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Reopen the matching events; omit for a dry-run report."),
    ] = False,
    max_reopens: Annotated[
        int,
        typer.Option(
            "--max-reopens",
            help="Blast-radius bound: refuse to apply more reopens than this.",
        ),
    ] = 20,
) -> None:
    """Reopen committed outcomes copied from a sibling case-baseline event.

    A deterministic repair over the committed ledger for the records an earlier
    single-open-event attribution shortcut left behind: a non-case-baseline
    event whose outcome duplicates a case-baseline sibling's
    `(actual_disposition, resolved_at, actual_granted)` exactly — a stay motion
    holding a copy of the petition's cert disposition. Each is deleted and its
    event reopened in both stores (the ledger `event.yaml` and the corpus event
    row), because the ledger does not carry the source order text, so no true
    disposition is recoverable here and an open event is the honest state. Only
    non-baseline events are repaired: reopening a case-baseline event makes it
    the stage-less fallback's target, so the next resolution pass would rewrite
    the deleted outcome — a duplication between two case-baseline events is
    reported for triage instead. An event carrying committed predict/evaluate
    output is likewise skipped. Idempotent, and convergent against the
    resolution pass. Dry-run by default; `--apply` writes, and refuses above
    `--max-reopens`: the population this sweep repairs is finite and
    non-growing, so a large count means the predicate widened, not that the
    ledger did — triage before raising the bound. Run where the corpus
    is pulled (run-seed's writer lane in production, after
    `remove-unmintable-events`). Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the repair.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        if apply:
            preview = reopen_misattributed_outcomes(conn, settings.data_root, apply=False)
            if len(preview.reopened) > max_reopens:
                typer.echo(
                    f"reopen-misattributed-outcomes: refusing to apply "
                    f"{len(preview.reopened)} reopens (--max-reopens {max_reopens}). "
                    "The population this sweep repairs is finite and non-growing; "
                    "a count this size means the predicate widened — triage before "
                    "raising the bound.",
                    err=True,
                )
                raise typer.Exit(code=1)
        result = reopen_misattributed_outcomes(conn, settings.data_root, apply=apply)
    verb = "reopened" if apply else "would reopen"
    typer.echo(
        f"reopen-misattributed-outcomes ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.reopened)} event(s); "
        f"skipped {len(result.skipped)} for triage"
    )
    for ref in result.reopened:
        typer.echo(f"  {verb} {ref}")
    for ref, reason in result.skipped:
        typer.echo(f"  skipped {ref}: {reason}")


@app.command("converge-disposition-labels")
def converge_disposition_labels_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Rewrite the confirmed outcomes; omit for a dry-run report."),
    ] = False,
    max_relabels: Annotated[
        int | None,
        typer.Option(
            "--max-relabels",
            help="Blast-radius bound, required with --apply: refuse to apply more than this.",
        ),
    ] = None,
    include_scored: Annotated[
        bool,
        typer.Option(
            "--include-scored",
            help="Also relabel candidates carrying committed predict/evaluate output.",
        ),
    ] = False,
) -> None:
    """Re-resolve committed `granted` cert outcomes against their stored docket text.

    A deterministic **ledger** convergence sweep for the labels no re-resolution
    reaches: `record_outcomes` is idempotent-by-filter, so a resolved event is
    never revisited. Over each committed cert-stage outcome labeled `granted`,
    the sweep reads the case's latest stored snapshot, parses the earliest
    disposing entry at or after the recorded resolution date, and relabels only
    where that parse confirms one of **two arms**.

    `gvr` — the same order read more finely: an order granting, vacating and
    remanding in one breath, which `match_disposition_signal` reads through its
    vacatur-sentence upgrade, sits recorded as a plain `granted`. The petition
    was granted either way, so only the label sharpens.

    `disowned-grant` — no order on the petition at all: the recorded grant was
    read off an ancillary order *about* the petition (an extension of time to
    respond, a delayed distribution, an unsealing) whose wording put the cert
    noun beside a granting verb, while the case's real terminal — a denial or a
    petition-stage Rule 46 dismissal — was recorded nowhere. This arm moves the
    grant binary 1 → 0 and re-dates the resolution to the confirming entry.

    The era boundary is the separation the forward-convention rule needs: before
    it, a cert label was normalized from upstream record fields and never passed
    through the disposition parser, so its `granted` is the older vocabulary's
    faithful record — the protected residual — not a parse gap. It governs the
    `gvr` arm outright. The `disowned-grant` arm reaches back through it on
    positive evidence instead of on the calendar: it fires only where an entry
    **dated the recorded resolution** exists and **nothing anywhere on the
    docket** still parses as a grant — an order sat there, a grant was read out
    of it once, and today's parser reads no grant at all, which is a parse gap
    with a date on it. A resolution date the snapshot carries no entry for, or a
    docket that still carries a grant order somewhere (the real grant whose Rule
    46 exit or mootness dismissal comes later), is reported and never rewritten.

    Candidates carrying committed predict/evaluate output are **held back by
    default**, because an `evaluation.json` is stamped with a `correct` bit
    computed from the outcome; `--include-scored` opts in and reports, per
    relabel, how many stamped evaluations it puts in the re-grade backlog that
    `stamp-cell --regrade` is the follow-through for. On a `disowned-grant` that
    backlog is not the whole debt. `resolved_at` only ever moves **later** (the
    confirming entry is at or after the recorded resolution), so a withdrawal
    can only push an already-scored cell from the retrospective stratum toward
    `forward` — the leaderboard's rank key — and can only clear a recorded
    forward-claim breach, never the reverse. Both are correct where the
    withdrawal is, but the direction is one-sided and flattering, so read the
    dry run for it; neither lands through `--regrade` — they arrive on the next
    board build.

    Self-confirming, so the report is the point: every relabel is printed with
    the arm that authorized it, every population member not relabeled with its
    reason, and the header carries the honest denominators — how many
    candidates were actually checkable, how many
    had no readable text, how many the sweep declines to judge, and how the
    relabels split between the two arms, since the `disowned-grant` count is the
    one that moves grant rates — in the ledger. **The corpus is a separate
    store and does not follow**: base rates and every published disposition
    figure are built from it, so until it is corrected too a withdrawn row reads
    0 here while still counting as a grant in the denominators those cells are
    scored against. The live channel closes part of the gap
    (`ingest._live_resolution` re-reads the proceedings through the same guard,
    and the columns take the incoming value on upsert rather than latching; the
    CourtListener pull reads the upstream record's own fields and never consults
    the guard) — but only for rows `corpus.live_rotation` still polls, which a
    fabricated grant that opened no merits event is not. Those owe a curated
    corpus write, and corpus writes belong to the writer jobs' upsert path.

    Idempotent (neither a `gvr` nor a `denied`/`dismissed` outcome reads
    `granted`). Dry-run by default.
    `--apply` writes and **requires** `--max-relabels`, so the number applied is
    one the maintainer read in the dry run rather than a default nobody chose;
    it refuses above that bound, since the population this sweep converges is
    finite and non-growing, so a large count means the predicate widened, not
    that the ledger did. Run where the corpus is pulled; the snapshot read is
    split-aware, so it serves from the per-case content store under the
    corpus-split mode. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    if apply and max_relabels is None:
        typer.echo(
            "converge-disposition-labels: --apply requires an explicit --max-relabels. "
            "Read the dry run first and pass the count you are approving.",
            err=True,
        )
        raise typer.Exit(code=2)
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the convergence sweep.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = converge_disposition_labels(
            conn,
            settings.data_root,
            apply=apply,
            max_relabels=max_relabels,
            include_scored=include_scored,
        )
    if result.refused:
        typer.echo(
            f"converge-disposition-labels: refusing to apply "
            f"{len(result.relabeled)} relabels (--max-relabels {max_relabels}). "
            "The population this sweep converges is finite and non-growing; "
            "a count this size means the predicate widened — triage before "
            "raising the bound.",
            err=True,
        )
        raise typer.Exit(code=1)
    verb = "relabeled" if apply else "would relabel"
    # Split by arm in the header: the two carry different risk — `gvr` sharpens a
    # label the binary keeps, `disowned-grant` withdraws the grant outright — so
    # the count a maintainer approves with `--max-relabels` has to say which.
    withdrawals = sum(1 for entry in result.relabeled if entry.arm == "disowned-grant")
    typer.echo(
        f"converge-disposition-labels ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.relabeled)} of {result.checkable} checkable candidate(s) "
        f"({len(result.relabeled) - withdrawals} gvr, {withdrawals} disowned-grant); "
        f"{result.uncheckable} uncheckable (no readable docket text); "
        f"{result.out_of_scope} out of scope"
    )
    for entry in result.relabeled:
        backlog = (
            f"; {entry.stamped_evaluations} stamped evaluation(s) to re-grade"
            if entry.stamped_evaluations
            else ""
        )
        # The `disowned-grant` arm moves the grant binary and re-dates the
        # resolution, so its line says both out loud rather than leaving a
        # reviewer to infer them from the label: those are the two fields a
        # relabel here can put out of step with anything already scored or
        # plotted against the old date.
        withdrawal = (
            f"; grant bit 1 -> 0, resolution re-dated to {entry.entry_filed.isoformat()}"
            if entry.arm == "disowned-grant"
            else ""
        )
        # A withdrawal rests on two pieces of text, not one, and the *refused*
        # sentence is the half a reviewer cannot reconstruct: it is why the
        # stored grant is a parse gap rather than a record to leave alone.
        # Printed first, since the arm is only warranted if it convinces.
        recital = f" — read from {entry.recital!r}" if entry.recital else ""
        typer.echo(
            f"  {verb} {entry.ref} [{entry.arm}]: {entry.was.value} -> {entry.now.value} "
            f"({entry.basis}) [entry {entry.entry_filed.isoformat()}, resolved "
            f"{entry.resolved_at.isoformat()}, snapshot {entry.snapshot_date.isoformat()}]"
            f"{withdrawal}{backlog}{recital} — {entry.evidence!r}"
        )
    for ref, reason in result.skipped:
        typer.echo(f"  skipped {ref}: {reason}")


@app.command("remove-unmintable-events")
def remove_unmintable_events_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Remove the matching events; omit for a dry-run report."),
    ] = False,
    max_removals: Annotated[
        int,
        typer.Option(
            "--max-removals",
            help="Blast-radius bound: refuse to apply more removals than this.",
        ),
    ] = 20,
) -> None:
    """Drop entry-pinned SCOTUS events carrying a case-baseline id, in both stores.

    A SCOTUS docket carries its petition and appeal request kinds only as the
    case-level baseline — `extract_events` mints no entry-pinned event for
    either — so an entry-pinned row whose id carries a case-baseline prefix is
    one no re-ingest reproduces. It is also the shape that makes the case-level
    disposition ambiguous, since `_cert_disposition_target`'s stage-less
    fallback keys on a *lone* open baseline. Removal rather than a reopen: the
    event names nothing the docket supports, and leaving it open would park a
    permanent phantom on the case and keep it forecastable. An event carrying
    committed predict/evaluate output is skipped and reported instead.
    Idempotent. Dry-run by default; `--apply` writes, and refuses above
    `--max-removals`: the population this sweep removes is finite and
    non-growing (the mint refuses the shape), so a large count means the
    predicate widened — triage before raising the bound. Run where the corpus
    is pulled (run-seed's writer lane in production); the ledger directory goes
    first, then the corpus row, so an interrupted run leaves the row as the
    detection handle for the next pass. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the removal.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        if apply:
            preview = remove_unmintable_baseline_events(conn, settings.data_root, apply=False)
            if len(preview.removed) > max_removals:
                typer.echo(
                    f"remove-unmintable-events: refusing to apply "
                    f"{len(preview.removed)} removals (--max-removals {max_removals}). "
                    "The population this sweep removes is finite and non-growing; "
                    "a count this size means the predicate widened — triage before "
                    "raising the bound.",
                    err=True,
                )
                raise typer.Exit(code=1)
        result = remove_unmintable_baseline_events(conn, settings.data_root, apply=apply)
    verb = "removed" if apply else "would remove"
    typer.echo(
        f"remove-unmintable-events ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.removed)} event(s); skipped {len(result.skipped)} for triage"
    )
    for ref in result.removed:
        typer.echo(f"  {verb} {ref}")
    for ref, reason in result.skipped:
        typer.echo(f"  skipped {ref}: {reason}")


@app.command("remove-ungranted-merits-events")
def remove_ungranted_merits_events_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Remove the matching events; omit for a dry-run report."),
    ] = False,
    max_removals: Annotated[
        int,
        typer.Option(
            "--max-removals",
            help="Blast-radius bound: refuse to apply more removals than this.",
        ),
    ] = 20,
    include_failed_attempts: Annotated[
        bool,
        typer.Option(
            "--include-failed-attempts",
            help=(
                "Also remove a phantom whose only committed output is attempt.json "
                "cell-failure records, deleting them with it. An attempt record under "
                "a phantom documents spend on an event that names nothing the docket "
                "supports; removing it trades that failure history for a ledger with "
                "no dangling phantom paths, which is why it is an explicit choice "
                "rather than the default. The condition is stricter than 'no "
                "prediction and no evaluation': EVERY file under predictions/ must "
                "be named attempt.json, and there must be no evaluations/ directory "
                "at all, so any other artifact the harness left beside an attempt "
                "record (usage.json, retrieval_log.json) keeps the event skipped."
            ),
        ),
    ] = False,
) -> None:
    """Drop open SCOTUS merits events whose docket carries no cert grant, in both stores.

    A merits event is born from a grant: every mint path routes through
    `opens_merits_proceeding`, which requires the row's `date_cert_granted`, and
    dates the grant moment from it. So an open merits-stage event on a row whose
    grant column is NULL is one no re-ingest or convergence pass reproduces —
    the shape left behind when the live re-poll stops reading a grant out of the
    proceedings and overwrites the stored date with NULL (that column is in none
    of the upsert's latch families). Removal rather than a reopen, but *not*
    because the event stays forecastable: the fan-out already refuses it, since
    a merits event is admitted only by `_merits_forecastable`, which needs the
    same grant column, and `unforecastable_listed_events` names this exact
    shape. The warrant is that the row is unmintable, permanently unresolvable
    (merits detection reads the same grant-gated columns, so nothing ever closes
    it), and so parks forever on the listed-unforecastable triage surface — a
    permanent dangling row rather than a mispredicted cell. Resolved merits
    events are out of population — one carries an observed judgment — as are
    events whose case row is absent, since the grant column cannot be read for
    them, and rows still labelled with a merits-proceeding disposition, where
    deleting the event would drop the docket out of the live rotation that would
    restore the date and so could not be undone. An event carrying committed
    predict/evaluate output, or a committed `outcome.json` the open corpus row
    contradicts, is skipped and reported instead. `--include-failed-attempts`
    narrows the first of those skips to what it is really protecting: a phantom
    that reached the fan-out before it was recognized carries only the
    `attempt.json` failure records of the cells that ran against it, which
    document spend on an event that names nothing the docket supports; removing
    them with it trades that failure history for a ledger with no dangling
    phantom paths. Which is worth more is a judgement about the record, so it is
    an explicit choice rather than the default, and its condition is stricter
    than "nothing predicted or graded": every file under `predictions/` must be
    named `attempt.json` and there must be no `evaluations/` directory, so a
    `usage.json` or `retrieval_log.json` the harness left beside an attempt
    record keeps the event skipped. Idempotent. Dry-run by
    default; `--apply` writes, and refuses above `--max-removals`: the
    population is finite and non-growing (no mint produces the shape), so a
    large count means the predicate widened — triage before raising the bound.
    Run where the corpus is pulled — a dev checkout dry-runs it, and the apply
    half belongs in run-repair's `merits-phantom-removal` pass, which holds the
    corpus-write
    credentials; the ledger directory goes first, then the corpus row, so an
    interrupted run leaves the row as the detection handle for the next pass.
    Fails loud if the corpus is absent.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the removal.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        if apply:
            preview = remove_ungranted_merits_events(
                conn,
                settings.data_root,
                apply=False,
                include_failed_attempts=include_failed_attempts,
            )
            if len(preview.removed) > max_removals:
                typer.echo(
                    f"remove-ungranted-merits-events: refusing to apply "
                    f"{len(preview.removed)} removals (--max-removals {max_removals}). "
                    "The population this sweep removes is finite and non-growing; "
                    "a count this size means the predicate widened — triage before "
                    "raising the bound.",
                    err=True,
                )
                raise typer.Exit(code=1)
        result = remove_ungranted_merits_events(
            conn,
            settings.data_root,
            apply=apply,
            include_failed_attempts=include_failed_attempts,
        )
    verb = "removed" if apply else "would remove"
    typer.echo(
        f"remove-ungranted-merits-events ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.removed)} event(s); skipped {len(result.skipped)} for triage"
    )
    for ref in result.removed:
        typer.echo(f"  {verb} {ref}")
    for ref, reason in result.skipped:
        typer.echo(f"  skipped {ref}: {reason}")


@app.command("normalize-docket-markings")
def normalize_docket_markings_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Rewrite the marked rows; omit for a dry-run report."),
    ] = False,
    max_rewrites: Annotated[
        int | None,
        typer.Option(
            "--max-rewrites",
            help="Blast-radius bound, required with --apply: refuse to apply more than this.",
        ),
    ] = None,
) -> None:
    """Converge stored docket numbers on their marking-free spelling.

    Drains the population the ``docket_numbers_carry_no_capital_marking`` corpus
    check reports, and is court-agnostic for the same reason — the marking is a
    SCOTUS habit upstream, but a pass filtering on court would leave a row that
    check reports with no repair.

    The ingest write site stores the number with the Court's ``*** CAPITAL CASE ***``
    marking removed and raises ``capital_case`` beside it, so the flag carries what
    the marking was the only record of. A stored row converges on that spelling only
    when the write site touches it again, and no automatic channel does so outside
    the live slice: a live-slice row normalizes on its next poll, while a row
    outside it converges only under a re-read aimed at it (``refresh-dockets`` on
    named rows, or a Term re-walk). This is the dedicated sweep that clears the
    backlog without one, reading the row with ``strip_docket_annotation`` and
    raising the flag with
    ``is_capital_docket_number``: the same pair the write site uses, so the number
    kept and the flag raised can never disagree about what was there.

    Selection is by the marking's **exact words**, never the ``*** … ***`` shape the
    comparison key reads. A shape match treats the asterisks as delimiters, so on a
    consolidated circuit docket that uses ``***`` as a separator between numbers it
    would delete a whole docket number out of the column that is the record —
    tolerable in a comparison key, where over-stripping costs only a missed join,
    and not tolerable here.

    The rewrite cannot mint a duplicate pair for ``dedupe-live-rows`` to find. Both
    SCOTUS channels reconcile identity on ``norm_dn``, which already strips the
    annotation by shape, so the marked and marking-free spellings of one docket
    compare equal to the join before the rewrite as well as after: no row moves into
    or out of any group. Rows that already share a normalized identity with another
    row are reported as a count, because they are the dedupe pass's population and
    this pass neither creates nor resolves them — it only makes the collision
    visible in the stored spelling.

    Idempotent: a rewritten row no longer carries the marking, so it leaves the
    population it was selected from, and ``capital_case`` max-latches so the flag can
    only advance. Run where the corpus is pulled — a dev checkout dry-runs it, and
    the apply half belongs in run-repair's `normalize-docket-markings` pass,
    which holds the corpus-write
    credentials. ``--apply`` refuses above ``--max-rewrites``: the population is
    finite and non-growing (the write site strips at ingest), so a count above the
    number read in the dry run means the predicate widened — triage before raising
    the bound. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    if apply and max_rewrites is None:
        typer.echo(
            "normalize-docket-markings: --apply requires an explicit --max-rewrites. "
            "Read the dry run first and pass the count you are approving.",
            err=True,
        )
        raise typer.Exit(code=2)
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the convergence.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = normalize_docket_markings(conn, apply=apply, max_rewrites=max_rewrites)
    if result.refused:
        typer.echo(
            f"normalize-docket-markings: refusing to apply {len(result.rewritten)} rewrites "
            f"(--max-rewrites {max_rewrites}). The population this sweep converges is finite "
            "and non-growing; a count this size means the predicate widened — triage before "
            "raising the bound.",
            err=True,
        )
        raise typer.Exit(code=1)
    verb = "rewrote" if apply else "would rewrite"
    shared = sum(1 for entry in result.rewritten if entry.shares_identity)
    typer.echo(
        f"normalize-docket-markings ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.rewritten)} marked docket number(s); "
        f"{shared} already share a normalized identity with another row"
    )
    for entry in result.rewritten:
        # Named as a shared identity rather than as the dedupe pass's work: that
        # pass acts only on groups of exactly two, so a three-plus group shares a
        # key here and is still left alone there.
        note = " [shares a normalized identity with another row]" if entry.shares_identity else ""
        typer.echo(f"  {verb} {entry.case_id}: {entry.was!r} -> {entry.now!r}{note}")


@app.command("backfill-response-fields")
def backfill_response_fields_cmd(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Fill the dated signals; omit for a dry-run report."),
    ] = False,
    max_fills: Annotated[
        int | None,
        typer.Option(
            "--max-fills",
            help="Blast-radius bound, required with --apply: refuse to apply more than this.",
        ),
    ] = None,
) -> None:
    """Re-derive the dated interim/merits signals from each row's newest live snapshot.

    ``response_requested_at``, ``response_filed_at`` and ``merits_brief_filed`` are
    parsed at ingest from the proceedings list. A row polled before those columns
    existed carries the undated ``response_requested`` flag with no date beside it,
    and no channel will ever correct it: the live poller serves the **undecided**
    slice, so a decided row is never re-polled, and the flag is a max-latched boolean
    a later write cannot turn back into a question. The gaps are recoverable from the
    corpus alone — the newest stored live-shaped snapshot is the same payload the
    original ingest read — so this re-parses it with the same pure parsers rather
    than re-fetching.

    A sibling of the live-signal back-fill rather than a widening of it, and the
    reason is that pass's predicate. A NULL ``distribution_count`` is the
    parse-coverage sentinel for the whole live-signal family, and that pass consumes
    it, writing the count **unconditionally** with no max latch — sound only because
    its predicate guarantees the column was NULL. Selecting rows whose count is
    already stored would let a payload served with its proceedings degraded, which
    parses as a confident ``0``, overwrite a good stored count: the precise
    regression the latch exists to reject.

    The three columns are fill-in only, matching the latch family they sit in on the
    upsert path, so a stored value is never overwritten and the pass converges. That
    also makes a degraded payload cheap here in a way it is not for a count — every
    parser below yields ``None``, filling nothing, rather than a confident zero that
    asserts a fact. Rows with no stored live-shaped snapshot are counted and
    reported, never failed: under the corpus-split mode the payloads live in the
    content store, and a poll that 404-stamped without storing one leaves nothing to
    re-read. The write is a direct ``UPDATE`` of the index and never the casestore
    mirror, so a store-side rebuild from ``case.json`` would resurrect the NULLs.

    Idempotent. Run where the corpus is pulled — a dev checkout dry-runs it, and the
    apply half belongs in run-repair's `response-backfill` pass, which holds the
    corpus-write
    credentials. ``--apply`` refuses above ``--max-fills``, which counts the rows
    actually filled — finite and non-growing, since ingest fills these columns going
    forward. The ``candidates`` denominator beside it is not: the granted arm admits
    every new cert grant that has not yet drawn a respondent brief, so a rising
    candidate count is the ordinary docket rather than a widened predicate. Prints
    each filled row with the dates it gains. Fails loud if the corpus is absent.
    """
    settings = get_settings()
    if apply and max_fills is None:
        typer.echo(
            "backfill-response-fields: --apply requires an explicit --max-fills. "
            "Read the dry run first and pass the count you are approving.",
            err=True,
        )
        raise typer.Exit(code=2)
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it (fedcourts corpus-pull) "
            "before running the back-fill.",
            err=True,
        )
        raise typer.Exit(code=1)
    with corpus.connect(db_path) as conn:
        result = backfill_response_fields(conn, apply=apply, max_fills=max_fills)
    if result.refused:
        typer.echo(
            f"backfill-response-fields: refusing to apply {len(result.filled)} fills "
            f"(--max-fills {max_fills}). The population this sweep repairs is finite and "
            "non-growing; a count this size means the predicate widened — triage before "
            "raising the bound.",
            err=True,
        )
        raise typer.Exit(code=1)
    verb = "filled" if apply else "would fill"
    typer.echo(
        f"backfill-response-fields ({'applied' if apply else 'dry-run'}): "
        f"{verb} {len(result.filled)} of {result.candidates} candidate(s); "
        f"{result.unchanged} read with nothing to fill; "
        f"{result.no_snapshot} with no stored snapshot; "
        f"{result.no_proceedings} whose snapshot discloses no proceedings"
    )
    for fill in result.filled:
        gained = ", ".join(
            f"{name} {value.isoformat()}"
            for name, value in (
                ("response_requested_at", fill.response_requested_at),
                ("response_filed_at", fill.response_filed_at),
                ("merits_brief_filed", fill.merits_brief_filed),
            )
            if value is not None
        )
        typer.echo(f"  {verb} {fill.case_id}: {gained}")


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


def _work_tree_root() -> Path | None:
    """The git work tree the process is running in, or ``None`` outside one.

    Walks up for the ``.git`` entry — a directory in a normal clone, a file in a
    linked worktree — so a caller cannot land a never-commit working file in the
    checkout by aiming outside ``data/``.
    """
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


@app.command("qp-corpus")
def qp_corpus(
    out: Annotated[Path, typer.Option(help="JSON output path for the extracted texts.")],
    corpus_db: Annotated[
        Path | None,
        typer.Option("--corpus", help="Corpus database (default: <corpus_root>/corpus.db)."),
    ] = None,
    all_texts: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Measurement form: every stored questions-presented row in the blob, unscoped.",
        ),
    ] = False,
) -> None:
    """Extract the stored ``questions-presented`` texts a topic labeler reads.

    Writes a JSON list of ``{case_id, docket_number, text}`` in ``case_id``
    order — the whole input a ``qp-topic-v0`` labeler is entitled to, since the
    vocabulary is text-only (``docs/qp-topic.md``): no docket context, no case
    name, no outcome, so a label can never encode a decision the text predates.

    **Scoped to the labeling population** by default: the live/historical
    slice's modern discretionary-cert petitions — exactly the frame the docket
    pack's topic section is computed over, so every labeled row has a published
    home and nothing in that frame is unlabelable. Narrowing further to the
    predict-scope segment is deliberately *not* done: it would drop the
    in-forma-pauperis stream while the hand reference set spans both, which
    would either put the publication gate's coverage floor out of reach or,
    with the reference set carried back in, make an IFP docket number a certain
    reference-membership tell (``docs/qp-topic.md``). ``--all`` is the unscoped
    **measurement** form — every stored questions-presented row in the blob,
    whatever its case — for answering what a given file holds. It is not a
    labeling selection.

    Reads each scoped case's documents through the registered payload path, so
    the extract serves from the per-case content store under the corpus split
    and from the blob otherwise; ``--all`` reads the blob's ``documents`` table
    directly, which a split blob leaves empty by construction. Opens the corpus
    strictly read-only and never migrates it, so either form is safe against a
    pulled blob. A row whose case carries no docket number, or whose stored text
    is empty, is skipped and counted rather than guessed at — the docket number
    is half the key the reference join is checked on, and an empty extraction is
    nothing to label.

    **Refuses an extract larger than the labeling ceiling**
    (:data:`~fedcourtsai.pipeline.qp_topics.LABEL_ROW_CEILING`), printing the
    count and the scope it would have had to label. A labeling dispatch is one
    headless turn under a hard step cap, and only a *complete* label file yields
    an artifact, so an over-budget extract does not buy partial coverage — it
    buys a killed step, full spend, and no artifact. The refusal is the count:
    it is what a maintainer needs to decide what to do next, and it costs the
    extract job rather than the labeling one.

    The extract is a working file for one labeler run, **never a committed
    artifact**: it enumerates the ingested corpus and republishes stored
    petition text, neither of which any committed surface does, so writing it
    anywhere inside the work tree is refused outright rather than left to
    reviewer attention — an untracked file in the checkout is one ``git add -A``
    from being committed.
    """
    settings = get_settings()
    destination = out.resolve()
    for boundary in (_work_tree_root(), settings.data_root.resolve()):
        if boundary is not None and (destination == boundary or boundary in destination.parents):
            typer.echo(
                f"qp-corpus: refusing to write the extract inside the checkout ({boundary}); "
                "it republishes stored petition text and enumerates the ingested corpus",
                err=True,
            )
            raise typer.Exit(code=2)
    db_path = corpus_db if corpus_db is not None else corpus.corpus_db_path(settings.corpus_root)
    if not db_path.is_file():
        typer.echo(f"qp-corpus: no corpus at {db_path} (run `fedcourts corpus-pull`)", err=True)
        raise typer.Exit(code=1)
    scope = (
        "every stored questions-presented row in the blob"
        if all_texts
        else "live-slice modern discretionary-cert petitions"
    )
    conn = sqlite3.connect(f"file:{quote(str(db_path.resolve()))}?mode=ro&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        extract = questions_presented_extract(conn, scoped=not all_texts)
    except Exception as exc:
        # Deliberately broad, and deliberately a named refusal. Under the split
        # the scoped pass's reads are content-store GETs, which surface
        # transport failures (denied credentials, throttling, an expired
        # session) as whatever the client raises, and `prefetch_by_case`
        # propagates by contract. A traceback in the extract job says nothing
        # useful in a run summary; this says which blob and which store failed,
        # and no partial extract is written either way.
        typer.echo(f"qp-corpus: cannot read stored documents for {db_path}: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    finally:
        conn.close()
    if not extract.rows:
        # An empty extract is a mis-wired run, never a labeling task: the blob
        # carries no document text for this scope (a payload-free index whose
        # content store is not wired, or `--all` against a split blob, whose
        # texts live in the store), so exiting 0 here would hand a labeler an
        # empty file and call it done.
        typer.echo(
            f"qp-corpus: no question-presented text in {db_path} for {scope} "
            f"({extract.skipped} row(s) skipped) — wrong blob for this command?",
            err=True,
        )
        raise typer.Exit(code=1)
    if len(extract.rows) > qp_topics.LABEL_ROW_CEILING:
        typer.echo(
            f"qp-corpus: refusing to write {len(extract.rows)} row(s) — over the "
            f"{qp_topics.LABEL_ROW_CEILING}-row labeling ceiling. Scope: {scope}. "
            "The labeler runs as one headless turn under a hard step cap and only a "
            "complete label file yields an artifact, so this extract would spend the "
            "run and produce nothing. Nothing was written, and there is no flag that "
            "makes this proceed: labeling this population needs a deliberately "
            "partial cut, which is a design decision and is not built (see "
            "docs/qp-topic.md). Do not truncate the extract by hand — case_id order "
            "is docket-number order, so a prefix selects on docket number.",
            err=True,
        )
        raise typer.Exit(code=1)
    write_raw_json(
        out,
        [
            {"case_id": row.case_id, "docket_number": row.docket_number, "text": row.text}
            for row in extract.rows
        ],
    )
    if extract.skipped:
        typer.echo(
            f"qp-corpus: skipped {extract.skipped} row(s) with no docket number or no text",
            err=True,
        )
    typer.echo(f"qp-corpus: {len(extract.rows)} question(s) presented ({scope}) -> {out}")


@app.command("qp-topics")
def qp_topics_cmd(
    labels: Annotated[
        Path,
        typer.Option(exists=True, help="Labeler's JSONL: one object per labeled text."),
    ],
    texts: Annotated[
        Path,
        typer.Option(exists=True, help="The `qp-corpus` extract, for the shadow pass."),
    ],
    labeler: Annotated[
        str, typer.Option(help="Who assigned the labels — engine and model, free-form.")
    ],
    out: Annotated[
        Path | None,
        typer.Option(help="JSON output path (default: <data_root>/qp-topics/qp-topics.json)."),
    ] = None,
) -> None:
    """Measure a topic labeler against the reference set and write its labels artifact.

    Reads the labeler's JSONL intermediate, validates every label against the
    ``qp-topic-v0`` vocabulary, joins it to the hand reference set on ``case_id``
    **and** ``docket_number`` — a pair that half-matches is a mis-join and stops
    the run rather than measuring one case's label against another's text — and
    records the resulting agreement, the triangle confusion matrix, and the
    shadow rules' disagreement rate. What comes out is agreement with a single
    v0 reference rater, not accuracy (``docs/qp-topic.md``).

    Below the publication gate the artifact is **not written**: the measured rate
    is printed and the command exits non-zero. The gate takes two conditions —
    the agreement rate, and how much of the reference set the run actually
    covered, since a high rate over a handful of self-chosen entries measures
    nothing. There is no override flag for either, because the gate is the only
    thing standing between a drifted labeler and a published topic distribution.
    """
    settings = get_settings()
    reference_path = qp_topics.reference_path(settings.data_root)
    if not reference_path.is_file():
        typer.echo(f"qp-topics: no reference set at {reference_path}", err=True)
        raise typer.Exit(code=1)
    try:
        artifact = qp_topics.build_labels(
            entries=qp_topics.read_label_lines(labels),
            texts=qp_topics.read_texts(texts),
            reference=read_model(reference_path, QpTopicReference),
            labeler=labeler,
        )
    except qp_topics.QpTopicError as exc:
        typer.echo(f"qp-topics: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"qp-topics: {artifact.cases} labeled case(s) by {artifact.labeler}")
    typer.echo(qp_topics.render_agreement(artifact.agreement))
    typer.echo(
        f"  shadow:    {artifact.shadow.disagreements} disagreement(s) on "
        f"{artifact.shadow.fired} rule firing(s) over {artifact.shadow.texts} text(s) — "
        "the rules are unmeasured off the reference set, so only the movement between "
        "runs of one labeler reads"
    )
    if not artifact.agreement.gate_passed:
        agreement = artifact.agreement
        rate = agreement.overall_rate
        measured = "nothing measured" if rate is None else f"{rate:.1%}"
        reference_cases = agreement.overall_n + agreement.uncovered
        covered = agreement.overall_n / reference_cases if reference_cases else 0.0
        typer.echo(
            f"qp-topics: refusing to write — agreement {measured} of n={agreement.overall_n} "
            f"against the {qp_topics.AGREEMENT_GATE:.0%} publication gate, over "
            f"{covered:.1%} of the reference set against a {qp_topics.COVERAGE_FLOOR:.0%} "
            "coverage floor",
            err=True,
        )
        raise typer.Exit(code=1)
    destination = out if out is not None else qp_topics.labels_path(settings.data_root)
    write_json(destination, artifact)
    typer.echo(f"qp-topics: gate passed -> {destination}")


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

    Resolves the pointer the read paths honor — the out-of-band override when
    set, else the committed ``corpus/corpus.db.ref`` — against the out-of-band
    remote URL, streams the blob to ``corpus/corpus.db``, and verifies its
    digest and size before the file lands — a truncated or corrupted transfer
    fails loudly instead of masquerading as the corpus.
    """
    if missing_pointer not in {"fail", "warn"}:
        typer.echo(f"--missing-pointer must be 'fail' or 'warn', not {missing_pointer!r}", err=True)
        raise typer.Exit(code=2)
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    pointer: Path | corpus_ranged.IndexPointer
    if settings.corpus_pointer is not None:
        # The override names a specific published blob; a missing committed
        # file is irrelevant to it, so the --missing-pointer modes don't apply.
        try:
            pointer = corpus_ranged.parse_pointer_override(settings.corpus_pointer)
        except corpus_ranged.RangedBackendError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    else:
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
    # The durable provenance record: the override dies with the shell, the
    # pulled file does not, so the sidecar (gitignored) is what lets a later
    # shell's `corpus-info` catch a blob that is not the committed pointer's.
    pulled = (
        pointer
        if isinstance(pointer, corpus_ranged.IndexPointer)
        else corpus_ranged.read_index_pointer(pointer)
    )
    corpus_remote.write_pointer(corpus_remote.pulled_pointer_path_for(db_path), pulled)
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

    Refuses to run while the out-of-band pointer override is set: a writer
    owns the *committed* pointer, and an environment that overrides reads is
    not reading the pair it would be publishing to.
    """
    settings = get_settings()
    if settings.corpus_pointer is not None:
        typer.echo(
            "corpus-push refuses to run while the out-of-band corpus pointer "
            "override is set (unset FEDCOURTS_CORPUS_POINTER / CORPUS_POINTER): "
            "a writer publishes the committed pointer, and an override in the "
            "same environment means reads and writes would name different pairs.",
            err=True,
        )
        raise typer.Exit(code=1)
    db_path = corpus.corpus_db_path(settings.corpus_root)
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


@app.command("corpus-seed-slice")
def corpus_seed_slice(  # noqa: PLR0913, PLR0917 - a CLI entrypoint; options map 1:1 to inputs
    source_remote: Annotated[
        str,
        typer.Option(
            help="The PRODUCTION corpus remote the slice is read from, and the "
            "destination rail's comparison basis. Pinned here rather than read "
            "from the environment, so repointing the environment's corpus "
            "variables cannot move it."
        ),
    ],
    source_casestore: Annotated[
        str,
        typer.Option(
            help="The PRODUCTION content store the slice's payloads are read "
            "from — the other half of the pinned source the rail compares "
            "destinations against."
        ),
    ],
    dest_remote: Annotated[
        str,
        typer.Option(
            help="Destination corpus remote as an s3 bucket URL with an optional "
            "prefix; must NOT be the pinned source remote."
        ),
    ],
    dest_casestore: Annotated[
        str,
        typer.Option(
            help="Destination content store as an s3 bucket URL with an optional "
            "prefix; must NOT be the pinned source store."
        ),
    ],
    dockets: Annotated[
        list[str] | None,
        typer.Option(
            "--dockets", help="A `<court>/<docket>` case id to include; repeat for several."
        ),
    ] = None,
    dockets_file: Annotated[
        Path | None,
        typer.Option(help="File of case ids, one per line (`#` comments and blanks ignored)."),
    ] = None,
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Seed the destination; omit for the dry-run census."),
    ] = False,
    max_cases: Annotated[
        int,
        typer.Option(help="Hard bound on cases seeded; the rest are reported as dropped."),
    ] = corpus_seed.DEFAULT_MAX_CASES,
    stage_db: Annotated[
        Path | None,
        typer.Option(
            help="Runner-local file the slice blob is built at; defaults to a "
            "gitignored path under the corpus root, with the pointer beside it."
        ),
    ] = None,
    summary_out: Annotated[
        Path | None,
        typer.Option(help="Append the Markdown census + verdict here (the step summary)."),
    ] = None,
) -> None:
    """Copy a named docket slice into a **staging** corpus (its own bucket pair).

    Builds the two halves a split-mode corpus has: a payload-free index blob
    carrying only the slice's `cases` and `events` rows — rebuilt through the
    corpus's own upsert seams, then published to `--dest-remote` at its
    content-addressed key exactly as `corpus-push` publishes production's — and
    a key-level copy of every content-store object under each case's prefix
    into `--dest-casestore`, so the staging store holds the writers' own bytes.
    Objects are copied before the blob is published, so a reader resolving the
    new pointer always finds the payloads its rows refer to; within a case the
    documents manifest lands after the leaves it names.

    Reads the source stores read-only, and the source is **pinned by
    `--source-remote` / `--source-casestore`** — never resolved from the
    environment, so a shell or Actions environment repointed at the staging
    pair cannot move what the seeder reads or what its rail compares against.
    The ranged backend resolves the checkout's committed pointer against the
    pinned remote (no pull — a bounded slice is a handful of point lookups);
    under the `local` backend the source blob is whatever pulled file is on
    disk, which the pin does not govern — the workflow always runs ranged.
    **Refuses**, in order: a corpus pointer override in the environment (the
    index half of the self-seeding hazard — a dev shell flipped to staging
    may carry one); a destination that *is* either pinned source store, or that
    sits inside either source bucket at any prefix — a local second line
    behind the IAM policy, which is what actually keeps the seeding role
    read-only on production.

    Convergent rather than idempotent in the strict sense: the remote is
    content-addressed and add-only, and write-once keys (dated snapshots,
    content-addressed document leaves) the destination already holds are
    skipped — but the three manifests the writers overwrite in place
    (`case.json`, `events.json`, `documents/documents.json`) are re-copied on
    every apply, or a re-seed would leave the staging store describing a case
    the source has moved past.

    Dry-run by default, printing the per-case census (rows, events, snapshots,
    documents, objects). An `--apply` additionally reports what it copied and
    the published pointer — the value a staging consumer resolves, and the one
    thing the thrown-away runner would otherwise lose.
    """
    settings = get_settings()
    staged = stage_db if stage_db is not None else settings.corpus_root / "staging-slice.db"
    try:
        # Both store pairs fail closed at construction on an empty slot, so an
        # unset workflow variable — which resolves to an empty string — is
        # refused here, before anything else runs.
        source = corpus_seed.Source(remote_url=source_remote, casestore_url=source_casestore)
        destination = corpus_seed.Destination(remote_url=dest_remote, casestore_url=dest_casestore)
        case_ids = corpus_seed.parse_case_ids(dockets or [], path=dockets_file)
        # Every rail runs before a client is built or a store is opened, so a
        # dispatch aimed at its own source — or at the checkout's own corpus
        # blob, or under a pointer override — is refused in milliseconds and
        # touches nothing. The pointer rail must fire HERE to precede the
        # read: `seed_slice` takes an already-open connection, so its own
        # re-assertion guards only the write half for a library caller. The
        # other two are genuinely re-asserted there; these calls are a
        # duplicate, not a substitute.
        corpus_seed.assert_no_pointer_override(settings)
        corpus_seed.assert_destination_is_not_the_source(destination, source=source)
        corpus_seed.assert_stage_db_is_not_the_corpus(staged, settings=settings)
    except corpus_seed.SeedSliceError as exc:
        typer.echo(f"corpus-seed-slice: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if corpus.resolve_backend() == "local" and not db_path.exists():
        # `connect` would create an empty database and report every requested
        # case missing; say what is actually wrong instead.
        typer.echo(
            f"corpus-seed-slice: no corpus at {db_path} — `fedcourts corpus-pull` "
            "to fetch it, or read it in place with the ranged backend.",
            err=True,
        )
        raise typer.Exit(code=1)
    try:
        # The pin's resolved identity, for the census: which source blob this
        # run measured. Only the ranged read has one — a local file is
        # whatever was pulled, and the committed pointer does not describe it.
        source_pointer = (
            corpus.resolve_read_pointer(db_path) if corpus.resolve_backend() == "ranged" else None
        )
        with corpus.connect_readonly(db_path, remote_url=source.remote_url) as conn:
            result = corpus_seed.seed_slice(
                source_conn=conn,
                source=source,
                case_ids=case_ids,
                destination=destination,
                settings=settings,
                stage_db=staged,
                apply=apply,
                max_cases=max_cases,
                source_pointer=source_pointer,
            )
    except (
        corpus_seed.SeedSliceError,
        casestore.CasestoreError,
        corpus_remote.CorpusRemoteError,
        corpus_ranged.RangedBackendError,
        # `connect_readonly` rejects the casestore and service backends with a
        # bare ValueError — a backend setting this command cannot serve. Caught
        # here so it lands in the same one-line message as every other refusal
        # rather than as a traceback.
        ValueError,
    ) as exc:
        typer.echo(f"corpus-seed-slice: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    markdown = result.render_markdown()
    if summary_out is not None:
        with summary_out.open("a", encoding="utf-8") as fh:
            fh.write(markdown)
    typer.echo(markdown)
    if result.census.missing:
        # Loud but not fatal: a slice naming a case the corpus does not carry
        # is an operator mistake worth seeing, and the cases that do exist are
        # still worth seeding.
        typer.echo(
            f"corpus-seed-slice: {len(result.census.missing)} requested case(s) "
            "have no row in the source corpus",
            err=True,
        )


@app.command()
def leaderboard(
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <metrics_root>/leaderboard.json)."),
    ] = None,
    all_versions: Annotated[
        bool,
        typer.Option(
            "--all-versions",
            help="Include every process version, not only the frozen headline "
            "(the shakedown pooled view).",
        ),
    ] = False,
) -> None:
    """Rank predictors from the evaluations ledger into ``metrics/leaderboard.json``.

    Deterministic and offline: aggregates the newest committed
    ``evaluation.json`` per (case, event, predictor, evaluator) under ``data/``
    into one best-first standing per predictor — accuracy, mean
    Brier score, mean vote accuracy (declared merits moments only — an
    individual cert vote is never scored, so the ranked board carries no vote
    mean), a reasoning-quality summary, and counts,
    each reported **per stratum** (forward forecasts vs retrospective cells vs
    procedural mootness-basis cells, never blended and with only the timing
    strata ranked; see the ``Leaderboard`` schema). The ranked board is the
    **cert stage**; a non-cert stage's cells report in their own unranked
    ``stages`` block, never pooled.

    Each stratum also carries the **realized-Term** skill mean beside the
    prior-Term one — the same band scored against the rate its own Term actually
    realized, read from the committed ``metrics/statpack.json`` at build time
    rather than from the cell, so the whole board shares one vintage. It is ex
    post, never ranks, and is never pooled with the prior-Term mean; the claim
    contract is ``metrics/README.md``. Without a readable pack the column is
    absent altogether, which the command says out loud rather than leaving it to
    read as "no cell qualified". The result
    writes through the shared serializer for minimal diffs. Reruns over an
    unchanged ledger and pack reproduce the file byte for byte.

    Two audit figures ride beside the standings, because neither is recoverable
    from the ranked numbers themselves. ``superseded_gradings`` counts the
    gradings the run collapse dropped: every figure on the board is taken after
    it, so a re-graded cell is otherwise indistinguishable from a once-graded
    one. Each entry's ``events_scored``, against its population's own, is the
    scored set's coverage: grading is gated at ``(evaluator, event)`` grain, so
    a predictor whose cells landed after its events were graded is compared
    over a subset — the command warns when that inequality exists, per
    population, and the ranks adjust for none of it. Silence is not a licence:
    equal coverage certifies the same event set, never the same stratum mix or
    panel depth (``metrics/README.md``).

    Defaults to the **frozen** headline: only cells whose predictor ran the
    blessed frozen process. Until a stamped cell postdates the freeze instant
    that is legitimately empty. ``--all-versions`` pools every process version.
    """
    settings = get_settings()
    scope: Literal["frozen", "all"] = "all" if all_versions else "frozen"
    frozen_only = not all_versions
    run = stratify(settings.data_root, frozen_only=frozen_only)
    _report_forward_claim_exclusions(run.excluded)
    cells = run.cells
    # The realized-Term skill column is scored at render against the committed
    # pack, so every cell on a board shares one vintage. Best-effort like the
    # ops feeds: no pack means the column is absent, never partly computed.
    statpack = _read_best_effort(settings.metrics_root / "statpack.json", StatPack)
    board = build_leaderboard(
        cells,
        big_case=big_case_agreement(settings.data_root, frozen_only=frozen_only),
        evaluators=evaluator_agreement(settings.data_root, frozen_only=frozen_only),
        process_scope=scope,
        skills=skill_components(cells, settings.data_root, statpack),
        forward_claim=_forward_claim_from(run),
        superseded_gradings=run.superseded,
    )
    destination = out if out is not None else settings.metrics_root / "leaderboard.json"
    write_json(destination, board)
    empty_note = (
        "  (frozen headline empty — no frozen-process evaluations yet)"
        if scope == "frozen" and board.predictors_ranked == 0
        else ""
    )
    # A re-grade is invisible on the board's own figures — every one of them is
    # taken after the collapse — so the count says so in the log too, where a
    # maintainer who ran `evaluate-matrix --force`, or re-ran a cached matrix,
    # is watching.
    regrade_note = (
        f"  ({board.superseded_gradings} superseded grading(s) collapsed away)"
        if board.superseded_gradings
        else ""
    )
    # An unreadable pack and a board where no cell qualified both render the
    # realized-Term column as null/0, so the one that is an input failure has to
    # say so — a suppressed column must never read as a computed zero.
    if statpack is None:
        typer.echo(
            "leaderboard: no readable metrics/statpack.json — "
            "realized-Term skill omitted from every stratum.",
            err=True,
        )
    _report_uneven_coverage(board)
    typer.echo(
        f"leaderboard [{scope}]: {board.predictors_ranked} predictor(s) from "
        f"{board.evaluations_total} cert-stage evaluation(s) "
        f"({board.forward_evaluations} forward / "
        f"{board.retrospective_evaluations} retrospective / "
        f"{board.procedural_evaluations} procedural) over "
        f"{board.events_scored} scored event(s) "
        f"-> {destination}{empty_note}{regrade_note}"
    )


@app.command("claim-scores")
def claim_scores_command(
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <metrics_root>/claim-scores.json)."),
    ] = None,
    all_versions: Annotated[
        bool,
        typer.Option(
            "--all-versions",
            help="Include every process version, not only the frozen headline "
            "(the shakedown pooled view).",
        ),
    ] = False,
) -> None:
    """Roll the ledger's claim-score blocks into ``metrics/claim-scores.json``.

    Deterministic and offline: aggregates the newest committed
    ``evaluation.json`` per (case, event, predictor, evaluator) carrying a
    harness-computed ``claim_scores`` block into per-predictor,
    per-stratum claim-total means (floor and lift beside them, per-claim means,
    the largest single-claim contribution) plus the pre-registered **judge
    validation** — Kendall tau-b between mechanical claim totals and
    ``reasoning_quality`` grades, per stratum, suppressed below 10 pairs with
    the counts still published. Advisory beside the leaderboard, never a rank
    key; the interpretation contract is ``metrics/README.md``. Reruns over an
    unchanged ledger reproduce the file byte for byte.

    Defaults to the **frozen** headline exactly like ``leaderboard``; while no
    committed evaluation carries a block the artifact renders its honest
    fully-suppressed state (zero counts, every coefficient null).
    """
    settings = get_settings()
    scope: Literal["frozen", "all"] = "all" if all_versions else "frozen"
    run = stratify(settings.data_root, frozen_only=not all_versions)
    _report_forward_claim_exclusions(run.excluded)
    board = build_claim_scores(
        run.cells,
        process_scope=scope,
        forward_claim=_forward_claim_from(run),
    )
    destination = out if out is not None else settings.metrics_root / "claim-scores.json"
    write_json(destination, board)
    typer.echo(
        f"claim-scores [{scope}]: {board.cells_with_claims} of {board.evaluations_total} "
        f"evaluation(s) carry a claim block; forward judge agreement: "
        f"{agreement_summary(board.forward_agreement)} -> {destination}"
    )


@app.command("semantic-summary")
def semantic_summary_command(
    out: Annotated[
        Path | None,
        typer.Option(
            help="Output path (default: <metrics_root>/semantic-grades-<stratum>-<scope>.json)."
        ),
    ] = None,
    stratum: Annotated[
        str,
        typer.Option(
            help="Which stratum to summarize (" + ", ".join(get_args(Stratum)) + "). One "
            "call is one segment: grades are never pooled across strata, and a graded "
            "unit carries no stratum of its own, so this states the population rather "
            "than describing it."
        ),
    ] = "forward",
    all_versions: Annotated[
        bool,
        typer.Option(
            "--all-versions",
            help="Include every process version, not only the frozen headline "
            "(the shakedown pooled view).",
        ),
    ] = False,
) -> None:
    """Roll the ledger's semantic grade blocks into a census, published only above the floor.

    Deterministic and offline: collects every committed ``evaluation.json``
    carrying a ``semantic_grades`` block for one stratum, bridges each through
    the **declaration** (``fedcourtsai.pipeline.semantic`` — the declared set,
    never the grader's block, fixes what is graded), and rolls the units into
    per-claim counts, a pooled coverage census, and leave-one-out inter-grader
    agreement. Descriptive only: no score, no total, never a rank key, and never
    pooled with a mechanical claim score. The reading contract is
    ``metrics/README.md``; the methodology is ``docs/outcome-decomposition.md``,
    *The semantic family, alpha*, and it is alpha.

    Three things this command owes the roll-up, which sees only the units it is
    handed.

    It **segments**, on every axis the roll-up says is never pooled — stratum,
    process scope, and *vantage*. The last one is why the cells are filtered to
    each stage's **first declared moment** (``pipeline.moments.first_moment``),
    the rule ``claim_metrics`` keeps for the same reason: a set is declared on
    every moment of its stage, so a later moment carries the same block off a
    larger information set, and pooling the two would average a forecast taken
    at the grant with one taken after briefing. Stratum and scope are recorded
    on the artifact; a census that does not state them is not readable at all.

    It **deduplicates re-runs** to one grade per grader per cell, newest first
    on the harness clock (``integrity.evaluation_clock``) rather than the
    agent-written ``created_at``. The *ordering* is the one ``claim-scores``
    uses; the *key* is not, and must not be — that surface collapses across
    evaluators because their blocks are identical harness output, while here
    graders genuinely differ and collapsing them would destroy the very
    population the agreement figure is computed over. A grader's newest run
    decides, including when it carries no block: that is a withdrawn grade, not
    a reason to resurrect an older one.

    And it **withholds** on two independent preconditions, because
    ``metrics/README.md`` bars publication on either. The pooled census must
    clear the ``SEMANTIC_MIN_GRADED`` floor, and at least one grader must carry
    a non-null agreement coefficient — a count or share with no agreement
    figure beside it is one reader's opinion presented as a measurement, and a
    null coefficient is not an agreement figure. Below either, nothing is
    written and the state is printed, naming which precondition failed.

    So today it writes nothing and says so. The evaluate prompt asks a merits
    grader for a block, but no opinion body is ingested to grade against and
    both declared claims require a majority opinion, so every unit is the
    availability mask and the census carries no ordinal grades to publish.
    """
    if stratum not in get_args(Stratum):
        raise typer.BadParameter(
            f"unknown stratum {stratum!r}; expected one of {', '.join(get_args(Stratum))}"
        )
    segment = cast(Stratum, stratum)
    settings = get_settings()
    scope: Literal["frozen", "all"] = "all" if all_versions else "frozen"
    run = stratify(settings.data_root, frozen_only=not all_versions)
    _report_forward_claim_exclusions(run.excluded)
    latest: dict[tuple[str, str, str, str], tuple[tuple[datetime, str, str], Evaluation]] = {}
    for evaluation, cell_stratum, stage, moment in run.cells:
        if cell_stratum != segment or stage is None:
            continue
        if moment != moments.first_moment(stage):
            continue
        key = (
            evaluation.case_id,
            evaluation.event_id,
            evaluation.predictor_id,
            evaluation.evaluator_id,
        )
        order = (evaluation_clock(evaluation), evaluation.evaluator_id, evaluation.run_id)
        current = latest.get(key)
        if current is None or order > current[0]:
            latest[key] = (order, evaluation)
    units: list[semantic.GradedUnit] = []
    blocks = 0
    refused = 0
    for key in sorted(latest):
        evaluation = latest[key][1]
        if evaluation.semantic_grades is None:
            continue
        blocks += 1
        produced = semantic.graded_units(evaluation)
        if not produced:
            # `graded_units` refuses silently, five ways. A systematic refusal —
            # every grader stamping a superseded declaration, say — would
            # otherwise render as "few grades" rather than "many grades refused".
            refused += 1
        units.extend(produced)
    summary = semantic.summarize_semantic_grades(units, stratum=segment, process_scope=scope)
    graded = summary.overall.graded if summary.overall is not None else 0
    masked = summary.overall.not_addressed if summary.overall is not None else 0
    disputed = summary.overall.mask_disputed if summary.overall is not None else 0
    agreed = any(record.rank_agreement is not None for record in summary.agreement.values())
    census = (
        f"{blocks} block(s), {refused} refused; {graded} graded / {masked} masked / "
        f"{disputed} mask-disputed unit(s) over {summary.cells} cell(s) "
        f"on {summary.cases} case(s)"
    )
    if graded < semantic.SEMANTIC_MIN_GRADED or not agreed:
        reason = (
            f"below the {semantic.SEMANTIC_MIN_GRADED}-unit floor"
            if graded < semantic.SEMANTIC_MIN_GRADED
            else "no grader carries an agreement coefficient"
        )
        typer.echo(
            f"semantic-summary [{segment}/{scope}]: withheld — {reason}. {census}. Nothing written."
        )
        return
    destination = (
        out
        if out is not None
        else settings.metrics_root / f"semantic-grades-{segment}-{scope}.json"
    )
    write_json(destination, summary)
    typer.echo(
        f"semantic-summary [{segment}/{scope}]: {census}, "
        f"{summary.graders} grader(s), set(s) "
        f"{', '.join(summary.declared_set_versions)} -> {destination}"
    )


@app.command("tool-usage")
def tool_usage_command(
    out: Annotated[
        Path | None,
        typer.Option(help="Write the ToolUsage JSON artifact here (default: stdout only)."),
    ] = None,
    markdown_out: Annotated[
        Path | None, typer.Option(help="Write the Markdown rollup here (e.g. a run summary).")
    ] = None,
    all_versions: Annotated[
        bool,
        typer.Option(
            "--all-versions",
            help="Pool every process version in the usefulness block (default: frozen only).",
        ),
    ] = False,
) -> None:
    """Roll committed retrieval logs into an offered-vs-called tool report.

    Answers which configured MCP tools are actually earning their place: which
    were offered but never called, which are used by some engines and not
    others, and how often each is called and by whom. Reads ``data/`` only — no
    corpus, no network — so it runs offline and in the gate.

    The offered denominator comes from each log's ``mcp_tools`` snapshot, not
    from ``mcp_servers`` (which names servers, and a server advertises many
    tools). Logs written before that field existed contribute calls but no
    denominator, and are counted separately rather than read as offering
    nothing. Call names are normalized to ``<server>.<tool>`` first, because
    engines spell the same MCP tool differently.

    A zero means **never called**, not useless — the prompt may never mention
    the tool, or a sandbox may have blocked it. The report says so; check the
    cause before retiring anything.

    Beside that it reports **result observability** per engine (a captured
    result digest is the only evidence the answer side was recorded at all, so
    the rate is two-state and an engine that captured none has its dead-end rows
    withheld rather than printed as total), cuts by mode / role / actor, calls
    beside each cell's estimated cost, and **call volume against Brier** joined
    to the gradings of each predicted cell. That last block is a grade-bearing
    surface, so it is scoped to blessed processes by default — ``--all-versions``
    pools every version, including shakedown cells whose Brier is comparable to
    nothing — and it publishes no correlation for any population below the floor
    pre-declared as ``tool_usage.TOOL_USAGE_CORRELATION_MIN_CELLS``.
    """
    settings = get_settings()
    # The current manifest's advertised set, so a never-called tool is visible
    # even though no committed log predating `mcp_tools` carries its own
    # denominator. Union across both registries: a tool offered to evaluators
    # but not predictors is still offered.
    offered_now: set[str] = set()
    for filename in ("predictors.yaml", "evaluators.yaml"):
        path = settings.config_root / filename
        if path.exists():
            offered_now.update(mcp.manifest_tools(load_mcp_servers(path)))
    usage = tool_usage.build_tool_usage(
        settings.data_root, sorted(offered_now), frozen_only=not all_versions
    )
    markdown = tool_usage.render_tool_usage_markdown(usage)
    if out is not None:
        write_json(out, usage)
    if markdown_out is not None:
        write_text(markdown_out, markdown)
    typer.echo(markdown)
    never = sum(1 for e in usage.entries if e.calls == 0)
    typer.echo(
        f"tool-usage: {usage.logs} log(s), {len(usage.entries)} tool(s), "
        f"{never} offered but never called",
        err=True,
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
            "has no registered runner); a concrete backend ("
            + ", ".join(available_backends())
            + ") routes every predictor through that one backend "
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
    salience_cfg = load_salience_config(settings.config_root)
    with corpus.connect(db_path) as conn:
        items = select_cert_backtest_set(
            conn,
            limit=limit,
            scope=scope,
            spread=spread,
            salience_floor=salience_cfg.floor,
        )
        backtesters = default_backtesters(conn)
        provisioning: dict[str, int] = {}  # empty unless an agentic replay ran
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
            replayed, unavailable, provisioning = replay_predictors(
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
        segments = build_segment_context(
            conn, items, statpack, lookback_terms=salience_cfg.base_rate_lookback_terms
        )
        report = run_cert_backtest(backtesters, items, segments=segments, provisioning=provisioning)
    write_json(destination, report)
    typer.echo(
        f"cert-backtest: {report.predictors_evaluated} predictor(s) over "
        f"{report.events_scored} decided petition(s); always-deny floor "
        f"{report.always_denied_accuracy:.3f} -> {destination}"
    )


@app.command("salience-replay")
def salience_replay_cmd(
    terms: Annotated[
        str,
        typer.Option(
            help="Comma-separated October Terms whose resolved petitions to replay, "
            "e.g. '2022,2023,2024'."
        ),
    ],
    policies: Annotated[
        str,
        typer.Option(
            help="Comma-separated cutoff policies, each one cell per Term per "
            "registered salience version: " + ", ".join(p.value for p in CutoffPolicy) + "."
        ),
    ] = "arrival,distribution-1,resolution",
    out: Annotated[
        Path | None,
        typer.Option(help="Output path (default: <metrics_root>/salience-replay.json)."),
    ] = None,
) -> None:
    """Replay the salience gate over past Terms into ``metrics/salience-replay.json``.

    Runs **every registered** frozen scoring, banding, and per-conference
    selection over each named Term's resolved paid modern-cert petitions,
    projected to the state their dockets disclosed at each cutoff policy's
    moment (arrival / first distribution / the last pre-resolution
    distribution) — one projection per moment, shared across versions — and
    scores each would-have-been selection against the
    realized grant-family outcomes — what the numbers do and do not claim:
    ``metrics/README.md``. Deterministic, offline, and free: no model runs, no
    tokens are spent, and nothing under ``data/`` is touched.
    """
    try:
        term_years = [int(raw.strip()) for raw in terms.split(",") if raw.strip()]
    except ValueError:
        raise typer.BadParameter(
            f"terms must be comma-separated years, got {terms!r}", param_hint="--terms"
        ) from None
    if not term_years:
        raise typer.BadParameter("no Terms named", param_hint="--terms")
    if any(not 1900 <= year <= 2099 for year in term_years):
        # The parseable modern docket forms sit inside this range, so anything
        # outside it is a typo that would otherwise write an all-zero report.
        raise typer.BadParameter(
            f"terms must be four-digit October-Term years, got {terms!r}", param_hint="--terms"
        )
    policy_list: list[CutoffPolicy] = []
    for raw in policies.split(","):
        name = raw.strip()
        if not name:
            continue
        try:
            policy_list.append(CutoffPolicy(name))
        except ValueError:
            raise typer.BadParameter(
                f"unknown policy {name!r}; choose from " + ", ".join(p.value for p in CutoffPolicy),
                param_hint="--policies",
            ) from None
    if not policy_list:
        raise typer.BadParameter("no policies named", param_hint="--policies")
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    destination = out if out is not None else settings.metrics_root / "salience-replay.json"
    if not db_path.exists():
        write_json(
            destination,
            SalienceReplay(
                salience_version=SALIENCE_VERSION,
                salience_versions=list(registered_versions()),
                terms=term_years,
                policies=[str(p) for p in policy_list],
            ),
        )
        typer.echo(f"No corpus at {db_path} — wrote empty salience-replay report -> {destination}")
        return
    report = replay_gate(
        db_path,
        terms=term_years,
        policies=policy_list,
        config=load_salience_config(settings.config_root),
    )
    write_json(destination, report)
    typer.echo(
        f"salience-replay: {report.cells_evaluated} cell(s) over "
        f"Term(s) {', '.join(str(t) for t in term_years)} x "
        f"{len(policy_list)} policy(ies) x "
        f"{len(report.salience_versions)} version(s) -> {destination}"
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
    write_text(
        md_dest,
        analytics.render_statpack_markdown(
            pack, markdown_terms=load_statpack_config(settings.config_root).markdown_terms
        ),
    )
    typer.echo(
        f"statpack: {pack.corpus_rows} case(s), {len(pack.sections)} section(s) "
        f"-> {json_dest}, {md_dest}"
    )


@app.command()
def docket(
    out: Annotated[
        Path | None,
        typer.Option(help="JSON output path (default: <metrics_root>/docket.json)."),
    ] = None,
    markdown_out: Annotated[
        Path | None,
        typer.Option(help="Markdown output path (default: <metrics_root>/docket.md)."),
    ] = None,
    qp_topics_path: Annotated[
        Path | None,
        typer.Option(
            "--qp-topics",
            exists=True,
            help="QP-topic labels artifact backing the topic cut "
            "(default: <data_root>/qp-topics/qp-topics.json, silently absent until a "
            "labeler run lands; naming one that does not exist is an error).",
        ),
    ] = None,
) -> None:
    """Roll the corpus into the court-facing docket pack at ``metrics/docket.{json,md}``.

    Facts about the dockets — composition by court and era, cert dispositions,
    originating circuit and state courts, relist counts, CVSG status, the paid/IFP
    fee split, and a per-Term census of docketed filings against grant rate.
    Carries **no claim about this project's predictions**: no accuracy, no
    leaderboard, no salience, so it is readable and citable by someone with no
    interest in the models. Every cert cut is denial-reweighted, so its rates
    estimate the population rather than the walked sample, and each states its
    own denominator. Deterministic and
    offline: a pure function of the corpus and, where one is on disk, the
    ``qp-topic-v0`` labels artifact — so reruns over unchanged inputs reproduce
    both files byte for byte. Writes the empty zero-count pack when the corpus is
    absent (run after a corpus pull).

    The question-presented topic cut renders only from a gate-passing
    ``qp-topic-v0`` labels artifact, always beside its labeler and measured
    agreement and always carrying the coverage caveat of ``docs/qp-topic.md``;
    with none there, the document names the missing distribution among its gaps
    instead. The **default** path is allowed to be absent — that is the standing
    state until a labeler run lands — while a path named on the command line is
    checked, so a typo cannot quietly publish the pack without its cut.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    labels = (
        qp_topics_path if qp_topics_path is not None else qp_topics.labels_path(settings.data_root)
    )
    pack = analytics.build_docket_pack(corpus_db_path=db_path, qp_topics_path=labels)
    json_dest = out if out is not None else settings.metrics_root / "docket.json"
    md_dest = markdown_out if markdown_out is not None else settings.metrics_root / "docket.md"
    write_json(json_dest, pack)
    write_text(md_dest, analytics.render_docket_markdown(pack))
    typer.echo(
        f"docket: {pack.corpus_rows} case(s), {len(pack.sections)} section(s), "
        f"{len(pack.terms)} Term(s) -> {json_dest}, {md_dest}"
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
    *,
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id this run predicted/scored.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    # Typed as the enums, so typer renders the choice list into the metavar
    # itself; restating it in the help would be a second copy to drift.
    engine: Annotated[Engine, typer.Option(help="Engine that ran.")],
    role: Annotated[UsageRole, typer.Option(help="Which agentic stage this cell was.")],
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


@app.command("stamp-cell")
def stamp_cell(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to inputs
    *,
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id this cell predicted/scored.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    role: Annotated[str, typer.Option(help="predictor | evaluator.")],
    actor: Annotated[str, typer.Option(help="The predictor_id or evaluator_id for this cell.")],
    pipeline_sha: Annotated[
        str,
        typer.Option(
            help="Pipeline checkout commit (provenance); defaults to GITHUB_SHA, "
            "then the local git HEAD, else omitted."
        ),
    ] = "",
    stamped_at: Annotated[
        str, typer.Option(help="ISO timestamp of the stamp; defaults to now (UTC).")
    ] = "",
    regrade: Annotated[
        bool,
        typer.Option(
            "--regrade",
            help="Evaluator role only: recompute the harness-owned graded fields over "
            "the committed artifacts as they stand now, leaving each record's "
            "existing process_version exactly as its producing run stamped it.",
        ),
    ] = False,
) -> None:
    """Stamp a cell's ``prediction.json`` / ``evaluation.json`` with its process version.

    The harness owns the stamp, not the agent — so a cell's version is derived
    from the registry and prompt in force at run time, exactly like ``usage.json``
    reads the engine's own log rather than the agent's word. Runs as a post-agent
    step, before ``validate``.

    The digest is resolved from the working tree (:func:`process_version.digest_for_actor`):
    the actor's prompt-template bytes plus its resolved registry config. A missing
    artifact is a clean no-op (a no-output cell has nothing to stamp and is already
    routed to a draft), but a missing registry entry or prompt file exits non-zero
    — a config inconsistency must fail the cell loudly rather than ship an
    unstamped-but-frozen-looking prediction.

    For ``--role evaluator`` a single cell writes one ``evaluation.json`` per
    scored predictor, so every one under this evaluator+event+run is stamped —
    and each also gets its ``claim_scores`` block computed and written here
    (:func:`fedcourtsai.pipeline.claims.score_claims`, over the committed
    prediction, outcome, and statpack), plus its ``base_rate_salience_version``
    derived from the recorded ``base_rate_basis`` and the scored prediction's
    frozen context (:func:`_base_rate_salience_version_for`), so both are the
    harness's word and an evaluator-authored value never survives the stamp.

    ``correct`` is stamped on **every** stage, cert included
    (:func:`_harness_correct_for`): it is a label comparison between the scored
    prediction and the outcome with no baseline and so no band to choose, which
    is the only thing the cert exemption below is about — and it is the
    leaderboard's first rank key, so the ranked cert board's lead column would
    otherwise rest on the evaluator's word alone. Cleared where either committed
    artifact is unreadable, like the Brier.

    **Who owns the skill record.** The harness stamps it wherever the baseline
    pool is a Term-keyed ratio of published integer counts with no band to
    choose — every **merits** and every **interim** cell — because there the
    evaluator exercises no judgment and hand-computing only adds arithmetic the
    record cannot check. On those two stages the whole record is written
    unconditionally (:func:`_skill_record_for`): the ``brier_score`` recomputed
    from the scored prediction's committed ``probability`` and the outcome's
    ``actual_granted``, the ``segment_base_rate`` pooled from the statpack, and
    the ``brier_skill_score`` derived from those two — each cleared where an
    input is missing so a hand-written number never survives a refusal, and both
    halves of the basis record cleared with them, since neither pooled rate is a
    salience-band product. All three come off one set of committed artifacts, so
    the skill ratio is verifiable rather than merely self-consistent: stamping
    the denominator over an agent-written numerator would reproduce from the
    record and still be wrong. The **cert** path stays the evaluator's and none
    of the three is touched there: which band population the rate is taken over
    — ``risk_set`` against ``terminal`` — is a judgment about the scored
    prediction's frozen band, recorded in ``base_rate_basis``, and the
    leaderboard's coherence check is what holds that arithmetic to its record.

    A mispaired basis exits non-zero after every cell is stamped — either
    half. A recorded ``risk_set`` basis whose version does not resolve: the
    null is still written — it is the deterministic record of what resolution
    produced — but a basis without its version half names a population nothing
    pins down. And a recorded ``terminal`` basis while the scored prediction
    froze a ``context.band`` at all: ``terminal`` is the fallback for a
    prediction that froze no band, so against a frozen band it prices the cell
    off the wrong population — a well-formed record where the band's version
    also resolves, and a moved band priced at the terminal rate where it does
    not. The correction either way is a re-derived evaluation whose rate,
    basis, and version come off one population together — or nulling the rate,
    the basis, and the skill together and re-stamping, which clears the
    version half — never a relabel of the basis under the number as written,
    which would pair one population's version with a rate read over the
    other's table. ``validate``'s
    :func:`fedcourtsai.validate.check_base_rate_version` holds both halves
    over the committed ledger, so a failed cell reaches a maintainer through
    the run's draft PR rather than a merged one.

    **``--regrade``: this stamp minus the process attribution.** A committed
    evaluation grades a prediction against a *committed outcome*, so a
    corrected outcome leaves every evaluation that read the old one recording
    a stale ``correct``, claim block, and skill record. Every one of those
    fields is already a pure function of the committed artifacts, so a re-grade
    recomputes exactly what an ordinary stamp would — and writes it without
    ``process_version``, because the process that produced the record is
    unchanged by the correction. The alternative reading, that a re-grade
    re-stamps the resolving registry's version, is wrong on the evidence: the
    record's prose was written by the earlier process, and re-labelling it
    would attribute an older process's judgment to a newer pre-registration.
    So a re-grade requires a record that already carries a stamp — a
    never-stamped cell has no attribution to preserve and takes the ordinary
    stamp — and it refuses ``--role predictor`` (a prediction carries no graded
    field to recompute) and refuses ``--stamped-at`` / ``--pipeline-sha``,
    which set only the version it declines to write. Finding no artifact at all
    exits non-zero, unlike the ordinary stamp's no-op: a re-grade's coordinates
    are typed by hand, so a mistyped run id must not read as a correction that
    landed. It also refuses a run a newer grading supersedes (nothing reads it,
    so recomputing it would report a correction that moved no published
    number), and a cell whose evaluator-owned Brier trio no longer reproduces
    against the corrected outcome (:func:`_require_reproducible_trio`) — every
    one of them judged before the first write, so a refusal cannot leave the
    event half corrected. Each target's process scope is echoed as it goes,
    since a frozen-scope cell moving with no ``superseded_gradings`` trace is
    the one thing a reader would want recorded outside ``data/``.

    The stamp it preserves is the vintage of the **producing** invocation, and
    a re-grade deliberately re-derives the graded block against the statpack
    and salience config committed *now* — same rule as the ordinary stamp, that
    a harness field is a function of the committed artifacts as of the
    invocation. Reconstructing a stamp-vintage pool would price a corrected
    outcome against a pack that never saw the correction. So the vintage
    discipline is the operator's: re-grade a whole cohort against one committed
    statpack, never a cell at a time across a moving pack.

    Re-grade **every evaluator on the event**, not one: ``validate``'s
    :func:`fedcourtsai.validate.check_evaluation_correct_agrees` collapses to
    the latest runs and requires the evaluators to agree, so a half-re-graded
    event fails the ledger — which is the check doing its job, not an obstacle
    to route around. One divergence a re-grade cannot repair: gradings that
    straddle a re-prediction each preserve their own ``prediction_run_id``,
    so their bits stay computed against different runs through any number of
    re-grades. The remedy there is the ordinary re-stamp of the event's
    evaluations, which re-resolves the identity to the latest prediction — at
    the stated cost that it rewrites ``process_version``, attributing the
    grading to the registry in force now rather than the one that produced
    it; that trade is why the straddle should be repaired promptly, not left
    to age.
    """
    settings = get_settings()
    if role not in ("predictor", "evaluator"):
        typer.echo(f"role must be predictor or evaluator, not {role!r}", err=True)
        raise typer.Exit(code=2)
    if regrade:
        _refuse_unsupported_regrade(role, pipeline_sha, stamped_at)

    # Under --regrade neither the digest nor the stamp over it is resolved: the
    # digest *is* the process attribution being withheld, so resolving it would
    # fail a re-grade of a record whose actor the live registry no longer
    # carries — over a version this run does not write.
    digest = ""
    update: dict[str, object] = {}
    if not regrade:
        digest = process_version.digest_for_actor(Path.cwd(), settings.config_root, role, actor)
        update["process_version"] = _resolve_stamp(digest, pipeline_sha, stamped_at)

    event_paths = CasePaths(settings.data_root, court, docket).event(event)
    if role == "predictor":
        targets = [event_paths.prediction(actor, run_id)]
        model_cls: type[Prediction] | type[Evaluation] = Prediction
    else:
        # One evaluate cell scores every predictor, so it writes one
        # evaluation.json per predictor at evaluations/<actor>/<predictor>/<run>/.
        targets = sorted(
            (event_paths.base / "evaluations" / actor).glob(f"*/{run_id}/evaluation.json")
        )
        model_cls = Evaluation

    if regrade:
        _echo_frozen_scope(_refuse_unregradable(targets, event_paths, actor, run_id))

    # A predictor's conditioning is stamped from the same provisioning record the
    # agent read, for the same reason the digest is: it is a scoring input, so it
    # cannot be the agent's word. `record/` is gitignored, so `prediction.json` is
    # where it has to become durable. Absent when provisioning left nothing to
    # freeze — and the evaluator then falls back to the terminal band rather
    # than inventing one.
    if role == "predictor":
        # Assigned unconditionally, so an agent-authored block is cleared rather
        # than preserved when provisioning left nothing to freeze. A guarded
        # assignment would let a cell that ran without a provisioned record
        # supply its own baseline conditioning, which is the one thing this
        # field must not be.
        update["context"] = _read_cell_context(CasePaths(settings.data_root, court, docket))

    graded = 0
    basis_records: dict[Path, tuple[str | None, str | None, Prediction | None]] = {}
    for path in targets:
        if not path.is_file():
            continue
        record = read_model(path, model_cls)
        cell_update = dict(update)
        if isinstance(record, Evaluation):
            # The graded-prediction identity is the harness's word like every
            # stamped field: the ordinary stamp resolves it (immediately
            # post-run, when the latest prediction is the scored one) and
            # overwrites an evaluator-written value; a re-grade leaves it
            # untouched, so a predictor re-run after the grading cannot
            # re-point the record. Assigned unconditionally on the ordinary
            # path, `None` included — the one way the harness could forget an
            # identity, safe because nothing removes a prediction from the
            # append-only ledger, so a stamp that resolves nothing is a cell
            # that never had a prediction to name. Written back onto `record`
            # first, so the graded computations below judge the same
            # prediction the stamp names.
            if not regrade:
                scored = _latest_prediction_for(event_paths, record.predictor_id)
                cell_update["prediction_run_id"] = scored.run_id if scored is not None else None
                record = record.model_copy(
                    update={"prediction_run_id": cell_update["prediction_run_id"]}
                )
            # Assigned unconditionally, like `context` above: the claim block is
            # the harness's word (docs/outcome-decomposition.md), so an
            # evaluator-authored one is replaced — with the computed block where
            # the committed inputs support one, with nothing otherwise.
            cell_update["claim_scores"] = _claim_scores_for(event_paths, record, settings)
            # `correct` on every stage, and the skill record — Brier, base
            # rate, and the ratio over them — on the stages that own it: same
            # discipline, derived deterministically from the stage and the
            # committed inputs, overwritten unconditionally so what it says is
            # the harness's word. The basis trio it returns is what the
            # mispairing guard below judges — the record as stamped, never as
            # the evaluator wrote it.
            skill_fields, basis_records[path] = _skill_record_for(event_paths, record, settings)
            cell_update.update(skill_fields)
        write_json(path, record.model_copy(update=cell_update))
        graded += 1

    if graded == 0:
        _report_no_targets(regrade, role, actor)
        return
    # Echoed before the guard so a failed cell's log still says how many stamps
    # landed; the guard is judged after every cell is written, so one
    # unresolvable record does not strand the run's remaining stamps.
    typer.echo(
        f"regrade: {actor} -> {graded} file(s); process_version left as stamped"
        if regrade
        else f"stamp: {actor} {digest} -> {graded} file(s)"
    )
    _fail_on_mispaired_basis(basis_records)


def _report_no_targets(regrade: bool, role: str, actor: str) -> None:
    """Say that the invocation found nothing to write — and fail a re-grade that did.

    The ordinary stamp's silence is the fan-out's contract: a no-output cell
    has nothing to stamp and is already routed to a draft, so a missing
    artifact is that cell's failure and not this step's. A re-grade is the
    opposite shape — a hand-run correction over cells that already exist, whose
    coordinates are typed rather than handed down by the matrix — so finding
    none means the cell was named wrong, and a mistyped run id must not read as
    a correction that landed.
    """
    if regrade:
        typer.echo(
            f"::error::regrade: no {role} artifact for {actor} at this event and run id; "
            + "a re-grade recomputes cells that already exist.",
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(f"stamp: no {role} artifact for {actor} to stamp; skipping.", err=True)


def _refuse_unsupported_regrade(role: str, pipeline_sha: str, stamped_at: str) -> None:
    """Exit non-zero where ``--regrade`` was asked for something it is not.

    Two refusals, both because the flag's whole content is *withholding the
    process attribution*. A **predictor** cell carries no harness-graded field
    — its ``correct`` and skill record live on the evaluations that score it —
    so a re-grade would recompute nothing and merely skip the stamp. And
    ``--stamped-at`` / ``--pipeline-sha`` set fields of the version a re-grade
    declines to write, so taking them silently would read as re-dating a stamp
    that by design never moves.
    """
    if role == "predictor":
        typer.echo(
            "--regrade recomputes an evaluation's graded fields; a prediction has none, "
            "so a predictor cell only ever takes the ordinary stamp.",
            err=True,
        )
        raise typer.Exit(code=2)
    if stamped_at or pipeline_sha:
        typer.echo(
            "--regrade writes no process_version, so --stamped-at and --pipeline-sha "
            "have nothing to set; drop them.",
            err=True,
        )
        raise typer.Exit(code=2)


def _refuse_unregradable(
    targets: Sequence[Path], event_paths: EventPaths, actor: str, run_id: str
) -> list[tuple[Path, Evaluation]]:
    """The re-gradable targets, or exit non-zero over the first that is not.

    Every check runs **before the first write**, because each failure mode is a
    half-corrected event: a run that stopped part-way through would leave the
    event's evaluators disagreeing on ``correct``, which is the exact state
    ``validate``'s ``evaluation_correct_agrees`` fails.

    Three refusals (:func:`_require_prior_stamp`, :func:`_require_latest_run`,
    :func:`_require_reproducible_trio`), all of them cases where recomputing
    the harness fields in place would leave the ledger worse than it found it:
    a record with no stamp to preserve, a superseded run nothing reads, and a
    cell whose evaluator-owned Brier trio the correction has invalidated.
    """
    records = [(path, read_model(path, Evaluation)) for path in targets if path.is_file()]
    _require_prior_stamp(records)
    _require_latest_run(records, event_paths, actor, run_id)
    _require_reproducible_trio(records, event_paths)
    return records


def _require_prior_stamp(records: Sequence[tuple[Path, Evaluation]]) -> None:
    """Exit non-zero unless every target already carries a ``process_version``.

    A re-grade preserves the stamp of the process that produced the record, so
    an unstamped cell has nothing for it to preserve: writing the graded fields
    alone would leave a cell reading as scored under no process at all. That
    cell takes the ordinary stamp instead.
    """
    for path, record in records:
        if record.process_version is None:
            typer.echo(
                f"::error::regrade: {path} carries no process_version. A re-grade "
                + "preserves the stamp of the process that produced the record; an "
                + "unstamped cell has none, so it takes the ordinary stamp instead.",
                err=True,
            )
            raise typer.Exit(code=1)


def _require_latest_run(
    records: Sequence[tuple[Path, Evaluation]], event_paths: EventPaths, actor: str, run_id: str
) -> None:
    """Exit non-zero where a newer grading by the same evaluator supersedes this run.

    Every surface that aggregates the ledger collapses a grader's re-runs of
    one cell to the newest (:func:`fedcourtsai.integrity.latest_evaluation_runs`),
    so recomputing a superseded run moves no published number while exiting
    clean — a correction that reads as landed and is not. The message names the
    run that actually wins, since that is the one to re-grade.
    """
    committed = sorted((event_paths.base / "evaluations" / actor).glob("*/*/evaluation.json"))
    graded: list[tuple[Path, Evaluation]] = [(p, read_model(p, Evaluation)) for p in committed]
    winners = {
        record.predictor_id: record.run_id
        for _, record in latest_evaluation_runs(graded, lambda item: item[1])
    }
    for path, record in records:
        winning = winners.get(record.predictor_id)
        if winning is not None and winning != run_id:
            typer.echo(
                f"::error::regrade: {path} is not {actor}'s surviving grading of "
                + f"{record.predictor_id} on this event — run {winning} supersedes it, and "
                + "every scoring surface collapses to that one. Re-grade the surviving run.",
                err=True,
            )
            raise typer.Exit(code=1)


def _require_reproducible_trio(
    records: Sequence[tuple[Path, Evaluation]], event_paths: EventPaths
) -> None:
    """Exit non-zero where a correction has invalidated an evaluator-owned Brier trio.

    On the stages :data:`_HARNESS_SKILL_STAGES` does not cover, the Brier, the
    segment base rate, and the skill over them stay the evaluator's arithmetic
    against its own frozen band — the stamp does not recompute them, and a
    re-grade must not either. A correction that moves the outcome's
    ``actual_granted`` therefore leaves a recomputed ``correct`` and claim
    block beside a trio scored against the superseded binary, and the two then
    describe different outcomes: the leaderboard drops such a cell from
    ``skill_scored`` (its recorded skill no longer reproduces from its own
    recorded inputs) while the corrected ``correct`` stays in accuracy, so the
    two columns would run over different populations with nothing saying so.

    Refused rather than repaired, because the repair is a judgment the harness
    does not hold: which band population the rate was taken over is the
    evaluator's. The remedy is the one the mispaired-basis guard already names
    — null ``brier_score``, ``segment_base_rate``, ``base_rate_basis``, and
    ``brier_skill_score`` together, or commit a genuine re-derivation — after
    which the re-grade proceeds. A correction that leaves the binary alone (a
    disposition relabelled within the granted set, say) reproduces and passes.
    """
    if _event_stage_and_opened(event_paths)[0] in _HARNESS_SKILL_STAGES:
        return
    outcome = _outcome_for(event_paths)
    for path, record in records:
        recorded = record.brier_score
        if recorded is None:
            continue
        recomputed = _harness_brier_for(event_paths, record, outcome)
        if recomputed is None or abs(recomputed - recorded) <= _STAMP_ECHO_TOLERANCE:
            continue
        typer.echo(
            f"::error::regrade: {path} records brier_score {recorded}, which does not "
            + f"reproduce against the committed outcome ({recomputed}). The Brier, the "
            + "segment base rate, and the skill over them are the evaluator's on this "
            + "stage, so a re-grade would leave them scored against the superseded "
            + "outcome while `correct` moved. Null `brier_score`, `segment_base_rate`, "
            + "`base_rate_basis`, and `brier_skill_score` together, or commit a "
            + "re-derivation, then re-grade.",
            err=True,
        )
        raise typer.Exit(code=1)


def _echo_frozen_scope(records: Sequence[tuple[Path, Evaluation]]) -> None:
    """Name each re-graded cell's process scope, one line per target.

    A re-grade leaves no ``superseded_gradings`` trace, so a cell whose
    numbers a published claim may rest on would otherwise move with nothing
    outside ``data/``'s git history recording that it did. The line puts that
    in the writer run's log and step summary, where it is greppable after the
    fact. Scope is the evaluation-side gate the headline itself uses —
    ``graded_post_freeze``, timing alone — because an evaluation's digest is
    recorded but never enforced: a cell graded under a since-superseded
    evaluator digest is still counted, so it must still print as
    frozen-scope here. It reports the stamp the record already carries,
    which is exactly the stamp the re-grade preserves.
    """
    for path, record in records:
        stamp = record.process_version
        if stamp is None:
            continue
        scope = "frozen" if process_version.graded_post_freeze(stamp) else "alpha"
        typer.echo(f"regrade: {path} — {scope}-scope cell stamped {stamp.label}")


def _resolve_stamp(digest: str, pipeline_sha: str, stamped_at: str) -> ProcessVersion:
    """The ``ProcessVersion`` an ordinary stamp writes, over its resolved digest.

    Exits non-zero rather than writing an unparseable or offset-less
    ``--stamped-at``, for the reason below.
    """
    if stamped_at:
        # The stamp is the frozen/alpha partition's time key; a naive value
        # has no defined order against the freeze instant and reads as
        # pre-freeze, so refuse to write one rather than stamp a cell out of
        # the headline by formatting accident.
        try:
            stamp_moment = datetime.fromisoformat(stamped_at)
        except ValueError:
            typer.echo(f"--stamped-at is not an ISO timestamp: {stamped_at!r}", err=True)
            raise typer.Exit(code=2) from None
        if stamp_moment.tzinfo is None:
            typer.echo("--stamped-at must carry a UTC offset (e.g. ...T12:00:00+00:00)", err=True)
            raise typer.Exit(code=2)
    else:
        stamp_moment = datetime.now(UTC)
    return ProcessVersion(
        label=process_version.CURRENT_PROCESS_LABEL,
        digest=digest,
        pipeline_sha=resolve_pipeline_sha(pipeline_sha),
        stamped_at=stamp_moment,
    )


def _fail_on_mispaired_basis(
    basis_records: Mapping[Path, tuple[str | None, str | None, Prediction | None]],
) -> None:
    """Exit non-zero where a stamped basis contradicts the scored prediction.

    Takes each stamped evaluation's ``(base_rate_basis,
    base_rate_salience_version, scored prediction)`` as written. Two
    mispairings, both fatal because a skill score is only comparable within a
    correctly recorded basis (``metrics/README.md``):

    - ``risk_set`` with no resolvable version — the join found no prediction,
      no frozen context, or no ``salience_version`` in it. The null version is
      still written (the deterministic record of what resolution produced);
      this guard is what stops the cell passing as scored.
    - ``terminal`` while the scored prediction froze a ``band`` at all —
      ``terminal`` is the fallback for a prediction that froze no band
      (``docs/salience.md``), so taking it against a frozen band prices the
      cell off the wrong population: a well-formed number where the band's
      version also resolves, a moved band priced at the terminal rate where
      it does not.

    One ``::error::`` per offender, so a maintainer reading the run log sees
    every cell at once, and each names the valid corrections for its own
    shape — never a basis relabel under the number as written, which would
    stamp a truthful-looking version onto a rate read over the other table.

    The two arms differ off the cert stage: the risk-set arm judges the
    record's own two halves and fires on any stage that reaches it, while the
    terminal arm needs the scored prediction, which the caller supplies only
    on a cert cell — the frozen-band pairing is a cert-petition concept, and
    the context is stamped per case, so on a stage-less event a case-level
    band must not reach a rule about cert populations.
    """
    failed = False
    for path, (basis, stamped_version, scored) in sorted(basis_records.items()):
        context = scored.context if scored is not None else None
        if basis == "risk_set" and stamped_version is None:
            failed = True
            typer.echo(
                f"::error::stamp: {path} records base_rate_basis 'risk_set' but no salience "
                + "version resolves — the join found no prediction for this predictor, no "
                + "frozen context on its latest one, or no `salience_version` in that "
                + "context. A risk-set base rate is banded under the scored prediction's "
                + "frozen `context.salience_version`, so a basis recorded without one names "
                + "a population nothing pins down. Where the join simply missed, a "
                + "corrected evaluation may take the terminal basis (the documented "
                + "fallback); where the scored prediction froze a band with no version "
                + "beside it, the terminal basis is wrong too — null `segment_base_rate`, "
                + "`base_rate_basis`, and `brier_skill_score` together and re-stamp, never "
                + "relabel the basis under the number as written.",
                err=True,
            )
        elif basis == "terminal" and context is not None and context.band is not None:
            failed = True
            # Narrowing only: `context` was read off `scored`, so a non-null
            # context implies the prediction it came from.
            assert scored is not None
            if context.salience_version is not None:
                detail = (
                    "carries a frozen `context.band` and `context.salience_version` — the "
                    + "fallback taken where the risk-set pairing was available, a "
                    + "well-formed rate read against the wrong population. Correct with a "
                    + "re-derived evaluation whose rate, basis, and version come off the "
                    + "risk-set population together, or null `segment_base_rate`, "
                    + "`base_rate_basis`, and `brier_skill_score` together and re-stamp; "
                    + "never relabel the basis under the number as written, which pairs "
                    + "one population's version with a rate read over the other's table."
                )
            else:
                detail = (
                    "froze a `context.band` with no salience version beside it — a frozen "
                    + "band priced at the terminal rate, where omission is the only "
                    + "answer: null `segment_base_rate`, `base_rate_basis`, and "
                    + "`brier_skill_score` together and re-stamp."
                )
            typer.echo(
                f"::error::stamp: {path} records base_rate_basis 'terminal' while the "
                + f"scored prediction (run {scored.run_id}) "
                + detail,
                err=True,
            )
    if failed:
        raise typer.Exit(code=1)


def _base_rate_salience_version_for(
    evaluation: Evaluation, context: PredictionContext | None
) -> str | None:
    """Which salience version the evaluation's segment base rate was read under.

    Deterministic from the same inputs ``base_rate_basis`` names, so the stamp
    records — never trusts — the evaluator: on the ``risk_set`` path the band
    was the scored prediction's frozen one, so the version is the passed
    ``context``'s ``salience_version`` — the caller resolves that context via
    the latest-prediction join every scoring surface uses; on the ``terminal``
    path the band was
    re-derived from the row under the live scorer, so the version is the live
    ``SALIENCE_VERSION``. ``None`` where the evaluation records no basis (no
    segment base rate was taken), or where the risk-set path's prediction or
    frozen context cannot be resolved — a gap recorded as absence, never
    guessed.
    """
    if evaluation.base_rate_basis == "terminal":
        return SALIENCE_VERSION
    if evaluation.base_rate_basis != "risk_set":
        return None
    return context.salience_version if context is not None else None


def _claim_scores_for(
    event_paths: EventPaths, evaluation: Evaluation, settings: Settings
) -> ClaimScoreBlock | None:
    """The harness-computed claim block for one evaluation, or ``None``.

    The join rule matches the leaderboard's: the scored prediction is the
    predictor's **latest** for this event (an evaluation records its predictor,
    not a prediction run id). Tolerant like the context stamp, because this
    runs as a post-agent step: a missing outcome, statpack, or prediction is a
    recorded gap — the stamp then clears the field rather than failing a cell
    that already produced its output. (One exception rides up from
    :func:`~fedcourtsai.pipeline.claims.score_claims`: a frozen
    ``salience_version`` missing from the scorer registry raises, since that
    record is corrupt rather than incomplete.) The lookback is the same
    ``salience.base_rate_lookback_terms`` the headline segment baseline uses,
    so the block and the skill score answer to one window.

    The **grant Term** is read here rather than derived from the prediction:
    the merits event's ``opened_at`` *is* the cert-grant date, and the merits
    baseline is keyed on the Term of the grant (the statpack merits section's
    own axis), which the frozen context's docket-number Term does not reliably
    equal. Absent or unreadable, it stays ``None`` and the merits claim goes
    unscored rather than anchoring to the wrong Term.
    """
    outcome = _outcome_for(event_paths)
    statpack = _statpack_for(settings)
    latest = _scored_prediction_for(event_paths, evaluation)
    if outcome is None or statpack is None or latest is None:
        return None
    return score_claims(
        latest,
        outcome,
        statpack,
        lookback_terms=load_salience_config(settings.config_root).base_rate_lookback_terms,
        grant_term=_grant_term_for(event_paths),
    )


def _scored_prediction_for(event_paths: EventPaths, evaluation: Evaluation) -> Prediction | None:
    """The prediction this evaluation grades, or ``None``.

    :func:`fedcourtsai.store.scored_prediction` over the cell's own record —
    the join every stamp-time computation uses, and the same resolver the
    stratified boards and the ``validate`` gates read, so no two enforcers of
    one rule can score different predictions. A stamped ``prediction_run_id``
    names the graded run outright (a ``None`` covers both a record predating
    the field and a stamp that resolved no prediction at all — the second is
    loud elsewhere, since ``correct`` stamps null beside it); the fallback is
    the predictor's latest prediction, the historical rule the stamp exists
    to retire.
    """
    return scored_prediction(
        event_paths.base, evaluation.predictor_id, evaluation.prediction_run_id
    )


def _latest_prediction_for(event_paths: EventPaths, predictor_id: str) -> Prediction | None:
    """A predictor's **latest** prediction on this event, or ``None``.

    By :func:`fedcourtsai.integrity.cell_clock`; ``None`` where the predictor
    wrote none. The fallback join for evaluations with no stamped
    ``prediction_run_id``, and the resolver the ordinary stamp reads that run
    id from — at stamp time, immediately post-run, the latest prediction *is*
    the scored one.
    """
    files = sorted(event_paths.predictions_dir.glob(f"{predictor_id}/*/prediction.json"))
    predictions = [read_model(p, Prediction) for p in files]
    return max(predictions, key=cell_clock) if predictions else None


def _outcome_for(event_paths: EventPaths) -> Outcome | None:
    """The event's committed ``outcome.json``, or ``None`` where none exists yet."""
    return read_model(event_paths.outcome, Outcome) if event_paths.outcome.is_file() else None


def _statpack_for(settings: Settings) -> StatPack | None:
    """The committed statpack, or ``None`` where none is readable.

    Tolerant like the rest of the stamp's inputs: this runs as a post-agent
    step, so an absent or unreadable pack is a recorded gap in whatever it
    feeds — never a failed cell whose output already exists.
    """
    return _read_best_effort(settings.metrics_root / "statpack.json", StatPack)


#: The stages whose whole skill record — ``brier_score``, ``segment_base_rate``,
#: and the ``brier_skill_score`` over them — the harness stamps rather than the
#: evaluator recording it: both pool a Term-keyed ratio of the statpack's
#: published integer counts, with no salience band to choose between and so no
#: judgment for an evaluator to exercise. The cert stage is absent by design —
#: see :func:`stamp_cell`. It governs the *skill record* only: ``correct`` needs
#: no pooled rate and so no band, and is stamped on every stage including cert.
_HARNESS_SKILL_STAGES = (Stage.merits, Stage.interim)


def _skill_record_for(
    event_paths: EventPaths, evaluation: Evaluation, settings: Settings
) -> tuple[dict[str, object], tuple[str | None, str | None, Prediction | None]]:
    """This cell's ``correct`` and skill record as a stamp update, plus its basis trio.

    ``correct`` is stamped on **every** stage, cert included, and is the one
    field here that does not split by stage. The exemption the cert stage holds
    is about the *baseline*: which band population a pooled rate is taken over
    is a judgment about the scored prediction's frozen band, and that judgment
    reaches the Brier skill through ``segment_base_rate``. ``correct`` has no
    baseline and no band — it is a label comparison between the scored
    prediction and the outcome (:func:`fedcourtsai.pipeline.evaluate.is_correct`,
    routed on the outcome's own axis) — so there is nothing on a cert cell for
    an evaluator to exercise judgment over, and no reason for the exemption to
    carry across. It is also the leaderboard's first rank key, so leaving it as
    the evaluator's word on the one stage the ranked board is built from would
    leave the board's lead column unverifiable exactly where it is load-bearing.
    Like the Brier it is ``None`` where either committed artifact — the scored
    predictor's latest prediction, or the outcome — is unreadable.

    The **skill record** beside it takes two shapes, keyed on the stage. On a
    **cert** cell the Brier, the rate, and
    the skill are the evaluator's — which band population the rate was taken
    over is a judgment about the scored prediction's frozen band, and the
    leaderboard's coherence check is what stands between that arithmetic and the
    published column — so only the version half of the basis record is derived
    here (:func:`_base_rate_salience_version_for`), exactly as ``claim_scores``
    is: deterministically, and overwriting whatever the evaluator wrote.

    On a stage of :data:`_HARNESS_SKILL_STAGES` the **whole** record is the
    harness's, and all five fields are assigned unconditionally. The Brier, the
    rate, and the skill over them are computed (:func:`_harness_brier_for`,
    :func:`_harness_base_rate_for`, :func:`_harness_skill_for`) and are ``None``
    where an input is missing — an evaluator-authored number surviving that
    refusal is the one thing stamping them exists to prevent. All three come off
    one set of committed inputs, which is what makes the ratio verifiable rather
    than merely internally consistent: a stamped skill whose numerator was the
    evaluator's word would reproduce from the record and still be wrong.

    Both halves of the **basis record** are cleared, because neither pooled rate
    is a salience-band product: there is no band population for a basis to name,
    and a recorded one would otherwise pull a salience version onto a rate no
    band ever produced — or fail the cell on the mispairing guard, whose remedy
    (the terminal basis) means nothing on a stage the harness pools itself.

    The returned ``(basis, version, scored prediction)`` trio is the record
    **as stamped** plus the prediction it scores, so the guard judges what was
    written rather than what the evaluator proposed — and can judge the
    terminal half of the mispairing, which is visible only against the frozen
    context the fallback declined to use. The prediction rides only on a
    **cert** cell: the frozen-band pairing is a cert-petition concept, so on a
    stage-less event a case-level frozen band must not reach the guard.
    """
    outcome = _outcome_for(event_paths)
    correct = _harness_correct_for(event_paths, evaluation, outcome)
    # The one field the evaluate prompt requires of every cell, so a null is a
    # contract miss rather than a stage's silence — and it costs the stamped
    # bit its only independent read, which is worth as much noise as a
    # disagreement.
    _warn_on_discarded_number(
        evaluation, "correct", evaluation.correct, correct, warn_on_omission=True
    )
    stage = _event_stage_and_opened(event_paths)[0]
    if stage not in _HARNESS_SKILL_STAGES:
        latest = _scored_prediction_for(event_paths, evaluation)
        context = latest.context if latest is not None else None
        version = _base_rate_salience_version_for(evaluation, context)
        return (
            {"correct": correct, "base_rate_salience_version": version},
            (evaluation.base_rate_basis, version, latest if stage == Stage.cert else None),
        )
    rate = _harness_base_rate_for(event_paths, evaluation, settings)
    brier = _harness_brier_for(event_paths, evaluation, outcome)
    _warn_on_discarded_number(evaluation, "brier_score", evaluation.brier_score, brier)
    _warn_on_discarded_number(evaluation, "segment_base_rate", evaluation.segment_base_rate, rate)
    return (
        {
            "correct": correct,
            "brier_score": brier,
            "segment_base_rate": rate,
            "brier_skill_score": _harness_skill_for(brier, outcome, rate),
            "base_rate_basis": None,
            "base_rate_salience_version": None,
        },
        (None, None, None),
    )


#: How far a recorded number may sit from the stamped one before
#: :func:`_warn_on_discarded_number` says so. Committed records carry three
#: decimals and both sides compute from the same committed inputs, so an
#: agreeing pair lands inside this; a wider gap is a different computation — a
#: different pool window or Term axis for the rate, a different probability or
#: binary for the Brier. Absolute rather than relative, so it is a floor on what
#: gets *said*, not on what gets written: a disagreeing Brier under it — which a
#: squared quantity reaches near ``p == y`` — is still replaced, silently. A
#: 0/1 field like ``correct`` can only disagree by a whole unit, so every
#: disagreement there is said.
_STAMP_ECHO_TOLERANCE = 1e-3


def _warn_on_discarded_number(
    evaluation: Evaluation,
    field: str,
    recorded: float | None,
    stamped: float | None,
    *,
    warn_on_omission: bool = False,
) -> None:
    """Say when a stamped number replaces a *different* one the evaluator wrote.

    The stamp overwrites either way — that is the point — but an overwrite that
    changes the number is the one thing a maintainer would want to see, and a
    silent one leaves no trace that the evaluator's own arithmetic disagreed
    (or that the harness declined a number the evaluator was willing to state).
    One ``::warning::``, never a failure: the harness's number is not in doubt,
    and a cell that produced its output must not fail on a note about it.

    It is also why the evaluate prompt goes on eliciting a number the stamp
    discards. An elicited value the harness overwrites is not waste: it is the
    only independent read of the same quantity anywhere in the run, so a
    systematic disagreement — an evaluator scoring the wrong binary, or reading
    a stale probability — surfaces here and nowhere else. A field the prompt
    stopped asking for would leave that check with nothing to compare.

    ``warn_on_omission`` extends that to the other direction: an evaluator that
    simply *omits* the elicited value kills the independent read as effectively
    as a wrong one, and silently, since there is then no disagreement to
    report. It is off by default because on an optional field an omission is
    the normal shape — most cells legitimately record no Brier or no rate — and
    on by exception for a field the prompt requires of every cell, where a null
    is a prompt-contract miss rather than a stage's silence.

    "Harness-stamped" in the note is said of the **field**, not the stage: on a
    cert cell ``correct`` is stamped while the skill record beside it is not, so
    naming the stage would misdescribe exactly the cell this most often fires on.
    """
    if recorded is None:
        if not (warn_on_omission and stamped is not None):
            return
    elif stamped is not None and abs(stamped - recorded) <= _STAMP_ECHO_TOLERANCE:
        return
    said = f"recorded no {field}" if recorded is None else f"recorded {field} {recorded}"
    typer.echo(
        f"::warning::stamp: {evaluation.evaluator_id}/{evaluation.predictor_id} {said} "
        + f"for a harness-stamped field; the stamp wrote {stamped}.",
        err=True,
    )


def _harness_correct_for(
    event_paths: EventPaths, evaluation: Evaluation, outcome: Outcome | None
) -> int | None:
    """The harness's own correctness bit for one evaluation, or ``None``.

    The stage's own label comparison between the two committed artifacts,
    through the shared numeric core
    (:func:`fedcourtsai.pipeline.evaluate.is_correct`, which routes on the
    outcome: judgment on a merits cell, disposition elsewhere), so the stamped
    bit is the definition rather than a restatement of it. The scored prediction
    is the predictor's **latest** for this event, the same join the Brier and
    the claim block take.

    Stamped on every stage, cert included — it needs no pooled baseline and so
    no band judgment, which is the whole of the cert stage's skill-record
    exemption. ``None`` only where an artifact is absent outright, exactly
    :func:`_harness_brier_for`'s tolerance: this is a post-agent step, so a
    missing input suppresses the bit rather than failing a cell that already
    produced its output.
    """
    latest = _scored_prediction_for(event_paths, evaluation)
    if latest is None or outcome is None:
        return None
    return is_correct(latest, outcome)


def _harness_brier_for(
    event_paths: EventPaths, evaluation: Evaluation, outcome: Outcome | None
) -> float | None:
    """The harness's own Brier score for one evaluation, or ``None``.

    ``(probability - actual_granted)**2`` over the two committed artifacts,
    through the same numeric core every scoring surface uses
    (:func:`fedcourtsai.pipeline.evaluate.brier_score`), so the stamped
    numerator is the definition rather than a restatement of it. The scored
    prediction is the predictor's **latest** for this event — the join
    ``claim_scores`` and the base rate already use, since an evaluation records
    its predictor and not a prediction run id.

    Neither input can be partly there: ``Prediction.probability`` and
    ``Outcome.actual_granted`` are both schema-required, so a readable artifact
    always carries its half of the formula. ``None`` only where an artifact is
    absent outright — no prediction from this predictor, or no committed
    outcome — which is the same tolerant clearing the rate takes: this runs as
    a post-agent step, so a missing input suppresses the number rather than
    failing a cell that already produced its output.
    """
    latest = _scored_prediction_for(event_paths, evaluation)
    if latest is None or outcome is None:
        return None
    return brier_score(latest, outcome)


def _harness_base_rate_for(
    event_paths: EventPaths, evaluation: Evaluation, settings: Settings
) -> float | None:
    """The harness's own segment base rate for one evaluation, or ``None``.

    Computed on the two stages of :data:`_HARNESS_SKILL_STAGES`, from the
    committed statpack under the same ``salience.base_rate_lookback_terms``
    window every other pooled baseline answers to. **Merits**: the disturbed
    rate over grant Terms strictly before the cell's, keyed on the Term
    :func:`_grant_term_for` resolves — the first merits moment's ``opened_at``,
    which is the cert grant, so a later moment cannot pool a Term the grant did
    not fall in. **Interim**: the substantive grant rate over application Terms
    strictly before the cell's, read off the scored prediction's **frozen**
    ``context.term`` (the application Term the cell was conditioned on) rather
    than re-derived at stamp time. A **cert** cell returns ``None``: there the
    rate is a band product, and which population it is taken over — the
    risk-set table against the terminal one — is a judgment about the scored
    prediction's frozen band, which the evaluator makes and records.

    ``None`` too wherever an input is missing: no readable statpack, no Term to
    key on, no prediction to read a frozen one off, or a pool below its own
    registered floor. The stamp then clears the field rather than leaving a
    number the harness cannot stand behind.
    """
    stage = _event_stage_and_opened(event_paths)[0]
    if stage not in _HARNESS_SKILL_STAGES:
        return None
    statpack = _statpack_for(settings)
    if statpack is None:
        # Said out loud, for the reason the leaderboard says it: a suppressed
        # baseline and a cell that never had one look identical in the record,
        # and this one is an input failure a maintainer can fix.
        typer.echo(
            "::warning::stamp: no readable metrics/statpack.json — this cell's "
            "segment base rate and skill are cleared rather than pooled.",
            err=True,
        )
        return None
    lookback = load_salience_config(settings.config_root).base_rate_lookback_terms
    if stage == Stage.merits:
        grant_term = _grant_term_for(event_paths)
        if grant_term is None:
            return None
        return merits_base_rate(grant_term, statpack, lookback_terms=lookback)
    latest = _scored_prediction_for(event_paths, evaluation)
    if latest is None or latest.context is None or latest.context.term is None:
        return None
    return interim_base_rate(latest.context.term, statpack, lookback_terms=lookback)


def _harness_skill_for(
    brier: float | None, outcome: Outcome | None, base_rate: float | None
) -> float | None:
    """The Brier skill of a stamped base rate against the *stamped* Brier.

    Written wherever the harness stamps the pair, through the same numeric core
    the evaluate path and the cert back-test share
    (:func:`fedcourtsai.pipeline.evaluate.brier_skill`). Both arguments are the
    harness's own numbers rather than the record's, so the ratio is correct by
    construction end to end: nothing the evaluator wrote reaches the numerator
    or the denominator. ``None`` when any input is missing — no stamped Brier,
    no stamped rate, no committed outcome to score against — and where the
    baseline is already exact, the ratio's undefined case. (The outcome guard is
    redundant against the Brier's, which is ``None`` whenever the outcome is;
    it is kept because it is what makes ``actual_granted`` reachable, and
    because the two would have to be un-coupled by hand to make it wrong.)
    """
    if brier is None or base_rate is None or outcome is None:
        return None
    return brier_skill(brier, outcome.actual_granted, base_rate)


def _grant_term_for(event_paths: EventPaths) -> int | None:
    """The October Term this event's cert **grant** fell in, or ``None``.

    The merits baseline pools strictly-prior grant Terms, so this must be the
    Term of the grant — never of the moment. The first merits moment opens on
    the grant date, so its own ``event.yaml`` is the record; a **later** merits
    moment opens on its own filing (a respondent's merits brief lands a median
    ~80 days after the grant), which routinely falls in the next October Term.
    Reading that as the grant Term would pool the case against a cohort it does
    not belong to — including, at the boundary, its own.

    So a later moment reads its sibling first-moment definition instead.
    ``None`` for any event that is not a dated merits moment, and for a later
    moment whose sibling is missing — suppressing the baseline rather than
    guessing a Term.
    """
    stage, opened_at = _event_stage_and_opened(event_paths)
    if stage != Stage.merits:
        return None
    spec = moments.spec_for(event_paths.base.name)
    if spec is not None and spec.ordinal > 0:
        first = moments.moments_for(Stage.merits)[0]
        _, opened_at = _event_stage_and_opened(event_paths.sibling(first.event_id))
    return grant_term_year(opened_at) if opened_at is not None else None


def _event_stage_and_opened(event_paths: EventPaths) -> tuple[Stage | None, date | None]:
    """The committed event definition's stage and opening date, best-effort.

    ``(None, None)`` where no ``event.yaml`` exists or it does not parse: the
    stamp runs after an agent has already produced output, so an unreadable
    definition suppresses whatever it keys — the merits grant Term, and the
    harness-stamped skill record, which is not merely emptied but not stamped
    at all, since an unnamed stage takes the cert branch and leaves what the
    evaluator wrote — rather than failing the cell.

    The stage comes back as the enum's **value** (the schema models are built
    with ``use_enum_values``), so compare it with ``==`` or ``in`` and never
    with ``is``: the string equals its member but is not it.
    """
    event_file = event_paths.event_file
    if not event_file.is_file():
        return (None, None)
    try:
        event = read_model(event_file, PredictableEvent)
    except (OSError, ValueError, ValidationError):
        return (None, None)
    return (event.stage, event.opened_at)


@app.command("process-digest")
def process_digest_cmd(
    role: Annotated[str, typer.Option(help="predictor | evaluator (ignored with --all).")] = "",
    actor: Annotated[str, typer.Option(help="Actor id (ignored with --all).")] = "",
    all_actors: Annotated[
        bool, typer.Option("--all", help="Print the digest of every enabled actor.")
    ] = False,
) -> None:
    """Print an actor's process digest — the value a maintainer blesses to freeze.

    The freeze procedure: run ``fedcourts process-digest --all``, paste the
    blessed digest(s) into ``FROZEN_PROCESS_DIGESTS`` in ``process_version.py``
    **and set ``FROZEN_SINCE`` beside it** (the two move together — a test
    pins it) in one small freeze commit, and record that commit as the cutover
    in the docs. Each digest's value there is its **bless moment**, the
    carrying promotion's merge time, written once that promotion lands; it is
    the retroactivity boundary, separate from the counting instant. Because
    the digest excludes the pipeline commit, the blessed map survives
    unrelated pipeline changes — predict/evaluate can resume at a newer HEAD
    and still match.
    """
    settings = get_settings()
    if all_actors:
        predictors = enabled_predictors(settings.config_root / "predictors.yaml")
        evaluators = enabled_evaluators(settings.config_root / "evaluators.yaml")
        rows = [("predictor", p.id) for p in predictors]
        rows += [("evaluator", e.id) for e in evaluators]
    else:
        if role not in ("predictor", "evaluator") or not actor:
            typer.echo("pass --all, or both --role and --actor.", err=True)
            raise typer.Exit(code=2)
        rows = [(role, actor)]
    for actor_role, actor_id in rows:
        digest = process_version.digest_for_actor(
            Path.cwd(), settings.config_root, actor_role, actor_id
        )
        typer.echo(f"{process_version.CURRENT_PROCESS_LABEL}  {actor_role}  {actor_id}  {digest}")


@app.command("record-retrieval")
def record_retrieval(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to inputs
    *,
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="Event id this run predicted/scored.")],
    run_id: Annotated[str, typer.Option(help="The fan-out run id (a UTC timestamp).")],
    # Typed as the enums, so typer renders the choice list into the metavar
    # itself; restating it in the help would be a second copy to drift.
    engine: Annotated[Engine, typer.Option(help="Engine that ran.")],
    role: Annotated[UsageRole, typer.Option(help="Which agentic stage this cell was.")],
    actor: Annotated[str, typer.Option(help="The predictor_id or evaluator_id for this cell.")],
    mode: Annotated[
        str, typer.Option(help="The cell's provisioned mode: forward | replay ('' = unknown).")
    ] = "",
    mode_from_context: Annotated[
        bool,
        typer.Option(
            "--mode-from-context",
            help="Read the mode from the cell's provisioned record/context.json "
            "— the record provisioning wrote — overriding --mode when the "
            "context exists and carries a known mode. --mode (or unknown) is "
            "the fallback, so an unprovisioned cell keeps the caller's word "
            "and a context carrying an out-of-vocabulary mode is refused with "
            "a warning rather than passed to the grader: the file sits in the "
            "agent's workspace, so its value is trusted only inside the "
            "declared vocabulary.",
        ),
    ] = False,
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
    pipeline-attribution record — as both the server pins and the tool names
    they advertise, so a later offered-vs-called rollup has a denominator rather
    than only the numerator. A cell with zero tool calls still records an
    empty log: "retrieved nothing" is itself evidence.
    """
    settings = get_settings()
    if mode_from_context:
        context = _read_cell_context(CasePaths(settings.data_root, court, docket))
        if context is not None:
            if context.mode in CELL_MODES:
                mode = context.mode
            else:
                # The context file lives in the agent's workspace; an
                # out-of-vocabulary mode is not a value to hand the grader.
                typer.echo(
                    f"::warning::record-retrieval: provisioned context carries an "
                    f"unknown mode {context.mode!r}; keeping the caller's "
                    f"({mode or 'unknown'})",
                    err=True,
                )
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
    offered: list[str] = []
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
            offered = mcp.manifest_tools(servers)
    except (OSError, KeyError):
        # Attribution is best-effort here: a registry drift must not lose the
        # harvested calls (the plan already validated the registry).
        labels = []
        offered = []

    record = RetrievalLog(
        case_id=ids.case_id(court, docket),
        run_id=run_id,
        role=role,
        actor_id=actor,
        engine=engine,
        mode=mode or None,
        mcp_servers=labels,
        mcp_tools=offered,
        calls=calls,
    )
    event_paths = CasePaths(settings.data_root, court, docket).event(event)
    destination = (
        event_paths.prediction_retrieval_log(actor, run_id)
        if role == UsageRole.predictor
        else event_paths.evaluation_retrieval_log(actor, run_id)
    )
    write_json(destination, record)
    # Redaction is a rewrite, not a gate: it lets a run through that the collect
    # scan would have withheld, so the fact that it fired has to be visible
    # somewhere or the signal is simply gone. Advisory — an agent can type the
    # marker itself — but a non-zero count is a maintainer's cue to look at the
    # cell's engine transcript while the run's artifacts still exist.
    redacted = sum(1 for call in calls if retrieval.carries_redaction(call))
    typer.echo(f"retrieval: {actor} {len(calls)} call(s), {redacted} redacted -> {destination}")
    if redacted:
        typer.echo(
            f"::warning::retrieval capture redacted credential-shaped text in {redacted} "
            f"call(s) for {actor} ({ids.case_id(court, docket)} {event})"
        )


@app.command("codex-item-shapes")
def codex_item_shapes(
    *,
    sessions_dir: Annotated[
        Path, typer.Option(help="Codex sessions dir (CODEX_HOME/sessions) to distill.")
    ],
    out: Annotated[Path, typer.Option(help="Where to write the distillation JSON.")],
) -> None:
    """Distill a Codex rollout tree into its item shapes — types and keys only.

    The observation half of ``record-retrieval``'s Codex path: that parser
    keys on the rollout's item types and field spellings, so a shape it does
    not recognize costs the cell's whole retrieval log while looking exactly
    like a cell that called nothing. This writes the transcript's distinct
    item shapes — the record envelope, the payload's type, and its key names
    with every value replaced by its JSON type name — so a real run can settle
    which of the two an empty log was, and pin the shapes a fixture must
    carry.

    No **value** crosses into the output: a rollout holds retrieved documents
    and tool arguments verbatim, and only key names, type discriminators, and
    JSON type names are emitted. The residual is stated rather than claimed
    away — a key name is emitted verbatim where it is identifier-shaped, so an
    object keyed by data can export a fragment of up to 64 characters (see
    :func:`~fedcourtsai.retrieval.distill_codex_shapes`). Retained shapes are
    capped, with the truncation marked in the output, so a transcript cannot
    choose the artifact's size. Tolerant like the
    capture steps it observes — a missing sessions dir distills to zero files
    rather than failing, because instrumentation must never take a run down.
    """
    distillation = retrieval.distill_codex_shapes(sessions_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(distillation, indent=2, sort_keys=True) + "\n")
    truncation = (
        f", {distillation['shapes_dropped']} record(s) past the shape cap"
        if distillation["truncated"]
        else ""
    )
    typer.echo(
        f"codex item shapes: {distillation['files']} file(s), "
        f"{distillation['records']} record(s), "
        f"{len(distillation['shapes'])} distinct shape(s){truncation} -> {out}"
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
    *,
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
    all_versions: Annotated[
        bool,
        typer.Option(
            "--all-versions",
            help="Score every process version, not only the frozen headline — "
            "matches the leaderboard's flag so the two surfaces agree.",
        ),
    ] = False,
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
    scope: Literal["frozen", "all"] = "all" if all_versions else "frozen"
    # Same shared producer + default as the leaderboard, so the two surfaces
    # always agree on the frozen headline. The census (ledger_cell_counts) stays
    # version-blind — it counts committed predictions, not scored cells. The
    # stage the join also carries is dropped here: the substance funnel is
    # deliberately stage-blind throughput (a census over every scored cell,
    # like the prediction counts beside it), so its counts pool stages by
    # design; per-stage segmentation — and every claim that must not pool —
    # is the leaderboard's job.
    stratified_run = stratify(settings.data_root, frozen_only=not all_versions)
    _report_forward_claim_exclusions(stratified_run.excluded)
    stratified = [(ev, stratum) for ev, stratum, _stage, _moment in stratified_run.cells]
    substance = summarize_substance(
        cell_counts=ledger_cell_counts(settings.data_root),
        stratified_evaluations=stratified,
        statpack=statpack,
        live_frontier=frontier,
        previous=prior,
        process_scope=scope,
        forward_claim=_forward_claim_from(stratified_run),
    )
    report = build_ops_report(
        generated_at=when,
        runs=run_rows,
        usage=iter_usage(settings.data_root),
        flags=iter_flags(settings.data_root),
        tooling=iter_tooling(settings.data_root),
        # Leakage grading is an all-versions diagnostic, like flags/tooling above
        # (which read the ledger directly): shakedown contamination is exactly
        # what it must surface, so it must NOT ride the frozen `stratified` stream
        # — that would blank the leakage digest during the shakedown window.
        evaluations=iter_evaluations(settings.data_root),
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
        str,
        typer.Option(help=f"Which client format to emit: {' | '.join(e.value for e in Engine)}."),
    ],
    role: Annotated[
        str,
        typer.Option(help=f"Registry to read: {' | '.join(r.value for r in UsageRole)}."),
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
        str,
        typer.Option(help=f"Registry to read: {' | '.join(r.value for r in UsageRole)}."),
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


# The cell modes `record/context.json` carries. One definition, so the option
# help, the validation below, and the replay provisioner cannot disagree.
CELL_MODES: tuple[str, ...] = ("forward", "replay")


CorpusBackendOption = Annotated[
    str,
    typer.Option(
        "--corpus-backend",
        help="Corpus read backend, one of "
        + " / ".join(get_args(CorpusBackend))
        + ": local reads the pulled file, ranged queries the blob in place on the "
        "corpus remote; query/open-events also accept service (forward to a corpus "
        "query sidecar — see corpus-serve), and the provisioning commands accept "
        "casestore (read the per-case content objects). Default: the "
        "corpus-backend setting from the environment.",
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

    Scope: **ranged index reads only.** Content-store transfer is not counted here
    — most importantly the per-row opinion bodies `query --full` hydrates under the
    corpus-split mode, which are the largest objects the system moves. So this line
    is a floor on a `--full` query's egress, not its total.
    """
    if isinstance(conn, corpus_ranged.RangedConnection):
        stats = conn.stats
        typer.echo(
            f"ranged corpus reads: {stats.gets} GET(s), {stats.bytes_fetched} byte(s)",
            err=True,
        )


def _echo_text_coverage(coverage: TextCoverage) -> None:
    """Print one text-coverage measurement, self-limiting on what it could read.

    Every line carries its own denominator, for the reason the censuses print
    theirs: a pass that reached one case in a hundred and one that reached all
    of them otherwise announce themselves identically. The source line leads,
    ahead of any count, because the lines below it assert *absence* — how many
    documents carry no text, how many cases hold no petition — and under the
    corpus split a store-blind run finds nothing at all. An assertion of
    absence must not be read before the thing that says whether the reader
    could have seen presence.

    Note what the empty share is *not*: a case whose petition row is absent
    entirely never enters it, which is why the missing-document population gets
    its own line rather than being left to a reader to notice.
    """
    if coverage.offloaded:
        typer.echo("text source: the per-case content store")
    else:
        typer.echo(
            "text source: this blob's own tables — under the corpus split the "
            "document text lives in the per-case content store, which this run is "
            "not configured to read, so every count below is the blob's own and "
            "undercounts the system"
        )
    # The petition alone leads the counts, never a total over the kinds: they do
    # not share a cause of emptiness, so a pooled headline would be the number
    # quoted and the one that means least. The other kinds are the table below.
    petitions, empty = coverage.kind_totals(KIND_PETITION)
    share = f"{100 * empty / petitions:.2f}%" if petitions else "-"
    scanned = empty - coverage.unopened_petitions
    typer.echo(
        f"text coverage: {empty} of {petitions} stored petition(s) carry no text "
        f"({share}) — {scanned} with pages but no text layer, "
        f"{coverage.unopened_petitions} a PDF the extractor could not open at all"
    )
    # The other failure mode, printed beside the first because it is the larger
    # one and nothing re-extracts what was never stored. Two denominators: the
    # stock of distributed rows (many predating the document channel, so never
    # fetched for), and the rows actually queued for prediction, which is the
    # population a missing petition costs a cell on.
    typer.echo(
        f"missing documents: {coverage.distributed_without_petition} of "
        f"{coverage.distributed} distributed case(s) hold no petition row at all, "
        f"and {coverage.queued_without_petition} of {coverage.queued} queued for "
        "prediction; an extraction fix reaches none of them. The wide count is a "
        "stock — a row distributed before the document channel existed was never "
        "fetched for — so read the queued one for what is recoverable now."
    )
    typer.echo(
        f"text frame: the pass read documents for {coverage.cases_read} of the "
        f"{coverage.cases} live-slice case(s) it walked — a reach count, not a "
        "failure rate: most of the rest were never fetched for (a historical-Term "
        "row, or a petition outside the upstream link window). A run that reaches "
        "nothing reports 0 here."
    )
    # Both columns sized from the data: a renamed or added segment must not
    # silently misalign the table against a hardcoded width.
    kind_width = max((len(cut.kind) for cut in coverage.cuts), default=0)
    segment_width = max((len(cut.segment) for cut in coverage.cuts), default=0)
    for cut in coverage.cuts:
        cut_share = f"{100 * cut.share:.2f}%" if cut.share is not None else "-"
        typer.echo(
            f"  {cut.segment:<{segment_width}} {cut.kind:<{kind_width}} "
            f"n={cut.documents} empty={cut.empty} ({cut_share})"
        )
    # Said in the report, not only in the source: a questions-presented row is
    # written only where the petition carries text, so its empty count is
    # conditioned on the very failure this measures and can never carry a scan.
    # Printed as 0.00% beside a real `n`, it would read as a measured zero.
    typer.echo(
        "  (a questions-presented row exists only where the petition has text, so "
        "its empty count is structurally unable to carry a scan; the segments are "
        "the salience gate's scored cut, in practice paid against IFP)"
    )
    # The triage list an extraction fix works from, untruncated for the reason
    # the questions-presented backfill prints its whole ledger: the count says
    # whether to act, the ids are what acting operates on.
    if coverage.empty_documents:
        typer.echo(f"empty text ({len(coverage.empty_documents)} case(s)):")
        for case_id, kinds in coverage.empty_documents.items():
            typer.echo(f"  {case_id}: {', '.join(kinds)}")


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


@app.command("refresh-historical")
def refresh_historical_cmd(
    term: Annotated[
        list[int] | None,
        typer.Option(
            "--term",
            help="Two-digit October Term to re-walk; repeatable. Default: every "
            "Term in `historical.terms`.",
        ),
    ] = None,
    stream: Annotated[
        list[str] | None,
        typer.Option(
            "--stream",
            help="Numbering stream to re-open: `historical-paid` or `historical-ifp`; "
            "repeatable. Default: both.",
        ),
    ] = None,
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Clear the cursors; omit for a dry-run listing."),
    ] = False,
) -> None:
    """Re-open past Terms for a full historical re-walk.

    Clears the per-(Term, stream) walk cursors so the next `historical-terms`
    invocations re-cover those Terms from the numbering base. This command moves
    no data and fetches nothing — the `run-seed` loop does the work afterwards.

    What it is for: the walk records what the pipeline could read at the time it
    ran. When the pipeline learns to read more — a new column, a corrected parser,
    a disposition pattern that used to be missed — already-walked Terms keep the
    older, thinner rows, and their cursors sit at the frontier so no ordinary run
    will ever revisit them. This is the way back.

    Re-walking **adds rows**: each re-served docket upserts onto its existing row
    through the corpus latches, so no row is deleted, `case_id` never moves, and
    every latched fact the first pass captured survives. An *unlatched* column is
    different — it takes the fresh parse, and the cert-stage disposition and its
    dates are unlatched — so a tightened pattern also retracts a stale reading.
    That is the way back from a false positive on a docket no rotation revisits,
    and it works only while the corrected parse still reads *some* disposition: a
    record that now reads undecided is counted `skipped_undecided` and never
    ingested. The real cost is upstream traffic (~1 req/s over each Term's full
    serial range), which is why this is dry-run by default.

    Deliberately separate from the walk rather than a flag on it: a walk that
    could rewind its own cursor could also do so on a degraded run and silently
    re-onboard a Term. Resetting stays an explicit, auditable act.

    `--stream` narrows which numbering sequences re-open. The two cost very
    differently — a Term's IFP sequence runs roughly three times its paid one —
    and only the paid stream feeds the scored segment, so a refresh aimed at the
    predicted population need not pay for the rest of the docket first.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it "
            "(fedcourts corpus-pull) before resetting walk cursors.",
            err=True,
        )
        raise typer.Exit(code=1)
    config = load_historical_config(settings.config_root)
    terms = term if term else list(config.terms)
    known = {name for name, _base in historical.HISTORICAL_STREAMS}
    if stream and not set(stream) <= known:
        typer.echo(
            f"unknown stream(s): {', '.join(sorted(set(stream) - known))}; "
            f"expected one of {', '.join(sorted(known))}.",
            err=True,
        )
        raise typer.Exit(code=2)
    wanted = [name for name, _base in historical.HISTORICAL_STREAMS if not stream or name in stream]
    if not apply:
        with corpus.connect(db_path) as conn:
            pending = [
                f"OT{2000 + t}/{name}"
                for t in sorted(set(terms))
                for name in wanted
                if corpus.get_live_cursor(conn, t, name) is not None
            ]
        typer.echo(
            f"refresh-historical (dry-run): would reset {len(pending)} cursor(s) "
            f"across {len(set(terms))} Term(s); re-run with --apply"
        )
        if pending:
            typer.echo(", ".join(pending))
        return
    report = historical.reset_walk(db_path, terms, wanted)
    typer.echo(
        f"refresh-historical (applied): reset {len(report.reset)} cursor(s), "
        f"{len(report.absent)} already absent"
    )
    typer.echo(report.model_dump_json())


@app.command("refresh-dockets")
def refresh_dockets_cmd(
    docket: Annotated[
        list[str] | None,
        typer.Option(
            "--docket",
            help="Term-form SCOTUS docket number to re-serve (e.g. `22-451`); repeatable.",
        ),
    ] = None,
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Re-serve and re-ingest; omit for a dry-run listing."),
    ] = False,
) -> None:
    """Re-snapshot named SCOTUS dockets without re-walking their Terms.

    The targeted counterpart to `refresh-historical`. That command re-opens whole
    Terms, which is what a population-wide re-read wants; this one is for the
    case where the dockets needing a fresh row are *known and enumerated*, where
    re-covering a Term would pay for its entire serial range at ~1 req/s to reach
    a handful of them.

    Each named number is re-served from the supremecourt.gov docket JSON and
    re-ingested through the walk's own path — identity reconciled by docket
    number, raw JSON stored as the dated snapshot, the resolved row upserted,
    documents provisioned from the document floor Term.
    **Additive**, exactly as a re-walk is: the upsert runs through the corpus
    latches, so no row is deleted and `case_id` never moves, while an unlatched
    column takes the fresh parse — the way back from a stale reading on a docket
    no rotation revisits.

    **Corpus-side, on the case this exists for.** The write is the shared ingest
    seam's, so `outcome.json` is recorded only where the event is still open: a
    committed outcome is never overwritten. A docket a walk already landed has
    its cert event latched resolved, so a re-serve converges the corpus row and
    leaves the ledger label alone — moving that is `converge-disposition-labels`'
    remit. A number the corpus has never held is onboarded outright, ledger
    included, exactly as the walk would have onboarded it.

    **No cursor moves.** A targeted re-snapshot is not a rewind: the walk resumes
    where it was, and re-reading a serial the cursor already passed is the point
    rather than state to record — so this is safe beside a walk of the same Term,
    both writing the same rows through the same latches.

    The walk's own rules hold, so a named list can never write what a walk would
    not: a served record with no machine-readable disposition is reported and
    skipped (pending matters are the forward poller's charter), and one whose
    case carries an open, predicted event is left to the watchlist so its
    resolution reaches the evaluate handoff this path never files.

    Dry-run by default: it resolves each number against the stored rows and
    fetches nothing, so the reading costs no upstream traffic. `--apply` does the
    re-serve, and is a corpus write — run it from the writer lane. The whole list
    is validated before the first fetch, so a typo lands no half of it.
    """
    settings = get_settings()
    numbers = list(docket or [])
    if not numbers:
        typer.echo("refresh-dockets: name at least one --docket.", err=True)
        raise typer.Exit(code=2)
    malformed = [n for n in numbers if parse_scotus_docket_number(n) is None]
    if malformed:
        typer.echo(
            f"not Term-form SCOTUS docket number(s): {', '.join(malformed)}; want e.g. 22-451. "
            "Applications (22A123) and original-docket numbers (22O141) are separate "
            "sequences this path does not serve.",
            err=True,
        )
        raise typer.Exit(code=2)
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if not db_path.exists():
        typer.echo(
            f"the corpus database is missing at {db_path}; provision it "
            "(fedcourts corpus-pull) before re-serving dockets.",
            err=True,
        )
        raise typer.Exit(code=1)
    cfg = load_historical_config(settings.config_root)
    if len(numbers) > cfg.max_probes_per_run:
        typer.echo(
            f"refresh-dockets: {len(numbers)} docket(s) named, past the "
            f"{cfg.max_probes_per_run}-probe bound one invocation runs under; "
            "split the list across dispatches.",
            err=True,
        )
        raise typer.Exit(code=2)
    if not apply:
        with corpus.connect(db_path) as conn:
            for number in numbers:
                known = corpus.scotus_case_id_by_docket_number(conn, number)
                typer.echo(f"  {number}: {known or 'no stored row — would onboard'}")
        typer.echo(
            f"refresh-dockets (dry-run): would re-serve {len(numbers)} docket(s) "
            "through the walk's ingest path, leaving every walk cursor where it is; "
            "re-run with --apply"
        )
        return
    with SupremeCourtClient(throttle_seconds=cfg.throttle_seconds) as client:
        rep = historical.refresh_dockets(
            client, db_path, settings.data_root, cfg, numbers, today=date.today()
        )
    _ensure_corpus_layout(db_path)
    ingested = rep.walk.ingested_granted + rep.walk.ingested_denied + rep.walk.ingested_other
    typer.echo(
        f"refresh-dockets (applied): served {len(rep.served)} of {len(numbers)} named; "
        f"ingested {ingested} (granted={rep.walk.ingested_granted} "
        f"denied={rep.walk.ingested_denied} other={rep.walk.ingested_other}); "
        f"documents={rep.walk.documents}"
    )
    if rep.unserved:
        typer.echo(f"  no record upstream: {', '.join(rep.unserved)}")
    if rep.undecided:
        typer.echo(f"  served but undecided (not ingested): {', '.join(rep.undecided)}")
    if rep.left_to_watchlist:
        typer.echo(
            f"  left to the watchlist: {', '.join(rep.left_to_watchlist)} "
            "(an open, predicted event — its re-poll files the evaluate handoff)"
        )
    # An upstream error is not a result: the named docket was neither re-served
    # nor found absent, so the list this dispatch answered for is incomplete.
    # Annotated rather than fatal, because the numbers that did land are landed
    # and the caller's next step is a re-dispatch of the remainder, not a
    # rollback — but it must not read as a clean pass in a run summary.
    for failure in rep.walk.failed:
        typer.echo(f"::warning::refresh-dockets could not serve a named docket: {failure}")


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
    cursors — and ingests **every decided petition**, denials included. Ingested
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
        f"documents={rep.documents} "
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
def corpus_info(
    corpus_backend: CorpusBackendOption = "",
    text_coverage: Annotated[
        bool,
        typer.Option(
            "--text-coverage",
            help="Also count the stored documents whose text is empty, per kind "
            "(petition / brief-in-opposition / questions-presented) and split on "
            "the salience gate's paid modern-cert segment. Opt-in and not cheap: "
            "it reads the documents of every live-slice case, tens of thousands of "
            "rows, which under the corpus split is a content-store manifest round "
            "trip each plus a full text body for every document stored — so the "
            "default vintage report stays a few KB.",
        ),
    ] = False,
) -> None:
    """Show the corpus location, row count, and freshness (after `corpus-pull`, or ranged).

    The freshness line is the reason to run this before making any claim that
    depends on corpus state: the committed pointer is a content digest carrying
    no date, so nothing beside the blob dates it, and it is only ever as fresh
    as the last pull left it. (The docket pack derives the same `last_pulled`
    maximum for its `pulled through` line — this is the cheap way to the
    number, not the only one.) Two dates, because they age differently and
    a blob can carry one without the other — `latest pull` is the newest
    `last_pulled` over the cases (kept in a payload-free index, so it reports
    on the production shape too) and `latest snapshot` the newest dated docket
    state the blob itself stores. A payload-free index stores none: the
    snapshots live in the per-case content store, which the snapshot count does
    not read (`--text-coverage` below is the one read that does reach the
    store). Hence `in this blob` on both snapshot readings — under the corpus
    split, `no snapshots` would otherwise read as a claim about the system.

    Both are maxima over the whole blob: its vintage, not any one case's. The
    pull governor rotates stalest-first, so a maximum says when *anything* was
    last refreshed — a claim about a specific case reads that case's own
    `last_pulled` instead.

    `--text-coverage` adds the other thing worth knowing about a blob before
    quoting it: not how old the documents are but whether they carry text at
    all. A filing that arrives as a scan with no text layer stores an empty
    string, which provisioning stamps on the cell manifest as `empty_text` —
    written into the cell's manifest, never into a corpus column — so the share
    is counted off the stored text rather than queried. The counts stay per
    kind because emptiness does not mean one thing across them: on the two
    fetched PDFs it reads as a scan, while an empty derived
    questions-presented row is as likely to be an extraction the deriver would
    not vouch for, over a petition that does carry text. It is opt-in because
    it reads every live-slice case's documents (a per-case content-store round
    trip each, under the corpus split), and it names the source that served
    those reads: a blob-only run against a split corpus finds no documents at
    all, and must not be read as a corpus with none.
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend))
    if backend == "local" and not db_path.exists():
        typer.echo(f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.")
        return
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        typer.echo(
            f"corpus {db_path} [{backend}]: {corpus.count(conn)} row(s), "
            f"{corpus.snapshot_count(conn)} snapshot(s) in this blob"
        )
        pulled = corpus.latest_pull_date(conn)
        snapshot = corpus.latest_snapshot_date(conn)
        pulled_text = f"latest pull {pulled.isoformat()}" if pulled else "never pulled"
        snapshot_text = (
            f"latest snapshot {snapshot.isoformat()}" if snapshot else "no snapshots in this blob"
        )
        typer.echo(f"freshness: {pulled_text}, {snapshot_text}")
        # A freshness claim must name the blob it was read from; with the
        # out-of-band override set, a ranged read served the override's object,
        # not the committed ref — say so, so no vintage is quoted blind. Under
        # any other backend the override did not govern this read, so claiming
        # its digest here would misattribute the local file's freshness.
        if settings.corpus_pointer is not None:
            if backend == "ranged":
                try:
                    override_sha = corpus_ranged.parse_pointer_override(
                        settings.corpus_pointer
                    ).sha256
                    typer.echo(f"pointer: out-of-band override (sha256 {override_sha})")
                except corpus_ranged.RangedBackendError:
                    typer.echo("pointer: out-of-band override (set but unparseable)")
            else:
                typer.echo(f"pointer: out-of-band override set (not read by the {backend} backend)")
        # The durable half of the same claim: under `local` the vintage above
        # is the on-disk blob's, and the pull's provenance sidecar says which
        # pointer that blob came from — a blob pulled through the override (or
        # left behind by a superseded pull) must not read as the committed ref's.
        if backend == "local":
            pulled_path = corpus_remote.pulled_pointer_path_for(db_path)
            if pulled_path.is_file():
                try:
                    pulled_sha: str | None = corpus_ranged.read_index_pointer(pulled_path).sha256
                except corpus_ranged.RangedBackendError:
                    pulled_sha = None
                committed_path = corpus_remote.pointer_path_for(db_path)
                try:
                    committed_sha: str | None = (
                        corpus_ranged.read_index_pointer(committed_path).sha256
                        if committed_path.is_file()
                        else None
                    )
                except corpus_ranged.RangedBackendError:
                    committed_sha = None
                if pulled_sha is not None and pulled_sha != committed_sha:
                    typer.echo(
                        f"pointer: the blob on disk is not the committed ref's (pulled "
                        f"sha256 {pulled_sha}) — re-pull before quoting this vintage"
                    )
        if text_coverage:
            _echo_text_coverage(document_text_coverage(conn))
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


#: The whole `query` interface, for an invocation that guessed a different one.
#: `{dispositions}` / `{eras}` are filled from the live vocabularies at print
#: time, so the tokens it offers are the ones the filters accept.
_QUERY_INTERFACE_HELP = """\
The `fedcourts query` interface, in full:

It takes no free-text search argument. It is a structured filter over the
corpus, not a search engine: a phrase, a case name or a docket caption is
rejected as an extra argument. Say what you want in flags.

Filters — every one optional, none of them positional:
  --court TEXT           one CourtListener court id, e.g. scotus
  --topic TEXT           nature-of-suit / subject, matched EXACTLY; the
                         values come off the `topic` field of returned rows
  --judge TEXT           repeatable; ranks on shared judges
  --citation TEXT        repeatable, e.g. '597 U.S. 1' — this case's own
                         parallel cite, not a cases-citing-it search
  --disposition TEXT     one realized outcome label, listed below
  --era TEXT             one decade token, listed below
  --decided-before YEAR  a bare four-digit year, not a date
  --limit N              how many priors to return
  --corpus-backend NAME  transport only: local / ranged / service; the run
                         environment sets this, so leave it alone
  --include-open, --include-applications, --full   take no value

The two closed vocabularies:
  --disposition
{dispositions}
  --era
{eras}

`--topic`, `--judge` and `--citation` are sparsely populated: a filter on
one can come back empty because the column is thin, not because no such
prior exists. Widen rather than retry.

Worked example:
  fedcourts query --court scotus --disposition granted --limit 5

Every flag with its own help: fedcourts query --help"""

#: Where the vocabulary lists wrap. Narrow enough that the terse default
#: terminal still renders each token list as a block rather than re-wrapping it
#: into the flag column, which is what makes the screen scannable at all.
_QUERY_HELP_WIDTH = 72


def _query_interface_help() -> str:
    """:data:`_QUERY_INTERFACE_HELP` with the current filter vocabularies in it."""

    def block(tokens: Iterable[str]) -> str:
        return textwrap.fill(
            " ".join(tokens),
            width=_QUERY_HELP_WIDTH,
            initial_indent="    ",
            subsequent_indent="    ",
        )

    return _QUERY_INTERFACE_HELP.format(
        dispositions=block(d.value for d in Disposition),
        eras=block(corpus.era_tokens()),
    )


class _TeachingQueryCommand(TyperCommand):
    """A command whose usage errors carry the interface they rejected.

    The failure this exists to stop is behavioural, not syntactic. An agent
    cell that guesses a search-engine interface — a bare phrase, a case name
    after ``--full``, a court-name era — gets one terse line naming what was
    wrong and nothing saying what is right, and abandons the corpus for the
    rest of its run, forecasting without priors. Appending the interface to
    the error makes the same cell's next attempt the correct one.

    Every parse-time usage error is augmented, not a chosen few: the guesses
    that produce them are open-ended (an unknown flag, a date where a year
    goes, a phrase left over after parsing), while what the reader needs back
    is the same one screen in each case. Nothing else about the failure changes — the usage
    line, the exit code, and the message click already wrote are as they were.

    The augmentation is of the **formatted** message, not of ``message``
    itself, and re-raised as a plain :class:`UsageError` rather than mutated in
    place. Click's subclasses build their rendering *around* that attribute —
    a near-miss flag appends "(Possible options: --court)" after it — so
    editing it in place would bury the single most actionable line of the error
    at the tail of a thirty-line screen. Formatting first keeps every
    subclass's own framing intact and puts the screen after all of it.

    Deliberately attached to one command rather than the app: it is worth doing
    where the surface is both narrow and easy to mistake for a search engine,
    and a CLI whose every misuse printed a page would teach nothing.
    """

    def parse_args(self, ctx: Any, args: list[str]) -> list[str]:
        try:
            return super().parse_args(ctx, args)
        except UsageError as exc:
            raise UsageError(
                f"{exc.format_message()}\n\n{_query_interface_help()}", ctx=exc.ctx
            ) from exc


@app.command(cls=_TeachingQueryCommand)
def query(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to the query filters
    *,
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
    include_applications: Annotated[
        bool,
        typer.Option(
            help="Include the non-cert SCOTUS letter forms — time-extension and "
            "unread-ask applications, original-jurisdiction and miscellaneous "
            "matters. Excluded by default because their 'granted' records an "
            "extension or a procedural leave rather than a cert vote, and "
            "resolving in days floats them to the head of the recency ranking; "
            "substantive applications (stays, injunctions) return either way."
        ),
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
    match on overlap and rank the results by how much they share. The SCOTUS
    letter forms that are not cert petitions — time-extension applications,
    original-jurisdiction and miscellaneous dockets — are screened out unless
    ``--include-applications``: their disposition is not a cert vote, and an
    extension resolves so fast that recency would put them ahead of the
    petitions a cert cell asked for. A substantive application — a stay, an
    injunction — is kept either way, being the interim predict scope.
    Prints one compact JSON row per line, ranked, with
    ``opinion_text`` omitted unless ``--full``.
    Reads the pulled file, the blob in place on the remote with
    ``--corpus-backend ranged``, or forwards to a corpus query sidecar with
    ``--corpus-backend service`` (same rows, same read-stats line — a
    transport change, not a different surface).

    Maintained as-is: cells' open-web retrieval moved to the official
    CourtListener MCP server, so this surface gets no further feature work —
    it stays the corpus-priors/base-rates read (the one retrieval a *replay*
    cell leans on) rather than growing into a bespoke search engine.
    """
    settings = get_settings()
    # The two closed vocabularies are judged before the corpus is looked for:
    # a caller who spelled a filter wrong needs the interface back whatever the
    # state of the blob, and "no corpus here" would send them to `corpus-pull`
    # for a failure the pull cannot fix.
    try:
        disp = Disposition(disposition) if disposition else None
    except ValueError as exc:
        choices = ", ".join(d.value for d in Disposition)
        typer.echo(f"Unknown disposition '{disposition}'; choose one of: {choices}", err=True)
        typer.echo(_query_interface_help(), err=True)
        raise typer.Exit(code=2) from exc
    # An era is refused rather than silently returning nothing: a guess at a
    # court-name era ("Roberts Court") would otherwise filter every row away
    # and read back as a corpus that holds no priors.
    if era and era not in corpus.era_tokens():
        typer.echo(
            f"Unknown era '{era}'; an era is one decade token — not a court, "
            "a Term or a date range. The vocabulary is below.",
            err=True,
        )
        typer.echo(_query_interface_help(), err=True)
        raise typer.Exit(code=2)
    db_path = corpus.corpus_db_path(settings.corpus_root)
    backend = corpus.resolve_backend(_corpus_backend(corpus_backend, allow_service=True))
    if backend == "local" and not db_path.exists():
        typer.echo(
            f"No corpus at {db_path} — `fedcourts corpus-pull` to fetch it from the remote.",
            err=True,
        )
        raise typer.Exit(code=1)
    q = corpus.PriorQuery(
        court=court or None,
        topic=topic or None,
        judges=judge or [],
        citations=citation or [],
        disposition=disp,
        era=era or None,
        decided_before=decided_before or None,
        resolved_only=not include_open,
        exclude_non_cert=not include_applications,
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
    # The sidecar log IS this process's stderr, and the service module's
    # per-request records and health-check transfer evidence are INFO-level —
    # without a configured handler the root default (WARNING) discards them
    # and the log carries only the startup banner and tracebacks. Configured
    # here, not at import: the CLI's other commands own their stderr contract.
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
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
    *,
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
            # Rendered from the accepted set, not restated: a hand-kept list
            # drifts silently every time a dimension lands, and `--help` is what a
            # cell agent reads to discover the cuts it can ask for. Dimensions
            # keyed off an artifact rather than a corpus row are section-only and
            # excluded, so nothing is offered that this command cannot compute.
            help="Break base-rates down by a dimension: "
            + ", ".join(g.value for g in analytics.STATS_DIMENSIONS)
            + ". Omit for the overall base rate only."
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
    overall and, with `--group-by`, per bucket of the dimension you name (listed
    under `--group-by` below).
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
    # `query`'s era vocabulary, refused on the same terms: this command answers
    # a base rate rather than returning rows, so an unrecognized era would come
    # back as a well-formed report over zero cases — a number, and the wrong
    # one, where `query` at least returned nothing visible.
    eras = corpus.era_tokens()
    if era and era not in eras:
        typer.echo(
            f"Unknown era '{era}'; choose one of: {', '.join(eras)}. A row dated "
            "outside that window carries an era this filter cannot name — such a "
            "row is unaddressable here, not absent from the corpus.",
            err=True,
        )
        raise typer.Exit(code=2)
    dimension = next((g for g in analytics.STATS_DIMENSIONS if g.value == group_by), None)
    if group_by and dimension is None:
        choices = ", ".join(g.value for g in analytics.STATS_DIMENSIONS)
        typer.echo(f"Unknown --group-by '{group_by}'; choose one of: {choices}", err=True)
        raise typer.Exit(code=2)
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


def _forward_leakage(payload: Mapping[str, Any], court: str, event_id: str) -> str | None:
    """Why a forward cell's snapshot already shows **its own** event's outcome.

    A forward *prediction* cell forecasts a genuinely pending event, so a
    snapshot disclosing that event's outcome must never be materialized — it
    would hand the predictor the answer. The question is always keyed on the
    event, because one docket carries outcomes of different events at once: a
    granted cert docket's grant order *is* a disclosed cert outcome and is also
    the thing that opens the merits proceeding, so the same entry that must
    refuse a cert cell must not refuse the merits cell it created.

    On the **merits** event the disclosed outcome is the judgment, tested two
    ways because they fail differently. The shared merits parser
    (:func:`fedcourtsai.pipeline.judgment.last_judgment_entry`) names the
    judgment it read, which makes the refusal legible; it is deliberately
    conservative, though, so :func:`snapshot_shows_judgment` runs beside it and
    supplies the recall — every terminal shape the cert scan catches is a
    decided merits docket too, and a miss here hands a forward cell its answer.
    Nothing cert-shaped applies beyond that: the grant, the distributions, and
    the CVSG are the merits cell's legitimate provisioned record.

    On every other event the disclosed outcome is the cert or interim
    disposition, and three checks run over either payload shape (REST
    ``docket_entries`` or the raw live ``ProceedingsandOrder``):

    - the high-recall terminal scan (:func:`snapshot_shows_disposition`, over
      *every* entry) — provisioning's semantic is "outcome visible anywhere in
      the snapshot", not docket pendency, so a disposition followed by
      administrative notations ("Application ... denied as moot") that hide it
      from the latest-entry rule, and the cert-before-judgment grant / merits
      judgment the resolver omits, are still caught;
    - the resolver (:func:`match_disposition_signal`) over *every* entry, which
      adds the plain cert grant/denial orders that are not terminal-shaped;
    - on an application-form docket, the high-recall interim disposal scan
      (:func:`interim_disposal_signal`) — the cert-shaped checks above match no
      application phrasing, and the interim resolver's exact vocabulary can
      miss a disposal that names the relief instead of the application.

    The pull-side routing skip and the resolver latch are the primary
    protections; this refusal is defense-in-depth for cells fanned out before
    the docket latched.
    """
    # Keyed on the event's declared STAGE, not on one event id: every merits
    # moment forecasts the judgment, so every one of them must take the judgment
    # branch. Testing an id would send a later merits moment down the cert
    # branch, where the grant order that opened its own proceeding reads as a
    # disclosed outcome — refusing the cell permanently, and silently.
    spec = moments.spec_for(event_id)
    if spec is not None and spec.stage is Stage.merits:
        judgment = last_judgment_entry(payload)
        if judgment is not None:
            return f"snapshot carries a merits judgment: {judgment[0].value!r}"
        return snapshot_shows_judgment(payload)
    terminal = snapshot_shows_disposition(payload)
    payload_number = str(payload.get("docket_number") or payload.get("CaseNumber") or "")
    if terminal is None and court == "scotus" and corpus.is_scotus_application_form(payload_number):
        terminal = interim_disposal_signal(payload)
    if terminal is None:
        for text in entry_descriptions(payload):
            matched = match_disposition_signal(text)
            if matched is not None:
                return f"snapshot carries a disposition order: {matched[2]!r}"
    return terminal


def _refuse_forward_if_closed(
    backend: corpus.CorpusBackend,
    gate_events: Sequence[corpus.CorpusEvent],
    gate_row: corpus.CorpusRow | None,
    court: str,
    docket: int,
    event: str,
    snapshot_date: date,
    max_snapshot_age_days: int,
) -> None:
    """The record and staleness gates of a forward cell; exit 3 on refusal.

    The mechanical half of ``--refuse-terminal`` (the textual scan stays with
    the caller, which holds the payload): the record gate over the parts
    provisioning already read on its own connection, the casestore row-half
    fallback through the ordinary index backend, and the wall-clock staleness
    bound. Refusals are ``::warning::`` annotations so a fleet of skipped
    cells is attributable per cause from the Actions UI.
    """
    settings = get_settings()
    case = ids.case_id(court, docket)
    reason = forward_refusal_reason_from_parts(
        settings.data_root, court, docket, event, gate_events, gate_row
    )
    if reason is None and backend == "casestore":
        reason = _casestore_row_refusal(
            corpus.corpus_db_path(settings.corpus_root), court, docket, event
        )
    if reason is not None:
        typer.echo(
            f"::warning::refusing to provision forward cell for {case}: {reason}",
            err=True,
        )
        raise typer.Exit(code=3)
    age_days = (date.today() - snapshot_date).days
    if max_snapshot_age_days and age_days > max_snapshot_age_days:
        typer.echo(
            f"::warning::refusing to provision forward cell for {case}: snapshot "
            f"{snapshot_date.isoformat()} is {age_days} day(s) old, over the "
            f"{max_snapshot_age_days}-day forward bound (--max-snapshot-age-days)",
            err=True,
        )
        raise typer.Exit(code=3)


def _casestore_row_refusal(db_path: Path, court: str, docket: int, event: str) -> str | None:
    """The row-level half of the forward record gate, from the casestore path.

    The casestore source exposes events but no corpus rows, so the row half
    consults the corpus **index** through the ordinary read backend — ranged in
    the cell workflows, whose provisioning step carries the index credentials
    beside the casestore URL. Degrades to a spoken warning when no index is
    reachable: the event-keyed half already ran, and a forward cell must not be
    lost to an index hiccup the snapshot read did not need.
    """
    settings = get_settings()
    choice = corpus.resolve_backend(None)
    if choice != "local" or db_path.exists():
        try:
            return forward_refusal_reason(
                db_path, settings.data_root, court, docket, event, backend=choice
            )
        except (OSError, corpus_ranged.RangedBackendError):
            pass
    typer.echo(
        "::warning::forward record gate ran without the row-level decided "
        "check: no corpus index reachable from the casestore path",
        err=True,
    )
    return None


def _read_cell_inputs(
    backend: corpus.CorpusBackend,
    db_path: Path,
    case: str,
    event: str,
    *,
    want_row: bool,
    cut: bool,
) -> provision.CellRead:
    """One backend read of everything a cell's provisioning decides on.

    Kept whole, and kept inside one connection, because that is what makes a
    ranged cell's egress counters (``_echo_read_stats``) the whole story of what
    the cell cost.

    ``want_row`` fetches the row half of the terminal gate, which only an armed
    gate reads. ``cut`` asks for the moment placement: ``provision.moment_cutoff``
    decides from the events whether this event declares a moment with a date to
    be placed at, and the pre-cutoff snapshot is fetched on the same connection.
    That read happens before the caller's gates run, so a refused cell pays for
    one snapshot it never uses; the alternative is a second connection on every
    cut cell.

    The events are read for either — the gate reads them, and a cutoff is a
    property of the moment the cell forecasts rather than of the gate — and for
    neither otherwise, which is the evaluate path: an unread list is egress this
    command's single-connection design exists to account for.
    """
    if backend == "casestore":
        source = _casestore_source()
        events = source.events_for_case(case) if want_row or cut else []
        cutoff = provision.moment_cutoff(event, events) if cut else None
        return provision.CellRead(
            latest=source.latest_snapshot(case),
            documents=source.documents_for_case(case),
            events=events,
            # The casestore exposes events but no rows; `_casestore_row_refusal`
            # is the gate's own fallback for the row half.
            row=None,
            cutoff=cutoff,
            dated=source.snapshot_at(case, before=cutoff) if cutoff is not None else None,
        )
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        events = corpus.events_for_case(conn, case) if want_row or cut else []
        cutoff = provision.moment_cutoff(event, events) if cut else None
        read = provision.CellRead(
            latest=corpus.latest_snapshot(conn, case),
            documents=corpus.documents_for_case(conn, case),
            events=events,
            row=corpus.get_row(conn, case) if want_row else None,
            cutoff=cutoff,
            dated=corpus.snapshot_at(conn, case, before=cutoff) if cutoff is not None else None,
        )
        _echo_read_stats(conn)
    return read


@app.command("provision-snapshot")
def provision_snapshot(  # noqa: PLR0913 - a CLI entrypoint; options map 1:1 to inputs
    *,
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    out: Annotated[
        Path | None,
        typer.Option(help="Where to write the snapshot; defaults to the case's record path."),
    ] = None,
    mode: Annotated[
        str,
        typer.Option(
            help="The cell's mode, written into record/context.json, one of "
            + " | ".join(CELL_MODES)
            + ". forward is a live cell and the default; replay is a back-test "
            "cell, which the replay provisioner in cert_backtest writes itself."
        ),
    ] = "forward",
    refuse_terminal: Annotated[
        bool,
        typer.Option(
            "--refuse-terminal",
            help="Refuse (exit 3, writing nothing) when the record or the "
            "snapshot shows the event is not open: the record already holds "
            "the outcome (committed outcome.json, corpus resolved flag, or "
            "the row's latched outcome for the event's stage), the snapshot "
            "is older than --max-snapshot-age-days, or the snapshot text "
            "discloses the outcome. A forward *prediction* cell must never "
            "see a decided docket. Only the forward predict path passes "
            "this: an evaluate cell targets exactly decided dockets, so the "
            "default provisions unconditionally.",
        ),
    ] = False,
    event: Annotated[
        str,
        typer.Option(
            help="The event this cell forecasts. Scopes --refuse-terminal to "
            "that event's own outcome, and places the cell at the event's "
            "declared moment (see --moment-cutoff); omitted, the guard reads "
            "the cert/interim disposition, which is the right question for "
            "every case-baseline cell, and no cut is taken.",
        ),
    ] = "",
    moment_cutoff: Annotated[
        bool,
        typer.Option(
            "--moment-cutoff/--no-moment-cutoff",
            help="Cut a forward cell's snapshot and documents to the "
            "information set its --event declares: everything filed strictly "
            "before the day after the event opened. A stage's later moments "
            "exist because their information sets differ, so a grant-moment "
            "merits cell provisioned from the latest snapshot would read the "
            "merits briefs only the briefed moment declares. On by default; it "
            "acts only on a forward cell whose --event names a declared moment "
            "whose opened_at is that moment's trigger and whose corpus row "
            "records it, so a case-baseline cell and an evaluate cell (no "
            "--event) are untouched either way.",
        ),
    ] = True,
    max_snapshot_age_days: Annotated[
        int,
        typer.Option(
            min=0,
            help="With --refuse-terminal on a forward cell, refuse (exit 3) a "
            "snapshot older than this many days. A time bound, not a content "
            "check: a snapshot taken before a pipeline pause discloses "
            "nothing about what happened during the pause — including the "
            "event's own resolution — so a forward cell fed one would claim "
            "to be live while answering a stale question. 0 (the default) "
            "disables the bound.",
        ),
    ] = 0,
    corpus_backend: CorpusBackendOption = "",
) -> None:
    """Materialize a case's corpus snapshot (and documents) for an agent run.

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
    fetch rights.

    "Most recent" is the answer only for a cell that has no declared moment of
    its own. Where ``--event`` names one (and ``--moment-cutoff`` is on, which is
    the default), a forward cell is placed at that moment instead: the snapshot
    is the one the docket served before the cutoff if the corpus stored one
    (``dated``), otherwise the latest payload with its post-cutoff entries
    removed and its date set to the cutoff (``truncated``), and the documents are
    cut with it. ``record/context.json`` records which, and the cutoff. Both
    gates below run on the latest payload first, before any of that.

    Exits non-zero if the corpus holds no snapshot for the case
    (code 1), or — under ``--refuse-terminal`` on a forward cell — if the
    record or the snapshot shows the event is not open (code 3, nothing
    written): the record already holds the outcome
    (:func:`fedcourtsai.store.forward_refusal_reason`), the snapshot is older
    than the forward staleness bound, or the snapshot text discloses the
    outcome (see :func:`_forward_leakage`).
    """
    settings = get_settings()
    db_path = corpus.corpus_db_path(settings.corpus_root)
    case = ids.case_id(court, docket)
    backend = _provision_backend(corpus_backend)
    gate_active = refuse_terminal and mode == "forward"
    # The cut applies to a forward cell that names an event; whether that event
    # *declares* a moment with a usable date is `provision.moment_cutoff`'s call.
    read = _read_cell_inputs(
        backend,
        db_path,
        case,
        event,
        want_row=gate_active,
        cut=moment_cutoff and mode == "forward" and bool(event),
    )
    found = read.latest
    documents = read.documents
    cutoff = read.cutoff
    if found is None:
        typer.echo(f"No snapshot in corpus for {case} (corpus-pull the corpus first?)", err=True)
        raise typer.Exit(code=1)
    if mode not in CELL_MODES:
        typer.echo(f"unknown --mode '{mode}'; choose forward or replay", err=True)
        raise typer.Exit(code=2)
    snapshot_date, payload = found
    # Refuses before writing anything (no snapshot, no context.json).
    # run-predict short-circuits the cell's agent steps on either non-zero exit
    # — this refusal (exit 3) and the missing snapshot (exit 1) alike, since a
    # predictor with no provisioned record has lost the guaranteed-common input
    # — and keeps the two causes apart in the log. Opt-in
    # because the other callers *must* see decided dockets: run-evaluate
    # provisions the same forward-mode cell for an already-resolved event, and
    # the replay provisioner truncates point-in-time itself.
    #
    # Three gates, mechanical before textual. The record gate asks whether the
    # outcome *exists* (committed outcome.json, the corpus event's resolved
    # flag, the row's latched outcome for the event's stage); the
    # staleness gate bounds how old a "live" snapshot may be, because a paused
    # pipeline resumes with snapshots that predate everything the world did in
    # the meantime — including the resolution — and such a snapshot passes the
    # textual scan by construction. Only then does the textual scan ask whether
    # the payload itself discloses the outcome. None of this rests on the
    # agent: a refused forward cell never receives a snapshot or a context —
    # un-minting is the plan seam's job (the matrix forecastability re-check), and
    # run-predict's refusal gate skips the cell's agent steps on exit 3
    # entirely. Refusals are ::warning::
    # annotations so a fleet of skipped cells is attributable per cause
    # from the Actions UI.
    if gate_active:
        _refuse_forward_if_closed(
            backend,
            read.events,
            read.row,
            court,
            docket,
            event,
            snapshot_date,
            max_snapshot_age_days,
        )
        terminal = _forward_leakage(payload, court, event)
        if terminal is not None:
            typer.echo(
                f"::warning::refusing to provision forward cell for {case}: {terminal}",
                err=True,
            )
            raise typer.Exit(code=3)
    # Both gates ran on the LATEST payload, before the cut, and that ordering is
    # the point of putting the cut here. The staleness bound asks whether the
    # *pipeline* is live, which only the latest snapshot's date can answer — a
    # cut payload is re-dated to its cutoff and would read as months stale by
    # construction. The terminal scan asks whether the docket is decided, and a
    # disposing order filed after the cutoff is exactly what the cut would hide:
    # the cell would be provisioned, not refused, against a case that is over.
    provenance: Literal["as-stored", "dated", "truncated"] = "as-stored"
    # Nothing was removed from a `dated` payload: it is what the docket served.
    dropped_entries = 0
    if cutoff is not None:
        if read.dated is not None and provision.shows_the_moment(read.dated[1], cutoff):
            # What the docket really served at the moment, which also knows what
            # had not yet been filed — strictly better than reconstructing it, so
            # it is preferred and recorded apart. Only where it reaches the
            # trigger, though: a stored snapshot from well before the moment
            # would place the cell earlier than the cohort it is filed under.
            snapshot_date, payload = read.dated
            provenance = "dated"
        else:
            # Reconstructed from a later payload: post-cutoff entries removed,
            # and an entry whose date is missing or unparseable removed with them
            # (`truncate_snapshot` fails closed — an undated entry could be the
            # one that decides the case). Never `blind`: this path always holds a
            # cutoff to keep entries against, so it never removes the proceedings
            # key outright, which is what that provenance records.
            payload, dropped_entries = truncate_snapshot(payload, cutoff)
            # The same date rule over the top-level fields truncation does not
            # reach, so the cut docket does not carry an argument date whose
            # entry it just removed.
            payload = provision.cut_dated_fields(payload, cutoff)
            # The docket as at the cutoff is dated by the cutoff, not by the pull
            # whose bytes it was reconstructed from — otherwise the one file the
            # cell's information set is judged against carries a later date than
            # anything in it.
            snapshot_date = cutoff
            provenance = "truncated"
        kept = provision.documents_before(documents, cutoff)
        dropped_documents = len(documents) - len(kept)
        documents = kept
        # Spoken, never written to `context.json`: the cell reads that file, and
        # how much a cut removed separates a grant from a denial about as
        # cleanly as the disposing order does. Here it is the harness's own
        # record — the auditable size of what placement excluded.
        typer.echo(
            f"::notice::{case} placed at {cutoff.isoformat()} ({provenance}): "
            f"{dropped_entries} entr(ies) and {dropped_documents} document(s) "
            f"postdate the moment",
            err=True,
        )
    paths = CasePaths(settings.data_root, court, docket)
    dest = out or paths.snapshot(snapshot_date.isoformat())
    write_raw_json(dest, payload)
    # The cell's context: its mode, and the conditioning state it is about to run
    # against. Both are stated at provisioning — the mode so the prompt contract
    # keys replay etiquette on it rather than inferring from env vars, and the
    # rest because the salience band only ever strengthens, so a band re-derived
    # later is the band the petition *ended* at. Derived from the payload rather
    # than the corpus row: the row holds current values, the payload is what this
    # cell can read, and a baseline has to be conditioned on the latter. The
    # cutoff rides along as the cohort marker: a forward cell whose `cutoff` is
    # non-null was placed at its moment, and a figure that pools it with one
    # provisioned from the latest snapshot pools two information sets.
    write_raw_json(
        paths.cell_context,
        cell_context.build(
            case,
            snapshot_date,
            payload,
            mode,
            provenance=provenance,
            cutoff=cutoff,
        ).model_dump(mode="json"),
    )
    placed = f" cut at {cutoff.isoformat()} ({provenance})" if cutoff is not None else ""
    typer.echo(f"{case} snapshot {snapshot_date.isoformat()} ({mode}){placed} -> {dest}")
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


@app.command("assert-cell-record")
def assert_cell_record(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[
        str,
        typer.Option(
            help="The event this cell forecasts. Names the cell in the warning so "
            "a fleet of skipped cells is attributable from the Actions log; the "
            "record itself is per case, so nothing about the check is event-keyed."
        ),
    ],
) -> None:
    """Assert that a cell's provisioned record landed complete, or exit 1.

    The provisioned snapshot is every predictor's guaranteed-common input, so a
    cell whose record never landed must not run its agent: it would forecast from
    base rates alone while its output claims the shared baseline, and nothing
    downstream can tell the two apart. ``provision-snapshot`` declares the
    failures it knows about through its exit code, but a read that half-lands
    declares nothing — this command asks the disk instead of the exit code, and
    is the predict cell's gate between provisioning and any token spend.

    Complete means both halves of the provisioning write are there and readable:
    ``record/context.json`` parses as a
    :class:`~fedcourtsai.schemas.PredictionContext`, and the dated snapshot that
    context names is present, non-empty, and parses as JSON. The snapshot is
    parsed rather than merely counted because provisioning's write is not atomic,
    so the very failure this command is named for — a write that half-lands —
    leaves a truncated file that a size check passes. Exit 0 complete; exit 1
    incomplete, with a ``::warning::`` naming which half is missing. It reads the
    default record paths — the ones the cell workflows provision into — so a
    ``provision-snapshot --out`` written elsewhere is not what it checks.

    The context load is spelled out here rather than reusing
    :func:`_read_cell_context`, which is deliberately tolerant and returns
    ``None`` for both "absent" and "unreadable": this command's whole output is
    *which* of those it found.
    """
    settings = get_settings()
    case = ids.case_id(court, docket)
    paths = CasePaths(settings.data_root, court, docket)
    context_path = paths.cell_context
    missing: str | None = None
    if not context_path.is_file():
        missing = f"no cell context at {context_path}"
    else:
        try:
            context = PredictionContext.model_validate_json(context_path.read_text())
        except (OSError, ValueError):
            missing = f"unreadable cell context at {context_path}"
        else:
            snapshot = paths.snapshot(context.snapshot_date.isoformat())
            if not snapshot.is_file():
                missing = f"no snapshot at {snapshot}"
            elif snapshot.stat().st_size == 0:
                missing = f"empty snapshot at {snapshot}"
            else:
                try:
                    json.loads(snapshot.read_text())
                except (OSError, ValueError):
                    missing = f"unreadable snapshot at {snapshot}"
    if missing is not None:
        typer.echo(
            f"::warning::incomplete cell record for {case} {event}: {missing}; no cell runs",
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(f"{case} {event} record complete -> {context_path}")


def _read_cell_context(paths: CasePaths) -> PredictionContext | None:
    """The provisioned cell context, or ``None`` when there is nothing usable.

    Tolerant on purpose: this runs as a post-agent step, and a missing or
    unreadable context file means the cell was not provisioned, which is a
    recorded gap rather than a reason to fail a prediction that already exists.
    The `mode`-only shape a pre-context provisioning wrote also lands here and is
    correctly rejected, since it carries no conditioning to freeze.
    """
    path = paths.cell_context
    if not path.is_file():
        return None
    try:
        return PredictionContext.model_validate_json(path.read_text())
    except (OSError, ValueError):
        # A file that exists but does not parse is worth a line: it is either a
        # replay cell's own `{mode, decided_before}` shape, which carries no
        # conditioning and is correctly rejected, or a provisioning bug.
        # No command prefix: both `stamp-cell` and `record-retrieval` land here.
        typer.echo(f"{path} carries no usable cell context; leaving it unset.", err=True)
        return None


@app.command("provision-blinded-predictions")
def provision_blinded_predictions_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="The resolved event whose predictions are graded.")],
    run_id: Annotated[str, typer.Option(help="The evaluate run id; seeds the alias assignment.")],
    map_dir: Annotated[
        Path,
        typer.Option(
            help="Where the alias map is written/read. Deliberately outside the "
            "case tree the grader is told to open; point it at a runner-local "
            "path (e.g. the runner temp dir) in CI.",
        ),
    ] = blinding.DEFAULT_MAP_DIR,
) -> None:
    """Stage every predictor's latest prediction under an opaque alias, for blind grading.

    A pre-agent step of the evaluate cell. Copies each candidate into
    ``record/blinded/<alias>/`` with its identity masked — ``predictor_id``
    becomes the alias, ``engine`` and ``model`` become null, ``process_version``
    is dropped, and every staged byte (the prose, ``retrieval.md``, and the
    captured transcript's strings) is scrubbed of predictor ids, evaluator ids,
    and engine/model names — and writes the alias map to ``--map-dir``.
    ``usage.json``, ``tooling.json``, and ``flags.json`` are not staged at all.
    ``record/`` is gitignored, so the masked copies never reach the ledger, and
    the map is written to ``--map-dir`` — outside the case tree, because the
    grader is sent into that tree and its key must not be found by an ``ls``
    nobody had to intend.

    Aliases are assigned by a keyed shuffle seeded on the run, case, and event —
    never predictor-id sort order, which would make the alias a bijection any
    reader could invert. Deterministic, so a re-run of the same cell assigns the
    same aliases.

    Exits 1 when the event carries no prediction: an evaluate cell with nothing
    to score is a matrix fault, and an empty staging area would have the grader
    write an empty cell instead of failing.

    The paired step is ``unblind-evaluations``, which must run **before**
    ``stamp-cell --role evaluator`` — see its help.
    """
    settings = get_settings()
    try:
        result = blinding.provision_blinded_predictions(
            data_root=settings.data_root,
            config_root=settings.config_root,
            court=court,
            docket=docket,
            event_id=event,
            run_id=run_id,
            map_dir=map_dir,
        )
    except blinding.BlindingError as exc:
        typer.echo(f"blinding failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    for candidate in result.candidates:
        typer.echo(f"{candidate.alias} <- {len(candidate.staged)} file(s)")
    typer.echo(f"blinded {len(result.candidates)} candidate(s) -> {result.root}")


@app.command("unblind-evaluations")
def unblind_evaluations_cmd(
    court: Annotated[str, typer.Option()],
    docket: Annotated[int, typer.Option()],
    event: Annotated[str, typer.Option(help="The resolved event that was graded.")],
    evaluator: Annotated[str, typer.Option(help="The evaluator id whose output is un-aliased.")],
    run_id: Annotated[str, typer.Option(help="The evaluate run id the map was minted under.")],
    map_dir: Annotated[
        Path,
        typer.Option(
            help="Where the alias map is written/read. Deliberately outside the "
            "case tree the grader is told to open; point it at a runner-local "
            "path (e.g. the runner temp dir) in CI.",
        ),
    ] = blinding.DEFAULT_MAP_DIR,
) -> None:
    """Rename an evaluate cell's alias-keyed output onto the real predictor ids.

    The other half of ``provision-blinded-predictions``. Reads the alias map
    from ``--map-dir`` (pass the same value both commands were given), moves each
    ``evaluations/<evaluator>/<alias>/<run>/`` to
    ``evaluations/<evaluator>/<predictor_id>/<run>/``, rewrites the
    ``predictor_id`` field inside each ``evaluation.json``, and resolves every
    alias the evaluator wrote into its prose, flags, tooling report, and captured
    log — a `likely`-leakage note naming ``candidate-b`` would otherwise reach a
    maintainer through the run PR with its only key thrown away with the runner.

    **This must run before ``stamp-cell --role evaluator``.** The stamp joins an
    evaluation to the prediction it scored on the ``predictor_id`` field and
    returns nothing on no match, so an alias reaching the stamp costs the cell
    its ``claim_scores`` block *silently* — the stamp assigns whatever the join
    produced rather than failing — while a ``risk_set`` base rate left with no
    ``base_rate_salience_version`` fails the stamp outright. The self-check for
    the silent half is
    ``validate data``'s ``check_evaluation_targets``, which resolves the same
    join and reports an orphan loudly — so the cell's order is: un-alias, stamp,
    validate.

    Idempotent over an already-un-aliased cell. Exits 1 on anything else — a
    missing or corrupt map, a map minted for another cell, an alias the map does
    not name, a destination that already exists, or an alias-shaped directory
    surviving the sweep — because degrading would ship alias-keyed evaluations
    into the ledger.
    """
    settings = get_settings()
    try:
        moved = blinding.unblind_evaluations(
            data_root=settings.data_root,
            court=court,
            docket=docket,
            event_id=event,
            evaluator_id=evaluator,
            run_id=run_id,
            map_dir=map_dir,
        )
    except blinding.BlindingError as exc:
        typer.echo(f"un-aliasing failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    for alias, predictor_id in moved:
        typer.echo(f"{alias} -> {predictor_id}")
    typer.echo(f"un-aliased {len(moved)} evaluation(s) for {evaluator}")


@app.command("hide-cell-record")
def hide_cell_record_cmd(
    stash_dir: Annotated[
        Path,
        typer.Option(
            help="Where the hidden trees are moved to. Point it outside the "
            "checkout — a runner-local path such as the runner temp dir — so "
            "the tree the grader browses does not contain its own hiding place.",
        ),
    ],
) -> None:
    """Move every committed ``predictions/``/``evaluations/`` tree out of the working tree.

    The blinding bracket's second pre-agent step, run **after**
    ``provision-blinded-predictions`` (which reads the committed predictions to
    stage them). The blinding hands the grader opaque aliases, and then a plain
    ``ls`` of the ledger names every predictor one directory above the staging
    area — before the agent has read the contract that forbids that tree. This
    moves both trees to ``--stash-dir`` for the duration of the run;
    ``restore-cell-record`` puts them back.

    Repo-wide, so it needs no cell coordinates and cannot be mis-keyed onto the
    wrong event, and because a predictor's prose on another case identifies it
    too. Only those two directory names, only directly under an event: the
    gitignored ``record/`` tree the grader *is* sent to read is out of reach by
    construction.

    This narrows the accidental surface, not the deliberate one — the checkout
    carries full history, so the hidden bytes stay one ``git show`` away, under
    the prompt's prohibition and the logged-tool-call audit.

    Exits 1 before moving anything when the stash already holds a manifest — any
    earlier hide, restored or not, since a second sweep over an emptied tree
    would move nothing and overwrite the one record of the first — and exits 1
    after the sweep when it hid **nothing**, which a wrong data root or working
    directory would otherwise turn into a green run that left the grader the
    whole committed record.
    """
    settings = get_settings()
    try:
        hidden = blinding.hide_committed_cells(data_root=settings.data_root, stash_dir=stash_dir)
    except blinding.BlindingError as exc:
        typer.echo(f"hiding failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"hid {len(hidden)} committed cell tree(s) -> {stash_dir}")


@app.command("restore-cell-record")
def restore_cell_record_cmd(
    stash_dir: Annotated[
        Path,
        typer.Option(help="The stash `hide-cell-record` wrote; pass the same value."),
    ],
) -> None:
    """Move the hidden cell trees back into the working tree.

    The other half of ``hide-cell-record``, and it runs the moment the agent
    stops — before the usage/retrieval capture, the un-aliasing, the stamp, and
    ``validate`` — so every later step sees a whole workspace rather than each
    one having to know what was hidden.

    Restores file by file and **refuses to overwrite**: the grader writes its
    own ``evaluations/<evaluator>/<alias>/<run>/`` under a hidden tree's path
    while it is hidden, so a directory-level replace would delete the cell's
    output. The agent's bytes always win, and a collision exits 1 rather than
    resolving silently.

    Exits 1 on a missing or malformed manifest, on a manifest minted against a
    different data root, and on a stashed tree that is no longer there — a cell
    that continued with committed data missing would fail the stamp's prediction
    join and ``validate``'s evaluation-target check with no sign of why.
    """
    settings = get_settings()
    try:
        restored = blinding.restore_committed_cells(
            data_root=settings.data_root, stash_dir=stash_dir
        )
    except blinding.BlindingError as exc:
        typer.echo(f"restoring failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"restored {restored} file(s) from {stash_dir}")


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
        # The sidecar counterpart of the fixed set: three reads through the
        # same client a cell's `service` backend forwards with (the service
        # exposes query and open-events; snapshot provisioning is not a cell
        # surface), the third the full-query probe that fails when an
        # opinion-bearing row hydrates no body.
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

    It also checks the registry manifest's recorded ``tools`` against what the
    server advertises. That list is the offered denominator every retrieval log
    snapshots and is captured by hand at pin time, so this is what stops a
    version bump from leaving it silently wrong.

    Exits 2 when the endpoint cannot be probed at all (a setup problem), 1
    when the protocol disappoints (no server name, no tools), the manifest has
    drifted from the server, or the budget blows.
    """
    expected: list[str] = []
    registry = get_settings().config_root / "predictors.yaml"
    if registry.exists():
        expected = sorted({tool for server in load_mcp_servers(registry) for tool in server.tools})
    try:
        report = integration_check.run_mcp_check(
            mcp_url=url, budget_seconds=budget_seconds, expected_tools=expected
        )
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
            help="Engine backend, one of "
            + " | ".join(available_backends())
            + ". stub is offline and the default; replay is also offline, emitting "
            "a recorded cassette."
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

    An event.yaml already present at the ledger path is **never rewritten**:
    the committed record stands, data PRs are additive-only (the path jail
    rejects any modification), and the corpus row moves — a field populated
    after the file was committed would otherwise ride into every later cell's
    run PR as a jailed modification. When the corpus projection differs from
    the committed file the drift is warned, field by field; the warning is the
    accepted steady state (the deterministic outcome writer refreshes the
    definition at resolution on its own lane), and a wholesale ledger backfill
    would be a one-time migration, not a cell command. ``--out`` still writes
    wherever it points, unconditionally.
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
    projected = PredictableEvent(
        event_id=match.event_id,
        case_id=match.case_id,
        kind=match.kind,
        stage=match.stage,
        moment=match.moment,
        title=match.title,
        description=match.description,
        docket_entry_id=match.docket_entry_id,
        opened_at=match.opened_at,
        decision_target=match.decision_target,
        resolved=match.resolved,
    )
    if out is None and dest.is_file():
        # Never rewrite the committed record (see the docstring); surface drift
        # instead, so a stale projection is a visible fact rather than a jailed
        # modification in the next run PR. Two volumes on purpose: the fields a
        # consumer keys behavior on get a ::warning:: annotation, while
        # cosmetic drift — upstream caption re-renderings move `title` on most
        # of the committed ledger, and a schema bump would move
        # `schema_version` on all of it — stays a plain log line, or the
        # annotation channel would drown the one drift that matters. An
        # unreadable committed file degrades to the loud marker rather than
        # failing the cell: `validate` owns rejecting a malformed ledger, and
        # a materialize crash here would spend nothing but lose the cell.
        try:
            committed_fields = read_model(dest, PredictableEvent).model_dump(mode="json")
            projected_fields = projected.model_dump(mode="json")
            drifted = sorted(
                field
                for field, value in projected_fields.items()
                if committed_fields.get(field) != value
            )
        except (OSError, ValueError, yaml.YAMLError):
            drifted = ["<unreadable committed file>"]
        cosmetic = {"title", "description", "schema_version"}
        loud = [field for field in drifted if field not in cosmetic]
        quiet = [field for field in drifted if field in cosmetic]
        if loud:
            typer.echo(
                f"::warning::{case} event {event}: the corpus projection drifted from "
                f"the committed event.yaml on {', '.join(loud)}; leaving the "
                f"committed file untouched (a backfill is a migration, not a cell step)",
                err=True,
            )
        if quiet:
            typer.echo(
                f"{case} event {event}: cosmetic drift on {', '.join(quiet)} "
                f"(committed file untouched)",
                err=True,
            )
        typer.echo(f"{case} event {event} already materialized -> {dest}")
        return
    write_yaml(dest, projected)
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
            "deterministically recordable; surfaced on the pipeline-runs dashboard)."
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
    # Re-derive owed gradings from the ledger, on top of this poll's fresh
    # resolutions. `already_queued` keeps a case the poll just queued from being
    # double-queued here.
    evaluate_cfg = load_evaluate_config(settings.config_root)
    evaluate_backlog(
        db,
        settings.data_root,
        settings.config_root / "evaluators.yaml",
        queues,
        cap=evaluate_cfg.backlog_cases_per_cycle,
        max_attempts=evaluate_cfg.max_attempts_per_cell,
        already_queued={f"{e['court']}/{e['docket']}" for e in queues.evaluate},
    )
    _ensure_corpus_layout(db)
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    unrecorded_out.write_text(json.dumps(queues.unrecorded) + "\n")
    refreshed = len(due) - len(queues.failed) - len(queues.deferred)
    typer.echo(
        f"Refreshed {refreshed}/{cap} case(s){_format_refresh_failures(queues.failed)}; "
        f"queued {len(queues.predict)} predict, {len(queues.evaluate)} evaluate"
        + (
            f" ({queues.evaluate_from_backlog} from backlog)"
            if queues.evaluate_from_backlog
            else ""
        )
        + f", {len(queues.unrecorded)} unrecorded"
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
            "deterministically recordable; surfaced on the pipeline-runs dashboard)."
        ),
    ] = Path("unrecorded-queue.json"),
    term: Annotated[
        int | None,
        typer.Option(
            help="Two-digit docket Term to probe for new filings (default: the "
            "Term the Clerk is numbering today — it rolls in July, ahead of "
            "the October Term; see current_docket_term)."
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
    Discovery probes the Term's numbering frontier across the paid, IFP, and
    application streams from the persisted per-(Term, stream) cursors and
    onboards each served petition or application — and, for a window after the
    July numbering roll, the outgoing Term too, so its late tail is caught; the
    refresh re-polls the pending
    modern-cert watchlist (recent Terms first), then the application rotation
    re-polls unresolved interim applications under its own cap — queueing
    predict for a changed, still-unresolved substantive application in scope
    (daily-debounced), ground truth for the rest. Resolution is detected from
    the proceedings text, so a decided petition or application lands
    ``outcome.json`` deterministically. Writes the same three handoff queues
    as ``pull-all``.
    """
    settings = get_settings()
    live_cfg = load_live_config(settings.config_root)
    predict_cfg = load_predict_config(settings.config_root)
    scope = predict_cfg.scope
    salience_cfg = load_salience_config(settings.config_root)
    cap = live_cfg.max_cases_per_run if limit is None else min(limit, live_cfg.max_cases_per_run)
    deadline = time.monotonic() + max_run_seconds if max_run_seconds is not None else None
    today = date.today()
    probe_term = term if term is not None else current_docket_term(today)
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
            # The selection sweep's per-cell owed check reads the predictor
            # registry and the predict-side attempt cap (see salience_sweep).
            predictors_path=settings.config_root / "predictors.yaml",
            predict_max_attempts=predict_cfg.max_attempts_per_cell,
            today=today,
            deadline=deadline,
        )
    evaluate_cfg = load_evaluate_config(settings.config_root)
    evaluate_backlog(
        db,
        settings.data_root,
        settings.config_root / "evaluators.yaml",
        queues,
        cap=evaluate_cfg.backlog_cases_per_cycle,
        max_attempts=evaluate_cfg.max_attempts_per_cell,
        already_queued={f"{e['court']}/{e['docket']}" for e in queues.evaluate},
        today=today,
    )
    _ensure_corpus_layout(db)
    out.write_text(json.dumps(queues.predict) + "\n")
    evaluate_out.write_text(json.dumps(queues.evaluate) + "\n")
    unrecorded_out.write_text(json.dumps(queues.unrecorded) + "\n")
    discovery_failed = f" ({len(discovery.failed)} stream error(s))" if discovery.failed else ""
    typer.echo(
        f"Live cycle (OT{probe_term:02d}): onboarded {len(discovery.onboarded)} new petition(s)"
        f"{discovery_failed}{_format_refresh_failures(queues.failed)}; "
        f"queued {len(queues.predict)} predict, {len(queues.evaluate)} evaluate"
        + (
            f" ({queues.evaluate_from_backlog} from backlog)"
            if queues.evaluate_from_backlog
            else ""
        )
        + f", {len(queues.unrecorded)} unrecorded"
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
        + (
            f" ({len(queues.predict_skipped_relist_cooldown)} relisted case(s) held on cooldown)"
            if queues.predict_skipped_relist_cooldown
            else ""
        )
        + "."
    )
    for skipped in (*queues.predict_skipped_decided, *queues.predict_skipped_relist_cooldown):
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


@dataclass(frozen=True)
class _DropRecord:
    """One case, event, or cell a planning step held back, with that step's reason.

    The reason string is the dropping step's own — printed verbatim, never
    re-worded here — so a plan that reports the wrong cell set names the step
    that decided it. ``event_id`` and ``actor_id`` are absent where the step
    works at a coarser grain: the scope gate drops whole cases — except where
    cohort completion keeps one narrowed, whose lost events are event-grained —
    and the forecastability re-check drops whole events. ``actor_id`` is the predictor or
    evaluator whose cell the drop cost, the same union
    :class:`fedcourtsai.collect.ExpectedCell` calls an actor.
    """

    case_id: str
    reason: str
    event_id: str | None = None
    actor_id: str | None = None

    def as_json(self) -> dict[str, str]:
        """The record as a plan-JSON object, omitting the grains it has none of."""
        out = {"case_id": self.case_id, "reason": self.reason}
        if self.event_id is not None:
            out["event_id"] = self.event_id
        if self.actor_id is not None:
            out["actor_id"] = self.actor_id
        return out


@dataclass
class _ResolveReport:
    """What event resolution decided, for a plan to report.

    ``unforecastable`` is the re-check's per-event drops. ``no_default_events``
    is the quieter class beside it: a case that listed no events and whose
    default lookup came back empty, which resolves to a case carrying zero
    events rather than to a drop — invisible in a case count and invisible in
    an event count, so it is named here instead.
    """

    unforecastable: list[_DropRecord] = field(default_factory=list)
    no_default_events: list[_DropRecord] = field(default_factory=list)


def _resolve_cases(
    cases: list[CaseRequest],
    default_events: Callable[[str, int], list[str]],
    *,
    drop_unforecastable: Callable[[str, int], Mapping[str, str]] | None = None,
    stage: str,
    report: bool,
    report_out: _ResolveReport | None = None,
) -> list[CaseRequest]:
    """Fill in each case's default events when the request listed none.

    ``drop_unforecastable`` re-checks a request's *listed* events against the
    corpus at plan time, returning ``{event_id: reason}`` for the ones the
    corpus now refuses. The listing is what makes the re-check necessary: a
    case with no events runs through selection, which applies every
    forecastability rule, while a listed event skips selection entirely — and a
    trigger issue is written when its events are forecastable and fanned out
    whenever the workflow runs, with a pipeline pause free to put an arbitrary
    gap between the two. Without the re-check the stale listing mints cells
    provisioning must then refuse one by one; with it each event is dropped
    here, once, with its own reason on the record (printed verbatim, so a new
    refusal class needs no second annotation site). An event the callback does
    not name stays listed, because the matrix trusts the trigger's event ids
    and the provisioning record gate backs the trust. The predict matrix passes
    :func:`fedcourtsai.store.unforecastable_listed_events`; evaluate passes
    ``None``, since its listed events are exactly the resolved ones.

    ``stage`` labels the warning lines and ``report`` is the minting path — a
    plan passes ``False`` and suppresses the annotations, carrying the same
    drops in ``report_out`` for its JSON instead. Both are keyword-required:
    a caller that has to name its stage cannot inherit another command's label
    by omission.
    """
    kept: list[CaseRequest] = []
    for c in cases:
        if not c.events:
            resolved = tuple(default_events(c.court, c.docket))
            if not resolved and report_out is not None:
                report_out.no_default_events.append(
                    _DropRecord(
                        ids.case_id(c.court, c.docket),
                        "the request listed no events and the corpus resolved none for this "
                        "case, so it contributes no cells",
                    )
                )
            kept.append(replace(c, events=resolved))
            continue
        if drop_unforecastable is None:
            kept.append(c)
            continue
        refused = drop_unforecastable(c.court, c.docket)
        gone = {e: refused[e] for e in c.events if e in refused}
        for dropped, reason in sorted(gone.items()):
            if report:
                typer.echo(
                    f"::warning::{stage}: dropped {dropped} on {c.court}/{c.docket} — {reason}",
                    err=True,
                )
            if report_out is not None:
                report_out.unforecastable.append(
                    _DropRecord(ids.case_id(c.court, c.docket), reason, event_id=dropped)
                )
        kept.append(replace(c, events=tuple(e for e in c.events if e not in gone)))
    return kept


def _cohort_narrowing_reason(data_root: Path, court: str, docket: int, event_id: str) -> str:
    """Why cohort completion left this listed event behind, in its own words.

    The two bounds refuse for opposite reasons and a single sentence can only
    state one of them truthfully: an event with no prediction at all would be
    **new spend** on a case the funding gate declined, while an event whose
    whole cohort sits outside the frozen process scope has predictions and is
    refused on **comparability** — completing it would leave a board an event
    scored on the completing engine alone. This string reaches a maintainer
    through the plan's approval report, so it names the ground that actually
    applied.
    """
    if event_has_predictions(data_root, court, docket, event_id):
        return (
            "narrowed away on a salience-deferred case kept for cohort completion: this "
            "event's whole cohort sits outside the frozen process scope, so a freshly "
            "stamped cell would not complete a comparison but leave a board an event "
            "scored on one engine alone."
        )
    return (
        "narrowed away on a salience-deferred case kept for cohort completion: no committed "
        "prediction on this event, so a cell here would be new spend rather than a missing "
        "engine."
    )


def _scope_filtered(
    cases: list[CaseRequest],
    scope: PredictScope,
    corpus_root: Path,
    corpus_backend: corpus.CorpusBackend,
    *,
    for_grading: bool = False,
    data_root: Path | None = None,
    dropped_out: list[_DropRecord] | None = None,
    cohort_narrowed_out: list[_DropRecord] | None = None,
) -> list[CaseRequest]:
    """Drop out-of-scope cases under ``scotus_docket``; the matrix backstop.

    ``for_grading`` is the evaluate matrix's reading: the salience-deferred
    skip does not apply, because selection decides which cases *earn new
    cells*, never whether a committed prediction is scored — a prediction on
    a case whose latch was since cleared (``unlatch-overselected``) must
    still be graded when its event resolves, exactly the stranding
    ``pipeline.pull.evaluate_backlog`` refuses to cause. The hard exclusions
    (court, ``predict_excluded``, the shared reason rules) still apply on
    both readings.

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
    file, or the resolved pointer read in place over ``ranged``. The matrix is
    built from the *specific* cases the trigger issue names, so gating is a
    handful of point lookups (each case's row, and a latest-snapshot lookup only
    for a bare-import row), which the ranged backend serves in KBs — no full
    pull. Under ``local`` the database must be on disk: if it is absent the gate
    cannot distinguish "case not eligible" from "corpus never provisioned"
    (:func:`corpus.connect` would silently create an empty database and drop
    *every* case, an empty matrix that looks like a normal "nothing in scope"
    result), so fail loud. Under ``ranged`` the resolved pointer + remote URL
    stand in for the file, and a missing pointer/URL fails loud in
    :func:`corpus.connect_readonly` itself.

    ``data_root`` enables the **cohort-completion** reading of the salience
    drop, the plan-time mirror of the live sweep's carve-out: a deferred case
    whose listed events hold a cohort a claimable board will count once the
    event resolves and is graded
    (:func:`fedcourtsai.store.event_has_claimable_prediction`) is kept, narrowed
    to exactly those events, because finishing such a cohort buys only the
    missing engines on a case the project already funded. Everything else about
    the case goes with the drop — its unpredicted events, which would be new
    spend on a case the funding gate declined, and its events whose whole cohort
    sits outside the frozen process scope, where a freshly-stamped cell would
    not complete a comparison but manufacture a one-engine one. A deferred case
    with no qualifying listed event is dropped as before, and so is one whose
    request lists no events at all: an unlisted request means "resolve this
    case's defaults", which is a request for new cells, not for a cohort.
    Without ``data_root`` (the evaluate reading, which ``for_grading`` already
    exempts from the salience drop) the carve-out is off.

    ``dropped_out`` collects each skipped case as a structured record carrying
    the same reason the stderr note prints, so a plan can attribute a missing
    case to this step. ``cohort_narrowed_out`` is the same channel for the
    narrowing's *event* casualties: a kept-narrowed case appears in no drop
    list, so without a record of its own the plan's machine-readable output
    would show a listed event simply gone — and the approval report a
    maintainer reads at the spend hold is built from that output, not from
    stderr.
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
            drop: str | None
            if row is None or row.court != "scotus":
                drop = "out of prediction scope (predict.scope=scotus_docket, not a SCOTUS docket)."
            elif row.predict_excluded:
                drop = "latched out of predict scope by the corpus reconcile."
            elif (reason := corpus.out_of_scope_reason_full(conn, row)) is not None:
                drop = f"{reason}."
            elif (
                not for_grading
                and corpus.is_salience_deferred(row)
                and not corpus.has_open_merits_event(conn, row.case_id)
            ):
                # The merits bypass: a below-cap petition still earns no cert
                # cell, but once the Court grants it the funding question is a
                # different one and the gate no longer answers it.
                drop = "not selected this salience round (scored, below the capacity slice)."
                if data_root is not None and (
                    cohort := tuple(
                        event_id
                        for event_id in case.events
                        if event_has_claimable_prediction(
                            data_root, case.court, case.docket, event_id
                        )
                    )
                ):
                    # Cohort completion: these events were funded and predicted
                    # already, so the missing engines are the only spend left on
                    # them. `predict_matrix`'s per-(predictor, event) skip mints
                    # exactly those; the narrowing here is what keeps the case's
                    # *unpredicted* events out of the fan-out entirely.
                    typer.echo(
                        f"Narrowing {case.court}/{case.docket}: {drop} Kept "
                        f"{len(cohort)} of {len(case.events)} listed event(s) for "
                        f"cohort completion ({', '.join(cohort)}).",
                        err=True,
                    )
                    if cohort_narrowed_out is not None:
                        # Each event the narrowing took away, as its own record:
                        # the case is kept, so it appears in no drop list, and
                        # without this the plan's only machine-readable channel
                        # would show a listed event simply gone. The reason is
                        # per event because the two bounds refuse for opposite
                        # reasons, and this string is what a maintainer reads in
                        # the approval report.
                        cohort_narrowed_out.extend(
                            _DropRecord(
                                ids.case_id(case.court, case.docket),
                                _cohort_narrowing_reason(
                                    data_root, case.court, case.docket, event_id
                                ),
                                event_id=event_id,
                            )
                            for event_id in case.events
                            if event_id not in cohort
                        )
                    kept.append(replace(case, events=cohort))
                    continue
            else:
                drop = None
            if drop is None:
                kept.append(case)
                continue
            typer.echo(f"Skipping {case.court}/{case.docket}: {drop}", err=True)
            if dropped_out is not None:
                dropped_out.append(_DropRecord(ids.case_id(case.court, case.docket), drop))
    return kept


def _evaluate_backlog_cases() -> list[CaseRequest]:
    """The evaluate stage's own case set, derived from the corpus-level backlog.

    What a scheduled evaluate run fans out over when no trigger names its cases:
    the gradings committed state still owes — a resolved event with a committed
    prediction and at least one enabled evaluator's evaluation missing (see
    :func:`fedcourtsai.pipeline.pull.derive_evaluate_backlog`, whose caps this
    takes from ``tracking.yaml``'s ``evaluate`` section).

    Stamp-free, deliberately. The pull lane's use of the same deriver writes
    ``evaluate_queued_at`` to debounce itself, but that is a write to the corpus
    of record, and those credentials live only in the writer jobs — a scheduled
    evaluate run has none, so a stamp it made would die with the runner. It
    needs none either: the fan-out's already-graded gate is the idempotency, and
    it reads the same committed ledger the deriver does. Re-deriving an
    unchanged backlog re-mints nothing once the gradings are committed, because
    a graded cell is dropped; a cell that has *not* been graded is work still
    owed and should re-mint. Two consequences to hold in view. The debounce is
    one-directional — this lane honours a stamp the pull lane wrote, but leaves
    none of its own, so it cannot hold the pull lane off a case it just queued.
    And the gate reads *committed* state, so it cannot see a run whose collect
    PR has not merged; what bounds a second derivation firing into that window
    is the workflow's concurrency group, not this gate.

    Requires a **pulled** corpus, and enforces it. The scan is one pass over
    every resolved event plus a point query per candidate case — tens of
    thousands of them — which is the opposite shape from the point lookups a
    trigger's named cases need, and so the opposite backend: served locally in
    seconds, it would be a range-request storm read in place. A non-local
    backend is refused here rather than left to be discovered as a slow run.
    An absent corpus is refused for the same reason in reverse — for an
    unattended lane, "nothing is owed" and "no corpus" must not be the same
    output.
    """
    settings = get_settings()
    evaluate_cfg = load_evaluate_config(settings.config_root)
    db_path = corpus.corpus_db_path(settings.corpus_root)
    if settings.corpus_backend != "local":
        raise typer.BadParameter(
            f"the evaluate backlog cannot be derived over the "
            f"{settings.corpus_backend!r} corpus backend: it scans every resolved "
            "event and reads a row per candidate case, which the local (pulled) "
            "corpus serves and a read-in-place backend does not. Pull the corpus "
            "and read local, or name the cases with --body-file."
        )
    if not db_path.exists():
        raise typer.BadParameter(
            f"no corpus at {db_path} to derive the evaluate backlog from — "
            "`fedcourts corpus-pull` first. Refusing rather than planning an "
            "empty fan-out, which is indistinguishable from a drained backlog."
        )
    with corpus.connect_readonly(db_path, backend=settings.corpus_backend) as conn:
        backlog = derive_evaluate_backlog(
            conn,
            settings.data_root,
            settings.config_root / "evaluators.yaml",
            cap=evaluate_cfg.backlog_cases_per_cycle,
            max_attempts=evaluate_cfg.max_attempts_per_cell,
        )
    return [CaseRequest(entry.court, entry.docket, entry.events) for entry in backlog.entries]


def _requested_cases(
    body_file: Path | None,
    court: str,
    docket: int | None,
    event: list[str] | None,
    *,
    backlog: bool = False,
    force: bool = False,
) -> list[CaseRequest]:
    """Cases to fan out over, from a batch body file, single-case flags, or the backlog.

    ``--body-file`` (one ``{court, docket, events}`` object or a JSON array of
    them) is the multi-case path a trigger issue takes. The single-case
    ``--court``/``--docket``/``--event`` flags serve ad-hoc invocations.

    ``backlog`` opens a third mode for the evaluate stage, whose schedule is its
    own: given *no* input at all, the cases come from the corpus-level evaluate
    backlog (:func:`_evaluate_backlog_cases`) rather than from a trigger, so a
    run needs no issue body to know what it owes. The predict stage has no such
    deriver — its case set is a funded salience selection, not a level on
    committed state — so it leaves ``backlog`` unset and an input-less
    invocation is refused.

    A *half*-named single case is refused in every mode. Silence is the backlog
    mode's trigger, so a dropped ``--docket`` would otherwise turn one intended
    case into the whole backlog — the one typo whose blast radius is a fan-out.

    ``force`` is refused with the backlog, because the two select opposite sets.
    A re-grade is deliberate and names its target; the backlog is what committed
    state still owes, and it drops a fully-graded case *before* the gate
    ``--force`` disables ever sees it. Accepting the pair would answer a re-grade
    request with an empty fan-out — the flag reading as honoured while selecting
    nothing.
    """
    if body_file is not None:
        return parse_cases(body_file.read_text())
    if court and docket is not None:
        return [CaseRequest(court, docket, tuple(event or ()))]
    if court or docket is not None:
        raise typer.BadParameter("--court and --docket go together; provide both or neither.")
    if backlog:
        if event:
            raise typer.BadParameter(
                "--event names events within a single case; pass it with --court and --docket. "
                "The backlog derives its own events per case."
            )
        if force:
            raise typer.BadParameter(
                "--force re-grades cases you name; it cannot re-grade the backlog, which "
                "excludes a fully-graded case before the already-graded gate --force "
                "disables. Name the target with --body-file, or --court and --docket."
            )
        return _evaluate_backlog_cases()
    raise typer.BadParameter("provide --body-file, or both --court and --docket.")


def _spend_gate_or_empty(stage: str) -> SpendVerdict:
    """The ex-post spend backstop, consulted before either stage mints a matrix.

    Returns the verdict so the caller can emit an empty matrix on a breach —
    deferring, never destroying: the trigger's cases stay in their queue and
    re-derive next cycle, exactly as under the volume cap. Reports on the same two
    channels as the other plan-time gates (a workflow-command line on stderr, and
    the step summary inside Actions), never on stdout, which carries only the
    matrix JSON.

    Disabled at the code default (a ceiling of ``0``), in which case this is
    silent and the ledger is never read; the shipped ``config/tracking.yaml``
    arms it ($2,500 over a trailing 30 days). See :mod:`fedcourtsai.spend` for
    what the ceiling can and cannot promise — chiefly that the ledger lags by
    however long a collect PR takes to merge, so it is a floor on spend rather
    than a live figure.
    """
    settings = get_settings()
    verdict = check_spend(settings.data_root, load_spend_config(settings.config_root))
    if not verdict.breached:
        return verdict
    typer.echo(
        f"::error::{stage}: spend backstop reached — ${verdict.spent_usd:.2f} recorded over the "
        f"trailing {verdict.window_days} day(s) across {verdict.cells} cell(s), at or above the "
        f"${verdict.ceiling_usd:.2f} ceiling, so no cells are minted this run. The queued work is "
        f"untouched and re-runs once the window rolls off or the ceiling is raised "
        f"(spend.ceiling_usd). NOTE: the ledger only counts cells whose collect PR has merged, so "
        f"actual spend is at least this.",
        err=True,
    )
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(
                f"## {stage} — spend backstop reached, no cells minted\n"
                f"Recorded **${verdict.spent_usd:.2f}** over the trailing "
                f"{verdict.window_days} day(s) across {verdict.cells} cell(s), at or above the "
                f"**${verdict.ceiling_usd:.2f}** ceiling (`spend.ceiling_usd`). Queued work is "
                f"deferred, not dropped — it re-runs once the window rolls off or the ceiling is "
                f"raised. The ledger counts only cells whose collect PR has merged, so actual "
                f"spend is at least this figure.\n"
            )
    return verdict


def _forward_claim_from(run: StratifiedRun) -> ForwardClaimRecord:
    """The published record for one stratify pass — pairs, denominator and all."""
    return forward_claim_record(
        [(cell.evaluation.predictor_id, cell.reason) for cell in run.excluded],
        run.claimed_forward,
    )


def _report_uneven_coverage(board: Leaderboard) -> None:
    """Warn where a population's predictors were not scored on the same events.

    Grading is gated at ``(evaluator, event)`` grain, so the scored set is
    *selected*: a prediction committed after a judge graded its event is never
    scored by that judge, and an engine whose cells backfill late is compared
    over a subset of the population's events. The ranks and means make no
    adjustment for that, so two entries at unequal coverage are not a
    cross-engine comparison at all. The board carries the counts; this makes the
    inequality itself loud at build time, so a comparability hazard does not
    wait for a reader to do the subtraction. It stays silent on equal coverage,
    which is not the same as endorsing the comparison: equality certifies the
    same event set and neither the stratum mix nor the panel depth, both of
    which the board publishes for the reader to check.

    Every population is checked against **its own** denominator — the ranked
    cert board and each ``stage@moment`` block — because a stage is scored on
    its own events, and measuring a merits entry against the cert union would
    report short coverage for every one of them.
    """
    populations: list[tuple[str, int, Sequence[LeaderboardStageEntry | LeaderboardEntry]]] = [
        ("cert", board.events_scored, board.entries)
    ]
    populations += [
        (key, board.stages[key].events_scored, board.stages[key].entries)
        for key in sorted(board.stages)
    ]
    for population, covered, entries in populations:
        short = [
            f"{entry.predictor_id} {entry.events_scored}/{covered}"
            for entry in entries
            if entry.events_scored < covered
        ]
        if not short:
            continue
        typer.echo(
            f"::warning::leaderboard [{population}]: unequal scored-set coverage — "
            + ", ".join(short)
            + ". Ranks and means make no adjustment for this; a cross-engine "
            "comparison over unequal coverage is over different populations.",
            err=True,
        )


def _report_forward_claim_exclusions(excluded: Sequence[ExcludedCell]) -> None:
    """One line per dropped cell, so the boards' count is never the only record."""
    for cell in excluded:
        ev = cell.evaluation
        typer.echo(
            f"::warning::forward-claim exclusion: {ev.case_id} {ev.event_id} "
            f"{ev.predictor_id} (graded by {ev.evaluator_id}) — {cell.reason}",
            err=True,
        )


def _report_predict_cap(capped: CappedMatrix, max_cells: int) -> None:
    """Surface a volume-cap deferral loudly, so a capped run is never silent.

    Two channels, both from here so no workflow change is needed: a ``::warning::``
    workflow-command line on stderr (an Actions annotation, and loud in any plain
    log), and — when ``$GITHUB_STEP_SUMMARY`` is set, i.e. inside Actions — a
    Markdown block appended to the plan job's summary. stdout stays the pure
    matrix JSON the plan step captures, so the warning must never go there. The
    wording says *deferred*, not dropped: the overflow cases keep their place in
    the predict queue and re-run next cycle.

    **All-deferred coupling.** When the cap defers *every* case (the kept matrix
    is empty because of the cap, not scope — reachable when the single
    lowest-``case_id`` case alone exceeds the cap, i.e. a pathological many-event
    case or a misconfigured tiny ``max_predict_cells_per_run``), the plan reports
    ``has_jobs=false`` and the workflow's empty-matrix step closes the trigger
    issue with an *out-of-scope* message — cap-empty and scope-empty are
    indistinguishable to that YAML step. So emit a distinct, escalated
    ``::error::`` here that names the cap as the cause, so the misattributed
    close is never the only record. It is still safe: the deferred cases stay in
    the corpus predict queue and re-queue next cycle regardless of the issue
    close.
    """
    cases = ", ".join(capped.dropped_cases)
    if not capped.include:
        # All cases deferred by the cap: escalate past the normal warning, because
        # the workflow's empty-matrix step will close the trigger issue with the
        # generic out-of-scope note (it cannot tell cap-empty from scope-empty).
        # This line is the correctly-attributed record; the close is harmless
        # because the deferred cases persist in the predict queue (see docstring).
        typer.echo(
            f"::error::predict-matrix: volume cap deferred ALL {len(capped.dropped_cases)} "
            f"case(s) this run — nothing fits under the {max_cells}-cell backstop, so the "
            f"matrix is empty and the trigger issue will close as if out of scope. The cases "
            f"remain queued and re-run next cycle ({cases}). Raise "
            f"predict.max_predict_cells_per_run or split the trigger if this is unexpected.",
            err=True,
        )
    else:
        typer.echo(
            f"::warning::predict-matrix: volume cap hit — deferred {capped.dropped_cells} cell(s) "
            f"across {len(capped.dropped_cases)} case(s) over the {max_cells}-cell backstop; "
            f"they stay queued and re-run next cycle ({cases})",
            err=True,
        )
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(
                f"## run-predict — volume cap deferred {capped.dropped_cells} cell(s)\n"
                f"The scope-filtered matrix exceeded the {max_cells}-cell backstop "
                f"(predictor x case x event). Kept {len(capped.include)} cell(s); deferred "
                f"{len(capped.dropped_cases)} whole case(s): {cases}. Deferred cases stay in the "
                f"predict queue and re-run next cycle — nothing is dropped from the corpus.\n"
            )


_STRANDED_RERUN_CAVEAT = (
    "`--failed` is right when only `collect` failed; if that run also had failed *cells* it "
    "re-runs those too and a duplicate artifact name rejects their uploads, so rerun the "
    "`collect` job alone instead."
)
_STRANDED_OVERRIDE = (
    "The guard releases itself: a run leaves the census once its `collect` concludes success, "
    "and ages out of the 48-hour window regardless. To get a fresh run *sooner*, delete the "
    "stranded run's cell artifacts (`gh api -X DELETE "
    "repos/<owner>/<repo>/actions/artifacts/<artifact_id>`) and re-queue — an explicit act "
    "rather than a new trigger."
)


def _stranded_note(runs: Sequence[int]) -> str:
    """The trigger-issue close note for a run the guard withheld entirely."""
    reruns = "\n".join(f"    gh run rerun {run} --failed" for run in runs)
    return (
        "Every cell this run would have queued already ran in a run whose `collect` never "
        "succeeded — the predictions exist as cell artifacts; what is missing is the step that "
        f"commits them. Recover {'that run' if len(runs) == 1 else 'those runs'} rather than "
        "re-running this one, which would re-spend the same tokens on the same events — rerun "
        "the collect job:\n\n"
        f"{reruns}\n\n"
        f"{_STRANDED_RERUN_CAVEAT}\n\n"
        "Closing this issue loses nothing: an event with no committed prediction re-queues on a "
        f"later cycle regardless. {_STRANDED_OVERRIDE}\n"
    )


@dataclass
class _StrandedGuardReport:
    """What the stranded-run guard did on one pass, for a plan to report.

    A withheld count of zero is three different states, and only one of them is
    a reason to distrust the plan: the guard ran and matched nothing
    (``active``, no ``degraded_reason``), no census was supplied so the guard
    never ran (neither), or the census was unreadable and the guard failed open
    (a ``degraded_reason``, no ``active``). ``unparsed`` names census records
    the guard could not read, which leaves it *partly* blind even when active —
    a withheld count that is honest about the records it was able to match, and
    silent about the ones it was not.
    """

    active: bool = False
    degraded_reason: str | None = None
    unparsed: tuple[str, ...] = ()
    withheld: tuple[StrandedCell, ...] = ()

    def as_json(self) -> dict[str, Any]:
        """The guard's state as a plan-JSON block."""
        return {
            "active": self.active,
            "degraded_reason": self.degraded_reason,
            "unparsed_records": list(self.unparsed),
        }


def _report_stranded_guard(guarded: GuardedMatrix, note_file: Path | None, *, stage: str) -> None:
    """The minting path's record of what the stranded-run guard withheld.

    Three channels, all of them a run's record rather than a plan's: a
    ``::warning::`` per withheld cell carrying its own recovery command, the
    escalated ``::error::`` plus ``note_file`` close note when the guard emptied
    the matrix (the workflow's close step posts the note in place of its generic
    out-of-scope one), and the Actions step summary. Called only when something
    was actually withheld.
    """
    runs = sorted({cell.run_db_id for cell in guarded.withheld})
    run_list = ", ".join(str(run) for run in runs)
    for cell in guarded.withheld:
        typer.echo(
            f"::warning::{stage}: withheld {cell.predictor_id} "
            f"{ids.case_id(cell.court, cell.docket)} {cell.event_id} — its output already "
            f"sits in uncollected run {cell.run_db_id}; recover it with "
            f"`gh run rerun {cell.run_db_id} --failed` rather than re-spending the cell",
            err=True,
        )
    if not guarded.include:
        # Every cell withheld: the plan reports has_jobs=false, and the workflow's
        # close step would otherwise post its generic out-of-scope note. Write the
        # honest one for it to post instead, and escalate here so the cause is on
        # the record even if the note never reaches the issue.
        typer.echo(
            f"::error::{stage}: the stranded-run guard withheld ALL "
            f"{len(guarded.withheld)} cell(s) — every event this trigger names already ran in "
            f"uncollected run(s) {run_list}. Recover rather than re-run: "
            f"`gh run rerun {runs[0]} --failed`. {_STRANDED_RERUN_CAVEAT} " + _STRANDED_OVERRIDE,
            err=True,
        )
        if note_file is not None:
            try:
                note_file.write_text(_stranded_note(runs), encoding="utf-8")
            except OSError as exc:
                # An unwritable note costs the issue its honest close message,
                # never the run: the ::error:: above is already on the record.
                typer.echo(
                    f"::warning::{stage}: could not write the stranded-run close note to "
                    f"{note_file} ({exc}); the trigger issue closes with the generic note",
                    err=True,
                )
    else:
        typer.echo(
            f"::warning::{stage}: the stranded-run guard withheld "
            f"{len(guarded.withheld)} cell(s) whose output sits in uncollected run(s) "
            f"{run_list}; the remaining {len(guarded.include)} cell(s) are genuinely new",
            err=True,
        )
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(
                f"## run-predict — stranded-run guard withheld {len(guarded.withheld)} cell(s)\n"
                f"Their output already sits in uncollected run(s) {run_list}, whose `collect` did "
                f"not succeed: the tokens are spent and the predictions exist as cell artifacts. "
                f"Recover with `gh run rerun {runs[0]} --failed` rather than re-running this "
                f"trigger. {_STRANDED_RERUN_CAVEAT} Kept {len(guarded.include)} genuinely new "
                f"cell(s). {_STRANDED_OVERRIDE}\n"
            )


def _guarded_matrix(
    matrix: dict[str, list[dict[str, Any]]],
    stranded_file: Path | None,
    note_file: Path | None,
    *,
    stage: str,
    report: bool,
    guard_out: _StrandedGuardReport | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Withhold cells whose output sits in an uncollected run, and say so loudly.

    Fails **open** in every degraded direction — an unreadable census, an
    artifact name that does not parse — because the failure this guard prevents
    is expensive, not dangerous: a census the plan cannot trust must never be
    the reason a legitimate run does not start. Reports on the same channels as
    the other plan-time gates (workflow-command lines on stderr and the step
    summary; stdout carries only the matrix JSON), plus ``note_file`` when the
    guard empties the matrix, which the workflow's close step posts in place of
    its generic out-of-scope note.

    ``stage`` labels those lines. ``report`` is the minting path: a plan passes
    ``False``, which suppresses every workflow-command annotation and the step
    summary together, and carries the same facts in ``guard_out`` for its JSON
    instead — a fail-open the plan document does not name would read exactly
    like a guard that matched nothing.
    """
    guard = guard_out if guard_out is not None else _StrandedGuardReport()
    if stranded_file is None:
        return matrix
    try:
        census = read_stranded_census(stranded_file)
    except (OSError, ValueError) as exc:
        guard.degraded_reason = (
            f"{stranded_file} is unreadable ({exc}); cells already sitting in an "
            f"uncollected run may be re-minted"
        )
        if report:
            typer.echo(
                f"::warning::{stage}: the stranded-run guard is off — {stranded_file} is "
                f"unreadable ({exc}). Cells already sitting in an uncollected run may be "
                f"re-minted.",
                err=True,
            )
        return matrix
    guard.active = True
    guard.unparsed = census.unparsed
    if report:
        for name in census.unparsed:
            typer.echo(
                f"::warning::{stage}: stranded-run guard skipped the census record {name!r} — "
                "it does not read as a cell artifact naming predictor/court/docket/event, and a "
                "guessed reading would withhold the wrong cell",
                err=True,
            )
    guarded = drop_stranded_cells(matrix, census.cells)
    guard.withheld = guarded.withheld
    if not guarded.withheld:
        return matrix
    if report:
        _report_stranded_guard(guarded, note_file, stage=stage)
    return {"include": guarded.include}


@dataclass(frozen=True)
class _PredictFanout:
    """One pass of the predict planning pipeline, recorded step by step.

    Every field is one named step's output, so a fan-out that mints the wrong
    cells is attributable to the step that decided it rather than to the
    pipeline as a whole. ``capped.include`` is the surviving cell set — what
    ``predict-matrix`` emits and ``predict-plan`` reports without minting.
    """

    requested: list[CaseRequest]
    resolved: list[CaseRequest]
    scope_dropped: tuple[_DropRecord, ...]
    #: The events the scope gate's cohort-completion narrowing took off a
    #: salience-deferred case it kept. Its own field because the case is kept:
    #: it is in no drop list, and `requested` is the pre-gate listing, so
    #: without this the difference between the two is unattributed.
    cohort_narrowed: tuple[_DropRecord, ...]
    resolution: _ResolveReport
    guard: _StrandedGuardReport
    capped: CappedMatrix
    max_cells: int


def _predict_fanout(
    requested_cases: list[CaseRequest],
    run_id: str,
    *,
    stage: str,
    stranded_file: Path | None,
    note_file: Path | None,
    report: bool,
) -> _PredictFanout:
    """Run the predict planning pipeline: scope, forecastability, ledger, guard, cap.

    The one definition of what a predict run would mint, shared by
    ``predict-matrix`` (which emits the surviving cells as the Actions matrix)
    and ``predict-plan`` (which reports them and spends nothing), so the dry run
    can never describe a different fan-out than the minting command performs.

    ``report`` is the minting command's reading: it emits the workflow-command
    annotations and appends the volume cap's block to the Actions step summary.
    A plan passes ``False`` — its JSON carries every one of those facts, and an
    annotation from a run that mints nothing describes something that did not
    happen. Suppression is all-or-nothing on that flag, so no plan-run log ever
    carries a partial set. ``note_file`` is the other write, and a plan passes
    ``None``.
    """
    settings = get_settings()
    predict_config = load_predict_config(settings.config_root)
    scope_dropped: list[_DropRecord] = []
    cohort_narrowed: list[_DropRecord] = []
    resolution = _ResolveReport()
    requested = _scope_filtered(
        requested_cases,
        predict_config.scope,
        settings.corpus_root,
        settings.corpus_backend,
        data_root=settings.data_root,
        dropped_out=scope_dropped,
        cohort_narrowed_out=cohort_narrowed,
    )
    # One clock for the whole plan, so a fan-out that straddles midnight cannot
    # apply a different staleness bound to selection than to the re-check.
    today = date.today()
    cases = _resolve_cases(
        requested,
        lambda c, d: forecastable_events(
            corpus.corpus_db_path(settings.corpus_root),
            c,
            d,
            backend=settings.corpus_backend,
            today=today,
        ),
        # Listed events the corpus now refuses — resolved since queueing, or a
        # merits moment whose row fails the selection predicate's row arms —
        # are dropped at plan time rather than minted into cells provisioning
        # must (or, for the gvr/stale classes, cannot) refuse. Keyed on the
        # same condition as the scope gate, because under `all` the corpus is
        # deliberately never consulted (dev / back-testing may fan out over an
        # empty corpus).
        drop_unforecastable=(
            recheck := (
                (
                    lambda c, d: unforecastable_listed_events(
                        corpus.corpus_db_path(settings.corpus_root),
                        c,
                        d,
                        today=today,
                        backend=settings.corpus_backend,
                    )
                )
                if predict_config.scope != PredictScope.all
                else None
            )
        ),
        stage=stage,
        report=report,
        report_out=resolution,
    )
    if requested and any(c.events for c in requested) and not any(c.events for c in cases):
        # Every listed event fell to the forecastability re-check, so the
        # emitted matrix will be empty and the workflow's empty-matrix step will
        # close the trigger issue with its generic out-of-scope note (it cannot
        # tell the causes apart). This line is the correctly-attributed record;
        # safe, because every class the re-check drops on needs something other
        # than a re-queue — a grade for a resolved event, a corpus fix for a
        # stale grant. The per-event warnings above carry which class each was.
        if report:
            typer.echo(
                f"::error::{stage}: the forecastability re-check dropped every listed event — "
                "none is still forecastable; nothing is minted",
                err=True,
            )
        # A workflow-log annotation is retention-bounded; the close note is the
        # durable, human-read surface. Re-derive the per-event reasons (point
        # lookups, only on this empty path) and hand the workflow's close step
        # an attributed note in place of its generic out-of-scope one — the
        # same channel the stranded guard uses.
        if note_file is not None and recheck is not None:
            lines: list[str] = []
            for c in requested:
                dropped = recheck(c.court, c.docket)
                lines.extend(
                    f"- `{ids.case_id(c.court, c.docket)}` `{event}` — {reason}"
                    for event, reason in sorted(dropped.items())
                    if event in c.events
                )
            note_file.write_text(
                "Every event this trigger listed has become unforecastable since it was "
                "queued, so nothing was minted:\n\n" + "\n".join(lines) + "\n\n"
                "None of these needs a re-queue — a resolved event needs its grade, and a "
                "decided or stale proceeding must not receive a forward cell.\n",
                encoding="utf-8",
            )
    # Per-predictor plan-time gate, before any model spend: a (predictor, event)
    # cell whose predictor already committed a prediction for that event is not
    # re-minted, so a re-queue where two of three engines landed mints only the
    # missing engine. See `predict_matrix` (the mirror of evaluate's gate).
    matrix = predict_matrix(
        settings.config_root / "predictors.yaml", cases, run_id, data_root=settings.data_root
    )
    # The stranded-run guard, before the volume cap so the cap's budget goes to
    # genuinely new cells: a cell whose output already sits in a run whose
    # `collect` never succeeded is withheld rather than re-spent. The ledger gate
    # above cannot see those predictions — they are cell artifacts, not commits —
    # which is exactly why a failed collect otherwise re-mints the whole run
    # every live cycle. Fail-open in every degraded direction; see
    # `_guarded_matrix` and `drop_stranded_cells`.
    guard = _StrandedGuardReport()
    matrix = _guarded_matrix(
        matrix,
        stranded_file,
        note_file,
        stage=stage,
        report=report,
        guard_out=guard,
    )
    # Salience-independent volume backstop, after scope filtering: hold the
    # fan-out under the cell cap even if selection failed open, deferring whole
    # overflow cases (they stay queued and re-run next cycle). See
    # `cap_predict_cells` and PredictConfig.max_predict_cells_per_run.
    #
    # Coupling to watch: if the cap defers ALL cases the emitted matrix is empty,
    # which the plan job's `has_jobs=false` path routes to the workflow's
    # empty-matrix step — and that step closes the trigger issue with a generic
    # *out-of-scope* note, since cap-empty and scope-empty look identical to it.
    # `_report_predict_cap` escalates to a ::error:: in that case so the cause is
    # on the record; it is safe because the deferred cases persist in the corpus
    # predict queue and re-queue next cycle regardless of the close.
    capped = cap_predict_cells(matrix, predict_config.max_predict_cells_per_run)
    if capped.dropped_cells and report:
        _report_predict_cap(capped, predict_config.max_predict_cells_per_run)
    return _PredictFanout(
        requested=requested_cases,
        resolved=cases,
        scope_dropped=tuple(scope_dropped),
        cohort_narrowed=tuple(cohort_narrowed),
        resolution=resolution,
        guard=guard,
        capped=capped,
        max_cells=predict_config.max_predict_cells_per_run,
    )


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
        list[str] | None,
        typer.Option(help="Single-case event id(s); default: open case-baseline events."),
    ] = None,
    stranded_file: Annotated[
        Path | None,
        typer.Option(
            help="Census of cell artifacts left by recent runs whose collect did not succeed; "
            "a cell already sitting in one is not re-minted. Absent or empty = guard off.",
        ),
    ] = None,
    stranded_note_file: Annotated[
        Path | None,
        typer.Option(
            help="Where to write the trigger-issue close note when the stranded-run guard "
            "withholds every cell (nothing is written otherwise).",
        ),
    ] = None,
) -> None:
    """Emit the predictor x case x event GitHub Actions matrix as compact JSON.

    A case with no listed ``events`` defaults to that case's open case-baseline
    (petition/appeal-kind) events.
    """
    fanout = _predict_fanout(
        _requested_cases(body_file, court, docket, event),
        run_id,
        stage="predict-matrix",
        stranded_file=stranded_file,
        note_file=stranded_note_file,
        report=True,
    )
    # The ex-post backstop, last: it reads measured spend rather than projected
    # volume, so it holds whatever the caps above decided. Checked after the cap
    # so a breach is reported against the run that would actually have been minted.
    if _spend_gate_or_empty("predict-matrix").breached:
        typer.echo(json.dumps({"include": []}, separators=(",", ":")))
        return
    typer.echo(json.dumps({"include": fanout.capped.include}, separators=(",", ":")))


@dataclass(frozen=True)
class _EvaluateFanout:
    """One pass of the evaluate planning pipeline, recorded step by step.

    The two cell-grain drop classes stay apart — one is a cost gate (nothing to
    score) and the other an idempotency gate (already scored) — because
    collapsed, a fully-graded re-queue reads as a run with no predictions.
    """

    requested: list[CaseRequest]
    resolved: list[CaseRequest]
    scope_dropped: tuple[_DropRecord, ...]
    resolution: _ResolveReport
    predictionless: tuple[_DropRecord, ...]
    already_evaluated: tuple[_DropRecord, ...]
    candidates: int
    matrix: dict[str, list[dict[str, Any]]]


def _evaluate_fanout(
    requested_cases: list[CaseRequest],
    run_id: str,
    *,
    stage: str,
    force: bool,
    report: bool,
) -> _EvaluateFanout:
    """Run the evaluate planning pipeline: scope, resolution, and the two gates.

    The one definition of what an evaluate run would mint, shared by
    ``evaluate-matrix`` and ``evaluate-plan``, so the dry run cannot describe a
    different fan-out than the minting command performs. Nothing here writes.

    ``report`` is the minting path's per-gate stderr lines; a plan passes
    ``False`` and carries the same two numbers in its own ``counts`` block,
    which is its single stderr voice.

    ``candidates`` is the opening balance — every evaluator x case x event cell
    the resolved request spans, before either gate — so a reader can reconcile
    the drops against the surviving set rather than take the difference on
    trust.
    """
    settings = get_settings()
    scope = load_predict_config(settings.config_root).scope
    scope_dropped: list[_DropRecord] = []
    resolution = _ResolveReport()
    cases = _resolve_cases(
        _scope_filtered(
            requested_cases,
            scope,
            settings.corpus_root,
            settings.corpus_backend,
            for_grading=True,
            dropped_out=scope_dropped,
        ),
        lambda c, d: resolved_events(
            corpus.corpus_db_path(settings.corpus_root), c, d, backend=settings.corpus_backend
        ),
        stage=stage,
        report=report,
        report_out=resolution,
    )
    # Two plan-time gates, both before any model spend: an event with no
    # committed prediction has nothing to score, and a judge that already graded
    # the event is not re-minted. See `evaluate_matrix`.
    evaluators_path = settings.config_root / "evaluators.yaml"
    matrix = evaluate_matrix(
        evaluators_path, cases, run_id, data_root=settings.data_root, skip_evaluated=not force
    )
    evaluators = [e for e in load_evaluators(evaluators_path) if e.enabled]
    # Report the two gates separately: one is a cost gate (nothing to score) and
    # the other an idempotency gate (already scored). Collapsed, a fully-graded
    # re-queue would read as a run with no predictions. Each is counted from the
    # same predicate the gate uses rather than by subtracting one from the total,
    # so the arithmetic does not silently depend on the order the gates run in
    # `evaluate_matrix` — reordering them there would otherwise print a negative.
    predictionless: list[_DropRecord] = []
    already: list[_DropRecord] = []
    for case in cases:
        case_id = ids.case_id(case.court, case.docket)
        for event_id in case.events:
            if not event_has_predictions(settings.data_root, case.court, case.docket, event_id):
                # Attribute an event that is both to the cost gate only; one
                # record per would-be cell, so the count is cells, not events.
                predictionless.extend(
                    _DropRecord(
                        case_id,
                        "no committed prediction for this event, so nothing to score",
                        event_id=event_id,
                        actor_id=evaluator.id,
                    )
                    for evaluator in evaluators
                )
                continue
            if force:
                continue
            already.extend(
                _DropRecord(
                    case_id,
                    "this evaluator has already graded the event",
                    event_id=event_id,
                    actor_id=evaluator.id,
                )
                for evaluator in evaluators
                if event_has_evaluations(
                    settings.data_root,
                    case.court,
                    case.docket,
                    event_id,
                    evaluator_id=evaluator.id,
                )
            )
    if report and predictionless:
        typer.echo(f"{stage}: dropped {len(predictionless)} predictionless cell(s)", err=True)
    if report and already:
        typer.echo(f"{stage}: dropped {len(already)} already-evaluated cell(s)", err=True)
    return _EvaluateFanout(
        requested=requested_cases,
        resolved=cases,
        scope_dropped=tuple(scope_dropped),
        resolution=resolution,
        predictionless=tuple(predictionless),
        already_evaluated=tuple(already),
        candidates=len(evaluators) * sum(len(case.events) for case in cases),
        matrix=matrix,
    )


@app.command("evaluate-matrix")
def evaluate_matrix_cmd(
    run_id: Annotated[str, typer.Option(help="Shared run id for this fan-out.")],
    body_file: Annotated[
        Path | None,
        typer.Option(
            help="Issue body file; its ```json block (one case or an array) is parsed. "
            "Omit it (with no --court/--docket) to derive the cases from the evaluate backlog."
        ),
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
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Re-mint cells for events a judge has already graded (a deliberate "
            "re-grade after a prompt or rubric change). Needs a named case; it "
            "cannot re-grade the backlog.",
        ),
    ] = False,
) -> None:
    """Emit the evaluator x case x event GitHub Actions matrix as compact JSON.

    Two input modes. ``--body-file`` takes the cases from a trigger issue, and
    ``--court``/``--docket`` name one ad hoc. Given no input at all, they come
    from the corpus-level evaluate backlog — the gradings committed state still
    owes — so a scheduled run derives its own work with no issue body. That
    derivation writes no ``evaluate_queued_at`` debounce stamp: the
    already-graded gate below is the idempotency, and the corpus of record is
    writable only from the writer jobs. Run it where the corpus is pulled.

    A case with no listed ``events`` defaults to that case's resolved events.

    Two deterministic gates drop cells before any model spend: an event with no
    committed prediction has nothing to score, and a judge that already graded
    the event is not re-minted. The second is what makes the fan-out idempotent,
    so a re-queue cannot double-count in the leaderboard — and what lets the
    backlog mode re-plan the same backlog without re-minting a graded cell.
    ``--force`` disables it for a deliberate re-grade, which otherwise would
    need committed artifacts deleted to get a cell minted.
    """
    fanout = _evaluate_fanout(
        _requested_cases(body_file, court, docket, event, backlog=True, force=force),
        run_id,
        stage="evaluate-matrix",
        force=force,
        report=True,
    )
    # The same ex-post backstop predict consults: the ceiling governs total
    # inference spend, and a grading costs a cell like a forecast does. An owed
    # grading is never lost by deferring it — the backlog deriver re-derives it
    # from committed ledger state on a later cycle.
    if _spend_gate_or_empty("evaluate-matrix").breached:
        typer.echo(json.dumps({"include": []}, separators=(",", ":")))
        return
    typer.echo(json.dumps(fanout.matrix, separators=(",", ":")))


#: The **fallback** per-cell rate, from *Capacity `N`: the funding knob* in
#: ``docs/budget.md``: $15 per fully-tournamented case divided across its design
#: mix of six cells. It prices a cell whose engine the table below does not name
#: — a new engine, or a registry entry ahead of the doc — so a plan never
#: silently drops such a cell from its total. Re-anchor it when the doc moves.
_PLANNING_USD_PER_CELL = 2.50

#: Per-cell rates in USD, keyed (seam, engine), from ``docs/budget.md``. The
#: predict row is the whole-run column of *Per-cell cost is keyed on the stage*
#: — one stamped fan-out, 81 cells over 27 events, since re-based out of the
#: frozen partition by the `proc-v5` instant. The evaluate row is
#: that section's evaluate-cohort table, ``proc-v2`` row (the better-matched of
#: its two pre-freeze anchors), scaled by the whole predict move (x1.218)
#: exactly as the doc's own per-case derivation does. The doc's stamped
#: evaluate rows are interim-stage, graded before the current instant under
#: superseded evaluator digests, so they re-anchor nothing here; see the
#: caveats below. The two sum
#: to $6.79 + $8.18 = $14.97 a case — the top of the doc's $14.6-15.0 band,
#: which the $2.50 fallback is the six-cell rounding of — so a full
#: three-engine, both-seam fan-out prices within a cent either way. What
#: conditioning buys is the *narrowed* plan: within a seam the engines differ
#: ~7x, so an engine-narrowed backfill priced at the flat rate is wrong by up
#: to ~4x.
#:
#: Engine keys, not actor ids: a cell carries its resolved ``engine``, and the
#: doc's per-actor columns are one actor per engine in the shipped registries.
_PLANNING_RATES_USD_PER_CELL: dict[str, dict[str, float]] = {
    "predict": {"claude-code": 4.27, "codex": 1.88, "gemini": 0.64},
    "evaluate": {"claude-code": 5.92, "codex": 1.30, "gemini": 0.96},
}

#: What the rates above can and cannot support, carried on every plan beside the
#: number so the estimate is never read as a measurement of this run. Keyed by
#: seam where the standing differs; :func:`_shared_spend_caveats` adds the rest.
#:
#: The two "four"s in this file name different things and each says which: the
#: four predict *moments* docs/budget.md measures, and the four pre-freeze
#: *gradings* the evaluate anchor is drawn from (of which the rates here use
#: three).
_SPEND_BASIS_CAVEATS: dict[str, list[str]] = {
    "predict": [
        "Measured, but over one stamped fan-out (81 cells, 27 events) that "
        + "predates the current freeze instant — a shakedown figure for claims "
        + "purposes. "
        + "docs/budget.md reads the ~+20% level gap to the 410-cell pre-freeze "
        + "ledger as an UPPER BOUND on any level effect, not a measurement of one.",
    ],
    "evaluate": [
        "An ASSUMPTION, not a measurement: docs/budget.md scales a pre-freeze "
        + "anchor by the whole predict move (~+22%). The anchor these rates use "
        + "is its `proc-v2` row — THREE graded events, the process-stamped subset "
        + "of the four pre-freeze gradings — taken as the better-matched of the "
        + "doc's two pre-freeze anchors; the pooled four-grading row is the more "
        + "cautious one and is NOT what these rates carry. All four are "
        + "cert-stage, so the anchor is stage-narrow either way.",
        "An evaluate measurement EXISTS outside the frozen partition, and these "
        + "rates do not use "
        + "it: two runs independently graded one six-event INTERIM population "
        + "($6.44 and $6.69 an event, one figure per run), before the current "
        + "instant and under since-superseded evaluator "
        + "digests. It lands below the scaled projection, but no pre-freeze "
        + "anchor covers the interim stage, so it bounds nothing — the rates "
        + "hold the pre-freeze anchor until an evaluate fan-out under the "
        + "currently blessed grading digests reaches the cert stage.",
    ],
}


def _shared_spend_caveats(seam: str) -> list[str]:
    """The caveats that hold on both seams, with the moment note routed by seam.

    The moment caveat is a statement about the *predict* measurements. It still
    belongs on an evaluate plan, because the evaluate rates are the predict
    move applied to a pre-freeze anchor — so whatever the predict mix carries,
    they carry — but it has to say so, or it reads as a moment conditioning on
    the evaluate side that these rates do not carry.
    """
    moment = (
        "Not conditioned on the forecast moment. Of the four predict MOMENTS "
        "docs/budget.md measures, only merits-above-cert-arrival separates at the "
        "measured n (~+$1.2 an event, on 11 events against 12); the rest sit "
        "within noise of each other, so conditioning on them would fit noise. "
        "The merits separation is real and is deliberately not applied here, so "
        "an all-merits plan reads ~10% LOW ($7.47 an event against the $6.79 "
        "whole-run rate these figures use)."
    )
    if seam == "evaluate":
        moment += (
            " This describes the predict seam, whose whole-run move the evaluate "
            "rates are scaled by, so it carries into them."
        )
    return [
        "Measured per-cell cost spans ~$0.25-8.30 by model mix, so a per-engine mean "
        + "prices a FAN-OUT and never a cell.",
        moment,
    ]


def _spend_verdict_json(verdict: SpendVerdict) -> dict[str, Any]:
    """The ex-post spend backstop's reading, for a plan to report rather than act on.

    Two honesty properties the raw verdict does not carry. **Unknowns print as
    unknown**: with no ceiling configured the backstop short-circuits before
    reading the ledger, so its zeros are unmeasured rather than measured-zero
    and are emitted as ``null``. And **the measurement is a floor**: a cell's
    ``usage.json`` reaches ``data/`` only on its run's collect PR, so spend
    already incurred but not yet committed is invisible to it.
    """
    enforced = verdict.enforced
    return {
        "enforced": enforced,
        "breached": verdict.breached,
        # The consequence, stated rather than left to be derived: under a breach
        # `would_mint` is a fan-out the run would not actually mint.
        "would_empty_matrix": verdict.breached,
        "spent_usd": verdict.spent_usd if enforced else None,
        "ceiling_usd": verdict.ceiling_usd if enforced else None,
        "cells": verdict.cells if enforced else None,
        "window_days": verdict.window_days,
        # Only where a figure exists to be a floor of. Claiming a null is a
        # floor is not a weaker claim than claiming it is exact — it is not a
        # claim about anything.
        "spent_usd_is_floor": True if enforced else None,
        "basis": (
            "The ledger counts collected cells only — a cell's usage.json reaches data/ when "
            "its run's collect PR merges — so spent_usd is a FLOOR on spend within the window, "
            "never a live figure. Null where no ceiling is configured: the backstop returns "
            "before reading the ledger, so those figures are unmeasured, not zero."
        ),
    }


def _plan_spend(cells: Sequence[Mapping[str, Any]], *, seam: str, breached: bool) -> dict[str, Any]:
    """Price a would-mint cell set at the per-(seam, engine) rates, with its basis.

    Summed cell by cell rather than multiplied by one blended rate, because the
    engines differ by ~7x within a seam: a plan narrowed to one engine priced at
    the design-mix average is wrong by up to 4x in either direction, and a
    narrowed plan is exactly the shape a backfill re-queue takes. A cell whose
    engine the table does not name falls back to the design-mix rate and is
    counted, so an unrecognized engine shows up as a stated approximation rather
    than as a cell missing from the total.
    """
    rates = _PLANNING_RATES_USD_PER_CELL[seam]
    total = 0.0
    at_fallback = 0
    for cell in cells:
        rate = rates.get(str(cell["engine"]))
        if rate is None:
            rate = _PLANNING_USD_PER_CELL
            at_fallback += 1
        total += rate
    caveats = list(_SPEND_BASIS_CAVEATS[seam]) + _shared_spend_caveats(seam)
    if seam == "predict":
        caveats.append(
            "Covers THIS run only: cells the volume cap deferred (see deferred_by_cap) "
            "re-queue on a later cycle and cost their own rates then."
        )
    if at_fallback:
        caveats.append(
            f"{at_fallback} cell(s) ran an engine the rate table does not name and are "
            f"priced at the ${_PLANNING_USD_PER_CELL:.2f} design-mix fallback."
        )
    return {
        "estimated_spend_usd": round(total, 2),
        # Non-null only under a breach, where the figure prices a fan-out the
        # run would not mint. Kept beside the number rather than only in
        # `spend_gate`, so a reader who takes the estimate takes the caveat.
        "estimated_spend_caveat": (
            "The ex-post spend backstop is breached, so a real run would mint 0 cells and "
            "spend $0.00; this prices the fan-out the earlier steps decided."
            if breached
            else None
        ),
        # The fallback rate is deliberately NOT published at the top level beside
        # `estimated_spend_usd`: there it reads as the rate the estimate used,
        # and a consumer multiplying it by `would_mint_cells` reconstructs
        # exactly the flat-rate error the per-engine table exists to remove. It
        # lives inside the basis block, named as the fallback it is.
        "spend_estimate_basis": {
            "source": (
                "docs/budget.md — 'Per-cell cost is keyed on the stage' (the predict "
                "whole-run row) and the evaluate-cohort table beside it (proc-v2 row, "
                "scaled by the predict move)"
            ),
            "seam": seam,
            "rates_usd_per_cell": dict(rates),
            "fallback_usd_per_cell": _PLANNING_USD_PER_CELL,
            "fallback_source": (
                "docs/budget.md — 'Capacity `N`: the funding knob' ($15 per "
                "fully-tournamented case over a six-cell design mix)"
            ),
            "cells_at_fallback_rate": at_fallback,
            "caveats": caveats,
        },
    }


@dataclass(frozen=True)
class _LedgerGate:
    """The predict ledger gate's reading: the opening balance and what it dropped.

    ``candidates`` is the FULL enabled-predictor x case x event product the
    resolved request spans, before any narrowing or gate — the plan's opening
    balance, so the later drops reconcile against the surviving set (candidates
    minus request-narrowed minus already-predicted minus withheld minus deferred
    is exactly what a run would mint) instead of being taken on trust.
    """

    candidates: int
    request_narrowed: tuple[_DropRecord, ...]
    already_predicted: tuple[_DropRecord, ...]


def _predict_ledger_gate(
    resolved: list[CaseRequest], predictors_path: Path, data_root: Path
) -> _LedgerGate:
    """Re-walk :func:`predict_matrix`'s product and report what removed cells from it.

    Re-derived from the same predicates, over the same predictor x case x event
    order, rather than by subtracting the surviving cells from a product — so
    the plan's counts cannot drift from the gates they report on, and stay right
    when a later step (the stranded guard, the cap) removes cells of its own.

    Two classes, held apart because they answer different questions: the
    request's own ``predictors:`` narrowing is what the *trigger* asked for (a
    backfill body naming the engines that failed), while the ledger gate is what
    the *corpus* already holds. Collapsed, a narrowed backfill would read as an
    already-complete event.
    """
    candidates = 0
    narrowed: list[_DropRecord] = []
    records: list[_DropRecord] = []
    for predictor in enabled_predictors(predictors_path):
        for case in resolved:
            candidates += len(case.events)
            case_id = ids.case_id(case.court, case.docket)
            if case.predictors and predictor.id not in case.predictors:
                narrowed.extend(
                    _DropRecord(
                        case_id,
                        f"the request narrows this case to predictors {sorted(case.predictors)}",
                        event_id=event_id,
                        actor_id=predictor.id,
                    )
                    for event_id in case.events
                )
                continue
            records.extend(
                _DropRecord(
                    case_id,
                    "this predictor has already committed a prediction for the event",
                    event_id=event_id,
                    actor_id=predictor.id,
                )
                for event_id in case.events
                if event_has_predictions(
                    data_root, case.court, case.docket, event_id, predictor_id=predictor.id
                )
            )
    return _LedgerGate(candidates, tuple(narrowed), tuple(records))


def _plan_count_lines(plan: dict[str, Any], *, stage: str) -> list[str]:
    """The plan's counts, one line per grain.

    Two lines because they are two grains — cases and events on one, cells on
    the other — and a single run-on line invites reading a case count as a cell
    count. Shared by the stderr summary and the approval report, so the two
    surfaces cannot disagree about what the plan counted.
    """
    counts = plan["counts"]
    return [
        f"{stage} {grain.replace('_', ' ')}: "
        + ", ".join(f"{name}={value}" for name, value in counts[grain].items())
        for grain in ("provenance", "cell_ledger")
    ]


def _plan_breach_line(plan: dict[str, Any], *, stage: str) -> str | None:
    """The ex-post backstop's warning, or ``None`` where it is not breached."""
    if not plan["spend_gate"]["breached"]:
        return None
    return (
        f"{stage}: the ex-post spend backstop is breached, so a real run would mint 0 cells "
        f"however many this plan lists; the plan reports the gate rather than applying it"
    )


def _plan_spend_line(plan: dict[str, Any], *, stage: str) -> str:
    """The closing sentence: what the fan-out would cost, with its basis in the sentence.

    The line a reader is most likely to quote, so every clause that changes what
    the number means travels inside it rather than a paragraph away — the
    evaluate seam's rates being an assumption, a breach that would empty the
    matrix anyway, and the cap-deferred cells the figure does not cover.
    """
    ledger = plan["counts"]["cell_ledger"]
    breached = bool(plan["spend_gate"]["breached"])
    # Without the suffix the line reads as a prediction of what the next run
    # costs, directly contradicting the breach warning above it — and the last
    # line is the one a reader keeps.
    breach_note = (
        " — but the spend backstop would empty the matrix, so a real run mints 0."
        if breached
        else "."
    )
    deferred = ledger.get("deferred_by_cap_cells", 0)
    cap_note = (
        f" Covers this run only: {deferred} cell(s) deferred by the volume cap re-queue on a "
        f"later cycle at their own cost."
        if deferred
        else ""
    )
    # The evaluate seam's rates are a scaled pre-freeze anchor, so the one line a
    # reader is most likely to quote has to carry that in the same sentence as
    # the number; predict's are measured and need no such clause.
    rate_note = (
        "docs/budget.md's per-engine rates, which for the evaluate seam are an "
        "assumption (pre-freeze cert-stage anchor scaled ~+22%), not a measurement"
        if plan["stage"] == "evaluate"
        else "the per-engine rates in docs/budget.md (see spend_estimate_basis)"
    )
    return (
        f"{stage}: would mint {ledger['would_mint_cells']} cell(s), estimated "
        f"${plan['estimated_spend_usd']:.2f} at {rate_note}. Nothing was spent and nothing "
        f"was written{breach_note}{cap_note}"
    )


#: Would-mint rows the approval report prints before it truncates. The comment
#: is read to decide one question — approve this fan-out or not — and forty rows
#: is already more than anyone checks line by line; past that the surviving
#: count and the plan JSON carry the fan-out better than another 200 rows would.
_APPROVAL_REPORT_MAX_ROWS = 40

#: The rendered document's hard ceiling, under GitHub's 65,536-character comment
#: limit. That limit is refused with a 422 rather than truncated, and a 422 is
#: not transient: a fan-out wide enough to overflow would lose its approval
#: surface at exactly the moment it most needs a human reading it. Every section
#: is bounded by construction; the clamp makes the bound a guarantee.
_APPROVAL_REPORT_MAX_CHARS = 60_000

_APPROVAL_REPORT_TRUNCATED = (
    "\n\n_Report truncated at the comment-size ceiling; the plan JSON carries the full fan-out._"
)

#: Drop classes as (plan key, the count's grain and what the class did), in
#: pipeline order. A key a seam does not have is skipped — the two gate on
#: different things — as is an empty one: the counts block above already
#: reconciles, so this section exists to name the classes that actually took
#: something. Each label opens with its own grain because the classes do not
#: share one: the scope gate drops whole *cases* (and, where cohort completion
#: keeps a case narrowed, the *events* it lost), the forecastability re-check
#: drops *events*, and only the ledger-grain classes drop *cells*. Under a
#: section a reader arrives at counting cells, an ungrained "3 dropped as out of
#: scope" is read as three cells when it means three cases' worth of them.
_APPROVAL_DROP_CLASSES: tuple[tuple[str, str], ...] = (
    ("dropped_out_of_scope", "case(s) dropped as out of scope"),
    (
        "dropped_cohort_narrowed",
        "event(s) narrowed away on a salience-deferred case kept for cohort completion",
    ),
    ("dropped_unforecastable", "event(s) dropped as no longer forecastable"),
    ("cases_with_no_default_events", "case(s) resolved to no default events"),
    ("dropped_by_request_narrowing", "cell(s) narrowed away by the request's event list"),
    ("dropped_already_predicted", "cell(s) dropped as already predicted by that predictor"),
    ("dropped_predictionless", "cell(s) dropped as having no committed prediction to score"),
    ("dropped_already_evaluated", "cell(s) dropped as already graded by that judge"),
    ("withheld_stranded", "cell(s) withheld by the stranded-run guard"),
)


def _md_cell(value: object) -> str:
    """One table cell: the value as a code span, with any pipe escaped.

    Two characters in a value would otherwise escape the cell it is rendered
    into, and this document is posted as a public issue comment:

    A `|` splits the row into an extra column even within a code span — GFM
    resolves the table's cell boundaries before it resolves inline code — so it
    is backslash-escaped, which keeps a stray pipe in an id from silently
    shifting every column to its right.

    A backtick would close the span early and let the rest of the value render
    as markdown. Rather than dropping it, the span is fenced with one more
    backtick than the longest run inside the value, padded where the value
    itself begins or ends with one (the renderer strips that padding again).
    Values here are corpus- and registry-derived ids, so this is a containment
    property rather than a live threat — but a cell that cannot break out is
    the same amount of code as one that can, and only one of them stays true
    when a future id gains a character nobody anticipated.
    """
    text = str(value).replace("|", r"\|")
    longest = run = 0
    for char in text:
        run = run + 1 if char == "`" else 0
        longest = max(longest, run)
    fence = "`" * (longest + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def _approval_report_table(plan: dict[str, Any]) -> list[str]:
    """The would-mint cells as a markdown table, ordered by case, truncated with its count.

    Sorted by (case, actor) rather than left in fan-out order so the 40 rows a
    truncated table keeps are a **contiguous range of cases**: a reader can see
    which cases the visible rows cover and know the rest lie past them, where
    the registry-major fan-out order would instead show every case's first
    engine and cut the others.
    """
    cells = plan["would_mint"]
    if not cells:
        return ["No cells would be minted, so approving this run would spend nothing."]
    evaluate = plan["stage"] == "evaluate"
    actor_key = "evaluator_id" if evaluate else "predictor_id"
    ordered = sorted(cells, key=lambda c: (c["court"], c["docket"], c[actor_key], c["event_id"]))
    rows = [
        f"| {'Evaluator' if evaluate else 'Predictor'} | Case | Event | Engine |",
        "| --- | --- | --- | --- |",
    ]
    rows.extend(
        f"| {_md_cell(cell[actor_key])} "
        f"| {_md_cell(ids.case_id(cell['court'], cell['docket']))} "
        f"| {_md_cell(cell['event_id'])} | {_md_cell(cell['engine'])} |"
        for cell in ordered[:_APPROVAL_REPORT_MAX_ROWS]
    )
    if len(cells) > _APPROVAL_REPORT_MAX_ROWS:
        rows.extend(
            [
                "",
                f"… and {len(cells) - _APPROVAL_REPORT_MAX_ROWS} more cells. Rows are ordered "
                f"by case, then actor, so the ones above are the lowest case ids; the plan "
                f"JSON carries every one of them.",
            ]
        )
    return rows


def _render_approval_report(plan: dict[str, Any], *, stage: str, run_url: str = "") -> str:
    """Render a plan as the bounded markdown a maintainer approves or rejects from.

    A pure function of the plan document, so the surface a hold decision is made
    on is unit-tested rather than assembled by a workflow's shell; the workflow
    posts this file and contributes only ``run_url``, the one line that needs to
    know where the deployment approval lives.

    Bounded by construction — a capped cell table, per-class drop *counts* with
    no per-record lists (those stay in the JSON, which is where a reader who
    wants one drop's reason goes), and a final clamp — because GitHub refuses an
    over-long comment with a 422 rather than truncating it, and the widest
    fan-out is exactly the one that must not lose its approval surface. Every
    count and caveat is the string the stderr summary prints, not a paraphrase
    of it, so the report cannot drift from the plan it renders.
    """
    ledger = plan["counts"]["cell_ledger"]
    # The heading is the one line a reader is guaranteed to see, so under a
    # breach it carries the consequence rather than a cell count that approving
    # would not deliver: the backstop empties the matrix whatever the plan lists.
    breach_heading = (
        " — but a real run mints 0 under the spend backstop"
        if plan["spend_gate"]["breached"]
        else ""
    )
    lines = [
        f"## {stage}: {ledger['would_mint_cells']} cell(s) held for approval{breach_heading}",
        "",
        f"Run `{plan['run_id']}` is held before minting anything. Nothing has been spent and "
        f"nothing has been written; this is what a run would do if approved.",
        "",
        "### Counts",
        "",
    ]
    lines.extend(f"- `{line}`" for line in _plan_count_lines(plan, stage=stage))
    lines.extend(["", "### Spend", "", _plan_spend_line(plan, stage=stage)])
    breach = _plan_breach_line(plan, stage=stage)
    if breach is not None:
        lines.extend(["", f"> {breach}"])
    guard = plan.get("stranded_guard")
    if guard is not None and (guard["degraded_reason"] or guard["unparsed_records"]):
        # A withheld count of zero is three states and only one of them is a
        # reason to distrust the plan, so the two degraded ones are named where
        # the decision is made rather than left for the JSON. The reason goes in
        # a code span: it quotes the underlying exception, whose text routinely
        # carries a repr like `<class 'dict'>` that GitHub's comment sanitizer
        # eats as a tag — leaving a reader "got ." where the cause should be —
        # and the span neutralizes any other markdown the exception carries.
        detail = (
            f"failed open (`{guard['degraded_reason']}`)"
            if guard["degraded_reason"]
            else f"ran but could not read {len(guard['unparsed_records'])} census record(s)"
        )
        lines.extend(
            [
                "",
                "### Stranded-run guard",
                "",
                f"The stranded-run guard {detail}, so a cell it could not check may re-spend "
                f"output an uncollected run already produced.",
            ]
        )
    lines.extend(["", "### Would mint", ""])
    lines.extend(_approval_report_table(plan))
    dropped = [
        f"- {len(plan[key])} {label}" for key, label in _APPROVAL_DROP_CLASSES if plan.get(key)
    ]
    deferred = ledger.get("deferred_by_cap_cells", 0)
    if deferred:
        dropped.append(
            f"- {deferred} cell(s) deferred by the volume cap "
            f"(max {plan['deferred_by_cap']['max_cells']} cells a run); they re-queue next cycle"
        )
    lines.extend(["", "### Dropped", ""])
    lines.extend(dropped or ["- Nothing was dropped: every candidate cell would be minted."])
    lines.extend(["", "Each drop's per-record reason is in the plan JSON."])
    if run_url:
        lines.extend(
            [
                "",
                # The literal environment name the workflows bind — one `review`
                # environment serves every spend hold, so the line never derives
                # a name a stage-specific environment would have to match.
                f"Approve or reject the `review` deployment on the run: {run_url}",
            ]
        )
    document = "\n".join(lines) + "\n"
    if len(document) > _APPROVAL_REPORT_MAX_CHARS:
        document = (
            document[: _APPROVAL_REPORT_MAX_CHARS - len(_APPROVAL_REPORT_TRUNCATED)]
            + _APPROVAL_REPORT_TRUNCATED
        )
    return document


# Declared once and shared by both plan commands rather than spelled out twice:
# the two options describe one contract, and a help text that drifted between
# the seams would document a difference that does not exist.
_ApprovalReportOption = Annotated[
    Path | None,
    typer.Option(
        help="Also write the plan as a bounded markdown report, for a hold gate to post as "
        "a trigger-issue comment. stdout is unchanged, with the flag or without it.",
    ),
]
_ApprovalReportRunUrlOption = Annotated[
    str,
    typer.Option(
        help="Run URL the approval report's closing line points at; omitted, the report "
        "carries no such line. Ignored without --approval-report.",
    ),
]


def _echo_plan(
    plan: dict[str, Any],
    *,
    stage: str,
    approval_report: Path | None = None,
    run_url: str = "",
) -> None:
    """Print the plan to stdout, its human summary to stderr, its report to a file.

    The repo's stdout/stderr split, for the same reason the matrix commands keep
    it: stdout is the machine surface a consuming gate parses, so every word
    meant for a person goes to stderr. ``approval_report`` adds a third channel
    and changes neither of the first two — with the flag or without it stdout
    carries the same bytes, so a gate that parses the plan cannot tell whether a
    report was written beside it.

    That write is deliberately **fail-loud**, and deliberately *before* the
    stdout echo, which is the opposite of the stranded-run close note's
    fail-open: an unwritable note costs the trigger issue a better message and
    nothing else, while an unwritable approval report costs the hold its entire
    decision surface. A gate that read the plan from stdout, found no report,
    and posted an empty comment would ask a maintainer to approve a fan-out
    they cannot see. Raising here stops the run instead.
    """
    for line in _plan_count_lines(plan, stage=stage):
        typer.echo(line, err=True)
    breach = _plan_breach_line(plan, stage=stage)
    if breach is not None:
        typer.echo(breach, err=True)
    typer.echo(_plan_spend_line(plan, stage=stage), err=True)
    if approval_report is not None:
        write_text(approval_report, _render_approval_report(plan, stage=stage, run_url=run_url))
    typer.echo(json.dumps(plan, separators=(",", ":")))


@app.command("predict-plan")
def predict_plan_cmd(
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
        typer.Option(help="Single-case event id(s); default: open case-baseline events."),
    ] = None,
    stranded_file: Annotated[
        Path | None,
        typer.Option(
            help="Census of cell artifacts left by recent runs whose collect did not succeed, "
            "as `predict-matrix` takes it; a cell already sitting in one is reported withheld.",
        ),
    ] = None,
    run_id: Annotated[
        str,
        typer.Option(
            help="Run id to plan under, echoed on the plan; defaults to now (UTC). No cell "
            "carries it — a plan mints none — so it names the run only in the plan."
        ),
    ] = "",
    approval_report: _ApprovalReportOption = None,
    approval_report_run_url: _ApprovalReportRunUrlOption = "",
) -> None:
    """Report the predict cells a run would mint, step by step, spending nothing.

    The dry run of ``predict-matrix``: the same inputs through the same pipeline
    — scope gate, forecastability re-check, per-predictor ledger gate,
    stranded-run guard, volume cap — with nothing minted and nothing written. No
    trigger-issue close note, no Actions step summary, no model spend; only the
    plan document on stdout, its summary lines on stderr, and — on request —
    the ``--approval-report`` markdown.

    stdout is a single JSON object. ``counts`` splits by grain — ``provenance``
    counts cases and events, ``cell_ledger`` counts cells — because the two are
    read for different questions and a flat block invites reading a case count
    as a cell count. The drop lists explain each count, every record carrying
    the dropping step's own reason; ``would_mint`` is the surviving cell set;
    and ``estimated_spend_usd`` prices it at the per-(seam, engine) rates in
    ``docs/budget.md``, with ``spend_estimate_basis`` naming the source section,
    the rates used, and what they cannot support. That makes "this change
    protects a rerun" a check someone can execute rather than a claim.

    The ex-post spend backstop is **reported, not applied**: ``spend_gate``
    carries its verdict while ``would_mint`` stays the fan-out the earlier steps
    decided, because a plan describes the pipeline rather than standing in for
    it. The consequence is on stdout as well as stderr —
    ``would_mint_cells_after_spend_gate``, ``spend_gate.would_empty_matrix``,
    and ``estimated_spend_caveat`` — so a machine reader cannot take
    ``would_mint`` for what a run would actually spend.

    ``--approval-report`` writes the same plan a second time as bounded
    markdown, for a hold gate to post where a maintainer decides on it. stdout
    is byte-identical either way: the report is a third channel, not a mode.
    """
    settings = get_settings()
    planned_run_id = run_id or ids.run_id()
    fanout = _predict_fanout(
        _requested_cases(body_file, court, docket, event),
        planned_run_id,
        stage="predict-plan",
        stranded_file=stranded_file,
        # A plan writes nothing: no close note, and no step-summary block.
        note_file=None,
        report=False,
    )
    gate = _predict_ledger_gate(
        fanout.resolved, settings.config_root / "predictors.yaml", settings.data_root
    )
    verdict = check_spend(settings.data_root, load_spend_config(settings.config_root))
    would_mint = [
        {
            "predictor_id": cell["predictor_id"],
            "court": cell["court"],
            "docket": cell["docket"],
            "event_id": cell["event_id"],
            # The resolved pair the cell would actually run on, not the registry
            # default: what a cell costs is keyed on them, so a plan that priced
            # the fan-out must name them.
            "engine": cell["engine"],
            "model": cell["model"],
        }
        for cell in fanout.capped.include
    ]
    plan: dict[str, Any] = {
        "stage": "predict",
        "run_id": planned_run_id,
        # Split by grain: `provenance` counts cases and events, `cell_ledger`
        # counts cells. Every key carries its own grain suffix as well, so a
        # count read out of its block is still unambiguous.
        "counts": {
            "provenance": {
                "requested_cases": len(fanout.requested),
                "requested_listed_events": sum(len(c.events) for c in fanout.requested),
                "dropped_out_of_scope_cases": len(fanout.scope_dropped),
                "dropped_cohort_narrowed_events": len(fanout.cohort_narrowed),
                "dropped_unforecastable_events": len(fanout.resolution.unforecastable),
                "resolved_cases": len(fanout.resolved),
                "resolved_events": sum(len(c.events) for c in fanout.resolved),
                "cases_with_no_default_events": len(fanout.resolution.no_default_events),
            },
            "cell_ledger": {
                # The opening balance, so the drops below reconcile: candidates
                # - request_narrowed - already_predicted - withheld - deferred
                # == would_mint.
                "candidate_cells": gate.candidates,
                "dropped_by_request_narrowing_cells": len(gate.request_narrowed),
                "dropped_already_predicted_cells": len(gate.already_predicted),
                "withheld_stranded_cells": len(fanout.guard.withheld),
                "deferred_by_cap_cells": fanout.capped.dropped_cells,
                "would_mint_cells": len(would_mint),
                # What a real run would mint once the ex-post backstop is
                # applied — zero under a breach. The plan reports the gate
                # rather than applying it, so the two numbers differ there.
                "would_mint_cells_after_spend_gate": (0 if verdict.breached else len(would_mint)),
            },
        },
        "dropped_out_of_scope": [r.as_json() for r in fanout.scope_dropped],
        "dropped_cohort_narrowed": [r.as_json() for r in fanout.cohort_narrowed],
        "dropped_unforecastable": [r.as_json() for r in fanout.resolution.unforecastable],
        "cases_with_no_default_events": [r.as_json() for r in fanout.resolution.no_default_events],
        "dropped_by_request_narrowing": [r.as_json() for r in gate.request_narrowed],
        "dropped_already_predicted": [r.as_json() for r in gate.already_predicted],
        # A withheld count of zero means nothing on its own — see
        # `_StrandedGuardReport`, which separates a clean guard from an absent
        # one and from one that failed open.
        "stranded_guard": fanout.guard.as_json(),
        "withheld_stranded": [
            {
                "case_id": ids.case_id(cell.court, cell.docket),
                "event_id": cell.event_id,
                "actor_id": cell.predictor_id,
                "run_db_id": cell.run_db_id,
                "reason": f"its output already sits in uncollected run {cell.run_db_id}",
            }
            for cell in fanout.guard.withheld
        ],
        "deferred_by_cap": {
            "cells": fanout.capped.dropped_cells,
            "cases": list(fanout.capped.dropped_cases),
            "max_cells": fanout.max_cells,
        },
        "spend_gate": _spend_verdict_json(verdict),
        "would_mint": would_mint,
        **_plan_spend(would_mint, seam="predict", breached=verdict.breached),
    }
    _echo_plan(
        plan,
        stage="predict-plan",
        approval_report=approval_report,
        run_url=approval_report_run_url,
    )


@app.command("evaluate-plan")
def evaluate_plan_cmd(
    body_file: Annotated[
        Path | None,
        typer.Option(
            help="Issue body file; its ```json block (one case or an array) is parsed. "
            "Omit it (with no --court/--docket) to plan the evaluate backlog derivation."
        ),
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
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Plan as a deliberate re-grade (the `evaluate-matrix` flag). Needs a "
            "named case; it cannot re-grade the backlog.",
        ),
    ] = False,
    run_id: Annotated[
        str,
        typer.Option(
            help="Run id to plan under, echoed on the plan; defaults to now (UTC). No cell "
            "carries it — a plan mints none — so it names the run only in the plan."
        ),
    ] = "",
    approval_report: _ApprovalReportOption = None,
    approval_report_run_url: _ApprovalReportRunUrlOption = "",
) -> None:
    """Report the evaluate cells a run would mint, step by step, spending nothing.

    The dry run of ``evaluate-matrix``, through the same pipeline and its two
    plan-time gates — an event with no committed prediction has nothing to
    score, and a judge that already graded the event is not re-minted. Same
    grain-split ``counts``, stdout/stderr split, and spend-gate reading as
    ``predict-plan``: the backstop's verdict is reported, never applied.

    It takes ``evaluate-matrix``'s two input modes, so the backlog derivation a
    scheduled run performs — the one that reads no trigger — has a dry run of
    its own: omit ``--body-file`` and the plan enumerates the cells that
    derivation would mint. Read-only in both modes, corpus included.

    Its ``estimated_spend_usd`` carries a weaker basis than predict's, and says
    so: the rates are ``docs/budget.md``'s pre-freeze cert-stage anchor scaled
    by the whole predict move, an assumption rather than a measurement.
    ``spend_estimate_basis.caveats`` states that on every plan, and
    ``--approval-report`` carries it into the rendered report's spend sentence.

    Why the assumption stands while a stamped evaluate measurement exists
    outside the frozen partition — that measurement grades one six-event
    interim population before the current instant, under since-superseded
    evaluator digests, at a stage no pre-freeze anchor covers,
    so the anchor holds until an evaluate fan-out under the currently blessed
    grading digests reaches the cert stage — rides in ``spend_estimate_basis.caveats`` alone.
    """
    settings = get_settings()
    planned_run_id = run_id or ids.run_id()
    fanout = _evaluate_fanout(
        _requested_cases(body_file, court, docket, event, backlog=True, force=force),
        planned_run_id,
        stage="evaluate-plan",
        force=force,
        report=False,
    )
    verdict = check_spend(settings.data_root, load_spend_config(settings.config_root))
    would_mint = [
        {
            "evaluator_id": cell["evaluator_id"],
            "court": cell["court"],
            "docket": cell["docket"],
            "event_id": cell["event_id"],
            # See predict-plan: the resolved pair the cell would run on.
            "engine": cell["engine"],
            "model": cell["model"],
        }
        for cell in fanout.matrix["include"]
    ]
    plan: dict[str, Any] = {
        "stage": "evaluate",
        "run_id": planned_run_id,
        # Split by grain, as predict-plan's is; see there.
        "counts": {
            "provenance": {
                "requested_cases": len(fanout.requested),
                "requested_listed_events": sum(len(c.events) for c in fanout.requested),
                "dropped_out_of_scope_cases": len(fanout.scope_dropped),
                "resolved_cases": len(fanout.resolved),
                "resolved_events": sum(len(c.events) for c in fanout.resolved),
                "cases_with_no_default_events": len(fanout.resolution.no_default_events),
            },
            "cell_ledger": {
                # The opening balance, so the drops below reconcile: candidates
                # - predictionless - already_evaluated == would_mint.
                "candidate_cells": fanout.candidates,
                "dropped_predictionless_cells": len(fanout.predictionless),
                "dropped_already_evaluated_cells": len(fanout.already_evaluated),
                "would_mint_cells": len(would_mint),
                "would_mint_cells_after_spend_gate": (0 if verdict.breached else len(would_mint)),
            },
        },
        "dropped_out_of_scope": [r.as_json() for r in fanout.scope_dropped],
        "cases_with_no_default_events": [r.as_json() for r in fanout.resolution.no_default_events],
        "dropped_predictionless": [r.as_json() for r in fanout.predictionless],
        "dropped_already_evaluated": [r.as_json() for r in fanout.already_evaluated],
        "spend_gate": _spend_verdict_json(verdict),
        "would_mint": would_mint,
        **_plan_spend(would_mint, seam="evaluate", breached=verdict.breached),
    }
    _echo_plan(
        plan,
        stage="evaluate-plan",
        approval_report=approval_report,
        run_url=approval_report_run_url,
    )


@app.command("authorize-trigger")
def authorize_trigger_cmd(
    sender_type: Annotated[
        str, typer.Option(help="github.event.sender.type (a 'Bot' sender is the App handoff).")
    ],
    actor: Annotated[str, typer.Option(help="github.actor that applied the run:* label.")],
    repo: Annotated[str, typer.Option(help="github.repository, owner/name.")],
    bot_actor: Annotated[
        str | None,
        typer.Option(
            help="Pin the Bot handoff to this login — the pipeline App's own "
            + "bot account; any other Bot sender is refused outright. Absent, "
            + "any Bot sender is trusted as the App handoff."
        ),
    ] = None,
) -> None:
    """Authorize a run:* label trigger, or refuse and exit non-zero (fail closed).

    The pipeline's trust boundary: a Bot sender is the trusted App handoff
    (pinnable to one login via ``--bot-actor``), any other actor needs
    write-or-higher collaborator access (looked up via ``gh api``). Every
    label-triggered ``run:*`` workflow runs this *before* it mints a token,
    assumes the S3 role, or runs an agent. Prints the authorization line and
    exits 0 when allowed;
    prints the refusal to stderr and exits 1 otherwise. Needs ``GH_TOKEN`` in
    the environment for the permission lookup.
    """
    decision = authorize_trigger(sender_type, actor, repo, bot_actor=bot_actor)
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


def _scan_listed_files(
    files: list[Path] | None,
    secrets: list[str],
    *,
    entropy: bool,
    noun: str,
    run_id: str | None = None,
) -> tuple[list[secretscan.Finding], bool]:
    """Scan caller-named files beside the change set; a missing one fails closed.

    The caller writes each file immediately before scanning, so absence is a
    misconfigured gate, never an empty surface. ``entropy`` passes through to
    the scanner — off for a transcript, whose format guarantees high-entropy
    ids as ordinary content — and so does ``run_id``, which narrows the
    entropy rule alone and is therefore inert wherever that rule is off.
    """
    findings: list[secretscan.Finding] = []
    misconfigured = False
    for path in files or []:
        if path.is_file():
            findings.extend(
                secretscan.scan_file(path, str(path), secrets, entropy=entropy, run_id=run_id)
            )
        else:
            misconfigured = True
            typer.echo(f"::error::secret-scan: {noun} {path} is missing", err=True)
    return findings, misconfigured


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
    transcript_file: Annotated[
        list[Path] | None,
        typer.Option(
            help="An engine transcript to scan with every detector except the "
            "generic high-entropy heuristic (repeatable; must exist, like "
            "--extra-file). A transcript's server-generated tool and request "
            "ids are high-entropy by format, so the generic heuristic convicts "
            "every real file and the artifact it gates never publishes with "
            "content; literal containment of each --known-secret-env credential "
            "and the structured credential shapes still run and are the "
            "detectors that can name a secret there."
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
    run_id: Annotated[
        str,
        typer.Option(
            help="The run being collected. Exempts that run's own ledger paths "
            "— the `predictions/` / `evaluations/` layouts and the "
            "cell-relative forms (`<actor>/<run id>[/<file stem>]`, "
            "`<evaluator>/<predictor>/<run id>`) — from the entropy heuristic "
            "only: a cell's logged shell commands name its own output paths, "
            "which are neither secret nor random but score like one. Every "
            "other detector is unaffected, and the run id segment (last, or "
            "second-to-last before a file stem) must equal this value exactly."
        ),
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
    too short, a missing ``--extra-file`` or ``--transcript-file``) fails the
    same way rather than silently dropping a detector or a surface. A
    ``--transcript-file`` is scanned without the generic high-entropy
    heuristic only — see the option's help for why that surface needs it, and
    ``--run-id`` for the one path shape that heuristic is told to skip.
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
    own_run = run_id or None
    # The run id is the single input that defines the exemption's shape, so a
    # value that is not a run id (an interpolation gone wrong) is a scan
    # misconfiguration, not a wider exemption.
    if own_run is not None and not secretscan.is_run_id_shaped(own_run):
        misconfigured = True
        own_run = None
        typer.echo(
            "::error::secret-scan: --run-id is not a run id; "
            "the own-run exemption cannot be applied",
            err=True,
        )
    findings = secretscan.scan_changes(changes, Path(), secrets, run_id=own_run)
    for files, entropy, noun in (
        (extra_file, True, "extra file"),
        (transcript_file, False, "transcript file"),
    ):
        listed_findings, missing = _scan_listed_files(
            files, secrets, entropy=entropy, noun=noun, run_id=own_run
        )
        findings.extend(listed_findings)
        misconfigured = misconfigured or missing
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


@app.command("assert-required-contexts")
def assert_required_contexts_cmd(
    workflows: Annotated[
        Path,
        typer.Option(help="Workflow directory of the branch PRs are merged INTO (its files run)."),
    ],
    context: Annotated[
        list[str] | None,
        typer.Option(help="A context the branch's ruleset requires today (repeatable)."),
    ] = None,
    candidate: Annotated[
        list[str] | None,
        typer.Option(help="A context you are considering requiring; reported, never fatal."),
    ] = None,
    base_branch: Annotated[
        str,
        typer.Option(help="Branch PRs target, to honour workflows' `branches:` filters. '' = any."),
    ] = "",
) -> None:
    """Check that every required status check has a job that can report it.

    A required context with no producing job on the base branch leaves every PR
    into that branch pending forever — the auto-merging collect PRs first, so
    data production stops on a rule that reads like a tightening. Exits non-zero
    naming any such context.

    ``--candidate`` answers the other half: whether a context is *safe* to
    require yet. A candidate whose job has landed on the branch is ready; one
    that has not promoted is not, and requiring it now would hang.
    """
    required = list(context or [])
    branch = base_branch or None
    # One scan, so the fatal and advisory answers cannot disagree.
    produced = produced_contexts(workflows, branch)
    hanging = sorted({name for name in required if name and name not in produced})
    for name in sorted({name for name in (candidate or []) if name}):
        verdict = "ready to require" if name in produced else "NOT yet requireable"
        reason = "a job on this branch reports it" if name in produced else "no job reports it"
        typer.echo(f"{verdict}: {name!r} — {reason}")
    if hanging:
        typer.echo(
            "::error::required context(s) no job on this branch reports, so every PR "
            f"into it would hang: {', '.join(hanging)}",
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(f"required contexts OK ({len(required)} checked)")


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
        typer.Option(
            help="File holding `git diff --cached --name-only -- metrics/ data/scope/` "
            "output to summarize."
        ),
    ],
    run_id: Annotated[
        str, typer.Option(help="Refresh run id for the PR prose; defaults to now (UTC).")
    ] = "",
) -> None:
    """Render the review-PR plan for a metrics refresh (``run-analytics``).

    The workflow regenerates the metrics artifacts (the same tested commands the
    stages run), stages them and reads ``git diff --cached --name-only -- metrics/
    data/scope/`` so a brand-new artifact is not missed, and hands the changed paths
    here; this prints a
    JSON plan ``{"changed":[...],"pr":<branch/title/commit/body|null>}`` with a
    per-artifact headline read from the regenerated files. ``pr`` is null when
    nothing changed (byte-stable artifacts -> empty diff -> no PR), so the workflow
    can exit quietly. The prose is rendered here, not with ``jq`` and a heredoc in
    the workflow, mirroring ``cleanup-out-of-scope-predictions``.
    """
    settings = get_settings()
    changed = [line.strip() for line in changed_file.read_text().splitlines() if line.strip()]
    # Repo-relative paths now, since the refresh carries `data/scope/scope.json`
    # alongside `metrics/`; the roots are siblings under the repo.
    # The roster feeds only a rendered PR's leaderboard line, so the no-change
    # path (empty diff -> null plan) never touches the config file at all.
    roster = (
        [predictor.id for predictor in enabled_predictors(settings.config_root / "predictors.yaml")]
        if changed
        else None
    )
    pr = metrics_refresh.render_refresh_pr(
        changed, settings.metrics_root.parent, run_id or ids.run_id(), predictor_roster=roster
    )
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


def _collect_plan_json(plan: CollectPlan, *, role: FinalizeRole, run_id: str) -> dict[str, object]:
    return {
        "ready": _pr_plan_json(plan.ready),
        "partial": _pr_plan_json(plan.partial),
        # The small auto-merging PR a wholesale-failed run opens to persist its
        # per-cell failure facts when there is no ready/partial PR to carry them;
        # null on any run that opened one (its facts ride that PR) and on a run
        # with no failed cell. Driven through the same loop as ready/partial.
        "facts_only": _pr_plan_json(plan.facts_only),
        "skipped": [
            {"actor": c.actor, "court": c.court, "docket": c.docket, "event_id": c.event_id}
            for c in plan.skipped
            if isinstance(c, CellStatus)
        ],
        "flags": plan.flags_markdown,
        # The harness-side counterpart of `flags`: what this run's captured
        # retrieval says the upstream quota did to it. It already rides the PR
        # body, but it leaves the process here too, so the surface that echoes
        # `flags` into the Actions summary can echo this beside it without
        # re-reading a single artifact. Empty on a genuinely clean run.
        "throttle": plan.throttle_markdown,
        # The corpus-side counterpart of `throttle`: which cells asked the
        # corpus index for priors and did not get them, plus the tripwire on
        # whether code-mode capture could have seen such an attempt at all. It
        # rides the PR body and leaves the process here for the same reason.
        # The warning half is empty on a run where every attempt was served;
        # the tripwire half still prints there, because it reports on what
        # capture could see rather than on what the corpus did.
        "prior_availability": plan.prior_availability_markdown,
        "feedback_comment": plan.feedback_comment,
        "stalled": plan.stalled,
        "dead_actors": list(plan.dead_actors),
        "noun": plan.noun,
        "missing_artifacts": list(plan.missing_artifacts),
        "uncovered_cells": [
            {"actor": c.actor, "court": c.court, "docket": c.docket, "event_id": c.event_id}
            for c in plan.uncovered_cells
        ],
        # The per-cell failure facts `record-cell-failures` writes into the ledger
        # so the attempt cap can count them. Computed here (pure) and carried on the
        # plan JSON, so the collect step's writer step reads the already-decided
        # partition rather than re-globbing the artifacts.
        "cell_failures": [
            f.model_dump(mode="json") for f in cell_failures(plan, run_id=run_id, role=role)
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


def _event_id_from_path(path: Path) -> str:
    """The event id an artifact path carries (``.../events/<event id>/...``), or ``""``.

    Neither ``RetrievalLog`` nor ``AgentToolingFeedback`` records the event, so
    the path is the only place a per-cell identity can pick it up. Searched from
    the right, because the case segments are upstream of it and a directory that
    happens to be named ``events`` higher up must not win. A path that carries
    none — a hand-built fixture, a layout change — yields ``""`` rather than
    raising: it feeds a notification, and a missing segment must not take down
    the aggregation carrying the run's only copy of its output.
    """
    parts = path.parts[:-1]
    for index in range(len(parts) - 2, -1, -1):
        if parts[index] == "events":
            return parts[index + 1]
    return ""


def _cell_name(log: RetrievalLog, path: Path) -> str:
    """One cell as ``case/event/actor``, for a note that names cells rather than counts."""
    return "/".join(part for part in (log.case_id, _event_id_from_path(path), log.actor_id) if part)


def _reported_corpus_use(log: RetrievalLog, path: Path) -> bool | None:
    """This cell's own ``tooling.json`` answer on whether it used the corpus query.

    ``None`` where there is no answer to read — no sibling report, one that
    does not parse, or one describing a different cell (an earlier run's report
    riding along in the artifact). Unknown is kept distinct from ``False``
    throughout, because "the cell said it got nothing" and "the cell said
    nothing" are different claims and only the first is evidence of starvation.
    """
    try:
        report = AgentToolingFeedback.model_validate_json(
            (path.parent / "tooling.json").read_text()
        )
    except (OSError, ValueError):
        return None
    if (report.case_id, report.run_id, report.actor_id, report.role) != (
        log.case_id,
        log.run_id,
        log.actor_id,
        log.role,
    ):
        return None
    return report.used_corpus_query


def _add_prior_cell(
    rollup: PriorAvailabilityRollup, log: RetrievalLog, path: Path
) -> PriorAvailabilityRollup:
    """Fold one cell's log (and its sibling tooling report) into the prior rollup."""
    rollup = replace(rollup, cells=rollup.cells + 1)
    if any(call.tool == CODE_MODE_PARENT_TOOL for call in log.calls):
        rollup = replace(rollup, code_mode_cells=rollup.code_mode_cells + 1)
    if code_mode_lift_blind(log.calls):
        rollup = replace(rollup, lift_blind_cells=rollup.lift_blind_cells + 1)
    if not attempted_corpus_query(log.calls):
        return rollup
    rollup = replace(rollup, attempted=rollup.attempted + 1)
    served = _reported_corpus_use(log, path)
    if served:
        return replace(rollup, served=rollup.served + 1)
    name = _cell_name(log, path)
    if served is None:
        return replace(rollup, unreported=(*rollup.unreported, name))
    return replace(rollup, starved=(*rollup.starved, name))


def _add_throttle_cell(rollup: ThrottleRollup, log: RetrievalLog) -> ThrottleRollup:
    """Fold one cell's log into the throttle rollup.

    Denominated by :func:`~fedcourtsai.schemas.observed_mcp_conditions` — the
    same helper the log's own ``throttled_calls`` and the corpus rollup's
    per-engine rate denominate by — so the three figures a maintainer may read
    side by side mean one thing. A cell it leaves empty (capture-blind, or
    calling no manifest tool) is counted as ``blind_cells`` rather than as a
    clean cell, because it could not have shown a throttle and must not read as
    evidence of none.
    """
    observed = observed_mcp_conditions(log.calls)
    if not observed:
        return replace(rollup, blind_cells=rollup.blind_cells + 1)
    throttled = sum(1 for call in observed if call.result_status == "throttled")
    return replace(
        rollup,
        cells=rollup.cells + 1,
        throttled_cells=rollup.throttled_cells + bool(throttled),
        calls=rollup.calls + len(observed),
        throttled_calls=rollup.throttled_calls + throttled,
    )


def _load_retrieval_rollups(
    status_dir: Path, run_id: str
) -> tuple[ThrottleRollup, PriorAvailabilityRollup]:
    """Summarize this run's captured retrieval from the cell artifacts.

    One walk, two roll-ups, because both read the same files and the fan-out
    they are read across is wide: what the shared upstream quota did to the run
    (:class:`~fedcourtsai.collect.ThrottleRollup`) and whether the corpus index
    served the cells that asked it for priors
    (:class:`~fedcourtsai.collect.PriorAvailabilityRollup`).

    The same walk shape as :func:`_load_flag_sets`, and for the same reason:
    each cell uploads its whole ``data/`` subtree, so the run's
    ``retrieval_log.json`` files land wherever the cell's own case path puts
    them. The two filters are the same two as well — **run id**, because every
    artifact also carries every *previously committed* log and an earlier run's
    throttling is not this run's; and **identity**, keyed on the cell a log
    describes, because a log committed by an earlier cell of this same run rides
    along in later cells' artifacts and would otherwise be counted once per
    cell. That identity takes its event id from the path, since a log records
    the case and the actor but not the event: a run covering two events of one
    case for one actor is two cells, and keying without the event would fold
    the second away — invisibly, in a note that names cells one by one.

    The run-id filter runs twice, once in the glob and once on the parsed
    record, and the pair is not redundant. Both roles key a cell's directory on
    its run id, so the glob skips the whole committed history without opening
    it — every log the ledger has ever carried rides in every artifact, so a
    parse-everything walk would validate that history once per cell of the
    fan-out. The record's own ``run_id`` is what the count is actually keyed
    on, so the cheap path filter can never be the thing that decides.

    A malformed or unreadable log counts as a throttle-blind cell rather than
    being dropped: it is a cell of this run — its path carries the run id —
    whose condition nothing can read, which is exactly what that counter means.
    It contributes nothing to the prior roll-up, whose attempt side needs rows
    it does not have. Neither is ever fatal, because these are notifications
    and must never take down the aggregation that carries the run's only copy
    of its output.
    """
    seen: set[tuple[str, str, str, str, str]] = set()
    throttle = ThrottleRollup()
    priors = PriorAvailabilityRollup()
    for path in sorted(status_dir.glob(f"**/{run_id}/retrieval_log.json")):
        try:
            log = RetrievalLog.model_validate_json(path.read_text())
        except (OSError, ValueError):
            throttle = replace(throttle, blind_cells=throttle.blind_cells + 1)
            continue
        if log.run_id != run_id:
            continue
        identity = (
            log.case_id,
            _event_id_from_path(path),
            log.actor_id,
            str(log.role),
            log.run_id,
        )
        if identity in seen:
            continue
        seen.add(identity)
        throttle = _add_throttle_cell(throttle, log)
        priors = _add_prior_cell(priors, log, path)
    return throttle, priors


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
    fully-failed run that opens no PR. ``throttle`` and ``prior_availability``
    are the two harness-rendered retrieval notes, read from the cells' own
    captured logs and likewise appended to the PR body: what the shared upstream
    quota did to the run, and whether the corpus index served the cells that
    asked it for priors. Both are empty on a run with nothing to report.
    """
    cells = []
    for status_path in sorted(status_dir.glob("**/status.json")):
        artifact_dir = str(status_path.parent.relative_to(status_dir))
        cells.append(
            CellStatus.from_dict(json.loads(status_path.read_text()), artifact_dir=artifact_dir)
        )
    throttle, priors = _load_retrieval_rollups(status_dir, run_id)
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
        # Whether the shared upstream quota starved this run's retrieval. Read
        # from the cells' harness-captured logs, not from what an agent said:
        # the 429 evidence lives only in the result payload, which capture
        # digests away, so the parse-time marker is the last place it is legible.
        throttle=throttle,
        # And whether the corpus index served the cells that asked it for
        # priors. A timed-out `fedcourts query` fails no cell — the cell
        # predicts from whatever else it had — so without a run-level count the
        # only trace is one line in one cell's tooling report.
        prior_availability=priors,
    )
    typer.echo(
        json.dumps(_collect_plan_json(plan, role=role, run_id=run_id), separators=(",", ":"))
    )


@app.command("record-cell-failures")
def record_cell_failures_cmd(
    plan_file: Annotated[
        Path, typer.Option(help="The `collect-plan` JSON (its `cell_failures` list is read).")
    ],
    data_root: Annotated[Path, typer.Option(help="The git-ledger root to write facts under.")],
) -> None:
    """Write one durable ``attempt.json`` per failed cell into the git ledger.

    The writer side of the per-cell attempt cap. ``collect`` is the only observer
    of a cell that ran and produced no usable artifact, but it is corpus-blind, so
    each failure is recorded as a run-scoped ledger file the pull/live derivers
    later count (:func:`fedcourtsai.matrix.cell_failure_count`). The failure
    partition is decided by ``collect-plan`` (pure) and carried in its JSON, so this
    step only materializes those facts — it re-globs nothing. Run-scoped paths make
    a rerun overwrite its own facts rather than duplicate them, and the facts ride
    the run's existing per-run PR (append-only under ``data/``, passing the path
    jail) because this runs before the ``git add data/`` union.
    """
    payload = json.loads(plan_file.read_text())
    facts = [CellFailure.model_validate(entry) for entry in payload.get("cell_failures", [])]
    for fact in facts:
        events = CasePaths(data_root, fact.court, fact.docket).event(fact.event_id)
        if fact.seam == "predict":
            destination = events.prediction_attempt(fact.actor, fact.run_id)
        else:
            destination = events.evaluation_attempt(fact.actor, fact.run_id)
        write_json(destination, fact)
    typer.echo(f"recorded {len(facts)} cell-failure fact(s) under {data_root}")


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


@app.command("post-issue-comment")
def post_issue_comment_cmd(
    issue: Annotated[int, typer.Option(help="Issue number to comment on.")],
    repo: Annotated[str, typer.Option(help="owner/name of the repository.")],
    marker: Annotated[
        str,
        typer.Option(
            help="Hidden key identifying this report; a comment already carrying it "
            "is not posted again."
        ),
    ],
    body_file: Annotated[Path, typer.Option(help="The rendered comment body.")],
) -> None:
    """Post a comment on an issue exactly once, keyed by ``--marker``.

    For the collect job's stall and secret-scan reports. Their step reruns
    whenever the collect job does — and rerunning collect is the documented
    recovery for a transfer failure — so without the marker every recovery
    attempt would stack another copy of the same warning on the trigger issue,
    burying the signal it exists to raise. An empty/absent body posts nothing.
    """
    body = body_file.read_text(encoding="utf-8") if body_file.exists() else ""
    if not body.strip():
        typer.echo("nothing to post")
        return
    typer.echo(post_once(repo=repo, issue=issue, marker=marker, body=body))


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
