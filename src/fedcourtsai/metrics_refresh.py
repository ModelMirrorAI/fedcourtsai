"""Scheduled refresh of the committed metrics artifacts.

The three metrics artifacts — ``metrics/leaderboard.json``, ``metrics/backtest.json``,
and ``metrics/statpack.{json,md}`` — are deterministic DVC stages, but nothing
regenerated them as their inputs (the ``data/`` evaluations ledger, the corpus) grew,
so they drifted stale on ``main`` between manual ``dvc repro`` runs. The
``run-analytics`` workflow's weekly ``metrics-refresh`` job closes that gap: it
regenerates the artifacts with the same tested ``fedcourts`` commands the stages
run, and — when anything changed — lands the result as a **reviewed** PR (never a
direct commit to ``main``, never auto-merged).

This module is the tested half of that workflow: given the changed paths (``git
diff --name-only -- metrics/``, plumbed by the workflow), it renders the branch and
PR prose, with a per-artifact headline read from the regenerated artifact itself.
Byte-stable artifacts mean a no-op refresh produces no changed paths and therefore
no PR.

The branch name is **fixed** (:data:`REFRESH_BRANCH`) rather than run-id-suffixed:
each refresh regenerates from the current ``main``, so an unmerged refresh PR is
strictly superseded by the next one — the workflow force-pushes the branch and the
open PR updates in place instead of stacking a new PR per schedule tick.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from .schemas import Backtest, CertBacktest, Leaderboard, StatPack
from .serialize import read_model

REFRESH_BRANCH = "metrics/refresh"

# Display order for the artifacts in the PR title and table.
_ARTIFACT_ORDER = ("leaderboard.json", "backtest.json", "statpack.json", "statpack.md")


class MetricsRefreshPr(BaseModel):
    """The branch and PR prose for a refresh, rendered here so the workflow only plumbs."""

    branch: str
    title: str
    commit_message: str
    body: str


def _headline(metrics_root: Path, filename: str) -> str:
    """One human line summarizing a refreshed artifact, read from the artifact itself."""
    if filename == "leaderboard.json":
        board = read_model(metrics_root / filename, Leaderboard)
        return (
            f"{board.predictors_ranked} predictor(s) ranked from "
            f"{board.evaluations_total} evaluation(s) "
            f"({board.forward_evaluations} forward / "
            f"{board.retrospective_evaluations} retrospective)"
        )
    if filename == "backtest.json":
        bt = read_model(metrics_root / filename, Backtest)
        return (
            f"{bt.predictors_evaluated} predictor(s) over {bt.events_scored} "
            f"resolved event(s) (retrospective by construction)"
        )
    if filename == "statpack.json":
        pack = read_model(metrics_root / filename, StatPack)
        return f"{pack.corpus_rows} corpus case(s): {pack.resolved} resolved / {pack.open} open"
    if filename == "statpack.md":
        return "human-readable statpack companion"
    return "refreshed"


def render_refresh_pr(
    changed: list[str], metrics_root: Path, run_id: str
) -> MetricsRefreshPr | None:
    """Render the review PR (branch / title / commit / body) for a refresh's changes.

    ``changed`` is the repo-relative output of ``git diff --name-only -- metrics/``
    after the regeneration commands ran; empty means the committed artifacts were
    already current and no PR should open (returns ``None``). The markdown lives in
    tested code rather than assembled with ``jq`` and a heredoc in the workflow,
    mirroring :func:`fedcourtsai.cleanup.render_cleanup_pr`.
    """
    names = {Path(path).name for path in changed}
    ordered = [name for name in _ARTIFACT_ORDER if name in names]
    if not ordered:
        return None
    # Name the artifacts (statpack.json/.md collapse to one) so the title reads
    # "metrics: refresh leaderboard, statpack" rather than a bare count.
    stems = list(dict.fromkeys(Path(name).stem for name in ordered))
    title = f"metrics: refresh {', '.join(stems)}"
    rows = "\n".join(f"| `metrics/{name}` | {_headline(metrics_root, name)} |" for name in ordered)
    body = (
        "Scheduled metrics refresh: the committed artifacts drifted from their "
        "inputs (the `data/` evaluations ledger and the corpus), so the scheduled "
        "refresh regenerated them with the same tested `fedcourts` commands the DVC stages "
        "run. Deterministic — an unchanged input produces a byte-identical artifact, "
        "so only genuinely stale files appear here.\n\n"
        "| artifact | now holds |\n"
        "|----------|-----------|\n"
        f"{rows}\n\n"
        f"Refresh run `{run_id}`. Review and merge — this PR is intentionally **not** "
        "auto-merged; if it sits unmerged, the next scheduled refresh force-pushes "
        "this same branch and the PR updates in place.\n"
    )
    return MetricsRefreshPr(
        branch=REFRESH_BRANCH,
        title=title,
        commit_message=title,
        body=body,
    )


BACKTEST_BRANCH = "metrics/cert-backtest"


def render_backtest_pr(
    metrics_root: Path, run_id: str, *, limit: int, engine: str
) -> MetricsRefreshPr | None:
    """Render the review PR for a maintainer-triggered cert back-test run.

    Reads the freshly-written ``metrics/cert-backtest.json`` for its headline
    (top lift over the always-deny floor, sample size) so the PR states what the
    run measured, not just that it ran. Returns ``None`` when the report is
    absent (the command wrote nothing) — the workflow then exits quietly. The
    markdown lives in tested code rather than a workflow heredoc, mirroring
    :func:`render_refresh_pr`.
    """
    report_path = metrics_root / "cert-backtest.json"
    if not report_path.exists():
        return None
    report = read_model(report_path, CertBacktest)
    if report.entries:
        top = report.entries[0]
        headline = (
            f"top predictor `{top.predictor_id}`: lift "
            f"**{top.lift_over_always_denied:+.1%}** over always-deny "
            f"(accuracy {top.accuracy:.0%}, Brier {top.mean_brier_score:.3f})"
        )
    else:
        headline = "no predictors scored (empty set)"
    title = f"metrics: cert back-test over {report.events_scored} petition(s)"
    body = (
        f"Maintainer-triggered cert back-test (run `{run_id}`): the enabled "
        f"predictors replayed over the {report.events_scored} most recently "
        f"decided modern discretionary-cert petition(s) with outcomes hidden "
        f"(`--limit {limit} --engine {engine}`), scored against the realized "
        "grant/deny. Retrospective by construction — iteration signal, never "
        "claimable performance.\n\n"
        f"- {headline}\n"
        f"- always-deny floor: **{report.always_denied_accuracy:.0%}** over this set\n"
        f"- predictors on the board: {report.predictors_evaluated}\n\n"
        "Review and merge — this PR is intentionally **not** auto-merged; a "
        "later run force-pushes this same branch and the PR updates in place.\n"
    )
    return MetricsRefreshPr(
        branch=BACKTEST_BRANCH,
        title=title,
        commit_message=title,
        body=body,
    )
