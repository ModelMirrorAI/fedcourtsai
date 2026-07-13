from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.ingest import from_api_docket
from fedcourtsai.pipeline.outcome import (
    appears_decided,
    detect_resolution,
    disposition_basis,
    granted_flag,
    is_machine_readable,
    record_outcomes,
    resolve_case,
    termination_signal,
)
from fedcourtsai.schemas import Disposition, EventKind, Outcome, PredictableEvent
from fedcourtsai.serialize import read_model

DECIDED_DOCKET = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "date_terminated": "2022-06-15",
    "disposition": "Petition denied",
    "citations": ["12 F.4th 100"],
}


def _db(tmp_path: Path) -> Path:
    return corpus.corpus_db_path(tmp_path / "corpus")


def _open_event(tmp_path: Path, event_id: str = "evt-petition-review") -> None:
    """Record an open predictable event in the corpus for the canned docket."""
    event = corpus.CorpusEvent(
        event_id=event_id,
        case_id="ca9/64512345",
        court="ca9",
        kind=EventKind.petition,
        title="Petition for review",
    )
    with corpus.connect(_db(tmp_path)) as conn:
        corpus.upsert_events(conn, [event])


# --- pure helpers --------------------------------------------------------------


def test_granted_flag_maps_partial_grant_to_granted() -> None:
    assert granted_flag(Disposition.granted) == 1
    assert granted_flag(Disposition.granted_in_part) == 1
    assert granted_flag(Disposition.denied) == 0
    assert granted_flag(Disposition.dismissed) == 0


def test_is_machine_readable_rejects_none_and_other() -> None:
    assert is_machine_readable(Disposition.denied) is True
    assert is_machine_readable(None) is False
    assert is_machine_readable(Disposition.other) is False


def test_appears_decided() -> None:
    assert appears_decided(from_api_docket(DECIDED_DOCKET)) is True
    pending = from_api_docket({"id": 1, "court_id": "ca9", "date_filed": "2024-01-01"})
    assert appears_decided(pending) is False
    # A SCOTUS docket whose only decided signal is the petition-stage cert date.
    cert_dated = from_api_docket({"id": 2, "court_id": "scotus", "date_cert_denied": "2023-01-09"})
    assert appears_decided(cert_dated) is True


# --- detection -----------------------------------------------------------------


def test_single_open_event_resolves_deterministically() -> None:
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.unrecorded
    outcome = resolution.outcomes["evt-petition-review"]
    assert outcome.actual_disposition == Disposition.denied
    assert outcome.actual_granted == 0
    assert outcome.resolved_at == date(2022, 6, 15)
    assert outcome.source == "12 F.4th 100"


def test_cert_dated_petition_resolves_at_the_petition_stage() -> None:
    # A fresh SCOTUS docket typically carries the petition decision only as a
    # cert-stage date: no disposition string, and for a granted petition no
    # termination until the merits judgment. The derived disposition plus the
    # petition-stage resolution date make it deterministic, stamped at the grant.
    row = from_api_docket(
        {
            "id": 22451,
            "court_id": "scotus",
            "docket_number": "22-451",
            "date_cert_granted": "2022-10-03",
            "date_terminated": "2023-06-30",
        }
    )
    resolution = detect_resolution(row, "scotus", 22451, ["evt-petition-disposition"])
    assert not resolution.unrecorded
    outcome = resolution.outcomes["evt-petition-disposition"]
    assert outcome.actual_disposition == Disposition.granted
    assert outcome.actual_granted == 1
    assert outcome.resolved_at == date(2022, 10, 3)


def test_undecided_docket_is_a_noop() -> None:
    row = from_api_docket({"id": 7, "court_id": "ca9", "date_filed": "2024-01-01"})
    resolution = detect_resolution(row, "ca9", 7, ["evt-petition-review"])
    assert not resolution.outcomes
    assert not resolution.unrecorded


def test_no_open_events_is_a_noop() -> None:
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, [])
    assert not resolution.outcomes
    assert not resolution.unrecorded


