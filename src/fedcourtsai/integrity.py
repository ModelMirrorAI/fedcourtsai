"""The mechanical integrity rules a scored cell must pass, and what qualifies a pass.

Clock, run, claim, leak, stratum — five pass/fail rules — plus one description
that a pass does not settle: how far behind its own frozen placement the cell
ran.

Five questions every scoring surface needs answered the same way, in one leaf
module so no join can answer them differently:

**Whose clock says when a cell ran?** The pre-registration boundary must not
rest on a clock the agent controls (:mod:`fedcourtsai.process_version` states
the rule for the freeze partition), and the stratum boundary is the same kind
of boundary: a predictor that back-dated its ``created_at`` to before a
resolution would otherwise classify as a forward forecast. :func:`cell_clock`
prefers the harness-written process stamp and falls back to the agent-written
``created_at`` only where no stamp exists — and an unstamped cell is outside
the frozen headline by construction (``is_frozen`` refuses a null), so the
fallback only ever positions cells — and adjudicates breaches — inside
diagnostic views, where an agent-movable clock costs a diagnostic row, never
a claim. Never the git
commit timestamp: the stratified join is documented deterministic and offline
over committed artifacts, and a git read would break that.

**Which of a cell's gradings counts?** A re-graded cell commits a second
``evaluation.json`` under a new run id beside the first, and both are real
artifacts of the ledger. Only one of them is an observation, so every scoring
surface collapses the re-runs to the newest before it counts anything
(:func:`latest_evaluation_runs`) — never across evaluators, whose multiplicity
is the panel.

**May the cell's forward claim be believed?** A cell whose harness-written
record says ``mode: forward`` while its event had resolved before the harness
clock's day is not a forecast — the claim and the record contradict each
other, and no scored stratum is a valid home for the observation
(:func:`forward_claim_breach`). What happens to such a cell is the
pre-registered :data:`FORWARD_CLAIM_POLICY`; the boards publish the policy and
the count beside their numbers so an exclusion can never be silent. A believable
forward claim is still not an equally *forward* one, so the same clock answers
the descriptive half: :func:`context_lag_days` measures how old the moment the
cell was placed at was when it ran, which is what separates a cell forecasting
its increments from one able to read them off a docket that moved since the
cutoff.

**Did the graded prediction read its own outcome?** The evaluators' coarse
leakage bit (``leakage_suspected``) answers it, and :func:`leakage_excluded`
turns the bit into the one rule every scoring surface applies: a cell carrying
it leaves every rank key and every scored aggregate. Independent of the claim
rule above and of the stratum below — the clock cannot see a leak, so a leaked
cell whose outcome resolves *after* its prediction's clock classifies forward
and only this bit keeps it out. It decides membership, never value: no score on
the record is touched, and the boards publish the count
(:func:`leakage_record`) beside their figures so the exclusion can never be
silent.

**Which stratum does the cell belong to?** The pre-registration split is the
same question asked once more, and it rests on the same clock, so the
vocabulary lives here too: the :data:`FORWARD` / :data:`RETROSPECTIVE` /
:data:`PROCEDURAL` names, the :data:`StratifiedCell` tuple the join yields, and
:func:`classify_stratum`, the single definition of the timing boundary. The
leaderboard, the claim metrics, the ops report and the store's join all read
them from here rather than off the board, which is what lets
:mod:`fedcourtsai.store` — the module every artifact reader goes through —
stay clear of the board that is built on top of it.

Everything here is derived from committed, harness-written artifacts — the
context and the stamp are the harness's fields (AGENTS.md), the outcome is the
docket record — so the rules are properties of the record, never of predictor
behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, date, datetime
from typing import Literal

from .schemas import (
    Evaluation,
    ForwardClaimRecord,
    LeakageExclusionRecord,
    Moment,
    Outcome,
    Prediction,
    ProcessVersion,
    Stage,
    Stratum,
)

#: What the scoring funnel does with a cell whose forward claim its own record
#: contradicts. ``"exclude"`` (the registered value) drops the cell from
#: every scored stratum: the retrospective stratum is the iteration signal,
#: measured over cells the clock honestly places after their resolution —
#: replay cells held to replay etiquette, and late cells that never claimed
#: otherwise — and a cell that believed it was forward, retrieved
#: unrestricted, and asserted a false mode degrades exactly that signal.
#: ``"retrospective"`` instead forces the cell into the retrospective stratum
#: (procedural still wins for a mootness-basis outcome) while counting it on
#: the board. A maintainer
#: moves this in a reviewed commit, the ``FROZEN_*`` pattern; the boards
#: record which policy built them, so a flip is one commit plus a refresh.
ForwardClaimPolicy = Literal["exclude", "retrospective"]
FORWARD_CLAIM_POLICY: ForwardClaimPolicy = "exclude"

#: One joined cell as ``store.iter_stratified_evaluations`` yields it:
#: ``(evaluation, stratum, stage, moment)``. The stage and the moment travel
#: together because neither alone identifies the population a cell belongs to —
#: the stage names the question, the moment names the information set that
#: answered it.
StratifiedCell = tuple[Evaluation, Stratum, Stage | None, Moment | None]

FORWARD: Stratum = "forward"
RETROSPECTIVE: Stratum = "retrospective"
# Cells whose outcome was mootness practice (the outcome's disposition_basis):
# the ground-truth label tracks the Court's vacatur wording rather than
# cert-worthiness, so these aggregate separately and never enter the ranking.
PROCEDURAL: Stratum = "procedural"


def classify_stratum(prediction_clock: datetime, resolved_at: date) -> Stratum:
    """Which pre-registration stratum a scored cell belongs to.

    Retrospective when the event's resolution predates the prediction's
    **harness clock** (:func:`cell_clock` — the process stamp, else the
    unstamped cell's ``created_at``; the boundary must not rest on a clock the
    agent controls). A same-day tie also counts as retrospective — the
    conservative reading, so a cell whose ordering within the day is unknowable
    is never presented as a forward forecast.
    """
    return RETROSPECTIVE if resolved_at <= prediction_clock.date() else FORWARD


def _harness_clock(process_version: ProcessVersion | None, created_at: datetime) -> datetime:
    """The one stamp-else-created_at rule behind both typed clocks.

    Private so the normalization is written once; the two public names exist
    for call-site type safety, not for divergent rules.
    """
    stamped = process_version.stamped_at if process_version is not None else None
    clock = stamped if stamped is not None else created_at
    return clock if clock.tzinfo is not None else clock.replace(tzinfo=UTC)


def cell_clock(prediction: Prediction) -> datetime:
    """When the harness ran this cell: the process stamp, else ``created_at``.

    Normalized to an aware datetime (a bare timestamp reads as UTC — the only
    zone any writer in this pipeline uses), so clocks from different writers
    always compare.
    """
    return _harness_clock(prediction.process_version, prediction.created_at)


def context_lag_days(prediction: Prediction) -> int | None:
    """How old the moment a forward cell was placed at was when the cell ran.

    Placement age, not freeze age: on a ``dated`` cell the payload itself was
    frozen a day or more before the cutoff, and it is the placement the cohort
    is filed under that this counts from. The days between the instant the cell
    was placed at — ``context.cutoff``, else the provisioned
    ``context.snapshot_date`` where no moment fixed one —
    and the cell's harness clock day (:func:`cell_clock`). Derived rather than
    stored, so it reads the same off every forward cell whose harness wrote a
    context and can segment the committed ledger retroactively, where a stored
    field could only ever describe cells minted after it.

    **This is placement lag, not pull staleness, and the two are different
    clocks.** Pull staleness is how old the corpus payload was, and
    ``provision-snapshot --max-snapshot-age-days`` bounds it — on the *latest*
    payload, before any cut. Placement lag is how long ago the moment the cell
    was placed at happened. A ``truncated`` cell's own ``snapshot_date`` is its
    cutoff (the reconstructed docket is dated by the moment, not by the pull
    whose bytes it was rebuilt from), so reading lag as staleness reads the
    moment's age as the corpus's — a cell provisioned from a same-day pull can
    carry weeks of lag with no stale byte in it. The one place the two
    coincide is the fallback branch: on an ``as-stored`` cell nothing fixed a
    cutoff, so ``snapshot_date`` *is* the pull's date and the number returned
    *is* payload age — bounded by the staleness gate wherever it is armed.
    That is why the distribution is read segmented on
    ``context.snapshot_provenance`` rather than pooled: pooled, it mixes the
    two mechanisms under a heading that disclaims one of them.

    **A nonzero lag is not a defect**, and it has two mechanisms that the
    reading has to keep apart (``metrics/README.md`` states the segmentation).
    *Cohort-completion lag* is the price of cohort comparability: every engine
    of a cohort must read one information set, so a cohort completed late is
    completed at the cutoff it opened with, not re-frozen to the day the last
    cell happened to run. *Moment pendency* is structural and no scheduling
    remedy touches it: a moment placed at an order whose disposition pends for
    months puts every cell of it far behind its own cutoff however promptly the
    cohort ran. What the lag costs is
    within-stratum comparability of the *claims* — a cell whose retrieval can
    observe weeks of post-cutoff docket is closer to reporting an increment
    than to forecasting it — which is why any figure pooling forward cells owes
    the lag distribution beside it (``metrics/README.md``).

    ``None`` where the number would assert something the record does not: a
    null-context cell did read a provisioned snapshot, but the record does not
    say which, so no lag is derivable — never read that ``None`` as a zero. The
    carve :func:`forward_claim_breach` makes holds here for the same reason — a
    ``replay`` cell runs long after its cutoff by design, so its lag measures
    the back-test's own age rather than any drift in what it could claim — and
    a ``None`` from either cause belongs in a published not-derivable count,
    not in the distribution.

    ``-1`` on a cell run the day its moment **opened**, which is the floor: the
    cutoff is the day *after* the opening
    (:func:`fedcourtsai.provision.moment_cutoff`), so the earliest placement a
    cell can be given is one day ahead of it. ``0`` is the cell run on its
    cutoff. Kept signed rather than clamped, so the two stay distinguishable.
    """
    context = prediction.context
    if context is None or context.mode != "forward":
        return None
    placed_at = context.cutoff if context.cutoff is not None else context.snapshot_date
    return (cell_clock(prediction).date() - placed_at).days


def evaluation_clock(evaluation: Evaluation) -> datetime:
    """When the harness ran this evaluation: the process stamp, else ``created_at``.

    The evaluation-side sibling of :func:`cell_clock`, and a distinct name on
    purpose: the prediction clock draws the pre-registration boundary, while
    this one orders re-runs of one grader on one cell (newest wins), so a join
    reaching for the wrong artifact's clock reads as the type error it is.
    Same normalization — a bare timestamp reads as UTC, so clocks from
    different writers always compare instead of raising on a naive/aware mix.

    The ``created_at`` fallback is contained the same way the prediction
    side's is: ``graded_post_freeze`` refuses a null stamp, so inside a
    frozen-scope build every evaluation is stamped and the agent-movable
    clock never picks a winning block behind a claimable mean — the fallback
    only ever orders diagnostic (``--all-versions``) views. The stamp is the
    vintage of the invocation that **produced** the record: an ordinary
    ``stamp-cell`` writes the graded block and the stamp together, so on a
    once-graded cell the stamp dates the statpack the block was pooled from.
    A ``stamp-cell --regrade`` parts them on purpose — it re-derives the block
    against the pools committed at re-grade time while preserving the producing
    run's stamp, because a corrected outcome changes the record's inputs and
    not the process that judged it — so the stamp bounds the block's vintage
    from below rather than pinning it. Re-grading a set of cells together is
    what keeps **that set** internally consistent, and it is the operator's
    discipline rather than the code's: re-grade a whole cohort against one
    committed statpack, never a cell at a time across a moving pack. It buys no
    more than that — the ledger already spreads across pack vintages between
    runs, which no re-grade widens, and the realized-Term column is immune
    either way, being built from one handed-in pack. A backdated
    ``--stamped-at`` misstates the vintage outright, which is a reason the flag
    is harness-side only.
    """
    return _harness_clock(evaluation.process_version, evaluation.created_at)


#: One graded cell's identity: ``(case, event, predictor, evaluator)``.
#: Deliberately **not** keyed on the run — the run is what varies between a
#: grading and its re-grading, so two runs sharing this key are one observation
#: — and deliberately keyed **on** the evaluator, because two judges of one
#: prediction are two observations, not a duplicate. (``leaderboard``'s
#: ``EvaluationKey`` is this tuple plus the run: the identity of a *grading*,
#: which is what a per-cell figure computed at render must be keyed on.)
EvaluationCellKey = tuple[str, str, str, str]


def evaluation_cell_key(evaluation: Evaluation) -> EvaluationCellKey:
    """This evaluation's :data:`EvaluationCellKey`."""
    return (
        evaluation.case_id,
        evaluation.event_id,
        evaluation.predictor_id,
        evaluation.evaluator_id,
    )


