"""The per-topic forecast cut: every forecast joined to its case's topic, per moment."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.integrity import FORWARD
from fedcourtsai.leaderboard import cell_facts, skill_components, vote_scores
from fedcourtsai.pipeline import qp_topics
from fedcourtsai.schemas import (
    EventKind,
    QpTopicApplicationLabels,
    QpTopicLabel,
    Stage,
    TopicCut,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import stratify
from fedcourtsai.topic_cut import UNLABELED, build_topic_cut, frame_for
from tests.test_docket_pack import _qp_labels
from tests.test_leaderboard import _evaluation, _write_cell

runner = CliRunner()


def _application_labels(path: Path, primaries: dict[str, QpTopicLabel]) -> None:
    """An application labels artifact, derived from the petition fixture's shape."""
    petition = _qp_labels(path, primaries)
    dumped = petition.read_text(encoding="utf-8")
    raw = json.loads(dumped)
    raw["vocabulary"] = "qp-topic-v1"
    raw["extract_rule"] = "application-extract-v1"
    for entry in raw["entries"]:
        entry["input_kind"] = "docket-only"
    write_json(path, QpTopicApplicationLabels.model_validate(raw))


def _cut(data_root: Path) -> TopicCut:
    cells = list(stratify(data_root, frozen_only=False).cells)
    return build_topic_cut(
        data_root,
        cells,
        process_scope="all",
        skills=skill_components(cells, data_root, None),
        facts=cell_facts(cells, data_root),
        vote_scores=vote_scores(cells, data_root),
    )


def _ledger(data_root: Path) -> None:
    """Two cert forecasts (one labeled case, one not) and one interim forecast."""
    _write_cell(data_root, _evaluation("alpha", case_id="scotus/101", event_id="evt-a"))
    _write_cell(data_root, _evaluation("beta", case_id="scotus/101", event_id="evt-a"))
    _write_cell(data_root, _evaluation("alpha", case_id="scotus/202", event_id="evt-b"))
    _write_cell(
        data_root,
        _evaluation("alpha", case_id="scotus/303", event_id="evt-c"),
        kind=EventKind.motion,
        stage=Stage.interim,
    )


def test_frame_for_joins_cert_and_merits_to_petitions_and_interim_to_applications() -> None:
    assert frame_for(Stage.cert) == "petitions"
    assert frame_for(Stage.merits) == "petitions"
    assert frame_for(Stage.interim) == "applications"
    assert frame_for(None) is None
    # The record models store the stage as its string; the join must still hold.
    stored = "interim"
    assert frame_for(stored) == "applications"  # type: ignore[arg-type]


def test_each_forecast_joins_its_frame_and_the_unlabeled_row_keeps_the_rest(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "data"
    _ledger(data_root)
    # scotus/303 carries a petition label too, which an interim forecast must not read.
    _qp_labels(
        qp_topics.labels_path(data_root),
        {"scotus/101": "criminal-law", "scotus/303": "tax"},
    )
    _application_labels(qp_topics.application_labels_path(data_root), {"scotus/303": "immigration"})

    cut = _cut(data_root)

    rows = {(c.moment.split("@", 1)[0], c.topic): c for c in cut.cells}
    assert set(rows) == {
        ("cert", "criminal-law"),
        ("cert", UNLABELED),
        ("interim", "immigration"),
    }
    labeled = rows[("cert", "criminal-law")]
    assert (labeled.forecast_events, labeled.forecast_cells, labeled.events_scored) == (1, 2, 1)
    assert labeled.frame == "petitions"
    assert [r.predictor_id for r in labeled.records] == ["alpha", "beta"]
    record = labeled.records[0]
    assert record.events_scored == 1
    assert record.forward is not None
    assert record.retrospective is None
    unlabeled = rows[("cert", UNLABELED)]
    assert (unlabeled.forecast_events, unlabeled.forecast_cells) == (1, 1)
    interim = rows[("interim", "immigration")]
    assert interim.frame == "applications"
    assert interim.forecast_events == 1
    # Every cell carries its frame's caveat, so a figure lifted out keeps it.
    assert "not accuracy" in labeled.scope
    assert "qp-topic-v1 application" in interim.scope
    assert [f.frame for f in cut.frames] == ["petitions", "applications"]
    assert cut.frames[0].labeled_cases == 2


def test_a_moments_topic_rows_sum_to_its_whole_forecast_population(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _ledger(data_root)
    _qp_labels(qp_topics.labels_path(data_root), {"scotus/101": "criminal-law"})

    cut = _cut(data_root)

    cert = [c for c in cut.cells if c.moment.startswith("cert@")]
    assert sum(c.forecast_events for c in cert) == 2
    assert sum(c.forecast_cells for c in cert) == 3
    # No application artifact: the interim forecast is unlabeled, not dropped.
    interim = [c for c in cut.cells if c.moment.startswith("interim")]
    assert [c.topic for c in interim] == [UNLABELED]
    assert "No applications topic labels are read" in interim[0].scope


def test_a_labels_artifact_below_the_gate_is_not_read(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _ledger(data_root)
    _qp_labels(
        qp_topics.labels_path(data_root),
        {"scotus/101": "criminal-law"},
        gate_passed=False,
    )

    cut = _cut(data_root)

    assert {c.topic for c in cut.cells if c.moment.startswith("cert@")} == {UNLABELED}
    assert cut.frames[0].labeled_cases == 0
    assert "below the publication gate" in cut.frames[0].scope


def test_records_are_split_by_stratum(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _ledger(data_root)
    cells = list(stratify(data_root, frozen_only=False).cells)
    assert {stratum for _, stratum, _, _ in cells} == {FORWARD}

    cut = _cut(data_root)

    for cell in cut.cells:
        for record in cell.records:
            assert record.forward is not None
            assert record.forward.evaluations >= 1


def test_cli_topic_cut_writes_a_valid_cut(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _ledger(data_root)
    _qp_labels(qp_topics.labels_path(data_root), {"scotus/101": "criminal-law"})
    out = tmp_path / "topic-cut.json"

    result = runner.invoke(
        app,
        ["topic-cut", "--out", str(out), "--all-versions"],
        env={"FEDCOURTS_DATA_ROOT": str(data_root), "FEDCOURTS_METRICS_ROOT": str(tmp_path)},
    )

    assert result.exit_code == 0, result.output
    cut = read_model(out, TopicCut)
    assert cut.process_scope == "all"
    assert "criminal-law" in result.output
    assert UNLABELED in result.output
