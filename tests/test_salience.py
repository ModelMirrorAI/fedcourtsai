"""Tests for the salience gate: the frozen sal-v1 scorer and the selection pass."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.config import SalienceConfig, load_salience_config
from fedcourtsai.pipeline import salience as salience_module
from fedcourtsai.pipeline.pull import _in_predict_scope
from fedcourtsai.pipeline.salience import (
    _CIRCUIT_GRANT_RATE,
    SALIENCE_VERSION,
    SCORERS,
    SalienceScorer,
    _selection_plan,
    apply_salience_selection,
    arrival_draw,
    carve_out,
    plan_cohorts,
    reconcile_salience_selection,
    registered_versions,
    salience_band,
    salience_bands,
    salience_score,
    scorer,
    unlatch_overselected,
)
from fedcourtsai.schemas import EventKind, Stage

REGULAR_CONFERENCE = date(2026, 1, 9)  # a Term conference (Oct-June)
LONG_CONFERENCE = date(2025, 9, 29)  # the Term's opening long conference (September)


def _petition(  # noqa: PLR0913 - a keyword-only test fixture builder, one arg per row feature
    case_id: str,
    *,
    distribution_count: int | None = 1,
    cvsg: bool = False,
    circuit: str | None = None,
    conference: date | None = REGULAR_CONFERENCE,
    docket: str = "25-100",
    selected: bool = False,
    court: str = "scotus",
    date_cert_denied: date | None = None,
    petitioner_title: str | None = None,
) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {
            "case_id": case_id,
            "court": court,
            "petitioner_title": petitioner_title,
            "docket_number": docket,
            "date_filed": date(2025, 10, 1),
            "distribution_count": distribution_count,
            "cvsg_date": date(2026, 1, 2) if cvsg else None,
            "originating_court": circuit,
            "distributed_for_conference": conference,
            "salience_selected": selected,
            "date_cert_denied": date_cert_denied,
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


@pytest.mark.parametrize("version", registered_versions())
def test_the_carve_out_set_is_exactly_the_strongest_band(version: str) -> None:
    """The carved set must be a clean prefix of the band order, no band mixed.

    The always-include rule (config floor + code predicates) and the band
    boundaries are separate constants in separate files; what must hold is
    that every band is carved entirely or not at all (a mixed band would give
    the statpack a base rate conditioned on a population its own carve status
    splits) and the fully-carved bands must be the *exact expected prefix*
    per version — sal-v1's is (high,), the original carved-iff-strongest
    identity; sal-v2's is (federal, high). Pinning the expected prefix keeps
    the check as strong as the original: a refit that silently carved an
    extra tier fails here. The enumeration
    drives the scorer over every relist state x circuit x CVSG x petitioner
    class, so it spans the achievable lattice of every registered version's
    features; the private constant is imported only to enumerate circuits.

    Parameterized over every registered version, so registering a second scorer
    cannot skip the check that the first one is held to."""
    banding = scorer(version)
    floor = load_salience_config(Path("config")).floor
    circuits = [*_CIRCUIT_GRANT_RATE, "xx-unknown", None]
    titles = ("United States", "State of Texas", "John Doe", None)
    carved_by_band: dict[str, set[bool]] = {band: set() for band in banding.bands}
    for distribution_count in (1, 2, 3, None):
        for circuit in circuits:
            for cvsg in (False, True):
                for title in titles:
                    row = _petition(
                        "scotus/lattice",
                        distribution_count=distribution_count,
                        cvsg=cvsg,
                        circuit=circuit,
                        petitioner_title=title,
                    )
                    score = banding.score(row)
                    band = banding.band(row)
                    carved = banding.carve_out(row, score, floor)
                    carved_by_band[band].add(carved)
    for band, outcomes in carved_by_band.items():
        assert len(outcomes) <= 1, f"{version}: band {band!r} mixes carved and uncarved members"
    fully_carved = tuple(b for b in banding.bands if carved_by_band[b] == {True})
    expected = {"sal-v1": ("high",), "sal-v2": ("federal", "high")}.get(
        version, banding.bands[: len(fully_carved)] if fully_carved else None
    )
    assert fully_carved == expected, f"{version}: carved bands {fully_carved}, expected {expected}"
    assert fully_carved, f"{version}: no band is carved — the always-include rule reaches nothing"


def test_the_active_scorer_is_what_the_bare_helpers_dispatch_to() -> None:
    """The module-level helpers are delegations, not a second implementation.

    Every existing caller reads `salience_score` / `salience_band` /
    `carve_out` as "the live scorer", so those names have to stay pinned to the
    registry's active entry rather than to whichever function happens to be
    defined beside them."""
    row = _petition("scotus/1", distribution_count=3, circuit="ca9")
    active = scorer()
    assert active.version == SALIENCE_VERSION
    assert active.score(row) == salience_score(row)
    assert active.band(row) == salience_band(row)
    assert active.bands == salience_bands()
    assert active.carve_out(row, salience_score(row), 0.28) == carve_out(
        row, salience_score(row), 0.28
    )


def test_registered_versions_leads_with_the_active_one() -> None:
    """Report cell order is stable across runs and puts the live scorer first."""
    versions = registered_versions()
    assert versions[0] == SALIENCE_VERSION
    assert set(versions) == set(SCORERS)
    assert list(versions[1:]) == sorted(versions[1:])


def test_an_unregistered_version_raises_rather_than_falling_back() -> None:
    """A caller asking for a scorer this process cannot produce wants an error.

    Falling back to the active scorer would silently return output banded under
    a version the caller did not ask for — which is exactly the confusion the
    version pin exists to prevent."""
    with pytest.raises(KeyError):
        scorer("sal-v0")


def test_every_registered_scorer_reports_its_own_version() -> None:
    """The registry key and the record's label cannot drift apart."""
    for version, entry in SCORERS.items():
        assert entry.version == version
        assert entry.bands, f"{version} declares no bands"
        assert len(set(entry.bands)) == len(entry.bands), f"{version} repeats a band name"


