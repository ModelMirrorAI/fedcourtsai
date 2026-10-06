"""The release's sensitivity lines: one disclosed departure from the board at a time.

``fedcourts release-sensitivity`` reads this. A sensitivity line is the same
figure the frozen board publishes, recomputed with exactly one disclosed
departure from the registered computation. It is a disclosure, never a result:
the registered figure stays the headline, and the lines are never stacked into
a second one. Every figure here is the board's own, rebuilt by
:func:`fedcourtsai.leaderboard.build_leaderboard` over the same stratified
cells (:func:`fedcourtsai.store.stratify`, frozen scope) — so accuracy, the
realized floor, the lift, population skill (a ratio of sums), the grant
comparison and ``complete_grid_by_band`` are computed exactly as the board
computes them, and the registered headline is the board itself. Three blocks:

1. **Exact-pool anchor.** Each skill-scored cert grading's prior-Term baseline
   is taken from the exact pool ``fedcourts segment-anchors`` computes for the
   scored prediction's ``(term, band)`` instead of the judge-recorded
   ``segment_base_rate``. The pool is read from the statpack build **the
   grading read**: the pack committed at the grading's harness-stamped
   ``process_version.pipeline_sha`` (the checkout the evaluate run graded on),
   pooled under that same checkout's lookback. A fill-time pool would fold the
   still-resolving Term's build drift into what is reported as transcription.
   The block also reports the transcription spread — recorded against exact —
   per judge and per docket Term, over the skill-scored cert cells the line
   recomputes and over the registered cohort's graded cert cells.
2. **Rule 20 petitions excluded.** Extraordinary-writ petitions are identified
   by the docket's opening petition entry in the stored live snapshot
   (:func:`opening_petition`), never by docket form, and every board cell on
   such a case is dropped.
3. **Post-conference first forecasts excluded.** The events whose first
   forward, frozen-scope cell — by the harness ``run_id``, never the
   agent-written ``created_at`` — ran on or after the day the conference that
   actually considered the petition sat (:func:`considering_conference`), and
   every board cell on them is dropped.

Read-only and offline over the ledger: the corpus supplies only the payloads
(blocks 2 and 3) and git supplies only the statpack builds (block 1). Nothing
here writes anything, and no figure here reaches the board.
"""

from __future__ import annotations

import math
import os
import re
import subprocess
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal, Protocol

import yaml

from .config import TRACKING_FILENAME, SalienceConfig
from .ids import parse_run_id
from .integrity import StratifiedCell
from .leaderboard import (
    CellSkill,
    EvaluationKey,
    build_leaderboard,
    cell_facts,
    skill_components,
    stage_moment_key,
)
from .paths import CasePaths
from .pipeline import asof, cert_signals
from .pipeline.base_rates import _pooled_band_rate
from .pipeline.moments import first_moment
from .process_version import is_frozen
from .schemas import (
    Evaluation,
    Leaderboard,
    LeaderboardStratum,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    Stage,
    StatPack,
)
from .serialize import read_model
from .store import iter_predicted_events, normalized_moment, normalized_stage, scored_prediction

#: The ranked board's block key: cert's first declared moment.
RANKED_ARM = stage_moment_key(Stage.cert, first_moment(Stage.cert))

#: The per-stratum figures each block can print — the per-band fields the
#: release write-up's section 3 reads off the board, in its order.
ALL_FIELDS: tuple[str, ...] = (
    "events_scored",
    "evaluations",
    "accuracy_events_scored",
    "event_accuracy",
    "event_always_deny_accuracy",
    "event_accuracy_lift",
    "accuracy",
    "accuracy_scored",
    "always_deny_accuracy",
    "accuracy_lift",
    "population_brier_skill_score",
    "skill_scored",
    "grants_expected",
    "grants_expected_scored",
    "grants_realized_expected_scored",
    "grants_realized",
)

#: Block 1 varies only the skill baseline, so only skill can move.
SKILL_FIELDS: tuple[str, ...] = ("events_scored", "population_brier_skill_score", "skill_scored")

#: Block 2's figures: headline accuracy (per petition), its floor and lift, and skill.
ACCURACY_SKILL_FIELDS: tuple[str, ...] = (
    "events_scored",
    "accuracy_events_scored",
    "event_accuracy",
    "event_always_deny_accuracy",
    "event_accuracy_lift",
    "population_brier_skill_score",
    "skill_scored",
)

#: A recorded rate within this of the exact pool is a transcription of it: half
#: a unit in the sixth decimal, the precision committed gradings record.
EXACT_TOLERANCE = 5e-7

#: A recorded rate deviating from the exact pool by more than this (relative)
#: is counted separately in the spread.
LARGE_DEVIATION = 0.01

#: The repository paths the statpack build and its lookback are read from at a
#: grading's checkout.
STATPACK_PATH = "metrics/statpack.json"
TRACKING_PATH = f"config/{TRACKING_FILENAME}"

