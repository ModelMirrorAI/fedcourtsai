"""Tests for the authorship distribution claims.

`pipeline.claims` declares three claims over the bench — `majority-author` and
`separate-writers` on the merits sets, `order-writers` on the cert and interim
sets — under set versions no moment names yet. The invariants pinned here: the
new versions keep their predecessors' binary claims, no moment reaches them
until the prompt elicits the forecast, each claim resolves only from the
outcome's observed writing roles (and, for a per curiam, its decision method),
the per-label rule combines by the claim's declared kind, a malformed or
partial block scores nothing without touching the binary block, and the new
fields leave older records' bytes unchanged.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime
from typing import Any

import pytest

from fedcourtsai.pipeline import claims as claims_module
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.base_rates import PER_CURIAM_LABEL, claim_score
from fedcourtsai.pipeline.claims import (
    CLAIM_JUDGMENT_DISTURBED,
    CLAIM_MAJORITY_AUTHOR,
    CLAIM_ORDER_WRITERS,
    CLAIM_SEPARATE_WRITERS,
    CLAIM_SET_CERT_V2,
    CLAIM_SET_CERT_V3,
    CLAIM_SET_INTERIM_V1,
    CLAIM_SET_INTERIM_V2,
    CLAIM_SET_MERITS_V1,
    CLAIM_SET_MERITS_V2,
    claim_block_problems,
    declared_distribution_claims,
    distribution_problems,
    distribution_score,
    score_claims,
    score_distributions,
)
from fedcourtsai.pipeline.outcome import (
    MERITS_EVENT_ID,
    build_merits_outcome,
    known_decision_method,
)
from fedcourtsai.schemas import (
    ClaimDistribution,
    ClaimProbability,
    ClaimScoreBlock,
    Disposition,
    Engine,
    Judgment,
    JusticeVote,
    MeritsDecisionMethod,
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
    VoteValue,
)

_BENCH = (
    "Thomas",
    "Roberts",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
    "Barrett",
    "Jackson",
)
_CERT_EVENT = "evt-petition-disposition"


def _sets_by_version() -> dict[str, tuple[str, tuple[str, ...]]]:
    return dict(claims_module._SETS_BY_VERSION)


def test_the_authorship_versions_keep_their_predecessors_binary_claims() -> None:
    sets = _sets_by_version()
    for new, old in (
        (CLAIM_SET_CERT_V3, CLAIM_SET_CERT_V2),
        (CLAIM_SET_INTERIM_V2, CLAIM_SET_INTERIM_V1),
        (CLAIM_SET_MERITS_V2, CLAIM_SET_MERITS_V1),
    ):
        assert sets[new] == (new, sets[old][1])


def test_no_moment_declares_an_authorship_claim_yet() -> None:
    # The versions are declared ahead of the prompt that elicits them; a moment
    # names one only when its cells are asked for the forecast.
    for spec in moments.DECLARED_MOMENTS:
        assert declared_distribution_claims(spec.event_id) == ()
    assert declared_distribution_claims("evt-petition-writ-of-certiorari") == ()


# --- resolution -----------------------------------------------------------------


def _roles(**writing: str | None) -> list[dict[str, Any]]:
    return [{"justice": name, "writing": writing.get(name, "none")} for name in _BENCH]


def _merits_outcome(
    *,
    roles: list[dict[str, Any]] | None,
    method: MeritsDecisionMethod | None = MeritsDecisionMethod.argued_signed,
    judgment: Judgment = Judgment.reversed,
    author: str | None = None,
) -> Outcome:
    payload: dict[str, Any] = {
        "case_id": "scotus/1",
        "event_id": MERITS_EVENT_ID,
        "resolved_at": "2026-06-01",
        "actual_disposition": "other",
        "actual_granted": 1,
        "judgment": judgment.value,
        "merits_decision_method": method.value if method is not None else None,
        "merits_author": author,
    }
    if roles is not None:
        payload["writing_roles"] = roles
        payload["vote_provenance"] = {
            "source": "supremecourt-opinions",
            "documents": ["https://www.supremecourt.gov/opinions/25pdf/1_abcd.pdf"],
            "grammars": [{"grammar": "scotus-syllabus", "version": 2}],
            "participating": len(roles),
            "complete": False,
        }
    return Outcome.model_validate(payload)


def _order_outcome(roles: list[dict[str, Any]] | None) -> Outcome:
    payload: dict[str, Any] = {
        "case_id": "scotus/1",
        "event_id": _CERT_EVENT,
        "resolved_at": "2026-06-01",
        "actual_disposition": "denied",
        "actual_granted": 0,
    }
    if roles is not None:
        payload["writing_roles"] = roles
        payload["vote_provenance"] = {
            "source": "supremecourt-orders",
            "documents": ["https://www.supremecourt.gov/orders/courtorders/060126zor.pdf"],
            "grammars": [{"grammar": "scotus-order-notations", "version": 1}],
            "participating": len(roles),
            "complete": False,
        }
    return Outcome.model_validate(payload)


def test_the_majority_author_is_the_stamped_author_over_the_bench() -> None:
    resolved = claims_module._resolve_majority_author(
        _merits_outcome(roles=_roles(Kagan="majority", Thomas="dissent"), author="Kagan")
    )
    assert resolved is not None
    assert resolved["Kagan"] == 1 and resolved[PER_CURIAM_LABEL] == 0
    assert sum(resolved.values()) == 1 and set(resolved) == {*_BENCH, PER_CURIAM_LABEL}
    # An author who also wrote separately carries a mixed role; the stamp still names them.
    mixed = claims_module._resolve_majority_author(
        _merits_outcome(roles=_roles(Alito=None), author="Alito")
    )
    assert mixed is not None and mixed["Alito"] == 1
    # With no roles observed, the author alone is a label; the rest resolve 0 by omission.
    bare = claims_module._resolve_majority_author(_merits_outcome(roles=None, author="Kagan"))
    assert bare == {"Kagan": 1, PER_CURIAM_LABEL: 0}


def test_a_per_curiam_resolves_from_the_stamp_under_a_per_curiam_method() -> None:
    outcome = _merits_outcome(
        roles=None, method=MeritsDecisionMethod.argued_per_curiam, author=PER_CURIAM_LABEL
    )
    assert claims_module._resolve_majority_author(outcome) == {PER_CURIAM_LABEL: 1}


@pytest.mark.parametrize(
    "outcome",
    [
        # No stamped author: masked whoever wrote, so the mask never reads the answer.
        _merits_outcome(roles=_roles(Kagan="majority")),
        _merits_outcome(roles=None, method=MeritsDecisionMethod.argued_per_curiam),
        # No deciding opinion: nobody to author it, per curiam or not.
        _merits_outcome(roles=None, method=MeritsDecisionMethod.dig, author=PER_CURIAM_LABEL),
        _merits_outcome(roles=None, method=MeritsDecisionMethod.summary_order, author="Kagan"),
        # An unclassified method masks every author alike.
        _merits_outcome(roles=None, method=None, author="Kagan"),
        _merits_outcome(roles=None, method=None, author=PER_CURIAM_LABEL),
        # A summary opinion is outside the argued population the baseline pools.
        _merits_outcome(
            roles=None, method=MeritsDecisionMethod.summary_opinion, author=PER_CURIAM_LABEL
        ),
        # The stamp and the method disagree.
        _merits_outcome(roles=None, author=PER_CURIAM_LABEL),
        _merits_outcome(roles=None, method=MeritsDecisionMethod.argued_per_curiam, author="Kagan"),
        # The roles contradict the stamp: off the bench, a dissent, another lead.
        _merits_outcome(roles=_roles(), author="Breyer"),
        _merits_outcome(roles=_roles(Kagan="dissent"), author="Kagan"),
        _merits_outcome(roles=_roles(Thomas="majority"), author="Kagan"),
    ],
)
def test_the_majority_author_is_masked_where_the_record_names_none(outcome: Outcome) -> None:
    assert claims_module._resolve_majority_author(outcome) is None


def test_separate_writers_counts_every_writing_but_the_lead_and_silence() -> None:
    resolved = claims_module._resolve_separate_writers(
        _merits_outcome(
            roles=_roles(
                Kagan="majority", Thomas="dissent", Gorsuch="concurrence-in-judgment", Barrett=None
            )
        )
    )
    assert resolved == {name: int(name in {"Thomas", "Gorsuch", "Barrett"}) for name in _BENCH}
    assert claims_module._resolve_separate_writers(_merits_outcome(roles=None)) is None


def test_order_writers_resolve_off_the_orders_source_only() -> None:
    resolved = claims_module._resolve_order_writers(
        _order_outcome(_roles(Sotomayor="dissent", Alito="statement"))
    )
    assert resolved == {name: int(name in {"Sotomayor", "Alito"}) for name in _BENCH}
    assert claims_module._resolve_order_writers(_order_outcome(None)) is None
    assert (
        claims_module._resolve_order_writers(_merits_outcome(roles=_roles(Kagan="majority")))
        is None
    )


# --- the rule, per label ----------------------------------------------------------


def test_a_categorical_claim_adds_its_label_terms() -> None:
    forecast = {"Kagan": 0.5, "Alito": 0.3, PER_CURIAM_LABEL: 0.2}
    baseline = {"Kagan": 0.4, "Alito": 0.4, PER_CURIAM_LABEL: 0.2}
    outcome = {"Kagan": 1, "Alito": 0, PER_CURIAM_LABEL: 0}
    expected = sum(
        claim_score(forecast[label], outcome[label], baseline[label]) for label in forecast
    )
    assert distribution_score(forecast, outcome, baseline, kind="categorical") == pytest.approx(
        expected
    )
    # Restating the baseline scores exactly zero, the floor.
    assert distribution_score(baseline, outcome, baseline, kind="categorical") == 0.0


def test_categorical_mass_on_a_label_the_outcome_lacks_is_a_miss() -> None:
    # Mass on a Justice who did not sit counts against the forecast, as mass on
    # a sitting non-author would; it is never dropped and renormalized away.
    baseline = {"Kagan": 0.5, "Alito": 0.5}
    outcome = {"Kagan": 1, "Alito": 0}
    off_bench = distribution_score(
        {"Kagan": 0.8, "Breyer": 0.2}, outcome, baseline, kind="categorical"
    )
    on_bench = distribution_score(
        {"Kagan": 0.8, "Alito": 0.2}, outcome, baseline, kind="categorical"
    )
    renormalized = distribution_score({"Kagan": 1.0}, outcome, baseline, kind="categorical")
    assert off_bench == pytest.approx(on_bench)
    assert off_bench is not None and renormalized is not None and off_bench < renormalized


def test_a_per_justice_claim_averages_so_the_bench_weighs_as_one_claim() -> None:
    outcome = {"Thomas": 1, "Kagan": 0}
    forecast = {"Thomas": 0.6, "Kagan": 0.1, "Breyer": 0.9}  # an extra label is ignored
    baseline = {"Thomas": 0.3, "Kagan": 0.2}
    expected = (claim_score(0.6, 1, 0.3) + claim_score(0.1, 0, 0.2)) / 2
    assert distribution_score(forecast, outcome, baseline, kind="per-justice") == pytest.approx(
        expected
    )
    # A Justice the outcome resolves and the forecast skips: a partial answer.
    assert distribution_score({"Thomas": 0.6}, outcome, baseline, kind="per-justice") is None
    assert distribution_score(forecast, outcome, {"Thomas": 0.3}, kind="per-justice") is None


def test_distribution_problems_name_a_malformed_forecast() -> None:
    assert distribution_problems(CLAIM_MAJORITY_AUTHOR, {"Kagan": 0.7, PER_CURIAM_LABEL: 0.3}) == []
    assert distribution_problems(CLAIM_MAJORITY_AUTHOR, {"Kagan": 0.7})  # sums to 0.7
    assert distribution_problems(CLAIM_MAJORITY_AUTHOR, {"Holmes": 1.0})  # off the roster
    # Per-Justice probabilities do not sum, and per curiam is no Justice.
    assert distribution_problems(CLAIM_SEPARATE_WRITERS, {"Kagan": 0.7, "Thomas": 0.7}) == []
    assert distribution_problems(CLAIM_SEPARATE_WRITERS, {PER_CURIAM_LABEL: 0.1})
    # Ten labels rounded to three decimals are one distribution.
    rounded = dict.fromkeys(_BENCH, 0.111) | {PER_CURIAM_LABEL: 0.0}
    assert distribution_problems(CLAIM_MAJORITY_AUTHOR, rounded) == []
    # A per-Justice forecast leaving out a sitting Justice would score nothing.
    partial = dict.fromkeys(_BENCH[1:], 0.2)
    assert distribution_problems(CLAIM_SEPARATE_WRITERS, partial, _BENCH) == [
        f"distribution claim {CLAIM_SEPARATE_WRITERS!r} states nothing for {_BENCH[0]!r}, "
        "who sits on the cell's snapshot date — a per-Justice forecast covers the bench"
    ]


# --- the block --------------------------------------------------------------------


@pytest.fixture
def merits_v2(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the merits grant moment at merits-v2, as the prompt switch-on will."""
    spec = moments.spec_for(MERITS_EVENT_ID)
    assert spec is not None
    switched = dataclasses.replace(spec, claim_set_version=CLAIM_SET_MERITS_V2)
    real = moments.spec_for
    monkeypatch.setattr(
        moments,
        "spec_for",
        lambda event_id: switched if event_id == MERITS_EVENT_ID else real(event_id),
    )