def test_salience_bands_are_ordered_strongest_first() -> None:
    assert salience_bands() == ("federal", "high", "state", "elevated", "baseline")


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


def test_decided_petition_is_scored_but_never_cohorted(tmp_path: Path) -> None:
    # A historical, already-decided docket still carries a distribution
    # conference, but it has no open event left to predict — the pass must
    # score it (the board wants a band) without ever latching it selected.
    db = _seed(
        tmp_path,
        [_petition("scotus/decided", distribution_count=3, date_cert_denied=date(2026, 1, 12))],
    )
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, SalienceConfig(), apply=True)
        row = corpus.get_row(conn, "scotus/decided")
    assert row is not None
    assert row.salience_score is not None  # scored
    assert row.salience_selected is False  # never cohorted, so never latched
    assert result.newly_selected == 0


def test_decided_petition_never_displaces_an_open_petition_within_capacity(tmp_path: Path) -> None:
    # A decided high-relist docket sharing a conference with a still-open,
    # lower-relist one must not eat into the open petition's cap — it is
    # excluded from the cohort entirely, not merely outranked.
    rows = [
        _petition("scotus/decided", distribution_count=3, date_cert_denied=date(2026, 1, 12)),
        _petition("scotus/open", distribution_count=1),
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=1, floor=0.28)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert _selected_ids(db) == {"scotus/open"}


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


def test_selection_plan_equals_wrapper_free_plan_cohorts(tmp_path: Path) -> None:
    # The conn-free core must be bit-identical to the live pass over the same
    # rows — including the scores dict's insertion order and to_select's cohort
    # extension order — so a replay through `plan_cohorts` reproduces the gate.
    rows = [
        _petition("scotus/a", distribution_count=1),  # ranked, ties on score
        _petition("scotus/b", distribution_count=1),
        _petition("scotus/c", distribution_count=1, selected=True),  # already latched
        _petition("scotus/hot", distribution_count=3),  # above-floor carve-out
        _petition("scotus/cvsg", distribution_count=1, cvsg=True),  # CVSG carve-out
        _petition("scotus/late", distribution_count=2, conference=date(2026, 2, 20)),
        _petition("scotus/pending", distribution_count=2, conference=None),  # no cohort
        _petition(  # decided: scored, never cohorted
            "scotus/done", distribution_count=3, date_cert_denied=date(2026, 1, 12)
        ),
        _petition("scotus/app", docket="25A100"),  # Tier-0 out of scope: filtered
        _petition("scotus/ifp", docket="25-5100"),  # Tier-0 IFP: filtered
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=1, floor=0.28)
    with corpus.connect(db) as conn:
        direct = _selection_plan(conn, config)
        eligible = [
            row
            for row in corpus.iter_rows(conn, court="scotus")
            if corpus.out_of_scope_reason_full(conn, row) is None
        ]
    assert plan_cohorts(eligible, config) == direct
    scores, to_select, eligible_count, conferences = direct
    assert eligible_count == 8  # the two Tier-0 rows never enter
    assert conferences == 2
    # The equivalence above is order-sensitive on both compound members.
    assert list(plan_cohorts(eligible, config)[0]) == list(scores)
    assert plan_cohorts(eligible, config)[1] == to_select


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
    assert config.per_conference_capacity == 12
    assert config.long_conference_capacity == 24
    assert config.floor == 0.28
    assert config.base_rate_lookback_terms == 0  # unbounded: every prior Term


