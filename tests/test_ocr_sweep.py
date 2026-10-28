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
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cli import app
from fedcourtsai.handoff import HandoffRefused, read_handoff, write_handoff
from fedcourtsai.pipeline.documents import (
    BIO_URL_JOIN,
    KIND_APPLICATION,
    KIND_CERT_REPLY,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
)
from fedcourtsai.pipeline.ocr_recovery import (
    OcrPageFactory,
    OcrRun,
    ScannedDocument,
    scanned_documents,
)
from fedcourtsai.pipeline.ocr_sweep import (
    FRESH_DAYS,
    OcrPlan,
    OcrPlanRow,
    OcrSweepApplyResult,
    OcrWorkItem,
    OcrWorklist,
    SweepCandidate,
    apply_ocr_plan,
    check_plan,
    dispatched_worklist,
    forward_case_ids,
    order_sweep_class,
    plan_worklist,
    select_sweep,
    sweep_selection,
    sweep_worklist,
    window_rotation,
)
from fedcourtsai.schemas import EventKind, Stage
from fedcourtsai.supremecourt import SupremeCourtClient

runner = CliRunner()

_TODAY = date(2026, 10, 17)
_NOW = datetime(2026, 10, 17, 2, 31, tzinfo=UTC)

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

_FRESH = date(2026, 10, 15)  # within FRESH_DAYS of _TODAY
_STALE = date(2026, 6, 2)  # long before it


def test_fresh_forward_candidates_come_first_newest_stored_first() -> None:
    """The cell for a new scan is the closest one, so it heads the slice."""
    ordered = order_sweep_class(
        [
            _candidate("scotus/1", forward=False),
            _candidate("scotus/2", forward=True, fetched_at=_FRESH - timedelta(days=1)),
            _candidate("scotus/3", forward=True, fetched_at=_FRESH),
            _candidate("scotus/4", forward=False),
            _candidate("scotus/5", forward=True, fetched_at=_STALE),
        ],
        rotation=0,
        today=_TODAY,
    )
    assert _keys(ordered) == [
        "scotus/3 petition",
        "scotus/2 petition",
        "scotus/5 petition",
        "scotus/1 petition",
        "scotus/4 petition",
    ]


def test_fresh_ties_keep_class_order() -> None:
    ordered = order_sweep_class(
        [
            _candidate("scotus/1", forward=True, fetched_at=_FRESH),
            _candidate("scotus/1", forward=True, kind=KIND_CERT_REPLY, fetched_at=_FRESH),
            _candidate("scotus/2", forward=True, fetched_at=_FRESH),
        ],
        rotation=7,
        today=_TODAY,
    )
    assert _keys(ordered) == ["scotus/1 petition", "scotus/1 cert-reply", "scotus/2 petition"]


def test_the_fresh_head_ages_out_into_rotation() -> None:
    """A forward scan that never reads holds an unrotated slot for FRESH_DAYS at most."""
    stored = _TODAY - timedelta(days=FRESH_DAYS)
    stuck = _candidate("scotus/1", forward=True, fetched_at=stored)
    others = [_candidate(f"scotus/{n}", forward=True, fetched_at=_STALE) for n in (2, 3)]
    on_day = order_sweep_class([stuck, *others], rotation=1, today=_TODAY)
    assert _keys(on_day)[0] == "scotus/1 petition"
    next_day = order_sweep_class([stuck, *others], rotation=1, today=_TODAY + timedelta(days=1))
    # Now one of three in the rotated forward tier, and rotation 1 starts it second.
    assert _keys(next_day) == ["scotus/2 petition", "scotus/3 petition", "scotus/1 petition"]


def test_the_older_tiers_rotate() -> None:
    """An unreadable head stays in the class, so a fixed order would starve the tail."""
    candidates = [
        _candidate("scotus/9", forward=True, fetched_at=_STALE),
        _candidate("scotus/8", forward=True, fetched_at=_STALE),
        *(_candidate(f"scotus/{n}", forward=False) for n in (1, 2, 3, 4)),
    ]
    assert _keys(order_sweep_class(candidates, rotation=2, today=_TODAY)) == [
        "scotus/9 petition",
        "scotus/8 petition",
        "scotus/3 petition",
        "scotus/4 petition",
        "scotus/1 petition",
        "scotus/2 petition",
    ]
    assert _keys(order_sweep_class(candidates, rotation=1, today=_TODAY))[:2] == [
        "scotus/8 petition",
        "scotus/9 petition",
    ]
    # Any integer is a rotation; it wraps.
    assert _keys(order_sweep_class(candidates, rotation=6, today=_TODAY)) == _keys(
        order_sweep_class(candidates, rotation=2, today=_TODAY)
    )


