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
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from . import corpus
from .analytics import _is_scored_segment_row
from .backtest import (
    Backtester,
    BacktestFeatures,
    BacktestItem,
    BacktestPrediction,
    backtest_features,
)
from .config import SalienceConfig
from .paths import CasePaths
from .pipeline import cell_context, cert_signals
from .pipeline.cert_signals import match_disposition_signal
from .pipeline.evaluate import brier_skill, segment_base_rate
from .pipeline.outcome import (
    entry_descriptions,
    granted_flag,
    is_machine_readable,
    snapshot_shows_disposition,
)
from .pipeline.runner import EngineUnavailable, Runner, RunRequest, get_runner
from .pipeline.salience import salience_band, salience_bands, salience_score
from .registry import enabled_predictors
from .schemas import (
    CalibrationBin,
    CertBacktest,
    CertBacktestBigCase,
    CertBacktestEntry,
    CertBacktestSegment,
    Disposition,
    EventKind,
    PredictableEvent,
    Prediction,
    PredictorConfig,
    StatPack,
    UsageRole,
)
from .serialize import read_model, write_raw_json, write_yaml

# Mirrors the leaderboard's tie-break: entries rank by lift (desc) then Brier
# (asc), and every entry here reports a Brier, so no missing-value sentinel is
# needed — kept as a constant anyway for parity if one ever is.
_CALIBRATION_BINS = 10


CERT_BACKTEST_SCOPES: tuple[str, ...] = ("all", "paid", "selected")


def _in_scope(row: corpus.CorpusRow, scope: str, floor: float) -> bool:
    """Whether a hard-eligible cert row is in the requested ``scope``.

    ``all`` is every modern-cert petition (the raw predictor-quality view).
    ``paid`` narrows to the paid segment the salience gate scores (IFP being the
    dominant Tier-0 exclusion — :func:`analytics._is_scored_segment_row`, the same
    scored-segment proxy the statpack uses; a non-IFP Tier-0 drop is not modeled
    here). ``selected`` narrows further to the gate's own **carve-out** rule — a
    CVSG petition or one at/above the salience ``floor``
    (:func:`pipeline.salience._select_cohort`) — the ``N``-independent core of the
    live selected slice. It is that core, not the whole live population: the live
    slice also fills to ``N`` by rank, a cohort-dependent remainder not
    reconstructable at back-test time.
    """
    if scope == "all":
        return True
    if not _is_scored_segment_row(row):  # paid modern-cert only
        return False
    if scope == "paid":
        return True
    return row.cvsg_date is not None or salience_score(row) >= floor


def _conference_key(row: corpus.CorpusRow) -> str:
    """A cohort key for the spread sampler: the conference, else the Term.

    Prefers the parsed ``distributed_for_conference`` (only the live/REST channels
    populate it); falls back to the docket's Term year so bulk-seeded rows still
    spread across terms rather than collapsing into one bucket.
    """
    if row.distributed_for_conference is not None:
        return row.distributed_for_conference.isoformat()
    term = corpus.scotus_term_year(row.docket_number)
    return f"term-{term}" if term is not None else "term-unknown"


def _spread_sample(rows_recent_first: list[corpus.CorpusRow], limit: int) -> list[corpus.CorpusRow]:
    """Round-robin across conference cohorts, most-recent within each.

    Most-recent-first ordering alone collapses a small ``limit`` onto the last
    order lists (a grant/GVR-heavy term-end snapshot); this instead draws the
    newest petition from each conference, then the next from each, until ``limit``
    — so the sample mirrors a full term's live cadence across conferences rather
    than one moment. Deterministic: buckets preserve the recency order they were
    fed, and cohorts are visited in most-recent-first order.
    """
    buckets: dict[str, list[corpus.CorpusRow]] = {}
    order: list[str] = []
    for row in rows_recent_first:
        key = _conference_key(row)
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(row)
    sampled: list[corpus.CorpusRow] = []
    depth = 0
    while len(sampled) < limit:
        progressed = False
        for key in order:
            if depth < len(buckets[key]):
                sampled.append(buckets[key][depth])
                progressed = True
                if len(sampled) >= limit:
                    return sampled
        if not progressed:
            break
        depth += 1
    return sampled


