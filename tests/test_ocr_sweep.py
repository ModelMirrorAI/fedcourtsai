"""The standing OCR sweep: its order, its slice, and the three-file split.

The order and the slice are pure (:func:`order_sweep_class`, :func:`select_sweep`)
and pinned directly. The split is exercised end to end with no binaries: the
parse takes the OCR seam injected, as the dispatched pass does, and the CLI's
parse is run against fake binaries laid on ``PATH``. The recovery itself — the
extractor, the marker, the questions-presented re-derivation — is the dispatched
pass's, pinned in ``tests/test_ocr_recovery.py``; what is pinned here is that
the sweep reaches it the same way and writes the same row.
"""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cli import app
from fedcourtsai.handoff import HandoffRefused, read_handoff, write_handoff
from fedcourtsai.pipeline.documents import (
    KIND_APPLICATION,
    KIND_CERT_REPLY,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
)
from fedcourtsai.pipeline.ocr_recovery import (
    OcrPageFactory,
    OcrRun,
    ScannedDocument,
)
from fedcourtsai.pipeline.ocr_sweep import (
    OcrPlan,
    OcrPlanRow,
    OcrWorkItem,
    OcrWorklist,
    SweepCandidate,
    apply_ocr_plan,
    backlog_rotation,
    check_plan,
    forward_case_ids,
    order_sweep_class,
    plan_worklist,
    select_sweep,
    sweep_selection,
    sweep_worklist,
)
from fedcourtsai.schemas import EventKind, Stage
from fedcourtsai.supremecourt import SupremeCourtClient

runner = CliRunner()

_TODAY = date(2026, 10, 17)

_OCR_TEXT = (
    "QUESTION PRESENTED\n"
    "Whether the court of appeals erred in holding that the statute reaches "
    "conduct wholly outside the United States.\n"
    "PARTIES TO THE PROCEEDING\nAcme Corp."
)


def _document(
    case_id: str,
    kind: str = KIND_PETITION,
    *,
    text: str = "",
    pages: int = 12,
    fetched_at: date = date(2026, 6, 2),
    url: str | None = None,
) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=kind,
        url=url or f"https://www.supremecourt.gov/{case_id.rsplit('/', 1)[-1]}-{kind}.pdf",
        entry_date="Jun 01 2026",
        fetched_at=fetched_at,
        pages=pages,
        text=text,
    )


def _candidate(
    case_id: str, *, forward: bool, kind: str = KIND_PETITION, fetched_at: date = date(2026, 6, 2)
) -> SweepCandidate:
    return SweepCandidate(
        scanned=ScannedDocument(
            document=_document(case_id, kind, fetched_at=fetched_at), stored_questions=None
        ),
        forward=forward,
    )


def _keys(candidates: list[SweepCandidate] | tuple[SweepCandidate, ...]) -> list[str]:
    return [c.key for c in candidates]


def _seed(
    corpus_root: Path,
    documents: list[corpus.CaseDocument],
    *,
    rows: dict[str, dict[str, object]] | None = None,
    events: list[corpus.CorpusEvent] | None = None,
) -> Path:
    """A corpus holding ``documents``; every owning case in the live slice."""
    db = corpus.corpus_db_path(corpus_root)
    overrides = rows or {}
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=f"25-{index}",
                    last_live_polled=date(2026, 6, 2),
                    **overrides.get(case_id, {}),
                )
                for index, case_id in enumerate(sorted({d.case_id for d in documents}), start=1)
            ],
        )
        corpus.upsert_documents(conn, documents)
        if events:
            corpus.upsert_events(conn, events)
    return db


def _open_event(case_id: str, *, stage: Stage | None = None) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id="evt-petition-disposition",
        case_id=case_id,
        court="scotus",
        kind=EventKind.petition,
        stage=stage,
        title="Disposition of the petition",
    )


def _client(served: dict[str, bytes]) -> SupremeCourtClient:
    def handler(request: httpx.Request) -> httpx.Response:
        key = str(request.url)
        if key in served:
            return httpx.Response(200, content=served[key])
        return httpx.Response(404)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None)


def _stub_ocr(text: str = _OCR_TEXT, *, budget_spent: bool = False) -> OcrPageFactory:
    @contextmanager
    def factory(_data: bytes) -> Iterator[OcrRun]:
        yield OcrRun(page=lambda _index: text, budget_spent=budget_spent)

    return factory


