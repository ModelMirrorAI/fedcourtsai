"""The semantic claim family: its declaration seam and its descriptive roll-up.

``docs/outcome-decomposition.md`` (*The semantic family, alpha*) is the design
authority. This module is the semantic sibling of
:mod:`fedcourtsai.pipeline.claims`, and it is deliberately shaped like it so
that turning the family on is a declaration plus a prompt that asks for it,
rather than a new shape. What stays unbuilt even then is named in
``docs/outcome-decomposition.md``, *What remains unbuilt* — most of all the
predictor-side mandatory set: :func:`graded_units` refuses a non-conforming
*grader* block, and nothing reads ``Prediction.semantic_claims`` at all:

- the **declaration table**, per event kind and per exact event id, under a
  versioned set id, and authoritative over any grader's block. It is **empty**:
  no stage declares a semantic set, so :func:`declared_semantic_claim_set`
  returns ``None`` for every event, no prompt asks a cell for a semantic claim,
  and no committed artifact carries one. That state is asserted in the tests
  rather than left implicit;
- the **grade vocabulary** (:class:`~fedcourtsai.schemas.SemanticSupport`) and
  the ordinal projection the summary and the agreement number read it through;
- :func:`summarize_semantic_grades`, the roll-up that turns graded units into a
  descriptive census plus leave-one-out inter-grader agreement.

**What is deliberately absent, and why.** There is no scoring function here and
no baseline. The mechanical rule
``claim_score = (b - y)^2 - (p - y)^2`` requires a harness-computed prior ``b``
drawn from strictly-prior history; a proposition like "the majority rests on
textualist grounds" has no such frequency, and forcing one would manufacture a
number rather than measure one. So a semantic claim carries an ordinal grade,
the grades are reported descriptively with agreement beside them, and whether
any baseline is ever derivable is left as an empirical question for when
opinion text exists. A semantic grade is never run through ``claim_score`` and
never pooled with a mechanical claim total.

The candidate claim vocabulary — what kinds of proposition may be claimed, and
which of them survive that document's tests — is
sketched in that document and deliberately **not** encoded here: an id in a
module constant reads as a declaration, and nothing in this family is declared.

**Alpha.** ``semantic-v0`` is provisional and unproven against opinion text. It
is *not* a pre-registered commitment in the sense ``cert-v1`` and ``merits-v1``
are, and it constrains none of them: the process freeze governs the digest —
the prompt bytes plus the resolved actor config — and nothing here is asked for
by a prompt, so no digest moves, no cell produces a grade, and no published number
depends on any of it. That is precisely what lets it change freely. The first
set actually put to work arrives as ``semantic-v1`` with its own review;
supersession is the expected path, not an exception.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Literal

from ..ids import parse_event_kind
from ..leaderboard import kendall_tau_b
from ..schemas import (
    Evaluation,
    EventKind,
    SemanticClaimSummary,
    SemanticGradeBlock,
    SemanticGraderAgreement,
    SemanticGradeSummary,
    SemanticSupport,
    Stratum,
)

# The versioned set id every semantic declaration and grade block is stamped
# with. A change to which claims a set carries is a NEW version, never an
# in-place edit — the same discipline `cert-v1` and `sal-v1` keep. `v0` is the
# alpha: the first set put to work is `semantic-v1`, with its own review.
SEMANTIC_SET_V0 = "semantic-v0"

# The minimum unit count below which a derived figure is withheld: the
# per-claim `supported_share` and every grader's agreement coefficient. Set to
# match the mechanical judge validation's threshold
# (`claim_metrics.AGREEMENT_MIN_PAIRS`) because both key on the same kind of
# quantity — a count of units behind a published number — but kept as its own
# constant, since the two families' thresholds are separate choices and moving
# one must not silently move the other.
SEMANTIC_MIN_GRADED = 10

# Per event kind, and per exact event id: the set id and the declared semantic
# claims, in reporting order. **Both are empty on purpose.** No opinion body is
# ingested, so no semantic claim has anything to be graded against, and the
# blinding precondition `docs/outcome-decomposition.md` states is a precondition
# on grading rather than a detail of it. The tables are the seam: declaring a
# set later is an entry here plus a prompt that asks for it, not a new shape.
DECLARED_SEMANTIC_CLAIM_SETS: Mapping[EventKind, tuple[str, tuple[str, ...]]] = {}
DECLARED_SEMANTIC_CLAIM_SETS_BY_EVENT_ID: Mapping[str, tuple[str, tuple[str, ...]]] = {}

# The ordinal projection of the grade vocabulary, and the whole of what "ordinal"
# means here: three ranked levels, and `not-addressed` deliberately absent. The
# mask is not a low grade — it is the record failing to put the claim in
# question — so it has no position on this scale and never enters a mean, a
# share, or a rank correlation.
_ORDINAL: Mapping[SemanticSupport, int] = {
    SemanticSupport.unsupported: 0,
    SemanticSupport.partial: 1,
    SemanticSupport.supported: 2,
}


def declared_semantic_claim_set(event_id: str) -> tuple[str, tuple[str, ...]] | None:
    """The ``(set_version, claim_ids)`` an event declares semantically, or ``None``.

    ``None`` for **every** event today, because both declaration tables are
    empty: no stage declares a semantic set. The lookup order mirrors
    :func:`fedcourtsai.pipeline.claims.declared_claim_set` — exact event id
    first (the shape the minted merits event needs, since its kind segment is
    ``order`` and not every order event is merits), then event kind — so a
    future declaration lands as a table entry and nothing else.
    """
    by_id = DECLARED_SEMANTIC_CLAIM_SETS_BY_EVENT_ID.get(event_id)
    if by_id is not None:
        return by_id
    kind_slug = parse_event_kind(event_id)
    if kind_slug is None:
        return None
    try:
        kind = EventKind(kind_slug)
    except ValueError:
        return None
    return DECLARED_SEMANTIC_CLAIM_SETS.get(kind)


def ordinal(grade: SemanticSupport) -> int | None:
    """A grade's position on the ordinal scale, or ``None`` for the mask."""
    return _ORDINAL.get(grade)


