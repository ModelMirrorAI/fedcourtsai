"""Tests for corpus base-rate aggregation (``fedcourts stats`` / :mod:`analytics`).

Run over the deterministic synthetic corpus (``fixture_corpus``): six cases across
ca9 / ca1 / scotus, four resolved (granted / two denied / dismissed) and two open, so
the base-rate math has known answers.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics
from fedcourtsai.analytics import AnalyticsQuery
from fedcourtsai.cli import app
from fedcourtsai.schemas import AnalyticsReport, BaseRateBucket, Disposition, GroupBy
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _report(fc: FixtureCorpus, **kwargs: object) -> AnalyticsReport:
    return analytics.run_analytics(corpus_db_path=fc.db_path, query=AnalyticsQuery(**kwargs))


def _bucket(report: AnalyticsReport, key: str) -> BaseRateBucket:
    return next(b for b in report.buckets if b.key == key)


def _shares(bucket: BaseRateBucket) -> dict[str, float]:
    return {d.disposition: d.share for d in bucket.dispositions}


def test_overall_base_rates(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus)
    assert not report.skipped
    assert report.group_by is None
    assert report.buckets == []
    total = report.total
    assert (total.cases, total.resolved, total.open) == (6, 4, 2)
    # Base rate over the 4 resolved cases: denied 2/4, dismissed 1/4, granted 1/4.
    assert _shares(total) == {"denied": 0.5, "dismissed": 0.25, "granted": 0.25}
    # Most common first; the two count-1 labels tie-break alphabetically.
    assert [d.disposition for d in total.dispositions] == ["denied", "dismissed", "granted"]


def test_group_by_court(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, group_by=GroupBy.court)
    assert report.group_by == "court"
    # Buckets sort by case count descending: ca9 (3), scotus (2), ca1 (1).
    assert [(b.key, b.cases) for b in report.buckets] == [("ca9", 3), ("scotus", 2), ("ca1", 1)]
    assert _shares(_bucket(report, "ca9")) == {"denied": 0.5, "granted": 0.5}
    assert _shares(_bucket(report, "scotus")) == {"denied": 1.0}
    assert _shares(_bucket(report, "ca1")) == {"dismissed": 1.0}


def test_group_by_term_year_parses_scotus_only(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, court="scotus", group_by=GroupBy.term_year)
    assert {b.key for b in report.buckets} == {"2022", "2024"}
    assert _shares(_bucket(report, "2022")) == {"denied": 1.0}
    # The open 2024 petition has no realized disposition, so no base rate.
    two_four = _bucket(report, "2024")
    assert (two_four.resolved, two_four.open) == (0, 1)
    assert two_four.dispositions == []


def test_group_by_judge_is_multivalued(fixture_corpus: FixtureCorpus) -> None:
    # A panel puts a case in each judge's bucket, so bucket cases exceed the 6 total.
    report = _report(fixture_corpus, group_by=GroupBy.judge)
    assert sum(b.cases for b in report.buckets) > report.total.cases
    # smith sits on ca9/101 (granted) and ca9/102 (denied).
    assert _shares(_bucket(report, "smith")) == {"denied": 0.5, "granted": 0.5}
    # berzon sits on ca9/101 (granted) and the open ca9/103.
    berzon = _bucket(report, "berzon")
    assert (berzon.cases, berzon.resolved) == (2, 1)
    assert _shares(berzon) == {"granted": 1.0}


def test_filter_topic(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, topic="civil rights")
    # ca9/101 (granted) and the open ca9/103 share the topic.
    assert (report.total.cases, report.total.resolved, report.total.open) == (2, 1, 1)
    assert _shares(report.total) == {"granted": 1.0}


def test_filter_judge_overlap(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, judges=["smith"])
    assert report.total.cases == 2
    assert _shares(report.total) == {"denied": 0.5, "granted": 0.5}


def test_filter_date_window(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, date_from=date(2024, 1, 1))
    # Filed on/after 2024-01-01: ca9/103, scotus/304 (denied), scotus/305 — one resolved.
    assert (report.total.cases, report.total.resolved) == (3, 1)
    assert _shares(report.total) == {"denied": 1.0}


def test_resolved_only_drops_open(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, resolved_only=True)
    assert (report.total.cases, report.total.resolved, report.total.open) == (4, 4, 0)


def test_filter_disposition(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, disposition=Disposition.denied)
    # ca9/102 and scotus/304 are the two denied cases.
    assert report.total.cases == 2
    assert _shares(report.total) == {"denied": 1.0}


def test_deterministic(fixture_corpus: FixtureCorpus) -> None:
    first = _report(fixture_corpus, group_by=GroupBy.court)
    second = _report(fixture_corpus, group_by=GroupBy.court)
    assert first.model_dump_json() == second.model_dump_json()


def test_absent_corpus_is_skipped(tmp_path: Path) -> None:
    report = analytics.run_analytics(
        corpus_db_path=tmp_path / "absent.db", query=AnalyticsQuery(group_by=GroupBy.court)
    )
    assert report.skipped
    assert report.group_by == "court"
    assert report.total.cases == 0


def test_render_markdown_grouped_and_skipped() -> None:
    skipped = analytics.render_markdown(AnalyticsReport(skipped=True))
    assert "No corpus present" in skipped

    report = AnalyticsReport(
        group_by=GroupBy.court,
        total=BaseRateBucket(cases=2, resolved=2),
        buckets=[BaseRateBucket(key="ca9", cases=2, resolved=2)],
    )
    md = analytics.render_markdown(report)
    assert "## Corpus analytics" in md
    assert "### By court" in md
    assert "| ca9 |" in md


# --- CLI ---------------------------------------------------------------------


def _stdout_report(output: str) -> dict[str, object]:
    return json.loads(output)  # type: ignore[no-any-return]


def test_cli_stats_overall(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0, result.output
    report = _stdout_report(result.stdout)
    total = report["total"]
    assert isinstance(total, dict)
    assert (total["cases"], total["resolved"], total["open"]) == (6, 4, 2)


def test_cli_stats_group_by_court(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--group-by", "court"])
    assert result.exit_code == 0, result.output
    report = _stdout_report(result.stdout)
    buckets = report["buckets"]
    assert isinstance(buckets, list)
    assert [b["key"] for b in buckets] == ["ca9", "scotus", "ca1"]


def test_cli_summary_out_appends(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    result = runner.invoke(app, ["stats", "--group-by", "court", "--summary-out", str(summary)])
    assert result.exit_code == 0, result.output
    text = summary.read_text()
    assert "## Corpus analytics" in text
    assert "### By court" in text


def test_cli_bad_group_by_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--group-by", "nope"])
    assert result.exit_code == 2
    assert "Unknown --group-by" in result.stderr


def test_cli_bad_disposition_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--disposition", "nope"])
    assert result.exit_code == 2
    assert "Unknown disposition" in result.stderr


def test_cli_bad_date_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--date-from", "not-a-date"])
    assert result.exit_code == 2
    assert "Bad date" in result.stderr


def test_cli_absent_corpus_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0, result.output
    assert _stdout_report(result.stdout)["skipped"] is True
