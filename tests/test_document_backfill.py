"""The bounded document back-fill for queued cases holding a document gap.

Nothing reaches supremecourt.gov here. The pass fetches through the real
:class:`SupremeCourtClient` over an ``httpx.MockTransport``, which is what keeps
the politeness posture — the browser UA, the throttle, the one retry — under
test rather than stubbed away, and the recorded request log is what proves the
dry run never asks for a PDF.

Three things worth stating about what is exercised: the primary arm of the
population predicate is **form-keyed**, so the tests that matter most there are
the ones where an application docket is measured against its application rather
than a petition it structurally never has; the merits arm is keyed on a granted
row whose respondent has *filed*, which is what separates a gap a fetch can
close from a case that is simply not briefed yet; and the ledger's two floors
have to stay apart from its losses, because a slice that clears its bound
without draining the class reads as a defect on any ledger that folds them
together.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus, supremecourt
from fedcourtsai.cli import app
from fedcourtsai.pipeline.document_backfill import (
    ESTIMATED_DOCKET_SECONDS,
    MODERN_LINK_TERM,
    backfill_documents,
    document_gaps,
    estimated_candidate_seconds,
    floor_probe_standing,
    is_predict_relevant,
)
from fedcourtsai.pipeline.documents import (
    KIND_APPLICATION,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_MERITS_BRIEF_PETITIONER,
    KIND_MERITS_BRIEF_RESPONDENT,
    KIND_MERITS_REPLY_PETITIONER,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
)
from fedcourtsai.supremecourt import SupremeCourtClient

runner = CliRunner()

_TODAY = date(2026, 9, 1)
_CHAR_CAP = 100_000

# A petition whose text is long enough that the extractor stores it rather than
# reporting an empty read, and which carries a questions-presented heading — so
# a recovered case exercises the derived row that lands beside the filing.
_PETITION_TEXT = (
    "QUESTION PRESENTED Whether the court of appeals erred in holding that the "
    "statute reaches conduct wholly outside the United States. PARTIES TO THE "
    "PROCEEDING Acme Corp."
)


def _pdf(text: str) -> bytes:
    """A one-page PDF drawing ``text`` (no parens), which the extractor reads."""
    stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        + b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    start = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    )
    return bytes(out)


def _petition_entry(*, url: str | None = "https://www.supremecourt.gov/pet.pdf") -> dict[str, Any]:
    """A cert docket's case-opening entry, with its filing link or without one.

    ``url=None`` is the Rule 34.6 shape: the Court docketed the filing and posted
    no PDF behind it, which is the ``no_link`` floor rather than a fetch failure.
    """
    links = [{"Description": "Petition", "DocumentUrl": url}] if url else []
    return {
        "Text": "Petition for a writ of certiorari filed.",
        "Date": "Jun 01 2026",
        "Links": links,
    }


def _application_entry(
    *, number: str = "26A203", url: str | None = "https://www.supremecourt.gov/app.pdf"
) -> dict[str, Any]:
    """An application docket's own submission entry, seeking substantive relief."""
    links = [{"Description": "Main Document", "DocumentUrl": url}] if url else []
    return {
        "Text": f"Application ({number}) for a stay of the mandate, submitted to Justice Kagan.",
        "Date": "Jun 01 2026",
        "Links": links,
    }


def _bio_entry(url: str) -> dict[str, Any]:
    """A respondent's brief in opposition — a kind the pass stores beside the primary one."""
    return {
        "Text": "Brief of respondent Acme Corp. in opposition filed.",
        "Date": "Jul 01 2026",
        "Links": [{"Description": "Main Document", "DocumentUrl": url}],
    }


def _payload(*entries: dict[str, Any]) -> dict[str, Any]:
    return {"ProceedingsandOrder": list(entries)}


def _row(case_id: str, docket_number: str, **fields: Any) -> corpus.CorpusRow:
    """A live-slice SCOTUS row, queued for prediction unless said otherwise."""
    base: dict[str, Any] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket_number,
        # `last_live_polled` is live-slice membership, which is the frame the
        # walk is taken over; the queue stamp is what makes the row predict-relevant.
        "last_live_polled": date(2026, 6, 2),
        "predict_queued_at": date(2026, 6, 2),
    }
    return corpus.CorpusRow.model_validate({**base, **fields})


def _document(case_id: str, kind: str, *, url: str = "https://x/stored.pdf") -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=kind,
        url=url,
        entry_date="Jun 01 2026",
        fetched_at=date(2026, 6, 2),
        pages=4,
        text="stored",
    )


@contextmanager
def _seeded(
    corpus_root: Path,
    rows: list[corpus.CorpusRow],
    documents: list[corpus.CaseDocument] | None = None,
) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        if documents:
            corpus.upsert_documents(conn, documents)
        conn.commit()
        yield conn


class _Requests:
    """Every URL the pass asked for, in order — the dry run's proof of restraint."""

    def __init__(self) -> None:
        self.urls: list[str] = []

    def pdfs(self) -> list[str]:
        return [url for url in self.urls if url.endswith(".pdf")]


def _client(
    dockets: dict[str, dict[str, Any]],
    *,
    pdfs: dict[str, bytes] | None = None,
    log: _Requests | None = None,
    errors: frozenset[str] = frozenset(),
    on_request: Callable[[str], None] | None = None,
) -> SupremeCourtClient:
    """The real client over a mock transport — same headers, same retry posture.

    ``dockets`` is keyed by the upstream slug (``"25-100"``, ``"26A203"``), which
    is what the pass builds from the stored docket number, so a test that
    mis-keys it gets the 404 branch rather than a silent pass. ``errors`` names
    slugs whose fetch fails transport-side, which is the branch counted apart
    from a 404.
    """
    served = pdfs or {}

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if log is not None:
            log.urls.append(url)
        if on_request is not None:
            on_request(url)
        slug = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if slug in errors:
            raise httpx.ConnectError("upstream unreachable")
        if url.endswith(".json"):
            return (
                httpx.Response(200, json=dockets[slug]) if slug in dockets else httpx.Response(404)
            )
        return httpx.Response(200, content=served[url]) if url in served else httpx.Response(404)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None)


def _run(
    conn: sqlite3.Connection,
    client: SupremeCourtClient,
    **kwargs: Any,
) -> Any:
    defaults: dict[str, Any] = {"apply": False, "char_cap": _CHAR_CAP, "today": _TODAY}
    return backfill_documents(conn, client=client, **{**defaults, **kwargs})


class _Clock:
    """A monotonic seam the test moves by hand.

    Wall clock is what the deadline is about, so the tests drive it directly
    rather than sleeping: `advance` is what a docket fetch and a filing download
    would have cost, and the pass reads the same clock it would read in production.
    """

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


# --- The population predicate ------------------------------------------------


