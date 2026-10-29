"""The harness-stamped cert skill anchor, and the board's re-pool of it.

From :data:`fedcourtsai.process_version.HARNESS_CERT_ANCHOR_FROM` on, a cert
grading whose scored prediction froze a band takes its whole skill record from
``stamp-cell``: the risk-set anchor pooled through the scorer's own pooler over
the frozen ``(band, salience_version, term)``, the Brier, the skill, the basis
pair, and the statpack build it read. An earlier label's grading keeps the
evaluator's transcription. From
:data:`fedcourtsai.process_version.PINNED_CERT_ANCHOR_FROM` on, the anchor is
the one the prediction's context froze at provisioning, wherever it carries
one. These run the real command over seeded cells.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from fedcourtsai import cli, process_version
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import _anchor_reproduces
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.pipeline.base_rates import freeze_cert_anchor, statpack_digest
from fedcourtsai.pipeline.salience import SALIENCE_VERSION
from fedcourtsai.schemas import (
    BaseRateBucket,
    CertAnchor,
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
from fedcourtsai.statpack_history import (
    StatpackRevision,
    find_statpack_build,
    git_statpack_history,
)

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
    assert stamped["base_rate_lookback_terms"] == 10  # config/tracking.yaml
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


def test_an_empty_pool_clears_the_anchor_and_names_no_build(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Band, version and Term all frozen, but no prior Term carries the band:
    no baseline, and no build named beside a rate that was never pooled."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    context = _frozen().model_copy(update={"term": 2024})
    event_paths = _seed(_roots, 7, context=context)

    result = _stamp(7)

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None
    assert stamped["base_rate_basis"] is None
    assert stamped["base_rate_statpack_digest"] is None
    assert stamped["base_rate_lookback_terms"] is None
    assert stamped["brier_score"] == pytest.approx(0.04)


def test_an_unreadable_statpack_clears_the_anchor_out_loud(
    _roots: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 8, context=_frozen())
    (tmp_path / "metrics" / "statpack.json").unlink()

    result = _stamp(8)

    assert result.exit_code == 0, result.output
    assert "no readable metrics/statpack.json" in result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] is None
    assert stamped["base_rate_basis"] is None
    assert stamped["base_rate_statpack_digest"] is None
    assert stamped["brier_score"] == pytest.approx(0.04)


def test_a_terminal_relabel_of_a_frozen_band_is_overwritten_and_said(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Before proc-v9 this mispairing fails the cell; from proc-v9 the harness
    owns the basis, so it is replaced by the risk-set pool — with a warning,
    since a discarded basis is not a number the numeric echo would catch."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 9, context=_frozen())
    path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    write_json(
        path,
        read_model(path, Evaluation).model_copy(update={"base_rate_basis": "terminal"}),
    )

    result = _stamp(9)

    assert result.exit_code == 0, result.output
    assert "base_rate_basis 'terminal'" in result.output
    stamped = _stamped(event_paths)
    assert stamped["base_rate_basis"] == "risk_set"
    assert stamped["segment_base_rate"] == pytest.approx(_EXACT_POOL)


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
        return _anchor_reproduces(cases, evaluation, Stage.cert, pack, pack_digest)

    assert reproduces(record)
    tampered = record.model_copy(update={"segment_base_rate": 0.071})
    assert not reproduces(tampered)
    assert reproduces(tampered, pack_digest="sha256:a-later-build")
    assert not reproduces(record.model_copy(update={"base_rate_statpack_digest": None}))
    assert not reproduces(record.model_copy(update={"base_rate_lookback_terms": None}))
    # The recorded window is the one re-pooled under: a one-Term window pools
    # 2025 alone (0.12), which the recorded 0.1 does not reproduce.
    assert not reproduces(record.model_copy(update={"base_rate_lookback_terms": 1}))
    assert record.process_version is not None
    earlier = ProcessVersion(
        label="proc-v8",
        digest=record.process_version.digest,
        stamped_at=record.process_version.stamped_at,
    )
    assert reproduces(tampered.model_copy(update={"process_version": earlier}))


def test_a_regrade_recomputes_a_harness_owned_cert_record_rather_than_refusing(
    _roots: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A correction that moves the binary refuses a re-grade of an
    evaluator-owned cert trio; a harness-owned one recomputes its Brier and
    skill, keyed on the label the record carries — not on the label in force
    at re-grade — over the anchor it was first stamped with, even after a
    statpack refresh would pool a different one."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v9")
    event_paths = _seed(_roots, 6, context=_frozen())
    assert _stamp(6).exit_code == 0
    first = _stamped(event_paths)
    # A refresh lands: the prior Term's rate moves.
    refreshed = _statpack().model_copy(
        update={"terms": [_term(2026, 0.5, 1000), _term(2025, 0.3, 200), _term(2024, 0.06, 100)]}
    )
    write_json(tmp_path / "metrics" / "statpack.json", refreshed)
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
    assert stamped["base_rate_statpack_digest"] == first["base_rate_statpack_digest"]
    assert stamped["base_rate_lookback_terms"] == first["base_rate_lookback_terms"]
    assert stamped["process_version"]["label"] == "proc-v9"  # type: ignore[index]


def _refreshed() -> StatPack:
    """A later build: the prior Term's rate moves, so a grading-time pool moves."""
    return _statpack().model_copy(
        update={"terms": [_term(2026, 0.5, 1000), _term(2025, 0.3, 200), _term(2024, 0.06, 100)]}
    )


