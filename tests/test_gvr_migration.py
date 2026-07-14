"""Tests for the one-time GVR-label backfill (relabel Munsingwear grants to gvr)."""

from __future__ import annotations

from pathlib import Path

from fedcourtsai.gvr_migration import relabel_munsingwear_gvr_outcomes
from fedcourtsai.schemas import Disposition, Outcome
from fedcourtsai.serialize import read_model, write_json


def _write_outcome(data_root: Path, case_id: str, disposition: Disposition, basis: str) -> Path:
    path = data_root / "cases" / case_id / "events" / "evt-petition-disposition" / "outcome.json"
    write_json(
        path,
        Outcome(
            case_id=case_id,
            event_id="evt-petition-disposition",
            resolved_at="2026-01-01",
            actual_disposition=disposition,
            actual_granted=1 if disposition in (Disposition.granted, Disposition.gvr) else 0,
            disposition_basis=basis,
        ),
    )
    return path


def test_relabels_only_the_munsingwear_grants(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    munsingwear = _write_outcome(data_root, "scotus/1", Disposition.granted, "mootness")
    merits_gvr = _write_outcome(data_root, "scotus/2", Disposition.granted, "standard")
    denied = _write_outcome(data_root, "scotus/3", Disposition.denied, "standard")

    result = relabel_munsingwear_gvr_outcomes(data_root, apply=True)

    assert result.applied is True
    assert result.relabeled == ["scotus/1"]
    # The Munsingwear grant flips to gvr; its basis and binary grant are preserved.
    m = read_model(munsingwear, Outcome)
    assert m.actual_disposition == Disposition.gvr
    assert m.disposition_basis == "mootness"
    assert m.actual_granted == 1
    # A plain-granted merits outcome (indistinguishable post-hoc) is left as granted.
    assert read_model(merits_gvr, Outcome).actual_disposition == Disposition.granted
    assert read_model(denied, Outcome).actual_disposition == Disposition.denied


def test_dry_run_finds_but_writes_nothing(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    path = _write_outcome(data_root, "scotus/1", Disposition.granted, "mootness")
    result = relabel_munsingwear_gvr_outcomes(data_root, apply=False)
    assert result.applied is False and result.relabeled == ["scotus/1"]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted  # untouched


def test_is_idempotent(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/1", Disposition.granted, "mootness")
    relabel_munsingwear_gvr_outcomes(data_root, apply=True)
    again = relabel_munsingwear_gvr_outcomes(data_root, apply=True)
    assert again.relabeled == []  # already gvr, no longer matches