def test_load_salience_config_reads_the_base_rate_lookback(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text("salience:\n  base_rate_lookback_terms: 5\n")
    assert load_salience_config(tmp_path).base_rate_lookback_terms == 5


def test_salience_config_rejects_a_negative_lookback() -> None:
    with pytest.raises(ValueError):
        SalienceConfig(base_rate_lookback_terms=-1)


def test_salience_config_rejects_a_smaller_long_conference_cap() -> None:
    with pytest.raises(ValueError, match="long_conference_capacity must be >="):
        SalienceConfig(per_conference_capacity=200, long_conference_capacity=100)


# --- the production caps under long-conference pressure -------------------------
#
# Every test above uses an artificial N of 1-3 over a handful of rows, which
# proves the mechanics but never exercises the caps actually configured. The
# September long conference is the first time the cap binds in production — it
# distributes ~276 petitions at once against `long_conference_capacity`, and the
# realized count is what the release costs. These tests pin that number and the
# invariants that must hold when the cohort is far larger than N.

# A long-conference composition. It clears the summer backlog, so newly-filed
# first distributions dominate; a minority arrive already relisted from the prior
# Term's close, and a handful carry a CVSG. Counts sum to 276, the observed
# long-conference distribution volume recorded in `config/tracking.yaml`.
_LC_RELIST_0 = 240  # first distribution — baseline band, score ~0.008 + circuit nudge
_LC_RELIST_1 = 25  # elevated band (~0.078); still below the floor
_LC_RELIST_2 = 8  # ~0.394 — at/above the floor, so a carve-out
_LC_CVSG = 3  # carve-out by CVSG regardless of relist count
_LC_TOTAL = _LC_RELIST_0 + _LC_RELIST_1 + _LC_RELIST_2 + _LC_CVSG
_LC_CARVE_OUTS = _LC_RELIST_2 + _LC_CVSG


def _long_conference_cohort() -> list[corpus.CorpusRow]:
    """~276 petitions distributed for one long conference, realistically mixed."""
    rows: list[corpus.CorpusRow] = []
    # Zero-padded ids so the cap's lexical case_id tie-break is numeric order here,
    # which is what makes the kept prefix predictable rather than incidental.
    for i in range(_LC_RELIST_0):
        rows.append(
            _petition(f"scotus/r0-{i:04d}", distribution_count=1, conference=LONG_CONFERENCE)
        )
    for i in range(_LC_RELIST_1):
        rows.append(
            _petition(f"scotus/r1-{i:04d}", distribution_count=2, conference=LONG_CONFERENCE)
        )
    for i in range(_LC_RELIST_2):
        rows.append(
            _petition(f"scotus/r2-{i:04d}", distribution_count=3, conference=LONG_CONFERENCE)
        )
    for i in range(_LC_CVSG):
        rows.append(
            _petition(
                f"scotus/cv-{i:04d}", distribution_count=1, cvsg=True, conference=LONG_CONFERENCE
            )
        )
    return rows


def test_long_conference_realized_count_is_n_plus_carveouts(tmp_path: Path) -> None:
    """The number the September release costs: N ranked picks PLUS the carve-outs.

    `N` is a guaranteed floor, not a ceiling, so the realized count is strictly
    above it — the property that makes the budget a floor too. Pinned against the
    configured caps rather than an artificial one, because a change to either the
    cap or the carve-out rule should move this number visibly.
    """
    db = _seed(tmp_path, _long_conference_cohort())
    config = load_salience_config(Path("config"))  # the caps actually in force
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, config, apply=True)

    selected = _selected_ids(db)
    assert result.eligible_cases == _LC_TOTAL
    assert len(selected) == config.long_conference_capacity + _LC_CARVE_OUTS
    assert result.newly_selected == len(selected)
    # The whole cohort is scored even though most of it is not funded: the board
    # publishes a ranking over the candidate pool, not just the selected slice.
    assert result.scored == _LC_TOTAL
    assert result.conferences == 1


