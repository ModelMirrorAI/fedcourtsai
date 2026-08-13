"""Tests for the corpus base-rate statpack (``fedcourts statpack`` / :mod:`analytics`).

Uses the deterministic synthetic corpus (``fixture_corpus``): seven cases across
ca9 / ca1 / scotus, five resolved and two open. The two SCOTUS petitions are
live-slice rows — ``scotus/304`` a walker-sampled denial at weight 5 (one
relist), ``scotus/305`` a pending poller row at weight 1 (CVSG on file) — and
``scotus/306`` is a resolved substantive stay application (the interim
docket's row, outside every cert-stage cut). The
fixture carries discovery cursors (OT22 paid complete at 850, OT22 IFP
partial at 460, OT24 paid partial at 12), so the weighted sections, the census,
and the completeness flags all have real material to aggregate.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus, fixture, serialize
from fedcourtsai.analytics import _STATPACK_SECTIONS
from fedcourtsai.cli import app
from fedcourtsai.pipeline.evaluate import merits_base_rate
from fedcourtsai.pipeline.salience import SALIENCE_VERSION, SCORERS, SalienceScorer
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    FeeClass,
    GroupBy,
    StatPack,
    StatPackSection,
    StatPackTerm,
)
from tests.conftest import FixtureCorpus

runner = CliRunner()

_BANDS = ("federal", "high", "state", "elevated", "baseline")


def _pack(fc: FixtureCorpus) -> StatPack:
    return analytics.build_statpack(corpus_db_path=fc.db_path)


def _section(pack: StatPack, title: str) -> StatPackSection:
    return next(s for s in pack.sections if s.title == title)


def _term(pack: StatPack, year: int) -> StatPackTerm:
    return next(t for t in pack.terms if t.term == year)


def test_build_statpack_headline_and_sections(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus)
    assert (pack.corpus_rows, pack.resolved, pack.open) == (7, 5, 2)
    # All five resolved fixture cases carry concrete labels and date pairs.
    assert (pack.machine_readable_resolved, pack.dated_resolved) == (5, 5)
    # Overall base rate over the five resolved cases (raw counts, never weighted).
    shares = {d.disposition: d.share for d in pack.overall.dispositions}
    assert shares == {"denied": 0.4, "granted": 0.4, "dismissed": 0.2}
    # One section per curated breakdown, in order.
    assert [s.title for s in pack.sections] == [spec.title for spec in _STATPACK_SECTIONS]


def test_build_statpack_coverage_block(fixture_corpus: FixtureCorpus) -> None:
    coverage = _pack(fixture_corpus).coverage
    # The two SCOTUS petitions plus the application are the live slice; the
    # denied petition and the granted application are resolved (raw counts).
    assert (coverage.live_slice_rows, coverage.live_slice_resolved) == (3, 2)
    # Census totals across the fixture cursors: OT22 paid 850 + OT22 IFP
    # (5460 - 5001 + 1 = 460) + OT24 paid 12.
    assert coverage.census_filings == 850 + 460 + 12


def test_build_statpack_court_breakdown(fixture_corpus: FixtureCorpus) -> None:
    by_court = _section(_pack(fixture_corpus), "Cases by court")
    assert by_court.court is None
    assert by_court.group_by == "court"
    assert by_court.live_slice is False and by_court.weighted is False
    assert [(b.key, b.cases) for b in by_court.buckets] == [("ca9", 3), ("scotus", 3), ("ca1", 1)]


def test_build_statpack_overall_timing(fixture_corpus: FixtureCorpus) -> None:
    timing = _pack(fixture_corpus).timing
    # The five resolved cases all carry date pairs: 22, 168, 319, 525, and 546 days.
    assert timing.cases == 5
    assert timing.mean_days == pytest.approx(316.0)
    assert timing.median_days == 319.0  # nearest-rank: ceil(0.5 x 5) = rank 3
    assert timing.p90_days == 546.0  # nearest-rank: ceil(0.9 x 5) = rank 5


def test_build_statpack_weighted_cert_anchor(fixture_corpus: FixtureCorpus) -> None:
    # The calibration anchor: live slice, denial-reweighted. scotus/304 (denied,
    # weight 5) counts as five petitions; scotus/305 (open, weight 1) as one.
    cert = _section(_pack(fixture_corpus), "Modern discretionary-cert petitions by disposition")
    assert cert.cert_stage is True and cert.court == "scotus"
    assert cert.live_slice is True and cert.weighted is True
    assert {(b.key, b.cases, b.resolved) for b in cert.buckets} == {
        ("denied", 5, 5),
        ("(open)", 1, 0),
    }


def test_build_statpack_weighted_circuit_cut(fixture_corpus: FixtureCorpus) -> None:
    scorecard = _section(_pack(fixture_corpus), "Modern cert petitions by originating circuit")
    assert scorecard.weighted is True
    # Both live petitions came up from ca9: 5 + 1 weighted cases, 5 resolved.
    assert [(b.key, b.cases, b.resolved, b.open) for b in scorecard.buckets] == [("ca9", 6, 5, 1)]


def test_build_statpack_relist_and_cvsg_cuts(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus)
    relists = _section(pack, "Cert petitions by relist count (paid scored segment)")
    # scotus/304: two distributions = one relist (weight 5); scotus/305: one
    # distribution = zero relists (weight 1).
    assert {(b.key, b.cases) for b in relists.buckets} == {("1", 5), ("0", 1)}
    cvsg = _section(pack, "Cert petitions by CVSG status (paid scored segment)")
    # scotus/305 carries the SG invitation; scotus/304 was parsed and has none.
    assert {(b.key, b.cases) for b in cvsg.buckets} == {("cvsg", 1), ("none", 5)}


def test_build_statpack_salience_band_section(fixture_corpus: FixtureCorpus) -> None:
    # The pack-wide segment board: paid scored segment, live slice, denial-weighted,
    # split by sal-v1 band. scotus/304 (one relist → elevated, weight 5, denied) and
    # scotus/305 (CVSG → high, weight 1, open).
    band = _section(_pack(fixture_corpus), "Cert petitions by salience band")
    assert band.cert_stage is True and band.court == "scotus"
    assert band.live_slice is True and band.weighted is True
    assert band.group_by == "salience_band"
    assert [(b.key, b.cases, b.resolved) for b in band.buckets] == [
        ("elevated", 5, 5),
        ("high", 1, 0),
    ]


def test_salience_band_section_excludes_ifp(fixture_corpus: FixtureCorpus) -> None:
    # An IFP live-slice cert row is Tier-0 excluded from the scored segment, so the
    # row_filter keeps it out of the band section entirely (no bucket, not `(none)`).
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9001",
                    court="scotus",
                    docket_number="24-5900",  # serial 5900 >= 5001 -> IFP
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=2,
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=fixture_corpus.db_path)
    band = _section(pack, "Cert petitions by salience band")
    # Still only the two paid petitions; the IFP row joins no band bucket.
    assert sum(b.cases for b in band.buckets) == 6  # 5 (elevated) + 1 (high)
    assert "(none)" not in {b.key for b in band.buckets}
    # And it never enters a Term's segment counts either.
    term = _term(pack, 2024)
    assert sum(s.ingested for s in term.segments) == 1  # only the paid scotus/305


def test_build_statpack_originating_court_names(fixture_corpus: FixtureCorpus) -> None:
    by_court = _section(
        _pack(fixture_corpus), "Petitions by originating court (incl. state courts)"
    )
    assert by_court.live_slice is True and by_court.weighted is False
    # Raw counts (2 petitions), keyed by the tracked circuit id where mapped.
    assert [(b.key, b.cases) for b in by_court.buckets] == [("ca9", 2)]


def test_state_court_petitions_key_on_the_raw_lower_court_name(tmp_path: Path) -> None:
    # A state-court petition has no tracked-court linkage (`originating_court`
    # None); the reader section falls back to the raw `LowerCourt` name instead
    # of collapsing it into `(none)`.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-10",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=1,
                    originating_court_name="Supreme Court of Nevada",
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="25-11",
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=0,
                ),
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    names = _section(pack, "Petitions by originating court (incl. state courts)")
    assert {(b.key, b.cases) for b in names.buckets} == {
        ("Supreme Court of Nevada", 1),
        ("(none)", 1),
    }


def test_gvr_counts_as_a_grant_in_the_term_grant_rate(tmp_path: Path) -> None:
    # A GVR is a grant: a Term whose only resolved petition is a `gvr` must show
    # a 100% grant rate and one grant, not zero (the regression if the grant
    # aggregation keyed on the literal "granted" label alone).
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
    pack = analytics.build_statpack(corpus_db_path=db)
    term = next(t for t in pack.terms if t.term == 2024)
    assert term.grants == 1  # the gvr row counts as a grant
    # The Term-level pooled series counts the gvr as a grant too.
    assert term.est_grant_family_rate == 1.0
    # The per-fee-class grant rate sums the grant family, so a lone gvr reads 100%.
    paid = next(c for c in term.classes if c.fee_class == "paid")
    assert paid.est_grant_rate == 1.0
    # gvr is tracked as its own disposition bucket, distinct from granted.
    assert {d.disposition for d in term.base_rates.dispositions} == {"gvr"}


def test_term_grant_family_rate_pools_the_split(tmp_path: Path) -> None:
    # `est_grant_family_rate` is the pooled granted+gvr series — the one per-Term
    # disposition figure comparable across Terms — and it must equal the sum of
    # the split's own shares, so the JSON's `dispositions` and the pooled field
    # can never disagree.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-10",
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="25-11",
                    disposition=Disposition.gvr,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="25-12",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=5,
                    distribution_count=1,
                ),
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    term = _term(pack, 2025)
    # granted 1 + gvr 1 over a weighted resolved of 7 (the denial stands in for 5).
    assert term.est_grant_family_rate == pytest.approx(2 / 7)
    assert term.est_grant_family_rate == sum(
        d.share for d in term.base_rates.dispositions if d.disposition in ("granted", "gvr")
    )
    # And the rendered Term row prints the field itself, not a recomputation.
    assert "28.6%" in analytics.render_statpack_markdown(pack)


def test_unparsed_rows_land_in_the_unknown_buckets(tmp_path: Path) -> None:
    # A live-slice row whose signals were never parsed (NULL distribution_count)
    # must read as coverage-unknown on the cert-signal cuts — never as
    # relist-zero or CVSG-none — and its NULL weight counts once.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-10",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    relists = _section(pack, "Cert petitions by relist count (paid scored segment)")
    cvsg = _section(pack, "Cert petitions by CVSG status (paid scored segment)")
    assert [(b.key, b.cases) for b in relists.buckets] == [("(unknown)", 1)]
    assert [(b.key, b.cases) for b in cvsg.buckets] == [("(unknown)", 1)]


def test_live_slice_sections_exclude_bulk_rows(fixture_corpus: FixtureCorpus) -> None:
    # A CourtListener-only SCOTUS row (no live poll stamp) joins the full-corpus
    # sections but none of the live-slice ones.
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/999",
                    court="scotus",
                    docket_number="21-99",
                    disposition=Disposition.granted,
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=fixture_corpus.db_path)
    by_court = _section(pack, "Cases by court")
    assert ("scotus", 4) in {(b.key, b.cases) for b in by_court.buckets}
    cert = _section(pack, "Modern discretionary-cert petitions by disposition")
    assert "granted" not in {b.key for b in cert.buckets}
    # And it defines no Term entry (OT21 has no live rows and no cursors).
    assert {t.term for t in pack.terms} == {2022, 2024}


def test_per_term_entries_carry_census_classes_and_estimates(
    fixture_corpus: FixtureCorpus,
) -> None:
    pack = _pack(fixture_corpus)
    assert [t.term for t in pack.terms] == [2024, 2022]

    resolved_term = _term(pack, 2022)
    # One raw row ingested; weighted base rates count its sampled denial as five.
    assert resolved_term.ingested == 1
    assert (resolved_term.base_rates.cases, resolved_term.base_rates.resolved) == (5, 5)
    assert {d.disposition for d in resolved_term.base_rates.dispositions} == {"denied"}
    # Cert timing keys on date_cert_denied (168 days), weighted.
    assert resolved_term.timing.cases == 5
    assert resolved_term.timing.median_days == 168.0
    assert resolved_term.grants == 0 and resolved_term.median_days_to_grant is None
    # All resolved rows are denials, so the pooled grant-family series is a real 0%.
    assert resolved_term.est_grant_family_rate == 0.0
    paid, ifp = resolved_term.classes
    assert (paid.fee_class, paid.filings, paid.complete) == (FeeClass.paid, 850, True)
    assert (paid.ingested, paid.resolved, paid.weighted_resolved) == (1, 1, 5)
    assert paid.est_grant_rate == 0.0  # resolved petitions, none granted
    assert (ifp.fee_class, ifp.filings, ifp.complete) == (FeeClass.ifp, 460, False)
    assert (ifp.ingested, ifp.weighted_resolved, ifp.est_grant_rate) == (0, 0, None)

    open_term = _term(pack, 2024)
    assert (open_term.base_rates.cases, open_term.base_rates.open) == (1, 1)
    assert open_term.est_grant_family_rate is None  # nothing resolved: no rate, not 0%
    assert open_term.timing.cases == 0  # nothing resolved yet
    paid, ifp = open_term.classes
    assert (paid.filings, paid.complete, paid.ingested) == (12, False, 1)
    assert paid.est_grant_rate is None  # nothing resolved
    assert (ifp.filings, ifp.complete) == (None, False)  # never probed


def test_per_term_segments_carry_the_salience_band_base_rate(
    fixture_corpus: FixtureCorpus,
) -> None:
    pack = _pack(fixture_corpus)
    # Every Term emits all three bands in the fixed strongest-first order, tagged
    # with the frozen scorer version — a stable JSON shape even for empty bands.
    resolved_term = _term(pack, 2022)
    assert resolved_term.salience_version == "sal-v2"
    assert [s.band for s in resolved_term.segments] == list(_BANDS)
    by_band = {s.band: s for s in resolved_term.segments}
    # scotus/304 is one relist -> elevated; its sampled denial weights the rate 5x.
    elevated = by_band["elevated"]
    assert (elevated.ingested, elevated.weighted_resolved) == (1, 5)
    assert elevated.est_grant_rate == 0.0  # weight-5 denial, none granted
    # The other bands hold no rows this Term: zero counts, no rate.
    assert by_band["high"].ingested == 0 and by_band["high"].est_grant_rate is None
    assert by_band["baseline"].ingested == 0 and by_band["baseline"].est_grant_rate is None
    # scotus/305 carries the CVSG invitation -> high band; still open, so no rate yet.
    high_2024 = {s.band: s for s in _term(pack, 2024).segments}["high"]
    assert (high_2024.ingested, high_2024.weighted_resolved) == (1, 0)
    assert high_2024.est_grant_rate is None


def test_segment_base_rate_is_per_term_not_blended(tmp_path: Path) -> None:
    # The leakage crux: a high-band grant in a later Term must NOT lift an earlier
    # Term's high-band rate. Two relist-2 (high) petitions, granted in OT24, denied
    # in OT23 — each Term's segment rate reflects only its own rows.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="23-500",
                    disposition=Disposition.denied,
                    date_filed=date(2023, 10, 1),
                    date_cert_denied=date(2024, 1, 8),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,  # 2 relists -> high band
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-500",
                    disposition=Disposition.granted,
                    date_filed=date(2024, 10, 1),
                    date_cert_granted=date(2025, 1, 6),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,  # 2 relists -> high band
                ),
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    high_23 = {s.band: s for s in _term(pack, 2023).segments}["high"]
    high_24 = {s.band: s for s in _term(pack, 2024).segments}["high"]
    assert high_23.est_grant_rate == 0.0  # OT23: the lone high petition was denied
    assert high_24.est_grant_rate == 1.0  # OT24: the lone high petition was granted


def test_gvr_counts_as_a_grant_in_the_segment_base_rate(tmp_path: Path) -> None:
    # A GVR grants the petition, so a high-band Term whose only resolved petition is
    # a gvr reads a 100% segment grant rate (the grant family, not the literal label).
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-400",
                    disposition=Disposition.gvr,
                    date_filed=date(2024, 10, 1),
                    date_cert_granted=date(2025, 1, 6),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,  # high band
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    high = {s.band: s for s in _term(pack, 2024).segments}["high"]
    assert (high.weighted_resolved, high.est_grant_rate) == (1, 1.0)


def test_cursor_only_term_appears_with_census_and_zero_rows(tmp_path: Path) -> None:
    # A Term the walker has probed but not yet populated (every serial so far
    # sampled out) still shows its census, so coverage is visible.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 23, "historical-paid", 40)
        corpus.set_live_frontier(conn, 23, "historical-paid", 40)
    pack = analytics.build_statpack(corpus_db_path=db)
    assert [t.term for t in pack.terms] == [2023]
    entry = pack.terms[0]
    assert entry.base_rates.cases == 0
    paid, ifp = entry.classes
    assert (paid.filings, paid.complete, paid.ingested) == (40, True, 0)
    assert (ifp.filings, ifp.complete) == (None, False)
    assert pack.coverage.census_filings == 40


def test_census_takes_the_furthest_cursor_in_a_stream_family(tmp_path: Path) -> None:
    # The poller and the walker cover the same serial space under different
    # stream names: the class census is the family max, and completeness reads
    # from the furthest cursor (a stale stamp on the shorter one is ignored).
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 25, "paid", 120)
        corpus.set_live_cursor(conn, 25, "historical-paid", 80)
        corpus.set_live_frontier(conn, 25, "historical-paid", 80)
    pack = analytics.build_statpack(corpus_db_path=db)
    paid = _term(pack, 2025).classes[0]
    assert (paid.filings, paid.complete) == (120, False)


def test_a_grant_records_pace_to_grant(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-7",
                    disposition=Disposition.granted,
                    date_filed=date(2024, 11, 1),
                    date_cert_granted=date(2025, 1, 10),  # 70 days
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=2,
                )
            ],
        )
    entry = _term(analytics.build_statpack(corpus_db_path=db), 2024)
    assert entry.grants == 1
    assert entry.median_days_to_grant == 70.0
    # Cert timing keys on the grant date, not the (absent) merits termination.
    assert entry.timing.cases == 1 and entry.timing.median_days == 70.0


def test_weighted_timing_repeats_the_sampled_denials(tmp_path: Path) -> None:
    # One weight-9 denial at 30 days and one weight-1 grant at 300 days: the
    # weighted median must sit at the denial (rank 5 of 10), not between them.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-10",
                    disposition=Disposition.denied,
                    date_filed=date(2025, 1, 1),
                    date_cert_denied=date(2025, 1, 31),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=9,
                    distribution_count=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-11",
                    disposition=Disposition.granted,
                    date_filed=date(2025, 1, 1),
                    date_cert_granted=date(2025, 10, 28),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=2,
                ),
            ],
        )
    entry = _term(analytics.build_statpack(corpus_db_path=db), 2024)
    assert entry.timing.cases == 10
    assert entry.timing.median_days == 30.0  # rank 5 of the 10-strong expansion
    assert entry.timing.p90_days == 30.0  # rank 9 still lands on the denials
    assert entry.timing.mean_days == pytest.approx(57.0)  # (30 x 9 + 300) / 10
    # And the weighted grant rate is 1/10, not 1/2.
    assert entry.base_rates.resolved == 10
    grant = next(d for d in entry.base_rates.dispositions if d.disposition == "granted")
    assert grant.share == pytest.approx(0.1)


def test_build_statpack_absent_corpus_is_empty_with_scaffolding(tmp_path: Path) -> None:
    pack = analytics.build_statpack(corpus_db_path=tmp_path / "absent.db")
    assert (pack.corpus_rows, pack.resolved, pack.open) == (0, 0, 0)
    assert pack.overall.cases == 0
    assert pack.coverage.census_filings is None
    # The section scaffolding is kept (empty buckets, flags intact) so the
    # artifact shape is stable.
    assert [s.title for s in pack.sections] == [spec.title for spec in _STATPACK_SECTIONS]
    assert all(s.buckets == [] for s in pack.sections)
    assert [(s.live_slice, s.weighted) for s in pack.sections] == [
        (spec.live_slice, spec.weighted) for spec in _STATPACK_SECTIONS
    ]


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


def test_committed_statpack_still_parses() -> None:
    # The committed artifact must always validate under the current model — a
    # model change that orphans it would strand every consumer (agent cells,
    # ops) until the next metrics refresh. Shape-agnostic on purpose: the
    # artifact regenerates on its own cadence, so this pins parseability, not
    # which vintage of the pack is committed (asserting pre-enrichment defaults
    # here would redden the exact refresh PR that fills them).
    committed = Path(__file__).resolve().parents[1] / "metrics" / "statpack.json"
    pack = StatPack.model_validate_json(committed.read_text())
    assert pack.corpus_rows > 0


def test_render_statpack_markdown_non_empty(fixture_corpus: FixtureCorpus) -> None:
    md = analytics.render_statpack_markdown(_pack(fixture_corpus))
    assert md.startswith("# Corpus statpack")
    assert "**7** case(s): 5 resolved, 2 open." in md
    assert "**Live/historical slice:** 3 case(s), 2 resolved" in md
    assert "1322 docketed filing(s)" in md
    assert "**Dated share:** 5 of 5 machine-readable resolved case(s)" in md
    # Full-corpus sections say so; live-slice sections state slice + weighting.
    assert "## Cases by court" in md
    assert "_Scope: all courts; includes the frozen bulk import._" in md
    assert (
        "_Scope: scotus, modern discretionary-cert dockets, live/historical slice; "
        "counts are denial-reweighted estimates._" in md
    )
    assert "median 319d, p90 546d (mean 316.0d over 5 dated case(s))" in md
    # The per-Term table: filings census, raw ingested count, weighted
    # estimates, completeness. OT22 ingested exactly one live row; the weighted
    # columns count its sampled denial as five.
    assert "## SCOTUS cert petitions by Term" in md
    assert "| 2022 | 850/460 | 1 | 5 | denied 100.0% | 0.0% | 0 | 168 | ✓/partial |" in md
    assert "| 2024 | 12/— | 1 | 0 | — | — | 0 | — | partial/partial |" in md
    # The replay self-selection rule rides under the Term table, verbatim.
    assert "anchor only on Term rows strictly preceding your clock" in md
    # The grant-family comparability caveat rides directly under the Term table —
    # the table whose base-rate column prints the `granted` / `gvr` split — before
    # the segment section begins.
    term_section = md.split("## SCOTUS cert petitions by Term")[1]
    assert (
        "**The `granted` / `gvr` split is not comparable across Terms.**"
        in term_section.split("### Segment base rate")[0]
    )


def test_render_statpack_markdown_renders_the_segment_base_rate(
    fixture_corpus: FixtureCorpus,
) -> None:
    md = analytics.render_statpack_markdown(_pack(fixture_corpus))
    # The pack-wide band section (blended) and the leakage-safe per-Term table.
    assert "## Cert petitions by salience band" in md
    assert "### Segment base rate by salience band (sal-v2)" in md
    assert "| Term | federal | high | state | elevated | baseline |" in md
    # OT22's lone scored petition is a weight-5 elevated denial. A cell leads with
    # the scored (terminal) rate and brackets the risk-set one. `high` is empty —
    # nothing reached it. `baseline` carries ONLY a bracket: no row ended there,
    # but this petition passed through it, so it is in that band's risk set. That
    # asymmetry is the whole point of publishing both.
    assert "| 2022 | — | — | — | 0.0% (n=5) [reached 0.0%, n=5] | [reached 0.0%, n=5] |" in md
    # The band table states its own rendered window. The predict/evaluate prompts
    # tell agents that this caption is how they detect truncation, so the count has
    # to sit on THIS table — the parent Term table's caption is a different section.
    band_caption = md.split("### Segment base rate by salience band")[1].split("\n\n")[0]
    assert "Term(s)" in band_caption


def test_render_statpack_markdown_caps_long_sections() -> None:
    # A section with more buckets than the cap renders the top slice plus an
    # explicit overflow line; the JSON carries everything.
    section = StatPackSection(
        title="Petitions by originating court (incl. state courts)",
        court="scotus",
        cert_stage=True,
        live_slice=True,
        group_by=GroupBy.originating_court,
        buckets=[
            BaseRateBucket(key=f"court-{i:03d}", cases=100 - i, resolved=0, open=100 - i)
            for i in range(30)
        ],
    )
    md = analytics.render_statpack_markdown(
        StatPack(corpus_rows=1, overall=BaseRateBucket(cases=1), sections=[section])
    )
    assert "| court-000 |" in md and "| court-024 |" in md
    assert "| court-025 |" not in md
    assert "5 more bucket(s) in the JSON" in md


def _terms_pack(*years: int) -> StatPack:
    return StatPack(
        corpus_rows=1,
        overall=BaseRateBucket(cases=1),
        terms=[StatPackTerm(term=y, base_rates=BaseRateBucket()) for y in years],
    )


def test_render_statpack_markdown_caps_the_term_table() -> None:
    # The per-Term cap is the forward stratum's segment base-rate lookback: the
    # predict/evaluate agents can anchor only on Terms this table renders.
    pack = _terms_pack(*range(2026, 2014, -1))  # 12 Terms
    md = analytics.render_statpack_markdown(pack)
    assert md.count("Most recent 10 of 12 Term(s)") == 2  # the Term table and the band table
    assert "| 2017 |" in md  # the 10th most recent
    assert "| 2016 |" not in md


def test_render_statpack_markdown_zero_markdown_terms_shows_every_term() -> None:
    # `0` means unbounded, as everywhere else in the config; `terms[:0]` would be
    # the empty slice, so the sentinel has to branch.
    md = analytics.render_statpack_markdown(_terms_pack(*range(2026, 2014, -1)), markdown_terms=0)
    assert "Most recent 12 of 12 Term(s)" in md
    assert "| 2015 |" in md


def test_render_statpack_markdown_honours_an_explicit_markdown_terms() -> None:
    md = analytics.render_statpack_markdown(_terms_pack(2025, 2024, 2023), markdown_terms=2)
    assert "Most recent 2 of 3 Term(s)" in md
    assert "| 2023 |" not in md


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
    assert pack.corpus_rows == 7
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


def test_build_statpack_era_section(fixture_corpus: FixtureCorpus) -> None:
    era = _section(_pack(fixture_corpus), "SCOTUS cases by era")
    # Both fixture SCOTUS petitions carry 2020s Term-prefixed docket numbers;
    # the application docket's era derives from its 2026 filing date.
    assert [(b.key, b.cases) for b in era.buckets] == [("2020s", 3)]


def test_the_risk_set_rate_nests_the_terminal_one(fixture_corpus: FixtureCorpus) -> None:
    """The structural invariant behind the forecast baseline.

    A band is monotone non-decreasing over a petition's life, so "has reached band
    b" is the same event as "ended at b or stronger". Two consequences that must
    hold on every Term, and would catch a mis-ordered or mis-indexed risk set:

    * the strongest band has nothing above it, so its risk set IS its terminal
      set — the two rates and denominators coincide exactly;
    * a weaker band's risk set is a superset of its terminal set, so its
      denominator can only grow.
    """
    pack = _pack(fixture_corpus)
    strongest = _BANDS[0]
    for term in pack.terms:
        by_band = {s.band: s for s in term.segments}
        top = by_band[strongest]
        assert top.prefix_weighted_resolved == top.weighted_resolved, term.term
        assert top.prefix_est_grant_rate == top.est_grant_rate, term.term
        for band in _BANDS[1:]:
            seg = by_band[band]
            assert seg.prefix_weighted_resolved >= seg.weighted_resolved, (term.term, band)


def test_the_risk_set_rate_lifts_a_weak_band_that_a_stronger_grant_passed_through(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The defect in one assertion: a petition that ends `elevated` was `baseline`
    when it was first distributed, so it belongs in `baseline`'s risk set. The
    terminal cut drops it, which is what understated that band several-fold."""
    term = _term(_pack(fixture_corpus), 2022)
    by_band = {s.band: s for s in term.segments}
    # OT2022's only scored row is the weight-5 elevated denial (see the segment
    # test above). It ended `elevated`, so `baseline` holds no row that ended
    # there — but the petition passed through `baseline`, so the risk set has it.
    assert by_band["baseline"].weighted_resolved == 0
    assert by_band["baseline"].est_grant_rate is None
    assert by_band["baseline"].prefix_weighted_resolved == 5
    assert by_band["baseline"].prefix_est_grant_rate == 0.0


