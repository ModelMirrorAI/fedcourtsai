"""Offered-vs-called tool rollup over the committed retrieval logs.

Read-only and offline: it reads ``data/`` and nothing else — no corpus, no
network — so it runs in the gate and answers, from cells that already ran, which
configured tools are actually being used.

Six questions, and one trap.

**Which offered tools were never called?** A cell's log records what it *called*;
the offered set comes from ``mcp_tools``, snapshotted from the pinned manifest at
capture time. ``mcp_servers`` cannot supply it — it names servers, and a server
advertises many tools — so a log written before ``mcp_tools`` existed has an
unknown denominator, reported as such rather than as zero offered.

**Which are called by some engines and not others?** Usually a prompt or sandbox
problem rather than a tool problem, so per-engine counts sit beside every total.

**How often is each called, and by whom?** Per engine and per actor.

The trap is interpretive, and the report is shaped to avoid setting it: a tool
can be unused because it is useless, because the prompt never mentions it, or
because a sandbox blocked it. Only the first would justify retiring it, and this
data cannot distinguish them. So a zero is reported as *never called*, always
beside the number of cells that offered it — a tool offered in 3 cells and never
called reads very differently from one offered in 400 — and the cause is left to
a human.

Engines do not agree on tool names. The same MCP tool arrives as
``mcp__courtlistener__search`` from one and ``mcp_courtlistener_search`` from
another, so calls are normalized to ``<server>.<tool>`` before counting;
un-normalized, one tool splits into two rows and every rate is wrong.

**Was the answer captured?** A call and its result are two different facts, and
only one of them is reliably in the record. ``result_digest`` is positive
evidence that the result side was captured and non-empty; a null covers both an
empty result and a result the engine's transcript never carried.
:class:`~fedcourtsai.schemas.RetrievalCall` carries a ``result_capture`` marker
that separates exactly those two, but only the logs captured since it existed
carry it; on the rest it reads null — capture-unknown, which is a third thing
again. So the rollup reports two
states per call, not three, and takes the
engine-level reading the per-call record cannot yet give: an engine with no positive
instance across every **MCP** call it ever made has an unobservable result side,
and its dead-end rows are withheld rather than printed as 100%. Gated on the MCP
subset rather than on any call, because a builtin whose output pairs cleanly
says nothing about whether the manifest tools' results reach the transcript.

**Was the cell starved?** Where a **manifest-tool** result was captured, its
``result_status`` says what came back, and ``throttled`` is the state that
changes how the cell should be read: the shared upstream quota turned the call
away, so it retrieved nothing and its cell is not comparable with a well-fed
one. Reported per engine as a count over the MCP calls whose condition was
legible — never over every call, since builtins cannot be throttled by this
quota and an engine whose results never reach the transcript would otherwise
post a clean 0% off a transcript that could not have shown a throttle. Every
figure is a floor: the parse-time predicate is anchored on the server's own
rate-limit phrasing and biased to miss rather than invent, and calls a starved
cell gave up on making leave no row at all. The cut is **descriptive of which
cells were unlucky, not a comparison between engines** — one bucket is consumed
run-wide, so a row measures ordering within the run.

**What did the calling cost?** Each log's sibling ``usage.json`` carries the
cell's estimated cost, so calls-per-cell and dollars-per-cell come from the same
join. A cell that committed no usage record contributes a null cost, never a
zero — a free cell and an unmeasured one must not average together.

**Did any of it help?** The question the rollup exists to reach and the one it
refuses to answer: call volume against the evaluators' Brier scores, published
as a denominator table with an ``n`` beside every mean. A Brier is a grade, so
that block alone is scoped to blessed processes and never pooled across modes or
across declared forecast moments, and it publishes a coefficient only for a
population that clears :data:`TOOL_USAGE_CORRELATION_MIN_CELLS` — there is no
pooled coefficient at any n.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from statistics import fmean, median

from .integrity import latest_evaluation_runs
from .leaderboard import kendall_tau_b
from .pipeline.moments import spec_for
from .process_version import graded_post_freeze, is_frozen
from .retrieval import RETRIEVAL_CALL_CAP
from .schemas import (
    Evaluation,
    ModelUsage,
    Prediction,
    RetrievalCall,
    RetrievalLog,
    ToolUsage,
    ToolUsageCell,
    ToolUsageCut,
    ToolUsageEngine,
    ToolUsageEntry,
    ToolUsefulness,
    ToolUsefulnessCorrelation,
    ToolUsefulnessSegment,
    UsageRole,
    normalize_call,
)
from .serialize import read_model

TOOL_USAGE_CORRELATION_MIN_CELLS = 30
"""Cells a population needs before its call-volume/Brier correlation is published.

Declared here, in code, ahead of any coefficient rather than judged once one is
in view — the difference between a floor and an excuse. Below it a rank
correlation is dominated by which handful of cases happened to be graded, and
publishing the number anyway invites exactly the reading the data cannot carry:
that retrieval helps, or that it does not. The published surface prints the
denominators instead and says it is under-powered.

Applied **per population** — one (mode, stage, moment) group at a time, within a
declared process scope — and never to a pooled total. Two under-powered
populations summing past the floor is not one population that cleared it, and
the pooled number would be the one a reader quotes.

