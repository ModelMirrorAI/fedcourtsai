"""Tests for the corpus base-rate statpack (``fedcourts statpack`` / :mod:`analytics`).

Uses the deterministic synthetic corpus (``fixture_corpus``): six cases across
ca9 / ca1 / scotus, four resolved and two open.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
from fedcourtsai.analytics import _STATPACK_SECTIONS
from fedcourtsai.cli import app
from fedcourtsai.schemas import Disposition, StatPack, StatPackSection
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _pack(fc: FixtureCorpus) -> StatPack:
    return analytics.build_statpack(corpus_db_path=fc.db_path)


def _section(pack: StatPack, title: str) -> StatPackSection:
    return next(s for s in pack.sections if s.title == title)


def test_build_statpack_headline_and_sections(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus)
    assert (pack.corpus_rows, pack.resolved, pack.open) == (6, 4, 2)
    # All four resolved fixture cases carry concrete labels and date pairs.
    assert (pack.machine_readable_resolved, pack.dated_resolved) == (4, 4)
    # Overall base rate over the four resolved cases.
    shares = {d.disposition: d.share for d in pack.overall.dispositions}
    assert shares == {"denied": 0.5, "dismissed": 0.25, "granted": 0.25}
    # One section per curated breakdown, in order.
    assert [s.title for s in pack.sections] == [t for t, _, _, _ in _STATPACK_SECTIONS]


def test_build_statpack_court_breakdown(fixture_corpus: FixtureCorpus) -> None:
    by_court = _section(_pack(fixture_corpus), "Cases by court")
    assert by_court.court is None
    assert by_court.group_by == "court"
    assert [(b.key, b.cases) for b in by_court.buckets] == [("ca9", 3), ("scotus", 2), ("ca1", 1)]


def test_build_statpack_overall_timing(fixture_corpus: FixtureCorpus) -> None:
    timing = _pack(fixture_corpus).timing
    # The four resolved cases all carry date pairs: 168, 319, 525, and 546 days.
    assert timing.cases == 4
    assert timing.mean_days == pytest.approx(389.5)
    assert timing.median_days == 319.0  # nearest-rank: ceil(0.5 x 4) = rank 2
    assert timing.p90_days == 546.0  # nearest-rank: ceil(0.9 x 4) = rank 4


def test_build_statpack_per_term_entries(fixture_corpus: FixtureCorpus) -> None:
    terms = _pack(fixture_corpus).terms
    # One entry per parseable SCOTUS Term, most recent first.
    assert [t.term for t in terms] == [2024, 2022]
    open_term, resolved_term = terms
    assert (open_term.base_rates.cases, open_term.base_rates.open) == (1, 1)
    assert open_term.timing.cases == 0  # nothing resolved yet
    assert (resolved_term.base_rates.cases, resolved_term.base_rates.resolved) == (1, 1)
    assert {d.disposition for d in resolved_term.base_rates.dispositions} == {"denied"}
    # scotus/304 filed 2024-01-08, denied 2024-06-24: 168 days.
    assert resolved_term.timing.cases == 1
    assert resolved_term.timing.median_days == 168.0


def test_build_statpack_originating_circuit_scorecard(fixture_corpus: FixtureCorpus) -> None:
    scorecard = _section(_pack(fixture_corpus), "SCOTUS petitions by originating circuit")
    assert scorecard.court == "scotus"
    assert scorecard.group_by == "originating_court"
    # Both fixture petitions came up from ca9; one resolved (denied), one open.
    assert [(b.key, b.cases, b.resolved, b.open) for b in scorecard.buckets] == [("ca9", 2, 1, 1)]


def test_build_statpack_absent_corpus_is_empty_with_scaffolding(tmp_path: Path) -> None:
    pack = analytics.build_statpack(corpus_db_path=tmp_path / "absent.db")
    assert (pack.corpus_rows, pack.resolved, pack.open) == (0, 0, 0)
    assert pack.overall.cases == 0
    # The section scaffolding is kept (empty buckets) so the artifact shape is stable.
    assert [s.title for s in pack.sections] == [t for t, _, _, _ in _STATPACK_SECTIONS]
    assert all(s.buckets == [] for s in pack.sections)


def test_build_statpack_dated_share_counts(tmp_path: Path) -> None:
    # The dated share reads on the machine-readable resolved slice only: `other`
    # rows fall out of the denominator, dateless rows out of the numerator, and a
    # SCOTUS row dated only at the cert stage still counts as dated.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="ca9/1",
                    court="ca9",
                    disposition=Disposition.denied,
                    date_decided=date(2024, 6, 1),
                ),
                corpus.CorpusRow(case_id="ca4/2", court="ca4", disposition=Disposition.denied),
                corpus.CorpusRow(
                    case_id="ca4/3",
                    court="ca4",
                    disposition=Disposition.other,
                    date_decided=date(2024, 6, 1),
                ),
                corpus.CorpusRow(
                    case_id="scotus/4",
                    court="scotus",
                    docket_number="22-451",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2023, 1, 9),
                ),
                corpus.CorpusRow(case_id="ca9/5", court="ca9"),  # open: untouched
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    assert pack.machine_readable_resolved == 3
    assert pack.dated_resolved == 2


def test_build_statpack_is_deterministic(fixture_corpus: FixtureCorpus) -> None:
    assert _pack(fixture_corpus).model_dump_json() == _pack(fixture_corpus).model_dump_json()


def test_render_statpack_markdown_non_empty(fixture_corpus: FixtureCorpus) -> None:
    md = analytics.render_statpack_markdown(_pack(fixture_corpus))
    assert md.startswith("# Corpus statpack")
    assert "**6** case(s): 4 resolved, 2 open." in md
    assert "**Dated share:** 4 of 4 machine-readable resolved case(s)" in md
    assert "## Cases by court" in md
    assert "| ca9 |" in md
    # Headline timing line and the per-Term detail table (recent first).
    assert "median 319d, p90 546d (mean 389.5d over 4 dated case(s))" in md
    assert "## SCOTUS petitions by Term" in md
    assert "| 2024 | 1 | 0 | 1 |" in md
    assert "| 2022 | 1 | 1 | 0 | denied 100.0% | 168 | 168 |" in md
    assert "## SCOTUS petitions by originating circuit" in md


def test_render_statpack_markdown_empty() -> None:
    md = analytics.render_statpack_markdown(StatPack())
    assert "# Corpus statpack" in md
    assert "Empty — no corpus present" in md


def test_cli_statpack_writes_both_files(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    json_out = tmp_path / "statpack.json"
    md_out = tmp_path / "statpack.md"
    result = runner.invoke(app, ["statpack", "--out", str(json_out), "--markdown-out", str(md_out)])
    assert result.exit_code == 0, result.output
    # The JSON validates as a StatPack, and the Markdown carries the rendered doc.
    pack = StatPack.model_validate_json(json_out.read_text())
    assert pack.corpus_rows == 6
    assert md_out.read_text().startswith("# Corpus statpack")


def test_cli_statpack_absent_corpus_writes_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    result = runner.invoke(app, ["statpack"])
    assert result.exit_code == 0, result.output
    pack = StatPack.model_validate_json((tmp_path / "metrics/statpack.json").read_text())
    assert pack.corpus_rows == 0
    assert "Empty — no corpus present" in (tmp_path / "metrics/statpack.md").read_text()


def test_build_statpack_era_and_cert_stage_sections(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus)
    era = _section(pack, "SCOTUS cases by era")
    # Both fixture SCOTUS petitions carry 2020s Term-prefixed docket numbers.
    assert [(b.key, b.cases) for b in era.buckets] == [("2020s", 2)]
    cert = _section(pack, "Modern discretionary-cert petitions by disposition")
    assert cert.cert_stage is True and cert.court == "scotus"
    # One resolved (denied) and one open modern cert petition.
    assert {(b.key, b.cases) for b in cert.buckets} == {("denied", 1), ("(open)", 1)}
