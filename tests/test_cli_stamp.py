"""End-to-end coverage of `fedcourts stamp-cell` and `process-digest`.

The stamp is harness-owned: the agent writes an unstamped prediction/evaluation,
then this step reads it, injects the process version derived from the registry,
and rewrites it. These exercise the real command against seeded ledger cells.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal

import pytest
from typer.testing import CliRunner, Result

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID
from fedcourtsai.pipeline.salience import SALIENCE_VERSION
from fedcourtsai.process_version import CURRENT_PROCESS_LABEL
from fedcourtsai.schemas import (
    BaseRateBucket,
    ClaimProbability,
    Disposition,
    Evaluation,
    EventKind,
    InterimResolutionSignals,
    Judgment,
    JusticeVote,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ResolutionSignals,
    Stage,
    StatPack,
    StatPackInterim,
    StatPackInterimTerm,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackTerm,
    StatPackTermSegment,
    VoteValue,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml
from tests.conftest import seed_evaluation, seed_prediction

runner = CliRunner()


@pytest.fixture(autouse=True)
def _data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return tmp_path / "data"


def _stamp(
    role: str,
    actor: str,
    docket: int,
    event: str,
    run_id: str,
    *,
    stamped_at: str = "2026-01-01T00:00:00Z",
) -> Result:
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
            stamped_at,
            "--pipeline-sha",
            "sha-abc",
        ],
    )


def _regrade(role: str, actor: str, docket: int, event: str, run_id: str) -> Result:
    """The same cell, re-graded: no stamp flags, since it writes no stamp."""
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
            "--regrade",
        ],
    )


def test_stamp_refuses_a_naive_stamped_at(_data_root: Path) -> None:
    """The stamp is the frozen/alpha partition's time key: an offset-less
    value has no defined order against the freeze instant and would read as
    pre-freeze, silently stamping the cell out of the headline — refused at
    the write end with a clean exit instead."""
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    result = runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            "1",
            "--event",
            "evt-x",
            "--run-id",
            "20260101T000000Z",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--stamped-at",
            "2026-01-01T00:00:00",
        ],
    )
    assert result.exit_code == 2
    assert "UTC offset" in result.output


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
    # Read from the constant, not a literal: the assertion is that the stamp
    # carries the label in force, which is what a label bump must not silently
    # break — the value itself is `test_process_version`'s to pin.
    assert pv["label"] == CURRENT_PROCESS_LABEL
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
        assert json.loads(path.read_text())["process_version"]["label"] == CURRENT_PROCESS_LABEL


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
    assert all("sha256:" in line and CURRENT_PROCESS_LABEL in line for line in lines)


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


def test_stamp_evaluator_fails_a_risk_set_basis_that_resolves_no_version(
    _data_root: Path,
) -> None:
    """A recorded `risk_set` basis beside a null version fails the cell.

    The basis says the segment base rate was read over the risk-set population;
    the version says under which banding. With no frozen context on the scored
    prediction the version does not resolve, so the pair names a population
    nothing pins down — and rewriting the basis to `terminal` would stamp the
    live scorer's version onto a rate taken over the other table. The null is
    still written (it is what resolution produced), the sibling cells are still
    stamped, and the exit is non-zero.
    """
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 6).event(event)
    # A prediction with no frozen context — provisioning failed, so the risk-set
    # band it would have been read under was never recorded.
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/6",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=None,
        ),
    )
    for predictor, basis in (("claude-baseline", "risk_set"), ("codex-baseline", "terminal")):
        write_json(
            event_paths.evaluation("claude-judge", predictor, "RID"),
            Evaluation(
                case_id="scotus/6",
                event_id=event,
                predictor_id=predictor,
                evaluator_id="claude-judge",
                engine="claude-code",
                run_id="RID",
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                correct=1,
                base_rate_basis=basis,
                segment_base_rate=0.3555,
            ),
        )

    result = _stamp("evaluator", "claude-judge", 6, event, "RID")
    assert result.exit_code != 0
    offender = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    assert "::error::" in result.output
    assert str(offender) in result.output
    assert "risk_set" in result.output

    # The offending cell is still stamped, with the null the resolution produced.
    stamped = json.loads(offender.read_text())
    assert stamped["base_rate_salience_version"] is None
    assert stamped["process_version"]["pipeline_sha"] == "sha-abc"
    # And one bad cell does not strand the rest of the run's stamps.
    sibling = json.loads(
        event_paths.evaluation("claude-judge", "codex-baseline", "RID").read_text()
    )
    assert sibling["base_rate_salience_version"] == SALIENCE_VERSION


def test_stamp_evaluator_scores_the_interim_set_off_the_application_term(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The production join for an interim cell: `stamp-cell` computes the block.

    Every interim moment declares `interim-v1`, so the harness scores four rows
    here. Only `interim-disposition` carries a baseline — pooled over the
    application Terms strictly before the cell's own, which the frozen context
    carries as the `YYAnnn` Term — while the three escalation increments resolve
    from both committed ends and stay unscored for want of a conditioned cut.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-motion-disposition"
    event_paths = CasePaths(_data_root, "scotus", 7).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/7",
            kind=EventKind.motion,
            stage=Stage.interim,
            moment=Moment.arrival,
            title="Application for a stay",
            opened_at=date(2026, 3, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/7",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 3, 2, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-03-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 3, 1),
                signals_observable=True,
                band=None,  # an application freezes none, by rule
                response_requested=False,
                referred_to_court=False,
                amicus_briefs=1,
                term=2026,  # the APPLICATION Term, from a `26Annn` number
            ),
            claims=[
                ClaimProbability(claim_id="interim-disposition", probability=0.2),
                ClaimProbability(claim_id="response-requested-increment", probability=0.4),
                ClaimProbability(claim_id="referral-increment", probability=0.3),
                ClaimProbability(claim_id="amicus-increment", probability=0.6),
            ],
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/7",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
            interim_signals=InterimResolutionSignals(
                response_requested=True,
                referred_to_court=False,
                amicus_briefs=3,
            ),
        ),
    )
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(
            corpus_rows=1,
            interim=StatPackInterim(
                substantive_resolved=110,
                substantive_granted=56,
                terms=[
                    # The cell's OWN Term, all-granted so pooling it is unmissable.
                    StatPackInterimTerm(term=2026, substantive_resolved=50, substantive_granted=50),
                    StatPackInterimTerm(term=2025, substantive_resolved=60, substantive_granted=6),
                ],
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/7",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=0.04,  # (0.2 - 0)**2
        ),
    )

    result = _stamp("evaluator", "claude-judge", 7, event, "RID")
    assert result.exit_code == 0, result.output

    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    stamped = json.loads(eval_path.read_text())
    block = stamped["claim_scores"]
    assert block["declared_set_version"] == "interim-v1"
    rows = {row["claim_id"]: row for row in block["claims"]}
    assert list(rows) == [
        "interim-disposition",
        "response-requested-increment",
        "referral-increment",
        "amicus-increment",
    ]
    # OT2025 alone: 6/60 = 0.10. The own Term would drag it to 56/110.
    assert rows["interim-disposition"]["baseline"] == pytest.approx(0.10)
    assert rows["interim-disposition"]["outcome"] == 0
    assert rows["interim-disposition"]["score"] == pytest.approx(0.10**2 - 0.20**2)
    # The increments resolve from both ends and go unscored for want of a cut.
    assert rows["response-requested-increment"]["outcome"] == 1
    assert rows["referral-increment"]["outcome"] == 0
    assert rows["amicus-increment"]["outcome"] == 1  # 1 -> 3
    for claim_id in ("response-requested-increment", "referral-increment", "amicus-increment"):
        assert rows[claim_id]["baseline"] is None
        assert rows[claim_id]["score"] is None
    # No band was frozen, so the basis record stays null on both halves — the
    # interim pool is not a band product.
    assert stamped["base_rate_salience_version"] is None
    # The headline record is stamped off the same frozen application Term and
    # the same committed artifacts: (0.2 - 0)**2, 0.10, and 1 - 0.04/(0.10)**2.
    assert stamped["brier_score"] == pytest.approx(0.04)
    assert stamped["segment_base_rate"] == pytest.approx(0.10)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.04 / 0.01)


def test_stamp_evaluator_clears_the_pair_where_the_pack_has_no_interim_section(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No interim section in the pack -> both halves cleared on an interim cell.

    The interim sibling of the merits refusal: an absent section is no pool, so
    the harness writes the null rather than letting a recorded rate stand in
    for a baseline it never computed.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-motion-disposition"
    event_paths = CasePaths(_data_root, "scotus", 9).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/9",
            kind=EventKind.motion,
            stage=Stage.interim,
            moment=Moment.arrival,
            title="Application for a stay",
            opened_at=date(2026, 3, 1),
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/9",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    # The prediction carries the frozen application Term, so the join resolves
    # and the pack is the only thing standing between the cell and a rate.
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/9",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 3, 2, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-03-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 3, 1),
                signals_observable=True,
                band=None,
                term=2026,
            ),
        ),
    )
    # A pack with cert Terms only — nothing the interim arm can pool.
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(corpus_rows=1, terms=[]),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/9",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=0.04,
            segment_base_rate=0.42,
            brier_skill_score=0.1,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 9, event, "RID")
    assert result.exit_code == 0, result.output
    # The discarded number is said out loud — the only trace an overwrite that
    # changes the value ever leaves.
    assert "::warning::" in result.output
    assert "0.42" in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None
    # The Brier is not cleared with them: it answers to the prediction and the
    # outcome, both committed here, and neither depends on the pack.
    assert stamped["brier_score"] == pytest.approx(0.04)


def test_stamp_leaves_a_cert_cells_recorded_base_rate_alone(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The cert trio is the evaluator's: the stamp touches none of the three.

    Which band population the rate is taken over is a judgment about the scored
    prediction's frozen band, so the harness records the basis version beside it
    but never overwrites the rate — nor the Brier scored against it, whose
    ownership follows the rate's on every stage — and the internal-coherence
    check on the board is what stands behind the cert column's arithmetic.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 10).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/10",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for a writ of certiorari",
            opened_at=date(2026, 1, 1),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/10",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=0.04,
            base_rate_basis="terminal",
            segment_base_rate=0.067,
            brier_skill_score=0.443,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 10, event, "RID")
    assert result.exit_code == 0, result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["segment_base_rate"] == pytest.approx(0.067)
    assert stamped["brier_skill_score"] == pytest.approx(0.443)
    # Untouched even though this cell has no prediction and no outcome to
    # recompute one from: none of the trio is stamped on a cert cell, so the
    # absence never reaches the clearing path.
    assert stamped["brier_score"] == pytest.approx(0.04)
    assert stamped["base_rate_salience_version"] == SALIENCE_VERSION
    # `correct` is not part of the trio and takes no cert exemption: with
    # neither artifact to compare, the stamp clears it.
    assert stamped["correct"] is None


def test_stamp_evaluator_keys_the_merits_baseline_on_the_grant_term(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The merits baselines are read at the **grant** Term, not the frozen
    context's docket-number Term — the claim block's and the headline
    `segment_base_rate` the stamp writes beside it, which is one pooled
    quantity computed once and never the evaluator's word.

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
                    StatPackMeritsTerm(term=2023, parsed=30, disturbed=30, cert_order_excluded=0),
                    StatPackMeritsTerm(term=2022, parsed=30, disturbed=21, cert_order_excluded=0),
                ],
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/5",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=0.04,  # (0.8 - 1)**2, on the disturbed binary
            # A hand-pooled pair, schema-valid and wrong: neither half survives.
            # The basis is the merits stage's other non-answer — a band record
            # on a rate no band produced — and does not survive either.
            segment_base_rate=0.85,
            brier_skill_score=0.9,
            base_rate_basis="risk_set",
        ),
    )
    # A second predictor's cell, with no prediction of its own on this event:
    # the rate is still the harness's, but there is nothing to score a Brier
    # from and so nothing to derive a skill from either.
    write_json(
        event_paths.evaluation("claude-judge", "codex-baseline", "RID"),
        Evaluation(
            case_id="scotus/5",
            event_id=event,
            predictor_id="codex-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 5, event, "RID")
    assert result.exit_code == 0, result.output
    # The evaluator's Brier here is the right one, so only the rate it got
    # wrong is called out: the warning marks a disagreement, not the overwrite.
    assert "brier_score" not in result.output
    assert "segment_base_rate 0.85" in result.output

    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    stamped = json.loads(eval_path.read_text())
    block = stamped["claim_scores"]
    assert block["declared_set_version"] == "merits-v1"
    [row] = block["claims"]
    assert row["claim_id"] == "judgment-disturbed"
    # OT2022 alone: 21/30 = 0.70. The context Term would give 51/60 = 0.85.
    assert row["baseline"] == pytest.approx(0.70)
    assert row["outcome"] == 1
    assert row["score"] == pytest.approx(0.30**2 - 0.20**2)
    # The headline record is stamped from the same pool, the same Term, and the
    # same committed artifacts, so the evaluator's own numbers are gone:
    # (0.8 - 1)**2, 0.70, and 1 - 0.04/(0.70 - 1)**2.
    assert stamped["brier_score"] == pytest.approx(0.04)
    assert stamped["segment_base_rate"] == pytest.approx(0.70)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.04 / 0.09)
    # Neither half of the basis record applies: the merits pool is no band
    # product, so the stamp clears both rather than letting a recorded
    # `risk_set` pull a salience version onto it — or fail the cell on a guard
    # whose documented remedy means nothing on a harness-pooled stage.
    assert stamped["base_rate_basis"] is None
    assert stamped["base_rate_salience_version"] is None

    # No prediction to score: the rate stands, the Brier and the skill do not.
    sibling = json.loads(
        event_paths.evaluation("claude-judge", "codex-baseline", "RID").read_text()
    )
    assert sibling["segment_base_rate"] == pytest.approx(0.70)
    assert sibling["brier_score"] is None
    assert sibling["brier_skill_score"] is None


def test_stamp_evaluator_clears_the_pair_where_the_merits_pool_refuses(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A merits pool below its floor clears **both** halves, never leaves one.

    An evaluator-authored number must not survive where the harness declined to
    compute one: nothing downstream distinguishes a recorded rate the harness
    stands behind from one it does not, so the refusal has to reach the record
    as a null on both halves rather than leaving the agent's pair in place.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = MERITS_EVENT_ID
    event_paths = CasePaths(_data_root, "scotus", 8).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/8",
            kind=EventKind.order,
            stage=Stage.merits,
            title="Merits judgment",
            opened_at=date(2024, 3, 1),
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/8",
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
                parsed=10,
                disturbed=7,
                # One prior Term, far below MERITS_BASE_RATE_MIN_PARSED.
                terms=[
                    StatPackMeritsTerm(term=2022, parsed=10, disturbed=7, cert_order_excluded=0)
                ],
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/8",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=0.04,
            segment_base_rate=0.7,
            brier_skill_score=0.55,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 8, event, "RID")
    assert result.exit_code == 0, result.output

    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    stamped = json.loads(eval_path.read_text())
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None
    # This cell has no prediction either, so the Brier clears on its own inputs
    # — the same tolerant discipline the rate takes, and for the same reason.
    assert stamped["brier_score"] is None

    # And the same where there is no pack at all to pool from.
    (tmp_path / "metrics" / "statpack.json").unlink()
    assert _stamp("evaluator", "claude-judge", 8, event, "RID").exit_code == 0
    stamped = json.loads(eval_path.read_text())
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None


def test_stamp_evaluator_recomputes_the_brier_over_the_evaluators_number(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """On a stamped stage the Brier is the harness's too, not the evaluator's.

    This is what makes the skill ratio *verifiable* rather than merely
    reproducible: with the base rate stamped and the Brier left to the agent,
    the board's internal-coherence check passes by construction on a numerator
    nothing ever checked, so a wrong Brier publishes a wrong skill that agrees
    with its own record. Here the evaluator writes a Brier off by an order of
    magnitude and the stamp replaces it from the two committed artifacts — and
    all three stamped numbers reproduce the ratio from one another.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = MERITS_EVENT_ID
    event_paths = CasePaths(_data_root, "scotus", 11).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/11",
            kind=EventKind.order,
            stage=Stage.merits,
            title="Merits judgment",
            opened_at=date(2024, 3, 1),  # a March grant → October Term 2023
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/11",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=1,
            probability=0.6,
            predicted_disposition=Disposition.other,
            judgment=Judgment.reversed,
            votes=[JusticeVote(justice="Roberts", vote=VoteValue.majority)],
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 1, 1),
                signals_observable=True,
                band="baseline",
                salience_version="sal-v1",
                term=2023,
            ),
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/11",
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
                parsed=30,
                disturbed=21,
                terms=[
                    StatPackMeritsTerm(term=2022, parsed=30, disturbed=21, cert_order_excluded=0)
                ],
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/11",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            # Off by an order of magnitude, and internally coherent with the
            # skill beside it against the rate the harness will stamp — exactly
            # the record the coherence check cannot tell from a right one.
            brier_score=0.016,
            segment_base_rate=0.70,
            brier_skill_score=1 - 0.016 / 0.09,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 11, event, "RID")
    assert result.exit_code == 0, result.output
    # The discarded Brier is named out loud, as the discarded rate is.
    assert "::warning::" in result.output
    assert "brier_score 0.016" in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    # (0.6 - 1)**2 from the committed probability and the committed binary.
    assert stamped["brier_score"] == pytest.approx(0.16)
    assert stamped["segment_base_rate"] == pytest.approx(0.70)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.16 / 0.09)
    # The whole point, stated as the reader of the frozen record would check
    # it: the skill reproduces from the two numbers stamped beside it, and both
    # of those answer to committed artifacts rather than to the agent.
    baseline = (stamped["segment_base_rate"] - 1) ** 2
    assert stamped["brier_skill_score"] == pytest.approx(1 - stamped["brier_score"] / baseline)


