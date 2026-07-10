"""Offline end-to-end regression for the seed → pull → outcome cascade.

The per-module suites (``test_seed``, ``test_pull``, ``test_outcome``,
``test_discover``, ``test_store`` …) each prove one stage in isolation. Nothing
there drives the stages *through a shared corpus in one flow*, so a regression in
how they compose — a cursor field that stops round-tripping, a queue that stops
being written in the shape the workflow reads, an outcome that stops escalating,
a rotation that stops skipping resolved cases — would land silently in CI.

This test wires them together against a single ``tmp_path`` corpus using the same
in-memory fakes the unit suites use, and asserts the **composition** the units do
not: that seed defines each docket's predictable event(s) in the shared corpus,
that seeded rows are what ``pull`` later rotates over, that a seed-defined event
is what a later resolution attaches an ``outcome.json`` to, that ``pull-all``
emits the three queue payloads ``run-pull.yml`` consumes, that the
deterministic-first / agent-fallback outcome split runs through the real
``pull`` + ``outcome`` code paths, and that oldest-first / skip-resolved rotation
holds across two rounds over the shared corpus.
"""

from datetime import date
from pathlib import Path
from typing import Any, cast

from fedcourtsai import corpus
from fedcourtsai.courtlistener import CourtListenerClient
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.discover import discover_cases
from fedcourtsai.pipeline.pull import pull_cases
from fedcourtsai.pipeline.seed import backfill, load_cursor, snapshot_date
from fedcourtsai.schemas import EventKind
from fedcourtsai.store import cases_due_for_pull
from tests.conftest import seed_prediction

# Reuse the per-stage fakes exactly as the unit suites define them.
from tests.test_discover import FakeSearch
from tests.test_discover import _docket as _search_docket
from tests.test_seed import FakeBulkSource, _row

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
    # The docket's own court must match the seeded row so the refresh updates it
    # in place (the normalizer derives case_id from this url, not the call args).
    return {
        "id": docket_id,
        "court": f"https://www.courtlistener.com/api/rest/v4/courts/{court}/",
        "docket_number": f"{docket_id}-x",
        "date_filed": "2021-03-01",
        **kw,
    }


def _seed_event_ids(db: Path, court: str, docket: int) -> list[str]:
    """The predictable-event ids *seed* recorded in the corpus for one case.

    The forward pipeline reads open/resolved event state from the corpus, so no
    materialization into git is needed: seed's event rows are already what a later
    resolution attaches an ``outcome.json`` to. Asserts seed defined at least one.
    """
    with corpus.connect(db) as conn:
        events = corpus.events_for_case(conn, f"{court}/{docket}")
    assert events, f"seed defined no events for {court}/{docket}"
    return [ev.event_id for ev in events]


def _seed_courts() -> dict[str, list[dict[str, str]]]:
    return {
        "ca1": [_row("ca1", i) for i in range(5)],
        "ca2": [_row("ca2", i) for i in range(3)],
    }


# --- 1. seed → corpus ----------------------------------------------------------


def test_seed_fills_shared_corpus_without_signing_off(tmp_path: Path) -> None:
    """Backfill across chunks lands rows + advances the cursor; sign-off stays human."""
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    src = FakeBulkSource("2026-Q2", _seed_courts())

    first = backfill(src, cursor_path=cursor, courts=["ca1", "ca2"], corpus_db_path=db, max_cases=4)
    assert first.complete is False
    assert load_cursor(cursor).courts["ca1"].offset == 4
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 4

    final = backfill(src, cursor_path=cursor, courts=["ca1", "ca2"], corpus_db_path=db, max_cases=4)
    assert final.complete is True
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 8  # both courts fully loaded into the shared corpus
        # Seed defines events too: every seeded docket carries its baseline
        # predictable event, so the historical backfill is visible to prediction.
        assert corpus.event_count(conn) == 8
        baseline = corpus.events_for_case(conn, "ca1/0")
        assert [e.event_id for e in baseline] == [_EVENT_ID]
        assert baseline[0].kind == EventKind.appeal and baseline[0].resolved is False
    # Completion is reported, but the maintainer sign-off flag is not flipped
    # automatically — only the completion PR sets it.
    assert load_cursor(cursor).completed is False


# --- 1b. seed → discovery frontier hand-off ------------------------------------


def test_seed_hands_discovery_frontier_to_pull(tmp_path: Path) -> None:
    """Seed sets the frontier from the snapshot date; discovery resumes from it.

    Composition the units don't: that the completed backfill's discovery watermark
    lands at the snapshot's as-of date, that a later forward discovery starts there
    (not at today's last-resort default, which would onboard nothing across the
    snapshot→today gap), and that an empty discovery run never rewinds it.
    """
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path / "corpus")

    # A dated bulk snapshot (2023-Q1) backfills ca9 to completion.
    backfill(
        FakeBulkSource("2023-Q1", {"ca9": [_row("ca9", i) for i in range(3)]}),
        cursor_path=cursor,
        courts=["ca9"],
        corpus_db_path=db,
        max_cases=100,
    )
    snapshot = snapshot_date("2023-Q1")
    assert snapshot == date(2023, 3, 31)
    with corpus.connect(db) as conn:
        # Hand-off: the completed court's watermark is the snapshot's as-of date.
        assert corpus.get_discovery_watermark(conn, "ca9") == snapshot

    # Forward discovery defaulting to "today" would search from 2026 and find
    # nothing; the seed hand-off makes it search from the 2023 snapshot and pick up
    # an April-2023 filing the bulk snapshot was too early to include.
    search = FakeSearch({"ca9": [_search_docket(900, "ca9", "2023-04-15")]})
    today = date(2026, 6, 25)
    result = discover_cases(
        cast(CourtListenerClient, search), db, ["ca9"], max_new=10, default_since=today
    )
    assert search.calls[-1][1] == snapshot  # searched from the snapshot, not today
    assert "ca9/900" in result.case_ids
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2023, 4, 15)

    # A second discovery run that finds nothing must not rewind to default_since:
    # it advances/holds at the date it searched from (the stored watermark).
    empty = FakeSearch({"ca9": []})
    discover_cases(cast(CourtListenerClient, empty), db, ["ca9"], max_new=10, default_since=today)
    assert empty.calls[-1][1] == date(2023, 4, 15)
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2023, 4, 15)


# --- 2 + 3. pull → corpus + queues, and the outcome cascade --------------------


def test_pull_all_queues_and_outcome_cascade(tmp_path: Path) -> None:
    """Seed, then run the pull-all resolution; assert queue shapes + the split."""
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"

    # Seed three pending cases into the shared corpus (these become the active set).
    seed = FakeBulkSource("2026-Q2", {"ca9": [_row("ca9", i) for i in (1, 2, 3)]})
    backfill(seed, cursor_path=cursor, courts=["ca9"], corpus_db_path=db, max_cases=100)

    # The open predictable event each case carries is the one *seed* defined in the
    # corpus — read straight from there (without seed defining events, there would
    # be none for a later resolution to attach an outcome to).
    for docket in (1, 2, 3):
        assert _seed_event_ids(db, "ca9", docket) == [_EVENT_ID]

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
    assert due == [("ca9", 1), ("ca9", 2), ("ca9", 3)]  # rotation feeds pull the seeded set

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
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"

    seed = FakeBulkSource("2026-Q2", {"ca1": [_row("ca1", i) for i in range(4)]})
    backfill(seed, cursor_path=cursor, courts=["ca1"], corpus_db_path=db, max_cases=100)

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