@dataclass(frozen=True)
class GradedUnit:
    """One grader's grade of one declared semantic claim on one cell.

    The roll-up's input, kept as a plain record rather than read off the ledger,
    because no ledger carries one yet: :func:`graded_units` is the bridge from a
    committed :class:`~fedcourtsai.schemas.Evaluation` for when one does, and the
    tests exercise the roll-up over synthetic units so the plumbing is proven
    before any real grade exists.

    The **unit** — the thing agreement is measured over and the census counts
    once — is ``(case_id, event_id, predictor_id, claim_id)``: one claim about
    one predictor's forecast of one event, which several graders grade
    independently.
    """

    case_id: str
    event_id: str
    predictor_id: str
    grader_id: str
    claim_id: str
    grade: SemanticSupport
    declared_set_version: str = SEMANTIC_SET_V0

    @property
    def unit_key(self) -> tuple[str, str, str, str]:
        """The (cell, claim) identity graders are compared across."""
        return (self.case_id, self.event_id, self.predictor_id, self.claim_id)

    @property
    def cell_key(self) -> tuple[str, str, str]:
        """The graded cell's identity: case, event, predictor."""
        return (self.case_id, self.event_id, self.predictor_id)


def graded_units(evaluation: Evaluation) -> tuple[GradedUnit, ...]:
    """The graded units one evaluation carries, or ``()`` where it carries none.

    **The declaration, not the grader's block, fixes what is graded** — the
    discipline :func:`fedcourtsai.pipeline.claims.score_claims` keeps for the
    mechanical family, and the reason it matters more here: a grade is the
    grader's word, so a block that named its own claim ids would let a reader
    define the population it is measured over. The declared set is read first
    and the rows are matched to it.

    The block's ``declared_set_version`` is **checked, not overwritten**.
    Distrusting the grader's label justifies refusing a block that disagrees
    with the declaration; it does not justify silently relabelling one, which
    would pool grades formed under two declarations under a single version
    string — precisely what
    :attr:`~fedcourtsai.schemas.SemanticGradeSummary.declared_set_versions`
    exists to expose.

    ``()`` — never a crash — five ways: no semantic block; no declared set for
    the event; a block grading the same claim twice (two grades for one
    proposition, so take none rather than pick silently between them); a block
    that skips a declared claim, since the set is mandatory and a partial
    answer grades nothing rather than the half the grader chose; and a block
    stamped with a different declaration, which is not a partial answer to this
    one but an answer to another question. Rows outside the declared set are
    ignored.

    Returns ``()`` on every committed evaluation, on the second ground: no
    stage declares a semantic set.
    """
    block: SemanticGradeBlock | None = evaluation.semantic_grades
    declared = declared_semantic_claim_set(evaluation.event_id)
    if block is None or declared is None:
        return ()
    set_version, claim_ids = declared
    if block.declared_set_version != set_version:
        return ()
    graded: dict[str, SemanticSupport] = {}
    for row in block.grades:
        if row.claim_id in graded:
            return ()
        graded[row.claim_id] = SemanticSupport(row.grade)
    if any(claim_id not in graded for claim_id in claim_ids):
        return ()
    return tuple(
        GradedUnit(
            case_id=evaluation.case_id,
            event_id=evaluation.event_id,
            predictor_id=evaluation.predictor_id,
            grader_id=evaluation.evaluator_id,
            claim_id=claim_id,
            grade=graded[claim_id],
            declared_set_version=set_version,
        )
        for claim_id in claim_ids
    )