def test_stamp_scores_the_merits_brier_on_the_undisturbed_side(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A merits cell whose judgment below **stood**: the binary is 0, not 1.

    The merits axis is P(disturbed), so an affirmance scores the same forecast
    the other way round. Every other merits case here resolves disturbed, which
    an implementation reading the wrong side of the binary would pass; this one
    is the direction that catches it.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = MERITS_EVENT_ID
    event_paths = CasePaths(_data_root, "scotus", 13).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/13",
            kind=EventKind.order,
            stage=Stage.merits,
            title="Merits judgment",
            opened_at=date(2024, 3, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/13",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=1,
            probability=0.6,
            predicted_disposition=Disposition.other,
            judgment=Judgment.reversed,
            votes=[JusticeVote(justice="Roberts", vote=VoteValue.majority)],
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/13",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.other,
            actual_granted=0,  # the judgment below stood
            judgment=Judgment.affirmed,
        ),
    )
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(
            corpus_rows=1,
            merits=StatPackMerits(
                parsed=30,
                disturbed=21,
                terms=[
                    StatPackMeritsTerm(term=2022, parsed=30, disturbed=21, cert_order_excluded=0)
                ],
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/13",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=0,
        ),
    )

    assert _stamp("evaluator", "claude-judge", 13, event, "RID").exit_code == 0

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    # (0.6 - 0)**2, not (0.6 - 1)**2: a confident disturbed call against an
    # affirmance scores badly, and the skill against a 0.70 baseline is deeply
    # negative rather than mildly so.
    assert stamped["brier_score"] == pytest.approx(0.36)
    assert stamped["segment_base_rate"] == pytest.approx(0.70)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.36 / 0.49)


