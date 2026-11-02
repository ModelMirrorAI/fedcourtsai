"""Model spend from runs that commit nothing to the ledger, recorded and reported apart.

The measured spend total (:func:`fedcourtsai.spend.measured_spend`) reads what
reaches ``data/``: cell ``usage.json``, case-summary front matter and the topic
labeler's run records. Integration smokes, the promotion gate, staging
rehearsals and the replay and pilot rounds spend real tokens and commit none of
that, so their spend is recorded here instead, one :class:`OffLedgerSpend`
record per leg:

1. **Record.** The leg runs ``fedcourts off-ledger-spend`` over its engine logs
   (:func:`spend_lines`) and uploads the record as an ``off-ledger-spend-*``
   run artifact. Nothing in the leg needs a write credential.
2. **Sweep.** The daily ``run-ops`` job downloads those artifacts and keeps
   each record that validates and names the run it came from
   (:func:`ingest`) under ``off-ledger-spend/`` on the ``ops-metrics`` branch,
   so a record outlives its runner and its artifact's retention.
3. **Report.** ``fedcourts off-ledger-spend-report`` renders the stored
   records by week and month, split by environment and lane, with the
   promotion gate's cost per candidate (:func:`summarize`,
   :func:`render_report`).

The figure is reported separately and counted nowhere: no reader of the spend
backstop or the auto-release budget reads these records, so test traffic never
holds back a production round. The promotion gate keeps its own bound, the
train's per-day dispatch cap.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .pricing import DEFAULT_MODELS, MODEL_RATES, TokenCounts, estimate_cost_usd
from .schemas import Engine, OffLedgerSpend, OffLedgerSpendLine
from .serialize import read_model, write_json
from .store import iter_usage
from .summaries import parse_summary
from .usage import (
    parse_claude_served_models,
    parse_claude_transcripts_usage,
    parse_claude_usage,
    parse_codex_usage_all,
    parse_gemini_served_models,
    parse_gemini_usage,
)

#: The directory, on the ``ops-metrics`` branch, the sweep keeps records in.
STORE_DIR = "off-ledger-spend"
#: The run-artifact name prefix a leg uploads its record under.
ARTIFACT_PREFIX = "off-ledger-spend-"


def record_filename(run_id: str, run_attempt: int, leg: str) -> str:
    """The canonical file name of one leg's record."""
    return f"{run_id}-{run_attempt}-{leg}.json"


def _price(model: str, counts: TokenCounts) -> tuple[float, str | None]:
    """The cost of ``counts`` at ``model``'s rate, or at the dearest rate if it has none.

    An unpriced model is never dropped and never under-counted: it is priced at
    the entry that prices these exact counts dearest, which is named back.
    """
    if model in MODEL_RATES:
        return estimate_cost_usd(model, counts), None
    # A served id can carry a release date the rate table's alias omits
    # (`claude-haiku-4-5-20251001`); the alias's rate is that model's rate.
    undated = re.sub(r"-\d{8}$", "", model)
    if undated in MODEL_RATES:
        return estimate_cost_usd(undated, counts), undated
    dearest = max(sorted(MODEL_RATES), key=lambda known: estimate_cost_usd(known, counts))
    return estimate_cost_usd(dearest, counts), dearest


def _log_line(source: str, engine: Engine, model: str, counts: TokenCounts) -> OffLedgerSpendLine:
    cost, priced_as = _price(model, counts)
    return OffLedgerSpendLine.model_validate(
        {
            "source": source,
            "engine": engine,
            "model": model,
            "priced_as": priced_as,
            "input_tokens": counts.input_tokens,
            "output_tokens": counts.output_tokens,
            "cache_read_input_tokens": counts.cache_read_input_tokens,
            "cache_creation_input_tokens": counts.cache_creation_input_tokens,
            "estimated_cost_usd": cost,
        }
    )


def _model_for(engine: Engine, explicit: str | None, served: list[str] | None) -> str:
    """The model a log is priced at: the caller's, else the first served, else the default."""
    if explicit:
        return explicit
    if served:
        return served[0]
    return DEFAULT_MODELS[engine.value]


@dataclass
class _Group:
    records: int = 0
    counts: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    cost: float = 0.0


def _grouped_line(
    source: str, engine: Engine | None, model: str, group: _Group
) -> OffLedgerSpendLine:
    return OffLedgerSpendLine.model_validate(
        {
            "source": source,
            "engine": engine,
            "model": model,
            "records": group.records,
            "input_tokens": group.counts[0],
            "output_tokens": group.counts[1],
            "cache_read_input_tokens": group.counts[2],
            "cache_creation_input_tokens": group.counts[3],
            "estimated_cost_usd": group.cost,
        }
    )


