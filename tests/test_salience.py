"""Tests for the salience gate: the frozen sal-v1 scorer and the selection pass."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import MappingProxyType

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.config import SalienceConfig, load_salience_config
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cell_context
from fedcourtsai.pipeline import salience as salience_module
from fedcourtsai.pipeline.cert_signals import DEFAULT_DISTRIBUTION_PARSE, DISTRIBUTION_PARSES
from fedcourtsai.pipeline.pull import _in_predict_scope
from fedcourtsai.pipeline.salience import (
    _ARRIVAL_EVENT_ID,
    _CIRCUIT_GRANT_RATE,
    SALIENCE_VERSION,
    SCORERS,
    SalienceScorer,
    _selection_plan,
    apply_salience_selection,
    arrival_draw,
    carve_out,
    distribution_census,
    plan_cohorts,
    reconcile_salience_selection,
    registered_versions,
    salience_band,
    salience_bands,
    salience_score,
    scorer,
    unlatch_overselected,
)
from fedcourtsai.schemas import Disposition, EventKind, Stage

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
    identity; the caption-banded versions' is (federal, high), whichever
    caption rule reads the class. Pinning the expected prefix keeps
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
    titles = (
        "United States",
        "State of Texas",
        "John Doe",
        # federal under caption-v2 only, so the lattice spans the class axis of
        # every registered caption rule and not just the one sal-v2 reads.
        "Office of the United States Trustee",
        None,
    )
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
    expected = {
        "sal-v1": ("high",),
        "sal-v2": ("federal", "high"),
        "sal-v3": ("federal", "high"),
    }.get(version, banding.bands[: len(fully_carved)] if fully_carved else None)
    assert fully_carved == expected, f"{version}: carved bands {fully_carved}, expected {expected}"
    assert fully_carved, f"{version}: no band is carved — the always-include rule reaches nothing"


def test_sal_v3_is_sal_v2_read_through_the_wider_caption_rule() -> None:
    """The only thing sal-v3 moves is which captions read `federal`.

    Same ranking score, same band vocabulary, same carve-in shape — so on a
    caption both rules agree about, the two versions are indistinguishable, and
    on a caption only caption-v2 reads as federal, sal-v3 bands and carves it
    while sal-v2 leaves it on its trajectory tier. Pinning both halves is what
    keeps the delta attributable to the caption rule rather than to a quiet
    refit riding along with it."""
    v2, v3 = scorer("sal-v2"), scorer("sal-v3")
    assert v3.bands == v2.bands
    assert v3.selects_arrivals is v2.selects_arrivals
    floor = load_salience_config(Path("config")).floor

    for title in ("United States", "State of Texas", "John Doe", None):
        row = _petition("scotus/agreed", distribution_count=1, petitioner_title=title)
        assert v3.score(row) == v2.score(row), title
        assert v3.band(row) == v2.band(row), title
        assert v3.carve_out(row, v3.score(row), floor) == v2.carve_out(row, v2.score(row), floor)

    widened = _petition(
        "scotus/widened",
        distribution_count=1,  # relist-0: nothing but the caption can carve it in
        petitioner_title="Office of the United States Trustee",
    )
    assert v2.band(widened) == "baseline"
    assert v2.carve_out(widened, v2.score(widened), floor) is False
    assert v3.band(widened) == "federal"
    assert v3.carve_out(widened, v3.score(widened), floor) is True


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


def _data_root(tmp_path: Path) -> Path:
    """The git ledger root the pass mints each arrival event's `event.yaml` into."""
    return tmp_path / "data"


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
        result = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
    assert _selected_ids(db) == {"scotus/a", "scotus/b"}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_petition("scotus/hot", distribution_count=2)])  # relist-1
        result = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
            conn,
            _data_root(tmp_path),
            SalienceConfig(per_conference_capacity=1, floor=0.28),
            apply=True,
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
    assert len(_selected_ids(db)) == 3  # the long-conference cap, not the regular 1


def test_petition_not_yet_distributed_is_scored_but_not_selected(tmp_path: Path) -> None:
    db = _seed(tmp_path, [_petition("scotus/pending", distribution_count=3, conference=None)])
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, _data_root(tmp_path), SalienceConfig(), apply=True)
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
        result = reconcile_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(), apply=True
        )
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
    assert _selected_ids(db) == {"scotus/open"}


