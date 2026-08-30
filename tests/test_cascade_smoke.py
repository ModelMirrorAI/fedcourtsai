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
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import build_leaderboard
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cascade
from fedcourtsai.pipeline.cascade import CascadeReport, run_cascade
from fedcourtsai.pipeline.claims import (
    CLAIM_AMICUS_INCREMENT,
    CLAIM_CVSG_INCREMENT,
    CLAIM_DISPOSITION,
    CLAIM_DISSENT_FROM_DENIAL,
    CLAIM_INTERIM_DISPOSITION,
    CLAIM_JUDGMENT_DISTURBED,
    CLAIM_REFERRAL_INCREMENT,
    CLAIM_RELIST_INCREMENT,
    CLAIM_RESPONSE_REQUESTED_INCREMENT,
    CLAIM_SUMMARY_ROUTE,
)
from fedcourtsai.pipeline.runner import RunRequest, get_runner
from fedcourtsai.pipeline.semantic import (
    SEMANTIC_MERITS_V1,
    SEMANTIC_SET_V1,
    graded_units,
    ordinal,
)
from fedcourtsai.registry import enabled_evaluators
from fedcourtsai.schemas import (
    Disposition,
    Evaluation,
    Judgment,
    Outcome,
    Prediction,
    SemanticSupport,
    UsageRole,
)
from fedcourtsai.serialize import read_model
from fedcourtsai.store import iter_stratified_evaluations

#: The declared cert set, in reporting order — every cert moment carries it.
_CERT_CLAIM_IDS = [
    CLAIM_DISPOSITION,
    CLAIM_RELIST_INCREMENT,
    CLAIM_CVSG_INCREMENT,
    CLAIM_SUMMARY_ROUTE,
    CLAIM_DISSENT_FROM_DENIAL,
]

CONFIG_ROOT = Path("config")
RUN = "20260628T120000Z"

#: The fixture's plain resolved cert petition — one event, one outcome, no
#: second moment. The scheduled-evaluate round below predicts this case and only
#: this case, so the backlog it then derives from the whole corpus has exactly
#: one case in it and the assertions can name what was planned.
BACKLOG_CASE = ("scotus", 304)
BACKLOG_EVENT = "evt-petition-disposition"


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
    # scotus/308 is granted and judged → the merits cell contract end to end.
    resolved = _run("ca9", 101)
    open_case = _run("ca9", 103)
    merits = _run("scotus", 308)

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
    assert merits_case.case_id == "scotus/308"

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
    motion-baseline event carries `Stage.interim`: provision → stub predict (the
    whole declared `interim-v1` set) → interim outcome (a granted stay, the
    interim escalation block and no cert `signals` block) → evaluate →
    validate, then the leaderboard build segments the cell into the unranked
    `interim` stages block, never the cert board.

    What this proves is the *composition* — an interim cell reaches every stage
    and lands in the right block. The rules it composes are pinned at their own
    seams, because the stub writes no skill fields and the cascade runs no
    stamp step, so the null skill/claim-score fields here would read null for
    any cell: the band suppression in
    ``tests/test_cli_provision.py::test_an_application_snapshot_freezes_no_band``,
    the interim baseline in ``tests/test_evaluate.py``'s ``segment_base_rate``
    cases, the interim ``signals`` guard in ``tests/test_cascade.py``, and the
    claim resolvers and baselines in ``tests/test_claims.py`` /
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
    # The interim block is there instead, the resolution end of the three
    # escalation increments (the fixture row carries all four latched columns).
    outcome = read_model(report.outcomes[0], Outcome)
    assert outcome.actual_granted == 1
    assert outcome.signals is None
    assert outcome.interim_signals is not None

    # The interim baseline moment declares `interim-v1`, so the stub prediction
    # answers all four claims — the prompt's declared-set rule, exercised offline.
    prediction_path = next(p for p in report.predictions if p.name == "prediction.json")
    claims = read_model(prediction_path, Prediction).claims
    assert claims is not None
    assert [claim.claim_id for claim in claims] == [
        CLAIM_INTERIM_DISPOSITION,
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    ]

    # The cell is scored on the probability: stub P=0.0 against a granted stay.
    # The skill and claim fields are null, which the stub would write for any
    # cell — the interim rules behind them are pinned at the seams named above.
    evaluation_path = next(p for p in report.evaluations if p.name == "evaluation.json")
    evaluation = read_model(evaluation_path, Evaluation)
    assert evaluation.brier_score == 1.0
    assert evaluation.correct == 0
    assert evaluation.segment_base_rate is None
    assert evaluation.claim_scores is None

    # No semantic set is declared off the merits moments, so the grader writes
    # no block — the counterpart of the prediction carrying no `semantic_claims`.
    assert evaluation.semantic_grades is None

    # The leaderboard build puts the cell in the unranked `interim@arrival`
    # stages block — the event's moment stamp survives resolution, so the cell
    # aggregates under its moment rather than falling to the bare stage-known-
    # moment-not block; nothing enters the ranked cert board from this ledger.
    board = build_leaderboard(iter_stratified_evaluations(data_root, frozen_only=False))
    assert "interim@arrival" in board.stages
    assert board.stages["interim@arrival"].evaluations_total >= 1
    assert board.evaluations_total == 0


