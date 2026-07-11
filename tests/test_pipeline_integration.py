"""Offline end-to-end regression for the pull → outcome cascade.

The per-module suites (``test_pull``, ``test_outcome``, ``test_discover``,
``test_store`` …) each prove one stage in isolation. Nothing there drives the
stages *through a shared corpus in one flow*, so a regression in how they
compose — a queue that stops being written in the shape the workflow reads, an
outcome that stops escalating, a rotation that stops skipping resolved cases —
would land silently in CI.

This test wires them together against a single ``tmp_path`` corpus using the
same in-memory fakes the unit suites use, and asserts the **composition** the
units do not: that onboarded rows are what ``pull`` later rotates over, that an
onboarding-defined event is what a later resolution attaches an ``outcome.json``
to, that ``pull-all`` emits the queue payloads ``run-pull.yml`` consumes, that
the deterministic-first / agent-fallback outcome split runs through the real
``pull`` + ``outcome`` code paths, and that oldest-first / skip-resolved
rotation holds across two rounds over the shared corpus.
"""

from pathlib import Path
from typing import Any, cast

from fedcourtsai import corpus
from fedcourtsai.courtlistener import CourtListenerClient
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.events import extract_events
from fedcourtsai.pipeline.ingest import from_api_docket, upsert_to_corpus
from fedcourtsai.pipeline.pull import pull_cases
from fedcourtsai.schemas import EventKind
from fedcourtsai.store import cases_due_for_pull
from tests.conftest import seed_prediction

_EVENT_ID = "evt-appeal-disposition"


class FakeCourtListenerClient:
    """Pull-side stand-in: canned dockets/entries keyed by docket id.

    Mirrors the ``FakeClient`` shapes in ``test_pull`` / ``test_discover`` but
    serves a *set* of dockets so a rotation pass can refresh several cases.
    """

    def __init__(
        self,
        dockets: dict[int, dict[str, Any]],
        entries: dict[int, list[dict[str, Any]]] | None = None,
    ) -> None:
        self._dockets = dockets
        self._entries = entries or {}

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return self._dockets[docket_id]

    def iter_docket_entries(self, docket_id: int) -> list[dict[str, Any]]:
        return self._entries.get(docket_id, [])


def _client(client: FakeCourtListenerClient) -> CourtListenerClient:
    return cast(CourtListenerClient, client)


def _docket(docket_id: int, court: str = "ca9", **kw: Any) -> dict[str, Any]:
    # The docket's own court must match the onboarded row so the refresh updates
    # it in place (the normalizer derives case_id from this url, not the call args).
    return {
        "id": docket_id,
        "court": f"https://www.courtlistener.com/api/rest/v4/courts/{court}/",
        "docket_number": f"{docket_id}-x",
        "date_filed": "2021-03-01",
        **kw,
    }


def _onboard(db: Path, docket: dict[str, Any]) -> None:
    """Land one pending docket in the shared corpus through the ingest core.

    The same normalize + upsert + extract seams every production channel runs
    (``pull_case``, the live poller), minus the channel's rotation stamp — so
    the onboarded rows read as never-pulled and the rotation tests below can
    assert the stalest-first ordering from a clean slate.
    """
    row = from_api_docket(docket)
    upsert_to_corpus(db, [row])
    extraction = extract_events(docket)
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, extraction.events)


def _event_ids(db: Path, court: str, docket: int) -> list[str]:
    """The predictable-event ids onboarding recorded in the corpus for one case.

    The forward pipeline reads open/resolved event state from the corpus, so no
    materialization into git is needed: the onboarding-defined event rows are
    already what a later resolution attaches an ``outcome.json`` to. Asserts
    onboarding defined at least one.
    """
    with corpus.connect(db) as conn:
        events = corpus.events_for_case(conn, f"{court}/{docket}")
    assert events, f"onboarding defined no events for {court}/{docket}"
    return [ev.event_id for ev in events]


# --- 1. onboarding → corpus ------------------------------------------------------


