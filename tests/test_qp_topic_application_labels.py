"""The application labels artifact: how an application batch is cut, measured and accrued."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline import qp_topics
from fedcourtsai.pipeline.qp_topics import (
    APPLICATION_BATCH_ORDER_SEED,
    QpText,
    QpTopicError,
    application_stratum_key,
    build_application_labels,
    derive_label_batch,
)
from fedcourtsai.schemas import (
    QpTopicApplicationLabels,
    QpTopicApplicationReference,
    QpTopicLabel,
    QpTopicLabelEntry,
)
from fedcourtsai.serialize import read_model, write_json

runner = CliRunner()

# Ten reference rows and two labeler rows: enough reference for one miss to
# leave the rate on the gate's right side.
_REFERENCE = [(f"scotus/{n}", f"25A{n}", "immigration") for n in range(10, 20)]
_FRESH = [("scotus/30", "24A30"), ("scotus/31", "25A31")]


def _block(rows: list[tuple[str, str, str]] = _REFERENCE) -> QpTopicApplicationReference:
    return QpTopicApplicationReference(
        cases=len(rows),
        entries=[
            {"case_id": c, "docket_number": d, "input_kind": "docket-only", "label": label}
            for c, d, label in rows
        ],
    )


def _line(case_id: str, docket: str, label: QpTopicLabel) -> QpTopicLabelEntry:
    return QpTopicLabelEntry(case_id=case_id, docket_number=docket, label=label)


def _extract() -> list[dict[str, object]]:
    rows = [(c, d) for c, d, _ in _REFERENCE] + _FRESH
    return [
        {
            "case_id": c,
            "docket_number": d,
            "input_kind": "application-text" if c == "scotus/31" else "docket-only",
            "caption": "A v. B",
            "lower_court": None,
            "text": "The Second Amendment protects the right." if c == "scotus/31" else "",
            "entries": [],
        }
        for c, d in rows
    ]


def _lines(miss: int = 1) -> list[QpTopicLabelEntry]:
    lines = [
        _line(c, d, "criminal-law" if index < miss else "immigration")
        for index, (c, d, _) in enumerate(_REFERENCE)
    ]
    return [*lines, _line(*_FRESH[0], "civil-procedure"), _line(*_FRESH[1], "firearms")]


def _texts() -> dict[str, QpText]:
    return {
        str(row["case_id"]): QpText(str(row["docket_number"]), str(row["text"]))
        for row in _extract()
    }


def _kinds() -> dict[str, qp_topics.InputKind]:
    kinds: dict[str, qp_topics.InputKind] = {}
    for row in _extract():
        kinds[str(row["case_id"])] = (
            "application-text" if row["input_kind"] == "application-text" else "docket-only"
        )
    return kinds


def test_the_application_batch_force_includes_the_block_and_strata_are_terms() -> None:
    frame = [(c, d) for c, d, _ in _REFERENCE] + _FRESH
    batch = derive_label_batch(
        frame=frame,
        reference=_block(),
        labeled=(),
        ceiling=11,
        stratum=application_stratum_key,
        seed=APPLICATION_BATCH_ORDER_SEED,
    )
    assert batch.reference_rows == 10
    assert batch.fill == 1
    assert [(row.key, row.pool) for row in batch.strata] == [
        ("2024/application", 1),
        ("2025/application", 1),
    ]
    assert application_stratum_key("not a docket") == qp_topics.UNPARSED_STRATUM


def test_reference_rows_publish_the_block_and_every_row_carries_its_input_kind() -> None:
    artifact = build_application_labels(
        entries=_lines(),
        texts=_texts(),
        input_kinds=_kinds(),
        reference=_block(),
        labeler="claude-code/test",
    )
    assert artifact.vocabulary == "qp-topic-v1"
    assert artifact.agreement.overall_n == 10
    assert artifact.agreement.overall_agree == 9
    assert artifact.agreement.gate_passed
    by_case = {entry.case_id: entry for entry in artifact.entries}
    # The labeler's miss on a reference row is measured, never published.
    assert by_case["scotus/10"].label == "immigration"
    assert by_case["scotus/10"].source == "reference"
    assert by_case["scotus/31"].input_kind == "application-text"
    assert by_case["scotus/30"].input_kind == "docket-only"
    assert artifact.batches[-1].labeler_rows == 2
    # The shadow rules read the stored application text, so only the row with
    # text can fire.
    assert (artifact.shadow.fired, artifact.shadow.disagreements) == (1, 0)


def test_a_second_batch_keeps_standing_rows_and_refuses_a_relabel() -> None:
    first = build_application_labels(
        entries=_lines(),
        texts=_texts(),
        input_kinds=_kinds(),
        reference=_block(),
        labeler="claude-code/test",
    )
    reference_only = [line for line in _lines() if line.case_id not in {"scotus/30", "scotus/31"}]
    fresh = _line("scotus/32", "25A32", "tax")
    texts = {k: v for k, v in _texts().items() if k not in {"scotus/30", "scotus/31"}}
    texts["scotus/32"] = QpText("25A32", "")
    kinds = {case_id: _kinds().get(case_id, "docket-only") for case_id in texts}
    second = build_application_labels(
        entries=[*reference_only, fresh],
        texts=texts,
        input_kinds=kinds,
        reference=_block(),
        labeler="claude-code/next",
        prior=first,
    )
    assert second.cases == 13
    assert [row.batch for row in second.batches] == [1, 2]
    assert {entry.case_id: entry.input_kind for entry in second.entries}["scotus/31"] == (
        "application-text"
    )
    with pytest.raises(QpTopicError, match="labeled once"):
        build_application_labels(
            entries=_lines(),
            texts=_texts(),
            input_kinds=_kinds(),
            reference=_block(),
            labeler="claude-code/again",
            prior=first,
        )


def test_an_extract_row_without_an_input_kind_is_refused() -> None:
    kinds = _kinds()
    kinds.pop("scotus/30")
    with pytest.raises(QpTopicError, match="input_kind"):
        build_application_labels(
            entries=_lines(),
            texts=_texts(),
            input_kinds=kinds,
            reference=_block(),
            labeler="claude-code/test",
        )


def _seed_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, miss: int) -> tuple[Path, Path]:
    data = tmp_path / "data"
    write_json(qp_topics.application_reference_path(data), _block())
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    texts = tmp_path / "applications.json"
    texts.write_text(json.dumps(_extract()))
    labels = tmp_path / "labels.jsonl"
    labels.write_text("".join(line.model_dump_json() + "\n" for line in _lines(miss)))
    return texts, labels


def test_the_command_measures_against_the_block_and_writes_the_application_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    texts, labels = _seed_run(tmp_path, monkeypatch, miss=1)
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
            "--frame-rows",
            "12",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "vs the application reference block" in result.output
    written = qp_topics.application_labels_path(tmp_path / "data")
    artifact = read_model(written, QpTopicApplicationLabels)
    assert artifact.batches[-1].frame_rows == 12
    # The petition artifact is untouched.
    assert not qp_topics.labels_path(tmp_path / "data").exists()
    validated = runner.invoke(app, ["validate", str(written.parent)])
    assert validated.exit_code == 0, validated.output


def test_the_command_refuses_to_write_below_the_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    texts, labels = _seed_run(tmp_path, monkeypatch, miss=3)
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
    assert result.exit_code == 1
    assert "of the application reference block" in result.stderr
    assert not qp_topics.application_labels_path(tmp_path / "data").exists()
