"""The merits-judgment parser and the granted-cohort backfill pass."""

from __future__ import annotations

import threading
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.judgment import (
    PER_CURIAM,
    backfill_merits_judgments,
    judgment_disturbed,
    judgment_rode_the_grant_order,
    last_judgment_entry,
    last_merits_termination,
    match_judgment,
    match_merits_termination,
    opinion_author,
)
from fedcourtsai.schemas import Disposition, Judgment, MeritsTermination
from tests.conftest import DictSnapshotSource

runner = CliRunner()


# --- the parser truth table -------------------------------------------------------

# Real-shaped disposition entries, one per vocabulary member plus the shapes
# that must stay unmatched (recitals, motions, cert-stage orders).
_TABLE: tuple[tuple[str, Judgment | None], ...] = (
    (
        "Judgment REVERSED and case REMANDED.  Gorsuch, J., delivered the opinion "
        + "of the Court, in which Roberts, C. J., and Thomas, J., joined.",
        Judgment.reversed,
    ),
    ("Judgment VACATED and case REMANDED.", Judgment.vacated),
    (
        "Judgment VACATED and case REMANDED for further consideration in light of "
        + "Smith v. Jones, 599 U. S. 1 (2023).",
        Judgment.vacated,
    ),
    (
        # The canonical GVR order: the disposition sentence follows the cert
        # recital, so it must parse from a sentence start, not the entry start.
        "Petition GRANTED.  Judgment VACATED, and case REMANDED for further "
        + "consideration in light of United States v. Jones, 565 U. S. 400 (2012).",
        Judgment.vacated,
    ),
    (
        # The prose form names the lower court between the noun and the verb.
        "Judgment of the United States Court of Appeals for the Ninth Circuit "
        + "REVERSED and case REMANDED.",
        Judgment.reversed,
    ),
    ("Judgment AFFIRMED.  Kagan, J., delivered the opinion of the Court.", Judgment.affirmed),
    ("Adjudged to be AFFIRMED.", Judgment.affirmed),
    ("The judgment is affirmed.", Judgment.affirmed),
    # The mixed outcome, in either verb order, vacatur-in-part included.
    ("Judgment AFFIRMED IN PART, REVERSED IN PART, and case REMANDED.", Judgment.affirmed_in_part),
    (
        "Judgment reversed in part and affirmed in part, and case remanded.",
        Judgment.affirmed_in_part,
    ),
    ("Judgment AFFIRMED IN PART, VACATED IN PART, and case REMANDED.", Judgment.affirmed_in_part),
    # The two non-merits exits.
    (
        "Writ of certiorari DISMISSED as improvidently granted.  Opinion per curiam.",
        Judgment.dig,
    ),
    ("The writ of certiorari is dismissed as improvidently granted.", Judgment.dig),
    ("Judgment AFFIRMED by an equally divided Court.", Judgment.equally_divided),
    ("Adjudged to be AFFIRMED BY AN EQUALLY DIVIDED COURT.", Judgment.equally_divided),
    # Near-misses that must stay unmatched: a motion is not the Court's order,
    # a recital opens with its own noun, and cert-stage orders are not merits.
    ("Motion of respondent to dismiss the writ as improvidently granted filed.", None),
    ("Motion of respondent to vacate the judgment and remand filed.", None),
    ("Notice of appeal filed from the judgment affirmed on March 3, 2023.", None),
    ("Judgment issued.", None),  # the mandate analog carries no merits verb
    ("Petition GRANTED.", None),
    ("Petition DENIED.", None),
    ("DISTRIBUTED for Conference of 1/10/2025.", None),
    ("Brief of respondent in opposition filed.", None),
    ("", None),
)


@pytest.mark.parametrize(("text", "expected"), _TABLE)
def test_match_judgment_truth_table(text: str, expected: Judgment | None) -> None:
    assert match_judgment(text) == expected


