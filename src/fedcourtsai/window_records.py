"""What a supersession or a revocation owes the record, computed from the ledger.

The freeze record's declaration that a superseded predictor process is closed,
not revoked (``docs/freeze-record.md``, 2026-09-26) leaves two things owed in
prose that this module makes runnable (``docs/process-version.md``):

* **The successor's disclosures** (:func:`successor_disclosures`). A successor
  entry states the closed windows' resolved and pending counts at its instant;
  the number of **split events**, on which some engines' counted cells come
  from a closed window and others' from the successor; per engine, how many of
  the successor's counted events hold a failed or missing earlier-window
  attempt (partitioned four ways), because the successor's population is the
  events the closed window did not reach, and that population is selected;
  and the count per evaluator digest of the closed windows' gradings, because
  a window's figure can pool rubrics once a full freeze moves the evaluator
  digests.
* **A revoked window's figures over its resolved slice**
  (:func:`revoked_window_board`). A revocation made after any affected outcome
  publishes the revoked window's figures over the slice that had resolved, so
  the exclusion is visible rather than silent.

Both are read-only, deterministic and offline over the committed ledger (the
board also reads the committed statpack, as ``fedcourts leaderboard`` does).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from . import process_version
from .ids import parse_run_id
from .integrity import cell_clock, latest_evaluation_runs
from .leaderboard import build_leaderboard, cell_facts, skill_components, vote_scores
from .paths import CasePaths
from .process_version import co_current, graded_in_window, window_of
from .schemas import (
    CountingWindow,
    Evaluation,
    Leaderboard,
    Outcome,
    StatPack,
)
from .serialize import read_model
from .store import (
    EvaluationKey,
    LedgerPrediction,
    evaluation_key,
    iter_predictions,
    ledger_counts,
    prediction_counts,
    scored_prediction,
    stratify,
)


class WindowRecordError(ValueError):
    """The registry holds no window the request names, or names it inconsistently."""


class _Report(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ClosedWindowCensus(_Report):
    """One closed window's counted events, split by whether they had resolved at its close."""

    label: str
    digest: str
    predictor_ids: list[str] = Field(
        description="The predictors whose committed cells carry this window's digest"
    )
    closes: datetime
    counted_events: int = Field(ge=0, description="Events on which the window holds a counted cell")
    resolved_at_close: int = Field(
        ge=0,
        description="Of those, events whose committed outcome resolved on or before the close's "
        "UTC day — an upper bound on the slice whose outcomes were visible when the close was "
        "decided, since an outcome dated the close's day may have landed after its instant",
    )
    pending_at_close: int = Field(
        ge=0, description="The rest: no outcome yet, or one that resolved after the close's day"
    )


class EngineEarlierAttempts(_Report):
    """One predictor's successor-window events, and what its closed window left on them."""

    predictor_id: str
    closed_window: str = Field(description="The label of the closed window read as its earlier one")
    closed_window_inferred: bool = Field(
        default=False,
        description="True where no committed cell carries one of the closed windows' digests "
        "for this predictor — an engine whose closed window produced only failures, or one the "
        "closed label never blessed — so its earlier span is read as the closed windows' whole "
        "span rather than one window's. Never reported as a clean zero",
    )
    successor_counted_events: int = Field(
        ge=0, description="The four counts below partition these events"
    )
    failed_earlier_attempt: int = Field(
        ge=0,
        description="Events on which the predictor holds a committed failure fact "
        "(`attempt.json`) whose run fell inside its earlier span",
    )
    uncounted_earlier_cell: int = Field(
        ge=0,
        description="Events with no such failure on which the predictor holds a committed cell "
        "inside its earlier span that does not count there (a shakedown run, an unstamped or "
        "unblessed digest) — an earlier attempt that failed to count",
    )
    not_reached_before_close: int = Field(
        ge=0,
        description="Events with neither, which no predictor had committed a cell on before the "
        "close — the closed window never had the chance to miss them",
    )
    missing_earlier_attempt: int = Field(
        ge=0,
        description="The rest: events the pipeline had reached before the close (some predictor "
        "committed a cell on them before it) on which this predictor left neither a cell nor a "
        "failure fact in its earlier span",
    )


