"""The integration probes behind ``fedcourts corpus-integration-check`` and
``fedcourts mcp-integration-check``.

Exercises :mod:`fedcourtsai.integration_check` over the fixture corpus on the
local backend, over moto's S3 stand-in on the ranged backend, and against
fake localhost sidecars for the service and MCP probes — the offline mirror
of what the integration-test workflow dispatches against the real remote. No
test touches the network.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import ClassVar

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus, corpus_ranged, corpus_service, ids, store
from fedcourtsai.cli import app
from fedcourtsai.fixture import build_fixture_corpus
from fedcourtsai.integration_check import (
    CaseResolutionError,
    IntegrationReport,
    McpProbeError,
    ResolvedCase,
    render_markdown,
    resolve_integration_case,
    run_integration_check,
    run_mcp_check,
    run_service_check,
)
from fedcourtsai.registry import load_mcp_servers
from fedcourtsai.schemas import Disposition, EventKind

REMOTE_URL = "s3://test-bucket/store"

# ca9/103 is the fixture's open-event appeals case: an open event, resolved
# priors in the same court, and a stored snapshot — the shape the check wants.
COURT, DOCKET = "ca9", 103


@pytest.fixture
def corpus_db(tmp_path: Path) -> Path:
    """A freshly built synthetic fixture corpus."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    build_fixture_corpus(db)
    return db


def _check(corpus_db: Path, **kwargs: object) -> IntegrationReport:
    return run_integration_check(
        corpus_db_path=corpus_db,
        court=COURT,
        docket=DOCKET,
        **kwargs,  # type: ignore[arg-type]
    )


def test_known_case_passes_every_read(corpus_db: Path) -> None:
    report = _check(corpus_db)

    assert report.ok and report.within_budget
    assert report.case_id == f"{COURT}/{DOCKET}"
    assert report.backend == "local"
    assert [s.ok for s in report.steps] == [True, True, True]
    # The local backend transfers nothing, so it carries no counters.
    assert all(s.gets is None and s.bytes_fetched is None for s in report.steps)
    assert "evt-appeal-disposition" in report.steps[0].detail


def test_snapshot_out_materializes_the_snapshot(corpus_db: Path, tmp_path: Path) -> None:
    dest = tmp_path / "snapshot.json"
    report = _check(corpus_db, snapshot_out=dest)

    assert report.ok
    payload = json.loads(dest.read_text())
    assert isinstance(payload, dict) and payload


def test_unknown_case_fails_the_point_reads(corpus_db: Path) -> None:
    report = run_integration_check(corpus_db_path=corpus_db, court="ca9", docket=99999999, limit=5)

    assert not report.ok
    by_name = {s.name: s for s in report.steps}
    assert not by_name["open-events"].ok
    assert not by_name["provision-snapshot"].ok
    # The priors read filters by court, not case, so it still succeeds.
    assert by_name["priors (court ca9, limit 5)"].ok


def test_blown_budget_fails_the_report(corpus_db: Path) -> None:
    report = _check(corpus_db, budget_seconds=0.0)

    assert not report.within_budget
    assert not report.ok
    assert all(s.ok for s in report.steps), "the reads themselves still pass"


def test_markdown_summary_names_every_read(corpus_db: Path) -> None:
    summary = render_markdown(_check(corpus_db))

    assert f"Corpus integration check — {COURT}/{DOCKET} [local]" in summary
    assert "| open-events | ok |" in summary
    assert "| provision-snapshot | ok |" in summary
    assert "within the 300s budget" in summary