# The termination vocabulary: entries that end a granted case's merits
# proceeding while saying nothing about the judgment below, plus the near
# misses — the motion that asks for the dismissal, the petition-stage twin, and
# a recital that names the shape mid-sentence.
_TERMINATION_TABLE: tuple[tuple[str, MeritsTermination | None], ...] = (
    ("Case Dismissed - Rule 46.", MeritsTermination.voluntary_dismissal),
    ("Case dismissed pursuant to Rule 46.1.", MeritsTermination.voluntary_dismissal),
    ("The case is dismissed under Rule 46.", MeritsTermination.voluntary_dismissal),
    # A PARTIAL Rule 46 dismissal leaves the case live as to the remaining
    # parties, so its merits question is still owed a forecast: closing
    # pendency here would lose one.
    ("Case dismissed as to petitioner Smith only under Rule 46.1.", None),
    ("Case Dismissed - Rule 46 as to respondent Jones.", None),
    ("JUDGMENT ISSUED.", MeritsTermination.judgment_issued),
    ("Judgment issued.", MeritsTermination.judgment_issued),
    # A petition-stage Rule 46 dismissal is a CERT event; the merits parser
    # must leave it to the cert seam, which is what anchoring on "case" buys.
    ("Petition Dismissed - Rule 46.", None),
    # The motion and the stipulation ask for the dismissal; neither is it.
    ("Motion to dismiss the case pursuant to Rule 46 filed by petitioner.", None),
    ("Stipulation of dismissal under Rule 46.1 filed.", None),
    ("Notice of appeal filed from the judgment issued on March 3, 2023.", None),
    # A real disposition is not a termination — the two vocabularies are disjoint.
    ("Judgment REVERSED and case REMANDED.", None),
    ("Writ of certiorari DISMISSED as improvidently granted.", None),
    ("DISTRIBUTED for Conference of 1/10/2025.", None),
    ("", None),
)


@pytest.mark.parametrize(("text", "expected"), _TERMINATION_TABLE)
def test_match_merits_termination_truth_table(
    text: str, expected: MeritsTermination | None
) -> None:
    assert match_merits_termination(text) == expected


@pytest.mark.parametrize(("text", "_expected"), _TERMINATION_TABLE)
def test_a_termination_is_never_a_disposition(text: str, _expected: object) -> None:
    """The two vocabularies never overlap on a termination shape.

    A termination states that the case ended, never how the judgment below
    fared, so admitting one to `Judgment` would fabricate merits ground truth —
    the truth table above pins "Judgment issued." to `None` for exactly that
    reason, and this holds the line for every shape the new vocabulary adds.
    """
    if match_merits_termination(text) is not None:
        assert match_judgment(text) is None


def test_judgment_disturbed_projection() -> None:
    # Reversal, vacatur, and the mixed outcome disturb the judgment below; an
    # affirmance does not, and neither non-merits exit does — a DIG dissolves
    # the writ (the judgment below stands), an equally divided Court affirms by
    # operation of law.
    disturbed = {Judgment.reversed, Judgment.vacated, Judgment.affirmed_in_part}
    for judgment in Judgment:
        assert judgment_disturbed(judgment) is (judgment in disturbed)


def test_opinion_author_best_effort() -> None:
    named = (
        "Judgment REVERSED and case REMANDED.  Gorsuch, J., delivered the opinion "
        "of the Court, in which Roberts, C. J., and Thomas, J., joined."
    )
    assert opinion_author(named) == "Gorsuch"
    chief = "Judgment AFFIRMED.  Roberts, C. J., delivered the opinion of the Court."
    assert opinion_author(chief) == "Roberts"
    per_curiam = "Writ of certiorari DISMISSED as improvidently granted.  Opinion per curiam."
    assert opinion_author(per_curiam) == PER_CURIAM
    # PER CURIAM is recognized distinctly from any single-token Justice name.
    assert " " in PER_CURIAM
    assert opinion_author("DISTRIBUTED for Conference of 1/10/2025.") is None
    assert opinion_author("") is None
    # A named author wins over a stray per curiam mention elsewhere in the entry.
    both = (
        "Judgment AFFIRMED.  Kagan, J., delivered the opinion of the Court "
        "(revising the per curiam order below)."
    )
    assert opinion_author(both) == "Kagan"


# --- last_judgment_entry over both payload shapes ---------------------------------


