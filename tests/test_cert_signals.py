"""The cert-disposition resolver's pattern behavior, pinned on real order-list text.

A resolver match records ground truth (disposition + decision date), so a false
positive fabricates an outcome while a miss merely leaves a decided docket to
the routing backstop — the negative space matters as much as the positive.
Match fixtures are the entry shapes decided SCOTUS dockets actually carry;
no-match fixtures are the pending-shaped near-misses a broadened pattern must
never read as a disposition.
"""

from fedcourtsai.pipeline.cert_signals import match_disposition_signal
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
    assert disposition == Disposition.granted
    assert label == "GVR"
    assert "VACATED" in snippet


def test_comma_form_vacate_and_remand_reads_as_a_gvr() -> None:
    matched = match_disposition_signal(
        "Judgment VACATED, and case REMANDED for further consideration in "
        "light of Louisiana v. Callais."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_prose_form_naming_the_lower_court_reads_as_a_gvr() -> None:
    # The order-list prose names the lower court between "judgment" and
    # "vacated"; the first gap is sized for it.
    matched = match_disposition_signal(
        "The judgment of the United States Court of Appeals for the Armed "
        "Forces is vacated, and the case is remanded for further consideration."
    )
    assert matched is not None and matched[0] == Disposition.granted and matched[1] == "GVR"


def test_cert_before_judgment_grant_with_vacatur_reads_as_granted() -> None:
    # A granted cert-before-judgment GVR carries the grant recital, so the
    # grant-anchored GVR row reads it; the bare-CBJ forms without a vacatur
    # are deliberate misses (see the no-match section).
    matched = match_disposition_signal(
        "Petition for writ of certiorari before judgment GRANTED. Judgment "
        "VACATED and case REMANDED."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_existing_shapes_still_read() -> None:
    # The pre-existing rows are untouched: the classic order-list forms.
    for text, expected in (
        ("Petition DENIED.", Disposition.denied),
        ("Petition GRANTED limited to Question 1.", Disposition.granted),
        ("Petition DISMISSED under Rule 46.", Disposition.dismissed),
        ("The petition was GVR'd in light of Ramirez.", Disposition.granted),
        (
            "Petition GRANTED. Judgment VACATED and case REMANDED for further consideration.",
            Disposition.granted,
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
        "petition for a writ of certiorari before judgment granted.",
        "Motion of petitioners to expedite consideration of the petition "
        "for a writ of certiorari before judgment denied.",
        "Motion of petitioner to expedite consideration of the petition "
        "for a writ of certiorari granted.",
        "Motion of respondent to expedite consideration of the petition "
        "for a writ of certiorari denied.",
    ):
        assert match_disposition_signal(text) is None, text


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


def test_ifp_grant_plus_cert_grant_compound_still_reads() -> None:
    matched = match_disposition_signal(
        "Motion to proceed in forma pauperis and petition for a writ of "
        "certiorari GRANTED. Judgment VACATED and case REMANDED for further "
        "consideration in light of Hewitt v. United States."
    )
    assert matched is not None and matched[0] == Disposition.granted


def test_party_papers_reciting_a_vacatur_are_not_a_disposition() -> None:
    # A brief or letter *describing* a vacatur decides nothing; the
    # entry-start anchor on the judgment-vacated row rejects them.
    for text in (
        "Brief of respondent suggesting that the judgment be vacated and the case remanded filed.",
        "Letter of respondent advising that the judgment below was vacated "
        "and the case remanded by the Court of Appeals filed.",
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


def test_bare_cert_before_judgment_disposition_is_a_deliberate_miss() -> None:
    # A CBJ disposition *without* a vacatur ("... before judgment DENIED.")
    # stays unmatched by design: accepting the multi-word gap would also
    # accept the expedite-motion recital above. The miss is cheap — the
    # routing backstop's anchored CBJ-denial shape (termination_signal) parks
    # the quiet decided docket for maintainer triage instead of recording.
    assert (
        match_disposition_signal("Petition for writ of certiorari before judgment DENIED.") is None
    )


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
        "petition for a writ of certiorari granted.",
        "Motion of petitioner to vacate the stay in the event the petition "
        "is granted in No. 25-332 filed.",
    ):
        assert match_disposition_signal(text) is None, text


def test_semicolon_scopes_a_trailing_filed_clause() -> None:
    # The genuine order before a semicolon-joined "...filed" notation must
    # keep reading — only the trailing clause is a recital.
    matched = match_disposition_signal(
        "Petition for a writ of certiorari granted; statement of Justice Alito filed."
    )
    assert matched is not None and matched[0] == Disposition.granted