def _even(labels: tuple[str, ...]) -> dict[str, float]:
    return {label: 1 / len(labels) for label in labels}


def _merits_prediction(distributions: list[ClaimDistribution] | None) -> Prediction:
    return Prediction(
        case_id="scotus/1",
        event_id=MERITS_EVENT_ID,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 3, 1),
        input_snapshot="x",
        granted=1,
        probability=0.7,
        predicted_disposition=Disposition.other,
        judgment=Judgment.reversed,
        votes=[JusticeVote(justice="Kagan", vote=VoteValue.majority)],
        context=PredictionContext(
            mode="forward", snapshot_date=date(2026, 3, 1), signals_observable=True, term=2025
        ),
        claims=[ClaimProbability(claim_id=CLAIM_JUDGMENT_DISTURBED, probability=0.7)],
        claim_distributions=distributions,
    )


def _authorship(author: dict[str, float], separate: dict[str, float]) -> list[ClaimDistribution]:
    return [
        ClaimDistribution(claim_id=CLAIM_MAJORITY_AUTHOR, probabilities=author),
        ClaimDistribution(claim_id=CLAIM_SEPARATE_WRITERS, probabilities=separate),
    ]


@pytest.mark.usefixtures("merits_v2")
def test_merits_v2_scores_both_claims_against_an_injected_baseline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    author_baseline = _even((*_BENCH, PER_CURIAM_LABEL))
    separate_baseline = dict.fromkeys(_BENCH, 0.2)
    monkeypatch.setattr(
        claims_module,
        "_distribution_baseline",
        lambda claim_id, *_a, **_k: (
            author_baseline if claim_id == CLAIM_MAJORITY_AUTHOR else separate_baseline
        ),
    )
    author = {"Kagan": 0.6} | {name: 0.4 / 9 for name in _BENCH if name != "Kagan"}
    author[PER_CURIAM_LABEL] = 0.4 / 9
    separate = dict.fromkeys(_BENCH, 0.1) | {"Thomas": 0.7}
    outcome = _merits_outcome(roles=_roles(Kagan="majority", Thomas="dissent"), author="Kagan")
    rows = score_distributions(
        _merits_prediction(_authorship(author, separate)),
        outcome,
        StatPack(corpus_rows=1),
        lookback_terms=3,
    )
    assert [row.claim_id for row in rows] == [CLAIM_MAJORITY_AUTHOR, CLAIM_SEPARATE_WRITERS]
    assert all(row.scored for row in rows)
    resolved_author = claims_module._resolve_majority_author(outcome)
    resolved_separate = claims_module._resolve_separate_writers(outcome)
    assert resolved_author is not None and resolved_separate is not None
    assert rows[0].score == pytest.approx(
        distribution_score(author, resolved_author, author_baseline, kind="categorical")
    )
    assert rows[1].score == pytest.approx(
        distribution_score(separate, resolved_separate, separate_baseline, kind="per-justice")
    )


