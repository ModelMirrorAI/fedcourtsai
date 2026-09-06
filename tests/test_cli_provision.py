import json
from datetime import date
from pathlib import Path
from typing import Any

from typer.testing import CliRunner, Result

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import arrival_cut, cell_context, cert_signals, ingest
from fedcourtsai.pipeline.salience import SALIENCE_VERSION
from fedcourtsai.schemas import EventKind, Moment, Stage
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
    # the refusal must write nothing (no snapshot, no context.json), which is
    # what the workflow's gate reads as a refused cell.
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
    of refused cells.
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
    assert context["salience_version"] == SALIENCE_VERSION
    assert context["term"] == 2024  # docket 24-12
    # The interim trio is NOT frozen on a cert cell. The block is part of the
    # cell's information set, so widening it for a stage that declares no claim
    # reading it would move what every cert cell sees with no prompt edit to
    # bound the change.
    assert context["response_requested"] is None
    assert context["referred_to_court"] is None
    assert context["amicus_briefs"] is None


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
    assert context["salience_version"] == SALIENCE_VERSION


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

    A cell can still reach the stamp with nothing provisioned to freeze — and that
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
    interim standard.

    What it *does* freeze is the interim conditioning: the escalation trio as at
    provisioning — the prediction end of the three increment claims — and the
    application Term the interim base rate pools strictly before."""
    context = cell_context.build(
        "scotus/9525000001", date(2026, 7, 9), _APPLICATION_PENDING, "forward"
    )
    assert context.signals_observable is True  # proceedings are present
    assert context.band is None
    assert context.salience_version is None
    # No cert Term on an A-form number; the application Term is what is frozen,
    # and the two never fill the field at once.
    assert context.term == 2025
    # The arrival snapshot discloses only the application itself: no response
    # called for, no referral, no amicus. Observed as false, not unknown.
    assert context.response_requested is False
    assert context.referred_to_court is False
    assert context.amicus_briefs == 0


def test_an_application_snapshot_freezes_the_escalation_state_it_discloses() -> None:
    escalated: dict[str, Any] = {
        "CaseNumber": "25A1 ",
        "ProceedingsandOrder": [
            *_APPLICATION_PENDING["ProceedingsandOrder"],
            {
                "Date": "Jul 05 2026",
                "Text": "Response to application (25A1) requested by The Chief Justice.",
            },
            {
                "Date": "Jul 06 2026",
                "Text": "Application (25A1) referred to the Court by The Chief Justice.",
            },
            {"Date": "Jul 07 2026", "Text": "Brief amicus curiae of the State of X filed."},
        ],
    }
    context = cell_context.build("scotus/9525000001", date(2026, 7, 9), escalated, "forward")
    assert context.response_requested is True
    assert context.referred_to_court is True
    assert context.amicus_briefs == 1
    assert context.band is None  # still no band: the rule is the docket form


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


def test_provision_refuses_a_forward_cell_whose_event_the_record_resolved(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The record gate: the corpus flipped the event resolved while the snapshot
    # stayed silent about it (the paused-pipeline shape) — the textual guard
    # sees nothing, the record still refuses, and nothing is written.
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.set_event_resolved(conn, "scotus/305", "evt-petition-disposition", resolved=True)

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--refuse-terminal",
            "--event",
            "evt-petition-disposition",
        ],
    )

    assert result.exit_code == 3
    assert "corpus records evt-petition-disposition resolved" in result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2025-03-03").exists()
    assert not paths.cell_context.exists()


def test_provision_refuses_a_forward_cell_whose_outcome_is_committed(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The ledger's outcome.json is the most specific record of a closed event;
    # it refuses the forward cell even before the corpus flips the flag.
    outcome = (
        CasePaths(fixture_corpus.data_root, "scotus", 305).event("evt-petition-disposition").outcome
    )
    outcome.parent.mkdir(parents=True)
    outcome.write_text("{}")

    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--refuse-terminal",
            "--event",
            "evt-petition-disposition",
        ],
    )

    assert result.exit_code == 3
    assert "already records an outcome" in result.output


def test_provision_refuses_a_stale_forward_snapshot(fixture_corpus: FixtureCorpus) -> None:
    # The staleness bound: scotus/305's latest fixture snapshot (2025-03-03) is
    # far older than 30 days, and a forward cell fed a pre-pause snapshot would
    # claim to be live while answering a stale question. Opt-in via the flag,
    # so evaluate and replay callers are untouched.
    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--refuse-terminal",
            "--event",
            "evt-petition-disposition",
            "--max-snapshot-age-days",
            "30",
        ],
    )

    assert result.exit_code == 3
    assert "forward bound" in result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 305).cell_context.exists()


def test_provision_record_gate_fires_before_the_textual_scan(
    fixture_corpus: FixtureCorpus,
) -> None:
    # scotus/304 is decided in the record (cert denied) AND its snapshot text
    # says so; the refusal must come from the record gate, not the text scan —
    # the ordering that makes the gate mechanical rather than best-effort.
    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "304",
            "--refuse-terminal",
            "--event",
            "evt-petition-disposition",
        ],
    )

    assert result.exit_code == 3
    assert "refusing to provision forward cell" in result.output
    assert "snapshot carries" not in result.output


def test_provision_without_refuse_terminal_still_serves_the_resolved_event(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The evaluate caller provisions decided dockets on purpose; the record
    # gate must stay behind --refuse-terminal.
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.set_event_resolved(conn, "scotus/305", "evt-petition-disposition", resolved=True)

    result = runner.invoke(
        app,
        ["provision-snapshot", "--court", "scotus", "--docket", "305"],
    )

    assert result.exit_code == 0, result.output


def test_the_staleness_bound_is_inclusive_at_the_boundary(
    fixture_corpus: FixtureCorpus, monkeypatch: Any
) -> None:
    # scotus/305's latest fixture snapshot is dated 2025-03-03. At exactly the
    # bound the cell provisions; one day past it refuses — the bound is "older
    # than", not "at least as old as".
    class _FrozenToday(date):
        @classmethod
        def today(cls) -> "_FrozenToday":
            return cls(2025, 4, 2)  # 30 days after the snapshot

    monkeypatch.setattr("fedcourtsai.cli.date", _FrozenToday)
    base = [
        "provision-snapshot",
        "--court",
        "scotus",
        "--docket",
        "305",
        "--refuse-terminal",
        "--event",
        "evt-petition-disposition",
        "--max-snapshot-age-days",
    ]

    at_bound = runner.invoke(app, [*base, "30"])
    assert at_bound.exit_code == 0, at_bound.output

    past_bound = runner.invoke(app, [*base, "29"])
    assert past_bound.exit_code == 3
    assert "forward bound" in past_bound.output


def _provision_305(fixture_corpus: FixtureCorpus) -> CasePaths:
    """Provision scotus/305 the way a predict cell does, and hand back its paths."""
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert result.exit_code == 0, result.output
    return CasePaths(fixture_corpus.data_root, "scotus", 305)


_ASSERT = [
    "assert-cell-record",
    "--court",
    "scotus",
    "--docket",
    "305",
    "--event",
    "evt-petition-disposition",
]


def test_assert_cell_record_accepts_a_complete_record(fixture_corpus: FixtureCorpus) -> None:
    _provision_305(fixture_corpus)

    result = runner.invoke(app, _ASSERT)

    assert result.exit_code == 0, result.output
    assert "record complete" in result.output


def test_assert_cell_record_refuses_when_nothing_was_provisioned(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The failure this guards: a cell whose record never landed would otherwise
    # run its agent and forecast from base rates alone, while its output claims
    # the guaranteed-common snapshot every other predictor read.
    result = runner.invoke(app, _ASSERT)

    assert result.exit_code == 1
    assert "no cell context" in result.output
    assert "context.json" in result.output
    # The refusal is an Actions annotation naming the cell: a fleet of skipped
    # cells has to be attributable per cell from the log, which is the whole
    # reason the command takes an event it does not otherwise need.
    assert "::warning::" in result.output
    assert "scotus/305" in result.output
    assert "evt-petition-disposition" in result.output


def test_assert_cell_record_refuses_a_missing_snapshot(fixture_corpus: FixtureCorpus) -> None:
    # The half-landed write: context.json is there and names a snapshot date,
    # but the snapshot the cell would read is not.
    paths = _provision_305(fixture_corpus)
    paths.snapshot("2025-03-03").unlink()

    result = runner.invoke(app, _ASSERT)

    assert result.exit_code == 1
    assert "no snapshot at" in result.output
    assert "2025-03-03" in result.output


def test_assert_cell_record_refuses_an_empty_snapshot(fixture_corpus: FixtureCorpus) -> None:
    # A truncated read leaves a zero-byte file, which exists but carries no docket.
    paths = _provision_305(fixture_corpus)
    paths.snapshot("2025-03-03").write_text("")

    result = runner.invoke(app, _ASSERT)

    assert result.exit_code == 1
    assert "empty snapshot at" in result.output


def test_assert_cell_record_refuses_a_truncated_snapshot(fixture_corpus: FixtureCorpus) -> None:
    # The half-landed write proper: provisioning writes non-atomically, so a
    # runner killed mid-write leaves a non-empty file that is not a snapshot.
    # A size check passes it; the cell would then read a broken baseline.
    paths = _provision_305(fixture_corpus)
    snapshot = paths.snapshot("2025-03-03")
    snapshot.write_text(snapshot.read_text()[:40])

    result = runner.invoke(app, _ASSERT)

    assert result.exit_code == 1
    assert "unreadable snapshot at" in result.output


def test_assert_cell_record_refuses_an_unparseable_context(fixture_corpus: FixtureCorpus) -> None:
    paths = _provision_305(fixture_corpus)
    paths.cell_context.write_text("{not json")

    result = runner.invoke(app, _ASSERT)

    assert result.exit_code == 1
    assert "unreadable cell context" in result.output


# The moment cutoff: a forward cell placed at the information set its declared
# moment fixes, rather than at the corpus's latest snapshot.

#: A granted case's docket months into the merits stage. The grant on 2026-01-15
#: is the merits moment's own trigger; everything after it belongs to the
#: *briefed* moment, which is a different declared forecast.
_MERITS_TIMELINE: dict[str, Any] = {
    "id": 305,
    "docket_number": "24-12",
    "docket_entries": [
        {
            "id": 1,
            "date_filed": "2025-01-15",
            "description": "Petition for writ of certiorari filed.",
        },
        {"id": 2, "date_filed": "2026-01-15", "description": "Petition GRANTED."},
        {
            "id": 3,
            "date_filed": "2026-03-02",
            "description": "Brief of petitioner on the merits filed.",
        },
        {
            "id": 4,
            "date_filed": "2026-04-06",
            "description": "SET FOR ARGUMENT on Monday, April 27, 2026.",
        },
    ],
}

#: The same docket as the grant left it: what a cell placed at the merits moment
#: should be reading, whichever way provisioning gets there.
_AT_THE_GRANT: dict[str, Any] = {
    "id": 305,
    "docket_number": "24-12",
    "docket_entries": _MERITS_TIMELINE["docket_entries"][:2],
}

#: The docket before the grant — a stored snapshot that does NOT reach the
#: merits moment, however far before the cutoff it happens to sit.
_PENDING_PETITION: dict[str, Any] = {
    "id": 305,
    "docket_number": "24-12",
    "docket_entries": _MERITS_TIMELINE["docket_entries"][:1],
}

_GRANT_DATE = date(2026, 1, 15)
#: The day after the grant, exclusive — so the grant entry survives the cut.
_GRANT_CUTOFF = date(2026, 1, 16)


def _seed_merits_event(
    fixture_corpus: FixtureCorpus, *, opened_at: date | None = _GRANT_DATE
) -> None:
    """Give scotus/305 the merits moment a cert grant opens."""
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-order-judgment",
                    case_id="scotus/305",
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                    moment=Moment.grant,
                    title="Cascade School District v. Doe",
                    decision_target="judgment",
                    opened_at=opened_at,
                )
            ],
        )


def _seed_snapshot(fixture_corpus: FixtureCorpus, on: date, payload: dict[str, Any]) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", on, payload)


def _drop_snapshots_before(fixture_corpus: FixtureCorpus, cutoff: date) -> None:
    """Remove every stored snapshot predating ``cutoff``.

    The fixture gives every case a dated snapshot, so a test about what
    provisioning does when *nothing* stored predates the cutoff has to take that
    one away first.
    """
    with corpus.connect(fixture_corpus.db_path) as conn:
        conn.execute(
            "DELETE FROM snapshots WHERE case_id = ? AND snapshot_date < ?",
            ("scotus/305", cutoff.isoformat()),
        )
        # `corpus.connect` leaves committing to the writers it yields to.
        conn.commit()


def _provision_cell(*args: str) -> Result:
    return runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305", *args])


def _context(fixture_corpus: FixtureCorpus) -> dict[str, Any]:
    context: dict[str, Any] = json.loads(
        CasePaths(fixture_corpus.data_root, "scotus", 305).cell_context.read_text()
    )
    return context


def test_a_merits_cell_takes_the_stored_snapshot_from_before_its_moment(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The strongest point-in-time evidence: a snapshot the docket really served
    # before the grant, which also reflects what had not yet been filed. The
    # latest snapshot exists and is months of merits briefing later; the cell
    # must not be reading it.
    _seed_merits_event(fixture_corpus)
    # Dated at the grant itself, and carrying it: a snapshot pulled earlier could
    # not show the moment, which is what the next test is about.
    _seed_snapshot(fixture_corpus, _GRANT_DATE, _AT_THE_GRANT)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2026-07-20").exists()
    payload = json.loads(paths.snapshot(_GRANT_DATE.isoformat()).read_text())
    descriptions = [entry["description"] for entry in payload["docket_entries"]]
    assert "Petition GRANTED." in descriptions
    assert not any("merits" in text for text in descriptions)
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "dated"
    assert context["cutoff"] == _GRANT_CUTOFF.isoformat()
    assert context["snapshot_date"] == _GRANT_DATE.isoformat()


def test_a_stored_snapshot_that_predates_the_moment_is_not_taken_as_dated(
    fixture_corpus: FixtureCorpus,
) -> None:
    # `snapshot_at` is bounded above by the cutoff and not at all below, so the
    # newest stored snapshot can predate the moment by weeks — routine for an
    # event opened by a backfill at a long-past latched date. Taking it would
    # place a merits cell on a still-pending petition while the artifact recorded
    # `dated` at the grant, putting two very different information sets in one
    # cohort. Reconstruction from the later payload is what actually reaches the
    # moment, so the cell gets that instead.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2025, 11, 3), _PENDING_PETITION)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2025-11-03").exists()
    payload = json.loads(paths.snapshot(_GRANT_CUTOFF.isoformat()).read_text())
    descriptions = [entry["description"] for entry in payload["docket_entries"]]
    assert "Petition GRANTED." in descriptions
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "truncated"
    assert context["cutoff"] == _GRANT_CUTOFF.isoformat()


def test_a_merits_cell_with_no_stored_snapshot_before_its_moment_is_truncated(
    fixture_corpus: FixtureCorpus,
) -> None:
    # No point-in-time snapshot survives, so the docket is reconstructed from the
    # later payload — and re-dated to the cutoff, because a file dated after
    # everything it contains would misstate the cell's own information set.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)
    _drop_snapshots_before(fixture_corpus, _GRANT_CUTOFF)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2026-07-20").exists()
    payload = json.loads(paths.snapshot(_GRANT_CUTOFF.isoformat()).read_text())
    descriptions = [entry["description"] for entry in payload["docket_entries"]]
    # The grant survives its own cutoff; the briefing and the argument setting
    # belong to the briefed moment and do not.
    assert descriptions == [
        "Petition for writ of certiorari filed.",
        "Petition GRANTED.",
    ]
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "truncated"
    assert context["cutoff"] == _GRANT_CUTOFF.isoformat()
    assert context["snapshot_date"] == _GRANT_CUTOFF.isoformat()


def test_the_cert_petition_baseline_is_not_cut_at_its_docketing_date(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The baseline's opened_at is docketing, not the distribution its moment
    # declares, so a cut there would delete the distribution and relist history
    # the cell is conditioned on. The declaration says so; provisioning obeys it.
    # scotus/305's petition event opened at filing, 2025-01-15; the latest
    # snapshot is 2025-03-03 and carries the brief-in-opposition request.
    result = _provision_cell("--event", "evt-petition-disposition")

    assert result.exit_code == 0, result.output
    assert CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2025-03-03").exists()
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "as-stored"
    assert context["cutoff"] is None


def test_a_moment_whose_opening_date_was_never_recorded_is_not_cut(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The moment is declared but the date it happened is not, and a guessed
    # cutoff would condition the cell on a fiction.
    _seed_merits_event(fixture_corpus, opened_at=None)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    assert CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-20").exists()
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "as-stored"
    assert context["cutoff"] is None


def test_no_moment_cutoff_provisions_the_latest_snapshot(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The escape hatch, for reading a cell's docket as it stands now.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)

    result = _provision_cell("--event", "evt-order-judgment", "--no-moment-cutoff")

    assert result.exit_code == 0, result.output
    assert CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-20").exists()
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "as-stored"
    assert context["cutoff"] is None


def test_provisioning_without_an_event_is_never_cut(fixture_corpus: FixtureCorpus) -> None:
    # run-evaluate provisions with no --event: its judge grades a resolved event
    # and must see the whole docket. The case's declared moments and their dates
    # exist either way, so the flag's default must not reach that caller.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)

    result = _provision_cell()

    assert result.exit_code == 0, result.output
    assert CasePaths(fixture_corpus.data_root, "scotus", 305).snapshot("2026-07-20").exists()
    context = _context(fixture_corpus)
    assert context["snapshot_provenance"] == "as-stored"
    assert context["cutoff"] is None


def test_the_cut_takes_the_documents_with_it(fixture_corpus: FixtureCorpus) -> None:
    # The snapshot is half a cell's information set: the merits briefs a
    # grant-moment cell must not read arrive as documents, and an unfiltered
    # record/documents/ would hand them over whatever the snapshot says.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind="petition",
                    url="https://example/petition.pdf",
                    entry_date="2025-01-15",
                    fetched_at=date(2025, 1, 20),
                    text="The petition.",
                ),
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind="merits-brief",
                    url="https://example/merits.pdf",
                    entry_date="2026-03-02",
                    fetched_at=date(2026, 3, 5),
                    text="The merits brief.",
                ),
            ],
        )

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert paths.document("petition").read_text() == "The petition.\n"
    assert not paths.document("merits-brief").exists()
    manifest = json.loads(paths.documents_manifest.read_text())
    assert [entry["kind"] for entry in manifest] == ["petition"]


def test_a_reconstructed_docket_drops_the_top_level_dates_that_postdate_it(
    fixture_corpus: FixtureCorpus,
) -> None:
    # Cutting the argument *entry* while leaving the argument *date* set would
    # remove the fact from one half of the payload and hand it over in the
    # other. The generation stamp goes unconditionally: it dates the pull the
    # docket was reconstructed from, months ahead of everything else in a file
    # re-dated to the cutoff.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(
        fixture_corpus,
        date(2026, 7, 20),
        {
            **_MERITS_TIMELINE,
            "date_filed": "2025-01-15",
            "date_argued": "2026-04-27",
            "sJsonCreationDate": "2026-07-20",
        },
    )
    _drop_snapshots_before(fixture_corpus, _GRANT_CUTOFF)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    payload = json.loads(paths.snapshot(_GRANT_CUTOFF.isoformat()).read_text())
    assert "date_argued" not in payload
    assert "sJsonCreationDate" not in payload
    # The docket's arrival precedes every moment and identifies what the cell is
    # looking at, so it is never subject to the rule.
    assert payload["date_filed"] == "2025-01-15"


def test_a_reconstructed_docket_keeps_a_top_level_date_that_precedes_it(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The rule is date-keyed, not key-keyed: a value that was already true at the
    # moment is part of what the cell should see. (An argument before the grant
    # is the cert-before-judgment shape.)
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(
        fixture_corpus,
        date(2026, 7, 20),
        {**_MERITS_TIMELINE, "date_argued": "2025-12-01"},
    )
    _drop_snapshots_before(fixture_corpus, _GRANT_CUTOFF)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    payload = json.loads(paths.snapshot(_GRANT_CUTOFF.isoformat()).read_text())
    assert payload["date_argued"] == "2025-12-01"


def test_a_point_in_time_docket_keeps_its_top_level_dates(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The field cut is for the reconstructed branch only: a `dated` payload is
    # what the docket really served, and its fields were true when it served it.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(
        fixture_corpus,
        _GRANT_DATE,
        {**_AT_THE_GRANT, "sJsonCreationDate": "2026-01-15"},
    )
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    payload = json.loads(paths.snapshot(_GRANT_DATE.isoformat()).read_text())
    assert payload["sJsonCreationDate"] == "2026-01-15"
    assert _context(fixture_corpus)["snapshot_provenance"] == "dated"


def test_the_placed_path_reports_what_it_removed(fixture_corpus: FixtureCorpus) -> None:
    # The auditable size of the cut, kept out of context.json on purpose: the
    # cell reads that file, and how much a cut removed separates a grant from a
    # denial about as cleanly as the disposing order does.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)
    _drop_snapshots_before(fixture_corpus, _GRANT_CUTOFF)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    # Two of the four entries postdate the grant moment.
    assert "2 entr(ies) and 0 document(s) are outside the moment" in result.output
    assert "postdate" not in _context(fixture_corpus).get("notes", "")


def test_the_interim_application_baseline_is_cut_at_its_arrival(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The other case-level baseline, and it *is* cut — the two are not a class.
    # The cert baseline's opened_at is docketing while its moment is the
    # distribution, so cutting would delete its signal; the interim baseline's
    # declared moment IS arrival, and the same filing date is that moment's own
    # trigger. So the escalation ladder the fixture's application climbed —
    # response requested, referral, an amicus — is exactly what an arrival cell
    # must not be conditioned on, and the frozen trio says so.
    result = runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "306",
            "--event",
            "evt-motion-disposition",
        ],
    )

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 306)
    # The application was filed 2026-06-22; the docket ran on to 2026-07-14.
    payload = json.loads(paths.snapshot("2026-06-23").read_text())
    descriptions = [entry["description"] for entry in payload["docket_entries"]]
    assert len(descriptions) == 1
    assert descriptions[0].startswith("Application (26A11) for a stay")
    context = json.loads(paths.cell_context.read_text())
    assert context["snapshot_provenance"] == "truncated"
    assert context["cutoff"] == "2026-06-23"
    assert context["response_requested"] is False
    assert context["referred_to_court"] is False
    assert context["amicus_briefs"] == 0


def test_a_document_with_no_readable_entry_date_falls_back_to_its_fetch(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The fallback is safe in one direction only: the pipeline cannot fetch a
    # document before it is filed, so a fetch before the cutoff means a filing
    # before it. The reverse does not hold — a backfill fetches an old document
    # late — so a partial date with a late fetch is dropped rather than kept.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind="petition",
                    url="https://example/petition.pdf",
                    # Partial: `cert_signals.entry_date` refuses it rather than
                    # letting today's date fill the missing components in.
                    entry_date="2025",
                    fetched_at=date(2025, 1, 20),
                    text="The petition.",
                ),
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind="questions-presented",
                    url="https://example/qp.pdf",
                    entry_date="",
                    fetched_at=date(2026, 5, 4),
                    text="Whether X.",
                ),
            ],
        )

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert paths.document("petition").read_text() == "The petition.\n"
    assert not paths.document("questions-presented").exists()


def test_the_terminal_gate_reads_a_disposition_the_cut_would_have_hidden(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The ordering the cut depends on: both gates run on the LATEST payload,
    # before the cut. The judgment postdates the moment, so a cell provisioned
    # from the cut docket would look open — and would be forecasting a case that
    # is already over. The refusal writes nothing, cut or no cut.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 1, 14), _AT_THE_GRANT)
    decided = {
        **_MERITS_TIMELINE,
        "docket_entries": [
            *_MERITS_TIMELINE["docket_entries"],
            {
                "id": 5,
                "date_filed": "2026-06-30",
                "description": "Judgment REVERSED and case REMANDED.",
            },
        ],
    }
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), decided)

    result = _provision_cell("--event", "evt-order-judgment", "--refuse-terminal")

    assert result.exit_code == 3
    assert "refusing to provision forward cell" in result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.snapshot("2026-01-14").exists()
    assert not paths.cell_context.exists()


def test_truncation_drops_an_entry_whose_date_cannot_be_read(
    fixture_corpus: FixtureCorpus,
) -> None:
    # Fails closed: an entry with no usable date could be the one that decides
    # the case, and nothing about it says otherwise. That costs a little
    # pre-moment context and cannot leak an outcome, which is the right way
    # round.
    _seed_merits_event(fixture_corpus)
    undated = {
        **_MERITS_TIMELINE,
        "docket_entries": [
            *_MERITS_TIMELINE["docket_entries"][:2],
            {"id": 3, "date_filed": "", "description": "Record received from the Ninth Circuit."},
        ],
    }
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), undated)
    _drop_snapshots_before(fixture_corpus, _GRANT_CUTOFF)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    payload = json.loads(paths.snapshot(_GRANT_CUTOFF.isoformat()).read_text())
    descriptions = [entry["description"] for entry in payload["docket_entries"]]
    assert "Record received from the Ninth Circuit." not in descriptions
    assert _context(fixture_corpus)["snapshot_provenance"] == "truncated"


# --- the interim arrival moment's anchor bound --------------------------------
#
# The interim baseline is the one moment whose trigger is a docket entry rather
# than a day, so its cut carries a second bound the others do not (see
# `fedcourtsai.pipeline.arrival_cut`). These pin what the cell reads and what its
# context records, over both provenances and both modes.

_APPLICATION_SUBMITTED = (
    "Application (26A11) for a stay of the mandate pending the filing and "
    + "disposition of a petition for a writ of certiorari, submitted to The Chief Justice."
)
_SAME_DAY_DENIAL = "Application (26A11) referred to the Court. Application denied by the Court."


def _seed_application_snapshot(
    fixture_corpus: FixtureCorpus, on: date, entries: list[tuple[str, str]]
) -> None:
    """Overlay a snapshot on the fixture's application docket, scotus/306."""
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(
            conn,
            "scotus/306",
            on,
            {
                "docket_number": "26A11",
                "docket_entries": [
                    {"id": index, "date_filed": when, "description": text}
                    for index, (when, text) in enumerate(entries, start=1)
                ],
            },
        )


