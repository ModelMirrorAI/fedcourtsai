"""The interim reading census: what the finer reading names, and that nothing moves.

The census re-reads stored application snapshots under both readings. It must
report the rows the finer reading names partial or moot, by Term, and what the
future map would do to the substantive counts — and write nothing: the stored
labels, the committed outcomes and the corpus file stay byte-identical.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.interim_reading_census import interim_reading_census
from fedcourtsai.pipeline.interim_signals import InterimReading
from fedcourtsai.schemas import Disposition, Outcome, Prediction, PredictionContext
from fedcourtsai.serialize import write_json

_EVENT = "evt-motion-disposition"
_DECIDED = date(2026, 7, 1)


def _row(case_id: str, docket: str, disposition: Disposition, **kwargs: object) -> corpus.CorpusRow:
    fields: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket,
        "case_name": "Marbury Power Cooperative v. Ellison",
        "last_live_polled": date(2026, 8, 1),
        "disposition": disposition,
        "date_decided": _DECIDED,
        "application_kind": "substantive",
        "amicus_briefs": 0,
    }
    fields.update(kwargs)
    return corpus.CorpusRow.model_validate(fields)


def _live(docket: str, order: str) -> dict[str, object]:
    return {
        "ProceedingsandOrder": [
            {"Date": "2026-06-20", "Text": f"Application ({docket}) for a stay, submitted."},
            {"Date": "2026-07-01", "Text": order},
        ]
    }


def _seed(conn: sqlite3.Connection) -> None:
    # Every stored label is the registered reading of its snapshot.
    corpus.upsert_rows(
        conn,
        [
            _row("scotus/700", "26A700", Disposition.denied),  # granted in part and denied in part
            _row("scotus/701", "26A701", Disposition.denied),  # denied as moot
            _row("scotus/702", "26A702", Disposition.dismissed, application_kind="extension"),
            _row("scotus/703", "26A703", Disposition.denied),  # plain denial
            _row("scotus/704", "26A704", Disposition.granted),  # plain grant
            _row("scotus/705", "26A705", Disposition.granted),  # granted insofar as
            _row("scotus/706", "26A706", Disposition.denied),  # no snapshot
            # The registered reading's side-motion misreading, stored as it reads.
            _row("scotus/707", "26A707", Disposition.denied),
            # Resolved, application-parsed, outside the live slice: counted, not re-read.
            _row("scotus/708", "26A708", Disposition.granted, last_live_polled=None),
        ],
    )
    orders = {
        "scotus/700": ("26A700", "Application (26A700) granted in part and denied in part."),
        "scotus/701": ("26A701", "Application (26A701) denied as moot."),
        "scotus/702": ("26A702", "Application (26A702) dismissed as moot."),
        "scotus/703": ("26A703", "Application (26A703) denied."),
        "scotus/704": ("26A704", "Application (26A704) granted."),
        "scotus/705": ("26A705", "The application (26A705) is granted insofar as it seeks a stay."),
        "scotus/707": (
            "26A707",
            "The application (26A707) for a stay is granted, and the motion to expedite is "
            + "denied as moot.",
        ),
    }
    for case_id, (docket, order) in orders.items():
        corpus.upsert_snapshot(conn, case_id, date(2026, 7, 10), _live(docket, order))


def _ledger(data_root: Path) -> Path:
    paths = CasePaths(data_root, "scotus", 701).event(_EVENT)
    write_json(
        paths.outcome,
        Outcome(
            case_id="scotus/701",
            event_id=_EVENT,
            resolved_at=_DECIDED,
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    write_json(
        paths.prediction("claude-baseline", "20260101T000000Z"),
        Prediction(
            case_id="scotus/701",
            event_id=_EVENT,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="20260101T000000Z",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.3,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward", snapshot_date=date(2026, 6, 24), signals_observable=True
            ),
        ),
    )
    return paths.outcome


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def seeded(tmp_path: Path) -> tuple[Path, Path, Path]:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        _seed(conn)
    data_root = tmp_path / "data"
    return db, data_root, _ledger(data_root)


def test_the_census_names_both_forms_and_keeps_the_populations_apart(
    seeded: tuple[Path, Path, Path],
) -> None:
    db, data_root, _ = seeded
    with corpus.connect(db) as conn:
        census = interim_reading_census(conn, data_root)
    assert (census.eligible, census.observable, census.unobservable) == (8, 7, 1)
    assert census.non_live == 1
    # Every stored label is the registered reading of its own snapshot.
    assert census.registered_disagreements == []
    # The registered reading's known misreading is named, not corrected.
    assert census.registered_plain_grant_misreads == ["scotus/707"]
    assert [(r.case_id, r.stored, r.reading, r.same_entry) for r in census.rows] == [
        ("scotus/700", Disposition.denied, InterimReading.granted_in_part, True),
        ("scotus/701", Disposition.denied, InterimReading.dismissed_moot, True),
        ("scotus/702", Disposition.dismissed, InterimReading.dismissed_moot, True),
        ("scotus/705", Disposition.granted, InterimReading.granted_in_part, True),
    ]
    assert census.by_term == {
        "OT2026": {
            "extension": {"dismissed-moot": 1},
            "substantive": {"dismissed-moot": 1, "granted-in-part": 2},
        }
    }
    counts = census.terms["OT2026"]
    # The statpack counts every substantive resolved row: 700, 701, 703-708.
    assert (counts.statpack_resolved, counts.statpack_granted) == (8, 3)
    # The re-read subset leaves out the unobservable 706 and the non-live 708.
    assert (counts.reread_resolved, counts.reread_granted) == (6, 2)
    assert (counts.unobservable, counts.non_live) == (1, 1)
    assert (counts.reread_partial, counts.reread_partial_stored_ungranted) == (2, 1)
    assert counts.reread_moot == 1
    assert [(o.ref, o.recorded, o.reading, o.predictions) for o in census.committed_outcomes] == [
        (f"scotus/701/{_EVENT}", Disposition.denied, InterimReading.dismissed_moot, 1)
    ]
    assert census.stored_labels_written == 0


def test_the_census_statpack_counts_are_the_statpacks_own(
    seeded: tuple[Path, Path, Path],
) -> None:
    """The per-Term statpack counts are the interim section's own, so the census
    reports the base rate's population rather than a lookalike."""
    db, data_root, _ = seeded
    with corpus.connect(db) as conn:
        census = interim_reading_census(conn, data_root)
    interim = analytics.build_statpack(corpus_db_path=db).interim
    assert interim is not None
    assert {
        f"OT{term.term}": (term.substantive_resolved, term.substantive_granted)
        for term in interim.terms
        if term.substantive_resolved
    } == {
        term: (counts.statpack_resolved, counts.statpack_granted)
        for term, counts in census.terms.items()
        if counts.statpack_resolved
    }


def test_the_census_writes_nothing(seeded: tuple[Path, Path, Path]) -> None:
    """The scored and cell-facing view is the stored one, and it stays byte-identical."""
    db, data_root, outcome = seeded
    before = (_digest(db), _digest(outcome))
    with corpus.connect(db) as conn:
        stored_before = [row.model_dump_json() for row in corpus.iter_rows(conn)]
        interim_reading_census(conn, data_root)
        stored_after = [row.model_dump_json() for row in corpus.iter_rows(conn)]
    assert stored_after == stored_before
    assert (_digest(db), _digest(outcome)) == before


def test_the_command_prints_the_census(
    seeded: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    db, data_root, _ = seeded
    assert corpus.corpus_db_path(db.parent) == db
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(db.parent))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")
    result = CliRunner().invoke(app, ["interim-reading-census"])
    assert result.exit_code == 0, result.output
    census = json.loads(result.stdout.strip().splitlines()[-1])
    assert len(census["rows"]) == 4
    assert census["registered_plain_grant_misreads"] == ["scotus/707"]
    assert census["stored_labels_written"] == 0