def _stage_ranged_remote(db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Publish the corpus blob to moto's S3 and point the env at it, ranged."""
    blob = db.read_bytes()
    sha256 = hashlib.sha256(blob).hexdigest()
    pointer = db.with_name(db.name + ".ref")
    pointer.write_text(
        json.dumps(
            {
                "key": f"index/sha256/{sha256}",
                "size": len(blob),
                "sha256": sha256,
                "schema_version": "1.0",
            }
        )
        + "\n"
    )
    remote = corpus_ranged.resolve_pointer(pointer, REMOTE_URL)
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=remote.bucket)
    client.put_object(Bucket=remote.bucket, Key=remote.key, Body=blob)
    db.unlink()  # ranged access must not need (or recreate) the local blob
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@mock_aws
def test_ranged_backend_reports_transfer_counters(
    corpus_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stage_ranged_remote(corpus_db, monkeypatch)

    report = _check(corpus_db)

    assert report.ok
    assert report.backend == "ranged"
    for step in report.steps:
        assert step.gets is not None and step.gets > 0
        assert step.bytes_fetched is not None and step.bytes_fetched > 0
    assert "GET(s)" in render_markdown(report)
    assert not corpus_db.exists(), "the ranged check must not create a local corpus file"


def test_cli_writes_summary_and_exits_by_verdict(corpus_db: Path, tmp_path: Path) -> None:
    summary_out = tmp_path / "summary.md"
    args = [
        "corpus-integration-check",
        "--court",
        COURT,
        "--docket",
        str(DOCKET),
        "--summary-out",
        str(summary_out),
    ]
    env = {"FEDCOURTS_CORPUS_ROOT": str(corpus_db.parent)}

    passed = CliRunner().invoke(app, args, env=env)
    assert passed.exit_code == 0, passed.output
    assert json.loads(passed.stdout)["ok"] is True
    assert "Corpus integration check" in summary_out.read_text()

    failed = CliRunner().invoke(
        app,
        ["corpus-integration-check", "--court", COURT, "--docket", "99999999"],
        env=env,
    )
    assert failed.exit_code == 1


# --- the service-backend counterpart ---------------------------------------


@contextmanager
def _service(db: Path) -> Iterator[str]:
    server = corpus_service.create_server(db, backend="local")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_service_check_passes_against_a_live_sidecar(corpus_db: Path) -> None:
    with _service(corpus_db) as url:
        report = run_service_check(service_url=url, court=COURT, docket=DOCKET)
    assert report.ok and report.backend == "service"
    assert [s.name for s in report.steps] == [
        f"service query (court {COURT}, limit 5)",
        "service open-events",
        "service full-query hydration",
    ]
    # The fixture corpus carries an opinion-bearing granted row, so the probe
    # verifies its body outright.
    assert "every body hydrated" in report.steps[2].detail
    # Local backend behind the service: no transfer counters, matching the CLI.
    assert all(s.gets is None for s in report.steps)


def test_service_hydration_probe_notes_an_unenriched_corpus(tmp_path: Path) -> None:
    """A corpus with granted rows but no opinion bodies yet must not fail the
    probe — before the first enrichment run there is nothing to certify — but
    the pass has to say so, loudly, rather than read as coverage."""
    db = corpus.corpus_db_path(tmp_path / "bare")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/601",
                    court="scotus",
                    docket_number="14-1234",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2015, 3, 2),
                )
            ],
        )
    with _service(db) as url:
        report = run_service_check(service_url=url, court="scotus", docket=601)
    probe = report.steps[2]
    assert probe.ok
    assert "UNVERIFIED" in probe.detail