class EvaluatorDigestCount(_Report):
    """How many of the closed windows' counted gradings one evaluator digest made."""

    evaluator_id: str
    digest: str | None = Field(
        description="The grading's harness-stamped digest; null if unstamped"
    )
    gradings: int = Field(ge=0)
    graded_after_instant: int = Field(
        ge=0, description="Of those, gradings stamped at or after the successor's instant"
    )


class SuccessorDisclosures(_Report):
    """Everything a successor's freeze-record entry states about the windows it closed."""

    closed_label: str
    successor_label: str
    instant: datetime = Field(description="The successor's counting instant (its windows' opening)")
    closed_windows: list[ClosedWindowCensus]
    split_events: int = Field(
        ge=0,
        description="Events on which counted cells come from both a closed window and a "
        "successor window that never ran together — events no complete grid holds",
    )
    split_events_resolved: int = Field(ge=0, description="Of those, events with an outcome")
    engines: list[EngineEarlierAttempts]
    evaluator_digests: list[EvaluatorDigestCount]


def _windows_labelled(label: str) -> list[CountingWindow]:
    return [w for w in process_version.COUNTING_WINDOWS if w.label == label]


def _outcome(data_root: Path, row: LedgerPrediction) -> Outcome | None:
    path = CasePaths(data_root, row.court_id, row.docket_id).event(row.event_id).outcome
    return read_model(path, Outcome) if path.is_file() else None


def _attempt_runs(data_root: Path, row: LedgerPrediction, predictor_id: str) -> list[datetime]:
    """When each committed failure fact of ``predictor_id`` on ``row``'s event ran."""
    event = CasePaths(data_root, row.court_id, row.docket_id).event(row.event_id)
    runs: list[datetime] = []
    for path in sorted(event.predictions_dir.glob(f"{predictor_id}/*/attempt.json")):
        try:
            runs.append(parse_run_id(path.parent.name))
        except ValueError:
            continue
    return runs


@dataclass(frozen=True)
class _Ledger:
    """The committed predictions read once: per event, each predictor's counted window."""

    rows: list[LedgerPrediction]
    #: (case, event) -> predictor -> the window its counted cell sits in
    counted: dict[tuple[str, str], dict[str, CountingWindow]]
    #: (case, event) -> one of its rows, for the event's paths
    example: dict[tuple[str, str], LedgerPrediction]
    #: (case, event) -> the earliest harness clock of any committed cell on it
    first_clock: dict[tuple[str, str], datetime]
    #: (case, event, predictor) -> the harness clock of each of its committed cells
    clocks: dict[tuple[str, str, str], list[datetime]]


def _read_ledger(data_root: Path) -> _Ledger:
    rows = iter_predictions(data_root)
    counted: dict[tuple[str, str], dict[str, CountingWindow]] = defaultdict(dict)
    example: dict[tuple[str, str], LedgerPrediction] = {}
    first_clock: dict[tuple[str, str], datetime] = {}
    clocks: dict[tuple[str, str, str], list[datetime]] = defaultdict(list)
    for row, counts in zip(rows, ledger_counts(rows), strict=True):
        key = (row.case_id, row.event_id)
        example.setdefault(key, row)
        clock = cell_clock(row.prediction)
        first_clock[key] = min(clock, first_clock.get(key, clock))
        clocks[(*key, row.predictor_id)].append(clock)
        window = window_of(row.prediction.process_version)
        if counts and window is not None:
            counted[key][row.predictor_id] = window
    return _Ledger(rows, counted, example, first_clock, clocks)


def successor_disclosures(
    data_root: Path, *, closed_label: str, successor_label: str
) -> SuccessorDisclosures:
    """The successor entry's disclosures for the windows ``closed_label`` closed.

    Read over the committed ledger as it stands; run it at the successor's
    freeze commit for the counts its entry quotes, and again at the carrying
    promotion (cells keep landing). The closed windows are ``closed_label``'s
    windows that carry a ``closes``; the instant is the earliest opening among
    ``successor_label``'s windows. A digest ``closed_label`` blessed and the
    successor carried forward byte-identical keeps one unbroken window, which is
    not closed and so appears in no census here.
    """
    closed = [w for w in _windows_labelled(closed_label) if w.closes is not None]
    successor = set(_windows_labelled(successor_label))
    if not closed:
        raise WindowRecordError(f"no closed window carries the label {closed_label!r}")
    if not successor:
        raise WindowRecordError(f"no window carries the label {successor_label!r}")
    ledger = _read_ledger(data_root)
    outcomes = {key: _outcome(data_root, row) for key, row in ledger.example.items()}
    split = [
        key
        for key, held in ledger.counted.items()
        if set(held.values()) & set(closed)
        and set(held.values()) & successor
        and not co_current(held.values())
    ]
    instant = min(w.opens for w in successor)
    return SuccessorDisclosures(
        closed_label=closed_label,
        successor_label=successor_label,
        instant=instant,
        closed_windows=_census(ledger, closed, outcomes),
        split_events=len(split),
        split_events_resolved=sum(1 for key in split if outcomes[key] is not None),
        engines=_engines(data_root, ledger, closed, successor),
        evaluator_digests=_evaluator_digests(data_root, set(closed), instant),
    )


