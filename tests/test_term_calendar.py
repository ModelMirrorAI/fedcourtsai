"""The Court's conference calendar (``fedcourts term-calendar``)."""

from __future__ import annotations

import ast
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import fedcourtsai.cli as cli_module
from fedcourtsai import corpus
from fedcourtsai import term_calendar as tc
from fedcourtsai.pipeline.live import LiveDiscovery
from fedcourtsai.pipeline.pull import PullQueues
from fedcourtsai.schedule import build_schedule
from fedcourtsai.schemas import FILENAME_MODELS, Schedule, TermCalendar
from fedcourtsai.serialize import read_model

_SRC = Path(cli_module.__file__).parent
_MONTHS = tc._MONTHS
_DASH = "\u2013"


def _spell(day: date) -> str:
    return f"{_MONTHS[day.month - 1]} {day.day}, {day.year}"


def _schedule_text(term: int, *, extra: str = "", title_term: int | None = None) -> str:
    """A schedule's text layer as the extractor serves it, stray spaces and all."""
    long_conference = date(term, 9, 28)
    lines = [
        f"CASE DISTRIBUTION SCHEDULE {_DASH} OCTOBER TERM {title_term or term} ",
        "DISTRIBUTION DATE LIST  CONFERENCE ",
        # The extractor splits words and numbers; the grammar reads past it.
        f"SE PTEMBER 2, {term} SUMMER LIST 23 (PAID) SE PTEMBER 28, 20 {str(term)[2:]}",
        f"{_spell(date(term, 9, 18))} LIST 27    {_spell(long_conference)} ",
    ]
    conference = date(term, 10, 9)
    for week in range(45):
        conference_day = conference + timedelta(weeks=week)
        paper = "PAID" if week % 2 == 0 else "IFP"
        lines.append(
            f"{_spell(conference_day - timedelta(days=16))} LI ST {week % 7 + 1} ({paper}) "
            f"{_spell(conference_day)} "
        )
        if week % 10 == 9:
            lines += ["7 ", " ", "DISTRIBUTION DATE LIST  CONFERENCE "]
    lines.append(f"JUNE 16, {term + 1} SUMMER LIST 1 (PAID) ")
    if extra:
        lines.append(extra)
    return "\n".join(lines)


class _Fetcher:
    """The live client's document fetch over canned bodies, keyed by URL."""

    def __init__(self, bodies: dict[int, str | None]) -> None:
        self.bodies = bodies
        self.urls: list[str] = []

    def get_document(self, url: str) -> bytes | None:
        self.urls.append(url)
        for term, body in self.bodies.items():
            if url == tc.SCHEDULE_URL.format(term=term):
                return None if body is None else body.encode()
        return None


def _text(data: bytes) -> str:
    return data.decode()


def test_a_schedule_reads_every_row_through_split_words() -> None:
    rows = tc.parse_schedule(_schedule_text(2026), term=2026)
    assert len(rows) == 48
    assert rows[0].list_name == "SUMMER LIST 23 (PAID)"
    assert rows[0].conference == date(2026, 9, 28)
    assert rows[1].list_name == "LIST 27"
    assert rows[2].list_name == "LIST 1 (PAID)"
    assert rows[-1].list_name == "SUMMER LIST 1 (PAID)"
    assert rows[-1].conference is None


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (_schedule_text(2026, extra="* Conference moved; see order"), "unrecognised line"),
        (_schedule_text(2026, title_term=2025), "titled OT2025"),
        (_schedule_text(2026).replace("CASE DISTRIBUTION SCHEDULE", "SCHEDULE"), "unrecognised"),
        (_schedule_text(2026, extra="JUNE 1, 2027 LIST 3 "), "no conference"),
        (_schedule_text(2026, extra="JUNE 1, 2027 LIST 3 MAY 1, 2027"), "distributed"),
        (_schedule_text(2026, extra="JUNE 1, 2027 LIST 3 OCTOBER 4, 2027"), "outside OT2026"),
        (
            _schedule_text(2026, extra="JULY 1, 2027 SUMMER LIST 2 (IFP) SEPTEMBER 27, 2027"),
            r"2 conference\(s\) take summer lists",
        ),
        (_schedule_text(2026, extra="FEBRUARY 30, 2027 LIST 3 MARCH 4, 2027"), "not a date"),
        (
            f"CASE DISTRIBUTION SCHEDULE {_DASH} OCTOBER TERM 2026\n"
            + "OCTOBER 5, 2026 LIST 5 OCTOBER 9, 2026",
            "fewer",
        ),
        ("", "no OT2026 title"),
    ],
)
def test_a_schedule_that_does_not_parse_whole_is_refused(text: str, reason: str) -> None:
    with pytest.raises(tc.CalendarRefused, match=reason):
        tc.parse_schedule(text, term=2026)


