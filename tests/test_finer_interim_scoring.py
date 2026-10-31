"""The finer interim reading's scoring, keyed on the scored prediction's label.

What the registration owes and these pin:

- **A cell stamped before `FINER_INTERIM_READING_FROM` scores exactly as
  before** — Brier, `correct`, the claim block and the pool all read the
  registered fields — whatever the outcome's finer reading says.
- **From that label on, an interim cell scores on `interim_granted`**: a partial
  grant is a grant, a moot dismissal (or an outcome with no finer reading)
  leaves the scored set, and `correct` follows the binary.
- **The finer pool** pools `finer_granted` / `finer_resolved`, applies the floor
  to that denominator, and refuses while any pooled Term is unread or predates
  the finer counts.
- **The outcome and the statpack** carry the finer reading beside the
  registered one, never in its place.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pytest

from fedcourtsai import corpus
from fedcourtsai.analytics import _InterimAcc
from fedcourtsai.pipeline.base_rates import interim_base_rate
from fedcourtsai.pipeline.claims import CLAIM_INTERIM_DISPOSITION, score_claims
from fedcourtsai.pipeline.evaluate import (
    brier_score,
    is_correct,
    scored_granted,
    stage_brier_score,
    stage_correct,
)
from fedcourtsai.pipeline.outcome import _build_outcome
from fedcourtsai.process_version import (
    FINER_INTERIM_READING_FROM,
    scores_finer_interim_reading,
)
from fedcourtsai.schemas import (
    ClaimProbability,
    Disposition,
    Engine,
    InterimResolutionSignals,
    Outcome,
    Prediction,
    PredictionContext,
    ProcessVersion,
    StatPack,
    StatPackInterim,
    StatPackInterimTerm,
)

_EVENT = "evt-motion-disposition"


def _prediction(
    label: str | None,
    *,
    probability: float = 0.3,
    disposition: Disposition = Disposition.denied,
    claims: list[ClaimProbability] | None = None,
) -> Prediction:
    return Prediction(
        case_id="scotus/2",
        event_id=_EVENT,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 11, 10),
        input_snapshot="x",
        granted=int(probability >= 0.5),
        probability=probability,
        predicted_disposition=disposition,
        context=PredictionContext(
            mode="forward",
            snapshot_date=date(2026, 11, 10),
            signals_observable=True,
            response_requested=False,
            referred_to_court=False,
            amicus_briefs=0,
            term=2026,
        ),
        claims=claims,
        process_version=(
            None
            if label is None
            else ProcessVersion(
                label=label,
                digest="sha256:" + "0" * 64,
                stamped_at=datetime(2026, 11, 10, tzinfo=UTC),
            )
        ),
    )


def _outcome(registered: Disposition, finer: str | None) -> Outcome:
    granted = {"granted": 1, "granted-in-part": 1, "dismissed-moot": None}.get(finer or "", 0)
    return Outcome(
        case_id="scotus/2",
        event_id=_EVENT,
        resolved_at=date(2026, 12, 1),
        actual_disposition=registered,
        actual_granted=int(registered is Disposition.granted),
        interim_signals=InterimResolutionSignals(
            response_requested=False, referred_to_court=False, amicus_briefs=0
        ),
        interim_reading=finer,
        interim_granted=None if finer is None else granted,
    )


def test_the_label_threshold() -> None:
    assert FINER_INTERIM_READING_FROM == "proc-v17"
    assert not scores_finer_interim_reading("proc-v16")
    assert scores_finer_interim_reading("proc-v17")
    assert scores_finer_interim_reading("proc-v100")
    assert not scores_finer_interim_reading(None)
    assert not scores_finer_interim_reading("proc-v17-draft")


@pytest.mark.parametrize("finer", ["granted-in-part", "dismissed-moot", None])
def test_an_earlier_label_scores_on_the_registered_reading(finer: str | None) -> None:
    prediction = _prediction("proc-v16")
    outcome = _outcome(Disposition.denied, finer)
    assert scored_granted(prediction, outcome, interim=True) == 0
    assert stage_brier_score(prediction, outcome, interim=True) == brier_score(prediction, outcome)
    assert stage_correct(prediction, outcome, interim=True) == is_correct(prediction, outcome)


def test_a_finer_label_scores_a_partial_grant_as_a_grant() -> None:
    prediction = _prediction(
        FINER_INTERIM_READING_FROM, probability=0.7, disposition=Disposition.granted
    )
    outcome = _outcome(Disposition.denied, "granted-in-part")
    assert scored_granted(prediction, outcome, interim=True) == 1
    assert stage_brier_score(prediction, outcome, interim=True) == pytest.approx(0.09)
    # `correct` follows the binary: a predicted plain grant against a partial one.
    assert stage_correct(prediction, outcome, interim=True) == 1
    assert is_correct(prediction, outcome) == 0


@pytest.mark.parametrize("finer", ["dismissed-moot", None])
def test_a_finer_label_leaves_a_moot_or_unread_outcome_unscored(finer: str | None) -> None:
    prediction = _prediction(FINER_INTERIM_READING_FROM)
    outcome = _outcome(Disposition.granted, finer)
    assert scored_granted(prediction, outcome, interim=True) is None
    assert stage_brier_score(prediction, outcome, interim=True) is None
    assert stage_correct(prediction, outcome, interim=True) is None


def test_off_the_interim_stage_the_label_changes_nothing() -> None:
    prediction = _prediction(FINER_INTERIM_READING_FROM)
    outcome = _outcome(Disposition.granted, "dismissed-moot")
    assert scored_granted(prediction, outcome, interim=False) == 1
    assert stage_correct(prediction, outcome, interim=False) == is_correct(prediction, outcome)


def test_the_outcome_refuses_a_binary_that_disagrees_with_its_reading() -> None:
    with pytest.raises(ValueError, match="interim_granted"):
        Outcome(
            case_id="scotus/2",
            event_id=_EVENT,
            resolved_at=date(2026, 12, 1),
            actual_disposition=Disposition.denied,
            actual_granted=0,
            interim_reading="granted-in-part",
            interim_granted=0,
        )


def test_an_outcome_without_the_finer_reading_serializes_as_before() -> None:
    outcome = _outcome(Disposition.denied, None)
    payload = json.loads(outcome.model_dump_json())
    assert "interim_reading" not in payload
    assert "interim_granted" not in payload
    moot = json.loads(_outcome(Disposition.denied, "dismissed-moot").model_dump_json())
    assert moot["interim_reading"] == "dismissed-moot"
    assert "interim_granted" not in moot


def _row(*, interim_reading: str | None) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id="scotus/2",
        court="scotus",
        docket_number="26A2",
        case_name="In re Application",
        disposition="denied",
        date_decided=date(2026, 12, 1),
        application_kind="substantive",
        response_requested=False,
        referred_to_court=False,
        amicus_briefs=0,
        interim_reading=interim_reading,
    )


def test_the_outcome_builder_copies_the_column_on_an_interim_recording_only() -> None:
    interim = _build_outcome(
        _row(interim_reading="granted-in-part"), _EVENT, "standard", interim=True
    )
    assert (interim.actual_disposition, interim.actual_granted) == (Disposition.denied, 0)
    assert (interim.interim_reading, interim.interim_granted) == ("granted-in-part", 1)
    cert = _build_outcome(_row(interim_reading="granted-in-part"), _EVENT, "standard")
    assert (cert.interim_reading, cert.interim_granted) == (None, None)
    unknown = _build_outcome(_row(interim_reading="vacated"), _EVENT, "standard", interim=True)
    assert (unknown.interim_reading, unknown.interim_granted) == (None, None)


def _pack(terms: dict[int, tuple[int, int, int | None, int | None, int]]) -> StatPack:
    """``term -> (granted, resolved, finer_granted, finer_resolved, finer_unread)``."""
    entries = [
        StatPackInterimTerm(
            term=year,
            substantive_resolved=resolved,
            substantive_granted=granted,
            finer_granted=fg,
            finer_resolved=fr,
            finer_moot=None if fr is None else 0,
            finer_unread=None if fr is None else unread,
        )
        for year, (granted, resolved, fg, fr, unread) in sorted(terms.items(), reverse=True)
    ]
    return StatPack(corpus_rows=1, interim=StatPackInterim(terms=entries))


def test_the_finer_pool_reads_the_finer_counts() -> None:
    pack = _pack({2024: (10, 100, 12, 95, 0), 2025: (5, 50, 6, 48, 0)})
    assert interim_base_rate(2026, pack) == pytest.approx(15 / 150)
    assert interim_base_rate(2026, pack, reading="finer") == pytest.approx(18 / 143)


def test_the_finer_floor_reads_the_finer_denominator() -> None:
    pack = _pack({2025: (5, 50, 5, 49, 0)})
    assert interim_base_rate(2026, pack) == pytest.approx(0.1)
    assert interim_base_rate(2026, pack, reading="finer") is None


@pytest.mark.parametrize(
    "older", [(10, 100, None, None, 0), (10, 100, 10, 99, 1)], ids=["predates", "unread"]
)
def test_the_finer_pool_refuses_a_term_it_does_not_cover(
    older: tuple[int, int, int | None, int | None, int],
) -> None:
    pack = _pack({2024: older, 2025: (5, 50, 6, 48, 0)})
    assert interim_base_rate(2026, pack) == pytest.approx(15 / 150)
    assert interim_base_rate(2026, pack, reading="finer") is None
    # Outside the window it is not pooled, so it does not refuse.
    wide = _pack({2024: older, 2025: (5, 60, 6, 58, 0)})
    assert interim_base_rate(2026, wide, reading="finer") is None
    assert interim_base_rate(2026, wide, lookback_terms=1, reading="finer") == pytest.approx(6 / 58)


def _claims(p: float) -> list[ClaimProbability]:
    return [
        ClaimProbability(claim_id=CLAIM_INTERIM_DISPOSITION, probability=p),
        ClaimProbability(claim_id="response-requested-increment", probability=0.3),
        ClaimProbability(claim_id="referral-increment", probability=0.2),
        ClaimProbability(claim_id="amicus-increment", probability=0.4),
    ]


def _disposition_row(
    prediction: Prediction, outcome: Outcome, pack: StatPack
) -> tuple[object, ...]:
    block = score_claims(prediction, outcome, pack, lookback_terms=10)
    assert block is not None
    row = next(c for c in block.claims if c.claim_id == CLAIM_INTERIM_DISPOSITION)
    return row.outcome, row.mask_reason, row.baseline


def test_the_claim_block_follows_the_label() -> None:
    pack = _pack({2024: (10, 100, 12, 95, 0)})
    partial = _outcome(Disposition.denied, "granted-in-part")
    moot = _outcome(Disposition.granted, "dismissed-moot")
    unread = _outcome(Disposition.granted, None)
    earlier = _prediction("proc-v16", claims=_claims(0.3))
    finer = _prediction(FINER_INTERIM_READING_FROM, claims=_claims(0.3))
    assert _disposition_row(earlier, partial, pack) == (0, None, pytest.approx(0.1))
    assert _disposition_row(earlier, moot, pack) == (1, None, pytest.approx(0.1))
    assert _disposition_row(finer, partial, pack) == (1, None, pytest.approx(12 / 95))
    assert _disposition_row(finer, moot, pack) == (None, "dismissed-moot", pytest.approx(12 / 95))
    assert _disposition_row(finer, unread, pack) == (
        None,
        "finer-reading-absent",
        pytest.approx(12 / 95),
    )


def test_the_statpack_counts_the_finer_reading_beside_the_registered_one() -> None:
    acc = _InterimAcc()
    for disposition, reading in (
        ("denied", "granted-in-part"),
        ("granted", "dismissed-moot"),
        ("denied", "denied"),
        ("granted", "granted"),
        ("denied", None),
    ):
        acc.add(
            corpus.CorpusRow(
                case_id=f"scotus/{len(reading or '')}{disposition}",
                court="scotus",
                docket_number="25A1",
                case_name="x",
                disposition=disposition,
                application_kind="substantive",
                interim_reading=reading,
            )
        )
    assert (acc.substantive_resolved, acc.substantive_granted) == (5, 2)
    assert (acc.finer_resolved, acc.finer_granted, acc.finer_moot, acc.finer_unread) == (3, 2, 1, 1)
