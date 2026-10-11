"""Document freshness: the stored set brought up to the docket the poll just read."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest

from fedcourtsai import corpus, supremecourt
from fedcourtsai.config import LiveConfig
from fedcourtsai.pipeline import live as live_module
from fedcourtsai.pipeline.documents import (
    KIND_APPLICATION,
    KIND_APPLICATION_REPLY,
    KIND_APPLICATION_RESPONSE,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_CERT_REPLY,
    KIND_DESCRIPTIONS,
    KIND_PETITION,
    TEXT_COVERAGE_KINDS,
    fetch_case_documents,
    select_documents,
    unheld_document_kinds,
)
from fedcourtsai.pipeline.ingest import from_live_docket, to_corpus_row
from fedcourtsai.pipeline.live import (
    FreshnessCandidate,
    _freshness_order,
    poll_applications,
    poll_live_cases,
    refresh_stale_documents,
)
from fedcourtsai.provision import CellRead, documents_before, moment_cutoff, place_at_moment
from fedcourtsai.supremecourt import SupremeCourtClient, live_docket_id
from tests.test_documents import _pdf

_HOST = "https://www.supremecourt.gov"
_TODAY = date(2026, 10, 9)


def _link(url: str, label: str = "Main Document") -> dict[str, str]:
    return {"Description": label, "DocumentUrl": f"{_HOST}/{url}"}


def _entry(day: str, text: str, *links: dict[str, str]) -> dict[str, Any]:
    return {"Date": day, "Text": text, "Links": list(links)}


_PETITION = _entry(
    "Jun 01 2026", "Petition for a writ of certiorari filed.", _link("p.pdf", "Petition")
)
_BIO_LEAD = _entry("Jul 01 2026", "Brief of respondent State in opposition filed.", _link("b1.pdf"))
_BIO_SECOND = _entry(
    "Jul 01 2026", "Brief of respondent County in opposition filed.", _link("b2.pdf")
)
_CERT_REPLY = _entry("Jul 10 2026", "Reply of petitioner Jane Doe filed.", _link("r.pdf"))


def _cert_payload(*entries: dict[str, Any], number: str = "25-100") -> dict[str, Any]:
    return {
        "CaseNumber": f"{number} ",
        "bCapitalCase": False,
        "sJsonCaseType": "Paid",
        "sJsonTerm": "2025",
        "DocketedDate": "June 2, 2026",
        "PetitionerTitle": "Doe, Petitioner",
        "RespondentTitle": "Roe, Respondent",
        "Petitioner": [{"PartyName": "Jane Doe", "Attorney": "A. Counsel"}],
        "Respondent": [{"PartyName": "Richard Roe", "Attorney": "B. Counsel"}],
        "ProceedingsandOrder": list(entries),
    }


# An interim docket in the shapes 26A370 carries: the application, the Justice's
# call for a response, the response, and the applicant's reply.
_APPLICATION = _entry(
    "Sep 16 2026",
    "Application (26A370) for a stay pending appeal, submitted to Justice Kagan.",
    _link("app.pdf"),
)
_RESPONSE_REQUESTED = _entry(
    "Sep 18 2026",
    "Response to application (26A370) requested by Justice Kagan, due by 4 p.m. (EDT) "
    + "on September 25, 2026.",
)
_RESPONSE = _entry(
    "Sep 25 2026",
    "Response to application from respondent Shawn Jensen, et al. filed.",
    _link("resp.pdf"),
    _link("resp-cert.pdf", "Certificate of Word Count"),
)
# Posted under the Clerk's `Reply` label, beside its proof of service.
_APPLICATION_REPLY = _entry(
    "Sep 29 2026",
    "Reply of applicant Ryan Thornell, et al. filed.",
    _link("reply.pdf", "Reply"),
    _link("reply-pos.pdf", "Proof of Service"),
)


def _application_payload(*entries: dict[str, Any]) -> dict[str, Any]:
    return {
        "CaseNumber": "26A370 ",
        "bCapitalCase": False,
        "sJsonCaseType": "Application",
        "sJsonTerm": "2026",
        "DocketedDate": "September 16, 2026",
        "PetitionerTitle": "Thornell, Applicant",
        "RespondentTitle": "Jensen, Respondent",
        "Petitioner": [{"PartyName": "Ryan Thornell", "Attorney": "A. Counsel"}],
        "Respondent": [{"PartyName": "Shawn Jensen", "Attorney": "B. Counsel"}],
        "ProceedingsandOrder": list(entries),
    }


_SERVED = {
    f"{_HOST}/{name}": _pdf(f"The text of {name}.")
    for name in ("p.pdf", "b1.pdf", "b2.pdf", "r.pdf", "app.pdf", "resp.pdf", "reply.pdf")
}


class _Recorder:
    """A served-PDF host that records every URL asked for."""

    def __init__(self, served: dict[str, bytes], dockets: dict[str, dict[str, Any]] | None = None):
        self.served = served
        self.dockets = dockets or {}
        self.asked: list[str] = []

    def client(self) -> SupremeCourtClient:
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            self.asked.append(url)
            name = request.url.path.rsplit("/", 1)[-1]
            if name.endswith(".json") and name.removesuffix(".json") in self.dockets:
                return httpx.Response(200, json=self.dockets[name.removesuffix(".json")])
            if url in self.served:
                return httpx.Response(200, content=self.served[url])
            return httpx.Response(404)

        inner = httpx.Client(
            transport=httpx.MockTransport(handler),
            headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
        )
        return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None)


def _stored(db: Path, case_id: str) -> dict[str, corpus.CaseDocument]:
    with corpus.connect(db) as conn:
        return {d.kind: d for d in corpus.documents_for_case(conn, case_id)}


def _store(db: Path, payload: dict[str, Any], case_id: str, *, on: date) -> None:
    """Provision ``case_id`` from ``payload`` as the poller would have on ``on``."""
    with _Recorder(_SERVED).client() as client:
        documents = fetch_case_documents(
            client, case_id, payload, stored_urls={}, char_cap=10_000, today=on
        )
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, documents)


@pytest.fixture
def db(tmp_path: Path) -> Iterator[Path]:
    path = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(path) as conn:
        conn.commit()
    yield path


# --- the held test ------------------------------------------------------------------


def test_unheld_names_a_filing_docketed_after_the_stored_set() -> None:
    refs = select_documents(_cert_payload(_PETITION, _BIO_LEAD, _CERT_REPLY))
    stored = {KIND_PETITION: f"{_HOST}/p.pdf"}
    assert unheld_document_kinds(refs, stored) == [KIND_BRIEF_IN_OPPOSITION, KIND_CERT_REPLY]


def test_unheld_names_a_superseding_link_and_nothing_held() -> None:
    refs = select_documents(_cert_payload(_PETITION))
    assert unheld_document_kinds(refs, {KIND_PETITION: f"{_HOST}/p.pdf"}) == []
    assert unheld_document_kinds(refs, {KIND_PETITION: f"{_HOST}/old.pdf"}) == [KIND_PETITION]


def test_unheld_reads_a_partial_opposition_as_owed() -> None:
    """25-1192's shape: two same-day oppositions selected, one stored."""
    refs = select_documents(_cert_payload(_PETITION, _BIO_LEAD, _BIO_SECOND))
    partial = {KIND_PETITION: f"{_HOST}/p.pdf", KIND_BRIEF_IN_OPPOSITION: f"{_HOST}/b1.pdf"}
    assert unheld_document_kinds(refs, partial) == [KIND_BRIEF_IN_OPPOSITION]
    whole = {**partial, KIND_BRIEF_IN_OPPOSITION: f"{_HOST}/b1.pdf|{_HOST}/b2.pdf"}
    assert unheld_document_kinds(refs, whole) == []


