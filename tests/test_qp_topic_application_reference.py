"""The application reference block's schema: what it accepts and what it refuses."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline.qp_topics import application_reference_path
from fedcourtsai.schemas import QpTopicApplicationReference
from fedcourtsai.serialize import write_json


def _entry(case_id: str, docket: str, label: str = "immigration") -> dict[str, str]:
    return {
        "case_id": case_id,
        "docket_number": docket,
        "input_kind": "docket-only",
        "label": label,
    }


def test_a_well_formed_block_validates_where_the_reader_looks(tmp_path: Path) -> None:
    block = QpTopicApplicationReference(
        cases=2,
        entries=[_entry("scotus/1", "24A949"), _entry("scotus/2", "24A950", "unclassifiable")],
    )
    path = application_reference_path(tmp_path / "data")
    write_json(path, block)
    result = CliRunner().invoke(app, ["validate", str(path.parent)])
    assert result.exit_code == 0, result.output
    assert block.vocabulary == "qp-topic-v1"
    assert block.extract_rule == "application-extract-v1"


@pytest.mark.parametrize(
    ("entries", "cases", "message"),
    [
        ([_entry("scotus/2", "24A950"), _entry("scotus/1", "24A949")], 2, "sorted"),
        ([_entry("scotus/1", "24A949"), _entry("scotus/2", "24a949 ")], 2, "at most once"),
        ([_entry("scotus/1", "24A949")], 2, "cases must equal"),
        ([_entry("scotus/1", "24A949", "stay-of-execution")], 1, "label"),
    ],
)
def test_a_malformed_block_is_refused(
    entries: list[dict[str, str]], cases: int, message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        QpTopicApplicationReference(cases=cases, entries=entries)