#: The docket's opening petition entry: "Petition for a writ of … filed".
_PETITION_ENTRY_RE = re.compile(
    r"^\s*petition\s+for\s+(?:an?\s+)?(?P<what>[^.(]*?\bwrit\b[^.(]*?)\s+filed\b", re.I
)
#: The extraordinary writs of the Court's Rule 20.
RULE_20_WRITS: tuple[str, ...] = ("mandamus", "prohibition", "habeas corpus")
#: A call for response: takes a petition off the conference it was distributed for.
_RESPONSE_REQUESTED_RE = re.compile(r"^\s*response\s+requested\b", re.I)
#: A bare reschedule entry: takes a petition off the conference it was distributed for.
_RESCHEDULED_RE = re.compile(r"^\s*rescheduled\b", re.I)

#: A case's latest live payload and the day it was stored, or ``None``.
PayloadReader = Callable[[str], tuple[date, Mapping[str, Any]] | None]


class ReleaseSensitivityError(RuntimeError):
    """An input the command cannot read honestly (a git failure, a shallow clone)."""


# ---------------------------------------------------------------------------
# Statpack builds
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StatpackBuild:
    """The statpack one checkout carried, with the lookback that checkout pooled under."""

    #: The commit that last wrote ``metrics/statpack.json`` at or before the checkout.
    build_commit: str
    #: The pack's git blob id — the build's identity, shared by every checkout carrying it.
    blob: str
    lookback: int
    statpack: StatPack


class BuildSource(Protocol):
    """Resolves a grading's checkout commit to the statpack build it read."""

    def build_at(self, pipeline_sha: str) -> StatpackBuild | None: ...


def _git(repo: Path, *args: str) -> str:
    """Run a read-only git command in ``repo``; a failure raises.

    An inherited ``GIT_DIR`` / ``GIT_WORK_TREE`` would override ``-C``, so both
    are dropped.
    """
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    try:
        done = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else exc
        raise ReleaseSensitivityError(f"git {' '.join(args[:2])} failed: {detail}") from exc
    return done.stdout


class GitBuildSource:
    """Statpack builds read from the repository's history, one parse per build.

    A grading's checkout is its ``process_version.pipeline_sha``; the build it
    read is ``metrics/statpack.json`` at that commit, and its lookback is
    ``salience.base_rate_lookback_terms`` in the same commit's
    ``config/tracking.yaml``. A commit the clone does not hold resolves to
    ``None`` — the caller counts it rather than substituting another build.
    """

    def __init__(self, repo: Path) -> None:
        if _git(repo, "rev-parse", "--is-shallow-repository").strip() != "false":
            raise ReleaseSensitivityError(
                "the checkout is a shallow clone, which cannot read the statpack each "
                "grading's checkout carried; fetch full history first"
            )
        self.repo = repo
        self._by_sha: dict[str, StatpackBuild | None] = {}
        self._by_blob: dict[tuple[str, int], StatpackBuild] = {}

    def build_at(self, pipeline_sha: str) -> StatpackBuild | None:
        if pipeline_sha not in self._by_sha:
            self._by_sha[pipeline_sha] = self._read(pipeline_sha)
        return self._by_sha[pipeline_sha]

    def _read(self, sha: str) -> StatpackBuild | None:
        try:
            _git(self.repo, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}")
            blob = _git(self.repo, "rev-parse", f"{sha}:{STATPACK_PATH}").strip()
        except ReleaseSensitivityError:
            return None
        try:
            tracking = yaml.safe_load(_git(self.repo, "show", f"{sha}:{TRACKING_PATH}")) or {}
        except ReleaseSensitivityError:
            tracking = {}
        lookback = SalienceConfig.model_validate(
            tracking.get("salience", {})
        ).base_rate_lookback_terms
        key = (blob, lookback)
        if key not in self._by_blob:
            build_commit = _git(self.repo, "log", "-1", "--format=%H", sha, "--", STATPACK_PATH)
            self._by_blob[key] = StatpackBuild(
                build_commit=build_commit.strip(),
                blob=blob,
                lookback=lookback,
                statpack=StatPack.model_validate_json(_git(self.repo, "cat-file", "blob", blob)),
            )
        return self._by_blob[key]


# ---------------------------------------------------------------------------
# Docket readings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OpeningPetition:
    """The docket's opening petition entry and the writ it names."""

    filed: date | None
    text: str
    writ: Literal["certiorari", "rule-20", "ambiguous", "other"]


