"""The merits-event backfill: population, mint, guards, idempotency, moments."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import corpus, store
from fedcourtsai.cli import app
from fedcourtsai.merits_event_migration import (
    BRIEFED_MERITS_EVENT_ID,
    backfill_event_moments,
    backfill_merits_events,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID
from fedcourtsai.schemas import EventKind, MeritsTermination

runner = CliRunner()

_GRANTED = "scotus/910001"  # granted, pending merits — the population
_BRIEFED = "scotus/910002"  # granted, pending, respondent's merits brief latched
_DECIDED = "scotus/910003"  # granted, judgment latched — forward-only, left alone
_GVR = "scotus/910004"  # a grant that decides in the cert order; never mints
_APPLICATION = "scotus/910005"  # a granted application; never enters the merits docket

_GRANT_DATE = date(2026, 1, 12)
_BRIEF_DATE = date(2026, 4, 3)


def _row(case_id: str, docket_number: str, **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket_number,
        "case_name": "Petitioner v. Respondent",
        "date_filed": date(2025, 8, 1),
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def _granted(case_id: str, docket_number: str, **kw: object) -> corpus.CorpusRow:
    return _row(
        case_id,
        docket_number,
        disposition="granted",
        date_cert_granted=_GRANT_DATE,
        **kw,
    )


def _pending_payload(*extra_entries: tuple[str, str]) -> dict[str, Any]:
    """A granted-but-pending live snapshot: the shape the pendency guard admits."""
    entries = [
        ("Jan 12 2026", "Petition GRANTED."),
        ("Apr 22 2026", "Argued. For petitioner: X."),
        *extra_entries,
    ]
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


@contextmanager
def _seeded(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """Latched grants in every population shape, none carrying a merits event."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _granted(_GRANTED, "25-100"),
                _granted(_BRIEFED, "25-101", merits_brief_filed=_BRIEF_DATE),
                _granted(
                    _DECIDED,
                    "25-102",
                    merits_judgment="affirmed",
                    merits_decided=date(2026, 6, 20),
                ),
                _row(_GVR, "25-103", disposition="gvr", date_cert_granted=_GRANT_DATE),
                _row(_APPLICATION, "25A155", disposition="granted"),
            ],
        )
        # Pending-shaped snapshots for the mintable cases: the pendency guard
        # requires a stored snapshot whose judgment scan is clean.
        for case_id in (_GRANTED, _BRIEFED):
            corpus.upsert_snapshot(conn, case_id, date(2026, 4, 22), _pending_payload())
        yield conn


def _data_root(tmp_path: Path) -> Path:
    return tmp_path / "data"


def test_dry_run_reports_and_writes_nothing(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=False)
        assert result.applied is False
        assert result.minted == [
            (_GRANTED, MERITS_EVENT_ID),
            (_BRIEFED, MERITS_EVENT_ID),
            (_BRIEFED, BRIEFED_MERITS_EVENT_ID),
        ]
        assert result.already_present == 0
        assert result.decided == 1
        assert result.skipped == []
        for case_id in (_GRANTED, _BRIEFED):
            assert corpus.events_for_case(conn, case_id) == []
    assert not _data_root(tmp_path).exists()


