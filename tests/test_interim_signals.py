"""Reading the interim docket — what an application asks, and how it ends.

Every fixture here is verbatim from supremecourt.gov, because the two readers
exist to survive real docket prose and every bug found while building them came
from text that looked like something it was not.
"""

from __future__ import annotations

from datetime import date

from fedcourtsai.cert_backtest import truncate_snapshot
from fedcourtsai.pipeline.ingest import default_event, from_live_record, map_live_docket
from fedcourtsai.pipeline.interim_signals import (
    ApplicationKind,
    ReferralPosture,
    amicus_briefs,
    application_arrival_date,
    application_kind,
    escalation_signals,
    is_predictable_application,
    match_interim_disposition,
    referral_posture,
    response_filed_date,
    response_requested,
    response_requested_date,
)
from fedcourtsai.pipeline.live import STREAMS
from fedcourtsai.provision import moment_cutoff
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


def test_a_brief_filed_by_several_amici_counts_like_one_filed_by_one() -> None:
    """The plural is half the record, not a stylistic variant: a brief filed by
    several amici is docketed with the noun declined, and a singular-only pattern
    therefore reads about half the amicus record — least of it where interest is
    highest, which is exactly where the stakes proxy is supposed to speak."""
    assert amicus_briefs(["Brief amici curiae of AARP, et al. filed."]) == 1
    assert (
        amicus_briefs(
            [
                "Brief amici curiae of AARP, et al. filed.",
                "Brief amicus curiae of American Association for Justice filed.",
            ]
        )
        == 2
    )


def test_an_attempt_at_a_brief_is_not_a_brief() -> None:
    """The pre-acceptance shapes, verbatim — a motion for leave and its denial, a
    submission awaiting the Clerk, a rejection — and none of them is a brief the
    Court has. Each is also a state a real brief passes *through*, and the docket
    appends the acceptance as its own later entry rather than rewriting the
    earlier one — so counting one of these counts a single brief twice, and the
    corpus column max-latches, which would make that overcount permanent."""
    assert (
        amicus_briefs(
            [
                "Motion for leave to file amicus brief filed by Cato Institute.",
                "Motion for leave to file amicus brief filed by Cato Institute DENIED.",
                "Amicus brief of Lepanto Institute submitted.",
                "Amicus brief of American Atheist, Inc., et al. not accepted for filing. "
                + "(To be corrected and resubmitted - April 9, 2025)",
            ]
        )
        == 0
    )


def test_the_rejected_brief_and_its_corrected_refiling_count_once() -> None:
    """24-394's rejection and its corrected refiling, in docket order: the same
    amicus, rejected and accepted on the same day. Both entries stand on the
    record forever, so the count has to read the pair as the one brief it is."""
    assert (
        amicus_briefs(
            [
                "Amicus brief of American Atheist, Inc., et al. not accepted for filing. "
                + "(To be corrected and resubmitted - April 9, 2025)",
                "Brief amici curiae of American Atheist, Inc., et al. filed. VIDED. (Distributed)",
            ]
        )
        == 1
    )


# 25-498 — the two filing shapes on one docket: five briefs on the record (four
# of them plural), then six submissions awaiting the Clerk. Verbatim.
_MIXED_AMICUS = [
    "Brief amici curiae of AARP, et al. filed.",
    "Brief amicus curiae of American Association for Justice filed.",
    "Brief amici curiae of Americans for Financial Reform, et al. filed.",
    "Brief amici curiae of Investment Law Scholars filed.",
    "Brief amici curiae of Phyllis C. Borzi, et al. filed.",
    "Amicus brief of The American Investment Council & The Managed Funds Association submitted.",
    "Amicus brief of American Benefits Council submitted.",
    "Amicus brief of The National Association of Manufacturers submitted.",
    "Amicus brief of Chamber of Commerce of the United States of America, American "
    + "Retirement Association, Business Roundtable, Committee on Investment of Employee "
    + "Benefit Assets, The ERISA Industry Committee, Securities Industry and Financial "
    + "Markets Association, and Stable Value Investment Association submitted.",
    "Amicus brief of Investment Company Institute submitted.",
    "Amicus brief of United States of America submitted.",
]


def test_a_mixed_docket_counts_the_briefs_on_the_record() -> None:
    """Eleven entries naming an amicus, five briefs the Court has. The submissions
    are three days old at this snapshot and not yet accepted; when the Clerk takes
    them the docket says so in its own entries and the count rises then, which is
    the direction a max-latched column can follow."""
    assert amicus_briefs(_MIXED_AMICUS) == 5


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