def test_the_calendar_reads_both_terms_and_marks_each_long_conference() -> None:
    fetcher = _Fetcher({2026: _schedule_text(2026), 2027: _schedule_text(2027)})
    calendar = tc.build_calendar(fetcher, today=date(2026, 11, 9), extract=_text)
    assert [s.term for s in calendar.sources] == [2026, 2027]
    longs = [s for s in calendar.sessions if s.long_conference]
    assert [(s.day, s.term) for s in longs] == [
        (date(2026, 9, 28), 2026),
        (date(2027, 9, 28), 2027),
    ]
    assert all(s.kind == "conference" for s in calendar.sessions)
    assert len(calendar.distributions) == 96
    assert tc.next_conference(calendar, date(2026, 11, 9)) == date(2026, 11, 13)


def test_an_unpublished_next_term_is_not_a_failure() -> None:
    fetcher = _Fetcher({2026: _schedule_text(2026)})
    calendar = tc.build_calendar(fetcher, today=date(2026, 11, 9), extract=_text)
    assert [s.term for s in calendar.sources] == [2026]


def test_the_term_is_the_october_term_today_falls_in() -> None:
    # Before October the current schedule is the outgoing Term's, and the
    # incoming Term's (with its late-September long conference) is the next.
    fetcher = _Fetcher({2025: _schedule_text(2025), 2026: _schedule_text(2026)})
    calendar = tc.build_calendar(fetcher, today=date(2026, 9, 1), extract=_text)
    assert [s.term for s in calendar.sources] == [2025, 2026]
    assert tc.next_conference(calendar, date(2026, 9, 1)) == date(2026, 9, 28)


def test_an_unserved_current_term_or_a_bad_next_term_refuses_the_build() -> None:
    with pytest.raises(tc.CalendarRefused, match="OT2026 schedule not served"):
        tc.build_calendar(
            _Fetcher({2027: _schedule_text(2027)}), today=date(2026, 11, 9), extract=_text
        )
    bad_next = _Fetcher({2026: _schedule_text(2026), 2027: "not a schedule"})
    with pytest.raises(tc.CalendarRefused, match="unrecognised line"):
        tc.build_calendar(bad_next, today=date(2026, 11, 9), extract=_text)


def test_an_oversized_document_is_refused_before_it_is_parsed() -> None:
    def _never(data: bytes) -> str:
        raise AssertionError("parsed")

    huge = _Fetcher({2026: "x" * (tc.MAX_DOCUMENT_BYTES + 1)})
    with pytest.raises(tc.CalendarRefused, match="over the cap"):
        tc.build_calendar(huge, today=date(2026, 11, 9), extract=_never)


def test_a_bad_pdf_is_refused_not_raised() -> None:
    with pytest.raises(tc.CalendarRefused, match="not a readable PDF"):
        tc.pdf_text(b"<html>error</html>")