def test_consecutive_windows_tile_the_backlog() -> None:
    backlog = [_candidate(f"scotus/{n}", forward=False) for n in range(1, 8)]
    cap = 3
    seen: list[str] = []
    start = datetime(2026, 10, 17, 2, 31, tzinfo=UTC)
    for window in range(3):
        rotation = window_rotation(start + timedelta(hours=6 * window), cap)
        seen.extend(_keys(select_sweep(backlog, cap=cap, rotation=rotation, today=_TODAY)))
    assert set(seen) == {c.key for c in backlog}


def test_each_seed_window_is_its_own_rotation() -> None:
    day = datetime(2026, 10, 17, tzinfo=UTC)
    windows = {window_rotation(day.replace(hour=h, minute=31), 1) for h in (2, 8, 14, 20)}
    assert len(windows) == 4
    assert window_rotation(day.replace(hour=20), 1) + 1 == window_rotation(
        day + timedelta(days=1, hours=2), 1
    )


def test_the_slice_is_the_cap() -> None:
    candidates = [_candidate(f"scotus/{n}", forward=n % 2 == 0) for n in range(1, 6)]
    assert len(select_sweep(candidates, cap=2, rotation=0, today=_TODAY)) == 2
    assert len(select_sweep(candidates, cap=50, rotation=0, today=_TODAY)) == 5
    assert select_sweep([], cap=3, rotation=0, today=_TODAY) == ()
    with pytest.raises(ValueError, match="at least 1"):
        select_sweep(candidates, cap=0, rotation=0, today=_TODAY)


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
            _document("scotus/2", KIND_APPLICATION, fetched_at=_FRESH),
            _document("scotus/3", text="extracted"),
            _document("scotus/4", pages=0),
        ],
        events=[_open_event("scotus/2")],
    )
    with corpus.connect(db) as conn:
        selection = sweep_selection(conn, cap=1, now=_NOW)
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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("case_id", "scotus/1\n## forged"),
        ("case_id", "nocourt"),
        ("case_id", "ca9/123"),
        ("kind", KIND_QUESTIONS_PRESENTED),
        ("kind", "petition\n"),
        ("url", "https://example.com/a.pdf"),
        ("url", "https://www.supremecourt.gov/a.pdf\n## forged"),
        ("url", "http://www.supremecourt.gov/a.pdf"),
    ],
)
def test_a_malformed_identifier_is_refused_on_read(tmp_path: Path, field: str, value: str) -> None:
    """Both files cross from another job: a bad id must never reach an apply or a summary."""
    item = _item("scotus/1").model_dump()
    row = _row(_document("scotus/1")).model_dump()
    for model, payload, wrap in (
        (OcrWorklist, item, lambda p: {"class_size": 1, "forward_size": 0, "cap": 1, "items": [p]}),
        (OcrPlan, row, lambda p: {"rows": [p]}),
    ):
        path = tmp_path / f"{model.__name__}.json"
        path.write_text(json.dumps(wrap({**payload, field: value})))
        with pytest.raises(HandoffRefused, match=f"not a valid {model.__name__}"):
            read_handoff(path, model)


@pytest.mark.parametrize(
    "extra",
    [
        {"failures": {"scotus/1 petition": "not-served\n## forged ledger line"}},
        {"failures": {"scotus/1 petition": "x" * 1000}},
        {"failures": {"scotus/1\npetition": "not-served"}},
        {"failures": {"scotus/1 petition": "something-else"}},
        {"unreached": ["scotus/1 petition\n## forged"]},
        {"unreached": ["scotus/1 petition"] * 201},
    ],
)
def test_a_free_text_failure_or_unreached_entry_is_refused_on_read(
    tmp_path: Path, extra: dict[str, object]
) -> None:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"rows": [], **extra}))
    with pytest.raises(HandoffRefused, match="not a valid OcrPlan"):
        read_handoff(path, OcrPlan)


