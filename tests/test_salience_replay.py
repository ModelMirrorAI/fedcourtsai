"""Salience-gate replay: the as-of projection layer and the per-Term gate replay."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus
from fedcourtsai.cli import app
from fedcourtsai.config import SalienceConfig
from fedcourtsai.pipeline import asof
from fedcourtsai.pipeline.asof import CutoffPolicy, replay_cutoff
from fedcourtsai.pipeline.salience import (
    SALIENCE_VERSION,
    SalienceScorer,
    registered_versions,
)
from fedcourtsai.salience_replay import replay_gate, select_replay_population
from fedcourtsai.schemas import Disposition, SalienceReplay
from fedcourtsai.serialize import read_model

runner = CliRunner()


def _live(*entries: tuple[str, str]) -> dict[str, Any]:
    return {
        "CaseNumber": "23-100",
        "ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries],
    }


# --- project_row: the honest synthesis -------------------------------------------


def _decided_row() -> corpus.CorpusRow:
    """A row carrying every field family: identity, latched signals, outcome, latches."""
    return corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        docket_number="23-100",
        case_name="Doe v. Roe",
        date_filed=date(2024, 1, 5),
        originating_court="ca9",
        originating_court_name="Ninth Circuit",
        originating_docket_number="22-15044",
        sample_weight=5,
        disposition=Disposition.granted,
        date_decided=date(2024, 6, 30),
        date_cert_granted=date(2024, 3, 4),
        distribution_count=3,
        cvsg_date=date(2024, 2, 1),
        distributed_for_conference=date(2024, 3, 1),
        salience_score=0.4,
        salience_version="sal-v1",
        salience_selected=True,
        predict_queued_at=date(2024, 2, 20),
        evaluate_queued_at=date(2024, 3, 10),
        last_live_polled=date(2024, 6, 30),
    )


def test_projection_nulls_every_outcome_and_latch_field() -> None:
    payload = _live(("Jan 5 2024", "Petition for a writ of certiorari filed."))
    projected = asof.project_row(
        _decided_row(), payload, cutoff=date(2024, 1, 6), provenance="truncated"
    )
    row = projected.row
    assert row.disposition is None
    assert row.date_decided is None
    assert row.date_cert_granted is None and row.date_cert_denied is None
    assert row.salience_score is None and row.salience_version is None
    assert row.salience_selected is False
    assert row.predict_queued_at is None and row.evaluate_queued_at is None
    assert row.predict_excluded is False
    assert row.distributed_for_conference is None  # the caller derives the as-of value


def test_projection_copies_the_invariants_and_rederives_the_signals() -> None:
    payload = _live(
        ("Jan 5 2024", "Petition for a writ of certiorari filed."),
        ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
    )
    projected = asof.project_row(
        _decided_row(), payload, cutoff=date(2024, 2, 3), provenance="truncated"
    )
    row = projected.row
    # Time-invariant identity, copied from the current row.
    assert row.case_id == "scotus/1" and row.docket_number == "23-100"
    assert row.case_name == "Doe v. Roe" and row.date_filed == date(2024, 1, 5)
    assert row.originating_court == "ca9" and row.sample_weight == 5
    # Docket-acquired signals, re-derived from the payload — not the latched 3 / CVSG.
    assert projected.observable is True
    assert row.distribution_count == 1
    assert row.cvsg_date is None


def test_projection_without_proceedings_is_unobservable_not_zero() -> None:
    projected = asof.project_row(
        _decided_row(), {"CaseNumber": "23-100"}, cutoff=None, provenance="blind"
    )
    assert projected.observable is False
    assert projected.row.distribution_count is None  # unknown, never asserted as 0
    # The interim trio goes null with it: one observability flag, both signal
    # families, because both come off the same proceedings list.
    assert projected.row.response_requested is None
    assert projected.row.referred_to_court is None
    assert projected.row.amicus_briefs is None


def _application_row() -> corpus.CorpusRow:
    """An application row carrying the latched *ending* escalation state."""
    return corpus.CorpusRow(
        case_id="scotus/2",
        court="scotus",
        docket_number="26A11",
        application_kind="substantive",
        response_requested=True,
        referred_to_court=True,
        amicus_briefs=4,
        disposition=Disposition.granted,
    )


def test_projection_rederives_the_interim_signals_rather_than_reading_the_latches() -> None:
    """The interim trio is re-derived from the payload, like the cert pair.

    The latched columns hold the *ending* state — the trio is monotone, exactly
    as the distribution count is — so a cell conditioned on them would be
    conditioned on its own future. Here the payload discloses only the
    application's arrival, so the projection reports the arrival state and not
    the row's latched `True / True / 4`.
    """
    payload = {
        "CaseNumber": "26A11",
        "ProceedingsandOrder": [
            {
                "Date": "Jan 5 2026",
                "Text": "Application (26A11) for a stay, submitted to The Chief Justice.",
            },
        ],
    }
    projected = asof.project_row(
        _application_row(), payload, cutoff=date(2026, 1, 6), provenance="truncated"
    )
    assert projected.observable is True
    assert projected.row.response_requested is False
    assert projected.row.referred_to_court is False
    assert projected.row.amicus_briefs == 0


def test_projection_reads_the_interim_signals_the_payload_does_disclose() -> None:
    payload = {
        "CaseNumber": "26A11",
        "ProceedingsandOrder": [
            {
                "Date": "Jan 5 2026",
                "Text": "Application (26A11) for a stay, submitted to The Chief Justice.",
            },
            {
                "Date": "Jan 8 2026",
                "Text": "Response to application (26A11) requested by The Chief Justice.",
            },
            {"Date": "Jan 9 2026", "Text": "Brief amicus curiae of the State of X filed."},
        ],
    }
    projected = asof.project_row(
        _application_row(), payload, cutoff=date(2026, 1, 10), provenance="truncated"
    )
    assert projected.row.response_requested is True
    assert projected.row.referred_to_court is False  # no referral entry yet
    assert projected.row.amicus_briefs == 1


# --- asof_conference: the latest-entry-wins rule, as-of ---------------------------


_TWO_DISTRIBUTIONS = _live(
    ("Jan 5 2024", "Petition for a writ of certiorari filed."),
    ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
    ("Feb 20 2024", "DISTRIBUTED for Conference of February 23, 2024."),
)


def test_asof_conference_latest_pre_cutoff_entry_wins() -> None:
    assert asof.asof_conference(_TWO_DISTRIBUTIONS, date(2024, 2, 10)) == date(2024, 2, 16)
    assert asof.asof_conference(_TWO_DISTRIBUTIONS, date(2024, 2, 21)) == date(2024, 2, 23)


def test_asof_conference_is_strict_at_the_cutoff() -> None:
    # An entry dated ON the cutoff is not yet observable — strictly-before only.
    assert asof.asof_conference(_TWO_DISTRIBUTIONS, date(2024, 2, 20)) == date(2024, 2, 16)


def test_asof_conference_equals_the_live_value_past_every_entry() -> None:
    # With the cutoff beyond the whole docket this is the live channel's
    # latest-entry-wins `distributed_for_conference`.
    assert asof.asof_conference(_TWO_DISTRIBUTIONS, date(2030, 1, 1)) == date(2024, 2, 23)


def test_asof_conference_unparseable_or_absent_is_none() -> None:
    unparseable = _live(("Feb 2 2024", "DISTRIBUTED for Conference of whenever suits."))
    assert asof.asof_conference(unparseable, date(2030, 1, 1)) is None
    assert asof.asof_conference(_live(("Jan 5 2024", "Petition filed.")), date(2030, 1, 1)) is None
    assert asof.asof_conference({}, date(2030, 1, 1)) is None


def test_asof_conference_skips_an_undated_entry() -> None:
    payload = _live(("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."))
    payload["ProceedingsandOrder"].append(
        {"Text": "DISTRIBUTED for Conference of March 1, 2024."}  # no date: fail closed
    )
    assert asof.asof_conference(payload, date(2030, 1, 1)) == date(2024, 2, 16)


# --- policy cutoffs ---------------------------------------------------------------


_TRAJECTORY = _live(
    ("Jan 5 2024", "Petition for a writ of certiorari filed."),
    ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
    ("Feb 20 2024", "DISTRIBUTED for Conference of February 23, 2024."),
    ("Feb 26 2024", "Petition GRANTED."),
)


def _row(**overrides: Any) -> corpus.CorpusRow:
    base: dict[str, Any] = {"case_id": "scotus/1", "court": "scotus", "docket_number": "23-100"}
    return corpus.CorpusRow(**(base | overrides))


def test_arrival_is_the_day_after_the_earliest_dated_entry() -> None:
    cutoff = asof.policy_cutoff(CutoffPolicy.arrival, _row(), _TRAJECTORY)
    assert cutoff == date(2024, 1, 6)


def test_arrival_falls_back_to_the_filing_date() -> None:
    row = _row(date_filed=date(2024, 1, 5))
    assert asof.policy_cutoff(CutoffPolicy.arrival, row, {}) == date(2024, 1, 6)
    assert asof.policy_cutoff(CutoffPolicy.arrival, _row(), {}) is None


def test_distribution_1_is_the_day_after_the_first_distributed_entry() -> None:
    cutoff = asof.policy_cutoff(CutoffPolicy.distribution_1, _row(), _TRAJECTORY)
    assert cutoff == date(2024, 2, 3)
    never = _live(("Jan 5 2024", "Petition filed."))
    assert asof.policy_cutoff(CutoffPolicy.distribution_1, _row(), never) is None


def test_resolution_delegates_to_the_cert_backtest_cutoff() -> None:
    row = _row(date_cert_granted=date(2024, 2, 26))
    cutoff = asof.policy_cutoff(CutoffPolicy.resolution, row, _TRAJECTORY)
    assert cutoff == replay_cutoff(_TRAJECTORY, date(2024, 2, 26)) == date(2024, 2, 21)
    assert asof.policy_cutoff(CutoffPolicy.resolution, _row(), _TRAJECTORY) is None  # unresolved


# --- the end-to-end gate replay ---------------------------------------------------


def _petition(
    case_id: str,
    docket: str,
    *,
    disposition: Disposition,
    entries: tuple[tuple[str, str], ...],
    resolved: date,
    weight: int = 1,
) -> tuple[corpus.CorpusRow, dict[str, Any]]:
    """A resolved live-slice OT2023 petition and its live-shaped snapshot."""
    row = corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        date_filed=date(2024, 1, 5),
        disposition=disposition,
        date_cert_granted=resolved if disposition == Disposition.granted else None,
        date_cert_denied=resolved if disposition == Disposition.denied else None,
        last_live_polled=date(2024, 7, 1),
        sample_weight=weight,
    )
    payload = {
        "CaseNumber": docket,
        "ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries],
    }
    return row, payload


def _seed_replay_corpus(corpus_root: Path) -> Path:
    """Four OT2023 resolved petitions plus one snapshotless row.

    - scotus/1: granted after three distributions (2 relists -> high band, a
      floor carve-out at resolution).
    - scotus/2: denied after one distribution, sample_weight 10 (the weighted
      denial the precision arithmetic turns on).
    - scotus/3: granted after one distribution (a grant the gate misses at
      capacity 1 -> recall below 1).
    - scotus/4: denied with no distribution at all (no resolution cutoff ->
      blind, unobservable).
    - scotus/5: no snapshot held -> skipped_no_snapshot.
    """
    db = corpus.corpus_db_path(corpus_root)
    filed = ("Jan 5 2024", "Petition for a writ of certiorari filed.")
    cases = [
        _petition(
            "scotus/1",
            "23-100",
            disposition=Disposition.granted,
            resolved=date(2024, 3, 4),
            entries=(
                filed,
                ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
                ("Feb 20 2024", "DISTRIBUTED for Conference of February 23, 2024."),
                ("Feb 26 2024", "DISTRIBUTED for Conference of March 1, 2024."),
                ("Mar 4 2024", "Petition GRANTED."),
            ),
        ),
        _petition(
            "scotus/2",
            "23-200",
            disposition=Disposition.denied,
            resolved=date(2024, 2, 20),
            weight=10,
            entries=(
                filed,
                ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
                ("Feb 20 2024", "Petition DENIED."),
            ),
        ),
        _petition(
            "scotus/3",
            "23-300",
            disposition=Disposition.granted,
            resolved=date(2024, 2, 20),
            entries=(
                filed,
                ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
                ("Feb 20 2024", "Petition GRANTED."),
            ),
        ),
        _petition(
            "scotus/4",
            "23-400",
            disposition=Disposition.denied,
            resolved=date(2024, 2, 1),
            entries=(filed, ("Feb 1 2024", "Petition DENIED.")),
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row for row, _ in cases])
        for row, payload in cases:
            corpus.upsert_snapshot(conn, row.case_id, date(2024, 7, 1), payload)
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/5",
                    court="scotus",
                    docket_number="23-500",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2024, 2, 20),
                    last_live_polled=date(2024, 7, 1),
                )
            ],
        )
    return db


_CONFIG = SalienceConfig(per_conference_capacity=1, floor=0.28)


def test_population_is_the_terms_paid_live_slice(tmp_path: Path) -> None:
    db = _seed_replay_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # IFP (serial >= 5001): fee class is fixed at filing, so the
                # Tier-0 exclusion applies time-invariantly.
                corpus.CorpusRow(
                    case_id="scotus/9",
                    court="scotus",
                    docket_number="23-6001",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2024, 2, 20),
                    last_live_polled=date(2024, 7, 1),
                ),
                # Off the named Terms.
                corpus.CorpusRow(
                    case_id="scotus/10",
                    court="scotus",
                    docket_number="21-100",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2022, 2, 20),
                    last_live_polled=date(2024, 7, 1),
                ),
                # Not live-slice: no parsed proceedings to reconstruct from.
                corpus.CorpusRow(
                    case_id="scotus/11",
                    court="scotus",
                    docket_number="23-700",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2024, 2, 20),
                ),
            ],
        )
        ids = {row.case_id for row in select_replay_population(conn, terms=[2023])}
    assert ids == {"scotus/1", "scotus/2", "scotus/3", "scotus/4", "scotus/5"}


def test_arrival_replay_is_degenerate_zero_selected_all_baseline(tmp_path: Path) -> None:
    """Issue-motivating fact, quantified: at arrival nothing separates petitions."""
    db = _seed_replay_corpus(tmp_path / "corpus")
    report = replay_gate(db, terms=[2023], policies=[CutoffPolicy.arrival], config=_CONFIG)
    cell = next(c for c in report.cells if c.salience_version == SALIENCE_VERSION)
    assert (cell.term, cell.policy) == (2023, "arrival")
    assert cell.eligible == 5 and cell.skipped_no_snapshot == 1
    assert cell.cohorts == 0 and cell.selected == 0
    assert cell.bands == {"baseline": 4}  # every projected docket reads relist-0
    assert cell.provenance == {"truncated": 4}
    assert cell.largest_weighted_cohort == 0.0  # no cohort formed at all
    assert cell.precision is None  # an empty selection has no rate, not a zero one
    assert cell.recall == 0.0  # but it does cover none of the Term's grants


def test_distribution_1_replay_cohorts_on_the_first_conference(tmp_path: Path) -> None:
    db = _seed_replay_corpus(tmp_path / "corpus")
    report = replay_gate(db, terms=[2023], policies=[CutoffPolicy.distribution_1], config=_CONFIG)
    cell = next(c for c in report.cells if c.salience_version == SALIENCE_VERSION)
    # scotus/1..3 all sit at their FIRST distribution (one conference, Feb 16),
    # every one relist-0/baseline; scotus/4 never distributed -> blind.
    assert cell.cohorts == 1
    assert cell.bands == {"baseline": 3, "unobservable": 1}
    # scotus/4's blind is a faithful gate miss (never distributed), and the
    # mix says so rather than pooling it with an untrusted reconstruction.
    assert cell.provenance == {"truncated": 3, "blind-no-moment": 1}
    # All baseline, so no carve-out; capacity 1 fills by case_id tie-break.
    assert (cell.selected, cell.selected_carve_out, cell.selected_rank_fill) == (1, 0, 1)
    assert cell.capacity_bound_cohorts == 1
    assert cell.largest_weighted_cohort == 12.0  # 1 + 10 + 1, all non-carve-out


def test_the_report_spans_term_by_policy_by_registered_version(tmp_path: Path) -> None:
    """Cells are (Term x policy x version), and every cell names its own scorer.

    The version axis is what makes a candidate scorer comparable to the
    incumbent: both score the same reconstructed dockets in one run, so any
    difference between their cells is the scoring function and nothing else."""
    db = _seed_replay_corpus(tmp_path / "corpus")
    policies = [CutoffPolicy.arrival, CutoffPolicy.resolution]
    report = replay_gate(db, terms=[2023], policies=policies, config=_CONFIG)

    versions = registered_versions()
    assert report.salience_versions == list(versions)
    assert report.salience_version == SALIENCE_VERSION  # the ACTIVE one
    assert report.cells_evaluated == len(policies) * len(versions)
    assert {cell.salience_version for cell in report.cells} == set(versions)
    for cell in report.cells:
        assert cell.salience_version, "every cell names the scorer that produced it"

    # Every version sees the same reconstruction, so the projection-derived
    # counts are identical across versions of one (Term, policy) — only the
    # scoring-derived ones may differ.
    for policy in policies:
        same_moment = [cell for cell in report.cells if cell.policy == str(policy)]
        assert len({c.eligible for c in same_moment}) == 1
        assert len({c.skipped_no_snapshot for c in same_moment}) == 1
        assert len({tuple(sorted(c.provenance.items())) for c in same_moment}) == 1


def test_resolution_replay_selects_the_carveout_and_scores_weighted(tmp_path: Path) -> None:
    db = _seed_replay_corpus(tmp_path / "corpus")
    report = replay_gate(db, terms=[2023], policies=[CutoffPolicy.resolution], config=_CONFIG)
    assert report.salience_version == SALIENCE_VERSION
    cell = next(c for c in report.cells if c.salience_version == SALIENCE_VERSION)
    # scotus/1 shows 2 relists at its last pre-grant distribution -> high band,
    # above the floor -> carve-out. scotus/2 and scotus/3 tie at baseline in the
    # Feb 16 cohort; capacity 1 takes scotus/2 by case_id -> rank fill.
    assert cell.bands == {"high": 1, "baseline": 2, "unobservable": 1}
    assert cell.cohorts == 2  # Feb 16 (scotus/2, scotus/3) and Mar 1 (scotus/1)
    assert (cell.selected, cell.selected_carve_out, cell.selected_rank_fill) == (2, 1, 1)
    assert cell.capacity_bound_cohorts == 1  # only Feb 16's rank fill actually cut
    assert cell.largest_weighted_cohort == 11.0  # Feb 16's non-carve-out weighted mass
    # Weighted precision: the weight-10 denial dominates the selected slice's
    # denominator — (1) / (1 + 10) — while raw counts stay readable beside it.
    assert cell.selected_granted == 1 and cell.realized_granted == 2
    assert cell.weighted_selected == 11.0 and cell.weighted_selected_granted == 1.0
    assert cell.precision == pytest.approx(1 / 11)
    assert cell.recall == pytest.approx(1 / 2)  # scotus/3's grant is missed
    assert cell.weighted_population == 13.0  # 1 + 10 + 1 + 1


def test_an_untrusted_cutoff_degrades_to_blind(tmp_path: Path) -> None:
    """The fail-closed seam: a rehearing distribution after a denial puts the
    resolution cutoff past the disposing order, so the disposition survives
    truncation and the projection must go blind — labeled as a reconstruction
    failure, not a gate miss, because the petition really was cohortable."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row = corpus.CorpusRow(
        case_id="scotus/8",
        court="scotus",
        docket_number="23-800",
        date_filed=date(2024, 1, 5),
        disposition=Disposition.denied,
        # The cert dates were never stamped, so resolution falls back to the
        # docket's termination — after the post-denial rehearing distribution.
        date_decided=date(2024, 5, 30),
        last_live_polled=date(2024, 7, 1),
    )
    payload = {
        "CaseNumber": "23-800",
        "ProceedingsandOrder": [
            {"Date": "Jan 5 2024", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "Feb 2 2024", "Text": "DISTRIBUTED for Conference of February 16, 2024."},
            {"Date": "Mar 10 2024", "Text": "Petition DENIED."},
            {"Date": "May 2 2024", "Text": "DISTRIBUTED for Conference of May 15, 2024."},
        ],
    }
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        corpus.upsert_snapshot(conn, row.case_id, date(2024, 7, 1), payload)
    report = replay_gate(db, terms=[2023], policies=[CutoffPolicy.resolution], config=_CONFIG)
    cell = next(c for c in report.cells if c.salience_version == SALIENCE_VERSION)
    assert cell.provenance == {"blind-untrusted-cutoff": 1}
    assert cell.bands == {"unobservable": 1}  # no trajectory shown, never banded
    assert cell.selected == 0


