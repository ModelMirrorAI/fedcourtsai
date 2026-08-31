"""Tests for corpus base-rate aggregation (``fedcourts stats`` / :mod:`analytics`).

Run over the deterministic synthetic corpus (``fixture_corpus``): seven cases across
ca9 / ca1 / scotus, five resolved (two granted / two denied / dismissed) and two open —
the resolved grants are ca9/101 and the scotus/306 stay application — so the
base-rate math has known answers.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
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
    assert (total.cases, total.resolved, total.open) == (7, 5, 2)
    # Base rate over the 5 resolved cases: denied 2/5, granted 2/5, dismissed 1/5.
    assert _shares(total) == {"denied": 0.4, "granted": 0.4, "dismissed": 0.2}
    # Most common first; the two count-2 labels tie-break alphabetically.
    assert [d.disposition for d in total.dispositions] == ["denied", "granted", "dismissed"]


def test_group_by_court(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, group_by=GroupBy.court)
    assert report.group_by == "court"
    # Buckets sort by case count descending, the ca9/scotus tie alphabetically.
    assert [(b.key, b.cases) for b in report.buckets] == [("ca9", 3), ("scotus", 3), ("ca1", 1)]
    assert _shares(_bucket(report, "ca9")) == {"denied": 0.5, "granted": 0.5}
    # scotus resolves the denied petition (304) and the granted application (306).
    assert _shares(_bucket(report, "scotus")) == {"denied": 0.5, "granted": 0.5}
    assert _shares(_bucket(report, "ca1")) == {"dismissed": 1.0}


def test_group_by_term_year_parses_scotus_only(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, court="scotus", group_by=GroupBy.term_year)
    # The application docket's A-form number ("26A11") parses no modern cert
    # Term, so it shares the visible (none) bucket rather than minting one.
    assert {b.key for b in report.buckets} == {"2022", "2024", "(none)"}
    assert _shares(_bucket(report, "2022")) == {"denied": 1.0}
    # The open 2024 petition has no realized disposition, so no base rate.
    two_four = _bucket(report, "2024")
    assert (two_four.resolved, two_four.open) == (0, 1)
    assert two_four.dispositions == []


def test_group_by_judge_is_multivalued(fixture_corpus: FixtureCorpus) -> None:
    # A panel puts a case in each judge's bucket, so bucket cases exceed the 7 total.
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
    # Filed on/after 2024-01-01: ca9/103, scotus/304 (denied), scotus/305, and
    # the scotus/306 application (granted) — two resolved.
    assert (report.total.cases, report.total.resolved) == (4, 2)
    assert _shares(report.total) == {"denied": 0.5, "granted": 0.5}


def test_group_by_originating_court_keeps_unlinked_visible(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, group_by=GroupBy.originating_court)
    # Only the two SCOTUS petitions carry the lower-court linkage (both from ca9);
    # the five unlinked cases share the (none) bucket so coverage stays visible.
    assert [(b.key, b.cases) for b in report.buckets] == [("(none)", 5), ("ca9", 2)]
    ca9 = _bucket(report, "ca9")
    assert (ca9.resolved, ca9.open) == (1, 1)
    assert _shares(ca9) == {"denied": 1.0}


def test_group_by_cert_signal_dimensions(fixture_corpus: FixtureCorpus) -> None:
    # The statpack's cert-signal cuts ride the same `_KEY_FNS` table, so
    # `fedcourts stats --group-by` gets them for free. Unweighted here — the
    # report is a raw-count view; weighting is the statpack's concern.
    relists = _report(fixture_corpus, court="scotus", group_by=GroupBy.relist_bucket)
    # scotus/304 had two distributions (one relist); scotus/305 one (zero). The
    # scotus/306 application carries no parsed cert signals (nobody looks on an
    # application docket), so it reads (unknown), never zero.
    assert {(b.key, b.cases) for b in relists.buckets} == {("0", 1), ("1", 1), ("(unknown)", 1)}
    cvsg = _report(fixture_corpus, court="scotus", group_by=GroupBy.cvsg)
    assert {(b.key, b.cases) for b in cvsg.buckets} == {
        ("cvsg", 1),
        ("none", 1),
        ("(unknown)", 1),
    }
    fee = _report(fixture_corpus, court="scotus", group_by=GroupBy.fee_class)
    # Both fixture petitions are paid-stream serials (845 and 12 < 5001); the
    # A-form application docket has no fee class and stays visible as (none).
    assert [(b.key, b.cases) for b in fee.buckets] == [("paid", 2), ("(none)", 1)]


def test_group_by_capital_case_buckets_the_unpolled_as_unknown(
    fixture_corpus: FixtureCorpus,
) -> None:
    # `capital_case` is a plain boolean column, but only supremecourt.gov serves
    # the marking it is latched from, so a row no live poll ever stamped reads
    # False for want of a writer. Bucketing that row as `unmarked` would read a
    # coverage gap as an absence of capital cases, so `last_live_polled` gates
    # the key: the four bulk-import circuit rows land in `(unknown)`, and only
    # the three live-slice SCOTUS rows can assert anything at all.
    report = _report(fixture_corpus, group_by=GroupBy.capital_case)
    assert [(b.key, b.cases) for b in report.buckets] == [("(unknown)", 4), ("unmarked", 3)]


def test_group_by_capital_case_separates_the_three_states(tmp_path: Path) -> None:
    # The full vocabulary on one corpus: a marked petition, a polled petition
    # the marking never reached, and an unpolled row that can say neither. The
    # denominator a capital rate is taken over is the first two only — which is
    # the whole point of keeping the third in its own bucket.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-100",
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 7, 1),
                    capital_case=True,
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-101",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                ),
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="24-102",
                    disposition=Disposition.denied,
                ),
            ],
        )
    report = analytics.run_analytics(
        corpus_db_path=db, query=AnalyticsQuery(group_by=GroupBy.capital_case)
    )
    assert sorted((b.key, b.cases) for b in report.buckets) == [
        ("(unknown)", 1),
        ("capital", 1),
        ("unmarked", 1),
    ]
    # The separation is the measurable claim: the marked petition's grant is not
    # diluted by the row that was never looked at.
    assert _shares(_bucket(report, "capital")) == {"granted": 1.0}


def test_filter_term_is_scotus_only(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, term=2022)
    # Only scotus/304 ("22-845") is Term 2022. The ca9 dockets ("22-15001",
    # "22-15044") coincidentally parse to 2022 but a Term is a SCOTUS concept.
    assert (report.total.cases, report.total.resolved) == (1, 1)
    assert _shares(report.total) == {"denied": 1.0}


def test_filter_term_open_petition(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, term=2024)
    assert (report.total.cases, report.total.resolved, report.total.open) == (1, 0, 1)


def test_group_by_era_buckets_by_decade(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, group_by=GroupBy.era)
    # Every fixture case is a 2020s matter (Term year or filing date).
    assert [(b.key, b.cases) for b in report.buckets] == [("2020s", 7)]


def test_filter_era(fixture_corpus: FixtureCorpus) -> None:
    assert _report(fixture_corpus, era="2020s").total.cases == 7
    assert _report(fixture_corpus, era="1890s").total.cases == 0


def test_filter_cert_stage_keeps_modern_cert_dockets_only(fixture_corpus: FixtureCorpus) -> None:
    # Only the two Term-prefixed SCOTUS petitions survive the cert-stage cut; the
    # court-of-appeals dockets (whose numbers coincidentally parse) never match.
    report = _report(fixture_corpus, cert_stage=True)
    total = report.total
    assert (total.cases, total.resolved, total.open) == (2, 1, 1)
    assert _shares(total) == {"denied": 1.0}


def test_resolved_only_drops_open(fixture_corpus: FixtureCorpus) -> None:
    report = _report(fixture_corpus, resolved_only=True)
    assert (report.total.cases, report.total.resolved, report.total.open) == (5, 5, 0)


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
    assert (total["cases"], total["resolved"], total["open"]) == (7, 5, 2)


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


def test_cli_stats_term_filter(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--term", "2022"])
    assert result.exit_code == 0, result.output
    report = _stdout_report(result.stdout)
    total = report["total"]
    assert isinstance(total, dict)
    assert (total["cases"], total["resolved"]) == (1, 1)


def test_cli_bad_term_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--term", "OT24"])
    assert result.exit_code == 2
    assert "Bad --term" in result.stderr


def test_cli_bad_group_by_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--group-by", "nope"])
    assert result.exit_code == 2
    assert "Unknown --group-by" in result.stderr
    # The refusal is half of discoverability: it must name the real set — the
    # dimensions keyed off a corpus row, which is what this command can compute.
    for dimension in analytics.STATS_DIMENSIONS:
        assert dimension.value in result.stderr


def test_stats_group_by_help_lists_every_dimension() -> None:
    """`--help` is how a cell agent discovers the cuts it can ask for, so a
    dimension the command accepts but the help omits is invisible in practice.

    Asserted against the joined accepted set rather than value-by-value: five of the
    dimensions (`court`, `topic`, `judge`, `era`, `disposition`) also name
    *other* options on the page, so a per-value search would pass even if
    `--group-by` listed none of them.

    Matching rendered output means normalizing what rich does to it, and both
    axes differ between a local shell and CI: a wide `COLUMNS` stops it breaking
    a value mid-word, and the ANSI strip handles colour, which it emits under
    CI's environment but not under a plain local run.
    """
    result = runner.invoke(app, ["stats", "--help"], env={"COLUMNS": "200", "NO_COLOR": "1"})
    assert result.exit_code == 0
    plain = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    rendered = " ".join(plain.replace("│", " ").split())
    assert ", ".join(g.value for g in analytics.STATS_DIMENSIONS) in rendered


def test_the_dispatch_input_advertises_every_dimension() -> None:
    """`run-analytics`'s `group_by` input is the surface a maintainer reads when
    dispatching, and a workflow input description cannot render from the enum —
    so it is pinned here instead, where the CLI help is pinned."""
    described = (Path(".github") / "workflows" / "run-analytics.yml").read_text()
    line = next(li for li in described.splitlines() if "corpus-stats: break base-rates" in li)
    missing = [g.value for g in analytics.STATS_DIMENSIONS if g.value not in line]
    assert not missing, f"the group_by dispatch input omits: {missing}"


@pytest.mark.parametrize("dimension", list(analytics.STATS_DIMENSIONS))
def test_every_advertised_dimension_actually_groups(
    dimension: GroupBy, fixture_corpus: FixtureCorpus
) -> None:
    """Advertised implies works, over the whole accepted set rather than a listed
    subset. `STATS_DIMENSIONS` derives from `_KEY_FNS`, so a member with no key
    function cannot reach an agent as an offered dimension; what this still pins is
    that every offered dimension groups a real corpus without erroring — a key
    function that is registered but broken, or that a filter interaction breaks."""
    result = runner.invoke(app, ["stats", "--group-by", dimension.value])
    assert result.exit_code == 0, result.output


def test_stats_offers_only_the_dimensions_it_can_compute(fixture_corpus: FixtureCorpus) -> None:
    # `qp_topic` keys off a labels artifact, not a corpus row, so `stats` cannot
    # serve it and must not advertise it — offering a `--group-by` the aggregation
    # cannot serve is the failure this pins. It lives beside the other
    # `STATS_DIMENSIONS` tests, where someone adding a dimension will look.
    assert GroupBy.qp_topic not in analytics.STATS_DIMENSIONS
    assert set(analytics.STATS_DIMENSIONS) == set(GroupBy) - {GroupBy.qp_topic}
    result = runner.invoke(app, ["stats", "--group-by", "qp_topic"])
    assert result.exit_code == 2
    assert "Unknown --group-by 'qp_topic'" in result.stderr


def test_the_aggregation_refuses_a_section_dimension_itself(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The CLI screens its own input, but the contract belongs to the aggregation:
    a programmatic caller grouping by an artifact-keyed dimension gets a named
    refusal that lists the servable cuts, not a `KeyError` out of the
    key-function table."""
    with pytest.raises(ValueError, match="artifact, not a corpus row"):
        analytics.run_analytics(
            corpus_db_path=fixture_corpus.db_path,
            query=AnalyticsQuery(group_by=GroupBy.qp_topic),
        )


def test_cli_bad_disposition_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--disposition", "nope"])
    assert result.exit_code == 2
    assert "Unknown disposition" in result.stderr


def test_cli_bad_era_errors(fixture_corpus: FixtureCorpus) -> None:
    # This command answers a base rate rather than returning rows, so an
    # unrecognized era would come back as a well-formed report over zero
    # cases — a number, and the wrong one. `query`'s vocabulary, same refusal.
    result = runner.invoke(app, ["stats", "--era", "Roberts Court"])
    assert result.exit_code == 2
    assert "Unknown era" in result.stderr
    assert "2020s" in result.stderr
    # A real decade still runs, whether or not the fixture holds one.
    assert runner.invoke(app, ["stats", "--era", "1890s"]).exit_code == 0


def test_cli_bad_date_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["stats", "--date-from", "not-a-date"])
    assert result.exit_code == 2
    assert "Bad date" in result.stderr


def test_cli_absent_corpus_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0, result.output
    assert _stdout_report(result.stdout)["skipped"] is True