def test_stamp_evaluator_clears_the_brier_with_no_committed_outcome(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No outcome -> no stamped Brier, no skill, and no `correct` either.

    The tolerant-clearing half of the rule. An interim cell can be stamped
    before its application resolves, and the harness has no binary to score
    against then; leaving the evaluator's number in place would let exactly the
    unchecked value the stamp exists to displace survive the one case where
    nothing can check it. `correct` takes the same clearing off the same two
    artifacts. The base rate, which needs the outcome no more than the pack
    does, stands.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-motion-disposition"
    event_paths = CasePaths(_data_root, "scotus", 12).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/12",
            kind=EventKind.motion,
            stage=Stage.interim,
            moment=Moment.arrival,
            title="Application for a stay",
            opened_at=date(2026, 3, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/12",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 3, 2, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-03-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 3, 1),
                signals_observable=True,
                band=None,
                term=2026,
            ),
        ),
    )
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(
            corpus_rows=1,
            interim=StatPackInterim(
                substantive_resolved=110,
                substantive_granted=56,
                terms=[
                    StatPackInterimTerm(term=2025, substantive_resolved=60, substantive_granted=6)
                ],
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/12",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=0.04,
            brier_skill_score=-3.0,
        ),
    )

    assert _stamp("evaluator", "claude-judge", 12, event, "RID").exit_code == 0

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["brier_score"] is None
    assert stamped["brier_skill_score"] is None
    assert stamped["correct"] is None
    # The pool needs only the pack and the frozen application Term: OT2025
    # alone, 6/60.
    assert stamped["segment_base_rate"] == pytest.approx(0.10)


