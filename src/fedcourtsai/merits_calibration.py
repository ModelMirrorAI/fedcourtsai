"""The pilot's replay merits calibration cells: kept forecasts laid into a ledger tree.

The ``predicted_reasoning_quality`` pilot (``docs/outcome-decomposition.md``,
*The pilot, and what it reports*) grades replay merits documents on decided
cases as **calibration evidence only**: their opinions are public, so a replay
document can carry its outcome and its grade never tests a predictor. The
documents come from a merits back-test's ``merits-forecasts`` artifact
(``run-backtest``'s ``replay: merits``), whose kept tree
(:func:`fedcourtsai.merits_backtest.kept_forecasts`) holds, per engine lane and
moment, each cell's event definition and forecast files.

:func:`read_kept_run` reads that tree back and refuses anything outside its
layout, since the tree crossed a run boundary as agent-written files.
:func:`calibration_documents` draws the cases to grade, and
:func:`write_calibration_overlay` lays them into a ``data/``-shaped root the way
an evaluate cell expects to find a resolved event: the predictions as kept, and
the event definition and the outcome rebuilt from the corpus rather than taken
from the tree. Nothing here writes the committed ledger: the overlay is a pilot
round's working tree, and the round commits nothing.
"""

from __future__ import annotations

import hashlib
import re
import stat
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import corpus
from .merits_backtest import (
    KEPT_FILE_MAX_BYTES,
    KEPT_FORECAST_FILES,
    MeritsReplayCase,
    replay_event,
)
from .paths import CasePaths
from .pipeline import moments
from .pipeline.outcome import build_merits_outcome, known_decision_method
from .reasoning_pilot import PilotDocument
from .schemas import Engine, Moment, PredictableEvent, Prediction, Stage
from .serialize import load_yaml, write_json, write_yaml

CALIBRATION_SEED = "predicted-reasoning-pilot/merits-calibration"
DEFAULT_CALIBRATION_CASES = 15
DEFAULT_CALIBRATION_MOMENT = Moment.briefed

_RUN_ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
_KEPT_PATH = re.compile(
    r"^(?P<lane>[^/]+)/(?P<moment>[^/]+)/cases/(?P<court>[^/]+)/(?P<docket>[^/]+)"
    r"/events/(?P<event>[^/]+)/(?:event\.yaml|predictions/(?P<predictor>[^/]+)"
    r"/(?P<run>[^/]+)/(?P<name>[^/]+))$"
)
_ENGINES = frozenset(engine.value for engine in Engine)


KEPT_MAX_FILES = 4000
"""More files than a 20-case replay keeps by an order of magnitude; past it, refused."""

KEPT_MAX_TOTAL_BYTES = 64 * 1024 * 1024
"""The whole kept tree's ceiling, beside the per-file cap."""


@dataclass(frozen=True)
class KeptForecast:
    """One predictor's kept cell: its forecast files, by name, at one case and moment."""

    lane: str
    moment: Moment
    case_id: str
    event_id: str
    opened_at: date | None
    prediction: Prediction
    files: Mapping[str, bytes]


@dataclass(frozen=True)
class KeptRun:
    """A merits back-test run's kept forecasts, read back and checked."""

    run_id: str
    forecasts: list[KeptForecast]


_CellKey = tuple[str, str, str, str, str]
_EventKey = tuple[str, str, str, str]


def _read_capped(path: Path) -> bytes:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{path} is not a regular file")
    if info.st_size > KEPT_FILE_MAX_BYTES:
        raise ValueError(f"{path} is over the kept-file cap")
    body = path.read_bytes()
    if len(body) > KEPT_FILE_MAX_BYTES:
        raise ValueError(f"{path} is over the kept-file cap")
    return body


def _walk(
    root: Path, run_id: str, lanes: frozenset[str]
) -> tuple[dict[_CellKey, dict[str, bytes]], dict[_EventKey, bytes]]:
    """Every kept file by cell, and every kept event definition, refused at the first misfit."""
    cells: dict[_CellKey, dict[str, bytes]] = defaultdict(dict)
    events: dict[_EventKey, bytes] = {}
    count = total = 0
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError(f"{rel} is not a regular file or directory")
        if path.is_dir() or rel == "run-id":
            continue
        match = _KEPT_PATH.match(rel)
        if match is None:
            raise ValueError(f"{rel} is outside the kept layout")
        if match["lane"] not in lanes:
            raise ValueError(f"{rel} is in lane {match['lane']!r}, not an engine's")
        spec = moments.spec_for(match["event"])
        if spec is None or spec.stage is not Stage.merits or spec.moment.value != match["moment"]:
            raise ValueError(f"{rel} is not the {match['moment']!r} merits moment's event")
        if match["predictor"] is not None and (
            match["run"] != run_id or match["name"] not in KEPT_FORECAST_FILES
        ):
            raise ValueError(f"{rel} is not one of this run's forecast files")
        body = _read_capped(path)
        count, total = count + 1, total + len(body)
        if count > KEPT_MAX_FILES or total > KEPT_MAX_TOTAL_BYTES:
            raise ValueError("the kept tree is larger than any merits replay keeps")
        event = (match["lane"], match["moment"], f"{match['court']}/{match['docket']}")
        if match["predictor"] is None:
            events[(*event, match["event"])] = body
        else:
            cells[(*event, match["event"], match["predictor"])][match["name"]] = body
    return cells, events


