"""Cert back-test: replay predictors over decided cert petitions, outcome hidden.

The cert-specific counterpart of :mod:`fedcourtsai.backtest`, and the standing
instrument for vetting cert predictors and prompt changes before a live
long-conference set exists. It differs from the generic back-test on exactly the
axes the cert task demands:

- **Selection** is the population the cert model actually predicts: resolved
  SCOTUS **modern discretionary-cert** petitions (:func:`corpus.is_modern_cert`)
  with a machine-readable grant/deny label — the pre-1925 mandatory-jurisdiction
  regime and the application/original forms are excluded up front, so scoring
  labels stay comparable. Most recently decided first, so a small ``--limit``
  reads on recent cert practice.
- **Scoring** reports the honest signal under cert's structural denial skew:
  raw accuracy is cheap when almost everything is denied, so each entry carries
  **lift over the always-deny floor** plus a decile **calibration** view of
  P(granted) against the observed grant rate.
- **Agentic replay** runs the configured predictors through the same engine
  runner ``run-predict`` uses, over a **redacted snapshot** — every field that
  exists only because the matter was decided is stripped — into a scratch root,
  never the ``data/`` ledger. The result is retrospective by construction (the
  outcomes predate every modern model's training cutoff), and the report says so
  (the same pre-registration rule the leaderboard stratifies on).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import corpus
from .backtest import (
    Backtester,
    BacktestFeatures,
    BacktestItem,
    BacktestPrediction,
    backtest_features,
)
from .paths import CasePaths
from .pipeline.outcome import granted_flag, is_machine_readable
from .pipeline.runner import Runner, RunRequest, get_runner
from .registry import enabled_predictors
from .schemas import (
    CalibrationBin,
    CertBacktest,
    CertBacktestEntry,
    Disposition,
    EventKind,
    PredictableEvent,
    Prediction,
    PredictorConfig,
    UsageRole,
)
from .serialize import read_model, write_raw_json, write_yaml

# Mirrors the leaderboard's tie-break: entries rank by lift (desc) then Brier
# (asc), and every entry here reports a Brier, so no missing-value sentinel is
# needed — kept as a constant anyway for parity if one ever is.
_CALIBRATION_BINS = 10


def select_cert_backtest_set(
    conn: sqlite3.Connection, *, limit: int | None = None
) -> list[BacktestItem]:
    """The decided cert petitions to back-test, most recently decided first.

    A row qualifies when it is a SCOTUS **modern discretionary-cert** docket
    (:func:`corpus.is_modern_cert` — the Term-prefixed post-1925 form, so the
    mandatory-jurisdiction and application/original regimes never contaminate
    the label space), carries a **machine-readable** disposition (the same bar
    outcome detection trusts), and has internally consistent dates. Ordered by
    most recent decision then ``case_id`` (deterministic), so a small ``limit``
    samples recent cert practice — the population the live task resembles.
    """
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", resolved=True)
        if row.disposition is not None
        and is_machine_readable(Disposition(row.disposition))
        and corpus.is_modern_cert(row)
        and not corpus.is_date_inconsistent(row)
    ]
    rows.sort(key=lambda r: (corpus.recency_key(r), r.case_id))
    if limit is not None:
        rows = rows[:limit]
    return [BacktestItem(backtest_features(row), Disposition(str(row.disposition))) for row in rows]


# Snapshot fields that exist only because the matter was decided (or that record
# the decision), stripped before an agentic replay sees the docket. Docket
# entries go wholesale: the disposing order lives there, and no deterministic
# rule can separate it from pre-decision entries. The live channel's snapshots
# (#472) are the raw supremecourt.gov JSON, whose entries key is
# `ProceedingsandOrder` — the disposing order rides there as plain text
# ("Petition DENIED."), so it gets the same wholesale treatment; this blocklist
# is key-name-based, so every channel's outcome-bearing keys must be listed.
SNAPSHOT_OUTCOME_FIELDS: tuple[str, ...] = (
    "disposition",
    "date_terminated",
    "date_decided",
    "date_cert_granted",
    "date_cert_denied",
    "date_argued",
    "date_reargued",
    "date_rehearing_denied",
    "clusters",
    "citations",
    "citation_count",
    "opinion_text",
    "precedential_status",
    "summary",
    "docket_entries",
    "ProceedingsandOrder",
    # Regenerated on docket activity, so on a decided live docket it postdates
    # (and thereby leaks the existence of) the decision.
    "sJsonCreationDate",
    # The /qp/ page is generated when certiorari is GRANTED and opens with the
    # grant order — the key's very presence leaks the outcome (verified live,
    # #474). The questions presented reach cells from the petition text instead.
    "QPLink",
)


def redact_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """A decided docket's snapshot as it would have read before the decision.

    Drops :data:`SNAPSHOT_OUTCOME_FIELDS` so a replayed predictor is tested on
    foresight, not on reading the outcome off the docket — the file-level
    counterpart of :class:`fedcourtsai.backtest.BacktestFeatures`' withholding.
    (What no redaction can remove is the model's parametric memory of a famous
    case; that is why the report is labeled retrospective.)
    """
    return {key: value for key, value in payload.items() if key not in SNAPSHOT_OUTCOME_FIELDS}


@dataclass(frozen=True)
class ReplayedBacktester:
    """A :class:`Backtester` over predictions already produced by an engine replay."""

    id: str
    predictions: dict[str, BacktestPrediction]

    def predict(self, features: BacktestFeatures) -> BacktestPrediction:
        return self.predictions[features.case_id]


def replayable_items(
    corpus_db_path: Path, items: list[BacktestItem]
) -> tuple[list[BacktestItem], list[str]]:
    """Split the cert set into replayable petitions and the skipped case ids.

    An engine replay needs what a live predict cell reads — a held snapshot and a
    petition event — and partial coverage is the norm while the date backfill
    drains (a bulk-seeded row has neither until its first fetch). Filtering up
    front keeps one report internally comparable: every backtester, offline
    baselines included, is scored over the same kept set, and the caller can name
    what was skipped instead of failing the whole run on the first bare row.
    """
    kept: list[BacktestItem] = []
    skipped: list[str] = []
    with corpus.connect_readonly(corpus_db_path) as conn:
        for item in items:
            found = corpus.latest_snapshot(conn, item.features.case_id)
            events = corpus.events_for_case(conn, item.features.case_id)
            if found is not None and any(ev.kind == EventKind.petition for ev in events):
                kept.append(item)
            else:
                skipped.append(item.features.case_id)
    return kept, skipped


def _runners_by_predictor(
    config_root: Path, engine_override: str | None
) -> list[tuple[PredictorConfig, Runner]]:
    """Pair each enabled predictor with its runner, dropping unroutable ones.

    Routing is per predictor — its configured ``engine`` names the backend — so a
    claude-baseline vs codex-baseline read stays apples-to-apples; a predictor
    whose engine has no registered runner (e.g. one only the live workflow's
    agent step can drive) is left out rather than silently replayed, mislabeled,
    through another model. ``engine_override`` routes every predictor through one
    named backend instead (the offline ``stub``/``replay`` runs); an unknown
    override still raises, since that is a caller typo rather than a config gap.
    """
    if engine_override is not None:
        runner = get_runner(engine_override)
        return [(p, runner) for p in enabled_predictors(config_root / "predictors.yaml")]
    pairs: list[tuple[PredictorConfig, Runner]] = []
    runners: dict[str, Runner] = {}
    for predictor in enabled_predictors(config_root / "predictors.yaml"):
        backend = str(predictor.engine)
        if backend not in runners:
            try:
                runners[backend] = get_runner(backend)
            except KeyError:
                continue
        pairs.append((predictor, runners[backend]))
    return pairs


def replay_predictors(
    items: list[BacktestItem],
    *,
    corpus_db_path: Path,
    config_root: Path,
    work_root: Path,
    run_id: str,
    engine_override: str | None = None,
) -> list[Backtester]:
    """Replay every routable enabled predictor over ``items``, each through its
    own configured engine.

    For each petition this provisions what a live predict cell reads — the
    latest snapshot (**redacted**, see :func:`redact_snapshot`) and the event
    definition **as it looked while open** (``resolved: false``, so nothing in
    the working tree says the matter is decided) — under ``work_root`` (a
    scratch tree, never the ``data/`` ledger), then runs each predictor's cell
    via its own engine's runner (see :func:`_runners_by_predictor`; a predictor
    whose engine has no registered runner is absent from the result rather than
    mislabeled through another engine, and ``engine_override`` forces one
    backend for offline ``stub``/``replay`` runs) and collects its
    ``prediction.json``. Each cell carries the trial's year as its replay clock
    (``DECIDED_BEFORE``), so the agent's own corpus retrieval is masked to
    provably earlier history — the same cutoff the offline prior-vote baseline
    honors. Returns one :class:`ReplayedBacktester` per routable predictor,
    ready for :func:`run_cert_backtest`. A real engine spends tokens per cell.
    Callers filter the set through :func:`replayable_items` first; a petition
    with no snapshot or petition event here is an internal-invariant error.
    """
    pairs = _runners_by_predictor(config_root, engine_override)
    collected: dict[str, dict[str, BacktestPrediction]] = {p.id: {} for p, _ in pairs}
    for item in items:
        court, _, docket_raw = item.features.case_id.partition("/")
        docket = int(docket_raw)
        case_paths = CasePaths(work_root, court, docket)
        with corpus.connect_readonly(corpus_db_path) as conn:
            found = corpus.latest_snapshot(conn, item.features.case_id)
            events = corpus.events_for_case(conn, item.features.case_id)
        petitions = [ev for ev in events if ev.kind == EventKind.petition]
        if found is None or not petitions:
            raise ValueError(
                f"{item.features.case_id}: no snapshot or petition event to replay against"
            )
        snapshot_date, payload = found
        write_raw_json(case_paths.snapshot(snapshot_date.isoformat()), redact_snapshot(payload))
        event = petitions[0]
        write_yaml(
            case_paths.event(event.event_id).event_file,
            PredictableEvent(
                event_id=event.event_id,
                case_id=event.case_id,
                kind=event.kind,
                title=event.title or event.case_id,
                description=event.description,
                opened_at=event.opened_at,
                decision_target=event.decision_target,
                resolved=False,  # the pre-decision view: the outcome stays hidden
            ),
        )
        for predictor, engine_runner in pairs:
            engine_runner.run(
                RunRequest(
                    role=UsageRole.predictor,
                    court_id=court,
                    docket_id=docket,
                    event_id=event.event_id,
                    actor_id=predictor.id,
                    run_id=run_id,
                    prompt=Path(predictor.prompt),
                    data_root=work_root,
                    # The replay clock: the cell sees it as DECIDED_BEFORE and
                    # masks its corpus retrieval to provably earlier history.
                    decided_before=item.features.year,
                )
            )
            cell = read_model(
                case_paths.event(event.event_id).prediction(predictor.id, run_id), Prediction
            )
            collected[predictor.id][item.features.case_id] = BacktestPrediction(
                Disposition(cell.predicted_disposition), cell.probability
            )
    return [ReplayedBacktester(id=pid, predictions=preds) for pid, preds in collected.items()]


def _calibration(pairs: list[tuple[float, int]]) -> list[CalibrationBin]:
    """Decile bins of (P(granted), realized granted); empty bins are omitted.

    The top bin is closed at 1.0 so a probability of exactly 1.0 lands in it.
    """
    bins: list[CalibrationBin] = []
    width = 1.0 / _CALIBRATION_BINS
    for index in range(_CALIBRATION_BINS):
        lower = index * width
        upper = 1.0 if index == _CALIBRATION_BINS - 1 else (index + 1) * width
        members = [
            (probability, granted)
            for probability, granted in pairs
            if lower <= probability < upper
            or (index == _CALIBRATION_BINS - 1 and probability == 1.0)
        ]
        if not members:
            continue
        bins.append(
            CalibrationBin(
                lower=lower,
                upper=upper,
                predictions=len(members),
                mean_probability=sum(p for p, _ in members) / len(members),
                observed_granted_rate=sum(g for _, g in members) / len(members),
            )
        )
    return bins


def _score_one(
    backtester: Backtester, items: list[BacktestItem], always_denied_accuracy: float
) -> CertBacktestEntry:
    correct = 0
    granted_correct = 0
    brier_sum = 0.0
    pairs: list[tuple[float, int]] = []
    for item in items:
        prediction = backtester.predict(item.features)
        actual_granted = granted_flag(item.actual_disposition)
        if prediction.predicted_disposition == item.actual_disposition:
            correct += 1
        if granted_flag(prediction.predicted_disposition) == actual_granted:
            granted_correct += 1
        brier_sum += (prediction.probability_granted - actual_granted) ** 2
        pairs.append((prediction.probability_granted, actual_granted))
    n = len(items)
    return CertBacktestEntry(
        predictor_id=backtester.id,
        rank=1,  # provisional; assigned after sorting
        events_scored=n,
        accuracy=correct / n,
        granted_accuracy=granted_correct / n,
        mean_brier_score=brier_sum / n,
        lift_over_always_denied=correct / n - always_denied_accuracy,
        calibration=_calibration(pairs),
    )


def run_cert_backtest(backtesters: list[Backtester], items: list[BacktestItem]) -> CertBacktest:
    """Replay each backtester over the cert set and roll the scores up best-first.

    Entries rank by **lift over the always-deny floor** (desc) — under the
    denial skew that, not raw accuracy, is the signal — then mean Brier (asc),
    then ``predictor_id``; a total order, deterministic under ties. An empty set
    yields the empty zero-count report.
    """
    if not items:
        return CertBacktest(events_scored=0, predictors_evaluated=0, entries=[])
    always_denied_accuracy = sum(
        item.actual_disposition == Disposition.denied for item in items
    ) / len(items)
    entries = [_score_one(backtester, items, always_denied_accuracy) for backtester in backtesters]
    entries.sort(key=lambda e: (-e.lift_over_always_denied, e.mean_brier_score, e.predictor_id))
    for position, entry in enumerate(entries, start=1):
        entry.rank = position
    return CertBacktest(
        events_scored=len(items),
        predictors_evaluated=len(entries),
        always_denied_accuracy=always_denied_accuracy,
        entries=entries,
    )
