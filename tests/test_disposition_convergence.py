"""The disposition convergence sweep: re-resolve granted cert labels from docket text."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.disposition_convergence import (
    _arm,
    _Confirmation,
    _Skip,
    converge_disposition_labels,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import Disposition, Outcome, ResolutionSignals
from fedcourtsai.serialize import read_model, write_json

runner = CliRunner()

_CASE = "scotus/900001"
_DOCKET = 900001
_BASELINE = "evt-petition-disposition"
_MERITS = "evt-order-judgment"
_RESOLVED_AT = date(2026, 5, 11)
# A resolution from before the parser recorded labels: the protected residual.
_PRE_ERA_RESOLVED_AT = date(2019, 6, 24)

# The prose GVR: one order granting, vacating and remanding. `match_disposition_signal`
# reads it as `gvr` off the vacatur sentence; the plain grant below does not.
_GVR_TEXT = (
    "Petition GRANTED. Judgment VACATED and case REMANDED for further "
    "consideration in light of Louisiana v. Callais."
)
_PLAIN_GRANT_TEXT = "Petition GRANTED limited to Question 1 presented by the petition."
# A Munsingwear vacatur: the same shape with the basis the order's own words carry.
_MOOT_GVR_TEXT = (
    "Petition GRANTED. Judgment VACATED and case REMANDED with instructions to dismiss as moot."
)


def _write_outcome(
    data_root: Path,
    case_id: str,
    docket: int,
    event_id: str,
    disposition: Disposition,
    **fields: Any,
) -> Path:
    """One committed outcome, with the grant binary the disposition implies."""
    paths = CasePaths(data_root, "scotus", docket).event(event_id)
    write_json(
        paths.outcome,
        Outcome(
            case_id=case_id,
            event_id=event_id,
            resolved_at=_RESOLVED_AT,
            actual_disposition=disposition,
            actual_granted=1 if disposition is Disposition.granted else 0,
            **fields,
        ),
    )
    return paths.outcome


def _snapshot(*entries: tuple[str, str]) -> dict[str, Any]:
    """A live-shaped payload: (date, text) per proceedings entry."""
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


def _rest_snapshot(*entries: tuple[str, str]) -> dict[str, Any]:
    """The CourtListener REST payload shape, which the population also carries."""
    return {"docket_entries": [{"date_filed": d, "description": t} for d, t in entries]}


@contextmanager
def _seeded(tmp_path: Path, snapshots: dict[str, dict[str, Any]]) -> Iterator[sqlite3.Connection]:
    """A corpus holding one row and one snapshot per named case."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow.model_validate({"case_id": case_id, "court": "scotus"})
                for case_id in snapshots
            ],
        )
        for case_id, payload in snapshots.items():
            corpus.upsert_snapshot(conn, case_id, _RESOLVED_AT, payload)
        yield conn


def _data_root(tmp_path: Path) -> Path:
    return tmp_path / "data"


def _seed_granted_baseline(tmp_path: Path) -> Path:
    """A committed `granted` cert baseline — the population this sweep re-resolves."""
    return _write_outcome(_data_root(tmp_path), _CASE, _DOCKET, _BASELINE, Disposition.granted)


def test_dry_run_reports_the_prose_gvr_and_writes_nothing(tmp_path: Path) -> None:
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(conn, _data_root(tmp_path), apply=False)

    assert result.applied is False
    assert [entry.ref for entry in result.relabeled] == [f"{_CASE}/{_BASELINE}"]
    relabel = result.relabeled[0]
    assert relabel.was is Disposition.granted and relabel.now is Disposition.gvr
    assert relabel.basis == "standard"
    assert "VACATED" in relabel.evidence  # the order's own words are the report's evidence
    assert read_model(path, Outcome).actual_disposition == Disposition.granted  # untouched


def test_apply_relabels_and_stamps_the_basis(tmp_path: Path) -> None:
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.applied is True and len(result.relabeled) == 1
    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.gvr
    assert written.disposition_basis == "standard"
    # A GVR is a grant, so the binary scoring target does not move.
    assert written.actual_granted == 1
    assert written.votes == []


def test_the_basis_reads_the_order_that_vacated(tmp_path: Path) -> None:
    """A vacatur ordered "to dismiss as moot" is `gvr` + `mootness`, not `standard`."""
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _MOOT_GVR_TEXT))}) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.gvr
    assert written.disposition_basis == "mootness"