# --- the writer -------------------------------------------------------------


def _row(document: corpus.CaseDocument, text: str = _OCR_TEXT) -> OcrPlanRow:
    return OcrPlanRow(
        case_id=document.case_id,
        kind=document.kind,
        url=document.url,
        text=text,
        pages=document.pages or 1,
        truncated=False,
        ocr_derived=True,
    )


def _bound(plan: OcrPlan, *, cap: int = 10) -> OcrWorklist:
    """The worklist a plan answers: one item per row, failure and unreached key."""
    items = [
        OcrWorkItem(case_id=r.case_id, kind=r.kind, url=r.url, pages=r.pages, forward=False)
        for r in plan.rows
    ]
    for key in [*plan.failures, *plan.unreached]:
        case_id, kind = key.split(" ")
        items.append(_item(case_id, kind))
    return OcrWorklist(class_size=len(items), forward_size=0, cap=cap, items=items)


def _apply(db: Path, plan: OcrPlan, *, apply: bool = True) -> OcrSweepApplyResult:
    with corpus.connect(db) as conn:
        return apply_ocr_plan(
            conn, plan, _bound(plan), cap=10, char_cap=150_000, today=_TODAY, apply=apply
        )


def test_the_writer_stores_the_reading_as_the_dispatched_pass_does(tmp_path: Path) -> None:
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    result = _apply(db, OcrPlan(rows=[_row(petition)]))
    assert list(result.written) == ["scotus/1 petition"]
    assert result.questions_rederived == 1
    stored = _documents(db, "scotus/1")
    assert stored[KIND_PETITION].text == _OCR_TEXT
    assert stored[KIND_PETITION].ocr_derived is True
    assert stored[KIND_PETITION].fetched_at == _TODAY
    assert "statute reaches" in stored[KIND_QUESTIONS_PRESENTED].text


_SET_KEY = (
    "https://www.supremecourt.gov/a.pdf" + BIO_URL_JOIN + "https://www.supremecourt.gov/b.pdf"
)


@pytest.mark.parametrize(
    ("stored", "outcome"),
    [
        ({"text": "now extracted"}, "has-text"),
        ({"pages": 0}, "no-pages"),
        ({"url": _SET_KEY}, "set-keyed"),
        ({"text": "  \n\t "}, "written"),
        ({}, "written"),
    ],
)
def test_the_writer_holds_each_row_to_the_recovery_class(
    tmp_path: Path, stored: dict[str, object], outcome: str
) -> None:
    """Every exclusion the dispatched pass applies, applied again at write time.

    A row that left the class since the projection is skipped and named, not
    written: dropping the writer's exclusion check fails one of these.
    """
    planned = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [planned.model_copy(update=stored)])
    result = _apply(db, OcrPlan(rows=[_row(planned)]))
    if outcome == "written":
        assert list(result.written) == ["scotus/1 petition"] and result.skipped == {}
        assert _documents(db, "scotus/1")[KIND_PETITION].text == _OCR_TEXT
    else:
        assert result.written == {}
        assert result.skipped == {"scotus/1 petition": outcome}
        assert _documents(db, "scotus/1")[KIND_PETITION].text != _OCR_TEXT


def test_the_writer_skips_a_row_whose_link_moved_or_vanished(tmp_path: Path) -> None:
    moved = _document("scotus/2")
    db = _seed(
        tmp_path / "corpus",
        [
            _document("scotus/1"),
            moved.model_copy(update={"url": "https://www.supremecourt.gov/new.pdf"}),
        ],
    )
    result = _apply(db, OcrPlan(rows=[_row(moved), _row(_document("scotus/1", KIND_CERT_REPLY))]))
    assert result.written == {}
    assert result.skipped == {
        "scotus/1 cert-reply": "no-stored-row",
        "scotus/2 petition": "url-changed",
    }