def opening_petition(payload: Mapping[str, Any]) -> OpeningPetition | None:
    """The first "Petition for a writ of … filed" entry, classified by its writ.

    The opening *petition* entry rather than the first entry of all: an
    application to extend the time to file precedes the petition on many
    dockets and names no writ of its own. ``rule-20`` names a writ of mandamus,
    prohibition or habeas corpus and no certiorari; ``ambiguous`` names both;
    ``other`` names neither. ``None`` where no such entry is disclosed.
    """
    for text, raw in cert_signals.proceedings_entries(payload):
        match = _PETITION_ENTRY_RE.search(text)
        if match is None:
            continue
        what = match.group("what").lower()
        extraordinary = any(writ in what for writ in RULE_20_WRITS)
        certiorari = "certiorari" in what
        writ: Literal["certiorari", "rule-20", "ambiguous", "other"]
        if extraordinary and certiorari:
            writ = "ambiguous"
        elif extraordinary:
            writ = "rule-20"
        elif certiorari:
            writ = "certiorari"
        else:
            writ = "other"
        return OpeningPetition(filed=cert_signals.entry_date(raw), text=text.strip(), writ=writ)
    return None


def _docket_number(payload: Mapping[str, Any]) -> str | None:
    """The payload's docket number, without the trailing markers the Court appends.

    The live ``CaseNumber`` carries flags such as ``*** CAPITAL CASE ***`` after
    the number itself; the number is its first token.
    """
    raw = str(payload.get("CaseNumber") or "").split()
    return raw[0] if raw else None


ConferenceReading = Literal["sat", "ahead", "off", "undistributed", "unknown"]


def considering_conference(
    payload: Mapping[str, Any], payload_date: date, run_day: date
) -> tuple[date | None, ConferenceReading]:
    """The earliest conference that sat on the petition on or before ``run_day``, if any.

    Every conference a DISTRIBUTED entry filed on or before ``run_day`` names
    is a candidate, read from the docket entries and never from the current
    ``distributed_for_conference`` column. A candidate on or before the run
    **sat on the petition** unless, between its distribution entry and its own
    day, the docket shows the petition taken off it: a call for response
    ("Response Requested"), a bare "Rescheduled", or a DISTRIBUTED entry naming
    a different conference (a reschedule by redistribution). A petition taken
    off a conference before it sat was never considered there. A relist —
    redistribution *after* a conference sat — leaves that conference sat, so a
    first forecast made after a relist is after the conference that considered
    the petition.

    Returns the earliest such conference and ``"sat"`` (a cell run on the
    conference day counts as after it). Otherwise the reading says why not:
    ``"unknown"`` — a candidate on or before the run is after the day the
    payload was stored, so whether something took it off cannot be read;
    ``"off"`` — every candidate on or before the run was taken off;
    ``"ahead"`` — the petition's conference is after the run; or
    ``"undistributed"`` — no distribution was disclosed by the run. Entries
    are day-grained, so an entry filed on the run day counts as before the run.
    ``run_day`` is the caller's: the commands pass the run's UTC day (the
    harness ``run_id``), which matches the Court's Eastern day for every cell
    run after 04:00 UTC (05:00 in winter).
    """
    entries = [
        (text, filed)
        for text, raw in cert_signals.proceedings_entries(payload)
        if (filed := cert_signals.entry_date(raw)) is not None
    ]
    distributions: list[tuple[date, date]] = []  # (filed, conference)
    for text, filed in entries:
        match = cert_signals.DISTRIBUTED_RE.search(text)
        if match is None or filed > run_day:
            continue
        conference = cert_signals.conference_date(match.group(1))
        if conference is not None:
            distributions.append((filed, conference))
    if not distributions:
        return None, "undistributed"
    past = sorted({c for _, c in distributions if c <= run_day})
    if not past:
        return asof.asof_conference(payload, run_day + timedelta(days=1)), "ahead"
    taken_off: date | None = None
    for conference in past:
        if payload_date < conference:
            return conference, "unknown"
        distributed = max(
            (f for f, c in distributions if c == conference and f < conference), default=None
        )
        if distributed is None:
            continue  # named only by an entry filed on or after its own day
        if any(
            distributed <= filed < conference
            and (
                _RESPONSE_REQUESTED_RE.search(text)
                or _RESCHEDULED_RE.search(text)
                or (
                    (match := cert_signals.DISTRIBUTED_RE.search(text)) is not None
                    and cert_signals.conference_date(match.group(1)) not in (None, conference)
                )
            )
            for text, filed in entries
        ):
            taken_off = taken_off or conference
            continue
        return conference, "sat"
    if any(c > run_day for _, c in distributions):
        return asof.asof_conference(payload, run_day + timedelta(days=1)), "ahead"
    return taken_off, "off"


# ---------------------------------------------------------------------------
# The board, rebuilt and projected
# ---------------------------------------------------------------------------


def _key(evaluation: Evaluation) -> EvaluationKey:
    return (
        evaluation.case_id,
        evaluation.event_id,
        evaluation.predictor_id,
        evaluation.evaluator_id,
        evaluation.run_id,
    )


