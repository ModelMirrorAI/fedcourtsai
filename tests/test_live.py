"""The SCOTUS live channel: client, mapping, identity, discovery, poll."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cert_backtest import redact_snapshot
from fedcourtsai.config import LiveConfig, PredictScope, SalienceConfig, load_live_config
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.ingest import (
    CorpusSource,
    backfill_live_signals,
    from_live_docket,
    to_corpus_row,
)
from fedcourtsai.pipeline.live import (
    discover_live,
    ingest_live_payload,
    live_poll_all,
)
from fedcourtsai.schemas import CellFailure, Disposition, Outcome
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.supremecourt import (
    SupremeCourtClient,
    current_october_term,
    is_live_docket_id,
    live_docket_id,
    parse_scotus_docket_number,
)
from tests.conftest import seed_prediction
from tests.test_documents import _pdf

# --- payload fixtures (trimmed real shapes, per docs/live-sources.md) -----


def _payload(
    number: str = "25-100",
    *,
    proceedings: list[dict[str, Any]] | None = None,
    respondent_title: str | None = "Roe, Respondent",
) -> dict[str, Any]:
    return {
        "CaseNumber": f"{number} ",  # the JSON carries a trailing space
        "bCapitalCase": False,
        "sJsonCaseType": "Paid",
        "sJsonTerm": "2025",
        "sJsonCreationDate": "07/10/2026",
        "DocketedDate": "June 2, 2026",
        "PetitionerTitle": "Doe, et al., Petitioners",
        "RespondentTitle": respondent_title,
        "LowerCourt": "United States Court of Appeals for the Ninth Circuit",
        "LowerCourtCaseNumbers": "(23-55501)",
        "Petitioner": [{"PartyName": "Jane Doe", "Attorney": "A. Counsel"}],
        "Respondent": [{"PartyName": "Richard Roe", "Attorney": "B. Counsel"}],
        "ProceedingsandOrder": proceedings
        if proceedings is not None
        else [
            {
                "Date": "Jun 01 2026",
                "Text": "Petition for a writ of certiorari filed.",
                "Links": [{"Description": "Petition", "DocumentUrl": "https://example/p.pdf"}],
            }
        ],
    }


_DENIED_ENTRY = {"Date": "Jul 06 2026", "Text": "Petition DENIED."}
_GRANTED_ENTRY = {"Date": "Jul 06 2026", "Text": "Petition GRANTED limited to Question 1."}
# A Rule 39.8 IFP-denial/dismissal: a terminal SCOTUS order the cert-disposition
# resolver deliberately does not match (many words separate "petition" from
# "dismissed"), so the routing backstop must keep it out of the forward queue.
_RULE_398_ENTRY = {
    "Date": "Oct 20 2025",
    "Text": (
        "Motion for leave to proceed in forma pauperis DENIED and petition for a "
        "writ of habeas corpus DISMISSED. See Rule 39.8."
    ),
}


# --- identity helpers ------------------------------------------------------------


def test_live_docket_id_is_deterministic_and_reserved() -> None:
    assert live_docket_id(25, 100) == 9_025_000_100
    assert live_docket_id(25, 5001) == 9_025_005_001
    assert is_live_docket_id(live_docket_id(17, 1)) is True
    assert is_live_docket_id(73_265_897) is False  # a CourtListener id
    with pytest.raises(ValueError):
        live_docket_id(125, 1)
    with pytest.raises(ValueError):
        live_docket_id(25, 0)


def test_parse_scotus_docket_number_accepts_term_form_only() -> None:
    assert parse_scotus_docket_number("25-100 ") == (25, 100)
    assert parse_scotus_docket_number("22-451") == (22, 451)
    assert parse_scotus_docket_number("22A123") is None  # application
    assert parse_scotus_docket_number("801") is None  # pre-1925 bare number
    assert parse_scotus_docket_number(None) is None


def test_current_october_term_rolls_in_october() -> None:
    assert current_october_term(date(2026, 7, 10)) == 25
    assert current_october_term(date(2026, 10, 6)) == 26


# --- the polite client -----------------------------------------------------------


def _client(handler: Any, sleeps: list[float] | None = None) -> SupremeCourtClient:
    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    record: list[float] = sleeps if sleeps is not None else []
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=record.append)


def test_client_fetches_missing_and_retries() -> None:
    calls: list[str] = []
    flaky = {"seen": False}

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        assert request.headers["User-Agent"] == supremecourt.BROWSER_USER_AGENT
        if request.url.path.endswith("25-100.json"):
            return httpx.Response(200, json=_payload())
        if request.url.path.endswith("25-101.json"):
            if not flaky["seen"]:
                flaky["seen"] = True
                return httpx.Response(500)
            return httpx.Response(200, json=_payload("25-101"))
        if request.url.path.endswith("25-103.json"):
            return httpx.Response(200, text="<html>not json</html>")
        return httpx.Response(404)

    sleeps: list[float] = []
    with _client(handler, sleeps) as client:
        assert client.get_docket(25, 100) is not None
        assert client.get_docket(25, 101) is not None  # 500 then success
        assert client.get_docket(25, 102) is None  # 404
        assert client.get_docket(25, 103) is None  # HTML body -> no docket
    # Paced between requests (not before the first), plus the one retry pause.
    assert sleeps.count(1.0) == 4
    assert supremecourt._RETRY_PAUSE_SECONDS in sleeps
    assert len(calls) == 5


# --- the live mapping ------------------------------------------------------------


def test_from_live_docket_maps_a_pending_petition() -> None:
    row = from_live_docket(_payload(), live_docket_id(25, 100))
    assert row.case_id == "scotus/9025000100"
    assert row.court == "scotus"
    assert row.docket_number == "25-100"
    assert row.case_name == "Doe, et al. v. Roe"
    assert row.date_filed == date(2026, 6, 2)
    assert row.disposition is None and row.date_cert_denied is None
    assert row.parties == sorted(["Jane Doe", "Richard Roe"])
    assert row.attorneys == sorted(["A. Counsel", "B. Counsel"])
    assert row.originating_court == "ca9"
    assert row.originating_docket_number == "23-55501"
    assert row.source == CorpusSource.live


def test_from_live_docket_reads_the_disposition_order() -> None:
    denied = from_live_docket(
        _payload(proceedings=[_payload()["ProceedingsandOrder"][0], _DENIED_ENTRY]),
        live_docket_id(25, 100),
    )
    assert denied.disposition == "denied"
    assert denied.date_cert_denied == date(2026, 7, 6)
    assert denied.date_cert_granted is None

    granted = from_live_docket(_payload(proceedings=[_GRANTED_ENTRY]), live_docket_id(25, 101))
    assert granted.disposition == "granted"
    assert granted.date_cert_granted == date(2026, 7, 6)


def test_from_live_docket_reads_a_bare_gvr_order() -> None:
    # The grant-less GVR ("Judgment VACATED and case REMANDED ... in light of
    # ...") resolves the petition on the granted side and stamps the grant
    # date, so the docket latches instead of lingering pending — an unlatched
    # decided docket keeps its events open and unscoreable.
    gvr_entry = {
        "Date": "May 11 2026",
        "Text": (
            "Judgment VACATED and case REMANDED for further consideration in "
            "light of Louisiana v. Callais."
        ),
    }
    row = from_live_docket(
        _payload(proceedings=[_payload()["ProceedingsandOrder"][0], gvr_entry]),
        live_docket_id(25, 274),
    )
    assert row.disposition == "gvr"
    assert row.date_cert_granted == date(2026, 5, 11)  # a GVR is a grant — dates the grant
    assert row.date_cert_denied is None


def test_from_live_docket_untracked_lower_court_leaves_linkage_unset() -> None:
    payload = _payload()
    payload["LowerCourt"] = "Circuit Court of Michigan, Genesee County"
    row = from_live_docket(payload, live_docket_id(25, 100))
    assert row.originating_court is None
    assert row.originating_docket_number == "23-55501"


def test_in_re_caption_without_respondent() -> None:
    payload = _payload(respondent_title=None)
    payload["PetitionerTitle"] = "In Re Jane Doe, Petitioner"
    row = from_live_docket(payload, live_docket_id(25, 100))
    assert row.case_name == "In Re Jane Doe"


# --- corpus: cursors, lookup, rotation, tracking column --------------------------


def test_live_cursor_roundtrip_and_forward_only(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 25, "paid") is None
        corpus.set_live_cursor(conn, 25, "paid", 120)
        corpus.set_live_cursor(conn, 25, "paid", 90)  # rewind ignored
        assert corpus.get_live_cursor(conn, 25, "paid") == 120
        assert corpus.get_live_cursor(conn, 25, "ifp") is None


def test_scotus_lookup_by_docket_number_normalizes_and_prefers_cl_row(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id="scotus/74112233", court="scotus", docket_number="25-9"),
                corpus.CorpusRow(
                    case_id="scotus/9025000009", court="scotus", docket_number="No. 25-9"
                ),
                corpus.CorpusRow(case_id="ca9/1", court="ca9", docket_number="25-9"),
            ],
        )
        assert corpus.scotus_case_id_by_docket_number(conn, "25-9 ") == "scotus/74112233"
        assert corpus.scotus_case_id_by_docket_number(conn, "25-404") is None
        assert corpus.scotus_case_id_by_docket_number(conn, None) is None


def test_live_rotation_orders_recent_term_then_staleness(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # OT25 never-polled -> first; OT25 polled -> after it.
                corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="25-2"),
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-1",
                    last_live_polled=date(2026, 7, 1),
                ),
                # Older Term follows the current one.
                corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24-3"),
                # Below the Term floor -> excluded.
                corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="16-4"),
                # Decided -> excluded.
                corpus.CorpusRow(
                    case_id="scotus/5",
                    court="scotus",
                    docket_number="25-5",
                    disposition="denied",
                ),
                # Application form -> excluded (not modern cert).
                corpus.CorpusRow(case_id="scotus/6", court="scotus", docket_number="25A6"),
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=f"scotus/{n}",
                    court="scotus",
                    kind="petition",
                    title=f"scotus/{n}",
                )
                for n in (1, 2, 3, 4, 5)
            ],
        )
        picked = [r.case_id for r in corpus.live_rotation(conn, limit=10)]
        assert picked == ["scotus/2", "scotus/1", "scotus/3"]
        # A case with no open event (scotus/6 above) never enters the rotation.


def test_last_live_polled_is_stamped_and_latched(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    row = from_live_docket(_payload(), live_docket_id(25, 100))
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [to_corpus_row(row, last_live_polled=date(2026, 7, 10))])
        # A later CourtListener-side write without the live stamp keeps it.
        corpus.upsert_rows(conn, [to_corpus_row(row, last_pulled=date(2026, 7, 11))])
        stored = corpus.get_row(conn, row.case_id)
    assert stored is not None
    assert stored.last_live_polled == date(2026, 7, 10)
    assert stored.last_pulled == date(2026, 7, 11)


# --- ingest + resolution ----------------------------------------------------------


def test_ingest_live_payload_pending_then_decided(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 100)

    first = ingest_live_payload(db, data_root, _payload(), docket_id, today=date(2026, 7, 9))
    assert first.changed is True and first.resolved == []
    # Identical re-poll: unchanged.
    second = ingest_live_payload(db, data_root, _payload(), docket_id, today=date(2026, 7, 9))
    assert second.changed is False

    # The denial order lands: outcome recorded deterministically, event closed.
    decided_payload = _payload(proceedings=[_payload()["ProceedingsandOrder"][0], _DENIED_ENTRY])
    decided = ingest_live_payload(
        db, data_root, decided_payload, docket_id, today=date(2026, 7, 10)
    )
    assert decided.changed is True
    assert decided.resolved == ["evt-petition-disposition"]
    assert decided.unrecorded_events == []
    outcome_path = (
        CasePaths(data_root, "scotus", docket_id).event("evt-petition-disposition").outcome
    )
    assert outcome_path.exists()
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, first.case_id)
        snap = corpus.latest_snapshot(conn, first.case_id)
    assert stored is not None and stored.disposition == "denied"
    assert snap is not None and snap[1] == decided_payload  # raw JSON is the snapshot


# --- discovery: frontier probing + identity reconciliation ------------------------


def _frontier_client(served: dict[str, dict[str, Any]]) -> SupremeCourtClient:
    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if name in served:
            return httpx.Response(200, json=served[name])
        return httpx.Response(404)

    return _client(handler)


def test_discover_live_onboards_to_the_frontier_and_persists_cursors(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {
        "25-1": _payload("25-1"),
        "25-2": _payload("25-2"),
        "25-5001": _payload("25-5001"),
    }
    with _frontier_client(served) as client:
        found = discover_live(
            client, db, tmp_path / "data", 25, max_new=10, today=date(2026, 7, 10)
        )
    assert found.case_ids == [
        "scotus/9025000001",
        "scotus/9025000002",
        "scotus/9025005001",
    ]
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 25, "paid") == 2
        assert corpus.get_live_cursor(conn, 25, "ifp") == 5001
        events = corpus.events_for_case(conn, "scotus/9025000001")
    assert [e.event_id for e in events] == ["evt-petition-disposition"]

    # The next cycle resumes past the cursor and finds nothing new.
    with _frontier_client(served) as client:
        again = discover_live(
            client, db, tmp_path / "data", 25, max_new=10, today=date(2026, 7, 11)
        )
    assert again.case_ids == []


def test_discover_live_enriches_an_existing_courtlistener_row(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/74112233", court="scotus", docket_number="25-1")],
        )
    with _frontier_client({"25-1": _payload("25-1")}) as client:
        found = discover_live(
            client, db, tmp_path / "data", 25, max_new=10, today=date(2026, 7, 10)
        )
    # Enriched under the existing CourtListener-keyed row; no live mint.
    assert found.case_ids == ["scotus/74112233"]
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/9025000001") is None
        enriched = corpus.get_row(conn, "scotus/74112233")
    assert enriched is not None and enriched.case_name == "Doe, et al. v. Roe"


def test_ingest_live_payload_flags_a_rule_398_terminal_order(tmp_path: Path) -> None:
    # The resolver misses a Rule 39.8 dismissal, so no outcome is recorded (the
    # event stays open) — but termination_signal fires on the same poll.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    docket_id = live_docket_id(25, 5001)
    payload = _payload(
        "25-5001", proceedings=[_payload()["ProceedingsandOrder"][0], _RULE_398_ENTRY]
    )
    result = ingest_live_payload(db, tmp_path / "data", payload, docket_id, today=date(2026, 7, 10))
    assert result.resolved == []  # the cert resolver did not match -> nothing recorded
    assert result.termination_signal is not None and "39.8" in result.termination_signal


def test_live_poll_all_skips_a_decided_looking_terminal_order_forward(tmp_path: Path) -> None:
    # A distributed petition whose latest order is a Rule 39.8 dismissal the
    # resolver missed diverts to predict_skipped_decided — never a forward cell
    # that could read the outcome from its own provisioned snapshot.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    served = {
        "25-5001": _payload(
            "25-5001",
            proceedings=[
                _payload()["ProceedingsandOrder"][0],
                {"Date": "Sep 15 2025", "Text": "DISTRIBUTED for Conference of 10/10/2025."},
                _RULE_398_ENTRY,
            ],
        )
    }
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client, db, data_root, term=25, config=LiveConfig(), today=date(2026, 7, 10)
        )
    assert queues.predict == []
    assert [q["docket"] for q in queues.predict_skipped_decided] == [live_docket_id(25, 5001)]
    assert "39.8" in str(queues.predict_skipped_decided[0]["reason"])


def test_live_poll_all_surfaces_evaluate_skipped_from_the_refresh_path(tmp_path: Path) -> None:
    # A petition that resolves on a refresh poll with no committed prediction to
    # score must surface on evaluate_skipped — the refresh path's queue, which
    # live_poll_all now merges (never silently discarded).
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    config = LiveConfig()
    served = {"25-1": _payload("25-1")}
    with _frontier_client(served) as client:
        live_poll_all(client, db, data_root, term=25, config=config, today=date(2026, 7, 9))
    # Refresh: the pending petition gains its denial order, but nothing predicted it.
    served["25-1"] = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DENIED_ENTRY]
    )
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 7, 10)
        )
    assert queues.evaluate == []
    assert [q["docket"] for q in queues.evaluate_skipped] == [9_025_000_001]


# --- the full cycle ---------------------------------------------------------------


def test_live_poll_all_predicts_on_distribution_and_evaluates_on_resolution(
    tmp_path: Path,
) -> None:
    """Live-channel acceptance: predictions queue on distribution transitions
    (fresh distribution, relist), never on mere docket change; a decided
    petition lands its outcome and queues evaluate."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    config = LiveConfig()

    # Cycle 1: discovery onboards two undistributed pending petitions (they only
    # enter the watchlist) and one already distributed (frontier catch-up -> it
    # queues predict immediately).
    served = {
        "25-1": _payload("25-1"),
        "25-2": _payload("25-2"),
        "25-3": _payload(
            "25-3",
            proceedings=[
                _payload()["ProceedingsandOrder"][0],
                {"Date": "Jul 07 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."},
            ],
        ),
    }
    with _frontier_client(served) as client:
        queues, discovery = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 7, 9)
        )
    assert len(discovery.onboarded) == 3
    assert {q["docket"] for q in queues.predict} == {9_025_000_003}
    assert queues.evaluate == [] and queues.unrecorded == []
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/9025000003")
    assert row is not None and row.distributed_for_conference == date(2026, 9, 29)

    # Cycle 2: 25-1 gains its denial order -> outcome + evaluate, no predict; a
    # BIO lands on 25-2 (docket changed, still undistributed) -> no predict.
    # The evaluate handoff requires a committed prediction (nothing to score
    # otherwise), so seed one for 25-1 as a predict run would have.
    seed_prediction(data_root, "scotus", 9_025_000_001, "evt-petition-disposition")
    served["25-1"] = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DENIED_ENTRY]
    )
    served["25-2"] = _payload(
        "25-2",
        proceedings=[
            _payload()["ProceedingsandOrder"][0],
            {"Date": "Jul 09 2026", "Text": "Brief of respondent in opposition filed."},
        ],
    )
    with _frontier_client(served) as client:
        queues2, _ = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 7, 10)
        )
    assert queues2.evaluate == [
        {"court": "scotus", "docket": 9_025_000_001, "events": ["evt-petition-disposition"]}
    ]
    assert queues2.predict == []

    # Cycle 3: 25-2 is distributed -> the transition queues predict.
    served["25-2"]["ProceedingsandOrder"].append(
        {"Date": "Jul 12 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."}
    )
    with _frontier_client(served) as client:
        queues3, _ = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 7, 13)
        )
    assert queues3.predict == [
        {"court": "scotus", "docket": 9_025_000_002, "events": ["evt-petition-disposition"]}
    ]

    # Cycle 4: unchanged membership -> nothing; then a relist (new conference
    # date) -> predict fires again.
    with _frontier_client(served) as client:
        queues4, _ = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 7, 14)
        )
    assert queues4.predict == []
    served["25-2"]["ProceedingsandOrder"].append(
        {"Date": "Oct 01 2026", "Text": "DISTRIBUTED for Conference of 10/10/2026."}
    )
    with _frontier_client(served) as client:
        queues5, _ = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 10, 2)
        )
    assert queues5.predict == [
        {"court": "scotus", "docket": 9_025_000_002, "events": ["evt-petition-disposition"]}
    ]
    with corpus.connect(db) as conn:
        relisted = corpus.get_row(conn, "scotus/9025000002")
    assert relisted is not None
    assert relisted.distributed_for_conference == date(2026, 10, 10)