Thirty is a necessary condition, never a sufficient one. Even above the floor
these cells are not independent — several judges score one prediction, several
moments share one case, and a cell calls more tools partly *because* its case is
hard — so a coefficient that clears it is still descriptive, never causal.
"""

# Per-cell scatter rows the Markdown will print inline. Past this the table
# stops being a scatter a reader can see and becomes a wall between them and the
# sections below; the rows stay in the JSON artifact either way.
_SCATTER_ROWS_MAX = 40

# What a cell's mode is called when its log predates the mode field. Not
# `forward`: an unrecorded mode is unknown, and defaulting it to the mode that
# happens to dominate today would make the cut agree with itself.
_UNKNOWN = "unknown"

# The engines' open-web tools, by their own names: claude-code's `WebSearch` /
# `WebFetch`, gemini's `google_web_search` / `web_fetch`, and codex's hosted
# `web_search_call`, which the rollout names by payload type rather than by a
# tool name. A cell of any engine can also reach the web through a spawned
# `curl`, which lands here as a shell call rather than a web one — so this
# counts the tools, not every route to the open web.
_WEB_TOOLS = frozenset(
    {"WebSearch", "WebFetch", "google_web_search", "web_fetch", "web_search_call"}
)


def is_web_tool(tool: str) -> bool:
    """Whether a call is to the open web rather than the corpus or the MCP."""
    return tool in _WEB_TOOLS


@dataclass(frozen=True)
class _PredictedCell:
    """A predicted cell's retrieval volume, keyed for the evaluation join.

    The retrieval log names its case but not its event, and an evaluation names
    the predictor but not which prediction *run* it scored. So the join is keyed
    at the grain both sides can agree on — the (event, predictor) cell, with the
    event taken from the path — and each side collapses to its latest run.

    ``mode`` comes from the log the harness wrote, not from the evaluator's
    transcription of it in the leakage block: the same fact, but one of them is
    a record and the other is a grading, and only the record is guaranteed
    present.
    """

    event_base: Path
    cell_dir: Path
    predictor_id: str
    run_id: str
    engine: str
    mode: str
    stage: str
    moment: str
    calls: int
    mcp_calls: int
    at_call_cap: bool


def _event_base(log_path: Path) -> Path | None:
    """The event directory a cell's log sits under, or ``None`` off the layout.

    Both roles nest the same distance below the event —
    ``predictions/<id>/<run>/`` and ``evaluations/<id>/<run>/`` — so one check on
    the collection directory covers them. Anything else (a flat fixture root, a
    stray copy) resolves to ``None`` and simply does not join, rather than
    guessing an event from a path that does not name one.
    """
    parents = log_path.parents
    if len(parents) > 3 and parents[2].name in ("predictions", "evaluations"):
        return parents[3]
    return None


@dataclass
class _Ledger:
    """Every counter one pass over the committed logs fills.

    The pass is one pass on purpose: the case tree dwarfs the set of cells in it,
    so each extra traversal of ``data/`` costs far more than the counting does.
    Holding the tallies together is what lets the walk stay a single loop while
    the rollup grows cuts.
    """

    logs: int = 0
    logs_without_offered: int = 0
    cells_with_mcp: int = 0
    cells_with_web: int = 0
    calls_by_tool: Counter[str] = field(default_factory=Counter)
    cells_by_tool: Counter[str] = field(default_factory=Counter)
    offered_cells: Counter[str] = field(default_factory=Counter)
    builtin_calls: Counter[str] = field(default_factory=Counter)
    pins: Counter[str] = field(default_factory=Counter)
    web_calls: Counter[str] = field(default_factory=Counter)
    web_without_mcp: Counter[str] = field(default_factory=Counter)
    result_calls: Counter[str] = field(default_factory=Counter)
    mcp_result_calls: Counter[str] = field(default_factory=Counter)
    mcp_status_calls: Counter[str] = field(default_factory=Counter)
    mcp_throttled_calls: Counter[str] = field(default_factory=Counter)
    engines_by_tool: defaultdict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    actors_by_tool: defaultdict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    null_results: defaultdict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    cells: list[ToolUsageCell] = field(default_factory=list)
    predicted: dict[tuple[Path, str], _PredictedCell] = field(default_factory=dict)

    def absorb(self, path: Path, log: RetrievalLog) -> None:
        """Count one cell's log into every tally it belongs to."""
        self.logs += 1
        # `str()`, not `.value`: the models use `use_enum_values`, so at run time
        # these fields are already the plain strings the types say are an Engine
        # and a UsageRole — a mismatch mypy cannot see, and `.value` fails on.
        engine = str(log.engine)
        for pin in log.mcp_servers:
            self.pins[pin] += 1
        if log.mcp_tools:
            for offered in log.mcp_tools:
                self.offered_cells[offered] += 1
        else:
            self.logs_without_offered += 1
        seen_here: set[str] = set()
        used_web = False
        mcp_calls = 0
        for call in log.calls:
            if call.result_digest is not None:
                self.result_calls[engine] += 1
            normalized = normalize_call(call.tool)
            if normalized is None:
                self.builtin_calls[call.tool] += 1
                if is_web_tool(call.tool):
                    self.web_calls[call.tool] += 1
                    used_web = True
                continue
            mcp_calls += 1
            self.calls_by_tool[normalized] += 1
            self.engines_by_tool[normalized][engine] += 1
            self.actors_by_tool[normalized][log.actor_id] += 1
            if call.result_digest is None:
                self.null_results[normalized][engine] += 1
            else:
                self.mcp_result_calls[engine] += 1
            self._count_condition(call, engine)
            seen_here.add(normalized)
        for normalized in seen_here:
            self.cells_by_tool[normalized] += 1
        self.cells_with_mcp += bool(seen_here)
        self.cells_with_web += used_web
        if used_web and not seen_here:
            self.web_without_mcp[engine] += 1
        base = _event_base(path)
        cell = ToolUsageCell(
            case_id=log.case_id,
            event_id=base.name if base is not None else _UNKNOWN,
            run_id=log.run_id,
            role=str(log.role),
            actor_id=log.actor_id,
            engine=engine,
            mode=log.mode or _UNKNOWN,
            calls=len(log.calls),
            mcp_calls=mcp_calls,
            cost_usd=_cell_cost(path.parent),
        )
        self.cells.append(cell)
        self._remember_predicted(path, cell)

    def _count_condition(self, call: RetrievalCall, engine: str) -> None:
        """Count one MCP call's result condition toward the engine's throttle rate.

        Counted over MCP calls alone, and denominated on the ones whose
        condition was legible rather than on every call: a builtin fetch of a
        page that happens to discuss rate limits is not this engine's manifest
        tools being starved, and an engine whose transcript captures no result
        at all must not read as one nothing ever turned away. A call with no
        condition marker — an unobserved result, or a log written before the
        marker existed — enters neither side.
        """
        if call.result_status is None or call.result_status == "unobserved":
            return
        self.mcp_status_calls[engine] += 1
        if call.result_status == "throttled":
            self.mcp_throttled_calls[engine] += 1

    def _remember_predicted(self, log_path: Path, cell: ToolUsageCell) -> None:
        """Keep this predicted cell for the usefulness join, latest run per cell.

        Re-running a predictor on an event commits a second log describing one
        forecast; entering both would put two non-independent points into a
        correlation that treats its inputs as independent. Run ids are UTC
        timestamps, so the greatest string is the newest run.
        """
        if cell.role != UsageRole.predictor:
            return
        base = _event_base(log_path)
        if base is None:
            return
        key = (base, cell.actor_id)
        previous = self.predicted.get(key)
        if previous is not None and previous.run_id >= cell.run_id:
            return
        spec = spec_for(base.name)
        self.predicted[key] = _PredictedCell(
            event_base=base,
            cell_dir=log_path.parent,
            predictor_id=cell.actor_id,
            run_id=cell.run_id,
            engine=cell.engine,
            mode=cell.mode,
            # The declared moment, not the event id's kind slug: one slug spans
            # several stages (an `order` event can be cert, interim, or merits),
            # so keying on it would pool exactly the populations this surface
            # promises to keep apart. An event the registry does not declare has
            # no population to belong to and says so.
            stage=str(spec.stage) if spec else _UNKNOWN,
            moment=str(spec.moment) if spec else _UNKNOWN,
            calls=cell.calls,
            mcp_calls=cell.mcp_calls,
            at_call_cap=cell.calls >= RETRIEVAL_CALL_CAP,
        )

    def entries(self, offered_now: list[str] | None) -> list[ToolUsageEntry]:
        """One row per tool, offered-but-never-called first, then by descending calls."""
        rows = [
            ToolUsageEntry(
                tool=tool,
                offered_cells=self.offered_cells.get(tool, 0),
                called_cells=self.cells_by_tool.get(tool, 0),
                calls=self.calls_by_tool.get(tool, 0),
                engines=dict(sorted(self.engines_by_tool[tool].items())),
                actors=dict(sorted(self.actors_by_tool[tool].items())),
                null_result_calls={
                    # Only engines with a captured result somewhere: elsewhere
                    # every call looks like a dead end because no call has a
                    # result side at all, and the rate would measure the
                    # transcript rather than the tool.
                    observed: count
                    for observed, count in sorted(self.null_results[tool].items())
                    if self.mcp_result_calls[observed]
                },
            )
            for tool in sorted(
                set(self.offered_cells) | set(self.calls_by_tool) | set(offered_now or ())
            )
        ]
        rows.sort(key=lambda e: (e.calls > 0, -e.calls, e.tool))
        return rows


