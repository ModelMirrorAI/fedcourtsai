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
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition
from tests.conftest import FixtureCorpus

_CHECKS = Path(__file__).resolve().parents[1] / "scripts" / "checks"


def _module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, _CHECKS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # A dataclass resolves its annotations through its module's registry entry.
    sys.modules[spec.name] = module
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


def test_the_withheld_census_classes_the_shapes_and_reports_no_text(tmp_path: Path) -> None:
    census = _module("withheld_petitioner_census")
    db = tmp_path / "corpus.db"
    proceedings = [{"Date": "2026-07-01", "Text": "Petition for a writ of certiorari filed."}]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/900", "25-900", salience_selected=True),
                _row("scotus/901", "25-901"),
                _row("scotus/902", "25-902"),
                # Outside the live slice: not walked.
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
    assert (found.rows, found.with_snapshot) == (3, 3)
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


def _live(*orders: str) -> dict[str, object]:
    return {
        "ProceedingsandOrder": [
            {"Date": "2026-06-20", "Text": "Application for a stay, submitted."},
            *({"Date": "2026-06-25", "Text": order} for order in orders),
        ]
    }


_AMICUS = "Motion for leave to file amicus brief granted."


def test_the_side_motion_census_splits_old_and_new_and_reports_no_text(tmp_path: Path) -> None:
    census = _module("side_motion_census")
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


def test_the_wrapper_clamps_a_section_at_a_line_boundary() -> None:
    wrapper = _module("freeze_record_census_fills")
    text = "counts: 3\n" + "".join(f"- row {i}\n" for i in range(100))
    assert wrapper.clamp(text, 10_000) == text
    cut = wrapper.clamp(text, 40)
    assert cut.startswith("counts: 3\n- row 0\n- row 1\n- row 2\n")
    assert "[section cut at 34 of 900 bytes;" in cut


def test_the_wrapper_runs_every_census_against_the_fixture_corpus(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrapper = _module("freeze_record_census_fills")
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("CHECK_SUMMARY", str(summary))
    assert wrapper.main([]) == 0
    text = summary.read_text(encoding="utf-8")
    for census in wrapper.CENSUSES:
        assert f"## {census.entry}\n" in text
        assert f"`scripts/checks/{census.script}`; ok." in text
    assert text.count("`fedcourts corpus-info`: as at the top.") == len(wrapper.CENSUSES)
    assert "All five censuses ran." in text