def _cell_usage_lines(data_root: Path) -> list[OffLedgerSpendLine]:
    """One line per (engine, model) over the ``usage.json`` records under ``data_root``.

    Each record was priced when its cell wrote it, so its cost is carried, not
    re-priced: the line says what the cells' own records say they cost.
    """
    groups: dict[tuple[Engine, str], _Group] = defaultdict(_Group)
    for usage in iter_usage(data_root):
        group = groups[(usage.engine, usage.model)]
        group.records += 1
        group.counts[0] += usage.input_tokens
        group.counts[1] += usage.output_tokens
        group.counts[2] += usage.cache_read_input_tokens
        group.counts[3] += usage.cache_creation_input_tokens
        group.cost += usage.estimated_cost_usd
    return [
        _grouped_line("cell-usage", engine, model, group)
        for (engine, model), group in sorted(groups.items())
    ]


def _summary_lines(data_root: Path) -> list[OffLedgerSpendLine]:
    """One line per model over the case summaries under ``data_root`` that carry usage."""
    groups: dict[str, _Group] = defaultdict(_Group)
    for path in sorted((data_root / "cases").glob("*/*/summaries/*.md")):
        front, _ = parse_summary(path.read_text(encoding="utf-8"))
        if front.usage is None:
            continue
        group = groups[front.model]
        group.records += 1
        group.counts[0] += front.usage.input_tokens
        group.counts[1] += front.usage.output_tokens
        group.cost += front.usage.estimated_cost_usd
    return [
        _grouped_line("case-summaries", None, model, group)
        for model, group in sorted(groups.items())
    ]


def spend_lines(  # noqa: PLR0913 - one keyword per source a leg may hold
    *,
    claude_execution_file: Path | None = None,
    claude_transcripts_dir: Path | None = None,
    codex_sessions_dir: Path | None = None,
    gemini_telemetry_file: Path | None = None,
    cell_usage_root: Path | None = None,
    case_summaries_root: Path | None = None,
    claude_model: str | None = None,
    codex_model: str | None = None,
    gemini_model: str | None = None,
) -> list[OffLedgerSpendLine]:
    """Every line of spend the given sources hold; a source with no usage adds none.

    Each engine log is read by the parser its cells' ``record-usage`` uses, and
    priced at the model the caller names, else the first model the log says
    served it, else the engine's default; the whole log is priced at that one
    model, a Gemini log's utility calls on helper models included, which errs
    high wherever the main model is the dearer. The Claude CLI transcripts
    carry the model on every response, so they are priced per model as served.
    """
    lines: list[OffLedgerSpendLine] = []
    if claude_execution_file is not None:
        counts = parse_claude_usage(claude_execution_file)
        if counts is not None and counts.total_tokens > 0:
            model = _model_for(
                Engine.claude_code,
                claude_model,
                parse_claude_served_models(claude_execution_file),
            )
            lines.append(_log_line("claude-execution-file", Engine.claude_code, model, counts))
    if claude_transcripts_dir is not None:
        for model, counts in (parse_claude_transcripts_usage(claude_transcripts_dir) or {}).items():
            lines.append(_log_line("claude-transcripts", Engine.claude_code, model, counts))
    if codex_sessions_dir is not None:
        counts = parse_codex_usage_all(codex_sessions_dir)
        if counts is not None and counts.total_tokens > 0:
            model = _model_for(Engine.codex, codex_model, None)
            lines.append(_log_line("codex-sessions", Engine.codex, model, counts))
    if gemini_telemetry_file is not None:
        counts = parse_gemini_usage(gemini_telemetry_file)
        if counts is not None and counts.total_tokens > 0:
            model = _model_for(
                Engine.gemini, gemini_model, parse_gemini_served_models(gemini_telemetry_file)
            )
            lines.append(_log_line("gemini-telemetry", Engine.gemini, model, counts))
    if cell_usage_root is not None:
        lines.extend(_cell_usage_lines(cell_usage_root))
    if case_summaries_root is not None:
        lines.extend(_summary_lines(case_summaries_root))
    return lines


# --- Sweep -------------------------------------------------------------------


@dataclass(frozen=True)
class IngestResult:
    """What one artifact's sweep kept, already held, and refused (with the reason)."""

    stored: list[str]
    unchanged: list[str]
    refused: list[tuple[str, str]]


