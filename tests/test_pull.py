from datetime import date
from pathlib import Path
from typing import Any, cast

import httpx

from fedcourtsai import corpus
from fedcourtsai.cli import _format_discovery_failures, _format_refresh_failures
from fedcourtsai.config import PredictScope
from fedcourtsai.courtlistener import CourtListenerClient, RateBudgetExceeded
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.discover import discover_cases
from fedcourtsai.pipeline.pull import _in_predict_scope, pull_case, pull_cases
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

    def __init__(
        self,
        docket: dict[str, Any],
        entries: list[dict[str, Any]],
        clusters: dict[int, dict[str, Any]] | None = None,
    ) -> None:
        self._docket = docket
        self._entries = entries
        self._clusters = clusters or {}
        self.cluster_fetches = 0

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return self._docket

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return self._entries

    def get_opinion_cluster(self, cluster_id: int) -> dict[str, Any]:
        self.cluster_fetches += 1
        if cluster_id not in self._clusters:
            raise httpx.HTTPStatusError(
                "404", request=httpx.Request("GET", "x"), response=httpx.Response(404)
            )
        return self._clusters[cluster_id]


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


def test_refresh_extracts_a_post_onboarding_motion(tmp_path: Path) -> None:
    # Issue #372: a refresh re-extracts events, so a stay motion filed after the
    # case was onboarded becomes a tracked predictable event — not just the
    # case-level baseline present at discovery.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    # Onboard with no entries: only the case-level baseline exists.
    _pull(FakeClient(DOCKET, []), tmp_path)
    assert open_events(db, "ca9", 64512345) == ["evt-appeal-disposition"]
    # A later refresh sees a newly-filed stay motion and adds it.
    result = _pull(
        FakeClient(DOCKET, [{"id": 9, "description": "Motion to stay the mandate"}]), tmp_path
    )
    assert open_events(db, "ca9", 64512345) == [
        "evt-appeal-disposition",
        "evt-motion-stay-the-mandate",
    ]
    assert result.ambiguous == []


def test_refresh_event_extraction_is_idempotent(tmp_path: Path) -> None:
    # Re-extracting on every refresh must converge, not duplicate: a second
    # identical refresh leaves the same events.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    entries = [{"id": 9, "description": "Motion to stay the mandate"}]
    _pull(FakeClient(DOCKET, entries), tmp_path)
    first = open_events(db, "ca9", 64512345)
    _pull(FakeClient(DOCKET, entries), tmp_path)
    assert open_events(db, "ca9", 64512345) == first


def test_refresh_never_reopens_a_resolved_event(tmp_path: Path) -> None:
    # The resolved latch holds through re-extraction: once the baseline event is
    # resolved, a later refresh re-extracting it does not reopen it.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    decided = {**DOCKET, "date_terminated": "2026-09-01", "disposition": "Petition denied"}
    _pull(FakeClient(decided, [{"id": 1, "description": "Order denying the petition"}]), tmp_path)
    assert open_events(db, "ca9", 64512345) == []
    assert resolved_events(db, "ca9", 64512345) == ["evt-appeal-disposition"]
    # Refresh again against the same decided docket — the event stays resolved.
    _pull(FakeClient(decided, [{"id": 1, "description": "Order denying the petition"}]), tmp_path)
    assert open_events(db, "ca9", 64512345) == []
    assert resolved_events(db, "ca9", 64512345) == ["evt-appeal-disposition"]


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


def test_in_predict_scope_excludes_eligible_but_out_of_scope_cases(tmp_path: Path) -> None:
    # The queue-time gate matches the matrix backstop: a SCOTUS-eligible case is still
    # out of scope if an exclusion predicate matches, so pull never queues it (and so
    # never files an all-out-of-scope, empty predict run).
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # eligible + in scope (recent Term) -> predictable
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-101",
                    predict_eligible=True,
                ),
                # eligible but stale-unresolvable (#333) -> out of scope
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="93-7515",
                    predict_eligible=True,
                ),
                # SCOTUS-touched but not eligible -> out (the existing latch)
                corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24-9"),
                # eligible but a bare bulk-import row whose snapshot links an
                # opinion cluster (#438) -> out via the snapshot-aware rule
                corpus.CorpusRow(case_id="scotus/4", court="scotus", predict_eligible=True),
            ],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/4",
            date(2026, 7, 2),
            {"id": 4, "clusters": ["https://example/clusters/88494/"]},
        )
    assert _in_predict_scope(db, "scotus/1") is True
    assert _in_predict_scope(db, "scotus/2") is False
    assert _in_predict_scope(db, "scotus/3") is False
    assert _in_predict_scope(db, "scotus/4") is False


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