def test_stub_cascade_merits_smoke(tmp_path: Path) -> None:
    """The fixture's granted docket runs the merits cell end to end offline.

    scotus/308's cert grant opened a merits proceeding, so it carries the
    `evt-order-judgment` event the grant mints (kind `order`, `Stage.merits`):
    provision → stub predict (a judgment with its mandatory vote block, and the
    whole declared `merits-v1` set) → merits outcome off the judgment axis →
    evaluate → validate, then the leaderboard build segments the cell into the
    unranked `merits` stages block, never the cert board.

    Addressed by event id, because the merits docket carries its resolved cert
    baseline beside the judgment event: without it the cascade would target
    the baseline too and the assertions would read a mixed ledger.

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
    assert merits_case.case_id == "scotus/308"  # the literals the call below uses

    report = run_cascade(
        corpus_db_path=db,
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court="scotus",
        docket=308,
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

    # It also answers the declared *semantic* set — the one stage that carries
    # one — with a proposition per claim and no probability anywhere in it.
    assert prediction.semantic_claims is not None
    assert [c.claim_id for c in prediction.semantic_claims] == [
        spec.claim_id for spec in SEMANTIC_MERITS_V1
    ]

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

    # The grader answers the same declared set, and every grade is the
    # availability mask: both claims require a majority opinion and the fixture
    # corpus holds none, so the block accumulates while the census stays empty.
    assert evaluation.semantic_grades is not None
    assert evaluation.semantic_grades.declared_set_version == SEMANTIC_SET_V1
    assert [g.grade for g in evaluation.semantic_grades.grades] == [
        SemanticSupport.not_addressed
    ] * len(SEMANTIC_MERITS_V1)
    units = graded_units(evaluation)
    assert units and all(ordinal(u.grade) is None for u in units)

    # The leaderboard build puts the cell in the unranked `merits@grant`
    # stages block — the event's moment stamp survives resolution, so the cell
    # aggregates under its moment rather than falling to the bare stage-known-
    # moment-not block; nothing enters the ranked cert board from this ledger.
    board = build_leaderboard(iter_stratified_evaluations(data_root, frozen_only=False))
    assert "merits@grant" in board.stages
    assert board.stages["merits@grant"].evaluations_total >= 1
    assert board.evaluations_total == 0


def test_stub_cascade_cvsg_smoke(tmp_path: Path) -> None:
    """The fixture's CVSG docket runs the cert re-forecast cell end to end offline.

    scotus/307 is a petition denied after a Call for the Views of the Solicitor
    General, so beside its resolved cert baseline it carries the resolved
    `evt-order-cvsg-disposition` event the CVSG mints (kind `order`,
    `Stage.cert`, opened at the CVSG date): provision → stub predict (the whole
    declared `cert-v2` set, since both cert moments declare the same claims) →
    a cert-vocabulary outcome off the row's disposition → evaluate → validate.

    What this proves is the *composition* — a later-moment cert cell reaches
    every stage under the cert contract. The rules it composes are pinned at
    their own seams: the fan-out admission and the switched-off-moment refusal
    in ``tests/test_store.py``, the mint's open-first-moment guard in
    ``tests/test_moments.py``, and the claim-board population filter in
    ``tests/test_claim_metrics.py``.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    cvsg_case = fixture.add_cvsg_fixture(db)
    data_root = tmp_path / "data"
    assert cvsg_case.case_id == "scotus/307"  # the literals the call below uses

    report = run_cascade(
        corpus_db_path=db,
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court="scotus",
        docket=307,
        event="evt-order-cvsg-disposition",
        run_id=RUN,
    )

    assert report.valid, report.problems
    assert report.events == ("evt-order-cvsg-disposition",)
    assert report.predictions and report.outcomes and report.evaluations

    # The ground truth took the cert vocabulary — the CVSG moment re-forecasts
    # the same petition disposition, not a different quantity — with the cert
    # signals block frozen in (this is a cert docket, not an application).
    outcome = read_model(report.outcomes[0], Outcome)
    assert outcome.actual_disposition == Disposition.denied
    assert outcome.actual_granted == 0
    assert outcome.signals is not None
    assert outcome.signals.cvsg_date == cvsg_case.cvsg_date

    # The prediction answers the whole declared cert-v2 set — the same set the
    # baseline declares, because the claims do not change with the moment —
    # with the disposition claim restating the headline probability exactly.
    prediction_path = next(p for p in report.predictions if p.name == "prediction.json")
    prediction = read_model(prediction_path, Prediction)
    assert prediction.claims is not None
    assert [c.claim_id for c in prediction.claims] == _CERT_CLAIM_IDS
    assert prediction.claims[0].probability == prediction.probability
    assert prediction.judgment is None  # the cert contract, not the merits one

    # Scored on the cert axes: the stub's denied/0.0 floor against the denied
    # outcome is a correct call and a perfect Brier score.
    evaluation_path = next(p for p in report.evaluations if p.name == "evaluation.json")
    evaluation = read_model(evaluation_path, Evaluation)
    assert evaluation.correct == 1
    assert evaluation.brier_score == 0.0