def test_out_of_scope_petition_is_not_scored(tmp_path: Path) -> None:
    # A non-cert SCOTUS form (an application, 25A100) is Tier-0 out of scope, so
    # the pass never scores or selects it.
    db = _seed(tmp_path, [_petition("scotus/app", docket="25A100", distribution_count=3)])
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(), apply=True
        )
        row = corpus.get_row(conn, "scotus/app")
    assert result.eligible_cases == 0
    assert row is not None and row.salience_score is None and row.salience_selected is False


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    db = _seed(tmp_path, [_petition("scotus/1", distribution_count=3)])
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(), apply=False
        )
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
        result = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)

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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)

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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)

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
            reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
            conn,
            _data_root(tmp_path),
            SalienceConfig(per_conference_capacity=3, floor=0.28),
            apply=True,
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
            conn,
            _data_root(tmp_path),
            SalienceConfig(per_conference_capacity=3, floor=0.28),
            apply=True,
        )
    resized = SalienceConfig(per_conference_capacity=1, floor=0.28)
    with corpus.connect(db) as conn:
        unlatch_overselected(conn, resized, apply=True)
    assert _selected_ids(db) == {"scotus/a"}
    with corpus.connect(db) as conn:
        result = reconcile_salience_selection(conn, _data_root(tmp_path), resized, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
    assert _selected_ids(db) == {"scotus/9525000001", "scotus/cvsg"}


def test_unfilled_reserve_returns_to_cert(tmp_path: Path) -> None:
    # Slots bound the reserve; only the slots actually in use displace. One
    # pending application under a reserve of 5 shrinks the fill by exactly 1.
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "abc"]
    rows.append(_application("scotus/9525000001", "25A1"))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=3, floor=0.28, interim_reserve_slots=5)
    with corpus.connect(db) as conn:
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        first = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
    assert first.newly_selected == 0  # the slot is occupied
    assert _selected_ids(db) == {"scotus/9525000001"}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [_application("scotus/9525000001", "25A1", selected=True, disposition="denied")]
        )
        second = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
        reconcile_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(interim_reserve_slots=0), apply=True
        )
    assert _selected_ids(db) == set()
    assert _in_predict_scope(db, "scotus/9525000001") is False  # scored, deferred
    with corpus.connect(db) as conn:
        reconcile_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(interim_reserve_slots=1), apply=True
        )
    assert _in_predict_scope(db, "scotus/9525000001") is True  # reserve-selected


def test_reserve_pass_is_idempotent(tmp_path: Path) -> None:
    # Convergence under the sticky latch: a second pass with no corpus change
    # latches nothing new and keeps the same displacement.
    rows = [_petition(f"scotus/{c}", distribution_count=1) for c in "ab"]
    rows.append(_application("scotus/9525000001", "25A1"))
    db = _seed(tmp_path, rows)
    config = SalienceConfig(per_conference_capacity=2, floor=0.28, interim_reserve_slots=1)
    with corpus.connect(db) as conn:
        first = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
        again = reconcile_salience_selection(conn, _data_root(tmp_path), config, apply=True)
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
    # active first, then the rest sorted
    assert registered_versions() == (SALIENCE_VERSION, "sal-toy", "sal-v1", "sal-v2")
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
    filed = {"date_filed": date(2026, 7, 20)}  # past the cohort-start bound
    rows = [
        # In the 1-in-20 slice at 0.05 (golden vector from the draw tests).
        _petition(
            "scotus/26000058", distribution_count=None, conference=None, docket="26-58"
        ).model_copy(update=filed),
        # Out of the slice, private petitioner: not selected.
        _petition(
            "scotus/26000001", distribution_count=None, conference=None, docket="26-1"
        ).model_copy(update=filed),
        # Out of the slice, federal petitioner: the carve-in takes it.
        _petition(
            "scotus/26000002",
            distribution_count=None,
            conference=None,
            docket="26-2",
            petitioner_title="United States",
        ).model_copy(update=filed),
        # Distributed: the escalation cohort's business, never the arrival pass.
        _petition("scotus/26000003", distribution_count=1, docket="26-3"),
        # Filed before the cohort-start bound: the standing backlog, out even
        # though federal — the backlog earns escalation selection, never an
        # arrival cell (the fixture default date_filed is pre-boundary).
        _petition(
            "scotus/26000004",
            distribution_count=None,
            conference=None,
            docket="25-4",
            petitioner_title="United States",
        ),
        # No filing date at all: no arrival moment to select at.
        _petition(
            "scotus/26000005",
            distribution_count=None,
            conference=None,
            docket="26-5",
            petitioner_title="United States",
        ).model_copy(update={"date_filed": None}),
    ]
    _, v2_select, _, _ = plan_cohorts(rows, config, version=SCORERS["sal-v2"])
    assert "scotus/26000058" in v2_select  # the draw
    assert "scotus/26000002" in v2_select  # the federal carve-in
    assert "scotus/26000001" not in v2_select
    assert "scotus/26000004" not in v2_select  # pre-boundary backlog
    assert "scotus/26000005" not in v2_select  # dateless
    _, v1_select, _, _ = plan_cohorts(rows, config, version=SCORERS["sal-v1"])
    assert not {"scotus/26000058", "scotus/26000001", "scotus/26000002"} & set(v1_select)


