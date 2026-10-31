"""The reference-only replicate mode: its batch, its measurement, its record and its pool.

A replicate labels a frame's reference rows alone and publishes nothing, so
repeat replicates read identical inputs and the spread of their agreement is the
labeler's run-to-run variation (``docs/qp-topic.md``).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline import qp_topics
from fedcourtsai.pipeline.qp_replicates import (
    Replicate,
    ReplicateError,
    chi2_sf,
    replicate_from_labels,
    replicates_from_records,
    spread,
)
from fedcourtsai.pipeline.qp_topics import (
    APPLICATION_BATCH_ORDER_SEED,
    QpText,
    QpTopicError,
    application_stratum_key,
    derive_label_batch,
    measure_replicate,
)
from fedcourtsai.schemas import (
    QpTopicApplicationReference,
    QpTopicLabel,
    QpTopicLabelEntry,
    QpTopicReplicate,
    QpTopicRunSpend,
)
from fedcourtsai.serialize import read_model, write_json

runner = CliRunner()

# Ten reference rows, the first two read from application text.
_REFERENCE = [(f"scotus/{n}", f"25A{n}", "immigration") for n in range(10, 20)]
_FRESH = [("scotus/30", "24A30"), ("scotus/31", "25A31")]


def _kind(case_id: str) -> str:
    return "application-text" if case_id in {"scotus/10", "scotus/11"} else "docket-only"


def _block() -> QpTopicApplicationReference:
    return QpTopicApplicationReference(
        cases=len(_REFERENCE),
        entries=[
            {"case_id": c, "docket_number": d, "input_kind": _kind(c), "label": label}
            for c, d, label in _REFERENCE
        ],
    )


def _line(case_id: str, docket: str, label: QpTopicLabel) -> QpTopicLabelEntry:
    return QpTopicLabelEntry(case_id=case_id, docket_number=docket, label=label)


def _lines(miss: frozenset[str] = frozenset()) -> list[QpTopicLabelEntry]:
    return [
        _line(c, d, "unclassifiable" if c in miss else "immigration") for c, d, _ in _REFERENCE
    ]


def _texts(rows: list[tuple[str, str]] | None = None) -> dict[str, QpText]:
    pairs = rows if rows is not None else [(c, d) for c, d, _ in _REFERENCE]
    return {c: QpText(d, "") for c, d in pairs}


def test_a_replicate_batch_is_the_reference_rows_alone() -> None:
    frame = [(c, d) for c, d, _ in _REFERENCE] + _FRESH
    batch = derive_label_batch(
        frame=frame,
        reference=_block(),
        labeled=set(),
        stratum=application_stratum_key,
        seed=APPLICATION_BATCH_ORDER_SEED,
        reference_only=True,
    )
    assert batch.case_ids == tuple(sorted(c for c, _, _ in _REFERENCE))
    assert batch.fill == 0
    # The pool is still counted, so the arithmetic names the frame it came from.
    assert batch.pool == len(_FRESH)
    assert batch.reference_covered == 1.0


def test_a_replicate_is_measured_row_by_row_in_reference_order() -> None:
    agreement, replicate = measure_replicate(
        entries=_lines(frozenset({"scotus/10", "scotus/15"})),
        texts=_texts(),
        reference=_block(),
        reference_sha256="a" * 64,
    )
    assert (agreement.overall_agree, agreement.overall_n) == (8, 10)
    assert replicate.matches == "0111101111"
    assert replicate.unclassifiable == 2
    kinds = {row.input_kind: (row.agree, row.n) for row in replicate.per_input_kind}
    assert kinds == {"application-text": (1, 2), "docket-only": (7, 8)}


def test_a_replicate_refuses_an_extract_row_outside_the_reference() -> None:
    lines = [*_lines(), _line(*_FRESH[0], "civil-procedure")]
    rows = [(c, d) for c, d, _ in _REFERENCE] + [_FRESH[0]]
    with pytest.raises(QpTopicError, match="not a replicate"):
        measure_replicate(
            entries=lines, texts=_texts(rows), reference=_block(), reference_sha256="a" * 64
        )


def test_the_replicate_record_is_bound_to_its_counts() -> None:
    with pytest.raises(ValueError, match="one character per reference entry"):
        QpTopicReplicate(
            reference_sha256="a" * 64, reference_entries=3, matches="11", unclassifiable=0
        )
    with pytest.raises(ValueError, match="per-kind n sum"):
        QpTopicReplicate(
            reference_sha256="a" * 64,
            reference_entries=2,
            matches="10",
            unclassifiable=0,
            per_input_kind=[{"input_kind": "docket-only", "agree": 1, "n": 1}],
        )


def _seed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path]:
    data = tmp_path / "data"
    write_json(qp_topics.application_reference_path(data), _block())
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data))
    texts = tmp_path / "replicate.json"
    texts.write_text(
        json.dumps(
            [
                {
                    "case_id": c,
                    "docket_number": d,
                    "input_kind": _kind(c),
                    "caption": "A v. B",
                    "lower_court": None,
                    "text": "",
                    "entries": [],
                }
                for c, d, _ in _REFERENCE
            ]
        )
    )
    labels = tmp_path / "labels.jsonl"
    # Three misses: 70%, under the gate, which a replicate records rather than refuses.
    miss = frozenset({"scotus/10", "scotus/12", "scotus/13"})
    labels.write_text("".join(line.model_dump_json() + "\n" for line in _lines(miss)))
    return data, texts, labels


def test_the_command_records_a_replicate_and_writes_no_labels(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, texts, labels = _seed(tmp_path, monkeypatch)
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
            "--agreement-out",
            str(tmp_path / "agreement.json"),
            "--replicate-out",
            str(tmp_path / "replicate.out.json"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "would not clear" in result.output
    assert not qp_topics.application_labels_path(data).exists()
    replicate = read_model(tmp_path / "replicate.out.json", QpTopicReplicate)
    digest = hashlib.sha256(qp_topics.application_reference_path(data).read_bytes()).hexdigest()
    assert replicate.reference_sha256 == digest
    assert replicate.matches == "0100111111"


def _execution_file(tmp_path: Path) -> Path:
    path = tmp_path / "execution.json"
    usage = {
        "input_tokens": 1_000,
        "output_tokens": 50_000,
        "cache_read_input_tokens": 2_000_000,
        "cache_creation_input_tokens": 100_000,
    }
    path.write_text(json.dumps([{"type": "system"}, {"type": "result", "usage": usage}]))
    return path


def _record(tmp_path: Path, run_id: str, *extra: str) -> Any:
    return runner.invoke(
        app,
        [
            "qp-topic-spend",
            "--execution-file",
            str(_execution_file(tmp_path)),
            "--frame",
            "applications",
            "--run-id",
            run_id,
            "--run-attempt",
            "1",
            "--model",
            "claude-opus-5-5",
            "--batch-rows",
            "10",
            "--label-lines",
            "10",
            "--agreement-file",
            str(tmp_path / "agreement.json"),
            *extra,
        ],
    )


def test_a_replicate_run_records_as_replicate_and_the_pool_reads_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, texts, labels = _seed(tmp_path, monkeypatch)
    measured = runner.invoke(
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
            "--agreement-out",
            str(tmp_path / "agreement.json"),
            "--replicate-out",
            str(tmp_path / "replicate.out.json"),
        ],
    )
    assert measured.exit_code == 0, measured.output
    for run_id in ("101", "102"):
        result = _record(tmp_path, run_id, "--replicate-file", str(tmp_path / "replicate.out.json"))
        assert result.exit_code == 0, result.output
    record = read_model(qp_topics.run_spend_path(data, "101", 1), QpTopicRunSpend)
    assert record.outcome == "replicate"
    assert record.replicate is not None and (record.agree, record.n) == (7, 10)
    validated = runner.invoke(app, ["validate", str(data / "qp-topics")])
    assert validated.exit_code == 0, validated.output
    # A replicate is never a published run.
    refused = _record(
        tmp_path, "103", "--published", "--replicate-file", str(tmp_path / "replicate.out.json")
    )
    assert refused.exit_code == 2
    pooled = runner.invoke(
        app,
        ["qp-topic-replicates", "--frame", "applications", "--out", str(tmp_path / "s.json")],
    )
    assert pooled.exit_code == 0, pooled.output
    assert "2 run(s) over 10 reference item(s)" in pooled.output
    report = json.loads((tmp_path / "s.json").read_text())
    assert report["rates"] == [0.7, 0.7] and report["run_sd"] == 0.0
    assert report["cochran_q"] is None  # no item flipped between identical runs


def test_a_record_against_another_reference_is_left_out_of_the_pool() -> None:
    def run(run_id: str, sha: str, model: str = "claude-opus-5-5") -> QpTopicRunSpend:
        return QpTopicRunSpend(
            frame="petitions",
            run_id=run_id,
            run_attempt=1,
            labeler=f"claude-code/{model}",
            model=model,
            outcome="replicate",
            batch_rows=3,
            label_lines=3,
            agree=2,
            n=3,
            rate=2 / 3,
            floor=0.5,
            recorded_at="2026-11-01T00:00:00Z",
            input_tokens=1,
            output_tokens=1,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
            estimated_cost_usd=1.0,
            replicate={
                "reference_sha256": sha,
                "reference_entries": 3,
                "matches": "110",
                "unclassifiable": 0,
            },
        )

    pooled, skipped = replicates_from_records(
        [run("2", "a" * 64), run("1", "a" * 64), run("3", "b" * 64), run("4", "a" * 64, "x")],
        frame="petitions",
        model="claude-opus-5-5",
        reference_sha256="a" * 64,
    )
    assert [r.name for r in pooled] == ["run 1-1", "run 2-1"]
    assert [r.run_id for r in skipped] == ["3", "4"]


def test_the_chi_square_tail_matches_known_quantiles() -> None:
    assert chi2_sf(3.841458820694124, 1) == pytest.approx(0.05, abs=1e-9)
    assert chi2_sf(5.991464547107979, 2) == pytest.approx(0.05, abs=1e-9)
    assert chi2_sf(7.814727903251178, 3) == pytest.approx(0.05, abs=1e-9)
    assert chi2_sf(0.5843743741, 3) == pytest.approx(0.9, abs=1e-8)
    # The df=3 closed form, deep in the tail where the continued fraction runs.
    tail = math.erfc(math.sqrt(15.0)) + math.sqrt(60.0 / math.pi) * math.exp(-15.0)
    assert chi2_sf(30.0, 3) == pytest.approx(tail, rel=1e-9)
    assert chi2_sf(0.0, 4) == 1.0


def test_the_spread_separates_run_level_from_item_level_variation() -> None:
    # Four items, three runs. Item 0 always matches, item 3 never; items 1 and 2
    # flip. Run rates 3/4, 2/4, 1/4.
    runs = [
        Replicate("a", "1110", 0),
        Replicate("b", "1100", 0),
        Replicate("c", "1000", 1),
    ]
    result = spread(runs)
    assert result.rates == (0.75, 0.5, 0.25)
    assert result.mean == pytest.approx(0.5)
    assert result.run_sd == pytest.approx(0.25)
    # Item-level term: items 1 and 2 each have p = 2/3 and 1/3; k/(k-1) p(1-p)
    # is 1/3 for both, so (2/3) / n^2 = 1/24.
    assert result.item_noise_var == pytest.approx(1 / 24)
    assert result.run_component_var == pytest.approx(0.0625 - 1 / 24)
    assert (result.always, result.never, result.flip) == (1, 1, 2)
    # Cochran's Q: (k-1)(k sum C^2 - N^2) / (k N - sum R^2) = 2 (3*14 - 36) / (18 - 14) = 3.
    assert result.cochran_q == pytest.approx(3.0)
    assert result.p_value == pytest.approx(math.exp(-1.5))
    assert result.unclassifiable_shares == (0.0, 0.0, 0.25)


def test_the_spread_reads_only_items_every_run_compared() -> None:
    result = spread([Replicate("a", "11-", 0), Replicate("b", "101", 0)])
    assert result.items == 2
    with pytest.raises(ReplicateError, match="at least two"):
        spread([Replicate("a", "11", 0)])
    with pytest.raises(ReplicateError, match="different lengths"):
        spread([Replicate("a", "11", 0), Replicate("b", "1", 0)])


def test_saved_labels_are_read_on_the_reference_rows_they_hold() -> None:
    reference = [("scotus/1", "tax", ""), ("scotus/2", "firearms", ""), ("scotus/3", "tax", "")]
    replicate = replicate_from_labels(
        "saved", {"scotus/1": "tax", "scotus/3": "unclassifiable", "scotus/9": "tax"}, reference
    )
    assert replicate.matches == "1-0"
    assert replicate.unclassifiable == 1
    assert replicate.kinds == ()