def test_unreadable_disposition_lands_unrecorded() -> None:
    # "affirmed" normalizes to the `other` catch-all — decided, but not how.
    row = from_api_docket({**DECIDED_DOCKET, "disposition": "affirmed"})
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.outcomes
    (req,) = resolution.unrecorded
    assert req.event_id == "evt-petition-review"
    assert "not machine-readable" in req.reason


def test_decided_without_date_lands_unrecorded() -> None:
    row = from_api_docket({"id": 64512345, "court_id": "ca9", "disposition": "Petition denied"})
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.outcomes
    (req,) = resolution.unrecorded
    assert "no decision date" in req.reason


def test_multiple_open_events_land_unrecorded() -> None:
    # One case-level disposition cannot be attributed across several open events.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-motion-a", "evt-motion-b"])
    assert not resolution.outcomes
    assert {r.event_id for r in resolution.unrecorded} == {"evt-motion-a", "evt-motion-b"}
    assert all("cannot be attributed" in r.reason for r in resolution.unrecorded)


# --- ledger write --------------------------------------------------------------


def test_record_outcomes_writes_outcome_and_marks_resolved(tmp_path: Path) -> None:
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    written = record_outcomes(_db(tmp_path), tmp_path, "ca9", 64512345, resolution)
    assert written == ["evt-petition-review"]

    event_paths = CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review")
    written_outcome = read_model(event_paths.outcome, Outcome)
    assert written_outcome.actual_disposition == Disposition.denied
    # The event.yaml is materialized beside the outcome (resolved), so the
    # deterministic writers' straight-to-main commits never leave a referential
    # orphan for the offline validate gate to reject.
    materialized = read_model(event_paths.event_file, PredictableEvent)
    assert materialized.event_id == "evt-petition-review"
    assert materialized.resolved is True
    # The corpus event is flipped resolved so it stays consistent with its outcome.
    with corpus.connect(_db(tmp_path)) as conn:
        (event,) = corpus.events_for_case(conn, "ca9/64512345")
    assert event.resolved is True


def test_resolve_case_end_to_end(tmp_path: Path) -> None:
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    assert "evt-petition-review" in resolution.outcomes
    assert CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review").outcome.exists()


def test_resolve_case_is_idempotent(tmp_path: Path) -> None:
    # A second refresh sees the event closed (corpus resolved flag) and does nothing.
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    again = resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    assert not again.outcomes
    assert not again.unrecorded


def test_record_outcomes_refuses_an_orphaned_outcome(tmp_path: Path) -> None:
    # A resolution for an event the corpus does not hold is an internal
    # inconsistency: fail before writing, never commit an outcome the offline
    # validate gate would reject as a referential orphan.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    with pytest.raises(RuntimeError, match="orphaned outcome"):
        record_outcomes(_db(tmp_path), tmp_path, "ca9", 64512345, resolution)
    assert not CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review").outcome.exists()


def test_termination_signal_reads_the_clerks_termination_entry() -> None:
    # A stale CA docket often carries no date_terminated/disposition, yet its
    # latest entry states the matter is over — the signal appears_decided
    # cannot see.
    docket = {
        "id": 1,
        "docket_entries": [
            {"id": 10, "description": "Briefing complete"},
            {"id": 11, "description": "Case termination for order and judgment"},
        ],
    }
    signal = termination_signal(docket)
    assert signal is not None and "Case termination" in signal


def test_termination_signal_reads_the_opinion_issued_entry() -> None:
    docket = {"id": 1, "docket_entries": [{"id": 10, "short_description": "Opinion Issued."}]}
    signal = termination_signal(docket)
    assert signal is not None and "Opinion Issued" in signal