def test_apply_mints_the_grant_event_with_its_stamps(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        assert result.applied is True
        (event,) = corpus.events_for_case(conn, _GRANTED)
    assert event.event_id == MERITS_EVENT_ID
    assert EventKind(event.kind) == EventKind.order
    assert event.stage == "merits"
    assert event.moment == "grant"
    assert event.opened_at == _GRANT_DATE
    assert event.decision_target == "judgment"
    assert event.docket_entry_id is None
    assert event.resolved is False
    assert event.title == "Petitioner v. Respondent"
    ledger = CasePaths(_data_root(tmp_path), "scotus", 910001).event(MERITS_EVENT_ID).event_file
    stamped = yaml.safe_load(ledger.read_text())
    assert stamped["event_id"] == MERITS_EVENT_ID
    assert stamped["stage"] == "merits"
    assert stamped["moment"] == "grant"
    assert stamped["resolved"] is False


def test_apply_mints_the_briefed_moment_where_the_brief_is_latched(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = {e.event_id: e for e in corpus.events_for_case(conn, _BRIEFED)}
    assert set(events) == {MERITS_EVENT_ID, BRIEFED_MERITS_EVENT_ID}
    briefed = events[BRIEFED_MERITS_EVENT_ID]
    assert EventKind(briefed.kind) == EventKind.brief
    assert briefed.stage == "merits"
    assert briefed.moment == "briefed"
    assert briefed.opened_at == _BRIEF_DATE
    assert briefed.resolved is False
    ledger = (
        CasePaths(_data_root(tmp_path), "scotus", 910002).event(BRIEFED_MERITS_EVENT_ID).event_file
    )
    assert ledger.exists()


def test_second_apply_is_a_noop(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        first = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        second = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _GRANTED)
    assert len(first.minted) == 3
    assert second.minted == []
    assert second.already_present == 2
    assert second.skipped == []
    assert [e.event_id for e in events] == [MERITS_EVENT_ID]


def test_decided_grant_is_left_alone(tmp_path: Path) -> None:
    # Forward-only, per the population choice: a latched judgment leaves
    # nothing to forecast, so the docket gets no event and no triage entry.
    with _seeded(tmp_path) as conn:
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _DECIDED)
    assert result.decided == 1
    assert events == []
    assert all(case_id != _DECIDED for case_id, _ in result.minted)
    assert all(case_id != _DECIDED for case_id, _ in result.skipped)


def test_gvr_never_mints(tmp_path: Path) -> None:
    # A GVR's disposition rides in the cert order itself —
    # `opens_merits_proceeding` refuses it, so it is outside the population.
    with _seeded(tmp_path) as conn:
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _GVR)
    assert events == []
    assert all(case_id != _GVR for case_id, _ in result.minted)


def test_application_never_mints(tmp_path: Path) -> None:
    # A granted application ends at the order; its ingest branch nulls
    # `date_cert_granted`, so `opens_merits_proceeding` refuses it.
    with _seeded(tmp_path) as conn:
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _APPLICATION)
    assert events == []
    assert all(case_id != _APPLICATION for case_id, _ in result.minted)


def test_minted_event_is_forecastable(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        assert store.forecastable_event_ids(conn, "scotus", 910001) == [MERITS_EVENT_ID]


def test_existing_grant_event_counts_already_present(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MERITS_EVENT_ID,
                    case_id=_GRANTED,
                    court="scotus",
                    kind=EventKind.order,
                    stage="merits",
                    title="already minted",
                    decision_target="judgment",
                    opened_at=_GRANT_DATE,
                )
            ],
        )
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _GRANTED)
    assert result.already_present == 1
    assert all(case_id != _GRANTED for case_id, _ in result.minted)
    assert event.title == "already minted"  # untouched


def _open_grant_event(case_id: str, **kw: object) -> corpus.CorpusEvent:
    """An already-minted, un-pinned open grant event, as the live mint writes it."""
    base: dict[str, object] = {
        "event_id": MERITS_EVENT_ID,
        "case_id": case_id,
        "court": "scotus",
        "kind": EventKind.order,
        "stage": "merits",
        "moment": "grant",
        "title": "already minted",
        "decision_target": "judgment",
        "opened_at": _GRANT_DATE,
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


def test_grant_present_brief_latched_mints_only_the_briefed_moment(tmp_path: Path) -> None:
    # The brief can latch after the grant event was minted (by the live path or
    # an earlier run of this sweep); the case is then owed just the briefed
    # moment, not counted converged.
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(conn, [_open_grant_event(_BRIEFED)])
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = {e.event_id: e for e in corpus.events_for_case(conn, _BRIEFED)}
    assert (_BRIEFED, BRIEFED_MERITS_EVENT_ID) in result.minted
    assert (_BRIEFED, MERITS_EVENT_ID) not in result.minted
    assert set(events) == {MERITS_EVENT_ID, BRIEFED_MERITS_EVENT_ID}
    assert events[MERITS_EVENT_ID].title == "already minted"  # untouched
    assert events[BRIEFED_MERITS_EVENT_ID].opened_at == _BRIEF_DATE


def test_resolved_grant_event_counts_converged(tmp_path: Path) -> None:
    # A resolved grant event means the merits question is closed, so nothing is
    # owed — even with the brief latched and no judgment column stamped.
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(conn, [_open_grant_event(_BRIEFED, resolved=True)])
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _BRIEFED)
    assert all(case_id != _BRIEFED for case_id, _ in result.minted)
    assert all(case_id != _BRIEFED for case_id, _ in result.skipped)
    assert [e.event_id for e in events] == [MERITS_EVENT_ID]