def test_every_carveout_survives_a_cohort_far_larger_than_n(tmp_path: Path) -> None:
    """No case at or above the floor is ever below the capacity line.

    The load-bearing promise of the design — "a major case can never fall below
    the capacity line" — and the one that cannot be checked at fixture scale,
    because the cap has to actually bite for the question to mean anything.
    """
    db = _seed(tmp_path, _long_conference_cohort())
    config = load_salience_config(Path("config"))
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)

    selected = _selected_ids(db)
    assert all(f"scotus/r2-{i:04d}" in selected for i in range(_LC_RELIST_2))
    assert all(f"scotus/cv-{i:04d}" in selected for i in range(_LC_CVSG))
    # And the cap did bite, so the assertion above is not vacuous.
    assert len(selected) < _LC_TOTAL


def test_the_cap_prefers_higher_scores_before_it_fills_with_ties(tmp_path: Path) -> None:
    """Ranking, not arrival order: every relisted petition is funded before any
    first-distribution one, because the cohort is ranked by score before the fill."""
    db = _seed(tmp_path, _long_conference_cohort())
    config = load_salience_config(Path("config"))
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)

    selected = _selected_ids(db)
    capacity = config.long_conference_capacity
    funded_r1 = sum(1 for s in selected if s.startswith("scotus/r1-"))
    funded_r0 = sum(1 for s in selected if s.startswith("scotus/r0-"))
    # Relist-1 outranks relist-0, so the rank fill is spent on relist-1 first and
    # reaches relist-0 only once every relist-1 petition is funded. Expressed
    # against the configured capacity rather than a literal, so the property
    # under test is the RANKING and the test survives a re-sizing of the gate.
    assert funded_r1 == min(_LC_RELIST_1, capacity)
    assert funded_r0 == max(0, capacity - _LC_RELIST_1)
    assert funded_r0 + funded_r1 == capacity  # the fill is exactly the cap
    # The tail of the weaker band is always cut: the cohort is far larger than
    # any capacity this gate is funded at.
    assert f"scotus/r0-{_LC_RELIST_0 - 1:04d}" not in selected


def test_selection_over_a_large_cohort_is_reproducible(tmp_path: Path) -> None:
    """Two independent passes over identical input select an identical set.

    Replay is a pure read of committed columns, which only holds if the ranking is
    deterministic where scores tie — and at this scale almost everything ties.
    """
    config = load_salience_config(Path("config"))
    runs = []
    for name in ("a", "b"):
        db = _seed(tmp_path / name, _long_conference_cohort())
        with corpus.connect(db) as conn:
            reconcile_salience_selection(conn, config, apply=True)
        runs.append(_selected_ids(db))
    assert runs[0] == runs[1]


# --- the interim reserve --------------------------------------------------------


def _application(  # a keyword-only test fixture builder, one arg per row feature
    case_id: str,
    docket: str,
    *,
    kind: str | None = "substantive",
    requested: bool = False,
    referred: bool = False,
    amici: int = 0,
    selected: bool = False,
    disposition: str | None = None,
) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {
            "case_id": case_id,
            "court": "scotus",
            "docket_number": docket,
            "application_kind": kind,
            "response_requested": requested,
            "referred_to_court": referred,
            "amicus_briefs": amici,
            "salience_selected": selected,
            "disposition": disposition,
            "date_decided": date(2026, 1, 20) if disposition else None,
        }
    )


def test_unlatch_overselected_clears_the_resize_overhang(tmp_path: Path) -> None:
    """The one-time reconcile for a capacity resize: the from-scratch pick
    survives, the pre-resize overflow clears, carve-outs stay above N, a dry
    run writes nothing, and a second apply clears nothing (idempotent)."""
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "abcde"]
    rows.append(_petition("scotus/cvsg", distribution_count=1, cvsg=True))
    db = _seed(tmp_path, rows)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(
            conn, SalienceConfig(per_conference_capacity=3, floor=0.28), apply=True
        )
    assert _selected_ids(db) == {"scotus/a", "scotus/b", "scotus/c", "scotus/cvsg"}
    resized = SalienceConfig(per_conference_capacity=1, floor=0.28)
    with corpus.connect(db) as conn:
        dry = unlatch_overselected(conn, resized, apply=False)
    assert dry.applied is False and dry.unlatched == 2 and dry.retained == 2
    assert _selected_ids(db) == {"scotus/a", "scotus/b", "scotus/c", "scotus/cvsg"}
    with corpus.connect(db) as conn:
        applied = unlatch_overselected(conn, resized, apply=True)
    assert applied.applied is True and applied.unlatched == 2
    assert applied.unlatched_case_ids == ["scotus/b", "scotus/c"]
    assert _selected_ids(db) == {"scotus/a", "scotus/cvsg"}
    with corpus.connect(db) as conn:
        again = unlatch_overselected(conn, resized, apply=True)
    assert again.unlatched == 0 and again.retained == 2