_ARRIVAL_CASE_ID = "scotus/26000002"  # enters the sal-v2 cohort by the federal carve-in


def _arrival_case(tmp_path: Path) -> Path:
    """A corpus holding one arrival-eligible pick: undistributed, in-cohort, baseline open."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row = _petition(
        _ARRIVAL_CASE_ID,
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
    return db


def _arrival_ledger_file(tmp_path: Path) -> Path:
    court, _, docket = _ARRIVAL_CASE_ID.partition("/")
    return CasePaths(_data_root(tmp_path), court, int(docket)).event(_ARRIVAL_EVENT_ID).event_file


def _arrival_pass(db: Path, tmp_path: Path) -> set[str]:
    """One selection pass over ``db``; returns the case's corpus event ids."""
    with corpus.connect(db) as conn:
        apply_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(per_conference_capacity=2, floor=0.28)
        )
        return {e.event_id for e in corpus.events_for_case(conn, _ARRIVAL_CASE_ID)}


def test_an_arrival_pick_mints_both_halves_of_its_event_in_the_same_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Latch and event arrive together, and the event arrives whole: an
    arrival-selected undistributed petition leaves the pass with
    evt-petition-arrival-disposition open beside its baseline *and* its ledger
    `event.yaml` written, because a declared moment's two halves are one mint.
    Git is the pre-registration record, so the day a case became forecastable
    is committed at the mint rather than at whatever later touch occurs."""
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-v2")
    db = _arrival_case(tmp_path)
    events = _arrival_pass(db, tmp_path)
    assert _ARRIVAL_EVENT_ID in events
    ledger = _arrival_ledger_file(tmp_path)
    assert ledger.is_file()
    defined = yaml.safe_load(ledger.read_text())
    assert defined["event_id"] == _ARRIVAL_EVENT_ID
    assert defined["case_id"] == _ARRIVAL_CASE_ID
    assert defined["resolved"] is False


def test_a_missing_ledger_half_is_rewritten_on_the_next_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mint is level-triggered on the pair, not on the corpus row: an
    arrival event whose `event.yaml` is gone (a pass interrupted between the
    two writes) heals on the next cycle rather than staying half-minted
    forever."""
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-v2")
    db = _arrival_case(tmp_path)
    _arrival_pass(db, tmp_path)
    ledger = _arrival_ledger_file(tmp_path)
    ledger.unlink()
    events = _arrival_pass(db, tmp_path)
    assert _ARRIVAL_EVENT_ID in events
    assert ledger.is_file()