def rebuild(
    cells: Sequence[StratifiedCell], data_root: Path, skills: Mapping[EvaluationKey, CellSkill]
) -> Leaderboard:
    """The frozen board's aggregates over ``cells``, built as ``fedcourts leaderboard`` does."""
    keys = {_key(ev) for ev, _s, _st, _m in cells}
    return build_leaderboard(
        cells,
        skills={key: skill for key, skill in skills.items() if key in keys},
        facts=cell_facts(cells, data_root),
    )


def _stratum(stratum: LeaderboardStratum | None, fields: Sequence[str]) -> dict[str, Any] | None:
    if stratum is None:
        return None
    dumped = stratum.model_dump(mode="json")
    return {name: dumped.get(name) for name in fields}


def project(board: Leaderboard, fields: Sequence[str] = ALL_FIELDS) -> dict[str, Any]:
    """Each cert arm's per-predictor forward and per-band figures, keyed ``<stage>@<moment>``.

    The ranked board is :data:`RANKED_ARM`; every other cert-stage block (the
    CVSG arm among them) is its own arm, never pooled with it.
    """
    arms: dict[str, Any] = {
        RANKED_ARM: {
            "events_scored": board.events_scored,
            "complete_grid_by_band": board.complete_grid_by_band,
            "entries": {
                entry.predictor_id: {
                    "events_scored": entry.events_scored,
                    "evaluators": entry.evaluators,
                    "forward": _stratum(entry.forward, fields),
                    "by_band": {
                        band: _stratum(s, fields) for band, s in (entry.by_band or {}).items()
                    },
                }
                for entry in sorted(board.entries, key=lambda e: e.predictor_id)
            },
        }
    }
    for key, stage in sorted(board.stages.items()):
        if not key.startswith(f"{Stage.cert}@"):
            continue
        arms[key] = {
            "events_scored": stage.events_scored,
            "complete_grid_by_band": stage.complete_grid_by_band,
            "entries": {
                entry.predictor_id: {
                    "events_scored": entry.events_scored,
                    "evaluators": entry.evaluators,
                    "forward": _stratum(entry.forward, fields),
                    "by_band": {
                        band: _stratum(s, fields) for band, s in (entry.by_band or {}).items()
                    },
                }
                for entry in stage.entries
            },
        }
    return arms


# ---------------------------------------------------------------------------
# Block 1: the exact-pool anchor
# ---------------------------------------------------------------------------


@dataclass
class _Spread:
    """One group's transcription spread: recorded ``segment_base_rate`` vs the exact pool."""

    cells: int = 0
    exact: int = 0
    over_one_percent: int = 0
    deviations: list[float] = field(default_factory=list)
    largest_at: dict[str, Any] | None = None

    def add(self, recorded: float, exact: float, where: dict[str, Any]) -> None:
        deviation = abs(recorded - exact) / exact
        self.cells += 1
        self.exact += abs(recorded - exact) <= EXACT_TOLERANCE
        self.over_one_percent += deviation > LARGE_DEVIATION
        if not self.deviations or deviation > max(self.deviations):
            self.largest_at = where | {"recorded": recorded, "exact": exact}
        self.deviations.append(deviation)

    def render(self) -> dict[str, Any]:
        return {
            "cells": self.cells,
            "exact": self.exact,
            "max_relative_deviation": max(self.deviations) if self.deviations else None,
            "mean_relative_deviation": (
                sum(self.deviations) / len(self.deviations) if self.deviations else None
            ),
            "over_one_percent": self.over_one_percent,
            "largest_at": self.largest_at,
        }


def _spread(rows: Iterable[tuple[str, int, float, float, dict[str, Any]]]) -> dict[str, Any]:
    """Spread per judge, per judge and docket Term, and over all, from (judge, term, ...)."""
    total = _Spread()
    by_judge: dict[str, _Spread] = defaultdict(_Spread)
    by_judge_term: dict[str, dict[int, _Spread]] = defaultdict(lambda: defaultdict(_Spread))
    for judge, term, recorded, exact, where in rows:
        total.add(recorded, exact, where)
        by_judge[judge].add(recorded, exact, where)
        by_judge_term[judge][term].add(recorded, exact, where)
    return {
        "all": total.render(),
        "by_judge": {
            judge: by_judge[judge].render()
            | {
                "by_docket_term": {
                    str(term): s.render() for term, s in sorted(by_judge_term[judge].items())
                }
            }
            for judge in sorted(by_judge)
        },
    }


@dataclass(frozen=True)
class _Anchored:
    """One cert grading's recorded and exact anchor, where both can be read."""

    evaluation: Evaluation
    term: int
    recorded: float
    exact: float | None
    build: StatpackBuild | None
    reason: str | None


