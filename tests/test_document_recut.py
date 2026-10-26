"""The bounded re-cut pass for filings stored under the plain head cut.

The pass re-fetches a stored petition, application or appendix and re-cuts it
with the fetching lanes' own extractor. These tests drive it over a mock
transport serving small PDFs, at a cap small enough that a few pages overflow
it: the stored rows are what the plain head cut made of the same bytes, which
is exactly the shape the class is.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import document_recut
from fedcourtsai.pipeline.document_recut import (
    EMPTY_AFTER_RECUT,
    HAS_CUT_NOTE,
    HEAD_CHANGED,
    NOT_A_RECUT_KIND,
    NOT_TRUNCATED,
    OCR_DERIVED,
    PAGES_CHANGED,
    RECUT_KINDS,
    SCOPE_ALL_LIVE,
    UNCHANGED,
    UNFETCHABLE_URL,
    UNREADABLE,
    RecutCandidate,
    estimated_candidate_seconds,
    exclusion_reason,
    recut_candidates,
    recut_documents,
)
from fedcourtsai.pipeline.documents import (
    APPENDIX_BEARING_KINDS,
    BIO_URL_JOIN,
    KIND_APPENDIX,
    KIND_APPLICATION,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
    ExtractedText,
    extract_filing_text,
    extract_pdf_text,
)
from fedcourtsai.supremecourt import SupremeCourtClient
from tests.test_documents import _pdf_pages
from tests.test_ocr_recovery import _client, _documents

runner = CliRunner()

_TODAY = date(2026, 10, 24)
_CAP = 1000

_QUESTION = (
    "QUESTION PRESENTED Whether the agency exceeded its statutory authority under "
    "the Act when it issued the rule. PARTIES TO THE PROCEEDING Acme Corp."
)
_QUESTION_TEXT = (
    "Whether the agency exceeded its statutory authority under the Act when it issued the rule."
)


def _pages(count: int = 6, *, front: str = _QUESTION) -> list[str]:
    """A filing's page texts: front matter, then argument pages past the cap."""
    return [front] + [f"Argument page {index} " * 25 for index in range(1, count + 1)]


def _url(case_id: str, kind: str = KIND_PETITION) -> str:
    return f"https://www.supremecourt.gov/{case_id.rsplit('/', 1)[-1]}-{kind}.pdf"


def _head_cut(
    case_id: str,
    pdf: bytes,
    *,
    kind: str = KIND_PETITION,
    url: str | None = None,
    ocr_derived: bool = False,
) -> corpus.CaseDocument:
    """The row the plain head cut stored for ``pdf`` — the class's shape."""
    extracted = extract_pdf_text(pdf, char_cap=_CAP)
    assert extracted.truncated
    return corpus.CaseDocument(
        case_id=case_id,
        kind=kind,
        url=url or _url(case_id, kind),
        entry_date="Jun 01 2026",
        fetched_at=date(2026, 6, 2),
        pages=extracted.pages,
        truncated=extracted.truncated,
        ocr_derived=ocr_derived,
        text=extracted.text,
    )


def _seed(
    corpus_root: Path,
    documents: list[corpus.CaseDocument],
    *,
    unqueued: frozenset[str] = frozenset(),
) -> Path:
    """A corpus holding ``documents``; every case live, and queued unless named."""
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=f"25-{index}",
                    last_live_polled=date(2026, 6, 2),
                    predict_queued_at=None if case_id in unqueued else date(2026, 6, 2),
                )
                for index, case_id in enumerate(sorted({d.case_id for d in documents}), start=1)
            ],
        )
        corpus.upsert_documents(conn, documents)
    return db


def _run(
    db: Path,
    served: dict[str, bytes],
    *,
    apply: bool,
    max_cases: int | None = None,
    status: dict[str, int] | None = None,
    **kwargs: object,
) -> document_recut.DocumentRecutResult:
    with corpus.connect(db) as conn, _client(served, status=status) as client:
        return recut_documents(
            conn,
            client=client,
            apply=apply,
            char_cap=_CAP,
            today=_TODAY,
            max_cases=max_cases,
            **kwargs,  # type: ignore[arg-type]
        )