@pytest.fixture(autouse=True)
def _history(monkeypatch: pytest.MonkeyPatch) -> list[StatpackRevision]:
    """The statpack's committed history the frozen-anchor check walks, newest first.

    One build, `_statpack()`, committed before every seeded prediction
    (`created_at` 2026-10-01); a test prepends later revisions.
    """
    revisions: list[StatpackRevision] = [
        (datetime(2026, 9, 1, tzinfo=UTC), _statpack().model_dump_json())
    ]
    monkeypatch.setattr(cli, "_statpack_history", lambda _root: list(revisions))
    return revisions


def _pinned(pack: StatPack | None = None) -> PredictionContext:
    """A frozen band carrying the anchor provisioning would have pooled from ``pack``."""
    context = _frozen()
    anchor = freeze_cert_anchor(context, pack or _statpack(), lookback_terms=10)
    return context.model_copy(update={"cert_anchor": anchor})


def test_the_pin_gate_opens_at_proc_v15() -> None:
    assert process_version.PINNED_CERT_ANCHOR_FROM == "proc-v15"
    assert not process_version.pins_cert_anchor("proc-v14")
    assert process_version.pins_cert_anchor("proc-v15")
    assert process_version.pins_cert_anchor("proc-v100"), "numeric, not lexical"
    assert not process_version.pins_cert_anchor(None)
    assert not process_version.pins_cert_anchor("proc-v15-draft")


def test_freezing_names_the_build_and_window_beside_the_pool() -> None:
    pack = _statpack()
    anchor = freeze_cert_anchor(_frozen(), pack, lookback_terms=10)
    assert anchor is not None
    assert anchor.rate == pytest.approx(_EXACT_POOL)
    assert anchor.statpack_digest == statpack_digest(pack)
    assert anchor.lookback_terms == 10
    # An empty pool keeps the build it came up empty against; no band, no record.
    empty = freeze_cert_anchor(_frozen().model_copy(update={"term": 2024}), pack, lookback_terms=10)
    assert empty is not None
    assert empty.rate is None
    assert freeze_cert_anchor(_frozen(band=None), pack, lookback_terms=10) is None


def test_from_proc_v15_a_refresh_after_provisioning_does_not_move_the_anchor(
    _roots: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _history: list[StatpackRevision],
) -> None:
    """The cell froze its anchor against the build in force at placement; a
    refresh lands before grading; the stamp finds the past build in history,
    verifies the frozen anchor against it, and copies it rather than
    re-pooling the pack now checked out."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v15")
    placed = _statpack()
    event_paths = _seed(_roots, 11, context=_pinned(placed))
    _history.insert(0, (datetime(2026, 10, 5, tzinfo=UTC), _refreshed().model_dump_json()))
    write_json(tmp_path / "metrics" / "statpack.json", _refreshed())

    result = _stamp(11)

    assert result.exit_code == 0, result.output
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] == pytest.approx(_EXACT_POOL)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.04 / _EXACT_POOL**2)
    assert stamped["base_rate_basis"] == "risk_set"
    assert stamped["base_rate_salience_version"] == _OLD_VERSION
    assert stamped["base_rate_statpack_digest"] == statpack_digest(placed)
    assert stamped["base_rate_statpack_digest"] != statpack_digest(_refreshed())
    assert stamped["base_rate_lookback_terms"] == 10


def _assert_cleared(stamped: dict[str, object]) -> None:
    assert stamped["segment_base_rate"] is None
    assert stamped["base_rate_basis"] is None
    assert stamped["base_rate_statpack_digest"] is None
    assert stamped["base_rate_lookback_terms"] is None
    assert stamped["brier_skill_score"] is None
    assert stamped["brier_score"] == pytest.approx(0.04)


@pytest.mark.parametrize(
    ("anchor", "reason"),
    [
        # A real build's digest beside a rate it does not pool to.
        (
            CertAnchor(rate=0.25, statpack_digest=statpack_digest(_statpack()), lookback_terms=10),
            "does not re-pool",
        ),
        # A digest no committed build carries.
        (
            CertAnchor(rate=0.25, statpack_digest="sha256:invented", lookback_terms=10),
            "no committed",
        ),
    ],
    ids=["tampered-rate", "unknown-digest"],
)
def test_a_frozen_anchor_that_does_not_verify_is_refused_out_loud(
    _roots: Path, monkeypatch: pytest.MonkeyPatch, anchor: CertAnchor, reason: str
) -> None:
    """`record/context.json` is reachable from the cell, so a frozen record is
    copied only where a committed build backs it; otherwise the anchor is
    cleared, never graded against."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v15")
    event_paths = _seed(_roots, 12, context=_frozen().model_copy(update={"cert_anchor": anchor}))

    result = _stamp(12)

    assert result.exit_code == 0, result.output
    assert "frozen cert anchor does not verify" in result.output
    assert reason in result.output
    _assert_cleared(_stamped(event_paths))


