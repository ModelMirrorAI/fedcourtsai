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

from .blinding import neutral_tool_class
from .finalize import FinalizeRole
from .schemas import AgentFlags, CellFailure, FlagSeverity, RetrievalCall, normalize_call

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


# The inverse split of `cell_artifact_name`. Three anchors make it unambiguous
# although both the actor id and the event id carry hyphens: an event id always
# begins `evt-` (`ids.event_id`), a docket is an integer, and a court id carries
# no hyphen. Example name: `predict-gemini-baseline-scotus-9026000183-evt-petition-arrival`.
_CELL_ARTIFACT_RE = re.compile(
    r"^(?P<role>[a-z]+)-(?P<actor>.+)-(?P<court>[^-]+)-(?P<docket>\d+)-(?P<event_id>evt-.+)$"
)


def parse_cell_artifact_name(role: FinalizeRole, name: str) -> ExpectedCell | None:
    """Read a cell's identity back out of its artifact name, or ``None``.

    The inverse of :func:`cell_artifact_name`, for the one caller that has the
    name and nothing else: the plan-time stranded-run guard, which *lists* a
    past run's artifacts rather than downloading them, and so must decide from
    the name alone whether a cell it is about to mint already ran.

    The parse is round-tripped through :func:`cell_artifact_name` before it is
    returned, so the two spellings of the convention cannot drift apart — a name
    this reads but cannot rebuild is reported unreadable rather than acted on,
    because a guessed split would name the wrong cell.

    The round trip cannot separate a genuinely ambiguous name, since both splits
    rebuild the same string: an event id that itself embedded ``-<digits>-evt-``
    would surrender its leading segments to the actor. That costs nothing, because the
    caller matches the result against real cells rather than trusting it — a
    mis-split yields a predictor id no registry holds, so the cell is minted
    rather than wrongly withheld.
    """
    match = _CELL_ARTIFACT_RE.match(name)
    if match is None or match["role"] != role.value:
        return None
    try:
        docket = int(match["docket"])
    except ValueError:
        # A digit run past the interpreter's int-parsing limit. Unreachable
        # through a real artifact name, and unreadable is the honest verdict —
        # the caller degrades one record rather than the whole census.
        return None
    cell = ExpectedCell(
        actor=match["actor"],
        court=match["court"],
        docket=docket,
        event_id=match["event_id"],
    )
    return cell if cell_artifact_name(role, cell) == name else None


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
    The collect job reports the stall only when this is true, so a genuine
    "nothing to do" run stays quiet.

    ``dead_actors`` are the engines that produced 0 of their cells this run — a
    whole engine absent from the tournament (e.g. quota exhaustion), as opposed
    to the per-cell ``skipped`` gaps. Because the live queue is
    transition-driven (it never re-queues a gap), a fully-absent engine would
    otherwise let the ready PR present a third of the board as silently
    missing; ``collect_plan`` therefore withholds the close and names the gap,
    so the round reads as incomplete.

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

    ``facts_only`` is the small auto-merging PR a *wholesale-failed* run opens to
    persist its per-cell failure facts when there is no ``ready`` and no
    ``partial`` PR to carry them (every cell was skipped, died, or otherwise left
    nothing to commit). Without it the ``attempt.json`` files
    :func:`cell_failures` computes would be written to the runner's checkout and
    then thrown away with it, so a persistently-100%-failing narrow run's attempt
    cap would never advance. Non-None exactly when ``ready`` and ``partial`` are
    both None **and** there is at least one failed cell; the workflow drives it
    through the same branch/gate/push loop as the other two kinds. It carries no
    ``Closes #`` — the run genuinely failed, so nothing it might close is
    settled by it — and its body is deterministic (no agent free text), so the
    secret scan cannot withhold the very facts it exists to persist.

    ``throttle_markdown`` is the harness-side counterpart of ``flags_markdown``:
    the warning that the shared upstream quota starved this run's retrieval,
    counted from the cells' own captured results rather than from an agent's
    account of them. It carries either the observed throttling or — where no
    cell could have shown any — the fact that the run was capture-blind, and is
    empty on a run that was genuinely clean. When non-empty it is appended
    ahead of the flags to whichever PR body opens, ``facts_only`` included:
    starvation is a live candidate cause of the wholesale failure that PR
    exists for.

    ``prior_availability_markdown`` is the other half of that question, and the
    one about the corpus rather than the upstream: whether the cells that asked
    the corpus index for priors got them. It travels the same way — appended to
    whichever PR body opens, ``facts_only`` included — and carries the
    code-mode capture tripwire beside it, because that is the blindness bound
    on its own count.
    """

    ready: PrPlan | None
    partial: PrPlan | None
    skipped: tuple[CellStatus, ...] = ()
    flags_markdown: str = ""
    throttle_markdown: str = ""
    prior_availability_markdown: str = ""
    feedback_comment: str = ""
    stalled: bool = False
    dead_actors: tuple[str, ...] = ()
    noun: str = ""
    missing_artifacts: tuple[str, ...] = ()
    uncovered_cells: tuple[ExpectedCell, ...] = ()
    salvage: tuple[CellStatus, ...] = ()
    facts_only: PrPlan | None = None


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


@dataclass(frozen=True)
class ThrottleRollup:
    """What this run's cell retrieval logs say about being starved by the quota.

    Counted over the **manifest-tool** calls whose result condition was legible
    (``fedcourtsai.schemas.observed_mcp_conditions``), which is the same
    denominator each log's own ``throttled_calls`` and the corpus rollup's
    per-engine rate use. Both of its exclusions drop calls that could never have
    shown a throttle: a builtin, which does not talk to the upstream this quota
    belongs to, and a result no transcript captured.

    ``cells`` therefore counts only the logs that could have shown one;
    ``blind_cells`` counts the rest — a Gemini cell, a cell that called no
    manifest tool — separately rather than as clean cells, because a cell that
    could not be observed is not evidence that nothing happened to it.
    """

    cells: int = 0
    throttled_cells: int = 0
    calls: int = 0
    throttled_calls: int = 0
    blind_cells: int = 0


def render_throttle_note(rollup: ThrottleRollup | None) -> str:
    """The run PR's warning about what the upstream quota did to this run.

    Two things can be worth saying, and a run says at most one. A **throttle**
    was observed → the count, its denominator, and what it costs a reader. No
    throttle was observed *and no cell could have shown one* → the shorter line
    that the run is capture-blind, which is a different claim from a clean run
    and the one a maintainer would otherwise draw by default.

    Everything else returns ``""``, and that includes the genuinely clean run:
    a standing "0 throttled" paragraph on a surface read once per run is noise
    that trains the eye to skip exactly the place the warning will one day
    appear. The corpus-wide tool-usage report makes the opposite choice on
    purpose — a diagnostic's reader needs to see that the question was asked.
    """
    if rollup is None:
        return ""
    if rollup.throttled_calls == 0:
        if rollup.cells or not rollup.blind_cells:
            return ""
        # Logs exist and not one of them could have shown a throttle. Silence
        # here would be read as a clean run, which is the reading this whole
        # marker exists to make impossible.
        return (
            f"**Retrieval throttling was not observable this run**: none of "
            f"{rollup.blind_cells} cell log(s) captured a manifest-tool result condition, "
            f"so no cell could have been seen being rate-limited. Capture-blind, not "
            f"throttle-free — an engine whose transcript drops results (Gemini's, by "
            f"construction) and a cell that called no manifest tool both land here, and "
            f"neither is evidence that the shared quota was not in the way."
        )
    blind = (
        f" {rollup.blind_cells} further cell(s) captured no result and could not be "
        f"observed either way."
        if rollup.blind_cells
        else ""
    )
    return (
        f"⚠️ **Retrieval was throttled this run**: {rollup.throttled_calls} of "
        f"{rollup.calls} manifest-tool result(s) whose condition capture could read came "
        f"back rate-limited — the shape an upstream HTTP 429 takes, which is what the "
        f"CourtListener MCP server renders a quota refusal as — across "
        f"{rollup.throttled_cells} of {rollup.cells} cell log(s) whose results were "
        f"legible.{blind} Those cells retrieved less than an unthrottled cell would have "
        f"— the shared daily quota, not the agent — so read their coverage, and any "
        f"comparison that puts them beside a well-fed cell, with that in mind. The count "
        f"is a floor: a call whose result never reached the transcript cannot be counted, "
        f"a builtin's result is not read for this at all, and a cell that gave up on a "
        f"call leaves no row."
    )


# The freeform builtin a code-mode engine is given in place of direct tool
# exposure; capture mints the parent row under this name, and the manifest
# calls the program makes are lifted out of its source into rows of their own
# marked `code_mode_source`. A parent standing beside no lifted row is what
# :func:`code_mode_lift_blind` keys on. Held here rather than imported so the
# retrieval parser stays the one place that mints rows; a test pins the two
# spellings together so a rename fails rather than silences the tripwire.
CODE_MODE_PARENT_TOOL = "exec"

# The corpus-CLI commands that pull priors, as they appear in a captured
# command line — the same pair `tooling.json`'s `used_corpus_query` asks the
# cell about, so the harness-observed side and the self-reported side
# denominate over one command family rather than two. Lenient about the
# command's surroundings, because a row keeps only a 500-character slice of its
# params and the invocation carries whatever prefix the cell typed (`uv run`, a
# `timeout`): the pattern matches wherever in the command it sits.
#
# Strict about one thing, because it is the difference between a query and a
# reading of the manual: `--help` does not touch the corpus. A cell that ran
# `fedcourts query --help`, read the flags, and decided the committed statpack
# answered its question **declined** — counting that as a service failure would
# report a choice as an outage, and it is the single commonest shape a
# code-mode cell's program takes.
_CORPUS_QUERY_RE = re.compile(r"\bfedcourts\s+(?:query|open-events)\b(?![\s\"'\\]*(?:--help|-h)\b)")
# Where one command in a captured line ends and the next begins. Only the
# segment a match sits in decides whether it is an invocation, so a chained
# `cat schemas/... && uv run fedcourts query ...` is still a query.
_SHELL_SEGMENT_RE = re.compile(r"[\n;|&]+")
# Commands that take the corpus CLI's *name* as a pattern or a path rather than
# running it — a cell grepping `docs/cli.md` for the flags asked the
# repository, not the corpus.
_READS_THE_NAME_RE = re.compile(r"\b(?:rg|ripgrep|grep|egrep|fgrep|sed|awk|less|head|tail)\b")

# How many starved cells the note names before it summarizes the rest. The
# names are the actionable part — they say which predictions to read as
# prior-thin — but a wide run could starve dozens, and a PR body that is mostly
# one paragraph of cell ids stops being read at all.
_NAMED_CELL_CAP = 8


#: The code-mode builtins that **run a command**, out of the enumerated set the
#: retrieval lift mints rows for. The other three carry prose the program wrote
#: — a patch body, a plan step, an image path — and their argument text becomes
#: the row's query slice verbatim, so a plan step reading "pull priors with
#: `fedcourts query`" or a patch that writes the attempted command into the
#: cell's own `retrieval.md` would otherwise be counted as the invocation it
#: describes. That is the same confusion between running a command and writing
#: one down that the shell-class screen exists to prevent, arriving by another
#: door. `test_the_command_running_builtins_are_a_subset_of_what_the_lift_mints`
#: pins this against the lift's own list, so a name added there is classified
#: rather than silently admitted.
CODE_MODE_SHELL_BUILTINS = frozenset({"exec_command", "write_stdin"})


def _ran_commands(call: RetrievalCall) -> bool:
    """Whether this row is one a corpus query could have been *run* from.

    Two shapes qualify, and the second is the whole reason this is a function
    rather than one comparison:

    * a **shell** call — which engine spellings those are comes from
      :func:`~fedcourtsai.blinding.neutral_tool_class`, the one place this
      vocabulary is defined, rather than a second copy that would drift from
      it;
    * a row **lifted out of a code-mode program's source** naming one of the
      command-running builtins (:data:`CODE_MODE_SHELL_BUILTINS`). A code-mode
      cell runs every command from inside a program, so those rows are its
      shell, and reading only the first shape would count such a cell's corpus
      attempts at nearly zero however many it made.

    What neither shape admits is a row that merely *carries* the command as
    content — a ``Write`` of the cell's own ``retrieval.md`` describing what it
    tried, or the patch/plan builtins that do the same from inside a program —
    which is why both tests are on the tool rather than on the text. A lifted
    row is weaker evidence than a shell row either way, since the lift reads
    program *text*: a call site in an untaken branch counts though it never
    ran. The note this feeds is advisory and says so.
    """
    if neutral_tool_class(call.tool) == "shell":
        return True
    return call.call_source == "code_mode_source" and call.tool in CODE_MODE_SHELL_BUILTINS


def attempted_corpus_query(calls: Sequence[RetrievalCall]) -> bool:
    """Whether this cell's captured shell ran a corpus-prior query at least once.

    The harness-observed half of :class:`PriorAvailabilityRollup` — read from
    the cell's own ``retrieval_log.json`` rather than from what the agent said
    about its tooling. Three screens, and each drops a row where the command's
    *name* appears but no query ran, because every one of those would otherwise
    report a cell's choice as the corpus failing it:

    * the row must be one a command could have been run from
      (:func:`_ran_commands`) — otherwise a cell that only *wrote* the command
      into its own ``retrieval.md``, describing what it tried, would read as
      having run it;
    * the subcommand must not be immediately followed by ``--help`` / ``-h``
      (:data:`_CORPUS_QUERY_RE`) — a flag further along the line is not
      screened, which errs toward counting the attempt;
    * and the command *segment* it sits in must not be a `grep`-alike reading
      the corpus CLI's name out of this repository's docs.

    What survives is still syntactic, and still misses in one direction: an
    invocation past a row's 500-character query cut is not counted at all. That
    bites hardest on a code-mode parent, whose slice holds only the head of a
    whole program — which is why the lifted rows count too, each carrying one
    call at its own head. What no row can show is a command the lift never
    matched, and nothing here watches for that: :func:`code_mode_lift_blind`
    beside it keys on the *manifest* half of the lift, so it is correlated with
    this count's coverage rather than a bound on it — a drift in the *builtin*
    idiom would empty this count for every code-mode cell and leave the
    tripwire silent. The note both feed is advisory, and says so.
    """
    for call in calls:
        if not _ran_commands(call):
            continue
        text = call.query or ""
        for match in _CORPUS_QUERY_RE.finditer(text):
            segment = _SHELL_SEGMENT_RE.split(text[: match.start()])[-1]
            if not _READS_THE_NAME_RE.search(segment):
                return True
    return False


def code_mode_lift_blind(calls: Sequence[RetrievalCall]) -> bool:
    """Whether this cell ran a code-mode program and nothing was lifted from it.

    The tripwire on the capture path the attempt count depends on. A code-mode
    cell reaches everything — manifest tools and the shell alike — from inside
    the program one freeform :data:`CODE_MODE_PARENT_TOOL` call carries, so the
    only rows that can name what it did are the ones capture lifts out of that
    program's source. Parents with no lifted row beside them is the shape a
    lift that stopped matching the engine's calling idiom leaves.

    Keyed on the **manifest** lifted rows, because capture lifts two idioms out
    of that source and each fails on its own. A program's builtin calls are the
    commoner shape by far, so a run whose manifest idiom stopped matching still
    mints lifted rows — and a tripwire that counted those would go quiet
    exactly where the manifest spelling drifted, which is the drift it exists
    to catch. The asymmetry is deliberate and it leaves the other half
    unwatched: a rename on the *builtin* side trips nothing here, and shows up
    instead as a code-mode cell's capture rate climbing back toward 1.0 while
    its program does all the work.

    It is a hint, not a finding, and it is loose at both ends. A program that
    genuinely called no manifest tool leaves the same shape as a lift that
    matched nothing, and the rows cannot separate the two. Nor can they
    separate a code-mode parent from an ordinary shell call an engine happens
    to spell the same way: the parser distinguishes them by the transcript
    item's *type*, which no field of the row records. That is exactly why it is
    worth printing — the reading a maintainer would otherwise default to is
    that the cell simply retrieved nothing.
    """
    return any(call.tool == CODE_MODE_PARENT_TOOL for call in calls) and not any(
        call.call_source == "code_mode_source" and normalize_call(call.tool) is not None
        for call in calls
    )


@dataclass(frozen=True)
class PriorAvailabilityRollup:
    """Whether this run's corpus priors actually reached the cells that asked.

    A cell whose ``fedcourts query`` times out against the corpus index is not
    a failed cell: it finishes, predicts from whatever else it had, and the
    only trace is one line in its own ``tooling.json``. Across a fan-out that
    is invisible, which is what this counts — the run-level rate at which the
    corpus-prior channel served the cells that reached for it.

    The two sides are **different kinds of evidence** and must not be read as
    one measurement. ``attempted`` is harness-captured: a row in the cell's
    retrieval log that a command could have been run from — a shell call, or
    one lifted out of a code-mode program — whose command ran a corpus-prior
    query. ``served`` is
    the cell's own word: the sibling ``tooling.json``'s ``used_corpus_query``.
    So ``starved`` is not "the corpus failed this cell" — it is the *disagreement*
    between the two channels, and at least three things produce it: a query
    that failed or timed out, a cell that queried and answered the field on
    some other reading, and a mis-parse on either side. On a **code-mode** cell
    there is a fourth, and it is why the two halves of ``attempted`` are not one
    kind of evidence either: such a cell's commands are read out of its
    program's source rather than observed running, so a call site in a branch
    the program never took is counted as an attempt. On a shell cell the
    statistic is "ran it, and did not report using it"; on a code-mode cell it
    is "asked for it in the program text, and did not report using it". The
    rows separate none of this, which is why the count is advisory and the note
    names the disagreement rather than a cause.

    On the ``served`` side the two channels do at least ask about roughly the
    same commands, and where they differ it is in the safe direction:
    :data:`_CORPUS_QUERY_RE` covers the ``query`` / ``open-events`` pair, while
    the tooling field's own wording ("query/open-events/etc.") is a
    **superset** — so a broader reading of the field can only move a cell out
    of ``starved``, never into it. That is a property of that side alone: the
    code-mode reading above moves cells the other way.

    ``cells`` is every legible cell log this run, the count ``attempted`` is a
    subset of. It rides along because ``attempted`` is not "the cells that
    asked": what capture could read of a cell's commands differs by
    engine — a code-mode cell's are visible only as far as the lift matched its
    program — so the denominator is **legibility**, and a reader who cannot see
    how much of the run it covers will read it as the run. For the same reason
    the rate is a within-run reading rather than a series: what capture can see
    of an engine moves with the parser, so two runs' rates are comparable only
    where nothing about capture changed between them. Unlike the row-level
    capture figures, which are baked at parse time and never re-derived, this
    rollup is computed **at collect time over committed rows** — so re-running
    ``collect-plan`` over an old run answers with today's predicate rather than
    the one that wrote that run's PR body, and nothing on either surface
    records which produced it.

    ``starved`` and ``unreported`` name their cells (``case/event/actor``)
    rather than counting them. They are separate because the claims differ:
    ``starved`` is a cell that reported no corpus use, ``unreported`` a cell
    whose report could not be read at all, which is unknown rather than no.
    Both lists are in artifact-walk order, so they are a prefix rather than a
    ranking — the note says so, because the cap means only the first few show.

    ``lift_blind_cells`` of ``code_mode_cells`` is the blindness bound on
    everything above, the counterpart of :class:`ThrottleRollup`'s
    ``blind_cells``. It carries its own denominator because it is a standing
    condition rather than a per-run event: the lift matches calling idioms
    syntactically and this counts the cells whose *manifest* one produced
    nothing, and a bare numerator on a surface read once per run would present
    a long-running gap as a fresh regression every time.
    """

    cells: int = 0
    attempted: int = 0
    served: int = 0
    starved: tuple[str, ...] = ()
    unreported: tuple[str, ...] = ()
    code_mode_cells: int = 0
    lift_blind_cells: int = 0


def _named_cells(names: Sequence[str]) -> str:
    """Cell ids as an inline code-quoted list, capped at :data:`_NAMED_CELL_CAP`.

    Each id is collapsed to one line and stripped of the backtick that would
    otherwise close the code span early — the same defence :func:`_md_cell`
    gives an agent-authored flag message. Belt and braces here: the ids are
    harness-written (capture stamps the log's ``case_id`` / ``actor_id`` from
    the matrix after the agent has finished, and the event id comes from the
    artifact path), so the no-agent-text property the facts-only PR body relies
    on holds without this — but the file does sit in the cell's own tree, and
    the escape costs nothing.
    """
    shown = ", ".join(f"`{_md_cell(name).replace('`', '')}`" for name in names[:_NAMED_CELL_CAP])
    rest = len(names) - _NAMED_CELL_CAP
    return f"{shown}, and {rest} more" if rest > 0 else shown


def render_prior_availability_note(rollup: PriorAvailabilityRollup | None) -> str:
    """The run PR's note on the corpus-prior channel, or ``""``.

    Up to three paragraphs, each printed only when it has something to say: the
    cells that asked the corpus for priors and reported not getting them, the
    cells whose answer could not be read at all, and the tripwire on whether
    code-mode capture could have seen such an attempt in the first place. The
    first two are separate because the claims are: a warning that the channel
    failed is not the same as a note that nobody can tell, and merging them
    would let the louder one speak for both.

    The two prior paragraphs are silent on a run where every attempt was
    served, and on one where no cell asked — the same convention
    :func:`render_throttle_note` keeps, and for the same reason: a standing "0
    starved" paragraph on a surface read once per run trains the eye to skip
    exactly the place the warning will one day appear. The denominator
    therefore rides inside the warning, where a reader needs it, rather than
    standing alone as a clean-run line.

    The tripwire is **not** conditioned on either of them, so a fully-served run
    still prints it whenever a code-mode program lifted nothing. That is
    deliberate: it is a statement about what capture could see, and a
    fully-served run is exactly where an unseen attempt would be least
    suspected. It is the reason this function returning non-empty is not by
    itself evidence that anything went wrong with the corpus.
    """
    if rollup is None:
        return ""
    paragraphs: list[str] = []
    if rollup.starved:
        paragraphs.append(
            f"⚠️ **Cells ran a corpus query and reported no corpus use**: "
            f"{len(rollup.starved)} of {rollup.attempted} cell(s) whose corpus attempt was "
            f"legible — an attempt is counted differently by engine, see below — out of "
            f"{rollup.cells} legible cell log(s) this run — "
            f"{_named_cells(rollup.starved)} (walk order, not severity). **A disagreement "
            f"between two channels, not a diagnosis.** The attempt is harness-captured (a "
            f"row a command could have run from — a shell call, or one lifted out of a "
            f"code-mode program); the service is the cell's own `tooling.json`. Three "
            f"things leave this shape and the rows tell none of them apart: a query that "
            f"failed or timed out against the corpus index (the reason the count is worth "
            f"printing), a cell that queried, got rows, and answered the field on some "
            f"other reading, and a mis-parse on either side. On a **code-mode** cell there "
            f"is a fourth, because its attempt is not an execution: its commands are read "
            f"out of the program's own source, so a call site in a branch the program "
            f"never took counts as an attempt. Read the named cells' `tooling.json` notes "
            f"before concluding anything about their priors. Not comparable across engines "
            f"— a shell row is an execution, a lifted row a source-text site — nor across "
            f"runs whenever capture itself has moved between them; and a drift in the "
            f"code-mode builtin idiom would empty these counts for such cells with nothing "
            f"here to show it."
        )
    if rollup.unreported:
        paragraphs.append(
            f"❔ **Whether the corpus served {len(rollup.unreported)} of {rollup.attempted} "
            f"cell(s) with a legible attempt cannot be read**: no `tooling.json` of their own "
            f"parsed, so there is no answer either way — unknown, not served and not "
            f"starved: {_named_cells(rollup.unreported)}. The denominator is what capture "
            f"could read of each engine's commands, so it is a within-run figure."
        )
    if rollup.lift_blind_cells:
        paragraphs.append(
            f"🔍 **Code-mode capture may be blind**: {rollup.lift_blind_cells} of "
            f"{rollup.code_mode_cells} cell(s) that called the freeform "
            f"`{CODE_MODE_PARENT_TOOL}` builtin — how a code-mode engine runs a program — "
            f"had **zero** manifest calls lifted out of its source. Three readings, and the "
            f"rows separate none of them: the program called no manifest tool worth a row, "
            f"the lift no longer matches the engine's manifest calling idiom, or the call "
            f"was an ordinary shell call an engine spells the same way (the parser tells "
            f"those apart by the transcript item's type, which no row records). A standing "
            f"condition rather than a fresh regression: check the ratio "
            f"against earlier runs before reading it as new. It watches the **manifest** "
            f"half of the lift while any attempt count above reads the **builtin** half, "
            f"so it is correlated with their coverage rather than a bound on it — neither "
            f"implies the other. What a lifted row does and does not claim: `call_source` "
            f"in `docs/predicted-artifacts.md`."
        )
    return "\n\n".join(paragraphs)


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
    """The stall report for a run that produced **no** output at all.

    A wholesale failure — every cell dying before its agent ran, or every cell
    finishing without an artifact — opens no PR, so without this the run would
    be invisible unless someone read the Actions history. The collect job's
    stall step writes it to the run's step summary (and, given an issue number,
    comments it there with the ambient ``GITHUB_TOKEN``, a non-triggering
    write).
    """
    return (
        f"⚠️ This {role.value} run **produced no output** — no cell "
        f"delivered an artifact, so nothing was committed and no PR opened. This "
        f"usually means the cells failed before their agents ran (job-setup or "
        f"infrastructure errors) rather than the agents declining the work.\n\n"
        f"Run log: {run_url}\n\n"
        f"Nothing has to be re-filed. The cells this round failed to produce are "
        f"still missing from committed state, so the next scheduled "
        f"{role.value} round derives them again once the cause is fixed; a "
        f"`workflow_dispatch` runs one sooner."
    )


def collect_plan(  # noqa: PLR0913 - one arg per independent per-run input the plan reads
    role: FinalizeRole,
    *,
    run_id: str,
    cells: Sequence[CellStatus],
    issue: int | None = None,
    flags: Sequence[AgentFlags] = (),
    missing_artifacts: Sequence[str] = (),
    expected: Sequence[ExpectedCell] = (),
    throttle: ThrottleRollup | None = None,
    prior_availability: PriorAvailabilityRollup | None = None,
) -> CollectPlan:
    """Partition a run's cells into one ready PR, one draft PR, and the skipped.

    A cell is **ready** (agent finished, wrote output, it validated) → the one
    auto-merging PR; **salvageable** (it wrote output but stopped early or failed
    validation) → the one *draft* PR a maintainer completes (a draft never
    auto-merges, preserving the per-cell graceful degradation the old
    one-PR-per-cell flow had); or **skipped** (it produced nothing) → nothing to
    commit, returned only so the workflow can warn. A run with no ready cells
    opens no ready PR; with nothing to salvage, no draft.

    ``issue`` is an optional issue for the ready PR to close on merge. No lane
    supplies one — every round enters on a schedule or a dispatch, neither of
    which carries an issue — so the parameter is the seam a future one would
    use, and the ``None`` path is the only one exercised in production
    (``tests/test_collect_issueless.py``). Where a number is given, the close
    lands on merge — but only when nothing is left to salvage, **no whole
    engine is absent** (a
    fully-missing engine at 0/N, see ``dead_actors``), **no cell's artifact was
    lost in transfer** (``missing_artifacts``), and **no queued cell went missing
    entirely** (``expected``), so a run with a pending draft or any uncovered gap
    closes nothing and stands as the record of the follow-up owed.

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
    tracking issue — a durable, centralized home for an agent's note that outlives
    the run itself, and even a fully-failed run that opens no PR.

    ``throttle`` is the run's harness-captured starvation count, summarized from
    the cells' own retrieval logs. It rides the same PR body as the flags because
    it answers the question a reader of those flags is already asking — whether
    the run's cells got the retrieval they asked for — and because the run PR is
    the only durable per-run surface that could carry it: the 429 evidence itself
    is digested away at capture, so nothing else records that a run was starved.
    Silent on a run that was genuinely clean, but not on one that merely could
    not see — those two must not look alike.

    ``prior_availability`` asks the same question of the *corpus* channel:
    which cells reached for corpus priors and did not get them. It rides the
    same bodies for the same reason. Its warning is likewise silent on a run
    where every attempt was served; the code-mode capture tripwire it carries
    beside that warning is not, because it reports on what could be seen rather
    than on what happened.
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
    # run — and unlike a partial failure it leaves no salvage draft to mark the
    # round incomplete. The live queue is transition-driven, so the gap never
    # re-queues; without withholding the close here the ready PR (the surviving
    # engines) would present the round as covered with that engine absent.
    # Keys on `produced` (not `agent_ok`): an engine that ran cleanly but
    # declined every cell is the same missing seat as a quota failure — the
    # tournament expects every seat to produce, so both withhold the close.
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
                f"⚠️ No output at all from {engines} this round — a full engine is "
                f"missing and the live queue will not re-queue it, so the gap needs a "
                f"named backfill (the per-case predictors filter) rather than the next "
                f"scheduled round."
            )
        if uncovered:
            rows = "\n".join(
                f"- `{c.actor}` on `{c.court}/{c.docket}` `{c.event_id}`" for c in uncovered
            )
            notes.append(
                f"⚠️ {len(uncovered)} queued cell(s) uploaded nothing at all — no "
                f"artifact and no status, so the cell died before it could report. "
                f"Re-running `collect` will not recover these; they need a re-derivation, "
                f"which the next scheduled round does on its own.\n{rows}"
            )
        if lost:
            names = "\n".join(f"- `{n}`" for n in lost)
            notes.append(
                f"⚠️ {len(lost)} cell artifact(s) did not transfer, so their output "
                f"is **not** in this PR even though the cells may have succeeded. "
                f"Re-run the `collect` job to recover them "
                f"(cell artifacts are retained 7 days).\n{names}"
            )
        note = ("\n\n" + "\n\n".join(notes)) if notes else ""
        # Close a named issue from the ready PR, but not while a draft still
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

    throttle_md = render_throttle_note(throttle)
    prior_md = render_prior_availability_note(prior_availability)

    # A wholesale-failed run — no ready PR and no draft — still has failure facts
    # to persist (skipped/salvage/uncovered), and no other PR to carry them. The
    # facts-only PR does that so the attempt cap advances even for a narrow run
    # that never opens a normal PR. Only when there is genuinely no other PR: any
    # ready or partial PR already unions the same `data/` (where the facts are
    # written) into its own commit, so opening a facts-only PR alongside would
    # duplicate them.
    facts_only_plan: PrPlan | None = None
    if ready_plan is None and partial_plan is None:
        facts_only_plan = _facts_only_plan(
            role,
            run_id=run_id,
            skipped=skipped,
            salvage=tuple(salvage),
            uncovered=uncovered,
            notes=(throttle_md, prior_md),
        )

    flags_md = render_flags(flags)
    # The harness facts first — what the run could see, and what reached it —
    # because that is the frame a maintainer needs before reading the agents'
    # own accounts of what they found.
    ready_plan, partial_plan = _append_sections(
        ready_plan, partial_plan, (throttle_md, prior_md, flags_md)
    )
    return CollectPlan(
        ready=ready_plan,
        partial=partial_plan,
        skipped=skipped,
        flags_markdown=flags_md,
        throttle_markdown=throttle_md,
        prior_availability_markdown=prior_md,
        feedback_comment=render_feedback_comment(role, run_id, flags_md),
        stalled=bool(cells) and not any(c.produced or c.agent_ok for c in cells),
        dead_actors=dead_actors,
        noun=noun,
        missing_artifacts=lost,
        uncovered_cells=uncovered,
        salvage=tuple(salvage),
        facts_only=facts_only_plan,
    )


