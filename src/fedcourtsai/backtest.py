"""Back-testing harness: replay predictors against resolved corpus events.

A corpus row carries the realized ``disposition`` (see
:mod:`fedcourtsai.corpus`), which makes the historical corpus a ready-made
back-test set: take every **resolved** event, hide its outcome, replay a
predictor against the facts it would have seen before the decision, and score
the prediction against the known label. The result rolls up into
``metrics/backtest.json`` (DVC-tracked) so ``dvc metrics diff`` tracks predictor
quality on history alongside the live leaderboard.

The scoring half here is deterministic and offline — a pure function of the
corpus, with no clock or randomness — so the same corpus always yields
byte-identical output. The *predictor* half is a seam: a :class:`Backtester`
maps the visible features of one trial to a predicted disposition and a
P(granted). Two reference baselines run entirely offline (a constant floor and a
corpus-retrieval vote), so the harness produces a real metric today; the
configured agentic predictors in ``config/predictors.yaml`` plug into the same
seam and are replayed out of band, exactly as ``run-predict`` runs them live.
"""

from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from . import corpus
from .corpus import CorpusRow, PriorQuery
from .pipeline.outcome import granted_flag, is_machine_readable
from .schemas import Backtest, BacktestEntry, Disposition

# Brier scores are bounded in [0, 1]; a predictor that reported none sorts after
# every one that did, without colliding with a real worst score (mirrors the
# leaderboard's tie-break sentinel).
_NO_BRIER: float = 2.0


@dataclass(frozen=True)
class BacktestFeatures:
    """The pre-decision facts a back-test predictor may see; outcome withheld.

    Deliberately excludes everything that reveals the result — the
    ``disposition`` label itself, the decision date, and the opinion text/summary
    that only exist once the matter is decided — so a replay is a fair test of
    foresight rather than hindsight.
    """

    case_id: str
    court: str
    topic: str | None
    judges: tuple[str, ...]
    citations: tuple[str, ...]
    date_filed: date | None


@dataclass(frozen=True)
class BacktestItem:
    """One resolved corpus case as a back-test trial: features + the hidden truth."""

    features: BacktestFeatures
    actual_disposition: Disposition


@dataclass(frozen=True)
class BacktestPrediction:
    """A predictor's output for one trial."""

    predicted_disposition: Disposition
    probability_granted: float


class Backtester(Protocol):
    """A predictor that can be replayed over the historical back-test set.

    The same seam the agentic predictors target out of band: given the visible
    features of one resolved event, return a predicted disposition and a
    calibrated P(granted) to score against the realized outcome.
    """

    @property
    def id(self) -> str: ...

    def predict(self, features: BacktestFeatures) -> BacktestPrediction: ...


def _features(row: CorpusRow) -> BacktestFeatures:
    return BacktestFeatures(
        case_id=row.case_id,
        court=row.court,
        topic=row.topic,
        judges=tuple(row.judges),
        citations=tuple(row.citations),
        date_filed=row.date_filed,
    )


def select_backtest_set(
    conn: sqlite3.Connection,
    *,
    court: str | None = None,
    limit: int | None = None,
) -> list[BacktestItem]:
    """The resolved corpus events to back-test, in ``case_id`` order.

    A row qualifies when its ``disposition`` is **machine-readable** — a concrete
    label, not ``None`` (unresolved) or ``other`` (decided but unclassified) —
    the same bar outcome detection uses before recording ground truth, so the
    back-test scores only against labels the pipeline trusts. ``court`` restricts
    the set; ``limit`` caps it (the first N in stable order).
    """
    items: list[BacktestItem] = []
    for row in corpus.iter_rows(conn, court=court):
        if row.disposition is None:
            continue
        disposition = Disposition(row.disposition)
        if not is_machine_readable(disposition):
            continue
        items.append(BacktestItem(_features(row), disposition))
        if limit is not None and len(items) >= limit:
            break
    return items


@dataclass(frozen=True)
class ConstantBacktester:
    """Always predicts one disposition — the trivial floor a real predictor must beat."""

    id: str
    disposition: Disposition

    def predict(self, features: BacktestFeatures) -> BacktestPrediction:
        return BacktestPrediction(self.disposition, float(granted_flag(self.disposition)))