def test_entry_pinned_briefed_row_blocks_the_whole_case(tmp_path: Path) -> None:
    # A conflicting briefed target withholds the grant event too: minting it
    # beside the conflict would hand triage a half-minted stage.
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=BRIEFED_MERITS_EVENT_ID,
                    case_id=_BRIEFED,
                    court="scotus",
                    kind=EventKind.brief,
                    title="entry-pinned brief",
                    docket_entry_id=11,
                )
            ],
        )
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _BRIEFED)
    assert all(case_id != _BRIEFED for case_id, _ in result.minted)
    ((skipped_case, reason),) = result.skipped
    assert skipped_case == _BRIEFED
    assert BRIEFED_MERITS_EVENT_ID in reason
    assert "entry-pinned" in reason
    assert [e.event_id for e in events] == [BRIEFED_MERITS_EVENT_ID]  # untouched


def test_entry_pinned_grant_row_blocks_the_mint(tmp_path: Path) -> None:
    # An evt-order-judgment row pinned to a docket entry is some filing's
    # event, not the grant moment — minting onto it would latch another
    # filing's state onto the forecast. Skip and report.
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MERITS_EVENT_ID,
                    case_id=_GRANTED,
                    court="scotus",
                    kind=EventKind.order,
                    title="entry-pinned order",
                    docket_entry_id=7,
                )
            ],
        )
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _GRANTED)
    assert all(case_id != _GRANTED for case_id, _ in result.minted)
    ((skipped_case, reason),) = result.skipped
    assert skipped_case == _GRANTED
    assert "entry-pinned" in reason
    assert event.title == "entry-pinned order"  # untouched
    assert event.moment is None


def test_committed_ledger_artifacts_block_the_mint(tmp_path: Path) -> None:
    # A ledger directory under the target id with no corpus row behind it holds
    # artifacts this mint would silently adopt. Skip and report.
    data_root = _data_root(tmp_path)
    ledger_dir = CasePaths(data_root, "scotus", 910001).event(MERITS_EVENT_ID).base
    ledger_dir.mkdir(parents=True)
    with _seeded(tmp_path) as conn:
        result = backfill_merits_events(conn, data_root, apply=True)
        events = corpus.events_for_case(conn, _GRANTED)
    assert events == []
    ((skipped_case, reason),) = result.skipped
    assert skipped_case == _GRANTED
    assert "ledger" in reason


def test_no_snapshot_blocks_the_mint(tmp_path: Path) -> None:
    # A null merits_judgment means unlatched, not pending: with no stored
    # snapshot the docket may be decided, and a snapshot-less forward cell
    # would defeat the provisioning guard. Skip and report.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _GRANTED)
    assert events == []
    assert result.minted == []
    ((skipped_case, reason),) = result.skipped
    assert skipped_case == _GRANTED
    assert "no stored snapshot" in reason


def test_unparsed_judgment_signal_blocks_the_mint(tmp_path: Path) -> None:
    # The judgment sweep's no_match residue: judgment language the deterministic
    # parser missed but the high-recall scan reads ("Judgment issued.") leaves
    # merits_judgment null on a possibly-decided docket. Skip and report.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        corpus.upsert_snapshot(
            conn,
            _GRANTED,
            date(2026, 7, 30),
            _pending_payload(("Jul 30 2026", "Judgment issued.")),
        )
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _GRANTED)
    assert events == []
    assert result.minted == []
    ((skipped_case, reason),) = result.skipped
    assert skipped_case == _GRANTED
    assert "possibly decided" in reason