def test_unheld_agrees_with_what_the_fetch_would_fetch() -> None:
    """The two readings cannot disagree: held means the fetch asks for nothing."""
    payload = _cert_payload(_PETITION, _BIO_LEAD, _BIO_SECOND, _CERT_REPLY)
    recorder = _Recorder(_SERVED)
    with recorder.client() as client:
        first = fetch_case_documents(
            client, "scotus/1", payload, stored_urls={}, char_cap=10_000, today=_TODAY
        )
    stored = {d.kind: d.url for d in first}
    assert unheld_document_kinds(select_documents(payload), stored) == []
    recorder.asked.clear()
    with recorder.client() as client:
        again = fetch_case_documents(
            client, "scotus/1", payload, stored_urls=stored, char_cap=10_000, today=_TODAY
        )
    assert again == [] and recorder.asked == []


# --- the interim kinds ---------------------------------------------------------------


def test_the_response_and_the_reply_are_selected_off_their_main_documents() -> None:
    refs = {
        ref.kind: ref
        for ref in select_documents(
            _application_payload(_APPLICATION, _RESPONSE_REQUESTED, _RESPONSE, _APPLICATION_REPLY)
        )
    }
    assert refs[KIND_APPLICATION].url == f"{_HOST}/app.pdf"
    assert refs[KIND_APPLICATION_RESPONSE].url == f"{_HOST}/resp.pdf"
    assert refs[KIND_APPLICATION_RESPONSE].entry_date == "Sep 25 2026"
    assert refs[KIND_APPLICATION_REPLY].url == f"{_HOST}/reply.pdf"
    # The request for a response is not the response, and a response is never
    # read as a cert-stage opposition.
    assert KIND_BRIEF_IN_OPPOSITION not in refs


