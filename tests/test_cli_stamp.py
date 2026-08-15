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
    assert pv["label"] == "proc-v2"
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
        assert json.loads(path.read_text())["process_version"]["label"] == "proc-v2"


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
    assert all("sha256:" in line and "proc-v2" in line for line in lines)


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
    # The headline pair is stamped off the same frozen application Term:
    # 0.10, and 1 - 0.04/(0.10 - 0)**2.
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


def test_stamp_leaves_a_cert_cells_recorded_base_rate_alone(
    _data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The cert pair is the evaluator's: the stamp touches neither half.

    Which band population the rate is taken over is a judgment about the scored
    prediction's frozen band, so the harness records the basis version beside it
    but never overwrites the rate — and the internal-coherence check on the
    board is what stands behind the cert column's arithmetic.
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
    assert stamped["base_rate_salience_version"] == SALIENCE_VERSION


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
    # A second predictor's cell, scored without a Brier: the rate is still the
    # harness's, but nothing derives a skill from it.
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
    # The headline pair is stamped from the same pool and the same Term, so the
    # evaluator's own numbers are gone: 0.70, and 1 - 0.04/(0.70 - 1)**2.
    assert stamped["segment_base_rate"] == pytest.approx(0.70)
    assert stamped["brier_skill_score"] == pytest.approx(1 - 0.04 / 0.09)
    # Neither half of the basis record applies: the merits pool is no band
    # product, so the stamp clears both rather than letting a recorded
    # `risk_set` pull a salience version onto it — or fail the cell on a guard
    # whose documented remedy means nothing on a harness-pooled stage.
    assert stamped["base_rate_basis"] is None
    assert stamped["base_rate_salience_version"] is None

    # No Brier to score: the rate stands, the skill it would derive does not.
    sibling = json.loads(
        event_paths.evaluation("claude-judge", "codex-baseline", "RID").read_text()
    )
    assert sibling["segment_base_rate"] == pytest.approx(0.70)
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

    # And the same where there is no pack at all to pool from.
    (tmp_path / "metrics" / "statpack.json").unlink()
    assert _stamp("evaluator", "claude-judge", 8, event, "RID").exit_code == 0
    stamped = json.loads(eval_path.read_text())
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None