def test_stub_cert_prediction_carries_the_declared_claims(tmp_path: Path) -> None:
    """A cert cell's stub prediction answers the whole declared cert-v2 set.

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
    assert [c.claim_id for c in prediction.claims] == _CERT_CLAIM_IDS
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


def _backlog_matrix(env: dict[str, str]) -> list[dict[str, Any]]:
    """The evaluate matrix the *scheduled* plan job derives.

    No ``--body-file`` and no ``--court``/``--docket``, which is how
    ``evaluate-matrix`` is told to take its cases from the corpus-level backlog.
    Omitting the flag and blanking it are different requests — an empty body
    file carries no ```json block and is refused outright — so the workflow
    builds the argument up rather than passing an empty one, and so does this.
    """
    result = CliRunner().invoke(app, ["evaluate-matrix", "--run-id", RUN], env=env)
    assert result.exit_code == 0, result.output
    include = json.loads(result.stdout)["include"]
    assert isinstance(include, list)
    return include


def test_stub_scheduled_evaluate_round_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A whole scheduled evaluate round, offline: backlog → cells → validate.

    The other smokes drive evaluate the way a *labelled* run does — the cases
    come from a trigger issue, and ``run_cascade`` grades whatever it just
    predicted in the same breath. The scheduled lane works the other way round:
    it runs over a ledger some earlier round committed, and derives its own work
    from committed state (resolved event + prediction + no evaluation). That
    derivation is the only thing standing between a dropped evaluate run and a
    grading lost for good, and until a round actually runs, nothing executes it
    end to end — the deriver is unit-tested in ``tests/test_evaluate_backlog.py``
    and the fan-out gates in ``tests/test_cli_matrix.py``, but no test carries a
    ledger from predict through a *derived* matrix to a validated grading.

    So: predict one case with the evaluators held off, derive the matrix from
    the backlog, run the cells it planned, and validate. The closing assertion
    is the one that says the round *completed* rather than merely ran — the
    re-derivation comes back empty, because the backlog the deriver watches has
    been drained.
    """
    court, docket = BACKLOG_CASE
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    data_root = tmp_path / "data"
    env = {
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),
        "FEDCOURTS_DATA_ROOT": str(data_root),
    }

    # The predict round: provision + predict + ground truth, and no grading.
    # Holding the evaluators off is what leaves a backlog to derive — it is the
    # committed state a dropped evaluate run leaves behind, reached here without
    # having to fail a run to get it.
    monkeypatch.setattr(cascade, "enabled_evaluators", lambda _path: [])
    predicted = run_cascade(
        corpus_db_path=db,
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court=court,
        docket=docket,
        run_id=RUN,
    )
    monkeypatch.setattr(cascade, "enabled_evaluators", enabled_evaluators)

    assert predicted.valid, predicted.problems
    assert predicted.events == (BACKLOG_EVENT,)
    assert predicted.predictions and predicted.outcomes
    assert not predicted.evaluations

    # The derivation, over the whole corpus rather than a named case: every
    # other resolved SCOTUS event in the fixture is unpredicted, and an event
    # with nothing to score is not owed — so the backlog is exactly this case.
    planned = _backlog_matrix(env)
    assert planned, "the backlog owes this case's gradings; a derived round would mint nothing"
    assert {(cell["court"], cell["docket"], cell["event_id"]) for cell in planned} == {
        (court, docket, BACKLOG_EVENT)
    }
    judges = {evaluator.id for evaluator in enabled_evaluators(CONFIG_ROOT / "evaluators.yaml")}
    assert {str(cell["evaluator_id"]) for cell in planned} == judges
    assert {cell["run_id"] for cell in planned} == {RUN}

    # The cells the matrix planned, run through the cascade's own evaluate stage
    # — called directly rather than through `run_cascade`, so the round grades
    # without re-predicting, which is the shape of the lane under test. That
    # seam rather than a hand-composed loop because it *is* the blind-grading
    # bracket (stage the candidates under aliases → run the judge → un-alias),
    # the contract `run-evaluate` puts around its agent step: composing it here
    # would fork a contract that must not drift. It fans out over the enabled
    # evaluators, asserted above to be exactly the planned set.
    runner = get_runner("stub")

    def _request(role: UsageRole, actor: str, prompt: str, event_id: str) -> RunRequest:
        return RunRequest(
            role=role,
            court_id=court,
            docket_id=docket,
            event_id=event_id,
            actor_id=actor,
            run_id=RUN,
            prompt=Path(prompt),
            data_root=data_root,
        )

    written: list[Path] = []
    for event_id in sorted({str(cell["event_id"]) for cell in planned}):
        written.extend(
            cascade._evaluate_event(
                runner=runner,
                request=_request,
                event_paths=CasePaths(data_root, court, docket).event(event_id),
                data_root=data_root,
                config_root=CONFIG_ROOT,
                court=court,
                docket=docket,
                event_id=event_id,
                run_id=RUN,
                map_dir=data_root.parent / ".blinding",
            )
        )
    assert [path for path in written if path.name == "evaluation.json"]

    # Every planned cell landed its judge's grading, not just some of them.
    for cell in planned:
        event_paths = CasePaths(data_root, court, docket).event(str(cell["event_id"]))
        graded = event_paths.evaluator_dir(str(cell["evaluator_id"]))
        assert list(graded.glob("*/*/evaluation.json")), (
            f"the matrix planned {cell['evaluator_id']} on {cell['event_id']} but it graded nothing"
        )

    # The round's ledger passes the same gate the run PR would be checked by.
    validated = CliRunner().invoke(app, ["validate", str(data_root)])
    assert validated.exit_code == 0, validated.output

    # And the backlog is drained — the lane's resting state — so the next
    # scheduled cycle re-derives nothing. A round that graded only some of what
    # it planned would still be owed here.
    assert _backlog_matrix(env) == []