def _owners(ledger: _Ledger, closed: Sequence[CountingWindow]) -> dict[CountingWindow, set[str]]:
    """Each closed window's predictors: those whose committed cells carry its digest."""
    by_digest = {window.digest: window for window in closed}
    owners: dict[CountingWindow, set[str]] = defaultdict(set)
    for row in ledger.rows:
        stamp = row.prediction.process_version
        if stamp is not None and stamp.digest in by_digest:
            owners[by_digest[stamp.digest]].add(row.predictor_id)
    return owners


def _census(
    ledger: _Ledger,
    closed: Sequence[CountingWindow],
    outcomes: dict[tuple[str, str], Outcome | None],
) -> list[ClosedWindowCensus]:
    """Each closed window's counted events, resolved and pending at its close."""
    owners = _owners(ledger, closed)
    census: list[ClosedWindowCensus] = []
    for window in sorted(closed, key=lambda w: (w.opens, w.digest)):
        closes = window.closes
        assert closes is not None
        events = [key for key, held in ledger.counted.items() if window in held.values()]
        resolved = sum(
            1
            for key in events
            if (outcome := outcomes[key]) is not None and outcome.resolved_at <= closes.date()
        )
        census.append(
            ClosedWindowCensus(
                label=window.label,
                digest=window.digest,
                predictor_ids=sorted(owners[window]),
                closes=closes,
                counted_events=len(events),
                resolved_at_close=resolved,
                pending_at_close=len(events) - resolved,
            )
        )
    return census


def _engines(
    data_root: Path,
    ledger: _Ledger,
    closed: Sequence[CountingWindow],
    successor: set[CountingWindow],
) -> list[EngineEarlierAttempts]:
    """Per predictor, its successor-counted events and what its earlier span left on them.

    A predictor's earlier span is the closed window whose digest its committed
    cells carry. Where none does, the closed windows' whole span stands in and
    the row says it was inferred: a failure fact names no digest, so an engine
    whose closed window only ever failed owns no window by its cells, and that
    is the engine whose disclosure matters most.
    """
    closed_of = {
        predictor_id: window
        for window, predictors in _owners(ledger, closed).items()
        for predictor_id in predictors
    }
    whole = CountingWindow(
        label=closed[0].label,
        digest=closed[0].digest,
        opens=min(w.opens for w in closed),
        closes=max(w.closes for w in closed if w.closes is not None),
    )
    events: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key, held in ledger.counted.items():
        for predictor_id, window in held.items():
            if window in successor:
                events[predictor_id].append(key)
    engines: list[EngineEarlierAttempts] = []
    for predictor_id in sorted(events):
        earlier = closed_of.get(predictor_id, whole)
        closes = earlier.closes
        assert closes is not None
        tally: Counter[str] = Counter()
        for key in events[predictor_id]:
            runs = _attempt_runs(data_root, ledger.example[key], predictor_id)
            if any(earlier.contains(run) for run in runs):
                tally["failed"] += 1
            elif any(earlier.contains(clock) for clock in ledger.clocks[(*key, predictor_id)]):
                tally["uncounted"] += 1
            elif ledger.first_clock[key] >= closes:
                tally["unreached"] += 1
            else:
                tally["missing"] += 1
        engines.append(
            EngineEarlierAttempts(
                predictor_id=predictor_id,
                closed_window=earlier.label,
                closed_window_inferred=predictor_id not in closed_of,
                successor_counted_events=len(events[predictor_id]),
                failed_earlier_attempt=tally["failed"],
                uncounted_earlier_cell=tally["uncounted"],
                not_reached_before_close=tally["unreached"],
                missing_earlier_attempt=tally["missing"],
            )
        )
    return engines