def _opinion_case(case_id: str, granted_on: date, opinion: str | None) -> corpus.CorpusRow:
    """A decided granted SCOTUS row, optionally carrying its opinion body."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number="14-1234",
        disposition=Disposition.granted,
        date_cert_granted=granted_on,
        has_opinion=True,
        opinion_text=opinion,
    )


def test_service_hydration_probe_verifies_opinion_bodies(corpus_db: Path) -> None:
    """The probe finds the survey's first opinion-bearing granted row and
    asserts the rank-anchored full re-ask returns that very row with a
    non-empty body."""
    with corpus.connect(corpus_db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _opinion_case("scotus/501", date(2015, 3, 2), "Held: reversed."),
                _opinion_case("scotus/502", date(2015, 10, 5), "Held: affirmed."),
            ],
        )
    with _service(corpus_db) as url:
        report = run_service_check(service_url=url, court="scotus", docket=501)
    probe = report.steps[2]
    assert probe.name == "service full-query hydration"
    assert probe.ok
    assert "every body hydrated" in probe.detail


def test_service_hydration_probe_fails_on_a_bodiless_opinion_row(corpus_db: Path) -> None:
    """The regression signature of a dead content store: a row whose retained
    `has_opinion` bit claims a body that hydrates to nothing. The probe must
    fail rather than let bodiless rows flow to every cell as valid output."""
    with corpus.connect(corpus_db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _opinion_case("scotus/503", date(2015, 3, 2), "Held: reversed."),
                _opinion_case("scotus/504", date(2015, 10, 5), None),
            ],
        )
    with _service(corpus_db) as url:
        report = run_service_check(service_url=url, court="scotus", docket=503)
    probe = report.steps[2]
    assert not probe.ok and not report.ok
    assert "scotus/504" in probe.detail and "hydrated no body" in probe.detail


def test_service_hydration_probe_reaches_past_newer_bodiless_grants(corpus_db: Path) -> None:
    """The sampling trap the probe must not fall into: recency ranking puts
    the newest grants — whose opinions do not exist yet — ahead of every
    enriched row, so a fixed-size hydration window would sample exactly the
    rows with nothing to hydrate and report the miss as health. The probe
    re-asks the survey's own query cut past the first bearing row's rank, so
    a bodiless bearing row ranked below a stack of newer clean grants still
    fails the step."""
    with corpus.connect(corpus_db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # Three newer grants, merits pending: no opinion yet, honestly.
                corpus.CorpusRow(
                    case_id=f"scotus/{910000510 + i}",
                    court="scotus",
                    docket_number=f"24-90{i}",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2026, 1, 10 + i),
                )
                for i in range(3)
            ]
            + [
                # The regression signature, ranked below all of them.
                _opinion_case("scotus/910000509", date(2015, 3, 2), None),
            ],
        )
    with _service(corpus_db) as url:
        report = run_service_check(service_url=url, court="scotus", docket=910000509)
    probe = report.steps[2]
    assert not probe.ok
    assert "scotus/910000509" in probe.detail and "hydrated no body" in probe.detail


def test_service_hydration_probe_discriminates_a_live_from_a_dead_store(
    corpus_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The production seam end to end: under the corpus split the blob column
    is NULL and `prior_payload` hydrates through the content-store read
    source, which swallows its own failures into None. The same index rows
    must pass the probe over a store that holds the body and fail it over an
    emptied store — the discriminating pair a NULL-column simulation alone
    cannot give."""
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    casestore.set_active_transport(casestore.InMemoryObjectTransport())
    with corpus.connect(corpus_db) as conn:
        corpus.upsert_rows(
            conn, [_opinion_case("scotus/910000520", date(2015, 3, 2), "Held: reversed.")]
        )
    with _service(corpus_db) as url:
        live = run_service_check(service_url=url, court="scotus", docket=910000520)
    assert live.steps[2].ok
    assert "every body hydrated" in live.steps[2].detail

    # Wipe the store behind the same retained `has_opinion` bit: the read
    # source now swallows its miss into None, and the probe must see it.
    casestore.set_active_transport(casestore.InMemoryObjectTransport())
    with _service(corpus_db) as url:
        dead = run_service_check(service_url=url, court="scotus", docket=910000520)
    probe = dead.steps[2]
    assert not probe.ok
    assert "scotus/910000520" in probe.detail and "hydrated no body" in probe.detail


def test_service_check_fails_on_an_unknown_case(corpus_db: Path) -> None:
    with _service(corpus_db) as url:
        report = run_service_check(service_url=url, court="nowhere", docket=1)
    assert not report.ok
    assert not report.steps[0].ok and "no resolved priors" in report.steps[0].detail
    assert not report.steps[1].ok


def test_service_check_raises_when_the_sidecar_is_down(corpus_db: Path) -> None:
    with pytest.raises(corpus_service.CorpusServiceError):
        run_service_check(service_url="http://127.0.0.1:9", court=COURT, docket=DOCKET)


# --- the MCP-sidecar probe ---------------------------------------------------


class _FakeMcpHandler(BaseHTTPRequestHandler):
    """A minimal streamable-HTTP MCP endpoint: initialize, then tools/list.

    Subclass per test to vary the framing (``sse``) and the advertised tools;
    ``seen_sessions`` records the Mcp-Session-Id each post-handshake request
    carried, asserted from the test body rather than the handler thread.
    """

    sse = False
    tools: ClassVar[list[dict[str, object]]] = [{"name": "search"}, {"name": "lookup_citation"}]
    seen_sessions: ClassVar[list[str | None]]

    def do_POST(self) -> None:  # BaseHTTPRequestHandler's casing contract
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length)) if length else {}
        method = payload.get("method")
        if method == "initialize":
            self._reply(
                payload["id"],
                {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "serverInfo": {"name": "fake-cl-mcp", "version": "9.9"},
                },
                session="sess-1",
            )
        elif method == "notifications/initialized":
            type(self).seen_sessions.append(self.headers.get("Mcp-Session-Id"))
            self.send_response(202)
            self.end_headers()
        elif method == "tools/list":
            type(self).seen_sessions.append(self.headers.get("Mcp-Session-Id"))
            self._reply(payload["id"], {"tools": type(self).tools})
        else:
            self.send_response(404)
            self.end_headers()

    def _reply(self, rpc_id: object, result: dict[str, object], session: str | None = None) -> None:
        message = json.dumps({"jsonrpc": "2.0", "id": rpc_id, "result": result})
        if type(self).sse:
            body = f"event: message\ndata: {message}\n\n".encode()
            content_type = "text/event-stream"
        else:
            body = message.encode()
            content_type = "application/json"
        self.send_response(200)
        if session is not None:
            self.send_header("Mcp-Session-Id", session)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_: object) -> None:  # keep the test output quiet
        pass


