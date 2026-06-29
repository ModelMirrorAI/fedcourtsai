"""Path-jail guardrail and per-run PR aggregation for the matrix stages.

The predict/evaluate/reconcile stages fan out one matrix cell per
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

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

from .finalize import FinalizeRole
from .schemas import AgentFlags, FlagSeverity

DATA_JAIL = "data/"

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

    Auto-merged predict/evaluate/reconcile PRs are append-only by construction:
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
class ReconcileCellStatus:
    """One reconcile cell's outcome — a cell is one *case* settling >=0 events.

    Reconcile fans out per case (it must weigh a case's open events together), so a
    cell has no single event/actor: ``settled`` is the event ids whose
    ``outcome.json`` the agent recorded this run. ``produced`` is "settled
    anything".
    """

    court: str
    docket: int
    run_id: str
    settled: tuple[str, ...]
    validated: bool
    agent_ok: bool
    artifact_dir: str

    @property
    def produced(self) -> bool:
        return bool(self.settled)

    @property
    def ready(self) -> bool:
        return self.produced and self.validated and self.agent_ok

    @property
    def _reason(self) -> str:
        if not self.produced:
            return "nothing settled"
        if not self.agent_ok:
            return "agent stopped early"
        if not self.validated:
            return "failed validation"
        return "ready"

    @classmethod
    def from_dict(cls, data: dict[str, object], *, artifact_dir: str) -> ReconcileCellStatus:
        settled = data.get("settled", [])
        return cls(
            court=str(data["court"]),
            docket=int(str(data["docket"])),
            run_id=str(data["run_id"]),
            settled=tuple(str(e) for e in settled) if isinstance(settled, list) else (),
            validated=bool(data["validated"]),
            agent_ok=bool(data["agent_ok"]),
            artifact_dir=artifact_dir,
        )


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
    """

    ready: PrPlan | None
    partial: PrPlan | None
    skipped: tuple[CellStatus | ReconcileCellStatus, ...] = ()
    flags_markdown: str = ""


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


def collect_plan(
    role: FinalizeRole,
    *,
    run_id: str,
    cells: Sequence[CellStatus],
    issue: int | None = None,
    flags: Sequence[AgentFlags] = (),
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
    only when nothing is left to salvage, so a run with a pending draft keeps its
    trigger issue open until a maintainer finishes that draft.

    ``flags`` is the run's per-cell :class:`~fedcourtsai.schemas.AgentFlags`. Their
    roll-up is appended to whichever PR body opens (the ready PR, else the draft)
    and returned as ``flags_markdown`` so the workflow can also surface it in the
    Actions summary — a durable, discoverable home for an agent's note that
    survives the trigger issue's closure.
    """
    if role not in _JUDGMENT_NOUN:
        raise ValueError(f"collect_plan supports predict/evaluate, not {role.value}")
    noun = _JUDGMENT_NOUN[role]
    ready = [c for c in cells if c.ready]
    salvage = [c for c in cells if c.produced and not c.ready]
    skipped = tuple(c for c in cells if not c.produced)

    ready_plan: PrPlan | None = None
    if ready:
        note = (
            f"\n\n{len(salvage)} cell(s) need review; see the companion draft PR."
            if salvage
            else ""
        )
        # Close the trigger issue from the ready PR, but not while a draft still
        # carries unfinished work for the same run.
        closes = f"\n\nCloses #{issue}" if issue is not None and not salvage else ""
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
        ready=ready_plan, partial=partial_plan, skipped=skipped, flags_markdown=flags_md
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


def _reconcile_table(cells: Sequence[ReconcileCellStatus], *, with_reason: bool) -> str:
    header = "| case | settled events |" + (" reason |" if with_reason else "")
    rule = "|---|---|" + ("---|" if with_reason else "")
    rows = []
    for c in cells:
        events = ", ".join(f"`{e}`" for e in c.settled) or "—"
        row = f"| `{c.court}/{c.docket}` | {events} |"
        if with_reason:
            row += f" {c._reason} |"
        rows.append(row)
    return "\n".join([header, rule, *rows])


def reconcile_collect_plan(
    *,
    run_id: str,
    cells: Sequence[ReconcileCellStatus],
    issue: int | None = None,
) -> CollectPlan:
    """Partition a reconcile run's per-case cells into one ready PR + one draft PR.

    Same ready/salvage/skipped split as :func:`collect_plan`, but per case: a cell
    is **ready** when it settled >=1 event, validated, and the agent finished;
    **salvageable** when it settled output but stopped early or failed validation
    (→ draft); **skipped** when it settled nothing (→ warning only). The ready PR's
    title and commit subject start with ``reconcile:`` so the squash-merge to
    ``main`` fires run-reconcile's evaluate handoff, and it closes the trigger
    issue on merge unless a salvage draft remains.
    """
    ready = [c for c in cells if c.ready]
    salvage = [c for c in cells if c.produced and not c.ready]
    skipped = tuple(c for c in cells if not c.produced)

    ready_plan: PrPlan | None = None
    if ready:
        note = (
            f"\n\n{len(salvage)} case(s) need review; see the companion draft PR."
            if salvage
            else ""
        )
        closes = f"\n\nCloses #{issue}" if issue is not None and not salvage else ""
        ready_plan = PrPlan(
            branch=f"reconcile/run-{run_id}",
            commit_message=f"reconcile: {len(ready)} case(s) (run {run_id})",
            title=f"reconcile: {len(ready)} case(s) (run {run_id})",
            body=(
                f"Reconciled ground truth for run `{run_id}`."
                f"\n\n{_reconcile_table(ready, with_reason=False)}"
                "\n\nWhen this merges, `run-reconcile` opens a `run:evaluate` issue "
                "for the settled events."
                f"{note}{closes}"
            ),
            draft=False,
            artifact_dirs=tuple(c.artifact_dir for c in ready),
        )

    partial_plan: PrPlan | None = None
    if salvage:
        partial_plan = PrPlan(
            branch=f"reconcile/run-{run_id}-partial",
            commit_message=f"reconcile: {len(salvage)} partial case(s) (run {run_id})",
            title=f"reconcile: {len(salvage)} partial case(s) (run {run_id})",
            body=f"{_PARTIAL_WARNING}\n\n{_reconcile_table(salvage, with_reason=True)}",
            draft=True,
            artifact_dirs=tuple(c.artifact_dir for c in salvage),
        )

    return CollectPlan(ready=ready_plan, partial=partial_plan, skipped=skipped)