# --- population ------------------------------------------------------------


def test_the_recut_kinds_are_the_appendix_bearing_ones_petition_first() -> None:
    assert set(RECUT_KINDS) == APPENDIX_BEARING_KINDS
    assert RECUT_KINDS[0] == KIND_PETITION


def test_every_exclusion_names_its_own_reason() -> None:
    pdf = _pdf_pages(_pages())
    row = _head_cut("scotus/1", pdf)
    assert exclusion_reason(row) is None
    assert (
        exclusion_reason(row.model_copy(update={"kind": KIND_BRIEF_IN_OPPOSITION}))
        == NOT_A_RECUT_KIND
    )
    assert exclusion_reason(row.model_copy(update={"truncated": False})) == NOT_TRUNCATED
    assert exclusion_reason(row.model_copy(update={"ocr_derived": True})) == OCR_DERIVED
    noted = row.model_copy(update={"text": row.text + "\n[pipeline note: 9 characters omitted]"})
    assert exclusion_reason(noted) == HAS_CUT_NOTE
    off_host = row.model_copy(update={"url": "https://example.com/a.pdf"})
    assert exclusion_reason(off_host) == UNFETCHABLE_URL
    joined = row.model_copy(update={"url": _url("scotus/1") + BIO_URL_JOIN + _url("scotus/2")})
    assert exclusion_reason(joined) == UNFETCHABLE_URL