def test_a_complete_arrival_pair_is_left_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Idempotence: with both halves present the pass skips the case entirely,
    so a committed definition is never rewritten under a later run."""
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-v2")
    db = _arrival_case(tmp_path)
    _arrival_pass(db, tmp_path)
    ledger = _arrival_ledger_file(tmp_path)
    ledger.write_text("sentinel: the committed definition\n")
    _arrival_pass(db, tmp_path)
    assert ledger.read_text() == "sentinel: the committed definition\n"


def test_every_owed_arrival_in_one_scan_gets_both_halves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The pass buffers its mints and writes after the scan, because the scan
    streams an open cursor over `cases` while the mint seam commits. With more
    than one case owed, a pass that wrote mid-scan would be reading through its
    own writes — so mint every one of them and check all the pairs."""
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-v2")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    case_ids = ["scotus/26000002", "scotus/26000003", "scotus/26000004"]
    with corpus.connect(db) as conn:
        for n, case_id in enumerate(case_ids, start=2):
            row = _petition(
                case_id,
                distribution_count=None,
                conference=None,
                docket=f"26-{n}",
                petitioner_title="United States",  # the federal carve-in, so every one is picked
            ).model_copy(update={"date_filed": date(2026, 7, 20)})
            corpus.upsert_rows(conn, [row])
            corpus.upsert_events(
                conn,
                [
                    corpus.CorpusEvent(
                        event_id="evt-petition-disposition",
                        case_id=case_id,
                        court="scotus",
                        kind=EventKind.petition,
                        stage=Stage.cert,
                    )
                ],
            )
        apply_salience_selection(
            conn, _data_root(tmp_path), SalienceConfig(per_conference_capacity=2, floor=0.28)
        )
        minted = {
            case_id
            for case_id in case_ids
            if _ARRIVAL_EVENT_ID in {e.event_id for e in corpus.events_for_case(conn, case_id)}
        }
    assert minted == set(case_ids)
    for case_id in case_ids:
        court, _, docket = case_id.partition("/")
        ledger = (
            CasePaths(_data_root(tmp_path), court, int(docket)).event(_ARRIVAL_EVENT_ID).event_file
        )
        assert ledger.is_file(), f"{case_id} minted its corpus row without its ledger half"


def test_a_resolved_arrival_event_heals_its_ledger_without_reopening(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Writing the missing half can never undo a resolution: the write path's
    `resolved` latch holds, so a closed arrival event gains its definition
    carrying `resolved: true` rather than being minted open again."""
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-v2")
    db = _arrival_case(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=_ARRIVAL_EVENT_ID,
                    case_id=_ARRIVAL_CASE_ID,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                    resolved=True,
                )
            ],
        )
    _arrival_pass(db, tmp_path)
    with corpus.connect(db) as conn:
        stored = {e.event_id: e for e in corpus.events_for_case(conn, _ARRIVAL_CASE_ID)}
    assert stored[_ARRIVAL_EVENT_ID].resolved is True
    defined = yaml.safe_load(_arrival_ledger_file(tmp_path).read_text())
    assert defined["resolved"] is True


# --- the versioned distribution parse ---------------------------------------------


@pytest.mark.parametrize("version", registered_versions())
def test_every_registered_scorer_pins_a_registered_distribution_parse(version: str) -> None:
    """A version's parse is part of what its band labels mean, so it must resolve.

    Every scorer registered today pins ``dist-v1`` — the reading the corpus's
    own ``distribution_count`` column holds — so the band a cell freezes and the
    band the live gate ranked it by are derived from one count.
    """
    assert SCORERS[version].distribution_parse in DISTRIBUTION_PARSES
    assert SCORERS[version].distribution_parse == "dist-v1"


def _census_row(case_id: str, docket: str) -> corpus.CorpusRow:
    """A live-slice, paid, modern-cert petition whose caption bands ``private``."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        case_name="John Doe v. Roe",
        last_live_polled=date(2026, 8, 1),
    )


def _census_payload(*texts: str) -> dict[str, object]:
    """A **live-shaped** snapshot — the only channel the census counts."""
    return {"ProceedingsandOrder": [{"Text": text, "Date": "08/01/2026"} for text in texts]}


def _rest_payload(*descriptions: str) -> dict[str, object]:
    """A REST-shaped snapshot, which the census must skip past rather than count."""
    return {"docket_entries": [{"description": text} for text in descriptions]}