def test_a_build_committed_after_the_prediction_is_refused(
    _roots: Path, monkeypatch: pytest.MonkeyPatch, _history: list[StatpackRevision]
) -> None:
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v15")
    later = _refreshed()
    _history.insert(0, (datetime(2026, 10, 5, tzinfo=UTC), later.model_dump_json()))
    event_paths = _seed(_roots, 17, context=_pinned(later))

    result = _stamp(17)

    assert result.exit_code == 0, result.output
    assert "after the prediction" in result.output
    _assert_cleared(_stamped(event_paths))


def test_a_verified_frozen_empty_pool_clears_the_anchor_quietly(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v15")
    context = _frozen().model_copy(update={"term": 2024})
    anchor = freeze_cert_anchor(context, _statpack(), lookback_terms=10)
    assert anchor is not None and anchor.rate is None
    event_paths = _seed(_roots, 13, context=context.model_copy(update={"cert_anchor": anchor}))

    result = _stamp(13)

    assert result.exit_code == 0, result.output
    assert "does not verify" not in result.output
    _assert_cleared(_stamped(event_paths))


def test_before_proc_v15_a_frozen_anchor_is_ignored_and_the_stamp_pools_now(
    _roots: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An earlier label keeps the grading-time pool even over a context that
    carries a frozen anchor, so nothing stamped before the pin moves."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v14")
    event_paths = _seed(_roots, 14, context=_pinned(_statpack()))
    refreshed = _refreshed()
    write_json(tmp_path / "metrics" / "statpack.json", refreshed)

    assert _stamp(14).exit_code == 0
    stamped = _stamped(event_paths)
    # (0.3 * 200 + 0.06 * 100) / 300, the refreshed pack's pool.
    assert stamped["segment_base_rate"] == pytest.approx(0.22)
    assert stamped["base_rate_statpack_digest"] == statpack_digest(refreshed)


def test_from_proc_v15_a_context_with_no_frozen_anchor_pools_now(
    _roots: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v15")
    event_paths = _seed(_roots, 15, context=_frozen())

    assert _stamp(15).exit_code == 0
    stamped = _stamped(event_paths)
    assert stamped["segment_base_rate"] == pytest.approx(_EXACT_POOL)
    pack = read_model(tmp_path / "metrics" / "statpack.json", StatPack)
    assert stamped["base_rate_statpack_digest"] == statpack_digest(pack)


def test_the_board_accepts_a_pinned_anchor_across_a_refresh_and_drops_a_mismatch(
    _roots: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A grading that records its prediction's pin passes whatever the board's
    build; one that disagrees with the pin — rate, build, or window — is
    dropped, even where the board's own build would not re-pool it."""
    monkeypatch.setattr(process_version, "CURRENT_PROCESS_LABEL", "proc-v15")
    placed = _statpack()
    event_paths = _seed(_roots, 16, context=_pinned(placed))
    assert _stamp(16).exit_code == 0
    record = read_model(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"), Evaluation
    )
    cases = _roots / "cases"
    refreshed = _refreshed()

    def reproduces(evaluation: Evaluation, pack: StatPack | None) -> bool:
        digest = statpack_digest(pack) if pack is not None else None
        return _anchor_reproduces(cases, evaluation, Stage.cert, pack, digest)

    assert reproduces(record, placed)
    assert reproduces(record, refreshed)
    assert reproduces(record, None)
    for update in (
        {"segment_base_rate": 0.22},
        {"base_rate_statpack_digest": statpack_digest(refreshed)},
        {"base_rate_lookback_terms": 1},
    ):
        mismatched = record.model_copy(update=update)
        assert not reproduces(mismatched, refreshed), update
        assert not reproduces(mismatched, None), update
    # An earlier label's grading over the same pinned prediction is read as
    # before the pin: a recorded build the board does not hold stands.
    assert record.process_version is not None
    earlier = record.model_copy(
        update={
            "process_version": record.process_version.model_copy(update={"label": "proc-v14"}),
            "segment_base_rate": 0.22,
        }
    )
    assert reproduces(earlier, refreshed)


def test_the_history_lookup_stops_at_the_newest_matching_build() -> None:
    pack = _statpack()
    revisions: list[StatpackRevision] = [
        (datetime(2026, 10, 9, tzinfo=UTC), "{not a statpack"),
        (datetime(2026, 10, 5, tzinfo=UTC), _refreshed().model_dump_json()),
        (datetime(2026, 9, 1, tzinfo=UTC), pack.model_dump_json()),
        (datetime(2026, 8, 1, tzinfo=UTC), pack.model_dump_json()),
    ]
    build = find_statpack_build(statpack_digest(pack), revisions)
    assert build is not None
    assert build.committed_at == datetime(2026, 9, 1, tzinfo=UTC)
    assert find_statpack_build("sha256:invented", revisions) is None


def test_a_metrics_root_outside_any_work_tree_has_no_history(tmp_path: Path) -> None:
    assert list(git_statpack_history(tmp_path / "metrics")) == []
