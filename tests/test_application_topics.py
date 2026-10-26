"""Fixture-pinned tests for the application extract a ``qp-topic-v1`` labeler reads.

The extract's one hard promise is that nothing in a row postdates the
disposition, so the fixtures pin the cutoff from each side: the order itself, a
filing docketed beside it, a later refiling, the stored decision date, and the
Court's own acts before the decision.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.application_topics import (
    APPLICATION_TEXT_BUDGET,
    application_extract,
    application_frame,
    application_row,
    pre_disposition_entries,
)
from fedcourtsai.pipeline.qp_topics import (
    APPLICATION_BATCH_ORDER_SEED,
    application_reference_path,
)
from fedcourtsai.schemas import Disposition, QpTopicApplicationReference
from fedcourtsai.serialize import write_json

runner = CliRunner()

CAPTION = "Kristi Noem, Secretary of Homeland Security, et al. v. Jane Doe, et al."


def _row(case_id: str, docket: str, **kwargs: object) -> corpus.CorpusRow:
    """One live-slice SCOTUS application row."""
    fields: dict[str, object] = {
        "case_name": CAPTION,
        "last_live_polled": date(2026, 9, 1),
        "application_kind": "substantive",
        **kwargs,
    }
    return corpus.CorpusRow(case_id=case_id, court="scotus", docket_number=docket, **fields)


def _payload(*entries: tuple[str, str]) -> dict[str, object]:
    return {
        "LowerCourt": "United States Court of Appeals for the First Circuit",
        "ProceedingsandOrder": [{"Date": dated, "Text": text} for dated, text in entries],
    }


def _document(case_id: str, kind: str, entry_date: str | None, text: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=kind,
        url=f"https://example.invalid/{kind}.pdf",
        entry_date=entry_date,
        fetched_at=date(2026, 1, 1),
        text=text,
    )


DOCKET = _payload(
    ("Mar 03 2025", "Application (24A949) for a stay, submitted to Justice Jackson."),
    ("Mar 05 2025", "Response to application (24A949) requested by Justice Jackson."),
    ("Mar 06 2025", "Administrative stay entered by Justice Jackson."),
    ("Mar 10 2025", "Response to application from respondent Jane Doe filed."),
    ("Mar 11 2025", "Motion for leave to file amicus brief granted."),
    ("Apr 10 2025", "Reply of applicant Kristi Noem filed."),
    ("Apr 10 2025", "Application (24A949) granted by the Court."),
    ("Apr 20 2025", "Letter of respondent Jane Doe filed."),
    ("", "Undated note."),
)


def test_only_filings_before_the_disposition_reach_the_labeler() -> None:
    read, cutoff, entries = pre_disposition_entries(DOCKET, None)
    assert (read, cutoff) == (True, date(2025, 4, 10))
    assert [entry.text for entry in entries] == [
        "Application (24A949) for a stay, submitted to Justice Jackson.",
        "Response to application (24A949) requested by Justice Jackson.",
        "Response to application from respondent Jane Doe filed.",
    ]
    # The reply docketed the same day as the order goes with it.
    assert all(entry.date < "2025-04-10" for entry in entries)


def test_the_first_disposition_cuts_a_refiled_application() -> None:
    refiled = _payload(
        ("Feb 11 2026", "Application (25A918) for a stay, submitted to The Chief Justice."),
        ("Feb 19 2026", "Application (25A918) denied by The Chief Justice."),
        ("Mar 10 2026", "Application (25A918) refiled and submitted to Justice Sotomayor."),
        ("Apr 06 2026", "Application (25A918) denied by the Court."),
    )
    _, cutoff, entries = pre_disposition_entries(refiled, None)
    assert cutoff == date(2026, 2, 19)
    assert len(entries) == 1


def test_a_stored_decision_date_cuts_where_no_order_is_read() -> None:
    _, cutoff, entries = pre_disposition_entries(DOCKET, date(2025, 3, 10))
    assert cutoff == date(2025, 3, 10)
    assert len(entries) == 2


def test_the_filing_entry_survives_naming_an_order_below() -> None:
    payload = _payload(
        ("Mar 03 2025", "Application (24A1) to vacate the injunction ordered by the court."),
        ("Mar 04 2025", "It is ordered that the response be filed."),
    )
    read, _, entries = pre_disposition_entries(payload, None)
    assert not read
    assert [entry.text for entry in entries] == [
        "Application (24A1) to vacate the injunction ordered by the court."
    ]


def test_an_undated_disposition_still_cuts_by_position() -> None:
    payload = _payload(
        ("Mar 03 2025", "Application (24A1) for a stay, submitted to Justice Kagan."),
        ("not a date", "Application (24A1) denied by Justice Kagan."),
        ("Mar 20 2025", "Application (24A1) refiled and submitted to Justice Gorsuch."),
        ("Mar 21 2025", "Letter from applicant regarding the denial filed."),
    )
    read, cutoff, entries = pre_disposition_entries(payload, None)
    assert (read, cutoff) == (True, None)
    assert [entry.date for entry in entries] == ["2025-03-03"]


@pytest.mark.parametrize(
    "text",
    [
        "Application (24A1) referred to the Court is deferred pending oral argument.",
        "SET FOR ARGUMENT on Monday, April 21, 2025.",
        "Argued. For applicants: D. John Sauer.",
        "Application (24A1) treated as a petition for a writ of certiorari.",
    ],
)
def test_the_courts_other_acts_are_dropped(text: str) -> None:
    payload = _payload(
        ("Mar 03 2025", "Application (24A1) for a stay, submitted to Justice Kagan."),
        ("Mar 04 2025", text),
    )
    _, _, entries = pre_disposition_entries(payload, None)
    assert len(entries) == 1


def test_a_row_reads_the_application_text_only_before_the_cutoff() -> None:
    row = _row("scotus/1", "24A949", date_decided=date(2025, 4, 10))
    long_text = "Whether the parole terminations are lawful. " * 400
    documents = [
        _document("scotus/1", "application-response", "2025-03-10", "Response text."),
        _document("scotus/1", "application", "2025-03-03", long_text),
    ]
    extracted = application_row(row, DOCKET, documents)
    assert extracted.input_kind == "application-text"
    assert len(extracted.text) == APPLICATION_TEXT_BUDGET
    assert extracted.lower_court == "United States Court of Appeals for the First Circuit"
    assert extracted.caption == CAPTION

    verbatim = [_document("scotus/1", "application", "Mar 03 2025", "Parole terminations.")]
    assert application_row(row, DOCKET, verbatim).input_kind == "application-text"
    late = [_document("scotus/1", "application", "Apr 10 2025", "Filed with the order.")]
    assert application_row(row, DOCKET, late).input_kind == "docket-only"
    blank = [_document("scotus/1", "application", "2025-03-03", "   ")]
    assert application_row(row, DOCKET, blank).input_kind == "docket-only"
    unreadable = [_document("scotus/1", "application", "sometime", "Parole terminations.")]
    assert application_row(row, DOCKET, unreadable).input_kind == "docket-only"
    undated = [_document("scotus/1", "application", None, "Parole terminations.")]
    assert application_row(row, DOCKET, undated).input_kind == "application-text"
    bare = application_row(row, None, [])
    assert (bare.input_kind, bare.entries, bare.lower_court) == ("docket-only", (), None)


def test_the_frame_is_one_row_per_docket_without_extensions() -> None:
    rows = [
        _row("scotus/1", "24A949"),
        _row("scotus/2", "24a949 "),
        _row("scotus/3", "24A950", application_kind="extension"),
        _row("scotus/4", "24A951", application_kind="unknown"),
        _row("scotus/5", "24A952", application_kind=None),
        _row("scotus/6", "24-1234", application_kind=None),
    ]
    frame, duplicates, extensions = application_frame(rows)
    assert [row.case_id for row in frame] == ["scotus/1", "scotus/4", "scotus/5"]
    assert (duplicates, extensions) == (1, 1)


def _seed(db: Path) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    "scotus/1",
                    "24A949",
                    disposition=Disposition.granted,
                    date_decided=date(2025, 4, 10),
                ),
                _row(
                    "scotus/2",
                    "25A10",
                    application_kind="unknown",
                    disposition=Disposition.denied,
                ),
                _row("scotus/3", "25A11", application_kind="extension"),
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/1", date(2025, 4, 11), DOCKET)
        corpus.upsert_documents(
            conn, [_document("scotus/1", "application", "2025-03-03", "Parole terminations.")]
        )
        conn.commit()


def test_the_extract_tallies_coverage_by_term_ask_and_input(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db)
    with corpus.connect(db) as conn:
        extract = application_extract(conn)
    assert [row.case_id for row in extract.rows] == ["scotus/1", "scotus/2"]
    assert (extract.extension_rows, extract.decided_unread) == (1, 1)
    assert dict(extract.coverage) == {
        (2024, "substantive", "application-text"): 1,
        (2025, "unknown", "docket-only"): 1,
    }


def test_the_command_writes_the_application_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    _seed(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    out = tmp_path / "applications.json"
    result = runner.invoke(app, ["qp-corpus", "--frame", "applications", "--out", str(out)])
    # The batch is cut against the application reference block, so the extract
    # refuses without one rather than handing a labeler an unmeasurable batch.
    assert result.exit_code == 1
    assert "no reference set" in result.stderr
    assert not out.exists()
    write_json(
        application_reference_path(tmp_path / "data"),
        QpTopicApplicationReference(
            cases=1,
            entries=[
                {
                    "case_id": "scotus/1",
                    "docket_number": "24A949",
                    "input_kind": "application-text",
                    "label": "immigration",
                }
            ],
        ),
    )
    result = runner.invoke(app, ["qp-corpus", "--frame", "applications", "--out", str(out)])
    assert result.exit_code == 0, result.output
    rows = json.loads(out.read_text())
    assert [row["docket_number"] for row in rows] == ["24A949", "25A10"]
    sidecar = json.loads(out.with_name("applications.batch.json").read_text())
    assert (sidecar["frame"], sidecar["rows"], sidecar["reference_rows"]) == (2, 2, 1)
    assert sidecar["seed"] == APPLICATION_BATCH_ORDER_SEED
    assert [row["stratum"] for row in sidecar["strata"]] == ["2025/application"]
    assert rows[0]["input_kind"] == "application-text"
    assert [entry["date"] for entry in rows[0]["entries"]] == [
        "2025-03-03",
        "2025-03-05",
        "2025-03-10",
    ]
    assert "granted by the Court" not in out.read_text()
    assert "application-extract-v1; 0 duplicate row(s) and 1 extension(s) left out; 1 decided" in (
        result.stderr
    )
    assert "OT2024 substantive application-text: 1" in result.stderr


def test_the_command_refuses_all_with_the_application_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    out = tmp_path / "applications.json"
    result = runner.invoke(
        app, ["qp-corpus", "--frame", "applications", "--all", "--out", str(out)]
    )
    assert result.exit_code == 2
    assert not out.exists()