def test_the_class_is_keyed_on_each_dockets_own_primary_document(tmp_path: Path) -> None:
    """An application docket is measured against its application, never a petition.

    The single most consequential choice in the predicate. A petition-keyed
    reading would put every application docket in the class permanently — an
    application docket structurally never holds a petition — so the pass would
    spend its whole bound every dispatch on cases it can never drain, and the
    application dockets that *are* recoverable would never be reached.
    """
    rows = [
        _row("scotus/1", "25-100"),  # cert form, no petition — in the class
        _row("scotus/2", "25-101"),  # cert form, holds its petition — out
        _row("scotus/3", "26A203"),  # application form, no application — in
        _row("scotus/4", "26A204"),  # application form, holds its application — out
    ]
    documents = [
        _document("scotus/2", KIND_PETITION),
        _document("scotus/4", KIND_APPLICATION),
        # The trap: an application docket holding a *petition* row would leave
        # the class under a petition-keyed reading and stay in it under a
        # form-keyed one, which is the correct answer — it holds no application.
        _document("scotus/3", KIND_PETITION),
        # And its mirror: a cert docket holding an application (an interim
        # application filed into a cert docket) still owes its petition.
        _document("scotus/1", KIND_APPLICATION),
    ]
    with _seeded(tmp_path / "corpus", rows, documents) as conn:
        scan = document_gaps(conn)
    assert [gap.case_id for gap in scan.gaps] == ["scotus/1", "scotus/3"]
    assert {gap.case_id: gap.kinds for gap in scan.gaps} == {
        "scotus/1": (KIND_PETITION,),
        "scotus/3": (KIND_APPLICATION,),
    }
    assert scan.cases_seen == 4
    assert scan.cases_with_documents == 4


def test_only_a_row_that_can_still_cost_a_cell_is_in_the_population(tmp_path: Path) -> None:
    """Queued or salience-selected — the selected arm is not redundant.

    A reserve-selected application has no distribution transition to be queued
    at and reaches the predict path through the selection sweep, so a
    queued-only predicate would drop exactly the rows the reserve funds.
    """
    rows = [
        _row("scotus/1", "25-100"),
        _row("scotus/2", "25-101", predict_queued_at=None, salience_selected=True),
        _row("scotus/3", "25-102", predict_queued_at=None),
    ]
    assert [is_predict_relevant(row) for row in rows] == [True, True, False]
    with _seeded(tmp_path / "corpus", rows) as conn:
        scan = document_gaps(conn)
    assert [gap.case_id for gap in scan.gaps] == ["scotus/1", "scotus/2"]
    # And the denominator is the population, not the frame: the unselected row
    # is never read for documents at all.
    assert scan.cases_seen == 2


def test_a_row_outside_the_live_slice_is_never_read(tmp_path: Path) -> None:
    """Documents reach the corpus on the live channel, so the walk frames on it."""
    rows = [_row("scotus/1", "25-100"), _row("scotus/2", "25-101", last_live_polled=None)]
    with _seeded(tmp_path / "corpus", rows) as conn:
        scan = document_gaps(conn)
    assert [gap.case_id for gap in scan.gaps] == ["scotus/1"]
    assert scan.cases_seen == 1


def test_an_unaddressable_row_is_counted_apart_and_never_enters_a_slice(tmp_path: Path) -> None:
    """A docket number no upstream endpoint serves cannot head the class forever.

    Counted rather than attempted: one at the head would consume the bound of
    every dispatch and nothing would ever drain behind it.
    """
    rows = [_row("scotus/1", "A-9999"), _row("scotus/2", "25-100")]
    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client({"25-100": _payload(_petition_entry())}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.unaddressable == 1
    assert result.candidates == 1
    assert list(result.selected) == ["scotus/2"]


# --- Floors, told apart from failures ----------------------------------------


def test_an_entry_with_no_filing_behind_it_is_the_paper_filing_floor(tmp_path: Path) -> None:
    """Rule 34.6: the Court docketed the filing and served no PDF. Nothing to fetch."""
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client({"25-100": _payload(_petition_entry(url=None))}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.no_link == 1
    assert result.no_entry == 0
    assert not result.no_entry_modern_cases
    # A floor is not a loss, and the ledger has to say so on both sides.
    assert result.docket_unserved == result.docket_errors == 0
    assert not sum(result.fetch_losses.values())
    # And it does not drain: the case is still in the class next dispatch.
    assert result.remaining == 1


def test_no_opening_entry_on_a_legacy_docket_is_a_floor_and_not_an_alarm(
    tmp_path: Path,
) -> None:
    """A pre-modern docket's proceedings list carries no document links at all."""
    legacy = f"{MODERN_LINK_TERM - 2000 - 3}-50"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", legacy)]) as conn,
        _client({legacy: _payload()}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.no_entry == 1
    assert result.no_link == 0
    assert not result.no_entry_modern_cases


def test_no_opening_entry_on_a_modern_docket_is_named_as_a_selector_regression(
    tmp_path: Path,
) -> None:
    """The one reading in this ledger that is a defect rather than a floor.

    A docket whose filing the selector should have an arm for, matching no
    entry, is a filing shape the selector cannot see — the class this pass
    exists to stop producing rather than to absorb. Named, not counted, so the
    cases can be read off the ledger and the arm widened.
    """
    modern = f"{MODERN_LINK_TERM - 2000 + 1}-50"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", modern)]) as conn,
        _client({modern: _payload()}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.no_entry == 1
    assert result.no_entry_modern_cases == ["scotus/1"]


def test_a_docket_upstream_serves_nothing_for_is_a_loss_not_a_floor(tmp_path: Path) -> None:
    """404 on the docket JSON: the row is addressable, upstream has nothing there."""
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client({}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.docket_unserved == 1
    assert result.no_link == result.no_entry == 0


def test_a_transport_failure_is_counted_apart_from_a_404(tmp_path: Path) -> None:
    """The repairs differ: a transport failure is worth re-attempting, a 404 is not."""
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client({}, errors=frozenset({"25-100"})) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.docket_errors == 1
    assert result.docket_unserved == 0


# --- The dry run --------------------------------------------------------------


def test_the_dry_run_fetches_the_docket_and_never_a_filing(tmp_path: Path) -> None:
    """The whole diagnostic, and the whole restraint.

    Running selection over a freshly served payload is what separates a case
    with a link waiting for it from one at a floor — so the docket GET is not
    optional. Downloading what selection nominated is, and a dry run that did it
    would spend the apply's budget without the apply's approval.
    """
    log = _Requests()
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client(
            {"25-100": _payload(_petition_entry())},
            pdfs={"https://www.supremecourt.gov/pet.pdf": _pdf(_PETITION_TEXT)},
            log=log,
        ) as client,
    ):
        result = _run(conn, client, max_cases=5)
        stored = corpus.documents_for_case(conn, "scotus/1")
    assert log.urls == ["https://www.supremecourt.gov/rss/cases/JSON/25-100.json"]
    assert not log.pdfs()
    assert not stored
    assert not result.applied
    assert result.selected == {"scotus/1": [KIND_PETITION]}
    assert not result.documents and not result.stored


def test_the_dry_run_takes_a_slice_too(tmp_path: Path) -> None:
    """It spends one paced round trip per candidate, so it is bounded on the same terms."""
    rows = [_row(f"scotus/{n}", f"25-10{n}") for n in range(4)]
    dockets = {f"25-10{n}": _payload(_petition_entry()) for n in range(4)}
    log = _Requests()
    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client(dockets, log=log) as client,
    ):
        result = _run(conn, client, max_cases=2)
    assert result.bound == 2
    assert result.attempted == 2
    assert result.candidates == 4
    assert len(log.urls) == 2


# --- The apply ----------------------------------------------------------------


def test_the_apply_provisions_the_case_through_the_pollers_own_path(tmp_path: Path) -> None:
    """A recovered case is provisioned exactly as one provisioned at its trigger was.

    Which means the opposition brief and the derived questions-presented row
    land with the petition — the pass calls the same `fetch_case_documents` the
    live poller does, so the ledger counts every kind it produced rather than
    only the one whose absence put the case in the class.
    """
    petition_url = "https://www.supremecourt.gov/pet.pdf"
    bio_url = "https://www.supremecourt.gov/bio.pdf"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client(
            {"25-100": _payload(_petition_entry(), _bio_entry(bio_url))},
            pdfs={petition_url: _pdf(_PETITION_TEXT), bio_url: _pdf("Respondent opposes.")},
        ) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind: d for d in corpus.documents_for_case(conn, "scotus/1")}
    assert result.applied
    assert set(stored) == {KIND_PETITION, KIND_BRIEF_IN_OPPOSITION, KIND_QUESTIONS_PRESENTED}
    assert stored[KIND_PETITION].url == petition_url
    assert result.documents["scotus/1"] == sorted(stored)
    assert result.stored[KIND_PETITION] == 1
    # The class is keyed on the primary document, so the case has left it.
    assert result.remaining == 0
    assert not result.selected


def test_an_application_docket_is_recovered_against_its_own_filing(tmp_path: Path) -> None:
    """The other half of the form-keyed predicate, end to end."""
    url = "https://www.supremecourt.gov/app.pdf"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "26A203")]) as conn,
        _client(
            {"26A203": _payload(_application_entry())},
            pdfs={url: _pdf("Applicant seeks a stay of the mandate.")},
        ) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind for d in corpus.documents_for_case(conn, "scotus/1")}
    assert stored == {KIND_APPLICATION}
    assert result.documents == {"scotus/1": [KIND_APPLICATION]}
    assert result.remaining == 0