def ingest(source: Path, *, run_id: str, workflow: str, ref: str, store: Path) -> IngestResult:
    """Keep each record under ``source`` that validates and names its own run.

    ``source`` is one downloaded ``off-ledger-spend-*`` artifact; ``run_id``,
    ``workflow`` and ``ref`` are what the Actions API says of the run that
    uploaded it (its id, its workflow file's stem, its head branch). A record
    that names another run, another workflow or another branch is refused, so
    one run's artifact cannot write another run's figure, and a run that is
    not the workflow it claims cannot pass as one. A record is immutable once
    kept (an attempt's leg spends once), so one already held unchanged is
    skipped, and one that differs from the held copy is refused rather than
    overwriting it.
    """
    stored: list[str] = []
    unchanged: list[str] = []
    refused: list[tuple[str, str]] = []
    for path in sorted(source.rglob("*.json")):
        try:
            record = read_model(path, OffLedgerSpend)
        except (OSError, ValueError) as exc:
            refused.append((path.name, f"does not validate: {exc}"))
            continue
        if record.run_id != run_id:
            refused.append((path.name, f"names run {record.run_id}, not {run_id}"))
            continue
        if record.workflow != workflow or record.ref != ref:
            refused.append(
                (
                    path.name,
                    f"names {record.workflow} on {record.ref}, but the run is {workflow} on {ref}",
                )
            )
            continue
        name = record_filename(record.run_id, record.run_attempt, record.leg)
        destination = store / name
        if destination.exists():
            try:
                held = read_model(destination, OffLedgerSpend)
            except (OSError, ValueError):
                held = None
            if held == record:
                unchanged.append(name)
            else:
                refused.append((name, "differs from the record already kept"))
            continue
        write_json(destination, record)
        stored.append(name)
    return IngestResult(stored=stored, unchanged=unchanged, refused=refused)


def read_store(store: Path) -> list[OffLedgerSpend]:
    """Every kept record, in file order; one that will not validate raises."""
    if not store.is_dir():
        return []
    return [read_model(path, OffLedgerSpend) for path in sorted(store.glob("*.json"))]


# --- Report ------------------------------------------------------------------


def _aware(moment: datetime) -> datetime:
    return moment if moment.tzinfo is not None else moment.replace(tzinfo=UTC)


@dataclass(frozen=True)
class WindowSpend:
    """Spend over one window, split by environment and by lane and environment."""

    label: str
    total_usd: float
    legs: int
    by_environment: dict[str, float]
    by_lane: dict[tuple[str, str], tuple[int, float]]


@dataclass(frozen=True)
class GateCandidate:
    """One promotion-gate run: every recorded leg of every attempt, summed."""

    run_id: str
    ref: str
    first_recorded: datetime
    attempts: int
    legs: int
    cost_usd: float


@dataclass(frozen=True)
class OffLedgerSummary:
    """The report's figures: trailing windows, calendar months, and the gate's cost."""

    as_of: datetime
    records: int
    windows: list[WindowSpend]
    months: list[tuple[str, dict[str, float]]]
    gate_candidates: list[GateCandidate]


def _window(label: str, records: Sequence[OffLedgerSpend]) -> WindowSpend:
    by_env: dict[str, float] = defaultdict(float)
    by_lane: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0.0, 0.0])
    for record in records:
        by_env[record.environment] += record.estimated_cost_usd
        cell = by_lane[(record.lane, record.environment)]
        cell[0] += 1
        cell[1] += record.estimated_cost_usd
    return WindowSpend(
        label=label,
        total_usd=sum(r.estimated_cost_usd for r in records),
        legs=len(records),
        by_environment=dict(sorted(by_env.items())),
        by_lane={key: (int(v[0]), v[1]) for key, v in sorted(by_lane.items())},
    )


def is_gate_leg(record: OffLedgerSpend) -> bool:
    """Whether a record is a leg of a promotion-gate run of the integration suite."""
    return record.workflow == "integration-test" and record.selection == "gate"


def summarize(
    records: Iterable[OffLedgerSpend], *, as_of: datetime, months: int = 6
) -> OffLedgerSummary:
    """The trailing 7- and 30-day windows, the newest ``months`` months with spend, and the gate.

    Windows read each record's ``recorded_at``; a record after ``as_of`` is
    left out, so a report taken at a past instant says what was known then.
    """
    as_of = _aware(as_of)
    kept = [r for r in records if _aware(r.recorded_at) <= as_of]
    windows = [
        _window(
            f"Trailing {days} days",
            [r for r in kept if _aware(r.recorded_at) > as_of - timedelta(days=days)],
        )
        for days in (7, 30)
    ]
    by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for record in kept:
        month = _aware(record.recorded_at).astimezone(UTC).strftime("%Y-%m")
        by_month[month][record.environment] += record.estimated_cost_usd
    newest_months = sorted(by_month)[-months:]
    gate: dict[str, list[OffLedgerSpend]] = defaultdict(list)
    for record in kept:
        if is_gate_leg(record):
            gate[record.run_id].append(record)
    candidates = sorted(
        (
            GateCandidate(
                run_id=run_id,
                ref=legs[0].ref,
                first_recorded=min(_aware(leg.recorded_at) for leg in legs),
                attempts=len({leg.run_attempt for leg in legs}),
                legs=len(legs),
                cost_usd=sum(leg.estimated_cost_usd for leg in legs),
            )
            for run_id, legs in gate.items()
        ),
        key=lambda c: (c.first_recorded, c.run_id),
    )
    return OffLedgerSummary(
        as_of=as_of,
        records=len(kept),
        windows=windows,
        months=[(month, dict(sorted(by_month[month].items()))) for month in newest_months],
        gate_candidates=candidates,
    )