def _evaluator_digests(
    data_root: Path, closed: set[CountingWindow], instant: datetime
) -> list[EvaluatorDigestCount]:
    """The closed windows' counted gradings, one per cell per judge, by evaluator digest."""
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    scoped: list[Evaluation] = []
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        event_dir = path.parents[4]
        scored = scored_prediction(event_dir, evaluation.predictor_id, evaluation.prediction_run_id)
        if scored is None or window_of(scored.process_version) not in closed:
            continue
        if not prediction_counts(event_dir, evaluation.predictor_id, scored):
            continue
        if not graded_in_window(evaluation.process_version, scored.process_version):
            continue
        scoped.append(evaluation)
    tally: Counter[tuple[str, str | None]] = Counter()
    after: Counter[tuple[str, str | None]] = Counter()
    for evaluation in latest_evaluation_runs(scoped, lambda ev: ev):
        stamp = evaluation.process_version
        key = (evaluation.evaluator_id, stamp.digest if stamp is not None else None)
        tally[key] += 1
        if stamp is not None and stamp.stamped_at >= instant:
            after[key] += 1
    return [
        EvaluatorDigestCount(
            evaluator_id=evaluator_id,
            digest=digest,
            gradings=tally[(evaluator_id, digest)],
            graded_after_instant=after[(evaluator_id, digest)],
        )
        for evaluator_id, digest in sorted(tally, key=lambda k: (k[0], k[1] or ""))
    ]


class RevokedWindowRecord(_Report):
    """A revoked window's board over the slice that had resolved when it was revoked."""

    label: str
    windows: list[CountingWindow] = Field(description="The revoked windows carrying the label")
    resolved_by: dict[str, date] = Field(
        description="Per revoked digest, the UTC day of its revocation: a cell enters the board "
        "only where its event's outcome resolved on or before it"
    )
    resolved_counted_events: dict[str, int] = Field(
        description="Per revoked digest, the events of every stage on which the window holds a "
        "counted cell (revocation lifted) whose outcome resolved by its revocation day, graded "
        "or not — the size of the resolved slice. Not a denominator for the board's cert-only "
        "`events_scored`, which covers the ranked cert moment alone"
    )
    forward_claim_excluded: int = Field(
        ge=0,
        description="The window's resolved-slice gradings the forward-claim rule kept off the "
        "board, as the leaderboard's own exclusion does",
    )
    leakage_excluded: int = Field(
        ge=0,
        description="The window's resolved-slice gradings the leakage bit kept off the board",
    )
    graded_after_revocation: int = Field(
        ge=0,
        description="Gradings on the board stamped after their window's revocation. The board "
        "reads the ledger's gradings as of its build, so a late grading or re-grade can enter; "
        "this says how many did",
    )
    board: Leaderboard = Field(
        description="The frozen leaderboard as the window's cells read with the revocation "
        "lifted, restricted to the window's own cells over the resolved slice, gradings as of "
        "the build. Its `process_scope` and ranks are the board builder's: this is a "
        "counterfactual record of what the exclusion removed, never a results surface, and "
        "never quoted as performance"
    )


