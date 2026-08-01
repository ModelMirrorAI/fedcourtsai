# Salience: which cases we predict, and the scores we pre-register

The design contract for **salience-ordered prediction scope** — the gate that
decides *which* eligible cert petitions are worth the expensive three-engine
tournament — and for the two **pre-registered scores** the program commits before
a term plays out: the deterministic **salience score** (which cases to forecast,
ranked) and the model-produced **big-case score** (how big we called them). For
the ingestion/prediction scope split this refines see the *Scope* section of
[data-pipeline.md](data-pipeline.md); for the cost argument it hangs on see
[budget.md](budget.md); for where the board lands on the roadmap see
[milestones.md](milestones.md).

This doc fixes the vocabulary and the seams and describes the gate as it runs;
its knobs are the `salience:` block of `config/tracking.yaml`. Where a piece is
still ahead of the implementation, it says so in place.

## Why salience

The agentic stages cost one to two orders of magnitude more than ingestion, so
running the tournament over the whole cert denominator would spend that budget
on thousands of petitions denied as a matter of course. Prediction scope is
therefore **salience-ordered**: the hard eligibility filters run first, then a
cheap deterministic score **ranks** the surviving petitions and the
predict/evaluate tournament runs only on the most salient slice, up to a
fundable **capacity `N`**.

The gate is live. The selection pass runs inside every live-channel cycle, its
decision is carried by the `salience_selected` corpus latch, and both the
predict matrix and the pull queue read that latch (*Selection* below).

Two scores fall out, and they are deliberately distinct:

- The **salience score** is *deterministic and pre-conference* — the pipeline's own
  cheap opinion of which petitions are worth forecasting, computed from features
  already in the corpus, published as a ranking before the conference sits.
- The **big-case score** is *model-produced and pre-registered* — each predictor's
  opinion of a case's stakes, committed with the grant/deny forecast and judged
  later by an independent evaluator rather than against a ground truth. It is a
  direct answer to the "bigness is only ever assigned in hindsight" critique: the
  git timestamp proves the stakes call preceded the term.

## The three tiers

Selection is a funnel, cheap filters first:

- **Tier 0 — hard eligibility (deterministic, at the row).**
  `corpus.OUT_OF_SCOPE_RULES`, evaluated through `out_of_scope_reason_full`,
  including the rule excluding **pro se / in-forma-pauperis** petitions. Fee
  class is derivable — IFP serials start at `IFP_SERIAL_BASE` (`5001`) in the
  SCOTUS docket number (`supremecourt.parse_scotus_docket_number`), so the rule
  is a row-only predicate needing no new column. This is a **documented scope
  decision** — a named rule in `OUT_OF_SCOPE_RULES` carrying its own reason
  string, not a silent drop: IFP grants are rare but non-zero (Gideon arrived
  IFP), so excluding them is a deliberate, recorded choice, not a claim that
  IFP cases never matter. A Tier-0 exclusion means *never predict, and prune any
  prediction already committed* — the same destructive-on-purpose semantics
  every hard-scope rule already carries.
- **Tier 1 — salience scoring (cheap, over all eligible).** A deterministic score
  over every Tier-0 survivor, from features the corpus already carries. This is a
  *scoring* pass, **not** a cheap *prediction* of every case — the whole point is to
  avoid spending tournament budget on the denominator.
- **Tier 2 — the tournament (expensive, over the salient slice).** The existing
  three-engine, cross-evaluated predict/evaluate, unchanged, run only on the
  selected cases. This is where the big-case score is produced and where the
  segment base rate (below) becomes the agent's prior and the evaluator's baseline.

## The salience score (`sal-v1`)

A **frozen, versioned** function — `salience.version`, first release `sal-v1` — a
weighted combination of Tier-1 features. It is reproducible from committed corpus
inputs; a scoring-function change is a **new version**, never an in-place edit, so
a skeptic can replay any past ranking against the version that produced it.