def test_the_distribution_census_counts_both_parses_over_one_frame(tmp_path: Path) -> None:
    """One frame, two readings, banded by one scorer — so the delta is the parse.

    The frame is the gate's scored segment with pending rows kept, because the
    count is a banding input the gate reads before a petition resolves. A case
    whose only extra distribution belongs to an ancillary motion loses that
    count under ``dist-v2`` and falls a band with it; a case distributed only
    for itself moves neither.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _census_row("scotus/1", "24-100"),  # band moves: one count is a motion's
                _census_row("scotus/2", "24-101"),  # unmoved: distributed only for itself
                _census_row("scotus/3", "24-102"),  # unobservable: no snapshot stored
                corpus.CorpusRow(  # IFP: outside the scored segment
                    case_id="scotus/4",
                    court="scotus",
                    docket_number="24-5001",
                    case_name="John Doe v. Roe",
                    last_live_polled=date(2026, 8, 1),
                ),
            ],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload(
                "DISTRIBUTED for Conference of 3/24/2023.",
                "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
            ),
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/2",
            date(2026, 8, 1),
            _census_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )
        census = distribution_census(conn, candidate_parse="dist-v2")
    assert (census.baseline_parse, census.candidate_parse) == ("dist-v1", "dist-v2")
    assert census.salience_version == SALIENCE_VERSION
    # Two cases carry a readable proceedings list; the third is unobservable
    # rather than agreeing, and the IFP row never enters the frame at all.
    assert (census.cases, census.unobservable) == (2, 1)
    assert (census.count_changed, census.band_changed) == (1, 1)
    assert census.count_changed_case_ids == ["scotus/1"]
    assert census.band_changed_case_ids == ["scotus/1"]
    # One relist under dist-v1 (two conferences), none under dist-v2. The matrix
    # is the whole square, so the two occupied cells sit among zeros rather than
    # alone: a reader can tell "measured, none" from "cell never emitted".
    vocabulary = SCORERS[census.salience_version].bands
    assert [(t.from_band, t.to_band) for t in census.transitions] == [
        (from_band, to_band) for from_band in vocabulary for to_band in vocabulary
    ]
    assert [(t.from_band, t.to_band, t.n) for t in census.transitions if t.n] == [
        ("elevated", "baseline", 1),
        ("baseline", "baseline", 1),
    ]
    # Maturity and the unobservable denominator ride per Term, not just in the
    # totals: both observable rows are undecided, the snapshot-less row is the
    # Term's own unobservable rather than a repo-wide footnote, and it is pending
    # too — so the frame's pending count exceeds the observable one.
    assert [
        (t.term, t.cases, t.pending, t.frame_pending, t.unobservable, t.count_changed)
        for t in census.terms
    ] == [(2024, 2, 2, 3, 1, 1)]
    assert [
        (t.band_changed, t.pending_count_changed, t.pending_band_changed) for t in census.terms
    ] == [(1, 1, 1)]
    # The frame's pending count is the unobservable row's too; the direction
    # split says the one moved count fell, which is what makes the square's empty
    # band-strengthening half an observation rather than an assertion.
    assert (census.frame_pending, census.count_increased, census.count_decreased) == (3, 0, 1)
    # The top-level observable pending is the per-Term tallies' own sum.
    assert census.pending == sum(t.pending for t in census.terms)
    # The per-band cut: the moving case is banded `elevated` by the incumbent
    # parse, so that is the band a reader sees the movement under, and every band
    # of the version is emitted whether or not the frame reached it.
    assert [b.band for b in census.bands] == list(vocabulary)
    assert [
        (b.band, b.cases, b.pending, b.count_changed, b.band_changed)
        for b in census.bands
        if b.cases
    ] == [("elevated", 1, 1, 1, 1), ("baseline", 1, 1, 0, 0)]


def test_the_distribution_census_is_a_no_op_when_both_parses_agree(tmp_path: Path) -> None:
    """Asked for one parse twice, the census reports a frame and no movement.

    The property that makes the artifact readable: a nonzero ``count_changed``
    is always the readings differing, never the census's own bookkeeping.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_census_row("scotus/1", "24-100")])
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload(
                "DISTRIBUTED for Conference of 3/24/2023.",
                "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
            ),
        )
        census = distribution_census(conn, candidate_parse="dist-v1")
    assert census.cases == 1
    assert (census.count_changed, census.band_changed) == (0, 0)
    assert census.count_changed_case_ids == []
    # The square is emitted whole, so the single unmoved case sits on its own
    # diagonal cell and every other cell reads as a measured zero.
    assert [(t.from_band, t.to_band, t.n) for t in census.transitions if t.n] == [
        ("elevated", "elevated", 1)
    ]
    assert len(census.transitions) == len(SCORERS[census.salience_version].bands) ** 2