def test_live_poll_all_expired_budget_is_a_clean_noop(tmp_path: Path) -> None:
    # A soft budget already spent: the cycle onboards nothing and polls nothing,
    # writing nothing — so a starved window is a no-op, never a partial-write mess.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    served = {"25-1": _payload("25-1")}
    with _frontier_client(served) as client:
        queues, discovery = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            today=date(2026, 7, 9),
            deadline=0.0,
            time_fn=lambda: 5.0,  # already past the deadline
        )
    assert discovery.onboarded == []
    assert queues.predict == [] and queues.evaluate == []
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/9025000001") is None


def test_live_poll_all_soft_budget_stops_the_refresh_partway(tmp_path: Path) -> None:
    # The refresh commits the polls it completes before the budget trips and
    # leaves the rest for next cycle (rotation resumes where it left off) — the
    # anti-livelock property.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    config = LiveConfig()
    distributed = {"Date": "Jul 07 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."}
    served = {
        f"25-{i}": _payload(
            f"25-{i}", proceedings=[_payload()["ProceedingsandOrder"][0], distributed]
        )
        for i in range(1, 5)
    }
    with _frontier_client(served) as client:
        _, discovery = live_poll_all(
            client, db, data_root, term=25, config=config, today=date(2026, 7, 1)
        )
    assert len(discovery.onboarded) == 4  # four distributed, still-pending petitions

    # Cycle 2: max_new=0 makes discovery a no-op that spends no budget (early
    # return before any clock read), so the deadline governs the refresh alone; a
    # clock that ticks once per row trips it after two polls.
    ticks = iter(range(100))
    refresh_only = config.model_copy(update={"max_new_cases_per_run": 0})
    with _frontier_client(served) as client:
        live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=refresh_only,
            today=date(2026, 7, 2),
            deadline=2,
            time_fn=lambda: next(ticks),
        )
    with corpus.connect(db) as conn:
        polled_today = [
            r.case_id
            for r in corpus.iter_rows(conn, court="scotus")
            if r.last_live_polled == date(2026, 7, 2)
        ]
    assert len(polled_today) == 2  # two committed this cycle; the other two wait