def test_the_amicus_column_takes_the_plural_off_the_docket_text() -> None:
    """The column the escalation ladder and the increment claim both read is
    written here, from the proceedings text, so the counter's reading has to
    survive the trip: an application whose briefs were all filed by several amici
    must not land as a zero. On the cert path the trio is never parsed at all,
    which is what `None` means in that column."""
    entries = (
        ("May 14 2025", "Application (24A1099) for a stay, submitted to The Chief Justice."),
        ("Jun 02 2025", "Brief amici curiae of AARP, et al. filed."),
        ("Jun 03 2025", "Brief amici curiae of Investment Law Scholars filed."),
        ("Jun 04 2025", "Amicus brief of American Benefits Council submitted."),
    )
    record = map_live_docket(_payload(*entries), 9_500_024_001, form="application")
    assert record["amicus_briefs"] == 2
    assert map_live_docket(_payload(*entries), 9_500_024_001)["amicus_briefs"] is None


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


# --- the two dated response moments ---------------------------------------------


def _entries(*rows: tuple[str, str]) -> list[tuple[str, str | None]]:
    return [(text, day) for day, text in rows]


def test_the_request_and_the_filing_are_read_apart() -> None:
    """They share an opening clause, and conflating them was a real bug.

    "Response to application (25A97) requested by Justice Alito, due by 4pm"
    and "Response to application from respondent Florida filed." both start the
    same way. An anchor-only pattern reads a third of the requests as filings —
    and since the two moments have very different horizons, that would have
    published one moment's numbers under the other's name.
    """
    entries = _entries(
        ("Jul 24 2025", "Response to application (25A97) requested by Justice Alito, due by 4pm."),
        ("Jul 30 2025", "Response to application from respondent Florida filed."),
    )
    assert response_requested_date(entries) == date(2025, 7, 24)
    assert response_filed_date(entries) == date(2025, 7, 30)


def test_a_respondent_name_carrying_periods_still_reads_as_filed() -> None:
    # "et al." ends a sentence as far as a `[^.]` bound is concerned, and
    # stopping there dropped a third of the real filings.
    entries = _entries(
        ("Aug 1 2025", "Response to application from respondents Michael Williams, et al. filed.")
    )
    assert response_filed_date(entries) == date(2025, 8, 1)


def test_a_request_alone_yields_no_filing_date() -> None:
    entries = _entries(
        ("Jul 24 2025", "Response to application (25A97) requested by Justice Kagan.")
    )
    assert response_requested_date(entries) == date(2025, 7, 24)
    assert response_filed_date(entries) is None


def test_the_first_response_wins() -> None:
    entries = _entries(
        ("Jul 30 2025", "Response to application from respondent Texas filed."),
        ("Aug 2 2025", "Response to application from respondent Louisiana filed."),
    )
    assert response_filed_date(entries) == date(2025, 7, 30)


def test_an_undated_entry_yields_no_moment() -> None:
    # The flag may still be set from the same entry; a date that opens an event
    # is held to the stricter standard.
    assert response_filed_date([("Response to application from respondent X filed.", None)]) is None
    assert response_requested([("Response to application requested by Justice Alito.")]) is True


# --- the arrival moment ----------------------------------------------------------


def test_the_application_opens_at_its_own_submission_entry() -> None:
    """The interim baseline's declared moment is arrival, so it needs a date.

    The submission entry is the docket's own record of when the application
    reached it, and on a row carrying no docketing date it is the only one —
    without it the moment is declared with no boundary, which is what sends
    provisioning back to the latest stored payload.
    """
    entries = _entries(
        ("May 14 2025", "Application (24A1099) for a stay, submitted to The Chief Justice."),
        (
            "May 23 2025",
            "Application (24A1099) for stay presented to The Chief Justice and by him "
            + "referred to the Court is denied.",
        ),
    )
    assert application_arrival_date("24A1099", entries) == date(2025, 5, 14)


def test_a_companion_applications_number_does_not_supply_the_arrival() -> None:
    # A consolidated matter recites its companions by number. The anchor is the
    # docket's OWN number, so a companion filed earlier cannot move this
    # docket's arrival back before the application existed.
    entries = _entries(
        ("May 1 2025", "Application (24A1000) for a stay in the companion matter, submitted."),
        ("May 14 2025", "Application (24A1099) for a stay, submitted to The Chief Justice."),
    )
    assert application_arrival_date("24A1099", entries) == date(2025, 5, 14)


def test_the_earliest_submission_wins_however_the_docket_is_ordered() -> None:
    # Only the submission clause matches, so the disposition below cannot
    # supply a date whatever order the stored entries arrive in.
    entries = _entries(
        ("May 23 2025", "Application (24A1099) denied by Justice Kagan."),
        ("May 14 2025", "Application (24A1099) for a stay, submitted to The Chief Justice."),
    )
    assert application_arrival_date("24A1099", entries) == date(2025, 5, 14)


