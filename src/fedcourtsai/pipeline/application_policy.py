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
one, so the field reaches the applications labeled before it existed; those
rows enter as ``policy_only``, their topic line neither measured nor
published. Whenever a batch owes any area, it carries every hand-labeled row
the frame holds too, for the measurement, exactly as a topic batch carries the
whole reference block. A batch owing none carries no policy rows at all.

**The measurement and its gate.** The labeler's area on each hand-labeled row
is compared with the hand label. The hand raters were not blind to the outcome
and read their own knowledge of a public case, which the labeler may not, so
the rate is agreement with that reference, not accuracy. The gate is the topic
gate's: the rate at least :data:`~fedcourtsai.pipeline.qp_topics.AGREEMENT_GATE`
and the compared rows at least
:data:`~fedcourtsai.pipeline.qp_topics.COVERAGE_FLOOR` of the hand set.

**What publishes.** Only a batch whose policy measurement passed publishes
areas, and it never touches a topic label. A hand-labeled row publishes its
hand label (``reference``); every other policy row publishes the labeler's
area (``labeler``). An area is set once: a row that already carries one keeps
it, except that a hand-labeled row always carries the hand label. A refused
policy measurement publishes nothing, leaves the standing areas and the
artifact's ``policy_agreement`` as they are, and is recorded on its batch's
ledger row, while the batch's topic labels publish under their own gate.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from ..schemas import (
    PolicyAreaLabel,
    QpTopicApplicationLabelEntry,
    QpTopicApplicationLabels,
    QpTopicApplicationPublishedEntry,
    QpTopicPolicyAgreement,
    QpTopicPolicyAreaShare,
)
from .policy_area import POLICY_AREAS, PolicyLabel
from .qp_topics import AGREEMENT_GATE, COVERAGE_FLOOR, QpTopicError, _batch_order_key


class PolicyFlags(NamedTuple):
    """One extract row's two policy flags."""

    policy_row: bool
    policy_only: bool


def read_policy_flags(path: Path) -> dict[str, PolicyFlags]:
    """Read each application extract row's ``policy_row`` and ``policy_only``, by ``case_id``.

    A row without the flags is read as neither, which is what an extract cut
    before the policy field existed means.
    """
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise QpTopicError(f"{path}: expected a JSON list of qp-corpus rows")
    flags: dict[str, PolicyFlags] = {}
    for row in payload:
        if not isinstance(row, dict) or "case_id" not in row:
            raise QpTopicError(f"{path}: row is not an application extract row")
        policy_row = row.get("policy_row", False)
        policy_only = row.get("policy_only", False)
        if not isinstance(policy_row, bool) or not isinstance(policy_only, bool):
            raise QpTopicError(f"{path}: {row['case_id']}: policy flags must be booleans")
        if policy_only and not policy_row:
            raise QpTopicError(f"{path}: {row['case_id']}: a policy_only row is a policy row")
        flags[str(row["case_id"])] = PolicyFlags(policy_row, policy_only)
    return flags


def _key(docket_number: str) -> str:
    return docket_number.strip().upper()


@dataclass(frozen=True)
class PolicyBatch:
    """The policy-only rows one batch adds, and why."""

    case_ids: tuple[str, ...]
    owed: int
    reference_rows: int
    backfill: int
    remaining: int