def test_the_committed_pack_holds_the_risk_set_invariants() -> None:
    """The structural claims, against real bands rather than the 6-row fixture.

    The fixture corpus has no resolved `high` row, so the strongest-band identity
    is vacuous there (0 == 0, None == None). It is the claim the rendered caption
    and both prompts rest on, so it is checked here on the committed artifact,
    which carries every band across nine Terms. These are invariants of the
    construction, not of the current data, so a refresh cannot falsify them.
    """
    pack = StatPack.model_validate_json(Path("metrics/statpack.json").read_text())
    # The committed pack's own vocabulary, not `_BANDS`: the artifact is
    # re-rendered on the refresh after an active-version flip, so between the
    # flip and the refresh the two legitimately disagree. The invariants are
    # structural, so they hold under whichever scorer rendered the file.
    bands = [s.band for s in pack.terms[0].segments]
    # ... but only a vocabulary some registered scorer actually declares — a
    # garbled artifact must not get to define its own bands and pass — and the
    # rendering version must itself be registered, so a stale artifact is at
    # worst a *retired* scorer's view, never an unknown one.
    assert pack.terms[0].salience_version in SCORERS
    assert tuple(bands) in {entry.bands for entry in SCORERS.values()}
    saw_populated_top = False
    for term in pack.terms:
        by_band = {s.band: s for s in term.segments}
        top = by_band[bands[0]]
        # Nothing sits above the strongest band, so its risk set IS its terminal set.
        assert top.prefix_weighted_resolved == top.weighted_resolved, term.term
        assert top.prefix_resolved == top.resolved, term.term
        assert top.prefix_est_grant_rate == top.est_grant_rate, term.term
        if top.weighted_resolved:
            saw_populated_top = True
        # Risk sets nest downward, so each denominator contains every stronger one.
        running = 0
        for band in bands:
            seg = by_band[band]
            running += seg.weighted_resolved
            assert seg.prefix_weighted_resolved == running, (term.term, band)
    assert saw_populated_top, "the identity would be vacuous without a resolved top band"