def _anchor(
    evaluation: Evaluation, prediction: Prediction | None, builds: BuildSource
) -> _Anchored | None:
    recorded = evaluation.segment_base_rate
    context = prediction.context if prediction is not None else None
    if recorded is None or context is None or context.term is None:
        return None
    if evaluation.base_rate_basis != "risk_set" or context.band is None:
        return _Anchored(evaluation, context.term, recorded, None, None, "not a frozen-band rate")
    if context.salience_version is None:
        return _Anchored(evaluation, context.term, recorded, None, None, "no salience version")
    sha = evaluation.process_version.pipeline_sha if evaluation.process_version else None
    build = builds.build_at(sha) if sha else None
    if build is None:
        return _Anchored(evaluation, context.term, recorded, None, None, "build not readable")
    exact = _pooled_band_rate(
        context.band,
        context.salience_version,
        context.term,
        build.statpack,
        lookback_terms=build.lookback,
        risk_set=True,
    )
    if exact is None or exact <= 0:
        return _Anchored(evaluation, context.term, recorded, None, build, "no exact pool")
    return _Anchored(evaluation, context.term, recorded, exact, build, None)


def exact_pool_anchor(
    cells: Sequence[StratifiedCell],
    data_root: Path,
    skills: Mapping[EvaluationKey, CellSkill],
    builds: BuildSource,
    registered: set[tuple[str, str]] | None,
) -> dict[str, Any]:
    """Block 1: skill against the exact pool of the build each grading read, plus the spread.

    The line's population is the board's own ``skill_scored`` cert cells, so
    each figure's ``skill_scored`` equals the registered one. A cell whose
    exact pool cannot be read keeps its recorded baseline and is counted in
    ``recorded_retained`` — never dropped, which would change the population.
    """
    cases_dir = data_root / "cases"
    outcomes: dict[tuple[str, str], Outcome] = {}
    adjusted = dict(skills)
    retained: list[dict[str, Any]] = []
    skill_rows: list[tuple[str, int, float, float, dict[str, Any]]] = []
    cohort_rows: list[tuple[str, int, float, float, dict[str, Any]]] = []
    builds_used: dict[str, dict[str, Any]] = {}
    cohort_unanchored: list[dict[str, Any]] = []
    for evaluation, _stratum_name, stage, _moment in cells:
        if stage != Stage.cert:
            continue
        key = _key(evaluation)
        skill = skills.get(key)
        scored_skill = skill is not None and skill.prior_term_baseline is not None
        in_cohort = registered is not None and (evaluation.case_id, evaluation.event_id) in (
            registered
        )
        if not scored_skill and not in_cohort:
            continue
        event_dir = cases_dir / evaluation.case_id / "events" / evaluation.event_id
        prediction = scored_prediction(
            event_dir, evaluation.predictor_id, evaluation.prediction_run_id
        )
        anchored = _anchor(evaluation, prediction, builds)
        where = {
            "case_id": evaluation.case_id,
            "event_id": evaluation.event_id,
            "predictor_id": evaluation.predictor_id,
            "evaluator_id": evaluation.evaluator_id,
        }
        if anchored is not None and anchored.build is not None and anchored.exact is not None:
            used = builds_used.setdefault(
                anchored.build.blob,
                {
                    "build_commit": anchored.build.build_commit,
                    "blob": anchored.build.blob,
                    "lookback": anchored.build.lookback,
                    "pipeline_shas": set(),
                    "gradings": 0,
                },
            )
            used["pipeline_shas"].add(
                evaluation.process_version.pipeline_sha if evaluation.process_version else None
            )
            used["gradings"] += 1
            row = (evaluation.evaluator_id, anchored.term, anchored.recorded, anchored.exact, where)
            if scored_skill:
                skill_rows.append(row)
            if in_cohort:
                cohort_rows.append(row)
        elif in_cohort and evaluation.segment_base_rate is not None:
            cohort_unanchored.append(
                where | {"reason": anchored.reason if anchored is not None else "no context"}
            )
        if not scored_skill:
            continue
        assert skill is not None  # scored_skill
        if anchored is None or anchored.exact is None:
            retained.append(
                where | {"reason": anchored.reason if anchored is not None else "no context"}
            )
            continue
        event_key = (evaluation.case_id, evaluation.event_id)
        if event_key not in outcomes:
            outcomes[event_key] = read_model(event_dir / "outcome.json", Outcome)
        baseline = (anchored.exact - outcomes[event_key].actual_granted) ** 2
        if baseline <= 0:
            retained.append(where | {"reason": "exact pool scores the outcome exactly"})
            continue
        adjusted[key] = CellSkill(
            brier=skill.brier,
            prior_term_baseline=baseline,
            realized_term_baseline=skill.realized_term_baseline,
        )
    board = rebuild(cells, data_root, adjusted)
    block = {
        "departure": (
            "each skill-scored cert grading's prior-Term baseline taken from the exact "
            "pool `segment-anchors` computes for the scored prediction's (docket term, "
            "band), read from the statpack build at the grading's "
            "process_version.pipeline_sha, instead of its recorded segment_base_rate"
        ),
        "recorded_retained": retained,
        "statpack_builds": [
            used | {"pipeline_shas": sorted(s for s in used["pipeline_shas"] if s)}
            for used in sorted(builds_used.values(), key=lambda u: str(u["build_commit"]))
        ],
        "transcription_spread": {
            "exact_tolerance": EXACT_TOLERANCE,
            "skill_scored_cert_cells": _spread(skill_rows),
            "registered_cohort_graded_cert_cells": (
                _spread(cohort_rows) | {"unanchored": cohort_unanchored}
                if registered is not None
                else None
            ),
        },
        "figures": project(board, SKILL_FIELDS),
    }
    return block


