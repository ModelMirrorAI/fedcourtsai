"""The ``Vide``-linked dockets a predict cell reads under ``record/related/``."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner, Result

from fedcourtsai import casestore, corpus
from fedcourtsai.cli import app
from fedcourtsai.fixture import build_fixture_corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cell_context
from fedcourtsai.pipeline.cascade import run_cascade
from fedcourtsai.pipeline.vide_links import MAX_RELATED_DOCKETS, vide_docket_numbers
from fedcourtsai.provision import (
    RelatedRead,
    place_related,
    read_related,
    related_manifest,
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
        event="evt-order-judgment",
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
        event="evt-petition-disposition",
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
    placed = place_related(
        read, None, event="evt-petition-disposition", mode=mode, vintage=date(2026, 7, 20)
    )
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


def test_a_number_not_shaped_as_a_docket_number_is_refused() -> None:
    # The number becomes a file name under record/related/.
    payload = {
        "CaseNumber": "25-1",
        "RelatedCaseNumber": [
            {"DisplayCaseNumber": "../../../x", "RelatedType": "Vide"},
            {"DisplayCaseNumber": "24-99, 24-100", "RelatedType": "Vide"},
            {"DisplayCaseNumber": "25A123", "RelatedType": "Vide"},
        ],
    }
    assert vide_docket_numbers(payload) == ("25A123",)


def test_no_index_is_recorded_as_unread_and_the_own_case_is_dropped() -> None:
    unread = read_related(
        ("24-99",), own_case="scotus/305", resolve=lambda _: None, snapshot=lambda _: None
    )
    assert [(r.docket_number, r.unread) for r in unread] == [
        ("24-99", "no corpus index to resolve it through")
    ]
    placed = place_related(
        unread[0], None, event="evt-petition-disposition", mode="forward", vintage=_GRANT_DATE
    )
    assert placed.reason == "no corpus index to resolve it through"
    own = read_related(
        ("24-12",),
        own_case="scotus/305",
        resolve=lambda _: {"24-12": "scotus/305"},
        snapshot=lambda _: None,
    )
    assert own == ()


def test_the_arrival_moment_bounds_a_companion_before_its_opening_day() -> None:
    # The cell's own docket is cut at the opening entry; a companion carries no
    # anchor, so the opening day is kept out entirely.
    companion = {
        "docket_entries": [
            {"id": 1, "date_filed": "2026-06-21", "description": "Petition filed."},
            {"id": 2, "date_filed": "2026-06-22", "description": "Application submitted."},
            {"id": 3, "date_filed": "2026-06-22", "description": "Application denied."},
        ]
    }
    placed = place_related(
        RelatedRead("26A11", "scotus/306", (date(2026, 7, 1), companion)),
        date(2026, 6, 23),
        event="evt-motion-disposition",
        mode="forward",
        vintage=date(2026, 7, 1),
    )
    assert placed.payload is not None
    assert _descriptions(placed.payload) == ["Petition filed."]


def test_a_companion_loses_its_undated_outcome_markers() -> None:
    granted_later = {
        **_COMPANION,
        "QPLink": "../qp/24-00099qp.pdf",
        "Other": [{"Attorney": "Amicus counsel", "Email": "a@example.com"}],
        "AttorneyHeaderOther": "Other",
        "Petitioner": [{"Attorney": "Self", "Email": "self@example.com"}],
        "PetitionerTitle": "Acme Corp.",
        "RelatedCaseNumber": [{"DisplayCaseNumber": "24-500", "RelatedType": "Vide"}],
        "docket_entries": [*_COMPANION["docket_entries"], {"id": 4, "description": "Undated."}],
    }
    placed = place_related(
        RelatedRead("24-99", "scotus/399", (date(2026, 7, 21), granted_later)),
        _GRANT_CUTOFF,
        event="evt-order-judgment",
        mode="forward",
        vintage=date(2026, 7, 20),
    )
    assert placed.payload is not None
    for key in ("QPLink", "Other", "AttorneyHeaderOther", "Petitioner"):
        assert key not in placed.payload
    assert placed.payload["PetitionerTitle"] == "Acme Corp."
    assert "RelatedCaseNumber" not in placed.payload
    assert "Undated." not in _descriptions(placed.payload)


def test_links_are_read_off_the_placed_snapshot(fixture_corpus: FixtureCorpus) -> None:
    # A dated snapshot from before the moment links nothing; the latest pull
    # links 24-99. The cell reads its moment's links, not today's.
    _seed(fixture_corpus)
    unlinked = {key: value for key, value in _CELL.items() if key != "RelatedCaseNumber"}
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", _GRANT_DATE, unlinked)

    result = _provision("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert not paths.related_manifest.exists()


def test_out_leaves_the_record_untouched(fixture_corpus: FixtureCorpus, tmp_path: Any) -> None:
    _seed(fixture_corpus)
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    paths.related_dir.mkdir(parents=True)
    paths.related_snapshot("24-1").write_text("{}")

    result = _provision("--event", "evt-order-judgment", "--out", str(tmp_path / "copy.json"))

    assert result.exit_code == 0, result.output
    assert paths.related_snapshot("24-1").exists()


def test_the_live_lookup_reads_only_the_live_slice(fixture_corpus: FixtureCorpus) -> None:
    _seed(fixture_corpus)
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id="scotus/398", court="scotus", docket_number="24-98"),
                corpus.CorpusRow(
                    case_id="scotus/1399",
                    court="scotus",
                    docket_number="No. 24-99",
                    last_live_polled=date(2026, 7, 20),
                ),
            ],
        )
        found = corpus.live_scotus_case_ids_by_docket_numbers(conn, ["24-99", "24-98", "24-7"])
    assert found == {"24-99": "scotus/399"}


@mock_aws
def test_the_casestore_backend_stages_the_same_companions(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The production backend: numbers resolve through the index, payloads come from the store."""
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="fcai-rel")
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", "s3://fcai-rel/casestore/v1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    casestore.set_active_transport(casestore.transport_from_settings())
    build_fixture_corpus(corpus.corpus_db_path(corpus_root))
    _seed(FixtureCorpus(corpus_root=corpus_root, data_root=tmp_path / "unused"))
    casestore.reset_active_transport()

    def tree(backend: str, data_root: Any) -> dict[str, bytes]:
        monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
        monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
        result = _provision("--event", "evt-order-judgment", "--corpus-backend", backend)
        assert result.exit_code == 0, result.output
        related = CasePaths(data_root, "scotus", 305).related_dir
        return {p.name: p.read_bytes() for p in sorted(related.iterdir())}

    blob = tree("local", tmp_path / "blob")
    store = tree("casestore", tmp_path / "cs")
    assert set(blob) == {"24-99.json", "related.json"}
    assert blob == store