def test_the_predictor_facing_cuts_are_paid_only(fixture_corpus: FixtureCorpus) -> None:
    """A predict cell's petition is always paid — IFP is excluded at Tier 0 — so a
    cut that pools IFP hands it a level it is never in. IFP petitions relist far
    less often and have never drawn a CVSG, so the pooled level sits below the one
    a selected petition faces, and a cell reading it anchors low."""
    titles = [s.title for s in _pack(fixture_corpus).sections]
    assert "Cert petitions by relist count (paid scored segment)" in titles
    assert "Cert petitions by CVSG status (paid scored segment)" in titles
    # The pooled versions stay off the predictor-facing pack; the court-facing
    # docket pack keeps them, where describing the whole docket is the point.
    assert "Cert petitions by relist count" not in titles  # the pooled cut
    assert "Cert petitions by CVSG status" not in titles


def test_the_docket_pack_warns_that_the_gvr_split_is_not_cross_term_comparable(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The `gvr` label is a forward convention, so two Terms resolved inside the
    window where it did not yet exist carry zero GVRs against 30-59% either side.
    A reader comparing the split across Terms would be reading ingestion history
    as if it were the Court, so the artifact has to say so where it publishes it."""
    md = analytics.render_docket_markdown(
        analytics.build_docket_pack(corpus_db_path=fixture_corpus.db_path)
    )
    assert "not comparable across Terms" in md
    assert "forward convention" in md
    assert "OT2023 and OT2024" in md


# --- The interim stage axis --------------------------------------------------


def _seed_applications(db_path: Path) -> None:
    """Insert a known interim-docket cohort: OT2024-heavy, one OT2023 row.

    OT2024: one granted extension, a granted substantive with every escalation
    signal, a denied substantive with none, an open substantive, an
    unknown-ask row, and a never-parsed row. OT2023: one dismissed substantive.
    """
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/900000001",
                    court="scotus",
                    docket_number="24A1",
                    application_kind="extension",
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900000002",
                    court="scotus",
                    docket_number="24A2",
                    application_kind="substantive",
                    disposition=Disposition.granted,
                    response_requested=True,
                    referred_to_court=True,
                    amicus_briefs=2,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900000003",
                    court="scotus",
                    docket_number="24A3",
                    application_kind="substantive",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900000004",
                    court="scotus",
                    docket_number="24A4",
                    application_kind="substantive",
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900000005",
                    court="scotus",
                    docket_number="24A5",
                    application_kind="unknown",
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900000006",
                    court="scotus",
                    docket_number="24A6",
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900000007",
                    court="scotus",
                    docket_number="23A9",
                    application_kind="substantive",
                    disposition=Disposition.dismissed,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                ),
            ],
        )


def test_interim_section_absent_without_application_rows(tmp_path: Path) -> None:
    # The stage section is shown only once its feed exists: no application rows,
    # no section — omitted from the serialized pack rather than emitted as null,
    # so a pack built from an application-free corpus keeps its pre-axis bytes.
    # The fixture corpus carries an application docket, so build the cert-only
    # slice of it here.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                case.row()
                for case in fixture.FIXTURE_CASES
                # The form recognizer is meaningless off SCOTUS, so gate on the
                # court the way its contract asks callers to.
                if not (
                    case.court == "scotus" and corpus.is_scotus_application_form(case.docket_number)
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    assert pack.interim is None
    assert "interim" not in pack.model_dump(mode="json")
    assert "The interim docket" not in analytics.render_statpack_markdown(pack)


def test_the_committed_pack_reserializes_byte_identically(tmp_path: Path) -> None:
    """The committed artifact must survive a parse → serialize round trip unchanged.

    `write_json` is deterministic and the pack is a pure function of the corpus,
    so this holds by construction — and it is exactly the property a model change
    can silently break (a new field serializing as `null` would perturb every
    rebuild whose corpus does not feed it). Pinned on the committed file, written
    back through the real writer, so the schema and the artifact cannot drift
    apart between refreshes.
    """
    committed = (Path(__file__).resolve().parents[1] / "metrics" / "statpack.json").read_text()
    pack = StatPack.model_validate_json(committed)
    rewritten = tmp_path / "statpack.json"
    serialize.write_json(rewritten, pack)
    assert rewritten.read_text() == committed


def test_interim_counts_by_kind_and_term(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_applications(db)
    interim = analytics.build_statpack(corpus_db_path=db).interim
    assert interim is not None
    # Pack-level kind counts: the never-parsed row is a coverage gap, kept apart
    # from the parsed-but-unreadable `unknown` ask.
    assert (interim.applications, interim.extension, interim.substantive) == (7, 1, 4)
    assert (interim.unknown, interim.unparsed) == (1, 1)
    # Substantive slice only: the granted extension never enters the rate, the
    # open substantive row never enters the denominator, and a dismissal resolves
    # without granting — so 1 granted of 3 resolved.
    assert (interim.substantive_resolved, interim.substantive_granted) == (3, 1)
    assert interim.substantive_grant_rate == pytest.approx(1 / 3)
    # Escalation signals count substantive applications carrying each column.
    assert (interim.response_requested, interim.referred_to_court, interim.with_amicus) == (1, 1, 1)
    # Per-application-Term split, most recent first, read off the A-form number.
    assert [t.term for t in interim.terms] == [2024, 2023]
    ot24, ot23 = interim.terms
    assert (ot24.applications, ot24.substantive_resolved, ot24.substantive_granted) == (6, 2, 1)
    assert ot24.substantive_grant_rate == pytest.approx(0.5)
    assert (ot23.applications, ot23.substantive, ot23.substantive_resolved) == (1, 1, 1)
    assert ot23.substantive_grant_rate == 0.0  # a dismissal resolves, ungranted


def test_interim_rate_is_substantive_only(tmp_path: Path) -> None:
    # A docket of granted extensions has NO rate: extensions are counted so their
    # dominance is visible, but they never pool into any rate (docs/salience.md).
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/90000000{i}",
                    court="scotus",
                    docket_number=f"25A{i}",
                    application_kind="extension",
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                )
                for i in range(1, 4)
            ],
        )
    interim = analytics.build_statpack(corpus_db_path=db).interim
    assert interim is not None
    assert (interim.applications, interim.extension) == (3, 3)
    assert (interim.substantive_resolved, interim.substantive_granted) == (0, 0)
    assert interim.substantive_grant_rate is None  # no rate, not 0% or 100%


def test_interim_out_of_vocabulary_kind_counts_as_unknown(tmp_path: Path) -> None:
    # The blob is external input: a kind string outside the vocabulary must not
    # vanish from the kind split (which would break the sum-to-`applications`
    # identity silently) — it counts with the unreadable asks.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/900000001",
                    court="scotus",
                    docket_number="25A1",
                    application_kind="garbled",
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                )
            ],
        )
    interim = analytics.build_statpack(corpus_db_path=db).interim
    assert interim is not None
    assert (interim.applications, interim.unknown) == (1, 1)
    assert (
        interim.extension + interim.substantive + interim.unknown + interim.unparsed
        == interim.applications
    )


def test_interim_other_disposition_stays_out_of_the_denominator(tmp_path: Path) -> None:
    # An `other` label means "decided, but we do not know how" — it can only
    # reach an application row through a channel crossing, never through the
    # interim vocabulary — so it joins the visibly unresolved residue instead of
    # entering the rate as a silent denial.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/900000001",
                    court="scotus",
                    docket_number="25A1",
                    application_kind="substantive",
                    disposition=Disposition.other,
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                )
            ],
        )
    interim = analytics.build_statpack(corpus_db_path=db).interim
    assert interim is not None
    assert (interim.substantive, interim.substantive_resolved) == (1, 0)
    assert interim.substantive_grant_rate is None


def test_application_rows_leave_the_cert_populations_unchanged(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The stage axis is disjoint from the cert one: an A-form docket defines no
    # cert Term entry and joins no cert-stage section, so seeding applications
    # changes only the full-corpus overview counts and the interim section
    # (which the fixture's own application docket already feeds).
    before = _pack(fixture_corpus)
    _seed_applications(fixture_corpus.db_path)
    after = _pack(fixture_corpus)
    assert after.terms == before.terms
    for prior, current in zip(before.sections, after.sections, strict=True):
        if prior.cert_stage:
            assert current == prior
    assert before.interim is not None and after.interim is not None
    assert after.interim.applications == before.interim.applications + 7


def test_render_statpack_markdown_interim_section(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_applications(db)
    md = analytics.render_statpack_markdown(analytics.build_statpack(corpus_db_path=db))
    assert "## The interim docket (applications)" in md
    # The caption carries the interpretation contract with the figures.
    interim_section = md.split("## The interim docket (applications)")[1]
    assert "resolved substantive" in interim_section
    assert "not a segment base rate" in interim_section
    assert "**7** application(s): 1 extension, 4 substantive" in interim_section
    # Rates print raw-count denominators beside them; per-Term rows carry the
    # kind counts, the substantive-only rate, and the escalation signals.
    assert "**Substantive slice:** 3 resolved, 1 granted — grant rate 33.3% (n=3)." in md
    assert "| 2024 | 6 | 1 | 3 | 1 | 1 | 2 | 1 | 50.0% (n=2) | 1 | 1 | 1 |" in md
    assert "| 2023 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0.0% (n=1) | 0 | 0 | 0 |" in md


# --- The merits stage axis ---------------------------------------------------


def _seed_granted_cohort(db_path: Path) -> None:
    """Insert a known granted-merits cohort split across two grant Terms.

    OT2023 (granted Jan 2024 -> Term 2023): a reversal, a vacatur, an
    affirmance, a DIG — every parsed judgment dated after its grant, as the
    pool guard requires — and a granted row with no parsed judgment (coverage
    gap). OT2024 (granted Oct 2024 -> Term 2024, October pivot): one
    equally-divided affirmance and one mixed in-part outcome. Plus a granted
    row carrying an out-of-vocabulary judgment string (counts as unparsed, so
    the distribution always sums to `parsed`), a denial, a GVR, and a
    stale-labeled GVR (labeled plain `granted`, its vacatur dated on the
    grant itself) — the last three never in the cohort: the labeled GVR
    because its
    vacatur is a cert-stage disposition, the stale-labeled one because the
    label-independent guard reads the same fact off the grant→judgment gap
    and counts it as `cert_order_excluded`.
    """
    ot23 = date(2024, 1, 12)
    ot24 = date(2024, 10, 7)
    rows = [
        corpus.CorpusRow(
            case_id="scotus/910000001",
            court="scotus",
            docket_number="23-201",
            disposition=Disposition.granted,
            date_cert_granted=ot23,
            merits_judgment="reversed",
            merits_decided=date(2024, 6, 27),
        ),
        corpus.CorpusRow(
            case_id="scotus/910000002",
            court="scotus",
            docket_number="23-202",
            disposition=Disposition.granted,
            date_cert_granted=ot23,
            merits_judgment="vacated",
            merits_decided=date(2024, 6, 20),
        ),
        corpus.CorpusRow(
            case_id="scotus/910000003",
            court="scotus",
            docket_number="23-203",
            disposition=Disposition.granted,
            date_cert_granted=ot23,
            merits_judgment="affirmed",
            merits_decided=date(2024, 6, 14),
        ),
        corpus.CorpusRow(
            case_id="scotus/910000004",
            court="scotus",
            docket_number="23-204",
            disposition=Disposition.granted,
            date_cert_granted=ot23,
            merits_judgment="dismissed-as-improvidently-granted",
            merits_decided=date(2024, 5, 20),
        ),
        corpus.CorpusRow(
            case_id="scotus/910000005",
            court="scotus",
            docket_number="23-205",
            disposition=Disposition.granted,
            date_cert_granted=ot23,
        ),
        corpus.CorpusRow(
            case_id="scotus/910000006",
            court="scotus",
            docket_number="24-101",
            disposition=Disposition.granted,
            date_cert_granted=ot24,
            merits_judgment="affirmed-by-an-equally-divided-court",
            merits_decided=date(2025, 5, 12),
        ),
        corpus.CorpusRow(
            case_id="scotus/910000007",
            court="scotus",
            docket_number="24-102",
            disposition=Disposition.granted,
            date_cert_granted=ot24,
            merits_judgment="affirmed-in-part-reversed-in-part",
            merits_decided=date(2025, 6, 2),
        ),
        corpus.CorpusRow(
            case_id="scotus/910000008",
            court="scotus",
            docket_number="24-103",
            disposition=Disposition.granted,
            date_cert_granted=ot24,
            merits_judgment="remanded-with-prejudice",  # out of vocabulary
        ),
        corpus.CorpusRow(
            case_id="scotus/910000009",
            court="scotus",
            docket_number="23-206",
            disposition=Disposition.denied,
            date_cert_denied=ot23,
            merits_judgment="affirmed",  # never eligible: a denial has no merits stage
        ),
        corpus.CorpusRow(
            case_id="scotus/910000010",
            court="scotus",
            docket_number="23-207",
            # A GVR vacates in the cert order itself, so it opens no merits
            # proceeding and must not enter the population — its near-certain
            # vacatur would otherwise read as a disturbed merits judgment.
            disposition=Disposition.gvr,
            date_cert_granted=ot23,
            merits_judgment="vacated",
        ),
        corpus.CorpusRow(
            case_id="scotus/910000011",
            court="scotus",
            docket_number="23-208",
            # The stale-labeled GVR shape: the `gvr` label is a forward
            # convention and labels lag their cert orders (measured, most
            # recently on IFP GVRs), so this row reads plain `granted` —
            # passing the disposition exclusion — while its vacatur rode the
            # cert order and carries the grant's own date. The
            # label-independent guard keeps it out of the cohort entirely,
            # exactly as the labeled GVR above is, and counts it.
            disposition=Disposition.granted,
            date_cert_granted=ot23,
            merits_judgment="vacated",
            merits_decided=ot23,
        ),
    ]
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(conn, rows)


def test_merits_section_absent_without_parsed_judgments(fixture_corpus: FixtureCorpus) -> None:
    # The stage section is shown only once its feed exists: no parsed judgment,
    # no section — omitted from the serialized pack rather than emitted as null,
    # so a pack built from a judgment-free corpus keeps its pre-axis bytes.
    pack = _pack(fixture_corpus)
    assert pack.merits is None
    assert "merits" not in pack.model_dump(mode="json")
    assert "The merits docket" not in analytics.render_statpack_markdown(pack)


def test_merits_section_absent_when_granted_rows_carry_no_judgment(tmp_path: Path) -> None:
    # A granted-but-unparsed cohort is a feed that does not exist yet: the
    # section joins on the parsed judgment, not on the grant.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/910000001",
                    court="scotus",
                    docket_number="23-201",
                    date_cert_granted=date(2024, 1, 12),
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    assert pack.merits is None
    assert "merits" not in pack.model_dump(mode="json")


def test_merits_counts_distribution_and_rate_by_grant_term(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_granted_cohort(db)
    merits = analytics.build_statpack(corpus_db_path=db).merits
    assert merits is not None
    # Pack-level coverage: 8 granted (the denial is not eligible), 6 parsed —
    # the unparsed row and the out-of-vocabulary value are both coverage gaps.
    assert (merits.granted, merits.parsed) == (8, 6)
    assert (merits.affirmed, merits.reversed, merits.vacated) == (1, 1, 1)
    assert (merits.affirmed_in_part, merits.dig, merits.equally_divided) == (1, 1, 1)
    # Disturbed = reversed + vacated + in-part; DIG and equally divided leave
    # the judgment below standing, so both sit in the denominator undisturbed.
    assert merits.disturbed == 3
    assert merits.disturbed_rate == pytest.approx(3 / 6)
    # Per-grant-Term split, most recent first, October pivot: the Oct 2024
    # grants are OT2024, the Jan 2024 grants OT2023.
    assert [t.term for t in merits.terms] == [2024, 2023]
    ot24, ot23 = merits.terms
    assert (ot24.granted, ot24.parsed, ot24.disturbed) == (3, 2, 1)
    assert ot24.disturbed_rate == pytest.approx(0.5)
    assert (ot23.granted, ot23.parsed, ot23.disturbed) == (5, 4, 2)
    assert ot23.disturbed_rate == pytest.approx(0.5)


def test_merits_population_excludes_grants_that_decide_in_the_cert_order(
    tmp_path: Path,
) -> None:
    """A GVR grants the petition and vacates below in one order, so it opens no
    merits proceeding and never mints a merits event to forecast. Pooling it
    would put a near-certain vacatur in the rate that scores merits forecasts,
    inflating the disturbed rate with cases no one was asked to predict."""
    db = tmp_path / "corpus.db"
    _seed_granted_cohort(db)
    merits = analytics.build_statpack(corpus_db_path=db).merits
    assert merits is not None
    # The cohort carries a GVR row stamped `vacated`; neither its grant nor its
    # judgment reaches any counter.
    assert (merits.granted, merits.parsed) == (8, 6)
    assert merits.vacated == 1
    assert merits.disturbed == 3


def test_merits_all_affirmed_term_has_a_real_zero_rate(tmp_path: Path) -> None:
    # An all-affirmed parsed slice is a real 0% — distinct from the no-rate
    # None an unparsed slice carries.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/910000001",
                    court="scotus",
                    docket_number="23-201",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2024, 1, 12),
                    merits_judgment="affirmed",
                    merits_decided=date(2024, 6, 14),
                )
            ],
        )
    merits = analytics.build_statpack(corpus_db_path=db).merits
    assert merits is not None
    assert merits.disturbed_rate == 0.0
    assert merits.terms[0].disturbed_rate == 0.0


def test_merits_rows_leave_live_slice_terms_and_interim_unchanged(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The merits axis is a projection over granted rows, not a new cert
    # population: the seeded (non-live) cohort adds the merits section without
    # moving the live-slice per-Term array or the interim stage section. The
    # full-corpus overview sections legitimately grow — the seeded rows are
    # real corpus rows — so they are deliberately not compared here.
    before = _pack(fixture_corpus)
    _seed_granted_cohort(fixture_corpus.db_path)
    after = _pack(fixture_corpus)
    assert before.merits is None and after.merits is not None
    assert after.terms == before.terms
    assert after.interim == before.interim


def test_render_statpack_markdown_merits_section(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_granted_cohort(db)
    md = analytics.render_statpack_markdown(analytics.build_statpack(corpus_db_path=db))
    assert "## The merits docket (granted cases)" in md
    # The caption carries the interpretation contract with the figures.
    merits_section = md.split("## The merits docket (granted cases)")[1]
    # The caption states the scored contract: the section's own disturbed rate
    # is the registered baseline's feed, over the population it scores.
    assert "registered merits Brier baseline" in merits_section
    assert "excluded by its disposition label" in merits_section
    assert "strictly before" in merits_section
    assert "undisturbed" in merits_section
    assert (
        "**8** granted case(s): 6 with a parsed, dated judgment; 1 excluded by the "
        "pool guard (judgment dated on or before its own grant)." in merits_section
    )
    # Rates print raw-count denominators beside them; per-Term rows carry the
    # coverage pair, the six-way distribution, and the disturbed rate.
    assert "disturbed rate 50.0% (n=6)." in merits_section
    # The excluded column sits between granted and parsed: OT2023 carries the
    # stale-labeled cert-order vacatur the guard removed and counted.
    assert "| 2024 | 3 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 50.0% (n=2) |" in merits_section
    assert "| 2023 | 5 | 1 | 4 | 1 | 1 | 1 | 0 | 1 | 0 | 2 | 50.0% (n=4) |" in merits_section


def _seed_merits_and_gvr_cohort(db_path: Path) -> None:
    """One grant Term holding a merits-bound cohort beside a GVR block.

    The merits-bound rows (`granted` / `granted-in-part` — the dispositions
    that mint a merits event) split 28 disturbed of 40, enough to clear the
    baseline's minimum sample; the 40 GVRs are the near-certain vacaturs the
    scored population is never drawn from.
    """
    granted = date(2024, 1, 12)
    rows = [
        corpus.CorpusRow(
            case_id=f"scotus/9200{n:05d}",
            court="scotus",
            docket_number=f"23-3{n:02d}",
            disposition=Disposition.granted_in_part if n == 0 else Disposition.granted,
            date_cert_granted=granted,
            merits_judgment="reversed" if n < 28 else "affirmed",
            merits_decided=date(2024, 6, 20),
        )
        for n in range(40)
    ] + [
        corpus.CorpusRow(
            case_id=f"scotus/9210{n:05d}",
            court="scotus",
            docket_number=f"23-4{n:02d}",
            disposition=Disposition.gvr,
            date_cert_granted=granted,
            merits_judgment="vacated",
        )
        for n in range(40)
    ]
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(conn, rows)


def test_the_scored_merits_baseline_never_sees_the_gvr_block(tmp_path: Path) -> None:
    """End to end: a GVR block cannot move the rate a merits cell is scored on.

    A GVR mints no merits event, so no merits cell is ever drawn from one.
    Pooling the near-certain GVR vacaturs would anchor every merits forecast
    above the rate its own population faces — the
    baseline-coarser-than-the-conditioning failure
    `docs/outcome-decomposition.md`'s third test rules out — and would restate
    a cert-stage disposition under a merits heading. Excluding them at the
    population is what makes the section's own `disturbed_rate` the baseline's
    feed.
    """
    db = tmp_path / "corpus.db"
    _seed_merits_and_gvr_cohort(db)
    pack = analytics.build_statpack(corpus_db_path=db)
    merits = pack.merits
    assert merits is not None
    assert (merits.granted, merits.parsed, merits.disturbed) == (40, 40, 28)
    assert merits.disturbed_rate == pytest.approx(0.70)
    assert merits.vacated == 0  # every vacatur in the corpus is a GVR's
    # The baseline reads those counts on the grant-Term axis: 0.70, not the
    # (28 + 40) / 80 = 0.85 a GVR-inclusive population would hand out.
    assert merits_base_rate(2024, pack) == pytest.approx(0.70)


# --- the alt_segments block: every registered version's bands, per Term ---------


def test_alt_segments_carry_exactly_the_non_active_versions(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The block exists for non-active registered versions — today, sal-v1
    beside the active sal-v2 — and never repeats the active one. (While only
    one version existed the key was absent entirely; a second registered
    version is what makes the committed pack gain the block at a refresh.)"""
    pack = _pack(fixture_corpus)
    for term in pack.terms:
        versions = {alt.salience_version for alt in term.alt_segments}
        assert versions == {"sal-v1"}, versions
    payload = pack.model_dump(mode="json")
    assert all("alt_segments" in term for term in payload["terms"])


def test_a_second_version_publishes_its_own_bands_beside_the_active_ones(
    fixture_corpus: FixtureCorpus, two_versions: SalienceScorer
) -> None:
    """A prediction keeps the version that banded it for life, so when the live
    pass moves on the retired scorer still needs a published base rate. This is
    the producer half of that contract — `_pooled_band_rate` reads what it emits."""
    pack = _pack(fixture_corpus)
    for term in pack.terms:
        assert term.salience_version == SALIENCE_VERSION
        assert [s.band for s in term.segments] == list(_BANDS)
        alts = {alt.salience_version: alt for alt in term.alt_segments}
        assert set(alts) == {"sal-toy", "sal-v1"}
        # Each version's own vocabulary, not the active scorer's — a band name
        # means something only under the function that assigned it.
        assert [s.band for s in alts["sal-toy"].segments] == ["hot", "cold"]
        assert [s.band for s in alts["sal-v1"].segments] == ["high", "elevated", "baseline"]
    # And it survives serialization rather than being dropped by the wrap serializer.
    payload = pack.model_dump(mode="json")
    assert all(len(term["alt_segments"]) == 2 for term in payload["terms"])


def test_both_versions_count_the_same_rows_into_their_own_bands(
    fixture_corpus: FixtureCorpus, two_versions: SalienceScorer
) -> None:
    """One streaming pass feeds every version, so the versions partition the same
    population — they disagree about which band a row lands in, never about
    whether it is in the scored segment at all."""
    pack = _pack(fixture_corpus)
    for term in pack.terms:
        for alt in term.alt_segments:
            assert sum(s.ingested for s in term.segments) == sum(
                s.ingested for s in alt.segments
            ), alt.salience_version
            assert sum(s.resolved for s in term.segments) == sum(
                s.resolved for s in alt.segments
            ), alt.salience_version


def test_merits_population_excludes_judgments_that_rode_the_grant_order(tmp_path: Path) -> None:
    """The label-independent twin of the GVR exclusion, loud on its own.

    A stale-labeled cert-order vacatur reads plain `granted` (the `gvr` label
    is a forward convention, and labels lag on recent IFP GVRs), so the
    disposition exclusion cannot see it — but its parsed vacatur carries the
    grant's own date, and the pool guard excludes it from the cohort entirely
    (not in `granted`, not in `parsed`, not in the rate) while counting it as
    `cert_order_excluded`. An undated parse is different: membership unknown,
    so it stays in `granted` as a visible coverage gap while its judgment
    stays out of the parsed slice — and the retained affirmance is what makes
    the RATE discriminate, not just the counts (guarded 1/2 vs 2/3 unguarded).
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/910000021",
                    court="scotus",
                    docket_number="19-101",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2020, 1, 10),
                    merits_judgment="reversed",
                    merits_decided=date(2020, 6, 22),
                ),
                corpus.CorpusRow(
                    case_id="scotus/910000022",
                    court="scotus",
                    docket_number="19-102",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2020, 1, 13),
                    merits_judgment="vacated",
                    merits_decided=date(2020, 1, 13),
                ),
                corpus.CorpusRow(
                    case_id="scotus/910000023",
                    court="scotus",
                    docket_number="19-103",
                    # The undated parse: the gap cannot be evaluated, so its
                    # membership is unknown — kept in `granted` as coverage,
                    # kept out of the parsed slice and the rate.
                    disposition=Disposition.granted,
                    date_cert_granted=date(2020, 1, 13),
                    merits_judgment="vacated",
                ),
                corpus.CorpusRow(
                    case_id="scotus/910000024",
                    court="scotus",
                    docket_number="19-104",
                    # A genuine argued affirmance: what makes the rate itself
                    # discriminate between the guarded and unguarded pool.
                    disposition=Disposition.granted,
                    date_cert_granted=date(2020, 1, 13),
                    merits_judgment="affirmed",
                    merits_decided=date(2020, 6, 29),
                ),
            ],
        )
    merits = analytics.build_statpack(corpus_db_path=db).merits
    assert merits is not None
    assert (merits.granted, merits.parsed, merits.disturbed) == (3, 2, 1)
    assert merits.cert_order_excluded == 1
    assert merits.terms[0].cert_order_excluded == 1
    assert merits.disturbed_rate == pytest.approx(0.5)


def test_a_clean_guarded_build_publishes_zero_not_null(tmp_path: Path) -> None:
    """The other side of the vintage distinction: a build the guard ran on
    with nothing to remove publishes the measured `0`, never the pre-guard
    `null`. `metrics/README.md` keys quotability on the null, so a regression
    collapsing the two (an `or None`, an accumulator initialized to `None`)
    would mark every clean guarded build unquotable while the fired-guard
    assertions above stay green."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/910000031",
                    court="scotus",
                    docket_number="19-201",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2020, 1, 10),
                    merits_judgment="reversed",
                    merits_decided=date(2020, 6, 22),
                )
            ],
        )
    pack = analytics.build_statpack(corpus_db_path=db)
    assert pack.merits is not None
    assert pack.merits.cert_order_excluded == 0
    assert pack.merits.terms[0].cert_order_excluded == 0
    markdown = analytics.render_statpack_markdown(pack)
    assert "0 excluded by the pool guard" in markdown
    assert "— excluded by the pool guard" not in markdown
