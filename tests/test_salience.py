"""Tests for the salience gate: the frozen sal-v1 scorer and the selection pass."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.config import SalienceConfig, load_salience_config
from fedcourtsai.pipeline.salience import (
    SALIENCE_VERSION,
    reconcile_salience_selection,
    salience_band,
    salience_bands,
    salience_score,
)

REGULAR_CONFERENCE = date(2026, 1, 9)  # a Term conference (Oct-June)
LONG_CONFERENCE = date(2025, 9, 29)  # the Term's opening long conference (September)


def _petition(
    case_id: str,
    *,
    distribution_count: int | None = 1,
    cvsg: bool = False,
    circuit: str | None = None,
    conference: date | None = REGULAR_CONFERENCE,
    docket: str = "25-100",
    selected: bool = False,
    court: str = "scotus",
) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {
            "case_id": case_id,
            "court": court,
            "docket_number": docket,
            "date_filed": date(2025, 10, 1),
            "distribution_count": distribution_count,
            "cvsg_date": date(2026, 1, 2) if cvsg else None,
            "originating_court": circuit,
            "distributed_for_conference": conference,
            "salience_selected": selected,
        }
    )


# --- the frozen sal-v1 scorer --------------------------------------------------


def test_score_rises_with_relists() -> None:
    r0 = salience_score(_petition("scotus/0", distribution_count=1))  # 0 relists
    r1 = salience_score(_petition("scotus/1", distribution_count=2))  # 1 relist
    r2 = salience_score(_petition("scotus/2", distribution_count=3))  # 2 relists
    assert r0 < r1 < r2
    assert r2 == pytest.approx(0.394 + 0.1 * 0.05)  # relist-2 + default-circuit nudge


def test_cvsg_lifts_a_low_relist_petition_over_the_floor() -> None:
    plain = salience_score(_petition("scotus/a", distribution_count=1))
    cvsg = salience_score(_petition("scotus/b", distribution_count=1, cvsg=True))
    assert cvsg > plain
    assert cvsg == pytest.approx(0.283 + 0.1 * 0.05)
    assert cvsg >= SalienceConfig().floor  # a CVSG petition always clears the floor


def test_circuit_is_only_a_bounded_nudge_not_a_co_equal_signal() -> None:
    # A relist-0 petition from a high-grant circuit must NOT be lifted to that
    # circuit's grant rate (that would double-count the circuit's relist mix); the
    # circuit contributes at most ~0.046 and never clears the floor on its own.
    cadc = salience_score(_petition("scotus/c", distribution_count=1, circuit="cadc"))
    assert cadc == pytest.approx(0.008 + 0.1 * 0.457)
    assert cadc < SalienceConfig().floor


def test_unknown_relist_scores_the_overall_rate() -> None:
    unknown = salience_score(_petition("scotus/u", distribution_count=None))
    assert unknown == pytest.approx(0.024 + 0.1 * 0.05)


# --- the frozen sal-v1 bands ---------------------------------------------------


def test_bands_track_the_relist_cvsg_tier() -> None:
    # The band is the petition's grant-likelihood tier: relist-2+ / CVSG are high,
    # one relist is elevated, relist-0 / never-scanned are baseline.
    assert salience_band(_petition("scotus/h", distribution_count=3)) == "high"  # 2 relists
    assert salience_band(_petition("scotus/v", distribution_count=1, cvsg=True)) == "high"
    assert salience_band(_petition("scotus/e", distribution_count=2)) == "elevated"  # 1 relist
    assert salience_band(_petition("scotus/b", distribution_count=1)) == "baseline"  # 0 relists
    assert salience_band(_petition("scotus/u", distribution_count=None)) == "baseline"


def test_circuit_nudge_never_carries_a_petition_across_a_band_boundary() -> None:
    # The cutpoints sit in the gaps between the relist/CVSG tiers, so even the
    # strongest circuit nudge (cadc) keeps a petition in its trajectory's band.
    for circuit in ("ca1", "cadc"):
        assert salience_band(_petition("scotus/0", distribution_count=1, circuit=circuit)) == (
            "baseline"
        )
        assert salience_band(_petition("scotus/1", distribution_count=2, circuit=circuit)) == (
            "elevated"
        )
        assert salience_band(_petition("scotus/2", distribution_count=3, circuit=circuit)) == "high"


def test_salience_bands_are_ordered_strongest_first() -> None:
    assert salience_bands() == ("high", "elevated", "baseline")


# --- the selection pass --------------------------------------------------------


def _seed(tmp_path: Path, rows: list[corpus.CorpusRow]) -> Path:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    return db


def _selected_ids(db: Path) -> set[str]:
    with corpus.connect(db) as conn:
        return {r.case_id for r in corpus.iter_rows(conn, court="scotus") if r.salience_selected}


def test_ranks_and_caps_to_n_with_carveouts_above_n(tmp_path: Path) -> None:
    # Five below-floor relist-0 petitions (ranked, cap bites) plus one CVSG
    # carve-out. N=3: the CVSG is always in, and the top 3 of the five ranked fill
    # to N — so the realized selected count is 4, above N (carve-outs sit above N).
    rows = [_petition(f"scotus/{i}", distribution_count=1) for i in range(5)]
    rows.append(_petition("scotus/cvsg", distribution_count=1, cvsg=True))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=3, floor=0.28)
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, config, apply=True)
    selected = _selected_ids(db)
    assert "scotus/cvsg" in selected  # carve-out, above N
    # The five relist-0 rows tie on score, so the cap takes the 3 lowest case_ids.
    assert {"scotus/0", "scotus/1", "scotus/2"} <= selected
    assert "scotus/3" not in selected and "scotus/4" not in selected
    assert result.newly_selected == 4
    assert result.version == SALIENCE_VERSION


def test_selection_is_sticky_across_runs(tmp_path: Path) -> None:
    # Round 1 selects the top-2 of three relist-0 petitions (a, b by case_id).
    # Round 2 adds a relist-1 petition that out-ranks them; the cap would now drop
    # 'b', but the one-way latch keeps it — a case selected once stays selected.
    db = _seed(tmp_path, [_petition(f"scotus/{c}", distribution_count=1) for c in "abc"])
    config = SalienceConfig(per_conference_capacity=2, floor=0.28)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert _selected_ids(db) == {"scotus/a", "scotus/b"}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_petition("scotus/hot", distribution_count=2)])  # relist-1
        result = reconcile_salience_selection(conn, config, apply=True)
    # 'hot' joins; 'b' stays despite dropping out of the fresh top-2. Never de-selected.
    assert _selected_ids(db) == {"scotus/a", "scotus/b", "scotus/hot"}
    assert result.newly_selected == 1  # only 'hot' is new this run


def test_capacity_is_per_conference(tmp_path: Path) -> None:
    # Two conferences, each capped independently at N=1.
    rows = [
        _petition(f"scotus/x{i}", distribution_count=1, conference=REGULAR_CONFERENCE)
        for i in range(3)
    ]
    rows += [
        _petition(f"scotus/y{i}", distribution_count=1, conference=date(2026, 2, 20))
        for i in range(3)
    ]
    db = _seed(tmp_path, rows)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(
            conn, SalienceConfig(per_conference_capacity=1, floor=0.28), apply=True
        )
    selected = _selected_ids(db)
    assert len([s for s in selected if s.startswith("scotus/x")]) == 1
    assert len([s for s in selected if s.startswith("scotus/y")]) == 1


def test_long_conference_uses_the_larger_cap(tmp_path: Path) -> None:
    rows = [
        _petition(f"scotus/{i}", distribution_count=1, conference=LONG_CONFERENCE) for i in range(4)
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=1, long_conference_capacity=3, floor=0.28)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert len(_selected_ids(db)) == 3  # the long-conference cap, not the regular 1


def test_petition_not_yet_distributed_is_scored_but_not_selected(tmp_path: Path) -> None:
    db = _seed(tmp_path, [_petition("scotus/pending", distribution_count=3, conference=None)])
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, SalienceConfig(), apply=True)
        row = corpus.get_row(conn, "scotus/pending")
    assert row is not None
    assert row.salience_score is not None  # scored
    assert row.salience_selected is False  # but not selected — not up for prediction yet


def test_out_of_scope_petition_is_not_scored(tmp_path: Path) -> None:
    # A non-cert SCOTUS form (an application, 25A100) is Tier-0 out of scope, so
    # the pass never scores or selects it.
    db = _seed(tmp_path, [_petition("scotus/app", docket="25A100", distribution_count=3)])
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, SalienceConfig(), apply=True)
        row = corpus.get_row(conn, "scotus/app")
    assert result.eligible_cases == 0
    assert row is not None and row.salience_score is None and row.salience_selected is False


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    db = _seed(tmp_path, [_petition("scotus/1", distribution_count=3)])
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, SalienceConfig(), apply=False)
        row = corpus.get_row(conn, "scotus/1")
    assert result.applied is False and result.scored == 1
    assert row is not None and row.salience_score is None and row.salience_selected is False


# --- config --------------------------------------------------------------------


def test_load_salience_config_reads_the_tracking_section(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text(
        "salience:\n  per_conference_capacity: 42\n  long_conference_capacity: 99\n  floor: 0.5\n"
    )
    config = load_salience_config(tmp_path)
    assert config.per_conference_capacity == 42
    assert config.long_conference_capacity == 99
    assert config.floor == 0.5


def test_load_salience_config_defaults_when_absent(tmp_path: Path) -> None:
    config = load_salience_config(tmp_path)  # no tracking.yaml
    assert config.per_conference_capacity == 150
    assert config.long_conference_capacity == 500
    assert config.floor == 0.28


def test_salience_config_rejects_a_smaller_long_conference_cap() -> None:
    with pytest.raises(ValueError, match="long_conference_capacity must be >="):
        SalienceConfig(per_conference_capacity=200, long_conference_capacity=100)