@pytest.mark.usefixtures("merits_v2")
def test_without_a_baseline_the_rows_bank_the_forecast_unscored() -> None:
    outcome = _merits_outcome(roles=_roles(Kagan="majority"), author="Kagan")
    block = score_claims(
        _merits_prediction(
            _authorship(_even((*_BENCH, PER_CURIAM_LABEL)), dict.fromkeys(_BENCH, 0.2))
        ),
        outcome,
        StatPack(corpus_rows=1),
        lookback_terms=3,
    )
    assert block is not None
    assert [row.claim_id for row in block.distributions] == [
        CLAIM_MAJORITY_AUTHOR,
        CLAIM_SEPARATE_WRITERS,
    ]
    assert all(row.score is None and row.outcome is not None for row in block.distributions)


@pytest.mark.usefixtures("merits_v2")
@pytest.mark.parametrize(
    "distributions",
    [
        # One declared claim left out.
        [ClaimDistribution(claim_id=CLAIM_MAJORITY_AUTHOR, probabilities={"Kagan": 1.0})],
        # One stated twice.
        [
            *_authorship({"Kagan": 1.0}, {"Kagan": 0.1}),
            ClaimDistribution(claim_id=CLAIM_MAJORITY_AUTHOR, probabilities={"Alito": 1.0}),
        ],
        # A categorical forecast that is not one distribution.
        _authorship({"Kagan": 0.5}, {"Kagan": 0.1}),
    ],
)
def test_a_malformed_block_scores_nothing_and_leaves_the_binary_block(
    distributions: list[ClaimDistribution],
) -> None:
    prediction = _merits_prediction(distributions)
    block = score_claims(
        prediction,
        _merits_outcome(roles=_roles(Kagan="majority")),
        StatPack(corpus_rows=1),
        lookback_terms=3,
    )
    assert block is not None and block.distributions == []
    assert [row.claim_id for row in block.claims] == [CLAIM_JUDGMENT_DISTURBED]
    assert claim_block_problems(prediction)