def test_unlatch_overselected_spares_decided_rows_and_applications(tmp_path: Path) -> None:
    """The reconcile's blast radius is pending cohort petitions only: a decided
    petition keeps its latch as the historical record of selection, and a
    latched pending application (the interim reserve's occupancy) is its own
    sticky contract."""
    rows = [
        _petition("scotus/pending", distribution_count=1, selected=True),
        _petition(
            "scotus/decided",
            distribution_count=1,
            selected=True,
            date_cert_denied=date(2026, 2, 1),
        ),
        _application("scotus/9525000001", "25A1", selected=True),
    ]
    db = _seed(tmp_path, rows)
    with corpus.connect(db) as conn:
        result = unlatch_overselected(
            conn, SalienceConfig(per_conference_capacity=1, floor=0.28), apply=True
        )
    # The lone pending petition survives at N=1; the decided row and the
    # application were never candidates, so nothing clears.
    assert result.unlatched == 0 and result.latched_pending == 1
    assert _selected_ids(db) == {"scotus/pending", "scotus/decided", "scotus/9525000001"}


def test_unlatch_overselected_counts_what_it_spares(tmp_path: Path) -> None:
    """The ledger reconciles against the corpus: a latched pending petition
    outside every cohort — never distributed, or Tier-0 excluded (IFP) — is
    spared AND counted, so "cleared X of Y" reads against a stated remainder."""
    rows = [
        _petition("scotus/incohort", distribution_count=1, selected=True),
        _petition("scotus/undistributed", distribution_count=1, selected=True, conference=None),
        _petition("scotus/ifp", distribution_count=1, selected=True, docket="25-5044"),
    ]
    db = _seed(tmp_path, rows)
    with corpus.connect(db) as conn:
        result = unlatch_overselected(
            conn, SalienceConfig(per_conference_capacity=1, floor=0.28), apply=True
        )
    assert result.latched_pending == 1  # only the cohort member was examined
    assert result.spared_undistributed == 1
    assert result.spared_out_of_scope == 1
    assert _selected_ids(db) == {"scotus/incohort", "scotus/undistributed", "scotus/ifp"}


def test_unlatch_retains_what_a_filled_reserve_would_displace(tmp_path: Path) -> None:
    """The reserve=0 safety claim: the reconcile ranks with no reserve, so a
    latched petition a filled interim reserve would displace from the live
    pass's fill is retained — permissive in exactly the destructive direction."""
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "ab"]
    rows.append(_application("scotus/9525000001", "25A1"))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=2, floor=0.28, interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    # The live pass funds the application + 1 cert fill; latch 'b' by hand to
    # simulate a pre-resize latch the reserve would now displace.
    with corpus.connect(db) as conn:
        corpus.latch_salience_selected(conn, ["scotus/b"])
        result = unlatch_overselected(conn, config, apply=True)
    assert result.unlatched == 0 and result.retained == 2  # 'a' and 'b' both kept
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/a", "scotus/b"}


def test_unlatch_then_live_pass_is_stable(tmp_path: Path) -> None:
    """No oscillation: after an applied reconcile, the live selection pass under
    the same config re-latches nothing — the cleared rows re-enter as
    candidates and lose to the same retained set."""
    db = _seed(tmp_path, [_petition(f"scotus/{c}", distribution_count=1) for c in "abcd"])
    with corpus.connect(db) as conn:
        reconcile_salience_selection(
            conn, SalienceConfig(per_conference_capacity=3, floor=0.28), apply=True
        )
    resized = SalienceConfig(per_conference_capacity=1, floor=0.28)
    with corpus.connect(db) as conn:
        unlatch_overselected(conn, resized, apply=True)
    assert _selected_ids(db) == {"scotus/a"}
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, resized, apply=True)
    assert result.newly_selected == 0
    assert _selected_ids(db) == {"scotus/a"}