def select_cert_backtest_set(
    conn: sqlite3.Connection,
    *,
    limit: int | None = None,
    scope: str = "all",
    spread: bool = False,
    salience_floor: float | None = None,
) -> list[BacktestItem]:
    """The decided cert petitions to back-test, most recently decided first.

    A row qualifies when it is a SCOTUS **modern discretionary-cert** docket
    (:func:`corpus.is_modern_cert` — the Term-prefixed post-1925 form, so the
    mandatory-jurisdiction and application/original regimes never contaminate
    the label space), carries a **machine-readable** disposition (the same bar
    outcome detection trusts), and has internally consistent dates.

    ``scope`` (:data:`CERT_BACKTEST_SCOPES`) then narrows to the population the
    live task runs on: ``all`` keeps every modern-cert petition; ``paid`` drops
    IFP (the gate's Tier-0 exclusion); ``selected`` keeps only the gate's
    carve-out core (CVSG or at/above ``salience_floor``), the closest replay-safe
    analog of the live selected slice. ``salience_floor`` defaults to the shipped
    :class:`SalienceConfig` floor.

    Ordering is by most recent decision then ``case_id`` (deterministic), so a
    small ``limit`` samples recent cert practice. ``spread`` instead round-robins
    across conference cohorts (:func:`_spread_sample`), so the sample mirrors a
    full term's live cadence rather than collapsing onto the last order lists.
    """
    if scope not in CERT_BACKTEST_SCOPES:
        raise ValueError(
            f"unknown scope {scope!r}; choose one of {', '.join(CERT_BACKTEST_SCOPES)}"
        )
    floor = salience_floor if salience_floor is not None else SalienceConfig().floor
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", resolved=True)
        if row.disposition is not None
        and is_machine_readable(Disposition(row.disposition))
        and corpus.is_modern_cert(row)
        and not corpus.is_date_inconsistent(row)
        and _in_scope(row, scope, floor)
    ]
    rows.sort(key=lambda r: (corpus.recency_key(r), r.case_id))
    if spread and limit is not None:
        rows = _spread_sample(rows, limit)
    elif limit is not None:
        rows = rows[:limit]
    return [BacktestItem(backtest_features(row), Disposition(str(row.disposition))) for row in rows]


# Snapshot fields that exist only because the matter was decided (or that record
# the decision), stripped before an agentic replay sees the docket. This
# blocklist is key-name-based, so every channel's outcome-bearing keys must be
# listed.
#
# The proceedings entries are NOT here: they are truncated by date instead
# (`truncate_snapshot`). Content offers no rule that separates a disposing order
# from a pre-decision entry, but a date does — an entry filed before the cutoff
# cannot record a decision that came after it. Dropping them wholesale left a
# replay cell reading a docket with no history at all, which is not the docket
# any forward cell ever saw, and left it unable to observe its own salience band.
# Truncation is applied on top of this list, never instead of it.
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
    # Regenerated on docket activity, so on a decided live docket it postdates
    # (and thereby leaks the existence of) the decision.
    "sJsonCreationDate",
    # The /qp/ page is generated when certiorari is GRANTED and opens with the
    # grant order — the key's very presence leaks the outcome (verified live).
    # The questions presented reach cells from the petition text instead.
    "QPLink",
)