def build_tool_usage(
    data_root: Path, offered_now: list[str] | None = None, *, frozen_only: bool = True
) -> ToolUsage:
    """Roll every committed ``retrieval_log.json`` into one offered-vs-called view.

    ``offered_now`` is the tool set the *current* manifest advertises. It exists
    because the per-cell ``mcp_tools`` snapshot only reaches logs written after
    that field landed: without it, a ledger of older logs reports "0 offered but
    never called" — true and useless, since a tool no cell recorded as offered is
    indistinguishable from one that does not exist. Passing the current manifest
    makes the never-called list visible immediately, at the cost of comparing
    today's advertised set against calls made under whatever was pinned then. A
    tool listed here with no calls is genuinely never-called; one absent here but
    called historically ran under an older pin.

    Deterministic: entries sort offered-then-never-called first (the actionable
    rows), then by descending calls, then by name — so a reader meets the gaps
    before the busy tools, and a rerun over an unchanged ledger reproduces the
    file byte for byte. Nothing here reads a clock; every number is a function of
    the committed ledger alone.

    ``frozen_only`` scopes the **usefulness** block alone, exactly as the boards
    scope theirs: only cells whose prediction carries a blessed process digest,
    graded at or after the freeze instant. The tool counts above it stay
    all-versions, because a count of what a cell called is a fact about the
    pipeline rather than a grade, and scoping it would hide the shakedown runs
    that are most of what there is to inspect. A Brier is a grade, so it does not
    get that latitude.

    One walk of ``data/`` does all of it. The cost join is a stat of each log's
    own directory, and the usefulness join a bounded glob under the event the
    cell's path names, so neither adds a second traversal of a ledger whose case
    tree is far larger than its set of cells.
    """
    ledger = _Ledger()
    for path in sorted(data_root.rglob("retrieval_log.json")):
        ledger.absorb(path, read_model(path, RetrievalLog))
    ledger.cells.sort(key=lambda c: (c.engine, c.actor_id, c.case_id, c.event_id, c.run_id, c.role))

    return ToolUsage(
        engine_profiles=_engine_profiles(
            ledger.cells,
            ledger.result_calls,
            ledger.mcp_result_calls,
            mcp_status_calls=ledger.mcp_status_calls,
            mcp_throttled_calls=ledger.mcp_throttled_calls,
        ),
        by_mode=_cut(ledger.cells, lambda cell: cell.mode),
        by_role=_cut(ledger.cells, lambda cell: cell.role),
        by_actor=_cut(ledger.cells, lambda cell: cell.actor_id, by_volume=True),
        cells=ledger.cells,
        usefulness=_usefulness(ledger.predicted, frozen_only=frozen_only),
        logs=ledger.logs,
        logs_without_offered_record=ledger.logs_without_offered,
        offered_now=sorted(offered_now or ()),
        pins=dict(sorted(ledger.pins.items())),
        web_calls=dict(sorted(ledger.web_calls.items(), key=lambda kv: (-kv[1], kv[0]))),
        cells_with_mcp=ledger.cells_with_mcp,
        cells_with_web=ledger.cells_with_web,
        web_without_mcp_by_engine=dict(sorted(ledger.web_without_mcp.items())),
        entries=ledger.entries(offered_now),
        builtin_calls=dict(sorted(ledger.builtin_calls.items(), key=lambda kv: (-kv[1], kv[0]))),
    )


def _cell_cost(cell_dir: Path) -> float | None:
    """The cell's estimated cost, from the ``usage.json`` beside its retrieval log.

    Missing degrades to ``None``, never to ``0.0``: a cell that committed no
    usage record is unmeasured, and averaging it in as free would pull every
    dollars-per-cell figure toward zero in proportion to how much data is
    absent. An unreadable or invalid record is treated the same way — this is a
    reporting view, and one malformed sibling must not take the whole rollup
    down.
    """
    path = cell_dir / "usage.json"
    if not path.exists():
        return None
    try:
        return read_model(path, ModelUsage).estimated_cost_usd
    except (OSError, ValueError):
        return None


