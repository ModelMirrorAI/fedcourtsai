"""The application reference block's schema: what it accepts and what it refuses."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.corpus import strip_docket_annotation
from fedcourtsai.pipeline.application_topics import (
    APPLICATION_EXTRACT_RULE,
    APPLICATION_TOPIC_VERSION,
)
from fedcourtsai.pipeline.qp_topics import application_reference_path
from fedcourtsai.schemas import QpTopicApplicationReference
from fedcourtsai.serialize import read_model, write_json


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
    # The schema's literals track the extract's constants, so bumping the rule
    # cannot leave the reference schema behind.
    assert block.vocabulary == APPLICATION_TOPIC_VERSION
    assert block.extract_rule == APPLICATION_EXTRACT_RULE


@pytest.mark.parametrize(
    ("entries", "cases", "message"),
    [
        ([_entry("scotus/2", "24A950"), _entry("scotus/1", "24A949")], 2, "sorted"),
        ([_entry("scotus/1", "24A949")], 2, "cases must equal"),
        ([_entry("scotus/1", "24A949", "stay-of-execution")], 1, "label"),
    ],
)
def test_a_malformed_block_is_refused(
    entries: list[dict[str, str]], cases: int, message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        QpTopicApplicationReference(cases=cases, entries=entries)


_COMMITTED = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "qp-topics"
    / "qp-topic-reference-applications.json"
)


@pytest.mark.reads_data
def test_the_committed_block_is_valid_canonical_and_keyed_once() -> None:
    block = read_model(_COMMITTED, QpTopicApplicationReference)
    # Docket uniqueness is checked on the spelling the join compares, the
    # Court's capital-case marking removed, which application dockets carry.
    dockets = [strip_docket_annotation(entry.docket_number) for entry in block.entries]
    assert len(set(dockets)) == len(dockets)
    payload = json.loads(_COMMITTED.read_text())
    assert _COMMITTED.read_text() == json.dumps(payload, indent=2, sort_keys=True) + "\n"