def test_stamp_recomputes_correct_on_a_cert_cell(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The cert stage's skill-record exemption does not extend to `correct`.

    The exemption is about the *baseline*: which band population a pooled rate
    is taken over is a judgment about the frozen band, and that judgment reaches
    the skill through `segment_base_rate`. `correct` has no baseline and no
    band — it is a label comparison between two committed artifacts — so there
    is nothing here for an evaluator to exercise judgment over, and the
    leaderboard's first rank key is recomputed rather than taken on its word.
    Here the evaluator scores a denial call correct against a granted outcome;
    the stamp writes the 0, says so, and leaves the cert trio alone.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 13).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/13",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for a writ of certiorari",
            opened_at=date(2026, 1, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/13",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/13",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/13",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,  # wrong: `denied` against a `granted` outcome
            brier_score=0.64,
            base_rate_basis="terminal",
            segment_base_rate=0.067,
            brier_skill_score=-9.28,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 13, event, "RID")
    assert result.exit_code == 0, result.output
    # The discarded bit is named out loud, as a discarded Brier or rate is.
    assert "::warning::" in result.output
    assert "recorded correct 1" in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["correct"] == 0
    # Regression guard on the exemption itself: the trio is still the
    # evaluator's on a cert cell, stamped `correct` beside it or not.
    assert stamped["brier_score"] == pytest.approx(0.64)
    assert stamped["segment_base_rate"] == pytest.approx(0.067)
    assert stamped["brier_skill_score"] == pytest.approx(-9.28)
    assert stamped["base_rate_basis"] == "terminal"


def test_stamp_recomputes_correct_on_the_merits_judgment_axis(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A merits cell's `correct` is the judgment match, and the stamp writes it.

    The routing is `pipeline.evaluate.is_correct`'s, on the **outcome**: a
    merits outcome's `actual_disposition` is the off-vocabulary `other`, so the
    comparison is judgment-to-judgment. The evaluator here records a 1 for a
    `reversed` call against an `affirmed` outcome — the disposition comparison's
    free `other == other` match, which is exactly the constant the merits axis
    exists to avoid — and the stamp replaces it with the 0.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = MERITS_EVENT_ID
    event_paths = CasePaths(_data_root, "scotus", 14).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/14",
            kind=EventKind.order,
            stage=Stage.merits,
            title="Merits judgment",
            opened_at=date(2024, 3, 1),  # a March grant → October Term 2023
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/14",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=1,
            probability=0.6,
            predicted_disposition=Disposition.other,
            judgment=Judgment.reversed,
            votes=[JusticeVote(justice="Roberts", vote=VoteValue.majority)],
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/14",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.other,
            actual_granted=0,
            judgment=Judgment.affirmed,
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/14",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,  # the disposition match, not the judgment one
        ),
    )

    result = _stamp("evaluator", "claude-judge", 14, event, "RID")
    assert result.exit_code == 0, result.output
    assert "recorded correct 1" in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["correct"] == 0
    # The Brier is scored on the disturbed binary off the same two artifacts.
    assert stamped["brier_score"] == pytest.approx(0.36)


