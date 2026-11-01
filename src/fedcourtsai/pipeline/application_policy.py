"""Executive policy areas read by the application labeler (``policy-area-v2``).

The application labeler gives a second field, the executive policy area, on
every application where the federal government is a party (the extract's
``policy_row``). This module cuts the rows a batch owes that field, measures
the labeler's areas against the ``policy-area-v1`` hand labels, and accrues the
areas onto the application labels artifact (``docs/qp-topic.md``, *Policy
areas*).

**Which rows a batch carries for their policy area.** A topic batch already
holds the new applications, and each of them that is a policy row is asked for
its area. A batch also owes the area of every published policy row that lacks
one, so the field reaches the applications labeled before it existed. Whenever
a batch owes any area, it carries every hand-labeled row the frame holds too,
for the measurement, exactly as a topic batch carries the whole reference
block, then the published rows lacking an area up to the labeling ceiling. A
batch owing none asks for no area at all: its rows go out with ``policy_row``
cleared.

**Nothing in the extract says which rows are measured.** Every policy row
carries the same flag. Which published rows are in the batch for their area
alone (their topic line neither measured nor published) is derived again at
measurement from committed state, never written into the file the labeler
reads, since on a converged frame the rows that are *not* there for their area
alone are the topic reference block, whose membership tracks disposition.

**The measurement and its gate.** The labeler's area on each hand-labeled row
is compared with the hand label. The hand raters were not blind to the outcome
and read their own knowledge of a public case, which the labeler may not, so
the rate is agreement with that reference, not accuracy. The gate is the topic
gate's: the rate at least :data:`~fedcourtsai.pipeline.qp_topics.AGREEMENT_GATE`,
above the constant-labeler floor, with the compared rows at least
:data:`~fedcourtsai.pipeline.qp_topics.COVERAGE_FLOOR` of the hand set.

**A refusal holds until the prompt changes.** A labeler that does not answer
the same way on every run would pass a re-measured gate by chance in the end,
so after a refused policy measurement no batch asks for areas again until the
labeling prompt's digest differs from the one the refused batch read.

**What publishes.** Only a batch whose policy measurement passed publishes
areas, and it never touches a topic label. A hand-labeled row publishes its
hand label (``reference``), always; every other policy row publishes the
labeler's area (``labeler``), once: a row that already carries one keeps it. A
refused policy measurement publishes nothing, leaves the standing areas and
the artifact's ``policy_agreement`` as they are, and is recorded on its batch's
ledger row, while the batch's topic labels publish under their own gate. The
topic gate is the artifact's: a batch whose topic measurement is refused
writes no artifact, so its policy areas do not publish either.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from ..schemas import (
    PolicyAreaLabel,
    QpTopicApplicationLabelEntry,
    QpTopicApplicationLabels,
    QpTopicApplicationReference,
    QpTopicPolicyAgreement,
    QpTopicPolicyAreaShare,
)
from .policy_area import POLICY_AREAS, PolicyLabel
from .qp_topics import AGREEMENT_GATE, COVERAGE_FLOOR, QpTopicError, _batch_order_key

#: The labeling prompt, at its place in the checkout the package is installed from.
LABEL_PROMPT: Path = Path(__file__).resolve().parents[3] / ".github/prompts/qp-topic-label.md"


def label_prompt_sha256(path: Path = LABEL_PROMPT) -> str | None:
    """The labeling prompt's sha256, or ``None`` where the checkout does not hold it."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read_policy_rows(path: Path) -> set[str]:
    """The ``case_id`` of every application extract row marked ``policy_row``."""
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise QpTopicError(f"{path}: expected a JSON list of qp-corpus rows")
    rows: set[str] = set()
    for row in payload:
        if not isinstance(row, dict) or "case_id" not in row:
            raise QpTopicError(f"{path}: row is not an application extract row")
        flag = row.get("policy_row", False)
        if not isinstance(flag, bool):
            raise QpTopicError(f"{path}: {row['case_id']}: policy_row must be a boolean")
        if flag:
            rows.add(str(row["case_id"]))
    return rows


