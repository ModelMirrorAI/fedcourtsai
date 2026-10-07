"""Scheduled refresh of the committed metrics artifacts.

The metrics artifacts are deterministic roll-ups whose inputs (the ``data/``
evaluations ledger, the corpus) move without them. The ``run-analytics``
workflow's weekly ``metrics-refresh`` job keeps the scheduled set current —
``metrics/leaderboard.json``, ``metrics/claim-scores.json``,
``metrics/backtest.json``, ``metrics/statpack.{json,md}``,
``metrics/big-cases.{json,md}``, and ``data/scope/scope.json`` — by rerunning
the tested ``fedcourts`` commands
(``leaderboard`` / ``claim-scores`` / ``backtest`` / ``statpack`` /
``big-cases`` / ``scope-manifest``) and, when anything changed,
landing the result as a **reviewed** PR (never a direct commit to ``main``,
never auto-merged). ``metrics/docket.{json,md}`` is committed alongside them but
is regenerated on demand with ``fedcourts docket``, not on the schedule.

This module is the tested half of that workflow: given the changed paths (``git
diff --cached --name-only -- metrics/ data/scope/``, plumbed by the workflow),
it renders the branch and
PR prose, with a per-artifact headline read from the regenerated artifact itself.
Byte-stable artifacts mean a no-op refresh produces no changed paths and therefore
no PR.

The branch name is **fixed** (:data:`REFRESH_BRANCH`) rather than run-id-suffixed:
each refresh regenerates from the current ``main``, so an unmerged refresh PR is
strictly superseded by the next one — the workflow force-pushes the branch and the
open PR updates in place instead of stacking a new PR per schedule tick.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from .claim_metrics import agreement_summary
from .leaderboard import entry_name
from .schemas import (
    CERT_BACKTEST_ARMS,
    Backtest,
    BigCaseBoard,
    CertBacktest,
    CertBacktestArm,
    CertBacktestDisclosure,
    CertBacktestEntry,
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
    "metrics/big-cases.json",
    "metrics/big-cases.md",
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
    "metrics/big-cases.md": lambda _: "human-readable big-case-board companion",
    "data/scope/scope.json": _scope_headline,
}


def _leaderboard_headline(path: Path, roster: Sequence[str] | None = None) -> str:
    """The board's line. Naming the scope keeps a refresh PR that drops the
    board to 0 during the shakedown reading as the frozen headline, not a
    regression. The ranked counts are the **cert stage's** and say so, with the
    unranked stage blocks' total appended — this is the line most likely to be
    quoted out of the body, and a bare "0 evaluation(s)" over a file holding
    populated stage blocks reads as an empty artifact.

    The audit figures append only where they have something to say, because
    the refresh PR body is the surface a maintainer actually reads: a
    leakage-exclusion count means cells were dropped from every figure above it
    (with the assessed denominator beside it, since a null bit is "not
    assessed" rather than "clean"), a
    supersession count means a standing may have moved on a re-grade, and
    unequal coverage means two entries were compared over different event sets.
    Neither is recoverable from the counts above them, and a build-time warning
    lands in the run log rather than here. The coverage clause carries the worst
    shortfall rather than a bare flag — a flag without a magnitude cannot be
    read — and it checks every population, ranked board and ``stage@moment``
    block alike, since a stage-only gap is as much a comparability hazard as a
    cert one. The shortfall scan iterates entries, so a predictor with **no
    entry at all** in a populated block is invisible to it; the roster check
    covers that hole, naming any configured predictor absent from a block other
    predictors were scored in, and the block it is absent from — the failure
    shape an engine-wide outage produces, whose comparability consequence
    depends on which population lost the engine.

    The stage clause sums ``evaluations_total`` and ``events_scored`` across
    blocks, which the stage schema's "nothing pools across blocks" contract
    tolerates for exactly this shape and no other: these are volume counts for
    an artifact-level inventory line, never rates or skill figures, and the
    event denominator travels beside the evaluation count so the volume cannot
    be read as a scored population.
    """
    board = read_model(path, Leaderboard)
    notes = ""
    if board.leakage_exclusion is not None and board.leakage_exclusion.excluded:
        notes += (
            f"; {board.leakage_exclusion.excluded} of "
            f"{board.leakage_exclusion.assessed} assessed cell(s) excluded as "
            "leakage-suspected"
        )
    if board.superseded_gradings:
        notes += f"; {board.superseded_gradings} superseded grading(s) collapsed away"
    populations = [("cert board", board.events_scored, board.entries)] + [
        (key, block.events_scored, block.entries) for key, block in board.stages.items()
    ]
    shortfalls = [
        (entry.events_scored - covered, entry_name(entry, entries), entry.events_scored, covered)
        for _label, covered, entries in populations
        for entry in entries
        if entry.events_scored < covered
    ]
    if shortfalls:
        _gap, predictor_id, scored, covered = min(shortfalls)
        notes += (
            f"; unequal scored-set coverage ({predictor_id} {scored}/{covered}) "
            "— not a cross-engine comparison"
        )
    if roster:
        rostered = set(roster)
        absences = [
            f"{predictor} from `{label}`"
            for label, _covered, entries in populations
            if entries
            for predictor in sorted(rostered - {entry.predictor_id for entry in entries})
        ]
        if absences:
            notes += (
                f"; absent from a populated block: {', '.join(absences)} "
                "— not a cross-engine comparison"
            )
    if board.stages:
        stage_evaluations = sum(block.evaluations_total for block in board.stages.values())
        stage_events = sum(block.events_scored for block in board.stages.values())
        notes = (
            f"; {stage_evaluations} evaluation(s) over {stage_events} scored "
            f"event(s) in {len(board.stages)} unranked stage block(s)" + notes
        )
    return (
        f"[{board.process_scope}] {board.predictors_ranked} predictor(s) ranked from "
        f"{board.evaluations_total} cert-stage evaluation(s) "
        f"({board.forward_evaluations} forward / "
        f"{board.retrospective_evaluations} retrospective / "
        f"{board.procedural_evaluations} procedural)"
        f"{notes}"
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


def _big_case_headline(path: Path) -> str:
    """The big-case board's line: the ranked population and its denominators.

    Deliberately carries no top-ranked case. The refresh PR body is quoted out
    of context more than any other surface here, and a case name beside a number
    reads as a finding about that case — which a stakes read cannot support.
    """
    board = read_model(path, BigCaseBoard)
    leakage = (
        f"; {board.rows_with_leakage_flag} row(s) leakage-flagged"
        if board.rows_with_leakage_flag
        else ""
    )
    # The scope is part of the headline, not a detail: `frozen` and `all` rank
    # different populations, so a bare case count read across two builds would
    # compare a selected hold-out against a census.
    held = f", {board.cases_out_of_scope} held off by the scope" if board.cases_out_of_scope else ""
    return (
        f"{board.cases} case(s) ranked over {board.scored_reads} scored stakes read(s) of "
        f"{board.current_reads} from {len(board.predictors)} predictor(s) at "
        f"`process_scope: {board.process_scope}`{held} (never scored, never ranked){leakage}"
    )


# The metrics-model artifacts, keyed by filename (they all live under
# `metrics/`; anything path-ambiguous belongs in _SPECIAL_HEADLINES instead).
_FILENAME_HEADLINES: dict[str, Callable[[Path], str]] = {
    # leaderboard.json is dispatched explicitly in `_headline` — its reader is
    # the one that takes the predictor roster, which a filename table of
    # single-argument readers cannot carry.
    "claim-scores.json": _claim_scores_headline,
    "backtest.json": _backtest_headline,
    "statpack.json": _statpack_headline,
    "docket.json": _docket_headline,
    "big-cases.json": _big_case_headline,
}


def _headline(path: Path, relpath: str, roster: Sequence[str] | None = None) -> str:
    """One human line summarizing a refreshed artifact, read from the artifact itself.

    ``roster`` reaches only the leaderboard's line — the one whose absence
    check needs to know which predictors are *configured*, not just which
    appear in the artifact.
    """
    special = _SPECIAL_HEADLINES.get(relpath)
    if special is not None:
        return special(path)
    if Path(relpath).name == "leaderboard.json":
        return _leaderboard_headline(path, roster)
    reader = _FILENAME_HEADLINES.get(Path(relpath).name)
    return reader(path) if reader is not None else "refreshed"


def render_refresh_pr(
    changed: list[str],
    repo_root: Path,
    run_id: str,
    predictor_roster: Sequence[str] | None = None,
) -> MetricsRefreshPr | None:
    """Render the review PR (branch / title / commit / body) for a refresh's changes.

    ``changed`` is the repo-relative output of ``git diff --cached --name-only`` over
    the refreshed paths, staged after the regeneration commands ran so a
    brand-new artifact is not missed; empty means the committed
    artifacts were already current and no PR should open (returns ``None``).
    Matched on the full relative path rather than the filename, so two artifacts
    sharing a basename across directories can never be confused for one another.
    ``predictor_roster`` is the configured predictor ids, for the leaderboard
    line's absent-predictor check; ``None`` skips that check rather than
    treating an empty roster as universal absence.

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
    rows = "\n".join(
        f"| `{rel}` | {_headline(repo_root / rel, rel, predictor_roster)} |" for rel in ordered
    )
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


def granted_in_set(report: CertBacktest) -> int | None:
    """Granted-side outcomes in the replayed set, or ``None`` when unrecoverable.

    What a lift is measured on is the *granted* side of the binary target, and
    cert's denial skew makes a draw with none of them an ordinary outcome at a
    small sample — one where every denial-heavy predictor ties the floor and the
    ranking is noise. So every surface that quotes the floor — the review PR,
    and the weekly digest's own line — says how many there were.

    The always-deny floor cannot answer it: that is the **denied** share, and a
    dismissal is neither denied nor granted, so ``1 - floor`` overstates the
    granted side by the dismissal-bearing draws. The calibration view can:
    every replayed petition lands in exactly one probability bin, so a bin's
    ``predictions x observed_granted_rate`` is its granted count and the sum
    over bins is the set's. It has to come from an entry that scored the **whole
    set**: an entry short some cells (``provenance.lost_cells``) bins only what
    it forecast, and reading the board's granted count off it would understate
    the draw. The offline reference baselines are pure functions of the corpus
    and are never short, so on any report that ran them there is such an entry.
    ``None`` where no entry accounts for the whole set, so a caller states
    nothing rather than a wrong number.
    """
    for entry in report.entries:
        bins = entry.calibration
        if bins and sum(one.predictions for one in bins) == report.events_scored:
            return round(sum(one.predictions * one.observed_granted_rate for one in bins))
    return None


#: A display rule, not a statistical threshold: below this many petitions the
#: review PR states a lift in petitions beside its percentage points, and a
#: lead at the top as a margin in petitions. One petition is worth ``100 / n``
#: points, so under a hundred a single outcome moves the figure by more than a
#: whole point, and a points figure alone hides that it counts a few
#: outcomes. The registered fortnightly draw is ten, where one petition is ten
#: points and the count is the measurement.
SMALL_N = 100


@dataclass(frozen=True)
class OutcomeMix:
    """The replayed set's realized outcomes, split three ways.

    ``other`` is what is neither denied nor grant-family — a dismissal or a
    withdrawal (the replay only takes petitions with a machine-readable
    disposition). Stated, not left as ``n - denied - granted``, because the
    always-deny floor is the denied share and ``1 - floor`` is not the granted
    share whenever this is non-zero.
    """

    denied: int
    granted: int
    other: int

    def text(self) -> str:
        return f"{self.denied} denied · {self.granted} granted · {self.other} dismissed/withdrawn"


def outcome_mix(report: CertBacktest) -> OutcomeMix | None:
    """The set's denied / grant-family / dismissed-or-withdrawn counts, or ``None``.

    Denied is the floor times the set (the floor is exactly that share); the
    grant-family count is :func:`granted_in_set`'s, so ``None`` wherever that
    is unrecoverable. The one source for the PR body's floor line and the
    weekly digest's, so the two cannot state the draw differently.
    """
    granted = granted_in_set(report)
    if granted is None or not report.events_scored:
        return None
    denied = round(report.always_denied_accuracy * report.events_scored)
    return OutcomeMix(denied=denied, granted=granted, other=report.events_scored - denied - granted)


def _whole_set_arms(report: CertBacktest) -> dict[str, CertBacktestArm]:
    """Per-arm counts from an entry that scored the whole set, or ``{}``.

    An arm's denied and granted counts are properties of the labels, so any
    entry scored over every petition carries the set's; a short entry carries
    only its own subset's. Empty on a report written before the split.
    """
    for entry in report.entries:
        if entry.arms and sum(a.events_scored for a in entry.arms) == report.events_scored:
            return {arm.arm: arm for arm in entry.arms}
    return {}


def _arm_order(keys: Sequence[str]) -> list[str]:
    """The known arms in reading order, then any unknown key: all are counted."""
    order = [arm for arm in CERT_BACKTEST_ARMS if arm in keys]
    return order + sorted(key for key in keys if key not in CERT_BACKTEST_ARMS)


def arm_mix_text(report: CertBacktest) -> str:
    """The provisioning mix with each arm's outcomes, or ``""`` with no mix.

    Each arm's denials come from ``provisioning_denied``; its grant-family and
    dismissed/withdrawn counts from a whole-set entry's ``arms`` where the
    report carries them. On an older report only the denials are known, and
    the text says the rest is unrecorded rather than leaving a reader to infer
    ``n - denied`` granted. Shared by the PR body and the weekly digest.
    """
    mix = report.provisioning
    if not mix:
        return ""
    arms = _whole_set_arms(report)
    parts = []
    for key in _arm_order(list(mix)):
        arm = arms.get(key)
        if arm is not None:
            other = arm.events_scored - arm.denied - arm.granted
            parts.append(
                f"{key} {arm.events_scored} ({arm.denied} denied · {arm.granted} granted · "
                f"{other} dismissed/withdrawn)"
            )
        elif key in report.provisioning_denied:
            parts.append(f"{key} {mix[key]} ({report.provisioning_denied[key]} denied)")
        else:
            parts.append(f"{key} {mix[key]}")
    text = "; ".join(parts)
    if not arms:
        text += " — the per-arm grant/dismissal split is not recorded in this report"
    return text


def arm_score_text(arm: CertBacktestArm) -> str:
    """One entry's score on one arm: correct over n, and its lift in petitions.

    The lift is ``correct - denied`` — what the entry got right beyond what
    always-deny gets right on that arm — so the arms' lifts add up to the
    entry's pooled lift in petitions.
    """
    return f"{arm.correct}/{arm.events_scored} ({arm.correct - arm.denied:+d})"


def _lift_text(entry: CertBacktestEntry) -> str:
    """A lift in percentage points, and in petitions when the entry's n is small."""
    n = entry.events_scored
    pp = f"{entry.lift_over_always_denied * 100:+.1f} pp"
    if n >= SMALL_N:
        return pp
    petitions = round(entry.lift_over_always_denied * n)
    noun = "petition" if abs(petitions) == 1 else "petitions"
    return f"{pp} ({petitions:+d} {noun} of {n})"


def _backtest_losses_line(report: CertBacktest) -> str:
    """The PR body's per-cell loss line, empty where nothing was lost.

    A lost cell leaves its predictor scored over fewer petitions than the set,
    which is invisible in a top line and decisive for reading one — so the
    review PR says it outright rather than leaving it
    to whoever opens the report's `provenance` block. Grouped by predictor,
    because "which predictor is short, and by how much" is the question the
    line exists to answer.
    """
    losses = report.provenance.lost_cells if report.provenance is not None else []
    if not losses:
        return ""
    by_predictor: dict[str, list[str]] = {}
    for loss in losses:
        by_predictor.setdefault(loss.predictor_id, []).append(f"{loss.case_id} ({loss.reason})")
    named = "; ".join(
        f"`{predictor}` — {', '.join(cells)}" for predictor, cells in sorted(by_predictor.items())
    )
    return (
        f"- **{len(losses)} cell(s) lost** (no score — unreadable, failed, or "
        f"not attempted after a spent quota): {named}. "
        "A predictor short some of its cells is scored over the petitions that "
        "came back, so its `events_scored` is below the set and its lift is "
        "floored over that subset — not the same measurement as a full entry, "
        "and never the headline above. One short every cell has no entry at all "
        "and is in `provenance.dropped_predictors`.\n"
    )


def _is_candidate(disclosure: CertBacktestDisclosure) -> bool:
    return any(f.outcome_exposure_candidate for f in disclosure.flags)


def _headline_disclosures(report: CertBacktest, predictor_id: str, *, named: bool = False) -> str:
    """The headline entry's own candidate and unreadable-note counts, or ``""``.

    On the headline itself, not only in the line below it: a caveat one line
    away does not travel when the headline is quoted — and with its direction,
    since that is what makes it actionable. ``named`` says whose cells they
    are, for a headline that names several tied entries.
    """
    if report.provenance is None:
        return ""
    own = [d for d in report.provenance.disclosures if d.predictor_id == predictor_id and d.scored]
    candidates = sum(1 for d in own if _is_candidate(d))
    unreadable = sum(1 for d in own if d.unreadable)
    if not candidates and not unreadable:
        return ""
    counts = []
    if candidates:
        counts.append(f"{candidates} raised a possible outcome-exposure note")
    if unreadable:
        counts.append(f"{unreadable} left an unreadable one")
    whose = f"`{predictor_id}`'s" if named else "its"
    return (
        f" — **of {whose} scored cells, {' and '.join(counts)}**, still counted in this "
        "figure, which a real exposure can only bias upward (see the disclosures below)"
    )


def _backtest_disclosures_line(report: CertBacktest) -> str:
    """The PR body's line naming the cells whose notes may disclose their outcome.

    Names each exposure-candidate cell — predictor, petition, the note's
    category — and each unreadable ``flags.json``, since an unread note may
    have been one. A **lost** cell's candidate is named too, in its own clause:
    it is in no figure, but every predictor on that petition read the same
    provisioned inputs, so a leak through them reaches the scored cells beside
    it. Never a message: the report does not carry them (they are outcome text
    keyed by case id, and ``metrics/`` sits beside later replay cells), so the
    line points at the run log, where each note was printed as it was read.
    Empty where no cell raised either.
    """
    if report.provenance is None:
        return ""
    disclosures = report.provenance.disclosures
    scored = [d for d in disclosures if d.scored and _is_candidate(d)]
    lost = [d for d in disclosures if not d.scored and _is_candidate(d)]
    unreadable = [d for d in disclosures if d.unreadable]
    if not scored and not lost and not unreadable:
        return ""

    def named(cells: list[CertBacktestDisclosure]) -> str:
        return "; ".join(
            f"`{d.predictor_id}` — {d.case_id} ("
            + ", ".join(sorted({str(f.category) for f in d.flags if f.outcome_exposure_candidate}))
            + ")"
            for d in cells
        )

    clauses = []
    if scored:
        clauses.append(
            f"{len(scored)} scored cell(s) raised a note a text rule reads as a possible "
            f"outcome exposure: {named(scored)}"
        )
    if lost:
        clauses.append(
            f"{len(lost)} lost cell(s) did too — in no figure, but read them for a leak "
            f"through the petition's shared inputs: {named(lost)}"
        )
    if unreadable:
        cells = ", ".join(
            f"`{d.predictor_id}` — {d.case_id}{'' if d.scored else ' (lost)'}" for d in unreadable
        )
        clauses.append(f"{len(unreadable)} cell(s) left an unreadable `flags.json`: {cells}")
    return (
        f"- **Cell disclosures**: {'; and '.join(clauses)}. Read each note in this run's "
        "log (`flag from <predictor> on <case>`, or `unreadable flags.json from …`) before "
        "reading the board: nothing is excluded — the back-test runs no evaluator — so a "
        "real exposure is still in its predictor's figures, which it can only bias upward. "
        "The rule both over-calls and misses, so an unmarked note is not a cleared one.\n"
    )


def _arm_carrier(entry: CertBacktestEntry) -> str | None:
    """The one arm a positive lift sits on, as a clause, or ``None``.

    Where exactly one arm's lift in petitions is positive and covers the whole
    pooled lift, the lift is that arm's — at the registered draw usually one
    petition — and the headline says so in place, since a caveat in the table
    below does not travel when the headline is quoted.
    """
    lifts = [(arm, arm.correct - arm.denied) for arm in entry.arms]
    pooled = sum(lift for _, lift in lifts)
    positive = [(arm, lift) for arm, lift in lifts if lift > 0]
    if pooled <= 0 or len(positive) != 1 or positive[0][1] < pooled:
        return None
    arm = positive[0][0]
    noun = "petition" if arm.events_scored == 1 else "petitions"
    return f"all of it on the {arm.arm} arm ({arm.events_scored} {noun})"


def _top_line(report: CertBacktest, full: list[CertBacktestEntry]) -> str:
    """The headline over the whole-set entries: the top one, or the tie at the top.

    ``full`` is in board order, and the board ranks whole-set entries by lift
    first, so ``full[0]`` holds the highest correct count. Whole-set entries
    share one floor, so their lifts order exactly as their correct counts do,
    and a tie on the count is a tie on lift. The board breaks it by Brier,
    which is a total order and nothing more: at the registered draw a Brier gap
    between tied entries rests on the one or two granted outcomes the draw
    holds, so naming the Brier winner the "top predictor" reads a tie-break as
    a finding. A tie is stated as one, every tied entry named; a lead below
    :data:`SMALL_N` petitions is stated as its margin in petitions, an
    ordering rather than a measurement.
    """
    n = report.events_scored
    best = full[0]
    correct = round(best.accuracy * n)
    tied = [e for e in full if round(e.accuracy * n) == correct]
    carriers = {_arm_carrier(e) for e in tied}
    carrier = next(iter(carriers)) if len(carriers) == 1 else None
    where = f" — {'for each, ' if len(tied) > 1 else ''}{carrier}" if carrier else ""
    if len(tied) == 1:
        runner_up = next((e for e in full[1:]), None)
        lead = ""
        if runner_up is not None and n < SMALL_N:
            margin = correct - round(runner_up.accuracy * n)
            noun = "petition" if margin == 1 else "petitions"
            lead = (
                f"; leads the next whole-set entry by {margin} {noun}, an ordering at "
                "this n rather than a measurement"
            )
        return (
            f"top predictor `{best.predictor_id}`: lift **{_lift_text(best)}** over "
            f"always-deny{where} (accuracy {correct}/{n}, Brier "
            f"{best.mean_brier_score:.3f}{lead})" + _headline_disclosures(report, best.predictor_id)
        )
    names = ", ".join(f"`{e.predictor_id}`" for e in tied)
    briers = " · ".join(f"{e.mean_brier_score:.3f}" for e in tied)
    caveats = "".join(_headline_disclosures(report, e.predictor_id, named=True) for e in tied)
    return (
        f"**{len(tied)} predictors tie at the top** — {names} — each {correct}/{n} "
        f"correct, lift **{_lift_text(best)}** over always-deny{where}. The board "
        f"orders them by Brier ({briers}), a tie-break rather than a ranking"
        + (" at this n" if n < SMALL_N else "")
        + caveats
    )


def _backtest_arms_lines(report: CertBacktest) -> str:
    """The floor's per-arm outcome mix and each entry's score per arm.

    The arms are three information sets whose membership correlates with the
    outcome in either direction, so a pooled lift can be carried by one arm —
    at the registered draw, by one petition. The table puts each entry's
    correct count beside the arm's own floor, its lift in petitions alongside.
    """
    mix = arm_mix_text(report)
    if not mix:
        return ""
    lines = f"- by arm: {mix}\n"
    scored = [e for e in report.entries if e.arms]
    if not scored:
        return lines + (
            "- per-arm scores: not recorded in this report, so whether one arm carries "
            "a lift cannot be read off it\n"
        )
    keys = _arm_order(sorted({a.arm for e in scored for a in e.arms}))
    header = " | ".join(keys)
    rows = []
    for entry in scored:
        by_arm = {a.arm: a for a in entry.arms}
        cells = " | ".join(arm_score_text(by_arm[key]) if key in by_arm else "—" for key in keys)
        rows.append(f"  | `{entry.predictor_id}` | {cells} |")
    return (
        lines + "- per-arm scores — correct/n on the arm, and in brackets the lift in "
        "petitions over that arm's always-deny (an arm of a few petitions is a count, "
        "not a rate; the arms' brackets sum to the pooled lift):\n\n"
        f"  | predictor | {header} |\n"
        f"  |---|{'---|' * len(keys)}\n" + "\n".join(rows) + "\n\n"
    )


def render_backtest_pr(
    metrics_root: Path, run_id: str, *, limit: int, engine: str
) -> MetricsRefreshPr | None:
    """Render the review PR for a cert back-test run a maintainer released.

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
    granted = granted_in_set(report)
    # The headline names a predictor scored over the **whole set**, or it names
    # none. An entry short some cells is floored over its own subset, and lift
    # is a per-petition mean, so dropping a petition the predictor got wrong
    # both rescales and shifts its lift — at a ten-petition draw, far enough to
    # outrank every honest full-set entry. Such an entry belongs on the board
    # and in the losses line, never on the top line.
    full = sorted(
        (e for e in report.entries if e.events_scored == report.events_scored),
        key=lambda e: e.rank,
    )
    if not report.entries:
        headline = "no predictors scored (empty set)"
    elif granted == 0:
        headline = (
            "no granted-side outcome in this set — every predictor is scored against a "
            "draw with nothing to discriminate, so the lift ordering is not a measurement"
        )
    elif not full:
        headline = (
            "no predictor scored the whole set — every entry is short some cells (see "
            "the losses below), so there is no lift here measured over the set and the "
            "ordering is not a measurement"
        )
    else:
        headline = _top_line(report, full)
    title = f"metrics: cert back-test over {report.events_scored} petition(s)"
    mix = outcome_mix(report)
    granted_line = (
        f" ({mix.text()} of {report.events_scored})"
        if mix is not None
        else " (granted-side count unavailable — no calibration view)"
    )
    body = (
        f"Cert back-test (run `{run_id}`): the enabled predictors replayed over "
        f"{report.events_scored} decided modern discretionary-cert petition(s) "
        f"with outcomes hidden (`--limit {limit} --engine {engine}`; the report's "
        "`provenance` block carries the rest of the dispatch — the scope, and "
        "how the set was drawn (`provenance.draw`) — which is what "
        "the population actually was), scored against the realized "
        "grant/deny. Retrospective by construction — iteration signal, never "
        "claimable performance.\n\n"
        f"- {headline}\n"
        f"- always-deny floor: **{report.always_denied_accuracy:.0%}** over this set"
        f"{granted_line}\n"
        f"{_backtest_arms_lines(report)}"
        f"- predictors on the board: {report.predictors_evaluated}\n"
        f"{_backtest_losses_line(report)}"
        f"{_backtest_disclosures_line(report)}\n"
        "Review and merge — this PR is intentionally **not** auto-merged; a "
        "later run force-pushes this same branch and the PR updates in place.\n"
    )
    return MetricsRefreshPr(
        branch=BACKTEST_BRANCH,
        title=title,
        commit_message=title,
        body=body,
    )