@dataclass
class _Census:
    """A mutable tally, finalized into a :class:`SemanticClaimSummary`."""

    supported: int = 0
    partial: int = 0
    unsupported: int = 0
    not_addressed: int = 0
    mask_disputed: int = 0
    cells: set[tuple[str, str, str]] = field(default_factory=set)

    def add_panel_grade(self, level: int, cell: tuple[str, str, str]) -> None:
        """Count one unit at its panel ordinal — the one place a grade becomes a count."""
        self.cells.add(cell)
        if level == _ORDINAL[SemanticSupport.supported]:
            self.supported += 1
        elif level == _ORDINAL[SemanticSupport.partial]:
            self.partial += 1
        elif level == _ORDINAL[SemanticSupport.unsupported]:
            self.unsupported += 1
        else:  # pragma: no cover - unreachable: `ordinal` yields only the three
            raise ValueError(f"not an ordinal grade level: {level!r}")

    def add_mask(self, cell: tuple[str, str, str]) -> None:
        """Count one unit the whole panel read as `not-addressed`."""
        self.cells.add(cell)
        self.not_addressed += 1

    def add_mask_dispute(self, cell: tuple[str, str, str]) -> None:
        """Count one unit the panel split on — mask against ordinal."""
        self.cells.add(cell)
        self.mask_disputed += 1

    def finalize(self, claim_id: str | None, *, min_graded: int) -> SemanticClaimSummary:
        graded = self.supported + self.partial + self.unsupported
        publishable = graded > 0 and graded >= min_graded
        return SemanticClaimSummary(
            claim_id=claim_id,
            supported=self.supported,
            partial=self.partial,
            unsupported=self.unsupported,
            not_addressed=self.not_addressed,
            mask_disputed=self.mask_disputed,
            graded=graded,
            cells=len(self.cells),
            supported_share=self.supported / graded if publishable else None,
        )


