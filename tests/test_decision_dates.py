"""The decision-date convergence: a denied petition's termination date.

The shape the sweep exists for is a resolved pre-2022 cert docket whose
``disposition`` and ``date_cert_denied`` are both latched while ``date_decided``
never took a value — the row reads terminated to every seam that consults the
disposition and undated to every seam that reads the date. The sweep fills the
date in from the row's own denial date, and the paired ingest default is what
keeps the fill from being undone by the next walk of the Term.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.analytics import _decision_days
from fedcourtsai.cli import app
from fedcourtsai.pipeline.decision_dates import converge_decision_dates
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row

runner = CliRunner()


#: The issue's own shape, in miniature: three denied dockets resolved years ago
#: with their cert-denial date latched and no `date_decided`, one granted docket
#: beside them (whose termination is a later merits judgment no column holds),
#: one GVR (grant side, same reason), one denial the parse never dated, and one
#: already-converged denial that must not be rewritten.
def _rows() -> list[corpus.CorpusRow]:
    return [
        corpus.CorpusRow(
            case_id="scotus/66721476",
            court="scotus",
            docket_number="18-710",
            date_filed=date(2018, 12, 3),
            disposition="denied",
            date_cert_denied=date(2019, 4, 22),
        ),
        corpus.CorpusRow(
            case_id="scotus/66726256",
            court="scotus",
            docket_number="19-337",
            date_filed=date(2019, 9, 12),
            disposition="denied",
            date_cert_denied=date(2020, 1, 13),
        ),
        corpus.CorpusRow(
            case_id="scotus/72465236",
            court="scotus",
            docket_number="20-1215",
            date_filed=date(2021, 3, 3),
            disposition="denied",
            date_cert_denied=date(2021, 6, 28),
        ),
        corpus.CorpusRow(
            case_id="scotus/72466202",
            court="scotus",
            docket_number="20-429",
            date_filed=date(2020, 10, 5),
            disposition="granted",
            date_cert_granted=date(2021, 2, 22),
        ),
        corpus.CorpusRow(
            case_id="scotus/72464349",
            court="scotus",
            docket_number="19-825",
            date_filed=date(2019, 12, 31),
            disposition="gvr",
            date_cert_granted=date(2020, 7, 9),
        ),
        # A denial whose disposing entry carried no date: nothing to converge
        # from, and the sweep never guesses one.
        corpus.CorpusRow(
            case_id="scotus/206",
            court="scotus",
            docket_number="93-5124",
            disposition="denied",
        ),
        # Already converged — out of population, so a second run reports it as
        # nothing owed rather than rewriting it.
        corpus.CorpusRow(
            case_id="scotus/999",
            court="scotus",
            docket_number="21-101",
            date_filed=date(2021, 8, 1),
            disposition="denied",
            date_cert_denied=date(2022, 1, 10),
            date_decided=date(2022, 1, 10),
        ),
        # A denial dated before its own filing: upstream nonsense the sweep
        # declines rather than spreading into a second column.
        corpus.CorpusRow(
            case_id="scotus/888",
            court="scotus",
            docket_number="24-1246",
            date_filed=date(2025, 6, 9),
            disposition="denied",
            date_cert_denied=date(2025, 6, 6),
        ),
        # A denial dated after the as-of day: a future-dated `date_decided` is
        # the one shape the validation monitor fails on outright.
        corpus.CorpusRow(
            case_id="scotus/777",
            court="scotus",
            docket_number="26-1",
            date_filed=date(2026, 1, 5),
            disposition="denied",
            date_cert_denied=date(2027, 1, 5),
        ),
        # A circuit docket: the sweep's SCOTUS filter is load-bearing, since
        # `date_cert_denied` has no meaning off the Supreme Court's docket.
        corpus.CorpusRow(
            case_id="ca9/4321",
            court="ca9",
            docket_number="21-35466",
            date_filed=date(2021, 5, 3),
            disposition="denied",
            date_cert_denied=date(2021, 11, 8),
        ),
    ]


#: The as-of day every test anchors the future-date guard on.
_TODAY = date(2026, 9, 3)


def _decided(db: Path, case_id: str) -> date | None:
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.date_decided


_GAP_CASES = ["scotus/66721476", "scotus/66726256", "scotus/72465236"]


def test_dry_run_plans_the_write_set_without_writing(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        result = converge_decision_dates(conn, apply=False, today=_TODAY)
    assert result.applied is False
    assert result.candidates == len(_GAP_CASES)
    assert result.converged == 0
    assert result.sample == sorted(_GAP_CASES)
    assert _decided(db, "scotus/66721476") is None  # dry run wrote nothing


def test_apply_fills_the_decision_date_from_the_rows_own_denial_date(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        result = converge_decision_dates(conn, apply=True, today=_TODAY)
    assert result.applied is True
    assert (result.candidates, result.converged) == (len(_GAP_CASES), len(_GAP_CASES))
    # Each converged row takes its OWN denial date, never a shared one.
    assert _decided(db, "scotus/66721476") == date(2019, 4, 22)
    assert _decided(db, "scotus/66726256") == date(2020, 1, 13)
    assert _decided(db, "scotus/72465236") == date(2021, 6, 28)


def test_the_grant_side_and_the_undated_denial_are_out_of_population(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        converge_decision_dates(conn, apply=True, today=_TODAY)
    # A granted docket terminates at its merits judgment, months after the
    # grant — a date no column on the row carries, so none is invented.
    assert _decided(db, "scotus/72466202") is None
    assert _decided(db, "scotus/72464349") is None  # a GVR is on the grant side
    # A denial the parse never dated has nothing to converge from.
    assert _decided(db, "scotus/206") is None
    # An already-converged row keeps the date it had.
    assert _decided(db, "scotus/999") == date(2022, 1, 10)
    # A circuit docket is outside the sweep's universe entirely.
    assert _decided(db, "ca9/4321") is None


def test_the_date_guards_decline_rather_than_propagate(tmp_path: Path) -> None:
    # Both guards keep the sweep from being the writer that creates a reading
    # the validation monitor would have to absorb: a decided-before-filed pair
    # it would otherwise spread into a second column, and a future-dated
    # `date_decided`, which `check_case_dates` fails on with no baseline.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        planned = corpus.denial_termination_gap_case_ids(conn, today=_TODAY)
        converge_decision_dates(conn, apply=True, today=_TODAY)
    assert "scotus/888" not in planned and "scotus/777" not in planned
    assert _decided(db, "scotus/888") is None  # denial predates its own filing
    assert _decided(db, "scotus/777") is None  # denial dated after the as-of day
    # The future-dated row is not refused forever — it converges once the as-of
    # day catches up, which is what makes the guard a bound rather than a drop.
    with corpus.connect(db) as conn:
        converge_decision_dates(conn, apply=True, today=date(2027, 6, 1))
    assert _decided(db, "scotus/777") == date(2027, 1, 5)
    assert _decided(db, "scotus/888") is None  # the ordering guard is permanent


def test_the_sweep_is_idempotent(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        converge_decision_dates(conn, apply=True, today=_TODAY)
        again = converge_decision_dates(conn, apply=True, today=_TODAY)
    assert (again.candidates, again.converged) == (0, 0)
    assert again.sample == []


def test_a_converged_row_survives_the_next_live_re_ingest(tmp_path: Path) -> None:
    # The pairing that makes this a convergence rather than a treadmill:
    # `date_decided` is last-write-wins on upsert, so the sweep's write holds
    # only because the live parse derives the same date. Re-ingesting the
    # docket the walker would re-serve must leave the converged value standing.
    db = corpus.corpus_db_path(tmp_path)
    payload = {
        "CaseNumber": "18-710",
        "ProceedingsandOrder": [
            {"Date": "Dec 03 2018", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "Apr 22 2019", "Text": "Petition DENIED."},
        ],
    }
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        converge_decision_dates(conn, apply=True, today=_TODAY)
        re_ingested = to_corpus_row(
            from_live_record(map_live_docket(payload, 66_721_476, form="cert"))
        )
        # The re-served row carries the date itself — the reason the upsert's
        # last-write-wins assignment cannot blank the converged column.
        assert re_ingested.date_decided == date(2019, 4, 22)
        corpus.upsert_rows(conn, [re_ingested])
    assert _decided(db, "scotus/66721476") == date(2019, 4, 22)
    # And the population stays empty: nothing re-enters the sweep.
    with corpus.connect(db) as conn:
        assert corpus.denial_termination_gap_case_ids(conn, today=_TODAY) == []


def test_the_fill_writes_the_date_the_row_already_resolved_on(tmp_path: Path) -> None:
    # The warrant for writing at all: `resolution_date` already returned this
    # value off `date_cert_denied`, so the converged column cannot disagree with
    # the date the rest of the pipeline reads off the row. It is the same before
    # the sweep as after — which is exactly why the fill invents nothing.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        before = corpus.get_row(conn, "scotus/66721476")
        assert before is not None and corpus.resolution_date(before) == date(2019, 4, 22)
        converge_decision_dates(conn, apply=True, today=_TODAY)
        after = corpus.get_row(conn, "scotus/66721476")
        assert after is not None
        assert after.date_decided == corpus.resolution_date(before)


def test_the_fill_admits_the_row_to_docket_termination_timing(tmp_path: Path) -> None:
    # What the fill is worth downstream, and the one measured surface it moves:
    # `_decision_days` keys the statpack's pack-level timing on
    # date_filed -> date_decided, so a gap-shaped denial contributes nothing
    # until the column is filled. The grant side stays absent either way.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
        gap = corpus.get_row(conn, "scotus/66721476")
        grant = corpus.get_row(conn, "scotus/72466202")
        assert gap is not None and grant is not None
        assert _decision_days(gap) is None
        converge_decision_dates(conn, apply=True, today=_TODAY)
        filled = corpus.get_row(conn, "scotus/66721476")
        still_granted = corpus.get_row(conn, "scotus/72466202")
        assert filled is not None and still_granted is not None
    # 2018-12-03 filed -> 2019-04-22 denied.
    assert _decision_days(filled) == 140
    assert _decision_days(still_granted) is None


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, _rows())
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["converge-decision-dates"])
    assert dry.exit_code == 0, dry.output
    assert "would converge 3 denied petition(s) missing a decision date" in dry.output
    applied = runner.invoke(app, ["converge-decision-dates", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "converged 3 denied petition(s) missing a decision date" in applied.output
    assert _decided(db, "scotus/66721476") == date(2019, 4, 22)


def test_cli_fails_loud_without_a_corpus(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-decision-dates", "--apply"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.output