def test_stamp_clears_correct_with_no_committed_prediction(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An outcome but no prediction to compare it against -> `correct` is null.

    The other half of the tolerant clearing: the join is the evaluation's
    *predictor*, so a cell whose predictor committed nothing readable has no
    label to compare and the harness declines a bit rather than letting the
    evaluator's stand where nothing can check it. Agreement is no defence — the
    recorded 0 here happens to be right, and is cleared anyway.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 15).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/15",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for a writ of certiorari",
            opened_at=date(2026, 1, 1),
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/15",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/15",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=0,
        ),
    )

    assert _stamp("evaluator", "claude-judge", 15, event, "RID").exit_code == 0

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["correct"] is None


def test_stamp_is_silent_where_the_recorded_correct_agrees(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An agreeing bit is overwritten **quietly** — the note is about disagreement.

    The stamp assigns unconditionally either way, so this is not a test of what
    gets written but of what gets *said*: a warning on every stamped cell would
    be noise a maintainer learns to skip, which is exactly how the disagreeing
    case gets missed. Here the evaluator's `correct` matches what the two
    committed artifacts produce, and nothing is echoed about it.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 16).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/16",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for a writ of certiorari",
            opened_at=date(2026, 1, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/16",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/16",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/16",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,  # right: `denied` against a `denied` outcome
        ),
    )

    result = _stamp("evaluator", "claude-judge", 16, event, "RID")
    assert result.exit_code == 0, result.output
    assert "correct" not in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["correct"] == 1


def test_stamp_warns_where_the_evaluator_recorded_no_correct(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An omitted bit is said too: it kills the independent read, silently.

    The elicited value the stamp discards is the only second read of the
    stamped quantity anywhere in a run, so an evaluator that writes nothing
    leaves the harness's arithmetic unchecked — and, unlike a wrong value,
    produces no disagreement to notice. The omission direction is on for
    `correct` because the prompt requires it of every cell; on a field where a
    null is the normal shape it stays off.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 17).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/17",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for a writ of certiorari",
            opened_at=date(2026, 1, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/17",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/17",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/17",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=None,
            # A null Brier on a cert cell is the normal shape and stays quiet,
            # which is what makes the omission warning field-specific.
            brier_score=None,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 17, event, "RID")
    assert result.exit_code == 0, result.output
    assert "recorded no correct" in result.output
    assert "brier_score" not in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["correct"] == 1


def test_stamp_recomputes_correct_on_an_interim_cell(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The third stage, stated rather than inferred from the other two.

    Cert and merits between them exercise both arms of the stage branch and
    both routings inside `is_correct`; interim is a harness-skill stage whose
    axis is the disposition, so it is the one combination neither covers. The
    claim is "every stage", so every stage is asserted.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event = "evt-motion-disposition"
    event_paths = CasePaths(_data_root, "scotus", 18).event(event)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/18",
            kind=EventKind.motion,
            stage=Stage.interim,
            moment=Moment.arrival,
            title="Application for a stay",
            opened_at=date(2026, 3, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/18",
            event_id=event,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 3, 2, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-03-01.json",
            granted=1,
            probability=0.8,
            predicted_disposition=Disposition.granted,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 3, 1),
                signals_observable=True,
                band=None,
                term=2026,
            ),
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="scotus/18",
            event_id=event,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/18",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,  # wrong: `granted` against a `denied` outcome
        ),
    )

    result = _stamp("evaluator", "claude-judge", 18, event, "RID")
    assert result.exit_code == 0, result.output
    assert "recorded correct 1" in result.output

    stamped = json.loads(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    assert stamped["correct"] == 0
    assert stamped["brier_score"] == pytest.approx(0.64)


def test_stamp_evaluator_fails_a_risk_set_basis_whose_join_finds_no_prediction(
    _data_root: Path,
) -> None:
    """The alias path: a `risk_set` basis with no prediction to join fails.

    A surviving alias (or a predictor that produced nothing) leaves the stamp's
    join empty, so the version cannot resolve — the same rule as the
    no-frozen-context case, pinned separately because four doc surfaces rest on
    this exact sentence.
    """
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 19).event(event)
    write_json(
        event_paths.evaluation("claude-judge", "claude_baseline", "RID"),
        Evaluation(
            case_id="scotus/19",
            event_id=event,
            predictor_id="claude_baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            base_rate_basis="risk_set",
            segment_base_rate=0.3555,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 19, event, "RID")
    assert result.exit_code != 0
    assert "::error::" in result.output
    assert "risk_set" in result.output


def test_stamp_evaluator_fails_a_terminal_basis_where_a_band_was_frozen(
    _data_root: Path,
) -> None:
    """The mirror mispairing: `terminal` taken where the prediction froze a band.

    Both frozen-band shapes are offenders — with the band's version beside it,
    a well-formed rate read against the wrong population; without it, a moved
    band priced at the terminal rate, where omission is the only answer — and
    each error names its own correction. Only a prediction that froze no band
    at all takes the fallback legitimately.
    """
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 20).event(event)
    # The guard's terminal arm keys on the cert stage, so the event definition
    # has to say so — an unreadable one suppresses the arm rather than firing it.
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=event,
            case_id="scotus/20",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition for writ of certiorari",
            opened_at=date(2025, 12, 1),
        ),
    )
    cases = (
        ("claude-baseline", "baseline", "sal-v1"),
        ("codex-baseline", "elevated", None),
        ("gemini-baseline", None, None),
    )
    for predictor, band, salience_version in cases:
        write_json(
            event_paths.prediction(predictor, "RID"),
            Prediction(
                case_id="scotus/20",
                event_id=event,
                predictor_id=predictor,
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
                    signals_observable=band is not None,
                    distribution_count=1,
                    band=band,
                    salience_version=salience_version,
                    term=2025,
                ),
            ),
        )
        write_json(
            event_paths.evaluation("claude-judge", predictor, "RID"),
            Evaluation(
                case_id="scotus/20",
                event_id=event,
                predictor_id=predictor,
                evaluator_id="claude-judge",
                engine="claude-code",
                run_id="RID",
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                correct=1,
                base_rate_basis="terminal",
                segment_base_rate=0.15,
            ),
        )

    result = _stamp("evaluator", "claude-judge", 20, event, "RID")
    assert result.exit_code != 0
    # The versioned offender gets the wrong-population arm, the versionless one
    # the omission arm — distinguishable at the console, each with the scored
    # prediction's run id so a maintainer can check the join without redoing it.
    versioned = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    assert str(versioned) in result.output
    assert "wrong population" in result.output
    versionless = event_paths.evaluation("claude-judge", "codex-baseline", "RID")
    assert str(versionless) in result.output
    assert "no salience version beside it" in result.output
    assert "run RID" in result.output
    # The band-less sibling took the documented fallback and is not named.
    survivor = event_paths.evaluation("claude-judge", "gemini-baseline", "RID")
    assert str(survivor) not in result.output