# ---------------------------------------------------------------------------
# Blocks 2 and 3: events excluded
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _EventInfo:
    case_id: str
    event_id: str
    stage: Stage | None
    moment: Moment | None
    resolved: bool
    frozen_forward_runs: tuple[str, ...]


def _cert_events(data_root: Path) -> list[_EventInfo]:
    """Every cert-stage event carrying a frozen-scope prediction, with its forward runs."""
    found: list[_EventInfo] = []
    for ref in iter_predicted_events(data_root):
        court_id, _, docket = ref.case_id.partition("/")
        paths = CasePaths(data_root, court_id, int(docket)).event(ref.event_id)
        if not paths.event_file.is_file():
            continue
        event = read_model(paths.event_file, PredictableEvent)
        stage = normalized_stage(event.kind, event.stage)
        if stage != Stage.cert:
            continue
        frozen = [
            prediction
            for path in sorted(paths.predictions_dir.glob("*/*/prediction.json"))
            if is_frozen((prediction := read_model(path, Prediction)).process_version)
        ]
        if not frozen:
            continue
        forward = sorted(
            p.run_id for p in frozen if p.context is not None and p.context.mode == "forward"
        )
        moment = normalized_moment(stage, event.moment)
        found.append(
            _EventInfo(
                case_id=ref.case_id,
                event_id=ref.event_id,
                stage=stage,
                moment=moment,
                resolved=paths.outcome.is_file(),
                frozen_forward_runs=tuple(forward),
            )
        )
    return found


def _graded(cells: Sequence[StratifiedCell]) -> dict[tuple[str, str], list[Evaluation]]:
    graded: dict[tuple[str, str], list[Evaluation]] = defaultdict(list)
    for evaluation, _s, _st, _m in cells:
        graded[(evaluation.case_id, evaluation.event_id)].append(evaluation)
    return graded


def _without(
    cells: Sequence[StratifiedCell], drop: Callable[[Evaluation], bool]
) -> list[StratifiedCell]:
    return [cell for cell in cells if not drop(cell[0])]


def rule_20_excluded(
    cells: Sequence[StratifiedCell],
    data_root: Path,
    skills: Mapping[EvaluationKey, CellSkill],
    events: Sequence[_EventInfo],
    payloads: PayloadReader,
    registered: set[tuple[str, str]] | None,
) -> dict[str, Any]:
    """Block 2: the board without the cases whose opening petition is a Rule 20 writ."""
    graded = _graded(cells)
    by_case: dict[str, list[_EventInfo]] = defaultdict(list)
    for info in events:
        by_case[info.case_id].append(info)
    identified: list[dict[str, Any]] = []
    flagged: list[dict[str, Any]] = []
    unclassified: list[dict[str, Any]] = []
    for case_id in sorted(by_case):
        found = payloads(case_id)
        petition = opening_petition(found[1]) if found is not None else None
        if petition is None:
            unclassified.append(
                {
                    "case_id": case_id,
                    "reason": "no live payload" if found is None else "no opening petition entry",
                }
            )
            continue
        if petition.writ == "certiorari":
            continue
        assert found is not None
        row = {
            "case_id": case_id,
            "docket_number": _docket_number(found[1]),
            "writ": petition.writ,
            "opening_entry": petition.text,
            "opening_entry_filed": petition.filed.isoformat() if petition.filed else None,
            "payload_date": found[0].isoformat(),
            "events": [
                {
                    "event_id": info.event_id,
                    "arm": stage_moment_key(info.stage, info.moment),
                    "resolved": info.resolved,
                    "graded_cells": len(graded.get((case_id, info.event_id), [])),
                    "registered": (
                        (case_id, info.event_id) in registered if registered is not None else None
                    ),
                }
                for info in by_case[case_id]
            ],
        }
        (identified if petition.writ == "rule-20" else flagged).append(row)
    excluded = {row["case_id"] for row in identified}
    kept = _without(cells, lambda ev: ev.case_id in excluded)
    return {
        "departure": (
            "every board cell on a case whose opening petition entry names a writ of "
            "mandamus, prohibition or habeas corpus removed"
        ),
        "cases_scanned": len(by_case),
        "identified": identified,
        "not_certiorari_not_rule_20": flagged,
        "unclassified": unclassified,
        "board_cells_removed": len(cells) - len(kept),
        "figures": project(rebuild(kept, data_root, skills), ACCURACY_SKILL_FIELDS),
    }


