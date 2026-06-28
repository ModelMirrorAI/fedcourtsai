from datetime import date
from pathlib import Path
from typing import Any, cast

import httpx

from fedcourtsai import corpus
from fedcourtsai.cli import _format_discovery_failures
from fedcourtsai.config import PredictScope
from fedcourtsai.courtlistener import CourtListenerClient
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.discover import discover_cases
from fedcourtsai.pipeline.pull import pull_case, pull_cases
from fedcourtsai.schemas import EventKind
from fedcourtsai.store import open_events, resolved_events

DOCKET: dict[str, Any] = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "nature_of_suit": "Civil Rights",
}


class FakeClient:
    """Stand-in for CourtListenerClient returning canned docket facts."""

    def __init__(self, docket: dict[str, Any], entries: list[dict[str, Any]]) -> None:
        self._docket = docket
        self._entries = entries

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return self._docket

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return self._entries


def _pull(client: FakeClient, tmp_path: Path) -> Any:
    return pull_case(
        cast(CourtListenerClient, client),
        corpus.corpus_db_path(tmp_path / "corpus"),
        tmp_path / "data",
        "ca9",
        64512345,
    )


def test_first_pull_onboards_into_corpus(tmp_path: Path) -> None:
    entries = [{"id": 1, "description": "Motion to stay"}]
    result = _pull(FakeClient(DOCKET, entries), tmp_path)
    assert result.case_id == "ca9/64512345"
    assert result.changed is True
    assert result.snapshot == date.today().isoformat()
    # Both the normalized row and the point-in-time snapshot land in the corpus,
    # not in per-case git files.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
        snap = corpus.latest_snapshot(conn, "ca9/64512345")
    assert row is not None
    assert row.court == "ca9"
    assert row.topic == "Civil Rights"
    assert snap is not None
    snap_date, payload = snap
    assert snap_date == date.today()
    assert payload == {**DOCKET, "docket_entries": entries}


def test_pull_writes_no_git_files(tmp_path: Path) -> None:
    # Pull is now corpus-only: it materializes nothing under data/ (the snapshot
    # lives in the corpus; predict/evaluate provision it from there per run).
    _pull(FakeClient(DOCKET, []), tmp_path)
    assert not (tmp_path / "data" / "cases").exists()


def test_unchanged_second_pull_reports_no_change(tmp_path: Path) -> None:
    entries = [{"id": 1, "description": "Motion to stay"}]
    assert _pull(FakeClient(DOCKET, entries), tmp_path).changed is True
    assert _pull(FakeClient(DOCKET, entries), tmp_path).changed is False


def test_changed_docket_is_detected(tmp_path: Path) -> None:
    assert _pull(FakeClient(DOCKET, []), tmp_path).changed is True
    new_entry = [{"id": 2, "description": "Order granting stay"}]
    assert _pull(FakeClient(DOCKET, new_entry), tmp_path).changed is True


def test_pull_stamps_last_pulled_in_corpus(tmp_path: Path) -> None:
    # Each refresh stamps today's date so the governor can rotate this case back.
    _pull(FakeClient(DOCKET, []), tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
    assert row is not None
    assert row.last_pulled == date.today()


class FakeMultiClient:
    """Returns a distinct docket per id (court taken from the canned facts)."""

    def __init__(self, dockets: dict[int, dict[str, Any]]) -> None:
        self._dockets = dockets

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return self._dockets[docket_id]

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return [{"id": 1, "description": "Filed"}]


def _scotus_ca9_client() -> FakeMultiClient:
    base = "https://www.courtlistener.com/api/rest/v4/courts"
    return FakeMultiClient(
        {
            900: {"id": 900, "court": f"{base}/scotus/", "date_filed": "2026-01-02"},
            901: {"id": 901, "court": f"{base}/ca9/", "date_filed": "2026-01-02"},
        }
    )


def _open_event(db: Path, court: str, docket: int) -> None:
    """Record an open predictable event in the corpus so `open_events` queues it."""
    event = corpus.CorpusEvent(
        event_id="evt-appeal-disposition",
        case_id=f"{court}/{docket}",
        court=court,
        kind=EventKind.appeal,
        title="Disposition of the appeal",
    )
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [event])


def _gate_queues(tmp_path: Path, scope: PredictScope) -> Any:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    _open_event(db, "scotus", 900)
    _open_event(db, "ca9", 901)
    return pull_cases(
        cast(CourtListenerClient, _scotus_ca9_client()),
        db,
        data_root,
        [("scotus", 900), ("ca9", 901)],
        scope=scope,
    )


def test_pull_cases_gate_enqueues_only_eligible_under_scotus_touched(tmp_path: Path) -> None:
    queues = _gate_queues(tmp_path, PredictScope.scotus_touched)
    # Only the SCOTUS (eligible) case reaches the predict queue; the ca9 case is gated.
    assert {(e["court"], e["docket"]) for e in queues.predict} == {("scotus", 900)}


def test_pull_cases_scope_all_enqueues_every_changed_case(tmp_path: Path) -> None:
    queues = _gate_queues(tmp_path, PredictScope.all)
    # No gate: both changed cases with open events are queued (today's behavior).
    assert {(e["court"], e["docket"]) for e in queues.predict} == {("scotus", 900), ("ca9", 901)}


