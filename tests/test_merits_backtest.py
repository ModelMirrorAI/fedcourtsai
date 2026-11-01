import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import corpus, merits_backtest
from fedcourtsai.cli import app
from fedcourtsai.merits_backtest import (
    KEPT_FILE_MAX_BYTES,
    KEPT_FORECAST_FILES,
    MERITS_BACKTEST_MOMENTS,
    MeritsReplayCase,
    MeritsReplayCell,
    MeritsReplayFenced,
    draw_cases,
    draw_rank,
    kept_forecasts,
    merits_backtest_population,
    moment_root,
    provision_replay_cell,
    provision_replay_cells,
    replay_merits_predictors,
    score_merits_backtest,
)
from fedcourtsai.pipeline.runner import EngineFailed, EngineQuotaExhausted
from fedcourtsai.provision import SNAPSHOT_OUTCOME_FIELDS
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import Judgment, MeritsBacktest, Moment

runner = CliRunner()


def _argued(case: int, docket: str, **fields: Any) -> corpus.CorpusRow:
    """A decided argued OT2024 plenary docket: granted, briefed, argued, reversed."""
    base: dict[str, Any] = {
        "case_id": f"scotus/{case}",
        "court": "scotus",
        "docket_number": docket,
        "case_name": f"Case {docket}",
        "disposition": "granted",
        "date_cert_granted": date(2024, 6, 3),
        "merits_brief_filed": date(2024, 9, 16),
        "merits_argued": date(2024, 12, 2),
        "merits_decided": date(2025, 5, 22),
        "merits_judgment": Judgment.reversed.value,
        "merits_decision_method": "argued-signed",
    }
    return corpus.CorpusRow.model_validate({**base, **fields})


def _member_payload(own: str, lead: str) -> dict[str, Any]:
    return {
        "CaseNumber": own,
        "ProceedingsandOrder": [
            {
                "Date": "Jul 01 2024",
                "Text": "Consolidated. Future filings and activity in the cases will now be "
                + f"reflected on the docket of No. {lead}.",
            }
        ],
    }