def _engine_profiles(
    cells: list[ToolUsageCell],
    result_calls: Mapping[str, int],
    mcp_result_calls: Mapping[str, int],
    *,
    mcp_status_calls: Mapping[str, int],
    mcp_throttled_calls: Mapping[str, int],
) -> list[ToolUsageEngine]:
    """Per-engine result observability and cost-per-cell, engine-id ordered.

    ``result_calls`` counts calls that carried a digest, which is the only
    positive evidence of result capture the record holds. Its absence is read
    twice over: as a rate over every call, where it is honestly two-state, and as
    ``captures_results`` — gated on the **MCP** subset, since a builtin whose
    output pairs cleanly says nothing about whether the manifest tools' results
    reach the transcript, and it is the manifest tools whose dead-end rows that
    bit releases.

    The throttle rate takes ``mcp_status_calls`` as its denominator rather than
    the engine's calls, so an engine that captures no result condition at all
    lands a null instead of a 0.0 — a clean rate is a claim only a transcript
    that could have shown a throttle is entitled to make.
    """
    profiles: list[ToolUsageEngine] = []
    for engine in sorted({cell.engine for cell in cells}):
        rows = [cell for cell in cells if cell.engine == engine]
        calls = sum(cell.calls for cell in rows)
        with_result = result_calls.get(engine, 0)
        mcp_with_result = mcp_result_calls.get(engine, 0)
        with_status = mcp_status_calls.get(engine, 0)
        throttled = mcp_throttled_calls.get(engine, 0)
        costs = [cell.cost_usd for cell in rows if cell.cost_usd is not None]
        profiles.append(
            ToolUsageEngine(
                engine=engine,
                cells=len(rows),
                calls=calls,
                calls_with_result=with_result,
                result_observability_rate=round(with_result / calls, 4) if calls else None,
                mcp_calls=sum(cell.mcp_calls for cell in rows),
                mcp_calls_with_result=mcp_with_result,
                captures_results=mcp_with_result > 0,
                mcp_calls_with_status=with_status,
                # Both null together where nothing was legible: a count of
                # throttles in a transcript that could not record one is no more
                # a fact than the rate would be.
                mcp_throttled_calls=throttled if with_status else None,
                mcp_throttle_rate=round(throttled / with_status, 4) if with_status else None,
                mean_calls_per_cell=round(fmean(cell.calls for cell in rows), 3),
                median_calls_per_cell=round(median(cell.calls for cell in rows), 3),
                cells_with_cost=len(costs),
                mean_cost_usd_per_cell=round(fmean(costs), 6) if costs else None,
                median_cost_usd_per_cell=round(median(costs), 6) if costs else None,
            )
        )
    return profiles


def _cut(
    cells: list[ToolUsageCell],
    key_of: Callable[[ToolUsageCell], str],
    *,
    by_volume: bool = False,
) -> list[ToolUsageCut]:
    """Cells and calls grouped by one facet of the log, ordered for reading.

    ``by_volume`` puts the busiest group first, which is what an actor list wants;
    the small closed vocabularies (mode, role) stay in key order so a reader can
    find the row they came for and so a group that drops to zero cells still
    holds its place.
    """
    keys = sorted({key_of(cell) for cell in cells})
    cuts = [
        ToolUsageCut(
            key=key,
            cells=sum(1 for cell in cells if key_of(cell) == key),
            calls=sum(cell.calls for cell in cells if key_of(cell) == key),
            mcp_calls=sum(cell.mcp_calls for cell in cells if key_of(cell) == key),
        )
        for key in keys
    ]
    if by_volume:
        cuts.sort(key=lambda cut: (-cut.calls, cut.key))
    return cuts


@dataclass
class _JoinedCell:
    """One predicted cell beside the panel's scores of it."""

    engine: str
    mode: str
    stage: str
    moment: str
    calls: int
    mcp_calls: int
    at_call_cap: bool
    briers: list[float] = field(default_factory=list)
    evaluations: int = 0

    @property
    def segment_key(self) -> tuple[str, str, str, str]:
        """The segment this cell belongs to: engine, mode, stage, moment."""
        return (self.engine, self.mode, self.stage, self.moment)

    @property
    def population_key(self) -> tuple[str, str, str]:
        """The population a coefficient may be taken over: mode, stage, moment."""
        return (self.mode, self.stage, self.moment)


def _in_scope_prediction(cell: _PredictedCell, *, frozen_only: bool) -> bool:
    """Whether the cell's prediction carries a blessed process, when scope demands it.

    A prediction with no readable artifact leaves the join rather than passing
    it: the frozen scope is a membership filter, and a cell nothing can be
    established about is not a member.
    """
    if not frozen_only:
        return True
    path = cell.cell_dir / "prediction.json"
    if not path.exists():
        return False
    try:
        return is_frozen(read_model(path, Prediction).process_version)
    except (OSError, ValueError):
        return False


def _scores_of(cell: _PredictedCell, *, frozen_only: bool) -> _JoinedCell | None:
    """The panel's scores of one predicted cell, or ``None`` if nobody scored it.

    A bounded glob under the cell's own event, not a second walk of the ledger.
    Each judge contributes its latest grading of the cell
    (:func:`~fedcourtsai.integrity.latest_evaluation_runs`, the same collapse
    every aggregate of this ledger uses): a re-grade describes the same
    observation, so counting both would weight one judge twice. Under the frozen
    scope a grading stamped before the freeze instant is not in the panel at all.
    """
    found: list[Evaluation] = []
    pattern = f"*/{cell.predictor_id}/*/evaluation.json"
    for path in sorted((cell.event_base / "evaluations").glob(pattern)):
        try:
            evaluation = read_model(path, Evaluation)
        except (OSError, ValueError):
            # One unreadable grading costs the cell that judge, not the run: this
            # is a reporting view over a ledger it does not own, and `validate` is
            # what fails loudly on a malformed artifact.
            continue
        if frozen_only and not graded_post_freeze(evaluation.process_version):
            continue
        found.append(evaluation)
    panel = latest_evaluation_runs(found, lambda evaluation: evaluation)
    if not panel:
        return None
    return _JoinedCell(
        engine=cell.engine,
        mode=cell.mode,
        stage=cell.stage,
        moment=cell.moment,
        calls=cell.calls,
        mcp_calls=cell.mcp_calls,
        at_call_cap=cell.at_call_cap,
        briers=[e.brier_score for e in panel if e.brier_score is not None],
        evaluations=len(panel),
    )