def test_a_case_that_gained_only_a_secondary_kind_is_not_a_recovery(tmp_path: Path) -> None:
    """A stored BIO does not drain a class keyed on the primary document.

    The one shape of an apply that reads like a recovery on a per-case line and
    is not one: the petition link *was* selected, its PDF did not serve, and the
    opposition brief landed beside it. `documents` names the case, `recovered`
    does not, and `remaining` is the complement of `recovered` — a headline taken
    off `documents` would contradict the number printed next to it. The fetch
    loss is attributed too, which is the ledger's own claim about this path.
    """
    petition_url = "https://www.supremecourt.gov/pet.pdf"
    bio_url = "https://www.supremecourt.gov/bio.pdf"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        # The petition entry carries its link, so selection nominates it — but
        # only the BIO is served, which is the fetch loss rather than a floor.
        _client(
            {"25-100": _payload(_petition_entry(url=petition_url), _bio_entry(bio_url))},
            pdfs={bio_url: _pdf("Respondent opposes.")},
        ) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind for d in corpus.documents_for_case(conn, "scotus/1")}
    assert stored == {KIND_BRIEF_IN_OPPOSITION}
    assert result.documents == {"scotus/1": [KIND_BRIEF_IN_OPPOSITION]}
    assert result.recovered == 0
    assert result.remaining == 1
    # Neither floor: the docket nominated a link, so this is a loss and has to be
    # attributable as one.
    assert result.no_link == result.no_entry == 0
    assert result.fetch_losses["unavailable"] == 1


def test_a_docket_that_nominated_nothing_is_a_floor_and_fetches_nothing(
    tmp_path: Path,
) -> None:
    """The neighbouring shape, told apart: no link selected means no fetch at all."""
    bio_url = "https://www.supremecourt.gov/bio.pdf"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client(
            {"25-100": _payload(_petition_entry(url=None), _bio_entry(bio_url))},
            pdfs={bio_url: _pdf("Respondent opposes.")},
        ) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind for d in corpus.documents_for_case(conn, "scotus/1")}
    assert result.no_link == 1
    assert not stored
    assert result.recovered == 0
    # Nothing was fetched and nothing recovered, and the candidate still left the
    # class: an applied floor is stamped against the docket it was read on, so
    # `remaining` nets it out exactly as it nets out a recovery.
    assert result.floors_stamped == 1
    assert result.remaining == 0


# --- The floor probe ---------------------------------------------------------