def redact_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop the derived fields that exist only because the matter was decided.

    :data:`SNAPSHOT_OUTCOME_FIELDS` only. The proceedings entries survive this
    and are handled by :func:`truncate_snapshot`, which is the other half — a
    caller wanting the pre-decision view wants both.
    """
    return {key: value for key, value in payload.items() if key not in SNAPSHOT_OUTCOME_FIELDS}


def replay_cutoff(payload: Mapping[str, Any], resolved_at: date) -> date | None:
    """The day after the last distribution entry that predates ``resolved_at``.

    A forward cell is queued by a **distribution transition**, so that is the
    moment a replay has to reproduce if the two channels are to be comparable.
    Taking the last such entry before resolution puts the replay at the latest
    posture a forward cell would have seen — the hardest and most realistic one,
    and exactly one cell per petition.

    ``None`` when the payload shows no dated distribution before resolution, in
    which case there is no forward moment to reproduce and the caller drops the
    entries wholesale rather than guessing a cutoff.

    Reading entry dates rather than the conference dates they name is deliberate:
    the entry "DISTRIBUTED for Conference of March 7" is *filed* in late February,
    and February is when a forward cell would have run.
    """
    latest: date | None = None
    for text, raw in cert_signals.proceedings_entries(payload):
        if not cert_signals.DISTRIBUTED_RE.search(text):
            continue
        filed = cert_signals.entry_date(raw)
        if filed is not None and filed < resolved_at and (latest is None or filed > latest):
            latest = filed
    return latest + timedelta(days=1) if latest is not None else None


def truncate_snapshot(
    payload: Mapping[str, Any], cutoff: date | None
) -> tuple[dict[str, Any], int]:
    """The docket as it stood strictly before ``cutoff``, and how many entries went.

    ``cutoff=None`` removes the proceedings **key**, not just its contents: when
    no forward moment could be identified the docket's posture is unknown, and an
    empty list would instead assert that it was empty. A real cutoff leaves the
    list even when nothing survives, because that genuinely is an observation.

    **Fails closed on an undated entry.** An entry whose date is missing or
    unparseable is dropped, because it could be the disposing order and nothing
    about it says otherwise. That costs a little pre-decision context and cannot
    leak an outcome, which is the right way round.

    A surviving entry is reduced to the fields a consumer reads (see
    :data:`_ENTRY_FIELDS`), because the outcome blocklist matches top-level keys
    only and nothing else screens what an entry nests.

    Entry ids are positional and assigned on read, so truncating the *tail*
    renumbers nothing. Dropping an undated entry from the *middle* does shift
    everything after it — accepted, because the alternative is keeping an entry
    that could be the disposing order, and nothing downstream pins an id across a
    truncation.
    """
    out = dict(payload)
    dropped = 0
    for key in cert_signals.PROCEEDINGS_KEYS:
        entries = out.get(key)
        if not isinstance(entries, list):
            continue
        if cutoff is None:
            # No cutoff means no moment could be identified, so the key is removed
            # outright rather than emptied. An empty list is an observation — "the
            # docket had no entries then" — and this is the opposite of one. Left
            # as `[]`, a cell would read zero distributions and claim the weakest
            # band about a petition whose posture is entirely unknown.
            dropped += len(entries)
            del out[key]
            continue
        kept: list[Any] = []
        for entry in entries:
            filed = (
                cert_signals.entry_date(_entry_raw_date(entry))
                if isinstance(entry, Mapping)
                else None
            )
            if filed is not None and filed < cutoff:
                kept.append(_entry_fields(entry))
            else:
                dropped += 1
        # A real cutoff with nothing surviving IS an observation: as at that date
        # the docket carried no entries, and `[]` says so.
        out[key] = kept
    return out, dropped


def _kept_entries_show_a_disposition(payload: Mapping[str, Any]) -> bool:
    """Whether a truncated payload still carries a disposing order.

    The date rule's premise is that the last distribution before resolution
    precedes the disposing order. That is usually true and not always: cert dates
    are not latched, so ``resolution_date`` can fall back to the docket's
    termination, and a rehearing petition after a denial draws a fresh
    distribution — either way the cutoff can land after the order that decided the
    matter.

    Rather than enumerate those cases, assert the property directly with the two
    instruments the forward path already uses for its own leakage guard
    (``provision-snapshot --refuse-terminal``): the high-recall terminal scan and
    the resolver, over every surviving entry. A hit means the cutoff cannot be
    trusted, and the caller degrades to showing no trajectory at all — which is
    the previous behaviour, and safe.
    """
    if snapshot_shows_disposition(payload) is not None:
        return True
    return any(match_disposition_signal(text) is not None for text in entry_descriptions(payload))


#: What a surviving entry keeps. The outcome blocklist matches **top-level** keys,
#: so nothing screens the structures nested inside an entry — a live entry's
#: `Links` (document pointers; a replay cell is provisioned no documents, so this
#: would be its only path to one) or a REST entry's `recap_documents`, which
#: carries document text and its own upload date. Rather than extend a blocklist
#: to a shape upstream can change under us, keep only the two fields every
#: consumer actually reads and drop the rest.
_ENTRY_FIELDS: tuple[str, ...] = ("Date", "Text", "date_filed", "description")


def _entry_fields(entry: Mapping[str, Any]) -> dict[str, Any]:
    """A surviving entry reduced to the fields a consumer reads."""
    return {key: entry[key] for key in _ENTRY_FIELDS if key in entry}


def _entry_raw_date(entry: Mapping[str, Any]) -> str | None:
    """An entry's own date string, over either payload shape."""
    raw = entry.get("Date") if "Date" in entry else entry.get("date_filed")
    return str(raw) if raw else None


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
    config_root: Path,
    engine_override: str | None,
    skip_engines: frozenset[str] = frozenset(),
) -> list[tuple[PredictorConfig, Runner]]:
    """Pair each enabled predictor with its runner, dropping unroutable ones.

    Routing is per predictor — its configured ``engine`` names the backend — so a
    claude-baseline vs codex-baseline read stays apples-to-apples; a predictor
    whose engine has no registered runner (e.g. one only the live workflow's
    agent step can drive) is left out rather than silently replayed, mislabeled,
    through another model. ``engine_override`` routes every predictor through one
    named backend instead (the offline ``stub``/``replay`` runs); an unknown
    override still raises, since that is a caller typo rather than a config gap.
    ``skip_engines`` is the explicit per-engine opt-out: a predictor whose own
    configured engine is named there is dropped up front — evaluated on the
    predictor's declared engine even under an ``engine_override`` sweep, so
    ``--skip-engines gemini`` means "don't run gemini-baseline" regardless of how
    the rest is routed. The default runs every enabled predictor's engine.
    """
    predictors = [
        p
        for p in enabled_predictors(config_root / "predictors.yaml")
        if str(p.engine) not in skip_engines
    ]
    if engine_override is not None:
        runner = get_runner(engine_override)
        return [(p, runner) for p in predictors]
    pairs: list[tuple[PredictorConfig, Runner]] = []
    runners: dict[str, Runner] = {}
    for predictor in predictors:
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
    skip_engines: frozenset[str] = frozenset(),
) -> tuple[list[Backtester], list[str], dict[str, int]]:
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
    backend for offline ``stub``/``replay`` runs, and ``skip_engines`` opts
    named engines out) and collects its
    ``prediction.json``. Each cell carries the trial's year as its replay clock
    (``DECIDED_BEFORE``), so the agent's own corpus retrieval is masked to
    provably earlier history — the same cutoff the offline prior-vote baseline
    honors. Returns the :class:`ReplayedBacktester` list (one per predictor that
    produced predictions) plus the ids of predictors whose engine turned out to
    be **unavailable** mid-run — the workflow installs every engine, so this is a
    safety net for config drift (a missing CLI binary), caught per engine and
    dropped **loudly** rather than crashing the whole run and stranding the spend
    already made on the other engines. A real engine spends tokens per cell.
    Callers filter the set through :func:`replayable_items` first; a petition
    with no snapshot or petition event here is an internal-invariant error.
    """
    pairs = _runners_by_predictor(config_root, engine_override, skip_engines)
    collected: dict[str, dict[str, BacktestPrediction]] = {p.id: {} for p, _ in pairs}
    unavailable: set[str] = set()
    # Three information sets, counted as they are provisioned. A blind cell cannot
    # observe its own relist history at all, which is most of what a cert forecast
    # turns on, so a score over their union is a score over a mixture.
    provisioning: Counter[str] = Counter()
    for item in items:
        court, _, docket_raw = item.features.case_id.partition("/")
        docket = int(docket_raw)
        case_paths = CasePaths(work_root, court, docket)
        with corpus.connect_readonly(corpus_db_path) as conn:
            found = corpus.latest_snapshot(conn, item.features.case_id)
            events = corpus.events_for_case(conn, item.features.case_id)
            row = corpus.get_row(conn, item.features.case_id)
            resolved_at = corpus.resolution_date(row) if row is not None else None
            # Prefer a snapshot the docket really served before the cutoff over one
            # reconstructed by truncation: only the first knows what had not yet
            # been filed. Both are recorded, so the two are never pooled silently.
            cutoff = (
                replay_cutoff(found[1], resolved_at)
                if found is not None and resolved_at is not None
                else None
            )
            dated = (
                corpus.snapshot_at(conn, item.features.case_id, before=cutoff)
                if cutoff is not None
                else None
            )
        petitions = [ev for ev in events if ev.kind == EventKind.petition]
        if found is None or not petitions:
            raise ValueError(
                f"{item.features.case_id}: no snapshot or petition event to replay against"
            )
        snapshot_date, payload = found
        provenance: Literal["dated", "truncated", "blind"] = (
            "truncated" if cutoff is not None else "blind"
        )
        if dated is not None:
            snapshot_date, payload = dated
            provenance = "dated"
        redacted = redact_snapshot(payload)
        # Truncation runs on the dated payload too. It is a no-op when the stored
        # snapshot really predates the cutoff, and an alarm when it does not —
        # nothing enforces that a snapshot's date equals the moment it was served.
        redacted, _ = truncate_snapshot(redacted, cutoff)
        # Fail closed on the premise the date rule rests on. `resolution_date` can
        # fall back to the docket's termination where the cert dates were never
        # stamped, and a rehearing petition after a denial draws a fresh
        # distribution — so a cutoff can legitimately land *after* the disposing
        # order, keeping it. The forward path already runs exactly this scan as its
        # own leakage guard; the replay path, which ships a decided docket's
        # entries, needs it more.
        if _kept_entries_show_a_disposition(redacted):
            redacted, _ = truncate_snapshot(redacted, None)
            provenance = "blind"
            cutoff = None
        # A truncated payload is the docket as at the cutoff, so it is dated by the
        # cutoff — not by the post-decision pull whose bytes it was reconstructed
        # from. Labelling it with the latter would put a date months after
        # resolution on the one file the leakage grade is judged against.
        if provenance != "dated" and cutoff is not None:
            snapshot_date = cutoff
        provisioning[provenance] += 1
        write_raw_json(case_paths.snapshot(snapshot_date.isoformat()), redacted)
        # The cell's mode context: a replay cell runs with the same tools
        # as a forward one — etiquette, logging, and the cross-evaluator's leakage
        # grading replace walls — so the prompt contract needs the mode stated, not
        # inferred. It carries the same conditioning block a forward cell gets, now
        # that truncation leaves a docket to derive one from: a replay cell that can
        # see its own trajectory can be scored against the rate that trajectory
        # implies, instead of one keyed on where the petition ended up.
        write_raw_json(
            case_paths.cell_context,
            cell_context.build(
                item.features.case_id,
                snapshot_date,
                redacted,
                "replay",
                provenance=provenance,
                cutoff=cutoff,
                decided_before=str(item.features.year),
            ).model_dump(mode="json"),
        )
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
            if predictor.id in unavailable:
                continue  # this engine's binary was already found missing
            try:
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
            except EngineUnavailable:
                # Config drift (the CLI binary is not installed): drop this engine
                # from the whole replay rather than crash and lose the spend the
                # other engines already made. The caller reports the drop loudly.
                unavailable.add(predictor.id)
                continue
            cell = read_model(
                case_paths.event(event.event_id).prediction(predictor.id, run_id), Prediction
            )
            collected[predictor.id][item.features.case_id] = BacktestPrediction(
                Disposition(cell.predicted_disposition),
                cell.probability,
                big_case_score=cell.big_case_score,
            )
    backtesters: list[Backtester] = [
        ReplayedBacktester(id=pid, predictions=preds)
        for pid, preds in collected.items()
        if pid not in unavailable
    ]
    return backtesters, sorted(unavailable), dict(provisioning)


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


@dataclass(frozen=True)
class _ItemSegment:
    """A cert item's salience band and its leakage-safe segment base rate."""

    band: str
    base_rate: float | None


