"""The committed qp-topic reference set stays valid, canonical, and measurable."""

import json
from pathlib import Path

from fedcourtsai.schemas import QP_TOPIC_LABELS, QpTopicReference
from fedcourtsai.serialize import read_model

_REFERENCE = Path(__file__).resolve().parents[1] / "data" / "qp-topics" / "qp-topic-reference.json"


def test_reference_set_is_valid_and_canonical() -> None:
    ref = read_model(_REFERENCE, QpTopicReference)
    assert ref.cases == len(ref.entries)
    case_ids = [e.case_id for e in ref.entries]
    assert case_ids == sorted(case_ids)
    assert len(set(case_ids)) == len(case_ids)
    docket_numbers = [e.docket_number for e in ref.entries]
    assert len(set(docket_numbers)) == len(docket_numbers)


def test_reference_set_bytes_are_the_canonical_serialization() -> None:
    # Hand edits must round-trip through the same serialization every other
    # committed artifact gets (serialize.write_json), or the first regeneration
    # buries the judgment change in a formatting diff.
    payload = json.loads(_REFERENCE.read_text())
    assert _REFERENCE.read_text() == json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_reference_set_exercises_the_whole_vocabulary() -> None:
    # A label with zero reference examples cannot be measured, so a vocabulary
    # change and a reference change must travel together.
    ref = read_model(_REFERENCE, QpTopicReference)
    assert {e.label for e in ref.entries} == set(QP_TOPIC_LABELS)
