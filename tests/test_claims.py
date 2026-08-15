"""Tests for the harness-declared claim sets and their scoring.

`pipeline.claims` owns the declaration table, the resolvers (with the
availability mask), the strictly-prior baselines, and the `score_claims`
orchestrator; the scoring *rule* itself is pinned in `test_claim_scoring.py`.
The invariants worth pinning here: each stage's set is exactly its declared
claims in a stable order, resolution reads only committed artifacts and masks
what the record does not disclose, baselines never see the case's own Term, and
an old prediction without the claims/context blocks yields no block rather than
a crash — and the validate-time report (`claim_block_problems`) moves with the
scorer's refusals in both directions.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Literal

import pytest

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
    CLAIM_SET_CERT_V1,
    CLAIM_SET_CERT_V2,
    CLAIM_SET_INTERIM_V1,
    CLAIM_SET_MERITS_V1,
    CLAIM_SUMMARY_ROUTE,
    claim_baseline,
    claim_block_problems,
    declared_claim_set,
    resolve_claim,
    score_claims,
)
from fedcourtsai.pipeline.judgment import judgment_disturbed
from fedcourtsai.schemas import (
    GRANTED_DISPOSITIONS,
    BaseRateBucket,
    ClaimProbability,
    ClaimScoreBlock,
    Disposition,
    DispositionShare,
    Engine,
    Evaluation,
    FeeClass,
    InterimResolutionSignals,
    Judgment,
    JusticeVote,
    Outcome,
    Prediction,
    PredictionContext,
    ResolutionSignals,
    StatPack,
    StatPackInterim,
    StatPackInterimTerm,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackTerm,
    StatPackTermClass,
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


def test_the_kind_keyed_cert_fallback_stays_at_cert_v1s_three_claims() -> None:
    """A petition event that is not a declared moment keeps the older set.

    The kind-keyed table is the fallback for an entry-pinned petition event or a
    legacy id minted before the moment table, and those were elicited under
    cert-v1's contract; scoring them against a larger set would report claims
    their cells were never asked for as unstated. Only the declared moments
    advance — see the cert-v2 section below.
    """
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
        StatPackMeritsTerm(term=year, disturbed=d, parsed=p, cert_order_excluded=0)
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


# --- cert-v2: the summary-route and dissent-from-denial claims ---------------------

#: A declared cert **moment**, which carries `cert-v2`. The module's `_EVENT_ID`
#: is deliberately not one — it exercises the kind-keyed fallback instead.
_CERT_MOMENT = "evt-petition-disposition"


def _cert_v2_claims(
    disposition: float = 0.2,
    relist: float = 0.5,
    cvsg: float = 0.05,
    route: float = 0.3,
    dissent: float = 0.1,
) -> list[ClaimProbability]:
    return [
        *_claims(disposition=disposition, relist=relist, cvsg=cvsg),
        ClaimProbability(claim_id=CLAIM_SUMMARY_ROUTE, probability=route),
        ClaimProbability(claim_id=CLAIM_DISSENT_FROM_DENIAL, probability=dissent),
    ]


def _cert_outcome(
    *,
    disposition: Disposition,
    route: Literal["plenary", "gvr", "summary-merits"] | None = None,
    dissent: bool | None = None,
) -> Outcome:
    return Outcome(
        case_id="scotus/1",
        event_id=_CERT_MOMENT,
        resolved_at=date(2025, 6, 1),
        actual_disposition=disposition,
        actual_granted=int(disposition in GRANTED_DISPOSITIONS),
        signals=ResolutionSignals(distribution_count=1),
        disposition_route=route,
        noted_dissent_from_denial=dissent,
    )


def _shares(counts: dict[str, int]) -> list[DispositionShare]:
    resolved = sum(counts.values())
    return [
        DispositionShare(
            disposition=Disposition(name.replace("_", "-")),
            count=count,
            share=count / resolved,
        )
        for name, count in counts.items()
    ]


def _disposition_term(year: int, *, ifp: dict[str, int] | None = None, **paid: int) -> StatPackTerm:
    """A Term with per-fee-class disposition counts, paid by keyword.

    The Term-level `base_rates` carries the pooled counts the way the real pack
    does, so a baseline reading the wrong surface is visibly wrong rather than
    accidentally right: the IFP block is what separates them.
    """
    ifp_counts = ifp or {}
    pooled = {name: paid.get(name, 0) + ifp_counts.get(name, 0) for name in {*paid, *ifp_counts}}
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(resolved=sum(pooled.values()), dispositions=_shares(pooled)),
        classes=[
            StatPackTermClass(fee_class=FeeClass.paid, dispositions=_shares(paid)),
            *(
                [StatPackTermClass(fee_class=FeeClass.ifp, dispositions=_shares(ifp_counts))]
                if ifp_counts
                else []
            ),
        ],
    )


def test_the_declared_cert_moment_carries_cert_v2s_five_claims() -> None:
    declared = declared_claim_set(_CERT_MOMENT)
    assert declared is not None
    version, claim_ids = declared
    assert version == CLAIM_SET_CERT_V2
    # Append-only against cert-v1's order, so a reader diffing two blocks reads
    # down the same rows.
    assert claim_ids == (
        CLAIM_DISPOSITION,
        CLAIM_RELIST_INCREMENT,
        CLAIM_CVSG_INCREMENT,
        CLAIM_SUMMARY_ROUTE,
        CLAIM_DISSENT_FROM_DENIAL,
    )
    # Every declared cert moment carries the same set — the claims do not change
    # because the forecast was taken later.
    for moment in ("evt-order-cvsg-disposition", "evt-petition-arrival-disposition"):
        assert declared_claim_set(moment) == declared


def test_summary_route_resolves_from_the_committed_marker() -> None:
    ctx = _context()
    granted = Disposition.granted
    assert (
        resolve_claim(CLAIM_SUMMARY_ROUTE, ctx, _cert_outcome(disposition=granted, route="plenary"))
        == 0
    )
    assert (
        resolve_claim(
            CLAIM_SUMMARY_ROUTE, ctx, _cert_outcome(disposition=granted, route="summary-merits")
        )
        == 1
    )
    assert (
        resolve_claim(CLAIM_SUMMARY_ROUTE, ctx, _cert_outcome(disposition=granted, route="gvr"))
        == 1
    )


# --- the interim set: four claims under interim-v1 --------------------------------

_INTERIM_EVENT = "evt-motion-disposition"


def _interim_pack(*, rate_terms: dict[int, tuple[int, int]]) -> StatPack:
    """A pack whose interim section carries ``term -> (granted, resolved)``."""
    terms = [
        StatPackInterimTerm(
            term=year,
            applications=resolved,
            substantive=resolved,
            substantive_resolved=resolved,
            substantive_granted=granted,
        )
        for year, (granted, resolved) in sorted(rate_terms.items(), reverse=True)
    ]
    return StatPack(
        corpus_rows=1,
        interim=StatPackInterim(
            substantive_resolved=sum(t.substantive_resolved for t in terms),
            substantive_granted=sum(t.substantive_granted for t in terms),
            terms=terms,
        ),
    )


def _interim_context(
    *,
    term: int | None = 2026,
    signals_observable: bool = True,
    response_requested: bool | None = False,
    referred_to_court: bool | None = False,
    amicus_briefs: int | None = 0,
) -> PredictionContext:
    """An application cell's frozen context: no band, an application Term, the trio."""
    return PredictionContext(
        mode="forward",
        snapshot_date=date(2026, 3, 1),
        signals_observable=signals_observable,
        band=None,
        salience_version=None,
        response_requested=response_requested,
        referred_to_court=referred_to_court,
        amicus_briefs=amicus_briefs,
        term=term,
    )