def _live_payload(*entries: tuple[str, str]) -> dict[str, Any]:
    return {
        "CaseNumber": "23-100",
        "ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries],
    }


def test_last_judgment_entry_takes_the_last_match_with_its_date() -> None:
    payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Apr 22 2024", "Argued. For petitioner: X. For respondent: Y."),
        ("Jun 27 2024", "Judgment REVERSED and case REMANDED."),
        ("Jul 30 2024", "Judgment issued."),
    )
    assert last_judgment_entry(payload) == (Judgment.reversed, date(2024, 6, 27))


def test_last_judgment_entry_rest_shape_and_undated_entry() -> None:
    rest = {
        "docket_entries": [
            {"date_filed": "2024-01-12", "description": "Petition GRANTED."},
            {"description": "Judgment AFFIRMED."},  # no date: parsed, date None
        ]
    }
    assert last_judgment_entry(rest) == (Judgment.affirmed, None)


def test_last_judgment_entry_none_without_a_match() -> None:
    assert last_judgment_entry(_live_payload(("Jan 12 2024", "Petition DENIED."))) is None
    assert last_judgment_entry({}) is None


def test_last_merits_termination_takes_the_last_match() -> None:
    payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Jul 09 2025", "Motion to dispense with printing the joint appendix filed."),
        ("Aug 08 2025", "Stipulation of dismissal under Rule 46.1 filed."),
        ("Aug 11 2025", "Case Dismissed - Rule 46."),
    )
    assert last_merits_termination(payload) == MeritsTermination.voluntary_dismissal
    assert last_merits_termination(_live_payload(("Jan 12 2024", "Petition GRANTED."))) is None
    assert last_merits_termination({}) is None


# --- the backfill pass ------------------------------------------------------------


def _granted_row(case_id: str, docket: str, granted: date) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        date_filed=date(2023, 9, 1),
        disposition=Disposition.granted,
        date_cert_granted=granted,
        last_live_polled=date(2024, 7, 1),
        sample_weight=1,
    )