@contextmanager
def _mcp_server(handler: type[_FakeMcpHandler]) -> Iterator[str]:
    handler.seen_sessions = []
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/mcp"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_mcp_check_passes_and_threads_the_session() -> None:
    class Handler(_FakeMcpHandler):
        pass

    with _mcp_server(Handler) as url:
        report = run_mcp_check(mcp_url=url)

    assert report.ok and report.url == url
    assert [s.name for s in report.steps] == ["initialize", "tools/list"]
    assert "fake-cl-mcp 9.9" in report.steps[0].detail
    assert report.steps[1].detail == "search, lookup_citation"
    # Both post-handshake requests carried the session the server issued.
    assert Handler.seen_sessions == ["sess-1", "sess-1"]
    assert f"CourtListener MCP check — {url}" in render_markdown(report)


def test_mcp_check_parses_sse_framed_responses() -> None:
    class Handler(_FakeMcpHandler):
        sse = True

    with _mcp_server(Handler) as url:
        report = run_mcp_check(mcp_url=url)
    assert report.ok, [s.detail for s in report.steps]


def test_mcp_check_fails_on_an_empty_tool_list() -> None:
    class Handler(_FakeMcpHandler):
        tools: ClassVar[list[dict[str, object]]] = []

    with _mcp_server(Handler) as url:
        report = run_mcp_check(mcp_url=url)
    assert not report.ok
    assert report.steps[0].ok
    assert not report.steps[1].ok and "no tools" in report.steps[1].detail


def test_mcp_check_raises_when_the_sidecar_is_down() -> None:
    with pytest.raises(McpProbeError):
        run_mcp_check(mcp_url="http://127.0.0.1:9/mcp")


def test_mcp_cli_writes_summary_and_exits_by_verdict(tmp_path: Path) -> None:
    # The CLI compares the server against the committed manifest, so the fake
    # has to advertise what the manifest records or the run legitimately fails
    # on drift. Deriving it here keeps the happy path honest AND covers the
    # matching case; the drift case is the test below.
    manifest = sorted(
        {t for srv in load_mcp_servers(Path("config") / "predictors.yaml") for t in srv.tools}
    )

    class Handler(_FakeMcpHandler):
        tools: ClassVar[list[dict[str, object]]] = [{"name": t} for t in manifest]

    summary_out = tmp_path / "summary.md"
    with _mcp_server(Handler) as url:
        passed = CliRunner().invoke(
            app, ["mcp-integration-check", "--url", url, "--summary-out", str(summary_out)]
        )
    assert passed.exit_code == 0, passed.output
    assert json.loads(passed.stdout)["ok"] is True
    assert "CourtListener MCP check" in summary_out.read_text()

    down = CliRunner().invoke(app, ["mcp-integration-check", "--url", "http://127.0.0.1:9/mcp"])
    assert down.exit_code == 2


def test_mcp_cli_fails_when_the_server_has_drifted_from_the_manifest(tmp_path: Path) -> None:
    # The manifest's tool list is the offered denominator every retrieval log
    # snapshots, and it is captured by hand at pin time. Without this check a
    # version bump that adds or drops a tool leaves it silently wrong and every
    # later offered-vs-called rollup inherits the error.
    class Handler(_FakeMcpHandler):
        tools: ClassVar[list[dict[str, object]]] = [{"name": "search"}]

    with _mcp_server(Handler) as url:
        result = CliRunner().invoke(app, ["mcp-integration-check", "--url", url])
    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    drift = next(s for s in report["steps"] if s["name"] == "manifest tools")
    assert not drift["ok"]
    assert "recorded but not advertised" in drift["detail"]


# --- the run-time case resolver ---------------------------------------------