def test_reserve_selects_pending_applications_and_shrinks_the_cert_fill(tmp_path: Path) -> None:
    # Three below-floor petitions at N=2 beside one pending substantive
    # application, reserve 1: the application is selected and the cert rank
    # fill shrinks to 1 — the reserve trades inside N, never adds to it.
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "abc"]
    rows.append(_application("scotus/9525000001", "25A1"))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=2, floor=0.28, interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/a"}


def test_reserve_never_displaces_a_carve_out(tmp_path: Path) -> None:
    # Carve-outs sit above N, so the reserve displaces only the rank fill: a
    # CVSG petition survives even when the reserve consumes the whole cap.
    rows = [
        _petition("scotus/cvsg", distribution_count=1, cvsg=True),
        _petition("scotus/ranked", distribution_count=1),
        _application("scotus/9525000001", "25A1"),
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=1, floor=0.28, interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/cvsg"}


def test_unfilled_reserve_returns_to_cert(tmp_path: Path) -> None:
    # Slots bound the reserve; only the slots actually in use displace. One
    # pending application under a reserve of 5 shrinks the fill by exactly 1.
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "abc"]
    rows.append(_application("scotus/9525000001", "25A1"))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=3, floor=0.28, interim_reserve_slots=5)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/a", "scotus/b"}


def test_reserve_picks_climb_the_escalation_ladder(tmp_path: Path) -> None:
    # Pick order is the two-signal ladder, strongest first — a requested
    # response, then the amicus count — a deterministic ordering, not a
    # scored rate.
    rows = [
        _application("scotus/9525000001", "25A1"),  # no signals
        _application("scotus/9525000002", "25A2", requested=True),
        _application("scotus/9525000003", "25A3", amici=2),
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(interim_reserve_slots=2)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    # The requested-response application outranks the amicus-carrying one; the
    # signal-less one waits for a freed slot.
    assert _selected_ids(db) == {"scotus/9525000002", "scotus/9525000003"}


def test_reserve_ladder_orders_by_amicus_count_and_breaks_ties_on_case_id(
    tmp_path: Path,
) -> None:
    # Within a rung the amicus count orders (more first); an exact tie breaks
    # deterministically on case_id, ascending.
    rows = [
        _application("scotus/9525000004", "25A4", amici=1),
        _application("scotus/9525000003", "25A3", amici=3),
        _application("scotus/9525000002", "25A2", amici=1),
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(interim_reserve_slots=2)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    # amici=3 first, then the amici=1 tie resolves to the lower case_id.
    assert _selected_ids(db) == {"scotus/9525000002", "scotus/9525000003"}


def test_reserve_ladder_ignores_the_referral_signal(tmp_path: Path) -> None:
    # The exclusion is the contract: a referral is usually the disposition
    # entry itself, so it carries no forecast horizon and buys no rank — a
    # referred-but-otherwise-signal-less application does NOT outrank one
    # carrying amici.
    rows = [
        _application("scotus/9525000001", "25A1", referred=True),
        _application("scotus/9525000002", "25A2", amici=1),
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    assert _selected_ids(db) == {"scotus/9525000002"}


def test_reserve_slots_are_occupied_until_resolution(tmp_path: Path) -> None:
    # A still-pending selected application keeps its slot (the sticky latch),
    # so a newcomer waits; once the occupant resolves, the freed slot goes to
    # the newcomer on the next pass — and the resolved one is never de-selected.
    db = _seed(
        tmp_path,
        [
            _application("scotus/9525000001", "25A1", selected=True),
            _application("scotus/9525000002", "25A2", requested=True),
        ],
    )
    config = SalienceConfig(interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        first = reconcile_salience_selection(conn, config, apply=True)
    assert first.newly_selected == 0  # the slot is occupied
    assert _selected_ids(db) == {"scotus/9525000001"}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [_application("scotus/9525000001", "25A1", selected=True, disposition="denied")]
        )
        second = reconcile_salience_selection(conn, config, apply=True)
    assert second.newly_selected == 1
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/9525000002"}


def test_reserve_displaces_only_the_current_conference(tmp_path: Path) -> None:
    # The application is live in the cycle whose conference the pass is
    # filling — the latest cohort — so an earlier conference's fill is intact.
    earlier, later = date(2026, 1, 9), date(2026, 2, 20)
    rows = [
        _petition("scotus/e1", distribution_count=1, conference=earlier),
        _petition("scotus/e2", distribution_count=1, conference=earlier),
        _petition("scotus/l1", distribution_count=1, conference=later),
        _petition("scotus/l2", distribution_count=1, conference=later),
        _application("scotus/9525000001", "25A1"),
    ]
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=2, floor=0.28, interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, config, apply=True)
    # Earlier cohort keeps both; the later (current) one shrinks to 1.
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/e1", "scotus/e2", "scotus/l1"}


def test_reserve_zero_keeps_applications_deferred_and_reserve_gates_predict_scope(
    tmp_path: Path,
) -> None:
    # The quota is the whole gate: with slots 0 a substantive application is
    # scored-and-deferred, and the shared predict-scope predicate drops it —
    # while a selected one passes. Fail-open before any pass has scored it.
    db = _seed(tmp_path, [_application("scotus/9525000001", "25A1")])
    assert _in_predict_scope(db, "scotus/9525000001") is True  # unscored: fail-open
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, SalienceConfig(interim_reserve_slots=0), apply=True)
    assert _selected_ids(db) == set()
    assert _in_predict_scope(db, "scotus/9525000001") is False  # scored, deferred
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, SalienceConfig(interim_reserve_slots=1), apply=True)
    assert _in_predict_scope(db, "scotus/9525000001") is True  # reserve-selected