_INTERIM_UNMOVED = object()  # sentinel: the default block, distinct from an explicit None


def _interim_outcome(
    *,
    granted: int = 0,
    response_requested: bool = False,
    referred_to_court: bool = False,
    amicus_briefs: int = 0,
    signals: InterimResolutionSignals | object | None = _INTERIM_UNMOVED,
) -> Outcome:
    if signals is _INTERIM_UNMOVED:
        signals = InterimResolutionSignals(
            response_requested=response_requested,
            referred_to_court=referred_to_court,
            amicus_briefs=amicus_briefs,
        )
    assert signals is None or isinstance(signals, InterimResolutionSignals)
    return Outcome(
        case_id="scotus/2",
        event_id=_INTERIM_EVENT,
        resolved_at=date(2026, 6, 1),
        actual_disposition=Disposition.granted if granted else Disposition.denied,
        actual_granted=granted,
        interim_signals=signals,
    )


def _interim_claims(
    disposition: float = 0.1,
    response: float = 0.3,
    referral: float = 0.2,
    amicus: float = 0.4,
) -> list[ClaimProbability]:
    return [
        ClaimProbability(claim_id=CLAIM_INTERIM_DISPOSITION, probability=disposition),
        ClaimProbability(claim_id=CLAIM_RESPONSE_REQUESTED_INCREMENT, probability=response),
        ClaimProbability(claim_id=CLAIM_REFERRAL_INCREMENT, probability=referral),
        ClaimProbability(claim_id=CLAIM_AMICUS_INCREMENT, probability=amicus),
    ]


