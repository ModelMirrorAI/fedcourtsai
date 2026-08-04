"""End-to-end coverage of `fedcourts stamp-cell` and `process-digest`.

The stamp is harness-owned: the agent writes an unstamped prediction/evaluation,
then this step reads it, injects the process version derived from the registry,
and rewrites it. These exercise the real command against seeded ledger cells.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID
from fedcourtsai.pipeline.salience import SALIENCE_VERSION
from fedcourtsai.schemas import (
    BaseRateBucket,
    ClaimProbability,
    Disposition,
    Evaluation,
    EventKind,
    Judgment,
    JusticeVote,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ResolutionSignals,
    Stage,
    StatPack,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackTerm,
    StatPackTermSegment,
    VoteValue,
)
from fedcourtsai.serialize import write_json, write_yaml
from tests.conftest import seed_evaluation, seed_prediction

runner = CliRunner()


@pytest.fixture(autouse=True)
def _data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return tmp_path / "data"


def _stamp(role: str, actor: str, docket: int, event: str, run_id: str) -> Result:
    return runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            str(docket),
            "--event",
            event,
            "--run-id",
            run_id,
            "--role",
            role,
            "--actor",
            actor,
            "--stamped-at",
            "2026-01-01T00:00:00Z",
            "--pipeline-sha",
            "sha-abc",
        ],
    )


def test_stamp_injects_the_process_version_into_the_agents_prediction(_data_root: Path) -> None:
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    path = (
        CasePaths(_data_root, "scotus", 1)
        .event("evt-x")
        .prediction("claude-baseline", "20260101T000000Z")
    )
    assert json.loads(path.read_text())["process_version"] is None, "agent writes it unstamped"

    result = _stamp("predictor", "claude-baseline", 1, "evt-x", "20260101T000000Z")
    assert result.exit_code == 0, result.output

    pv = json.loads(path.read_text())["process_version"]
    assert pv["label"] == "proc-v1"
    assert pv["digest"].startswith("sha256:")
    assert pv["pipeline_sha"] == "sha-abc"


def test_stamp_is_byte_stable_under_a_fixed_clock(_data_root: Path) -> None:
    """Everything but `stamped_at` is deterministic: re-stamping with the same
    clock is byte-identical. In production `stamped_at` defaults to now, so a
    rerun's bytes differ there — but the partition-relevant `digest` is stable
    (proven in test_process_version), and a rerun regenerates the cell from the
    agent anyway, so the wall-clock field never moves a metric."""
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    path = (
        CasePaths(_data_root, "scotus", 1)
        .event("evt-x")
        .prediction("claude-baseline", "20260101T000000Z")
    )
    _stamp("predictor", "claude-baseline", 1, "evt-x", "20260101T000000Z")
    first = path.read_bytes()
    _stamp("predictor", "claude-baseline", 1, "evt-x", "20260101T000000Z")
    assert path.read_bytes() == first


def test_stamp_evaluator_covers_every_predictors_evaluation(_data_root: Path) -> None:
    """One evaluate cell scores every predictor, so the stamp must reach all of
    its evaluation.json — a single-file assumption would leave most unstamped."""
    for predictor in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        seed_evaluation(
            _data_root,
            "scotus",
            2,
            "evt-y",
            evaluator_id="claude-judge",
            predictor_id=predictor,
            run_id="RID",
        )
    result = _stamp("evaluator", "claude-judge", 2, "evt-y", "RID")
    assert result.exit_code == 0, result.output
    assert "3 file(s)" in result.output

    for predictor in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        path = (
            CasePaths(_data_root, "scotus", 2)
            .event("evt-y")
            .evaluation("claude-judge", predictor, "RID")
        )
        assert json.loads(path.read_text())["process_version"]["label"] == "proc-v1"


def test_stamp_evaluator_computes_the_claim_block_and_overwrites_the_agents(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`claim_scores` is the harness's word: the evaluator stamp computes it
    from the committed prediction, outcome, and statpack — and an
    evaluator-authored block does not survive the stamp."""
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 3).event(event)
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/3",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 1, 1),
                signals_observable=True,
                distribution_count=1,
                band="baseline",
                salience_version="sal-v1",
                term=2025,
            ),
            claims=[
                ClaimProbability(claim_id="disposition", probability=0.2),
                ClaimProbability(claim_id="relist-increment", probability=0.5),
                ClaimProbability(claim_id="cvsg-increment", probability=0.05),
            ],
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/3",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
            signals=ResolutionSignals(distribution_count=3),
        ),
    )
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(
            corpus_rows=1,
            terms=[
                StatPackTerm(
                    term=2024,
                    base_rates=BaseRateBucket(),
                    salience_version="sal-v1",
                    segments=[
                        StatPackTermSegment(
                            band="baseline",
                            prefix_weighted_resolved=100,
                            prefix_est_grant_rate=0.06,
                        )
                    ],
                )
            ],
        ),
    )
    seed_evaluation(
        _data_root,
        "scotus",
        3,
        event,
        evaluator_id="claude-judge",
        predictor_id="claude-baseline",
        run_id="RID",
    )
    # An evaluator-authored block — schema-valid, wrong — which must not survive.
    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    authored = json.loads(eval_path.read_text())
    authored["claim_scores"] = {
        "declared_set_version": "made-up",
        "claims": [],
        "total": 9.9,
        "floor": None,
        "lift": None,
    }
    eval_path.write_text(json.dumps(authored))

    result = _stamp("evaluator", "claude-judge", 3, event, "RID")
    assert result.exit_code == 0, result.output

    block = json.loads(eval_path.read_text())["claim_scores"]
    assert block["declared_set_version"] == "cert-v1"
    by_id = {row["claim_id"]: row for row in block["claims"]}
    # Disposition scored against the strictly-prior band rate; the increments
    # resolve but carry no baseline yet, so they stay unscored.
    assert by_id["disposition"]["score"] == pytest.approx(0.06**2 - 0.2**2)
    assert by_id["relist-increment"]["outcome"] == 1
    assert by_id["relist-increment"]["score"] is None
    assert block["floor"] == 0.0
    assert block["total"] == pytest.approx(0.06**2 - 0.2**2)