def test_a_stored_question_survives_an_empty_rederivation(tmp_path: Path) -> None:
    """The deriver's honest empty row never replaces a stored question."""
    petition = _document("scotus/1")
    question = corpus.CaseDocument(
        case_id="scotus/1",
        kind=KIND_QUESTIONS_PRESENTED,
        url=petition.url,
        fetched_at=_STALE,
        pages=0,
        text="Whether the stored question survives.",
    )
    db = _seed(tmp_path / "corpus", [petition, question])
    heading_only = "QUESTION PRESENTED\n\nPARTIES TO THE PROCEEDING\nAcme Corp."
    result = _apply(db, OcrPlan(rows=[_row(petition, heading_only)]))
    assert list(result.written) == ["scotus/1 petition"]
    stored = _documents(db, "scotus/1")
    assert stored[KIND_QUESTIONS_PRESENTED].text == "Whether the stored question survives."


def test_the_writer_dry_run_writes_nothing(tmp_path: Path) -> None:
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    result = _apply(db, OcrPlan(rows=[_row(petition)]), apply=False)
    assert list(result.written) == ["scotus/1 petition"] and result.applied is False
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""


def test_the_writer_refuses_a_plan_whole() -> None:
    one = _row(_document("scotus/1"))
    two = _row(_document("scotus/2"))

    def check(
        plan: OcrPlan, *, cap: int = 10, char_cap: int = 10_000, bound: OcrPlan | None = None
    ) -> None:
        check_plan(plan, _bound(bound or plan), cap=cap, char_cap=char_cap)

    with pytest.raises(HandoffRefused, match="above the cap"):
        check(OcrPlan(rows=[one, two]), cap=1)
    with pytest.raises(HandoffRefused, match="twice"):
        check(OcrPlan(rows=[one, one]), bound=OcrPlan(rows=[one]))
    with pytest.raises(HandoffRefused, match="document cap"):
        check(OcrPlan(rows=[one]), char_cap=10)
    with pytest.raises(HandoffRefused, match="empty"):
        check(OcrPlan(rows=[one.model_copy(update={"text": "  \n"})]))
    with pytest.raises(HandoffRefused, match="not marked ocr_derived"):
        check(OcrPlan(rows=[one.model_copy(update={"ocr_derived": False})]))
    # Bound to the projection's worklist: a row, failure or unreached key off it.
    with pytest.raises(HandoffRefused, match="not an item of this window's worklist"):
        check(OcrPlan(rows=[one, two]), bound=OcrPlan(rows=[one]))
    moved = one.model_copy(update={"url": "https://www.supremecourt.gov/other.pdf"})
    with pytest.raises(HandoffRefused, match="not an item of this window's worklist"):
        check(OcrPlan(rows=[moved]), bound=OcrPlan(rows=[one]))
    with pytest.raises(HandoffRefused, match="not on this window's worklist"):
        check(
            OcrPlan(rows=[one], failures={"scotus/2 petition": "not-served"}),
            bound=OcrPlan(rows=[one]),
        )
    with pytest.raises(HandoffRefused, match="not on this window's worklist"):
        check(OcrPlan(rows=[one], unreached=["scotus/2 petition"]), bound=OcrPlan(rows=[one]))


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
    # The fill sweeps' ledger shape (config/tracking.yaml), exactly.
    assert (
        "sweep ledger — ocr-recover-petitions: would fill 2; filled 0; remaining 2 (cap 10)\n"
    ) in result.output
    assert "1 of the class a forward cell reads" in result.output
    lines = [line.strip() for line in result.output.splitlines() if "slice " in line]
    # The application's forward row is older than FRESH_DAYS here, so it leads the
    # rotated forward tier, which still precedes the backlog.
    assert lines[0].startswith("slice scotus/2 application: 12 pages, forward")
    assert lines[1].startswith("slice scotus/1 petition: 12 pages, backlog")


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
    pdf = _blank_pdf(12)  # the page count the stored row carries

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
    assert "scotus/1 petition: pages=12" in parsed.output

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    written = runner.invoke(
        app,
        [
            "ocr-recover-petitions",
            "--from-plan",
            str(plan),
            "--bind-worklist",
            str(worklist),
            "--sweep",
            "--apply",
        ],
    )
    assert written.exit_code == 0, written.output
    assert "would fill 1; filled 1; remaining 0 (cap 10)" in written.output
    assert "Recovered page text" not in written.output
    stored = _documents(db, "scotus/1")[KIND_PETITION]
    assert "Recovered page text." in stored.text and stored.ocr_derived is True