def _blank_pdf(pages: int = 1) -> bytes:
    """A PDF whose every page has an empty content stream: a scan, to the extractor."""
    kids = " ".join(f"{3 + 2 * page} 0 R" for page in range(pages))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {pages} >>".encode(),
    ]
    for page in range(pages):
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4 + 2 * page} 0 R "
            ">>".encode()
        )
        objects.append(b"<< /Length 0 >>\nstream\n\nendstream")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    start = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF".encode()
    )
    return bytes(out)


def _documents(db: Path, case_id: str) -> dict[str, corpus.CaseDocument]:
    with corpus.connect(db) as conn:
        return {d.kind: d for d in corpus.documents_for_case(conn, case_id)}


# --- the order and the slice (pure) ---------------------------------------


def test_forward_candidates_come_first_newest_stored_first() -> None:
    """The cell for a new scan is the closest one, so it heads the slice."""
    ordered = order_sweep_class(
        [
            _candidate("scotus/1", forward=False),
            _candidate("scotus/2", forward=True, fetched_at=date(2026, 10, 1)),
            _candidate("scotus/3", forward=True, fetched_at=date(2026, 10, 15)),
            _candidate("scotus/4", forward=False),
        ],
        rotation=0,
    )
    assert _keys(ordered) == [
        "scotus/3 petition",
        "scotus/2 petition",
        "scotus/1 petition",
        "scotus/4 petition",
    ]


def test_forward_ties_keep_class_order() -> None:
    same = date(2026, 10, 15)
    ordered = order_sweep_class(
        [
            _candidate("scotus/1", forward=True, fetched_at=same),
            _candidate("scotus/1", forward=True, kind=KIND_CERT_REPLY, fetched_at=same),
            _candidate("scotus/2", forward=True, fetched_at=same),
        ],
        rotation=7,
    )
    assert _keys(ordered) == ["scotus/1 petition", "scotus/1 cert-reply", "scotus/2 petition"]


def test_the_backlog_rotates_and_the_forward_tier_does_not() -> None:
    """An unreadable backlog head stays in the class, so a fixed order would starve the tail."""
    candidates = [
        _candidate("scotus/9", forward=True),
        *(_candidate(f"scotus/{n}", forward=False) for n in (1, 2, 3, 4)),
    ]
    assert _keys(order_sweep_class(candidates, rotation=2)) == [
        "scotus/9 petition",
        "scotus/3 petition",
        "scotus/4 petition",
        "scotus/1 petition",
        "scotus/2 petition",
    ]
    # Any integer is a rotation; it wraps.
    assert _keys(order_sweep_class(candidates, rotation=6)) == _keys(
        order_sweep_class(candidates, rotation=2)
    )


def test_consecutive_days_tile_the_backlog() -> None:
    backlog = [_candidate(f"scotus/{n}", forward=False) for n in range(1, 8)]
    cap = 3
    seen: list[str] = []
    day = date(2026, 10, 17)
    for offset in range(3):
        rotation = backlog_rotation(date.fromordinal(day.toordinal() + offset), cap)
        seen.extend(_keys(select_sweep(backlog, cap=cap, rotation=rotation)))
    assert set(seen) == {c.key for c in backlog}


def test_the_slice_is_the_cap() -> None:
    candidates = [_candidate(f"scotus/{n}", forward=n % 2 == 0) for n in range(1, 6)]
    assert len(select_sweep(candidates, cap=2, rotation=0)) == 2
    assert len(select_sweep(candidates, cap=50, rotation=0)) == 5
    assert select_sweep([], cap=3, rotation=0) == ()
    with pytest.raises(ValueError, match="at least 1"):
        select_sweep(candidates, cap=0, rotation=0)


# --- the forward tier -------------------------------------------------------


def test_the_forward_tier_is_open_in_scope_and_not_deferred(tmp_path: Path) -> None:
    db = _seed(
        tmp_path / "corpus",
        [_document(f"scotus/{n}") for n in range(1, 7)],
        rows={
            # 2: in scope, scored and not selected — deferred.
            "scotus/2": {"salience_version": "sal-v1", "salience_selected": False},
            # 3: scored and selected.
            "scotus/3": {"salience_version": "sal-v1", "salience_selected": True},
            # 4: deferred, but an open merits event bypasses the gate.
            "scotus/4": {"salience_version": "sal-v1", "salience_selected": False},
            # 5: out of predict scope.
            "scotus/5": {"predict_excluded": True},
        },
        events=[
            _open_event("scotus/1"),
            _open_event("scotus/2"),
            _open_event("scotus/3"),
            _open_event("scotus/4", stage=Stage.merits),
            _open_event("scotus/5"),
            # 6: its only event is resolved.
            _open_event("scotus/6").model_copy(update={"resolved": True}),
        ],
    )
    with corpus.connect(db) as conn:
        assert forward_case_ids(conn) == {"scotus/1", "scotus/3", "scotus/4"}