def test_only_the_first_response_is_taken() -> None:
    later = _entry(
        "Sep 26 2026", "Response to application from respondent State filed.", _link("x.pdf")
    )
    refs = select_documents(_application_payload(_APPLICATION, _RESPONSE, later))
    assert [r.url for r in refs if r.kind == KIND_APPLICATION_RESPONSE] == [f"{_HOST}/resp.pdf"]


@pytest.mark.parametrize(
    "text",
    [
        "Reply of applicant Jane Doe in support of motion to expedite filed.",
        "Reply of amicus curiae Acme supporting applicant filed.",
        "Reply of applicant Jane Doe",  # no filing verb
        "Reply of petitioner Jane Doe filed.",  # the cert-stage reply, not an applicant's
    ],
)
def test_the_reply_arm_refuses_what_is_not_the_applicants_reply(text: str) -> None:
    refs = select_documents(
        _application_payload(_APPLICATION, _entry("Sep 29 2026", text, _link("z.pdf")))
    )
    assert KIND_APPLICATION_REPLY not in {r.kind for r in refs}


def test_the_reply_arm_takes_no_proof_of_service() -> None:
    papers_only = _entry(
        "Sep 29 2026",
        "Reply of applicant Ryan Thornell, et al. filed.",
        _link("pos.pdf", "Proof of Service"),
    )
    refs = select_documents(_application_payload(_APPLICATION, papers_only))
    assert KIND_APPLICATION_REPLY not in {r.kind for r in refs}


def test_a_reply_link_to_the_application_itself_is_not_the_reply() -> None:
    """26A428's shape: the reply entry's `Reply` link serves the application's PDF."""
    misposted = _entry(
        "Sep 30 2026",
        "Reply of applicant Kenneth Nelsen, Warden filed.",
        _link("app.pdf", "Reply"),
    )
    refs = select_documents(_application_payload(_APPLICATION, _RESPONSE, misposted))
    kinds = [r.kind for r in refs]
    assert KIND_APPLICATION in kinds and KIND_APPLICATION_REPLY not in kinds


def test_an_applicants_reply_is_not_a_cert_reply() -> None:
    refs = select_documents(_cert_payload(_PETITION, _BIO_LEAD, _APPLICATION_REPLY))
    kinds = {r.kind for r in refs}
    assert KIND_CERT_REPLY not in kinds and KIND_APPLICATION_REPLY in kinds


def test_the_interim_kinds_are_registered_everywhere_a_kind_is_read() -> None:
    for kind in (KIND_APPLICATION_RESPONSE, KIND_APPLICATION_REPLY):
        assert kind in TEXT_COVERAGE_KINDS
        assert KIND_DESCRIPTIONS[kind]


# --- the cutoff: a fresher set never reaches a cell placed before the filing --------


def _interim_events(case_id: str) -> list[corpus.CorpusEvent]:
    return [
        corpus.CorpusEvent(
            event_id="evt-order-response-requested-disposition",
            case_id=case_id,
            court="scotus",
            kind="order",
            title=case_id,
            opened_at=date(2026, 9, 18),
        ),
        corpus.CorpusEvent(
            event_id="evt-brief-response-disposition",
            case_id=case_id,
            court="scotus",
            kind="brief",
            title=case_id,
            opened_at=date(2026, 9, 25),
        ),
    ]