def _usefulness(
    predicted: Mapping[tuple[Path, str], _PredictedCell], *, frozen_only: bool
) -> ToolUsefulness:
    """Call volume against Brier, with the floor that decides whether to publish.

    Joins each in-scope predicted cell to the gradings of it, collapses the panel
    to one Brier per cell, and segments by engine, mode, and forecast moment with
    the cell count beside every mean. A coefficient is computed per (mode, event
    kind) population and only above :data:`TOOL_USAGE_CORRELATION_MIN_CELLS`;
    below it the value stays null and ``withheld_reason`` says why, so no
    downstream reader can quote a number the floor refused.

    Three groupings that could each have been one number, and are not. Modes are
    separate because a replay cell's grade is not claimable performance and can
    never share a population with a forward cell's. Forecast moments are separate
    because a cert Brier and a merits Brier score different questions against
    different base rates. Engines are pooled *within* a row and split across the
    segment table, so the confound is visible in the denominators even where the
    coefficient absorbs it.
    """
    joined: list[_JoinedCell] = []
    for cell in sorted(predicted.values(), key=lambda c: (c.engine, c.predictor_id, c.run_id)):
        if not _in_scope_prediction(cell, frozen_only=frozen_only):
            continue
        scores = _scores_of(cell, frozen_only=frozen_only)
        if scores is None or not scores.briers:
            continue
        joined.append(scores)

    segments = [
        ToolUsefulnessSegment(
            engine=key[0],
            mode=key[1],
            stage=key[2],
            moment=key[3],
            cells=len(group),
            evaluations=sum(cell.evaluations for cell in group),
            brier_gradings=sum(len(cell.briers) for cell in group),
            mean_calls=round(fmean(cell.calls for cell in group), 3),
            mean_mcp_calls=round(fmean(cell.mcp_calls for cell in group), 3),
            mean_brier_score=round(fmean(fmean(cell.briers) for cell in group), 6),
        )
        for key, group in _grouped(joined, lambda cell: cell.segment_key)
    ]
    correlations = [
        _correlate(key, group) for key, group in _grouped(joined, lambda cell: cell.population_key)
    ]
    return ToolUsefulness(
        process_scope="frozen" if frozen_only else "all",
        min_cells_for_correlation=TOOL_USAGE_CORRELATION_MIN_CELLS,
        predicted_cells=len(predicted),
        joined_cells=len(joined),
        joined_evaluations=sum(cell.evaluations for cell in joined),
        brier_gradings=sum(len(cell.briers) for cell in joined),
        cells_at_call_cap=sum(1 for cell in joined if cell.at_call_cap),
        segments=segments,
        correlations=correlations,
    )


def _correlate(
    population: tuple[str, str, str], group: list[_JoinedCell]
) -> ToolUsefulnessCorrelation:
    """One population's coefficient, or the refusal and the reason for it."""
    mode, stage, moment = population
    points = [(float(cell.calls), fmean(cell.briers)) for cell in group]
    tau = kendall_tau_b(points) if len(points) >= TOOL_USAGE_CORRELATION_MIN_CELLS else None
    reason: str | None = None
    if tau is None and len(points) < TOOL_USAGE_CORRELATION_MIN_CELLS:
        reason = (
            f"{len(points)} joined cell(s), below the pre-declared floor of "
            f"{TOOL_USAGE_CORRELATION_MIN_CELLS} — a coefficient over them would be noise "
            "reading as a finding"
        )
    elif tau is None:
        reason = (
            "undefined: every pair of these cells ties on call volume or on Brier, so a "
            "rank correlation has no denominator"
        )
    return ToolUsefulnessCorrelation(
        mode=mode,
        stage=stage,
        moment=moment,
        cells=len(points),
        published=tau is not None,
        calls_brier_tau=round(tau, 4) if tau is not None else None,
        withheld_reason=reason,
    )


def _grouped[K: tuple[str, ...]](
    joined: list[_JoinedCell], key_of: Callable[[_JoinedCell], K]
) -> list[tuple[K, list[_JoinedCell]]]:
    """The joined cells grouped by a tuple key, in key order."""
    grouped: defaultdict[K, list[_JoinedCell]] = defaultdict(list)
    for cell in joined:
        grouped[key_of(cell)].append(cell)
    return [(key, grouped[key]) for key in sorted(grouped)]


def render_tool_usage_markdown(usage: ToolUsage) -> str:
    """A short human-readable rollup — the shape the run summary carries."""
    lines = ["# Tool usage — offered vs called", ""]
    if usage.logs == 0:
        lines.append("_No retrieval logs committed yet._")
        return "\n".join(lines) + "\n"

    never = [e for e in usage.entries if e.calls == 0]
    lines += [
        f"**{usage.logs}** cell log(s). **{len(usage.entries)}** MCP tool(s) seen "
        f"offered or called; **{len(never)}** never called.",
        "",
    ]
    by_tool = {e.tool: e.calls for e in usage.entries}
    if usage.offered_now:
        called_now = sum(1 for t in usage.offered_now if by_tool.get(t))
        lines += [
            f"_The current manifest advertises **{len(usage.offered_now)}** tool(s); "
            f"**{called_now}** of them have ever been called._",
            "",
        ]
    if usage.logs_without_offered_record:
        pins = ", ".join(f"`{pin}` ({n})" for pin, n in usage.pins.items()) or "an unnamed pin"
        lines += [
            f"_{usage.logs_without_offered_record} log(s) predate the offered-tools "
            "record, so their own denominator is unknown — the `offered in` column reads "
            "`—` for them. Those cells ran under " + pins + ", while the offered set above "
            "is what the manifest pins **now**: a tool listed with no calls is genuinely "
            "never-called, and one called but not listed ran under an older pin._",
            "",
        ]
    lines += [
        "| tool | offered in | called in | calls | engines |",
        "| --- | --: | --: | --: | --- |",
    ]
    for entry in usage.entries:
        engines = ", ".join(f"{k} {v}" for k, v in entry.engines.items()) or "—"
        # `—`, not `0`: no cell recorded this tool as offered, which on a ledger
        # of pre-`mcp_tools` logs means unknown. Printing 0 beside a headline
        # that counts it as offered-but-never-called reads as a contradiction.
        offered = str(entry.offered_cells) if entry.offered_cells else "—"
        lines.append(
            f"| {entry.tool} | {offered} | {entry.called_cells} | {entry.calls} | {engines} |"
        )
    lines += [
        "",
        "_A zero means **never called**, not useless: a tool can go unused because "
        + "the prompt never mentions it or a sandbox blocked it, and this data cannot "
        + "tell those apart. Read the offered count beside it — unused in 3 cells is "
        + "not unused in 400 — and check the cause before retiring anything._",
    ]
    if usage.cells_with_web or usage.cells_with_mcp:
        web = ", ".join(f"`{name}` {count}" for name, count in usage.web_calls.items()) or "none"
        lines += [
            "",
            "## Open web vs the MCP",
            "",
            f"**{usage.cells_with_mcp}** cell(s) called an MCP tool; "
            f"**{usage.cells_with_web}** reached the open web ({web}).",
        ]
        if usage.web_without_mcp_by_engine:
            per_engine = ", ".join(
                f"{engine} {count}" for engine, count in usage.web_without_mcp_by_engine.items()
            )
            total = sum(usage.web_without_mcp_by_engine.values())
            lines += [
                "",
                f"**{total}** cell(s) searched the web without calling the MCP at all "
                f"({per_engine}) — the substitution signal, and the place to look for a "
                "gap or a failure in the MCP surface.",
            ]
        lines += [
            "",
            "_Suggestive, not proof. A forward cell is explicitly allowed to use public "
            + "context the corpus does not carry, so web use is sanctioned rather than a "
            + "fault; what it flags is a cell that needed something and did not get it from "
            + "the configured tools. Each engine is counted under its own tool names, so a "
            + "zero is not by itself evidence that a cell chose not to search — check the "
            + "retrieval surface its process version records._",
        ]
    if usage.builtin_calls:
        shown = list(usage.builtin_calls.items())[:10]
        rows = ", ".join(f"`{name}` {count}" for name, count in shown)
        lines += [
            "",
            f"**Engine built-ins** (not manifest tools, counted separately): {rows}. "
            + "A code-mode engine's counts nest rather than add up: the freeform builtin "
            + "that carries a program is one call, and the builtins that program invokes "
            + "are lifted into calls of their own, so both appear here.",
        ]
    lines += _render_observability(usage)
    lines += _render_dead_ends(usage)
    lines += _render_cuts(usage)
    lines += _render_cost(usage)
    lines += _render_usefulness(usage)
    return "\n".join(lines) + "\n"