def _usd(value: float) -> str:
    return f"${value:,.2f}"


def render_report(summary: OffLedgerSummary, *, recent_gate_runs: int = 10) -> str:
    """The report as Markdown, for a run summary."""
    out = [
        "## Test and staging model spend",
        "",
        "Integration smokes, the promotion gate, staging rehearsals and the replay and "
        "pilot rounds, from the per-leg records the `run-ops` sweep keeps on the "
        f"`ops-metrics` branch ({summary.records} records as of "
        f"{summary.as_of.strftime('%Y-%m-%d %H:%M')}Z). **Reported separately: none of "
        "this counts toward the spend backstop or the auto-release budget.**",
        "",
    ]
    for window in summary.windows:
        envs = ", ".join(f"{env} {_usd(v)}" for env, v in window.by_environment.items())
        out.append(
            f"**{window.label}:** {_usd(window.total_usd)} over {window.legs} legs"
            + (f" ({envs})" if envs else "")
            + "."
        )
        if window.by_lane:
            out += ["", "| Lane | Environment | Legs | Spend |", "| --- | --- | ---: | ---: |"]
            out += [
                f"| {lane} | {env} | {legs} | {_usd(cost)} |"
                for (lane, env), (legs, cost) in window.by_lane.items()
            ]
        out.append("")
    if summary.months:
        out += [
            "**By month:**",
            "",
            "| Month | prod | staging | Total |",
            "| --- | ---: | ---: | ---: |",
        ]
        for month, by_env in summary.months:
            prod, staging = by_env.get("prod", 0.0), by_env.get("staging", 0.0)
            out.append(f"| {month} | {_usd(prod)} | {_usd(staging)} | {_usd(prod + staging)} |")
        out.append("")
    candidates = summary.gate_candidates
    if candidates:
        costs = sorted(c.cost_usd for c in candidates)
        middle = len(costs) // 2
        median = costs[middle] if len(costs) % 2 else (costs[middle - 1] + costs[middle]) / 2
        out += [
            f"**Promotion gate:** {len(candidates)} gate runs on record, median "
            f"{_usd(median)} a run (every recorded leg of every attempt; a leg whose record "
            "was lost is missing, so read it as a lower bound), range "
            f"{_usd(costs[0])} to {_usd(costs[-1])}.",
            "",
            "| Run | Ref | Recorded | Attempts | Legs | Spend |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
        out += [
            f"| {c.run_id} | `{c.ref}` | {c.first_recorded.strftime('%Y-%m-%d')} | "
            f"{c.attempts} | {c.legs} | {_usd(c.cost_usd)} |"
            for c in candidates[-recent_gate_runs:]
        ]
        out.append("")
    else:
        out += ["**Promotion gate:** no gate run on record yet.", ""]
    return "\n".join(out)


def summary_json(summary: OffLedgerSummary) -> str:
    """The summary as a JSON document (the report's figures, unrounded)."""
    doc = {
        "as_of": summary.as_of.isoformat(),
        "records": summary.records,
        "counted_in_backstop": False,
        "windows": [
            {
                "label": w.label,
                "total_usd": w.total_usd,
                "legs": w.legs,
                "by_environment": w.by_environment,
                "by_lane": [
                    {"lane": lane, "environment": env, "legs": legs, "usd": cost}
                    for (lane, env), (legs, cost) in w.by_lane.items()
                ],
            }
            for w in summary.windows
        ],
        "months": [{"month": m, "by_environment": envs} for m, envs in summary.months],
        "gate_candidates": [
            {
                "run_id": c.run_id,
                "ref": c.ref,
                "first_recorded": c.first_recorded.isoformat(),
                "attempts": c.attempts,
                "legs": c.legs,
                "usd": c.cost_usd,
            }
            for c in summary.gate_candidates
        ],
    }
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"