def test_conference_parse_last_distribution_wins() -> None:
    payload = _payload(
        proceedings=[
            _payload()["ProceedingsandOrder"][0],
            {"Date": "Mar 08 2023", "Text": "DISTRIBUTED for Conference of 3/24/2023."},
            {"Date": "Mar 08 2023", "Text": "Reply of petitioners filed. (Distributed)"},
            {"Date": "Mar 27 2023", "Text": "DISTRIBUTED for Conference of 3/31/2023."},
        ]
    )
    row = from_live_docket(payload, live_docket_id(25, 100))
    # The relist's date wins; the "(Distributed)" filing suffix never matches.
    assert row.distributed_for_conference == date(2023, 3, 31)


def test_live_rotation_distributed_petitions_lead(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # Undistributed current-Term petition.
                corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="25-1"),
                # Distributed, nearest conference -> first overall despite older Term.
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-2",
                    distributed_for_conference=date(2026, 9, 29),
                ),
                # Distributed for a later conference -> second.
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="25-3",
                    distributed_for_conference=date(2026, 10, 10),
                ),
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=f"scotus/{n}",
                    court="scotus",
                    kind="petition",
                    title=f"scotus/{n}",
                )
                for n in (1, 2, 3)
            ],
        )
        picked = [r.case_id for r in corpus.live_rotation(conn, limit=10)]
        watchlist = [r.case_id for r in corpus.conference_watchlist(conn)]
    assert picked == ["scotus/2", "scotus/3", "scotus/1"]
    assert watchlist == ["scotus/2", "scotus/3"]


