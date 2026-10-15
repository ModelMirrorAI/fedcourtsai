"""The pre-mint poll through ``provision-snapshot``.

A forward cell's stored snapshot can be days behind the docket, so provisioning
polls the live docket once more just before writing the record. These pin that a
decided docket refuses the cell, that an open one records its poll for the usage
record without touching the cell's own context, and that a failed poll lets the
cell proceed on the stored-snapshot gates.
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner, Result

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from tests.conftest import FixtureCorpus
from tests.test_cli_provision import _GRANTED_PENDING_PAYLOAD

runner = CliRunner()

_LIVE_PENDING = {
    "CaseNumber": "24-12 ",
    "ProceedingsandOrder": [
        {"Text": "Petition for writ of certiorari filed."},
        {"Text": "Petition GRANTED."},
        {"Text": "Argued. For petitioner: counsel of record."},
    ],
}
_LIVE_DECIDED = {
    "CaseNumber": "24-12 ",
    "ProceedingsandOrder": [
        *_LIVE_PENDING["ProceedingsandOrder"],
        {"Text": "JUDGMENT ISSUED."},
    ],
}


class _LiveDocket:
    def __init__(self, payload: dict[str, Any] | None) -> None:
        self.payload = payload
        self.fetched: list[tuple[int, int, str]] = []

    def __enter__(self) -> "_LiveDocket":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get_docket_response(
        self, term: int, serial: int, *, form: str = "cert"
    ) -> httpx.Response | None:
        self.fetched.append((term, serial, form))
        if self.payload is None:
            return None
        return httpx.Response(
            200,
            content=json.dumps(self.payload).encode(),
            request=httpx.Request("GET", "https://www.supremecourt.gov/"),
        )


@pytest.fixture
def granted_pending(fixture_corpus: FixtureCorpus) -> FixtureCorpus:
    """scotus/305 as a granted, argued, undecided merits docket: a forward merits cell."""
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 20), _GRANTED_PENDING_PAYLOAD)
    return fixture_corpus


def _with_live_docket(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any] | None
) -> _LiveDocket:
    live = _LiveDocket(payload)
    monkeypatch.setattr("fedcourtsai.pipeline.pre_mint.bounded_client", lambda: live)
    return live


def _provision(*extra: str) -> Result:
    return runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-order-judgment",
            "--mode",
            "forward",
            "--refuse-terminal",
            *extra,
        ],
    )


def test_a_forward_cell_the_live_docket_shows_decided_is_refused(
    granted_pending: FixtureCorpus, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    live = _with_live_docket(monkeypatch, _LIVE_DECIDED)
    out = tmp_path / "poll.json"

    result = _provision("--pre-mint-poll", "--pre-mint-poll-out", str(out))

    assert result.exit_code == 3, result.output
    assert "live docket polled at" in result.output
    assert live.fetched == [(24, 12, "cert")]
    assert json.loads(out.read_text())["state"] == "decided"
    assert not CasePaths(granted_pending.data_root, "scotus", 305).cell_context.exists()


def test_a_forward_cell_the_live_docket_shows_open_records_its_poll(
    granted_pending: FixtureCorpus, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _with_live_docket(monkeypatch, _LIVE_PENDING)
    out = tmp_path / "poll.json"

    result = _provision("--pre-mint-poll", "--pre-mint-poll-out", str(out))

    assert result.exit_code == 0, result.output
    poll = json.loads(out.read_text())
    assert poll["state"] == "open"
    assert poll["polled_at"].endswith("Z")
    # The poll is harness provenance, never cell input: context.json does not carry it.
    context = json.loads(
        CasePaths(granted_pending.data_root, "scotus", 305).cell_context.read_text()
    )
    assert "pre_mint_poll" not in context


def test_a_failed_poll_lets_the_cell_proceed_and_says_so(
    granted_pending: FixtureCorpus, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _with_live_docket(monkeypatch, None)
    out = tmp_path / "poll.json"

    result = _provision("--pre-mint-poll", "--pre-mint-poll-out", str(out))

    assert result.exit_code == 0, result.output
    assert "established nothing" in result.output
    assert json.loads(out.read_text())["state"] == "unavailable"


def test_no_poll_runs_without_the_flag(
    granted_pending: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    live = _with_live_docket(monkeypatch, None)

    result = _provision()

    assert result.exit_code == 0, result.output
    assert live.fetched == []


def test_poll_docket_records_the_post_run_poll_and_never_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    live = _with_live_docket(monkeypatch, _LIVE_DECIDED)
    out = tmp_path / "post.json"

    result = runner.invoke(
        app,
        [
            "poll-docket",
            "--court",
            "scotus",
            "--docket-number",
            "24-12",
            "--event",
            "evt-order-judgment",
            "--out",
            str(out),
        ],
    )

    # Record only: a decided post-run poll exits 0 and removes nothing.
    assert result.exit_code == 0, result.output
    assert live.fetched == [(24, 12, "cert")]
    record = json.loads(out.read_text())
    assert record["state"] == "decided"
    assert record["docket_number"] == "24-12"
