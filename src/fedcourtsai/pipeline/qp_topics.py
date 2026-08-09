"""Shadow rules and reference agreement for ``qp-topic-v0`` question-presented labels.

Labeling authority belongs to the agent labeler alone (``docs/qp-topic.md``):
the vocabulary's labels are defined by what a question *asks*, the two largest
error sinks carry no distinctive citation, and keywords actively mislead —
background prose fires rules, a cited statute often belongs to a different
subject than the question, and a case name mentioned in passing contaminates.
Nothing here assigns a published label. The four rules below are a **shadow
check**: they publish nothing and pre-empt nothing, and their disagreement rate
with the labeler is a standing regression trip-wire, so a drifting labeler shows
up as a moving disagreement rate before it shows up in a cut.

The rules are therefore **precision-first**, twice over. Each is written from
the statutes and doctrinal phrases the label's own definition names, so it fires
only where the vocabulary itself is explicit; and :func:`shadow_label` returns a
label only when *exactly one* rule fires, so a text that trips two rules is
silently declined rather than arbitrated. Declining costs recall, which the
shadow check can afford; guessing costs precision, which is the only thing it
has.

Measured against the reference set's founding block (189 labels; the labels are
committed, their texts are corpus-only, read at corpus pointer ``0efacfd9…``, so
no test can pin the table below and this docstring is its whole record):

===================================  ======  =======  ==========================
Rule                                  fired  correct  in-sample precision (bound)
===================================  ======  =======  ==========================
``firearms``                             23       23  1.000
``intellectual-property``                 4        4  1.000
``tax``                                   2        2  1.000
``employment-and-antidiscrimination``     7        7  1.000
===================================  ======  =======  ==========================

Jointly, exactly one rule fires on 36 of the 189 founding texts and is right on
all 36; no founding text trips two rules, and each rule fires on every founding
entry of its own label, so in-sample *recall* is likewise 1.000 and an equally
weak bound. The reference supplement (164 texts these patterns were never tuned
on) is the out-of-sample check, and it lands where the warning below predicts:
32 firings, 23 in agreement — 71.9% — with ``firearms`` holding (12/13) and
``tax``/``intellectual-property`` collapsing to 1/3 each on exactly the
``taxpayer``-standing and trademark-speech contaminations named there.

Read all of it as **bounds, not estimates**. The patterns were tuned on the same
189 texts they are measured on; the labels they cover rest on 2 to 23 reference
positives each; and the reference set's frame is grant-enriched, so precision on
the denial stream — where a labeler run spends most of its texts — is
unmeasured. Three out-of-sample failures are readable off the vocabulary itself:
``taxpayer`` fires on taxpayer-standing questions, which the vocabulary routes to
``civil-procedure``; ``lanham act`` / ``trademark`` fires on First Amendment
challenges to registration bars, which route to ``first-amendment``; and ``nlrb``
fires on agency-power questions about the Board, which route to
``administrative-law-and-benefit-programs``. A perfect in-sample rate is what
tuning on the measurement set buys; it is not evidence about the next text.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, NamedTuple

from ..schemas import (
    QP_TOPIC_LABELS,
    QpTopicAgreement,
    QpTopicLabel,
    QpTopicLabelAgreement,
    QpTopicLabelEntry,
    QpTopicLabels,
    QpTopicReference,
    QpTopicShadow,
    QpTopicTriangleRow,
)

# The publication gate: a labeler whose overall agreement with the reference
# rater falls below this publishes nothing (``docs/qp-topic.md``).
AGREEMENT_GATE: Final = 0.80

# Per-label support floor. Under it a label's agreement is reported as a raw
# count and never as a rate — one entry moves the ratio by tens of points.
SUPPORT_FLOOR: Final = 10

# The share of the reference set a run must cover for its rate to be a
# measurement of the stream rather than of a sliver. Without it the gate is
# trivially defeated: label the five easiest reference cases correctly, cover
# nothing else, and 100% of n=5 licenses a thousand unmeasured labels.
COVERAGE_FLOOR: Final = 0.90

# The confusion-matrix labels, in row and column order. These three carry the
# boundaries where the labeling actually goes wrong, so they get a matrix rather
# than a rate.
TRIANGLE: Final[tuple[QpTopicLabel, ...]] = (
    "constitutional-rights",
    "criminal-law",
    "civil-procedure",
)

# One rule per label it covers, each a disjunction of the statutes and doctrinal
# phrases that label's definition names. Patterns run against normalized text
# (see :func:`_normalize`). ``title ix`` alone is education, not employment — a
# sex-discrimination-in-schools question is `constitutional-rights` when it is
# framed on equal protection — so it fires only where employment vocabulary
# *follows* it, a deliberately one-directional lookahead: the cheap miss is the
# right trade for a rule whose only asset is precision.
_SHADOW_RULES: Final[tuple[tuple[QpTopicLabel, re.Pattern[str]], ...]] = (
    (
        "employment-and-antidiscrimination",
        re.compile(
            r"\btitle vii\b|americans with disabilities|rehabilitation act"
            + r"|fair labor standards|\bflsa\b|\berisa\b|employee retirement income"
            + r"|national labor relations|\bnlrb\b|\bfela\b|fair housing act"
            + r"|age discrimination in employment|\btitle ix\b(?=.*\bemploy)"
        ),
    ),
    (
        "firearms",
        re.compile(
            r"\b922\s*\(\s*g\s*\)|second (and \w+ )?amendments?\b|keep and bear arms"
            + r"|\bfirearms? (licens|regulat|dealer)|27 c\.?f\.?r\.? ?478"
        ),
    ),
    (
        "intellectual-property",
        re.compile(
            r"\bcopyright|\btrademarks?\b|\btrade secrets?\b|lanham act"
            + r"|\bpatent(s|ed|able|ability)?\b"
        ),
    ),
    (
        "tax",
        re.compile(
            r"internal revenue|\b26 u\.?s\.?c|\btax court\b|\btaxpayer\b"
            + r"|\b(estate|income|excise|franchise|property) tax\b"
        ),
    ),
)


class QpTopicError(ValueError):
    """A labeler's output cannot be reconciled with the vocabulary or the reference set."""


