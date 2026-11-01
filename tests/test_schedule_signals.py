"""The argument day and response deadline read off a docket's proceedings."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.pipeline.live import ingest_live_payload
from fedcourtsai.pipeline.schedule_signals import argument_set_date, response_deadline
from fedcourtsai.supremecourt import live_docket_id


def _docket(*texts: str) -> dict[str, Any]:
    return {"ProceedingsandOrder": [{"Date": "Oct 01 2026", "Text": text} for text in texts]}


_FILED = "Petition for a writ of certiorari filed. (Response due November 6, 2026)"


def test_the_newest_argument_setting_wins() -> None:
    assert argument_set_date(_docket("Petition GRANTED.")) is None
    assert argument_set_date(
        _docket("Petition GRANTED.", "SET FOR ARGUMENT on Monday, November 3, 2026.")
    ) == date(2026, 11, 3)
    assert argument_set_date(
        _docket(
            "SET FOR ARGUMENT on Monday, November 3, 2026.",
            "SET FOR ARGUMENT on Tuesday, December 1, 2026. VIDED.",
        )
    ) == date(2026, 12, 1)
    # A motion that only asks for argument time sets nothing.
    assert argument_set_date(_docket("Motion for divided argument filed.")) is None


def test_a_docketing_deadline_is_due_until_answered() -> None:
    assert response_deadline(_docket(_FILED)) == (date(2026, 11, 6), "due")
    assert response_deadline(
        _docket(_FILED, "Brief of respondent U.S. Bank N.A. in opposition filed.")
    ) == (date(2026, 11, 6), "filed")
    assert response_deadline(
        _docket(_FILED, "Waiver of right of respondent Acme Inc. to respond filed.")
    ) == (date(2026, 11, 6), "waived")


def test_an_extension_moves_the_deadline_and_a_request_alone_does_not() -> None:
    requested = (
        "Motion to extend the time to file a response from November 6, 2026 to "
        "December 7, 2026, submitted to The Clerk."
    )
    granted = (
        "Motion to extend the time to file a response is granted and the time is extended "
        "to and including December 7, 2026."
    )
    assert response_deadline(_docket(_FILED, requested)) == (date(2026, 11, 6), "due")
    assert response_deadline(_docket(_FILED, requested, granted)) == (date(2026, 12, 7), "due")


def test_a_call_for_response_reopens_a_waived_deadline() -> None:
    called = "Response Requested. (Due December 10, 2026)"
    assert response_deadline(
        _docket(_FILED, "Waiver of right of respondent Roe to respond filed.", called)
    ) == (date(2026, 12, 10), "due")


def test_an_application_response_request_states_its_deadline() -> None:
    request = (
        "Response to application (26A123) requested by Justice Kavanaugh, due by 4 p.m. "
        "(EST) on Friday, November 13, 2026."
    )
    filed = "Response to application (26A123) from respondent Roe filed."
    assert response_deadline(_docket("Application (26A123) for a stay.", request)) == (
        date(2026, 11, 13),
        "due",
    )
    assert response_deadline(_docket(request, filed)) == (date(2026, 11, 13), "filed")


def test_amicus_briefs_and_replies_do_not_answer_the_deadline() -> None:
    assert response_deadline(
        _docket(
            _FILED,
            "Brief amicus curiae of Respondents' Bar Association filed.",
            "Reply of petitioner Doe filed.",
        )
    ) == (date(2026, 11, 6), "due")


def test_nothing_read_is_not_a_reading() -> None:
    # No proceedings key: unobservable, so the corpus pair latch keeps what it has.
    assert response_deadline({}) == (None, None)
    # Proceedings with no deadline stated read nothing either.
    assert response_deadline(_docket("Petition for a writ of certiorari filed.")) == (None, None)


def _live(*texts: str) -> dict[str, Any]:
    return {
        "CaseNumber": "26-100 ",
        "DocketedDate": "October 1, 2026",
        "PetitionerTitle": "Doe, Petitioner",
        "RespondentTitle": "Roe, Respondent",
        "ProceedingsandOrder": [{"Date": "Oct 01 2026", "Text": text} for text in texts],
    }


def test_the_live_poll_lands_the_dates_and_the_latches_hold_them(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(26, 100)

    def _poll(payload: dict[str, Any]) -> corpus.CorpusRow:
        result = ingest_live_payload(db, data_root, payload, docket_id, today=date(2026, 10, 20))
        with corpus.connect(db) as conn:
            stored = corpus.get_row(conn, result.case_id)
        assert stored is not None
        return stored

    stored = _poll(_live(_FILED))
    assert (stored.response_due, stored.response_due_state) == (date(2026, 11, 6), "due")
    assert stored.argument_set_for is None
    # A payload served without its proceedings reads nothing and keeps the pair.
    degraded = _live()
    del degraded["ProceedingsandOrder"]
    stored = _poll(degraded)
    assert (stored.response_due, stored.response_due_state) == (date(2026, 11, 6), "due")
    # A brief in opposition ends the deadline: the pair takes the fresh reading.
    stored = _poll(_live(_FILED, "Brief of respondent Roe in opposition filed."))
    assert (stored.response_due, stored.response_due_state) == (date(2026, 11, 6), "filed")
    # A writer that carries none of the three keeps them all.
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [stored.model_copy(update=_UNREAD)])
        kept = corpus.get_row(conn, stored.case_id)
    assert kept is not None
    assert (kept.response_due, kept.response_due_state) == (date(2026, 11, 6), "filed")
    # The argument day is fill-in latched and a new setting replaces it.
    stored = _poll(_live(_FILED, "SET FOR ARGUMENT on Monday, November 30, 2026."))
    assert stored.argument_set_for == date(2026, 11, 30)
    stored = _poll(_live(_FILED))
    assert stored.argument_set_for == date(2026, 11, 30)


_UNREAD: dict[str, Any] = {
    "argument_set_for": None,
    "response_due": None,
    "response_due_state": None,
}


def test_only_the_respondents_own_answer_ends_the_deadline() -> None:
    for entry in (
        "Motion of petitioner to expedite and to shorten respondent's time to respond filed.",
        "Response of petitioner to respondent's motion to dismiss filed.",
        "Motion of petitioner for leave to file a reply to respondent brief filed.",
        "Brief of the State of Texas in support of respondent filed.",
        "Response to motion from respondent Roe filed.",
        "Motion of respondent Acme Inc. to extend the time to file a response filed.",
    ):
        assert response_deadline(_docket(_FILED, entry)) == (date(2026, 11, 6), "due"), entry
    for entry in (
        "Memorandum of respondent United States filed.",
        "Motion of appellee to dismiss or affirm filed.",
        "Brief of the federal respondents in opposition filed.",
    ):
        assert response_deadline(_docket(_FILED, entry)) == (date(2026, 11, 6), "filed"), entry


def test_an_extension_for_a_brief_in_opposition_moves_the_deadline() -> None:
    granted = (
        "Motion to extend the time to file a brief in opposition is granted and the time is "
        "extended to and including December 7, 2026."
    )
    assert response_deadline(_docket(_FILED, granted)) == (date(2026, 12, 7), "due")
