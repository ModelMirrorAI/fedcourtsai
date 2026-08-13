import json
from datetime import date
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cell_context, cert_signals, ingest
from tests.conftest import FixtureCorpus

runner = CliRunner()

# A snapshot whose latest entry states the disposition — the payload a forward
# cell must never be provisioned from (it would hand the predictor the outcome).
_DECIDED_PAYLOAD: dict[str, Any] = {
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


# A granted-but-undecided merits docket: the grant order is the entry that
# opened the merits proceeding, and the case is argued but not yet decided.
_GRANTED_PENDING_PAYLOAD: dict[str, Any] = {
    "id": 305,
    "docket_number": "24-12",
    "docket_entries": [
        {"id": 1, "description": "Petition for writ of certiorari filed."},
        {"id": 2, "description": "Petition GRANTED."},
        {"id": 3, "description": "Argued. For petitioner: counsel of record."},
    ],
}


def test_provision_snapshot_provisions_a_merits_cell_on_its_own_grant_order(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The cert grant that opened the merits event is not that event's outcome.

    The guard is keyed on the event: on the merits event the disclosed outcome
    is the judgment, so a grant order — which every merits cell's docket
    necessarily carries, since it is what minted the cell — must provision
    rather than refuse. Without the key the merits fan-out would be a fan-out
    of snapshot-less cells.
    """
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 20), _GRANTED_PENDING_PAYLOAD)

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-order-judgment",
            "--refuse-terminal",
        ],
    )

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert paths.snapshot("2026-07-20").exists()
    assert paths.cell_context.exists()


def test_provision_snapshot_refuses_a_merits_cell_on_a_decided_judgment(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The merits event's own leak: the judgment is legible in the snapshot, so
    # the cell was minted against a docket that is already decided.
    decided = {
        **_GRANTED_PENDING_PAYLOAD,
        "docket_entries": [
            *_GRANTED_PENDING_PAYLOAD["docket_entries"],
            {"id": 4, "description": "Judgment REVERSED and case REMANDED."},
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 21), decided)

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-order-judgment",
            "--refuse-terminal",
        ],
    )

    assert result.exit_code == 3
    assert "merits judgment" in result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-21").exists()


def test_provision_snapshot_refuses_a_merits_cell_on_a_terminal_entry_the_parser_misses(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The merits guard keeps the cert scan's recall rather than narrowing to the
    # deterministic judgment parser: the parser is conservative by design (a
    # miss costs one unparsed row in a descriptive count) while a miss here
    # hands a forward cell its answer. "Opinion Issued" parses as no judgment
    # and is unmistakably a decided merits docket.
    decided = {
        **_GRANTED_PENDING_PAYLOAD,
        "docket_entries": [
            *_GRANTED_PENDING_PAYLOAD["docket_entries"],
            {"id": 4, "description": "Opinion Issued."},
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 23), decided)

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-order-judgment",
            "--refuse-terminal",
        ],
    )

    assert result.exit_code == 3
    assert "reads as terminal" in result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-23").exists()


def test_provision_snapshot_provisions_a_merits_cell_opened_before_judgment(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The one terminal shape dropped from the merits scan: a cert-before-judgment
    # GRANT opens a merits proceeding exactly as an ordinary grant does, so it is
    # the cell's own opening rather than its outcome.
    cbj = {
        "id": 305,
        "docket_number": "25-243",
        "docket_entries": [
            {"id": 1, "description": "Petition for writ of certiorari before judgment GRANTED."},
            {"id": 2, "description": "Argued. For petitioner: counsel of record."},
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 24), cbj)

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-order-judgment",
            "--refuse-terminal",
        ],
    )

    assert result.exit_code == 0, result.output
    assert CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-24").exists()


def test_provision_snapshot_still_refuses_a_cert_cell_on_the_same_grant_order(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The other side of the key: the same payload, addressed as the cert
    # petition's cell, discloses that petition's outcome and must be refused.
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 22), _GRANTED_PENDING_PAYLOAD)

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
            "--refuse-terminal",
        ],
    )

    assert result.exit_code == 3
    assert "disposition order" in result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2026-07-22").exists()
    assert not paths.cell_context.exists()


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


# A payload that discloses its own trajectory: two distinct conferences and a
# CVSG invitation, the two signals the salience band turns on.
_DISTRIBUTED_PAYLOAD: dict[str, Any] = {
    # The real live supremecourt.gov shape: `CaseNumber`, not `docket_number`.
    # Pairing REST keys with live proceedings would be a payload no upstream
    # emits, and would hide the Term derivation entirely.
    "CaseNumber": "24-12 ",
    "ProceedingsandOrder": [
        {"Date": "Jan 5 2025", "Text": "Petition for a writ of certiorari filed."},
        {"Date": "Feb 7 2025", "Text": "DISTRIBUTED for Conference of February 21, 2025."},
        {"Date": "Feb 24 2025", "Text": "DISTRIBUTED for Conference of March 7, 2025."},
        {"Date": "Mar 3 2025", "Text": "The Solicitor General is invited to file a brief."},
    ],
}


def _provision(
    fixture_corpus: FixtureCorpus, payload: dict[str, object], on: date
) -> dict[str, Any]:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", on, payload)
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert result.exit_code == 0, result.output
    context: dict[str, Any] = json.loads(
        CasePaths(fixture_corpus.data_root, "scotus", 305).cell_context.read_text()
    )
    return context


def test_the_cell_context_freezes_the_band_the_snapshot_discloses(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The conditioning is derived from the payload the cell reads, not the corpus
    row, so it records what this cell could actually see."""
    context = _provision(fixture_corpus, _DISTRIBUTED_PAYLOAD, date(2026, 7, 14))
    assert context["mode"] == "forward"
    assert context["signals_observable"] is True
    # Two distinct conferences, so one relist; a CVSG lifts it to the top band.
    assert context["distribution_count"] == 2
    assert context["cvsg_date"] == "2025-03-03"
    assert context["band"] == "high"
    assert context["salience_version"] == "sal-v2"
    assert context["term"] == 2024  # docket 24-12


def test_the_cell_context_reads_the_caption_band_from_the_payload(
    fixture_corpus: FixtureCorpus,
) -> None:
    """A federal-petitioner arrival cell must freeze `federal`, and the caption
    has to come from the payload the cell reads — a band frozen from a corpus
    column the snapshot never disclosed would break the reproducibility rule
    the module states (an auditor re-parses the provisioned snapshot and
    recovers the same band)."""
    payload: dict[str, Any] = {
        "CaseNumber": "24-12 ",
        "PetitionerTitle": "United States",
        "ProceedingsandOrder": [
            {"Date": "Jan 5 2025", "Text": "Petition for a writ of certiorari filed."},
        ],
    }
    context = _provision(fixture_corpus, payload, date(2026, 7, 14))
    assert context["signals_observable"] is True
    assert context["distribution_count"] == 0  # arrival posture: nothing distributed
    assert context["band"] == "federal"
    assert context["salience_version"] == "sal-v2"


def test_a_repeated_conference_does_not_inflate_the_frozen_count(
    fixture_corpus: FixtureCorpus,
) -> None:
    """Distinct parsed conference dates, not raw entry matches — a re-docketed
    notice of the same conference must not read as another relist."""
    payload: dict[str, Any] = {
        "CaseNumber": "24-12 ",
        "ProceedingsandOrder": [
            # Two spellings of one conference, plus a phrase the capture group
            # matches but no date parses out of. Deduping on the matched text
            # rather than the parsed date would read three distributions here and
            # move the frozen band two tiers.
            {"Date": "Feb 7 2025", "Text": "DISTRIBUTED for Conference of February 21, 2025."},
            {"Date": "Feb 8 2025", "Text": "DISTRIBUTED for Conference of 2/21/2025."},
            {"Date": "Feb 9 2025", "Text": "DISTRIBUTED for Conference of the Court."},
        ],
    }
    context = _provision(fixture_corpus, payload, date(2026, 7, 15))
    assert context["distribution_count"] == 1
    assert context["band"] == "baseline"  # one distribution is no relist


def test_the_frozen_count_agrees_with_what_ingest_would_record(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The reproducibility claim: provisioning and the corpus must not disagree
    about one payload, or the frozen band cannot be re-derived by an auditor."""
    payload = _DISTRIBUTED_PAYLOAD
    assert cert_signals.snapshot_distribution_count(payload) == ingest._live_distribution_count(
        ingest._live_entries(payload)
    )


def test_an_empty_proceedings_list_is_observable_and_zero(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The boundary `signals_observable` exists to draw: a docket with no entries
    yet is observed to have none, which is not the same as a redacted snapshot."""
    context = _provision(
        fixture_corpus,
        {"CaseNumber": "24-12 ", "ProceedingsandOrder": []},
        date(2026, 7, 17),
    )
    assert context["signals_observable"] is True
    assert context["distribution_count"] == 0
    assert context["band"] == "baseline"


def test_a_rest_shaped_snapshot_also_freezes_its_term(fixture_corpus: FixtureCorpus) -> None:
    """The other payload shape carries `docket_number`; both must resolve a Term."""
    context = _provision(
        fixture_corpus,
        {
            "id": 305,
            "docket_number": "24-12",
            "docket_entries": [{"description": "DISTRIBUTED for Conference of February 21, 2025."}],
        },
        date(2026, 7, 18),
    )
    assert context["term"] == 2024
    assert context["distribution_count"] == 1


def test_a_snapshot_without_proceedings_freezes_no_band(fixture_corpus: FixtureCorpus) -> None:
    """A redacted replay snapshot drops the proceedings key wholesale. Reading that
    absence as zero distributions would assert `baseline` about a petition whose
    posture is simply unknown, so the band is left null and the evaluator falls
    back rather than scoring against an invented one."""
    context = _provision(fixture_corpus, {"id": 305, "docket_number": "24-12"}, date(2026, 7, 16))
    assert context["signals_observable"] is False
    assert context["distribution_count"] is None
    assert context["band"] is None
    assert context["salience_version"] is None


def test_stamping_clears_a_context_the_agent_wrote_itself(
    fixture_corpus: FixtureCorpus,
) -> None:
    """`context` is a scoring input, so it is the harness's like `process_version`.

    Provisioning is continue-on-error, so a cell can run snapshot-less — and that
    is exactly the case where an agent inventing its own band would hand itself a
    baseline. The stamp assigns unconditionally, so an authored block is cleared
    rather than preserved.
    """
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    event = paths.event("evt-petition-disposition")
    target = event.prediction("claude-baseline", "20260101T000000Z")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "case_id": "scotus/305",
                "event_id": "evt-petition-disposition",
                "predictor_id": "claude-baseline",
                "engine": "claude-code",
                "run_id": "20260101T000000Z",
                "created_at": "2026-01-01T00:00:00",
                "input_snapshot": "record/snapshots/2025-03-03.json",
                "granted": 1,
                "probability": 0.9,
                "predicted_disposition": "granted",
                # An agent asserting the strongest band for itself.
                "context": {
                    "schema_version": "1.0",
                    "mode": "forward",
                    "snapshot_date": "2025-03-03",
                    "signals_observable": True,
                    "distribution_count": 9,
                    "band": "high",
                    "term": 2024,
                },
            }
        )
    )
    assert paths.cell_context.exists() is False  # nothing was provisioned

    result = runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
            "--run-id",
            "20260101T000000Z",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(target.read_text())["context"] is None