def test_conference_date_survives_a_courtlistener_write(tmp_path: Path) -> None:
    # A CourtListener enrichment (no conference parse) must not wipe the live
    # channel's stored membership — the COALESCE latch, like last_live_polled.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="25-1",
                    distributed_for_conference=date(2026, 9, 29),
                )
            ],
        )
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="25-1")],
        )
        stored = corpus.get_row(conn, "scotus/1")
    assert stored is not None
    assert stored.distributed_for_conference == date(2026, 9, 29)


# --- replay redaction -------------------------------------------------------------


def test_redact_snapshot_strips_live_outcome_keys() -> None:
    redacted = redact_snapshot(
        _payload(proceedings=[_DENIED_ENTRY]) | {"docket_entries": [{"id": 1}]}
    )
    assert "ProceedingsandOrder" not in redacted
    assert "sJsonCreationDate" not in redacted
    assert "docket_entries" not in redacted
    assert redacted["CaseNumber"] == "25-100 "


# --- config -----------------------------------------------------------------------


def test_load_live_config_reads_section_and_defaults(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text("live:\n  max_cases_per_run: 5\n")
    cfg = load_live_config(tmp_path)
    assert cfg.max_cases_per_run == 5
    assert cfg.term_floor_year == 2017  # default holds

    defaults = load_live_config(tmp_path / "absent")
    assert defaults.max_new_cases_per_run == 25
    assert defaults.frontier_misses == 2


def test_repo_tracking_yaml_carries_live_section() -> None:
    cfg = load_live_config(Path("config"))
    # Sized to re-poll the whole pending watchlist each cycle at its seasonal
    # peak (the September long conference ~276); bounded by the ~1 req/s throttle,
    # not an API budget.
    assert cfg.max_cases_per_run == 300
    assert cfg.max_new_cases_per_run == 100
    assert cfg.term_floor_year == 2017


def test_distribution_transition_provisions_documents(tmp_path: Path) -> None:
    # The same transition that queues predict fetches the petition text
    # and derives the questions presented into the corpus documents table.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    served_docs = {
        "https://example/p.pdf": _pdf(
            "QUESTION PRESENTED Whether Z. PARTIES TO THE PROCEEDING Acme."
        )
    }
    served = {"25-1": _payload("25-1")}

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url in served_docs:
            return httpx.Response(200, content=served_docs[url])
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if name in served:
            return httpx.Response(200, json=served[name])
        return httpx.Response(404)

    # Cycle 1: onboarded undistributed -> no documents fetched.
    with _client(handler) as client:
        live_poll_all(client, db, data_root, term=25, config=LiveConfig(), today=date(2026, 7, 9))
    with corpus.connect(db) as conn:
        assert corpus.documents_for_case(conn, "scotus/9025000001") == []

    # Cycle 2: distribution lands -> predict queues AND documents provision.
    served["25-1"]["ProceedingsandOrder"].append(
        {"Date": "Jul 10 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."}
    )
    with _client(handler) as client:
        queues, _ = live_poll_all(
            client, db, data_root, term=25, config=LiveConfig(), today=date(2026, 7, 10)
        )
    assert [q["docket"] for q in queues.predict] == [9_025_000_001]
    with corpus.connect(db) as conn:
        stored = {d.kind: d for d in corpus.documents_for_case(conn, "scotus/9025000001")}
    assert set(stored) == {"petition", "questions-presented"}
    assert stored["questions-presented"].text == "Whether Z."