def test_termination_signal_only_reads_the_latest_entry() -> None:
    # Pendency is event-level: a filing *after* a terminal entry (a
    # stay-the-mandate motion, a rehearing petition) reopens the docket, so
    # the earlier terminal entry must not starve the later event.
    docket = {
        "id": 1,
        "docket_entries": [
            {"id": 10, "description": "Opinion Issued."},
            {"id": 11, "description": "Motion to stay the mandate"},
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_a_cluster_link_alone() -> None:
    # A linked opinion cluster alone is deliberately not a signal: a
    # motions-panel opinion can publish on a still-pending appeal.
    docket = {
        "id": 1,
        "docket_entries": [{"id": 10, "description": "Filed"}],
        "clusters": ["https://www.courtlistener.com/api/rest/v4/clusters/10122744/"],
    }
    assert termination_signal(docket) is None


def test_termination_signal_none_for_a_pending_docket() -> None:
    # Routine entries — including ones that merely *mention* an opinion — read
    # as pending; only the anchored terminal phrasings match.
    docket = {
        "id": 1,
        "docket_entries": [
            {"id": 10, "description": "Motion to stay pending appeal"},
            {"id": 11, "description": "Citing the opinion issued in a related case"},
        ],
        "clusters": [],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_rule_398_ifp_dismissal() -> None:
    # A Rule 39.8 IFP-denial/dismissal the cert-disposition resolver does not
    # match (the noun and verb are many words apart); the routing backstop does.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion for leave to proceed in forma pauperis DENIED and petition "
                    "for a writ of habeas corpus DISMISSED. See Rule 39.8."
                ),
            }
        ],
    }
    signal = termination_signal(docket)
    assert signal is not None and "39.8" in signal


def test_termination_signal_reads_a_bare_rule_398_filing_bar() -> None:
    # An abusive-filer Rule 39.8 bar with no "petition ... dismissed" verb: only
    # the rule-39.8 alternation can catch it, so this pins that branch specifically.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion for leave to proceed in forma pauperis DENIED. See Rule 39.8."
                ),
            }
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_reads_a_fee_default_closure() -> None:
    docket = {"id": 1, "docket_entries": [{"id": 10, "description": "Case considered closed."}]}
    assert termination_signal(docket) is not None


def test_termination_signal_ignores_an_ifp_denial_with_a_fee_deadline() -> None:
    # The initial IFP denial that only sets a payment deadline is NOT terminal:
    # the petition may still proceed on payment, so it must stay predictable —
    # the later closure/dismissal entry, not this denial, is the terminal signal.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion for leave to proceed in forma pauperis is denied. Petitioner "
                    "allowed until Nov 12 2025, to pay the docketing fee. Rule 33.1."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_gvr_vacate_and_remand_order() -> None:
    # The GVR shape the cert-disposition resolver's grant-anchored patterns
    # miss: a bare vacate-and-remand order carries no "grant" word and no
    # literal "GVR" token, yet the matter is decided. This is the exact entry
    # that leaked already-decided SCOTUS dockets into forward cells.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Judgment VACATED and case REMANDED for further consideration "
                    "in light of Louisiana v. Callais."
                ),
            }
        ],
    }
    signal = termination_signal(docket)
    assert signal is not None and "VACATED" in signal


def test_termination_signal_reads_the_judgment_issued_entry() -> None:
    # "Judgment Issued" is the SCOTUS mandate analog — it follows the
    # disposition order, so it is often the *latest* entry and the only
    # terminal-shaped text the latest-entry rule can see.
    docket = {"id": 1, "docket_entries": [{"id": 10, "description": "Judgment Issued."}]}
    assert termination_signal(docket) is not None