def latest_evaluation_runs[T](items: Iterable[T], evaluation: Callable[[T], Evaluation]) -> list[T]:
    """Collapse re-runs of one grader on one cell to the newest, in input order.

    The ledger keeps every grading a judge committed, so a re-graded cell holds
    two ``evaluation.json`` files that describe **one** observation. Counting
    both would let a re-grade reweight a predictor's standing with no trace —
    silently, since nothing about the aggregate looks wrong — so every surface
    that aggregates the ledger collapses on :data:`EvaluationCellKey` first.

    Newest wins, on the **harness clock** (:func:`evaluation_clock` — the
    process stamp, with the agent-written ``created_at`` only where no stamp
    exists, which the frozen scope excludes; aware-normalized, so a naive/aware
    mix cannot raise). ``run_id`` breaks a clock tie, highest winning: the
    evaluator is already part of the key and so cannot decide one, and the
    tiebreak is the opposite convention from the prediction side's
    ``max(predictions, key=cell_clock)``, which keeps the first path. Survivors
    hold the **winner's** position in the input, which is path order at every
    ledger read — and a cell's runs are path-adjacent under both ledger globs
    (``.../evaluations/<evaluator>/<predictor>/<run>/``), so the survivors come
    back in the order the uncollapsed stream had and the collapse cannot move a
    byte of a deterministic artifact.

    The collapse stops at the evaluator: panel means, the ``evaluators`` count,
    and both agreement views rest on several judges reading one cell, so
    pooling them here would erase the multiplicity that is the measurement.

    ``evaluation`` names the ``Evaluation`` inside each item, so a caller
    carrying the record's path or its joined siblings collapses the whole row
    rather than re-deriving it afterwards.
    """
    latest: dict[EvaluationCellKey, tuple[tuple[datetime, str, str], int, T]] = {}
    for position, item in enumerate(items):
        record = evaluation(item)
        order = (evaluation_clock(record), record.evaluator_id, record.run_id)
        key = evaluation_cell_key(record)
        current = latest.get(key)
        if current is None or order > current[0]:
            latest[key] = (order, position, item)
    return [item for _order, _position, item in sorted(latest.values(), key=lambda kept: kept[1])]