def test_the_selection_reads_the_class_and_slices_it(tmp_path: Path) -> None:
    db = _seed(
        tmp_path / "corpus",
        [
            _document("scotus/1"),
            _document("scotus/2", KIND_APPLICATION, fetched_at=date(2026, 10, 15)),
            _document("scotus/3", text="extracted"),
            _document("scotus/4", pages=0),
        ],
        events=[_open_event("scotus/2")],
    )
    with corpus.connect(db) as conn:
        selection = sweep_selection(conn, cap=1, today=_TODAY)
    assert selection.class_size == 2
    assert selection.forward_size == 1
    assert selection.class_by_kind == {KIND_PETITION: 1, KIND_APPLICATION: 1}
    assert _keys(selection.slice) == ["scotus/2 application"]
    worklist = sweep_worklist(selection, cap=1)
    assert worklist.items == [
        OcrWorkItem(
            case_id="scotus/2",
            kind=KIND_APPLICATION,
            url="https://www.supremecourt.gov/2-application.pdf",
            pages=12,
            forward=True,
        )
    ]


# --- the parse --------------------------------------------------------------


def _worklist(*items: OcrWorkItem, cap: int = 10) -> OcrWorklist:
    return OcrWorklist(class_size=len(items), forward_size=0, cap=cap, items=list(items))


def _item(case_id: str, kind: str = KIND_PETITION, *, pages: int = 12) -> OcrWorkItem:
    doc = _document(case_id, kind)
    return OcrWorkItem(case_id=case_id, kind=kind, url=doc.url, pages=pages, forward=False)


def test_the_parse_reads_each_item_and_names_what_it_could_not() -> None:
    served = _item("scotus/1")
    missing = _item("scotus/2")
    with _client({served.url: _blank_pdf(2)}) as client:
        plan = plan_worklist(
            client, _worklist(served, missing), char_cap=150_000, ocr_page_factory=_stub_ocr()
        )
    assert [row.key for row in plan.rows] == ["scotus/1 petition"]
    row = plan.rows[0]
    assert row.ocr_derived is True and row.pages == 2 and _OCR_TEXT in row.text
    assert plan.failures == {"scotus/2 petition": "not-served"}
    assert plan.unreached == []


def test_the_parse_discards_a_partial_or_empty_reading() -> None:
    item = _item("scotus/1")
    with _client({item.url: _blank_pdf()}) as client:
        cut = plan_worklist(
            client,
            _worklist(item),
            char_cap=150_000,
            ocr_page_factory=_stub_ocr(budget_spent=True),
        )
        blank = plan_worklist(
            client, _worklist(item), char_cap=150_000, ocr_page_factory=_stub_ocr("")
        )
    assert cut.rows == [] and cut.failures == {"scotus/1 petition": "budget-exhausted"}
    assert blank.rows == [] and blank.failures == {"scotus/1 petition": "empty-after-ocr"}


def test_the_parse_deadline_declines_the_rest_in_order() -> None:
    items = [_item("scotus/1", pages=1), _item("scotus/2", pages=200), _item("scotus/3", pages=1)]
    with _client({i.url: _blank_pdf() for i in items}) as client:
        plan = plan_worklist(
            client,
            _worklist(*items),
            char_cap=150_000,
            ocr_page_factory=_stub_ocr(),
            deadline=100.0,
            monotonic=lambda: 0.0,
        )
    assert [row.key for row in plan.rows] == ["scotus/1 petition"]
    assert plan.unreached == ["scotus/2 petition", "scotus/3 petition"]


def test_the_parse_refuses_a_worklist_the_projection_could_not_write() -> None:
    item = _item("scotus/1")
    with _client({}) as client:
        with pytest.raises(HandoffRefused, match="twice"):
            plan_worklist(client, _worklist(item, item), char_cap=1, ocr_page_factory=_stub_ocr())
        with pytest.raises(HandoffRefused, match="above its cap"):
            plan_worklist(
                client,
                _worklist(item, _item("scotus/2"), cap=1),
                char_cap=1,
                ocr_page_factory=_stub_ocr(),
            )
        derived = item.model_copy(update={"kind": KIND_QUESTIONS_PRESENTED})
        with pytest.raises(HandoffRefused, match="not a recoverable kind"):
            plan_worklist(client, _worklist(derived), char_cap=1, ocr_page_factory=_stub_ocr())