def test_reserve_pass_is_idempotent(tmp_path: Path) -> None:
    # Convergence under the sticky latch: a second pass with no corpus change
    # latches nothing new and keeps the same displacement.
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "ab"]
    rows.append(_application("scotus/9525000001", "25A1"))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=2, floor=0.28, interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        first = reconcile_salience_selection(conn, config, apply=True)
        again = reconcile_salience_selection(conn, config, apply=True)
    assert first.newly_selected == 2  # the application + the one remaining fill
    assert again.newly_selected == 0
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/a"}


# --- the registry under a second version ---------------------------------------
#
# Every claim the registry makes is about what happens when a SECOND scorer
# exists, so the single shipped version cannot exercise any of it: a loop over
# one entry passes with the loop deleted. These tests register a toy scorer with
# a deliberately DIFFERENT band vocabulary — so a band name leaking across
# versions shows up as a KeyError rather than as a plausible number — and are
# the only place the multi-version paths run at all.


def test_a_second_version_is_reachable_and_the_active_one_is_unchanged(
    two_versions: SalienceScorer,
) -> None:
    assert registered_versions() == (SALIENCE_VERSION, "sal-toy", "sal-v1")  # active first
    row = _petition("scotus/1", distribution_count=3, cvsg=True)
    assert scorer("sal-toy").band(row) == "hot"
    assert salience_band(row) == "high"  # the bare helpers still mean the ACTIVE scorer
    assert salience_bands() == ("federal", "high", "state", "elevated", "baseline")


def test_each_version_selects_under_its_own_scorer(two_versions: SalienceScorer) -> None:
    """The same rows, two scorers, two different picks — which is the whole point.

    sal-v1 carves in the CVSG petition and rank-fills the rest to `N`; the toy
    carves in the CVSG petition and, having no rank order worth the name, still
    fills to `N`. What must differ is the *scoring*, and what must not differ is
    the population either one sees."""
    rows = [_petition(f"scotus/{i}", distribution_count=3) for i in range(4)]
    rows.append(_petition("scotus/cvsg", distribution_count=1, cvsg=True))
    config = SalienceConfig(per_conference_capacity=2, floor=0.28)

    v1_scores, v1_pick, v1_eligible, _ = plan_cohorts(rows, config)
    toy_scores, toy_pick, toy_eligible, _ = plan_cohorts(rows, config, version=two_versions)

    assert v1_eligible == toy_eligible == len(rows)  # same population, both times
    assert v1_scores != toy_scores  # different scale
    assert set(v1_pick) != set(toy_pick) or v1_scores["scotus/0"] != toy_scores["scotus/0"]
    # sal-v1 puts every relist-2 row in `high` and above the floor, so all four
    # carve in; the toy scores them 0.1 and carves in only the CVSG row.
    assert set(v1_pick) == {f"scotus/{i}" for i in range(4)} | {"scotus/cvsg"}
    assert "scotus/cvsg" in toy_pick


