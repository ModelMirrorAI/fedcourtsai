import json
from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from fedcourtsai.corpus import CorpusLayout
from fedcourtsai.schemas import CorpusRow, Disposition, SeedProgress


def test_layout_locations() -> None:
    layout = CorpusLayout(Path("/repo"))
    assert layout.corpus_dir == Path("/repo/corpus")
    assert layout.shards_dir == Path("/repo/corpus/shards")
    assert layout.metrics_dir == Path("/repo/metrics")
    assert layout.cursor == Path("/repo/config/seed-progress.yaml")


def test_shard_and_metric_paths() -> None:
    layout = CorpusLayout(Path("."))
    assert layout.shard("ca9") == Path("corpus/shards/ca9.parquet")
    # Court ids are slugified so the shard name is always filesystem-safe.
    assert layout.shard("CA DC") == Path("corpus/shards/ca-dc.parquet")
    assert layout.metric("backtest") == Path("metrics/backtest.json")


def test_corpus_row_minimal_and_labeled() -> None:
    row = CorpusRow(case_id="ca9/123", court="ca9")
    # Unresolved rows carry no label.
    assert row.disposition is None
    assert row.judges == []
    assert row.embedding is None

    labeled = CorpusRow(
        case_id="ca9/123",
        court="ca9",
        docket_number="22-1234",
        date_filed=date(2020, 1, 2),
        date_decided=date(2021, 3, 4),
        disposition=Disposition.granted,
        judges=["smith", "jones"],
        nature_topic="civil-rights",
        citations=["410 U.S. 113"],
        opinion_summary="Affirmed.",
    )
    assert labeled.disposition == Disposition.granted
    assert labeled.judges == ["smith", "jones"]


def test_corpus_row_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CorpusRow.model_validate({"case_id": "ca9/1", "court": "ca9", "surprise": "nope"})


def test_committed_seed_cursor_validates() -> None:
    """The checked-in cursor must match SeedProgress and cover the tracked courts."""
    cursor = CorpusLayout().cursor
    data = yaml.safe_load(cursor.read_text())
    progress = SeedProgress.model_validate(data)

    tracking = yaml.safe_load((Path("config") / "tracking.yaml").read_text())
    assert {c.court for c in progress.courts} == set(tracking["courts"])
    # Starts empty: nothing loaded, nothing complete.
    assert all(c.rows_loaded == 0 and not c.complete for c in progress.courts)


def test_dvc_metrics_wiring() -> None:
    """Every metric file registered in dvc.yaml exists and is valid JSON."""
    dvc = yaml.safe_load(Path("dvc.yaml").read_text())
    metric_files = dvc["metrics"]
    assert metric_files, "expected at least one metric file registered for `dvc metrics`"
    for rel in metric_files:
        path = Path(rel)
        assert path.is_file(), f"{rel} is registered in dvc.yaml but missing"
        json.loads(path.read_text())