# --- the writer -------------------------------------------------------------


def _row(document: corpus.CaseDocument, text: str = _OCR_TEXT) -> OcrPlanRow:
    return OcrPlanRow(
        case_id=document.case_id,
        kind=document.kind,
        url=document.url,
        text=text,
        pages=document.pages,
        truncated=False,
        ocr_derived=True,
    )


def test_the_writer_stores_the_reading_as_the_dispatched_pass_does(tmp_path: Path) -> None:
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with corpus.connect(db) as conn:
        result = apply_ocr_plan(
            conn,
            OcrPlan(rows=[_row(petition)]),
            cap=10,
            char_cap=150_000,
            today=_TODAY,
            apply=True,
        )
    assert list(result.written) == ["scotus/1 petition"]
    assert result.questions_rederived == 1
    stored = _documents(db, "scotus/1")
    assert stored[KIND_PETITION].text == _OCR_TEXT
    assert stored[KIND_PETITION].ocr_derived is True
    assert stored[KIND_PETITION].fetched_at == _TODAY
    assert "statute reaches" in stored[KIND_QUESTIONS_PRESENTED].text


def test_the_writer_skips_a_row_the_corpus_moved_past(tmp_path: Path) -> None:
    """A row that gained text, moved its link or vanished since the projection is
    skipped and named: the corpus moved on, which is not a forged plan."""
    gained = _document("scotus/1", text="now extracted")
    moved = _document("scotus/2")
    db = _seed(tmp_path / "corpus", [gained, moved])
    plan = OcrPlan(
        rows=[
            _row(_document("scotus/1")),
            _row(moved).model_copy(update={"url": "https://www.supremecourt.gov/old.pdf"}),
            _row(_document("scotus/1", KIND_CERT_REPLY)),
        ]
    )
    with corpus.connect(db) as conn:
        result = apply_ocr_plan(conn, plan, cap=10, char_cap=150_000, today=_TODAY, apply=True)
    assert result.written == {}
    assert result.skipped == {
        "scotus/1 cert-reply": "no-stored-row",
        "scotus/1 petition": "has-text",
        "scotus/2 petition": "url-changed",
    }
    assert _documents(db, "scotus/1")[KIND_PETITION].text == "now extracted"


def test_the_writer_dry_run_writes_nothing(tmp_path: Path) -> None:
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with corpus.connect(db) as conn:
        result = apply_ocr_plan(
            conn,
            OcrPlan(rows=[_row(petition)]),
            cap=10,
            char_cap=150_000,
            today=_TODAY,
            apply=False,
        )
    assert list(result.written) == ["scotus/1 petition"] and result.applied is False
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""


def test_the_writer_refuses_a_plan_whole() -> None:
    one = _row(_document("scotus/1"))
    with pytest.raises(HandoffRefused, match="above the cap"):
        check_plan(OcrPlan(rows=[one, _row(_document("scotus/2"))]), cap=1, char_cap=10_000)
    with pytest.raises(HandoffRefused, match="twice"):
        check_plan(OcrPlan(rows=[one, one]), cap=10, char_cap=10_000)
    with pytest.raises(HandoffRefused, match="document cap"):
        check_plan(OcrPlan(rows=[one]), cap=10, char_cap=10)
    with pytest.raises(HandoffRefused, match="empty"):
        check_plan(OcrPlan(rows=[one.model_copy(update={"text": "  \n"})]), cap=10, char_cap=100)
    derived = one.model_copy(update={"kind": KIND_QUESTIONS_PRESENTED})
    with pytest.raises(HandoffRefused, match="not a recoverable kind"):
        check_plan(OcrPlan(rows=[derived]), cap=10, char_cap=10_000)


def test_a_plan_with_an_unknown_field_is_refused_on_read(tmp_path: Path) -> None:
    path = tmp_path / "plan.json"
    write_handoff(path, OcrPlan(rows=[_row(_document("scotus/1"))]))
    payload = json.loads(path.read_text())
    payload["rows"][0]["note"] = "x"
    path.write_text(json.dumps(payload))
    with pytest.raises(HandoffRefused, match="not a valid OcrPlan"):
        read_handoff(path, OcrPlan)


# --- the CLI ----------------------------------------------------------------