def test_the_distribution_census_refuses_an_unregistered_parse_or_version(tmp_path: Path) -> None:
    """Both labels resolve up front, so an empty frame fails as loudly as a full one."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        with pytest.raises(KeyError):
            distribution_census(conn, candidate_parse="dist-v0")
        with pytest.raises(KeyError):
            distribution_census(conn, baseline_parse="dist-v0", candidate_parse="dist-v2")
        with pytest.raises(KeyError):
            distribution_census(conn, candidate_parse="dist-v2", version="sal-v0")


def test_the_distribution_census_counts_the_live_channel_only(tmp_path: Path) -> None:
    """A newer REST snapshot must not become the thing the parses are compared on.

    The two channels docket the same facts in different prose and the
    entry-initial rule is a claim about the live channel's conventions, so
    counting REST text under it would report a channel artifact as a parse
    delta. A case whose only snapshot is REST-shaped is unobservable.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_census_row("scotus/1", "24-100")])
        # The live snapshot carries the ancillary entry; a LATER REST snapshot
        # does not. Reading the newest row of either shape would find no
        # disagreement at all and report the parses as identical.
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload(
                "DISTRIBUTED for Conference of 3/24/2023.",
                "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
            ),
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 2),
            _rest_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )
        census = distribution_census(conn, candidate_parse="dist-v2")
    assert (census.cases, census.unobservable) == (1, 0)
    assert census.count_changed_case_ids == ["scotus/1"]

    db2 = tmp_path / "rest-only.db"
    with corpus.connect(db2) as conn:
        corpus.upsert_rows(conn, [_census_row("scotus/1", "24-100")])
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _rest_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )
        rest_only = distribution_census(conn, candidate_parse="dist-v2")
    assert (rest_only.cases, rest_only.unobservable) == (0, 1)


def test_the_distribution_census_refuses_a_subsampled_frame(tmp_path: Path) -> None:
    """Every figure is a raw count, so a weighted row would silently stand for ten."""
    db = tmp_path / "corpus.db"
    row = _census_row("scotus/1", "24-100").model_copy(update={"sample_weight": 10})
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )
        with pytest.raises(ValueError, match="sample_weight"):
            distribution_census(conn, candidate_parse="dist-v2")


def test_the_distribution_census_per_band_cut_adds_up_to_the_totals(tmp_path: Path) -> None:
    """The per-band cut is a partition of the observable frame, keyed on the incumbent band.

    Every band of the version is emitted whether the frame reached it or not, so
    an empty band reads as measured-empty; and the per-band counters sum to the
    census totals, which is what makes "which band would move" answerable from
    the artifact rather than only by joining the changed ids back to the corpus.
    """
    db = tmp_path / "corpus.db"
    ancillary = "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026."
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [_census_row(f"scotus/{n}", f"24-10{n}") for n in (1, 2, 3)],
        )
        # Two relists under dist-v1 and one under dist-v2: `high` -> `elevated`.
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload(
                "DISTRIBUTED for Conference of 3/24/2023.",
                "DISTRIBUTED for Conference of 4/14/2023.",
                ancillary,
            ),
        )
        # One relist under dist-v1 and none under dist-v2: `elevated` -> `baseline`.
        corpus.upsert_snapshot(
            conn,
            "scotus/2",
            date(2026, 8, 1),
            _census_payload("DISTRIBUTED for Conference of 3/24/2023.", ancillary),
        )
        # Unmoved, and the band the other two land in.
        corpus.upsert_snapshot(
            conn,
            "scotus/3",
            date(2026, 8, 1),
            _census_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )
        census = distribution_census(conn, candidate_parse="dist-v2")
    assert [b.band for b in census.bands] == list(SCORERS[census.salience_version].bands)
    assert sum(b.cases for b in census.bands) == census.cases == 3
    # The per-band pending is the OBSERVABLE one, so it matches the per-Term
    # observable count and sits at or under the frame's — never chained to it.
    assert sum(b.pending for b in census.bands) == sum(t.pending for t in census.terms) == 3
    assert sum(b.pending for b in census.bands) <= census.frame_pending
    assert sum(b.count_changed for b in census.bands) == census.count_changed == 2
    assert sum(b.band_changed for b in census.bands) == census.band_changed == 2
    # Keyed on the BASELINE band: both movers are counted under the band the
    # baseline parse implies, not under the one they would move to.
    assert [(b.band, b.cases, b.count_changed) for b in census.bands if b.cases] == [
        ("high", 1, 1),
        ("elevated", 1, 1),
        ("baseline", 1, 0),
    ]