def _facts_only_plan(
    role: FinalizeRole,
    *,
    run_id: str,
    skipped: Sequence[CellStatus],
    salvage: Sequence[CellStatus],
    uncovered: Sequence[ExpectedCell],
    notes: Sequence[str] = (),
) -> PrPlan | None:
    """The auto-merging PR that persists a wholesale-failed run's failure facts.

    Returns None when there is nothing to record (no failed cell), so the caller
    opens no PR. Otherwise it mirrors the ready PR — a run-scoped ``<role>/run-<
    run_id>-facts`` branch the workflow drives through the same gate/push loop —
    but carries no ``data/`` union of its own: the ``attempt.json`` facts are
    already written into the checkout's ``data/`` by ``record-cell-failures``
    before the loop, so this PR's ``git add data/`` simply picks them up. It never
    closes any issue (the run failed) and its body is deterministic — no
    agent-authored text — so the producer-side secret scan can never withhold the
    branch and lose the very facts it exists to persist.

    ``notes`` are the run-level retrieval roll-ups — the upstream quota turning
    cells away (or no cell being able to tell), and the corpus index not
    serving the cells that asked it for priors. They ride along when they have
    anything to say, because this is the one PR a wholesale-failed run opens
    and starvation on either channel is a live candidate cause of one. Both are
    harness-rendered from the cells' own logs, so they keep the body's
    no-agent-text property. Empty ones are dropped.
    """
    total = len(skipped) + len(salvage) + len(uncovered)
    if total == 0:
        return None
    rows = [
        *(_facts_row(c.actor, c.court, c.docket, c.event_id, "no output") for c in skipped),
        *(
            _facts_row(c.actor, c.court, c.docket, c.event_id, "produced, unusable")
            for c in salvage
        ),
        *(_facts_row(c.actor, c.court, c.docket, c.event_id, "never uploaded") for c in uncovered),
    ]
    table = "\n".join(["| actor | case | event | why |", "|---|---|---|---|", *rows])
    body = (
        f"Every cell of run `{run_id}` failed, so this run produced no output and "
        f"opens no {_JUDGMENT_NOUN[role]} PR. This PR persists one durable "
        f"`attempt.json` per failed cell so the per-cell attempt cap advances "
        f"even for a run that never opens a normal PR.\n\n"
        f"{table}\n\n"
        f"The cells are still owed: none of them landed a {_JUDGMENT_NOUN[role]}, so "
        f"the next scheduled round derives them again — this PR only records that "
        f"they were attempted."
    )
    for note in notes:
        if note:
            body = f"{body}\n\n{note}"
    return PrPlan(
        branch=f"{role.value}/run-{run_id}-facts",
        commit_message=f"{role.value}(run {run_id}): {total} cell-failure fact(s)",
        title=f"{role.value}: {total} cell-failure fact(s) (run {run_id})",
        body=body,
        draft=False,
        artifact_dirs=(),
    )


