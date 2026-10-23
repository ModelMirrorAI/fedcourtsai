"""The freeze-record census checks: each classifies as its entry says, and none reports text.

`scripts/checks/withheld_petitioner_census.py` and
`scripts/checks/side_motion_census.py` run the shipped predicate and scan over
stored payloads and post counts and identifiers to a public PR comment; the
wrapper `scripts/checks/freeze_record_census_fills.py` runs them with the three
other pending censuses. The fixture corpus holds no withheld-block payload and no
substantive application, so these tests build the rows that exercise each
class, and check that no stored entry or document text reaches the summary.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition
from tests.conftest import FixtureCorpus

_CHECKS = Path(__file__).resolve().parents[1] / "scripts" / "checks"


def _module(name: str, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"_census_check_{name}", _CHECKS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # A dataclass resolves its annotations through its module's registry entry;
    # the prefixed name keeps it off any real module's, and monkeypatch drops it.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def _row(case_id: str, docket: str, **kwargs: object) -> corpus.CorpusRow:
    fields: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket,
        "case_name": "Doe v. Marbury Power Cooperative",
        "last_live_polled": date(2026, 8, 1),
    }
    fields.update(kwargs)
    return corpus.CorpusRow.model_validate(fields)


_RESPONDENT = [{"Attorney": "Jane Counsel", "IsCounselofRecord": True, "Title": "Counsel"}]
_EMAIL = "filer.private@example.com"


def test_the_withheld_census_classes_the_shapes_and_reports_no_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    census = _module("withheld_petitioner_census", monkeypatch)
    db = tmp_path / "corpus.db"
    proceedings = [{"Date": "2026-07-01", "Text": "Petition for a writ of certiorari filed."}]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/900", "25-900", salience_selected=True),
                _row("scotus/901", "25-901"),
                _row("scotus/902", "25-902"),
                # Outside the live slice: not walked, though its snapshot withholds.
                _row("scotus/903", "25-903", last_live_polled=None),
            ],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/900",
            date(2026, 7, 2),
            {"ProceedingsandOrder": proceedings, "Respondent": _RESPONDENT},
        )
        corpus.upsert_snapshot(
            conn, "scotus/901", date(2026, 7, 2), {"ProceedingsandOrder": proceedings}
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/902",
            date(2026, 7, 2),
            {"ProceedingsandOrder": proceedings, "Petitioner": [], "Respondent": _RESPONDENT},
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/903",
            date(2026, 7, 2),
            {"ProceedingsandOrder": proceedings, "Respondent": _RESPONDENT},
        )
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/900",
                    kind="petition",
                    url="https://www.supremecourt.gov/petition.pdf",
                    fetched_at=date(2026, 7, 2),
                    text=f"Write to the petitioner at {_EMAIL} for service.",
                )
            ],
        )
    with corpus.connect_readonly(db) as conn:
        found = census.run_census(conn)
    assert (found.rows, found.with_snapshot, found.unread) == (3, 3, False)
    assert (found.residual, found.residual_selected, found.residual_pending) == (1, 0, 1)
    (only,) = found.found
    assert (only.case_id, only.change, only.selected, only.pending, only.documents) == (
        "scotus/900",
        "newly-scrubbed",
        True,
        True,
        1,
    )
    assert only.spans >= 1
    text = census.render(found, listings=True)
    assert "- withheld petitioner block: 1" in text
    assert "  - newly-scrubbed: 1 (selected 1, pending 1, with stored documents 1," in text
    assert "- residual, Court shape with neither counsel key: 1 (selected 0, pending 1)" in text
    assert "`scotus/900` newly-scrubbed selected pending docs=1" in text
    assert _EMAIL not in text and "Write to the petitioner" not in text
    assert "scotus/900" not in census.render(found, listings=False)
    assert "scotus/903" not in text and "FAILED" not in text


def test_the_withheld_census_fails_when_no_walked_row_holds_a_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    census = _module("withheld_petitioner_census", monkeypatch)
    rows = [_row("scotus/910", "25-910"), _row("scotus/911", "25-911")]
    other_channel = tmp_path / "other.db"
    with corpus.connect(other_channel) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_snapshot(conn, "scotus/911", date(2026, 7, 2), {"docket": "rest"})
    with corpus.connect_readonly(other_channel) as conn:
        # Another channel's snapshot alone: no live snapshot, but the store was read.
        assert census.run_census(conn).unread is False
    empty = tmp_path / "empty.db"
    with corpus.connect(empty) as conn:
        corpus.upsert_rows(conn, rows)
    with corpus.connect_readonly(empty) as conn:
        found = census.run_census(conn)
    assert (found.rows, found.with_snapshot, found.unread) == (2, 0, True)
    assert "- FAILED: no walked row holds a stored snapshot" in census.render(found, listings=False)


def _live(*orders: str) -> dict[str, object]:
    return {
        "ProceedingsandOrder": [
            {"Date": "2026-06-20", "Text": "Application for a stay, submitted."},
            *({"Date": "2026-06-25", "Text": order} for order in orders),
        ]
    }


_AMICUS = "Motion for leave to file amicus brief granted."


def test_the_side_motion_census_splits_old_and_new_and_reports_no_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    census = _module("side_motion_census", monkeypatch)
    db = tmp_path / "corpus.db"
    decided = date(2026, 7, 1)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/800", "26A800", application_kind="substantive"),  # pending, freed
                _row("scotus/801", "26A801", application_kind="substantive"),  # pending, no snap
                _row(
                    "scotus/802",
                    "26A802",
                    application_kind="substantive",
                    disposition=Disposition.granted,
                    date_decided=decided,
                ),  # freed
                _row(
                    "scotus/803",
                    "26A803",
                    application_kind="substantive",
                    disposition=Disposition.denied,
                    date_decided=decided,
                ),  # still parked
                _row(
                    "scotus/804",
                    "26A804",
                    application_kind="substantive",
                    disposition=Disposition.denied,
                    date_decided=decided,
                ),  # never fired
                _row(
                    "scotus/805",
                    "26A805",
                    application_kind="substantive",
                    disposition=Disposition.denied,
                    date_decided=decided,
                ),  # no pre-resolution snapshot: skipped
                _row("scotus/806", "26A806", application_kind="extension"),  # not substantive
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/800", date(2026, 7, 2), _live(_AMICUS))
        corpus.upsert_snapshot(conn, "scotus/802", date(2026, 6, 26), _live(_AMICUS))
        corpus.upsert_snapshot(
            conn, "scotus/803", date(2026, 6, 26), _live(_AMICUS, "Application denied.")
        )
        corpus.upsert_snapshot(conn, "scotus/804", date(2026, 6, 26), _live())
        corpus.upsert_snapshot(conn, "scotus/805", decided, _live(_AMICUS))
        corpus.upsert_snapshot(conn, "scotus/806", date(2026, 7, 2), _live(_AMICUS))
    with corpus.connect_readonly(db) as conn:
        found = census.run_census(conn)
    assert (found.pending, found.no_snapshot, found.old_fires) == (2, 1, 1)
    assert (found.new_fires, found.freed_dockets, found.wider) == (0, 1, 0)
    assert {bucket: dict(counts) for bucket, counts in found.split.items()} == {
        "freed": {"granted": 1},
        "still_parked": {"denied": 1},
        "never_fired": {"denied": 1},
    }
    assert found.skipped == 1
    text = census.render(found, listings=True)
    assert "- old pattern is the current base pattern: True" in text
    assert "pending=2 no_snapshot=1 old_fires=1 new_fires=0 freed_dockets=1" in text
    assert "- freed: n=1 granted=1" in text
    assert "- still_parked: n=1 denied=1" in text
    assert "`scotus/800` 26A800 FREED 1" in text
    assert "`scotus/802` 26A802 granted 1" in text
    assert "amicus" not in text.lower() and "Application denied" not in text
    assert census.failures(found, same=True) == [] and "FAILED" not in text
    # Every count before either listing, so a cut summary loses listing rows first.
    assert text.index("- skipped (") < text.index("`scotus/800`") < text.index("`scotus/802`")


def test_the_side_motion_census_names_each_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    census = _module("side_motion_census", monkeypatch)
    unread = census.Census(pending=4, no_snapshot=4)
    assert census.failures(census.Census(), same=True) == []
    assert census.failures(census.Census(pending=4, no_snapshot=3), same=True) == []
    (reason,) = census.failures(unread, same=True)
    assert reason.startswith("every pending application read as holding no snapshot")
    assert len(census.failures(census.Census(wider=1), same=False)) == 2
    assert f"- FAILED: {reason}" in census.render(unread, listings=True, same=True)


def test_the_side_motion_census_names_what_a_failed_text_coverage_run_raised(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    census = _module("side_motion_census", monkeypatch)
    traceback = (
        "Traceback (most recent call last):\n"
        + '  File "/x/cli.py", line 1, in <module>\n'
        + "botocore.exceptions.NoCredentialsError: Unable to locate credentials at /home/x\n"
    )
    assert census.failure_class(traceback) == "botocore.exceptions.NoCredentialsError"
    pretty = (
        "╭──── Traceback (most recent call last) ────╮\n"
        + "│ /x/cli.py:1 in corpus_info                │\n"
        + "╰───────────────────────────────────────────╯\n"
        + "CantOpenError: the ranged VFS serves only the main database\n"
    )
    assert census.failure_class(pretty) == "CantOpenError"
    # Only the line that ends the traceback names the class: a later line that
    # merely looks like one, or an indented one, is message text.
    assert census.failure_class(traceback + "SecretTokenError\n") == (
        "botocore.exceptions.NoCredentialsError"
    )
    assert census.failure_class(pretty.replace("CantOpenError", "   CantOpenError")) is None
    assert census.failure_class("No corpus at /x\n") is None

    def run(*_: object, **__: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 1, stdout="corpus x\n", stderr=traceback)

    monkeypatch.setattr(census.subprocess, "run", run)
    line = census.text_source_line()
    assert line == "text source: not printed (exit 1: botocore.exceptions.NoCredentialsError)"
    assert "/home/x" not in line

    def bare(*_: object, **__: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 1, stdout="", stderr="Killed\n")

    monkeypatch.setattr(census.subprocess, "run", bare)
    assert census.text_source_line() == "text source: not printed (exit 1)"


def test_the_wrapper_clamps_a_section_at_a_line_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    wrapper = _module("freeze_record_census_fills", monkeypatch)
    text = "counts: 3\n" + "".join(f"- row {i}\n" for i in range(100))
    assert wrapper.clamp(text, 10_000) == text
    cut = wrapper.clamp(text, 200)
    assert len(cut.encode("utf-8")) <= 200
    assert cut.startswith("counts: 3\n- row 0\n")
    kept = cut[: cut.index("\n[section cut")]
    assert text.startswith(kept) and kept.endswith("\n")
    assert f"{len(kept.encode('utf-8'))} of 900 bytes kept" in cut


def test_the_wrapper_gives_short_sections_room_to_long_ones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrapper = _module("freeze_record_census_fills", monkeypatch)
    assert wrapper.shared_cap([100, 200, 5_000, 9_000], 6_000) == 2_850
    assert wrapper.shared_cap([100, 200], 6_000) == 200
    assert wrapper.shared_cap([3_000, 3_000], 1_000) == 500
    sections = ["s\n" * 50, "".join(f"- row {i}\n" for i in range(5_000))]
    fitted = wrapper.fit(sections, 10_000)
    assert fitted[0] == sections[0]
    assert sum(len(text.encode("utf-8")) for text in fitted) <= 10_000
    assert len(fitted[1].encode("utf-8")) > 9_000


def test_the_wrapper_runs_every_census_against_the_fixture_corpus(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrapper = _module("freeze_record_census_fills", monkeypatch)
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("CHECK_SUMMARY", str(summary))
    assert wrapper.main([]) == 0
    text = summary.read_text(encoding="utf-8")
    for census in wrapper.CENSUSES:
        assert f"## {census.entry}\n" in text
        assert f"`scripts/checks/{census.script}`; ok." in text
    assert text.count("`fedcourts corpus-info`: as at the top.") == len(wrapper.CENSUSES)
    assert f"All {len(wrapper.CENSUSES)} censuses ran." in text
    assert len(text.encode("utf-8")) <= wrapper.DEFAULT_MAX_BYTES


def _scripts(tmp_path: Path, **bodies: str) -> dict[str, str]:
    """Stand-in census scripts, each writing a line to its summary first."""
    paths: dict[str, str] = {}
    for name, body in bodies.items():
        path = tmp_path / f"{name}.py"
        path.write_text(
            "import os, sys, time\n"
            + "open(os.environ['CHECK_SUMMARY'], 'a').write('"
            + name
            + " wrote\\n')\n"
            + body
            + "\n",
            encoding="utf-8",
        )
        paths[name] = str(path)
    return paths


def _wrapper_with(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, **bodies: str
) -> tuple[ModuleType, Path]:
    wrapper = _module("freeze_record_census_fills", monkeypatch)
    scripts = _scripts(tmp_path, **bodies)
    monkeypatch.setattr(
        wrapper,
        "CENSUSES",
        tuple(wrapper.Census(path, f"Entry {name}", "a figure") for name, path in scripts.items()),
    )
    monkeypatch.setattr(wrapper, "corpus_info", lambda: ("sha256: fixture\n", None))
    monkeypatch.setattr(wrapper, "ledger_vintage", lambda _root: "ledger: fixture")
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("CHECK_SUMMARY", str(summary))
    return wrapper, summary


def test_the_wrapper_reports_a_failed_and_a_timed_out_census_and_runs_the_next(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrapper, summary = _wrapper_with(
        monkeypatch,
        tmp_path,
        fails="sys.exit(1)",
        hangs="time.sleep(60)",
        passes="",
    )
    monkeypatch.setattr(wrapper, "RESERVE_SECONDS", 1)
    assert wrapper.main(["--budget-seconds", "3"]) == 1
    text = summary.read_text(encoding="utf-8")
    assert "fails.py`; FAILED, exit 1." in text
    assert "hangs.py`; FAILED, timed out after 1 s." in text
    assert "passes.py`; ok." in text
    assert text.index("fails wrote") < text.index("hangs wrote") < text.index("passes wrote")
    assert text.rstrip().endswith("(timed out after 1 s).")
    (failed,) = [line for line in text.splitlines() if line.startswith("Failed: ")]
    assert "fails.py (exit 1)" in failed and "hangs.py (timed out" in failed
    assert "passes.py" not in failed


def test_the_wrapper_marks_a_census_the_spent_budget_left_unrun(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrapper, summary = _wrapper_with(
        monkeypatch, tmp_path, passes="", hangs="time.sleep(60)", never="sys.exit(0)"
    )
    monkeypatch.setattr(wrapper, "RESERVE_SECONDS", 0)
    assert wrapper.main(["--budget-seconds", "1"]) == 1
    text = summary.read_text(encoding="utf-8")
    assert "passes.py`; ok." in text
    assert "hangs.py`; FAILED, timed out after" in text
    assert "never.py`; FAILED, not run: the time budget was spent." in text
    assert "never wrote" not in text
    assert "never.py (not run: the time budget was spent)" in text