class TimeoutClient:
    """Every fetch raises a transient transport error (a degraded upstream)."""

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        raise httpx.ReadTimeout("The read operation timed out")

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:  # pragma: no cover
        return []


class BudgetClient:
    """Every fetch raises RateBudgetExceeded (the API budget is spent)."""

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        raise RateBudgetExceeded("next request must wait 3000s, over the 300s bound")

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:  # pragma: no cover
        return []


def test_pull_cases_stops_at_the_deadline_and_defers_the_rest(tmp_path: Path) -> None:
    # A degraded upstream must degrade the run, not hang it into the CI job
    # timeout: past the deadline the rotation stops between cases, defers the
    # unreached slice, and keeps everything already refreshed.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    client = _scotus_ca9_client()
    clock = iter([0.0, 100.0])  # first case starts pre-deadline, second is past it

    queues = pull_cases(
        cast(CourtListenerClient, client),
        db,
        tmp_path / "data",
        [("scotus", 900), ("ca9", 901)],
        deadline=50.0,
        time_fn=lambda: next(clock),
    )

    # The first case refreshed fully; the second was deferred, not failed.
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/900") is not None
        assert corpus.get_row(conn, "ca9/901") is None
    assert queues.stopped == "run deadline reached"
    assert queues.deferred == [{"court": "ca9", "docket": 901}]
    assert queues.failed == []


def test_consecutive_transient_failures_trip_the_breaker(tmp_path: Path) -> None:
    # When the upstream is down, every case burns a full retry cycle of budget
    # and wall clock; after the threshold the rotation stops and defers the rest.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    due = [("scotus", n) for n in range(900, 905)]

    queues = pull_cases(
        cast(CourtListenerClient, TimeoutClient()),
        db,
        tmp_path / "data",
        due,
        max_consecutive_transient_failures=2,
    )

    assert [f["docket"] for f in queues.failed] == [900, 901]
    assert queues.stopped == "2 consecutive transient REST failures"
    assert [d["docket"] for d in queues.deferred] == [902, 903, 904]


def test_deterministic_failures_never_trip_the_breaker(tmp_path: Path) -> None:
    # 404s are per-docket conditions, not upstream degradation: a run of them
    # must not stop the rotation.
    db = corpus.corpus_db_path(tmp_path / "corpus")

    class All404Client:
        def get_docket(self, docket_id: int) -> dict[str, Any]:
            raise httpx.HTTPStatusError(
                "404 Not Found",
                request=httpx.Request("GET", f"https://example/dockets/{docket_id}/"),
                response=httpx.Response(404),
            )

        def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:  # pragma: no cover
            return []

    queues = pull_cases(
        cast(CourtListenerClient, All404Client()),
        db,
        tmp_path / "data",
        [("scotus", n) for n in range(900, 904)],
        max_consecutive_transient_failures=2,
    )

    assert len(queues.failed) == 4  # every case tried; none deferred
    assert queues.stopped is None
    assert queues.deferred == []


def test_exhausted_api_budget_stops_the_rotation(tmp_path: Path) -> None:
    # RateBudgetExceeded means every later case would hit the same wall this
    # window: stop at once and defer them all.
    db = corpus.corpus_db_path(tmp_path / "corpus")

    queues = pull_cases(
        cast(CourtListenerClient, BudgetClient()),
        db,
        tmp_path / "data",
        [("scotus", 900), ("ca9", 901)],
    )

    assert queues.stopped is not None
    assert queues.stopped.startswith("API budget exhausted")
    assert [d["docket"] for d in queues.deferred] == [900, 901]
    assert queues.failed == []


def test_format_refresh_failures_surfaces_each_cases_reason() -> None:
    """``pull-all`` echoes every failed docket alongside its recorded reason."""
    assert _format_refresh_failures([]) == ""
    failed: list[dict[str, object]] = [
        {"court": "scotus", "docket": 900, "reason": "ReadTimeout: read timed out"},
    ]
    summary = _format_refresh_failures(failed)
    assert summary.startswith(" (1 failed: ")
    assert "scotus/900 [ReadTimeout: read timed out]" in summary


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


