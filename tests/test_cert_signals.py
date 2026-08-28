"""The cert-disposition resolver's pattern behavior, pinned on real order-list text.

A resolver match records ground truth (disposition + decision date), so a false
positive fabricates an outcome while a miss merely leaves a decided docket to
the routing backstop — the negative space matters as much as the positive.
Match fixtures are the entry shapes decided SCOTUS dockets actually carry;
no-match fixtures are the pending-shaped near-misses a broadened pattern must
never read as a disposition.
"""

from datetime import date

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.cert_signals import (
    DISTRIBUTION_PARSES,
    dissent_from_denial,
    match_disposition_signal,
    mootness_disposition,
    refused_grant_sentence,
    snapshot_distribution_count,
)
from fedcourtsai.pipeline.ingest import _live_distribution_count, _live_resolution
from fedcourtsai.schemas import Disposition

# --- dispositions the resolver must read -----------------------------------------


def test_bare_vacate_and_remand_reads_as_a_gvr() -> None:
    # The GVR form with no "grant" word: the mandatory-jurisdiction direct
    # appeal disposed in light of a related merits decision.
    matched = match_disposition_signal(
        "Judgment VACATED and case REMANDED for further consideration in light "
        "of Louisiana v. Callais."
    )
    assert matched is not None
    disposition, label, snippet = matched
    assert disposition == Disposition.gvr
    assert label == "GVR"
    assert "VACATED" in snippet


def test_comma_form_vacate_and_remand_reads_as_a_gvr() -> None:
    matched = match_disposition_signal(
        "Judgment VACATED, and case REMANDED for further consideration in "
        "light of Louisiana v. Callais."
    )
    assert matched is not None and matched[0] == Disposition.gvr


def test_prose_form_naming_the_lower_court_reads_as_a_gvr() -> None:
    # The order-list prose names the lower court between "judgment" and
    # "vacated"; the first gap is sized for it.
    matched = match_disposition_signal(
        "The judgment of the United States Court of Appeals for the Armed "
        "Forces is vacated, and the case is remanded for further consideration."
    )
    assert matched is not None and matched[0] == Disposition.gvr and matched[1] == "GVR"


def test_cert_before_judgment_grant_with_vacatur_reads_as_a_gvr() -> None:
    # A cert-before-judgment grant that vacates and remands is a GVR, so the
    # grant-and-vacate-and-remand row reads it as `gvr`; the bare-CBJ forms
    # without a vacatur are deliberate misses (see the no-match section).
    matched = match_disposition_signal(
        "Petition for writ of certiorari before judgment GRANTED. Judgment "
        "VACATED and case REMANDED."
    )
    assert matched is not None and matched[0] == Disposition.gvr


def test_existing_shapes_still_read() -> None:
    # The pre-existing rows are untouched: the classic order-list forms.
    for text, expected in (
        ("Petition DENIED.", Disposition.denied),
        ("Petition GRANTED limited to Question 1.", Disposition.granted),
        ("Petition DISMISSED under Rule 46.", Disposition.dismissed),
        ("The petition was GVR'd in light of Ramirez.", Disposition.gvr),
        (
            "Petition GRANTED. Judgment VACATED and case REMANDED for further consideration.",
            Disposition.gvr,
        ),
        ("certiorari denied", Disposition.denied),
    ):
        matched = match_disposition_signal(text)
        assert matched is not None and matched[0] == expected, text


# --- pending-shaped near-misses that must never read as a disposition -------------


def test_expedite_motion_orders_are_not_the_cert_disposition() -> None:
    # The clerk's order on an expedite motion embeds the full cert noun phrase
    # as the *motion's object* ("consideration of the petition ..."), with the
    # motion's verb right after — and it appears earlier in docket order than
    # the petition's own disposition, so a match here would stamp the wrong
    # outcome with the wrong date. Both polarities, both the plain and the
    # before-judgment forms, must stay unmatched.
    for text in (
        "Motion of the Special Counsel to expedite consideration of the "
        + "petition for a writ of certiorari before judgment granted.",
        "Motion of petitioners to expedite consideration of the petition "
        + "for a writ of certiorari before judgment denied.",
        "Motion of petitioner to expedite consideration of the petition "
        + "for a writ of certiorari granted.",
        "Motion of respondent to expedite consideration of the petition "
        + "for a writ of certiorari denied.",
    ):
        assert match_disposition_signal(text) is None, text


def test_qualified_motion_orders_about_the_petition_are_not_the_cert_disposition() -> None:
    # Same shape as the expedite order — the petition is the object of
    # "consideration of", so the verb decides the motion — but the motion word
    # carries a qualifier, so the subject anchor has to see past it. The
    # deferral form is the live one: it precedes the petition's own disposition
    # in docket order, so a match stamps a grant on a case that was never
    # granted, dated to the motion order.
    for text in (
        "Joint motion to defer consideration of the petition for a writ of certiorari GRANTED.",
        "Joint motion to defer consideration of the petition for a writ of certiorari DENIED.",
        "Consent motion to defer consideration of the petition for a writ of "
        + "certiorari is granted.",
        "The joint motions to defer consideration of the petitions for writs "
        + "of certiorari are granted.",
        "Petitioner's motion to defer consideration of the petition for a "
        + "writ of certiorari granted.",
        # The typographic apostrophe, which the clerk types as often as the
        # ASCII one: a possessive qualifier must count as one word either way,
        # or the anchor loses the bound and the sentence reads as an order.
        "Petitioner\u2019s motion to defer consideration of the petition for a "
        + "writ of certiorari granted.",
        "The unopposed joint motion to defer consideration of the petition for "
        + "a writ of certiorari is granted.",
    ):
        assert match_disposition_signal(text) is None, text


