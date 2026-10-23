"""The cert-stage amicus count: its cut, its column, and the stat-pack cut built on it."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.cert_amicus import (
    cert_amicus_briefs,
    cert_amicus_briefs_before,
    cert_stage_entries,
)
from fedcourtsai.pipeline.cert_signals import proceedings_entries
from fedcourtsai.pipeline.ingest import from_live_record, map_live_docket, to_corpus_row
from fedcourtsai.pipeline.interim_signals import amicus_briefs
from fedcourtsai.schemas import Disposition, GroupBy
from tests.conftest import FixtureCorpus

runner = CliRunner()

_PETITION = ("Jan 09 2026", "Petition for a writ of certiorari filed.")
_CERT_AMICI = (
    ("Feb 10 2026", "Brief amicus curiae of Cato Institute filed."),
    ("Feb 11 2026", "Brief amici curiae of Professors of Law, et al. filed."),
    # Submitted, then accepted: one brief, counted once by the shared reading.
    ("Feb 12 2026", "Amicus brief of Pilots Union submitted."),
    ("Feb 13 2026", "Brief amicus curiae of Pilots Union filed."),
)
_GRANT = ("Jun 01 2026", "Petition GRANTED.")
_MERITS_AMICI = (
    ("Jul 15 2026", "Brief amicus curiae of Chamber of Commerce filed."),
    ("Jul 16 2026", "Brief for the United States as amicus curiae supporting petitioners filed."),
    ("Jul 17 2026", "Brief amici curiae of States of Ohio, et al. filed."),
)


def _payload(*entries: tuple[str, str], number: str = "25-700") -> dict[str, object]:
    return {
        "CaseNumber": f"{number} ",
        "ProceedingsandOrder": [{"Date": d, "Text": t, "Links": []} for d, t in entries],
    }


def _entries(*entries: tuple[str, str]) -> list[tuple[str, str | None]]:
    return proceedings_entries(_payload(*entries))


# --- the count -------------------------------------------------------------------


def test_the_count_is_the_interim_reading_over_the_cert_stage() -> None:
    entries = _entries(_PETITION, *_CERT_AMICI)
    # One reading, two cuts: an open petition's cert stage is its whole docket,
    # so the cert count and the interim count agree entry for entry.
    assert cert_amicus_briefs(entries) == amicus_briefs([t for t, _ in entries]) == 3


def test_a_granted_cases_merits_amici_never_reach_the_cert_count() -> None:
    granted = _entries(_PETITION, *_CERT_AMICI, _GRANT, *_MERITS_AMICI)
    assert cert_amicus_briefs(granted) == 3
    # The disposing entry ends the cut and is not in it.
    assert cert_stage_entries(granted)[-1][1] == "Feb 13 2026"


def test_the_cut_is_positional_so_an_undated_merits_amicus_stays_out() -> None:
    undated_after = _entries(_PETITION, _GRANT, ("", "Brief amicus curiae of Cato filed."))
    assert cert_amicus_briefs(undated_after) == 0
    # Undated at the cert stage still counts at disposition.
    undated_before = _entries(_PETITION, ("", "Brief amicus curiae of Cato filed."), _GRANT)
    assert cert_amicus_briefs(undated_before) == 1


def test_a_denied_petition_stops_at_the_denial() -> None:
    denied = _entries(
        _PETITION,
        _CERT_AMICI[0],
        ("Mar 02 2026", "Petition DENIED."),
        ("Mar 20 2026", "Brief amicus curiae of Cato Institute in support of rehearing filed."),
    )
    assert cert_amicus_briefs(denied) == 1


def test_the_count_only_grows_as_an_open_docket_does() -> None:
    """Max-latch compatible: each prefix of an append-only docket counts no more."""
    full = (_PETITION, *_CERT_AMICI, _GRANT, *_MERITS_AMICI)
    counts = [cert_amicus_briefs(_entries(*full[:n])) for n in range(len(full) + 1)]
    assert counts == sorted(counts)
    assert counts[-1] == 3


def test_the_prediction_side_count_is_strictly_before_the_cutoff() -> None:
    entries = _entries(_PETITION, *_CERT_AMICI, _GRANT, *_MERITS_AMICI)
    assert cert_amicus_briefs_before(entries, date(2026, 2, 10)) == 0
    # The entry dated on the cutoff is out, as it is out of a cell cut there.
    assert cert_amicus_briefs_before(entries, date(2026, 2, 11)) == 1
    assert cert_amicus_briefs_before(entries, date(2026, 2, 12)) == 2
    # The submission is a brief the docket was handed, then deduped on acceptance.
    assert cert_amicus_briefs_before(entries, date(2026, 2, 13)) == 3
    assert cert_amicus_briefs_before(entries, date(2026, 2, 14)) == 3
    # A cutoff past the grant still never reaches the merits amici.
    assert cert_amicus_briefs_before(entries, date(2026, 12, 1)) == 3


def test_the_prediction_side_count_leaves_an_undated_entry_out() -> None:
    entries = _entries(_PETITION, ("", "Brief amicus curiae of Cato filed."))
    assert cert_amicus_briefs_before(entries, date(2026, 12, 1)) == 0
    assert cert_amicus_briefs(entries) == 1


# --- the column --------------------------------------------------------------------


def test_the_live_cert_branch_latches_the_count_at_ingest() -> None:
    payload = _payload(_PETITION, *_CERT_AMICI, _GRANT, *_MERITS_AMICI)
    row = to_corpus_row(from_live_record(map_live_docket(payload, 70_000_001, form="cert")))
    assert row.cert_amicus_briefs == 3
    # The interim column stays the application branch's alone.
    assert row.amicus_briefs is None


def test_a_payload_without_proceedings_writes_no_count() -> None:
    payload: dict[str, object] = {"CaseNumber": "25-700 "}
    row = to_corpus_row(from_live_record(map_live_docket(payload, 70_000_002, form="cert")))
    assert row.cert_amicus_briefs is None


def test_the_application_branch_writes_no_cert_count() -> None:
    payload = _payload(
        ("Jan 09 2026", "Application (25A700) for a stay, submitted to Justice Kagan."),
        ("Jan 12 2026", "Brief amicus curiae of Cato Institute filed."),
        number="25A700",
    )
    row = to_corpus_row(from_live_record(map_live_docket(payload, 70_000_003, form="application")))
    assert row.cert_amicus_briefs is None
    assert row.amicus_briefs == 1


def _scotus_row(**kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {"case_id": "scotus/70", "court": "scotus", "docket_number": "25-70"}
    return corpus.CorpusRow(**{**base, **kw})


def test_the_column_migrates_and_max_latches(tmp_path: Path) -> None:
    pre = tmp_path / "pre-change.db"
    legacy = sqlite3.connect(pre)
    columns = ",\n".join(
        f"{name} {ddl}"
        for name, ddl in corpus._CASES_COLUMN_DDL.items()
        if name != "cert_amicus_briefs"
    )
    legacy.executescript(
        f"CREATE TABLE cases ({columns});\n"
        "INSERT INTO cases (case_id, court, docket_number) VALUES "
        "('scotus/70', 'scotus', '25-70');"
    )
    legacy.commit()
    legacy.close()
    with corpus.connect(pre) as conn:
        migrated = corpus.get_row(conn, "scotus/70")
        assert migrated is not None and migrated.cert_amicus_briefs is None
        corpus.upsert_rows(conn, [_scotus_row(cert_amicus_briefs=4)])
        # A degraded parse's confident 0, and a writer carrying nothing, both
        # leave the stored count where it was.
        corpus.upsert_rows(conn, [_scotus_row(cert_amicus_briefs=0)])
        corpus.upsert_rows(conn, [_scotus_row()])
        kept = corpus.get_row(conn, "scotus/70")
        assert kept is not None and kept.cert_amicus_briefs == 4
        corpus.upsert_rows(conn, [_scotus_row(cert_amicus_briefs=6)])
        grown = corpus.get_row(conn, "scotus/70")
    assert grown is not None and grown.cert_amicus_briefs == 6


def test_the_column_is_withheld_from_the_retrieval_surface() -> None:
    assert "cert_amicus_briefs" in corpus.RETRIEVAL_WITHHELD_COLUMNS
    assert "cert_amicus_briefs" not in corpus.prior_payload(_scotus_row(cert_amicus_briefs=2))


# --- the stat-pack cut -------------------------------------------------------------


def _segment_row(case_id: str, number: str, **kw: object) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=number,
        last_live_polled=date(2026, 7, 1),
        **kw,
    )


def test_the_amicus_cut_buckets_the_paid_scored_segment(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _segment_row(
                    "scotus/1",
                    "24-100",
                    disposition=Disposition.denied,
                    sample_weight=5,
                    cert_amicus_briefs=0,
                ),
                _segment_row(
                    "scotus/2",
                    "24-101",
                    disposition=Disposition.granted,
                    sample_weight=1,
                    cert_amicus_briefs=1,
                ),
                _segment_row(
                    "scotus/3",
                    "24-102",
                    disposition=Disposition.granted,
                    sample_weight=1,
                    cert_amicus_briefs=7,
                ),
                _segment_row("scotus/4", "24-103", sample_weight=1, cert_amicus_briefs=2),
                # Never cert-parsed since the column existed: unknown, not zero.
                _segment_row("scotus/5", "24-104", disposition=Disposition.denied, sample_weight=1),
                # IFP: outside the paid scored segment, so in no bucket.
                _segment_row(
                    "scotus/6",
                    "24-5100",
                    disposition=Disposition.denied,
                    sample_weight=1,
                    cert_amicus_briefs=3,
                ),
            ],
        )
    section = analytics.cert_amicus_section(corpus_db_path=db)
    assert section.title == "Cert petitions by amicus-brief count (paid scored segment)"
    assert (section.group_by, section.weighted, section.cert_stage, section.live_slice) == (
        GroupBy.cert_amicus,
        True,
        True,
        True,
    )
    assert {(b.key, b.cases, b.resolved) for b in section.buckets} == {
        ("0", 5, 5),
        ("1", 1, 1),
        ("2+", 2, 1),
        ("(unknown)", 1, 1),
    }
    two_plus = next(b for b in section.buckets if b.key == "2+")
    assert [(d.disposition, d.share) for d in two_plus.dispositions] == [("granted", 1.0)]
    # The timing travels with the numbers.
    assert section.scope_note is not None
    assert "at the petition's disposition" in section.scope_note
    assert "merits" in section.scope_note


def test_the_amicus_cut_shares_the_relist_cuts_population() -> None:
    spec = analytics._CERT_BY_AMICUS_PAID
    relist = analytics._CERT_BY_RELIST_PAID
    assert (spec.court, spec.cert_stage, spec.live_slice, spec.weighted, spec.row_filter) == (
        relist.court,
        relist.cert_stage,
        relist.live_slice,
        relist.weighted,
        relist.row_filter,
    )


def test_the_amicus_cut_is_not_rendered_into_the_statpack(
    fixture_corpus: FixtureCorpus,
) -> None:
    """Cells read the statpack, and the column is mostly unfilled until a
    re-derivation runs, so the cut is built but kept out of the pack."""
    assert analytics._CERT_BY_AMICUS_PAID not in analytics._STATPACK_SECTIONS
    assert analytics._CERT_BY_AMICUS_PAID not in analytics._DOCKET_SECTIONS
    pack = analytics.build_statpack(corpus_db_path=fixture_corpus.db_path)
    assert all(section.group_by != GroupBy.cert_amicus for section in pack.sections)


def test_an_absent_corpus_yields_the_empty_cut(tmp_path: Path) -> None:
    section = analytics.cert_amicus_section(corpus_db_path=tmp_path / "missing.db")
    assert section.buckets == []


def test_stats_does_not_offer_the_amicus_cut(fixture_corpus: FixtureCorpus) -> None:
    # `stats` is a cell's tool, and the column is withheld from what a cell reads.
    assert GroupBy.cert_amicus not in analytics.STATS_DIMENSIONS
    result = runner.invoke(app, ["stats", "--group-by", "cert_amicus"])
    assert result.exit_code == 2
    assert "Unknown --group-by 'cert_amicus'" in result.stderr