def test_an_empty_term_still_yields_its_cells(tmp_path: Path) -> None:
    db = _seed_replay_corpus(tmp_path / "corpus")
    report = replay_gate(
        db, terms=[2019], policies=[CutoffPolicy.arrival, CutoffPolicy.resolution], config=_CONFIG
    )
    # 2 (term, policy) cells x every registered version — the cell grid is the
    # product, so registering a scorer widens it rather than replacing a cell.
    assert report.cells_evaluated == 2 * len(registered_versions())
    assert all(cell.eligible == 0 and cell.selected == 0 for cell in report.cells)


# --- point-in-time snapshot reads (casestore + split mode) ------------------------


def _store_with_snapshots() -> casestore.InMemoryObjectTransport:
    transport = casestore.InMemoryObjectTransport()
    casestore.write_snapshot(transport, "scotus/1", date(2024, 2, 1), {"v": "february"})
    casestore.write_snapshot(transport, "scotus/1", date(2024, 5, 1), {"v": "may"})
    return transport


def test_read_snapshot_at_returns_the_newest_strictly_before() -> None:
    transport = _store_with_snapshots()
    found = casestore.read_snapshot_at(transport, "scotus/1", before=date(2024, 3, 1))
    assert found == (date(2024, 2, 1), {"v": "february"})
    # Exclusive at the bound, matching the truncation cutoff it pairs with.
    found = casestore.read_snapshot_at(transport, "scotus/1", before=date(2024, 5, 1))
    assert found == (date(2024, 2, 1), {"v": "february"})
    assert casestore.read_snapshot_at(transport, "scotus/1", before=date(2024, 2, 1)) is None
    assert casestore.read_snapshot_at(transport, "scotus/2", before=date(2024, 3, 1)) is None