def test_the_class_is_scoped_ordered_and_tallies_its_exclusions(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    db = _seed(
        tmp_path / "corpus",
        [
            _head_cut("scotus/1", pdf, kind=KIND_APPENDIX),
            _head_cut("scotus/1", pdf),
            _head_cut("scotus/2", pdf, kind=KIND_APPLICATION),
            _head_cut("scotus/3", pdf, ocr_derived=True),
            _head_cut("scotus/4", pdf),  # not queued: outside the default scope
        ],
        unqueued=frozenset({"scotus/4"}),
    )
    with corpus.connect(db) as conn:
        scan = recut_candidates(conn)
        wide = recut_candidates(conn, scope=SCOPE_ALL_LIVE)
    assert [c.key for c in scan.candidates] == [
        "scotus/1 petition",
        "scotus/1 appendix",
        "scotus/2 application",
    ]
    assert scan.cases_seen == 3 and scan.documents_seen == 4
    assert scan.excluded == {OCR_DERIVED: 1}
    assert [c.key for c in wide.candidates][-1] == "scotus/4 petition"
    assert wide.cases_seen == 4


def test_the_estimate_reads_the_stored_page_count() -> None:
    row = _head_cut("scotus/1", _pdf_pages(_pages()))
    candidate = RecutCandidate(document=row, stored_questions=None)
    assert estimated_candidate_seconds(candidate) == (
        document_recut.ESTIMATED_CANDIDATE_OVERHEAD_SECONDS
        + row.pages * document_recut.ESTIMATED_SECONDS_PER_PAGE
    )


# --- outcomes --------------------------------------------------------------


def test_the_dry_run_recuts_and_writes_nothing(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    db = _seed(tmp_path / "corpus", [stored])
    result = _run(db, {stored.url: pdf}, apply=False)
    assert result.applied is False and result.bound is None
    assert result.recut == 1 and result.remaining == 1
    assert result.outcomes_by_kind == {KIND_PETITION: {"recut": 1}}
    assert "notes=1" in result.recuts["scotus/1 petition"]
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored


def test_the_apply_writes_the_recut_row_and_it_leaves_the_class(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    db = _seed(tmp_path / "corpus", [stored])
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.applied is True and result.recut == 1 and result.remaining == 0
    written = _documents(db, "scotus/1")[KIND_PETITION]
    assert "[pipeline note:" in written.text and written.text != stored.text
    assert len(written.text) <= _CAP
    assert written.truncated is True and written.ocr_derived is False
    assert (written.url, written.entry_date, written.pages) == (
        stored.url,
        stored.entry_date,
        stored.pages,
    )
    assert written.fetched_at == _TODAY
    # The witness the workflow runs: the class re-walked holds what the apply left.
    with corpus.connect(db) as conn:
        assert recut_candidates(conn).candidates == ()


def test_a_link_serving_another_page_count_is_skipped(tmp_path: Path) -> None:
    stored = _head_cut("scotus/1", _pdf_pages(_pages(6)))
    db = _seed(tmp_path / "corpus", [stored])
    result = _run(db, {stored.url: _pdf_pages(_pages(9))}, apply=True, max_cases=5)
    assert result.pages_changed == 1 and result.recut == 0 and result.remaining == 1
    assert result.skipped == {"scotus/1 petition": f"{PAGES_CHANGED} (stored 7, served 10)"}
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored


def test_a_link_serving_another_filing_of_the_same_length_is_skipped(tmp_path: Path) -> None:
    stored = _head_cut("scotus/1", _pdf_pages(_pages(6)))
    db = _seed(tmp_path / "corpus", [stored])
    other = _pdf_pages(_pages(6, front="CORRECTED PETITION " + _QUESTION))
    result = _run(db, {stored.url: other}, apply=True, max_cases=5)
    assert result.head_changed == 1 and result.recut == 0
    assert result.skipped == {"scotus/1 petition": HEAD_CHANGED}
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored


def test_line_breaks_the_pdf_library_moved_are_the_same_filing() -> None:
    stored = "PETITION FOR A WRIT \n \nR\nOMAN MARTINEZ \nWashington, DC\n 20004 Argument"
    recut = "PETITION FOR A WRIT \n \n ROMAN MARTINEZ \nWashington, DC 20004 Argument more"
    assert document_recut._same_head(recut, stored)
    assert not document_recut._same_head("CORRECTED " + recut, stored)


def test_a_caption_glyph_the_pdf_library_reads_differently_is_the_same_filing() -> None:
    rule = "\u2014" * 4
    stored = f"No. 24-1\n{rule}\u00a8{rule}\nIN THE SUPREME COURT\u00cb RESPONDENT"
    recut = f"No. 24-1\n{rule}\u00a4{rule}\nIN THE SUPREME COURT\u00b8 RESPONDENT more"
    assert document_recut._same_head(recut, stored)
    assert not document_recut._same_head(recut.replace("24-1", "24-2"), stored)
    assert not document_recut._same_head(recut.replace("RESPONDENT", "PETITIONER"), stored)
    assert not document_recut._same_head(f"{rule}\u00a4{rule}", stored)


def test_bytes_that_do_not_parse_are_unreadable_not_another_filing(tmp_path: Path) -> None:
    stored = _head_cut("scotus/1", _pdf_pages(_pages(6)))
    db = _seed(tmp_path / "corpus", [stored])
    result = _run(db, {stored.url: b"%PDF-1.7 truncated"}, apply=True, max_cases=5)
    assert result.unreadable == 1 and result.pages_changed == 0 and result.recut == 0
    assert result.skipped["scotus/1 petition"].startswith(UNREADABLE)
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored


def test_an_extractor_that_raises_costs_only_its_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = _head_cut("scotus/1", _pdf_pages(_pages(6)))
    second = _head_cut("scotus/2", _pdf_pages(_pages(6)))
    db = _seed(tmp_path / "corpus", [first, second])
    real = extract_filing_text
    calls: list[int] = []

    def _flaky(data: bytes, **kwargs: object) -> object:
        calls.append(1)
        if len(calls) == 1:
            raise KeyError("/Root")
        return real(data, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(document_recut, "extract_filing_text", _flaky)
    served = {first.url: _pdf_pages(_pages(6)), second.url: _pdf_pages(_pages(6))}
    result = _run(db, served, apply=True, max_cases=5)
    assert result.unreadable == 1 and result.recut == 1
    assert result.skipped == {"scotus/1 petition": f"{UNREADABLE} (KeyError)"}


def test_a_recut_equal_to_the_stored_text_is_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    db = _seed(tmp_path / "corpus", [stored])
    monkeypatch.setattr(
        document_recut,
        "extract_filing_text",
        lambda _data, *, kind, char_cap: ExtractedText(
            text=stored.text, pages=stored.pages, truncated=True
        ),
    )
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.unchanged == 1 and result.recut == 0
    assert result.skipped == {"scotus/1 petition": UNCHANGED}
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored


def test_remaining_counts_a_written_row_that_stays_in_the_class(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`remaining` is read off the written rows, because the witness is exact.

    A re-cut leaves the class by carrying a cut note; one that somehow did not
    would still be in it on the re-walk, and a `remaining` that assumed every
    re-cut left would turn that into a reported write failure.
    """
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    db = _seed(tmp_path / "corpus", [stored])
    monkeypatch.setattr(
        document_recut,
        "extract_filing_text",
        lambda _data, *, kind, char_cap: ExtractedText(
            text=stored.text[:-1], pages=stored.pages, truncated=True
        ),
    )
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.recut == 1 and result.remaining == 1
    with corpus.connect(db) as conn:
        assert len(recut_candidates(conn).candidates) == result.remaining


def test_an_empty_recut_never_replaces_stored_text(tmp_path: Path) -> None:
    stored = _head_cut("scotus/1", _pdf_pages(_pages()))
    db = _seed(tmp_path / "corpus", [stored])
    blank = _pdf_pages([""] * stored.pages)
    result = _run(db, {stored.url: blank}, apply=True, max_cases=5)
    assert result.empty_after_recut == 1 and result.recut == 0
    assert result.skipped == {"scotus/1 petition": EMPTY_AFTER_RECUT}
    assert _documents(db, "scotus/1")[KIND_PETITION] == stored


def test_a_fetch_failure_writes_nothing_and_is_named(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    unserved = _head_cut("scotus/1", pdf)
    forbidden = _head_cut("scotus/2", pdf)
    db = _seed(tmp_path / "corpus", [unserved, forbidden])
    result = _run(db, {}, apply=True, max_cases=5, status={forbidden.url: 403})
    assert result.fetch_failed == {"http-403": 1, "not-served": 1}
    assert result.outcomes_by_kind == {KIND_PETITION: {"fetch-failed": 2}}
    assert result.skipped["scotus/1 petition"] == "fetch-failed (not-served)"
    assert result.remaining == 2
    assert _documents(db, "scotus/2")[KIND_PETITION] == forbidden


def test_the_slice_bound_and_deadline_leave_the_tail_unreached(tmp_path: Path) -> None:
    pdf = _pdf_pages(_pages())
    rows = [_head_cut(f"scotus/{n}", pdf) for n in (1, 2, 3, 4)]
    db = _seed(tmp_path / "corpus", rows)
    served = {row.url: pdf for row in rows}
    # 100 s of budget at a fixed clock admits the first candidate's estimate
    # only once, because the clock moves by that estimate after each fetch.
    clock = [0.0]

    def monotonic() -> float:
        clock[0] += 60.0
        return clock[0]

    result = _run(db, served, apply=True, max_cases=3, deadline=100.0, monotonic=monotonic)
    assert result.attempted == 1 and result.recut == 1
    assert result.unreached == ["scotus/2 petition", "scotus/3 petition"]
    assert result.outcomes_by_kind == {KIND_PETITION: {"recut": 1, "unreached": 2}}
    assert result.remaining == 3


def test_an_empty_slice_walks_the_class_and_fetches_nothing(tmp_path: Path) -> None:
    stored = _head_cut("scotus/1", _pdf_pages(_pages()))
    db = _seed(tmp_path / "corpus", [stored])

    def refuse(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("an empty slice fetched")

    client = SupremeCourtClient(
        throttle_seconds=1.0,
        client=httpx.Client(transport=httpx.MockTransport(refuse)),
        sleep=lambda _s: None,
    )
    with corpus.connect(db) as conn, client:
        result = recut_documents(
            conn, client=client, apply=True, char_cap=_CAP, today=_TODAY, max_cases=0
        )
    assert result.candidates == 1 and result.attempted == 0 and result.remaining == 1


def test_an_apply_without_its_bound_is_refused(tmp_path: Path) -> None:
    db = _seed(tmp_path / "corpus", [_head_cut("scotus/1", _pdf_pages(_pages()))])
    with pytest.raises(ValueError, match="slice bound"):
        _run(db, {}, apply=True)


# --- the questions-presented row --------------------------------------------


def _questions(case_id: str, text: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_QUESTIONS_PRESENTED,
        url=_url(case_id),
        entry_date="Jun 01 2026",
        fetched_at=date(2026, 6, 2),
        pages=0,
        text=text,
    )


def test_a_recut_that_keeps_the_front_matter_leaves_the_questions_row(tmp_path: Path) -> None:
    """The ordinary case: both cuts keep the front matter, so the section agrees.

    The stored row is deliberately *not* what the deriver reads today — the shape
    of a cutter change no back-fill has converged — and the re-cut leaves it
    alone, because converging it is the questions-presented back-fill's work.
    """
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    unconverged = _questions("scotus/1", "Whether the agency exceeded its authority. ii")
    db = _seed(tmp_path / "corpus", [stored, unconverged])
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.recut == 1 and result.questions_rederived == 0
    assert _documents(db, "scotus/1")[KIND_QUESTIONS_PRESENTED] == unconverged


def test_a_recut_that_moves_the_section_rewrites_the_questions_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Synthetic stored text opens unlike the served PDF; the head check is not
    # what these exercise.
    monkeypatch.setattr(document_recut, "HEAD_CHECK_CHARS", 0)
    pdf = _pdf_pages(_pages())
    # Stored text whose own derivation finds no heading at all: the re-cut's does.
    stored = _head_cut("scotus/1", pdf).model_copy(update={"text": "Argument only. " * 70})
    db = _seed(tmp_path / "corpus", [stored])
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.questions_rederived == 1
    assert "questions-presented=rederived" in result.recuts["scotus/1 petition"]
    questions = _documents(db, "scotus/1")[KIND_QUESTIONS_PRESENTED]
    assert questions.text == _QUESTION_TEXT and questions.fetched_at == _TODAY


def test_a_stored_row_a_cutter_change_left_behind_is_never_rewritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The re-cut moves the derivation, but the stored row is not the stored
    text's derivation either: that is the questions-presented back-fill's."""
    monkeypatch.setattr(document_recut, "HEAD_CHECK_CHARS", 0)
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf).model_copy(update={"text": "Argument only. " * 70})
    unconverged = _questions("scotus/1", "Whether the agency exceeded its authority. ii")
    db = _seed(tmp_path / "corpus", [stored, unconverged])
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.recut == 1 and result.questions_rederived == 0
    assert _documents(db, "scotus/1")[KIND_QUESTIONS_PRESENTED] == unconverged


def test_a_recut_never_empties_a_stored_question(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Synthetic stored text opens unlike the served PDF; the head check is not
    # what these exercise.
    monkeypatch.setattr(document_recut, "HEAD_CHECK_CHARS", 0)
    served = _pdf_pages(_pages(front="QUESTION PRESENTED PARTIES TO THE PROCEEDING Acme Corp."))
    stored = _head_cut("scotus/1", served).model_copy(
        update={"text": _QUESTION + " " + "Argument only. " * 60}
    )
    kept = _questions("scotus/1", _QUESTION_TEXT)
    db = _seed(tmp_path / "corpus", [stored, kept])
    result = _run(db, {stored.url: served}, apply=True, max_cases=5)
    assert result.recut == 1 and result.questions_rederived == 0
    assert _documents(db, "scotus/1")[KIND_QUESTIONS_PRESENTED] == kept


def test_only_a_petition_rederives_questions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Synthetic stored text opens unlike the served PDF; the head check is not
    # what these exercise.
    monkeypatch.setattr(document_recut, "HEAD_CHECK_CHARS", 0)
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf, kind=KIND_APPLICATION).model_copy(
        update={"text": "Argument only. " * 70}
    )
    db = _seed(tmp_path / "corpus", [stored])
    result = _run(db, {stored.url: pdf}, apply=True, max_cases=5)
    assert result.recut == 1 and result.questions_rederived == 0
    assert KIND_QUESTIONS_PRESENTED not in _documents(db, "scotus/1")


# --- the CLI ---------------------------------------------------------------


def _patch_client(monkeypatch: pytest.MonkeyPatch, served: dict[str, bytes]) -> None:
    def factory(**_kwargs: object) -> SupremeCourtClient:
        return _client(served)

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", factory)


def _small_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the CLI at this file's cap rather than the configured one."""
    real = document_recut.recut_documents

    def capped(*args: object, **kwargs: object) -> document_recut.DocumentRecutResult:
        kwargs["char_cap"] = _CAP
        return real(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr("fedcourtsai.cli.recut_documents", capped)


def test_the_cli_dry_run_prints_the_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    _seed(tmp_path / "corpus", [stored])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    _patch_client(monkeypatch, {stored.url: pdf})
    _small_cap(monkeypatch)
    result = runner.invoke(app, ["recut-documents", "--max-cases", "1"])
    assert result.exit_code == 0, result.output
    assert "recut-documents (dry-run, predict-relevant): 1 head-cut filing(s)" in result.output
    assert "would re-cut 1, 1 left in the class" in result.output
    assert "  petition: recut 1" in result.output
    assert "scotus/1 petition: WOULD RE-CUT pages=7" in result.output
    assert '"applied":false' in result.output.splitlines()[-1]


def test_the_cli_warns_when_a_whole_slice_is_residue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stored = _head_cut("scotus/1", _pdf_pages(_pages(6)))
    _seed(tmp_path / "corpus", [stored])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    _patch_client(monkeypatch, {stored.url: _pdf_pages(_pages(9))})
    _small_cap(monkeypatch)
    result = runner.invoke(app, ["recut-documents", "--max-cases", "1"])
    assert result.exit_code == 0, result.output
    assert "::warning::recut-documents: the whole slice was skipped" in result.output


def test_the_cli_apply_writes_and_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf = _pdf_pages(_pages())
    stored = _head_cut("scotus/1", pdf)
    db = _seed(tmp_path / "corpus", [stored])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    _patch_client(monkeypatch, {stored.url: pdf})
    _small_cap(monkeypatch)
    result = runner.invoke(app, ["recut-documents", "--apply", "--max-cases", "1", "--all-live"])
    assert result.exit_code == 0, result.output
    assert "(applied, all-live)" in result.output and "re-cut 1, 0 left" in result.output
    assert "[pipeline note:" in _documents(db, "scotus/1")[KIND_PETITION].text


def test_the_cli_refuses_an_apply_without_its_slice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(tmp_path / "corpus", [_head_cut("scotus/1", _pdf_pages(_pages()))])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["recut-documents", "--apply"])
    assert result.exit_code == 2
    assert "requires an explicit --max-cases" in result.output


@pytest.mark.parametrize("argv", [["--max-cases", "-1"], ["--deadline-seconds", "nan"]])
def test_the_cli_refuses_a_bound_that_is_not_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, argv: list[str]
) -> None:
    _seed(tmp_path / "corpus", [_head_cut("scotus/1", _pdf_pages(_pages()))])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["recut-documents", *argv])
    assert result.exit_code == 2


def test_the_cli_fails_loud_without_a_corpus(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["recut-documents"], env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")}
    )
    assert result.exit_code == 1
    assert "corpus database is missing" in result.output


def test_the_cli_refuses_a_corpus_whose_documents_it_cannot_read(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-1",
                    last_live_polled=date(2026, 6, 2),
                    predict_queued_at=date(2026, 6, 2),
                )
            ],
        )
    result = runner.invoke(app, ["recut-documents"], env={"FEDCOURTS_CORPUS_ROOT": str(root)})
    assert result.exit_code == 1
    assert "no stored documents" in result.output and "wrong blob" in result.output