def _floored(tmp_path: Path, **row_fields: Any) -> tuple[Path, str]:
    """Apply one slice over a single candidate whose docket posts no link.

    Returns the corpus root and the case's stored probe stamp, so a caller can
    re-open the same corpus and scan it again. The docket carries the petition
    entry with nothing behind it, which is the `no_link` floor.
    """
    corpus_root = tmp_path / "corpus"
    with (
        _seeded(corpus_root, [_row("scotus/1", "25-100", **row_fields)]) as conn,
        _client({"25-100": _payload(_petition_entry(url=None))}) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        assert result.no_link == 1
        assert result.floors_stamped == 1
        stamped = corpus.get_row(conn, "scotus/1")
    assert stamped is not None and stamped.document_floor_probed_at == _TODAY
    return corpus_root, "scotus/1"


def test_an_applied_floor_is_held_out_of_the_next_scan(tmp_path: Path) -> None:
    """The defect this probe exists for: a floor re-walked every dispatch.

    The second scan must not merely decline to fetch — it must not *reach* the
    candidate at all, because reaching it is the paced docket GET the class
    cannot afford once its floors outnumber its recoverable head.
    """
    corpus_root, _ = _floored(tmp_path)
    log = _Requests()
    with (
        corpus.connect(corpus.corpus_db_path(corpus_root)) as conn,
        _client({"25-100": _payload(_petition_entry(url=None))}, log=log) as client,
    ):
        again = _run(conn, client, max_cases=5)
    assert again.candidates == 0
    assert again.standing_floors == 1
    # The row still holds its gap — the exclusion is about what a slice spends
    # on, not about the case having been repaired.
    assert again.cases_seen == 1
    assert not log.urls


def test_a_polled_docket_returns_its_floored_candidate_to_the_class(tmp_path: Path) -> None:
    """The exclusion lasts a docket version, not forever.

    A live poll after the probe is the corpus saying the docket was read again,
    so whatever the floor was read off may have moved and the candidate is owed
    another look.
    """
    corpus_root, case_id = _floored(tmp_path)
    url = "https://www.supremecourt.gov/pet.pdf"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        stored = corpus.get_row(conn, case_id)
        assert stored is not None
        corpus.upsert_rows(conn, [stored.model_copy(update={"last_live_polled": date(2026, 9, 8)})])
        conn.commit()
    with (
        corpus.connect(corpus.corpus_db_path(corpus_root)) as conn,
        _client(
            {"25-100": _payload(_petition_entry(url=url))},
            pdfs={url: _pdf("The petition presents one question.")},
        ) as client,
    ):
        again = _run(conn, client, apply=True, max_cases=5)
        recovered = {d.kind for d in corpus.documents_for_case(conn, case_id)}
    assert again.candidates == 1
    assert again.standing_floors == 0
    assert again.recovered == 1
    assert recovered == {KIND_PETITION}


def test_a_recoverable_candidate_is_never_stamped(tmp_path: Path) -> None:
    """Only a floor is stamped: a case that gained its filing left on its own."""
    url = "https://www.supremecourt.gov/pet.pdf"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client(
            {"25-100": _payload(_petition_entry(url=url))},
            pdfs={url: _pdf("The petition presents one question.")},
        ) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        row = corpus.get_row(conn, "scotus/1")
    assert result.recovered == 1
    assert result.floors_stamped == 0
    assert row is not None and row.document_floor_probed_at is None


def test_a_partly_recovered_candidate_is_not_stamped(tmp_path: Path) -> None:
    """A candidate that stored something is not at a floor, however much it owes.

    The merits arm is where the two readings diverge: this docket serves one of
    the two briefs, so the case is a write and not a recovery — and stamping it
    would hold a case with a fetchable link left on it out of the class.
    """
    url = "https://www.supremecourt.gov/merits-pet.pdf"
    with (
        _seeded(tmp_path / "corpus", [_granted_row("scotus/1", "25-100")]) as conn,
        _client(
            {"25-100": _payload(_grant_entry(), _merits_entry("Brief of petitioner", url))},
            pdfs={url: _pdf("Petitioner's brief on the merits.")},
        ) as client,
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        row = corpus.get_row(conn, "scotus/1")
    assert result.recovered == 0
    assert result.documents == {"scotus/1": [KIND_MERITS_BRIEF_PETITIONER]}
    assert result.floors_stamped == 0
    assert row is not None and row.document_floor_probed_at is None
    # Still in the class, still at the head of the next slice.
    assert result.remaining == 1


def test_a_dry_run_reads_a_floor_and_stamps_nothing(tmp_path: Path) -> None:
    """The stamp is an apply's write. A dry run's would never be pushed."""
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client({"25-100": _payload(_petition_entry(url=None))}) as client,
    ):
        result = _run(conn, client, max_cases=5)
        row = corpus.get_row(conn, "scotus/1")
    assert result.no_link == 1
    assert result.floors_stamped == 0
    assert result.remaining == 1
    assert row is not None and row.document_floor_probed_at is None


def test_the_ledger_splits_the_class_between_walked_and_held_out(tmp_path: Path) -> None:
    """`candidates + standing_floors` is the addressable gap class, on one ledger.

    Two rows hold the same gap; one was floored on the docket the corpus still
    holds and one has been polled since. A slice spends on the second, and the
    first is still reported.
    """
    rows = [
        _row("scotus/1", "25-100", document_floor_probed_at=date(2026, 8, 1)),
        _row("scotus/2", "25-101", document_floor_probed_at=date(2026, 5, 1)),
    ]
    log = _Requests()
    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client({"25-101": _payload(_petition_entry(url=None))}, log=log) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.cases_seen == 2
    assert result.candidates == 1
    assert result.standing_floors == 1
    assert result.attempted == 1
    assert result.no_link == 1
    # One docket GET, for the one candidate the class still admits.
    assert len(log.urls) == 1


def test_a_standing_probe_leaves_the_walk_order_alone(tmp_path: Path) -> None:
    """Exclusion, not re-ordering: what remains is still in `case_id` order."""
    rows = [
        _row("scotus/1", "25-100"),
        _row("scotus/2", "25-101", document_floor_probed_at=date(2026, 8, 1)),
        _row("scotus/3", "25-102"),
    ]
    with _seeded(tmp_path / "corpus", rows) as conn:
        scan = document_gaps(conn)
    assert [gap.case_id for gap in scan.gaps] == ["scotus/1", "scotus/3"]
    assert scan.standing_floors == 1


def test_the_probe_stands_only_against_the_docket_it_was_read_on() -> None:
    """The predicate itself, at each of its edges.

    The unstamped-live-poll arm is the one the lane's witness silently depends
    on: a stamped row reading as a candidate again would leave the apply's
    `remaining` short of the walk-only re-read and fail the job. It cannot arise
    today because the walk's population filter *is* that column being set, so
    the assertion is here to trip a test rather than a red job if that ever
    changes.
    """
    polled = date(2026, 8, 1)
    assert not floor_probe_standing(_row("scotus/1", "25-100", last_live_polled=polled))
    assert floor_probe_standing(
        _row("scotus/1", "25-100", last_live_polled=polled, document_floor_probed_at=polled)
    )
    assert not floor_probe_standing(
        _row(
            "scotus/1",
            "25-100",
            last_live_polled=polled,
            document_floor_probed_at=date(2026, 7, 31),
        )
    )
    assert not floor_probe_standing(
        _row("scotus/1", "25-100", last_live_polled=None, document_floor_probed_at=polled)
    )


def test_an_applies_remaining_equals_the_walk_only_re_read(tmp_path: Path) -> None:
    """The lane's witness, pinned here: `remaining` is what the next scan sees.

    The run-repair step re-reads the class on an empty slice after every apply
    and fails the job unless the count matches the ledger's `remaining`, because
    a content-store write that silently failed would leave a "recovered" case in
    the class. A stamped floor leaves the class exactly as a recovery does, so
    `remaining` has to net out both or the witness fires on a healthy run. The
    slice below does one of each and leaves a third candidate untouched.
    """
    url = "https://www.supremecourt.gov/pet.pdf"
    rows = [
        _row("scotus/1", "25-100"),  # recoverable
        _row("scotus/2", "25-101"),  # at the no_link floor
        _row("scotus/3", "25-102"),  # outside the bound
    ]
    corpus_root = tmp_path / "corpus"
    with (
        _seeded(corpus_root, rows) as conn,
        _client(
            {
                "25-100": _payload(_petition_entry(url=url)),
                "25-101": _payload(_petition_entry(url=None)),
            },
            pdfs={url: _pdf("The petition presents one question.")},
        ) as client,
    ):
        applied = _run(conn, client, apply=True, max_cases=2)
    assert applied.recovered == 1
    assert applied.floors_stamped == 1
    with (
        corpus.connect(corpus.corpus_db_path(corpus_root)) as conn,
        _client({}) as client,
    ):
        witness = _run(conn, client, max_cases=0)
    assert witness.candidates == applied.remaining == 1
    assert witness.standing_floors == 1


def test_the_floor_stamp_does_not_rewrite_the_stored_case_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The stamp is a column write, and under the split that is load-bearing.

    The pass reads its population off the payload-free index, where the opinion
    body is stripped and the store's `case.json` holds it. Upserting such a row
    back to stamp it would re-mirror a body-less `case.json` over the stored one
    — deleting the body while `has_opinion` stays latched — on a class that is
    granted and decided, which is exactly where the enrichment lands bodies.
    """
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    store = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(store)
    row = _row("scotus/1", "25-100", opinion_text="THE OPINION BODY")
    with (
        _seeded(tmp_path / "corpus", [row]) as conn,
        _client({"25-100": _payload(_petition_entry(url=None))}) as client,
    ):
        assert corpus.get_row(conn, "scotus/1") is not None
        assert _run(conn, client, apply=True, max_cases=5).floors_stamped == 1
        stamped = corpus.get_row(conn, "scotus/1")
    # The index carries the stamp — it is the system of record for the column.
    assert stamped is not None and stamped.document_floor_probed_at == _TODAY
    # And the store still serves the body the index cannot.
    assert casestore.read_opinion_text(store, "scotus/1") == "THE OPINION BODY"
    mirrored = json.loads(store.objects[casestore.case_key("scotus/1")])
    assert mirrored["opinion_text"] == "THE OPINION BODY"


def test_a_floor_the_alarm_fired_on_is_never_stamped(tmp_path: Path) -> None:
    """A floor this pass may itself be the cause of is not recorded as one.

    A missing kind the selector matched no entry for, on a docket modern enough
    to carry links, is the selector's blind spot rather than the docket's last
    word — and it is the shape an upstream payload that changed or degraded
    would take across a whole slice. Stamping it would bank an exclusion over a
    defect on our side, so the candidate keeps its place and widening the
    selector is enough to recover it.
    """
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", f"{MODERN_LINK_TERM - 1999}-100")]) as conn,
        _client({f"{MODERN_LINK_TERM - 1999}-100": _payload(_bio_entry("https://x/bio.pdf"))}) as (
            client
        ),
    ):
        result = _run(conn, client, apply=True, max_cases=5)
        row = corpus.get_row(conn, "scotus/1")
    assert result.no_entry_modern_cases == ["scotus/1"]
    assert result.no_entry == 1
    assert result.floors_stamped == 0
    assert row is not None and row.document_floor_probed_at is None
    # Still in the class, so a widened selector reaches it next dispatch.
    assert result.remaining == 1


def test_the_apply_is_written_per_case_as_it_goes(tmp_path: Path) -> None:
    """A slice killed mid-way has banked what it already recovered.

    The claim is about *when* the write happens, so the run has to actually die
    between two candidates rather than merely fail one of them: a batched write
    would pass any test the pass returns normally from. The second candidate's
    fetch raises something the pass does not catch, and the first case's
    documents must still be in the corpus — under the corpus split the per-case
    content-store write is itself the durable one.
    """
    rows = [_row("scotus/1", "25-100"), _row("scotus/2", "25-101")]
    url = "https://www.supremecourt.gov/pet.pdf"

    def _die_on_the_second(fetched: str) -> None:
        if fetched.endswith("25-101.json"):
            raise KeyboardInterrupt("the step's cap, mid-slice")

    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client(
            {"25-100": _payload(_petition_entry()), "25-101": _payload(_petition_entry())},
            pdfs={url: _pdf(_PETITION_TEXT)},
            on_request=_die_on_the_second,
        ) as client,
        pytest.raises(KeyboardInterrupt),
    ):
        _run(conn, client, apply=True, max_cases=5)
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        first = {d.kind for d in corpus.documents_for_case(conn, "scotus/1")}
    assert KIND_PETITION in first


def test_the_apply_is_idempotent_against_what_is_already_stored(tmp_path: Path) -> None:
    """A second slice over a recovered case re-fetches nothing and stores nothing new."""
    url = "https://www.supremecourt.gov/pet.pdf"
    dockets = {"25-100": _payload(_petition_entry())}
    pdfs = {url: _pdf(_PETITION_TEXT)}
    with _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn:
        with _client(dockets, pdfs=pdfs) as client:
            _run(conn, client, apply=True, max_cases=5)
        before = {d.kind: d.text for d in corpus.documents_for_case(conn, "scotus/1")}
        log = _Requests()
        with _client(dockets, pdfs=pdfs, log=log) as client:
            again = _run(conn, client, apply=True, max_cases=5)
        after = {d.kind: d.text for d in corpus.documents_for_case(conn, "scotus/1")}
    assert before == after
    # The case left the class at the first slice, so the second never even
    # reaches its docket.
    assert again.candidates == 0
    assert not log.urls


def test_an_apply_with_no_slice_is_refused_and_fetches_nothing(tmp_path: Path) -> None:
    """A bound is the only thing between this pass and an unbounded fetch campaign.

    Reported as a ledger field rather than only as an exit code, so a witness
    reading the summary sees the refusal instead of an empty pass.
    """
    log = _Requests()
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client({"25-100": _payload(_petition_entry())}, log=log) as client,
    ):
        result = _run(conn, client, apply=True)
    assert result.refused
    assert not result.applied
    assert not log.urls
    assert result.cases_seen == 0


# --- The slice deadline -------------------------------------------------------


def test_the_deadline_declines_a_candidate_the_budget_will_not_hold(tmp_path: Path) -> None:
    """Unreached, not failed: nothing fetched, nothing written, first next dispatch."""
    rows = [_row(f"scotus/{n}", f"25-10{n}") for n in range(3)]
    dockets = {f"25-10{n}": _payload(_petition_entry()) for n in range(3)}
    clock = _Clock()
    log = _Requests()
    estimate = estimated_candidate_seconds(apply=False)
    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client(dockets, log=log, on_request=lambda _u: clock.advance(estimate)) as client,
    ):
        result = _run(conn, client, max_cases=3, deadline=estimate * 2, monotonic=clock)
    assert result.attempted == 2
    assert result.unreached == ["scotus/2"]
    assert len(log.urls) == 2


def test_the_deadline_stops_the_slice_rather_than_skipping_ahead(tmp_path: Path) -> None:
    """Declining in order is what puts the declined candidates at the head of the next.

    The class is in `case_id` order and every candidate costs the same estimate,
    so skipping ahead would buy nothing and lose the ordering that makes a
    bounded slice self-advancing.
    """
    rows = [_row(f"scotus/{n}", f"25-10{n}") for n in range(4)]
    dockets = {f"25-10{n}": _payload(_petition_entry()) for n in range(4)}
    clock = _Clock()
    estimate = estimated_candidate_seconds(apply=False)
    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client(dockets, on_request=lambda _u: clock.advance(estimate)) as client,
    ):
        result = _run(conn, client, max_cases=4, deadline=estimate, monotonic=clock)
    assert result.attempted == 1
    assert result.unreached == ["scotus/1", "scotus/2", "scotus/3"]


def test_a_candidate_already_started_finishes_past_the_deadline(tmp_path: Path) -> None:
    """The deadline is the last moment work may begin, not the moment it stops."""
    clock = _Clock()
    url = "https://www.supremecourt.gov/pet.pdf"
    with (
        _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]) as conn,
        _client(
            {"25-100": _payload(_petition_entry())},
            pdfs={url: _pdf(_PETITION_TEXT)},
            on_request=lambda _u: clock.advance(10_000.0),
        ) as client,
    ):
        result = _run(
            conn,
            client,
            apply=True,
            max_cases=1,
            deadline=estimated_candidate_seconds(apply=True),
            monotonic=clock,
        )
        stored = {d.kind for d in corpus.documents_for_case(conn, "scotus/1")}
    assert result.attempted == 1
    assert not result.unreached
    assert KIND_PETITION in stored


def test_the_estimate_charges_a_dry_run_for_the_docket_alone(tmp_path: Path) -> None:
    """It fetches no filings, so charging it for them would decline candidates it could run."""
    assert estimated_candidate_seconds(apply=False) == ESTIMATED_DOCKET_SECONDS
    assert estimated_candidate_seconds(apply=True) > estimated_candidate_seconds(apply=False)


# --- The denominators ---------------------------------------------------------


def test_the_ledger_carries_both_readings_of_an_unreadable_store(tmp_path: Path) -> None:
    """Zero candidates and every-row-a-candidate are the two ways a store can lie.

    `cases_seen` is the denominator a caller refuses on — zero means the
    population could not be read rather than that the class is empty — and
    `cases_with_documents` is the opposite degradation, where a store serving no
    documents makes every row in the population look like a gap.
    """
    rows = [_row("scotus/1", "25-100"), _row("scotus/2", "25-101")]
    with _seeded(tmp_path / "corpus", rows, [_document("scotus/2", KIND_PETITION)]) as conn:
        scan = document_gaps(conn)
    assert scan.cases_seen == 2
    assert scan.cases_with_documents == 1
    with _seeded(tmp_path / "corpus2", []) as conn:
        empty = document_gaps(conn)
    assert empty.cases_seen == 0 and not empty.gaps


# --- The command surface ------------------------------------------------------


def _cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *args: str) -> Any:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return runner.invoke(app, ["backfill-documents", *args])


def test_cli_refuses_an_apply_with_no_slice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _cli(tmp_path, monkeypatch, "--apply")
    assert result.exit_code == 2
    assert "requires an explicit --max-cases" in result.output


@pytest.mark.parametrize("seconds", ["-1", "nan", "inf"])
def test_cli_refuses_a_deadline_that_is_not_a_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, seconds: str
) -> None:
    """`nan` compares false against every estimate and `inf` never runs out.

    Either would *disable* the deadline while reading as one that was set, which
    is the failure the refusal exists for — and the refusal names this command,
    since more than one deadlined pass reads its budget through the same helper.
    """
    result = _cli(tmp_path, monkeypatch, "--deadline-seconds", seconds)
    assert result.exit_code == 2
    assert "backfill-documents: --deadline-seconds must be a finite" in result.output


def test_cli_refuses_a_negative_slice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A slice is `candidates[:n]`, and Python reads a negative n from the other end.

    `--max-cases -5` would take *every candidate but the last five* — a nearly
    unbounded fetch campaign wearing the argument that exists to prevent one.
    Zero is legitimate and stays so: an empty slice that walks and fetches nothing.
    """
    result = _cli(tmp_path, monkeypatch, "--max-cases", "-5")
    assert result.exit_code == 2
    assert "backfill-documents: --max-cases must be zero or a positive" in result.output


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _cli(tmp_path, monkeypatch)
    assert result.exit_code == 1
    assert "corpus database is missing" in result.output


def test_cli_refuses_a_blob_with_no_predict_relevant_population(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A zero denominator is the wrong blob, not a converged class."""
    with _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100", predict_queued_at=None)]):
        pass
    result = _cli(tmp_path, monkeypatch)
    assert result.exit_code == 1
    assert "no predict-relevant live-slice rows" in result.output


def test_cli_an_empty_slice_walks_the_class_and_fetches_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--max-cases 0` is the free reading, and the apply's own write witness.

    It has to reach the ledger without a round trip, because the step reads its
    convergence verdict off it immediately after a slice that already spent the
    budget.
    """
    with _seeded(tmp_path / "corpus", [_row("scotus/1", "25-100")]):
        pass

    def _refuse(*_a: object, **_k: object) -> None:
        raise AssertionError("the walk-only reading must not construct a client that fetches")

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient.get_docket", _refuse)
    result = _cli(tmp_path, monkeypatch, "--max-cases", "0")
    assert result.exit_code == 0
    assert '"candidates":1' in result.output
    assert '"attempted":0' in result.output


# --- The merits arm of the gap class -----------------------------------------


def _grant_entry(date_: str = "Apr 06 2026") -> dict[str, Any]:
    """The cert grant in the Court's own words — what dates the merits stage."""
    return {"Text": "Petition GRANTED.", "Date": date_, "Links": []}


def _merits_entry(text: str, url: str | None, *, date_: str = "Jun 01 2026") -> dict[str, Any]:
    """A post-grant merits filing, with its `Main Document` link or without one."""
    links = [{"Description": "Main Document", "DocumentUrl": url}] if url else []
    return {"Text": text, "Date": date_, "Links": links}


def _granted_row(case_id: str, docket_number: str, **fields: Any) -> corpus.CorpusRow:
    """A granted row whose respondent has filed on the merits — the merits arm's shape."""
    return _row(
        case_id,
        docket_number,
        date_cert_granted=date(2026, 4, 6),
        merits_brief_filed=date(2026, 7, 13),
        **fields,
    )


def test_a_granted_briefed_row_owes_its_merits_briefs(tmp_path: Path) -> None:
    """Holding the petition is no longer leaving the class on a granted docket."""
    rows = [
        _granted_row("scotus/1", "25-100"),  # holds its petition, owes both briefs
        _row("scotus/2", "25-101"),  # ungranted, holds its petition — out
        _granted_row("scotus/3", "25-102"),  # owes the petition *and* both briefs
    ]
    documents = [
        _document("scotus/1", KIND_PETITION),
        _document("scotus/2", KIND_PETITION),
    ]
    with _seeded(tmp_path / "corpus", rows, documents) as conn:
        scan = document_gaps(conn)
    assert {gap.case_id: gap.kinds for gap in scan.gaps} == {
        "scotus/1": (KIND_MERITS_BRIEF_PETITIONER, KIND_MERITS_BRIEF_RESPONDENT),
        "scotus/3": (
            KIND_PETITION,
            KIND_MERITS_BRIEF_PETITIONER,
            KIND_MERITS_BRIEF_RESPONDENT,
        ),
    }
    assert [gap.merits for gap in scan.gaps] == [True, True]


def test_a_granted_row_with_no_briefing_dated_on_it_is_not_in_the_merits_arm(
    tmp_path: Path,
) -> None:
    """Granted-and-briefed, not granted alone — which is what makes the arm drain.

    A granted docket whose respondent has not filed has nothing for this route to
    fetch; it is a live case the selection sweep provisions at its next pass. A
    granted-alone predicate would park it in the class for as long as the row
    lives and spend the bound on it every dispatch.
    """
    rows = [
        _row("scotus/1", "25-100", date_cert_granted=date(2026, 4, 6)),
        _granted_row("scotus/2", "25-101"),
    ]
    documents = [_document("scotus/1", KIND_PETITION), _document("scotus/2", KIND_PETITION)]
    with _seeded(tmp_path / "corpus", rows, documents) as conn:
        scan = document_gaps(conn)
    assert [gap.case_id for gap in scan.gaps] == ["scotus/2"]


def test_a_missing_reply_is_not_a_gap(tmp_path: Path) -> None:
    """Not every granted case is replied to, so an absent reply is the docket's shape.

    Keying the class on one would hold every un-replied case in it forever, which
    is the floor this arm is built to avoid rather than to create.
    """
    rows = [_granted_row("scotus/1", "25-100")]
    documents = [
        _document("scotus/1", KIND_PETITION),
        _document("scotus/1", KIND_MERITS_BRIEF_PETITIONER),
        _document("scotus/1", KIND_MERITS_BRIEF_RESPONDENT),
    ]
    with _seeded(tmp_path / "corpus", rows, documents) as conn:
        scan = document_gaps(conn)
    assert scan.gaps == ()


def test_an_apply_fetches_the_merits_briefs_and_the_reply_beside_them(tmp_path: Path) -> None:
    """The recovery, end to end: the arm's own kinds plus what rides with them.

    The reply is not a gap kind, so it does not put the case in the class — and it
    is fetched all the same, because the apply runs the whole selector over the
    payload it just fetched.
    """
    rows = [_granted_row("scotus/1", "25-100")]
    documents = [_document("scotus/1", KIND_PETITION, url="https://www.supremecourt.gov/pet.pdf")]
    docket = _payload(
        _petition_entry(),
        _grant_entry(),
        _merits_entry(
            "Brief of petitioner Floyd Johnson filed.", "https://www.supremecourt.gov/mp.pdf"
        ),
        _merits_entry(
            "Brief of respondent United States filed.",
            "https://www.supremecourt.gov/mr.pdf",
            date_="Jul 13 2026",
        ),
        _merits_entry(
            "Reply of petitioner Floyd Johnson filed.  (Distributed)",
            "https://www.supremecourt.gov/rp.pdf",
            date_="Aug 12 2026",
        ),
    )
    pdfs = {
        "https://www.supremecourt.gov/mp.pdf": _pdf("Petitioner says reverse."),
        "https://www.supremecourt.gov/mr.pdf": _pdf("Respondent says affirm."),
        "https://www.supremecourt.gov/rp.pdf": _pdf("Petitioner replies."),
    }
    log = _Requests()
    with _seeded(tmp_path / "corpus", rows, documents) as conn:
        with _client({"25-100": docket}, pdfs=pdfs, log=log) as client:
            result = _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind: d for d in corpus.documents_for_case(conn, "scotus/1")}
    assert result.merits_candidates == 1
    assert result.recovered == 1
    assert result.remaining == 0
    assert "Petitioner says reverse." in stored[KIND_MERITS_BRIEF_PETITIONER].text
    assert "Respondent says affirm." in stored[KIND_MERITS_BRIEF_RESPONDENT].text
    assert "Petitioner replies." in stored[KIND_MERITS_REPLY_PETITIONER].text
    # The petition it already holds is not re-fetched: the stored URL is unchanged,
    # which is what keeps a merits candidate's charge to what the merits stage added.
    assert "https://www.supremecourt.gov/pet.pdf" not in log.pdfs()


def test_one_side_recovered_is_not_a_recovery(tmp_path: Path) -> None:
    """Recovery is leaving the class, so it is measured against every missing kind."""
    rows = [_granted_row("scotus/1", "25-100")]
    documents = [_document("scotus/1", KIND_PETITION, url="https://www.supremecourt.gov/pet.pdf")]
    docket = _payload(
        _petition_entry(),
        _grant_entry(),
        _merits_entry(
            "Brief of petitioner Floyd Johnson filed.", "https://www.supremecourt.gov/mp.pdf"
        ),
        # The respondent's brief is on the docket with no main document behind it.
        _merits_entry("Brief of respondent United States filed.", None, date_="Jul 13 2026"),
    )
    pdfs = {"https://www.supremecourt.gov/mp.pdf": _pdf("Petitioner says reverse.")}
    with _seeded(tmp_path / "corpus", rows, documents) as conn:
        with _client({"25-100": docket}, pdfs=pdfs) as client:
            result = _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind for d in corpus.documents_for_case(conn, "scotus/1")}
    assert KIND_MERITS_BRIEF_PETITIONER in stored
    assert result.recovered == 0
    assert result.remaining == 1
    assert result.documents == {"scotus/1": [KIND_MERITS_BRIEF_PETITIONER]}