def test_the_distribution_census_square_separates_a_zero_from_an_unreachable_cell(
    tmp_path: Path,
) -> None:
    """The matrix is the whole square, so an unoccupied cell is a measured zero.

    A subset candidate can only lower the count and every band function is
    monotone in it, so no case can move to a stronger band — the census reports
    that as zero-filled cells plus ``count_increased == 0``, an observation,
    rather than by omitting the cells and leaving a reader to infer it.
    """
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_census_row("scotus/1", "24-100")])
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload(
                "DISTRIBUTED for Conference of 3/24/2023.",
                "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
            ),
        )
        census = distribution_census(conn, candidate_parse="dist-v2")
    vocabulary = SCORERS[census.salience_version].bands
    cells = {(t.from_band, t.to_band): t.n for t in census.transitions}
    assert len(census.transitions) == len(cells) == len(vocabulary) ** 2
    assert cells[("elevated", "baseline")] == 1
    # The band-strengthening cells are present and zero rather than absent.
    assert cells[("baseline", "elevated")] == 0
    assert (census.count_increased, census.count_decreased) == (0, 1)
    assert census.count_increased + census.count_decreased == census.count_changed


def test_the_distribution_census_counts_pending_over_the_whole_frame(tmp_path: Path) -> None:
    """Two pending denominators, because they are two populations.

    The per-Term ``pending`` rides the observable rows; the frame holds the
    unreadable ones too. Maturity is a property of the docket and readability a
    property of the pull, so publishing one number would leave a reader to guess
    which denominator it sat over.
    """
    db = tmp_path / "corpus.db"
    resolved = _census_row("scotus/1", "24-100").model_copy(
        update={"disposition": Disposition.denied}
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [resolved, _census_row("scotus/2", "24-101")])
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )  # scotus/2 is pending and stores no snapshot: unobservable, and pending
        census = distribution_census(conn, candidate_parse="dist-v2")
    assert (census.cases, census.unobservable) == (1, 1)
    assert census.frame_pending == 1
    assert [(t.cases, t.pending, t.frame_pending, t.unobservable) for t in census.terms] == [
        (1, 0, 1, 1)
    ]
    # The relation the two counters exist to make visible, over every Term.
    assert all(t.frame_pending >= t.pending for t in census.terms)
    assert census.frame_pending >= sum(t.pending for t in census.terms)


