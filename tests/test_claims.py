"""Tests for the harness-declared claim sets and their scoring.

`pipeline.claims` owns the declaration table, the resolvers (with the
availability mask), the strictly-prior baselines, and the `score_claims`
orchestrator; the scoring *rule* itself is pinned in `test_claim_scoring.py`.
The invariants worth pinning here: the cert set is exactly the three declared
claims in a stable order, resolution reads only committed artifacts and masks
what the record does not disclose, baselines never see the case's own Term, and
an old prediction without the claims/context blocks yields no block rather than
a crash — and the validate-time report (`claim_block_problems`) moves with the
scorer's refusals in both directions.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from fedcourtsai.pipeline.claims import (
    CLAIM_CVSG_INCREMENT,
    CLAIM_DISPOSITION,
    CLAIM_JUDGMENT_DISTURBED,
    CLAIM_RELIST_INCREMENT,
    CLAIM_SET_CERT_V1,
    CLAIM_SET_MERITS_V1,
    claim_baseline,
    claim_block_problems,
    declared_claim_set,
    resolve_claim,
    score_claims,
)
from fedcourtsai.pipeline.judgment import judgment_disturbed
from fedcourtsai.schemas import (
    BaseRateBucket,
    ClaimProbability,
    ClaimScoreBlock,
    Disposition,
    Engine,
    Evaluation,
    Judgment,
    JusticeVote,
    Outcome,
    Prediction,
    PredictionContext,
    ResolutionSignals,
    StatPack,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackTerm,
    StatPackTermSegment,
    VoteValue,
)
from fedcourtsai.serialize import read_model, write_json

_EVENT_ID = "evt-petition-writ-of-certiorari"


def _context(
    *,
    band: str | None = "baseline",
    term: int | None = 2025,
    distribution_count: int | None = 1,
    cvsg_date: date | None = None,
    signals_observable: bool = True,
) -> PredictionContext:
    return PredictionContext(
        mode="forward",
        snapshot_date=date(2025, 3, 1),
        signals_observable=signals_observable,
        distribution_count=distribution_count,
        cvsg_date=cvsg_date,
        band=band,
        salience_version="sal-v1" if band else None,
        term=term,
    )


def _prediction(
    *,
    claims: list[ClaimProbability] | None,
    context: PredictionContext | None,
    event_id: str = _EVENT_ID,
    probability: float = 0.2,
) -> Prediction:
    return Prediction(
        case_id="scotus/1",
        event_id=event_id,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 3, 1),
        input_snapshot="x",
        granted=int(probability >= 0.5),
        probability=probability,
        predicted_disposition=Disposition.granted if probability >= 0.5 else Disposition.denied,
        context=context,
        claims=claims,
    )


_UNMOVED = object()  # sentinel: the default signals block, distinct from an explicit None


def _outcome(*, granted: int = 0, signals: ResolutionSignals | object | None = _UNMOVED) -> Outcome:
    if signals is _UNMOVED:
        signals = ResolutionSignals(distribution_count=1)
    assert signals is None or isinstance(signals, ResolutionSignals)
    return Outcome(
        case_id="scotus/1",
        event_id=_EVENT_ID,
        resolved_at=date(2025, 6, 1),
        actual_disposition=Disposition.granted if granted else Disposition.denied,
        actual_granted=granted,
        signals=signals,
    )


def _term(year: int, *, rate: float, n: int = 100) -> StatPackTerm:
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(),
        salience_version="sal-v1",
        segments=[
            StatPackTermSegment(
                band="baseline",
                weighted_resolved=n,
                est_grant_rate=0.99,  # decoy: the frozen band must read the risk-set rate
                prefix_weighted_resolved=n,
                prefix_est_grant_rate=rate,
            )
        ],
    )


def _statpack(*terms: StatPackTerm) -> StatPack:
    return StatPack(corpus_rows=1, terms=list(terms))


def _claims(
    disposition: float = 0.2, relist: float = 0.5, cvsg: float = 0.05
) -> list[ClaimProbability]:
    return [
        ClaimProbability(claim_id=CLAIM_DISPOSITION, probability=disposition),
        ClaimProbability(claim_id=CLAIM_RELIST_INCREMENT, probability=relist),
        ClaimProbability(claim_id=CLAIM_CVSG_INCREMENT, probability=cvsg),
    ]


# --- the declaration table --------------------------------------------------------


def test_the_cert_set_is_exactly_the_three_claims_in_stable_order() -> None:
    declared = declared_claim_set(_EVENT_ID)
    assert declared is not None
    version, claim_ids = declared
    assert version == CLAIM_SET_CERT_V1
    assert claim_ids == (CLAIM_DISPOSITION, CLAIM_RELIST_INCREMENT, CLAIM_CVSG_INCREMENT)


def test_kinds_without_a_declaration_declare_nothing() -> None:
    # A motion has no declared set, and a malformed id declares nothing rather
    # than guessing a kind.
    assert declared_claim_set("evt-motion-stay-pending-appeal") is None
    assert declared_claim_set("evt-order-x") is None
    assert declared_claim_set("not-an-event-id") is None
    assert declared_claim_set("evt-") is None
    assert declared_claim_set("evt-petition-") is None  # empty label: malformed, no set


# --- resolvers: committed artifacts in, {0, 1, mask} out --------------------------


def test_disposition_resolves_the_grant_flag() -> None:
    ctx = _context()
    assert resolve_claim(CLAIM_DISPOSITION, ctx, _outcome(granted=1)) == 1
    assert resolve_claim(CLAIM_DISPOSITION, ctx, _outcome(granted=0)) == 0


def test_relist_increment_is_about_the_rise_not_the_level() -> None:
    ctx = _context(distribution_count=1)
    unmoved = _outcome(signals=ResolutionSignals(distribution_count=1))
    rose = _outcome(signals=ResolutionSignals(distribution_count=3))
    assert resolve_claim(CLAIM_RELIST_INCREMENT, ctx, unmoved) == 0
    assert resolve_claim(CLAIM_RELIST_INCREMENT, ctx, rose) == 1


def test_relist_increment_is_masked_where_either_end_is_undisclosed() -> None:
    # No prediction-time count (proceedings unobservable) -> no increment to
    # resolve; same for an outcome that froze no signals block.
    blind = _context(distribution_count=None, signals_observable=False, band=None)
    assert resolve_claim(CLAIM_RELIST_INCREMENT, blind, _outcome()) is None
    assert resolve_claim(CLAIM_RELIST_INCREMENT, _context(), _outcome(signals=None)) is None


def test_cvsg_increment_truth_table() -> None:
    ctx = _context(cvsg_date=None)
    none_to_none = _outcome(signals=ResolutionSignals(distribution_count=1))
    none_to_date = _outcome(
        signals=ResolutionSignals(distribution_count=1, cvsg_date=date(2025, 4, 1))
    )
    assert resolve_claim(CLAIM_CVSG_INCREMENT, ctx, none_to_none) == 0
    assert resolve_claim(CLAIM_CVSG_INCREMENT, ctx, none_to_date) == 1


def test_cvsg_increment_is_vacuous_with_a_cvsg_already_on_the_docket() -> None:
    # A cvsg_date, once set, stays set: there is nothing left to forecast, so
    # the claim is masked for the cell — a property of the record.
    ctx = _context(cvsg_date=date(2025, 1, 15))
    resolved = _outcome(
        signals=ResolutionSignals(distribution_count=2, cvsg_date=date(2025, 1, 15))
    )
    assert resolve_claim(CLAIM_CVSG_INCREMENT, ctx, resolved) is None


def test_cvsg_increment_is_masked_where_absence_is_ambiguous() -> None:
    # signals_observable=False means the null cvsg_date is "nobody looked", not
    # "no CVSG" — reading it as a prediction-time state would invent a fact.
    blind = _context(distribution_count=None, signals_observable=False, band=None)
    assert resolve_claim(CLAIM_CVSG_INCREMENT, blind, _outcome()) is None
    assert resolve_claim(CLAIM_CVSG_INCREMENT, _context(), _outcome(signals=None)) is None


# --- baselines: strictly prior, or honestly absent --------------------------------


def test_the_disposition_baseline_never_sees_the_cases_own_term() -> None:
    pack = _statpack(
        _term(2025, rate=0.90),  # the case's own Term: must not contribute
        _term(2024, rate=0.06),
    )
    ctx = _context(term=2025)
    assert claim_baseline(CLAIM_DISPOSITION, ctx, pack, lookback_terms=0) == pytest.approx(0.06)


def test_the_increment_baselines_are_none_until_the_statpack_carries_the_cut() -> None:
    # The committed pack's relist/CVSG cuts pool every Term (the case's own
    # included) and its per-Term surface carries neither, so no strictly-prior
    # conditioned rate is derivable — the honest baseline is no baseline.
    pack = _statpack(_term(2024, rate=0.06))
    ctx = _context()
    assert claim_baseline(CLAIM_RELIST_INCREMENT, ctx, pack, lookback_terms=0) is None
    assert claim_baseline(CLAIM_CVSG_INCREMENT, ctx, pack, lookback_terms=0) is None


# --- score_claims: the assembled block --------------------------------------------


def test_score_claims_end_to_end_matches_the_hand_computed_rule() -> None:
    pack = _statpack(_term(2024, rate=0.06))
    prediction = _prediction(
        claims=_claims(disposition=0.2, relist=0.7, cvsg=0.05), context=_context()
    )
    outcome = _outcome(granted=0, signals=ResolutionSignals(distribution_count=3))
    block = score_claims(prediction, outcome, pack, lookback_terms=0)
    assert block is not None
    assert block.declared_set_version == CLAIM_SET_CERT_V1
    by_id = {row.claim_id: row for row in block.claims}
    assert list(by_id) == [CLAIM_DISPOSITION, CLAIM_RELIST_INCREMENT, CLAIM_CVSG_INCREMENT]

    # Disposition: y=0, b=0.06, p=0.2 -> (0.06-0)^2 - (0.2-0)^2.
    disposition = by_id[CLAIM_DISPOSITION]
    assert disposition.outcome == 0
    assert disposition.baseline == pytest.approx(0.06)
    assert disposition.score == pytest.approx(0.06**2 - 0.2**2)

    # Relist increment resolved true (1 -> 3) but has no baseline -> unscored.
    relist = by_id[CLAIM_RELIST_INCREMENT]
    assert relist.outcome == 1
    assert relist.baseline is None and relist.score is None

    # The total sums only the scored claims; the floor is the realized total of
    # the baseline-reporting control, which is exactly zero.
    assert block.total == pytest.approx(0.06**2 - 0.2**2)
    assert block.floor == 0.0
    assert block.lift == pytest.approx(block.total)


def test_restating_the_baseline_totals_exactly_zero() -> None:
    # p == b scores 0.0 exactly — the two Brier terms are the same expression —
    # so the block's total and lift are exact zeros, not approximate ones.
    pack = _statpack(_term(2024, rate=0.06))
    prediction = _prediction(claims=_claims(disposition=0.06), context=_context(), probability=0.06)
    block = score_claims(prediction, _outcome(granted=0), pack, lookback_terms=0)
    assert block is not None
    assert block.total == 0.0
    assert block.lift == 0.0


def test_a_divergent_disposition_claim_voids_the_block() -> None:
    # The disposition claim restates the headline probability; a pair that
    # diverges is two committed numbers for one belief — malformed, so no
    # block, never a silent pick between them.
    pack = _statpack(_term(2024, rate=0.06))
    divergent = _prediction(claims=_claims(disposition=0.3), context=_context(), probability=0.2)
    assert score_claims(divergent, _outcome(), pack, lookback_terms=0) is None


def test_a_block_with_nothing_scored_carries_no_total() -> None:
    # Every claim masked or baseline-less -> rows exist, numbers do not: the
    # honest answer is None, never a fabricated 0.
    pack = _statpack(_term(2024, rate=0.06))
    blind = _context(band=None, distribution_count=None, signals_observable=False)
    prediction = _prediction(claims=_claims(), context=blind)
    block = score_claims(prediction, _outcome(signals=None), pack, lookback_terms=0)
    assert block is not None
    assert block.total is None and block.floor is None and block.lift is None
    assert all(row.score is None for row in block.claims)


def test_an_old_prediction_yields_no_block_not_a_crash() -> None:
    # Every committed prediction predates both blocks; scoring one is a no-op.
    pack = _statpack(_term(2024, rate=0.06))
    old = _prediction(claims=None, context=None)
    assert score_claims(old, _outcome(), pack, lookback_terms=0) is None


def test_the_mandatory_set_scores_all_or_nothing() -> None:
    pack = _statpack(_term(2024, rate=0.06))
    partial = _prediction(claims=_claims()[:2], context=_context())
    assert score_claims(partial, _outcome(), pack, lookback_terms=0) is None
    duplicated = _prediction(claims=[*_claims(), _claims()[0]], context=_context())
    assert score_claims(duplicated, _outcome(), pack, lookback_terms=0) is None


def test_claim_block_problems_names_exactly_what_the_scorer_voids() -> None:
    """The validate-time report and the scorer's silent refusals move together:
    every malformed shape `score_claims` voids on yields a named problem, and
    the shapes it accepts (or legitimately skips) yield none — so `validate`
    can never pass a block the board will silently drop, nor flag one it
    would score."""
    pack = _statpack(_term(2024, rate=0.06))
    voids = {
        "divergent headline": _prediction(
            claims=_claims(disposition=0.3), context=_context(), probability=0.2
        ),
        "partial set": _prediction(claims=_claims()[:2], context=_context()),
        "duplicated id": _prediction(claims=[*_claims(), _claims()[0]], context=_context()),
    }
    for label, prediction in voids.items():
        assert score_claims(prediction, _outcome(), pack, lookback_terms=0) is None, label
        assert claim_block_problems(prediction), label
    # A missing context also voids at scoring, but it is a tolerated
    # provisioning gap (a harness stamp, not the agent's block), so the
    # report deliberately stays silent on it.
    unprovisioned = _prediction(claims=_claims(), context=None)
    assert score_claims(unprovisioned, _outcome(), pack, lookback_terms=0) is None
    assert claim_block_problems(unprovisioned) == []
    # Absence is legitimate, not a defect: no block, or no declared set.
    assert claim_block_problems(_prediction(claims=None, context=None)) == []
    assert (
        claim_block_problems(
            _prediction(claims=_claims(), context=_context(), event_id="evt-motion-stay")
        )
        == []
    )
    # Coherent blocks report nothing AND score — including one with an
    # undeclared extra, which the scorer ignores rather than voids.
    coherent = _prediction(claims=_claims(), context=_context())
    assert claim_block_problems(coherent) == []
    assert score_claims(coherent, _outcome(), pack, lookback_terms=0) is not None
    extra = ClaimProbability(claim_id="own-invention", probability=0.9)
    extra_block = _prediction(claims=[*_claims(), extra], context=_context())
    assert claim_block_problems(extra_block) == []
    assert score_claims(extra_block, _outcome(), pack, lookback_terms=0) is not None


def test_undeclared_stated_claims_are_ignored() -> None:
    # The declaration, not the census, fixes what is scored: an extra claim id
    # neither blocks the set nor earns a row.
    pack = _statpack(_term(2024, rate=0.06))
    extra = ClaimProbability(claim_id="own-invention", probability=0.9)
    prediction = _prediction(claims=[*_claims(), extra], context=_context())
    block = score_claims(prediction, _outcome(), pack, lookback_terms=0)
    assert block is not None
    assert [row.claim_id for row in block.claims] == [
        CLAIM_DISPOSITION,
        CLAIM_RELIST_INCREMENT,
        CLAIM_CVSG_INCREMENT,
    ]


def test_events_without_a_declared_set_yield_no_block() -> None:
    pack = _statpack(_term(2024, rate=0.06))
    motion = _prediction(claims=_claims(), context=_context(), event_id="evt-motion-stay")
    assert score_claims(motion, _outcome(), pack, lookback_terms=0) is None


# --- the schema surface round-trips through serialize -----------------------------


def test_prediction_claims_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "prediction.json"
    write_json(path, _prediction(claims=_claims(), context=_context()))
    read = read_model(path, Prediction)
    assert read.claims is not None
    assert [claim.claim_id for claim in read.claims] == [
        CLAIM_DISPOSITION,
        CLAIM_RELIST_INCREMENT,
        CLAIM_CVSG_INCREMENT,
    ]


def test_evaluation_claim_scores_round_trip(tmp_path: Path) -> None:
    pack = _statpack(_term(2024, rate=0.06))
    prediction = _prediction(claims=_claims(), context=_context())
    block = score_claims(prediction, _outcome(), pack, lookback_terms=0)
    assert block is not None
    evaluation = Evaluation(
        case_id="scotus/1",
        event_id=_EVENT_ID,
        predictor_id="p",
        evaluator_id="e",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 6, 2),
        correct=1,
        claim_scores=block,
    )
    path = tmp_path / "evaluation.json"
    write_json(path, evaluation)
    read = read_model(path, Evaluation)
    assert read.claim_scores is not None
    assert isinstance(read.claim_scores, ClaimScoreBlock)
    assert read.claim_scores.model_dump() == block.model_dump()


# --- the merits set: judgment-disturbed under merits-v1 ---------------------------

_MERITS_EVENT = "evt-order-judgment"


def _merits_pack(*, rate_terms: dict[int, tuple[int, int]]) -> StatPack:
    """A pack whose merits section carries ``term -> (disturbed, parsed)``."""
    terms = [
        StatPackMeritsTerm(term=year, disturbed=d, parsed=p)
        for year, (d, p) in sorted(rate_terms.items(), reverse=True)
    ]
    return StatPack(
        corpus_rows=1,
        merits=StatPackMerits(
            parsed=sum(t.parsed for t in terms),
            disturbed=sum(t.disturbed for t in terms),
            terms=terms,
        ),
    )


def _merits_prediction(
    *, probability: float = 0.7, claim: float | None = 0.7, context: PredictionContext | None = None
) -> Prediction:
    claims = (
        None
        if claim is None
        else [ClaimProbability(claim_id=CLAIM_JUDGMENT_DISTURBED, probability=claim)]
    )
    return Prediction(
        case_id="scotus/1",
        event_id=_MERITS_EVENT,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 3, 1),
        input_snapshot="x",
        granted=int(probability >= 0.5),
        probability=probability,
        predicted_disposition=Disposition.other,
        judgment=Judgment.reversed,
        votes=[JusticeVote(justice="roberts", vote=VoteValue.majority)],
        context=context if context is not None else _context(band=None, term=2025),
        claims=claims,
    )


def _merits_outcome(judgment: Judgment) -> Outcome:
    return Outcome(
        case_id="scotus/1",
        event_id=_MERITS_EVENT,
        resolved_at=date(2026, 6, 1),
        actual_disposition=Disposition.other,
        actual_granted=int(judgment_disturbed(judgment)),
        judgment=judgment,
    )


def test_the_merits_event_declares_exactly_the_disturbed_claim() -> None:
    # Keyed on the minted merits event id, not the order kind: any other order
    # event still declares nothing (the `evt-order-x` case above).
    assert declared_claim_set(_MERITS_EVENT) == (CLAIM_SET_MERITS_V1, (CLAIM_JUDGMENT_DISTURBED,))


def test_judgment_disturbed_resolves_through_the_shared_projection() -> None:
    ctx = _context()
    assert resolve_claim(CLAIM_JUDGMENT_DISTURBED, ctx, _merits_outcome(Judgment.reversed)) == 1
    assert resolve_claim(CLAIM_JUDGMENT_DISTURBED, ctx, _merits_outcome(Judgment.vacated)) == 1
    assert resolve_claim(CLAIM_JUDGMENT_DISTURBED, ctx, _merits_outcome(Judgment.affirmed)) == 0
    # The two non-merits exits leave the judgment below standing: undisturbed.
    assert resolve_claim(CLAIM_JUDGMENT_DISTURBED, ctx, _merits_outcome(Judgment.dig)) == 0
    assert (
        resolve_claim(CLAIM_JUDGMENT_DISTURBED, ctx, _merits_outcome(Judgment.equally_divided)) == 0
    )
    # A record without a judgment is masked, never guessed.
    assert resolve_claim(CLAIM_JUDGMENT_DISTURBED, ctx, _outcome(granted=1)) is None


def test_the_disturbed_baseline_is_keyed_on_the_grant_term() -> None:
    pack = _merits_pack(rate_terms={2025: (40, 40), 2024: (24, 40), 2023: (32, 40)})
    ctx = _context(band=None, term=2025)
    # The GRANT Term guards the pool, supplied by the caller from the merits
    # event's opened_at — not the context's docket-number Term, which can run a
    # Term later and would admit the case's own cohort.
    assert claim_baseline(
        CLAIM_JUDGMENT_DISTURBED, ctx, pack, lookback_terms=0, grant_term=2025
    ) == pytest.approx(0.70)
    # No grant Term supplied (every cert cell, and any merits event whose
    # definition could not be read) => unscored, never a docket-Term fallback.
    assert claim_baseline(CLAIM_JUDGMENT_DISTURBED, ctx, pack, lookback_terms=0) is None


def test_the_disturbed_baseline_ignores_the_contexts_docket_term() -> None:
    """A summer-docketed, pre-October grant has docket Term = grant Term + 1.

    Keying on the docket Term would pool the case's own grant cohort — the one
    Term the leakage guard exists to exclude. The frozen context here carries
    the later docket Term while the grant Term is the earlier one; the pool
    must follow the grant Term.
    """
    pack = _merits_pack(rate_terms={2024: (40, 40), 2023: (28, 40)})
    ctx = _context(band=None, term=2025)  # docket Term, one later than the grant
    assert claim_baseline(
        CLAIM_JUDGMENT_DISTURBED, ctx, pack, lookback_terms=0, grant_term=2024
    ) == pytest.approx(0.70)


def test_merits_score_claims_end_to_end() -> None:
    pack = _merits_pack(rate_terms={2024: (28, 40)})
    prediction = _merits_prediction(probability=0.9, claim=0.9, context=_context(band=None))
    block = score_claims(
        prediction,
        _merits_outcome(Judgment.reversed),
        pack,
        lookback_terms=0,
        grant_term=2025,
    )
    assert block is not None and block.declared_set_version == CLAIM_SET_MERITS_V1
    [row] = block.claims
    assert row.claim_id == CLAIM_JUDGMENT_DISTURBED
    assert row.outcome == 1 and row.baseline == pytest.approx(0.70)
    assert row.score == pytest.approx((0.70 - 1) ** 2 - (0.9 - 1) ** 2)
    assert block.floor == 0.0 and block.lift == block.total


def test_a_divergent_disturbed_claim_voids_the_block() -> None:
    # The disturbed claim restates the merits headline probability; a pair that
    # diverges is malformed, exactly as the cert disposition pair is.
    pack = _merits_pack(rate_terms={2024: (7, 10)})
    prediction = _merits_prediction(probability=0.9, claim=0.4)
    assert (
        score_claims(prediction, _merits_outcome(Judgment.reversed), pack, lookback_terms=0) is None
    )
