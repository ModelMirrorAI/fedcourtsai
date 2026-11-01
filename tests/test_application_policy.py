"""Policy areas read by the application labeler (policy-area-v2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.cli import app
from fedcourtsai.pipeline import policy_area as policy_area_module
from fedcourtsai.pipeline import qp_topics
from fedcourtsai.pipeline.application_policy import (
    PolicyBatch,
    accrue_policy,
    derive_policy_rows,
    label_prompt_sha256,
    measure_policy,
    policy_only_rows,
    read_policy_rows,
    refusal_hold,
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

_SHA = "a" * 64


def _hand_area(index: int) -> PolicyAreaLabel:
    return "immigration" if index < len(_REFERENCE) // 2 else "health"


# Every topic-reference row is also hand-labeled for policy, in two areas, so a
# constant labeler's floor is one half.
_HAND: dict[str, PolicyLabel] = {
    docket.upper(): PolicyLabel(_hand_area(index), "hand", index == 0)
    for index, (_, docket, _) in enumerate(_REFERENCE)
}


def _policy_lines(miss: int = 0) -> list[QpTopicApplicationLabelEntry]:
    """The topic lines, each carrying a policy area: ``miss`` hand rows say `other`."""
    out: list[QpTopicApplicationLabelEntry] = []
    for index, line in enumerate(_lines(miss=0)):
        if line.case_id == _FRESH[1][0]:
            area: PolicyAreaLabel = "firearms"
        elif line.case_id == _FRESH[0][0]:
            area = "other"
        else:
            area = "other" if index < miss else _hand_area(index)
        out.append(QpTopicApplicationLabelEntry(**line.model_dump(), policy_area=area))
    return out


def _all_rows() -> set[str]:
    return set(_texts())


def _artifact() -> QpTopicApplicationLabels:
    return build_application_labels(
        entries=_lines(miss=0),
        texts=_texts(),
        input_kinds=_kinds(),
        reference=_block(),
        labeler="claude-code/test",
    )


def _accrued(miss: int, sha: str | None = _SHA) -> QpTopicApplicationLabels:
    measured = measure_policy(
        entries=_policy_lines(miss=miss), policy_rows=_all_rows(), hand=_HAND, prompt_sha256=sha
    )
    assert measured is not None
    accrued, _ = accrue_policy(_artifact(), agreement=measured[0], areas=measured[1], hand=_HAND)
    return accrued


def _frame(flag: bool = True) -> list[tuple[str, str, bool]]:
    return [(c, d, flag) for c, d, _ in _REFERENCE] + [(c, d, flag) for c, d in _FRESH]


def test_a_batch_owing_no_policy_area_adds_no_rows() -> None:
    batch = derive_policy_rows(
        frame=_frame(flag=False),
        topic_batch=[],
        artifact=None,
        hand=_HAND,
        budget=100,
        seed="s",
        prompt_sha256=_SHA,
    )
    assert batch.case_ids == ()
    assert batch.owed == 0
    assert not batch.asks


def test_a_batch_owing_areas_carries_the_hand_rows_and_backfills_up_to_the_budget() -> None:
    # Nothing new in the topic batch: every published policy row lacks an area.
    batch = derive_policy_rows(
        frame=_frame(),
        topic_batch=[],
        artifact=_artifact(),
        hand=_HAND,
        budget=11,
        seed="s",
        prompt_sha256=_SHA,
    )
    assert batch.owed == 12
    assert batch.reference_rows == 10
    assert batch.backfill == 1
    assert batch.remaining == 1
    assert len(batch.case_ids) == 11
    assert batch.asks


def test_a_budget_too_small_for_the_hand_rows_holds_the_areas_rather_than_failing() -> None:
    batch = derive_policy_rows(
        frame=_frame(),
        topic_batch=[],
        artifact=_artifact(),
        hand=_HAND,
        budget=5,
        seed="s",
        prompt_sha256=_SHA,
    )
    assert batch.case_ids == ()
    assert not batch.asks
    assert batch.held is not None
    assert "hand-labeled policy row" in batch.held


def test_a_frame_short_of_the_hand_set_holds_the_areas() -> None:
    wider = {**_HAND, "26A1": PolicyLabel("health", "hand", False), "26A2": _HAND["25A10"]}
    batch = derive_policy_rows(
        frame=_frame(),
        topic_batch=[],
        artifact=_artifact(),
        hand=wider,
        budget=100,
        seed="s",
        prompt_sha256=_SHA,
    )
    assert not batch.asks
    assert batch.held is not None
    assert "coverage floor" in batch.held


def test_a_refused_measurement_holds_until_the_prompt_changes() -> None:
    refused = _accrued(miss=3)
    assert refusal_hold(refused, _SHA)
    assert refusal_hold(refused, None)
    assert not refusal_hold(refused, "b" * 64)
    assert not refusal_hold(_accrued(miss=1), _SHA)
    assert not refusal_hold(_artifact(), _SHA)
    held = derive_policy_rows(
        frame=_frame(),
        topic_batch=[],
        artifact=refused,
        hand=_HAND,
        budget=100,
        seed="s",
        prompt_sha256=_SHA,
    )
    assert not held.asks
    assert held.held is not None
    assert "refused" in held.held
    revised = derive_policy_rows(
        frame=_frame(),
        topic_batch=[],
        artifact=refused,
        hand=_HAND,
        budget=100,
        seed="s",
        prompt_sha256="b" * 64,
    )
    assert revised.asks


def test_the_measurement_counts_agreement_per_area_and_drops_off_frame_areas() -> None:
    rows = _all_rows() - {_FRESH[0][0]}
    measured = measure_policy(
        entries=_policy_lines(miss=1), policy_rows=rows, hand=_HAND, prompt_sha256=_SHA
    )
    assert measured is not None
    agreement, areas = measured
    assert (agreement.agree, agreement.n, agreement.uncovered) == (9, 10, 0)
    assert agreement.off_frame == 1
    assert agreement.floor == 0.5
    assert (agreement.named_agree, agreement.named_n) == (9, 10)
    # The one uncertain hand row is the one missed.
    assert (agreement.certain_agree, agreement.certain_n) == (9, 9)
    assert agreement.gate_passed
    assert agreement.prompt_sha256 == _SHA
    assert [(s.area, s.agree, s.n, s.labeled_other) for s in agreement.per_area] == [
        ("immigration", 4, 5, 1),
        ("health", 5, 5, 0),
    ]
    assert _FRESH[0][0] not in areas
    assert areas[_FRESH[1][0]] == "firearms"


def test_the_gate_refuses_low_agreement_and_a_labeler_no_better_than_constant() -> None:
    low = measure_policy(entries=_policy_lines(miss=3), policy_rows=_all_rows(), hand=_HAND)
    assert low is not None
    assert not low[0].gate_passed
    one_area = {key: PolicyLabel("immigration", "hand", False) for key in _HAND}
    constant = [line.model_copy(update={"policy_area": "immigration"}) for line in _policy_lines()]
    flat = measure_policy(entries=constant, policy_rows=_all_rows(), hand=one_area)
    assert flat is not None
    assert flat[0].rate == 1.0
    assert not flat[0].gate_passed


def test_the_gate_refuses_a_batch_short_of_the_hand_set() -> None:
    wider = {**_HAND, "26A1": PolicyLabel("health", "hand", False), "26A2": _HAND["25A10"]}
    measured = measure_policy(entries=_policy_lines(), policy_rows=_all_rows(), hand=wider)
    assert measured is not None
    assert measured[0].rate == 1.0
    assert not measured[0].gate_passed


def test_a_passing_measurement_publishes_hand_and_labeler_areas_once() -> None:
    artifact = _artifact()
    measured = measure_policy(entries=_policy_lines(miss=1), policy_rows=_all_rows(), hand=_HAND)
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
    assert accrued.batches[-1].policy_gate_passed is True
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
    accrued = _accrued(miss=3)

    assert accrued.policy_agreement is None
    assert all(entry.policy_area is None for entry in accrued.entries)
    last = accrued.batches[-1]
    assert (last.policy_agree, last.policy_n, last.policy_published) == (7, 10, 0)
    assert last.policy_gate_passed is False
    assert last.policy_prompt_sha256 == _SHA


def test_a_later_topic_batch_keeps_the_published_areas_and_the_standing_measurement() -> None:
    accrued = _accrued(miss=1)

    fresh = {case_id for case_id, _ in _FRESH}
    later = build_application_labels(
        entries=[line for line in _lines(miss=0) if line.case_id not in fresh],
        texts={c: t for c, t in _texts().items() if c not in fresh},
        input_kinds={c: k for c, k in _kinds().items() if c not in fresh},
        reference=_block(),
        labeler="claude-code/test",
        prior=accrued,
    )

    assert later.policy_agreement == accrued.policy_agreement
    before = {e.case_id: (e.policy_area, e.policy_source, e.policy_batch) for e in accrued.entries}
    after = {e.case_id: (e.policy_area, e.policy_source, e.policy_batch) for e in later.entries}
    assert after == before
    assert after[_REFERENCE[0][0]] == ("immigration", "reference", 1)


def test_the_cut_reads_v2_only_once_a_measurement_passed() -> None:
    assert policy_source(None).rule_version == POLICY_AREA_RULE_VERSION
    assert policy_source(_artifact()).rule_version == POLICY_AREA_RULE_VERSION
    assert policy_source(_accrued(miss=3)).rule_version == POLICY_AREA_RULE_VERSION

    source = policy_source(_accrued(miss=1))

    assert source.rule_version == POLICY_AREA_V2_RULE_VERSION
    label = source.label(_FRESH[1][1].lower())
    assert label is not None
    assert (label.area, label.source) == ("firearms", "labeler")


def test_v2_keeps_every_hand_label_including_dockets_outside_the_artifact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    outside = PolicyLabel("elections-census", "hand", False)
    monkeypatch.setattr(policy_area_module, "policy_areas", lambda: {**_HAND, "19A9": outside})

    source = policy_source(_accrued(miss=1))

    label = source.label("19A9")
    assert label is not None
    assert (label.area, label.source) == ("elections-census", "reference")


def test_a_published_row_outside_the_reference_block_is_policy_only() -> None:
    prior = _artifact()
    ids = [c for c, _, _ in _REFERENCE] + [c for c, _ in _FRESH] + ["scotus/99"]
    assert policy_only_rows(ids, prior, _block()) == {c for c, _ in _FRESH}
    assert policy_only_rows(ids, None, _block()) == set()


def test_the_extract_marks_policy_rows_and_nothing_else(tmp_path: Path) -> None:
    path = tmp_path / "extract.json"
    path.write_text(
        json.dumps([{"case_id": "scotus/1", "policy_row": True}, {"case_id": "scotus/2"}])
    )
    assert read_policy_rows(path) == {"scotus/1"}
    path.write_text(json.dumps([{"case_id": "scotus/1", "policy_row": "yes"}]))
    with pytest.raises(QpTopicError, match="policy_row must be a boolean"):
        read_policy_rows(path)


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
    # Nothing in the extract says which; the measurement derives it.
    fresh_case, fresh_docket = _FRESH[1]
    extract = [{**row, "policy_row": True} for row in _extract() if row["case_id"] != _FRESH[0][0]]
    assert all("policy_only" not in row for row in extract)
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
    assert written.batches[-1].policy_prompt_sha256 == label_prompt_sha256()
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
    # The topic batch is the reference block; the two fresh rows return for their area,
    # flagged like every other policy row.
    assert len(rows) == len(_REFERENCE) + len(_FRESH)
    assert {row.case_id for row in rows} >= {case_id for case_id, _ in _FRESH}
    assert all(isinstance(row, ApplicationExtractRow) and row.policy_row for row in rows)
    assert all("policy_only" not in row.as_json() for row in rows)
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


def test_a_batch_asking_no_area_clears_every_policy_row() -> None:
    rows = _rows(policy_row=True)
    quiet = PolicyBatch(case_ids=(), owed=3, reference_rows=0, backfill=0, remaining=3, held="x")

    cleared = cli._with_policy(rows[:4], rows, quiet)

    assert [row.case_id for row in cleared] == [row.case_id for row in rows[:4]]
    assert not any(row.policy_row for row in cleared)
    asking = PolicyBatch(
        case_ids=(rows[5].case_id,), owed=1, reference_rows=0, backfill=1, remaining=0
    )
    added = cli._with_policy(rows[:4], rows, asking)
    assert [row.case_id for row in added] == [*(r.case_id for r in rows[:4]), rows[5].case_id]
    assert all(row.policy_row for row in added)