def test_resolution_without_predictions_queues_no_evaluate(tmp_path: Path) -> None:
    # The 51-case incident shape: the live sweep resolves petitions nothing ever
    # predicted — record the outcome, but queue NO evaluate (an evaluator cell
    # per judge with nothing to score is pure spend).
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    # Cycle 1 onboards it pending (open event); cycle 2's denial resolves it —
    # with no committed prediction, exactly the incident's shape.
    served = {"25-1": _payload("25-1")}
    with _frontier_client(served) as client:
        live_poll_all(client, db, data_root, term=25, config=LiveConfig(), today=date(2026, 7, 9))
    served["25-1"] = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DENIED_ENTRY]
    )
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client, db, data_root, term=25, config=LiveConfig(), today=date(2026, 7, 10)
        )
    assert queues.evaluate == []  # resolved, but never predicted -> nothing to score
    # The outcome + event.yaml pair still lands (ground truth is never gated).
    paths = CasePaths(data_root, "scotus", 9_025_000_001).event("evt-petition-disposition")
    assert paths.outcome.exists() and paths.event_file.exists()


# --- live-parsed signals: distributions, CVSG, lower-court name, weights ----------

_DISTRIBUTED_SEP = {"Date": "Sep 15 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."}
_DISTRIBUTED_OCT = {"Date": "Oct 01 2026", "Text": "DISTRIBUTED for Conference of 10/10/2026."}
_CVSG_ENTRY = {
    "Date": "Jan 12 2026",
    "Text": "The Solicitor General is invited to file a brief in this case expressing "
    "the views of the United States.",
}


def test_from_live_docket_parses_distributions_cvsg_and_lower_court_name() -> None:
    filing = _payload()["ProceedingsandOrder"][0]
    row = from_live_docket(
        _payload(
            proceedings=[
                filing,
                _CVSG_ENTRY,
                _DISTRIBUTED_SEP,
                _DISTRIBUTED_SEP,  # upstream re-serve: same conference, not double-counted
                _DISTRIBUTED_OCT,  # the relist
            ]
        ),
        live_docket_id(25, 100),
    )
    assert row.distribution_count == 2
    assert row.cvsg_date == date(2026, 1, 12)
    assert row.originating_court_name == ("United States Court of Appeals for the Ninth Circuit")
    # A never-distributed petition asserts observed-zero, never unknown.
    bare = from_live_docket(_payload(), live_docket_id(25, 101))
    assert bare.distribution_count == 0
    assert bare.cvsg_date is None


def test_ingest_live_payload_lands_weight_one_and_observed_zero_signals(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    result = ingest_live_payload(
        db, tmp_path / "data", _payload(), live_docket_id(25, 100), today=date(2026, 7, 10)
    )
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, result.case_id)
    assert stored is not None
    assert stored.sample_weight == 1  # the poller includes every row it touches
    assert stored.distribution_count == 0  # parsed, never distributed


def test_walker_weight_never_regresses_a_poller_row(tmp_path: Path) -> None:
    # The poller landed the row with certainty (weight 1); the walker later
    # re-serves its sampled serial with weight N — the min-latch keeps 1.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    docket_id = live_docket_id(25, 100)
    ingest_live_payload(db, tmp_path / "data", _payload(), docket_id, today=date(2026, 7, 9))
    ingest_live_payload(
        db, tmp_path / "data", _payload(), docket_id, today=date(2026, 7, 10), sample_weight=10
    )
    with corpus.connect(db) as conn:
        stored = corpus.get_row(conn, "scotus/9025000100")
    assert stored is not None and stored.sample_weight == 1


def test_discover_live_stamps_the_frontier_on_a_miss_exit(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    served = {"25-1": _payload("25-1"), "25-2": _payload("25-2")}
    # Capped run: frontier not observed, no stamp.
    with _frontier_client(served) as client:
        discover_live(client, db, tmp_path / "data", 25, max_new=1, today=date(2026, 7, 10))
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 25, "paid") == 1
        assert corpus.get_live_frontier(conn, 25, "paid") is None
    # Uncapped run walks to the misses and stamps the frontier at the cursor.
    with _frontier_client(served) as client:
        discover_live(client, db, tmp_path / "data", 25, max_new=10, today=date(2026, 7, 11))
    with corpus.connect(db) as conn:
        assert corpus.get_live_cursor(conn, 25, "paid") == 2
        assert corpus.get_live_frontier(conn, 25, "paid") == 2
        assert corpus.get_live_frontier(conn, 25, "ifp") is None  # nothing ever served


# --- the pre-capture backfill ------------------------------------------------------


def _strip_capture(db: Path, case_id: str) -> None:
    """Simulate a row written before the signal columns existed."""
    with corpus.connect(db) as conn, conn:
        conn.execute(
            "UPDATE cases SET distribution_count = NULL, cvsg_date = NULL, "
            "originating_court_name = NULL, sample_weight = NULL WHERE case_id = ?",
            (case_id,),
        )


