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
    # as the *motion's object*, with the motion's verb right after — and it
    # appears earlier in docket order than the petition's own disposition, so
    # a match here would stamp the wrong outcome with the wrong date. Both
    # polarities must stay unmatched.
    for text in (
        "Motion of the Special Counsel to expedite consideration of the "
        "petition for a writ of certiorari before judgment granted.",
        "Motion of petitioners to expedite consideration of the petition "
        "for a writ of certiorari before judgment denied.",
    ):
        assert match_disposition_signal(text) is None, text


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
    # routing backstop parks the decided docket for triage.
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