def _interim_prediction(
    *,
    claims: list[ClaimProbability] | None,
    context: PredictionContext | None,
    probability: float = 0.1,
) -> Prediction:
    return Prediction(
        case_id="scotus/2",
        event_id=_INTERIM_EVENT,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 3, 1),
        input_snapshot="x",
        granted=int(probability >= 0.5),
        probability=probability,
        predicted_disposition=Disposition.granted if probability >= 0.5 else Disposition.denied,
        context=context,
        claims=claims,
    )


def test_the_interim_set_is_exactly_the_four_claims_in_stable_order() -> None:
    declared = declared_claim_set(_INTERIM_EVENT)
    assert declared is not None
    version, claim_ids = declared
    assert version == CLAIM_SET_INTERIM_V1
    assert claim_ids == (
        CLAIM_INTERIM_DISPOSITION,
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    )
    # A distinct id from the cert claim, because baseline routing keys on it and
    # the two draw on different populations.
    assert CLAIM_INTERIM_DISPOSITION != CLAIM_DISPOSITION


def test_interim_disposition_resolves_the_grant_flag() -> None:
    ctx = _interim_context()
    assert resolve_claim(CLAIM_INTERIM_DISPOSITION, ctx, _interim_outcome(granted=1)) == 1
    assert resolve_claim(CLAIM_INTERIM_DISPOSITION, ctx, _interim_outcome(granted=0)) == 0
    # `actual_granted` is required and immutable, so the mask never bites here —
    # not even on an outcome that froze no interim signals block.
    assert (
        resolve_claim(CLAIM_INTERIM_DISPOSITION, ctx, _interim_outcome(granted=1, signals=None))
        == 1
    )


def test_summary_route_assessability_never_depends_on_the_route() -> None:
    """The marker is the only source, even where the label would settle it.

    Reading 1 off a `gvr` label whose outcome carries no marker would recover a
    resolution — and would make the cases resolving 1 always assessable while
    the cases resolving 0 are assessable only where a payload was retained. The
    assessed subpopulation's rate would then sit above the baseline's, and a
    predictor could bank the gap without forecasting anything. So an unmarked
    outcome is masked whatever its label says.
    """
    ctx = _context()
    for disposition in (Disposition.gvr, Disposition.summary_reversal, Disposition.granted):
        unmarked = _cert_outcome(disposition=disposition)
        assert resolve_claim(CLAIM_SUMMARY_ROUTE, ctx, unmarked) is None
    # With the marker present, the same labels resolve.
    marked = _cert_outcome(disposition=Disposition.gvr, route="gvr")
    assert resolve_claim(CLAIM_SUMMARY_ROUTE, ctx, marked) == 1


def test_summary_route_is_vacuous_on_a_denial() -> None:
    # The grant conditioning is what carries the claim past the eight tests'
    # volume condition: a denial has no route to forecast, so it is masked
    # rather than resolved 0 into an unconditional near-boundary rate.
    ctx = _context()
    for disposition in (Disposition.denied, Disposition.dismissed):
        outcome = _cert_outcome(disposition=disposition, route=None, dissent=True)
        assert resolve_claim(CLAIM_SUMMARY_ROUTE, ctx, outcome) is None


def test_dissent_from_denial_truth_table() -> None:
    ctx = _context()
    denied = Disposition.denied
    noted = _cert_outcome(disposition=denied, dissent=True)
    quiet = _cert_outcome(disposition=denied, dissent=False)
    unread = _cert_outcome(disposition=denied, dissent=None)
    assert resolve_claim(CLAIM_DISSENT_FROM_DENIAL, ctx, noted) == 1
    assert resolve_claim(CLAIM_DISSENT_FROM_DENIAL, ctx, quiet) == 0
    # Coverage mask: no retained order text was assessed, which false must stay
    # distinguishable from.
    assert resolve_claim(CLAIM_DISSENT_FROM_DENIAL, ctx, unread) is None