def policy_only_rows(
    case_ids: Collection[str],
    prior: QpTopicApplicationLabels | None,
    reference: QpTopicApplicationReference,
) -> set[str]:
    """The batch rows there for their policy area alone, derived from committed state.

    A row the committed artifact already publishes and the topic reference
    block does not hold can be in a batch only for its policy area: the topic
    rule excludes published rows outside the block.
    """
    if prior is None:
        return set()
    published = {entry.case_id for entry in prior.entries}
    block = {entry.case_id for entry in reference.entries}
    return {case_id for case_id in case_ids if case_id in published and case_id not in block}


def _key(docket_number: str) -> str:
    return docket_number.strip().upper()


def refusal_hold(artifact: QpTopicApplicationLabels | None, prompt_sha256: str | None) -> bool:
    """Whether a refused policy measurement still holds policy areas back.

    It holds while the newest batch that measured policy areas was refused and
    the prompt has not visibly changed since: the same digest, or either one
    unknown.
    """
    if artifact is None:
        return False
    measured = [row for row in artifact.batches if row.policy_gate_passed is not None]
    if not measured or measured[-1].policy_gate_passed:
        return False
    refused = measured[-1].policy_prompt_sha256
    return refused is None or prompt_sha256 is None or refused == prompt_sha256


@dataclass(frozen=True)
class PolicyBatch:
    """The rows one batch adds for their policy area, and why."""

    case_ids: tuple[str, ...]
    owed: int
    reference_rows: int
    backfill: int
    remaining: int
    held: str | None = None

    @property
    def asks(self) -> bool:
        """Whether the batch asks for any policy area at all."""
        return self.owed > 0 and self.held is None


def derive_policy_rows(
    *,
    frame: Sequence[tuple[str, str, bool]],
    topic_batch: Collection[str],
    artifact: QpTopicApplicationLabels | None,
    hand: Mapping[str, PolicyLabel],
    budget: int,
    seed: str,
    prompt_sha256: str | None,
) -> PolicyBatch:
    """Choose the rows a batch adds for their policy area, from committed state alone.

    ``frame`` is the application extract as ``(case_id, docket_number,
    policy_row)``, ``topic_batch`` the case ids the topic rule already chose,
    ``artifact`` the committed labels artifact, ``hand`` the hand labels, and
    ``budget`` the rows left under the labeling ceiling. A batch owes an area
    on each policy row in ``topic_batch`` that the artifact has not published,
    and on each published policy row without one. When it owes any, every
    hand-labeled row in the frame is added for the measurement, then the
    published rows lacking an area, ordered by ``seed``, up to ``budget``.

    Asks for nothing, with the reason in ``held``, while a refused measurement
    holds (:func:`refusal_hold`), when the frame's hand-labeled policy rows
    fall under the coverage floor (the gate could not pass, as the topic
    frame's coverage refusal reads it at extract time), or when ``budget``
    cannot hold the hand rows, since a batch carrying only some of them
    measures a different set; the topic batch goes ahead either way.
    """
    standing = {entry.case_id: entry for entry in artifact.entries} if artifact is not None else {}
    chosen = set(topic_batch)
    policy_rows = [(case_id, number) for case_id, number, flag in frame if flag]
    new_owed = sum(1 for case_id, _ in policy_rows if case_id in chosen and case_id not in standing)
    lacking = [
        case_id
        for case_id, _ in policy_rows
        if case_id in standing and standing[case_id].policy_area is None
    ]
    owed = new_owed + len(lacking)
    hand_rows = [case_id for case_id, number in policy_rows if _key(number) in hand]
    if not owed:
        return PolicyBatch(case_ids=(), owed=0, reference_rows=0, backfill=0, remaining=0)
    if refusal_hold(artifact, prompt_sha256):
        return PolicyBatch(
            case_ids=(),
            owed=owed,
            reference_rows=0,
            backfill=0,
            remaining=len(lacking),
            held="the last policy measurement was refused and the labeling prompt has not "
            "changed since; a re-run would re-measure the same labeler on the same rows",
        )
    if len(hand_rows) < COVERAGE_FLOOR * len(hand) or not hand:
        return PolicyBatch(
            case_ids=(),
            owed=owed,
            reference_rows=0,
            backfill=0,
            remaining=len(lacking),
            held=f"the frame holds {len(hand_rows)} of the {len(hand)} hand-labeled row(s) as "
            f"policy rows, under the {COVERAGE_FLOOR:.0%} coverage floor, so the measurement "
            "could not pass whatever the labeler did",
        )
    measured = [case_id for case_id in hand_rows if case_id not in chosen]
    if len(measured) > budget:
        return PolicyBatch(
            case_ids=(),
            owed=owed,
            reference_rows=0,
            backfill=0,
            remaining=len(lacking),
            held=f"the {len(measured)} hand-labeled policy row(s) do not fit the {budget} "
            "row(s) the topic batch leaves under the labeling ceiling",
        )
    taken = set(measured)
    fill = sorted(
        (case_id for case_id in lacking if case_id not in chosen and case_id not in taken),
        key=lambda case_id: _batch_order_key(case_id, seed),
    )
    drawn = fill[: budget - len(measured)]
    return PolicyBatch(
        case_ids=tuple(sorted([*measured, *drawn])),
        owed=owed,
        reference_rows=len(hand_rows),
        backfill=len(drawn),
        remaining=len(fill) - len(drawn),
    )


