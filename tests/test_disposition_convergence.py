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
from fedcourtsai.disposition_convergence import converge_disposition_labels
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import Disposition, Outcome
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


def test_a_disagreeing_parse_outside_the_remit_is_reported_not_applied(tmp_path: Path) -> None:
    """The sweep declines a label it now disagrees with unless the parse is `gvr`."""
    path = _seed_granted_baseline(tmp_path)
    with _seeded(tmp_path, {_CASE: _snapshot(("2026-05-11", "Petition DENIED."))}) as conn:
        result = converge_disposition_labels(
            conn, _data_root(tmp_path), apply=True, max_relabels=20
        )

    assert result.relabeled == []
    assert "outside this sweep's remit" in result.skipped[0][1]
    assert read_model(path, Outcome).actual_disposition == Disposition.granted


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