def _rate(value: float | None) -> str:
    """A rate as a percentage, or an em dash where it is undefined."""
    return "—" if value is None else f"{value * 100:.1f}%"


def _usd(value: float | None) -> str:
    """A dollar figure, or an em dash where no cell carried one."""
    return "—" if value is None else f"${value:.4f}"


def _render_observability(usage: ToolUsage) -> list[str]:
    """Per engine, how often the result side of a call was captured at all."""
    if not usage.engine_profiles:
        return []
    lines = [
        "",
        "## Result observability",
        "",
        "| engine | cells | calls | with result | observability | MCP with result |",
        "| --- | --: | --: | --: | --: | --: |",
    ]
    for profile in usage.engine_profiles:
        # The flag rides in the cell, not only in the paragraph below: a table row
        # is what gets copied out of a run summary, and `0.0%` alone reads as an
        # engine whose every call came back empty.
        rate = _rate(profile.result_observability_rate)
        if profile.calls and not profile.captures_results:
            # An engine can score well on this rate off builtin output alone while
            # none of its MCP results reach the transcript, so the flag has to name
            # which capture is missing rather than read as a flat zero.
            rate = f"{_rate(profile.result_observability_rate)} (no MCP result capture)"
        lines.append(
            f"| {profile.engine} | {profile.cells} | {profile.calls} | "
            f"{profile.calls_with_result} | {rate} | {profile.mcp_calls_with_result} |"
        )
    blind = [p.engine for p in usage.engine_profiles if p.calls and not p.captures_results]
    lines += [
        "",
        "_Two states, not three. A captured result digest proves the result side was "
        + "recorded and non-empty; a null covers an empty result **and** a result the "
        + "transcript never carried. The per-call `result_capture` marker separates "
        + "those two, but only the logs captured since it existed carry it; on the rest "
        + "it reads null. So this "
        + "column is a floor on how much of the answer side is observable, not a hit rate. "
        + "Its denominator is every call, builtins included — the MCP column beside it is "
        + "the one that speaks to the manifest tools. For a code-mode engine that "
        + "denominator also gains one row per call lifted from a freeform call's source — "
        + "the engine's own builtins, which is where such a program does most of its work, "
        + "as much as the manifest tools — each unobserved by construction, so its rate "
        + "falls for a reason of call shape rather than of capture quality. Which idioms "
        + "the lift matched decides how many rows a program left, and rows are written "
        + "once at parse time, so a code-mode engine's row here pools logs minted under "
        + "whatever lift each was captured with: a move across runs may be a capture "
        + "change rather than a behavioural one._",
    ]
    if blind:
        lines += [
            "",
            f"**{', '.join(blind)}**: not one **MCP** call in the whole ledger carried a "
            + "result digest. Read that as a capture gap in the engine's transcript rather "
            + "than as an engine whose every call came back empty — and note what it costs "
            + "downstream: the leakage grading reads results, so those cells are graded on "
            + "queries alone.",
        ]
    return lines + _render_throttling(usage)


def _throttle_cell(profile: ToolUsageEngine) -> str:
    """One engine's throttle figure, carrying its own reason for being empty.

    Three distinguishable states, each said in the cell rather than in a note
    below it, because the number is what gets copied out of a report: a real
    ratio, *capture-blind* (MCP calls were made and no result condition came
    back), and *no MCP calls in the ledger* (nothing to be throttled). A bare
    ``0/0 (—)`` collapses the last two into each other and reads as neither.

    The last is scoped to the ledger on purpose. It is a statement about what
    capture recorded, and capture reads what an engine's transcript exposes: a
    code-mode engine invokes its manifest tools from inside a freeform builtin
    call, and rows for those invocations exist only where capture lifted them
    out of that call's source. A log carrying no such row is one capture never
    minted them for — a null ``RetrievalCall.call_source`` is what that reads
    like in the data — so an engine can show empty here over a stretch of the
    ledger in which it was retrieving.
    """
    if profile.mcp_calls_with_status:
        return (
            f"`{profile.engine}` {profile.mcp_throttled_calls}/{profile.mcp_calls_with_status} "
            f"({_rate(profile.mcp_throttle_rate)})"
        )
    if profile.mcp_calls:
        return f"`{profile.engine}` — (capture-blind)"
    return f"`{profile.engine}` — (no MCP calls in the ledger)"