@contextmanager
def _seeded(
    tmp_path: Path,
    rows: list[corpus.CorpusRow],
    snapshots: dict[str, dict[str, Any] | None] | None = None,
) -> Iterator[corpus.ReadConnection]:
    """Seed ``rows``, each with a plain stored snapshot unless ``snapshots`` names one;
    a ``None`` there leaves that case with no snapshot at all."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    stored: dict[str, dict[str, Any] | None] = {
        row.case_id: {"CaseNumber": row.docket_number, "ProceedingsandOrder": []} for row in rows
    }
    stored.update(snapshots or {})
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        for case_id, payload in stored.items():
            if payload is not None:
                corpus.upsert_snapshot(conn, case_id, date(2025, 7, 1), payload)
        conn.commit()
        yield conn


def test_a_decided_argued_case_is_replayed_at_both_moments(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_argued(1, "24-100")]) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    [case] = population.cases
    assert (case.case_id, case.term, case.judgment, case.disturbed) == (
        "scotus/1",
        2024,
        Judgment.reversed,
        True,
    )
    assert [c.moment for c in case.cutoffs] == list(MERITS_BACKTEST_MOMENTS)
    grant, briefed = case.cutoffs
    assert (grant.event_id, grant.opened_at, grant.cutoff) == (
        "evt-order-judgment",
        date(2024, 6, 3),
        date(2024, 6, 4),
    )
    assert (briefed.event_id, briefed.opened_at, briefed.cutoff) == (
        "evt-brief-judgment",
        date(2024, 9, 16),
        date(2024, 9, 17),
    )


def test_a_dig_and_an_equally_divided_court_stay_in_as_undisturbed(tmp_path: Path) -> None:
    """Forward merits cells are scored on both, and the base rate counts them."""
    rows = [
        _argued(1, "24-100", merits_judgment=Judgment.dig.value, merits_decision_method="dig"),
        _argued(
            2,
            "24-200",
            merits_judgment=Judgment.equally_divided.value,
            merits_decision_method="argued-per-curiam",
        ),
    ]
    with _seeded(tmp_path, rows) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert [(c.case_id, c.disturbed) for c in population.cases] == [
        ("scotus/1", False),
        ("scotus/2", False),
    ]


def test_order_riding_pending_and_terminated_grants_are_never_candidates(
    tmp_path: Path,
) -> None:
    rows = [
        _argued(1, "24-100"),
        # A GVR: the disposition rode the grant order.
        _argued(
            2,
            "24-200",
            disposition="gvr",
            date_cert_granted=date(2024, 11, 4),
            merits_argued=None,
            merits_brief_filed=None,
            merits_judgment=None,
            merits_decided=None,
            merits_decision_method=None,
        ),
        # Argued, not yet decided.
        _argued(3, "24-300", merits_judgment=None, merits_decided=None),
        # Dismissed after the grant: nothing decided.
        _argued(
            4,
            "24-400",
            merits_judgment=None,
            merits_decided=None,
            merits_terminated="voluntary-dismissal",
        ),
    ]
    with _seeded(tmp_path, rows) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert [c.case_id for c in population.cases] == ["scotus/1"]
    assert population.excluded == []
    [term] = population.terms
    assert (term.order_riding, term.plenary_decided, term.cases) == (1, 1, 1)


def test_a_consolidated_member_is_set_aside_for_its_lead(tmp_path: Path) -> None:
    """The member carries its own briefed date, so only the consolidation entry sets it aside."""
    rows = [_argued(1, "24-20"), _argued(2, "24-151")]
    snapshots: dict[str, dict[str, Any] | None] = {
        "scotus/1": _member_payload("24-20", "24-20"),
        "scotus/2": _member_payload("24-151", "24-20"),
    }
    with _seeded(tmp_path, rows, snapshots) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert [c.case_id for c in population.cases] == ["scotus/1"]
    [member] = population.excluded
    assert (member.docket_number, member.reason) == ("24-151", "consolidated-member")
    assert "No. 24-20" in member.detail
    assert population.terms[0].excluded == {"consolidated-member": 1}


def test_a_member_whose_lead_is_not_kept_is_named_as_such(tmp_path: Path) -> None:
    """The argued case drops out whole, and the record says so rather than "for its lead"."""
    rows = [_argued(1, "24-20", merits_brief_filed=None), _argued(2, "24-151")]
    snapshots: dict[str, dict[str, Any] | None] = {"scotus/2": _member_payload("24-151", "24-20")}
    with _seeded(tmp_path, rows, snapshots) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert population.cases == []
    assert sorted((e.docket_number, e.reason) for e in population.excluded) == [
        ("24-151", "lead-not-replayed"),
        ("24-20", "no-briefed-date"),
    ]


def test_a_docket_with_no_snapshot_is_set_aside_rather_than_guessed(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_argued(1, "24-100")], {"scotus/1": None}) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert population.cases == []
    assert [e.reason for e in population.excluded] == ["no-snapshot"]


def test_a_set_aside_docket_carries_its_judgment_for_the_audit(tmp_path: Path) -> None:
    row = _argued(1, "24-100", merits_brief_filed=None, merits_judgment=Judgment.affirmed.value)
    with _seeded(tmp_path, [row]) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    [item] = population.excluded
    assert (item.judgment, item.disturbed) == (Judgment.affirmed, False)


def test_an_argued_docket_with_no_judgment_read_is_counted(tmp_path: Path) -> None:
    """A parse gap the draw cannot keep is counted rather than silent."""
    rows = [_argued(1, "24-100"), _argued(2, "24-200", merits_judgment=None)]
    with _seeded(tmp_path, rows) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    [term] = population.terms
    assert (term.argued_unjudged, term.plenary_decided, term.cases) == (1, 1, 1)


def test_a_reargued_case_keeps_cuts_that_precede_its_first_argument(tmp_path: Path) -> None:
    """Assigned by its reargument, cut at the grant and the briefs the first argument followed."""
    row = _argued(1, "23-100", merits_argued=date(2024, 10, 7))
    with _seeded(tmp_path, [row]) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    [case] = population.cases
    assert case.term == 2024
    assert [c.cutoff for c in case.cutoffs] == [date(2024, 6, 4), date(2024, 9, 17)]


def test_a_case_without_a_briefed_date_is_set_aside_rather_than_replayed_once(
    tmp_path: Path,
) -> None:
    """Every kept case faces both moments, so a case missing one is out whole."""
    with _seeded(tmp_path, [_argued(1, "24-100", merits_brief_filed=None)]) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert population.cases == []
    assert [e.reason for e in population.excluded] == ["no-briefed-date"]


@pytest.mark.parametrize(
    "briefed",
    [date(2024, 5, 1), date(2024, 6, 3), date(2024, 12, 3)],
    ids=["before-the-grant", "on-the-grant", "after-argument"],
)
def test_dates_out_of_order_are_set_aside(tmp_path: Path, briefed: date) -> None:
    with _seeded(tmp_path, [_argued(1, "24-100", merits_brief_filed=briefed)]) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert population.cases == []
    assert [e.reason for e in population.excluded] == ["dates-out-of-order"]


def test_cases_are_assigned_to_the_term_they_were_argued_in(tmp_path: Path) -> None:
    """A 24- docket argued in the autumn of 2025 is an OT2025 case."""
    rows = [
        _argued(1, "24-100"),
        _argued(
            2,
            "24-900",
            date_cert_granted=date(2025, 1, 17),
            merits_brief_filed=date(2025, 6, 11),
            merits_argued=date(2025, 10, 6),
            merits_decided=date(2026, 2, 20),
        ),
    ]
    with _seeded(tmp_path, rows) as conn:
        population = merits_backtest_population(conn, terms=[2025, 2024])

    # Listed in the order named: the Term put first heads the list.
    assert [(c.case_id, c.term) for c in population.cases] == [
        ("scotus/2", 2025),
        ("scotus/1", 2024),
    ]
    assert [t.term for t in population.terms] == [2025, 2024]


def test_an_ifp_case_is_kept_and_marked(tmp_path: Path) -> None:
    with _seeded(tmp_path, [_argued(1, "24-5438")]) as conn:
        population = merits_backtest_population(conn, terms=[2024])

    assert [c.ifp for c in population.cases] == [True]


def test_no_term_is_refused(tmp_path: Path) -> None:
    with _seeded(tmp_path, []) as conn, pytest.raises(ValueError, match="at least one"):
        merits_backtest_population(conn, terms=[])


def test_the_plan_command_writes_the_population_and_names_what_it_set_aside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    rows = [_argued(1, "24-100"), _argued(2, "24-200", merits_brief_filed=None)]
    with _seeded(tmp_path, rows):
        pass
    out = tmp_path / "population.json"

    result = runner.invoke(
        app,
        ["merits-backtest-plan", "--terms", "2024", "--out", str(out), "--corpus-backend", "local"],
    )

    assert result.exit_code == 0, result.output
    assert "OT2024: 1 case(s) to replay" in result.output
    assert "24-200: no-briefed-date" in result.output
    body = json.loads(out.read_text())
    assert [c["case_id"] for c in body["cases"]] == ["scotus/1"]
    assert [c["moment"] for c in body["cases"][0]["cutoffs"]] == [
        Moment.grant.value,
        Moment.briefed.value,
    ]


@pytest.mark.parametrize("terms", ["OT25", "25", ""])
def test_the_plan_command_refuses_a_term_that_is_not_a_year(tmp_path: Path, terms: str) -> None:
    result = runner.invoke(app, ["merits-backtest-plan", "--terms", terms])

    assert result.exit_code == 2


# --- the replay cell -----------------------------------------------------------------


def _docket(*entries: tuple[str, str]) -> dict[str, Any]:
    return {
        "CaseNumber": "24-100",
        "ProceedingsandOrder": [{"Date": day, "Text": text} for day, text in entries],
    }


_DECIDED_DOCKET = _docket(
    ("Jan 10 2024", "Petition for a writ of certiorari filed."),
    ("Jun 03 2024", "Petition GRANTED."),
    ("Sep 16 2024", "Brief of respondent Smith filed."),
    ("Dec 02 2024", "Argued. For petitioner: A. For respondent: B."),
    ("May 22 2025", "Judgment REVERSED and case REMANDED. Kagan, J., delivered the opinion."),
)


def _document(kind: str, entry_date: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="scotus/1",
        kind=kind,
        url=f"https://www.supremecourt.gov/{kind}.pdf",
        entry_date=entry_date,
        fetched_at=date(2025, 7, 1),
        text=f"The {kind} text.",
    )


@contextmanager
def _replayable(tmp_path: Path, payload: dict[str, Any]) -> Iterator[corpus.ReadConnection]:
    with _seeded(tmp_path, [_argued(1, "24-100")], {"scotus/1": payload}) as conn:
        corpus.upsert_documents(
            conn,  # type: ignore[arg-type]
            [
                _document("petition", "Jan 10 2024"),
                _document("merits-brief-petitioner", "Aug 01 2024"),
                _document("merits-brief-respondent", "Sep 16 2024"),
            ],
        )
        yield conn


def _case(conn: corpus.ReadConnection) -> MeritsReplayCase:
    [case] = merits_backtest_population(conn, terms=[2024]).cases
    return case


def _entries(cell_root: Path) -> list[str]:
    [snapshot] = (cell_root / "cases/scotus/1/record/snapshots").iterdir()
    return [e["Text"] for e in json.loads(snapshot.read_text())["ProceedingsandOrder"]]


def test_each_moment_gets_its_own_record_cut_at_its_cutoff(tmp_path: Path) -> None:
    work = tmp_path / "cells"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        case = _case(conn)
        grant, briefed = (provision_replay_cell(conn, case, cut, work) for cut in case.cutoffs)

    assert isinstance(grant, MeritsReplayCell) and isinstance(briefed, MeritsReplayCell)
    assert (grant.documents, briefed.documents) == (
        ["petition"],
        ["merits-brief-petitioner", "merits-brief-respondent", "petition"],
    )
    grant_root, briefed_root = moment_root(work, Moment.grant), moment_root(work, Moment.briefed)
    assert len(_entries(grant_root)) == 2
    assert len(_entries(briefed_root)) == 3
    for root, event_id in (
        (grant_root, "evt-order-judgment"),
        (briefed_root, "evt-brief-judgment"),
    ):
        event = yaml.safe_load((root / f"cases/scotus/1/events/{event_id}/event.yaml").read_text())
        assert event["resolved"] is False
        context = json.loads((root / "cases/scotus/1/record/context.json").read_text())
        assert (context["mode"], context["decided_before"]) == ("replay", "2024")
    assert not any("REVERSED" in text for text in _entries(briefed_root))


def test_a_replay_cell_is_never_handed_the_lower_court_kinds(tmp_path: Path) -> None:
    """The fill walks undecided cases only, so a decided case holds them by
    timing alone; a forward merits cell may read them, a replay cell may not."""
    work = tmp_path / "cells"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        corpus.upsert_documents(
            conn,  # type: ignore[arg-type]
            [
                _document("decision-below", "Jan 02 2024"),
                _document("lower-court-docket", "Jan 02 2024"),
            ],
        )
        case = _case(conn)
        grant = provision_replay_cell(conn, case, case.cutoffs[0], work)

    assert isinstance(grant, MeritsReplayCell)
    assert grant.documents == ["petition"]
    staged = moment_root(work, Moment.grant) / "cases/scotus/1/record/documents"
    assert not list(staged.glob("decision-below*")) and not list(staged.glob("lower-court*"))


def test_the_snapshots_outcome_fields_are_stripped(tmp_path: Path) -> None:
    payload = {**_DECIDED_DOCKET, "QPLink": "/qp/24-00100qp.pdf", "Petitioner": [{"Name": "A"}]}
    assert {"QPLink", "Petitioner"} <= set(SNAPSHOT_OUTCOME_FIELDS)
    work = tmp_path / "cells"
    with _replayable(tmp_path, payload) as conn:
        case = _case(conn)
        provision_replay_cell(conn, case, case.cutoffs[0], work)

    [snapshot] = (moment_root(work, Moment.grant) / "cases/scotus/1/record/snapshots").iterdir()
    kept = set(json.loads(snapshot.read_text()))
    assert "ProceedingsandOrder" in kept
    assert not kept & set(SNAPSHOT_OUTCOME_FIELDS)


def test_a_cell_whose_kept_entries_show_the_judgment_is_fenced(tmp_path: Path) -> None:
    """An undated-looking judgment entry the date cut keeps: the scan refuses the cell."""
    payload = _docket(
        ("Jun 03 2024", "Petition GRANTED."),
        ("Jun 03 2024", "Judgment REVERSED and case REMANDED."),
    )
    work = tmp_path / "cells"
    with _replayable(tmp_path, payload) as conn:
        case = _case(conn)
        fenced = provision_replay_cell(conn, case, case.cutoffs[0], work)

    assert isinstance(fenced, MeritsReplayFenced)
    assert fenced.reason == "shows-the-judgment"
    assert not (moment_root(work, Moment.grant) / "cases").exists()


def test_a_briefed_cell_without_the_respondents_brief_is_fenced(tmp_path: Path) -> None:
    work = tmp_path / "cells"
    with _seeded(tmp_path, [_argued(1, "24-100")], {"scotus/1": _DECIDED_DOCKET}) as conn:
        corpus.upsert_documents(conn, [_document("petition", "Jan 10 2024")])  # type: ignore[arg-type]
        case = _case(conn)
        fenced = provision_replay_cell(conn, case, case.cutoffs[1], work)

    assert isinstance(fenced, MeritsReplayFenced)
    assert fenced.reason == "briefs-not-staged"


def test_a_case_with_no_snapshot_is_fenced(tmp_path: Path) -> None:
    work = tmp_path / "cells"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        case = _case(conn)
        conn.execute("DELETE FROM snapshots")
        fenced = provision_replay_cell(conn, case, case.cutoffs[0], work)

    assert isinstance(fenced, MeritsReplayFenced)
    assert fenced.reason == "no-snapshot"


def test_a_snapshot_stored_before_the_cutoff_is_read_as_dated(tmp_path: Path) -> None:
    work = tmp_path / "cells"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        early = _docket(
            ("Jan 10 2024", "Petition for a writ of certiorari filed."),
            ("Jun 03 2024", "Petition GRANTED."),
        )
        corpus.upsert_snapshot(conn, "scotus/1", date(2024, 6, 3), early)  # type: ignore[arg-type]
        case = _case(conn)
        grant = provision_replay_cell(conn, case, case.cutoffs[0], work)

    assert isinstance(grant, MeritsReplayCell)
    assert (grant.provenance, grant.snapshot_date) == ("dated", date(2024, 6, 3))
    assert (grant.dropped_entries, len(_entries(moment_root(work, Moment.grant)))) == (0, 2)


def test_a_bad_document_kind_fences_the_cell_rather_than_the_sweep(tmp_path: Path) -> None:
    work = tmp_path / "cells"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        corpus.upsert_documents(conn, [_document("../escape", "Jan 10 2024")])  # type: ignore[arg-type]
        sweep = provision_replay_cells(conn, [_case(conn)], work)

    assert sweep.cells == []
    assert {fence.reason for fence in sweep.fenced} == {"bad-document-kind"}
    assert not work.exists() or not any(work.iterdir())


def test_a_sweep_pairs_only_the_cases_written_at_both_moments(tmp_path: Path) -> None:
    """A briefed fence drops that moment's cell, not the case's grant cell."""
    rows = [_argued(1, "24-100"), _argued(2, "24-200")]
    payloads: dict[str, dict[str, Any] | None] = {
        "scotus/1": _DECIDED_DOCKET,
        "scotus/2": _DECIDED_DOCKET,
    }
    work = tmp_path / "cells"
    with _seeded(tmp_path, rows, payloads) as conn:
        corpus.upsert_documents(
            conn,  # type: ignore[arg-type]
            [
                _document("petition", "Jan 10 2024"),
                _document("merits-brief-respondent", "Sep 16 2024"),
                _document("petition", "Jan 10 2024").model_copy(update={"case_id": "scotus/2"}),
            ],
        )
        cases = merits_backtest_population(conn, terms=[2024]).cases
        sweep = provision_replay_cells(conn, cases, work)

    assert sorted((cell.case_id, cell.moment) for cell in sweep.cells) == [
        ("scotus/1", Moment.briefed),
        ("scotus/1", Moment.grant),
        ("scotus/2", Moment.grant),
    ]
    [fence] = sweep.fenced
    assert (fence.case_id, fence.reason, fence.judgment, fence.disturbed) == (
        "scotus/2",
        "briefs-not-staged",
        Judgment.reversed,
        True,
    )
    assert sweep.paired == ["scotus/1"]
    assert sweep.fence_counts() == {"grant": {}, "briefed": {"briefs-not-staged": 1}}


def test_a_sweep_refuses_a_tree_that_is_not_empty(tmp_path: Path) -> None:
    work = tmp_path / "cells"
    (work / "grant").mkdir(parents=True)
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn, pytest.raises(ValueError, match="fresh"):
        provision_replay_cells(conn, [_case(conn)], work)


def test_a_stub_replay_runs_every_predictor_at_both_moments(tmp_path: Path) -> None:
    work, kept = tmp_path / "replay", tmp_path / "kept"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        case = _case(conn)
        outcome = replay_merits_predictors(
            conn,
            [case],
            config_root=Path("config"),
            work_root=work,
            run_id="20261024T000000Z",
            engine_override="stub",
            keep_root=kept,
        )

    assert outcome.unavailable == [] and outcome.lost_cells == []
    assert outcome.predictions
    for by_moment in outcome.predictions.values():
        assert set(by_moment) == set(MERITS_BACKTEST_MOMENTS)
        assert all(set(found) == {"scotus/1"} for found in by_moment.values())
    assert all(engine == "stub" for engine, _ in outcome.ran_on.values())
    # Each moment's trees leave the work root once its cells are read back.
    assert not any(work.rglob("context.json"))
    # What is kept is the forecasts alone: no record, every file allowlisted.
    assert (kept / "run-id").read_text() == "20261024T000000Z\n"
    files = {p.relative_to(kept).as_posix() for p in kept.rglob("*") if p.is_file()}
    assert not any("/record/" in f for f in files)
    names = {f.rsplit("/", 1)[-1] for f in files} - {"run-id"}
    assert names <= KEPT_FORECAST_FILES | {"event.yaml"}
    for moment in MERITS_BACKTEST_MOMENTS:
        event_dir = next((moment_root(kept / "stub", moment) / "cases/scotus/1/events").iterdir())
        assert (event_dir / "event.yaml").is_file()
        assert (
            event_dir / "predictions/claude-baseline/20261024T000000Z/prediction.json"
        ).is_file()


def test_a_keep_root_written_during_the_run_keeps_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file planted in the keep root while the cells ran is never shipped beside them."""
    work, kept = tmp_path / "replay", tmp_path / "kept"
    real = merits_backtest.kept_forecasts

    def planting(root: Path, run_id: str) -> tuple[dict[Path, bytes], list[str]]:
        (kept / "stub").mkdir(parents=True, exist_ok=True)
        (kept / "stub/notes.txt").write_text("a record copy")
        return real(root, run_id)

    monkeypatch.setattr(merits_backtest, "kept_forecasts", planting)
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        outcome = replay_merits_predictors(
            conn,
            [_case(conn)],
            config_root=Path("config"),
            work_root=work,
            run_id="20261024T000000Z",
            engine_override="stub",
            keep_root=kept,
        )

    assert not (kept / "run-id").exists()
    assert [p.name for p in kept.rglob("*") if p.is_file()] == ["notes.txt"]
    assert outcome.unkept == [f"{kept}: written during the run; nothing kept"]
    with (
        _replayable(tmp_path / "again", _DECIDED_DOCKET) as conn,
        pytest.raises(ValueError, match="not empty"),
    ):
        replay_merits_predictors(
            conn,
            [_case(conn)],
            config_root=Path("config"),
            work_root=tmp_path / "replay2",
            run_id="20261024T000000Z",
            engine_override="stub",
            keep_root=kept,
        )