def _normalize(text: str) -> str:
    """Lowercase, rejoin hyphenated line breaks, and collapse whitespace.

    The stored texts come out of petition PDFs, where a word is routinely split
    across lines (``Amend- ments``, ``regu- lated``). Rejoining those before a
    rule runs is the difference between a pattern that matches the sentence a
    reader sees and one that matches the column width the printer chose.
    """
    lowered = text.lower()
    return re.sub(r"\s+", " ", re.sub(r"(\w)-\s+(\w)", r"\1\2", lowered))


def shadow_label(text: str) -> QpTopicLabel | None:
    """The shadow rules' label for one question-presented text, or ``None``.

    A label is returned only when **exactly one** rule fires. Two rules firing
    means the text names two subjects' statutes, which is precisely the case the
    keyword rules cannot arbitrate — the vocabulary picks a primary by what the
    question asks, and a rule cannot see that — so the shadow check declines
    instead of guessing. No rule firing is the ordinary case: twelve of the
    sixteen labels have no rule at all.
    """
    normalized = _normalize(text)
    fired = [label for label, pattern in _SHADOW_RULES if pattern.search(normalized)]
    return fired[0] if len(fired) == 1 else None


def measure_agreement(labels: Mapping[str, str], reference: QpTopicReference) -> QpTopicAgreement:
    """Measure a labeler's primaries against the hand reference set.

    ``labels`` maps ``case_id`` to the labeler's primary. Only reference entries
    the labeler covered are compared; the rest are counted in ``uncovered``
    rather than scored as disagreements, so a partial run reports what it
    measured instead of being punished for what it did not read. What comes back
    is agreement with a single hand rater, not accuracy — see
    :class:`~fedcourtsai.schemas.QpTopicAgreement`.

    The gate therefore takes **two** conditions, because forgiving what was not
    covered would otherwise pay for skipping it: the rate must reach
    :data:`AGREEMENT_GATE`, *and* the compared entries must reach
    :data:`COVERAGE_FLOOR` of the reference set.
    """
    compared = [entry for entry in reference.entries if entry.case_id in labels]
    overall_n = len(compared)
    overall_agree = sum(1 for entry in compared if labels[entry.case_id] == entry.label)
    overall_rate = overall_agree / overall_n if overall_n else None

    per_label: list[QpTopicLabelAgreement] = []
    for label in QP_TOPIC_LABELS:
        rows = [entry for entry in compared if entry.label == label]
        if not rows:
            continue
        agree = sum(1 for entry in rows if labels[entry.case_id] == label)
        per_label.append(
            QpTopicLabelAgreement(
                label=label,
                agree=agree,
                n=len(rows),
                rate=agree / len(rows) if len(rows) >= SUPPORT_FLOOR else None,
            )
        )

    triangle: list[QpTopicTriangleRow] = []
    for row_label in TRIANGLE:
        rows = [entry for entry in compared if entry.label == row_label]
        counts = [
            sum(1 for entry in rows if labels[entry.case_id] == column) for column in TRIANGLE
        ]
        triangle.append(
            QpTopicTriangleRow(
                reference=row_label,
                counts=counts,
                other=len(rows) - sum(counts),
                n=len(rows),
            )
        )

    # What a constant labeler scores on the same entries: the largest reference
    # class's share. The rate alone is unreadable — only the distance from here
    # is skill, and on a sixteen-label vocabulary that distance is most of it.
    class_counts = Counter(entry.label for entry in compared)
    floor = max(class_counts.values()) / overall_n if overall_n else None

    covered = overall_n / len(reference.entries) if reference.entries else 0.0
    return QpTopicAgreement(
        floor=floor,
        overall_agree=overall_agree,
        overall_n=overall_n,
        overall_rate=overall_rate,
        uncovered=len(reference.entries) - overall_n,
        per_label=per_label,
        triangle=triangle,
        gate_passed=(
            overall_rate is not None
            and overall_rate >= AGREEMENT_GATE
            and covered >= COVERAGE_FLOOR
        ),
    )