def test_dissent_from_denial_is_vacuous_on_anything_but_a_denial() -> None:
    # A granted petition was never denied, and a dismissal or a withdrawal is
    # not the Court refusing review — so none of them has a denial to have
    # dissented from, even where the payload-level read set the marker. The test
    # keys on the disposition rather than on `actual_granted`, so it names the
    # same population the claim and the marker's writer do.
    ctx = _context()
    for disposition in (
        Disposition.granted,
        Disposition.gvr,
        Disposition.dismissed,
        Disposition.withdrawn,
    ):
        outcome = _cert_outcome(disposition=disposition, dissent=True)
        assert resolve_claim(CLAIM_DISSENT_FROM_DENIAL, ctx, outcome) is None, disposition


def test_the_summary_route_baseline_pools_strictly_prior_terms() -> None:
    pack = _statpack(
        _disposition_term(2025, granted=0, gvr=100, denied=900),  # own Term: excluded
        _disposition_term(2024, granted=60, gvr=40, denied=5000),
        _disposition_term(2023, granted=90, gvr=10, denied=5000),
    )
    ctx = _context(term=2025)
    # Pooled over both prior Terms: 50 cert-order dispositions over 200 grants.
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, pack, lookback_terms=0) == pytest.approx(0.25)
    # The lookback bounds the pool as a Term-year band, exactly as the other
    # pooled baselines do: only OT2024 is inside a one-Term window.
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, pack, lookback_terms=1) == pytest.approx(0.40)


def test_the_summary_route_baseline_reads_the_paid_class_only() -> None:
    """IFP rows are Tier-0-excluded, so they are never a scored cell.

    They are also GVR-heavy, so pooling them prices a population no cell belongs
    to — and on the committed pack that gap is about eleven points, several
    times the drift term the register calls dominant. The Term-level
    `base_rates` block here carries the pooled counts the real pack carries, so
    a baseline reading the wrong surface reads 0.70 instead of 0.40.
    """
    pack = _statpack(
        _disposition_term(2024, granted=60, gvr=40, denied=5000, ifp={"gvr": 60, "denied": 4000}),
    )
    ctx = _context(term=2025)
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, pack, lookback_terms=0) == pytest.approx(0.40)


def test_the_summary_route_baseline_conditions_on_the_grant_family_only() -> None:
    # Denials never enter the denominator: the resolver masks them, so a
    # baseline counting them would be conditioned differently from the claim.
    dense = _statpack(_disposition_term(2024, granted=60, gvr=40, denied=0))
    sparse = _statpack(_disposition_term(2024, granted=60, gvr=40, denied=9_000))
    ctx = _context(term=2025)
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, dense, lookback_terms=0) == pytest.approx(0.40)
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, sparse, lookback_terms=0) == pytest.approx(0.40)


def test_the_summary_route_baseline_refuses_a_thin_prior_history() -> None:
    thin = _statpack(_disposition_term(2024, granted=8, gvr=2, denied=4000))
    ctx = _context(term=2025)
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, thin, lookback_terms=0) is None
    # A prior Term thin in PAID grants does not clear the floor on the strength
    # of its IFP grants, which are not the scored population.
    ifp_heavy = _statpack(
        _disposition_term(2024, granted=8, gvr=2, denied=4000, ifp={"gvr": 200, "granted": 50})
    )
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, ifp_heavy, lookback_terms=0) is None
    # And with no prior Term at all there is nothing to pool.
    own_only = _statpack(_disposition_term(2025, granted=60, gvr=40))
    assert claim_baseline(CLAIM_SUMMARY_ROUTE, ctx, own_only, lookback_terms=0) is None


def test_the_dissent_baseline_is_none_until_a_cut_carries_it() -> None:
    # No published section counts order-list notations, so the honest baseline
    # is no baseline; the claim stays declared and banks its probabilities.
    pack = _statpack(_disposition_term(2024, granted=60, gvr=40, denied=5000))
    assert claim_baseline(CLAIM_DISSENT_FROM_DENIAL, _context(), pack, lookback_terms=0) is None


