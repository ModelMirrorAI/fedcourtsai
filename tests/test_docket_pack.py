"""Tests for the court-facing docket pack (``fedcourts docket`` / :mod:`analytics`).

Uses the same deterministic synthetic corpus as the statpack tests
(``fixture_corpus``): seven cases across ca9 / ca1 / scotus, five resolved and
two open, with two live-slice SCOTUS petitions — ``scotus/304`` a walker-sampled
paid denial at weight 5 (OT22, one relist) and ``scotus/305`` a pending paid
poller row at weight 1 (OT24, CVSG on file) — plus discovery cursors (OT22 paid
complete at 850, OT22 IFP partial at 460, OT24 paid partial at 12), so the
pooled per-Term census and the fee-class cut both have real material. The
``scotus/306`` stay application is a live-slice row too, so it counts in the
coverage block while joining no cert section — the cut every cert assertion
here is scoped to.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
from fedcourtsai.analytics import _DOCKET_SECTIONS, _STATPACK_SECTIONS
from fedcourtsai.cli import app
from fedcourtsai.schemas import (
    Disposition,
    DocketPack,
    GroupBy,
    QpTopicAgreement,
    QpTopicLabel,
    QpTopicLabelAgreement,
    QpTopicLabelEntry,
    QpTopicLabels,
    QpTopicShadow,
    StatPackSection,
)
from fedcourtsai.serialize import write_json
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _pack(db_path: Path, qp_topics_path: Path | None = None) -> DocketPack:
    return analytics.build_docket_pack(corpus_db_path=db_path, qp_topics_path=qp_topics_path)


def _section(pack: DocketPack, title: str) -> StatPackSection:
    return next(s for s in pack.sections if s.title == title)


def test_docket_sections_are_court_facing_only() -> None:
    # The artifact's contract: docket composition, never a statement about which
    # petitions this project predicts. The salience band is the one statpack cut
    # that is such a statement, so it must not appear here — and the fee-class
    # cut, which the statpack does not publish, must.
    titles = [spec.title for spec in _DOCKET_SECTIONS]
    assert not any("salience" in title.lower() for title in titles)
    assert "Cert petitions by fee class (paid vs IFP)" in titles
    # `_SectionSpec` is frozen, so a cut published by both artifacts compares equal
    # only while every scope flag agrees — the drift this catches.
    assert set(_DOCKET_SECTIONS) & set(_STATPACK_SECTIONS)
    # EVERY section is reweighted, not merely the cert-stage ones. Scoping this to
    # `cert_stage` was the earlier mistake, and it left the two overview cuts —
    # where nearly every labeled SCOTUS row is a sampled one — publishing a raw
    # split that overstated the grant family several-fold. This artifact exists to
    # be quoted, so an unweighted section anywhere in it is the bug.
    unweighted = [spec.title for spec in _DOCKET_SECTIONS if not spec.weighted]
    assert not unweighted, f"court-facing sections must be reweighted: {unweighted}"


def test_build_docket_pack_headline_and_sections(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus.db_path)
    assert (pack.corpus_rows, pack.resolved, pack.open) == (7, 5, 2)
    assert [s.title for s in pack.sections] == [spec.title for spec in _DOCKET_SECTIONS]
    # Coverage denominators span the whole live slice (the application row
    # included), even though the cert sections aggregate only the petitions.
    assert pack.coverage.live_slice_rows == 3
    assert pack.coverage.live_slice_resolved == 2
    assert pack.coverage.census_filings == 1322  # 850 + 460 + 12


def test_fee_class_section_splits_the_numbering_streams(tmp_path: Path) -> None:
    # Paid petitions number from 1 and IFP from 5001, so the class is exact from
    # the docket number; the section is denial-reweighted like the other cert
    # cuts, so a sampled denial counts for the serials it stands in for.
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
                    sample_weight=1,
                    distribution_count=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-5100",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=4,
                    distribution_count=1,
                ),
            ],
        )
    fees = _section(_pack(db), "Cert petitions by fee class (paid vs IFP)")
    assert (fees.group_by, fees.weighted, fees.cert_stage) == (GroupBy.fee_class, True, True)
    assert [(b.key, b.cases, b.resolved) for b in fees.buckets] == [("ifp", 4, 4), ("paid", 1, 1)]
    paid = next(b for b in fees.buckets if b.key == "paid")
    assert [(d.disposition, d.share) for d in paid.dispositions] == [("granted", 1.0)]


def test_fee_class_keeps_an_unreadable_docket_number_visible(tmp_path: Path) -> None:
    # An annotated docket number is still a modern cert petition, but the fee
    # class cannot be read from it. It joins `(none)` rather than being dropped
    # or guessed into a stream, so the cut's coverage gap stays on the page.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-7255 *** CAPITAL CASE ***",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=1,
                )
            ],
        )
    fees = _section(_pack(db), "Cert petitions by fee class (paid vs IFP)")
    assert [(b.key, b.cases) for b in fees.buckets] == [("(none)", 1)]


def test_per_term_census_pools_the_fee_streams(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus.db_path)
    assert [t.term for t in pack.terms] == [2024, 2022]

    ot22 = next(t for t in pack.terms if t.term == 2022)
    # Both OT22 streams were probed, so filings sum them; the IFP walk is still
    # partial, so the Term as a whole is not complete.
    assert ot22.filings == 1310
    assert ot22.complete is False
    assert (ot22.ingested, ot22.resolved, ot22.weighted_resolved) == (1, 1, 5)
    assert ot22.est_grant_rate == 0.0  # a resolved denial, reweighted to five
    # The pooled cross-Term series carries the same value under the shared name.
    assert ot22.est_grant_family_rate == 0.0
    assert ot22.grants == 0 and ot22.median_days_to_grant is None

    ot24 = next(t for t in pack.terms if t.term == 2024)
    # Only the paid stream has been probed, so filings count it alone.
    assert ot24.filings == 12
    assert (ot24.ingested, ot24.resolved) == (1, 0)
    assert ot24.est_grant_rate is None  # nothing resolved yet
    assert ot24.est_grant_family_rate is None  # no rate at all, not 0%


def test_a_term_is_complete_only_when_every_probed_stream_is(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 24, "paid", 100)
        corpus.set_live_frontier(conn, 24, "paid", 100)
        corpus.set_live_cursor(conn, 24, "ifp", 5400)
        corpus.set_live_cursor(conn, 23, "paid", 90)
        corpus.set_live_frontier(conn, 23, "paid", 90)
    pack = _pack(db)
    by_term = {t.term: t for t in pack.terms}
    # OT24: paid walked to its frontier, IFP not — partial overall.
    assert by_term[2024].complete is False
    assert by_term[2024].filings == 100 + 400
    # OT23: the one probed stream reached its frontier.
    assert by_term[2023].complete is True
    # A cursor-only Term still appears, with zero ingested rows, so the gap shows.
    assert by_term[2023].ingested == 0


def test_gvr_counts_as_a_grant_in_the_term_grant_rate(tmp_path: Path) -> None:
    # A GVR grants the petition, so it joins the grant family in the census rate.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-10",
                    disposition=Disposition.gvr,
                    date_filed=date(2024, 10, 1),
                    date_cert_granted=date(2025, 1, 6),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=1,
                )
            ],
        )
    term = next(t for t in _pack(db).terms if t.term == 2024)
    assert term.est_grant_rate == 1.0
    assert term.est_grant_family_rate == 1.0  # the pooled series counts a gvr too
    assert term.grants == 1
    assert term.median_days_to_grant == 97.0
    # Pace to grant states the subset it was computed over, not the grant count.
    assert term.dated_grants == 1


def test_build_docket_pack_absent_corpus_is_empty_with_scaffolding(tmp_path: Path) -> None:
    pack = _pack(tmp_path / "absent.db")
    assert (pack.corpus_rows, pack.resolved, pack.open) == (0, 0, 0)
    assert pack.coverage.census_filings is None
    assert [s.title for s in pack.sections] == [spec.title for spec in _DOCKET_SECTIONS]
    assert all(s.buckets == [] for s in pack.sections)
    assert [(s.live_slice, s.weighted) for s in pack.sections] == [
        (spec.live_slice, spec.weighted) for spec in _DOCKET_SECTIONS
    ]


def test_build_docket_pack_is_deterministic(fixture_corpus: FixtureCorpus) -> None:
    db = fixture_corpus.db_path
    assert _pack(db).model_dump_json() == _pack(db).model_dump_json()
    assert analytics.render_docket_markdown(_pack(db)) == analytics.render_docket_markdown(
        _pack(db)
    )


def test_committed_docket_pack_still_parses() -> None:
    # The committed artifact must always validate under the current model.
    # Shape-agnostic on purpose: it regenerates on its own cadence, so this pins
    # parseability rather than which vintage is committed.
    committed = Path(__file__).resolve().parents[1] / "metrics" / "docket.json"
    pack = DocketPack.model_validate_json(committed.read_text())
    assert pack.corpus_rows > 0


def test_render_docket_markdown_carries_scope_and_sample_size(
    fixture_corpus: FixtureCorpus,
) -> None:
    md = analytics.render_docket_markdown(_pack(fixture_corpus.db_path))
    assert md.startswith("# Docket pack")
    assert "**Corpus.** 7 case(s): 5 resolved, 2 open." in md
    assert "**Live/historical slice.** 3 case(s), 2 resolved" in md
    assert "1322 docketed filing(s)" in md
    # Every section states its own scope, and every base rate its denominator.
    assert "## Cert petitions by fee class (paid vs IFP)" in md
    assert (
        "_Scope: scotus, modern discretionary-cert dockets, live/historical slice; "
        "counts are denial-reweighted estimates._" in md
    )
    assert "| paid | 6 | 5 | 1 | denied 100.0% (est. n=5) |" in md
    # The per-Term census pools the streams and states the sample size inline.
    assert "## SCOTUS cert petitions by Term" in md
    assert "| 2022 | 1310 | 1 | 0.0% (est. n=5) | 0 | — | partial |" in md
    assert "| 2024 | 12 | 1 | — | 0 | — | partial |" in md
    # The overview cuts are reweighted too, so they say `est. n=` like the rest.
    # A plain `n=` anywhere in a breakdown would mean a raw rate had reappeared
    # over the sampled frame, which is what this artifact must never publish.
    overview = md.split("## Cases by court")[1].split("##")[0]
    assert "est. n=" in overview
    assert "(n=" not in overview


def test_render_docket_markdown_makes_no_prediction_claim(fixture_corpus: FixtureCorpus) -> None:
    # The artifact is readable by someone with no interest in the models, so the
    # prediction-facing vocabulary is absent from the document — the salience
    # program and the scoring machinery are never named at all.
    md = analytics.render_docket_markdown(_pack(fixture_corpus.db_path)).lower()
    for term in ("salience", "leaderboard", "brier", "evaluator", "accuracy score"):
        assert term not in md
    # The replay reading instruction is the deliberate exception: it is a leakage
    # control on the document's own per-Term rates, not a claim about how the
    # models perform, and the artifact ships into every cell's checkout.
    assert "backtest" in md
    # The lead paragraph disclaims the prediction vocabulary, so the stricter
    # check is on the figures themselves: nothing from the first table onward
    # reports how the models did.
    body = md.split("\n## ", 1)[1]
    for term in ("predictor", "accuracy", "calibration", "prediction"):
        assert term not in body


def test_render_docket_markdown_carries_the_replay_self_selection_rule(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The rendered document lands in every cell's checkout beside statpack.md, so
    # its unbounded per-Term grant rates need the same self-selection rule: a
    # time-masked cell anchors only on Terms strictly before its clock. Without
    # it the artifact would be a per-Term outcome surface that silently opts out
    # of the discipline its sibling states.
    md = analytics.render_docket_markdown(_pack(fixture_corpus.db_path))
    assert "anchor only on Term rows strictly preceding your clock" in md
    # It sits under the Term table, not at the foot of the document.
    assert md.index("anchor only on Term rows") < md.index("## Not yet included")


def test_render_docket_markdown_names_the_gaps(fixture_corpus: FixtureCorpus) -> None:
    # The statistics a reader expects and this corpus cannot compute are named,
    # so a citation is never read as a claim that the figure is zero.
    md = analytics.render_docket_markdown(_pack(fixture_corpus.db_path))
    assert "## Not yet included" in md
    assert "claim taxonomy" in md
    assert "Summary reversals" in md
    # The grant-family comparability caveat still rides with the gaps — the same
    # constant the statpack renders under its Term table.
    assert "**The `granted` / `gvr` split is not comparable across Terms.**" in md


def test_render_docket_markdown_empty() -> None:
    md = analytics.render_docket_markdown(DocketPack())
    assert md.startswith("# Docket pack")
    assert "Empty — no corpus present" in md


def test_cli_docket_writes_both_files(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    json_out = tmp_path / "docket.json"
    md_out = tmp_path / "docket.md"
    result = runner.invoke(app, ["docket", "--out", str(json_out), "--markdown-out", str(md_out)])
    assert result.exit_code == 0, result.output
    pack = DocketPack.model_validate_json(json_out.read_text())
    assert pack.corpus_rows == 7
    assert md_out.read_text().startswith("# Docket pack")


def test_cli_docket_absent_corpus_writes_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    result = runner.invoke(app, ["docket"])
    assert result.exit_code == 0, result.output
    pack = DocketPack.model_validate_json((tmp_path / "metrics/docket.json").read_text())
    assert pack.corpus_rows == 0
    assert "Empty — no corpus present" in (tmp_path / "metrics/docket.md").read_text()


def test_the_reader_cut_names_state_courts_and_reweights_them(tmp_path: Path) -> None:
    """The docket pack's by-originating-court cut is a *separate* spec from the
    statpack's, not the same one with a flag: it keys on the raw lower-court name
    so state courts appear by name, and it reweights so the rate is a population
    estimate. Both halves matter, and both are asserted here — dropping either
    was previously invisible to every test in this file.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # A sampled denial: weight 10 in the pack, one row on hand.
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-10",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=10,
                    distribution_count=1,
                    originating_court_name="Supreme Court of Nevada",
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="25-11",
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=1,
                    originating_court_name="Supreme Court of Nevada",
                ),
            ],
        )
    docket = _pack(db)
    reader = _section(docket, "Petitions by originating court (incl. state courts)")
    # Named, not collapsed into `(none)` — the key_fn is doing its work.
    (nevada,) = [b for b in reader.buckets if b.key == "Supreme Court of Nevada"]
    # Reweighted: the sampled denial stands in for ten, so 11 cases not 2.
    assert nevada.cases == 11
    shares = {str(d.disposition): d.share for d in nevada.dispositions}
    assert shares[Disposition.denied.value] > shares[Disposition.granted.value]
    # The statpack's sibling cut is raw over the same rows — that contrast is the
    # reason the two specs exist separately.
    statpack = analytics.build_statpack(corpus_db_path=db)
    raw = next(
        s
        for s in statpack.sections
        if s.title == "Petitions by originating court (incl. state courts)"
    )
    (raw_nevada,) = [b for b in raw.buckets if b.key == "Supreme Court of Nevada"]
    assert raw_nevada.cases == 2