def build_segment_context(
    conn: sqlite3.Connection,
    items: list[BacktestItem],
    statpack: StatPack,
    *,
    lookback_terms: int | None = None,
) -> dict[str, _ItemSegment]:
    """Map each **paid scored-segment** petition to its sal-v1 band + base rate.

    The band comes from :func:`salience_band` and the base rate from
    :func:`segment_base_rate` (leakage-safe: pooled over statpack Terms strictly
    before the item's own). IFP and other non-scored rows are omitted — they sit
    outside the population the salience gate predicts, so the per-band breakdown
    covers the same paid segment the statpack's segment rate is computed over.

    ``lookback_terms`` bounds that pool; ``None`` takes the field default
    (``0``, the absent-file fallback — every prior Term), **not** the shipped
    config value. Production passes the loaded config's window.
    """
    window = (
        lookback_terms if lookback_terms is not None else SalienceConfig().base_rate_lookback_terms
    )
    context: dict[str, _ItemSegment] = {}
    for item in items:
        row = corpus.get_row(conn, item.features.case_id)
        if row is None or not _is_scored_segment_row(row):
            continue
        context[item.features.case_id] = _ItemSegment(
            band=salience_band(row),
            base_rate=segment_base_rate(row, statpack, lookback_terms=window),
        )
    return context