# --- linked-cluster enrichment for dateless dockets ------------------------------

CLUSTER_URL = "https://www.courtlistener.com/api/rest/v4/clusters/85157/"


def _dateless_docket(**kw: Any) -> dict[str, Any]:
    """A historical bulk-era docket: no decision-time dates, one linked cluster."""
    base: dict[str, Any] = {
        "id": 64512345,
        "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
        "docket_number": "21-55555",
        "case_name": "Doe v. Roe",
        "clusters": [CLUSTER_URL],
    }
    base.update(kw)
    return base


def test_dateless_docket_gains_decision_facts_from_its_cluster(tmp_path: Path) -> None:
    # The recoverability probe's headline finding: the docket carries no dates
    # even on a fresh fetch, but its cluster holds the decision date, citation,
    # and (sometimes) a disposition string. One extra request recovers them all.
    client = FakeClient(
        _dateless_docket(),
        [],
        clusters={
            85157: {
                "id": 85157,
                "date_filed": "1993-11-29",
                "disposition": "Petition denied",
                "citations": [{"volume": 510, "reporter": "U.S.", "page": "992"}],
            }
        },
    )
    result = _pull(client, tmp_path)
    assert client.cluster_fetches == 1
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
        snapshot = corpus.latest_snapshot(conn, "ca9/64512345")
    assert row is not None
    assert row.date_decided == date(1993, 11, 29)
    assert row.disposition == "denied"
    assert row.citations == ["510 U.S. 992"]
    # The snapshot stays the raw docket: enrichment feeds only the normalized row.
    assert snapshot is not None
    assert "date_decided" not in snapshot[1]
    assert result.changed is True


def test_cluster_date_alone_dates_the_row_and_routes_to_reconcile(tmp_path: Path) -> None:
    # The realistic cert-denial shape: the cluster carries the date and the
    # reporter cite but no disposition text — the date is the win (the replay
    # clock anchors), and the still-unlabeled outcome goes to the agent.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-review",
                    case_id="ca9/64512345",
                    court="ca9",
                    kind=EventKind.petition,
                    title="Petition for review",
                )
            ],
        )
    client = FakeClient(
        _dateless_docket(),
        [],
        clusters={85157: {"id": 85157, "date_filed": "1993-11-29", "disposition": ""}},
    )
    result = _pull(client, tmp_path)
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
    assert row is not None
    assert row.date_decided == date(1993, 11, 29)
    assert row.disposition is None
    (req,) = result.reconcile
    assert "not machine-readable" in req.reason


def test_dated_docket_skips_the_cluster_fetch(tmp_path: Path) -> None:
    client = FakeClient(
        _dateless_docket(date_terminated="2022-06-15", disposition="Petition denied"),
        [],
    )
    _pull(client, tmp_path)
    assert client.cluster_fetches == 0


def test_dateless_docket_without_cluster_skips_the_fetch(tmp_path: Path) -> None:
    client = FakeClient(_dateless_docket(clusters=[]), [])
    _pull(client, tmp_path)
    assert client.cluster_fetches == 0


def test_cluster_fetch_failure_never_fails_the_refresh(tmp_path: Path) -> None:
    # No canned cluster -> the fake 404s; the refresh proceeds unenriched.
    client = FakeClient(_dateless_docket(), [])
    result = _pull(client, tmp_path)
    assert client.cluster_fetches == 1
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
    assert row is not None and row.date_decided is None
    assert result.case_id == "ca9/64512345"


def test_docket_level_facts_win_over_the_cluster(tmp_path: Path) -> None:
    # Gap-fill only: a docket carrying its own disposition text keeps it even
    # when the cluster disagrees; the cluster still supplies the missing date.
    client = FakeClient(
        _dateless_docket(disposition="Petition dismissed"),
        [],
        clusters={
            85157: {"id": 85157, "date_filed": "1993-11-29", "disposition": "Petition denied"}
        },
    )
    _pull(client, tmp_path)
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        row = corpus.get_row(conn, "ca9/64512345")
    assert row is not None
    assert row.disposition == "dismissed"
    assert row.date_decided == date(1993, 11, 29)
