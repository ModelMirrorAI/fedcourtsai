"""The document back-fill run as the credential split runs it, against the pass in one job.

The split's claim is that moving the fetch into a job with no corpus changes
nothing the pass reads or writes, so the central tests here run both over the
same fixture corpus and compare the ledgers whole, and on an apply the stored
documents and floor stamps beside them. The rest pin what the writer refuses:
the plan crossed from a job that ran a parse, so every way it could depart from
what an honest parse writes for this worklist is a refusal before any write.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.handoff import HandoffRefused, read_handoff, write_handoff
from fedcourtsai.pipeline.document_backfill import (
    MODERN_LINK_TERM,
    DocumentBackfillResult,
    backfill_documents,
)
from fedcourtsai.pipeline.document_backfill_split import (
    BackfillPlan,
    BackfillReading,
    BackfillWorklist,
    PlanDocument,
    apply_backfill_plan,
    backfill_worklist,
    dry_run_ledger,
    plan_backfill_worklist,
)
from fedcourtsai.pipeline.documents import (
    KIND_APPLICATION,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_MERITS_BRIEF_PETITIONER,
    KIND_PETITION,
)
from tests.test_document_backfill import (
    _application_entry,
    _bio_entry,
    _client,
    _Clock,
    _document,
    _grant_entry,
    _granted_row,
    _merits_entry,
    _payload,
    _pdf,
    _petition_entry,
    _row,
    _seeded,
)

runner = CliRunner()

_TODAY = date(2026, 9, 1)
_CAP = 100_000
_COURT = "https://www.supremecourt.gov"
_LEGACY = f"{MODERN_LINK_TERM - 2000 - 3}-50"
_MODERN = f"{MODERN_LINK_TERM - 2000 + 1}-50"


def _mixed(root: Path) -> tuple[Path, dict[str, dict[str, Any]], dict[str, bytes], frozenset[str]]:
    """A corpus and an upstream holding every shape the pass reads.

    A recovered petition with its opposition, a recovered application, a
    petition selected and not served beside an opposition that was, a paper
    filing, a legacy docket, a modern docket the selector cannot read, a docket
    upstream serves nothing for, one it fails transport-side on, a recovered
    merits candidate, an unaddressable row and a standing floor.
    """
    rows = [
        _row("scotus/1", "25-100"),
        _row("scotus/2", "26A203"),
        _row("scotus/3", "25-102"),
        _row("scotus/4", "25-103"),
        _row("scotus/5", _LEGACY),
        _row("scotus/6", _MODERN),
        _row("scotus/7", "25-104"),
        _row("scotus/8", "25-105"),
        _granted_row("scotus/9", "25-106"),
        _row("scotus/10", "A-9999"),
        _row("scotus/11", "25-107", document_floor_probed_at=date(2026, 6, 3)),
    ]
    documents = [_document("scotus/9", KIND_PETITION, url=f"{_COURT}/9-pet.pdf")]
    dockets: dict[str, dict[str, Any]] = {
        "25-100": _payload(
            _petition_entry(url=f"{_COURT}/1-pet.pdf"), _bio_entry(f"{_COURT}/1-bio.pdf")
        ),
        "26A203": _payload(_application_entry()),
        "25-102": _payload(
            _petition_entry(url=f"{_COURT}/3-pet.pdf"), _bio_entry(f"{_COURT}/3-bio.pdf")
        ),
        "25-103": _payload(_petition_entry(url=None)),
        _LEGACY: _payload(),
        _MODERN: _payload(),
        "25-106": _payload(
            _petition_entry(url=f"{_COURT}/9-pet.pdf"),
            _grant_entry(),
            _merits_entry("Brief of petitioner Floyd Johnson filed.", f"{_COURT}/9-mp.pdf"),
            _merits_entry(
                "Brief of respondent United States filed.",
                f"{_COURT}/9-mr.pdf",
                date_="Jul 13 2026",
            ),
        ),
        "25-107": _payload(_petition_entry(url=f"{_COURT}/11-pet.pdf")),
    }
    pdfs = {
        f"{_COURT}/1-pet.pdf": _pdf("QUESTION PRESENTED Whether the statute applies. PARTIES"),
        f"{_COURT}/1-bio.pdf": _pdf("Respondent opposes."),
        f"{_COURT}/app.pdf": _pdf("Applicant seeks a stay of the mandate."),
        f"{_COURT}/3-bio.pdf": _pdf("Respondent opposes too."),
        f"{_COURT}/9-mp.pdf": _pdf("Petitioner says reverse."),
        f"{_COURT}/9-mr.pdf": _pdf("Respondent says affirm."),
    }
    with _seeded(root, rows, documents):
        pass
    return corpus.corpus_db_path(root), dockets, pdfs, frozenset({"25-105"})


def _in_one_job(root: Path, *, apply: bool, max_cases: int | None) -> DocumentBackfillResult:
    db, dockets, pdfs, errors = _mixed(root)
    with corpus.connect(db) as conn, _client(dockets, pdfs=pdfs, errors=errors) as client:
        result = backfill_documents(
            conn,
            client=client,
            apply=apply,
            char_cap=_CAP,
            today=_TODAY,
            max_cases=max_cases,
        )
        conn.commit()
    return result


def _worklist(db: Path, bound: int | None) -> BackfillWorklist:
    with corpus.connect(db) as conn:
        worklist, _ = backfill_worklist(conn, bound=bound)
    return worklist


def _split(root: Path, *, apply: bool, max_cases: int | None) -> DocumentBackfillResult:
    db, dockets, pdfs, errors = _mixed(root)
    worklist = _worklist(db, max_cases)
    with _client(dockets, pdfs=pdfs, errors=errors) as client:
        if not apply:
            return dry_run_ledger(client, worklist, char_cap=_CAP, today=_TODAY)
        plan = plan_backfill_worklist(client, worklist, char_cap=_CAP, today=_TODAY)
    with corpus.connect(db) as conn:
        result = apply_backfill_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY)
        conn.commit()
    return result


def _state(root: Path) -> tuple[dict[str, list[corpus.CaseDocument]], dict[str, date | None]]:
    db = corpus.corpus_db_path(root)
    with corpus.connect(db) as conn:
        rows = list(corpus.iter_rows(conn, court="scotus"))
        documents = {row.case_id: corpus.documents_for_case(conn, row.case_id) for row in rows}
        stamps = {row.case_id: row.document_floor_probed_at for row in rows}
    return documents, stamps


@pytest.mark.parametrize(("apply", "max_cases"), [(False, None), (False, 4), (True, 20), (True, 4)])
def test_the_split_reads_and_writes_as_the_pass_in_one_job(
    tmp_path: Path, apply: bool, max_cases: int | None
) -> None:
    one = _in_one_job(tmp_path / "one", apply=apply, max_cases=max_cases)
    split = _split(tmp_path / "split", apply=apply, max_cases=max_cases)
    assert split.model_dump() == one.model_dump()
    assert _state(tmp_path / "split") == _state(tmp_path / "one")


def test_the_mixed_fixture_reaches_every_shape(tmp_path: Path) -> None:
    result = _split(tmp_path, apply=True, max_cases=20)
    assert result.candidates == 9 and result.unaddressable == 1 and result.standing_floors == 1
    assert result.recovered == 3 and result.floors_stamped == 2
    assert result.documents["scotus/3"] == [KIND_BRIEF_IN_OPPOSITION]
    assert result.no_link == 1 and result.no_entry == 2
    assert result.no_entry_modern_cases == ["scotus/6"]
    assert result.docket_unserved == 1 and result.docket_errors == 1
    assert result.fetch_losses["unavailable"] == 1
    assert result.remaining == 4 and result.left_class == 0


def test_the_projection_carries_public_facts_and_the_class_ledger(tmp_path: Path) -> None:
    db, _dockets, _pdfs, _errors = _mixed(tmp_path)
    with corpus.connect(db) as conn:
        worklist, reading = backfill_worklist(conn, bound=2)
    # Class order is case-id order, past the unaddressable row and the standing floor.
    assert [item.case_id for item in worklist.items] == ["scotus/1", "scotus/2"]
    assert set(worklist.items[0].model_dump()) == {
        "case_id",
        "kinds",
        "term",
        "serial",
        "form",
        "term_year",
        "stored_urls",
    }
    assert worklist.bound == 2 and worklist.candidates == reading.candidates == 9
    assert reading.attempted == 0 and reading.remaining == 9 and not reading.applied


def test_the_parse_deadline_leaves_the_tail_unreached_as_the_pass_does(tmp_path: Path) -> None:
    db, dockets, pdfs, errors = _mixed(tmp_path)
    worklist = _worklist(db, 3)
    clock = _Clock()

    def monotonic() -> float:
        clock.advance(70.0)
        return clock()

    with _client(dockets, pdfs=pdfs, errors=errors) as client:
        plan = plan_backfill_worklist(
            client, worklist, char_cap=_CAP, today=_TODAY, deadline=200.0, monotonic=monotonic
        )
    assert [reading.case_id for reading in plan.readings] == ["scotus/1"]
    assert plan.unreached == ["scotus/2", "scotus/3"]
    with corpus.connect(db) as conn:
        result = apply_backfill_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY)
    assert result.attempted == 1 and result.unreached == ["scotus/2", "scotus/3"]


def test_the_parse_ends_its_slice_before_its_plan_outgrows_the_byte_budget(
    tmp_path: Path,
) -> None:
    db, dockets, pdfs, errors = _mixed(tmp_path)
    worklist = _worklist(db, 3)
    with _client(dockets, pdfs=pdfs, errors=errors) as client:
        whole = plan_backfill_worklist(client, worklist, char_cap=_CAP, today=_TODAY)
        first = len(whole.readings[0].model_dump_json().encode())
        plan = plan_backfill_worklist(
            client, worklist, char_cap=_CAP, today=_TODAY, byte_budget=first
        )
    assert [reading.case_id for reading in plan.readings] == ["scotus/1"]
    assert plan.unreached == ["scotus/2", "scotus/3"]
    # The discarded reading's losses are not the plan's.
    assert whole.fetch_losses["unavailable"] == 1
    assert not any(plan.fetch_losses.values())


def test_a_reading_whose_candidate_left_the_class_is_not_written(tmp_path: Path) -> None:
    db, dockets, pdfs, errors = _mixed(tmp_path)
    worklist = _worklist(db, 1)
    with _client(dockets, pdfs=pdfs, errors=errors) as client:
        plan = plan_backfill_worklist(client, worklist, char_cap=_CAP, today=_TODAY)
    stored = _document("scotus/1", KIND_PETITION, url=f"{_COURT}/other.pdf")
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, [stored])
        result = apply_backfill_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY)
        kept = {d.kind: d for d in corpus.documents_for_case(conn, "scotus/1")}
    assert result.left_class == 1 and result.recovered == 0 and not result.documents
    assert kept == {KIND_PETITION: stored}


def test_a_reading_whose_gap_changed_since_the_projection_is_not_written(
    tmp_path: Path,
) -> None:
    db, dockets, pdfs, errors = _mixed(tmp_path)
    worklist = _worklist(db, None)
    assert "scotus/9" in [item.case_id for item in worklist.items]
    with _client(dockets, pdfs=pdfs, errors=errors) as client:
        plan = plan_backfill_worklist(client, worklist, char_cap=_CAP, today=_TODAY)
    # The live channel stores one of the two missing merits briefs in between:
    # the case is still in the class, missing one kind rather than two.
    stored = _document("scotus/9", KIND_MERITS_BRIEF_PETITIONER, url=f"{_COURT}/9-mp.pdf")
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, [stored])
        result = apply_backfill_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY)
        kept = {d.kind: d for d in corpus.documents_for_case(conn, "scotus/9")}
    assert result.left_class == 1
    assert kept[KIND_MERITS_BRIEF_PETITIONER] == stored
    assert set(kept) == {KIND_PETITION, KIND_MERITS_BRIEF_PETITIONER}


# --- what the writer refuses -------------------------------------------------


def _planned(tmp_path: Path) -> tuple[Path, BackfillWorklist, BackfillPlan]:
    db, dockets, pdfs, errors = _mixed(tmp_path)
    worklist = _worklist(db, 6)
    with _client(dockets, pdfs=pdfs, errors=errors) as client:
        plan = plan_backfill_worklist(client, worklist, char_cap=_CAP, today=_TODAY)
    assert [reading.case_id for reading in plan.readings] == [
        "scotus/1",
        "scotus/2",
        "scotus/3",
        "scotus/4",
        "scotus/5",
        "scotus/6",
    ]
    return db, worklist, plan


def _refused(db: Path, plan: BackfillPlan, worklist: BackfillWorklist, match: str) -> None:
    with corpus.connect(db) as conn, pytest.raises(HandoffRefused, match=match):
        apply_backfill_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY)


def _with(plan: BackfillPlan, index: int, **update: Any) -> BackfillPlan:
    readings = list(plan.readings)
    readings[index] = readings[index].model_copy(update=update)
    return plan.model_copy(update={"readings": readings})


def test_the_writer_refuses_a_plan_that_drops_repeats_or_strays(tmp_path: Path) -> None:
    db, worklist, plan = _planned(tmp_path)
    dropped = plan.model_copy(update={"readings": plan.readings[1:]})
    _refused(db, dropped, worklist, "accounts for 5 of the worklist's 6 items")
    twice = plan.model_copy(update={"unreached": ["scotus/6"]})
    _refused(db, twice, worklist, "names scotus/6 twice")
    stray = _with(plan, 0, case_id="scotus/99")
    _refused(db, stray, worklist, "not on this worklist")


def test_the_writer_refuses_unreached_items_off_the_worklist_tail(tmp_path: Path) -> None:
    db, worklist, plan = _planned(tmp_path)
    ahead = plan.model_copy(update={"readings": plan.readings[1:], "unreached": ["scotus/1"]})
    _refused(db, ahead, worklist, "not the worklist's tail")


def test_the_writer_refuses_a_reading_no_parse_could_make(tmp_path: Path) -> None:
    db, worklist, plan = _planned(tmp_path)
    _refused(db, _with(plan, 0, loss="docket-error"), worklist, "more than one shape")
    _refused(db, _with(plan, 3, alarmed=True, floor=None), worklist, "no floor can carry")
    # scotus/5 is the legacy docket: no alarm can fire below the modern Term.
    _refused(db, _with(plan, 4, alarmed=True), worklist, "no floor can carry")


def test_the_writer_refuses_a_document_off_its_reading(tmp_path: Path) -> None:
    db, worklist, plan = _planned(tmp_path)
    first = plan.readings[0].documents[0]
    other = first.model_copy(update={"case_id": "scotus/2"})
    _refused(db, _with(plan, 0, documents=[other]), worklist, "another case")
    _refused(db, _with(plan, 0, documents=[first, first]), worklist, "names .* twice")
    long = first.model_copy(update={"text": "x" * (_CAP + 1)})
    _refused(db, _with(plan, 0, documents=[long]), worklist, "document cap")


def test_the_writer_refuses_losses_under_another_reason(tmp_path: Path) -> None:
    db, worklist, plan = _planned(tmp_path)
    forged = plan.model_copy(update={"fetch_losses": {**plan.fetch_losses, "forged": 1}})
    _refused(db, forged, worklist, "fetch's own reasons")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("url", "https://example.com/pet.pdf"),
        ("url", "file:///etc/passwd"),
        ("kind", "not-a-kind"),
        ("case_id", "scotus/1\n::error::forged"),
    ],
)
def test_a_malformed_document_is_refused_on_read(tmp_path: Path, field: str, value: str) -> None:
    _db, _worklist, plan = _planned(tmp_path)
    body = plan.model_dump(mode="json")
    body["readings"][0]["documents"][0][field] = value
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(body))
    with pytest.raises(HandoffRefused):
        read_handoff(path, BackfillPlan)


def test_a_plan_file_round_trips(tmp_path: Path) -> None:
    _db, _wl, plan = _planned(tmp_path)
    path = tmp_path / "plan.json"
    write_handoff(path, plan)
    assert read_handoff(path, BackfillPlan) == plan
    assert isinstance(plan.readings[0], BackfillReading)
    assert isinstance(plan.readings[0].documents[0], PlanDocument)
    assert {document.kind for document in plan.readings[1].documents} == {KIND_APPLICATION}


# --- the command, as the workflow runs it -----------------------------------


def _patch_client(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    _db, dockets, pdfs, errors = _mixed(root / "upstream")

    def client(**_kwargs: object) -> Any:
        return _client(dockets, pdfs=pdfs, errors=errors)

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", client)


def _last_json(output: str) -> dict[str, Any]:
    return dict(json.loads(output.strip().splitlines()[-1]))


def test_the_cli_split_round_trips_as_the_workflow_runs_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _mixed(tmp_path / "corpus")
    _patch_client(monkeypatch, tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    worklist = tmp_path / "handoff" / "projection.json"
    plan = tmp_path / "handoff" / "plan.json"
    command = ["backfill-documents"]

    emitted = runner.invoke(app, [*command, "--emit-worklist", str(worklist), "--max-cases", "4"])
    assert emitted.exit_code == 0, emitted.output
    assert "backfill-documents (projection): 9 addressable candidate(s)" in emitted.output
    assert "worklist: 4 item(s), the apply's slice" in emitted.output

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    dry = runner.invoke(app, [*command, "--worklist", str(worklist)])
    assert dry.exit_code == 0, dry.output
    assert _last_json(dry.output)["selected"] == {
        "scotus/1": [KIND_PETITION],
        "scotus/2": [KIND_APPLICATION],
        "scotus/3": [KIND_PETITION],
    }
    parsed = runner.invoke(app, [*command, "--worklist", str(worklist), "--plan-out", str(plan)])
    assert parsed.exit_code == 0, parsed.output
    assert "fetched for 3; floors 1; docket losses 0; unreached 0" in parsed.output
    assert "Respondent opposes" not in parsed.output

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    writer = [*command, "--from-plan", str(plan), "--bind-worklist", str(worklist), "--apply"]
    refused = runner.invoke(app, [*writer, "--max-cases", "5"])
    assert refused.exit_code == 1
    assert "cut for a bound of 4, not this dispatch's 5" in refused.output

    applied = runner.invoke(app, [*writer, "--max-cases", "4"])
    assert applied.exit_code == 0, applied.output
    ledger = _last_json(applied.output)
    assert ledger["recovered"] == 2 and ledger["floors_stamped"] == 1
    witness = runner.invoke(app, [*command, "--max-cases", "0"])
    assert _last_json(witness.output)["candidates"] == ledger["remaining"]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--plan-out", "p.json"], "the parse takes --worklist"),
        (["--worklist", "w.json", "--apply"], "opens no corpus"),
        (["--worklist", "w.json", "--max-cases", "1"], "opens no corpus"),
        (["--worklist", "w.json", "--from-plan", "p.json"], "opens no corpus"),
        (["--emit-worklist", "w.json", "--from-plan", "p.json"], "pass one"),
        (["--from-plan", "p.json"], "go together"),
        (["--emit-worklist", "w.json", "--deadline-seconds", "60"], "bounds the parse"),
        (["--emit-worklist", "w.json", "--max-cases", "0"], "hands the parse nothing"),
        (["--emit-worklist", "w.json", "--apply"], "the projection writes nothing"),
        (["--from-plan", "p.json", "--bind-worklist", "w.json", "--apply"], "explicit --max-cases"),
        (["--from-plan", "p.json", "--bind-worklist", "w.json", "--max-cases", "1"], "--apply"),
    ],
)
def test_the_cli_refuses_a_mode_it_cannot_tell_apart(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, argv: list[str], message: str
) -> None:
    _mixed(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["backfill-documents", *argv])
    assert result.exit_code == 2, result.output
    assert message in result.output
    assert not (tmp_path / "w.json").exists()