def test_stamp_evaluator_clears_claim_scores_where_nothing_supports_a_block(
    _data_root: Path,
) -> None:
    """No outcome on disk -> the stamp writes `claim_scores: null` — a recorded
    gap, not a failure, and still never the agent's word."""
    seed_evaluation(_data_root, "scotus", 4, "evt-y", run_id="RID")
    result = _stamp("evaluator", "claude-judge", 4, "evt-y", "RID")
    assert result.exit_code == 0, result.output
    path = (
        CasePaths(_data_root, "scotus", 4)
        .event("evt-y")
        .evaluation("claude-judge", "claude-baseline", "RID")
    )
    assert json.loads(path.read_text())["claim_scores"] is None


def test_a_missing_artifact_is_a_clean_no_op(_data_root: Path) -> None:
    """A no-output cell has nothing to stamp; it must not fail the cell."""
    result = _stamp("predictor", "claude-baseline", 999, "evt-x", "RID")
    assert result.exit_code == 0
    assert "no predictor artifact" in result.output


def test_an_unknown_actor_fails_the_cell(_data_root: Path) -> None:
    """A registry typo must fail loudly, not ship an unstamped-but-frozen-looking
    cell — the artifact exists but the config to derive its digest does not."""
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    result = _stamp("predictor", "no-such-predictor", 1, "evt-x", "20260101T000000Z")
    assert result.exit_code != 0


def test_process_digest_all_lists_every_enabled_actor() -> None:
    result = runner.invoke(app, ["process-digest", "--all"])
    assert result.exit_code == 0, result.output
    lines = [line for line in result.output.splitlines() if line.strip()]
    # Three predictors + three evaluators in the shipped registry.
    assert len(lines) == 6
    assert all("sha256:" in line and "proc-v1" in line for line in lines)


