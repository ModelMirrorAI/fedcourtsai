"""Gate smoke: the offline stub cascade over the fixture corpus is validatable.

Drives provision → predict → evaluate → ``validate`` against the deterministic
fixture corpus with no model and no network, so a broken predict/evaluate cell —
an artifact that stops validating, a corpus read seam that stops resolving — fails
here in seconds in ``pytest`` instead of in a labelled CI run.

:mod:`tests.test_cascade` exercises ``run_cascade``'s behaviours case by case;
this is the one compose check the documented gate points at: an open, a
resolved, *and* a decided merits case run into a single ledger that passes the
same ``fedcourts validate`` the PR gate runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import build_leaderboard
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cascade
from fedcourtsai.pipeline.cascade import CascadeReport, run_cascade
from fedcourtsai.pipeline.claims import (
    CLAIM_CVSG_INCREMENT,
    CLAIM_DISPOSITION,
    CLAIM_JUDGMENT_DISTURBED,
    CLAIM_RELIST_INCREMENT,
)
from fedcourtsai.schemas import Disposition, Evaluation, Judgment, Outcome, Prediction
from fedcourtsai.serialize import read_model
from fedcourtsai.store import iter_stratified_evaluations

CONFIG_ROOT = Path("config")
RUN = "20260628T120000Z"


def test_stub_cascade_smoke(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    merits_case = fixture.add_merits_fixture(db)
    data_root = tmp_path / "data"

    def _run(court: str, docket: int) -> CascadeReport:
        return run_cascade(
            corpus_db_path=db,
            data_root=data_root,
            config_root=CONFIG_ROOT,
            court=court,
            docket=docket,
            run_id=RUN,
        )

    # ca9/101 is resolved → predict + materialize outcome + evaluate;
    # ca9/103 is open → predict only, nothing to score;
    # scotus/306 is granted and judged → the merits cell contract end to end.
    resolved = _run("ca9", 101)
    open_case = _run("ca9", 103)
    merits = _run("scotus", 306)

    assert resolved.valid, resolved.problems
    assert resolved.predictions and resolved.outcomes and resolved.evaluations
    assert open_case.valid, open_case.problems
    assert open_case.predictions and not open_case.outcomes and not open_case.evaluations
    assert merits.valid, merits.problems
    assert merits.predictions and merits.outcomes and merits.evaluations

    # The merits ground truth took the judgment mapping, not the cert vocabulary
    # (the fixture's cert baseline has no docket-level decision date, so the one
    # outcome here is the merits event's) …
    [merits_outcome_path] = merits.outcomes
    outcome = json.loads(merits_outcome_path.read_text())
    assert merits_outcome_path.parent.name == "evt-order-judgment"
    assert outcome["judgment"] == "reversed"
    assert outcome["actual_disposition"] == "other"
    assert outcome["actual_granted"] == 1  # reversed => disturbed, the declared binary

    # … the stub's merits prediction carried the mandatory judgment + votes pair,
    # and the evaluation scored the merits axes deterministically: the stub's
    # affirmed/0.0 floor against a reversed outcome is a full Brier miss and a
    # judgment mismatch.
    evaluation_path = next(
        p
        for p in merits.evaluations
        if p.name == "evaluation.json" and "evt-order-judgment" in str(p)
    )
    evaluation = json.loads(evaluation_path.read_text())
    assert evaluation["judgment_correct"] == 0
    assert evaluation["brier_score"] == 1.0
    prediction_path = next(
        p
        for p in merits.predictions
        if p.name == "prediction.json" and "evt-order-judgment" in str(p)
    )
    prediction = json.loads(prediction_path.read_text())
    assert prediction["judgment"] == "affirmed" and prediction["votes"]
    assert merits_case.case_id == "scotus/306"

    # The blind-grading bracket ran around every evaluate cell: a candidate was
    # staged per predictor, and nothing alias-keyed reached the ledger (the stub
    # writes real ids, so un-aliasing is a no-op — what this pins is that the
    # bracket runs at all and leaves the committed layout untouched).
    blinded = CasePaths(data_root, "ca9", 101).blinded_predictions
    assert sorted(p.name for p in blinded.iterdir()) == [
        "candidate-a",
        "candidate-b",
        "candidate-c",
    ]
    assert (blinded / "candidate-a" / "prediction.json").is_file()
    assert not list(data_root.glob("cases/*/*/events/*/evaluations/*/candidate-*"))

    # The compose check: all cases in one ledger pass the gate's own validate CLI
    # (the merits-contract check included, now that a merits event is in the tree).
    result = CliRunner().invoke(app, ["validate", str(data_root)])

    assert result.exit_code == 0, result.output
    assert "valid" in result.output


def test_stub_cascade_interim_application_smoke(tmp_path: Path) -> None:
    """The fixture's application docket runs the interim cell end to end offline.

    scotus/306 (`26A11`) is a resolved substantive stay application, so its
    motion-baseline event carries `Stage.interim`: provision → stub predict →
    interim outcome (a granted stay, no cert `signals` block) → evaluate →
    validate, then the leaderboard build segments the cell into the unranked
    `interim` stages block, never the cert board.

    What this proves is the *composition* — an interim cell reaches every stage
    and lands in the right block. The rules it composes are pinned at their own
    seams, because the stub writes no skill fields and the cascade runs no
    stamp step, so the null skill/claim fields here would read null for any
    cell: the band suppression in
    ``tests/test_cli_provision.py::test_an_application_snapshot_freezes_no_band``,
    the absent cert baseline in ``tests/test_evaluate.py``'s
    ``segment_base_rate`` cases, the interim ``signals`` guard in
    ``tests/test_cascade.py``, and the claim block in ``tests/test_claims.py`` /
    ``tests/test_cli_stamp.py``.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    data_root = tmp_path / "data"

    report = run_cascade(
        corpus_db_path=db,
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court="scotus",
        docket=306,
        run_id=RUN,
    )

    assert report.valid, report.problems
    assert report.events == ("evt-motion-disposition",)
    assert report.predictions and report.outcomes and report.evaluations

    # The interim outcome: relief granted, dated, and no cert signals block —
    # distribution count and CVSG are observations nobody makes on an application.
    outcome = read_model(report.outcomes[0], Outcome)
    assert outcome.actual_granted == 1
    assert outcome.signals is None

    # A motion-kind event declares no claim set, so the stub prediction carries
    # no claims field — the prompt's declared-set rule, exercised offline.
    prediction_path = next(p for p in report.predictions if p.name == "prediction.json")
    assert read_model(prediction_path, Prediction).claims is None

    # The cell is scored on the probability: stub P=0.0 against a granted stay.
    # The skill and claim fields are null, which the stub would write for any
    # cell — the interim rules behind them are pinned at the seams named above.
    evaluation_path = next(p for p in report.evaluations if p.name == "evaluation.json")
    evaluation = read_model(evaluation_path, Evaluation)
    assert evaluation.brier_score == 1.0
    assert evaluation.correct == 0
    assert evaluation.segment_base_rate is None
    assert evaluation.claim_scores is None

    # The leaderboard build puts the cell in the unranked `interim` stages
    # block; nothing enters the ranked cert board from this ledger.
    board = build_leaderboard(iter_stratified_evaluations(data_root, frozen_only=False))
    assert "interim" in board.stages
    assert board.stages["interim"].evaluations_total >= 1
    assert board.evaluations_total == 0