def _panel_ordinal(levels: list[int]) -> int:
    """The panel's grade for a unit: the **lower median** of the graders' ordinals.

    The lower median, not the floor of the median — on ``[0, 0, 2, 2]`` this is
    0 where the floor of the median would be 1. That is the point: it stays on
    the vocabulary rather than inventing a level between two, and an even split
    lands on the *less* supported side so that grader multiplicity can never
    manufacture credit.

    A unit is counted **once** however many graders graded it, or the census
    would weight a unit by its grader count — the same distortion the mechanical
    surface removes by deduplicating blocks to one per event. Unlike that
    deduplication this one discards information (the mechanical copies are
    byte-identical; graders genuinely differ), which is admissible only because
    the discarded disagreement is republished as the agreement figure.

    A summary convention of the alpha, not a pre-registered rule.
    """
    ordered = sorted(levels)
    return ordered[(len(ordered) - 1) // 2]


def summarize_semantic_grades(
    units: Iterable[GradedUnit],
    *,
    min_graded: int = SEMANTIC_MIN_GRADED,
    stratum: Stratum | None = None,
    process_scope: Literal["frozen", "all"] | None = None,
) -> SemanticGradeSummary:
    """Roll graded units up into the descriptive census plus grader agreement.

    Deterministic and offline: a pure function of the units, independent of
    their iteration order, producing no score and no total. What it computes,
    per declared claim and pooled:

    - the **census** — one entry per unit at the panel's grade
      (:func:`_panel_ordinal`), with the availability mask counted apart from
      the ordinal levels, and ``supported_share`` withheld below
      ``min_graded``;
    - the **mask dispute** — a unit some graders read as ``not-addressed`` and
      others graded on the ordinal scale. It enters neither the ordinal counts
      nor the agreement coefficient: the graders disagree about what the
      *record* discloses, which measures the record's adequacy rather than the
      predictor or the panel;
    - **leave-one-out inter-grader agreement**, per grader: Kendall's tau-b
      between that grader's ordinals and the mean of the *other* graders' over
      the units they share — the same estimator and the same leave-one-out
      shape as ``Leaderboard.evaluator_agreement``, over a different population
      and never the same figure. Withheld below ``min_graded`` units, with both
      the unit count and the distinct-cell count still published.

    Three obligations sit with the **caller**, because this function sees only
    the units it is handed:

    - **Segment before summarizing.** Strata, process versions, and stages are
      never pooled (``metrics/README.md``), and a ``GradedUnit`` carries none of
      them, so one call is one segment. ``stratum`` and ``process_scope`` are
      recorded verbatim and never inferred — a caller that does not state them
      produces a census recorded as undeclared: a null is the only signal
      there is, and an undeclared census is not publishable.
    - **Deduplicate re-runs.** An evaluator legitimately has several runs per
      cell (the evaluations path is keyed on ``run_id``), and two runs are two
      grades from one grader on one unit. Collapse them the way
      ``claim_metrics`` collapses blocks — newest wins, on
      ``(evaluation_clock(ev), evaluator_id, run_id)`` with the harness clock
      from ``fedcourtsai.integrity`` — before calling; otherwise the
      ``ValueError`` below fires on an ordinary state.
    - **Publish the agreement figure with any count or share taken from here.**

    Raises ``ValueError`` where one grader grades one unit twice — an ambiguity
    a caller must resolve, not a state to average over. :func:`graded_units`
    never produces one from a single evaluation.

    One honesty limit the shape cannot remove: the coefficient is agreement
    **conditional on the panel unanimously agreeing the record spoke**, since a
    mask-disputed unit is dropped before the points are built — and those are
    the units graders disagreed on most sharply. Read it against
    ``mask_disputed``, not merely beside it.
    """
    by_unit: dict[tuple[str, str, str, str], dict[str, SemanticSupport]] = defaultdict(dict)
    cells: set[tuple[str, str, str]] = set()
    graders: set[str] = set()
    versions: set[str] = set()
    for unit in units:
        panel = by_unit[unit.unit_key]
        if unit.grader_id in panel:
            raise ValueError(
                f"grader {unit.grader_id!r} graded {unit.claim_id!r} twice on the same cell"
            )
        panel[unit.grader_id] = unit.grade
        cells.add(unit.cell_key)
        graders.add(unit.grader_id)
        versions.add(unit.declared_set_version)

    per_claim: dict[str, _Census] = defaultdict(_Census)
    pooled = _Census()
    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    paired_cells: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    paired_claims: dict[str, set[str]] = defaultdict(set)
    for unit_key in sorted(by_unit):
        cell, claim_id = unit_key[:3], unit_key[3]
        panel = by_unit[unit_key]
        levels = {grader: ordinal(grade) for grader, grade in panel.items()}
        graded_levels = {g: lvl for g, lvl in levels.items() if lvl is not None}
        if not graded_levels:
            per_claim[claim_id].add_mask(cell)
            pooled.add_mask(cell)
            continue
        if len(graded_levels) != len(levels):
            per_claim[claim_id].add_mask_dispute(cell)
            pooled.add_mask_dispute(cell)
            continue
        panel_level = _panel_ordinal(list(graded_levels.values()))
        per_claim[claim_id].add_panel_grade(panel_level, cell)
        pooled.add_panel_grade(panel_level, cell)
        if len(graded_levels) < 2:
            continue  # nothing to agree with on this unit
        for grader, own in graded_levels.items():
            peers = [lvl for other, lvl in graded_levels.items() if other != grader]
            points[grader].append((float(own), sum(peers) / len(peers)))
            paired_cells[grader].add(cell)
            paired_claims[grader].add(claim_id)

    agreement: dict[str, SemanticGraderAgreement] = {}
    for grader in sorted(points):
        pairs = points[grader]
        suppressed = len(pairs) < min_graded
        agreement[grader] = SemanticGraderAgreement(
            rank_agreement=None if suppressed else kendall_tau_b(pairs),
            paired_units=len(pairs),
            cells=len(paired_cells[grader]),
            claims_pooled=len(paired_claims[grader]),
            suppressed=suppressed,
        )

    return SemanticGradeSummary(
        stratum=stratum,
        process_scope=process_scope,
        declared_set_versions=sorted(versions),
        cells=len(cells),
        units=len(by_unit),
        graders=len(graders),
        min_graded=min_graded,
        claims=[
            per_claim[claim_id].finalize(claim_id, min_graded=min_graded)
            for claim_id in sorted(per_claim)
        ],
        overall=pooled.finalize(None, min_graded=min_graded) if by_unit else None,
        agreement=agreement,
    )
