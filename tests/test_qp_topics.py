"""The qp-topic labeler machinery: shadow rules, agreement, and the gated builder.

Offline throughout — the shadow rules read text, the agreement reads two label
sets, and the CLI round-trip runs against a tmp reference set. Nothing here
touches the corpus, so a rule change surfaces in seconds.

The shadow fixtures are **in-sample**: the positives are shortened reference
texts the rules were tuned to fire on and the negatives are the boundary texts
they were tuned to decline. They pin the tuned behaviour against regression;
they cannot detect that the tuning overfit, and a green suite is no evidence
about an unseen text (see :mod:`fedcourtsai.pipeline.qp_topics`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline.qp_topics import (
    AGREEMENT_GATE,
    COVERAGE_FLOOR,
    SUPPORT_FLOOR,
    TRIANGLE,
    QpText,
    QpTopicError,
    build_labels,
    measure_agreement,
    shadow_label,
)
from fedcourtsai.schemas import (
    QpTopicLabel,
    QpTopicLabelEntry,
    QpTopicLabels,
    QpTopicReference,
    QpTopicReferenceEntry,
)
from fedcourtsai.serialize import read_model, write_json

# Each rule's positives are shortened from reference texts it fires on; each
# negative is a text the vocabulary routes elsewhere and the rule must decline.
FIRES = [
    (
        "firearms",
        "Whether 18 U.S.C. § 922(g)(1) comports with the Second Amendment as applied to a "
        + "defendant whose most serious prior felony conviction is drug trafficking?",
    ),
    (
        # PDF line-break hyphenation is rejoined before the rule runs, and the
        # "Second and Fourteenth Amendments" form is the same claim as "Second
        # Amendment".
        "firearms",
        "Whether the Second and Fourteenth Amend-\nments guarantee the right to possess "
        + "AR-15 platform and similar semiautomatic rifles.",
    ),
    (
        # Firearms regulation, not a Second Amendment challenge — the label covers both.
        "firearms",
        "Does Massachusetts' firearms licensing regime, which grants a police colonel the "
        + "power to deny any nonresident traveler a temporary firearms license, violate the "
        + "constitutional rights of nonresident travelers?",
    ),
    (
        "intellectual-property",
        "Did the Fourth Circuit err in holding an online service provider secondarily liable "
        + "for copyright infringement committed by its users?",
    ),
    (
        "intellectual-property",
        "Whether trademark strength is a question of fact in a likelihood-of-confusion "
        + "analysis under the Lanham Act, 15 U.S.C. 1114.",
    ),
    (
        "tax",
        "Whether a proceeding under 26 U.S.C. 6330 for a pre-deprivation determination about "
        + "a levy proposed by the Internal Revenue Service becomes moot.",
    ),
    (
        "tax",
        "Whether the proceeds of a life-insurance policy taken out by a closely held "
        + "corporation should be a corporate asset for purposes of the federal estate tax.",
    ),
    (
        "employment-and-antidiscrimination",
        "Whether the burden of proof employers must satisfy to demonstrate an FLSA exemption "
        + "is a preponderance of the evidence or clear and convincing evidence.",
    ),
    (
        "employment-and-antidiscrimination",
        "Whether Title IX provides employees of federally funded educational institutions a "
        + "private right of action to sue for sex discrimination in employment.",
    ),
    (
        "employment-and-antidiscrimination",
        "Under the Employee Retirement Income Security Act of 1974 (ERISA), a plan fiduciary "
        + "is subject to a prudent man standard of care. Whether a complaint states a claim.",
    ),
]

DECLINES = [
    # The sentencing consequence of a firearms conviction is criminal-law, and
    # "firearm offenses" in background prose must not drag it into `firearms`.
    "The First Step Act significantly reduced the mandatory minimum sentences for several "
    + "federal drug and firearm offenses. The question presented is whether those reduced "
    + "sentences apply at a resentencing after the Act's enactment.",
    # "patently" is not a patent.
    "Whether the court of appeals applied a patently erroneous standard of review when it "
    + "affirmed the denial of a motion to suppress.",
    # A tax-foreclosure taking follows the takings routing, not `tax`.
    "Isabella County confiscated the estate's private home for approximately $2,200 in taxes "
    + "and fees. Whether keeping the surplus value violates the Takings Clause.",
    # Subject-flavored words with no cognizable question is `unclassifiable`.
    "In this voting rights appeal we all know the rally cry of 'no taxation without "
    + "representation' which gave birth to this great nation.",
    # Title IX framed on equal protection in schools is not an employment question.
    "Whether Title IX prevents a state from designating girls' and boys' sports teams based "
    + "on biological sex, and whether the Equal Protection Clause does.",
    # The FAA's seamen exemption is business-and-financial-regulation; "employment"
    # alone never fires the rule.
    "The Federal Arbitration Act exempts the contracts of employment of seamen, railroad "
    + "employees, or any other class of workers engaged in interstate commerce.",
]


@pytest.mark.parametrize(("label", "text"), FIRES)
def test_shadow_rules_fire_on_their_own_subject(label: str, text: str) -> None:
    assert shadow_label(text) == label


@pytest.mark.parametrize("text", DECLINES)
def test_shadow_rules_decline_the_boundary_texts(text: str) -> None:
    assert shadow_label(text) is None


def test_shadow_label_declines_when_two_rules_fire() -> None:
    # Precision-first: two subjects' statutes in one text is exactly the case a
    # keyword rule cannot arbitrate, so it declines rather than picking one.
    both = (
        "Whether the Second Amendment permits taxing firearm transfers under the federal "
        "excise tax imposed by the Internal Revenue Code."
    )
    assert shadow_label(both) is None


def _reference(*pairs: tuple[str, QpTopicLabel]) -> QpTopicReference:
    entries = [
        QpTopicReferenceEntry(case_id=case_id, docket_number=f"25-{index}", label=label)
        for index, (case_id, label) in enumerate(pairs)
    ]
    return QpTopicReference(cases=len(entries), entries=entries)


def _triangle_reference(rows: int) -> QpTopicReference:
    # `rows` cases per triangle label, ids ordered so the reference stays canonical.
    pairs = [
        (f"scotus/{index:03d}", label)
        for index, label in enumerate(label for label in TRIANGLE for _ in range(rows))
    ]
    return _reference(*pairs)


def test_agreement_counts_only_covered_reference_entries() -> None:
    reference = _reference(("scotus/1", "tax"), ("scotus/2", "tax"), ("scotus/3", "firearms"))
    agreement = measure_agreement({"scotus/1": "tax", "scotus/2": "firearms"}, reference)

    assert (agreement.overall_agree, agreement.overall_n) == (1, 2)
    assert agreement.overall_rate == 0.5
    assert agreement.uncovered == 1  # scotus/3 was never labeled, so it is not a disagreement


def test_per_label_rate_is_withheld_below_the_support_floor() -> None:
    reference = _triangle_reference(SUPPORT_FLOOR)
    labels = {entry.case_id: entry.label for entry in reference.entries}
    # One extra label with support of exactly one.
    thin = _reference(*[(e.case_id, e.label) for e in reference.entries], ("scotus/999", "tax"))
    labels["scotus/999"] = "tax"

    rows = {row.label: row for row in measure_agreement(labels, thin).per_label}
    assert rows["criminal-law"].n == SUPPORT_FLOOR
    assert rows["criminal-law"].rate == 1.0
    assert rows["tax"].n == 1
    assert rows["tax"].agree == 1
    assert rows["tax"].rate is None  # counted, never rated


def test_triangle_matrix_places_rows_columns_and_the_other_bucket() -> None:
    reference = _reference(
        ("scotus/1", "constitutional-rights"),
        ("scotus/2", "constitutional-rights"),
        ("scotus/3", "criminal-law"),
        ("scotus/4", "civil-procedure"),
    )
    labels = {
        "scotus/1": "constitutional-rights",  # diagonal
        "scotus/2": "criminal-law",  # off-diagonal, inside the triangle
        "scotus/3": "habeas-and-postconviction",  # outside the triangle
        "scotus/4": "civil-procedure",
    }
    rows = {row.reference: row for row in measure_agreement(labels, reference).triangle}

    assert [row.reference for row in measure_agreement(labels, reference).triangle] == list(
        TRIANGLE
    )
    assert rows["constitutional-rights"].counts == [1, 1, 0]
    assert rows["constitutional-rights"].other == 0
    assert rows["criminal-law"].counts == [0, 0, 0]
    assert rows["criminal-law"].other == 1  # the labeler left the triangle
    assert all(row.n == sum(row.counts) + row.other for row in rows.values())


def test_gate_turns_at_the_publication_threshold() -> None:
    reference = _reference(*[(f"scotus/{index:03d}", "tax") for index in range(100)])
    ids = [entry.case_id for entry in reference.entries]

    def labels(correct: int) -> dict[str, str]:
        return {
            case_id: "tax" if rank < correct else "firearms" for rank, case_id in enumerate(ids)
        }

    below = measure_agreement(labels(79), reference)
    assert below.overall_rate == pytest.approx(AGREEMENT_GATE - 0.01)
    assert below.gate_passed is False

    at = measure_agreement(labels(80), reference)
    assert at.overall_rate == pytest.approx(AGREEMENT_GATE)
    assert at.gate_passed is True


def test_agreement_of_an_empty_comparison_fails_the_gate() -> None:
    agreement = measure_agreement({}, _reference(("scotus/1", "tax")))
    assert agreement.overall_rate is None
    assert agreement.gate_passed is False
    assert agreement.uncovered == 1


def test_a_perfect_rate_over_a_sliver_of_the_reference_set_fails_the_gate() -> None:
    # Forgiving what was not covered must not pay for skipping it: without the
    # coverage floor, labeling the easiest handful correctly would license a
    # whole run of unmeasured labels.
    reference = _reference(*[(f"scotus/{index:03d}", "tax") for index in range(100)])
    thin = {entry.case_id: "tax" for entry in reference.entries[:5]}

    agreement = measure_agreement(thin, reference)

    assert agreement.overall_rate == 1.0
    assert agreement.overall_n == 5
    assert agreement.uncovered == 95
    assert agreement.gate_passed is False

    # At the floor exactly, a passing rate passes.
    at_floor = {entry.case_id: "tax" for entry in reference.entries[: int(COVERAGE_FLOOR * 100)]}
    assert measure_agreement(at_floor, reference).gate_passed is True


def _entry(case_id: str, docket_number: str, label: QpTopicLabel) -> QpTopicLabelEntry:
    return QpTopicLabelEntry(case_id=case_id, docket_number=docket_number, label=label)


def test_builder_rejects_duplicate_case_ids() -> None:
    with pytest.raises(QpTopicError, match="duplicate case_id"):
        build_labels(
            entries=[_entry("scotus/1", "25-1", "tax"), _entry("scotus/1", "25-1", "firearms")],
            texts={},
            reference=_reference(("scotus/1", "tax")),
            labeler="test",
        )


def test_builder_aborts_on_a_half_matching_reference_pair() -> None:
    reference = QpTopicReference(
        cases=1,
        entries=[QpTopicReferenceEntry(case_id="scotus/1", docket_number="25-1", label="tax")],
    )
    # Same case, different docket number: a mis-join would measure this label
    # against another case's text.
    with pytest.raises(QpTopicError, match="reference join mismatch"):
        build_labels(
            entries=[_entry("scotus/1", "25-999", "tax")],
            texts={},
            reference=reference,
            labeler="test",
        )
    # Same docket number, different case id — the mirror image.
    with pytest.raises(QpTopicError, match="reference join mismatch"):
        build_labels(
            entries=[_entry("scotus/999", "25-1", "tax")],
            texts={},
            reference=reference,
            labeler="test",
        )


def test_builder_counts_shadow_firings_and_disagreements() -> None:
    reference = _reference(("scotus/1", "tax"))
    labels = build_labels(
        entries=[
            _entry("scotus/1", "25-0", "tax"),
            _entry("scotus/2", "25-2", "criminal-law"),
            _entry("scotus/3", "25-3", "civil-procedure"),
        ],
        texts={
            "scotus/1": QpText(
                "25-0", "Whether the Internal Revenue Service may levy on the account."
            ),
            "scotus/2": QpText(
                "25-2", "Whether 18 U.S.C. § 922(g)(1) comports with the Second Amendment."
            ),
            "scotus/3": QpText(
                "25-3", "Whether the court of appeals had jurisdiction over the appeal."
            ),
        },
        reference=reference,
        labeler="test",
    )
    # Two rules fired; the firearms one disagreed with the agent's criminal-law
    # call, and the text no rule fired on is not counted either way — but it is
    # still in the denominator, so a zero can be told from a non-measurement.
    assert (labels.shadow.texts, labels.shadow.fired, labels.shadow.disagreements) == (3, 2, 1)
    assert [entry.case_id for entry in labels.entries] == ["scotus/1", "scotus/2", "scotus/3"]
    assert labels.cases == 3


def test_qp_corpus_refuses_to_write_the_extract_into_the_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The extract republishes stored petition text and enumerates the ingested
    # corpus; the refusal fires before the corpus is even opened, so no corpus
    # is needed to prove it.
    data_root = tmp_path / "data"
    data_root.mkdir()
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))

    result = CliRunner().invoke(
        app, ["qp-corpus", "--out", str(data_root / "qp-topics" / "x.json")]
    )

    assert result.exit_code == 2
    assert "refusing to write the extract inside the checkout" in result.output
    assert not (data_root / "qp-topics").exists()


def test_qp_corpus_refuses_to_write_anywhere_in_the_work_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Aiming outside `data/` is no escape: an untracked file anywhere in the
    # checkout is one `git add -A` from being committed.
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    in_tree = Path(__file__).resolve().parents[1] / "qp-extract-should-not-exist.json"

    result = CliRunner().invoke(app, ["qp-corpus", "--out", str(in_tree)])

    assert result.exit_code == 2
    assert "refusing to write the extract inside the checkout" in result.output
    assert not in_tree.exists()


def test_builder_requires_the_labels_and_the_extract_to_be_the_same_cases() -> None:
    # A partial run measures a prefix of case_id order, not a sample, and turns
    # the printed n into a membership probe on an outcome-encoding reference set.
    # A mis-wired --texts would report clean zeros having measured nothing.
    reference = _reference(("scotus/1", "tax"))
    text = QpText("25-0", "Whether the Internal Revenue Service may levy.")
    with pytest.raises(QpTopicError, match="not the same case set"):
        build_labels(
            entries=[_entry("scotus/1", "25-0", "tax")],
            texts={"scotus/other": text},
            reference=reference,
            labeler="test",
        )
    with pytest.raises(QpTopicError, match="left unlabeled"):
        build_labels(
            entries=[_entry("scotus/1", "25-0", "tax")],
            texts={"scotus/1": text, "scotus/2": text},
            reference=reference,
            labeler="test",
        )


def test_builder_aborts_when_the_labels_retype_the_extract_docket_number() -> None:
    with pytest.raises(QpTopicError, match="extract join mismatch"):
        build_labels(
            entries=[_entry("scotus/1", "25-999", "tax")],
            texts={"scotus/1": QpText("25-0", "Whether the levy proceeding is moot.")},
            reference=_reference(),
            labeler="test",
        )


def test_agreement_carries_the_constant_labeler_floor() -> None:
    # A 16-label agreement rate is unreadable without the rate a constant
    # labeler would score on the same entries.
    reference = _reference(
        ("scotus/1", "criminal-law"),
        ("scotus/2", "criminal-law"),
        ("scotus/3", "criminal-law"),
        ("scotus/4", "tax"),
    )
    labels = {entry.case_id: entry.label for entry in reference.entries}

    agreement = measure_agreement(labels, reference)

    assert agreement.overall_rate == 1.0
    assert agreement.floor == 0.75  # always-criminal-law scores 3 of 4
    assert measure_agreement({}, reference).floor is None


def _write_run(tmp_path: Path, entries: list[dict[str, object]]) -> tuple[Path, Path]:
    labels = tmp_path / "labels.jsonl"
    labels.write_text("".join(json.dumps(entry, sort_keys=True) + "\n" for entry in entries))
    texts = tmp_path / "qp.json"
    texts.write_text(
        json.dumps(
            [
                {"case_id": entry["case_id"], "docket_number": entry["docket_number"], "text": ""}
                for entry in entries
            ]
        )
    )
    return labels, texts


def _install_reference(data_root: Path, reference: QpTopicReference) -> None:
    write_json(data_root / "qp-topics" / "qp-topic-reference.json", reference)


def test_cli_writes_the_canonical_artifact_when_the_gate_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_root = tmp_path / "data"
    reference = _reference(*[(f"scotus/{index:03d}", "tax") for index in range(10)])
    _install_reference(data_root, reference)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    labels, texts = _write_run(
        tmp_path,
        [
            {"case_id": entry.case_id, "docket_number": entry.docket_number, "label": "tax"}
            for entry in reference.entries
        ],
    )

    result = CliRunner().invoke(
        app,
        ["qp-topics", "--labels", str(labels), "--texts", str(texts), "--labeler", "stub/model"],
    )

    assert result.exit_code == 0, result.output
    assert "agreement, not accuracy" in result.output
    written = data_root / "qp-topics" / "qp-topics.json"
    payload = json.loads(written.read_text())
    assert written.read_text() == json.dumps(payload, indent=2, sort_keys=True) + "\n"
    assert payload["labeler"] == "stub/model"
    assert payload["agreement"]["gate_passed"] is True


def test_cli_refuses_to_write_below_the_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_root = tmp_path / "data"
    reference = _reference(*[(f"scotus/{index:03d}", "tax") for index in range(10)])
    _install_reference(data_root, reference)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    labels, texts = _write_run(
        tmp_path,
        [
            {
                "case_id": entry.case_id,
                "docket_number": entry.docket_number,
                "label": "tax" if rank < 7 else "firearms",
            }
            for rank, entry in enumerate(reference.entries)
        ],
    )

    result = CliRunner().invoke(
        app,
        ["qp-topics", "--labels", str(labels), "--texts", str(texts), "--labeler", "stub/model"],
    )

    assert result.exit_code == 1
    assert "refusing to write" in result.output
    assert "70.0%" in result.output
    assert not (data_root / "qp-topics" / "qp-topics.json").exists()


def test_cli_rejects_a_label_outside_the_vocabulary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_root = tmp_path / "data"
    _install_reference(data_root, _reference(("scotus/000", "tax")))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    labels, texts = _write_run(
        tmp_path, [{"case_id": "scotus/000", "docket_number": "25-0", "label": "antitrust"}]
    )

    result = CliRunner().invoke(
        app,
        ["qp-topics", "--labels", str(labels), "--texts", str(texts), "--labeler", "stub/model"],
    )

    assert result.exit_code == 1
    assert "unusable label line" in result.output
    assert "antitrust" in result.output  # the offending line comes back with it


def test_written_artifact_round_trips_through_the_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_root = tmp_path / "data"
    reference = _reference(*[(f"scotus/{index:03d}", "tax") for index in range(10)])
    _install_reference(data_root, reference)
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    labels, texts = _write_run(
        tmp_path,
        [
            {
                "case_id": entry.case_id,
                "docket_number": entry.docket_number,
                "label": "tax",
                "secondary": "civil-procedure",
                "vehicle": True,
            }
            for entry in reference.entries
        ],
    )
    CliRunner().invoke(
        app,
        ["qp-topics", "--labels", str(labels), "--texts", str(texts), "--labeler", "stub/model"],
    )

    written = read_model(data_root / "qp-topics" / "qp-topics.json", QpTopicLabels)
    assert written.cases == len(written.entries) == 10
    assert written.entries[0].secondary == "civil-procedure"
    assert written.entries[0].vehicle is True