def revoked_window_board(
    data_root: Path, *, label: str, statpack: StatPack | None
) -> RevokedWindowRecord:
    """The revoked window's figures over its resolved slice.

    The board's cells and figures are built as ``fedcourts leaderboard`` builds
    the frozen board's — the same stratify pass and exclusions, skill terms,
    band facts and vote scores — without the agreement views or the collapse
    count, with the revocation lifted for ``label``'s revoked windows only and
    the cells then restricted to those windows' cells on events whose outcome
    resolved on or before the day each window was revoked. Lifting the
    revocation restores those cells' counting as it stood before it — a later
    window's cell stamped before the revocation stays behind the restored
    earlier cell, as it did — so the board is the one the revocation removed,
    cut to the outcomes that had been seen. Gradings are the ledger's as of the
    build, so a later grading or re-grade can enter; the record counts how many
    did. Its ``frozen_process`` is the registry as committed, revocation
    included, and ``resolved_counted_events`` is the resolved slice the board's
    events are a part of.
    """
    revoked = [w for w in _windows_labelled(label) if w.revoked_at is not None]
    if not revoked:
        raise WindowRecordError(f"no revoked window carries the label {label!r}")
    lifted = {w: w.model_copy(update={"revoked_at": None}) for w in revoked}
    resolved_by = {w.digest: _day(w.revoked_at) for w in revoked}
    revocations = {w.digest: w.revoked_at for w in revoked if w.revoked_at is not None}

    keep = set(lifted.values())

    def in_slice(evaluation: Evaluation, windows: Mapping[EvaluationKey, CountingWindow]) -> bool:
        window = windows.get(evaluation_key(evaluation))
        return (
            window is not None
            and window in keep
            and _resolved_by(data_root, evaluation, resolved_by[window.digest])
        )

    registry = tuple(lifted.get(w, w) for w in process_version.COUNTING_WINDOWS)
    with process_version.counting_windows(registry):
        run = stratify(data_root, refuse_pooled_windows=False)
        cells = [cell for cell in run.cells if in_slice(cell[0], run.cell_windows)]
        rows = iter_predictions(data_root)
        slice_events: dict[str, set[tuple[str, str]]] = {w.digest: set() for w in revoked}
        for row, counts in zip(rows, ledger_counts(rows), strict=True):
            window = window_of(row.prediction.process_version)
            if counts and window in keep and window is not None:
                outcome = _outcome(data_root, row)
                if outcome is not None and outcome.resolved_at <= resolved_by[window.digest]:
                    slice_events[window.digest].add((row.case_id, row.event_id))
        board = build_leaderboard(
            cells,
            process_scope="frozen",
            skills=skill_components(cells, data_root, statpack),
            facts=cell_facts(cells, data_root),
            vote_scores=vote_scores(cells, data_root),
            cell_windows=run.cell_windows,
        )
    return RevokedWindowRecord(
        label=label,
        windows=revoked,
        resolved_by=resolved_by,
        resolved_counted_events={digest: len(keys) for digest, keys in slice_events.items()},
        forward_claim_excluded=sum(
            1 for cell in run.excluded if in_slice(cell.evaluation, run.cell_windows)
        ),
        leakage_excluded=sum(
            1 for cell in run.leaked if in_slice(cell.evaluation, run.cell_windows)
        ),
        graded_after_revocation=sum(
            1
            for evaluation, *_ in cells
            if evaluation.process_version is not None
            and (window := run.cell_windows.get(evaluation_key(evaluation))) is not None
            and evaluation.process_version.stamped_at > revocations[window.digest]
        ),
        board=board.model_copy(update={"frozen_process": process_version.frozen_process_record()}),
    )


def _day(when: datetime | None) -> date:
    assert when is not None
    return when.date()


def _resolved_by(data_root: Path, evaluation: Evaluation, day: date) -> bool:
    court, _, docket = evaluation.case_id.partition("/")
    path = CasePaths(data_root, court, int(docket)).event(evaluation.event_id).outcome
    return path.is_file() and read_model(path, Outcome).resolved_at <= day


def render_disclosures(report: SuccessorDisclosures) -> str:
    """The disclosures as the lines a successor's freeze-record entry quotes."""
    lines = [
        f"successor {report.successor_label} closes {report.closed_label} at "
        f"{report.instant.isoformat()}",
    ]
    for window in report.closed_windows:
        lines.append(
            f"  closed {window.label} {', '.join(window.predictor_ids) or '(no cells)'}: "
            f"{window.counted_events} counted event(s) — {window.resolved_at_close} resolved, "
            f"{window.pending_at_close} pending at close"
        )
    lines.append(
        f"  split events: {report.split_events} ({report.split_events_resolved} resolved) "
        "— in no complete grid"
    )
    for engine in report.engines:
        lines.append(
            f"  {engine.predictor_id}: {engine.successor_counted_events} successor-counted "
            f"event(s); earlier window {engine.closed_window}"
            f"{' (inferred span)' if engine.closed_window_inferred else ''}: "
            f"{engine.failed_earlier_attempt} failed, {engine.uncounted_earlier_cell} uncounted "
            f"cell, {engine.missing_earlier_attempt} missing, "
            f"{engine.not_reached_before_close} not reached before the close"
        )
    for count in report.evaluator_digests:
        lines.append(
            f"  graded by {count.evaluator_id} @ {count.digest or 'unstamped'}: "
            f"{count.gradings} grading(s), {count.graded_after_instant} at or after the instant"
        )
    return "\n".join(lines)
