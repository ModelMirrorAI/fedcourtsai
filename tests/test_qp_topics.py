"""The qp-topic labeler machinery: shadow rules, agreement, and the gated builder.

Offline throughout — the shadow rules read text, the agreement reads two label
sets, and the CLI round-trip runs against a tmp reference set. The extract
tests build a five-row corpus in ``tmp_path``, so a rule change still surfaces
in seconds and nothing here reads a pulled blob.

The shadow fixtures are **in-sample**: the positives are shortened reference
texts the rules were tuned to fire on and the negatives are the boundary texts
they were tuned to decline. They pin the tuned behaviour against regression;
they cannot detect that the tuning overfit, and a green suite is no evidence
about an unseen text (see :mod:`fedcourtsai.pipeline.qp_topics`).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline import qp_topics as qp_topics_module
from fedcourtsai.pipeline.documents import KIND_QUESTIONS_PRESENTED, questions_presented_extract
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


# --- the labeling extract: scope, the measurement escape, and the budget guard ---


def _scoped_case(case_id: str, docket_number: str, **kw: object) -> corpus.CorpusRow:
    """A row inside the labeling scope: live slice, modern cert, nothing excluded."""
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket_number,
        "date_filed": date(2025, 10, 1),
        "last_live_polled": date(2026, 8, 27),
    }
    return corpus.CorpusRow(**(base | kw))


def _qp_document(case_id: str, text: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_QUESTIONS_PRESENTED,
        url=f"https://example/{case_id}.pdf",
        fetched_at=date(2026, 8, 27),
        text=text,
    )


def _seed_extract_corpus(db: Path) -> None:
    """Five QP-bearing cases: one in scope, four out of it for a different reason."""
    rows = [
        _scoped_case("scotus/1", "25-101"),
        # IFP: the serial is at/above IFP_SERIAL_BASE, the one predict-scope rule
        # that bites on a QP-bearing population.
        _scoped_case("scotus/2", "25-5101"),
        # Bulk-import row: no live-channel poll, so outside the live slice.
        _scoped_case("scotus/3", "25-103", last_live_polled=None),
        # An application docket: live, but not the discretionary-cert form.
        _scoped_case("scotus/4", "25A103"),
        # In scope, but the extractor could not vouch for the capture.
        _scoped_case("scotus/5", "25-105"),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_documents(
            conn,
            [
                _qp_document("scotus/1", "Whether the paid petition presents a question."),
                _qp_document("scotus/2", "Whether the IFP petition presents a question."),
                _qp_document("scotus/3", "Whether the bulk-import row presents a question."),
                _qp_document("scotus/4", "Whether the application presents a question."),
                _qp_document("scotus/5", "   \n "),
            ],
        )


def test_extract_scopes_to_the_labeling_population(tmp_path: Path) -> None:
    # The scoped selection is the docket pack's own topic-section frame:
    # live-slice modern cert. Each excluded row here fails exactly one clause,
    # so a dropped clause would show up as a specific extra case rather than a
    # count.
    db = tmp_path / "corpus.db"
    _seed_extract_corpus(db)

    with corpus.connect(db) as conn:
        extract = questions_presented_extract(conn)

    assert [row.case_id for row in extract.rows] == ["scotus/1", "scotus/2"]
    # The empty capture is a skip (a row the pass declined); the two
    # out-of-frame cases are not — they were never in the population.
    assert extract.skipped == 1


def test_extract_keeps_the_ifp_stream_the_reference_set_spans(tmp_path: Path) -> None:
    # The frame deliberately stops short of the predict-scope segment. Dropping
    # IFP rows would put the publication gate's coverage floor out of reach (the
    # reference set spans both fee streams), and carrying the reference set back
    # in to restore it would make an IFP docket number a certain
    # reference-membership tell for the labeler.
    db = tmp_path / "corpus.db"
    _seed_extract_corpus(db)
    ifp = corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="25-5101")
    assert corpus.is_ifp_petition(ifp)
    assert corpus.out_of_scope_reason(ifp) is not None

    with corpus.connect(db) as conn:
        extract = questions_presented_extract(conn)

    assert "scotus/2" in [row.case_id for row in extract.rows]


def test_extract_all_flag_takes_every_stored_row(tmp_path: Path) -> None:
    # The measurement form answers "what is in this blob", so scope does not
    # apply — but the skip rule still does.
    db = tmp_path / "corpus.db"
    _seed_extract_corpus(db)

    with corpus.connect(db) as conn:
        extract = questions_presented_extract(conn, scoped=False)

    assert [row.case_id for row in extract.rows] == [
        "scotus/1",
        "scotus/2",
        "scotus/3",
        "scotus/4",
    ]
    assert extract.skipped == 1


def _extract_corpus_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, rows: int) -> Path:
    """A corpus root whose scoped extract holds exactly ``rows`` labelable cases."""
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    data_root.mkdir()
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [_scoped_case(f"scotus/{n}", f"25-{n}") for n in range(1, rows + 1)]
        )
        corpus.upsert_documents(
            conn,
            [
                _qp_document(f"scotus/{n}", f"Whether question {n} is presented.")
                for n in range(1, rows + 1)
            ],
        )
    return corpus_root


def test_qp_corpus_all_flag_reaches_the_unscoped_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The flag is the seam between the CLI and the two selections, and it is the
    # one a maintainer reaches for by hand: pin that `--all` really changes the
    # population read and says which one it used, not just that it parses.
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    data_root.mkdir()
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    _seed_extract_corpus(corpus.corpus_db_path(corpus_root))
    scoped_out = tmp_path / "scoped.json"
    all_out = tmp_path / "all.json"

    scoped = CliRunner().invoke(app, ["qp-corpus", "--out", str(scoped_out)])
    unscoped = CliRunner().invoke(app, ["qp-corpus", "--all", "--out", str(all_out)])

    assert (scoped.exit_code, unscoped.exit_code) == (0, 0), scoped.output + unscoped.output
    assert [row["case_id"] for row in json.loads(scoped_out.read_text())] == [
        "scotus/1",
        "scotus/2",
    ]
    assert [row["case_id"] for row in json.loads(all_out.read_text())] == [
        "scotus/1",
        "scotus/2",
        "scotus/3",
        "scotus/4",
    ]
    assert "live-slice modern discretionary-cert petitions" in scoped.output
    assert "every stored questions-presented row in the blob" in unscoped.output


def test_qp_corpus_refuses_an_extract_over_the_labeling_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Only a complete label file yields an artifact, so an over-budget extract
    # buys a cancelled job and no artifact rather than partial coverage. The
    # refusal has to name the count and the scope: that is what decides between
    # a narrower scope and a different design.
    monkeypatch.setattr(qp_topics_module, "LABEL_ROW_CEILING", 2)
    _extract_corpus_root(tmp_path, monkeypatch, rows=3)
    out = tmp_path / "extract.json"

    result = CliRunner().invoke(app, ["qp-corpus", "--out", str(out)])

    assert result.exit_code == 1
    assert "refusing to write 3 row(s)" in result.output
    assert "2-row labeling ceiling" in result.output
    assert "live-slice modern discretionary-cert petitions" in result.output
    assert not out.exists()


def test_qp_corpus_writes_an_extract_at_the_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # At the ceiling the guard does not fire — it is a bound on what a run can
    # be handed, not a margin below one.
    monkeypatch.setattr(qp_topics_module, "LABEL_ROW_CEILING", 3)
    _extract_corpus_root(tmp_path, monkeypatch, rows=3)
    out = tmp_path / "extract.json"

    result = CliRunner().invoke(app, ["qp-corpus", "--out", str(out)])

    assert result.exit_code == 0, result.output
    assert [row["case_id"] for row in json.loads(out.read_text())] == [
        "scotus/1",
        "scotus/2",
        "scotus/3",
    ]


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
