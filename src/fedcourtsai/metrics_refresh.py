"""Scheduled refresh of the committed metrics artifacts.

The metrics artifacts are deterministic roll-ups whose inputs (the ``data/``
evaluations ledger, the corpus) move without them. The ``run-analytics``
workflow's weekly ``metrics-refresh`` job keeps the scheduled set current —
``metrics/leaderboard.json``, ``metrics/claim-scores.json``,
``metrics/backtest.json``, and ``metrics/statpack.{json,md}`` — by rerunning
the tested ``fedcourts`` commands
(``leaderboard`` / ``claim-scores`` / ``backtest`` / ``statpack``) and, when anything changed,
landing the result as a **reviewed** PR (never a direct commit to ``main``,
never auto-merged). ``metrics/docket.{json,md}`` is committed alongside them but
is regenerated on demand with ``fedcourts docket``, not on the schedule.

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

from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from .claim_metrics import agreement_summary
from .schemas import (
    Backtest,
    CertBacktest,
    ClaimScoreBoard,
    DocketPack,
    Leaderboard,
    ScopeManifest,
    StatPack,
)
from .serialize import read_model

REFRESH_BRANCH = "metrics/refresh"

# Display order for the artifacts a refresh PR may carry, as repo-relative paths.
# It is also the filter: a changed path not listed here drives no PR and appears
# in none, so an artifact must be named to be reportable at all. The docket pack
# is listed defensively: the analytics workflow does not regenerate it, so it
# should never appear here — but if it ever does, being named is what keeps it in
# the PR body rather than silently absent from it.
#
# `data/scope/scope.json` is the one entry outside `metrics/`. It is a
# deterministic, git-tracked artifact regenerated from the corpus plus the
# committed case tree, which is exactly what this refresh exists to keep current
# — and it is the only surface that publishes the salience decision, so drift in
# it falsifies a claim `README.md` makes rather than merely aging a number.
_ARTIFACT_ORDER = (
    "metrics/leaderboard.json",
    "metrics/claim-scores.json",
    "metrics/backtest.json",
    "metrics/statpack.json",
    "metrics/statpack.md",
    "metrics/docket.json",
    "metrics/docket.md",
    "data/scope/scope.json",
)


class MetricsRefreshPr(BaseModel):
    """The branch and PR prose for a refresh, rendered here so the workflow only plumbs."""

    branch: str
    title: str
    commit_message: str
    body: str


# The rendered companions carry no headline of their own: the figures live in
# the JSON sibling listed beside them.
def _scope_headline(path: Path) -> str:
    """The scope manifest's line: the public set and how it splits.

    A `skipped` manifest is called out rather than reported as zero cases — the
    command writes one when the corpus is not on disk, and "0 public cases" would
    read as the public set collapsing rather than as a missing input.
    """
    manifest = read_model(path, ScopeManifest)
    if manifest.skipped:
        return "skipped (no corpus on disk at refresh time)"
    return (
        f"{manifest.cases} public case(s): {manifest.eligible} eligible / "
        f"{manifest.excluded} excluded"
    )


# Artifacts whose headline does not come from reading a metrics model: the two
# rendered companions, which have nothing to summarize, and the scope manifest,
# which is a different model in a different tree. Keyed by full relative path so
# a same-named file elsewhere cannot pick one up.
_SPECIAL_HEADLINES: dict[str, Callable[[Path], str]] = {
    "metrics/statpack.md": lambda _: "human-readable statpack companion",
    "metrics/docket.md": lambda _: "human-readable docket-pack companion",
    "data/scope/scope.json": _scope_headline,
}


def _leaderboard_headline(path: Path) -> str:
    """The board's line. Naming the scope keeps a refresh PR that drops the
    board to 0 during the shakedown reading as the frozen headline, not a
    regression."""
    board = read_model(path, Leaderboard)
    return (
        f"[{board.process_scope}] {board.predictors_ranked} predictor(s) ranked from "
        f"{board.evaluations_total} evaluation(s) "
        f"({board.forward_evaluations} forward / "
        f"{board.retrospective_evaluations} retrospective / "
        f"{board.procedural_evaluations} procedural)"
    )


def _claim_scores_headline(path: Path) -> str:
    """The claim-score surface's line. The scope and the suppression state are
    the headline while the ledger carries no blocks: "0 of 0 ... no cells" is
    the honest empty state."""
    claims = read_model(path, ClaimScoreBoard)
    return (
        f"[{claims.process_scope}] {claims.cells_with_claims} of "
        f"{claims.evaluations_total} evaluation(s) carry claim scores; "
        f"forward judge agreement: {agreement_summary(claims.forward_agreement)}"
    )


def _backtest_headline(path: Path) -> str:
    bt = read_model(path, Backtest)
    return (
        f"{bt.predictors_evaluated} predictor(s) over {bt.events_scored} "
        f"resolved event(s) (retrospective by construction)"
    )


def _statpack_headline(path: Path) -> str:
    pack = read_model(path, StatPack)
    return f"{pack.corpus_rows} corpus case(s): {pack.resolved} resolved / {pack.open} open"


def _docket_headline(path: Path) -> str:
    """The docket pack's line, led by the figures that move between refreshes:
    the section count is a constant, so a row headlined by it would never show
    what changed."""
    docket = read_model(path, DocketPack)
    return (
        f"{docket.coverage.live_slice_rows} live-slice case(s) "
        f"({docket.coverage.live_slice_resolved} resolved) over "
        f"{len(docket.terms)} Term(s)"
    )


# The metrics-model artifacts, keyed by filename (they all live under
# `metrics/`; anything path-ambiguous belongs in _SPECIAL_HEADLINES instead).
_FILENAME_HEADLINES: dict[str, Callable[[Path], str]] = {
    "leaderboard.json": _leaderboard_headline,
    "claim-scores.json": _claim_scores_headline,
    "backtest.json": _backtest_headline,
    "statpack.json": _statpack_headline,
    "docket.json": _docket_headline,
}


def _headline(path: Path, relpath: str) -> str:
    """One human line summarizing a refreshed artifact, read from the artifact itself."""
    special = _SPECIAL_HEADLINES.get(relpath)
    if special is not None:
        return special(path)
    reader = _FILENAME_HEADLINES.get(Path(relpath).name)
    return reader(path) if reader is not None else "refreshed"


def render_refresh_pr(changed: list[str], repo_root: Path, run_id: str) -> MetricsRefreshPr | None:
    """Render the review PR (branch / title / commit / body) for a refresh's changes.

    ``changed`` is the repo-relative output of ``git diff --name-only`` over the
    refreshed paths after the regeneration commands ran; empty means the committed
    artifacts were already current and no PR should open (returns ``None``).
    Matched on the full relative path rather than the filename, so two artifacts
    sharing a basename across directories can never be confused for one another.

    The markdown lives in tested code rather than assembled with ``jq`` and a
    heredoc in the workflow, mirroring
    :func:`fedcourtsai.cleanup.render_cleanup_pr`.
    """
    paths = {path.strip() for path in changed if path.strip()}
    ordered = [rel for rel in _ARTIFACT_ORDER if rel in paths]
    if not ordered:
        return None
    # Name the artifacts (statpack.json/.md collapse to one) so the title reads
    # "metrics: refresh leaderboard, statpack" rather than a bare count.
    stems = list(dict.fromkeys(Path(rel).stem for rel in ordered))
    title = f"metrics: refresh {', '.join(stems)}"
    rows = "\n".join(f"| `{rel}` | {_headline(repo_root / rel, rel)} |" for rel in ordered)
    body = (
        "Scheduled metrics refresh: the committed artifacts drifted from their "
        "inputs (the `data/` evaluations ledger and the corpus), so the scheduled "
        "refresh regenerated them with the same tested `fedcourts` commands the pipeline "
        "runs. Deterministic — an unchanged input produces a byte-identical artifact, "
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