def read_label_lines(path: Path) -> list[QpTopicLabelEntry]:
    """Read the labeler's JSONL intermediate, one entry per line.

    Every line validates against the vocabulary before anything is measured: an
    unknown label is a labeler that has drifted from ``docs/qp-topic.md``, and
    silently dropping the line would move the measurement instead of failing it.
    The offending line is quoted back with its number, because the labeler that
    has to fix it reads a run log, not a traceback.
    """
    entries: list[QpTopicLabelEntry] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(QpTopicLabelEntry.model_validate(json.loads(line)))
        except (ValueError, TypeError) as exc:
            # Echo the head of the line only: a labeler that pasted petition
            # text into it would otherwise republish that text into a run log.
            raise QpTopicError(
                f"{path}:{number}: unusable label line: {line.strip()[:160]} ({exc})"
            ) from exc
    if not entries:
        raise QpTopicError(f"{path}: no label lines")
    return entries


class QpText(NamedTuple):
    """One ``qp-corpus`` row: the docket number it was extracted under, and the text."""

    docket_number: str
    text: str


def read_texts(path: Path) -> dict[str, QpText]:
    """Read the ``qp-corpus`` extract into ``case_id`` -> row.

    The docket number is kept, not discarded: it is the second half of the key
    pair, and checking the labeler copied it back unchanged is the only thing
    standing between a mistyped row and a label attached to the wrong case.
    """
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise QpTopicError(f"{path}: expected a JSON list of qp-corpus rows")
    texts: dict[str, QpText] = {}
    for row in payload:
        if not isinstance(row, dict) or not {"case_id", "docket_number", "text"} <= set(row):
            raise QpTopicError(f"{path}: row is not a qp-corpus row: {sorted(row)!r}")
        case_id = str(row["case_id"])
        if case_id in texts:
            raise QpTopicError(f"{path}: duplicate case_id {case_id}")
        texts[case_id] = QpText(str(row["docket_number"]), str(row["text"]))
    return texts


def _check_reference_join(
    entries: Sequence[QpTopicLabelEntry], reference: QpTopicReference
) -> None:
    """Fail loudly when a labeled case and a reference entry half-match.

    The two sets are joined on ``case_id`` *and* ``docket_number``. A pair that
    agrees on one key and disagrees on the other is a mis-join, not a
    disagreement: it would silently measure one case's label against another
    case's text. Measuring is not worth doing until it is resolved by hand.
    """
    by_case = {entry.case_id: entry for entry in reference.entries}
    by_docket = {entry.docket_number: entry for entry in reference.entries}
    for entry in entries:
        reference_entry = by_case.get(entry.case_id)
        if reference_entry is not None and reference_entry.docket_number != entry.docket_number:
            raise QpTopicError(
                f"reference join mismatch: {entry.case_id} is docket "
                f"{reference_entry.docket_number} in the reference set, "
                f"{entry.docket_number} in the labels"
            )
        reference_entry = by_docket.get(entry.docket_number)
        if reference_entry is not None and reference_entry.case_id != entry.case_id:
            raise QpTopicError(
                f"reference join mismatch: docket {entry.docket_number} is "
                f"{reference_entry.case_id} in the reference set, {entry.case_id} in the labels"
            )


