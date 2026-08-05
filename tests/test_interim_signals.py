"""Reading the interim docket — what an application asks, and how it ends.

Every fixture here is verbatim from supremecourt.gov, because the two readers
exist to survive real docket prose and every bug found while building them came
from text that looked like something it was not.
"""

from __future__ import annotations

from fedcourtsai.pipeline.ingest import map_live_docket
from fedcourtsai.pipeline.interim_signals import (
    ApplicationKind,
    ReferralPosture,
    amicus_briefs,
    application_kind,
    escalation_signals,
    is_predictable_application,
    match_interim_disposition,
    referral_posture,
    response_requested,
)
from fedcourtsai.pipeline.live import STREAMS
from fedcourtsai.schemas import Disposition
from fedcourtsai.supremecourt import live_application_id, live_docket_id

# 24A1 — the administrative majority, verbatim.
_EXTENSION = [
    "Application (24A1) to extend the time to file a petition for a writ of "
    + "certiorari from July 15, 2024 to September 13, 2024, submitted to Justice Alito.",
    "Application (24A1) granted by Justice Alito extending the time to file until August 15, 2024.",
]
# 24A1099 — a stay, referred to the full Court and denied.
_STAY_REFERRED = [
    "Application (24A1099) for a stay, submitted to The Chief Justice.",
    "Application (24A1099) referred to the Court.",
    "Application (24A1099) for stay presented to The Chief Justice and by him "
    + "referred to the Court is denied.",
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


def test_the_court_requesting_a_response_is_not_a_response_arriving() -> None:
    """The discriminator on the interim docket, and the two are easy to conflate:
    a respondent may answer uninvited, but only the Court asks. That makes a
    request the analogue of a CVSG — an act of attention — rather than of a
    relist."""
    assert response_requested(
        ["Response to application (23A350) requested by The Chief Justice, due by 4 p.m."]
    )
    assert not response_requested(
        ["Response to application from respondent Jeremiah Sweeney filed."]
    )


def test_amicus_interest_is_counted_not_flagged() -> None:
    """One brief is a different signal from a dozen. Counted per entry, so an
    entry naming several filers counts once — an undercount, which is the
    direction that cannot manufacture salience."""
    assert amicus_briefs(["Brief amicus curiae of Energy Infrastructure Council filed."]) == 1
    assert amicus_briefs(["Reply of applicant filed."]) == 0
    assert (
        amicus_briefs(["Brief amicus curiae of A filed.", "Brief amicus curiae of B filed."]) == 2
    )


def test_the_escalation_ladder_separates_the_sampled_outcomes() -> None:
    """The three real applications, in the order the ladder puts them: a summary
    denial with no engagement, a referred denial, and a granted application that
    drew a requested response and an amicus brief. Suggestive of a structure, and
    far too few for a rate — which is why none is published."""
    assert escalation_signals(_STAY_CIRCUIT) == (False, False, 0)
    assert escalation_signals(_STAY_REFERRED) == (False, True, 0)
    assert escalation_signals(
        [
            "Application (23A350) for a stay, submitted to The Chief Justice.",
            "Response to application (23A350) requested by The Chief Justice.",
            "Brief amicus curiae of Energy Infrastructure Council filed.",
            "Application (23A350) referred to the Court.",
        ]
    ) == (True, True, 1)


# --- ingestion: an application maps to a resolved row -----------------------------


def _payload(*entries: tuple[str, str]) -> dict[str, object]:
    return {
        "CaseNumber": "24A1099 ",
        "DocketedDate": "May 14, 2025",
        "LowerCourt": "United States Court of Appeals for the Fourth Circuit",
        "ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries],
    }


def test_an_application_resolves_through_its_own_vocabulary() -> None:
    """Ingested on the cert path an application never resolves — the cert order
    patterns match nothing in its proceedings, so it would sit open forever."""
    payload = _payload(
        ("May 14 2025", "Application (24A1099) for a stay, submitted to The Chief Justice."),
        (
            "May 23 2025",
            "Application (24A1099) for stay presented to The Chief Justice and by him "
            + "referred to the Court is denied.",
        ),
    )
    cert = map_live_docket(payload, 9_500_024_001)
    assert cert["disposition"] is None  # the cert resolver reads nothing here

    interim = map_live_docket(payload, 9_500_024_001, form="application")
    assert interim["disposition"] == "denied"
    assert interim["date_terminated"] == "2025-05-23"


def test_an_application_carries_no_cert_stage_columns() -> None:
    """It has no cert stage. Dating one as a cert grant would put a stay into the
    cert population's timing, since `resolution_date` prefers those columns; a
    distribution count of 0 would put it in the weakest salience band rather than
    outside the band system entirely."""
    record = map_live_docket(
        _payload(("May 23 2025", "Application (24A1099) denied by Justice Kagan.")),
        9_500_024_001,
        form="application",
    )
    assert record["date_cert_granted"] is None
    assert record["date_cert_denied"] is None
    assert record["distributed_for_conference"] is None
    assert record["cvsg_date"] is None
    assert record["distribution_count"] is None  # unobservable, not zero


def test_the_last_disposing_entry_wins_on_the_interim_docket() -> None:
    """Opposite to the cert side's first-match rule, because an application can be
    deferred pending argument and decided months later. Verbatim from 23A350."""
    record = map_live_docket(
        _payload(
            ("Dec 20 2023", "Application (23A350) referred to the Court."),
            (
                "Dec 20 2023",
                "Consideration of the applications for stay (23A349, 23A350) presented "
                + "to The Chief Justice and by him referred to the Court is deferred "
                + "pending oral argument.",
            ),
            ("Feb 21 2024", "Argued."),
            (
                "Jun 27 2024",
                "Applications for stays (23A349, 23A350, 23A351, and 23A384) granted by the Court.",
            ),
        ),
        9_500_023_350,
        form="application",
    )
    assert record["disposition"] == "granted"
    assert record["date_terminated"] == "2024-06-27"


def test_the_application_branch_lands_the_conditioning_columns() -> None:
    """The ask and the three ladder signals become corpus columns at ingest —
    under the corpus split the proceedings text lives only in the content store,
    so a column is the one place an interim cohort can be assembled from."""
    record = map_live_docket(
        _payload(
            ("Dec 18 2023", "Application (23A350) for a stay, submitted to The Chief Justice."),
            ("Dec 19 2023", "Response to application (23A350) requested by The Chief Justice."),
            ("Dec 20 2023", "Brief amicus curiae of Energy Infrastructure Council filed."),
            ("Dec 20 2023", "Application (23A350) referred to the Court."),
        ),
        9_500_023_350,
        form="application",
    )
    assert record["application_kind"] == "substantive"
    assert record["response_requested"] is True
    assert record["referred_to_court"] is True
    assert record["amicus_briefs"] == 1


def test_a_cert_docket_never_carries_application_columns() -> None:
    """None — the never-application-parsed sentinel — not a confident 'unknown'
    or False: the cert branch does not read the interim signals at all, and the
    storage latches rely on the distinction."""
    record = map_live_docket(
        _payload(("May 14 2025", "Petition for a writ of certiorari filed.")), 9_025_000_100
    )
    assert record["application_kind"] is None
    assert record["response_requested"] is None
    assert record["referred_to_court"] is None
    assert record["amicus_briefs"] is None


def test_the_frontier_walk_probes_the_interim_sequence() -> None:
    """Applications are a third stream, addressed and identified differently: a
    cert petition and an application can share `(term, serial)` and are different
    matters, so they cannot share an id range."""
    forms = {name: form for name, _, form in STREAMS}
    assert forms == {"paid": "cert", "ifp": "cert", "application": "application"}
    assert live_application_id(24, 1) != live_docket_id(24, 1)