def test_a_post_grant_rule_46_dismissal_blocks_the_mint(tmp_path: Path) -> None:
    # The residue shape the disposition scan has no branch for: a granted case
    # voluntarily dismissed under Rule 46 ends with no disposition at all, so
    # the high-recall merits scan has to read the termination vocabulary or the
    # docket mints a forward event on a closed proceeding.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        corpus.upsert_snapshot(
            conn,
            _GRANTED,
            date(2026, 8, 11),
            _pending_payload(("Aug 11 2026", "Case Dismissed - Rule 46.")),
        )
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _GRANTED)
    assert events == []
    ((skipped_case, reason),) = result.skipped
    assert skipped_case == _GRANTED
    assert "possibly decided" in reason


def test_a_recorded_termination_leaves_the_row_alone(tmp_path: Path) -> None:
    # Once the sweep has recorded the termination the row is decided for the
    # mint's purposes, exactly as a latched judgment is — the population is
    # forward-only, and there is nothing left to forecast.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        corpus.upsert_snapshot(conn, _GRANTED, date(2026, 4, 22), _pending_payload())
        corpus.set_merits_termination(conn, _GRANTED, MeritsTermination.voluntary_dismissal)
        result = backfill_merits_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _GRANTED)
    assert events == []
    assert result.minted == [] and result.skipped == []
    assert result.decided == 1


def test_backfill_event_moments_stamps_and_converges(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        corpus.upsert_events(
            conn,
            [
                # A stage-carrying row missing its moment: the stamp target.
                corpus.CorpusEvent(
                    event_id=MERITS_EVENT_ID,
                    case_id=_GRANTED,
                    court="scotus",
                    kind=EventKind.order,
                    stage="merits",
                    title="t",
                ),
                # A cert-staged baseline missing its moment: stamped too.
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=_GRANTED,
                    court="scotus",
                    kind=EventKind.petition,
                    stage="cert",
                    title="t",
                ),
                # A stage-less event: no stage, no first moment, never touched.
                corpus.CorpusEvent(
                    event_id="evt-motion-stay",
                    case_id=_GRANTED,
                    court="scotus",
                    kind=EventKind.motion,
                    title="t",
                    docket_entry_id=3,
                ),
            ],
        )
        dry = backfill_event_moments(conn, apply=False)
        assert dry.applied is False
        assert dry.stamped == {"cert": 1, "merits": 1}
        events = {e.event_id: e for e in corpus.events_for_case(conn, _GRANTED)}
        assert events[MERITS_EVENT_ID].moment is None  # dry run wrote nothing

        applied = backfill_event_moments(conn, apply=True)
        assert applied.stamped == {"cert": 1, "merits": 1}
        events = {e.event_id: e for e in corpus.events_for_case(conn, _GRANTED)}
        assert events[MERITS_EVENT_ID].moment == "grant"
        assert events["evt-petition-disposition"].moment == "distribution"
        assert events["evt-motion-stay"].moment is None

        again = backfill_event_moments(conn, apply=True)
        assert again.stamped == {}


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        corpus.upsert_snapshot(conn, _GRANTED, date(2026, 4, 22), _pending_payload())
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))

    result = runner.invoke(app, ["backfill-merits-events"])
    assert result.exit_code == 0, result.output
    assert "dry-run" in result.output
    assert "would mint 1 merits event(s) on 1 case(s)" in result.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        assert corpus.events_for_case(conn, _GRANTED) == []

    applied = runner.invoke(app, ["backfill-merits-events", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "applied" in applied.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _GRANTED)
        assert event.event_id == MERITS_EVENT_ID


def test_cli_backfill_event_moments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, [_granted(_GRANTED, "25-100")])
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MERITS_EVENT_ID,
                    case_id=_GRANTED,
                    court="scotus",
                    kind=EventKind.order,
                    stage="merits",
                    title="t",
                )
            ],
        )
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))

    result = runner.invoke(app, ["backfill-event-moments"])
    assert result.exit_code == 0, result.output
    assert "would stamp 1 event row(s)" in result.output

    applied = runner.invoke(app, ["backfill-event-moments", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "stamped 1 event row(s)" in applied.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _GRANTED)
        assert event.moment == "grant"


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    assert runner.invoke(app, ["backfill-merits-events"]).exit_code == 1
    assert runner.invoke(app, ["backfill-event-moments"]).exit_code == 1
