"""Batching, shadow rules, and reference agreement for ``qp-topic-v0`` labels.

The labeling frame runs well past what one dispatch can finish, so
:func:`derive_label_batch` cuts each run's batch from committed state and
:func:`build_labels` accrues the artifact batch by batch; the rule, the seed, and
what "converged" means are documented on those two functions and in
``docs/qp-topic.md``.

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

import hashlib
import json
import re
from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, NamedTuple

from ..corpus import scotus_term_year, strip_docket_annotation
from ..schemas import (
    QP_TOPIC_LABELS,
    QpTopicAgreement,
    QpTopicBatchEntry,
    QpTopicLabel,
    QpTopicLabelAgreement,
    QpTopicLabelEntry,
    QpTopicLabels,
    QpTopicPublishedEntry,
    QpTopicReference,
    QpTopicShadow,
    QpTopicTriangleRow,
)
from ..supremecourt import IFP_SERIAL_BASE, parse_scotus_docket_number

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

# The most extract rows one labeling dispatch may be handed. The single place
# the labeling budget is stated: `qp-corpus` sizes each derived batch to it, and
# the labeling prompt states its budget as "whatever the extract holds" rather
# than restating a number that could drift from this one.
#
# Derived from what a dispatch can *finish*, and from the cap that actually
# stops it. That is the **labeler step's** 40 minutes, not the surrounding job's
# 75: the step is bounded below the job deliberately, so a runaway trips the
# step and leaves something to report. A ceiling sized against the job cap would
# therefore admit an extract the step kills, which is the exact failure the
# ceiling exists to prevent.
#
# 40 minutes buys about 1,200 texts at the only pace this repository has a
# figure for — the labeling prompt's own declared budget, which paired that step
# with roughly this many rows. Be honest about what that makes this number: the
# pace is **unmeasured** (no labeling dispatch has completed), and the budget it
# comes from was written when the extract happened to be about this size, so the
# ceiling is not independent of the population it bounds. It is a declared
# budget, not an observed rate. The first finished run is what should re-derive
# it, and until then the guard's value is that it refuses *loudly* rather than
# that it sits in exactly the right place.
#
# Raising the caps is not the lever either. The step cap sits inside a 75-minute
# job cap on purpose — a runaway that trips the step still leaves a run to
# report, where a job-level cancellation leaves nothing — so lifting the step
# means lifting both, and a single agent turn measured in hours is not a shape
# this repository runs. A population above the ceiling is served by batching
# (:func:`derive_label_batch`) rather than by a bigger number here.
LABEL_ROW_CEILING: Final = 1200

# The seed the within-stratum draw order is derived from. Named, constant, and
# never varied per run: the batch has to be a pure function of committed state,
# so re-deriving it on another runner, or after a failed dispatch, selects the
# same rows. A random seed would make the batch unreproducible; a per-run seed
# would make two dispatches over the same committed state disagree, and the
# second would then re-label rows the first had already published.
#
# The order it induces is a keyed hash of the case id, which is what keeps the
# draw off every property a docket number carries. `case_id` order is docket
# order, so a prefix of the frame selects on Term and fee class — the two things
# the labeling contract works hardest to keep out of the labeler's reach — and
# would make the published topic mix a function of docket number. The
# stratification below restores Term and fee class *deliberately*, as
# proportions; the hash decides only who goes first inside a stratum.
#
# Not a pre-registered constant, and no digest reads it. Moving it re-draws only
# *future* batches — label-once already excludes every published row, so nothing
# already in the artifact can be re-based by a new seed — which is why a change
# here needs a diff review rather than a version bump.
BATCH_ORDER_SEED: Final = "qp-topic-v0:batch-order"

# The stratum an unparsable docket number falls into. Empty over the labeling
# frame by construction — it is modern-cert-scoped, so every number parses — and
# kept so a frame that ever widens buckets those rows visibly rather than
# dropping them out of the draw.
UNPARSED_STRATUM: Final = "(unparsed)"

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


def reference_path(data_root: Path) -> Path:
    """Where the hand reference set lives under a data root."""
    return data_root / "qp-topics" / "qp-topic-reference.json"


def labels_path(data_root: Path) -> Path:
    """Where a labeler run's artifact lives under a data root.

    One definition because the writer and every reader must agree on it: a
    docket-pack build that looked one directory away from where ``qp-topics``
    wrote would omit the topic cut and report it as "no labeler has run".
    """
    return data_root / "qp-topics" / "qp-topics.json"


@dataclass(frozen=True)
class QpTopicStratum:
    """One Term x fee-class cell of the unlabeled pool, and what the batch drew from it."""

    key: str
    pool: int
    selected: int


@dataclass(frozen=True)
class QpTopicBatch:
    """The rows one labeling dispatch is handed, and the arithmetic that chose them."""

    case_ids: tuple[str, ...]
    frame: int
    labeled: int
    reference_rows: int
    reference_total: int
    pool: int
    fill: int
    remaining: int
    strata: tuple[QpTopicStratum, ...]
    converged: bool

    @property
    def reference_covered(self) -> float:
        """The share of the committed reference set this batch will be measured over.

        Exact rather than projected: the batch carries every reference member the
        frame holds and the labeler labels every extract row, so this is the
        coverage :func:`measure_agreement` will compute. Reference members the
        frame does not hold are simply unreachable — a case in the labeling scope
        whose stored questions-presented text is gone is a case no batch can put
        in front of a labeler — so this is the number that decides whether the
        run can clear the coverage floor at all, knowable before the dispatch.
        """
        return self.reference_rows / self.reference_total if self.reference_total else 0.0


def _batch_order_key(case_id: str) -> tuple[bytes, str]:
    """The seeded hash a stratum's rows are ordered by, ties broken on the id itself.

    ``blake2b`` rather than :func:`hash`, which is salted per process: a batch
    that changed with ``PYTHONHASHSEED`` would not be a function of committed
    state at all.
    """
    digest = hashlib.blake2b(f"{BATCH_ORDER_SEED}\x00{case_id}".encode(), digest_size=16).digest()
    return (digest, case_id)


def _stratum_key(docket_number: str) -> str:
    """The ``<Term>/<fee class>`` cell a docket number belongs to.

    Both halves ride in the number itself — the Term prefix and the serial, which
    runs from :data:`~fedcourtsai.supremecourt.IFP_SERIAL_BASE` on the IFP
    stream — read with the same two helpers the docket pack's own Term and
    fee-class cuts use, so a batch's strata name the same cells a published cut
    does.

    These are the two dimensions the batch is stratified on because they are the
    two the frame is most obviously *not* uniform across: coverage is thin and
    growing Term over Term, and far higher on paid dockets than IFP. What the
    stratification buys is **variance reduction, not bias removal** — the order
    key is a keyed hash independent of both dimensions, so an unstratified draw
    of the lowest hashes would already be an equal-probability sample and
    unbiased for the pool's mix. Proportional allocation makes each batch's
    margins exact instead of binomially noisy, which is what keeps an early batch
    from being read as a Term or fee-class statement it is not.
    """
    year = scotus_term_year(docket_number)
    parsed = parse_scotus_docket_number(strip_docket_annotation(docket_number))
    if year is None or parsed is None:
        return UNPARSED_STRATUM
    return f"{year}/{'ifp' if parsed[1] >= IFP_SERIAL_BASE else 'paid'}"


def _apportion(sizes: Mapping[str, int], quota: int) -> dict[str, int]:
    """Split ``quota`` across strata in proportion to their sizes (largest remainder).

    Integer arithmetic throughout: the remainders are compared as exact integers
    rather than as floats, so the apportionment cannot depend on rounding, and
    ties fall to the lower stratum key. Under-quota strata are never allocated
    more than they hold — with ``quota < total`` every floor is strictly below
    its stratum's size, so the one seat a remainder can add still fits.
    """
    total = sum(sizes.values())
    if total == 0:
        return dict.fromkeys(sizes, 0)
    if quota >= total:
        return dict(sizes)
    base = {key: quota * size // total for key, size in sizes.items()}
    remainders = {key: quota * size - base[key] * total for key, size in sizes.items()}
    seats = quota - sum(base.values())
    for key in sorted(sizes, key=lambda key: (-remainders[key], key))[:seats]:
        base[key] += 1
    return base


def derive_label_batch(
    *,
    frame: Sequence[tuple[str, str]],
    reference: QpTopicReference,
    labeled: Collection[str],
    ceiling: int | None = None,
) -> QpTopicBatch:
    """Choose the rows one labeling dispatch labels, from committed state alone.

    ``frame`` is the scoped extract as ``(case_id, docket_number)`` pairs,
    ``reference`` the committed hand set, and ``labeled`` the case ids the
    committed labels artifact already publishes. Nothing else is read, and
    nothing about the run enters: the same three inputs always produce the same
    batch, on any runner, in any order.

    The rule, in two clauses:

    1. **Every reference member present in the frame is force-included**, batch
       after batch. They are the measurement, not the output — their published
       labels come from the reference set, so re-labeling them costs a fraction
       of each batch and buys the agreement rate the publication gate turns on.
       Including only some would both lower the coverage the gate measures and
       turn membership in the batch into a probe on a set whose membership
       encodes cert outcomes. Note what the complete force-include does *not*
       promise: reference members the frame does not hold cannot be reached at
       all, so the coverage a run will be graded on is ``reference_covered``, and
       a frame missing enough of them cannot clear the floor however well the
       labeler reads. The caller checks that before spending the dispatch.
    2. **The rest of the ceiling is filled from the not-yet-labeled rows**,
       stratified by Term x fee class in proportion to that stratum's share of
       the unlabeled pool, ordered inside each stratum by :func:`_batch_order_key`.
       Already-published rows are excluded, so a row is labeled once and no
       second labeling exists to disagree with the first.

    Because both clauses read only committed files, batch membership discloses
    nothing a reader of those files does not already have — which is the whole
    reason the force-include is *complete*: a partial one would make membership
    informative about the reference set, and the reference set is an outcome
    oracle (``docs/qp-topic.md``).

    Repeat dispatches clear the frame batch by batch. When the unlabeled pool
    empties the batch is ``converged``: everything outside the reference set is
    labeled, and another run would re-grade the reference and publish nothing.
    """
    # Resolved here rather than as a default argument, which would bind the
    # module value once at import and ignore any later reading of it.
    budget = LABEL_ROW_CEILING if ceiling is None else ceiling
    members = {entry.case_id for entry in reference.entries}
    published = set(labeled)
    numbers = dict(frame)
    if len(numbers) != len(frame):
        # `dict` would keep the last docket number and report a frame one row
        # short, so a duplicated case would silently shrink the population every
        # later count is taken against. `read_texts` refuses the same thing.
        seen = Counter(case_id for case_id, _ in frame)
        raise QpTopicError(
            "duplicate case_id in the frame: "
            + ", ".join(sorted(case_id for case_id, count in seen.items() if count > 1))
        )
    in_reference = sorted(case_id for case_id in numbers if case_id in members)
    if len(in_reference) > budget:
        raise QpTopicError(
            f"{len(in_reference)} reference case(s) are in the frame, over the {budget}-row "
            "labeling ceiling — every batch carries the whole reference set, so no batch can "
            "be both measurable and inside the budget. Raising the ceiling means raising the "
            "labeling step's cap; narrowing the reference set means re-deriving the gate"
        )
    pool = [case_id for case_id in numbers if case_id not in members and case_id not in published]
    buckets: dict[str, list[str]] = {}
    for case_id in pool:
        buckets.setdefault(_stratum_key(numbers[case_id]), []).append(case_id)
    for rows in buckets.values():
        rows.sort(key=_batch_order_key)
    allocation = _apportion(
        {key: len(rows) for key, rows in buckets.items()}, budget - len(in_reference)
    )
    drawn = [case_id for key in sorted(buckets) for case_id in buckets[key][: allocation[key]]]
    return QpTopicBatch(
        case_ids=tuple(sorted([*in_reference, *drawn])),
        frame=len(numbers),
        labeled=sum(1 for case_id in numbers if case_id in published),
        reference_rows=len(in_reference),
        reference_total=len(reference.entries),
        pool=len(pool),
        fill=len(drawn),
        remaining=len(pool) - len(drawn),
        strata=tuple(
            QpTopicStratum(key=key, pool=len(buckets[key]), selected=allocation[key])
            for key in sorted(buckets)
        ),
        converged=not pool,
    )


def batch_metadata(batch: QpTopicBatch, *, ceiling: int | None = None) -> dict[str, object]:
    """The batch's arithmetic as JSON, for the record beside the extract.

    Deliberately **not** written into the extract itself. The extract is the
    labeler's entire evidentiary input and the contract is text-only; strata
    counts are Term and fee-class counts, and the selection rule is exactly what
    the labeling prompt forbids reasoning from. Handing the labeler the shape of
    its own draw — how many of its rows are measured, how the fee streams split —
    is the effort asymmetry the gate cannot detect. The withholding is
    shape-level, not absolute: ``docs/qp-topic.md`` states the rule and the
    reference share in prose, and the prompt sends the labeler there. What no
    channel gives it is which of *its* rows are which.

    ``reference_rows`` travels with ``reference_total`` and the coverage they
    make, because this file and the run log are where a maintainer decides
    whether to spend the dispatch, and a count without its denominator is the
    shape of claim the rest of this repository refuses.
    """
    return {
        "seed": BATCH_ORDER_SEED,
        "ceiling": LABEL_ROW_CEILING if ceiling is None else ceiling,
        "frame": batch.frame,
        "labeled": batch.labeled,
        # `rows`, not `batch`: the ledger's `batch` is an index, and one word for
        # a size in one artifact and an index in the other invites a mis-read.
        "rows": len(batch.case_ids),
        "reference_rows": batch.reference_rows,
        "reference_total": batch.reference_total,
        "reference_covered": batch.reference_covered,
        "coverage_floor": COVERAGE_FLOOR,
        "pool": batch.pool,
        "fill": batch.fill,
        "remaining": batch.remaining,
        "converged": batch.converged,
        "strata": [
            {"stratum": row.key, "pool": row.pool, "selected": row.selected} for row in batch.strata
        ],
    }


def render_batch(batch: QpTopicBatch) -> str:
    """The batch block a labeling dispatch's extract job prints for the run log."""
    lines = [
        f"  frame:     {batch.frame} scoped row(s), {batch.labeled} already labeled",
        f"  batch:     {len(batch.case_ids)} row(s) = {batch.reference_rows} reference "
        + f"(re-graded every run, published from the hand labels) + {batch.fill} new",
        f"  measured:  {batch.reference_rows} of {batch.reference_total} reference case(s) "
        + f"({batch.reference_covered:.1%}) against a {COVERAGE_FLOOR:.0%} coverage floor",
        f"  remaining: {batch.remaining} unlabeled row(s) for later batches",
        f"  order:     seeded hash of case_id (seed {BATCH_ORDER_SEED!r}), "
        + "stratified by Term x fee class:",
    ]
    lines += [f"    {row.key:16s} {row.selected} of {row.pool} unlabeled" for row in batch.strata]
    return "\n".join(lines)


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
    prior: QpTopicLabels | None = None,
) -> QpTopicLabels:
    """Assemble the labels artifact: this batch's measurement over the accumulated union.

    ``entries`` is one batch's labeler output and ``texts`` that batch's extract;
    ``prior`` is the committed artifact the batch accrues onto, or ``None`` for
    the first batch. Pure: every input is already in memory, so the same inputs
    reproduce the artifact byte for byte. The gate is *measured* here and
    enforced by the caller — the artifact records ``gate_passed`` either way, and
    it is the writer that refuses to put a failing run on disk.

    Two publication rules, and they are the point of the design rather than
    bookkeeping:

    **A reference member publishes the reference's hand label, never the
    labeler's.** The labeler's call on those rows is measurement input: it is
    scored into the agreement rate above and then discarded. So a labeler that
    flips a reference case moves that run's measured rate — the only thing it
    should move — and can neither block the run (the gate reads the rate, and one
    row moves it by a fraction of a point on a set this size) nor change a
    published row.

    **Every other row is published once.** The batch a dispatch is handed already
    excludes what the artifact publishes (:func:`derive_label_batch`), so a
    second labeling of the same row is a derivation bug rather than a
    disagreement to arbitrate, and it stops the run. Deliberate relabeling — a
    vocabulary version bump, or an extraction repair that changes the text a
    label was assigned from — supersedes by rewriting the artifact under its own
    reviewed diff, not by a labeler quietly disagreeing with an earlier one.
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

    agreement = measure_agreement({e.case_id: e.label for e in entries}, reference)
    hand = {entry.case_id: entry for entry in reference.entries}
    carried = list(prior.entries) if prior is not None else []
    batch = max((row.batch for row in prior.batches), default=0) + 1 if prior is not None else 1

    published = {entry.case_id: entry for entry in carried}
    for entry in entries:
        standing = published.get(entry.case_id)
        adjudicated = hand.get(entry.case_id)
        if adjudicated is None:
            if standing is not None:
                raise QpTopicError(
                    f"{entry.case_id} already carries a published label from batch "
                    f"{standing.batch}: a non-reference row is labeled once, and the batch "
                    "this extract was derived from should have excluded it"
                )
            published[entry.case_id] = QpTopicPublishedEntry(
                **entry.model_dump(), source="labeler", batch=batch
            )
        else:
            # The facets go with the label they belong to: the reference set
            # holds primaries only, so a reference row carries no secondary and
            # no vehicle flag rather than the labeler's, which nothing measured.
            published[entry.case_id] = QpTopicPublishedEntry(
                case_id=entry.case_id,
                docket_number=entry.docket_number,
                label=adjudicated.label,
                source="reference",
                batch=standing.batch if standing is not None else batch,
            )

    superseded = 0
    for standing in carried:
        current = published[standing.case_id]
        if current == standing:
            continue
        if current.source != "reference":
            raise QpTopicError(
                f"{standing.case_id} would change from {standing.label} to {current.label} "
                "without a reference label behind it — published rows are immutable outside "
                "the reference set"
            )
        superseded += 1

    fresh = [row for row in published.values() if row.batch == batch]
    ledger = [*(prior.batches if prior is not None else [])]
    ledger.append(
        QpTopicBatchEntry(
            batch=batch,
            labeler=labeler,
            published=len(fresh),
            # Split out, because on the first batch every reference row is also
            # newly published and `published` would otherwise credit the labeler
            # with the hand set's rows.
            labeler_rows=sum(1 for row in fresh if row.source == "labeler"),
            measured=len(entries),
            agree=agreement.overall_agree,
            n=agreement.overall_n,
            floor=agreement.floor,
            fired=fired,
            disagreements=disagreements,
            superseded=superseded,
        )
    )
    return QpTopicLabels(
        labeler=labeler,
        cases=len(published),
        agreement=agreement,
        shadow=QpTopicShadow(texts=len(entries), fired=fired, disagreements=disagreements),
        batches=ledger,
        entries=sorted(published.values(), key=lambda row: row.case_id),
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