def _facts_row(actor: str, court: str, docket: int, event_id: str, why: str) -> str:
    return f"| `{actor}` | `{court}/{docket}` | `{event_id}` | {why} |"


def _append_sections(
    ready: PrPlan | None, partial: PrPlan | None, sections: Sequence[str]
) -> tuple[PrPlan | None, PrPlan | None]:
    """Append the run-level roll-ups to the run's primary PR body (ready, else draft).

    The flag roll-up, the throttle note, and the prior-availability note belong
    to the run, not a single cell, so they ride the one PR a maintainer reviews
    — the auto-merging ready PR when there is one, otherwise the draft. Empty
    sections are dropped, so a run with none leaves the body untouched; with no
    PR at all each roll-up still travels on the plan (``flags_markdown`` /
    ``throttle_markdown`` / ``prior_availability_markdown``) and out through
    ``collect-plan``'s JSON.

    They are not equally surfaced. The flag roll-up also reaches the Actions
    summary and the agent-feedback issue, because the collect action reads it
    off that JSON and echoes it; the two harness-rendered notes reach the PR
    body alone until that action is wired to echo them too, which is a change
    to the permission surface and so a maintainer's to make. All three are on
    the JSON so the wiring is the only thing missing.
    """
    body = "\n\n".join(section for section in sections if section)
    if not body:
        return ready, partial
    if ready is not None:
        return replace(ready, body=f"{ready.body}\n\n{body}"), partial
    if partial is not None:
        return ready, replace(partial, body=f"{partial.body}\n\n{body}")
    return ready, partial