def _refreshed_interim_set(db: Path) -> tuple[str, dict[str, Any], list[corpus.CaseDocument]]:
    """The application stored at its first fetch, then the freshness pass after the reply."""
    case_id = "scotus/9526000370"
    _store(db, _application_payload(_APPLICATION), case_id, on=date(2026, 9, 17))
    payload = _application_payload(_APPLICATION, _RESPONSE_REQUESTED, _RESPONSE, _APPLICATION_REPLY)
    with _Recorder(_SERVED).client() as client:
        refresh_stale_documents(
            client,
            db,
            [FreshnessCandidate(case_id, payload, changed=True)],
            cap=5,
            char_cap=10_000,
            today=date(2026, 10, 1),
        )
    with corpus.connect(db) as conn:
        documents = corpus.documents_for_case(conn, case_id)
    return case_id, payload, documents


def test_refreshed_rows_carry_their_docket_dates_not_the_fetch_date(db: Path) -> None:
    _, _, documents = _refreshed_interim_set(db)
    by_kind = {d.kind: d for d in documents}
    assert by_kind[KIND_APPLICATION_RESPONSE].entry_date == "Sep 25 2026"
    assert by_kind[KIND_APPLICATION_RESPONSE].fetched_at == date(2026, 10, 1)
    assert by_kind[KIND_APPLICATION_REPLY].entry_date == "Sep 29 2026"


def test_the_response_filed_cell_reads_the_response_that_opens_it(db: Path) -> None:
    case_id, _, documents = _refreshed_interim_set(db)
    cutoff = moment_cutoff("evt-brief-response-disposition", _interim_events(case_id))
    assert cutoff == date(2026, 9, 26)
    kept = {d.kind for d in documents_before(documents, cutoff)}
    assert kept == {KIND_APPLICATION, KIND_APPLICATION_RESPONSE}  # the reply came after


def test_a_cell_cut_before_a_refreshed_filing_never_receives_it(db: Path) -> None:
    """Every filing the freshness pass adds is placed by its own docket date, so
    a cell cut at the response-requested moment receives neither the response
    nor the reply, however long after the cutoff the pass stored them. The
    placement takes no mode — the local cascade's replay cells go through it as
    forward ones do — and `provision-snapshot` cuts in either mode
    (`tests/test_cli_provision.py`)."""
    case_id, payload, documents = _refreshed_interim_set(db)
    event = "evt-order-response-requested-disposition"
    events = _interim_events(case_id)
    cutoff = moment_cutoff(event, events)
    assert cutoff == date(2026, 9, 19)
    read = CellRead(
        latest=(date(2026, 10, 1), payload),
        documents=documents,
        events=events,
        row=None,
        cutoff=cutoff,
        dated=None,
    )
    placement = place_at_moment(
        case_id,
        event,
        cutoff,
        read,
        payload=payload,
        snapshot_date=date(2026, 10, 1),
        documents=documents,
    )
    assert {d.kind for d in placement.documents} == {KIND_APPLICATION}
    assert placement.dropped_documents == 2


def test_the_cutoff_boundary_is_exclusive_on_the_filing_day(db: Path) -> None:
    """A filing docketed the day before the cutoff (the trigger day) is in; one
    docketed on the cutoff day itself is out."""
    _, _, documents = _refreshed_interim_set(db)
    response_day = date(2026, 9, 25)
    on_trigger = {d.kind for d in documents_before(documents, response_day + timedelta(days=1))}
    on_cutoff = {d.kind for d in documents_before(documents, response_day)}
    assert KIND_APPLICATION_RESPONSE in on_trigger
    assert KIND_APPLICATION_RESPONSE not in on_cutoff


# --- the pass: what it fetches, and its cap ------------------------------------------


