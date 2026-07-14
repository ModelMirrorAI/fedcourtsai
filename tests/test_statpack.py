"""Tests for the corpus base-rate statpack (``fedcourts statpack`` / :mod:`analytics`).

Uses the deterministic synthetic corpus (``fixture_corpus``): six cases across
ca9 / ca1 / scotus, four resolved and two open. The two SCOTUS petitions are
live-slice rows — ``scotus/304`` a walker-sampled denial at weight 5 (one
relist), ``scotus/305`` a pending poller row at weight 1 (CVSG on file) — and
the fixture carries discovery cursors (OT22 paid complete at 850, OT22 IFP
partial at 460, OT24 paid partial at 12), so the weighted sections, the census,
and the completeness flags all have real material to aggregate.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
from fedcourtsai.analytics import _STATPACK_SECTIONS
from fedcourtsai.cli import app
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

_BANDS = ("high", "elevated", "baseline")


def _pack(fc: FixtureCorpus) -> StatPack:
    return analytics.build_statpack(corpus_db_path=fc.db_path)


def _section(pack: StatPack, title: str) -> StatPackSection:
    return next(s for s in pack.sections if s.title == title)


def _term(pack: StatPack, year: int) -> StatPackTerm:
    return next(t for t in pack.terms if t.term == year)


def test_build_statpack_headline_and_sections(fixture_corpus: FixtureCorpus) -> None:
    pack = _pack(fixture_corpus)
    assert (pack.corpus_rows, pack.resolved, pack.open) == (6, 4, 2)
    # All four resolved fixture cases carry concrete labels and date pairs.
    assert (pack.machine_readable_resolved, pack.dated_resolved) == (4, 4)
    # Overall base rate over the four resolved cases (raw counts, never weighted).
    shares = {d.disposition: d.share for d in pack.overall.dispositions}
    assert shares == {"denied": 0.5, "dismissed": 0.25, "granted": 0.25}
    # One section per curated breakdown, in order.
    assert [s.title for s in pack.sections] == [spec.title for spec in _STATPACK_SECTIONS]


def test_build_statpack_coverage_block(fixture_corpus: FixtureCorpus) -> None:
    coverage = _pack(fixture_corpus).coverage
    # The two SCOTUS petitions are the live slice; one is resolved (raw count).
    assert (coverage.live_slice_rows, coverage.live_slice_resolved) == (2, 1)
    # Census totals across the fixture cursors: OT22 paid 850 + OT22 IFP
    # (5460 - 5001 + 1 = 460) + OT24 paid 12.
    assert coverage.census_filings == 850 + 460 + 12


def test_build_statpack_court_breakdown(fixture_corpus: FixtureCorpus) -> None:
    by_court = _section(_pack(fixture_corpus), "Cases by court")
    assert by_court.court is None
    assert by_court.group_by == "court"
    assert by_court.live_slice is False and by_court.weighted is False
    assert [(b.key, b.cases) for b in by_court.buckets] == [("ca9", 3), ("scotus", 2), ("ca1", 1)]


def test_build_statpack_overall_timing(fixture_corpus: FixtureCorpus) -> None:
    timing = _pack(fixture_corpus).timing
    # The four resolved cases all carry date pairs: 168, 319, 525, and 546 days.
    assert timing.cases == 4
    assert timing.mean_days == pytest.approx(389.5)
    assert timing.median_days == 319.0  # nearest-rank: ceil(0.5 x 4) = rank 2
    assert timing.p90_days == 546.0  # nearest-rank: ceil(0.9 x 4) = rank 4


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
    relists = _section(pack, "Cert petitions by relist count")
    # scotus/304: two distributions = one relist (weight 5); scotus/305: one
    # distribution = zero relists (weight 1).
    assert {(b.key, b.cases) for b in relists.buckets} == {("1", 5), ("0", 1)}
    cvsg = _section(pack, "Cert petitions by CVSG status")
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
    # The per-fee-class grant rate sums the grant family, so a lone gvr reads 100%.
    paid = next(c for c in term.classes if c.fee_class == "paid")
    assert paid.est_grant_rate == 1.0
    # gvr is tracked as its own disposition bucket, distinct from granted.
    assert {d.disposition for d in term.base_rates.dispositions} == {"gvr"}


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
    relists = _section(pack, "Cert petitions by relist count")
    cvsg = _section(pack, "Cert petitions by CVSG status")
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
    assert ("scotus", 3) in {(b.key, b.cases) for b in by_court.buckets}
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
    paid, ifp = resolved_term.classes
    assert (paid.fee_class, paid.filings, paid.complete) == (FeeClass.paid, 850, True)
    assert (paid.ingested, paid.resolved, paid.weighted_resolved) == (1, 1, 5)
    assert paid.est_grant_rate == 0.0  # resolved petitions, none granted
    assert (ifp.fee_class, ifp.filings, ifp.complete) == (FeeClass.ifp, 460, False)
    assert (ifp.ingested, ifp.weighted_resolved, ifp.est_grant_rate) == (0, 0, None)

    open_term = _term(pack, 2024)
    assert (open_term.base_rates.cases, open_term.base_rates.open) == (1, 1)
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
    assert resolved_term.salience_version == "sal-v1"
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
    assert "**6** case(s): 4 resolved, 2 open." in md
    assert "**Live/historical slice:** 2 case(s), 1 resolved" in md
    assert "1322 docketed filing(s)" in md
    assert "**Dated share:** 4 of 4 machine-readable resolved case(s)" in md
    # Full-corpus sections say so; live-slice sections state slice + weighting.
    assert "## Cases by court" in md
    assert "_Scope: all courts; includes the frozen bulk import._" in md
    assert (
        "_Scope: scotus, modern discretionary-cert dockets, live/historical slice; "
        "counts are denial-reweighted estimates._" in md
    )
    assert "median 319d, p90 546d (mean 389.5d over 4 dated case(s))" in md
    # The per-Term table: filings census, raw ingested count, weighted
    # estimates, completeness. OT22 ingested exactly one live row; the weighted
    # columns count its sampled denial as five.
    assert "## SCOTUS cert petitions by Term" in md
    assert "| 2022 | 850/460 | 1 | 5 | denied 100.0% | 0.0% | 0 | 168 | ✓/partial |" in md
    assert "| 2024 | 12/— | 1 | 0 | — | — | 0 | — | partial/partial |" in md
    # The replay self-selection rule rides under the Term table, verbatim.
    assert "anchor only on Term rows strictly preceding your clock" in md


def test_render_statpack_markdown_renders_the_segment_base_rate(
    fixture_corpus: FixtureCorpus,
) -> None:
    md = analytics.render_statpack_markdown(_pack(fixture_corpus))
    # The pack-wide band section (blended) and the leakage-safe per-Term table.
    assert "## Cert petitions by salience band" in md
    assert "### Segment base rate by salience band (sal-v1)" in md
    assert "| Term | high | elevated | baseline |" in md
    # OT22's lone elevated petition is a weight-5 denial: 0.0% over n=5, other bands —.
    assert "| 2022 | — | 0.0% (n=5) | — |" in md


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


def test_build_statpack_era_section(fixture_corpus: FixtureCorpus) -> None:
    era = _section(_pack(fixture_corpus), "SCOTUS cases by era")
    # Both fixture SCOTUS petitions carry 2020s Term-prefixed docket numbers.
    assert [(b.key, b.cases) for b in era.buckets] == [("2020s", 2)]
