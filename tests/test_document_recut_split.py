"""The re-cut pass split at the credential boundary: projection, parse, reader.

The split must read exactly as the pass in one job does, so the central tests
run both over the same corpus and the same served bytes and compare the
ledgers whole. The rest pin what each side refuses: the parse's plan crosses
from a job that ran a parser, and the reader takes it as untrusted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.handoff import HandoffRefused, read_handoff, write_handoff
from fedcourtsai.pipeline import document_recut
from fedcourtsai.pipeline.document_recut import (
    LEFT_THE_CLASS,
    SCOPE_ALL_LIVE,
    SCOPE_PREDICT_RELEVANT,
    UNCHANGED,
    DocumentRecutResult,
    recut_documents,
)
from fedcourtsai.pipeline.document_recut_split import (
    RecutPlan,
    RecutPlanRow,
    RecutWorklist,
    apply_recut_plan,
    plan_recut_worklist,
    recut_worklist,
)
from fedcourtsai.pipeline.documents import KIND_APPENDIX, KIND_PETITION, ExtractedText
from tests.test_document_recut import (
    _CAP,
    _QUESTION,
    _TODAY,
    _head_cut,
    _pages,
    _patch_client,
    _seed,
    _small_cap,
)
from tests.test_documents import _pdf_pages
from tests.test_ocr_recovery import _client, _documents

runner = CliRunner()


def _mixed(root: Path) -> tuple[Path, dict[str, bytes], dict[str, int]]:
    """A class whose slice reaches every outcome the served PDF or the stored text decides."""
    pdf = _pdf_pages(_pages(6))
    rows = {
        "recut": _head_cut("scotus/1", pdf),
        "appendix": _head_cut("scotus/1", pdf, kind=KIND_APPENDIX),
        "pages": _head_cut("scotus/2", pdf),
        "head": _head_cut("scotus/3", pdf),
        "unreadable": _head_cut("scotus/4", pdf),
        "empty": _head_cut("scotus/5", pdf),
        "forbidden": _head_cut("scotus/6", pdf),
        "unserved": _head_cut("scotus/7", pdf),
        "beyond": _head_cut("scotus/8", pdf),
    }
    served = {
        rows["recut"].url: pdf,
        rows["appendix"].url: pdf,
        rows["pages"].url: _pdf_pages(_pages(9)),
        rows["head"].url: _pdf_pages(_pages(6, front="CORRECTED PETITION " + _QUESTION)),
        rows["unreadable"].url: b"%PDF-1.7 truncated",
        rows["empty"].url: _pdf_pages([""] * rows["empty"].pages),
        rows["beyond"].url: pdf,
    }
    db = _seed(root, list(rows.values()))
    return db, served, {rows["forbidden"].url: 403}


def _in_one_job(
    db: Path,
    served: dict[str, bytes],
    status: dict[str, int],
    *,
    apply: bool,
    max_cases: int | None,
    scope: str = SCOPE_PREDICT_RELEVANT,
) -> DocumentRecutResult:
    with corpus.connect(db) as conn, _client(served, status=status) as client:
        return recut_documents(
            conn,
            client=client,
            apply=apply,
            char_cap=_CAP,
            today=_TODAY,
            max_cases=max_cases,
            scope=scope,
        )


def _split(
    db: Path,
    served: dict[str, bytes],
    status: dict[str, int],
    *,
    apply: bool,
    max_cases: int | None,
    scope: str = SCOPE_PREDICT_RELEVANT,
) -> DocumentRecutResult:
    with corpus.connect(db) as conn:
        worklist, _reading = recut_worklist(conn, scope=scope, bound=max_cases)
    with _client(served, status=status) as client:
        plan = plan_recut_worklist(client, worklist, char_cap=_CAP)
    with corpus.connect(db) as conn:
        return apply_recut_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY, apply=apply)


@pytest.mark.parametrize(("apply", "max_cases"), [(False, None), (False, 8), (True, 8)])
def test_the_split_reads_and_writes_as_the_pass_in_one_job(
    tmp_path: Path, apply: bool, max_cases: int | None
) -> None:
    one_db, served, status = _mixed(tmp_path / "one")
    split_db, _served, _status = _mixed(tmp_path / "split")
    one = _in_one_job(one_db, served, status, apply=apply, max_cases=max_cases)
    split = _split(split_db, served, status, apply=apply, max_cases=max_cases)
    assert split.model_dump() == one.model_dump()
    # The ninth candidate is the one a bound of eight leaves out.
    assert one.recut == (3 if max_cases is None else 2)
    assert one.pages_changed == 1 and one.head_changed == 1
    assert one.unreadable == 1 and one.empty_after_recut == 1
    assert one.fetch_failed == {"http-403": 1, "not-served": 1}
    for case_id in (f"scotus/{n}" for n in range(1, 9)):
        assert _documents(split_db, case_id) == _documents(one_db, case_id)
    if apply:
        assert "[pipeline note:" in _documents(split_db, "scotus/1")[KIND_PETITION].text
        assert one.remaining == one.candidates - 2


def test_the_split_reads_an_unchanged_recut_as_the_pass_does(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    one_db = _seed(tmp_path / "one", [stored])
    split_db = _seed(tmp_path / "split", [stored])
    monkeypatch.setattr(
        document_recut,
        "extract_filing_text",
        lambda _data, *, kind, char_cap: ExtractedText(
            text=stored.text, pages=stored.pages, truncated=True
        ),
    )
    one = _in_one_job(one_db, {stored.url: pdf}, {}, apply=True, max_cases=1)
    split = _split(split_db, {stored.url: pdf}, {}, apply=True, max_cases=1)
    assert split.model_dump() == one.model_dump()
    assert split.skipped == {"scotus/1 petition": UNCHANGED}


def test_the_parse_deadline_leaves_the_tail_unreached_as_the_pass_does(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    rows = [_head_cut(f"scotus/{n}", pdf) for n in (1, 2, 3)]
    db = _seed(tmp_path / "corpus", rows)
    clock = [0.0]

    def monotonic() -> float:
        clock[0] += 60.0
        return clock[0]

    with corpus.connect(db) as conn:
        worklist, _ = recut_worklist(conn, scope=SCOPE_PREDICT_RELEVANT, bound=3)
    with _client({row.url: pdf for row in rows}) as client:
        plan = plan_recut_worklist(
            client, worklist, char_cap=_CAP, deadline=100.0, monotonic=monotonic
        )
    assert plan.unreached == ["scotus/2 petition", "scotus/3 petition"]
    with corpus.connect(db) as conn:
        result = apply_recut_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY, apply=True)
    assert result.attempted == 1 and result.recut == 1
    assert result.outcomes_by_kind == {KIND_PETITION: {"recut": 1, "unreached": 2}}
    assert result.remaining == 2


def test_the_worklist_carries_public_facts_and_the_class_ledger(tmp_path: Path) -> None:
    db, _served, _status = _mixed(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        bounded, reading = recut_worklist(conn, scope=SCOPE_ALL_LIVE, bound=2)
        whole, _ = recut_worklist(conn, scope=SCOPE_PREDICT_RELEVANT, bound=None)
    assert [item.key for item in bounded.items] == ["scotus/1 petition", "scotus/1 appendix"]
    assert bounded.scope == SCOPE_ALL_LIVE and bounded.bound == 2
    assert set(bounded.items[0].model_dump()) == {"case_id", "kind", "url", "pages"}
    assert len(whole.items) == reading.candidates == 9
    assert reading.attempted == 0 and reading.remaining == 9 and not reading.applied


def test_a_row_that_left_the_class_is_not_written(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    db = _seed(tmp_path / "corpus", [stored])
    with corpus.connect(db) as conn:
        worklist, _ = recut_worklist(conn, scope=SCOPE_PREDICT_RELEVANT, bound=1)
    with _client({stored.url: pdf}) as client:
        plan = plan_recut_worklist(client, worklist, char_cap=_CAP)
    # The fetching lanes stored the filing whole since the projection read it.
    whole = stored.model_copy(update={"truncated": False})
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, [whole])
        result = apply_recut_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY, apply=True)
    assert result.skipped == {"scotus/1 petition": LEFT_THE_CLASS}
    assert result.outcomes_by_kind == {KIND_PETITION: {LEFT_THE_CLASS: 1}}
    assert result.recut == 0 and result.candidates == 0 and result.remaining == 0
    assert _documents(db, "scotus/1")[KIND_PETITION] == whole


# --- what the reader refuses ------------------------------------------------


def _one_item(tmp_path: Path) -> tuple[Path, RecutWorklist, RecutPlan]:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    second = _head_cut("scotus/2", pdf)
    db = _seed(tmp_path / "corpus", [stored, second])
    with corpus.connect(db) as conn:
        worklist, _ = recut_worklist(conn, scope=SCOPE_PREDICT_RELEVANT, bound=2)
    with _client({stored.url: pdf, second.url: pdf}) as client:
        plan = plan_recut_worklist(client, worklist, char_cap=_CAP)
    assert len(plan.rows) == 2
    return db, worklist, plan


def _refused(db: Path, plan: RecutPlan, worklist: RecutWorklist, match: str) -> None:
    with corpus.connect(db) as conn, pytest.raises(HandoffRefused, match=match):
        apply_recut_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY, apply=True)


def test_the_reader_refuses_a_plan_that_drops_or_repeats_an_item(tmp_path: Path) -> None:
    db, worklist, plan = _one_item(tmp_path)
    dropped = plan.model_copy(update={"rows": plan.rows[:1]})
    _refused(db, dropped, worklist, "accounts for 1 of the worklist's 2 items")
    twice = plan.model_copy(update={"skips": {"scotus/1 petition": "unreadable"}})
    _refused(db, twice, worklist, "names scotus/1 petition twice")


def test_the_reader_refuses_a_row_off_its_item(tmp_path: Path) -> None:
    db, worklist, plan = _one_item(tmp_path)
    first, second = plan.rows
    moved = first.model_copy(update={"pages": first.pages + 1})
    _refused(db, plan.model_copy(update={"rows": [moved, second]}), worklist, "page count")
    elsewhere = first.model_copy(update={"url": "https://www.supremecourt.gov/other.pdf"})
    _refused(db, plan.model_copy(update={"rows": [elsewhere, second]}), worklist, "at its URL")
    long = first.model_copy(update={"text": "x" * (_CAP + 1)})
    _refused(db, plan.model_copy(update={"rows": [long, second]}), worklist, "document cap")
    stray = RecutPlanRow(**{**first.model_dump(), "case_id": "scotus/9"})
    _refused(db, plan.model_copy(update={"rows": [stray, second]}), worklist, "not on this")


def test_the_reader_refuses_a_page_skip_naming_another_stored_count(tmp_path: Path) -> None:
    db, worklist, plan = _one_item(tmp_path)
    forged = plan.model_copy(
        update={
            "rows": plan.rows[1:],
            "skips": {"scotus/1 petition": "pages-changed (stored 99, served 100)"},
        }
    )
    _refused(db, forged, worklist, "its stored page count beside another")
    pages = worklist.items[0].pages
    same = forged.model_copy(
        update={"skips": {"scotus/1 petition": f"pages-changed (stored {pages}, served {pages})"}}
    )
    _refused(db, same, worklist, "its stored page count beside another")


def test_the_reader_refuses_unreached_items_off_the_worklist_tail(tmp_path: Path) -> None:
    db, worklist, plan = _one_item(tmp_path)
    ahead = plan.model_copy(update={"rows": plan.rows[1:], "unreached": ["scotus/1 petition"]})
    _refused(db, ahead, worklist, "not the worklist's tail")


def test_the_parse_ends_its_slice_before_its_rows_outgrow_the_byte_budget(
    tmp_path: Path,
) -> None:
    pdf = _pdf_pages(_pages())
    rows = [_head_cut(f"scotus/{n}", pdf) for n in (1, 2, 3)]
    db = _seed(tmp_path / "corpus", rows)
    with corpus.connect(db) as conn:
        worklist, _ = recut_worklist(conn, scope=SCOPE_PREDICT_RELEVANT, bound=3)
    with _client({row.url: pdf for row in rows}) as client:
        plan = plan_recut_worklist(client, worklist, char_cap=_CAP, byte_budget=6 * _CAP + 4096 + 1)
    assert [row.key for row in plan.rows] == ["scotus/1 petition"]
    assert plan.unreached == ["scotus/2 petition", "scotus/3 petition"]
    with corpus.connect(db) as conn:
        result = apply_recut_plan(conn, plan, worklist, char_cap=_CAP, today=_TODAY, apply=False)
    assert result.outcomes_by_kind == {KIND_PETITION: {"recut": 1, "unreached": 2}}


@pytest.mark.parametrize(
    "skip",
    [
        "something-else",
        "unreadable (## John Doe)",
        "fetch-failed (anything)",
        "pages-changed (stored 7, served 8)\n## forged",
        "head-changed",
        "recut",
    ],
)
def test_a_skip_outside_the_parse_outcomes_is_refused_on_read(tmp_path: Path, skip: str) -> None:
    """The parse settles only what the served PDF shows: the rest is the reader's to judge."""
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"rows": [], "skips": {"scotus/1 petition": skip}}))
    with pytest.raises(HandoffRefused, match="not a valid RecutPlan"):
        read_handoff(path, RecutPlan)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("case_id", "scotus/1\n## forged"),
        ("kind", "brief-in-opposition"),
        ("url", "https://example.com/a.pdf"),
        ("pages", "7"),
    ],
)
def test_a_malformed_item_is_refused_on_read(tmp_path: Path, field: str, value: str) -> None:
    item = {
        "case_id": "scotus/1",
        "kind": "petition",
        "url": "https://www.supremecourt.gov/1-petition.pdf",
        "pages": 7,
    }
    path = tmp_path / "worklist.json"
    path.write_text(
        json.dumps({"scope": "predict-relevant", "bound": 1, "items": [{**item, field: value}]})
    )
    with pytest.raises(HandoffRefused, match="not a valid RecutWorklist"):
        read_handoff(path, RecutWorklist)