def latest_evaluations(evaluations: Iterable[Evaluation]) -> list[Evaluation]:
    """:func:`latest_evaluation_runs` where the item *is* the evaluation."""
    return latest_evaluation_runs(evaluations, lambda evaluation: evaluation)


def forward_claim_breach(prediction: Prediction, outcome: Outcome) -> str | None:
    """Why this cell's own harness record contradicts its forward claim.

    ``None`` unless the harness-written context claims ``forward`` **and** the
    event had resolved strictly before the cell's harness clock day
    (:func:`cell_clock`). A same-day tie is deliberately **not** a breach: the
    record is ambiguous there — an honest forward cell that lost a same-day
    race looks identical to a mis-provisioned one — so the tie falls to the
    stratum boundary's own conservative rule (same-day counts as
    retrospective) rather than to exclusion. A null-context cell cannot
    breach: it asserts nothing, and the clock alone already routes it
    retrospective wherever it ran late. A ``replay`` cell cannot breach:
    running after the resolution is its design.
    """
    context = prediction.context
    if context is None or context.mode != "forward":
        return None
    resolved_at = outcome.resolved_at
    clock_date = cell_clock(prediction).date()
    if resolved_at < clock_date:
        return (
            f"the record claims a forward cell, but the event resolved "
            f"{resolved_at.isoformat()} — before the cell's harness clock day "
            f"({clock_date.isoformat()})"
        )
    return None


