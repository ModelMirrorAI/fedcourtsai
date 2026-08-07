"""The merits-judgment parser and the granted-cohort backfill pass."""

from __future__ import annotations

from datetime import date
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
    last_judgment_entry,
    match_judgment,
    opinion_author,
)
from fedcourtsai.schemas import Disposition, Judgment

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