def _scored_after_conference(
    cells: Sequence[StratifiedCell],
    members: set[tuple[str, str]],
    payloads: PayloadReader,
) -> list[dict[str, Any]]:
    """Board cells outside the subset whose *scored* run postdates its considering conference."""
    outside: list[dict[str, Any]] = []
    for evaluation, _s, stage, moment in cells:
        run = evaluation.prediction_run_id
        if stage_moment_key(stage, moment) != RANKED_ARM or not run:
            continue
        if (evaluation.case_id, evaluation.event_id) in members:
            continue
        found = payloads(evaluation.case_id)
        if found is None:
            continue
        conference, reading = considering_conference(found[1], found[0], parse_run_id(run).date())
        if reading == "sat" and conference is not None:
            outside.append(
                {
                    "case_id": evaluation.case_id,
                    "event_id": evaluation.event_id,
                    "predictor_id": evaluation.predictor_id,
                    "evaluator_id": evaluation.evaluator_id,
                    "scored_run_id": run,
                    "considering_conference": conference.isoformat(),
                }
            )
    return outside


def _tally_by_conference(subset: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    """Per considering conference: events, and how many are resolved, graded and registered."""
    by_conference: dict[str, dict[str, int]] = {}
    for row in subset:
        tally = by_conference.setdefault(
            row["considering_conference"],
            {"events": 0, "resolved": 0, "graded": 0, "registered": 0},
        )
        tally["events"] += 1
        tally["resolved"] += bool(row["resolved"])
        tally["graded"] += row["graded_cells"] > 0
        tally["registered"] += bool(row["registered"])
    return dict(sorted(by_conference.items()))


def post_conference_excluded(
    cells: Sequence[StratifiedCell],
    data_root: Path,
    skills: Mapping[EvaluationKey, CellSkill],
    events: Sequence[_EventInfo],
    payloads: PayloadReader,
    registered: set[tuple[str, str]] | None,
    grant_list: date | None,
) -> dict[str, Any]:
    """Block 3: the board without the events first forecast after their considering conference.

    The population is the cert distribution-moment events carrying a forward,
    frozen-scope cell — a CVSG cell is cut at the invitation and an interim
    cell names no conference, so neither arm is read this way. The first
    forward cell is the earliest harness ``run_id``; the conference it is read
    against is :func:`considering_conference`'s. Because the board scores each
    predictor's newest cell rather than its first, every board cell whose
    *scored* run postdates its own considering conference is checked too, and
    any outside the subset is named.
    """
    graded = _graded(cells)
    subset: list[dict[str, Any]] = []
    unreadable: list[dict[str, Any]] = []
    for info in events:
        if stage_moment_key(info.stage, info.moment) != RANKED_ARM:
            continue
        if not info.frozen_forward_runs:
            continue
        first = info.frozen_forward_runs[0]
        run_day = parse_run_id(first).date()
        found = payloads(info.case_id)
        if found is None:
            unreadable.append(
                {"case_id": info.case_id, "event_id": info.event_id, "reason": "no live payload"}
            )
            continue
        conference, reading = considering_conference(found[1], found[0], run_day)
        if reading == "unknown":
            unreadable.append(
                {
                    "case_id": info.case_id,
                    "event_id": info.event_id,
                    "reason": f"payload of {found[0]} predates the conference of {conference}",
                }
            )
            continue
        if reading != "sat":
            continue
        assert conference is not None
        key = (info.case_id, info.event_id)
        subset.append(
            {
                "case_id": info.case_id,
                "docket_number": _docket_number(found[1]),
                "event_id": info.event_id,
                "considering_conference": conference.isoformat(),
                "first_forward_run_id": first,
                "first_forward_day": run_day.isoformat(),
                "after_grant_list": (run_day > grant_list) if grant_list is not None else None,
                "resolved": info.resolved,
                "graded_cells": len(graded.get(key, [])),
                "registered": key in registered if registered is not None else None,
                "payload_date": found[0].isoformat(),
            }
        )
    members = {(row["case_id"], row["event_id"]) for row in subset}
    outside = _scored_after_conference(cells, members, payloads)
    by_conference = _tally_by_conference(subset)
    kept = _without(cells, lambda ev: (ev.case_id, ev.event_id) in members)
    graded_members = sum(1 for row in subset if row["graded_cells"])
    return {
        "departure": (
            "every board cell on a cert distribution event whose first forward "
            "frozen-scope cell (harness run_id) ran on or after the day the conference "
            "that considered the petition sat removed"
        ),
        "grant_list": grant_list.isoformat() if grant_list is not None else None,
        "events": len(subset),
        "resolved": sum(1 for row in subset if row["resolved"]),
        "graded": graded_members,
        "registered": (
            sum(1 for row in subset if row["registered"]) if registered is not None else None
        ),
        "by_conference": by_conference,
        "subset": sorted(subset, key=lambda r: (r["considering_conference"], r["case_id"])),
        "not_after_grant_list": [row for row in subset if row["after_grant_list"] is False],
        "unreadable": unreadable,
        "scored_after_conference_outside_subset": outside,
        "lines_equal_headline": graded_members == 0,
        "board_cells_removed": len(cells) - len(kept),
        "figures": project(rebuild(kept, data_root, skills), ALL_FIELDS),
    }


# ---------------------------------------------------------------------------
# The command's body
# ---------------------------------------------------------------------------


def release_sensitivity(
    cells: Sequence[StratifiedCell],
    data_root: Path,
    statpack: StatPack | None,
    *,
    builds: BuildSource,
    payloads: PayloadReader,
    registered: set[tuple[str, str]] | None = None,
    grant_list: date | None = None,
    committed_board: Leaderboard | None = None,
) -> dict[str, Any]:
    """The registered headline and the three sensitivity blocks, as one JSON-ready dict.

    ``cells`` is the frozen board's stratified pass and ``statpack`` the
    fill-time pack the board reads — the same two inputs ``fedcourts
    leaderboard`` builds from — so the registered headline is the board.
    ``committed_board``, when given, is checked against it: a ``false`` means
    the committed ``metrics/leaderboard.json`` is not this ledger's board and
    nothing here may be quoted beside it.
    """
    skills = skill_components(cells, data_root, statpack)
    registered_board = rebuild(cells, data_root, skills)
    headline = project(registered_board)
    cached: dict[str, tuple[date, Mapping[str, Any]] | None] = {}

    def read(case_id: str) -> tuple[date, Mapping[str, Any]] | None:
        if case_id not in cached:
            cached[case_id] = payloads(case_id)
        return cached[case_id]

    events = _cert_events(data_root)
    anchor = exact_pool_anchor(cells, data_root, skills, builds, registered)
    return {
        "registered_headline": {
            "matches_committed_board": (
                project(committed_board) == headline if committed_board is not None else None
            ),
            "figures": headline,
        },
        "blocks": {
            "exact_pool_anchor": anchor,
            "rule_20_excluded": rule_20_excluded(
                cells, data_root, skills, events, read, registered
            ),
            "post_conference_first_forecasts_excluded": post_conference_excluded(
                cells, data_root, skills, events, read, registered, grant_list
            ),
        },
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:+.4f}" if not math.isnan(value) else "nan"
    return str(value)


def render_table(result: Mapping[str, Any]) -> list[str]:
    """The human table: per arm, predictor and band, the registered figure beside each line."""
    headline = result["registered_headline"]["figures"]
    blocks = result["blocks"]
    lines: list[str] = []
    columns = (
        ("anchor skill", blocks["exact_pool_anchor"]["figures"], "population_brier_skill_score"),
        ("-R20 acc", blocks["rule_20_excluded"]["figures"], "event_accuracy"),
        ("-R20 skill", blocks["rule_20_excluded"]["figures"], "population_brier_skill_score"),
        (
            "-post acc",
            blocks["post_conference_first_forecasts_excluded"]["figures"],
            "event_accuracy",
        ),
        (
            "-post skill",
            blocks["post_conference_first_forecasts_excluded"]["figures"],
            "population_brier_skill_score",
        ),
    )
    for arm, figures in headline.items():
        lines.append(f"{arm} (events scored {figures['events_scored']})")
        for predictor, entry in figures["entries"].items():
            rows = [("forward", entry["forward"]), *entry["by_band"].items()]
            for band, stratum in rows:
                if stratum is None:
                    continue
                parts = [
                    f"acc {_fmt(stratum['event_accuracy'])} "
                    f"(n={stratum['accuracy_events_scored']})",
                    f"skill {_fmt(stratum['population_brier_skill_score'])} "
                    f"(n={stratum['skill_scored']})",
                ]
                for label, block_figures, name in columns:
                    other = block_figures.get(arm, {}).get("entries", {}).get(predictor, {})
                    cut = (
                        other.get("forward")
                        if band == "forward"
                        else other.get("by_band", {}).get(band)
                    )
                    if cut is None:
                        parts.append(f"{label} —")
                        continue
                    n_name = "skill_scored" if "skill" in name else "accuracy_events_scored"
                    parts.append(f"{label} {_fmt(cut.get(name))} (n={cut.get(n_name)})")
                lines.append(f"  {predictor:<16} {band:<18} " + "; ".join(parts))
    return lines