@pytest.mark.usefixtures("merits_v2")
def test_a_well_formed_block_reports_no_problem_and_an_absent_one_none() -> None:
    assert (
        claim_block_problems(
            _merits_prediction(_authorship({"Kagan": 1.0}, dict.fromkeys(_BENCH, 0.2)))
        )
        == []
    )
    assert claim_block_problems(_merits_prediction(None)) == []
    # A well-formed block stated without the claims block rides nothing.
    orphan = _merits_prediction(_authorship({"Kagan": 1.0}, dict.fromkeys(_BENCH, 0.2)))
    orphan = orphan.model_copy(update={"claims": None})
    assert claim_block_problems(orphan) == [
        "distribution claims are stated without the claims block — they are "
        "reported beside it, so they go unscored without it"
    ]
    assert (
        score_distributions(
            _merits_prediction(None),
            _merits_outcome(roles=_roles(Kagan="majority"), author="Kagan"),
            StatPack(corpus_rows=1),
            lookback_terms=3,
        )
        == []
    )


def test_order_writers_are_resolved_and_never_scored(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = moments.spec_for(_CERT_EVENT)
    assert spec is not None
    switched = dataclasses.replace(spec, claim_set_version=CLAIM_SET_CERT_V3)
    monkeypatch.setattr(moments, "spec_for", lambda event_id: switched)
    monkeypatch.setattr(
        claims_module, "_distribution_baseline", lambda *_a, **_k: dict.fromkeys(_BENCH, 0.01)
    )
    prediction = Prediction(
        case_id="scotus/1",
        event_id=_CERT_EVENT,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 3, 1),
        input_snapshot="x",
        granted=0,
        probability=0.1,
        predicted_disposition=Disposition.denied,
        context=PredictionContext(
            mode="forward", snapshot_date=date(2026, 3, 1), signals_observable=True, term=2025
        ),
        claim_distributions=[
            ClaimDistribution(
                claim_id=CLAIM_ORDER_WRITERS, probabilities=dict.fromkeys(_BENCH, 0.02)
            )
        ],
    )
    rows = score_distributions(
        prediction,
        _order_outcome(_roles(Sotomayor="dissent")),
        StatPack(corpus_rows=1),
        lookback_terms=3,
    )
    assert len(rows) == 1
    assert rows[0].scored is False and rows[0].score is None and rows[0].baseline is None
    assert rows[0].outcome == {name: int(name == "Sotomayor") for name in _BENCH}