def test_a_lost_head_entry_yields_no_arrival_rather_than_the_disposition_date() -> None:
    """The failure the submission clause exists to refuse.

    On most application dockets the next entry naming the number after the
    submission *is the disposition*. A bare-number anchor over a payload whose
    head entry is missing would therefore stamp the arrival at the day the
    application was decided — and the cell would be provisioned under a
    well-formed `truncated` cutoff admitting its own outcome. Requiring the
    filing verb degrades that to `None`, and the stamp falls back to the
    docketing date, which is merely late.
    """
    decapitated = _entries(
        ("May 20 2025", "Response to application (24A1099) filed."),
        ("May 23 2025", "Application (24A1099) denied by Justice Kagan."),
    )
    assert application_arrival_date("24A1099", decapitated) is None

    # End to end: the baseline takes the docketing date rather than the denial.
    payload = {
        "CaseNumber": "24A1099",
        "DocketedDate": "May 14, 2025",
        "ProceedingsandOrder": [
            {"Date": day, "Text": text} for text, day in decapitated if day is not None
        ],
    }
    record = map_live_docket(payload, live_application_id(24, 1099), form="application")
    assert record["application_filed_at"] is None
    assert default_event(from_live_record(record)).opened_at == date(2025, 5, 14)


def test_a_renewal_to_a_second_justice_does_not_displace_the_submission() -> None:
    # The Clerk's renewal form is "refiled and submitted", which satisfies the
    # submission anchor — so the verb alone does not exclude it. With the head
    # entry present `min` keeps the original.
    entries = _entries(
        ("May 14 2025", "Application (24A1099) for a stay, submitted to Justice Alito."),
        ("May 19 2025", "Application (24A1099) refiled and submitted to Justice Kagan."),
    )
    assert application_arrival_date("24A1099", entries) == date(2025, 5, 14)


def test_a_refiling_alone_yields_no_arrival() -> None:
    """The case `min` cannot decide, and the one that discriminates.

    A refiling always follows a denial, so a decapitated payload whose only
    submission-shaped entry is the renewal would be stamped *after* the
    application's own first disposition — the same admits-its-own-outcome
    failure the submission clause exists to refuse, wearing the filing verb.
    The renewal exclusion is what refuses it; the stamp falls back to docketing.
    """
    entries = _entries(
        ("May 19 2025", "Application (24A1099) refiled and submitted to Justice Kagan."),
    )
    assert application_arrival_date("24A1099", entries) is None

    payload = {
        "CaseNumber": "24A1099",
        "DocketedDate": "May 14, 2025",
        "ProceedingsandOrder": [
            {"Date": "May 19 2025", "Text": "Application (24A1099) refiled and submitted."},
        ],
    }
    record = map_live_docket(payload, live_application_id(24, 1099), form="application")
    assert record["application_filed_at"] is None
    assert default_event(from_live_record(record)).opened_at == date(2025, 5, 14)


def test_the_cut_separates_arrival_from_the_response_request_it_precedes() -> None:
    """The moment separation the fix buys, on the shape 57% of the sample takes.

    An application submitted the day before it is docketed, whose response
    request lands on the docketing day itself. Stamped at docketing the cut
    falls the day after and admits the response request — the interim stage's
    strongest cheap signal, and the trigger of a *different* declared moment
    (`evt-order-response-requested-disposition`). The arrival cell would then
    be conditioned on the thing that defines the moment after it.
    """
    payload = {
        "CaseNumber": "26A203",
        "DocketedDate": "August 14, 2026",
        "ProceedingsandOrder": [
            {
                "Date": "Aug 13 2026",
                "Text": "Application (26A203) for a stay of mandate, submitted to Justice Kagan.",
            },
            {
                "Date": "Aug 14 2026",
                "Text": "Response to application (26A203) requested, due August 18, 2026.",
            },
        ],
    }
    record = map_live_docket(payload, live_application_id(26, 203), form="application")
    assert record["date_filed"] == "August 14, 2026"
    assert record["application_filed_at"] == "2026-08-13"
    assert record["response_requested_at"] == "2026-08-14"

    event = default_event(from_live_record(record))
    assert event.opened_at == date(2026, 8, 13)
    cutoff = moment_cutoff("evt-motion-disposition", [event])
    assert cutoff == date(2026, 8, 14)

    kept, dropped = truncate_snapshot(payload, cutoff)
    assert [entry["Text"] for entry in kept["ProceedingsandOrder"]] == [
        "Application (26A203) for a stay of mandate, submitted to Justice Kagan."
    ]
    assert dropped == 1
    # The docketing stamp would have kept it: cutoff 2026-08-15, both entries.
    stale, _ = truncate_snapshot(payload, date(2026, 8, 15))
    assert len(stale["ProceedingsandOrder"]) == 2