def _forecast(
    key: _CellKey,
    found: Mapping[str, bytes],
    run_id: str,
    event_file: bytes | None,
    predictors: Mapping[str, str] | None,
) -> KeptForecast:
    lane, moment, case_id, event_id, predictor_id = key
    where = f"{lane}/{moment}/{case_id}/{event_id}/{predictor_id}"
    if "prediction.json" not in found:
        raise ValueError(f"{where}: no prediction")
    prediction = Prediction.model_validate_json(found["prediction.json"])
    actual = (prediction.case_id, prediction.event_id, prediction.predictor_id, prediction.run_id)
    if actual != (case_id, event_id, predictor_id, run_id):
        raise ValueError(f"{where}: prediction names {actual}")
    engine = str(prediction.engine)
    if lane not in {"stub", engine}:
        raise ValueError(f"{where}: ran on {engine}")
    # A stub lane stamps every predictor with one engine, so it is held to the id alone.
    configured = None if predictors is None else predictors.get(predictor_id)
    if predictors is not None and (configured is None or lane not in {"stub", configured}):
        raise ValueError(f"{where}: not a configured predictor on {engine}")
    opened_at = None
    if event_file is not None:
        opened_at = PredictableEvent.model_validate(load_yaml(event_file.decode())).opened_at
    return KeptForecast(
        lane=lane,
        moment=Moment(moment),
        case_id=case_id,
        event_id=event_id,
        opened_at=opened_at,
        prediction=prediction,
        files=found,
    )


def read_kept_run(
    root: Path, *, allow_stub: bool = False, predictors: Mapping[str, str] | None = None
) -> KeptRun:
    """The kept tree at ``root``, refused whole if any entry falls outside its layout.

    Every entry must be a directory or a regular file within the per-file cap,
    the tree within :data:`KEPT_MAX_FILES` and :data:`KEPT_MAX_TOTAL_BYTES`,
    and every file the ``run-id`` or a path the keep step writes: an event
    directory named for the merits moment its path says, each forecast under
    this run's id in an engine's own lane, and each ``prediction.json`` the
    run's, for its own case, event and lane, and (with ``predictors``, id to
    engine) a configured predictor on that engine. One predictor kept twice at
    one event is refused. A stub lane is refused unless ``allow_stub`` (a free
    rehearsal also uploads the artifact). The kept ``event.yaml`` contributes
    its ``opened_at`` alone, which :func:`calibration_documents` checks against
    the cutoff it rebuilds; the overlay rebuilds the definition itself.

    What it does not check is the content of the forecast documents and
    ``flags.json``, and the harness stamps a kept ``prediction.json`` may
    carry: those are what a judge grades, as calibration evidence only, and a
    caller validates the overlay before it is graded.
    """
    run_file = root / "run-id"
    run_id = _read_capped(run_file).decode().strip()
    if not _RUN_ID.match(run_id):
        raise ValueError(f"{run_file} does not hold a run id")
    lanes = _ENGINES | {"stub"} if allow_stub else _ENGINES
    cells, events = _walk(root, run_id, lanes)
    forecasts = [
        _forecast(key, found, run_id, events.get(key[:4]), predictors)
        for key, found in sorted(cells.items())
    ]
    seen: set[tuple[Moment, str, str, str]] = set()
    for forecast in forecasts:
        cell = (
            forecast.moment,
            forecast.case_id,
            forecast.event_id,
            forecast.prediction.predictor_id,
        )
        if cell in seen:
            raise ValueError(f"{'/'.join(map(str, cell))}: kept in more than one lane")
        seen.add(cell)
    return KeptRun(run_id=run_id, forecasts=forecasts)


def _draw_key(case_id: str) -> str:
    return hashlib.sha256(f"{CALIBRATION_SEED}\0{case_id}".encode()).hexdigest()


