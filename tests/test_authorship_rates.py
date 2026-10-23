"""The statpack's authorship section and the authorship claims' strictly-prior baselines."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.analytics import build_statpack
from fedcourtsai.pipeline import claims as claims_module
from fedcourtsai.pipeline.authorship_rates import authorship_section
from fedcourtsai.pipeline.base_rates import (
    AUTHORSHIP_BASE_RATE_MIN_DECISIONS,
    AUTHORSHIP_PRIOR_WEIGHT,
    PER_CURIAM_LABEL,
    majority_author_base_rate,
    separate_writing_base_rate,
)
from fedcourtsai.pipeline.claims import CLAIM_MAJORITY_AUTHOR, CLAIM_SEPARATE_WRITERS
from fedcourtsai.pipeline.justices import bench_on
from fedcourtsai.schemas import (
    PredictionContext,
    StatPack,
    StatPackAuthorship,
    StatPackAuthorshipJustice,
    StatPackAuthorshipTerm,
)

_BENCH = bench_on(date(2025, 1, 15))


def _writing(
    listing: str,
    position: int,
    kind: str,
    author: str | None,
    *,
    argued: str | None = "2024-11-04",
    coauthors: tuple[str, ...] = (),
    case_id: str | None = None,
) -> tuple[object, ...]:
    return (
        2024,
        listing,
        position,
        f"24-{listing}",
        "2025-01-15",
        argued,
        kind,
        author,
        json.dumps(list(coauthors)),
        case_id,
    )


def _seed(tmp_path: Path) -> Path:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    writings = [
        # Signed, observed: Kagan writes; Thomas dissents, Gorsuch joins Thomas's
        # concurrence as co-author; Barrett took no part.
        _writing("1", 1, "opinion-of-the-court", "Kagan"),
        _writing("1", 2, "dissent", "Thomas"),
        _writing("1", 3, "concurrence", "Alito", coauthors=("Gorsuch",)),
        # Signed, no bench row: counts for authorship only.
        _writing("2", 1, "plurality", "Alito"),
        _writing("2", 2, "dissent", "Sotomayor"),
        # A per curiam prints no argument date; its case row says it was argued.
        _writing("3", 1, "per-curiam", None, argued=None, case_id="scotus/3"),
        # A summary per curiam, a DIG, and one linked to no row: outside the population.
        _writing("4", 1, "per-curiam", None, argued=None, case_id="scotus/4"),
        _writing("5", 1, "per-curiam", None, argued=None, case_id="scotus/5"),
        _writing("6", 1, "per-curiam", None, argued=None),
        # An argued per curiam whose row is not yet classified: the claim masks it.
        _writing("7", 1, "per-curiam", None, argued=None, case_id="scotus/7"),
        # Observed, but the author also concurs: the claim masks it, so it is
        # no observation of separate writing.
        _writing("8", 1, "opinion-of-the-court", "Kavanaugh"),
        _writing("8", 2, "concurrence", "Kavanaugh"),
        _writing("8", 3, "dissent", "Jackson"),
    ]
    benches = [
        (2024, "1", json.dumps(list(_BENCH)), json.dumps(["Barrett"])),
        (2024, "3", None, None),
        (2024, "8", json.dumps(list(_BENCH)), json.dumps([])),
    ]
    rows = [
        corpus.CorpusRow(
            case_id="scotus/3",
            court="scotus",
            docket_number="24-3",
            merits_argued=date(2024, 11, 4),
            merits_decision_method="argued-per-curiam",
        ),
        corpus.CorpusRow(
            case_id="scotus/4",
            court="scotus",
            docket_number="24-4",
            merits_decision_method="summary-opinion",
        ),
        corpus.CorpusRow(
            case_id="scotus/5",
            court="scotus",
            docket_number="24-5",
            merits_argued=date(2024, 11, 5),
            merits_decision_method="dig",
        ),
        corpus.CorpusRow(
            case_id="scotus/7",
            court="scotus",
            docket_number="24-7",
            merits_argued=date(2024, 11, 6),
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        conn.executemany(
            "INSERT INTO opinions (term, listing_number, position, docket, decided, argued, "
            "kind, author, coauthors, case_id, words, word_rule, document_url, read_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 10, 'w/1', 'u', '2025-07-01')",
            writings,
        )
        conn.executemany(
            "INSERT INTO opinion_benches (term, listing_number, bench, took_no_part, lineup, "
            "read_at) VALUES (?, ?, ?, ?, '', '2025-07-01')",
            benches,
        )
        conn.commit()
    return db


def test_the_section_counts_argued_decisions_and_observed_separate_writings(
    tmp_path: Path,
) -> None:
    db = _seed(tmp_path)
    with corpus.connect_readonly(db) as conn:
        section = authorship_section(conn)
    assert section is not None
    (term,) = section.terms
    assert (term.term, term.decisions, term.per_curiam, term.observed) == (2024, 3, 1, 1)
    rows = {row.justice: row for row in term.justices}
    assert [row.justice for row in term.justices] == list(_BENCH)
    assert all(row.decisions == 3 for row in term.justices)
    assert (rows["Kagan"].majority, rows["Alito"].majority, rows["Thomas"].majority) == (1, 1, 0)
    # Only the observed decision counts toward separate writing, and Barrett took no part.
    assert rows["Barrett"].sat == 0 and rows["Kagan"].sat == 1
    assert {name for name, row in rows.items() if row.separate} == {"Thomas", "Alito", "Gorsuch"}
    assert rows["Sotomayor"].separate == 0  # her dissent rode an unobserved decision
    assert rows["Jackson"].separate == 0 and rows["Kavanaugh"].majority == 0


def test_a_blob_without_the_record_has_no_section(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        conn.commit()
    with corpus.connect_readonly(db) as conn:
        assert authorship_section(conn) is None
    pack = build_statpack(corpus_db_path=db)
    assert pack.authorship is None and "authorship" not in pack.model_dump(mode="json")


def test_the_statpack_carries_the_section(tmp_path: Path) -> None:
    pack = build_statpack(corpus_db_path=_seed(tmp_path))
    assert pack.authorship is not None and pack.authorship.terms[0].decisions == 3


def test_a_blob_without_the_tables_reads_as_an_empty_record(tmp_path: Path) -> None:
    db = tmp_path / "bare.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE cases (case_id TEXT)")
    with sqlite3.connect(db) as conn:
        assert authorship_section(conn) is None


# --- the baselines ----------------------------------------------------------------


def _term(
    term: int, *, decisions: int, per_curiam: int, majority: dict[str, int], separate: int = 0
) -> StatPackAuthorshipTerm:
    return StatPackAuthorshipTerm(
        term=term,
        decisions=decisions,
        per_curiam=per_curiam,
        observed=decisions - per_curiam,
        justices=[
            StatPackAuthorshipJustice(
                justice=name,
                decisions=decisions,
                majority=majority.get(name, 0),
                sat=decisions - per_curiam,
                separate=separate if name == "Thomas" else 0,
            )
            for name in _BENCH
        ],
    )


def _pack(*terms: StatPackAuthorshipTerm) -> StatPack:
    return StatPack(corpus_rows=1, authorship=StatPackAuthorship(terms=list(terms)))


_EVEN = dict.fromkeys(_BENCH, 6)


def test_the_author_baseline_is_a_distribution_over_the_bench_and_the_per_curiam() -> None:
    pack = _pack(_term(2023, decisions=60, per_curiam=6, majority=_EVEN | {"Kagan": 10}))
    baseline = majority_author_base_rate(2024, _BENCH, pack)
    assert baseline is not None
    assert sum(baseline.values()) == pytest.approx(1.0)
    assert baseline[PER_CURIAM_LABEL] == pytest.approx(6.5 / 61)
    assert baseline["Kagan"] > baseline["Thomas"]
    assert set(baseline) == {*_BENCH, PER_CURIAM_LABEL}


def test_a_newly_seated_justice_is_priced_at_the_even_share() -> None:
    pack = _pack(_term(2023, decisions=60, per_curiam=6, majority=_EVEN))
    bench = (*_BENCH[:-1], "Newcomer")
    baseline = majority_author_base_rate(2024, bench, pack)
    assert baseline is not None
    even = (1 - 6.5 / 61) / 9
    # No record: the even share, up to the bench-wide scaling.
    assert baseline["Newcomer"] == pytest.approx(even, rel=0.01)
    assert sum(baseline.values()) == pytest.approx(1.0)


def test_the_baselines_pool_only_strictly_prior_terms_inside_the_band() -> None:
    prior = _term(2023, decisions=60, per_curiam=6, majority=_EVEN)
    own = _term(2024, decisions=60, per_curiam=60, majority={})
    old = _term(2019, decisions=60, per_curiam=60, majority={})
    pack = _pack(own, prior, old)
    baseline = majority_author_base_rate(2024, _BENCH, pack, lookback_terms=3)
    assert baseline is not None and baseline[PER_CURIAM_LABEL] == pytest.approx(6.5 / 61)
    # Unbounded, the old Term joins; the case's own still never does.
    unbounded = majority_author_base_rate(2024, _BENCH, pack)
    assert unbounded is not None and unbounded[PER_CURIAM_LABEL] == pytest.approx(66.5 / 121)


def test_a_window_with_no_per_curiam_still_prices_one() -> None:
    pack = _pack(_term(2023, decisions=60, per_curiam=0, majority=_EVEN))
    baseline = majority_author_base_rate(2024, _BENCH, pack)
    assert baseline is not None and baseline[PER_CURIAM_LABEL] == pytest.approx(0.5 / 61)
    assert sum(baseline.values()) == pytest.approx(1.0)


def test_below_the_floor_there_is_no_baseline() -> None:
    small = _term(2023, decisions=AUTHORSHIP_BASE_RATE_MIN_DECISIONS - 1, per_curiam=0, majority={})
    assert majority_author_base_rate(2024, _BENCH, _pack(small)) is None
    assert separate_writing_base_rate(2024, _BENCH, _pack(small)) is None
    assert majority_author_base_rate(2024, _BENCH, StatPack(corpus_rows=1)) is None
    assert (
        majority_author_base_rate(
            2024, (), _pack(_term(2023, decisions=60, per_curiam=0, majority={}))
        )
        is None
    )


def test_the_separate_rate_shrinks_toward_the_pooled_rate() -> None:
    pack = _pack(_term(2023, decisions=60, per_curiam=0, majority={}, separate=18))
    baseline = separate_writing_base_rate(2024, _BENCH, pack)
    assert baseline is not None and set(baseline) == set(_BENCH)
    pooled = 18 / (60 * len(_BENCH))
    weight = AUTHORSHIP_PRIOR_WEIGHT
    assert baseline["Thomas"] == pytest.approx((18 + weight * pooled) / (60 + weight))
    assert baseline["Roberts"] == pytest.approx(weight * pooled / (60 + weight))


def test_the_claims_price_the_cell_bench_from_the_snapshot_term() -> None:
    pack = _pack(_term(2024, decisions=60, per_curiam=6, majority=_EVEN))
    context = PredictionContext(
        mode="forward", snapshot_date=date(2025, 11, 3), signals_observable=True, term=2025
    )
    author = claims_module._distribution_baseline(
        CLAIM_MAJORITY_AUTHOR, context, pack, lookback_terms=3
    )
    separate = claims_module._distribution_baseline(
        CLAIM_SEPARATE_WRITERS, context, pack, lookback_terms=3
    )
    assert author is not None and set(author) == {
        *bench_on(context.snapshot_date),
        PER_CURIAM_LABEL,
    }
    assert separate is not None and set(separate) == set(bench_on(context.snapshot_date))
    # A snapshot in OT2024 reads only the Terms before it.
    earlier = context.model_copy(update={"snapshot_date": date(2025, 3, 3)})
    assert (
        claims_module._distribution_baseline(CLAIM_MAJORITY_AUTHOR, earlier, pack, lookback_terms=3)
        is None
    )