def test_stamp_evaluator_derives_the_base_rate_salience_version(_data_root: Path) -> None:
    """The version half of the basis record is the harness's word.

    `risk_set` reads the scored prediction's frozen `context.salience_version`,
    `terminal` the live scorer's version, no basis no version — and an
    evaluator-authored value never survives the stamp.
    """
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 4).event(event)
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/4",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 1, 1),
                signals_observable=True,
                distribution_count=1,
                band="baseline",
                salience_version="sal-frozen",
                term=2025,
            ),
        ),
    )
    cases = {
        "claude-baseline": ("risk_set", "sal-frozen"),
        "codex-baseline": ("terminal", SALIENCE_VERSION),
        "gemini-baseline": (None, None),
    }
    for predictor, (basis, _) in cases.items():
        write_json(
            event_paths.evaluation("claude-judge", predictor, "RID"),
            Evaluation(
                case_id="scotus/4",
                event_id=event,
                predictor_id=predictor,
                evaluator_id="claude-judge",
                engine="claude-code",
                run_id="RID",
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                correct=1,
                base_rate_basis=basis,
                base_rate_salience_version="sal-agent-invented",  # must not survive
            ),
        )

    result = _stamp("evaluator", "claude-judge", 4, event, "RID")
    assert result.exit_code == 0, result.output

    for predictor, (_, expected) in cases.items():
        stamped = json.loads(event_paths.evaluation("claude-judge", predictor, "RID").read_text())
        assert stamped["base_rate_salience_version"] == expected, predictor


def test_stamp_evaluator_keys_the_merits_baseline_on_the_grant_term(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The merits claim's baseline is read at the **grant** Term, not the
    frozen context's docket-number Term.

    The two disagree for a petition docketed into the incoming Term and granted
    before that Term opens, and there the docket Term runs one later — pooling
    at it would admit the case's own cohort. The fixture makes the two answers
    differ: keyed on the grant Term (OT2023, from the committed event's
    `opened_at`) the pool is OT2022 alone; keyed on the context's OT2024 it
    would swallow OT2023 as well.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = MERITS_EVENT_ID
    event_paths = CasePaths(_data_root, "scotus", 5).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/5",
            kind=EventKind.order,
            stage=Stage.merits,
            title="Merits judgment",
            opened_at=date(2024, 3, 1),  # a March grant → October Term 2023
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/5",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=1,
            probability=0.8,
            predicted_disposition=Disposition.other,
            judgment=Judgment.reversed,
            votes=[JusticeVote(justice="Roberts", vote=VoteValue.majority)],
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 1, 1),
                signals_observable=True,
                band="baseline",
                salience_version="sal-v1",
                term=2024,  # the docket-number Term, one later than the grant's
            ),
            claims=[ClaimProbability(claim_id="judgment-disturbed", probability=0.8)],
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/5",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.other,
            actual_granted=1,
            judgment=Judgment.reversed,
        ),
    )
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(
            corpus_rows=1,
            merits=StatPackMerits(
                parsed=60,
                disturbed=51,
                terms=[
                    # OT2023 is all-disturbed, so pooling it is unmissable.
                    StatPackMeritsTerm(term=2023, parsed=30, disturbed=30),
                    StatPackMeritsTerm(term=2022, parsed=30, disturbed=21),
                ],
            ),
        ),
    )
    seed_evaluation(
        _data_root,
        "scotus",
        5,
        event,
        evaluator_id="claude-judge",
        predictor_id="claude-baseline",
        run_id="RID",
    )

    result = _stamp("evaluator", "claude-judge", 5, event, "RID")
    assert result.exit_code == 0, result.output

    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    block = json.loads(eval_path.read_text())["claim_scores"]
    assert block["declared_set_version"] == "merits-v1"
    [row] = block["claims"]
    assert row["claim_id"] == "judgment-disturbed"
    # OT2022 alone: 21/30 = 0.70. The context Term would give 51/60 = 0.85.
    assert row["baseline"] == pytest.approx(0.70)
    assert row["outcome"] == 1
    assert row["score"] == pytest.approx(0.30**2 - 0.20**2)