def test_the_pass_fetches_only_what_the_stored_set_lacks(db: Path) -> None:
    case_id = "scotus/9025000100"
    _store(db, _cert_payload(_PETITION), case_id, on=date(2026, 7, 16))
    recorder = _Recorder(_SERVED)
    payload = _cert_payload(_PETITION, _BIO_LEAD, _BIO_SECOND, _CERT_REPLY)
    with recorder.client() as client:
        ledger = refresh_stale_documents(
            client,
            db,
            [FreshnessCandidate(case_id, payload, changed=True)],
            cap=5,
            char_cap=10_000,
            today=_TODAY,
        )
    # The petition's link is unchanged, so it is never asked for again.
    assert f"{_HOST}/p.pdf" not in recorder.asked
    assert sorted(recorder.asked) == [f"{_HOST}/b1.pdf", f"{_HOST}/b2.pdf", f"{_HOST}/r.pdf"]
    stored = _stored(db, case_id)
    assert stored[KIND_BRIEF_IN_OPPOSITION].url == f"{_HOST}/b1.pdf|{_HOST}/b2.pdf"
    assert stored[KIND_CERT_REPLY].entry_date == "Jul 10 2026"
    assert stored[KIND_PETITION].fetched_at == date(2026, 7, 16)  # not re-cut
    assert ledger["stale"] == 1 and ledger["refreshed"] == 1 and ledger["deferred"] == 0
    assert ledger["owed"] == {KIND_BRIEF_IN_OPPOSITION: 1, KIND_CERT_REPLY: 1}


def test_a_held_case_costs_no_request(db: Path) -> None:
    case_id = "scotus/9025000100"
    payload = _cert_payload(_PETITION, _BIO_LEAD)
    _store(db, payload, case_id, on=date(2026, 7, 16))
    recorder = _Recorder(_SERVED)
    with recorder.client() as client:
        ledger = refresh_stale_documents(
            client,
            db,
            [FreshnessCandidate(case_id, payload, changed=True)],
            cap=5,
            char_cap=10_000,
            today=_TODAY,
        )
    assert recorder.asked == []
    assert ledger["checked"] == 1 and ledger["stale"] == 0 and ledger["refreshed"] == 0


def test_the_cap_bounds_the_cases_fetched_and_moved_dockets_go_first(db: Path) -> None:
    ids = [f"scotus/90250001{n:02d}" for n in range(4)]
    for case_id in ids:
        _store(db, _cert_payload(_PETITION), case_id, on=date(2026, 7, 16))
    payload = _cert_payload(_PETITION, _BIO_LEAD)
    candidates = [
        FreshnessCandidate(ids[0], payload, changed=False),
        FreshnessCandidate(ids[1], payload, changed=True),
        FreshnessCandidate(ids[2], payload, changed=False),
        FreshnessCandidate(ids[3], payload, changed=True),
    ]
    with _Recorder(_SERVED).client() as client:
        ledger = refresh_stale_documents(
            client, db, candidates, cap=2, char_cap=10_000, today=_TODAY
        )
    assert ledger["stale"] == 4 and ledger["refreshed"] == 2 and ledger["deferred"] == 2
    refreshed = {cid for cid in ids if KIND_BRIEF_IN_OPPOSITION in _stored(db, cid)}
    assert refreshed == {ids[1], ids[3]}


def test_a_zero_cap_reads_and_fetches_nothing(db: Path) -> None:
    recorder = _Recorder(_SERVED)
    candidate = FreshnessCandidate("scotus/1", _cert_payload(_PETITION), changed=True)
    with recorder.client() as client:
        ledger = refresh_stale_documents(
            client, db, [candidate], cap=0, char_cap=10_000, today=_TODAY
        )
    assert recorder.asked == [] and ledger["checked"] == 0


def test_a_spent_deadline_defers_every_stale_case(db: Path) -> None:
    case_id = "scotus/9025000100"
    _store(db, _cert_payload(_PETITION), case_id, on=date(2026, 7, 16))
    recorder = _Recorder(_SERVED)
    candidate = FreshnessCandidate(case_id, _cert_payload(_PETITION, _BIO_LEAD), changed=True)
    clock = iter([0.0, 0.0, 99.0, 99.0, 99.0])
    with recorder.client() as client:
        ledger = refresh_stale_documents(
            client,
            db,
            [candidate],
            cap=5,
            char_cap=10_000,
            today=_TODAY,
            deadline=10.0,
            time_fn=lambda: next(clock),
        )
    assert recorder.asked == []
    assert ledger["stale"] == 1 and ledger["deferred"] == 1 and ledger["refreshed"] == 0