def test_termination_signal_ignores_a_vacatur_without_a_remand() -> None:
    # An interim vacatur (a stay vacated, an order vacated on rehearing) does
    # not end the matter; only the vacate-and-remand pair reads terminal.
    docket = {
        "id": 1,
        "docket_entries": [{"id": 10, "description": "Order vacating the stay entered."}],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_a_vacate_and_remand_motion() -> None:
    # The SG's confession-of-error *motion* asks for a vacate-and-remand but
    # decides nothing — the verb precedes "judgment", which the disposition
    # noun-verb shape ("judgment ... vacated ... remand") does not match.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion of respondent to vacate the judgment and remand the case "
                    "for further proceedings filed."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_an_en_banc_panel_opinion_vacatur() -> None:
    # Rehearing en banc vacates the *panel opinion* and remands to the panel —
    # the appeal is very much alive, and no "judgment" anchors the pair.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Rehearing en banc GRANTED. The panel opinion is VACATED and "
                    "the case is REMANDED to the panel."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_a_judgment_issued_recital() -> None:
    # A docketing recital that merely *mentions* an issued judgment ("NOTICE OF
    # APPEAL filed from the judgment issued on ...") opens a matter rather than
    # closing one; only the start-anchored bare "Judgment Issued" entry counts.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "NOTICE OF APPEAL filed from the judgment issued on 03/04/2026 "
                    "by the district court."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_cert_before_judgment_denial() -> None:
    # The CBJ denial is a deliberate resolver miss (its multi-word noun-verb
    # gap would also admit the expedite-motion recital), so routing is its
    # only net — the denied-CBJ docket goes quiet with this as its latest entry.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": "Petition for a writ of certiorari before judgment denied.",
            }
        ],
    }
    assert termination_signal(docket) is not None
    # The consolidated-docket plural form terminates the same way.
    plural = {
        "id": 2,
        "docket_entries": [
            {
                "id": 10,
                "description": "Petitions for writs of certiorari before judgment denied.",
            }
        ],
    }
    assert termination_signal(plural) is not None


def test_termination_signal_ignores_a_cbj_expedite_motion_order() -> None:
    # The order on an expedite motion recites the same noun phrase but opens
    # with "Motion ..." — a pending CBJ docket must never be parked out of the
    # forward queue by its own scheduling order.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion of petitioners to expedite consideration of the "
                    "petition for a writ of certiorari before judgment denied."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_circuit_vacate_and_remand_disposition() -> None:
    # The CA disposition shape carries the same judgment-vacated-remand
    # noun-verb order as the SCOTUS GVR, so the one pattern covers both.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "OPINION filed. The judgment of the district court is VACATED "
                    "and the case is REMANDED for further proceedings."
                ),
            }
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_reads_the_raw_live_payload_shape() -> None:
    # The live channel stores the supremecourt.gov JSON verbatim as the
    # point-in-time snapshot: proceedings ride under ProceedingsandOrder/Text,
    # not docket_entries/description. The signal must read both shapes.
    docket = {
        "CaseNumber": "25-274 ",
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "May 11 2026", "Text": "Judgment Issued."},
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_latest_entry_rule_holds_on_the_live_shape() -> None:
    # Same pendency semantics on the raw shape: an administrative notation
    # after the terminal entry is the latest described entry, so the
    # latest-entry rule reads the docket as active — provisioning's
    # whole-snapshot disposition scan, not this signal, covers that tail.
    docket = {
        "CaseNumber": "25-274 ",
        "ProceedingsandOrder": [
            {"Date": "May 11 2026", "Text": "Judgment Issued."},
            {"Date": "May 11 2026", "Text": "Application (25A1231) denied as moot."},
        ],
    }
    assert termination_signal(docket) is None


def test_disposition_basis_reads_the_payload_and_threads_into_the_outcome() -> None:
    munsingwear = {
        "CaseNumber": "25-100 ",
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {
                "Date": "May 11 2026",
                "Text": (
                    "Judgment VACATED and case REMANDED with instructions to "
                    "dismiss the case as moot."
                ),
            },
        ],
    }
    assert disposition_basis(munsingwear) == "mootness"
    plain = {
        "id": 1,
        "docket_entries": [{"id": 10, "description": "Petition DENIED."}],
    }
    assert disposition_basis(plain) == "standard"
    assert disposition_basis({"id": 2, "docket_entries": []}) == "standard"

    # The basis lands on the written ground truth.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row, "ca9", 64512345, ["evt-petition-review"], disposition_basis="mootness"
    )
    assert resolution.outcomes["evt-petition-review"].disposition_basis == "mootness"
    # And defaults to standard when the channel passes nothing.
    default = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert default.outcomes["evt-petition-review"].disposition_basis == "standard"