def test_an_undated_submission_entry_yields_no_arrival() -> None:
    # The same discipline the two response moments apply: a date that opens an
    # event is never guessed at.
    entries: list[tuple[str, str | None]] = [
        ("Application (24A1099) for a stay, submitted to The Chief Justice.", None)
    ]
    assert application_arrival_date("24A1099", entries) is None


def test_an_unusable_docket_number_yields_no_arrival() -> None:
    # Nothing to anchor on, so nothing is read — rather than matching every
    # entry that happens to carry a parenthesis.
    entries = _entries(("May 14 2025", "Application (24A1099) for a stay, submitted."))
    assert application_arrival_date("", entries) is None
    assert application_arrival_date("  ", entries) is None


def test_an_application_with_no_docketed_date_still_opens_at_its_arrival() -> None:
    """The shape the fix exists for.

    A payload carrying proceedings but no ``DocketedDate`` opened its baseline
    at nothing at all, so the provisioned cell fell back to an as-stored
    snapshot carrying filings that postdate the moment it claims to represent.
    """
    payload = {
        "CaseNumber": "24A1099 ",
        "ProceedingsandOrder": [
            {
                "Date": "May 14 2025",
                "Text": "Application (24A1099) for a stay, submitted to The Chief Justice.",
            },
            {"Date": "May 20 2025", "Text": "Response to application (24A1099) filed."},
        ],
    }
    record = map_live_docket(payload, live_application_id(24, 1099), form="application")
    assert record["date_filed"] is None
    assert record["application_filed_at"] == "2025-05-14"

    event = default_event(from_live_record(record))
    assert event.event_id == "evt-motion-disposition"
    assert event.opened_at == date(2025, 5, 14)
    # And the stamp is what places the cell: the cutoff is the day after the
    # moment, exclusive, so the application's own entry survives and the
    # response that postdates it does not.
    assert moment_cutoff("evt-motion-disposition", [event]) == date(2025, 5, 15)


def test_the_submission_entry_wins_over_a_docketing_date_that_precedes_it() -> None:
    """The stamp is where provisioning cuts, so it must keep its own trigger.

    `_payload` dates its docketing May 14; the submission entry here is a day
    later. Stamped at the docketing date the cut would fall on May 15 — before
    the entry that states the application — and the arrival cell would be
    handed an application docket with no application on it.
    """
    payload = _payload(
        ("May 15 2025", "Application (24A1099) for a stay, submitted to Justice Kagan."),
        ("May 23 2025", "Application (24A1099) denied by Justice Kagan."),
    )
    record = map_live_docket(payload, live_application_id(24, 1099), form="application")
    assert record["date_filed"] == "May 14, 2025"
    assert record["application_filed_at"] == "2025-05-15"

    event = default_event(from_live_record(record))
    assert event.opened_at == date(2025, 5, 15)
    cutoff = moment_cutoff("evt-motion-disposition", [event])
    assert cutoff == date(2025, 5, 16)
    # The invariant the ordering exists for: the trigger entry survives its own
    # cut, so the cell reads the application it is forecasting — and nothing
    # filed after it. A May 15 cutoff (the docketing date + 1) would have left
    # an application docket with no application on it.
    kept, dropped = truncate_snapshot(payload, cutoff)
    assert [entry["Text"] for entry in kept["ProceedingsandOrder"]] == [
        "Application (24A1099) for a stay, submitted to Justice Kagan."
    ]
    assert dropped == 1


def test_a_capital_marked_application_still_finds_its_own_number() -> None:
    # The anchor reads the STRIPPED number, so the display annotation upstream
    # appends to some case numbers cannot make the docket unmatchable.
    payload = {
        **_payload(("May 14 2025", "Application (24A1099) for a stay, submitted.")),
        "CaseNumber": "24A1099 *** CAPITAL CASE ***",
    }
    record = map_live_docket(payload, live_application_id(24, 1099), form="application")
    assert record["docket_number"] == "24A1099"
    assert record["application_filed_at"] == "2025-05-14"


def test_a_cert_docket_never_takes_the_application_arrival_read() -> None:
    # The read is application-branch only, so a cert docket's baseline keeps
    # opening at its docketing date and nothing about the cert lane moves.
    payload = {
        **_payload(("Jan 15 2025", "Petition for a writ of certiorari filed.")),
        "CaseNumber": "24-1099",
        "DocketedDate": "January 15, 2025",
    }
    record = map_live_docket(payload, live_docket_id(24, 1099))
    assert record["application_filed_at"] is None
    event = default_event(from_live_record(record))
    assert event.event_id == "evt-petition-disposition"
    assert event.opened_at == date(2025, 1, 15)