def calibration_documents(
    kept: KeptRun,
    cases: Sequence[MeritsReplayCase],
    *,
    moment: Moment = DEFAULT_CALIBRATION_MOMENT,
    limit: int = DEFAULT_CALIBRATION_CASES,
) -> list[KeptForecast]:
    """Up to ``limit`` cases' kept forecasts at ``moment``, every predictor of each.

    ``cases`` is the population the overlay may grade (the caller's Terms), so
    a kept forecast for any other case is left out, as is one whose case has no
    cutoff at that moment and event, or one whose kept event opened on another
    day than the cutoff rebuilt now (the corpus moved, and the cell graded
    would not be the cell that ran). Cases are taken whole, in an order fixed
    by a salted hash of the case id, and only those holding a forecast with a
    document to grade.
    """
    cutoffs = {
        (case.case_id, cut.event_id): cut
        for case in cases
        for cut in case.cutoffs
        if cut.moment is moment
    }
    by_case: dict[str, list[KeptForecast]] = defaultdict(list)
    for forecast in kept.forecasts:
        cut = cutoffs.get((forecast.case_id, forecast.event_id))
        doc = forecast.prediction.predicted_reasoning_doc
        if forecast.moment is not moment or cut is None or doc not in forecast.files:
            continue
        if forecast.opened_at is not None and forecast.opened_at != cut.opened_at:
            continue  # the corpus moved since the replay: not the cell that ran
        by_case[forecast.case_id].append(forecast)
    chosen = sorted(by_case, key=_draw_key)[:limit]
    return [
        forecast
        for case_id in sorted(chosen)
        for forecast in sorted(by_case[case_id], key=lambda f: f.prediction.predictor_id)
    ]


def write_calibration_overlay(
    conn: corpus.ReadConnection,
    documents: Sequence[KeptForecast],
    cases: Sequence[MeritsReplayCase],
    data_root: Path,
    *,
    ledger: Path | None = None,
) -> list[PilotDocument]:
    """Lay ``documents`` into ``data_root`` as resolved merits events; return the sample.

    Per event: its definition, rebuilt from the replay case's own cutoff and
    marked resolved; its outcome, built from the corpus row the way the cascade
    builds a decided merits event's; and each predictor's kept forecast files
    under ``predictions/<predictor>/<run>/``. An event the tree already holds
    anything for is refused, so an overlay never sits beside committed
    forecasts or a committed outcome, and so is one ``ledger`` (the committed
    ledger) holds, so the overlay can be laid into a checkout of it; every
    event is checked before the first is written, so a refusal leaves the tree
    as it was.
    """
    by_id = {case.case_id: case for case in cases}
    events: dict[tuple[str, str], list[KeptForecast]] = defaultdict(list)
    for forecast in documents:
        events[(forecast.case_id, forecast.event_id)].append(forecast)
    planned = []
    for (case_id, event_id), forecasts in sorted(events.items()):
        case = by_id[case_id]
        court, docket = case_id.split("/")
        paths = CasePaths(data_root, court, int(docket)).event(event_id)
        if paths.base.exists():
            raise ValueError(f"{case_id} {event_id}: the tree already holds this event")
        if (
            ledger is not None
            and CasePaths(ledger, court, int(docket)).event(event_id).base.exists()
        ):
            raise ValueError(f"{case_id} {event_id}: the committed ledger holds this event")
        cut = next((c for c in case.cutoffs if c.event_id == event_id), None)
        if cut is None:
            raise ValueError(f"{case_id} {event_id}: no replay cutoff for this event")
        row = corpus.get_row(conn, case_id)
        if row is None:
            raise ValueError(f"{case_id}: no corpus row")
        planned.append((case, cut, row, paths, forecasts))
    sample: list[PilotDocument] = []
    for case, cut, row, paths, forecasts in planned:
        case_id, event_id = case.case_id, cut.event_id
        write_yaml(paths.event_file, replay_event(case, cut, resolved=True))
        write_json(
            paths.outcome,
            build_merits_outcome(
                case_id,
                event_id,
                case.judgment,
                case.decided,
                distribution_count=row.distribution_count,
                cvsg_date=row.cvsg_date,
                source=row.citations[0] if row.citations else None,
                decision_method=known_decision_method(row.merits_decision_method),
            ),
        )
        for forecast in forecasts:
            prediction = forecast.prediction
            run_dir = paths.prediction_dir(prediction.predictor_id, prediction.run_id)
            run_dir.mkdir(parents=True)
            for name, body in sorted(forecast.files.items()):
                run_dir.joinpath(name).write_bytes(body)
            doc = prediction.predicted_reasoning_doc
            assert doc is not None  # calibration_documents keeps only documented cells
            sample.append(
                PilotDocument(
                    case_id=case_id,
                    event_id=event_id,
                    stage=Stage.merits,
                    predictor_id=prediction.predictor_id,
                    run_id=prediction.run_id,
                    engine=Engine(prediction.engine),
                    path=run_dir / doc,
                )
            )
    return sample