# --- the polls collect their candidates ----------------------------------------------


def _seed(db: Path, payload: dict[str, Any], docket_id: int, **update: Any) -> corpus.CorpusRow:
    row = to_corpus_row(from_live_docket(payload, docket_id), last_live_polled=date(2026, 7, 16))
    row = row.model_copy(update=update)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        stored = corpus.get_row(conn, row.case_id)
    assert stored is not None
    return stored


def test_the_cert_poll_collects_a_predict_relevant_case_it_did_not_provision(
    db: Path, tmp_path: Path
) -> None:
    """25-901's shape: queued, provisioned at its trigger, then the opposition
    and the reply land with no new distribution — no trigger fires, so only the
    freshness pass can bring them in."""
    docket_id = live_docket_id(25, 100)
    old = _cert_payload(_PETITION)
    due = _seed(db, old, docket_id, predict_queued_at=date(2026, 7, 16))
    _store(db, old, due.case_id, on=date(2026, 7, 16))
    other = _seed(db, _cert_payload(_PETITION, number="25-101"), live_docket_id(25, 101))
    new = _cert_payload(_PETITION, _BIO_LEAD, _CERT_REPLY)
    recorder = _Recorder(
        _SERVED, dockets={"25-100": new, "25-101": _cert_payload(_PETITION, number="25-101")}
    )
    collected: list[FreshnessCandidate] = []
    with recorder.client() as client:
        poll_live_cases(
            client, db, tmp_path / "data", [due, other], freshness=collected, today=_TODAY
        )
        # The poll itself fetched no filing: only the two dockets.
        assert all(url.endswith(".json") for url in recorder.asked)
        assert [c.case_id for c in collected] == [due.case_id]  # 25-101 is not predict-relevant
        assert collected[0].changed
        live_module.refresh_stale_documents(
            client, db, collected, cap=5, char_cap=10_000, today=_TODAY
        )
    assert {KIND_BRIEF_IN_OPPOSITION, KIND_CERT_REPLY} <= set(_stored(db, due.case_id))


def test_the_application_poll_collects_the_response_its_debounce_skipped(
    db: Path, tmp_path: Path
) -> None:
    """26A370's shape: queued the day the response lands, so the debounce keeps
    the poll from provisioning — and the response-filed cell would read the
    application alone."""
    docket_id = 9_526_000_370
    old = _application_payload(_APPLICATION, _RESPONSE_REQUESTED)
    due = _seed(db, old, docket_id, predict_queued_at=_TODAY)
    _store(db, old, due.case_id, on=date(2026, 9, 18))
    new = _application_payload(_APPLICATION, _RESPONSE_REQUESTED, _RESPONSE)
    recorder = _Recorder(_SERVED, dockets={"26A370": new})
    collected: list[FreshnessCandidate] = []
    with recorder.client() as client:
        poll_applications(client, db, tmp_path / "data", [due], freshness=collected, today=_TODAY)
        assert [c.case_id for c in collected] == [due.case_id]
        refresh_stale_documents(client, db, collected, cap=5, char_cap=10_000, today=_TODAY)
    assert _stored(db, due.case_id)[KIND_APPLICATION_RESPONSE].url == f"{_HOST}/resp.pdf"


def test_a_poll_without_a_freshness_list_collects_nothing(db: Path, tmp_path: Path) -> None:
    docket_id = live_docket_id(25, 100)
    old = _cert_payload(_PETITION)
    due = _seed(db, old, docket_id, predict_queued_at=date(2026, 7, 16))
    _store(db, old, due.case_id, on=date(2026, 7, 16))
    recorder = _Recorder(_SERVED, dockets={"25-100": _cert_payload(_PETITION, _BIO_LEAD)})
    with recorder.client() as client:
        poll_live_cases(client, db, tmp_path / "data", [due], today=_TODAY)
    assert KIND_BRIEF_IN_OPPOSITION not in _stored(db, due.case_id)