def test_qualified_motion_compounds_that_do_grant_the_petition_still_read() -> None:
    # The widening's own risk direction: shapes the subject anchor reaches,
    # which must still resolve because the petition is a *conjunctive subject*
    # rather than the motion's object — the clerk's "and" is what marks it.
    # Without these the precision fixtures above could be satisfied by a guard
    # that ate every qualified-motion order outright.
    for text in (
        "Motions to proceed in forma pauperis and petitions for writs of certiorari GRANTED.",
        "Petitioner's motion for leave to proceed in forma pauperis and the "
        + "petition for a writ of certiorari are granted.",
        "The unopposed joint motion to expedite and the petition for a writ of "
        + "certiorari are GRANTED.",
    ):
        matched = match_disposition_signal(text)
        assert matched is not None and matched[0] == Disposition.granted, text


def test_a_qualified_motion_order_beside_a_real_grant_leaves_the_grant_readable() -> None:
    # The guard is sentence-scoped, so suppressing the motion sentence must not
    # cost the petition sentence next to it — the entry still resolves as a
    # grant, off the petition's own order.
    matched = match_disposition_signal(
        "Joint motion to defer consideration of the petition for a writ of "
        "certiorari DENIED.  Petition for a writ of certiorari GRANTED."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_filing_recital_with_a_conditional_disposition_is_not_an_order() -> None:
    # A docketing recital — the sentence ends in "filed" — decides nothing,
    # however much disposition language rides inside it. This exact entry
    # fabricated a corpus row's grant, dated to the motion's filing.
    assert (
        match_disposition_signal(
            "Motion of petitioner to expedite consideration of the petition for "
            "a writ of certiorari and to expedite merits briefing and oral "
            "arugment in the event the petition is granted filed."  # (sic) — verbatim
        )
        is None
    )


def test_compound_expedite_and_petition_grant_still_reads() -> None:
    # The conjunctive compound — motion AND petition granted together — is a
    # real cert grant: the motion word opens the sentence, but nothing recites
    # the petition as "consideration of" an object.
    matched = match_disposition_signal(
        "The motion to expedite and the petition for a writ of certiorari are "
        "GRANTED.  The petition for a writ of certiorari before judgment in "
        "No. 24-1287 is granted.  The cases are consolidated."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_stay_application_treated_as_petition_and_granted_still_reads() -> None:
    # The application-order form that converts a stay application into a CBJ
    # petition and grants it — a genuine grant that must keep latching.
    matched = match_disposition_signal(
        "Application (25A264) for stay presented to The Chief Justice and by "
        "him referred to the Court is granted. The July 17, 2025 order of the "
        "United States District Court is stayed. The application is also "
        "treated as a petition for a writ of certiorari before judgment, and "
        "the petition is granted (case No. 25-332)."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_rule_398_compound_dismissal_still_reads() -> None:
    # The Rule 39.8 long form opens with a motion word too — the guard must
    # not eat it: "writ of certiorari is dismissed" is the real disposition.
    matched = match_disposition_signal(
        "The motion for leave to proceed in forma pauperis is denied, and the "
        "petition for a writ of certiorari is dismissed.  See Rule 39.8."
    )
    assert matched is not None and matched[0] == Disposition.dismissed


def test_ancillary_motion_orders_about_the_petition_are_not_the_cert_disposition() -> None:
    # Verbatim proceedings text from the SCOTUS dockets whose stored
    # `date_cert_granted` these sentences fabricated — an extension of time to
    # respond, a delayed distribution, an unsealing. In each the petition is the
    # motion's *object*, never the subject of the granting verb, and each order
    # predates the petition's own denial or Rule 46 dismissal, so a match here
    # records a grant on a case that was never granted and dates it to a
    # housekeeping order. The clerk's typos ("peition", "writ certiorari") are
    # kept as filed: the guard has to hold on the text as it is stored, not on a
    # tidied version of it.
    for text in (
        "The motions to extend the time to file responses to the petition for a "
        + "writ of certiorari are granted and the time is extended to and "
        + "including March 18, 2019, for all respondents.",
        "The motions to extend the time to file responses to the petition are "
        + "granted and the time is extended to and including April 29, 2020, "
        + "for all respondents.",
        "The motions to extend the time to file responses to the peition for a "
        + "writ of certiorari are granted and the time is extended to and "
        + "including January 13, 2021, for all respondents.",
        "The motions to extend the time to file responses to the petition for a "
        + "writ of certiorari are granted in part and the time is extended to "
        + "and including June 1, 2021, for all respondents.",
        "Motion to delay distribution of the petition for a writ certiorari "
        + "granted. The petition will be distributed on the next distribution "
        + "date after April 30, 2020, which is May 5, 2020.",
        "Motion to delay distribution of the petition for a writ certiorari "
        + "granted; the petition will be distributed on June 17, 2020.",
        "Motion to delay distribution of the petition for a writ certiorari "
        + "granted in part; the petition will be distributed on Wednesday, "
        + "June 10, 2020.",
        "Motion to delay distribution of the petition granted. The petition "
        + "will be distributed December 23, 2020.",
        # Not "motion" at all — the clerk files the same paper as a request, so
        # the subject anchor has to reach it or this one shape survives the fix.
        "Petitioner's request to delay distribution of the petition granted. "
        + "The petition will be distributed on January 21, 2021.",
        "Motion to unseal the petition for a writ of certiorari GRANTED.",
        "Motion (21M21) for leave to file a petition for a writ of certiorari "
        + "under seal with redacted copies for the public record Granted.",
    ):
        assert match_disposition_signal(text) is None, text


def test_the_real_terminals_of_those_dockets_still_read() -> None:
    # The other half of the same fix: with the ancillary orders suppressed, the
    # entry the parser reaches is the docket's actual terminal. Both forms the
    # class carries must read, or the cases would go from mislabeled to
    # unresolved.
    for text, expected in (
        ("Petition DENIED.", Disposition.denied),
        ("Petition Dismissed - Rule 46.", Disposition.dismissed),
    ):
        matched = match_disposition_signal(text)
        assert matched is not None and matched[0] == expected, text


def test_conjoined_petition_orders_that_open_with_a_motion_still_read() -> None:
    # The escape the guard turns on, in the clerk's own words: every compound
    # order that really does decide the petition conjoins it into the subject
    # with "and". These are verbatim corpus entries — without them the
    # precision fixtures above would be satisfied by a guard that swallowed
    # every motion-opening order outright.
    for text, expected in (
        (
            "The motion for leave to proceed in forma pauperis is denied, and "
            + "the petition for a writ of certiorari is dismissed.",
            Disposition.dismissed,
        ),
        (
            "Motion to proceed in forma pauperis and petition for a writ of certiorari GRANTED.",
            Disposition.granted,
        ),
        (
            "The motion to expedite and the petition for a writ of certiorari are GRANTED.",
            Disposition.granted,
        ),
        # A "request" subject with the conjunction — and the typographic
        # apostrophe the clerk types, so the qualifier stays one word: the
        # widened anchor reaches this sentence, and only the escape keeps it a
        # grant.
        (
            "The Special Counsel\u2019s request to treat the stay application "
            + "as a petition for a writ of certiorari s granted (23-939), and "
            + "that petition is granted limited to the following question: "
            + "Whether a former President enjoys presidential immunity.",
            Disposition.granted,
        ),
    ):
        matched = match_disposition_signal(text)
        assert matched is not None and matched[0] == expected, text


def test_a_motions_own_coordination_is_not_the_petition_conjunction() -> None:
    # The escape is anchored on "and" running straight into the cert noun, so a
    # motion that coordinates its own purposes — or an extension order whose
    # tail reads "and the time is extended" — never buys its way out of the
    # guard.
    for text in (
        "Motion to extend the time to file a response and to delay "
        + "distribution of the petition for a writ of certiorari granted.",
        "Motion to delay distribution of the petition for a writ of certiorari "
        + "granted, and the time is extended to and including June 1, 2021.",
        # A conjoined petition that is not the cert petition. Without the
        # lookahead the escape would fire on "and the petition for", and the
        # ancillary order would read as a cert disposition again.
        "Motion to delay distribution of the petition for a writ of certiorari "
        + "granted, and the petition for rehearing is denied.",
        "Motion to unseal the petition for a writ of certiorari GRANTED, and "
        + "the petition for leave to proceed in forma pauperis is granted.",
    ):
        assert match_disposition_signal(text) is None, text


def test_the_refused_grant_sentence_is_the_text_a_grant_was_read_out_of() -> None:
    # The audit handle the convergence sweep's withdrawal arm rests on: it
    # names the ancillary sentence a stored `granted` came from, and stays
    # silent both where a grant genuinely reads and where nothing grant-shaped
    # appears at all.
    refused = refused_grant_sentence(
        "The motions to extend the time to file responses to the petition for a "
        "writ of certiorari are granted and the time is extended to and "
        "including March 18, 2019, for all respondents."
    )
    assert refused is not None and refused.startswith("The motions to extend the time")
    assert refused_grant_sentence("Petition GRANTED.") is None
    assert refused_grant_sentence("Petition DENIED.") is None
    assert refused_grant_sentence("Distributed for Conference of March 5, 2021.") is None
    # A real compound grant reads, so it is not a refusal to report either.
    assert (
        refused_grant_sentence(
            "The motion to expedite and the petition for a writ of certiorari are GRANTED."
        )
        is None
    )


def test_ifp_grant_plus_cert_grant_compound_still_reads() -> None:
    matched = match_disposition_signal(
        "Motion to proceed in forma pauperis and petition for a writ of "
        "certiorari GRANTED. Judgment VACATED and case REMANDED for further "
        "consideration in light of Hewitt v. United States."
    )
    # The grant-and-vacate-and-remand compound is a GVR.
    assert matched is not None and matched[0] == Disposition.gvr


def test_party_papers_reciting_a_vacatur_are_not_a_disposition() -> None:
    # A brief or letter *describing* a vacatur decides nothing; the
    # entry-start anchor on the judgment-vacated row rejects them.
    for text in (
        "Brief of respondent suggesting that the judgment be vacated and the case remanded filed.",
        "Letter of respondent advising that the judgment below was vacated "
        + "and the case remanded by the Court of Appeals filed.",
    ):
        assert match_disposition_signal(text) is None, text


def test_confession_of_error_motion_is_not_a_disposition() -> None:
    # The SG's vacate-and-remand *motion* asks; it does not decide.
    assert (
        match_disposition_signal(
            "Motion of respondent to vacate the judgment and remand the case "
            "for further proceedings filed."
        )
        is None
    )


def test_en_banc_panel_opinion_vacatur_is_not_a_disposition() -> None:
    # An en banc court vacates the *panel opinion*, not a judgment; the matter
    # is very much alive, and no entry-leading "judgment" anchors the pair.
    assert (
        match_disposition_signal(
            "The panel opinion is VACATED and the case is REMANDED to the panel."
        )
        is None
    )


def test_rehearing_denial_is_not_the_cert_disposition() -> None:
    # The gap between the cert noun and the verb stays one word, so a
    # rehearing denial never resolves the petition.
    assert match_disposition_signal("Petition for rehearing DENIED.") is None


def test_bare_cert_before_judgment_denial_is_a_deliberate_miss() -> None:
    # A CBJ *denial* or dismissal stays unmatched by design: accepting the
    # multi-word gap on those verbs would also accept the expedite-motion recital
    # above, and the miss is cheap — the routing backstop's anchored CBJ shape
    # (termination_signal) parks the quiet decided docket for triage instead of
    # recording. The grant is the deliberate exception (it wastes forward cells);
    # see test_cert_before_judgment_grant_reads_as_granted.
    assert (
        match_disposition_signal("Petition for writ of certiorari before judgment DENIED.") is None
    )
    assert (
        match_disposition_signal("Petition for a writ of certiorari before judgment DISMISSED.")
        is None
    )


def test_cert_before_judgment_grant_reads_as_granted() -> None:
    # The CBJ grant is read (start-anchored to the petition noun), so a decided
    # grant records its outcome and routes to evaluate instead of wasting a
    # forward-predict cell every cycle. Cover the order-list variants: with and
    # without "a", singular/plural, and the "is granted" / bare "granted" forms.
    for text in (
        "Petition for a writ of certiorari before judgment GRANTED.",
        "Petition for writ of certiorari before judgment granted.",
        "The petition for a writ of certiorari before judgment is granted.",
        "Petitions for writs of certiorari before judgment are granted.",
    ):
        matched = match_disposition_signal(text)
        assert matched is not None and matched[0] == Disposition.granted, text
        assert matched[1] == "cert granted before judgment", text


def test_judgment_issued_is_not_a_disposition() -> None:
    # "Judgment Issued" says the matter ended, not *how* — that entry is the
    # routing backstop's business (termination_signal), never the resolver's.
    assert match_disposition_signal("Judgment Issued.") is None


def test_ifp_denial_is_not_a_cert_disposition() -> None:
    # The Rule 39.8 family stays deliberately unresolved (routing backstop
    # territory): "petitioner" does not read as the cert noun, and the many
    # words between "petition" and the verb keep the gap rule unsatisfied.
    assert (
        match_disposition_signal(
            "Motion of petitioner for leave to proceed in forma pauperis DENIED."
        )
        is None
    )


def test_routine_pending_entries_do_not_match() -> None:
    for text in (
        "Petition for a writ of certiorari filed.",
        "DISTRIBUTED for Conference of 9/29/2025.",
        "Brief of respondent in opposition filed.",
        "Reply of petitioner filed. (Distributed)",
    ):
        assert match_disposition_signal(text) is None, text


def test_abbreviation_periods_do_not_split_guard_sentences() -> None:
    # "Inc." / "No." periods are citations, not sentence ends — a false
    # boundary would strip the motion-word opening or the terminal "filed"
    # and let the recital shapes pierce the guard.
    for text in (
        "Motion of petitioner Acme Inc. to expedite consideration of the "
        + "petition for a writ of certiorari granted.",
        "Motion of petitioner to vacate the stay in the event the petition "
        + "is granted in No. 25-332 filed.",
    ):
        assert match_disposition_signal(text) is None, text


def test_semicolon_scopes_a_trailing_filed_clause() -> None:
    # The genuine order before a semicolon-joined "...filed" notation must
    # keep reading — only the trailing clause is a recital.
    matched = match_disposition_signal(
        "Petition for a writ of certiorari granted; statement of Justice Alito filed."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_mootness_disposition_reads_the_munsingwear_and_moot_dismissal_forms() -> None:
    # Mootness practice: the order's own sentence carries the mootness basis.
    assert mootness_disposition(
        "Judgment VACATED and case REMANDED to the United States Court of "
        "Appeals for the Ninth Circuit with instructions to dismiss the case "
        "as moot."
    )
    assert mootness_disposition("Petition for a writ of certiorari dismissed as moot.")
    # Merits dispositions stay standard — including the ordinary GVR.
    assert not mootness_disposition(
        "Judgment VACATED and case REMANDED for further consideration in "
        "light of Louisiana v. Callais."
    )
    assert not mootness_disposition("Petition DENIED.")
    # Sentence-scoped: mootness discussed in a separate sentence is not the basis.
    assert not mootness_disposition(
        "Petition DENIED. Justice Jackson, dissenting, would note the case may be moot."
    )
    # No disposition at all reads False, never mootness.
    assert not mootness_disposition("DISTRIBUTED for Conference of 9/29/2025.")


def test_compound_moot_motion_denial_is_not_a_mootness_basis() -> None:
    # A comma-conjoined compound order: the motion clause is denied AS MOOT,
    # the petition clause is a genuine merits denial — clause scoping keeps
    # the merits denial out of the procedural stratum.
    assert not mootness_disposition(
        "The motion of petitioner to expedite consideration is denied as "
        "moot, and the petition for a writ of certiorari is denied."
    )


def test_cbj_grant_with_a_named_lower_court_reads_as_gvr() -> None:
    # The prose GVR: the cert-before-judgment grant names the lower court
    # between "granted" and "vacated", so the gap-bounded GVR rows miss it and
    # the grant row wins — the tail upgrade must re-label it. This is the
    # scotus/73275185 order shape (May 11, 2026).
    text = (
        "The petition for a writ of certiorari before judgment is granted. The "
        "judgment of the United States District Court for the Northern District "
        "of Alabama is vacated, and the case is remanded to that court for "
        "further consideration in light of Louisiana v. Callais."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.gvr
    assert matched[1] == "GVR"


def test_allcaps_cbj_grant_with_a_named_lower_court_reads_as_gvr() -> None:
    # The terse all-caps clerk form of the same order: no copula anywhere —
    # "Judgment ... VACATED and case REMANDED" — with the lower court named
    # between the verbs, so the gap-bounded rows miss it, the entry-start
    # anchor misses it (the vacatur is the second sentence), and the prose
    # copula the tail otherwise requires never appears. The case-sensitive
    # VACATED alternative is what re-labels it.
    text = (
        "Petition for writ of certiorari before judgment GRANTED. Judgment of "
        "the United States District Court for the Northern District of Alabama "
        "VACATED and case REMANDED for further consideration in light of "
        "Louisiana v. Callais."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.gvr
    assert matched[1] == "GVR"


def test_a_lowercase_narrative_vacatur_does_not_upgrade_a_grant() -> None:
    # The lowercase narrative participle — no ordering voice anywhere — is
    # the shape the tail has always excluded, and the case-sensitive
    # `(?-i:VACATED)` group must not relax it. The named court holds the
    # vacatur beyond the gap-bounded grant..vacate..remand row's reach, so
    # the tail is the only path that could re-label this entry.
    text = (
        "Petition GRANTED. The judgment of the United States Court of Appeals "
        "for the Ninth Circuit, previously vacated and remanded in an earlier "
        "round of this litigation, returns on a renewed petition."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.granted
    assert matched[1] == "cert granted"  # the upgrade never clobbers the label


@pytest.mark.parametrize(
    "tail_sentence",
    [
        # An all-caps entry reciting history: the auxiliary marks the voice
        # as narrative however the participle is cased.
        (
            "THE JUDGMENT OF THE UNITED STATES COURT OF APPEALS FOR THE NINTH "
            "CIRCUIT WAS VACATED AND REMANDED LAST TERM."
        ),
        # Mixed-case narrative with a capitalized participle.
        (
            "The judgment of the United States Court of Appeals for the Ninth "
            "Circuit was VACATED and the case REMANDED last Term."
        ),
        # A suggested vacatur that capitalizes the verbs.
        (
            "The judgment of the United States Court of Appeals for the Ninth "
            "Circuit should be VACATED and the case REMANDED."
        ),
        # A participial-clause recital.
        (
            "The judgment of the United States Court of Appeals for the Ninth "
            "Circuit having been VACATED and the case REMANDED by that court, "
            "the petition is held."
        ),
        # The citation-recital shape: the comma marks the capitalized pair as
        # subsequent-history notation, not this entry's order.
        (
            "The judgment under review in No. 23-100, reported below as "
            "United States v. Doe, VACATED AND REMANDED (9th Cir. 2024), is "
            "attached."
        ),
        # A doubled interior space between auxiliary and participle: the
        # sentence is whitespace-collapsed before matching, so the
        # fixed-width lookbehinds still see the marker.
        (
            "THE JUDGMENT OF THE UNITED STATES COURT OF APPEALS FOR THE NINTH "
            "CIRCUIT WAS  VACATED AND REMANDED LAST TERM."
        ),
    ],
)
def test_a_capitalized_narrative_vacatur_does_not_upgrade_a_grant(tail_sentence: str) -> None:
    # The precision bound the clerk-voice admission must hold: capitalization
    # alone is not the ordering voice. Each shape carries a narrative marker
    # (auxiliary, "having been", or the recital comma) that the lookbehinds
    # bar, so the grant keeps its label. The named court holds each participle
    # beyond the gap-bounded grant..vacate..remand rows' reach, so the tail is
    # the only path that could re-label these entries.
    matched = match_disposition_signal(f"Petition GRANTED. {tail_sentence}")

    assert matched is not None
    assert matched[0] is Disposition.granted


def test_cbj_grant_without_a_vacatur_stays_granted() -> None:
    text = "The petition for a writ of certiorari before judgment is granted."

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.granted
    assert matched[1] == "cert granted before judgment"  # the upgrade never clobbers the label


def test_a_recited_vacatur_does_not_upgrade_a_grant() -> None:
    # The party paper beside the grant recites a vacatur but orders nothing;
    # the tail carries the same non-order-sentence discipline as the main scan.
    # The recital sits beyond the gap-bounded GVR rows' reach (a directly
    # adjacent recital is matched by the pre-existing grant..vacate..remand row
    # across the sentence boundary — a precision bound this change leaves as
    # it found it), so what this pins is the upgrade's own guard.
    text = (
        "Petition GRANTED. The Chief Justice took no part in the consideration "
        "or decision of this petition. Brief of respondent suggesting that the "
        "judgment be vacated and the case remanded filed."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.granted


def test_the_gvr_upgrade_never_invents_a_disposition() -> None:
    # A tail with no disposition signal anywhere stays a miss: the upgrade
    # only re-labels an entry some grant row already matched.
    text = "We note the judgment was vacated and the case remanded previously."

    assert match_disposition_signal(text) is None


def test_the_upgrade_only_ever_touches_a_grant() -> None:
    # The `is Disposition.granted` gate is the only thing keeping a denial
    # beside an order-shaped vacatur a denial.
    text = "Petition DENIED. The judgment of the Court of Appeals is vacated and the case remanded."

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.denied


def test_a_suggested_vacatur_does_not_upgrade_a_grant() -> None:
    # Order voice is required: a suggestion that the judgment *be* or *should
    # be* vacated is not an order, whatever sentence carries it.
    text = (
        "The petition for a writ of certiorari is granted. The Solicitor "
        "General suggests that the judgment below should be vacated and the "
        "case remanded for reconsideration."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.granted


def test_a_narrative_vacatur_does_not_upgrade_a_grant() -> None:
    # Subject anchoring plus order voice: a sentence recounting a past vacatur
    # in a companion proceeding is narration, not this entry's order.
    text = (
        "Petition for a writ of certiorari granted limited to Question 1 "
        "presented by the petition. Justice Alito took no part. The judgment "
        "entered below in the companion proceeding was vacated and remanded "
        "last Term."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.granted


def test_a_prose_munsingwear_reads_gvr_with_the_mootness_basis() -> None:
    # The upgrade and the basis read the same vacatur sentence, so the pair is
    # `gvr` + mootness (the procedural stratum), never a merits GVR.
    text = (
        "The petition for a writ of certiorari before judgment is granted. "
        "The judgment of the United States Court of Appeals for the Ninth "
        "Circuit is vacated, and the case is remanded with instructions to "
        "dismiss the case as moot."
    )

    matched = match_disposition_signal(text)

    assert matched is not None
    assert matched[0] is Disposition.gvr
    assert mootness_disposition(text) is True


def test_a_merits_gvr_keeps_the_standard_basis() -> None:
    # The real scotus/73275185 shape: a GVR for reconsideration, no mootness.
    text = (
        "The petition for a writ of certiorari before judgment is granted. The "
        "judgment of the United States District Court for the Northern District "
        "of Alabama is vacated, and the case is remanded to that court for "
        "further consideration in light of Louisiana v. Callais."
    )

    assert mootness_disposition(text) is False


def test_a_prose_cbj_gvr_resolves_gvr_and_opens_no_merits_proceeding() -> None:
    # The seam the fix serves: ingest's resolution reads the prose CBJ-GVR
    # entry as a gvr grant (dating date_cert_granted), and the gvr label keeps
    # the row out of the merits population — no wasted merits cell.
    entries = [
        {
            "description": "Petition for a writ of certiorari before judgment filed.",
            "date_filed": "2026-01-15",
        },
        {
            "description": (
                "The petition for a writ of certiorari before judgment is granted. "
                "The judgment of the United States District Court for the Northern "
                "District of Alabama is vacated, and the case is remanded to that "
                "court for further consideration in light of Louisiana v. Callais."
            ),
            "date_filed": "2026-05-11",
        },
    ]

    disposition, cert_granted, cert_denied, terminated = _live_resolution(entries)

    assert disposition == "gvr"
    assert cert_granted == date(2026, 5, 11)
    assert cert_denied is None and terminated is None
    row = corpus.CorpusRow(
        case_id="scotus/73275185",
        court="scotus",
        docket_number="24A1007",
        disposition=disposition,
        date_cert_granted=cert_granted,
    )
    assert corpus.opens_merits_proceeding(row) is False


def test_a_deferral_motion_grant_does_not_pre_empt_the_petitions_own_dismissal() -> None:
    # The whole seam, in docket order: the deferral order lands first, so a
    # match there wins ingest's first-entry rule and records a grant — with the
    # motion's date — on a petition that was in fact dismissed under Rule 46 a
    # month later. Suppressing the motion sentence lets the real terminal entry
    # resolve the row, and it leaves the merits population.
    entries = [
        {
            "description": "Petition for a writ of certiorari filed.",
            "date_filed": "2023-11-09",
        },
        {
            "description": (
                "Joint motion to defer consideration of the petition for a writ "
                "of certiorari GRANTED."
            ),
            "date_filed": "2024-03-18",
        },
        {"description": "Petition Dismissed - Rule 46.", "date_filed": "2024-04-22"},
    ]

    disposition, cert_granted, cert_denied, terminated = _live_resolution(entries)

    assert disposition == "dismissed"
    assert cert_granted is None and cert_denied is None
    assert terminated == date(2024, 4, 22)
    row = corpus.CorpusRow(
        case_id="scotus/72480144",
        court="scotus",
        docket_number="23-506",
        disposition=disposition,
        date_cert_granted=cert_granted,
    )
    assert corpus.opens_merits_proceeding(row) is False


# --- the noted dissent from a denial ---------------------------------------------

#: Real-shaped order-list text carrying each of the four notations. Aggregated
#: existence is all that is read: no fixture asserts *which* Justice.
_DISSENT_SHAPES = (
    "Petition DENIED. Justice Sotomayor, with whom Justice Jackson joins, "
    + "dissenting from the denial of certiorari.",
    "Petition DENIED. Justice Thomas would grant the petition for a writ of certiorari.",
    "Statement of Justice Alito respecting the denial of certiorari.",
    "Petition DENIED. JUSTICE GORSUCH, dissenting.",
    # The bare notation as the clerk usually files it — a recital ending in
    # "filed", which the disposition guard would reject and this one must not.
    "Petition DENIED. Statement of Justice Alito, dissenting, filed.",
)

#: Shapes the parser must stay silent on: a plain denial, every grant-side
#: disposition (a dissent from a GVR is not a dissent from a denial), and the
#: pending-docket near-misses the disposition table's own guards exist for.
_NOT_A_NOTED_DISSENT = (
    "Petition DENIED.",
    "Petition DENIED. Justice Barrett took no part in the consideration or "
    + "decision of this petition.",
    "DISTRIBUTED for Conference of 9/29/2025.",
    "Judgment VACATED and case REMANDED for further consideration in light of "
    + "Louisiana v. Callais. Justice Alito, dissenting.",
    "Petition for a writ of certiorari granted; statement of Justice Alito filed.",
    "The petition for a writ of certiorari before judgment is granted. The "
    + "judgment of the United States Court of Appeals for the Ninth Circuit is "
    + "vacated, and the case is remanded with instructions to dismiss the case as moot.",
    "Motion of petitioner to expedite consideration of the petition for a writ "
    + "of certiorari in the event the petition is granted filed.",
    "Brief of respondent suggesting that the judgment be vacated and the case " + "remanded filed.",
)


def test_dissent_from_denial_reads_the_four_order_list_notations() -> None:
    for text in _DISSENT_SHAPES:
        assert dissent_from_denial(text) is True, text


def test_a_motion_denial_anchors_no_bare_dissent_notation() -> None:
    # The bare notation counts only where *this entry's own order* is a denial,
    # and a denied motion about the petition is not one — so the guard that
    # suppresses the disposition takes the anchor with it, and the entry reads
    # False. That is the safe direction: naming a Justice is not itself the
    # observable, and a false positive would commit a fact to the record.
    motion_denial = (
        "Joint motion to defer consideration of the petition for a writ of "
        "certiorari DENIED. Justice Sotomayor, dissenting."
    )
    assert dissent_from_denial(motion_denial) is False
    # A self-anchored notation names the denial itself, so it still reads
    # through the same text — the suppression costs only the bare shape.
    assert (
        dissent_from_denial(
            "Joint motion to defer consideration of the petition for a writ of "
            "certiorari DENIED. Justice Sotomayor, dissenting from the denial of certiorari."
        )
        is True
    )


def test_dissent_from_denial_stays_silent_on_quiet_denials_and_grants() -> None:
    for text in _NOT_A_NOTED_DISSENT:
        assert dissent_from_denial(text) is False, text


def test_the_bare_notation_needs_its_own_entry_to_be_the_denial() -> None:
    # "Justice X, dissenting" names no denial, so alone it is as likely to be a
    # merits dissent; the three denial-worded notations do name one and read on
    # an entry of their own, as an order list files them.
    assert dissent_from_denial("Justice Gorsuch, dissenting.") is False
    assert dissent_from_denial("Justice Thomas would grant the petition.") is True


# --- the versioned distribution parse --------------------------------------------

#: The three prefixed shapes a docket carries when some paper *other than the
#: petition* goes to a conference. Each names its paper first, which is what
#: `dist-v2`'s entry-initial anchor reads and `dist-v1`'s free search does not.
_ANCILLARY_DISTRIBUTIONS = (
    "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
    "Application (23A242) DISTRIBUTED for Conference of 5/19/2026.",
    "Suggestion of mootness DISTRIBUTED for Conference of 5/19/2026.",
)

#: The petition's own distribution, which the clerk always enters entry-initial.
_OWN_DISTRIBUTION = "DISTRIBUTED for Conference of 3/24/2023."


def _payload(*descriptions: str) -> dict[str, object]:
    """A REST-shaped snapshot payload carrying one entry per description."""
    return {"docket_entries": [{"description": text} for text in descriptions]}


def _live_payload(*texts: str) -> dict[str, object]:
    """A live-shaped (supremecourt.gov) snapshot payload.

    The shape the entry-initial rule was measured on, and the one the census
    counts, so the parses are pinned against it and not only against the REST
    rendering of the same facts.
    """
    return {"ProceedingsandOrder": [{"Text": text, "Date": "08/01/2026"} for text in texts]}


def _entries(*descriptions: str) -> list[dict[str, object]]:
    """The synthesized live entry list ingest counts over."""
    return [{"description": text} for text in descriptions]


@pytest.mark.parametrize("text", _ANCILLARY_DISTRIBUTIONS)
def test_an_ancillary_papers_distribution_counts_only_under_dist_v1(text: str) -> None:
    """The prefix before DISTRIBUTED is the whole discriminator.

    Every ancillary distribution names its own paper first, so a free search
    reads it as the petition's own trajectory and the entry-initial anchor does
    not. The count feeds the salience band's primary feature, which is why the
    two readings are separately registered rather than one silently replacing
    the other.
    """
    assert snapshot_distribution_count(_payload(text), parse="dist-v1") == 1
    assert snapshot_distribution_count(_payload(text), parse="dist-v2") == 0
    # The live shape is where the rule was measured, so it is pinned directly
    # rather than only through the REST rendering of the same facts.
    assert snapshot_distribution_count(_live_payload(text), parse="dist-v1") == 1
    assert snapshot_distribution_count(_live_payload(text), parse="dist-v2") == 0
    # The corpus-side counter reads the same registry, so it cannot disagree.
    assert _live_distribution_count(_entries(text), parse="dist-v1") == 1
    assert _live_distribution_count(_entries(text), parse="dist-v2") == 0


def test_the_petitions_own_distribution_counts_under_both_parses() -> None:
    """dist-v2 narrows the reading; it must not narrow it past the signal itself."""
    for parse in DISTRIBUTION_PARSES:
        assert snapshot_distribution_count(_payload(_OWN_DISTRIBUTION), parse=parse) == 1
        assert snapshot_distribution_count(_live_payload(_OWN_DISTRIBUTION), parse=parse) == 1
        assert _live_distribution_count(_entries(_OWN_DISTRIBUTION), parse=parse) == 1


def test_dist_v2_tolerates_leading_whitespace_before_the_entry() -> None:
    """Indentation is upstream formatting, not a paper naming itself."""
    padded = f"  \n\t{_OWN_DISTRIBUTION}"
    assert snapshot_distribution_count(_payload(padded), parse="dist-v2") == 1
    assert _live_distribution_count(_entries(padded), parse="dist-v2") == 1


def test_a_mixed_docket_sheds_exactly_the_ancillary_entries() -> None:
    """The two readings differ by the prefixed entries and by nothing else."""
    docket = _payload(
        "DISTRIBUTED for Conference of 3/24/2023.",
        "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
        "DISTRIBUTED for Conference of 4/14/2023.",
    )
    assert snapshot_distribution_count(docket, parse="dist-v1") == 3
    assert snapshot_distribution_count(docket, parse="dist-v2") == 2


def test_the_conference_date_dedupe_survives_both_parses() -> None:
    """Distinct parsed conference dates, not raw matches — under either reading.

    Two spellings of one conference are one distribution, so a re-docketed
    notice never inflates the count and the parse change cannot smuggle in a
    different dedupe rule alongside it.
    """
    respelled = _payload(
        "DISTRIBUTED for Conference of 3/24/2023.",
        "DISTRIBUTED for Conference of March 24, 2023.",
    )
    for parse in DISTRIBUTION_PARSES:
        assert snapshot_distribution_count(respelled, parse=parse) == 1
        assert (
            _live_distribution_count(
                _entries(
                    "DISTRIBUTED for Conference of 3/24/2023.",
                    "DISTRIBUTED for Conference of March 24, 2023.",
                ),
                parse=parse,
            )
            == 1
        )


def test_an_unregistered_parse_raises_rather_than_falling_back() -> None:
    """A count produced by a reading the caller did not name is worse than an error."""
    with pytest.raises(KeyError):
        snapshot_distribution_count(_payload(_OWN_DISTRIBUTION), parse="dist-v0")
    with pytest.raises(KeyError):
        _live_distribution_count(_entries(_OWN_DISTRIBUTION), parse="dist-v0")


def test_a_payload_with_no_proceedings_is_unobservable_under_every_parse() -> None:
    """Absence of a proceedings list is unknown, never zero — whichever reading asks."""
    for parse in DISTRIBUTION_PARSES:
        assert snapshot_distribution_count({}, parse=parse) is None