# --- the CLI, as run-repair's jobs run it -----------------------------------


def _small_split_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the split's parse and reader at this file's cap rather than the configured one."""
    real_plan, real_apply = plan_recut_worklist, apply_recut_plan

    def plan(*args: object, **kwargs: object) -> RecutPlan:
        kwargs["char_cap"] = _CAP
        return real_plan(*args, **kwargs)  # type: ignore[arg-type]

    def judge(*args: object, **kwargs: object) -> DocumentRecutResult:
        kwargs["char_cap"] = _CAP
        return real_apply(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr("fedcourtsai.cli.plan_recut_worklist", plan)
    monkeypatch.setattr("fedcourtsai.cli.apply_recut_plan", judge)


def _last_json(output: str) -> dict[str, object]:
    return dict(json.loads(output.strip().splitlines()[-1]))


def test_the_cli_split_round_trips_as_the_workflow_runs_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    other = _head_cut("scotus/2", pdf)
    db = _seed(tmp_path / "corpus", [stored, other])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    _small_cap(monkeypatch)
    _small_split_cap(monkeypatch)
    worklist = tmp_path / "handoff" / "projection.json"
    plan = tmp_path / "handoff" / "plan.json"

    _patch_client(monkeypatch, {})
    emitted = runner.invoke(
        app, ["recut-documents", "--emit-worklist", str(worklist), "--max-cases", "1"]
    )
    assert emitted.exit_code == 0, emitted.output
    assert "recut-documents (projection, predict-relevant): 2 head-cut filing(s)" in emitted.output
    assert "worklist: 1 item(s), the apply's slice" in emitted.output

    _patch_client(monkeypatch, {stored.url: pdf})
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    parsed = runner.invoke(
        app, ["recut-documents", "--worklist", str(worklist), "--plan-out", str(plan)]
    )
    assert parsed.exit_code == 0, parsed.output
    assert "re-cut 1 for the reader to judge" in parsed.output
    assert stored.text[:40] not in parsed.output

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    reader = ["recut-documents", "--from-plan", str(plan), "--bind-worklist", str(worklist)]
    read = runner.invoke(app, [*reader, "--max-cases", "1"])
    assert read.exit_code == 0, read.output
    assert "would re-cut 1, 2 left in the class" in read.output
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored

    refused = runner.invoke(app, [*reader, "--max-cases", "2", "--apply"])
    assert refused.exit_code == 1
    assert "cut for a bound of 1, not this dispatch's 2" in refused.output
    wide = runner.invoke(app, [*reader, "--max-cases", "1", "--all-live", "--apply"])
    assert wide.exit_code == 2
    assert "takes no --all-live" in wide.output

    applied = runner.invoke(app, [*reader, "--max-cases", "1", "--apply"])
    assert applied.exit_code == 0, applied.output
    ledger = _last_json(applied.output)
    assert ledger["recut"] == 1 and ledger["remaining"] == 1
    witness = runner.invoke(app, ["recut-documents", "--max-cases", "0"])
    assert _last_json(witness.output)["candidates"] == ledger["remaining"]
    assert "[pipeline note:" in _documents(db, "scotus/1")[KIND_PETITION].text


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--worklist", "w.json"], "--worklist and --plan-out together"),
        (["--worklist", "w.json", "--plan-out", "p.json", "--apply"], "opens no corpus"),
        (["--worklist", "w.json", "--plan-out", "p.json", "--max-cases", "1"], "opens no corpus"),
        (["--worklist", "w.json", "--plan-out", "p.json", "--all-live"], "opens no corpus"),
        (["--emit-worklist", "w.json", "--from-plan", "p.json"], "pass one"),
        (["--from-plan", "p.json"], "go together"),
        (["--emit-worklist", "w.json", "--deadline-seconds", "60"], "bounds the parse"),
        (["--emit-worklist", "w.json", "--max-cases", "0"], "hands the parse nothing"),
        (["--emit-worklist", "w.json", "--apply"], "the projection writes nothing"),
        (["--from-plan", "p.json", "--bind-worklist", "w.json", "--apply"], "explicit --max-cases"),
    ],
)
def test_the_cli_refuses_a_mode_it_cannot_tell_apart(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, argv: list[str], message: str
) -> None:
    _seed(tmp_path / "corpus", [_head_cut("scotus/1", _pdf_pages(_pages()))])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["recut-documents", *argv])
    assert result.exit_code == 2, result.output
    assert message in result.output
    assert not (tmp_path / "w.json").exists()


def test_a_plan_file_round_trips(tmp_path: Path) -> None:
    _db, _worklist, plan = _one_item(tmp_path)
    path = tmp_path / "plan.json"
    write_handoff(path, plan)
    assert read_handoff(path, RecutPlan) == plan
    assert read_handoff(tmp_path / "plan.json", RecutPlan).rows[0].key == "scotus/1 petition"