def test_a_petitioners_reply_is_never_the_applicants() -> None:
    joint = _entry(
        "Jul 10 2026", "Reply of petitioner and applicant Jane Doe filed.", _link("r.pdf")
    )
    refs = select_documents(_cert_payload(_PETITION, _BIO_LEAD, joint))
    assert KIND_APPLICATION_REPLY not in {r.kind for r in refs}


def test_the_link_read_matches_the_stored_rows(db: Path) -> None:
    case_id = "scotus/9025000100"
    _store(db, _cert_payload(_PETITION, _BIO_LEAD), case_id, on=date(2026, 7, 16))
    with corpus.connect(db) as conn:
        assert corpus.document_urls_for_case(conn, case_id) == {
            d.kind: d.url for d in corpus.documents_for_case(conn, case_id)
        }
        assert corpus.document_urls_for_case(conn, "scotus/1") == {}


def test_a_link_upstream_does_not_serve_is_counted_unwritten(db: Path) -> None:
    case_id = "scotus/9025000100"
    _store(db, _cert_payload(_PETITION), case_id, on=date(2026, 7, 16))
    gone = _entry(
        "Jul 01 2026", "Brief of respondent State in opposition filed.", _link("gone.pdf")
    )
    candidate = FreshnessCandidate(case_id, _cert_payload(_PETITION, gone), changed=False)
    with _Recorder(_SERVED).client() as client:
        ledger = refresh_stale_documents(
            client, db, [candidate], cap=5, char_cap=10_000, today=_TODAY
        )
    assert ledger["refreshed"] == 1 and ledger["documents"] == 0 and ledger["unwritten"] == 1


def test_one_case_that_raises_costs_only_that_case(
    db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ids = ["scotus/9025000100", "scotus/9025000101"]
    for case_id in ids:
        _store(db, _cert_payload(_PETITION), case_id, on=date(2026, 7, 16))
    real = live_module.provision_documents

    def flaky(client: SupremeCourtClient, path: Path, case_id: str, *a: Any, **kw: Any) -> int:
        if case_id == ids[0]:
            raise RuntimeError("store throttled")
        return int(real(client, path, case_id, *a, **kw))

    monkeypatch.setattr(live_module, "provision_documents", flaky)
    payload = _cert_payload(_PETITION, _BIO_LEAD)
    with _Recorder(_SERVED).client() as client:
        ledger = refresh_stale_documents(
            client,
            db,
            [FreshnessCandidate(case_id, payload, changed=True) for case_id in ids],
            cap=5,
            char_cap=10_000,
            today=_TODAY,
        )
    assert ledger["failed"] == 1 and ledger["refreshed"] == 2
    assert KIND_BRIEF_IN_OPPOSITION in _stored(db, ids[1])


def test_a_pass_that_raises_never_costs_the_window(
    db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The polls, cursors and outcomes are written before the pass runs, and the
    corpus push comes after the command: a raise here would lose them all."""

    def broken(*_a: Any, **_kw: Any) -> dict[str, object]:
        raise RuntimeError("content store throttled")

    monkeypatch.setattr(live_module, "refresh_stale_documents", broken)
    served = {"25-1": _cert_payload(_PETITION, number="25-1")}
    with _Recorder(_SERVED, dockets=served).client() as client:
        queues, discovery = live_module.live_poll_all(
            client, db, tmp_path / "data", term=25, config=LiveConfig(), today=_TODAY
        )
    assert queues.document_freshness == {"error": "RuntimeError"}
    assert len(discovery.onboarded) == 1


def test_the_unchanged_half_rotates_by_day_behind_the_moved_dockets() -> None:
    """A run of cases owing a dead link sits in the unchanged half; its order
    rotates daily so it cannot hold the cap ahead of the same cases forever."""
    payload = _cert_payload(_PETITION)
    unchanged = [FreshnessCandidate(f"scotus/{n}", payload, changed=False) for n in range(10)]
    moved = FreshnessCandidate("scotus/99", payload, changed=True)

    def order(day: date) -> list[str]:
        ranked = sorted([*unchanged, moved], key=lambda c: _freshness_order(c, day))
        return [c.case_id for c in ranked]

    first, second = order(date(2026, 10, 9)), order(date(2026, 10, 10))
    assert first[0] == second[0] == "scotus/99"
    assert first[1:] != second[1:]
    assert order(date(2026, 10, 9)) == first  # deterministic within a day