def test_backfill_live_signals_reparses_snapshots_and_applies_the_weight_rule(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    today = date(2026, 7, 10)
    filing = _payload()["ProceedingsandOrder"][0]

    # A: walker-sampled denial (serial on the grid, cursor covers it) -> weight 10,
    # signals re-parsed from its stored live snapshot even under a newer REST one.
    a = ingest_live_payload(
        db,
        data_root,
        _payload("25-100", proceedings=[filing, _CVSG_ENTRY, _DISTRIBUTED_SEP, _DENIED_ENTRY]),
        live_docket_id(25, 100),
        today=today,
    )
    # B: denied off the sample grid -> weight 1.
    b = ingest_live_payload(
        db,
        data_root,
        _payload("25-101", proceedings=[filing, _DENIED_ENTRY]),
        live_docket_id(25, 101),
        today=today,
    )
    # C: denied on the grid but no historical cursor for its stream -> weight 1.
    c = ingest_live_payload(
        db,
        data_root,
        _payload("25-5010", proceedings=[filing, _DENIED_ENTRY]),
        live_docket_id(25, 5010),
        today=today,
    )
    # D: granted -> weight 1 regardless of serial.
    d = ingest_live_payload(
        db,
        data_root,
        _payload("25-120", proceedings=[filing, _GRANTED_ENTRY]),
        live_docket_id(25, 120),
        today=today,
    )
    for result in (a, b, c, d):
        _strip_capture(db, result.case_id)
    with corpus.connect(db) as conn:
        corpus.set_live_cursor(conn, 25, "historical-paid", 150)
        # A newer REST-shaped snapshot on A must not blind the re-parse.
        corpus.upsert_snapshot(conn, a.case_id, date(2026, 7, 20), {"id": 1, "court": "scotus"})
        # E: a live-slice row with no live-shaped snapshot at all (a 404-stamped
        # poll): weight still fills, signals stay NULL for a later look.
        corpus.upsert_rows(conn, [corpus.CorpusRow(case_id="scotus/74110000", court="scotus")])
        conn.execute(
            "UPDATE cases SET last_live_polled = '2026-07-10' WHERE case_id = 'scotus/74110000'"
        )
        conn.commit()

    assert backfill_live_signals(db, denial_sample_every=10) == (4, 5)
    with corpus.connect(db) as conn:
        row_a = corpus.get_row(conn, a.case_id)
        row_b = corpus.get_row(conn, b.case_id)
        row_c = corpus.get_row(conn, c.case_id)
        row_d = corpus.get_row(conn, d.case_id)
        row_e = corpus.get_row(conn, "scotus/74110000")
    assert row_a is not None and row_a.sample_weight == 10
    assert row_a.distribution_count == 1 and row_a.cvsg_date == date(2026, 1, 12)
    assert row_a.originating_court_name is not None
    assert row_b is not None and row_b.sample_weight == 1
    assert row_c is not None and row_c.sample_weight == 1
    assert row_d is not None and row_d.sample_weight == 1
    assert row_e is not None and row_e.sample_weight == 1
    assert row_e.distribution_count is None  # no live snapshot to parse

    # Idempotent: everything resolvable was resolved; the second run is a no-op.
    assert backfill_live_signals(db, denial_sample_every=10) == (0, 0)


def test_munsingwear_disposition_records_a_mootness_basis(tmp_path: Path) -> None:
    # The Munsingwear order latches `gvr` (a grant/vacate/remand) but its
    # wording is mootness practice — the recorded ground truth carries the
    # basis so scoring segments the cell into the procedural stratum.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 274)
    ingest_live_payload(db, data_root, _payload("25-274"), docket_id, today=date(2026, 7, 9))

    munsingwear_entry = {
        "Date": "May 11 2026",
        "Text": (
            "Petition GRANTED. Judgment VACATED and case REMANDED with "
            "instructions to dismiss the case as moot."
        ),
    }
    decided = ingest_live_payload(
        db,
        data_root,
        _payload("25-274", proceedings=[_payload()["ProceedingsandOrder"][0], munsingwear_entry]),
        docket_id,
        today=date(2026, 7, 10),
    )
    (event_id,) = decided.resolved
    outcome_path = CasePaths(data_root, "scotus", docket_id).event(event_id).outcome
    outcome = read_model(outcome_path, Outcome)
    assert outcome.actual_disposition == Disposition.gvr
    assert outcome.disposition_basis == "mootness"
    assert outcome.actual_granted == 1  # a GVR is a grant on the binary axis


# --- the salience gate wired into the cycle -------------------------------------

_DISTRIBUTED_ENTRY = {"Date": "Jul 10 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."}
_GATED = PredictScope.scotus_docket
_PREDICTORS = Path("config/predictors.yaml")


def _sweep_config(**kw: Any) -> SalienceConfig:
    return SalienceConfig.model_validate(kw)


def test_gated_cycle_rescues_a_first_transition_the_pass_selects(tmp_path: Path) -> None:
    """The ordering fix: a petition scored (not selected) by an earlier pass whose
    first distribution and first selection land in the same cycle is deferred at
    queue time but queued by the cycle-end sweep — never silently dropped."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    served = {"25-1": _payload("25-1")}
    cfg = _sweep_config()

    # Cycle 1: onboarded undistributed; the pass stamps its salience version.
    with _frontier_client(served) as client:
        queues1, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 9),
        )
    assert queues1.predict == []
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/9025000001")
    assert row is not None and row.salience_version is not None
    assert not row.salience_selected  # scored, undistributed: not up for selection

    # Cycle 2: the distribution transition arrives. The queue-time latch read
    # still says "scored, not selected" (deferred), so only the cycle-end pass +
    # sweep can queue it.
    served["25-1"]["ProceedingsandOrder"].append(_DISTRIBUTED_ENTRY)
    with _frontier_client(served) as client:
        queues2, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 10),
        )
    assert [q["docket"] for q in queues2.predict] == [9_025_000_001]
    with corpus.connect(db) as conn:
        selected_row = corpus.get_row(conn, "scotus/9025000001")
    assert selected_row is not None and selected_row.salience_selected


def test_gated_cycle_defers_a_below_cap_transition_without_provisioning(tmp_path: Path) -> None:
    # Zero capacity and an unreachable floor: nothing is ever selected, so a
    # distribution transition queues nothing and spends no document fetches.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    served = {"25-1": _payload("25-1")}
    cfg = _sweep_config(per_conference_capacity=0, long_conference_capacity=0, floor=1.0)

    with _frontier_client(served) as client:
        live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 9),
        )
    served["25-1"]["ProceedingsandOrder"].append(_DISTRIBUTED_ENTRY)
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 10),
        )
    assert queues.predict == []
    with corpus.connect(db) as conn:
        assert corpus.documents_for_case(conn, "scotus/9025000001") == []
        row = corpus.get_row(conn, "scotus/9025000001")
    assert row is not None and not row.salience_selected


def test_sweep_queues_the_selected_unpredicted_backlog(tmp_path: Path) -> None:
    """The catch-up: a distributed petition whose transitions all predate the
    first applied pass is latched and swept the cycle the gate goes live."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    # Its distribution predates the gate: ingested with the membership already
    # present, so no post-wiring poll ever sees a transition.
    ingest_live_payload(
        db,
        data_root,
        _payload("25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]),
        docket_id,
        today=date(2026, 7, 9),
    )
    served = {
        "25-1": _payload(
            "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
        )
    }
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            today=date(2026, 7, 10),
        )
    assert [q["docket"] for q in queues.predict] == [docket_id]


def test_sweep_debounces_a_case_polled_today_and_skips_a_predicted_one(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    distributed = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
    )
    ingest_live_payload(db, data_root, distributed, docket_id, today=date(2026, 7, 9))
    served = {"25-1": distributed}
    cfg = _sweep_config()

    # First window of the day: the rotation re-polls (no transition), the pass
    # latches, and the sweep queues + stamps the queue date.
    with _frontier_client(served) as client:
        queues1, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 10),
        )
    assert [q["docket"] for q in queues1.predict] == [docket_id]

    # A later window the same day: queued today, run PR may still be in flight
    # — the debounce leaves it alone.
    with _frontier_client(served) as client:
        queues2, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 10),
        )
    assert queues2.predict == []

    # Next day, still no committed prediction (the run failed): retried.
    with _frontier_client(served) as client:
        queues3, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 11),
        )
    assert [q["docket"] for q in queues3.predict] == [docket_id]

    # A committed prediction ends the sweep's interest for good.
    seed_prediction(data_root, "scotus", docket_id, "evt-petition-disposition")
    with _frontier_client(served) as client:
        queues4, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 12),
        )
    assert queues4.predict == []