def test_kept_forecasts_take_the_allowlist_and_refuse_links_and_bulk(tmp_path: Path) -> None:
    run = "20261024T000000Z"
    event = tmp_path / "cases/scotus/1/events/evt-x"
    cell = event / "predictions/p/" / run
    cell.mkdir(parents=True)
    (event / "event.yaml").write_text("id: evt-x\n")
    (cell / "prediction.json").write_text("{}")
    (cell / "reasoning.md").write_bytes(b"x" * (KEPT_FILE_MAX_BYTES + 1))
    (cell / "copy.md").write_text("a record copied under another name")
    (event / "record").mkdir()
    (event / "record/snapshot.json").write_text("{}")
    (cell / "flags.json").symlink_to(event / "record/snapshot.json")
    stale = event / "predictions/p/20250101T000000Z"
    stale.mkdir()
    (stale / "prediction.json").write_text("{}")

    kept, refused = kept_forecasts(tmp_path, run)

    assert {p.as_posix() for p in kept} == {
        "cases/scotus/1/events/evt-x/event.yaml",
        f"cases/scotus/1/events/evt-x/predictions/p/{run}/prediction.json",
    }
    assert refused == [
        f"cases/scotus/1/events/evt-x/predictions/p/{run}/flags.json",
        f"cases/scotus/1/events/evt-x/predictions/p/{run}/reasoning.md",
    ]