# --- the records -----------------------------------------------------------------


def test_the_new_fields_leave_older_records_bytes_unchanged() -> None:
    prediction = _merits_prediction(None)
    assert "claim_distributions" not in prediction.model_dump(mode="json")
    assert "claim_distributions" in _merits_prediction(
        _authorship({"Kagan": 1.0}, {"Kagan": 0.1})
    ).model_dump(mode="json")
    outcome = _merits_outcome(roles=None, method=None)
    assert "merits_decision_method" not in outcome.model_dump(mode="json")
    assert "merits_author" not in outcome.model_dump(mode="json")
    stamped = _merits_outcome(roles=None, author="Kagan").model_dump(mode="json")
    assert stamped["merits_author"] == "Kagan"
    block = ClaimScoreBlock(declared_set_version=CLAIM_SET_MERITS_V1)
    assert "distributions" not in block.model_dump(mode="json")


def test_the_merits_writer_stamps_the_decision_method() -> None:
    outcome = build_merits_outcome(
        "scotus/1",
        MERITS_EVENT_ID,
        Judgment.affirmed,
        date(2026, 6, 1),
        distribution_count=None,
        cvsg_date=None,
        source=None,
        decision_method=known_decision_method("argued-per-curiam"),
    )
    assert outcome.merits_decision_method == MeritsDecisionMethod.argued_per_curiam
    assert known_decision_method(None) is None
    assert known_decision_method("not-a-method") is None


@pytest.mark.parametrize(
    ("field", "value"), [("merits_decision_method", "argued-signed"), ("merits_author", "Kagan")]
)
def test_a_merits_fact_off_the_merits_stage_does_not_validate(field: str, value: str) -> None:
    with pytest.raises(ValueError, match=f"`{field}` is set off the merits stage"):
        Outcome.model_validate(
            {
                "case_id": "scotus/1",
                "event_id": _CERT_EVENT,
                "resolved_at": "2026-06-01",
                "actual_disposition": "denied",
                "actual_granted": 0,
                field: value,
            }
        )


def test_separate_writers_mask_a_signed_decision_with_no_single_lead() -> None:
    # The author's null role may be the lead opinion written in part.
    outcome = _merits_outcome(roles=_roles(Kagan=None, Thomas="dissent"))
    assert claims_module._resolve_separate_writers(outcome) is None
    dig = _merits_outcome(roles=_roles(Thomas="dissent"), method=MeritsDecisionMethod.dig)
    resolved = claims_module._resolve_separate_writers(dig)
    assert resolved is not None and resolved["Thomas"] == 1