def test_cert_v2_score_claims_end_to_end() -> None:
    pack = _statpack(
        _term(2024, rate=0.06),  # the band segment the disposition baseline reads
        _disposition_term(2023, granted=60, gvr=40, denied=5000),
    )
    prediction = _prediction(
        claims=_cert_v2_claims(disposition=0.2, route=0.3, dissent=0.1),
        context=_context(term=2025),
        event_id=_CERT_MOMENT,
    )
    outcome = _cert_outcome(disposition=Disposition.denied, dissent=True)
    block = score_claims(prediction, outcome, pack, lookback_terms=0)

    assert block is not None
    assert block.declared_set_version == CLAIM_SET_CERT_V2
    by_id = {row.claim_id: row for row in block.claims}
    assert list(by_id) == [
        CLAIM_DISPOSITION,
        CLAIM_RELIST_INCREMENT,
        CLAIM_CVSG_INCREMENT,
        CLAIM_SUMMARY_ROUTE,
        CLAIM_DISSENT_FROM_DENIAL,
    ]

    # The route claim is vacuous on a denial: masked, and out of the total —
    # its baseline still computes, since a baseline is a property of the frozen
    # conditioning rather than of the outcome.
    route = by_id[CLAIM_SUMMARY_ROUTE]
    assert route.outcome is None and route.score is None
    assert route.baseline == pytest.approx(0.40)

    # The dissent claim resolved true but has no baseline yet, so it banks its
    # probability and scores nothing.
    dissent = by_id[CLAIM_DISSENT_FROM_DENIAL]
    assert dissent.outcome == 1
    assert dissent.baseline is None and dissent.score is None
    assert dissent.probability == pytest.approx(0.1)

    # Only the disposition claim scores, exactly as under cert-v1.
    assert block.total == pytest.approx(0.06**2 - 0.2**2)
    assert block.floor == 0.0


def test_a_cert_v2_moment_missing_a_new_claim_voids_the_block() -> None:
    # The set is fixed and mandatory: a cell answering only cert-v1's three
    # against a cert-v2 moment scores nothing rather than the half it chose,
    # and `validate` names the gap while the cell can still be fixed.
    pack = _statpack(_term(2024, rate=0.06))
    prediction = _prediction(claims=_claims(), context=_context(), event_id=_CERT_MOMENT)
    outcome = _cert_outcome(disposition=Disposition.denied)
    assert score_claims(prediction, outcome, pack, lookback_terms=0) is None
    problems = claim_block_problems(prediction)
    assert [p for p in problems if CLAIM_SUMMARY_ROUTE in p]
    assert [p for p in problems if CLAIM_DISSENT_FROM_DENIAL in p]


def test_the_response_requested_increment_truth_table() -> None:
    ctx = _interim_context(response_requested=False)
    unmoved = _interim_outcome(response_requested=False)
    fired = _interim_outcome(response_requested=True)
    assert resolve_claim(CLAIM_RESPONSE_REQUESTED_INCREMENT, ctx, unmoved) == 0
    assert resolve_claim(CLAIM_RESPONSE_REQUESTED_INCREMENT, ctx, fired) == 1
    # Max-latched: a request already on the docket leaves nothing to forecast,
    # so the claim is vacuous — masked, a property of the record.
    already = _interim_context(response_requested=True)
    assert resolve_claim(CLAIM_RESPONSE_REQUESTED_INCREMENT, already, fired) is None


def test_the_referral_increment_truth_table() -> None:
    ctx = _interim_context(referred_to_court=False)
    unmoved = _interim_outcome(referred_to_court=False)
    fired = _interim_outcome(referred_to_court=True)
    assert resolve_claim(CLAIM_REFERRAL_INCREMENT, ctx, unmoved) == 0
    assert resolve_claim(CLAIM_REFERRAL_INCREMENT, ctx, fired) == 1
    # A referral is never undone, so the same vacuity arm applies.
    already = _interim_context(referred_to_court=True)
    assert resolve_claim(CLAIM_REFERRAL_INCREMENT, already, fired) is None


def test_the_interim_increments_are_masked_three_ways() -> None:
    # (1) no resolution-end block, (2) prediction-time signals unobservable —
    # the null then means "nobody looked", not "the Court had not acted" — and
    # (3) the field itself undisclosed at prediction. All three are properties
    # of the record, never of the predictor.
    increments = (
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    )
    blind = _interim_context(
        signals_observable=False,
        response_requested=None,
        referred_to_court=None,
        amicus_briefs=None,
    )
    undisclosed = _interim_context(
        response_requested=None, referred_to_court=None, amicus_briefs=None
    )
    for claim_id in increments:
        no_block = resolve_claim(claim_id, _interim_context(), _interim_outcome(signals=None))
        assert no_block is None, claim_id
        assert resolve_claim(claim_id, blind, _interim_outcome()) is None, claim_id
        assert resolve_claim(claim_id, undisclosed, _interim_outcome()) is None, claim_id


