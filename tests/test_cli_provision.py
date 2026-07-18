import json
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from tests.conftest import FixtureCorpus

runner = CliRunner()

# A snapshot whose latest entry states the disposition — the payload a forward
# cell must never be provisioned from (it would hand the predictor the outcome).
_DECIDED_PAYLOAD = {
    "id": 305,
    "docket_number": "24-12",
    "docket_entries": [
        {"id": 1, "description": "Petition for writ of certiorari filed."},
        {
            "id": 2,
            "description": (
                "Judgment VACATED and case REMANDED for further consideration "
                "in light of Louisiana v. Callais."
            ),
        },
    ],
}


def _seed_decided_snapshot(fixture_corpus: FixtureCorpus) -> None:
    """Overlay a newer, decided-looking snapshot onto the open fixture case scotus/305."""
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 13), _DECIDED_PAYLOAD)


def test_provision_snapshot_writes_latest_from_corpus(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])

    assert result.exit_code == 0, result.output
    # scotus/305's latest fixture snapshot is dated 2025-03-03.
    dest = CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2025-03-03")
    payload = json.loads(dest.read_text())
    assert payload["docket_number"] == "24-12"
    assert payload["docket_entries"]  # the materialized snapshot carries docket entries


def test_provision_snapshot_honors_explicit_out(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    out = tmp_path / "scratch" / "snap.json"

    result = runner.invoke(
        app, ["provision-snapshot", "--court", "ca9", "--docket", "101", "--out", str(out)]
    )

    assert result.exit_code == 0, result.output
    assert json.loads(out.read_text())["docket_number"] == "22-15001"


def test_provision_snapshot_missing_corpus_snapshot_exits_nonzero(
    fixture_corpus: FixtureCorpus,
) -> None:
    # 999 is not in the fixture, so the corpus holds no snapshot for it.
    result = runner.invoke(app, ["provision-snapshot", "--court", "ca9", "--docket", "999"])

    assert result.exit_code == 1
    assert "No snapshot" in result.output


def test_provision_snapshot_refuses_a_forward_cell_on_a_terminal_snapshot(
    fixture_corpus: FixtureCorpus,
) -> None:
    # Leakage guard: under --refuse-terminal the latest snapshot's last entry
    # reads terminal (a GVR), so a forward cell must not be materialized — and
    # the refusal must write nothing (no snapshot, no context.json), leaving
    # the cell snapshot-less.
    _seed_decided_snapshot(fixture_corpus)

    result = runner.invoke(
        app,
        ["provision-snapshot", "--court", "scotus", "--docket", "305", "--refuse-terminal"],
    )

    assert result.exit_code == 3
    assert "refusing to provision forward cell" in result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2026-07-13").exists()
    assert not paths.cell_context.exists()


def test_provision_snapshot_refuses_a_disposition_masked_by_trailing_cleanup(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The leak shape (scotus/25-243): the cert-before-judgment GRANT is not the
    # last entry — post-disposition cleanup ("Judgment Issued", a stay
    # application denied as moot) trails it — so the latest-entry rule misses it.
    # The whole-snapshot disposition scan must still refuse the forward cell.
    masked = {
        "id": 305,
        "docket_number": "25-243",
        "docket_entries": [
            {"id": 1, "description": "Petition for writ of certiorari before judgment GRANTED."},
            {"id": 2, "description": "Judgment Issued."},
            {"id": 3, "description": "Application (25A1229) denied as moot by Justice Thomas."},
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 17), masked)

    result = runner.invoke(
        app,
        ["provision-snapshot", "--court", "scotus", "--docket", "305", "--refuse-terminal"],
    )

    assert result.exit_code == 3
    assert "refusing to provision forward cell" in result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-17").exists()


def test_provision_snapshot_default_still_provisions_a_terminal_snapshot(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The guard is opt-in: run-evaluate invokes provision-snapshot with no
    # flag (and no --mode), and its cells target exactly decided dockets — a
    # terminal latest entry must still provision under the defaults.
    _seed_decided_snapshot(fixture_corpus)

    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    payload = json.loads(paths.snapshot("2026-07-13").read_text())
    assert payload["docket_number"] == "24-12"
    assert paths.cell_context.exists()


def test_provision_snapshot_replay_mode_is_exempt_from_the_terminal_guard(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # A replay cell is *meant* to see a decided docket (its own provisioner
    # truncates point-in-time), so even with the flag the guard keys on
    # forward mode.
    _seed_decided_snapshot(fixture_corpus)
    out = tmp_path / "replay" / "snap.json"

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--mode",
            "replay",
            "--refuse-terminal",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(out.read_text())["docket_number"] == "24-12"


# The raw live-channel snapshot shape: the disposition order sits mid-docket
# with an administrative notation after it, so the latest-entry routing rule
# alone cannot see it — the guard's whole-snapshot disposition scan must.
_LIVE_DECIDED_PAYLOAD = {
    "CaseNumber": "24-12 ",
    "ProceedingsandOrder": [
        {"Date": "Jun 01 2025", "Text": "Petition for a writ of certiorari filed."},
        {
            "Date": "May 11 2026",
            "Text": (
                "Judgment VACATED and case REMANDED for further consideration "
                "in light of Louisiana v. Callais."
            ),
        },
        {"Date": "May 11 2026", "Text": "Judgment Issued."},
        {"Date": "May 11 2026", "Text": "Application (25A1231) denied as moot."},
    ],
}


def test_provision_snapshot_refuses_a_live_shape_snapshot_with_a_buried_disposition(
    fixture_corpus: FixtureCorpus,
) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 13), _LIVE_DECIDED_PAYLOAD)

    result = runner.invoke(
        app,
        ["provision-snapshot", "--court", "scotus", "--docket", "305", "--refuse-terminal"],
    )

    assert result.exit_code == 3
    assert "refusing to provision forward cell" in result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 305).cell_context.exists()


def test_provision_snapshot_guard_ignores_a_pending_live_shape_snapshot(
    fixture_corpus: FixtureCorpus,
) -> None:
    # A genuinely pending live snapshot (filed + distributed, no disposition)
    # provisions under the guard — the disposition scan must not read routine
    # entries as outcomes.
    pending = {
        "CaseNumber": "24-12 ",
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "Jun 20 2026", "Text": "Brief of respondent in opposition filed."},
            {"Date": "Jul 01 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."},
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 14), pending)

    result = runner.invoke(
        app,
        ["provision-snapshot", "--court", "scotus", "--docket", "305", "--refuse-terminal"],
    )

    assert result.exit_code == 0, result.output