def _plain(text: str) -> str:
    """CLI output with ANSI styling stripped and runs of whitespace collapsed.

    CI runs with ``FORCE_COLOR=1``, and Typer wraps its error panels to a
    terminal width no test can pin, so neither the escapes nor the line breaks
    can appear in an assertion.
    """
    return " ".join(re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text).replace("│", " ").split())


def _open_row(
    docket: int,
    *,
    docket_number: str = "24-100",
    last_live_polled: date | None = None,
    predict_excluded: bool = False,
    date_cert_granted: date | None = None,
) -> corpus.CorpusRow:
    """An unresolved SCOTUS cert row — the shape the resolver is looking for."""
    return corpus.CorpusRow(
        case_id=ids.case_id("scotus", docket),
        court="scotus",
        docket_number=docket_number,
        case_name=f"Petitioner {docket} v. Respondent",
        date_filed=date(2025, 1, 5),
        predict_eligible=True,
        predict_excluded=predict_excluded,
        last_live_polled=last_live_polled,
        date_cert_granted=date_cert_granted,
    )


def _seed(
    db: Path,
    rows: Sequence[corpus.CorpusRow],
    *,
    snapshotless: Sequence[str] = (),
    disposed_events: Sequence[str] = (),
) -> None:
    """Write each row with its cert-petition event and a stored snapshot.

    ``snapshotless`` names the case ids to leave without one, ``disposed_events``
    those whose event is already resolved — the two shapes that must not be
    handed to the suite.
    """
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, list(rows))
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=ids.event_id("petition", "disposition"),
                    case_id=row.case_id,
                    court=row.court,
                    kind=EventKind.petition,
                    title=row.case_name,
                    resolved=row.case_id in disposed_events,
                )
                for row in rows
            ],
        )
        for row in rows:
            if row.case_id not in snapshotless:
                corpus.upsert_snapshot(
                    conn,
                    row.case_id,
                    date(2026, 8, 1),
                    {"id": 1, "docket_entries": []},
                )


def _resolve(db: Path, tmp_path: Path, **kwargs: object) -> ResolvedCase:
    """Resolve against ``db`` with an empty ledger, so the record gate sees no
    committed outcome and judges the corpus row alone."""
    return resolve_integration_case(
        corpus_db_path=db,
        data_root=tmp_path / "empty-ledger",
        **kwargs,  # type: ignore[arg-type]
    )


def test_resolver_picks_the_fixture_open_case(corpus_db: Path, tmp_path: Path) -> None:
    """The fixture's one unresolved, in-scope, snapshot-bearing SCOTUS docket."""
    resolved = _resolve(corpus_db, tmp_path)

    assert (resolved.court, resolved.docket) == ("scotus", 305)
    assert resolved.case_id == "scotus/305"
    assert resolved.open_event_ids == ("evt-petition-disposition",)
    assert resolved.snapshot_date == date(2025, 3, 3)
    assert resolved.scanned == 1


def test_resolver_prefers_the_freshest_live_poll(tmp_path: Path) -> None:
    """The ordering is the contract: most recently live-polled first (the live
    channel stamps exactly the modern petitions the suite wants), never-polled
    last, so the same corpus always resolves the same case."""
    db = corpus.corpus_db_path(tmp_path / "ordered")
    _seed(
        db,
        [
            _open_row(701, last_live_polled=date(2026, 8, 1)),
            _open_row(702, last_live_polled=date(2026, 8, 20)),
            _open_row(703, last_live_polled=None),
        ],
    )

    assert _resolve(db, tmp_path).case_id == "scotus/702"


def test_resolver_ignores_the_pull_stamp(tmp_path: Path) -> None:
    """`last_pulled` must not decide the pick. The pull governor rotates over
    the whole active set including the historical bulk import, so its freshest
    stamps are ancient dockets a repair sweep happened to touch — ordering on it
    puts those at the head and the live petitions at the tail."""
    db = corpus.corpus_db_path(tmp_path / "pull-stamp")
    stale_but_live = _open_row(761, last_live_polled=date(2026, 8, 31))
    fresh_pull_never_polled = _open_row(762, last_live_polled=None).model_copy(
        update={"last_pulled": date(2026, 8, 31)}
    )
    _seed(db, [stale_but_live, fresh_pull_never_polled])

    assert _resolve(db, tmp_path).case_id == "scotus/761"