def test_a_scorers_band_function_only_ever_returns_a_declared_band(
    two_versions: SalienceScorer,
) -> None:
    """The registry's core consistency invariant, and the one the statpack relies on.

    `analytics._TermAcc` indexes `segments[version][band]` and calls
    `bands.index(band)`, so a scorer whose band function returns a label outside
    its own `bands` raises rather than mis-slicing — but it raises deep inside a
    streaming corpus pass, which is a poor place to learn it."""
    for version in registered_versions():
        banding = scorer(version)
        for distribution_count in (1, 2, 3, None):
            for cvsg in (False, True):
                row = _petition("scotus/x", distribution_count=distribution_count, cvsg=cvsg)
                assert banding.band(row) in banding.bands, (
                    f"{version} banded a row {banding.band(row)!r}, "
                    f"which is not among {banding.bands}"
                )


def test_arrival_draw_is_deterministic_and_rate_honest() -> None:
    """The random slice's whole contract: the same id always draws the same
    answer under the committed key, the endpoints are exact, and the realized
    fraction over a large id population sits at the rate — an auditable
    property, not a trusted one."""
    # Golden vectors pin the exact mapping — key, separator, truncation, and
    # endianness together: any change to the wire format re-draws the whole
    # pre-registered slice and must fail here first.
    assert not arrival_draw("scotus/26000001", 0.05)  # digest head 1265526251733217086
    assert arrival_draw("scotus/26000058", 0.05)  # digest head 69070351232753145
    assert not arrival_draw("scotus/26000001", 0.0)
    assert arrival_draw("scotus/26000001", 1.0)
    ids = [f"scotus/26{n:06d}" for n in range(20_000)]
    realized = sum(arrival_draw(cid, 0.05) for cid in ids) / len(ids)
    assert abs(realized - 0.05) < 0.005, realized
    # Rate monotonicity: structural for this implementation (fixed hash,
    # monotone threshold) — pinned as the guard against a future bucketing
    # rewrite (e.g. digest % 100), where nesting genuinely can fail.
    lower = {cid for cid in ids[:2000] if arrival_draw(cid, 0.02)}
    higher = {cid for cid in ids[:2000] if arrival_draw(cid, 0.10)}
    assert lower <= higher


def test_sal_v2_selects_the_arrival_cohort_by_predicate() -> None:
    """The arrival cohort under sal-v2: an undistributed pending petition is
    selected by the deterministic draw or the federal carve-in — no rank, no
    capacity — while sal-v1 (docket-acquired features only) selects none of
    them, and a distributed petition never enters the arrival pass."""
    config = SalienceConfig(per_conference_capacity=2, floor=0.28, arrival_sample_rate=0.05)
    rows = [
        # In the 1-in-20 slice at 0.05 (golden vector from the draw tests).
        _petition("scotus/26000058", distribution_count=None, conference=None, docket="26-58"),
        # Out of the slice, private petitioner: not selected.
        _petition("scotus/26000001", distribution_count=None, conference=None, docket="26-1"),
        # Out of the slice, federal petitioner: the carve-in takes it.
        _petition(
            "scotus/26000002",
            distribution_count=None,
            conference=None,
            docket="26-2",
            petitioner_title="United States",
        ),
        # Distributed: the escalation cohort's business, never the arrival pass.
        _petition("scotus/26000003", distribution_count=1, docket="26-3"),
    ]
    _, v2_select, _, _ = plan_cohorts(rows, config, version=SCORERS["sal-v2"])
    assert "scotus/26000058" in v2_select  # the draw
    assert "scotus/26000002" in v2_select  # the federal carve-in
    assert "scotus/26000001" not in v2_select
    _, v1_select, _, _ = plan_cohorts(rows, config, version=SCORERS["sal-v1"])
    assert not {"scotus/26000058", "scotus/26000001", "scotus/26000002"} & set(v1_select)


def test_an_arrival_pick_mints_its_event_in_the_same_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Latch and event arrive together: an arrival-selected undistributed
    petition leaves the pass with evt-petition-arrival-disposition open beside
    its baseline, so the sweep has the right — and only the right — cell to
    queue (the baseline waits for its own distribution moment)."""
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-v2")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row = _petition(
        "scotus/26000002",
        distribution_count=None,
        conference=None,
        docket="26-2",
        petitioner_title="United States",
    ).model_copy(update={"date_filed": date(2026, 7, 20)})
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=row.case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                )
            ],
        )
        selected = apply_salience_selection(
            conn, SalienceConfig(per_conference_capacity=2, floor=0.28)
        )
        assert row.case_id in selected
        events = {e.event_id for e in corpus.events_for_case(conn, row.case_id)}
    assert "evt-petition-arrival-disposition" in events
