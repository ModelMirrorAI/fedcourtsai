"""The historical Term walker (the run-seed workflow): sampling, cursors, caps."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus
from fedcourtsai.config import HistoricalConfig, load_historical_config
from fedcourtsai.pipeline import historical as historical_module
from fedcourtsai.pipeline.historical import (
    HistoricalReport,
    StreamProgress,
    fold_totals,
    load_terms,
    render_markdown,
)
from fedcourtsai.pipeline.live import ingest_live_payload
from fedcourtsai.schemas import EventKind
from fedcourtsai.supremecourt import SupremeCourtClient, live_docket_id
from tests.conftest import FixtureCorpus, seed_prediction
from tests.test_documents import _pdf
from tests.test_live import _DENIED_ENTRY, _GRANTED_ENTRY, _client, _payload

_DISMISSED_ENTRY = {"Date": "Jul 06 2026", "Text": "Petition for a writ of certiorari dismissed."}


def _decided(number: str, order: dict[str, Any]) -> dict[str, Any]:
    """A decided petition payload: the filing entry plus its disposition order."""
    return _payload(number, proceedings=[_payload()["ProceedingsandOrder"][0], order])


def _config(**overrides: Any) -> HistoricalConfig:
    defaults: dict[str, Any] = {
        "terms": [22],
        "denial_sample_every": 3,
        "max_probes_per_run": 100,
        # No document fetching unless a test opts in.
        "document_floor_term": 99,
    }
    defaults.update(overrides)
    return HistoricalConfig.model_validate(defaults)


def _serving_client(
    served: dict[str, dict[str, Any]], calls: list[str] | None = None
) -> SupremeCourtClient:
    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if calls is not None:
            calls.append(name)
        if name in served:
            return httpx.Response(200, json=served[name])
        return httpx.Response(404)

    return _client(handler)


# --- sampling ---------------------------------------------------------------------


def test_all_grants_kept_and_denials_sampled_every_nth(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {
        "22-1": _decided("22-1", _DENIED_ENTRY),  # 1 % 3 != 0 -> sampled out
        "22-2": _decided("22-2", _GRANTED_ENTRY),  # grant -> always kept
        "22-3": _decided("22-3", _DENIED_ENTRY),  # 3 % 3 == 0 -> kept
        "22-4": _decided("22-4", _DISMISSED_ENTRY),  # other decided -> kept
        "22-5": _payload("22-5"),  # no disposition -> skipped entirely
        "22-5001": _decided("22-5001", _DENIED_ENTRY),  # IFP; 5001 % 3 == 0 -> kept
    }
    with _serving_client(served) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))

    assert report.ingested_granted == 1
    assert report.ingested_denied == 2  # 22-3 and 22-5001
    assert report.ingested_other == 1  # the dismissal
    assert report.skipped_denials == 1  # 22-1
    assert report.skipped_undecided == 1  # 22-5
    assert report.served == 6
    assert report.complete is True and report.stopped == "complete"

    with corpus.connect(db) as conn:
        kept = {
            r.case_id: r
            for r in (
                corpus.get_row(conn, f"scotus/{d}")
                for d in (
                    9_022_000_002,
                    9_022_000_003,
                    9_022_000_004,
                    9_022_005_001,
                )
            )
            if r is not None
        }
        sampled_out = corpus.get_row(conn, "scotus/9022000001")
        undecided = corpus.get_row(conn, "scotus/9022000005")
    assert set(kept) == {
        "scotus/9022000002",
        "scotus/9022000003",
        "scotus/9022000004",
        "scotus/9022005001",
    }
    assert sampled_out is None and undecided is None
    # Every ingested row lands already resolved: the machine-read label (the
    # back-test target the replay scores against), the raw JSON as its dated
    # snapshot, and its cert event formed and latched resolved.
    assert kept["scotus/9022000002"].disposition == "granted"
    assert kept["scotus/9022000003"].disposition == "denied"
    assert kept["scotus/9022000004"].disposition == "dismissed"
    with corpus.connect(db) as conn:
        snap = corpus.latest_snapshot(conn, "scotus/9022000002")
        events = corpus.events_for_case(conn, "scotus/9022000002")
    assert snap is not None and snap[1] == served["22-2"]
    assert [e.event_id for e in events] == ["evt-petition-disposition"]
    assert all(e.resolved for e in events)


def test_gvr_counts_as_a_grant_in_the_walk_report(tmp_path: Path) -> None:
    # A GVR is a grant, so a walked gvr docket increments ingested_granted (not
    # ingested_other) — the regression if the counter keyed on `granted` alone.
    gvr_entry = {
        "Date": "Jul 06 2026",
        "Text": "Judgment VACATED and case REMANDED for further consideration in light of X v. Y.",
    }
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with _serving_client({"22-2": _decided("22-2", gvr_entry)}) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    assert report.ingested_granted == 1
    assert report.ingested_other == 0
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/9022000002")
    assert row is not None and row.disposition == "gvr"


def test_loader_feeds_no_predict_queue(tmp_path: Path) -> None:
    """Ingested petitions are decided history: their events land resolved, the
    pending rotation never picks them, and the loader emits no queues at all."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {"22-3": _decided("22-3", _DENIED_ENTRY), "22-2": _decided("22-2", _GRANTED_ENTRY)}
    with _serving_client(served) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    assert report.ingested_granted + report.ingested_denied == 2
    with corpus.connect(db) as conn:
        assert corpus.live_rotation(conn, limit=10) == []
        events = corpus.events_for_case(conn, "scotus/9022000002")
    assert events and all(e.resolved for e in events)