def measure_policy(
    *,
    entries: Sequence[QpTopicApplicationLabelEntry],
    policy_rows: Collection[str],
    hand: Mapping[str, PolicyLabel],
    prompt_sha256: str | None = None,
) -> tuple[QpTopicPolicyAgreement, dict[str, PolicyAreaLabel]] | None:
    """Measure the batch's policy areas against the hand labels; ``None`` if it asks for none.

    Returns the measurement and the usable areas by ``case_id``: every area
    given on a policy row. An area given on a row not marked ``policy_row`` is
    dropped and counted (``off_frame``) rather than failing the run, since the
    topic labels beside it are measured apart. The hand label is looked up by
    the line's docket number, which the extract join has already held to the
    extract's.
    """
    rows = set(policy_rows)
    if not rows:
        return None
    areas: dict[str, PolicyAreaLabel] = {}
    off_frame = 0
    for entry in entries:
        if entry.policy_area is None:
            continue
        if entry.case_id not in rows:
            off_frame += 1
            continue
        areas[entry.case_id] = entry.policy_area
    numbers = {entry.case_id: entry.docket_number for entry in entries}
    in_batch = sorted(case_id for case_id in rows if _key(numbers.get(case_id, "")) in hand)
    agree: Counter[str] = Counter()
    compared: Counter[str] = Counter()
    to_other: Counter[str] = Counter()
    named = [0, 0]
    certain = [0, 0]
    uncovered = 0
    for case_id in in_batch:
        expected = hand[_key(numbers[case_id])]
        given = areas.get(case_id)
        if given is None:
            uncovered += 1
            continue
        hit = given == expected.area
        compared[expected.area] += 1
        agree[expected.area] += hit
        to_other[expected.area] += expected.area != "other" and given == "other"
        if expected.area != "other":
            named[0] += hit
            named[1] += 1
        if not expected.uncertain:
            certain[0] += hit
            certain[1] += 1
    n = sum(compared.values())
    matched = sum(agree.values())
    rate = matched / n if n else None
    floor = max(compared.values()) / n if n else None
    gate = (
        rate is not None
        and floor is not None
        and rate >= AGREEMENT_GATE
        and rate > floor
        and bool(hand)
        and n / len(hand) >= COVERAGE_FLOOR
    )
    return (
        QpTopicPolicyAgreement(
            reference_rows=len(in_batch),
            reference_total=len(hand),
            agree=matched,
            n=n,
            named_agree=named[0],
            named_n=named[1],
            certain_agree=certain[0],
            certain_n=certain[1],
            rate=rate,
            floor=floor,
            uncovered=uncovered,
            off_frame=off_frame,
            per_area=[
                QpTopicPolicyAreaShare(
                    area=area, agree=agree[area], n=compared[area], labeled_other=to_other[area]
                )
                for area in POLICY_AREAS
                if compared[area]
            ],
            gate_passed=gate,
            prompt_sha256=prompt_sha256,
        ),
        areas,
    )