def test_a_merits_candidate_with_no_link_is_a_floor_not_a_selector_alarm(tmp_path: Path) -> None:
    """The entry is there and nothing fetchable is behind it — a floor, and no alarm.

    The alarm is reserved for a filing shape the selector has no arm for, which is
    the class this pass exists to stop producing. A docket that posted no PDF is
    not that, and raising it as one on a modern docket would bury the real ones.
    """
    docket_number = f"{MODERN_LINK_TERM - 1998}-100"
    rows = [_granted_row("scotus/1", docket_number)]
    documents = [_document("scotus/1", KIND_PETITION)]
    docket = _payload(
        _petition_entry(),
        _grant_entry(),
        _merits_entry("Brief of petitioner Floyd Johnson filed.", None),
        _merits_entry("Brief of respondent United States filed.", None, date_="Jul 13 2026"),
    )
    with (
        _seeded(tmp_path / "corpus", rows, documents) as conn,
        _client({docket_number: docket}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.no_link == 1
    assert result.no_entry == 0
    assert result.no_entry_modern_cases == []


def test_a_merits_candidate_the_selector_cannot_read_raises_the_alarm(tmp_path: Path) -> None:
    """No entry any arm recognizes — a selector regression rather than a floor.

    The row says the respondent filed on the merits, so the filing is on the
    docket; a docket where no arm can find it is the pass's own alarm.
    """
    docket_number = f"{MODERN_LINK_TERM - 1998}-100"
    rows = [_granted_row("scotus/1", docket_number)]
    documents = [_document("scotus/1", KIND_PETITION)]
    docket = _payload(
        # The petition entry is dropped too, so neither arm of the class matches:
        # the case owes only its merits briefs here, and nothing reads them.
        _grant_entry(),
        # A merits brief the Clerk recorded under counsel's name rather than a
        # party's — no party-word anchor reaches it.
        _merits_entry("Brief of AT&T, Inc. filed.", "https://www.supremecourt.gov/x.pdf"),
    )
    with (
        _seeded(tmp_path / "corpus", rows, documents) as conn,
        _client({docket_number: docket}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.no_entry == 1
    assert result.no_entry_modern_cases == ["scotus/1"]


def test_an_undatable_grant_on_a_merits_candidate_is_a_floor(tmp_path: Path) -> None:
    """The stage bound cannot place the entry, so nothing is selected — and no alarm.

    The row carries the grant the corpus read at ingest; the *payload* the fetch
    served has no disposition entry this reader can date, so the selector's merits
    arms decline every entry on it. That is a floor this route cannot clear, and
    calling it a selector regression would point a maintainer at the wrong repair.
    """
    docket_number = f"{MODERN_LINK_TERM - 1998}-100"
    rows = [_granted_row("scotus/1", docket_number)]
    documents = [_document("scotus/1", KIND_PETITION)]
    docket = _payload(
        # Both sides' entries are on the docket and readable as text — it is only
        # the *stage* that cannot be placed, because no entry here dates a grant.
        _merits_entry(
            "Brief of petitioner Floyd Johnson filed.", "https://www.supremecourt.gov/mp.pdf"
        ),
        _merits_entry(
            "Brief of respondent United States filed.",
            "https://www.supremecourt.gov/mr.pdf",
            date_="Jul 13 2026",
        ),
    )
    with (
        _seeded(tmp_path / "corpus", rows, documents) as conn,
        _client({docket_number: docket}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    assert result.no_link == 1
    assert result.no_entry_modern_cases == []


def test_the_ledger_splits_the_two_arms(tmp_path: Path) -> None:
    """`merits_candidates` is the line a dispatch is sized against."""
    rows = [
        _granted_row("scotus/1", "25-100"),  # merits only
        _row("scotus/2", "25-101"),  # primary only
        _granted_row("scotus/3", "25-102"),  # both
    ]
    documents = [_document("scotus/1", KIND_PETITION)]
    with _seeded(tmp_path / "corpus", rows, documents) as conn, _client({}) as client:
        result = _run(conn, client, max_cases=0)
    assert result.candidates == 3
    assert result.merits_candidates == 2


def test_a_both_arm_candidate_still_raises_the_primary_selector_alarm(tmp_path: Path) -> None:
    """The alarm is per kind, so a readable merits entry cannot silence it.

    This is the shape the widening would otherwise disable outright: a granted,
    briefed row is in the merits arm only because the docket carries an entry the
    respondent-brief predicate reads, so a candidate in *both* arms almost always
    matches something. If the alarm were per candidate, the one missing kind the
    selector genuinely cannot read — its opening filing — would be hidden behind
    the merits entry that did match, and the class this pass exists to stop
    producing would stop being reported.
    """
    docket_number = f"{MODERN_LINK_TERM - 1998}-100"
    rows = [_granted_row("scotus/1", docket_number)]  # holds nothing at all
    docket = _payload(
        # An opening filing in a shape no arm reads, and readable merits entries
        # with nothing fetchable behind them.
        _merits_entry("Application for review filed.", None, date_="Jan 05 2026"),
        _grant_entry(),
        _merits_entry("Brief of petitioner Floyd Johnson filed.", None),
        _merits_entry("Brief of respondent United States filed.", None, date_="Jul 13 2026"),
    )
    with (
        _seeded(tmp_path / "corpus", rows) as conn,
        _client({docket_number: docket}) as client,
    ):
        result = _run(conn, client, max_cases=5)
    # Counted once, at the floor its matched kinds put it at …
    assert result.no_link == 1
    assert result.no_entry == 0
    # … and still named, because one of its missing kinds matched no entry.
    assert result.no_entry_modern_cases == ["scotus/1"]


def test_a_motion_reply_does_not_take_the_reply_slot(tmp_path: Path) -> None:
    """A collateral-motion reply is not merits advocacy, and must not close the arm.

    Each reply arm takes the first qualifying entry in docket order and then
    closes, so a motion reply filed between the grant and the briefs would both
    store a procedural paper as merits advocacy and put the case's real reply
    permanently out of reach.
    """
    rows = [_granted_row("scotus/1", "25-100")]
    documents = [_document("scotus/1", KIND_PETITION, url="https://www.supremecourt.gov/pet.pdf")]
    docket = _payload(
        _petition_entry(),
        _grant_entry(),
        _merits_entry(
            "Reply of petitioners in support of motion for divided argument filed.",
            "https://www.supremecourt.gov/motion-reply.pdf",
            date_="May 01 2026",
        ),
        _merits_entry(
            "Brief of petitioner Floyd Johnson filed.", "https://www.supremecourt.gov/mp.pdf"
        ),
        _merits_entry(
            "Brief of respondent United States filed.",
            "https://www.supremecourt.gov/mr.pdf",
            date_="Jul 13 2026",
        ),
        _merits_entry(
            "Reply of petitioner Floyd Johnson filed.  (Distributed)",
            "https://www.supremecourt.gov/rp.pdf",
            date_="Aug 12 2026",
        ),
    )
    pdfs = {
        "https://www.supremecourt.gov/motion-reply.pdf": _pdf("About the argument order."),
        "https://www.supremecourt.gov/mp.pdf": _pdf("Petitioner says reverse."),
        "https://www.supremecourt.gov/mr.pdf": _pdf("Respondent says affirm."),
        "https://www.supremecourt.gov/rp.pdf": _pdf("Petitioner replies."),
    }
    with (
        _seeded(tmp_path / "corpus", rows, documents) as conn,
        _client({"25-100": docket}, pdfs=pdfs) as client,
    ):
        _run(conn, client, apply=True, max_cases=5)
        stored = {d.kind: d for d in corpus.documents_for_case(conn, "scotus/1")}
    assert "Petitioner replies." in stored[KIND_MERITS_REPLY_PETITIONER].text
    assert "About the argument order." not in stored[KIND_MERITS_REPLY_PETITIONER].text