# --- cursors: resume, never re-probe ------------------------------------------------


def test_probe_cap_stops_the_walk_and_the_next_run_resumes(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {f"22-{n}": _decided(f"22-{n}", _GRANTED_ENTRY) for n in (1, 2, 3, 4)}

    calls_first: list[str] = []
    with _serving_client(served, calls_first) as client:
        first = load_terms(
            client,
            db,
            tmp_path / "data",
            _config(max_probes_per_run=2),
            today=date(2026, 7, 10),
        )
    assert first.probed == 2 and first.stopped == "probe-cap"
    assert first.complete is False
    assert calls_first == ["22-1", "22-2"]
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 2
        assert corpus.get_live_cursor(conn, 22, "historical-ifp") is None

    # The next invocation resumes past the cursor — earlier serials (including
    # any sampled-out denial) are never re-probed.
    calls_second: list[str] = []
    with _serving_client(served, calls_second) as client:
        second = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 11))
    assert calls_second[0] == "22-3"
    assert "22-1" not in calls_second and "22-2" not in calls_second
    assert second.ingested_granted == 2  # 22-3 and 22-4
    assert second.complete is True
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 4


def test_sampled_out_denial_advances_the_cursor(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {"22-1": _decided("22-1", _DENIED_ENTRY)}  # 1 % 3 != 0 -> skipped
    with _serving_client(served) as client:
        load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 1


def test_historical_cursors_never_collide_with_the_forward_pollers(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 22, "paid", 500)  # the forward frontier
    with _serving_client({"22-1": _decided("22-1", _GRANTED_ENTRY)}) as client:
        load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "paid") == 500  # untouched
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 1


def test_legacy_cursor_names_migrate_in_place_and_the_walk_resumes(tmp_path: Path) -> None:
    """A corpus carrying the walker's earlier cursor names resumes gap-free: the
    old-named rows are renamed at walk start (idempotently — a re-run with no
    legacy rows is a no-op) and the walk continues past the migrated serial."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 22, "seed-paid", 2)
        corpus.set_live_cursor(conn, 22, "seed-ifp", 5001)
    served = {f"22-{n}": _decided(f"22-{n}", _GRANTED_ENTRY) for n in (1, 2, 3)}
    calls: list[str] = []
    with _serving_client(served, calls) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    # The walk resumed past the migrated serial: 22-1 / 22-2 were never re-probed.
    assert calls[0] == "22-3"
    assert report.ingested_granted == 1
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 3
        assert corpus.get_live_cursor(conn, 22, "historical-ifp") == 5001
        assert corpus.get_live_cursor(conn, 22, "seed-paid") is None
        assert corpus.get_live_cursor(conn, 22, "seed-ifp") is None


def test_legacy_cursor_migration_keeps_the_further_cursor_on_collision(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 22, "seed-paid", 7)
        corpus.set_live_cursor(conn, 22, "historical-paid", 3)  # behind the legacy row
        migrated = corpus.rename_live_streams(conn, {"seed-paid": "historical-paid"})
    assert migrated == 1
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 7
        assert corpus.get_live_cursor(conn, 22, "seed-paid") is None


def test_legacy_cursor_migration_never_rewinds_a_further_new_cursor(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 22, "historical-paid", 9)  # ahead of the legacy row
        corpus.set_live_cursor(conn, 22, "seed-paid", 3)
        corpus.rename_live_streams(conn, {"seed-paid": "historical-paid"})
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 9  # forward-only
        assert corpus.get_live_cursor(conn, 22, "seed-paid") is None


def test_legacy_cursor_migration_is_a_no_op_when_clean(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 22, "seed-paid", 5)
        first = corpus.rename_live_streams(conn, {"seed-paid": "historical-paid"})
        second = corpus.rename_live_streams(conn, {"seed-paid": "historical-paid"})
    assert (first, second) == (1, 0)
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 5


# --- the watchlist guard -------------------------------------------------------------


def test_decided_petition_with_open_predicted_event_is_left_to_the_watchlist(
    tmp_path: Path,
) -> None:
    """A serial resolving to an existing case with an open, predicted event is
    never ingested here: the walker files no evaluate handoffs, so recording the
    outcome would strand the committed prediction unscored — the watchlist's
    re-poll owns that resolution. The cursor still advances (never re-probed)."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/74112233", court="scotus", docket_number="22-2")],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/74112233",
                    court="scotus",
                    kind=EventKind.petition,
                )
            ],
        )
    seed_prediction(data_root, "scotus", 74112233, "evt-petition-disposition")

    with _serving_client({"22-2": _decided("22-2", _GRANTED_ENTRY)}) as client:
        report = load_terms(client, db, data_root, _config(), today=date(2026, 7, 10))

    assert report.left_to_watchlist == 1
    assert report.ingested_granted == 0
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/74112233")
        assert row is not None and row.disposition is None  # untouched, watchlist's to resolve
        events = corpus.events_for_case(conn, "scotus/74112233")
        assert all(not e.resolved for e in events)
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 2  # never re-probed