def _seed_backfill_corpus(corpus_root: Path) -> Path:
    """Granted rows covering parsed / no-match / no-snapshot, plus a denial.

    - scotus/1: granted, snapshot ends in a reversal -> parsed (reversed).
    - scotus/2: granted, snapshot ends in a DIG -> parsed (dig).
    - scotus/3: granted, snapshot still pending-shaped -> no_match.
    - scotus/4: granted, no snapshot stored -> no_snapshot.
    - scotus/5: denied -> not eligible at all.
    """
    db = corpus.corpus_db_path(corpus_root)
    reversed_payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        (
            "Jun 27 2024",
            "Judgment REVERSED and case REMANDED.  Gorsuch, J., "
            + "delivered the opinion of the Court.",
        ),
    )
    dig_payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Jun 20 2024", "Writ of certiorari DISMISSED as improvidently granted."),
    )
    pending_payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Apr 22 2024", "Argued. For petitioner: X."),
    )
    rows = [
        _granted_row("scotus/1", "23-101", date(2024, 1, 12)),
        _granted_row("scotus/2", "23-102", date(2024, 1, 12)),
        _granted_row("scotus/3", "23-103", date(2024, 1, 12)),
        _granted_row("scotus/4", "23-104", date(2024, 1, 12)),
        corpus.CorpusRow(
            case_id="scotus/5",
            court="scotus",
            docket_number="23-105",
            disposition=Disposition.denied,
            date_cert_denied=date(2024, 1, 12),
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_snapshot(conn, "scotus/1", date(2024, 7, 1), reversed_payload)
        corpus.upsert_snapshot(conn, "scotus/2", date(2024, 7, 1), dig_payload)
        corpus.upsert_snapshot(conn, "scotus/3", date(2024, 7, 1), pending_payload)
    return db


def test_backfill_dry_run_counts_and_writes_nothing(tmp_path: Path) -> None:
    db = _seed_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        result = backfill_merits_judgments(conn, apply=False)
        row = corpus.get_row(conn, "scotus/1")
    assert result.applied is False
    assert result.eligible == 4
    assert result.parsed == 2 and result.updated == 2 and result.unchanged == 0
    assert result.no_snapshot == 1 and result.no_match == 1
    assert result.judgments == {"dismissed-as-improvidently-granted": 1, "reversed": 1}
    assert row is not None and row.merits_judgment is None and row.merits_decided is None


def test_backfill_apply_stamps_and_is_idempotent(tmp_path: Path) -> None:
    db = _seed_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        first = backfill_merits_judgments(conn, apply=True)
        one = corpus.get_row(conn, "scotus/1")
        two = corpus.get_row(conn, "scotus/2")
        three = corpus.get_row(conn, "scotus/3")
        again = backfill_merits_judgments(conn, apply=True)
    assert first.applied is True and first.updated == 2
    assert one is not None
    assert one.merits_judgment == Judgment.reversed.value
    assert one.merits_decided == date(2024, 6, 27)
    assert two is not None
    assert two.merits_judgment == Judgment.dig.value
    assert two.merits_decided == date(2024, 6, 20)
    assert three is not None and three.merits_judgment is None
    # Idempotent: the second pass finds everything already stored.
    assert again.parsed == 2 and again.unchanged == 2 and again.updated == 0
    assert again.stale == 0


def test_backfill_counts_stored_judgments_it_cannot_rederive_as_stale(tmp_path: Path) -> None:
    # The pass never clears a stored judgment, so a reading it can no longer
    # re-derive (snapshot gone, or a tightened parser retracting a match) must
    # at least stay visible: it lands in `stale`, and the value is kept.
    db = _seed_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        # scotus/3 (pending-shaped snapshot) and scotus/4 (no snapshot) carry
        # judgments no current parse supports.
        corpus.set_merits_judgment(conn, "scotus/3", Judgment.affirmed, None)
        corpus.set_merits_judgment(conn, "scotus/4", Judgment.reversed, date(2024, 6, 1))
        result = backfill_merits_judgments(conn, apply=True)
        three = corpus.get_row(conn, "scotus/3")
        four = corpus.get_row(conn, "scotus/4")
    assert result.stale == 2
    assert result.no_match == 1 and result.no_snapshot == 1
    assert three is not None and three.merits_judgment == Judgment.affirmed.value
    assert four is not None and four.merits_judgment == Judgment.reversed.value


def test_backfill_reads_the_content_store_concurrently_and_identically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The offloaded branch serves the snapshot reads from the registered
    source — one read per eligible row, none repeated — and its result is
    identical to the serial SQLite pass: same counts, same distributions, same
    stale/termination classification. The eligibility walk stays in SQLite
    either way (it is metadata); only the snapshot reads move."""
    db = _seed_backfill_corpus(tmp_path / "corpus")
    eligible = [f"scotus/{n}" for n in (1, 2, 3, 4)]
    with corpus.connect(db) as conn:
        serial = backfill_merits_judgments(conn, apply=False)
        stored = {case_id: corpus.latest_snapshot(conn, case_id) for case_id in eligible}
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    source = DictSnapshotSource(stored)
    # Save/restore the registered source around the swap; the read of the
    # private registry is the only way to put back the casestore singleton it
    # registers at import (there is no public getter).
    previous = corpus._READ_SOURCE.get("source")
    corpus.set_payload_read_source(source)
    try:
        assert corpus.payload_reads_offloaded()
        with corpus.connect(db) as conn:
            offloaded = backfill_merits_judgments(conn, apply=False)
    finally:
        corpus.set_payload_read_source(previous)
    assert offloaded == serial
    assert offloaded.eligible == 4 and offloaded.parsed == 2 and offloaded.no_snapshot == 1
    # One read per eligible row — the denied row is never read, and the pool
    # never duplicates a fetch.
    assert sorted(source.read_threads) == eligible
    assert all(len(idents) == 1 for idents in source.read_threads.values())
    # The warm-up read runs on the calling thread; the tail runs off it.
    assert source.read_threads[eligible[0]] == [threading.get_ident()]
    tail_idents = {
        idents[0] for case_id, idents in source.read_threads.items() if case_id != eligible[0]
    }
    assert threading.get_ident() not in tail_idents


def _seed_termination_corpus(corpus_root: Path) -> Path:
    """Two granted rows the disposition parser cannot read, one terminated.

    - scotus/10: merits briefing, then a post-grant Rule 46 dismissal.
    - scotus/11: a decided docket whose only terminal notation is the mandate.
    - scotus/12: pending-shaped, so still genuine `no_match` residue.
    """
    db = corpus.corpus_db_path(corpus_root)
    dismissed = _live_payload(
        ("Jan 10 2025", "Petition GRANTED."),
        ("Aug 08 2025", "Stipulation of dismissal under Rule 46.1 filed."),
        ("Aug 11 2025", "Case Dismissed - Rule 46."),
    )
    mandate_only = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Jul 30 2024", "JUDGMENT ISSUED."),
    )
    pending = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Apr 22 2024", "Argued. For petitioner: X."),
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _granted_row("scotus/10", "24-413", date(2025, 1, 10)),
                _granted_row("scotus/11", "18-710", date(2024, 1, 12)),
                _granted_row("scotus/12", "23-103", date(2024, 1, 12)),
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/10", date(2026, 7, 1), dismissed)
        corpus.upsert_snapshot(conn, "scotus/11", date(2026, 7, 1), mandate_only)
        corpus.upsert_snapshot(conn, "scotus/12", date(2026, 7, 1), pending)
    return db


def test_backfill_records_terminations_without_a_judgment(tmp_path: Path) -> None:
    db = _seed_termination_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        dry = backfill_merits_judgments(conn, apply=False)
        untouched = corpus.get_row(conn, "scotus/10")
        applied = backfill_merits_judgments(conn, apply=True)
        dismissal = corpus.get_row(conn, "scotus/10")
        mandate = corpus.get_row(conn, "scotus/11")
        residue = corpus.get_row(conn, "scotus/12")
        again = backfill_merits_judgments(conn, apply=True)
    assert dry.terminated == 2 and dry.terminations_written == 2
    assert untouched is not None and untouched.merits_terminated is None
    # A termination resolves pendency and nothing else: no judgment is invented,
    # so the parsed slice and the disturbed rate never see these rows.
    assert applied.terminated == 2 and applied.parsed == 0 and applied.no_match == 1
    assert dismissal is not None
    assert dismissal.merits_terminated == MeritsTermination.voluntary_dismissal.value
    assert dismissal.merits_judgment is None and dismissal.merits_decided is None
    assert mandate is not None
    assert mandate.merits_terminated == MeritsTermination.judgment_issued.value
    assert mandate.merits_judgment is None
    assert residue is not None and residue.merits_terminated is None
    # Idempotent: a second pass still counts them but writes nothing new.
    assert again.terminated == 2 and again.terminations_written == 0
    # Published per class: the two shapes carry different evidence, so a climb
    # in the mandate-notation count is a parser gap rather than a docket trend.
    assert applied.terminations == {
        MeritsTermination.judgment_issued.value: 1,
        MeritsTermination.voluntary_dismissal.value: 1,
    }
    # A terminated row is never also a `no_match`: the residue is the genuine
    # remainder, so the two counts partition the unparsed rows.
    assert applied.no_match == 1 and applied.eligible == 3


def test_a_termination_never_displaces_a_parsed_disposition(tmp_path: Path) -> None:
    # "JUDGMENT ISSUED." trails the real disposition on an ordinary decided
    # docket. The fallback runs only when no judgment shape matched anywhere,
    # so the mandate notation can never overwrite the reversal.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        ("Jun 27 2024", "Judgment REVERSED and case REMANDED."),
        ("Jul 30 2024", "JUDGMENT ISSUED."),
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted_row("scotus/20", "23-120", date(2024, 1, 12))])
        corpus.upsert_snapshot(conn, "scotus/20", date(2024, 8, 1), payload)
        result = backfill_merits_judgments(conn, apply=True)
        row = corpus.get_row(conn, "scotus/20")
    assert result.parsed == 1 and result.terminated == 0
    assert row is not None
    assert row.merits_judgment == Judgment.reversed.value
    assert row.merits_decided == date(2024, 6, 27)
    assert row.merits_terminated is None


def test_a_retracted_parse_stays_stale_and_never_becomes_a_termination(tmp_path: Path) -> None:
    """A stored judgment the pass cannot re-derive is a retraction, not a termination.

    The trap the fallback ordering has to avoid: "Judgment issued." is the
    ordinary trailing mandate notation on a decided merits docket, so a
    disposition-parser tightening that retracts a reading would land every
    affected row in `terminated` — silencing the `stale` counter that exists to
    make the retraction visible, and leaving one row carrying a stored
    disposition *and* a termination, the pair the two columns are defined never
    to share.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    payload = _live_payload(
        ("Jan 12 2024", "Petition GRANTED."),
        # A disposition shape the parser does not know, so `last_judgment_entry`
        # finds nothing — followed by the mandate notation.
        ("Jun 27 2024", "Decree of the court below set aside on the merits."),
        ("Jul 30 2024", "JUDGMENT ISSUED."),
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted_row("scotus/30", "23-130", date(2024, 1, 12))])
        corpus.upsert_snapshot(conn, "scotus/30", date(2024, 8, 1), payload)
        corpus.set_merits_judgment(conn, "scotus/30", Judgment.reversed, date(2024, 6, 27))
        result = backfill_merits_judgments(conn, apply=True)
        row = corpus.get_row(conn, "scotus/30")
    assert result.stale == 1 and result.no_match == 1
    assert result.terminated == 0 and result.terminations_written == 0
    assert row is not None
    # Neither column moved: the stored parse is kept (never cleared) and no
    # termination was invented beside it.
    assert row.merits_judgment == Judgment.reversed.value
    assert row.merits_terminated is None


def test_ingestion_upsert_keeps_a_recorded_termination(tmp_path: Path) -> None:
    # The sweep owns the column; no ingestion channel ever has one to assert, so
    # a re-ingest must not carry its NULL through and clear the finding.
    db = _seed_termination_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        backfill_merits_judgments(conn, apply=True)
        corpus.upsert_rows(conn, [_granted_row("scotus/10", "24-413", date(2025, 1, 10))])
        row = corpus.get_row(conn, "scotus/10")
    assert row is not None
    assert row.merits_terminated == MeritsTermination.voluntary_dismissal.value


def test_backfill_ingestion_upsert_keeps_the_stamped_columns(tmp_path: Path) -> None:
    # A re-ingest of the same case (no merits columns of its own) must not wipe
    # what the backfill stamped — the keep-stored latch in `_update_clause`.
    db = _seed_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        backfill_merits_judgments(conn, apply=True)
        corpus.upsert_rows(conn, [_granted_row("scotus/1", "23-101", date(2024, 1, 12))])
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None
    assert row.merits_judgment == Judgment.reversed.value
    assert row.merits_decided == date(2024, 6, 27)


# --- CLI --------------------------------------------------------------------------


def test_cli_dry_run_reports_and_apply_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = _seed_backfill_corpus(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["backfill-merits-judgments"])
    assert dry.exit_code == 0, dry.output
    assert "dry-run" in dry.output and "would stamp 2" in dry.output
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None and row.merits_judgment is None

    applied = runner.invoke(app, ["backfill-merits-judgments", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "applied" in applied.output and "stamped 2" in applied.output
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None and row.merits_judgment == Judgment.reversed.value


def test_cli_fails_loud_without_a_corpus(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["backfill-merits-judgments"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )
    assert result.exit_code == 1


def test_judgment_rode_the_grant_order_is_the_gap_guard() -> None:
    """Same-day (and data-noise earlier) judgments rode the cert order; a
    judgment even one day later is the merits court's own — an expedited
    argued case lands days after its grant, never on it."""
    granted = date(2020, 1, 13)
    assert judgment_rode_the_grant_order(granted, granted)
    assert judgment_rode_the_grant_order(granted - timedelta(days=3), granted)
    assert not judgment_rode_the_grant_order(granted + timedelta(days=1), granted)
