"""The salience activation dry-run check sizes the first pass without writing."""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from fedcourtsai import corpus

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "checks" / "salience_activation_dry_run.py"
)
_CONFERENCE = date(2026, 1, 9)


def _module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location("_check_salience_activation", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def _row(case_id: str, docket: str, writ: str, *, selected: bool = False) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        petitioner_title="John Doe",
        date_filed=date(2025, 10, 1),
        distribution_count=2,
        opening_writ=writ,
        distributed_for_conference=_CONFERENCE,
        salience_selected=selected,
    )


def test_counts_new_picks_standing_latches_and_refused_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module(monkeypatch)
    root = tmp_path / "config"
    root.mkdir()
    (root / "tracking.yaml").write_text("salience:\n  per_conference_capacity: 1\n")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    rows = [
        _row("scotus/1", "25-101", "certiorari"),
        _row("scotus/2", "25-102", "certiorari", selected=True),
        _row("scotus/3", "25-103", "rule-20"),
        _row("scotus/4", "25-104", "rule-20", selected=True),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        conn.execute("UPDATE cases SET salience_version = 'sal-v4' WHERE case_id = 'scotus/4'")
        conn.commit()

    lines = module.render(db, root, date(2026, 1, 2))

    # The standing latches count the latched writ too: it still holds its latch.
    assert "| 2026-01-09 | 1 | 2 |" in lines
    assert "Rows the active segment refuses: 2." in lines
    assert "| no | none | 1 |" in lines
    assert "| yes | sal-v4 | 1 |" in lines
    with corpus.connect(db) as conn:
        untouched = corpus.get_row(conn, "scotus/3")
    assert untouched is not None and untouched.salience_version is None