def test_onboarding_defines_baseline_events_in_shared_corpus(tmp_path: Path) -> None:
    """Onboarded dockets land rows + their baseline predictable event."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    for docket_id in (1, 2):
        _onboard(db, _docket(docket_id))
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 2
        assert corpus.event_count(conn) == 2
        baseline = corpus.events_for_case(conn, "ca9/1")
    assert [e.event_id for e in baseline] == [_EVENT_ID]
    assert baseline[0].kind == EventKind.appeal and baseline[0].resolved is False


# --- 2 + 3. pull → corpus + queues, and the outcome cascade --------------------


def test_pull_all_queues_and_outcome_cascade(tmp_path: Path) -> None:
    """Onboard, then run the pull-all resolution; assert queue shapes + the split."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"

    # Onboard three pending cases into the shared corpus (the active set).
    for docket_id in (1, 2, 3):
        _onboard(db, _docket(docket_id))

    # The open predictable event each case carries is the one onboarding defined
    # in the corpus — read straight from there (without it, there would be none
    # for a later resolution to attach an outcome to).
    for docket in (1, 2, 3):
        assert _event_ids(db, "ca9", docket) == [_EVENT_ID]

    # ca9/1: machine-readable disposition → deterministic outcome (evaluate).
    # ca9/2: decided but only "affirmed" → ambiguous → reconcile, no outcome.
    # ca9/3: still pending → changed case with an open event → predict.
    client = FakeCourtListenerClient(
        {
            1: _docket(1, date_terminated="2022-06-15", disposition="Petition denied"),
            2: _docket(2, date_terminated="2022-06-15", disposition="affirmed"),
            3: _docket(3),
        }
    )

    due = cases_due_for_pull(db, limit=50)
    assert due == [("ca9", 1), ("ca9", 2), ("ca9", 3)]  # rotation feeds pull the onboarded set

    # The evaluate handoff requires something to score: seed the prediction a
    # predict run would have committed for the case that is about to resolve.
    seed_prediction(data_root, "ca9", 1, _EVENT_ID)

    queues = pull_cases(_client(client), db, data_root, due)

    # Queue payloads are shaped exactly as run-pull.yml's jq reads them.
    for entry in queues.predict + queues.evaluate:
        assert set(entry) >= {"court", "docket", "events"}
        assert isinstance(entry["events"], list) and entry["events"]
    for entry in queues.reconcile:
        assert set(entry) >= {"court", "docket", "events", "reason"}

    # Deterministic-first: ca9/1 gained an outcome and is queued for evaluate, not predict.
    assert {(e["court"], e["docket"]) for e in queues.evaluate} == {("ca9", 1)}
    assert queues.evaluate[0]["events"] == [_EVENT_ID]
    assert CasePaths(data_root, "ca9", 1).event(_EVENT_ID).outcome.exists()
    assert ("ca9", 1) not in {(e["court"], e["docket"]) for e in queues.predict}

    # Agent-fallback: ca9/2 routes to reconcile and writes NO outcome on a guess.
    (recon,) = queues.reconcile
    assert (recon["court"], recon["docket"]) == ("ca9", 2)
    assert "not machine-readable" in cast(str, recon["reason"])
    assert not CasePaths(data_root, "ca9", 2).event(_EVENT_ID).outcome.exists()

    # ca9/3: changed + open event → predict handoff.
    assert ("ca9", 3) in {(e["court"], e["docket"]) for e in queues.predict}

    # The corpus learned the dispositions this pull resolved (the row is now labeled).
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "ca9/1").disposition == "denied"  # type: ignore[union-attr]


# --- 4. last_pulled rotation across two rounds ---------------------------------


def test_rotation_is_oldest_first_and_skips_resolved(tmp_path: Path) -> None:
    """Oldest-``last_pulled``-first + skip-resolved holds across two pull rounds."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"

    for docket_id in range(4):
        _onboard(db, _docket(docket_id, court="ca1"))

    # ca1/0 refreshes as decided (becomes resolved); the rest stay pending.
    client = FakeCourtListenerClient(
        {
            0: _docket(0, court="ca1", date_terminated="2022-06-15", disposition="Petition denied"),
            1: _docket(1, court="ca1"),
            2: _docket(2, court="ca1"),
            3: _docket(3, court="ca1"),
        }
    )

    # Round 1: the two stalest (never-pulled, case_id order) are selected.
    round1 = cases_due_for_pull(db, limit=2)
    assert round1 == [("ca1", 0), ("ca1", 1)]
    pull_cases(_client(client), db, data_root, round1)

    # Round 2: never-pulled cases (2, 3) lead the round-1 case (1) that was just
    # stamped, and the resolved case (0) is dropped from the active set entirely.
    round2 = cases_due_for_pull(db, limit=10)
    assert round2 == [("ca1", 2), ("ca1", 3), ("ca1", 1)]