def test_a_refused_refresh_keeps_the_committed_calendar(tmp_path: Path) -> None:
    good = _Fetcher({2026: _schedule_text(2026)})
    tc.refresh_calendar(good, tmp_path, today=date(2026, 11, 8), extract=_text)
    committed = tc.term_calendar_path(tmp_path).read_bytes()
    broken = _Fetcher({2026: _schedule_text(2026, extra="garbled")})
    with pytest.raises(tc.CalendarRefused, match="2026-11-08's calendar kept"):
        tc.refresh_calendar(broken, tmp_path, today=date(2026, 11, 9), extract=_text)
    assert tc.term_calendar_path(tmp_path).read_bytes() == committed
    assert not list(tc.term_calendar_path(tmp_path).parent.glob("*.tmp"))


def test_a_first_refusal_writes_nothing(tmp_path: Path) -> None:
    with pytest.raises(tc.CalendarRefused, match="nothing written"):
        tc.refresh_calendar(_Fetcher({}), tmp_path, today=date(2026, 11, 9), extract=_text)
    assert not tc.term_calendar_path(tmp_path).exists()


def test_the_calendar_is_read_at_most_once_a_day(tmp_path: Path) -> None:
    fetcher = _Fetcher({2026: _schedule_text(2026)})
    tc.refresh_calendar(fetcher, tmp_path, today=date(2026, 11, 9), extract=_text)
    fetched = len(fetcher.urls)
    line = tc.refresh_calendar(fetcher, tmp_path, today=date(2026, 11, 9), extract=_text)
    assert "not re-read" in line
    assert len(fetcher.urls) == fetched
    tc.refresh_calendar(fetcher, tmp_path, today=date(2026, 11, 9), force=True, extract=_text)
    assert len(fetcher.urls) == 2 * fetched


def test_a_write_that_fails_partway_leaves_the_committed_calendar(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fetcher = _Fetcher({2026: _schedule_text(2026)})
    tc.refresh_calendar(fetcher, tmp_path, today=date(2026, 11, 8), extract=_text)
    committed = tc.term_calendar_path(tmp_path).read_bytes()

    def _truncating(path: Path, model: Any) -> None:
        path.write_text('{"schema_version"')
        raise OSError("disk full")

    monkeypatch.setattr(tc, "write_json", _truncating)
    with pytest.raises(OSError, match="disk full"):
        tc.refresh_calendar(fetcher, tmp_path, today=date(2026, 11, 9), extract=_text)
    assert tc.term_calendar_path(tmp_path).read_bytes() == committed
    assert not list(tc.term_calendar_path(tmp_path).parent.glob("*.tmp"))


def test_the_calendar_validates_under_its_filename(tmp_path: Path) -> None:
    fetcher = _Fetcher({2026: _schedule_text(2026)})
    tc.refresh_calendar(fetcher, tmp_path, today=date(2026, 11, 9), extract=_text)
    path = tc.term_calendar_path(tmp_path)
    assert FILENAME_MODELS[path.name] is TermCalendar
    assert read_model(path, TermCalendar).checked_on == date(2026, 11, 9)


def test_a_calendar_needs_sessions_in_day_order() -> None:
    calendar = tc.build_calendar(
        _Fetcher({2026: _schedule_text(2026)}), today=date(2026, 11, 9), extract=_text
    )
    payload = calendar.model_dump(mode="json")
    with pytest.raises(ValueError, match="at least 1"):
        TermCalendar.model_validate({**payload, "sessions": []})
    with pytest.raises(ValueError, match="day order"):
        TermCalendar.model_validate({**payload, "sessions": payload["sessions"][::-1]})


def test_the_schedule_carries_the_courts_next_conference(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db):
        pass
    tc.refresh_calendar(
        _Fetcher({2026: _schedule_text(2026)}), data_root, today=date(2026, 11, 9), extract=_text
    )
    built = build_schedule(data_root=data_root, corpus_db_path=db, as_of=date(2026, 11, 9))
    assert built.entries == []
    assert built.court_next_conference == date(2026, 11, 13)
    assert built.schema_version == "1.3"
    # No calendar committed: the field is null, and the schedule still builds.
    tc.term_calendar_path(data_root).unlink()
    bare = build_schedule(data_root=data_root, corpus_db_path=db, as_of=date(2026, 11, 9))
    assert bare.court_next_conference is None


def test_an_older_schedule_version_carries_no_court_conference() -> None:
    with pytest.raises(ValueError, match=r"needs 1\.3"):
        Schedule(
            schema_version="1.2", as_of=date(2026, 11, 9), court_next_conference=date(2026, 11, 13)
        )
    assert Schedule(schema_version="1.2", as_of=date(2026, 11, 9)).court_next_conference is None


def _invoke_live_poll(tmp_path: Path) -> Any:
    return CliRunner().invoke(
        cli_module.app,
        [
            "live-poll",
            *("--out", str(tmp_path / "p.json")),
            *("--evaluate-out", str(tmp_path / "e.json")),
            *("--unrecorded-out", str(tmp_path / "u.json")),
        ],
    )


def _stub_cycle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli_module, "live_poll_all", lambda *a, **k: (PullQueues(), LiveDiscovery())
    )
    monkeypatch.setattr(cli_module, "evaluate_backlog", lambda *a, **k: None)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))