`sal-v1`'s weights are **fit to the empirical per-bucket grant rates**, not
hand-tuned: a case's score approximates `P(grant | its relist / CVSG / circuit /
fee-class cell)` read off the committed statpack, so the ranking is directly
interpretable — a higher score means a historically higher grant rate for cases
like this — and calibrated to reality rather than to arbitrary coefficients. The
exact coefficients are pinned and documented in the implementing change against
the statpack numbers in force.

`sal-v1` uses only features that exist today and are available **pre-conference**:

- **Relist count** — `distribution_count − 1`, floored at 0 (a petition
  distributed once has not been relisted). The strongest cheap signal: the
  committed statpack shows relist-0 petitions granting ~0.8% but relist-2 at
  ~39.4%. `NULL` `distribution_count` (never live-parsed) scores as unknown, not 0.
- **CVSG present** — `cvsg_date IS NOT NULL`. A Call for the Views of the Solicitor
  General is the Court's own signal of stakes; CVSG petitions grant ~28% vs ~3%
  without.
- **Originating circuit** — `originating_court`. Circuits vary in grant rate; a
  documented per-circuit weight.
- **Fee class** — paid vs IFP. (IFP is Tier-0-excluded, so within the scored set
  this is near-constant; retained so the score composes if the Tier-0 rule is ever
  relaxed.)

Deferred, each with a stated reason:

- **Below-decision division** (a dissent or en-banc split in the court below) is a
  strong salience signal but is **not recoverable** from the corpus today — no
  column, and not cheaply derivable from stored text. A `sal-v2` feature once the
  below-court signal is extracted.
- **Amicus-brief count** is arguably the strongest pre-decision salience proxy, but
  its presence in the supremecourt.gov docket JSON is **unverified** and no
  extractor counts it. A `sal-v2` enrichment if a data-availability check confirms
  it; `sal-v1` is designed to stand without it.
- **Cheap-model QP enrichment** — an optional model pass over the questions
  presented to sharpen the deterministic score — is **default off** for the first
  release, so `sal-v1` is fully deterministic and free.

## Selection — deterministic rank-and-cap, sticky per conference

Selection ranks the scored set and caps it to `N`. **The enforcement mechanism is
the load-bearing decision here, because the obvious one is wrong.**

**Why below-cap is not a scope exclusion.** The shared reason evaluator
`out_of_scope_reason_full` is consumed by several seams, and one of them —
`cleanup.find_out_of_scope_predictions` — **deletes committed prediction
artifacts** (`shutil.rmtree`) for any case it flags. That deletion is correct for a Tier-0 hard
exclusion (a pre-1925 mandatory case should never carry a prediction). It is
**fatal** for below-cap selection: a petition legitimately predicted early, whose
salience later drifts below the cap as fresher petitions distribute, must **keep**
its committed forward forecast — deleting it would destroy exactly the
pre-registered prediction the whole thesis rests on and corrupt the leaderboard's
forward stratum. So below-cap selection **must not** route through
`out_of_scope_reason_full` / `predict_excluded` / cleanup.

**The mechanism: a separate, sticky latch.** A case-level corpus column
`salience_selected` (with `salience_score` and `salience_version` alongside),
written only by the deterministic selection pass — applied inside every live
cycle, with `reconcile-salience-selection` as its manual entry point,
structurally analogous to the scope reconcile — carries the decision:

1. **Cohort key = `distributed_for_conference`.** Capacity is a *per-conference*
   fundable slice, not a global one. This is what makes replay tractable: "why this
   case and not that one" is always answered within one conference's candidate pool
   at a fixed score version.
2. **Score** every Tier-0-eligible SCOTUS row in the cohort (`salience_score`,
   `salience_version`) — including an already-**decided** petition, so its
   historical row still carries a band. A decided petition never enters cohort
   selection, though: it has no open event left to predict, and latching it
   would muddy "`salience_selected` = tournament spend" with cases the gate
   never actually funds.
3. **Always-include carve-outs**, unconditionally selected **above** the `N`
   budget: CVSG petitions (`cvsg_date IS NOT NULL`) and anything at or above a
   documented **salience floor** — set at the grant-rate level of clearly
   cert-worthy cases, ≈ the relist-2 / CVSG band (~25%+ historical grant rate). A
   major case can never fall below the capacity line.
4. **Rank the remainder** by score and fill to `N`. **Additive-above-N**: `N` is a
   *guaranteed floor* of ranked picks; carve-outs and sticky latches may push the
   realized count above `N`. This is the simplest policy and never destructive.
5. **Latch `salience_selected = 1`** for the union. The latch is **one-way
   (`0 → 1`, never `1 → 0`)**: once selected, a case stays selected for its
   lifetime. The score recomputes every pass on fresh features, and ranking uses
   the fresh scores to *fill remaining capacity* — but selection never de-commits.

This resolves the temporal dynamics of a live conference cleanly: a case selected
early and later out-ranked **stays selected** (its committed prediction is safe,
cleanup never touches it, no thrash); a high-salience petition appearing mid-cycle
is picked up on the next pass if capacity or a carve-out admits it. Because
selection is additive-only and scores are versioned, the selected set at any time
is reconstructable from committed columns — the pre-registration replay is a pure
read, not a re-derivation that could drift.

**Enforcement wiring** is small but real (it is not free):

- `predict-matrix`'s scope filter carries one skip branch — a hard-in-scope SCOTUS
  docket with `salience_selected == 0` is dropped from the tournament matrix with a
  distinct "not selected this salience round" note (read-time, non-destructive).
- The pull queue declines to enqueue unselected cases.
- **Cleanup stays keyed to hard-scope only.** It never consults `salience_selected`;
  a below-cap-but-hard-in-scope case keeps its committed predictions and simply
  gets no *new* ones.
- **Fail-open**: a legacy row with `salience_selected` unset is treated as
  *selected*, so nothing already committed is ever stranded.

**Production wiring — the live cycle.** The write pass runs inside every
live-channel cycle (`live-poll`), after the polls have ingested the day's
distribution transitions and before the workflow pushes the corpus, so the
committed pointer carries the **post-pass** latch state: every sweep pick is
selected at the pointer the predict matrix gate reads, and a fail-open queue
entry (a never-scored petition queued at transition time) that the same
cycle's pass scores-and-defers is dropped by that read-time gate,
non-destructively. Ordering is the load-bearing detail: the queue-time
deferral check reads
the *pre-pass* latch, so transition routing alone would silently drop a petition
whose first transition and first selection land in the same cycle. The cycle
therefore ends with a **selection sweep**: every selected petition with an open
event still *owed* a prediction is re-polled, provisioned, and queued — stalest
first, capped by `salience.sweep_cases_per_cycle` in `config/tracking.yaml`. Owed
is per `(predictor, event)` cell — mirroring the evaluate backlog deriver — so a
case where two of three engines landed and one quota-failed is still swept for
the missing engine, and the per-cell attempt cap `predict.max_attempts_per_cell`
keeps one cell that fails every attempt from re-queuing forever without
suppressing a sibling engine still owed the same event. The same sweep is the
catch-up for petitions whose transitions all predate the first applied pass, and
the retry for a selected petition whose queued run left a cell without a
committed prediction; the `predict_queued_at` stamp the routing writes with every
queue entry debounces that retry to daily, so an open-but-unmerged run PR is not
re-queued every cycle. Document provisioning follows the same gate: a deferred
petition's transition fetches nothing, and its documents are provisioned by the
sweep if it is ever latched.

**The relist requeue cooldown.** A **relist** — a distribution transition on a
petition already distributed before, as opposed to its first distribution — inside
`salience.relist_requeue_cooldown_days` (default 1) of the case's last
`predict_queued_at` stamp is treated as administrative churn rather than a
materially different posture, and is not requeued: the divert is surfaced on
`predict_skipped_relist_cooldown` for triage, never silently dropped, and it
re-stamps `predict_queued_at` (anchoring the next cooldown check and keeping
the same-cycle sweep from immediately re-queuing what was just suppressed). The
default suppresses only a same-day repeat — a petition re-tournamented hours
after its first prediction, the observed failure mode — while a relist the
next day or later queues normally. Only applies under the gated scope with a
salience config in force (capacity actually enforced); `0` disables it.

## Replaying the gate

Because `sal-v1` is frozen and selection is a pure function of a row's
features, the gate can be **replayed over past Terms at reconstructed
moments**: `fedcourts salience-replay` projects each resolved paid modern-cert
petition of a named Term to the state its docket disclosed at a chosen cutoff
— petition **arrival**, the **first distribution**, or the **last
pre-resolution distribution** — and runs the same selection core the live pass
runs (`plan_cohorts`) over the projection, into `metrics/salience-replay.json`.

The projection layer (`fedcourtsai.pipeline.asof`) is the honesty mechanism:
time-invariant identity (docket number, fee class, originating court, sampling
weight) is copied from the row, the docket-acquired signals (relists, CVSG,
the conference cohort) are re-derived from a point-in-time payload via the
same parsers the predict cell's conditioning context uses, and every outcome
and latch field is nulled. A payload that discloses no proceedings projects as
**unobservable** — unknown posture, never banded, never selected — and the
reconstruction reuses the cert back-test's leakage machinery (redaction,
date-keyed truncation, the dated-snapshot preference, the fail-closed
disposition scan), so the two replays share one definition of a
point-in-time docket.

What the report shows, per (Term, policy): the would-have-been selection
split into carve-outs and rank fill, where capacity actually bit, the band and
provenance mix, and sample-weighted precision/recall of the selection against
the realized grant-family outcomes. The arrival cells quantify the gate's
structural degeneracy — every signal the score turns on is docket-acquired, so
at arrival everything reads baseline and nothing is selected — and the
resolution cells bound what the carve-outs would have caught. The same
population frame and cutoffs are what a full predict/evaluate backtest over a
past Term inherits. What the numbers may and may not be read as:
`metrics/README.md`.

## Capacity `N` — the funding knob

`N` is the single parameter that scales inference cost, and the mechanism the
budget's "more funding = more cases" equation and the milestones' funding milestone
both hang on. It is a **per-conference** config value, and raising it **deepens the
salience-ranked slice rather than changing the ranking**. The **OT2026 default** is
sized to the **bootstrapping** budget — the flagship three-engine long-conference
release fits the ~$10K envelope (~$5K inference at the ~$13/fully-tournamented-case
planning rate, ~$11 measured): **~150 per regular conference and ~200 for the long
conference** (which clears the summer backlog of 1,000+ petitions at once). Those
caps leave headroom inside the same envelope, deliberately — the long conference is
the one cohort whose realized size has never been observed, so the default funds it
plus the Term's first regular conferences rather than spending the envelope on a
single guess. A per-conference cap
matches the Court's cadence and scopes replay to one conference's candidate pool;
the long conference carries a larger `N` so a flat cap does not under-serve it. At
the top of the same dial, `N` = "every eligible event" makes salience purely the
public ranking rather than a spend control. `budget.md` works the `N → funding`
math; this doc owns the default and the knob's semantics.

## The big-case score (a pre-registered stakes opinion)

A field on `prediction.json` — `big_case_score` (0–1) plus an optional one-line
rationale — capturing the predictor's view of the case's **stakes / importance /
newsworthiness, decoupled from grant likelihood**. Define it as *significance if
decided*: a case can be denied yet high-stakes and closely watched, or granted yet
narrow and technical, so the score carries information beyond `probability` rather
than shadowing it.

It is **judged by an independent evaluator, not against a ground truth**. At
evaluation the evaluator forms its **own** read of how big the case is, and the
grade is the *agreement* between the predictor's pre-registered score and the
evaluator's independent read:

- The evaluator's read must be formed **before** it is shown the predictor's
  number, or it anchors and the agreement is circular.
- Under cross-evaluation this yields a **panel** of independent reads per case;
  aggregate against the panel to damp single-judge noise.
- The evaluator is a **judge, not a forecaster**: it may use post-decision context
  available at evaluation time (the outcome, the immediate reaction). This is the
  mirror of the leakage rule — press coverage is the classic post-hoc salience
  proxy, forbidden as a *predictor* input but fair as *evaluator* context.

Both scores are 0–1 absolute, but the meaningful signal is **ordering across the
cohort** ("big relative to this term's docket"), so leaderboard aggregation uses
**rank-agreement** across the evaluated set, not only per-case absolute deltas.

## Base rates & baselines for the predicted segment

Salience gating makes the predicted population a **biased subsample** — high-relist
and CVSG petitions dominate the selected slice and grant far above the ~1–3%
whole-docket cert rate. So the docket-wide base rate is the wrong anchor for both
consumers that need one: the **prediction agent** (its prior) and the **evaluator**
(the naive baseline a real forecast must beat). Both need a base rate conditioned
on **the segment we predict on**.

**The leakage constraint is the crux.** The statpack is a pure function of the
whole committed corpus — it has no clock. Leakage-safety comes solely from the
**per-Term self-selection surface**: a replay/back-test cell restricts itself to
Term rows strictly preceding its `DECIDED_BEFORE` clock. Today that per-Term
surface carries only *overall + per-fee-class* grant rates; the relist/CVSG cuts
are **pack-wide marginals blended across all Terms** and would leak the current
term's outcomes if a replay cell read them. Therefore the segment base rate **must
live in the per-Term surface**, keyed by a deterministic salience-score band, so it
inherits the per-Term self-selection contract. A pack-wide segment section may also
be published for the current-term human board, but only the per-Term cut is
replay-safe.

The base rate then flows to both consumers on the same footing as the grant/deny
prediction's timing contract:

- **Predictor** — reads the committed statpack (no per-case provisioning) and
  anchors on the selected-segment per-Term rate, adjusting from the case's own
  relist/CVSG/circuit/fee-class detail.
- **Evaluator** — scores a **Brier skill score / lift vs the segment base rate**,
  so a prediction that merely parrots the base rate earns ~zero skill and a genuine
  edge shows as positive lift. The leaderboard carries the aggregated
  skill-vs-baseline column, **per stratum** — so a forward cell's skill lands
  there. The ops dashboard reports the selected segment's size and its base grant
  rate, and compares predictions to that baseline **for the replay stratum
  only**: its calibration block filters to retrospective cells before averaging,
  so no volume of forward grading ever fills that line. Replay cells come from
  the cert back-test, not the evaluate channel.

**The lookback window is a stated choice, not a default.** The band rate is pooled
over prior Terms — but *how many* prior Terms is a real parameter, and it moves the
anchor. Per-Term high-band grant rates over the walked range (OT2017–OT2025) run
**25.8%–48.0%**, nearly 2×; elevated runs 16.8%–25.2% on the **risk-set** rate a
forecast is scored against (8.7%–18.8% on the terminal rate the same table shows
in the lead column — see below). Anchored at an OT2026
petition, the high band reads roughly **37% (n≈1000)** pooling every prior Term,
**34% (n≈610)** over the last five, and **44% (n≈70)** over the last one — recompute
from the statpack's per-Term band table rather than quoting these. That is a
~10-point spread in the number a forecast's Brier skill is scored against, and in
the prior a cell is told to start from, turning on a parameter — so the parameter
is stated rather than left to a default.

**Two rates per band, and which one is scored depends on how the band was
obtained.** A band only ever strengthens — the distribution count is max-latched
and a CVSG date, once set, stays set — so a band re-derived at evaluation is the
band a petition *ended* at, while the band frozen on the prediction is the one
the cell faced. The statpack publishes both rates against each band: the terminal
one over petitions that ended there, and the **risk-set** one over every petition
that ever reached it. A cell carrying a frozen band is scored against the
risk-set rate, because that is the population it belonged to; a cell without one
falls back to the terminal band and the terminal rate, which at least agree with
each other. Reading either rate against the other kind of band is the error the
pairing exists to prevent — the risk-set rate against a terminal band overstates
the baseline for exactly the petitions whose band moved, and the terminal rate
against a frozen band understates it several-fold in the weak bands. The top band
has nothing above it, so its two rates coincide exactly.

The tension is bias against variance, and it has no free answer. Per-Term
high-band samples are small (61–163 weighted-resolved petitions), so a short
window is noisy: two Terms gives n≈192. Pooling every prior Term buys n≈1000 and a
stable estimate, but assumes the Court's grant behaviour is stationary across the
whole range, which the spread above suggests it is not. Two second-order effects
push the same way. The bands are frozen at `sal-v1`, so a long window also assumes
band *semantics* are stable across every Term pooled — each per-Term entry carries
its own `salience_version` for exactly this reason, and a bounded window would
limit that exposure as a side effect. And the pooling weights are
`weighted_resolved`, not `resolved` (OT2024's high band is `resolved=58`,
`weighted_resolved=121`), so a long window compounds Terms whose walk coverage
differs.

So the window is **config, not a constant**: `salience.base_rate_lookback_terms`
in `config/tracking.yaml`, where `0` means every prior Term. It ships at **0**, the
pre-registered behaviour, so that the choice is on the record and a change to it is
a reviewable diff rather than an invisible shift in every published
skill number. It is counted in Term *years*, not statpack rows: a Term absent from
the pack, or present only as a zero-row cursor entry, shortens the sample rather
than pulling an older Term in to refill the slot, so the window cannot move as the
walker's coverage changes. Moving it off `0` is an evidence-led call worth making
before the process-version freeze ([milestones.md](milestones.md)), since it
re-bases every forward skill number at once.

**The scored baseline and the anchor an agent reads do not share the window.** The
baseline is computed in code
(`fedcourtsai.pipeline.evaluate.segment_base_rate`) and honours
`salience.base_rate_lookback_terms`. No agent runs that code: every agent that
needs a prior — the forward predictor and evaluator, and the cert back-test's
replayed predictors, which run the same prompt — reads the band table in
`metrics/statpack.md`, so its window is whatever that table renders, capped by
`statpack.markdown_terms` (default 10). The bound is conventional, not a capability
limit: `statpack.json` sits in the same checkout and carries every Term, and the
prompts are what direct anchoring at the table.

With the walked range at OT2017–OT2025 the pack holds nine Terms, nothing is
truncated, and the two windows **coincide**. They part the first season the pack
passes ten Terms — and the sharpest consequence is inside a single back-test run,
where a replayed agent would be scored against a Term it was never shown. Both
knobs are stated for that reason, so the pair is reconciled — or deliberately left
apart — as one decision rather than two accidents. Both per-Term captions in
`statpack.md` state the rendered window, so a truncation is visible to the agent
reading the table rather than silent.

The ops dashboard's segment rate is a **third, different number**: pack-wide,
blended across every Term and unmasked by any clock (`fedcourtsai.ops`). It is an
operational statistic for the human board, never the scored baseline, so neither
knob applies to it.

### Scope: SCOTUS cert only, deliberately

The segment baseline is **not** generalised to other courts, and that is a
decision rather than an omission. Circuit rows are ingested for retrieval context
and never predicted; when they enter prediction scope they will need a skill
baseline, and this one does not translate. Three of its four load-bearing parts
are SCOTUS-cert-shaped by construction:

- **The Term is the leakage control**, not a label. Pooling Terms strictly before
  the case's own is what makes the anchor replay-safe, and `segment_base_rate`
  returns `None` without one. A circuit docket has no Term, so an equivalent
  guard has to be built from something else — a rolling window on the decision
  date is the nearest candidate, and a calendar year is not a natural unit of
  appellate practice the way a Term is for the Court.
- **The `sal-v1` bands do not generalise at all.** Relist count, CVSG presence,
  originating circuit and fee class have no circuit analogues — there is no
  relist, no CVSG, no court below in the same sense, and no IFP serial convention
  to read a fee class from. A circuit band function is a new scorer over
  different features, not a re-parameterisation.
- **The outcome is a different act.** `granted` means cert was granted on a
  SCOTUS row and a motion was granted on a circuit one. A circuit baseline has to
  choose which binary it estimates before it can estimate a rate, and the useful
  one is probably affirm/reverse — which no column carries cleanly today.

What *does* generalise is the **per-court always-deny floor**, which
`metrics/backtest.json` already reports per court. That is the reason the cut is
per-court rather than SCOTUS-only: a circuit predictor gets an interpretable
floor the day it runs, with no new machinery.

So the near-term position is that circuits are covered by the floor and by
nothing else. Publishing a cross-court "segment base rate" would produce a number
that looks comparable between courts and is not, which is worse than reporting
none — the same reasoning the generic back-test applies in declining a segment
baseline of its own.

## GVR as a first-class label

A grant/vacate/remand — and especially a Munsingwear vacatur, where the Court
grants and vacates because a case became moot — conflates *cert-worthiness* with
*vacatur practice*: the disposition tracks the Court's housekeeping wording, not
whether the question was worth deciding. The prediction vocabulary makes GVR a
**first-class predictable label** so an agent can forecast a GVR specifically
rather than folding it into an undifferentiated "granted."

- The realized-outcome vocabulary gains a **`gvr`** disposition. The Munsingwear
  *mootness* sub-type stays encoded by the existing `Outcome.disposition_basis`
  (`gvr` + `mootness` = a Munsingwear vacatur, segmented into the procedural
  leaderboard stratum; `gvr` + `standard` = a merits GVR). There is no separate
  `vacated-moot` label — the basis attribute already carries that distinction.
- **A GVR still counts as a grant on the binary axis** (`gvr` joins the granted set
  for `actual_granted`), so `probability` (P(granted)) and the Brier score remain
  **fully comparable across all history** — the binary axis is the comparability
  anchor; only the disposition-label axis gains the new value.
- **Migration is a forward-convention change, not a retroactive relabel.** New
  resolutions label a GVR `gvr`; outcomes recorded before the label keep `granted`,
  because retroactively flipping a decided outcome would penalize a past
  `granted` prediction for using the *then-current* vocabulary (its `correct` is
  frozen and fair). The one exception a one-time deterministic backfill *can* fix
  from committed data alone is the **identifiable Munsingwear vacatur** (`granted`
  + `mootness` basis → `gvr`), which is already in the non-ranked procedural
  stratum, so no metric moves. A plain-`granted` **merits** GVR in history is an
  accepted residual — indistinguishable post-hoc without re-resolving the source
  docket text (the `outcome.json` does not carry it), and immaterial on the binary
  axis.
- **Routing.** "Is this a likely GVR / mootness-prone case" is a genuine routing
  signal, but deterministic **pre-decision** detection does not exist today (a
  strategically-mooted case reveals itself only through docket text that no
  extractor parses). So the near-term fold-in is the **model-produced** call — the
  predictor forecasts `gvr` when it reads the posture that way, and the big-case
  score captures the stakes — with deterministic mootness-proneness deferred to a
  possible `sal-v2` feature.

## The interim docket (designed, not measured)

The cert program above selects petitions. The interim docket — stays,
injunctions, vacaturs pending certiorari — needs its own, because none of
`sal-v1`'s features exists there: an application is not distributed for
conference, and a CVSG is a cert-stage act. Reusing the band would be the
conditioning mismatch this document spends its length warning about.

**Most of the docket is not the thing predicted.** Over a spread sample of 26
OT2023–OT2024 applications, **85%** are requests to extend the time to file:
granted by a single Justice as a matter of course, with nothing about the case
moving the answer. 12% are substantive. Admitting the whole docket would hand a
predictor a base rate it beats by answering "granted" every time — the IFP
problem in a sharper form. `interim_signals.is_predictable_application` keeps only
the substantive ones, and excludes an unreadable ask with them: that is a parser
gap, and shrinking coverage visibly is better than admitting a matter of unknown
character into a scored population.

**The escalation ladder is the salience structure.** Three signals are readable
from the proceedings before an application resolves:

| signal | what it is |
| --- | --- |
| the Court **requests** a response | an affirmative act of attention — the interim analogue of a CVSG, and *not* the same event as a response arriving uninvited |
| the application is **referred to the Court** | the full bench takes it, rather than a Circuit Justice acting alone — which is also what selects the aggregation rule |
| **amicus briefs** filed | a proxy for stakes, counted rather than flagged |

The three sampled substantive applications separate on exactly that ladder — a
two-entry summary denial with no signals, a referred denial with a response
filed, and a granted application that drew a requested response, an amicus brief
and oral argument. That is a suggestive shape and **not a base rate**: three
observations cannot support a rate, and none is published or scored against.

**The two traps transfer unchanged.** All three signals are monotone over an
application's life — the Court does not un-request a response, un-refer an
application, or un-file a brief. So the band derived at resolution is the band the
application *ended* at rather than the one a cell faced, and a rate conditioned on
the ending band understates what a live application faces. Those are the same two
defects the cert program corrected, and the answers carry over: freeze the band as
at prediction, and pool the rate over a risk set.

**What is missing is the rate.** Measuring it means resolving enough substantive
applications to condition on, and they are 12% of a docket the pipeline does not
yet poll. Until then the interim segment is declared unspecified rather than given
a cert-shaped stand-in — the same posture the merits stage takes, and for the same
reason.

## Shared discipline: leakage / timing

The deterministic salience features and the predictor's big-case score both rest on
**pre-conference / pre-decision** material only. Allowed predictor signals: the
docket facts (relists, CVSG, circuit, fee class, questions presented, the petition
and brief in opposition). Forbidden on the predictor side: the post-hoc press proxy
and anything dated after the event — the same signals the evaluator *may* use as a
judge. This makes both scores' timing contract identical to the grant/deny
prediction's, so they slot into the existing forward/replay frame with no new
machinery: a forward cell computes them live, a replay cell self-selects its
statpack Term rows behind the `DECIDED_BEFORE` clock.

## Where it plugs in (seams)

- **`scope.json`** records each entry's `salience_score`, `salience_version`, and
  `salience_selected` as the published transparency artifact — but only for cases
  that already have a committed `data/cases` directory (its enumerate-from-the-tree
  invariant; it never scans the corpus). It is a *record*, not an input: no pipeline
  seam reads it back to drive selection. The **full candidate pool** —
  including Tier-0-excluded and below-cap cases that have no committed
  directory — belongs on the salience board (below), not here.
- **The selection is driven by the `salience_selected` corpus latch**, not by
  reading `scope.json`. `predict-matrix`'s scope filter consumes the latch
  directly, the same way it consumes `predict_excluded` and the court predicate
  today.
- **Hard eligibility** stays in `corpus.OUT_OF_SCOPE_RULES` /
  `out_of_scope_reason_full` (the IFP rule among them). Below-cap selection is a
  **separate** latch and never enters this evaluator.
- **The salience ranking** has no published board yet: the scores and the latch
  live in the corpus and reach git only through `scope.json`. The planned
  artifact is a deterministic board under `metrics/salience.{json,md}`,
  regenerated like the other roll-ups — the pre-registered big-case board,
  carrying the ranking, the full candidate pool, the selected set, and the
  segment base rate ([milestones.md](milestones.md)).

## Ratified decisions (config, tunable)

The knobs are settled for the first release; each is config, so changing one is a
config edit, not a redesign. `N` **is a guaranteed floor, not a hard ceiling** —
the posture below keeps selection additive and never destructive:

- **Capacity `N`** — per-conference, OT2026 default ~150 / regular conference and
  ~200 / long conference (the bootstrapping envelope above). **Whether the cap
  binds at all depends on the Tier-0 IFP filter, which is larger than it sounds.**
  Measured on the accumulating OT2026 long-conference cohort: of the petitions
  distributed for it, **roughly two thirds are IFP** and leave at Tier 0, so the
  eligible pool is about a third of the raw distribution volume. At that ratio the
  200-case cap starts binding only once the conference draws more than ~600
  petitions; below that every eligible petition is funded and `N` is inert. Read a
  raw distribution count as a *ceiling* on the funded slice, never an estimate of
  it — and re-measure the ratio rather than assuming it holds, since it is a
  property of who files, not of the pipeline.
- **Carve-outs sit above `N`** (not consuming it): CVSG and above-floor cases are
  guaranteed in, and `N` still fills with the next-best ranked cases, so no major
  case is ever crowded out.
- **Mid-cycle arrivals: additive-above-N** — a late high-salience petition is
  simply selected too (consistent with the sticky, never-de-select latch); no
  reserved headroom.
- **Unspent capacity is never reclaimed** — a small conference may under-fill `N`;
  reclaiming would break per-cohort replay reproducibility.
- **`sal-v1` weights are fit to the empirical per-bucket grant rates** (above); the
  salience floor sits at the relist-2 / CVSG grant-rate band (~25%+). Exact
  coefficients are pinned in the implementing change.
- **The segment base rate's lookback is unbounded** —
  `salience.base_rate_lookback_terms: 0`, every Term strictly before the case's
  own, preserving the pre-registered behaviour exactly. The agent-facing window is
  `statpack.markdown_terms: 10`. Both are stated so the pair can be moved
  together, on evidence, in one reviewable diff (*Base rates & baselines for the
  predicted segment* above).
- **The segment baseline stays SCOTUS-cert-only** — the Term is its leakage
  control, the `sal-v1` bands have no circuit analogue, and `granted` names a
  different act on a circuit docket. Other courts are covered by the per-court
  always-deny floor and nothing else, because a cross-court "segment base rate"
  would look comparable between courts without being so (*Scope* above).
- **The `big_case` grade is rank-agreement across the cohort** (bigness is
  comparative), with a per-case absolute delta kept only as a secondary diagnostic.