def cell_failures(plan: CollectPlan, *, run_id: str, role: FinalizeRole) -> list[CellFailure]:
    """One durable failure fact per cell that ran and produced no usable artifact.

    The writer side of the per-cell attempt cap. ``collect`` is the only observer
    of a cell failure but is corpus-blind, so each fact is a git-ledger
    ``attempt.json`` the derivers later count
    (:func:`fedcourtsai.matrix.cell_failure_count`) — but only once it is
    committed, and a fact rides a PR. On a run with any output the facts ride the
    run's own ready/partial PR; on a wholesale-failed run where every cell died
    and no ready/partial PR opens, they ride the small auto-merging *facts-only*
    PR (``ready``/``partial`` both None → :func:`_facts_only_plan`), so even a
    persistently-100%-failing narrow run accrues committed facts and its cap
    advances. The only tail left uncovered is a run that leaves no trace at all
    (no cell artifact *and* no matrix to enumerate what it should have produced),
    for which the loud stall comment is the sole signal. The truly-failed cells
    are the union of three disjoint buckets — ``skipped``, ``salvage``, and
    ``uncovered_cells``:

    * ``skipped`` — ran and produced nothing (``no_output``).
    * ``salvage`` — produced output that failed validation or stopped early
      (``partial``).
    * ``uncovered_cells`` — queued but uploaded nothing at all; the job died before
      it could report (``died``).

    ``missing_artifacts`` is deliberately excluded: a lost artifact is
    re-collectable download loss (re-run ``collect``), not a cell failure, so it
    must not burn a cap attempt. ``dead_actors`` is not a separate bucket either —
    it is engine-level and only *refines* the class. An engine that uploaded at
    least one status but produced nothing lands in ``dead_actors``, so its
    ``skipped``/``salvage`` cells read ``quota``; an engine that uploaded nothing
    at all is absent from ``dead_actors`` (it never entered ``cells``), so its
    ``uncovered`` cells stay ``died``. Either way every fact counts equally.

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