def _check_extract_join(entries: Sequence[QpTopicLabelEntry], texts: Mapping[str, QpText]) -> None:
    """Fail unless the labels and the extract are the same cases, keyed the same way.

    The extract is the labeler's entire entitled input, so exact coverage is the
    contract — the prompt asks for one line per text. Enforcing it closes three
    holes at once: a labeled case that is in no extract row carries an unverified
    key pair into the artifact; a partial run turns the printed ``n`` into a
    membership probe on the reference set, whose membership encodes cert
    outcomes; and a truncated run measures a prefix of ``case_id`` order, which
    is not a random sample of the frame.
    """
    labeled = {entry.case_id for entry in entries}
    missing = sorted(labeled - set(texts))
    unlabeled = sorted(set(texts) - labeled)
    if missing or unlabeled:
        raise QpTopicError(
            f"labels and texts are not the same case set: {len(missing)} labeled case(s) "
            f"absent from the extract (e.g. {missing[:3]}), {len(unlabeled)} extract row(s) "
            f"left unlabeled (e.g. {unlabeled[:3]}) — label every row of the extract, once"
        )
    for entry in entries:
        extracted = texts[entry.case_id].docket_number
        if extracted != entry.docket_number:
            raise QpTopicError(
                f"extract join mismatch: {entry.case_id} is docket {extracted} in the "
                f"extract, {entry.docket_number} in the labels"
            )


def build_labels(
    *,
    entries: Sequence[QpTopicLabelEntry],
    texts: Mapping[str, QpText],
    reference: QpTopicReference,
    labeler: str,
) -> QpTopicLabels:
    """Assemble one labeler run's artifact: its labels, its agreement, its shadow check.

    Pure: every input is already in memory, so the same inputs reproduce the
    artifact byte for byte. The gate is *measured* here and enforced by the
    caller — the artifact records ``gate_passed`` either way, and it is the
    writer that refuses to put a failing run on disk.
    """
    seen = Counter(entry.case_id for entry in entries)
    duplicates = sorted(case_id for case_id, count in seen.items() if count > 1)
    if duplicates:
        raise QpTopicError(f"duplicate case_id in the labels: {', '.join(duplicates)}")
    _check_reference_join(entries, reference)
    _check_extract_join(entries, texts)

    fired = 0
    disagreements = 0
    for entry in entries:
        rule_label = shadow_label(texts[entry.case_id].text)
        if rule_label is None:
            continue
        fired += 1
        disagreements += rule_label != entry.label

    ordered = sorted(entries, key=lambda entry: entry.case_id)
    return QpTopicLabels(
        labeler=labeler,
        cases=len(ordered),
        agreement=measure_agreement({e.case_id: e.label for e in entries}, reference),
        shadow=QpTopicShadow(texts=len(entries), fired=fired, disagreements=disagreements),
        entries=ordered,
    )


def render_agreement(agreement: QpTopicAgreement) -> str:
    """Render the measured agreement block a labeler run reports.

    The rate is always printed beside its ``n`` and never alone: an agreement
    number without its denominator is the shape of claim ``docs/qp-topic.md``
    exists to prevent.
    """
    rate = "n/a" if agreement.overall_rate is None else f"{agreement.overall_rate:.1%}"
    floor = "n/a" if agreement.floor is None else f"{agreement.floor:.1%}"
    lines = [
        f"  overall:   {agreement.overall_agree}/{agreement.overall_n} ({rate}) "
        f"vs the v0 reference rater — agreement, not accuracy",
        f"  floor:     {floor} — what a constant labeler scores on the same entries",
        f"  uncovered: {agreement.uncovered} reference entr(ies) the labeler did not cover",
    ]
    for row in agreement.per_label:
        measured = "unmeasured in v0" if row.rate is None else f"{row.rate:.1%}"
        lines.append(f"    {row.label:38s} {row.agree}/{row.n} ({measured})")
    lines.append("  triangle (rows = reference, cols = " + ", ".join(TRIANGLE) + "):")
    for triangle_row in agreement.triangle:
        cells = " ".join(f"{count:3d}" for count in triangle_row.counts)
        lines.append(
            f"    {triangle_row.reference:24s} {cells}  other={triangle_row.other} "
            f"n={triangle_row.n}"
        )
    return "\n".join(lines)