def _qp_corpus(db: Path) -> None:
    """Three modern live-slice cert petitions, so a labeled subset is a real subset."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/{serial}",
                    court="scotus",
                    docket_number=f"24-{serial}",
                    disposition=disposition,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=weight,
                    distribution_count=1,
                )
                for serial, disposition, weight in (
                    (101, Disposition.granted, 1),
                    (102, Disposition.denied, 4),
                    (103, Disposition.denied, 4),
                )
            ],
        )


def _qp_labels(path: Path, primaries: dict[str, QpTopicLabel], *, gate_passed: bool = True) -> Path:
    """Write a labels artifact for ``case_id -> primary``, through the real model."""
    artifact = QpTopicLabels(
        labeler="stub-labeler",
        cases=len(primaries),
        agreement=QpTopicAgreement(
            overall_agree=170,
            overall_n=189,
            overall_rate=170 / 189,
            uncovered=2,
            floor=0.25,
            per_label=[
                QpTopicLabelAgreement(label="criminal-law", agree=35, n=39, rate=35 / 39),
                QpTopicLabelAgreement(label="tax", agree=2, n=2),
            ],
            gate_passed=gate_passed,
        ),
        shadow=QpTopicShadow(texts=len(primaries), fired=0, disagreements=0),
        entries=[
            QpTopicLabelEntry(
                case_id=case_id, docket_number=case_id.removeprefix("scotus/"), label=label
            )
            for case_id, label in sorted(primaries.items())
        ],
    )
    write_json(path, artifact)
    return path


def test_docket_pack_omits_the_topic_cut_without_a_labels_artifact(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # No labeler has run, so the pack is exactly what it was: no cut, and the gap
    # bullet that says the distribution is not computed is still true.
    for path in (None, tmp_path / "absent.json"):
        pack = _pack(fixture_corpus.db_path, path)
        assert pack.qp_topics is None
        assert [s.title for s in pack.sections] == [spec.title for spec in _DOCKET_SECTIONS]
        assert "claim taxonomy" in analytics.render_docket_markdown(pack)


def test_qp_topic_cut_buckets_primaries_over_the_labeled_rows_only(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _qp_corpus(db)
    labels = _qp_labels(
        tmp_path / "qp-topics.json",
        {"scotus/101": "criminal-law", "scotus/103": "unclassifiable"},
    )
    pack = _pack(db, labels)
    assert pack.qp_topics is not None
    section = pack.qp_topics.section
    # Same scope as the neighbouring cert cuts, and reweighted like every other
    # section in this artifact — a raw share over the walker's sampled frame would
    # misreport the topic mix exactly where denials dominate it.
    assert (section.court, section.cert_stage, section.live_slice, section.weighted) == (
        "scotus",
        True,
        True,
        True,
    )
    assert section.group_by == GroupBy.qp_topic
    # `scotus/102` carries no label, so it is out of the cut's population entirely
    # rather than joining a `(none)` bucket: no one asked what it is about.
    # `unclassifiable` is a bucket like any other — dropping it would inflate every
    # other share.
    assert [(b.key, b.cases) for b in section.buckets] == [
        ("unclassifiable", 4),  # a sampled denial, reweighted
        ("criminal-law", 1),
    ]
    # The provenance a quoted share needs travels with it: who labeled, how well
    # they agreed with the reference rater, the rate a constant labeler would
    # score (without which an agreement rate is unreadable), what went uncovered,
    # the join health, and the labels the reference set cannot measure.
    assert (pack.qp_topics.labeler, pack.qp_topics.agree, pack.qp_topics.n) == (
        "stub-labeler",
        170,
        189,
    )
    assert (pack.qp_topics.floor, pack.qp_topics.uncovered) == (0.25, 2)
    assert (pack.qp_topics.labeled_cases, pack.qp_topics.matched_cases) == (2, 2)
    # The cut rides beside `sections`, never inside it: a share lifted from the
    # sections array would leave its labeler and its caveat behind.
    assert [s.title for s in pack.sections] == [spec.title for spec in _DOCKET_SECTIONS]
    # `tax` carries no rate in the artifact — under the reference support floor —
    # so the cut names it as uncertified by the headline figure.
    assert pack.qp_topics.unmeasured_labels == ["tax"]


def test_qp_topic_cut_is_absent_when_no_labeled_case_joins_a_row(tmp_path: Path) -> None:
    # Labels produced against a different corpus vintage join nothing. Publishing
    # an empty table *and* dropping the gap bullet would leave the document
    # silent in the one state a reader most needs it named in, so there is no cut.
    db = tmp_path / "corpus.db"
    _qp_corpus(db)
    labels = _qp_labels(tmp_path / "qp-topics.json", {"scotus/999": "criminal-law"})
    pack = _pack(db, labels)
    assert pack.qp_topics is None
    assert "claim taxonomy" in analytics.render_docket_markdown(pack)


def test_qp_topic_cut_refuses_a_labels_artifact_that_failed_the_gate(tmp_path: Path) -> None:
    # `fedcourts qp-topics` declines to write a failing run, but the artifact
    # records the flag either way and a hand-copied file is what the flag is for:
    # a below-gate labeler publishes nothing.
    db = tmp_path / "corpus.db"
    _qp_corpus(db)
    labels = _qp_labels(
        tmp_path / "qp-topics.json", {"scotus/101": "criminal-law"}, gate_passed=False
    )
    pack = _pack(db, labels)
    assert pack.qp_topics is None
    assert "claim taxonomy" in analytics.render_docket_markdown(pack)


def test_qp_topic_cut_renders_with_its_mandatory_scope_string(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _qp_corpus(db)
    labels = _qp_labels(
        tmp_path / "qp-topics.json",
        {"scotus/101": "criminal-law", "scotus/103": "unclassifiable"},
    )
    md = analytics.render_docket_markdown(_pack(db, labels))
    assert "## Cert petitions by question-presented topic (`qp-topic-v0`)" in md
    # The caveat travels inline with real numbers, because a section-level caveat
    # does not survive a quoted figure (`docs/qp-topic.md`). Two of the three
    # walked cert rows carry a label.
    # The mandated string leads and stays contiguous, so it is quotable whole; the
    # counts are ingested rows, which this document distinguishes from walked ones.
    assert (
        "_Scope: scotus, modern discretionary-cert dockets, live/historical slice; "
        "counts are denial-reweighted estimates. QP-bearing rows only — 2 of 3 ingested "
        "rows; grant-enriched; primaries only; not docket-representative." in md
    )
    assert "no reweighting recovers the docket" in md
    assert "not comparable to the sections above" in md
    assert (
        "A naive share partly counts coordinated filing campaigns rather than subjects; "
        "no de-duplicated companion is published._" in md
    )
    # Reweighted like every other section, so its denominators are estimates.
    assert "| unclassifiable | 4 | 4 | 0 | denied 100.0% (est. n=4) |" in md
    # Agreement, never accuracy, and never without the constant-labeler floor: on a
    # sixteen-label vocabulary most of any rate is the floor, and only the distance
    # from it is skill.
    assert (
        "matched the `qp-topic-v0` reference rater on 170 of 189 reference case(s) (89.9%), "
        "against the 25.0% a constant labeler scores on the same entries" in md
    )
    assert "**agreement, not accuracy**" in md
    assert "2 reference entr(ies) went uncovered" in md
    assert "2 of 2 labeled case(s) joined a row" in md
    # The labels the reference set cannot measure are named beside the table that
    # publishes their shares.
    assert "Per-label agreement is **unmeasured in v0** for `tax`" in md
    # The gap bullet said no labeler had run; one has, so it goes. The other gaps
    # are untouched.
    assert "claim taxonomy" not in md
    assert "Summary reversals" in md
    assert "**The `granted` / `gvr` split is not comparable across Terms.**" in md


def test_qp_topic_cut_publishes_no_secondary_or_vehicle_facet(tmp_path: Path) -> None:
    # `docs/qp-topic.md` holds both out of every published cut while the reference
    # set leaves them unmeasured, so a labeled secondary must change nothing about
    # what the cut counts.
    db = tmp_path / "corpus.db"
    _qp_corpus(db)
    path = tmp_path / "qp-topics.json"
    plain = _pack(db, _qp_labels(path, {"scotus/101": "criminal-law"}))
    artifact = QpTopicLabels.model_validate_json(path.read_text())
    faceted = artifact.model_copy(
        update={
            "entries": [
                entry.model_copy(update={"secondary": "civil-procedure", "vehicle": True})
                for entry in artifact.entries
            ]
        }
    )
    write_json(path, faceted)
    assert plain.qp_topics is not None
    assert _pack(db, path).qp_topics == plain.qp_topics


def test_cli_docket_renders_the_topic_cut_from_the_data_root(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # The command defaults to the artifact `fedcourts qp-topics` writes, so the cut
    # appears without a flag as soon as a labeler run lands.
    _qp_labels(
        fixture_corpus.data_root / "qp-topics" / "qp-topics.json", {"scotus/304": "criminal-law"}
    )
    json_out = tmp_path / "docket.json"
    md_out = tmp_path / "docket.md"
    result = runner.invoke(app, ["docket", "--out", str(json_out), "--markdown-out", str(md_out)])
    assert result.exit_code == 0, result.output
    pack = DocketPack.model_validate_json(json_out.read_text())
    assert pack.qp_topics is not None
    assert [b.key for b in pack.qp_topics.section.buckets] == ["criminal-law"]


def test_cli_docket_refuses_a_named_labels_path_that_does_not_exist(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # The default path is allowed to be absent — that is the standing state until
    # a labeler run lands — but a path typed on the command line is checked, so a
    # typo cannot quietly publish the pack without its cut.
    result = runner.invoke(app, ["docket", "--qp-topics", str(tmp_path / "typo.json")])
    assert result.exit_code == 2


def test_the_pack_states_its_corpus_vintage(fixture_corpus: FixtureCorpus) -> None:
    """A citable artifact has to say what it read. The vintage is the corpus's own
    high-water `last_pulled`, never a clock, so the pack stays a pure function of
    its input and two runs over one corpus agree.
    """
    pack = _pack(fixture_corpus.db_path)
    rendered = analytics.render_docket_markdown(pack)
    if pack.corpus_through is None:
        assert "pulled through" not in rendered
    else:
        assert f"pulled through {pack.corpus_through.isoformat()}" in rendered