def accrue_policy(
    artifact: QpTopicApplicationLabels,
    *,
    agreement: QpTopicPolicyAgreement,
    areas: Mapping[str, PolicyAreaLabel],
    hand: Mapping[str, PolicyLabel],
) -> tuple[QpTopicApplicationLabels, int]:
    """Accrue one batch's policy areas onto the artifact its topic accrual just built.

    The artifact's newest ledger row is this batch's; it takes the policy
    figures. A passing measurement publishes, by the module docstring's rules,
    and becomes the artifact's ``policy_agreement``; a refused one publishes
    nothing and leaves the standing ``policy_agreement``. Returns the artifact
    and the count of areas published.
    """
    if not artifact.batches:
        raise QpTopicError("the artifact has no batch to record the policy measurement on")
    batch = artifact.batches[-1].batch
    published = 0
    entries = list(artifact.entries)
    if agreement.gate_passed:
        for index, entry in enumerate(entries):
            reference = hand.get(_key(entry.docket_number))
            if reference is not None:
                area, source = reference.area, "reference"
            elif entry.case_id in areas and entry.policy_area is None:
                area, source = areas[entry.case_id], "labeler"
            else:
                continue
            if entry.policy_area == area and entry.policy_source == source:
                continue
            entries[index] = entry.model_copy(
                update={"policy_area": area, "policy_source": source, "policy_batch": batch}
            )
            published += 1
    ledger = list(artifact.batches)
    ledger[-1] = ledger[-1].model_copy(
        update={
            "policy_agree": agreement.agree,
            "policy_n": agreement.n,
            "policy_published": published,
            "policy_gate_passed": agreement.gate_passed,
            "policy_prompt_sha256": agreement.prompt_sha256,
        }
    )
    update: dict[str, object] = {"batches": ledger, "entries": entries}
    if agreement.gate_passed:
        update["policy_agreement"] = agreement
    accrued = QpTopicApplicationLabels.model_validate(
        artifact.model_copy(update=update).model_dump()
    )
    return accrued, published


def render_policy(agreement: QpTopicPolicyAgreement, published: int) -> str:
    """The policy measurement as a run log reads it."""

    def share(agree: int, n: int) -> str:
        return f"{agree}/{n}" + (f" = {agree / n:.1%}" if n else "")

    rate = "n/a" if agreement.rate is None else f"{agreement.rate:.1%}"
    floor = "n/a" if agreement.floor is None else f"{agreement.floor:.1%}"
    lines = [
        f"policy areas (against {agreement.reference_rule} hand labels, not accuracy): "
        f"{agreement.agree}/{agreement.n} = {rate} against a {floor} constant-labeler floor; "
        f"named areas {share(agreement.named_agree, agreement.named_n)}, rows the hand set "
        f"does not flag uncertain {share(agreement.certain_agree, agreement.certain_n)}; "
        f"{agreement.reference_rows} of {agreement.reference_total} hand row(s) in the batch, "
        f"{agreement.uncovered} given no area, {agreement.off_frame} area(s) off the frame "
        f"dropped; gate {'passed' if agreement.gate_passed else 'refused'}; "
        f"{published} area(s) published",
    ]
    lines.extend(
        f"  {row.area}: {row.agree}/{row.n} ({row.labeled_other} called other)"
        for row in agreement.per_area
    )
    return "\n".join(lines)
