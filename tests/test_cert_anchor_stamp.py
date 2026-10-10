"""The harness-stamped cert skill anchor, and the board's re-pool of it.

From :data:`fedcourtsai.process_version.HARNESS_CERT_ANCHOR_FROM` on, a cert
grading whose scored prediction froze a band takes its whole skill record from
``stamp-cell``: the risk-set anchor pooled through the scorer's own pooler over
the frozen ``(band, salience_version, term)``, the Brier, the skill, the basis
pair, and the statpack build it read. An earlier label's grading keeps the
evaluator's transcription. These run the real command over seeded cells.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from fedcourtsai import process_version
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import _anchor_reproduces
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.pipeline.base_rates import statpack_digest
from fedcourtsai.pipeline.salience import SALIENCE_VERSION
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    Evaluation,
    EventKind,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
    Stage,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
    StatPackTermVersionSegments,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml

runner = CliRunner()

_EVENT = "evt-petition-disposition"
#: A salience version the rendered statpack table no longer shows: it survives
#: only in the Terms' `alt_segments`, which is the case a judge transcribing
#: `metrics/statpack.md` could not pool and recorded null for.
_OLD_VERSION = "sal-old"
#: The exact risk-set pool over the two prior Terms' `alt_segments` below:
#: (0.12 * 200 + 0.06 * 100) / 300.
_EXACT_POOL = 0.1


@pytest.fixture(autouse=True)
def _roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    write_json(tmp_path / "metrics" / "statpack.json", _statpack())
    return tmp_path / "data"


def _segment(band: str, rate: float, n: int) -> StatPackTermSegment:
    return StatPackTermSegment(
        band=band,
        prefix_est_grant_rate=rate,
        prefix_weighted_resolved=n,
        est_grant_rate=rate,
        weighted_resolved=n,
    )


def _term(term: int, alt_rate: float, alt_n: int) -> StatPackTerm:
    # The active version's slice is a decoy several-fold off the exact pool: a
    # transcription off the rendered table reads it, the version-pinned pooler
    # never does.
    return StatPackTerm(
        term=term,
        base_rates=BaseRateBucket(),
        salience_version=SALIENCE_VERSION,
        segments=[_segment("baseline", 0.9, 500)],
        alt_segments=[
            StatPackTermVersionSegments(
                salience_version=_OLD_VERSION, segments=[_segment("baseline", alt_rate, alt_n)]
            )
        ],
    )


def _statpack() -> StatPack:
    return StatPack(
        corpus_rows=1,
        terms=[
            # The case's own Term: never pooled for a 2026 docket.
            _term(2026, 0.5, 1000),
            _term(2025, 0.12, 200),
            _term(2024, 0.06, 100),
        ],
    )


def _seed(
    data_root: Path,
    docket: int,
    *,
    context: PredictionContext | None,
    recorded_rate: float | None = 0.071,
) -> EventPaths:
    """A cert cell graded against a denial, with a transcribed anchor of 7.1%."""
    event_paths = CasePaths(data_root, "scotus", docket).event(_EVENT)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=_EVENT,
            case_id=f"scotus/{docket}",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition disposition",
            opened_at=date(2026, 10, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id=f"scotus/{docket}",
            event_id=_EVENT,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 10, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-10-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=context,
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id=f"scotus/{docket}",
            event_id=_EVENT,
            resolved_at=date(2026, 10, 6),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    brier = 0.04
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id=f"scotus/{docket}",
            event_id=_EVENT,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 10, 7, tzinfo=UTC),
            correct=1,
            brier_score=brier,
            segment_base_rate=recorded_rate,
            base_rate_basis="risk_set" if recorded_rate is not None else None,
            brier_skill_score=(1 - brier / recorded_rate**2 if recorded_rate is not None else None),
            base_rate_statpack_digest="sha256:agent-invented",  # must not survive
        ),
    )
    return event_paths


def _frozen(band: str | None = "baseline", version: str | None = _OLD_VERSION) -> PredictionContext:
    return PredictionContext(
        mode="forward",
        snapshot_date=date(2026, 10, 1),
        signals_observable=True,
        distribution_count=1,
        band=band,
        salience_version=version,
        term=2026,
    )


def _stamp(docket: int) -> Result:
    return runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            str(docket),
            "--event",
            _EVENT,
            "--run-id",
            "RID",
            "--role",
            "evaluator",
            "--actor",
            "claude-judge",
            "--stamped-at",
            "2026-10-20T00:00:00Z",
            "--pipeline-sha",
            "sha-abc",
        ],
    )


def _stamped(event_paths: EventPaths) -> dict[str, object]:
    path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    loaded: dict[str, object] = json.loads(path.read_text())
    return loaded


def test_the_label_gate_opens_at_proc_v9() -> None:
    assert process_version.HARNESS_CERT_ANCHOR_FROM == "proc-v9"
    assert not process_version.harness_stamps_cert_anchor("proc-v8")
    assert process_version.harness_stamps_cert_anchor("proc-v9")
    assert process_version.harness_stamps_cert_anchor("proc-v10"), "numeric, not lexical"
    assert not process_version.harness_stamps_cert_anchor(None)
    assert not process_version.harness_stamps_cert_anchor("proc-v9-draft")


def test_from_proc_v9_the_stamp_writes_the_exact_pool_and_names_its_build(
    _roots: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The evaluator's transcription is replaced by the scorer's own pool — read
    off `alt_segments` for a band whose version the rendered table no longer
    shows — with the Brier, skill, basis pair, and statpack build beside it."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 1, context=_frozen())

    result = _stamp(1)

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] == pytest.approx(_EXACT_POOL)
    assert stamped["brier_score"] == pytest.approx(0.04)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.04 / _EXACT_POOL**2)
    assert stamped["base_rate_basis"] == "risk_set"
    assert stamped["base_rate_salience_version"] == _OLD_VERSION
    pack = read_model(tmp_path / "metrics" / "statpack.json", StatPack)
    assert stamped["base_rate_statpack_digest"] == statpack_digest(pack)
    # The overwrite of a different number is said, never silent.
    assert "segment_base_rate" in result.output


def test_before_proc_v9_the_cert_record_stays_the_evaluators(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An earlier label keeps the registered reading: the transcribed trio is
    untouched, and no build is named for a rate the harness did not pool."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v8")
    event_paths = _seed(_roots, 2, context=_frozen())

    result = _stamp(2)

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] == pytest.approx(0.071)
    assert stamped["base_rate_basis"] == "risk_set"
    assert stamped["base_rate_statpack_digest"] is None


def test_a_frozen_band_without_its_version_is_the_omission(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No version, no population: rate, basis, version, and skill are cleared
    together — never relabelled terminal — while the Brier still stamps."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 3, context=_frozen(version=None))

    result = _stamp(3)

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None
    assert stamped["base_rate_basis"] is None
    assert stamped["base_rate_salience_version"] is None
    assert stamped["brier_score"] == pytest.approx(0.04)


def test_a_prediction_with_no_frozen_band_keeps_the_evaluators_terminal_record(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The terminal fallback re-derives a band from the corpus row, a read the
    stamp does not make, so that record stays the evaluator's even from proc-v9."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 4, context=None)
    path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    write_json(
        path,
        read_model(path, Evaluation).model_copy(update={"base_rate_basis": "terminal"}),
    )

    result = _stamp(4)

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] == pytest.approx(0.071)
    assert stamped["base_rate_basis"] == "terminal"
    assert stamped["base_rate_salience_version"] == SALIENCE_VERSION
    assert stamped["base_rate_statpack_digest"] is None


def test_the_board_re_pools_a_stamped_anchor_against_the_build_it_names(
    _roots: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same build: a tampered rate is refused. Another build: the stamp stands.
    An earlier label's transcription is never re-pooled."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 5, context=_frozen())
    assert _stamp(5).exit_code == 0
    path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    record = read_model(path, Evaluation)
    pack = read_model(tmp_path / "metrics" / "statpack.json", StatPack)
    digest = statpack_digest(pack)
    cases = _roots / "cases"

    def reproduces(evaluation: Evaluation, pack_digest: str | None = digest) -> bool:
        return _anchor_reproduces(cases, evaluation, Stage.cert, pack, pack_digest, 10)

    assert reproduces(record)
    tampered = record.model_copy(update={"segment_base_rate": 0.071})
    assert not reproduces(tampered)
    assert reproduces(tampered, pack_digest="sha256:a-later-build")
    assert not reproduces(record.model_copy(update={"base_rate_statpack_digest": None}))
    assert record.process_version is not None
    earlier = ProcessVersion(
        label="proc-v8",
        digest=record.process_version.digest,
        stamped_at=record.process_version.stamped_at,
    )
    assert reproduces(tampered.model_copy(update={"process_version": earlier}))
    # No configured window: the check is not run.
    assert _anchor_reproduces(cases, tampered, Stage.cert, pack, digest, None)


def test_a_regrade_recomputes_a_harness_owned_cert_record_rather_than_refusing(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A correction that moves the binary refuses a re-grade of an
    evaluator-owned cert trio; a harness-owned one is recomputed whole, keyed
    on the label the record carries — not on the label in force at re-grade."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 6, context=_frozen())
    assert _stamp(6).exit_code == 0
    write_json(
        event_paths.outcome,
        read_model(event_paths.outcome, Outcome).model_copy(
            update={"actual_disposition": Disposition.granted, "actual_granted": 1}
        ),
    )
    # The label in force has moved on; the record's own label is what decides.
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v8")

    result = runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            "6",
            "--event",
            _EVENT,
            "--run-id",
            "RID",
            "--role",
            "evaluator",
            "--actor",
            "claude-judge",
            "--regrade",
        ],
    )

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["brier_score"] == pytest.approx(0.64)
    assert stamped["segment_base_rate"] == pytest.approx(_EXACT_POOL)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.64 / (1 - _EXACT_POOL) ** 2)
    assert stamped["process_version"]["label"] == "proc-v9"  # type: ignore[index]