def _fake_binary(directory: Path, name: str, script: str) -> None:
    path = directory / name
    path.write_text(f"#!/bin/sh\n{script}\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_the_cli_dry_run_lists_the_slice_and_fetches_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(
        tmp_path / "corpus",
        [_document("scotus/1"), _document("scotus/2", KIND_APPLICATION)],
        events=[_open_event("scotus/2")],
    )
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))

    def no_fetch(*_args: object, **_kwargs: object) -> SupremeCourtClient:
        raise AssertionError("the sweep's dry run fetches nothing")

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", no_fetch)
    result = runner.invoke(app, ["ocr-recover-petitions", "--sweep"])
    assert result.exit_code == 0, result.output
    assert (
        "sweep ledger — ocr-recover-petitions: would fill 2; filled 0; remaining 2 (cap 10); "
        "1 a forward cell reads"
    ) in result.output
    lines = [line.strip() for line in result.output.splitlines() if "slice " in line]
    assert lines == [
        "slice scotus/2 application: 12 pages, forward, stored 2026-06-02",
        "slice scotus/1 petition: 12 pages, backlog, stored 2026-06-02",
    ]


def test_the_cli_split_round_trips_through_its_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Projection, parse and writer, each its own invocation, as the three jobs run them."""
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition], events=[_open_event("scotus/1")])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    worklist = tmp_path / "handoff" / "worklist.json"
    plan = tmp_path / "handoff" / "plan.json"

    emitted = runner.invoke(
        app, ["ocr-recover-petitions", "--sweep", "--emit-worklist", str(worklist)]
    )
    assert emitted.exit_code == 0, emitted.output
    assert read_handoff(worklist, OcrWorklist).items[0].key == "scotus/1 petition"

    binaries = tmp_path / "bin"
    binaries.mkdir()
    _fake_binary(binaries, "pdftoppm", "printf PNG")
    _fake_binary(binaries, "tesseract", "printf 'Recovered page text.'")
    monkeypatch.setenv("PATH", f"{binaries}{os.pathsep}{os.environ['PATH']}")
    pdf = _blank_pdf(3)

    class _Served(SupremeCourtClient):
        def __init__(self, **_kwargs: object) -> None:
            super().__init__(
                throttle_seconds=1.0,
                client=httpx.Client(
                    transport=httpx.MockTransport(lambda _r: httpx.Response(200, content=pdf)),
                    headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
                ),
                sleep=lambda _s: None,
            )

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", _Served)
    # The parse opens no corpus: point it at one that does not exist.
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    parsed = runner.invoke(
        app,
        [
            "ocr-recover-petitions",
            "--worklist",
            str(worklist),
            "--plan-out",
            str(plan),
            "--deadline-seconds",
            "600",
        ],
    )
    assert parsed.exit_code == 0, parsed.output
    assert "read 1; not recovered 0; unreached 0" in parsed.output
    assert "Recovered page text" not in parsed.output, "the parse never prints filing text"
    assert "scotus/1 petition: pages=3" in parsed.output

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    written = runner.invoke(
        app, ["ocr-recover-petitions", "--from-plan", str(plan), "--sweep", "--apply"]
    )
    assert written.exit_code == 0, written.output
    assert "planned 1; wrote 1; skipped 0" in written.output
    assert "Recovered page text" not in written.output
    stored = _documents(db, "scotus/1")[KIND_PETITION]
    assert "Recovered page text." in stored.text and stored.ocr_derived is True


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--sweep", "--max-cases", "5"], "takes no --max-cases"),
        (["--sweep", "--apply"], "applies only --from-plan"),
        (["--emit-worklist", "w.json"], "run in --sweep mode"),
        (["--worklist", "w.json"], "go together"),
        (["--worklist", "w.json", "--plan-out", "p.json", "--sweep"], "opens no corpus"),
        (["--sweep", "--emit-worklist", "w.json", "--from-plan", "p.json"], "pass one"),
        (["--sweep", "--deadline-seconds", "60"], "bounds the parse"),
    ],
)
def test_the_cli_refuses_a_mode_it_cannot_tell_apart(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, argv: list[str], message: str
) -> None:
    _seed(tmp_path / "corpus", [_document("scotus/1")])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["ocr-recover-petitions", *argv])
    assert result.exit_code == 2, result.output
    assert message in result.output


def test_the_cli_writer_refuses_a_plan_above_the_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    documents = [_document(f"scotus/{n}") for n in range(1, 13)]
    db = _seed(tmp_path / "corpus", documents)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    plan = tmp_path / "plan.json"
    write_handoff(plan, OcrPlan(rows=[_row(d) for d in documents]))
    result = runner.invoke(
        app, ["ocr-recover-petitions", "--from-plan", str(plan), "--sweep", "--apply"]
    )
    assert result.exit_code == 1, result.output
    assert "above the cap of 10" in result.output
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""
