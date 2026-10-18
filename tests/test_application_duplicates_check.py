"""The application-duplicates corpus check: it runs, agrees with the statpack, reports no text.

`scripts/checks/application_duplicates.py` posts its summary to a public PR
comment, so beside the figures these tests hold it to counts, identifiers,
field names and labels: a caption stored on a twin never reaches the summary.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "checks" / "application_duplicates.py"
_CAPTION = "Marbury Power Cooperative v. Ellison"


def _module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location("_census_check_application_duplicates", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def _row(case_id: str, docket: str, **kwargs: object) -> corpus.CorpusRow:
    fields: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket,
        "case_name": _CAPTION,
        "application_kind": "substantive",
        "last_live_polled": date(2026, 8, 1),
    }
    fields.update(kwargs)
    return corpus.CorpusRow.model_validate(fields)


def _seed(db: Path) -> None:
    granted = {"disposition": Disposition.granted}
    denied = {"disposition": Disposition.denied}
    rows = [_row(f"scotus/{100 + i}", f"24A{i}", **denied) for i in range(1, 61)]
    rows += [
        _row("scotus/500", "24A910", **granted),
        _row("scotus/900", "24A910", case_name="Another caption entirely", **granted),
        # A stub with the lower id beside the parsed row: the parsed row counts.
        _row("scotus/50", "24A931", application_kind=None, last_live_polled=None),
        _row("scotus/950", "24A931", **granted),
        _row("scotus/700", "25A1", **denied),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


def test_the_census_counts_each_number_once_and_reports_no_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    check = _module(monkeypatch)
    db = tmp_path / "corpus.db"
    _seed(db)
    lines = check._census(db, tmp_path / "data", 10)
    text = "\n".join(lines)
    assert "duplicated numbers: 2; rows the dedupe skips: 2" in text
    assert "| 24A910 | scotus/500, scotus/900 |" in text
    assert "| 24A931 | scotus/950, scotus/50 |" in text
    assert "groups counting an unobserved row while skipping an observed one: 0" in text
    assert "groups whose counted row is not the plain lowest docket id: 1" in text
    assert "`build_statpack`'s interim section equals the one-row-per-number counts: True" in text
    # OT2024 resolves 63 rows (60 denials, three grant rows) but 62 numbers: the
    # twice-stored 24A910 counts once, and the 24A931 stub carries no disposition.
    assert "OT2025 application cells: 3/63 = 0.0476 -> 2/62 = 0.0323" in text
    assert _CAPTION not in text and "Another caption" not in text


def test_the_census_reports_an_empty_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    check = _module(monkeypatch)
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/1", "24-1", application_kind=None)])
    lines = check._census(db, tmp_path / "data", 10)
    assert lines[-1] == "- the corpus holds no strict-form application rows"


def test_a_failing_corpus_info_fails_the_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    check = _module(monkeypatch)
    _seed(tmp_path / "corpus.db")
    settings = SimpleNamespace(
        corpus_root=tmp_path,
        data_root=tmp_path / "data",
        config_root=Path(__file__).resolve().parents[1] / "config",
    )
    monkeypatch.setattr(check, "get_settings", lambda: settings)
    monkeypatch.setattr(check, "_git_head", lambda _path: "unknown")
    monkeypatch.setattr(
        check.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, stdout="", stderr="boom\n"),
    )
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("CHECK_SUMMARY", str(summary))
    assert check.main() == 1
    assert "duplicated numbers: 2" in summary.read_text()
