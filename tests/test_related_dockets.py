"""The ``Vide``-linked dockets a predict cell reads under ``record/related/``."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import pytest
from typer.testing import CliRunner, Result

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.provision import (
    MAX_RELATED_DOCKETS,
    RelatedRead,
    place_related,
    related_manifest,
    vide_docket_numbers,
)
from fedcourtsai.schemas import EventKind, Moment, Stage
from tests.conftest import FixtureCorpus

runner = CliRunner()

_GRANT_DATE = date(2026, 1, 15)
_GRANT_CUTOFF = date(2026, 1, 16)

#: scotus/305 (No. 24-12) as the live channel serves it, linking No. 24-99.
_CELL: dict[str, Any] = {
    "id": 305,
    "docket_number": "24-12",
    "CaseNumber": "24-12 ",
    "RelatedCaseNumber": [
        {"DisplayCaseNumber": "24-99", "RelatedType": "Vide"},
        {"DisplayCaseNumber": "24-12", "RelatedType": "Vide"},
        {"DisplayCaseNumber": "23-500", "RelatedType": "Consolidated"},
        {"DisplayCaseNumber": "24-777", "RelatedType": "Vide"},
    ],
    "docket_entries": [
        {"id": 1, "date_filed": "2025-01-15", "description": "Petition filed."},
        {"id": 2, "date_filed": "2026-01-15", "description": "Petition GRANTED."},
    ],
}

#: The companion, No. 24-99: granted with 24-12, and decided long after.
_COMPANION: dict[str, Any] = {
    "id": 399,
    "docket_number": "24-99",
    "docket_entries": [
        {"id": 1, "date_filed": "2025-01-20", "description": "Cross-petition filed."},
        {"id": 2, "date_filed": "2026-01-15", "description": "Petition GRANTED."},
        {"id": 3, "date_filed": "2026-06-30", "description": "Judgment AFFIRMED."},
    ],
}


def _seed(fixture_corpus: FixtureCorpus) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/399",
                    court="scotus",
                    docket_number="24-99",
                    last_live_polled=date(2026, 7, 20),
                )
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 20), _CELL)
        corpus.upsert_snapshot(conn, "scotus/399", date(2026, 7, 21), _COMPANION)
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
                    opened_at=_GRANT_DATE,
                )
            ],
        )


def _provision(*args: str) -> Result:
    return runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305", *args])


def _descriptions(payload: dict[str, Any]) -> list[str]:
    return [str(entry["description"]) for entry in payload["docket_entries"]]


def test_only_vide_links_are_read_without_the_dockets_own_number() -> None:
    assert vide_docket_numbers(_CELL) == ("24-99", "24-777")
    assert vide_docket_numbers({"RelatedCaseNumber": "24-99"}) == ()
    assert vide_docket_numbers({}) == ()


def test_the_links_stop_at_the_bound_in_served_order() -> None:
    linked = [
        {"DisplayCaseNumber": f"24-{n}", "RelatedType": "Vide"}
        for n in range(1, MAX_RELATED_DOCKETS + 3)
    ]
    numbers = vide_docket_numbers({"CaseNumber": "25-1", "RelatedCaseNumber": linked})
    assert numbers == tuple(f"24-{n}" for n in range(1, MAX_RELATED_DOCKETS + 1))


def test_a_companion_is_cut_to_the_cells_cutoff() -> None:
    placed = place_related(
        RelatedRead("24-99", "scotus/399", (date(2026, 7, 21), _COMPANION)),
        _GRANT_CUTOFF,
        mode="replay",
        vintage=date(2026, 7, 20),
    )
    assert placed.payload is not None
    assert _descriptions(placed.payload) == ["Cross-petition filed.", "Petition GRANTED."]
    assert placed.snapshot_date == _GRANT_CUTOFF


def test_an_uncut_forward_cells_companion_is_bounded_by_its_own_snapshot_date() -> None:
    # The companion was pulled a day after the cell's docket; anything it shows
    # from that day on is past what the cell's terminal gate read.
    placed = place_related(
        RelatedRead("24-99", "scotus/399", (date(2026, 7, 21), _COMPANION)),
        None,
        mode="forward",
        vintage=date(2026, 6, 30),
    )
    assert placed.payload is not None
    assert "Judgment AFFIRMED." not in _descriptions(placed.payload)
    assert placed.snapshot_date == date(2026, 6, 30)


@pytest.mark.parametrize(
    ("read", "mode", "reason"),
    [
        (RelatedRead("24-777", None, None), "forward", "not in the corpus"),
        (RelatedRead("24-99", "scotus/399", None), "forward", "no stored snapshot"),
        (
            RelatedRead("24-99", "scotus/399", (date(2026, 7, 21), _COMPANION)),
            "replay",
            "a replay cell with no cutoff",
        ),
    ],
)
def test_a_companion_that_cannot_be_placed_is_recorded_with_its_reason(
    read: RelatedRead, mode: str, reason: str
) -> None:
    placed = place_related(read, None, mode=mode, vintage=date(2026, 7, 20))
    assert placed.payload is None
    assert placed.reason == reason
    [row] = related_manifest([placed])
    assert row["staged"] is False
    assert row["file"] is None
    assert row["reason"] == reason


def test_provision_stages_the_companion_cut_to_the_moment(fixture_corpus: FixtureCorpus) -> None:
    _seed(fixture_corpus)

    result = _provision("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    staged = json.loads(paths.related_snapshot("24-99").read_text())
    assert _descriptions(staged) == ["Cross-petition filed.", "Petition GRANTED."]
    manifest = json.loads(paths.related_manifest.read_text())
    assert [(row["docket_number"], row["staged"], row["reason"]) for row in manifest] == [
        ("24-99", True, None),
        ("24-777", False, "not in the corpus"),
    ]
    assert "related (24-99, 24-777 (not in the corpus))" in result.output


def test_a_cell_without_an_event_reads_no_companion(fixture_corpus: FixtureCorpus) -> None:
    # The evaluate path names no event: it grades against the resolved docket.
    _seed(fixture_corpus)
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    paths.related_dir.mkdir(parents=True)
    paths.related_snapshot("24-1").write_text("{}")

    result = _provision()

    assert result.exit_code == 0, result.output
    assert not any(paths.related_dir.iterdir())