def _provision_application(*args: str) -> Result:
    return runner.invoke(
        app,
        [
            "provision-snapshot",
            "--court",
            "scotus",
            "--docket",
            "306",
            "--event",
            "evt-motion-disposition",
            *args,
        ],
    )


def _application_context(fixture_corpus: FixtureCorpus) -> dict[str, Any]:
    context: dict[str, Any] = json.loads(
        CasePaths(fixture_corpus.data_root, "scotus", 306).cell_context.read_text()
    )
    return context


def test_an_arrival_cell_records_the_boundary_it_was_cut_at(
    fixture_corpus: FixtureCorpus,
) -> None:
    # `cutoff` alone cannot say where inside the opening day the cell stops, and
    # an artifact byte-identical either side of this change would leave the
    # replay leakage clock reading the looser rule. So the boundary is on the
    # context.
    result = _provision_application()

    assert result.exit_code == 0, result.output
    context = _application_context(fixture_corpus)
    assert context["cut_kind"] == "arrival-position"
    assert context["cut_anchor_index"] == 0
    assert context["cutoff"] == "2026-06-23"


def test_a_moment_with_no_intra_day_tail_records_the_plain_date_rule(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The separability the freeze record rests on: the two conditionings are
    # distinguishable in the artifact rather than pooled behind one date.
    _seed_merits_event(fixture_corpus)
    _seed_snapshot(fixture_corpus, date(2026, 7, 20), _MERITS_TIMELINE)
    _drop_snapshots_before(fixture_corpus, _GRANT_CUTOFF)

    result = _provision_cell("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    context = _context(fixture_corpus)
    assert context["cut_kind"] == "date"
    assert context["cut_anchor_index"] is None


def test_an_uncut_cell_records_no_boundary_at_all(fixture_corpus: FixtureCorpus) -> None:
    result = _provision_cell()

    assert result.exit_code == 0, result.output
    context = _context(fixture_corpus)
    assert context["cut_kind"] is None
    assert context["cut_anchor_index"] is None


def test_a_same_day_disposed_application_is_not_provisioned_its_own_denial(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The shape the defect was measured on: submitted, referred and denied
    # inside the arrival day, so the date rule — which keeps everything filed
    # strictly before the day AFTER the arrival — necessarily admits the denial.
    _seed_application_snapshot(
        fixture_corpus,
        date(2026, 7, 14),
        [
            ("2026-06-22", _APPLICATION_SUBMITTED),
            ("2026-06-22", "Application (26A11) referred to the Court."),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    result = _provision_application()

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 306)
    payload = json.loads(paths.snapshot("2026-06-23").read_text())
    descriptions = [entry["description"] for entry in payload["docket_entries"]]
    assert descriptions == [_APPLICATION_SUBMITTED]
    assert not any("denied" in text.lower() for text in descriptions)


def test_the_anchor_bound_runs_on_a_dated_payload_too(
    fixture_corpus: FixtureCorpus,
) -> None:
    # A `dated` payload is exempt from the DATE rule because the docket really
    # served it — but a snapshot served on the arrival day itself already
    # carries that day's later entries, so the branch that reads a payload
    # unmodified is the one this bound is most needed on.
    _seed_application_snapshot(
        fixture_corpus,
        date(2026, 6, 22),
        [
            ("2026-06-22", _APPLICATION_SUBMITTED),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    result = _provision_application()

    assert result.exit_code == 0, result.output
    context = _application_context(fixture_corpus)
    assert context["snapshot_provenance"] == "dated"
    assert context["cut_kind"] == "arrival-position"
    payload = json.loads(
        CasePaths(fixture_corpus.data_root, "scotus", 306).snapshot("2026-06-22").read_text()
    )
    assert [e["description"] for e in payload["docket_entries"]] == [_APPLICATION_SUBMITTED]


def test_a_replay_arrival_cell_takes_the_same_bound(fixture_corpus: FixtureCorpus) -> None:
    # The bound is a property of the moment, not of the lane: a replay path
    # provisioning one uncut would reconstruct exactly the conditioning the
    # forward path refuses.
    _seed_application_snapshot(
        fixture_corpus,
        date(2026, 7, 14),
        [
            ("2026-06-22", _APPLICATION_SUBMITTED),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    result = _provision_application("--mode", "replay")

    assert result.exit_code == 0, result.output
    context = _application_context(fixture_corpus)
    assert context["mode"] == "replay"
    assert context["cut_kind"] == "arrival-position"


def test_an_unanchorable_arrival_row_refuses_rather_than_taking_the_date_cut(
    fixture_corpus: FixtureCorpus,
) -> None:
    # Never a silent fall back: the date rule is the conditioning the anchor
    # bound replaces, so a cell taking it while its context recorded the tighter
    # one would carry the defect together with a record saying it was fixed.
    _seed_application_snapshot(
        fixture_corpus,
        date(2026, 7, 14),
        [
            ("2026-06-22", "Motion for leave to proceed in forma pauperis filed."),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    result = _provision_application()

    assert result.exit_code == 4, result.output
    assert "could not be anchored" in result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 306)
    # Refused before writing anything: no snapshot, no context.
    assert not paths.cell_context.exists()
    assert not paths.snapshot("2026-06-23").exists()


# --- the ledger: the figures the freeze record cites come from here -----------


def _seed_live(fixture_corpus: FixtureCorpus, entries: list[tuple[str, str]]) -> None:
    """Give the fixture's application docket a live-shaped snapshot to read.

    The ledger reads `latest_live_snapshot`, which skips a REST-shaped payload —
    the fixture's own snapshot is REST-shaped, so a row with no live snapshot is
    the corpus's default state here and has to be overlaid deliberately.
    """
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(
            conn,
            "scotus/306",
            date(2026, 7, 14),
            {
                "CaseNumber": "26A11",
                "ProceedingsandOrder": [{"Date": when, "Text": text} for when, text in entries],
            },
        )


def _ledger(fixture_corpus: FixtureCorpus) -> arrival_cut.ArrivalCutLedger:
    with corpus.connect_readonly(fixture_corpus.db_path, backend="local") as conn:
        return arrival_cut.arrival_cut_ledger(conn, corpus_vintage=date(2026, 9, 5))


def test_the_ledger_counts_a_row_with_no_live_snapshot_apart(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The wrong-blob arm, and the reason it is reported rather than failed: a
    # reading taken without the content store addressed lands the whole
    # population here and still exits 0, so the count is the only signal that
    # separates it from a clean run.
    ledger = _ledger(fixture_corpus)

    assert ledger.rows_seen == 1
    assert ledger.no_snapshot == 1
    assert ledger.anchored == 0
    assert ledger.refused == 0


def test_the_ledger_reads_the_tail_and_the_scope_split(
    fixture_corpus: FixtureCorpus,
) -> None:
    _seed_live(
        fixture_corpus,
        [
            ("2026-06-22", _APPLICATION_SUBMITTED),
            ("2026-06-22", "Response to application (26A11) requested, due July 2, 2026."),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    ledger = _ledger(fixture_corpus)

    assert ledger.no_snapshot == 0
    assert ledger.anchored == 1
    assert ledger.refused == 0
    # The fixture's application is substantive, so it is a row the matrix can
    # actually mint a cell for — the denominator every operational rate uses.
    assert ledger.scope_rows == 1
    assert ledger.kind_counts == {"substantive": 1}
    assert ledger.scope_anchored == 1
    # Two same-day entries sit after the opening entry, one of them the denial.
    assert ledger.tail_rows == 1
    assert ledger.tail_entries == 2
    assert ledger.tail_carries_disposition == 1
    assert ledger.scope_tail_entries == 2
    assert ledger.scope_tail_carries_disposition == 1
    # The response request was in that tail, so its increment claim moves from
    # vacuously masked to resolvable.
    assert ledger.response_requested_unmasked == 1


def test_the_ledger_separates_a_stale_stamp_from_an_unanchorable_docket(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The two refusal causes are different findings and the split is what makes
    # the headline readable: a stamp that disagrees with the docket is corpus
    # convergence state, while a docket naming no submission entry is a property
    # of the case.
    _seed_live(
        fixture_corpus,
        [
            ("2026-06-20", _APPLICATION_SUBMITTED),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    ledger = _ledger(fixture_corpus)

    # `opened_at` is 2026-06-22; the submission entry is dated 2026-06-20.
    assert ledger.refused == 1
    assert ledger.refused_stale_stamp == 1
    assert ledger.refused_no_submission_entry == 0
    assert ledger.anchored == 0


def test_a_docket_naming_no_submission_entry_is_the_other_refusal(
    fixture_corpus: FixtureCorpus,
) -> None:
    _seed_live(
        fixture_corpus,
        [
            ("2026-06-22", "Motion for leave to proceed in forma pauperis filed."),
            ("2026-06-22", _SAME_DAY_DENIAL),
        ],
    )

    ledger = _ledger(fixture_corpus)

    assert ledger.refused == 1
    assert ledger.refused_no_submission_entry == 1
    assert ledger.refused_stale_stamp == 0


def test_the_same_day_read_anchors_on_the_docket_not_the_stamp(
    fixture_corpus: FixtureCorpus,
) -> None:
    # A stale-stamp refusal IS the finding that the stamp names no submission
    # entry, so reading "disposed of on its arrival day" against the stamp would
    # answer a question about a day the application did not arrive on. Here the
    # docket arrived and was denied on 06-20, while the stamp says 06-22: the
    # row refuses, and the same-day flag must still be true.
    _seed_live(
        fixture_corpus,
        [
            ("2026-06-20", _APPLICATION_SUBMITTED),
            ("2026-06-20", _SAME_DAY_DENIAL),
        ],
    )

    ledger = _ledger(fixture_corpus)

    assert ledger.refused_stale_stamp == 1
    assert ledger.refused_same_day_disposition == 1
    assert [row.same_day_disposition for row in ledger.rows] == [True]