def derive_policy_rows(
    *,
    frame: Sequence[tuple[str, str, bool]],
    topic_batch: Collection[str],
    artifact: QpTopicApplicationLabels | None,
    hand: Mapping[str, PolicyLabel],
    budget: int,
    seed: str,
) -> PolicyBatch:
    """Choose the ``policy_only`` rows a batch adds, from committed state alone.

    ``frame`` is the application extract as ``(case_id, docket_number,
    policy_row)``, ``topic_batch`` the case ids the topic rule already chose,
    ``artifact`` the committed labels artifact, ``hand`` the hand labels, and
    ``budget`` the rows left under the labeling ceiling. A batch owes an area
    on each policy row in ``topic_batch`` that the artifact has not published,
    and on each published policy row without one. When it owes any, every
    hand-labeled row in the frame is added for the measurement, then the
    published rows lacking an area, ordered by ``seed``, up to ``budget``.
    Refuses a budget that cannot hold the hand rows, since a batch that carries
    only some of them measures a different set.
    """
    standing: dict[str, QpTopicApplicationPublishedEntry] = (
        {entry.case_id: entry for entry in artifact.entries} if artifact is not None else {}
    )
    chosen = set(topic_batch)
    policy_rows = [(case_id, number) for case_id, number, flag in frame if flag]
    new_owed = sum(1 for case_id, _ in policy_rows if case_id in chosen and case_id not in standing)
    lacking = [
        case_id
        for case_id, _ in policy_rows
        if case_id in standing and standing[case_id].policy_area is None
    ]
    hand_rows = [case_id for case_id, number in policy_rows if _key(number) in hand]
    owed = new_owed + len(lacking)
    if not owed:
        return PolicyBatch(case_ids=(), owed=0, reference_rows=0, backfill=0, remaining=0)
    measured = [case_id for case_id in hand_rows if case_id not in chosen]
    if len(measured) > budget:
        raise QpTopicError(
            f"{len(measured)} hand-labeled policy row(s) do not fit the {budget} row(s) left "
            "under the labeling ceiling; every batch that publishes policy areas carries the "
            "whole hand set"
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
    flags: Mapping[str, PolicyFlags],
    hand: Mapping[str, PolicyLabel],
) -> tuple[QpTopicPolicyAgreement, dict[str, PolicyAreaLabel]] | None:
    """Measure the batch's policy areas against the hand labels; ``None`` if it carries none.

    Returns the measurement and the usable areas by ``case_id``: every area
    given on a policy row. An area given on a row not marked ``policy_row`` is
    dropped and counted (``off_frame``) rather than failing the run, since the
    topic labels beside it are measured apart.
    """
    policy_rows = {case_id for case_id, flag in flags.items() if flag.policy_row}
    if not policy_rows:
        return None
    areas: dict[str, PolicyAreaLabel] = {}
    off_frame = 0
    for entry in entries:
        if entry.policy_area is None:
            continue
        if entry.case_id not in policy_rows:
            off_frame += 1
            continue
        areas[entry.case_id] = entry.policy_area
    numbers = {entry.case_id: entry.docket_number for entry in entries}
    in_batch = sorted(case_id for case_id in policy_rows if _key(numbers.get(case_id, "")) in hand)
    agree: Counter[str] = Counter()
    compared: Counter[str] = Counter()
    uncovered = 0
    for case_id in in_batch:
        expected = hand[_key(numbers[case_id])].area
        given = areas.get(case_id)
        if given is None:
            uncovered += 1
            continue
        compared[expected] += 1
        agree[expected] += given == expected
    n = sum(compared.values())
    matched = sum(agree.values())
    rate = matched / n if n else None
    floor = max(compared.values()) / n if n else None
    gate = (
        rate is not None
        and rate >= AGREEMENT_GATE
        and bool(hand)
        and n / len(hand) >= COVERAGE_FLOOR
    )
    return (
        QpTopicPolicyAgreement(
            reference_rows=len(in_batch),
            reference_total=len(hand),
            agree=matched,
            n=n,
            rate=rate,
            floor=floor,
            uncovered=uncovered,
            off_frame=off_frame,
            per_area=[
                QpTopicPolicyAreaShare(area=area, agree=agree[area], n=compared[area])
                for area in POLICY_AREAS
                if compared[area]
            ],
            gate_passed=gate,
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
    nothing. Returns the artifact and the count of areas published.
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
        }
    )
    update: dict[str, object] = {"batches": ledger, "entries": entries}
    if agreement.gate_passed:
        update["policy_agreement"] = agreement
    return QpTopicApplicationLabels.model_validate(
        artifact.model_copy(update=update).model_dump()
    ), published


def render_policy(agreement: QpTopicPolicyAgreement, published: int) -> str:
    """The policy measurement as a run log reads it."""
    rate = "n/a" if agreement.rate is None else f"{agreement.rate:.1%}"
    floor = "n/a" if agreement.floor is None else f"{agreement.floor:.1%}"
    lines = [
        f"policy areas (against {agreement.reference_rule} hand labels, not accuracy): "
        f"{agreement.agree}/{agreement.n} = {rate} against a {floor} constant-labeler floor; "
        f"{agreement.reference_rows} of {agreement.reference_total} hand row(s) in the batch, "
        f"{agreement.uncovered} given no area, {agreement.off_frame} area(s) off the frame "
        f"dropped; gate {'passed' if agreement.gate_passed else 'refused'}; "
        f"{published} area(s) published",
    ]
    lines.extend(f"  {share.area}: {share.agree}/{share.n}" for share in agreement.per_area)
    return "\n".join(lines)