def test_the_live_poll_refreshes_the_calendar_before_the_schedule(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_cycle(monkeypatch, tmp_path)
    seen: list[str] = []

    def _refresh(client: object, data_root: Path, *, today: date) -> str:
        seen.append("calendar")
        return "term-calendar: stubbed"

    def _schedule(*args: object, **kwargs: object) -> None:
        seen.append("schedule")

    monkeypatch.setattr(tc, "refresh_calendar", _refresh)
    monkeypatch.setattr(cli_module, "_write_schedule", _schedule)
    result = _invoke_live_poll(tmp_path)
    assert result.exit_code == 0, result.output
    assert seen == ["calendar", "schedule"]
    assert "term-calendar: stubbed" in result.output


def test_a_calendar_failure_warns_and_never_fails_the_live_cycle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _stub_cycle(monkeypatch, tmp_path)

    def _refused(*args: object, **kwargs: object) -> str:
        raise tc.CalendarRefused("not a readable PDF ('a\n::stop-commands::x'); nothing written")

    monkeypatch.setattr(tc, "refresh_calendar", _refused)
    result = _invoke_live_poll(tmp_path)
    assert result.exit_code == 0, result.output
    assert "::warning::term-calendar: not refreshed (CalendarRefused" in result.output
    assert not any(line.startswith("::stop-commands") for line in result.output.splitlines())
    assert (tmp_path / "p.json").exists()


def test_the_command_exits_non_zero_on_a_refusal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))

    def _refused(*args: object, **kwargs: object) -> str:
        raise tc.CalendarRefused("OT2026 schedule not served; nothing written")

    monkeypatch.setattr(tc, "refresh_calendar", _refused)
    result = CliRunner().invoke(cli_module.app, ["term-calendar", "--today", "2026-11-09"])
    assert result.exit_code == 1
    assert "term-calendar: refused: OT2026 schedule not served" in result.output


#: The modules that build what a predict or evaluate cell is handed.
_PROVISIONING_MODULES = (
    "provision.py",
    "blinding.py",
    "pipeline/cell_context.py",
    "pipeline/predict.py",
    "pipeline/evaluate.py",
    "pipeline/prefetch.py",
)


@pytest.mark.parametrize("module", _PROVISIONING_MODULES)
def test_no_provisioning_module_reads_the_calendar(module: str) -> None:
    source = (_SRC / module).read_text()
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    } | {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not imported & {"term_calendar", ".term_calendar", "TermCalendar"}
    assert "term-calendar" not in source
