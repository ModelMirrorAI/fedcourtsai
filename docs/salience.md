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

**One predicted stream sits outside this gate entirely.** A cert grant opens a
merits event, and that event is forecastable on its own terms — no salience
score, no rank, and no reserve, because the case was already selected once as a
petition and the grant cohort is self-limiting at the Court's own volume. The
gate below governs which *petitions* and which *applications* earn cells; the
merits cell rides the grant. Its cost is priced in [budget.md](budget.md) and
its scoring contract in [decision-model.md](decision-model.md).

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
hand-tuned: a case's score approximates `P(grant | its relist / CVSG / circuit
cell)` read off the committed statpack, so the ranking is directly
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

Fee class (paid vs IFP) deliberately does **not** enter the score: IFP petitions
are Tier-0-excluded, leaving the scored set paid-only.

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

### The `sal-v2` intent (pre-registered)

`sal-v1`'s features are docket-acquired — relists and CVSG accumulate over a
petition's life — so at arrival every observable petition scores `baseline` and the gate
is structurally inert at the one moment a truly prospective selection would
have to act: no cohort forms, no band stratifies, recall over realized grants
is zero by construction (the gate replay measures exactly this). The rework is
pre-registered here so the shape is fixed before the evidence exists, and it
is **two cohorts, never pooled**:

- **The arrival cohort** — selected at docketing on arrival-time features
  (originating court, party/counsel structure) **plus a random-sample
  component**. The random slice is load-bearing, not a fallback: with no
  strong arrival-time signal it is the only route to an unbiased selected
  population, it makes the cohort's baseline exactly the unconditional grant
  rate, and no selection rule can game it. This is the only cohort whose
  skill numbers transfer to live prospective use.
- **The escalation cohort** — re-selected as relist / CVSG / response signals
  accumulate: `sal-v1`'s current behaviour, which remains the right way to
  spend tournament budget on cases that have become interesting. It reports
  against its own risk-set baselines and never against — or blended with —
  the arrival cohort's.

Three constraints carry over from the versioning discipline. `sal-v2` is a
**new frozen version, never an in-place edit** — `sal-v1` rankings must replay
under `sal-v1` forever, which the scorer registry below is what enforces. Its
evidence base does not exist yet: arrival-time
signals live in small subgroups, which the legacy denial subsampling cannot
measure, so fitting waits for the denial-complete historical re-walk, and any
candidate is judged by replaying the gate against the same corpus state as a
fresh `sal-v1` run — the bar is the arrival population's own weighted grant
rate at comparable recall, recomputed post-re-walk rather than quoted. And the
carve-out/band alignment is pinned by test: the always-include floor and the
strongest band's cutpoint are separate constants in separate files, and the
identity between "carved in" and "strongest band" is checked exhaustively over
`sal-v1`'s achievable score lattice, so a refit of it cannot open a silent gap
between them. The check runs for every registered version, but the lattice it
enumerates is `sal-v1`'s feature space — relist count, CVSG, originating
circuit — so a version keying on anything else is checked only at those
features' defaults. Registering `sal-v2` means extending the enumeration to
span its own features; until then its coverage is partial and said so here.

### The scorer registry

A salience version is not a function but four things that decide together what
a band label means: the score function, the band function, the band *names*,
and the always-include rule. A fifth belongs with them and deliberately does
not travel on the record: the always-include **floor** the carve-out compares
against is `config/tracking.yaml`'s single shared `salience.floor`, so it is
config rather than code and every registered version is held to the same value.
That is a real cost, stated rather than hidden — a replay run today reproduces
a past ranking only if the floor has not moved since, and a candidate scorer
cannot choose its own carve-out threshold without moving the shared one.
`pipeline.salience.SCORERS` holds each version as
one `SalienceScorer` record, and `SALIENCE_VERSION` names the **active** one —
the version the live pass scores with and stamps onto the corpus and onto every
prediction's frozen context. A refit registers a new record beside the old
rather than editing it, and `scorer(version)` raises on an unregistered label
rather than falling back, so no consumer can silently receive output banded
under a version it did not ask for.

Three consequences are worth stating, because each is a place the discipline
could otherwise leak:

- **The corpus is single-version by design.** `salience_score` and
  `salience_version` are one column each, holding the active scorer's view. What
  makes history safe is not the corpus but the band and version frozen onto each
  committed prediction, so re-pointing the active version can never retroactively
  re-band a prediction **that carries a frozen band**. A prediction written
  before that block existed has its band re-derived from the row by the active
  scorer, and is re-baselined by a version switch; `base_rate_salience_version`
  on the evaluation is what makes that visible after the fact.
- **`statpack.json` publishes every version.** A base-rate pool is pinned to the
  scorer that assigned the band it quotes, so a prediction frozen at a retired
  version would lose its baseline the day the live pass moved on. Each Term
  carries the active version's `segments` plus an `alt_segments` block per other
  registered version; the block is absent from the payload while only one
  version is registered. The **Markdown** pack renders the active version only,
  so a reader of `statpack.md` under two versions is reading one of them.
- **The gate replay is a three-axis report.** Cells span Term x policy x
  version, and each (Term, policy) is projected once and scored by every
  registered version, so two versions cannot differ in the dockets they saw.
  They are not compared at a matched operating point, though: the floor and the
  capacity are shared, so a scorer with a different score scale selects a
  differently sized set. Read a cross-version comparison at matched **recall** —
  the bar pre-registered above — never as a bare precision delta
  (`metrics/README.md`).

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
4. **Rank the remainder** by score and fill to `N`, minus any **interim reserve
   slots in use** in the current (latest) cohort — the one carve-*in*: a live
   substantive application's slot displaces the lowest-ranked rank-fill pick,
   never a carve-out (see *The interim docket* below). **Additive-above-N**
   otherwise: carve-outs and sticky latches may push the realized count above
   `N`. This is the simplest policy and never destructive.
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
case-baseline (petition/appeal-kind) event still *owed* a prediction is
re-polled, provisioned, and queued — stalest
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

Because `sal-v1` scoring is a pure function of a row's features — and
selection a pure function of a cohort's — the frozen gate can be **replayed
over past Terms at reconstructed moments**: `fedcourts salience-replay`
projects each of a named Term's resolved, live-slice, paid modern-cert
petitions to the state its docket disclosed at a chosen cutoff
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

What the report shows, per (Term, policy, salience version): the would-have-been selection
split into carve-outs and rank fill, where capacity actually bit, the band and
provenance mix, and sample-weighted precision/recall of the selection against
the realized grant-family outcomes. The arrival cells quantify the gate's
structural degeneracy — the primary signals the score turns on are
docket-acquired (the circuit rides only as a bounded nudge that can never move
a band or clear the floor), so at arrival every observable projection reads
baseline and nothing is selected — and the
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
  there, aggregated as a population ratio of summed Briers rather than a mean of
  per-cell ratios. Beside it the board publishes a second, deliberately **ex-post**
  column: the same band scored against the rate the case's *own* Term realized,
  leave-one-out, which nets out level-knowledge and leaves discrimination. It is
  a board-only figure — no cell records it, no predictor could have known it,
  and it never ranks — with its claim contract in
  [metrics/README.md](../metrics/README.md). The ops dashboard reports the selected segment's size and its base grant
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

**The pool is version-pinned, and a lagging statpack yields no baseline rather
than a blended one.** A band name is meaningful only under the salience version
that assigned it — a hypothetical `sal-v2 high` and a `sal-v1 high` are
different populations that happen to share a label. So every band-rate entry
point pins the version — the two scored baselines
(`fedcourtsai.pipeline.evaluate.segment_base_rate` and
`prediction_base_rate`, through their shared pooler), and the board's ex-post
`realized_band_rate`, which pins identically on its single Term. They read
**only** the statpack
Terms whose `salience_version` matches the version that produced the band
(the frozen `PredictionContext.salience_version` on the risk-set path; the
live scorer's version on the terminal path), and when no Term matches, the
baseline is `None` — the same contracted no-baseline answer as a case with no
prior-Term data. On a statpack that lags the band's version both paths are
version-starved, so `brier_skill_score` is omitted rather than computed
against a number no version ever defined; in the mirror case — a pack already
re-rendered under a newer version while an old frozen-band cell is scored —
the risk-set path yields `None` and the evaluator falls back to the terminal
band under the live scorer, on the `terminal` basis it records. The evaluator
prompt carries the agent-side half of the same rule: the rendered band table's
heading names its salience version, and on a mismatch with the prediction's
frozen version the agent omits the baseline and flags it rather than pooling
from a table another version rendered. The
operational consequence is deliberate: after a salience version ships, forward
cells scored under it have no skill baseline until the statpack re-renders
under the same version, and that gap is visible instead of silently papered
over.

The tension is bias against variance, and it has no free answer. Per-Term
high-band samples are small (61–163 weighted-resolved petitions), so a short
window is noisy: two Terms gives n≈192. Pooling every prior Term buys n≈1000 and a
stable estimate, but assumes the Court's grant behaviour is stationary across the
whole range, which the spread above suggests it is not. Two second-order effects
push the same way. The bands are frozen at `sal-v1`, and each per-Term entry
carries its own `salience_version` — the field the version pin above reads, so
cross-version pooling is impossible at any window length and the window carries
no versioning duty. And the pooling weights are
`weighted_resolved`, not `resolved` (OT2024's high band is `resolved=58`,
`weighted_resolved=121`), so a long window compounds Terms whose walk coverage
differs.

So the window is **config, not a constant**: `salience.base_rate_lookback_terms`
in `config/tracking.yaml`, where `0` would mean every prior Term. It is set to
**10**, matching `statpack.markdown_terms`, so the scored baseline and the band
table the agents anchor on share one window by construction and cannot silently
diverge as walked Terms accumulate; with nine Terms walked the bound excludes
nothing, so every published skill number is what the unbounded pool produced.
The choice is on the record and a change to it is
a reviewable diff rather than an invisible shift in every published
skill number. It is counted in Term *years*, not statpack rows: a Term absent from
the pack, or present only as a zero-row cursor entry, shortens the sample rather
than pulling an older Term in to refill the slot, so the window cannot move as the
walker's coverage changes.

**The scored baseline and the anchor an agent reads share the window by
configuration, not by mechanism.** The
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
truncated, and the two windows **coincide** — and because both knobs read `10`,
they keep coinciding when the pack passes ten Terms, instead of parting inside a
single back-test run where a replayed agent would be scored against a Term it
was never shown. Both knobs are stated so the pair is moved — or deliberately
split — as one decision rather than two accidents. Both per-Term captions in
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
- **The `sal-v1` bands do not generalise at all.** Relist count, CVSG presence
  and originating circuit have no circuit analogues — there is no relist, no
  CVSG, no court below in the same sense, and no IFP serial convention to read
  the Tier-0 fee-class exclusion from. A circuit band function is a new scorer over
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

## The interim docket (predicted, quota'd; published descriptively, not yet skill-scored)

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

**Predict scope is the substantive slice, funded by a bounded reserve inside
`N`.** Only a substantive application
(`interim_signals.is_predictable_application`) is ever predicted — the scope
rules keep extensions and unreadable asks excluded, and the next run of the
two-directional reconcile releases an application's latch once a poll has
latched its substantive reading. Selection is a **quota, not a ranking**: `sal-v1`'s
features do not exist here, so each selection pass fills up to
`salience.interim_reserve_slots` (5) with pending substantive applications in
**escalation-ladder order** — requested response first, then referral, then
the amicus count, `case_id` for determinism. That order is a deterministic
*pick sequence*, not a scored rate: choosing by the ladder asserts no grant
probability. A selected application occupies its slot until it resolves (the
sticky latch never de-selects), so the reserve bounds *concurrent* live
interim predictions and a slot frees only on resolution — where "resolves"
means the machine-matched resolution the accumulation rule below requires, so
an application decided in language the vocabulary misses pins its slot (and
its one displaced cert pick per pass) until a maintainer resolves the residue;
it is visible as the application rotation's long-unresolved tail. The slots in
use displace cert **rank-fill** capacity one-for-one in the **latest
conference cohort of the pass** — never a carve-out — so the reserve trades
slots inside `N` and target spend stays as [budget.md](budget.md) publishes;
an unfilled reserve displaces nothing. The trade is prospective, pass by
pass: a cohort whose rank fill latched *before* a slot was occupied keeps its
sticky picks, and an application queued in the fail-open window before its
first scoring pass rides outside the quota for that cycle — both can push a
conference's realized count transiently above `N`, the same drift-above-`N`
the carve-outs and sticky latch already produce. The predict trigger is the
interim analogue of the
distribution transition: an application has no conference calendar, so any
observed docket change on a still-unresolved substantive application in scope
queues its motion/interim baseline forward, debounced to daily by the shared
`predict_queued_at` stamp; the selection sweep addresses reserve-selected
applications too, since a selection can postdate the application's last
docket change. A machine-matched resolution then records the interim
`outcome.json` on the same baseline — the interim disposition vocabulary,
dated by the disposing entry, with no cert-only `signals` block.

**What is still missing is the rate; the cohort keeps accumulating.** The live
cycle re-polls unresolved applications up to a small per-cycle cap
(`live.max_applications_per_run`). Each poll persists the ask
(`application_kind` — arrival-time,
so safe to condition on) and the three ladder signals as latched corpus
columns, so an interim cohort can be assembled from the index: which
applications, which asks, how far each had escalated by resolution. The latched
signals are the *ending* band — the thing the two traps above forbid
conditioning a rate on directly — while the as-at-prediction values a valid
rate needs stay recoverable from the per-poll dated snapshots, whose entry
dates carry each signal's onset. One caveat bounds the accumulation itself: an
application counts as resolved only when the interim disposition vocabulary
matches its disposing entry, so the resolved set is selected for
machine-matchable resolution text (an unmatched resolution stays in the
rotation as a visibly long-unresolved residue rather than silently counting).
The accumulating cohort is published descriptively — the statpack's
interim section carries the counts by ask, the substantive slice's
resolved/granted counts and raw grant rate, and the escalation-signal counts,
pack-level and per application-Term — but **no interim skill is scored**:
`segment_base_rate` yields nothing for an application docket, so an interim
cell's evaluation carries a null skill, and the leaderboard segments the cell
into its unranked `interim` stage block, never the cert board. The predict and
evaluate prompts carry the agent-side half of the same rule in their interim
rules: the predictor reads the statpack's interim section as
descriptive counts rather than a scored base rate, and the evaluator omits
`segment_base_rate` and `brier_skill_score` (with `base_rate_basis` null) as
the stage's standing rule rather than a per-cell anomaly.
**Pre-registered claimability rule:** the interim segment base rate publishes
— and skill over the interim stage becomes claimable — once the statpack's
substantive **resolved count reaches 25**; until then the stage reports
counts and raw rates only. The estimator is pre-registered with the floor,
because the forking paths close now or never: when it publishes, the rate is
pooled over the **substantive resolved slice of application-Terms strictly
before the case's own** (the same leakage rule the cert band rate uses),
**unweighted raw counts** (the application stream has no denial sampling, so
every row stands for itself), with withdrawn/dismissed counted as ungranted
and the machine-matched-resolution selection caveat traveling with the number
wherever it is quoted. Two collapses in the resolved labels are likewise
recorded here rather than discovered later: an unmatched resolution never
enters the denominator (the accumulation rule above), and a mixed partial
disposition — "granted in part and denied in part", a real shadow-docket
shape — currently reads **denial-first** through the interim vocabulary and
lands as `denied` / ungranted; if that collapse proves material once volume
exists, changing it is a new reading applied forward, never a silent
relabel. The floor, the estimator, and the collapses are fixed here, before
any interim cell has been scored, so none can be tuned to a result. The
**merits** stage is a stage ahead of that: its baseline is not merely
pre-registered but wired — the statpack merits section's disturbed rate pooled
strictly-prior (`docs/decision-model.md`) — so interim is the only stage whose
estimator is written down and waiting on its cohort.

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
- **The segment base rate's lookback matches the agent-facing window** —
  `salience.base_rate_lookback_terms: 10` equals `statpack.markdown_terms: 10`,
  so the scored baseline and the band table the agents anchor on share one
  window; with nine Terms walked the bound excludes nothing. Both are stated so
  the pair can be moved together, on evidence, in one reviewable diff (*Base
  rates & baselines for the predicted segment* above).
- **The segment baseline stays SCOTUS-cert-only** — the Term is its leakage
  control, the `sal-v1` bands have no circuit analogue, and `granted` names a
  different act on a circuit docket. Other courts are covered by the per-court
  always-deny floor and nothing else, because a cross-court "segment base rate"
  would look comparable between courts without being so (*Scope* above).
- **The `big_case` grade is rank-agreement across the cohort** (bigness is
  comparative), with a per-case absolute delta kept only as a secondary diagnostic.
