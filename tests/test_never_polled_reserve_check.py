"""The never-polled reserve corpus check counts what the reserve would take, by Term and stream."""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from fedcourtsai import corpus

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "checks" / "never_polled_reserve.py"


def _module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location("_check_never_polled_reserve", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def _open_petition(case_id: str) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id="evt-petition-disposition",
        case_id=case_id,
        court="scotus",
        kind="petition",
        title=case_id,
    )


def test_counts_qualifying_rows_by_term_and_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module(monkeypatch)
    db = tmp_path / "corpus.db"
    rows = [
        corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="17-100"),
        corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="17-5100"),
        corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="18-5200"),
        # Polled, decided, below the floor, or a duplicate above a lower id:
        # none of these is the reserve's.
        corpus.CorpusRow(
            case_id="scotus/4",
            court="scotus",
            docket_number="18-300",
            last_live_polled=date(2026, 10, 1),
        ),
        corpus.CorpusRow(
            case_id="scotus/5", court="scotus", docket_number="18-400", disposition="denied"
        ),
        corpus.CorpusRow(case_id="scotus/6", court="scotus", docket_number="16-500"),
        corpus.CorpusRow(case_id="scotus/33", court="scotus", docket_number="18-5200"),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_events(conn, [_open_petition(row.case_id) for row in rows])
    counts = module.backlog(db)
    assert counts == {(2017, "paid"): 1, (2017, "ifp"): 1, (2018, "ifp"): 1}
    table = module.render(counts)
    assert "| OT2017 | 1 | 1 | 0 |" in table
    assert "| OT2018 | 0 | 1 | 0 |" in table
    assert table[-1] == "\nTotal: 3"