def test_resolver_skips_a_case_whose_event_is_resolved(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "disposed")
    _seed(
        db,
        [
            # Fresher, but its event is already resolved: nothing left to forecast.
            _open_row(711, last_live_polled=date(2026, 8, 20)),
            _open_row(712, last_live_polled=date(2026, 8, 1)),
        ],
        disposed_events=["scotus/711"],
    )

    assert _resolve(db, tmp_path).case_id == "scotus/712"


def test_resolver_skips_a_granted_petition_awaiting_judgment(tmp_path: Path) -> None:
    """The shape a naive "undisposed" filter admits and the consumer refuses: a
    cert-granted petition whose merits judgment has not landed carries no
    disposition and no decision date, but `resolution_date` is its cert-grant
    date, so `provision-snapshot --refuse-terminal` records the case decided.
    Handing it to the suite would fail the cascade leg, which requires that
    command to succeed."""
    db = corpus.corpus_db_path(tmp_path / "granted")
    granted = _open_row(
        771, last_live_polled=date(2026, 8, 31), date_cert_granted=date(2026, 6, 30)
    )
    pending = _open_row(772, last_live_polled=date(2026, 8, 1))
    _seed(db, [granted, pending])

    resolved = _resolve(db, tmp_path)

    assert resolved.case_id == "scotus/772"
    # Rejected by the window itself, so it never spends a candidate slot.
    assert resolved.scanned == 1
    assert (
        store.forward_refusal_reason_from_parts(
            tmp_path / "empty-ledger", "scotus", 771, "", [], granted
        )
        == "the corpus records the case decided"
    )


def test_resolver_skips_a_case_the_predict_scope_excludes(tmp_path: Path) -> None:
    """Both halves of the scope screen: the latched row and the row an
    exclusion predicate catches unlatched (an IFP serial, ``24-6001``)."""
    db = corpus.corpus_db_path(tmp_path / "scope")
    _seed(
        db,
        [
            _open_row(721, last_live_polled=date(2026, 8, 20), predict_excluded=True),
            _open_row(722, docket_number="24-6001", last_live_polled=date(2026, 8, 15)),
            _open_row(723, last_live_polled=date(2026, 8, 1)),
        ],
    )

    resolved = _resolve(db, tmp_path)

    assert resolved.case_id == "scotus/723"
    # The latched row never reaches the window at all; the unlatched IFP row
    # does, and is rejected by the reason evaluator.
    assert resolved.scanned == 2


def test_resolver_skips_a_snapshotless_case(tmp_path: Path) -> None:
    """The property `provision-snapshot` needs: a case with an open event but
    nothing stored to provision from. It is the window's own driver, so a
    snapshotless case is never even a candidate."""
    db = corpus.corpus_db_path(tmp_path / "snapshotless")
    _seed(
        db,
        [
            _open_row(731, last_live_polled=date(2026, 8, 20)),
            _open_row(732, last_live_polled=date(2026, 8, 1)),
        ],
        snapshotless=["scotus/731"],
    )

    resolved = _resolve(db, tmp_path)

    assert resolved.case_id == "scotus/732"
    assert resolved.scanned == 1


def test_resolver_refuses_when_nothing_qualifies(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "barren")
    _seed(
        db,
        [_open_row(741, docket_number="24-6001", last_live_polled=date(2026, 8, 1))],
    )

    with pytest.raises(CaseResolutionError) as excinfo:
        _resolve(db, tmp_path)

    message = str(excinfo.value)
    assert "1 candidate(s)" in message
    assert "in-forma-pauperis" in message