def test_a_refused_cell_reads_no_companion(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(fixture_corpus)
    decided = {
        **_CELL,
        "docket_entries": [
            *_CELL["docket_entries"],
            {"id": 3, "date_filed": "2026-06-30", "description": "Judgment REVERSED."},
        ],
    }
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_snapshot(conn, "scotus/305", date(2026, 7, 22), decided)

    def _no_lookup(*_args: object) -> None:
        raise AssertionError("a refused cell resolved its companions")

    monkeypatch.setattr(corpus, "live_scotus_case_ids_by_docket_numbers", _no_lookup)

    result = _provision("--event", "evt-order-judgment", "--refuse-terminal")

    assert result.exit_code == 3, result.output
    assert not CasePaths(fixture_corpus.data_root, "scotus", 305).related_dir.exists()


def test_the_local_cascade_stages_the_companion(
    fixture_corpus: FixtureCorpus, tmp_path: Any
) -> None:
    _seed(fixture_corpus)

    report = run_cascade(
        corpus_db_path=fixture_corpus.db_path,
        data_root=fixture_corpus.data_root,
        config_root=Path("config"),
        court="scotus",
        docket=305,
        event="evt-order-judgment",
        run_id="20260720T120000Z",
    )

    assert report.valid, report.problems
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    manifest = json.loads(paths.related_manifest.read_text())
    assert [(row["docket_number"], row["staged"]) for row in manifest] == [
        ("24-99", True),
        ("24-777", False),
    ]
    staged = json.loads(paths.related_snapshot("24-99").read_text())
    assert _descriptions(staged) == ["Cross-petition filed.", "Petition GRANTED."]


def test_the_context_freezes_the_placed_payloads_links() -> None:
    context = cell_context.build("scotus/305", date(2026, 7, 20), _CELL, "forward")
    assert context.vide_links == ["24-99", "24-777"]
    unlinked = {key: value for key, value in _CELL.items() if key != "RelatedCaseNumber"}
    assert cell_context.build("scotus/305", date(2026, 7, 20), unlinked, "forward").vide_links == []
    rest = {"id": 305, "docket_number": "24-12", "docket_entries": []}
    assert cell_context.build("scotus/305", date(2026, 7, 20), rest, "forward").vide_links is None


def test_the_provisioned_context_carries_the_links(fixture_corpus: FixtureCorpus) -> None:
    _seed(fixture_corpus)

    result = _provision("--event", "evt-order-judgment")

    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert json.loads(paths.cell_context.read_text())["vide_links"] == ["24-99", "24-777"]