class _BandAcc:
    """Streaming accumulator for one salience band's cert back-test scores."""

    __slots__ = ("base_rates", "brier_sum", "correct", "events", "skills")

    def __init__(self) -> None:
        self.events = 0
        self.correct = 0
        self.brier_sum = 0.0
        self.base_rates: list[float] = []
        self.skills: list[float] = []

    def add(
        self, disp_correct: bool, brier: float, actual_granted: int, base_rate: float | None
    ) -> None:
        self.events += 1
        self.correct += int(disp_correct)
        self.brier_sum += brier
        if base_rate is not None:
            self.base_rates.append(base_rate)
        skill = brier_skill(brier, actual_granted, base_rate)
        if skill is not None:
            self.skills.append(skill)


def _band_segments(band_acc: dict[str, _BandAcc]) -> list[CertBacktestSegment]:
    """Roll the per-band accumulators into segments, in the fixed band order."""
    segments = []
    for band in salience_bands():
        acc = band_acc.get(band)
        if acc is None or acc.events == 0:
            continue
        segments.append(
            CertBacktestSegment(
                band=band,
                events_scored=acc.events,
                accuracy=acc.correct / acc.events,
                mean_brier_score=acc.brier_sum / acc.events,
                segment_base_rate=(
                    sum(acc.base_rates) / len(acc.base_rates) if acc.base_rates else None
                ),
                mean_brier_skill=(sum(acc.skills) / len(acc.skills) if acc.skills else None),
            )
        )
    return segments


