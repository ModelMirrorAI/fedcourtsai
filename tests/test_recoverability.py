"""Unit tests for the read-only recoverability probe (issue #369).

Everything here runs against a canned, stubbed client — no live network — mirroring
the stub seam described in ``docs/testing.md``. The three headline cases the probe
must distinguish are a cert-order **entry** (recoverable), a **cluster** disposition
(recoverable), and a **genuinely bare** shell (absent).
"""

from __future__ import annotations

import json
from types import TracebackType
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.pipeline.recoverability import (
    Classification,
    ProbeReport,
    parse_docket_pairs,
    probe_docket,
    probe_dockets,
    render_summary,
    scan_entries,
)
from fedcourtsai.schemas import Disposition

JsonDict = dict[str, Any]


class StubClient:
    """Canned CourtListener responses keyed by docket id; asserts read-only use."""

    def __init__(
        self,
        dockets: dict[int, JsonDict],
        entries: dict[int, list[JsonDict]] | None = None,
        clusters: dict[int, JsonDict] | None = None,
    ) -> None:
        self._dockets = dockets
        self._entries = entries or {}
        self._clusters = clusters or {}

    def __enter__(self) -> StubClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    def get_docket(self, docket_id: int) -> JsonDict:
        if docket_id not in self._dockets:
            raise httpx.HTTPStatusError(
                "404", request=httpx.Request("GET", "x"), response=httpx.Response(404)
            )
        return self._dockets[docket_id]

    def iter_docket_entries(self, docket_id: int) -> list[JsonDict]:
        return self._entries.get(docket_id, [])

    def get_opinion_cluster(self, cluster_id: int) -> JsonDict:
        if cluster_id not in self._clusters:
            raise httpx.HTTPStatusError(
                "404", request=httpx.Request("GET", "x"), response=httpx.Response(404)
            )
        return self._clusters[cluster_id]


def _bare_docket(docket_id: int, **overrides: Any) -> JsonDict:
    base: JsonDict = {
        "id": docket_id,
        "case_name": "Petitioner v. Respondent",
        "date_filed": "1994-05-01",
        "date_terminated": None,
        "clusters": [],
    }
    base.update(overrides)
    return base


# --- the three headline classifications ---------------------------------------


def test_entry_order_cert_denial_is_recoverable() -> None:
    client = StubClient(
        dockets={1000512: _bare_docket(1000512)},
        entries={
            1000512: [
                {"id": 9, "description": "Waiver of right of respondent filed."},
                {"id": 12, "description": "Petition for writ of certiorari DENIED."},
            ]
        },
    )
    probe = probe_docket(client, "scotus", 1000512)
    assert probe.classification is Classification.recoverable
    assert probe.source == "entry-order"
    assert probe.entry_signals[0].disposition is Disposition.denied
    assert "DENIED" in probe.entry_signals[0].snippet
    assert probe.error is None


def test_cluster_disposition_is_recoverable() -> None:
    client = StubClient(
        dockets={
            1002339: _bare_docket(
                1002339,
                date_terminated="1998-06-25",
                clusters=["https://www.courtlistener.com/api/rest/v4/clusters/778899/"],
            )
        },
        clusters={
            778899: {
                "id": 778899,
                "disposition": "Affirmed in part, reversed in part",
                "precedential_status": "Published",
                "date_filed": "1998-06-25",
                "citations": [{"volume": "524", "reporter": "U.S.", "page": "775"}],
            }
        },
    )
    probe = probe_docket(client, "scotus", 1002339)
    # "reversed" isn't in the vocabulary, but the cluster carries a citation → the
    # published opinion's disposition is recoverable by enrichment.
    assert probe.classification is Classification.recoverable
    assert probe.source == "citation"
    assert probe.cluster is not None
    assert probe.cluster.citations == ["524 U.S. 775"]


def test_cluster_with_machine_readable_disposition_names_that_source() -> None:
    client = StubClient(
        dockets={7: _bare_docket(7, clusters=[7001])},
        clusters={7001: {"id": 7001, "disposition": "Petition granted", "citations": []}},
    )
    probe = probe_docket(client, "scotus", 7)
    assert probe.classification is Classification.recoverable
    assert probe.source == "cluster-disposition"
    assert probe.cluster is not None
    assert probe.cluster.disposition is Disposition.granted


def test_genuinely_bare_docket_is_absent() -> None:
    client = StubClient(dockets={1003943: _bare_docket(1003943)}, entries={1003943: []})
    probe = probe_docket(client, "scotus", 1003943)
    assert probe.classification is Classification.absent
    assert probe.source is None
    assert probe.docket_entry_count == 0
    assert "bare" in probe.reason


# --- the middle ground and other sources --------------------------------------


def test_linked_cluster_without_disposition_or_citation_is_ambiguous() -> None:
    # The #333 pattern: a linked cluster exists but exposes nothing usable.
    client = StubClient(
        dockets={1004289: _bare_docket(1004289, clusters=[42])},
        clusters={
            42: {"id": 42, "disposition": None, "precedential_status": None, "citations": []}
        },
    )
    probe = probe_docket(client, "scotus", 1004289)
    assert probe.classification is Classification.ambiguous
    assert probe.cluster is not None
    assert probe.cluster.cluster_id == 42