def _distributed_selected(tmp_path: Path) -> tuple[Path, Path, int]:
    """A distributed, selectable petition ingested and ready for the sweep.

    The salience pass selects it (default capacity/floor), so the cycle-end sweep
    considers it — the shared setup for the per-cell owed tests below.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    distributed = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
    )
    ingest_live_payload(db, data_root, distributed, docket_id, today=date(2026, 7, 9))
    return db, data_root, docket_id


def test_sweep_requeues_a_partially_predicted_selected_case_per_cell(tmp_path: Path) -> None:
    """The keystone: a selected case where two of three engines committed a
    prediction and one quota-failed is still owed the missing engine, so the sweep
    re-queues it. The old case-level gate treated any single landed prediction as
    'done' and never retried — this is exactly the behavior change."""
    db, data_root, docket_id = _distributed_selected(tmp_path)
    seed_prediction(
        data_root, "scotus", docket_id, "evt-petition-disposition", predictor_id="claude-baseline"
    )
    seed_prediction(
        data_root, "scotus", docket_id, "evt-petition-disposition", predictor_id="codex-baseline"
    )
    served = {
        "25-1": _payload(
            "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
        )
    }
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            predictors_path=_PREDICTORS,
            today=date(2026, 7, 10),
        )
    assert [q["docket"] for q in queues.predict] == [docket_id]


def test_sweep_leaves_a_fully_predicted_selected_case_alone(tmp_path: Path) -> None:
    # Every enabled engine has predicted the open event: nothing owed, no sweep —
    # even with the per-cell registry handle wired in.
    db, data_root, docket_id = _distributed_selected(tmp_path)
    for pid in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        seed_prediction(
            data_root, "scotus", docket_id, "evt-petition-disposition", predictor_id=pid
        )
    served = {
        "25-1": _payload(
            "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
        )
    }
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            predictors_path=_PREDICTORS,
            today=date(2026, 7, 10),
        )
    assert queues.predict == []


def test_sweep_owed_honors_the_predict_attempt_cap(tmp_path: Path) -> None:
    """A (predictor, event) cell with the cap's worth of committed failure facts is
    no longer owed, so a case whose only-missing engine is capped is not swept;
    max_attempts=0 disables the cap and the cell is owed again. The cap reads the
    ledger `attempt.json` facts the collect job writes."""
    db, data_root, docket_id = _distributed_selected(tmp_path)
    # Two engines landed; gemini-baseline is the only cell still missing.
    seed_prediction(
        data_root, "scotus", docket_id, "evt-petition-disposition", predictor_id="claude-baseline"
    )
    seed_prediction(
        data_root, "scotus", docket_id, "evt-petition-disposition", predictor_id="codex-baseline"
    )
    # Two committed predict-seam failure facts for the missing cell → count 2.
    for i in range(2):
        run_id = f"20260101T0000{i:02d}Z"
        write_json(
            CasePaths(data_root, "scotus", docket_id)
            .event("evt-petition-disposition")
            .prediction_attempt("gemini-baseline", run_id),
            CellFailure(
                seam="predict",
                actor="gemini-baseline",
                court="scotus",
                docket=docket_id,
                event_id="evt-petition-disposition",
                run_id=run_id,
                error_class="no_output",
            ),
        )
    served = {
        "25-1": _payload(
            "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
        )
    }

    # Capped at 2 attempts: the only owed cell is poison-pilled → nothing swept.
    with _frontier_client(served) as client:
        capped, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            predictors_path=_PREDICTORS,
            predict_max_attempts=2,
            today=date(2026, 7, 10),
        )
    assert capped.predict == []

    # max_attempts=0 disables the cap → the cell is owed again and swept.
    with _frontier_client(served) as client:
        uncapped, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            predictors_path=_PREDICTORS,
            predict_max_attempts=0,
            today=date(2026, 7, 11),
        )
    assert [q["docket"] for q in uncapped.predict] == [docket_id]


def test_sweep_respects_the_cap_and_the_ungated_scope(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    distributed = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
    )
    ingest_live_payload(db, data_root, distributed, docket_id, today=date(2026, 7, 9))
    served = {"25-1": distributed}

    # A zero sweep cap: the pass still latches, but nothing is swept.
    with _frontier_client(served) as client:
        capped, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(sweep_cases_per_cycle=0),
            today=date(2026, 7, 10),
        )
    assert capped.predict == []
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/9025000001")
    assert row is not None and row.salience_selected

    # Ungated scope: the pass may run, but the sweep never queues.
    with _frontier_client(served) as client:
        ungated, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=PredictScope.all,
            salience_config=_sweep_config(),
            today=date(2026, 7, 11),
        )
    assert ungated.predict == []


def test_sweep_diverts_a_decided_looking_selected_case_once_per_day(tmp_path: Path) -> None:
    # A selected petition whose latest order is a terminal form the resolver
    # misses: the sweep must divert it (never a forward cell) and stamp, so a
    # later window the same day appends no duplicate divert entry.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    decided_looking = _payload(
        "25-1",
        proceedings=[
            _payload()["ProceedingsandOrder"][0],
            _DISTRIBUTED_ENTRY,
            _RULE_398_ENTRY,
        ],
    )
    ingest_live_payload(db, data_root, decided_looking, docket_id, today=date(2026, 7, 9))
    served = {"25-1": decided_looking}
    cfg = _sweep_config()

    with _frontier_client(served) as client:
        queues1, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 10),
        )
    assert queues1.predict == []
    assert [q["docket"] for q in queues1.predict_skipped_decided] == [docket_id]
    assert "39.8" in str(queues1.predict_skipped_decided[0]["reason"])

    with _frontier_client(served) as client:
        queues2, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=cfg,
            today=date(2026, 7, 10),
        )
    assert queues2.predict == [] and queues2.predict_skipped_decided == []


def test_selected_case_transition_queues_exactly_once(tmp_path: Path) -> None:
    # An already-selected petition that relists: the inline transition path
    # queues it (and stamps), and the same cycle's sweep must not add a second
    # entry for the same docket.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    distributed = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
    )
    ingest_live_payload(db, data_root, distributed, docket_id, today=date(2026, 7, 9))
    with corpus.connect(db) as conn:
        corpus.latch_salience_selected(conn, ["scotus/9025000001"])

    relisted = _payload(
        "25-1",
        proceedings=[
            _payload()["ProceedingsandOrder"][0],
            _DISTRIBUTED_ENTRY,
            {"Date": "Jul 11 2026", "Text": "DISTRIBUTED for Conference of 10/10/2026."},
        ],
    )
    served = {"25-1": relisted}
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            today=date(2026, 7, 11),
        )
    assert [q["docket"] for q in queues.predict] == [docket_id]


def _relist_fixture(
    tmp_path: Path, *, predict_queued_at: date
) -> tuple[Path, Path, int, dict[str, Any]]:
    """A selected, already-predicted petition, freshly relisted to a new conference.

    Onboards via ``discover_live`` (not the direct ``ingest_live_payload``
    helper other fixtures in this module use) so the frontier cursor actually
    advances past serial 1 — otherwise the next cycle's discovery step would
    re-probe and re-"onboard" this same docket from scratch (no persisted
    cursor to tell it otherwise), routing the relist through the discovery
    path's onboarding queue-check instead of the due-rotation refresh this
    test targets (:func:`poll_live_cases`, the only place the cooldown applies).
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    distributed = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
    )
    with _frontier_client({"25-1": distributed}) as client:
        discover_live(client, db, data_root, 25, max_new=1, today=date(2026, 7, 9))
    with corpus.connect(db) as conn:
        corpus.latch_salience_selected(conn, ["scotus/9025000001"])
        corpus.stamp_predict_queued(conn, ["scotus/9025000001"], predict_queued_at)
    relisted = _payload(
        "25-1",
        proceedings=[
            _payload()["ProceedingsandOrder"][0],
            _DISTRIBUTED_ENTRY,
            {"Date": "Jul 11 2026", "Text": "DISTRIBUTED for Conference of 10/10/2026."},
        ],
    )
    return db, data_root, docket_id, {"25-1": relisted}