#: The reason recorded against a cell the leakage bit drops. One string, so
#: every surface names the exclusion identically and the stderr line, the board
#: block and the tests cannot drift apart.
LEAKAGE_EXCLUSION_REASON = (
    "the grading records `leakage_suspected` — the prediction may have read its "
    "own outcome, so the cell is an observation of no scored stratum"
)


def leakage_excluded(evaluation: Evaluation) -> bool:
    """Whether this grading's leakage bit keeps its cell out of every scored figure.

    True only on an explicit ``leakage_suspected: true``. A **null** bit is "not
    assessed" — offline evaluators and records written before the field existed
    — and is deliberately not read as a suspicion: excluding on a null would
    empty the board of every unassessed cell, which is most of the ledger.

    The rule is independent of :func:`forward_claim_breach` and of
    :func:`classify_stratum`, and that independence is the point. The timing
    split rests on the clock, so a leaked cell whose outcome resolves *after*
    its prediction's harness clock classifies **forward** and would be published
    as claimable forecasting performance; the clock cannot see the leak, and
    this bit is the only thing that can. It is an exclusion, never a stratum
    change: a cell that carries it leaves every rank key and every scored
    aggregate rather than moving to a different one, because the retrospective
    stratum is the iteration signal and a cell that read its own outcome
    degrades exactly that.
    """
    return evaluation.leakage_suspected is True