# An application-docket snapshot: pending, then disposed in language the interim
# resolving vocabulary misses (relief named, no "application" anchor).
_APPLICATION_PENDING: dict[str, Any] = {
    "CaseNumber": "25A1 ",
    "ProceedingsandOrder": [
        {
            "Date": "Jul 01 2026",
            "Text": "Application (25A1) for a stay, submitted to The Chief Justice.",
        },
    ],
}


def test_an_application_snapshot_freezes_no_band() -> None:
    """An application docket takes no salience band by rule, not by parse
    accident: sal-v1's features are cert observations that do not exist on the
    interim docket, and a band frozen from their absence would hand the
    evaluator a cert-population base rate for a cell that resolves on the
    interim standard."""
    context = cell_context.build(
        "scotus/9525000001", date(2026, 7, 9), _APPLICATION_PENDING, "forward"
    )
    assert context.signals_observable is True  # proceedings are present
    assert context.band is None
    assert context.salience_version is None
    assert context.term is None  # the A-form carries no cert Term


def test_provision_snapshot_refuses_an_application_disposal_the_vocabulary_missed(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The forward-cell leakage guard's application branch: the cert-shaped
    # scans match no application phrasing, and the interim resolver's exact
    # vocabulary misses a relief-named disposal — the high-recall interim scan
    # must still refuse the cell.
    disposed: dict[str, Any] = {
        "CaseNumber": "25A1 ",
        "ProceedingsandOrder": [
            *_APPLICATION_PENDING["ProceedingsandOrder"],
            {
                "Date": "Jul 18 2026",
                "Text": "Stay of execution granted by The Chief Justice pending further order.",
            },
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/9525000001", date(2026, 7, 19), disposed)

    result = runner.invoke(
        app,
        ["provision-snapshot", "--court", "scotus", "--docket", "9525000001", "--refuse-terminal"],
    )

    assert result.exit_code == 3
    assert "interim disposal" in result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 9525000001).cell_context.exists()