def test_resolver_says_so_under_the_corpus_split(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The candidate window reads the blob's `snapshots` table, which the split
    empties — so an empty window there means "the index cannot answer", not "no
    such case". Reporting it as an absent case would send a maintainer hunting
    for a corpus problem that is a mode."""
    db = corpus.corpus_db_path(tmp_path / "split")
    _seed(db, [_open_row(781, last_live_polled=date(2026, 8, 1))], snapshotless=["scotus/781"])
    monkeypatch.setattr(corpus, "payload_reads_offloaded", lambda: True)

    with pytest.raises(CaseResolutionError) as excinfo:
        _resolve(db, tmp_path)

    assert "corpus-split" in str(excinfo.value)


def test_resolver_bounds_the_candidate_scan(tmp_path: Path) -> None:
    """``scan_limit`` bounds the SQL window, not just the Python loop. With the
    window cut to the one unusable head candidate, the qualifying row below it
    is out of reach and the resolver refuses."""
    db = corpus.corpus_db_path(tmp_path / "bounded")
    _seed(
        db,
        [
            _open_row(751, docket_number="24-6001", last_live_polled=date(2026, 8, 20)),
            _open_row(752, last_live_polled=date(2026, 8, 1)),
        ],
    )

    assert _resolve(db, tmp_path, scan_limit=2).case_id == "scotus/752"
    with pytest.raises(CaseResolutionError):
        _resolve(db, tmp_path, scan_limit=1)


def test_resolver_hands_over_a_case_the_forward_gate_accepts(
    corpus_db: Path, tmp_path: Path
) -> None:
    """The claim the whole command exists to make, asserted end to end: the case
    it resolves is one the suite's own provisioning guard will not refuse."""
    resolved = _resolve(corpus_db, tmp_path)

    assert (
        store.forward_refusal_reason(
            corpus_db,
            tmp_path / "empty-ledger",
            resolved.court,
            resolved.docket,
            "",
        )
        is None
    )


@mock_aws
def test_resolver_runs_on_the_ranged_backend(
    corpus_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The backend the suite actually resolves on: the integration legs never
    pull, so the resolver must work with no local corpus file at all."""
    _stage_ranged_remote(corpus_db, monkeypatch)

    resolved = _resolve(corpus_db, tmp_path)

    assert resolved.case_id == "scotus/305"
    assert not corpus_db.exists(), "the ranged resolution must not create a local corpus file"


def test_case_cli_prints_the_resolved_case_as_key_values(corpus_db: Path) -> None:
    """The output contract the workflow parses: stdout is exactly the two
    ``key=value`` lines a step appends to ``$GITHUB_OUTPUT``, and the human line
    naming the case stays on stderr."""
    result = CliRunner().invoke(
        app,
        ["corpus-integration-case"],
        env={"FEDCOURTS_CORPUS_ROOT": str(corpus_db.parent)},
    )

    assert result.exit_code == 0, result.output
    assert _plain(result.stdout) == "court=scotus docket=305"
    assert "resolved scotus/305" in _plain(result.stderr)
    assert "evt-petition-disposition" in _plain(result.stderr)


def test_case_cli_output_is_a_github_output_fragment(corpus_db: Path) -> None:
    """What the workflow step does with stdout: append it verbatim to
    `$GITHUB_OUTPUT`. Every line must therefore parse as `key=value` with a key
    the step can name, and nothing else may reach stdout."""
    result = CliRunner().invoke(
        app,
        ["corpus-integration-case"],
        env={"FEDCOURTS_CORPUS_ROOT": str(corpus_db.parent)},
    )

    assert result.exit_code == 0, result.output
    parsed = dict(line.split("=", 1) for line in result.stdout.splitlines() if line)
    assert parsed == {"court": "scotus", "docket": "305"}


def test_case_cli_exits_2_when_no_case_qualifies(corpus_db: Path) -> None:
    result = CliRunner().invoke(
        app,
        ["corpus-integration-case", "--court", "ca1"],
        env={"FEDCOURTS_CORPUS_ROOT": str(corpus_db.parent)},
    )

    assert result.exit_code == 2
    assert not result.stdout.strip(), "a refusal must emit no key=value line"
    assert "no case in ca1 is shaped for the integration suite" in _plain(result.stderr)


def test_case_cli_refuses_the_service_backend_from_the_setting(corpus_db: Path) -> None:
    """The corpus-service leg exports the service backend into the environment,
    and that sidecar serves no unresolved-first census — so the ambient setting
    has to be refused as clearly as an explicit flag."""
    env = {
        "FEDCOURTS_CORPUS_ROOT": str(corpus_db.parent),
        "FEDCOURTS_CORPUS_BACKEND": "service",
    }

    ambient = CliRunner().invoke(app, ["corpus-integration-case"], env=env)
    assert ambient.exit_code == 2
    assert "cannot resolve a case" in _plain(ambient.stderr)

    explicit = CliRunner().invoke(
        app, ["corpus-integration-case", "--corpus-backend", "service"], env=env
    )
    assert explicit.exit_code == 2
    assert "choose local, ranged" in _plain(explicit.stderr)


def test_case_cli_exits_1_without_a_pulled_corpus(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        ["corpus-integration-case"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )

    assert result.exit_code == 1
    assert "corpus-pull" in _plain(result.stderr)