def _big_case_distribution(scores: list[float]) -> CertBacktestBigCase | None:
    """Summarize a predictor's pre-registered stakes scores, or ``None`` if it gave none.

    A distribution, not a grade: the replay has no independent evaluator, so it
    reports coverage and spread (never a correlation with the realized grant —
    stakes are not grant likelihood).
    """
    if not scores:
        return None
    return CertBacktestBigCase(
        scored=len(scores),
        mean=sum(scores) / len(scores),
        minimum=min(scores),
        maximum=max(scores),
    )


def _score_one(
    backtester: Backtester,
    items: list[BacktestItem],
    always_denied_accuracy: float,
    segments: Mapping[str, _ItemSegment] | None,
) -> CertBacktestEntry:
    correct = 0
    granted_correct = 0
    brier_sum = 0.0
    pairs: list[tuple[float, int]] = []
    band_acc: dict[str, _BandAcc] = {}
    big_case_scores: list[float] = []
    for item in items:
        prediction = backtester.predict(item.features)
        actual_granted = granted_flag(item.actual_disposition)
        disp_correct = prediction.predicted_disposition == item.actual_disposition
        if disp_correct:
            correct += 1
        if granted_flag(prediction.predicted_disposition) == actual_granted:
            granted_correct += 1
        brier = (prediction.probability_granted - actual_granted) ** 2
        brier_sum += brier
        pairs.append((prediction.probability_granted, actual_granted))
        if prediction.big_case_score is not None:
            big_case_scores.append(prediction.big_case_score)
        if segments is not None:
            seg = segments.get(item.features.case_id)
            if seg is not None:
                acc = band_acc.setdefault(seg.band, _BandAcc())
                acc.add(disp_correct, brier, actual_granted, seg.base_rate)
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
        segments=_band_segments(band_acc),
        big_case=_big_case_distribution(big_case_scores),
    )


def run_cert_backtest(
    backtesters: list[Backtester],
    items: list[BacktestItem],
    *,
    segments: Mapping[str, _ItemSegment] | None = None,
    provisioning: Mapping[str, int] | None = None,
) -> CertBacktest:
    """Replay each backtester over the cert set and roll the scores up best-first.

    Entries rank by **lift over the always-deny floor** (desc) — under the
    denial skew that, not raw accuracy, is the signal — then mean Brier (asc),
    then ``predictor_id``; a total order, deterministic under ties. An empty set
    yields the empty zero-count report. When ``segments`` is given (from
    :func:`build_segment_context`), each entry also carries the per-salience-band
    skill breakdown vs the leakage-safe segment base rate — the same yardstick the
    forward stratum uses; omitted on the offline runs that pass no statpack.
    """
    if not items:
        return CertBacktest(events_scored=0, predictors_evaluated=0, entries=[])
    always_denied_accuracy = sum(
        item.actual_disposition == Disposition.denied for item in items
    ) / len(items)
    entries = [
        _score_one(backtester, items, always_denied_accuracy, segments)
        for backtester in backtesters
    ]
    entries.sort(key=lambda e: (-e.lift_over_always_denied, e.mean_brier_score, e.predictor_id))
    for position, entry in enumerate(entries, start=1):
        entry.rank = position
    return CertBacktest(
        events_scored=len(items),
        predictors_evaluated=len(entries),
        always_denied_accuracy=always_denied_accuracy,
        provisioning=dict(provisioning or {}),
        entries=entries,
    )