class FakeDiscoverPullClient:
    """One fake covering both discovery (``iter_dockets``) and refresh (``get_docket``).

    The single mutable ``docket`` is what the next refresh sees, so a test can
    onboard a pending docket and then flip it to a decided one.
    """

    def __init__(self, filed: dict[str, list[dict[str, Any]]], docket: dict[str, Any]) -> None:
        self._filed = filed
        self.docket = docket
        self.entries: list[dict[str, Any]] = []

    def iter_dockets(
        self, court: str, date_filed_gte: date, *, max_results: int
    ) -> list[dict[str, Any]]:
        hits = [
            d
            for d in self._filed.get(court, [])
            if date.fromisoformat(d["date_filed"]) >= date_filed_gte
        ]
        return hits[:max_results]

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return self.docket

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return self.entries


class FlakyMultiClient:
    """Like FakeMultiClient, but one docket id always fails its fetch.

    Models a transient REST failure on a single case mid-rotation (e.g. a 404 or
    retries exhausted) so a test can assert the rest of the run still makes
    progress.
    """

    def __init__(self, dockets: dict[int, dict[str, Any]], fail_on: int) -> None:
        self._dockets = dockets
        self._fail_on = fail_on

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        if docket_id == self._fail_on:
            raise httpx.HTTPStatusError(
                "404 Not Found",
                request=httpx.Request("GET", f"https://example/dockets/{docket_id}/"),
                response=httpx.Response(404),
            )
        return self._dockets[docket_id]

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return [{"id": 1, "description": "Filed"}]


def test_pull_cases_isolates_a_failed_docket_from_the_rest(tmp_path: Path) -> None:
    # A single docket's REST failure must not abort the rotation: the case that
    # did refresh keeps its corpus write and predict-queue entry, and the failure
    # is recorded rather than raised.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    base = "https://www.courtlistener.com/api/rest/v4/courts"
    client = FlakyMultiClient(
        {901: {"id": 901, "court": f"{base}/ca9/", "date_filed": "2026-01-02"}},
        fail_on=902,
    )
    _open_event(db, "ca9", 901)
    _open_event(db, "ca9", 902)

    # The failing case (902) comes first; the rotation must still reach 901.
    queues = pull_cases(
        cast(CourtListenerClient, client),
        db,
        data_root,
        [("ca9", 902), ("ca9", 901)],
    )

    # The good case is fully processed: corpus row written and queued to predict.
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "ca9/901") is not None
    assert [(e["court"], e["docket"]) for e in queues.predict] == [("ca9", 901)]
    # The failure is surfaced, not swallowed, and carries triage context.
    assert [(f["court"], f["docket"]) for f in queues.failed] == [("ca9", 902)]
    assert "404" in str(queues.failed[0]["reason"])


def test_discover_pull_predict_then_evaluate_from_corpus_events(tmp_path: Path) -> None:
    # The forward pipeline must run off corpus events alone — no hand-written
    # git event.yaml anywhere in discover → pull → predict/evaluate.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    base = "https://www.courtlistener.com/api/rest/v4/courts"
    pending = {"id": 101, "court": f"{base}/ca9/", "date_filed": "2026-06-10", "case_name": "Doe"}
    client = FakeDiscoverPullClient({"ca9": [pending]}, pending)

    # Discovery onboards the case and its open event as raw facts in the corpus.
    discover_cases(
        cast(CourtListenerClient, client), db, ["ca9"], max_new=10, default_since=date(2026, 6, 1)
    )
    assert open_events(db, "ca9", 101) == ["evt-appeal-disposition"]
    assert not (data_root / "cases").exists()  # nothing materialized into git

    # Pull enqueues the corpus-backed open event to predict (no event.yaml needed).
    queues = pull_cases(cast(CourtListenerClient, client), db, data_root, [("ca9", 101)])
    assert [(e["court"], e["docket"]) for e in queues.predict] == [("ca9", 101)]
    assert queues.predict[0]["events"] == ["evt-appeal-disposition"]
    assert queues.evaluate == []

    # The case resolves: a later refresh records outcome.json and enqueues evaluate.
    client.docket = {**pending, "date_terminated": "2026-09-01", "disposition": "Petition denied"}
    client.entries = [{"id": 1, "description": "Order denying the petition"}]
    queues = pull_cases(cast(CourtListenerClient, client), db, data_root, [("ca9", 101)])
    assert [(e["court"], e["docket"]) for e in queues.evaluate] == [("ca9", 101)]
    assert queues.evaluate[0]["events"] == ["evt-appeal-disposition"]

    # outcome.json lands in git; the corpus event is now resolved (out of predict).
    outcome = CasePaths(data_root, "ca9", 101).event("evt-appeal-disposition").outcome
    assert outcome.exists()
    assert open_events(db, "ca9", 101) == []
    assert resolved_events(db, "ca9", 101) == ["evt-appeal-disposition"]


def test_format_discovery_failures_surfaces_each_courts_reason() -> None:
    """``pull-all`` echoes every failed court alongside its recorded reason."""
    # No casualties -> empty suffix that appends cleanly to the count line.
    assert _format_discovery_failures([]) == ""

    failed: list[dict[str, object]] = [
        {"court": "scotus", "reason": "ReadTimeout: read timed out"},
        {"court": "ca1", "reason": "HTTPStatusError: 429 Too Many Requests"},
    ]
    summary = _format_discovery_failures(failed)
    assert summary.startswith(" (2 court(s) failed: ")
    # Both the court id and its failure type/message are visible from the log line.
    assert "scotus [ReadTimeout: read timed out]" in summary
    assert "ca1 [HTTPStatusError: 429 Too Many Requests]" in summary
