"""Policy areas read by the application labeler (policy-area-v2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.cli import app
from fedcourtsai.pipeline import qp_topics
from fedcourtsai.pipeline.application_policy import (
    PolicyFlags,
    accrue_policy,
    derive_policy_rows,
    measure_policy,
    read_policy_flags,
)
from fedcourtsai.pipeline.application_topics import ApplicationExtractRow
from fedcourtsai.pipeline.policy_area import (
    POLICY_AREA_RULE_VERSION,
    POLICY_AREA_V2_RULE_VERSION,
    PolicyLabel,
    policy_source,
)
from fedcourtsai.pipeline.qp_topics import QpTopicError, build_application_labels
from fedcourtsai.schemas import (
    PolicyAreaLabel,
    QpTopicApplicationLabelEntry,
    QpTopicApplicationLabels,
)
from fedcourtsai.serialize import read_model, write_json
from tests.test_qp_topic_application_labels import (
    _FRESH,
    _REFERENCE,
    _block,
    _extract,
    _kinds,
    _lines,
    _texts,
)

runner = CliRunner()

# Every topic-reference row is also hand-labeled for policy, plus one fresh row.
_HAND: dict[str, PolicyLabel] = {
    docket.upper(): PolicyLabel("immigration", "hand", False) for _, docket, _ in _REFERENCE
}


def _policy_lines(miss: int = 0) -> list[QpTopicApplicationLabelEntry]:
    """The topic lines, each carrying a policy area: ``miss`` hand rows get it wrong."""
    out: list[QpTopicApplicationLabelEntry] = []
    for index, line in enumerate(_lines(miss=0)):
        area: PolicyAreaLabel = "health" if index < miss else "immigration"
        if line.case_id == _FRESH[1][0]:
            area = "firearms"
        out.append(QpTopicApplicationLabelEntry(**line.model_dump(), policy_area=area))
    return out


def _flags(*, policy_only: frozenset[str] = frozenset()) -> dict[str, PolicyFlags]:
    return {
        case_id: PolicyFlags(policy_row=True, policy_only=case_id in policy_only)
        for case_id in _texts()
    }


def _artifact() -> QpTopicApplicationLabels:
    return build_application_labels(
        entries=_lines(miss=0),
        texts=_texts(),
        input_kinds=_kinds(),
        reference=_block(),
        labeler="claude-code/test",
    )


def test_a_batch_owing_no_policy_area_adds_no_rows() -> None:
    frame = [(c, d, False) for c, d, _ in _REFERENCE]
    batch = derive_policy_rows(
        frame=frame, topic_batch=[], artifact=None, hand=_HAND, budget=100, seed="s"
    )
    assert batch.case_ids == ()
    assert batch.owed == 0


def test_a_batch_owing_areas_carries_the_hand_rows_and_backfills_up_to_the_budget() -> None:
    artifact = _artifact()
    frame = [(c, d, True) for c, d, _ in _REFERENCE] + [(c, d, True) for c, d in _FRESH]
    # Nothing new in the topic batch: every published policy row lacks an area.
    batch = derive_policy_rows(
        frame=frame, topic_batch=[], artifact=artifact, hand=_HAND, budget=11, seed="s"
    )
    assert batch.owed == 12
    assert batch.reference_rows == 10
    assert batch.backfill == 1
    assert batch.remaining == 1
    assert len(batch.case_ids) == 11
    with pytest.raises(QpTopicError, match="hand-labeled policy row"):
        derive_policy_rows(
            frame=frame, topic_batch=[], artifact=artifact, hand=_HAND, budget=5, seed="s"
        )


def test_the_measurement_counts_agreement_per_area_and_drops_off_frame_areas() -> None:
    lines = _policy_lines(miss=1)
    flags = _flags()
    flags[_FRESH[0][0]] = PolicyFlags(policy_row=False, policy_only=False)
    measured = measure_policy(entries=lines, flags=flags, hand=_HAND)
    assert measured is not None
    agreement, areas = measured
    assert (agreement.agree, agreement.n, agreement.uncovered) == (9, 10, 0)
    assert agreement.off_frame == 1
    assert agreement.floor == 1.0
    assert agreement.gate_passed
    assert [(s.area, s.agree, s.n) for s in agreement.per_area] == [("immigration", 9, 10)]
    assert _FRESH[0][0] not in areas
    assert areas[_FRESH[1][0]] == "firearms"


def test_the_gate_refuses_low_agreement() -> None:
    measured = measure_policy(entries=_policy_lines(miss=3), flags=_flags(), hand=_HAND)
    assert measured is not None
    assert not measured[0].gate_passed


def test_a_passing_measurement_publishes_hand_and_labeler_areas_once() -> None:
    artifact = _artifact()
    measured = measure_policy(entries=_policy_lines(miss=1), flags=_flags(), hand=_HAND)
    assert measured is not None
    agreement, areas = measured

    accrued, published = accrue_policy(artifact, agreement=agreement, areas=areas, hand=_HAND)

    rows = {entry.case_id: entry for entry in accrued.entries}
    # A hand row publishes its hand label even where the labeler missed it.
    missed = rows[_REFERENCE[0][0]]
    assert (missed.policy_area, missed.policy_source) == ("immigration", "reference")
    fresh = rows[_FRESH[1][0]]
    assert (fresh.policy_area, fresh.policy_source, fresh.policy_batch) == (
        "firearms",
        "labeler",
        1,
    )
    assert published == 12
    assert accrued.policy_agreement == agreement
    assert accrued.batches[-1].policy_published == 12
    # Topic labels are untouched.
    assert [(e.case_id, e.label) for e in accrued.entries] == [
        (e.case_id, e.label) for e in artifact.entries
    ]
    # Set once: a later passing batch does not move a labeler area.
    changed = {**areas, _FRESH[1][0]: "health"}
    again, republished = accrue_policy(accrued, agreement=agreement, areas=changed, hand=_HAND)
    assert {e.case_id: e for e in again.entries}[_FRESH[1][0]].policy_area == "firearms"
    assert republished == 0


def test_a_refused_measurement_publishes_nothing_and_keeps_the_standing_record() -> None:
    artifact = _artifact()
    measured = measure_policy(entries=_policy_lines(miss=3), flags=_flags(), hand=_HAND)
    assert measured is not None
    agreement, areas = measured

    accrued, published = accrue_policy(artifact, agreement=agreement, areas=areas, hand=_HAND)

    assert published == 0
    assert accrued.policy_agreement is None
    assert all(entry.policy_area is None for entry in accrued.entries)
    assert (accrued.batches[-1].policy_agree, accrued.batches[-1].policy_n) == (7, 10)
    assert accrued.batches[-1].policy_published == 0


def test_the_cut_reads_v2_only_once_a_measurement_passed() -> None:
    artifact = _artifact()
    assert policy_source(None).rule_version == POLICY_AREA_RULE_VERSION
    assert policy_source(artifact).rule_version == POLICY_AREA_RULE_VERSION
    measured = measure_policy(entries=_policy_lines(miss=1), flags=_flags(), hand=_HAND)
    assert measured is not None
    accrued, _ = accrue_policy(artifact, agreement=measured[0], areas=measured[1], hand=_HAND)

    source = policy_source(accrued)

    assert source.rule_version == POLICY_AREA_V2_RULE_VERSION
    label = source.label(_FRESH[1][1].lower())
    assert label is not None
    assert label.area == "firearms"


def test_a_policy_only_row_must_be_a_policy_row(tmp_path: Path) -> None:
    path = tmp_path / "extract.json"
    path.write_text(json.dumps([{"case_id": "scotus/1", "policy_only": True}]))
    with pytest.raises(QpTopicError, match="policy_only row is a policy row"):
        read_policy_flags(path)
    path.write_text(json.dumps([{"case_id": "scotus/1"}]))
    assert read_policy_flags(path) == {"scotus/1": PolicyFlags(False, False)}


def test_the_command_backfills_a_policy_only_row_without_touching_its_topic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = tmp_path / "data"
    write_json(qp_topics.application_reference_path(data), _block())
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    monkeypatch.setattr(cli, "policy_areas", lambda: _HAND)
    # A standing artifact with no policy areas; the fresh rows are published.
    prior = _artifact()
    write_json(qp_topics.application_labels_path(data), prior)
    # The second batch: the reference block, and one fresh row back for its area alone.
    fresh_case, fresh_docket = _FRESH[1]
    extract = [
        {**row, "policy_row": True, "policy_only": row["case_id"] == fresh_case}
        for row in _extract()
        if row["case_id"] != _FRESH[0][0]
    ]
    texts = tmp_path / "applications.json"
    texts.write_text(json.dumps(extract))
    lines = [line for line in _policy_lines() if line.case_id != _FRESH[0][0]]
    # The labeler's topic call on the policy-only row is discarded, not a relabel.
    lines = [
        line.model_copy(update={"label": "tax"}) if line.case_id == fresh_case else line
        for line in lines
    ]
    labels = tmp_path / "labels.jsonl"
    labels.write_text("".join(line.model_dump_json() + "\n" for line in lines))

    result = runner.invoke(
        app,
        [
            "qp-topics",
            "--frame",
            "applications",
            "--labels",
            str(labels),
            "--texts",
            str(texts),
            "--labeler",
            "claude-code/test",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "policy areas (against policy-area-v1 hand labels, not accuracy)" in result.output
    written = read_model(qp_topics.application_labels_path(data), QpTopicApplicationLabels)
    row = {entry.case_id: entry for entry in written.entries}[fresh_case]
    standing = {entry.case_id: entry for entry in prior.entries}[fresh_case]
    assert row.label == standing.label
    assert row.batch == standing.batch
    assert (row.policy_area, row.policy_source, row.policy_batch) == ("firearms", "labeler", 2)
    assert written.batches[-1].measured == len(_REFERENCE)
    assert row.docket_number == fresh_docket
    validated = runner.invoke(app, ["validate", str(data / "qp-topics")])
    assert validated.exit_code == 0, validated.output


def _rows(policy_row: bool) -> list[ApplicationExtractRow]:
    return [
        ApplicationExtractRow(
            case_id=str(row["case_id"]),
            docket_number=str(row["docket_number"]),
            input_kind="docket-only",
            caption="A v. United States",
            lower_court=None,
            text="",
            entries=(),
            policy_row=policy_row,
        )
        for row in _extract()
    ]


def test_a_converged_frame_still_cuts_a_batch_while_policy_areas_are_owed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = tmp_path / "data"
    write_json(qp_topics.application_reference_path(data), _block())
    write_json(qp_topics.application_labels_path(data), _artifact())
    monkeypatch.setattr(cli, "policy_areas", lambda: _HAND)
    out = tmp_path / "extract.json"

    rows = cli._labeling_batch(
        _rows(policy_row=True), data_root=data, out=out, scope="test", applications=True
    )

    assert rows is not None
    only = sorted(row.case_id for row in rows if row.policy_only)
    # The topic batch is the reference block; the two fresh rows return for their area.
    assert only == sorted(case_id for case_id, _ in _FRESH)
    assert len(rows) == len(_REFERENCE) + len(_FRESH)
    # With no policy row owed, the converged frame stands down as before.
    standing = cli._labeling_batch(
        _rows(policy_row=False),
        data_root=data,
        out=out,
        scope="test",
        applications=True,
        converged_ok=True,
    )
    assert standing is None