def test_termination_date_alone_is_recoverable() -> None:
    client = StubClient(dockets={5: _bare_docket(5, date_terminated="2005-03-01")})
    probe = probe_docket(client, "scotus", 5)
    assert probe.classification is Classification.recoverable
    assert probe.source == "date_terminated"


def test_other_only_text_is_ambiguous() -> None:
    client = StubClient(
        dockets={6: _bare_docket(6, disposition="Distributed for conference")},
    )
    probe = probe_docket(client, "scotus", 6)
    # Normalizes only to the `other` catch-all → not machine-readable → ambiguous.
    assert probe.classification is Classification.ambiguous
    assert probe.docket_disposition is Disposition.other


def test_gvr_entry_signals_granted() -> None:
    entries = [{"id": 1, "description": "Petition GRANTED. Judgment vacated and case remanded."}]
    signals = scan_entries(entries)
    assert len(signals) == 1
    assert signals[0].disposition is Disposition.granted
    assert signals[0].label in {"GVR", "cert granted"}


# --- resilience: fetch failures are reported, never raised ---------------------


def test_missing_docket_is_reported_as_error_not_raised() -> None:
    client = StubClient(dockets={})
    probe = probe_docket(client, "scotus", 404404)
    assert probe.classification is None
    assert probe.error is not None
    assert "404" in probe.error


def test_missing_cluster_degrades_to_note_and_still_classifies() -> None:
    client = StubClient(
        dockets={8: _bare_docket(8, date_terminated="2001-01-01", clusters=[9999])},
        clusters={},
    )
    probe = probe_docket(client, "scotus", 8)
    # Cluster fetch failed, but the docket still classifies on its termination date.
    assert probe.classification is Classification.recoverable
    assert probe.source == "date_terminated"
    assert probe.error is not None and "9999" in probe.error


# --- parsing + rendering -------------------------------------------------------


def test_parse_docket_pairs_dedupes_and_preserves_order() -> None:
    pairs = parse_docket_pairs(["scotus/1000512,scotus/1000515", "scotus/1000512", "ca9/7"])
    assert pairs == [("scotus", 1000512), ("scotus", 1000515), ("ca9", 7)]


@pytest.mark.parametrize("bad", ["", "scotus", "scotus/", "/123", "scotus/abc"])
def test_parse_docket_pairs_rejects_malformed(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_docket_pairs([bad])


def test_counts_and_summary_render() -> None:
    report = probe_dockets(
        StubClient(
            dockets={
                1: _bare_docket(1),  # absent
                2: _bare_docket(2, date_terminated="2000-01-01"),  # recoverable
            },
            entries={1: []},
        ),
        [("scotus", 1), ("scotus", 2), ("scotus", 404)],
    )
    counts = report.counts()
    assert counts["ABSENT"] == 1
    assert counts["RECOVERABLE"] == 1
    assert counts["error"] == 1
    summary = render_summary(report)
    assert "Recoverability probe" in summary
    assert "`scotus/404`" in summary and "ERROR" in summary


# --- the CLI command is read-only and emits JSON + a summary -------------------


def test_cli_probe_recoverability_is_read_only_and_emits_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    stub = StubClient(
        dockets={
            1000512: _bare_docket(1000512),
            1000515: _bare_docket(1000515, date_terminated="1999-01-01"),
        },
        entries={1000512: [{"id": 1, "description": "Certiorari denied."}]},
    )
    monkeypatch.setattr(cli, "_client", lambda: stub)
    summary_path = tmp_path / "summary.md"
    result = CliRunner().invoke(
        cli.app,
        [
            "probe-recoverability",
            "--dockets",
            "scotus/1000512,scotus/1000515",
            "--summary-out",
            str(summary_path),
        ],
    )
    assert result.exit_code == 0, result.output
    report = ProbeReport.model_validate_json(result.stdout)
    verdicts = {d.docket: d.classification for d in report.dockets}
    assert verdicts[1000512] is Classification.recoverable
    assert verdicts[1000515] is Classification.recoverable
    # The summary is appended to the file and echoed to stderr; nothing under data/.
    assert "Recoverability probe" in summary_path.read_text()
    assert "Recoverability probe" in result.stderr
    assert not (tmp_path / "data").exists()


def test_cli_probe_recoverability_rejects_bad_dockets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_client", lambda: StubClient(dockets={}))
    result = CliRunner().invoke(cli.app, ["probe-recoverability", "--dockets", "not-a-pair"])
    assert result.exit_code == 2
    assert "bad --dockets" in result.stderr


def test_report_json_roundtrips() -> None:
    report = probe_dockets(
        StubClient(dockets={1: _bare_docket(1)}, entries={1: []}), [("scotus", 1)]
    )
    payload = json.loads(report.model_dump_json())
    assert payload["dockets"][0]["classification"] == "ABSENT"