@dataclass
class PriorVoteBacktester:
    """Predicts the majority disposition among similar resolved priors (leave-one-out).

    The corpus-as-back-test-set made literal: for each trial it retrieves priors
    sharing the case's court / judges / citations (excluding the case itself via
    leave-one-out), predicts their most common disposition, and reads P(granted)
    off the fraction of those priors that were granted. With no matching prior it
    falls back to ``denied`` / 0.0, so it always returns a prediction.
    """

    conn: sqlite3.Connection
    id: str = "prior-vote"
    limit: int = corpus.DEFAULT_PRIOR_LIMIT

    def predict(self, features: BacktestFeatures) -> BacktestPrediction:
        query = PriorQuery(
            court=features.court,
            judges=list(features.judges),
            citations=list(features.citations),
            resolved_only=True,
        )
        # Pull one extra so dropping the case under test still leaves up to `limit`.
        retrieved = corpus.retrieve_priors(self.conn, query, limit=self.limit + 1)
        priors = [row for row in retrieved if row.case_id != features.case_id][: self.limit]
        labels = [Disposition(row.disposition) for row in priors if row.disposition is not None]
        if not labels:
            return BacktestPrediction(Disposition.denied, 0.0)
        # Most common label, ties broken by the Disposition enum order for determinism.
        counts = Counter(labels)
        top = max(counts, key=lambda d: (counts[d], -list(Disposition).index(d)))
        granted_share = sum(granted_flag(label) for label in labels) / len(labels)
        return BacktestPrediction(top, granted_share)


def default_backtesters(conn: sqlite3.Connection) -> list[Backtester]:
    """The reference baselines the ``backtest`` command replays offline.

    A constant floor plus the retrieval vote — both deterministic — so the
    metric is real without an agent in the loop. Agentic predictors are layered
    on the same :class:`Backtester` seam out of band.
    """
    return [
        ConstantBacktester(id="constant-denied", disposition=Disposition.denied),
        PriorVoteBacktester(conn),
    ]


def _score_one(backtester: Backtester, items: list[BacktestItem]) -> BacktestEntry:
    correct = 0
    granted_correct = 0
    brier_sum = 0.0
    for item in items:
        prediction = backtester.predict(item.features)
        if prediction.predicted_disposition == item.actual_disposition:
            correct += 1
        actual_granted = granted_flag(item.actual_disposition)
        if granted_flag(prediction.predicted_disposition) == actual_granted:
            granted_correct += 1
        brier_sum += (prediction.probability_granted - actual_granted) ** 2
    n = len(items)
    return BacktestEntry(
        predictor_id=backtester.id,
        rank=1,  # provisional; assigned after sorting
        events_scored=n,
        accuracy=correct / n,
        granted_accuracy=granted_correct / n,
        mean_brier_score=brier_sum / n,
    )


def run_backtest(backtesters: list[Backtester], items: list[BacktestItem]) -> Backtest:
    """Replay each backtester over ``items`` and roll the scores up best-first.

    One entry per predictor: disposition accuracy, binary granted accuracy, and
    the mean Brier score of P(granted). Entries rank by accuracy (desc), then
    mean Brier score (asc, missing last), then ``predictor_id`` — a total order,
    so the ranking is deterministic under ties. An empty back-test set (no
    resolved events, or no corpus) yields an empty zero-count report rather than
    rows of meaningless zeros.
    """
    if not items:
        return Backtest(predictors_evaluated=0, events_scored=0, entries=[])

    entries = [_score_one(backtester, items) for backtester in backtesters]
    entries.sort(
        key=lambda e: (
            -e.accuracy,
            e.mean_brier_score if e.mean_brier_score is not None else _NO_BRIER,
            e.predictor_id,
        )
    )
    for position, entry in enumerate(entries, start=1):
        entry.rank = position
    return Backtest(
        predictors_evaluated=len(entries),
        events_scored=len(items),
        entries=entries,
    )
