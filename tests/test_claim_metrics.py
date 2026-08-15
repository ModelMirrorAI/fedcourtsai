"""Claim-score aggregation and judge validation over a small fixture ledger."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version
from fedcourtsai.claim_metrics import (
    AGREEMENT_MIN_PAIRS,
    agreement_summary,
    build_claim_scores,
)
from fedcourtsai.cli import app
from fedcourtsai.integrity import FORWARD, PROCEDURAL, RETROSPECTIVE, StratifiedCell
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    ClaimScore,
    ClaimScoreBlock,
    ClaimScoreBoard,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    ProcessVersion,
    Stage,
    Stratum,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.store import iter_stratified_evaluations

runner = CliRunner()


def _block(
    disposition_score: float | None = 0.4,
    relist_score: float | None = None,
    cvsg_score: float | None = None,
    *,
    set_version: str = "cert-v1",
) -> ClaimScoreBlock:
    """A synthetic harness block over the cert-v1 shape.

    Scored rows carry an outcome and baseline like the real harness writes;
    a ``None`` score models the availability mask / missing-baseline state.
    The total/floor/lift arithmetic mirrors ``pipeline.claims.score_claims``:
    sums over the scored rows only, floor identically 0 where anything scored.
    """
    rows = [
        ClaimScore(
            claim_id="disposition",
            probability=0.7,
            baseline=0.3 if disposition_score is not None else None,
            outcome=1 if disposition_score is not None else None,
            score=disposition_score,
        ),
        ClaimScore(
            claim_id="relist-increment",
            probability=0.5,
            baseline=0.3 if relist_score is not None else None,
            outcome=0 if relist_score is not None else None,
            score=relist_score,
        ),
        ClaimScore(
            claim_id="cvsg-increment",
            probability=0.2,
            baseline=0.1 if cvsg_score is not None else None,
            outcome=0 if cvsg_score is not None else None,
            score=cvsg_score,
        ),
    ]
    scored = [s for s in (disposition_score, relist_score, cvsg_score) if s is not None]
    total = sum(scored) if scored else None
    floor = 0.0 if scored else None
    return ClaimScoreBlock(
        declared_set_version=set_version,
        claims=rows,
        total=total,
        floor=floor,
        lift=total - floor if total is not None and floor is not None else None,
    )


def _evaluation(
    predictor_id: str,
    *,
    claim_scores: ClaimScoreBlock | None = None,
    reasoning_quality: float | None = 0.8,
    **kw: object,
) -> Evaluation:
    base: dict[str, object] = dict(
        case_id="scotus/123",
        event_id="evt-petition-disposition",
        predictor_id=predictor_id,
        evaluator_id="eval-a",
        engine=Engine.claude_code,
        run_id="r1",
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        correct=1,
        reasoning_quality=reasoning_quality,
        claim_scores=claim_scores,
    )
    base.update(kw)
    return Evaluation.model_validate(base)


def _cells(
    *items: tuple[Evaluation, Stratum],
    stage: Stage | None = Stage.cert,
    moment: Moment | None = Moment.distribution,
) -> list[StratifiedCell]:
    """Stage-annotate fixture cells the way the stratified join yields them."""
    return [(ev, stratum, stage, moment) for ev, stratum in items]


def test_empty_stream_is_the_fully_suppressed_board() -> None:
    board = build_claim_scores([])
    assert board.process_scope == "frozen"
    assert board.evaluations_total == 0
    assert board.cells_with_claims == 0
    assert board.entries == []
    # Even the empty board records what the freeze constants were, exactly as
    # the leaderboard does, so `frozen` is answerable from the artifact alone.
    assert board.frozen_process is not None
    assert board.frozen_process.digests == sorted(process_version.FROZEN_PROCESS_DIGESTS)
    assert board.frozen_process.since == process_version.FROZEN_SINCE
    # A stratum with no cells at all carries no agreement record, not a zero.
    assert board.forward_agreement is None
    assert board.retrospective_agreement is None
    assert board.procedural_agreement is None


def test_blockless_cells_publish_counts_and_suppress_the_coefficient() -> None:
    # The current data reality: evaluations exist, none carry a block. The
    # artifact must render honest counts with every coefficient withheld.
    cells = _cells(*((_evaluation("alpha"), FORWARD) for _ in range(3)))
    board = build_claim_scores(cells)
    assert board.evaluations_total == 3
    assert board.cells_with_claims == 0
    assert board.entries == []  # an all-null predictor row states nothing
    agreement = board.forward_agreement
    assert agreement is not None
    assert agreement.pairs == 0
    assert agreement.suppressed is True
    assert agreement.rank_agreement is None
    assert agreement.missing_claim_block == 3
    assert agreement.masked_claim_total == 0
    assert agreement.missing_reasoning_quality == 0


def test_non_cert_stage_cells_sit_outside_the_population() -> None:
    # Only the cert-stage event kinds declare a claim set, so a cell on any
    # other stage (or with no stage) is never owed a block — it must not
    # inflate the population or the operational-absence counts.
    in_population = _cells((_evaluation("alpha"), FORWARD))
    outside = _cells((_evaluation("alpha", event_id="evt-i"), FORWARD), stage=Stage.interim)
    stageless = _cells((_evaluation("alpha", event_id="evt-n"), FORWARD), stage=None)
    board = build_claim_scores(in_population + outside + stageless, process_scope="all")
    assert board.evaluations_total == 1
    agreement = board.forward_agreement
    assert agreement is not None
    assert agreement.missing_claim_block == 1


def test_a_later_cert_moment_sits_outside_the_population() -> None:
    # The moment axis of the same rule: a CVSG cell carries the same declared
    # cert block as the distribution cell, so filtering on the stage alone would
    # pool two information sets into one claim mean. Only the cert stage's
    # FIRST moment is the population — the later moment neither inflates the
    # counts nor contributes its block.
    in_population = _cells((_evaluation("alpha", claim_scores=_block(0.4)), FORWARD))
    later_moment = _cells(
        (_evaluation("alpha", claim_scores=_block(0.2), event_id="evt-c"), FORWARD),
        moment=Moment.cvsg,
    )
    board = build_claim_scores(in_population + later_moment, process_scope="all")
    assert board.evaluations_total == 1
    assert board.cells_with_claims == 1
    [entry] = board.entries
    assert entry.forward is not None
    assert entry.forward.cells == 1
    assert entry.forward.mean_total == pytest.approx(0.4)  # never pooled with 0.2


def test_aggregates_per_predictor_per_stratum_and_never_pools() -> None:
    cells = _cells(
        (_evaluation("alpha", claim_scores=_block(0.4), event_id="evt-a"), FORWARD),
        (_evaluation("alpha", claim_scores=_block(0.2), event_id="evt-b"), FORWARD),
        (_evaluation("alpha", claim_scores=_block(-0.1), event_id="evt-c"), RETROSPECTIVE),
        (_evaluation("beta", claim_scores=_block(0.3), event_id="evt-a"), PROCEDURAL),
    )
    board = build_claim_scores(cells, process_scope="all")
    assert board.cells_with_claims == 4
    assert [e.predictor_id for e in board.entries] == ["alpha", "beta"]
    alpha = board.entries[0]
    assert alpha.forward is not None
    assert alpha.forward.cells == 2
    assert alpha.forward.events == 2
    assert alpha.forward.scored_events == 2
    assert alpha.forward.declared_set_versions == ["cert-v1"]
    assert alpha.forward.mean_total == pytest.approx(0.3)
    assert alpha.forward.mean_floor == 0.0
    assert alpha.forward.mean_lift == pytest.approx(0.3)
    # The retrospective stratum aggregates separately — never blended.
    assert alpha.retrospective is not None
    assert alpha.retrospective.mean_total == pytest.approx(-0.1)
    assert alpha.procedural is None
    beta = board.entries[1]
    assert beta.forward is None and beta.procedural is not None


def test_per_claim_means_keep_unscored_claims_visible() -> None:
    cells = _cells(
        (_evaluation("alpha", claim_scores=_block(0.4, relist_score=0.1)), FORWARD),
        (_evaluation("alpha", claim_scores=_block(0.2), event_id="evt-b"), FORWARD),
    )
    stratum = build_claim_scores(cells, process_scope="all").entries[0].forward
    assert stratum is not None
    by_claim = {row.claim_id: row for row in stratum.claims}
    # Declaration order is preserved from the blocks.
    assert list(by_claim) == ["disposition", "relist-increment", "cvsg-increment"]
    assert by_claim["disposition"].scored == 2
    assert by_claim["disposition"].mean_score == pytest.approx(0.3)
    assert by_claim["relist-increment"].scored == 1
    assert by_claim["relist-increment"].mean_score == pytest.approx(0.1)
    # A never-scored declared claim still appears: a coverage gap, not absence.
    assert by_claim["cvsg-increment"].scored == 0
    assert by_claim["cvsg-increment"].mean_score is None


def test_largest_single_claim_contribution_is_by_magnitude() -> None:
    # A big negative surprise is as capable of being "the whole total" as a
    # big positive one, so magnitude decides.
    cells = _cells(
        (_evaluation("alpha", claim_scores=_block(0.4)), FORWARD),
        (_evaluation("alpha", claim_scores=_block(-0.5, relist_score=0.1), event_id="b"), FORWARD),
    )
    stratum = build_claim_scores(cells, process_scope="all").entries[0].forward
    assert stratum is not None
    assert stratum.largest_claim_id == "disposition"
    assert stratum.largest_claim_score == -0.5


def test_masked_blocks_count_as_availability_not_scoring() -> None:
    # A block whose every claim is masked has a null total: it is present
    # (cells counts it) but scores nothing and enters no pair.
    masked = _block(None)
    cells = _cells((_evaluation("alpha", claim_scores=masked), FORWARD))
    board = build_claim_scores(cells, process_scope="all")
    stratum = board.entries[0].forward
    assert stratum is not None
    assert stratum.cells == 1
    assert stratum.scored_events == 0
    assert stratum.mean_total is None
    assert stratum.largest_claim_score is None
    agreement = board.forward_agreement
    assert agreement is not None
    assert agreement.pairs == 0
    assert agreement.masked_claim_total == 1
    assert agreement.missing_claim_block == 0


def _pair_cells(
    predictor: str, stratum: Stratum, totals_and_grades: list[tuple[float, float]]
) -> list[StratifiedCell]:
    """One intersection pair per (total, reasoning_quality), distinct events."""
    return _cells(
        *(
            (
                _evaluation(
                    predictor,
                    claim_scores=_block(total),
                    reasoning_quality=grade,
                    event_id=f"evt-{stratum}-{i}",
                ),
                stratum,
            )
            for i, (total, grade) in enumerate(totals_and_grades)
        )
    )


def test_agreement_below_the_preregistered_minimum_is_suppressed() -> None:
    pairs = [(i / 10, i / 20) for i in range(AGREEMENT_MIN_PAIRS - 1)]
    board = build_claim_scores(_pair_cells("alpha", FORWARD, pairs), process_scope="all")
    agreement = board.forward_agreement
    assert agreement is not None
    assert agreement.pairs == AGREEMENT_MIN_PAIRS - 1
    assert agreement.suppressed is True
    # The coefficient is withheld even though 9 pairs would define a tau.
    assert agreement.rank_agreement is None


def test_agreement_at_the_minimum_computes_tau_per_stratum() -> None:
    concordant = [(i / 10, i / 20) for i in range(AGREEMENT_MIN_PAIRS)]
    discordant = [(i / 10, (AGREEMENT_MIN_PAIRS - i) / 20) for i in range(AGREEMENT_MIN_PAIRS)]
    board = build_claim_scores(
        _pair_cells("alpha", FORWARD, concordant) + _pair_cells("alpha", RETROSPECTIVE, discordant),
        process_scope="all",
    )
    # Strata never pool: a perfectly concordant forward set and a perfectly
    # discordant retrospective set publish +1 and -1, not a blended 0.
    assert board.forward_agreement is not None
    assert board.forward_agreement.suppressed is False
    assert board.forward_agreement.rank_agreement == 1.0
    assert board.retrospective_agreement is not None
    assert board.retrospective_agreement.rank_agreement == -1.0


def test_agreement_counts_operational_absences_beside_the_intersection() -> None:
    pairs = _pair_cells("alpha", FORWARD, [(i / 10, i / 20) for i in range(4)])
    extras = _cells(
        (_evaluation("alpha", event_id="no-block"), FORWARD),
        (
            _evaluation(
                "alpha", claim_scores=_block(0.4), reasoning_quality=None, event_id="no-rq"
            ),
            FORWARD,
        ),
    )
    board = build_claim_scores(pairs + extras, process_scope="all")
    agreement = board.forward_agreement
    assert agreement is not None
    assert agreement.pairs == 4
    assert agreement.pair_events == 4
    assert agreement.missing_claim_block == 1
    assert agreement.missing_reasoning_quality == 1


def test_evaluator_multiplicity_collapses_to_the_event_unit() -> None:
    # Three evaluators of the same prediction carry an identical harness block:
    # the reporting unit is the event, so the means see one block while `cells`
    # keeps the raw census and `pair_events` exposes the tau's multiplicity.
    cells = _cells(
        *(
            (
                _evaluation(
                    "alpha", claim_scores=_block(0.4), evaluator_id=f"eval-{i}", run_id=f"r{i}"
                ),
                FORWARD,
            )
            for i in range(3)
        ),
        (_evaluation("alpha", claim_scores=_block(0.2), event_id="evt-b"), FORWARD),
    )
    board = build_claim_scores(cells, process_scope="all")
    stratum = board.entries[0].forward
    assert stratum is not None
    assert stratum.cells == 4
    assert stratum.events == 2
    assert stratum.scored_events == 2
    # An event-mean: (0.4 + 0.2) / 2, not the cell-mean (0.4*3 + 0.2) / 4.
    assert stratum.mean_total == pytest.approx(0.3)
    by_claim = {row.claim_id: row for row in stratum.claims}
    assert by_claim["disposition"].scored == 2
    agreement = board.forward_agreement
    assert agreement is not None
    assert agreement.pairs == 4  # per-cell, as the pre-registration fixes it
    assert agreement.pair_events == 2


def test_mixed_declarations_are_listed_so_pooling_is_visible() -> None:
    cells = _cells(
        (_evaluation("alpha", claim_scores=_block(0.4)), FORWARD),
        (
            _evaluation("alpha", claim_scores=_block(0.2, set_version="cert-v2"), event_id="b"),
            FORWARD,
        ),
    )
    stratum = build_claim_scores(cells, process_scope="all").entries[0].forward
    assert stratum is not None
    assert stratum.declared_set_versions == ["cert-v1", "cert-v2"]


def test_agreement_summary_states_every_state() -> None:
    assert agreement_summary(None) == "no cells"
    suppressed = build_claim_scores(
        _cells((_evaluation("alpha"), FORWARD)), process_scope="all"
    ).forward_agreement
    assert agreement_summary(suppressed) == f"suppressed (n=0 < {AGREEMENT_MIN_PAIRS})"
    computed = build_claim_scores(
        _pair_cells("alpha", FORWARD, [(i / 10, i / 20) for i in range(AGREEMENT_MIN_PAIRS)]),
        process_scope="all",
    ).forward_agreement
    assert agreement_summary(computed) == f"tau-b +1.00 (n={AGREEMENT_MIN_PAIRS})"
    # Every pair tied on one axis: defined n, undefined tau — not suppressed.
    tied = build_claim_scores(
        _pair_cells("alpha", FORWARD, [(0.4, i / 20) for i in range(AGREEMENT_MIN_PAIRS)]),
        process_scope="all",
    ).forward_agreement
    assert tied is not None and tied.rank_agreement is None and tied.suppressed is False
    assert agreement_summary(tied) == f"undefined over n={AGREEMENT_MIN_PAIRS}"


def _write_cell(
    data_root: Path,
    ev: Evaluation,
    *,
    predicted_at: datetime = datetime(2026, 6, 20, tzinfo=UTC),
    resolved_at: date = date(2026, 6, 23),
) -> None:
    """A full scored cell on disk: evaluation plus the event, prediction, and outcome.

    The petition kind with a null stage is the committed-ledger shape, which
    the stratification join normalizes to the cert stage.
    """
    court, _, docket = ev.case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(ev.event_id)
    write_yaml(
        event.event_file,
        PredictableEvent(
            event_id=ev.event_id,
            case_id=ev.case_id,
            kind=EventKind.petition,
            title="Test event",
            resolved=True,
        ),
    )
    write_json(event.evaluation(ev.evaluator_id, ev.predictor_id, ev.run_id), ev)
    write_json(
        event.prediction(ev.predictor_id, "p1"),
        Prediction(
            case_id=ev.case_id,
            event_id=ev.event_id,
            predictor_id=ev.predictor_id,
            engine=Engine.claude_code,
            run_id="p1",
            created_at=predicted_at,
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
        ),
    )
    write_json(
        event.outcome,
        Outcome(
            case_id=ev.case_id,
            event_id=ev.event_id,
            resolved_at=resolved_at,
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )


def test_cli_writes_a_valid_deterministic_board(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_cell(data_root, _evaluation("alpha", claim_scores=_block(0.4)))
    _write_cell(data_root, _evaluation("beta", event_id="evt-b", case_id="scotus/456"))
    out = tmp_path / "claim-scores.json"
    result = runner.invoke(
        app,
        ["claim-scores", "--out", str(out), "--all-versions"],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert result.exit_code == 0, result.output
    assert "1 of 2 evaluation(s) carry a claim block" in result.output
    assert "suppressed (n=1 < 10)" in result.output
    board = read_model(out, ClaimScoreBoard)
    assert board.process_scope == "all"
    assert [e.predictor_id for e in board.entries] == ["alpha"]
    # The stratified join classifies the cell forward (resolved after commit).
    assert board.entries[0].forward is not None
    # Deterministic: a second run reproduces the file byte for byte.
    first = out.read_text()
    runner.invoke(
        app,
        ["claim-scores", "--out", str(out), "--all-versions"],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert out.read_text() == first


def test_cli_defaults_to_the_frozen_headline(tmp_path: Path) -> None:
    # Shakedown ledger (no stamp, nothing blessed): the frozen surface is the
    # honest empty state, mirroring the leaderboard's default.
    data_root = tmp_path / "data"
    _write_cell(data_root, _evaluation("alpha", claim_scores=_block(0.4)))
    out = tmp_path / "claim-scores.json"
    result = runner.invoke(
        app, ["claim-scores", "--out", str(out)], env={"FEDCOURTS_DATA_ROOT": str(data_root)}
    )
    assert result.exit_code == 0, result.output
    board = read_model(out, ClaimScoreBoard)
    assert board.process_scope == "frozen"
    assert board.evaluations_total == 0
    assert board.entries == []
    # Confirm the fixture itself is visible under the pooled view.
    assert iter_stratified_evaluations(data_root, frozen_only=False) != []


def test_the_winning_block_keys_on_the_harness_clock_not_the_agent_clock() -> None:
    # The later *agent-written* created_at sits on the earlier-stamped run: the
    # dedup must follow the harness stamp (integrity.evaluation_clock), so the
    # block from the newer-stamped evaluation wins even though the agent clock
    # points the other way.
    stamped_early = _evaluation(
        "alpha",
        claim_scores=_block(0.4),
        run_id="r1",
        created_at=datetime(2026, 6, 30, tzinfo=UTC),
        process_version=ProcessVersion(
            label="proc-v2", digest="sha256:x", stamped_at=datetime(2026, 6, 1, tzinfo=UTC)
        ),
    )
    stamped_late = _evaluation(
        "alpha",
        claim_scores=_block(0.2),
        run_id="r2",
        created_at=datetime(2026, 6, 1, tzinfo=UTC),
        process_version=ProcessVersion(
            label="proc-v2", digest="sha256:x", stamped_at=datetime(2026, 6, 20, tzinfo=UTC)
        ),
    )
    board = build_claim_scores(_cells((stamped_early, FORWARD), (stamped_late, FORWARD)))
    stratum = board.entries[0].forward
    assert stratum is not None
    assert stratum.cells == 2
    assert stratum.events == 1
    assert stratum.mean_total == pytest.approx(0.2)


def test_a_naive_and_aware_created_at_mix_cannot_raise() -> None:
    # Agent-written created_at carries no offset guarantee; two unstamped runs
    # of one cell mixing naive and aware clocks must still order (naive reads
    # as UTC) instead of raising TypeError out of the tuple compare.
    naive = _evaluation(
        "alpha", claim_scores=_block(0.4), run_id="r1", created_at=datetime(2026, 6, 1)
    )
    aware = _evaluation(
        "alpha",
        claim_scores=_block(0.2),
        run_id="r2",
        created_at=datetime(2026, 6, 2, tzinfo=UTC),
    )
    board = build_claim_scores(_cells((naive, FORWARD), (aware, FORWARD)))
    stratum = board.entries[0].forward
    assert stratum is not None
    assert stratum.cells == 2
    assert stratum.events == 1
    assert stratum.mean_total == pytest.approx(0.2)


def test_a_statpack_revision_between_evaluator_stamps_picks_the_newer_stamp() -> None:
    # The registered scenario: two *different* judges of one prediction whose
    # blocks differ because a statpack revision landed between their stamps.
    # The later-stamped judge's block carries the newer vintage and must win,
    # even though the earlier-stamped judge wrote the later agent clock.
    earlier_vintage = _evaluation(
        "alpha",
        claim_scores=_block(0.4),
        evaluator_id="eval-a",
        run_id="r1",
        created_at=datetime(2026, 6, 30, tzinfo=UTC),
        process_version=ProcessVersion(
            label="proc-v2", digest="sha256:x", stamped_at=datetime(2026, 6, 1, tzinfo=UTC)
        ),
    )
    later_vintage = _evaluation(
        "alpha",
        claim_scores=_block(0.2),
        evaluator_id="eval-b",
        run_id="r1",
        created_at=datetime(2026, 6, 1, tzinfo=UTC),
        process_version=ProcessVersion(
            label="proc-v2", digest="sha256:x", stamped_at=datetime(2026, 6, 20, tzinfo=UTC)
        ),
    )
    board = build_claim_scores(_cells((earlier_vintage, FORWARD), (later_vintage, FORWARD)))
    stratum = board.entries[0].forward
    assert stratum is not None
    assert stratum.cells == 2
    assert stratum.events == 1
    assert stratum.mean_total == pytest.approx(0.2)