def test_the_cli_writer_prints_only_counts_of_the_parses_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """What reaches the public step summary from the plan: counts and validated keys."""
    petition = _document("scotus/1")
    _seed(tmp_path / "corpus", [petition, _document("scotus/2")])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    plan = OcrPlan(
        rows=[_row(petition, "SECRET-FILING-TEXT")],
        failures={"scotus/2 petition": "empty-after-ocr"},
        unreached=["scotus/3 petition"],
    )
    plan_path, bound_path = tmp_path / "plan.json", tmp_path / "worklist.json"
    write_handoff(plan_path, plan)
    write_handoff(bound_path, _bound(plan))
    result = runner.invoke(
        app,
        [
            "ocr-recover-petitions",
            "--from-plan",
            str(plan_path),
            "--bind-worklist",
            str(bound_path),
            "--sweep",
            "--apply",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "SECRET-FILING-TEXT" not in result.output
    assert "scotus/2" not in result.output and "scotus/3" not in result.output
    assert "the parse did not recover 1 and did not reach 1" in result.output
    keys = [
        line.split(":", 1)[0].strip()
        for line in result.output.splitlines()
        if line.startswith("  scotus/")
    ]
    assert keys == ["scotus/1 petition"]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--sweep", "--max-cases", "5"], "takes no --max-cases"),
        (["--sweep", "--apply"], "applies only --from-plan"),
        (["--emit-worklist", "w.json", "--apply"], "the projection writes nothing"),
        (["--emit-worklist", "w.json", "--max-cases", "201"], "a slice of 1 to 200"),
        (["--emit-worklist", "w.json", "--max-cases", "0"], "a slice of 1 to 200"),
        (["--emit-worklist", "w.json", "--max-cases", "2", "--probe", "1"], "pass one"),
        (["--from-plan", "p.json", "--bind-worklist", "w.json"], "takes the dispatch's"),
        (["--from-plan", "p.json"], "--bind-worklist go together"),
        (["--worklist", "w.json"], "exactly one of"),
        (["--worklist", "w.json", "--plan-out", "p.json", "--probe-only"], "exactly one of"),
        (["--worklist", "w.json", "--probe-only", "--max-cases", "1"], "opens no corpus"),
        (["--worklist", "w.json", "--plan-out", "p.json", "--sweep"], "opens no corpus"),
        (["--sweep", "--emit-worklist", "w.json", "--from-plan", "p.json"], "pass one"),
        (["--sweep", "--deadline-seconds", "60"], "bounds the parse"),
        (["--sweep", "--from-plan", "p.json"], "--bind-worklist go together"),
        (["--sweep", "--probe", "3"], "the sweep probes nothing"),
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
    plan = OcrPlan(rows=[_row(d) for d in documents])
    plan_path, bound_path = tmp_path / "plan.json", tmp_path / "worklist.json"
    write_handoff(plan_path, plan)
    write_handoff(bound_path, _bound(plan, cap=12))
    result = runner.invoke(
        app,
        [
            "ocr-recover-petitions",
            "--from-plan",
            str(plan_path),
            "--bind-worklist",
            str(bound_path),
            "--sweep",
            "--apply",
        ],
    )
    assert result.exit_code == 1, result.output
    assert "above the cap of 10" in result.output
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""


@pytest.mark.parametrize(
    "payload",
    [
        {"rows": [], "EVIL **md** [x](https://e.vil) 555-1212": 1},
        {"rows": [], "failures": {"## John Doe 123 Main St": "not-served"}},
        {"rows": [], "failures": {"scotus/1\npetition": "not-served"}},
        {"rows": [], "failures": {"scotus/1 petition": "## John Doe 123 Main St\n"}},
    ],
)
def test_a_refusal_names_none_of_the_files_own_text(
    tmp_path: Path, payload: dict[str, object]
) -> None:
    """The refusal reaches a public step summary: an extra field's name or a dict key
    is the file's own text, so the message carries only the error type and positions."""
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(HandoffRefused) as refused:
        read_handoff(path, OcrPlan)
    message = str(refused.value).replace(str(path), "<path>")
    for forged in ("\n", "EVIL", "**", "](", "555", "1212", "John", "123", "Main", "##"):
        assert forged not in message, (forged, message)
    assert "not a valid OcrPlan" in message


@pytest.mark.parametrize(
    "extra",
    [
        {"failures": {"scotus/1 questions-presented": "not-served"}},
        {"unreached": ["scotus/1 not-a-kind"]},
    ],
)
def test_a_key_naming_a_kind_outside_the_class_is_refused_on_read(
    tmp_path: Path, extra: dict[str, object]
) -> None:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"rows": [], **extra}))
    with pytest.raises(HandoffRefused, match="not a valid OcrPlan"):
        read_handoff(path, OcrPlan)