def _render_throttling(usage: ToolUsage) -> list[str]:
    """How often the upstream quota turned an MCP call away, per engine.

    Rendered whenever there are engines to report, zeros included: the reader
    of a retrieval count needs to know a throttle was looked for and not found,
    which a line that appears only on bad news cannot tell them. Every reason a
    figure is empty is named in the figure itself (:func:`_throttle_cell`) —
    an em dash in a row of rates is exactly the shape a reader rounds to zero.
    """
    if not usage.engine_profiles:
        return []
    rows = ", ".join(_throttle_cell(profile) for profile in usage.engine_profiles)
    lines = [
        "",
        "## Upstream throttling",
        "",
        "Throttled MCP results, over the manifest-tool calls whose result condition was "
        + f"legible: {rows}.",
        "",
        "_A throttled call is the shared daily quota turning the cell away — it retrieved "
        + "nothing, so a starved cell's coverage is not comparable with a well-fed one's. "
        + "Every count here is a **floor**: the parse-time predicate is anchored on the "
        + "server's own rate-limit phrasing and biased to miss a throttle rather than "
        + "invent one, it is read only from manifest-tool results (a builtin echoing prose "
        + "about rate limits is not this cell being refused), and calls the cell gave up on "
        + "making are not in the ledger at all._",
        "",
        "_**The per-engine cut is descriptive, not a comparison.** The quota is one bucket "
        + "every cell of a run draws from, so which engine's cells meet the wall is a fact "
        + "about ordering and concurrency within the run — who called first, who was still "
        + "running when the budget ran out — not about the engine. Read a row as *these "
        + "cells were unlucky*; do not rank engines on it, difference two of them, or carry "
        + "a rate into any cross-engine claim._",
    ]
    blind = [p.engine for p in usage.engine_profiles if p.mcp_calls and not p.mcp_calls_with_status]
    if blind:
        lines += [
            "",
            f"**{', '.join(blind)}**: made MCP calls and not one of their result conditions "
            + "was legible, so there is no denominator and the figure is an em dash rather "
            + "than 0%. Read that as **capture-blind, not throttle-free** — Gemini's "
            + "telemetry logs no result payload by construction, and a log written before "
            + "the per-call condition marker existed carries none either. A code-mode "
            + "engine reaching its manifest tools from inside a freeform builtin call is a "
            + "third way to land here: only the program's combined output is captured, and "
            + "no part of it is attributable to an individual call inside the program, so "
            + "every such row is unobserved by construction. These engines cannot be "
            + "observed being starved, so "
            + "they cannot supply evidence that they were not. An engine marked *no MCP "
            + "calls in the ledger* is a different thing again: no such call was recorded "
            + "for it, so nothing in the ledger could have been throttled.",
        ]
    return lines


def _render_dead_ends(usage: ToolUsage) -> list[str]:
    """Per tool per engine, the share of calls that came back with nothing."""
    rows = [
        (entry.tool, engine, entry.engines.get(engine, 0), nulls)
        for entry in usage.entries
        for engine, nulls in entry.null_result_calls.items()
        if nulls
    ]
    if not rows:
        return []
    rows.sort(key=lambda row: (-row[3], row[0], row[1]))
    lines = [
        "",
        "## Calls with no captured result",
        "",
        "| tool | engine | calls | no result | rate |",
        "| --- | --- | --: | --: | --: |",
    ]
    for tool, engine, calls, nulls in rows:
        lines.append(f"| {tool} | {engine} | {calls} | {nulls} | {_rate(nulls / calls)} |")
    lines += [
        "",
        "_An **upper bound** on the dead-end rate, and only for engines whose transcripts "
        + "carry results at all — elsewhere the row is withheld, because an engine that "
        + "captures no result would otherwise read as 100% dead ends. Even here a null "
        + "digest may be a result the transcript failed to pair to its call rather than a "
        + "query that found nothing._",
    ]
    return lines


def _render_cuts(usage: ToolUsage) -> list[str]:
    """The mode, role, and actor cuts, each as a small table."""
    sections = (
        ("Mode", usage.by_mode, "mode"),
        ("Role", usage.by_role, "role"),
        ("Actor", usage.by_actor, "actor"),
    )
    lines: list[str] = []
    for title, cuts, column in sections:
        if not cuts:
            continue
        lines += [
            "",
            f"## {title}",
            "",
            f"| {column} | cells | calls | of which MCP |",
            "| --- | --: | --: | --: |",
        ]
        lines += [f"| {cut.key} | {cut.cells} | {cut.calls} | {cut.mcp_calls} |" for cut in cuts]
        if column == "mode" and len(cuts) == 1:
            lines += [
                "",
                f"_Every cell in the ledger is `{cuts[0].key}`, so the mode cut compares "
                + "nothing yet. It is computed anyway: the moment replay cells land, the "
                + "forward/replay difference in retrieval behaviour is the first thing to "
                + "look at._",
            ]
    return lines


def _render_cost(usage: ToolUsage) -> list[str]:
    """Calls per cell beside dollars per cell, and the scatter behind the means."""
    if not usage.engine_profiles:
        return []
    lines = [
        "",
        "## Cost vs retrieval",
        "",
        "| engine | cells | calls/cell (mean) | (median) | costed cells | $/cell (mean) "
        + "| (median) |",
        "| --- | --: | --: | --: | --: | --: | --: |",
    ]
    for profile in usage.engine_profiles:
        lines.append(
            f"| {profile.engine} | {profile.cells} | {profile.mean_calls_per_cell} | "
            f"{profile.median_calls_per_cell} | {profile.cells_with_cost} | "
            f"{_usd(profile.mean_cost_usd_per_cell)} | {_usd(profile.median_cost_usd_per_cell)} |"
        )
    uncosted = sum(p.cells - p.cells_with_cost for p in usage.engine_profiles)
    lines += [
        "",
        "_Cost is the **whole cell's** model spend estimated from published rates — not a "
        + "billed figure, and not retrieval's share of it, so a cell is not expensive "
        + "*because* it called tools. The dollars-per-cell denominator is **costed cells**, "
        + "not cells: a cell that "
        + "committed no usage record is unmeasured, never free. Read the median beside the "
        + "mean — one runaway cell moves the mean and not the median._",
    ]
    if uncosted:
        lines += [
            "",
            f"**{uncosted}** cell(s) have a retrieval log and no `usage.json` beside it, so "
            + "they contribute calls but no cost.",
        ]
    if usage.cells and len(usage.cells) <= _SCATTER_ROWS_MAX:
        lines += [
            "",
            "| cell | engine | mode | calls | MCP | cost |",
            "| --- | --- | --- | --: | --: | --: |",
        ]
        lines += [
            f"| {cell.case_id} {cell.event_id} {cell.actor_id} | {cell.engine} | {cell.mode} "
            f"| {cell.calls} | {cell.mcp_calls} | {_usd(cell.cost_usd)} |"
            for cell in usage.cells
        ]
    elif usage.cells:
        lines += [
            "",
            f"_{len(usage.cells)} cells — past the {_SCATTER_ROWS_MAX} the summary prints "
            + "inline. The per-cell rows are in the JSON artifact._",
        ]
    return lines