def test_the_distribution_census_banner_states_its_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``cases`` is printed against the frame it is a share of, not on its own.

    A census that could read a tenth of its frame and one that read all of it
    otherwise announce themselves identically, and the difference is exactly
    what a reviewer weighing the artifact needs first.
    """
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn, [_census_row("scotus/1", "24-100"), _census_row("scotus/2", "24-101")]
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload(
                "DISTRIBUTED for Conference of 3/24/2023.",
                "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
            ),
        )  # scotus/2 stores no snapshot, so half the frame is unreadable
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = CliRunner().invoke(app, ["distribution-census", "--candidate-parse", "dist-v2"])
    assert result.exit_code == 0, result.output
    assert "cases=1 (50.0% of the 2-row frame)" in result.stderr
    assert "pending=2 of the frame" in result.stderr
    assert "and 1 of the 1 observable" in result.stderr
    # The occupied cells as a count, never as a share of the square: how many
    # cells a parse pair can reach is a property of the pair, so a density would
    # read as sparsity where the unreached cells are an identity.
    assert "elevated -> baseline: 1" in result.stderr
    bands = len(SCORERS[SALIENCE_VERSION].bands)
    assert (
        f"occupied off-diagonal transition cells: 1 (the square carries all {bands**2} zero-filled"
        in result.stderr
    )
    assert "count moved up in 0 case(s), down in 1" in result.stderr


def test_every_registered_band_function_is_monotone_in_the_distribution_count() -> None:
    """The premise the census's empty transition half rests on, pinned over the registry.

    A subset candidate parse can only lower the count, so "no case moves to a
    stronger band" holds only while every registered band function is monotone
    in the count. ``count_increased`` observes the nesting on a frame; nothing
    else observes this, and the headroom is thin — the never-parsed sentinel
    scores above relist-0, and only the band cutpoints keep that from crossing a
    boundary. A version that read the count non-monotonically would falsify the
    census's own docstring while every other test stayed green.
    """
    for version in registered_versions():
        entry = SCORERS[version]
        rank = {band: index for index, band in enumerate(entry.bands)}
        for cvsg in (None, date(2026, 3, 1)):
            for court in ("ca9", "cadc", None):
                for name in ("John Doe v. Roe", "United States v. Roe", "California v. Roe"):
                    row = corpus.CorpusRow(
                        case_id="scotus/1",
                        court="scotus",
                        docket_number="24-100",
                        case_name=name,
                        originating_court=court,
                        cvsg_date=cvsg,
                    )
                    banded = [
                        entry.band(row.model_copy(update={"distribution_count": n}))
                        for n in (None, 0, 1, 2, 3, 4, 5)
                    ]
                    ranks = [rank[band] for band in banded]
                    # Strongest band first in the vocabulary, so a rising count
                    # must never raise the rank index (never weaken the band).
                    assert ranks == sorted(ranks, reverse=True), (version, name, banded)


def test_the_census_refuses_a_band_outside_the_versions_declared_vocabulary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The per-band cut and the square are emitted from the declared bands.

    A band function returning a label outside that tuple would drop cases out of
    both while the totals still counted them — an artifact that silently does
    not add up, which is worse than a failed run.
    """
    stray = SalienceScorer(
        version="sal-test",
        score=SCORERS[SALIENCE_VERSION].score,
        band=lambda row: "invented",
        bands=SCORERS[SALIENCE_VERSION].bands,
        carve_out=SCORERS[SALIENCE_VERSION].carve_out,
    )
    # The registry is a read-only mapping by design, so the stand-in is one too.
    monkeypatch.setattr(
        salience_module, "SCORERS", MappingProxyType({**SCORERS, "sal-test": stray})
    )
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_census_row("scotus/1", "24-100")])
        corpus.upsert_snapshot(
            conn,
            "scotus/1",
            date(2026, 8, 1),
            _census_payload("DISTRIBUTED for Conference of 3/24/2023."),
        )
        with pytest.raises(ValueError, match="outside sal-test's declared bands"):
            distribution_census(conn, candidate_parse="dist-v2", version="sal-test")


def test_the_active_scorers_parse_is_the_one_the_corpus_column_holds() -> None:
    """The alignment the relist-increment claim's monotonicity rests on.

    The claim reads its prediction-time count from the frozen context (the
    active scorer's parse) and its resolution-time count from the corpus column
    (written at the default). "The count never falls" holds across that pair
    only while the two labels agree.
    """
    assert SCORERS[SALIENCE_VERSION].distribution_parse == DEFAULT_DISTRIBUTION_PARSE


def test_a_cells_frozen_count_follows_the_active_scorers_parse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Registering a dist-v2 scorer moves what a provisioned cell freezes.

    Without this the parse hand-off in `cell_context` is delete-safe — every
    registered version pins the default today, so nothing else would notice.
    """
    narrow = SalienceScorer(
        version="sal-test",
        score=SCORERS[SALIENCE_VERSION].score,
        band=SCORERS[SALIENCE_VERSION].band,
        bands=SCORERS[SALIENCE_VERSION].bands,
        carve_out=SCORERS[SALIENCE_VERSION].carve_out,
        distribution_parse="dist-v2",
    )
    payload = {
        "CaseNumber": "24-100",
        "PetitionerTitle": "John Doe",
        "ProceedingsandOrder": [
            {"Text": "DISTRIBUTED for Conference of 3/24/2023.", "Date": "03/10/2023"},
            {
                "Text": "Motion (25M82) DISTRIBUTED for Conference of 5/19/2026.",
                "Date": "05/01/2026",
            },
        ],
    }
    built = cell_context.build("scotus/1", date(2026, 8, 1), payload, "forward")
    assert built.distribution_count == 2  # dist-v1: the motion's trip counts

    monkeypatch.setattr(salience_module, "SCORERS", {**SCORERS, "sal-test": narrow})
    monkeypatch.setattr(salience_module, "SALIENCE_VERSION", "sal-test")
    narrowed = cell_context.build("scotus/1", date(2026, 8, 1), payload, "forward")
    assert narrowed.distribution_count == 1