def test_a_page_count_must_be_an_integer(tmp_path: Path) -> None:
    row = _row(_document("scotus/1")).model_dump()
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"rows": [{**row, "pages": "12"}]}))
    with pytest.raises(HandoffRefused, match="not a valid OcrPlan"):
        read_handoff(path, OcrPlan)


def test_the_writer_skips_a_reading_of_another_length(tmp_path: Path) -> None:
    """The link now serves a different filing than the one the projection counted."""
    stored = _document("scotus/1", pages=12)
    db = _seed(tmp_path / "corpus", [stored])
    result = _apply(db, OcrPlan(rows=[_row(stored).model_copy(update={"pages": 30})]))
    assert result.written == {}
    assert result.skipped == {"scotus/1 petition": "pages-changed"}


# --- the dispatched pass's split (run-repair's ocr-recovery) ---------------


def _dispatched_apply(db: Path, plan: OcrPlan, bound: OcrWorklist) -> OcrSweepApplyResult:
    with corpus.connect(db) as conn:
        return apply_ocr_plan(
            conn,
            plan,
            bound,
            cap=bound.cap,
            char_cap=150_000,
            today=_TODAY,
            apply=True,
            dispatched=True,
        )


def test_the_dispatched_worklist_is_the_head_of_the_class_or_a_spread_sample(
    tmp_path: Path,
) -> None:
    """An apply's worklist is the slice in class order; a dry run's is the probe sample."""
    documents = [_document(f"scotus/{n}") for n in range(1, 7)]
    db = _seed(tmp_path / "corpus", documents, events=[_open_event("scotus/2")])
    with corpus.connect(db) as conn:
        scan = scanned_documents(conn)
        sliced = dispatched_worklist(conn, scan.candidates, max_cases=2, probe=3)
        sampled = dispatched_worklist(conn, scan.candidates, max_cases=None, probe=3)
    assert [item.key for item in sliced.items] == ["scotus/1 petition", "scotus/2 petition"]
    assert sliced.cap == 2 and sliced.class_size == 6 and sliced.forward_size == 1
    assert [item.forward for item in sliced.items] == [False, True]
    assert [item.key for item in sampled.items] == [
        "scotus/1 petition",
        "scotus/3 petition",
        "scotus/5 petition",
    ]


def test_the_dispatched_writer_stores_what_the_dispatched_pass_stored(tmp_path: Path) -> None:
    """A text-layer reading and a filing of another length are written, as before the split.

    The sweep's writer refuses the first and skips the second; the dispatched
    pass always stored whatever the re-served filing read as.
    """
    first, second = _document("scotus/1"), _document("scotus/2")
    db = _seed(tmp_path / "corpus", [first, second])
    plan = OcrPlan(
        rows=[
            _row(first).model_copy(update={"ocr_derived": False}),
            _row(second).model_copy(update={"pages": 30}),
        ]
    )
    result = _dispatched_apply(db, plan, _bound(plan, cap=2))
    assert sorted(result.written) == ["scotus/1 petition", "scotus/2 petition"]
    assert _documents(db, "scotus/1")[KIND_PETITION].ocr_derived is False
    assert _documents(db, "scotus/2")[KIND_PETITION].pages == 30


def test_the_dispatched_writer_refuses_a_plan_that_drops_an_item(tmp_path: Path) -> None:
    """Every item read, not recovered or unreached, exactly once: the ledger is built on it."""
    first, second = _document("scotus/1"), _document("scotus/2")
    db = _seed(tmp_path / "corpus", [first, second])
    plan = OcrPlan(rows=[_row(first)])
    bound = _bound(OcrPlan(rows=[_row(first), _row(second)]), cap=2)
    with pytest.raises(HandoffRefused, match="accounts for 1 of the worklist's 2 items"):
        _dispatched_apply(db, plan, bound)
    twice = OcrPlan(rows=[_row(first)], failures={"scotus/1 petition": "not-served"})
    with pytest.raises(HandoffRefused, match="names scotus/1 petition twice"):
        _dispatched_apply(db, twice, _bound(OcrPlan(rows=[_row(first)]), cap=2))