def leakage_record(
    excluded: Sequence[tuple[str, str]] | int, assessed: int = 0
) -> LeakageExclusionRecord:
    """The leakage-exclusion record every scoring surface publishes beside its numbers.

    ``excluded`` is the exclusion ledger's ``(predictor_id, reason)`` pairs (a
    bare count is accepted where a caller has only the number and no
    per-predictor split to publish), mirroring :func:`forward_claim_record`.
    """
    if isinstance(excluded, int):
        return LeakageExclusionRecord(excluded=excluded, assessed=assessed)
    by_predictor: dict[str, int] = {}
    for predictor_id, _reason in excluded:
        by_predictor[predictor_id] = by_predictor.get(predictor_id, 0) + 1
    return LeakageExclusionRecord(
        excluded=len(excluded),
        assessed=assessed,
        by_predictor=dict(sorted(by_predictor.items())),
    )


def forward_claim_record(
    excluded: Sequence[tuple[str, str]] | int, claimed_forward: int = 0
) -> ForwardClaimRecord:
    """The record every scoring surface publishes beside its numbers.

    ``excluded`` is the exclusion ledger's ``(predictor_id, reason)`` pairs
    (a bare count is accepted where a caller has only the number and no
    per-predictor split to publish).
    """
    if isinstance(excluded, int):
        return ForwardClaimRecord(
            policy=FORWARD_CLAIM_POLICY, excluded=excluded, claimed_forward=claimed_forward
        )
    by_predictor: dict[str, int] = {}
    for predictor_id, _reason in excluded:
        by_predictor[predictor_id] = by_predictor.get(predictor_id, 0) + 1
    return ForwardClaimRecord(
        policy=FORWARD_CLAIM_POLICY,
        excluded=len(excluded),
        claimed_forward=claimed_forward,
        by_predictor=dict(sorted(by_predictor.items())),
    )
