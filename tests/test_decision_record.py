"""The merits decision record: the argued date and how a granted case was decided.

Entry texts are verbatim live-docket spellings (supremecourt.gov wraps the
opinion in a link, which the readers drop), so a test failing here reads as the
docket shape it broke on.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.decision_record import (
    backfill_decision_record,
    decision_census,
    decision_date,
    decision_judgment,
    decision_method,
    decision_term,
    read_decision_record,
)
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row
from fedcourtsai.pipeline.judgment import (
    JudgmentEntry,
    opinion_author,
    per_curiam_opinion,
    signed_opinion,
)
from fedcourtsai.pipeline.merits_signals import argued_date, is_argument_entry
from fedcourtsai.schemas import Judgment, MeritsDecisionMethod

runner = CliRunner()

_LINK = "<a href = 'https://www.supremecourt.gov/opinions/25pdf/24-482_1a2b.pdf'>opinion</a>"
_PC_LINK = "<a href = 'https://www.supremecourt.gov/opinions/25pdf/25-297_bqm2.pdf'>Opinion</a>"

_SIGNED = (
    "Judgment REVERSED and case REMANDED. Gorsuch, J., delivered the "
    + _LINK
    + " of the Court, in which Roberts, C. J., and Thomas, Alito, JJ., joined. "
    + "Sotomayor, J., filed a dissenting opinion."
)
_UNANIMOUS = (
    "Judgment REVERSED and case REMANDED. Kavanaugh, J., delivered the opinion for a "
    + "unanimous Court. Thomas, J., filed a concurring opinion, in which Gorsuch, J., joined."
)
_FRACTURED = (
    "Adjudged to be AFFIRMED. Roberts, C. J., announced the judgment of the Court and "
    + "delivered the opinion of the Court with respect to Parts I and II-B."
)
_SUMMARY_REVERSAL = (
    "Petition GRANTED. Judgment REVERSED. "
    + _PC_LINK
    + " per curiam. (Detached "
    + _PC_LINK
    + ") Justice Sotomayor, with whom Justice Kagan joins, dissenting."
)
_GRR = (
    "Petition GRANTED. Judgment REVERSED and case REMANDED for further proceedings "
    + "consistent with the "
    + _LINK
    + " of the Court. "
    + _PC_LINK
    + " per curiam. Justice Jackson would deny the petition for a writ of certiorari."
)
# An ordinary GVR cites another case's per curiam: that says nothing about this one.
_GVR_CITING_A_PER_CURIAM = (
    "Petition GRANTED. Judgment VACATED and case REMANDED for further consideration in "
    + "light of <i>Clark</i> v. <i>Sweeney</i>, 607 U. S. 7 (2025) (<i>per curiam</i>)."
)
_DIG = "Writ of certiorari DISMISSED as improvidently granted. " + _PC_LINK + " per curiam."
_EQUALLY_DIVIDED = (
    "Adjudged to be AFFIRMED by an equally divided Court. Justice Barrett took no part "
    + "in the consideration or decision of these cases. "
    + _PC_LINK
    + " per curiam. VIDED."
)
_ARGUED_PER_CURIAM = (
    "Judgment REVERSED. The mandate shall issue forthwith. "
    + _PC_LINK
    + " per curiam. Barrett, J., filed an opinion concurring in part."
)


def _live(*entries: tuple[str, str], number: str = "24-482 ") -> dict[str, Any]:
    return {
        "CaseNumber": number,
        "DocketedDate": "Dec 10, 2024",
        "LowerCourt": "United States Court of Appeals for the Eighth Circuit",
        "ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries],
    }


# --- the argued date --------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "argued"),
    [
        ("Argued. For petitioner: Adam G. Unikowsky, Washington, D. C.", True),
        ("Reargued. For appellants: Janai S. Nelson, New York, N. Y.", True),
        ("Argued. Argued. For New Jersey Transit Corporation, et al.: Michael", True),
        ("SET FOR ARGUMENT on Monday, October 6, 2025.", False),
        (
            "Roman Martinez, Esquire, of Washington, D. C., is invited to brief and argue "
            + "this case, as amicus curiae, in support of the judgment below.",
            False,
        ),
        ("Motion for divided argument filed by the Solicitor General.", False),
        ("CIRCULATED", False),
    ],
)
def test_the_argument_entry_is_start_anchored_on_its_verb(text: str, argued: bool) -> None:
    assert is_argument_entry(text) is argued


def test_the_last_argument_after_the_grant_dates_the_case() -> None:
    """A reargued case is decided on the reargument, so the later date wins."""
    payload = _live(
        ("Nov 04 2024", "Petition GRANTED."),
        ("Mar 24 2025", "Argued. For appellants: X."),
        ("Jun 27 2025", "Case restored to the calendar for reargument."),
        ("Oct 15 2025", "Reargued. For appellants: X."),
    )
    assert argued_date(payload, granted_on=date(2024, 11, 4)) == date(2025, 10, 15)


def test_no_grant_means_no_argued_date_and_an_undated_entry_is_skipped() -> None:
    payload = _live(("", "Argued. For petitioner: X."), ("Apr 22 2025", "Argued."))
    assert argued_date(payload, granted_on=None) is None
    assert argued_date(payload, granted_on=date(2025, 1, 10)) == date(2025, 4, 22)
    assert argued_date(_live(("", "Argued.")), granted_on=date(2025, 1, 10)) is None


# --- the opinion form -------------------------------------------------------------


def test_the_signed_and_per_curiam_readers_see_through_the_live_link() -> None:
    assert signed_opinion(_SIGNED)
    assert signed_opinion(_UNANIMOUS)
    assert signed_opinion(_FRACTURED)
    assert not signed_opinion(_SUMMARY_REVERSAL)
    assert not signed_opinion(_ARGUED_PER_CURIAM)  # a concurrence is not the Court's opinion
    assert per_curiam_opinion(_SUMMARY_REVERSAL)
    assert per_curiam_opinion(_GRR)
    assert not per_curiam_opinion(_GVR_CITING_A_PER_CURIAM)
    assert not per_curiam_opinion(_SIGNED)


def test_opinion_author_reads_the_linked_spelling() -> None:
    assert opinion_author(_SIGNED) == "Gorsuch"


# --- the method -------------------------------------------------------------------

_GRANT = date(2025, 4, 7)
_ARGUED = date(2025, 10, 14)
_DECIDED = date(2026, 1, 20)


def _entry(judgment: Judgment, decided: date | None, text: str) -> JudgmentEntry:
    return JudgmentEntry(judgment, decided, text)


@pytest.mark.parametrize(
    ("disposition", "argued", "entry", "method"),
    [
        (
            "granted",
            _ARGUED,
            _entry(Judgment.reversed, _DECIDED, _SIGNED),
            MeritsDecisionMethod.argued_signed,
        ),
        (
            "granted",
            _ARGUED,
            _entry(Judgment.reversed, _DECIDED, _UNANIMOUS),
            MeritsDecisionMethod.argued_signed,
        ),
        (
            "granted",
            _ARGUED,
            _entry(Judgment.reversed, _DECIDED, _ARGUED_PER_CURIAM),
            MeritsDecisionMethod.argued_per_curiam,
        ),
        (
            "granted",
            _ARGUED,
            _entry(
                Judgment.equally_divided,
                _DECIDED,
                "Adjudged to be AFFIRMED by an equally divided Court.",
            ),
            MeritsDecisionMethod.argued_per_curiam,
        ),
        (
            "granted",
            _ARGUED,
            _entry(Judgment.dig, _DECIDED, _DIG),
            MeritsDecisionMethod.dig,
        ),
        (
            "granted",
            None,
            _entry(Judgment.dig, _DECIDED, _DIG),
            MeritsDecisionMethod.dig,
        ),
        # A summary reversal recorded as plain `granted`: the judgment rides the grant.
        (
            "granted",
            None,
            _entry(Judgment.reversed, _GRANT, _SUMMARY_REVERSAL),
            MeritsDecisionMethod.summary_opinion,
        ),
        (
            "granted",
            None,
            _entry(Judgment.reversed, _GRANT, _GRR),
            MeritsDecisionMethod.summary_opinion,
        ),
        (
            "gvr",
            None,
            _entry(Judgment.vacated, _GRANT, _GVR_CITING_A_PER_CURIAM),
            MeritsDecisionMethod.summary_order,
        ),
        (
            "summary-reversal",
            None,
            _entry(Judgment.reversed, _GRANT, _SUMMARY_REVERSAL),
            MeritsDecisionMethod.summary_opinion,
        ),
        # Argued, but the entry recites no opinion form: left unclassified.
        ("granted", _ARGUED, _entry(Judgment.affirmed, _DECIDED, "Adjudged to be AFFIRMED."), None),
        # Decided after the grant without argument, with no opinion: unclassified.
        ("granted", None, _entry(Judgment.affirmed, _DECIDED, "Adjudged to be AFFIRMED."), None),
        ("granted", _ARGUED, None, None),
    ],
)
def test_decision_method(
    disposition: str,
    argued: date | None,
    entry: JudgmentEntry | None,
    method: MeritsDecisionMethod | None,
) -> None:
    assert (
        decision_method(disposition=disposition, granted_on=_GRANT, argued=argued, entry=entry)
        is method
    )


def test_no_grant_reads_no_method() -> None:
    entry = _entry(Judgment.reversed, _DECIDED, _SIGNED)
    assert decision_method(disposition=None, granted_on=None, argued=_ARGUED, entry=entry) is None


def test_read_decision_record_over_a_live_payload() -> None:
    payload = _live(
        ("Apr 07 2025", "Petition GRANTED."),
        ("Oct 14 2025", "Argued. For petitioner: X. For respondent: Y."),
        ("Jan 20 2026", _UNANIMOUS),
        ("Feb 23 2026", "Judgment Issued."),
    )
    record = read_decision_record(payload, disposition="granted", granted_on=_GRANT)
    assert record.argued == _ARGUED
    assert record.method is MeritsDecisionMethod.argued_signed
    assert read_decision_record(payload, disposition="granted", granted_on=None).argued is None


# --- the live channel -------------------------------------------------------------


def test_the_live_channel_latches_the_decision_record_on_a_granted_docket() -> None:
    payload = _live(
        ("Dec 10 2024", "Petition for a writ of certiorari filed."),
        ("Apr 07 2025", "Petition GRANTED."),
        ("Oct 14 2025", "Argued. For petitioner: X. For respondent: Y."),
        ("Jan 20 2026", _UNANIMOUS),
    )
    record = map_live_docket(payload, 9_500_024_482)
    assert record["merits_argued"] == "2025-10-14"
    assert record["merits_decision_method"] == "argued-signed"
    stored = to_corpus_row(from_live_record(record))
    assert stored.merits_argued == _ARGUED
    assert stored.merits_decision_method == "argued-signed"


def test_the_live_channel_classifies_a_gvr_the_merits_pair_never_reaches() -> None:
    payload = _live(
        ("Dec 10 2024", "Petition for a writ of certiorari filed."),
        ("Jun 08 2026", _GVR_CITING_A_PER_CURIAM),
    )
    record = map_live_docket(payload, 9_500_024_482)
    assert record["disposition"] == "gvr"
    assert record["merits_judgment"] is None  # the merits pair's population excludes a GVR
    assert record["merits_decision_method"] == "summary-order"


def test_an_ungranted_docket_carries_no_decision_record() -> None:
    record = map_live_docket(_live(("Dec 10 2024", "Petition for a writ of certiorari filed.")), 1)
    assert record["merits_argued"] is None
    assert record["merits_decision_method"] is None


# --- storage ----------------------------------------------------------------------


def _row(**fields: Any) -> corpus.CorpusRow:
    base: dict[str, Any] = {
        "case_id": "scotus/900482",
        "court": "scotus",
        "docket_number": "24-482",
        "last_live_polled": date(2026, 2, 1),
        "disposition": "granted",
        "date_cert_granted": _GRANT,
    }
    return corpus.CorpusRow.model_validate({**base, **fields})


@contextmanager
def _seeded(
    tmp_path: Path,
    rows: list[corpus.CorpusRow],
    snapshots: dict[str, dict[str, Any]] | None = None,
) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        for case_id, payload in (snapshots or {}).items():
            corpus.upsert_snapshot(conn, case_id, date(2026, 2, 1), payload)
        conn.commit()
        yield conn


def _stored(tmp_path: Path, case_id: str = "scotus/900482") -> corpus.CorpusRow:
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        row = corpus.get_row(conn, case_id)
    assert row is not None
    return row


def test_the_upsert_fills_in_and_never_clears(tmp_path: Path) -> None:
    """A writer with no reading keeps the stored one; a fresh reading takes over."""
    with _seeded(tmp_path, [_row(merits_argued=date(2025, 3, 24))]) as conn:
        corpus.upsert_rows(conn, [_row()])  # e.g. a REST enrichment, which reads nothing
        assert corpus.get_row(conn, "scotus/900482").merits_argued == date(2025, 3, 24)  # type: ignore[union-attr]
        corpus.upsert_rows(
            conn,
            [_row(merits_argued=date(2025, 10, 15), merits_decision_method="argued-signed")],
        )
        stored = corpus.get_row(conn, "scotus/900482")
    assert stored is not None
    assert stored.merits_argued == date(2025, 10, 15)  # the reargument replaced it
    assert stored.merits_decision_method == "argued-signed"


def test_the_decision_record_never_reaches_the_retrieval_surface() -> None:
    """The query rows a cell retrieves are exactly what they were before the columns."""
    row = _row(merits_argued=_ARGUED, merits_decision_method="argued-signed")
    withheld = {"merits_argued", "merits_decision_method"}
    assert withheld == corpus.RETRIEVAL_WITHHELD_COLUMNS
    every_other = set(corpus.CorpusRow.model_fields) - withheld
    assert set(corpus.prior_payload(row, full=True)) == every_other | {"era"}
    assert set(corpus.prior_payload(row)) == (every_other - {"opinion_text"}) | {"era"}


def test_a_legacy_blob_gains_the_columns_on_connect(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_row()]) as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(cases)")}
    assert {"merits_argued", "merits_decision_method"} <= cols


def test_from_record_tolerates_a_blob_without_the_columns() -> None:
    record = corpus._to_record(_row())
    del record["merits_argued"]
    del record["merits_decision_method"]
    assert corpus._from_record(record) == _row()


# --- the projections --------------------------------------------------------------


def test_the_disposition_is_one_judgment_vocabulary() -> None:
    assert decision_judgment(_row(merits_judgment="affirmed")) is Judgment.affirmed
    assert decision_judgment(_row(disposition="gvr")) is Judgment.vacated
    assert decision_judgment(_row(disposition="summary-reversal")) is Judgment.reversed
    assert decision_judgment(_row()) is None
    assert decision_judgment(_row(merits_judgment="not-a-judgment")) is None


def test_the_term_is_the_argument_term_not_the_docket_prefix() -> None:
    """A January grant on a 25- docket is argued in April and decided in OT2025's
    June — and a 24- docket granted in June is argued in October of OT2025 too."""
    late = _row(
        docket_number="25-466",
        date_cert_granted=date(2026, 1, 9),
        merits_argued=date(2026, 4, 20),
        merits_judgment="affirmed",
        merits_decided=date(2026, 6, 4),
    )
    assert decision_term(late) == 2025
    summary = _row(disposition="gvr", date_cert_granted=date(2025, 11, 24))
    assert decision_date(summary) == date(2025, 11, 24)
    assert decision_term(summary) == 2025
    assert decision_term(_row()) is None  # granted, not argued, not decided: pending


# --- the back-fill ----------------------------------------------------------------


def _decided_payload() -> dict[str, Any]:
    return _live(
        ("Apr 07 2025", "Petition GRANTED."),
        ("Oct 14 2025", "Argued. For petitioner: X."),
        ("Jan 20 2026", _SIGNED),
    )


def test_the_backfill_dry_runs_then_fills_once(tmp_path: Path) -> None:
    rows = [
        _row(merits_judgment="reversed", merits_decided=_DECIDED),
        _row(case_id="scotus/900483", docket_number="24-483"),  # no snapshot
        _row(case_id="scotus/900484", docket_number="24-484", merits_terminated="abated"),
        _row(case_id="scotus/900485", docket_number="24-485", disposition="denied"),
    ]
    with _seeded(tmp_path, rows, {"scotus/900482": _decided_payload()}) as conn:
        dry = backfill_decision_record(conn, apply=False)
        assert dry.candidates == 2  # the terminated and the denied rows are not selected
        assert dry.no_snapshot == 1
        assert [(f.case_id, f.argued, f.method) for f in dry.filled] == [
            ("scotus/900482", _ARGUED, MeritsDecisionMethod.argued_signed)
        ]
        assert dry.methods == {"argued-signed": 1}
        assert corpus.get_row(conn, "scotus/900482").merits_argued is None  # type: ignore[union-attr]

        refused = backfill_decision_record(conn, apply=True, max_fills=0)
        assert refused.refused and not refused.applied

        applied = backfill_decision_record(conn, apply=True, max_fills=5)
        assert applied.applied
        again = backfill_decision_record(conn, apply=False)
    assert again.candidates == 1 and not again.filled  # the classified row left the population
    stored = _stored(tmp_path)
    assert stored.merits_argued == _ARGUED
    assert stored.merits_decision_method == "argued-signed"


def test_the_backfill_fills_an_argued_date_on_a_pending_case(tmp_path: Path) -> None:
    pending = _live(("Apr 07 2025", "Petition GRANTED."), ("Oct 14 2025", "Argued."))
    with _seeded(tmp_path, [_row()], {"scotus/900482": pending}) as conn:
        result = backfill_decision_record(conn, apply=True, max_fills=5)
        assert [(f.argued, f.method) for f in result.filled] == [(_ARGUED, None)]
        again = backfill_decision_record(conn, apply=False)
    assert again.candidates == 1 and again.unchanged == 1  # still pending, nothing new


def test_the_cli_requires_a_bound_and_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with _seeded(tmp_path, [_row()], {"scotus/900482": _decided_payload()}):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    unbounded = runner.invoke(app, ["backfill-decision-record", "--apply"])
    assert unbounded.exit_code == 2
    dry = runner.invoke(app, ["backfill-decision-record"])
    assert dry.exit_code == 0, dry.output
    assert "would fill 1 of 1 candidate(s)" in dry.output
    assert "argued-signed: 1" in dry.output
    applied = runner.invoke(app, ["backfill-decision-record", "--apply", "--max-fills", "1"])
    assert applied.exit_code == 0, applied.output
    assert _stored(tmp_path).merits_decision_method == "argued-signed"


# --- the census -------------------------------------------------------------------


def test_the_census_counts_per_term(tmp_path: Path) -> None:
    rows = [
        _row(
            merits_argued=_ARGUED,
            merits_judgment="reversed",
            merits_decided=_DECIDED,
            merits_decision_method="argued-signed",
        ),
        _row(
            case_id="scotus/900500",
            docket_number="25-500",
            disposition="gvr",
            date_cert_granted=date(2026, 6, 8),
            merits_decision_method="summary-order",
        ),
        _row(case_id="scotus/900501", docket_number="25-501"),  # pending
        _row(case_id="scotus/900502", docket_number="25-502", merits_terminated="abated"),
        _row(case_id="scotus/900503", docket_number="25A503"),  # not a cert docket
    ]
    with _seeded(tmp_path, rows) as conn:
        census = decision_census(conn, first_term=2024, last_term=2025)
    assert [t.term for t in census.terms] == [2024, 2025]
    assert census.terms[0].granted == 0
    ot25 = census.terms[1]
    assert (ot25.granted, ot25.argued, ot25.decided) == (2, 1, 2)
    assert ot25.methods == {"argued-signed": 1, "summary-order": 1}
    assert ot25.dispositions == {"reversed": 1, "vacated": 1}
    assert (census.pending, census.terminated) == (1, 1)


def test_the_census_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _seeded(tmp_path, [_row()]):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["decision-census", "--first-term", "2025", "--last-term", "2025"])
    assert result.exit_code == 0, result.output
    assert "OT2025: granted 0" in result.output
    backwards = runner.invoke(
        app, ["decision-census", "--first-term", "2025", "--last-term", "2024"]
    )
    assert backwards.exit_code == 2
