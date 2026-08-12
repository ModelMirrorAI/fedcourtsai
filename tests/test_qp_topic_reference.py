"""The committed qp-topic reference set stays valid, canonical, and complete."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai.schemas import QP_TOPIC_LABELS, QpTopicReference, QpTopicReferenceEntry
from fedcourtsai.serialize import read_model

_REFERENCE = Path(__file__).resolve().parents[1] / "data" / "qp-topics" / "qp-topic-reference.json"


def _entry(case_id: str, docket_number: str) -> QpTopicReferenceEntry:
    return QpTopicReferenceEntry(case_id=case_id, docket_number=docket_number, label="tax")


def test_reference_set_is_valid_and_canonical() -> None:
    ref = read_model(_REFERENCE, QpTopicReference)
    # cases == len(entries) and case_id order/uniqueness are schema-enforced by
    # the model validator; docket_number uniqueness is the docstring's pairing
    # contract, checked only here.
    docket_numbers = [entry.docket_number for entry in ref.entries]
    assert len(set(docket_numbers)) == len(docket_numbers)


def test_reference_set_bytes_are_the_canonical_serialization() -> None:
    # Hand edits must round-trip through the same serialization every other
    # committed artifact gets (serialize.write_json), or the first regeneration
    # buries the judgment change in a formatting diff.
    payload = json.loads(_REFERENCE.read_text())
    assert _REFERENCE.read_text() == json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_reference_set_exercises_the_whole_vocabulary() -> None:
    # Every label appears at least once, so a vocabulary change and a reference
    # change must travel together. Presence is not measurability: per-label
    # rates below the support floor stay unmeasured (docs/qp-topic.md).
    ref = read_model(_REFERENCE, QpTopicReference)
    assert {entry.label for entry in ref.entries} == set(QP_TOPIC_LABELS)


def test_model_rejects_count_drift() -> None:
    with pytest.raises(ValidationError, match="cases must equal"):
        QpTopicReference(cases=2, entries=[_entry("scotus/1", "25-1")])


def test_model_rejects_unsorted_or_duplicate_case_ids() -> None:
    with pytest.raises(ValidationError, match="sorted by case_id"):
        QpTopicReference(cases=2, entries=[_entry("scotus/2", "25-2"), _entry("scotus/1", "25-1")])
    with pytest.raises(ValidationError, match="sorted by case_id"):
        QpTopicReference(cases=2, entries=[_entry("scotus/1", "25-1"), _entry("scotus/1", "25-2")])