def test_split_mode_snapshot_at_is_served_from_the_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Under the corpus split every dated snapshot is an addressable store
    object, so a dated point-in-time read is served from the store."""
    casestore.set_active_transport(_store_with_snapshots())
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    with corpus.connect(tmp_path / "corpus.db") as conn:  # empty blob: nothing served from SQL
        found = corpus.snapshot_at(conn, "scotus/1", before=date(2024, 3, 1))
    assert found == (date(2024, 2, 1), {"v": "february"})


# --- CLI --------------------------------------------------------------------------


def test_cli_writes_a_valid_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_replay_corpus(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    out = tmp_path / "salience-replay.json"
    result = runner.invoke(app, ["salience-replay", "--terms", "2023", "--out", str(out)])
    assert result.exit_code == 0, result.output
    report = read_model(out, SalienceReplay)  # validates against the schema model
    assert report.terms == [2023]
    assert report.policies == ["arrival", "distribution-1", "resolution"]
    cells = 3 * len(registered_versions())  # 3 policies x every registered version
    assert report.cells_evaluated == cells
    assert report.salience_version == SALIENCE_VERSION
    assert f"salience-replay: {cells} cell(s)" in result.output


def test_cli_absent_corpus_writes_empty_report(tmp_path: Path) -> None:
    out = tmp_path / "salience-replay.json"
    result = runner.invoke(
        app,
        ["salience-replay", "--terms", "2022,2023", "--out", str(out)],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, SalienceReplay)
    assert report.cells_evaluated == 0 and report.cells == []
    assert report.terms == [2022, 2023]


def test_cli_rejects_an_unknown_policy(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["salience-replay", "--terms", "2023", "--policies", "bogus"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path)},
    )
    assert result.exit_code != 0
    assert "unknown policy 'bogus'" in result.output


def test_cli_rejects_non_year_terms(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["salience-replay", "--terms", "twenty-two"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path)},
    )
    assert result.exit_code != 0


def test_a_second_version_doubles_the_cells_over_one_shared_projection(
    tmp_path: Path, two_versions: SalienceScorer
) -> None:
    """The version axis, exercised — a foreign band vocabulary shows it plainly.

    Every registered scorer, one shared reconstruction per (Term, policy,
    distribution parse). What must be identical across a moment's cells is
    everything the projection decided: how many rows were eligible, how many had
    no snapshot, and where each reconstruction came from. What must differ is the
    banding, because that is the only thing the comparison is entitled to
    attribute to the scorer.

    The parse is the one axis that splits the reconstruction rather than riding
    it: sal-v4 pins `dist-v2` and is projected separately from the four `dist-v1`
    versions. Its projection-derived counts still match theirs — a parse changes
    the *count* read off a docket, never which dockets the frame holds or which
    of them disclosed a snapshot — so those figures are pinned across the parse
    split too, which is what makes a cross-parse band comparison legible.
    """
    db = _seed_replay_corpus(tmp_path / "corpus")
    report = replay_gate(db, terms=[2023], policies=[CutoffPolicy.resolution], config=_CONFIG)

    assert report.salience_versions == [SALIENCE_VERSION, "sal-toy", "sal-v1", "sal-v2", "sal-v4"]
    assert report.salience_version == SALIENCE_VERSION  # the report names the ACTIVE one
    assert report.cells_evaluated == 5  # one (term, policy) cell x 5 registered versions
    by_version = {cell.salience_version: cell for cell in report.cells}
    assert set(by_version) == {SALIENCE_VERSION, "sal-toy", "sal-v1", "sal-v2", "sal-v4"}
    active, toy, v1, v2, v4 = (
        by_version[v] for v in (SALIENCE_VERSION, "sal-toy", "sal-v1", "sal-v2", "sal-v4")
    )
    # Each cell records the parse its reconstruction was counted under.
    assert {active.distribution_parse, toy.distribution_parse} == {"dist-v1"}
    assert v4.distribution_parse == "dist-v2"

    # The projection is shared, so every projection-derived figure matches.
    for other in (toy, v1, v2, v4):
        assert active.eligible == other.eligible
        assert active.skipped_no_snapshot == other.skipped_no_snapshot
        assert active.provenance == other.provenance

    # The banding is not: each cell reports its own scorer's vocabulary, and
    # no version's band names appear under another's.
    caption_bands = {"federal", "high", "state", "elevated", "baseline", "unobservable"}
    assert set(active.bands) <= caption_bands
    assert set(v2.bands) <= caption_bands  # the caption-banded scorers share one vocabulary
    assert set(v4.bands) <= caption_bands  # sal-v4 shares sal-v3's vocabulary exactly
    assert set(toy.bands) <= {"hot", "cold", "unobservable"}
    assert set(v1.bands) <= {"high", "elevated", "baseline", "unobservable"}
    assert (
        sum(active.bands.values())
        == sum(toy.bands.values())
        == sum(v1.bands.values())
        == sum(v2.bands.values())
        == sum(v4.bands.values())
    )


def test_a_second_parse_gets_its_own_projection_and_bands_differently(tmp_path: Path) -> None:
    """The parse axis is a real split in the reconstruction, not a recorded label.

    Every other replay test seeds only entry-initial DISTRIBUTED lines, on which
    ``dist-v1`` and ``dist-v2`` count identically — so they would all pass against
    an implementation that reused one projection for every version and copied the
    label onto each cell. This seeds an ancillary paper's distributions, which the
    two readings disagree about, placed so the disagreement straddles a band
    cutpoint: ``dist-v1`` reads three conferences (relist-2, ``high``) while
    ``dist-v2`` reads the petition's own one (relist-0, ``baseline``).

    ``sal-v3`` and ``sal-v4`` differ in nothing but the parse, so a band
    difference between their cells can only have come from the split
    reconstruction.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row, payload = _petition(
        "scotus/9",
        "23-900",
        disposition=Disposition.denied,
        resolved=date(2024, 3, 4),
        entries=(
            ("Jan 5 2024", "Petition for a writ of certiorari filed."),
            ("Feb 2 2024", "DISTRIBUTED for Conference of February 16, 2024."),
            ("Feb 20 2024", "Motion (25M82) DISTRIBUTED for Conference of February 23, 2024."),
            ("Feb 26 2024", "Motion (25M83) DISTRIBUTED for Conference of March 1, 2024."),
            ("Mar 4 2024", "Petition DENIED."),
        ),
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        corpus.upsert_snapshot(conn, row.case_id, date(2024, 7, 1), payload)

    report = replay_gate(db, terms=[2023], policies=[CutoffPolicy.resolution], config=_CONFIG)
    cells = {cell.salience_version: cell for cell in report.cells}
    v3, v4 = cells["sal-v3"], cells["sal-v4"]

    assert (v3.distribution_parse, v4.distribution_parse) == ("dist-v1", "dist-v2")
    # The projection is split but reads the same frame: a parse changes the count
    # read off a docket, never which dockets are eligible or which disclosed a
    # state to reconstruct from.
    assert v3.eligible == v4.eligible == 1
    assert v3.skipped_no_snapshot == v4.skipped_no_snapshot == 0
    assert v3.provenance == v4.provenance
    # And the banding differs, which only a second reconstruction can produce.
    assert v3.bands == {"high": 1}
    assert v4.bands == {"baseline": 1}