def test_the_amicus_increment_is_about_the_rise_not_the_level() -> None:
    # A count, not a flag: strict comparison of both committed ends, and no
    # vacuity arm — a docket already carrying briefs can always carry another.
    ctx = _interim_context(amicus_briefs=2)
    assert resolve_claim(CLAIM_AMICUS_INCREMENT, ctx, _interim_outcome(amicus_briefs=2)) == 0
    assert resolve_claim(CLAIM_AMICUS_INCREMENT, ctx, _interim_outcome(amicus_briefs=5)) == 1


def test_the_interim_disposition_baseline_never_pools_the_cases_own_term() -> None:
    pack = _interim_pack(
        rate_terms={
            2026: (60, 60),  # the case's own application Term: must not contribute
            2025: (6, 60),
        }
    )
    ctx = _interim_context(term=2026)
    assert claim_baseline(CLAIM_INTERIM_DISPOSITION, ctx, pack, lookback_terms=0) == pytest.approx(
        0.10
    )
    # No frozen Term (a docket number neither parser reads) => unscored.
    no_term = _interim_context(term=None)
    assert claim_baseline(CLAIM_INTERIM_DISPOSITION, no_term, pack, lookback_terms=0) is None


def test_the_interim_increment_baselines_are_none_until_the_statpack_carries_the_cut() -> None:
    # The pack's escalation columns are terminal counts over the whole
    # substantive slice, not the arrival-conditioned hazard the claims need.
    pack = _interim_pack(rate_terms={2025: (6, 60)})
    ctx = _interim_context()
    for claim_id in (
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    ):
        assert claim_baseline(claim_id, ctx, pack, lookback_terms=0) is None, claim_id


def test_interim_score_claims_end_to_end_matches_the_hand_computed_rule() -> None:
    pack = _interim_pack(rate_terms={2025: (6, 60)})
    prediction = _interim_prediction(
        claims=_interim_claims(disposition=0.1, response=0.3, referral=0.2, amicus=0.4),
        context=_interim_context(amicus_briefs=1),
        probability=0.1,
    )
    outcome = _interim_outcome(granted=1, response_requested=True, amicus_briefs=3)
    block = score_claims(prediction, outcome, pack, lookback_terms=0)
    assert block is not None
    assert block.declared_set_version == CLAIM_SET_INTERIM_V1
    by_id = {row.claim_id: row for row in block.claims}
    assert list(by_id) == [
        CLAIM_INTERIM_DISPOSITION,
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    ]

    # Disposition: y=1, b=0.10, p=0.1 -> (0.10-1)^2 - (0.1-1)^2, which is 0.
    disposition = by_id[CLAIM_INTERIM_DISPOSITION]
    assert disposition.outcome == 1
    assert disposition.baseline == pytest.approx(0.10)
    assert disposition.score == pytest.approx((0.10 - 1) ** 2 - (0.1 - 1) ** 2)

    # The three increments resolve — a response was called for, no referral, the
    # amicus count rose 1 -> 3 — but carry no baseline, so none of them scores.
    assert by_id[CLAIM_RESPONSE_REQUESTED_INCREMENT].outcome == 1
    assert by_id[CLAIM_REFERRAL_INCREMENT].outcome == 0
    assert by_id[CLAIM_AMICUS_INCREMENT].outcome == 1
    for claim_id in (
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    ):
        assert by_id[claim_id].baseline is None and by_id[claim_id].score is None

    assert block.total == pytest.approx((0.10 - 1) ** 2 - (0.1 - 1) ** 2)
    assert block.floor == 0.0
    assert block.lift == pytest.approx(block.total)


def test_a_divergent_interim_disposition_claim_voids_the_block() -> None:
    # The interim disposition claim restates the interim headline probability,
    # so a divergent pair is malformed exactly as at the other two stages.
    pack = _interim_pack(rate_terms={2025: (6, 60)})
    divergent = _interim_prediction(
        claims=_interim_claims(disposition=0.6), context=_interim_context(), probability=0.1
    )
    assert score_claims(divergent, _interim_outcome(), pack, lookback_terms=0) is None
    assert claim_block_problems(divergent)
