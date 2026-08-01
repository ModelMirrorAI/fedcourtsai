"""Reading the interim docket — what an application asks, and how it ends.

Every fixture here is verbatim from supremecourt.gov, because the two readers
exist to survive real docket prose and every bug found while building them came
from text that looked like something it was not.
"""

from __future__ import annotations

from fedcourtsai.pipeline.interim_signals import (
    ApplicationKind,
    ReferralPosture,
    application_kind,
    is_predictable_application,
    match_interim_disposition,
    referral_posture,
)
from fedcourtsai.schemas import Disposition

# 24A1 — the administrative majority, verbatim.
_EXTENSION = [
    "Application (24A1) to extend the time to file a petition for a writ of "
    "certiorari from July 15, 2024 to September 13, 2024, submitted to Justice Alito.",
    "Application (24A1) granted by Justice Alito extending the time to file until August 15, 2024.",
]
# 24A1099 — a stay, referred to the full Court and denied.
_STAY_REFERRED = [
    "Application (24A1099) for a stay, submitted to The Chief Justice.",
    "Application (24A1099) referred to the Court.",
    "Application (24A1099) for stay presented to The Chief Justice and by him "
    "referred to the Court is denied.",
]
# 24A650 — a stay a single Justice denied without referring it.
_STAY_CIRCUIT = [
    "Application (24A650) for a stay, submitted to Justice Kagan.",
    "Application (24A650) denied by Justice Kagan.",
]


def test_an_extension_is_read_from_its_own_ask_not_the_writ_it_names() -> None:
    """The bug this exists to prevent: an extension's ask says "a petition for a
    writ of certiorari" — the thing whose deadline moves — and a relief-shaped
    pattern run over the joined proceedings reads that as a request for a writ.
    All 26 sampled applications classified substantive that way."""
    assert application_kind(_EXTENSION) is ApplicationKind.extension


def test_a_stay_is_substantive_whichever_bench_took_it() -> None:
    assert application_kind(_STAY_REFERRED) is ApplicationKind.substantive
    assert application_kind(_STAY_CIRCUIT) is ApplicationKind.substantive


def test_an_unreadable_ask_is_not_guessed_at() -> None:
    """A parser gap is a coverage question, not a classification. Folding it into
    either bucket would silently move the size of the predicted population."""
    assert application_kind(["Letter of applicant filed."]) is ApplicationKind.unknown
    assert application_kind([]) is ApplicationKind.unknown


def test_only_substantive_applications_are_predicted() -> None:
    """An extension is ~always granted by one Justice and no fact about the case
    moves it. A population that is 85% extensions would give a predictor a base
    rate it beats by answering "granted" every time."""
    assert is_predictable_application(ApplicationKind.substantive)
    assert not is_predictable_application(ApplicationKind.extension)
    assert not is_predictable_application(ApplicationKind.unknown)


def test_the_referral_posture_is_observable() -> None:
    """The interim aggregation rule turns on this: a Circuit Justice may act
    alone, or refer to the full Court, which decides by majority. The referral is
    an ordinary docket entry, which is what makes the stage modelable."""
    assert referral_posture(_STAY_REFERRED) is ReferralPosture.referred_to_court
    assert referral_posture(_STAY_CIRCUIT) is ReferralPosture.circuit_justice
    # Acting alone leaves no entry, so absence is the right reading — the Court
    # records the exception, not the rule.
    assert referral_posture([]) is ReferralPosture.circuit_justice


def test_a_denial_is_read_before_a_grant_in_the_full_court_form() -> None:
    """ "presented to The Chief Justice and by him referred to the Court is denied"
    states the referral and the outcome in one sentence, so a grant-first scan
    would stop on the referral clause."""
    hit = match_interim_disposition(_STAY_REFERRED[-1])
    assert hit is not None and hit[0] == Disposition.denied


def test_a_single_justice_disposition_reads() -> None:
    hit = match_interim_disposition(_STAY_CIRCUIT[-1])
    assert hit is not None and hit[0] == Disposition.denied


def test_a_consolidated_order_disposes_of_every_application_it_names() -> None:
    """Verbatim from 23A350 (Ohio v. EPA). One order decides four applications, so
    the plural is the shape a consolidated interim matter always takes — a
    singular-only pattern reads it as undecided."""
    hit = match_interim_disposition(
        "Applications for stays (23A349, 23A350, 23A351, and 23A384) granted by the Court."
    )
    assert hit is not None and hit[0] == Disposition.granted


def test_a_deferred_application_has_not_been_decided() -> None:
    """Also verbatim from 23A350: the Court deferred it pending oral argument and
    granted it six months later. Reading "deferred" as a disposition would record
    an outcome the Court had not reached."""
    assert (
        match_interim_disposition(
            "Consideration of the applications for stay (23A349, 23A350, 23A351, and "
            "23A384) presented to The Chief Justice and by him referred to the Court "
            "is deferred pending oral argument."
        )
        is None
    )


def test_an_ordinary_entry_disposes_of_nothing() -> None:
    for text in (
        "Response to application from respondent Jeremiah Sweeney filed.",
        "Brief amicus curiae of Energy Infrastructure Council filed.",
        "SET FOR ARGUMENT on Wednesday, February 21, 2024. VIDED.",
    ):
        assert match_interim_disposition(text) is None, text