def test_decided_petition_with_open_but_unpredicted_event_is_still_ingested(
    tmp_path: Path,
) -> None:
    """No prediction, nothing to score: the walker may land the resolution."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/74112233", court="scotus", docket_number="22-2")],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/74112233",
                    court="scotus",
                    kind=EventKind.petition,
                )
            ],
        )
    with _serving_client({"22-2": _decided("22-2", _GRANTED_ENTRY)}) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    assert report.left_to_watchlist == 0
    assert report.ingested_granted == 1
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/74112233")
    assert row is not None and row.disposition == "granted"


def test_time_cap_stops_the_walk(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {f"22-{n}": _decided(f"22-{n}", _GRANTED_ENTRY) for n in (1, 2, 3)}
    ticks = iter(range(100))
    with _serving_client(served) as client:
        report = load_terms(
            client,
            db,
            tmp_path / "data",
            _config(max_run_minutes=2 / 60),  # a 2-second budget on a 1s/tick clock
            today=date(2026, 7, 10),
            clock=lambda: float(next(ticks)),
        )
    assert report.stopped == "time-cap"
    assert report.complete is False
    assert report.probed < 6  # the walk stopped early, mid-Term


def test_stream_error_stops_the_stream_but_not_the_walk(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")

    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if name.startswith("22-5"):  # the IFP stream (5001+) works
            if name == "22-5001":
                return httpx.Response(200, json=_decided("22-5001", _GRANTED_ENTRY))
            return httpx.Response(404)
        return httpx.Response(500)  # the paid stream is degraded

    with _client(handler) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    assert [f["stream"] for f in report.failed] == ["historical-paid"]
    assert report.ingested_granted == 1  # the IFP stream still walked
    assert report.complete is False and report.stopped == "stream-errors"
    with corpus.connect(db) as conn:
        # The failed stream's cursor is untouched: the retry is gap-free.
        assert corpus.get_live_cursor(conn, 22, "historical-paid") is None
        assert corpus.get_live_cursor(conn, 22, "historical-ifp") == 5001


# --- identity reconciliation --------------------------------------------------------


def test_loader_enriches_an_existing_courtlistener_row(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/74112233", court="scotus", docket_number="22-2")],
        )
    with _serving_client({"22-2": _decided("22-2", _GRANTED_ENTRY)}) as client:
        load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/9022000002") is None  # no live mint
        enriched = corpus.get_row(conn, "scotus/74112233")
    assert enriched is not None
    assert enriched.disposition == "granted"
    assert enriched.case_name == "Doe, et al. v. Roe"


# --- documents: the OT2021+ floor ---------------------------------------------------


def test_documents_fetched_only_from_the_floor_term_up(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    pdf = _pdf("QUESTION PRESENTED Whether Z. PARTIES TO THE PROCEEDING Acme.")
    rich = _decided("22-2", _GRANTED_ENTRY)
    rich["ProceedingsandOrder"][0]["Links"] = [
        {"Description": "Petition", "DocumentUrl": "https://example/22.pdf"}
    ]
    old = _decided("20-2", _GRANTED_ENTRY)
    old["ProceedingsandOrder"][0]["Links"] = [
        {"Description": "Petition", "DocumentUrl": "https://example/20.pdf"}
    ]
    served = {"22-2": rich, "20-2": old}
    doc_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith(".pdf"):
            doc_urls.append(url)
            return httpx.Response(200, content=pdf)
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if name in served:
            return httpx.Response(200, json=served[name])
        return httpx.Response(404)

    with _client(handler) as client:
        report = load_terms(
            client,
            db,
            tmp_path / "data",
            _config(terms=[22, 20], document_floor_term=21),
            today=date(2026, 7, 10),
        )
    # Only the at-or-above-floor Term's documents were fetched at all.
    assert doc_urls == ["https://example/22.pdf"]
    assert report.documents == 2  # petition + derived questions-presented
    with corpus.connect(db) as conn:
        rich_docs = corpus.documents_for_case(conn, "scotus/9022000002")
        old_docs = corpus.documents_for_case(conn, "scotus/9020000002")
    assert {d.kind for d in rich_docs} == {"petition", "questions-presented"}
    assert old_docs == []


# --- config -------------------------------------------------------------------------


def test_load_historical_config_reads_section_and_defaults(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text("historical:\n  denial_sample_every: 5\n")
    cfg = load_historical_config(tmp_path)
    assert cfg.denial_sample_every == 5
    assert cfg.terms == [25, 24, 23, 22, 21, 20, 19, 18, 17]  # default holds

    defaults = load_historical_config(tmp_path / "absent")
    assert defaults.max_probes_per_run == 600
    assert defaults.document_floor_term == 21


def test_historical_config_rejects_terms_below_the_probe_floor() -> None:
    with pytest.raises(ValueError, match="October Terms >= 17"):
        HistoricalConfig.model_validate({"terms": [16]})


def test_repo_tracking_yaml_carries_historical_section() -> None:
    cfg = load_historical_config(Path("config"))
    assert cfg.terms[0] == 25 and cfg.terms[-1] == 17
    assert cfg.denial_sample_every == 10
    assert cfg.document_floor_term == 21


def test_fold_totals_sums_counts_and_keeps_latest_walk_state() -> None:
    chunk1 = HistoricalReport(
        probed=600,
        served=580,
        ingested_granted=3,
        ingested_denied=50,
        skipped_denials=520,
        stopped="probe-cap",
        streams=[
            StreamProgress(term=24, stream="historical-paid", cursor=598, frontier_reached=False)
        ],
    )
    chunk2 = HistoricalReport(
        probed=40,
        served=30,
        ingested_denied=3,
        skipped_denials=27,
        complete=True,
        stopped="complete",
        streams=[
            StreamProgress(term=24, stream="historical-paid", cursor=620, frontier_reached=True),
            StreamProgress(term=24, stream="historical-ifp", cursor=5005, frontier_reached=True),
        ],
    )
    totals = fold_totals(fold_totals(None, chunk1), chunk2)
    assert totals.probed == 640 and totals.served == 610
    assert totals.ingested_granted == 3 and totals.ingested_denied == 53
    assert totals.skipped_denials == 547
    assert totals.complete is True and totals.stopped == "complete"
    # The latest invocation's per-stream state wins; nothing is double-counted.
    by_key = {(s.term, s.stream): s for s in totals.streams}
    assert by_key[(24, "historical-paid")].cursor == 620
    assert by_key[(24, "historical-paid")].frontier_reached is True
    assert by_key[(24, "historical-ifp")].cursor == 5005


# --- the progress rendering ---------------------------------------------------------


def test_render_markdown_carries_counts_and_stream_table() -> None:
    report = HistoricalReport(
        probed=10,
        served=8,
        ingested_granted=1,
        ingested_denied=2,
        skipped_denials=5,
        complete=True,
        streams=[
            {"term": 22, "stream": "historical-paid", "cursor": 8, "frontier_reached": True},
        ],
    )
    body = render_markdown(report)
    assert "walk complete" in body
    assert "**10** serial(s)" in body
    assert "| 22 | historical-paid | 8 | ✅ |" in body


# --- sample weights + the persisted frontier ----------------------------------------


def test_walker_stamps_weights_and_the_frontier(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {
        "22-2": _decided("22-2", _GRANTED_ENTRY),  # kept with certainty -> weight 1
        "22-3": _decided("22-3", _DENIED_ENTRY),  # 3 % 3 == 0 -> sampled -> weight 3
    }
    with _serving_client(served) as client:
        report = load_terms(client, db, tmp_path / "data", _config(), today=date(2026, 7, 10))
    assert report.complete is True
    with corpus.connect(db) as conn:
        granted = corpus.get_row(conn, "scotus/9022000002")
        denied = corpus.get_row(conn, "scotus/9022000003")
        # A completed walk persists where the end was observed, per stream.
        assert corpus.get_live_frontier(conn, 22, "historical-paid") == corpus.get_live_cursor(
            conn, 22, "historical-paid"
        )
    assert granted is not None and granted.sample_weight == 1
    assert denied is not None and denied.sample_weight == 3


def test_capped_walk_leaves_no_frontier_stamp(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {"22-1": _decided("22-1", _GRANTED_ENTRY), "22-2": _decided("22-2", _GRANTED_ENTRY)}
    with _serving_client(served) as client:
        report = load_terms(
            client,
            db,
            tmp_path / "data",
            _config(max_probes_per_run=1),
            today=date(2026, 7, 10),
        )
    assert report.stopped == "probe-cap"
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 22, "historical-paid") == 1
        assert corpus.get_live_frontier(conn, 22, "historical-paid") is None


def test_load_terms_backfills_precapture_live_rows(tmp_path: Path) -> None:
    # A pre-capture live row (NULL weight and signals) is healed by the walk's
    # start-of-run backfill before any probing happens.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    stale = ingest_live_payload(
        db,
        data_root,
        _decided("22-3", _DENIED_ENTRY),
        live_docket_id(22, 3),
        today=date(2026, 7, 1),
    )
    with corpus.connect(db) as conn, conn:
        conn.execute(
            "UPDATE cases SET sample_weight = NULL, distribution_count = NULL WHERE case_id = ?",
            (stale.case_id,),
        )
        corpus.set_live_cursor(conn, 22, "historical-paid", 3)
    with _serving_client({}) as client:
        load_terms(client, db, data_root, _config(), today=date(2026, 7, 10))
    with corpus.connect(db) as conn:
        healed = corpus.get_row(conn, stale.case_id)
    assert healed is not None
    assert healed.sample_weight == 3  # denied, on the grid, cursor-covered
    assert healed.distribution_count == 0  # re-parsed from the stored snapshot


@pytest.mark.parametrize(
    ("cli_args", "expected_minutes"),
    [
        (["--max-run-seconds", "90"], 1.5),  # 90s < config → the override binds
        (["--max-run-seconds", "6000"], 20.0),  # 100min > config → clamped to config
        ([], 20.0),  # no flag → the config default is untouched
    ],
)
def test_cli_max_run_seconds_only_lowers_walker_budget(
    fixture_corpus: FixtureCorpus,
    monkeypatch: pytest.MonkeyPatch,
    cli_args: list[str],
    expected_minutes: float,
) -> None:
    """The run-pull loop feeds its remaining budget as ``--max-run-seconds`` so
    the final chunk stops itself before the job's hard timeout. It can only
    LOWER the walker's wall clock (never raise it past ``historical.
    max_run_minutes``), mirroring ``--max-probes`` — and leaves the probe cap
    alone."""
    captured: dict[str, float] = {}

    def _fake_load_terms(
        client: object, db: object, data_root: object, config: HistoricalConfig, **kwargs: object
    ) -> HistoricalReport:
        captured["max_run_minutes"] = config.max_run_minutes
        captured["max_probes_per_run"] = config.max_probes_per_run
        return HistoricalReport(stopped="time-cap")

    monkeypatch.setattr(historical_module, "load_terms", _fake_load_terms)
    result = CliRunner().invoke(cli.app, ["historical-terms", *cli_args])
    assert result.exit_code == 0, result.output
    assert captured["max_run_minutes"] == pytest.approx(expected_minutes)
    assert captured["max_probes_per_run"] == 600  # this option never disturbs the probe cap


def test_cli_max_run_seconds_rejects_non_positive(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-positive budget would make the walk a silent no-op (model_copy
    bypasses the field's gt=0 check), so the option is bounded at the boundary:
    ``0`` is a Click usage error (exit 2) and the walker never runs."""
    ran = False

    def _fake_load_terms(*args: object, **kwargs: object) -> HistoricalReport:
        nonlocal ran
        ran = True
        return HistoricalReport()

    monkeypatch.setattr(historical_module, "load_terms", _fake_load_terms)
    result = CliRunner().invoke(cli.app, ["historical-terms", "--max-run-seconds", "0"])
    # Exit 2 is Click's canonical bad-parameter code; asserting on the rendered
    # error text is brittle (Rich wraps the option name at narrow terminal
    # widths). The walker not running proves the boundary rejected the value.
    assert result.exit_code == 2
    assert ran is False