def test_the_backtest_command_writes_a_report_over_a_stub_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    with _replayable(tmp_path, _DECIDED_DOCKET):
        pass
    out = tmp_path / "merits-backtest.json"

    result = runner.invoke(
        app,
        [
            "merits-backtest",
            "--terms",
            "2024",
            "--engine",
            "stub",
            "--out",
            str(out),
            "--work-dir",
            str(tmp_path / "work"),
            "--corpus-backend",
            "local",
        ],
    )

    assert result.exit_code == 0, result.output
    report = MeritsBacktest.model_validate_json(out.read_text())
    assert (report.cells, report.paired_cases) == ({"grant": 1, "briefed": 1}, 1)
    assert report.dispatch is not None and report.dispatch.engine == "stub"
    assert report.entries
    for entry in report.entries:
        assert [m.events_scored for m in entry.moments] == [1, 1]
        # One pooled judgment is below the floor: scored, with no baseline.
        assert all(m.baselined == 0 and m.brier_skill is None for m in entry.moments)


def test_a_limited_draw_is_keyed_by_the_vintage_alone(tmp_path: Path) -> None:
    rows = [_argued(n, f"24-{n}00") for n in range(1, 7)]
    with _seeded(tmp_path, rows) as conn:
        cases = merits_backtest_population(conn, terms=[2024]).cases

    first = draw_cases(cases, 3, "2026-10-24")
    assert len(first) == 3
    assert draw_cases(list(reversed(cases)), 3, "2026-10-24") == first
    assert draw_cases(cases, 0, "2026-10-24") == sorted(
        cases, key=lambda c: draw_rank("2026-10-24", c.case_id)
    )