def test_stub_cascade_merits_smoke(tmp_path: Path) -> None:
    """The fixture's granted docket runs the merits cell end to end offline.

    scotus/306's cert grant opened a merits proceeding, so it carries the
    `evt-order-judgment` event the grant mints (kind `order`, `Stage.merits`):
    provision → stub predict (a judgment with its mandatory vote block, and the
    whole declared `merits-v1` set) → merits outcome off the judgment axis →
    evaluate → validate, then the leaderboard build segments the cell into the
    unranked `merits` stages block, never the cert board.

    Addressed by event id, because `add_merits_fixture` writes its row over the
    interim application docket's: without it the cascade would target that
    case's motion baseline too and the assertions would read a mixed ledger.

    What this proves is the *composition* — a merits cell reaches every stage
    and lands in the right block. The rules it composes are pinned at their own
    seams: the judgment axes in ``tests/test_evaluate.py``, the merits claim
    set in ``tests/test_claims.py``, the harness-computed claim block in
    ``tests/test_cli_stamp.py``, and the fan-out admission in
    ``tests/test_store.py``. The stub writes no skill fields and the cascade
    runs no stamp step, so the null skill/claim fields here would read null for
    any cell.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    merits_case = fixture.add_merits_fixture(db)
    data_root = tmp_path / "data"
    assert merits_case.case_id == "scotus/306"  # the literals the call below uses

    report = run_cascade(
        corpus_db_path=db,
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court="scotus",
        docket=306,
        event="evt-order-judgment",
        run_id=RUN,
    )

    assert report.valid, report.problems
    assert report.events == ("evt-order-judgment",)
    assert report.predictions and report.outcomes and report.evaluations

    # The ground truth took the judgment mapping, not the cert vocabulary: the
    # cert axis has no member for a judgment, and `actual_granted` carries the
    # declared merits binary so one Brier formula serves every stage.
    outcome = read_model(report.outcomes[0], Outcome)
    assert outcome.judgment == Judgment.reversed
    assert outcome.actual_disposition == Disposition.other
    assert outcome.actual_granted == 1
    # No votes: the terminal docket entry discloses no participating count, so
    # the writer records none and the mandatory vote block stays unscored.
    assert outcome.votes == []

    # The prediction carries the merits contract — a judgment with its
    # mandatory vote block — and answers the whole declared `merits-v1` set,
    # whose one claim restates the headline probability exactly (a divergent
    # pair voids the block at stamp time).
    prediction_path = next(p for p in report.predictions if p.name == "prediction.json")
    prediction = read_model(prediction_path, Prediction)
    assert prediction.judgment == Judgment.affirmed
    assert prediction.votes
    assert prediction.claims is not None
    assert [c.claim_id for c in prediction.claims] == [CLAIM_JUDGMENT_DISTURBED]
    assert prediction.claims[0].probability == prediction.probability

    # Scored on the merits axes: the stub's affirmed/0.0 floor against a
    # reversed outcome is a judgment mismatch and a full Brier miss, and
    # `correct` is the judgment comparison rather than the disposition one.
    # `vote_accuracy` is null because the outcome names no Justice — the
    # intersection rule, so a banked vote block costs nothing.
    evaluation_path = next(p for p in report.evaluations if p.name == "evaluation.json")
    evaluation = read_model(evaluation_path, Evaluation)
    assert evaluation.correct == 0
    assert evaluation.judgment_correct == 0
    assert evaluation.brier_score == 1.0
    assert evaluation.vote_accuracy is None
    assert evaluation.segment_base_rate is None
    assert evaluation.claim_scores is None

    # The leaderboard build puts the cell in the unranked `merits` stages
    # block; nothing enters the ranked cert board from this ledger.
    board = build_leaderboard(iter_stratified_evaluations(data_root, frozen_only=False))
    assert "merits" in board.stages
    assert board.stages["merits"].evaluations_total >= 1
    assert board.evaluations_total == 0


def test_stub_cert_prediction_carries_the_declared_claims(tmp_path: Path) -> None:
    """A cert cell's stub prediction answers the whole declared cert-v1 set.

    The claim_scores block itself is stamped by the workflow's post-agent
    `stamp-cell` step, which the cascade deliberately does not run — production
    computes it harness-side, never in the cell — so the block's computation is
    asserted at its unit seam (`tests/test_claims.py` over `score_claims`).
    What the cascade can prove offline is the prediction-side contract: the
    stub answers every declared claim, in declared order, with the disposition
    claim restating the headline probability exactly (a divergent pair voids
    the block at stamp time).
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)

    report = run_cascade(
        corpus_db_path=db,
        data_root=tmp_path / "data",
        config_root=CONFIG_ROOT,
        court="scotus",
        docket=304,
        run_id=RUN,
    )

    assert report.valid, report.problems
    prediction_path = next(p for p in report.predictions if p.name == "prediction.json")
    prediction = read_model(prediction_path, Prediction)
    assert prediction.claims is not None
    assert [c.claim_id for c in prediction.claims] == [
        CLAIM_DISPOSITION,
        CLAIM_RELIST_INCREMENT,
        CLAIM_CVSG_INCREMENT,
    ]
    disposition = next(c for c in prediction.claims if c.claim_id == CLAIM_DISPOSITION)
    assert disposition.probability == prediction.probability


def test_require_predictions_fails_a_cell_that_produced_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The engine-smoke guard: a real agent that finishes "blocked" exits 0
    with a validly-empty ledger, and the cascade would report green around an
    empty cell — `--require-predictions` turns that into a failure."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    env = {
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
    }
    args = ["local-cascade", "--court", "ca9", "--docket", "103", "--require-predictions"]

    # The stub writes its prediction pair, so the guard is quiet.
    ok = CliRunner().invoke(app, args, env=env)
    assert ok.exit_code == 0, ok.output

    class _BlockedRunner:
        """An engine that exits 0 without writing any artifact."""

        def run(self, request: object) -> list[Path]:
            return []

    monkeypatch.setattr(cascade, "get_runner", lambda *_: _BlockedRunner())
    blocked = CliRunner().invoke(app, args, env=env)
    assert blocked.exit_code == 1
    assert "no predictor cell wrote a prediction" in blocked.output