def _render_usefulness(usage: ToolUsage) -> list[str]:
    """The call-volume-vs-Brier denominators, and the refusal to correlate them."""
    useful = usage.usefulness
    if useful is None:
        return []
    scope = (
        "blessed processes only"
        if useful.process_scope == "frozen"
        else "**every process version, shakedown cells included**"
    )
    lines = [
        "",
        "## Does retrieval buy accuracy?",
        "",
        f"_Process scope: **{useful.process_scope}** ({scope}). "
        + f"**{useful.joined_cells}** of **{useful.predicted_cells}** predicted cell(s) join "
        + "a grading that recorded a Brier._",
        "",
    ]
    if not useful.segments:
        lines.append(
            "_Nothing joins in this scope, so there is nothing to compare. That is a "
            "statement about the ledger, not about retrieval: a cell joins once a blessed "
            "prediction and a Brier-bearing grading of it sit beside a committed retrieval "
            "log._"
        )
        return lines
    lines += [
        "| engine | mode | stage | moment | cells (n) | Brier gradings | mean calls "
        + "| of which MCP | mean Brier |",
        "| --- | --- | --- | --- | --: | --: | --: | --: | --: |",
    ]
    for segment in useful.segments:
        brier = "—" if segment.mean_brier_score is None else f"{segment.mean_brier_score:.4f}"
        lines.append(
            f"| {segment.engine} | {segment.mode} | {segment.stage} | {segment.moment} "
            f"| {segment.cells} | {segment.brier_gradings} | {segment.mean_calls} "
            f"| {segment.mean_mcp_calls} | {brier} |"
        )
    lines += ["", *_render_correlations(useful)]
    lines += [
        "",
        "_Cells, not gradings, are the unit: several judges score one prediction, so "
        + f"the **{useful.joined_cells}** cell(s) here carry **{useful.joined_evaluations}** "
        + f"grading(s), of which **{useful.brier_gradings}** recorded a Brier, collapsed to "
        + "one Brier per cell. Counting the gradings would inflate the n with observations "
        + "that are not independent._",
    ]
    if useful.cells_at_call_cap:
        lines += [
            "",
            f"_**{useful.cells_at_call_cap}** cell(s) hit the per-log call cap of "
            + f"{RETRIEVAL_CALL_CAP}, so their call volume is right-censored: the top of "
            + "the x axis is compressed, and any coefficient understates the spread it was "
            + "taken over._",
        ]
    lines += [
        "",
        "_An ops view, not a scored board. It shares the boards' process scope and their "
        + "one-grading-per-judge collapse, but it applies neither the forward-claim nor "
        + "the leakage exclusion, and it keys `mode` on the harness's own record rather "
        + "than on the "
        + "derived stratum — so this population is a superset of the leaderboard's, and a "
        + "figure here that differs from a board figure is two populations rather than an "
        + "error in either. The leakage half has a direction worth naming: a cell that "
        + "read its outcome out of its snapshot scores a near-zero Brier having made few "
        + "calls, which pushes the calls-against-Brier coefficient toward 'retrieval "
        + "does not help'._",
    ]
    return lines


def _render_correlations(useful: ToolUsefulness) -> list[str]:
    """Each population's coefficient, or the under-powered verdict standing in for it."""
    # The pre-registration sentence rides both branches. The mixed state — one
    # population published, the rest withheld — is the likely steady state, and
    # it is exactly where a reader needs to be told the floor was declared ahead
    # of the numbers rather than fitted to them.
    floor = (
        "The floor is declared in code ahead of any coefficient "
        f"(`TOOL_USAGE_CORRELATION_MIN_CELLS = {useful.min_cells_for_correlation}`), not "
        "chosen once the numbers were in view, and it is applied per population rather "
        "than to a pooled total — pooling forward with replay cells, or cert with merits, "
        "would blend populations whose grades are not comparable into the one number a "
        "reader would quote."
    )
    published = [c for c in useful.correlations if c.published and c.calls_brier_tau is not None]
    if not published:
        counts = ", ".join(
            f"{c.mode}/{c.stage}/{c.moment} n={c.cells}" for c in useful.correlations
        )
        return [
            "**Under-powered — no correlation published.** No population clears the floor "
            + f"({counts}). {floor} What is above is a denominator table: read the `n` "
            + "beside every mean, and read no relationship between calls and Brier out of it."
        ]
    lines = ["| population | cells (n) | tau-b (calls vs Brier) |", "| --- | --: | --: |"]
    for row in useful.correlations:
        tau = "withheld" if row.calls_brier_tau is None else f"{row.calls_brier_tau:+.3f}"
        lines.append(f"| {row.mode} / {row.stage} / {row.moment} | {row.cells} | {tau} |")
    lines += [
        "",
        f"_{floor}_",
        "",
        "_Brier is a **loss**, so a NEGATIVE tau is the one that would mean more calls "
        + "beside better forecasts. Descriptive, never causal, and never pooled across "
        + "populations: within a row the engines are pooled, so the coefficient carries "
        + "every difference between them — prompt, model, sandbox — and a cell calls more "
        + "tools partly *because* its case is hard._",
        "",
        "_The call axis is the row count, and that unit is **not uniform across engines "
        + "or across the ledger**. A code-mode engine's cell carries its freeform builtin "
        + "call plus one row per call lifted from that call's source — the builtins such "
        + "a program leans on as much as the manifest tools, and the builtin term is the "
        + "larger by far — so its "
        + "count sits higher than a direct-calling engine's for the same retrieval, and "
        + "higher again than a cell of its own captured under a narrower lift. Engines are pooled "
        + "within a row, so read a coefficient over a population spanning both shapes as "
        + "carrying that mixture, not only the tool use it is meant to measure._",
    ]
    return lines