def test_stamp_evaluator_keeps_the_terminal_arm_off_unstaged_events(
    _data_root: Path,
) -> None:
    """The terminal arm is cert-only; an event with no readable stage passes.

    The frozen-band pairing is a cert-petition concept while the frozen
    context is stamped per case, so a case-level band visible from a
    stage-less event's cell must not reach the rule. The risk-set arm is not
    narrowed — a `risk_set` basis without its version is incoherent on any
    stage — so only the terminal shape is exercised here.
    """
    event = "evt-petition-writ-of-certiorari"
    event_paths = CasePaths(_data_root, "scotus", 21).event(event)
    # No event.yaml is written, so the stage is unresolvable by design.
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="scotus/21",
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
                salience_version="sal-v1",
                term=2025,
            ),
        ),
    )
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id="scotus/21",
            event_id=event,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            base_rate_basis="terminal",
            segment_base_rate=0.15,
        ),
    )

    result = _stamp("evaluator", "claude-judge", 21, event, "RID")
    assert result.exit_code == 0, result.output


_CERT_EVENT = "evt-petition-disposition"


def _commit_cert_disposition(event_paths: EventPaths, docket: int, actual: Disposition) -> None:
    """(Re-)commit the cert event's outcome under one disposition label."""
    write_json(
        event_paths.outcome,
        Outcome(
            case_id=f"scotus/{docket}",
            event_id=_CERT_EVENT,
            resolved_at=date(2026, 5, 1),
            actual_disposition=actual,
            # `gvr` joins the granted set on the binary axis, so a correction
            # between *those two* labels moves the label comparison and nothing
            # else — which is what isolates `correct`. A correction reaching
            # `denied` moves the binary too, which is the other case entirely.
            actual_granted=0 if actual is Disposition.denied else 1,
        ),
    )


def _seed_cert_cell(
    data_root: Path,
    docket: int,
    *,
    actual: Disposition,
    basis: Literal["risk_set", "terminal"] | None = None,
) -> EventPaths:
    """A cert cell whose predictor called `gvr`, graded against `actual`.

    The prediction freezes no context, so a `risk_set` basis here resolves no
    salience version — which is the mispairing the stamp's guard fails on.
    """
    event_paths = CasePaths(data_root, "scotus", docket).event(_CERT_EVENT)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=_CERT_EVENT,
            case_id=f"scotus/{docket}",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Petition disposition",
            opened_at=date(2026, 1, 1),
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id=f"scotus/{docket}",
            event_id=_CERT_EVENT,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=1,
            probability=0.6,
            predicted_disposition=Disposition.gvr,
        ),
    )
    _commit_cert_disposition(event_paths, docket, actual)
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id=f"scotus/{docket}",
            event_id=_CERT_EVENT,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=0,
            base_rate_basis=basis,
            segment_base_rate=None if basis is None else 0.15,
        ),
    )
    return event_paths


def _commit_merits_judgment(event_paths: EventPaths, docket: int, judgment: Judgment) -> None:
    """(Re-)commit the merits event's outcome under one judgment."""
    write_json(
        event_paths.outcome,
        Outcome(
            case_id=f"scotus/{docket}",
            event_id=MERITS_EVENT_ID,
            resolved_at=date(2026, 5, 1),
            actual_disposition=Disposition.other,
            # The merits binary is judgment-disturbed, so the correction moves
            # the Brier's target as well as the label comparison's.
            actual_granted=1 if judgment is Judgment.reversed else 0,
            judgment=judgment,
        ),
    )


def _seed_merits_cell(data_root: Path, docket: int, *, judgment: Judgment) -> EventPaths:
    """A merits cell whose predictor called `reversed`, graded against `judgment`.

    Identical between two dockets but for the committed judgment, so a pair of
    these differs only where the outcome does — which is what makes the two
    stamped records comparable field by field.
    """
    event_paths = CasePaths(data_root, "scotus", docket).event(MERITS_EVENT_ID)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=MERITS_EVENT_ID,
            case_id=f"scotus/{docket}",
            kind=EventKind.order,
            stage=Stage.merits,
            title="Merits judgment",
            opened_at=date(2024, 3, 1),  # a March grant → October Term 2023
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id=f"scotus/{docket}",
            event_id=MERITS_EVENT_ID,
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
            # The claim block is scored against the frozen context, so without
            # one there is no block for the twins to differ over.
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 1, 1),
                signals_observable=True,
                band="baseline",
                salience_version="sal-v1",
                term=2024,
            ),
            claims=[ClaimProbability(claim_id="judgment-disturbed", probability=0.8)],
        ),
    )
    _commit_merits_judgment(event_paths, docket, judgment)
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID"),
        Evaluation(
            case_id=f"scotus/{docket}",
            event_id=MERITS_EVENT_ID,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            # Hand-written and wrong on every axis the harness owns, so a field
            # the stamp failed to compute would show up as the evaluator's.
            correct=1,
            brier_score=0.04,
            segment_base_rate=0.85,
            brier_skill_score=0.9,
        ),
    )
    return event_paths