def test_the_cli_dispatched_split_round_trips_and_states_the_class_it_leaves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Projection, parse and writer as run-repair's three jobs run them.

    The projection prints the dry run's class ledger and fetches nothing; the
    writer's JSON ledger carries the `remaining` the workflow's re-read must
    then find as `candidates`.
    """
    db = _seed(tmp_path / "corpus", [_document("scotus/1"), _document("scotus/2")])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    worklist = tmp_path / "handoff" / "projection.json"
    plan = tmp_path / "handoff" / "plan.json"

    def no_fetch(*_args: object, **_kwargs: object) -> SupremeCourtClient:
        raise AssertionError("the projection fetches nothing")

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", no_fetch)
    emitted = runner.invoke(
        app,
        ["ocr-recover-petitions", "--emit-worklist", str(worklist), "--max-cases", "1"],
    )
    assert emitted.exit_code == 0, emitted.output
    assert "ocr-recover-petitions (dry-run): 2 scanned filing(s)" in emitted.output
    assert "worklist: 1 item(s), the apply's slice" in emitted.output
    assert [i.key for i in read_handoff(worklist, OcrWorklist).items] == ["scotus/1 petition"]

    binaries = tmp_path / "bin"
    binaries.mkdir()
    _fake_binary(binaries, "pdftoppm", "printf PNG")
    _fake_binary(binaries, "tesseract", "printf 'Recovered page text.'")
    monkeypatch.setenv("PATH", f"{binaries}{os.pathsep}{os.environ['PATH']}")
    pdf = _blank_pdf(12)

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
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    parsed = runner.invoke(
        app,
        ["ocr-recover-petitions", "--worklist", str(worklist), "--plan-out", str(plan)],
    )
    assert parsed.exit_code == 0, parsed.output

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    refused = runner.invoke(
        app,
        [
            "ocr-recover-petitions",
            *("--from-plan", str(plan), "--bind-worklist", str(worklist)),
            *("--max-cases", "2", "--apply"),
        ],
    )
    assert refused.exit_code == 1
    assert "cut for a bound of 1, not this dispatch's 2" in refused.output
    written = runner.invoke(
        app,
        [
            "ocr-recover-petitions",
            *("--from-plan", str(plan), "--bind-worklist", str(worklist)),
            *("--max-cases", "1", "--apply"),
        ],
    )
    assert written.exit_code == 0, written.output
    assert "Recovered page text" not in written.output
    ledger = json.loads(written.output.strip().splitlines()[-1])
    assert ledger["applied"] is True
    assert (ledger["candidates"], ledger["attempted"], ledger["remaining"]) == (2, 1, 1)
    assert "Recovered page text." in _documents(db, "scotus/1")[KIND_PETITION].text

    reread = runner.invoke(app, ["ocr-recover-petitions", "--probe=0"])
    assert reread.exit_code == 0, reread.output
    assert json.loads(reread.output.strip().splitlines()[-1])["candidates"] == 1


def test_the_cli_probe_parse_reports_each_items_status_and_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    item = _item("scotus/1")
    worklist = tmp_path / "worklist.json"
    write_handoff(worklist, _worklist(item, cap=3))

    class _Served(SupremeCourtClient):
        def __init__(self, **_kwargs: object) -> None:
            super().__init__(
                throttle_seconds=1.0,
                client=httpx.Client(
                    transport=httpx.MockTransport(lambda _r: httpx.Response(403)),
                    headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
                ),
                sleep=lambda _s: None,
            )

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", _Served)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = runner.invoke(
        app, ["ocr-recover-petitions", "--worklist", str(worklist), "--probe-only"]
    )
    assert result.exit_code == 0, result.output
    assert "probe scotus/1 petition: http-error (status 403, 0 bytes)" in result.output
    assert sorted(p.name for p in tmp_path.iterdir()) == ["worklist.json"]