def test_relist_inside_cooldown_is_suppressed_not_requeued(tmp_path: Path) -> None:
    # Relisted the same day its predict was last queued: the default 1-day
    # cooldown treats this as administrative churn, not a fresh prediction.
    db, data_root, docket_id, served = _relist_fixture(
        tmp_path, predict_queued_at=date(2026, 7, 11)
    )
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            today=date(2026, 7, 11),
        )
    assert queues.predict == []
    assert [q["docket"] for q in queues.predict_skipped_relist_cooldown] == [docket_id]
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/9025000001")
    assert row is not None and row.predict_queued_at == date(2026, 7, 11)  # re-stamped


def test_relist_after_cooldown_elapses_requeues_normally(tmp_path: Path) -> None:
    # One full day has elapsed since the last predict queue: the default 1-day
    # cooldown no longer applies, so the relist queues exactly like before.
    db, data_root, docket_id, served = _relist_fixture(
        tmp_path, predict_queued_at=date(2026, 7, 10)
    )
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            today=date(2026, 7, 11),
        )
    assert [q["docket"] for q in queues.predict] == [docket_id]
    assert queues.predict_skipped_relist_cooldown == []


def test_relist_cooldown_disabled_by_zero_always_requeues(tmp_path: Path) -> None:
    # A same-day relist that would otherwise be suppressed queues normally when
    # the knob is set to 0 (disabled).
    db, data_root, docket_id, served = _relist_fixture(
        tmp_path, predict_queued_at=date(2026, 7, 11)
    )
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(relist_requeue_cooldown_days=0),
            today=date(2026, 7, 11),
        )
    assert [q["docket"] for q in queues.predict] == [docket_id]
    assert queues.predict_skipped_relist_cooldown == []


def test_relist_cooldown_longer_than_a_day_advances_the_stamp(tmp_path: Path) -> None:
    # A longer cooldown (3 days) still suppresses two days after the last
    # queue, and the divert re-stamps predict_queued_at forward to today —
    # not a no-op, since the pre-poll stamp is genuinely in the past.
    db, data_root, docket_id, served = _relist_fixture(tmp_path, predict_queued_at=date(2026, 7, 9))
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(relist_requeue_cooldown_days=3),
            today=date(2026, 7, 11),
        )
    assert queues.predict == []
    assert [q["docket"] for q in queues.predict_skipped_relist_cooldown] == [docket_id]
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/9025000001")
    assert row is not None and row.predict_queued_at == date(2026, 7, 11)  # advanced, not stale


def test_relist_cooldown_does_not_suppress_a_first_distribution(tmp_path: Path) -> None:
    # The cooldown only ever applies to a relist (a case already distributed
    # before this poll) -- a case's first-ever distribution must never be
    # suppressed, even if it was queued (e.g. onboarded) earlier the same day.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(25, 1)
    undistributed = _payload("25-1")
    # discover_live (not the direct ingest helper) so the frontier cursor
    # advances and the next cycle's transition reaches poll_live_cases via the
    # due rotation rather than being re-onboarded by discovery.
    with _frontier_client({"25-1": undistributed}) as client:
        discover_live(client, db, data_root, 25, max_new=1, today=date(2026, 7, 11))
    with corpus.connect(db) as conn:
        corpus.latch_salience_selected(conn, ["scotus/9025000001"])
        corpus.stamp_predict_queued(conn, ["scotus/9025000001"], date(2026, 7, 11))
    distributed = _payload(
        "25-1", proceedings=[_payload()["ProceedingsandOrder"][0], _DISTRIBUTED_ENTRY]
    )
    served = {"25-1": distributed}
    with _frontier_client(served) as client:
        queues, _ = live_poll_all(
            client,
            db,
            data_root,
            term=25,
            config=LiveConfig(),
            scope=_GATED,
            salience_config=_sweep_config(),
            today=date(2026, 7, 11),
        )
    assert [q["docket"] for q in queues.predict] == [docket_id]
    assert queues.predict_skipped_relist_cooldown == []