def test_regrade_recomputes_correct_under_the_producing_process_stamp(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A corrected outcome re-grades the cell under the stamp already on it.

    `correct` is a comparison between two committed artifacts, so re-committing
    the outcome makes every evaluation that read the old one stale — while
    changing nothing about the run that produced them. Recomputing the graded
    fields is the correction; re-resolving the version beside them would
    attribute the earlier run's prose and judgment to whatever process the
    registry resolves now.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event_paths = _seed_cert_cell(_data_root, 22, actual=Disposition.granted)
    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")

    stamp_result = _stamp("evaluator", "claude-judge", 22, _CERT_EVENT, "RID")
    assert stamp_result.exit_code == 0, stamp_result.output
    stamped = json.loads(eval_path.read_text())
    assert stamped["correct"] == 0, "`gvr` against the disposition as first committed"
    produced_under = stamped["process_version"]
    assert produced_under is not None

    _commit_cert_disposition(event_paths, 22, Disposition.gvr)
    result = _regrade("evaluator", "claude-judge", 22, _CERT_EVENT, "RID")
    assert result.exit_code == 0, result.output

    regraded = json.loads(eval_path.read_text())
    assert regraded["correct"] == 1
    # The whole block, `stamped_at` included: what the correction changed is
    # the record's inputs, not the process that read them.
    assert regraded["process_version"] == produced_under


def test_regrade_fails_the_mispaired_basis_after_the_graded_fields_land(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The basis guard judges the record as written, and a re-grade writes the
    same record — so it fails the same way, and after the same writes. A
    `risk_set` basis whose version does not resolve names a population nothing
    pins down, and that stays true when the numbers beside it are recomputed
    rather than first written: the recompute lands, and the cell still fails."""
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event_paths = _seed_cert_cell(_data_root, 27, actual=Disposition.granted, basis="risk_set")
    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")

    # The ordinary stamp fails the same guard and still writes, which is what
    # leaves a stamped record for the re-grade to preserve.
    first = _stamp("evaluator", "claude-judge", 27, _CERT_EVENT, "RID")
    assert first.exit_code == 1, first.output
    produced_under = json.loads(eval_path.read_text())["process_version"]
    assert produced_under is not None

    _commit_cert_disposition(event_paths, 27, Disposition.gvr)
    result = _regrade("evaluator", "claude-judge", 27, _CERT_EVENT, "RID")
    assert result.exit_code == 1, result.output
    assert "base_rate_basis 'risk_set'" in result.output

    regraded = json.loads(eval_path.read_text())
    assert regraded["correct"] == 1, "the graded fields landed before the guard fired"
    assert regraded["process_version"] == produced_under


def test_regrade_refuses_a_cert_trio_the_correction_invalidated(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A correction that moves the binary invalidates the evaluator's Brier trio.

    The stamp leaves a cert cell's `brier_score`, `segment_base_rate`, and
    `brier_skill_score` as the evaluator wrote them — which band population the
    rate came from is its judgment. So a `denied` → `granted` correction would
    otherwise recompute `correct` against the new binary while the trio stayed
    scored against the old one: the leaderboard drops such a cell from
    `skill_scored` (its recorded skill stops reproducing) while the corrected
    `correct` stays in accuracy, and the two columns silently run over
    different populations. Refused instead, pointing at the remedy, with
    nothing written.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event_paths = _seed_cert_cell(_data_root, 29, actual=Disposition.denied)
    eval_path = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    # The evaluator's own trio, correct against the outcome as first committed:
    # the prediction's 0.6 against a denial is (0.6 - 0)**2.
    write_json(
        eval_path,
        read_model(eval_path, Evaluation).model_copy(
            update={
                "brier_score": 0.36,
                "segment_base_rate": 0.15,
                "base_rate_basis": "terminal",
                "brier_skill_score": 1 - 0.36 / 0.0225,
            }
        ),
    )
    first = _stamp("evaluator", "claude-judge", 29, _CERT_EVENT, "RID")
    assert first.exit_code == 0, first.output
    before = eval_path.read_bytes()

    # The correction moves the binary: `gvr` joins the granted set, so the
    # recorded Brier no longer reproduces.
    _commit_cert_disposition(event_paths, 29, Disposition.gvr)
    result = _regrade("evaluator", "claude-judge", 29, _CERT_EVENT, "RID")
    assert result.exit_code == 1
    assert "does not reproduce" in result.output
    assert "brier_skill_score" in result.output, "the message names the remedy"
    assert eval_path.read_bytes() == before, "refused before anything was written"


def test_regrade_refuses_a_run_a_newer_grading_supersedes(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every scoring surface collapses a grader's re-runs of one cell to the
    newest, so recomputing a superseded run moves no published number while
    exiting clean — a correction that reads as landed and is not. The message
    names the run that wins."""
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event_paths = _seed_cert_cell(_data_root, 30, actual=Disposition.granted)
    assert _stamp("evaluator", "claude-judge", 30, _CERT_EVENT, "RID").exit_code == 0
    # A second grading of the same cell, stamped later, which every ledger read
    # collapses to.
    write_json(
        event_paths.evaluation("claude-judge", "claude-baseline", "RID2"),
        read_model(
            event_paths.evaluation("claude-judge", "claude-baseline", "RID"), Evaluation
        ).model_copy(update={"run_id": "RID2"}),
    )
    assert (
        _stamp(
            "evaluator",
            "claude-judge",
            30,
            _CERT_EVENT,
            "RID2",
            stamped_at="2026-06-01T00:00:00Z",
        ).exit_code
        == 0
    )

    _commit_cert_disposition(event_paths, 30, Disposition.gvr)
    result = _regrade("evaluator", "claude-judge", 30, _CERT_EVENT, "RID")
    assert result.exit_code == 1
    assert "RID2 supersedes it" in result.output
    # The surviving run re-grades cleanly.
    survivor = _regrade("evaluator", "claude-judge", 30, _CERT_EVENT, "RID2")
    assert survivor.exit_code == 0, survivor.output
    winning = event_paths.evaluation("claude-judge", "claude-baseline", "RID2")
    assert json.loads(winning.read_text())["correct"] == 1


def test_regrade_echoes_each_cells_process_scope(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A re-grade leaves no `superseded_gradings` trace, so the scope of every
    cell it touches is echoed: a frozen-scope cell moving is what a reader
    would want recorded somewhere outside `data/`'s git history."""
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    event_paths = _seed_cert_cell(_data_root, 31, actual=Disposition.granted)
    assert _stamp("evaluator", "claude-judge", 31, _CERT_EVENT, "RID").exit_code == 0

    _commit_cert_disposition(event_paths, 31, Disposition.gvr)
    result = _regrade("evaluator", "claude-judge", 31, _CERT_EVENT, "RID")
    assert result.exit_code == 0, result.output
    # The scope word itself is what the freeze state decides, so the assertion
    # is on the annotation being there and naming the stamp it preserved.
    assert "-scope cell stamped" in result.output
    assert CURRENT_PROCESS_LABEL in result.output


def test_regrade_fails_where_it_matched_no_artifact(_data_root: Path) -> None:
    """The ordinary stamp's no-op is the fan-out's contract — a no-output cell
    is already routed to a draft. A re-grade's coordinates are typed by hand
    instead, so matching nothing means the cell was named wrong, and a mistyped
    run id must not exit clean as though a correction had landed."""
    seed_evaluation(_data_root, "scotus", 28, "evt-y", run_id="RID")
    result = _regrade("evaluator", "claude-judge", 28, "evt-y", "MISTYPED")
    assert result.exit_code == 1
    assert "no evaluator artifact" in result.output


def test_regrade_refuses_an_evaluation_that_was_never_stamped(_data_root: Path) -> None:
    """A re-grade preserves a stamp; where there is none it has nothing to
    preserve, and writing the graded fields alone would leave a cell that
    reads as scored under no process at all. The ordinary stamp is the one
    that resolves a version for it."""
    seed_evaluation(_data_root, "scotus", 23, "evt-y", run_id="RID")
    path = (
        CasePaths(_data_root, "scotus", 23)
        .event("evt-y")
        .evaluation("claude-judge", "claude-baseline", "RID")
    )
    before = path.read_bytes()

    result = _regrade("evaluator", "claude-judge", 23, "evt-y", "RID")
    assert result.exit_code != 0
    assert "no process_version" in result.output
    assert path.read_bytes() == before, "refused before anything was written"


def test_regrade_refuses_the_predictor_role(_data_root: Path) -> None:
    """A prediction carries no harness-graded field — its `correct` and skill
    record live on the evaluations that score it — so there is nothing for a
    re-grade to recompute, and a predictor cell only ever takes the ordinary
    stamp."""
    seed_prediction(_data_root, "scotus", 24, "evt-x", predictor_id="claude-baseline")
    path = (
        CasePaths(_data_root, "scotus", 24)
        .event("evt-x")
        .prediction("claude-baseline", "20260101T000000Z")
    )
    before = path.read_bytes()

    result = _regrade("predictor", "claude-baseline", 24, "evt-x", "20260101T000000Z")
    assert result.exit_code == 2
    assert path.read_bytes() == before


def test_regrade_refuses_the_flags_that_only_set_a_stamp(_data_root: Path) -> None:
    """`--stamped-at` and `--pipeline-sha` set fields of the version a re-grade
    declines to write, so accepting them silently would read as re-dating a
    stamp that never moves."""
    result = runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            "25",
            "--event",
            "evt-y",
            "--run-id",
            "RID",
            "--role",
            "evaluator",
            "--actor",
            "claude-judge",
            "--regrade",
            "--stamped-at",
            "2026-01-01T00:00:00Z",
        ],
    )
    assert result.exit_code == 2
    assert "nothing to set" in result.output


def test_regrade_writes_what_an_ordinary_stamp_would_but_the_version(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Re-grade is the ordinary stamp minus the process attribution.

    Twin merits cells over one statpack: one graded against a judgment later
    corrected and then re-graded, one graded against the corrected judgment
    from the start. Every harness-owned field — `correct`, the claim block, and
    the merits skill record — has to land identically, because each is a
    function of the committed artifacts and of nothing about the run. Only the
    version differs, and only because the re-graded twin keeps the one its
    producing run stamped.
    """
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    write_json(
        tmp_path / "metrics" / "statpack.json",
        StatPack(
            corpus_rows=1,
            merits=StatPackMerits(
                parsed=60,
                disturbed=51,
                terms=[
                    StatPackMeritsTerm(term=2023, parsed=30, disturbed=30, cert_order_excluded=0),
                    StatPackMeritsTerm(term=2022, parsed=30, disturbed=21, cert_order_excluded=0),
                ],
            ),
        ),
    )
    corrected = _seed_merits_cell(_data_root, 25, judgment=Judgment.reversed)
    fresh = _seed_merits_cell(_data_root, 26, judgment=Judgment.affirmed)

    first = _stamp(
        "evaluator", "claude-judge", 25, MERITS_EVENT_ID, "RID", stamped_at="2025-06-01T00:00:00Z"
    )
    assert first.exit_code == 0, first.output
    _commit_merits_judgment(corrected, 25, Judgment.affirmed)
    again = _regrade("evaluator", "claude-judge", 25, MERITS_EVENT_ID, "RID")
    assert again.exit_code == 0, again.output
    twin = _stamp("evaluator", "claude-judge", 26, MERITS_EVENT_ID, "RID")
    assert twin.exit_code == 0, twin.output

    regraded = json.loads(
        corrected.evaluation("claude-judge", "claude-baseline", "RID").read_text()
    )
    stamped = json.loads(fresh.evaluation("claude-judge", "claude-baseline", "RID").read_text())
    # The graded fields did move off the stale judgment: `reversed` against an
    # `affirmed` outcome, and the Brier on the undisturbed binary.
    assert regraded["correct"] == 0
    assert regraded["brier_score"] == pytest.approx(0.64)
    assert regraded["claim_scores"] is not None
    # The version each record carries is the one thing the two must not share:
    # the re-graded cell keeps its own producing run's stamp. The pops feed the
    # whole-record comparison below, so they stay out of the asserts
    # `python -O` strips.
    regraded_version = regraded.pop("process_version")
    stamped_version = stamped.pop("process_version")
    regraded_case = regraded.pop("case_id")
    stamped_case = stamped.pop("case_id")
    assert regraded_version["stamped_at"].startswith("2025-06-01")
    assert stamped_version["stamped_at"].startswith("2026-01-01")
    assert regraded_case == "scotus/25"
    assert stamped_case == "scotus/26"
    assert regraded == stamped
