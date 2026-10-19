"""The published schedule (``fedcourts schedule`` / :mod:`fedcourtsai.schedule`)."""

from __future__ import annotations

import ast
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import fedcourtsai.cli as cli_module
from fedcourtsai import corpus
from fedcourtsai import schedule as schedule_module
from fedcourtsai.pipeline.live import LiveDiscovery
from fedcourtsai.pipeline.pull import PullQueues
from fedcourtsai.schedule import build_schedule, schedule_path
from fedcourtsai.schemas import FILENAME_MODELS, Disposition, Schedule, ScheduleEntry
from fedcourtsai.serialize import read_model, write_json

_AS_OF = date(2026, 10, 19)
_SRC = Path(cli_module.__file__).parent


def _make_case_dir(data_root: Path, case_id: str) -> None:
    court, _, docket = case_id.partition("/")
    (data_root / "cases" / court / docket).mkdir(parents=True, exist_ok=True)


def _seed(tmp_path: Path, rows: list[corpus.CorpusRow], public: list[str]) -> tuple[Path, Path]:
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    for case_id in public:
        _make_case_dir(data_root, case_id)
    return data_root, db


def _row(case_id: str, **fields: Any) -> corpus.CorpusRow:
    return corpus.CorpusRow(case_id=case_id, court="scotus", docket_number="26-1", **fields)


def test_skipped_when_corpus_absent(tmp_path: Path) -> None:
    built = build_schedule(
        data_root=tmp_path / "data",
        corpus_db_path=corpus.corpus_db_path(tmp_path / "corpus"),
        as_of=_AS_OF,
    )
    assert built == Schedule(skipped=True)


def test_lists_only_pending_distributed_public_dockets(tmp_path: Path) -> None:
    conference = date(2026, 10, 30)
    data_root, db = _seed(
        tmp_path,
        [
            _row(
                "scotus/2",
                distributed_for_conference=conference,
                last_live_polled=date(2026, 10, 18),
            ),
            # Never distributed.
            _row("scotus/3"),
            # Decided: cert denied, and a disposition with no date yet.
            _row(
                "scotus/4",
                distributed_for_conference=conference,
                date_cert_denied=date(2026, 10, 13),
            ),
            _row("scotus/5", distributed_for_conference=conference, disposition=Disposition.denied),
            # Distributed but not public: never enumerated from the corpus.
            _row("scotus/9999", distributed_for_conference=conference),
        ],
        public=["scotus/2", "scotus/3", "scotus/4", "scotus/5"],
    )
    built = build_schedule(data_root=data_root, corpus_db_path=db, as_of=_AS_OF)
    assert built.as_of == _AS_OF
    assert built.entries == [
        ScheduleEntry(
            case_id="scotus/2",
            next_conference=conference,
            distributed_for_conference=conference,
            last_live_polled=date(2026, 10, 18),
        )
    ]


def test_a_passed_conference_is_never_published_as_upcoming(tmp_path: Path) -> None:
    data_root, db = _seed(
        tmp_path,
        [
            _row("scotus/2", distributed_for_conference=date(2026, 10, 10)),
            # The conference day itself is still upcoming.
            _row("scotus/3", distributed_for_conference=_AS_OF),
        ],
        public=["scotus/2", "scotus/3"],
    )
    built = build_schedule(data_root=data_root, corpus_db_path=db, as_of=_AS_OF)
    passed, today = built.entries
    assert (passed.next_conference, passed.stale_reason) == (None, "conference_passed")
    assert passed.distributed_for_conference == date(2026, 10, 10)
    assert (today.next_conference, today.stale_reason) == (_AS_OF, None)


def test_an_entry_is_scheduled_or_says_why_not() -> None:
    with pytest.raises(ValueError, match="stale_reason"):
        ScheduleEntry(case_id="scotus/2", next_conference=None, distributed_for_conference=_AS_OF)
    with pytest.raises(ValueError, match="stale_reason"):
        ScheduleEntry(
            case_id="scotus/2",
            next_conference=_AS_OF,
            distributed_for_conference=_AS_OF,
            stale_reason="conference_passed",
        )


def test_cli_schedule_writes_and_a_skipped_build_leaves_the_committed_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_root, _ = _seed(
        tmp_path,
        [_row("scotus/2", distributed_for_conference=date(2999, 1, 1))],
        public=["scotus/2"],
    )
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = CliRunner().invoke(cli_module.app, ["schedule"])
    assert result.exit_code == 0, result.output
    written = read_model(schedule_path(data_root), Schedule)
    assert [entry.next_conference for entry in written.entries] == [date(2999, 1, 1)]

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = CliRunner().invoke(cli_module.app, ["schedule"])
    assert result.exit_code == 0, result.output
    assert "skipped" in result.output
    assert read_model(schedule_path(data_root), Schedule) == written


def test_live_poll_writes_the_schedule_after_its_cycle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_root, _ = _seed(
        tmp_path,
        [_row("scotus/2", distributed_for_conference=date(2999, 1, 1))],
        public=["scotus/2"],
    )
    monkeypatch.setattr(
        cli_module, "live_poll_all", lambda *a, **k: (PullQueues(), LiveDiscovery())
    )
    monkeypatch.setattr(cli_module, "evaluate_backlog", lambda *a, **k: None)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = CliRunner().invoke(
        cli_module.app,
        [
            "live-poll",
            *("--out", str(tmp_path / "p.json")),
            *("--evaluate-out", str(tmp_path / "e.json")),
            *("--unrecorded-out", str(tmp_path / "u.json")),
        ],
    )
    assert result.exit_code == 0, result.output
    assert [e.case_id for e in read_model(schedule_path(data_root), Schedule).entries] == [
        "scotus/2"
    ]


def test_a_schedule_failure_never_fails_the_live_cycle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _broken(**kwargs: Any) -> Schedule:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        cli_module, "live_poll_all", lambda *a, **k: (PullQueues(), LiveDiscovery())
    )
    monkeypatch.setattr(cli_module, "evaluate_backlog", lambda *a, **k: None)
    monkeypatch.setattr(schedule_module, "build_schedule", _broken)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = CliRunner().invoke(
        cli_module.app,
        [
            "live-poll",
            *("--out", str(tmp_path / "p.json")),
            *("--evaluate-out", str(tmp_path / "e.json")),
            *("--unrecorded-out", str(tmp_path / "u.json")),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "p.json").exists()
    assert not schedule_path(tmp_path / "data").exists()


#: The modules that build what a predict or evaluate cell is handed. A scheduled
#: date is public, but feeding it to a cell would change what the cell sees,
#: which is a process decision and not a side effect of publishing it.
_PROVISIONING_MODULES = (
    "provision.py",
    "blinding.py",
    "pipeline/cell_context.py",
    "pipeline/predict.py",
    "pipeline/evaluate.py",
    "pipeline/prefetch.py",
)


@pytest.mark.parametrize("module", _PROVISIONING_MODULES)
def test_no_provisioning_module_reads_the_schedule(module: str) -> None:
    source = (_SRC / module).read_text()
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    } | {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not imported & {"schedule", ".schedule", "schedule_path", "Schedule"}
    assert "schedule.json" not in source
    assert '"schedule"' not in source


def test_the_schedule_validates_under_its_filename(tmp_path: Path) -> None:
    assert FILENAME_MODELS[schedule_path(tmp_path).name] is Schedule
    write_json(schedule_path(tmp_path), Schedule(as_of=_AS_OF))
    assert read_model(schedule_path(tmp_path), Schedule).as_of == _AS_OF