def test_apply_is_idempotent(tmp_path: Path) -> None:
    _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)
        again = converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)
    # The relabeled outcome has left the population: it no longer reads `granted`.
    assert again.relabeled == []
    assert again.skipped == []


def test_a_plain_grant_is_left_alone(tmp_path: Path) -> None:
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _PLAIN_GRANT_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert result.skipped == [
        (f"{_CASE}/{_BASELINE}", "docket text parses 'granted'; the label agrees")
    ]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_a_case_with_no_snapshot_is_skipped_with_its_reason(tmp_path: Path) -> None:
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert result.skipped == [
        (
            f"{_CASE}/{_BASELINE}",
            "no stored snapshot for the case, so there is no docket text to re-resolve against",
        )
    ]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_an_order_before_the_resolution_date_is_out_of_range(tmp_path: Path) -> None:
    """An earlier order on the same docket never authorizes the relabel."""
    _seed_granted_baseline(tmp_path)
    snapshot = _snapshot(("2026-01-05", _GVR_TEXT))
    with _seeded(tmp_path, {_CASE: snapshot}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert result.skipped[0][0] == f"{_CASE}/{_BASELINE}"
    assert "none of them parses as a disposition" in result.skipped[0][1]


def test_a_label_no_arm_names_is_reported_not_applied() -> None:
    """The total-function default: a parse neither arm claims is reported, never acted on.

    Unreachable through the sweep today — every label
    `cert_signals._ENTRY_SIGNALS` can return is either `granted` (which agrees)
    or one of the two arms' — so it is exercised directly. It is what a label
    the parser gains later would meet, and the point is that the sweep's remit
    only ever widens deliberately.
    """
    confirmed = _Confirmation(
        disposition=Disposition.withdrawn,
        basis="standard",
        evidence="Petition WITHDRAWN.",
        filed=_RESOLVED_AT,
    )
    outcome = Outcome(
        case_id=_CASE,
        event_id=_BASELINE,
        resolved_at=_RESOLVED_AT,
        actual_disposition=Disposition.granted,
        actual_granted=1,
    )
    chosen = _arm(confirmed, Disposition.granted, outcome, _snapshot(("2026-05-11", "Docketed.")))
    assert isinstance(chosen, _Skip)
    assert "outside this sweep's remit" in chosen.reason


def test_a_non_granted_outcome_is_never_in_the_population(tmp_path: Path) -> None:
    path = _write_outcome(_data_root(tmp_path), _CASE, _DOCKET, _BASELINE, Disposition.denied)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == [] and result.skipped == []
    assert read_model(path, Outcome).actual_disposition == Disposition.denied


def test_a_non_cert_stage_outcome_is_never_in_the_population(tmp_path: Path) -> None:
    """The merits moment forecasts the judgment, so the cert vocabulary has no claim on it."""
    path = _write_outcome(_data_root(tmp_path), _CASE, _DOCKET, _MERITS, Disposition.granted)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == [] and result.skipped == []
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_cli_apply_relabels_the_ledger(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels", "--apply", "--max-relabels", "20"])
    assert result.exit_code == 0, result.output
    assert "relabeled 1 of 1 checkable" in result.output
    assert "granted -> gvr" in result.output
    assert read_model(path, Outcome).actual_disposition == Disposition.gvr


def test_cli_dry_run_reports_without_writing(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels"])
    assert result.exit_code == 0, result.output
    assert "would relabel 1 of 1 checkable" in result.output
    assert f"{_CASE}/{_BASELINE}" in result.output
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_cli_apply_refuses_above_the_relabel_bound(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The blast-radius cap: an over-bound apply exits non-zero and writes nothing.

    The population is finite and non-growing, so the bound turns a widened
    predicate from an unattended mass rewrite in the writer lane into a loud
    refusal the run's log names.
    """
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels", "--apply", "--max-relabels", "0"])
    assert result.exit_code == 1
    assert "refusing to apply 1 relabels (--max-relabels 0)" in result.output
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_cli_exits_when_the_corpus_is_absent(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _seed_granted_baseline(tmp_path)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.output


# --- payload shapes, entry selection, and the fields that must not move ---------


def test_the_rest_payload_shape_reads_the_same(tmp_path: Path) -> None:
    """Both stored shapes reach the parser, so the population is not live-only."""
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _rest_snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert len(result.relabeled) == 1
    assert read_model(path, Outcome).actual_disposition == Disposition.gvr


def test_an_undated_entry_is_never_read(tmp_path: Path) -> None:
    """A partial date is refused rather than guessed at, so it confirms nothing."""
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "none of them parses as a disposition" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_the_earliest_dated_order_wins_regardless_of_payload_order(tmp_path: Path) -> None:
    """Selection is by date, not position: upstream's ordering must not decide the label."""
    _seed_granted_baseline(tmp_path)
    # The later denial is listed FIRST; the disposing GVR order is listed second.
    snapshot = _snapshot(("2026-06-01", "Petition DENIED."), ("2026-05-11", _GVR_TEXT))
    with _seeded(tmp_path, {_CASE: snapshot}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert len(result.relabeled) == 1
    assert result.relabeled[0].now is Disposition.gvr


def test_a_committed_mootness_basis_is_never_cleared(tmp_path: Path) -> None:
    """The basis latches on: a demotion would move the cell into a ranked stratum."""
    path = _write_outcome(
        _data_root(tmp_path),
        _CASE,
        _DOCKET,
        _BASELINE,
        Disposition.granted,
        disposition_basis="mootness",
    )
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.gvr
    assert written.disposition_basis == "mootness"  # the standard parse did not demote it
    assert result.relabeled[0].basis == "mootness"


def test_an_assessed_route_advances_with_the_label(tmp_path: Path) -> None:
    """`disposition_route` is derived from the label, so a stale `plenary` cannot stand."""
    path = _write_outcome(
        _data_root(tmp_path),
        _CASE,
        _DOCKET,
        _BASELINE,
        Disposition.granted,
        disposition_route="plenary",
    )
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.gvr
    assert written.disposition_route == "gvr"


def test_an_unassessed_route_stays_null(tmp_path: Path) -> None:
    """A null route is a coverage sentinel; filling it in would widen the assessed set."""
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    assert read_model(path, Outcome).disposition_route is None


def test_every_other_recorded_field_survives_the_relabel(tmp_path: Path) -> None:
    """The write is a `model_copy`, so nothing the record already carried is dropped."""
    path = _write_outcome(
        _data_root(tmp_path),
        _CASE,
        _DOCKET,
        _BASELINE,
        Disposition.granted,
        source="entry-42",
        noted_dissent_from_denial=False,
    )
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.gvr
    assert written.source == "entry-42"
    assert written.noted_dissent_from_denial is False
    assert written.resolved_at == _RESOLVED_AT
    assert written.actual_granted == 1


def test_an_undeclared_event_id_is_reported_not_swept(tmp_path: Path) -> None:
    """The dry run is only a complete ledger if an unjudgeable id says so."""
    path = _write_outcome(
        _data_root(tmp_path), _CASE, _DOCKET, "evt-order-something-legacy", Disposition.granted
    )
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "declares no stage for this event id" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_a_mixed_run_relabels_and_reports_across_cases(tmp_path: Path) -> None:
    """Several cases in one pass: the report carries both halves."""
    root = _data_root(tmp_path)
    _write_outcome(root, _CASE, _DOCKET, _BASELINE, Disposition.granted)
    _write_outcome(root, "scotus/900002", 900002, _BASELINE, Disposition.granted)
    _write_outcome(root, "scotus/900003", 900003, _BASELINE, Disposition.granted)
    snapshots = {
        _CASE: _snapshot(("2026-05-11", _GVR_TEXT)),
        "scotus/900002": _snapshot(("2026-05-11", _GVR_TEXT)),
        "scotus/900003": _snapshot(("2026-05-11", _PLAIN_GRANT_TEXT)),
    }
    with _seeded(tmp_path, snapshots) as conn:
        result = converge_disposition_labels(conn, root, apply=True, max_relabels=20)

    assert [entry.ref for entry in result.relabeled] == [
        f"{_CASE}/{_BASELINE}",
        f"scotus/900002/{_BASELINE}",
    ]
    assert [ref for ref, _reason in result.skipped] == [f"scotus/900003/{_BASELINE}"]


def test_cli_bound_counts_the_whole_run_not_one_case(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Two confirmed relabels refuse under a bound of one, and neither is written."""
    root = _data_root(tmp_path)
    first = _write_outcome(root, _CASE, _DOCKET, _BASELINE, Disposition.granted)
    second = _write_outcome(root, "scotus/900002", 900002, _BASELINE, Disposition.granted)
    snapshots = {
        _CASE: _snapshot(("2026-05-11", _GVR_TEXT)),
        "scotus/900002": _snapshot(("2026-05-11", _GVR_TEXT)),
    }
    with _seeded(tmp_path, snapshots):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels", "--apply", "--max-relabels", "1"])
    assert result.exit_code == 1
    assert "refusing to apply 2 relabels (--max-relabels 1)" in result.output
    assert read_model(first, Outcome).actual_disposition == Disposition.granted
    assert read_model(second, Outcome).actual_disposition == Disposition.granted


# --- the era boundary: the older vocabulary's record is not a parse gap ---------


def _write_pre_era_outcome(tmp_path: Path) -> Path:
    """A `granted` cert baseline resolved before the parser recorded labels."""
    paths = CasePaths(_data_root(tmp_path), "scotus", _DOCKET).event(_BASELINE)
    write_json(
        paths.outcome,
        Outcome(
            case_id=_CASE,
            event_id=_BASELINE,
            resolved_at=_PRE_ERA_RESOLVED_AT,
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )
    return paths.outcome


def test_a_pre_era_outcome_is_left_alone_even_when_the_text_parses_gvr(tmp_path: Path) -> None:
    """The protected residual: `granted` there is the older vocabulary, not a parse gap.

    This is the separation the forward-convention rule rests on, so it is
    enforced in the predicate rather than left to snapshot coverage — widening
    the snapshot store must never quietly reach these rows.
    """
    path = _write_pre_era_outcome(tmp_path)
    snapshot = {"ProceedingsandOrder": [{"Date": "2019-06-24", "Text": _GVR_TEXT}]}
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [corpus.CorpusRow.model_validate({"case_id": _CASE, "court": "scotus"})]
        )
        corpus.upsert_snapshot(conn, _CASE, _PRE_ERA_RESOLVED_AT, snapshot)
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "the older vocabulary's record, not a parse gap" in result.skipped[0][1]
    assert result.out_of_scope == 1 and result.checkable == 0
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


# --- scored cells: a committed evaluation holds the relabel back ----------------


def _stamp_evaluation(tmp_path: Path) -> None:
    """A committed evaluate cell under the event, as the ledger lays it out."""
    paths = CasePaths(_data_root(tmp_path), "scotus", _DOCKET).event(_BASELINE)
    cell = paths.evaluations_dir / "some-evaluator" / "20260801T000000Z"
    cell.mkdir(parents=True)
    (cell / "evaluation.json").write_text("{}")


def test_a_scored_cell_is_held_back_by_default(tmp_path: Path) -> None:
    """A stamped `correct` bit was computed from this label, so the relabel waits."""
    path = _seed_granted_baseline(tmp_path)
    _stamp_evaluation(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "committed predict/evaluate output" in result.skipped[0][1]
    assert result.out_of_scope == 1
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_include_scored_relabels_and_reports_the_regrade_backlog(tmp_path: Path) -> None:
    """Opting in relabels and states the re-grade debt the write creates."""
    path = _seed_granted_baseline(tmp_path)
    _stamp_evaluation(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20, include_scored=True
        )

    assert len(result.relabeled) == 1
    assert result.relabeled[0].stamped_evaluations == 1
    assert read_model(path, Outcome).actual_disposition == Disposition.gvr


def test_cli_apply_requires_an_explicit_bound(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The maintainer states the number they read in the dry run; no default applies."""
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels", "--apply"])
    assert result.exit_code == 2
    assert "--apply requires an explicit --max-relabels" in result.output
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_the_dry_run_needs_no_bound(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Reading the ledger is unbounded; only the write demands a stated number."""
    _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels"])
    assert result.exit_code == 0, result.output
    assert "would relabel 1 of 1 checkable" in result.output


def test_the_evidence_line_carries_the_three_dates(tmp_path: Path) -> None:
    """The review-of-record question is whether the matched entry is the resolving order."""
    _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        result = converge_disposition_labels(conn, _data_root(tmp_path), apply=False)

    entry = result.relabeled[0]
    assert entry.entry_filed == date(2026, 5, 11)
    assert entry.resolved_at == _RESOLVED_AT
    assert entry.snapshot_date == _RESOLVED_AT
    # Both halves of the order and the citation that identifies it.
    assert "GRANTED" in entry.evidence and "VACATED" in entry.evidence
    assert "Louisiana v. Callais" in entry.evidence


def test_a_snapshot_predating_the_resolution_is_uncheckable(tmp_path: Path) -> None:
    """Structurally uncheckable, and counted apart from a snapshot that simply disagrees."""
    _seed_granted_baseline(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [corpus.CorpusRow.model_validate({"case_id": _CASE, "court": "scotus"})]
        )
        corpus.upsert_snapshot(
            conn, _CASE, date(2026, 1, 5), _snapshot(("2026-01-05", "Docketed."))
        )
        result = converge_disposition_labels(conn, _data_root(tmp_path), apply=False)

    assert result.relabeled == []
    assert "the stored snapshot predates the resolution" in result.skipped[0][1]
    assert result.uncheckable == 1 and result.checkable == 0


# --- the disowned-grant arm: a grant read off an ancillary order ----------------
#
# Verbatim proceedings text from the dockets whose stored `granted` these orders
# fabricated. The extension order is No. 18-710's (the petition was denied); the
# distribution order is No. 19-1094's (denied); the unsealing order is No.
# 21-497's, where the denial lands the same day.

_EXTENSION_ORDER = (
    "The motions to extend the time to file responses to the petition for a writ "
    "of certiorari are granted and the time is extended to and including "
    "March 18, 2019, for all respondents."
)
_DISTRIBUTION_ORDER = (
    "Motion to delay distribution of the petition for a writ certiorari granted; "
    "the petition will be distributed on June 17, 2020."
)
_UNSEAL_ORDER = "Motion to unseal the petition for a writ of certiorari GRANTED."


def _seed_ancillary_grant(tmp_path: Path, resolved_at: date, **fields: Any) -> Path:
    """A `granted` cert baseline dated to an ancillary order, as the ledger holds them."""
    paths = CasePaths(_data_root(tmp_path), "scotus", _DOCKET).event(_BASELINE)
    write_json(
        paths.outcome,
        Outcome(
            case_id=_CASE,
            event_id=_BASELINE,
            resolved_at=resolved_at,
            actual_disposition=Disposition.granted,
            actual_granted=1,
            **fields,
        ),
    )
    return paths.outcome


@contextmanager
def _seeded_at(
    tmp_path: Path, snapshot_date: date, payload: dict[str, Any]
) -> Iterator[sqlite3.Connection]:
    """One case, one snapshot, taken on a caller-chosen day."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [corpus.CorpusRow.model_validate({"case_id": _CASE, "court": "scotus"})]
        )
        corpus.upsert_snapshot(conn, _CASE, snapshot_date, payload)
        yield conn


def _ancillary_then_denial(
    ancillary: str,
    granted_on: date,
    terminal: str,
    terminal_on: date,
) -> dict[str, Any]:
    """The class's docket shape: the housekeeping order, then the real terminal."""
    return _snapshot((granted_on.isoformat(), ancillary), (terminal_on.isoformat(), terminal))


def test_a_grant_read_off_an_extension_order_is_withdrawn(tmp_path: Path) -> None:
    """The class this arm exists for: the label's own entry no longer parses as a grant.

    Pre-era on purpose — every real member of the class is — which is why the
    warrant is in the docket text rather than on the calendar.
    """
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert len(result.relabeled) == 1
    relabel = result.relabeled[0]
    assert relabel.arm == "disowned-grant"
    assert relabel.was is Disposition.granted and relabel.now is Disposition.denied
    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.denied
    # The binary and the date move with the label: the record's whole warrant is
    # the denial entry now, so leaving either would date a denial to a motion.
    assert written.actual_granted == 0
    assert written.resolved_at == denied_on


def test_a_grant_read_off_a_distribution_order_is_withdrawn(tmp_path: Path) -> None:
    """The second wording of the same mistake, and the semicolon that splits it."""
    granted_on, denied_on = date(2020, 5, 21), date(2020, 10, 5)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(_DISTRIBUTION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.denied
    assert written.actual_granted == 0 and written.resolved_at == denied_on


def test_a_same_day_denial_beside_the_ancillary_order_still_resolves(tmp_path: Path) -> None:
    """The unsealing order and the denial share a day; the denial is the one that decides."""
    both_on = date(2021, 12, 6)
    path = _seed_ancillary_grant(tmp_path, both_on)
    payload = _ancillary_then_denial(_UNSEAL_ORDER, both_on, "Petition DENIED.", both_on)
    with _seeded_at(tmp_path, both_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert len(result.relabeled) == 1
    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.denied
    assert written.resolved_at == both_on


def test_a_petition_stage_rule_46_dismissal_is_the_other_terminal(tmp_path: Path) -> None:
    """Two of the class exit by Rule 46 rather than denial, so both labels must land."""
    granted_on, dismissed_on = date(2019, 3, 21), date(2019, 6, 10)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(
        _EXTENSION_ORDER, granted_on, "Petition Dismissed - Rule 46.", dismissed_on
    )
    with _seeded_at(tmp_path, dismissed_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled[0].now is Disposition.dismissed
    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.dismissed
    assert written.actual_granted == 0


def test_a_real_grant_with_a_later_dismissal_is_never_withdrawn(tmp_path: Path) -> None:
    """The mistake this arm must never make: a post-grant Rule 46 exit is not a correction.

    The grant order still parses, so the docket-wide grant test refuses the
    withdrawal however the docket ends.
    """
    granted_on, dismissed_on = date(2021, 2, 22), date(2021, 3, 12)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(
        "Petition GRANTED. The cases are consolidated. VIDED.",
        granted_on,
        "Writ of Certiorari Dismissed - Rule 46.",
        dismissed_on,
    )
    with _seeded_at(tmp_path, dismissed_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "the label agrees" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_a_grant_order_before_the_recorded_date_still_protects_the_label(
    tmp_path: Path,
) -> None:
    """The grant test is docket-wide, not scoped to the confirming entry's window.

    Here the record is dated to the dismissal rather than to the grant, so the
    entry the sweep confirms off *is* a dismissal — and the earlier grant order,
    outside that window entirely, is the only thing standing between a real
    grant and a withdrawal.
    """
    granted_on, recorded_on = date(2021, 2, 22), date(2021, 3, 12)
    path = _seed_ancillary_grant(tmp_path, recorded_on)
    payload = _snapshot(
        (granted_on.isoformat(), "Petition GRANTED."),
        (recorded_on.isoformat(), "Writ of Certiorari Dismissed - Rule 46."),
    )
    with _seeded_at(tmp_path, recorded_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "still parses as a grant" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_a_resolution_date_with_no_entry_is_reported_not_withdrawn(tmp_path: Path) -> None:
    """No entry that day means the label was not read off this docket: the protected residual."""
    path = _seed_ancillary_grant(tmp_path, date(2019, 2, 4))
    payload = _snapshot(("2019-04-22", "Petition DENIED."))
    with _seeded_at(tmp_path, date(2019, 4, 22), payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "no entry dated the recorded resolution" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_an_unrelated_entry_on_the_recorded_day_does_not_warrant_a_withdrawal(
    tmp_path: Path,
) -> None:
    """The warrant is the refused *sentence*, never merely a docket day that has entries.

    The dangerous shape, and the reason the test is stricter than "an entry
    exists": a real grant whose order text the payload does not carry, with a
    routine entry on the recorded day and a Rule 46 exit later. Warranted on a
    day-only test, refused here — there is no sentence a grant could have been
    read out of.
    """
    granted_on, dismissed_on = date(2021, 2, 22), date(2021, 3, 12)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _snapshot(
        (granted_on.isoformat(), "Distributed for Conference of March 5, 2021."),
        (dismissed_on.isoformat(), "Petition Dismissed - Rule 46."),
    )
    with _seeded_at(tmp_path, dismissed_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "no entry dated the recorded resolution" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


def test_the_report_quotes_the_sentence_the_grant_was_read_out_of(tmp_path: Path) -> None:
    """A withdrawal rests on two texts, and the refused one is the half under review."""
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        result = converge_disposition_labels(conn, _data_root(tmp_path), apply=False)

    relabel = result.relabeled[0]
    assert relabel.recital is not None
    assert "motions to extend the time" in relabel.recital
    # And the confirming order stays the `evidence`, so the two are not conflated.
    assert relabel.evidence == "Petition DENIED."


def test_a_withdrawal_never_moves_the_resolution_backward(tmp_path: Path) -> None:
    """The date is monotone forward, which is the property the stratum argument rests on.

    `_confirming_signal` reads only entries at or after the recorded resolution,
    so a withdrawal can push an already-scored cell toward the `forward` stratum
    and clear a forward-claim breach, never the reverse. An earlier terminal on
    the same docket must not be reachable, or that one-sidedness stops holding.
    """
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _snapshot(
        # An earlier denial the sweep must not reach, then the ancillary order
        # the label was read from, then the real terminal.
        ("2018-11-05", "Petition DENIED."),
        (granted_on.isoformat(), _EXTENSION_ORDER),
        (denied_on.isoformat(), "Petition DENIED."),
    )
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled[0].entry_filed == denied_on
    assert read_model(path, Outcome).resolved_at == denied_on >= granted_on


def test_a_withdrawal_clears_the_signal_blocks(tmp_path: Path) -> None:
    """`signals` is frozen *as at resolution*, so a moved date strands it.

    The increment claims score the block against the prediction-time value, and
    a block frozen at the ancillary order would hide every docket step between
    the two dates — resolving those claims 0 where the truth is 1. Null is the
    field's own "nobody looked" sentinel, which every claim masks on.
    """
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    path = _seed_ancillary_grant(
        tmp_path,
        granted_on,
        signals=ResolutionSignals(distribution_count=1, cvsg_date=None),
    )
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    written = read_model(path, Outcome)
    assert written.resolved_at == denied_on
    assert written.signals is None


def test_the_gvr_arm_keeps_the_signal_blocks(tmp_path: Path) -> None:
    """It does not move the date, so the block still describes the resolution it was frozen at."""
    path = _write_outcome(
        _data_root(tmp_path),
        _CASE,
        _DOCKET,
        _BASELINE,
        Disposition.granted,
        signals=ResolutionSignals(distribution_count=1, cvsg_date=None),
    )
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", _GVR_TEXT))}) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.gvr
    assert written.signals is not None and written.signals.distribution_count == 1


def test_a_withdrawal_clears_an_assessed_route(tmp_path: Path) -> None:
    """`disposition_route` reads null for every non-grant, so a stale `plenary` cannot stand."""
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    path = _seed_ancillary_grant(tmp_path, granted_on, disposition_route="plenary")
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    assert read_model(path, Outcome).disposition_route is None


def test_a_scored_withdrawal_is_held_back_like_any_other(tmp_path: Path) -> None:
    """The holdback is arm-blind: a stamped `correct` bit was computed from this label too."""
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    _stamp_evaluation(tmp_path)
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        held = converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)
        opted_in = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20, include_scored=True
        )

    assert held.relabeled == [] and "committed predict/evaluate output" in held.skipped[0][1]
    assert len(opted_in.relabeled) == 1
    assert opted_in.relabeled[0].stamped_evaluations == 1
    assert read_model(path, Outcome).actual_disposition == Disposition.denied


def test_a_withdrawal_is_idempotent(tmp_path: Path) -> None:
    """The relabel leaves the population: a denied outcome no longer reads `granted`."""
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)
        again = converge_disposition_labels(conn, _data_root(tmp_path), apply=True, max_relabels=20)

    assert again.relabeled == [] and again.skipped == []


def test_the_dry_run_reports_a_withdrawal_without_writing(tmp_path: Path) -> None:
    """Dry-run-first holds for the arm that moves the binary most of all."""
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    path = _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload) as conn:
        result = converge_disposition_labels(conn, _data_root(tmp_path), apply=False)

    assert result.applied is False and len(result.relabeled) == 1
    written = read_model(path, Outcome)
    assert written.actual_disposition == Disposition.granted and written.actual_granted == 1


def test_cli_names_the_arm_and_the_fields_it_moves(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The maintainer approves a count with `--max-relabels`, so the line has to say which."""
    granted_on, denied_on = date(2019, 2, 4), date(2019, 4, 22)
    _seed_ancillary_grant(tmp_path, granted_on)
    payload = _ancillary_then_denial(_EXTENSION_ORDER, granted_on, "Petition DENIED.", denied_on)
    with _seeded_at(tmp_path, denied_on, payload):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["converge-disposition-labels"])

    assert result.exit_code == 0, result.output
    assert "(0 gvr, 1 disowned-grant)" in result.output
    assert "[disowned-grant]: granted -> denied" in result.output
    assert "grant bit 1 -> 0, resolution re-dated to 2019-04-22" in result.output
    # Both texts, so the maintainer choosing `--max-relabels` reads the warrant
    # for the withdrawal as well as the order that replaces it.
    assert "read from 'The motions to extend the time" in result.output
    assert "'Petition DENIED.'" in result.output