class _FailingRunner:
    """A runner whose engine fails every cell, or reports its quota spent."""

    def __init__(self, fault: Exception) -> None:
        self.fault, self.calls = fault, 0

    def run(self, request: Any) -> None:
        self.calls += 1
        raise self.fault


def _routed(monkeypatch: pytest.MonkeyPatch, runner: _FailingRunner) -> None:
    predictor = next(iter(enabled_predictors(Path("config") / "predictors.yaml")))
    monkeypatch.setattr(
        merits_backtest, "_runners_by_predictor", lambda *_args: [(predictor, runner)]
    )


def test_a_predictor_that_loses_every_cell_stays_on_the_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failing = _FailingRunner(EngineFailed("boom"))
    _routed(monkeypatch, failing)
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        case = _case(conn)
        outcome = replay_merits_predictors(
            conn, [case], config_root=Path("config"), work_root=tmp_path / "w", run_id="r"
        )
        population = merits_backtest_population(conn, terms=[2024])

    [(predictor_id, by_moment)] = outcome.predictions.items()
    assert not any(by_moment.values())
    assert sorted((loss.moment, loss.reason) for loss in outcome.lost_cells) == [
        (Moment.briefed, "engine-failed"),
        (Moment.grant, "engine-failed"),
    ]
    [entry] = score_merits_backtest(population, [], outcome).entries
    assert entry.predictor_id == predictor_id
    assert [(m.events_scored, m.lost) for m in entry.moments] == [(0, 1), (0, 1)]


def test_a_quota_spent_at_grant_is_not_spent_again_at_briefed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failing = _FailingRunner(EngineQuotaExhausted("spent"))
    _routed(monkeypatch, failing)
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        outcome = replay_merits_predictors(
            conn, [_case(conn)], config_root=Path("config"), work_root=tmp_path / "w", run_id="r"
        )

    assert failing.calls == 1
    assert sorted((loss.moment, loss.reason) for loss in outcome.lost_cells) == [
        (Moment.briefed, "quota-exhausted"),
        (Moment.grant, "quota-exhausted"),
    ]
