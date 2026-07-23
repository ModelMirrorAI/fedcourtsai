"""Path-jail guardrail and per-run PR aggregation for the matrix stages.

The predict/evaluate stages fan out one matrix cell per
predictor/evaluator x case x event and used to open one PR per cell — dozens a
day, each merged by hand. They now aggregate: every cell uploads its ``data/``
output as a build artifact, and a single ``collect`` job unions them into **one
PR per run** that auto-merges once the required checks are green.

Because that PR merges without a human, two controls keep it honest, and both
live here as small pure functions the CLI wraps so the YAML only runs git/gh:

- The **path jail** (:func:`assert_within_jail`): an auto-merged data PR may only
  *add* files under ``data/``. Anything else — a touched workflow, a modified or
  deleted artifact, a write into another run's directory — is rejected. It runs
  producer-side in the ``collect`` job (before the commit) and again as a required
  status check on the PR, so the guarantee holds independently of the workflow
  that produced the branch.
- The **collect plan** (:func:`collect_plan`): partitions a run's cells into the
  ready set (one auto-merging PR) and the partial set (a failed or invalid
  agent's output, opened as a single *draft* PR a maintainer finishes — a draft
  never auto-merges), and builds the branch, commit message, PR title, and body.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import Literal

from .finalize import FinalizeRole
from .schemas import AgentFlags, CellFailure, FlagSeverity

DATA_JAIL = "data/"

# A cleanup-sweep PR may only delete files under a case event's predictions subtree:
# data/cases/<court>/<docket>/events/<event>/predictions/<...>. The trailing slash
# means the event.yaml / outcome.json one level up never match.
_PREDICTIONS_JAIL = re.compile(r"^data/cases/[^/]+/[^/]+/events/[^/]+/predictions/")

# The judgment noun each role's aggregated PR is about, for human-facing text.
_JUDGMENT_NOUN = {FinalizeRole.predict: "prediction", FinalizeRole.evaluate: "evaluation"}

_PARTIAL_WARNING = (
    "⚠️ These cells did not finish cleanly (a turn/time limit, or output that "
    "failed schema validation). This is a **draft** — it never auto-merges; a "
    "maintainer reviews and completes it."
)


class PathJailError(Exception):
    """A data-production PR changed a path outside the append-only ``data/`` jail."""


@dataclass(frozen=True)
class PathChange:
    """One entry from ``git diff --name-status``: the status letter and the path."""

    status: str
    path: str


def _within_data(path: str) -> bool:
    return path == "data" or path.startswith(DATA_JAIL)


def parse_name_status(text: str) -> list[PathChange]:
    """Parse ``git diff --name-status`` output into :class:`PathChange` entries.

    Each line is a status letter then tab-separated path(s); a rename or copy
    carries both the old and new path, so we key on the *new* (last) path and
    take the leading status letter (``R100`` -> ``R``). Blank lines are ignored.
    """
    changes: list[PathChange] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        fields = line.split("\t")
        changes.append(PathChange(status=fields[0][:1], path=fields[-1]))
    return changes


def assert_within_jail(changes: Iterable[PathChange], *, run_id: str | None = None) -> None:
    """Raise :class:`PathJailError` unless every change is an *addition* under ``data/``.

    Auto-merged predict/evaluate PRs are append-only by construction:
    each writes a fresh ``<...>/<run_id>/`` directory and never touches code,
    workflows, config, or an existing artifact. This enforces exactly that — any
    path outside ``data/``, and any status other than add (modify, delete,
    rename, copy, type-change), is a violation. When ``run_id`` is given, every
    path must also contain that run id, so the change set can only add the current
    run's files.
    """
    violations: list[str] = []
    for change in changes:
        if not _within_data(change.path):
            violations.append(f"{change.path!r} is outside the data/ jail")
        elif change.status != "A":
            violations.append(
                f"{change.path!r} has status {change.status!r}; data PRs only add files"
            )
        elif run_id is not None and f"/{run_id}/" not in f"/{change.path}":
            violations.append(f"{change.path!r} is not under run id {run_id!r}")
    if violations:
        raise PathJailError("path jail rejected the change set:\n- " + "\n- ".join(violations))


def assert_cleanup_within_jail(changes: Iterable[PathChange]) -> None:
    """Raise :class:`PathJailError` unless every change *deletes* a prediction file.

    The cleanup sweep is the mirror of the append-only writers: it only ever
    removes already-merged predictions for out-of-scope cases, never adds or edits.
    So every change must be a delete (status ``D``) of a file under a
    ``data/cases/<court>/<docket>/events/<event>/predictions/`` subtree — anything
    else (a non-delete status, a path outside that subtree, an ``event.yaml`` /
    ``outcome.json`` one level up, code, a workflow) is a violation. CI enforces this
    on the cleanup PR, so a sweep cannot reach ``main`` having touched anything but
    out-of-scope prediction artifacts.
    """
    violations: list[str] = []
    for change in changes:
        if change.status != "D":
            violations.append(
                f"{change.path!r} has status {change.status!r}; cleanup PRs only delete files"
            )
        elif not _PREDICTIONS_JAIL.match(change.path):
            violations.append(
                f"{change.path!r} is not under a data/cases/**/events/*/predictions/ subtree"
            )
    if violations:
        raise PathJailError("cleanup jail rejected the change set:\n- " + "\n- ".join(violations))


@dataclass(frozen=True)
class CellStatus:
    """One matrix cell's outcome, read from the status JSON it uploaded.

    ``artifact_dir`` is the cell's directory under the collect job's download root
    (the parent of its ``status.json``); the workflow copies that subtree's
    ``data/`` into the PR it belongs to.
    """

    court: str
    docket: int
    event_id: str
    actor: str
    run_id: str
    produced: bool
    validated: bool
    agent_ok: bool
    artifact_dir: str

    @property
    def ready(self) -> bool:
        """A cell is ready only if its agent finished, wrote output, and it validated."""
        return self.produced and self.validated and self.agent_ok

    @property
    def _reason(self) -> str:
        if not self.produced:
            return "no output"
        if not self.agent_ok:
            return "agent stopped early"
        if not self.validated:
            return "failed validation"
        return "ready"

    @classmethod
    def from_dict(cls, data: dict[str, object], *, artifact_dir: str) -> CellStatus:
        return cls(
            court=str(data["court"]),
            docket=int(str(data["docket"])),
            event_id=str(data["event_id"]),
            actor=str(data["actor"]),
            run_id=str(data["run_id"]),
            produced=bool(data["produced"]),
            validated=bool(data["validated"]),
            agent_ok=bool(data["agent_ok"]),
            artifact_dir=artifact_dir,
        )


@dataclass(frozen=True)
class ExpectedCell:
    """One cell the plan queued — the identity a ``status.json`` must match.

    Read from the plan job's matrix, which is the only record of what a run was
    *supposed* to produce. The cell census cannot supply it: a cell that never
    uploaded leaves no ``status.json``, so without the matrix it is
    indistinguishable from a cell that was never queued.
    """

    actor: str
    court: str
    docket: int
    event_id: str

    @classmethod
    def from_matrix_entry(cls, entry: dict[str, object]) -> ExpectedCell:
        """Parse one ``include[]`` entry from ``predict-matrix`` / ``evaluate-matrix``."""
        actor = entry.get("predictor_id") or entry.get("evaluator_id")
        if actor is None:
            raise ValueError("matrix entry has neither predictor_id nor evaluator_id")
        return cls(
            actor=str(actor),
            court=str(entry["court"]),
            docket=int(str(entry["docket"])),
            event_id=str(entry["event_id"]),
        )


def cell_artifact_name(role: FinalizeRole, cell: ExpectedCell) -> str:
    """The artifact name a cell uploads, rebuilt from its identity.

    Mirrors the ``name:`` expression on the cell workflows' upload step. That
    coupling is unavoidable — the upload name is a workflow expression and cannot
    call this — so it is asserted by a workflow test rather than left to drift.
    Used to tell a cell whose artifact *failed to transfer* (recoverable: re-run
    collect) from one that *never uploaded at all* (the cell died; needs a
    re-queue), since both are absent from the census.
    """
    return f"{role.value}-{cell.actor}-{cell.court}-{cell.docket}-{cell.event_id}"


@dataclass(frozen=True)
class PrPlan:
    """One PR the collect job should open: ready or partial."""

    branch: str
    commit_message: str
    title: str
    body: str
    draft: bool
    artifact_dirs: tuple[str, ...]


@dataclass(frozen=True)
class CollectPlan:
    """The aggregate decision for a run.

    ``ready`` is the one auto-merging PR (None if no cell finished cleanly);
    ``partial`` is the one draft PR carrying *salvageable* output a maintainer
    finishes (None if there is nothing to salvage); ``skipped`` are the cells that
    produced no output at all — nothing to commit, only worth a warning so the run
    never silently drops a cell. ``flags_markdown`` is the run's rolled-up agent
    flags (empty when none); it is also appended to whichever PR body the run
    opens, so the workflow can surface it in the Actions summary even when no PR is.
    ``feedback_comment`` wraps that same roll-up for the long-lived agent-feedback
    tracking issue (empty when no flags), so a note reaches a durable, centralized
    home even when a fully-failed run opens no PR.

    ``stalled`` is the infrastructure-failure signal: no cell produced output
    **and** no agent finished cleanly — the cells died before (or while) their
    agents ran, as opposed to agents that ran and legitimately produced nothing.
    The collect job posts the
    stall comment on the trigger issue only when this is true, so a genuine
    "nothing to do" run stays quiet.

    ``dead_actors`` are the engines that produced 0 of their cells this run — a
    whole engine absent from the tournament (e.g. quota exhaustion), as opposed
    to the per-cell ``skipped`` gaps. Because the live queue is
    transition-driven (it never re-queues a gap), a fully-absent engine would
    otherwise let the ready PR close the trigger issue with a third of the board
    silently missing; ``collect_plan`` therefore withholds the close and names
    the gap, keeping the issue open for a backfill.

    ``noun`` is the role's judgment word ("prediction" / "evaluation"). It rides
    on the plan so the collect action can render its per-cell warnings from the
    same mapping that names the PR title and commit message, rather than
    re-deriving the role's vocabulary in shell and letting the two drift.

    ``salvage`` are the cells that wrote output but stopped early or failed
    validation — the ones the draft PR carries. It rides on the plan (rather than
    living only inside ``partial``'s opaque ``artifact_dirs``) so that
    :func:`cell_failures` can name them: a salvage cell ran and produced no
    *usable* artifact, so it is a per-cell failure that counts toward the attempt
    cap alongside ``skipped`` and ``uncovered_cells``.
    """

    ready: PrPlan | None
    partial: PrPlan | None
    skipped: tuple[CellStatus, ...] = ()
    flags_markdown: str = ""
    feedback_comment: str = ""
    stalled: bool = False
    dead_actors: tuple[str, ...] = ()
    noun: str = ""
    missing_artifacts: tuple[str, ...] = ()
    uncovered_cells: tuple[ExpectedCell, ...] = ()
    salvage: tuple[CellStatus, ...] = ()


def _table(cells: Sequence[CellStatus], *, with_reason: bool) -> str:
    header = "| predictor | case | event |" + (" reason |" if with_reason else "")
    rule = "|---|---|---|" + ("---|" if with_reason else "")
    rows = []
    for c in cells:
        row = f"| `{c.actor}` | `{c.court}/{c.docket}` | `{c.event_id}` |"
        if with_reason:
            row += f" {c._reason} |"
        rows.append(row)
    return "\n".join([header, rule, *rows])


# Loudest first, so the roll-up leads with anything that blocked a cell.
_SEVERITY_RANK = {FlagSeverity.blocker: 0, FlagSeverity.warning: 1, FlagSeverity.info: 2}
# info carries no icon (its glyph is visually ambiguous and adds nothing).
_SEVERITY_ICON = {FlagSeverity.blocker: "🛑", FlagSeverity.warning: "⚠️"}


def _md_cell(value: object) -> str:
    """Render one markdown table cell from agent-authored text, kept on one line.

    Flag messages are agent output, so collapse newlines and escape the pipe that
    would otherwise break the table; the schema already caps the length.
    """
    return " ".join(str(value).split()).replace("|", "\\|") or "—"


# The columns a maintainer triages flags on, shared by every flag table.
FLAGS_TABLE_HEADER = (
    "| severity | category | actor | case | event | note |\n|---|---|---|---|---|---|"
)


def flags_table(flag_sets: Sequence[AgentFlags]) -> str:
    """Render flag sets as one severity-sorted markdown table, or ``""`` if none.

    The shared table body behind both the per-run roll-up (:func:`render_flags`) and
    the run-ops dashboard's open-flags section: one row per flag, loudest severity
    first, carrying the columns a maintainer triages on (severity, category, actor,
    case, event, note). Flag messages are agent-authored, so each cell is collapsed
    to one line and pipe-escaped. Returns ``""`` when no set raised a flag.
    """
    rows: list[tuple[int, str, str, str]] = []
    for fs in flag_sets:
        for flag in fs.flags:
            severity = FlagSeverity(flag.severity)
            event = flag.event_id or ""
            rows.append(
                (
                    _SEVERITY_RANK.get(severity, 99),
                    fs.actor_id,
                    event,
                    f"| {_SEVERITY_ICON.get(severity, '')} {severity.value} "
                    f"| {_md_cell(flag.category)} | `{_md_cell(fs.actor_id)}` "
                    f"| `{_md_cell(fs.case_id)}` | {f'`{_md_cell(event)}`' if event else '—'} "
                    f"| {_md_cell(flag.message)} |",
                )
            )
    if not rows:
        return ""
    body = "\n".join(row[3] for row in sorted(rows, key=lambda r: r[:3]))
    return f"{FLAGS_TABLE_HEADER}\n{body}"


def render_flags(flag_sets: Sequence[AgentFlags]) -> str:
    """Roll a run's per-cell ``flags.json`` into one markdown section, or ``""``.

    One row per flag, loudest severity first, so a maintainer reading the run PR (or
    the Actions summary) sees every agent-surfaced note — a data-quality problem, a
    scope question, the reason a cell was blocked — in one place rather than buried
    across the run's ``reasoning.md`` files. Returns the empty string when no cell
    raised a flag, so the caller can omit the section entirely.
    """
    table = flags_table(flag_sets)
    if not table:
        return ""
    count = sum(len(fs.flags) for fs in flag_sets)
    return (
        f"## 🚩 Agent flags ({count})\n\n"
        "Structured notes the agents surfaced this run, for triage.\n\n" + table
    )


def feedback_marker(role: FinalizeRole, run_id: str) -> str:
    """The hidden HTML marker that keys one run's note on the agent-feedback issue.

    Embedded as the first line of :func:`render_feedback_comment`'s output so the
    collect job can grep an existing comment for it and post each run's roll-up
    exactly once to the single long-lived issue — even if the job re-runs.
    """
    return f"<!-- agent-feedback-run: {role.value}/{run_id} -->"


def render_feedback_comment(role: FinalizeRole, run_id: str, flags_markdown: str) -> str:
    """Wrap a run's flag roll-up as a comment for the latched agent-feedback issue.

    Returns ``""`` when the run raised no flags (``flags_markdown`` empty) so the
    caller posts nothing. Otherwise leads with a per-run :func:`feedback_marker`
    (for one-time posting) and a header naming the stage and run, then the roll-up —
    so the single long-lived issue accrues one comment per flagged run, a durable
    home that survives even a fully-failed run that opens no PR.
    """
    if not flags_markdown:
        return ""
    return f"{feedback_marker(role, run_id)}\n### {role.value} · run `{run_id}`\n\n{flags_markdown}"


def render_stall_comment(role: FinalizeRole, run_url: str) -> str:
    """The trigger-issue comment for a run that produced **no** output at all.

    A wholesale failure — every cell dying before its agent ran, or every cell
    finishing without an artifact — opens no PR, so the trigger issue would
    otherwise sit silently orphaned open, invisible unless someone reads the
    Actions history. This comment makes the stall loud on the issue itself and
    says how to retry. Posted with the ambient ``GITHUB_TOKEN`` (a
    non-triggering write) by the collect job's stall step.
    """
    return (
        f"⚠️ The {role.value} run for this issue **produced no output** — no cell "
        f"delivered an artifact, so nothing was committed and no PR opened. This "
        f"usually means the cells failed before their agents ran (job-setup or "
        f"infrastructure errors) rather than the agents declining the work.\n\n"
        f"Run log: {run_url}\n\n"
        f"The issue stays open. To retry once the cause is fixed, remove and "
        f"re-apply the `run:{role.value}` label — the plan re-checks scope, and an "
        f"empty matrix closes this issue with a note."
    )


def collect_plan(
    role: FinalizeRole,
    *,
    run_id: str,
    cells: Sequence[CellStatus],
    issue: int | None = None,
    flags: Sequence[AgentFlags] = (),
    missing_artifacts: Sequence[str] = (),
    expected: Sequence[ExpectedCell] = (),
) -> CollectPlan:
    """Partition a run's cells into one ready PR, one draft PR, and the skipped.

    A cell is **ready** (agent finished, wrote output, it validated) → the one
    auto-merging PR; **salvageable** (it wrote output but stopped early or failed
    validation) → the one *draft* PR a maintainer completes (a draft never
    auto-merges, preserving the per-cell graceful degradation the old
    one-PR-per-cell flow had); or **skipped** (it produced nothing) → nothing to
    commit, returned only so the workflow can warn. A run with no ready cells
    opens no ready PR; with nothing to salvage, no draft.

    ``issue`` is the triggering issue, which the ready PR closes on merge — but
    only when nothing is left to salvage, **no whole engine is absent** (a
    fully-missing engine at 0/N, see ``dead_actors``), **no cell's artifact was
    lost in transfer** (``missing_artifacts``), and **no queued cell went missing
    entirely** (``expected``), so a run with a pending draft or any uncovered gap
    keeps its trigger issue open for the follow-up.

    ``missing_artifacts`` names the cells whose artifacts the collect job could
    not download. They are invisible to the cell census — a lost artifact leaves
    no ``status.json``, so it appears in neither ``skipped`` nor ``dead_actors``
    unless it happens to take out an engine entirely. Without naming them here,
    a partial transfer failure would auto-merge a PR presenting itself as the
    whole run while quietly omitting cells, with the only trace a log line that
    expires. They are recoverable (re-run the collect job while the artifacts
    live), which is why this withholds the close rather than failing the run.

    ``expected`` is the cell set the plan job queued, from its matrix. A cell
    absent from the census *and* from ``missing_artifacts`` never uploaded at
    all — its job died before it could report — and is returned as
    ``uncovered_cells``. The distinction from a lost artifact is the remedy, and
    it is worth the extra field: a lost artifact is recovered by re-running
    collect while the artifact lives, whereas an uncovered cell produced nothing
    to recover and needs a re-queue. Sending an operator down the wrong one
    means either waiting out a rerun that cannot help, or paying for the cell
    twice. Empty ``expected`` disables the census entirely.

    ``flags`` is the run's per-cell :class:`~fedcourtsai.schemas.AgentFlags`. Their
    roll-up is appended to whichever PR body opens (the ready PR, else the draft)
    and returned as ``flags_markdown`` so the workflow can also surface it in the
    Actions summary, and as ``feedback_comment`` for the long-lived agent-feedback
    tracking issue — a durable, centralized home for an agent's note that survives
    the trigger issue's closure and even a fully-failed run that opens no PR.
    """
    if role not in _JUDGMENT_NOUN:
        raise ValueError(f"collect_plan supports predict/evaluate, not {role.value}")
    noun = _JUDGMENT_NOUN[role]
    lost = tuple(sorted(missing_artifacts))
    # A queued cell that is in neither the census nor the transfer-loss list
    # never uploaded at all — its job died before (or during) the upload. That
    # is a different remedy from a lost artifact: re-running collect cannot
    # recover it, only a re-queue can, so the two are counted separately.
    observed = {(c.actor, c.court, c.docket, c.event_id) for c in cells}
    lost_names = set(lost)
    uncovered = tuple(
        sorted(
            {
                cell
                for cell in expected
                if (cell.actor, cell.court, cell.docket, cell.event_id) not in observed
                and cell_artifact_name(role, cell) not in lost_names
            },
            key=lambda c: (c.actor, c.court, c.docket, c.event_id),
        )
    )
    ready = [c for c in cells if c.ready]
    salvage = [c for c in cells if c.produced and not c.ready]
    skipped = tuple(c for c in cells if not c.produced)

    # An actor that produced 0 of its cells is a whole engine missing from the
    # run — and unlike a partial failure it leaves no salvage draft to hold the
    # issue open. The live queue is transition-driven, so the gap never
    # re-queues; without withholding the close here the ready PR (the surviving
    # engines) would shut the trigger issue with that engine silently absent.
    # Keys on `produced` (not `agent_ok`): an engine that ran cleanly but
    # declined every cell is the same missing seat as a quota failure — the
    # tournament expects every seat to produce, so both keep the issue open.
    produced_actors = {c.actor for c in cells if c.produced}
    dead_actors = tuple(sorted({c.actor for c in cells} - produced_actors))

    ready_plan: PrPlan | None = None
    if ready:
        notes = []
        if salvage:
            notes.append(f"{len(salvage)} cell(s) need review; see the companion draft PR.")
        if dead_actors:
            engines = ", ".join(f"`{a}`" for a in dead_actors)
            notes.append(
                f"⚠️ No output at all from {engines} this run — a full engine is "
                f"missing and the live queue will not re-queue it, so this issue "
                f"stays open for a backfill (the per-case predictors filter)."
            )
        if uncovered:
            rows = "\n".join(
                f"- `{c.actor}` on `{c.court}/{c.docket}` `{c.event_id}`" for c in uncovered
            )
            notes.append(
                f"⚠️ {len(uncovered)} queued cell(s) uploaded nothing at all — no "
                f"artifact and no status, so the cell died before it could report. "
                f"Re-running `collect` will not recover these; they need a re-queue. "
                f"This issue stays open.\n{rows}"
            )
        if lost:
            names = "\n".join(f"- `{n}`" for n in lost)
            notes.append(
                f"⚠️ {len(lost)} cell artifact(s) did not transfer, so their output "
                f"is **not** in this PR even though the cells may have succeeded. "
                f"This issue stays open; re-run the `collect` job to recover them "
                f"(cell artifacts are retained 7 days).\n{names}"
            )
        note = ("\n\n" + "\n\n".join(notes)) if notes else ""
        # Close the trigger issue from the ready PR, but not while a draft still
        # carries unfinished work, a whole engine is missing, or a cell's output
        # was lost in transfer — each is a gap the run does not actually cover.
        closes = (
            f"\n\nCloses #{issue}"
            if issue is not None and not salvage and not dead_actors and not lost and not uncovered
            else ""
        )
        ready_plan = PrPlan(
            branch=f"{role.value}/run-{run_id}",
            commit_message=f"{role.value}(run {run_id}): {len(ready)} {noun}(s)",
            title=f"{role.value}: {len(ready)} {noun}(s) (run {run_id})",
            body=(
                f"Automated {noun}s for run `{run_id}`."
                f"\n\n{_table(ready, with_reason=False)}{note}{closes}"
            ),
            draft=False,
            artifact_dirs=tuple(c.artifact_dir for c in ready),
        )

    partial_plan: PrPlan | None = None
    if salvage:
        partial_plan = PrPlan(
            branch=f"{role.value}/run-{run_id}-partial",
            commit_message=f"{role.value}(run {run_id}): {len(salvage)} partial {noun}(s)",
            title=f"{role.value}: {len(salvage)} partial {noun}(s) (run {run_id})",
            body=f"{_PARTIAL_WARNING}\n\n{_table(salvage, with_reason=True)}",
            draft=True,
            artifact_dirs=tuple(c.artifact_dir for c in salvage),
        )

    flags_md = render_flags(flags)
    ready_plan, partial_plan = _append_flags(ready_plan, partial_plan, flags_md)
    return CollectPlan(
        ready=ready_plan,
        partial=partial_plan,
        skipped=skipped,
        flags_markdown=flags_md,
        feedback_comment=render_feedback_comment(role, run_id, flags_md),
        stalled=bool(cells) and not any(c.produced or c.agent_ok for c in cells),
        dead_actors=dead_actors,
        noun=noun,
        missing_artifacts=lost,
        uncovered_cells=uncovered,
        salvage=tuple(salvage),
    )


def _append_flags(
    ready: PrPlan | None, partial: PrPlan | None, flags_md: str
) -> tuple[PrPlan | None, PrPlan | None]:
    """Append the flag roll-up to the run's primary PR body (ready, else draft).

    The flags belong to the run, not a single cell, so they ride the one PR a
    maintainer reviews — the auto-merging ready PR when there is one, otherwise the
    draft. With no PR at all the roll-up still travels as ``flags_markdown``.
    """
    if not flags_md:
        return ready, partial
    if ready is not None:
        return replace(ready, body=f"{ready.body}\n\n{flags_md}"), partial
    if partial is not None:
        return ready, replace(partial, body=f"{partial.body}\n\n{flags_md}")
    return ready, partial


def cell_failures(plan: CollectPlan, *, run_id: str, role: FinalizeRole) -> list[CellFailure]:
    """One durable failure fact per cell that ran and produced no usable artifact.

    The writer side of the per-cell attempt cap. ``collect`` is the only observer
    of a cell failure but is corpus-blind, so each fact is a git-ledger
    ``attempt.json`` the derivers later count
    (:func:`fedcourtsai.matrix.cell_failure_count`). The truly-failed cells are the
    union of three disjoint buckets — ``skipped``, ``salvage``, and
    ``uncovered_cells``:

    * ``skipped`` — ran and produced nothing (``no_output``).
    * ``salvage`` — produced output that failed validation or stopped early
      (``partial``).
    * ``uncovered_cells`` — queued but uploaded nothing at all; the job died before
      it could report (``died``).

    ``missing_artifacts`` is deliberately excluded: a lost artifact is
    re-collectable download loss (re-run ``collect``), not a cell failure, so it
    must not burn a cap attempt. ``dead_actors`` is not a separate bucket either —
    a dead engine's cells already surface in ``uncovered`` (or ``skipped``); its
    membership only *refines* the class, promoting the cell to ``quota``.

    ``error_class`` is coarse triage metadata only: every fact counts equally
    toward the cap. ``run_id`` is stamped on **all** facts from the collect job's
    known run id — an uncovered cell carries no run id in its identity, and using
    one uniform id keeps every fact's path run-scoped (so a rerun overwrites).
    """
    dead = set(plan.dead_actors)
    seam = role.value  # FinalizeRole values are exactly the CellFailure seam literals

    def _fact(
        actor: str,
        court: str,
        docket: int,
        event_id: str,
        bucket: Literal["no_output", "partial", "died"],
    ) -> CellFailure:
        # A dead-actor cell reads as `quota` (its whole engine produced nothing);
        # otherwise the coarse bucket the cell fell in.
        error_class: Literal["no_output", "partial", "died", "quota"] = (
            "quota" if actor in dead else bucket
        )
        return CellFailure(
            seam=seam,
            actor=actor,
            court=court,
            docket=docket,
            event_id=event_id,
            run_id=run_id,
            error_class=error_class,
        )

    facts = [_fact(c.actor, c.court, c.docket, c.event_id, "no_output") for c in plan.skipped]
    facts += [_fact(c.actor, c.court, c.docket, c.event_id, "partial") for c in plan.salvage]
    facts += [_fact(c.actor, c.court, c.docket, c.event_id, "died") for c in plan.uncovered_cells]
    return facts
